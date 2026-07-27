"""C# PrepareModel preprocessing regressions for the supported masonry topology."""
from __future__ import annotations

import copy
from pathlib import Path

import numpy as np
import pytest

from histra.io.hr_loader import load_model
from histra.preprocessing import prepare_model, inspect_solver_readiness
from histra.solver.assembler import assemble_global_k
from histra.solver.load_control import LoadControl
from histra.solver.model_manager import ModelManager
from histra.solver.solve import solve_static_nonlinear

ROOT = Path(__file__).resolve().parents[1]
LOCKED_HRX = ROOT / "model-output" / "model.hrx"


def _interface_signature(model):
    return [
        (
            intf.parent_type_element1,
            intf.parent_element_key1,
            intf.parent_type_element2,
            intf.parent_element_key2,
            intf.face1,
            intf.face2,
            intf.nrow,
            intf.ncol,
        )
        for intf in model.collections.interfaces.values()
    ]


def _reset_to_initial(model) -> None:
    ModelManager.clear_hysteretic_batch()
    for quad in model.collections.quads.values():
        quad.spring.revert_to_start()
        quad.spring.revert_to_last_commit()
    for intf in model.collections.interfaces.values():
        for spring in (*intf.trasv_1, *intf.slid, *intf.slid_out_plan):
            spring.revert_to_start()
            spring.revert_to_last_commit()
        intf.status.init_from_interface(intf)
    ModelManager.compute_k(model, 0.0)


def test_force_regeneration_matches_csharp_locked_topology_and_counts():
    reference = load_model(LOCKED_HRX)
    generated = load_model(LOCKED_HRX)
    reference_signature = _interface_signature(reference)

    report = prepare_model(generated, force=True)

    assert report.prepared
    assert report.gdl == 126
    assert report.quads == 18
    assert report.quad_springs == 18
    assert report.interfaces == 29
    assert report.quad_quad_interfaces == 27
    assert report.restraint_interfaces == 2
    assert report.transverse_springs == 2349
    assert report.sliding_springs == 29
    assert report.out_of_plane_springs == 58
    assert _interface_signature(generated) == reference_signature
    assert inspect_solver_readiness(generated).is_ready

    # C# AfferenceMatrix.SetFromCoefficients uses a 1e-4 cutoff.  Therefore the
    # generated row structure and global DOF sequence must match exactly.
    reference_entries = [
        (entry.gdl, entry.alfa)
        for intf in reference.collections.interfaces.values()
        for row in intf.aff
        for entry in row
    ]
    generated_entries = [
        (entry.gdl, entry.alfa)
        for intf in generated.collections.interfaces.values()
        for row in intf.aff
        for entry in row
    ]
    assert len(generated_entries) == len(reference_entries) == 880
    assert [item[0] for item in generated_entries] == [item[0] for item in reference_entries]
    np.testing.assert_allclose(
        [item[1] for item in generated_entries],
        [item[1] for item in reference_entries],
        rtol=2.0e-6,
        atol=1.5e-5,
    )


def test_regenerated_initial_stiffness_matches_csharp_preprocessed_model():
    reference = load_model(LOCKED_HRX)
    generated = load_model(LOCKED_HRX)
    prepare_model(generated, force=True)

    _reset_to_initial(reference)
    k_reference = assemble_global_k(reference, alfa=0.0).toarray()
    _reset_to_initial(generated)
    k_generated = assemble_global_k(generated, alfa=0.0).toarray()

    relative_error = np.linalg.norm(k_generated - k_reference) / np.linalg.norm(k_reference)
    assert relative_error <= 5.0e-6
    assert np.isfinite(k_generated).all()
    ModelManager.clear_hysteretic_batch()


def test_prepare_model_is_idempotent_and_model_manager_exposes_csharp_entrypoint():
    model = load_model(LOCKED_HRX)
    first = ModelManager.prepare_model(model, force=True)
    interfaces_before = tuple(model.collections.interfaces)
    springs_before = tuple(id(q.spring) for q in model.collections.quads.values())

    second = ModelManager.prepare_model(model)

    assert first.prepared
    assert not second.prepared
    assert tuple(model.collections.interfaces) == interfaces_before
    assert tuple(id(q.spring) for q in model.collections.quads.values()) == springs_before


def test_solver_auto_prepares_unlocked_geometry_model(monkeypatch):
    model = load_model(LOCKED_HRX)
    # Recreate the state of an unlocked geometry HRX without depending on a
    # machine-specific fixture path.
    model.is_locked = False
    model.gdl = 0
    model.collections.interfaces.clear()
    for quad in model.collections.quads.values():
        quad.aff = []
        quad.spring = None
        quad.interface_keys = [[] for _ in range(6)]

    original_commit = LoadControl.commit

    def stop_after_first(self, model_, analysis, displacement, dof, changed):
        original_commit(self, model_, analysis, displacement, dof, changed)
        return True

    monkeypatch.setattr(LoadControl, "commit", stop_after_first)
    messages: list[str] = []
    code, rows = solve_static_nonlinear(
        model,
        copy.deepcopy(model.collections.analyses[1]),
        1,
        on_log=messages.append,
    )

    assert code == 0
    assert len(rows) == 1
    assert rows[0]["status"] == "OK"
    assert inspect_solver_readiness(model).is_ready
    assert any("PrepareModel completed" in message for message in messages)
    ModelManager.clear_hysteretic_batch()
