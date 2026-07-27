"""
Global stiffness matrix and load vector assembly.

Maps .NET HiStrA element assembly into COO / CSC format for scipy.
"""
from __future__ import annotations

import numpy as np
import scipy.sparse as sp
from typing import List, Set, Tuple

from histra.model.model import Model
from histra.model.quad import Quad
from histra.model.interface import Interface
from histra.model._types import AfferenceEntry


# ── Interface stiffness helpers ──────────────────────────────────────────────

def _intf_get_di(intf: Interface, row: int, index: int) -> float:
    """Port of Interface.Getdi(row, index): bilinear interpolation of vInt2D.X.

    `row` cycles over Nrow, `index` over Ncol.  In the .NET code, the local
    coordinates (xi, eta) are:
        xi = -1 + 2/Ncol * index + 1/Ncol      (in [-1, 1] across Ncol)
        eta = -1 + 2/Nrow * row  + 1/Nrow        (in [-1, 1] across Nrow)
    """
    nrow = intf.nrow if intf.nrow > 0 else 1
    ncol = intf.ncol if intf.ncol > 0 else 1
    xi = -1.0 + 2.0 / ncol * index + 1.0 / ncol
    eta = -1.0 + 2.0 / nrow * row + 1.0 / nrow
    v = intf.vint2d  # [Point]×4
    return (
        v[0].x * (1.0 - xi) * (1.0 - eta) / 4.0
        + v[1].x * (1.0 + xi) * (1.0 - eta) / 4.0
        + v[2].x * (1.0 + xi) * (1.0 + eta) / 4.0
        + v[3].x * (1.0 - xi) * (1.0 + eta) / 4.0
    )


def _intf_get_dj(intf: Interface, row: int, index: int) -> float:
    """Port of Interface.Getdj(row, index) = Length - Getdi(row, index)."""
    return intf.length - _intf_get_di(intf, row, index)


def _intf_get_dm(intf: Interface, row: int, index: int) -> float:
    """Port of Interface.Getdm(row, index) = 0.5*Length - Getdi(row, index)."""
    return 0.5 * intf.length - _intf_get_di(intf, row, index)


def _intf_ecc_spring(intf: Interface, row: int, index: int) -> float:
    """Port of Interface.EccSpring(row, index): bilinear interpolation of vInt2D.Y."""
    nrow = intf.nrow if intf.nrow > 0 else 1
    ncol = intf.ncol if intf.ncol > 0 else 1
    xi = -1.0 + 2.0 / ncol * index + 1.0 / ncol
    eta = -1.0 + 2.0 / nrow * row + 1.0 / nrow
    v = intf.vint2d  # [Point]×4
    return (
        v[0].y * (1.0 - xi) * (1.0 - eta) / 4.0
        + v[1].y * (1.0 + xi) * (1.0 - eta) / 4.0
        + v[2].y * (1.0 + xi) * (1.0 + eta) / 4.0
        + v[3].y * (1.0 - xi) * (1.0 + eta) / 4.0
    )


def _compute_interface_kfless(intf: Interface, alfa: float = 0.0) -> List[List[float]]:
    """Build the 6×6 flexural stiffness matrix (port of ComputeKflessNoInteract).

    Uses bilinear shape-function interpolation over `_vInt2D` corner points
    to obtain di, dj, dm (geometry) and eccentricity (EccSpring) for each
    integration-point spring on the Nrow×Ncol grid.
    """
    k = [[0.0] * 6 for _ in range(6)]
    nrow = intf.nrow if intf.nrow > 0 else 1
    ncol = intf.ncol if intf.ncol > 0 else 1

    def idx(i: int, j: int) -> int:
        return i * ncol + j

    num, num2, num3 = 0.0, 0.0, 0.0
    for i in range(nrow):
        for j in range(ncol):
            if idx(i, j) >= len(intf.trasv_1):
                continue
            di = _intf_get_di(intf, i, j)
            dj = _intf_get_dj(intf, i, j)
            # dm is recomputed below via GeometrySpring. Reference dm = 0.5*Length - di.
            ks = intf.trasv_1[idx(i, j)].get_k(alfa)
            num += ks * di * di
            num3 += ks * di * dj
            num2 += ks * dj * dj

    dm = intf.length * intf.length
    if dm > 1e-30:
        num /= dm
        num3 /= dm
        num2 /= dm

    constrained = intf.interfaccia_vincolata_computed()

    if constrained:
        # InterfacciaVincolata() branch
        num4, num5, num6 = 0.0, 0.0, 0.0
        for i in range(ncol):
            for j in range(nrow):
                # GeometrySpring(j, i)
                di = _intf_get_di(intf, j, i)
                # dm
                dmx = _intf_get_dm(intf, j, i)
                ks = intf.trasv_1[idx(j, i)].get_k(alfa)
                num4 += ks
                num5 -= ks * dmx
                num6 += ks * dmx * dmx
        k[0][0] = num4
        k[0][1] = num5
        k[1][1] = num6
        k[0][2] = -num - num3
        k[0][3] = -num3 - num2
        k[1][2] = num3 * intf.length / 2.0 - num * intf.length / 2.0
        k[1][3] = num2 * intf.length / 2.0 - num3 * intf.length / 2.0
        k[2][2] = num
        k[2][3] = num3
        k[3][3] = num2
    else:
        # Most common non-constrained interface
        k[0][0] = num2
        k[0][1] = num3
        k[0][2] = -num3
        k[0][3] = -num2
        k[1][1] = num
        k[1][2] = -num
        k[1][3] = -num3
        k[2][2] = num
        k[2][3] = num3
        k[3][3] = num2

    # Symmetrize the 4×4 upper-left block
    for i in range(4):
        for j in range(i + 1, 4):
            k[j][i] = k[i][j]

    if intf.dim_aff[2] <= 0:
        return k

    # Residual DOFs 4,5 — match reference (ComputeKflessNoInteract tail)
    num7 = 0.0
    for i in range(ncol):
        for j in range(nrow):
            if idx(j, i) >= len(intf.trasv_1):
                continue
            ks = intf.trasv_1[idx(j, i)].get_k(alfa)
            ecc = _intf_ecc_spring(intf, j, i)
            num7 += ks * ecc * ecc
    k[4][4] = num7
    k[5][5] = num7
    k[4][5] = -num7
    k[5][4] = -num7

    # coupling terms K[0..3,4] and K[0..3,5]
    num7 = 0.0
    num8 = 0.0
    for i in range(ncol):
        for j in range(nrow):
            if idx(j, i) >= len(intf.trasv_1):
                continue
            ks = intf.trasv_1[idx(j, i)].get_k(alfa)
            di = _intf_get_di(intf, j, i)
            dj = _intf_get_dj(intf, j, i)
            ecc = _intf_ecc_spring(intf, j, i)
            num7 += ks * dj * ecc
            num8 += ks * di * ecc
    L = intf.length
    if L > 1e-30:
        num7 /= L
        num8 /= L

    if not constrained:
        k[0][4] = -num7
        k[1][4] = -num8
        k[2][4] = num8
        k[3][4] = num7
        k[0][5] = num7
        k[1][5] = num8
        k[2][5] = -num8
        k[3][5] = -num7
    else:
        k[0][4] = -num7 - num8
        k[1][4] = (-num8 + num7) * L / 2.0
        k[2][4] = num8
        k[3][4] = num7
        k[0][5] = num7 + num8
        k[1][5] = (num8 - num7) * L / 2.0
        k[2][5] = -num8
        k[3][5] = -num7

    # Symmetrize K[i,4..5] vs K[4..5,i]
    for i in range(4):
        k[4][i] = k[i][4]
        k[5][i] = k[i][5]

    return k


def _compute_interface_kslid(intf: Interface, alfa: float = 0.0) -> List[List[float]]:
    """2×2 sliding stiffness (port of ComputeKslid)."""
    k_val = intf.slid[0].get_k(alfa) if intf.slid else 0.0
    return [[k_val, -k_val], [-k_val, k_val]]


def _compute_interface_kslid_op(intf: Interface, alfa: float = 0.0) -> List[List[float]]:
    """Out-of-plane stiffness using the C# model's active ``TwoSprings`` branch."""
    d2 = intf.dim_aff[2] if len(intf.dim_aff) > 2 else 4
    intf._compute_kslid_out_plan(alfa)
    return [row[:] for row in intf.status.kslid_out_plan[:d2]]


# ── Assembly helpers ────────────────────────────────────────────────────────

def _assemble_afference(
    rows: list, cols: list, vals: list,
    n: int,
    aff_i: List[AfferenceEntry],
    aff_j: List[AfferenceEntry],
    k_ij: float,
):
    """Scatter local stiffness k_ij through afference matrices into global COO."""
    if abs(k_ij) < 1e-30:
        return
    for ei in aff_i:
        gi = ei.gdl - 1
        if gi < 0 or gi >= n:
            continue
        for ej in aff_j:
            gj = ej.gdl - 1
            if gj < 0 or gj >= n:
                continue
            v = k_ij * ei.alfa * ej.alfa
            if abs(v) < 1e-30:
                continue
            rows.append(gi)
            cols.append(gj)
            vals.append(v)


# ── Public API ──────────────────────────────────────────────────────────────

def assemble_global_k(model: Model, alfa: float = 0.0) -> sp.csc_matrix:
    """
    Assemble the global stiffness matrix K (CSC format).

    Includes contributions from:
      - Quad diagonal (Aff[6]) — scalar stiffness * alfa_i * alfa_j
      - Interface flexural (DimAff[0]×DimAff[0] block) via Trasv_1 springs
      - Interface sliding (DimAff[1]×DimAff[1] block) via Slid springs
      - Interface out-of-plane (DimAff[2]×DimAff[2] block) via SlidOutPlan springs
    """
    n = model.gdl
    rows, cols, vals = [], [], []

    # ── Quad contributions ──
    for quad in model.collections.quads.values():
        quad.compute_k(alfa)
        k_scalar = quad.status.k
        if not quad.aff or len(quad.aff) <= 6:
            continue
        aff6 = quad.aff[6]
        if not aff6:
            continue
        for ei in aff6:
            gi = ei.gdl - 1
            for ej in aff6:
                gj = ej.gdl - 1
                v = k_scalar * ei.alfa * ej.alfa
                if abs(v) > 1e-30:
                    rows.append(gi)
                    cols.append(gj)
                    vals.append(v)

    # ── Interface contributions ──
    dim0 = 6  # typical flexural DOF count
    dim1 = 2  # typical sliding DOF count
    dim2 = 4  # typical out-of-plane DOF count

    for intf in model.collections.interfaces.values():
        d0 = intf.dim_aff[0] if len(intf.dim_aff) > 0 else dim0
        d1 = intf.dim_aff[1] if len(intf.dim_aff) > 1 else dim1
        d2 = intf.dim_aff[2] if len(intf.dim_aff) > 2 else dim2

        # Flexural block
        k_flex = _compute_interface_kfless(intf, alfa)
        for i in range(d0):
            for j in range(d0):
                k_ij = k_flex[i][j]
                if i < len(intf.aff) and j < len(intf.aff):
                    _assemble_afference(rows, cols, vals, n,
                                        intf.aff[i], intf.aff[j], k_ij)

        # Sliding block
        if intf.slid:
            k_slid = _compute_interface_kslid(intf, alfa)
            for i in range(d1):
                for j in range(d1):
                    ai = d0 + i
                    aj = d0 + j
                    k_ij = k_slid[i][j]
                    if ai < len(intf.aff) and aj < len(intf.aff):
                        _assemble_afference(rows, cols, vals, n,
                                            intf.aff[ai], intf.aff[aj], k_ij)

        # Out-of-plane sliding block
        if len(intf.slid_out_plan) >= 2:
            k_sop = _compute_interface_kslid_op(intf, alfa)
            for i in range(d2):
                for j in range(d2):
                    ai = d0 + d1 + i
                    aj = d0 + d1 + j
                    k_ij = k_sop[i][j]
                    if ai < len(intf.aff) and aj < len(intf.aff):
                        _assemble_afference(rows, cols, vals, n,
                                            intf.aff[ai], intf.aff[aj], k_ij)

    K = sp.coo_matrix((vals, (rows, cols)), shape=(n, n)).tocsc()
    return K


def get_restrained_dofs(model: Model, K: Optional[sp.csc_matrix] = None) -> Set[int]:
    """
    Identify DOF indices (0-based) that are fixed.

    1. Explicit restraints from the model (NodeC-based).
    2. Any DOF with zero diagonal stiffness (passive DOFs that carry no
       load and must be removed to avoid a singular system).

    A Restraint with K[i] < 0 means that DOF i is fully fixed.
    """
    restrained: Set[int] = set()

    # ── 1. Explicit restraints ──
    for r in model.collections.restraints.values():
        # Restraint references NodeC objects via node_c_keys
        for nc_key in r.node_c_keys:
            if nc_key == 0 or nc_key not in model.collections.node_c:
                continue
            nc = model.collections.node_c[nc_key]
            node_key = nc.node_key
            if node_key == 0:
                continue
            # Find all quads that reference this node
            for quad in model.collections.quads.values():
                if node_key not in quad.node_keys:
                    continue
                pos = quad.node_keys.index(node_key)
                if pos > 1:
                    # Only diagonal nodes (pos 0 or 1) have direct DOFs
                    continue
                # Map restraint DOFs to quad DOFs based on node position
                # pos=0 → aff[0..2], pos=1 → aff[3..5]
                dof_offset = pos * 3
                for i in range(3):  # U1, U2, U3 only (ignore rotational K[3..5])
                    if i < len(r.k) and r.k[i] < 0:
                        for entry in quad.aff[dof_offset + i]:
                            restrained.add(entry.gdl - 1)

    # ── 2. Zero-diagonal DOFs (no stiffness contribution) ──
    if K is not None and K.nnz > 0:
        diag = K.diagonal()
        for dof in range(K.shape[0]):
            if abs(diag[dof]) < 1e-30:
                restrained.add(dof)

    return restrained


def apply_boundary_conditions(
    K: sp.csc_matrix,
    b: np.ndarray,
    fixed_dofs: Set[int],
) -> Tuple[sp.csc_matrix, np.ndarray]:
    """
    Eliminate fixed DOFs from the system (row/col deletion).

    Returns reduced K and b.
    """
    if not fixed_dofs:
        return K, b
    n = K.shape[0]
    free = sorted(set(range(n)) - fixed_dofs)
    K_free = K[np.ix_(free, free)]
    b_free = b[free]
    return K_free, b_free


# ── Load generation ──────────────────────────────────────────────────────────


def _get_comb_coeff_gravity(model: Model, analysis_key: int, combination: int) -> float:
    """
    Port of GetCombCoeffGravity: read gravity coefficient from load combination.

    Returns the scalar multiplier for self-weight loads.
    """
    an = model.collections.analyses.get(analysis_key)
    if an is None:
        raise KeyError(f"Analysis {analysis_key} is not present in the model")

    lc = model.collections.load_combinations.get(an.load_combination_key)
    if lc is None:
        raise KeyError(
            f"Load combination {an.load_combination_key} for analysis {analysis_key} is missing"
        )

    # Find gravity load condition (Action == 1)
    gravity_lc = None
    for cond in model.collections.load_conditions.values():
        if cond.is_gravity():
            gravity_lc = cond
            break
    if gravity_lc is None:
        raise NotImplementedError(
            f"Analysis {analysis_key} has no gravity load condition (Action == 1); "
            "non-gravity load generation is not implemented"
        )

    # Look up the coefficient item for this condition at the given combination (row)
    item = lc.get_coefficient(combination, gravity_lc.id)
    if item is None:
        raise KeyError(
            f"Load combination {lc.key} has no row {combination} coefficient "
            f"for gravity condition {gravity_lc.id}"
        )

    # Resolve the coefficient value based on TypeData
    coeff = _resolve_coefficient(item, gravity_lc)
    return coeff


def _resolve_coefficient(item: "LoadCombinationItem", lc: "LoadCondition") -> float:
    """Port of LoadTemplateManager.GetCoefficient for a single item + condition."""
    td = item.type_data
    if td == "Number":
        return item.val
    if td == "GammaFavSTR":
        return lc.gamma_fav_str
    if td == "GammaUnfavSTR":
        return lc.gamma_unfav_str
    if td == "GammaFavGEO":
        return lc.gamma_fav_geo
    if td == "GammaUnfavGEO":
        return lc.gamma_unfav_geo
    if td in {
        "Psi0", "Psi1", "Psi2",
        "GammaFavSTR_Psi0", "GammaUnfavSTR_Psi0",
        "GammaFavGEO_Psi0", "GammaUnfavGEO_Psi0",
    }:
        raise NotImplementedError(
            f"Combination coefficient {td} requires Psi values from the C# "
            "LoadTemplateItem model, which is not present in this Python snapshot."
        )
    raise NotImplementedError(
        f"Unsupported load-combination coefficient type: {td}"
    )


def generate_self_weight_loads(model: Model, analysis_key: int, combination: int = 1):
    """
    Port of GenerateLoadsForceAnalysis for self-weight only.

    Computes P[0..6] for each Quad from its self-weight and stores
    it in quad.status.p.
    """
    an = model.collections.analyses.get(analysis_key)
    if an is None:
        raise KeyError(f"Analysis {analysis_key} is not present in the model")

    coeff = _get_comb_coeff_gravity(model, analysis_key, combination)
    if abs(coeff) < 1e-30:
        return

    # Direction: for non-seismic, use (0, 0, -1); for seismic, use dir from analysis
    if an.is_seismic:
        dir_vec = (float(an.dir_x), float(an.dir_y), float(an.dir_z))
    else:
        dir_vec = (0.0, 0.0, -1.0)

    dx, dy, dz = dir_vec[0] * coeff, dir_vec[1] * coeff, dir_vec[2] * coeff

    for quad in model.collections.quads.values():
        # Zero P
        for j in range(7):
            quad.status.p[j] = 0.0

        # Look up material weight
        mat = model.collections.materials.get(quad.material_key)
        if mat is None or abs(mat.w) < 1e-30:
            continue

        # Get node coordinates
        node_coords = []
        for nk in quad.node_keys:
            node = model.collections.nodes.get(nk)
            if node is None:
                break
            node_coords.append(node.point)
        if len(node_coords) != 4:
            continue

        # Compute self-weight nodal forces
        nodal_forces = quad.compute_self_weight_load(dx, dy, dz, mat.w)

        # Compute P from shape-function integration
        p = quad.compute_static_load_internal(node_coords, nodal_forces)
        for j in range(7):
            quad.status.p[j] += p[j]


def assemble_load_vector(model: Model, analysis_key: int | None = None, combination: int = 1) -> np.ndarray:
    """
    Assemble the global load vector b.

    If analysis_key is given, first generates self-weight loads.
    Then distributes element P[i] through afference matrices.
    """
    if analysis_key is not None:
        generate_self_weight_loads(model, analysis_key, combination)

    n = model.gdl
    b = np.zeros(n)

    for quad in model.collections.quads.values():
        for i in range(7):
            pi = quad.status.p[i] if i < len(quad.status.p) else 0.0
            if abs(pi) < 1e-30:
                continue
            if i < len(quad.aff):
                for entry in quad.aff[i]:
                    gi = entry.gdl - 1
                    if 0 <= gi < n:
                        b[gi] += pi * entry.alfa

    return b


def extract_displacements(
    model: Model,
    results_path: "str | None" = None,
    analysis_key: int = 1,
    combination: int = 1,
    step: "int | None" = None,
) -> np.ndarray:
    """
    Extract the full displacement vector u from the model state.

    If `results_path` is given (a path to a .Results SQLite DB), read Quad U1..U7
    for the specified (analysis, combination, step) and place them at the correct
    global DOF positions.  If `step` is None, the LAST stored step is used.

    Otherwise, fall back to the post-solve state attached to the parsed Model
    (Quad.status.u read from the .hrx XML).
    """
    n = model.gdl
    u = np.zeros(n)

    if results_path is not None:
        from histra.io.results_reader import read_quad_states
        sql_u = read_quad_states(results_path, analysis_key, combination, step)
        for quad_key, quad_state in sql_u.items():
            if quad_key not in model.collections.quads:
                continue
            quad = model.collections.quads[quad_key]
            quad_u = quad_state.u if hasattr(quad_state, "u") else quad_state
            for i in range(7):
                if i < len(quad.aff) and quad.aff[i]:
                    gdl = quad.aff[i][0].gdl - 1
                    if 0 <= gdl < n:
                        u[gdl] = quad_u[i]
        return u

    for quad in model.collections.quads.values():
        for i in range(7):
            if i < len(quad.aff) and quad.aff[i]:
                # Take the first afference entry as the primary DOF
                gdl = quad.aff[i][0].gdl - 1
                if 0 <= gdl < n:
                    u[gdl] = quad.status.u[i] if i < len(quad.status.u) else 0.0
    return u
