"""Port of the Quad/Restraint subset of C# ``ModelManager.PrepareModel``.

The original desktop preprocessor supports many computational element types and
polygonal partial intersections.  This module deliberately implements the
solver path needed by the supplied RailBridge models:

* four-node masonry ``Quad`` elements;
* full and collinear partial-edge Quad--Quad contacts;
* fixed line ``Restraint`` contacts already associated with a Quad face;
* masonry diagonal, transverse, in-plane and out-of-plane springs;
* global DOF numbering and Quad/Interface afference matrices.

Unsupported topologies fail explicitly rather than producing a partial model.
"""

from __future__ import annotations

from dataclasses import dataclass
import copy
import math
from typing import Iterable, Sequence

import numpy as np

try:
    from numba import njit
except Exception:  # pragma: no cover - scalar fallback remains available
    njit = None

from histra.elements.interface import Interface
from histra.elements.quad import Quad
from histra.elements.interface_state import InterfaceState
from histra.elements.quad_state import QuadState
from histra.model.masonry_material import MasonryMaterial
from histra.model.model import Model
from histra.model.restraint import Restraint
from histra.springs.coulomb03 import SpringCoulomb03
from histra.springs.elastic import SpringElastic
from histra.springs.hysteretic import SpringHysteretic
from histra.types.afference_entry import AfferenceEntry
from histra.types.point import Point


_TOL = 1.0e-5


class ModelPreparationError(RuntimeError):
    """Raised when an HRX uses a preprocessing feature not yet translated."""


@dataclass(frozen=True)
class PreparationReport:
    prepared: bool
    gdl: int
    quads: int
    quad_springs: int
    interfaces: int
    quad_quad_interfaces: int
    restraint_interfaces: int
    transverse_springs: int
    sliding_springs: int
    out_of_plane_springs: int


@dataclass(frozen=True)
class _HystereticLaw:
    E: float
    fy_t: float
    fy_c: float
    tensile_curve: str
    compressive_curve: str
    ratio_et_t: float
    ratio_et_c: float
    alfa_r_t: float
    alfa_r_c: float
    alfa_u_t: float
    alfa_u_c: float
    G_t: float
    G_c: float
    eps_u_t: float
    eps_u_c: float
    law_type: str


@dataclass(frozen=True)
class _CoulombLaw:
    E: float
    cohesion: float
    mu: float
    plastic_stiffness_ratio: float
    max_tensile_ratio: float
    reload_stiffness_ratio: float = 1.0
    plastic_stiffness_ratio2: float = 1.0
    plastic_strain: float = 1.0
    sub_law: str = "Coulomb"
    hysteretic_type: str = "Initial"
    fracture_energy: bool = False
    G: float = 0.0
    ductility: float = 100000.0
    is_ductility_fixed: bool = True
    check_contact_area: bool = False
    bcacovic: float = 0.0


def _v(point: Point | Sequence[float]) -> np.ndarray:
    if isinstance(point, Point):
        return np.asarray((point.x, point.y, point.z), dtype=float)
    return np.asarray(point, dtype=float)


def _p(value: Sequence[float]) -> Point:
    return Point(float(value[0]), float(value[1]), float(value[2]))


def _norm3(value: Sequence[float]) -> float:
    return math.sqrt(
        float(value[0]) * float(value[0])
        + float(value[1]) * float(value[1])
        + float(value[2]) * float(value[2])
    )


def _unit(value: Sequence[float], *, label: str) -> np.ndarray:
    out = np.asarray(value, dtype=float)
    norm = _norm3(out)
    if norm <= 1.0e-12:
        raise ModelPreparationError(f"Cannot normalize zero vector while building {label}.")
    return out / norm


def _series(k1: float, k2: float, restrained: bool) -> float:
    if restrained and (k1 == -1.0 or k2 == -1.0):
        return k2 if k1 == -1.0 else k1
    if k1 != 0.0 or k2 != 0.0:
        denominator = k1 + k2
        return k1 * k2 / denominator if denominator != 0.0 else 0.0
    return 0.0


def _material(model: Model, key: int) -> MasonryMaterial:
    assert model.collections is not None
    try:
        return model.collections.materials[key]
    except KeyError as exc:
        raise ModelPreparationError(f"Missing MasonryMaterial key {key}.") from exc


def _bool(material: MasonryMaterial, name: str, default: bool = False) -> bool:
    return bool(material.value(name, default))


def _float(material: MasonryMaterial, name: str, default: float = 0.0) -> float:
    """Read a C# ``MasonryMaterial`` numeric property as ``System.Single``.

    The desktop material class stores these values in ``float`` fields.  The
    rounded value is then promoted to ``double`` by constitutive constructors.
    Keeping the XML decimal as a Python double changes near-zero Coulomb
    capacities enough to select a different phase.
    """
    return float(np.float32(float(material.value(name, default))))


def _flex_law(material: MasonryMaterial, *, vertical: bool = False) -> _HystereticLaw:
    suffix = "Ver" if vertical else "Hor"
    curve_suffix = "Vertical" if vertical else ""
    E = _float(material, "Ever" if vertical else "Ehor")
    fy_t = _float(material, f"Ftm{suffix}")
    fy_c = _float(material, f"Fm{suffix}")
    duct_t = _float(material, f"DuctTrazRocking{suffix}", 1.0)
    duct_c = _float(material, f"DuctComprRocking{suffix}", 1.0)
    # Exact ConstitutiveLawHysteretic constructor semantics.  Despite their
    # names, IsDuct* == true makes the ultimate strain effectively unlimited;
    # false converts the supplied ductility factor into a strain at yield.
    eps_t = 1.0e20 if _bool(material, "IsDuctTraz", True) else duct_t * fy_t / E
    eps_c = 1.0e20 if _bool(material, "IsDuctCompr", False) else duct_c * fy_c / E
    return _HystereticLaw(
        E=E,
        fy_t=fy_t,
        fy_c=fy_c,
        tensile_curve=str(material.value(f"TensileCurveType{curve_suffix}", "LinearSoftening")),
        compressive_curve=str(material.value(f"CompressiveCurveType{curve_suffix}", "LinearSoftening")),
        ratio_et_t=_float(material, "RatioEtTraction"),
        ratio_et_c=_float(material, "RatioEtCompression"),
        # C# passes the BetaUnload values into Alfa_u and hard-codes Alfa_r=1.
        alfa_r_t=1.0,
        alfa_r_c=1.0,
        alfa_u_t=_float(material, f"BetaUnloadTractionRocking{suffix}"),
        alfa_u_c=_float(material, f"BetaUnloadCompressionRocking{suffix}"),
        G_t=_float(material, "GtVer" if vertical else "Gt"),
        G_c=_float(material, "GcVer" if vertical else "Gc"),
        eps_u_t=eps_t,
        eps_u_c=eps_c,
        law_type=str(material.value("ConstitutiveLawFlex", "Hysteretic")),
    )


def _diagonal_flex_law(material: MasonryMaterial) -> _HystereticLaw:
    """Apply C# ``PropOrthotropyParameter(sqrt(2)/2, sqrt(2)/2)``."""
    vertical = _flex_law(material, vertical=True)
    horizontal = _flex_law(material, vertical=False)
    c = math.sqrt(2.0) / 2.0
    w = c * c
    elasto_plastic = vertical.law_type.startswith("ElastoPlastic")
    return _HystereticLaw(
        E=vertical.E * w + horizontal.E * w,
        fy_t=vertical.fy_t * w + horizontal.fy_t * w,
        fy_c=vertical.fy_c * w + horizontal.fy_c * w,
        tensile_curve=horizontal.tensile_curve,
        compressive_curve=horizontal.compressive_curve,
        ratio_et_t=vertical.ratio_et_t * w + horizontal.ratio_et_t * w,
        ratio_et_c=vertical.ratio_et_c * w + horizontal.ratio_et_c * w,
        alfa_r_t=vertical.alfa_r_t,
        alfa_r_c=vertical.alfa_r_c,
        alfa_u_t=vertical.alfa_u_t,
        alfa_u_c=vertical.alfa_u_c,
        G_t=vertical.G_t * w + horizontal.G_t * w,
        G_c=vertical.G_c * w + horizontal.G_c * w,
        # C# ConstitutiveLawElastoPlastic contains a source-level asymmetry:
        # tensile ultimate strain uses c rather than c².
        eps_u_t=(vertical.eps_u_t * c + horizontal.eps_u_t * c)
        if elasto_plastic
        else (vertical.eps_u_t * w + horizontal.eps_u_t * w),
        eps_u_c=vertical.eps_u_c * w + horizontal.eps_u_c * w,
        law_type=vertical.law_type,
    )


def _shear_law(material: MasonryMaterial) -> _CoulombLaw:
    alfa = _float(material, "AlfaShearUser", 1.0)
    if alfa == 0.0:
        raise ModelPreparationError(f"Material {material.key} has AlfaShearUser=0.")
    return _CoulombLaw(
        E=_float(material, "Gd") / alfa,
        cohesion=_float(material, "fvk0d"),
        mu=_float(material, "FrictionRatioShear"),
        plastic_stiffness_ratio=_float(material, "ShearPlasticStiffnessRatio"),
        max_tensile_ratio=_float(material, "ShearMaxTensileRatio", 0.5),
        reload_stiffness_ratio=_float(material, "ShearReloadStiffnessRatio", 1.0),
        plastic_stiffness_ratio2=_float(material, "ShearPlasticStiffnessRatio2", 1.0),
        plastic_strain=_float(material, "ShearPlasticStrain", 100.0),
        sub_law=str(material.value("CriterioSnervamento", "Coulomb")),
        hysteretic_type=str(material.value("UnloadShear", "Initial")),
        fracture_energy=(str(material.value("ConstitutiveLawMasonryShear", "")) == "ElastoPlasticFractureEnergyFixed"),
        G=_float(material, "FractureEnergyShear"),
        ductility=_float(material, "DuctilityShear", 100.0),
        is_ductility_fixed=True,
        check_contact_area=_bool(material, "CheckContactArea", False),
        bcacovic=_float(material, "Bcacovic"),
    )


def _sliding_law(material: MasonryMaterial, *, out_of_plane: bool, vertical: bool) -> _CoulombLaw:
    if out_of_plane:
        E = _float(material, "Gd")
    else:
        alpha = _float(material, "AlfaShearUser", 0.9)
        if abs(1.0 - alpha) <= 1.0e-12:
            raise ModelPreparationError(f"Material {material.key} has AlfaShearUser=1.")
        E = 2.0 * _float(material, "Gd") / (1.0 - alpha)
    suffix = "Vert" if vertical else "Hor"
    return _CoulombLaw(
        E=E,
        cohesion=_float(material, f"CohesionSliding{suffix}"),
        mu=_float(material, f"FrictionRatioSliding{suffix}"),
        plastic_stiffness_ratio=_float(material, f"SlidingPlasticStiffnessRatio{suffix}"),
        max_tensile_ratio=_float(material, f"SlidingMaxTensileRatio{suffix}", 0.8),
        sub_law=str(material.value(f"SlidingYieldingDomain{suffix}", "Coulomb")),
        hysteretic_type="Initial",
        fracture_energy=_bool(material, f"SlidingFractureEnergy{'Ver' if vertical else ''}", False),
        G=_float(material, f"Gs{'Ver' if vertical else ''}"),
        ductility=100000.0,
        is_ductility_fixed=True,
        check_contact_area=_bool(material, "CheckContactArea", False),
    )


def _configure_coulomb(
    *, k: float, area: float, length: float, law: _CoulombLaw,
    cohesion_force: float | None = None, mu: float | None = None,
    ur: float | None = None, hysteretic_type: str | None = None,
    plastic_strain: float | None = None, use_second_branch: bool = False,
    sub_law: str | None = None,
) -> SpringCoulomb03:
    """Create the virgin C# SpringCoulomb03 envelope.

    C# ``Set``/``Set2`` use constitutive-law ratios to construct the envelope
    but, somewhat surprisingly, do not copy most of those ratios into the
    spring's serialized properties.  The spring therefore retains its class
    defaults (0.0001, 0.8, 1.0) while the initial envelope can have a different
    tangent.  Preserving that behavior matters when normal force later causes
    the Coulomb envelope to be rebuilt.
    """
    spring = SpringCoulomb03(type_of="HiStrA.Objects.SpringCoulomb03")
    spring.k = float(k)
    spring.area = float(area)
    spring.length = float(length)
    spring.cohesion = float(law.cohesion * area if cohesion_force is None else cohesion_force)
    spring.mu = float(law.mu if mu is None else mu)
    spring.sub_law = sub_law or law.sub_law
    spring.hysteretic_type = hysteretic_type or law.hysteretic_type
    spring.bcacovic = float(law.bcacovic)

    ultimate = float(law.ductility if ur is None else ur)
    if ultimate <= 0.0:
        ultimate = 100000.0
    ktan = spring.k * law.plastic_stiffness_ratio
    ktan2 = spring.k * law.plastic_stiffness_ratio2
    mom1p = max(1.0e-9, spring.cohesion)
    rot1p = mom1p / spring.k if spring.k else 0.0

    if use_second_branch and ktan2 < 0.0:
        ps = float(ultimate if plastic_strain is None else plastic_strain)
        spring.plastic_strain_ratio = ps  # Set2 is the one C# path that stores it.
        rot2p = max(ps, rot1p * 1.0001)
        mom2p = mom1p + ktan * (rot2p - rot1p)
        if law.is_ductility_fixed:
            rot3p = max(ultimate, rot2p * 1.0001)
            mom3p = 0.0
        else:
            mom3p = 0.0
            rot3p = rot1p - mom1p / ktan2
    elif ktan < 0.0:
        if law.is_ductility_fixed:
            rot2p = max(ultimate, rot1p * 1.0001)
            mom2p = 0.0
        else:
            mom2p = 0.0
            rot2p = rot1p - mom1p / ktan
        rot3p = 1.0001 * rot2p
        mom3p = 0.0
    else:
        rot2p = max(ultimate, rot1p * 1.0001)
        mom2p = mom1p + ktan * (rot2p - rot1p)
        rot3p = 1.0001 * rot2p
        mom3p = 0.0 if law.is_ductility_fixed else mom1p + ktan * (rot3p - rot1p)

    spring.mom1p, spring.rot1p = mom1p, rot1p
    spring.mom2p, spring.rot2p = mom2p, rot2p
    spring.mom3p, spring.rot3p = mom3p, rot3p
    spring.mom1n, spring.rot1n = -mom1p, -rot1p
    spring.mom2n, spring.rot2n = -mom2p, -rot2p
    spring.mom3n, spring.rot3n = -mom3p, -rot3p
    spring.fy = [spring.cohesion, -spring.cohesion]
    spring.ur = [ultimate, -ultimate]
    spring.umax = [spring.cohesion / spring.k if spring.k else 0.0,
                   -spring.cohesion / spring.k if spring.k else 0.0]
    spring._set_envelope()
    spring.energy_a = 0.5 * (
        rot1p*mom1p + (rot2p-rot1p)*(mom2p+mom1p)
        + (rot3p-rot2p)*(mom3p+mom2p)
        + spring.rot1n*spring.mom1n
        + (spring.rot2n-spring.rot1n)*(spring.mom2n+spring.mom1n)
        + (spring.rot3n-spring.rot2n)*(spring.mom3n+spring.mom2n)
    )
    spring.revert_to_start()
    spring.revert_to_last_commit()
    return spring


def _set_coulomb_ultimate(
    spring: SpringCoulomb03, law1: _CoulombLaw, law2: _CoulombLaw
) -> None:
    """Port ``SpringCoulomb03.SetUltimateDisplacement``."""
    energies = [law.G for law in (law1, law2) if law.fracture_energy]
    if not energies or spring.area == 0.0 or spring.fy[0] == 0.0:
        return
    spring.hysteretic_type = "Initial"
    spring.check_contact_area = law1.check_contact_area or law2.check_contact_area
    energy = sum(energies) / len(energies)
    ur = 2.0 * energy / (spring.fy[0] / spring.area) + spring.fy[0] / spring.k
    ur = max(ur, spring.fy[0] / spring.k * 1.0001)
    spring.ur = [ur, -ur]
    spring.rot2p = ur
    spring.mom2p = 0.0
    spring.rot3p = 1.01 * ur
    spring.mom3p = 0.0
    spring.rot2n = -ur
    spring.mom2n = 0.0
    spring.rot3n = -1.01 * ur
    spring.mom3n = 0.0
    spring._set_envelope()
    spring.revert_to_start()
    spring.revert_to_last_commit()

def _configure_hysteretic(k: float, area: float, length: float, law: _HystereticLaw) -> SpringHysteretic:
    spring = SpringHysteretic(type_of="HiStrA.Objects.SpringHysteretic")
    spring.k = float(k)
    spring.area = float(area)
    spring.length = float(length)
    spring.tensile_curve_type = law.tensile_curve
    spring.compressive_curve_type = law.compressive_curve
    spring.fy = [area * law.fy_t, -area * law.fy_c]
    spring.kt = [0.0, 0.0]
    if law.tensile_curve == "Elastic":
        spring.fy[0] = k * 100000000.0
        spring.kt[0] = k
    elif law.tensile_curve == "LinearHardening":
        spring.kt[0] = k * law.ratio_et_t
    if law.compressive_curve == "Elastic":
        spring.fy[1] = -k * 100000000.0
        spring.kt[1] = k
    elif law.compressive_curve == "LinearHardening":
        spring.kt[1] = k * law.ratio_et_c
    spring.alfar = [law.alfa_r_t, law.alfa_r_c]
    spring.alfau = [law.alfa_u_t, law.alfa_u_c]
    # Temporary values; _set_ultimate_displacement reproduces the post-series
    # C# call and then initialize() rebuilds the envelope.
    spring.ur = [max(spring.fy[0] / k if k else 0.0, law.eps_u_t * length),
                 min(spring.fy[1] / k if k else 0.0, -law.eps_u_c * length)]
    _set_ultimate_displacement(spring, law, law)
    spring.initialize()
    spring.revert_to_start()
    spring.revert_to_last_commit()
    return spring


def _set_ultimate_displacement(spring: SpringHysteretic, law1: _HystereticLaw, law2: _HystereticLaw) -> None:
    # Exact fracture-energy branches used by the supplied materials.
    gt = [law.G_t for law in (law1, law2) if law.tensile_curve in {"LinearSoftening", "Exponential"}]
    if gt and spring.area and spring.fy[0]:
        g = sum(gt) / len(gt)
        if spring.tensile_curve_type == "LinearSoftening":
            spring.ur[0] = 2.0 * g / (spring.fy[0] / spring.area) + spring.fy[0] / spring.k
            spring.kt[0] = -spring.fy[0] / (spring.ur[0] - spring.fy[0] / spring.k)
        elif spring.tensile_curve_type == "Exponential":
            spring.ur[0] = g / (spring.fy[0] / spring.area) + spring.fy[0] / spring.k
        spring.ur[0] = max(spring.ur[0], spring.fy[0] / spring.k)
    else:
        candidates = []
        for law in (law1, law2):
            if law.tensile_curve != "Elastic" and law.fy_t and law.E:
                candidates.append(spring.fy[0] / spring.k * law.eps_u_t / (law.fy_t / law.E))
        if candidates:
            spring.ur[0] = min(candidates)

    gc = [law.G_c for law in (law1, law2) if law.compressive_curve in {"LinearSoftening", "Parabolic"}]
    if gc and spring.area and spring.fy[1]:
        g = sum(gc) / len(gc)
        if spring.compressive_curve_type == "LinearSoftening":
            spring.ur[1] = 2.0 * g / (spring.fy[1] / spring.area) + spring.fy[1] / spring.k
            spring.kt[1] = -spring.fy[1] / (spring.ur[1] - spring.fy[1] / spring.k)
        elif spring.compressive_curve_type == "Parabolic":
            spring.ur[1] = 3.0 * g / (2.0 * spring.fy[1] / spring.area) + 5.0 * spring.fy[1] / (3.0 * spring.k)
        spring.ur[1] = min(spring.ur[1], spring.fy[1] / spring.k)
    else:
        candidates = []
        for law in (law1, law2):
            if law.compressive_curve != "Elastic" and law.fy_c and law.E:
                candidates.append(spring.fy[1] / spring.k * law.eps_u_c / (law.fy_c / law.E))
        if candidates:
            spring.ur[1] = max(candidates)


def _combine_hysteretic(sp1: SpringHysteretic, sp2: SpringHysteretic, restrained: bool,
                        law1: _HystereticLaw, law2: _HystereticLaw) -> SpringHysteretic:
    if sp1.k == -1.0:
        out = copy.deepcopy(sp2)
    elif sp2.k == -1.0:
        out = copy.deepcopy(sp1)
    else:
        out = SpringHysteretic(type_of="HiStrA.Objects.SpringHysteretic")
        out.k = _series(sp1.k, sp2.k, restrained)
        # C# SetSpringYieldingForce: weakest tension and least-compressive
        # compression, carrying the associated area.
        if sp1.fy[0] <= sp2.fy[0]:
            out.fy[0], area_t = sp1.fy[0], sp1.area
        else:
            out.fy[0], area_t = sp2.fy[0], sp2.area
        if sp1.fy[1] <= sp2.fy[1]:
            out.fy[1], area_c = sp2.fy[1], sp2.area
        else:
            out.fy[1], area_c = sp1.fy[1], sp1.area
        out.area = area_c
        out.length = sp1.length + sp2.length
        out.alfau = [max(sp1.alfau[0], sp2.alfau[0]), max(sp1.alfau[1], sp2.alfau[1])]
        out.alfar = [max(sp1.alfar[0], sp2.alfar[0]), max(sp1.alfar[1], sp2.alfar[1])]
        # The current materials use matching curve families. Preserve the
        # weaker spring's family for mixed cases, matching the C# switch.
        out.tensile_curve_type = sp1.tensile_curve_type if sp1.fy[0] <= sp2.fy[0] else sp2.tensile_curve_type
        out.compressive_curve_type = sp1.compressive_curve_type if sp1.fy[1] >= sp2.fy[1] else sp2.compressive_curve_type
        out.kt = [
            out.k if out.tensile_curve_type == "Elastic" else _series(sp1.kt[0], sp2.kt[0], restrained),
            out.k if out.compressive_curve_type == "Elastic" else _series(sp1.kt[1], sp2.kt[1], restrained),
        ]
        out.ur = [max(out.fy[0] / out.k if out.k else 0.0, 0.0), min(out.fy[1] / out.k if out.k else 0.0, 0.0)]
        _set_ultimate_displacement(out, law1, law1)
        ur1 = out.ur[:]
        _set_ultimate_displacement(out, law2, law2)
        ur2 = out.ur[:]
        out.ur[0] = min(v for v in (ur1[0], ur2[0]) if v != 0.0) if ur1[0] and ur2[0] else max(ur1[0], ur2[0])
        out.ur[1] = max(v for v in (ur1[1], ur2[1]) if v != 0.0) if ur1[1] and ur2[1] else min(ur1[1], ur2[1])
        out.initialize()
        out.revert_to_start()
        out.revert_to_last_commit()
        return out
    _set_ultimate_displacement(out, law1, law2)
    out.initialize()
    out.revert_to_start()
    out.revert_to_last_commit()
    return out


def _combine_coulomb(sp1: SpringCoulomb03, sp2: SpringCoulomb03, restrained: bool) -> SpringCoulomb03:
    if sp1.k == -1.0:
        return copy.deepcopy(sp2)
    if sp2.k == -1.0:
        return copy.deepcopy(sp1)
    k = _series(sp1.k, sp2.k, restrained)
    cohesion = min(sp1.cohesion, sp2.cohesion)
    area = sp1.area if sp1.cohesion <= sp2.cohesion else sp2.area
    mu = min(sp1.mu, sp2.mu)
    ur = min(sp1.ur[0], sp2.ur[0])
    # C# CombinationSpring(SpringCoulomb03, ...) uses each temporary
    # spring's *actual* hardening modulus H, not the serialized class
    # property PlasticStiffnessRatio.  SetQuadSlidSpring intentionally leaves
    # that property at its SpringCoulomb03 default (1e-4), while the envelope
    # tangent E2p is built from the material ratio.  Using the property here
    # introduced an artificial softening branch for the common material value
    # SlidingPlasticStiffnessRatio=0 and changed the committed Vert phase of
    # near-zero-capacity in-plane sliders.
    h1 = sp1.h
    h2 = sp2.h
    h = min(h1, h2)
    ktan = -k * h / (k - h) if k != h else 0.0
    ratio = ktan / k if k else 0.0
    law = _CoulombLaw(
        E=0.0, cohesion=0.0, mu=mu, plastic_stiffness_ratio=ratio,
        max_tensile_ratio=min(sp1.max_tensile_ratio, sp2.max_tensile_ratio),
        sub_law=sp1.sub_law, hysteretic_type=sp1.hysteretic_type,
        ductility=ur, is_ductility_fixed=True,
    )
    out = _configure_coulomb(k=k, area=area, length=sp1.length + sp2.length, law=law,
                             cohesion_force=cohesion, mu=mu, ur=ur,
                             hysteretic_type=sp1.hysteretic_type)
    return out


def _quad_face_vertices(model: Model, quad: Quad, face: int) -> list[np.ndarray]:
    assert model.collections is not None
    if face not in range(4):
        raise ModelPreparationError(f"Only lateral Quad faces 0..3 are supported, got {face}.")
    nodes = [_v(model.collections.nodes[k].point) for k in quad.node_keys]
    normals = [_unit(_v(n), label=f"Quad {quad.key} normal") for n in quad.normal]
    minus = [nodes[i] - normals[i] * quad.thickness[i] / 2.0 for i in range(4)]
    plus = [nodes[i] + normals[i] * quad.thickness[i] / 2.0 for i in range(4)]
    nxt = (face + 1) % 4
    if face in (0, 3):
        return [minus[face], minus[nxt], plus[nxt], plus[face]]
    return [minus[nxt], minus[face], plus[face], plus[nxt]]


def _edge_node_order(quad: Quad, face: int) -> tuple[int, int]:
    # Midpoints of VInt[1]/VInt[2] and VInt[0]/VInt[3], respectively.
    if face == 0:
        return quad.node_keys[1], quad.node_keys[0]
    if face == 1:
        return quad.node_keys[1], quad.node_keys[2]
    if face == 2:
        return quad.node_keys[2], quad.node_keys[3]
    if face == 3:
        return quad.node_keys[0], quad.node_keys[3]
    raise ModelPreparationError(f"Invalid Quad face {face}.")


def _edge_face_map(quads: Iterable[Quad]) -> dict[tuple[int, int], list[tuple[Quad, int]]]:
    out: dict[tuple[int, int], list[tuple[Quad, int]]] = {}
    for quad in quads:
        for face in range(4):
            a = quad.node_keys[face]
            b = quad.node_keys[(face + 1) % 4]
            out.setdefault(tuple(sorted((a, b))), []).append((quad, face))
    return out


def _make_interface_geometry(model: Model, intf: Interface, vertices: Sequence[np.ndarray],
                             node_keys: tuple[int, int], parent1_g: np.ndarray | None) -> None:
    assert model.collections is not None
    intf.node_keys = [int(node_keys[0]), int(node_keys[1])]
    p1 = _v(model.collections.nodes[node_keys[0]].point)
    p2 = _v(model.collections.nodes[node_keys[1]].point)
    e1 = _unit(p2 - p1, label=f"Interface {intf.key} e1")
    if parent1_g is None:
        # Restraint VInt defines its local axes. Use the first edge and the
        # vector from endpoint 1 across the face.
        across = (vertices[3] - vertices[0] + vertices[2] - vertices[1]) * 0.5
        e3 = _unit(-across, label=f"Interface {intf.key} e3")
        e2 = _unit(np.cross(e3, e1), label=f"Interface {intf.key} e2")
        e3 = _unit(np.cross(e1, e2), label=f"Interface {intf.key} e3")
        origin = p1
    else:
        midpoint = 0.5 * (p1 + p2)
        inward = midpoint - parent1_g
        inward = inward - e1 * float(np.dot(inward, e1))
        e2 = _unit(inward, label=f"Interface {intf.key} e2")
        e3 = _unit(np.cross(e1, e2), label=f"Interface {intf.key} e3")
        origin = p1
    intf.reference_e1 = tuple(float(x) for x in e1)
    intf.reference_e2 = tuple(float(x) for x in e2)
    intf.reference_e3 = tuple(float(x) for x in e3)
    intf.reference_origin = _p(origin)
    intf.vint3d = [_p(v) for v in vertices]
    intf.vint2d = [Point(float(np.dot(v - origin, e1)), float(np.dot(v - origin, e3)), 0.0) for v in vertices]
    intf.length = float(np.linalg.norm(p2 - p1))
    intf._perf_area = None



def _find_or_create_geometric_node(model: Model, point: np.ndarray, *, tolerance: float = 1.0e-4) -> int:
    """Return the C# PrepareBuildInterface endpoint node for an intersection edge.

    C# first catches an existing node near the midpoint of the interface's
    thickness edge and creates a geometry-only node only when none exists.
    Computational DOFs remain attached to Quads, so a newly created node does
    not alter ``model.gdl``.
    """
    assert model.collections is not None
    best_key: int | None = None
    best_distance = float("inf")
    for key, node in model.collections.nodes.items():
        distance = float(np.linalg.norm(_v(node.point) - point))
        if distance <= tolerance and distance < best_distance:
            best_key = int(key)
            best_distance = distance
    if best_key is not None:
        return best_key

    from histra.model.node import Node

    key = max(model.collections.nodes, default=0) + 1
    model.collections.nodes[key] = Node(key=key, point=_p(point), name=str(key))
    return key


def _segment_overlap(
    p0: np.ndarray, p1: np.ndarray, q0: np.ndarray, q1: np.ndarray,
    *, distance_tolerance: float = 1.0e-4, angle_tolerance: float = 1.0e-6,
) -> tuple[np.ndarray, np.ndarray, float, float] | None:
    """Return the positive collinear overlap, parameterized on ``p0 -> p1``."""
    dp = p1 - p0
    dq = q1 - q0
    lp = float(np.linalg.norm(dp))
    lq = float(np.linalg.norm(dq))
    if lp <= distance_tolerance or lq <= distance_tolerance:
        return None
    up = dp / lp
    uq = dq / lq
    if float(np.linalg.norm(np.cross(up, uq))) > angle_tolerance:
        return None
    # The two centre-line edges must be on the same infinite line.
    if float(np.linalg.norm(np.cross(q0 - p0, up))) > distance_tolerance:
        return None
    if float(np.linalg.norm(np.cross(q1 - p0, up))) > distance_tolerance:
        return None
    tq0 = float(np.dot(q0 - p0, up))
    tq1 = float(np.dot(q1 - p0, up))
    lo = max(0.0, min(tq0, tq1))
    hi = min(lp, max(tq0, tq1))
    if hi - lo <= distance_tolerance:
        return None
    return p0 + up * lo, p0 + up * hi, lo / lp, hi / lp


def _partial_face_vertices(
    model: Model, quad: Quad, face: int, t0: float, t1: float,
) -> list[np.ndarray]:
    """Clip a lateral Quad face to a centre-line parameter interval."""
    assert model.collections is not None
    nxt = (face + 1) % 4
    n0 = _v(model.collections.nodes[quad.node_keys[face]].point)
    n1 = _v(model.collections.nodes[quad.node_keys[nxt]].point)
    normal0 = _unit(_v(quad.normal[face]), label=f"Quad {quad.key} normal")
    normal1 = _unit(_v(quad.normal[nxt]), label=f"Quad {quad.key} normal")
    minus0 = n0 - normal0 * quad.thickness[face] / 2.0
    plus0 = n0 + normal0 * quad.thickness[face] / 2.0
    minus1 = n1 - normal1 * quad.thickness[nxt] / 2.0
    plus1 = n1 + normal1 * quad.thickness[nxt] / 2.0

    def lerp(a: np.ndarray, b: np.ndarray, t: float) -> np.ndarray:
        return a + (b - a) * t

    ma, mb = lerp(minus0, minus1, t0), lerp(minus0, minus1, t1)
    pa, pb = lerp(plus0, plus1, t0), lerp(plus0, plus1, t1)
    if face in (0, 3):
        return [ma, mb, pb, pa]
    return [mb, ma, pa, pb]


def _quad_contact_pairs(model: Model) -> list[tuple[Quad, int, Quad, int, list[np.ndarray], tuple[int, int], float]]:
    """Generate C# GIQuadQuad contacts for full and collinear partial edges.

    The exact-node map handles the common conforming mesh quickly.  Boundary
    edges are then checked for T-junction/partition overlaps such as one long
    Quad face touching two shorter faces.
    """
    assert model.collections is not None
    c = model.collections
    edge_map = _edge_face_map(c.quads.values())
    for edge, attached in edge_map.items():
        if len(attached) > 2:
            raise ModelPreparationError(
                f"Edge {edge} is shared by {len(attached)} Quads; non-manifold contacts are unsupported."
            )

    contacts: dict[tuple[int, int, int, int], tuple[Quad, int, Quad, int, list[np.ndarray], tuple[int, int], float]] = {}
    boundary: list[tuple[Quad, int, np.ndarray, np.ndarray]] = []
    for attached in edge_map.values():
        if len(attached) == 2:
            (qa, fa), (qb, fb) = sorted(attached, key=lambda pair: pair[0].key)
            vertices = _quad_face_vertices(model, qa, fa)
            nodes = _edge_node_order(qa, fa)
            contacts[(qa.key, qb.key, fa, fb)] = (qa, fa, qb, fb, vertices, nodes, float(qa.length[fa]))
        elif len(attached) == 1:
            quad, face = attached[0]
            p0 = _v(c.nodes[quad.node_keys[face]].point)
            p1 = _v(c.nodes[quad.node_keys[(face + 1) % 4]].point)
            boundary.append((quad, face, p0, p1))

    for i, (qa, fa, ap0, ap1) in enumerate(boundary):
        for qb, fb, bp0, bp1 in boundary[i + 1:]:
            if qa.key == qb.key:
                continue
            if qa.key < qb.key:
                q1, f1, p0, p1, q2, f2, r0, r1 = qa, fa, ap0, ap1, qb, fb, bp0, bp1
            else:
                q1, f1, p0, p1, q2, f2, r0, r1 = qb, fb, bp0, bp1, qa, fa, ap0, ap1
            overlap = _segment_overlap(p0, p1, r0, r1)
            if overlap is None:
                continue
            a, b, t0, t1 = overlap
            # A full exact edge was already inserted from the node-key map.
            signature = (q1.key, q2.key, f1, f2)
            if signature in contacts:
                continue
            vertices = _partial_face_vertices(model, q1, f1, t0, t1)
            start_key = _find_or_create_geometric_node(model, a)
            end_key = _find_or_create_geometric_node(model, b)
            node_order = (end_key, start_key) if f1 in (0, 3) else (start_key, end_key)
            contacts[signature] = (q1, f1, q2, f2, vertices, node_order, float(np.linalg.norm(b - a)))

    return [contacts[key] for key in sorted(contacts)]

def _generate_interfaces(model: Model) -> tuple[int, int]:
    assert model.collections is not None
    c = model.collections
    c.interfaces.clear()
    for quad in c.quads.values():
        quad.interface_keys = [[] for _ in range(6)]
    key = 1
    qq = 0
    qr = 0
    # C# GIQuadQuad scans parent 1, parent 2, then face indices.  The
    # generated order is observable in serialized interface keys.
    for q1, f1, q2, f2, vertices, node_order, contact_length in _quad_contact_pairs(model):
        intf = Interface(
            key=key,
            name=str(key),
            parent_element_key1=q1.key,
            parent_element_key2=q2.key,
            parent_type_element1="Quad",
            parent_type_element2="Quad",
            face1=f1,
            face2=f2,
            thickness=[sum(q1.thickness) / 4.0, sum(q2.thickness) / 4.0],
            nrow=max(int(model.interface_nrow), 2 * (int(0.5 * max(q1.thickness) / model.interface_imax) + 1)),
            ncol=max(int(model.interface_nrow), 2 * (int(0.5 * contact_length / model.interface_imax) + 1)),
            nspring=max(int(model.interface_nrow), 2 * (int(0.5 * contact_length / model.interface_imax) + 1)),
            dim_aff=[6, 2, 4], dim_aff_tot=12, imax=int(model.interface_imax),
        )
        _make_interface_geometry(model, intf, vertices, node_order, _v(q1.g))
        c.interfaces[key] = intf
        q1.interface_keys[f1].append(key)
        q2.interface_keys[f2].append(key)
        key += 1
        qq += 1

    for restraint in sorted(c.restraints.values(), key=lambda item: item.key):
        if restraint.computational_element_type != "Quad":
            raise ModelPreparationError(
                f"Restraint {restraint.key} targets unsupported element type "
                f"{restraint.computational_element_type!r}."
            )
        if any(abs(value + 1.0) > 1.0e-12 for value in restraint.k):
            raise ModelPreparationError(
                f"Restraint {restraint.key} is not fully fixed; elastic/free restraint DOFs are not translated."
            )
        try:
            quad = c.quads[restraint.computational_element_key]
        except KeyError as exc:
            raise ModelPreparationError(
                f"Restraint {restraint.key} references missing Quad {restraint.computational_element_key}."
            ) from exc
        face = restraint.computational_element_edge
        vertices = [_v(point) for point in restraint.points]
        n1, n2 = restraint.node_keys
        intf = Interface(
            key=key,
            name=str(key),
            parent_element_key1=restraint.key,
            parent_element_key2=quad.key,
            parent_type_element1="Restraint",
            parent_type_element2="Quad",
            face1=0,
            face2=face,
            thickness=[sum(quad.thickness) / 4.0, sum(quad.thickness) / 4.0],
            nrow=max(int(model.interface_nrow), 2 * (int(0.5 * max(quad.thickness) / model.interface_imax) + 1)),
            ncol=max(int(model.interface_nrow), 2 * (int(0.5 * np.linalg.norm(_v(c.nodes[n2].point)-_v(c.nodes[n1].point)) / model.interface_imax) + 1)),
            nspring=max(int(model.interface_nrow), 2 * (int(0.5 * np.linalg.norm(_v(c.nodes[n2].point)-_v(c.nodes[n1].point)) / model.interface_imax) + 1)),
            dim_aff=[6, 2, 4], dim_aff_tot=12, imax=int(model.interface_imax),
            interfaccia_vincolata=True,
        )
        _make_interface_geometry(model, intf, vertices, (n1, n2), None)
        c.interfaces[key] = intf
        quad.interface_keys[face].append(key)
        key += 1
        qr += 1
    return qq, qr


def _assign_quad_afference(model: Model) -> None:
    assert model.collections is not None
    gdl = 1
    for quad in sorted(model.collections.quads.values(), key=lambda item: item.key):
        if quad.master_element_key not in (0, -1):
            raise ModelPreparationError(
                f"Quad {quad.key} is a slave of {quad.master_element_type} {quad.master_element_key}; "
                "slave-element constraints are not translated."
            )
        quad.aff = [[AfferenceEntry(gdl=gdl + i, alfa=1.0)] for i in range(7)]
        gdl += 7
    model.gdl = gdl - 1


def _warping_nodal_vectors(quad: Quad) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    e1 = np.asarray(quad.reference_e1, dtype=float)
    e2 = np.asarray(quad.reference_e2, dtype=float)
    zero = np.zeros(3)
    if abs(quad.sin[2]) <= 1.0e-12:
        node2 = zero.copy()
    else:
        node2 = -quad.length[3] * quad.sin[3] / quad.sin[2] * (
            quad.sin[1] * e1 + quad.cos[1] * e2
        )
    node3 = -quad.length[3] * (quad.sin[0] * e1 - quad.cos[0] * e2)
    return zero.copy(), zero.copy(), node2, node3


def _warping_vector_at_point(quad: Quad, point: np.ndarray, model: Model) -> np.ndarray:
    """C# ``GetDisplacementFromShearDOF`` on a lateral-interface endpoint.

    The C# method bilinearly interpolates the four nodal shear-displacement
    vectors at the projected point.  Interface endpoints lie on a Quad edge,
    where that interpolation reduces to a linear interpolation of the two edge
    nodal vectors.  This also supports partial-edge contacts whose endpoint node
    is not a vertex of both parent Quads.
    """
    assert model.collections is not None
    vertices = [_v(model.collections.nodes[key].point) for key in quad.node_keys]
    warping = _warping_nodal_vectors(quad)
    scale = max(max(float(np.linalg.norm(vertices[(i + 1) % 4] - vertices[i])) for i in range(4)), 1.0)
    tolerance = max(1.0e-4, scale * 1.0e-8)
    for i in range(4):
        a = vertices[i]
        b = vertices[(i + 1) % 4]
        edge = b - a
        length2 = float(np.dot(edge, edge))
        if length2 <= tolerance * tolerance:
            continue
        t = float(np.dot(point - a, edge) / length2)
        if t < -1.0e-7 or t > 1.0 + 1.0e-7:
            continue
        projected = a + edge * min(max(t, 0.0), 1.0)
        if float(np.linalg.norm(point - projected)) <= tolerance:
            t = min(max(t, 0.0), 1.0)
            return warping[i] + (warping[(i + 1) % 4] - warping[i]) * t
    raise ModelPreparationError(
        f"Interface endpoint {point.tolist()} does not lie on a lateral face of Quad {quad.key}."
    )


def _point_afference(model: Model, quad: Quad, point: np.ndarray, node_key: int, direction: np.ndarray) -> list[AfferenceEntry]:
    r = point - _v(quad.g)
    coeff = np.zeros(7)
    coeff[:3] = direction
    coeff[3:6] = np.cross(r, direction)
    coeff[6] = float(np.dot(_warping_vector_at_point(quad, point, model), direction))
    out: list[AfferenceEntry] = []
    # C# Quad.PointAfference delegates to
    # AfferenceMatrix.SetFromCoefficients, which discards coefficients whose
    # absolute value is not greater than 1e-4.
    for local, value in enumerate(coeff):
        if abs(value) <= 1.0e-4:
            continue
        for entry in quad.aff[local]:
            out.append(AfferenceEntry(gdl=entry.gdl, alfa=float(value * entry.alfa)))
    return out


def _rotation_afference(quad: Quad, direction: np.ndarray) -> list[AfferenceEntry]:
    out: list[AfferenceEntry] = []
    for local in range(3, 6):
        value = float(direction[local - 3])
        # InterfacePoligonalOperations.ComputeAff applies the same 1e-4
        # directional cutoff before adding rotational afference terms.
        if abs(value) <= 1.0e-4:
            continue
        for entry in quad.aff[local]:
            out.append(AfferenceEntry(gdl=entry.gdl, alfa=value * entry.alfa))
    return out


def _assign_interface_afference(model: Model) -> None:
    assert model.collections is not None
    c = model.collections
    for intf in c.interfaces.values():
        intf.aff = [[] for _ in range(12)]
        e1 = np.asarray(intf.reference_e1, dtype=float)
        e2 = np.asarray(intf.reference_e2, dtype=float)
        e3 = np.asarray(intf.reference_e3, dtype=float)
        points = [_v(c.nodes[k].point) for k in intf.node_keys]
        parents = [
            (intf.parent_type_element1, intf.parent_element_key1, 0),
            (intf.parent_type_element2, intf.parent_element_key2, 1),
        ]
        for typ, key, side in parents:
            if typ == "Restraint":
                continue
            if typ != "Quad":
                raise ModelPreparationError(f"Interface {intf.key} has unsupported parent type {typ!r}.")
            quad = c.quads[key]
            if side == 0:
                slots_e2 = (0, 1)
                slot_rot, slot_flex = 4, 6
                slots_e3 = (8, 9)
            else:
                slots_e2 = (3, 2)
                slot_rot, slot_flex = 5, 7
                slots_e3 = (10, 11)
            intf.aff[slots_e2[0]] = _point_afference(model, quad, points[0], intf.node_keys[0], e2)
            intf.aff[slots_e2[1]] = _point_afference(model, quad, points[1], intf.node_keys[1], e2)
            intf.aff[slot_rot] = _rotation_afference(quad, e1)
            intf.aff[slot_flex] = _point_afference(model, quad, points[1], intf.node_keys[1], e1)
            intf.aff[slots_e3[0]] = _point_afference(model, quad, points[0], intf.node_keys[0], e3)
            intf.aff[slots_e3[1]] = _point_afference(model, quad, points[1], intf.node_keys[1], e3)
        intf.status = InterfaceState()
        intf.status.init_from_interface(intf)
        intf._perf_aff_pairs = None


def _quad_vint(model: Model, quad: Quad) -> tuple[np.ndarray, ...]:
    cached = getattr(quad, "_prep_vint", None)
    if cached is not None:
        return cached
    faces = [np.asarray(_quad_face_vertices(model, quad, face), dtype=float) for face in range(4)]
    faces.append(np.asarray([faces[2][1], faces[0][1], faces[0][0], faces[2][0]], dtype=float))
    faces.append(np.asarray([faces[2][3], faces[0][3], faces[0][2], faces[2][2]], dtype=float))
    cached = tuple(faces)
    quad._prep_vint = cached
    return cached


def _bilinear(vertices: Sequence[np.ndarray], u: float, v: float) -> np.ndarray:
    return (
        vertices[0] * (1.0-u)*(1.0-v)/4.0
        + vertices[1] * (1.0+u)*(1.0-v)/4.0
        + vertices[2] * (1.0+u)*(1.0+v)/4.0
        + vertices[3] * (1.0-u)*(1.0+v)/4.0
    )


def _inverse_bilinear(vertices: Sequence[np.ndarray], point: np.ndarray) -> tuple[float, float]:
    # C# solves a 2x2 Newton system.  Avoiding np.linalg.lstsq for this tiny,
    # repeated system removes tens of thousands of LAPACK/Python crossings.
    normal = np.cross(vertices[1]-vertices[0], vertices[3]-vertices[0])
    drop = int(np.argmax(np.abs(normal)))
    keep0, keep1 = (1, 2) if drop == 0 else ((0, 2) if drop == 1 else (0, 1))
    target0 = float(point[keep0])
    target1 = float(point[keep1])
    u = v = 0.0
    for _ in range(20):
        mapped = _bilinear(vertices, u, v)
        du = (-vertices[0]*(1-v) + vertices[1]*(1-v) + vertices[2]*(1+v) - vertices[3]*(1+v))/4.0
        dv = (-vertices[0]*(1-u) - vertices[1]*(1+u) + vertices[2]*(1+u) + vertices[3]*(1-u))/4.0
        j00, j01 = float(du[keep0]), float(dv[keep0])
        j10, j11 = float(du[keep1]), float(dv[keep1])
        r0 = target0 - float(mapped[keep0])
        r1 = target1 - float(mapped[keep1])
        det = j00*j11 - j01*j10
        if abs(det) <= 1.0e-30:
            raise ModelPreparationError("Degenerate bilinear face mapping.")
        delta_u = (j11*r0 - j01*r1) / det
        delta_v = (-j10*r0 + j00*r1) / det
        u += delta_u
        v += delta_v
        if max(abs(delta_u), abs(delta_v)) < 1.0e-10:
            break
    return u, v


def _cell_vertices(intf: Interface, index: int) -> list[np.ndarray]:
    row, col = divmod(index, intf.ncol)
    u0 = col * 2.0 / intf.ncol - 1.0
    u1 = (col+1) * 2.0 / intf.ncol - 1.0
    v0 = row * 2.0 / intf.nrow - 1.0
    v1 = (row+1) * 2.0 / intf.nrow - 1.0
    intrinsic = ((u0,v0),(u1,v0),(u1,v1),(u0,v1))
    vertices = getattr(intf, "_prep_vertices", None)
    if vertices is None:
        vertices = np.asarray([_v(p) for p in intf.vint3d], dtype=float)
        intf._prep_vertices = vertices
    return [_bilinear(vertices, u, v) for u,v in intrinsic]


def _polygon_area_3d(points: Sequence[np.ndarray]) -> float:
    accum = np.zeros(3)
    for idx, point in enumerate(points):
        accum += np.cross(point, points[(idx+1) % len(points)])
    return 0.5 * float(np.linalg.norm(accum))



if njit is not None:
    @njit(cache=True, inline="always")
    def _dot3_nb(a, b):
        return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

    @njit(cache=True, inline="always")
    def _norm3_nb(a):
        return math.sqrt(a[0]*a[0] + a[1]*a[1] + a[2]*a[2])

    @njit(cache=True, inline="always")
    def _cross3_nb(a, b, out):
        out[0] = a[1]*b[2] - a[2]*b[1]
        out[1] = a[2]*b[0] - a[0]*b[2]
        out[2] = a[0]*b[1] - a[1]*b[0]

    @njit(cache=True, inline="always")
    def _bilinear_nb(vertices, u, v, out):
        n0 = (1.0-u)*(1.0-v)/4.0
        n1 = (1.0+u)*(1.0-v)/4.0
        n2 = (1.0+u)*(1.0+v)/4.0
        n3 = (1.0-u)*(1.0+v)/4.0
        for j in range(3):
            out[j] = vertices[0,j]*n0 + vertices[1,j]*n1 + vertices[2,j]*n2 + vertices[3,j]*n3

    @njit(cache=True, inline="always")
    def _inverse_bilinear_nb(vertices, point):
        a = np.empty(3, dtype=np.float64)
        b = np.empty(3, dtype=np.float64)
        normal = np.empty(3, dtype=np.float64)
        for j in range(3):
            a[j] = vertices[1,j] - vertices[0,j]
            b[j] = vertices[3,j] - vertices[0,j]
        _cross3_nb(a, b, normal)
        drop = 0
        if abs(normal[1]) > abs(normal[drop]):
            drop = 1
        if abs(normal[2]) > abs(normal[drop]):
            drop = 2
        if drop == 0:
            k0, k1 = 1, 2
        elif drop == 1:
            k0, k1 = 0, 2
        else:
            k0, k1 = 0, 1
        u = 0.0
        v = 0.0
        mapped = np.empty(3, dtype=np.float64)
        du = np.empty(3, dtype=np.float64)
        dv = np.empty(3, dtype=np.float64)
        for _ in range(20):
            _bilinear_nb(vertices, u, v, mapped)
            for j in range(3):
                du[j] = (-vertices[0,j]*(1.0-v) + vertices[1,j]*(1.0-v) + vertices[2,j]*(1.0+v) - vertices[3,j]*(1.0+v))/4.0
                dv[j] = (-vertices[0,j]*(1.0-u) - vertices[1,j]*(1.0+u) + vertices[2,j]*(1.0+u) + vertices[3,j]*(1.0-u))/4.0
            j00, j01 = du[k0], dv[k0]
            j10, j11 = du[k1], dv[k1]
            r0 = point[k0] - mapped[k0]
            r1 = point[k1] - mapped[k1]
            det = j00*j11 - j01*j10
            if abs(det) <= 1.0e-30:
                return 0.0, 0.0, -1
            delta_u = (j11*r0 - j01*r1) / det
            delta_v = (-j10*r0 + j00*r1) / det
            u += delta_u
            v += delta_v
            if max(abs(delta_u), abs(delta_v)) < 1.0e-10:
                break
        return u, v, 0

    @njit(cache=True, nogil=True)
    def _fiber_stiffness_batch_nb(near_face, far_face, cells, E, reference_e2, output, errors):
        face_a = np.empty(3, dtype=np.float64)
        face_b = np.empty(3, dtype=np.float64)
        face_cross = np.empty(3, dtype=np.float64)
        for j in range(3):
            face_a[j] = near_face[1,j] - near_face[0,j]
            face_b[j] = near_face[3,j] - near_face[0,j]
        _cross3_nb(face_a, face_b, face_cross)
        for idx in range(cells.shape[0]):
            points = cells[idx].copy()
            ca = np.empty(3, dtype=np.float64)
            cb = np.empty(3, dtype=np.float64)
            ccross = np.empty(3, dtype=np.float64)
            for j in range(3):
                ca[j] = points[1,j] - points[0,j]
                cb[j] = points[3,j] - points[0,j]
            _cross3_nb(ca, cb, ccross)
            if _dot3_nb(face_cross, ccross) < 0.0:
                tmp = points[1].copy()
                points[1] = points[3]
                points[3] = tmp
            best_shift = 0
            best_score = 1.0e300
            diff = np.empty(3, dtype=np.float64)
            for shift in range(4):
                score = 0.0
                for k in range(4):
                    pidx = (shift+k) % 4
                    for j in range(3):
                        diff[j] = points[pidx,j] - near_face[k,j]
                    score += _norm3_nb(diff)
                if score < best_score:
                    best_score = score
                    best_shift = shift
            ordered = np.empty((4,3), dtype=np.float64)
            for i in range(4):
                for j in range(3):
                    ordered[i,j] = points[(best_shift+i)%4,j]
            uv = np.empty((4,2), dtype=np.float64)
            far_points = np.empty((4,3), dtype=np.float64)
            error = 0
            for i in range(4):
                u, v, err = _inverse_bilinear_nb(near_face, ordered[i])
                if err:
                    error = 1
                uv[i,0], uv[i,1] = u, v
                _bilinear_nb(far_face, u, v, far_points[i])
            if error:
                errors[idx] = 1
                continue
            uc = (uv[0,0]+uv[1,0]+uv[2,0]+uv[3,0])/4.0
            vc = (uv[0,1]+uv[1,1]+uv[2,1]+uv[3,1])/4.0
            center_near = np.empty(3, dtype=np.float64)
            center_far = np.empty(3, dtype=np.float64)
            _bilinear_nb(near_face, uc, vc, center_near)
            _bilinear_nb(far_face, uc, vc, center_far)
            cvec = np.empty(3, dtype=np.float64)
            for j in range(3):
                cvec[j] = center_far[j] - center_near[j]
            lp = _norm3_nb(cvec)
            if lp <= 1.0e-12:
                errors[idx] = 2
                continue
            for j in range(3):
                cvec[j] /= lp
            p0rel = np.empty(3, dtype=np.float64)
            for j in range(3):
                p0rel[j] = ordered[0,j] - center_near[j]
            axial = _dot3_nb(p0rel, cvec)
            vector3 = np.empty(3, dtype=np.float64)
            for j in range(3):
                vector3[j] = p0rel[j] - axial*cvec[j]
            nvec = _norm3_nb(vector3)
            if nvec <= 1.0e-12:
                errors[idx] = 3
                continue
            for j in range(3):
                vector3[j] /= nvec
            value = np.empty(3, dtype=np.float64)
            _cross3_nb(vector3, cvec, value)
            a5 = np.empty((4,3), dtype=np.float64)
            a7 = np.empty((4,3), dtype=np.float64)
            for i in range(4):
                relp = np.empty(3, dtype=np.float64)
                relf = np.empty(3, dtype=np.float64)
                for j in range(3):
                    relp[j] = ordered[i,j] - center_near[j]
                    relf[j] = far_points[i,j] - center_near[j]
                v4x, v4y, v4z = _dot3_nb(value, relp), _dot3_nb(vector3, relp), _dot3_nb(cvec, relp)
                v6x, v6y, v6z = _dot3_nb(value, relf), _dot3_nb(vector3, relf), _dot3_nb(cvec, relf)
                denom = v4z-v6z
                if abs(denom) <= 1.0e-14:
                    error = 1
                    break
                num6 = v4z/denom
                num7 = -(lp-v4z)/denom
                a5[i,0] = v4x+(v6x-v4x)*num6
                a5[i,1] = v4y+(v6y-v4y)*num6
                a5[i,2] = v4z+(v6z-v4z)*num6
                a7[i,0] = v4x+(v6x-v4x)*num7
                a7[i,1] = v4y+(v6y-v4y)*num7
                a7[i,2] = v4z+(v6z-v4z)*num7
            if error:
                errors[idx] = 4
                continue
            c0 = 0.5*((-(a5[1,0]-a5[3,0]-a7[1,0]+a5[3,0]))*(a5[0,1]-a5[2,1]-a7[0,1]+a5[2,1]) + (a5[0,0]-a5[2,0]-a7[0,0]+a5[2,0])*(a5[1,1]-a5[3,1]-a7[1,1]+a5[3,1]))
            c1 = 0.5*(-2*a5[0,0]*a5[1,1]+2*a5[2,0]*a5[1,1]+a7[0,0]*a5[1,1]-a7[2,0]*a5[1,1]-(a7[1,0]-a7[3,0])*(a5[0,1]-a5[2,1])+2*a5[0,0]*a5[3,1]-2*a5[2,0]*a5[3,1]-a7[0,0]*a5[3,1]+a7[2,0]*a5[3,1]+a5[0,0]*a7[1,1]-a5[2,0]*a7[1,1]+a5[3,0]*(-2*a5[0,1]+2*a5[2,1]+a7[0,1]-a7[2,1])-a5[1,0]*(-2*a5[0,1]+2*a5[2,1]+a7[0,1]-a7[2,1])-a5[0,0]*a7[3,1]+a5[2,0]*a7[3,1])
            c2 = 0.5*(-(a5[1,0]-a5[3,0])*(a5[0,1]-a5[2,1])+(a5[0,0]-a5[2,0])*(a5[1,1]-a5[3,1]))
            signed_area = 0.0
            for i in range(4):
                ni=(i+1)%4
                signed_area += a5[i,0]*a5[ni,1]-a5[ni,0]*a5[i,1]
            signed_area *= 0.5
            if signed_area < 0.0:
                c0, c1, c2 = -c0, -c1, -c2
                signed_area = -signed_area
            if signed_area <= 1.0e-14:
                errors[idx] = 5
                continue
            upper=0.5
            tiny=1.0e-10
            if c0 <= tiny:
                if abs(c1)>tiny:
                    integral=(math.log(abs(upper+c2/c1))-math.log(abs(c2/c1)))/c1
                else:
                    integral=upper/c2
            else:
                disc=c1*c1-4.0*c0*c2
                if disc>0.0:
                    root=math.sqrt(disc); r1=(-c1+root)/(2.0*c0); r2=(-c1-root)/(2.0*c0)
                    integral=(math.log(abs((upper-r1)/(upper-r2)))-math.log(abs((-r1)/(-r2))))/root
                elif disc==0.0:
                    integral=-(1.0/(upper+c1/(2.0*c0))-2.0*c0/c1)/c0
                else:
                    root=math.sqrt(-disc); integral=2.0*(math.atan((2.0*c0*upper+c1)/root)-math.atan(c1/root))/root
            compliance=lp*integral
            edge1=abs(c0*upper*upper+c1*upper+c2)
            edge2=abs(c2)
            area=edge1 if edge1<edge2 else edge2
            projection=abs(_dot3_nb(cvec, reference_e2))
            output[idx,0]=abs(E/compliance*projection)
            output[idx,1]=area
            output[idx,2]=lp*upper
else:
    _fiber_stiffness_batch_nb = None


def _fiber_stiffness_batch(model: Model, quad: Quad, intf: Interface,
                            cells: np.ndarray, E: float, face: int) -> np.ndarray:
    if _fiber_stiffness_batch_nb is None:
        return np.asarray([
            _fiber_stiffness(model, quad, intf, cell, E, face) for cell in cells
        ], dtype=float)
    vints = _quad_vint(model, quad)
    opposite = {0:2,1:3,2:0,3:1,4:5,5:4}[face]
    output = np.zeros((len(cells),3), dtype=np.float64)
    errors = np.zeros(len(cells), dtype=np.int32)
    _fiber_stiffness_batch_nb(
        np.asarray(vints[face], dtype=np.float64),
        np.asarray(vints[opposite], dtype=np.float64),
        np.asarray(cells, dtype=np.float64), float(E),
        np.asarray(intf.reference_e2, dtype=np.float64), output, errors,
    )
    if np.any(errors):
        index = int(np.flatnonzero(errors)[0])
        raise ModelPreparationError(
            f"Quad {quad.key}, Interface {intf.key}: compiled fibre geometry error {errors[index]} at cell {index}."
        )
    return output

def _fiber_stiffness(model: Model, quad: Quad, intf: Interface, cell: Sequence[np.ndarray],
                     E: float, face: int) -> tuple[float, float, float]:
    """Direct port of C# ``Quad.GetFiberProperties/GetFiberStiffness``."""
    vints = _quad_vint(model, quad)
    opposite = {0: 2, 1: 3, 2: 0, 3: 1, 4: 5, 5: 4}[face]
    near_face = vints[face]
    points = [np.asarray(v, dtype=float).copy() for v in cell]

    face_cross = np.cross(near_face[1] - near_face[0], near_face[3] - near_face[0])
    cell_cross = np.cross(points[1] - points[0], points[3] - points[0])
    if float(np.dot(face_cross, cell_cross)) < 0.0:
        points[1], points[3] = points[3], points[1]

    # Rotate the polygon so its vertices correspond to the face vertices.
    scores = []
    for shift in range(4):
        scores.append(sum(_norm3(points[(shift+k) % 4] - near_face[k]) for k in range(4)))
    shift = int(np.argmin(scores))
    points = [points[(shift+i) % 4] for i in range(4)]

    far_face = vints[opposite]
    uv = [_inverse_bilinear(near_face, point) for point in points]
    far_points = [_bilinear(far_face, u, v) for u, v in uv]
    uc = sum(u for u, _ in uv) / 4.0
    vc = sum(v for _, v in uv) / 4.0
    center_near = _bilinear(near_face, uc, vc)
    center_far = _bilinear(far_face, uc, vc)
    lp = _norm3(center_far - center_near)
    if lp <= 1.0e-12:
        raise ModelPreparationError(f"Quad {quad.key}, Interface {intf.key}: zero fibre length.")
    cvec = _unit(center_far - center_near, label="fibre direction")
    axial = float(np.dot(points[0] - center_near, cvec))
    transverse = points[0] - center_near - axial * cvec
    vector3 = _unit(transverse, label="fibre local axis")
    value = np.cross(vector3, cvec)

    a4: list[np.ndarray] = []
    a6: list[np.ndarray] = []
    a5: list[np.ndarray] = []
    a7: list[np.ndarray] = []
    for point, far in zip(points, far_points):
        v4 = np.asarray((
            float(np.dot(value, point-center_near)),
            float(np.dot(vector3, point-center_near)),
            float(np.dot(cvec, point-center_near)),
        ))
        v6 = np.asarray((
            float(np.dot(value, far-center_near)),
            float(np.dot(vector3, far-center_near)),
            float(np.dot(cvec, far-center_near)),
        ))
        denom = v4[2] - v6[2]
        if abs(denom) <= 1.0e-14:
            raise ModelPreparationError(f"Quad {quad.key}, Interface {intf.key}: degenerate fibre projection.")
        num6 = v4[2] / denom
        num7 = -(lp-v4[2]) / denom
        a4.append(v4); a6.append(v6)
        a5.append(v4 + (v6-v4)*num6)
        a7.append(v4 + (v6-v4)*num7)

    c0 = 0.5 * (
        (-(a5[1][0]-a5[3][0]-a7[1][0]+a5[3][0]))
        * (a5[0][1]-a5[2][1]-a7[0][1]+a5[2][1])
        + (a5[0][0]-a5[2][0]-a7[0][0]+a5[2][0])
        * (a5[1][1]-a5[3][1]-a7[1][1]+a5[3][1])
    )
    c1 = 0.5 * (
        -2*a5[0][0]*a5[1][1] + 2*a5[2][0]*a5[1][1]
        + a7[0][0]*a5[1][1] - a7[2][0]*a5[1][1]
        - (a7[1][0]-a7[3][0])*(a5[0][1]-a5[2][1])
        + 2*a5[0][0]*a5[3][1] - 2*a5[2][0]*a5[3][1]
        - a7[0][0]*a5[3][1] + a7[2][0]*a5[3][1]
        + a5[0][0]*a7[1][1] - a5[2][0]*a7[1][1]
        + a5[3][0]*(-2*a5[0][1]+2*a5[2][1]+a7[0][1]-a7[2][1])
        - a5[1][0]*(-2*a5[0][1]+2*a5[2][1]+a7[0][1]-a7[2][1])
        - a5[0][0]*a7[3][1] + a5[2][0]*a7[3][1]
    )
    c2 = 0.5 * (
        -(a5[1][0]-a5[3][0])*(a5[0][1]-a5[2][1])
        + (a5[0][0]-a5[2][0])*(a5[1][1]-a5[3][1])
    )
    coeff = [float(c0), float(c1), float(c2)]
    signed_area = 0.5 * sum(
        a5[i][0]*a5[(i+1)%4][1] - a5[(i+1)%4][0]*a5[i][1]
        for i in range(4)
    )
    if signed_area < 0.0:
        coeff = [-x for x in coeff]
        signed_area = -signed_area
    if signed_area <= 1.0e-14:
        raise ModelPreparationError(f"Quad {quad.key}, Interface {intf.key}: zero fibre area.")

    a, b, cc = coeff
    upper = 0.5
    tiny = 1.0e-10
    if a <= tiny:
        if abs(b) > tiny:
            integral = (math.log(abs(upper + cc/b)) - math.log(abs(cc/b))) / b
        else:
            integral = upper / cc
    else:
        disc = b*b - 4.0*a*cc
        if disc > 0.0:
            root = math.sqrt(disc)
            r1 = (-b+root)/(2.0*a)
            r2 = (-b-root)/(2.0*a)
            integral = (
                math.log(abs((upper-r1)/(upper-r2)))
                - math.log(abs((-r1)/(-r2)))
            ) / root
        elif disc == 0.0:
            integral = -(1.0/(upper+b/(2.0*a)) - 2.0*a/b) / a
        else:
            root = math.sqrt(-disc)
            integral = 2.0 * (
                math.atan((2.0*a*upper+b)/root) - math.atan(b/root)
            ) / root
    compliance = lp * integral
    area = min(abs(a*upper*upper+b*upper+cc), abs(cc))
    half_length = lp*upper
    projection = float(np.dot(cvec, np.asarray(intf.reference_e2, dtype=float)))
    k = abs(E/compliance*projection)
    return k, area, half_length

def _distance_to_interface_plane(quad: Quad, intf: Interface) -> float:
    p0 = _v(intf.vint3d[0])
    normal = _unit(np.cross(_v(intf.vint3d[1])-p0, _v(intf.vint3d[2])-p0), label="interface plane")
    return abs(float(np.dot(_v(quad.g)-p0, normal)))


def _quad_spring(model: Model, quad: Quad) -> SpringCoulomb03 | SpringHysteretic | SpringElastic:
    material = _material(model, quad.material_key)
    flex = _diagonal_flex_law(material)
    shear = _shear_law(material)
    length = quad.d_alfa_2d_diag()
    k = quad.get_diagonal_stiffness(flex.E, shear.E)
    if shear.sub_law in {"Coulomb", "Cacovic"}:
        fy_compression = (
            flex.fy_c
            if flex.law_type.startswith("ElastoPlastic")
            else 10.0 * shear.cohesion
        )
        fy = quad.set_non_linear_properties(
            k, flex.E, shear.E, shear.cohesion, fy_compression
        )
        cos_alpha = quad.cos_alfa
        if shear.fracture_energy:
            strength = min(abs(fy[0]), abs(fy[1]))
            yield_u = strength/k if k else 0.0
            ur = ((shear.G * quad.compute_volume() - 0.5*strength*yield_u)/strength + yield_u) if strength else length*shear.ductility
        else:
            ur = shear.ductility * length
        area = length * quad.diago[1] / quad.length[0] * (sum(quad.thickness)/4.0)
        spring = _configure_coulomb(
            k=k, area=area, length=length, law=shear,
            cohesion_force=min(abs(fy[0]), abs(fy[1])),
            mu=shear.mu/cos_alpha if cos_alpha else shear.mu,
            ur=ur, hysteretic_type="Takeda",
            plastic_strain=(ur if shear.fracture_energy else shear.plastic_strain * length),
            use_second_branch=shear.plastic_stiffness_ratio2 < 0.0,
            sub_law=shear.sub_law,
        )
    else:
        spring = SpringElastic(type_of="HiStrA.Objects.SpringElastic", k=k, area=k*length/shear.E, length=length)
    spring.key = 0
    spring.parent_key = quad.key
    spring.parent_type = "Quad"
    spring.spring_purpose = "Diagonal"
    return spring


def _side_transverse_spring(model: Model, parent_type: str, parent_key: int, face: int,
                            intf: Interface, cell: Sequence[np.ndarray],
                            material_override: MasonryMaterial | None = None) -> tuple[SpringHysteretic, _HystereticLaw]:
    assert model.collections is not None
    if parent_type == "Restraint":
        sp = SpringHysteretic(type_of="HiStrA.Objects.SpringHysteretic")
        sp.k = -1.0
        sp.area = _polygon_area_3d(cell)
        if material_override is not None:
            return sp, _flex_law(material_override)
        quad_key = (
            intf.parent_element_key1
            if intf.parent_type_element1 == "Quad"
            else intf.parent_element_key2
        )
        return sp, _flex_law(_material(model, model.collections.quads[quad_key].material_key))
    quad = model.collections.quads[parent_key]
    material = material_override if material_override is not None else _material(model, quad.material_key)
    # Current bridge materials are flexurally isotropic. Choose vertical for
    # predominantly vertical interface normal, horizontal otherwise.
    vertical = abs(float(np.dot(np.asarray(intf.reference_e2), np.asarray((0.0,0.0,1.0))))) > math.cos(math.radians(45.0))
    law = _flex_law(material, vertical=vertical)
    k, area, length = _fiber_stiffness(model, quad, intf, cell, law.E, face)
    return _configure_hysteretic(k, area, length, law), law


def _side_sliding_spring(model: Model, parent_type: str, parent_key: int, intf: Interface,
                         *, out_of_plane: bool, area: float, vertical: bool,
                         material_override: MasonryMaterial | None = None) -> SpringCoulomb03:
    assert model.collections is not None
    if parent_type == "Restraint":
        spring = SpringCoulomb03(type_of="HiStrA.Objects.SpringCoulomb03")
        spring.k = -1.0
        spring.area = area
        return spring
    quad = model.collections.quads[parent_key]
    material = material_override if material_override is not None else _material(model, quad.material_key)
    law = _sliding_law(material, out_of_plane=out_of_plane, vertical=vertical)
    distance = _distance_to_interface_plane(quad, intf)
    if distance <= 1.0e-12:
        raise ModelPreparationError(f"Quad {quad.key}, Interface {intf.key}: zero sliding distance.")
    # ``area`` is already the half-interface area for the two-spring
    # out-of-plane torsion model. C# GetOutOfPlaneSlidingStiffness also uses
    # Interface.Area()/2, so no second division is applied here.
    effective_area = area
    k = law.E * effective_area / distance
    spring = _configure_coulomb(k=k, area=area, length=intf.length, law=law,
                                cohesion_force=area*law.cohesion, ur=100000.0,
                                hysteretic_type="Initial")
    spring.plastic_strain_ratio = 1.0
    return spring


def _transverse_side_properties_batch(
    model: Model, parent_type: str, parent_key: int, face: int,
    intf: Interface, cells: np.ndarray,
    material_override: MasonryMaterial | None = None,
) -> tuple[np.ndarray, _HystereticLaw]:
    assert model.collections is not None
    if parent_type == "Restraint":
        props = np.zeros((len(cells), 3), dtype=np.float64)
        props[:, 0] = -1.0
        props[:, 1] = np.asarray([_polygon_area_3d(cell) for cell in cells])
        if material_override is not None:
            law = _flex_law(material_override)
        else:
            quad_key = (
                intf.parent_element_key1
                if intf.parent_type_element1 == "Quad"
                else intf.parent_element_key2
            )
            law = _flex_law(_material(model, model.collections.quads[quad_key].material_key))
        return props, law
    quad = model.collections.quads[parent_key]
    material = material_override if material_override is not None else _material(model, quad.material_key)
    vertical = abs(float(np.dot(
        np.asarray(intf.reference_e2), np.asarray((0.0, 0.0, 1.0))
    ))) > math.cos(math.radians(45.0))
    law = _flex_law(material, vertical=vertical)
    return _fiber_stiffness_batch(model, quad, intf, cells, law.E, face), law


def _create_interface_springs(model: Model, intf: Interface) -> None:
    restrained = intf.parent_type_element1 == "Restraint" or intf.parent_type_element2 == "Restraint"
    custom_material = None
    if int(intf.material_key) != 0:
        custom_material = _material(model, int(intf.material_key))
    cell_count = intf.nrow * intf.ncol
    cells = np.asarray([_cell_vertices(intf, index) for index in range(cell_count)], dtype=np.float64)
    props1, law1 = _transverse_side_properties_batch(
        model, intf.parent_type_element1, intf.parent_element_key1,
        intf.face1, intf, cells, custom_material,
    )
    props2, law2 = _transverse_side_properties_batch(
        model, intf.parent_type_element2, intf.parent_element_key2,
        intf.face2, intf, cells, custom_material,
    )
    intf.trasv_1 = []
    for index in range(cell_count):
        k1, area1, length1 = map(float, props1[index])
        k2, area2, length2 = map(float, props2[index])
        if k1 == -1.0:
            sp1 = SpringHysteretic(type_of="HiStrA.Objects.SpringHysteretic")
            sp1.k, sp1.area = -1.0, area1
        else:
            sp1 = _configure_hysteretic(k1, area1, length1, law1)
        if k2 == -1.0:
            sp2 = SpringHysteretic(type_of="HiStrA.Objects.SpringHysteretic")
            sp2.k, sp2.area = -1.0, area2
        else:
            sp2 = _configure_hysteretic(k2, area2, length2, law2)
        if custom_material is not None and restrained:
            # C# Interface.SetSpring: for a custom material on a restraint/Quad
            # interface, clone the non-restraint spring rather than combining
            # it with the rigid restraint-side placeholder.
            spring = copy.deepcopy(sp2 if intf.parent_type_element1 == "Restraint" else sp1)
        else:
            spring = _combine_hysteretic(sp1, sp2, restrained, law1, law2)
        spring.key = index
        spring.parent_key = intf.key
        spring.parent_type = "Interface"
        spring.spring_purpose = "Transversal1"
        spring.length = 0.0
        intf.trasv_1.append(spring)

    area = intf.area()
    vertical = abs(float(np.dot(np.asarray(intf.reference_e2), np.asarray((0.0,0.0,1.0))))) > math.cos(math.radians(45.0))
    s1 = _side_sliding_spring(model, intf.parent_type_element1, intf.parent_element_key1, intf,
                              out_of_plane=False, area=area, vertical=vertical,
                              material_override=custom_material)
    s2 = _side_sliding_spring(model, intf.parent_type_element2, intf.parent_element_key2, intf,
                              out_of_plane=False, area=area, vertical=vertical,
                              material_override=custom_material)
    slid = _combine_coulomb(s1, s2, restrained)
    # C# invokes SetUltimateDisplacement after combining both sides.
    def _law_for(parent_type: str, parent_key: int, *, out_plane: bool) -> _CoulombLaw:
        if custom_material is not None:
            return _sliding_law(
                custom_material, out_of_plane=out_plane, vertical=vertical
            )
        if parent_type == "Restraint":
            if intf.parent_type_element1 == "Quad":
                other_key = intf.parent_element_key1
            elif intf.parent_type_element2 == "Quad":
                other_key = intf.parent_element_key2
            else:
                raise ModelPreparationError(
                    f"Interface {intf.key} has a restraint but no Quad parent."
                )
            return _sliding_law(
                _material(model, model.collections.quads[other_key].material_key),
                out_of_plane=out_plane,
                vertical=vertical,
            )
        return _sliding_law(
            _material(model, model.collections.quads[parent_key].material_key),
            out_of_plane=out_plane,
            vertical=vertical,
        )
    _set_coulomb_ultimate(
        slid,
        _law_for(intf.parent_type_element1, intf.parent_element_key1, out_plane=False),
        _law_for(intf.parent_type_element2, intf.parent_element_key2, out_plane=False),
    )
    slid.key = 0; slid.parent_key = intf.key; slid.parent_type = "Interface"; slid.spring_purpose = "Slid"
    slid.length = intf.length
    intf.slid = [slid]

    intf.slid_out_plan = []
    for index in range(2):
        half_area = area / 2.0
        o1 = _side_sliding_spring(model, intf.parent_type_element1, intf.parent_element_key1, intf,
                                  out_of_plane=True, area=half_area, vertical=vertical,
                                  material_override=custom_material)
        o2 = _side_sliding_spring(model, intf.parent_type_element2, intf.parent_element_key2, intf,
                                  out_of_plane=True, area=half_area, vertical=vertical,
                                  material_override=custom_material)
        out = _combine_coulomb(o1, o2, restrained)
        _set_coulomb_ultimate(
            out,
            _law_for(intf.parent_type_element1, intf.parent_element_key1, out_plane=True),
            _law_for(intf.parent_type_element2, intf.parent_element_key2, out_plane=True),
        )
        out.key=index; out.parent_key=intf.key; out.parent_type="Interface"; out.spring_purpose="SlidOutOfPlan"
        out.area=half_area; out.length=intf.length/2.0
        intf.slid_out_plan.append(out)

    intf.status = InterfaceState()
    intf.status.init_from_interface(intf)
    intf._perf_di = intf._perf_dj = intf._perf_ecc = None
    intf._perf_area = None


def rebuild_interface_springs(model: Model, interface: Interface | int) -> Interface:
    """Recreate one interface's constitutive definitions from its material key.

    Geometry, topology, DOFs and afference matrices are preserved.  A nonzero
    ``Interface.material_key`` overrides both parent material laws, matching
    C# ``InterfaceOperations.ReSetInterfaces``.
    """
    if model.collections is None:
        raise ModelPreparationError("Model.collections is not initialized.")
    intf = (
        model.collections.interfaces[int(interface)]
        if isinstance(interface, int)
        else interface
    )
    _create_interface_springs(model, intf)
    return intf


def prepare_model(model: Model, *, force: bool = False) -> PreparationReport:
    """Prepare an unlocked Quad/Restraint HRX for the nonlinear solver.

    The operation is idempotent for an already prepared model unless ``force``
    is true.  Existing generated interfaces/springs are replaced only when a
    fresh preparation is required.
    """
    if model.collections is None:
        raise ModelPreparationError("Model.collections is not initialized.")
    from .validation import inspect_solver_readiness
    current = inspect_solver_readiness(model)
    if current.is_ready and not force:
        c = model.collections
        return PreparationReport(
            prepared=False, gdl=model.gdl, quads=len(c.quads),
            quad_springs=sum(q.spring is not None for q in c.quads.values()),
            interfaces=len(c.interfaces),
            quad_quad_interfaces=sum(i.parent_type_element1=="Quad" and i.parent_type_element2=="Quad" for i in c.interfaces.values()),
            restraint_interfaces=sum("Restraint" in (i.parent_type_element1,i.parent_type_element2) for i in c.interfaces.values()),
            transverse_springs=sum(len(i.trasv_1) for i in c.interfaces.values()),
            sliding_springs=sum(len(i.slid) for i in c.interfaces.values()),
            out_of_plane_springs=sum(len(i.slid_out_plan) for i in c.interfaces.values()),
        )
    c = model.collections
    if not c.quads:
        raise ModelPreparationError("PrepareModel currently requires at least one Quad.")
    _assign_quad_afference(model)
    for quad in c.quads.values():
        quad.status = QuadState()
        quad.spring = _quad_spring(model, quad)
        quad._perf_aff_pairs = None
        quad._perf_dn_edges = None
        quad._perf_dn_areas = None
    qq, qr = _generate_interfaces(model)
    _assign_interface_afference(model)
    for intf in c.interfaces.values():
        _create_interface_springs(model, intf)
    model.is_locked = True
    report = inspect_solver_readiness(model)
    if not report.is_ready:
        raise ModelPreparationError(
            "Python PrepareModel produced an incomplete model: " + "; ".join(report.missing)
        )
    return PreparationReport(
        prepared=True, gdl=model.gdl, quads=len(c.quads),
        quad_springs=sum(q.spring is not None for q in c.quads.values()),
        interfaces=len(c.interfaces), quad_quad_interfaces=qq, restraint_interfaces=qr,
        transverse_springs=sum(len(i.trasv_1) for i in c.interfaces.values()),
        sliding_springs=sum(len(i.slid) for i in c.interfaces.values()),
        out_of_plane_springs=sum(len(i.slid_out_plan) for i in c.interfaces.values()),
    )
