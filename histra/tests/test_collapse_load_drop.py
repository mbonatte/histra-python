"""Tests for Feature 5: Automatic Detection and Diagnosis of Sharp Load Drops."""
from __future__ import annotations

import math
import numpy as np
import pytest

from histra.collapse import (
    ClassifierThresholds,
    CollapseCategory,
    LoadDropAnalysisReport,
    LoadDropCriteria,
    LoadDropEvent,
    LoadHistoryCurve,
    classify_bridge_components,
    detect_load_drop_events,
    evaluate_load_drop_analysis,
    extract_load_history,
)
from histra.io.hr_loader import load_model
from histra.solver.model_manager import ModelManager
from histra.solver.outcomes import AnalysisExecution, AnalysisOutcome, AnalysisStep


class TestLoadDropDetectionMath:
    """Test curve inspection and event localization."""

    def test_monotonic_ascending_curve_has_no_drop(self):
        """Monotonically increasing resistance yields no drop events."""
        curve = LoadHistoryCurve(
            steps=(1, 2, 3, 4),
            displacements=(-0.1, -0.2, -0.3, -0.4),
            load_factors=(0.25, 0.50, 0.75, 1.00),
            reactions_z=(25.0, 50.0, 75.0, 100.0),
            resistance_values=(0.25, 0.50, 0.75, 1.00),
            control_method="LoadControl",
            peak_load=1.0,
            displacement_at_peak_load=-0.4,
            peak_step=4,
            terminal_load=1.0,
            terminal_displacement=-0.4,
            terminal_step=4,
        )
        drops = detect_load_drop_events(curve)
        assert drops == []

    def test_sharp_drop_detection(self):
        """Single sharp load drop from 1.5 to 0.75 is detected."""
        curve = LoadHistoryCurve(
            steps=(1, 2, 3, 4, 5),
            displacements=(-0.1, -0.2, -0.3, -0.4, -0.5),
            load_factors=(0.5, 1.0, 1.5, 1.0, 0.75),
            reactions_z=(50.0, 100.0, 150.0, 100.0, 75.0),
            resistance_values=(0.5, 1.0, 1.5, 1.0, 0.75),
            control_method="LoadControl",
            peak_load=1.5,
            displacement_at_peak_load=-0.3,
            peak_step=3,
            terminal_load=0.75,
            terminal_displacement=-0.5,
            terminal_step=5,
        )
        drops = detect_load_drop_events(curve, LoadDropCriteria(drop_threshold=0.10))
        assert len(drops) == 1
        onset_idx, trough_idx = drops[0]
        assert onset_idx == 2  # Step 3 (index 2), load = 1.5
        assert trough_idx == 4  # Step 5 (index 4), load = 0.75

    def test_micro_chatter_filtered_out(self):
        """Fluctuations smaller than drop_threshold are ignored as numerical noise."""
        curve = LoadHistoryCurve(
            steps=(1, 2, 3, 4),
            displacements=(-0.1, -0.2, -0.3, -0.4),
            load_factors=(1.0, 1.01, 0.99, 1.02),
            reactions_z=(100.0, 101.0, 99.0, 102.0),
            resistance_values=(1.0, 1.01, 0.99, 1.02),
            control_method="LoadControl",
            peak_load=1.02,
            displacement_at_peak_load=-0.4,
            peak_step=4,
            terminal_load=1.02,
            terminal_displacement=-0.4,
            terminal_step=4,
        )
        # Drop is only ~1.9%, below default 5% threshold
        drops = detect_load_drop_events(curve, LoadDropCriteria(drop_threshold=0.05))
        assert drops == []


class TestLoadDropEvaluationAndDiagnosis:
    """Test full load-drop evaluation and physical cause diagnosis."""

    def test_evaluate_local_backfill_failure_drop(self):
        """Sharp drop caused by localized backfill punch-through with uncracked arch."""
        m = load_model("histra/model-live/model.hrx")
        ModelManager.prepare_model(m, force=True)
        cls = classify_bridge_components(m)

        # Pre-drop step 1: peak load 1.2, small elastic displacement
        u1 = np.zeros(m.gdl, dtype=float)
        s1 = AnalysisStep.from_mapping({"step": 1, "status": "OK", "u": u1, "load_factor": 1.2, "displacement": -0.2})

        # Post-drop step 2: load drops sharply to 0.6 (50% drop), with heavy backfill punch-through
        u2 = np.zeros(m.gdl, dtype=float)
        for qk in [1, 2]:
            q = m.collections.quads[qk]
            for entry in q.aff[2]:
                u2[entry.gdl - 1] = -3.5
        s2 = AnalysisStep.from_mapping({"step": 2, "status": "OK", "u": u2, "load_factor": 0.6, "displacement": -3.5})

        exec_res = AnalysisExecution(
            analysis_key=10,
            analysis_name="PushDown_PunchThrough",
            code=0,
            steps=(s1, s2),
            runtime_seconds=2.0,
            outcome=AnalysisOutcome.COMPLETED,
            initial_step=AnalysisStep.initial(u1),
        )

        report = evaluate_load_drop_analysis(m, exec_res, classification=cls)
        assert report.has_significant_drop
        assert len(report.events) == 1

        ev = report.primary_event
        assert ev is not None
        assert ev.onset_step == 1
        assert ev.trough_step == 2
        assert math.isclose(ev.relative_drop_ratio, 0.50, rel_tol=1e-3)
        assert ev.is_sharp
        assert ev.primary_cause == "LOCAL_BACKFILL"
        assert "LOCAL_BACKFILL_FAILURE" in ev.diagnosis
        assert "intact with 0 hinges" in ev.diagnosis

    def test_evaluate_structural_collapse_drop(self):
        """Sharp drop caused by arch hinge formation."""
        m = load_model("histra/model-live/model.hrx")
        ModelManager.prepare_model(m, force=True)
        cls = classify_bridge_components(m)

        # Pre-drop step 1: peak load 1.4
        u1 = np.zeros(m.gdl, dtype=float)
        s1 = AnalysisStep.from_mapping({"step": 1, "status": "OK", "u": u1, "load_factor": 1.4, "displacement": -0.3})

        # Post-drop step 2: load drops to 0.7 with 3 arch hinges formed
        u2 = np.zeros(m.gdl, dtype=float)
        u2[46] = 0.02   # Quad 7 (GDL 47)
        u2[53] = -0.02  # Quad 8 (GDL 54)
        u2[109] = 0.02  # Quad 16 (GDL 110)
        u2[116] = -0.02 # Quad 17 (GDL 117)
        s2 = AnalysisStep.from_mapping({"step": 2, "status": "OK", "u": u2, "load_factor": 0.7, "displacement": -1.8})

        exec_res = AnalysisExecution(
            analysis_key=11,
            analysis_name="PushDown_ArchCollapse",
            code=0,
            steps=(s1, s2),
            runtime_seconds=3.0,
            outcome=AnalysisOutcome.COMPLETED,
            initial_step=AnalysisStep.initial(u1),
        )

        report = evaluate_load_drop_analysis(m, exec_res, classification=cls)
        assert report.has_significant_drop
        assert report.primary_event is not None
        assert report.primary_event.primary_cause in ("STRUCTURAL_COLLAPSE", "SINGLE_SPAN_COLLAPSE")
        assert "hinge" in report.primary_event.diagnosis.lower()

    def test_evaluate_numerical_divergence_drop(self):
        """Drop coinciding with solver divergence without physical collapse."""
        m = load_model("histra/model-live/model.hrx")
        ModelManager.prepare_model(m, force=True)

        u1 = np.zeros(m.gdl, dtype=float)
        s1 = AnalysisStep.from_mapping({"step": 1, "status": "OK", "u": u1, "load_factor": 1.0, "displacement": -0.1})

        # Solver failed with small drop and micro-displacement
        u2 = np.full(m.gdl, 1.0e-6)
        s2 = AnalysisStep.from_mapping({"step": 2, "status": "FAILED", "u": u2, "load_factor": 0.85, "displacement": -0.11})

        exec_res = AnalysisExecution(
            analysis_key=12,
            analysis_name="PushDown_Divergence",
            code=1,
            steps=(s1, s2),
            runtime_seconds=1.5,
            outcome=AnalysisOutcome.NONCONVERGED,
            initial_step=AnalysisStep.initial(u1),
        )

        report = evaluate_load_drop_analysis(m, exec_res)
        assert report.has_significant_drop
        ev = report.primary_event
        assert ev is not None
        assert ev.coincides_with_failure
        assert ev.primary_cause == "NUMERICAL_UNCERTAINTY"
        assert "NUMERICAL_UNCERTAINTY" in ev.diagnosis

    def test_clean_analysis_without_drop(self):
        """Clean ascending push-down run has no significant drop."""
        m = load_model("histra/model-live/model.hrx")
        ModelManager.prepare_model(m, force=True)

        u1 = np.zeros(m.gdl, dtype=float)
        s1 = AnalysisStep.from_mapping({"step": 1, "status": "OK", "u": u1, "load_factor": 0.5, "displacement": -0.05})
        s2 = AnalysisStep.from_mapping({"step": 2, "status": "OK", "u": u1, "load_factor": 1.0, "displacement": -0.10})

        exec_res = AnalysisExecution(
            analysis_key=13,
            analysis_name="PushDown_Stable",
            code=0,
            steps=(s1, s2),
            runtime_seconds=1.0,
            outcome=AnalysisOutcome.COMPLETED,
            initial_step=AnalysisStep.initial(u1),
        )

        report = evaluate_load_drop_analysis(m, exec_res)
        assert not report.has_significant_drop
        assert report.primary_event is None
        assert "NO_SIGNIFICANT_DROP" in report.overall_diagnosis

        # Verify full dictionary serialization
        rep_dict = report.to_dict()
        assert rep_dict["analysis_key"] == 13
        assert rep_dict["has_significant_drop"] is False
        assert "curve" in rep_dict
        assert "summary" in rep_dict
