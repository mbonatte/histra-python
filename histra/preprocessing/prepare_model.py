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
    return [
        np.asarray(_bilinear(vertices, u, v), dtype=np.float32)
        for u, v in intrinsic
    ]


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
        # Interface polygons are Microsoft.Xna.Framework.Vector3 values in
        # C#.  Retain their single-precision construction before the fibre
        # routine promotes selected results to double.
        cells = np.empty((nrow * ncol, 4, 3), dtype=np.float32)
        point = np.empty(3, dtype=np.float32)
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
        a = np.empty(3, dtype=np.float32)
        b = np.empty(3, dtype=np.float32)
        normal = np.empty(3, dtype=np.float32)
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
        mapped = np.empty(3, dtype=np.float32)
        du = np.empty(3, dtype=np.float32)
        dv = np.empty(3, dtype=np.float32)
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
        face_a = np.empty(3, dtype=np.float32)
        face_b = np.empty(3, dtype=np.float32)
        face_cross = np.empty(3, dtype=np.float32)
        for j in range(3):
            face_a[j] = near_face[1,j] - near_face[0,j]
            face_b[j] = near_face[3,j] - near_face[0,j]
        _cross3_nb(face_a, face_b, face_cross)
        for idx in range(cells.shape[0]):
            points = cells[idx].copy()
            ca = np.empty(3, dtype=np.float32)
            cb = np.empty(3, dtype=np.float32)
            ccross = np.empty(3, dtype=np.float32)
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
            diff = np.empty(3, dtype=np.float32)
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
            ordered = np.empty((4,3), dtype=np.float32)
            for i in range(4):
                for j in range(3):
                    ordered[i,j] = points[(best_shift+i)%4,j]
            uv = np.empty((4,2), dtype=np.float32)
            far_points = np.empty((4,3), dtype=np.float32)
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
            center_near = np.empty(3, dtype=np.float32)
            center_far = np.empty(3, dtype=np.float32)
            _bilinear_nb(near_face, uc, vc, center_near)
            _bilinear_nb(far_face, uc, vc, center_far)
            cvec = np.empty(3, dtype=np.float32)
            for j in range(3):
                cvec[j] = center_far[j] - center_near[j]
            lp = _norm3_nb(cvec)
            if lp <= 1.0e-12:
                errors[idx] = 2
                continue
            for j in range(3):
                cvec[j] /= lp
            p0rel = np.empty(3, dtype=np.float32)
            for j in range(3):
                p0rel[j] = ordered[0,j] - center_near[j]
            axial = _dot3_nb(p0rel, cvec)
            vector3 = np.empty(3, dtype=np.float32)
            for j in range(3):
                vector3[j] = p0rel[j] - axial*cvec[j]
            nvec = _norm3_nb(vector3)
            if nvec <= 1.0e-12:
                errors[idx] = 3
                continue
            for j in range(3):
                vector3[j] /= nvec
            value = np.empty(3, dtype=np.float32)
            _cross3_nb(vector3, cvec, value)
            a5 = np.empty((4,3), dtype=np.float32)
            a7 = np.empty((4,3), dtype=np.float32)
            for i in range(4):
                relp = np.empty(3, dtype=np.float32)
                relf = np.empty(3, dtype=np.float32)
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
    vertices = np.asarray(vertices, dtype=np.float32)
    if njit is not None:
        return _interface_cells_nb(vertices, nrow, ncol)
    return np.asarray(
        [_cell_vertices(intf, index) for index in range(nrow * ncol)],
        dtype=np.float32,
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
        np.asarray(vints[face], dtype=np.float32),
        np.asarray(far_face, dtype=np.float32),
        np.asarray(cells, dtype=np.float32), float(E),
        np.asarray(intf.reference_e2, dtype=np.float32), output, errors,
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
