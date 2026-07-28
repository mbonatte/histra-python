from __future__ import annotations
from dataclasses import dataclass, field
from math import sqrt

import numpy as np
from typing import Dict, List, Tuple, Optional

try:
    from numba import njit
except Exception:  # pragma: no cover
    njit = None
from histra.types.point import Point
from histra.types.afference_entry import AfferenceEntry
from histra.springs.base import Spring
from histra.elements.quad_state import QuadState


if njit is not None:
    @njit(cache=True, nogil=True)
    def _quad_yield_search_kernel(
        k, E, G, Fyt, Fyc, dalfa,
        L0, L1, L3, cos0, cos1, sin0, sin1, sin2, sin3,
    ):
        nu = E / (2.0 * G) - 1.0
        lam = E * nu / (2.0 * (1.0 + 2.0 * nu))
        x0, x1 = -L0/2.0, L0/2.0
        x2, x3 = L0/2.0-L1*cos1, -L0/2.0+L3*cos0
        y0, y1, y2, y3 = 0.0, 0.0, L1*sin1, L3*sin0
        if abs(sin2) <= 1.0e-30:
            return 0.0, 0.0
        w0 = -L3*sin3*sin1/sin2
        w1 = -L3*sin3*cos1/sin2
        w2 = -L3*sin0
        w3 = -L3*cos0
        max_principal = 0.0
        min_principal = 0.0
        result0 = 0.0
        result1 = 0.0
        n = 100
        for pass_index in range(2):
            direction = 1.0 if pass_index == 0 else -1.0
            pass_min = 0.0
            pass_max = 0.0
            for row in range(1, n+1):
                eta = -1.0 + 2.0/n*(row-1.0) + 1.0/n
                dxi0 = -(1.0-eta)/4.0
                dxi1 = (1.0-eta)/4.0
                dxi2 = (1.0+eta)/4.0
                dxi3 = -(1.0+eta)/4.0
                for col in range(1, n+1):
                    xi = -1.0 + 2.0/n*(col-1.0) + 1.0/n
                    deta0 = -(1.0-xi)/4.0
                    deta1 = -(1.0+xi)/4.0
                    deta2 = (1.0+xi)/4.0
                    deta3 = (1.0-xi)/4.0
                    j11=x0*dxi0+x1*dxi1+x2*dxi2+x3*dxi3
                    j12=x0*deta0+x1*deta1+x2*deta2+x3*deta3
                    j21=y0*dxi0+y1*dxi1+y2*dxi2+y3*dxi3
                    j22=y0*deta0+y1*deta1+y2*deta2+y3*deta3
                    det=j11*j22-j12*j21
                    if abs(det)<=1.0e-30:
                        continue
                    inv11=j22/det; inv12=-j21/det; inv21=-j12/det; inv22=j11/det
                    b1x=inv11*(1.0+eta)/4.0+inv12*(1.0+xi)/4.0
                    b2x=-inv11*(1.0+eta)/4.0+inv12*(1.0-xi)/4.0
                    b1y=inv21*(1.0+eta)/4.0+inv22*(1.0+xi)/4.0
                    b2y=-inv21*(1.0+eta)/4.0+inv22*(1.0-xi)/4.0
                    eps_x=direction*(w0*b1x+w2*b2x)
                    eps_y=direction*(w1*b1y+w3*b2y)
                    gamma=direction*(w0*b1y+w1*b1x+w2*b2y+w3*b2x)
                    sx=lam*(eps_x+eps_y)+2.0*G*eps_x
                    sy=lam*(eps_x+eps_y)+2.0*G*eps_y
                    tau=G*gamma
                    avg=(sx+sy)/2.0
                    radius=sqrt(((sx-sy)/2.0)**2+tau*tau)
                    pmax=avg+radius; pmin=avg-radius
                    if pmin<pass_min: pass_min=pmin
                    if pmax>pass_max: pass_max=pmax
            if pass_min<min_principal: min_principal=pass_min
            if pass_max>max_principal: max_principal=pass_max
            value=0.0
            if max_principal != 0.0 and min_principal != 0.0:
                scale=direction*min(abs(Fyt/max_principal),abs(Fyc/min_principal))
                value=k*dalfa*scale
            if pass_index==0: result0=value
            else: result1=value
        return result0, result1
else:
    _quad_yield_search_kernel = None


@dataclass
class Quad:
    key: int = 0
    node_keys: List[int] = field(default_factory=lambda: [0, 0, 0, 0])
    length: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0])
    sin: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0])
    cos: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0])
    diago: List[float] = field(default_factory=lambda: [0.0, 0.0])
    thickness: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0])
    normal: List[Point] = field(default_factory=lambda: [Point(), Point(), Point(), Point()])
    g: Point = field(default_factory=Point)
    material_key: int = 0
    spring: Spring | None = None

    @property
    def springs(self) -> List[Spring]:
        return [self.spring] if self.spring else []

    @springs.setter
    def springs(self, val: List[Spring]) -> None:
        self.spring = val[0] if val else None
    # 7 Afference matrices (each is a list of (gdl, alfa) entries)
    aff: List[List[AfferenceEntry]] = field(default_factory=lambda: [[] for _ in range(7)])
    interface_keys: List[List[int]] = field(default_factory=lambda: [[] for _ in range(6)])
    # Reference system
    reference_e1: Tuple[float, float, float] = (1.0, 0.0, 0.0)
    reference_e2: Tuple[float, float, float] = (0.0, 1.0, 0.0)
    reference_e3: Tuple[float, float, float] = (0.0, 0.0, 1.0)
    reference_origin: Point = field(default_factory=Point)
    status: QuadState = field(default_factory=QuadState)
    name: str = ""
    extra: Dict[str, str] = field(default_factory=dict)
    parent_key: int = 0
    parent_type: str = ""
    material_key: int = 0
    layer_key: int = 0
    master_element_key: int = 0
    master_element_type: str = ""
    sigma_initial: float = 0.0
    _perf_volume: float | None = field(default=None, init=False, repr=False, compare=False)
    _perf_aff_pairs: tuple[tuple[tuple[int, float], ...], ...] | None = field(default=None, init=False, repr=False, compare=False)
    _perf_dn_edges: tuple[tuple[tuple[object, bool], ...], ...] | None = field(default=None, init=False, repr=False, compare=False)
    _perf_dn_areas: tuple[float, ...] | None = field(default=None, init=False, repr=False, compare=False)

    def compute_static_load_internal(self, node_coords: List[Point], nodal_forces: List[Tuple[float, float, float]]) -> List[float]:
        """Port C# ``Quad.ComputeStaticLoadInternal`` for area loads.

        The original implementation stores geometry, shape functions, force
        interpolation and Jacobians in ``float``/XNA ``Vector3`` values, then
        adds each Gauss-point contribution to a ``double[7]`` result.  Keeping
        those single-precision operation boundaries is necessary for numerical
        path compatibility with its work-based nonlinear convergence test.
        """
        f32 = np.float32

        out = np.zeros(7, dtype=np.float64)
        gp = f32(f32(np.sqrt(3.0)) / f32(3.0))
        gauss = (gp, f32(-gp))

        g = np.asarray((self.g.x, self.g.y, self.g.z), dtype=np.float32)
        e1 = np.asarray(self.reference_e1, dtype=np.float32)
        e2 = np.asarray(self.reference_e2, dtype=np.float32)
        transform = np.zeros((4, 3, 7), dtype=np.float32)

        for i, node in enumerate(node_coords):
            xyz = np.asarray((node.x, node.y, node.z), dtype=np.float32)
            dx, dy, dz = xyz - g
            transform[i, 0, 0] = f32(1.0)
            transform[i, 1, 1] = f32(1.0)
            transform[i, 2, 2] = f32(1.0)
            transform[i, 0, 4] = dz
            transform[i, 0, 5] = f32(-dy)
            transform[i, 1, 3] = f32(-dz)
            transform[i, 1, 5] = dx
            transform[i, 2, 3] = dy
            transform[i, 2, 4] = f32(-dx)

        # C# evaluates these expressions in double precision and explicitly
        # converts the completed warping coefficient to Single.
        for component in range(3):
            transform[2, component, 6] = f32(
                -self.length[3]
                * self.sin[3]
                / self.sin[2]
                * (
                    self.sin[1] * float(e1[component])
                    + self.cos[1] * float(e2[component])
                )
            )
            transform[3, component, 6] = f32(
                -self.length[3]
                * (
                    self.sin[0] * float(e1[component])
                    - self.cos[0] * float(e2[component])
                )
            )

        length0 = f32(self.length[0])
        length1 = f32(self.length[1])
        length3 = f32(self.length[3])
        cos0 = f32(self.cos[0])
        cos1 = f32(self.cos[1])
        sin0 = f32(self.sin[0])
        sin1 = f32(self.sin[1])
        local = np.zeros((4, 2), dtype=np.float32)
        local[0] = (f32(f32(-length0) / f32(2.0)), f32(0.0))
        local[1] = (f32(length0 / f32(2.0)), f32(0.0))
        local[2] = (
            f32(f32(length0 / f32(2.0)) - f32(length1 * cos1)),
            f32(length1 * sin1),
        )
        local[3] = (
            f32(f32(-length0) / f32(2.0) + f32(length3 * cos0)),
            f32(length3 * sin0),
        )
        forces = np.asarray(nodal_forces, dtype=np.float32)

        def sum4(values: List[np.float32]) -> np.float32:
            # C#'s source expression is left associative and every operand is
            # Single; spell that out rather than allowing a NumPy reduction.
            return f32(f32(f32(values[0] + values[1]) + values[2]) + values[3])

        one = f32(1.0)
        four = f32(4.0)
        for xi in gauss:
            for eta in gauss:
                shape = np.asarray(
                    (
                        f32(f32(one - xi) * f32(one - eta) / four),
                        f32(f32(one + xi) * f32(one - eta) / four),
                        f32(f32(one + xi) * f32(one + eta) / four),
                        f32(f32(one - xi) * f32(one + eta) / four),
                    ),
                    dtype=np.float32,
                )
                dxi = np.asarray(
                    (
                        f32(-f32(one - eta) / four),
                        f32(f32(one - eta) / four),
                        f32(f32(one + eta) / four),
                        f32(-f32(one + eta) / four),
                    ),
                    dtype=np.float32,
                )
                deta = np.asarray(
                    (
                        f32(-f32(one - xi) / four),
                        f32(-f32(one + xi) / four),
                        f32(f32(one + xi) / four),
                        f32(f32(one - xi) / four),
                    ),
                    dtype=np.float32,
                )

                j11 = sum4([f32(local[i, 0] * dxi[i]) for i in range(4)])
                j12 = sum4([f32(local[i, 0] * deta[i]) for i in range(4)])
                j21 = sum4([f32(local[i, 1] * dxi[i]) for i in range(4)])
                j22 = sum4([f32(local[i, 1] * deta[i]) for i in range(4)])
                det_j = f32(f32(j11 * j22) - f32(j12 * j21))

                force_gp = np.zeros(3, dtype=np.float32)
                for component in range(3):
                    force_gp[component] = sum4(
                        [f32(shape[i] * forces[i, component]) for i in range(4)]
                    )

                transform_gp = np.zeros((3, 7), dtype=np.float32)
                for row in range(3):
                    for column in range(7):
                        transform_gp[row, column] = sum4(
                            [
                                f32(transform[i, row, column] * shape[i])
                                for i in range(4)
                            ]
                        )

                for column in range(7):
                    projection = f32(
                        f32(
                            f32(force_gp[0] * transform_gp[0, column])
                            + f32(force_gp[1] * transform_gp[1, column])
                        )
                        + f32(force_gp[2] * transform_gp[2, column])
                    )
                    # The product is Single; assignment into double[] performs
                    # the only widening conversion in this accumulation.
                    out[column] += float(f32(projection * det_j))

        return out.tolist()

    def compute_line_load_internal(
        self,
        node_coords: List[Point],
        points: Tuple[Tuple[float, float, float], Tuple[float, float, float]],
        endpoint_forces: Tuple[Tuple[float, float, float], Tuple[float, float, float]],
    ) -> List[float]:
        """Port the C# ``Quad.ComputeStaticLoadInternal`` line-load branch.

        The source uses XNA ``Vector`` values and ``float`` arrays throughout.
        It also contains a compatibility-sensitive interpolation typo for the
        intrinsic line coordinates: both endpoint terms use ``(1-gp)/2``.
        This method deliberately preserves that behavior because it is part of
        the committed C# LiveLoad reference path.
        """
        f32 = np.float32
        out = np.zeros(7, dtype=np.float64)
        gp0 = f32(f32(np.sqrt(3.0)) / f32(3.0))
        gauss = (gp0, f32(-gp0))

        g = np.asarray((self.g.x, self.g.y, self.g.z), dtype=np.float32)
        e1 = np.asarray(self.reference_e1, dtype=np.float32)
        e2 = np.asarray(self.reference_e2, dtype=np.float32)
        e3 = np.asarray(self.reference_e3, dtype=np.float32)
        origin = np.asarray(
            (self.reference_origin.x, self.reference_origin.y, self.reference_origin.z),
            dtype=np.float32,
        )

        transform = np.zeros((4, 3, 7), dtype=np.float32)
        for i, node in enumerate(node_coords):
            xyz = np.asarray((node.x, node.y, node.z), dtype=np.float32)
            dx, dy, dz = xyz - g
            transform[i, 0, 0] = f32(1.0)
            transform[i, 1, 1] = f32(1.0)
            transform[i, 2, 2] = f32(1.0)
            transform[i, 0, 4] = dz
            transform[i, 0, 5] = f32(-dy)
            transform[i, 1, 3] = f32(-dz)
            transform[i, 1, 5] = dx
            transform[i, 2, 3] = dy
            transform[i, 2, 4] = f32(-dx)

        for component in range(3):
            transform[2, component, 6] = f32(
                -self.length[3]
                * self.sin[3]
                / self.sin[2]
                * (
                    self.sin[1] * float(e1[component])
                    + self.cos[1] * float(e2[component])
                )
            )
            transform[3, component, 6] = f32(
                -self.length[3]
                * (
                    self.sin[0] * float(e1[component])
                    - self.cos[0] * float(e2[component])
                )
            )

        l0, l1, l3 = f32(self.length[0]), f32(self.length[1]), f32(self.length[3])
        local_nodes = np.asarray(
            (
                (f32(-l0 / f32(2.0)), f32(0.0)),
                (f32(l0 / f32(2.0)), f32(0.0)),
                (
                    f32(l0 / f32(2.0) - f32(l1 * f32(self.cos[1]))),
                    f32(l1 * f32(self.sin[1])),
                ),
                (
                    f32(-l0 / f32(2.0) + f32(l3 * f32(self.cos[0]))),
                    f32(l3 * f32(self.sin[0])),
                ),
            ),
            dtype=np.float32,
        )

        local_points3 = np.zeros((2, 3), dtype=np.float32)
        local_points2 = np.zeros((2, 2), dtype=np.float32)
        for i, point in enumerate(points):
            vector = np.asarray(point, dtype=np.float32) - origin
            local_points3[i] = (
                f32(np.dot(vector, e1)),
                f32(np.dot(vector, e2)),
                f32(np.dot(vector, e3)),
            )
            local_points2[i] = (
                f32(local_points3[i, 0] - l0 / f32(2.0)),
                local_points3[i, 1],
            )

        def intrinsic(point: np.ndarray) -> tuple[np.float32, np.float32]:
            # Newton inversion of the bilinear map.  C#'s FindU/FindV stops at
            # 0.001; this converges more tightly while retaining float32 math.
            u = f32(0.0)
            v = f32(0.0)
            one = f32(1.0)
            four = f32(4.0)
            for _ in range(30):
                n = np.asarray(
                    (
                        f32((one-u)*(one-v)/four),
                        f32((one+u)*(one-v)/four),
                        f32((one+u)*(one+v)/four),
                        f32((one-u)*(one+v)/four),
                    ), dtype=np.float32,
                )
                du = np.asarray(
                    (f32(-(one-v)/four), f32((one-v)/four),
                     f32((one+v)/four), f32(-(one+v)/four)), dtype=np.float32,
                )
                dv = np.asarray(
                    (f32(-(one-u)/four), f32(-(one+u)/four),
                     f32((one+u)/four), f32((one-u)/four)), dtype=np.float32,
                )
                mapped = np.asarray(
                    (f32(np.dot(n, local_nodes[:,0])), f32(np.dot(n, local_nodes[:,1]))),
                    dtype=np.float32,
                )
                residual = mapped - point
                jac = np.asarray(
                    ((f32(np.dot(du, local_nodes[:,0])), f32(np.dot(dv, local_nodes[:,0]))),
                     (f32(np.dot(du, local_nodes[:,1])), f32(np.dot(dv, local_nodes[:,1])))),
                    dtype=np.float32,
                )
                det = f32(jac[0,0]*jac[1,1] - jac[0,1]*jac[1,0])
                if abs(float(det)) < 1e-20:
                    break
                duv0 = f32(( jac[1,1]*residual[0] - jac[0,1]*residual[1]) / det)
                duv1 = f32((-jac[1,0]*residual[0] + jac[0,0]*residual[1]) / det)
                u = f32(u - duv0)
                v = f32(v - duv1)
                if max(abs(float(duv0)), abs(float(duv1))) < 1e-7:
                    break
            return u, v

        uv = [intrinsic(local_points2[i]) for i in range(2)]
        forces = np.asarray(endpoint_forces, dtype=np.float32)
        line_length = f32(np.linalg.norm(np.asarray(points[0], np.float32) - np.asarray(points[1], np.float32)))
        one = f32(1.0)
        two = f32(2.0)
        four = f32(4.0)

        for gauss_point in gauss:
            force = np.asarray(
                [f32(forces[0,j]*(one-gauss_point)/two + forces[1,j]*(one+gauss_point)/two) for j in range(3)],
                dtype=np.float32,
            )
            # Preserve C# source typo (both endpoint terms use 1-gp).
            u = f32(uv[0][0]*(one-gauss_point)/two + uv[1][0]*(one-gauss_point)/two)
            v = f32(uv[0][1]*(one-gauss_point)/two + uv[1][1]*(one-gauss_point)/two)
            shape = np.asarray(
                (f32((one-u)*(one-v)/four), f32((one+u)*(one-v)/four),
                 f32((one+u)*(one+v)/four), f32((one-u)*(one+v)/four)),
                dtype=np.float32,
            )
            transform_gp = np.zeros((3,7), dtype=np.float32)
            for row in range(3):
                for col in range(7):
                    acc = f32(0.0)
                    for i in range(4):
                        acc = f32(acc + f32(transform[i,row,col]*shape[i]))
                    transform_gp[row,col] = acc
            for col in range(7):
                projection = f32(
                    f32(f32(force[0]*transform_gp[0,col]) + f32(force[1]*transform_gp[1,col]))
                    + f32(force[2]*transform_gp[2,col])
                )
                out[col] += float(f32(projection * line_length / two))

        # C# adds the moment of the line resultant about its projection on the
        # quad plane.  This term is zero for the supplied symmetric transverse
        # line, but retain the general calculation.
        f0, f1 = forces[0], forces[1]
        l0f, l1f = f32(np.linalg.norm(f0)), f32(np.linalg.norm(f1))
        denom = f32(l1f + l0f)
        if line_length > 0 and abs(float(denom)) > 1e-30:
            distance = f32(line_length / f32(3.0) * f32(f32(2.0)*l1f + l0f) / denom)
            direction = np.asarray(points[1], np.float32) - np.asarray(points[0], np.float32)
            direction /= f32(np.linalg.norm(direction))
            centroid = np.asarray(points[0], np.float32) + f32(distance) * direction
            normal = e3 / f32(np.linalg.norm(e3))
            plane_point = np.asarray((node_coords[0].x,node_coords[0].y,node_coords[0].z), np.float32)
            projected = centroid - f32(np.dot(centroid-plane_point, normal)) * normal
            resultant = f32(0.5) * (f0+f1) * line_length
            moment = np.cross(centroid-projected, resultant).astype(np.float32)
            out[3] += float(moment[0]); out[4] += float(moment[1]); out[5] += float(moment[2])
        return out.tolist()

    def compute_self_weight_load(self, dir_x: float, dir_y: float, dir_z: float, w: float) -> List[Tuple[float, float, float]]:
        """Port C# ``Thickness[i] * w * Vector3 dir`` in single precision."""
        f32 = np.float32
        direction = (f32(dir_x), f32(dir_y), f32(dir_z))
        weight = f32(w)
        forces: List[Tuple[float, float, float]] = []
        for thickness in self.thickness:
            scalar = f32(f32(thickness) * weight)
            forces.append(
                tuple(float(f32(scalar * component)) for component in direction)
            )
        return forces

    # ── Diagonal spring kinematic transformation ─────────────────────────────

    def d_alfa_2d_diag(self) -> float:
        r"""Kinematic factor from 7th DOF (warping amplitude) to diagonal spring strain.

        Corresponds to C# ``DAlfa2DDiag()``:

            = Length[0] * Length[3] * Sin[0] / Diago[1]
        """
        if self.diago[1] == 0.0:
            return 0.0
        return self.length[0] * self.length[3] * self.sin[0] / self.diago[1]

    def d_diag_2d_alfa(self) -> float:
        """Inverse of :meth:`d_alfa_2d_diag`."""
        v = self.d_alfa_2d_diag()
        return 1.0 / v if v != 0.0 else 0.0

    @property
    def cos_alfa(self) -> float:
        """Literal port of C# ``Quad.cosAlfa``.

        The property is a law-of-cosines quantity based on ``Diago[0]`` and
        can legitimately be negative for distorted quadrilaterals.  Its sign
        is part of the diagonal Coulomb friction law.
        """
        denominator = 2.0 * self.length[0] * self.diago[0]
        if denominator == 0.0:
            return 0.0
        return (
            self.length[0] ** 2
            + self.diago[0] ** 2
            - self.length[1] ** 2
        ) / denominator

    # ── ComputeK ─────────────────────────────────────────────────────────────

    def compute_k(self, alfa: float = 0.0) -> float:
        """Diagonal (7th DOF) stiffness.

        C# ``ComputeK``:

            k = Spring.GetK(alfa)
            Status.K = k * DAlfa2DDiag()^2
        """
        if self.spring is None:
            return 0.0
        k = self.spring.get_k(alfa)
        dalfa = self.d_alfa_2d_diag()
        self.status.k = k * dalfa * dalfa
        return self.status.k

    # ── GetDiagonalStiffness ─────────────────────────────────────────────────

    def get_diagonal_stiffness(self, E: float, G: float) -> float:
        """Full in-plane stiffness projected onto the diagonal (7th) DOF.

        C# ``GetDiagonalStiffness(E, G)``.

        Performs a 2×2 Gauss-Legendre integration of the plane-stress
        constitutive matrix B^T·D·B over the quadrilateral mid-surface,
        then projects through the warping displacement vector.

        Parameters
        ----------
        E : Young's modulus.
        G : Shear modulus.
        """
        nu = E / (2.0 * G) - 1.0           # Poisson ratio
        lam = E * nu / (2.0 * (1.0 + 2.0 * nu))  # λ = νE/((1+ν)(1-2ν)) – first Lamé param

        # Local node coordinates (X, Y)
        L0, L1, L3 = self.length[0], self.length[1], self.length[3]
        Cos0, Cos1 = self.cos[0], self.cos[1]
        Sin0, Sin1 = self.sin[0], self.sin[1]
        X = [ -L0 / 2.0,  L0 / 2.0,
               L0 / 2.0 - L1 * Cos1,  -L0 / 2.0 + L3 * Cos0 ]
        Y = [ 0.0, 0.0,  L1 * Sin1,  L3 * Sin0 ]

        # Gauss points (2×2)
        gp = sqrt(3.0) / 3.0
        gauss = [gp, -gp]

        # Accumulated stiffness coefficients (symmetric 4×4 layout)
        num3 = num4 = num5 = num6 = 0.0
        num7 = num8 = num9 = 0.0
        num10 = num11 = num12 = 0.0
        num3 = num4 = num5 = num6 = 0.0
        num7 = num8 = num9 = 0.0
        num10 = num11 = num12 = 0.0

        # Gauss-point arrays (2 × 2)
        array3 = [[0.0]*2 for _ in range(2)]   # thickness interpolated
        array4 = [[0.0]*2 for _ in range(2)]
        array5 = [[0.0]*2 for _ in range(2)]
        array6 = [[0.0]*2 for _ in range(2)]
        array7 = [[0.0]*2 for _ in range(2)]
        array8 = [[0.0]*2 for _ in range(2)]
        array9 = [[0.0]*2 for _ in range(2)]
        array10 = [[0.0]*2 for _ in range(2)]
        array11 = [[0.0]*2 for _ in range(2)]
        array12 = [[0.0]*2 for _ in range(2)]
        array13 = [[0.0]*2 for _ in range(2)]
        array14 = [[0.0]*2 for _ in range(2)]
        array15 = [[0.0]*2 for _ in range(2)]
        array16 = [[0.0]*2 for _ in range(2)]
        array17 = [[0.0]*2 for _ in range(2)]
        array18 = [[0.0]*2 for _ in range(2)]
        array19 = [[0.0]*2 for _ in range(2)]
        array20 = [[0.0]*2 for _ in range(2)]
        array21 = [[0.0]*2 for _ in range(2)]
        array22 = [[0.0]*2 for _ in range(2)]
        array23 = [[0.0]*2 for _ in range(2)]
        array24 = [[0.0]*2 for _ in range(2)]
        array25 = [[0.0]*2 for _ in range(2)]
        array26 = [[0.0]*2 for _ in range(2)]
        array27 = [[0.0]*2 for _ in range(2)]
        array28 = [[0.0]*2 for _ in range(2)]
        array29 = [[0.0]*2 for _ in range(2)]
        array30 = [[0.0]*2 for _ in range(2)]
        array31 = [[0.0]*2 for _ in range(2)]
        array32 = [[0.0]*2 for _ in range(2)]
        array33 = [[0.0]*2 for _ in range(2)]
        array34 = [[0.0]*2 for _ in range(2)]

        for i in range(2):
            for j in range(2):
                xi = gauss[i]
                eta = gauss[j]

                # C# array3 = interpolated thickness
                array3[i][j] = (self.thickness[0] * (1.0 - xi) * (1.0 - eta) / 4.0 +
                                self.thickness[1] * (1.0 + xi) * (1.0 - eta) / 4.0 +
                                self.thickness[2] * (1.0 + xi) * (1.0 + eta) / 4.0 +
                                self.thickness[3] * (1.0 - xi) * (1.0 + eta) / 4.0)

                # array4..array11: shape function derivatives at xi,eta
                # These correspond to dN_k/dxi and dN_k/deta for each of the 4 nodes
                # but the C# code evaluates them in a specific pattern.

                # C# array4 = -(1-eta)/4  (dN0/dxi)
                # array5 =  (1-eta)/4     (dN1/dxi)
                # array6 =  (1+eta)/4     (dN2/dxi)
                # array7 = -(1+eta)/4     (dN3/dxi)
                array4[i][j] = -(1.0 - eta) / 4.0
                array5[i][j] =  (1.0 - eta) / 4.0
                array6[i][j] =  (1.0 + eta) / 4.0
                array7[i][j] = -(1.0 + eta) / 4.0

                # array8 = -(1-xi)/4      (dN0/deta)
                # array9 = -(1+xi)/4      (dN1/deta)
                # array10 = (1+xi)/4      (dN2/deta)
                # array11 = (1-xi)/4      (dN3/deta)
                array8[i][j] = -(1.0 - xi) / 4.0
                array9[i][j] = -(1.0 + xi) / 4.0
                array10[i][j] = (1.0 + xi) / 4.0
                array11[i][j] = (1.0 - xi) / 4.0

                # Jacobian rows: dX/dxi, dX/deta and dY/dxi, dY/deta
                # array12 = dX/dxi, array13 = dX/deta
                # array14 = dY/dxi, array15 = dY/deta
                array12[i][j] = (X[0] * array4[i][j] + X[1] * array5[i][j] +
                                 X[2] * array6[i][j] + X[3] * array7[i][j])
                array13[i][j] = (X[0] * array8[i][j] + X[1] * array9[i][j] +
                                 X[2] * array10[i][j] + X[3] * array11[i][j])
                array14[i][j] = (Y[0] * array4[i][j] + Y[1] * array5[i][j] +
                                 Y[2] * array6[i][j] + Y[3] * array7[i][j])
                array15[i][j] = (Y[0] * array8[i][j] + Y[1] * array9[i][j] +
                                 Y[2] * array10[i][j] + Y[3] * array11[i][j])

                # Jacobian determinant
                array16[i][j] = (array12[i][j] * array15[i][j] -
                                 array13[i][j] * array14[i][j])

                if abs(array16[i][j]) < 1e-30:
                    continue

                # Inverse Jacobian
                array17[i][j] =  array15[i][j] / array16[i][j]   # dxi/dX
                array18[i][j] = -array14[i][j] / array16[i][j]   # deta/dX
                array19[i][j] = -array13[i][j] / array16[i][j]   # dxi/dY
                array20[i][j] =  array12[i][j] / array16[i][j]   # deta/dY

                # dN_i/dX, dN_i/dY assembled into "B" columns
                # array21 = dN2/dX, array22 = dN3/dX
                # array23 = dN2/dY, array24 = dN3/dY
                # (only nodes 2 and 3 have non-zero warping contribution)
                # Wait — the C# code computes for all 4 "columns", but actually:
                # array21 = dN1/dX * (1+eta)/4 + dN2/dX * (1+xi)/4  (??)
                # Let's re-read the C# more carefully.

                # C# array21 = array17 * (1+eta)/4 + array18 * (1+xi)/4
                # This is NOT a shape function derivative — it's a B-matrix
                # component for the warping DOF.
                # Actually looking at the C# code:
                #   array21[i,j] = array17[i,j] * (1+eta)/4 + array18[i,j] * (1+xi)/4
                # These are the terms ∂N_k/∂x · ψ_k where ψ is the warping shape.

                array21[i][j] = (array17[i][j] * (1.0 + eta) / 4.0 +
                                 array18[i][j] * (1.0 + xi) / 4.0)
                array22[i][j] = (-array17[i][j] * (1.0 + eta) / 4.0 +
                                 array18[i][j] * (1.0 - xi) / 4.0)
                array23[i][j] = (array19[i][j] * (1.0 + eta) / 4.0 +
                                 array20[i][j] * (1.0 + xi) / 4.0)
                array24[i][j] = (-array19[i][j] * (1.0 + eta) / 4.0 +
                                 array20[i][j] * (1.0 - xi) / 4.0)

                # Constitutive contributions to the 4×4 stiffness block
                # (actually 2×2 since we only have 2 warping modes)
                # These are B^T·D·B integrated over the element.
                array25[i][j] = ((lam + 2.0 * G) * array21[i][j]**2 +
                                 G * array23[i][j]**2)
                array26[i][j] = ((lam + G) * array21[i][j] * array23[i][j])
                array27[i][j] = ((lam + 2.0 * G) * array21[i][j] * array22[i][j] +
                                 G * array23[i][j] * array24[i][j])
                array28[i][j] = (lam * array21[i][j] * array24[i][j] +
                                 G * array23[i][j] * array22[i][j])
                array29[i][j] = ((lam + 2.0 * G) * array23[i][j]**2 +
                                 G * array21[i][j]**2)
                array30[i][j] = (lam * array23[i][j] * array22[i][j] +
                                 G * array21[i][j] * array24[i][j])
                array31[i][j] = ((lam + 2.0 * G) * array23[i][j] * array24[i][j] +
                                 G * array21[i][j] * array22[i][j])
                array32[i][j] = ((lam + 2.0 * G) * array22[i][j]**2 +
                                 G * array24[i][j]**2)
                array33[i][j] = ((lam + G) * array22[i][j] * array24[i][j])
                array34[i][j] = ((lam + 2.0 * G) * array24[i][j]**2 +
                                 G * array22[i][j]**2)

                # Accumulate weighted by thickness * detJ
                w = array3[i][j] * array16[i][j]

                num3  += w * array25[i][j]
                num4  += w * array26[i][j]
                num5  += w * array27[i][j]
                num6  += w * array28[i][j]
                num7  += w * array29[i][j]
                num8  += w * array30[i][j]
                num9  += w * array31[i][j]
                num10 += w * array32[i][j]
                num11 += w * array33[i][j]
                num12 += w * array34[i][j]

        # Warping displacement vector (C# array2)
        Sin2, Sin3 = self.sin[2], self.sin[3]
        Cos2, Cos0 = self.cos[2], self.cos[0]
        a = [0.0] * 4
        if abs(Sin2) > 1e-30:
            a[0] = -L3 * Sin3 * Sin1 / Sin2
            a[1] = -L3 * Sin3 * Cos1 / Sin2
        else:
            a[0] = a[1] = 0.0
        a[2] = -L3 * Sin0
        a[3] =  L3 * Cos0

        # Quadratic form a^T · [stiffness_4x4] · a
        S = (num3 * a[0]**2 + num7 * a[1]**2 + num10 * a[2]**2 + num12 * a[3]**2 +
             2.0 * num4 * a[0] * a[1] +
             2.0 * num5 * a[0] * a[2] +
             2.0 * num6 * a[0] * a[3] +
             2.0 * num8 * a[1] * a[2] +
             2.0 * num9 * a[1] * a[3] +
             2.0 * num11 * a[2] * a[3])

        # Scale by (d_diag_2d_alfa)^2
        scale = self.d_diag_2d_alfa()
        return scale * scale * S

    # ── SetNonLinearProperties ───────────────────────────────────────────────

    def set_non_linear_properties(self, k: float, E: float, G: float,
                                   Fyt: float, Fyc: float) -> Tuple[float, float]:
        """Literal port of C# ``Quad.SetNonLinearProperties``.

        The C# routine evaluates both principal stresses for each of two
        opposite unit diagonal deformations.  Its extrema are intentionally
        cumulative across the two passes; the first and second returned yield
        forces can therefore have different magnitudes.  A previous Python
        simplification used one symmetric extrema pair and overestimated the
        Quad cohesion by up to two orders of magnitude.
        """
        if _quad_yield_search_kernel is not None:
            return _quad_yield_search_kernel(
                float(k), float(E), float(G), float(Fyt), float(Fyc),
                float(self.d_alfa_2d_diag()),
                float(self.length[0]), float(self.length[1]), float(self.length[3]),
                float(self.cos[0]), float(self.cos[1]),
                float(self.sin[0]), float(self.sin[1]), float(self.sin[2]), float(self.sin[3]),
            )
        nu = E / (2.0 * G) - 1.0
        lam = E * nu / (2.0 * (1.0 + 2.0 * nu))

        L0, L1, L3 = self.length[0], self.length[1], self.length[3]
        cos0, cos1 = self.cos[0], self.cos[1]
        sin0, sin1, sin2, sin3 = self.sin[0], self.sin[1], self.sin[2], self.sin[3]
        x = [-L0 / 2.0, L0 / 2.0, L0 / 2.0 - L1 * cos1, -L0 / 2.0 + L3 * cos0]
        y = [0.0, 0.0, L1 * sin1, L3 * sin0]

        # These are C# num4 (largest principal stress) and num5 (smallest).
        # They are deliberately not reset between the two deformation signs.
        max_principal = 0.0
        min_principal = 0.0
        result = [0.0, 0.0]
        n = 100

        if abs(sin2) <= 1.0e-30:
            return 0.0, 0.0
        w0 = -L3 * sin3 * sin1 / sin2
        w1 = -L3 * sin3 * cos1 / sin2
        w2 = -L3 * sin0
        # C# SetNonLinearProperties uses a negative fourth warping term
        # here (unlike GetDiagonalStiffness, whose projection vector stores
        # the positive value). Preserve that source-level sign asymmetry.
        w3 = -L3 * cos0

        for pass_index in range(2):
            direction = (-1.0) ** pass_index
            pass_min = 0.0
            pass_max = 0.0
            for flat_index in range(n * n):
                row = flat_index // n + 1
                col = flat_index + 1 - (row - 1) * n
                xi = -1.0 + 2.0 / n * (col - 1.0) + 1.0 / n
                eta = -1.0 + 2.0 / n * (row - 1.0) + 1.0 / n

                dxi = [
                    -(1.0 - eta) / 4.0,
                    (1.0 - eta) / 4.0,
                    (1.0 + eta) / 4.0,
                    -(1.0 + eta) / 4.0,
                ]
                deta = [
                    -(1.0 - xi) / 4.0,
                    -(1.0 + xi) / 4.0,
                    (1.0 + xi) / 4.0,
                    (1.0 - xi) / 4.0,
                ]
                j11 = sum(x[i] * dxi[i] for i in range(4))
                j12 = sum(x[i] * deta[i] for i in range(4))
                j21 = sum(y[i] * dxi[i] for i in range(4))
                j22 = sum(y[i] * deta[i] for i in range(4))
                det = j11 * j22 - j12 * j21
                if abs(det) <= 1.0e-30:
                    continue

                inv11 = j22 / det
                inv12 = -j21 / det
                inv21 = -j12 / det
                inv22 = j11 / det

                b1x = inv11 * (1.0 + eta) / 4.0 + inv12 * (1.0 + xi) / 4.0
                b2x = -inv11 * (1.0 + eta) / 4.0 + inv12 * (1.0 - xi) / 4.0
                b1y = inv21 * (1.0 + eta) / 4.0 + inv22 * (1.0 + xi) / 4.0
                b2y = -inv21 * (1.0 + eta) / 4.0 + inv22 * (1.0 - xi) / 4.0

                eps_x = direction * (w0 * b1x + w2 * b2x)
                eps_y = direction * (w1 * b1y + w3 * b2y)
                gamma_xy = direction * (
                    w0 * b1y + w1 * b1x + w2 * b2y + w3 * b2x
                )
                sigma_x = lam * (eps_x + eps_y) + 2.0 * G * eps_x
                sigma_y = lam * (eps_x + eps_y) + 2.0 * G * eps_y
                tau = G * gamma_xy
                average = (sigma_x + sigma_y) / 2.0
                radius = sqrt(((sigma_x - sigma_y) / 2.0) ** 2 + tau ** 2)
                principal_max = average + radius
                principal_min = average - radius
                if principal_min < pass_min:
                    pass_min = principal_min
                if principal_max > pass_max:
                    pass_max = principal_max

            if pass_min < min_principal:
                min_principal = pass_min
            if pass_max > max_principal:
                max_principal = pass_max

            if max_principal == 0.0 or min_principal == 0.0:
                result[pass_index] = 0.0
            else:
                scale = direction * min(
                    abs(Fyt / max_principal),
                    abs(Fyc / min_principal),
                )
                result[pass_index] = k * self.d_alfa_2d_diag() * scale

        return result[0], result[1]

    # ── SetResistingForce / GetResistingForce ────────────────────────────────

    def set_resisting_force(self) -> None:
        """Compute internal force F[0] from the diagonal spring.

        C# ``SetResistingForce``:

            base.F[0] = DAlfa2DDiag() * Spring.GetForce()
        """
        if self.spring is None:
            return
        self.status.f = self.d_alfa_2d_diag() * self.spring.get_force()

    def get_resisting_force(self, gdl_map: List[int],
                             alfa_map: List[float],
                             b: List[float]) -> None:
        """Distribute the diagonal spring resisting force into global vector b.

        C# ``GetResistingForce(LS, gdl=None)``.

        Parameters
        ----------
        gdl_map : list of global DOF indices (0-based) from Aff[6]
        alfa_map : corresponding alfa coefficients
        b : global load vector (mutated in-place)
        """
        if self.spring is None or not gdl_map:
            return
        # Ensure F[0] is up-to-date
        self.set_resisting_force()
        f0 = self.status.f

        for g, a in zip(gdl_map, alfa_map):
            if 0 <= g < len(b):
                b[g] -= f0 * a

    def compute_volume(self) -> float:
        """Return the cached C# ``Quad.GetVolume`` value."""
        if self._perf_volume is not None:
            return self._perf_volume
        l0, l1, l3 = self.length[0], self.length[1], self.length[3]
        xcoord = [-l0 / 2.0, l0 / 2.0, l0 / 2.0 - l1 * self.cos[1], -l0 / 2.0 + l3 * self.cos[0]]
        ycoord = [0.0, 0.0, l1 * self.sin[1], l3 * self.sin[0]]
        gp = sqrt(3.0) / 3.0
        volume = 0.0
        for xi in (gp, -gp):
            for eta in (gp, -gp):
                n = [
                    (1.0 - xi) * (1.0 - eta) / 4.0,
                    (1.0 + xi) * (1.0 - eta) / 4.0,
                    (1.0 + xi) * (1.0 + eta) / 4.0,
                    (1.0 - xi) * (1.0 + eta) / 4.0,
                ]
                dxi = [-(1.0 - eta) / 4.0, (1.0 - eta) / 4.0, (1.0 + eta) / 4.0, -(1.0 + eta) / 4.0]
                deta = [-(1.0 - xi) / 4.0, -(1.0 + xi) / 4.0, (1.0 + xi) / 4.0, (1.0 - xi) / 4.0]
                j11 = sum(xcoord[i] * dxi[i] for i in range(4))
                j12 = sum(xcoord[i] * deta[i] for i in range(4))
                j21 = sum(ycoord[i] * dxi[i] for i in range(4))
                j22 = sum(ycoord[i] * deta[i] for i in range(4))
                thickness = sum(n[i] * self.thickness[i] for i in range(4))
                volume += thickness * (j11 * j22 - j12 * j21)
        self._perf_volume = volume
        return volume

    def _ensure_dn_cache(self, collections) -> None:
        if self._perf_dn_edges is not None:
            return
        edges: list[tuple[tuple[object, bool], ...]] = []
        areas: list[float] = []
        for edge in range(4):
            refs: list[tuple[object, bool]] = []
            area = 0.0
            for interface_key in self.interface_keys[edge]:
                intf = collections.interfaces.get(interface_key)
                if intf is None:
                    continue
                area += intf.area()
                belongs = (
                    (intf.parent_type_element1 == "Quad" and intf.parent_element_key1 == self.key)
                    or (intf.parent_type_element2 == "Quad" and intf.parent_element_key2 == self.key)
                )
                if not belongs:
                    continue
                custom_springs = any(
                    "get_force" in spring.__dict__ or "get_incr_force" in spring.__dict__
                    for spring in intf.trasv_1
                )
                refs.append((intf, custom_springs))
            edges.append(tuple(refs))
            areas.append(area)
        self._perf_dn_edges = tuple(edges)
        self._perf_dn_areas = tuple(areas)

    def compute_dn(self, collections, ls=None, nr: bool = False) -> tuple[float, float]:
        """Port of C# ``Quad.ComputeDN`` using cached interface relationships."""
        del ls
        if not nr:
            raise NotImplementedError("Quad.ComputeDN with NR=False is not implemented")
        self._ensure_dn_cache(collections)
        assert self._perf_dn_edges is not None
        assert self._perf_dn_areas is not None
        normal_increment = [0.0] * 4
        committed_stress = [0.0] * 4
        for edge, refs in enumerate(self._perf_dn_edges):
            force = 0.0
            for intf, custom_springs in refs:
                custom_interface = "compute_dn" in intf.__dict__
                if custom_interface or custom_springs:
                    normal_increment[edge] += intf.compute_dn(nr=True)
                    force += sum(
                        float(spring.get_force() - spring.get_incr_force())
                        for spring in intf.trasv_1
                    )
                else:
                    normal_increment[edge] += float(intf.status.normal_increment)
                    force += float(intf.status.committed_normal_force)
            area = self._perf_dn_areas[edge]
            if area > 0.0:
                committed_stress[edge] = force / area
        sigma = 0.5 * (committed_stress[0] + committed_stress[2]) + 0.5 * (committed_stress[1] + committed_stress[3])
        dn = 0.5 * (normal_increment[0] + normal_increment[2]) + 0.5 * (normal_increment[1] + normal_increment[3])
        return dn, sigma

    def _local_increment(self, x: np.ndarray) -> list[float]:
        if self._perf_aff_pairs is None:
            self._perf_aff_pairs = tuple(
                tuple((entry.gdl - 1, float(entry.alfa)) for entry in entries)
                for entries in self.aff[:7]
            )
        size = len(x)
        out = [0.0] * 7
        for i, pairs in enumerate(self._perf_aff_pairs):
            total = 0.0
            for gdl, coefficient in pairs:
                if 0 <= gdl < size:
                    total += x[gdl] * coefficient
            out[i] = total
        return out

    def update_domain(self, ls_or_x, state, collections=None) -> None:
        """Port of ``Quad.UpdateDomain``.

        Calls ``set_trial_strain_takeda_diagonal_quad`` when the diagonal
        spring is a ``SpringCoulomb03`` (passing normal-force increment and
        material params), otherwise falls back to ``Spring.set_trial_strain``.
        """
        if self.spring is None:
            return
        x = ls_or_x.x if hasattr(ls_or_x, "x") else ls_or_x
        local_du = self._local_increment(x)
        for i, value in enumerate(local_du):
            self.status.u[i] += float(value)
        from histra.springs.coulomb03 import SpringCoulomb03
        if isinstance(self.spring, SpringCoulomb03):
            if collections is None:
                raise RuntimeError("Quad Coulomb update requires model collections for ComputeDN")
            dN, sigma = self.compute_dn(collections, ls_or_x, nr=True)
            if int(getattr(state, "step", 0)) == 1:
                self.sigma_initial = sigma
            strain = self.d_alfa_2d_diag() * self.status.u[6]
            self.spring.set_trial_strain_takeda_diagonal_quad(
                strain,
                dN,
                masonry=collections.materials.get(self.material_key),
                volume=self.compute_volume(),
                sigma=self.sigma_initial,
            )
        else:
            self.spring.set_trial_strain(self.d_alfa_2d_diag() * self.status.u[6])

    def commit(self, _ls=None) -> None:
        """Port of ``Quad.Commit``."""
        if self.spring is not None and not getattr(
            self.spring, "_histra_batch_managed", False
        ):
            self.spring.commit()

    def revert_to_last_commit(self, ls) -> None:
        """Port of ``Quad.revertToLastCommit``."""
        x = ls.x if hasattr(ls, "x") else ls
        for i, value in enumerate(self._local_increment(x)):
            self.status.u[i] += float(value)
        if self.spring is not None:
            batch = getattr(self.spring, "_histra_quad_batch", None)
            if batch is not None and getattr(self.spring, "_histra_batch_managed", False):
                batch.revert_quad(self)
            else:
                self.spring.revert_to_last_commit()
                if hasattr(self.spring, "revert_to_last_commit_stress_normal"):
                    self.spring.revert_to_last_commit_stress_normal()

    def max_u(self) -> float:
        """Port of ``Quad.MaxU``."""
        return max((abs(value) for value in self.status.u), default=0.0)

    # ── Set diagonal quad ────────────────────────────────────────────────────

    @classmethod
    def _warping_coeffs(cls, quad: Quad) -> List[float]:
        """Compute the warping displacement vector a[0..3] (C# array2)."""
        L3 = quad.length[3]
        Sin0, Sin1 = quad.sin[0], quad.sin[1]
        Sin2, Sin3 = quad.sin[2], quad.sin[3]
        Cos0, Cos1 = quad.cos[0], quad.cos[1]
        a = [0.0] * 4
        if abs(Sin2) > 1e-30:
            a[0] = -L3 * Sin3 * Sin1 / Sin2
            a[1] = -L3 * Sin3 * Cos1 / Sin2
        a[2] = -L3 * Sin0
        a[3] =  L3 * Cos0
        return a

    def compute_energy(self) -> Tuple[float, float, float]:
        """Port of Quad.ComputeEnergy — delegates to the spring."""
        if self.spring is not None and hasattr(self.spring, 'compute_energy'):
            return self.spring.compute_energy()
        k = getattr(self.spring, 'k', 0.0) if self.spring else 0.0
        u = getattr(self.spring, 'u', 0.0) if self.spring else 0.0
        e = 0.5 * k * u * u
        return e, 0.0, e

    @classmethod
    def from_xml(cls, elem) -> Quad:
        q = cls()
        q.key = int(elem.get("Key", "0"))
        q.name = elem.get("Name", "")
        for k, v in elem.attrib.items():
            if k not in {"Key", "Name"}:
                q.extra[k] = v
        q.parent_key = int(elem.get("ParentKey", "0"))
        q.parent_type = elem.get("ParentTypeElement", "")
        q.material_key = int(elem.get("MaterialKey", "0"))
        q.layer_key = int(elem.get("LayerKey", "0"))
        q.master_element_key = int(elem.get("MasterElementKey", "0"))
        q.master_element_type = elem.get("MasterElementType", "None")

        for i in range(4):
            q.node_keys[i] = int(elem.get(f"NodeKey{i+1}", "0"))
            q.length[i] = float(elem.get(f"Length{i+1}", "0"))
            q.sin[i] = float(elem.get(f"Sin{i+1}", "0"))
            q.cos[i] = float(elem.get(f"Cos{i+1}", "0"))
            q.thickness[i] = float(elem.get(f"Thickness{i+1}", "0"))
            nstr = elem.get(f"Normal{i+1}", None)
            if nstr:
                q.normal[i] = Point.from_str(nstr)
        for i in range(2):
            q.diago[i] = float(elem.get(f"Diago{i+1}", "0"))

        gstr = elem.get("G", None)
        if gstr:
            q.g = Point.from_str(gstr)

        # U1..U7 (post-solve state)
        for i in range(7):
            ustr = elem.get(f"U{i+1}", None)
            if ustr is not None:
                q.status.u[i] = float(ustr)

        # Spring
        sp = elem.find("Spring")
        if sp is not None:
            from histra.springs.registry import spring_from_xml
            q.spring = spring_from_xml(sp)

        # AfferenceMatrices
        aff_elem = elem.find("AfferenceMatrices")
        if aff_elem is not None:
            mats = aff_elem.findall("AfferenceMatrix")
            for idx, m in enumerate(mats):
                if idx >= 7:
                    break
                alfa_items = m.find("Alfa")
                gdl_items = m.find("Gdl")
                if alfa_items is not None and gdl_items is not None:
                    alfas = [float(a.get("Value", "0")) for a in alfa_items.findall("item")]
                    gdls = [int(g.get("Value", "0")) for g in gdl_items.findall("item")]
                    q.aff[idx] = [AfferenceEntry(gdl=g, alfa=a) for a, g in zip(alfas, gdls)]

        # Interface references
        for f in range(6):
            grp = elem.find(f"Interfaces{f+1}")
            if grp is not None:
                q.interface_keys[f] = [int(iface.get("Value", "0")) for iface in grp.findall("Interface")]

        # ReferenceSystem
        rs = elem.find("ReferenceSystem")
        if rs is not None:
            e1 = rs.get("E1", "1;0;0")
            e2 = rs.get("E2", "0;1;0")
            e3 = rs.get("E3", "0;0;1")
            q.reference_e1 = tuple(float(x) for x in e1.split(";"))
            q.reference_e2 = tuple(float(x) for x in e2.split(";"))
            q.reference_e3 = tuple(float(x) for x in e3.split(";"))
            orig = rs.get("Origin", None)
            if orig:
                q.reference_origin = Point.from_str(orig)

        return q
