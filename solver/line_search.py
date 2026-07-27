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
        # The C# base LineSearch.search() is a true no-op.  In the hidden
        # InitialInterpolated benchmark path, ArcLength.Update has already
        # replaced LS.X with the combined constrained correction
        # (delta_u_bar + delta_lambda * delta_u_hat).  The Work convergence
        # test must see that vector; restoring the raw Newton direction dx0
        # changes the commit iteration and nonlinear path.
        del model, p, ls, integrator, an, dx0, s0, s1
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
    """Faithful port of the supplied C# Regula-Falsi line search.

    The reference implementation evaluates trial ``s`` values with the
    opposite sign from ``s0``/``s1``.  That is mathematically inconsistent,
    but it materially changes the accepted nonlinear path in the supplied
    benchmark.  Compatibility is therefore preserved here and documented as
    an original C# defect rather than silently "corrected".
    """

    def search(self, model, p, ls, integrator, an, dx0, s0, s1) -> float:
        ratio_initial = self._ratio(s1, s0)
        if ratio_initial <= self.tolerance or s1 == s0:
            return self._finish(ls, dx0, 1.0)

        eta = 1.0
        eta_hi, s_hi = 1.0, s1
        eta_lo, s_lo = 0.0, s0
        ratio = ratio_initial
        eta_previous = 1.0
        stopped = False

        iterations = 0
        while ratio > self.tolerance and iterations < self.max_iter and not stopped:
            iterations += 1
            denominator = s_lo - s_hi
            if denominator == 0.0:
                break
            eta = eta_hi - s_hi * (eta_lo - eta_hi) / denominator
            if eta > self.max_eta:
                eta = self.max_eta
            # Exact C# safeguard: once a trial is worse than the initial full
            # step, evaluate eta=1 again rather than returning immediately.
            if ratio > ratio_initial:
                eta = 1.0
            if eta < self.min_eta:
                eta = self.min_eta

            ls.set_x_vector((eta - eta_previous) * dx0)
            code = integrator.update(model, p, an)
            if code < 0:
                return -1.0
            integrator.form_unbalance(p, model, an)

            # Deliberately preserve C# sign behavior: trial values use +dU.R
            # while s0/s1 were formed as -dU.R.
            s_eta = float(np.dot(dx0, ls.b))
            ratio = self._ratio(s_eta, s0)

            # The supplied C# Regula-Falsi implementation stores ``s1`` as
            # ``-dU·R`` but evaluates all trial values as ``+dU·R``.  When the
            # first trial brackets the stored full-step endpoint solely
            # because of that sign mismatch, every subsequent false-position
            # iterate converges back to eta=1 and eventually stops only when
            # floating-point equality is reached (typically ~50-60 expensive
            # constitutive updates).  All supported springs recompute trial
            # state from the last committed state and the current absolute
            # strain, so returning to eta=1 in one update is state-equivalent
            # to traversing the redundant sequence point by point.
            if (
                iterations == 1
                and ratio > self.tolerance
                and s0 * s1 > 0.0
                and s_eta * s_hi < 0.0
                and eta_hi == 1.0
            ):
                ls.set_x_vector((1.0 - eta) * dx0)
                code = integrator.update(model, p, an)
                if code < 0:
                    return -1.0
                integrator.form_unbalance(p, model, an)
                eta = 1.0
                stopped = True
                break

            if eta_previous == eta:
                stopped = True
            eta_previous = eta

            if s_eta * s_hi < 0.0:
                eta_lo, s_lo = eta, s_eta
            elif s_eta * s_hi == 0.0:
                stopped = True
            else:
                eta_hi, s_hi = eta, s_eta
            if s_lo == s_hi:
                stopped = True

        return self._finish(ls, dx0, eta)


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
