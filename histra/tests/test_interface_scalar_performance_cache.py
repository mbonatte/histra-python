from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass

import numpy as np

from histra.elements.interface import Interface
from histra.types.afference_entry import AfferenceEntry


@dataclass
class _Spring:
    u: float = 0.0
    _cstress: float = 0.25
    _tstress: float = 0.25
    stiffness: float = 3.0

    def set_trial_strain(self, value: float) -> None:
        self._tstress = self._cstress + self.stiffness * value


def _old_update_domain(interface: Interface, x: np.ndarray) -> None:
    """The pre-optimization scalar path, retained as an exact oracle."""
    interface._ensure_performance_cache()
    local_du = [0.0] * interface.dim_aff_tot
    for i, pairs in enumerate(interface._perf_aff_pairs or ()):
        total = 0.0
        for gdl, coefficient in pairs:
            if 0 <= gdl < len(x):
                total += x[gdl] * coefficient
        local_du[i] = total
    for i, value in enumerate(local_du):
        interface.status.u[i] += float(value)
    if not interface.interfaccia_vincolata_computed():
        num = local_du[3] - local_du[0]
        num2 = local_du[2] - local_du[1]
    else:
        half_length = interface.length / 2.0
        num = local_du[3] - (local_du[0] - local_du[1] * half_length)
        num2 = local_du[2] - (local_du[0] + local_du[1] * half_length)
    delta_flex = local_du[5] - local_du[4]
    normal_increment = 0.0
    committed_normal_force = 0.0
    max_displacement = 0.0
    inv_length = 1.0 / interface.length
    for spring, di, dj, ecc in zip(
        interface.trasv_1,
        interface._perf_di or (),
        interface._perf_dj or (),
        interface._perf_ecc or (),
    ):
        increment = (num * dj + num2 * di) * inv_length - delta_flex * ecc
        new_u = spring.u + increment
        spring.u = new_u
        spring.set_trial_strain(new_u)
        if "get_incr_force" in spring.__dict__ or "get_force" in spring.__dict__:
            trial = float(spring.get_force())
            committed = trial - float(spring.get_incr_force())
        else:
            trial = float(spring._tstress)
            committed = float(spring._cstress)
        normal_increment -= trial - committed
        committed_normal_force += committed
        abs_u = abs(new_u)
        if abs_u > max_displacement:
            max_displacement = abs_u
    interface.status.normal_increment = normal_increment
    interface.status.committed_normal_force = committed_normal_force
    interface.status.max_spring_displacement = max_displacement


def _make_interface() -> Interface:
    interface = Interface(length=2.5, nrow=1, ncol=3, nspring=3)
    interface.trasv_1 = [_Spring(), _Spring(stiffness=4.0), _Spring(stiffness=5.0)]
    interface.aff = [[] for _ in range(12)]
    for local_dof in range(6):
        interface.aff[local_dof] = [
            AfferenceEntry(gdl=local_dof + 1, alfa=1.0),
            AfferenceEntry(gdl=12 - local_dof, alfa=-0.125),
        ]
    return interface


def test_cached_scalar_update_is_bitwise_equal_to_previous_path() -> None:
    expected = _make_interface()
    actual = deepcopy(expected)
    increment = np.asarray(
        [0.001, -0.002, 0.003, -0.004, 0.005, -0.006,
         0.007, -0.008, 0.009, -0.010, 0.011, -0.012],
        dtype=np.float64,
    )

    _old_update_domain(expected, increment)
    actual.update_domain(increment, object())

    np.testing.assert_array_equal(actual.status.u, expected.status.u)
    assert actual.status.normal_increment == expected.status.normal_increment
    assert actual.status.committed_normal_force == expected.status.committed_normal_force
    assert actual.status.max_spring_displacement == expected.status.max_spring_displacement
    for actual_spring, expected_spring in zip(actual.trasv_1, expected.trasv_1):
        assert actual_spring.u == expected_spring.u
        assert actual_spring._tstress == expected_spring._tstress


def test_local_increment_reuses_private_work_buffer() -> None:
    interface = _make_interface()
    first = interface._local_increment(np.ones(12, dtype=np.float64))
    first_id = id(first)
    second = interface._local_increment(np.zeros(12, dtype=np.float64))
    assert id(second) == first_id
    assert second == [0.0] * 12
