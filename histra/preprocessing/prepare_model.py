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
from histra.preprocessing.contact_geometry import (
    _CONTACT_ANGLE_TOLERANCE,
    _CONTACT_AREA_TOLERANCE,
    _CONTACT_BATCH_SIZE,
    _CONTACT_DISTANCE_TOLERANCE,
    _TOL,
    _build_geometric_node_index,
    _clean_clipped_polygon,
    _clip_convex_quad_2d,
    _convex_quad_overlap_prefilter_batch,
    _coplanar_quad_intersection,
    _coplanar_quad_intersection_prechecked,
    _cross3,
    _cross3_f32,
    _cross_2d,
    _dot3_f32,
    _f32,
    _face_normal,
    _face_normals_batch,
    _find_or_create_geometric_node,
    _generate_interfaces,
    _interface_division_count,
    _line_intersection_2d,
    _make_interface_geometry,
    _norm3,
    _norm3_f32,
    _node_bucket,
    _p,
    _passes_csharp_lateral_area_filter,
    _polygon_area_2d,
    _polygon_area_3d,
    _polygon_edge_at_point,
    _prepare_interface_endpoints,
    _quad_contact_pairs,
    _quad_face_reference_edge,
    _quad_face_vertices,
    _quad_lateral_face_vertices,
    _quad_vint,
    _unit,
    _unit_f32,
    _v,
)
from histra.preprocessing.afference import (
    _QuadAfferenceGeometry,
    _assign_interface_afference,
    _assign_quad_afference,
    _bilinear,
    _bilinear_component_f32_nb,
    _bilinear_f32,
    _inverse_bilinear,
    _inverse_bilinear_f32,
    _inverse_bilinear_f32_bisection_reference,
    _inverse_bilinear_f32_nb,
    _inverse_bilinear_f32_python,
    _point_afference,
    _quad_afference_geometry,
    _rotation_afference,
    _warping_nodal_vectors,
    _warping_vector_at_point,
    _warping_vector_from_geometry,
)
from histra.preprocessing.fibre_geometry import (
    _bilinear_nb,
    _cell_vertices,
    _cross3_nb,
    _dot3_nb,
    _fiber_stiffness,
    _fiber_stiffness_batch,
    _fiber_stiffness_batch_nb,
    _interface_cells,
    _interface_cells_nb,
    _inverse_bilinear_nb,
    _norm3_nb,
    _polygon_areas_3d,
    _polygon_areas_3d_nb,
)
from histra.preprocessing.constitutive_laws import (
    CoulombLaw as _CoulombLaw,
    HystereticLaw as _HystereticLaw,
    diagonal_flex_law as _diagonal_flex_law,
    flex_law as _flex_law,
    material_bool as _bool,
    material_float as _float,
    shear_law as _shear_law,
    sliding_law as _sliding_law,
)
from histra.preprocessing.errors import ModelPreparationError
from histra.preprocessing.spring_factory import (
    _combine_coulomb,
    _combine_hysteretic,
    _combine_sliding,
    _configure_combined_hysteretic,
    _configure_combined_hysteretic_batch,
    _configure_coulomb,
    _configure_hysteretic,
    _copy_coulomb_spring,
    _copy_hysteretic_spring,
    _hysteretic_side_definition,
    _new_hysteretic_spring,
    _series,
    _set_coulomb_ultimate,
    _set_ultimate_displacement,
)
from histra.preprocessing.material_selection import (
    _blend_coulomb_laws,
    _cached_diagonal_laws,
    _cached_flex_law,
    _cached_sliding_law,
    _interface_sliding_law,
    _material,
)
from histra.springs.coulomb03 import SpringCoulomb03
from histra.springs.elastic import SpringElastic
from histra.springs.hysteretic import SpringHysteretic


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
        sp = _new_hysteretic_spring()
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
) -> SpringCoulomb03 | SpringElastic:
    assert model.collections is not None
    if parent_type == "Restraint":
        if law is not None and law.is_elastic:
            spring = SpringElastic(
                type_of="HiStrA.Objects.SpringLinearElastic", k_tang=-1.0
            )
        else:
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
    if law.is_elastic:
        return SpringElastic(
            type_of="HiStrA.Objects.SpringLinearElastic",
            k=k,
            k_tang=k,
            area=area,
            length=intf.length,
        )
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

    if not restrained:
        intf.trasv_1 = _configure_combined_hysteretic_batch(
            props1, law1, props2, law2, interface_key=intf.key
        )
    else:
        intf.trasv_1 = []
        append_transverse = intf.trasv_1.append
        for index in range(cell_count):
            k1, area1, length1 = map(float, props1[index])
            k2, area2, length2 = map(float, props2[index])

            if k1 == -1.0:
                sp1 = _new_hysteretic_spring()
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
                sp2 = _new_hysteretic_spring()
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
                spring = _copy_hysteretic_spring(
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
    slid = _combine_sliding(s1, s2, restrained)
    # C# invokes SetUltimateDisplacement after combining both sides.
    if isinstance(slid, SpringCoulomb03):
        _set_coulomb_ultimate(slid, in_law1, in_law2)
    slid.key = 0
    slid.parent_key = intf.key
    slid.parent_type = "Interface"
    slid.spring_purpose = "Slid"
    slid.length = intf.length
    intf.slid = [slid]

    half_area = area / 2.0
    intf.slid_out_plan = []

    # C# Interface.SetSpring creates the two *side* springs once, then invokes
    # CombinationSpring twice using those same temporaries.  Usually each call
    # returns a fresh combined spring.  For a restraint interface with a
    # custom material, however, the restraint-side placeholder has K == -1 and
    # CombinationSpring returns the active-side temporary itself.  Reusing the
    # temporaries therefore makes SlidOutPlan[0] and [1] the same object.
    # This is observable in the reference HRX (both entries serialize with
    # Key=1) and in the C# spring displacement, which accumulates both
    # interpolation contributions into the shared U field.
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
    for index in range(2):
        out = _combine_sliding(
            o1,
            o2,
            restrained,
            preserve_single_side_identity=(custom_material is not None and restrained),
        )
        if isinstance(out, SpringCoulomb03):
            _set_coulomb_ultimate(out, out_law1, out_law2)
        out.key = index
        out.parent_key = intf.key
        out.parent_type = "Interface"
        out.spring_purpose = "SlidOutOfPlan"
        out.area = half_area
        out.length = intf.length / 2.0
        intf.slid_out_plan.append(out)

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
    dirty = getattr(model, "_perf_initial_stiffness_dirty_interfaces", None)
    if dirty is None:
        dirty = set()
        model._perf_initial_stiffness_dirty_interfaces = dirty
    dirty.add(int(intf.key))
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
    for cache_name in (
        "_perf_element_stiffness_topology_signature",
        "_perf_element_stiffness_alfa",
        "_perf_initial_stiffness_dirty_interfaces",
    ):
        if hasattr(model, cache_name):
            delattr(model, cache_name)
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
