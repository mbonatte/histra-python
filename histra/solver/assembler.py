"""
Global stiffness matrix and load vector assembly.

Maps .NET HiStrA element assembly into COO / CSC format for scipy.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional, Set, Tuple

import numpy as np
import scipy.sparse as sp

try:
    from numba import njit
except Exception:  # pragma: no cover - optional acceleration
    njit = None

from histra.model.model import Model
from histra.model.quad import Quad
from histra.model.interface import Interface
from histra.model._types import AfferenceEntry
from histra.solver.load_assembly import (
    _get_comb_coeff_gravity,
    _get_load_template_coefficient,
    _resolve_coefficient,
    assemble_load_vector,
    extract_displacements,
    generate_line_loads,
    generate_self_weight_loads,
)


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

def _assemble_global_k_legacy(
    model: Model,
    alfa: float = 0.0,
    *,
    recompute_elements: bool = True,
) -> sp.csc_matrix:
    """
    Assemble the global stiffness matrix K (CSC format).

    Includes contributions from:
      - Quad diagonal (Aff[6]) — scalar stiffness * alfa_i * alfa_j
      - Interface flexural (DimAff[0]×DimAff[0] block) via Trasv_1 springs
      - Interface sliding (DimAff[1]×DimAff[1] block) via Slid springs
      - Interface out-of-plane (DimAff[2]×DimAff[2] block) via SlidOutPlan springs

    When ``recompute_elements`` is false, assemble the stiffness blocks already
    stored on each element by ``ModelManager.compute_k``. This avoids executing
    every constitutive/geometry stiffness calculation twice in the normal
    ``compute_ktang -> compute_k -> assemble_k`` path while keeping standalone
    assembler behaviour unchanged by default.
    """
    n = model.gdl
    rows, cols, vals = [], [], []

    # ── Quad contributions ──
    for quad in model.collections.quads.values():
        if recompute_elements:
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
        if recompute_elements:
            intf.compute_k(alfa)

        # Flexural block
        k_flex = intf.status.k
        for i in range(d0):
            for j in range(d0):
                k_ij = k_flex[i][j]
                if i < len(intf.aff) and j < len(intf.aff):
                    _assemble_afference(rows, cols, vals, n,
                                        intf.aff[i], intf.aff[j], k_ij)

        # Sliding block
        if intf.slid:
            k_slid = intf.status.kslid
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
            k_sop = intf.status.kslid_out_plan
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


class _AssemblyPlanIncompatible(RuntimeError):
    """Internal signal requesting the exact legacy scatter fallback."""


@dataclass(slots=True)
class _InterfaceAssemblyLayout:
    interface: Interface
    aff_lists: tuple[Any, ...]
    d0: int
    d1: int
    d2: int
    has_slid: bool
    has_out_of_plane: bool


@dataclass(slots=True)
class _StiffnessAssemblyPlan:
    """C#-ordered fixed CSC scatter topology for a prepared model.

    HiStrA C# first maps a fixed symmetric sparse mask, then every AssembleK
    call performs ``Ax[idx] += value`` immediately in element/local-loop order.
    Rebuilding COO triplets and consolidating duplicates changes that floating-
    point accumulation order.  This plan stores the exact contribution stream
    and the target CSC slot for every contribution so nonlinear iterations can
    replay C# assembly without Python object traversal.
    """

    n: int
    all_quads: tuple[Quad, ...]
    quad_terms: tuple[tuple[Quad, Any], ...]
    interfaces: tuple[_InterfaceAssemblyLayout, ...]
    indptr: np.ndarray
    indices: np.ndarray
    output_indices: np.ndarray
    term_indices: np.ndarray
    alpha_i: np.ndarray
    alpha_j: np.ndarray
    term_count: int

    def compatible(self, model: Model) -> bool:
        if int(model.gdl) != self.n or model.collections is None:
            return False
        quads = model.collections.quads
        interfaces = model.collections.interfaces
        if len(quads) != len(self.all_quads) or len(interfaces) != len(self.interfaces):
            return False
        for current, expected in zip(quads.values(), self.all_quads):
            if current is not expected:
                return False
        for current, layout in zip(interfaces.values(), self.interfaces):
            if current is not layout.interface:
                return False
            d0 = current.dim_aff[0] if len(current.dim_aff) > 0 else 6
            d1 = current.dim_aff[1] if len(current.dim_aff) > 1 else 2
            d2 = current.dim_aff[2] if len(current.dim_aff) > 2 else 4
            if (d0, d1, d2) != (layout.d0, layout.d1, layout.d2):
                return False
            if bool(current.slid) != layout.has_slid:
                return False
            if (len(current.slid_out_plan) >= 2) != layout.has_out_of_plane:
                return False
            if len(current.aff) != len(layout.aff_lists):
                return False
            for current_aff, expected_aff in zip(current.aff, layout.aff_lists):
                if current_aff is not expected_aff:
                    return False
        for quad, aff6 in self.quad_terms:
            if len(quad.aff) <= 6 or quad.aff[6] is not aff6:
                return False
        return True



def _expand_scatter_terms_numeric(
    *,
    aff_starts: np.ndarray,
    aff_lengths: np.ndarray,
    aff_gdls: np.ndarray,
    aff_coefficients: np.ndarray,
    term_aff_i: np.ndarray,
    term_aff_j: np.ndarray,
    term_values: np.ndarray,
    term_mirror: np.ndarray,
    chunk_terms: int = 8192,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Expand local afference Cartesian products with NumPy, in C# order.

    The old plan builder executed one Python function call per stiffness term
    and five ``array.array.append`` calls per emitted contribution.  Large
    bridges therefore spent several seconds creating ~2.8 million scalar
    records in Python before the numerical solve started.

    Here Python records only one compact metadata row per *local stiffness
    term*.  NumPy expands the variable-size Cartesian products in chunks.
    Ordering is unchanged:

    * terms remain in C# element/local-loop order;
    * ``ei`` is the outer loop and ``ej`` the inner loop;
    * mirrored interface contributions are emitted immediately after their
      corresponding forward contribution;
    * mirrored entries intentionally retain ``alpha_i, alpha_j`` in the same
      order as C# ``LinearSystem.SumK(..., d:false)``.
    """
    if term_values.size == 0:
        empty_i = np.empty(0, dtype=np.int32)
        empty_f = np.empty(0, dtype=np.float64)
        return empty_i, empty_i.copy(), empty_i.copy(), empty_f, empty_f.copy()

    len_i = aff_lengths[term_aff_i].astype(np.int64, copy=False)
    len_j = aff_lengths[term_aff_j].astype(np.int64, copy=False)
    factors = 1 + term_mirror.astype(np.int64, copy=False)
    counts = len_i * len_j * factors
    total = int(np.sum(counts, dtype=np.int64))

    rows = np.empty(total, dtype=np.int32)
    cols = np.empty(total, dtype=np.int32)
    out_terms = np.empty(total, dtype=np.int32)
    alpha_i = np.empty(total, dtype=np.float64)
    alpha_j = np.empty(total, dtype=np.float64)

    cursor = 0
    term_count = int(term_values.size)
    for begin in range(0, term_count, chunk_terms):
        stop = min(begin + chunk_terms, term_count)
        chunk_counts = counts[begin:stop]
        chunk_total = int(np.sum(chunk_counts, dtype=np.int64))
        if chunk_total == 0:
            continue

        # Metadata-row index for every emitted contribution in this chunk.
        meta = np.repeat(
            np.arange(begin, stop, dtype=np.int32),
            chunk_counts,
        )
        local_counts = chunk_counts.astype(np.int64, copy=False)
        starts = np.cumsum(local_counts, dtype=np.int64) - local_counts
        within = (
            np.arange(chunk_total, dtype=np.int64)
            - np.repeat(starts, local_counts)
        )

        factor = factors[meta]
        pair = within // factor
        nj = len_j[meta]
        ai_pos = aff_starts[term_aff_i[meta]] + pair // nj
        aj_pos = aff_starts[term_aff_j[meta]] + pair % nj

        forward_rows = aff_gdls[ai_pos]
        forward_cols = aff_gdls[aj_pos]
        mirrored = (factor == 2) & ((within & 1) == 1)

        target = slice(cursor, cursor + chunk_total)
        rows[target] = np.where(mirrored, forward_cols, forward_rows)
        cols[target] = np.where(mirrored, forward_rows, forward_cols)
        out_terms[target] = term_values[meta]
        alpha_i[target] = aff_coefficients[ai_pos]
        alpha_j[target] = aff_coefficients[aj_pos]
        cursor += chunk_total

    if cursor != total:
        raise _AssemblyPlanIncompatible(
            f"numeric stiffness scatter expansion wrote {cursor} of {total} entries"
        )
    return rows, cols, out_terms, alpha_i, alpha_j

def _map_contributions_to_csc_python(
    rows: np.ndarray,
    cols: np.ndarray,
    indptr: np.ndarray,
    indices: np.ndarray,
) -> np.ndarray:
    out = np.empty(rows.size, dtype=np.int32)
    for k in range(rows.size):
        row = int(rows[k])
        col = int(cols[k])
        lo = int(indptr[col])
        hi = int(indptr[col + 1])
        pos = int(np.searchsorted(indices[lo:hi], row)) + lo
        if pos >= hi or int(indices[pos]) != row:
            out[k] = -1
        else:
            out[k] = pos
    return out


if njit is not None:
    _map_contributions_to_csc_impl = njit(cache=True, nogil=True)(
        _map_contributions_to_csc_python
    )
else:  # pragma: no cover
    _map_contributions_to_csc_impl = _map_contributions_to_csc_python


def _map_contributions_to_csc(
    rows: np.ndarray,
    cols: np.ndarray,
    indptr: np.ndarray,
    indices: np.ndarray,
) -> np.ndarray:
    """Map contribution coordinates to sorted CSC slots without a huge dict."""
    out = _map_contributions_to_csc_impl(rows, cols, indptr, indices)
    if np.any(out < 0):
        bad = int(np.flatnonzero(out < 0)[0])
        raise _AssemblyPlanIncompatible(
            f"CSC mask is missing stiffness entry ({int(rows[bad])}, {int(cols[bad])})"
        )
    return out



def _build_stiffness_assembly_plan(model: Model) -> _StiffnessAssemblyPlan:
    """Build immutable global scatter topology in exact C# assembly order.

    Only local-term metadata is accumulated in Python.  The millions of
    individual afference contributions are expanded numerically afterwards.
    """
    if model.collections is None:
        raise _AssemblyPlanIncompatible("Model.collections is not initialized")

    n = int(model.gdl)
    all_quads = tuple(model.collections.quads.values())
    quad_terms: list[tuple[Quad, Any]] = []

    # Flatten every distinct afference list once.  Each interface aff[i] list
    # is reused by many local stiffness terms, so repeatedly traversing those
    # Python objects was pure overhead in the former builder.
    aff_cache: dict[int, int] = {}
    aff_starts_list: list[int] = []
    aff_lengths_list: list[int] = []
    aff_gdls_list: list[int] = []
    aff_coefficients_list: list[float] = []

    def register_aff(entries: List[AfferenceEntry]) -> int:
        cache_key = id(entries)
        cached = aff_cache.get(cache_key)
        if cached is not None:
            return cached

        slot = len(aff_starts_list)
        aff_cache[cache_key] = slot
        start = len(aff_gdls_list)
        for entry in entries:
            gdl = int(entry.gdl) - 1
            if 0 <= gdl < n:
                aff_gdls_list.append(gdl)
                aff_coefficients_list.append(float(entry.alfa))
        aff_starts_list.append(start)
        aff_lengths_list.append(len(aff_gdls_list) - start)
        return slot

    # One metadata row per local stiffness term that can emit contributions.
    term_aff_i_list: list[int] = []
    term_aff_j_list: list[int] = []
    term_values_list: list[int] = []
    term_mirror_list: list[bool] = []

    append_term_i = term_aff_i_list.append
    append_term_j = term_aff_j_list.append
    append_term_value = term_values_list.append
    append_term_mirror = term_mirror_list.append

    term_index = 0

    # C# ModelManager.AssembleK: all Quads first, each Aff[6] i,j pair.
    for quad in all_quads:
        if not quad.aff or len(quad.aff) <= 6 or not quad.aff[6]:
            continue
        aff6 = quad.aff[6]
        quad_terms.append((quad, aff6))
        slot = register_aff(aff6)
        if aff_lengths_list[slot]:
            append_term_i(slot)
            append_term_j(slot)
            append_term_value(term_index)
            append_term_mirror(False)
        term_index += 1

    # Then Interfaces. C# reads only the local upper triangle and immediately
    # mirrors every off-diagonal local term via LinearSystem.SumK(..., d:false).
    interface_layouts: list[_InterfaceAssemblyLayout] = []
    for intf in model.collections.interfaces.values():
        aff = intf.aff
        aff_len = len(aff)
        d0 = intf.dim_aff[0] if len(intf.dim_aff) > 0 else 6
        d1 = intf.dim_aff[1] if len(intf.dim_aff) > 1 else 2
        d2 = intf.dim_aff[2] if len(intf.dim_aff) > 2 else 4

        has_slid = bool(intf.slid)
        has_out_of_plane = len(intf.slid_out_plan) >= 2
        # Register each local afference list exactly once. The previous
        # record_term path performed two cached function/dict lookups for every
        # one of the ~34 local stiffness terms per interface.
        aff_slots = [register_aff(entries) for entries in aff]
        interface_layouts.append(
            _InterfaceAssemblyLayout(
                interface=intf,
                aff_lists=tuple(aff),
                d0=d0,
                d1=d1,
                d2=d2,
                has_slid=has_slid,
                has_out_of_plane=has_out_of_plane,
            )
        )

        for i in range(d0):
            for j in range(i, d0):
                if i < aff_len and j < aff_len:
                    slot_i = aff_slots[i]
                    slot_j = aff_slots[j]
                    if aff_lengths_list[slot_i] and aff_lengths_list[slot_j]:
                        append_term_i(slot_i)
                        append_term_j(slot_j)
                        append_term_value(term_index)
                        append_term_mirror(i != j)
                term_index += 1

        if has_slid:
            for i in range(d1):
                for j in range(i, d1):
                    ai_idx = d0 + i
                    aj_idx = d0 + j
                    if ai_idx < aff_len and aj_idx < aff_len:
                        slot_i = aff_slots[ai_idx]
                        slot_j = aff_slots[aj_idx]
                        if aff_lengths_list[slot_i] and aff_lengths_list[slot_j]:
                            append_term_i(slot_i)
                            append_term_j(slot_j)
                            append_term_value(term_index)
                            append_term_mirror(ai_idx != aj_idx)
                    term_index += 1

        if has_out_of_plane:
            for i in range(d2):
                for j in range(i, d2):
                    ai_idx = d0 + d1 + i
                    aj_idx = d0 + d1 + j
                    if ai_idx < aff_len and aj_idx < aff_len:
                        slot_i = aff_slots[ai_idx]
                        slot_j = aff_slots[aj_idx]
                        if aff_lengths_list[slot_i] and aff_lengths_list[slot_j]:
                            append_term_i(slot_i)
                            append_term_j(slot_j)
                            append_term_value(term_index)
                            append_term_mirror(ai_idx != aj_idx)
                    term_index += 1

    aff_starts = np.asarray(aff_starts_list, dtype=np.int64)
    aff_lengths = np.asarray(aff_lengths_list, dtype=np.int32)
    aff_gdls = np.asarray(aff_gdls_list, dtype=np.int32)
    aff_coefficients = np.asarray(aff_coefficients_list, dtype=np.float64)
    term_aff_i = np.asarray(term_aff_i_list, dtype=np.int32)
    term_aff_j = np.asarray(term_aff_j_list, dtype=np.int32)
    term_values = np.asarray(term_values_list, dtype=np.int32)
    term_mirror = np.asarray(term_mirror_list, dtype=np.bool_)

    row_arr, col_arr, contribution_terms, alpha_i, alpha_j = (
        _expand_scatter_terms_numeric(
            aff_starts=aff_starts,
            aff_lengths=aff_lengths,
            aff_gdls=aff_gdls,
            aff_coefficients=aff_coefficients,
            term_aff_i=term_aff_i,
            term_aff_j=term_aff_j,
            term_values=term_values,
            term_mirror=term_mirror,
        )
    )

    # C# ComputeMaskK begins by inserting every diagonal.
    # MapSparseMatrix then sorts row indices within each CSC column.
    pattern = sp.coo_matrix(
        (
            np.ones(row_arr.size, dtype=np.int8),
            (row_arr, col_arr),
        ),
        shape=(n, n),
    ).tocsc()
    pattern.setdiag(1)
    pattern.sum_duplicates()
    pattern.sort_indices()

    indptr = np.asarray(pattern.indptr, dtype=np.int32).copy()
    indices = np.asarray(pattern.indices, dtype=np.int32).copy()
    output_indices = _map_contributions_to_csc(
        row_arr, col_arr, indptr, indices,
    )

    return _StiffnessAssemblyPlan(
        n=n,
        all_quads=all_quads,
        quad_terms=tuple(quad_terms),
        interfaces=tuple(interface_layouts),
        indptr=indptr,
        indices=indices,
        output_indices=output_indices,
        term_indices=contribution_terms,
        alpha_i=alpha_i,
        alpha_j=alpha_j,
        term_count=term_index,
    )

def _fill_stiffness_terms(plan: _StiffnessAssemblyPlan) -> np.ndarray:
    terms = np.empty(plan.term_count, dtype=np.float64)
    index = 0
    for quad, _aff6 in plan.quad_terms:
        terms[index] = float(quad.status.k)
        index += 1
    for layout in plan.interfaces:
        intf = layout.interface
        for i in range(layout.d0):
            row = intf.status.k[i]
            for j in range(i, layout.d0):
                terms[index] = float(row[j])
                index += 1
        if layout.has_slid:
            for i in range(layout.d1):
                row = intf.status.kslid[i]
                for j in range(i, layout.d1):
                    terms[index] = float(row[j])
                    index += 1
        if layout.has_out_of_plane:
            for i in range(layout.d2):
                row = intf.status.kslid_out_plan[i]
                for j in range(i, layout.d2):
                    terms[index] = float(row[j])
                    index += 1
    if index != plan.term_count:
        raise _AssemblyPlanIncompatible(
            f"stiffness term layout changed ({index} != {plan.term_count})"
        )
    return terms


def _accumulate_csharp_order_python(
    values: np.ndarray,
    output_indices: np.ndarray,
    term_indices: np.ndarray,
    alpha_i: np.ndarray,
    alpha_j: np.ndarray,
    terms: np.ndarray,
) -> None:
    # Deliberately scalar and left-associated, matching:
    #   a = k * alfa_i * alfa_j; Ax[idx] += a
    for k in range(output_indices.size):
        a = terms[term_indices[k]] * alpha_i[k]
        a = a * alpha_j[k]
        values[output_indices[k]] += a


if njit is not None:
    _accumulate_csharp_order_impl = njit(cache=True, nogil=True)(
        _accumulate_csharp_order_python
    )
else:  # pragma: no cover
    _accumulate_csharp_order_impl = _accumulate_csharp_order_python


def _accumulate_csharp_order(
    values: np.ndarray,
    output_indices: np.ndarray,
    term_indices: np.ndarray,
    alpha_i: np.ndarray,
    alpha_j: np.ndarray,
    terms: np.ndarray,
) -> None:
    _accumulate_csharp_order_impl(
        values, output_indices, term_indices, alpha_i, alpha_j, terms
    )


def _assemble_global_k_cached(model: Model, plan: _StiffnessAssemblyPlan) -> sp.csc_matrix:
    terms = _fill_stiffness_terms(plan)
    values = np.zeros(plan.indices.size, dtype=np.float64)
    _accumulate_csharp_order(
        values,
        plan.output_indices,
        plan.term_indices,
        plan.alpha_i,
        plan.alpha_j,
        terms,
    )
    return sp.csc_matrix(
        (values, plan.indices, plan.indptr), shape=(plan.n, plan.n), copy=False
    )


def _get_stiffness_assembly_plan(model: Model) -> _StiffnessAssemblyPlan:
    plan = getattr(model, "_perf_stiffness_assembly_plan", None)
    if isinstance(plan, _StiffnessAssemblyPlan) and plan.compatible(model):
        return plan
    plan = _build_stiffness_assembly_plan(model)
    setattr(model, "_perf_stiffness_assembly_plan", plan)
    return plan


def assemble_global_k(
    model: Model,
    alfa: float = 0.0,
    *,
    recompute_elements: bool = True,
) -> sp.csc_matrix:
    """Assemble global stiffness, reusing static scatter topology when safe.

    ``recompute_elements=True`` intentionally retains the original standalone
    implementation. The nonlinear solver first computes every element block
    and calls this function with ``recompute_elements=False``; only that path
    uses the topology cache. If the prepared topology has changed, the cache is
    rebuilt. If a cached layout cannot be consumed safely, the authoritative
    legacy scatter remains the fallback.
    """
    if recompute_elements:
        return _assemble_global_k_legacy(
            model, alfa=alfa, recompute_elements=True
        )
    try:
        plan = _get_stiffness_assembly_plan(model)
        return _assemble_global_k_cached(model, plan)
    except _AssemblyPlanIncompatible:
        if hasattr(model, "_perf_stiffness_assembly_plan"):
            delattr(model, "_perf_stiffness_assembly_plan")
        return _assemble_global_k_legacy(
            model, alfa=alfa, recompute_elements=False
        )


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
