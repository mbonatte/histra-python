from __future__ import annotations
import math
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple
from histra.types.phase_enum import PhaseEnum
from histra.types.xml_utils import _attr
from histra.types.hysteretic_curve_types import (
    HystereticTensileCurveTypeEnum,
    HystereticCompressiveCurveTypeEnum,
)
from histra.springs.base import Spring
from histra.springs.registry import _register_spring


@_register_spring("HiStrA.Objects.SpringCoulomb03")
@dataclass(slots=True)
class SpringCoulomb03(Spring):
    """Coulomb friction spring type 03 — direct port of C# SpringCoulomb03.

    Full Takeda hysteretic state machine with Coulomb (or Cacovic) yielding.
    """
    # -------------------------------------------------------------------
    # Serialised scalar parameters  (XML attributes)
    # -------------------------------------------------------------------
    check_contact_area: bool = False
    sub_law: str = "Coulomb"
    hysteretic_type: str = "Takeda"
    cohesion: float = 0.0
    mu: float = 0.0

    @property
    def c(self) -> float:
        return self.cohesion

    @c.setter
    def c(self, val: float) -> None:
        self.cohesion = val

    @property
    def kt(self) -> float:
        return self.k_tang

    @kt.setter
    def kt(self, val: float) -> None:
        self.k_tang = val
    plastic_strain_ratio: float = 0.0
    plastic_stiffness_ratio: float = 0.0001
    max_tensile_ratio: float = 0.8
    reload_stiffness_ratio: float = 1.0
    bcacovic: float = 0.0

    # -------------------------------------------------------------------
    # Backbone envelope points
    # -------------------------------------------------------------------
    mom1p: float = 0.0
    rot1p: float = 0.0
    mom2p: float = 0.0
    rot2p: float = 0.0
    mom3p: float = 0.0
    rot3p: float = 0.0
    mom1n: float = 0.0
    rot1n: float = 0.0
    mom2n: float = 0.0
    rot2n: float = 0.0
    mom3n: float = 0.0
    rot3n: float = 0.0

    # -------------------------------------------------------------------
    # Envelope slopes  (set by _set_envelope)
    # -------------------------------------------------------------------
    e1p: float = 0.0
    e2p: float = 0.0
    e3p: float = 0.0
    e1n: float = 0.0
    e2n: float = 0.0
    e3n: float = 0.0
    eup: float = 0.0
    eun: float = 0.0

    # -------------------------------------------------------------------
    # Energy  (envelope area)
    # -------------------------------------------------------------------
    energy_a: float = 0.0

    # -------------------------------------------------------------------
    # Array-backed state
    # -------------------------------------------------------------------
    fy: list = field(default_factory=lambda: [0.0, 0.0])
    ur: list = field(default_factory=lambda: [0.0, 0.0])
    umax: list = field(default_factory=lambda: [0.0, 0.0])   # [0]=CrotMax, [1]=CrotMin

    # -------------------------------------------------------------------
    # Committed state  (C prefix in C#)
    # -------------------------------------------------------------------
    _cstress: float = 0.0
    _cstrain: float = 0.0
    _cstress_normal: float = 0.0
    _cstress_normal_prev: float = 0.0
    _ccontact_area: float = 0.0
    _crot_pu: float = 0.0
    _crot_nu: float = 0.0
    _crot_lim_pu: float = 0.0
    _crot_lim_nu: float = 0.0
    _crot_yp: float = 0.0
    _crot_yn: float = 0.0
    _cmom_max: float = 0.0
    _cmom_min: float = 0.0
    _cload_indicator: int = 0
    _cplastic_tension_indicator: bool = False
    _cplastic_compression_indicator: bool = False
    _c_phase_unload_t: int = 0      # PhaseEnum.Elastic
    _c_phase_unload_c: int = 0
    _cup: float = 0.0
    cenergy_d: float = 0.0

    # -------------------------------------------------------------------
    # Trial state  (T prefix in C#)
    # -------------------------------------------------------------------
    _tstress: float = 0.0
    _tstrain: float = 0.0
    _tstress_normal: float = 0.0
    _tcontact_area: float = 0.0
    _trot_max: float = 0.0
    _trot_min: float = 0.0
    _trot_pu: float = 0.0
    _trot_nu: float = 0.0
    _trot_lim_pu: float = 0.0
    _trot_lim_nu: float = 0.0
    _trot_yp: float = 0.0
    _trot_yn: float = 0.0
    _tmom_max: float = 0.0
    _tmom_min: float = 0.0
    _tload_indicator: int = 0
    _tplastic_tension_indicator: bool = False
    _tplastic_compression_indicator: bool = False
    _t_phase_unload_t: int = 0
    _t_phase_unload_c: int = 0
    _tenergy_d: float = 0.0
    _tup: float = 0.0

    # -------------------------------------------------------------------
    # Misc
    # -------------------------------------------------------------------
    dn: float = 0.0
    area_corrente: float = 0.0
    k_tang_committed: float = 0.0
    _tangent_reload_t: float = 0.0
    _tangent_reload_c: float = 0.0
    phase: int = 0     # PhaseEnum.Elastic  (committed)
    t_phase: int = 0   # PhaseEnum.Elastic  (trial)

    # C# SpringCoulomb03 does not expose the raw stored reload tangent.
    # Its TangentReload_t/c getters enforce a lower bound of 0.0001 * K.
    # Keeping that behaviour is essential because the Takeda state machine
    # divides by these values while resolving yielding displacements.
    @property
    def tangent_reload_t(self) -> float:
        return max(1.0e-4 * self.k, self._tangent_reload_t)

    @tangent_reload_t.setter
    def tangent_reload_t(self, value: float) -> None:
        self._tangent_reload_t = value

    @property
    def tangent_reload_c(self) -> float:
        return max(1.0e-4 * self.k, self._tangent_reload_c)

    @tangent_reload_c.setter
    def tangent_reload_c(self, value: float) -> None:
        self._tangent_reload_c = value

    # ===================================================================
    # XML construction
    # ===================================================================

    @classmethod
    def _from_xml(cls, elem: ET.Element, type_of: str = "") -> SpringCoulomb03:
        inst = super(SpringCoulomb03, cls)._from_xml(elem, type_of)
        inst.check_contact_area = _attr(elem, "CheckContactArea", False, lambda v: str(v).lower() == "true")
        inst.sub_law = _attr(elem, "SubLaw", "Coulomb")
        inst.hysteretic_type = _attr(elem, "HystereticType", "Takeda")
        inst.cohesion = _attr(elem, "C", 0.0, float) or _attr(elem, "Fy_0", 0.0, float)
        inst.mu = _attr(elem, "Mu", 0.0, float)
        inst.plastic_strain_ratio = _attr(elem, "PlasticStrainRatio", 0.0, float)
        inst.plastic_stiffness_ratio = _attr(elem, "PlasticStiffnessRatio", 0.0001, float)
        inst.max_tensile_ratio = _attr(elem, "MaxTensileRatio", 0.8, float)
        inst.reload_stiffness_ratio = _attr(elem, "ReloadStiffnessRatio", 1.0, float)
        inst.bcacovic = _attr(elem, "Bcacovic", 0.0, float)
        inst.mom1p = _attr(elem, "Mom1p", 0.0, float)
        inst.rot1p = _attr(elem, "Rot1p", 0.0, float)
        inst.mom2p = _attr(elem, "Mom2p", 0.0, float)
        inst.rot2p = _attr(elem, "Rot2p", 0.0, float)
        inst.mom3p = _attr(elem, "Mom3p", 0.0, float)
        inst.rot3p = _attr(elem, "Rot3p", 0.0, float)
        inst.mom1n = _attr(elem, "Mom1n", 0.0, float)
        inst.rot1n = _attr(elem, "Rot1n", 0.0, float)
        inst.mom2n = _attr(elem, "Mom2n", 0.0, float)
        inst.rot2n = _attr(elem, "Rot2n", 0.0, float)
        inst.mom3n = _attr(elem, "Mom3n", 0.0, float)
        inst.rot3n = _attr(elem, "Rot3n", 0.0, float)
        inst.e1p = _attr(elem, "E1p", inst.k, float)
        inst.e2p = _attr(elem, "E2p", 0.0, float)
        inst.e3p = _attr(elem, "E3p", 0.0, float)
        inst.e1n = _attr(elem, "E1n", inst.k, float)
        inst.e2n = _attr(elem, "E2n", 0.0, float)
        inst.e3n = _attr(elem, "E3n", 0.0, float)
        inst.eup = _attr(elem, "Eup", 0.0, float)
        inst.eun = _attr(elem, "Eun", 0.0, float)
        inst.energy_a = _attr(elem, "EnergyA", 0.0, float)
        inst.fy = [_attr(elem, "Fy1", 0.0, float), _attr(elem, "Fy2", 0.0, float)]
        inst.ur = [_attr(elem, "Ur1", 0.0, float), _attr(elem, "Ur2", 0.0, float)]
        inst._set_envelope()
        inst.revert_to_start()
        inst.revert_to_last_commit()
        return inst

    # ===================================================================
    # Envelope helpers
    # ===================================================================

    def _set_envelope(self) -> None:
        """Compute envelope slopes from backbone points (C# setEnvelope)."""
        if self.rot1p != 0.0:
            self.e1p = self.mom1p / self.rot1p
        if self.rot2p - self.rot1p != 0.0:
            self.e2p = (self.mom2p - self.mom1p) / (self.rot2p - self.rot1p)
        if self.rot3p - self.rot2p != 0.0:
            self.e3p = (self.mom3p - self.mom2p) / (self.rot3p - self.rot2p)
        if self.rot1n != 0.0:
            self.e1n = self.mom1n / self.rot1n
        if self.rot2n - self.rot1n != 0.0:
            self.e2n = (self.mom2n - self.mom1n) / (self.rot2n - self.rot1n)
        if self.rot3n - self.rot2n != 0.0:
            self.e3n = (self.mom3n - self.mom2n) / (self.rot3n - self.rot2n)
        self.eup = max(self.e1p, self.e2p, self.e3p)
        # C# setEnvelope selects the numerically largest negative-side slope.
        # The slopes are generally positive secants/tangents despite belonging
        # to the negative envelope; using min() selected the soft descending
        # branch and corrupted Takeda unloading/reloading after a restart.
        self.eun = max(self.e1n, self.e2n, self.e3n)

    def _tau_limite(self, N: float, ratio_cohesion: float = 1.0) -> float:
        """Coulomb or Cacovic limiting shear stress (C# TauLimite)."""
        c = self.cohesion * ratio_cohesion
        if self.sub_law == "Coulomb":
            return max(0.0, c + self.mu * N)
        elif self.sub_law == "Cacovic":
            val = 1.0 + N / (1.5 * c)
            if val < 0.0:
                return 0.0
            return 1.5 / self.bcacovic * c * math.sqrt(val)
        return 0.0

    @property
    def h(self) -> float:
        """Hardening modulus (C# H = E1p*E2p/(E1p - E2p))."""
        if self.e1p == 0.0:
            self._set_envelope()
        denom = self.e1p - self.e2p
        if denom == 0.0:
            return 0.0
        return self.e1p * self.e2p / denom

    # ===================================================================
    # Envelope stress / tangent  (Takeda type)
    # ===================================================================

    def _pos_envlp_stress_takeda(self, strain: float) -> float:
        """Positive envelope stress (C# posEnvlpStressTakeda)."""
        if self.hysteretic_type == "Initial":
            return min(self.mom1p, self._cstress + self.e1p * (self._tstrain - self._cstrain))
        # Takeda
        yp = self._trot_yp if self._tplastic_tension_indicator else self.rot1p
        if strain < yp:
            return self.e1p * strain
        if strain <= self.rot2p:
            return self.mom1p + self.e2p * (strain - yp)
        if strain <= self.rot3p:
            return self.mom2p + self.e3p * (strain - self.rot2p)
        return self.mom3p

    def _neg_envlp_stress_takeda(self, strain: float) -> float:
        """Negative envelope stress (C# negEnvlpStressTakeda)."""
        if self.hysteretic_type == "Initial":
            return max(self.mom1n, self._cstress + self.e1n * (self._tstrain - self._cstrain))
        yn = self._trot_yn if self._tplastic_compression_indicator else self.rot1n
        if strain > yn:
            return self.e1n * strain
        if strain >= self.rot2n:
            return self.mom1n + self.e2n * (strain - yn)
        if strain >= self.rot3n:
            return self.mom2n + self.e3n * (strain - self.rot2n)
        return self.mom3n

    def _pos_envlp_tangent_takeda(self, strain: float) -> float:
        """Positive envelope tangent, sets t_phase based on branch (C# posEnvlpTangentTakeda)."""
        yp = self._trot_yp if self._tplastic_tension_indicator else self.rot1p
        if strain < yp:
            self.t_phase = PhaseEnum.Elastic
            return self.e1p
        if strain <= self.rot2p:
            self.t_phase = PhaseEnum.Plastic_t
            return self.e2p
        if strain <= self.rot3p:
            self.t_phase = PhaseEnum.Plastic_t
            return self.e3p
        self.t_phase = PhaseEnum.RuptureTraz
        return self.e1p * 1e-09

    def _neg_envlp_tangent_takeda(self, strain: float) -> float:
        """Negative envelope tangent, sets t_phase (C# negEnvlpTangentTakeda)."""
        pu = self._trot_pu
        yn = self._trot_yn if self._t_phase_unload_c != PhaseEnum.Elastic else self.rot1n
        if strain > pu:
            return self.e1n * 1e-09
        if strain > yn:
            self.t_phase = PhaseEnum.Elastic
            return self.e1n
        if strain >= self.rot2n:
            self.t_phase = PhaseEnum.Plastic_c
            return self.e2n
        if strain >= self.rot3n:
            self.t_phase = PhaseEnum.Plastic_c
            return self.e3n
        self.t_phase = PhaseEnum.RuptureComp
        return self.e1n * 1e-09

    # ===================================================================
    # Yielding displacement helpers
    # ===================================================================

    def _get_current_yielding_displacement_tension(self, phase_unload: int, dstrain: float) -> float:
        """C# GetCurrentYieldingDisplacementTension."""
        if not self._tplastic_tension_indicator:
            num2 = self.mom1p
            num3 = self.rot1p
        else:
            num2 = self._cmom_max
            num3 = self.umax[0]   # CrotMax

        if dstrain < 0.0:
            return num3

        if self.t_phase == PhaseEnum.Slip:
            return self._trot_max
        if self.t_phase in (PhaseEnum.Elastic, PhaseEnum.Plastic_t):
            return self.umax[0]
        if self.t_phase == PhaseEnum.Plastic_c:
            if phase_unload == PhaseEnum.Elastic:
                return num3
            if phase_unload in (PhaseEnum.Plastic_t, PhaseEnum.Reload_t):
                num4 = self._cstrain - self._cstress / self.e1n
                num5 = self.tangent_reload_t if num2 <= 0.0 else num2 / (num3 - num4)
                return self.mom1p / num5 + num4
        if self.t_phase == PhaseEnum.Unload_t:
            if phase_unload == PhaseEnum.Elastic:
                return num3
            if phase_unload == PhaseEnum.Plastic_t:
                return self._trot_pu + self.mom1p / self.e1p
            if phase_unload == PhaseEnum.Reload_t:
                if self._tstrain < self._trot_lim_pu:
                    return self._trot_pu + self.mom1p / self.e1p
                else:
                    return self._trot_nu + self.mom1p / self.tangent_reload_t
        if self.t_phase == PhaseEnum.Unload_c:
            if phase_unload == PhaseEnum.Elastic:
                return num3
            if phase_unload in (PhaseEnum.Plastic_t, PhaseEnum.Reload_t):
                num5 = self.tangent_reload_t if num2 <= 0.0 else num2 / (num3 - self._trot_nu)
                return self._trot_nu + self.mom1p / num5
        if self.t_phase == PhaseEnum.Reload_t:
            if phase_unload in (PhaseEnum.Elastic, PhaseEnum.Reload_t):
                num5 = self.tangent_reload_t
                num = self._trot_nu + self.mom1p / num5
                if self.e3p < 0.0:
                    val = (self._trot_nu * num5 - self.rot3p * self.e3p) / (num5 - self.e3p)
                    num = min(num, val)
                return num
        if self.t_phase == PhaseEnum.Reload_c:
            if phase_unload == PhaseEnum.Elastic:
                return num3
            if phase_unload == PhaseEnum.Plastic_t:
                num4 = self._cstrain - self._cstress / self.e1n
                num5 = self.tangent_reload_t if num2 <= 0.0 else num2 / (num3 - num4)
                return num4 + self.mom1p / num5
            if phase_unload == PhaseEnum.Reload_t:
                if self._t_phase_unload_c == PhaseEnum.Reload_c:
                    num4 = self._cstrain - self._cstress / self.e1n
                    num5 = self.tangent_reload_t if num2 <= 0.0 else num2 / (num3 - num4)
                    return self._trot_nu + self.mom1p / num5
                else:
                    return self._trot_nu + self.mom1p / self.tangent_reload_t
        return num3

    def _get_current_yielding_displacement_compression(self, phase_unload: int, dstrain: float) -> float:
        """C# GetCurrentYieldingDisplacementCompression."""
        if not self._tplastic_compression_indicator:
            num2 = self.mom1n
            num3 = self.rot1n
        else:
            num2 = self._cmom_min
            num3 = self.umax[1]   # CrotMin

        if dstrain > 0.0:
            return num3

        if self.t_phase == PhaseEnum.Slip:
            return self._trot_min
        if self.t_phase in (PhaseEnum.Elastic, PhaseEnum.Plastic_c):
            return self.umax[1]
        if self.t_phase == PhaseEnum.Plastic_t:
            if phase_unload == PhaseEnum.Elastic:
                return num3
            if phase_unload in (PhaseEnum.Plastic_c, PhaseEnum.Reload_c):
                num4 = self._cstrain - self._cstress / self.e1p
                tc = self.tangent_reload_c if num2 == 0.0 else num2 / (num3 - num4)
                return self.mom1n / tc + num4
        if self.t_phase == PhaseEnum.Unload_t:
            if phase_unload in (PhaseEnum.Elastic,):
                return num3
            if phase_unload in (PhaseEnum.Plastic_c, PhaseEnum.Reload_c):
                tc = self.tangent_reload_c if num2 == 0.0 else num2 / (num3 - self._trot_pu)
                return self._trot_pu + self.mom1n / tc
        if self.t_phase == PhaseEnum.Unload_c:
            if phase_unload == PhaseEnum.Elastic:
                return num3
            if phase_unload == PhaseEnum.Plastic_c:
                return self._trot_nu + self.mom1n / self.e1n
            if phase_unload == PhaseEnum.Reload_c:
                if self._tstrain > self._trot_lim_nu:
                    return self._trot_nu + self.mom1n / self.e1n
                else:
                    return self._trot_pu + self.mom1n / self.tangent_reload_c
        if self.t_phase == PhaseEnum.Reload_t:
            if phase_unload == PhaseEnum.Elastic:
                return num3
            if phase_unload == PhaseEnum.Plastic_c:
                num4 = self._cstrain - self._cstress / self.e1p
                tc = self.tangent_reload_c if num2 == 0.0 else num2 / (num3 - num4)
                return num4 + self.mom1n / tc
            if phase_unload == PhaseEnum.Reload_c:
                if self._t_phase_unload_t == PhaseEnum.Reload_t:
                    num4 = self._cstrain - self._cstress / self.e1p
                    tc = self.tangent_reload_c if num2 == 0.0 else num2 / (num3 - num4)
                    return num4 + self.mom1n / tc
                else:
                    return self._trot_pu + self.mom1n / self.tangent_reload_c
        if self.t_phase == PhaseEnum.Reload_c:
            if phase_unload in (PhaseEnum.Elastic, PhaseEnum.Reload_c):
                tc = self.tangent_reload_c
                num = self._trot_pu + self.mom1n / tc
                if self.e3n < 0.0:
                    val = (self._trot_pu * tc - self.rot3n * self.e3n) / (tc - self.e3n)
                    num = max(num, val)
                return num
        return num3

    # ===================================================================
    # Increment handlers
    # ===================================================================

    def _positive_increment_takeda(self, dstrain: float) -> None:
        """C# positiveIncrementTakeda."""
        if self._tload_indicator == 2:
            if (self._t_phase_unload_c == PhaseEnum.Reload_c
                    and self._tmom_min > self._cstress and self._cstress < 0.0):
                self._tmom_min = self._cstress
                self._trot_min = self._cstrain
                self._trot_nu = self._cstrain - self._cstress / (self.eun * 1.0)
            if self._t_phase_unload_c == PhaseEnum.Reload_c and self.t_phase == PhaseEnum.Reload_c:
                self._trot_lim_nu = self._cstrain
            self._tload_indicator = 1
            if self._cstress <= 0.0:
                self._trot_nu = self._cstrain - self._cstress / (self.eun * 1.0)
                self._trot_max = self.umax[0] * (1.0 + 0.0)

        self._tload_indicator = 1
        if not self._tplastic_tension_indicator:
            self._trot_max = self.rot1p
            self._tmom_max = self.mom1p

        tmom_max = self._tmom_max
        trot_nu = self._trot_nu

        if self._tstrain < self._trot_nu:
            self.k_tang = self.e1n
            self._tstress = self._cstress + self.k_tang * dstrain
            if self._tstress < self.mom1n:
                self._tstress = self.mom1n
            if self._tstress >= 0.0:
                self._tstress = 0.0
                self.k_tang = self.eun * 1e-09
            return

        p = self.t_phase
        if p == PhaseEnum.Plastic_c:
            self.k_tang = tmom_max / (self._trot_max - trot_nu)
            self._tstress = self.k_tang * (self._tstrain - trot_nu)
        elif p in (PhaseEnum.Elastic, PhaseEnum.Unload_c):
            if self._t_phase_unload_c == PhaseEnum.Elastic:
                self.k_tang = tmom_max / (self._trot_max - trot_nu)
                self._tstress = self._cstress + self.k_tang * dstrain
            elif self._t_phase_unload_c in (PhaseEnum.Plastic_c, PhaseEnum.Reload_c):
                self.k_tang = tmom_max / (self._trot_max - trot_nu)
                self._tstress = self.k_tang * (self._tstrain - trot_nu)
        elif p == PhaseEnum.Unload_t:
            if self._t_phase_unload_t in (PhaseEnum.Elastic, PhaseEnum.Plastic_t):
                self.k_tang = self.e1p
                self._tstress = self._cstress + self.k_tang * dstrain
            elif self._t_phase_unload_t == PhaseEnum.Reload_t:
                if self._tstrain < self._trot_lim_pu:
                    self.k_tang = self.e1p
                    self._tstress = self._cstress + self.k_tang * dstrain
                else:
                    self.k_tang = self.tangent_reload_t
                    self._tstress = self.k_tang * (self._tstrain - trot_nu)
        elif p == PhaseEnum.Reload_c:
            self.k_tang = tmom_max / (self._trot_max - trot_nu)
            self._tstress = self.k_tang * (self._tstrain - trot_nu)
        elif p == PhaseEnum.Reload_t:
            self.k_tang = self.tangent_reload_t
            self._tstress = self.k_tang * (self._tstrain - trot_nu)
        # Plastic_t: no-op

    def _negative_increment_takeda(self, dstrain: float) -> None:
        """C# negativeIncrementTakeda."""
        if self._tload_indicator == 1:
            if (self._t_phase_unload_t == PhaseEnum.Reload_t
                    and self._tmom_max < self._cstress and self._cstress > 0.0):
                self._tmom_max = self._cstress
                self._trot_max = self._cstrain
                self._trot_pu = self._cstrain - self._cstress / (self.eup * 1.0)
            if self._t_phase_unload_t == PhaseEnum.Reload_t and self.t_phase == PhaseEnum.Reload_t:
                self._trot_lim_pu = self._cstrain
            self._tload_indicator = 2
            if self._cstress >= 0.0:
                self._trot_pu = self._cstrain - self._cstress / (self.eup * 1.0)
                self._trot_min = self.umax[1] * (1.0 + 0.0)

        self._tload_indicator = 2
        if not self._tplastic_compression_indicator:
            self._trot_min = self.rot1n
            self._tmom_min = self.mom1n

        tmom_min = self._tmom_min
        trot_pu = self._trot_pu

        if self._tstrain > self._trot_pu:
            self.k_tang = self.e1p
            self._tstress = self._cstress + self.k_tang * dstrain
            if self._tstress > self.mom1p:
                self._tstress = self.mom1p
            if self._tstress <= 0.0:
                self._tstress = 0.0
                self.k_tang = self.eup * 1e-09
            return

        p = self.t_phase
        if p == PhaseEnum.Plastic_t:
            self.k_tang = tmom_min / (self._trot_min - trot_pu)
            self._tstress = self.k_tang * (self._tstrain - trot_pu)
        elif p in (PhaseEnum.Elastic, PhaseEnum.Unload_t):
            if self._t_phase_unload_t == PhaseEnum.Elastic:
                self.k_tang = tmom_min / (self._trot_min - trot_pu)
                self._tstress = self._cstress + self.k_tang * dstrain
            elif self._t_phase_unload_t in (PhaseEnum.Plastic_t, PhaseEnum.Reload_t):
                self.k_tang = tmom_min / (self._trot_min - trot_pu)
                self._tstress = self.k_tang * (self._tstrain - trot_pu)
        elif p == PhaseEnum.Unload_c:
            if self._t_phase_unload_c in (PhaseEnum.Elastic, PhaseEnum.Plastic_c):
                self.k_tang = self.e1n
                self._tstress = self._cstress + self.k_tang * dstrain
            elif self._t_phase_unload_c == PhaseEnum.Reload_c:
                if self._tstrain > self._trot_lim_nu:
                    self.k_tang = self.e1n
                    self._tstress = self._cstress + self.k_tang * dstrain
                else:
                    self.k_tang = self.tangent_reload_c
                    self._tstress = self.k_tang * (self._tstrain - trot_pu)
        elif p == PhaseEnum.Reload_t:
            self.k_tang = tmom_min / (self._trot_min - trot_pu)
            self._tstress = self.k_tang * (self._tstrain - trot_pu)
        elif p == PhaseEnum.Reload_c:
            self.k_tang = self.tangent_reload_c
            self._tstress = self.k_tang * (self._tstrain - trot_pu)
        # Plastic_c: no-op

    # ===================================================================
    # Main state machine — Takeda type (diagonal quad variant)
    # ===================================================================

    def set_trial_strain_takeda_diagonal_quad(
        self, strain: float, dN: float, masonry=None, volume: float = 0.0, sigma: float = 0.0
    ) -> int:
        """C# setTrialStrainTakedaDiagonalQuad."""
        self.dn = dN
        if self._tload_indicator == 0 and strain == 0.0:
            return 0
        self.revert_to_last_commit()
        self._tstrain = strain
        dstrain = self._tstrain - self._cstrain

        # Normal stress carried by the spring increment (flag=False means DN used _tstressNormal update at end)
        # _tstressNormal += DN is deferred to the end of this method

        tau = self._tau_limite(self._tstress_normal)
        num3 = tau / self.e1p if self.e1p != 0.0 else 0.0

        # Fracture energy path  (ConstitutiveLawMasonryShearEnum 4 or 5)
        if masonry is not None and hasattr(masonry, 'constitutive_law_masonry_shear') and masonry.constitutive_law_masonry_shear in (4, 5):
            shear_ult_strain = masonry.get_shear_ultimate_strain(tau, num3, volume, sigma)
            self.ur[0] = shear_ult_strain
            self.ur[1] = -shear_ult_strain
            self.mom2p = self.mom1p = tau
            self.mom2n = self.mom1n = -tau
            self.rot1p = num3
            self.rot2p = max(shear_ult_strain, self.rot1p * 1.0001)
            self.rot3p = max(shear_ult_strain, self.rot2p * 1.0001)
        else:
            self.mom1p = tau
            self.rot1p = num3
            if self.e3p < 0.0:
                self.rot2p = max(self.plastic_strain_ratio, self.rot1p * 1.0001)
                self.rot3p = self.rot2p - self.mom2p / self.e3p
            if self.rot2p < self.rot1p:
                self.rot2p = self.rot1p * 1.0001
            if self.rot3p < self.rot2p:
                self.rot3p = self.rot2p * 1.0001
            self.mom2p = self.mom1p + self.e2p * (self.rot2p - self.rot1p)

        self.mom1n = -self.mom1p
        self.rot1n = -self.rot1p
        self.mom2n = -self.mom2p
        self.rot2n = -self.rot2p
        self.rot3n = -self.rot3p
        self.fy[0] = self.mom1p
        self.fy[1] = self.mom1n

        # Slip check
        if self.mom1p == 0.0:
            self.t_phase = PhaseEnum.Slip
            self._tstress = 0.0
            self.k_tang = 0.0
            self._tenergy_d = self.cenergy_d + 0.5 * (self._cstress + self._tstress) * dstrain
            self._tstress_normal += self.dn
            return 0

        # Coming from Slip
        if self.phase == PhaseEnum.Slip:
            if self.mom1p > 0.0:
                self._tload_indicator = 0
                self.t_phase = PhaseEnum.Elastic
                self._tplastic_tension_indicator = True
                self._tplastic_compression_indicator = True
                self._trot_nu = self._cstrain
                self._trot_pu = self._cstrain
                self.k_tang = self.e2p
                self.tangent_reload_c = self.k_tang
                self.tangent_reload_t = self.k_tang
                self._tstress = self.k_tang * dstrain
                self._trot_max = self._cstrain + self.rot1p
                self._tmom_max = self.k_tang * self.rot1p
                self._trot_min = self._cstrain + self.rot1n
                self._tmom_min = self.k_tang * self.rot1n
                if dstrain > 0.0:
                    self._tload_indicator = 1
                    self.t_phase = PhaseEnum.Reload_t
                else:
                    self.t_phase = PhaseEnum.Reload_c
                    self._tload_indicator = 2
                if abs(self._tstress) - self.mom1p > 0.0:
                    sign = 1.0 if self._tstress > 0.0 else -1.0
                    self._tstress = self.mom1p * sign
                    if sign > 0.0:
                        self.t_phase = PhaseEnum.Plastic_t
                        self._tmom_max = self._tstress
                        self._trot_max = self._tstrain
                    else:
                        self.t_phase = PhaseEnum.Plastic_c
                        self._tmom_min = self._tstress
                        self._trot_min = self._tstrain
                self._tenergy_d = self.cenergy_d + 0.5 * (self._cstress + self._tstress) * dstrain
                self._tstress_normal += self.dn
                return 0
            self._tstress = 0.0
            self.k_tang = 0.0
            self._tenergy_d = self.cenergy_d + 0.5 * (self._cstress + self._tstress) * dstrain
            self._tstress_normal += self.dn
            return 0

        # Rupture
        if self.phase in (PhaseEnum.RuptureTraz, PhaseEnum.RuptureComp):
            self._tstress = 0.0
            self.k_tang = 0.0
            self._tenergy_d = self.cenergy_d + 0.5 * (self._cstress + self._tstress) * dstrain
            self._tstress_normal += self.dn
            return 0

        # Core state machine
        self._trot_yp = self._get_current_yielding_displacement_tension(self._c_phase_unload_t, dstrain)
        self._trot_yn = self._get_current_yielding_displacement_compression(self._c_phase_unload_c, dstrain)

        if self._tload_indicator == 0:
            self._tload_indicator = 1 if dstrain >= 0.0 else 2

        if self._tstrain >= self._trot_yp and dstrain > 0.0:
            self._trot_max = self._tstrain
            self.k_tang = self._pos_envlp_tangent_takeda(self._tstrain)
            self._tstress = self._pos_envlp_stress_takeda(self._tstrain)
            self._tload_indicator = 1
            num5 = (self._tstress - self._cstress) / self.e1p if self.e1p != 0.0 else 0.0
            self._tup += dstrain - num5
            if self.t_phase == PhaseEnum.Plastic_t:
                self._tplastic_tension_indicator = True
            self._tmom_max = self._tstress
        elif self._tstrain <= self._trot_yn and dstrain < 0.0:
            self._trot_min = self._tstrain
            self.k_tang = self._neg_envlp_tangent_takeda(self._tstrain)
            self._tstress = self._neg_envlp_stress_takeda(self._tstrain)
            self._tload_indicator = 2
            num6 = (self._tstress - self._cstress) / self.e1n if self.e1n != 0.0 else 0.0
            self._tup += dstrain - num6
            if self.t_phase == PhaseEnum.Plastic_c:
                self._tplastic_compression_indicator = True
            self._tmom_min = self._tstress
        elif dstrain < 0.0:
            self._negative_increment_takeda(dstrain)
            if self._tstress > 0.0:
                self.t_phase = PhaseEnum.Unload_t
            elif self.t_phase == PhaseEnum.Unload_c:
                self.t_phase = PhaseEnum.Unload_c
                if self._tstrain <= self._trot_lim_nu and self._c_phase_unload_c == PhaseEnum.Reload_c:
                    self.t_phase = PhaseEnum.Reload_c
            else:
                self.t_phase = PhaseEnum.Reload_c
        elif dstrain > 0.0:
            self._positive_increment_takeda(dstrain)
            if self._tstress < 0.0:
                self.t_phase = PhaseEnum.Unload_c
            elif self.t_phase == PhaseEnum.Unload_t:
                self.t_phase = PhaseEnum.Unload_t
                if self._tstrain >= self._trot_lim_pu and self._c_phase_unload_t == PhaseEnum.Reload_t:
                    self.t_phase = PhaseEnum.Reload_t
            else:
                self.t_phase = PhaseEnum.Reload_t

        self._tenergy_d = self.cenergy_d + 0.5 * (self._cstress + self._tstress) * dstrain
        self._tstress_normal += self.dn
        return 0

    # ===================================================================
    # Main state machine — Takeda type (generic)
    # ===================================================================

    def set_trial_strain_takeda(self, strain: float) -> int:
        """C# setTrialStrainTakeda (generic, no fracture-energy path)."""
        if self._tload_indicator == 0 and strain == 0.0:
            return 0
        self.revert_to_last_commit()
        self._tstrain = strain
        dstrain = self._tstrain - self._cstrain

        self.mom1p = self._tau_limite(self._tstress_normal)
        self.rot1p = self.mom1p / self.e1p if self.e1p != 0.0 else 0.0

        if self.e3p < 0.0:
            self.rot2p = max(self.plastic_strain_ratio, self.rot1p * 1.0001)
            self.rot3p = self.rot2p - self.mom2p / self.e3p
        if self.rot2p < self.rot1p:
            self.rot2p = self.rot1p * 1.0001
        if self.rot3p < self.rot2p:
            self.rot3p = self.rot2p * 1.0001
        self.mom2p = self.mom1p + self.e2p * (self.rot2p - self.rot1p)

        self.mom1n = -self.mom1p
        self.rot1n = -self.rot1p
        self.mom2n = -self.mom2p
        self.rot2n = -self.rot2p
        self.rot3n = -self.rot3p
        self.fy[0] = self.mom1p
        self.fy[1] = self.mom1n

        if self.mom1p == 0.0:
            self.t_phase = PhaseEnum.Slip
            self._tstress = 0.0
            self.k_tang = 0.0
            self._tenergy_d = self.cenergy_d + 0.5 * (self._cstress + self._tstress) * dstrain
            self._tstress_normal += self.dn
            return 0

        if self.phase == PhaseEnum.Slip:
            if self.mom1p > 0.0:
                self._tload_indicator = 0
                self.t_phase = PhaseEnum.Elastic
                self._tplastic_tension_indicator = True
                self._tplastic_compression_indicator = True
                self._trot_nu = self._cstrain
                self._trot_pu = self._cstrain
                self.k_tang = self.e2p
                self.tangent_reload_c = self.k_tang
                self.tangent_reload_t = self.k_tang
                self._tstress = self.k_tang * dstrain
                self._trot_max = self._cstrain + self.rot1p
                self._tmom_max = self.k_tang * self.rot1p
                self._trot_min = self._cstrain + self.rot1n
                self._tmom_min = self.k_tang * self.rot1n
                if dstrain > 0.0:
                    self._tload_indicator = 1
                    self.t_phase = PhaseEnum.Reload_t
                else:
                    self.t_phase = PhaseEnum.Reload_c
                    self._tload_indicator = 2
                if abs(self._tstress) - self.mom1p > 0.0:
                    sign = 1.0 if self._tstress > 0.0 else -1.0
                    self._tstress = self.mom1p * sign
                    if sign > 0.0:
                        self.t_phase = PhaseEnum.Plastic_t
                        self._tmom_max = self._tstress
                        self._trot_max = self._tstrain
                    else:
                        self.t_phase = PhaseEnum.Plastic_c
                        self._tmom_min = self._tstress
                        self._trot_min = self._tstrain
                self._tenergy_d = self.cenergy_d + 0.5 * (self._cstress + self._tstress) * dstrain
                self._tstress_normal += self.dn
                return 0
            self._tstress = 0.0
            self.k_tang = 0.0
            self._tenergy_d = self.cenergy_d + 0.5 * (self._cstress + self._tstress) * dstrain
            self._tstress_normal += self.dn
            return 0

        if self.phase in (PhaseEnum.RuptureTraz, PhaseEnum.RuptureComp):
            self._tstress = 0.0
            self.k_tang = 0.0
            self._tenergy_d = self.cenergy_d + 0.5 * (self._cstress + self._tstress) * dstrain
            self._tstress_normal += self.dn
            return 0

        self._trot_yp = self._get_current_yielding_displacement_tension(self._c_phase_unload_t, dstrain)
        self._trot_yn = self._get_current_yielding_displacement_compression(self._c_phase_unload_c, dstrain)

        if self._tload_indicator == 0:
            self._tload_indicator = 1 if dstrain >= 0.0 else 2

        if self._tstrain >= self._trot_yp and dstrain > 0.0:
            self._trot_max = self._tstrain
            self.k_tang = self._pos_envlp_tangent_takeda(self._tstrain)
            self._tstress = self._pos_envlp_stress_takeda(self._tstrain)
            self._tload_indicator = 1
            num5 = (self._tstress - self._cstress) / self.e1p if self.e1p != 0.0 else 0.0
            self._tup += dstrain - num5
            if self.t_phase == PhaseEnum.Plastic_t:
                self._tplastic_tension_indicator = True
            self._tmom_max = self._tstress
        elif self._tstrain <= self._trot_yn and dstrain < 0.0:
            self._trot_min = self._tstrain
            self.k_tang = self._neg_envlp_tangent_takeda(self._tstrain)
            self._tstress = self._neg_envlp_stress_takeda(self._tstrain)
            self._tload_indicator = 2
            num6 = (self._tstress - self._cstress) / self.e1n if self.e1n != 0.0 else 0.0
            self._tup += dstrain - num6
            if self.t_phase == PhaseEnum.Plastic_c:
                self._tplastic_compression_indicator = True
            self._tmom_min = self._tstress
        elif dstrain < 0.0:
            self._negative_increment_takeda(dstrain)
            if self._tstress > 0.0:
                self.t_phase = PhaseEnum.Unload_t
            elif self.t_phase == PhaseEnum.Unload_c:
                self.t_phase = PhaseEnum.Unload_c
                if self._tstrain <= self._trot_lim_nu and self._c_phase_unload_c == PhaseEnum.Reload_c:
                    self.t_phase = PhaseEnum.Reload_c
            else:
                self.t_phase = PhaseEnum.Reload_c
        elif dstrain > 0.0:
            self._positive_increment_takeda(dstrain)
            if self._tstress < 0.0:
                self.t_phase = PhaseEnum.Unload_c
            elif self.t_phase == PhaseEnum.Unload_t:
                self.t_phase = PhaseEnum.Unload_t
                if self._tstrain >= self._trot_lim_pu and self._c_phase_unload_t == PhaseEnum.Reload_t:
                    self.t_phase = PhaseEnum.Reload_t
            else:
                self.t_phase = PhaseEnum.Reload_t

        self._tenergy_d = self.cenergy_d + 0.5 * (self._cstress + self._tstress) * dstrain
        self._tstress_normal += self.dn
        return 0

    # ===================================================================
    # Main state machine — Initial type
    # ===================================================================

    def set_trial_strain_initial(self, strain: float) -> int:
        """C# setTrialStrainInitial (simpler elastic-plastic with hardening)."""
        self.revert_to_last_commit()
        self._tstrain = strain
        dstrain = self._tstrain - self._cstrain

        if self.phase == PhaseEnum.Rupture:
            self._tstress = self._cstress
            self._tstress_normal += self.dn
            return 0

        if self.check_contact_area:
            self._tcontact_area = self.area_corrente
            self.fy[0] += self.cohesion * (self._tcontact_area - self._ccontact_area) / self.area
            self.mom1p = self._tau_limite(self._tstress_normal, self._tcontact_area / self.area)
        else:
            self._tcontact_area = self.area
            self.mom1p = self._tau_limite(self._tstress_normal)

        c_hard = self.cohesion + self.h * abs(self._cup)
        self.fy[0] = self._tau_limite(self._tstress_normal, c_hard / self.cohesion) if self.cohesion != 0.0 else 0.0
        if self.fy[0] < 0.0:
            self.fy[0] = 0.0

        self.rot1p = self.mom1p / self.e1p if self.e1p != 0.0 else 0.0
        if self.e2p < 0.0:
            self.mom2p = 0.0
            self.rot2p = self.rot1p - self.mom1p / self.e2p
        else:
            if self.rot2p < self.rot1p:
                self.rot2p = self.rot1p
                self.rot3p = self.rot2p * 1.0001
            self.mom2p = self.mom1p + self.e2p * (self.rot2p - self.rot1p)

        self.mom1n = -self.mom1p
        self.rot1n = -self.rot1p
        self.mom2n = -self.mom2p
        self.rot2n = -self.rot2p
        self.rot3n = -self.rot3p

        if self.phase == PhaseEnum.Rupture and self.mom1p == 0.0:
            self._tstress = 0.0
            self.k_tang = 0.0
            return 0

        num3 = self._cstress + self.k * dstrain
        if abs(num3) - self.fy[0] > 0.0:
            if num3 > 0.0:
                self.t_phase = PhaseEnum.Plastic_t
                sign = 1.0
            else:
                self.t_phase = PhaseEnum.Plastic_c
                sign = -1.0
            num5 = (abs(num3) - self.fy[0]) / self.k
            num6 = self.k * num5 / (self.h + self.k)
            self.fy[0] += self.h * num6
            self._tstress = self.fy[0] * sign
            if self.t_phase == PhaseEnum.Plastic_t and self._tstress < 0.0:
                self.t_phase = PhaseEnum.Rupture
                self._tstress = 0.0
                self.k_tang = 0.0
            elif self.t_phase == PhaseEnum.Plastic_c and self._tstress > 0.0:
                self.t_phase = PhaseEnum.Rupture
                self._tstress = 0.0
                self.k_tang = 0.0
            else:
                self._tup += num6
                self.k_tang = self.e2p
        else:
            self._tstress = num3
            self.k_tang = self.k
            self.t_phase = PhaseEnum.Elastic

        self._tenergy_d = self.cenergy_d + 0.5 * (self._cstress + self._tstress) * dstrain
        self._tstress_normal += self.dn
        return 0

    # ===================================================================
    # Lifecycle
    # ===================================================================

    def revert_to_start(self) -> None:
        """C# revertToStart."""
        self.umax[0] = 0.0
        self.umax[1] = 0.0
        self._crot_pu = 0.0
        self._crot_nu = 0.0
        self.cenergy_d = 0.0
        self._cload_indicator = 0
        self._cstress = 0.0
        self._cstrain = 0.0
        self._tstrain = 0.0
        self._tstress = 0.0
        self.k_tang = self.e1p if self.e1p != 0.0 else self.k
        self._tstress_normal = 0.0
        self._cstress_normal = 0.0
        self.dn = 0.0
        self.f = self._cstress
        self.u = self._tstrain
        self.k_tang_committed = self.k_tang
        self._ccontact_area = self.area
        self._tcontact_area = self.area
        self.phase = PhaseEnum.Elastic
        self._cmom_max = 0.0
        self._cmom_min = 0.0
        self._crot_lim_pu = 0.0
        self._crot_lim_nu = 0.0
        self._crot_yp = 0.0
        self._crot_yn = 0.0
        self._cplastic_compression_indicator = False
        self._cplastic_tension_indicator = False
        self._c_phase_unload_t = PhaseEnum.Elastic
        self._c_phase_unload_c = PhaseEnum.Elastic
        self.tangent_reload_c = 0.0
        self.tangent_reload_t = 0.0

    def revert_to_last_commit(self) -> None:
        """C# RevertToLastCommit."""
        # C# restores the trial positive capacity from the committed negative
        # capacity here (``Fy[0] = -Fy[1]``).  Reversing that assignment lets
        # a rejected line-search trial leak its normal-force-updated ``Fy[0]``
        # into the next trial.
        self.fy[0] = -self.fy[1]
        self._trot_max = self.umax[0]
        self._trot_min = self.umax[1]
        self._trot_pu = self._crot_pu
        self._trot_nu = self._crot_nu
        self._tenergy_d = self.cenergy_d
        self._tload_indicator = self._cload_indicator
        self._tstress = self._cstress
        self._tstrain = self._cstrain
        self._tstress_normal = self._cstress_normal
        self._tcontact_area = self._ccontact_area
        self._tup = self._cup
        self.t_phase = self.phase
        self._tmom_max = self._cmom_max
        self._tmom_min = self._cmom_min
        self._trot_lim_pu = self._crot_lim_pu
        self._trot_lim_nu = self._crot_lim_nu
        self._trot_yp = self._crot_yp
        self._trot_yn = self._crot_yn
        self._tplastic_tension_indicator = self._cplastic_tension_indicator
        self._tplastic_compression_indicator = self._cplastic_compression_indicator
        self._t_phase_unload_t = self._c_phase_unload_t
        self._t_phase_unload_c = self._c_phase_unload_c

    def revert_to_last_commit_stress_normal(self) -> None:
        """C# ``revertToLastCommitStressNormal`` used by diagonal quads."""
        self._cstress_normal = self._cstress_normal_prev

    def commit(self) -> None:
        """C# Commit."""
        if not self.is_on:
            return
        self.fy[1] = -self.fy[0]
        self._cup = self._tup
        self.umax[0] = self._trot_max
        self.umax[1] = self._trot_min
        self._crot_pu = self._trot_pu
        self._crot_nu = self._trot_nu
        self.cenergy_d = self._tenergy_d
        self._cload_indicator = self._tload_indicator
        self._cstress_normal_prev = self._cstress_normal
        self._cstress = self._tstress
        self._cstrain = self._tstrain
        self._cstress_normal = self._tstress_normal
        self._ccontact_area = self._tcontact_area
        self.dn = 0.0
        self.f = self._cstress
        self.u = self._tstrain
        self.k_tang = self.k_tang
        self.k_tang_committed = self.k_tang
        self.phase = self.t_phase
        self._cmom_max = self._tmom_max
        self._cmom_min = self._tmom_min
        self._crot_lim_pu = self._trot_lim_pu
        self._crot_lim_nu = self._trot_lim_nu
        self._crot_yp = self._trot_yp
        self._crot_yn = self._trot_yn
        if self.phase == PhaseEnum.Plastic_t:
            self._t_phase_unload_t = self.phase
        elif self.phase == PhaseEnum.Plastic_c:
            self._t_phase_unload_c = self.phase
        elif self.phase == PhaseEnum.Reload_t:
            if not self._tplastic_tension_indicator and not self._tplastic_compression_indicator:
                self._t_phase_unload_t = PhaseEnum.Elastic
            else:
                self._t_phase_unload_t = self.phase
                self._tplastic_tension_indicator = True
            self.tangent_reload_t = self.k_tang
        elif self.phase == PhaseEnum.Reload_c:
            if not self._tplastic_tension_indicator and not self._tplastic_compression_indicator:
                self._t_phase_unload_c = PhaseEnum.Elastic
            else:
                self._t_phase_unload_c = self.phase
                self._tplastic_compression_indicator = True
            self.tangent_reload_c = self.k_tang
        self._cplastic_compression_indicator = self._tplastic_compression_indicator
        self._cplastic_tension_indicator = self._tplastic_tension_indicator
        self._c_phase_unload_t = self._t_phase_unload_t
        self._c_phase_unload_c = self._t_phase_unload_c

    # ===================================================================
    # Dispatch
    # ===================================================================

    def set_trial_strain(self, strain: float) -> None:
        """Dispatch to Takeda or Initial hysteretic type (C# setTrialStrain)."""
        if not self.is_on:
            return
        if self.hysteretic_type == "Takeda" or self.hysteretic_type == "TakedaTensileCompressive":
            self.set_trial_strain_takeda(strain)
        else:
            self.set_trial_strain_initial(strain)

    def get_force(self) -> float:
        return self._tstress

    def get_incr_force(self) -> float:
        return self._tstress - self._cstress

    def get_displacement(self) -> float:
        return self._tstrain
