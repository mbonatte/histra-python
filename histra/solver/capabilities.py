"""Preflight checks for running an HRX job with the Python solver."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from histra.preprocessing.constitutive_laws import validate_masonry_material_enums



_STATIC_INTEGRATORS = {"LoadControl", "ArcLength", "ArcLengthLinear"}
_STATIC_METHODS = {
    "StandardNewtonRaphson",
    "ModifiedNewtonRaphson",
    "StandardSecantLineSearch",
    "StandardRegulaFalsiLineSearch",
    "StandardBisectionLineSearch",
    "StandardInitialInterpolatedLineSearch",
    "ModifiedSecantLineSearch",
    "ModifiedRegulaFalsiLineSearch",
    "ModifiedBisectionLineSearch",
    "ModifiedInitialInterpolatedLineSearch",
}
_CONVERGENCE_CRITERIA = {"ForceMoment", "DispRotation", "Work"}
_PDELTA_EFFECTS = {"none", "eachstep", "eachiteration", "0", "1", "2"}


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

    reachable = _inspect_dependency_graph(analyses, resolved.values(), issues)
    for analysis in reachable:
        _inspect_analysis_definition(analysis, issues)
    _inspect_materials(collections, issues)
    return SolverCapabilityReport(supported=not issues, issues=tuple(issues))


def _inspect_materials(collections: Any, issues: list[SolverCapabilityIssue]) -> None:
    for key, material in getattr(collections, "materials", {}).items():
        try:
            validate_masonry_material_enums(material)
        except (TypeError, ValueError) as exc:
            issues.append(
                SolverCapabilityIssue(
                    "MASONRY_CONSTITUTIVE_ENUM_UNSUPPORTED",
                    f"Masonry material {key}: {exc}",
                )
            )


def _inspect_dependency_graph(
    analyses: Mapping[int, Any],
    requested: Iterable[Any],
    issues: list[SolverCapabilityIssue],
) -> tuple[Any, ...]:
    reachable: dict[int, Any] = {}
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
            reachable[key] = current
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
    return tuple(reachable.values())


def _inspect_analysis_definition(
    analysis: Any,
    issues: list[SolverCapabilityIssue],
) -> None:
    name = str(getattr(analysis, "name", getattr(analysis, "key", "<unknown>")))
    analysis_type = int(getattr(analysis, "analysis_type", 2))
    if analysis_type in {3, 4}:
        issues.append(
            SolverCapabilityIssue(
                "DYNAMIC_ANALYSIS_UNSUPPORTED",
                "Dynamic linear and nonlinear analyses are outside the V1 masonry core.",
                name,
            )
        )
        return
    if analysis_type not in {2, 5}:
        issues.append(
            SolverCapabilityIssue(
                "ANALYSIS_TYPE_UNSUPPORTED",
                f"AnalysisType={analysis_type} is not supported by the V1 solver.",
                name,
            )
        )
        return

    raw_pdelta = getattr(analysis, "pdelta_effect", "None")
    if isinstance(raw_pdelta, bool):
        pdelta = "1" if raw_pdelta else "0"
    elif raw_pdelta is None:
        pdelta = "none"
    else:
        pdelta = str(raw_pdelta).strip().casefold()
    if pdelta in {"", "false", "disabled", "no"}:
        pdelta = "none"
    if pdelta not in _PDELTA_EFFECTS:
        issues.append(
            SolverCapabilityIssue(
                "PDELTA_EFFECT_UNSUPPORTED",
                f"Unknown PdeltaEffect={raw_pdelta!r}; expected None, EachStep, or EachIteration.",
                name,
            )
        )

    if analysis_type == 5:
        if pdelta not in {"none", "0"}:
            issues.append(
                SolverCapabilityIssue(
                    "MODAL_PDELTA_UNSUPPORTED",
                    "Modal analysis cannot be combined with P-Delta in the V1 solver.",
                    name,
                )
            )
        return

    integration = str(getattr(analysis, "integration_method", "LoadControl"))
    if integration not in _STATIC_INTEGRATORS:
        issues.append(
            SolverCapabilityIssue(
                "STATIC_INTEGRATOR_UNSUPPORTED",
                f"Unknown IntegrationMethod={integration!r}; expected one of {sorted(_STATIC_INTEGRATORS)}.",
                name,
            )
        )
    method = str(getattr(analysis, "method", "StandardNewtonRaphson"))
    if method not in _STATIC_METHODS:
        issues.append(
            SolverCapabilityIssue(
                "NONLINEAR_METHOD_UNSUPPORTED",
                f"Unknown Method={method!r}; the C# factory does not provide this V1 path.",
                name,
            )
        )
    criterion = str(
        getattr(analysis, "adaptive_convergence_criteria", "ForceMoment")
    )
    if criterion not in _CONVERGENCE_CRITERIA:
        issues.append(
            SolverCapabilityIssue(
                "CONVERGENCE_CRITERION_UNSUPPORTED",
                f"Unknown convergence criterion {criterion!r}; expected ForceMoment, DispRotation, or Work.",
                name,
            )
        )


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
