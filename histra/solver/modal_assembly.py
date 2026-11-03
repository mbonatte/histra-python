"""Compiled modal COO scatter preserving the original full-block term order.

The static solver's cached C# scatter uses upper triangles and a different
reduction order. Modal regression depends on the original full-block COO order,
so keep that order and SciPy's duplicate reduction while compiling its hot loop.
"""

from __future__ import annotations

import numpy as np

try:
    from numba import njit
except Exception:  # Read-only imports and explicit scalar diagnostics remain usable.
    njit = None
import scipy.sparse as sp


def _scatter_blocks_impl(values, dimensions, active, offsets, dofs, coefficients, n, quad):
    capacity = 0
    start = 0
    for block in range(len(dimensions)):
        end = start + dimensions[block]
        if active[block]:
            capacity += (offsets[end] - offsets[start]) ** 2
        start = end
    rows = np.empty(capacity, np.int64)
    columns = np.empty(capacity, np.int64)
    data = np.empty(capacity, np.float64)
    count = 0
    start = 0
    value_start = 0
    for block in range(len(dimensions)):
        dimension = dimensions[block]
        if active[block]:
            for i in range(dimension):
                for j in range(dimension):
                    stiffness = values[value_start + i * dimension + j]
                    if not quad and abs(stiffness) < 1.0e-30:
                        continue
                    for ai in range(offsets[start + i], offsets[start + i + 1]):
                        gi = dofs[ai]
                        if not quad and (gi < 0 or gi >= n):
                            continue
                        for aj in range(offsets[start + j], offsets[start + j + 1]):
                            gj = dofs[aj]
                            if not quad and (gj < 0 or gj >= n):
                                continue
                            value = stiffness * coefficients[ai] * coefficients[aj]
                            # The historical Quad and Interface guards differ at
                            # exactly 1e-30 and for NaN. Retain both comparisons.
                            if quad:
                                if not abs(value) > 1.0e-30:
                                    continue
                            elif abs(value) < 1.0e-30:
                                continue
                            rows[count], columns[count], data[count] = gi, gj, value
                            count += 1
        value_start += dimension * dimension
        start += dimension
    return rows[:count].copy(), columns[:count].copy(), data[:count].copy()


_scatter_blocks = njit(cache=True)(_scatter_blocks_impl) if njit is not None else None


def _pack_afferences(afferences, count):
    groups = [afferences[index] if index < len(afferences) else () for index in range(count)]
    offsets = np.cumsum([0] + [len(group) for group in groups], dtype=np.int64)
    dofs = np.asarray([entry.gdl - 1 for group in groups for entry in group], np.int64)
    coefficients = np.asarray([entry.alfa for group in groups for entry in group], np.float64)
    return offsets, dofs, coefficients


def _quad_chunk(quad, n, alfa, quad_k_buf=None):
    quad.compute_k(alfa)
    packed = getattr(quad, "_modal_packed", None)
    if packed is None:
        afference = quad.aff[6] if quad.aff and len(quad.aff) > 6 else []
        packed = (
            np.asarray([1], np.int64),
            np.asarray([True]),
            *_pack_afferences([afference], 1),
        )
        quad._modal_packed = packed
    dims, act, offsets, dofs, coefs = packed
    if quad_k_buf is None:
        quad_k_buf = np.empty(1, dtype=np.float64)
    quad_k_buf[0] = quad.status.k
    return _scatter_blocks(
        quad_k_buf,
        dims,
        act,
        offsets,
        dofs,
        coefs,
        n,
        True,
    )


def _interface_chunk(interface, n, alfa, out_buf=None):
    interface.compute_k(alfa)
    packed = getattr(interface, "_modal_packed", None)
    if packed is None:
        dims = np.asarray(
            [
                interface.dim_aff[i] if i < len(interface.dim_aff) else default
                for i, default in enumerate((6, 2, 4))
            ],
            np.int64,
        )
        act = np.asarray([True, bool(interface.slid), len(interface.slid_out_plan) >= 2])
        packed = (dims, act, *_pack_afferences(interface.aff, int(dims.sum())))
        interface._modal_packed = packed
    dims, act, offsets, dofs, coefs = packed

    if out_buf is None:
        out_buf = np.empty(64, dtype=np.float64)

    pos = 0
    d0 = dims[0]
    k = interface.status.k
    for i in range(d0):
        row = k[i]
        for j in range(d0):
            out_buf[pos] = row[j]
            pos += 1
    d1 = dims[1]
    if act[1]:
        kslid = interface.status.kslid
        for i in range(d1):
            row = kslid[i]
            for j in range(d1):
                out_buf[pos] = row[j]
                pos += 1
    else:
        for _ in range(d1 * d1):
            out_buf[pos] = 0.0
            pos += 1
    d2 = dims[2]
    if act[2]:
        kout = interface.status.kslid_out_plan
        for i in range(d2):
            row = kout[i]
            for j in range(d2):
                out_buf[pos] = row[j]
                pos += 1
    else:
        for _ in range(d2 * d2):
            out_buf[pos] = 0.0
            pos += 1

    return _scatter_blocks(
        out_buf[:pos],
        dims,
        act,
        offsets,
        dofs,
        coefs,
        n,
        False,
    )


def assemble_modal_stiffness(model, alfa=1.0):
    """Recompute the same element blocks and scatter them without Python inner loops."""
    if _scatter_blocks is None:
        from histra.solver.backend_coverage import CompiledBackendRequiredError

        raise CompiledBackendRequiredError("Compiled modal scatter requires Numba")
    n = int(model.gdl)
    chunks = []
    append = chunks.append
    quad_k_buf = np.empty(1, dtype=np.float64)
    for quad in model.collections.quads.values():
        append(_quad_chunk(quad, n, alfa, quad_k_buf))
    out_buf = np.empty(64, dtype=np.float64)
    for interface in model.collections.interfaces.values():
        append(_interface_chunk(interface, n, alfa, out_buf))
    if not chunks:
        return sp.csc_matrix((n, n), dtype=np.float64)
    rows, columns, values = (np.concatenate(parts) for parts in zip(*chunks))
    return sp.coo_matrix((values, (rows, columns)), shape=(n, n)).tocsc()
