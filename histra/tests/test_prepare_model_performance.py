from __future__ import annotations

from types import SimpleNamespace

import importlib
from pathlib import Path

import numpy as np
import pytest

from histra.preprocessing.prepare_model import (
    _HystereticLaw,
    _combine_hysteretic,
    _configure_combined_hysteretic,
    _configure_hysteretic,
    _find_or_create_geometric_node,
)
from histra.types.point import Point

from histra.io.hr_loader import load_model

pm = importlib.import_module("histra.preprocessing.prepare_model")
ROOT = Path(__file__).resolve().parents[1]
LOCKED_HRX = ROOT / "model-output" / "model.hrx"


def _law(tensile: str, compressive: str, *, scale: float) -> _HystereticLaw:
    return _HystereticLaw(
        E=12000.0 * scale,
        fy_t=0.25 * scale,
        fy_c=4.5 * scale,
        tensile_curve=tensile,
        compressive_curve=compressive,
        ratio_et_t=0.015,
        ratio_et_c=0.02,
        alfa_r_t=0.1,
        alfa_r_c=0.2,
        alfa_u_t=0.3,
        alfa_u_c=0.4,
        G_t=0.08 * scale,
        G_c=2.5 * scale,
        eps_u_t=0.004,
        eps_u_c=0.012,
        law_type="Flexural",
    )

def _afference_values(model):
    return [
        (entry.gdl, entry.alfa)
        for intf in model.collections.interfaces.values()
        for row in intf.aff
        for entry in row
    ]

@pytest.mark.parametrize(
    ("tensile", "compressive"),
    [
        ("LinearSoftening", "LinearSoftening"),
        ("Exponential", "Parabolic"),
        ("LinearHardening", "LinearHardening"),
        ("Elastic", "Elastic"),
    ],
)
def test_direct_combined_hysteretic_matches_legacy_path(tensile, compressive):
    law1 = _law(tensile, compressive, scale=1.0)
    law2 = _law(tensile, compressive, scale=1.3)
    legacy = _combine_hysteretic(
        _configure_hysteretic(1800.0, 2.5, 0.75, law1),
        _configure_hysteretic(2600.0, 3.0, 1.10, law2),
        False,
        law1,
        law2,
    )
    direct = _configure_combined_hysteretic(
        1800.0, 2.5, 0.75, law1,
        2600.0, 3.0, 1.10, law2,
    )

    scalar_fields = (
        "k", "area", "length", "energy_a", "betap", "betan",
        "rot1p", "mom1p", "rot2p", "mom2p", "rot3p", "mom3p",
        "rot1n", "mom1n", "rot2n", "mom2n", "rot3n", "mom3n",
        "e1p", "e2p", "e3p", "eup", "e1n", "e2n", "e3n", "eun",
        "k_tang", "k_tang_committed", "f", "u",
    )
    for name in scalar_fields:
        assert getattr(direct, name) == pytest.approx(getattr(legacy, name))
    for name in ("fy", "kt", "ur", "alfar", "alfau", "umax", "uy_corr"):
        np.testing.assert_allclose(getattr(direct, name), getattr(legacy, name), rtol=0.0, atol=0.0)
    assert direct.tensile_curve_type == legacy.tensile_curve_type
    assert direct.compressive_curve_type == legacy.compressive_curve_type
    assert direct.phase == legacy.phase
    assert direct.t_phase == legacy.t_phase


def test_geometric_node_spatial_index_preserves_tolerance_reuse():
    nodes = {
        1: SimpleNamespace(point=Point(0.0, 0.0, 0.0)),
        2: SimpleNamespace(point=Point(1.0, 2.0, 3.0)),
    }
    model = SimpleNamespace(collections=SimpleNamespace(nodes=nodes))

    assert _find_or_create_geometric_node(
        model, np.asarray((1.0 + 5.0e-5, 2.0, 3.0))
    ) == 2
    new_key = _find_or_create_geometric_node(
        model, np.asarray((4.0, 5.0, 6.0))
    )
    assert new_key == 3
    # The newly inserted node must be visible through the same spatial index.
    assert _find_or_create_geometric_node(
        model, np.asarray((4.0, 5.0 + 5.0e-5, 6.0))
    ) == new_key

def test_compiled_bilinear_preserves_scalar_evaluation_order():
    if pm.njit is None:
        return

    vertices = np.asarray(
        [
            [10.878649652149079, 632.2133485321168, 2287.9252612892487],
            [1193.974419132613, 1920.230899639857, 1577.1037912572513],
            [363.53635362901946, 1541.9522204102932, 683.404548834184],
            [677.6108838410398, 1097.1673186704572, -525.9304065189515],
        ],
        dtype=np.float64,
    )
    u = 0.6484831921948226
    v = -0.572474073249809
    expected = pm._bilinear(vertices, u, v)
    actual = np.empty(3, dtype=np.float64)

    pm._bilinear_nb(vertices, u, v, actual)

    np.testing.assert_array_equal(actual, expected)


def test_batched_interface_cells_match_scalar_reference_geometry():
    model = load_model(LOCKED_HRX)
    for intf in model.collections.interfaces.values():
        expected = np.asarray(
            [
                pm._cell_vertices(intf, index)
                for index in range(int(intf.nrow) * int(intf.ncol))
            ],
            dtype=np.float64,
        )
        actual = pm._interface_cells(intf)
        np.testing.assert_allclose(actual, expected, rtol=2.0e-14, atol=2.0e-14)
        np.testing.assert_allclose(
            pm._polygon_areas_3d(actual),
            [pm._polygon_area_3d(cell) for cell in expected],
            rtol=2.0e-14,
            atol=2.0e-14,
        )


def test_batched_quad_face_normals_match_scalar_reference_geometry():
    model = load_model(LOCKED_HRX)
    quads = list(model.collections.quads.values())
    faces = np.asarray(
        [np.asarray(pm._quad_vint(model, quad), dtype=float) for quad in quads],
        dtype=np.float64,
    )
    expected = np.asarray(
        [
            [pm._face_normal(faces[qindex, face]) for face in range(6)]
            for qindex in range(len(quads))
        ]
    )
    actual = pm._face_normals_batch(faces)
    np.testing.assert_allclose(actual, expected, rtol=2.0e-14, atol=2.0e-14)


def test_afference_reuses_each_quad_endpoint_warping_once(monkeypatch):
    model = load_model(LOCKED_HRX)
    reference = _afference_values(model)
    pm._assign_quad_afference(model)

    expected_warping_pairs: set[tuple[int, int]] = set()
    for intf in model.collections.interfaces.values():
        for parent_type, parent_key, face in (
            (
                intf.parent_type_element1,
                intf.parent_element_key1,
                intf.face1,
            ),
            (
                intf.parent_type_element2,
                intf.parent_element_key2,
                intf.face2,
            ),
        ):
            if parent_type == "Quad" and face <= 3:
                expected_warping_pairs.update(
                    (int(parent_key), int(node_key))
                    for node_key in intf.node_keys
                )

    calls: list[tuple[int, tuple[float, float, float]]] = []
    original = pm._warping_vector_from_geometry

    def counted(geometry, point):
        calls.append((id(geometry), tuple(float(value) for value in point)))
        return original(geometry, point)

    monkeypatch.setattr(pm, "_warping_vector_from_geometry", counted)
    pm._assign_interface_afference(model)

    assert len(calls) == len(expected_warping_pairs)
    generated = _afference_values(model)
    assert [item[0] for item in generated] == [item[0] for item in reference]
    np.testing.assert_allclose(
        [item[1] for item in generated],
        [item[1] for item in reference],
        rtol=2.0e-6,
        atol=1.5e-5,
    )


def test_interface_sliding_plane_distance_is_computed_once_per_quad_side(
    monkeypatch,
):
    model = load_model(LOCKED_HRX)
    intf = next(
        item
        for item in model.collections.interfaces.values()
        if item.parent_type_element1 == "Quad"
        and item.parent_type_element2 == "Quad"
    )
    expected_quad_sides = sum(
        parent_type == "Quad"
        for parent_type in (
            intf.parent_type_element1,
            intf.parent_type_element2,
        )
    )

    calls: list[int] = []
    original = pm._distance_to_interface_plane

    def counted(quad, interface):
        calls.append(int(quad.key))
        return original(quad, interface)

    monkeypatch.setattr(pm, "_distance_to_interface_plane", counted)
    pm._create_interface_springs(
        model,
        intf,
        flex_law_cache={},
        sliding_law_cache={},
    )

    assert len(calls) == expected_quad_sides
    assert len(intf.slid) == 1
    assert len(intf.slid_out_plan) == 2
    assert len(intf.trasv_1) == int(intf.nrow) * int(intf.ncol)


def test_interface_cell_batch_has_scalar_fallback(monkeypatch):
    model = load_model(LOCKED_HRX)
    intf = next(iter(model.collections.interfaces.values()))
    expected = pm._interface_cells(intf)
    monkeypatch.setattr(pm, "njit", None)
    if hasattr(intf, "_prep_vertices"):
        delattr(intf, "_prep_vertices")
    actual = pm._interface_cells(intf)
    np.testing.assert_allclose(actual, expected, rtol=2.0e-14, atol=2.0e-14)


def test_prepare_model_parses_each_material_law_once_per_orientation(
    monkeypatch,
):
    model = load_model(LOCKED_HRX)
    calls = {"flex": 0, "sliding": 0, "diagonal": 0, "shear": 0}

    original_flex = pm._flex_law
    original_sliding = pm._sliding_law
    original_diagonal = pm._diagonal_flex_law
    original_shear = pm._shear_law

    def counted_flex(*args, **kwargs):
        calls["flex"] = 1
        return original_flex(*args, **kwargs)

    def counted_sliding(*args, **kwargs):
        calls["sliding"] = 1
        return original_sliding(*args, **kwargs)

    def counted_diagonal(*args, **kwargs):
        calls["diagonal"] = 1
        return original_diagonal(*args, **kwargs)

    def counted_shear(*args, **kwargs):
        calls["shear"] = 1
        return original_shear(*args, **kwargs)

    monkeypatch.setattr(pm, "_flex_law", counted_flex)
    monkeypatch.setattr(pm, "_sliding_law", counted_sliding)
    monkeypatch.setattr(pm, "_diagonal_flex_law", counted_diagonal)
    monkeypatch.setattr(pm, "_shear_law", counted_shear)

    pm.prepare_model(model, force=True)

    quad_material_keys = {
        int(quad.material_key) for quad in model.collections.quads.values()
    }
    interface_material_keys = {
        int(intf.material_key)
        for intf in model.collections.interfaces.values()
        if int(intf.material_key) != 0
    }
    interface_material_keys.update(quad_material_keys)

    assert calls["diagonal"] <= len(quad_material_keys)
    assert calls["shear"] <= len(quad_material_keys)
    assert calls["flex"] <= 2 * len(interface_material_keys)
    assert calls["sliding"] <= 4 * len(interface_material_keys)
