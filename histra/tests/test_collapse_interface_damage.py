"""Tests for Feature 3: Nonlinear Interface, Hinge Detection, and Damage Participation."""
from __future__ import annotations

import math
import numpy as np
import pytest

from histra.collapse import (
    DamageParticipationSummary,
    ExecutionInterfaceReport,
    InterfaceActivityRecord,
    InterfaceClassification,
    InterfaceCriteria,
    InterfaceForces,
    InterfaceKinematics,
    RegionalInterfaceSummary,
    StepInterfaceReport,
    classify_bridge_components,
    classify_bridge_interfaces,
    compute_spatial_concentration,
    evaluate_damage_participation,
    evaluate_execution_interface_damage,
    evaluate_step_interface_damage,
    extract_interface_constitutive,
    extract_interface_forces,
    extract_interface_kinematics,
)
from histra.io.hr_loader import load_model
from histra.solver.model_manager import ModelManager
from histra.solver.outcomes import AnalysisExecution, AnalysisOutcome, AnalysisStep


class TestSpatialConcentrationMath:
    """Test invariants of area-weighted spatial concentration index C."""

    def test_uniform_activity_gives_one(self):
        """Uniform activity across all interface areas yields C = 1.0."""
        areas = np.array([100.0, 250.0, 50.0, 500.0])
        activities = np.full(4, 2.5)
        c = compute_spatial_concentration(areas, activities)
        assert math.isclose(c, 1.0, rel_tol=1e-12)

    def test_single_active_interface(self):
        """When only interface k is active, C = A_k / A_total."""
        areas = np.array([20.0, 80.0, 100.0])  # Total = 200.0
        # Only interface 0 is active
        activities = np.array([5.0, 0.0, 0.0])
        c = compute_spatial_concentration(areas, activities)
        expected = 20.0 / 200.0  # 0.10
        assert math.isclose(c, expected, rel_tol=1e-12)

    def test_zero_activity_gives_zero(self):
        """When all activities are zero, C = 0.0."""
        areas = np.array([100.0, 200.0])
        activities = np.array([0.0, 0.0])
        c = compute_spatial_concentration(areas, activities)
        assert c == 0.0

    def test_scale_invariance(self):
        """Multiplying activity field by positive scalar leaves C invariant."""
        areas = np.array([10.0, 50.0, 30.0])
        act1 = np.array([0.2, 1.5, 0.05])
        act2 = act1 * 42.0
        c1 = compute_spatial_concentration(areas, act1)
        c2 = compute_spatial_concentration(areas, act2)
        assert math.isclose(c1, c2, rel_tol=1e-12)


class TestInterfaceClassification:
    """Test bridge interface component categorization."""

    def test_model_live_interface_classification(self):
        m = load_model("histra/model-live/model.hrx")
        ModelManager.prepare_model(m, force=True)
        cls = classify_bridge_components(m)
        intf_cls = classify_bridge_interfaces(m, cls)

        assert len(intf_cls.all_interface_keys) == 29
        assert len(intf_cls.backfill_interface_keys) == 16
        assert len(intf_cls.backfill_contact_interface_keys) == 6
        assert len(intf_cls.foundation_interface_keys) == 2
        # Arch interfaces (including arch-pier)
        assert len(intf_cls.arch_interface_keys) == 5
        assert len(intf_cls.masonry_structure_interface_keys) == 7

    def test_model_chain_multi_span_interfaces(self):
        m = load_model("histra/model-chain/model.hrx")
        ModelManager.prepare_model(m, force=True)
        cls = classify_bridge_components(m)
        intf_cls = classify_bridge_interfaces(m, cls)

        assert len(intf_cls.all_interface_keys) == 365
        assert len(intf_cls.backfill_interface_keys) == 202
        assert len(intf_cls.backfill_contact_interface_keys) == 48
        assert len(intf_cls.foundation_interface_keys) == 12
        assert len(intf_cls.arch_interface_keys) == 66  # 54 arch + 12 arch-pier
        assert len(intf_cls.pier_interface_keys) == 37

        # Spans partitioned
        assert len(intf_cls.arch_spans) == 2
        assert "span_1" in intf_cls.arch_spans
        assert "span_2" in intf_cls.arch_spans
        assert len(intf_cls.arch_spans["span_1"]) > 0
        assert len(intf_cls.arch_spans["span_2"]) > 0


class TestInterfaceKinematicsExtraction:
    """Test relative normal opening, sliding, in-plane rotation, and hinge detection."""

    def test_relative_opening_and_sliding(self):
        m = load_model("histra/model-live/model.hrx")
        ModelManager.prepare_model(m, force=True)
        intf = m.collections.interfaces[1]  # unconstrained interface between Quad 1 and 2

        # Create synthetic displacement vector
        # Apply normal separation (local DOF 3 moves +0.5 cm, local DOF 0 moves 0.0)
        u_global = np.zeros(m.gdl, dtype=float)
        for entry in intf.aff[3]:
            u_global[entry.gdl - 1] = 0.5

        kin = extract_interface_kinematics(intf, u_global)
        assert kin.is_opening
        assert kin.opening_max > 0.40
        assert kin.opening_mean > 0.20

    def test_flexural_hinge_candidate_detection(self):
        """A joint with opening on one edge, compression on the other, and rotation is a hinge candidate."""
        m = load_model("histra/model-live/model.hrx")
        ModelManager.prepare_model(m, force=True)
        intf = m.collections.interfaces[13]  # Arch interface between Quad 7 and 8

        # Produce flexural bending: rotate Quad 8 by 0.02 rad (GDL 54 -> index 53)
        u_global = np.zeros(m.gdl, dtype=float)
        u_global[53] = 0.02

        crit = InterfaceCriteria(hinge_opening_tolerance=0.05, hinge_rotation_tolerance=1e-4)
        kin = extract_interface_kinematics(intf, u_global, criteria=crit)

        assert kin.opening_max >= 0.05
        assert abs(kin.rotation_in_plane) > 1e-4
        assert kin.is_hinge_candidate

    def test_pure_sliding_without_opening(self):
        """Relative sliding along interface tangent without separation."""
        m = load_model("histra/model-live/model.hrx")
        ModelManager.prepare_model(m, force=True)
        intf = m.collections.interfaces[4]  # Contact interface between Quad 1 and 7

        # Apply horizontal translation to Quad 1 (GDL 1, ux) = 0.5 cm
        u_global = np.zeros(m.gdl, dtype=float)
        u_global[0] = 0.5

        kin = extract_interface_kinematics(intf, u_global)
        assert kin.is_sliding
        assert kin.sliding_magnitude >= 0.20
        assert not kin.is_hinge_candidate


class TestDamageParticipationSummary:
    """Test component-level failure activity and dissipation summaries."""

    def test_damage_participation_on_model_live(self):
        m = load_model("histra/model-live/model.hrx")
        ModelManager.prepare_model(m, force=True)
        cls = classify_bridge_components(m)
        intf_cls = classify_bridge_interfaces(m, cls)

        # Zero displacement: all quiescent
        u0 = np.zeros(m.gdl, dtype=float)
        summary = evaluate_damage_participation(m, u0, classification=cls, intf_classification=intf_cls)

        assert summary.arch_barrel.hinge_candidate_count == 0
        assert summary.backfill.sliding_interface_count == 0
        assert summary.dominant_mechanism == "DISTRIBUTED_OR_ELASTIC"
        assert len(summary.hinge_candidate_keys) == 0

    def test_simulated_backfill_punch_through_dominance(self):
        """Heavy sliding in backfill interfaces with quiescent arch produces LOCAL_BACKFILL_FAILURE."""
        m = load_model("histra/model-live/model.hrx")
        ModelManager.prepare_model(m, force=True)
        cls = classify_bridge_components(m)
        intf_cls = classify_bridge_interfaces(m, cls)

        # Move only backfill quads 1 and 2 vertically down (localized punch-through)
        u_step = np.zeros(m.gdl, dtype=float)
        for qkey in [1, 2]:
            q = m.collections.quads[qkey]
            for entry in q.aff[2]:  # uz
                u_step[entry.gdl - 1] = -2.0

        summary = evaluate_damage_participation(m, u_step, classification=cls, intf_classification=intf_cls)

        # Backfill sliding is activated
        assert summary.backfill.sliding_interface_count > 0
        assert summary.backfill.sliding_area_fraction > 0.15

        # Arch barrel has no hinges
        assert summary.arch_barrel.hinge_candidate_count == 0
        assert summary.dominant_mechanism in ("LOCAL_BACKFILL_FAILURE", "BACKFILL_ARCH_CONTACT_SLIP")


class TestStepAndExecutionInterfaceDamage:
    """Test step-level and execution-level interface damage evaluation."""

    def test_evaluate_step_interface_damage(self):
        m = load_model("histra/model-live/model.hrx")
        ModelManager.prepare_model(m, force=True)
        cls = classify_bridge_components(m)
        intf_cls = classify_bridge_interfaces(m, cls)

        u0 = np.zeros(m.gdl, dtype=float)
        step0 = AnalysisStep.initial(u0)

        # Step 1: backfill punch-through displacement
        u1 = np.zeros(m.gdl, dtype=float)
        for qkey in [1, 2]:
            q = m.collections.quads[qkey]
            for entry in q.aff[2]:
                u1[entry.gdl - 1] = -1.5

        step1 = AnalysisStep.from_mapping({
            "step": 1,
            "status": "OK",
            "exit_code": 0,
            "u": u1,
            "load_factor": 1.0,
            "displacement": -1.5,
        })

        report = evaluate_step_interface_damage(
            m, step1, previous_step=step0, initial_step=step0, classification=cls, intf_classification=intf_cls
        )
        assert report.step == 1
        assert report.cumulative.backfill.sliding_interface_count > 0
        assert len(report.interpretation_notes) > 0
        assert any("backfill" in n.lower() for n in report.interpretation_notes)

    def test_evaluate_execution_interface_damage_serialization(self):
        m = load_model("histra/model-live/model.hrx")
        ModelManager.prepare_model(m, force=True)

        u0 = np.zeros(m.gdl, dtype=float)
        u1 = np.zeros(m.gdl, dtype=float)
        u1[0] = 0.5

        step0 = AnalysisStep.initial(u0)
        step1 = AnalysisStep.from_mapping({"step": 1, "status": "OK", "u": u1, "load_factor": 1.0, "displacement": 0.5})

        exec_res = AnalysisExecution(
            analysis_key=22,
            analysis_name="LiveLoad_1",
            code=0,
            steps=(step1,),
            runtime_seconds=1.0,
            outcome=AnalysisOutcome.COMPLETED,
            initial_step=step0,
        )

        exec_report = evaluate_execution_interface_damage(m, exec_res)
        assert exec_report.analysis_name == "LiveLoad_1"
        assert len(exec_report.steps) == 1

        # Check JSON serialization
        as_dict = exec_report.to_dict()
        assert as_dict["analysis_key"] == 22
        assert "steps" in as_dict
        assert "terminal_dominant_mechanism" in as_dict["summary"]
