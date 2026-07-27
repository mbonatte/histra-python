from __future__ import annotations

from typing import Any

import numpy as np

from histra.model.model import Model
from histra.solver.incremental_integrator import StaticIntegrator
from histra.solver.model_manager import ModelManager
from histra.solver.program import Program
from histra.types.linear_system import LinearSolveError, LinearSystem


class ArcLength(StaticIntegrator):
    """Arc-length integrator ported from the original C# implementation.

    The algorithm separates the residual displacement ``delta_u_bar`` from the
    reference-load displacement ``delta_u_hat`` and enforces the quadratic
    constraint over either a control DOF or all active generalized DOFs.

    Two apparent C# defects are intentionally corrected:

    * the adaptive radius is not reset to ``Analysis.Dr2`` at every step;
    * ``MaxArcLengthRay`` is compared with the radius, not radius-squared.
    """

    def __init__(self) -> None:
        super().__init__()
        self._target_displacement = 0.0
        self._target_displacement_base = 0.0
        self._arc_length2 = 0.0
        self._alpha2 = 0.0
        self._delta_u_hat: np.ndarray | None = None
        self._delta_u_bar: np.ndarray | None = None
        self._delta_u: np.ndarray | None = None
        self._delta_u_step: np.ndarray | None = None
        self._phat: np.ndarray | None = None
        self._phat_ref: np.ndarray | None = None
        self._delta_lambda_step = 0.0
        self._current_lambda = 0.0
        self._adapt_exponent = 0.5
        self._dofs: np.ndarray | None = None
        self._lf_items: list[tuple[float, float]] = []
        self._current_lf_item = 1
        self._initialized = False
        self._step_snapshot: dict[str, Any] | None = None

    def _load_items(self, an: Any) -> list[tuple[float, float]]:
        items = list(getattr(getattr(an, "load_function", None), "items", []) or [])
        values = sorted(
            [(float(item.pseudo_time), float(item.multiplier)) for item in items],
            key=lambda item: item[0],
        )
        return values if len(values) >= 2 else [(0.0, 0.0), (1.0, 1.0)]

    def _segment_sign(self) -> float:
        previous = self._lf_items[self._current_lf_item - 1][1]
        current = self._lf_items[self._current_lf_item][1]
        sign = float(np.sign(current - previous))
        return sign if sign != 0.0 else 1.0

    def _select_dofs(self, p: Program, an: Any, fallback_dof: int | None = None) -> np.ndarray:
        n = p.ls.n
        procedure = str(getattr(an, "arc_length_procedure", "OnlyControlPoint")).lower()
        if "only" not in procedure and "control" not in procedure:
            return np.arange(n, dtype=int)

        master = int(getattr(an, "master_point", -10))
        candidate = fallback_dof if master == -10 else master
        if candidate is not None and 0 <= int(candidate) < n:
            return np.array([int(candidate)], dtype=int)

        # C# auto-selection maximizes deltaUhat[i] * phat[i].
        if self._delta_u_hat is not None and self._phat is not None and n:
            products = self._delta_u_hat * self._phat
            return np.array([int(np.argmax(products))], dtype=int)
        return np.array([0], dtype=int) if n else np.zeros(0, dtype=int)

    def _selected(self, vector: np.ndarray) -> np.ndarray:
        if self._dofs is None or len(self._dofs) == 0:
            return vector
        return vector[self._dofs]

    def _refresh_segment_load(self) -> None:
        if self._phat_ref is None:
            return
        self._phat = self._segment_sign() * self._phat_ref
        ModelManager._ptarget = self._phat.copy()
        multiplier = self._lf_items[self._current_lf_item][1]
        self._target_displacement = self._target_displacement_base * multiplier

    def domain_changed(self, p: Program, model: Model, size: int) -> None:
        del model
        an = self.state.analysis
        if not self._initialized:
            self._lf_items = self._load_items(an)
            self._current_lf_item = min(1, len(self._lf_items) - 1)
            self._target_displacement_base = float(getattr(an, "target_displacement", 0.0))
            self._arc_length2 = abs(float(getattr(an, "dr2", 1e-4)))
            self._alpha2 = 0.0
            self._phat_ref = np.asarray(ModelManager._ptarget, dtype=float).copy()
            self._initialized = True

        self._delta_u_hat = np.zeros(size)
        self._delta_u_bar = np.zeros(size)
        self._delta_u = np.zeros(size)
        self._delta_u_step = np.zeros(size)
        self._current_lambda = 0.0
        self._delta_lambda_step = 0.0
        self._refresh_segment_load()
        self._dofs = None

        # Determine a stable automatic control DOF when no explicit point is
        # supplied.  A valid initial stiffness has already been assembled.
        if int(getattr(an, "master_point", -10)) == -10 and size:
            try:
                p.ls.solve(rhs=self._phat)
                self._delta_u_hat[:] = p.ls.x
                self._dofs = self._select_dofs(p, an)
            except LinearSolveError:
                self._dofs = np.array([0], dtype=int)

    def new_step(
        self,
        p: Program,
        model: Model,
        ls: LinearSystem,
        an: Any,
        combination: int,
        step: int,
        dof: int,
    ) -> None:
        self.step = step
        self.iteration = 0
        self._step_snapshot = {
            "u": None if self.u is None else self.u.copy(),
            "fext": None if ModelManager._fext is None else ModelManager._fext.copy(),
            "mult": self.mult,
            "lambda": self._current_lambda,
            "delta_lambda_step": self._delta_lambda_step,
            "delta_u_step": None if self._delta_u_step is None else self._delta_u_step.copy(),
        }

        if self.update_ptarget(p, model, an, combination, self.iteration):
            self._phat_ref = np.asarray(ModelManager._ptarget, dtype=float).copy()
            self._refresh_segment_load()
        if self._phat is None:
            raise RuntimeError("ArcLength reference load is not initialized")

        ls.solve(rhs=self._phat)
        self._delta_u_hat = ls.x.copy()
        self._dofs = self._select_dofs(p, an, fallback_dof=dof)
        selected_hat = self._selected(self._delta_u_hat)
        denominator = float(np.dot(selected_hat, selected_hat) + self._alpha2)
        if denominator <= 1e-30:
            raise LinearSolveError("ArcLength has a zero reference-load displacement")

        # OnlyControlPoint in C# scales Dr2 by the selected DOF count.
        radius2 = self._arc_length2
        if "only" in str(getattr(an, "arc_length_procedure", "")).lower():
            radius2 *= max(1, len(self._dofs))

        delta_lambda = float(np.sqrt(radius2 / denominator))
        if bool(getattr(an, "is_max_arc_length_ray", False)):
            max_radius = abs(float(getattr(an, "max_arc_length_ray", 1.0)))
            if max_radius > 0.0 and np.sqrt(radius2) > max_radius:
                radius2 = max_radius * max_radius
                self._arc_length2 = radius2
                delta_lambda = float(np.sqrt(radius2 / denominator))

        selected_load = self._selected(self._phat)
        if delta_lambda * float(np.dot(selected_hat, selected_load)) < 0.0:
            delta_lambda *= -1.0

        self._delta_lambda_step = delta_lambda
        self._current_lambda += delta_lambda
        self._delta_u = delta_lambda * self._delta_u_hat
        self._delta_u_step[:] = self._delta_u
        ls.set_x_vector(self._delta_u)
        if self.u is not None:
            self.u += self._delta_u
        self.apply_load_domain(model, delta_lambda)
        ModelManager.update_domain(model, ls, self.state)

        display_radius = np.sqrt(radius2 / max(1, len(self._dofs)))
        p.log(
            f"Step {step} solving: dr={display_radius:.6g}, "
            f"dLambda={delta_lambda:.6g}"
        )

    def update(self, model: Model, p: Program, an: Any) -> int:
        self.iteration += 1
        ls = p.ls
        self._delta_u_bar = ls.x.copy()
        if self._phat is None or self._delta_u_step is None:
            self.errors.append("ArcLength is not initialized")
            return -10

        try:
            ls.solve(rhs=self._phat)
        except LinearSolveError as exc:
            self.errors.append(f"ArcLength reference-load solve failed: {exc}")
            return -10
        self._delta_u_hat = ls.x.copy()

        hat = self._selected(self._delta_u_hat)
        bar = self._selected(self._delta_u_bar)
        step = self._selected(self._delta_u_step)

        a = self._alpha2 + float(np.dot(hat, hat))
        b = 2.0 * (
            self._alpha2 * self._delta_lambda_step
            + float(np.dot(hat, bar))
            + float(np.dot(step, hat))
        )
        c = 2.0 * float(np.dot(step, bar)) + float(np.dot(bar, bar))

        if abs(a) < 1e-30:
            if abs(b) < 1e-30:
                self.errors.append("ArcLength constraint has zero reference load and denominator")
                return -10
            delta_lambda = -c / b
        else:
            discriminant = b * b - 4.0 * a * c
            if discriminant < 0.0:
                # Same fallback as C#, with denominator checking and a coherent
                # direction choice.
                numerator = float(np.dot(step, bar))
                denominator = float(np.dot(step, hat)) + self._alpha2 * self._delta_lambda_step
                if abs(denominator) < 1e-30:
                    self.errors.append("ArcLength linearized constraint denominator is zero")
                    return -10
                delta_lambda = -numerator / denominator
                if self._phat is not None:
                    if delta_lambda * float(np.dot(hat, self._selected(self._phat))) < 0.0:
                        delta_lambda *= -1.0
            else:
                root = float(np.sqrt(discriminant))
                dl1 = (-b + root) / (2.0 * a)
                dl2 = (-b - root) / (2.0 * a)
                directional = float(np.dot(hat, step))
                criterion1 = float(np.dot(step, step) + np.dot(bar, step) + dl1 * directional)
                delta_lambda = dl1 if criterion1 > 0.0 else dl2

        self._delta_u = self._delta_u_bar + delta_lambda * self._delta_u_hat
        self._delta_u_step += self._delta_u
        self._delta_lambda_step += delta_lambda
        self._current_lambda += delta_lambda
        ls.set_x_vector(self._delta_u)
        if self.u is not None:
            self.u += self._delta_u
        ModelManager.update_domain(model, ls, self.state)
        self.apply_load_domain(model, delta_lambda)
        return 0

    def revert_failed_step(self, model: Model, ls: LinearSystem) -> None:
        if self._step_snapshot is None:
            self.revert_to_last_commit(model, ls)
            return
        snapshot = self._step_snapshot
        if snapshot["fext"] is not None and ModelManager._fext is not None:
            ModelManager._fext[:] = snapshot["fext"]
        self.mult = snapshot["mult"]
        self._current_lambda = snapshot["lambda"]
        self._delta_lambda_step = snapshot["delta_lambda_step"]
        if snapshot["delta_u_step"] is not None and self._delta_u_step is not None:
            self._delta_u_step[:] = snapshot["delta_u_step"]
        self.revert_to_last_commit(model, ls)

    def commit(
        self,
        model: Model,
        an: Any,
        disp: float,
        dof_max: int,
        has_domain_changed: list[bool],
    ) -> bool:
        del model, dof_max
        if self.u_committed is not None and self.u is not None:
            self.u_committed[:] = self.u

        previous_multiplier = self._lf_items[self._current_lf_item - 1][1]
        target_multiplier = self._lf_items[self._current_lf_item][1]
        increasing = target_multiplier - previous_multiplier > 0.0
        reached = disp >= self._target_displacement if increasing else disp <= self._target_displacement

        if reached and self._current_lf_item < len(self._lf_items) - 1:
            self._current_lf_item += 1
            has_domain_changed[0] = True
            reached = False

        if bool(getattr(an, "update_dr2", False)):
            desired = max(1.0, float(getattr(an, "desired_iterations", 5)))
            actual = max(1.0, float(self.iteration))
            self._arc_length2 *= (desired / actual) ** self._adapt_exponent

        if bool(getattr(an, "is_max_arc_length_ray", False)):
            max_radius = abs(float(getattr(an, "max_arc_length_ray", 1.0)))
            if max_radius > 0.0:
                self._arc_length2 = min(self._arc_length2, max_radius * max_radius)
        return reached

    def get_time(self) -> float:
        return float(self.step)


class ArcLengthLinear(ArcLength):
    """Linear arc-length variant using the same corrected constraint machinery."""
