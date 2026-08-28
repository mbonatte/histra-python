"""Strict C# comparison for the local Article Models benchmark suite.

Two runs are supported:

``authored``
    Preserve every HRX convergence setting.  This reproduces the C# numerical
    path and exposes states accepted by displacement/work criteria but rejected
    by the independent equilibrium audit.

``strict``
    Select the C# ``ForceMoment`` residual criterion for every nonlinear stage
    and tighten (never loosen) its convergence tolerance to the unchanged
    equilibrium-audit residual limit.  The warning policy and warning
    tolerances are identical to the authored run.

The command intentionally returns compact metrics from worker processes rather
than complete displacement histories.  That keeps parallel runs fast and
avoids copying every global displacement vector back to the parent process.
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
import json
import os
from pathlib import Path
import sqlite3
import time
from typing import Any, Iterable, Mapping
import warnings

import numpy as np

from histra.io.hr_loader import load_model
from histra.solver import AnalysisSession
from histra.solver.equilibrium import UnsafeEquilibriumWarning
from histra.solver.model_manager import ModelManager
from histra.solver.output_projection import compute_model_point_displacements


AUDIT_FORCE_ABSOLUTE_TOLERANCE = 1.0e-3
AUDIT_FORCE_RELATIVE_TOLERANCE = 1.0e-5
AUDIT_RESIDUAL_TOLERANCE = 1.0e-4
PARITY_REACTION_ABSOLUTE_TOLERANCE = 0.1
PARITY_DISPLACEMENT_ABSOLUTE_TOLERANCE_MM = 0.05


BENCHMARK_MODELS: tuple[dict[str, Any], ...] = (
    {"id": "3.1_coarse", "name": "Bridge_3.1_Coarse", "target": "Second"},
    {"id": "3.1_multiring", "name": "Bridge_3.1_Multiring", "target": "NewAnalysis"},
    {"id": "3.2", "name": "Bridge_3.2", "target": "NewAnalysis"},
    {"id": "3.3_drucker", "name": "Bridge_3.3_2_Zhang_drucker", "target": "NewAnalysis"},
    {"id": "3.3_drucker_tol", "name": "Bridge_3.3_2_Zhang_drucker_tol", "target": "NewAnalysis"},
    {"id": "3.4_zhang", "name": "Bridge_3.4_Zhang", "target": "NewAnalysis"},
    {"id": "3_abutment", "name": "Bridge_3_abutment", "target": "NewAnalysis"},
    {"id": "5.1_coarse", "name": "Bridge_5.1_coarse", "target": "NewAnalysis"},
    {"id": "5.1_spandrel", "name": "Bridge_5.1_load_spandrel", "target": "NewAnalysis"},
    {"id": "5.1_backfill", "name": "Bridge_5.1_load_spandrel_backfill", "target": "NewAnalysis"},
    {"id": "5.2_coarse", "name": "Bridge_5.2_coarse", "target": "NewAnalysis"},
    {"id": "bridge_1", "name": "Bridge_1", "target": "NewAnalysis"},
    {"id": "bridge_1_layers", "name": "Bridge_1_traversal_layers", "target": "NewAnalysis"},
    {"id": "bridge_2", "name": "Bridge_2", "target": "NewAnalysis"},
)


def strict_convergence_tolerance(
    authored_tolerance: float,
    audit_residual_tolerance: float = AUDIT_RESIDUAL_TOLERANCE,
) -> float:
    """Return a safe ForceMoment tolerance without weakening either limit."""

    authored = float(authored_tolerance)
    audit = float(audit_residual_tolerance)
    if not np.isfinite(authored) or authored <= 0.0:
        raise ValueError("authored convergence tolerance must be finite and positive")
    if not np.isfinite(audit) or audit <= 0.0:
        raise ValueError("audit residual tolerance must be finite and positive")
    return min(authored, audit)


def _read_csharp_reference(
    results_path: Path,
    analysis_keys: Iterable[int],
) -> tuple[
    dict[tuple[int, int], np.ndarray],
    dict[tuple[int, int, int], np.ndarray],
]:
    selected = {int(value) for value in analysis_keys}
    reactions: dict[tuple[int, int], np.ndarray] = {}
    displacements: dict[tuple[int, int, int], np.ndarray] = {}
    with sqlite3.connect(results_path) as db:
        for analysis, step, r1, r2, r3 in db.execute(
            "SELECT AnalysisKey,Step,R1,R2,R3 FROM ReactionSumStates"
        ):
            key = int(analysis)
            if key in selected:
                reactions[(key, int(step))] = np.asarray((r1, r2, r3), dtype=np.float64)
        for analysis, parent, step, ux, uy, uz in db.execute(
            "SELECT AnalysisKey,ParentKey,Step,Ux,Uy,Uz FROM DisplModelPoints"
        ):
            key = int(analysis)
            if key in selected:
                displacements[(key, int(step), int(parent))] = np.asarray(
                    (ux, uy, uz), dtype=np.float64
                )
    return reactions, displacements


def _max_steps_by_analysis(
    reactions: Mapping[tuple[int, int], np.ndarray],
) -> dict[int, int]:
    limits: dict[int, int] = {}
    for analysis, step in reactions:
        if step > 0:
            limits[analysis] = max(limits.get(analysis, 0), step)
    return limits


def _vector_error_metrics(
    reference: Mapping[Any, np.ndarray],
    actual: Mapping[Any, np.ndarray],
    *,
    scale: float = 1.0,
) -> dict[str, Any]:
    reference_keys = set(reference)
    actual_keys = set(actual)
    common = sorted(reference_keys & actual_keys)
    missing = sorted(reference_keys - actual_keys)
    extra = sorted(actual_keys - reference_keys)
    if not common:
        return {
            "reference_rows": len(reference_keys),
            "actual_rows": len(actual_keys),
            "matched_rows": 0,
            "missing_rows": len(missing),
            "extra_rows": len(extra),
            "max_absolute": None,
            "relative_l2": None,
            "worst_key": None,
        }

    expected = np.stack([np.asarray(reference[key], dtype=np.float64) for key in common])
    observed = np.stack([np.asarray(actual[key], dtype=np.float64) for key in common])
    delta = (observed - expected) * float(scale)
    absolute = np.abs(delta)
    flat_index = int(np.argmax(absolute))
    row, component = np.unravel_index(flat_index, absolute.shape)
    denominator = max(float(np.linalg.norm(expected * float(scale))), np.finfo(float).tiny)
    return {
        "reference_rows": len(reference_keys),
        "actual_rows": len(actual_keys),
        "matched_rows": len(common),
        "missing_rows": len(missing),
        "extra_rows": len(extra),
        "max_absolute": float(absolute[row, component]),
        "relative_l2": float(np.linalg.norm(delta) / denominator),
        "worst_key": [int(value) for value in common[row]],
        "worst_component": int(component),
        "reference_at_worst": float(expected[row, component] * float(scale)),
        "actual_at_worst": float(observed[row, component] * float(scale)),
    }


def compute_parity_metrics(
    csharp_reactions: Mapping[tuple[int, int], np.ndarray],
    python_reactions: Mapping[tuple[int, int], np.ndarray],
    csharp_displacements: Mapping[tuple[int, int, int], np.ndarray],
    python_displacements: Mapping[tuple[int, int, int], np.ndarray],
    *,
    expected_steps: Iterable[tuple[int, int]] | None = None,
    actual_steps: Iterable[tuple[int, int]] | None = None,
) -> dict[str, Any]:
    """Compare signed reactions and every available model-point component."""

    reaction_reference = {key: value for key, value in csharp_reactions.items() if key[1] > 0}
    reaction_actual = {key: value for key, value in python_reactions.items() if key[1] > 0}
    displacement_reference = {
        key: value for key, value in csharp_displacements.items() if key[1] > 0
    }
    displacement_actual = {
        key: value for key, value in python_displacements.items() if key[1] > 0
    }
    reaction = _vector_error_metrics(reaction_reference, reaction_actual)
    displacement = _vector_error_metrics(
        displacement_reference,
        displacement_actual,
        scale=10.0,  # HRX/C# centimetres -> millimetres.
    )
    expected_step_keys = set(expected_steps or reaction_reference)
    actual_step_keys = set(actual_steps or reaction_actual)
    missing_steps = expected_step_keys - actual_step_keys
    extra_steps = actual_step_keys - expected_step_keys
    step_history = {
        "expected_steps": len(expected_step_keys),
        "actual_steps": len(actual_step_keys),
        "matched_steps": len(expected_step_keys & actual_step_keys),
        "missing_steps": len(missing_steps),
        "extra_steps": len(extra_steps),
    }
    complete = step_history["missing_steps"] == 0 and step_history["extra_steps"] == 0
    reference_outputs_complete = (
        reaction["missing_rows"] == 0 and displacement["missing_rows"] == 0
    )
    within_tolerance = bool(
        complete
        and reference_outputs_complete
        and reaction["max_absolute"] is not None
        and displacement["max_absolute"] is not None
        and reaction["max_absolute"] <= PARITY_REACTION_ABSOLUTE_TOLERANCE
        and displacement["max_absolute"] <= PARITY_DISPLACEMENT_ABSOLUTE_TOLERANCE_MM
    )
    return {
        "complete_step_history": complete,
        "reference_outputs_complete": reference_outputs_complete,
        "within_parity_tolerance": within_tolerance,
        "step_history": step_history,
        "reaction": reaction,
        "model_point_displacement_mm": displacement,
    }


def _project_python_history(
    model: Any,
    executions: Iterable[Any],
) -> tuple[
    dict[tuple[int, int], np.ndarray],
    dict[tuple[int, int, int], np.ndarray],
]:
    reactions: dict[tuple[int, int], np.ndarray] = {}
    displacements: dict[tuple[int, int, int], np.ndarray] = {}
    for execution in executions:
        analysis = int(execution.analysis_key)
        for step in execution.output_steps:
            if (
                step.reaction_x is not None
                and step.reaction_y is not None
                and step.reaction_z is not None
            ):
                reactions[(analysis, step.step)] = np.asarray(
                    (step.reaction_x, step.reaction_y, step.reaction_z),
                    dtype=np.float64,
                )
            for point in compute_model_point_displacements(model, step.u, step=step.step):
                displacements[(analysis, step.step, point.parent_key)] = np.asarray(
                    (point.ux, point.uy, point.uz), dtype=np.float64
                )
    return reactions, displacements


def run_model(
    model_info: Mapping[str, Any],
    models_dir: Path,
    run_mode: str,
) -> dict[str, Any]:
    """Run one model and return only compact verification evidence."""

    name = str(model_info["name"])
    hrx_path = models_dir / f"{name}.hrx"
    results_path = models_dir / f"{name}.Results"
    started = time.perf_counter()
    model = load_model(hrx_path)
    preparation_started = time.perf_counter()
    preparation = ModelManager.prepare_model(model)
    preparation_seconds = time.perf_counter() - preparation_started

    session = AnalysisSession(
        model,
        equilibrium_policy="warn",
        equilibrium_force_absolute_tolerance=AUDIT_FORCE_ABSOLUTE_TOLERANCE,
        equilibrium_force_relative_tolerance=AUDIT_FORCE_RELATIVE_TOLERANCE,
        equilibrium_residual_tolerance=AUDIT_RESIDUAL_TOLERANCE,
    )
    chain = session.dependency_chain(str(model_info["target"]))
    chain_keys = tuple(int(analysis.key) for analysis in chain)
    csharp_reactions, csharp_displacements = _read_csharp_reference(
        results_path, chain_keys
    )
    step_limits = _max_steps_by_analysis(csharp_reactions)

    settings: list[dict[str, Any]] = []
    executions: list[Any] = []
    captured_warnings: list[warnings.WarningMessage]
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always", UnsafeEquilibriumWarning)
        for analysis in chain:
            authored_criterion = str(analysis.adaptive_convergence_criteria)
            authored_tolerance = float(analysis.convergence_tolerance)
            if run_mode == "strict" and int(getattr(analysis, "analysis_type", 0)) != 5:
                analysis.adaptive_convergence_criteria = "ForceMoment"
                analysis.convergence_tolerance = strict_convergence_tolerance(
                    authored_tolerance
                )
            settings.append(
                {
                    "analysis_key": int(analysis.key),
                    "analysis_name": str(analysis.name),
                    "authored_criterion": authored_criterion,
                    "authored_tolerance": authored_tolerance,
                    "effective_criterion": str(analysis.adaptive_convergence_criteria),
                    "effective_tolerance": float(analysis.convergence_tolerance),
                    "csharp_steps": int(step_limits.get(int(analysis.key), 0)),
                }
            )
            execution = session.run(
                analysis,
                max_committed_steps=step_limits.get(int(analysis.key)),
            )
            executions.append(execution)
            if not execution.completed:
                break
        captured_warnings = list(captured)

    python_reactions, python_displacements = _project_python_history(model, executions)
    expected_steps = {
        (analysis, step)
        for analysis, limit in step_limits.items()
        for step in range(1, limit + 1)
    }
    actual_steps = {
        (int(execution.analysis_key), int(step.step))
        for execution in executions
        for step in execution.committed_steps
    }
    parity = compute_parity_metrics(
        csharp_reactions,
        python_reactions,
        csharp_displacements,
        python_displacements,
        expected_steps=expected_steps,
        actual_steps=actual_steps,
    )
    unsafe_steps = [
        step
        for execution in executions
        for step in execution.committed_steps
        if step.equilibrium_ok is False
    ]
    unsafe_criteria = Counter(str(step.get("convergence_criterion", "")) for step in unsafe_steps)
    outcomes = [
        {
            "analysis_key": int(execution.analysis_key),
            "analysis_name": execution.analysis_name,
            "outcome": execution.outcome.value,
            "exit_code": int(execution.code),
            "committed_steps": len(execution.committed_steps),
            "runtime_seconds": float(execution.runtime_seconds),
        }
        for execution in executions
    ]
    return {
        "id": str(model_info["id"]),
        "name": name,
        "run_mode": run_mode,
        "gdl": int(model.gdl),
        "interfaces": int(preparation.interfaces),
        "preparation_seconds": preparation_seconds,
        "total_seconds": time.perf_counter() - started,
        "audit_tolerances": {
            "force_absolute": AUDIT_FORCE_ABSOLUTE_TOLERANCE,
            "force_relative": AUDIT_FORCE_RELATIVE_TOLERANCE,
            "residual": AUDIT_RESIDUAL_TOLERANCE,
        },
        "settings": settings,
        "outcomes": outcomes,
        "warning_count": sum(
            issubclass(item.category, UnsafeEquilibriumWarning)
            for item in captured_warnings
        ),
        "unsafe_step_count": len(unsafe_steps),
        "unsafe_steps_by_criterion": dict(sorted(unsafe_criteria.items())),
        "parity": parity,
    }


def _worker(task: tuple[dict[str, Any], str, str]) -> dict[str, Any]:
    model_info, models_dir, run_mode = task
    try:
        return run_model(model_info, Path(models_dir), run_mode)
    except Exception as exc:
        return {
            "id": str(model_info["id"]),
            "name": str(model_info["name"]),
            "run_mode": run_mode,
            "error": f"{type(exc).__name__}: {exc}",
        }


def _markdown_report(results: list[dict[str, Any]]) -> str:
    lines = [
        "# Article Models: Python vs C# verification",
        "",
        "Warning tolerances are unchanged: force absolute `1e-3`, force relative "
        "`1e-5`, active-residual L2 `1e-4`.",
        "",
        "| Mode | Model | Steps | Unsafe | Max reaction error (kN) | "
        "Max model-point error (mm) | C# parity |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for result in sorted(results, key=lambda item: (item["run_mode"], item["name"])):
        if "error" in result:
            lines.append(
                f"| {result['run_mode']} | {result['name']} | - | - | - | - | "
                f"ERROR: {result['error']} |"
            )
            continue
        parity = result["parity"]
        reaction = parity["reaction"]
        displacement = parity["model_point_displacement_mm"]
        step_history = parity["step_history"]
        steps = f"{step_history['actual_steps']}/{step_history['expected_steps']}"
        status = "PASS" if parity["within_parity_tolerance"] else "DRIFT"
        lines.append(
            f"| {result['run_mode']} | {result['name']} | {steps} | "
            f"{result['unsafe_step_count']} | {reaction['max_absolute']!s} | "
            f"{displacement['max_absolute']!s} | {status} |"
        )
    lines.append("")
    lines.append(
        "`strict` uses ForceMoment on every nonlinear stage and tightens, never "
        "loosens, the HRX convergence tolerance to the unchanged audit limit."
    )
    return "\n".join(lines) + "\n"


def _select_models(target: str) -> list[dict[str, Any]]:
    if target.casefold() == "all":
        return [dict(item) for item in BENCHMARK_MODELS]
    selected = [
        dict(item)
        for item in BENCHMARK_MODELS
        if target.casefold() in {str(item["id"]).casefold(), str(item["name"]).casefold()}
    ]
    if not selected:
        raise ValueError(f"unknown article benchmark model: {target!r}")
    return selected


def _checkpoint_path(output_dir: Path, model_info: Mapping[str, Any], run_mode: str) -> Path:
    return output_dir / "checkpoints" / f"{run_mode}_{model_info['id']}.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models-dir", type=Path, required=True)
    parser.add_argument("--model", default="all")
    parser.add_argument("--run-mode", choices=("authored", "strict", "both"), default="both")
    parser.add_argument("--max-workers", type=int, default=None)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    selected = _select_models(args.model)
    modes = ("authored", "strict") if args.run_mode == "both" else (args.run_mode,)
    tasks = [(model, str(args.models_dir.resolve()), mode) for mode in modes for model in selected]
    # These models can each retain several GiB of constitutive state. Four
    # concurrent workers measured faster than eight or fourteen on the 32-GiB
    # reference workstation because the larger pools exhausted swap.
    workers = args.max_workers or min(4, len(tasks), os.cpu_count() or 1)
    started = time.perf_counter()
    results: list[dict[str, Any]] = []
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "checkpoints").mkdir(parents=True, exist_ok=True)
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(_worker, task): task for task in tasks}
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            model_info, _models_dir, run_mode = futures[future]
            _checkpoint_path(args.output_dir, model_info, run_mode).write_text(
                json.dumps({"schema_version": 1, "result": result}, indent=2) + "\n",
                encoding="utf-8",
            )
            if "error" in result:
                print(f"[{result['run_mode']}] {result['name']}: {result['error']}", flush=True)
            else:
                parity = result["parity"]
                reaction = parity["reaction"]
                step_history = parity["step_history"]
                print(
                    f"[{result['run_mode']}] {result['name']}: "
                    f"steps={step_history['actual_steps']}/{step_history['expected_steps']}, "
                    f"unsafe={result['unsafe_step_count']}, "
                    f"dR={reaction['max_absolute']:.6g} kN, "
                    f"time={result['total_seconds']:.2f}s",
                    flush=True,
                )

    payload = {
        "schema_version": 1,
        "wall_seconds": time.perf_counter() - started,
        "workers": workers,
        "results": sorted(results, key=lambda item: (item["run_mode"], item["name"])),
    }
    (args.output_dir / "article_models_csharp_verification.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    (args.output_dir / "article_models_csharp_verification.md").write_text(
        _markdown_report(results), encoding="utf-8"
    )
    return 1 if any("error" in result for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
