from pathlib import Path
import tempfile
import warnings
import xml.etree.ElementTree as ET

import numpy as np
import pytest

import histra
from histra.postprocessing import compute_node_displacements
from histra.solver.model_manager import ModelManager

HRX_PATH = Path(__file__).resolve().parent.parent / "model-output" / "model.hrx"


@pytest.fixture(scope="module")
def vert_execution():
    model = histra.load_model(HRX_PATH)
    session = histra.AnalysisSession(model)
    execution = session.run("Vert")
    return model, session, execution


def test_results_export_two_tier_files(vert_execution):
    model, session, execution = vert_execution
    with tempfile.TemporaryDirectory() as td:
        created = session.export_analysis("Vert", td)
        assert "summary" in created
        assert "fields" in created

        summary_path = created["summary"]
        fields_path = created["fields"]
        assert summary_path.is_file()
        assert fields_path.is_file()

        # Size requirements: summary < 100 KB, fields < 20 MB
        summary_size = summary_path.stat().st_size
        fields_size = fields_path.stat().st_size
        assert summary_size <= 100 * 1024, f"Summary size {summary_size} exceeds 100 KB"
        assert fields_size <= 20 * 1024 * 1024, f"Fields size {fields_size} exceeds 20 MB"

        # Check SimulationResults can load from fields path or summary path
        sr = histra.SimulationResults.load(fields_path)
        assert sr.summary is not None
        assert "metadata" in sr.summary
        assert "metrics" in sr.summary
        assert sr.summary["metrics"]["completed"] is True
        assert sr.summary["metrics"]["total_steps"] > 0

        # Load from summary path
        sr_summary = histra.SimulationResults.load(summary_path)
        assert sr_summary.fields_path == fields_path


def test_results_export_round_trip_parity(vert_execution):
    model, session, execution = vert_execution
    last_u = execution.committed_steps[-1].u

    with tempfile.TemporaryDirectory() as td:
        created = session.export_analysis("Vert", td)
        sr = histra.SimulationResults.load(created["fields"])

        # 1. Displacement field parity
        disp_field = sr.get_displacement_field(step=-1)
        expected_rows = compute_node_displacements(model, last_u, only_quad_nodes=True)
        expected_arr = np.array(
            [[r.ux, r.uy, r.uz] for r in expected_rows], dtype=np.float32
        )
        l_inf_disp = np.max(np.abs(disp_field - expected_arr))
        assert l_inf_disp < 1.0e-6, f"Displacement L_inf mismatch: {l_inf_disp}"

        # 2. Interface resultants parity
        rt = ModelManager.hysteretic_batch_for(model)
        assert rt is not None
        expected_forces = rt.all_resultant_forces()
        actual_forces = sr.get_interface_resultants(step=-1)
        l_inf_forces = np.max(np.abs(actual_forces - expected_forces))
        assert l_inf_forces < 1.0e-6, f"Interface resultants L_inf mismatch: {l_inf_forces}"

        # 3. Filtered interface keys
        keys = list(sr.mesh_interface_keys)
        subset_keys = keys[:5]
        sub_forces = sr.get_interface_resultants(step=-1, interface_keys=subset_keys)
        assert sub_forces.shape == (5, 3)
        np.testing.assert_array_equal(sub_forces, actual_forces[:5])

        # 4. Pushover curve
        disp_curve, force_curve = sr.get_pushover_curve()
        assert len(disp_curve) == len(force_curve)
        assert len(disp_curve) == len(execution.output_steps)


def test_results_export_session_bundle(vert_execution):
    model, session, _ = vert_execution
    with tempfile.TemporaryDirectory() as td:
        bundle = session.export_session(td, "test_bundle")
        assert "Vert" in bundle
        assert bundle["Vert"]["summary"].is_file()
        assert bundle["Vert"]["fields"].is_file()


def test_results_export_tier_filtering(vert_execution):
    _, session, _ = vert_execution
    with tempfile.TemporaryDirectory() as td:
        # Tier summary only
        res_sum = session.export_analysis("Vert", td, base_name="sum_only", tier="summary")
        assert "summary" in res_sum
        assert "fields" not in res_sum
        assert res_sum["summary"].is_file()

        # Tier fields only
        res_fld = session.export_analysis("Vert", td, base_name="fld_only", tier="fields")
        assert "fields" in res_fld
        assert "summary" not in res_fld
        assert res_fld["fields"].is_file()


def test_results_export_h5_fallback_when_unavailable(vert_execution):
    _, session, _ = vert_execution
    with tempfile.TemporaryDirectory() as td:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            created = session.export_analysis("Vert", td, base_name="h5_test", format="h5")

        # Either created h5 or gracefully fell back to npz with warning
        fields_path = created["fields"]
        assert fields_path.is_file()
        if fields_path.suffix == ".npz":
            assert any("h5py is not installed" in str(w.message) for w in caught)


def test_simulation_results_to_vtk(vert_execution):
    _, session, _ = vert_execution
    with tempfile.TemporaryDirectory() as td:
        created = session.export_analysis("Vert", td)
        sr = histra.SimulationResults.load(created["fields"])

        vtu_path = Path(td) / "deformed_bridge.vtu"
        sr.to_vtk(vtu_path, step=-1)
        assert vtu_path.is_file()

        # Validate VTU is well-formed XML
        tree = ET.parse(vtu_path)
        root = tree.getroot()
        assert root.tag == "VTKFile"
        assert root.attrib.get("type") == "UnstructuredGrid"

        piece = root.find(".//Piece")
        assert piece is not None
        assert int(piece.attrib["NumberOfPoints"]) == len(sr.mesh_nodes_xyz)
        assert int(piece.attrib["NumberOfCells"]) == len(sr.mesh_quad_conn)


def test_step_resultant_hooks_numpy_arrays(vert_execution):
    _, _, execution = vert_execution
    # Verify every committed step has contiguous NumPy arrays without proxy objects
    for step in execution.committed_steps:
        forces = step.interface_resultants
        moments = step.interface_moments
        assert forces is not None
        assert moments is not None
        assert isinstance(forces, np.ndarray)
        assert isinstance(moments, np.ndarray)
        assert forces.dtype == np.float32
        assert moments.dtype == np.float32
