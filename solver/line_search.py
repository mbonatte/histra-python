from __future__ import annotations

from typing import Any

import numpy as np


class LineSearch:
    """Base/no-op line search matching the C# solver interface."""

    def __init__(self) -> None:
        self.tolerance = 0.8
        self.max_iter = 100
        self.min_eta = 0.1
        self.max_eta = 10.0
        self.print_flag = 1
        self._direction: np.ndarray | None = None

    def new_step(self, p: Any, ls: Any) -> None:
        del p
        self._direction = ls.x.copy()

    def search(
        self,
        model: Any,
        p: Any,
        ls: Any,
        integrator: Any,
        an: Any,
        dx0: np.ndarray,
        s0: float,
        s1: float,
    ) -> float:
        del model, p, integrator, an, s0, s1
        ls.set_x_vector(dx0)
        return 1.0

    def _trial(
        self,
        model: Any,
        p: Any,
        ls: Any,
        integrator: Any,
        an: Any,
        direction: np.ndarray,
        eta: float,
        eta_previous: float,
    ) -> tuple[int, float]:
        """Move from the current trial point to ``eta`` and evaluate ``s``.

        The full Newton step has already been applied by ``NewtonLineSearch``,
        so the first correction is ``(eta - 1) * direction``.  Trial points are
        reached incrementally, exactly as in the C# algorithm.
        """
        ls.set_x_vector((eta - eta_previous) * direction)
        code = integrator.update(model, p, an)
        if code < 0:
            return code, float("nan")
        integrator.form_unbalance(p, model, an)
        # Fix an original C# inconsistency: s0/s1 use -dU·R, whereas trial
        # values used +dU·R.  A single sign convention is required for valid
        # secant/bracketing logic.
        return 0, -float(np.dot(direction, ls.b))

    @staticmethod
    def _ratio(s: float, s0: float) -> float:
        return abs(s / s0) if abs(s0) > 1e-30 else 0.0

    def _finish(self, ls: Any, direction: np.ndarray, eta: float) -> float:
        # Elements and total displacement are already at eta from incremental
        # trial corrections.  Set LS.x to the *total* scaled Newton increment
        # for displacement/work convergence tests, without updating again.
        ls.set_x_vector(eta * direction)
        return float(eta)


class RegulaFalsiLineSearch(LineSearch):
    """C# Regula Falsi algorithm with corrected bracket and sign handling."""

    def search(self, model, p, ls, integrator, an, dx0, s0, s1) -> float:
        if abs(s0) < 1e-30 or self._ratio(s1, s0) <= self.tolerance or s1 == s0:
            return self._finish(ls, dx0, 1.0)

        eta_lo, s_lo = 0.0, s0
        eta_hi, s_hi = 1.0, s1
        eta_previous = 1.0
        eta = 1.0
        baseline_ratio = self._ratio(s1, s0)

        for _ in range(self.max_iter):
            denominator = s_lo - s_hi
            if abs(denominator) < 1e-30:
                break
            eta = eta_hi - s_hi * (eta_lo - eta_hi) / denominator
            eta = float(np.clip(eta, self.min_eta, self.max_eta))

            code, s_eta = self._trial(
                model, p, ls, integrator, an, dx0, eta, eta_previous
            )
            if code < 0:
                return -1.0
            ratio = self._ratio(s_eta, s0)
            if ratio <= self.tolerance:
                return self._finish(ls, dx0, eta)

            # Keep the original safeguard, but compare against the initial full
            # step rather than against the same expression.
            if ratio > baseline_ratio and eta != 1.0:
                code, s_eta = self._trial(
                    model, p, ls, integrator, an, dx0, 1.0, eta
                )
                if code < 0:
                    return -1.0
                return self._finish(ls, dx0, 1.0)

            if s_eta * s_hi < 0.0:
                eta_lo, s_lo = eta, s_eta
            elif s_eta == 0.0:
                return self._finish(ls, dx0, eta)
            else:
                eta_hi, s_hi = eta, s_eta
            eta_previous = eta

        return self._finish(ls, dx0, eta_previous)


class SecantLineSearch(LineSearch):
    """C# secant line search with consistent residual signs."""

    def search(self, model, p, ls, integrator, an, dx0, s0, s1) -> float:
        if abs(s0) < 1e-30 or self._ratio(s1, s0) <= self.tolerance or s1 == s0:
            return self._finish(ls, dx0, 1.0)

        eta_prev2, s_prev2 = 0.0, s0
        eta_prev, s_prev = 1.0, s1
        baseline_ratio = self._ratio(s1, s0)

        for _ in range(self.max_iter):
            denominator = s_prev2 - s_prev
            if abs(denominator) < 1e-30:
                break
            eta = eta_prev - s_prev * (eta_prev2 - eta_prev) / denominator
            eta = float(np.clip(eta, self.min_eta, self.max_eta))
            code, s_eta = self._trial(
                model, p, ls, integrator, an, dx0, eta, eta_prev
            )
            if code < 0:
                return -1.0
            ratio = self._ratio(s_eta, s0)
            if ratio <= self.tolerance:
                return self._finish(ls, dx0, eta)
            if ratio > baseline_ratio and eta != 1.0:
                code, _ = self._trial(model, p, ls, integrator, an, dx0, 1.0, eta)
                if code < 0:
                    return -1.0
                return self._finish(ls, dx0, 1.0)
            eta_prev2, s_prev2 = eta_prev, s_prev
            eta_prev, s_prev = eta, s_eta

        return self._finish(ls, dx0, eta_prev)


class BisectionLineSearch(LineSearch):
    """Bracket-and-bisect search based on the original C# implementation."""

    def search(self, model, p, ls, integrator, an, dx0, s0, s1) -> float:
        if abs(s0) < 1e-30 or self._ratio(s1, s0) <= self.tolerance or s1 == s0:
            return self._finish(ls, dx0, 1.0)

        eta_lo, s_lo = 0.0, s0
        eta_hi, s_hi = 1.0, s1
        eta_previous = 1.0

        # Expand the upper point until a sign change is found.
        attempts = 0
        while s_lo * s_hi > 0.0 and eta_hi < self.max_eta and attempts < self.max_iter:
            attempts += 1
            eta_new = min(self.max_eta, 2.0 * eta_hi)
            code, s_new = self._trial(
                model, p, ls, integrator, an, dx0, eta_new, eta_previous
            )
            if code < 0:
                return -1.0
            eta_previous = eta_new
            eta_hi, s_hi = eta_new, s_new
            if self._ratio(s_hi, s0) <= self.tolerance:
                return self._finish(ls, dx0, eta_hi)

        if s_lo * s_hi > 0.0:
            # No bracket: restore the already accepted full Newton point.
            if eta_previous != 1.0:
                code, _ = self._trial(
                    model, p, ls, integrator, an, dx0, 1.0, eta_previous
                )
                if code < 0:
                    return -1.0
            return self._finish(ls, dx0, 1.0)

        eta = eta_previous
        for _ in range(max(0, self.max_iter - attempts)):
            eta = 0.5 * (eta_lo + eta_hi)
            code, s_eta = self._trial(
                model, p, ls, integrator, an, dx0, eta, eta_previous
            )
            if code < 0:
                return -1.0
            eta_previous = eta
            if self._ratio(s_eta, s0) <= self.tolerance or s_eta == 0.0:
                break
            if s_eta * s_hi < 0.0:
                eta_lo, s_lo = eta, s_eta
            else:
                eta_hi, s_hi = eta, s_eta

        return self._finish(ls, dx0, eta)


class InitialInterpolatedLineSearch(LineSearch):
    """Initial-interpolation search, ported as a real override.

    The original C# class declares ``new virtual`` instead of ``override``;
    through a base ``LineSearch`` reference that likely dispatches to the no-op
    base method.  The Python version implements the intended algorithm.
    """

    def search(self, model, p, ls, integrator, an, dx0, s0, s1) -> float:
        if abs(s0) < 1e-30 or self._ratio(s1, s0) <= self.tolerance or s1 == s0:
            return self._finish(ls, dx0, 1.0)

        eta_previous = 1.0
        eta = float(np.clip(s0 / (s0 - s1), self.min_eta, self.max_eta))
        for _ in range(self.max_iter):
            code, s_eta = self._trial(
                model, p, ls, integrator, an, dx0, eta, eta_previous
            )
            if code < 0:
                return -1.0
            if self._ratio(s_eta, s0) <= self.tolerance:
                break
            denominator = s0 - s_eta
            if abs(denominator) < 1e-30:
                break
            eta_previous = eta
            eta = float(np.clip(eta * s0 / denominator, self.min_eta, self.max_eta))
        return self._finish(ls, dx0, eta)
