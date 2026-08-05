"""Run one HRX modal analysis and export summaries/mode shapes.

Example:
    python -m histra.tools.run_modal bridge.hrx --analysis Modal_-1 \
        --output modal.json --shapes modal_shapes.npz
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from histra.io.hr_loader import load_model
from histra.solver.modal import solve_modal_analysis


def _resolve_analysis(model: Any, selector: str) -> Any:
    if selector.lstrip("-").isdigit():
        key = int(selector)
        try:
            return model.collections.analyses[key]
        except KeyError as exc:
            raise SystemExit(f"Analysis key {key} is absent from the HRX.") from exc
    matches = [
        analysis
        for analysis in model.collections.analyses.values()
        if str(analysis.name).casefold() == selector.casefold()
    ]
    if len(matches) != 1:
        raise SystemExit(
            f"Expected exactly one analysis named {selector!r}; found {len(matches)}."
        )
    return matches[0]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("hrx", type=Path, help="HiStrA .hrx model")
    parser.add_argument(
        "--analysis",
        required=True,
        help="Modal analysis key or exact name",
    )
    parser.add_argument(
        "--results",
        type=Path,
        help="C# .Results database required by a chained modal analysis",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write modal summaries as JSON",
    )
    parser.add_argument(
        "--shapes",
        type=Path,
        help="Write mode_shapes, frequencies and eigenvalues as compressed NPZ",
    )
    args = parser.parse_args()

    model = load_model(args.hrx)
    analysis = _resolve_analysis(model, args.analysis)
    result = solve_modal_analysis(
        model,
        analysis,
        results_path=args.results,
        on_log=print,
    )

    print(
        f"Completed {result.analysis_name}: {result.converged_modes}/"
        f"{result.requested_modes} modes, {result.dof_count} DOFs, "
        f"{result.runtime_seconds:.3f} s"
    )
    print("Mode       Fn [Hz]          T [s]       Mx [%]       My [%]       Mz [%]")
    for mode in result.modes:
        print(
            f"{mode.mode_number:4d}  {mode.frequency:14.8f}  {mode.period:13.8f}  "
            f"{mode.mass_percent_x:11.6f}  {mode.mass_percent_y:11.6f}  "
            f"{mode.mass_percent_z:11.6f}"
        )

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result.as_dict(include_shapes=False), indent=2),
            encoding="utf-8",
        )
        print(f"Modal summary written to {args.output}")

    if args.shapes is not None:
        args.shapes.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            args.shapes,
            mode_shapes=result.mode_shapes,
            frequencies=result.frequencies,
            angular_frequencies=result.angular_frequencies,
            periods=result.periods,
            eigenvalues=np.asarray([mode.eigenvalue for mode in result.modes]),
        )
        print(f"Mode shapes written to {args.shapes}")


if __name__ == "__main__":
    main()
