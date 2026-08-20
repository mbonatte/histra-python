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
                _inspect_model_points(model, str(requested_name), issues)
            modal = getattr(request, "modal_contributions", None)
            if modal is not None and bool(getattr(modal, "enabled", False)):
                issues.append(
                    SolverCapabilityIssue(
                        "MODAL_CONTRIBUTION_OUTPUT_UNSUPPORTED",
                        "Response-spectrum modal contribution projection is not implemented; "
                        "modal eigenanalysis itself is supported.",
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


def _inspect_model_points(model: Any, analysis_name: str, issues: list[SolverCapabilityIssue]) -> None:
    collections = model.collections
    for point in collections.model_points.values():
        element_type = str(point.element_type).casefold().split(".")[-1]
        if element_type == "node":
            if int(point.element_key) not in collections.nodes:
                issues.append(SolverCapabilityIssue(
                    "MODEL_POINT_ELEMENT_MISSING",
                    f"ModelPoint {point.key} references missing Node {point.element_key}.",
                    analysis_name,
                ))
        elif element_type == "quad":
            quad = collections.quads.get(int(point.element_key))
            if quad is None:
                issues.append(SolverCapabilityIssue(
                    "MODEL_POINT_ELEMENT_MISSING",
                    f"ModelPoint {point.key} references missing Quad {point.element_key}.",
                    analysis_name,
                ))
            elif not 0 <= int(point.id_vertex) <= len(quad.node_keys):
                issues.append(SolverCapabilityIssue(
                    "MODEL_POINT_VERTEX_UNSUPPORTED",
                    f"ModelPoint {point.key} has IdVertex={point.id_vertex}.",
                    analysis_name,
                ))
        else:
            issues.append(SolverCapabilityIssue(
                "MODEL_POINT_TYPE_UNSUPPORTED",
                f"ModelPoint {point.key} uses unsupported element type {point.element_type!r}.",
                analysis_name,
            ))
