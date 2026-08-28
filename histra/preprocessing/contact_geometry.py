"""C#-compatible Quad contact detection and interface topology generation."""

from __future__ import annotations

import math
from typing import Sequence

import numpy as np

from histra.elements.interface import Interface
from histra.elements.quad import Quad
from histra.model.model import Model
from histra.preprocessing.errors import ModelPreparationError
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


# ``np.float32`` already performs the exact System.Single conversion required
# by the XNA-compatibility path. Bind it directly so the millions of scalar
# conversions performed while creating large interface models do not pay an
# extra Python function-frame call for a one-operation wrapper.
_f32 = np.float32


def _cross3_f32(first: Sequence[float], second: Sequence[float]) -> np.ndarray:
    """XNA-compatible three-component cross product.

    The desktop implementation constructs interface afferences with
    ``Microsoft.Xna.Framework.Vector3``.  Its arithmetic is single precision,
    even though the resulting coefficients are subsequently stored as
    ``double``.  NumPy otherwise promotes the loaded coordinates to float64
    and produces a measurably different prepared model.
    """
    a = np.asarray(first, dtype=np.float32)
    b = np.asarray(second, dtype=np.float32)
    return np.asarray(
        (
            _f32(_f32(a[1] * b[2]) - _f32(a[2] * b[1])),
            _f32(_f32(a[2] * b[0]) - _f32(a[0] * b[2])),
            _f32(_f32(a[0] * b[1]) - _f32(a[1] * b[0])),
        ),
        dtype=np.float32,
    )


def _dot3_f32(first: Sequence[float], second: Sequence[float]) -> np.float32:
    """XNA ``Vector3.Dot`` reduction order and precision."""
    a = np.asarray(first, dtype=np.float32)
    b = np.asarray(second, dtype=np.float32)
    return _f32(
        _f32(_f32(a[0] * b[0]) + _f32(a[1] * b[1]))
        + _f32(a[2] * b[2])
    )


def _norm3_f32(value: Sequence[float]) -> np.float32:
    """XNA ``Vector3.Length`` precision."""
    return _f32(np.sqrt(_dot3_f32(value, value), dtype=np.float32))


def _unit_f32(value: Sequence[float], *, label: str) -> np.ndarray:
    out = np.asarray(value, dtype=np.float32)
    norm = _norm3_f32(out)
    if float(norm) <= 1.0e-12:
        raise ModelPreparationError(f"Cannot normalize zero vector while building {label}.")
    return np.asarray(
        (_f32(out[0] / norm), _f32(out[1] / norm), _f32(out[2] / norm)),
        dtype=np.float32,
    )

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
    p1 = np.asarray(_v(model.collections.nodes[node_keys[0]].point), dtype=np.float32)
    p2 = np.asarray(_v(model.collections.nodes[node_keys[1]].point), dtype=np.float32)
    vertices_f = tuple(np.asarray(vertex, dtype=np.float32) for vertex in vertices)
    e1 = _unit_f32(p2 - p1, label=f"Interface {intf.key} e1")

    # C# Interface.Set identifies the polygon edge containing each interface
    # endpoint.  Those edges define both the local thickness and the reference
    # system.  Using the vector from the parent centroid to the interface works
    # only for centred contacts and tilts offset interfaces out of their plane.
    edge_matches: list[tuple[float, np.ndarray]] = []
    for endpoint in (p1, p2):
        match = _polygon_edge_at_point(vertices_f, endpoint)
        if match is None:
            raise ModelPreparationError(
                f"Interface {intf.key}: endpoint {endpoint.tolist()} is not aligned "
                "with an intersection-polygon edge."
            )
        edge_matches.append(match)

    if parent1_g is None:
        # Restraint VInt defines its local axes. Use the first edge and the
        # vector from endpoint 1 across the face.
        across = np.asarray(
            (vertices_f[3]-vertices_f[0]+vertices_f[2]-vertices_f[1])
            * _f32(0.5),
            dtype=np.float32,
        )
        e3 = _unit_f32(-across, label=f"Interface {intf.key} e3")
        e2 = _unit_f32(_cross3_f32(e3, e1), label=f"Interface {intf.key} e2")
        e3 = _unit_f32(_cross3_f32(e1, e2), label=f"Interface {intf.key} e3")
    else:
        if parent2_g is None:
            raise ModelPreparationError(
                f"Interface {intf.key}: the second Quad centroid is required."
            )
        thickness_direction1 = edge_matches[0][1].copy()
        thickness_direction2 = edge_matches[1][1].copy()
        if float(_dot3_f32(
            _cross3_f32(e1, thickness_direction1),
            _cross3_f32(e1, thickness_direction2),
        )) < 0.0:
            thickness_direction1 *= -1.0

        e2 = _unit_f32(
            _cross3_f32(e1, thickness_direction1),
            label=f"Interface {intf.key} e2",
        )
        e3 = _unit_f32(_cross3_f32(e1, e2), label=f"Interface {intf.key} e3")

        polygon_normal = _cross3_f32(
            vertices_f[1]-vertices_f[0], vertices_f[2]-vertices_f[0]
        )
        if float(np.linalg.norm(polygon_normal)) <= 1.0e-12:
            polygon_normal = _cross3_f32(
                vertices_f[1]-vertices_f[0], vertices_f[3]-vertices_f[0]
            )
        polygon_normal = _unit_f32(
            polygon_normal,
            label=f"Interface {intf.key} polygon normal",
        )
        parent2_direction = _unit_f32(
            vertices_f[0] - np.asarray(parent2_g, dtype=np.float32),
            label=f"Interface {intf.key} second-parent direction",
        )
        parent2_normal = _unit_f32(
            _dot3_f32(polygon_normal, parent2_direction) * polygon_normal,
            label=f"Interface {intf.key} second-parent normal",
        )
        if float(_dot3_f32(e2, parent2_normal)) > 0.0:
            e2 *= -1.0
            e3 *= -1.0

    origin = p1
    intf.reference_e1 = tuple(float(x) for x in e1)
    intf.reference_e2 = tuple(float(x) for x in e2)
    intf.reference_e3 = tuple(float(x) for x in e3)
    intf.reference_origin = _p(origin)
    intf.vint3d = [_p(v) for v in vertices_f]
    intf.vint2d = [
        Point(
            float(_dot3_f32(v - origin, e1)),
            float(_dot3_f32(v - origin, e3)),
            0.0,
        )
        for v in vertices_f
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


def _convex_quad_overlap_prefilter_batch(
    first: np.ndarray, second: np.ndarray, normals: np.ndarray,
) -> np.ndarray:
    """Conservatively reject separated coplanar convex quads in bulk.

    The broad phase intentionally uses axis-aligned boxes, so many coplanar
    face pairs reach the Python Sutherland-Hodgman narrow phase even though
    their polygons are clearly separated.  For convex quads, the separating
    axis theorem provides a numerical prefilter using the four edge normals
    from each polygon.

    This function is *not* an alternate intersection implementation: surviving
    pairs still go through ``_coplanar_quad_intersection_prechecked``.  The
    separation tolerance is twice the clipping tolerance so borderline/touching
    contacts are deliberately retained for the authoritative scalar path.
    """
    first = np.asarray(first, dtype=np.float64)
    second = np.asarray(second, dtype=np.float64)
    normals = np.asarray(normals, dtype=np.float64)
    if first.shape != second.shape or first.ndim != 3 or first.shape[1:] != (4, 3):
        raise ValueError(
            f"Expected matching (n, 4, 3) quad batches; got "
            f"{first.shape} and {second.shape}"
        )
    if normals.shape != (first.shape[0], 3):
        raise ValueError(
            f"Expected normals shape {(first.shape[0], 3)}; got {normals.shape}"
        )
    if first.shape[0] == 0:
        return np.empty(0, dtype=np.bool_)

    first_edges = np.roll(first, -1, axis=1) - first
    second_edges = np.roll(second, -1, axis=1) - second
    axes = np.concatenate(
        (
            np.cross(normals[:, None, :], first_edges),
            np.cross(normals[:, None, :], second_edges),
        ),
        axis=1,
    )
    axis_norm2 = np.sum(axes * axes, axis=2)

    first_projection = np.einsum(
        "nvd,nad->nav", first, axes, optimize=False
    )
    second_projection = np.einsum(
        "nvd,nad->nav", second, axes, optimize=False
    )
    # Use a *physical-distance* margin twice the clipping tolerance. The SAT
    # axes have magnitude equal to the source edge length, hence the projection
    # tolerance must be scaled by |axis|. This is deliberately more conservative
    # than the scalar clipping half-space tolerance for long edges.
    tolerance = (
        2.0 * _CONTACT_DISTANCE_TOLERANCE * np.sqrt(axis_norm2)
    )
    separated = (
        (
            np.max(first_projection, axis=2)
            < np.min(second_projection, axis=2) - tolerance
        )
        | (
            np.max(second_projection, axis=2)
            < np.min(first_projection, axis=2) - tolerance
        )
    ) & (axis_norm2 > 1.0e-24)
    return ~np.any(separated, axis=1)


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
            direction = _unit_f32(
                np.asarray(start, dtype=np.float32)-np.asarray(end, dtype=np.float32),
                label="Interface thickness direction",
            )
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
        candidate = candidate[coplanar]
        face1 = face1[coplanar]
        face2 = face2[coplanar]
        normals1 = normals1[coplanar]
        if candidate.size:
            first_faces = faces[first[candidate], face1]
            second_faces = faces[second[candidate], face2]
            overlap = _convex_quad_overlap_prefilter_batch(
                first_faces, second_faces, normals1
            )
            candidate = candidate[overlap]
            face1 = face1[overlap]
            face2 = face2[overlap]
        surface_candidates.extend(zip(
            first[candidate].tolist(), face1.tolist(),
            second[candidate].tolist(), face2.tolist(),
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
