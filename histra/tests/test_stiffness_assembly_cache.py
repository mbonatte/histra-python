from __future__ import annotations

from types import SimpleNamespace

import numpy as np

from histra.elements.interface import Interface
from histra.solver.assembler import (
    _assemble_global_k_legacy,
    assemble_global_k,
)
from histra.springs.base import Spring
from histra.types.afference_entry import AfferenceEntry


def _interface(key: int, *, gdl_count: int = 32) -> Interface:
    interface = Interface(key=key, dim_aff=[6, 2, 4], dim_aff_tot=12)
    interface.trasv_1 = [Spring(k=1.0)]
    interface.slid = [Spring(k=1.0)]
    interface.slid_out_plan = [Spring(k=1.0), Spring(k=1.0)]
    interface.status.k = [
        [0.2 + (row * 6 + col) * 0.001 for col in range(6)]
        for row in range(6)
    ]
    interface.status.kslid = [[1.1, -1.1], [-1.1, 1.1]]
    interface.status.kslid_out_plan = [
        [0.3 + (row * 4 + col) * 0.002 for col in range(4)]
        for row in range(4)
    ]
    interface.aff = []
    for local_dof in range(12):
        base = (key * 7 + local_dof * 3) % gdl_count
        interface.aff.append(
            [
                AfferenceEntry(gdl=base + 1, alfa=1.0),
                AfferenceEntry(gdl=((base + 5) % gdl_count) + 1, alfa=-0.125),
                AfferenceEntry(gdl=((base + 11) % gdl_count) + 1, alfa=0.03125),
            ]
        )
    return interface


def _model(count: int = 4) -> SimpleNamespace:
    interfaces = {key: _interface(key) for key in range(1, count + 1)}
    return SimpleNamespace(
        gdl=32,
        collections=SimpleNamespace(quads={}, interfaces=interfaces),
    )


def _assert_csc_bitwise_equal(actual, expected) -> None:
    np.testing.assert_array_equal(actual.indptr, expected.indptr)
    np.testing.assert_array_equal(actual.indices, expected.indices)
    np.testing.assert_array_equal(actual.data, expected.data)


def test_cached_stiffness_scatter_is_bitwise_equal_to_legacy() -> None:
    model = _model()
    expected = _assemble_global_k_legacy(model, recompute_elements=False)
    actual = assemble_global_k(model, recompute_elements=False)
    _assert_csc_bitwise_equal(actual, expected)


def test_cached_stiffness_scatter_reuses_topology_for_new_local_values() -> None:
    model = _model()
    assemble_global_k(model, recompute_elements=False)
    first_plan = model._perf_stiffness_assembly_plan

    target = model.collections.interfaces[2]
    target.status.k[2][3] = -7.125
    target.status.kslid[0][1] = 0.0
    target.status.kslid_out_plan[3][1] = 2.375

    expected = _assemble_global_k_legacy(model, recompute_elements=False)
    actual = assemble_global_k(model, recompute_elements=False)

    assert model._perf_stiffness_assembly_plan is first_plan
    _assert_csc_bitwise_equal(actual, expected)


def test_material_like_spring_replacement_keeps_scatter_plan() -> None:
    model = _model()
    assemble_global_k(model, recompute_elements=False)
    first_plan = model._perf_stiffness_assembly_plan

    target = model.collections.interfaces[3]
    target.trasv_1 = [Spring(k=9.0)]
    target.slid = [Spring(k=8.0)]
    target.slid_out_plan = [Spring(k=7.0), Spring(k=6.0)]

    actual = assemble_global_k(model, recompute_elements=False)
    expected = _assemble_global_k_legacy(model, recompute_elements=False)

    assert model._perf_stiffness_assembly_plan is first_plan
    _assert_csc_bitwise_equal(actual, expected)


def test_afference_replacement_invalidates_and_rebuilds_scatter_plan() -> None:
    model = _model()
    assemble_global_k(model, recompute_elements=False)
    first_plan = model._perf_stiffness_assembly_plan

    target = model.collections.interfaces[1]
    target.aff[0] = [
        AfferenceEntry(gdl=1, alfa=0.75),
        AfferenceEntry(gdl=9, alfa=-0.25),
    ]

    actual = assemble_global_k(model, recompute_elements=False)
    expected = _assemble_global_k_legacy(model, recompute_elements=False)

    assert model._perf_stiffness_assembly_plan is not first_plan
    _assert_csc_bitwise_equal(actual, expected)


def test_threshold_semantics_match_legacy_exactly() -> None:
    model = _model(1)
    target = model.collections.interfaces[1]
    # Interface scatter rejects tiny k_ij before afference multiplication.
    target.status.k[0][0] = 5.0e-31
    # A nearby value survives the local-k threshold but is removed only after
    # multiplication, exercising both legacy checks.
    target.status.k[0][1] = 2.0e-30

    actual = assemble_global_k(model, recompute_elements=False)
    expected = _assemble_global_k_legacy(model, recompute_elements=False)
    _assert_csc_bitwise_equal(actual, expected)


def test_cached_plan_preserves_legacy_interface_emission_order() -> None:
    from histra.solver.assembler import _build_stiffness_assembly_plan

    model = _model(2)
    # Exercise the legacy invalid-DOF filtering inside interface scatter.
    model.collections.interfaces[1].aff[0].insert(
        1, AfferenceEntry(gdl=0, alfa=9.5)
    )
    plan = _build_stiffness_assembly_plan(model)

    expected_rows: list[int] = []
    expected_cols: list[int] = []
    expected_terms: list[int] = []
    expected_alpha_i: list[float] = []
    expected_alpha_j: list[float] = []
    term_index = 0

    for interface in model.collections.interfaces.values():
        d0, d1, d2 = interface.dim_aff
        blocks = [(0, d0)]
        if interface.slid:
            blocks.append((d0, d1))
        if len(interface.slid_out_plan) >= 2:
            blocks.append((d0 + d1, d2))

        for offset, size in blocks:
            for i in range(size):
                for j in range(size):
                    local_i = offset + i
                    local_j = offset + j
                    if local_i < len(interface.aff) and local_j < len(interface.aff):
                        for ei in interface.aff[local_i]:
                            gi = int(ei.gdl) - 1
                            if gi < 0 or gi >= model.gdl:
                                continue
                            for ej in interface.aff[local_j]:
                                gj = int(ej.gdl) - 1
                                if gj < 0 or gj >= model.gdl:
                                    continue
                                expected_rows.append(gi)
                                expected_cols.append(gj)
                                expected_terms.append(term_index)
                                expected_alpha_i.append(float(ei.alfa))
                                expected_alpha_j.append(float(ej.alfa))
                    term_index += 1

    np.testing.assert_array_equal(plan.rows, np.asarray(expected_rows, dtype=np.int32))
    np.testing.assert_array_equal(plan.cols, np.asarray(expected_cols, dtype=np.int32))
    np.testing.assert_array_equal(
        plan.term_indices, np.asarray(expected_terms, dtype=np.int32)
    )
    np.testing.assert_array_equal(
        plan.alpha_i, np.asarray(expected_alpha_i, dtype=np.float64)
    )
    np.testing.assert_array_equal(
        plan.alpha_j, np.asarray(expected_alpha_j, dtype=np.float64)
    )
