"""Strict tests for the compact Article Models benchmark harness."""
from __future__ import annotations

import numpy as np
import pytest

from histra.tools.article_models_benchmark import (
    ARTICLE_FIGURES,
    ARTICLE_TABLE_1_CAPACITIES_KN,
    AUDIT_RESIDUAL_TOLERANCE,
    BENCHMARK_MODELS,
    compare_phase_distributions,
    compute_curve_metrics,
    compute_parity_metrics,
    _markdown_report,
    _progress_line,
    strict_convergence_tolerance,
    validate_article_source_data,
)


def test_registry_covers_all_models_article_figures_and_table_capacities() -> None:
    assert len(BENCHMARK_MODELS) == 14
    assert len({item["id"] for item in BENCHMARK_MODELS}) == 14
    assert set(ARTICLE_FIGURES) == {
        figure for item in BENCHMARK_MODELS for figure in item["figures"]
    }
    assert ARTICLE_TABLE_1_CAPACITIES_KN == {
        "3.1": 540.0, "3.2": 360.0, "3.3": 600.0, "3.4": 320.0,
        "5.1": 1720.0, "5.2": 500.0, "MS1": 455.0, "MS2": 320.0,
        "MS3": 325.0,
    }


@pytest.mark.parametrize(
    ("authored", "expected"),
    [
        (1.0e-2, 1.0e-4),
        (1.0e-4, 1.0e-4),
        (1.0e-6, 1.0e-6),
    ],
)
def test_strict_force_moment_tolerance_never_loosens_limits(
    authored: float,
    expected: float,
) -> None:
    actual = strict_convergence_tolerance(authored)
    assert actual == expected
    assert actual <= authored
    assert actual <= AUDIT_RESIDUAL_TOLERANCE


@pytest.mark.parametrize("invalid", [0.0, -1.0, np.inf, np.nan])
def test_strict_force_moment_tolerance_rejects_invalid_values(invalid: float) -> None:
    with pytest.raises(ValueError, match="finite and positive"):
        strict_convergence_tolerance(invalid)


def test_parity_compares_signed_all_component_vectors() -> None:
    csharp_reactions = {
        (1, 0): np.array([0.0, 0.0, 0.0]),
        (1, 1): np.array([1.0, -2.0, 3.0]),
        (2, 1): np.array([4.0, 5.0, -6.0]),
    }
    python_reactions = {
        (1, 0): np.array([999.0, 999.0, 999.0]),
        (1, 1): np.array([-1.0, -2.0, 3.0]),
        (2, 1): np.array([4.0, 5.0, -6.0]),
    }
    csharp_displacements = {
        (1, 1, 7): np.array([0.1, 0.2, -0.3]),
        (2, 1, 9): np.array([0.4, -0.5, 0.6]),
    }
    python_displacements = {
        (1, 1, 7): np.array([0.1, 0.2, -0.29]),
        (2, 1, 9): np.array([0.4, -0.5, 0.6]),
    }

    metrics = compute_parity_metrics(
        csharp_reactions,
        python_reactions,
        csharp_displacements,
        python_displacements,
    )

    assert metrics["complete_step_history"]
    assert not metrics["within_parity_tolerance"]
    assert metrics["reaction"]["max_absolute"] == 2.0
    assert metrics["reaction"]["worst_key"] == [1, 1]
    assert metrics["reaction"]["worst_component"] == 0
    assert metrics["model_point_displacement_mm"]["max_absolute"] == pytest.approx(0.1)
    assert metrics["model_point_displacement_mm"]["worst_key"] == [1, 1, 7]


def test_parity_fails_closed_on_missing_or_extra_history_rows() -> None:
    reference_reactions = {
        (1, 1): np.zeros(3),
        (1, 2): np.ones(3),
    }
    actual_reactions = {
        (1, 1): np.zeros(3),
        (1, 3): np.ones(3),
    }
    reference_displacements = {
        (1, 1, 5): np.zeros(3),
        (1, 2, 5): np.ones(3),
    }
    actual_displacements = {(1, 1, 5): np.zeros(3)}

    metrics = compute_parity_metrics(
        reference_reactions,
        actual_reactions,
        reference_displacements,
        actual_displacements,
    )

    assert not metrics["complete_step_history"]
    assert not metrics["within_parity_tolerance"]
    assert metrics["reaction"]["missing_rows"] == 1
    assert metrics["reaction"]["extra_rows"] == 1
    assert metrics["model_point_displacement_mm"]["missing_rows"] == 1
    assert metrics["model_point_displacement_mm"]["extra_rows"] == 0


def test_sparse_csharp_output_rows_do_not_look_like_missing_solver_steps() -> None:
    reference_reactions = {(1, 1): np.zeros(3), (1, 5): np.ones(3)}
    actual_reactions = {
        (1, step): np.zeros(3) if step == 1 else np.ones(3)
        for step in range(1, 6)
    }
    reference_displacements = {(1, 5, 7): np.ones(3)}
    actual_displacements = {
        (1, step, 7): np.ones(3)
        for step in range(1, 6)
    }

    metrics = compute_parity_metrics(
        reference_reactions,
        actual_reactions,
        reference_displacements,
        actual_displacements,
        expected_steps={(1, step) for step in range(1, 6)},
        actual_steps={(1, step) for step in range(1, 6)},
    )

    assert metrics["complete_step_history"]
    assert metrics["reference_outputs_complete"]
    assert metrics["within_parity_tolerance"]
    assert metrics["reaction"]["extra_rows"] == 3
    assert metrics["model_point_displacement_mm"]["extra_rows"] == 4


def test_curve_metrics_apply_release_acceptance_limits() -> None:
    reference_x = [0.0, 1.0, 2.0, 3.0]
    reference_y = [0.0, 10.0, 19.0, 20.0]
    passing = compute_curve_metrics(
        reference_x, reference_y, reference_x, [0.0, 10.02, 19.02, 20.02]
    )
    failing = compute_curve_metrics(
        reference_x, reference_y, reference_x, [0.0, 8.0, 15.0, 16.0]
    )
    assert passing["within_curve_tolerance"]
    assert not failing["within_curve_tolerance"]


def test_phase_distribution_comparison_fails_closed() -> None:
    matched = compare_phase_distributions({0: 2, 4: 1}, {0: 2, 4: 1})
    assert matched["available"]
    assert matched["exact"]
    report = compare_phase_distributions({0: 2, 4: 1}, {0: 3})
    assert not report["exact"]
    assert report["mismatches"]["4"] == {"csharp": 1, "python": 0}

    missing = compare_phase_distributions({}, {0: 3})
    assert not missing["available"]
    assert not missing["exact"]
    assert missing["reason"] == "no C# SpringStates rows at the terminal step"


def test_progress_line_handles_a_strict_run_without_comparable_rows() -> None:
    result = {
        "run_mode": "strict",
        "name": "Bridge",
        "unsafe_step_count": 0,
        "total_seconds": 1.25,
        "parity": {
            "step_history": {"actual_steps": 0, "expected_steps": 10},
            "reaction": {"max_absolute": None},
        },
    }
    assert "dR=n/a" in _progress_line(result)


def test_markdown_report_uses_na_when_strict_run_has_no_comparable_rows() -> None:
    result = {
        "run_mode": "strict",
        "name": "Bridge",
        "unsafe_step_count": 0,
        "release_gate_pass": False,
        "parity": {
            "step_history": {"actual_steps": 0, "expected_steps": 10},
            "reaction": {"max_absolute": None},
            "model_point_displacement_mm": {"max_absolute": None},
        },
    }

    report = _markdown_report([result])

    assert "| strict | Bridge | 0/10 | 0 | n/a | n/a | NOT RELEASE-READY |" in report


def test_article_source_data_validation_is_fail_closed_and_hashes_inputs(tmp_path) -> None:
    missing = validate_article_source_data(tmp_path)
    assert not missing["valid"]
    assert len(missing["issues"]) == len(ARTICLE_FIGURES) + 1

    for figure in ARTICLE_FIGURES:
        (tmp_path / f"figure_{figure:02d}.csv").write_text(
            "series,displacement_mm,load_kn,provenance\n"
            "experiment,0,0,user-original\n"
            "experiment,1,2,user-original\n",
            encoding="utf-8",
        )
    table_rows = "".join(
        f"{specimen},{capacity},user-original\n"
        for specimen, capacity in ARTICLE_TABLE_1_CAPACITIES_KN.items()
    )
    (tmp_path / "table_01.csv").write_text(
        "specimen,capacity_kn,provenance\n" + table_rows,
        encoding="utf-8",
    )

    report = validate_article_source_data(tmp_path)
    assert report["valid"]
    assert report["issues"] == []
    assert report["figures"]["9"]["rows"] == 2
    assert len(report["figures"]["9"]["sha256"]) == 64
    assert report["table_1"]["capacities_kn"]["MS1"] == 455.0
