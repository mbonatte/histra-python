"""Port of the Quad/Restraint subset of C# ``ModelManager.PrepareModel``.

The original desktop preprocessor supports many computational element types.
This module implements the masonry-Quad solver path needed by the supplied
RailBridge models, including the C# six-face surface-intersection topology:

* four-node masonry ``Quad`` elements;
* coplanar polygonal intersections on all six Quad faces;
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
_CONTACT_DISTANCE_TOLERANCE = 2.0e-4
_CONTACT_ANGLE_TOLERANCE = 1.0e-5
_CONTACT_AREA_TOLERANCE = 1.0e-6
_CONTACT_BATCH_SIZE = 4096


def _interface_division_count(size: float, *, minimum: int, imax: float) -> int:
    """Return C# ``Interface.Set``'s even subdivision count.

    XNA geometry is evaluated in single precision.  Add the same contact
    tolerance used by the C# intersection search before the integer boundary
    so values such as 159.99996 mm do not fall below the intended 160 mm bin.
    """
    if imax <= 0.0:
        raise ModelPreparationError(f"Interface maximum size must be positive, got {imax}.")
    csharp_size = float(np.float32(size))
    return max(
        int(minimum),
        2 * (int(0.5 * (csharp_size + _CONTACT_DISTANCE_TOLERANCE) / imax) + 1),
    )


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
class _HystereticSideDefinition:
    k: float
    area: float
    length: float
    fy_t: float
    fy_c: float
    kt_t: float
    kt_c: float
    alfa_r_t: float
    alfa_r_c: float
    alfa_u_t: float
    alfa_u_c: float
    tensile_curve: str
    compressive_curve: str


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


@dataclass(frozen=True)
class _QuadAfferenceGeometry:
    centre: np.ndarray
    vertices: np.ndarray
    normal: np.ndarray
    warping_nodal: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]


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


def _cross3(first: Sequence[float], second: Sequence[float]) -> np.ndarray:
    """Three-component cross product without NumPy axis dispatch.

    ``np.cross`` spends most of its time normalizing axes for the very small
    vectors used throughout preprocessing.  Keeping the scalar operation here
    preserves the same arithmetic while avoiding hundreds of thousands of
    temporary arrays and ``moveaxis`` calls.
    """
    ax, ay, az = float(first[0]), float(first[1]), float(first[2])
    bx, by, bz = float(second[0]), float(second[1]), float(second[2])
    return np.asarray(
        (ay * bz - az * by, az * bx - ax * bz, ax * by - ay * bx),
        dtype=float,
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


def _sliding_law(
    material: MasonryMaterial,
    *,
    out_of_plane: bool,
    direction: str,
) -> _CoulombLaw:
    """Return one of C#'s horizontal, vertical or direction-3 laws.

    ``ConstitutiveLawOperations`` creates three in-plane laws and three
    out-of-plane laws.  Direction 3 is materially different for in-plane
    sliding: it uses ``Gd`` directly, while horizontal/vertical use
    ``2*Gd/(1-AlfaShear)``.  This distinction is decisive on Quad faces 4/5.
    """
    normalized = direction.casefold()
    if normalized not in {"hor", "vert", "dir3"}:
        raise ValueError(f"Unsupported sliding-law direction {direction!r}.")
    if out_of_plane or normalized == "dir3":
        E = _float(material, "Gd")
    else:
        alpha = _float(material, "AlfaShearUser", 0.9)
        if abs(1.0 - alpha) <= 1.0e-12:
            raise ModelPreparationError(f"Material {material.key} has AlfaShearUser=1.")
        E = 2.0 * _float(material, "Gd") / (1.0 - alpha)

    if normalized == "hor":
        suffix = "Hor"
        fracture_name = "SlidingFractureEnergy"
        energy_name = "Gs"
        max_tensile_name = "SlidingMaxTensileRatioHor"
    elif normalized == "vert":
        suffix = "Vert"
        fracture_name = "SlidingFractureEnergyVer"
        energy_name = "GsVer"
        max_tensile_name = "SlidingMaxTensileRatioVer"
    else:
        suffix = "Dir3"
        fracture_name = "SlidingFractureEnergyDir3"
        energy_name = "GsDir3"
        # C# uses the vertical maximum-tension ratio for direction 3.
        max_tensile_name = "SlidingMaxTensileRatioVer"
    return _CoulombLaw(
        E=E,
        cohesion=_float(material, f"CohesionSliding{suffix}"),
        mu=_float(material, f"FrictionRatioSliding{suffix}"),
        plastic_stiffness_ratio=_float(material, f"SlidingPlasticStiffnessRatio{suffix}"),
        max_tensile_ratio=_float(material, max_tensile_name, 0.8),
        sub_law=str(material.value(f"SlidingYieldingDomain{suffix}", "Coulomb")),
        hysteretic_type="Initial",
        fracture_energy=_bool(material, fracture_name, False),
        G=_float(material, energy_name),
        ductility=100000.0,
        is_ductility_fixed=True,
        check_contact_area=_bool(material, "CheckContactArea", False),
    )


def _cached_flex_law(
    material: MasonryMaterial,
    *,
    vertical: bool,
    cache: dict[tuple[int, bool], _HystereticLaw] | None,
) -> _HystereticLaw:
    if cache is None:
        return _flex_law(material, vertical=vertical)
    key = (id(material), bool(vertical))
    law = cache.get(key)
    if law is None:
        law = _flex_law(material, vertical=vertical)
        cache[key] = law
    return law


def _cached_diagonal_laws(
    material: MasonryMaterial,
    cache: dict[int, tuple[_HystereticLaw, _CoulombLaw]] | None,
) -> tuple[_HystereticLaw, _CoulombLaw]:
    if cache is None:
        return _diagonal_flex_law(material), _shear_law(material)
    key = id(material)
    laws = cache.get(key)
    if laws is None:
        laws = (_diagonal_flex_law(material), _shear_law(material))
        cache[key] = laws
    return laws


def _cached_sliding_law(
    material: MasonryMaterial,
    *,
    out_of_plane: bool,
    direction: str,
    cache: dict[tuple[int, bool, str], _CoulombLaw] | None,
) -> _CoulombLaw:
    if cache is None:
        return _sliding_law(
            material, out_of_plane=out_of_plane, direction=direction
        )
    key = (id(material), bool(out_of_plane), direction.casefold())
    law = cache.get(key)
    if law is None:
        law = _sliding_law(
            material, out_of_plane=out_of_plane, direction=direction
        )
        cache[key] = law
    return law


def _blend_coulomb_laws(
    primary: _CoulombLaw,
    secondary: _CoulombLaw,
    c1: float,
    c2: float,
) -> _CoulombLaw:
    """Port ``ConstitutiveLawCoulomb.PropOrthotropyParameter``.

    The C# method modifies only E, Fy_0, Mu and U_r.  Other envelope settings
    remain those of the primary (horizontal) law.
    """
    w1 = float(c1) * float(c1)
    w2 = float(c2) * float(c2)
    return _CoulombLaw(
        E=primary.E * w1 + secondary.E * w2,
        cohesion=primary.cohesion * w1 + secondary.cohesion * w2,
        mu=primary.mu * w1 + secondary.mu * w2,
        plastic_stiffness_ratio=primary.plastic_stiffness_ratio,
        max_tensile_ratio=primary.max_tensile_ratio,
        reload_stiffness_ratio=primary.reload_stiffness_ratio,
        plastic_stiffness_ratio2=primary.plastic_stiffness_ratio2,
        plastic_strain=primary.plastic_strain,
        sub_law=primary.sub_law,
        hysteretic_type=primary.hysteretic_type,
        fracture_energy=primary.fracture_energy,
        G=primary.G,
        ductility=primary.ductility * w1 + secondary.ductility * w2,
        is_ductility_fixed=primary.is_ductility_fixed,
        check_contact_area=primary.check_contact_area,
        bcacovic=primary.bcacovic,
    )


def _interface_sliding_law(
    model: Model,
    intf: Interface,
    *,
    parent_type: str,
    parent_key: int,
    face: int,
    material: MasonryMaterial,
    out_of_plane: bool,
    vertical: bool,
    cache: dict[tuple[int, bool, str], _CoulombLaw] | None,
) -> _CoulombLaw:
    """Select/blend the same constitutive-law slot used by C# Interface.SetSpring."""
    assert model.collections is not None
    effective_face = int(face)
    quad = None
    if parent_type == "Quad":
        quad = model.collections.quads[parent_key]
    elif parent_type == "Restraint":
        if intf.parent_type_element1 == "Quad":
            quad = model.collections.quads[intf.parent_element_key1]
            effective_face = int(intf.face1)
        elif intf.parent_type_element2 == "Quad":
            quad = model.collections.quads[intf.parent_element_key2]
            effective_face = int(intf.face2)

    # C# ``MasonryMaterial.SlidingOrthotropyType`` is a read-only property
    # that always returns true. ``ortsc`` only controls whether SetIsotropic
    # copies the horizontal parameters into the vertical/dir3 fields; it does
    # not disable directional law selection in Interface.SetSpring.
    orthotropic = True
    if orthotropic and effective_face in (4, 5):
        return _cached_sliding_law(
            material,
            out_of_plane=out_of_plane,
            direction="dir3",
            cache=cache,
        )
    if orthotropic and quad is not None:
        horizontal = _cached_sliding_law(
            material,
            out_of_plane=out_of_plane,
            direction="hor",
            cache=cache,
        )
        vertical_law = _cached_sliding_law(
            material,
            out_of_plane=out_of_plane,
            direction="vert",
            cache=cache,
        )
        c1 = abs(float(np.dot(np.asarray(intf.reference_e1), np.asarray(quad.reference_e1))))
        c1 = min(1.0, max(0.0, c1))
        c2 = math.sqrt(max(0.0, 1.0 - c1 * c1))
        return _blend_coulomb_laws(horizontal, vertical_law, c1, c2)
    return _cached_sliding_law(
        material,
        out_of_plane=out_of_plane,
        direction="hor" if vertical else "vert",
        cache=cache,
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
    if not math.isfinite(k) or k <= 0.0:
        raise ModelPreparationError(
            f"Cannot create a transverse hysteretic spring with stiffness K={k!r}."
        )
    if not math.isfinite(area) or area <= 0.0:
        raise ModelPreparationError(
            f"Cannot create a transverse hysteretic spring with area={area!r}."
        )
    if not math.isfinite(length) or length <= 0.0:
        raise ModelPreparationError(
            f"Cannot create a transverse hysteretic spring with length={length!r}."
        )
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


def _hysteretic_side_definition(
    k: float, area: float, length: float, law: _HystereticLaw,
) -> _HystereticSideDefinition:
    if not math.isfinite(k) or k <= 0.0:
        raise ModelPreparationError(
            f"Cannot create a transverse hysteretic spring with stiffness K={k!r}."
        )
    if not math.isfinite(area) or area <= 0.0:
        raise ModelPreparationError(
            f"Cannot create a transverse hysteretic spring with area={area!r}."
        )
    if not math.isfinite(length) or length <= 0.0:
        raise ModelPreparationError(
            f"Cannot create a transverse hysteretic spring with length={length!r}."
        )

    fy_t = area * law.fy_t
    fy_c = -area * law.fy_c
    kt_t = 0.0
    kt_c = 0.0
    if law.tensile_curve == "Elastic":
        fy_t = k * 100000000.0
        kt_t = k
    elif law.tensile_curve == "LinearHardening":
        kt_t = k * law.ratio_et_t
    if law.compressive_curve == "Elastic":
        fy_c = -k * 100000000.0
        kt_c = k
    elif law.compressive_curve == "LinearHardening":
        kt_c = k * law.ratio_et_c

    # _configure_hysteretic calls _set_ultimate_displacement before the two
    # side springs are combined. Linear-softening laws therefore contribute
    # their fracture-energy tangent, not the initial zero placeholder.
    if law.tensile_curve == "LinearSoftening" and area and fy_t:
        ultimate_t = 2.0 * law.G_t / (fy_t / area) + fy_t / k
        kt_t = -fy_t / (ultimate_t - fy_t / k)
    if law.compressive_curve == "LinearSoftening" and area and fy_c:
        ultimate_c = 2.0 * law.G_c / (fy_c / area) + fy_c / k
        kt_c = -fy_c / (ultimate_c - fy_c / k)

    return _HystereticSideDefinition(
        k=float(k), area=float(area), length=float(length),
        fy_t=float(fy_t), fy_c=float(fy_c),
        kt_t=float(kt_t), kt_c=float(kt_c),
        alfa_r_t=float(law.alfa_r_t), alfa_r_c=float(law.alfa_r_c),
        alfa_u_t=float(law.alfa_u_t), alfa_u_c=float(law.alfa_u_c),
        tensile_curve=law.tensile_curve,
        compressive_curve=law.compressive_curve,
    )


def _configure_combined_hysteretic(
    k1: float, area1: float, length1: float, law1: _HystereticLaw,
    k2: float, area2: float, length2: float, law2: _HystereticLaw,
) -> SpringHysteretic:
    """Create the final Quad/Quad fibre spring without temporary objects.

    This is algebraically identical to configuring two side springs and calling
    ``_combine_hysteretic``.  It avoids two temporary SpringHysteretic objects
    and two full envelope initializations per generated fibre.
    """
    side1 = _hysteretic_side_definition(k1, area1, length1, law1)
    side2 = _hysteretic_side_definition(k2, area2, length2, law2)
    out = SpringHysteretic(type_of="HiStrA.Objects.SpringHysteretic")
    out.k = _series(side1.k, side2.k, False)

    if side1.fy_t <= side2.fy_t:
        out.fy[0] = side1.fy_t
        out.tensile_curve_type = side1.tensile_curve
    else:
        out.fy[0] = side2.fy_t
        out.tensile_curve_type = side2.tensile_curve

    if side1.fy_c <= side2.fy_c:
        out.fy[1] = side2.fy_c
        out.area = side2.area
    else:
        out.fy[1] = side1.fy_c
        out.area = side1.area
    out.compressive_curve_type = (
        side1.compressive_curve
        if side1.fy_c >= side2.fy_c
        else side2.compressive_curve
    )
    out.length = side1.length + side2.length
    out.alfau = [
        max(side1.alfa_u_t, side2.alfa_u_t),
        max(side1.alfa_u_c, side2.alfa_u_c),
    ]
    out.alfar = [
        max(side1.alfa_r_t, side2.alfa_r_t),
        max(side1.alfa_r_c, side2.alfa_r_c),
    ]
    out.kt = [
        out.k if out.tensile_curve_type == "Elastic" else _series(side1.kt_t, side2.kt_t, False),
        out.k if out.compressive_curve_type == "Elastic" else _series(side1.kt_c, side2.kt_c, False),
    ]
    out.ur = [
        max(out.fy[0] / out.k if out.k else 0.0, 0.0),
        min(out.fy[1] / out.k if out.k else 0.0, 0.0),
    ]
    _set_ultimate_displacement(out, law1, law1)
    ur1 = out.ur[:]
    _set_ultimate_displacement(out, law2, law2)
    ur2 = out.ur[:]
    out.ur[0] = (
        min(value for value in (ur1[0], ur2[0]) if value != 0.0)
        if ur1[0] and ur2[0]
        else max(ur1[0], ur2[0])
    )
    out.ur[1] = (
        max(value for value in (ur1[1], ur2[1]) if value != 0.0)
        if ur1[1] and ur2[1]
        else min(ur1[1], ur2[1])
    )
    out.initialize()
    out.revert_to_start()
    out.revert_to_last_commit()
    return out


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


def _quad_lateral_face_vertices(model: Model, quad: Quad, face: int) -> list[np.ndarray]:
    """Return one of the four extruded lateral surfaces used by C# ``Quad.VInt``."""
    assert model.collections is not None
    if face not in range(4):
        raise ModelPreparationError(f"Invalid lateral Quad face {face}; expected 0..3.")
    nodes = [_v(model.collections.nodes[k].point) for k in quad.node_keys]
    normals = [_unit(_v(n), label=f"Quad {quad.key} normal") for n in quad.normal]
    minus = [nodes[i] - normals[i] * quad.thickness[i] / 2.0 for i in range(4)]
    plus = [nodes[i] + normals[i] * quad.thickness[i] / 2.0 for i in range(4)]
    nxt = (face + 1) % 4
    if face in (0, 3):
        return [minus[face], minus[nxt], plus[nxt], plus[face]]
    return [minus[nxt], minus[face], plus[face], plus[nxt]]


def _quad_face_vertices(model: Model, quad: Quad, face: int) -> list[np.ndarray]:
    """Return C# ``Quad.GetNodeList(face)`` for all six surfaces."""
    if face not in range(6):
        raise ModelPreparationError(f"Invalid Quad face {face}; expected 0..5.")
    return [vertex.copy() for vertex in _quad_vint(model, quad)[face]]


def _make_interface_geometry(
    model: Model,
    intf: Interface,
    vertices: Sequence[np.ndarray],
    node_keys: tuple[int, int],
    parent1_g: np.ndarray | None,
    parent2_g: np.ndarray | None = None,
) -> None:
    assert model.collections is not None
    intf.node_keys = [int(node_keys[0]), int(node_keys[1])]
    p1 = _v(model.collections.nodes[node_keys[0]].point)
    p2 = _v(model.collections.nodes[node_keys[1]].point)
    e1 = _unit(p2 - p1, label=f"Interface {intf.key} e1")

    # C# Interface.Set identifies the polygon edge containing each interface
    # endpoint.  Those edges define both the local thickness and the reference
    # system.  Using the vector from the parent centroid to the interface works
    # only for centred contacts and tilts offset interfaces out of their plane.
    edge_matches: list[tuple[float, np.ndarray]] = []
    for endpoint in (p1, p2):
        match = _polygon_edge_at_point(vertices, endpoint)
        if match is None:
            raise ModelPreparationError(
                f"Interface {intf.key}: endpoint {endpoint.tolist()} is not aligned "
                "with an intersection-polygon edge."
            )
        edge_matches.append(match)

    if parent1_g is None:
        # Restraint VInt defines its local axes. Use the first edge and the
        # vector from endpoint 1 across the face.
        across = (vertices[3] - vertices[0] + vertices[2] - vertices[1]) * 0.5
        e3 = _unit(-across, label=f"Interface {intf.key} e3")
        e2 = _unit(_cross3(e3, e1), label=f"Interface {intf.key} e2")
        e3 = _unit(_cross3(e1, e2), label=f"Interface {intf.key} e3")
    else:
        if parent2_g is None:
            raise ModelPreparationError(
                f"Interface {intf.key}: the second Quad centroid is required."
            )
        thickness_direction1 = edge_matches[0][1].copy()
        thickness_direction2 = edge_matches[1][1].copy()
        if float(np.dot(
            _cross3(e1, thickness_direction1),
            _cross3(e1, thickness_direction2),
        )) < 0.0:
            thickness_direction1 *= -1.0

        e2 = _unit(
            _cross3(e1, thickness_direction1),
            label=f"Interface {intf.key} e2",
        )
        e3 = _unit(_cross3(e1, e2), label=f"Interface {intf.key} e3")

        polygon_normal = _cross3(vertices[1] - vertices[0], vertices[2] - vertices[0])
        if float(np.linalg.norm(polygon_normal)) <= 1.0e-12:
            polygon_normal = _cross3(vertices[1] - vertices[0], vertices[3] - vertices[0])
        polygon_normal = _unit(
            polygon_normal,
            label=f"Interface {intf.key} polygon normal",
        )
        parent2_direction = _unit(
            vertices[0] - parent2_g,
            label=f"Interface {intf.key} second-parent direction",
        )
        parent2_normal = _unit(
            float(np.dot(polygon_normal, parent2_direction)) * polygon_normal,
            label=f"Interface {intf.key} second-parent normal",
        )
        if float(np.dot(e2, parent2_normal)) > 0.0:
            e2 *= -1.0
            e3 *= -1.0

    origin = p1
    intf.reference_e1 = tuple(float(x) for x in e1)
    intf.reference_e2 = tuple(float(x) for x in e2)
    intf.reference_e3 = tuple(float(x) for x in e3)
    intf.reference_origin = _p(origin)
    intf.vint3d = [_p(v) for v in vertices]
    intf.vint2d = [
        Point(
            float(np.dot(v - origin, e1)),
            float(np.dot(v - origin, e3)),
            0.0,
        )
        for v in vertices
    ]
    # XNA ``Vector3.Distance`` is evaluated in Single precision in C# and
    # then promoted into the interface's double-valued Length property.
    intf.length = float(np.float32(np.linalg.norm(p2 - p1)))

    intf.thickness = [match[0] for match in edge_matches]
    intf.nrow = _interface_division_count(
        max(intf.thickness),
        minimum=int(model.interface_nrow),
        imax=float(model.interface_imax),
    )
    intf.ncol = _interface_division_count(
        intf.length,
        minimum=int(model.interface_nrow),
        imax=float(model.interface_imax),
    )
    intf.nspring = intf.ncol
    intf._perf_area = None



def _node_bucket(point: np.ndarray, tolerance: float) -> tuple[int, int, int]:
    return tuple(int(math.floor(float(value) / tolerance)) for value in point)


def _build_geometric_node_index(
    model: Model, *, tolerance: float = 1.0e-4,
) -> tuple[dict[tuple[int, int, int], list[int]], dict[int, np.ndarray]]:
    """Build the spatial lookup used by C#-style endpoint node reuse.

    The previous implementation scanned every node for every interface endpoint.
    The generated bridge has thousands of endpoints and nodes, making that
    quadratic scan one of PrepareModel's dominant Python costs.
    """
    assert model.collections is not None
    buckets: dict[tuple[int, int, int], list[int]] = {}
    points: dict[int, np.ndarray] = {}
    for key, node in model.collections.nodes.items():
        value = _v(node.point)
        int_key = int(key)
        points[int_key] = value
        buckets.setdefault(_node_bucket(value, tolerance), []).append(int_key)
    model._prep_geometric_node_index = (float(tolerance), buckets, points)
    return buckets, points


def _find_or_create_geometric_node(model: Model, point: np.ndarray, *, tolerance: float = 1.0e-4) -> int:
    """Return the C# PrepareBuildInterface endpoint node for an intersection edge.

    C# first catches an existing node near the midpoint of the interface's
    thickness edge and creates a geometry-only node only when none exists.
    Computational DOFs remain attached to Quads, so a newly created node does
    not alter ``model.gdl``.
    """
    assert model.collections is not None
    cached = getattr(model, "_prep_geometric_node_index", None)
    if cached is None or cached[0] != float(tolerance):
        buckets, points = _build_geometric_node_index(model, tolerance=tolerance)
    else:
        _, buckets, points = cached

    bucket = _node_bucket(point, tolerance)
    best_key: int | None = None
    best_distance2 = float("inf")
    tolerance2 = tolerance * tolerance
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                for key in buckets.get(
                    (bucket[0] + dx, bucket[1] + dy, bucket[2] + dz), ()
                ):
                    delta = points[key] - point
                    distance2 = float(np.dot(delta, delta))
                    if distance2 <= tolerance2 and distance2 < best_distance2:
                        best_key = key
                        best_distance2 = distance2
    if best_key is not None:
        return best_key

    from histra.model.node import Node

    key = max(model.collections.nodes, default=0) + 1
    value = np.asarray(point, dtype=float).copy()
    model.collections.nodes[key] = Node(key=key, point=_p(value), name=str(key))
    points[key] = value
    buckets.setdefault(_node_bucket(value, tolerance), []).append(key)
    return key


def _face_normal(vertices: np.ndarray) -> np.ndarray:
    """Stable Newell normal for a four-point surface."""
    nx = ny = nz = 0.0
    count = len(vertices)
    for index in range(count):
        current = vertices[index]
        following = vertices[(index + 1) % count]
        nx += (
            float(current[1]) * float(following[2])
            - float(current[2]) * float(following[1])
        )
        ny += (
            float(current[2]) * float(following[0])
            - float(current[0]) * float(following[2])
        )
        nz += (
            float(current[0]) * float(following[1])
            - float(current[1]) * float(following[0])
        )
    return _unit((nx, ny, nz), label="Quad face normal")


def _face_normals_batch(faces: np.ndarray) -> np.ndarray:
    """Return Newell normals for ``(..., vertex, xyz)`` face arrays."""
    faces = np.asarray(faces, dtype=np.float64)
    if faces.ndim < 3 or faces.shape[-1] != 3:
        raise ModelPreparationError(
            "Quad face array must have shape (..., vertex, 3); "
            f"received {faces.shape}."
        )
    following = np.roll(faces, -1, axis=-2)
    normals = np.empty(faces.shape[:-2] + (3,), dtype=np.float64)
    normals[..., 0] = np.sum(
        faces[..., 1] * following[..., 2]
        - faces[..., 2] * following[..., 1],
        axis=-1,
    )
    normals[..., 1] = np.sum(
        faces[..., 2] * following[..., 0]
        - faces[..., 0] * following[..., 2],
        axis=-1,
    )
    normals[..., 2] = np.sum(
        faces[..., 0] * following[..., 1]
        - faces[..., 1] * following[..., 0],
        axis=-1,
    )
    lengths = np.sqrt(np.sum(normals * normals, axis=-1))
    invalid = np.argwhere(lengths <= 1.0e-12)
    if invalid.size:
        location = tuple(int(value) for value in invalid[0])
        raise ModelPreparationError(
            "Cannot normalize zero vector while building Quad face normal "
            f"at batch index {location}."
        )
    return normals / lengths[..., None]


def _cross_2d(a: Sequence[float], b: Sequence[float], c: Sequence[float]) -> float:
    return float((b[0]-a[0]) * (c[1]-a[1]) - (b[1]-a[1]) * (c[0]-a[0]))


def _polygon_area_2d(vertices: Sequence[Sequence[float]]) -> float:
    return 0.5 * sum(
        float(a[0]) * float(b[1]) - float(a[1]) * float(b[0])
        for a, b in zip(vertices, (*vertices[1:], vertices[0]))
    )


def _line_intersection_2d(
    start: Sequence[float], end: Sequence[float],
    clip_start: Sequence[float], clip_end: Sequence[float],
) -> tuple[float, float]:
    dx, dy = float(end[0]-start[0]), float(end[1]-start[1])
    cx, cy = float(clip_end[0]-clip_start[0]), float(clip_end[1]-clip_start[1])
    denominator = dx*cy - dy*cx
    if abs(denominator) <= 1.0e-15:
        return (0.5 * (float(start[0])+float(end[0])),
                0.5 * (float(start[1])+float(end[1])))
    t = ((float(clip_start[0])-float(start[0]))*cy
         - (float(clip_start[1])-float(start[1]))*cx) / denominator
    return (float(start[0]) + t*dx, float(start[1]) + t*dy)


def _clean_clipped_polygon(vertices: list[tuple[float, float]]) -> list[tuple[float, float]]:
    deduplicated: list[tuple[float, float]] = []
    for point in vertices:
        if not deduplicated or (
            (point[0]-deduplicated[-1][0])**2
            + (point[1]-deduplicated[-1][1])**2
        ) > 1.0e-14:
            deduplicated.append(point)
    if len(deduplicated) > 1 and (
        (deduplicated[0][0]-deduplicated[-1][0])**2
        + (deduplicated[0][1]-deduplicated[-1][1])**2
    ) <= 1.0e-14:
        deduplicated.pop()

    changed = True
    while changed and len(deduplicated) > 3:
        changed = False
        cleaned: list[tuple[float, float]] = []
        count = len(deduplicated)
        for index, point in enumerate(deduplicated):
            if abs(_cross_2d(
                deduplicated[index-1], point, deduplicated[(index+1) % count]
            )) <= 1.0e-8:
                changed = True
            else:
                cleaned.append(point)
        if not cleaned:
            break
        deduplicated = cleaned
    return deduplicated


def _clip_convex_quad_2d(
    subject: list[tuple[float, float]], clipper: list[tuple[float, float]],
) -> list[tuple[float, float]]:
    """Sutherland-Hodgman clipping while preserving parent-1 vertex order."""
    # FindIntersectionBetweenQuadrilaters preserves the first face's cyclic
    # order. Only the clip polygon is normalized for the inside test.
    clip = list(clipper)
    if _polygon_area_2d(clip) < 0.0:
        clip.reverse()
    output = list(subject)
    for clip_start, clip_end in zip(clip, (*clip[1:], clip[0])):
        input_vertices = output
        output = []
        if not input_vertices:
            break
        start = input_vertices[-1]
        start_inside = _cross_2d(clip_start, clip_end, start) >= -_CONTACT_DISTANCE_TOLERANCE
        for end in input_vertices:
            end_inside = _cross_2d(clip_start, clip_end, end) >= -_CONTACT_DISTANCE_TOLERANCE
            if end_inside:
                if not start_inside:
                    output.append(_line_intersection_2d(start, end, clip_start, clip_end))
                output.append(end)
            elif start_inside:
                output.append(_line_intersection_2d(start, end, clip_start, clip_end))
            start, start_inside = end, end_inside
    return _clean_clipped_polygon(output)


def _coplanar_quad_intersection_prechecked(
    first: np.ndarray, second: np.ndarray, normal_first: np.ndarray,
) -> list[np.ndarray] | None:
    """Clip two faces after the vectorized broad phase proved coplanarity."""
    drop = int(np.argmax(np.abs(normal_first)))
    keep = [axis for axis in range(3) if axis != drop]
    subject = [(float(point[keep[0]]), float(point[keep[1]])) for point in first]
    clipper = [(float(point[keep[0]]), float(point[keep[1]])) for point in second]
    clipped = _clip_convex_quad_2d(subject, clipper)
    # C# GIQuadQuad accepts only four-point surface intersections. Point/line
    # contacts and higher-order polygons are deliberately not interfaces.
    area = abs(_polygon_area_2d(clipped)) if len(clipped) == 4 else 0.0
    if len(clipped) != 4 or area <= _CONTACT_AREA_TOLERANCE:
        return None

    # The C# intersection path does not emit finite interfaces for contacts
    # whose apparent width is only a coordinate-tolerance artefact.  The
    # vectorized Python broad phase intentionally uses a 2e-4 distance
    # tolerance, so clipping can otherwise turn a 3e-5 gap into a very thin
    # quadrilateral.  Reject these slivers by their area/longest-edge width.
    edge_lengths = [
        math.hypot(float(end[0])-float(start[0]), float(end[1])-float(start[1]))
        for start, end in zip(clipped, (*clipped[1:], clipped[0]))
    ]
    longest_edge = max(edge_lengths, default=0.0)
    if longest_edge <= 0.0 or area / longest_edge <= _CONTACT_DISTANCE_TOLERANCE:
        return None

    plane_origin = first[0]
    result: list[np.ndarray] = []
    for x, y in clipped:
        point = np.zeros(3, dtype=float)
        point[keep[0]], point[keep[1]] = x, y
        point[drop] = plane_origin[drop] - (
            normal_first[keep[0]] * (x-plane_origin[keep[0]])
            + normal_first[keep[1]] * (y-plane_origin[keep[1]])
        ) / normal_first[drop]
        result.append(point)
    return result


def _coplanar_quad_intersection(
    first: np.ndarray, second: np.ndarray,
) -> list[np.ndarray] | None:
    normal_first = _face_normal(first)
    normal_second = _face_normal(second)
    if float(np.linalg.norm(_cross3(normal_first, normal_second))) > _CONTACT_ANGLE_TOLERANCE:
        return None
    origin = np.mean(first, axis=0)
    if float(np.max(np.abs((second-origin) @ normal_first))) > _CONTACT_DISTANCE_TOLERANCE:
        return None
    return _coplanar_quad_intersection_prechecked(first, second, normal_first)


def _polygon_edge_at_point(
    vertices: Sequence[np.ndarray], point: np.ndarray,
) -> tuple[float, np.ndarray] | None:
    best: tuple[float, float, np.ndarray] | None = None
    tolerance = max(1.0e-4, _CONTACT_DISTANCE_TOLERANCE)
    for start, end in zip(vertices, (*vertices[1:], vertices[0])):
        edge = end-start
        length2 = float(np.dot(edge, edge))
        if length2 <= 1.0e-18:
            continue
        parameter = float(np.dot(point-start, edge) / length2)
        projected = start + min(max(parameter, 0.0), 1.0) * edge
        distance = float(np.linalg.norm(point-projected))
        if -1.0e-6 <= parameter <= 1.0+1.0e-6 and distance <= tolerance:
            # C# obtains the edge length through XNA ``Vector3.Distance``.
            length = float(np.float32(math.sqrt(length2)))
            direction = _unit(start-end, label="Interface thickness direction")
            if best is None or distance < best[0]:
                best = (distance, length, direction)
    return None if best is None else (best[1], best[2])


def _quad_face_reference_edge(
    model: Model, quad: Quad, face: int,
) -> tuple[np.ndarray, np.ndarray]:
    assert model.collections is not None
    if face < 4:
        return (
            _v(model.collections.nodes[quad.node_keys[face]].point),
            _v(model.collections.nodes[quad.node_keys[(face+1) % 4]].point),
        )
    vertices = _quad_vint(model, quad)[face]
    return 0.5*(vertices[0]+vertices[1]), 0.5*(vertices[2]+vertices[3])


def _prepare_interface_endpoints(
    model: Model, q1: Quad, face1: int, q2: Quad, face2: int,
    vertices: Sequence[np.ndarray],
) -> tuple[tuple[int, int], float]:
    """Exact endpoint selection from C# ``PrepareBuildInterface``."""
    polygon = np.asarray(vertices, dtype=float)
    reference_start, reference_end = _quad_face_reference_edge(model, q1, face1)
    # C# derives the reference direction from the intersection polygon when a
    # horizontal face meets a lateral face.  When *both* faces are horizontal,
    # however, relying on the polygon's cyclic start makes the result dependent
    # on the clipping implementation.  C#'s NodeListOut happens to start on the
    # parent-1 reference edge; Sutherland-Hodgman may start 90 degrees away.
    # Retain q1's actual face reference in the both-horizontal case so endpoint
    # selection, local axes and NRow/NCol are invariant and match C#.
    if (face1 >= 4) != (face2 >= 4):
        reference_start = 0.5*(polygon[0]+polygon[1])
        reference_end = 0.5*(polygon[2]+polygon[3])
        if face1 < 4:
            if abs(float(np.dot(np.asarray(q1.reference_e3), reference_end-reference_start))) > 1.0e-12:
                reference_start = 0.5*(polygon[1]+polygon[2])
                reference_end = 0.5*(polygon[0]+polygon[3])
        elif face2 < 4:
            if abs(float(np.dot(np.asarray(q2.reference_e3), reference_end-reference_start))) > 1.0e-12:
                reference_start = 0.5*(polygon[1]+polygon[2])
                reference_end = 0.5*(polygon[0]+polygon[3])

    reference = _unit(reference_end-reference_start, label="Interface reference edge")
    option_a = _unit(
        0.5*(polygon[1]+polygon[2]) - 0.5*(polygon[0]+polygon[3]),
        label="Interface endpoint option A",
    )
    option_b = _unit(
        0.5*(polygon[2]+polygon[3]) - 0.5*(polygon[0]+polygon[1]),
        label="Interface endpoint option B",
    )
    if abs(float(np.dot(reference, option_a))) > abs(float(np.dot(reference, option_b))):
        first = 0.5*(polygon[2]+polygon[1])
        second = 0.5*(polygon[0]+polygon[3])
    else:
        first = 0.5*(polygon[0]+polygon[1])
        second = 0.5*(polygon[2]+polygon[3])
    first_key = _find_or_create_geometric_node(model, first)
    second_key = _find_or_create_geometric_node(model, second)
    return (first_key, second_key), float(
        np.float32(np.linalg.norm(second-first))
    )


def _passes_csharp_lateral_area_filter(
    q1: Quad, face1: int, q2: Quad, face2: int,
    vertices: Sequence[np.ndarray], model: Model,
) -> bool:
    if face1 >= 4 or face2 >= 4:
        return True
    reference_start, reference_end = _quad_face_reference_edge(model, q1, face1)
    characteristic = min(
        float(np.linalg.norm(reference_start-reference_end)),
        max(max(q1.thickness), max(q2.thickness)),
    )
    if _polygon_area_3d(vertices) >= characteristic*characteristic/400.0:
        return True
    centre_delta = _v(q2.g)-_v(q1.g)
    if float(np.linalg.norm(centre_delta)) <= 1.0e-12:
        return False
    normal = _face_normal(np.asarray(vertices, dtype=float))
    return abs(float(np.dot(normal, _unit(centre_delta, label="Quad centre direction")))) >= math.cos(math.radians(80.0))


def _quad_contact_pairs(model: Model) -> list[tuple[Quad, int, Quad, int, list[np.ndarray], tuple[int, int], float]]:
    """Port C# ``GIQuadQuadSerial`` for all six Quad surfaces.

    A vectorized broad phase keeps the C# all-pairs semantics practical. The
    narrow phase performs coplanar convex-polygon clipping and accepts the same
    four-vertex intersections used by ``BuildInterface``.
    """
    assert model.collections is not None
    quads = sorted(model.collections.quads.values(), key=lambda item: item.key)
    count = len(quads)
    if count < 2:
        return []

    faces = np.asarray([
        np.asarray(_quad_vint(model, quad), dtype=float) for quad in quads
    ], dtype=float)
    face_min = np.min(faces, axis=2)
    face_max = np.max(faces, axis=2)
    face_center = np.mean(faces, axis=2)
    face_normal = _face_normals_batch(faces)
    centres = np.asarray([_v(quad.g) for quad in quads], dtype=float)
    broad_radius = np.asarray([
        max(quad.length) + max(quad.thickness) for quad in quads
    ], dtype=float)

    pair_i: list[int] = []
    pair_j: list[int] = []
    for first in range(count-1):
        delta = centres[first+1:] - centres[first]
        distance = np.linalg.norm(delta, axis=1)
        candidates = np.flatnonzero(
            distance < broad_radius[first] + broad_radius[first+1:]
        )
        pair_i.extend([first] * len(candidates))
        pair_j.extend((first+1+candidates).tolist())
    first_indices = np.asarray(pair_i, dtype=np.int64)
    second_indices = np.asarray(pair_j, dtype=np.int64)

    surface_candidates: list[tuple[int, int, int, int]] = []
    for offset in range(0, len(first_indices), _CONTACT_BATCH_SIZE):
        first = first_indices[offset:offset+_CONTACT_BATCH_SIZE]
        second = second_indices[offset:offset+_CONTACT_BATCH_SIZE]
        overlap = np.all(
            (face_max[first, :, None, :] >= face_min[second, None, :, :] - _CONTACT_DISTANCE_TOLERANCE)
            & (face_max[second, None, :, :] >= face_min[first, :, None, :] - _CONTACT_DISTANCE_TOLERANCE),
            axis=3,
        )
        candidate, face1, face2 = np.nonzero(overlap)
        normals1 = face_normal[first[candidate], face1]
        normals2 = face_normal[second[candidate], face2]
        parallel = np.linalg.norm(np.cross(normals1, normals2), axis=1) <= _CONTACT_ANGLE_TOLERANCE
        candidate, face1, face2, normals1 = (
            candidate[parallel], face1[parallel], face2[parallel], normals1[parallel]
        )
        plane_distance = np.abs(np.sum(
            (face_center[second[candidate], face2] - face_center[first[candidate], face1]) * normals1,
            axis=1,
        ))
        coplanar = plane_distance <= _CONTACT_DISTANCE_TOLERANCE
        surface_candidates.extend(zip(
            first[candidate[coplanar]].tolist(), face1[coplanar].tolist(),
            second[candidate[coplanar]].tolist(), face2[coplanar].tolist(),
        ))

    surface_candidates.sort(key=lambda item: (item[0], item[2], item[1], item[3]))
    contacts: list[tuple[Quad, int, Quad, int, list[np.ndarray], tuple[int, int], float]] = []
    for first, face1, second, face2 in surface_candidates:
        q1, q2 = quads[first], quads[second]
        intersection = _coplanar_quad_intersection_prechecked(
            faces[first, face1], faces[second, face2],
            face_normal[first, face1],
        )
        if intersection is None:
            continue
        if not _passes_csharp_lateral_area_filter(q1, face1, q2, face2, intersection, model):
            continue
        node_order, contact_length = _prepare_interface_endpoints(
            model, q1, face1, q2, face2, intersection
        )
        contacts.append((
            q1, face1, q2, face2, intersection, node_order, contact_length
        ))

    contacts.sort(key=lambda item: (item[0].key, item[2].key, item[1], item[3]))
    return contacts

def _generate_interfaces(model: Model) -> tuple[int, int]:
    assert model.collections is not None
    c = model.collections
    c.interfaces.clear()
    _build_geometric_node_index(model)
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
        _make_interface_geometry(
            model, intf, vertices, node_order, _v(q1.g), _v(q2.g)
        )
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


def _quad_afference_geometry(model: Model, quad: Quad) -> _QuadAfferenceGeometry:
    assert model.collections is not None
    vertices = np.asarray(
        [_v(model.collections.nodes[key].point) for key in quad.node_keys],
        dtype=float,
    )
    normal = _unit(
        _cross3(vertices[1] - vertices[0], vertices[2] - vertices[0]),
        label=f"Quad {quad.key} midsurface normal",
    )
    return _QuadAfferenceGeometry(
        centre=_v(quad.g),
        vertices=vertices,
        normal=normal,
        warping_nodal=_warping_nodal_vectors(quad),
    )


def _warping_vector_from_geometry(
    geometry: _QuadAfferenceGeometry, point: np.ndarray
) -> np.ndarray:
    projected = point - geometry.normal * float(
        np.dot(point - geometry.vertices[0], geometry.normal)
    )
    u, v = _inverse_bilinear(geometry.vertices, projected)
    return _bilinear(geometry.warping_nodal, u, v)


def _warping_vector_at_point(quad: Quad, point: np.ndarray, model: Model) -> np.ndarray:
    """C# ``GetDisplacementFromShearDOF`` for an arbitrary face point.

    C# projects the interface endpoint onto the Quad midsurface, solves its
    intrinsic coordinates and bilinearly interpolates the four nodal warping
    vectors. Restricting this operation to centre-line edges loses the offset
    lateral contacts created by the full surface-intersection algorithm.
    """
    return _warping_vector_from_geometry(
        _quad_afference_geometry(model, quad), point
    )


def _point_afference(
    model: Model, quad: Quad, point: np.ndarray, node_key: int,
    direction: np.ndarray, *, face: int,
    _geometry: _QuadAfferenceGeometry | None = None,
    _point_cache: dict[
        tuple[int, int], tuple[np.ndarray, np.ndarray | None]
    ] | None = None,
) -> list[AfferenceEntry]:
    geometry = (
        _quad_afference_geometry(model, quad)
        if _geometry is None
        else _geometry
    )
    cache_key = (int(quad.key), int(node_key))
    cached = None if _point_cache is None else _point_cache.get(cache_key)
    if cached is None:
        r = point - geometry.centre
        warping = None
    else:
        r, warping = cached

    if face <= 3 and warping is None:
        warping = _warping_vector_from_geometry(geometry, point)
    if _point_cache is not None:
        if cached is None or (cached[1] is None and warping is not None):
            _point_cache[cache_key] = (r, warping)

    dx, dy, dz = (
        float(direction[0]), float(direction[1]), float(direction[2])
    )
    rx, ry, rz = float(r[0]), float(r[1]), float(r[2])
    shear = 0.0 if face > 3 else float(np.dot(warping, direction))
    coeff = (
        dx,
        dy,
        dz,
        ry * dz - rz * dy,
        rz * dx - rx * dz,
        rx * dy - ry * dx,
        shear,
    )
    out: list[AfferenceEntry] = []
    # C# Quad.PointAfference delegates to
    # AfferenceMatrix.SetFromCoefficients, which discards coefficients whose
    # absolute value is not greater than 1e-4.
    for local, value in enumerate(coeff):
        if abs(value) <= 1.0e-4:
            continue
        for entry in quad.aff[local]:
            out.append(
                AfferenceEntry(gdl=entry.gdl, alfa=float(value * entry.alfa))
            )
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
    geometry_cache: dict[int, _QuadAfferenceGeometry] = {}
    point_cache: dict[
        tuple[int, int], tuple[np.ndarray, np.ndarray | None]
    ] = {}
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
                raise ModelPreparationError(
                    f"Interface {intf.key} has unsupported parent type {typ!r}."
                )
            quad = c.quads[key]
            geometry = geometry_cache.get(int(quad.key))
            if geometry is None:
                geometry = _quad_afference_geometry(model, quad)
                geometry_cache[int(quad.key)] = geometry
            parent_face = intf.face1 if side == 0 else intf.face2
            if side == 0:
                slots_e2 = (0, 1)
                slot_rot, slot_flex = 4, 6
                slots_e3 = (8, 9)
            else:
                slots_e2 = (3, 2)
                slot_rot, slot_flex = 5, 7
                slots_e3 = (10, 11)
            common = {
                "face": parent_face,
                "_geometry": geometry,
                "_point_cache": point_cache,
            }
            intf.aff[slots_e2[0]] = _point_afference(
                model, quad, points[0], intf.node_keys[0], e2, **common
            )
            intf.aff[slots_e2[1]] = _point_afference(
                model, quad, points[1], intf.node_keys[1], e2, **common
            )
            intf.aff[slot_rot] = _rotation_afference(quad, e1)
            intf.aff[slot_flex] = _point_afference(
                model, quad, points[1], intf.node_keys[1], e1, **common
            )
            intf.aff[slots_e3[0]] = _point_afference(
                model, quad, points[0], intf.node_keys[0], e3, **common
            )
            intf.aff[slots_e3[1]] = _point_afference(
                model, quad, points[1], intf.node_keys[1], e3, **common
            )
        intf.status = InterfaceState()
        intf.status.init_from_interface(intf)
        intf._perf_aff_pairs = None


def _quad_vint(model: Model, quad: Quad) -> tuple[np.ndarray, ...]:
    cached = getattr(quad, "_prep_vint", None)
    if cached is not None:
        return cached
    faces = [np.asarray(_quad_lateral_face_vertices(model, quad, face), dtype=float) for face in range(4)]
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
    normal = _cross3(vertices[1]-vertices[0], vertices[3]-vertices[0])
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
    nx = ny = nz = 0.0
    count = len(points)
    for index in range(count):
        current = points[index]
        following = points[(index + 1) % count]
        nx += (
            float(current[1]) * float(following[2])
            - float(current[2]) * float(following[1])
        )
        ny += (
            float(current[2]) * float(following[0])
            - float(current[0]) * float(following[2])
        )
        nz += (
            float(current[0]) * float(following[1])
            - float(current[1]) * float(following[0])
        )
    return 0.5 * math.sqrt(nx * nx + ny * ny + nz * nz)



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
        # Preserve the scalar/C# evaluation order exactly.  Precomputing the
        # four shape-function weights changes floating-point rounding because
        # ``vertex * ((1 +/- u) * (1 +/- v) / 4)`` is not bitwise identical
        # to ``vertex * (1 +/- u) * (1 +/- v) / 4``.  Cell areas feed spring
        # stiffnesses, so keep the authoritative operation sequence here.
        for j in range(3):
            term0 = vertices[0,j]*(1.0-u)*(1.0-v)/4.0
            term1 = vertices[1,j]*(1.0+u)*(1.0-v)/4.0
            term2 = vertices[2,j]*(1.0+u)*(1.0+v)/4.0
            term3 = vertices[3,j]*(1.0-u)*(1.0+v)/4.0
            out[j] = term0 + term1 + term2 + term3

    @njit(cache=True, nogil=True)
    def _interface_cells_nb(vertices, nrow, ncol):
        cells = np.empty((nrow * ncol, 4, 3), dtype=np.float64)
        point = np.empty(3, dtype=np.float64)
        index = 0
        for row in range(nrow):
            v0 = row * 2.0 / nrow - 1.0
            v1 = (row + 1) * 2.0 / nrow - 1.0
            for col in range(ncol):
                u0 = col * 2.0 / ncol - 1.0
                u1 = (col + 1) * 2.0 / ncol - 1.0
                _bilinear_nb(vertices, u0, v0, point)
                for component in range(3):
                    cells[index, 0, component] = point[component]
                _bilinear_nb(vertices, u1, v0, point)
                for component in range(3):
                    cells[index, 1, component] = point[component]
                _bilinear_nb(vertices, u1, v1, point)
                for component in range(3):
                    cells[index, 2, component] = point[component]
                _bilinear_nb(vertices, u0, v1, point)
                for component in range(3):
                    cells[index, 3, component] = point[component]
                index += 1
        return cells

    @njit(cache=True, nogil=True)
    def _polygon_areas_3d_nb(cells):
        areas = np.empty(cells.shape[0], dtype=np.float64)
        for cell_index in range(cells.shape[0]):
            nx = 0.0
            ny = 0.0
            nz = 0.0
            for index in range(cells.shape[1]):
                following = (index + 1) % cells.shape[1]
                x0 = cells[cell_index, index, 0]
                y0 = cells[cell_index, index, 1]
                z0 = cells[cell_index, index, 2]
                x1 = cells[cell_index, following, 0]
                y1 = cells[cell_index, following, 1]
                z1 = cells[cell_index, following, 2]
                nx += y0 * z1 - z0 * y1
                ny += z0 * x1 - x0 * z1
                nz += x0 * y1 - y0 * x1
            areas[cell_index] = 0.5 * math.sqrt(nx * nx + ny * ny + nz * nz)
        return areas

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


def _interface_cells(intf: Interface) -> np.ndarray:
    nrow = int(intf.nrow)
    ncol = int(intf.ncol)
    if nrow <= 0 or ncol <= 0:
        raise ModelPreparationError(
            f"Interface {intf.key} has invalid spring grid "
            f"Nrow={nrow}, Ncol={ncol}."
        )
    vertices = getattr(intf, "_prep_vertices", None)
    if vertices is None:
        vertices = np.asarray([_v(point) for point in intf.vint3d], dtype=float)
        intf._prep_vertices = vertices
    vertices = np.asarray(vertices, dtype=np.float64)
    if njit is not None:
        return _interface_cells_nb(vertices, nrow, ncol)
    return np.asarray(
        [_cell_vertices(intf, index) for index in range(nrow * ncol)],
        dtype=np.float64,
    )


def _polygon_areas_3d(cells: np.ndarray) -> np.ndarray:
    cells = np.asarray(cells, dtype=np.float64)
    if njit is not None:
        return _polygon_areas_3d_nb(cells)
    return np.asarray([_polygon_area_3d(cell) for cell in cells], dtype=np.float64)


def _fiber_stiffness_batch(model: Model, quad: Quad, intf: Interface,
                            cells: np.ndarray, E: float, face: int) -> np.ndarray:
    if _fiber_stiffness_batch_nb is None:
        return np.asarray([
            _fiber_stiffness(model, quad, intf, cell, E, face) for cell in cells
        ], dtype=float)
    vints = _quad_vint(model, quad)
    opposite = {0:2,1:3,2:0,3:1,4:5,5:4}[face]
    far_face = vints[opposite]
    # C# Quad.GetFiberProperties reverses the opposite broad face explicitly:
    # face 4 uses VInt[5, 3..0], and face 5 uses VInt[4, 3..0].
    if face >= 4:
        far_face = tuple(reversed(far_face))
    output = np.zeros((len(cells),3), dtype=np.float64)
    errors = np.zeros(len(cells), dtype=np.int32)
    _fiber_stiffness_batch_nb(
        np.asarray(vints[face], dtype=np.float64),
        np.asarray(far_face, dtype=np.float64),
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

    face_cross = _cross3(near_face[1] - near_face[0], near_face[3] - near_face[0])
    cell_cross = _cross3(points[1] - points[0], points[3] - points[0])
    if float(np.dot(face_cross, cell_cross)) < 0.0:
        points[1], points[3] = points[3], points[1]

    # Rotate the polygon so its vertices correspond to the face vertices.
    scores = []
    for shift in range(4):
        scores.append(sum(_norm3(points[(shift+k) % 4] - near_face[k]) for k in range(4)))
    shift = int(np.argmin(scores))
    points = [points[(shift+i) % 4] for i in range(4)]

    far_face = vints[opposite]
    # C# reverses the opposite face only for the two broad surfaces. Without
    # this, corresponding intrinsic coordinates map to the wrong corners and
    # can make the fibre direction orthogonal to Interface.ReferenceSystem.e2.
    if face >= 4:
        far_face = tuple(reversed(far_face))
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
    value = _cross3(vector3, cvec)

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
    normal = _unit(_cross3(_v(intf.vint3d[1])-p0, _v(intf.vint3d[2])-p0), label="interface plane")
    return abs(float(np.dot(_v(quad.g)-p0, normal)))


def _quad_spring(
    model: Model,
    quad: Quad,
    *,
    law_cache: dict[int, tuple[_HystereticLaw, _CoulombLaw]] | None = None,
) -> SpringCoulomb03 | SpringHysteretic | SpringElastic:
    material = _material(model, quad.material_key)
    flex, shear = _cached_diagonal_laws(material, law_cache)
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


def _interface_parent_material(
    model: Model,
    intf: Interface,
    parent_type: str,
    parent_key: int,
    material_override: MasonryMaterial | None,
) -> MasonryMaterial:
    """Return the material governing one interface side.

    Restraint-side ultimate-displacement rules use the material of the Quad on
    the opposite side in the C# implementation.  Resolving that material once
    also avoids repeating collection lookups for the three sliding springs.
    """
    assert model.collections is not None
    if material_override is not None:
        return material_override
    if parent_type == "Quad":
        return _material(model, model.collections.quads[parent_key].material_key)
    if parent_type != "Restraint":
        raise ModelPreparationError(
            f"Interface {intf.key} has unsupported parent type {parent_type!r}."
        )
    if intf.parent_type_element1 == "Quad":
        quad_key = intf.parent_element_key1
    elif intf.parent_type_element2 == "Quad":
        quad_key = intf.parent_element_key2
    else:
        raise ModelPreparationError(
            f"Interface {intf.key} has a restraint but no Quad parent."
        )
    return _material(model, model.collections.quads[quad_key].material_key)


def _side_sliding_spring(
    model: Model,
    parent_type: str,
    parent_key: int,
    intf: Interface,
    *,
    out_of_plane: bool,
    area: float,
    vertical: bool,
    material_override: MasonryMaterial | None = None,
    law: _CoulombLaw | None = None,
    distance: float | None = None,
) -> SpringCoulomb03:
    assert model.collections is not None
    if parent_type == "Restraint":
        spring = SpringCoulomb03(type_of="HiStrA.Objects.SpringCoulomb03")
        spring.k = -1.0
        spring.area = area
        return spring
    quad = model.collections.quads[parent_key]
    if law is None:
        material = (
            material_override
            if material_override is not None
            else _material(model, quad.material_key)
        )
        law = _sliding_law(
            material, out_of_plane=out_of_plane, vertical=vertical
        )
    if distance is None:
        distance = _distance_to_interface_plane(quad, intf)
    if distance <= 1.0e-12:
        raise ModelPreparationError(
            f"Quad {quad.key}, Interface {intf.key}: zero sliding distance."
        )
    # ``area`` is already the half-interface area for the two-spring
    # out-of-plane torsion model. C# GetOutOfPlaneSlidingStiffness also uses
    # Interface.Area()/2, so no second division is applied here.
    effective_area = area
    k = law.E * effective_area / distance
    spring = _configure_coulomb(
        k=k,
        area=area,
        length=intf.length,
        law=law,
        cohesion_force=area * law.cohesion,
        ur=100000.0,
        hysteretic_type="Initial",
    )
    spring.plastic_strain_ratio = 1.0
    return spring


def _transverse_side_properties_batch(
    model: Model, parent_type: str, parent_key: int, face: int,
    intf: Interface, cells: np.ndarray,
    material_override: MasonryMaterial | None = None,
    *,
    vertical: bool | None = None,
    law_cache: dict[tuple[int, bool], _HystereticLaw] | None = None,
) -> tuple[np.ndarray, _HystereticLaw]:
    assert model.collections is not None
    if parent_type == "Restraint":
        props = np.zeros((len(cells), 3), dtype=np.float64)
        props[:, 0] = -1.0
        props[:, 1] = _polygon_areas_3d(cells)
        if material_override is not None:
            law = _cached_flex_law(
                material_override, vertical=False, cache=law_cache
            )
        else:
            quad_key = (
                intf.parent_element_key1
                if intf.parent_type_element1 == "Quad"
                else intf.parent_element_key2
            )
            material = _material(
                model, model.collections.quads[quad_key].material_key
            )
            law = _cached_flex_law(
                material, vertical=False, cache=law_cache
            )
        return props, law
    quad = model.collections.quads[parent_key]
    material = (
        material_override
        if material_override is not None
        else _material(model, quad.material_key)
    )
    if vertical is None:
        vertical = abs(float(intf.reference_e2[2])) > math.cos(math.radians(45.0))
    law = _cached_flex_law(
        material, vertical=vertical, cache=law_cache
    )
    return _fiber_stiffness_batch(
        model, quad, intf, cells, law.E, face
    ), law


def _create_interface_springs(
    model: Model,
    intf: Interface,
    *,
    flex_law_cache: dict[tuple[int, bool], _HystereticLaw] | None = None,
    sliding_law_cache: dict[tuple[int, bool, str], _CoulombLaw] | None = None,
) -> None:
    assert model.collections is not None
    restrained = (
        intf.parent_type_element1 == "Restraint"
        or intf.parent_type_element2 == "Restraint"
    )
    custom_material = None
    if int(intf.material_key) != 0:
        custom_material = _material(model, int(intf.material_key))

    vertical = abs(float(intf.reference_e2[2])) > math.cos(math.radians(45.0))
    cells = _interface_cells(intf)
    cell_count = len(cells)
    props1, law1 = _transverse_side_properties_batch(
        model,
        intf.parent_type_element1,
        intf.parent_element_key1,
        intf.face1,
        intf,
        cells,
        custom_material,
        vertical=vertical,
        law_cache=flex_law_cache,
    )
    props2, law2 = _transverse_side_properties_batch(
        model,
        intf.parent_type_element2,
        intf.parent_element_key2,
        intf.face2,
        intf,
        cells,
        custom_material,
        vertical=vertical,
        law_cache=flex_law_cache,
    )

    intf.trasv_1 = []
    append_transverse = intf.trasv_1.append
    for index in range(cell_count):
        k1, area1, length1 = map(float, props1[index])
        k2, area2, length2 = map(float, props2[index])
        if not restrained:
            try:
                spring = _configure_combined_hysteretic(
                    k1, area1, length1, law1,
                    k2, area2, length2, law2,
                )
            except ModelPreparationError as exc:
                raise ModelPreparationError(
                    f"Interface {intf.key}, transverse cell {index}: {exc}"
                ) from exc
            spring.key = index
            spring.parent_key = intf.key
            spring.parent_type = "Interface"
            spring.spring_purpose = "Transversal1"
            spring.length = 0.0
            append_transverse(spring)
            continue

        if k1 == -1.0:
            sp1 = SpringHysteretic(type_of="HiStrA.Objects.SpringHysteretic")
            sp1.k, sp1.area = -1.0, area1
        else:
            try:
                sp1 = _configure_hysteretic(k1, area1, length1, law1)
            except ModelPreparationError as exc:
                raise ModelPreparationError(
                    f"Interface {intf.key}, transverse cell {index}, parent 1 "
                    f"({intf.parent_type_element1} {intf.parent_element_key1}, "
                    f"face {intf.face1}): {exc}"
                ) from exc
        if k2 == -1.0:
            sp2 = SpringHysteretic(type_of="HiStrA.Objects.SpringHysteretic")
            sp2.k, sp2.area = -1.0, area2
        else:
            try:
                sp2 = _configure_hysteretic(k2, area2, length2, law2)
            except ModelPreparationError as exc:
                raise ModelPreparationError(
                    f"Interface {intf.key}, transverse cell {index}, parent 2 "
                    f"({intf.parent_type_element2} {intf.parent_element_key2}, "
                    f"face {intf.face2}): {exc}"
                ) from exc
        if custom_material is not None and restrained:
            # C# Interface.SetSpring: for a custom material on a restraint/Quad
            # interface, clone the non-restraint spring rather than combining
            # it with the rigid restraint-side placeholder.
            spring = copy.deepcopy(
                sp2 if intf.parent_type_element1 == "Restraint" else sp1
            )
        else:
            spring = _combine_hysteretic(
                sp1, sp2, restrained, law1, law2
            )
        spring.key = index
        spring.parent_key = intf.key
        spring.parent_type = "Interface"
        spring.spring_purpose = "Transversal1"
        spring.length = 0.0
        append_transverse(spring)

    area = intf.area()
    material1 = _interface_parent_material(
        model,
        intf,
        intf.parent_type_element1,
        intf.parent_element_key1,
        custom_material,
    )
    material2 = _interface_parent_material(
        model,
        intf,
        intf.parent_type_element2,
        intf.parent_element_key2,
        custom_material,
    )
    in_law1 = _interface_sliding_law(
        model,
        intf,
        parent_type=intf.parent_type_element1,
        parent_key=intf.parent_element_key1,
        face=intf.face1,
        material=material1,
        out_of_plane=False,
        vertical=vertical,
        cache=sliding_law_cache,
    )
    in_law2 = _interface_sliding_law(
        model,
        intf,
        parent_type=intf.parent_type_element2,
        parent_key=intf.parent_element_key2,
        face=intf.face2,
        material=material2,
        out_of_plane=False,
        vertical=vertical,
        cache=sliding_law_cache,
    )
    out_law1 = _interface_sliding_law(
        model,
        intf,
        parent_type=intf.parent_type_element1,
        parent_key=intf.parent_element_key1,
        face=intf.face1,
        material=material1,
        out_of_plane=True,
        vertical=vertical,
        cache=sliding_law_cache,
    )
    out_law2 = _interface_sliding_law(
        model,
        intf,
        parent_type=intf.parent_type_element2,
        parent_key=intf.parent_element_key2,
        face=intf.face2,
        material=material2,
        out_of_plane=True,
        vertical=vertical,
        cache=sliding_law_cache,
    )

    distance1 = None
    if intf.parent_type_element1 == "Quad":
        distance1 = _distance_to_interface_plane(
            model.collections.quads[intf.parent_element_key1], intf
        )
    distance2 = None
    if intf.parent_type_element2 == "Quad":
        distance2 = _distance_to_interface_plane(
            model.collections.quads[intf.parent_element_key2], intf
        )

    s1 = _side_sliding_spring(
        model,
        intf.parent_type_element1,
        intf.parent_element_key1,
        intf,
        out_of_plane=False,
        area=area,
        vertical=vertical,
        material_override=custom_material,
        law=in_law1,
        distance=distance1,
    )
    s2 = _side_sliding_spring(
        model,
        intf.parent_type_element2,
        intf.parent_element_key2,
        intf,
        out_of_plane=False,
        area=area,
        vertical=vertical,
        material_override=custom_material,
        law=in_law2,
        distance=distance2,
    )
    slid = _combine_coulomb(s1, s2, restrained)
    # C# invokes SetUltimateDisplacement after combining both sides.
    _set_coulomb_ultimate(slid, in_law1, in_law2)
    slid.key = 0
    slid.parent_key = intf.key
    slid.parent_type = "Interface"
    slid.spring_purpose = "Slid"
    slid.length = intf.length
    intf.slid = [slid]

    half_area = area / 2.0
    intf.slid_out_plan = []
    append_out = intf.slid_out_plan.append
    for index in range(2):
        o1 = _side_sliding_spring(
            model,
            intf.parent_type_element1,
            intf.parent_element_key1,
            intf,
            out_of_plane=True,
            area=half_area,
            vertical=vertical,
            material_override=custom_material,
            law=out_law1,
            distance=distance1,
        )
        o2 = _side_sliding_spring(
            model,
            intf.parent_type_element2,
            intf.parent_element_key2,
            intf,
            out_of_plane=True,
            area=half_area,
            vertical=vertical,
            material_override=custom_material,
            law=out_law2,
            distance=distance2,
        )
        out = _combine_coulomb(o1, o2, restrained)
        _set_coulomb_ultimate(out, out_law1, out_law2)
        out.key = index
        out.parent_key = intf.key
        out.parent_type = "Interface"
        out.spring_purpose = "SlidOutOfPlan"
        out.area = half_area
        out.length = intf.length / 2.0
        append_out(out)

    intf.status = InterfaceState()
    intf.status.init_from_interface(intf)
    intf._perf_di = intf._perf_dj = intf._perf_ecc = None
    intf._perf_area = None


def rebuild_interface_springs(
    model: Model,
    interface: Interface | int,
    *,
    flex_law_cache: dict[tuple[int, bool], _HystereticLaw] | None = None,
    sliding_law_cache: dict[tuple[int, bool, str], _CoulombLaw] | None = None,
) -> Interface:
    """Recreate one interface's constitutive definitions from its material key.

    Geometry, topology, DOFs and afference matrices are preserved.  A nonzero
    ``Interface.material_key`` overrides both parent material laws, matching
    C# ``InterfaceOperations.ReSetInterfaces``.

    Optional law caches let callers rebuilding several interfaces reuse the
    same immutable material-law definitions.  Omitting them preserves the
    existing one-interface behaviour.
    """
    if model.collections is None:
        raise ModelPreparationError("Model.collections is not initialized.")
    intf = (
        model.collections.interfaces[int(interface)]
        if isinstance(interface, int)
        else interface
    )
    _create_interface_springs(
        model,
        intf,
        flex_law_cache=flex_law_cache,
        sliding_law_cache=sliding_law_cache,
    )
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
    diagonal_law_cache: dict[
        int, tuple[_HystereticLaw, _CoulombLaw]
    ] = {}
    flex_law_cache: dict[tuple[int, bool], _HystereticLaw] = {}
    sliding_law_cache: dict[
        tuple[int, bool, str], _CoulombLaw
    ] = {}

    _assign_quad_afference(model)
    for quad in c.quads.values():
        quad.status = QuadState()
        quad.spring = _quad_spring(
            model, quad, law_cache=diagonal_law_cache
        )
        quad._perf_aff_pairs = None
        quad._perf_dn_edges = None
        quad._perf_dn_areas = None
    qq, qr = _generate_interfaces(model)
    _assign_interface_afference(model)
    for intf in c.interfaces.values():
        _create_interface_springs(
            model,
            intf,
            flex_law_cache=flex_law_cache,
            sliding_law_cache=sliding_law_cache,
        )
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
