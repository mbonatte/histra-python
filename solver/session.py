"""In-memory execution of HRX-defined chained nonlinear analyses."""
from __future__ import annotations

import copy
import time
from dataclasses import dataclass
from typing import Any, Callable, Iterable

import numpy as np

from histra.solver.interface_material import (
    InterfaceMaterialMutationReport,
    change_interface_materials,
)
from histra.solver.solve import solve_static_nonlinear


class AnalysisSessionError(RuntimeError):
    """Raised when an HRX analysis chain is inconsistent with session state."""


@dataclass(frozen=True)
class AnalysisExecution:
    analysis_key: int
    analysis_name: str
    code: int
    steps: tuple[dict[str, Any], ...]
    runtime_seconds: float

    @property
    def committed_steps(self) -> tuple[dict[str, Any], ...]:
        return tuple(step for step in self.steps if step.get("status") == "OK")

    @property
    def completed(self) -> bool:
        return self.code == 0


class AnalysisSession:
    """Keep model and constitutive state alive across HRX analyses.

    The HRX remains authoritative for each analysis' predecessor, method,
    integration settings, load combinations and stopping criteria.  This class
    only manages the in-memory committed state and boundary mutations.
    """

    def __init__(
        self,
        model: Any,
        *,
        combination_row: int = 1,
        on_log: Callable[[str], None] | None = None,
        on_progress: Callable[[float], None] | None = None,
    ) -> None:
        if model.collections is None:
            raise AnalysisSessionError("Model.collections is not initialized.")
        self.model = model
        self.combination_row = int(combination_row)
        self.on_log = on_log
        self.on_progress = on_progress
        self.current_analysis_key: int | None = None
        self.current_displacement: np.ndarray | None = None
        self.executions: list[AnalysisExecution] = []
        self.mutations: list[InterfaceMaterialMutationReport] = []

    def resolve_analysis(self, analysis: int | str | Any) -> Any:
        if hasattr(analysis, "key") and hasattr(analysis, "name"):
            return analysis
        if isinstance(analysis, int) or str(analysis).lstrip("-").isdigit():
            key = int(analysis)
            try:
                return self.model.collections.analyses[key]
            except KeyError as exc:
                raise AnalysisSessionError(f"Analysis key {key} is absent from the HRX.") from exc
        name = str(analysis)
        matches = [
            item for item in self.model.collections.analyses.values()
            if item.name.casefold() == name.casefold()
        ]
        if len(matches) != 1:
            raise AnalysisSessionError(
                f"Expected one HRX analysis named {name!r}, found {len(matches)}."
            )
        return matches[0]

    def change_interface_materials(
        self,
        interface_keys: Iterable[int],
        material_key: int,
        *,
        preserve_committed_state: bool = True,
    ) -> InterfaceMaterialMutationReport:
        report = change_interface_materials(
            self.model,
            interface_keys,
            material_key,
            preserve_committed_state=preserve_committed_state,
        )
        self.mutations.append(report)
        if self.on_log is not None:
            self.on_log(
                f"Changed {report.interface_count} interfaces to material "
                f"{report.material_key}; rebuilt {report.spring_count} springs"
            )
        return report

    def run(
        self,
        analysis: int | str | Any,
        *,
        max_committed_steps: int | None = None,
    ) -> AnalysisExecution:
        definition = copy.deepcopy(self.resolve_analysis(analysis))
        initial_key = int(getattr(definition, "initial_analysis_key", -100))
        kwargs: dict[str, Any] = {}
        if initial_key < 0:
            if self.current_analysis_key is not None:
                raise AnalysisSessionError(
                    f"Analysis {definition.key}:{definition.name} is virgin but session "
                    f"already contains committed analysis {self.current_analysis_key}."
                )
        else:
            if self.current_analysis_key != initial_key or self.current_displacement is None:
                raise AnalysisSessionError(
                    f"Analysis {definition.key}:{definition.name} requires predecessor "
                    f"{initial_key}, but current session predecessor is "
                    f"{self.current_analysis_key}."
                )
            kwargs.update(
                initial_displacement=self.current_displacement,
                restart_from_current_state=True,
            )

        started = time.perf_counter()
        code, steps = solve_static_nonlinear(
            self.model,
            definition,
            self.combination_row,
            on_log=self.on_log,
            on_progress=self.on_progress,
            max_committed_steps=max_committed_steps,
            **kwargs,
        )
        runtime = time.perf_counter() - started
        execution = AnalysisExecution(
            analysis_key=int(definition.key),
            analysis_name=str(definition.name),
            code=int(code),
            steps=tuple(steps),
            runtime_seconds=float(runtime),
        )
        committed = execution.committed_steps
        if committed:
            self.current_analysis_key = int(definition.key)
            self.current_displacement = np.asarray(committed[-1]["u"], dtype=float).copy()
        self.executions.append(execution)
        return execution

    def dependency_chain(self, target: int | str | Any) -> tuple[Any, ...]:
        """Return the HRX-defined predecessor chain ending at ``target``."""
        chain: list[Any] = []
        seen: set[int] = set()
        current = self.resolve_analysis(target)
        while True:
            key = int(current.key)
            if key in seen:
                raise AnalysisSessionError(
                    f"Cycle detected in HRX analysis dependencies at key {key}."
                )
            seen.add(key)
            chain.append(current)
            predecessor = int(getattr(current, "initial_analysis_key", -100))
            if predecessor < 0:
                break
            try:
                current = self.model.collections.analyses[predecessor]
            except KeyError as exc:
                raise AnalysisSessionError(
                    f"Analysis {key}:{current.name} requires missing predecessor "
                    f"{predecessor}."
                ) from exc
        chain.reverse()
        return tuple(chain)

    def run_to(
        self,
        target: int | str | Any,
        *,
        before_analysis: Callable[["AnalysisSession", Any], None] | None = None,
    ) -> tuple[AnalysisExecution, ...]:
        """Run the HRX dependency chain, optionally mutating at boundaries."""
        results: list[AnalysisExecution] = []
        for analysis in self.dependency_chain(target):
            if before_analysis is not None:
                before_analysis(self, analysis)
            results.append(self.run(analysis))
        return tuple(results)

    def run_sequence(self, analyses: Iterable[int | str | Any]) -> tuple[AnalysisExecution, ...]:
        return tuple(self.run(analysis) for analysis in analyses)
