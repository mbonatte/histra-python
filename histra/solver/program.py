from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from histra.solver.cancellation import CancelCheck, raise_if_cancelled


@dataclass
class Program:
    """Runtime vectors, status and callbacks used by the solver."""

    gdl: int = 0
    ls: Any | None = None
    u: Any | None = None
    v: Any | None = None
    max_u: float = 0.0
    elem_max_u_key: int = 0
    elem_max_u_type: str = ""
    to_stop: bool = False
    index_fact_k: int = 0
    current_load_factor: float = 0.0
    on_log: Any | None = None
    on_progress: Any | None = None
    should_cancel: CancelCheck | None = None
    diagnostics: Any | None = None

    def log(self, msg: str) -> None:
        if self.on_log:
            self.on_log(msg)
        else:
            import logging

            logging.getLogger(__name__).info(msg)

    def progress(self, val: float) -> None:
        self.check_cancelled()
        if self.on_progress:
            self.on_progress(float(val))

    def check_cancelled(self) -> None:
        """Raise at a solver-safe checkpoint when cancellation is requested."""
        raise_if_cancelled(self.should_cancel)

    def get_value_graph_analysis(
        self,
        collections: Any,
        an: Any,
        dof: int,
        reaction_sum: Any,
        out_displ: list,
    ) -> list[float]:
        """Return the core force/displacement pair used by solver monitoring.
        Full C# graph extraction can sum reactions and query model points.  This
        snapshot lacks those subsystems, so it returns the actual integrator
        load factor and a real generalized displacement instead of the former
        hard-coded load factor ``1.0``.
        """
        del collections, an, reaction_sum, out_displ
        displacement = 0.0
        if self.u is not None and 0 <= int(dof) < len(self.u):
            displacement = float(self.u[int(dof)])
        return [float(self.current_load_factor), displacement]
    def add_value_graph_static_analysis(
        self,
        collections: Any,
        an: Any,
        values: list,
        ref_values: list,
        dof: int,
        step: int,
        time: float,
    ) -> None:
        del collections, an, values, ref_values, dof, step, time
