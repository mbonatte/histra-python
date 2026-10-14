"""Tests for Task 12: Configuration and Usability options for collapse mechanism screening."""
from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pytest

from histra.collapse import (
    CollapseCategory,
    CollapseConfig,
    CollapseScreeningReport,
    ComponentMappingConfig,
    ReviewPriority,
    resolve_component_mapping,
    screen_analysis_collapse,
)
from histra.io.hr_loader import load_model
from histra.solver.model_manager import ModelManager
from histra.solver.outcomes import AnalysisExecution, AnalysisOutcome, AnalysisStep


class TestCollapseConfigurationUsability:
    """Test configuration schema, serialization, and enable/disable controls."""

    def test_default_config_properties(self):
        """Default configuration enables screening with standard physical tolerances."""
        cfg = CollapseConfig()
        assert cfg.enabled
        assert cfg.relative_active_tolerance == 0.10
        assert cfg.min_absolute_displacement == 1.0e-4
        assert cfg.load_drop_trigger == 0.05
        assert cfg.significant_load_drop == 0.15
        assert cfg.compute_interface_kinematics
        assert not cfg.compute_energy_dissipation
        assert cfg.export_incremental_history

    def test_disabled_screening_bypasses_calculation(self):
        """Disabled configuration skips screening with zero overhead."""
        m = load_model("histra/model-live/model.hrx")
        ModelManager.prepare_model(m, force=True)

        u = np.zeros(m.gdl, dtype=float)
        steps = (AnalysisStep.from_mapping({"step": 1, "status": "OK", "u": u, "load_factor": 1.0, "displacement": -0.1}),)
        exec_res = AnalysisExecution(
            analysis_key=1,
            analysis_name="PushDown_Disabled",
            code=0,
            steps=steps,
            runtime_seconds=0.1,
            outcome=AnalysisOutcome.COMPLETED,
        )

        cfg = CollapseConfig.disabled()
        report = screen_analysis_collapse(m, exec_res, config=cfg)

        assert not report.is_screened
        assert report.status == "DISABLED"
        assert "disabled by user configuration" in report.primary_diagnosis.lower()

    def test_json_roundtrip_serialization(self, tmp_path: Path):
        """Configuration and reusable mapping serialize and deserialize to/from JSON."""
        mapping = ComponentMappingConfig(
            material_names={"arch": ("*masonry*", "*brick*"), "backfill": ("*soil*", "*fill*")},
            quad_keys={"pier": (10, 11, 12), "abutment": (20, 21)},
            layer_keys={"arch": (0,)},
            fallback_to_heuristics=False,
            strict=False,
        )
        cfg = CollapseConfig(
            enabled=True,
            relative_active_tolerance=0.08,
            min_absolute_displacement=5.0e-5,
            load_drop_trigger=0.08,
            significant_load_drop=0.20,
            compute_energy_dissipation=True,
            export_incremental_history=False,
            mapping=mapping,
        )

        json_file = tmp_path / "collapse_config.json"
        cfg.to_json(json_file)
        assert json_file.exists()

        loaded_cfg = CollapseConfig.from_json(json_file)
        assert loaded_cfg.enabled == cfg.enabled
        assert loaded_cfg.relative_active_tolerance == 0.08
        assert loaded_cfg.load_drop_trigger == 0.08
        assert loaded_cfg.compute_energy_dissipation
        assert not loaded_cfg.export_incremental_history
        assert loaded_cfg.mapping.material_names == mapping.material_names
        assert loaded_cfg.mapping.quad_keys == mapping.quad_keys
        assert loaded_cfg.mapping.layer_keys == mapping.layer_keys
        assert not loaded_cfg.mapping.fallback_to_heuristics


class TestComponentMappingAndDiagnostics:
    """Test custom component & material mapping and visibility into unmapped/ambiguous items."""

    def test_custom_material_key_and_name_mapping(self):
        """Map components using explicit material keys and wildcard patterns."""
        m = load_model("histra/model-live/model.hrx")
        ModelManager.prepare_model(m, force=True)

        mapping = ComponentMappingConfig(
            material_names={
                "backfill": ("*soil*", "*fill*"),
                "arch": ("*masonry*", "*pietra*"),
            },
            quad_keys={
                "abutment": (10, 11),
            },
        )

        cls = resolve_component_mapping(m, mapping)
        assert cls.has_backfill
        assert cls.has_arch
        assert 10 in cls.abutment_quad_keys
        assert 11 in cls.abutment_quad_keys
        # Abutments are structural masonry, included in total_structure
        assert 10 in cls.total_structure_quad_keys
        assert 11 in cls.total_structure_quad_keys

    def test_unmapped_elements_visibility_in_output(self):
        """Elements not covered by mapping are explicitly visible in unmapped list and warnings."""
        m = load_model("histra/model-live/model.hrx")
        ModelManager.prepare_model(m, force=True)

        # Mapping that intentionally only maps 2 quads and disables heuristic fallback
        mapping = ComponentMappingConfig(
            quad_keys={"arch": (1, 2)},
            fallback_to_heuristics=False,
            strict=False,
        )

        cls = resolve_component_mapping(m, mapping)
        assert cls.has_unmapped
        assert len(cls.unmapped_quad_keys) > 0
        assert 1 not in cls.unmapped_quad_keys
        assert 2 not in cls.unmapped_quad_keys
        assert cls.has_warnings
        assert any("could not be mapped" in w for w in cls.mapping_warnings)

    def test_ambiguous_mapping_detection_and_precedence(self):
        """Elements matching conflicting categories are recorded as ambiguous with warnings."""
        m = load_model("histra/model-live/model.hrx")
        ModelManager.prepare_model(m, force=True)

        # Quad 5 is assigned to both arch and pier
        mapping = ComponentMappingConfig(
            quad_keys={"arch": (5,), "pier": (5,)},
            fallback_to_heuristics=True,
        )

        cls = resolve_component_mapping(m, mapping)
        assert cls.has_ambiguous
        assert 5 in cls.ambiguous_quad_keys
        assert set(cls.ambiguous_quad_keys[5]) == {"arch", "pier"}
        assert any("conflicting categories" in w for w in cls.mapping_warnings)
        # Precedence picks arch over pier
        assert 5 in cls.arch_quad_keys
        assert 5 not in cls.pier_quad_keys

    def test_strict_mapping_raises_on_unmapped(self):
        """Strict mapping raises ValueError when elements are unmapped."""
        m = load_model("histra/model-live/model.hrx")
        ModelManager.prepare_model(m, force=True)

        mapping = ComponentMappingConfig(
            quad_keys={"arch": (1,)},
            fallback_to_heuristics=False,
            strict=True,
        )
        with pytest.raises(ValueError, match="Strict component mapping failed"):
            resolve_component_mapping(m, mapping)


class TestFullAutomatedScreeningAndSummary:
    """Test screen_analysis_collapse and tabular summary generation."""

    def test_screen_analysis_collapse_full_pipeline(self, tmp_path: Path):
        """Automated screening executes full pipeline, writes CSV, and generates summary row."""
        m = load_model("histra/model-live/model.hrx")
        ModelManager.prepare_model(m, force=True)

        u = np.zeros(m.gdl, dtype=float)
        steps = (
            AnalysisStep.from_mapping({"step": 1, "status": "OK", "u": u, "load_factor": 0.5, "displacement": -0.05}),
            AnalysisStep.from_mapping({"step": 2, "status": "OK", "u": u, "load_factor": 1.0, "displacement": -0.10}),
        )
        exec_res = AnalysisExecution(
            analysis_key=101,
            analysis_name="PushDown_PipelineTest",
            code=0,
            steps=steps,
            runtime_seconds=1.5,
            outcome=AnalysisOutcome.COMPLETED,
        )

        csv_out = tmp_path / "pipeline_evolution.csv"
        cfg = CollapseConfig(
            enabled=True,
            export_incremental_history=True,
            export_csv_path=str(csv_out),
        )

        report = screen_analysis_collapse(m, exec_res, config=cfg)

        assert report.is_screened
        assert report.status == "COMPLETED"
        assert report.category == CollapseCategory.NO_SIGNIFICANT_FAILURE_EVENT
        assert report.peak_resistance == 1.0
        assert report.evolution_history is not None
        assert csv_out.exists()

        # Tabular summary row suitable for batch simulation DataFrame
        row = report.summary_row
        assert row["analysis_key"] == 101
        assert row["analysis_name"] == "PushDown_PipelineTest"
        assert row["status"] == "COMPLETED"
        assert row["category"] == "NO_SIGNIFICANT_FAILURE_EVENT"
        assert row["peak_resistance"] == 1.0
        assert "warnings_count" in row
        assert "diagnosis" in row

        # Serializes cleanly to dictionary
        r_dict = report.to_dict()
        assert r_dict["analysis_key"] == 101
        assert r_dict["mapping_diagnostics"]["total_quads"] > 0
