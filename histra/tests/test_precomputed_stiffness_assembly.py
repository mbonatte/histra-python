from __future__ import annotations

from types import SimpleNamespace

import numpy as np

from histra.solver.assembler import assemble_global_k


def _entry(gdl: int, alfa: float = 1.0) -> SimpleNamespace:
    return SimpleNamespace(gdl=gdl, alfa=alfa)


def test_assemble_global_k_reuses_precomputed_element_stiffness() -> None:
    def must_not_recompute(_alfa: float) -> None:
        raise AssertionError("element stiffness was recomputed during assembly")

    quad = SimpleNamespace(
        status=SimpleNamespace(k=4.0),
        aff=[[], [], [], [], [], [], [_entry(1), _entry(2, 0.5)]],
        compute_k=must_not_recompute,
    )
    interface = SimpleNamespace(
        dim_aff=[1, 2, 0],
        status=SimpleNamespace(
            k=[[10.0]],
            kslid=[[3.0, -3.0], [-3.0, 3.0]],
            kslid_out_plan=[],
        ),
        aff=[[_entry(1)], [_entry(2)], [_entry(3)]],
        slid=[object()],
        slid_out_plan=[],
    )
    model = SimpleNamespace(
        gdl=3,
        collections=SimpleNamespace(
            quads={1: quad},
            interfaces={1: interface},
        ),
    )

    matrix = assemble_global_k(
        model, alfa=0.0, recompute_elements=False
    ).toarray()

    expected = np.array(
        [
            [14.0, 2.0, 0.0],
            [2.0, 4.0, -3.0],
            [0.0, -3.0, 3.0],
        ]
    )
    np.testing.assert_array_equal(matrix, expected)
