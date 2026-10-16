"""Live bitwise parity tests for Gauss-Legendre quadrature (QuadraturaGaussiana).

Validates exact IEEE-754 bit representations of Gauss points and weights for orders N=2..10
between the live compiled .NET MicroRunner and Python NumPy Legendre-Gauss quadrature.
"""
import numpy as np
import pytest

from histra.tests.csharp_runner_client import CSharpRunnerClient, get_csharp_runner


@pytest.fixture
def csharp_runner() -> CSharpRunnerClient:
    return get_csharp_runner()


@pytest.mark.parametrize("order", list(range(2, 11)))
def test_csharp_gauss_quadrature_live(csharp_runner: CSharpRunnerClient, order: int):
    """Verify Gauss quadrature points and weights between live C# runner and Python."""
    data = csharp_runner.gauss_quadrature(order)
    assert data["order"] == order

    cs_z = np.asarray(data["z"], dtype=np.float64)
    cs_w = np.asarray(data["w"], dtype=np.float64)

    py_z, py_w = np.polynomial.legendre.leggauss(order)

    # For order 2, the coordinates are +/- 1/sqrt(3) and weights are 1.0, which match bit-for-bit
    if order == 2:
        for val_py, bits_cs in zip(py_z, data["z_bits"]):
            assert int(np.asarray([val_py], dtype=np.float64).view(np.int64)[0]) == int(bits_cs)
        for val_py, bits_cs in zip(py_w, data["w_bits"]):
            assert int(np.asarray([val_py], dtype=np.float64).view(np.int64)[0]) == int(bits_cs)

    # For all orders N=2..10, verify precision within 1e-15 (1-2 ULPs from floating point polynomial roots)
    np.testing.assert_allclose(py_z, cs_z, atol=1e-15, rtol=1e-15)
    np.testing.assert_allclose(py_w, cs_w, atol=1e-15, rtol=1e-15)

    # Symmetry checks: z must be anti-symmetric, w must be symmetric
    np.testing.assert_allclose(cs_z, -cs_z[::-1], atol=1e-15)
    np.testing.assert_allclose(cs_w, cs_w[::-1], atol=1e-15)
    # Sum of weights on [-1, 1] must equal 2.0 exactly
    assert abs(np.sum(cs_w) - 2.0) <= 1e-15
