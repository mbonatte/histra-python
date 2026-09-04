"""Run a reproducible, correctness-first nonlinear strategy matrix."""
from __future__ import annotations

import argparse
import copy
from importlib import metadata
import json
from pathlib import Path
import platform
import sys
import time
from typing import Any, Mapping

from histra.io import load_model
from histra.solver import AnalysisSession
from histra.solver.model_manager import ModelManager
from histra.tools.article_models_benchmark import compute_curve_metrics, _file_sha256


def _peak_rss_bytes() -> int | None:
    try:
        import resource
    except ImportError:
        return None
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if platform.system() == "Darwin" else value * 1024


def _candidate_curve(execution: Any, analysis: Any) -> tuple[list[float], list[float]]:
    direction = (
        float(getattr(analysis, "dir_x", 0.0)),
        float(getattr(analysis, "dir_y", 0.0)),
        float(getattr(analysis, "dir_z", 0.0)),
    )
    initial = execution.initial_step
    reaction0 = (
        float(initial.reaction_x or 0.0),
        float(initial.reaction_y or 0.0),
        float(initial.reaction_z or 0.0),
    )
    displacement0 = float(initial.get("displacement", 0.0))
    x: list[float] = []
    y: list[float] = []
    for step in execution.committed_steps:
        x.append((float(step.get("displacement", 0.0)) - displacement0) * 10.0)
        reaction = (
            float(step.reaction_x or 0.0),
            float(step.reaction_y or 0.0),
            float(step.reaction_z or 0.0),
        )
        y.append(sum((reaction[i] - reaction0[i]) * direction[i] for i in range(3)))
    return x, y


def run_candidate(
    hrx_path: Path,
    target: str,
    candidate: Mapping[str, Any],
    *,
    max_steps: int | None,
) -> dict[str, Any]:
    model = load_model(hrx_path)
    preparation_started = time.perf_counter()
    ModelManager.prepare_model(model)
    preparation_seconds = time.perf_counter() - preparation_started
    session = AnalysisSession(
        model,
        equilibrium_policy="error",
        strategy_policy="off",
    )
    chain = session.dependency_chain(target)
    target_definition = chain[-1]
    for field in (
        "integration_method", "method", "adaptive_convergence_criteria",
        "pdelta_effect", "convergence_tolerance",
    ):
        if field in candidate:
            setattr(target_definition, field, candidate[field])
    started = time.perf_counter()
    executions = []
    for definition in chain:
        execution = session.run(
            definition,
            max_committed_steps=max_steps if definition is target_definition else None,
        )
        executions.append(execution)
        if not execution.completed:
            break
    runtime_seconds = time.perf_counter() - started
    target_execution = executions[-1]
    x, y = _candidate_curve(target_execution, target_definition)
    steps = [step for execution in executions for step in execution.steps]
    terminal_step = next(
        (execution.steps[-1] for execution in reversed(executions) if execution.steps),
        None,
    )
    return {
        "id": str(candidate["id"]),
        "configuration": {
            field: getattr(target_definition, field)
            for field in (
                "integration_method", "method", "adaptive_convergence_criteria",
                "pdelta_effect", "convergence_tolerance",
            )
        },
        "completed": len(executions) == len(chain) and all(item.completed for item in executions),
        "unsafe_steps": sum(step.equilibrium_ok is False for step in steps),
        "committed_steps": sum(len(item.committed_steps) for item in executions),
        "iterations": sum(int(step.get("iterations", 0)) for step in steps),
        # These counters are cumulative on the session's LinearSystem. Reading
        # only the last available step avoids double-counting dependency stages.
        "linear_solves": int(terminal_step.get("linear_solve_count", 0)) if terminal_step else 0,
        "factorizations": int(terminal_step.get("factorization_count", 0)) if terminal_step else 0,
        "preparation_seconds": preparation_seconds,
        "runtime_seconds": runtime_seconds,
        "peak_rss_bytes": _peak_rss_bytes(),
        "curve": {"displacement_mm": x, "load_kn": y},
    }


def qualify_candidates(results: list[dict[str, Any]], baseline_id: str) -> None:
    baseline = next(item for item in results if item["id"] == baseline_id)
    baseline_curve = baseline["curve"]
    for result in results:
        curve = result["curve"]
        response = compute_curve_metrics(
            baseline_curve["displacement_mm"], baseline_curve["load_kn"],
            curve["displacement_mm"], curve["load_kn"],
        )
        result["response_vs_baseline"] = response
        result["qualifies"] = bool(
            result["completed"]
            and result["unsafe_steps"] == 0
            and response.get("within_curve_tolerance", False)
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("matrix", type=Path, help="JSON matrix definition")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    definition = json.loads(args.matrix.read_text(encoding="utf-8"))
    hrx_path = Path(definition["hrx"]).resolve()
    candidates = list(definition["candidates"])
    if not candidates or len({item["id"] for item in candidates}) != len(candidates):
        parser.error("candidates must contain unique ids")
    results = [
        run_candidate(
            hrx_path,
            str(definition["target"]),
            copy.deepcopy(candidate),
            max_steps=definition.get("max_steps"),
        )
        for candidate in candidates
    ]
    baseline_id = str(definition.get("baseline_id", candidates[0]["id"]))
    qualify_candidates(results, baseline_id)
    qualifying = [item for item in results if item["qualifies"]]
    recommended = min(qualifying, key=lambda item: item["runtime_seconds"])["id"] if qualifying else None
    packages: dict[str, str] = {}
    for package in ("histra-python", "numpy", "scipy", "numba"):
        try:
            packages[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            packages[package] = "not-installed"
    payload = {
        "schema_version": 1,
        "scenario": definition.get("scenario"),
        "environment": {
            "platform": platform.platform(),
            "python": sys.version.split()[0],
            "packages": packages,
            "warmup_policy": definition.get("warmup_policy", "fresh model per candidate; no unrecorded warm-up"),
            "repetitions": 1,
        },
        "hrx": {"path": str(hrx_path), "sha256": _file_sha256(hrx_path)},
        "target": definition["target"],
        "baseline_id": baseline_id,
        "recommended_id": recommended,
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 0 if recommended is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())
