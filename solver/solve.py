from __future__ import annotations

from pathlib import Path
import gc
from typing import Any, Callable

import numpy as np

from histra.model.model import Model
from histra.io.results_reader import ResultsStateError, find_results_path
from histra.solver.arc_length import ArcLength
from histra.solver.assembler import assemble_load_vector
from histra.solver.incremental_integrator import StaticIntegrator
from histra.solver.load_control import LoadControl
from histra.solver.model_manager import ModelManager, pdelta_enabled
from histra.solver.program import Program
from histra.solver.solution_algorithm import EquiSolnAlgo
from histra.solver.state_snapshot import SolverStateSnapshot
from histra.solver.restart import restore_committed_analysis_state
from histra.postprocessing import compute_total_reaction
from histra.preprocessing import inspect_solver_readiness, require_solver_ready
from histra.types.linear_system import LinearSolveError, LinearSystem


def solve_static_nonlinear(
    model: Model,
    analysis: Any,
    combination: int = 1,
    *,
    on_log: Callable[[str], None] | None = None,
    on_progress: Callable[[float], None] | None = None,
    results_path: str | Path | None = None,
    initial_displacement: np.ndarray | None = None,
    restart_from_current_state: bool = False,
    auto_prepare: bool = True,
) -> tuple[int, list[dict[str, Any]]]:
    """Execute a static nonlinear analysis with bounded snapshot GC overhead.

    Reversible Newton trials create thousands of short-lived state containers.
    CPython's cyclic collector can pause for minutes while scanning these fully
    reachable constitutive graphs even though reference counting already frees
    each prior snapshot.  Suspend cyclic collection only for the synchronous
    solve and restore the caller's GC setting on every exit.
    """
    gc_was_enabled = gc.isenabled()
    if gc_was_enabled:
        gc.disable()
    try:
        return _solve_static_nonlinear_impl(
            model, analysis, combination, on_log=on_log,
            on_progress=on_progress, results_path=results_path,
            initial_displacement=initial_displacement,
            restart_from_current_state=restart_from_current_state,
            auto_prepare=auto_prepare,
        )
    finally:
        if gc_was_enabled:
            gc.enable()


def _solve_static_nonlinear_impl(
    model: Model,
    analysis: Any,
    combination: int = 1,
    *,
    on_log: Callable[[str], None] | None = None,
    on_progress: Callable[[float], None] | None = None,
    results_path: str | Path | None = None,
    initial_displacement: np.ndarray | None = None,
    restart_from_current_state: bool = False,
    auto_prepare: bool = True,
) -> tuple[int, list[dict[str, Any]]]:
    """C#-ordered static nonlinear solver implementation."""
    if model.collections is None:
        raise ValueError("Model.collections is not initialized")
    readiness = inspect_solver_readiness(model)
    if not readiness.is_ready and auto_prepare:
        if on_log is not None:
            on_log(
                "Preparing unlocked HRX computational model in Python "
                f"({readiness.quad_count} Quads)..."
            )
        prep = ModelManager.prepare_model(model)
        if on_log is not None:
            on_log(
                "PrepareModel completed: "
                f"GDL={prep.gdl}, interfaces={prep.interfaces}, "
                f"springs={prep.quad_springs + prep.transverse_springs + prep.sliding_springs + prep.out_of_plane_springs}"
            )
    require_solver_ready(model)
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
    initial_external_load = np.zeros(n)
    if initial_analysis_key < 0:
        if restart_from_current_state or initial_displacement is not None:
            raise ValueError(
                "A virgin analysis cannot restart from an in-memory committed state."
            )
        ModelManager.clear_hysteretic_batch()
        _set_initial_state(model, p.u, p.v, ls)
        ModelManager.prepare_hysteretic_batch(model, rebuild=True)
    elif restart_from_current_state:
        if initial_displacement is None:
            raise ValueError(
                "restart_from_current_state=True requires initial_displacement."
            )
        restored_u = np.asarray(initial_displacement, dtype=float)
        if restored_u.shape != (n,):
            raise ValueError(
                f"Expected initial_displacement shape ({n},), got {restored_u.shape}."
            )
        if not np.all(np.isfinite(restored_u)):
            raise ValueError("initial_displacement contains NaN or infinite values.")
        p.u[:] = restored_u
        p.v.fill(0.0)
        ls.set_zero_displacement()
        p.log(
            f"Using in-memory committed state from analysis {initial_analysis_key}: "
            f"{n} DOFs"
        )
        # The model's Quad/Interface/spring objects are already at the prior
        # analysis' last committed state. Reuse (or build) the dense hysteretic
        # runtime from those committed objects before evaluating equilibrium.
        ModelManager.prepare_hysteretic_batch(model, rebuild=False)
        # Reproduce C# SetFextEqualToFint so the new analysis starts from exact
        # equilibrium without a .Results DB.
        ModelManager.get_resisting_force(model, ls)
        initial_external_load = -ls.b.copy()
        p.log(
            "Restored chained baseline load from in-memory resisting forces: "
            f"norm={np.linalg.norm(initial_external_load):.6g}"
        )
    else:
        initial_combination = int(
            getattr(analysis, "initial_combination_analysis_key", combination)
        )
        resolved_results = Path(results_path) if results_path is not None else (
            find_results_path(model.source_path) if model.source_path else None
        )
        if resolved_results is None:
            raise ResultsStateError(
                "Chained analysis requires a C# .Results database. Pass results_path=... "
                "or place a sibling .Results file next to the HRX model."
            )
        ModelManager.clear_hysteretic_batch()
        restart = restore_committed_analysis_state(
            model, resolved_results, initial_analysis_key, initial_combination,
            p.u, p.v, ls,
        )
        ModelManager.prepare_hysteretic_batch(model, rebuild=True)
        p.log(
            f"Restored analysis {restart.analysis_key}, combination {restart.combination}, "
            f"step {restart.step}: {restart.dof_count} DOFs, "
            f"{restart.spring_count} complete spring states"
        )
        # C# does not reconstruct the predecessor load combination here.
        # After restoring the committed element state it calls
        # SetFextEqualToFint(), making the chained analysis start from an
        # exactly self-equilibrated baseline even when the predecessor was
        # committed by a work criterion with a non-zero residual.
        ModelManager.get_resisting_force(model, ls)
        initial_external_load = -ls.b.copy()
        p.log(
            f"Restored chained baseline load from committed resisting forces: "
            f"norm={np.linalg.norm(initial_external_load):.6g}"
        )

    ModelManager._ptarget = np.zeros(n)
    ModelManager._fext = initial_external_load.copy()
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
    # C# PrepareModelForAnalysis calls PrepareK(..., alfa=0) for every static
    # non-modal analysis, regardless of whether the later Newton method is
    # labelled Standard or Modified.  Standard methods may replace this matrix
    # inside their iteration loop; StandardInitialInterpolatedLineSearch is
    # accidentally omitted from that loop and therefore relies on this exact
    # initial-stiffness matrix for the whole step.
    integrator.update_k(p, model, 0.0)
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
        step_snapshot = SolverStateSnapshot.capture(
            model, p, ls, integrator, algorithm.the_test, algorithm.the_line_search
        )
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
                p, ls, model, analysis, combination, step, alfa, integrator, algorithm, step_snapshot
            )
        elif result == -2 and isinstance(integrator, ArcLength) and alfa != 0.0:
            # Retry from a complete pre-step state, not a partial global-vector rollback.
            step_snapshot.restore()
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
            # Preserve the trial termination diagnostics before restoring the
            # complete pre-step state. In particular, a -3 result represents
            # the model-wide element displacement limit, which is not
            # necessarily the graph/control DOF exported as ``displacement``.
            failure_max_u = float(p.max_u)
            failure_max_key = int(p.elem_max_u_key)
            failure_max_type = str(p.elem_max_u_type)
            failure_iterations = int(algorithm.the_test.current_iter)
            failure_error = float(algorithm.the_test.get_error())
            failure_residual = float(ls.get_b_norm())
            failure_increment = float(ls.get_x_norm())
            failure_load_factor = float(integrator.mult)
            failure_displacement = float(p.u[dof]) if 0 <= dof < n else 0.0
            step_snapshot.restore()
            p.current_load_factor = integrator.mult
            final_code = result
            step_data.append(
                {
                    "step": step,
                    "status": "FAILED",
                    "exit_code": result,
                    "u": p.u.copy(),
                    "load_factor": failure_load_factor,
                    "displacement": failure_displacement,
                    "iterations": failure_iterations,
                    "convergence_error": failure_error,
                    "residual_norm": failure_residual,
                    "increment_norm": failure_increment,
                    "max_element_displacement": failure_max_u,
                    "max_element_key": failure_max_key,
                    "max_element_type": failure_max_type,
                }
            )
            p.log(f"Analysis stopped: convergence failed at step {step} (code {result})")
            break

        de_el, de_pl = ModelManager.compute_energy(model)
        energy_elastic += de_el
        energy_dissipated += de_pl
        _commit_state(model, ls)

        reaction = compute_total_reaction(model)

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
                "convergence_error": float(algorithm.the_test.get_error()),
                "residual_norm": float(ls.get_b_norm()),
                "increment_norm": float(ls.get_x_norm()),
                "max_element_displacement": float(p.max_u),
                "max_element_key": int(p.elem_max_u_key),
                "max_element_type": str(p.elem_max_u_type),
                "elastic_energy": energy_elastic,
                "dissipated_energy": energy_dissipated,
                "reaction_x": reaction.x,
                "reaction_y": reaction.y,
                "reaction_z": reaction.z,
                "balancing_reaction_x": reaction.balancing_x,
                "balancing_reaction_y": reaction.balancing_y,
                "balancing_reaction_z": reaction.balancing_z,
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
        state.normal_increment = 0.0
        state.committed_normal_force = 0.0
        state.max_spring_displacement = 0.0
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
    runtime = ModelManager.hysteretic_batch_for(model)
    if runtime is not None:
        runtime.commit()
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
    step_snapshot: SolverStateSnapshot,
) -> int:
    """Automatic load-step reduction following the original C# sequence."""
    if not isinstance(integrator, LoadControl):
        return -2

    original_increment = integrator.incr_mult
    factor = max(2, int(getattr(an, "load_factor_als", 2)))
    max_reductions = max(1, int(getattr(an, "max_number_als", 5)))

    # Start ALS from an exact pre-step snapshot.  This restores external loads,
    # pseudo-time, all local element values, and every trial/committed spring field.
    step_snapshot.restore()

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

        substep_snapshot = SolverStateSnapshot.capture(
            model, p, ls, integrator, algorithm.the_test, algorithm.the_line_search
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

        # Restore the exact last-successful substep checkpoint.
        substep_snapshot.restore()
        reduction += 1
        if reduction > max_reductions:
            step_snapshot.restore()
            return -2
        sub_increment /= factor

    integrator.incr_mult = original_increment
    return 0
