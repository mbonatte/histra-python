from __future__ import annotations

import numpy as np
import scipy.sparse as sp

from histra.types.linear_system import LinearSystem
from histra.types.umfpack import UmfpackFactorization, find_umfpack_library


def test_umfpack_refactor_numeric() -> None:
    if find_umfpack_library() is None:
        return

    # Two matrices with identical sparsity pattern
    indptr = np.array([0, 2, 3], dtype=np.int32)
    indices = np.array([0, 1, 1], dtype=np.int32)
    data1 = np.array([4.0, 1.0, 3.0], dtype=np.float64)
    data2 = np.array([8.0, 2.0, 6.0], dtype=np.float64)

    k1 = sp.csc_matrix((data1, indices, indptr), shape=(2, 2))
    k2 = sp.csc_matrix((data2, indices, indptr), shape=(2, 2))
    b = np.array([1.0, 2.0], dtype=np.float64)

    fac = UmfpackFactorization(k1)
    try:
        assert fac.can_refactor_numeric(k2)

        # Different pattern matrix
        k_diff = sp.csc_matrix(np.eye(2))
        assert not fac.can_refactor_numeric(k_diff)

        sol1 = fac.solve(b).copy()
        expected1 = sp.linalg.spsolve(k1, b)
        assert np.allclose(sol1, expected1)

        refactored = fac.refactor_numeric(k2)
        assert refactored

        sol2 = fac.solve(b).copy()
        expected2 = sp.linalg.spsolve(k2, b)
        assert np.allclose(sol2, expected2)
    finally:
        fac.close()


def test_linear_system_symbolic_reuse() -> None:
    if find_umfpack_library() is None:
        return

    ls = LinearSystem(2, backend="umfpack")

    indptr = np.array([0, 2, 3], dtype=np.int32)
    indices = np.array([0, 1, 1], dtype=np.int32)
    data1 = np.array([4.0, 1.0, 3.0], dtype=np.float64)
    data2 = np.array([8.0, 2.0, 6.0], dtype=np.float64)

    ls.k = sp.csc_matrix((data1, indices, indptr), shape=(2, 2))
    ls.b[:] = [1.0, 2.0]
    ls.solve()
    assert np.allclose(ls.x, sp.linalg.spsolve(ls.k, ls.b))
    assert ls.factorization_count == 1

    orig_fac = ls._factorization
    assert isinstance(orig_fac, UmfpackFactorization)
    orig_sym_ptr = orig_fac._symbolic.value

    # Update k with new numerical values
    ls.k = sp.csc_matrix((data2, indices, indptr), shape=(2, 2))
    ls.b[:] = [1.0, 2.0]
    ls.solve()
    assert np.allclose(ls.x, sp.linalg.spsolve(ls.k, ls.b))
    assert ls.factorization_count == 2
    # Factorization object and symbolic pointer must be preserved!
    assert ls._factorization is orig_fac
    assert orig_fac._symbolic.value == orig_sym_ptr
