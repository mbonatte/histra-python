from __future__ import annotations

from typing import Any

from histra.types.linear_system import LinearSystem


class ConvergenceTest:
    """C#-aligned nonlinear convergence test.

    The original solver selects one of three absolute criteria:

    * ``ForceMoment``: norm of the residual vector ``b``;
    * ``DispRotation``: norm of the last displacement increment ``x``;
    * ``Work``: ``0.5 * abs(x dot b)``.

    The Python translation previously used a relative residual by default and
    failed to initialize its reference norm in the line-search path.  That was
    not how the C# implementation behaves.
    """

    def __init__(
        self,
        tolerance: float = 1e-6,
        max_iter: int = 100,
        max_u: float = 1e30,
        print_level: int = 0,
        norm_type: int = 2,
        criterion: str = "ForceMoment",
        absolute: bool = True,
    ) -> None:
        self.tolerance = float(tolerance)
        self.max_iter = int(max_iter)
        self.max_u = float(max_u)
        self.print_level = int(print_level)
        self.norm_type = int(norm_type)
        self.criterion = self._normalize_criterion(criterion)
        self.absolute = bool(absolute)
        self.current_iter = 0
        self.flag = 0
        self._error = 0.0
        self._previous_raw_norm = 1.0

    @staticmethod
    def _normalize_criterion(value: Any) -> str:
        text = str(value or "ForceMoment").replace("_", "").replace(" ", "").lower()
        if text in {"disprotation", "displacement", "displacementincrement", "normdispincr"}:
            return "DispRotation"
        if text in {"work", "energy", "energyincrement"}:
            return "Work"
        return "ForceMoment"

    def set_tolerance(self, tol: float) -> None:
        self.tolerance = float(tol)

    def set_max_num_iter(self, n: int) -> None:
        self.max_iter = int(n)

    def set_print_level(self, n: int) -> None:
        self.print_level = int(n)

    def start(self, ls: LinearSystem | None = None, reference_norm: float = 0.0) -> int:
        del ls, reference_norm
        self.current_iter = 1
        self._error = 0.0
        self._previous_raw_norm = 1.0
        return 0

    def _raw_error(self, ls: LinearSystem) -> float:
        if self.criterion == "DispRotation":
            return ls.get_x_norm(self.norm_type)
        if self.criterion == "Work":
            return 0.5 * abs(ls.get_x_per_b())
        return ls.get_b_norm(self.norm_type)

    def test(self, p: Any, model: Any, ls: LinearSystem) -> int:
        """Return C#-compatible result codes.

        ``>=0`` converged, ``-1`` continue, ``-2`` iteration limit and ``-3``
        maximum displacement reached.
        """
        from histra.solver.model_manager import ModelManager

        ModelManager.find_max_u(model, p)
        raw = self._raw_error(ls)

        if self.absolute:
            self._error = raw
        else:
            # Retained as an opt-in compatibility mode.  The original force
            # test compares the current norm with the first measured norm.
            if self.current_iter == 1:
                self._previous_raw_norm = max(abs(raw), 1e-30)
            self._error = raw / self._previous_raw_norm

        if self._error <= self.tolerance:
            return self.current_iter
        if self.current_iter >= self.max_iter:
            self.current_iter += 1
            return -2
        if p.max_u >= self.max_u:
            return -3

        self.current_iter += 1
        return -1

    def get_error(self) -> float:
        return abs(float(self._error))

    def get_tol(self) -> float:
        return self.tolerance

    def get_copy(self, iterations: int) -> "ConvergenceTest":
        """Return a same-type test with a different iteration cap.

        This intentionally fixes a bug in the original C# implementation where
        ``CTestNormUnbalance.getCopy`` returned a displacement-increment test.
        """
        return ConvergenceTest(
            tolerance=self.tolerance,
            max_iter=iterations,
            max_u=self.max_u,
            print_level=self.print_level,
            norm_type=self.norm_type,
            criterion=self.criterion,
            absolute=self.absolute,
        )
