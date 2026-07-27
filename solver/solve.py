from __future__ import annotations

from typing import Any, Callable

import numpy as np

from histra.model.model import Model
from histra.solver.arc_length import ArcLength
from histra.solver.incremental_integrator import StaticIntegrator
from histra.solver.load_control import LoadControl
from histra.solver.model_manager import ModelManager, pdelta_enabled
from histra.solver.program import Program
from histra.solver.solution_algorithm import EquiSolnAlgo
from histra.types.linear_system import LinearSolveError, LinearSystem


def solve_static_nonlinear(
    model: Model,
    analysis: Any,
    combination: int = 1,
    *,
    on_log: Callable[[str], None] | None = None,
    on_progress: Callable[[float], None] | None = None,
) -> tuple[int, list[dict[str, Any]]]:
    """Execute the translated static nonlinear solver.

    The execution order follows the original C# ``StaticNonLinearAnalysis``:
    prepare load and initial stiffness, initialize the integrator, apply a load
    step, solve iterations, optionally retry with ALS/initial stiffness, commit,
    and return the true final status.
    """
    if model.collections is None:
        raise ValueError("Model.collections is not initialized")
    if pdelta_enabled(getattr(analysis, "pdelta_effect", None)):
        raise NotImplementedError(
            "P-Delta is implemented in the original C# code but the required "
            "frame/load-generation subsystem is absent from this Python port."
        )

    n = int(model.gdl)
    p = Program(gdl=n, on_log=on_log, on_progress=on_progress)
    ls = LinearSystem(n)
    p.ls = ls
    p.u = np.zeros(n)
    p.v = np.zeros(n)

    # C# ModelManager.SetStatus/CommonOperations.SetInitial initializes a
    # virgin analysis independently of any solved state serialized in the HRX.
    # Without this reset, the first Python increment is added to the saved local
    # element displacements, producing a completely different residual path.
    initial_analysis_key = int(getattr(analysis, "initial_analysis_key", -100))
    if initial_analysis_key < 0:
        _set_initial_state(model, p.u, p.v, ls)
    else:
        raise NotImplementedError(
            "This analysis restarts from analysis "
            f"{initial_analysis_key}, combination "
            f"{getattr(analysis, 'initial_combination_analysis_key', 1)}. "
            "Restoring the complete prior C# database state (global vectors, "
            "element-local states, and all committed spring history variables) "
            "is not yet implemented; starting from zero would be incorrect."
        )

    ModelManager._ptarget = np.zeros(n)
    ModelManager._fext = np.zeros(n)
    ModelManager._pq = np.zeros(n)
    ModelManager._pq_prev = np.zeros(n)
    ModelManager._u_total = p.u

    if getattr(analysis, "load_function_key", 0) in model.collections.load_functions:
        analysis.load_function = model.collections.load_functions[analysis.load_function_key]

    ModelManager.assemble_load(model, ls, getattr(analysis, "key", None), combination)

    algorithm = EquiSolnAlgo.new_equi_soln_algo(analysis, combination)
    integrator = algorithm.the_integrator
    assert integrator is not None
    integrator.u = p.u
    integrator.v = p.v
    integrator.u_committed = p.u.copy()

    alfa = 0.0 if "Modified" in str(getattr(analysis, "method", "")) else 1.0
    # C# PrepareModelForAnalysis leaves a factorable stiffness ready before the
    # first NewStep.  This is essential for the ArcLength predictor.
    integrator.update_k(p, model, alfa)
    integrator.domain_changed(p, model, n)

    p.current_load_factor = integrator.mult
    dof = ModelManager.get_dof_for_max_displacement(p, model, analysis)
    reference = p.get_value_graph_analysis(model.collections, analysis, dof, None, [])

    step_data: list[dict[str, Any]] = []
    final_code = 0
    step = 0
    continue_steps = True
    max_force_change = 0.0
    energy_elastic = 0.0
    energy_dissipated = 0.0

    p.log(
        f"Analysis method: {getattr(analysis, 'integration_method', 'LoadControl')} "
        f"with {getattr(analysis, 'method', 'StandardNewtonRaphson')}"
    )

    while continue_steps:
        step += 1
        dof = ModelManager.get_dof_for_max_displacement(p, model, analysis)
        try:
            integrator.new_step(p, model, ls, analysis, combination, step, dof)
            result = algorithm.solve_current_step(
                p, ls, model, analysis, combination, step, alfa
            )
        except LinearSolveError as exc:
            p.log(f"Linear solve failed at step {step}: {exc}")
            result = -3

        if result == -2 and isinstance(integrator, LoadControl) and bool(getattr(analysis, "als", False)):
            result = _als_loop(
                p, ls, model, analysis, combination, step, alfa, integrator, algorithm
            )
        elif result == -2 and isinstance(integrator, ArcLength) and alfa != 0.0:
            # Original C# retry: revert and switch ArcLength to initial stiffness.
            integrator.revert_failed_step(model, ls)
            alfa = 0.0
            integrator.update_k(p, model, alfa)
            integrator.new_step(p, model, ls, analysis, combination, step, dof)
            result = algorithm.solve_current_step(
                p, ls, model, analysis, combination, step, alfa
            )

        p.current_load_factor = integrator.mult
        ModelManager._u_total = p.u
        if p.to_stop:
            result = -4

        if result < 0:
            if isinstance(integrator, LoadControl):
                integrator.undo_current_load_increment(model)
                integrator.revert_to_last_commit(model, ls)
            elif isinstance(integrator, ArcLength):
                integrator.revert_failed_step(model, ls)
            p.current_load_factor = integrator.mult
            final_code = result
            step_data.append(
                {
                    "step": step,
                    "status": "FAILED",
                    "exit_code": result,
                    "u": p.u.copy(),
                    "load_factor": integrator.mult,
                    "displacement": float(p.u[dof]) if 0 <= dof < n else 0.0,
                    "iterations": algorithm.the_test.current_iter,
                }
            )
            p.log(f"Analysis stopped: convergence failed at step {step} (code {result})")
            break

        de_el, de_pl = ModelManager.compute_energy(model)
        energy_elastic += de_el
        energy_dissipated += de_pl
        _commit_state(model, ls)

        p.current_load_factor = integrator.mult
        values = p.get_value_graph_analysis(model.collections, analysis, dof, None, [])
        displacement = values[1]
        step_data.append(
            {
                "step": step,
                "status": "OK",
                "exit_code": result,
                "u": p.u.copy(),
                "load_factor": values[0],
                "displacement": displacement,
                "iterations": algorithm.the_test.current_iter,
                "elastic_energy": energy_elastic,
                "dissipated_energy": energy_dissipated,
            }
        )
        p.log(
            f"Step {step}: committed, load_factor={values[0]:.6f}, "
            f"displacement={displacement:.6e}, "
            f"iterations={algorithm.the_test.current_iter}"
        )

        force_change = abs(values[0] - reference[0])
        max_force_change = max(max_force_change, force_change)
        load_reduction_ratio = force_change / max(max_force_change, 1e-30)

        changed = [False]
        stop = integrator.commit(model, analysis, displacement, dof, changed)
        if changed[0]:
            integrator.update_k(p, model, alfa)
            integrator.domain_changed(p, model, n)
        continue_steps = not stop

        if bool(getattr(analysis, "load_reduction_ratio_to_stop", False)):
            threshold = float(getattr(analysis, "load_reduction_ratio_to_stop_value", 0.1))
            if load_reduction_ratio < threshold:
                continue_steps = False

    if final_code == 0:
        p.log("Analysis executed and completed" if step else "Analysis not executed")
    else:
        p.log("Analysis executed but not completed")
    return final_code, step_data


def _set_initial_state(
    model: Model, u: np.ndarray, v: np.ndarray, ls: LinearSystem
) -> None:
    """Reset the supported model entities to the C# virgin state.

    This is the translated subset of ``CommonOperations.SetInitial`` for the
    element types implemented by this Python package.  Applied loads stored in
    ``Quad.status.p`` are deliberately preserved; they are regenerated later by
    ``ModelManager.assemble_load``.
    """
    ls.set_zero_displacement()
    u.fill(0.0)
    v.fill(0.0)

    for quad in model.collections.quads.values():
        quad.status.u[:] = [0.0] * len(quad.status.u)
        quad.status.f = 0.0
        if quad.spring is not None:
            quad.spring.k_tang = quad.spring.k
            quad.spring.revert_to_start()
            quad.spring.revert_to_last_commit()

    for intf in model.collections.interfaces.values():
        state = intf.status
        state.evd = 0.0
        state.u[:] = [0.0] * len(state.u)
        state.v[:] = [0.0] * len(state.v)
        state.fd[:] = [0.0] * len(state.fd)
        state.forces = (0.0, 0.0, 0.0)
        state.bending_moments = (0.0, 0.0, 0.0)
        intf.f[:] = [0.0] * len(intf.f)

        for spring_group in (
            intf.trasv_1, intf.trasv_2, intf.slid, intf.slid_out_plan
        ):
            for spring in spring_group:
                if spring is None:
                    continue
                spring.revert_to_start()
                spring.revert_to_last_commit()



def _is_load_control(an: Any) -> bool:
    return "ArcLength" not in str(getattr(an, "integration_method", "LoadControl"))


def _commit_state(model: Model, ls: LinearSystem) -> None:
    for collection_name in ("quads", "interfaces"):
        for element in getattr(model.collections, collection_name).values():
            element.commit(ls)


def _als_loop(
    p: Program,
    ls: LinearSystem,
    model: Model,
    an: Any,
    combination: int,
    step: int,
    alfa: float,
    integrator: StaticIntegrator,
    algorithm: EquiSolnAlgo,
) -> int:
    """Automatic load-step reduction following the original C# sequence."""
    if not isinstance(integrator, LoadControl):
        return -2

    original_increment = integrator.incr_mult
    factor = max(2, int(getattr(an, "load_factor_als", 2)))
    max_reductions = max(1, int(getattr(an, "max_number_als", 5)))

    # Undo the complete failed increment before starting reduced substeps.
    integrator.undo_current_load_increment(model)
    integrator.revert_to_last_commit(model, ls)

    completed = 0.0
    sub_increment = original_increment / factor
    reduction = 0

    while abs(original_increment - completed) > 1e-12 and reduction <= max_reductions:
        remaining = original_increment - completed
        direction = 1.0 if remaining >= 0.0 else -1.0
        trial_increment = direction * min(abs(sub_increment), abs(remaining))
        p.log(
            f">>> Automatic step reduction ({reduction + 1}): "
            f"LoadIncrement={trial_increment:.6g}"
        )

        integrator.new_step_with_incr(
            p, model, ls, an, combination, step, trial_increment
        )
        result = algorithm.solve_current_step(
            p, ls, model, an, combination, step, alfa
        )
        if result >= 0:
            _commit_state(model, ls)
            if integrator.u_committed is not None and integrator.u is not None:
                integrator.u_committed[:] = integrator.u
            completed += trial_increment
            continue

        # Undo only the failed substep, returning to the last successful
        # substep commit, then reduce the increment as in C#.
        integrator.undo_current_load_increment(model)
        integrator.revert_to_last_commit(model, ls)
        reduction += 1
        if reduction > max_reductions:
            return -2
        sub_increment /= factor

    integrator.incr_mult = original_increment
    return 0
