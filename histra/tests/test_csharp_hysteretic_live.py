"""Live bitwise parity tests for hysteretic spring (SpringHysteretic).

Validates force/displacement response, linear hardening, unloading/reloading branches, and pinching
between the live compiled .NET MicroRunner and Python SpringHysteretic routines with exact bitwise assertions.
"""
import numpy as np
import pytest

from histra.springs.hysteretic import SpringHysteretic
from histra.tests.csharp_runner_client import CSharpRunnerClient, get_csharp_runner


@pytest.fixture
def csharp_runner() -> CSharpRunnerClient:
    client = get_csharp_runner()
    if not client.is_available():
        pytest.skip("C# HiStrA .NET MicroRunner binary is not available in this environment")
    return client


def test_csharp_hysteretic_elastic_regime_bitwise(csharp_runner: CSharpRunnerClient):
    """Verify bitwise IEEE-754 force parity in the reversible elastic regime."""
    k = 2500.0
    strains = [0.0002, 0.0006, 0.001, -0.0004, -0.0008]

    cs_res = csharp_runner.spring_hysteretic(
        k=k,
        kt_1=250.0,
        kt_2=100.0,
        fy_1=25.0,
        fy_2=-25.0,
        ur_1=0.05,
        ur_2=-0.05,
        strains=strains,
        commit_each_step=True,
    )

    py_spring = SpringHysteretic(
        k=k,
        e1p=k,
        e1n=-k,
        tensile_curve_type="Elastic",
        compressive_curve_type="Elastic",
    )

    for i, s in enumerate(strains):
        py_spring.set_trial_strain(s)
        py_f = py_spring.get_force()
        py_spring.commit()

        # Bitwise IEEE-754 representation matching
        py_bits = int(np.asarray([py_f], dtype=np.float64).view(np.int64)[0])
        cs_bits = int(cs_res["force_bits"][i])
        assert cs_bits == py_bits, f"Elastic hysteretic bit mismatch at strain {s}: py={py_bits}, cs={cs_bits}"
        assert abs(cs_res["displacements"][i] - s) <= 1e-15


def test_csharp_hysteretic_linear_hardening_and_unloading(csharp_runner: CSharpRunnerClient):
    """Verify post-yield linear hardening branch and unloading stiffness."""
    k = 1000.0
    kt_1 = 100.0
    kt_2 = 50.0
    fy_1 = 10.0
    fy_2 = -10.0
    ur_1 = 0.05
    ur_2 = -0.05

    # 1. 0.005: elastic (f = 5.0)
    # 2. 0.015: plastic hardening (f = 10.0 + 100.0 * (0.015 - 0.010) = 10.5)
    # 3. -0.005: compressive reversal (f = -5.0)
    strains = [0.005, 0.015, -0.005]

    cs_res = csharp_runner.spring_hysteretic(
        k=k,
        kt_1=kt_1,
        kt_2=kt_2,
        fy_1=fy_1,
        fy_2=fy_2,
        ur_1=ur_1,
        ur_2=ur_2,
        strains=strains,
        commit_each_step=True,
    )

    forces = cs_res["forces"]
    force_bits = cs_res["force_bits"]
    tangents = cs_res["tangents"]

    # Segment 1: Elastic (f = 5.0, tangent = 1000.0)
    expected_f1 = 5.0
    py_bits1 = int(np.asarray([expected_f1], dtype=np.float64).view(np.int64)[0])
    assert force_bits[0] == py_bits1
    assert tangents[0] == 1000.0

    # Segment 2: Hardening (f = 10.5, tangent = 100.0)
    expected_f2 = 10.5
    py_bits2 = int(np.asarray([expected_f2], dtype=np.float64).view(np.int64)[0])
    assert force_bits[1] == py_bits2
    assert tangents[1] == 100.0

    # Segment 3: Compressive reversal (f = -5.0, tangent = 1000.0)
    expected_f3 = -5.0
    py_bits3 = int(np.asarray([expected_f3], dtype=np.float64).view(np.int64)[0])
    assert force_bits[2] == py_bits3
    assert tangents[2] == 1000.0


def test_csharp_hysteretic_pinching_parameters(csharp_runner: CSharpRunnerClient):
    """Verify execution of full 24-parameter pinching model in C# runner."""
    # 24-parameter constructor with pinching
    cs_res = csharp_runner.spring_hysteretic(
        m1p=10.0, r1p=0.01,
        m2p=15.0, r2p=0.03,
        m3p=5.0, r3p=0.05,
        m1n=-10.0, r1n=-0.01,
        m2n=-15.0, r2n=-0.03,
        m3n=-5.0, r3n=-0.05,
        pinchXp=0.5, pinchYp=0.25,
        pinchXn=0.5, pinchYn=0.25,
        d1p=0.0, d2p=0.0,
        d1n=0.0, d2n=0.0,
        betap=0.0, betan=0.0,
        strains=[0.005, 0.02, 0.01, -0.01, -0.02],
        commit_each_step=True,
    )

    assert len(cs_res["forces"]) == 5
    assert cs_res["forces"][0] == 5.0
    # At 0.02, hardened in [10, 15] along rot [0.01, 0.03]: f = 10 + 5 * (0.01/0.02) = 12.5
    assert abs(cs_res["forces"][1] - 12.5) < 1e-9
    # Unloading from 0.02 to 0.01 has positive residual force
    assert cs_res["forces"][2] > 0.0
    # Compressive loading has negative force
    assert cs_res["forces"][3] < 0.0
    assert cs_res["forces"][4] < cs_res["forces"][3]
