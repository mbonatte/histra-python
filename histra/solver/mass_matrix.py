"""C#-compatible mass-matrix assembly for HiStrA macro-elements.

The active C# ``Quad.ComputeLocalMassfromSelfWeight`` implementation always
integrates a consistent 7x7 macro-element mass matrix with a 6x6x6 Gauss rule.
Its ``diagonal``/``MassMatrixType`` argument is currently ignored; this module
preserves that observed behaviour for numerical parity.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any, Callable

import numpy as np
import scipy.sparse as sp

try:
    from numba import njit, prange
except Exception:  # pragma: no cover
    njit = None
    prange = range

# Original Operations.g and MasonryMaterial.w are System.Single.
GRAVITY_ACCELERATION = float(np.float32(980.6))
_GAUSS_COORDS, _GAUSS_WEIGHTS_1D = np.polynomial.legendre.leggauss(6)
_GAUSS_POINTS = np.asarray(
    [(a, b, c) for a in _GAUSS_COORDS for b in _GAUSS_COORDS for c in _GAUSS_COORDS],
    dtype=float,
)
_GAUSS_WEIGHTS = np.asarray(
    [wa * wb * wc for wa in _GAUSS_WEIGHTS_1D for wb in _GAUSS_WEIGHTS_1D for wc in _GAUSS_WEIGHTS_1D],
    dtype=float,
)


class MassMatrixError(RuntimeError):
    """Raised when a C#-compatible mass matrix cannot be assembled."""


@dataclass(frozen=True)
class MassMatrixAssembly:
    matrix: sp.csc_matrix
    requested_type: str
    effective_type: str
    quad_count: int


def _shape3(coords: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """C# ``FForma(0)`` trilinear-hexahedron shape functions and derivatives."""
    a = coords[:, 0]
    b = coords[:, 1]
    c = coords[:, 2]
    ap, am = 1.0 + a, 1.0 - a
    bp, bm = 1.0 + b, 1.0 - b
    cp, cm = 1.0 + c, 1.0 - c
    n = np.column_stack(
        (
            ap * bp * cp,
            ap * bm * cp,
            ap * bm * cm,
            ap * bp * cm,
            am * bp * cp,
            am * bm * cp,
            am * bm * cm,
            am * bp * cm,
        )
    ) / 8.0
    da = np.column_stack(
        (bp * cp, bm * cp, bm * cm, bp * cm, -bp * cp, -bm * cp, -bm * cm, -bp * cm)
    ) / 8.0
    db = np.column_stack(
        (ap * cp, -ap * cp, -ap * cm, ap * cm, am * cp, -am * cp, -am * cm, am * cm)
    ) / 8.0
    dc = np.column_stack(
        (ap * bp, ap * bm, -ap * bm, -ap * bp, am * bp, am * bm, -am * bm, -am * bp)
    ) / 8.0
    return n, da, db, dc


_N8, _D1, _D2, _D3 = _shape3(_GAUSS_POINTS)


def _map_hexahedron(
    coordinates: np.ndarray, natural_coordinate: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    n, da, db, dc = _shape3(np.asarray(natural_coordinate, dtype=float).reshape(1, 3))
    return n[0] @ coordinates, da[0] @ coordinates, db[0] @ coordinates, dc[0] @ coordinates


def _invert_hexahedron(target: np.ndarray, coordinates: np.ndarray) -> np.ndarray:
    """Newton inversion matching the role of C# ``FForma.Invert3D``."""
    natural = np.zeros(3, dtype=float)
    previous_error = float("inf")
    for _ in range(100):
        position, dx1, dx2, dx3 = _map_hexahedron(coordinates, natural)
        jacobian = np.column_stack((dx1, dx2, dx3))
        try:
            increment = np.linalg.solve(jacobian, target - position)
        except np.linalg.LinAlgError as exc:
            raise MassMatrixError("Degenerate Quad thickness volume while locating its centre.") from exc
        candidate = natural + increment
        error = float(np.abs(candidate - natural).sum())
        natural = candidate
        if error <= 1.0e-13:
            return natural
        if error >= previous_error:
            break
        previous_error = error
    return natural


def _b_matrices(quad: Any, natural: np.ndarray, positions: np.ndarray, node0: np.ndarray) -> np.ndarray:
    """Evaluate the C# local kinematic ``B`` matrix at one or many points."""
    natural = np.asarray(natural, dtype=float).reshape(-1, 3)
    positions = np.asarray(positions, dtype=float).reshape(-1, 3)
    result = np.zeros((natural.shape[0], 3, 4), dtype=float)
    offset = positions - node0
    result[:, 0, 1] = offset[:, 2]
    result[:, 1, 0] = -offset[:, 2]
    result[:, 2, 0] = offset[:, 1]
    result[:, 0, 2] = -offset[:, 1]
    result[:, 1, 2] = offset[:, 0]
    result[:, 2, 1] = -offset[:, 0]

    a = natural[:, 0]
    b = natural[:, 1]
    m2 = (1.0 - a) * (1.0 - b) / 4.0
    m3 = (1.0 + a) * (1.0 - b) / 4.0
    length4 = float(quad.length[3])
    sin4 = float(quad.sin[3])
    sin2 = float(quad.sin[1])
    sin3 = float(quad.sin[2])
    if abs(sin3) <= 1.0e-30:
        raise MassMatrixError(f"Quad {quad.key} has Sin3=0 and cannot form its mass matrix.")
    cos2 = float(quad.cos[1])
    sin1 = float(quad.sin[0])
    cos1 = float(quad.cos[0])
    first = (-length4 * sin4 * sin2 / sin3) * m2 + (-length4 * sin1) * m3
    second = (-length4 * sin4 * cos2 / sin3) * m2 + (length4 * cos1) * m3
    e1 = np.asarray(quad.reference_e1, dtype=np.float32).astype(float)
    e2 = np.asarray(quad.reference_e2, dtype=np.float32).astype(float)
    result[:, :, 3] = first[:, None] * e1 + second[:, None] * e2
    return result


if njit is not None:
    @njit(cache=True, inline="always")
    def _det3(m):
        return (
            m[0, 0] * (m[1, 1] * m[2, 2] - m[1, 2] * m[2, 1])
            - m[0, 1] * (m[1, 0] * m[2, 2] - m[1, 2] * m[2, 0])
            + m[0, 2] * (m[1, 0] * m[2, 1] - m[1, 1] * m[2, 0])
        )

    @njit(cache=True, inline="always")
    def _solve3(A, b, x):
        detA = _det3(A)
        if abs(detA) <= 1.0e-30:
            return False
        invA = 1.0 / detA
        m0 = np.empty((3, 3), dtype=np.float64)
        m0[0, 0] = b[0]; m0[0, 1] = A[0, 1]; m0[0, 2] = A[0, 2]
        m0[1, 0] = b[1]; m0[1, 1] = A[1, 1]; m0[1, 2] = A[1, 2]
        m0[2, 0] = b[2]; m0[2, 1] = A[2, 1]; m0[2, 2] = A[2, 2]
        x[0] = _det3(m0) * invA

        m1 = np.empty((3, 3), dtype=np.float64)
        m1[0, 0] = A[0, 0]; m1[0, 1] = b[0]; m1[0, 2] = A[0, 2]
        m1[1, 0] = A[1, 0]; m1[1, 1] = b[1]; m1[1, 2] = A[1, 2]
        m1[2, 0] = A[2, 0]; m1[2, 1] = b[2]; m1[2, 2] = A[2, 2]
        x[1] = _det3(m1) * invA

        m2 = np.empty((3, 3), dtype=np.float64)
        m2[0, 0] = A[0, 0]; m2[0, 1] = A[0, 1]; m2[0, 2] = b[0]
        m2[1, 0] = A[1, 0]; m2[1, 1] = A[1, 1]; m2[1, 2] = b[1]
        m2[2, 0] = A[2, 0]; m2[2, 1] = A[2, 1]; m2[2, 2] = b[2]
        x[2] = _det3(m2) * invA
        return True

    @njit(cache=True, inline="always")
    def _shape3_point(a, b, c, n, da, db, dc):
        ap = 1.0 + a; am = 1.0 - a
        bp = 1.0 + b; bm = 1.0 - b
        cp = 1.0 + c; cm = 1.0 - c

        n[0] = ap * bp * cp / 8.0
        n[1] = ap * bm * cp / 8.0
        n[2] = ap * bm * cm / 8.0
        n[3] = ap * bp * cm / 8.0
        n[4] = am * bp * cp / 8.0
        n[5] = am * bm * cp / 8.0
        n[6] = am * bm * cm / 8.0
        n[7] = am * bp * cm / 8.0

        da[0] = bp * cp / 8.0;  da[1] = bm * cp / 8.0;  da[2] = bm * cm / 8.0;  da[3] = bp * cm / 8.0
        da[4] = -bp * cp / 8.0; da[5] = -bm * cp / 8.0; da[6] = -bm * cm / 8.0; da[7] = -bp * cm / 8.0

        db[0] = ap * cp / 8.0;  db[1] = -ap * cp / 8.0; db[2] = -ap * cm / 8.0; db[3] = ap * cm / 8.0
        db[4] = am * cp / 8.0;  db[5] = -am * cp / 8.0; db[6] = -am * cm / 8.0; db[7] = am * cm / 8.0

        dc[0] = ap * bp / 8.0;  dc[1] = ap * bm / 8.0;  dc[2] = -ap * bm / 8.0; dc[3] = -ap * bp / 8.0
        dc[4] = am * bp / 8.0;  dc[5] = am * bm / 8.0;  dc[6] = -am * bm / 8.0; dc[7] = -am * bp / 8.0

    @njit(cache=True, nogil=True)
    def _invert_hexahedron_nb(target, volume_nodes, natural_out):
        natural_out[0] = 0.0
        natural_out[1] = 0.0
        natural_out[2] = 0.0

        n = np.empty(8, dtype=np.float64)
        da = np.empty(8, dtype=np.float64)
        db = np.empty(8, dtype=np.float64)
        dc = np.empty(8, dtype=np.float64)

        J = np.empty((3, 3), dtype=np.float64)
        diff = np.empty(3, dtype=np.float64)
        inc = np.empty(3, dtype=np.float64)

        prev_error = 1.0e30
        for _ in range(100):
            _shape3_point(natural_out[0], natural_out[1], natural_out[2], n, da, db, dc)
            pos_x = 0.0; pos_y = 0.0; pos_z = 0.0
            dx1_x = 0.0; dx1_y = 0.0; dx1_z = 0.0
            dx2_x = 0.0; dx2_y = 0.0; dx2_z = 0.0
            dx3_x = 0.0; dx3_y = 0.0; dx3_z = 0.0

            for k in range(8):
                vx = volume_nodes[k, 0]
                vy = volume_nodes[k, 1]
                vz = volume_nodes[k, 2]
                pos_x += n[k] * vx; pos_y += n[k] * vy; pos_z += n[k] * vz
                dx1_x += da[k] * vx; dx1_y += da[k] * vy; dx1_z += da[k] * vz
                dx2_x += db[k] * vx; dx2_y += db[k] * vy; dx2_z += db[k] * vz
                dx3_x += dc[k] * vx; dx3_y += dc[k] * vy; dx3_z += dc[k] * vz

            J[0, 0] = dx1_x; J[0, 1] = dx2_x; J[0, 2] = dx3_x
            J[1, 0] = dx1_y; J[1, 1] = dx2_y; J[1, 2] = dx3_y
            J[2, 0] = dx1_z; J[2, 1] = dx2_z; J[2, 2] = dx3_z

            diff[0] = target[0] - pos_x
            diff[1] = target[1] - pos_y
            diff[2] = target[2] - pos_z

            if not _solve3(J, diff, inc):
                break

            cand_x = natural_out[0] + inc[0]
            cand_y = natural_out[1] + inc[1]
            cand_z = natural_out[2] + inc[2]

            err = abs(cand_x - natural_out[0]) + abs(cand_y - natural_out[1]) + abs(cand_z - natural_out[2])
            natural_out[0] = cand_x
            natural_out[1] = cand_y
            natural_out[2] = cand_z

            if err <= 1.0e-13:
                break
            if err >= prev_error:
                break
            prev_error = err

    @njit(cache=True, inline="always")
    def _b_matrix_single(a, b, pos, node0, l4, s4, s2, s3, c2, s1, c1, e1, e2, out_b):
        off_x = pos[0] - node0[0]
        off_y = pos[1] - node0[1]
        off_z = pos[2] - node0[2]

        out_b[0, 0] = 0.0
        out_b[0, 1] = off_z
        out_b[0, 2] = -off_y

        out_b[1, 0] = -off_z
        out_b[1, 1] = 0.0
        out_b[1, 2] = off_x

        out_b[2, 0] = off_y
        out_b[2, 1] = -off_x
        out_b[2, 2] = 0.0

        m2 = (1.0 - a) * (1.0 - b) / 4.0
        m3 = (1.0 + a) * (1.0 - b) / 4.0
        first = (-l4 * s4 * s2 / s3) * m2 + (-l4 * s1) * m3
        second = (-l4 * s4 * c2 / s3) * m2 + (l4 * c1) * m3

        out_b[0, 3] = first * e1[0] + second * e2[0]
        out_b[1, 3] = first * e1[1] + second * e2[1]
        out_b[2, 3] = first * e1[2] + second * e2[2]

    @njit(cache=True, nogil=True)
    def _compute_quad_mass_kernel(
        volume_nodes, centre, node0,
        l4, s4, s2, s3, c2, s1, c1, e1, e2,
        density, gravity, applied_p,
        gauss_pts, gauss_w, n8, d1, d2, d3,
        out_mass
    ):
        nat_centre = np.empty(3, dtype=np.float64)
        _invert_hexahedron_nb(centre, volume_nodes, nat_centre)

        n_c = np.empty(8, dtype=np.float64)
        da_c = np.empty(8, dtype=np.float64)
        db_c = np.empty(8, dtype=np.float64)
        dc_c = np.empty(8, dtype=np.float64)
        _shape3_point(nat_centre[0], nat_centre[1], nat_centre[2], n_c, da_c, db_c, dc_c)

        pos_c = np.empty(3, dtype=np.float64)
        pos_c[0] = 0.0; pos_c[1] = 0.0; pos_c[2] = 0.0
        for k in range(8):
            pos_c[0] += n_c[k] * volume_nodes[k, 0]
            pos_c[1] += n_c[k] * volume_nodes[k, 1]
            pos_c[2] += n_c[k] * volume_nodes[k, 2]

        b_centre = np.empty((3, 4), dtype=np.float64)
        _b_matrix_single(nat_centre[0], nat_centre[1], pos_c, node0, l4, s4, s2, s3, c2, s1, c1, e1, e2, b_centre)

        for i in range(7):
            for j in range(7):
                out_mass[i, j] = 0.0

        b_g = np.empty((3, 4), dtype=np.float64)
        vel = np.empty((3, 7), dtype=np.float64)
        vel[0, 0] = 1.0; vel[0, 1] = 0.0; vel[0, 2] = 0.0
        vel[1, 0] = 0.0; vel[1, 1] = 1.0; vel[1, 2] = 0.0
        vel[2, 0] = 0.0; vel[2, 1] = 0.0; vel[2, 2] = 1.0

        for p in range(216):
            pos_x = 0.0; pos_y = 0.0; pos_z = 0.0
            dx1_x = 0.0; dx1_y = 0.0; dx1_z = 0.0
            dx2_x = 0.0; dx2_y = 0.0; dx2_z = 0.0
            dx3_x = 0.0; dx3_y = 0.0; dx3_z = 0.0

            for k in range(8):
                vx = volume_nodes[k, 0]
                vy = volume_nodes[k, 1]
                vz = volume_nodes[k, 2]
                pos_x += n8[p, k] * vx; pos_y += n8[p, k] * vy; pos_z += n8[p, k] * vz
                dx1_x += d1[p, k] * vx; dx1_y += d1[p, k] * vy; dx1_z += d1[p, k] * vz
                dx2_x += d2[p, k] * vx; dx2_y += d2[p, k] * vy; dx2_z += d2[p, k] * vz
                dx3_x += d3[p, k] * vx; dx3_y += d3[p, k] * vy; dx3_z += d3[p, k] * vz

            cx = dx1_y * dx2_z - dx1_z * dx2_y
            cy = dx1_z * dx2_x - dx1_x * dx2_z
            cz = dx1_x * dx2_y - dx1_y * dx2_x
            det = cx * dx3_x + cy * dx3_y + cz * dx3_z
            if det <= 0.0 or not np.isfinite(det):
                return False

            pos_arr = np.array([pos_x, pos_y, pos_z], dtype=np.float64)
            _b_matrix_single(gauss_pts[p, 0], gauss_pts[p, 1], pos_arr, node0, l4, s4, s2, s3, c2, s1, c1, e1, e2, b_g)

            for r in range(3):
                for c in range(4):
                    vel[r, 3 + c] = b_g[r, c] - b_centre[r, c]

            w_det = gauss_w[p] * det * density
            for i in range(7):
                for j in range(7):
                    v_dot = vel[0, i] * vel[0, j] + vel[1, i] * vel[1, j] + vel[2, i] * vel[2, j]
                    out_mass[i, j] += v_dot * w_det

        for i in range(7):
            out_mass[i, i] += abs(applied_p[i] / gravity)

        max_val = 0.0
        for i in range(7):
            for j in range(7):
                if abs(out_mass[i, j]) > max_val:
                    max_val = abs(out_mass[i, j])
        cutoff = max_val * 1.0e-15
        for i in range(7):
            for j in range(7):
                if abs(out_mass[i, j]) < cutoff:
                    out_mass[i, j] = 0.0
        return True

    @njit(cache=True, nogil=True, parallel=True)
    def _compute_all_quad_mass_nb(
        vol_nodes_all, centres_all, node0_all,
        params_all, axes_e1, axes_e2,
        density_all, gravity, applied_p_all,
        gauss_pts, gauss_w, n8, d1, d2, d3,
        out_mass_all, valid_all
    ):
        nq = len(centres_all)
        for q in prange(nq):
            ok = _compute_quad_mass_kernel(
                vol_nodes_all[q], centres_all[q], node0_all[q],
                params_all[q, 0], params_all[q, 1], params_all[q, 2], params_all[q, 3],
                params_all[q, 4], params_all[q, 5], params_all[q, 6],
                axes_e1[q], axes_e2[q],
                density_all[q], gravity, applied_p_all[q],
                gauss_pts, gauss_w, n8, d1, d2, d3,
                out_mass_all[q]
            )
            valid_all[q] = ok

    @njit(cache=True, nogil=True)
    def _assemble_mass_coo_nb(out_mass_all, dof_offsets, dof_indices, rows, cols, values):
        count = 0
        nq = len(out_mass_all)
        for q in range(nq):
            for i in range(7):
                start_i = dof_offsets[q, i]
                end_i = dof_offsets[q, i + 1]
                for j in range(7):
                    v = out_mass_all[q, i, j]
                    if v == 0.0:
                        continue
                    start_j = dof_offsets[q, j]
                    end_j = dof_offsets[q, j + 1]
                    for ai in range(start_i, end_i):
                        gi = dof_indices[ai]
                        for aj in range(start_j, end_j):
                            gj = dof_indices[aj]
                            rows[count] = gi
                            cols[count] = gj
                            values[count] = v
                            count += 1
        return count
else:
    _compute_quad_mass_kernel = None
    _compute_all_quad_mass_nb = None
    _assemble_mass_coo_nb = None


def compute_quad_local_mass(
    quad: Any,
    model: Any,
    *,
    gravity: float = GRAVITY_ACCELERATION,
) -> np.ndarray:
    """Return the active C# implementation's 7x7 Quad mass matrix."""
    if gravity <= 0.0 or not isfinite(gravity):
        raise ValueError("gravity must be a positive finite value.")
    try:
        nodes = [model.collections.nodes[int(key)].point for key in quad.node_keys]
    except KeyError as exc:
        raise MassMatrixError(f"Quad {quad.key} references missing Node {exc.args[0]}.") from exc
    try:
        material = model.collections.materials[int(quad.material_key)]
    except KeyError as exc:
        raise MassMatrixError(
            f"Quad {quad.key} references missing masonry material {quad.material_key}."
        ) from exc

    # Native Node.Point, Quad.Normal/Thickness and reference axes are Single
    # storage, promoted before the Point3d/Double mass integration arithmetic.
    mid_surface = np.asarray([(point.x, point.y, point.z) for point in nodes], dtype=np.float32).astype(float)
    normals = np.asarray([(point.x, point.y, point.z) for point in quad.normal], dtype=np.float32).astype(float)
    thickness = np.asarray(quad.thickness, dtype=np.float32).astype(float)
    if mid_surface.shape != (4, 3) or normals.shape != (4, 3) or thickness.shape != (4,):
        raise MassMatrixError(f"Quad {quad.key} has incomplete geometry for mass integration.")

    volume_nodes = np.vstack(
        (
            mid_surface + normals * thickness[:, None] / 2.0,
            mid_surface - normals * thickness[:, None] / 2.0,
        )
    )
    centre = np.asarray((quad.g.x, quad.g.y, quad.g.z), dtype=np.float32).astype(float)

    if _compute_quad_mass_kernel is not None:
        sin3 = float(quad.sin[2])
        if abs(sin3) <= 1.0e-30:
            raise MassMatrixError(f"Quad {quad.key} has Sin3=0 and cannot form its mass matrix.")
        applied = np.asarray(getattr(quad.status, "p", np.zeros(7)), dtype=float)
        if applied.shape[0] < 7:
            raise MassMatrixError(f"Quad {quad.key} has fewer than seven local load entries.")
        local = np.empty((7, 7), dtype=np.float64)
        density = float(np.float32(material.w)) / gravity
        valid_det = _compute_quad_mass_kernel(
            volume_nodes, centre, mid_surface[0],
            float(quad.length[3]), float(quad.sin[3]), float(quad.sin[1]), float(quad.sin[2]),
            float(quad.cos[1]), float(quad.sin[0]), float(quad.cos[0]),
            np.asarray(quad.reference_e1, dtype=np.float32).astype(float),
            np.asarray(quad.reference_e2, dtype=np.float32).astype(float),
            density, gravity, applied,
            _GAUSS_POINTS, _GAUSS_WEIGHTS, _N8, _D1, _D2, _D3,
            local,
        )
        if not valid_det:
            raise MassMatrixError(
                f"Quad {quad.key} has a non-positive 3D Jacobian during mass integration."
            )
        return local

    centre_natural = _invert_hexahedron(centre, volume_nodes)

    positions = _N8 @ volume_nodes
    dx1 = _D1 @ volume_nodes
    dx2 = _D2 @ volume_nodes
    dx3 = _D3 @ volume_nodes
    determinants = np.einsum("ij,ij->i", np.cross(dx1, dx2), dx3)
    if np.any(~np.isfinite(determinants)) or np.any(determinants <= 0.0):
        minimum = float(np.nanmin(determinants))
        raise MassMatrixError(
            f"Quad {quad.key} has a non-positive 3D Jacobian during mass integration "
            f"(minimum {minimum:.6g})."
        )

    b_gauss = _b_matrices(quad, _GAUSS_POINTS, positions, mid_surface[0])
    centre_position, _, _, _ = _map_hexahedron(volume_nodes, centre_natural)
    b_centre = _b_matrices(
        quad,
        centre_natural.reshape(1, 3),
        centre_position.reshape(1, 3),
        mid_surface[0],
    )[0]

    # Vtilde * N from the C# routine simplifies to [I, B(q)-B(centre)].
    velocity = np.zeros((_GAUSS_POINTS.shape[0], 3, 7), dtype=float)
    velocity[:, :, :3] = np.eye(3)
    velocity[:, :, 3:] = b_gauss - b_centre

    density = float(np.float32(material.w)) / gravity
    local = np.einsum(
        "pki,pkj,p->ij",
        velocity,
        velocity,
        determinants * _GAUSS_WEIGHTS,
    ) * density

    # The C# implementation treats existing local applied loads as point masses.
    applied = np.asarray(getattr(quad.status, "p", np.zeros(7)), dtype=float)
    if applied.shape[0] < 7:
        raise MassMatrixError(f"Quad {quad.key} has fewer than seven local load entries.")
    local[np.arange(7), np.arange(7)] += np.abs(applied[:7] / gravity)

    cutoff = float(np.max(local)) * 1.0e-15
    local[np.abs(local) < cutoff] = 0.0
    return local


def assemble_mass_matrix(
    model: Any,
    *,
    on_progress: Callable[[float], None] | None = None,
) -> MassMatrixAssembly:
    """Assemble the global C#-compatible mass matrix for supported elements.

    The Python domain currently implements Quad/Interface models. Interfaces
    carry no independent mass in the C# path. Vertex, Solid, Frame and Fiber
    masses are rejected if such future collections are populated rather than
    being silently discarded.
    """
    collections = getattr(model, "collections", None)
    if collections is None:
        raise MassMatrixError("Model.collections is not initialized.")
    n = int(getattr(model, "gdl", 0))
    if n <= 0:
        raise MassMatrixError("The model has no active global DOFs.")

    for collection_name in ("vertices", "solids", "frames", "fibers"):
        unsupported = getattr(collections, collection_name, None)
        if unsupported:
            raise NotImplementedError(
                f"Modal mass assembly for {collection_name} is not implemented in the Python port."
            )

    quads = tuple(collections.quads.values())
    if _compute_all_quad_mass_nb is not None and len(quads) > 0:
        nq = len(quads)
        vol_nodes_all = np.empty((nq, 8, 3), dtype=np.float64)
        centres_all = np.empty((nq, 3), dtype=np.float64)
        node0_all = np.empty((nq, 3), dtype=np.float64)
        params_all = np.empty((nq, 7), dtype=np.float64)
        axes_e1 = np.empty((nq, 3), dtype=np.float64)
        axes_e2 = np.empty((nq, 3), dtype=np.float64)
        density_all = np.empty(nq, dtype=np.float64)
        applied_p_all = np.empty((nq, 7), dtype=np.float64)
        out_mass_all = np.empty((nq, 7, 7), dtype=np.float64)
        valid_all = np.empty(nq, dtype=np.bool_)

        dof_offsets = np.empty((nq, 8), dtype=np.int64)
        dof_list: list[int] = []
        tot_dofs = 0

        for q, quad in enumerate(quads):
            if len(quad.aff) < 7:
                raise MassMatrixError(f"Quad {quad.key} has only {len(quad.aff)} afference rows.")
            try:
                nodes = [collections.nodes[int(key)].point for key in quad.node_keys]
            except KeyError as exc:
                raise MassMatrixError(f"Quad {quad.key} references missing Node {exc.args[0]}.") from exc
            try:
                material = collections.materials[int(quad.material_key)]
            except KeyError as exc:
                raise MassMatrixError(
                    f"Quad {quad.key} references missing masonry material {quad.material_key}."
                ) from exc
            mid_surface = np.asarray([(p.x, p.y, p.z) for p in nodes], dtype=np.float32).astype(float)
            normals = np.asarray([(p.x, p.y, p.z) for p in quad.normal], dtype=np.float32).astype(float)
            thickness = np.asarray(quad.thickness, dtype=np.float32).astype(float)
            if mid_surface.shape != (4, 3) or normals.shape != (4, 3) or thickness.shape != (4,):
                raise MassMatrixError(f"Quad {quad.key} has incomplete geometry for mass integration.")

            vol_nodes_all[q] = np.vstack((mid_surface + normals * thickness[:, None] / 2.0, mid_surface - normals * thickness[:, None] / 2.0))
            centres_all[q] = np.asarray((quad.g.x, quad.g.y, quad.g.z), dtype=np.float32).astype(float)
            node0_all[q] = mid_surface[0]
            sin3 = float(quad.sin[2])
            if abs(sin3) <= 1.0e-30:
                raise MassMatrixError(f"Quad {quad.key} has Sin3=0 and cannot form its mass matrix.")
            params_all[q, 0] = float(quad.length[3])
            params_all[q, 1] = float(quad.sin[3])
            params_all[q, 2] = float(quad.sin[1])
            params_all[q, 3] = sin3
            params_all[q, 4] = float(quad.cos[1])
            params_all[q, 5] = float(quad.sin[0])
            params_all[q, 6] = float(quad.cos[0])
            axes_e1[q] = np.asarray(quad.reference_e1, dtype=np.float32).astype(float)
            axes_e2[q] = np.asarray(quad.reference_e2, dtype=np.float32).astype(float)
            density_all[q] = float(np.float32(material.w)) / GRAVITY_ACCELERATION
            applied_p_all[q] = np.asarray(getattr(quad.status, "p", np.zeros(7)), dtype=float)

            dof_offsets[q, 0] = tot_dofs
            for local_i in range(7):
                for aff_i in quad.aff[local_i]:
                    gid = int(aff_i.gdl) - 1
                    if not 0 <= gid < n:
                        raise MassMatrixError(f"Quad {quad.key} has out-of-range mass DOF {aff_i.gdl}.")
                    dof_list.append(gid)
                    tot_dofs += 1
                dof_offsets[q, local_i + 1] = tot_dofs

        _compute_all_quad_mass_nb(
            vol_nodes_all, centres_all, node0_all,
            params_all, axes_e1, axes_e2,
            density_all, GRAVITY_ACCELERATION, applied_p_all,
            _GAUSS_POINTS, _GAUSS_WEIGHTS, _N8, _D1, _D2, _D3,
            out_mass_all, valid_all,
        )
        if not np.all(valid_all):
            bad_q = int(np.flatnonzero(~valid_all)[0])
            raise MassMatrixError(f"Quad {quads[bad_q].key} has a non-positive 3D Jacobian during mass integration.")

        dof_indices = np.asarray(dof_list, dtype=np.int64)
        max_entries = int(sum((dof_offsets[q, 7] - dof_offsets[q, 0]) ** 2 for q in range(nq)))
        rows = np.empty(max_entries, dtype=np.int64)
        cols = np.empty(max_entries, dtype=np.int64)
        values = np.empty(max_entries, dtype=np.float64)

        count = _assemble_mass_coo_nb(out_mass_all, dof_offsets, dof_indices, rows, cols, values)
        matrix = sp.coo_matrix((values[:count], (rows[:count], cols[:count])), shape=(n, n), dtype=float).tocsc()
        matrix.sum_duplicates()
        if on_progress is not None:
            on_progress(1.0)
        if matrix.nnz == 0:
            raise MassMatrixError("The assembled mass matrix is empty.")
        if np.any(~np.isfinite(matrix.data)):
            raise MassMatrixError("The assembled mass matrix contains NaN or infinite values.")

        requested = str(getattr(model, "mass_matrix_type", "Consistent"))
        return MassMatrixAssembly(
            matrix=matrix,
            requested_type=requested,
            effective_type="Consistent (C# Quad integration; HRX switch ignored)",
            quad_count=len(quads),
        )

    rows: list[int] = []
    cols: list[int] = []
    values: list[float] = []
    for index, quad in enumerate(quads, start=1):
        local = compute_quad_local_mass(quad, model)
        if len(quad.aff) < 7:
            raise MassMatrixError(f"Quad {quad.key} has only {len(quad.aff)} afference rows.")
        for local_i in range(7):
            for local_j in range(7):
                value = float(local[local_i, local_j])
                if value == 0.0:
                    continue
                # Deliberately do not multiply by afference alpha: C# AssembleM
                # scatters the local value unchanged to every afference pair.
                for aff_i in quad.aff[local_i]:
                    global_i = int(aff_i.gdl) - 1
                    if not 0 <= global_i < n:
                        raise MassMatrixError(
                            f"Quad {quad.key} has out-of-range mass DOF {aff_i.gdl}."
                        )
                    for aff_j in quad.aff[local_j]:
                        global_j = int(aff_j.gdl) - 1
                        if not 0 <= global_j < n:
                            raise MassMatrixError(
                                f"Quad {quad.key} has out-of-range mass DOF {aff_j.gdl}."
                            )
                        rows.append(global_i)
                        cols.append(global_j)
                        values.append(value)
        if on_progress is not None and quads:
            on_progress(index / len(quads))

    matrix = sp.coo_matrix((values, (rows, cols)), shape=(n, n), dtype=float).tocsc()
    matrix.sum_duplicates()
    if matrix.nnz == 0:
        raise MassMatrixError("The assembled mass matrix is empty.")
    if np.any(~np.isfinite(matrix.data)):
        raise MassMatrixError("The assembled mass matrix contains NaN or infinite values.")

    requested = str(getattr(model, "mass_matrix_type", "Consistent"))
    return MassMatrixAssembly(
        matrix=matrix,
        requested_type=requested,
        effective_type="Consistent (C# Quad integration; HRX switch ignored)",
        quad_count=len(quads),
    )


def build_translational_pseudovectors(model: Any, mass: sp.spmatrix) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Build C# ``ex/ey/ez``, ``M*e`` and total directional masses."""
    collections = getattr(model, "collections", None)
    if collections is None:
        raise MassMatrixError("Model.collections is not initialized.")
    n = int(model.gdl)
    directions = np.zeros((n, 3), dtype=float)
    for direction in range(3):
        for quad in collections.quads.values():
            if direction < len(quad.aff) and quad.aff[direction]:
                entry = quad.aff[direction][0]
                dof = int(entry.gdl) - 1
                if not 0 <= dof < n:
                    raise MassMatrixError(
                        f"Quad {quad.key} has out-of-range pseudovector DOF {entry.gdl}."
                    )
                # C# assignment semantics: later elements overwrite, not add.
                directions[dof, direction] = float(entry.alfa)
        # NodeC pseudovectors can be added when preprocessing parses their
        # afferences; current supported HRX Quad topology already contributes
        # every active translational DOF.
    mass_times_direction = np.asarray(mass @ directions, dtype=float)
    totals = np.einsum("ij,ij->j", directions, mass_times_direction)
    if np.any(totals <= 0.0) or np.any(~np.isfinite(totals)):
        raise MassMatrixError(
            "At least one translational pseudovector has zero or invalid total mass."
        )
    return directions, mass_times_direction, totals
