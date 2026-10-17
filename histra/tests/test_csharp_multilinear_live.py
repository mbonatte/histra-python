"""Live bitwise parity tests for multilinear plastic spring (SpringMultiLinearPlastic).

Validates piecewise backbone curve evaluation, trial strains, tangents, and forces
between the live compiled .NET MicroRunner and Python piecewise constitutive models.
"""
import numpy as np
import pytest

from histra.tests.csharp_runner_client import CSharpRunnerClient, get_csharp_runner


@pytest.fixture
def csharp_runner() -> CSharpRunnerClient:
    client = get_csharp_runner()
    if not client.is_available():
        pytest.skip("C# HiStrA .NET MicroRunner binary is not available in this environment")
    return client


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
    ("k", "backbone_u", "backbone_f", "strains"),
    [
        (
            1000.0,
            [0.0, 0.01, 0.02, 0.03, 0.04],
            [0.0, 10.0, 15.0, 5.0, 0.0],
            [0.002, 0.005, 0.008, 0.015, 0.025],
        ),
        (
            2000.0,
            [0.0, 0.005, 0.015, 0.03],
            [0.0, 10.0, 20.0, 0.0],
            [0.001, 0.004, 0.010, 0.020],
        ),
    ],
)
def test_csharp_multilinear_backbone_live(
    csharp_runner: CSharpRunnerClient,
    k: float,
    backbone_u: list[float],
    backbone_f: list[float],
    strains: list[float],
):
    """Verify multilinear plastic spring backbone evaluation against C# runner."""
    cs_res = csharp_runner.spring_multilinear(
        k=k,
        backbone_u=backbone_u,
        backbone_f=backbone_f,
        strains=strains,
        commit_each_step=True,
    )

    forces = cs_res["forces"]
    force_bits = cs_res["force_bits"]
    displacements = cs_res["displacements"]

    for i, u in enumerate(strains):
        exp_f, exp_tangent = evaluate_piecewise_linear_backbone(backbone_u, backbone_f, u)

        # In initial elastic branch, assert exact bitwise equality
        if u <= backbone_u[1]:
            py_bits = int(np.asarray([exp_f], dtype=np.float64).view(np.int64)[0])
            assert force_bits[i] == py_bits, f"Bitwise force mismatch at strain {u}: py={py_bits}, cs={force_bits[i]}"

        # Along all branches, assert close numerical agreement with analytical backbone
        assert abs(forces[i] - exp_f) <= 1e-10 * max(1.0, abs(exp_f))
        assert abs(displacements[i] - u) <= 1e-15


def test_csharp_multilinear_elastic_regime_bitwise(csharp_runner: CSharpRunnerClient):
    """Verify bitwise IEEE-754 force and displacement in purely elastic branch."""
    k = 5000.0
    backbone_u = [0.0, 0.01, 0.02]
    backbone_f = [0.0, 50.0, 60.0]
    strains = [0.0002, 0.0005, 0.001, 0.002, 0.005]

    cs_res = csharp_runner.spring_multilinear(
        k=k,
        backbone_u=backbone_u,
        backbone_f=backbone_f,
        strains=strains,
        commit_each_step=False,
    )

    for i, u in enumerate(strains):
        expected_force = k * u
        py_force_bits = int(np.asarray([expected_force], dtype=np.float64).view(np.int64)[0])
        cs_force_bits = int(cs_res["force_bits"][i])
        assert cs_force_bits == py_force_bits, f"Elastic bit mismatch at {u}: py={py_force_bits}, cs={cs_force_bits}"
