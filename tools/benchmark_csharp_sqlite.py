#!/usr/bin/env python3
"""Run a HiStrA nonlinear analysis and compare every committed step to C# SQLite.

Run from the directory containing the ``histra`` package, for example::

    cd ..
    python -m histra.tools.benchmark_csharp_sqlite \
        --hrx histra/model-output/model.hrx \
        --results histra/model-output/model.Results \
        --analysis 1 --combination 1 \
        --output histra_benchmark_metrics.json
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import platform
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

# Permit direct execution from ``histra/tools`` without installing the package.
_PROJECT = Path(__file__).resolve().parents[1]
_PARENT = _PROJECT.parent
if str(_PARENT) not in sys.path:
    sys.path.insert(0, str(_PARENT))

from histra.io.hr_loader import load_model
from histra.io.results_reader import (
    read_analysis_metadata,
    read_global_displacements,
    read_load_multiplier,
)
from histra.solver.solve import solve_static_nonlinear


def _finite(value: Any) -> Any:
    if isinstance(value, (float, np.floating)):
        return float(value) if math.isfinite(float(value)) else None
    if isinstance(value, (int, np.integer)):
        return int(value)
    return value


def run_benchmark(
    hrx: Path,
    results: Path,
    analysis_key: int,
    combination: int,
    selected_dofs: list[int],
    echo_solver_log: bool,
) -> dict[str, Any]:
    model = load_model(hrx)
    try:
        analysis = copy.deepcopy(model.collections.analyses[analysis_key])
    except KeyError as exc:
        raise SystemExit(f"Analysis key {analysis_key} is absent from {hrx}") from exc

    metadata = read_analysis_metadata(results, analysis_key)
    reference_steps = metadata.steps_by_combination.get(combination, ())
    committed_steps = [step for step in reference_steps if step > 0]
    if not committed_steps:
        raise SystemExit(
            f"No committed C# steps for analysis {analysis_key}, combination {combination}"
        )

    # Read all references before solving. This keeps database I/O out of the
    # timing and ensures a malformed benchmark fails before mutating the model.
    references = {
        step: read_global_displacements(
            results, analysis_key, combination, step, model_or_hrx=model
        )
        for step in committed_steps
    }
    reference_multipliers = {
        step: read_load_multiplier(hrx, analysis_key, step) for step in committed_steps
    }

    logs: list[str] = []

    def on_log(message: str) -> None:
        logs.append(message)
        if echo_solver_log:
            print(message, flush=True)

    started = time.perf_counter()
    code, solved_steps = solve_static_nonlinear(
        model,
        analysis,
        combination,
        on_log=on_log,
        results_path=results,
    )
    elapsed = time.perf_counter() - started

    rows: list[dict[str, Any]] = []
    for record in solved_steps:
        step = int(record["step"])
        u = np.asarray(record["u"], dtype=float)
        ref = references.get(step)
        row: dict[str, Any] = {
            "step": step,
            "status": record["status"],
            "exit_code": int(record["exit_code"]),
            "load_factor": _finite(record.get("load_factor")),
            "iterations": int(record.get("iterations", 0)),
            "convergence_error": _finite(record.get("convergence_error")),
            "residual_norm": _finite(record.get("residual_norm")),
            "increment_norm": _finite(record.get("increment_norm")),
            "elastic_energy": _finite(record.get("elastic_energy")),
            "dissipated_energy": _finite(record.get("dissipated_energy")),
            "no_nan_or_infinite": bool(np.all(np.isfinite(u))),
            "selected_dofs": {
                str(dof): float(u[dof])
                for dof in selected_dofs
                if 0 <= dof < u.size
            },
        }
        if ref is not None:
            diff = u - ref
            denominator = max(float(np.linalg.norm(ref)), np.finfo(float).tiny)
            row.update(
                {
                    "reference_load_factor": float(reference_multipliers[step]),
                    "relative_displacement_error": float(np.linalg.norm(diff) / denominator),
                    "max_absolute_dof_difference": float(np.max(np.abs(diff))),
                    "python_displacement_norm": float(np.linalg.norm(u)),
                    "csharp_displacement_norm": float(np.linalg.norm(ref)),
                    "load_factor_absolute_error": abs(
                        float(record.get("load_factor", 0.0))
                        - float(reference_multipliers[step])
                    ),
                }
            )
        rows.append(row)

    solved_numbers = [row["step"] for row in rows if row["status"] == "OK"]
    expected_numbers = committed_steps
    metrics: dict[str, Any] = {
        "schema_version": 1,
        "benchmark": {
            "hrx": str(hrx.resolve()),
            "results": str(results.resolve()),
            "analysis_key": analysis_key,
            "analysis_name": str(getattr(analysis, "name", "")),
            "combination": combination,
            "integration_method": str(getattr(analysis, "integration_method", "")),
            "solution_method": str(getattr(analysis, "method", "")),
            "dof_count": int(model.gdl),
            "reference_steps": expected_numbers,
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
        },
        "run": {
            "completion_code": int(code),
            "completion_status": "completed" if code == 0 else "failed",
            "elapsed_seconds": elapsed,
            "steps_completed": solved_numbers,
            "step_order_exact": solved_numbers == expected_numbers,
            "all_values_finite": all(row["no_nan_or_infinite"] for row in rows),
        },
        "acceptance": {
            "global_displacement_relative_tolerance": 1.0e-4,
            "load_factor_absolute_tolerance": 1.0e-6,
            "per_step": {
                str(row["step"]): {
                    "displacement": row.get("relative_displacement_error", math.inf) <= 1.0e-4,
                    "load_factor": row.get("load_factor_absolute_error", math.inf) <= 1.0e-6,
                }
                for row in rows
            },
        },
        "steps": rows,
        "solver_log": logs,
    }
    return metrics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hrx", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--analysis", type=int, default=1)
    parser.add_argument("--combination", type=int, default=1)
    parser.add_argument("--selected-dofs", type=int, nargs="*", default=[0, 6, 42, 125])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--quiet", action="store_true", help="suppress live solver log")
    args = parser.parse_args()

    metrics = run_benchmark(
        args.hrx,
        args.results,
        args.analysis,
        args.combination,
        args.selected_dofs,
        not args.quiet,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(metrics, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    print(json.dumps(metrics["run"], indent=2))
    return 0 if metrics["run"]["completion_code"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
