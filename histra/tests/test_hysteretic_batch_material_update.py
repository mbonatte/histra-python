from __future__ import annotations

from copy import deepcopy
from types import SimpleNamespace

import numpy as np
import pytest

import histra.solver.hysteretic_batch as batch
from histra.elements.interface import Interface
from histra.springs.coulomb03 import SpringCoulomb03
from histra.springs.hysteretic import SpringHysteretic
from histra.types.afference_entry import AfferenceEntry
from histra.types.phase_enum import PhaseEnum
from histra.types.point import Point


def _hysteretic(seed: int, stiffness: float) -> SpringHysteretic:
    spring = SpringHysteretic(
        key=seed,
        k=stiffness,
        k_tang=0.75 * stiffness,
        e1p=stiffness,
        e1n=stiffness,
        e2p=0.1 * stiffness,
        e2n=0.1 * stiffness,
        betap=1.0,
        betan=0.0,
        tensile_curve_type="LinearSoftening",
        compressive_curve_type="LinearSoftening",
    )
    spring.revert_to_start()
    spring.umax[:] = [1.0e-4 * seed, -2.0e-4 * seed]
    spring._crot_pu = 3.0e-5 * seed
    spring._crot_nu = -4.0e-5 * seed
    spring.cenergy_d = 5.0e-3 * seed
    spring._cload_indicator = seed % 3
    spring._cstress = 0.25 * seed
    spring._cstrain = 2.0e-5 * seed
    spring.phase = PhaseEnum.Elastic
    spring.k_tang_committed = 0.75 * stiffness
    spring.revert_to_last_commit()
    spring.k_tang = spring.k_tang_committed
    spring.f = spring._cstress
    spring.u = spring._cstrain
    return spring


def _coulomb(seed: int, stiffness: float) -> SpringCoulomb03:
    spring = SpringCoulomb03(
        key=seed,
        k=stiffness,
        k_tang=0.8 * stiffness,
        e1p=stiffness,
        e1n=stiffness,
        e2p=0.05 * stiffness,
        e2n=0.05 * stiffness,
        hysteretic_type="Initial",
        sub_law="Coulomb",
        area=1.0 + 0.1 * seed,
        mu=0.35,
        cohesion=0.75,
    )
    spring.revert_to_start()
    spring.fy[:] = [1.2 + seed, -(1.2 + seed)]
    spring._cup = 1.0e-5 * seed
    spring._cstress = 0.4 * seed
    spring._cstrain = 3.0e-5 * seed
    spring._cstress_normal = -2.0 * seed
    spring._cstress_normal_prev = -1.5 * seed
    spring._ccontact_area = spring.area
    spring.cenergy_d = 2.0e-3 * seed
    spring.phase = PhaseEnum.Elastic
    spring.k_tang_committed = 0.8 * stiffness
    spring.revert_to_last_commit()
    spring.k_tang = spring.k_tang_committed
    spring.f = spring._cstress
    spring.u = spring._cstrain
    return spring


def _interface(key: int, gdl_offset: int) -> Interface:
    interface = Interface(
        key=key,
        length=2.0,
        thickness=[1.0, 1.0],
        nrow=2,
        ncol=2,
        nspring=4,
    )
    interface.vint2d = [
        Point(0.0, 0.0, 0.0),
        Point(2.0, 0.0, 0.0),
        Point(2.0, 1.0, 0.0),
        Point(0.0, 1.0, 0.0),
    ]
    interface.trasv_1 = [
        _hysteretic(100 * key + index + 1, 10.0 + key + index)
        for index in range(4)
    ]
    interface.slid = [_coulomb(1000 * key + 1, 20.0 + key)]
    interface.slid_out_plan = [
        _coulomb(1000 * key + 2, 30.0 + key),
        _coulomb(1000 * key + 3, 40.0 + key),
    ]
    for local_dof in range(12):
        interface.aff[local_dof] = [
            AfferenceEntry(gdl=gdl_offset + local_dof + 1, alfa=1.0)
        ]
    interface.status.u[:] = [1.0e-6 * (key + index) for index in range(12)]
    interface.status.normal_increment = 0.5 * key
    interface.status.committed_normal_force = -0.25 * key
    interface.status.max_spring_displacement = 1.0e-4 * key
    return interface


def _model() -> SimpleNamespace:
    first = _interface(1, 0)
    second = _interface(2, 12)
    return SimpleNamespace(
        gdl=24,
        collections=SimpleNamespace(
            interfaces={1: first, 2: second},
            quads={},
            materials={},
        ),
    )


def _replace_definition(interface: Interface, factor: float) -> None:
    transverse: list[SpringHysteretic] = []
    for old in interface.trasv_1:
        spring = deepcopy(old)
        spring.k *= factor
        spring.e1p *= factor
        spring.e1n *= factor
        spring.e2p *= factor
        spring.e2n *= factor
        transverse.append(spring)
    interface.trasv_1 = transverse

    slid: list[SpringCoulomb03] = []
    for old in interface.slid:
        spring = deepcopy(old)
        spring.k *= factor
        spring.e1p *= factor
        spring.e1n *= factor
        spring.e2p *= factor
        spring.e2n *= factor
        spring.cohesion *= 0.5
        slid.append(spring)
    interface.slid = slid

    out: list[SpringCoulomb03] = []
    for old in interface.slid_out_plan:
        spring = deepcopy(old)
        spring.k *= factor
        spring.e1p *= factor
        spring.e1n *= factor
        spring.e2p *= factor
        spring.e2n *= factor
        spring.mu *= 0.8
        out.append(spring)
    interface.slid_out_plan = out


@pytest.mark.skipif(batch.njit is None, reason="Numba is unavailable")
def test_incremental_material_update_matches_fresh_full_runtime_exactly() -> None:
    incremental_model = _model()
    full_model = deepcopy(incremental_model)
    incremental = batch.HystereticBatchRuntime(incremental_model)

    persistent_arrays = {
        name: id(getattr(incremental, name))
        for name in (
            "params", "committed", "trial", "targets", "enabled",
            "coulomb_params", "coulomb_state", "coulomb_targets",
            "_di", "_dj", "_ecc", "_aff_offsets", "_aff_gdls",
            "_aff_coefficients", "_local_u", "_local_full_forces",
        )
    }
    unaffected_before = incremental.params[4:8].copy()
    unaffected_objects = tuple(incremental.springs[4:8])

    _replace_definition(incremental_model.collections.interfaces[1], 1.7)
    _replace_definition(full_model.collections.interfaces[1], 1.7)

    assert incremental.try_update_material_interfaces(
        [incremental_model.collections.interfaces[1]]
    ) is True
    rebuilt = batch.HystereticBatchRuntime(full_model)

    for name in (
        "params", "committed", "trial", "targets", "enabled",
        "_transverse_k", "coulomb_params", "coulomb_state",
        "coulomb_targets", "coulomb_dns", "coulomb_enabled",
        "_di", "_dj", "_ecc", "_record_index", "_starts", "_stops",
        "_dist", "_dist_for", "_aff_offsets", "_aff_gdls",
        "_aff_coefficients", "_local_u", "_local_full_forces",
        "_global_resisting_force", "_max_u_cache",
    ):
        np.testing.assert_array_equal(getattr(incremental, name), getattr(rebuilt, name))

    assert incremental._simple_hysteretic == rebuilt._simple_hysteretic
    assert tuple(incremental.springs[4:8]) == unaffected_objects
    np.testing.assert_array_equal(incremental.params[4:8], unaffected_before)
    for name, object_id in persistent_arrays.items():
        assert id(getattr(incremental, name)) == object_id


@pytest.mark.skipif(batch.njit is None, reason="Numba is unavailable")
def test_incremental_material_update_rejects_changed_transverse_layout_without_mutation() -> None:
    model = _model()
    runtime = batch.HystereticBatchRuntime(model)
    params_before = runtime.params.copy()
    springs_before = tuple(runtime.springs)

    interface = model.collections.interfaces[1]
    interface.trasv_1 = interface.trasv_1[:-1]

    assert runtime.try_update_material_interfaces([interface]) is False
    np.testing.assert_array_equal(runtime.params, params_before)
    assert tuple(runtime.springs) == springs_before


@pytest.mark.skipif(batch.njit is None, reason="Numba is unavailable")
def test_incremental_material_update_rejects_incompatible_coulomb_layout_without_mutation() -> None:
    model = _model()
    runtime = batch.HystereticBatchRuntime(model)
    state_before = runtime.coulomb_state.copy()
    springs_before = tuple(runtime.coulomb_springs)

    interface = model.collections.interfaces[1]
    replacement = deepcopy(interface.slid[0])
    replacement.hysteretic_type = "Takeda"
    interface.slid = [replacement]

    assert runtime.try_update_material_interfaces([interface]) is False
    np.testing.assert_array_equal(runtime.coulomb_state, state_before)
    assert tuple(runtime.coulomb_springs) == springs_before


@pytest.mark.skipif(batch.njit is None, reason="Numba is unavailable")
def test_incremental_material_update_rejects_unsynchronized_object_state() -> None:
    model = _model()
    runtime = batch.HystereticBatchRuntime(model)
    params_before = runtime.params.copy()
    _replace_definition(model.collections.interfaces[1], 1.5)
    runtime._objects_trial_synced = False

    assert runtime.try_update_material_interfaces([model.collections.interfaces[1]]) is False
    np.testing.assert_array_equal(runtime.params, params_before)

@pytest.mark.skipif(batch.njit is None, reason="Numba is unavailable")
def test_repeated_incremental_material_updates_match_repeated_full_rebuilds() -> None:
    incremental_model = _model()
    full_model = deepcopy(incremental_model)
    incremental = batch.HystereticBatchRuntime(incremental_model)
    params_id = id(incremental.params)
    committed_id = id(incremental.committed)

    for key, factor in ((1, 1.2), (1, 0.85), (2, 1.4), (1, 1.1)):
        _replace_definition(incremental_model.collections.interfaces[key], factor)
        _replace_definition(full_model.collections.interfaces[key], factor)

        assert incremental.try_update_material_interfaces(
            [incremental_model.collections.interfaces[key]]
        ) is True
        rebuilt = batch.HystereticBatchRuntime(full_model)

        for name in (
            "params", "committed", "trial", "targets", "enabled",
            "_transverse_k", "coulomb_params", "coulomb_state",
            "coulomb_targets", "coulomb_dns", "coulomb_enabled",
            "_local_u", "_local_full_forces", "_global_resisting_force",
        ):
            np.testing.assert_array_equal(
                getattr(incremental, name), getattr(rebuilt, name)
            )
        assert id(incremental.params) == params_id
        assert id(incremental.committed) == committed_id


@pytest.mark.skipif(batch.njit is None, reason="Numba is unavailable")
def test_transverse_parameter_import_matches_scalar_attribute_reference_exactly() -> None:
    model = _model()
    runtime = batch.HystereticBatchRuntime(model)

    for index, spring in enumerate(runtime.springs):
        expected = np.asarray(
            [float(getattr(spring, name)) for name in batch._PARAM_NAMES],
            dtype=np.float64,
        )
        np.testing.assert_array_equal(
            runtime.params[index, : len(batch._PARAM_NAMES)], expected
        )
