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
from histra.preprocessing.spring_assignment import (
    _create_interface_springs,
    _distance_to_interface_plane,
    _interface_parent_material,
    _quad_spring,
    _side_sliding_spring,
    _side_transverse_spring,
    _transverse_side_properties_batch,
    rebuild_interface_springs,
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
