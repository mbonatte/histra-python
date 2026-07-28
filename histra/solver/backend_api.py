"""High-level in-process API intended for orchestration backends."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import time
from typing import Any, Callable, Iterable, Mapping

from histra.io.hr_loader import load_model
from histra.solver.cancellation import CancelCheck, SolverCancelled
from histra.solver.capabilities import inspect_solver_capabilities
from histra.solver.interface_material import InterfaceMaterialMutationReport
from histra.solver.outcomes import AnalysisExecution, AnalysisOutcome
from histra.solver.output_projection import project_analysis_outputs
from histra.solver.session import AnalysisSession


@dataclass(frozen=True)
class ConcreteInterfaceMutation:
    """Backend-ready interface mutation using resolved HRX keys."""

    interface_keys: tuple[int, ...]
    material_key: int
    preserve_committed_state: bool = True


@dataclass(frozen=True)
class PythonAnalysisRequest:
    name: str
    output_request: Any
    timeout_seconds: float


@dataclass(frozen=True)
class PythonAnalysisResult:
    execution: AnalysisExecution
    outputs: Mapping[str, Any]
    mutation: InterfaceMaterialMutationReport | None = None


@dataclass(frozen=True)
class PythonSolverJobResult:
    analyses: Mapping[str, PythonAnalysisResult]
    executions: tuple[AnalysisExecution, ...]
    logs: tuple[str, ...]
    model_path: Path
    metadata: Mapping[str, Any] = field(default_factory=dict)


class PythonSolverJobError(RuntimeError):
    """Raised when an analysis cannot produce a completed backend result."""

    def __init__(self, execution: AnalysisExecution):
        super().__init__(
            f"Analysis {execution.analysis_name!r} ended as "
            f"{(execution.outcome or AnalysisOutcome.FAILED).value}: "
            f"{execution.message or 'no diagnostic message'}"
        )
        self.execution = execution


class PythonSolverTimeout(TimeoutError):
    """Raised when a job-wide or per-analysis deadline expires."""


def run_python_solver_job(
    model_path: str | Path,
    analyses: Iterable[PythonAnalysisRequest],
    *,
    timeout_seconds: float,
    interface_mutations: Mapping[str, ConcreteInterfaceMutation] | None = None,
    combination_row: int = 1,
    on_log: Callable[[str], None] | None = None,
    on_progress: Callable[[float], None] | None = None,
    should_cancel: CancelCheck | None = None,
) -> PythonSolverJobResult:
    """Run an HRX analysis plan entirely in process.

    The mutation mapping deliberately uses concrete interface/material keys.
    Translation from bridge/pier scour semantics remains an orchestration concern
    until those bridge entities are represented by the Python domain model.
    """
    job_timeout = float(timeout_seconds)
    if job_timeout <= 0.0:
        raise ValueError("timeout_seconds must be positive.")

    requested = tuple(analyses)
    if not requested:
        raise ValueError("At least one analysis request is required.")
    for request in requested:
        if float(request.timeout_seconds) <= 0.0:
            raise ValueError(
                f"Analysis {request.name!r} timeout_seconds must be positive."
            )

    path = Path(model_path)
    model = load_model(path)
    output_requests = {request.name: request.output_request for request in requested}
    capability_report = inspect_solver_capabilities(
        model,
        [request.name for request in requested],
        output_requests=output_requests,
    )
    capability_report.require_supported()

    captured_logs: list[str] = []

    def log(message: str) -> None:
        captured_logs.append(str(message))
        if on_log is not None:
            on_log(str(message))

    session = AnalysisSession(
        model,
        combination_row=combination_row,
        on_log=log,
        on_progress=on_progress,
    )
    request_by_name = {request.name.casefold(): request for request in requested}
    run_order = _dependency_order(session, requested)
    implicit_timeout = max(float(request.timeout_seconds) for request in requested)
    mutations = interface_mutations or {}
    mutation_by_name = {name.casefold(): value for name, value in mutations.items()}
    job_deadline = time.monotonic() + job_timeout
    results: dict[str, PythonAnalysisResult] = {}

    for definition in run_order:
        name = str(definition.name)
        request = request_by_name.get(name.casefold())
        analysis_timeout = (
            float(request.timeout_seconds) if request is not None else implicit_timeout
        )
        analysis_deadline = min(job_deadline, time.monotonic() + analysis_timeout)
        if analysis_deadline <= time.monotonic():
            raise PythonSolverTimeout(
                f"Deadline expired before analysis {name!r} could start."
            )

        mutation_report: InterfaceMaterialMutationReport | None = None
        mutation = mutation_by_name.get(name.casefold())
        if mutation is not None:
            mutation_report = session.change_interface_materials(
                mutation.interface_keys,
                mutation.material_key,
                preserve_committed_state=mutation.preserve_committed_state,
            )

        def analysis_cancelled() -> bool:
            return (
                time.monotonic() >= analysis_deadline
                or (should_cancel is not None and bool(should_cancel()))
            )

        execution = session.run(definition, should_cancel=analysis_cancelled)
        if not execution.completed:
            if time.monotonic() >= analysis_deadline:
                raise PythonSolverTimeout(
                    f"Analysis {name!r} exceeded its effective timeout."
                )
            if execution.outcome is AnalysisOutcome.CANCELLED:
                raise SolverCancelled(
                    f"Analysis {name!r} was cancelled by the caller."
                )
            raise PythonSolverJobError(execution)

        if request is not None:
            results[request.name] = PythonAnalysisResult(
                execution=execution,
                outputs=project_analysis_outputs(
                    model,
                    execution,
                    request.output_request,
                ),
                mutation=mutation_report,
            )

    return PythonSolverJobResult(
        analyses=results,
        executions=tuple(session.executions),
        logs=tuple(captured_logs),
        model_path=path,
        metadata={
            "combination_row": int(combination_row),
            "serialized_in_process": True,
        },
    )


def _dependency_order(
    session: AnalysisSession,
    requested: Iterable[PythonAnalysisRequest],
) -> tuple[Any, ...]:
    ordered: list[Any] = []
    seen: set[int] = set()
    for request in requested:
        for definition in session.dependency_chain(request.name):
            key = int(definition.key)
            if key not in seen:
                seen.add(key)
                ordered.append(definition)
    return tuple(ordered)
