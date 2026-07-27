from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Any, List, Tuple
import numpy as np
from histra.types.point import Point
from histra.types.afference_entry import AfferenceEntry
from histra.elements.interface_state import InterfaceState, _list2d


@dataclass
class Interface:
    key: int = 0
    node_keys: List[int] = field(default_factory=lambda: [0, 0])
    parent_element_key1: int = 0
    parent_element_key2: int = 0
    parent_type_element1: str = ""
    parent_type_element2: str = ""
    face1: int = 0
    face2: int = 0
    length: float = 0.0
    thickness: List[float] = field(default_factory=lambda: [0.0, 0.0])
    nrow: int = 3
    ncol: int = 3
    nspring: int = 9
    dim_aff: List[int] = field(default_factory=lambda: [6, 2, 4])
    dim_aff_tot: int = 12
    trasv_1: list = field(default_factory=list)  # Springs
    trasv_2: list = field(default_factory=list)
    slid: list = field(default_factory=list)
    slid_out_plan: list = field(default_factory=list)
    aff: List[List[AfferenceEntry]] = field(default_factory=lambda: [[] for _ in range(12)])
    reference_e1: Tuple[float, float, float] = (1.0, 0.0, 0.0)
    reference_e2: Tuple[float, float, float] = (0.0, 1.0, 0.0)
    reference_e3: Tuple[float, float, float] = (0.0, 0.0, 1.0)
    reference_origin: Point = field(default_factory=Point)
    status: InterfaceState = field(default_factory=InterfaceState)
    name: str = ""
    material_key: int = 0
    layer_key: int = 0
    interfaccia_vincolata: bool = False
    frot: int = 0
    imax: int = 400
    csi: float = 0.0
    vint2d: List[Point] = field(default_factory=lambda: [Point(), Point(), Point(), Point()])
    vint3d: List[Point] = field(default_factory=lambda: [Point(), Point(), Point(), Point()])
    # Local 12-DOF resisting-force vector (port of ComputationalElement.F)
    f: List[float] = field(default_factory=lambda: [0.0] * 12)

    def interfaccia_vincolata_computed(self) -> bool:
        """Port of .NET InterfacciaVincolata(): True if either parent is a Restraint."""
        return self.parent_type_element1 == "Restraint" or self.parent_type_element2 == "Restraint"

    # ═════════════════════════════════════════════════════════════════════════
    # Geometry helpers  (port of Interface geometry methods)
    # ═════════════════════════════════════════════════════════════════════════

    def idx(self, row: int, col: int) -> int:
        """Port of Interface.idx(riga, colonna) = riga * Ncol + colonna."""
        return row * self.ncol + col

    def get_di(self, row: int, index: int) -> float:
        """Port of Interface.Getdi(row, index).

        Bilinear interpolation of VInt2D.X over the master-element face.
        """
        nrow = max(self.nrow, 1)
        ncol = max(self.ncol, 1)
        xi = -1.0 + 2.0 / ncol * index + 1.0 / ncol
        eta = -1.0 + 2.0 / nrow * row + 1.0 / nrow
        v = self.vint2d
        return (
            v[0].x * (1.0 - xi) * (1.0 - eta) / 4.0
            + v[1].x * (1.0 + xi) * (1.0 - eta) / 4.0
            + v[2].x * (1.0 + xi) * (1.0 + eta) / 4.0
            + v[3].x * (1.0 - xi) * (1.0 + eta) / 4.0
        )

    def get_dj(self, row: int, index: int) -> float:
        """Port of Interface.Getdj(row, index) = Length - Getdi(row, index)."""
        return self.length - self.get_di(row, index)

    def get_dm(self, row: int, index: int) -> float:
        """Port of Interface.Getdm(row, index) = 0.5*Length - Getdi(row, index)."""
        return 0.5 * self.length - self.get_di(row, index)

    def geometry_spring(self, row: int, index: int) -> Tuple[float, float, float]:
        """Port of Interface.GeometrySpring(row, index, di, dj, dm)."""
        di = self.get_di(row, index)
        dj = self.get_dj(row, index)
        dm = self.get_dm(row, index)
        return di, dj, dm

    def ecc_spring(self, row: int, index: int) -> float:
        """Port of Interface.EccSpring(row, index).

        Bilinear interpolation of VInt2D.Y over the master-element face.
        """
        nrow = max(self.nrow, 1)
        ncol = max(self.ncol, 1)
        xi = -1.0 + 2.0 / ncol * index + 1.0 / ncol
        eta = -1.0 + 2.0 / nrow * row + 1.0 / nrow
        v = self.vint2d
        return (
            v[0].y * (1.0 - xi) * (1.0 - eta) / 4.0
            + v[1].y * (1.0 + xi) * (1.0 - eta) / 4.0
            + v[2].y * (1.0 + xi) * (1.0 + eta) / 4.0
            + v[3].y * (1.0 - xi) * (1.0 + eta) / 4.0
        )

    # ── ComputeDistSpring (two overloads) ───────────────────────────────────

    def compute_dist_spring(self) -> Tuple[float, float]:
        """Compute distance distribution factors *di*, *dj*.

        Port of ``ComputeDistSpring(out double di, out double dj)``
        (the parameterless overload that uses *this*).
        """
        di = self._compute_di_from_geometry(self)
        dj = 1.0 - di
        return di, dj

    def compute_dist_spring_for(self, intf: Interface) -> Tuple[float, float]:
        """Port of ``ComputeDistSpring(Interface I, ref double di, ref double dj)``.

        The protected virtual overload that takes an explicit Interface argument.
        If either parent is Fiber and the other is not, *di* = 0.5.
        """
        is_fiber1 = self.parent_type_element1 == "Fiber"
        is_fiber2 = self.parent_type_element2 == "Fiber"
        if (is_fiber1 and not is_fiber2) or (is_fiber2 and not is_fiber1):
            di = 0.5
        else:
            di = self._compute_di_from_geometry(intf)
        dj = 1.0 - di
        return di, dj

    def _compute_di_from_geometry(self, intf: Interface) -> float:
        """Helper: compute *di* from plate theory (port of the else-branch).

        Uses ``intf.thickness[0]`` and ``intf.length``.
        """
        t = intf.thickness[0]
        L = intf.length
        num = min(t, L)
        num2 = max(t, L)
        if num <= 0.0:
            return 0.5
        x_val = 3.0 * num2 / (num * (num2 / num - 0.63))
        x_val = math.sqrt(x_val)
        num3 = 2.0 * num / x_val
        return 0.5 - 0.5 * num3 / L

    # ═════════════════════════════════════════════════════════════════════════
    # ComputeK storage  (port of Interface.ComputeK / ComputeKfless / etc.)
    # ═════════════════════════════════════════════════════════════════════════

    def compute_k(self, alfa: float = 0.0) -> None:
        """Port of Interface.ComputeK(double alfa).

        Computes and stores the three stiffness blocks into *status*.
        """
        self._compute_kfless(alfa)
        self._compute_kslid(alfa)
        self._compute_kslid_out_plan(alfa)

    # ── ComputeKflessNoInteract ─────────────────────────────────────────────

    def _compute_kfless(self, alfa: float) -> None:
        """Port of ComputeKflessNoInteract (ComputeKfless for Ngroup == 1).

        Builds the 6×6 (or 4×4 + coupling) flexural stiffness matrix.
        """
        I = self  # alias for readability, matching C# convention
        d0 = I.dim_aff[0] if len(I.dim_aff) > 0 else 6
        K = _list2d(d0, d0) if d0 > 4 else _list2d(6, 6)

        nrow = max(I.nrow, 1)
        ncol = max(I.ncol, 1)

        num = num2 = num3 = 0.0
        for i in range(nrow):
            for j in range(ncol):
                idx_ = I.idx(i, j)
                if idx_ >= len(I.trasv_1):
                    continue
                di = I.get_di(i, j)
                dj = I.get_dj(i, j)
                k = I.trasv_1[idx_].get_k(alfa)
                num += k * di * di
                num3 += k * di * dj
                num2 += k * dj * dj

        L = I.length
        L2 = L * L
        if L2 > 1e-30:
            num /= L2
            num3 /= L2
            num2 /= L2

        constrained = I.interfaccia_vincolata_computed()

        if constrained:
            num4 = num5 = num6 = 0.0
            for i_ in range(ncol):
                for j_ in range(nrow):
                    idx_ = I.idx(j_, i_)
                    if idx_ >= len(I.trasv_1):
                        continue
                    di = I.get_di(j_, i_)
                    dm = I.get_dm(j_, i_)
                    k = I.trasv_1[idx_].get_k(alfa)
                    num4 += k
                    num5 -= k * dm
                    num6 += k * dm * dm
            K[0][0] = num4
            K[0][1] = num5
            K[1][1] = num6
            K[0][2] = -num - num3
            K[0][3] = -num3 - num2
            K[1][2] = num3 * L / 2.0 - num * L / 2.0
            K[1][3] = num2 * L / 2.0 - num3 * L / 2.0
            K[2][2] = num
            K[2][3] = num3
            K[3][3] = num2
        else:
            K[0][0] = num2
            K[0][1] = num3
            K[0][2] = -num3
            K[0][3] = -num2
            K[1][1] = num
            K[1][2] = -num
            K[1][3] = -num3
            K[2][2] = num
            K[2][3] = num3
            K[3][3] = num2

        # Symmetrise upper-left 4×4
        for i_ in range(4):
            for j_ in range(i_ + 1, 4):
                K[j_][i_] = K[i_][j_]

        d2 = I.dim_aff[2] if len(I.dim_aff) > 2 else 4
        if d2 <= 0:
            # Store and return
            self.status.k = K
            return

        # ── Out-of-plane coupling (DOFs 4,5) ────────────────────────────────
        num7 = 0.0
        for i_ in range(ncol):
            for j_ in range(nrow):
                idx_ = I.idx(j_, i_)
                if idx_ >= len(I.trasv_1):
                    continue
                k = I.trasv_1[idx_].get_k(alfa)
                ecc = I.ecc_spring(j_, i_)
                num7 += k * ecc * ecc

        K[4][4] = num7
        K[5][5] = num7
        K[4][5] = -num7
        K[5][4] = -num7

        num7 = 0.0
        num8 = 0.0
        for i_ in range(ncol):
            for j_ in range(nrow):
                idx_ = I.idx(j_, i_)
                if idx_ >= len(I.trasv_1):
                    continue
                k = I.trasv_1[idx_].get_k(alfa)
                di = I.get_di(j_, i_)
                dj = I.get_dj(j_, i_)
                ecc = I.ecc_spring(j_, i_)
                num7 += k * dj * ecc
                num8 += k * di * ecc

        if L > 1e-30:
            num7 /= L
            num8 /= L

        if not constrained:
            K[0][4] = -num7
            K[1][4] = -num8
            K[2][4] = num8
            K[3][4] = num7
            K[0][5] = num7
            K[1][5] = num8
            K[2][5] = -num8
            K[3][5] = -num7
        else:
            K[0][4] = -num7 - num8
            K[1][4] = (-num8 + num7) * L / 2.0
            K[2][4] = num8
            K[3][4] = num7
            K[0][5] = num7 + num8
            K[1][5] = (num8 - num7) * L / 2.0
            K[2][5] = -num8
            K[3][5] = -num7

        # Symmetrise coupling rows
        for i_ in range(4):
            K[4][i_] = K[i_][4]
            K[5][i_] = K[i_][5]

        self.status.k = K

    # ── ComputeKslid ────────────────────────────────────────────────────────

    def _compute_kslid(self, alfa: float) -> None:
        """Port of ComputeKslid — 2×2 in-plane sliding stiffness."""
        d1 = self.dim_aff[1] if len(self.dim_aff) > 1 else 2
        K = _list2d(d1, d1)
        if self.slid:
            k_val = self.slid[0].get_k(alfa)
            K[0][0] = k_val
            K[0][1] = -k_val
            K[1][0] = -k_val
            K[1][1] = k_val
        self.status.kslid = K

    # ── ComputeKslidOutPlan ─────────────────────────────────────────────────

    def _compute_kslid_out_plan(self, alfa: float) -> None:
        """Port of ComputeKslidOutPlan → RotationalSpring branch (default)."""
        d2 = self.dim_aff[2] if len(self.dim_aff) > 2 else 4
        K = _list2d(d2, d2)
        if len(self.slid_out_plan) < 2:
            self.status.kslid_out_plan = K
            return

        # ComputeKslidOutPlanRotationalSpring
        k1 = self.slid_out_plan[0].get_k(alfa) / 4.0
        L2 = self.length * self.length
        k2 = self.slid_out_plan[1].get_k(alfa) / L2 if L2 > 1e-30 else 0.0

        K[0][0] = k1 + k2
        K[0][1] = k1 - k2
        K[0][2] = -(k1 + k2)
        K[0][3] = -(k1 - k2)
        K[1][0] = k1 - k2
        K[1][1] = k1 + k2
        K[1][2] = -(k1 - k2)
        K[1][3] = -(k1 + k2)
        K[2][0] = -(k1 + k2)
        K[2][1] = -(k1 - k2)
        K[2][2] = k1 + k2
        K[2][3] = k1 - k2
        K[3][0] = -(k1 - k2)
        K[3][1] = -(k1 + k2)
        K[3][2] = k1 - k2
        K[3][3] = k1 + k2

        self.status.kslid_out_plan = K

    # ═════════════════════════════════════════════════════════════════════════
    # UpdateDomain  (port of Interface.UpdateDomain)
    # ═════════════════════════════════════════════════════════════════════════

    def update_domain(self, x: np.ndarray, state: Any) -> None:
        """Port of Interface.UpdateDomain(LinearSystem LS, IntegratorState state).

        Updates element-local displacements *U* from the global displacement
        increment *x* (Δu), then computes spring deformations and pushes
        trial strains.
        """
        I = self

        # ── 1. Accumulate U from afference ──────────────────────────────────
        for i in range(I.dim_aff_tot):
            total = 0.0
            if i < len(I.aff):
                for entry in I.aff[i]:
                    g = entry.gdl - 1
                    if 0 <= g < len(x):
                        total += x[g] * entry.alfa
            I.status.u[i] += total

        # ── 2. Compute flexural deformation modes ───────────────────────────
        if not I.interfaccia_vincolata_computed():
            num = (I.status.compute_du(I, x, 3)
                   - I.status.compute_du(I, x, 0))
            num2 = (I.status.compute_du(I, x, 2)
                    - I.status.compute_du(I, x, 1))
        else:
            num = (I.status.compute_du(I, x, 3)
                   - (I.status.compute_du(I, x, 0)
                      - I.status.compute_du(I, x, 1) * (I.length / 2.0)))
            num2 = (I.status.compute_du(I, x, 2)
                    - (I.status.compute_du(I, x, 0)
                       + I.status.compute_du(I, x, 1) * (I.length / 2.0)))

        num3 = I.status.compute_du(I, x, 4)
        num4 = I.status.compute_du(I, x, 5)

        # ── 3. Update transversal springs ───────────────────────────────────
        for i_ in range(I.nrow):
            for j_ in range(I.ncol):
                idx_ = I.idx(i_, j_)
                if idx_ >= len(I.trasv_1):
                    continue
                di = I.get_di(i_, j_)
                dj = I.get_dj(i_, j_)
                ecc = I.ecc_spring(i_, j_)
                du_spring = (num * dj + num2 * di) / I.length - (num4 - num3) * ecc
                I.trasv_1[idx_].u += du_spring
                I.trasv_1[idx_].set_trial_strain(I.trasv_1[idx_].u)

        # ── 4. Update in-plane sliding spring ───────────────────────────────
        d0 = I.dim_aff[0] if len(I.dim_aff) > 0 else 6
        i3 = d0
        i4 = d0 + 1
        du_slid = (I.status.compute_du(I, x, i3)
                   - I.status.compute_du(I, x, i4))
        if I.slid:
            I.slid[0].u += du_slid
            I.slid[0].set_trial_strain(I.slid[0].u)

        # ── 5. Update out-of-plane sliding springs ──────────────────────────
        d1 = I.dim_aff[1] if len(I.dim_aff) > 1 else 2
        i3 = d0 + d1
        i4 = d0 + d1 + 2
        du_op_a = (I.status.compute_du(I, x, i3)
                   - I.status.compute_du(I, x, i4))
        i3 = d0 + d1 + 1
        i4 = d0 + d1 + 3
        du_op_b = (I.status.compute_du(I, x, i3)
                   - I.status.compute_du(I, x, i4))

        di_sop, dj_sop = I.compute_dist_spring_for(I)
        if len(I.slid_out_plan) >= 2:
            I.slid_out_plan[0].u += du_op_a + (du_op_b - du_op_a) * di_sop
            I.slid_out_plan[1].u += du_op_a + (du_op_b - du_op_a) * dj_sop
            I.slid_out_plan[0].set_trial_strain(I.slid_out_plan[0].u)
            I.slid_out_plan[1].set_trial_strain(I.slid_out_plan[1].u)

    # ═════════════════════════════════════════════════════════════════════════
    # SetResistingForce  (port of Interface.SetResistingForce)
    # ═════════════════════════════════════════════════════════════════════════

    def set_resisting_force(self) -> None:
        """Port of Interface.SetResistingForce().

        Computes the local 12-DOF resisting force vector *F* from spring
        forces and stores it in ``self.f``.
        """
        # Zero the local force vector
        for i in range(12):
            self.f[i] = 0.0

        constrained = self.interfaccia_vincolata_computed()

        # ── Transversal springs (Trasv_1) → DOFs 0..5 ───────────────────────
        for i in range(self.nrow):
            for j in range(self.ncol):
                idx_ = self.idx(i, j)
                if idx_ >= len(self.trasv_1):
                    continue
                spring_force = self.trasv_1[idx_].get_force()
                dj = self.get_dj(i, j)
                di = self.get_di(i, j)
                L = self.length

                if not constrained:
                    self.f[3] += spring_force * dj / L
                    self.f[2] += spring_force * di / L
                    self.f[0] += -spring_force * dj / L
                    self.f[1] += -spring_force * di / L
                else:
                    self.f[3] += spring_force * dj / L
                    self.f[2] += spring_force * di / L
                    self.f[0] += -spring_force * di / L - spring_force * dj / L
                    self.f[1] += 0.5 * L * (spring_force * dj / L - spring_force * di / L)

                ecc = self.ecc_spring(i, j)
                self.f[4] += spring_force * ecc
                self.f[5] += -spring_force * ecc

        # ── In-plane sliding → DOFs 6,7 ─────────────────────────────────────
        if self.slid:
            slid_force = self.slid[0].get_force()
            self.f[6] += slid_force
            self.f[7] += -slid_force

        # ── Out-of-plane sliding → DOFs 8..11 ───────────────────────────────
        if len(self.slid_out_plan) >= 2:
            di, dj = self.compute_dist_spring()
            sop0_force = self.slid_out_plan[0].get_force()
            sop1_force = self.slid_out_plan[1].get_force()
            self.f[8] += dj * sop0_force + di * sop1_force
            self.f[9] += di * sop0_force + dj * sop1_force
            self.f[10] -= dj * sop0_force + di * sop1_force
            self.f[11] -= di * sop0_force + dj * sop1_force

    # ═════════════════════════════════════════════════════════════════════════
    # GetResistingForce global scatter  (port of Interface.GetResistingForce)
    # ═════════════════════════════════════════════════════════════════════════

    def get_resisting_force(self, ls: Any) -> None:
        """Port of Interface.GetResistingForce(LinearSystem A).

        Computes the local resisting force array then scatters it into the
        global residual vector ``ls.b`` (with negative sign, as in the C#
        port).
        """
        # Local force array of size DimAffTot
        arr = [0.0] * self.dim_aff_tot

        constrained = self.interfaccia_vincolata_computed()

        # ── Transversal springs ─────────────────────────────────────────────
        for i in range(self.nrow):
            for j in range(self.ncol):
                idx_ = self.idx(i, j)
                if idx_ >= len(self.trasv_1):
                    continue
                spring_force = self.trasv_1[idx_].get_force()
                dj = self.get_dj(i, j)
                di = self.get_di(i, j)
                L = self.length

                if not constrained:
                    arr[3] += spring_force * dj / L
                    arr[2] += spring_force * di / L
                    arr[0] += -spring_force * dj / L
                    arr[1] += -spring_force * di / L
                else:
                    arr[3] += spring_force * dj / L
                    arr[2] += spring_force * di / L
                    arr[0] += -spring_force * di / L - spring_force * dj / L
                    arr[1] += 0.5 * L * (spring_force * dj / L - spring_force * di / L)

                ecc = self.ecc_spring(i, j)
                arr[4] += spring_force * ecc
                arr[5] += -spring_force * ecc

        # ── In-plane sliding ────────────────────────────────────────────────
        if self.slid:
            slid_force = self.slid[0].get_force()
            arr[6] += slid_force
            arr[7] += -slid_force

        # ── Out-of-plane sliding ────────────────────────────────────────────
        if len(self.slid_out_plan) >= 2:
            di, dj = self.compute_dist_spring()
            sop0_force = self.slid_out_plan[0].get_force()
            sop1_force = self.slid_out_plan[1].get_force()
            arr[8] += dj * sop0_force + di * sop1_force
            arr[9] += di * sop0_force + dj * sop1_force
            arr[10] -= dj * sop0_force + di * sop1_force
            arr[11] -= di * sop0_force + dj * sop1_force

        # ── Scatter to global via afference (with negative sign) ────────────
        for i in range(self.dim_aff_tot):
            if i >= len(self.aff):
                continue
            for entry in self.aff[i]:
                g = entry.gdl - 1
                if 0 <= g < ls.n:
                    ls.b[g] += (-arr[i]) * entry.alfa

    # ═════════════════════════════════════════════════════════════════════════
    # Commit  (port of Interface.Commit)
    # ═════════════════════════════════════════════════════════════════════════

    def commit(self, ls: Any = None) -> None:
        """Port of Interface.Commit().

        Commits all spring states (trial → committed).
        The *ls* argument is accepted for interface compatibility with the
        solver but is not used (C# Commit has no LS parameter).
        """
        for s in self.trasv_1:
            if hasattr(s, 'commit'):
                s.commit()
        for s in self.slid:
            if hasattr(s, 'commit'):
                s.commit()
        for s in self.slid_out_plan:
            if hasattr(s, 'commit'):
                s.commit()

    # ═════════════════════════════════════════════════════════════════════════
    # revertToLastCommit  (port of Interface.revertToLastCommit)
    # ═════════════════════════════════════════════════════════════════════════

    def revert_to_last_commit(self, ls: Any) -> None:
        """Port of Interface.revertToLastCommit(LinearSystem LS).

        Reverts *Status.U* using the displacement increment stored in
        *ls.x* (which at this point contains *u_committed - u*, i.e. the
        negative of the current increment), then calls
        ``RevertToLastCommit`` on each spring.
        """
        I = self
        x = ls.x if hasattr(ls, 'x') else ls  # accept both LS and raw array

        # Revert Status.U using the negative increment
        for i in range(I.dim_aff_tot):
            if i >= len(I.aff):
                continue
            total = 0.0
            for entry in I.aff[i]:
                g = entry.gdl - 1
                if 0 <= g < len(x):
                    total += x[g] * entry.alfa
            I.status.u[i] += total

        # Revert springs
        for s in I.trasv_1:
            if hasattr(s, 'revert_to_last_commit'):
                s.revert_to_last_commit()
        for s in I.slid:
            if hasattr(s, 'revert_to_last_commit'):
                s.revert_to_last_commit()
        for s in I.slid_out_plan:
            if hasattr(s, 'revert_to_last_commit'):
                s.revert_to_last_commit()

    # ═════════════════════════════════════════════════════════════════════════
    # max_u / compute_energy  (convenience stubs matching solver expectations)
    # ═════════════════════════════════════════════════════════════════════════

    def max_u(self) -> float:
        """Maximum absolute spring displacement (port of a common pattern)."""
        mx = 0.0
        for s in self.trasv_1:
            mx = max(mx, abs(getattr(s, 'u', 0.0)))
        for s in self.slid:
            mx = max(mx, abs(getattr(s, 'u', 0.0)))
        for s in self.slid_out_plan:
            mx = max(mx, abs(getattr(s, 'u', 0.0)))
        return mx

    def compute_energy(self) -> Tuple[float, float, float]:
        """Port of Interface.ComputeEnergy.

        Returns (elastic, plastic, total) energy summed over all springs.
        """
        e_el = e_pl = e_tot = 0.0
        for s in self.trasv_1:
            if hasattr(s, 'compute_energy'):
                de_el, de_pl, de_tot = s.compute_energy()
                e_el += de_el
                e_pl += de_pl
                e_tot += de_tot
            else:
                e_tot += 0.5 * getattr(s, 'k', 0.0) * getattr(s, 'u', 0.0) ** 2
                e_el = e_tot
        for s in self.slid:
            if hasattr(s, 'compute_energy'):
                de_el, de_pl, de_tot = s.compute_energy()
                e_el += de_el
                e_pl += de_pl
                e_tot += de_tot
            else:
                e_tot += 0.5 * getattr(s, 'k', 0.0) * getattr(s, 'u', 0.0) ** 2
        for s in self.slid_out_plan:
            if hasattr(s, 'compute_energy'):
                de_el, de_pl, de_tot = s.compute_energy()
                e_el += de_el
                e_pl += de_pl
                e_tot += de_tot
            else:
                e_tot += 0.5 * getattr(s, 'k', 0.0) * getattr(s, 'u', 0.0) ** 2
        return e_el, e_pl, e_tot

    @classmethod
    def from_xml(cls, elem) -> Interface:
        intf = cls()
        intf.key = int(elem.get("Key", "0"))
        intf.name = elem.get("Name", "")
        intf.parent_element_key1 = int(elem.get("ParentElementKey1", "0"))
        intf.parent_element_key2 = int(elem.get("ParentElementKey2", "0"))
        intf.parent_type_element1 = elem.get("ParentTypeElement1", "")
        intf.parent_type_element2 = elem.get("ParentTypeElement2", "")
        intf.face1 = int(elem.get("Face1", "0"))
        intf.face2 = int(elem.get("Face2", "0"))
        intf.length = float(elem.get("Length", "0"))
        intf.material_key = int(elem.get("MaterialKey", "0"))
        intf.layer_key = int(elem.get("LayerKey", "0"))
        intf.nrow = int(elem.get("Nrow", "3"))
        # In the .NET reference, Nspring and Ncol share the same backing field (`_ncol`).
        # The XML serializes the field once (typ= "Nspring"), so we read Nspring first
        # and only fall back to a "Ncol" attribute if explicitly present.
        ns = elem.get("Nspring")
        nc = elem.get("Ncol")
        if nc is not None:
            intf.ncol = int(nc)
        elif ns is not None:
            intf.ncol = int(ns)
        else:
            intf.ncol = 3
        intf.nspring = intf.ncol  # kept for parity with .NET (alias)
        intf.dim_aff = [
            int(elem.get("DimAff1", "6")),
            int(elem.get("DimAff2", "2")),
            int(elem.get("DimAff3", "4")),
        ]
        intf.dim_aff_tot = int(elem.get("DimAffTot", "12"))
        intf.frot = int(elem.get("Frot", "0"))
        intf.imax = int(elem.get("Imax", "400"))
        intf.csi = float(elem.get("Csi", "0"))
        intf.interfaccia_vincolata = elem.get("InterfacciaVincolata", "false") == "true"

        for i in range(2):
            intf.node_keys[i] = int(elem.get(f"NodeKey{i+1}", "0"))

        tstr = elem.get("Thickness1", None)
        if tstr is not None:
            intf.thickness[0] = float(tstr)
        tstr = elem.get("Thickness2", None)
        if tstr is not None:
            intf.thickness[1] = float(tstr)

        # VInt2D and VInt3D
        for i in range(4):
            v2d = elem.get(f"VInt2D{i+1}", None)
            if v2d:
                intf.vint2d[i] = Point.from_str(v2d)
            v3d = elem.get(f"VInt3D{i+1}", None)
            if v3d:
                intf.vint3d[i] = Point.from_str(v3d)

        # Springs
        from histra.springs.registry import spring_from_xml
        trasv1 = elem.find("Trasv1")
        if trasv1 is not None:
            for sp in trasv1.findall("Spring"):
                intf.trasv_1.append(spring_from_xml(sp))
        trasv2 = elem.find("Trasv2")
        if trasv2 is not None:
            for sp in trasv2.findall("Spring"):
                intf.trasv_2.append(spring_from_xml(sp))
        slid = elem.find("Slid")
        if slid is not None:
            for sp in slid.findall("Spring"):
                intf.slid.append(spring_from_xml(sp))
        sop = elem.find("SlidOutPlan")
        if sop is not None:
            for sp in sop.findall("Spring"):
                intf.slid_out_plan.append(spring_from_xml(sp))

        # AfferenceMatrices
        aff_elem = elem.find("AfferenceMatrices")
        if aff_elem is not None:
            mats = aff_elem.findall("AfferenceMatrix")
            for idx, m in enumerate(mats):
                if idx >= 12:
                    break
                alfa_items = m.find("Alfa")
                gdl_items = m.find("Gdl")
                if alfa_items is not None and gdl_items is not None:
                    alfas = [float(a.get("Value", "0")) for a in alfa_items.findall("item")]
                    gdls = [int(g.get("Value", "0")) for g in gdl_items.findall("item")]
                    intf.aff[idx] = [AfferenceEntry(gdl=g, alfa=a) for a, g in zip(alfas, gdls)]

        # ReferenceSystem
        rs = elem.find("ReferenceSystem")
        if rs is not None:
            e1 = rs.get("E1", "1;0;0")
            e2 = rs.get("E2", "0;1;0")
            e3 = rs.get("E3", "0;0;1")
            intf.reference_e1 = tuple(float(x) for x in e1.split(";"))
            intf.reference_e2 = tuple(float(x) for x in e2.split(";"))
            intf.reference_e3 = tuple(float(x) for x in e3.split(";"))
            orig = rs.get("Origin", None)
            if orig:
                intf.reference_origin = Point.from_str(orig)

        return intf
