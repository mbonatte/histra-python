from __future__ import annotations

import math
from typing import Any

import numpy as np

try:
    from numba import njit
except Exception:  # pragma: no cover - optional acceleration
    njit = None

from histra.model.model import Model
from histra.solver.program import Program
from histra.solver.solution_algorithm import EquiSolnAlgo, _new_line_search
from histra.types.linear_system import LinearSolveError, LinearSystem


def _csharp_dot_python(left: np.ndarray, right: np.ndarray) -> float:
    """Scalar C# reduction used as the authoritative fallback/reference."""
    value = 0.0
    for index in range(left.size):
        value += float(left[index]) * float(right[index])
    return value


if njit is not None:
    _csharp_dot_impl = njit(cache=True, nogil=True)(_csharp_dot_python)
else:  # pragma: no cover
    _csharp_dot_impl = _csharp_dot_python


def _csharp_dot(left: np.ndarray, right: np.ndarray) -> float:
    """C# MatrixManager.Vector ``^`` reduction order, compiled when possible.

    Fast-math is deliberately disabled.  The loop remains scalar and
    left-associated, so this changes execution location only, not the
    floating-point reduction order used for C# parity.
    """
    if left.shape != right.shape:
        raise ValueError(f"dot shape mismatch: {left.shape} vs {right.shape}")
    return float(_csharp_dot_impl(left, right))


def _updates_tangent_each_iteration(an: Any) -> bool:
    """Match the exact C# NewtonLineSearch dispatch condition.

    The original condition accidentally omits StandardInitialInterpolatedLineSearch
    (and repeats StandardBisectionLineSearch), so that nominally standard method
    keeps the initial stiffness throughout the step.  Existing C# result databases
    therefore depend on this compatibility behavior.
    """
    return str(getattr(an, "method", "")) in {
        "StandardNewtonRaphson",
        "StandardBisectionLineSearch",
        "StandardRegulaFalsiLineSearch",
        "StandardSecantLineSearch",
    }


class NewtonLineSearch(EquiSolnAlgo):
    """Newton-Raphson with the C# line-search call sequence."""

    def solve_current_step(
        self,
        p: Program,
        ls: LinearSystem,
        model: Model,
        an: Any,
        combination: int,
        step: int,
        alfa: float,
    ) -> int:
        del combination
        assert self.the_integrator is not None
        assert self.the_test is not None
        if self.the_line_search is None:
            self.the_line_search = _new_line_search(an)
        diagnostics = p.diagnostics

        self.the_test.start()
        if diagnostics is None:
            self.the_integrator.form_unbalance(p, model, an)
        else:
            with diagnostics.timed("residual_assembly"):
                self.the_integrator.form_unbalance(p, model, an)
        result = -1
        previous_error = 1.0

        while result == -1:
            p.check_cancelled()
            # Match the C# NewtonLineSearch sequence: line-search points are
            # reached incrementally from the current trial point and no full
            # constitutive snapshot is taken for each Newton correction.
            # solve.py owns the complete pre-step checkpoint and restores it
            # after any failed/cancelled step (including ALS and ArcLength
            # retries), so an additional per-iteration copy is redundant.
            residual0 = ls.b.copy()
            if _updates_tangent_each_iteration(an) and alfa != 0.0:
                if diagnostics is None:
                    self.the_integrator.update_k(p, model, alfa)
                else:
                    with diagnostics.timed("tangent_assembly"):
                        self.the_integrator.update_k(p, model, alfa)

            try:
                if diagnostics is None:
                    self.the_integrator.compute_increment(p, ls, model, an)
                else:
                    with diagnostics.timed("linear_solver"):
                        self.the_integrator.compute_increment(p, ls, model, an)
            except LinearSolveError as exc:
                p.log(f"Stiffness matrix is singular at step {step}: {exc}")
                return -3

            dx0 = ls.x.copy()
            self.the_line_search.new_step(p, ls)
            s0 = -_csharp_dot(dx0, residual0)

            if diagnostics is None:
                update_code = self.the_integrator.update(model, p, an)
            else:
                with diagnostics.timed("update_domain"):
                    update_code = self.the_integrator.update(model, p, an)
            if update_code < 0:
                return update_code

            if diagnostics is None:
                self.the_integrator.form_unbalance(p, model, an)
            else:
                with diagnostics.timed("residual_assembly"):
                    self.the_integrator.form_unbalance(p, model, an)
            s1 = -_csharp_dot(dx0, ls.b)
            if diagnostics is None:
                eta = self.the_line_search.search(
                    model, p, ls, self.the_integrator, an, dx0, s0, s1
                )
            else:
                with diagnostics.timed("line_search"):
                    eta = self.the_line_search.search(
                        model, p, ls, self.the_integrator, an, dx0, s0, s1
                    )
            if eta < 0.0:
                return -10

            # Search evaluates the residual at its final trial point and stores
            # eta*dx0 in LS.x for displacement/work convergence tests.
            result = self.the_test.test(p, model, ls)
            error = self.the_test.get_error()
            if diagnostics is not None:
                tested_iteration = max(
                    1,
                    int(self.the_test.current_iter)
                    - (1 if result in {-1, -2} else 0),
                )
                captured = diagnostics.capture_state(
                    label="newton",
                    step=step,
                    iteration=tested_iteration,
                    program=p,
                    model=model,
                )
                diagnostics.emit(
                    "iteration",
                    step=step,
                    iteration=tested_iteration,
                    solver="NewtonLineSearch",
                    line_search=type(self.the_line_search).__name__,
                    eta=float(eta),
                    s0=float(s0),
                    s1=float(s1),
                    convergence_error=float(error),
                    convergence_tolerance=float(self.the_test.tolerance),
                    convergence_criterion=str(self.the_test.criterion),
                    convergence_result=int(result),
                    convergence_reason=diagnostics.result_reason(result, self.the_test, p),
                    vector_snapshot=captured,
                    **diagnostics.integrator_metrics(self.the_integrator),
                    **diagnostics.vector_metrics(ls),
                    **diagnostics.spring_metrics(model),
                )
            if not math.isfinite(error):
                p.log(
                    f"Non-finite convergence error at step={step}, "
                    f"iteration={self.the_test.current_iter}"
                )
                return -4

            iteration = max(1, self.the_test.current_iter)
            estimate = max(iteration + 1.0, float(self.the_test.max_iter))
            if error < previous_error:
                estimate = max(iteration + 1.0, iteration / max(1e-6, 1.0 - error / max(previous_error, 1e-30)))
            p.progress(min(90.0, iteration / estimate * 100.0))
            previous_error = error

            if p.to_stop:
                return -4

        if result == -2:
            p.log(
                f"Line-search convergence failed at step={step}: "
                f"error={self.the_test.get_error():.6e}"
            )
        elif result == -3:
            p.log(
                f"Maximum displacement reached at step={step}: "
                f"max_u={p.max_u:.6e}"
            )
        return result
