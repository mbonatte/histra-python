from __future__ import annotations

from types import SimpleNamespace
import warnings

import pytest

from histra import (
    SuboptimalSolverStrategyWarning,
    inspect_solver_strategy,
)
from histra.solver.session import AnalysisSession


def _analysis(
    *,
    key: int = 1,
    name: str = "Live",
    integration: str = "ArcLength",
    method: str = "ModifiedRegulaFalsiLineSearch",
    criterion: str = "Work",
    analysis_type: int = 2,
) -> SimpleNamespace:
    return SimpleNamespace(
        key=key,
        name=name,
        initial_analysis_key=-100,
        integration_method=integration,
        method=method,
        adaptive_convergence_criteria=criterion,
        analysis_type=analysis_type,
        pdelta_effect="None",
        max_u=1.0,
    )


def _model(*analyses: SimpleNamespace) -> SimpleNamespace:
    return SimpleNamespace(
        collections=SimpleNamespace(analyses={item.key: item for item in analyses}),
        gdl=1,
    )


def test_strategy_inspection_is_read_only_and_structured() -> None:
    analysis = _analysis()
    model = _model(analysis)

    report = inspect_solver_strategy(model, ["Live"])

    assert not report.recommended
    assert [item.code for item in report.advisories] == [
        "HISTRA-STRATEGY-001",
        "HISTRA-STRATEGY-002",
    ]
    assert analysis.method == "ModifiedRegulaFalsiLineSearch"
    assert analysis.adaptive_convergence_criteria == "Work"


def test_recommended_force_moment_arc_length_has_no_advisory() -> None:
    analysis = _analysis(
        method="StandardRegulaFalsiLineSearch",
        criterion="ForceMoment",
    )

    assert inspect_solver_strategy(_model(analysis), [1]).recommended


def test_session_emits_warning_and_log_once(monkeypatch: pytest.MonkeyPatch) -> None:
    analysis = _analysis()
    model = _model(analysis)
    logs: list[str] = []
    monkeypatch.setattr(
        "histra.solver.session.solve_static_nonlinear",
        lambda *args, **kwargs: (
            0,
            [
                {
                    "step": 1,
                    "status": "OK",
                    "exit_code": 0,
                    "u": [0.0],
                    "reaction_x": 0.0,
                    "reaction_y": 0.0,
                    "reaction_z": 0.0,
                }
            ],
        ),
    )
    session = AnalysisSession(model, on_log=logs.append)

    with pytest.warns(SuboptimalSolverStrategyWarning) as captured:
        session.run("Live")

    assert len(captured) == 2
    assert sum("HISTRA-STRATEGY-001" in item for item in logs) == 1
    assert sum("HISTRA-STRATEGY-002" in item for item in logs) == 1


def test_strategy_policy_off_is_silent(monkeypatch: pytest.MonkeyPatch) -> None:
    analysis = _analysis()
    model = _model(analysis)
    monkeypatch.setattr(
        "histra.solver.session.solve_static_nonlinear",
        lambda *args, **kwargs: (0, []),
    )
    session = AnalysisSession(model, strategy_policy="off")

    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        session.run("Live")

    assert not captured


@pytest.mark.parametrize("policy", ["", "error", "ignore"])
def test_strategy_policy_rejects_unknown_values(policy: str) -> None:
    with pytest.raises(ValueError, match="strategy_policy"):
        AnalysisSession(_model(_analysis()), strategy_policy=policy)
