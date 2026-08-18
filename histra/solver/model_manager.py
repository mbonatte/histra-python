from __future__ import annotations

from typing import Any, Callable

import numpy as np

from histra.model.model import Model
from histra.solver.assembler import assemble_global_k, assemble_load_vector
from histra.solver.program import Program
from histra.types.integrator_state import IntegratorState
from histra.types.linear_system import LinearSystem


def pdelta_enabled(value: Any) -> bool:
    """Normalize the C# enum/string representation of P-Delta settings."""
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return int(value) != 0
    text = str(value).strip().lower()
    return text not in {"", "0", "none", "no", "false", "disabled"}


class ModelManager:
    """Global assembly/state operations aligned with the C# ``ModelManager``."""

    _ptarget: np.ndarray | None = None
    _fext: np.ndarray | None = None
    _pq: np.ndarray | None = None
    _pq_prev: np.ndarray | None = None
    _u_total: np.ndarray | None = None
    _hysteretic_batch: Any | None = None
    _hysteretic_batch_model_id: int | None = None
    _hysteretic_batch_error: str | None = None

    on_log: Callable[[str], None] | None = None
    on_progress: Callable[[float], None] | None = None

    @classmethod
    def prepare_model(cls, model: Model, *, force: bool = False):
        """Port the C# ``ModelManager.PrepareModel`` preprocessing stage.

        The translated implementation currently covers the Quad/Restraint
        computational topology used by the supplied masonry models.  It
        creates interfaces, constitutive springs, global DOFs, and afference
        mappings, then returns a :class:`PreparationReport`.
        """
        from histra.preprocessing.prepare_model import prepare_model

        cls.clear_hysteretic_batch()
        return prepare_model(model, force=force)

    @classmethod
    def clear_hysteretic_batch(cls) -> None:
        """Detach any compiled spring runtime from its model objects."""
        runtime = cls._hysteretic_batch
        if runtime is not None:
            for record in runtime.records:
                interface = record.interface
                for name in ("_perf_hysteretic_batch", "_perf_hysteretic_slice"):
                    if hasattr(interface, name):
                        delattr(interface, name)
            for spring in getattr(runtime, "managed_springs", runtime.springs):
                for name in (
                    "_histra_batch_managed", "_histra_quad_batch",
                    "_histra_quad_batch_index",
                ):
                    if hasattr(spring, name):
                        delattr(spring, name)
        cls._hysteretic_batch = None
        cls._hysteretic_batch_model_id = None
        cls._hysteretic_batch_error = None

    @classmethod
    def prepare_hysteretic_batch(cls, model: Model, *, rebuild: bool = False) -> Any | None:
        """Build or reuse the optional compiled transverse-spring runtime."""
        if (
            not rebuild
            and cls._hysteretic_batch is not None
            and cls._hysteretic_batch_model_id == id(model)
        ):
            return cls._hysteretic_batch
        cls.clear_hysteretic_batch()
        try:
            from histra.solver.hysteretic_batch import build_hysteretic_batch
            runtime = build_hysteretic_batch(model)
        except Exception as exc:
            # Acceleration is optional. The tested scalar implementation remains
            # the authoritative fallback on platforms without a working Numba.
            runtime = None
            cls._hysteretic_batch_error = f"{type(exc).__name__}: {exc}"
        cls._hysteretic_batch = runtime
        cls._hysteretic_batch_model_id = id(model) if runtime is not None else None
        return runtime

    @classmethod
    def hysteretic_batch_for(cls, model: Model) -> Any | None:
        if (
            cls._hysteretic_batch_model_id == id(model)
            and cls._hysteretic_batch is not None
            and getattr(cls._hysteretic_batch, "model", None) is model
        ):
            return cls._hysteretic_batch
        return None

    @classmethod
    def assemble_k(
        cls,
        model: Model,
        ls: LinearSystem,
        alfa: float = 1.0,
        *,
        set_zero: bool = True,
        recompute_elements: bool = True,
    ) -> None:
        """Assemble the element stiffness selected by ``alfa``.

        The C# code first calls each element's ``ComputeK(alfa)`` and then
        scatters those current coefficients.  The earlier Python port always
        reassembled with ``alfa=0``, silently turning Standard Newton into
        Modified Newton.
        """
        if set_zero:
            ls.set_zero()
        ls.k = assemble_global_k(
            model, alfa=alfa, recompute_elements=recompute_elements
        ).tocsc()

    @classmethod
    def assemble_load(
        cls,
        model: Model,
        ls: LinearSystem,
        analysis_key: int | None = None,
        combination: int = 1,
    ) -> None:
        cls._ptarget = assemble_load_vector(model, analysis_key, combination)
        ls.set_zero_load()

    @classmethod
    def compute_ktang(cls, model: Model, ls: LinearSystem, alfa: float) -> int:
        runtime = cls.hysteretic_batch_for(model)
        if runtime is not None and alfa != 0.0:
            # Updated-tangent methods still use the object-level ComputeK port.
            # Publish dense trial tangents only when that path is requested.
            runtime.sync_all_to_objects()
        cls.compute_k(model, alfa)
        cls.assemble_k(
            model, ls, alfa=alfa, set_zero=True, recompute_elements=False
        )
        return 0

    @classmethod
    def compute_k(cls, model: Model, alfa: float = 1.0) -> None:
        for quad in model.collections.quads.values():
            quad.compute_k(alfa)
        for intf in model.collections.interfaces.values():
            intf.compute_k(alfa)

    @classmethod
    def form_unbalance(cls, model: Model, ls: LinearSystem, an: Any) -> None:
        cls.get_resisting_force(model, ls)
        fext = cls._fext if cls._fext is not None else np.zeros(ls.n)
        pq = cls._pq if cls._pq is not None else np.zeros(ls.n)
        residual_external = fext + pq if pdelta_enabled(getattr(an, "pdelta_effect", None)) else fext
        ls.b[: min(ls.n, len(residual_external))] += residual_external[:ls.n]

    @classmethod
    def get_resisting_force(cls, model: Model, ls: LinearSystem) -> None:
        ls.set_zero_load()
        runtime = cls.hysteretic_batch_for(model)
        if runtime is not None:
            runtime.copy_resisting_force_to(ls.b)
            for quad in runtime.unmanaged_quads:
                if quad.spring is None or len(quad.aff) <= 6:
                    continue
                quad.set_resisting_force()
                for entry in quad.aff[6]:
                    gdl = entry.gdl - 1
                    if 0 <= gdl < ls.n:
                        ls.sumb(gdl, -quad.status.f * entry.alfa)
            for intf in runtime.unmanaged_interfaces:
                intf.get_resisting_force(ls)
        else:
            for quad in model.collections.quads.values():
                if quad.spring is None or len(quad.aff) <= 6:
                    continue
                quad.set_resisting_force()
                for entry in quad.aff[6]:
                    gdl = entry.gdl - 1
                    if 0 <= gdl < ls.n:
                        ls.sumb(gdl, -quad.status.f * entry.alfa)
            for intf in model.collections.interfaces.values():
                intf.get_resisting_force(ls)

    @classmethod
    def update_domain(cls, model: Model, ls: LinearSystem, state: IntegratorState) -> None:
        # C# updates interfaces before quads. Quad.ComputeDN depends on the
        # transverse interface spring increments produced in this same trial.
        runtime = cls.hysteretic_batch_for(model)
        if runtime is not None:
            runtime.update_domain(ls.x, state)
            for intf in runtime.unmanaged_interfaces:
                intf.update_domain(ls.x, state)
        else:
            for intf in model.collections.interfaces.values():
                intf.update_domain(ls.x, state)
        if runtime is not None:
            for quad in runtime.unmanaged_quads:
                quad.update_domain(ls, state, model.collections)
        else:
            for quad in model.collections.quads.values():
                quad.update_domain(ls, state, model.collections)

    @classmethod
    def compute_energy(cls, model: Model) -> tuple[float, float]:
        runtime = cls.hysteretic_batch_for(model)
        eel, ed = runtime.compute_energy() if runtime is not None else (0.0, 0.0)
        elements = (
            [*runtime.unmanaged_quads, *runtime.unmanaged_interfaces]
            if runtime is not None
            else [
                *model.collections.quads.values(),
                *model.collections.interfaces.values(),
            ]
        )
        for element in elements:
            de_el, de_pl, _ = element.compute_energy()
            eel += float(de_el)
            ed += float(de_pl)
        return eel, ed

    @classmethod
    def find_max_u(cls, model: Model, p: Program) -> None:
        runtime = cls.hysteretic_batch_for(model)
        if runtime is not None:
            max_u, max_key, max_type = runtime.cached_max_u()
            collections = (
                ("Quad", runtime.unmanaged_quads),
                ("Interface", runtime.unmanaged_interfaces),
            )
            for kind, elements in collections:
                for element in elements:
                    value = abs(float(element.max_u()))
                    if value > max_u:
                        max_u = value
                        max_key = int(getattr(element, "key", 0))
                        max_type = kind
        else:
            max_u = 0.0
            max_key = 0
            max_type = ""
            for kind, collection in (
                ("Quad", model.collections.quads.values()),
                ("Interface", model.collections.interfaces.values()),
            ):
                for element in collection:
                    value = abs(float(element.max_u()))
                    if value > max_u:
                        max_u = value
                        max_key = int(getattr(element, "key", 0))
                        max_type = kind
        p.max_u = max_u
        p.elem_max_u_key = max_key
        p.elem_max_u_type = max_type

    @classmethod
    def get_dof_for_max_displacement(cls, p: Program, model: Model, an: Any) -> int:
        del model
        master = int(getattr(an, "master_point", -10))
        # HRX/C# external DOF identifiers are commonly one-based; accept a
        # valid zero-based value too and clamp only at the usage site.
        if master != -10:
            return master
        if p.u is not None and len(p.u):
            return int(np.argmax(np.abs(p.u)))
        return 0
