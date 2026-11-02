"""Pure polygon clipping and area calculation utilities for contact preprocessing.

Extracted from contact_geometry to isolate 2D/3D computational geometry operations
(Sutherland-Hodgman polygon clipping, Newell polygon area reduction) from mesh
topology generation.
"""

from __future__ import annotations

import math
from typing import Sequence

import numpy as np

try:
    from numba import njit
except Exception:
    njit = None

_CONTACT_DISTANCE_TOLERANCE = 2.0e-4


if njit is not None:
    @njit(cache=True, nogil=True)
    def _clip_convex_quad_2d_kernel(subject_xy, clipper_xy, out_buf):
        in_buf = np.empty((16, 2), dtype=np.float64)
        tmp_buf = np.empty((16, 2), dtype=np.float64)

        n_in = 4
        for i in range(4):
            in_buf[i, 0] = subject_xy[i, 0]
            in_buf[i, 1] = subject_xy[i, 1]

        clip = np.empty((4, 2), dtype=np.float64)
        c0x, c0y = clipper_xy[0, 0], clipper_xy[0, 1]
        c1x, c1y = clipper_xy[1, 0], clipper_xy[1, 1]
        c2x, c2y = clipper_xy[2, 0], clipper_xy[2, 1]
        c3x, c3y = clipper_xy[3, 0], clipper_xy[3, 1]

        area2 = (c0x * c1y - c0y * c1x) + (c1x * c2y - c1y * c2x) + (c2x * c3y - c2y * c3x) + (c3x * c0y - c3y * c0x)
        if area2 < 0.0:
            clip[0, 0] = c3x; clip[0, 1] = c3y
            clip[1, 0] = c2x; clip[1, 1] = c2y
            clip[2, 0] = c1x; clip[2, 1] = c1y
            clip[3, 0] = c0x; clip[3, 1] = c0y
        else:
            for i in range(4):
                clip[i, 0] = clipper_xy[i, 0]
                clip[i, 1] = clipper_xy[i, 1]

        for i in range(4):
            cx = clip[i, 0]
            cy = clip[i, 1]
            next_i = (i + 1) % 4
            edx = clip[next_i, 0] - cx
            edy = clip[next_i, 1] - cy

            if n_in == 0:
                break

            n_out = 0
            start_x = in_buf[n_in - 1, 0]
            start_y = in_buf[n_in - 1, 1]
            start_inside = (edx * (start_y - cy) - edy * (start_x - cx)) >= -2.0e-4

            for j in range(n_in):
                end_x = in_buf[j, 0]
                end_y = in_buf[j, 1]
                end_inside = (edx * (end_y - cy) - edy * (end_x - cx)) >= -2.0e-4

                if end_inside:
                    if not start_inside:
                        dx = end_x - start_x
                        dy = end_y - start_y
                        denom = dx * edy - dy * edx
                        if abs(denom) <= 1.0e-15:
                            tmp_buf[n_out, 0] = 0.5 * (start_x + end_x)
                            tmp_buf[n_out, 1] = 0.5 * (start_y + end_y)
                        else:
                            t = ((cx - start_x) * edy - (cy - start_y) * edx) / denom
                            tmp_buf[n_out, 0] = start_x + t * dx
                            tmp_buf[n_out, 1] = start_y + t * dy
                        n_out += 1
                    tmp_buf[n_out, 0] = end_x
                    tmp_buf[n_out, 1] = end_y
                    n_out += 1
                elif start_inside:
                    dx = end_x - start_x
                    dy = end_y - start_y
                    denom = dx * edy - dy * edx
                    if abs(denom) <= 1.0e-15:
                        tmp_buf[n_out, 0] = 0.5 * (start_x + end_x)
                        tmp_buf[n_out, 1] = 0.5 * (start_y + end_y)
                    else:
                        t = ((cx - start_x) * edy - (cy - start_y) * edx) / denom
                        tmp_buf[n_out, 0] = start_x + t * dx
                        tmp_buf[n_out, 1] = start_y + t * dy
                    n_out += 1

                start_x = end_x
                start_y = end_y
                start_inside = end_inside

            n_in = n_out
            for k in range(n_out):
                in_buf[k, 0] = tmp_buf[k, 0]
                in_buf[k, 1] = tmp_buf[k, 1]

        # 1. Deduplication
        n_dedup = 0
        dedup = np.empty((16, 2), dtype=np.float64)
        for k in range(n_in):
            px = in_buf[k, 0]
            py = in_buf[k, 1]
            if n_dedup == 0:
                dedup[0, 0] = px
                dedup[0, 1] = py
                n_dedup = 1
            else:
                d2 = (px - dedup[n_dedup - 1, 0]) ** 2 + (py - dedup[n_dedup - 1, 1]) ** 2
                if d2 > 1.0e-14:
                    dedup[n_dedup, 0] = px
                    dedup[n_dedup, 1] = py
                    n_dedup += 1

        if n_dedup > 1:
            d2 = (dedup[0, 0] - dedup[n_dedup - 1, 0]) ** 2 + (dedup[0, 1] - dedup[n_dedup - 1, 1]) ** 2
            if d2 <= 1.0e-14:
                n_dedup -= 1

        # 2. Collinear removal
        cleaned = np.empty((16, 2), dtype=np.float64)
        changed = True
        while changed and n_dedup > 3:
            changed = False
            n_cleaned = 0
            for idx in range(n_dedup):
                prev_idx = n_dedup - 1 if idx == 0 else idx - 1
                next_idx = 0 if idx == n_dedup - 1 else idx + 1

                ax = dedup[prev_idx, 0]; ay = dedup[prev_idx, 1]
                bx = dedup[idx, 0];      by = dedup[idx, 1]
                cx = dedup[next_idx, 0]; cy = dedup[next_idx, 1]

                cross = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)
                if abs(cross) <= 1.0e-8:
                    changed = True
                else:
                    cleaned[n_cleaned, 0] = bx
                    cleaned[n_cleaned, 1] = by
                    n_cleaned += 1

            if n_cleaned == 0:
                break
            n_dedup = n_cleaned
            for k in range(n_cleaned):
                dedup[k, 0] = cleaned[k, 0]
                dedup[k, 1] = cleaned[k, 1]

        for k in range(n_dedup):
            out_buf[k, 0] = dedup[k, 0]
            out_buf[k, 1] = dedup[k, 1]
        return n_dedup
else:
    _clip_convex_quad_2d_kernel = None


def _cross_2d(a: Sequence[float], b: Sequence[float], c: Sequence[float]) -> float:
    return float((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))


def _polygon_area_2d(vertices: Sequence[Sequence[float]]) -> float:
    return 0.5 * sum(
        float(a[0]) * float(b[1]) - float(a[1]) * float(b[0])
        for a, b in zip(vertices, (*vertices[1:], vertices[0]))
    )


def _polygon_area_3d(points: Sequence[np.ndarray]) -> float:
    """Return a small polygon's area using Newell's exact reduction order."""
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


def _line_intersection_2d(
    start: Sequence[float],
    end: Sequence[float],
    clip_start: Sequence[float],
    clip_end: Sequence[float],
) -> tuple[float, float]:
    dx, dy = float(end[0] - start[0]), float(end[1] - start[1])
    cx, cy = float(clip_end[0] - clip_start[0]), float(clip_end[1] - clip_start[1])
    denominator = dx * cy - dy * cx
    if abs(denominator) <= 1.0e-15:
        return (
            0.5 * (float(start[0]) + float(end[0])),
            0.5 * (float(start[1]) + float(end[1])),
        )
    t = (
        (float(clip_start[0]) - float(start[0])) * cy
        - (float(clip_start[1]) - float(start[1])) * cx
    ) / denominator
    return (float(start[0]) + t * dx, float(start[1]) + t * dy)


def _clean_clipped_polygon(
    vertices: list[tuple[float, float]],
) -> list[tuple[float, float]]:
    deduplicated: list[tuple[float, float]] = []
    for point in vertices:
        if not deduplicated or (
            (point[0] - deduplicated[-1][0]) ** 2
            + (point[1] - deduplicated[-1][1]) ** 2
        ) > 1.0e-14:
            deduplicated.append(point)
    if len(deduplicated) > 1 and (
        (deduplicated[0][0] - deduplicated[-1][0]) ** 2
        + (deduplicated[0][1] - deduplicated[-1][1]) ** 2
    ) <= 1.0e-14:
        deduplicated.pop()

    changed = True
    while changed and len(deduplicated) > 3:
        changed = False
        cleaned: list[tuple[float, float]] = []
        count = len(deduplicated)
        for index, point in enumerate(deduplicated):
            if (
                abs(
                    _cross_2d(
                        deduplicated[index - 1],
                        point,
                        deduplicated[(index + 1) % count],
                    )
                )
                <= 1.0e-8
            ):
                changed = True
            else:
                cleaned.append(point)
        if not cleaned:
            break
        deduplicated = cleaned
    return deduplicated


def _clip_convex_quad_2d(
    subject: list[tuple[float, float]],
    clipper: list[tuple[float, float]],
) -> list[tuple[float, float]]:
    """Sutherland-Hodgman clipping while preserving parent-1 vertex order."""
    if _clip_convex_quad_2d_kernel is not None and len(subject) == 4 and len(clipper) == 4:
        sub_arr = np.asarray(subject, dtype=np.float64)
        clp_arr = np.asarray(clipper, dtype=np.float64)
        out_buf = np.empty((16, 2), dtype=np.float64)
        n = _clip_convex_quad_2d_kernel(sub_arr, clp_arr, out_buf)
        return [(float(out_buf[i, 0]), float(out_buf[i, 1])) for i in range(n)]

    clip = list(clipper)
    # Fast 4-vertex polygon orientation check
    if len(clip) == 4:
        c0, c1, c2, c3 = clip[0], clip[1], clip[2], clip[3]
        if (
            (c0[0] * c1[1] - c0[1] * c1[0])
            + (c1[0] * c2[1] - c1[1] * c2[0])
            + (c2[0] * c3[1] - c2[1] * c3[0])
            + (c3[0] * c0[1] - c3[1] * c0[0])
        ) < 0.0:
            clip = [c3, c2, c1, c0]
    elif _polygon_area_2d(clip) < 0.0:
        clip.reverse()

    output = list(subject)
    n_clip = len(clip)
    for i in range(n_clip):
        clip_start = clip[i]
        clip_end = clip[(i + 1) % n_clip]
        cx, cy = clip_start[0], clip_start[1]
        edx = clip_end[0] - cx
        edy = clip_end[1] - cy

        input_vertices = output
        output = []
        if not input_vertices:
            break
        start = input_vertices[-1]
        start_inside = (
            edx * (start[1] - cy) - edy * (start[0] - cx)
        ) >= -_CONTACT_DISTANCE_TOLERANCE
        for end in input_vertices:
            end_inside = (
                edx * (end[1] - cy) - edy * (end[0] - cx)
            ) >= -_CONTACT_DISTANCE_TOLERANCE
            if end_inside:
                if not start_inside:
                    dx = end[0] - start[0]
                    dy = end[1] - start[1]
                    denom = dx * edy - dy * edx
                    if abs(denom) <= 1.0e-15:
                        output.append(
                            (0.5 * (start[0] + end[0]), 0.5 * (start[1] + end[1]))
                        )
                    else:
                        t = ((cx - start[0]) * edy - (cy - start[1]) * edx) / denom
                        output.append((start[0] + t * dx, start[1] + t * dy))
                output.append(end)
            elif start_inside:
                dx = end[0] - start[0]
                dy = end[1] - start[1]
                denom = dx * edy - dy * edx
                if abs(denom) <= 1.0e-15:
                    output.append(
                        (0.5 * (start[0] + end[0]), 0.5 * (start[1] + end[1]))
                    )
                else:
                    t = ((cx - start[0]) * edy - (cy - start[1]) * edx) / denom
                    output.append((start[0] + t * dx, start[1] + t * dy))
            start, start_inside = end, end_inside
    return _clean_clipped_polygon(output)
