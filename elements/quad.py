from __future__ import annotations
from dataclasses import dataclass, field
from math import sqrt
from typing import Dict, List, Tuple, Optional
from histra.types.point import Point
from histra.types.afference_entry import AfferenceEntry
from histra.springs.base import Spring
from histra.elements.quad_state import QuadState


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

    def compute_static_load_internal(self, node_coords: List[Point], nodal_forces: List[Tuple[float, float, float]]) -> List[float]:
        """2×2 Gauss integration of load distribution → P[0..6]."""
        L0, L1, L3 = self.length[0], self.length[1], self.length[3]
        Sin0, Sin1 = self.sin[0], self.sin[1]
        Sin2, Sin3 = self.sin[2], self.sin[3]
        Cos0, Cos1 = self.cos[0], self.cos[1]
        Gx, Gy, Gz = self.g.x, self.g.y, self.g.z
        e1x, e1y, e1z = self.reference_e1
        e2x, e2y, e2z = self.reference_e2

        # Transformation matrices for each node (3×7)
        # Columns 0-2: identity (direct forces), 3-5: moment arms, 6: warping
        T = []
        for i in range(4):
            n = node_coords[i]
            dx, dy, dz = n.x - Gx, n.y - Gy, n.z - Gz
            ti = [
                [1.0, 0.0, 0.0, 0.0, dz, -dy, 0.0],
                [0.0, 1.0, 0.0, -dz, 0.0, dx, 0.0],
                [0.0, 0.0, 1.0, dy, -dx, 0.0, 0.0],
            ]
            T.append(ti)

        # Warping column (col 6) for nodes 2 and 3
        if L0 != 0 and Sin2 != 0:
            T[2][0][6] = -L3 * Sin3 / Sin2 * (Sin1 * e1x + Cos1 * e2x)
            T[2][1][6] = -L3 * Sin3 / Sin2 * (Sin1 * e1y + Cos1 * e2y)
            T[2][2][6] = -L3 * Sin3 / Sin2 * (Sin1 * e1z + Cos1 * e2z)
            T[3][0][6] = -L3 * (Sin0 * e1x - Cos0 * e2x)
            T[3][1][6] = -L3 * (Sin0 * e1y - Cos0 * e2y)
            T[3][2][6] = -L3 * (Sin0 * e1z - Cos0 * e2z)

        # Node local (u,v) coordinates
        u_vals = [-L0 / 2, L0 / 2, L0 / 2 - L1 * Cos1, -L0 / 2 + L3 * Cos0]
        v_vals = [0.0, 0.0, L1 * Sin1, L3 * Sin0]

        # Gauss points
        gp = sqrt(3.0) / 3.0
        gauss = [gp, -gp]

        out = [0.0] * 7

        for li in range(2):
            xi = gauss[li]
            for mi in range(2):
                eta = gauss[mi]

                # Shape functions
                N = [
                    (1.0 - xi) * (1.0 - eta) / 4.0,
                    (1.0 + xi) * (1.0 - eta) / 4.0,
                    (1.0 + xi) * (1.0 + eta) / 4.0,
                    (1.0 - xi) * (1.0 + eta) / 4.0,
                ]

                # Shape function derivatives w.r.t. xi and eta
                dN_dxi = [
                    -(1.0 - eta) / 4.0,
                    (1.0 - eta) / 4.0,
                    (1.0 + eta) / 4.0,
                    -(1.0 + eta) / 4.0,
                ]
                dN_deta = [
                    -(1.0 - xi) / 4.0,
                    -(1.0 + xi) / 4.0,
                    (1.0 + xi) / 4.0,
                    (1.0 - xi) / 4.0,
                ]

                # Jacobian
                J11 = sum(u_vals[i] * dN_dxi[i] for i in range(4))
                J12 = sum(u_vals[i] * dN_deta[i] for i in range(4))
                J21 = sum(v_vals[i] * dN_dxi[i] for i in range(4))
                J22 = sum(v_vals[i] * dN_deta[i] for i in range(4))
                detJ = J11 * J22 - J12 * J21

                # Interpolated force at Gauss point
                fx = sum(N[i] * nodal_forces[i][0] for i in range(4))
                fy = sum(N[i] * nodal_forces[i][1] for i in range(4))
                fz = sum(N[i] * nodal_forces[i][2] for i in range(4))

                # Interpolated transformation matrix
                T_gp = [[0.0] * 7 for _ in range(3)]
                for n in range(3):
                    for c in range(7):
                        T_gp[n][c] = sum(N[i] * T[i][n][c] for i in range(4))

                # Accumulate: P += (Fx * T_row0 + Fy * T_row1 + Fz * T_row2) * detJ
                for c in range(7):
                    val = fx * T_gp[0][c] + fy * T_gp[1][c] + fz * T_gp[2][c]
                    out[c] += val * detJ

        return out

    def compute_self_weight_load(self, dir_x: float, dir_y: float, dir_z: float, w: float) -> List[Tuple[float, float, float]]:
        """Compute nodal forces for self-weight: F[i] = thickness[i] * w * dir"""
        return [
            (self.thickness[i] * w * dir_x, self.thickness[i] * w * dir_y, self.thickness[i] * w * dir_z)
            for i in range(4)
        ]

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
        """Compute nonlinear yield forces in tension and compression.

        C# ``SetNonLinearProperties(k, E, G, Fyt, Fyc)``.

        Searches over a 100×100 grid in the parametric domain for the
        minimum principal stress (compression) and maximum principal stress
        (tension), then returns the yield forces scaled by ``d_alfa_2d_diag()``.

        Returns
        -------
        (fy_tension, fy_compression)  — the forces at which the diagonal
        spring yields in tension and compression respectively.
        """
        nu = E / (2.0 * G) - 1.0
        lam = E * nu / (2.0 * (1.0 + 2.0 * nu))

        L0, L1, L3 = self.length[0], self.length[1], self.length[3]
        Cos0, Cos1 = self.cos[0], self.cos[1]
        Sin0, Sin1 = self.sin[0], self.sin[1]
        Sin2, Sin3 = self.sin[2], self.sin[3]
        Cos2, Cos0 = self.cos[2], self.cos[0]

        X = [-L0 / 2.0, L0 / 2.0,
             L0 / 2.0 - L1 * Cos1, -L0 / 2.0 + L3 * Cos0]
        Y = [0.0, 0.0, L1 * Sin1, L3 * Sin0]

        n = 100  # grid size (C#: num3 = 100)
        s_min = 0.0  # most compressive (most negative)
        s_max = 0.0  # most tensile (most positive)
        # Location of principal stresses
        xi_comp = yi_comp = 0.0
        xi_tens = yi_tens = 0.0

        for sign in (1, -1):  # sign = +1 for tension, -1 for compression
            s_best = -1e100 if sign > 0 else 1e100
            for j in range(n):
                for i_idx in range(n):
                    eta = -1.0 + 2.0 / n * i_idx + 1.0 / n
                    xi = -1.0 + 2.0 / n * j + 1.0 / n

                    # Shape function derivatives at (xi, eta)
                    dN_dxi  = [-(1.0 - eta) / 4.0,  (1.0 - eta) / 4.0,
                                (1.0 + eta) / 4.0, -(1.0 + eta) / 4.0]
                    dN_deta = [-(1.0 - xi) / 4.0, -(1.0 + xi) / 4.0,
                                (1.0 + xi) / 4.0,  (1.0 - xi) / 4.0]

                    J11 = sum(X[i] * dN_dxi[i] for i in range(4))
                    J12 = sum(X[i] * dN_deta[i] for i in range(4))
                    J21 = sum(Y[i] * dN_dxi[i] for i in range(4))
                    J22 = sum(Y[i] * dN_deta[i] for i in range(4))
                    detJ = J11 * J22 - J12 * J21
                    if abs(detJ) < 1e-30:
                        continue

                    inv11 =  J22 / detJ
                    inv12 = -J12 / detJ
                    inv21 = -J21 / detJ
                    inv22 =  J11 / detJ

                    # B-matrix columns (C# lines: num28..num31)
                    a1 = inv11 * (1.0 + eta) / 4.0 + inv12 * (1.0 + xi) / 4.0
                    a2 = -inv11 * (1.0 + eta) / 4.0 + inv12 * (1.0 - xi) / 4.0
                    b1 = inv21 * (1.0 + eta) / 4.0 + inv22 * (1.0 + xi) / 4.0
                    b2 = -inv21 * (1.0 + eta) / 4.0 + inv22 * (1.0 - xi) / 4.0

                    # Warping function coefficients at this point
                    # C#: w1 = array2[0]*N1 + array2[2]*N4? Actually no:
                    # num32 = sign * (a[0]*a1 + a[2]*a2)  (eps_x)
                    # num33 = sign * (a[1]*b1 + a[3]*b2)  (eps_y)
                    # num34 = sign * (a[0]*b1 + a[1]*a1 + a[2]*b2 + a[3]*a2) (gamma_xy)
                    if abs(Sin2) > 1e-30:
                        w0 = -L3 * Sin3 * Sin1 / Sin2
                        w1 = -L3 * Sin3 * Cos1 / Sin2
                    else:
                        w0 = w1 = 0.0
                    w2 = -L3 * Sin0
                    w3 =  L3 * Cos0

                    eps_x = w0 * a1 + w2 * a2
                    eps_y = w1 * b1 + w3 * b2
                    gam_xy = w0 * b1 + w1 * a1 + w2 * b2 + w3 * a2

                    eps_x *= sign
                    eps_y *= sign
                    gam_xy *= sign

                    # Stress from constitutive law (plane stress)
                    sig_x = (lam + 2.0 * G) * eps_x + lam * eps_y
                    sig_y = lam * eps_x + (lam + 2.0 * G) * eps_y
                    tau_xy = G * gam_xy

                    # Principal stresses
                    sig_avg = (sig_x + sig_y) / 2.0
                    sig_diff = sqrt(((sig_x - sig_y) / 2.0)**2 + tau_xy**2)
                    sig_1 = sig_avg + sig_diff  # max principal
                    sig_3 = sig_avg - sig_diff  # min principal

                    if sign > 0 and sig_1 > s_best:
                        s_best = sig_1
                        xi_tens, yi_tens = xi, eta
                    elif sign < 0 and sig_3 < s_best:
                        s_best = sig_3
                        xi_comp, yi_comp = xi, eta

            if sign > 0:
                s_max = s_best
            else:
                s_min = s_best

        # Scale yield stresses by interpolation at the critical points
        def interp_coords(xi, eta):
            """Bilinear interpolation of local (X,Y) at (xi, eta)."""
            N = [(1.0 - xi) * (1.0 - eta) / 4.0,
                 (1.0 + xi) * (1.0 - eta) / 4.0,
                 (1.0 + xi) * (1.0 + eta) / 4.0,
                 (1.0 - xi) * (1.0 + eta) / 4.0]
            x = sum(X[i] * N[i] for i in range(4))
            y = sum(Y[i] * N[i] for i in range(4))
            return x, y

        # For tension direction
        f_max = min(abs(Fyt / s_max) if abs(s_max) > 1e-30 else 0.0,
                    abs(Fyc / s_min) if abs(s_min) > 1e-30 else 0.0)
        f_min = -f_max

        dalfa = self.d_alfa_2d_diag()
        fy_t = k * dalfa * f_max
        fy_c = k * dalfa * f_min
        return fy_t, fy_c

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

    def update_domain(self, x, state) -> None:
        """Port of ``Quad.UpdateDomain``.

        Calls ``set_trial_strain_takeda_diagonal_quad`` when the diagonal
        spring is a ``SpringCoulomb03`` (passing normal-force increment and
        material params), otherwise falls back to ``Spring.set_trial_strain``.
        """
        if self.spring is None:
            return
        for i, aff_i in enumerate(self.aff[:7]):
            self.status.u[i] += sum(
                x[entry.gdl - 1] * entry.alfa
                for entry in aff_i
                if 0 <= entry.gdl - 1 < len(x)
            )
            from histra.springs.coulomb03 import SpringCoulomb03
        if isinstance(self.spring, SpringCoulomb03):
            # dN = 0.0 until interface normal-force coupling is connected
            dN = 0.0
            strain = self.d_alfa_2d_diag() * self.status.u[6]
            self.spring.set_trial_strain_takeda_diagonal_quad(
                strain, dN, masonry=None, volume=0.0, sigma=0.0
            )
        else:
            self.spring.set_trial_strain(self.d_alfa_2d_diag() * self.status.u[6])

    def commit(self, _ls=None) -> None:
        """Port of ``Quad.Commit``."""
        if self.spring is not None:
            self.spring.commit()

    def revert_to_last_commit(self, ls) -> None:
        """Port of ``Quad.revertToLastCommit``."""
        x = ls.x if hasattr(ls, "x") else ls
        for i, aff_i in enumerate(self.aff[:7]):
            self.status.u[i] += sum(
                x[entry.gdl - 1] * entry.alfa
                for entry in aff_i
                if 0 <= entry.gdl - 1 < len(x)
            )
        if self.spring is not None:
            self.spring.revert_to_last_commit()

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
