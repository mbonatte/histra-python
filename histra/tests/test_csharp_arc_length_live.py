"""Live bitwise parity tests for Arc-Length Crisfield constraint update.

Compares root selection, delta_lambda, and incremental displacement delta_u
between the live compiled C# micro-runner and Python ArcLength with exact
IEEE-754 bit representations.
"""
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pytest

from histra.solver.arc_length import ArcLength
from histra.tests.csharp_runner_client import CSharpRunnerClient, get_csharp_runner

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "csharp_arc_length_update_2026_1_1.json"


@pytest.fixture
def csharp_runner() -> CSharpRunnerClient:
    return get_csharp_runner()


class MockLinearSystem:
    def __init__(self, val: float):
        self.matrix_version = 1
        self.x = np.array([val], dtype=np.float64)

    def solve(self, rhs):
        self.x = rhs.copy()

    def set_x_vector(self, values):
        self.x = values.copy()


def _run_python_arc_length(case: dict) -> tuple[int, ArcLength]:
    arc = ArcLength(constraint_mode="csharp")
    arc._alpha2 = float(case["alpha2"])
    arc._phat = np.array([float(case["hat"])], dtype=np.float64)
    arc._delta_u_step = np.array([float(case["step"])], dtype=np.float64)
    arc._dofs = np.array([0])
    arc.u = np.zeros(1, dtype=np.float64)
    arc.state.combination = 1
    arc.update_ptarget = lambda *args: None
    arc.apply_load_domain = lambda *args: None

    with patch("histra.solver.arc_length.ModelManager.update_domain"):
        code = arc.update(object(), SimpleNamespace(ls=MockLinearSystem(float(case["bar"]))), object())
    return code, arc


def test_csharp_arc_length_live_all_fixture_cases(csharp_runner: CSharpRunnerClient):
    """Verify all 8 authoritative ArcLength update cases against live C# micro-runner."""
    cases = json.loads(FIXTURE_PATH.read_text(encoding="utf-8-sig"))["cases"]

    for i, case in enumerate(cases):
        cs_res = csharp_runner.arc_length(case)
        py_code, arc = _run_python_arc_length(case)

        # Verification of return code
        assert py_code == cs_res["code"], f"Case {i} return code mismatch: py={py_code}, cs={cs_res['code']}"

        if case["code"] < 0:
            assert arc.errors
            assert arc._delta_lambda_step == 0.0
            assert arc.u[0] == 0.0
        else:
            py_lambda_bits = int(np.asarray([arc._last_delta_lambda], dtype=np.float64).view(np.int64)[0])
            cs_lambda_bits = int(cs_res["lambda_bits"])
            assert py_lambda_bits == cs_lambda_bits, f"Case {i} lambda_bits mismatch: py={py_lambda_bits}, cs={cs_lambda_bits}"

            py_du_bits = int(np.asarray([arc._last_delta_u[0]], dtype=np.float64).view(np.int64)[0])
            cs_du_bits = int(cs_res["du_bits"])
            assert py_du_bits == cs_du_bits, f"Case {i} du_bits mismatch: py={py_du_bits}, cs={cs_du_bits}"


@pytest.mark.parametrize(
    ("alpha2", "hat", "bar", "step"),
    [
        (0.0, 2.0, 0.5, 0.02),
        (1.0, 1.5, -0.2, 0.05),
        (0.5, 3.0, 1.2, -0.01),
    ],
)
def test_csharp_arc_length_live_dynamic_cases(
    csharp_runner: CSharpRunnerClient,
    alpha2: float,
    hat: float,
    bar: float,
    step: float,
):
    """Verify dynamically synthesized parameters against live C# micro-runner."""
    case = {"alpha2": alpha2, "hat": hat, "bar": bar, "step": step}
    cs_res = csharp_runner.arc_length(case)
    py_code, arc = _run_python_arc_length(case)

    assert py_code == cs_res["code"]
    if py_code == 0:
        py_lambda_bits = int(np.asarray([arc._last_delta_lambda], dtype=np.float64).view(np.int64)[0])
        cs_lambda_bits = int(cs_res["lambda_bits"])
        assert py_lambda_bits == cs_lambda_bits

        py_du_bits = int(np.asarray([arc._last_delta_u[0]], dtype=np.float64).view(np.int64)[0])
        cs_du_bits = int(cs_res["du_bits"])
        assert py_du_bits == cs_du_bits
