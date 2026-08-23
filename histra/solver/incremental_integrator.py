from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import numpy as np

from histra.solver.model_manager import ModelManager, pdelta_enabled
from histra.types.integrator_state import IntegratorState
from histra.types.linear_system import LinearSystem


class IncrementalIntegrator(ABC):
    """Base state and operations shared by static integrators.

    This follows the original C# separation between the total displacement
    ``U``, the last committed displacement ``U_commited`` and the current
    linear-system increment ``LS.X``.
    """

    def __init__(self) -> None:
        self.state = IntegratorState()
        self.u: np.ndarray | None = None
        self.v: np.ndarray | None = None
        self.u_committed: np.ndarray | None = None
        self.errors: list[str] = []

    @property
    def step(self) -> int:
        return self.state.step

    @step.setter
    def step(self, value: int) -> None:
        self.state.step = int(value)

    @property
    def iteration(self) -> int:
        return getattr(self.state, "iteration", 0)

    @iteration.setter
    def iteration(self, value: int) -> None:
        self.state.iteration = int(value)

    @property
    def incr_mult(self) -> float:
        return getattr(self.state, "incr_mult", 0.0)

    @incr_mult.setter
    def incr_mult(self, value: float) -> None:
        self.state.incr_mult = float(value)

    @property
    def mult(self) -> float:
        return getattr(self.state, "mult", 0.0)

    @mult.setter
    def mult(self, value: float) -> None:
        self.state.mult = float(value)

    def form_unbalance(self, p: Any, model: Any, an: Any) -> None:
        ModelManager.form_unbalance(model, p.ls, an)

    def update_k(self, p: Any, model: Any, alfa: float, compute_c: bool = False) -> int:
        del compute_c
        return ModelManager.compute_ktang(model, p.ls, alfa)

    def compute_increment(
        self,
        p: Any,
        ls: LinearSystem,
        model: Any,
        an: Any,
        fixed_dofs: set[int] | None = None,
    ) -> np.ndarray:
        """Solve the active generalized-DOF system, as the C# solver does."""
        del p, model, an, fixed_dofs
        ls.solve()
        return ls.x

    def update_ptarget(
        self,
        p: Any,
        model: Any,
        an: Any,
        combination: int,
        iteration: int,
    ) -> bool:
        """Refresh load vectors and second-order P-Delta loads.

        Port of C# IncrementalIntegrator.UpdatePtarget.
        """
        pdelta = str(getattr(an, "pdelta_effect", "") or "").strip().lower()
        need_pdelta = (pdelta in ("eachiteration", "2")) or (pdelta in ("eachstep", "1") and iteration == 0)
        if getattr(an, "key", None) is not None:
            ModelManager.assemble_load(
                model, p.ls, an.key, combination, reuse_current=True
            )
        if need_pdelta:
            ModelManager.compute_and_assemble_pdelta_load(
                model, p.ls, an, combination
            )
        if getattr(an, "key", None) is not None:
            return True
        return need_pdelta

    def revert_to_last_commit(self, model: Any, ls: LinearSystem) -> None:
        """Undo trial displacements and restore committed element states."""
        if self.u_committed is None or self.u is None:
            return
        correction = self.u_committed - self.u
        self.u[:] = self.u_committed
        ls.set_x_vector(correction)
        for collection_name in ("quads", "interfaces"):
            collection = getattr(model.collections, collection_name, {})
            for element in collection.values():
                element.revert_to_last_commit(ls)

    @abstractmethod
    def update(self, model: Any, p: Any, an: Any) -> int:
        raise NotImplementedError

    @abstractmethod
    def new_step(
        self,
        p: Any,
        model: Any,
        ls: LinearSystem,
        an: Any,
        combination: int,
        step: int,
        dof: int,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def commit(
        self,
        model: Any,
        an: Any,
        disp: float,
        dof_max: int,
        has_domain_changed: list[bool],
    ) -> bool:
        raise NotImplementedError

    def domain_changed(self, p: Any, model: Any, size: int) -> None:
        del p, model, size

    def get_time(self) -> float:
        return 0.0


class StaticIntegrator(IncrementalIntegrator):
    """Static-integrator base with load-domain accumulation and factory."""

    def apply_load_domain(self, model: Any, incr_mult: float) -> None:
        del model
        self.incr_mult = incr_mult
        self.mult += incr_mult
        if ModelManager._fext is None or ModelManager._ptarget is None:
            return
        n = min(len(ModelManager._fext), len(ModelManager._ptarget))
        ModelManager._fext[:n] += ModelManager._ptarget[:n] * incr_mult

    @staticmethod
    def new_static_integrator(an: Any, combination: int) -> "StaticIntegrator":
        method = str(getattr(an, "integration_method", "LoadControl"))
        if method == "ArcLength":
            from histra.solver.arc_length import ArcLength

            integrator: StaticIntegrator = ArcLength()
        elif method == "ArcLengthLinear":
            from histra.solver.arc_length import ArcLengthLinear

            integrator = ArcLengthLinear()
        else:
            from histra.solver.load_control import LoadControl

            integrator = LoadControl()
        integrator.state.analysis = an
        integrator.state.combination = combination
        return integrator
