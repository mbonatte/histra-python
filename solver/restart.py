"""Restore a complete committed C# nonlinear state for chained analyses."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from histra.io.results_reader import (
    ResultsStateError,
    read_dynamic_vectors,
    read_interface_states,
    read_last_committed_step,
    read_quad_states,
    read_spring_states,
)
from histra.springs.coulomb03 import SpringCoulomb03
from histra.springs.hysteretic import SpringHysteretic


@dataclass(frozen=True)
class RestartSummary:
    analysis_key: int
    combination: int
    step: int
    dof_count: int
    quad_count: int
    interface_count: int
    spring_count: int


def _f(values: dict[str, Any] | Any, name: str, default: float = 0.0) -> float:
    value = values.get(name, default)
    return float(default if value is None else value)


def _i(values: dict[str, Any] | Any, name: str, default: int = 0) -> int:
    value = values.get(name, default)
    return int(default if value is None else value)


def _b(values: dict[str, Any] | Any, name: str, default: bool = False) -> bool:
    value = values.get(name, default)
    return bool(default if value is None else value)


def _spring_targets(model: Any):
    """Yield C# database identities and their live Python spring objects."""
    for key, intf in model.collections.interfaces.items():
        for local, spring in enumerate(intf.trasv_1):
            yield (102, int(key), 1, local), spring
        for local, spring in enumerate(intf.slid):
            yield (102, int(key), 11, local), spring
        for local, spring in enumerate(intf.slid_out_plan):
            yield (102, int(key), 21, local), spring
    for key, quad in model.collections.quads.items():
        yield (106, int(key), 30, 0), quad.spring


def _restore_common_spring(spring: Any, values: dict[str, Any]) -> None:
    spring.u = _f(values, "U")
    spring.f = _f(values, "F")
    spring.k_tang = _f(values, "K_tang", spring.k)
    spring.k_tang_committed = spring.k_tang
    spring.phase = _i(values, "Phase")
    spring.t_phase = spring.phase


def _restore_hysteretic(spring: SpringHysteretic, values: dict[str, Any]) -> None:
    _restore_common_spring(spring, values)
    spring.umax[:] = [_f(values, "Umax1"), _f(values, "Umax2")]
    spring.uy_corr[:] = [_f(values, "Uy1"), _f(values, "Uy2")]
    spring.fy[:] = [_f(values, "Fy1"), _f(values, "Fy2")]
    spring._crot_pu = _f(values, "Uu1")
    spring._crot_nu = _f(values, "Uu2")
    spring._cload_indicator = _i(values, "LoadIndicator")
    spring.f0 = _f(values, "F0")
    spring._cstrain = spring.u
    spring._cstress = spring.f
    spring.cenergy_d = _f(values, "Ed", 0.0)
    spring.revert_to_last_commit()


def _restore_coulomb(spring: SpringCoulomb03, values: dict[str, Any]) -> None:
    _restore_common_spring(spring, values)
    spring.umax[:] = [_f(values, "Umax1"), _f(values, "Umax2")]
    spring.fy[:] = [_f(values, "Fy1"), _f(values, "Fy2")]
    spring._crot_pu = _f(values, "Uu1")
    spring._crot_nu = _f(values, "Uu2")
    spring._cload_indicator = _i(values, "LoadIndicator")
    normal = _f(values, "N")
    spring._cstress_normal = normal
    spring._cstress_normal_prev = normal
    spring._ccontact_area = _f(values, "ContactArea", spring.area)
    # C# stores two Up slots for a scalar plastic/slip displacement in this law.
    # They are equal in the benchmark; reject lossy input rather than guessing.
    up1, up2 = _f(values, "Up1"), _f(values, "Up2")
    if abs(up1 - up2) > 1.0e-12:
        raise ResultsStateError(
            f"Coulomb03 restart has unequal Up1/Up2 ({up1}, {up2}); Python state is scalar"
        )
    spring._cup = up1
    spring._cmom_min = _f(values, "CmomMin")
    # The supplied C# SetSpring omits CmomMax during non-envelope restoration.
    # Python restores the persisted value because omitting it is demonstrably lossy.
    spring._cmom_max = _f(values, "CmomMax")
    spring._crot_lim_nu = _f(values, "CrotLimNu")
    spring._crot_lim_pu = _f(values, "CrotLimPu")
    spring._crot_yn = _f(values, "CrotYn")
    spring._crot_yp = _f(values, "CrotYp")
    spring._c_phase_unload_t = _i(values, "CPhaseUnload_t")
    spring._c_phase_unload_c = _i(values, "CPhaseUnload_c")
    spring.tangent_reload_c = _f(values, "TangentReload_c")
    spring.tangent_reload_t = _f(values, "TangentReload_t")
    spring._cplastic_tension_indicator = _b(values, "CplasticTensionIndicator")
    spring._cplastic_compression_indicator = _b(values, "CplasticCompressionIndicator")
    spring._cstrain = spring.u
    spring._cstress = spring.f
    spring.cenergy_d = _f(values, "Ed", 0.0)
    spring.dn = 0.0
    spring.revert_to_last_commit()


def restore_committed_analysis_state(
    model: Any,
    results_path: str | Path,
    analysis_key: int,
    combination: int,
    u: Any,
    v: Any,
    ls: Any,
    *,
    step: int | None = None,
) -> RestartSummary:
    """Restore global, local, and complete spring history at a committed step.

    Restart is accepted only when the C# database contains the final complete
    ``SpringStates`` record set.  Intermediate ``SpringStatesTmp`` is not enough
    to reproduce unloading/reloading history and therefore raises explicitly.
    """
    step = read_last_committed_step(results_path, analysis_key, combination) if step is None else int(step)
    db_u, db_v, vector_step = read_dynamic_vectors(
        results_path, analysis_key, combination, step, size=int(model.gdl)
    )
    if vector_step != step:
        raise ResultsStateError(
            f"Requested restart step {step}, but DynamicVectorsState is at {vector_step}"
        )
    qstates = read_quad_states(results_path, analysis_key, combination, step)
    istates = read_interface_states(results_path, analysis_key, combination, step)
    sstates = read_spring_states(
        results_path, analysis_key, combination, step, require_complete=True
    )

    missing_quads = set(model.collections.quads) - set(qstates)
    extra_quads = set(qstates) - set(model.collections.quads)
    missing_interfaces = set(model.collections.interfaces) - set(istates)
    extra_interfaces = set(istates) - set(model.collections.interfaces)
    if missing_quads or extra_quads or missing_interfaces or extra_interfaces:
        raise ResultsStateError(
            "HRX/database element mismatch: "
            f"missing_quads={sorted(missing_quads)}, extra_quads={sorted(extra_quads)}, "
            f"missing_interfaces={sorted(missing_interfaces)}, extra_interfaces={sorted(extra_interfaces)}"
        )

    u[:] = db_u
    v[:] = db_v
    ls.set_zero_displacement()

    for key, record in qstates.items():
        quad = model.collections.quads[key]
        quad.status.u[:] = record.u
        quad.status.k = record.k
        quad.status.f = 0.0
        quad.sigma_initial = 0.0
    for key, record in istates.items():
        intf = model.collections.interfaces[key]
        intf.status.u[:] = record.u
        intf.status.forces = record.forces
        intf.status.bending_moments = record.bending_moments
        intf.status.v[:] = [0.0] * len(intf.status.v)
        intf.status.fd[:] = [0.0] * len(intf.status.fd)
        intf.f[:] = [0.0] * len(intf.f)

    targets = dict(_spring_targets(model))
    if set(targets) != set(sstates):
        missing = sorted(set(targets) - set(sstates))
        extra = sorted(set(sstates) - set(targets))
        raise ResultsStateError(
            f"HRX/database spring mismatch: missing={missing[:10]}, extra={extra[:10]}, "
            f"counts=({len(targets)},{len(sstates)})"
        )
    for identity, spring in targets.items():
        if spring is None:
            raise ResultsStateError(f"Database spring {identity} maps to None in HRX")
        values = dict(sstates[identity].values)
        if isinstance(spring, SpringHysteretic):
            _restore_hysteretic(spring, values)
        elif isinstance(spring, SpringCoulomb03):
            _restore_coulomb(spring, values)
        else:
            raise ResultsStateError(
                f"Unsupported restart spring type {type(spring).__name__} for {identity}"
            )

    return RestartSummary(
        analysis_key=int(analysis_key),
        combination=int(combination),
        step=step,
        dof_count=len(db_u),
        quad_count=len(qstates),
        interface_count=len(istates),
        spring_count=len(sstates),
    )
