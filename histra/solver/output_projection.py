"""Backend-facing projection of in-memory solver results."""
from __future__ import annotations

from typing import Any, Iterable

from histra.solver.outcomes import AnalysisExecution, AnalysisStep


class OutputProjectionError(RuntimeError):
    """Raised when requested output cannot be projected from an execution."""


class UnsupportedOutputError(OutputProjectionError):
    """Raised when the Python solver does not yet implement an output family."""


def project_reactions(execution: AnalysisExecution, request: Any) -> list[dict[str, Any]]:
    """Project reactions using the Job Runner's ``ReactionSumStates`` shape."""
    selected = _select_steps(execution.output_steps, request)
    rows: list[dict[str, Any]] = []
    for step in selected:
        if step.reaction_x is None or step.reaction_y is None or step.reaction_z is None:
            raise OutputProjectionError(
                f"Analysis {execution.analysis_name!r} step {step.step} has no committed reaction."
            )
        rows.append(
            {
                "Step": int(step.step),
                "R1": float(step.reaction_x),
                "R2": float(step.reaction_y),
                "R3": float(step.reaction_z),
            }
        )
    return rows


def project_analysis_outputs(
    model: Any,
    execution: AnalysisExecution,
    request: Any,
) -> dict[str, Any]:
    """Project supported outputs without depending on Job Runner classes."""
    del model
    result: dict[str, Any] = {}

    reactions = getattr(request, "reactions", None)
    if reactions is not None and bool(getattr(reactions, "enabled", False)):
        result["reactions"] = project_reactions(execution, reactions)

    displacements = getattr(request, "displacements", None)
    if displacements is not None and bool(getattr(displacements, "enabled", False)):
        raise UnsupportedOutputError(
            "Exact DisplModelPoints projection is not implemented. The mapping of HRX "
            "ModelPoint identifiers and interpolation to C# IdElement/ParentKey rows must "
            "first be verified against authoritative .Results fixtures."
        )

    modal = getattr(request, "modal_contributions", None)
    if modal is not None and bool(getattr(modal, "enabled", False)):
        raise UnsupportedOutputError(
            "Modal contribution projection is not supported by the Python solver."
        )

    return result


def _select_steps(
    available: Iterable[AnalysisStep],
    request: Any,
) -> tuple[AnalysisStep, ...]:
    steps = tuple(available)
    if not steps:
        raise OutputProjectionError("The analysis has no committed output steps.")

    if bool(getattr(request, "all_steps", False)):
        return steps

    requested_step = getattr(request, "step", None)
    if requested_step is not None:
        target = int(requested_step)
        selected = tuple(step for step in steps if step.step == target)
        if not selected:
            available_steps = ", ".join(str(step.step) for step in steps)
            raise OutputProjectionError(
                f"Requested step {target} is unavailable; available steps: {available_steps}."
            )
        return selected

    return (steps[-1],)
