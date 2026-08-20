"""Optional Numba batch runtime for interface SpringHysteretic objects.

The nonlinear benchmark updates thousands of independent transverse springs on
nearly every Newton correction.  Calling the Python state machine spring by
spring dominates runtime.  This module keeps the same committed/trial variables
in dense arrays and evaluates the supported linear and exponential-tension
hysteretic laws in one compiled loop. Unsupported curves transparently remain
on the Python path.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from operator import attrgetter
import os
from typing import Any

import numpy as np

from histra.model.shear_law import (
    ELASTO_PLASTIC_ENERGY_SIGMA_INTERPOLATION,
    ELASTO_PLASTIC_FRACTURE_ENERGY_FIXED,
    fracture_energy_shear,
    masonry_shear_law_code,
)
from histra.springs.hysteretic import SpringHysteretic
from histra.types.phase_enum import PhaseEnum

try:  # optional acceleration dependency
    from numba import njit, prange
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

# Positive-envelope dispatch stored in the final dense parameter column.
# Existing numeric parameter indices remain unchanged.
TENSILE_LINEAR = 0
TENSILE_EXPONENTIAL = 1
TENSILE_CURVE_TYPE_PARAM = 32
TRANSVERSE_PARAM_SIZE = 33

# Dense state columns for interface SpringCoulomb03 objects using the C#
# ``Initial`` law.  Keeping the state in one contiguous array avoids hundreds
# of thousands of Python attribute reads/writes per Newton correction.
CFY0 = 0
CFY1 = 1
CCUP = 2
CCSTRESS = 3
CCSTRAIN = 4
CCSTRESS_NORMAL = 5
CCSTRESS_NORMAL_PREV = 6
CCCONTACT_AREA = 7
CCENERGY = 8
CCPHASE = 9
CTUP = 10
CTSTRESS = 11
CTSTRAIN = 12
CTSTRESS_NORMAL = 13
CTCONTACT_AREA = 14
CTENERGY = 15
CTPHASE = 16
CKTANG = 17
CMOM1P = 18
CROT1P = 19
CMOM2P = 20
CROT2P = 21
CMOM1N = 22
CROT1N = 23
CMOM2N = 24
CROT2N = 25
CROT3N = 26
CROT3P = 27
CU = 28
CF = 29
CKTANG_COMMITTED = 30
CDN = 31
COULOMB_STATE_SIZE = 32

# Dense state for Quad diagonal SpringCoulomb03 (Takeda, Coulomb law, no
# fracture-energy material callback).  The layout deliberately contains both
# committed and trial values because rejected Newton/ArcLength trials must be
# reversible without touching thousands of Python attributes.
QFY0, QFY1 = 0, 1
QUMAX0, QUMAX1 = 2, 3
QCROT_PU, QCROT_NU, QCROT_LIM_PU, QCROT_LIM_NU = 4, 5, 6, 7
QCROT_YP, QCROT_YN, QCMOM_MAX, QCMOM_MIN = 8, 9, 10, 11
QCLOAD, QCPLAST_T, QCPLAST_C, QCUNLOAD_T, QCUNLOAD_C = 12, 13, 14, 15, 16
QCUP, QCENERGY, QCSTRESS, QCSTRAIN = 17, 18, 19, 20
QCSTRESS_NORMAL, QCSTRESS_NORMAL_PREV, QCCONTACT = 21, 22, 23
QPHASE, QTANG_RELOAD_T, QTANG_RELOAD_C, QKTANG_COMMITTED = 24, 25, 26, 27
QTROT_MAX, QTROT_MIN, QTROT_PU, QTROT_NU = 28, 29, 30, 31
QTROT_LIM_PU, QTROT_LIM_NU, QTROT_YP, QTROT_YN = 32, 33, 34, 35
QTMOM_MAX, QTMOM_MIN, QTLOAD = 36, 37, 38
QTPLAST_T, QTPLAST_C, QTUNLOAD_T, QTUNLOAD_C = 39, 40, 41, 42
QTENERGY, QTUP, QTSTRESS, QTSTRAIN = 43, 44, 45, 46
QTSTRESS_NORMAL, QTCONTACT, QTPHASE, QKTANG = 47, 48, 49, 50
QMOM1P, QROT1P, QMOM2P, QROT2P, QMOM3P, QROT3P = 51, 52, 53, 54, 55, 56
QMOM1N, QROT1N, QMOM2N, QROT2N, QMOM3N, QROT3N = 57, 58, 59, 60, 61, 62
QUR0, QUR1, QDN = 63, 64, 65
QUAD_STATE_SIZE = 66

QPCOHESION, QPMU = 0, 1
QPE1P, QPE2P, QPE3P = 2, 3, 4
QPE1N, QPE2N, QPE3N = 5, 6, 7
QPEUP, QPEUN, QPPLASTIC_STRAIN, QPENABLED = 8, 9, 10, 11
QPK = 12
QPSUBLAW = 13
QPBCACOVIC = 14
QPFRACTURE_MODE = 15
QPFRACTURE_ENERGY = 16
QUAD_PARAM_SIZE = 17

# ``PhaseEnum(code)`` goes through EnumMeta on every call.  Dense batch rows
# contain only the canonical C# phase codes 0..10, so reuse the singleton
# IntEnum objects.  The fallback retains the former ValueError semantics if a
# corrupted/out-of-range state ever reaches the object synchronization path.
_PHASE_BY_CODE = tuple(PhaseEnum(code) for code in range(11))


def _phase_from_code(value: float | int) -> PhaseEnum:
    code = int(value)
    if 0 <= code < len(_PHASE_BY_CODE):
        return _PHASE_BY_CODE[code]
    return PhaseEnum(code)


QUAD_SUBLAW_COULOMB = 0
QUAD_SUBLAW_CACOVIC = 1
QUAD_FRACTURE_NONE = 0
QUAD_FRACTURE_FIXED = ELASTO_PLASTIC_FRACTURE_ENERGY_FIXED
QUAD_FRACTURE_INTERPOLATED = ELASTO_PLASTIC_ENERGY_SIGMA_INTERPOLATION


if njit is not None:
    @njit(cache=True, inline="always")
    def _quad_tau_limit(par, normal_stress):
        cohesion = par[QPCOHESION]
        if int(par[QPSUBLAW]) == QUAD_SUBLAW_CACOVIC:
            value = 1.0 + normal_stress / (1.5 * cohesion)
            if value < 0.0:
                return 0.0
            return 1.5 / par[QPBCACOVIC] * cohesion * np.sqrt(value)
        value = cohesion + par[QPMU] * normal_stress
        return value if value > 0.0 else 0.0

    @njit(cache=True, inline="always")
    def _quad_interpolated_shear_energy(sigma):
        # C# MasonryMaterial.GetShearUltimateStrain interpolates at -sigma.
        x = -sigma
        if x <= 0.05:
            return 0.0012385
        if x >= 0.07:
            return 0.0001699
        if x <= 0.055:
            return 0.0012385 + (0.0007775 - 0.0012385) * (x - 0.05) / 0.005
        if x <= 0.06:
            return 0.0007775 + (0.0004402 - 0.0007775) * (x - 0.055) / 0.005
        return 0.0004402 + (0.0001699 - 0.0004402) * (x - 0.06) / 0.01

    @njit(cache=True, inline="always")
    def _quad_shear_ultimate_strain(par, f_limit, yield_strain, volume, sigma):
        mode = int(par[QPFRACTURE_MODE])
        if mode == QUAD_FRACTURE_INTERPOLATED:
            energy = _quad_interpolated_shear_energy(sigma)
        else:
            energy = par[QPFRACTURE_ENERGY]
        if f_limit == 0.0:
            numerator = energy * volume
            if numerator == 0.0:
                return np.nan
            return np.inf if numerator > 0.0 else -np.inf
        return energy * volume / f_limit + 0.5 * yield_strain

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
    def _pos_stress_typed(
        curve_type, strain, rot1p, mom1p, rot2p, mom2p, rot3p, mom3p,
        e1p, e2p, e3p,
    ):
        if curve_type == TENSILE_EXPONENTIAL:
            if strain <= 0.0:
                return 0.0
            if strain <= rot1p:
                return e1p * strain
            denominator = rot2p - rot1p
            # C# floating-point evaluation tends to zero for the degenerate
            # positive-increment case; avoid a Numba ZeroDivisionError.
            if denominator == 0.0:
                return 0.0
            return mom1p * np.exp(-(strain - rot1p) / denominator)
        return _pos_stress(
            strain, rot1p, mom1p, rot2p, mom2p, rot3p, mom3p,
            e1p, e2p, e3p,
        )

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
    def _pos_tangent_typed(
        curve_type, strain, rot1p, rot2p, rot3p, e1p, e2p, e3p,
        tstress, cstress, cstrain,
    ):
        if curve_type == TENSILE_EXPONENTIAL:
            if strain < 0.0:
                return e1p * 1.0e-9, ELASTIC
            if strain <= rot1p:
                return e1p, ELASTIC
            dstrain = strain - cstrain
            if dstrain != 0.0:
                return (tstress - cstress) / dstrain, PLASTIC_T
            # The scalar Python implementation protects this otherwise
            # undefined repeated-trial case while retaining Plastic_t phase.
            return e1p, PLASTIC_T
        return _pos_tangent(strain, rot1p, rot2p, rot3p, e1p, e2p, e3p)

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
    def _pos_rotlim_typed(
        curve_type, strain, rot1p, mom1p, rot2p, mom2p, e2p, e3p,
        rot3p, mom3p, e1p,
    ):
        result = np.inf
        if strain <= rot1p:
            return result
        if strain <= rot2p and e2p < 0.0 and e2p != 0.0:
            result = rot1p - mom1p / e2p
        if strain > rot2p and e3p < 0.0 and e3p != 0.0:
            result = rot2p - mom2p / e3p
        if np.isinf(result):
            return result
        if _pos_stress_typed(
            curve_type, result, rot1p, mom1p, rot2p, mom2p, rot3p,
            mom3p, e1p, e2p, e3p,
        ) > 0.0:
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

    @njit(cache=True, nogil=True, parallel=True)
    def _evaluate_linear_batch(params, committed, trial, targets, enabled):
        n = targets.size
        for i in prange(n):
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
            tensile_curve_type = TENSILE_LINEAR
            if params.shape[1] > TENSILE_CURVE_TYPE_PARAM:
                tensile_curve_type = int(params[i, TENSILE_CURVE_TYPE_PARAM])

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
                tstress = _pos_stress_typed(
                    tensile_curve_type, tstrain, rot1p, mom1p, rot2p, mom2p,
                    rot3p, mom3p, e1p, e2p, e3p,
                )
                ktang, tphase = _pos_tangent_typed(
                    tensile_curve_type, tstrain, rot1p, rot2p, rot3p,
                    e1p, e2p, e3p, tstress, cstress, cstrain,
                )
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
                    env = _pos_stress_typed(
                        tensile_curve_type, umax_p, rot1p, mom1p, rot2p,
                        mom2p, rot3p, mom3p, e1p, e2p, e3p,
                    )
                    num2 = env / mom1p / num2 if num2 != 0.0 else 1.0
                if tload == 1:
                    tload = 2
                    if cstress >= 0.0:
                        denom = eup * num2
                        trot_pu = cstrain - cstress / denom if denom != 0.0 else 0.0
                        if _pos_stress_typed(
                            tensile_curve_type, umax_p, rot1p, mom1p, rot2p,
                            mom2p, rot3p, mom3p, e1p, e2p, e3p,
                        ) == 0.0:
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
                num6 = _pos_rotlim_typed(
                    tensile_curve_type, umax_p, rot1p, mom1p, rot2p, mom2p,
                    e2p, e3p, rot3p, mom3p, e1p,
                )
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
                    env = _pos_stress_typed(
                        tensile_curve_type, umax_p, rot1p, mom1p, rot2p,
                        mom2p, rot3p, mom3p, e1p, e2p, e3p,
                    )
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
                num5 = _pos_stress_typed(
                    tensile_curve_type, trot_max, rot1p, mom1p, rot2p, mom2p,
                    rot3p, mom3p, e1p, e2p, e3p,
                )
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

    @njit(cache=True, nogil=True, parallel=True)
    def _evaluate_simple_linear_batch(params, committed, trial, targets, enabled):
        """Specialized C# Hysteretic path for generated masonry fibers.

        PrepareModel creates these springs with zero pinching/damage,
        BetaP=1 and BetaN=0.  Algebraically removing the inactive pinching and
        damage branches avoids hundreds of millions of redundant operations
        while retaining the same state-transition ordering and envelope calls.
        """
        # Runtime-built simple batches may use the compact 21-column layout;
        # direct/unit callers can still pass the historical 33-column layout.
        # Only the storage indices differ.  The constitutive arithmetic below
        # is intentionally unchanged.
        compact = params.shape[1] == SIMPLE_TRANSVERSE_PARAM_SIZE
        parameter_offset = 0 if compact else 10
        tensile_curve_column = (
            SIMPLE_TENSILE_CURVE_TYPE_PARAM
            if compact else TENSILE_CURVE_TYPE_PARAM
        )

        for i in prange(targets.size):
            if not enabled[i]:
                continue
            previous_tload = int(trial[i, 5])
            strain = targets[i]
            if previous_tload == 0 and strain == 0.0:
                continue

            rot1p, mom1p, rot2p, mom2p = (
                params[i, parameter_offset],
                params[i, parameter_offset + 1],
                params[i, parameter_offset + 2],
                params[i, parameter_offset + 3],
            )
            rot3p, mom3p = (
                params[i, parameter_offset + 4],
                params[i, parameter_offset + 5],
            )
            mom1n, rot1n, rot2n, mom2n = (
                params[i, parameter_offset + 6],
                params[i, parameter_offset + 7],
                params[i, parameter_offset + 8],
                params[i, parameter_offset + 9],
            )
            rot3n, mom3n = (
                params[i, parameter_offset + 10],
                params[i, parameter_offset + 11],
            )
            e1n, e1p, e2n, e2p = (
                params[i, parameter_offset + 12],
                params[i, parameter_offset + 13],
                params[i, parameter_offset + 14],
                params[i, parameter_offset + 15],
            )
            e3n, e3p, eun, eup = (
                params[i, parameter_offset + 16],
                params[i, parameter_offset + 17],
                params[i, parameter_offset + 18],
                params[i, parameter_offset + 19],
            )
            tensile_curve_type = TENSILE_LINEAR
            if params.shape[1] > tensile_curve_column:
                tensile_curve_type = int(params[i, tensile_curve_column])

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
                tstress = _pos_stress_typed(
                    tensile_curve_type, tstrain, rot1p, mom1p, rot2p,
                    mom2p, rot3p, mom3p, e1p, e2p, e3p,
                )
                ktang, tphase = _pos_tangent_typed(
                    tensile_curve_type, tstrain, rot1p, rot2p, rot3p,
                    e1p, e2p, e3p, tstress, cstress, cstrain,
                )
                tload = 1
            elif tstrain <= umax_n:
                trot_min = tstrain
                tstress = _neg_stress(
                    tstrain, mom1n, rot1n, rot2n, mom2n, rot3n, mom3n,
                    e1n, e2n, e3n,
                )
                ktang, tphase = _neg_tangent(
                    tstrain, rot1n, rot2n, rot3n, e1n, e2n, e3n,
                )
                tload = 2
            elif dstrain < 0.0:
                tphase = UNLOAD_T if tstress > 0.0 else RELOAD_C
                num = 1.0
                num2 = (umax_p / rot1p) ** 1.0 if rot1p != 0.0 else 0.0
                if num2 <= 1.0:
                    num2 = 1.0
                else:
                    env = _pos_stress_typed(
                        tensile_curve_type, umax_p, rot1p, mom1p, rot2p,
                        mom2p, rot3p, mom3p, e1p, e2p, e3p,
                    )
                    num2 = env / mom1p / num2 if num2 != 0.0 else 1.0
                if tload == 1:
                    tload = 2
                    if cstress >= 0.0:
                        denom = eup * num2
                        trot_pu = cstrain - cstress / denom if denom != 0.0 else 0.0
                        if _pos_stress_typed(
                            tensile_curve_type, umax_p, rot1p, mom1p, rot2p,
                            mom2p, rot3p, mom3p, e1p, e2p, e3p,
                        ) == 0.0:
                            trot_pu = 0.0
                        trot_min = umax_n
                tload = 2
                if trot_min > rot1n:
                    trot_min = rot1n
                num5 = _neg_stress(
                    trot_min, mom1n, rot1n, rot2n, mom2n, rot3n, mom3n,
                    e1n, e2n, e3n,
                )
                num6 = _pos_rotlim_typed(
                    tensile_curve_type, umax_p, rot1p, mom1p, rot2p, mom2p,
                    e2p, e3p, rot3p, mom3p, e1p,
                )
                num7 = num6 if num6 < trot_pu else trot_pu
                if tstrain >= trot_pu:
                    ktang = eup * num2
                    tstress = cstress + ktang * dstrain
                    if tstress <= 0.0:
                        tstress = 0.0
                elif tstrain > num7:
                    tstress = 0.0
                else:
                    denom9 = trot_min - num7
                    ktang = num5 / denom9 if denom9 != 0.0 else 0.0
                    num10 = cstress + eun * num * dstrain
                    num11 = (tstrain - num7) * ktang
                    if num10 > num11:
                        tstress = num10
                        ktang = eun * num
                    else:
                        tstress = num11
                    if cstrain > trot_pu and tstrain < trot_pu:
                        ktang = eup * num2
                        tstress = cstress + ktang * (trot_pu - cstrain)
                        ktang = num5 / denom9 if denom9 != 0.0 else 0.0
                        tstress += ktang * (tstrain - trot_pu)
            elif dstrain > 0.0:
                tphase = RELOAD_T if tstress > 0.0 else UNLOAD_C
                num = 1.0
                num2 = (umax_p / rot1p) ** 1.0 if rot1p != 0.0 else 0.0
                if num2 <= 1.0:
                    num2 = 1.0
                else:
                    env = _pos_stress_typed(
                        tensile_curve_type, umax_p, rot1p, mom1p, rot2p,
                        mom2p, rot3p, mom3p, e1p, e2p, e3p,
                    )
                    num2 = env / mom1p / num2 if num2 != 0.0 else 1.0
                if tload == 2:
                    tload = 1
                    if cstress <= 0.0:
                        denom = eun * num
                        trot_nu = cstrain - cstress / denom if denom != 0.0 else 0.0
                        if _neg_stress(
                            umax_n, mom1n, rot1n, rot2n, mom2n,
                            rot3n, mom3n, e1n, e2n, e3n,
                        ) == 0.0:
                            trot_nu = 0.0
                        trot_max = umax_p
                tload = 1
                if trot_max < rot1p:
                    trot_max = rot1p
                num5 = _pos_stress_typed(
                    tensile_curve_type, trot_max, rot1p, mom1p, rot2p,
                    mom2p, rot3p, mom3p, e1p, e2p, e3p,
                )
                num6 = _neg_rotlim(
                    umax_n, mom1n, rot1n, rot2n, mom2n, e2n, e3n,
                    rot3n, mom3n, e1n,
                )
                num7 = num6 if num6 > trot_nu else trot_nu
                if tstrain <= trot_nu:
                    ktang = eun * num
                    tstress = cstress + ktang * dstrain
                    if tstress >= 0.0:
                        tstress = 0.0
                elif tstrain < num7:
                    tstress = 0.0
                else:
                    denom9 = trot_max - num7
                    ktang = num5 / denom9 if denom9 != 0.0 else 0.0
                    num10 = cstress + eup * num2 * dstrain
                    num11 = (tstrain - num7) * ktang
                    if num10 < num11:
                        tstress = num10
                        ktang = eup * num2
                    else:
                        tstress = num11
                    if cstrain < trot_nu and tstrain > trot_nu:
                        ktang = eun * num
                        tstress = cstress + ktang * (trot_nu - cstrain)
                        ktang = num5 / denom9 if denom9 != 0.0 else 0.0
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

    @njit(cache=True, nogil=True, parallel=True)
    def _advance_and_evaluate_simple_linear_batch(
        params, committed, trial, targets, enabled,
        record_index, kin_num, kin_num2, di, dj, lengths, delta_flex, ecc,
    ):
        """Advance transverse target strain and evaluate the simple law in one pass.

        The target expression and constitutive arithmetic are intentionally the
        same as the separate production kernels. ``targets`` is still populated
        so snapshots/diagnostics retain the historical dense state.
        """
        # Runtime-built simple batches may use the compact 21-column layout;
        # direct/unit callers can still pass the historical 33-column layout.
        # Only the storage indices differ.  The constitutive arithmetic below
        # is intentionally unchanged.
        compact = params.shape[1] == SIMPLE_TRANSVERSE_PARAM_SIZE
        parameter_offset = 0 if compact else 10
        tensile_curve_column = (
            SIMPLE_TENSILE_CURVE_TYPE_PARAM
            if compact else TENSILE_CURVE_TYPE_PARAM
        )

        for i in prange(targets.size):
            # Target kinematics are advanced for every managed fibre.  The
            # historical two-kernel path only applies ``enabled`` to the
            # constitutive evaluation, so keep that ordering exactly.
            ri = record_index[i]
            strain = trial[i, 7] + (
                (kin_num[ri] * dj[i] + kin_num2[ri] * di[i]) / lengths[ri]
                - delta_flex[ri] * ecc[i]
            )
            targets[i] = strain
            if not enabled[i]:
                continue
            previous_tload = int(trial[i, 5])
            if previous_tload == 0 and strain == 0.0:
                continue

            rot1p, mom1p, rot2p, mom2p = (
                params[i, parameter_offset],
                params[i, parameter_offset + 1],
                params[i, parameter_offset + 2],
                params[i, parameter_offset + 3],
            )
            rot3p, mom3p = (
                params[i, parameter_offset + 4],
                params[i, parameter_offset + 5],
            )
            mom1n, rot1n, rot2n, mom2n = (
                params[i, parameter_offset + 6],
                params[i, parameter_offset + 7],
                params[i, parameter_offset + 8],
                params[i, parameter_offset + 9],
            )
            rot3n, mom3n = (
                params[i, parameter_offset + 10],
                params[i, parameter_offset + 11],
            )
            e1n, e1p, e2n, e2p = (
                params[i, parameter_offset + 12],
                params[i, parameter_offset + 13],
                params[i, parameter_offset + 14],
                params[i, parameter_offset + 15],
            )
            e3n, e3p, eun, eup = (
                params[i, parameter_offset + 16],
                params[i, parameter_offset + 17],
                params[i, parameter_offset + 18],
                params[i, parameter_offset + 19],
            )
            tensile_curve_type = TENSILE_LINEAR
            if params.shape[1] > tensile_curve_column:
                tensile_curve_type = int(params[i, tensile_curve_column])

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
                tstress = _pos_stress_typed(
                    tensile_curve_type, tstrain, rot1p, mom1p, rot2p,
                    mom2p, rot3p, mom3p, e1p, e2p, e3p,
                )
                ktang, tphase = _pos_tangent_typed(
                    tensile_curve_type, tstrain, rot1p, rot2p, rot3p,
                    e1p, e2p, e3p, tstress, cstress, cstrain,
                )
                tload = 1
            elif tstrain <= umax_n:
                trot_min = tstrain
                tstress = _neg_stress(
                    tstrain, mom1n, rot1n, rot2n, mom2n, rot3n, mom3n,
                    e1n, e2n, e3n,
                )
                ktang, tphase = _neg_tangent(
                    tstrain, rot1n, rot2n, rot3n, e1n, e2n, e3n,
                )
                tload = 2
            elif dstrain < 0.0:
                tphase = UNLOAD_T if tstress > 0.0 else RELOAD_C
                num = 1.0
                num2 = (umax_p / rot1p) ** 1.0 if rot1p != 0.0 else 0.0
                if num2 <= 1.0:
                    num2 = 1.0
                else:
                    env = _pos_stress_typed(
                        tensile_curve_type, umax_p, rot1p, mom1p, rot2p,
                        mom2p, rot3p, mom3p, e1p, e2p, e3p,
                    )
                    num2 = env / mom1p / num2 if num2 != 0.0 else 1.0
                if tload == 1:
                    tload = 2
                    if cstress >= 0.0:
                        denom = eup * num2
                        trot_pu = cstrain - cstress / denom if denom != 0.0 else 0.0
                        if _pos_stress_typed(
                            tensile_curve_type, umax_p, rot1p, mom1p, rot2p,
                            mom2p, rot3p, mom3p, e1p, e2p, e3p,
                        ) == 0.0:
                            trot_pu = 0.0
                        trot_min = umax_n
                tload = 2
                if trot_min > rot1n:
                    trot_min = rot1n
                num5 = _neg_stress(
                    trot_min, mom1n, rot1n, rot2n, mom2n, rot3n, mom3n,
                    e1n, e2n, e3n,
                )
                num6 = _pos_rotlim_typed(
                    tensile_curve_type, umax_p, rot1p, mom1p, rot2p, mom2p,
                    e2p, e3p, rot3p, mom3p, e1p,
                )
                num7 = num6 if num6 < trot_pu else trot_pu
                if tstrain >= trot_pu:
                    ktang = eup * num2
                    tstress = cstress + ktang * dstrain
                    if tstress <= 0.0:
                        tstress = 0.0
                elif tstrain > num7:
                    tstress = 0.0
                else:
                    denom9 = trot_min - num7
                    ktang = num5 / denom9 if denom9 != 0.0 else 0.0
                    num10 = cstress + eun * num * dstrain
                    num11 = (tstrain - num7) * ktang
                    if num10 > num11:
                        tstress = num10
                        ktang = eun * num
                    else:
                        tstress = num11
                    if cstrain > trot_pu and tstrain < trot_pu:
                        ktang = eup * num2
                        tstress = cstress + ktang * (trot_pu - cstrain)
                        ktang = num5 / denom9 if denom9 != 0.0 else 0.0
                        tstress += ktang * (tstrain - trot_pu)
            elif dstrain > 0.0:
                tphase = RELOAD_T if tstress > 0.0 else UNLOAD_C
                num = 1.0
                num2 = (umax_p / rot1p) ** 1.0 if rot1p != 0.0 else 0.0
                if num2 <= 1.0:
                    num2 = 1.0
                else:
                    env = _pos_stress_typed(
                        tensile_curve_type, umax_p, rot1p, mom1p, rot2p,
                        mom2p, rot3p, mom3p, e1p, e2p, e3p,
                    )
                    num2 = env / mom1p / num2 if num2 != 0.0 else 1.0
                if tload == 2:
                    tload = 1
                    if cstress <= 0.0:
                        denom = eun * num
                        trot_nu = cstrain - cstress / denom if denom != 0.0 else 0.0
                        if _neg_stress(
                            umax_n, mom1n, rot1n, rot2n, mom2n,
                            rot3n, mom3n, e1n, e2n, e3n,
                        ) == 0.0:
                            trot_nu = 0.0
                        trot_max = umax_p
                tload = 1
                if trot_max < rot1p:
                    trot_max = rot1p
                num5 = _pos_stress_typed(
                    tensile_curve_type, trot_max, rot1p, mom1p, rot2p,
                    mom2p, rot3p, mom3p, e1p, e2p, e3p,
                )
                num6 = _neg_rotlim(
                    umax_n, mom1n, rot1n, rot2n, mom2n, e2n, e3n,
                    rot3n, mom3n, e1n,
                )
                num7 = num6 if num6 > trot_nu else trot_nu
                if tstrain <= trot_nu:
                    ktang = eun * num
                    tstress = cstress + ktang * dstrain
                    if tstress >= 0.0:
                        tstress = 0.0
                elif tstrain < num7:
                    tstress = 0.0
                else:
                    denom9 = trot_max - num7
                    ktang = num5 / denom9 if denom9 != 0.0 else 0.0
                    num10 = cstress + eup * num2 * dstrain
                    num11 = (tstrain - num7) * ktang
                    if num10 < num11:
                        tstress = num10
                        ktang = eup * num2
                    else:
                        tstress = num11
                    if cstrain < trot_nu and tstrain > trot_nu:
                        ktang = eun * num
                        tstress = cstress + ktang * (trot_nu - cstrain)
                        ktang = num5 / denom9 if denom9 != 0.0 else 0.0
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

    @njit(cache=True, nogil=True, parallel=True)
    def _advance_transverse_targets(
        trial, record_index, num, num2, di, dj, lengths, delta_flex, ecc, targets,
    ):
        """Update transverse trial strains with one independent row per fibre.

        Each output row depends only on immutable geometry and its owning
        interface kinematics, so parallel execution cannot change reduction
        order or constitutive history.
        """
        for i in prange(targets.size):
            ri = record_index[i]
            targets[i] = trial[i, 7] + (
                (num[ri] * dj[i] + num2[ri] * di[i]) / lengths[ri]
                - delta_flex[ri] * ecc[i]
            )

    @njit(cache=True, nogil=True, parallel=True)
    def _finish_transverse_batch(
        trial, committed, di, dj, ecc, lengths,
        starts, stops, constrained, local_forces,
        normal_increments, committed_forces, max_displacements,
    ):
        for record_index in prange(starts.size):
            start = starts[record_index]
            stop = stops[record_index]
            for local_dof in range(6):
                local_forces[record_index, local_dof] = 0.0
            normal_increment = 0.0
            committed_force = 0.0
            max_displacement = 0.0
            # These values are constant for all fibres in the interface.  Keep
            # the spring accumulation order unchanged while avoiding two dense
            # array reads for every transverse spring.
            length = lengths[record_index]
            is_constrained = constrained[record_index]
            if not is_constrained:
                # Quad/Quad components 0/1/5 are exact antisymmetric
                # counterparts of 3/2/4. Accumulate each ordered reduction
                # once, then mirror it without changing spring order.
                force_3 = 0.0
                force_2 = 0.0
                force_4 = 0.0
                for spring_index in range(start, stop):
                    force = trial[spring_index, 6]
                    committed_value = committed[spring_index, 6]
                    normal_increment -= force - committed_value
                    committed_force += committed_value
                    displacement = abs(trial[spring_index, 7])
                    if displacement > max_displacement:
                        max_displacement = displacement

                    force_3 += force * dj[spring_index] / length
                    force_2 += force * di[spring_index] / length
                    force_4 += force * ecc[spring_index]

                local_forces[record_index, 3] = force_3
                local_forces[record_index, 2] = force_2
                local_forces[record_index, 4] = force_4
                # The original accumulators start at positive zero.
                local_forces[record_index, 0] = 0.0 if force_3 == 0.0 else -force_3
                local_forces[record_index, 1] = 0.0 if force_2 == 0.0 else -force_2
                local_forces[record_index, 5] = 0.0 if force_4 == 0.0 else -force_4
            else:
                # Restraint interfaces use a different transformation; keep
                # their original C#-ordered arithmetic verbatim.
                for spring_index in range(start, stop):
                    force = trial[spring_index, 6]
                    committed_value = committed[spring_index, 6]
                    normal_increment -= force - committed_value
                    committed_force += committed_value
                    displacement = abs(trial[spring_index, 7])
                    if displacement > max_displacement:
                        max_displacement = displacement

                    local_forces[record_index, 3] += force * dj[spring_index] / length
                    local_forces[record_index, 2] += force * di[spring_index] / length
                    local_forces[record_index, 0] += (
                        (0.0 - force) * di[spring_index] / length
                        - force * dj[spring_index] / length
                    )
                    local_forces[record_index, 1] += 0.5 * length * (
                        force * dj[spring_index] / length
                        - force * di[spring_index] / length
                    )
                    local_forces[record_index, 4] += force * ecc[spring_index]
                    local_forces[record_index, 5] += (0.0 - force) * ecc[spring_index]
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

    @njit(cache=True, nogil=True)
    def _refresh_global_resisting_force(
        quad_d_alfa, quad_state, quad_forces,
        quad_offsets, quad_gdls, quad_coefficients,
        interface_forces, interface_offsets, interface_gdls,
        interface_coefficients, global_force,
    ):
        global_force[:] = 0.0
        for i in range(quad_forces.shape[0]):
            quad_forces[i, 0] = quad_d_alfa[i] * quad_state[i, QTSTRESS]
        _scatter_local_forces(
            interface_forces, interface_offsets, interface_gdls,
            interface_coefficients, global_force,
        )
        _scatter_local_forces(
            quad_forces, quad_offsets, quad_gdls, quad_coefficients,
            global_force,
        )

    @njit(cache=True, nogil=True)
    def _refresh_max_u_cache(quad_local_u, interface_max_u, cache):
        value = 0.0
        index = -1
        kind = 0
        for i in range(quad_local_u.shape[0]):
            for j in range(quad_local_u.shape[1]):
                candidate = abs(quad_local_u[i, j])
                if candidate > value:
                    value = candidate
                    index = i
                    kind = 1
        for i in range(interface_max_u.size):
            candidate = abs(interface_max_u[i])
            if candidate > value:
                value = candidate
                index = i
                kind = 2
        cache[0] = value
        cache[1] = index
        cache[2] = kind

    @njit(cache=True, nogil=True)
    def _prepare_interface_kinematics(
        local_du, local_u, lengths, constrained, d0s, d1s,
        nums, nums2, delta_flex, pending,
    ):
        for i in range(local_du.shape[0]):
            for j in range(local_du.shape[1]):
                local_u[i, j] += local_du[i, j]
            if not constrained[i]:
                nums[i] = local_du[i, 3] - local_du[i, 0]
                nums2[i] = local_du[i, 2] - local_du[i, 1]
            else:
                half_length = 0.5 * lengths[i]
                nums[i] = local_du[i, 3] - (local_du[i, 0] - local_du[i, 1] * half_length)
                nums2[i] = local_du[i, 2] - (local_du[i, 0] + local_du[i, 1] * half_length)
            delta_flex[i] = local_du[i, 5] - local_du[i, 4]
            d0 = d0s[i]
            d1 = d1s[i]
            pending[i, 0] = local_du[i, d0] - local_du[i, d0 + 1]
            pending[i, 1] = local_du[i, d0 + d1] - local_du[i, d0 + d1 + 2]
            pending[i, 2] = local_du[i, d0 + d1 + 1] - local_du[i, d0 + d1 + 3]

    @njit(cache=True, nogil=True)
    def _advance_interface_coulomb_targets(
        pending, dist_for, normal_increments, slid_index, oop0_index, oop1_index,
        targets, dns,
    ):
        for i in range(pending.shape[0]):
            s = slid_index[i]
            if s >= 0:
                targets[s] += pending[i, 0]
                dns[s] = normal_increments[i]
            a = oop0_index[i]
            b = oop1_index[i]
            if a >= 0 and b >= 0:
                di = dist_for[i, 0]
                dj = dist_for[i, 1]
                dua = pending[i, 1]
                dub = pending[i, 2]
                targets[a] += dua + (dub - dua) * di
                targets[b] += dua + (dub - dua) * dj
                dn = 0.5 * normal_increments[i]
                dns[a] = dn
                dns[b] = dn

    @njit(cache=True, nogil=True)
    def _evaluate_initial_coulomb_batch(params, state, targets, dns, enabled):
        """Exact C# ``setTrialStrainInitial`` for interface Coulomb springs.

        The accelerated path is deliberately limited to the model's supported
        no-contact-area Coulomb law.  Other variants stay on the scalar path.
        """
        for i in range(targets.size):
            if not enabled[i]:
                continue
            k = params[i, 0]
            h = params[i, 1]
            cohesion = params[i, 2]
            mu = params[i, 3]
            area = params[i, 4]
            e1p = params[i, 5]
            e2p = params[i, 6]

            # C# RevertToLastCommit subset used by the Initial law.
            fy0 = -state[i, CFY1]
            tup = state[i, CCUP]
            cstress = state[i, CCSTRESS]
            cstrain = state[i, CCSTRAIN]
            tstress_normal = state[i, CCSTRESS_NORMAL]
            tcontact_area = state[i, CCCONTACT_AREA]
            tenergy = state[i, CCENERGY]
            phase = int(state[i, CCPHASE])
            tphase = phase
            tstress = cstress
            tstrain = targets[i]
            ktang = state[i, CKTANG]
            dstrain = tstrain - cstrain

            if phase == RUPTURE:
                tstress = cstress
                tstress_normal += dns[i]
                state[i, CFY0] = fy0
                state[i, CTUP] = tup
                state[i, CTSTRESS] = tstress
                state[i, CTSTRAIN] = tstrain
                state[i, CTSTRESS_NORMAL] = tstress_normal
                state[i, CTCONTACT_AREA] = tcontact_area
                state[i, CTENERGY] = tenergy
                state[i, CTPHASE] = tphase
                state[i, CKTANG] = ktang
                state[i, CU] = tstrain
                state[i, CF] = tstress
                state[i, CDN] = dns[i]
                continue

            tcontact_area = area
            mom1p = cohesion + mu * tstress_normal
            if mom1p < 0.0:
                mom1p = 0.0
            c_hard = cohesion + h * abs(state[i, CCUP])
            if cohesion != 0.0:
                fy0 = c_hard + mu * tstress_normal
            else:
                fy0 = 0.0
            if fy0 < 0.0:
                fy0 = 0.0

            rot1p = mom1p / e1p if e1p != 0.0 else 0.0
            rot2p = state[i, CROT2P]
            rot3p = state[i, CROT3P]
            if e2p < 0.0:
                mom2p = 0.0
                rot2p = rot1p - mom1p / e2p
            else:
                if rot2p < rot1p:
                    rot2p = rot1p
                    rot3p = rot2p * 1.0001
                mom2p = mom1p + e2p * (rot2p - rot1p)
            mom1n = -mom1p
            rot1n = -rot1p
            mom2n = -mom2p
            rot2n = -rot2p
            rot3n = -rot3p

            num3 = cstress + k * dstrain
            if abs(num3) - fy0 > 0.0:
                if num3 > 0.0:
                    tphase = PLASTIC_T
                    sign = 1.0
                else:
                    tphase = PLASTIC_C
                    sign = -1.0
                num5 = (abs(num3) - fy0) / k
                num6 = k * num5 / (h + k)
                fy0 += h * num6
                tstress = fy0 * sign
                if tphase == PLASTIC_T and tstress < 0.0:
                    tphase = RUPTURE
                    tstress = 0.0
                    ktang = 0.0
                elif tphase == PLASTIC_C and tstress > 0.0:
                    tphase = RUPTURE
                    tstress = 0.0
                    ktang = 0.0
                else:
                    tup += num6
                    ktang = e2p
            else:
                tstress = num3
                ktang = k
                tphase = ELASTIC

            tenergy = state[i, CCENERGY] + 0.5 * (cstress + tstress) * dstrain
            tstress_normal += dns[i]
            state[i, CFY0] = fy0
            state[i, CTUP] = tup
            state[i, CTSTRESS] = tstress
            state[i, CTSTRAIN] = tstrain
            state[i, CTSTRESS_NORMAL] = tstress_normal
            state[i, CTCONTACT_AREA] = tcontact_area
            state[i, CTENERGY] = tenergy
            state[i, CTPHASE] = tphase
            state[i, CKTANG] = ktang
            state[i, CMOM1P] = mom1p
            state[i, CROT1P] = rot1p
            state[i, CMOM2P] = mom2p
            state[i, CROT2P] = rot2p
            state[i, CMOM1N] = mom1n
            state[i, CROT1N] = rot1n
            state[i, CMOM2N] = mom2n
            state[i, CROT2N] = rot2n
            state[i, CROT3N] = rot3n
            state[i, CROT3P] = rot3p
            state[i, CU] = tstrain
            state[i, CF] = tstress
            state[i, CDN] = dns[i]

    @njit(cache=True, nogil=True)
    def _assemble_full_interface_forces(
        transverse_forces, coulomb_state, slid_index, oop0_index, oop1_index,
        dist, local_full_forces, max_displacements, coulomb_targets,
    ):
        local_full_forces[:, :] = 0.0
        local_full_forces[:, :6] = transverse_forces
        for i in range(local_full_forces.shape[0]):
            max_u = max_displacements[i]
            s = slid_index[i]
            if s >= 0:
                force = coulomb_state[s, CTSTRESS]
                local_full_forces[i, 6] += force
                local_full_forces[i, 7] -= force
                value = abs(coulomb_targets[s])
                if value > max_u:
                    max_u = value
            a = oop0_index[i]
            b = oop1_index[i]
            if a >= 0 and b >= 0:
                di = dist[i, 0]
                dj = dist[i, 1]
                force0 = coulomb_state[a, CTSTRESS]
                force1 = coulomb_state[b, CTSTRESS]
                first = dj * force0 + di * force1
                second = di * force0 + dj * force1
                local_full_forces[i, 8] += first
                local_full_forces[i, 9] += second
                local_full_forces[i, 10] -= first
                local_full_forces[i, 11] -= second
                value = abs(coulomb_targets[a])
                if value > max_u:
                    max_u = value
                value = abs(coulomb_targets[b])
                if value > max_u:
                    max_u = value
            max_displacements[i] = max_u

    @njit(cache=True, nogil=True)
    def _prepare_quad_kinematics(
        local_du, local_u, edge_offsets, edge_records, edge_areas,
        interface_normal_increments, interface_committed_forces,
        d_alfa, step, sigma_initial, strains, dns,
    ):
        for q in range(local_du.shape[0]):
            for j in range(local_du.shape[1]):
                local_u[q, j] += local_du[q, j]
            normal0 = 0.0
            normal1 = 0.0
            normal2 = 0.0
            normal3 = 0.0
            stress0 = 0.0
            stress1 = 0.0
            stress2 = 0.0
            stress3 = 0.0
            base = q * 4
            for edge in range(4):
                normal = 0.0
                force = 0.0
                edge_index = base + edge
                for k in range(edge_offsets[edge_index], edge_offsets[edge_index + 1]):
                    record_index = edge_records[k]
                    normal += interface_normal_increments[record_index]
                    force += interface_committed_forces[record_index]
                area = edge_areas[q, edge]
                stress = force / area if area > 0.0 else 0.0
                if edge == 0:
                    normal0 = normal
                    stress0 = stress
                elif edge == 1:
                    normal1 = normal
                    stress1 = stress
                elif edge == 2:
                    normal2 = normal
                    stress2 = stress
                else:
                    normal3 = normal
                    stress3 = stress
            sigma = 0.5 * (stress0 + stress2) + 0.5 * (stress1 + stress3)
            dn = 0.5 * (normal0 + normal2) + 0.5 * (normal1 + normal3)
            if step == 1:
                sigma_initial[q] = sigma
            dns[q] = dn
            strains[q] = d_alfa[q] * local_u[q, 6]
    @njit(cache=True, inline="always")
    def _quad_revert_trial(row):
        row[QFY0] = -row[QFY1]
        row[QTROT_MAX] = row[QUMAX0]
        row[QTROT_MIN] = row[QUMAX1]
        row[QTROT_PU] = row[QCROT_PU]
        row[QTROT_NU] = row[QCROT_NU]
        row[QTENERGY] = row[QCENERGY]
        row[QTLOAD] = row[QCLOAD]
        row[QTSTRESS] = row[QCSTRESS]
        row[QTSTRAIN] = row[QCSTRAIN]
        row[QTSTRESS_NORMAL] = row[QCSTRESS_NORMAL]
        row[QTCONTACT] = row[QCCONTACT]
        row[QTUP] = row[QCUP]
        row[QTPHASE] = row[QPHASE]
        row[QTMOM_MAX] = row[QCMOM_MAX]
        row[QTMOM_MIN] = row[QCMOM_MIN]
        row[QTROT_LIM_PU] = row[QCROT_LIM_PU]
        row[QTROT_LIM_NU] = row[QCROT_LIM_NU]
        row[QTROT_YP] = row[QCROT_YP]
        row[QTROT_YN] = row[QCROT_YN]
        row[QTPLAST_T] = row[QCPLAST_T]
        row[QTPLAST_C] = row[QCPLAST_C]
        row[QTUNLOAD_T] = row[QCUNLOAD_T]
        row[QTUNLOAD_C] = row[QCUNLOAD_C]

    @njit(cache=True, inline="always")
    def _quad_tangent_reload_t(row, par):
        """C# SpringCoulomb03.TangentReload_t getter semantics."""
        minimum = 1.0e-4 * par[QPK]
        stored = row[QTANG_RELOAD_T]
        return minimum if stored < minimum else stored

    @njit(cache=True, inline="always")
    def _quad_tangent_reload_c(row, par):
        """C# SpringCoulomb03.TangentReload_c getter semantics."""
        minimum = 1.0e-4 * par[QPK]
        stored = row[QTANG_RELOAD_C]
        return minimum if stored < minimum else stored

    @njit(cache=True, inline="always")
    def _quad_yield_tension(row, par, phase_unload, dstrain):
        if row[QTPLAST_T] == 0.0:
            num2 = row[QMOM1P]
            num3 = row[QROT1P]
        else:
            num2 = row[QCMOM_MAX]
            num3 = row[QUMAX0]
        if dstrain < 0.0:
            return num3
        phase = int(row[QTPHASE])
        if phase == 10:
            return row[QTROT_MAX]
        if phase == ELASTIC or phase == PLASTIC_T:
            return row[QUMAX0]
        if phase == PLASTIC_C:
            if phase_unload == ELASTIC:
                return num3
            if phase_unload == PLASTIC_T or phase_unload == RELOAD_T:
                num4 = row[QCSTRAIN] - row[QCSTRESS] / par[QPE1N]
                num5 = _quad_tangent_reload_t(row, par) if num2 <= 0.0 else num2 / (num3 - num4)
                return row[QMOM1P] / num5 + num4
        if phase == UNLOAD_T:
            if phase_unload == ELASTIC:
                return num3
            if phase_unload == PLASTIC_T:
                return row[QTROT_PU] + row[QMOM1P] / par[QPE1P]
            if phase_unload == RELOAD_T:
                if row[QTSTRAIN] < row[QTROT_LIM_PU]:
                    return row[QTROT_PU] + row[QMOM1P] / par[QPE1P]
                return row[QTROT_NU] + row[QMOM1P] / _quad_tangent_reload_t(row, par)
        if phase == UNLOAD_C:
            if phase_unload == ELASTIC:
                return num3
            if phase_unload == PLASTIC_T or phase_unload == RELOAD_T:
                num5 = _quad_tangent_reload_t(row, par) if num2 <= 0.0 else num2 / (num3 - row[QTROT_NU])
                return row[QTROT_NU] + row[QMOM1P] / num5
        if phase == RELOAD_T:
            if phase_unload == ELASTIC or phase_unload == RELOAD_T:
                num5 = _quad_tangent_reload_t(row, par)
                num = row[QTROT_NU] + row[QMOM1P] / num5
                if par[QPE3P] < 0.0:
                    val = (row[QTROT_NU] * num5 - row[QROT3P] * par[QPE3P]) / (num5 - par[QPE3P])
                    if val < num:
                        num = val
                return num
        if phase == RELOAD_C:
            if phase_unload == ELASTIC:
                return num3
            if phase_unload == PLASTIC_T:
                num4 = row[QCSTRAIN] - row[QCSTRESS] / par[QPE1N]
                num5 = _quad_tangent_reload_t(row, par) if num2 <= 0.0 else num2 / (num3 - num4)
                return num4 + row[QMOM1P] / num5
            if phase_unload == RELOAD_T:
                if int(row[QTUNLOAD_C]) == RELOAD_C:
                    num4 = row[QCSTRAIN] - row[QCSTRESS] / par[QPE1N]
                    num5 = _quad_tangent_reload_t(row, par) if num2 <= 0.0 else num2 / (num3 - num4)
                    return row[QTROT_NU] + row[QMOM1P] / num5
                return row[QTROT_NU] + row[QMOM1P] / _quad_tangent_reload_t(row, par)
        return num3

    @njit(cache=True, inline="always")
    def _quad_yield_compression(row, par, phase_unload, dstrain):
        if row[QTPLAST_C] == 0.0:
            num2 = row[QMOM1N]
            num3 = row[QROT1N]
        else:
            num2 = row[QCMOM_MIN]
            num3 = row[QUMAX1]
        if dstrain > 0.0:
            return num3
        phase = int(row[QTPHASE])
        if phase == 10:
            return row[QTROT_MIN]
        if phase == ELASTIC or phase == PLASTIC_C:
            return row[QUMAX1]
        if phase == PLASTIC_T:
            if phase_unload == ELASTIC:
                return num3
            if phase_unload == PLASTIC_C or phase_unload == RELOAD_C:
                num4 = row[QCSTRAIN] - row[QCSTRESS] / par[QPE1P]
                tc = _quad_tangent_reload_c(row, par) if num2 == 0.0 else num2 / (num3 - num4)
                return row[QMOM1N] / tc + num4
        if phase == UNLOAD_T:
            if phase_unload == ELASTIC:
                return num3
            if phase_unload == PLASTIC_C or phase_unload == RELOAD_C:
                tc = _quad_tangent_reload_c(row, par) if num2 == 0.0 else num2 / (num3 - row[QTROT_PU])
                return row[QTROT_PU] + row[QMOM1N] / tc
        if phase == UNLOAD_C:
            if phase_unload == ELASTIC:
                return num3
            if phase_unload == PLASTIC_C:
                return row[QTROT_NU] + row[QMOM1N] / par[QPE1N]
            if phase_unload == RELOAD_C:
                if row[QTSTRAIN] > row[QTROT_LIM_NU]:
                    return row[QTROT_NU] + row[QMOM1N] / par[QPE1N]
                return row[QTROT_PU] + row[QMOM1N] / _quad_tangent_reload_c(row, par)
        if phase == RELOAD_T:
            if phase_unload == ELASTIC:
                return num3
            if phase_unload == PLASTIC_C:
                num4 = row[QCSTRAIN] - row[QCSTRESS] / par[QPE1P]
                tc = _quad_tangent_reload_c(row, par) if num2 == 0.0 else num2 / (num3 - num4)
                return num4 + row[QMOM1N] / tc
            if phase_unload == RELOAD_C:
                if int(row[QTUNLOAD_T]) == RELOAD_T:
                    num4 = row[QCSTRAIN] - row[QCSTRESS] / par[QPE1P]
                    tc = _quad_tangent_reload_c(row, par) if num2 == 0.0 else num2 / (num3 - num4)
                    return num4 + row[QMOM1N] / tc
                return row[QTROT_PU] + row[QMOM1N] / _quad_tangent_reload_c(row, par)
        if phase == RELOAD_C:
            if phase_unload == ELASTIC or phase_unload == RELOAD_C:
                tc = _quad_tangent_reload_c(row, par)
                num = row[QTROT_PU] + row[QMOM1N] / tc
                if par[QPE3N] < 0.0:
                    val = (row[QTROT_PU] * tc - row[QROT3N] * par[QPE3N]) / (tc - par[QPE3N])
                    if val > num:
                        num = val
                return num
        return num3

    @njit(cache=True, inline="always")
    def _quad_positive_increment(row, par, dstrain):
        if int(row[QTLOAD]) == 2:
            if (int(row[QTUNLOAD_C]) == RELOAD_C
                    and row[QTMOM_MIN] > row[QCSTRESS] and row[QCSTRESS] < 0.0):
                row[QTMOM_MIN] = row[QCSTRESS]
                row[QTROT_MIN] = row[QCSTRAIN]
                row[QTROT_NU] = row[QCSTRAIN] - row[QCSTRESS] / par[QPEUN]
            if int(row[QTUNLOAD_C]) == RELOAD_C and int(row[QTPHASE]) == RELOAD_C:
                row[QTROT_LIM_NU] = row[QCSTRAIN]
            row[QTLOAD] = 1.0
            if row[QCSTRESS] <= 0.0:
                row[QTROT_NU] = row[QCSTRAIN] - row[QCSTRESS] / par[QPEUN]
                row[QTROT_MAX] = row[QUMAX0]
        row[QTLOAD] = 1.0
        if row[QTPLAST_T] == 0.0:
            row[QTROT_MAX] = row[QROT1P]
            row[QTMOM_MAX] = row[QMOM1P]
        tmom_max = row[QTMOM_MAX]
        trot_nu = row[QTROT_NU]
        if row[QTSTRAIN] < trot_nu:
            row[QKTANG] = par[QPE1N]
            row[QTSTRESS] = row[QCSTRESS] + row[QKTANG] * dstrain
            if row[QTSTRESS] < row[QMOM1N]:
                row[QTSTRESS] = row[QMOM1N]
            if row[QTSTRESS] >= 0.0:
                row[QTSTRESS] = 0.0
                row[QKTANG] = par[QPEUN] * 1e-9
            return
        phase = int(row[QTPHASE])
        if phase == PLASTIC_C:
            row[QKTANG] = tmom_max / (row[QTROT_MAX] - trot_nu)
            row[QTSTRESS] = row[QKTANG] * (row[QTSTRAIN] - trot_nu)
        elif phase == ELASTIC or phase == UNLOAD_C:
            if int(row[QTUNLOAD_C]) == ELASTIC:
                row[QKTANG] = tmom_max / (row[QTROT_MAX] - trot_nu)
                row[QTSTRESS] = row[QCSTRESS] + row[QKTANG] * dstrain
            elif int(row[QTUNLOAD_C]) == PLASTIC_C or int(row[QTUNLOAD_C]) == RELOAD_C:
                row[QKTANG] = tmom_max / (row[QTROT_MAX] - trot_nu)
                row[QTSTRESS] = row[QKTANG] * (row[QTSTRAIN] - trot_nu)
        elif phase == UNLOAD_T:
            if int(row[QTUNLOAD_T]) == ELASTIC or int(row[QTUNLOAD_T]) == PLASTIC_T:
                row[QKTANG] = par[QPE1P]
                row[QTSTRESS] = row[QCSTRESS] + row[QKTANG] * dstrain
            elif int(row[QTUNLOAD_T]) == RELOAD_T:
                if row[QTSTRAIN] < row[QTROT_LIM_PU]:
                    row[QKTANG] = par[QPE1P]
                    row[QTSTRESS] = row[QCSTRESS] + row[QKTANG] * dstrain
                else:
                    row[QKTANG] = _quad_tangent_reload_t(row, par)
                    row[QTSTRESS] = row[QKTANG] * (row[QTSTRAIN] - trot_nu)
        elif phase == RELOAD_C:
            row[QKTANG] = tmom_max / (row[QTROT_MAX] - trot_nu)
            row[QTSTRESS] = row[QKTANG] * (row[QTSTRAIN] - trot_nu)
        elif phase == RELOAD_T:
            row[QKTANG] = _quad_tangent_reload_t(row, par)
            row[QTSTRESS] = row[QKTANG] * (row[QTSTRAIN] - trot_nu)

    @njit(cache=True, inline="always")
    def _quad_negative_increment(row, par, dstrain):
        if int(row[QTLOAD]) == 1:
            if (int(row[QTUNLOAD_T]) == RELOAD_T
                    and row[QTMOM_MAX] < row[QCSTRESS] and row[QCSTRESS] > 0.0):
                row[QTMOM_MAX] = row[QCSTRESS]
                row[QTROT_MAX] = row[QCSTRAIN]
                row[QTROT_PU] = row[QCSTRAIN] - row[QCSTRESS] / par[QPEUP]
            if int(row[QTUNLOAD_T]) == RELOAD_T and int(row[QTPHASE]) == RELOAD_T:
                row[QTROT_LIM_PU] = row[QCSTRAIN]
            row[QTLOAD] = 2.0
            if row[QCSTRESS] >= 0.0:
                row[QTROT_PU] = row[QCSTRAIN] - row[QCSTRESS] / par[QPEUP]
                row[QTROT_MIN] = row[QUMAX1]
        row[QTLOAD] = 2.0
        if row[QTPLAST_C] == 0.0:
            row[QTROT_MIN] = row[QROT1N]
            row[QTMOM_MIN] = row[QMOM1N]
        tmom_min = row[QTMOM_MIN]
        trot_pu = row[QTROT_PU]
        if row[QTSTRAIN] > trot_pu:
            row[QKTANG] = par[QPE1P]
            row[QTSTRESS] = row[QCSTRESS] + row[QKTANG] * dstrain
            if row[QTSTRESS] > row[QMOM1P]:
                row[QTSTRESS] = row[QMOM1P]
            if row[QTSTRESS] <= 0.0:
                row[QTSTRESS] = 0.0
                row[QKTANG] = par[QPEUP] * 1e-9
            return
        phase = int(row[QTPHASE])
        if phase == PLASTIC_T:
            row[QKTANG] = tmom_min / (row[QTROT_MIN] - trot_pu)
            row[QTSTRESS] = row[QKTANG] * (row[QTSTRAIN] - trot_pu)
        elif phase == ELASTIC or phase == UNLOAD_T:
            if int(row[QTUNLOAD_T]) == ELASTIC:
                row[QKTANG] = tmom_min / (row[QTROT_MIN] - trot_pu)
                row[QTSTRESS] = row[QCSTRESS] + row[QKTANG] * dstrain
            elif int(row[QTUNLOAD_T]) == PLASTIC_T or int(row[QTUNLOAD_T]) == RELOAD_T:
                row[QKTANG] = tmom_min / (row[QTROT_MIN] - trot_pu)
                row[QTSTRESS] = row[QKTANG] * (row[QTSTRAIN] - trot_pu)
        elif phase == UNLOAD_C:
            if int(row[QTUNLOAD_C]) == ELASTIC or int(row[QTUNLOAD_C]) == PLASTIC_C:
                row[QKTANG] = par[QPE1N]
                row[QTSTRESS] = row[QCSTRESS] + row[QKTANG] * dstrain
            elif int(row[QTUNLOAD_C]) == RELOAD_C:
                if row[QTSTRAIN] > row[QTROT_LIM_NU]:
                    row[QKTANG] = par[QPE1N]
                    row[QTSTRESS] = row[QCSTRESS] + row[QKTANG] * dstrain
                else:
                    row[QKTANG] = _quad_tangent_reload_c(row, par)
                    row[QTSTRESS] = row[QKTANG] * (row[QTSTRAIN] - trot_pu)
        elif phase == RELOAD_T:
            row[QKTANG] = tmom_min / (row[QTROT_MIN] - trot_pu)
            row[QTSTRESS] = row[QKTANG] * (row[QTSTRAIN] - trot_pu)
        elif phase == RELOAD_C:
            row[QKTANG] = _quad_tangent_reload_c(row, par)
            row[QTSTRESS] = row[QKTANG] * (row[QTSTRAIN] - trot_pu)

    @njit(cache=True, nogil=True)
    def _evaluate_quad_takeda_batch(params, state, strains, dns, volumes, sigma_initial):
        for i in range(state.shape[0]):
            row = state[i]
            par = params[i]
            if par[QPENABLED] == 0.0:
                continue
            strain = strains[i]
            dn = dns[i]
            row[QDN] = dn
            if int(row[QTLOAD]) == 0 and strain == 0.0:
                continue
            _quad_revert_trial(row)
            row[QTSTRAIN] = strain
            dstrain = strain - row[QCSTRAIN]
            tau = _quad_tau_limit(par, row[QTSTRESS_NORMAL])
            rot1p = tau / par[QPE1P] if par[QPE1P] != 0.0 else 0.0
            if int(par[QPFRACTURE_MODE]) in (
                QUAD_FRACTURE_FIXED, QUAD_FRACTURE_INTERPOLATED
            ):
                ultimate = _quad_shear_ultimate_strain(
                    par, tau, rot1p, volumes[i], sigma_initial[i]
                )
                row[QUR0] = ultimate
                row[QUR1] = -ultimate
                row[QMOM1P] = tau
                row[QMOM2P] = tau
                row[QROT1P] = rot1p
                row[QROT2P] = max(ultimate, rot1p * 1.0001)
                row[QROT3P] = max(ultimate, row[QROT2P] * 1.0001)
            else:
                row[QMOM1P] = tau
                row[QROT1P] = rot1p
                if par[QPE3P] < 0.0:
                    rot2p = par[QPPLASTIC_STRAIN]
                    candidate = rot1p * 1.0001
                    if candidate > rot2p:
                        rot2p = candidate
                    row[QROT2P] = rot2p
                    row[QROT3P] = rot2p - row[QMOM2P] / par[QPE3P]
                if row[QROT2P] < rot1p:
                    row[QROT2P] = rot1p * 1.0001
                if row[QROT3P] < row[QROT2P]:
                    row[QROT3P] = row[QROT2P] * 1.0001
                row[QMOM2P] = tau + par[QPE2P] * (row[QROT2P] - rot1p)
            row[QMOM1N] = -row[QMOM1P]
            row[QROT1N] = -row[QROT1P]
            row[QMOM2N] = -row[QMOM2P]
            row[QROT2N] = -row[QROT2P]
            row[QROT3N] = -row[QROT3P]
            row[QFY0] = row[QMOM1P]
            row[QFY1] = row[QMOM1N]
            if row[QMOM1P] == 0.0:
                row[QTPHASE] = 10.0
                row[QTSTRESS] = 0.0
                row[QKTANG] = 0.0
                row[QTENERGY] = row[QCENERGY] + 0.5 * (row[QCSTRESS] + row[QTSTRESS]) * dstrain
                row[QTSTRESS_NORMAL] += dn
                continue
            if int(row[QPHASE]) == 10:
                row[QTLOAD] = 0.0
                row[QTPHASE] = ELASTIC
                row[QTPLAST_T] = 1.0
                row[QTPLAST_C] = 1.0
                row[QTROT_NU] = row[QCSTRAIN]
                row[QTROT_PU] = row[QCSTRAIN]
                row[QKTANG] = par[QPE2P]
                row[QTANG_RELOAD_C] = row[QKTANG]
                row[QTANG_RELOAD_T] = row[QKTANG]
                row[QTSTRESS] = row[QKTANG] * dstrain
                row[QTROT_MAX] = row[QCSTRAIN] + row[QROT1P]
                row[QTMOM_MAX] = row[QKTANG] * row[QROT1P]
                row[QTROT_MIN] = row[QCSTRAIN] + row[QROT1N]
                row[QTMOM_MIN] = row[QKTANG] * row[QROT1N]
                if dstrain > 0.0:
                    row[QTLOAD] = 1.0
                    row[QTPHASE] = RELOAD_T
                else:
                    row[QTPHASE] = RELOAD_C
                    row[QTLOAD] = 2.0
                if abs(row[QTSTRESS]) - row[QMOM1P] > 0.0:
                    sign = 1.0 if row[QTSTRESS] > 0.0 else -1.0
                    row[QTSTRESS] = row[QMOM1P] * sign
                    if sign > 0.0:
                        row[QTPHASE] = PLASTIC_T
                        row[QTMOM_MAX] = row[QTSTRESS]
                        row[QTROT_MAX] = row[QTSTRAIN]
                    else:
                        row[QTPHASE] = PLASTIC_C
                        row[QTMOM_MIN] = row[QTSTRESS]
                        row[QTROT_MIN] = row[QTSTRAIN]
                row[QTENERGY] = row[QCENERGY] + 0.5 * (row[QCSTRESS] + row[QTSTRESS]) * dstrain
                row[QTSTRESS_NORMAL] += dn
                continue
            if int(row[QPHASE]) == RUPTURE_T or int(row[QPHASE]) == RUPTURE_C:
                row[QTSTRESS] = 0.0
                row[QKTANG] = 0.0
                row[QTENERGY] = row[QCENERGY] + 0.5 * row[QCSTRESS] * dstrain
                row[QTSTRESS_NORMAL] += dn
                continue
            row[QTROT_YP] = _quad_yield_tension(row, par, int(row[QCUNLOAD_T]), dstrain)
            row[QTROT_YN] = _quad_yield_compression(row, par, int(row[QCUNLOAD_C]), dstrain)
            if int(row[QTLOAD]) == 0:
                row[QTLOAD] = 1.0 if dstrain >= 0.0 else 2.0
            if row[QTSTRAIN] >= row[QTROT_YP] and dstrain > 0.0:
                row[QTROT_MAX] = row[QTSTRAIN]
                yp = row[QTROT_YP] if row[QTPLAST_T] != 0.0 else row[QROT1P]
                if row[QTSTRAIN] < yp:
                    row[QTPHASE] = ELASTIC
                    row[QKTANG] = par[QPE1P]
                elif row[QTSTRAIN] <= row[QROT2P]:
                    row[QTPHASE] = PLASTIC_T
                    row[QKTANG] = par[QPE2P]
                elif row[QTSTRAIN] <= row[QROT3P]:
                    row[QTPHASE] = PLASTIC_T
                    row[QKTANG] = par[QPE3P]
                else:
                    row[QTPHASE] = RUPTURE_T
                    row[QKTANG] = par[QPE1P] * 1e-9
                if row[QTSTRAIN] < yp:
                    row[QTSTRESS] = par[QPE1P] * row[QTSTRAIN]
                elif row[QTSTRAIN] <= row[QROT2P]:
                    row[QTSTRESS] = row[QMOM1P] + par[QPE2P] * (row[QTSTRAIN] - yp)
                elif row[QTSTRAIN] <= row[QROT3P]:
                    row[QTSTRESS] = row[QMOM2P] + par[QPE3P] * (row[QTSTRAIN] - row[QROT2P])
                else:
                    row[QTSTRESS] = row[QMOM3P]
                row[QTLOAD] = 1.0
                num5 = (row[QTSTRESS] - row[QCSTRESS]) / par[QPE1P] if par[QPE1P] != 0.0 else 0.0
                row[QTUP] += dstrain - num5
                if int(row[QTPHASE]) == PLASTIC_T:
                    row[QTPLAST_T] = 1.0
                row[QTMOM_MAX] = row[QTSTRESS]
            elif row[QTSTRAIN] <= row[QTROT_YN] and dstrain < 0.0:
                row[QTROT_MIN] = row[QTSTRAIN]
                yn = row[QTROT_YN] if int(row[QTUNLOAD_C]) != ELASTIC else row[QROT1N]
                if row[QTSTRAIN] > row[QTROT_PU]:
                    row[QKTANG] = par[QPE1N] * 1e-9
                elif row[QTSTRAIN] > yn:
                    row[QTPHASE] = ELASTIC
                    row[QKTANG] = par[QPE1N]
                elif row[QTSTRAIN] >= row[QROT2N]:
                    row[QTPHASE] = PLASTIC_C
                    row[QKTANG] = par[QPE2N]
                elif row[QTSTRAIN] >= row[QROT3N]:
                    row[QTPHASE] = PLASTIC_C
                    row[QKTANG] = par[QPE3N]
                else:
                    row[QTPHASE] = RUPTURE_C
                    row[QKTANG] = par[QPE1N] * 1e-9
                yn2 = row[QTROT_YN] if row[QTPLAST_C] != 0.0 else row[QROT1N]
                if row[QTSTRAIN] > yn2:
                    row[QTSTRESS] = par[QPE1N] * row[QTSTRAIN]
                elif row[QTSTRAIN] >= row[QROT2N]:
                    row[QTSTRESS] = row[QMOM1N] + par[QPE2N] * (row[QTSTRAIN] - yn2)
                elif row[QTSTRAIN] >= row[QROT3N]:
                    row[QTSTRESS] = row[QMOM2N] + par[QPE3N] * (row[QTSTRAIN] - row[QROT2N])
                else:
                    row[QTSTRESS] = row[QMOM3N]
                row[QTLOAD] = 2.0
                num6 = (row[QTSTRESS] - row[QCSTRESS]) / par[QPE1N] if par[QPE1N] != 0.0 else 0.0
                row[QTUP] += dstrain - num6
                if int(row[QTPHASE]) == PLASTIC_C:
                    row[QTPLAST_C] = 1.0
                row[QTMOM_MIN] = row[QTSTRESS]
            elif dstrain < 0.0:
                _quad_negative_increment(row, par, dstrain)
                if row[QTSTRESS] > 0.0:
                    row[QTPHASE] = UNLOAD_T
                elif int(row[QTPHASE]) == UNLOAD_C:
                    row[QTPHASE] = UNLOAD_C
                    if row[QTSTRAIN] <= row[QTROT_LIM_NU] and int(row[QCUNLOAD_C]) == RELOAD_C:
                        row[QTPHASE] = RELOAD_C
                else:
                    row[QTPHASE] = RELOAD_C
            elif dstrain > 0.0:
                _quad_positive_increment(row, par, dstrain)
                if row[QTSTRESS] < 0.0:
                    row[QTPHASE] = UNLOAD_C
                elif int(row[QTPHASE]) == UNLOAD_T:
                    row[QTPHASE] = UNLOAD_T
                    if row[QTSTRAIN] >= row[QTROT_LIM_PU] and int(row[QCUNLOAD_T]) == RELOAD_T:
                        row[QTPHASE] = RELOAD_T
                else:
                    row[QTPHASE] = RELOAD_T
            row[QTENERGY] = row[QCENERGY] + 0.5 * (row[QCSTRESS] + row[QTSTRESS]) * dstrain
            row[QTSTRESS_NORMAL] += dn

    @njit(cache=True, nogil=True)
    def _commit_quad_takeda_batch(params, state):
        for i in range(state.shape[0]):
            if params[i, QPENABLED] == 0.0:
                continue
            row = state[i]
            row[QFY1] = -row[QFY0]
            row[QCUP] = row[QTUP]
            row[QUMAX0] = row[QTROT_MAX]
            row[QUMAX1] = row[QTROT_MIN]
            row[QCROT_PU] = row[QTROT_PU]
            row[QCROT_NU] = row[QTROT_NU]
            row[QCENERGY] = row[QTENERGY]
            row[QCLOAD] = row[QTLOAD]
            row[QCSTRESS_NORMAL_PREV] = row[QCSTRESS_NORMAL]
            row[QCSTRESS] = row[QTSTRESS]
            row[QCSTRAIN] = row[QTSTRAIN]
            row[QCSTRESS_NORMAL] = row[QTSTRESS_NORMAL]
            row[QCCONTACT] = row[QTCONTACT]
            row[QDN] = 0.0
            row[QKTANG_COMMITTED] = row[QKTANG]
            row[QPHASE] = row[QTPHASE]
            row[QCMOM_MAX] = row[QTMOM_MAX]
            row[QCMOM_MIN] = row[QTMOM_MIN]
            row[QCROT_LIM_PU] = row[QTROT_LIM_PU]
            row[QCROT_LIM_NU] = row[QTROT_LIM_NU]
            row[QCROT_YP] = row[QTROT_YP]
            row[QCROT_YN] = row[QTROT_YN]
            phase = int(row[QPHASE])
            if phase == PLASTIC_T:
                row[QTUNLOAD_T] = phase
            elif phase == PLASTIC_C:
                row[QTUNLOAD_C] = phase
            elif phase == RELOAD_T:
                if row[QTPLAST_T] == 0.0 and row[QTPLAST_C] == 0.0:
                    row[QTUNLOAD_T] = ELASTIC
                else:
                    row[QTUNLOAD_T] = phase
                    row[QTPLAST_T] = 1.0
                row[QTANG_RELOAD_T] = row[QKTANG]
            elif phase == RELOAD_C:
                if row[QTPLAST_T] == 0.0 and row[QTPLAST_C] == 0.0:
                    row[QTUNLOAD_C] = ELASTIC
                else:
                    row[QTUNLOAD_C] = phase
                    row[QTPLAST_C] = 1.0
                row[QTANG_RELOAD_C] = row[QKTANG]
            row[QCPLAST_C] = row[QTPLAST_C]
            row[QCPLAST_T] = row[QTPLAST_T]
            row[QCUNLOAD_T] = row[QTUNLOAD_T]
            row[QCUNLOAD_C] = row[QTUNLOAD_C]

    @njit(cache=True, nogil=True)
    def _commit_initial_coulomb_batch(state, enabled):
        for i in range(state.shape[0]):
            if not enabled[i]:
                continue
            row = state[i]
            row[CFY1] = -row[CFY0]
            row[CCUP] = row[CTUP]
            row[CCSTRESS_NORMAL_PREV] = row[CCSTRESS_NORMAL]
            row[CCSTRESS] = row[CTSTRESS]
            row[CCSTRAIN] = row[CTSTRAIN]
            row[CCSTRESS_NORMAL] = row[CTSTRESS_NORMAL]
            row[CCCONTACT_AREA] = row[CTCONTACT_AREA]
            row[CCENERGY] = row[CTENERGY]
            row[CCPHASE] = row[CTPHASE]
            row[CKTANG_COMMITTED] = row[CKTANG]
            row[CU] = row[CTSTRAIN]
            row[CF] = row[CTSTRESS]
            row[CDN] = 0.0

    @njit(cache=True, nogil=True)
    def _managed_elastic_energy(transverse_k, transverse_trial, quad_k, quad_state):
        # Preserve the Python/C# element iteration order: Quads first, then
        # interface transverse springs. Interface Coulomb springs are not part
        # of ModelManager's elastic-energy accumulator.
        value = 0.0
        for i in range(quad_k.size):
            # Preserve the existing solver ordering: energy is evaluated
            # before Quad.Commit publishes the current trial strain, so the
            # object-level implementation sees the last committed strain.
            strain = quad_state[i, QCSTRAIN]
            value += 0.5 * quad_k[i] * strain * strain
        for i in range(transverse_k.size):
            strain = transverse_trial[i, 7]
            value += 0.5 * transverse_k[i] * strain * strain
        return value

    @njit(cache=True, nogil=True)
    def _update_domain_batch(
        x,
        aff_offsets, aff_gdls, aff_coefficients, local_du,
        local_u, lengths, constrained, d0s, d1s, num, num2, delta_flex,
        pending_values, record_index, di, dj, ecc, inv_length, targets,
        params, committed, trial, enabled, simple_hysteretic,
        starts, stops, local_forces,
        normal_increments, committed_forces, max_displacements,
        dist_for, slid_index, oop0_index, oop1_index, coulomb_targets,
        coulomb_dns, coulomb_params, coulomb_state, coulomb_enabled,
        dist, local_full_forces,
        quad_aff_offsets, quad_aff_gdls, quad_aff_coefficients, quad_local_du,
        quad_local_u, quad_edge_offsets, quad_edge_records, quad_edge_areas,
        quad_d_alfa, quad_volumes, step, quad_sigma_initial, quad_strains, quad_dns,
        quad_params, quad_state, quad_forces, quad_force_offsets,
        quad_force_gdls, quad_force_coefficients, global_resisting_force,
        max_u_cache,
    ):
        # One compiled boundary per Newton correction. Calling the individual
        # kernels from Numba avoids four Python↔native transitions and keeps
        # their shared dense arrays hot in cache.
        _map_global_to_local(
            x, aff_offsets, aff_gdls, aff_coefficients, local_du,
        )
        _prepare_interface_kinematics(
            local_du, local_u, lengths, constrained, d0s, d1s,
            num, num2, delta_flex, pending_values,
        )
        for i in range(targets.size):
            ri = record_index[i]
            targets[i] = trial[i, 7] + (
                (num[ri] * dj[i] + num2[ri] * di[i]) / lengths[ri]
                - delta_flex[ri] * ecc[i]
            )
        if simple_hysteretic:
            _evaluate_simple_linear_batch(
                params, committed, trial, targets, enabled,
            )
        else:
            _evaluate_linear_batch(
                params, committed, trial, targets, enabled,
            )
        _finish_transverse_batch(
            trial, committed, di, dj, ecc, lengths, starts, stops,
            constrained, local_forces, normal_increments,
            committed_forces, max_displacements,
        )
        if coulomb_targets.size:
            _advance_interface_coulomb_targets(
                pending_values, dist_for, normal_increments,
                slid_index, oop0_index, oop1_index,
                coulomb_targets, coulomb_dns,
            )
            _evaluate_initial_coulomb_batch(
                coulomb_params, coulomb_state, coulomb_targets,
                coulomb_dns, coulomb_enabled,
            )
        _assemble_full_interface_forces(
            local_forces, coulomb_state, slid_index, oop0_index, oop1_index,
            dist, local_full_forces, max_displacements, coulomb_targets,
        )

        if quad_local_du.shape[0]:
            _map_global_to_local(
                x, quad_aff_offsets, quad_aff_gdls,
                quad_aff_coefficients, quad_local_du,
            )
            _prepare_quad_kinematics(
                quad_local_du, quad_local_u, quad_edge_offsets,
                quad_edge_records, quad_edge_areas, normal_increments,
                committed_forces, quad_d_alfa, step, quad_sigma_initial,
                quad_strains, quad_dns,
            )
            _evaluate_quad_takeda_batch(
                quad_params, quad_state, quad_strains, quad_dns,
                quad_volumes, quad_sigma_initial,
            )
        _refresh_global_resisting_force(
            quad_d_alfa, quad_state, quad_forces, quad_force_offsets,
            quad_force_gdls, quad_force_coefficients, local_full_forces,
            aff_offsets, aff_gdls, aff_coefficients, global_resisting_force,
        )
        _refresh_max_u_cache(quad_local_u, max_displacements, max_u_cache)

else:
    _quad_tau_limit = None
    _quad_interpolated_shear_energy = None
    _quad_shear_ultimate_strain = None
    _pos_stress_typed = None
    _pos_tangent_typed = None
    _pos_rotlim_typed = None
    _evaluate_linear_batch = None
    _advance_transverse_targets = None
    _evaluate_simple_linear_batch = None
    _advance_and_evaluate_simple_linear_batch = None
    _finish_transverse_batch = None
    _map_global_to_local = None
    _scatter_local_forces = None
    _refresh_global_resisting_force = None
    _refresh_max_u_cache = None
    _prepare_interface_kinematics = None
    _advance_interface_coulomb_targets = None
    _evaluate_initial_coulomb_batch = None
    _assemble_full_interface_forces = None
    _prepare_quad_kinematics = None
    _evaluate_quad_takeda_batch = None
    _commit_quad_takeda_batch = None
    _commit_initial_coulomb_batch = None
    _managed_elastic_energy = None
    _update_domain_batch = None


_PARAM_NAMES = (
    "pinch_xp", "pinch_yp", "pinch_xn", "pinch_yn",
    "damfc1p", "damfc2p", "damfc1n", "damfc2n", "betap", "betan",
    "rot1p", "mom1p", "rot2p", "mom2p", "rot3p", "mom3p",
    "mom1n", "rot1n", "rot2n", "mom2n", "rot3n", "mom3n",
    "e1n", "e1p", "e2n", "e2p", "e3n", "e3p", "eun", "eup",
    "energy_a", "k",
)


if len(_PARAM_NAMES) != TENSILE_CURVE_TYPE_PARAM:
    raise RuntimeError(
        "Transverse hysteretic parameter layout changed without updating "
        "TENSILE_CURVE_TYPE_PARAM"
    )

_PARAM_GETTER = attrgetter(*_PARAM_NAMES)

# Generated masonry interface fibres use the zero-pinching/zero-damage
# specialization below.  The specialized kernel never reads parameter columns
# 0..9 (pinching/damage/beta), ``energy_a`` (column 30), or ``k`` (column 31).
# Keeping those twelve float64 values for every one of the ~550k transverse
# fibres in a representative bridge costs about 50 MiB with no numerical use.
# A compact runtime therefore stores only columns 10..29 plus the tensile-law
# discriminator.  The generic layout remains unchanged for non-simple springs
# and for the diagnostic force-general switch.
SIMPLE_PARAM_NAMES = _PARAM_NAMES[10:30]
SIMPLE_TENSILE_CURVE_TYPE_PARAM = len(SIMPLE_PARAM_NAMES)
SIMPLE_TRANSVERSE_PARAM_SIZE = SIMPLE_TENSILE_CURVE_TYPE_PARAM + 1
_SIMPLE_PARAM_GETTER = attrgetter(*SIMPLE_PARAM_NAMES)


def _force_general_hysteretic_batch() -> bool:
    return os.environ.get(
        "HISTRA_FORCE_GENERAL_HYSTERETIC_BATCH", ""
    ).strip().lower() in {"1", "true", "yes", "on"}


def _uses_simple_hysteretic_parameters(spring: SpringHysteretic) -> bool:
    """Return the exact predicate used by the specialized dense kernel."""
    return (
        spring.pinch_xp == 0.0
        and spring.pinch_yp == 0.0
        and spring.pinch_xn == 0.0
        and spring.pinch_yn == 0.0
        and spring.damfc1p == 0.0
        and spring.damfc2p == 0.0
        and spring.damfc1n == 0.0
        and spring.damfc2n == 0.0
        and spring.betap == 1.0
        and spring.betan == 0.0
    )


class _TransverseParameterView:
    """Logical 33-column view over transverse hysteretic parameters.

    ``HystereticBatchRuntime.params`` historically exposed the complete dense
    parameter layout.  The compact simple-law runtime stores only the 21 values
    consumed by the specialized Numba kernel, but diagnostics and regression
    tooling still rely on the legacy column numbers (notably column 32 for the
    tensile-envelope discriminator).  This view preserves those read/write
    semantics without allocating a second full matrix during normal solves.

    Accessing a broad slice or coercing the view to an ndarray materializes only
    the requested logical values.  Writing through the view promotes the runtime
    to the full 33-column storage first; this is intentionally rare and preserves
    the historical mutability of ``params`` without compromising the compact
    production path.
    """

    def __init__(self, runtime: "HystereticBatchRuntime") -> None:
        self._runtime = runtime

    @property
    def shape(self) -> tuple[int, int]:
        return (self._runtime._params.shape[0], TRANSVERSE_PARAM_SIZE)

    @property
    def ndim(self) -> int:
        return 2

    @property
    def dtype(self) -> np.dtype:
        return np.dtype(np.float64)

    @property
    def size(self) -> int:
        rows, columns = self.shape
        return rows * columns

    def __len__(self) -> int:
        return self.shape[0]

    @staticmethod
    def _normalise_column(column: int) -> int:
        if column < 0:
            column += TRANSVERSE_PARAM_SIZE
        if not 0 <= column < TRANSVERSE_PARAM_SIZE:
            raise IndexError(
                f"index {column} is out of bounds for axis 1 with size "
                f"{TRANSVERSE_PARAM_SIZE}"
            )
        return column

    def _selected_energy_a(self, rows: Any) -> Any:
        indices = np.arange(len(self), dtype=np.intp)[rows]
        if np.ndim(indices) == 0:
            return float(self._runtime.springs[int(indices)].energy_a)
        flat = np.asarray(indices, dtype=np.intp).ravel()
        values = np.fromiter(
            (float(self._runtime.springs[int(index)].energy_a) for index in flat),
            dtype=np.float64,
            count=flat.size,
        )
        return values.reshape(np.asarray(indices).shape)

    def _materialize_rows(self, rows: Any) -> np.ndarray:
        runtime = self._runtime
        if not runtime._compact_simple_params:
            return np.asarray(runtime._params[rows], dtype=np.float64).copy()

        compact = runtime._params[rows]
        output_shape = compact.shape[:-1] + (TRANSVERSE_PARAM_SIZE,)
        result = np.empty(output_shape, dtype=np.float64)
        result[..., :8] = 0.0
        result[..., 8] = 1.0
        result[..., 9] = 0.0
        result[..., 10:30] = compact[..., :len(SIMPLE_PARAM_NAMES)]
        result[..., 30] = self._selected_energy_a(rows)
        result[..., 31] = runtime._transverse_k[rows]
        result[..., TENSILE_CURVE_TYPE_PARAM] = (
            compact[..., SIMPLE_TENSILE_CURVE_TYPE_PARAM]
        )
        return result

    def __getitem__(self, key: Any) -> Any:
        runtime = self._runtime
        if not runtime._compact_simple_params:
            return runtime._params[key]

        if isinstance(key, tuple) and len(key) == 2:
            rows, columns = key
            if isinstance(columns, (int, np.integer)):
                column = self._normalise_column(int(columns))
                if column < 8 or column == 9:
                    selected = runtime._transverse_k[rows]
                    if np.ndim(selected) == 0:
                        return 0.0
                    return np.zeros_like(selected, dtype=np.float64)
                if column == 8:
                    selected = runtime._transverse_k[rows]
                    if np.ndim(selected) == 0:
                        return 1.0
                    return np.ones_like(selected, dtype=np.float64)
                if 10 <= column < 30:
                    return runtime._params[rows, column - 10]
                if column == 30:
                    return self._selected_energy_a(rows)
                if column == 31:
                    return runtime._transverse_k[rows]
                return runtime._params[rows, SIMPLE_TENSILE_CURVE_TYPE_PARAM]
            return self._materialize_rows(rows)[..., columns]

        return self._materialize_rows(key)

    def __setitem__(self, key: Any, value: Any) -> None:
        runtime = self._runtime
        if runtime._compact_simple_params:
            runtime._promote_transverse_parameter_storage()
        runtime._params[key] = value
        # Column 31 historically represented ``k`` in the full parameter array;
        # keep the dedicated stiffness cache coherent after any compatibility
        # write.
        runtime._transverse_k[:] = runtime._params[:, 31]
        runtime._refresh_simple_hysteretic_flag()

    def copy(self, order: str = "C") -> np.ndarray:
        return np.array(self._materialize_rows(slice(None)), copy=True, order=order)

    def __array__(self, dtype: Any = None, copy: bool | None = None) -> np.ndarray:
        array = self._materialize_rows(slice(None))
        if dtype is not None:
            array = array.astype(dtype, copy=False)
        if copy is True:
            array = array.copy()
        return array

    def __repr__(self) -> str:
        return repr(self._materialize_rows(slice(None)))


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
        self.interface_rejection_reasons: Counter[str] = Counter()
        springs: list[SpringHysteretic] = []
        for interface in model.collections.interfaces.values():
            group = list(interface.trasv_1)
            if not group:
                self.interface_rejection_reasons["no_transverse_springs"] += 1
                continue
            rejection_reason = ""
            for spring in group:
                rejection_reason = self._transverse_rejection_reason(spring)
                if rejection_reason:
                    break
            if rejection_reason:
                self.interface_rejection_reasons[rejection_reason] += 1
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
        self._compact_simple_params = bool(
            n
            and not _force_general_hysteretic_batch()
            and all(_uses_simple_hysteretic_parameters(spring) for spring in springs)
        )
        parameter_count = (
            SIMPLE_TRANSVERSE_PARAM_SIZE
            if self._compact_simple_params else TRANSVERSE_PARAM_SIZE
        )
        self._params = np.empty((n, parameter_count), dtype=np.float64)
        # Keep the historical 33-column logical parameter interface while the
        # solver consumes the compact physical storage directly.
        self.params = _TransverseParameterView(self)
        self.committed = np.empty((n, 9), dtype=np.float64)
        self.trial = np.empty((n, 10), dtype=np.float64)
        self.targets = np.empty(n, dtype=np.float64)
        self.enabled = np.empty(n, dtype=np.bool_)
        self._transverse_k = np.empty(n, dtype=np.float64)
        self._read_transverse_objects_bulk(springs)
        self._refresh_simple_hysteretic_flag()
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
        self._lengths = np.asarray(
            [record.interface.length for record in self.records], dtype=np.float64
        )
        self._d0s = np.asarray(
            [
                record.interface.dim_aff[0] if record.interface.dim_aff else 6
                for record in self.records
            ],
            dtype=np.int32,
        )
        self._d1s = np.asarray(
            [
                record.interface.dim_aff[1]
                if len(record.interface.dim_aff) > 1 else 2
                for record in self.records
            ],
            dtype=np.int32,
        )
        self._pending_values = np.zeros((len(self.records), 3), dtype=np.float64)
        self._local_forces = np.zeros((len(self.records), 6), dtype=np.float64)
        self._normal_increments = np.zeros(len(self.records), dtype=np.float64)
        self._committed_forces = np.zeros(len(self.records), dtype=np.float64)
        self._max_displacements = np.zeros(len(self.records), dtype=np.float64)
        self._record_by_id = {
            id(record.interface): index for index, record in enumerate(self.records)
        }

        # Batch the three interface Coulomb springs (one in-plane and two
        # out-of-plane) when they use the simple C# Initial law.  Unsupported
        # variants remain on the scalar object path.
        from histra.springs.coulomb03 import SpringCoulomb03
        self.interface_coulomb_rejection_reasons: Counter[str] = Counter()
        coulomb_springs: list[SpringCoulomb03] = []
        # C# can hold the same SpringCoulomb03 object in both out-of-plane
        # positions of a restraint/custom-material interface.  Preserve that
        # identity in dense state so both kinematic increments accumulate into
        # one row just as the two C# list accesses update one object.
        coulomb_index_by_id: dict[int, int] = {}
        self._slid_index = np.full(len(self.records), -1, dtype=np.int32)
        self._oop0_index = np.full(len(self.records), -1, dtype=np.int32)
        self._oop1_index = np.full(len(self.records), -1, dtype=np.int32)
        self._dist = np.zeros((len(self.records), 2), dtype=np.float64)
        self._dist_for = np.zeros((len(self.records), 2), dtype=np.float64)
        for record_index, record in enumerate(self.records):
            interface = record.interface
            interface._ensure_performance_cache()
            if interface._perf_dist is not None:
                self._dist[record_index, :] = interface._perf_dist
            if interface._perf_dist_for is not None:
                self._dist_for[record_index, :] = interface._perf_dist_for

            candidates: list[tuple[str, Any]] = []
            if interface.slid:
                candidates.append(("slid", interface.slid[0]))
            if len(interface.slid_out_plan) >= 2:
                candidates.extend(
                    (("oop0", interface.slid_out_plan[0]),
                     ("oop1", interface.slid_out_plan[1]))
                )
            for kind, spring in candidates:
                rejection_reason = self._coulomb_rejection_reason(spring)
                if rejection_reason:
                    self.interface_coulomb_rejection_reasons[
                        f"{kind}:{rejection_reason}"
                    ] += 1
                    continue
                spring_id = id(spring)
                index = coulomb_index_by_id.get(spring_id, -1)
                if index < 0:
                    index = len(coulomb_springs)
                    coulomb_index_by_id[spring_id] = index
                    coulomb_springs.append(spring)
                    spring._histra_batch_managed = True
                if kind == "slid":
                    self._slid_index[record_index] = index
                elif kind == "oop0":
                    self._oop0_index[record_index] = index
                else:
                    self._oop1_index[record_index] = index

        self.coulomb_springs = coulomb_springs
        nc = len(coulomb_springs)
        self.coulomb_params = np.empty((nc, 7), dtype=np.float64)
        self.coulomb_state = np.empty((nc, COULOMB_STATE_SIZE), dtype=np.float64)
        self.coulomb_targets = np.empty(nc, dtype=np.float64)
        self.coulomb_dns = np.zeros(nc, dtype=np.float64)
        self.coulomb_enabled = np.empty(nc, dtype=np.bool_)
        for i, spring in enumerate(coulomb_springs):
            self.coulomb_params[i, :] = (
                float(spring.k), float(spring.h), float(spring.cohesion),
                float(spring.mu), float(spring.area), float(spring.e1p),
                float(spring.e2p),
            )
            self._read_coulomb_object(i, spring)
            self.coulomb_targets[i] = float(spring.u)
            self.coulomb_enabled[i] = bool(spring.is_on)
        self.managed_springs = [*self.springs, *self.coulomb_springs]
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
        self._local_u = np.asarray(
            [record.interface.status.u[:12] for record in self.records],
            dtype=np.float64,
        )
        self._local_full_forces = np.zeros((len(self.records), 12), dtype=np.float64)

        # Dense Quad kinematics / ComputeDN preparation. Compatible diagonal
        # SpringCoulomb03 laws are evaluated in the fused Numba kernel.  Every
        # rejected Quad is classified so production profiles can explain the
        # residual scalar path instead of only reporting its aggregate cost.
        self.quad_records: list[Any] = []
        self.quad_rejection_reasons: Counter[str] = Counter()
        quad_offsets = [0]
        quad_gdls: list[int] = []
        quad_coefficients: list[float] = []
        edge_offsets = [0]
        edge_records: list[int] = []
        edge_areas: list[list[float]] = []
        quad_d_alfa: list[float] = []
        quad_volumes: list[float] = []
        quad_materials: list[Any] = []
        quad_sublaws: list[int] = []
        quad_fracture_modes: list[int] = []
        quad_fracture_energies: list[float] = []
        disable_quad_batch = os.environ.get(
            "HISTRA_DISABLE_COMPILED_QUADS", ""
        ).strip().lower() in {"1", "true", "yes", "on"}
        for quad in model.collections.quads.values():
            if disable_quad_batch:
                self.quad_rejection_reasons["disabled_by_environment"] += 1
                continue
            spring = getattr(quad, "spring", None)
            if not isinstance(spring, SpringCoulomb03):
                self.quad_rejection_reasons["unsupported_spring_type"] += 1
                continue
            if spring.hysteretic_type != "Takeda":
                self.quad_rejection_reasons["unsupported_hysteretic_type"] += 1
                continue
            sub_law_name = str(spring.sub_law).strip().lower()
            if sub_law_name == "coulomb":
                sub_law = QUAD_SUBLAW_COULOMB
            elif sub_law_name == "cacovic":
                if float(spring.cohesion) == 0.0 or float(spring.bcacovic) == 0.0:
                    self.quad_rejection_reasons["invalid_cacovic_parameters"] += 1
                    continue
                sub_law = QUAD_SUBLAW_CACOVIC
            else:
                self.quad_rejection_reasons["unsupported_shear_sublaw"] += 1
                continue
            if spring.check_contact_area:
                self.quad_rejection_reasons["contact_area_check"] += 1
                continue
            if _evaluate_quad_takeda_batch is None:
                self.quad_rejection_reasons["numba_kernel_unavailable"] += 1
                continue

            material = model.collections.materials.get(quad.material_key)
            fracture_mode = masonry_shear_law_code(material)
            if fracture_mode not in (
                ELASTO_PLASTIC_FRACTURE_ENERGY_FIXED,
                ELASTO_PLASTIC_ENERGY_SIGMA_INTERPOLATION,
            ):
                fracture_mode = QUAD_FRACTURE_NONE

            quad._ensure_dn_cache(model.collections)
            assert quad._perf_dn_edges is not None
            assert quad._perf_dn_areas is not None
            compatible = True
            rejection_reason = ""
            local_edge_records: list[int] = []
            local_edge_counts: list[int] = []
            for refs in quad._perf_dn_edges:
                count = 0
                for interface, custom_springs in refs:
                    if custom_springs:
                        compatible = False
                        rejection_reason = "custom_edge_springs"
                        break
                    if "compute_dn" in interface.__dict__:
                        compatible = False
                        rejection_reason = "custom_interface_compute_dn"
                        break
                    record_index = self._record_by_id.get(id(interface))
                    if record_index is None:
                        compatible = False
                        rejection_reason = "edge_interface_not_batched"
                        break
                    local_edge_records.append(record_index)
                    count += 1
                if not compatible:
                    break
                local_edge_counts.append(count)
            if not compatible:
                self.quad_rejection_reasons[rejection_reason] += 1
                continue

            self.quad_records.append(quad)
            if quad._perf_aff_pairs is None:
                quad._perf_aff_pairs = tuple(
                    tuple((entry.gdl - 1, float(entry.alfa)) for entry in entries)
                    for entries in quad.aff[:7]
                )
            for local_dof in range(7):
                pairs = quad._perf_aff_pairs[local_dof] if quad._perf_aff_pairs else ()
                for gdl, coefficient in pairs:
                    quad_gdls.append(int(gdl))
                    quad_coefficients.append(float(coefficient))
                quad_offsets.append(len(quad_gdls))
            cursor = 0
            for count in local_edge_counts:
                edge_records.extend(local_edge_records[cursor:cursor + count])
                cursor += count
                edge_offsets.append(len(edge_records))
            edge_areas.append([float(value) for value in quad._perf_dn_areas])
            quad_d_alfa.append(float(quad.d_alfa_2d_diag()))
            quad_volumes.append(float(quad.compute_volume()))
            quad_materials.append(material)
            quad_sublaws.append(sub_law)
            quad_fracture_modes.append(fracture_mode)
            quad_fracture_energies.append(fracture_energy_shear(material))

        self.quad_ids = frozenset(id(quad) for quad in self.quad_records)
        self.unmanaged_interfaces = tuple(
            interface for interface in model.collections.interfaces.values()
            if id(interface) not in self.interface_ids
        )
        self.unmanaged_quads = tuple(
            quad for quad in model.collections.quads.values()
            if id(quad) not in self.quad_ids
        )
        self._quad_aff_offsets = np.asarray(quad_offsets, dtype=np.int32)
        self._quad_aff_gdls = np.asarray(quad_gdls, dtype=np.int32)
        self._quad_aff_coefficients = np.asarray(quad_coefficients, dtype=np.float64)
        self._quad_edge_offsets = np.asarray(edge_offsets, dtype=np.int32)
        self._quad_edge_records = np.asarray(edge_records, dtype=np.int32)
        self._quad_edge_areas = np.asarray(
            edge_areas, dtype=np.float64
        ).reshape((len(self.quad_records), 4))
        self._quad_d_alfa = np.asarray(quad_d_alfa, dtype=np.float64)
        self._quad_volumes = np.asarray(quad_volumes, dtype=np.float64)
        self._quad_materials = quad_materials
        self._quad_local_du = np.zeros((len(self.quad_records), 7), dtype=np.float64)
        # ``np.asarray([])`` has shape ``(0,)``.  Keep the Quad displacement
        # storage rank-stable when the diagnostic interface-only runtime
        # deliberately contains no managed Quads; Numba kernels consume this
        # array as a two-dimensional ``(n_quads, 7)`` matrix.
        self._quad_local_u = np.asarray(
            [quad.status.u[:7] for quad in self.quad_records], dtype=np.float64
        ).reshape((len(self.quad_records), 7))
        self._quad_sigma_initial = np.asarray(
            [float(quad.sigma_initial) for quad in self.quad_records], dtype=np.float64
        )
        self._quad_strains = np.zeros(len(self.quad_records), dtype=np.float64)
        self._quad_dns = np.zeros(len(self.quad_records), dtype=np.float64)
        self.quad_params = np.zeros(
            (len(self.quad_records), QUAD_PARAM_SIZE), dtype=np.float64
        )
        self.quad_state = np.zeros(
            (len(self.quad_records), QUAD_STATE_SIZE), dtype=np.float64
        )
        self._quad_k = np.empty(len(self.quad_records), dtype=np.float64)
        for index, quad in enumerate(self.quad_records):
            spring = quad.spring
            spring._histra_batch_managed = True
            spring._histra_quad_batch = self
            spring._histra_quad_batch_index = index
            self.quad_params[index, :] = (
                float(spring.cohesion), float(spring.mu),
                float(spring.e1p), float(spring.e2p), float(spring.e3p),
                float(spring.e1n), float(spring.e2n), float(spring.e3n),
                float(spring.eup), float(spring.eun),
                float(spring.plastic_strain_ratio), float(bool(spring.is_on)),
                float(spring.k), float(quad_sublaws[index]),
                float(spring.bcacovic), float(quad_fracture_modes[index]),
                float(quad_fracture_energies[index]),
            )
            self._read_quad_object(index, spring)
            self._quad_k[index] = float(spring.k)
        self.managed_springs.extend(quad.spring for quad in self.quad_records)
        self._quad_forces = np.zeros((len(self.quad_records), 1), dtype=np.float64)
        quad_force_offsets = [0]
        quad_force_gdls: list[int] = []
        quad_force_coefficients: list[float] = []
        for quad in self.quad_records:
            pairs = quad._perf_aff_pairs[6] if quad._perf_aff_pairs else ()
            for gdl, coefficient in pairs:
                quad_force_gdls.append(int(gdl))
                quad_force_coefficients.append(float(coefficient))
            quad_force_offsets.append(len(quad_force_gdls))
        self._quad_force_offsets = np.asarray(quad_force_offsets, dtype=np.int32)
        self._quad_force_gdls = np.asarray(quad_force_gdls, dtype=np.int32)
        self._quad_force_coefficients = np.asarray(
            quad_force_coefficients, dtype=np.float64
        )
        self._global_resisting_force = np.zeros(int(model.gdl), dtype=np.float64)
        self._max_u_cache = np.zeros(3, dtype=np.float64)
        self._refresh_transverse_cache()
        self._refresh_full_force_cache()
        self._refresh_global_resisting_force_cache()
        self._refresh_max_u_cache()
        self._objects_trial_synced = True

    @staticmethod
    def _transverse_rejection_reason(spring: Any) -> str:
        if not isinstance(spring, SpringHysteretic):
            return "unsupported_transverse_spring_type"
        if spring.tensile_curve_type not in {
            "LinearHardening", "LinearSoftening", "Exponential"
        }:
            return "unsupported_tensile_curve_type"
        if spring.compressive_curve_type not in {
            "LinearHardening", "LinearSoftening"
        }:
            return "unsupported_compressive_curve_type"
        return ""

    @staticmethod
    def _coulomb_rejection_reason(spring: Any) -> str:
        from histra.springs.coulomb03 import SpringCoulomb03

        if not isinstance(spring, SpringCoulomb03):
            return "unsupported_spring_type"
        if spring.hysteretic_type != "Initial":
            return "unsupported_hysteretic_type"
        if spring.sub_law != "Coulomb":
            return "unsupported_shear_sublaw"
        if spring.check_contact_area:
            return "contact_area_check"
        return ""

    def _rebuild_interface_coulomb_storage(
        self, *, changed_record_indices: frozenset[int] | None = None
    ) -> None:
        """Rebuild only interface-Coulomb dense rows after topology changes.

        Foundation material replacement can split an aliased fixed-restraint
        out-of-plane spring into two independent soil springs (or the reverse).
        That changes only the tiny interface-Coulomb identity/index topology;
        rebuilding the complete runtime also re-imported ~550k transverse
        hysteretic objects and all Quad metadata.

        Recreate the same Coulomb coverage/order used by ``__init__`` while
        retaining transverse, geometry and Quad dense arrays unchanged.  When
        the caller identifies the records that changed, rows whose spring
        identity occurs only in untouched records are copied from the previous
        synchronized dense storage instead of re-reading dozens of Python
        attributes from every Coulomb object. ``coulomb_dns`` deliberately is
        *not* copied: a topology rebuild historically resets that array to zero.
        """
        from histra.springs.coulomb03 import SpringCoulomb03

        old_springs = self.coulomb_springs
        old_params = self.coulomb_params
        old_state = self.coulomb_state
        old_targets = self.coulomb_targets
        old_enabled = self.coulomb_enabled
        old_slid_index = self._slid_index
        old_oop0_index = self._oop0_index
        old_oop1_index = self._oop1_index
        known_changes = changed_record_indices is not None
        changed_records = changed_record_indices or frozenset()

        for spring in old_springs:
            if hasattr(spring, "_histra_batch_managed"):
                delattr(spring, "_histra_batch_managed")

        rejection_reasons: Counter[str] = Counter()
        springs: list[SpringCoulomb03] = []
        index_by_id: dict[int, int] = {}
        # At most three interface Coulomb rows can occur per record. Keep the
        # reuse metadata compact instead of allocating Python int/bool lists.
        max_coulomb_rows = 3 * len(self.records)
        old_row_for_new = np.full(max_coulomb_rows, -1, dtype=np.int32)
        row_touched = np.empty(max_coulomb_rows, dtype=np.bool_)
        slid_index = np.full(len(self.records), -1, dtype=np.int32)
        oop0_index = np.full(len(self.records), -1, dtype=np.int32)
        oop1_index = np.full(len(self.records), -1, dtype=np.int32)

        for record_index, record in enumerate(self.records):
            interface = record.interface
            candidates: list[tuple[str, Any]] = []
            if interface.slid:
                candidates.append(("slid", interface.slid[0]))
            if len(interface.slid_out_plan) >= 2:
                candidates.extend(
                    (
                        ("oop0", interface.slid_out_plan[0]),
                        ("oop1", interface.slid_out_plan[1]),
                    )
                )

            for kind, spring in candidates:
                rejection_reason = self._coulomb_rejection_reason(spring)
                if rejection_reason:
                    rejection_reasons[f"{kind}:{rejection_reason}"] += 1
                    continue

                spring_id = id(spring)
                dense_index = index_by_id.get(spring_id, -1)
                if dense_index < 0:
                    dense_index = len(springs)
                    index_by_id[spring_id] = dense_index
                    springs.append(spring)
                    if kind == "slid":
                        previous_index = int(old_slid_index[record_index])
                    elif kind == "oop0":
                        previous_index = int(old_oop0_index[record_index])
                    else:
                        previous_index = int(old_oop1_index[record_index])
                    if (
                        0 <= previous_index < len(old_springs)
                        and old_springs[previous_index] is spring
                    ):
                        old_row_for_new[dense_index] = previous_index
                    row_touched[dense_index] = (
                        (not known_changes) or record_index in changed_records
                    )
                    spring._histra_batch_managed = True
                elif record_index in changed_records:
                    # An object may be shared by multiple interfaces. If even
                    # one occurrence belongs to a changed record, re-import it
                    # rather than assuming an in-place material mutation did
                    # not alter the shared object.
                    row_touched[dense_index] = True

                if kind == "slid":
                    slid_index[record_index] = dense_index
                elif kind == "oop0":
                    oop0_index[record_index] = dense_index
                else:
                    oop1_index[record_index] = dense_index

        count = len(springs)
        old_row_for_new = old_row_for_new[:count]
        row_touched = row_touched[:count]
        params = np.empty((count, 7), dtype=np.float64)
        state = np.empty((count, COULOMB_STATE_SIZE), dtype=np.float64)
        targets = np.empty(count, dtype=np.float64)
        dns = np.zeros(count, dtype=np.float64)
        enabled = np.empty(count, dtype=np.bool_)

        # Publish storage before importing rows because _read_coulomb_object()
        # writes through self.coulomb_state.
        self.coulomb_springs = springs
        self.coulomb_params = params
        self.coulomb_state = state
        self.coulomb_targets = targets
        self.coulomb_dns = dns
        self.coulomb_enabled = enabled
        self._slid_index = slid_index
        self._oop0_index = oop0_index
        self._oop1_index = oop1_index
        self.interface_coulomb_rejection_reasons = rejection_reasons

        # Unchanged identities retain scan order, so material topology edits
        # normally leave a handful of contiguous old->new index runs. Copy
        # those runs as slices. This avoids the full-sized temporary arrays
        # created by NumPy advanced indexing while still doing each bulk copy
        # in C. The scalar fallback is only the number of topology boundaries,
        # not the number of unchanged Coulomb rows.
        run_new = -1
        run_old = -1
        previous_old = -2

        def copy_run(start_new: int, start_old: int, stop_new: int) -> None:
            if start_new < 0:
                return
            length = stop_new - start_new
            old_stop = start_old + length
            params[start_new:stop_new, :] = old_params[start_old:old_stop, :]
            state[start_new:stop_new, :] = old_state[start_old:old_stop, :]
            targets[start_new:stop_new] = old_targets[start_old:old_stop]
            enabled[start_new:stop_new] = old_enabled[start_old:old_stop]

        for index, (old_index, touched) in enumerate(
            zip(old_row_for_new, row_touched, strict=True)
        ):
            reusable = old_index >= 0 and not touched
            if reusable and run_new >= 0 and old_index == previous_old + 1:
                previous_old = old_index
                continue
            if run_new >= 0:
                copy_run(run_new, run_old, index)
                run_new = -1
            if reusable:
                run_new = index
                run_old = old_index
                previous_old = old_index
        if run_new >= 0:
            copy_run(run_new, run_old, count)

        for index, spring in enumerate(springs):
            if old_row_for_new[index] >= 0 and not row_touched[index]:
                continue
            params[index, :] = (
                float(spring.k),
                float(spring.h),
                float(spring.cohesion),
                float(spring.mu),
                float(spring.area),
                float(spring.e1p),
                float(spring.e2p),
            )
            self._read_coulomb_object(index, spring)
            targets[index] = float(spring.u)
            enabled[index] = bool(spring.is_on)

        # Preserve the constructor's managed-spring ordering exactly:
        # transverse -> interface Coulomb -> Quad diagonal.
        self.managed_springs = [
            *self.springs,
            *self.coulomb_springs,
            *(quad.spring for quad in self.quad_records),
        ]

    def _read_transverse_objects_bulk(
        self, springs: list[SpringHysteretic], *, chunk_size: int = 4096
    ) -> None:
        """Import the initial transverse object state in NumPy-sized chunks.

        The previous constructor called ``_read_transverse_object`` once for
        every fibre.  With ~550k fibres that means ~550k Python→NumPy row
        assignments for each dense array.  Material updates usually touch only
        a few interfaces and should retain the scalar importer; the initial
        runtime build is large enough to amortize bulk conversion.

        Chunking bounds temporary Python tuples/NumPy arrays to a few MiB and
        preserves spring order and float64 conversion semantics exactly.
        """
        count = len(springs)
        if count == 0:
            return
        if chunk_size <= 0:
            raise ValueError(f"chunk_size must be positive, got {chunk_size}")

        if self._compact_simple_params:
            getter = _SIMPLE_PARAM_GETTER
            fixed_parameter_count = len(SIMPLE_PARAM_NAMES)
            curve_column = SIMPLE_TENSILE_CURVE_TYPE_PARAM
        else:
            getter = _PARAM_GETTER
            fixed_parameter_count = len(_PARAM_NAMES)
            curve_column = TENSILE_CURVE_TYPE_PARAM

        for start in range(0, count, chunk_size):
            stop = min(start + chunk_size, count)
            group = springs[start:stop]
            group_count = stop - start

            self._params[start:stop, :fixed_parameter_count] = np.asarray(
                [getter(spring) for spring in group], dtype=np.float64
            )
            self._params[start:stop, curve_column] = np.fromiter(
                (
                    TENSILE_EXPONENTIAL
                    if spring.tensile_curve_type == "Exponential"
                    else TENSILE_LINEAR
                    for spring in group
                ),
                dtype=np.float64,
                count=group_count,
            )
            self._transverse_k[start:stop] = np.fromiter(
                (spring.k for spring in group),
                dtype=np.float64,
                count=group_count,
            )
            self.committed[start:stop, :] = np.asarray(
                [
                    (
                        spring.umax[0], spring.umax[1], spring._crot_pu,
                        spring._crot_nu, spring.cenergy_d,
                        spring._cload_indicator, spring._cstress,
                        spring._cstrain, int(spring.phase),
                    )
                    for spring in group
                ],
                dtype=np.float64,
            )
            self.trial[start:stop, :] = np.asarray(
                [
                    (
                        spring._trot_max, spring._trot_min, spring._trot_pu,
                        spring._trot_nu, spring._tenergy_d,
                        spring._tload_indicator, spring._tstress,
                        spring._tstrain, int(spring.t_phase), spring.k_tang,
                    )
                    for spring in group
                ],
                dtype=np.float64,
            )
            self.targets[start:stop] = np.fromiter(
                (spring._tstrain for spring in group),
                dtype=np.float64,
                count=group_count,
            )
            self.enabled[start:stop] = np.fromiter(
                (spring.is_on for spring in group),
                dtype=np.bool_,
                count=group_count,
            )

    def _read_transverse_object(self, index: int, spring: SpringHysteretic) -> None:
        # ``operator.attrgetter`` performs the fixed 32-attribute traversal in
        # C and returns the values in exactly ``_PARAM_NAMES`` order. NumPy
        # performs the same float64 conversion on assignment as the previous
        # Python ``float(getattr(...))`` list comprehension, without creating
        # 32 Python float objects and a temporary list for every spring.
        if self._compact_simple_params:
            self._params[index, :len(SIMPLE_PARAM_NAMES)] = _SIMPLE_PARAM_GETTER(spring)
            self._params[index, SIMPLE_TENSILE_CURVE_TYPE_PARAM] = (
                TENSILE_EXPONENTIAL
                if spring.tensile_curve_type == "Exponential"
                else TENSILE_LINEAR
            )
        else:
            self._params[index, :len(_PARAM_NAMES)] = _PARAM_GETTER(spring)
            self._params[index, TENSILE_CURVE_TYPE_PARAM] = (
                TENSILE_EXPONENTIAL
                if spring.tensile_curve_type == "Exponential"
                else TENSILE_LINEAR
            )
        self._transverse_k[index] = float(spring.k)
        self.committed[index, :] = (
            spring.umax[0], spring.umax[1], spring._crot_pu, spring._crot_nu,
            spring.cenergy_d, spring._cload_indicator, spring._cstress,
            spring._cstrain, int(spring.phase),
        )
        self.trial[index, :] = (
            spring._trot_max, spring._trot_min, spring._trot_pu,
            spring._trot_nu, spring._tenergy_d, spring._tload_indicator,
            spring._tstress, spring._tstrain, int(spring.t_phase),
            spring.k_tang,
        )
        self.targets[index] = float(spring._tstrain)
        self.enabled[index] = bool(spring.is_on)

    def _promote_transverse_parameter_storage(self) -> None:
        """Materialize the historical full layout after an explicit write."""
        if not self._compact_simple_params:
            return
        full = self.params._materialize_rows(slice(None))
        self._params = full
        self._compact_simple_params = False

    def _refresh_simple_hysteretic_flag(self) -> None:
        n = len(self.springs)
        if self._compact_simple_params:
            # Compact storage is created only after every spring satisfies the
            # exact simple-law predicate, and incremental material updates are
            # rejected before import if a replacement violates it.
            self._simple_hysteretic = bool(n)
        else:
            self._simple_hysteretic = bool(
                n
                and np.all(self._params[:, :8] == 0.0)
                and np.all(self._params[:, 8] == 1.0)
                and np.all(self._params[:, 9] == 0.0)
            )
        # Diagnostic/correctness switch.  The specialized zero-pinching kernel
        # must remain bit-for-bit equivalent to the authoritative scalar state
        # machine through unloading/reloading histories.  Force the general
        # compiled kernel while investigating any full-analysis divergence.
        if _force_general_hysteretic_batch() and not self._compact_simple_params:
            self._simple_hysteretic = False

    @property
    def active(self) -> bool:
        return bool(self.springs or self.coulomb_springs or self.quad_records)

    def try_update_material_interfaces(self, interfaces: list[Any] | tuple[Any, ...]) -> bool:
        """Refresh changed interface constitutive rows without rebuilding the runtime.

        Material-only mutations preserve geometry, DOFs and afference topology.
        Transverse rows are refreshed in place; compact parameter storage is
        promoted to the full constitutive layout when required. Compatible
        interface-Coulomb identity/index changes (notably fixed-restraint to
        soil out-of-plane alias splitting) rebuild only that small dense
        subsystem. Any unsupported constitutive or structural change returns
        ``False`` before runtime arrays are modified, preserving the existing
        conservative full-runtime fallback.

        The spring objects must already contain the authoritative committed and
        trial state.  ``solve_static_nonlinear`` guarantees that condition at
        analysis boundaries by synchronizing the dense runtime in ``finally``.
        """
        changed = tuple(interfaces)
        if not changed:
            return True
        if not self._objects_trial_synced:
            # Do not import potentially stale object state into the dense
            # runtime.  A full rebuild is the conservative fallback.
            return False

        validated: list[tuple[int, _InterfaceSlice, tuple[Any, ...], tuple[tuple[int, Any], ...]]] = []
        requires_full_parameter_storage = False
        requires_coulomb_rebuild = False
        for interface in changed:
            record_index = self._record_by_id.get(id(interface))
            if record_index is None:
                return False
            record = self.records[record_index]
            group = tuple(interface.trasv_1)
            if len(group) != record.stop - record.start:
                return False
            if any(self._transverse_rejection_reason(spring) for spring in group):
                return False
            if self._compact_simple_params and any(
                not _uses_simple_hysteretic_parameters(spring) for spring in group
            ):
                # The compact matrix omits pinching/damage/beta columns, but a
                # material-only mutation does not change runtime topology.  Do
                # not discard and rebuild every dense array merely because the
                # constitutive row now needs the general layout.  Finish
                # validating *all* changed interfaces first, then promote the
                # existing transverse parameter storage once and update only
                # the changed rows below.
                requires_full_parameter_storage = True

            candidates: list[tuple[int, Any]] = []
            if len(interface.slid) > 1 or len(interface.slid_out_plan) > 2:
                return False

            old_oop0 = int(self._oop0_index[record_index])
            old_oop1 = int(self._oop1_index[record_index])
            old_oop_alias = old_oop0 >= 0 and old_oop0 == old_oop1
            new_oop_alias = (
                len(interface.slid_out_plan) >= 2
                and interface.slid_out_plan[0] is interface.slid_out_plan[1]
            )
            # A material mutation can change object-identity topology (fixed
            # restraint -> Soil is the relevant case).  Only the interface
            # Coulomb mapping needs rebuilding; the ~550k transverse rows and
            # all Quad/geometry arrays remain valid.
            if old_oop_alias != new_oop_alias:
                # Identity topology can change without invalidating any of the
                # large transverse/Quad arrays, but only if every replacement
                # spring still belongs to the compiled interface-Coulomb law.
                # Otherwise this interface must return to the conservative
                # scalar/full-runtime fallback.
                current_coulomb = []
                if interface.slid:
                    current_coulomb.append(interface.slid[0])
                current_coulomb.extend(interface.slid_out_plan[:2])
                if any(
                    self._coulomb_rejection_reason(spring)
                    for spring in current_coulomb
                ):
                    return False
                requires_coulomb_rebuild = True
                validated.append((record_index, record, group, ()))
                continue
            layouts = (
                (int(self._slid_index[record_index]), interface.slid[0] if interface.slid else None),
                (old_oop0, interface.slid_out_plan[0] if len(interface.slid_out_plan) >= 1 else None),
                (old_oop1, interface.slid_out_plan[1] if len(interface.slid_out_plan) >= 2 else None),
            )
            for dense_index, spring in layouts:
                if dense_index < 0:
                    if spring is not None:
                        # Runtime coverage may grow after a material-only
                        # mutation, but only for laws the compiled interface
                        # Coulomb path already supports. Unsupported laws must
                        # keep the conservative full-runtime fallback.
                        if self._coulomb_rejection_reason(spring):
                            return False
                        requires_coulomb_rebuild = True
                    continue
                if spring is None:
                    requires_coulomb_rebuild = True
                    continue
                if self._coulomb_rejection_reason(spring):
                    return False
                candidates.append((dense_index, spring))
            validated.append((record_index, record, group, tuple(candidates)))

        # Validation above is intentionally complete before touching any dense
        # state.  A compact runtime can be promoted in place because the
        # mutation is constitutive-only: geometry, dense indices, afference and
        # every state array keep the same topology.  Promotion reconstructs the
        # historical 33-column values exactly from the current synchronized
        # spring objects, avoiding a full 500k+ spring runtime rebuild after
        # scour-material changes.
        if requires_full_parameter_storage:
            self._promote_transverse_parameter_storage()

        # The remaining operations are fixed-shape assignments from production
        # spring types and cannot change runtime topology.
        for record_index, record, group, candidates in validated:
            start = record.start
            for offset, spring in enumerate(group):
                dense_index = start + offset
                predecessor = self.springs[dense_index]
                if predecessor is not spring and hasattr(predecessor, "_histra_batch_managed"):
                    delattr(predecessor, "_histra_batch_managed")
                self.springs[dense_index] = spring
                self.managed_springs[dense_index] = spring
                spring._histra_batch_managed = True
                self._read_transverse_object(dense_index, spring)
                self._transverse_k[dense_index] = float(spring.k)

            if not requires_coulomb_rebuild:
                coulomb_offset = len(self.springs)
                for dense_index, spring in candidates:
                    predecessor = self.coulomb_springs[dense_index]
                    if predecessor is not spring and hasattr(predecessor, "_histra_batch_managed"):
                        delattr(predecessor, "_histra_batch_managed")
                    self.coulomb_springs[dense_index] = spring
                    self.managed_springs[coulomb_offset + dense_index] = spring
                    spring._histra_batch_managed = True
                    self.coulomb_params[dense_index, :] = (
                        float(spring.k), float(spring.h), float(spring.cohesion),
                        float(spring.mu), float(spring.area), float(spring.e1p),
                        float(spring.e2p),
                    )
                    self._read_coulomb_object(dense_index, spring)
                    self.coulomb_targets[dense_index] = float(spring.u)
                    self.coulomb_dns[dense_index] = 0.0
                    self.coulomb_enabled[dense_index] = bool(spring.is_on)

            # The interface object itself is retained by material mutation, so
            # the existing dense slice and record mapping remain valid.
            interface = record.interface
            interface._perf_hysteretic_batch = self
            interface._perf_hysteretic_slice = (record.start, record.stop)
            self._local_u[record_index, :] = interface.status.u[:12]

        if requires_coulomb_rebuild:
            self._rebuild_interface_coulomb_storage(
                changed_record_indices=frozenset(
                    record_index for record_index, _, _, _ in validated
                )
            )

        self._refresh_simple_hysteretic_flag()
        self._pending_values.fill(0.0)
        self._refresh_transverse_cache()
        self._refresh_full_force_cache()
        self._refresh_global_resisting_force_cache()
        self._refresh_max_u_cache()
        self._objects_trial_synced = True
        return True

    def performance_counts(self) -> dict[str, Any]:
        """Return stable production-backend coverage and rejection counters."""
        managed_quad_coulomb = sum(
            1 for row in self.quad_params
            if int(row[QPSUBLAW]) == QUAD_SUBLAW_COULOMB
        )
        managed_quad_cacovic = len(self.quad_records) - managed_quad_coulomb
        return {
            "managed_transverse_springs": len(self.springs),
            "transverse_parameter_columns": TRANSVERSE_PARAM_SIZE,
            "transverse_parameter_storage_columns": int(self._params.shape[1]),
            "compact_simple_hysteretic_params": bool(self._compact_simple_params),
            "managed_interface_coulomb_springs": len(self.coulomb_springs),
            "managed_quad_coulomb_springs": managed_quad_coulomb,
            "managed_quad_cacovic_springs": managed_quad_cacovic,
            "managed_coulomb_springs": len(self.coulomb_springs) + managed_quad_coulomb,
            "managed_quad_records": len(self.quad_records),
            "unmanaged_interfaces": len(self.unmanaged_interfaces),
            "unmanaged_quads": len(self.unmanaged_quads),
            "interface_rejection_reasons": dict(
                sorted(self.interface_rejection_reasons.items())
            ),
            "interface_coulomb_rejection_reasons": dict(
                sorted(self.interface_coulomb_rejection_reasons.items())
            ),
            "quad_rejection_reasons": dict(sorted(self.quad_rejection_reasons.items())),
        }

    def _read_quad_object(self, index: int, spring: Any) -> None:
        row = self.quad_state[index]
        row[QFY0], row[QFY1] = map(float, spring.fy[:2])
        row[QUMAX0], row[QUMAX1] = map(float, spring.umax[:2])
        row[QCROT_PU] = float(spring._crot_pu)
        row[QCROT_NU] = float(spring._crot_nu)
        row[QCROT_LIM_PU] = float(spring._crot_lim_pu)
        row[QCROT_LIM_NU] = float(spring._crot_lim_nu)
        row[QCROT_YP] = float(spring._crot_yp)
        row[QCROT_YN] = float(spring._crot_yn)
        row[QCMOM_MAX] = float(spring._cmom_max)
        row[QCMOM_MIN] = float(spring._cmom_min)
        row[QCLOAD] = int(spring._cload_indicator)
        row[QCPLAST_T] = float(bool(spring._cplastic_tension_indicator))
        row[QCPLAST_C] = float(bool(spring._cplastic_compression_indicator))
        row[QCUNLOAD_T] = int(spring._c_phase_unload_t)
        row[QCUNLOAD_C] = int(spring._c_phase_unload_c)
        row[QCUP] = float(spring._cup)
        row[QCENERGY] = float(spring.cenergy_d)
        row[QCSTRESS] = float(spring._cstress)
        row[QCSTRAIN] = float(spring._cstrain)
        row[QCSTRESS_NORMAL] = float(spring._cstress_normal)
        row[QCSTRESS_NORMAL_PREV] = float(spring._cstress_normal_prev)
        row[QCCONTACT] = float(spring._ccontact_area)
        row[QPHASE] = int(spring.phase)
        row[QTANG_RELOAD_T] = float(spring.tangent_reload_t)
        row[QTANG_RELOAD_C] = float(spring.tangent_reload_c)
        row[QKTANG_COMMITTED] = float(spring.k_tang_committed)
        row[QTROT_MAX] = float(spring._trot_max)
        row[QTROT_MIN] = float(spring._trot_min)
        row[QTROT_PU] = float(spring._trot_pu)
        row[QTROT_NU] = float(spring._trot_nu)
        row[QTROT_LIM_PU] = float(spring._trot_lim_pu)
        row[QTROT_LIM_NU] = float(spring._trot_lim_nu)
        row[QTROT_YP] = float(spring._trot_yp)
        row[QTROT_YN] = float(spring._trot_yn)
        row[QTMOM_MAX] = float(spring._tmom_max)
        row[QTMOM_MIN] = float(spring._tmom_min)
        row[QTLOAD] = int(spring._tload_indicator)
        row[QTPLAST_T] = float(bool(spring._tplastic_tension_indicator))
        row[QTPLAST_C] = float(bool(spring._tplastic_compression_indicator))
        row[QTUNLOAD_T] = int(spring._t_phase_unload_t)
        row[QTUNLOAD_C] = int(spring._t_phase_unload_c)
        row[QTENERGY] = float(spring._tenergy_d)
        row[QTUP] = float(spring._tup)
        row[QTSTRESS] = float(spring._tstress)
        row[QTSTRAIN] = float(spring._tstrain)
        row[QTSTRESS_NORMAL] = float(spring._tstress_normal)
        row[QTCONTACT] = float(spring._tcontact_area)
        row[QTPHASE] = int(spring.t_phase)
        row[QKTANG] = float(spring.k_tang)
        row[QMOM1P] = float(spring.mom1p)
        row[QROT1P] = float(spring.rot1p)
        row[QMOM2P] = float(spring.mom2p)
        row[QROT2P] = float(spring.rot2p)
        row[QMOM3P] = float(spring.mom3p)
        row[QROT3P] = float(spring.rot3p)
        row[QMOM1N] = float(spring.mom1n)
        row[QROT1N] = float(spring.rot1n)
        row[QMOM2N] = float(spring.mom2n)
        row[QROT2N] = float(spring.rot2n)
        row[QMOM3N] = float(spring.mom3n)
        row[QROT3N] = float(spring.rot3n)
        row[QUR0], row[QUR1] = map(float, spring.ur[:2])
        row[QDN] = float(spring.dn)

    def _write_quad_object(self, index: int, spring: Any) -> None:
        row = self.quad_state[index]
        spring.fy[:] = [float(row[QFY0]), float(row[QFY1])]
        spring.umax[:] = [float(row[QUMAX0]), float(row[QUMAX1])]
        spring._crot_pu = float(row[QCROT_PU])
        spring._crot_nu = float(row[QCROT_NU])
        spring._crot_lim_pu = float(row[QCROT_LIM_PU])
        spring._crot_lim_nu = float(row[QCROT_LIM_NU])
        spring._crot_yp = float(row[QCROT_YP])
        spring._crot_yn = float(row[QCROT_YN])
        spring._cmom_max = float(row[QCMOM_MAX])
        spring._cmom_min = float(row[QCMOM_MIN])
        spring._cload_indicator = int(row[QCLOAD])
        spring._cplastic_tension_indicator = bool(row[QCPLAST_T])
        spring._cplastic_compression_indicator = bool(row[QCPLAST_C])
        spring._c_phase_unload_t = _PHASE_BY_CODE[int(row[QCUNLOAD_T])]
        spring._c_phase_unload_c = _PHASE_BY_CODE[int(row[QCUNLOAD_C])]
        spring._cup = float(row[QCUP])
        spring.cenergy_d = float(row[QCENERGY])
        spring._cstress = float(row[QCSTRESS])
        spring._cstrain = float(row[QCSTRAIN])
        spring._cstress_normal = float(row[QCSTRESS_NORMAL])
        spring._cstress_normal_prev = float(row[QCSTRESS_NORMAL_PREV])
        spring._ccontact_area = float(row[QCCONTACT])
        spring.phase = _PHASE_BY_CODE[int(row[QPHASE])]
        spring.tangent_reload_t = float(row[QTANG_RELOAD_T])
        spring.tangent_reload_c = float(row[QTANG_RELOAD_C])
        spring.k_tang_committed = float(row[QKTANG_COMMITTED])
        spring._trot_max = float(row[QTROT_MAX])
        spring._trot_min = float(row[QTROT_MIN])
        spring._trot_pu = float(row[QTROT_PU])
        spring._trot_nu = float(row[QTROT_NU])
        spring._trot_lim_pu = float(row[QTROT_LIM_PU])
        spring._trot_lim_nu = float(row[QTROT_LIM_NU])
        spring._trot_yp = float(row[QTROT_YP])
        spring._trot_yn = float(row[QTROT_YN])
        spring._tmom_max = float(row[QTMOM_MAX])
        spring._tmom_min = float(row[QTMOM_MIN])
        spring._tload_indicator = int(row[QTLOAD])
        spring._tplastic_tension_indicator = bool(row[QTPLAST_T])
        spring._tplastic_compression_indicator = bool(row[QTPLAST_C])
        spring._t_phase_unload_t = _PHASE_BY_CODE[int(row[QTUNLOAD_T])]
        spring._t_phase_unload_c = _PHASE_BY_CODE[int(row[QTUNLOAD_C])]
        spring._tenergy_d = float(row[QTENERGY])
        spring._tup = float(row[QTUP])
        spring._tstress = float(row[QTSTRESS])
        spring._tstrain = float(row[QTSTRAIN])
        spring._tstress_normal = float(row[QTSTRESS_NORMAL])
        spring._tcontact_area = float(row[QTCONTACT])
        spring.t_phase = _PHASE_BY_CODE[int(row[QTPHASE])]
        spring.k_tang = float(row[QKTANG])
        spring.mom1p = float(row[QMOM1P])
        spring.rot1p = float(row[QROT1P])
        spring.mom2p = float(row[QMOM2P])
        spring.rot2p = float(row[QROT2P])
        spring.mom3p = float(row[QMOM3P])
        spring.rot3p = float(row[QROT3P])
        spring.mom1n = float(row[QMOM1N])
        spring.rot1n = float(row[QROT1N])
        spring.mom2n = float(row[QMOM2N])
        spring.rot2n = float(row[QROT2N])
        spring.mom3n = float(row[QMOM3N])
        spring.rot3n = float(row[QROT3N])
        spring.ur[:] = [float(row[QUR0]), float(row[QUR1])]
        spring.dn = float(row[QDN])
        spring.f = float(row[QCSTRESS])
        spring.u = float(row[QTSTRAIN])

    def _read_coulomb_object(self, index: int, spring: Any) -> None:
        row = self.coulomb_state[index]
        row[CFY0] = float(spring.fy[0])
        row[CFY1] = float(spring.fy[1])
        row[CCUP] = float(spring._cup)
        row[CCSTRESS] = float(spring._cstress)
        row[CCSTRAIN] = float(spring._cstrain)
        row[CCSTRESS_NORMAL] = float(spring._cstress_normal)
        row[CCSTRESS_NORMAL_PREV] = float(spring._cstress_normal_prev)
        row[CCCONTACT_AREA] = float(spring._ccontact_area)
        row[CCENERGY] = float(spring.cenergy_d)
        row[CCPHASE] = int(spring.phase)
        row[CTUP] = float(spring._tup)
        row[CTSTRESS] = float(spring._tstress)
        row[CTSTRAIN] = float(spring._tstrain)
        row[CTSTRESS_NORMAL] = float(spring._tstress_normal)
        row[CTCONTACT_AREA] = float(spring._tcontact_area)
        row[CTENERGY] = float(spring._tenergy_d)
        row[CTPHASE] = int(spring.t_phase)
        row[CKTANG] = float(spring.k_tang)
        row[CMOM1P] = float(spring.mom1p)
        row[CROT1P] = float(spring.rot1p)
        row[CMOM2P] = float(spring.mom2p)
        row[CROT2P] = float(spring.rot2p)
        row[CMOM1N] = float(spring.mom1n)
        row[CROT1N] = float(spring.rot1n)
        row[CMOM2N] = float(spring.mom2n)
        row[CROT2N] = float(spring.rot2n)
        row[CROT3N] = float(spring.rot3n)
        row[CROT3P] = float(spring.rot3p)
        row[CU] = float(spring.u)
        row[CF] = float(spring.f)
        row[CKTANG_COMMITTED] = float(spring.k_tang_committed)
        row[CDN] = float(spring.dn)

    def _write_coulomb_object(self, index: int, spring: Any) -> None:
        row = self.coulomb_state[index]
        spring.fy[0] = float(row[CFY0])
        spring.fy[1] = float(row[CFY1])
        spring._cup = float(row[CCUP])
        spring._cstress = float(row[CCSTRESS])
        spring._cstrain = float(row[CCSTRAIN])
        spring._cstress_normal = float(row[CCSTRESS_NORMAL])
        spring._cstress_normal_prev = float(row[CCSTRESS_NORMAL_PREV])
        spring._ccontact_area = float(row[CCCONTACT_AREA])
        spring.cenergy_d = float(row[CCENERGY])
        spring.phase = _PHASE_BY_CODE[int(row[CCPHASE])]
        spring._tup = float(row[CTUP])
        spring._tstress = float(row[CTSTRESS])
        spring._tstrain = float(row[CTSTRAIN])
        spring._tstress_normal = float(row[CTSTRESS_NORMAL])
        spring._tcontact_area = float(row[CTCONTACT_AREA])
        spring._tenergy_d = float(row[CTENERGY])
        spring.t_phase = _PHASE_BY_CODE[int(row[CTPHASE])]
        spring.k_tang = float(row[CKTANG])
        spring.mom1p = float(row[CMOM1P])
        spring.rot1p = float(row[CROT1P])
        spring.mom2p = float(row[CMOM2P])
        spring.rot2p = float(row[CROT2P])
        spring.mom1n = float(row[CMOM1N])
        spring.rot1n = float(row[CROT1N])
        spring.mom2n = float(row[CMOM2N])
        spring.rot2n = float(row[CROT2N])
        spring.rot3n = float(row[CROT3N])
        spring.rot3p = float(row[CROT3P])
        spring.u = float(row[CU])
        spring.f = float(row[CF])
        spring.k_tang_committed = float(row[CKTANG_COMMITTED])
        spring.dn = float(row[CDN])

    def _sync_interface_status_to_objects(self) -> None:
        for index, record in enumerate(self.records):
            record.interface.status.u[:12] = self._local_u[index].tolist()
            record.interface.status.normal_increment = float(self._normal_increments[index])
            record.interface.status.committed_normal_force = float(self._committed_forces[index])
            record.interface.status.max_spring_displacement = float(self._max_displacements[index])

    def prepare(self, x: np.ndarray) -> None:
        """Map one global Newton increment to all batched spring strains."""
        _map_global_to_local(
            x, self._aff_offsets, self._aff_gdls, self._aff_coefficients,
            self._local_du,
        )
        _prepare_interface_kinematics(
            self._local_du, self._local_u, self._lengths, self._constrained,
            self._d0s, self._d1s, self._num, self._num2, self._delta_flex,
            self._pending_values,
        )

        indices = self._record_index
        self.targets[:] = self.trial[:, 7] + (
            (self._num[indices] * self._dj + self._num2[indices] * self._di)
            / self._lengths[indices]
            - self._delta_flex[indices] * self._ecc
        )

    def evaluate(self) -> None:
        evaluator = (
            _evaluate_simple_linear_batch
            if self._simple_hysteretic
            else _evaluate_linear_batch
        )
        evaluator(
            self._params, self.committed, self.trial, self.targets, self.enabled
        )
        self._objects_trial_synced = False

    def _refresh_transverse_cache(self) -> None:
        _finish_transverse_batch(
            self.trial, self.committed, self._di, self._dj, self._ecc,
            self._lengths, self._starts, self._stops, self._constrained,
            self._local_forces, self._normal_increments,
            self._committed_forces, self._max_displacements,
        )

    def finish(self) -> None:
        self._refresh_transverse_cache()
        if self.coulomb_springs:
            _advance_interface_coulomb_targets(
                self._pending_values, self._dist_for, self._normal_increments,
                self._slid_index, self._oop0_index, self._oop1_index,
                self.coulomb_targets, self.coulomb_dns,
            )
            _evaluate_initial_coulomb_batch(
                self.coulomb_params, self.coulomb_state,
                self.coulomb_targets, self.coulomb_dns, self.coulomb_enabled,
            )
        self._refresh_full_force_cache()
        # Keep the compact status values visible to Quad.ComputeDN and the
        # convergence/max-displacement checks.  Full local U and spring object
        # states are synchronized only at committed steps or snapshots.
        for record_index, record in enumerate(self.records):
            interface = record.interface
            interface.status.normal_increment = float(self._normal_increments[record_index])
            interface.status.committed_normal_force = float(self._committed_forces[record_index])
            interface.status.max_spring_displacement = float(self._max_displacements[record_index])

    def update_domain(self, x: np.ndarray, state: Any) -> None:
        """Evaluate all managed interfaces and Quads.

        The constitutive work is split into compiled kernels rather than
        wrapped in one outer Numba dispatcher.  That allows Numba's parallel
        scheduler to execute the independent transverse-fibre and per-interface
        loops concurrently.  The call sequence and every within-spring /
        within-interface accumulation order remain identical to the original
        fused implementation.
        """
        _map_global_to_local(
            x, self._aff_offsets, self._aff_gdls, self._aff_coefficients,
            self._local_du,
        )
        _prepare_interface_kinematics(
            self._local_du, self._local_u, self._lengths, self._constrained,
            self._d0s, self._d1s, self._num, self._num2, self._delta_flex,
            self._pending_values,
        )
        if self._simple_hysteretic:
            _advance_and_evaluate_simple_linear_batch(
                self._params, self.committed, self.trial, self.targets, self.enabled,
                self._record_index, self._num, self._num2, self._di, self._dj,
                self._lengths, self._delta_flex, self._ecc,
            )
        else:
            _advance_transverse_targets(
                self.trial, self._record_index, self._num, self._num2, self._di,
                self._dj, self._lengths, self._delta_flex, self._ecc, self.targets,
            )
            _evaluate_linear_batch(
                self._params, self.committed, self.trial, self.targets, self.enabled
            )
        _finish_transverse_batch(
            self.trial, self.committed, self._di, self._dj, self._ecc,
            self._lengths, self._starts, self._stops, self._constrained,
            self._local_forces, self._normal_increments,
            self._committed_forces, self._max_displacements,
        )
        if self.coulomb_targets.size:
            _advance_interface_coulomb_targets(
                self._pending_values, self._dist_for, self._normal_increments,
                self._slid_index, self._oop0_index, self._oop1_index,
                self.coulomb_targets, self.coulomb_dns,
            )
            _evaluate_initial_coulomb_batch(
                self.coulomb_params, self.coulomb_state, self.coulomb_targets,
                self.coulomb_dns, self.coulomb_enabled,
            )
        _assemble_full_interface_forces(
            self._local_forces, self.coulomb_state, self._slid_index,
            self._oop0_index, self._oop1_index, self._dist,
            self._local_full_forces, self._max_displacements,
            self.coulomb_targets,
        )

        if self._quad_local_du.shape[0]:
            _map_global_to_local(
                x, self._quad_aff_offsets, self._quad_aff_gdls,
                self._quad_aff_coefficients, self._quad_local_du,
            )
            _prepare_quad_kinematics(
                self._quad_local_du, self._quad_local_u,
                self._quad_edge_offsets, self._quad_edge_records,
                self._quad_edge_areas, self._normal_increments,
                self._committed_forces, self._quad_d_alfa,
                int(getattr(state, "step", 0)), self._quad_sigma_initial,
                self._quad_strains, self._quad_dns,
            )
            _evaluate_quad_takeda_batch(
                self.quad_params, self.quad_state, self._quad_strains,
                self._quad_dns, self._quad_volumes, self._quad_sigma_initial,
            )
        _refresh_global_resisting_force(
            self._quad_d_alfa, self.quad_state, self._quad_forces,
            self._quad_force_offsets, self._quad_force_gdls,
            self._quad_force_coefficients, self._local_full_forces,
            self._aff_offsets, self._aff_gdls, self._aff_coefficients,
            self._global_resisting_force,
        )
        _refresh_max_u_cache(
            self._quad_local_u, self._max_displacements, self._max_u_cache
        )
        self._objects_trial_synced = False

    def update_quads(self, x: np.ndarray, state: Any) -> None:
        if not self.quad_records:
            return
        _map_global_to_local(
            x, self._quad_aff_offsets, self._quad_aff_gdls,
            self._quad_aff_coefficients, self._quad_local_du,
        )
        _prepare_quad_kinematics(
            self._quad_local_du, self._quad_local_u,
            self._quad_edge_offsets, self._quad_edge_records,
            self._quad_edge_areas, self._normal_increments,
            self._committed_forces, self._quad_d_alfa,
            int(getattr(state, "step", 0)), self._quad_sigma_initial,
            self._quad_strains, self._quad_dns,
        )
        _evaluate_quad_takeda_batch(
            self.quad_params, self.quad_state,
            self._quad_strains, self._quad_dns,
            self._quad_volumes, self._quad_sigma_initial,
        )
        for index, quad in enumerate(self.quad_records):
            quad.status.u[:7] = self._quad_local_u[index].tolist()
            quad.sigma_initial = float(self._quad_sigma_initial[index])
            # Keep the tangent visible to any analysis method that explicitly
            # asks Quad.compute_k for an updated stiffness.  The complete
            # constitutive object is synchronized only at commits/restores.
            quad.spring.k_tang = float(self.quad_state[index, QKTANG])

    def manages_quad(self, quad: Any) -> bool:
        return id(quad) in self.quad_ids

    def _refresh_full_force_cache(self) -> None:
        _assemble_full_interface_forces(
            self._local_forces, self.coulomb_state,
            self._slid_index, self._oop0_index, self._oop1_index,
            self._dist, self._local_full_forces, self._max_displacements,
            self.coulomb_targets,
        )

    def _refresh_global_resisting_force_cache(self) -> None:
        _refresh_global_resisting_force(
            self._quad_d_alfa, self.quad_state, self._quad_forces,
            self._quad_force_offsets, self._quad_force_gdls,
            self._quad_force_coefficients, self._local_full_forces,
            self._aff_offsets, self._aff_gdls, self._aff_coefficients,
            self._global_resisting_force,
        )

    def _refresh_max_u_cache(self) -> None:
        _refresh_max_u_cache(
            self._quad_local_u, self._max_displacements, self._max_u_cache
        )

    def copy_resisting_force_to(self, destination: np.ndarray) -> None:
        destination[:] = self._global_resisting_force

    def scatter_quad_resisting_force(self, global_force: np.ndarray) -> None:
        for index, quad in enumerate(self.quad_records):
            force = float(self._quad_d_alfa[index] * self.quad_state[index, QTSTRESS])
            quad.status.f = force
            self._quad_forces[index, 0] = force
        _scatter_local_forces(
            self._quad_forces, self._quad_force_offsets,
            self._quad_force_gdls, self._quad_force_coefficients,
            global_force,
        )

    def scatter_resisting_force(self, global_force: np.ndarray) -> None:
        _scatter_local_forces(
            self._local_full_forces, self._aff_offsets, self._aff_gdls,
            self._aff_coefficients, global_force,
        )

    def cached_max_u(self) -> tuple[float, int, str]:
        value = float(self._max_u_cache[0])
        index = int(self._max_u_cache[1])
        kind = int(self._max_u_cache[2])
        if kind == 1 and 0 <= index < len(self.quad_records):
            return value, int(self.quad_records[index].key), "Quad"
        if kind == 2 and 0 <= index < len(self.records):
            return value, int(self.records[index].interface.key), "Interface"
        return value, 0, ""

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
            spring.t_phase = _PHASE_BY_CODE[int(row[8])]
            spring.k_tang = float(row[9])
            spring.f = spring._tstress
            spring.u = spring._tstrain

        record_index = self._record_by_id[id(interface)]
        for spring_index in (
            int(self._slid_index[record_index]),
            int(self._oop0_index[record_index]),
            int(self._oop1_index[record_index]),
        ):
            if spring_index >= 0:
                self._write_coulomb_object(
                    spring_index, self.coulomb_springs[spring_index]
                )
        interface.status.u[:12] = self._local_u[record_index].tolist()

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

    def sync_all_to_objects(self) -> None:
        """Publish the authoritative dense state to the compatibility objects."""
        for i, spring in enumerate(self.springs):
            committed = self.committed[i]
            trial = self.trial[i]
            spring.umax[0] = float(committed[0])
            spring.umax[1] = float(committed[1])
            spring._crot_pu = float(committed[2])
            spring._crot_nu = float(committed[3])
            spring.cenergy_d = float(committed[4])
            spring._cload_indicator = int(committed[5])
            spring._cstress = float(committed[6])
            spring._cstrain = float(committed[7])
            spring.phase = _PHASE_BY_CODE[int(committed[8])]
            spring._trot_max = float(trial[0])
            spring._trot_min = float(trial[1])
            spring._trot_pu = float(trial[2])
            spring._trot_nu = float(trial[3])
            spring._tenergy_d = float(trial[4])
            spring._tload_indicator = int(trial[5])
            spring._tstress = float(trial[6])
            spring._tstrain = float(trial[7])
            spring.t_phase = _PHASE_BY_CODE[int(trial[8])]
            spring.k_tang = float(trial[9])
            spring.k_tang_committed = float(trial[9])
            spring.f = float(trial[6])
            spring.u = float(trial[7])
        for i, spring in enumerate(self.coulomb_springs):
            self._write_coulomb_object(i, spring)
        for i, quad in enumerate(self.quad_records):
            self._write_quad_object(i, quad.spring)
            quad.status.u[:7] = self._quad_local_u[i].tolist()
            quad.status.f = float(self._quad_forces[i, 0])
            quad.sigma_initial = float(self._quad_sigma_initial[i])
        self._sync_interface_status_to_objects()
        self._objects_trial_synced = True

    def compute_energy(self) -> tuple[float, float]:
        """Return the same managed elastic/plastic totals as element scans."""
        return (
            float(
                _managed_elastic_energy(
                    self._transverse_k,
                    self.trial,
                    self._quad_k,
                    self.quad_state,
                )
            ),
            0.0,
        )

    def commit(self, *, sync_objects: bool = False) -> None:
        if self.quad_records:
            _commit_quad_takeda_batch(self.quad_params, self.quad_state)
        self.committed[:, 0] = self.trial[:, 0]
        self.committed[:, 1] = self.trial[:, 1]
        self.committed[:, 2] = self.trial[:, 2]
        self.committed[:, 3] = self.trial[:, 3]
        self.committed[:, 4] = self.trial[:, 4]
        self.committed[:, 5] = self.trial[:, 5]
        self.committed[:, 6] = self.trial[:, 6]
        self.committed[:, 7] = self.trial[:, 7]
        self.committed[:, 8] = self.trial[:, 8]
        if self.coulomb_springs:
            _commit_initial_coulomb_batch(
                self.coulomb_state, self.coulomb_enabled
            )
            self.coulomb_targets[:] = self.coulomb_state[:, CU]
        self._sync_interface_status_to_objects()
        self._objects_trial_synced = False
        if sync_objects:
            self.sync_all_to_objects()

    def snapshot(self) -> tuple[np.ndarray, ...]:
        return (
            self.committed.copy(), self.trial.copy(), self.targets.copy(),
            self.coulomb_state.copy(), self.coulomb_targets.copy(),
            self.coulomb_dns.copy(), self._local_u.copy(),
            self._quad_local_u.copy(), self._quad_sigma_initial.copy(),
            self.quad_state.copy(),
        )

    def restore(self, state: tuple[np.ndarray, ...]) -> None:
        (
            committed, trial, targets, coulomb_state, coulomb_targets,
            coulomb_dns, local_u, quad_local_u, quad_sigma_initial,
            quad_state,
        ) = state
        self.committed[...] = committed
        self.trial[...] = trial
        self.targets[...] = targets
        self.coulomb_state[...] = coulomb_state
        self.coulomb_targets[...] = coulomb_targets
        self.coulomb_dns[...] = coulomb_dns
        self._local_u[...] = local_u
        self._quad_local_u[...] = quad_local_u
        self._quad_sigma_initial[...] = quad_sigma_initial
        self.quad_state[...] = quad_state
        self._pending_values.fill(0.0)
        self._refresh_transverse_cache()
        self._objects_trial_synced = False
        self.sync_trial_to_objects()
        for index, quad in enumerate(self.quad_records):
            quad.status.u[:7] = self._quad_local_u[index].tolist()
            quad.sigma_initial = float(self._quad_sigma_initial[index])
            self._write_quad_object(index, quad.spring)
        self._refresh_full_force_cache()
        self._refresh_global_resisting_force_cache()
        self._refresh_max_u_cache()

    def revert_quad(self, quad: Any) -> None:
        index = int(quad.spring._histra_quad_batch_index)
        row = self.quad_state[index]
        _quad_revert_trial(row)
        # Preserve the C# ordering in Quad.revertToLastCommit: trial normal
        # stress is restored first, then committed normal stress rolls back to
        # its previous committed value.
        row[QCSTRESS_NORMAL] = row[QCSTRESS_NORMAL_PREV]
        self._write_quad_object(index, quad.spring)

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
        record_index = self._record_by_id[id(interface)]
        for spring_index in (
            int(self._slid_index[record_index]),
            int(self._oop0_index[record_index]),
            int(self._oop1_index[record_index]),
        ):
            if spring_index < 0:
                continue
            spring = self.coulomb_springs[spring_index]
            # Use the object's exact C# lifecycle implementation for this rare
            # rollback path, then refresh the dense representation.
            self._write_coulomb_object(spring_index, spring)
            spring.revert_to_last_commit()
            self._read_coulomb_object(spring_index, spring)
            self.coulomb_targets[spring_index] = float(spring._cstrain)
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
