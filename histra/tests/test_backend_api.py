from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

import numpy as np
import pytest

from histra.solver.cancellation import CANCELLED_EXIT_CODE, SolverCancelled, raise_if_cancelled
from histra.solver.capabilities import inspect_solver_capabilities
from histra.solver.outcomes import (
    AnalysisExecution,
    AnalysisOutcome,
    AnalysisStep,
    classify_analysis_outcome,
)
from histra.solver.output_projection import (
    OutputProjectionError,
    UnsupportedOutputError,
    project_analysis_outputs,
    project_reactions,
)


@dataclass(frozen=True)
class StepRequest:
    enabled: bool = True
    all_steps: bool = True
    step: int | None = None


@dataclass(frozen=True)
class OutputRequest:
    reactions: StepRequest
    displacements: StepRequest
    modal_contributions: StepRequest


def _committed(step: int, reaction: tuple[float, float, float]) -> AnalysisStep:
    return AnalysisStep.from_mapping(
        {
            "step": step,
            "status": "OK",
            "exit_code": 0,
            "u": np.array([float(step)]),
            "reaction_x": reaction[0],
            "reaction_y": reaction[1],
            "reaction_z": reaction[2],
        }
    )


def test_analysis_step_preserves_legacy_mapping_access() -> None:
    step = _committed(2, (1.0, 2.0, 3.0))

    assert step["step"] == 2
    assert step.get("status") == "OK"
    assert np.array_equal(step["u"], np.array([2.0]))
    assert dict(step)["reaction_z"] == 3.0


def test_displacement_limit_is_a_completed_outcome() -> None:
    terminal = AnalysisStep.from_mapping(
        {
            "step": 7,
            "status": "FAILED",
            "exit_code": -3,
            "u": np.zeros(1),
            "max_element_displacement": 0.125,
        }
    )
    analysis = SimpleNamespace(max_u=0.1)

    outcome = classify_analysis_outcome(-3, (terminal,), analysis)

    assert outcome is AnalysisOutcome.COMPLETED_AT_DISPLACEMENT_LIMIT


def test_cancellation_has_a_distinct_outcome() -> None:
    cancelled = AnalysisStep.from_mapping(
        {
            "step": 1,
            "status": "CANCELLED",
            "exit_code": CANCELLED_EXIT_CODE,
            "u": np.zeros(1),
        }
    )

    assert classify_analysis_outcome(
        CANCELLED_EXIT_CODE, (cancelled,), SimpleNamespace(max_u=1.0)
    ) is AnalysisOutcome.CANCELLED
    with pytest.raises(SolverCancelled):
        raise_if_cancelled(lambda: True)


def test_reaction_projection_includes_step_zero_and_committed_steps() -> None:
    execution = AnalysisExecution(
        analysis_key=3,
        analysis_name="Live",
        code=0,
        steps=(_committed(1, (10.0, 20.0, 30.0)), _committed(2, (11.0, 21.0, 31.0))),
        runtime_seconds=0.1,
        outcome=AnalysisOutcome.COMPLETED,
        initial_step=AnalysisStep.initial(np.zeros(1), reaction_x=1.0, reaction_y=2.0, reaction_z=3.0),
    )

    assert project_reactions(execution, StepRequest(all_steps=True)) == [
        {"Step": 0, "R1": 1.0, "R2": 2.0, "R3": 3.0},
        {"Step": 1, "R1": 10.0, "R2": 20.0, "R3": 30.0},
        {"Step": 2, "R1": 11.0, "R2": 21.0, "R3": 31.0},
    ]
    assert project_reactions(execution, StepRequest(all_steps=False, step=None)) == [
        {"Step": 2, "R1": 11.0, "R2": 21.0, "R3": 31.0}
    ]
    assert project_reactions(execution, StepRequest(all_steps=False, step=0)) == [
        {"Step": 0, "R1": 1.0, "R2": 2.0, "R3": 3.0}
    ]


def test_reaction_projection_rejects_missing_step() -> None:
    execution = AnalysisExecution(
        analysis_key=1,
        analysis_name="A",
        code=0,
        steps=(_committed(1, (1.0, 2.0, 3.0)),),
        runtime_seconds=0.0,
        outcome=AnalysisOutcome.COMPLETED,
        initial_step=AnalysisStep.initial(np.zeros(1)),
    )
    with pytest.raises(OutputProjectionError, match="Requested step 99"):
        project_reactions(execution, StepRequest(all_steps=False, step=99))


def test_output_projection_rejects_uninitialized_model() -> None:
    execution = AnalysisExecution(
        analysis_key=1, analysis_name="A", code=0,
        steps=(_committed(1, (1.0, 2.0, 3.0)),), runtime_seconds=0.0,
        outcome=AnalysisOutcome.COMPLETED,
        initial_step=AnalysisStep.initial(np.zeros(1)),
    )
    request = OutputRequest(
        reactions=StepRequest(enabled=False),
        displacements=StepRequest(enabled=True),
        modal_contributions=StepRequest(enabled=False),
    )
    with pytest.raises(OutputProjectionError, match="Model.collections"):
        project_analysis_outputs(object(), execution, request)


def test_output_projection_includes_modal_summary() -> None:
    modal_result = SimpleNamespace(
        as_dict=lambda include_shapes=False: {
            "converged_modes": 2,
            "include_shapes": include_shapes,
        }
    )
    execution = AnalysisExecution(
        analysis_key=30,
        analysis_name="Modal",
        code=0,
        steps=(),
        runtime_seconds=0.1,
        outcome=AnalysisOutcome.COMPLETED,
        initial_step=AnalysisStep.initial(np.zeros(3)),
        modal_result=modal_result,
    )
    request = SimpleNamespace(
        include_modal_shapes=True,
        reactions=StepRequest(enabled=False),
        displacements=StepRequest(enabled=False),
        modal_contributions=StepRequest(enabled=False),
    )

    assert project_analysis_outputs(SimpleNamespace(collections=object()), execution, request) == {
        "modal_analysis": {"converged_modes": 2, "include_shapes": True}
    }


def test_capability_preflight_resolves_dependencies_and_outputs() -> None:
    root = SimpleNamespace(key=1, name="Root", initial_analysis_key=-100, pdelta_effect=False)
    child = SimpleNamespace(key=2, name="Child", initial_analysis_key=1, pdelta_effect=False)
    model = SimpleNamespace(collections=SimpleNamespace(analyses={1: root, 2: child}))
    request = OutputRequest(
        reactions=StepRequest(enabled=True),
        displacements=StepRequest(enabled=False),
        modal_contributions=StepRequest(enabled=False),
    )

    report = inspect_solver_capabilities(
        model,
        ["Child"],
        output_requests={"Child": request},
    )

    assert report.supported
    assert report.issues == ()
