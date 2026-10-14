"""Tests for Feature 6: Mechanism Evolution Tracking across nonlinear push-down increments."""
from __future__ import annotations

import csv
import math
from pathlib import Path
import numpy as np
import pytest

from histra.collapse import (
    ClassifierThresholds,
    CollapseCategory,
    EvolutionStepRecord,
    MechanismEvolutionHistory,
    MechanismEvolutionTracker,
    MechanismTransition,
    ReviewPriority,
    classify_bridge_components,
    track_mechanism_evolution,
)
from histra.io.hr_loader import load_model
from histra.solver.model_manager import ModelManager
from histra.solver.outcomes import AnalysisExecution, AnalysisOutcome, AnalysisStep


class TestMechanismEvolutionTracker:
    """Test streaming incremental tracking and step record completeness."""

    def test_step_record_fields_completeness(self):
        """Every step record exports all specified physical and kinematic quantities."""
        m = load_model("histra/model-live/model.hrx")
        ModelManager.prepare_model(m, force=True)
        cls = classify_bridge_components(m)

        tracker = MechanismEvolutionTracker(
            m,
            analysis_key=10,
            analysis_name="PushDown_Test",
            classification=cls,
        )

        u = np.zeros(m.gdl, dtype=float)
        rec = tracker.process_step(
            step_number=1,
            u=u,
            load_factor=0.5,
            displacement=-0.1,
            reaction_z=50.0,
            status="OK",
        )

        assert isinstance(rec, EvolutionStepRecord)
        assert rec.step == 1
        assert rec.status == "OK"
        assert rec.load_factor == 0.5
        assert rec.applied_force == 50.0
        assert rec.control_displacement == -0.1
        assert rec.is_peak
        assert rec.running_peak_resistance == 0.5

        # All specified metrics must be accessible
        assert hasattr(rec, "k_total_structure")
        assert hasattr(rec, "k_backfill")
        assert hasattr(rec, "k_arch")
        assert hasattr(rec, "k_piers")
        assert hasattr(rec, "m_active_structure")
        assert hasattr(rec, "m_active_backfill")
        assert hasattr(rec, "m_active_arch")
        assert hasattr(rec, "m_active_piers")
        assert hasattr(rec, "max_arch_opening")
        assert hasattr(rec, "max_arch_rotation")
        assert hasattr(rec, "arch_hinge_count")
        assert hasattr(rec, "backfill_sliding_area_fraction")
        assert hasattr(rec, "d_backfill")
        assert hasattr(rec, "d_masonry")
        assert hasattr(rec, "is_in_load_drop")
        assert hasattr(rec, "classification")

        # Serializes cleanly to dictionary
        d = rec.to_dict()
        assert d["step"] == 1
        assert d["classification"] == rec.classification.value

        # Flattened row dictionary for DataFrame / CSV
        flat = rec.to_flat_dict()
        assert "step" in flat
        assert "classification" in flat


class TestLocalToGlobalEvolution:
    """Test detection of mechanism transitions from local backfill failure to structural collapse."""

    def test_local_backfill_to_arch_mechanism_transition(self):
        """Track multi-step progression: No failure -> Local backfill -> Mixed -> Arch collapse."""
        m = load_model("histra/model-live/model.hrx")
        ModelManager.prepare_model(m, force=True)
        cls = classify_bridge_components(m)

        tracker = MechanismEvolutionTracker(
            m,
            analysis_key=20,
            analysis_name="PushDown_Transition",
            classification=cls,
        )

        # Step 1: Initial elastic compaction
        u1 = np.zeros(m.gdl, dtype=float)
        r1 = tracker.process_step(
            step_number=1, u=u1, load_factor=0.3, displacement=-0.05, reaction_z=30.0
        )
        assert r1.classification == CollapseCategory.NO_SIGNIFICANT_FAILURE_EVENT

        # Step 2: Local backfill punch-through begins
        u2 = np.zeros(m.gdl, dtype=float)
        for qk in [1, 2]:
            q = m.collections.quads[qk]
            for entry in q.aff[2]:
                u2[entry.gdl - 1] = -1.5
        r2 = tracker.process_step(
            step_number=2, u=u2, load_factor=0.8, displacement=-1.5, reaction_z=80.0
        )
        assert r2.classification == CollapseCategory.LOCAL_BACKFILL_FAILURE

        # Step 3: Progressive spread - backfill displacement deepens and arch rotation initiates (1 hinge)
        u3 = np.array(u2, copy=True)
        for qk in [1, 2]:
            q = m.collections.quads[qk]
            for entry in q.aff[2]:
                u3[entry.gdl - 1] = -2.5
        # One hinge in arch: Quad 7 (GDL 47) / Quad 8 (GDL 54)
        u3[46] = 0.02
        u3[53] = -0.02
        r3 = tracker.process_step(
            step_number=3, u=u3, load_factor=1.2, displacement=-2.5, reaction_z=120.0
        )
        assert r3.classification == CollapseCategory.MIXED_OR_PROGRESSIVE_FAILURE

        # Step 4: Complete 4-hinge arch mechanism forms, load drops
        u4 = np.array(u3, copy=True)
        # Second hinge: Quad 16 (GDL 110) / Quad 17 (GDL 117)
        u4[109] = 0.025
        u4[116] = -0.025
        r4 = tracker.process_step(
            step_number=4, u=u4, load_factor=0.7, displacement=-3.5, reaction_z=70.0
        )
        assert r4.is_global or r4.is_single_span

        history = tracker.finalize()
        assert isinstance(history, MechanismEvolutionHistory)
        assert history.step_count == 4
        assert history.has_local_to_global_transition
        assert history.local_to_global_transition is not None

        # Verify transition was recorded
        trans = history.local_to_global_transition
        assert trans.from_category == CollapseCategory.LOCAL_BACKFILL_FAILURE
        assert trans.to_category == CollapseCategory.MIXED_OR_PROGRESSIVE_FAILURE
        assert trans.to_step == 3
        assert trans.is_local_to_global

        # Verify narrative contains clear tracking information
        narrative = history.evolution_narrative
        assert "LOCAL-TO-GLOBAL TRANSITION" in narrative
        assert "Step 3" in narrative
        assert "LOCAL_BACKFILL_FAILURE -> MIXED_OR_PROGRESSIVE_FAILURE" in narrative

    def test_purely_local_backfill_without_global_transition(self):
        """Backfill punch-through deepens without activating arch hinges -> No global transition."""
        m = load_model("histra/model-live/model.hrx")
        ModelManager.prepare_model(m, force=True)
        cls = classify_bridge_components(m)

        tracker = MechanismEvolutionTracker(
            m,
            analysis_key=21,
            analysis_name="PushDown_PureLocal",
            classification=cls,
        )

        u1 = np.zeros(m.gdl, dtype=float)
        tracker.process_step(step_number=1, u=u1, load_factor=0.4, displacement=-0.1)

        # Punch through deepens
        for step, disp in [(2, -1.0), (3, -2.5), (4, -4.0)]:
            u = np.zeros(m.gdl, dtype=float)
            for qk in [1, 2]:
                q = m.collections.quads[qk]
                for entry in q.aff[2]:
                    u[entry.gdl - 1] = disp
            tracker.process_step(step_number=step, u=u, load_factor=0.9, displacement=disp)

        history = tracker.finalize()
        assert not history.has_local_to_global_transition
        assert history.local_to_global_transition is None
        assert history.dominant_mechanism == CollapseCategory.LOCAL_BACKFILL_FAILURE
        assert "No local-to-global transition occurred" in history.evolution_narrative


class TestLoadDropAndExport:
    """Test load drop correlation along the path and CSV/tabular export."""

    def test_load_drop_tracking_along_path(self):
        """Tracker detects on-the-fly load drops as capacity drops from running peak."""
        m = load_model("histra/model-live/model.hrx")
        ModelManager.prepare_model(m, force=True)

        tracker = MechanismEvolutionTracker(m, analysis_key=30, analysis_name="PushDown_Drop")

        u = np.zeros(m.gdl, dtype=float)
        s1 = tracker.process_step(step_number=1, u=u, load_factor=0.5, displacement=-0.1)
        s2 = tracker.process_step(step_number=2, u=u, load_factor=1.0, displacement=-0.2)
        s3 = tracker.process_step(step_number=3, u=u, load_factor=1.5, displacement=-0.3)  # Peak = 1.5

        assert not s1.is_in_load_drop
        assert not s2.is_in_load_drop
        assert not s3.is_in_load_drop
        assert s3.is_peak

        # Capacity drops to 1.0 (33% drop from 1.5)
        s4 = tracker.process_step(step_number=4, u=u, load_factor=1.0, displacement=-0.4)
        assert s4.is_in_load_drop
        assert math.isclose(s4.relative_drop_ratio, 0.3333, rel_tol=1e-2)
        assert s4.is_sharp_drop

    def test_export_csv_and_records(self, tmp_path: Path):
        """History exports cleanly to records and CSV file."""
        m = load_model("histra/model-live/model.hrx")
        ModelManager.prepare_model(m, force=True)

        u = np.zeros(m.gdl, dtype=float)
        steps = (
            AnalysisStep.from_mapping({"step": 1, "status": "OK", "u": u, "load_factor": 0.5, "displacement": -0.1}),
            AnalysisStep.from_mapping({"step": 2, "status": "OK", "u": u, "load_factor": 1.0, "displacement": -0.2}),
        )
        exec_res = AnalysisExecution(
            analysis_key=35,
            analysis_name="PushDown_Export",
            code=0,
            steps=steps,
            runtime_seconds=1.0,
            outcome=AnalysisOutcome.COMPLETED,
        )

        history = track_mechanism_evolution(m, exec_res)
        assert history.step_count == 2

        # 1. to_records
        records = history.to_records()
        assert len(records) == 2
        assert "k_total_structure" in records[0]
        assert "classification" in records[0]

        # 2. to_csv_string
        csv_str = history.to_csv_string()
        assert "k_total_structure" in csv_str
        assert "classification" in csv_str

        # 3. export_csv to file
        csv_path = tmp_path / "evolution_test.csv"
        history.export_csv(csv_path)
        assert csv_path.exists()

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
            assert rows[0]["step"] == "1"
            assert rows[1]["step"] == "2"

        # 4. to_dict
        h_dict = history.to_dict()
        assert h_dict["analysis_key"] == 35
        assert len(h_dict["steps"]) == 2
