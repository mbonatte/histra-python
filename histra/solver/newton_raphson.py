from __future__ import annotations

import math
import os
from typing import Any

from histra.model.model import Model
from histra.solver.program import Program
from histra.solver.solution_algorithm import EquiSolnAlgo
from histra.solver.state_snapshot import SolverStateSnapshot
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
        diagnostics = p.diagnostics

        if diagnostics is None:
            self.the_integrator.form_unbalance(p, model, an)
        else:
            with diagnostics.timed("residual_assembly"):
                self.the_integrator.form_unbalance(p, model, an)
        self.the_test.start()
        result = -1
        previous_error = 1.0
        error = 1.0
        is_standard = _is_standard_method(an)
        adaptive_tangent_refresh = getattr(an, "adaptive_tangent_refresh", None)
        if adaptive_tangent_refresh is None:
            env_val = os.environ.get("HISTRA_ADAPTIVE_TANGENT_REFRESH", "").strip().lower()
            if env_val in {"1", "true", "yes", "on", "adaptive"}:
                adaptive_tangent_refresh = True
            elif env_val in {"0", "false", "no", "off"}:
                adaptive_tangent_refresh = False
            elif env_val.isdigit():
                adaptive_tangent_refresh = int(env_val)
            else:
                adaptive_tangent_refresh = False
        tangent_refresh_cadence = getattr(an, "tangent_refresh_cadence", None)
        if tangent_refresh_cadence is None:
            env_cadence = os.environ.get("HISTRA_TANGENT_REFRESH_CADENCE")
            if env_cadence is not None and env_cadence.isdigit():
                tangent_refresh_cadence = int(env_cadence)

        while result == -1:
            p.check_cancelled()
            iteration_snapshot = SolverStateSnapshot.capture(
                model, p, ls, self.the_integrator, self.the_test, self.the_line_search
            )
            current_it = self.the_test.current_iter

            refresh_tangent = False
            if is_standard and alfa != 0.0:
                refresh_tangent = True
            elif adaptive_tangent_refresh and not is_standard:
                if tangent_refresh_cadence is not None and tangent_refresh_cadence > 0:
                    if current_it == 1 or (current_it % tangent_refresh_cadence == 0):
                        refresh_tangent = True
                elif isinstance(adaptive_tangent_refresh, int) and adaptive_tangent_refresh > 0:
                    if current_it == 1 or (current_it % adaptive_tangent_refresh == 0):
                        refresh_tangent = True
                elif adaptive_tangent_refresh is True or str(adaptive_tangent_refresh).lower() in {"true", "adaptive"}:
                    if current_it == 1 and step > 1:
                        refresh_tangent = True
                    elif current_it >= 4 and (error > 0.7 * previous_error or current_it % 5 == 0):
                        refresh_tangent = True

            if refresh_tangent:
                refresh_alfa = alfa if (is_standard and alfa != 0.0) else 1.0
                if diagnostics is None:
                    self.the_integrator.update_k(p, model, refresh_alfa)
                else:
                    with diagnostics.timed("tangent_assembly"):
                        self.the_integrator.update_k(p, model, refresh_alfa)

            try:
                if diagnostics is None:
                    self.the_integrator.compute_increment(p, ls, model, an)
                else:
                    with diagnostics.timed("linear_solver"):
                        self.the_integrator.compute_increment(p, ls, model, an)
            except LinearSolveError as exc:
                iteration_snapshot.restore()
                p.log(f"Stiffness matrix is singular at step {step}: {exc}")
                return -3

            if diagnostics is None:
                update_code = self.the_integrator.update(model, p, an)
            else:
                with diagnostics.timed("update_domain"):
                    update_code = self.the_integrator.update(model, p, an)
            if update_code < 0:
                iteration_snapshot.restore()
                return update_code

            if diagnostics is None:
                self.the_integrator.form_unbalance(p, model, an)
            else:
                with diagnostics.timed("residual_assembly"):
                    self.the_integrator.form_unbalance(p, model, an)
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
                    solver="NewtonRaphson",
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
                iteration_snapshot.restore()
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
                iteration_snapshot.restore()
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
