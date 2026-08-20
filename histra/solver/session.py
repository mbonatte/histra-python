"""In-memory execution of HRX-defined chained nonlinear analyses."""
from __future__ import annotations

import copy
import time
from typing import Any, Callable, Iterable

import numpy as np

from histra.postprocessing import compute_total_reaction
from histra.solver.cancellation import CancelCheck
from histra.solver.interface_material import (
    InterfaceMaterialMutationReport,
    change_interface_materials,
)
from histra.solver.outcomes import (
    AnalysisExecution,
    AnalysisOutcome,
    AnalysisStep,
    classify_analysis_outcome,
)
from histra.solver.modal import solve_modal_analysis
from histra.solver.solve import solve_static_nonlinear


class AnalysisSessionError(RuntimeError):
    """Raised when an HRX analysis chain is inconsistent with session state."""


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
        self._tainted_reason: str | None = None

    @property
    def usable(self) -> bool:
        """Whether the session can safely start another analysis."""
        return self._tainted_reason is None

    def _require_usable(self) -> None:
        if self._tainted_reason is not None:
            raise AnalysisSessionError(
                "This analysis session cannot be reused after an incomplete solve: "
                f"{self._tainted_reason}. Reload the HRX and create a new session."
            )

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
        self._require_usable()
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
        should_cancel: CancelCheck | None = None,
    ) -> AnalysisExecution:
        self._require_usable()
        definition = copy.deepcopy(self.resolve_analysis(analysis))
        initial_key = int(getattr(definition, "initial_analysis_key", -100))
        kwargs: dict[str, Any] = {}
        if initial_key < 0:
            if self.current_analysis_key is not None:
                raise AnalysisSessionError(
                    f"Analysis {definition.key}:{definition.name} is virgin but session "
                    f"already contains committed analysis {self.current_analysis_key}."
                )
            initial_step = AnalysisStep.initial(np.zeros(int(self.model.gdl), dtype=float))
        else:
            if self.current_analysis_key != initial_key or self.current_displacement is None:
                raise AnalysisSessionError(
                    f"Analysis {definition.key}:{definition.name} requires predecessor "
                    f"{initial_key}, but current session predecessor is "
                    f"{self.current_analysis_key}."
                )
            predecessor_reaction = compute_total_reaction(self.model)
            initial_step = AnalysisStep.initial(
                self.current_displacement,
                reaction_x=predecessor_reaction.x,
                reaction_y=predecessor_reaction.y,
                reaction_z=predecessor_reaction.z,
            )
            kwargs.update(
                initial_displacement=self.current_displacement,
                restart_from_current_state=True,
            )

        started = time.perf_counter()
        try:
            if int(getattr(definition, "analysis_type", 0)) == 5:
                modal_result = solve_modal_analysis(
                    self.model,
                    definition,
                    self.combination_row,
                    on_log=self.on_log,
                    on_progress=self.on_progress,
                    should_cancel=should_cancel,
                    **kwargs,
                )
                code = 0
                raw_steps: list[dict[str, Any]] = []
            else:
                modal_result = None
                code, raw_steps = solve_static_nonlinear(
                    self.model,
                    definition,
                    self.combination_row,
                    on_log=self.on_log,
                    on_progress=self.on_progress,
                    max_committed_steps=max_committed_steps,
                    should_cancel=should_cancel,
                    **kwargs,
                )
        except Exception as exc:
            self._tainted_reason = f"{type(exc).__name__}: {exc}"
            raise
        runtime = time.perf_counter() - started
        steps = tuple(AnalysisStep.from_mapping(step) for step in raw_steps)
        outcome = classify_analysis_outcome(int(code), steps, definition)
        execution = AnalysisExecution(
            analysis_key=int(definition.key),
            analysis_name=str(definition.name),
            code=int(code),
            steps=steps,
            runtime_seconds=float(runtime),
            outcome=outcome,
            message=_outcome_message(outcome),
            initial_step=initial_step,
            modal_result=modal_result,
        )
        committed = execution.committed_steps
        if execution.completed and execution.modal_result is not None:
            self.current_analysis_key = int(definition.key)
            self.current_displacement = initial_step.u.copy()
        elif execution.completed and committed:
            self.current_analysis_key = int(definition.key)
            self.current_displacement = committed[-1].u.copy()
        elif not execution.completed:
            self._tainted_reason = (
                f"analysis {definition.key}:{definition.name} ended as {outcome.value}"
            )
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
        should_cancel: CancelCheck | None = None,
    ) -> tuple[AnalysisExecution, ...]:
        """Run the HRX dependency chain, optionally mutating at boundaries."""
        results: list[AnalysisExecution] = []
        for analysis in self.dependency_chain(target):
            if before_analysis is not None:
                before_analysis(self, analysis)
            results.append(self.run(analysis, should_cancel=should_cancel))
        return tuple(results)

    def run_sequence(
        self,
        analyses: Iterable[int | str | Any],
        *,
        should_cancel: CancelCheck | None = None,
    ) -> tuple[AnalysisExecution, ...]:
        return tuple(
            self.run(analysis, should_cancel=should_cancel) for analysis in analyses
        )


def _outcome_message(outcome: AnalysisOutcome) -> str:
    if outcome is AnalysisOutcome.COMPLETED:
        return "Analysis completed."
    if outcome is AnalysisOutcome.COMPLETED_AT_DISPLACEMENT_LIMIT:
        return "Analysis reached its configured element displacement limit."
    if outcome is AnalysisOutcome.CANCELLED:
        return "Analysis was cancelled and its active trial step was rolled back."
    if outcome is AnalysisOutcome.NONCONVERGED:
        return "Analysis did not converge."
    return f"Analysis ended as {outcome.value}."
