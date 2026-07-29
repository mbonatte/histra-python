from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import numpy as np
import pytest

import histra.solver.hysteretic_batch as batch
from histra.io.hr_loader import load_model
from histra.solver.hysteretic_batch import (
    _evaluate_linear_batch,
    build_hysteretic_batch,
)

MODEL = Path(__file__).resolve().parents[1] / "model-live" / "model.hrx"


@pytest.mark.skipif(_evaluate_linear_batch is None, reason="Numba is unavailable")
def test_compiled_hysteretic_batch_matches_scalar_state_machine(monkeypatch):
    monkeypatch.delenv("HISTRA_DISABLE_COMPILED_SPRINGS", raising=False)
    model = load_model(MODEL)
    runtime = build_hysteretic_batch(model)
    assert runtime is not None
    scalar = [deepcopy(spring) for spring in runtime.springs]

    rot_p = np.asarray([spring.rot1p for spring in scalar])
    rot_n = np.asarray([spring.rot1n for spring in scalar])
    history = (
        0.8 * rot_p,
        1.2 * rot_p,
        0.4 * rot_p,
        0.5 * rot_n,
        1.1 * rot_n,
        -0.2 * rot_n,
    )

    for targets in history:
        runtime.targets[:] = targets
        runtime.evaluate()
        for index, (spring, target) in enumerate(zip(scalar, targets)):
            spring.set_trial_strain(float(target))
            expected = np.asarray(
                [
                    spring._trot_max,
                    spring._trot_min,
                    spring._trot_pu,
                    spring._trot_nu,
                    spring._tenergy_d,
                    spring._tload_indicator,
                    spring._tstress,
                    spring._tstrain,
                    int(spring.t_phase),
                    spring.k_tang,
                ],
                dtype=float,
            )
            np.testing.assert_array_equal(runtime.trial[index], expected)
        for spring in scalar:
            spring.commit()
        runtime.commit()


@pytest.mark.skipif(batch.njit is None, reason="Numba is unavailable")
def test_compiled_quad_reload_tangents_use_csharp_minimum():
    """The dense Takeda path must not bypass SpringCoulomb03 getters."""
    row = np.zeros(batch.QUAD_STATE_SIZE, dtype=np.float64)
    params = np.zeros(batch.QUAD_PARAM_SIZE, dtype=np.float64)
    params[batch.QPK] = 10_000.0
    params[batch.QPE3P] = -100.0
    params[batch.QPE3N] = -100.0

    # C# stores the raw values, but every read returns max(0.0001*K, value).
    row[batch.QTANG_RELOAD_T] = 0.0
    row[batch.QTANG_RELOAD_C] = 0.0
    assert batch._quad_tangent_reload_t(row, params) == 1.0
    assert batch._quad_tangent_reload_c(row, params) == 1.0

    # Exercise the same compression branch that failed in the scalar path.
    row[batch.QTPHASE] = batch.RELOAD_C
    row[batch.QTROT_PU] = 0.0
    row[batch.QMOM1N] = -100.0
    row[batch.QROT3N] = -1.0
    yn = batch._quad_yield_compression(
        row, params, batch.ELASTIC, -1.0e-6
    )
    assert np.isfinite(yn)
    assert yn == pytest.approx(-100.0 / 101.0)

    # Exercise the symmetric tension branch.
    row[batch.QTPHASE] = batch.RELOAD_T
    row[batch.QTROT_NU] = 0.0
    row[batch.QMOM1P] = 100.0
    row[batch.QROT3P] = 1.0
    yp = batch._quad_yield_tension(
        row, params, batch.ELASTIC, 1.0e-6
    )
    assert np.isfinite(yp)
    assert yp == pytest.approx(100.0 / 101.0)

@pytest.mark.skipif(_evaluate_linear_batch is None, reason="Numba is unavailable")
def test_compiled_hysteretic_batch_can_force_general_kernel(monkeypatch):
    monkeypatch.delenv("HISTRA_DISABLE_COMPILED_SPRINGS", raising=False)
    monkeypatch.setenv("HISTRA_FORCE_GENERAL_HYSTERETIC_BATCH", "1")
    model = load_model(MODEL)
    runtime = build_hysteretic_batch(model)
    assert runtime is not None
    assert runtime._simple_hysteretic is False


@pytest.mark.skipif(_evaluate_linear_batch is None, reason="Numba is unavailable")
def test_compiled_hysteretic_batch_can_disable_quad_batch(monkeypatch):
    monkeypatch.delenv("HISTRA_DISABLE_COMPILED_SPRINGS", raising=False)
    monkeypatch.setenv("HISTRA_DISABLE_COMPILED_QUADS", "1")
    model = load_model(MODEL)
    runtime = build_hysteretic_batch(model)
    assert runtime is not None
    assert runtime.quad_records == []
    assert len(runtime.unmanaged_quads) == len(model.collections.quads)
    assert runtime._quad_local_du.shape == (0, 7)
    assert runtime._quad_local_u.shape == (0, 7)
    assert runtime._quad_edge_areas.shape == (0, 4)

    # Numba type-checks the complete fused kernel, including the Quad branch,
    # even though there are no managed Quads. Exercise the interface-only
    # update to ensure every empty Quad array retains its production rank.
    runtime.update_domain(
        np.zeros(int(model.gdl), dtype=np.float64),
        type("State", (), {"step": 1})(),
    )

def test_compiled_hysteretic_batch_can_be_disabled(monkeypatch):
    monkeypatch.setenv("HISTRA_DISABLE_COMPILED_SPRINGS", "1")
    model = load_model(MODEL)
    assert build_hysteretic_batch(model) is None
