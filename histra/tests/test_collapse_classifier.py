"""Tests for Feature 4: Automatic Local/Global Collapse Classification."""
from __future__ import annotations

import math
import numpy as np
import pytest

from histra.collapse import (
    ClassificationResult,
    ClassifierThresholds,
    CollapseCategory,
    EvidenceBundle,
    ExecutionClassificationReport,
    ReviewPriority,
    classify_bridge_components,
    classify_bridge_interfaces,
    classify_collapse_mechanism,
    classify_execution,
)
from histra.io.hr_loader import load_model
from histra.solver.model_manager import ModelManager
from histra.solver.outcomes import AnalysisExecution, AnalysisOutcome, AnalysisStep


class TestCollapseClassifierCategories:
    """Test decision logic across all 7 collapse mechanism categories."""

    def test_no_significant_failure_event(self):
        """Monotonic or small displacement state with no load drop or hinges."""
        m = load_model("histra/model-live/model.hrx")
        ModelManager.prepare_model(m, force=True)

        u0 = np.zeros(m.gdl, dtype=float)
        res = classify_collapse_mechanism(
            m,
            displacement_vector=u0,
            load_current=1.0,
            load_peak=1.0,
            monitored_displacement=0.01,
            solver_status="OK",
            solver_outcome="completed",
        )

        assert res.category == CollapseCategory.NO_SIGNIFICANT_FAILURE_EVENT
        assert res.review_priority == ReviewPriority.LOW
        assert res.confidence_score >= 0.85
        assert not res.is_global
        assert not res.is_local_backfill

    def test_local_backfill_failure(self):
        """Punch-through in backfill directly under load while arch remains quiescent."""
        m = load_model("histra/model-live/model.hrx")
        ModelManager.prepare_model(m, force=True)
        cls = classify_bridge_components(m)

        # Move only backfill quads 1 and 2 vertically downwards by 3.0 cm
        u = np.zeros(m.gdl, dtype=float)
        for qk in [1, 2]:
            q = m.collections.quads[qk]
            for entry in q.aff[2]:
                u[entry.gdl - 1] = -3.0

        res = classify_collapse_mechanism(
            m,
            displacement_vector=u,
            load_current=0.70,
            load_peak=1.0,  # 30% load drop
            monitored_displacement=-3.0,
            solver_status="OK",
            solver_outcome="completed",
            classification=cls,
        )

        assert res.category == CollapseCategory.LOCAL_BACKFILL_FAILURE
        assert res.is_local_backfill
        assert not res.is_global
        assert res.review_priority == ReviewPriority.LOW
        assert res.confidence_score >= 0.85
        assert res.evidence.arch_hinge_count == 0
        assert res.evidence.backfill_sliding_area_fraction > 0.15
        assert any("backfill" in r.lower() for r in res.rationale)

    def test_global_bridge_mechanism(self):
        """Formation of multiple arch hinges with high rotation triggers GLOBAL_BRIDGE_MECHANISM."""
        m = load_model("histra/model-live/model.hrx")
        ModelManager.prepare_model(m, force=True)
        cls = classify_bridge_components(m)

        # Produce multi-hinge mechanism: rotate quads across both sides of the arch vault
        u = np.zeros(m.gdl, dtype=float)
        u[46] = 0.02   # Quad 7 (GDL 47)
        u[53] = -0.02  # Quad 8 (GDL 54)
        u[109] = 0.02  # Quad 16 (GDL 110)
        u[116] = -0.02 # Quad 17 (GDL 117)

        res = classify_collapse_mechanism(
            m,
            displacement_vector=u,
            load_current=0.60,
            load_peak=1.0,  # 40% load drop
            monitored_displacement=-1.5,
            solver_status="OK",
            solver_outcome="completed",
            classification=cls,
        )

        assert res.category == CollapseCategory.GLOBAL_BRIDGE_MECHANISM
        assert res.is_global
        assert not res.is_local_backfill
        assert res.confidence_score >= 0.85
        assert res.evidence.arch_hinge_count >= 2
        assert any("hinge" in r.lower() for r in res.rationale)

    def test_single_span_mechanism_on_multi_span_bridge(self):
        """On a 2-span bridge, hinges forming only in Span 1 yields SINGLE_SPAN_MECHANISM."""
        m = load_model("histra/model-chain/model.hrx")
        ModelManager.prepare_model(m, force=True)
        cls = classify_bridge_components(m)

        u = np.zeros(m.gdl, dtype=float)
        # Rotate quads in Span 1 arch
        span_1_quads = cls.arch_spans["span_1"]
        for qk in span_1_quads[:4]:
            q = m.collections.quads[qk]
            # Set rotation DOF (aff index 5 -> phi_y)
            if len(q.aff) > 4:
                for entry in q.aff[4]:
                    u[entry.gdl - 1] = 0.03

        res = classify_collapse_mechanism(
            m,
            displacement_vector=u,
            load_current=0.65,
            load_peak=1.0,
            monitored_displacement=-2.0,
            solver_status="OK",
            solver_outcome="completed",
            classification=cls,
        )

        assert res.category in (CollapseCategory.SINGLE_SPAN_MECHANISM, CollapseCategory.GLOBAL_BRIDGE_MECHANISM)
        if res.category == CollapseCategory.SINGLE_SPAN_MECHANISM:
            assert "span_1" in res.primary_mechanism_description.lower()
        assert res.is_global

    def test_local_masonry_failure(self):
        """Only 1 isolated hinge with low active mass gives LOCAL_MASONRY_FAILURE."""
        m = load_model("histra/model-live/model.hrx")
        ModelManager.prepare_model(m, force=True)
        cls = classify_bridge_components(m)

        u = np.zeros(m.gdl, dtype=float)
        # Tiny rotation on only Quad 8 producing 1 hinge
        u[53] = 0.015

        res = classify_collapse_mechanism(
            m,
            displacement_vector=u,
            load_current=0.90,
            load_peak=1.0,
            monitored_displacement=-0.1,
            solver_status="OK",
            solver_outcome="completed",
            classification=cls,
            thresholds=ClassifierThresholds(arch_hinge_mechanism_count=3),
        )

        assert res.category == CollapseCategory.LOCAL_MASONRY_FAILURE
        assert not res.is_global
        assert not res.is_local_backfill
        assert res.review_priority == ReviewPriority.MEDIUM

    def test_numerical_or_uncertain(self):
        """Solver failure without physical collapse mechanism triggers NUMERICAL_OR_UNCERTAIN."""
        m = load_model("histra/model-live/model.hrx")
        ModelManager.prepare_model(m, force=True)

        # Micro-displacements at linear solver precision floor
        u = np.full(m.gdl, 1.0e-7)

        res = classify_collapse_mechanism(
            m,
            displacement_vector=u,
            load_current=0.98,
            load_peak=1.0,
            monitored_displacement=-0.001,
            solver_status="FAILED",
            solver_outcome="nonconverged",
            iterations=40,
        )

        assert res.category == CollapseCategory.NUMERICAL_OR_UNCERTAIN
        assert res.is_uncertain
        assert res.review_priority == ReviewPriority.HIGH
        assert any("solver" in r.lower() or "nonconvergence" in r.lower() for r in res.rationale)


class TestExecutionClassifier:
    """Test full execution analysis and critical collapse event localization."""

    def test_classify_execution_clean_run(self):
        m = load_model("histra/model-live/model.hrx")
        ModelManager.prepare_model(m, force=True)

        # Build synthetic step sequence: ascending steps
        u0 = np.zeros(m.gdl, dtype=float)
        u1 = np.zeros(m.gdl, dtype=float)
        u1[0] = 0.05
        u2 = np.zeros(m.gdl, dtype=float)
        u2[0] = 0.10

        s0 = AnalysisStep.initial(u0)
        s1 = AnalysisStep.from_mapping({"step": 1, "status": "OK", "u": u1, "load_factor": 0.5, "displacement": -0.05})
        s2 = AnalysisStep.from_mapping({"step": 2, "status": "OK", "u": u2, "load_factor": 1.0, "displacement": -0.10})

        exec_res = AnalysisExecution(
            analysis_key=1,
            analysis_name="PushDown_Vert",
            code=0,
            steps=(s1, s2),
            runtime_seconds=1.2,
            outcome=AnalysisOutcome.COMPLETED,
            initial_step=s0,
        )

        report = classify_execution(m, exec_res)
        assert report.analysis_name == "PushDown_Vert"
        assert report.peak_load_factor == 1.0
        assert report.result.category == CollapseCategory.NO_SIGNIFICANT_FAILURE_EVENT

        # Check dictionary serialization for batch comparison
        rep_dict = report.to_dict()
        assert rep_dict["analysis_key"] == 1
        assert "classification" in rep_dict
        assert rep_dict["classification"]["category"] == "NO_SIGNIFICANT_FAILURE_EVENT"
        assert "evidence" in rep_dict["classification"]

    def test_classify_execution_post_peak_drop(self):
        m = load_model("histra/model-live/model.hrx")
        ModelManager.prepare_model(m, force=True)
        cls = classify_bridge_components(m)

        # Step 1: peak load factor 1.2
        u1 = np.zeros(m.gdl, dtype=float)
        s1 = AnalysisStep.from_mapping({"step": 1, "status": "OK", "u": u1, "load_factor": 1.2, "displacement": -0.5})

        # Step 2: load drop to 0.7 with heavy backfill punch-through
        u2 = np.zeros(m.gdl, dtype=float)
        for qk in [1, 2]:
            q = m.collections.quads[qk]
            for entry in q.aff[2]:
                u2[entry.gdl - 1] = -3.5
        s2 = AnalysisStep.from_mapping({"step": 2, "status": "OK", "u": u2, "load_factor": 0.7, "displacement": -3.5})

        exec_res = AnalysisExecution(
            analysis_key=2,
            analysis_name="PushDown_Failure",
            code=0,
            steps=(s1, s2),
            runtime_seconds=2.5,
            outcome=AnalysisOutcome.COMPLETED,
            initial_step=AnalysisStep.initial(u1),
        )

        report = classify_execution(m, exec_res, classification=cls)
        assert report.critical_step_index == 1  # Step 2 (0-indexed 1) where drop occurred
        assert report.result.category == CollapseCategory.LOCAL_BACKFILL_FAILURE
        assert report.result.evidence.load_drop_ratio > 0.40
        assert report.result.review_priority == ReviewPriority.LOW
