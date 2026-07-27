from __future__ import annotations

import math
from typing import Any

from histra.model.model import Model
from histra.solver.program import Program
from histra.solver.solution_algorithm import EquiSolnAlgo
from histra.types.linear_system import LinearSolveError, LinearSystem


def _is_standard_method(an: Any) -> bool:
    return str(getattr(an, "method", "")).startswith("Standard")


class NewtonRaphson(EquiSolnAlgo):
    """C#-aligned Newton-Raphson iteration loop."""

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

        self.the_integrator.form_unbalance(p, model, an)
        self.the_test.start()
        result = -1
        previous_error = 1.0

        while result == -1:
            if _is_standard_method(an) and alfa != 0.0:
                self.the_integrator.update_k(p, model, alfa)

            try:
                self.the_integrator.compute_increment(p, ls, model, an)
            except LinearSolveError as exc:
                p.log(f"Stiffness matrix is singular at step {step}: {exc}")
                return -3

            update_code = self.the_integrator.update(model, p, an)
            if update_code < 0:
                return update_code

            self.the_integrator.form_unbalance(p, model, an)
            result = self.the_test.test(p, model, ls)
            error = self.the_test.get_error()
            if not math.isfinite(error):
                p.log(
                    f"Non-finite convergence error at step={step}, "
                    f"iteration={self.the_test.current_iter}"
                )
                return -4

            # Keep progress informative without reproducing divide-by-zero
            # behavior in the original estimate formula.
            iteration = max(1, self.the_test.current_iter)
            if error < previous_error and previous_error > 0.0:
                reduction = max(error / previous_error, 1e-12)
                if reduction < 1.0 and error > 0.0:
                    target_ratio = max(self.the_test.tolerance / error, 1e-300)
                    remaining = max(1.0, abs(math.log(target_ratio) / math.log(reduction)))
                else:
                    remaining = 1.0
                estimate = iteration + remaining
            else:
                estimate = max(iteration + 1.0, float(self.the_test.max_iter))
            p.progress(min(90.0, iteration / estimate * 100.0))
            previous_error = error

            if p.to_stop:
                return -4

        if result == -2:
            p.log(
                f"Convergence failed at step={step}: max iterations "
                f"({self.the_test.max_iter}), error={self.the_test.get_error():.6e}"
            )
        elif result == -3:
            p.log(
                f"Maximum displacement reached at step={step}: "
                f"max_u={p.max_u:.6e}, limit={self.the_test.max_u:.6e}"
            )
        return result
