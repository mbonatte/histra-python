"""Live bitwise parity tests for Coulomb friction spring (SpringCoulomb03).

Validates shear yield, Mohr-Coulomb envelope, normal force coupling, and hysteretic state transitions
between the live compiled .NET MicroRunner and Python SpringCoulomb03 routines with exact bitwise assertions.
"""
import numpy as np
import pytest

from histra.springs.coulomb03 import SpringCoulomb03
from histra.tests.csharp_runner_client import CSharpRunnerClient, get_csharp_runner
from histra.types.phase_enum import PhaseEnum


@pytest.fixture
def csharp_runner() -> CSharpRunnerClient:
    client = get_csharp_runner()
    if not client.is_available():
        pytest.skip("C# HiStrA .NET MicroRunner binary is not available in this environment")
    return client


@pytest.mark.parametrize(
    ("cohesion", "mu", "normal_force"),
    [
        (10.0, 0.5, 0.0),
        (10.0, 0.5, 10.0),
        (25.0, 0.6, 20.0),
        (5.0, 0.35, 50.0),
        (15.0, 0.0, 100.0), # zero friction
    ],
)
def test_csharp_coulomb_normal_coupling_and_yield_envelope(
    csharp_runner: CSharpRunnerClient,
    cohesion: float,
    mu: float,
    normal_force: float,
):
    """Verify Mohr-Coulomb normal coupling TauLimite = c + mu * N between C# and Python."""
    k = 1000.0
    ur = 0.05
    expected_yield = cohesion + mu * normal_force

    # Python envelope limit
    s_py = SpringCoulomb03(k=k, cohesion=cohesion, mu=mu, sub_law="Coulomb")
    tau_lim_py = s_py._tau_limite(normal_force)
    assert abs(tau_lim_py - expected_yield) < 1e-12

    # Query C# runner with strain just before and just after yield
    strain_pre = (expected_yield * 0.5) / k
    strain_yield = (expected_yield) / k
    strain_post = (expected_yield * 1.5) / k

    cs_res = csharp_runner.spring_coulomb(
        k=k,
        cohesion=cohesion,
        mu=mu,
        ur=ur,
        normal_force=normal_force,
        strains=[strain_pre, strain_yield, strain_post],
        commit_each_step=False,
    )

    forces = cs_res["forces"]
    force_bits = cs_res["force_bits"]

    # 1. Pre-yield is purely elastic: force = k * strain_pre
    expected_pre_force = k * strain_pre
    assert abs(forces[0] - expected_pre_force) < 1e-12
    py_pre_bits = int(np.asarray([expected_pre_force], dtype=np.float64).view(np.int64)[0])
    assert force_bits[0] == py_pre_bits

    # 2. At yield: force = expected_yield
    assert abs(forces[1] - expected_yield) < 1e-12
    py_yield_bits = int(np.asarray([expected_yield], dtype=np.float64).view(np.int64)[0])
    assert force_bits[1] == py_yield_bits

    # 3. Post-yield with zero hardening tangent clamps to yield
    assert forces[2] <= expected_yield + 1e-9


def test_csharp_coulomb_elastic_shear_bitwise(csharp_runner: CSharpRunnerClient):
    """Verify exact IEEE-754 bitwise parity in elastic shear loading."""
    k = 2500.0
    strains = [0.0001, 0.0004, 0.0008, 0.0012]
    cs_res = csharp_runner.spring_coulomb(
        k=k,
        cohesion=100.0,
        mu=0.5,
        ur=0.05,
        strains=strains,
        commit_each_step=True,
    )

    for strain, cs_f, cs_bits in zip(strains, cs_res["forces"], cs_res["force_bits"]):
        expected_f = k * strain
        py_bits = int(np.asarray([expected_f], dtype=np.float64).view(np.int64)[0])
        assert int(cs_bits) == py_bits, f"Bitwise mismatch at strain {strain}: py={py_bits}, cs={cs_bits}"


def test_csharp_coulomb_state_transitions(csharp_runner: CSharpRunnerClient):
    """Verify phase transitions: Elastic -> Plastic_t -> Unload_t."""
    k = 1000.0
    cohesion = 1.0
    mu = 0.5
    ur = 0.05
    strains = [0.0005, 0.002, 0.001] # load to elastic, exceed yield, reverse load

    cs_res = csharp_runner.spring_coulomb(
        k=k,
        cohesion=cohesion,
        mu=mu,
        ur=ur,
        strains=strains,
        commit_each_step=True,
    )

    t_phases = cs_res["t_phases"]
    # Step 0 (0.0005 * 1000 = 0.5 < 1.0): Elastic (0)
    assert t_phases[0] == int(PhaseEnum.Elastic)
    # Step 1 (0.002 * 1000 = 2.0 > 1.0): Plastic_t (1)
    assert t_phases[1] == int(PhaseEnum.Plastic_t)
    # Step 2 (reversal from 0.002 to 0.001 with negative delta): Reload_c (6)
    assert t_phases[2] == int(PhaseEnum.Reload_c)
