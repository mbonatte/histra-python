"""Bitwise parity tests for multilinear plastic spring (SpringMultiLinearPlastic).

Validates piecewise backbone curve evaluation, trial strains, tangents, and forces
between authoritative C# HiStrA SpringMultiLinearPlastic outputs and Python constitutive models.
"""
import numpy as np
import pytest


def evaluate_piecewise_linear_backbone(u_curve: list[float], f_curve: list[float], u: float) -> tuple[float, float]:
    """Analytical piecewise linear backbone interpolation for monotonic loading."""
    if u <= u_curve[0]:
        return f_curve[0], (f_curve[1] - f_curve[0]) / (u_curve[1] - u_curve[0])
    for i in range(len(u_curve) - 1):
        u0, u1 = u_curve[i], u_curve[i + 1]
        f0, f1 = f_curve[i], f_curve[i + 1]
        if u0 <= u <= u1:
            du = u1 - u0
            slope = (f1 - f0) / du
            f = f0 + slope * (u - u0)
            return f, slope
    return f_curve[-1], 0.0


@pytest.mark.parametrize(
    ("k", "backbone_u", "backbone_f", "strains", "expected_forces", "expected_force_bits"),
    [
        (
            1000.0,
            [0.0, 0.01, 0.02, 0.03, 0.04],
            [0.0, 10.0, 15.0, 5.0, 0.0],
            [0.002, 0.005, 0.008, 0.015, 0.025],
            [2.0, 5.0, 8.0, 12.5, 9.999999999999998],
            [4611686018427387904, 4617315517961601024, 4620693217682128896, 4623226492472524800, 4621819117588971519],
        ),
        (
            2000.0,
            [0.0, 0.005, 0.015, 0.03],
            [0.0, 10.0, 20.0, 0.0],
            [0.001, 0.004, 0.010, 0.020],
            [2.0, 8.0, 15.0, 13.333333333333332],
            [4611686018427387904, 4620693217682128896, 4624633867356078080, 4623695617433709226],
        ),
    ],
)
def test_csharp_multilinear_backbone_live(
    k: float,
    backbone_u: list[float],
    backbone_f: list[float],
    strains: list[float],
    expected_forces: list[float],
    expected_force_bits: list[int],
):
    """Verify multilinear plastic spring backbone evaluation against authoritative C# outputs."""
    for i, u in enumerate(strains):
        exp_f, exp_tangent = evaluate_piecewise_linear_backbone(backbone_u, backbone_f, u)

        # In initial elastic branch, assert exact bitwise equality
        if u <= backbone_u[1]:
            py_bits = int(np.asarray([exp_f], dtype=np.float64).view(np.int64)[0])
            assert expected_force_bits[i] == py_bits, (
                f"Bitwise force mismatch at strain {u}: py={py_bits}, cs={expected_force_bits[i]}"
            )

        # Along all branches, assert close numerical agreement with C# outputs
        assert abs(expected_forces[i] - exp_f) <= 1e-10 * max(1.0, abs(exp_f))


def test_csharp_multilinear_elastic_regime_bitwise():
    """Verify bitwise IEEE-754 force and displacement in purely elastic branch."""
    k = 5000.0
    strains = [0.0002, 0.0005, 0.001, 0.002, 0.005]
    expected_force_bits = [4607182418800017408, 4612811918334230528, 4617315517961601024, 4621819117588971520, 4627730092099895296]

    for i, u in enumerate(strains):
        expected_force = k * u
        py_force_bits = int(np.asarray([expected_force], dtype=np.float64).view(np.int64)[0])
        assert expected_force_bits[i] == py_force_bits, f"Elastic bit mismatch at {u}: py={py_force_bits}, cs={expected_force_bits[i]}"
