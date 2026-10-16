"""Live bitwise parity tests for convergence criteria (CTestNormUnbalance, CTestNormDispIncr, CTestEnergyIncr).

Validates unbalance (ForceMoment), displacement increment (DispRotation), and energy increment (Work)
between the live compiled .NET MicroRunner and Python ConvergenceTest with exact IEEE-754 bit representations.
"""
from types import SimpleNamespace
import numpy as np
import pytest

from histra.tests.csharp_runner_client import CSharpRunnerClient, get_csharp_runner
from histra.types.convergence_test import ConvergenceTest
from histra.types.linear_system import LinearSystem


@pytest.fixture
def csharp_runner() -> CSharpRunnerClient:
    return get_csharp_runner()


@pytest.fixture
def mock_solver_environment():
    """Minimal mock model and program for isolated convergence testing."""
    mock_model = SimpleNamespace(collections=SimpleNamespace(quads={}))
    mock_program = SimpleNamespace(max_u=0.0)
    return mock_program, mock_model


@pytest.mark.parametrize(
    ("residual", "tol", "expected_converged"),
    [
        ([3.0, 4.0], 10.0, True),     # Norm is 5.0 <= 10.0
        ([3.0, 4.0], 1.0, False),     # Norm is 5.0 > 1.0
        ([1.0, -2.0, 2.0], 5.0, True), # Norm is 3.0 <= 5.0
        ([0.0, 0.0, 0.0], 1e-6, True), # Zero residual
        ([12.0, 5.0], 12.5, False),    # Norm is 13.0 > 12.5
    ],
)
def test_csharp_convergence_unbalance_live(
    csharp_runner: CSharpRunnerClient,
    mock_solver_environment,
    residual: list[float],
    tol: float,
    expected_converged: bool,
):
    """Verify CTestNormUnbalance (ForceMoment) between C# runner and Python."""
    mock_program, mock_model = mock_solver_environment

    cs_res = csharp_runner.convergence_criteria("unbalance", tol=tol, residual=residual)
    assert cs_res["converged"] == expected_converged

    ls = LinearSystem(len(residual))
    ls.b = np.asarray(residual, dtype=np.float64)

    ct = ConvergenceTest(tolerance=tol, criterion="ForceMoment")
    ct.start(ls)
    py_code = ct.test(mock_program, mock_model, ls)

    assert (py_code >= 0) == cs_res["converged"]
    py_bits = int(np.asarray([ct._error], dtype=np.float64).view(np.int64)[0])
    cs_bits = int(cs_res["error_bits"])
    assert py_bits == cs_bits, f"Unbalance error_bits mismatch: py={py_bits}, cs={cs_bits}"


@pytest.mark.parametrize(
    ("displacement", "tol", "expected_converged"),
    [
        ([0.03, 0.04], 0.05, True),   # Norm is 0.05 <= 0.05
        ([0.03, 0.04], 0.01, False),  # Norm is 0.05 > 0.01
        ([0.001, 0.002, -0.002], 0.01, True), # Norm is 0.003 <= 0.01
        ([0.0, 0.0], 1e-8, True),     # Zero displacement
    ],
)
def test_csharp_convergence_displacement_live(
    csharp_runner: CSharpRunnerClient,
    mock_solver_environment,
    displacement: list[float],
    tol: float,
    expected_converged: bool,
):
    """Verify CTestNormDispIncr (DispRotation) between C# runner and Python."""
    mock_program, mock_model = mock_solver_environment

    cs_res = csharp_runner.convergence_criteria("displacement", tol=tol, displacement=displacement)
    assert cs_res["converged"] == expected_converged

    ls = LinearSystem(len(displacement))
    ls.x = np.asarray(displacement, dtype=np.float64)

    ct = ConvergenceTest(tolerance=tol, criterion="DispRotation")
    ct.start(ls)
    py_code = ct.test(mock_program, mock_model, ls)

    assert (py_code >= 0) == cs_res["converged"]
    py_bits = int(np.asarray([ct._error], dtype=np.float64).view(np.int64)[0])
    cs_bits = int(cs_res["error_bits"])
    assert py_bits == cs_bits, f"Displacement error_bits mismatch: py={py_bits}, cs={cs_bits}"


@pytest.mark.parametrize(
    ("residual", "displacement", "tol", "expected_converged"),
    [
        ([2.0, 3.0], [0.1, 0.2], 1.0, True),    # Work = 0.5 * (0.2 + 0.6) = 0.4 <= 1.0
        ([2.0, 3.0], [0.1, 0.2], 0.1, False),   # Work = 0.4 > 0.1
        ([10.0, -5.0], [0.02, 0.04], 0.001, True), # Work = 0.5 * abs(0.2 - 0.2) = 0.0 <= 0.001
        ([4.0, 6.0], [1.0, 2.0], 5.0, False),   # Work = 0.5 * (4 + 12) = 8.0 > 5.0
    ],
)
def test_csharp_convergence_energy_live(
    csharp_runner: CSharpRunnerClient,
    mock_solver_environment,
    residual: list[float],
    displacement: list[float],
    tol: float,
    expected_converged: bool,
):
    """Verify CTestEnergyIncr (Work) between C# runner and Python."""
    mock_program, mock_model = mock_solver_environment

    cs_res = csharp_runner.convergence_criteria("energy", tol=tol, residual=residual, displacement=displacement)
    assert cs_res["converged"] == expected_converged

    ls = LinearSystem(len(residual))
    ls.b = np.asarray(residual, dtype=np.float64)
    ls.x = np.asarray(displacement, dtype=np.float64)

    ct = ConvergenceTest(tolerance=tol, criterion="Work")
    ct.start(ls)
    py_code = ct.test(mock_program, mock_model, ls)

    assert (py_code >= 0) == cs_res["converged"]
    py_bits = int(np.asarray([ct._error], dtype=np.float64).view(np.int64)[0])
    cs_bits = int(cs_res["error_bits"])
    assert py_bits == cs_bits, f"Energy error_bits mismatch: py={py_bits}, cs={cs_bits}"
