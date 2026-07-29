from __future__ import annotations

from types import SimpleNamespace

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
