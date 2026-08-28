"""C#-compatible masonry material to constitutive-law mappings.

The authoritative implementation is
``ModelManagement.ComputationalElementsOperations/ConstitutiveLawOperations.cs``
and ``Objects.Material/MasonryMaterial.cs``.  Masonry properties are stored as
``System.Single`` in C#, so every numeric read is rounded to float32 before it
is promoted to Python's float.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from histra.model.masonry_material import MasonryMaterial


@dataclass(frozen=True)
class HystereticLaw:
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
class CoulombLaw:
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
    is_elastic: bool = False


def material_bool(
    material: MasonryMaterial, name: str, default: bool = False
) -> bool:
    return bool(material.value(name, default))


def material_float(
    material: MasonryMaterial, name: str, default: float = 0.0
) -> float:
    """Read a C# ``MasonryMaterial`` numeric property as ``System.Single``."""
    return float(np.float32(float(material.value(name, default))))


def _alfa_shear(material: MasonryMaterial) -> float:
    """Return C# ``MasonryMaterial.AlfaShear``'s clamped value."""
    value = material_float(material, "AlfaShearUser", 1.0)
    if value >= float(np.float32(0.99999)):
        return float(np.float32(0.99999))
    if value < float(np.float32(1.0e-5)):
        return float(np.float32(1.0e-5))
    return value


def flex_law(material: MasonryMaterial, *, vertical: bool = False) -> HystereticLaw:
    suffix = "Ver" if vertical else "Hor"
    curve_suffix = "Vertical" if vertical else ""
    E = material_float(material, "Ever" if vertical else "Ehor")
    fy_t = material_float(material, f"Ftm{suffix}")
    fy_c = material_float(material, f"Fm{suffix}")
    duct_t = material_float(material, f"DuctTrazRocking{suffix}", 1.0)
    duct_c = material_float(material, f"DuctComprRocking{suffix}", 1.0)
    # ConstitutiveLawHysteretic uses IsDuct*=true for effectively unlimited
    # ultimate strain and false for a yield-strain-scaled ductility value.
    eps_t = (
        1.0e20
        if material_bool(material, "IsDuctTraz", True)
        else duct_t * fy_t / E
    )
    eps_c = (
        1.0e20
        if material_bool(material, "IsDuctCompr", False)
        else duct_c * fy_c / E
    )
    return HystereticLaw(
        E=E,
        fy_t=fy_t,
        fy_c=fy_c,
        tensile_curve=str(
            material.value(f"TensileCurveType{curve_suffix}", "LinearSoftening")
        ),
        compressive_curve=str(
            material.value(
                f"CompressiveCurveType{curve_suffix}", "LinearSoftening"
            )
        ),
        ratio_et_t=material_float(material, "RatioEtTraction"),
        ratio_et_c=material_float(material, "RatioEtCompression"),
        alfa_r_t=1.0,
        alfa_r_c=1.0,
        alfa_u_t=material_float(material, f"BetaUnloadTractionRocking{suffix}"),
        alfa_u_c=material_float(material, f"BetaUnloadCompressionRocking{suffix}"),
        G_t=material_float(material, "GtVer" if vertical else "Gt"),
        G_c=material_float(material, "GcVer" if vertical else "Gc"),
        eps_u_t=eps_t,
        eps_u_c=eps_c,
        law_type=str(material.value("ConstitutiveLawFlex", "Hysteretic")),
    )


def diagonal_flex_law(material: MasonryMaterial) -> HystereticLaw:
    """Apply C# ``PropOrthotropyParameter(sqrt(2)/2, sqrt(2)/2)``."""
    vertical = flex_law(material, vertical=True)
    horizontal = flex_law(material, vertical=False)
    c = math.sqrt(2.0) / 2.0
    w = c * c
    elasto_plastic = vertical.law_type.startswith("ElastoPlastic")
    return HystereticLaw(
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
        # Preserve ConstitutiveLawElastoPlastic's source-level asymmetry.
        eps_u_t=(vertical.eps_u_t * c + horizontal.eps_u_t * c)
        if elasto_plastic
        else (vertical.eps_u_t * w + horizontal.eps_u_t * w),
        eps_u_c=vertical.eps_u_c * w + horizontal.eps_u_c * w,
        law_type=vertical.law_type,
    )


def shear_law(material: MasonryMaterial) -> CoulombLaw:
    law_type = str(material.value("ConstitutiveLawMasonryShear", ""))
    is_ductility = law_type in {"Elastic", "ElastoPlastic"}
    return CoulombLaw(
        E=material_float(material, "Gd") / _alfa_shear(material),
        cohesion=material_float(material, "fvk0d"),
        mu=material_float(material, "FrictionRatioShear"),
        plastic_stiffness_ratio=material_float(
            material, "ShearPlasticStiffnessRatio"
        ),
        max_tensile_ratio=material_float(material, "ShearMaxTensileRatio", 0.5),
        reload_stiffness_ratio=material_float(
            material, "ShearReloadStiffnessRatio", 1.0
        ),
        plastic_stiffness_ratio2=material_float(
            material, "ShearPlasticStiffnessRatio2", 1.0
        ),
        plastic_strain=material_float(material, "ShearPlasticStrain", 100.0),
        sub_law=str(material.value("CriterioSnervamento", "Coulomb")),
        hysteretic_type=str(material.value("UnloadShear", "Initial")),
        fracture_energy=(law_type == "ElastoPlasticFractureEnergyFixed"),
        G=material_float(material, "FractureEnergyShear"),
        ductility=(
            1.0e20
            if is_ductility
            else material_float(material, "DuctilityShear", 100.0)
        ),
        is_ductility_fixed=not is_ductility,
        check_contact_area=material_bool(material, "CheckContactArea", False),
        bcacovic=material_float(material, "Bcacovic"),
    )


def sliding_law(
    material: MasonryMaterial,
    *,
    out_of_plane: bool,
    direction: str,
) -> CoulombLaw:
    """Map one of C#'s horizontal, vertical or direction-3 sliding laws."""
    normalized = direction.casefold()
    if normalized not in {"hor", "vert", "dir3"}:
        raise ValueError(f"Unsupported sliding-law direction {direction!r}.")

    E = material_float(material, "Gd")
    if not out_of_plane and normalized != "dir3":
        E = 2.0 * E / (1.0 - _alfa_shear(material))

    if normalized == "hor":
        suffix = "Hor"
        fracture_name = "SlidingFractureEnergy"
        energy_name = "Gs"
        max_tensile_name = "SlidingMaxTensileRatioHor"
    elif normalized == "vert":
        suffix = "Vert"
        fracture_name = "SlidingFractureEnergyVer"
        # C# out-of-plane vertical sliding deliberately uses Gs, not GsVer.
        energy_name = "Gs" if out_of_plane else "GsVer"
        max_tensile_name = "SlidingMaxTensileRatioVer"
    else:
        suffix = "Dir3"
        fracture_name = "SlidingFractureEnergyDir3"
        energy_name = "GsDir3"
        max_tensile_name = "SlidingMaxTensileRatioVer"

    enabled_name = {
        "hor": "scorrhor",
        "vert": "scorrvert",
        "dir3": "scorrDir3",
    }[normalized]
    sub_law_name = (
        "CriterioSnervamento"
        if out_of_plane
        else f"SlidingYieldingDomain{suffix}"
    )
    return CoulombLaw(
        E=E,
        cohesion=material_float(material, f"CohesionSliding{suffix}"),
        mu=material_float(material, f"FrictionRatioSliding{suffix}"),
        plastic_stiffness_ratio=material_float(
            material, f"SlidingPlasticStiffnessRatio{suffix}"
        ),
        max_tensile_ratio=material_float(material, max_tensile_name, 0.8),
        sub_law=str(material.value(sub_law_name, "Coulomb")),
        hysteretic_type="Initial",
        fracture_energy=material_bool(material, fracture_name, False),
        G=material_float(material, energy_name),
        ductility=100000.0,
        is_ductility_fixed=True,
        check_contact_area=material_bool(material, "CheckContactArea", False),
        is_elastic=not material_bool(material, enabled_name, False),
    )


__all__ = [
    "CoulombLaw",
    "HystereticLaw",
    "diagonal_flex_law",
    "flex_law",
    "material_bool",
    "material_float",
    "shear_law",
    "sliding_law",
]
