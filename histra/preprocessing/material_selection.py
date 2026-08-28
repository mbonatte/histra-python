"""Masonry material lookup and C# constitutive-law selection/blending.

Owns the immutable material-to-law mapping consumed by model preparation:
cached flexural, diagonal and sliding law construction, the
``ConstitutiveLawCoulomb.PropOrthotropyParameter`` orthotropic blend and the
``Interface.SetSpring`` sliding-law slot selection (broad faces 4/5 use the
direction-3 law; other faces blend horizontal/vertical by the interface/quad
e1 alignment).

C# authorities:

- ``ModelManagement.ComputationalElementsOperations/ConstitutiveLawOperations.cs``
- ``Objects.Material/MasonryMaterial.cs``
- ``Objects.ConstitutiveLaw/ConstitutiveLawCoulomb.cs``

This module must not depend on spring construction; it selects parameters only.
"""

from __future__ import annotations

import math

import numpy as np

from histra.elements.interface import Interface
from histra.model.masonry_material import MasonryMaterial
from histra.model.model import Model
from histra.preprocessing.constitutive_laws import (
    CoulombLaw as _CoulombLaw,
    HystereticLaw as _HystereticLaw,
    diagonal_flex_law as _diagonal_flex_law,
    flex_law as _flex_law,
    shear_law as _shear_law,
    sliding_law as _sliding_law,
)
from histra.preprocessing.errors import ModelPreparationError


def _material(model: Model, key: int) -> MasonryMaterial:
    assert model.collections is not None
    try:
        return model.collections.materials[key]
    except KeyError as exc:
        raise ModelPreparationError(f"Missing MasonryMaterial key {key}.") from exc


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
        # PropOrthotropyParameter changes values on the primary C# law; it
        # does not change its runtime constitutive-law type.
        is_elastic=primary.is_elastic,
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
