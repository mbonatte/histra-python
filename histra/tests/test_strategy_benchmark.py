from histra.tools.strategy_benchmark import qualify_candidates


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
