from types import SimpleNamespace

import pytest

from histra.tools.strategy_benchmark import _apply_candidate_overrides, qualify_candidates


def _result(identifier: str, load: list[float], *, completed: bool = True, unsafe: int = 0):
    return {
        "id": identifier,
        "completed": completed,
        "unsafe_steps": unsafe,
        "curve": {
            "displacement_mm": [0.0, 1.0, 2.0],
            "load_kn": load,
        },
    }


def test_qualification_is_correctness_first() -> None:
    results = [
        _result("baseline", [0.0, 10.0, 20.0]),
        _result("fast-safe", [0.0, 10.01, 20.01]),
        _result("unsafe", [0.0, 10.0, 20.0], unsafe=1),
        _result("drift", [0.0, 8.0, 15.0]),
    ]

    qualify_candidates(results, "baseline")

    assert [item["qualifies"] for item in results] == [True, True, False, False]

    results[1]["range_covered"] = False
    qualify_candidates(results, "baseline")
    assert not results[1]["qualifies"]


def test_candidate_can_override_dependency_strategies_without_mutating_others() -> None:
    vert = SimpleNamespace(name="Vert", method="ModifiedNewtonRaphson")
    live = SimpleNamespace(
        name="Live", method="ModifiedNewtonRaphson",
        adaptive_convergence_criteria="Work",
    )
    _apply_candidate_overrides(
        [vert, live],
        {
            "id": "safe",
            "method": "StandardRegulaFalsiLineSearch",
            "adaptive_convergence_criteria": "ForceMoment",
            "analysis_overrides": {
                "Vert": {"method": "StandardRegulaFalsiLineSearch"},
            },
        },
    )
    assert vert.method == "StandardRegulaFalsiLineSearch"
    assert live.method == "StandardRegulaFalsiLineSearch"
    assert live.adaptive_convergence_criteria == "ForceMoment"


def test_candidate_rejects_unknown_dependency_override() -> None:
    definition = SimpleNamespace(name="Vert")
    with pytest.raises(ValueError, match="Unsupported strategy override"):
        _apply_candidate_overrides(
            [definition],
            {"id": "bad", "analysis_overrides": {"Vert": {"future": 1}}},
        )
