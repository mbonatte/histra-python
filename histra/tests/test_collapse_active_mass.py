"""Tests for the Active Mass Fraction and regional span diagnostics."""
from __future__ import annotations

import math
import numpy as np
import pytest

from histra.collapse import (
    ActiveMassCriteria,
    ActiveMassIndex,
    ExecutionActiveMassReport,
    RegionalActiveMassSummary,
    StepActiveMassReport,
    classify_bridge_components,
    compute_active_mass_fraction,
    compute_active_mass_sensitivity,
    evaluate_execution_active_mass,
    evaluate_regional_active_mass,
    evaluate_step_active_mass,
)
from histra.io.hr_loader import load_model
from histra.solver.model_manager import ModelManager
from histra.solver.outcomes import AnalysisExecution, AnalysisOutcome, AnalysisStep


class TestActiveMassMath:
    """Test mathematical invariants of M_active = Σ(m_i for active points) / Σ(m_i)."""

    def test_uniform_motion_gives_one(self):
        """When all points move identically above noise floor, M_active = 1.0 (100%)."""
        masses = np.array([10.0, 20.0, 30.0, 40.0])
        disps = np.full(4, 0.5)  # 0.5 cm > 1e-4 cm
        res = compute_active_mass_fraction(masses, disps)
        assert res.status == "VALID"
        assert math.isclose(res.fraction, 1.0, rel_tol=1e-12)
        assert math.isclose(res.fraction_percentage, 100.0, rel_tol=1e-12)
        assert res.active_points_count == 4
        assert res.total_points_count == 4
        assert res.mobility_extent == "GLOBAL"

    def test_localized_single_point_motion(self):
        """When only 1 of N points moves, M_active = m_k / M_total."""
        masses = np.array([5.0, 15.0, 30.0, 50.0])  # total = 100.0
        # Only point 0 has displacement 1.0 cm, others 0.0
        disps = np.array([1.0, 0.0, 0.0, 0.0])
        res = compute_active_mass_fraction(masses, disps, criteria=ActiveMassCriteria(relative_threshold=0.10))
        assert res.status == "VALID"
        assert math.isclose(res.fraction, 5.0 / 100.0, rel_tol=1e-12)
        assert res.active_points_count == 1
        assert res.total_points_count == 4
        assert res.mobility_extent == "LOCALIZED"

    def test_relative_threshold_discrimination(self):
        """Points below relative_threshold * a_max are excluded from active mass."""
        masses = np.array([10.0, 10.0, 10.0, 10.0])
        # Peak is 1.0 cm; threshold at 10% is 0.10 cm
        disps = np.array([1.0, 0.15, 0.08, 0.02])
        # Point 0 (1.0 >= 0.10) active, Point 1 (0.15 >= 0.10) active,
        # Point 2 (0.08 < 0.10) inactive, Point 3 (0.02 < 0.10) inactive
        res = compute_active_mass_fraction(masses, disps, criteria=ActiveMassCriteria(relative_threshold=0.10))
        assert res.status == "VALID"
        assert res.active_points_count == 2
        assert math.isclose(res.fraction, 20.0 / 40.0, rel_tol=1e-12)
        assert math.isclose(res.threshold_used, 0.10, rel_tol=1e-12)

    def test_absolute_noise_floor_rejection(self):
        """When displacements are below absolute_threshold (e.g. 1e-4 cm), status is NO_MOTION."""
        masses = np.array([10.0, 20.0])
        # Tiny numerical roundoff: peak 5e-5 cm < 1e-4 cm
        disps = np.array([5e-5, 2e-5])
        res = compute_active_mass_fraction(masses, disps, criteria=ActiveMassCriteria(absolute_threshold=1e-4))
        assert res.status == "NO_MOTION"
        assert res.fraction == 0.0
        assert res.active_mass == 0.0
        assert res.active_points_count == 0
        assert not res.has_motion

    def test_absolute_floor_overrides_tiny_relative_threshold(self):
        """Even if relative threshold would be 1e-6 cm, absolute floor 1e-4 cm cuts off chatter."""
        masses = np.array([10.0, 10.0])
        # Peak is 5e-4 cm; 10% would be 5e-5 cm, but absolute floor is 1e-4 cm
        # Point 0: 5e-4 cm (active since >= 1e-4 cm)
        # Point 1: 8e-5 cm (inactive since < 1e-4 cm, even though > 5e-5 cm)
        disps = np.array([5e-4, 8e-5])
        res = compute_active_mass_fraction(masses, disps, criteria=ActiveMassCriteria(relative_threshold=0.10, absolute_threshold=1e-4))
        assert res.status == "VALID"
        assert res.active_points_count == 1
        assert math.isclose(res.fraction, 0.5, rel_tol=1e-12)
        assert math.isclose(res.threshold_used, 1e-4, rel_tol=1e-12)

    def test_directional_active_mass(self):
        """Directional filtering extracts motion along specified global axis."""
        masses = np.array([10.0, 10.0])
        # Point 0 moves in X only, Point 1 moves in Z only
        vecs = np.array([
            [1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0],
        ])
        crit_x = ActiveMassCriteria(direction="x", relative_threshold=0.10)
        crit_z = ActiveMassCriteria(direction="z", relative_threshold=0.10)
        crit_y = ActiveMassCriteria(direction="y", relative_threshold=0.10)

        res_x = compute_active_mass_fraction(masses, vecs, criteria=crit_x)
        assert res_x.status == "VALID"
        assert res_x.active_points_count == 1
        assert math.isclose(res_x.fraction, 0.5, rel_tol=1e-12)

        res_z = compute_active_mass_fraction(masses, vecs, criteria=crit_z)
        assert res_z.status == "VALID"
        assert res_z.active_points_count == 1
        assert math.isclose(res_z.fraction, 0.5, rel_tol=1e-12)

        res_y = compute_active_mass_fraction(masses, vecs, criteria=crit_y)
        assert res_y.status == "NO_MOTION"
        assert res_y.fraction == 0.0

    def test_sensitivity_profile_monotonicity(self):
        """Active mass fraction must be monotonically non-increasing as relative threshold increases."""
        masses = np.array([10.0, 15.0, 25.0, 50.0])
        disps = np.array([1.0, 0.45, 0.15, 0.05])
        thresholds = (0.01, 0.05, 0.10, 0.20, 0.50, 0.80)
        curve = compute_active_mass_sensitivity(masses, disps, thresholds=thresholds)

        fractions = [curve[t] for t in thresholds]
        for i in range(len(fractions) - 1):
            assert fractions[i] >= fractions[i + 1]


class TestMultiSpanClassificationAndPartitioning:
    """Test bridge multi-span arch connectivity clustering and backfill allocation."""

    def test_model_chain_span_partitioning(self):
        """model-chain has 2 distinct spans: 18 arch quads each, and 96 backfill quads partitioned 48/48."""
        m = load_model("histra/model-chain/model.hrx")
        cls = classify_bridge_components(m)

        assert len(cls.arch_spans) == 2
        assert "span_1" in cls.arch_spans
        assert "span_2" in cls.arch_spans
        assert len(cls.arch_spans["span_1"]) == 18
        assert len(cls.arch_spans["span_2"]) == 18

        # Backfill spans partitioned across midpoint
        assert len(cls.backfill_spans) == 2
        assert "span_1" in cls.backfill_spans
        assert "span_2" in cls.backfill_spans
        assert len(cls.backfill_spans["span_1"]) == 48
        assert len(cls.backfill_spans["span_2"]) == 48

    def test_single_span_bridge_model_live(self):
        """model-live has 1 span: all 4 arch quads in span_1."""
        m = load_model("histra/model-live/model.hrx")
        cls = classify_bridge_components(m)

        assert len(cls.arch_spans) == 1
        assert "span_1" in cls.arch_spans
        assert len(cls.arch_spans["span_1"]) == 4


class TestRegionalActiveMassEvaluation:
    """Test regional active mass summary across structure, arch, piers, and backfill."""

    def test_regional_active_mass_backfill_localization(self):
        """Synthetic punch-through in backfill with quiescent arch barrel."""
        m = load_model("histra/model-live/model.hrx")
        ModelManager.prepare_model(m, force=True)
        cls = classify_bridge_components(m)

        # Displacements: only backfill quads move downwards 2.0 cm; arch quads move 0.0001 cm (at noise floor)
        u_step = np.zeros(m.gdl, dtype=float)
        for qkey in cls.backfill_quad_keys:
            q = m.collections.quads[qkey]
            for entry in q.aff[2]:
                u_step[entry.gdl - 1] = -2.0
        for qkey in cls.arch_quad_keys:
            q = m.collections.quads[qkey]
            for entry in q.aff[2]:
                u_step[entry.gdl - 1] = -1.0e-5

        crit = ActiveMassCriteria(relative_threshold=0.10, absolute_threshold=1.0e-4)
        summary = evaluate_regional_active_mass(m, u_step, classification=cls, criteria=crit)

        # Backfill is 100% active
        assert summary.backfill.is_valid
        assert math.isclose(summary.backfill.fraction, 1.0, rel_tol=1e-6)

        # Arch barrel motion is 1e-5 cm < 1e-4 cm absolute floor -> NO_MOTION
        assert summary.arch_barrel.status == "NO_MOTION"
        assert summary.arch_barrel.fraction == 0.0

        # Ratios reflect severe backfill concentration
        assert summary.backfill_to_structure_active_ratio > 10.0

    def test_global_vs_group_reference_scope(self):
        """Global reference scope uses global peak; group scope uses group peak."""
        m = load_model("histra/model-live/model.hrx")
        ModelManager.prepare_model(m, force=True)
        cls = classify_bridge_components(m)

        # Backfill moves 10.0 cm, Arch moves 0.5 cm
        u_step = np.zeros(m.gdl, dtype=float)
        for qkey in cls.backfill_quad_keys:
            q = m.collections.quads[qkey]
            for entry in q.aff[2]:
                u_step[entry.gdl - 1] = -10.0
        for qkey in cls.arch_quad_keys:
            q = m.collections.quads[qkey]
            for entry in q.aff[2]:
                u_step[entry.gdl - 1] = -0.5

        # Group scope: arch peak is 0.5 cm, threshold = max(0.10 * 0.5, 1e-4) = 0.05 cm. Arch is active!
        crit_group = ActiveMassCriteria(relative_threshold=0.10, reference_scope="group")
        sum_group = evaluate_regional_active_mass(m, u_step, classification=cls, criteria=crit_group)
        assert sum_group.arch_barrel.fraction > 0.90

        # Global scope: global peak is 10.0 cm, threshold = max(0.10 * 10.0, 1e-4) = 1.0 cm.
        # Arch motion (0.5 cm) is below 1.0 cm -> Arch is inactive under global scope!
        crit_global = ActiveMassCriteria(relative_threshold=0.10, reference_scope="global")
        sum_global = evaluate_regional_active_mass(m, u_step, classification=cls, criteria=crit_global)
        assert sum_global.arch_barrel.fraction == 0.0

    def test_multi_span_active_mass_isolation(self):
        """Applying displacement to only Span 1 of a multi-span bridge isolates active mass to Span 1."""
        m = load_model("histra/model-chain/model.hrx")
        ModelManager.prepare_model(m, force=True)
        cls = classify_bridge_components(m)

        u_step = np.zeros(m.gdl, dtype=float)
        # Move only Span 1 arch quads
        for qkey in cls.arch_spans["span_1"]:
            q = m.collections.quads[qkey]
            for entry in q.aff[2]:
                u_step[entry.gdl - 1] = -1.5

        crit = ActiveMassCriteria(relative_threshold=0.10, absolute_threshold=1.0e-4)
        summary = evaluate_regional_active_mass(m, u_step, classification=cls, criteria=crit)

        assert "span_1" in summary.arch_spans
        assert "span_2" in summary.arch_spans
        assert summary.arch_spans["span_1"].fraction > 0.90
        assert summary.arch_spans["span_2"].status == "NO_MOTION"
        assert summary.arch_spans["span_2"].fraction == 0.0


class TestStepAndExecutionActiveMass:
    """Test full step-level and execution-level active mass evaluation."""

    def test_evaluate_step_active_mass(self):
        m = load_model("histra/model-live/model.hrx")
        ModelManager.prepare_model(m, force=True)
        cls = classify_bridge_components(m)

        u0 = np.zeros(m.gdl, dtype=float)
        step0 = AnalysisStep.initial(u0)

        # Step 1: backfill punch-through
        u1 = np.zeros(m.gdl, dtype=float)
        for qkey in cls.backfill_quad_keys:
            q = m.collections.quads[qkey]
            for entry in q.aff[2]:
                u1[entry.gdl - 1] = -3.0

        step1 = AnalysisStep.from_mapping({
            "step": 1,
            "status": "OK",
            "exit_code": 0,
            "u": u1,
            "load_factor": 1.0,
            "displacement": -3.0,
        })

        crit = ActiveMassCriteria(relative_threshold=0.10, absolute_threshold=1.0e-4)
        report = evaluate_step_active_mass(m, step1, previous_step=step0, initial_step=step0, classification=cls, criteria=crit)

        assert report.step == 1
        assert report.incremental.backfill.fraction == 1.0
        assert report.cumulative.backfill.fraction == 1.0
        assert report.incremental.arch_barrel.status == "NO_MOTION"
        assert len(report.interpretation_notes) > 0
        assert any("backfill" in n.lower() for n in report.interpretation_notes)

    def test_evaluate_execution_active_mass(self):
        m = load_model("histra/model-live/model.hrx")
        ModelManager.prepare_model(m, force=True)

        u0 = np.zeros(m.gdl, dtype=float)
        u1 = np.zeros(m.gdl, dtype=float)
        u1[0] = 0.5
        u2 = np.zeros(m.gdl, dtype=float)
        u2[0] = 1.0

        step0 = AnalysisStep.initial(u0)
        step1 = AnalysisStep.from_mapping({"step": 1, "status": "OK", "u": u1, "load_factor": 0.5, "displacement": 0.5})
        step2 = AnalysisStep.from_mapping({"step": 2, "status": "OK", "u": u2, "load_factor": 1.0, "displacement": 1.0})

        exec_res = AnalysisExecution(
            analysis_key=22,
            analysis_name="LiveLoad_1",
            code=0,
            steps=(step1, step2),
            runtime_seconds=1.5,
            outcome=AnalysisOutcome.COMPLETED,
            initial_step=step0,
        )

        exec_report = evaluate_execution_active_mass(m, exec_res)
        assert exec_report.analysis_name == "LiveLoad_1"
        assert len(exec_report.steps) == 2
        assert "committed_step_count" in exec_report.summary
        assert exec_report.summary["committed_step_count"] == 2

        # Verify serialization to dict for batch comparison
        as_dict = exec_report.to_dict()
        assert as_dict["analysis_key"] == 22
        assert len(as_dict["steps"]) == 2
        assert "criteria" in as_dict
        assert as_dict["criteria"]["relative_threshold"] == 0.10
