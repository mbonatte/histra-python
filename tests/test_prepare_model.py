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


def test_regenerated_quad_diagonal_envelopes_match_csharp_locked_model():
    """Catches the C# cosAlfa and SetNonLinearProperties sign conventions."""
    reference = load_model(LOCKED_HRX)
    generated = load_model(LOCKED_HRX)
    prepare_model(generated, force=True)

    np.testing.assert_allclose(
        [quad.spring.cohesion for quad in generated.collections.quads.values()],
        [quad.spring.cohesion for quad in reference.collections.quads.values()],
        rtol=5.0e-7,
        atol=1.0e-5,
    )
    np.testing.assert_allclose(
        [quad.spring.mu for quad in generated.collections.quads.values()],
        [quad.spring.mu for quad in reference.collections.quads.values()],
        rtol=5.0e-7,
        atol=5.0e-7,
    )


def test_distorted_quad_uses_csharp_diagonal_signs_and_yield_search():
    """Representative C# values from Quad key 21 in the 560-DOF benchmark."""
    from histra.elements.quad import Quad

    quad = Quad(
        length=[21.4999847412109, 87.0741653442383, 21.5000019073486, 76.2800369262695],
        sin=[0.951635564897295, 0.953827636154029, 0.979428628995489, 0.980859329226481],
        cos=[-0.307229151648418, 0.300354524701755, 0.201790883599871, -0.194717683504551],
        diago=[83.1839904785156, 85.3733978271484],
        thickness=[288.0, 288.0, 288.0, 288.0],
    )

    assert quad.cos_alfa == pytest.approx(-0.05593786469959976, abs=1.0e-14)
    fy_t, fy_c = quad.set_non_linear_properties(
        1024446.6401416943,
        1620.0,
        782.2222222222222,
        0.029,
        2.68,
    )
    assert fy_t == pytest.approx(212.998674604, rel=1.0e-7)
    assert fy_c == pytest.approx(-197.709832167, rel=1.0e-7)


def test_coulomb_combination_uses_actual_hardening_modulus_not_serialized_default():
    """C# CombinationSpring(SpringCoulomb03) combines ``sp.H`` values.

    ``SetQuadSlidSpring`` does not copy the material's plastic-stiffness ratio
    into the spring's serialized ``PlasticStiffnessRatio`` property, so that
    property remains at its class default 1e-4.  For a material ratio of zero,
    using the property invents a softening branch and changes the committed
    in-plane sliding phase under gravity.
    """
    from histra.preprocessing.prepare_model import (
        _CoulombLaw,
        _combine_coulomb,
        _configure_coulomb,
    )

    law = _CoulombLaw(
        E=1000.0,
        cohesion=0.1,
        mu=1.2,
        plastic_stiffness_ratio=0.0,
        max_tensile_ratio=0.8,
    )
    side1 = _configure_coulomb(k=9000.0, area=10.0, length=1.0, law=law)
    side2 = _configure_coulomb(k=12000.0, area=10.0, length=1.0, law=law)

    # This is the observable C# quirk: the property remains at its default,
    # while the actual envelope hardening modulus is zero.
    assert side1.plastic_stiffness_ratio == pytest.approx(1.0e-4)
    assert side1.h == pytest.approx(0.0)
    assert side2.h == pytest.approx(0.0)

    combined = _combine_coulomb(side1, side2, restrained=False)

    assert combined.h == pytest.approx(0.0)
    assert combined.e2p == pytest.approx(0.0)
    assert combined.mom2p == pytest.approx(combined.mom1p)
