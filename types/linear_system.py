from __future__ import annotations

import warnings

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import MatrixRankWarning, spsolve


class LinearSolveError(RuntimeError):
    """Raised when the sparse stiffness solve is singular or non-finite."""


class LinearSystem:
    """Sparse global system used by the translated static solver.

    The original C# ``LinearSystem.SetZero`` clears only the matrix values.
    Load and displacement vectors are cleared by separate methods.  Preserving
    that distinction is important because a standard Newton iteration rebuilds
    ``K`` *after* the residual has already been assembled in ``b``.
    """

    def __init__(self, n: int):
        self.n = int(n)
        self.k = sp.csc_matrix((self.n, self.n), dtype=np.float64)
        self.m = sp.csc_matrix((self.n, self.n), dtype=np.float64)
        self.c = sp.csc_matrix((self.n, self.n), dtype=np.float64)
        self.x = np.zeros(self.n, dtype=np.float64)
        self.b = np.zeros(self.n, dtype=np.float64)
        self.b0 = np.zeros(self.n, dtype=np.float64)

    def sumb(self, i: int, v: float) -> None:
        self.b[i] += v

    def get_b_norm(self, norm_type: int = 2) -> float:
        if self.b.size == 0:
            return 0.0
        if norm_type == 2:
            return float(np.linalg.norm(self.b))
        return float(np.max(np.abs(self.b)))

    def get_x_norm(self, norm_type: int = 2) -> float:
        if self.x.size == 0:
            return 0.0
        if norm_type == 2:
            return float(np.linalg.norm(self.x))
        return float(np.max(np.abs(self.x)))

    def get_x_per_b(self) -> float:
        return float(np.dot(self.x, self.b))

    def set_x(self, i: int, v: float) -> None:
        self.x[i] = v

    def set_x_vector(self, values: np.ndarray) -> None:
        values = np.asarray(values, dtype=np.float64)
        if values.shape != (self.n,):
            raise ValueError(
                f"Expected displacement vector of shape {(self.n,)}, "
                f"received {values.shape}"
            )
        self.x[:] = values

    def get_x(self, i: int) -> float:
        return float(self.x[i])

    def set_b(self, i: int, v: float) -> None:
        self.b[i] = v

    def set_b_vector(self, values: np.ndarray) -> None:
        values = np.asarray(values, dtype=np.float64)
        if values.shape != (self.n,):
            raise ValueError(
                f"Expected load vector of shape {(self.n,)}, "
                f"received {values.shape}"
            )
        self.b[:] = values

    def get_b(self, i: int) -> float:
        return float(self.b[i])

    def set_k(self, i: int, j: int, v: float) -> None:
        if not sp.isspmatrix_lil(self.k):
            self.k = self.k.tolil()
        self.k[i, j] = v

    def get_k(self, i: int, j: int) -> float:
        return float(self.k[i, j])

    def zero_b(self) -> None:
        self.b[:] = 0.0

    def zero_x(self) -> None:
        self.x[:] = 0.0

    def copy_b_to_b0(self) -> None:
        self.b0[:] = self.b

    def set_zero_load(self) -> None:
        self.b[:] = 0.0

    def set_zero_displacement(self) -> None:
        self.x[:] = 0.0

    def set_zero(self) -> None:
        """Clear only stiffness coefficients, matching C# ``K.SetZero()``."""
        self.k = sp.csc_matrix((self.n, self.n), dtype=np.float64)

    def solve(self, rhs: np.ndarray | None = None) -> int:
        """Solve ``K x = rhs`` and store the result in ``x``.

        HiStrA's saved afference matrices are expressed in active generalized
        DOFs: fixed DOFs are omitted while the C# model is prepared.  Therefore
        this method solves the assembled active system directly rather than
        trying to infer and eliminate restraints a second time.

        Returns ``0`` on success and raises :class:`LinearSolveError` on a
        singular or non-finite result.
        """
        if self.n == 0:
            self.x = np.zeros(0, dtype=np.float64)
            return 0

        vector = self.b if rhs is None else np.asarray(rhs, dtype=np.float64)
        if vector.shape != (self.n,):
            raise ValueError(
                f"Expected right-hand side of shape {(self.n,)}, "
                f"received {vector.shape}"
            )

        matrix = self.k.tocsc()
        if matrix.shape != (self.n, self.n):
            raise LinearSolveError(
                f"Stiffness matrix has shape {matrix.shape}; "
                f"expected {(self.n, self.n)}"
            )

        with warnings.catch_warnings():
            warnings.simplefilter("error", MatrixRankWarning)
            try:
                solution = spsolve(matrix, vector)
            except (MatrixRankWarning, RuntimeError, ValueError) as exc:
                raise LinearSolveError(f"Unable to solve stiffness system: {exc}") from exc

        solution = np.asarray(solution, dtype=np.float64).reshape(-1)
        if solution.shape != (self.n,) or not np.all(np.isfinite(solution)):
            raise LinearSolveError(
                "Sparse solve returned a singular or non-finite displacement vector"
            )

        self.x[:] = solution
        return 0
