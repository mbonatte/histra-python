"""Lossless nonlinear solver-state snapshots.

Snapshots deliberately mutate existing arrays/objects on restore so aliases
(``Program.u``, integrator ``u``, and ``ModelManager._u_total``) remain valid.
They cover the translated element/spring set and fail explicitly for state that
cannot be copied.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import hashlib
import pickle
from typing import Any, Iterable
from enum import Enum

import numpy as np

from histra.solver.model_manager import ModelManager


def _copy_array(value: Any) -> Any:
    """Fast value copy for solver state.

    Nonlinear snapshots contain thousands of spring dictionaries made almost
    entirely of scalars and short numeric containers.  ``deepcopy`` on each
    complete dictionary creates large memo/GC workloads and can cause very
    long pauses in multi-step ArcLength runs.  Copy the supported state shapes
    directly and retain ``deepcopy`` only as an explicit fallback.
    """
    if isinstance(value, np.ndarray):
        return value.copy()
    if value is None or isinstance(value, (bool, int, float, complex, str, bytes, Enum)):
        return value
    if isinstance(value, list):
        return [_copy_array(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_copy_array(item) for item in value)
    if isinstance(value, dict):
        return {key: _copy_array(item) for key, item in value.items()}
    if isinstance(value, set):
        return {_copy_array(item) for item in value}
    return deepcopy(value)


def _copy_state_dict(values: dict[str, Any]) -> dict[str, Any]:
    return {key: _copy_array(value) for key, value in values.items()}


def _restore_array(target: Any, saved: Any) -> Any:
    if isinstance(target, np.ndarray) and isinstance(saved, np.ndarray) and target.shape == saved.shape:
        target[...] = saved
        return target
    return _copy_array(saved)


def _iter_springs(model: Any) -> Iterable[Any]:
    seen: set[int] = set()
    for quad in model.collections.quads.values():
        spring = getattr(quad, "spring", None)
        if spring is not None and id(spring) not in seen:
            seen.add(id(spring))
            yield spring
    for intf in model.collections.interfaces.values():
        for name in ("trasv_1", "trasv_2", "slid", "slid_out_plan"):
            for spring in getattr(intf, name, ()):
                if spring is not None and id(spring) not in seen:
                    seen.add(id(spring))
                    yield spring


@dataclass
class SolverStateSnapshot:
    """Captured global, integrator, element, and constitutive state."""

    p: Any
    ls: Any
    integrator: Any
    convergence_test: Any
    line_search: Any
    program_state: dict[str, Any]
    linear_state: dict[str, Any]
    manager_state: dict[str, Any]
    integrator_state: dict[str, Any]
    integrator_member_state: dict[str, Any]
    convergence_state: dict[str, Any] | None
    line_search_state: dict[str, Any] | None
    quad_state: list[tuple[Any, dict[str, Any]]]
    interface_state: list[tuple[Any, dict[str, Any]]]
    spring_state: list[tuple[Any, dict[str, Any]]]

    @classmethod
    def capture(
        cls,
        model: Any,
        p: Any,
        ls: Any,
        integrator: Any,
        convergence_test: Any | None = None,
        line_search: Any | None = None,
    ) -> "SolverStateSnapshot":
        program_state = {
            key: _copy_array(getattr(p, key))
            for key in (
                "u", "v", "max_u", "elem_max_u_key", "elem_max_u_type",
                "to_stop", "index_fact_k", "current_load_factor",
            )
        }
        linear_state = {
            "k": ls.k.copy(), "m": ls.m.copy(), "c": ls.c.copy(),
            "x": ls.x.copy(), "b": ls.b.copy(), "b0": ls.b0.copy(),
        }
        manager_state = {
            key: _copy_array(getattr(ModelManager, key))
            for key in ("_ptarget", "_fext", "_pq", "_pq_prev", "_u_total")
        }
        member_state: dict[str, Any] = {}
        for key, value in integrator.__dict__.items():
            if key in {"state", "u", "v", "u_committed"}:
                continue
            member_state[key] = _copy_array(value)
        state_data = {
            key: _copy_array(value)
            for key, value in integrator.state.__dict__.items()
            if key not in {"analysis"}
        }
        state_data["__u"] = _copy_array(integrator.u)
        state_data["__v"] = _copy_array(integrator.v)
        state_data["__u_committed"] = _copy_array(integrator.u_committed)

        quads = []
        for quad in model.collections.quads.values():
            quads.append((quad, {
                "status": _copy_state_dict(quad.status.__dict__),
                "sigma_initial": float(getattr(quad, "sigma_initial", 0.0)),
            }))
        interfaces = []
        for intf in model.collections.interfaces.values():
            interfaces.append((intf, {
                "status": _copy_state_dict(intf.status.__dict__),
                "f": _copy_array(intf.f),
            }))
        springs = [(spring, _copy_state_dict(spring.__dict__)) for spring in _iter_springs(model)]
        return cls(
            p=p,
            ls=ls,
            integrator=integrator,
            convergence_test=convergence_test,
            line_search=line_search,
            program_state=program_state,
            linear_state=linear_state,
            manager_state=manager_state,
            integrator_state=state_data,
            integrator_member_state=member_state,
            convergence_state=_copy_state_dict(convergence_test.__dict__) if convergence_test else None,
            line_search_state=_copy_state_dict(line_search.__dict__) if line_search else None,
            quad_state=quads,
            interface_state=interfaces,
            spring_state=springs,
        )

    def restore(self) -> None:
        for key, saved in self.program_state.items():
            current = getattr(self.p, key)
            setattr(self.p, key, _restore_array(current, saved))
        self.ls.k = self.linear_state["k"].copy()
        self.ls.m = self.linear_state["m"].copy()
        self.ls.c = self.linear_state["c"].copy()
        self.ls.x[...] = self.linear_state["x"]
        self.ls.b[...] = self.linear_state["b"]
        self.ls.b0[...] = self.linear_state["b0"]

        for key, saved in self.manager_state.items():
            current = getattr(ModelManager, key)
            setattr(ModelManager, key, _restore_array(current, saved))

        reserved_integrator = {"state", "u", "v", "u_committed"}
        for key in list(self.integrator.__dict__):
            if key not in reserved_integrator and key not in self.integrator_member_state:
                del self.integrator.__dict__[key]
        for key, saved in self.integrator_member_state.items():
            current = getattr(self.integrator, key, None)
            setattr(self.integrator, key, _restore_array(current, saved))

        saved_state_keys = {
            key for key in self.integrator_state if not key.startswith("__")
        }
        for key in list(self.integrator.state.__dict__):
            if key != "analysis" and key not in saved_state_keys:
                del self.integrator.state.__dict__[key]
        for key, saved in self.integrator_state.items():
            if key.startswith("__"):
                continue
            current = getattr(self.integrator.state, key, None)
            setattr(self.integrator.state, key, _restore_array(current, saved))
        self.integrator.u = _restore_array(self.integrator.u, self.integrator_state["__u"])
        self.integrator.v = _restore_array(self.integrator.v, self.integrator_state["__v"])
        self.integrator.u_committed = _restore_array(
            self.integrator.u_committed, self.integrator_state["__u_committed"]
        )
        # Re-establish aliases used by the static solver.
        if isinstance(self.p.u, np.ndarray) and isinstance(self.integrator.u, np.ndarray):
            if self.p.u is not self.integrator.u:
                self.integrator.u = self.p.u
        if isinstance(self.p.v, np.ndarray) and isinstance(self.integrator.v, np.ndarray):
            if self.p.v is not self.integrator.v:
                self.integrator.v = self.p.v
        ModelManager._u_total = self.p.u

        if self.convergence_test is not None and self.convergence_state is not None:
            self.convergence_test.__dict__.clear()
            self.convergence_test.__dict__.update(_copy_state_dict(self.convergence_state))
        if self.line_search is not None and self.line_search_state is not None:
            self.line_search.__dict__.clear()
            self.line_search.__dict__.update(_copy_state_dict(self.line_search_state))

        for quad, saved in self.quad_state:
            quad.status.__dict__.clear()
            quad.status.__dict__.update(_copy_state_dict(saved["status"]))
            quad.sigma_initial = saved["sigma_initial"]
        for intf, saved in self.interface_state:
            intf.status.__dict__.clear()
            intf.status.__dict__.update(_copy_state_dict(saved["status"]))
            intf.f[:] = _copy_array(saved["f"])
        for spring, saved in self.spring_state:
            spring.__dict__.clear()
            spring.__dict__.update(_copy_state_dict(saved))

    def fingerprint(self) -> str:
        """Stable value fingerprint used by rollback regression tests."""
        payload = (
            self.program_state,
            self.linear_state,
            self.manager_state,
            self.integrator_state,
            self.integrator_member_state,
            self.convergence_state,
            self.line_search_state,
            [saved for _obj, saved in self.quad_state],
            [saved for _obj, saved in self.interface_state],
            [saved for _obj, saved in self.spring_state],
        )
        return hashlib.sha256(pickle.dumps(payload, protocol=5)).hexdigest()
