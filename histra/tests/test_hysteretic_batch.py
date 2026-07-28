from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import numpy as np
import pytest

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


def test_compiled_hysteretic_batch_can_be_disabled(monkeypatch):
    monkeypatch.setenv("HISTRA_DISABLE_COMPILED_SPRINGS", "1")
    model = load_model(MODEL)
    assert build_hysteretic_batch(model) is None
