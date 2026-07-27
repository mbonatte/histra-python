"""Optional Numba batch runtime for interface SpringHysteretic objects.

The nonlinear benchmark updates thousands of independent transverse springs on
nearly every Newton correction.  Calling the Python state machine spring by
spring dominates runtime.  This module keeps the same committed/trial variables
in dense arrays and evaluates the linear-backbone hysteretic law in one compiled
loop.  Unsupported spring curves transparently remain on the Python path.
"""
from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any

import numpy as np

from histra.springs.hysteretic import SpringHysteretic
from histra.types.phase_enum import PhaseEnum

try:  # optional acceleration dependency
    from numba import njit
except Exception:  # pragma: no cover - exercised when numba is unavailable
    njit = None


ELASTIC = int(PhaseEnum.Elastic)
PLASTIC_T = int(PhaseEnum.Plastic_t)
PLASTIC_C = int(PhaseEnum.Plastic_c)
UNLOAD_T = int(PhaseEnum.Unload_t)
UNLOAD_C = int(PhaseEnum.Unload_c)
RELOAD_T = int(PhaseEnum.Reload_t)
RELOAD_C = int(PhaseEnum.Reload_c)
RUPTURE = int(PhaseEnum.Rupture)
RUPTURE_T = int(PhaseEnum.RuptureTraz)
RUPTURE_C = int(PhaseEnum.RuptureComp)


if njit is not None:
    @njit(cache=True, inline="always")
    def _pos_stress(strain, rot1p, mom1p, rot2p, mom2p, rot3p, mom3p, e1p, e2p, e3p):
        if strain <= 0.0:
            return 0.0
        if strain <= rot1p:
            return e1p * strain
        if strain <= rot2p:
            return mom1p + e2p * (strain - rot1p)
        if strain <= rot3p or e3p > 0.0:
            return mom2p + e3p * (strain - rot2p)
        return mom3p

    @njit(cache=True, inline="always")
    def _neg_stress(strain, mom1n, rot1n, rot2n, mom2n, rot3n, mom3n, e1n, e2n, e3n):
        if strain >= 0.0:
            return 0.0
        if strain >= rot1n:
            return e1n * strain
        if strain >= rot2n:
            return mom1n + e2n * (strain - rot1n)
        if strain >= rot3n or e3n > 0.0:
            return mom2n + e3n * (strain - rot2n)
        return mom3n

    @njit(cache=True, inline="always")
    def _pos_tangent(strain, rot1p, rot2p, rot3p, e1p, e2p, e3p):
        if strain < 0.0:
            return e1p * 1.0e-9, ELASTIC
        if strain <= rot1p:
            return e1p, ELASTIC
        if strain <= rot2p:
            return e2p, PLASTIC_T
        if strain <= rot3p or e3p > 0.0:
            return e3p, PLASTIC_T
        return e1p * 1.0e-9, RUPTURE_T

    @njit(cache=True, inline="always")
    def _neg_tangent(strain, rot1n, rot2n, rot3n, e1n, e2n, e3n):
        if strain > 0.0:
            return e1n * 1.0e-9, ELASTIC
        if strain >= rot1n:
            return e1n, ELASTIC
        if strain >= rot2n:
            return e2n, PLASTIC_C
        if strain >= rot3n or e3n > 0.0:
            return e3n, PLASTIC_C
        return e1n * 1.0e-9, RUPTURE_C

    @njit(cache=True, inline="always")
    def _pos_rotlim(strain, rot1p, mom1p, rot2p, mom2p, e2p, e3p,
                    rot3p, mom3p, e1p):
        result = np.inf
        if strain <= rot1p:
            return result
        if strain <= rot2p and e2p < 0.0 and e2p != 0.0:
            result = rot1p - mom1p / e2p
        if strain > rot2p and e3p < 0.0 and e3p != 0.0:
            result = rot2p - mom2p / e3p
        if np.isinf(result):
            return result
        if _pos_stress(result, rot1p, mom1p, rot2p, mom2p, rot3p, mom3p, e1p, e2p, e3p) > 0.0:
            return np.inf
        return result

    @njit(cache=True, inline="always")
    def _neg_rotlim(strain, mom1n, rot1n, rot2n, mom2n, e2n, e3n,
                    rot3n, mom3n, e1n):
        result = -np.inf
        if strain >= rot1n:
            return result
        if strain >= rot2n and e2n < 0.0 and e2n != 0.0:
            result = rot1n - mom1n / e2n
        if strain < rot2n and e3n < 0.0 and e3n != 0.0:
            result = rot2n - mom2n / e3n
        if np.isinf(result):
            return result
        if _neg_stress(result, mom1n, rot1n, rot2n, mom2n, rot3n, mom3n, e1n, e2n, e3n) < 0.0:
            return -np.inf
        return result

    @njit(cache=True, nogil=True)
    def _evaluate_linear_batch(params, committed, trial, targets, enabled):
        n = targets.size
        for i in range(n):
            if not enabled[i]:
                continue
            previous_tload = int(trial[i, 5])
            strain = targets[i]
            if previous_tload == 0 and strain == 0.0:
                continue

            pinch_xp, pinch_yp, pinch_xn, pinch_yn = params[i, 0], params[i, 1], params[i, 2], params[i, 3]
            damfc1p, damfc2p, damfc1n, damfc2n = params[i, 4], params[i, 5], params[i, 6], params[i, 7]
            betap, betan = params[i, 8], params[i, 9]
            rot1p, mom1p, rot2p, mom2p = params[i, 10], params[i, 11], params[i, 12], params[i, 13]
            rot3p, mom3p = params[i, 14], params[i, 15]
            mom1n, rot1n, rot2n, mom2n = params[i, 16], params[i, 17], params[i, 18], params[i, 19]
            rot3n, mom3n = params[i, 20], params[i, 21]
            e1n, e1p, e2n, e2p = params[i, 22], params[i, 23], params[i, 24], params[i, 25]
            e3n, e3p, eun, eup = params[i, 26], params[i, 27], params[i, 28], params[i, 29]
            energy_a = params[i, 30]

            umax_p, umax_n = committed[i, 0], committed[i, 1]
            trot_pu, trot_nu = committed[i, 2], committed[i, 3]
            cenergy = committed[i, 4]
            tload = int(committed[i, 5])
            cstress, cstrain = committed[i, 6], committed[i, 7]
            phase = int(committed[i, 8])

            trot_max, trot_min = umax_p, umax_n
            tstress, tstrain, tphase = cstress, strain, phase
            ktang = trial[i, 9]
            dstrain = tstrain - cstrain
            if tload == 0:
                tload = 1 if dstrain >= 0.0 else 2

            if phase == RUPTURE or phase == RUPTURE_C or phase == RUPTURE_T:
                tstress = 0.0
                ktang = 0.0
                if tstrain >= umax_p:
                    trot_max = tstrain
                elif tstrain <= umax_n:
                    trot_min = tstrain

            if tstrain >= umax_p:
                trot_max = tstrain
                tstress = _pos_stress(tstrain, rot1p, mom1p, rot2p, mom2p, rot3p, mom3p, e1p, e2p, e3p)
                ktang, tphase = _pos_tangent(tstrain, rot1p, rot2p, rot3p, e1p, e2p, e3p)
                tload = 1
            elif tstrain <= umax_n:
                trot_min = tstrain
                tstress = _neg_stress(tstrain, mom1n, rot1n, rot2n, mom2n, rot3n, mom3n, e1n, e2n, e3n)
                ktang, tphase = _neg_tangent(tstrain, rot1n, rot2n, rot3n, e1n, e2n, e3n)
                tload = 2
            elif dstrain < 0.0:
                tphase = UNLOAD_T if tstress > 0.0 else RELOAD_C
                num = (umax_n / rot1n) ** betan if rot1n != 0.0 else 0.0
                if num <= 1.0:
                    num = 1.0
                else:
                    env = _neg_stress(umax_n, mom1n, rot1n, rot2n, mom2n, rot3n, mom3n, e1n, e2n, e3n)
                    num = env / mom1n / num if num != 0.0 else 1.0
                num2 = (umax_p / rot1p) ** betap if rot1p != 0.0 else 0.0
                if num2 <= 1.0:
                    num2 = 1.0
                else:
                    env = _pos_stress(umax_p, rot1p, mom1p, rot2p, mom2p, rot3p, mom3p, e1p, e2p, e3p)
                    num2 = env / mom1p / num2 if num2 != 0.0 else 1.0
                if tload == 1:
                    tload = 2
                    if cstress >= 0.0:
                        denom = eup * num2
                        trot_pu = cstrain - cstress / denom if denom != 0.0 else 0.0
                        if _pos_stress(umax_p, rot1p, mom1p, rot2p, mom2p, rot3p, mom3p, e1p, e2p, e3p) == 0.0:
                            trot_pu = 0.0
                        num3 = cenergy - 0.5 * cstress / denom * cstress if denom != 0.0 else cenergy
                        num4 = 0.0
                        if umax_p > rot1p:
                            num4 = damfc2n * num3 / energy_a if energy_a != 0.0 else 0.0
                            num4 += damfc1n * (umax_p - rot1p) / rot1p if rot1p != 0.0 else 0.0
                        trot_min = umax_n * (1.0 + num4)
                tload = 2
                if trot_min > rot1n:
                    trot_min = rot1n
                num5 = _neg_stress(trot_min, mom1n, rot1n, rot2n, mom2n, rot3n, mom3n, e1n, e2n, e3n)
                num6 = _pos_rotlim(umax_p, rot1p, mom1p, rot2p, mom2p, e2p, e3p, rot3p, mom3p, e1p)
                num7 = num6 if num6 < trot_pu else trot_pu
                denom = eun * num
                num8 = trot_min - (1.0 - pinch_yn) * num5 / denom if denom != 0.0 else trot_min
                if num == 0.0:
                    num8 = trot_min
                num9 = num7 + (num8 - num7) * pinch_xn
                if tstrain >= trot_pu:
                    ktang = eup * num2
                    tstress = cstress + ktang * dstrain
                    if tstress <= 0.0:
                        tstress = 0.0
                elif tstrain <= trot_pu and tstrain > num9:
                    if tstrain >= num7:
                        tstress = 0.0
                    else:
                        denom9 = num9 - num7
                        ktang = num5 * pinch_yn / denom9 if denom9 != 0.0 else 0.0
                        num10 = cstress + eun * num * dstrain
                        num11 = (tstrain - num7) * ktang
                        if num10 > num11:
                            tstress = num10
                            ktang = eun * num
                        else:
                            tstress = num11
                else:
                    denom9 = trot_min - num9
                    ktang = (1.0 - pinch_yn) * num5 / denom9 if denom9 != 0.0 else 0.0
                    num10 = cstress + eun * num * dstrain
                    num11 = pinch_yn * num5 + (tstrain - num9) * ktang
                    if num10 > num11:
                        tstress = num10
                        ktang = eun * num
                    else:
                        tstress = num11
                    if cstrain > trot_pu and tstrain < trot_pu:
                        ktang = eup * num2
                        tstress = cstress + ktang * (trot_pu - cstrain)
                        ktang = (1.0 - pinch_yn) * num5 / denom9 if denom9 != 0.0 else 0.0
                        tstress += ktang * (tstrain - trot_pu)
            elif dstrain > 0.0:
                tphase = RELOAD_T if tstress > 0.0 else UNLOAD_C
                num = (umax_n / rot1n) ** betan if rot1n != 0.0 else 0.0
                if num <= 1.0:
                    num = 1.0
                else:
                    env = _neg_stress(umax_n, mom1n, rot1n, rot2n, mom2n, rot3n, mom3n, e1n, e2n, e3n)
                    num = env / mom1n / num if num != 0.0 else 1.0
                num2 = (umax_p / rot1p) ** betap if rot1p != 0.0 else 0.0
                if num2 <= 1.0:
                    num2 = 1.0
                else:
                    env = _pos_stress(umax_p, rot1p, mom1p, rot2p, mom2p, rot3p, mom3p, e1p, e2p, e3p)
                    num2 = env / mom1p / num2 if num2 != 0.0 else 1.0
                if tload == 2:
                    tload = 1
                    if cstress <= 0.0:
                        denom = eun * num
                        trot_nu = cstrain - cstress / denom if denom != 0.0 else 0.0
                        if _neg_stress(umax_n, mom1n, rot1n, rot2n, mom2n, rot3n, mom3n, e1n, e2n, e3n) == 0.0:
                            trot_nu = 0.0
                        num3 = cenergy - 0.5 * cstress / denom * cstress if denom != 0.0 else cenergy
                        num4 = 0.0
                        if umax_n < rot1n:
                            num4 = damfc2p * num3 / energy_a if energy_a != 0.0 else 0.0
                            num4 += damfc1p * (umax_n - rot1n) / rot1n if rot1n != 0.0 else 0.0
                        trot_max = umax_p * (1.0 + num4)
                tload = 1
                if trot_max < rot1p:
                    trot_max = rot1p
                num5 = _pos_stress(trot_max, rot1p, mom1p, rot2p, mom2p, rot3p, mom3p, e1p, e2p, e3p)
                num6 = _neg_rotlim(umax_n, mom1n, rot1n, rot2n, mom2n, e2n, e3n, rot3n, mom3n, e1n)
                num7 = num6 if num6 > trot_nu else trot_nu
                denom = eup * num2
                num8 = trot_max - (1.0 - pinch_yp) * num5 / denom if denom != 0.0 else trot_max
                if num2 == 0.0:
                    num8 = trot_max
                num9 = num7 + (num8 - num7) * pinch_xp
                if tstrain <= trot_nu:
                    ktang = eun * num
                    tstress = cstress + ktang * dstrain
                    if tstress >= 0.0:
                        tstress = 0.0
                elif trot_nu < tstrain < num9:
                    if tstrain <= num7:
                        tstress = 0.0
                    else:
                        denom9 = num9 - num7
                        ktang = num5 * pinch_yp / denom9 if denom9 != 0.0 else 0.0
                        num10 = cstress + eup * num2 * dstrain
                        num11 = (tstrain - num7) * ktang
                        if num10 < num11:
                            tstress = num10
                            ktang = eup * num2
                        else:
                            tstress = num11
                else:
                    denom9 = trot_max - num9
                    ktang = (1.0 - pinch_yp) * num5 / denom9 if denom9 != 0.0 else 0.0
                    num10 = cstress + eup * num2 * dstrain
                    num11 = pinch_yp * num5 + (tstrain - num9) * ktang
                    if num10 < num11:
                        tstress = num10
                        ktang = eup * num2
                    else:
                        tstress = num11
                    if cstrain < trot_nu and tstrain > trot_nu:
                        ktang = eun * num
                        tstress = cstress + ktang * (trot_nu - cstrain)
                        ktang = (1.0 - pinch_yp) * num5 / denom9 if denom9 != 0.0 else 0.0
                        tstress += ktang * (tstrain - trot_nu)

            tenergy = cenergy + 0.5 * (cstress + tstress) * dstrain
            trial[i, 0] = trot_max
            trial[i, 1] = trot_min
            trial[i, 2] = trot_pu
            trial[i, 3] = trot_nu
            trial[i, 4] = tenergy
            trial[i, 5] = tload
            trial[i, 6] = tstress
            trial[i, 7] = tstrain
            trial[i, 8] = tphase
            trial[i, 9] = ktang

    @njit(cache=True, nogil=True)
    def _finish_transverse_batch(
        trial, committed, di, dj, ecc, inv_length,
        starts, stops, constrained, local_forces,
        normal_increments, committed_forces, max_displacements,
    ):
        for record_index in range(starts.size):
            start = starts[record_index]
            stop = stops[record_index]
            for local_dof in range(6):
                local_forces[record_index, local_dof] = 0.0
            normal_increment = 0.0
            committed_force = 0.0
            max_displacement = 0.0
            for spring_index in range(start, stop):
                force = trial[spring_index, 6]
                committed_value = committed[spring_index, 6]
                normal_increment -= force - committed_value
                committed_force += committed_value
                displacement = abs(trial[spring_index, 7])
                if displacement > max_displacement:
                    max_displacement = displacement

                force_di = force * di[spring_index] * inv_length[spring_index]
                force_dj = force * dj[spring_index] * inv_length[spring_index]
                if not constrained[record_index]:
                    local_forces[record_index, 3] += force_dj
                    local_forces[record_index, 2] += force_di
                    local_forces[record_index, 0] -= force_dj
                    local_forces[record_index, 1] -= force_di
                else:
                    local_forces[record_index, 3] += force_dj
                    local_forces[record_index, 2] += force_di
                    local_forces[record_index, 0] -= force_di + force_dj
                    # Length/2 * (force_dj-force_di) equals the original code;
                    # derive length from inv_length to retain one immutable array.
                    local_forces[record_index, 1] += (
                        0.5 / inv_length[spring_index] * (force_dj - force_di)
                    )
                force_ecc = force * ecc[spring_index]
                local_forces[record_index, 4] += force_ecc
                local_forces[record_index, 5] -= force_ecc
            normal_increments[record_index] = normal_increment
            committed_forces[record_index] = committed_force
            max_displacements[record_index] = max_displacement

    @njit(cache=True, nogil=True)
    def _map_global_to_local(x, offsets, gdls, coefficients, out):
        flat = out.reshape(out.size)
        for local_index in range(flat.size):
            total = 0.0
            for pair_index in range(offsets[local_index], offsets[local_index + 1]):
                gdl = gdls[pair_index]
                if 0 <= gdl < x.size:
                    total += x[gdl] * coefficients[pair_index]
            flat[local_index] = total

    @njit(cache=True, nogil=True)
    def _scatter_local_forces(local_forces, offsets, gdls, coefficients, global_force):
        flat = local_forces.reshape(local_forces.size)
        for local_index in range(flat.size):
            force = flat[local_index]
            if force == 0.0:
                continue
            for pair_index in range(offsets[local_index], offsets[local_index + 1]):
                gdl = gdls[pair_index]
                if 0 <= gdl < global_force.size:
                    global_force[gdl] -= force * coefficients[pair_index]
else:
    _evaluate_linear_batch = None
    _finish_transverse_batch = None
    _map_global_to_local = None
    _scatter_local_forces = None


_PARAM_NAMES = (
    "pinch_xp", "pinch_yp", "pinch_xn", "pinch_yn",
    "damfc1p", "damfc2p", "damfc1n", "damfc2n", "betap", "betan",
    "rot1p", "mom1p", "rot2p", "mom2p", "rot3p", "mom3p",
    "mom1n", "rot1n", "rot2n", "mom2n", "rot3n", "mom3n",
    "e1n", "e1p", "e2n", "e2p", "e3n", "e3p", "eun", "eup",
    "energy_a", "k",
)


@dataclass(frozen=True)
class _InterfaceSlice:
    interface: Any
    start: int
    stop: int


class HystereticBatchRuntime:
    """Dense committed/trial state for compatible transverse springs."""

    def __init__(self, model: Any) -> None:
        if _evaluate_linear_batch is None:
            raise RuntimeError("Numba is unavailable")
        self.model = model
        self.records: list[_InterfaceSlice] = []
        springs: list[SpringHysteretic] = []
        for interface in model.collections.interfaces.values():
            group = list(interface.trasv_1)
            if not group:
                continue
            if not all(
                isinstance(spring, SpringHysteretic)
                and spring.tensile_curve_type in {"LinearHardening", "LinearSoftening"}
                and spring.compressive_curve_type in {"LinearHardening", "LinearSoftening"}
                for spring in group
            ):
                continue
            start = len(springs)
            springs.extend(group)
            stop = len(springs)
            self.records.append(_InterfaceSlice(interface, start, stop))
            interface._perf_hysteretic_batch = self
            interface._perf_hysteretic_slice = (start, stop)
            for spring in group:
                spring._histra_batch_managed = True

        self.springs = springs
        self.interface_ids = frozenset(id(record.interface) for record in self.records)
        n = len(springs)
        self.params = np.empty((n, len(_PARAM_NAMES)), dtype=np.float64)
        self.committed = np.empty((n, 9), dtype=np.float64)
        self.trial = np.empty((n, 10), dtype=np.float64)
        self.targets = np.empty(n, dtype=np.float64)
        self.enabled = np.empty(n, dtype=np.bool_)
        for i, spring in enumerate(springs):
            self.params[i, :] = [float(getattr(spring, name)) for name in _PARAM_NAMES]
            self.committed[i, :] = (
                spring.umax[0], spring.umax[1], spring._crot_pu, spring._crot_nu,
                spring.cenergy_d, spring._cload_indicator, spring._cstress,
                spring._cstrain, int(spring.phase),
            )
            self.trial[i, :] = (
                spring._trot_max, spring._trot_min, spring._trot_pu,
                spring._trot_nu, spring._tenergy_d, spring._tload_indicator,
                spring._tstress, spring._tstrain, int(spring.t_phase),
                spring.k_tang,
            )
            self.targets[i] = spring._tstrain
            self.enabled[i] = bool(spring.is_on)
        self._pending: dict[int, tuple[float, float, float]] = {}
        self._record_index = np.empty(n, dtype=np.int32)
        self._di = np.empty(n, dtype=np.float64)
        self._dj = np.empty(n, dtype=np.float64)
        self._ecc = np.empty(n, dtype=np.float64)
        self._inv_length = np.empty(n, dtype=np.float64)
        for record_index, record in enumerate(self.records):
            interface = record.interface
            interface._ensure_performance_cache()
            assert interface._perf_di is not None
            assert interface._perf_dj is not None
            assert interface._perf_ecc is not None
            sl = slice(record.start, record.stop)
            self._record_index[sl] = record_index
            self._di[sl] = interface._perf_di
            self._dj[sl] = interface._perf_dj
            self._ecc[sl] = interface._perf_ecc
            self._inv_length[sl] = 1.0 / interface.length
        self._num = np.empty(len(self.records), dtype=np.float64)
        self._num2 = np.empty(len(self.records), dtype=np.float64)
        self._delta_flex = np.empty(len(self.records), dtype=np.float64)
        self._starts = np.asarray([record.start for record in self.records], dtype=np.int32)
        self._stops = np.asarray([record.stop for record in self.records], dtype=np.int32)
        self._constrained = np.asarray(
            [record.interface.interfaccia_vincolata_computed() for record in self.records],
            dtype=np.bool_,
        )
        self._local_forces = np.zeros((len(self.records), 6), dtype=np.float64)
        self._normal_increments = np.zeros(len(self.records), dtype=np.float64)
        self._committed_forces = np.zeros(len(self.records), dtype=np.float64)
        self._max_displacements = np.zeros(len(self.records), dtype=np.float64)
        self._record_by_id = {
            id(record.interface): index for index, record in enumerate(self.records)
        }
        offsets = [0]
        gdls: list[int] = []
        coefficients: list[float] = []
        for record in self.records:
            interface = record.interface
            assert interface._perf_aff_pairs is not None
            for local_dof in range(12):
                pairs = (
                    interface._perf_aff_pairs[local_dof]
                    if local_dof < len(interface._perf_aff_pairs)
                    else ()
                )
                for gdl, coefficient in pairs:
                    gdls.append(int(gdl))
                    coefficients.append(float(coefficient))
                offsets.append(len(gdls))
        self._aff_offsets = np.asarray(offsets, dtype=np.int32)
        self._aff_gdls = np.asarray(gdls, dtype=np.int32)
        self._aff_coefficients = np.asarray(coefficients, dtype=np.float64)
        self._local_du = np.zeros((len(self.records), 12), dtype=np.float64)
        self._local_full_forces = np.zeros((len(self.records), 12), dtype=np.float64)
        self._refresh_transverse_cache()
        self._refresh_full_force_cache()
        self._objects_trial_synced = True

    @property
    def active(self) -> bool:
        return bool(self.springs)

    def prepare(self, x: np.ndarray) -> None:
        """Map one global Newton increment to all batched spring strains."""
        self._pending.clear()
        _map_global_to_local(
            x, self._aff_offsets, self._aff_gdls, self._aff_coefficients,
            self._local_du,
        )
        for record_index, record in enumerate(self.records):
            interface = record.interface
            local_du = self._local_du[record_index]
            for i, value in enumerate(local_du):
                interface.status.u[i] += float(value)

            if not interface.interfaccia_vincolata_computed():
                num = local_du[3] - local_du[0]
                num2 = local_du[2] - local_du[1]
            else:
                half_length = interface.length / 2.0
                num = local_du[3] - (local_du[0] - local_du[1] * half_length)
                num2 = local_du[2] - (local_du[0] + local_du[1] * half_length)
            self._num[record_index] = num
            self._num2[record_index] = num2
            self._delta_flex[record_index] = local_du[5] - local_du[4]

            d0 = interface.dim_aff[0] if interface.dim_aff else 6
            d1 = interface.dim_aff[1] if len(interface.dim_aff) > 1 else 2
            self._pending[id(interface)] = (
                local_du[d0] - local_du[d0 + 1],
                local_du[d0 + d1] - local_du[d0 + d1 + 2],
                local_du[d0 + d1 + 1] - local_du[d0 + d1 + 3],
            )

        indices = self._record_index
        self.targets[:] = self.trial[:, 7] + (
            (self._num[indices] * self._dj + self._num2[indices] * self._di)
            * self._inv_length
            - self._delta_flex[indices] * self._ecc
        )

    def evaluate(self) -> None:
        _evaluate_linear_batch(
            self.params, self.committed, self.trial, self.targets, self.enabled
        )
        self._objects_trial_synced = False

    def _refresh_transverse_cache(self) -> None:
        _finish_transverse_batch(
            self.trial, self.committed, self._di, self._dj, self._ecc,
            self._inv_length, self._starts, self._stops, self._constrained,
            self._local_forces, self._normal_increments,
            self._committed_forces, self._max_displacements,
        )

    def finish(self) -> None:
        from histra.springs.coulomb03 import SpringCoulomb03

        self._refresh_transverse_cache()
        for record_index, record in enumerate(self.records):
            interface = record.interface
            normal_increment = float(self._normal_increments[record_index])
            interface.status.normal_increment = normal_increment
            interface.status.committed_normal_force = float(
                self._committed_forces[record_index]
            )
            max_displacement = float(self._max_displacements[record_index])

            du_slid, du_op_a, du_op_b = self._pending[id(interface)]
            if interface.slid:
                spring = interface.slid[0]
                spring.u += float(du_slid)
                if isinstance(spring, SpringCoulomb03):
                    spring.dn = normal_increment
                    if spring.check_contact_area:
                        spring.area_corrente = interface.compute_area_corr()
                spring.set_trial_strain(spring.u)
                max_displacement = max(max_displacement, abs(float(spring.u)))

            assert interface._perf_dist_for is not None
            di_sop, dj_sop = interface._perf_dist_for
            if len(interface.slid_out_plan) >= 2:
                spring0, spring1 = interface.slid_out_plan[0], interface.slid_out_plan[1]
                spring0.u += float(du_op_a + (du_op_b - du_op_a) * di_sop)
                spring1.u += float(du_op_a + (du_op_b - du_op_a) * dj_sop)
                if isinstance(spring0, SpringCoulomb03):
                    dn = 0.5 * normal_increment
                    spring0.dn = dn
                    spring1.dn = dn
                    if spring0.check_contact_area:
                        area = 0.5 * interface.compute_area_corr()
                        spring0.area_corrente = area
                        spring1.area_corrente = area
                spring0.set_trial_strain(spring0.u)
                spring1.set_trial_strain(spring1.u)
                max_displacement = max(
                    max_displacement, abs(float(spring0.u)), abs(float(spring1.u))
                )
            interface.status.max_spring_displacement = max_displacement
        self._refresh_full_force_cache()

    def _refresh_full_force_cache(self) -> None:
        self._local_full_forces.fill(0.0)
        self._local_full_forces[:, :6] = self._local_forces
        for record_index, record in enumerate(self.records):
            interface = record.interface
            arr = self._local_full_forces[record_index]
            if interface.slid:
                spring = interface.slid[0]
                force = float(spring._tstress) if hasattr(spring, "_tstress") else float(spring.get_force())
                arr[6] += force
                arr[7] -= force
            if len(interface.slid_out_plan) >= 2:
                assert interface._perf_dist is not None
                di, dj = interface._perf_dist
                spring0, spring1 = interface.slid_out_plan[0], interface.slid_out_plan[1]
                force0 = float(spring0._tstress) if hasattr(spring0, "_tstress") else float(spring0.get_force())
                force1 = float(spring1._tstress) if hasattr(spring1, "_tstress") else float(spring1.get_force())
                first = dj * force0 + di * force1
                second = di * force0 + dj * force1
                arr[8] += first
                arr[9] += second
                arr[10] -= first
                arr[11] -= second

    def scatter_resisting_force(self, global_force: np.ndarray) -> None:
        _scatter_local_forces(
            self._local_full_forces, self._aff_offsets, self._aff_gdls,
            self._aff_coefficients, global_force,
        )

    def manages(self, interface: Any) -> bool:
        return id(interface) in self.interface_ids

    def sync_interface_trial_to_objects(self, interface: Any) -> None:
        start, stop = interface._perf_hysteretic_slice
        for local_i, spring in enumerate(self.springs[start:stop], start):
            row = self.trial[local_i]
            spring._trot_max = float(row[0])
            spring._trot_min = float(row[1])
            spring._trot_pu = float(row[2])
            spring._trot_nu = float(row[3])
            spring._tenergy_d = float(row[4])
            spring._tload_indicator = int(row[5])
            spring._tstress = float(row[6])
            spring._tstrain = float(row[7])
            spring.t_phase = PhaseEnum(int(row[8]))
            spring.k_tang = float(row[9])
            spring.f = spring._tstress
            spring.u = spring._tstrain

    def local_force_for(self, interface: Any) -> np.ndarray:
        return self._local_full_forces[self._record_by_id[id(interface)]]

    def transverse_force_for(self, interface: Any) -> np.ndarray:
        return self._local_forces[self._record_by_id[id(interface)]]

    def trial_stresses_for(self, interface: Any) -> np.ndarray:
        start, stop = interface._perf_hysteretic_slice
        return self.trial[start:stop, 6]

    def sync_trial_to_objects(self) -> None:
        if self._objects_trial_synced:
            return
        for record in self.records:
            self.sync_interface_trial_to_objects(record.interface)
        self._objects_trial_synced = True

    def commit(self) -> None:
        self.committed[:, 0] = self.trial[:, 0]
        self.committed[:, 1] = self.trial[:, 1]
        self.committed[:, 2] = self.trial[:, 2]
        self.committed[:, 3] = self.trial[:, 3]
        self.committed[:, 4] = self.trial[:, 4]
        self.committed[:, 5] = self.trial[:, 5]
        self.committed[:, 6] = self.trial[:, 6]
        self.committed[:, 7] = self.trial[:, 7]
        self.committed[:, 8] = self.trial[:, 8]
        self.sync_trial_to_objects()
        for i, spring in enumerate(self.springs):
            row = self.committed[i]
            spring.umax[0] = float(row[0])
            spring.umax[1] = float(row[1])
            spring._crot_pu = float(row[2])
            spring._crot_nu = float(row[3])
            spring.cenergy_d = float(row[4])
            spring._cload_indicator = int(row[5])
            spring._cstress = float(row[6])
            spring._cstrain = float(row[7])
            spring.phase = PhaseEnum(int(row[8]))
            spring.k_tang_committed = spring.k_tang

    def snapshot(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        return self.committed.copy(), self.trial.copy(), self.targets.copy()

    def restore(self, state: tuple[np.ndarray, np.ndarray, np.ndarray]) -> None:
        committed, trial, targets = state
        self.committed[...] = committed
        self.trial[...] = trial
        self.targets[...] = targets
        self._pending.clear()
        self._refresh_transverse_cache()
        self._objects_trial_synced = False
        self.sync_trial_to_objects()
        self._refresh_full_force_cache()

    def revert_interface(self, interface: Any) -> None:
        start, stop = interface._perf_hysteretic_slice
        self.trial[start:stop, 0] = self.committed[start:stop, 0]
        self.trial[start:stop, 1] = self.committed[start:stop, 1]
        self.trial[start:stop, 2] = self.committed[start:stop, 2]
        self.trial[start:stop, 3] = self.committed[start:stop, 3]
        self.trial[start:stop, 4] = self.committed[start:stop, 4]
        self.trial[start:stop, 5] = self.committed[start:stop, 5]
        self.trial[start:stop, 6] = self.committed[start:stop, 6]
        self.trial[start:stop, 7] = self.committed[start:stop, 7]
        self.trial[start:stop, 8] = self.committed[start:stop, 8]
        self.targets[start:stop] = self.committed[start:stop, 7]
        self.sync_interface_trial_to_objects(interface)
        self._objects_trial_synced = False


def build_hysteretic_batch(model: Any) -> HystereticBatchRuntime | None:
    """Return an active batch runtime, or ``None`` for a safe Python fallback."""
    disabled = os.environ.get("HISTRA_DISABLE_COMPILED_SPRINGS", "").strip().lower()
    if disabled in {"1", "true", "yes", "on"}:
        return None
    if _evaluate_linear_batch is None:
        return None
    runtime = HystereticBatchRuntime(model)
    return runtime if runtime.active else None
