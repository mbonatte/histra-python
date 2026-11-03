"""Generalized-DOF afference mappings and inverse bilinear interpolation.

The Quad and Interface afference matrices translated from C#
``ModelManager.PrepareModel`` / ``AfferenceMatrix`` live here, together with the
float32 forward/inverse bilinear maps used by the shear-DOF warping
interpolation (C# ``Operations.GetValueFromIntrinsecSystem`` and
``GetIntrinsecCoordinates``).

Numerical notes that must survive any refactor of this module:

* the C# inverse is a bisection over projected polygon strips, not a Newton
  solve; the bisection reference is kept alongside the faster float32 Newton
  path that reproduces the converged serialized results;
* every float32 operation is explicit (``np.float32`` casts and helper
  rounding) because the shear-DOF afference coefficients are sensitive to
  reduction order;
* the Numba kernels mirror the scalar float32 reference operation by
  operation and are compared bit-exactly by ``uint32`` patterns in tests.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np

try:
    from numba import njit
except Exception:  # pragma: no cover - scalar fallback remains available
    njit = None

from histra.elements.interface_state import InterfaceState
from histra.elements.quad import Quad
from histra.model.model import Model
from histra.preprocessing.contact_geometry import (
    _cross3,
    _cross3_f32,
    _dot3_f32,
    _f32,
    _unit_f32,
    _v,
)
from histra.preprocessing.errors import ModelPreparationError
from histra.preprocessing.intrinsic_coordinates import native_projected_intrinsic
from histra.types.afference_entry import AfferenceEntry


if njit is not None:
    @njit(cache=True)
    def _bilinear_f32_nb(warping_nodal: np.ndarray, u: float, v: float) -> np.ndarray:
        one = np.float32(1.0)
        four = np.float32(4.0)
        u_f = np.float32(u)
        v_f = np.float32(v)
        w0 = np.float32(np.float32(np.float32(one - u_f) * np.float32(one - v_f)) / four)
        w1 = np.float32(np.float32(np.float32(one + u_f) * np.float32(one - v_f)) / four)
        w2 = np.float32(np.float32(np.float32(one + u_f) * np.float32(one + v_f)) / four)
        w3 = np.float32(np.float32(np.float32(one - u_f) * np.float32(one + v_f)) / four)
        out = np.zeros(3, dtype=np.float32)
        for i in range(3):
            out[i] = np.float32(out[i] + np.float32(warping_nodal[0, i] * w0))
            out[i] = np.float32(out[i] + np.float32(warping_nodal[1, i] * w1))
            out[i] = np.float32(out[i] + np.float32(warping_nodal[2, i] * w2))
            out[i] = np.float32(out[i] + np.float32(warping_nodal[3, i] * w3))
        return out

    @njit(cache=True)
    def _warping_vector_nb(vertices: np.ndarray, warping_nodal: np.ndarray, point: np.ndarray, node_tolerance: float) -> np.ndarray:
        uv = native_projected_intrinsic(vertices, point, node_tolerance)
        return _bilinear_f32_nb(warping_nodal, uv[0], uv[1])

    @njit(cache=True, inline="always")
    def _point_afference_nb(
        rx, ry, rz, dx, dy, dz, wx, wy, wz, is_lateral,
        aff_gdls, aff_alfas, out_gdl, out_alfa
    ):
        f = np.float32
        shear = f(f(f(wx * f(dx)) + f(wy * f(dy))) + f(wz * f(dz))) if is_lateral else f(0.0)
        c0 = dx
        c1 = dy
        c2 = dz
        c3 = f(f(ry * dz) - f(rz * dy))
        c4 = f(f(rz * dx) - f(rx * dz))
        c5 = f(f(rx * dy) - f(ry * dx))
        c6 = shear

        cnt = 0
        if abs(c0) > 1.0e-4:
            out_gdl[cnt] = aff_gdls[0]; out_alfa[cnt] = float(c0 * aff_alfas[0]); cnt += 1
        if abs(c1) > 1.0e-4:
            out_gdl[cnt] = aff_gdls[1]; out_alfa[cnt] = float(c1 * aff_alfas[1]); cnt += 1
        if abs(c2) > 1.0e-4:
            out_gdl[cnt] = aff_gdls[2]; out_alfa[cnt] = float(c2 * aff_alfas[2]); cnt += 1
        if abs(c3) > 1.0e-4:
            out_gdl[cnt] = aff_gdls[3]; out_alfa[cnt] = float(c3 * aff_alfas[3]); cnt += 1
        if abs(c4) > 1.0e-4:
            out_gdl[cnt] = aff_gdls[4]; out_alfa[cnt] = float(c4 * aff_alfas[4]); cnt += 1
        if abs(c5) > 1.0e-4:
            out_gdl[cnt] = aff_gdls[5]; out_alfa[cnt] = float(c5 * aff_alfas[5]); cnt += 1
        if abs(c6) > 1.0e-4:
            out_gdl[cnt] = aff_gdls[6]; out_alfa[cnt] = float(c6 * aff_alfas[6]); cnt += 1

        return cnt
else:
    _bilinear_f32_nb = None
    _warping_vector_nb = None
    _point_afference_nb = None


@dataclass(frozen=True)
class _QuadAfferenceGeometry:
    centre: np.ndarray
    vertices: np.ndarray
    normal: np.ndarray
    warping_nodal: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]
    node_tolerance: float = 1.0


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
        quad._aff_by_local = tuple((gdl + i, 1.0) for i in range(7))
        gdl += 7
    model.gdl = gdl - 1


def _warping_nodal_vectors(quad: Quad, normal: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    # Quad.GetDisplacementFromShearDOF builds these vectors with XNA Vector3
    # and Convert.ToSingle intermediates.
    e1 = np.asarray(quad.reference_e1, dtype=np.float32)
    e2 = (np.asarray(quad.reference_e2, dtype=np.float32) if normal is None
          else _cross3_f32(normal, e1))
    zero = np.zeros(3, dtype=np.float32)
    if abs(quad.sin[2]) <= 1.0e-12:
        node2 = zero.copy()
    else:
        scale_e1 = _f32(
            -float(quad.length[3]) * float(quad.sin[3])
            * float(quad.sin[1]) / float(quad.sin[2])
        )
        scale_e2 = _f32(
            -float(quad.length[3]) * float(quad.sin[3])
            * float(quad.cos[1]) / float(quad.sin[2])
        )
        node2 = np.asarray(
            [
                _f32(_f32(e1[i] * scale_e1) + _f32(e2[i] * scale_e2))
                for i in range(3)
            ],
            dtype=np.float32,
        )
    scale_e1 = _f32(-float(quad.length[3]) * float(quad.sin[0]))
    scale_e2 = _f32(float(quad.length[3]) * float(quad.cos[0]))
    node3 = np.asarray(
        [
            _f32(_f32(e1[i] * scale_e1) + _f32(e2[i] * scale_e2))
            for i in range(3)
        ],
        dtype=np.float32,
    )
    return zero.copy(), zero.copy(), node2, node3


def _quad_afference_geometry(model: Model, quad: Quad) -> _QuadAfferenceGeometry:
    assert model.collections is not None
    vertices = np.asarray(
        [_v(model.collections.nodes[key].point) for key in quad.node_keys],
        dtype=np.float32,
    )
    normal = _unit_f32(
        _cross3_f32(vertices[1] - vertices[0], vertices[2] - vertices[0]),
        label=f"Quad {quad.key} midsurface normal",
    )
    return _QuadAfferenceGeometry(
        centre=np.asarray(_v(quad.g), dtype=np.float32),
        vertices=vertices,
        normal=normal,
        warping_nodal=_warping_nodal_vectors(quad, normal),
        node_tolerance=float(getattr(model, "geometry_tolerance_node", 1.0)),
    )


def _warping_vector_from_geometry(
    geometry: _QuadAfferenceGeometry, point: np.ndarray
) -> np.ndarray:
    from histra.preprocessing.intrinsic_coordinates import native_projected_intrinsic

    u, v = native_projected_intrinsic(
        geometry.vertices, np.asarray(point, dtype=np.float32),
        np.float32(geometry.node_tolerance),
    )
    return _bilinear_f32(geometry.warping_nodal, u, v)
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
    model: Model, quad: Quad, point: Sequence[float], node_key: int,
    direction: Sequence[float] | np.ndarray, *, face: int,
    _geometry: _QuadAfferenceGeometry | None = None,
    _point_cache: dict[
        tuple[int, int], tuple[float, float, float, np.ndarray | None]
    ] | None = None,
) -> list[AfferenceEntry]:
    geometry = (
        _quad_afference_geometry(model, quad)
        if _geometry is None
        else _geometry
    )
    cache_key = (int(quad.key), int(node_key))
    cached = None if _point_cache is None else _point_cache.get(cache_key)
    f = np.float32
    if cached is None:
        px = float(point[0])
        py = float(point[1])
        pz = float(point[2])
        cx, cy, cz = geometry.centre
        rx = float(f(px - cx))
        ry = float(f(py - cy))
        rz = float(f(pz - cz))
        warping = None
    else:
        rx, ry, rz, warping = cached

    if face <= 3 and warping is None:
        pt_arr = np.asarray(point, dtype=np.float32)
        warping = _warping_vector_from_geometry(geometry, pt_arr)
    if _point_cache is not None:
        if cached is None or (cached[3] is None and warping is not None):
            _point_cache[cache_key] = (rx, ry, rz, warping)

    dx = float(f(direction[0]))
    dy = float(f(direction[1]))
    dz = float(f(direction[2]))
    shear = 0.0 if face > 3 else float(f(warping[0] * dx + warping[1] * dy + warping[2] * dz))
    coeff = (
        dx,
        dy,
        dz,
        float(f(f(ry * dz) - f(rz * dy))),
        float(f(f(rz * dx) - f(rx * dz))),
        float(f(f(rx * dy) - f(ry * dx))),
        shear,
    )
    out: list[AfferenceEntry] = []
    append = out.append
    aff_local = getattr(quad, "_aff_by_local", None)
    if aff_local is not None:
        for local, value in enumerate(coeff):
            if abs(value) <= 1.0e-4:
                continue
            gdl, alfa = aff_local[local]
            append(AfferenceEntry(gdl=gdl, alfa=float(value * alfa)))
    else:
        for local, value in enumerate(coeff):
            if abs(value) <= 1.0e-4:
                continue
            for entry in quad.aff[local]:
                append(
                    AfferenceEntry(gdl=entry.gdl, alfa=float(value * entry.alfa))
                )
    return out


def _rotation_afference(quad: Quad, direction: np.ndarray) -> list[AfferenceEntry]:
    out: list[AfferenceEntry] = []
    append = out.append
    aff_local = getattr(quad, "_aff_by_local", None)
    if aff_local is not None:
        for local in (3, 4, 5):
            value = float(np.float32(direction[local - 3]))
            if abs(value) <= 1.0e-4:
                continue
            gdl, alfa = aff_local[local]
            append(AfferenceEntry(gdl=gdl, alfa=value * alfa))
    else:
        for local in range(3, 6):
            value = float(np.float32(direction[local - 3]))
            if abs(value) <= 1.0e-4:
                continue
            for entry in quad.aff[local]:
                append(AfferenceEntry(gdl=entry.gdl, alfa=value * entry.alfa))
    return out


def _assign_interface_afference(model: Model) -> None:
    assert model.collections is not None
    c = model.collections

    if _point_afference_nb is not None:
        point_cache: dict[tuple[int, int], tuple[float, float, float, np.ndarray | None]] = {}
        f = np.float32

        # Pre-compute cached geometry and dof arrays for all quads
        for quad in c.quads.values():
            aff_local = getattr(quad, "_aff_by_local", None)
            if aff_local is not None:
                quad._prep_gdls = np.asarray([entry[0] for entry in aff_local], dtype=np.int64)
                quad._prep_alfas = np.asarray([entry[1] for entry in aff_local], dtype=np.float64)
            else:
                quad._prep_gdls = np.asarray([quad.aff[i][0].gdl if quad.aff[i] else 0 for i in range(7)], dtype=np.int64)
                quad._prep_alfas = np.asarray([quad.aff[i][0].alfa if quad.aff[i] else 0.0 for i in range(7)], dtype=np.float64)

            geom = _quad_afference_geometry(model, quad)
            w_nodal = np.vstack(geom.warping_nodal)
            quad._prep_geom = (geom, geom.centre, geom.vertices, geom.normal, w_nodal, geom.node_tolerance)

        gdl_buf = np.empty(7, dtype=np.int64)
        alfa_buf = np.empty(7, dtype=np.float64)

        for intf in c.interfaces.values():
            intf_aff = [[] for _ in range(12)]
            e1 = np.asarray(intf.reference_e1, dtype=np.float32)
            e2 = np.asarray(intf.reference_e2, dtype=np.float32)
            e3 = np.asarray(intf.reference_e3, dtype=np.float32)

            n0_key = intf.node_keys[0]
            n1_key = intf.node_keys[1]
            n0 = c.nodes[n0_key].point
            n1 = c.nodes[n1_key].point
            p0 = (n0.x, n0.y, n0.z)
            p1 = (n1.x, n1.y, n1.z)
            p0_arr = np.asarray(p0, dtype=f)
            p1_arr = np.asarray(p1, dtype=f)

            # Parent 1
            p1_type = intf.parent_type_element1
            p1_key = intf.parent_element_key1
            if p1_type == "Quad":
                q1 = c.quads[p1_key]
                geom1, centre, verts, normal, w_nodal, tol = q1._prep_geom
                is_lat = intf.face1 <= 3

                ck0 = (p1_key, n0_key)
                cached0 = point_cache.get(ck0)
                if cached0 is None:
                    rx0 = float(f(p0[0] - centre[0]))
                    ry0 = float(f(p0[1] - centre[1]))
                    rz0 = float(f(p0[2] - centre[2]))
                    w0 = _warping_vector_from_geometry(geom1, p0_arr) if is_lat else None
                    cached0 = (rx0, ry0, rz0, w0)
                    point_cache[ck0] = cached0
                else:
                    rx0, ry0, rz0, w0 = cached0
                    if is_lat and w0 is None:
                        w0 = _warping_vector_from_geometry(geom1, p0_arr)
                        cached0 = (rx0, ry0, rz0, w0)
                        point_cache[ck0] = cached0

                ck1 = (p1_key, n1_key)
                cached1 = point_cache.get(ck1)
                if cached1 is None:
                    rx1 = float(f(p1[0] - centre[0]))
                    ry1 = float(f(p1[1] - centre[1]))
                    rz1 = float(f(p1[2] - centre[2]))
                    w1 = _warping_vector_from_geometry(geom1, p1_arr) if is_lat else None
                    cached1 = (rx1, ry1, rz1, w1)
                    point_cache[ck1] = cached1
                else:
                    rx1, ry1, rz1, w1 = cached1
                    if is_lat and w1 is None:
                        w1 = _warping_vector_from_geometry(geom1, p1_arr)
                        cached1 = (rx1, ry1, rz1, w1)
                        point_cache[ck1] = cached1

                wx0 = 0.0 if w0 is None else float(w0[0])
                wy0 = 0.0 if w0 is None else float(w0[1])
                wz0 = 0.0 if w0 is None else float(w0[2])

                wx1 = 0.0 if w1 is None else float(w1[0])
                wy1 = 0.0 if w1 is None else float(w1[1])
                wz1 = 0.0 if w1 is None else float(w1[2])

                q_gdls = q1._prep_gdls
                q_alfas = q1._prep_alfas

                cnt = _point_afference_nb(rx0, ry0, rz0, float(e2[0]), float(e2[1]), float(e2[2]), wx0, wy0, wz0, is_lat, q_gdls, q_alfas, gdl_buf, alfa_buf)
                intf_aff[0] = [AfferenceEntry(int(gdl_buf[i]), float(alfa_buf[i])) for i in range(cnt)]

                cnt = _point_afference_nb(rx1, ry1, rz1, float(e2[0]), float(e2[1]), float(e2[2]), wx1, wy1, wz1, is_lat, q_gdls, q_alfas, gdl_buf, alfa_buf)
                intf_aff[1] = [AfferenceEntry(int(gdl_buf[i]), float(alfa_buf[i])) for i in range(cnt)]

                intf_aff[4] = _rotation_afference(q1, e1)

                cnt = _point_afference_nb(rx1, ry1, rz1, float(e1[0]), float(e1[1]), float(e1[2]), wx1, wy1, wz1, is_lat, q_gdls, q_alfas, gdl_buf, alfa_buf)
                intf_aff[6] = [AfferenceEntry(int(gdl_buf[i]), float(alfa_buf[i])) for i in range(cnt)]

                cnt = _point_afference_nb(rx0, ry0, rz0, float(e3[0]), float(e3[1]), float(e3[2]), wx0, wy0, wz0, is_lat, q_gdls, q_alfas, gdl_buf, alfa_buf)
                intf_aff[8] = [AfferenceEntry(int(gdl_buf[i]), float(alfa_buf[i])) for i in range(cnt)]

                cnt = _point_afference_nb(rx1, ry1, rz1, float(e3[0]), float(e3[1]), float(e3[2]), wx1, wy1, wz1, is_lat, q_gdls, q_alfas, gdl_buf, alfa_buf)
                intf_aff[9] = [AfferenceEntry(int(gdl_buf[i]), float(alfa_buf[i])) for i in range(cnt)]
            elif p1_type != "Restraint":
                raise ModelPreparationError(
                    f"Interface {intf.key} has unsupported parent type {p1_type!r}."
                )

            # Parent 2
            p2_type = intf.parent_type_element2
            p2_key = intf.parent_element_key2
            if p2_type == "Quad":
                q2 = c.quads[p2_key]
                geom2, centre, verts, normal, w_nodal, tol = q2._prep_geom
                is_lat2 = intf.face2 <= 3

                ck0 = (p2_key, n0_key)
                cached0 = point_cache.get(ck0)
                if cached0 is None:
                    rx0 = float(f(p0[0] - centre[0]))
                    ry0 = float(f(p0[1] - centre[1]))
                    rz0 = float(f(p0[2] - centre[2]))
                    w0 = _warping_vector_from_geometry(geom2, p0_arr) if is_lat2 else None
                    cached0 = (rx0, ry0, rz0, w0)
                    point_cache[ck0] = cached0
                else:
                    rx0, ry0, rz0, w0 = cached0
                    if is_lat2 and w0 is None:
                        w0 = _warping_vector_from_geometry(geom2, p0_arr)
                        cached0 = (rx0, ry0, rz0, w0)
                        point_cache[ck0] = cached0

                ck1 = (p2_key, n1_key)
                cached1 = point_cache.get(ck1)
                if cached1 is None:
                    rx1 = float(f(p1[0] - centre[0]))
                    ry1 = float(f(p1[1] - centre[1]))
                    rz1 = float(f(p1[2] - centre[2]))
                    w1 = _warping_vector_from_geometry(geom2, p1_arr) if is_lat2 else None
                    cached1 = (rx1, ry1, rz1, w1)
                    point_cache[ck1] = cached1
                else:
                    rx1, ry1, rz1, w1 = cached1
                    if is_lat2 and w1 is None:
                        w1 = _warping_vector_from_geometry(geom2, p1_arr)
                        cached1 = (rx1, ry1, rz1, w1)
                        point_cache[ck1] = cached1

                wx0 = 0.0 if w0 is None else float(w0[0])
                wy0 = 0.0 if w0 is None else float(w0[1])
                wz0 = 0.0 if w0 is None else float(w0[2])

                wx1 = 0.0 if w1 is None else float(w1[0])
                wy1 = 0.0 if w1 is None else float(w1[1])
                wz1 = 0.0 if w1 is None else float(w1[2])

                q_gdls = q2._prep_gdls
                q_alfas = q2._prep_alfas

                cnt = _point_afference_nb(rx0, ry0, rz0, float(e2[0]), float(e2[1]), float(e2[2]), wx0, wy0, wz0, is_lat2, q_gdls, q_alfas, gdl_buf, alfa_buf)
                intf_aff[3] = [AfferenceEntry(int(gdl_buf[i]), float(alfa_buf[i])) for i in range(cnt)]

                cnt = _point_afference_nb(rx1, ry1, rz1, float(e2[0]), float(e2[1]), float(e2[2]), wx1, wy1, wz1, is_lat2, q_gdls, q_alfas, gdl_buf, alfa_buf)
                intf_aff[2] = [AfferenceEntry(int(gdl_buf[i]), float(alfa_buf[i])) for i in range(cnt)]

                intf_aff[5] = _rotation_afference(q2, e1)

                cnt = _point_afference_nb(rx1, ry1, rz1, float(e1[0]), float(e1[1]), float(e1[2]), wx1, wy1, wz1, is_lat2, q_gdls, q_alfas, gdl_buf, alfa_buf)
                intf_aff[7] = [AfferenceEntry(int(gdl_buf[i]), float(alfa_buf[i])) for i in range(cnt)]

                cnt = _point_afference_nb(rx0, ry0, rz0, float(e3[0]), float(e3[1]), float(e3[2]), wx0, wy0, wz0, is_lat2, q_gdls, q_alfas, gdl_buf, alfa_buf)
                intf_aff[10] = [AfferenceEntry(int(gdl_buf[i]), float(alfa_buf[i])) for i in range(cnt)]

                cnt = _point_afference_nb(rx1, ry1, rz1, float(e3[0]), float(e3[1]), float(e3[2]), wx1, wy1, wz1, is_lat2, q_gdls, q_alfas, gdl_buf, alfa_buf)
                intf_aff[11] = [AfferenceEntry(int(gdl_buf[i]), float(alfa_buf[i])) for i in range(cnt)]
            elif p2_type != "Restraint":
                raise ModelPreparationError(
                    f"Interface {intf.key} has unsupported parent type {p2_type!r}."
                )

            intf.aff = intf_aff
            if intf.status is None:
                intf.status = InterfaceState()
                intf.status.init_from_interface(intf)
            intf._perf_aff_pairs = None
        return

    geometry_cache: dict[int, _QuadAfferenceGeometry] = {}
    point_cache: dict[
        tuple[int, int], tuple[np.ndarray, np.ndarray | None]
    ] = {}
    for intf in c.interfaces.values():
        intf.aff = [[] for _ in range(12)]
        e1 = np.asarray(intf.reference_e1, dtype=np.float32)
        e2 = np.asarray(intf.reference_e2, dtype=np.float32)
        e3 = np.asarray(intf.reference_e3, dtype=np.float32)
        n0 = c.nodes[intf.node_keys[0]].point
        n1 = c.nodes[intf.node_keys[1]].point
        points = ((n0.x, n0.y, n0.z), (n1.x, n1.y, n1.z))
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
        if intf.status is None:
            intf.status = InterfaceState()
            intf.status.init_from_interface(intf)
        intf._perf_aff_pairs = None


def _bilinear(vertices: Sequence[np.ndarray], u: float, v: float) -> np.ndarray:
    return (
        vertices[0] * (1.0-u)*(1.0-v)/4.0
        + vertices[1] * (1.0+u)*(1.0-v)/4.0
        + vertices[2] * (1.0+u)*(1.0+v)/4.0
        + vertices[3] * (1.0-u)*(1.0+v)/4.0
    )


def _bilinear_f32(
    vertices: Sequence[np.ndarray], u: np.float32, v: np.float32
) -> np.ndarray:
    """C# ``Operations.GetValueFromIntrinsecSystem`` in single precision."""
    one = _f32(1.0)
    four = _f32(4.0)
    weights = (
        _f32(_f32(_f32(one-u) * _f32(one-v)) / four),
        _f32(_f32(_f32(one+u) * _f32(one-v)) / four),
        _f32(_f32(_f32(one+u) * _f32(one+v)) / four),
        _f32(_f32(_f32(one-u) * _f32(one+v)) / four),
    )
    out = np.zeros(3, dtype=np.float32)
    for vertex, weight in zip(vertices, weights):
        vertex_f = np.asarray(vertex, dtype=np.float32)
        for index in range(3):
            out[index] = _f32(out[index] + _f32(vertex_f[index] * weight))
    return out


def _inverse_bilinear_f32_bisection_reference(
    vertices: Sequence[np.ndarray], point: np.ndarray
) -> tuple[np.float32, np.float32]:
    """C# ``Operations.GetIntrinsecCoordinates`` compatibility path.

    Despite the method's purpose, the desktop code does not use a Newton
    inverse.  It projects the surface to a local 2-D system and bisects two
    polygon strips to a tolerance of 0.001.  Replacing it with an algebraically
    more accurate inverse changes the shear-DOF afference by up to 4e-3 in the
    bridge models.
    """
    vertices_f = tuple(np.asarray(vertex, dtype=np.float32) for vertex in vertices)
    point_f = np.asarray(point, dtype=np.float32)
    e1 = _unit_f32(vertices_f[1]-vertices_f[0], label="intrinsic e1")
    normal = _unit_f32(
        _cross3_f32(e1, vertices_f[3]-vertices_f[0]),
        label="intrinsic normal",
    )
    e2 = _cross3_f32(normal, e1)

    def project(value: np.ndarray) -> np.ndarray:
        delta = np.asarray(value-vertices_f[0], dtype=np.float32)
        return np.asarray(
            (_dot3_f32(delta, e1), _dot3_f32(delta, e2)),
            dtype=np.float32,
        )

    polygon = tuple(project(vertex) for vertex in vertices_f)
    target = project(point_f)
    tolerance_node = 1.0

    def align(value: np.ndarray, start: np.ndarray, end: np.ndarray) -> int:
        x, y = float(value[0]), float(value[1])
        x1, y1 = float(start[0]), float(start[1])
        x2, y2 = float(end[0]), float(end[1])
        if abs(x-x1) < tolerance_node and abs(y-y1) < tolerance_node:
            return 2
        if abs(x-x2) < tolerance_node and abs(y-y2) < tolerance_node:
            return 3
        dx, dy = x2-x1, y2-y1
        px, py = x-x1, y-y1
        length = math.sqrt(dx*dx+dy*dy)
        point_length = math.sqrt(px*px+py*py)
        if length == 0.0 or point_length == 0.0:
            return 0
        cosine = max(-1.0, min(1.0, (dx*px+dy*py)/(length*point_length)))
        distance = math.sqrt(max(0.0, 1.0-cosine*cosine))*point_length
        if not (-tolerance_node < distance < tolerance_node):
            return 0
        return 1 if cosine > 0.0 and point_length <= length else -1

    def inside(poly: Sequence[np.ndarray]) -> bool:
        previous = len(poly)-1
        flag = False
        for index, vertex in enumerate(poly):
            following = poly[(index+1) % len(poly)]
            if align(target, vertex, following) > 0:
                return True
            py = target[1]
            if (
                ((vertex[1] <= py < poly[previous][1])
                 or (poly[previous][1] <= py < vertex[1]))
                and target[0] < _f32(
                    _f32(poly[previous][0]-vertex[0])
                    * _f32(py-vertex[1])
                    / _f32(poly[previous][1]-vertex[1])
                    + vertex[0]
                )
            ):
                flag = not flag
            previous = index
        return flag

    if align(target, polygon[0], polygon[3]) > 0:
        u = _f32(-1.0)
    elif align(target, polygon[1], polygon[2]) > 0:
        u = _f32(1.0)
    else:
        u = _f32(0.0)
        lower = _f32(-1.0)
        upper = _f32(1.0)
        x5 = _f32((polygon[2][0]+polygon[3][0])/np.float32(2.0))
        y5 = _f32((polygon[2][1]+polygon[3][1])/np.float32(2.0))
        x6 = _f32((polygon[0][0]+polygon[1][0])/np.float32(2.0))
        y6 = _f32((polygon[0][1]+polygon[1][1])/np.float32(2.0))
        if inside(polygon):
            for _ in range(1000):
                if float(upper-lower) < 0.001:
                    break
                strip = (polygon[0], np.asarray((x6,y6),dtype=np.float32),
                         np.asarray((x5,y5),dtype=np.float32), polygon[3])
                if inside(strip):
                    upper = u
                    u = _f32((lower+u)/np.float32(2.0))
                else:
                    lower = u
                    u = _f32((upper+u)/np.float32(2.0))
                x6 = _f32(
                    _f32(polygon[0][0]*_f32(1.0-u))/np.float32(2.0)
                    + _f32(polygon[1][0]*_f32(1.0+u))/np.float32(2.0)
                )
                y6 = _f32(
                    _f32(polygon[0][1]*_f32(1.0-u))/np.float32(2.0)
                    + _f32(polygon[1][1]*_f32(1.0+u))/np.float32(2.0)
                )
                x5 = _f32(
                    _f32(polygon[2][0]*_f32(1.0+u))/np.float32(2.0)
                    + _f32(polygon[3][0]*_f32(1.0-u))/np.float32(2.0)
                )
                y5 = _f32(
                    _f32(polygon[2][1]*_f32(1.0+u))/np.float32(2.0)
                    + _f32(polygon[3][1]*_f32(1.0-u))/np.float32(2.0)
                )

    if align(target, polygon[0], polygon[1]) > 0:
        v = _f32(-1.0)
    elif align(target, polygon[3], polygon[2]) > 0:
        v = _f32(1.0)
    else:
        v = _f32(0.0)
        lower = _f32(-1.0)
        upper = _f32(1.0)
        x5 = _f32((polygon[2][0]+polygon[1][0])/np.float32(2.0))
        y5 = _f32((polygon[2][1]+polygon[1][1])/np.float32(2.0))
        x6 = _f32((polygon[0][0]+polygon[3][0])/np.float32(2.0))
        y6 = _f32((polygon[0][1]+polygon[3][1])/np.float32(2.0))
        if inside(polygon):
            for _ in range(1000):
                if float(upper-lower) < 0.001:
                    break
                strip = (polygon[0], polygon[1],
                         np.asarray((x5,y5),dtype=np.float32),
                         np.asarray((x6,y6),dtype=np.float32))
                if inside(strip):
                    upper = v
                    v = _f32((lower+v)/np.float32(2.0))
                else:
                    lower = v
                    v = _f32((upper+v)/np.float32(2.0))
                x6 = _f32(
                    _f32(polygon[0][0]*_f32(1.0-v))/np.float32(2.0)
                    + _f32(polygon[3][0]*_f32(1.0+v))/np.float32(2.0)
                )
                y6 = _f32(
                    _f32(polygon[0][1]*_f32(1.0-v))/np.float32(2.0)
                    + _f32(polygon[3][1]*_f32(1.0+v))/np.float32(2.0)
                )
                x5 = _f32(
                    _f32(polygon[1][0]*_f32(1.0-v))/np.float32(2.0)
                    + _f32(polygon[2][0]*_f32(1.0+v))/np.float32(2.0)
                )
                y5 = _f32(
                    _f32(polygon[1][1]*_f32(1.0-v))/np.float32(2.0)
                    + _f32(polygon[2][1]*_f32(1.0+v))/np.float32(2.0)
                )
    return u, v


def _inverse_bilinear_f32_python(
    vertices: Sequence[np.ndarray], point: np.ndarray
) -> tuple[np.float32, np.float32]:
    """Scalar reference for the float32 afference inverse.

    The desktop bisection is retained above as a literal reference, but its
    one-unit geometric edge tolerance depends on mutable application globals.
    On the supplied serialized model the converged intrinsic coordinates are
    reproduced more reliably by this float32 Newton solve.
    """
    vertices_f = tuple(np.asarray(vertex, dtype=np.float32) for vertex in vertices)
    point_f = np.asarray(point, dtype=np.float32)
    normal = _cross3_f32(vertices_f[1]-vertices_f[0], vertices_f[3]-vertices_f[0])
    drop = int(np.argmax(np.abs(normal)))
    keep0, keep1 = (1, 2) if drop == 0 else ((0, 2) if drop == 1 else (0, 1))
    target0, target1 = point_f[keep0], point_f[keep1]
    u = _f32(0.0)
    v = _f32(0.0)
    four = _f32(4.0)
    one = _f32(1.0)
    for _ in range(20):
        mapped = _bilinear_f32(vertices_f, u, v)
        du = np.asarray([
            _f32(
                _f32(
                    _f32(-vertices_f[0][i] * _f32(one-v))
                    + _f32(vertices_f[1][i] * _f32(one-v))
                )
                + _f32(
                    _f32(vertices_f[2][i] * _f32(one+v))
                    - _f32(vertices_f[3][i] * _f32(one+v))
                )
            ) / four
            for i in range(3)
        ], dtype=np.float32)
        dv = np.asarray([
            _f32(
                _f32(
                    _f32(-vertices_f[0][i] * _f32(one-u))
                    - _f32(vertices_f[1][i] * _f32(one+u))
                )
                + _f32(
                    _f32(vertices_f[2][i] * _f32(one+u))
                    + _f32(vertices_f[3][i] * _f32(one-u))
                )
            ) / four
            for i in range(3)
        ], dtype=np.float32)
        j00, j01 = du[keep0], dv[keep0]
        j10, j11 = du[keep1], dv[keep1]
        r0 = _f32(target0 - mapped[keep0])
        r1 = _f32(target1 - mapped[keep1])
        det = _f32(_f32(j00*j11) - _f32(j01*j10))
        if abs(float(det)) <= 1.0e-20:
            break
        step_u = _f32(_f32(_f32(r0*j11) - _f32(j01*r1)) / det)
        step_v = _f32(_f32(_f32(j00*r1) - _f32(r0*j10)) / det)
        u = _f32(u + step_u)
        v = _f32(v + step_v)
        if max(abs(float(step_u)), abs(float(step_v))) <= 1.0e-6:
            break
    return u, v


if njit is not None:
    @njit(cache=True, inline="always")
    def _bilinear_component_f32_nb(vertices, u, v, component):
        """One component of ``_bilinear_f32`` with identical reductions."""
        one = np.float32(1.0)
        four = np.float32(4.0)
        weights = np.empty(4, dtype=np.float32)
        weights[0] = np.float32(
            np.float32(np.float32(one - u) * np.float32(one - v)) / four
        )
        weights[1] = np.float32(
            np.float32(np.float32(one + u) * np.float32(one - v)) / four
        )
        weights[2] = np.float32(
            np.float32(np.float32(one + u) * np.float32(one + v)) / four
        )
        weights[3] = np.float32(
            np.float32(np.float32(one - u) * np.float32(one + v)) / four
        )
        value = np.float32(0.0)
        for index in range(4):
            value = np.float32(
                value + np.float32(vertices[index, component] * weights[index])
            )
        return value

    @njit(cache=True, nogil=True)
    def _inverse_bilinear_f32_nb(vertices, point):
        """Compiled equivalent of ``_inverse_bilinear_f32_python``."""
        edge10 = np.empty(3, dtype=np.float32)
        edge30 = np.empty(3, dtype=np.float32)
        for index in range(3):
            edge10[index] = np.float32(vertices[1, index] - vertices[0, index])
            edge30[index] = np.float32(vertices[3, index] - vertices[0, index])
        normal = np.empty(3, dtype=np.float32)
        normal[0] = np.float32(
            np.float32(edge10[1] * edge30[2])
            - np.float32(edge10[2] * edge30[1])
        )
        normal[1] = np.float32(
            np.float32(edge10[2] * edge30[0])
            - np.float32(edge10[0] * edge30[2])
        )
        normal[2] = np.float32(
            np.float32(edge10[0] * edge30[1])
            - np.float32(edge10[1] * edge30[0])
        )
        drop = 0
        if abs(normal[1]) > abs(normal[drop]):
            drop = 1
        if abs(normal[2]) > abs(normal[drop]):
            drop = 2
        if drop == 0:
            keep0, keep1 = 1, 2
        elif drop == 1:
            keep0, keep1 = 0, 2
        else:
            keep0, keep1 = 0, 1

        target0 = point[keep0]
        target1 = point[keep1]
        u = np.float32(0.0)
        v = np.float32(0.0)
        one = np.float32(1.0)
        four = np.float32(4.0)
        for _ in range(20):
            mapped0 = _bilinear_component_f32_nb(vertices, u, v, keep0)
            mapped1 = _bilinear_component_f32_nb(vertices, u, v, keep1)
            one_minus_v = np.float32(one - v)
            one_plus_v = np.float32(one + v)
            one_minus_u = np.float32(one - u)
            one_plus_u = np.float32(one + u)

            du0 = np.float32(
                np.float32(
                    np.float32(-vertices[0, keep0] * one_minus_v)
                    + np.float32(vertices[1, keep0] * one_minus_v)
                )
                + np.float32(
                    np.float32(vertices[2, keep0] * one_plus_v)
                    - np.float32(vertices[3, keep0] * one_plus_v)
                )
            ) / four
            du1 = np.float32(
                np.float32(
                    np.float32(-vertices[0, keep1] * one_minus_v)
                    + np.float32(vertices[1, keep1] * one_minus_v)
                )
                + np.float32(
                    np.float32(vertices[2, keep1] * one_plus_v)
                    - np.float32(vertices[3, keep1] * one_plus_v)
                )
            ) / four
            dv0 = np.float32(
                np.float32(
                    np.float32(-vertices[0, keep0] * one_minus_u)
                    - np.float32(vertices[1, keep0] * one_plus_u)
                )
                + np.float32(
                    np.float32(vertices[2, keep0] * one_plus_u)
                    + np.float32(vertices[3, keep0] * one_minus_u)
                )
            ) / four
            dv1 = np.float32(
                np.float32(
                    np.float32(-vertices[0, keep1] * one_minus_u)
                    - np.float32(vertices[1, keep1] * one_plus_u)
                )
                + np.float32(
                    np.float32(vertices[2, keep1] * one_plus_u)
                    + np.float32(vertices[3, keep1] * one_minus_u)
                )
            ) / four

            r0 = np.float32(target0 - mapped0)
            r1 = np.float32(target1 - mapped1)
            det = np.float32(
                np.float32(du0 * dv1) - np.float32(dv0 * du1)
            )
            if abs(det) <= 1.0e-20:
                break
            step_u = np.float32(
                np.float32(np.float32(r0 * dv1) - np.float32(dv0 * r1)) / det
            )
            step_v = np.float32(
                np.float32(np.float32(du0 * r1) - np.float32(r0 * du1)) / det
            )
            u = np.float32(u + step_u)
            v = np.float32(v + step_v)
            if max(abs(float(step_u)), abs(float(step_v))) <= 1.0e-6:
                break
        return u, v
else:  # pragma: no cover - exercised when Numba is unavailable
    _inverse_bilinear_f32_nb = None


def _inverse_bilinear_f32(
    vertices: Sequence[np.ndarray], point: np.ndarray
) -> tuple[np.float32, np.float32]:
    """Stable float32 inverse used by the afference compatibility path."""
    vertices_f = np.asarray(vertices, dtype=np.float32)
    point_f = np.asarray(point, dtype=np.float32)
    if _inverse_bilinear_f32_nb is None:
        return _inverse_bilinear_f32_python(vertices_f, point_f)
    u, v = _inverse_bilinear_f32_nb(vertices_f, point_f)
    return np.float32(u), np.float32(v)


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
