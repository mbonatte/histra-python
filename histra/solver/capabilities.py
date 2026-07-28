"""Preflight checks for running an HRX job with the Python solver."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from histra.solver.model_manager import pdelta_enabled


@dataclass(frozen=True)
class SolverCapabilityIssue:
    code: str
    message: str
    analysis_name: str | None = None


@dataclass(frozen=True)
class SolverCapabilityReport:
    supported: bool
    issues: tuple[SolverCapabilityIssue, ...]

    def require_supported(self) -> None:
        if self.supported:
            return
        details = "; ".join(
            f"{issue.analysis_name}: {issue.message}" if issue.analysis_name else issue.message
            for issue in self.issues
        )
        raise UnsupportedSolverCapability(details)


class UnsupportedSolverCapability(RuntimeError):
    """Raised when preflight detects unsupported model or output features."""


def inspect_solver_capabilities(
    model: Any,
    analysis_names: Iterable[str],
    *,
    output_requests: Mapping[str, Any] | None = None,
) -> SolverCapabilityReport:
    issues: list[SolverCapabilityIssue] = []
    collections = getattr(model, "collections", None)
    if collections is None:
        return SolverCapabilityReport(
            supported=False,
            issues=(SolverCapabilityIssue("MODEL_NOT_LOADED", "Model.collections is not initialized."),),
        )

    analyses = getattr(collections, "analyses", {})
    by_name: dict[str, list[Any]] = {}
    for analysis in analyses.values():
        by_name.setdefault(str(getattr(analysis, "name", "")).casefold(), []).append(analysis)

    resolved: dict[str, Any] = {}
    for requested_name in analysis_names:
        matches = by_name.get(str(requested_name).casefold(), [])
        if len(matches) != 1:
            issues.append(
                SolverCapabilityIssue(
                    "ANALYSIS_NOT_UNIQUE",
                    f"Expected exactly one analysis, found {len(matches)}.",
                    str(requested_name),
                )
            )
            continue
        analysis = matches[0]
        resolved[str(requested_name)] = analysis
        if pdelta_enabled(getattr(analysis, "pdelta_effect", None)):
            issues.append(
                SolverCapabilityIssue(
                    "PDELTA_UNSUPPORTED",
                    "P-Delta requires a subsystem that is not present in the Python port.",
                    str(requested_name),
                )
            )

        request = output_requests.get(str(requested_name)) if output_requests else None
        if request is not None:
            displacements = getattr(request, "displacements", None)
            if displacements is not None and bool(getattr(displacements, "enabled", False)):
                issues.append(
                    SolverCapabilityIssue(
                        "MODEL_POINT_OUTPUT_UNVERIFIED",
                        "Exact C# DisplModelPoints-compatible projection is not implemented.",
                        str(requested_name),
                    )
                )
            modal = getattr(request, "modal_contributions", None)
            if modal is not None and bool(getattr(modal, "enabled", False)):
                issues.append(
                    SolverCapabilityIssue(
                        "MODAL_OUTPUT_UNSUPPORTED",
                        "Modal contribution output is not implemented by the Python solver.",
                        str(requested_name),
                    )
                )

    _inspect_dependency_graph(analyses, resolved.values(), issues)
    return SolverCapabilityReport(supported=not issues, issues=tuple(issues))


def _inspect_dependency_graph(
    analyses: Mapping[int, Any],
    requested: Iterable[Any],
    issues: list[SolverCapabilityIssue],
) -> None:
    for target in requested:
        seen: set[int] = set()
        current = target
        while True:
            key = int(getattr(current, "key"))
            name = str(getattr(current, "name", key))
            if key in seen:
                issues.append(
                    SolverCapabilityIssue(
                        "ANALYSIS_DEPENDENCY_CYCLE",
                        f"Dependency cycle detected at analysis key {key}.",
                        name,
                    )
                )
                break
            seen.add(key)
            predecessor = int(getattr(current, "initial_analysis_key", -100))
            if predecessor < 0:
                break
            if predecessor not in analyses:
                issues.append(
                    SolverCapabilityIssue(
                        "MISSING_PREDECESSOR",
                        f"Required predecessor analysis key {predecessor} is absent.",
                        name,
                    )
                )
                break
            current = analyses[predecessor]
