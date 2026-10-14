"""Active Mass Fraction for masonry arch bridge collapse analysis.

This module implements the active mass fraction metric representing the proportion
of structural mass exhibiting significant displacement in a nonlinear push-down analysis:

    M_active = Σ(m_i for active points in G) / Σ(m_i for all points in G)

A mass point i in group G is classified as active when its displacement magnitude a_i
satisfies both relative and absolute threshold criteria:

    a_i >= max(relative_threshold * a_ref, absolute_threshold)

where:
    - relative_threshold: Configurable ratio (default 0.10 = 10% of peak displacement).
    - absolute_threshold: Configurable minimum displacement (default 1.0e-4 cm = 1.0 um)
      below which all motion is deemed numerical roundoff / solver precision noise.
    - a_ref: Reference peak displacement (either group peak max_{i in G}(a_i) or
      model-wide peak max(a_i)).

Key Engineering Interpretation Rules:
    - The 10% threshold is an initial screening parameter, not a universal failure criterion.
      Configurable thresholds and multi-threshold sensitivity curves are supported.
    - If peak displacement is below absolute_threshold, the group status is "NO_MOTION"
      with active mass = 0.0, preventing numerical chatter from being misclassified as motion.
    - Separate calculations are performed for:
        1. Entire masonry structure (excluding backfill)
        2. Arch barrel (overall and broken down per span for multi-arch bridges)
        3. Piers (or status "NOT_PRESENT" if no piers exist)
        4. Backfill (overall and broken down per span)
        5. Other available structural regions (e.g. spandrel walls, abutments)
    - Both incremental displacements (Δu) and cumulative displacements (u) are evaluated
      and clearly distinguished.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any, Mapping, Sequence

import numpy as np

from histra.collapse.participation import (
    BridgeClassification,
    classify_bridge_components,
    sample_quad_displacements_and_masses,
)
from histra.model.model import Model
from histra.solver.outcomes import AnalysisExecution, AnalysisStep


@dataclass(frozen=True)
class ActiveMassCriteria:
    """Configurable thresholds for classifying mass points as active."""

    relative_threshold: float = 0.10
    """Fraction of peak displacement required for activity (default 0.10 = 10%)."""

    absolute_threshold: float = 1.0e-4
    """Minimum physical displacement in model length units (cm) to reject numerical noise.
    1.0e-4 cm = 1.0 um, well above Newton-Raphson linear solve precision."""

    reference_scope: str = "group"
    """'group' evaluates relative threshold against group peak; 'global' against model peak."""

    direction: str = "all"
    """Directional filter: 'all' (magnitude), 'x', 'y', or 'z'."""

    motion_tolerance: float = 1.0e-9
    """Absolute zero-motion cutoff (cm)."""


@dataclass(frozen=True)
class ActiveMassIndex:
    """Active mass fraction for a component group."""

    fraction: float
    """M_active in [0.0, 1.0]: fraction of total group mass that is active."""

    active_mass: float
    """Sum of mass weights for active sampling points."""

    total_mass: float
    """Sum of mass weights for all sampling points in the group."""

    status: str
    """Status: 'VALID', 'NO_MOTION', 'NO_MASS', or 'NOT_PRESENT'."""

    threshold_used: float
    """Numerical displacement threshold (cm) applied to determine activity."""

    relative_threshold: float
    """Configured relative fraction (e.g. 0.10)."""

    absolute_threshold: float
    """Configured absolute minimum displacement floor (cm)."""

    active_points_count: int
    """Number of active sampling points."""

    total_points_count: int
    """Total sampling points in the group."""

    max_disp: float
    """Peak displacement magnitude in the group (cm)."""

    mean_disp: float
    """Mean displacement magnitude of the group (cm)."""

    direction: str = "all"
    """Direction: 'all', 'x', 'y', 'z'."""

    @property
    def is_valid(self) -> bool:
        return self.status == "VALID"

    @property
    def has_motion(self) -> bool:
        return self.status not in {"NO_MOTION", "NO_MASS", "NOT_PRESENT"}

    @property
    def fraction_percentage(self) -> float:
        """Active mass fraction as a percentage (0.0 to 100.0%)."""
        return float(self.fraction * 100.0)

    @property
    def mobility_extent(self) -> str:
        """Qualitative description of active mass mobilization."""
        if not self.is_valid:
            return self.status
        f = self.fraction
        if f >= 0.50:
            return "GLOBAL"
        if f >= 0.20:
            return "PARTIAL"
        return "LOCALIZED"

    def to_dict(self) -> dict[str, Any]:
        return {
            "fraction": self.fraction,
            "fraction_percentage": self.fraction_percentage,
            "active_mass": self.active_mass,
            "total_mass": self.total_mass,
            "status": self.status,
            "threshold_used": self.threshold_used,
            "relative_threshold": self.relative_threshold,
            "absolute_threshold": self.absolute_threshold,
            "active_points_count": self.active_points_count,
            "total_points_count": self.total_points_count,
            "max_disp": self.max_disp,
            "mean_disp": self.mean_disp,
            "direction": self.direction,
            "mobility_extent": self.mobility_extent,
        }


@dataclass(frozen=True)
class RegionalActiveMassSummary:
    """Active mass fraction evaluation across all structural regions and spans."""

    entire_structure: ActiveMassIndex
    arch_barrel: ActiveMassIndex
    piers: ActiveMassIndex
    backfill: ActiveMassIndex
    other_regions: ActiveMassIndex
    global_model: ActiveMassIndex
    arch_spans: dict[str, ActiveMassIndex] = field(default_factory=dict)
    backfill_spans: dict[str, ActiveMassIndex] = field(default_factory=dict)
    directional_x: ActiveMassIndex | None = None
    directional_y: ActiveMassIndex | None = None
    directional_z: ActiveMassIndex | None = None
    sensitivity_profile: dict[str, dict[float, float]] = field(default_factory=dict)
    backfill_to_structure_active_ratio: float = 0.0
    backfill_to_arch_active_ratio: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "entire_structure": self.entire_structure.to_dict(),
            "arch_barrel": self.arch_barrel.to_dict(),
            "piers": self.piers.to_dict(),
            "backfill": self.backfill.to_dict(),
            "other_regions": self.other_regions.to_dict(),
            "global_model": self.global_model.to_dict(),
            "arch_spans": {k: v.to_dict() for k, v in self.arch_spans.items()},
            "backfill_spans": {k: v.to_dict() for k, v in self.backfill_spans.items()},
            "directional_x": self.directional_x.to_dict() if self.directional_x else None,
            "directional_y": self.directional_y.to_dict() if self.directional_y else None,
            "directional_z": self.directional_z.to_dict() if self.directional_z else None,
            "sensitivity_profile": self.sensitivity_profile,
            "backfill_to_structure_active_ratio": self.backfill_to_structure_active_ratio,
            "backfill_to_arch_active_ratio": self.backfill_to_arch_active_ratio,
        }


@dataclass(frozen=True)
class StepActiveMassReport:
    """Active mass fraction evaluation for one committed analysis step."""

    step: int
    load_factor: float
    monitored_displacement: float
    incremental: RegionalActiveMassSummary
    cumulative: RegionalActiveMassSummary
    criteria: ActiveMassCriteria
    interpretation_notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "step": self.step,
            "load_factor": self.load_factor,
            "monitored_displacement": self.monitored_displacement,
            "incremental": self.incremental.to_dict(),
            "cumulative": self.cumulative.to_dict(),
            "criteria": {
                "relative_threshold": self.criteria.relative_threshold,
                "absolute_threshold": self.criteria.absolute_threshold,
                "reference_scope": self.criteria.reference_scope,
                "direction": self.criteria.direction,
            },
            "interpretation_notes": list(self.interpretation_notes),
        }


@dataclass(frozen=True)
class ExecutionActiveMassReport:
    """Active mass fraction history across all committed steps of an analysis."""

    analysis_key: int
    analysis_name: str
    steps: tuple[StepActiveMassReport, ...]
    criteria: ActiveMassCriteria
    summary: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "analysis_key": self.analysis_key,
            "analysis_name": self.analysis_name,
            "steps": [s.to_dict() for s in self.steps],
            "criteria": {
                "relative_threshold": self.criteria.relative_threshold,
                "absolute_threshold": self.criteria.absolute_threshold,
                "reference_scope": self.criteria.reference_scope,
            },
            "summary": self.summary,
        }


# =============================================================================
# Core Active Mass Calculations
# =============================================================================

def compute_active_mass_fraction(
    masses: np.ndarray,
    displacements: np.ndarray,
    *,
    criteria: ActiveMassCriteria | None = None,
    ref_max_disp: float | None = None,
) -> ActiveMassIndex:
    """Calculate the active mass fraction for a group of mass points.

    M_active = Σ(m_i for active points) / Σ(m_i for all points)

    Parameters
    ----------
    masses : np.ndarray
        1D array of positive mass weights.
    displacements : np.ndarray
        Array of point displacements (1D scalars or (N, 3) 3D vectors).
    criteria : ActiveMassCriteria, optional
        Configurable relative and absolute threshold settings.
    ref_max_disp : float, optional
        External reference peak displacement when reference_scope == 'global'.
    """
    if criteria is None:
        criteria = ActiveMassCriteria()

    m = np.asarray(masses, dtype=np.float64).ravel()
    d = np.asarray(displacements, dtype=np.float64)

    direction = criteria.direction
    if d.ndim == 2 and d.shape[1] == 3:
        if direction == "x":
            a = np.abs(d[:, 0])
        elif direction == "y":
            a = np.abs(d[:, 1])
        elif direction == "z":
            a = np.abs(d[:, 2])
        else:
            a = np.sqrt(d[:, 0] ** 2 + d[:, 1] ** 2 + d[:, 2] ** 2)
    elif d.ndim == 1:
        a = np.abs(d)
    else:
        raise ValueError(f"Expected 1D or (N, 3) displacements array, got shape {d.shape}")

    if a.size != m.size:
        raise ValueError(f"Size mismatch: {m.size} masses vs {a.size} displacements")

    total_mass = float(np.sum(m))
    if m.size == 0 or total_mass <= 0.0:
        return ActiveMassIndex(
            fraction=0.0,
            active_mass=0.0,
            total_mass=0.0,
            status="NO_MASS",
            threshold_used=criteria.absolute_threshold,
            relative_threshold=criteria.relative_threshold,
            absolute_threshold=criteria.absolute_threshold,
            active_points_count=0,
            total_points_count=0,
            max_disp=0.0,
            mean_disp=0.0,
            direction=direction,
        )

    max_disp = float(np.max(a)) if a.size > 0 else 0.0
    mean_disp = float(np.sum(m * a) / total_mass)

    # Reference displacement for relative scaling
    if criteria.reference_scope == "global" and ref_max_disp is not None:
        base_disp = max(ref_max_disp, max_disp)
    else:
        base_disp = max_disp

    # Noise rejection: if maximum displacement does not exceed the absolute threshold
    if base_disp < criteria.absolute_threshold or max_disp < criteria.motion_tolerance:
        return ActiveMassIndex(
            fraction=0.0,
            active_mass=0.0,
            total_mass=total_mass,
            status="NO_MOTION",
            threshold_used=criteria.absolute_threshold,
            relative_threshold=criteria.relative_threshold,
            absolute_threshold=criteria.absolute_threshold,
            active_points_count=0,
            total_points_count=int(m.size),
            max_disp=max_disp,
            mean_disp=mean_disp,
            direction=direction,
        )

    # Dual threshold: max(relative * peak, absolute noise floor)
    cutoff = max(criteria.relative_threshold * base_disp, criteria.absolute_threshold)

    active_mask = (a >= cutoff) & (a >= criteria.absolute_threshold)
    active_mass = float(np.sum(m[active_mask]))
    active_count = int(np.count_nonzero(active_mask))

    fraction = min(1.0, max(0.0, active_mass / total_mass))

    return ActiveMassIndex(
        fraction=fraction,
        active_mass=active_mass,
        total_mass=total_mass,
        status="VALID",
        threshold_used=float(cutoff),
        relative_threshold=float(criteria.relative_threshold),
        absolute_threshold=float(criteria.absolute_threshold),
        active_points_count=active_count,
        total_points_count=int(m.size),
        max_disp=max_disp,
        mean_disp=mean_disp,
        direction=direction,
    )


def compute_active_mass_sensitivity(
    masses: np.ndarray,
    displacements: np.ndarray,
    *,
    thresholds: Sequence[float] = (0.01, 0.02, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50, 0.75),
    absolute_threshold: float = 1.0e-4,
    direction: str = "all",
) -> dict[float, float]:
    """Calculate active mass fraction across a range of relative thresholds for sensitivity study.

    A plateau (constant M_active across thresholds) indicates a uniform rigid-body or global mechanism.
    A steep drop indicates highly localized, non-uniform deformation.
    """
    profile: dict[float, float] = {}
    for th in thresholds:
        crit = ActiveMassCriteria(
            relative_threshold=float(th),
            absolute_threshold=float(absolute_threshold),
            direction=direction,
        )
        res = compute_active_mass_fraction(masses, displacements, criteria=crit)
        profile[round(float(th), 4)] = round(res.fraction, 6)
    return profile


# =============================================================================
# Regional and Step Active Mass Evaluators
# =============================================================================

def evaluate_regional_active_mass(
    model: Model,
    displacement_vector: np.ndarray,
    classification: BridgeClassification,
    *,
    criteria: ActiveMassCriteria | None = None,
    kinematic_mode: str = "volume_8point",
) -> RegionalActiveMassSummary:
    """Evaluate active mass fractions across structural components and spans."""
    if criteria is None:
        criteria = ActiveMassCriteria()

    assert model.collections is not None

    quad_points: dict[int, np.ndarray] = {}
    quad_masses: dict[int, np.ndarray] = {}

    for quad_key, quad in model.collections.quads.items():
        disps, masses = sample_quad_displacements_and_masses(
            quad, model, displacement_vector, kinematic_mode=kinematic_mode
        )
        quad_points[quad_key] = disps
        quad_masses[quad_key] = masses

    def gather(keys: Sequence[int]) -> tuple[np.ndarray, np.ndarray]:
        if not keys:
            return np.zeros((0, 3), dtype=np.float64), np.zeros(0, dtype=np.float64)
        selected_disps = [quad_points[k] for k in keys if k in quad_points]
        selected_masses = [quad_masses[k] for k in keys if k in quad_masses]
        if not selected_disps:
            return np.zeros((0, 3), dtype=np.float64), np.zeros(0, dtype=np.float64)
        return np.vstack(selected_disps), np.concatenate(selected_masses)

    d_struct, m_struct = gather(classification.total_structure_quad_keys)
    d_backfill, m_backfill = gather(classification.backfill_quad_keys)
    d_arch, m_arch = gather(classification.arch_quad_keys)
    d_piers, m_piers = gather(classification.pier_quad_keys)
    d_other, m_other = gather(classification.other_quad_keys)
    d_global, m_global = gather(classification.all_quad_keys)

    global_max = float(np.max(np.linalg.norm(d_global, axis=1))) if d_global.size > 0 else 0.0

    # Calculate component active mass
    act_struct = compute_active_mass_fraction(
        m_struct, d_struct, criteria=criteria, ref_max_disp=global_max
    )
    act_backfill = compute_active_mass_fraction(
        m_backfill, d_backfill, criteria=criteria, ref_max_disp=global_max
    )
    act_arch = compute_active_mass_fraction(
        m_arch, d_arch, criteria=criteria, ref_max_disp=global_max
    )
    act_piers = (
        compute_active_mass_fraction(
            m_piers, d_piers, criteria=criteria, ref_max_disp=global_max
        )
        if classification.has_piers
        else ActiveMassIndex(
            fraction=0.0,
            active_mass=0.0,
            total_mass=0.0,
            status="NOT_PRESENT",
            threshold_used=criteria.absolute_threshold,
            relative_threshold=criteria.relative_threshold,
            absolute_threshold=criteria.absolute_threshold,
            active_points_count=0,
            total_points_count=0,
            max_disp=0.0,
            mean_disp=0.0,
        )
    )
    act_other = compute_active_mass_fraction(
        m_other, d_other, criteria=criteria, ref_max_disp=global_max
    )
    act_global = compute_active_mass_fraction(
        m_global, d_global, criteria=criteria, ref_max_disp=global_max
    )

    # Multi-span breakdown for arch barrels and backfill
    arch_spans_act: dict[str, ActiveMassIndex] = {}
    for span_name, span_keys in classification.arch_spans.items():
        d_span, m_span = gather(span_keys)
        arch_spans_act[span_name] = compute_active_mass_fraction(
            m_span, d_span, criteria=criteria, ref_max_disp=global_max
        )

    backfill_spans_act: dict[str, ActiveMassIndex] = {}
    for span_name, span_keys in classification.backfill_spans.items():
        d_span, m_span = gather(span_keys)
        backfill_spans_act[span_name] = compute_active_mass_fraction(
            m_span, d_span, criteria=criteria, ref_max_disp=global_max
        )

    # Directional active mass for structure
    crit_x = ActiveMassCriteria(
        relative_threshold=criteria.relative_threshold,
        absolute_threshold=criteria.absolute_threshold,
        direction="x",
    )
    crit_y = ActiveMassCriteria(
        relative_threshold=criteria.relative_threshold,
        absolute_threshold=criteria.absolute_threshold,
        direction="y",
    )
    crit_z = ActiveMassCriteria(
        relative_threshold=criteria.relative_threshold,
        absolute_threshold=criteria.absolute_threshold,
        direction="z",
    )
    dir_x = compute_active_mass_fraction(m_struct, d_struct, criteria=crit_x)
    dir_y = compute_active_mass_fraction(m_struct, d_struct, criteria=crit_y)
    dir_z = compute_active_mass_fraction(m_struct, d_struct, criteria=crit_z)

    # Sensitivity profiles across thresholds (0.02, 0.05, 0.10, 0.20, 0.30, 0.50)
    sensitivity = {
        "entire_structure": compute_active_mass_sensitivity(
            m_struct, d_struct, absolute_threshold=criteria.absolute_threshold
        ),
        "backfill": compute_active_mass_sensitivity(
            m_backfill, d_backfill, absolute_threshold=criteria.absolute_threshold
        ),
        "arch_barrel": compute_active_mass_sensitivity(
            m_arch, d_arch, absolute_threshold=criteria.absolute_threshold
        ),
    }
    if classification.has_piers:
        sensitivity["piers"] = compute_active_mass_sensitivity(
            m_piers, d_piers, absolute_threshold=criteria.absolute_threshold
        )

    # Ratios
    b_to_s_active = float(act_backfill.fraction / max(act_struct.fraction, 1.0e-30))
    b_to_a_active = float(act_backfill.fraction / max(act_arch.fraction, 1.0e-30))

    return RegionalActiveMassSummary(
        entire_structure=act_struct,
        arch_barrel=act_arch,
        piers=act_piers,
        backfill=act_backfill,
        other_regions=act_other,
        global_model=act_global,
        arch_spans=arch_spans_act,
        backfill_spans=backfill_spans_act,
        directional_x=dir_x,
        directional_y=dir_y,
        directional_z=dir_z,
        sensitivity_profile=sensitivity,
        backfill_to_structure_active_ratio=b_to_s_active,
        backfill_to_arch_active_ratio=b_to_a_active,
    )


def evaluate_step_active_mass(
    model: Model,
    current_step: AnalysisStep | Mapping[str, Any] | np.ndarray,
    previous_step: AnalysisStep | Mapping[str, Any] | np.ndarray | None = None,
    initial_step: AnalysisStep | Mapping[str, Any] | np.ndarray | None = None,
    *,
    classification: BridgeClassification | None = None,
    criteria: ActiveMassCriteria | None = None,
    kinematic_mode: str = "volume_8point",
) -> StepActiveMassReport:
    """Evaluate active mass fractions for one committed analysis step."""
    if classification is None:
        classification = classify_bridge_components(model)
    if criteria is None:
        criteria = ActiveMassCriteria()

    def extract_u(item: Any) -> np.ndarray:
        if isinstance(item, np.ndarray):
            return np.asarray(item, dtype=np.float64)
        if isinstance(item, Mapping) and "u" in item:
            return np.asarray(item["u"], dtype=np.float64)
        if hasattr(item, "u"):
            return np.asarray(item.u, dtype=np.float64)
        return np.asarray(item, dtype=np.float64)

    u_curr = extract_u(current_step)
    u_prev = extract_u(previous_step) if previous_step is not None else np.zeros_like(u_curr)
    u_init = extract_u(initial_step) if initial_step is not None else np.zeros_like(u_curr)

    delta_u = u_curr - u_prev
    cumul_u = u_curr - u_init

    incremental_summary = evaluate_regional_active_mass(
        model, delta_u, classification, criteria=criteria, kinematic_mode=kinematic_mode
    )
    cumulative_summary = evaluate_regional_active_mass(
        model, cumul_u, classification, criteria=criteria, kinematic_mode=kinematic_mode
    )

    notes: list[str] = []
    step_num = int(current_step.get("step", 0)) if isinstance(current_step, Mapping) else int(getattr(current_step, "step", 0))
    lf = float(current_step.get("load_factor", 0.0)) if isinstance(current_step, Mapping) else float(getattr(current_step, "load_factor", 0.0))
    mon_disp = float(current_step.get("displacement", 0.0)) if isinstance(current_step, Mapping) else float(getattr(current_step, "displacement", 0.0))

    act_struct = incremental_summary.entire_structure
    act_back = incremental_summary.backfill

    # Structural mobility notes
    if act_struct.is_valid:
        if act_struct.fraction >= 0.50:
            notes.append(
                f"Step {step_num}: Broad active structural mass ({act_struct.fraction_percentage:.1f}% "
                f"active above {act_struct.threshold_used:.3e} cm cutoff)."
            )
        elif act_struct.fraction < 0.20:
            notes.append(
                f"Step {step_num}: Concentrated active mass ({act_struct.fraction_percentage:.1f}% "
                f"active in structure)."
            )

    # Backfill localization vs structural motion
    if act_back.is_valid:
        if not act_struct.has_motion:
            notes.append(
                f"Step {step_num}: Localized backfill movement with quiescent structural components "
                f"({act_back.fraction_percentage:.1f}% backfill active, structure has no motion)."
            )
        elif incremental_summary.backfill_to_structure_active_ratio > 2.0:
            notes.append(
                f"Step {step_num}: Backfill activity significantly exceeds structural activity "
                f"(backfill {act_back.fraction_percentage:.1f}% active vs structure {act_struct.fraction_percentage:.1f}% active; "
                f"ratio={incremental_summary.backfill_to_structure_active_ratio:.2f})."
            )

    # Multi-span localization note
    if len(incremental_summary.arch_spans) > 1:
        span_fractions = {k: v.fraction for k, v in incremental_summary.arch_spans.items() if v.is_valid}
        if span_fractions:
            max_span = max(span_fractions, key=span_fractions.get)
            min_span = min(span_fractions, key=span_fractions.get)
            if span_fractions[max_span] > 0.30 and span_fractions[min_span] < 0.05:
                notes.append(
                    f"Step {step_num}: Active arch motion is localized to {max_span} "
                    f"({span_fractions[max_span]*100:.1f}%) while {min_span} remains quiescent "
                    f"({span_fractions[min_span]*100:.1f}%)."
                )

    return StepActiveMassReport(
        step=step_num,
        load_factor=lf,
        monitored_displacement=mon_disp,
        incremental=incremental_summary,
        cumulative=cumulative_summary,
        criteria=criteria,
        interpretation_notes=tuple(notes),
    )


def evaluate_execution_active_mass(
    model: Model,
    execution: AnalysisExecution,
    *,
    classification: BridgeClassification | None = None,
    criteria: ActiveMassCriteria | None = None,
    kinematic_mode: str = "volume_8point",
) -> ExecutionActiveMassReport:
    """Evaluate active mass fraction history across all committed steps of an analysis."""
    if classification is None:
        classification = classify_bridge_components(model)
    if criteria is None:
        criteria = ActiveMassCriteria()

    committed = execution.committed_steps
    if not committed:
        return ExecutionActiveMassReport(
            analysis_key=execution.analysis_key,
            analysis_name=execution.analysis_name,
            steps=(),
            criteria=criteria,
            summary={"committed_steps": 0, "status": "NO_COMMITTED_STEPS"},
        )

    initial_step = execution.initial_step
    step_reports: list[StepActiveMassReport] = []

    prev_step = initial_step
    for step in committed:
        rep = evaluate_step_active_mass(
            model,
            step,
            previous_step=prev_step,
            initial_step=initial_step,
            classification=classification,
            criteria=criteria,
            kinematic_mode=kinematic_mode,
        )
        step_reports.append(rep)
        prev_step = step

    terminal = step_reports[-1]
    peak_active_struct = max((s.incremental.entire_structure.fraction for s in step_reports), default=0.0)
    terminal_active_struct = terminal.incremental.entire_structure.fraction
    terminal_active_back = terminal.incremental.backfill.fraction

    summary = {
        "analysis_key": execution.analysis_key,
        "analysis_name": execution.analysis_name,
        "outcome": str(execution.outcome.value if execution.outcome else "unknown"),
        "committed_step_count": len(step_reports),
        "peak_active_structure_incremental": peak_active_struct,
        "terminal_active_structure_incremental": terminal_active_struct,
        "terminal_active_backfill_incremental": terminal_active_back,
        "terminal_active_structure_cumulative": terminal.cumulative.entire_structure.fraction,
        "terminal_active_backfill_cumulative": terminal.cumulative.backfill.fraction,
        "terminal_backfill_to_structure_ratio": terminal.incremental.backfill_to_structure_active_ratio,
        "multi_span_count": len(classification.arch_spans),
    }

    return ExecutionActiveMassReport(
        analysis_key=execution.analysis_key,
        analysis_name=execution.analysis_name,
        steps=tuple(step_reports),
        criteria=criteria,
        summary=summary,
    )
