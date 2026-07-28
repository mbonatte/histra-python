from __future__ import annotations

import math
from typing import Any

import numpy as np

from histra.model.model import Model
from histra.solver.program import Program
from histra.solver.solution_algorithm import EquiSolnAlgo, _new_line_search
from histra.solver.line_search import LineSearch
from histra.solver.state_snapshot import SolverStateSnapshot
from histra.types.linear_system import LinearSolveError, LinearSystem


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

        self.the_test.start()
        self.the_integrator.form_unbalance(p, model, an)
        result = -1
        previous_error = 1.0

        while result == -1:
            # The C# InitialInterpolated class hides rather than overrides the
            # base methods, so this benchmark dispatches through the exact
            # no-op LineSearch type.  No rejected trial point exists in that
            # path: a failure terminates the step and the complete pre-step
            # snapshot in solve.py restores it.  Avoid copying 2,454 spring
            # histories on every accepted Newton correction.  Real line-search
            # implementations retain a full per-iteration rollback snapshot.
            needs_iteration_snapshot = type(self.the_line_search) is not LineSearch
            iteration_snapshot = (
                SolverStateSnapshot.capture(
                    model, p, ls, self.the_integrator, self.the_test, self.the_line_search
                )
                if needs_iteration_snapshot else None
            )
            residual0 = ls.b.copy()
            if _updates_tangent_each_iteration(an) and alfa != 0.0:
                self.the_integrator.update_k(p, model, alfa)

            try:
                self.the_integrator.compute_increment(p, ls, model, an)
            except LinearSolveError as exc:
                if iteration_snapshot is not None:
                    iteration_snapshot.restore()
                p.log(f"Stiffness matrix is singular at step {step}: {exc}")
                return -3

            dx0 = ls.x.copy()
            self.the_line_search.new_step(p, ls)
            s0 = -float(np.dot(dx0, residual0))

            update_code = self.the_integrator.update(model, p, an)
            if update_code < 0:
                if iteration_snapshot is not None:
                    iteration_snapshot.restore()
                return update_code

            self.the_integrator.form_unbalance(p, model, an)
            s1 = -float(np.dot(dx0, ls.b))
            eta = self.the_line_search.search(
                model, p, ls, self.the_integrator, an, dx0, s0, s1
            )
            if eta < 0.0:
                if iteration_snapshot is not None:
                    iteration_snapshot.restore()
                return -10

            # Search evaluates the residual at its final trial point and stores
            # eta*dx0 in LS.x for displacement/work convergence tests.
            result = self.the_test.test(p, model, ls)
            error = self.the_test.get_error()
            if not math.isfinite(error):
                p.log(
                    f"Non-finite convergence error at step={step}, "
                    f"iteration={self.the_test.current_iter}"
                )
                if iteration_snapshot is not None:
                    iteration_snapshot.restore()
                return -4

            iteration = max(1, self.the_test.current_iter)
            estimate = max(iteration + 1.0, float(self.the_test.max_iter))
            if error < previous_error:
                estimate = max(iteration + 1.0, iteration / max(1e-6, 1.0 - error / max(previous_error, 1e-30)))
            p.progress(min(90.0, iteration / estimate * 100.0))
            previous_error = error

            if p.to_stop:
                if iteration_snapshot is not None:
                    iteration_snapshot.restore()
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
