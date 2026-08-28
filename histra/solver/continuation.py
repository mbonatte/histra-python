"""Continuation controls for the static nonlinear analysis.

Automatic load-step reduction (ALS) following the original C# sequence, the
load-control predicate and the shared element/state commit helper used by the
step executor and the ALS sub-stepping path.

ALS always restarts from an exact pre-step snapshot: this restores external
loads, pseudo-time, all local element values and every trial/committed spring
field before any reduced increment is applied.
"""
from __future__ import annotations

import time
from typing import Any

from histra.model.model import Model
from histra.solver.load_control import LoadControl
from histra.solver.model_manager import ModelManager
from histra.solver.program import Program
from histra.solver.solution_algorithm import EquiSolnAlgo
from histra.solver.state_snapshot import SolverStateSnapshot
from histra.types.linear_system import LinearSystem


def _is_load_control(an: Any) -> bool:
    return "ArcLength" not in str(getattr(an, "integration_method", "LoadControl"))



def _commit_state(model: Model, ls: LinearSystem) -> None:
    runtime = ModelManager.hysteretic_batch_for(model)
    if runtime is not None:
        runtime.commit()
    for collection_name in ("quads", "interfaces"):
        for element in getattr(model.collections, collection_name).values():
            element.commit(ls)

def _execute_steps(
    model: Model,
    analysis: Any,
    combination: int,
    *,
    p: Program,
    ls: LinearSystem,
    n: int,
    integrator: Any,
    algorithm: EquiSolnAlgo,
    alfa: float,
    dof: int,
    diagnostic_writer: DiagnosticOptions | None,
    initial_reaction: Any,
    equilibrium_reference_load_factor: float,
    equilibrium_target_force: Any,
    reference: list,
    reference_displacement: float,
    equilibrium_policy: str,
    equilibrium_force_absolute_tolerance: float,
    equilibrium_force_relative_tolerance: float,
    equilibrium_residual_tolerance: float,
    on_step_committed: Callable[[dict[str, Any], Any], None] | None,
    should_stop_after_commit: Callable[[dict[str, Any]], bool] | None,
    max_committed_steps: int | None,
) -> tuple[int, list[dict[str, Any]], int, int]:
    """Run the committed-step loop; returns (final_code, step_data, unsafe_count)."""
    step_data: list[dict[str, Any]] = []
    unsafe_equilibrium_steps = 0
    warned_unsafe_equilibrium = False
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
        snapshot_started = time.perf_counter()
        step_snapshot = SolverStateSnapshot.capture(
            model, p, ls, integrator, algorithm.the_test, algorithm.the_line_search
        )
        if diagnostic_writer is not None:
            diagnostic_writer.add_timing("snapshot", time.perf_counter() - snapshot_started)
            diagnostic_writer.emit(
                "snapshot",
                step=step,
                scope="pre_step",
                **diagnostic_writer.integrator_metrics(integrator),
            )
        dof = ModelManager.get_dof_for_max_displacement(p, model, analysis)
        try:
            p.check_cancelled()
            try:
                integrator.new_step(p, model, ls, analysis, combination, step, dof)
                if diagnostic_writer is not None:
                    diagnostic_writer.emit(
                        "step_start",
                        step=step,
                        control_dof=int(dof),
                        **diagnostic_writer.integrator_metrics(integrator),
                        **diagnostic_writer.vector_metrics(ls),
                    )
                p.check_cancelled()
                result = algorithm.solve_current_step(
                    p, ls, model, analysis, combination, step, alfa
                )
                p.check_cancelled()
            except LinearSolveError as exc:
                p.log(f"Linear solve failed at step {step}: {exc}")
                result = -3
            if result == -2 and isinstance(integrator, LoadControl) and bool(getattr(analysis, "als", False)):
                result = _als_loop(
                    p, ls, model, analysis, combination, step, alfa, integrator, algorithm, step_snapshot
                )
            elif result == -2 and isinstance(integrator, ArcLength) and alfa != 0.0:
                # Retry from a complete pre-step state, not a partial global-vector rollback.
                p.check_cancelled()
                restore_started = time.perf_counter()
                step_snapshot.restore()
                if diagnostic_writer is not None:
                    diagnostic_writer.add_timing("restore", time.perf_counter() - restore_started)
                    diagnostic_writer.emit("restore", step=step, reason="arc_length_initial_tangent_retry")
                alfa = 0.0
                integrator.update_k(p, model, alfa)
                integrator.new_step(p, model, ls, analysis, combination, step, dof)
                p.check_cancelled()
                result = algorithm.solve_current_step(
                    p, ls, model, analysis, combination, step, alfa
                )
                p.check_cancelled()
            max_cutbacks = max(
                0, int(getattr(analysis, "arc_length_max_cutbacks", 0))
            )
            cutback = 0
            while (
                result in {-2, -3}
                and isinstance(integrator, ArcLength)
                and cutback < max_cutbacks
                and integrator.cutback_step(analysis)
            ):
                cutback += 1
                p.check_cancelled()
                restore_started = time.perf_counter()
                step_snapshot.restore()
                if diagnostic_writer is not None:
                    diagnostic_writer.add_timing(
                        "restore", time.perf_counter() - restore_started
                    )
                    diagnostic_writer.emit(
                        "restore",
                        step=step,
                        reason="arc_length_radius_cutback",
                        cutback=cutback,
                        radius=float(np.sqrt(abs(float(analysis.dr2)))),
                    )
                alfa = 0.0
                integrator.update_k(p, model, alfa)
                p.log(
                    f"Step {step}: retrying after ArcLength cutback {cutback}/"
                    f"{max_cutbacks}, dr={np.sqrt(abs(float(analysis.dr2))):.6g}"
                )
                try:
                    integrator.new_step(
                        p, model, ls, analysis, combination, step, dof
                    )
                    p.check_cancelled()
                    result = algorithm.solve_current_step(
                        p, ls, model, analysis, combination, step, alfa
                    )
                    p.check_cancelled()
                except LinearSolveError as exc:
                    p.log(f"Linear solve failed at step {step}: {exc}")
                    result = -3
        except SolverCancelled:
            cancelled_load_factor = float(integrator.mult)
            cancelled_displacement = float(p.u[dof]) if 0 <= dof < n else 0.0
            restore_started = time.perf_counter()
            step_snapshot.restore()
            if diagnostic_writer is not None:
                diagnostic_writer.add_timing("restore", time.perf_counter() - restore_started)
                diagnostic_writer.emit("restore", step=step, reason="cancelled")
            p.current_load_factor = integrator.mult
            final_code = CANCELLED_EXIT_CODE
            step_data.append(
                {
                    "step": step,
                    "status": "CANCELLED",
                    "exit_code": CANCELLED_EXIT_CODE,
                    "u": p.u.copy(),
                    "load_factor": cancelled_load_factor,
                    "displacement": cancelled_displacement,
                    "iterations": int(algorithm.the_test.current_iter),
                    "convergence_criterion": str(algorithm.the_test.criterion),
                    "convergence_tolerance": float(algorithm.the_test.tolerance),
                    "convergence_error": float(algorithm.the_test.get_error()),
                    "residual_norm": float(ls.get_b_norm()),
                    "increment_norm": float(ls.get_x_norm()),
                    "max_element_displacement": float(p.max_u),
                    "max_element_key": int(p.elem_max_u_key),
                    "max_element_type": str(p.elem_max_u_type),
                }
            )
            p.log(f"Analysis cancelled at step {step}; trial state was rolled back")
            break
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
            if diagnostic_writer is not None:
                captured = diagnostic_writer.capture_state(
                    label="failed",
                    step=step,
                    iteration=max(0, failure_iterations),
                    program=p,
                    model=model,
                )
                diagnostic_writer.emit(
                    "step_failure",
                    step=step,
                    exit_code=int(result),
                    reason=diagnostic_writer.result_reason(result, algorithm.the_test, p),
                    convergence_error=failure_error,
                    iterations=failure_iterations,
                    max_element_displacement=failure_max_u,
                    max_element_key=failure_max_key,
                    max_element_type=failure_max_type,
                    vector_snapshot=captured,
                    **diagnostic_writer.integrator_metrics(integrator),
                    **diagnostic_writer.vector_metrics(ls),
                    **diagnostic_writer.spring_metrics(model),
                )
            restore_started = time.perf_counter()
            step_snapshot.restore()
            if diagnostic_writer is not None:
                diagnostic_writer.add_timing("restore", time.perf_counter() - restore_started)
                diagnostic_writer.emit("restore", step=step, reason="failed_step")
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
                    "convergence_criterion": str(algorithm.the_test.criterion),
                    "convergence_tolerance": float(algorithm.the_test.tolerance),
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
        reaction = compute_total_reaction(model)
        equilibrium_fields: dict[str, Any] = {
            "equilibrium_checked": equilibrium_policy != "off",
        }
        if equilibrium_policy != "off":
            audit = audit_static_equilibrium(
                reaction=reaction,
                reference_reaction=initial_reaction,
                target_force=equilibrium_target_force,
                load_factor_increment=(
                    float(integrator.mult) - equilibrium_reference_load_factor
                ),
                residual=ls.b,
                force_absolute_tolerance=equilibrium_force_absolute_tolerance,
                force_relative_tolerance=equilibrium_force_relative_tolerance,
                residual_tolerance=equilibrium_residual_tolerance,
            )
            equilibrium_fields.update(audit.step_fields())
            if not audit.safe:
                unsafe_equilibrium_steps += 1
                message = audit.warning_message(
                    analysis_name=str(getattr(analysis, "name", "")),
                    step=step,
                    criterion=str(algorithm.the_test.criterion),
                    criterion_error=float(algorithm.the_test.get_error()),
                )
                p.log(f"################# {message} #################")
                if equilibrium_policy == "warn" and not warned_unsafe_equilibrium:
                    warnings.warn(
                        message + " Further unsafe steps are logged and marked in step data.",
                        UnsafeEquilibriumWarning,
                        stacklevel=2,
                    )
                    warned_unsafe_equilibrium = True
                if equilibrium_policy == "error":
                    failure_trial_u = p.u.copy()
                    failure_load_factor = float(integrator.mult)
                    failure_displacement = float(p.u[dof]) if 0 <= dof < n else 0.0
                    failure_increment_norm = float(ls.get_x_norm())
                    failure_max_u = float(p.max_u)
                    failure_max_key = int(p.elem_max_u_key)
                    failure_max_type = str(p.elem_max_u_type)
                    restore_started = time.perf_counter()
                    step_snapshot.restore()
                    if diagnostic_writer is not None:
                        diagnostic_writer.add_timing(
                            "restore", time.perf_counter() - restore_started
                        )
                        diagnostic_writer.emit(
                            "restore", step=step, reason="unsafe_equilibrium"
                        )
                    p.current_load_factor = integrator.mult
                    final_code = UNSAFE_EQUILIBRIUM_EXIT_CODE
                    step_data.append(
                        {
                            "step": step,
                            "status": "FAILED",
                            "exit_code": UNSAFE_EQUILIBRIUM_EXIT_CODE,
                            "u": p.u.copy(),
                            "trial_u": failure_trial_u,
                            "load_factor": failure_load_factor,
                            "displacement": failure_displacement,
                            "iterations": int(algorithm.the_test.current_iter),
                            "convergence_criterion": str(algorithm.the_test.criterion),
                            "convergence_tolerance": float(algorithm.the_test.tolerance),
                            "convergence_error": float(algorithm.the_test.get_error()),
                            "residual_norm": audit.residual_norm,
                            "increment_norm": failure_increment_norm,
                            "max_element_displacement": failure_max_u,
                            "max_element_key": failure_max_key,
                            "max_element_type": failure_max_type,
                            "reaction_x": reaction.x,
                            "reaction_y": reaction.y,
                            "reaction_z": reaction.z,
                            "balancing_reaction_x": reaction.balancing_x,
                            "balancing_reaction_y": reaction.balancing_y,
                            "balancing_reaction_z": reaction.balancing_z,
                            **equilibrium_fields,
                        }
                    )
                    p.log(
                        f"Analysis stopped before committing step {step}: "
                        "independent equilibrium safety audit failed"
                    )
                    break

        de_el, de_pl = ModelManager.compute_energy(model)
        energy_elastic += de_el
        energy_dissipated += de_pl
        commit_started = time.perf_counter()
        _commit_state(model, ls)
        if diagnostic_writer is not None:
            diagnostic_writer.add_timing("commit", time.perf_counter() - commit_started)

        p.current_load_factor = integrator.mult
        graph_displ: list[float] = []
        values = p.get_value_graph_analysis(
            model.collections, analysis, dof, reaction, graph_displ
        )
        displacement = graph_displ[0] if graph_displ else 0.0
        relative_displacement = displacement - reference_displacement
        step_data.append(
            {
                "step": step,
                "status": "OK",
                "exit_code": result,
                "u": p.u.copy(),
                "load_factor": p.current_load_factor,
                "displacement": displacement,
                "iterations": algorithm.the_test.current_iter,
                "convergence_criterion": str(algorithm.the_test.criterion),
                "convergence_tolerance": float(algorithm.the_test.tolerance),
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
                **equilibrium_fields,
            }
        )
        p.log(
            f"Step {step}: committed, load_factor={p.current_load_factor:.6f}, "
            f"displacement={displacement:.6e}, "
            f"iterations={algorithm.the_test.current_iter}"
        )
        force_change = abs(values[0] - reference[0])
        max_force_change = max(max_force_change, force_change)
        load_reduction_ratio = force_change / max(max_force_change, 1e-30)

        changed = [False]
        # C# subtracts the initial graph displacement before ArcLength/LoadControl
        # commit decisions.  This matters for chained analyses whose predecessor
        # already displaced the control point.
        stop = integrator.commit(model, analysis, relative_displacement, dof, changed)
        if diagnostic_writer is not None:
            captured = diagnostic_writer.capture_state(
                label="committed",
                step=step,
                iteration=int(algorithm.the_test.current_iter),
                program=p,
                model=model,
            )
            diagnostic_writer.emit(
                "commit",
                step=step,
                iterations=int(algorithm.the_test.current_iter),
                load_factor=float(p.current_load_factor),
                absolute_displacement=float(displacement),
                relative_displacement=float(relative_displacement),
                reaction_x=float(reaction.x),
                reaction_y=float(reaction.y),
                reaction_z=float(reaction.z),
                **equilibrium_fields,
                domain_changed=bool(changed[0]),
                stop=bool(stop),
                vector_snapshot=captured,
                **diagnostic_writer.integrator_metrics(integrator),
                **diagnostic_writer.vector_metrics(ls),
                **diagnostic_writer.spring_metrics(model),
            )
        if changed[0]:
            integrator.update_k(p, model, alfa)
            integrator.domain_changed(p, model, n)
        continue_steps = not stop
        if on_step_committed is not None:
            on_step_committed(step_data[-1], analysis)
        if should_stop_after_commit is not None and should_stop_after_commit(step_data[-1]):
            p.log(f"Requested post-commit stop condition reached at step {step}")
            continue_steps = False
        if max_committed_steps is not None and step >= max_committed_steps:
            p.log(f"Requested committed-step limit reached at step {step}")
            continue_steps = False

        if bool(getattr(analysis, "load_reduction_ratio_to_stop", False)):
            threshold = float(getattr(analysis, "load_reduction_ratio_to_stop_value", 0.1))
            if load_reduction_ratio < threshold:
                continue_steps = False


    return final_code, step_data, unsafe_equilibrium_steps, step


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
    restore_started = time.perf_counter()
    step_snapshot.restore()
    if p.diagnostics is not None:
        p.diagnostics.add_timing("restore", time.perf_counter() - restore_started)
        p.diagnostics.emit("restore", step=step, reason="als_start")

    completed = 0.0
    sub_increment = original_increment / factor
    reduction = 0
    while abs(original_increment - completed) > 1e-12 and reduction <= max_reductions:
        p.check_cancelled()
        remaining = original_increment - completed
        direction = 1.0 if remaining >= 0.0 else -1.0
        trial_increment = direction * min(abs(sub_increment), abs(remaining))
        p.log(
            f">>> Automatic step reduction ({reduction + 1}): "
            f"LoadIncrement={trial_increment:.6g}"
        )
        snapshot_started = time.perf_counter()
        substep_snapshot = SolverStateSnapshot.capture(
            model, p, ls, integrator, algorithm.the_test, algorithm.the_line_search
        )
        if p.diagnostics is not None:
            p.diagnostics.add_timing("snapshot", time.perf_counter() - snapshot_started)
            p.diagnostics.emit(
                "als_substep_start",
                step=step,
                reduction=reduction + 1,
                trial_increment=float(trial_increment),
                completed_increment=float(completed),
            )
        integrator.new_step_with_incr(
            p, model, ls, an, combination, step, trial_increment
        )
        p.check_cancelled()
        result = algorithm.solve_current_step(
            p, ls, model, an, combination, step, alfa
        )
        p.check_cancelled()
        if result >= 0:
            commit_started = time.perf_counter()
            _commit_state(model, ls)
            if p.diagnostics is not None:
                p.diagnostics.add_timing("commit", time.perf_counter() - commit_started)
                p.diagnostics.emit(
                    "als_substep_commit",
                    step=step,
                    reduction=reduction + 1,
                    trial_increment=float(trial_increment),
                )
            if integrator.u_committed is not None and integrator.u is not None:
                integrator.u_committed[:] = integrator.u
            completed += trial_increment
            continue
        # Restore the exact last-successful substep checkpoint.
        restore_started = time.perf_counter()
        substep_snapshot.restore()
        if p.diagnostics is not None:
            p.diagnostics.add_timing("restore", time.perf_counter() - restore_started)
            p.diagnostics.emit(
                "restore",
                step=step,
                reason="als_substep_failure",
                reduction=reduction + 1,
            )
        reduction += 1
        if reduction > max_reductions:
            restore_started = time.perf_counter()
            step_snapshot.restore()
            if p.diagnostics is not None:
                p.diagnostics.add_timing("restore", time.perf_counter() - restore_started)
                p.diagnostics.emit("restore", step=step, reason="als_exhausted")
            return -2
        sub_increment /= factor

    integrator.incr_mult = original_increment
    return 0
