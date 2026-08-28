"""Interface spring-cell geometry and C# ``Quad.GetFiberProperties`` kernels.

The scalar functions in this module are exact test oracles and fallbacks; the
real multi-cell production path is the Numba/NumPy batch family
(``_interface_cells_nb``, ``_polygon_areas_3d_nb``, ``_fiber_stiffness_batch_nb``).

Numerical notes that must survive any refactor of this module:

* ``_bilinear_nb`` preserves the scalar/C# evaluation order exactly.
  Precomputing the four shape-function weights changes floating-point rounding
  because ``vertex * ((1 +/- u) * (1 +/- v) / 4)`` is not bitwise identical to
  ``vertex * (1 +/- u) * (1 +/- v) / 4``. Cell areas feed spring stiffnesses.
* Interface polygons are Microsoft.Xna.Framework.Vector3 values in C#, so the
  compiled cell construction keeps single precision before selected results
  are promoted to double.
* The compiled inverse bilinear returns error codes (degenerate mapping,
  zero fibre length, degenerate projection, zero area) that the scalar
  reference raises as :class:`ModelPreparationError`; both paths must agree on
  which cells fail.
"""

from __future__ import annotations

import math
from typing import Sequence

import numpy as np

try:
    from numba import njit
except Exception:  # pragma: no cover - scalar fallback remains available
    njit = None

from histra.elements.interface import Interface
from histra.elements.quad import Quad
from histra.model.model import Model
from histra.preprocessing.afference import (
    _bilinear,
    _inverse_bilinear,
)
from histra.preprocessing.contact_geometry import (
    _cross3,
    _norm3,
    _polygon_area_3d,
    _quad_vint,
    _unit,
    _v,
)
from histra.preprocessing.errors import ModelPreparationError


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
