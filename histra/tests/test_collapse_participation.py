"""Tests for the Kinematic Participation Index and collapse diagnostics."""
from __future__ import annotations

import math
import numpy as np
import pytest

from histra.collapse import (
    BridgeClassification,
    KinematicParticipationIndex,
    RegionalParticipationSummary,
    StepParticipationReport,
    classify_bridge_components,
    compute_kinematic_participation,
    compute_quad_mass,
    evaluate_execution_participation,
    evaluate_regional_participation,
    evaluate_step_participation,
    sample_quad_displacements_and_masses,
)
from histra.io.hr_loader import load_model
from histra.postprocessing import _quad_local_displacement
from histra.solver.model_manager import ModelManager
from histra.solver.outcomes import AnalysisExecution, AnalysisOutcome, AnalysisStep


class TestKinematicParticipationMath:
    """Test mathematical invariants of K = [Σ(m_i × a_i)]² / [Σ(m_i) × Σ(m_i × a_i²)]."""

    def test_uniform_motion_gives_one(self):
        """Uniform displacement magnitude across any mass distribution yields K = 1.0 exactly."""
        masses = np.array([10.0, 25.0, 5.0, 100.0, 0.5])
        # Uniform magnitude 3.5
        disps = np.full(5, 3.5)
        res = compute_kinematic_participation(masses, disps)
        assert res.status == "VALID"
        assert res.k is not None
        assert math.isclose(res.k, 1.0, rel_tol=1e-12)
        assert res.spatial_distribution == "DISTRIBUTED"
        assert math.isclose(res.concentration_ratio, 1.0, rel_tol=1e-12)

    def test_cauchy_schwarz_upper_bound(self):
        """Random positive masses and displacements are strictly bounded in (0, 1]."""
        rng = np.random.default_rng(42)
        for _ in range(50):
            masses = rng.uniform(0.1, 100.0, size=20)
            disps = rng.uniform(0.001, 10.0, size=20)
            res = compute_kinematic_participation(masses, disps)
            assert res.status == "VALID"
            assert res.k is not None
            assert 0.0 <= res.k <= 1.0

    def test_localized_single_point_motion(self):
        """If only point k moves while others remain fixed, K = m_k / M_total."""
        masses = np.array([2.0, 8.0, 10.0])  # total = 20.0
        # Only point 0 moves
        disps = np.array([5.0, 0.0, 0.0])
        res = compute_kinematic_participation(masses, disps)
        assert res.status == "VALID"
        expected_k = 2.0 / 20.0  # 0.10
        assert res.k is not None
        assert math.isclose(res.k, expected_k, rel_tol=1e-12)
        assert res.spatial_distribution == "LOCALIZED"

    def test_scale_invariance(self):
        """Multiplying displacement field by any positive scalar leaves K unchanged."""
        masses = np.array([1.0, 2.0, 3.0, 4.0])
        disps1 = np.array([0.5, 1.2, 0.1, 3.0])
        disps2 = disps1 * 123.456

        res1 = compute_kinematic_participation(masses, disps1)
        res2 = compute_kinematic_participation(masses, disps2)
        assert res1.k is not None and res2.k is not None
        assert math.isclose(res1.k, res2.k, rel_tol=1e-12)

    def test_no_motion_status(self):
        """When displacements are zero or below tolerance, status is 'NO_MOTION'."""
        masses = np.array([10.0, 20.0])
        disps = np.array([1e-11, 0.0])
        res = compute_kinematic_participation(masses, disps, motion_tolerance=1e-9)
        assert res.status == "NO_MOTION"
        assert res.k is None
        assert not res.has_motion
        assert res.k_or_zero == 0.0

    def test_directional_participation(self):
        """Directional participation isolates ux, uy, uz components."""
        masses = np.array([5.0, 5.0])
        # Point 0 moves only in X, Point 1 moves only in Z
        vecs = np.array([
            [2.0, 0.0, 0.0],
            [0.0, 0.0, 2.0],
        ])
        res_x = compute_kinematic_participation(masses, vecs, direction="x")
        res_z = compute_kinematic_participation(masses, vecs, direction="z")
        res_y = compute_kinematic_participation(masses, vecs, direction="y")

        # In X direction: only point 0 moves -> K_x = 5 / 10 = 0.5
        assert res_x.k is not None
        assert math.isclose(res_x.k, 0.5, rel_tol=1e-12)

        # In Z direction: only point 1 moves -> K_z = 5 / 10 = 0.5
        assert res_z.k is not None
        assert math.isclose(res_z.k, 0.5, rel_tol=1e-12)

        # In Y direction: no motion -> NO_MOTION
        assert res_y.status == "NO_MOTION"
        assert res_y.k is None


class TestBridgeClassification:
    """Test bridge component identification on canonical HRX models."""

    def test_model_chain_classification(self):
        m = load_model("histra/model-chain/model.hrx")
        cls = classify_bridge_components(m)
        assert cls.has_backfill
        assert cls.has_arch
        assert cls.has_piers
        assert len(cls.backfill_quad_keys) == 96
        assert len(cls.arch_quad_keys) == 36
        assert len(cls.pier_quad_keys) == 24
        assert len(cls.total_structure_quad_keys) == 60
        assert len(cls.all_quad_keys) == 156

    def test_model_live_classification(self):
        m = load_model("histra/model-live/model.hrx")
        cls = classify_bridge_components(m)
        assert len(cls.backfill_quad_keys) == 12
        assert len(cls.arch_quad_keys) == 4
        assert len(cls.pier_quad_keys) == 2
        assert len(cls.total_structure_quad_keys) == 6
        assert len(cls.all_quad_keys) == 18

    def test_custom_classification_override(self):
        m = load_model("histra/model-live/model.hrx")
        custom = {
            "total_structure": [1, 2, 3],
            "backfill": [4, 5],
            "arch": [1, 2],
            "piers": [3],
        }
        cls = classify_bridge_components(m, custom_regions=custom)
        assert cls.total_structure_quad_keys == (1, 2, 3)
        assert cls.backfill_quad_keys == (4, 5)
        assert cls.arch_quad_keys == (1, 2)
        assert cls.pier_quad_keys == (3,)


class TestMacroElementKinematics:
    """Test that Quad sampling accounts for translations, rotations, and warping."""

    def test_pure_centroid_translation(self):
        m = load_model("histra/model-live/model.hrx")
        q = list(m.collections.quads.values())[0]

        # Global vector producing pure translation ux = 1.0, uy = 2.0, uz = 3.0 at centroid
        global_u = np.zeros(m.gdl, dtype=float)
        for i in range(3):
            for entry in q.aff[i]:
                # If unit entry
                global_u[entry.gdl - 1] = float(i + 1)

        disps_8, masses_8 = sample_quad_displacements_and_masses(q, m, global_u, kinematic_mode="volume_8point")
        assert disps_8.shape == (8, 3)
        assert masses_8.shape == (8,)
        assert math.isclose(np.sum(masses_8), compute_quad_mass(q, m), rel_tol=1e-9)

        # All 8 points translate identically
        for i in range(8):
            assert math.isclose(disps_8[i, 0], 1.0, abs_tol=1e-5)
            assert math.isclose(disps_8[i, 1], 2.0, abs_tol=1e-5)
            assert math.isclose(disps_8[i, 2], 3.0, abs_tol=1e-5)

    def test_rigid_rotation_detected_by_8point_sampling(self):
        """A pure rotation around centroid has u_G = 0, but 8-point sampling captures non-zero motion."""
        m = load_model("histra/model-live/model.hrx")
        q = list(m.collections.quads.values())[0]

        # Set rotation DOF phi_z (index 5) = 0.05 rad, with translation DOFs = 0
        global_u = np.zeros(m.gdl, dtype=float)
        for entry in q.aff[5]:
            global_u[entry.gdl - 1] = 0.05

        # Centroid sampling reports 0 translation
        disp_c, _ = sample_quad_displacements_and_masses(q, m, global_u, kinematic_mode="centroid")
        assert math.isclose(float(np.linalg.norm(disp_c)), 0.0, abs_tol=1e-9)

        # Volume 8-point sampling captures the non-zero rotational movement
        disp_8, _ = sample_quad_displacements_and_masses(q, m, global_u, kinematic_mode="volume_8point")
        magnitudes = np.linalg.norm(disp_8, axis=1)
        assert np.all(magnitudes > 1e-4)

    def test_warping_internal_deformation_captured(self):
        """Warping distortion (u_6) is captured at nodes 2 and 3."""
        m = load_model("histra/model-live/model.hrx")
        q = list(m.collections.quads.values())[0]

        # Set warping DOF (index 6) = 0.1
        global_u = np.zeros(m.gdl, dtype=float)
        for entry in q.aff[6]:
            global_u[entry.gdl - 1] = 0.1

        disp_8, _ = sample_quad_displacements_and_masses(q, m, global_u, kinematic_mode="volume_8point")
        # Nodes 2 and 3 have non-zero warping displacements
        assert np.max(np.linalg.norm(disp_8, axis=1)) > 1e-4


class TestStepAndExecutionParticipation:
    """Test full step-level and execution-level participation evaluation."""

    def test_evaluate_step_participation(self):
        m = load_model("histra/model-live/model.hrx")
        ModelManager.prepare_model(m, force=True)
        cls = classify_bridge_components(m)

        # Create synthetic steps
        # Step 0: initial zero
        u0 = np.zeros(m.gdl, dtype=float)
        step0 = AnalysisStep.initial(u0)

        # Step 1: backfill moves vertically downward by 2.0 cm, arch moves by 0.01 cm
        u1 = np.zeros(m.gdl, dtype=float)
        for qkey in cls.backfill_quad_keys:
            q = m.collections.quads[qkey]
            for entry in q.aff[2]:  # uz
                u1[entry.gdl - 1] = -2.0
        for qkey in cls.arch_quad_keys:
            q = m.collections.quads[qkey]
            for entry in q.aff[2]:
                u1[entry.gdl - 1] = -0.01

        step1 = AnalysisStep.from_mapping({
            "step": 1,
            "status": "OK",
            "exit_code": 0,
            "u": u1,
            "load_factor": 1.0,
            "displacement": -2.0,
        })

        report = evaluate_step_participation(m, step1, previous_step=step0, initial_step=step0, classification=cls)
        assert report.step == 1
        assert report.incremental.k_backfill.is_valid
        assert report.incremental.k_total_structure.is_valid
        # Backfill moved uniformly -> K_backfill == 1.0
        assert math.isclose(report.incremental.k_backfill.k_or_zero, 1.0, rel_tol=1e-6)
        # Backfill displacement is 200x arch displacement
        assert report.incremental.backfill_to_structure_disp_ratio > 100.0
        # Notes reflect backfill dominance
        assert any("backfill" in note.lower() for note in report.interpretation_notes)

    def test_evaluate_execution_participation(self):
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
            runtime_seconds=1.2,
            outcome=AnalysisOutcome.COMPLETED,
            initial_step=step0,
        )

        exec_report = evaluate_execution_participation(m, exec_res)
        assert exec_report.analysis_name == "LiveLoad_1"
        assert len(exec_report.steps) == 2
        assert "committed_step_count" in exec_report.summary
        assert exec_report.summary["committed_step_count"] == 2

        # Verify serialization
        as_dict = exec_report.to_dict()
        assert as_dict["analysis_key"] == 22
        assert len(as_dict["steps"]) == 2
