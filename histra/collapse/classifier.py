"""Automatic Local vs Global Collapse Mechanism Classifier for HiStrA.

This module implements Feature 4: a transparent, rule-based classification system
for nonlinear static push-down analyses of masonry arch bridges.

Categories:
    - LOCAL_BACKFILL_FAILURE:
        Localized backfill deformation/punch-through near the load application,
        with limited or no arch/pier collapse mechanism.
    - LOCAL_MASONRY_FAILURE:
        Localized masonry damage or displacement without sufficient evidence
        of a wider collapse mechanism.
    - SINGLE_SPAN_MECHANISM:
        A complete structural mechanism (3- to 4-hinges) in a single arch span,
        while adjacent spans remain quiescent.
    - GLOBAL_BRIDGE_MECHANISM:
        A structural mechanism involving multiple spans, pier overturning/shear,
        or a substantial connected portion of the bridge.
    - MIXED_OR_PROGRESSIVE_FAILURE:
        Substantial interaction between local backfill failure and structural
        arch hinge formation, or local failure evolving into wider collapse.
    - NUMERICAL_OR_UNCERTAIN:
        Loss of convergence, solver divergence, or contradictory indicators
        preventing reliable physical classification.
    - NO_SIGNIFICANT_FAILURE_EVENT:
        No detected load-drop or collapse event meeting screening criteria.

Critical Engineering Rules:
    - Do not classify failure based on K alone.
    - Do not classify a bridge as globally collapsed simply because displacement is large.
    - Distinguish rigid-body movement (e.g. foundation settlement) from internal arch hinges.
    - A complete mechanism in one span is classified as SINGLE_SPAN_MECHANISM, not whole-bridge collapse.
    - All thresholds are documented and configurable.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import math
from typing import Any, Mapping, Sequence

import numpy as np

from histra.collapse.active_mass import (
    ActiveMassCriteria,
    ActiveMassIndex,
    RegionalActiveMassSummary,
    evaluate_regional_active_mass,
)
from histra.collapse.interface_damage import (
    DamageParticipationSummary,
    InterfaceClassification,
    InterfaceCriteria,
    classify_bridge_interfaces,
    evaluate_damage_participation,
)
from histra.collapse.participation import (
    BridgeClassification,
    KinematicParticipationIndex,
    RegionalParticipationSummary,
    classify_bridge_components,
    evaluate_regional_participation,
)
from histra.model.model import Model
from histra.solver.model_manager import ModelManager
from histra.solver.outcomes import AnalysisExecution, AnalysisOutcome, AnalysisStep


class CollapseCategory(str, Enum):
    """Exhaustive collapse mechanism classification categories."""

    LOCAL_BACKFILL_FAILURE = "LOCAL_BACKFILL_FAILURE"
    LOCAL_MASONRY_FAILURE = "LOCAL_MASONRY_FAILURE"
    SINGLE_SPAN_MECHANISM = "SINGLE_SPAN_MECHANISM"
    GLOBAL_BRIDGE_MECHANISM = "GLOBAL_BRIDGE_MECHANISM"
    MIXED_OR_PROGRESSIVE_FAILURE = "MIXED_OR_PROGRESSIVE_FAILURE"
    NUMERICAL_OR_UNCERTAIN = "NUMERICAL_OR_UNCERTAIN"
    NO_SIGNIFICANT_FAILURE_EVENT = "NO_SIGNIFICANT_FAILURE_EVENT"


class ReviewPriority(str, Enum):
    """Engineer review priority for batch simulation triage."""

    LOW = "LOW"
    """High-confidence, unambiguous physical mechanism."""

    MEDIUM = "MEDIUM"
    """Recognized mechanism with minor secondary ambiguities."""

    HIGH = "HIGH"
    """Numerical divergence, contradictory evidence, or borderline screening."""


@dataclass(frozen=True)
class ClassifierThresholds:
    """Configurable, documented engineering thresholds for collapse classification."""

    load_drop_trigger: float = 0.05
    """Minimum fractional load drop from peak (5%) to flag a capacity-loss event."""

    significant_load_drop: float = 0.15
    """Fractional load drop (15%) signifying major physical collapse."""

    arch_hinge_mechanism_count: int = 3
    """Minimum arch hinges required for a complete flexural collapse mechanism."""

    arch_hinge_opening_tolerance: float = 0.02
    """Crack opening threshold (cm = 0.2 mm) for flexural hinge candidacy."""

    arch_hinge_rotation_tolerance: float = 1.0e-3
    """Relative rotation threshold (rad = 1 mrad) across hinge joint."""

    backfill_sliding_fraction_threshold: float = 0.20
    """Fraction of backfill interface area sliding to indicate backfill mobilization."""

    backfill_disp_dominance_ratio: float = 3.0
    """Ratio of backfill peak displacement to structural peak displacement."""

    backfill_dissipation_dominance_ratio: float = 0.60
    """Fraction of irreversible dissipation in backfill to declare backfill dominance."""

    masonry_active_mass_low: float = 0.15
    """Upper bound on active masonry mass for purely localized failure."""

    masonry_active_mass_high: float = 0.35
    """Lower bound on active masonry mass for widespread structural mobilization."""

    single_span_dominance_ratio: float = 0.70
    """Fraction of arch hinges/active mass concentrated in one span for single-span mechanism."""

    rigid_body_strain_cutoff: float = 1.0e-4
    """Internal shear strain below which motion is classified as rigid body."""


@dataclass(frozen=True)
class EvidenceBundle:
    """Structured collection of numerical indicators supporting the classification decision."""

    step_number: int
    load_peak: float
    load_current: float
    load_drop_ratio: float
    monitored_displacement: float
    k_total_structure: float
    k_backfill: float
    k_arch: float
    k_piers: float
    active_mass_structure: float
    active_mass_backfill: float
    active_mass_arch: float
    active_mass_piers: float
    active_mass_per_span: dict[str, float]
    arch_hinge_count: int
    arch_hinges_per_span: dict[str, int]
    max_arch_opening: float
    max_arch_rotation: float
    backfill_sliding_area_fraction: float
    backfill_to_structure_disp_ratio: float
    d_backfill: float
    d_masonry: float
    d_arch: float
    d_piers: float
    d_contacts: float
    total_dissipated_energy: float
    energy_status: str
    is_predominantly_rigid: bool
    solver_status: str
    solver_outcome: str
    iterations: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_number": self.step_number,
            "load_peak": self.load_peak,
            "load_current": self.load_current,
            "load_drop_ratio": self.load_drop_ratio,
            "monitored_displacement": self.monitored_displacement,
            "kinematic_participation": {
                "k_total_structure": self.k_total_structure,
                "k_backfill": self.k_backfill,
                "k_arch": self.k_arch,
                "k_piers": self.k_piers,
            },
            "active_mass_fraction": {
                "structure": self.active_mass_structure,
                "backfill": self.active_mass_backfill,
                "arch": self.active_mass_arch,
                "piers": self.active_mass_piers,
                "per_span": self.active_mass_per_span,
            },
            "hinges": {
                "total_arch_hinges": self.arch_hinge_count,
                "per_span": self.arch_hinges_per_span,
                "max_opening": self.max_arch_opening,
                "max_rotation": self.max_arch_rotation,
            },
            "backfill_indicators": {
                "sliding_area_fraction": self.backfill_sliding_area_fraction,
                "backfill_to_structure_disp_ratio": self.backfill_to_structure_disp_ratio,
            },
            "energy_dissipation_ratios": {
                "d_backfill": self.d_backfill,
                "d_masonry": self.d_masonry,
                "d_arch": self.d_arch,
                "d_piers": self.d_piers,
                "d_contacts": self.d_contacts,
                "total_dissipated_energy": self.total_dissipated_energy,
                "status": self.energy_status,
            },
            "is_predominantly_rigid": self.is_predominantly_rigid,
            "solver": {
                "status": self.solver_status,
                "outcome": self.solver_outcome,
                "iterations": self.iterations,
            },
        }


@dataclass(frozen=True)
class ClassificationResult:
    """Diagnostic outcome of the collapse mechanism classification."""

    category: CollapseCategory
    confidence_score: float
    """Heuristic agreement score in [0.0, 1.0], representing multi-indicator concordance."""

    review_priority: ReviewPriority
    primary_mechanism_description: str
    rationale: tuple[str, ...]
    evidence: EvidenceBundle
    critical_step: int

    @property
    def is_global(self) -> bool:
        return self.category in (
            CollapseCategory.GLOBAL_BRIDGE_MECHANISM,
            CollapseCategory.SINGLE_SPAN_MECHANISM,
        )

    @property
    def is_local_backfill(self) -> bool:
        return self.category == CollapseCategory.LOCAL_BACKFILL_FAILURE

    @property
    def is_uncertain(self) -> bool:
        return self.category == CollapseCategory.NUMERICAL_OR_UNCERTAIN

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category.value,
            "confidence_score": self.confidence_score,
            "review_priority": self.review_priority.value,
            "primary_mechanism_description": self.primary_mechanism_description,
            "rationale": list(self.rationale),
            "critical_step": self.critical_step,
            "is_global": self.is_global,
            "is_local_backfill": self.is_local_backfill,
            "is_uncertain": self.is_uncertain,
            "evidence": self.evidence.to_dict(),
        }


# =============================================================================
# Rule-Based Decision Engine
# =============================================================================

def classify_collapse_mechanism(
    model: Model,
    *,
    displacement_vector: np.ndarray,
    step_number: int = 1,
    load_current: float = 1.0,
    load_peak: float = 1.0,
    monitored_displacement: float = 0.0,
    solver_status: str = "OK",
    solver_outcome: str = "completed",
    iterations: int = 1,
    classification: BridgeClassification | None = None,
    intf_classification: InterfaceClassification | None = None,
    thresholds: ClassifierThresholds | None = None,
    runtime: Any | None = None,
) -> ClassificationResult:
    """Evaluate all evidence and classify the collapse mechanism at a given state."""
    if thresholds is None:
        thresholds = ClassifierThresholds()
    if classification is None:
        classification = classify_bridge_components(model)
    if intf_classification is None:
        intf_classification = classify_bridge_interfaces(model, classification)
    if runtime is None:
        runtime = ModelManager.hysteretic_batch_for(model)

    # 1. Evaluate Features 1, 2, and 3
    part_summary = evaluate_regional_participation(model, displacement_vector, classification)
    act_criteria = ActiveMassCriteria(relative_threshold=0.10, absolute_threshold=1.0e-4)
    act_summary = evaluate_regional_active_mass(
        model, displacement_vector, classification, criteria=act_criteria
    )
    intf_criteria = InterfaceCriteria(
        hinge_opening_tolerance=thresholds.arch_hinge_opening_tolerance,
        hinge_rotation_tolerance=thresholds.arch_hinge_rotation_tolerance,
    )
    dam_summary = evaluate_damage_participation(
        model,
        displacement_vector,
        classification=classification,
        intf_classification=intf_classification,
        runtime=runtime,
        criteria=intf_criteria,
    )

    # Load-drop metrics
    load_drop = max(0.0, load_peak - load_current)
    drop_ratio = (load_drop / load_peak) if load_peak > 1.0e-6 else 0.0

    # Extract numerical evidence
    k_struct = part_summary.k_total_structure.k_or_zero
    k_back = part_summary.k_backfill.k_or_zero
    k_arch = part_summary.k_arch.k_or_zero
    k_piers = part_summary.k_piers.k_or_zero

    act_struct = act_summary.entire_structure.fraction
    act_back = act_summary.backfill.fraction
    act_arch = act_summary.arch_barrel.fraction
    act_piers = act_summary.piers.fraction
    act_spans = {k: v.fraction for k, v in act_summary.arch_spans.items()}

    hinges_tot = dam_summary.arch_barrel.hinge_candidate_count
    hinges_spans = {k: v.hinge_candidate_count for k, v in dam_summary.arch_spans.items()}
    max_open = dam_summary.arch_barrel.max_opening
    max_rot = dam_summary.arch_barrel.max_rotation

    backfill_sliding_frac = dam_summary.backfill.sliding_area_fraction
    backfill_disp_ratio = part_summary.backfill_to_structure_disp_ratio

    d_back = dam_summary.d_backfill
    d_mas = dam_summary.d_masonry
    d_arch = dam_summary.d_arch
    d_piers = dam_summary.d_piers
    d_cont = dam_summary.d_contacts
    tot_energy = dam_summary.total_dissipated_energy
    energy_status = dam_summary.energy_status

    is_rigid = part_summary.deformation_total_structure.is_predominantly_rigid

    evidence = EvidenceBundle(
        step_number=step_number,
        load_peak=load_peak,
        load_current=load_current,
        load_drop_ratio=drop_ratio,
        monitored_displacement=monitored_displacement,
        k_total_structure=k_struct,
        k_backfill=k_back,
        k_arch=k_arch,
        k_piers=k_piers,
        active_mass_structure=act_struct,
        active_mass_backfill=act_back,
        active_mass_arch=act_arch,
        active_mass_piers=act_piers,
        active_mass_per_span=act_spans,
        arch_hinge_count=hinges_tot,
        arch_hinges_per_span=hinges_spans,
        max_arch_opening=max_open,
        max_arch_rotation=max_rot,
        backfill_sliding_area_fraction=backfill_sliding_frac,
        backfill_to_structure_disp_ratio=backfill_disp_ratio,
        d_backfill=d_back,
        d_masonry=d_mas,
        d_arch=d_arch,
        d_piers=d_piers,
        d_contacts=d_cont,
        total_dissipated_energy=tot_energy,
        energy_status=energy_status,
        is_predominantly_rigid=is_rigid,
        solver_status=solver_status,
        solver_outcome=solver_outcome,
        iterations=iterations,
    )

    rationale: list[str] = []
    category = CollapseCategory.NUMERICAL_OR_UNCERTAIN
    confidence = 0.50
    priority = ReviewPriority.MEDIUM
    desc = ""

    is_solver_failed = (solver_status == "FAILED" or solver_outcome in ("nonconverged", "failed"))
    has_significant_load_drop = drop_ratio >= thresholds.load_drop_trigger

    # -------------------------------------------------------------------------
    # Case 1: Numerical divergence or nonconvergence without physical collapse
    # -------------------------------------------------------------------------
    if is_solver_failed and hinges_tot < 2 and backfill_sliding_frac < 0.15 and drop_ratio < thresholds.significant_load_drop:
        category = CollapseCategory.NUMERICAL_OR_UNCERTAIN
        confidence = 0.85
        priority = ReviewPriority.HIGH
        desc = "Solver divergence/nonconvergence without evidence of physical collapse mechanism."
        rationale.append(f"Solver terminated with status '{solver_status}' (outcome '{solver_outcome}').")
        rationale.append(f"Arch hinge count ({hinges_tot}) and backfill sliding ({backfill_sliding_frac*100:.1f}%) remain well below failure thresholds.")
        rationale.append(f"Load drop ratio was {drop_ratio*100:.1f}%, indicating premature numerical stoppage rather than physical exhaustion.")
        return ClassificationResult(category, confidence, priority, desc, tuple(rationale), evidence, step_number)

    # -------------------------------------------------------------------------
    # Case 2: Local backfill failure
    # -------------------------------------------------------------------------
    # Conditions for local backfill failure:
    # 1. Physical mobilization: backfill interface sliding > 20%, OR dissipation dominance > 60%,
    #    OR significant load drop coinciding with backfill displacement dominance (> 3.0).
    # 2. Masonry arch barrel has zero hinges (or max opening is tiny < 0.2 mm).
    # 3. Active structural mass is small (<= 15%).
    is_backfill_dominant = (
        (
            backfill_sliding_frac >= thresholds.backfill_sliding_fraction_threshold
            or (energy_status == "AVAILABLE" and d_back >= thresholds.backfill_dissipation_dominance_ratio)
            or (has_significant_load_drop and backfill_disp_ratio >= thresholds.backfill_disp_dominance_ratio)
        )
        and hinges_tot == 0
        and max_open < thresholds.arch_hinge_opening_tolerance
        and act_struct <= thresholds.masonry_active_mass_low
    )

    if is_backfill_dominant:
        category = CollapseCategory.LOCAL_BACKFILL_FAILURE
        priority = ReviewPriority.LOW
        desc = "Localized failure and sliding in backfill directly beneath loading, with unaffected arch barrel."
        rationale.append(
            f"Backfill motion dominates structural motion (displacement ratio = {backfill_disp_ratio:.1f}, "
            f"sliding area fraction = {backfill_sliding_frac*100:.1f}%)."
        )
        rationale.append(f"Arch vault is quiescent: 0 hinges detected, peak crack opening = {max_open:.4e} cm.")
        rationale.append(f"Only {act_struct*100:.1f}% of masonry structure mass is active.")
        if energy_status == "AVAILABLE":
            rationale.append(f"Irreversible dissipation is heavily backfill-dominated (D_backfill = {d_back*100:.1f}%).")
            confidence = 0.95
        else:
            confidence = 0.88
        return ClassificationResult(category, confidence, priority, desc, tuple(rationale), evidence, step_number)

    # -------------------------------------------------------------------------
    # Case 3: Mixed or Progressive Failure
    # -------------------------------------------------------------------------
    # Concurrent active backfill sliding AND arch hinge activation (1 to 2 hinges or high contact slip)
    is_mixed = (
        (backfill_sliding_frac >= 0.15 or d_back >= 0.25 or dam_summary.backfill_contacts.sliding_area_fraction >= 0.30)
        and (hinges_tot >= 1 or act_struct >= 0.20 or d_mas >= 0.25)
        and hinges_tot < thresholds.arch_hinge_mechanism_count
    )
    if is_mixed:
        category = CollapseCategory.MIXED_OR_PROGRESSIVE_FAILURE
        confidence = 0.80
        priority = ReviewPriority.MEDIUM
        desc = "Progressive interaction between localized backfill deformation and partial arch hinge activation."
        rationale.append(f"Simultaneous backfill sliding ({backfill_sliding_frac*100:.1f}%) and arch hinge initiation ({hinges_tot} hinge(s)).")
        rationale.append(f"Active masonry mass = {act_struct*100:.1f}%, active backfill mass = {act_back*100:.1f}%.")
        if energy_status == "AVAILABLE":
            rationale.append(f"Dissipation shared across media: D_backfill = {d_back*100:.1f}%, D_masonry = {d_mas*100:.1f}%.")
        return ClassificationResult(category, confidence, priority, desc, tuple(rationale), evidence, step_number)

    # -------------------------------------------------------------------------
    # Case 4: No significant failure event (stable ascending / elastic state)
    # -------------------------------------------------------------------------
    has_arch_mechanism = (
        hinges_tot >= thresholds.arch_hinge_mechanism_count
        or (hinges_tot >= 2 and max_rot >= thresholds.arch_hinge_rotation_tolerance)
    )

    if not has_significant_load_drop and not is_solver_failed and not has_arch_mechanism:
        category = CollapseCategory.NO_SIGNIFICANT_FAILURE_EVENT
        confidence = 0.92
        priority = ReviewPriority.LOW
        desc = "No failure event detected; load factor is ascending or stable near peak without structural collapse mechanism."
        rationale.append(f"Load factor is at or near peak (drop ratio = {drop_ratio*100:.2f}% < {thresholds.load_drop_trigger*100:.1f}% threshold).")
        rationale.append(f"No complete arch collapse mechanism detected ({hinges_tot} hinge(s) present).")
        return ClassificationResult(category, confidence, priority, desc, tuple(rationale), evidence, step_number)

    # -------------------------------------------------------------------------
    # Case 5: Single-Span vs Global Bridge Structural Mechanism
    # -------------------------------------------------------------------------
    has_arch_mechanism = (
        hinges_tot >= thresholds.arch_hinge_mechanism_count
        or (hinges_tot >= 2 and max_rot >= thresholds.arch_hinge_rotation_tolerance)
    )

    if has_arch_mechanism:
        num_spans = classification.num_spans
        # Check if hinges and active mass are localized to a single span
        is_single_span = False
        target_span = ""
        if num_spans > 1 and hinges_spans:
            for sname, hcnt in hinges_spans.items():
                if hcnt >= 2 and (hcnt / max(1, hinges_tot)) >= thresholds.single_span_dominance_ratio:
                    span_act = act_spans.get(sname, 0.0)
                    other_acts = [v for k, v in act_spans.items() if k != sname]
                    if other_acts and span_act > 2.0 * max(other_acts):
                        is_single_span = True
                        target_span = sname
                        break

        if is_single_span:
            category = CollapseCategory.SINGLE_SPAN_MECHANISM
            confidence = 0.90
            priority = ReviewPriority.LOW
            desc = f"Complete structural collapse mechanism isolated to arch {target_span}."
            rationale.append(f"Arch hinge mechanism concentrated in {target_span} ({hinges_spans.get(target_span, 0)} hinges; max opening = {max_open:.3f} cm).")
            rationale.append(f"Adjacent bridge spans remain quiescent (active mass in {target_span} = {act_spans.get(target_span, 0.0)*100:.1f}%).")
            return ClassificationResult(category, confidence, priority, desc, tuple(rationale), evidence, step_number)

        # Global Bridge Mechanism
        category = CollapseCategory.GLOBAL_BRIDGE_MECHANISM
        confidence = 0.92
        priority = ReviewPriority.LOW
        if num_spans > 1:
            desc = "Multi-span structural collapse mechanism involving multiple arch spans or pier supports."
            rationale.append(f"Total arch hinges across spans = {hinges_tot} (distributed across bridge).")
        else:
            desc = "Global structural collapse mechanism involving complete arch hinge mechanism."
            rationale.append(f"Complete flexural arch mechanism formed with {hinges_tot} hinges (max rotation = {max_rot:.4f} rad).")

        rationale.append(f"Substantial active structural mass: {act_struct*100:.1f}%.")
        if is_rigid:
            rationale.append("Notice: Coordinated rigid-block kinematic rotation between hinge lines.")
        return ClassificationResult(category, confidence, priority, desc, tuple(rationale), evidence, step_number)

    # -------------------------------------------------------------------------
    # Case 6: Local Masonry Failure
    # -------------------------------------------------------------------------
    if hinges_tot in (1, 2) and act_struct <= thresholds.masonry_active_mass_low and not is_backfill_dominant:
        category = CollapseCategory.LOCAL_MASONRY_FAILURE
        confidence = 0.75
        priority = ReviewPriority.MEDIUM
        desc = "Localized masonry joint damage/opening without forming a complete multi-hinge collapse mechanism."
        rationale.append(f"Only {hinges_tot} isolated hinge/crack candidate(s) detected; incomplete for full mechanism.")
        rationale.append(f"Active structural mass is low ({act_struct*100:.1f}%).")
        return ClassificationResult(category, confidence, priority, desc, tuple(rationale), evidence, step_number)

    # -------------------------------------------------------------------------
    # Case 7: Fallback to Numerical or Uncertain
    # -------------------------------------------------------------------------
    category = CollapseCategory.NUMERICAL_OR_UNCERTAIN
    confidence = 0.50
    priority = ReviewPriority.HIGH
    desc = "Contradictory or inconclusive evidence; manual engineer inspection recommended."
    rationale.append(f"Load drop = {drop_ratio*100:.1f}%, arch hinges = {hinges_tot}, backfill sliding = {backfill_sliding_frac*100:.1f}%.")
    rationale.append("Indicators do not clearly align with a canonical local or global collapse prototype.")
    return ClassificationResult(category, confidence, priority, desc, tuple(rationale), evidence, step_number)


# =============================================================================
# Execution Level Analysis & Critical Event Finder
# =============================================================================

@dataclass(frozen=True)
class ExecutionClassificationReport:
    """Full analysis classification report including critical event tracking."""

    analysis_key: int
    analysis_name: str
    result: ClassificationResult
    critical_step_index: int
    peak_load_factor: float
    terminal_load_factor: float
    max_displacement: float
    outcome: str
    summary: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "analysis_key": self.analysis_key,
            "analysis_name": self.analysis_name,
            "outcome": self.outcome,
            "peak_load_factor": self.peak_load_factor,
            "terminal_load_factor": self.terminal_load_factor,
            "max_displacement": self.max_displacement,
            "critical_step_index": self.critical_step_index,
            "classification": self.result.to_dict(),
            "summary": self.summary,
        }


def classify_execution(
    model: Model,
    execution: AnalysisExecution,
    *,
    classification: BridgeClassification | None = None,
    intf_classification: InterfaceClassification | None = None,
    thresholds: ClassifierThresholds | None = None,
) -> ExecutionClassificationReport:
    """Classify the entire nonlinear execution by locating the critical collapse state."""
    if thresholds is None:
        thresholds = ClassifierThresholds()
    if classification is None:
        classification = classify_bridge_components(model)
    if intf_classification is None:
        intf_classification = classify_bridge_interfaces(model, classification)

    committed = execution.committed_steps
    if not committed:
        empty_evidence = EvidenceBundle(
            step_number=0,
            load_peak=0.0,
            load_current=0.0,
            load_drop_ratio=0.0,
            monitored_displacement=0.0,
            k_total_structure=0.0,
            k_backfill=0.0,
            k_arch=0.0,
            k_piers=0.0,
            active_mass_structure=0.0,
            active_mass_backfill=0.0,
            active_mass_arch=0.0,
            active_mass_piers=0.0,
            active_mass_per_span={},
            arch_hinge_count=0,
            arch_hinges_per_span={},
            max_arch_opening=0.0,
            max_arch_rotation=0.0,
            backfill_sliding_area_fraction=0.0,
            backfill_to_structure_disp_ratio=0.0,
            d_backfill=0.0,
            d_masonry=0.0,
            d_arch=0.0,
            d_piers=0.0,
            d_contacts=0.0,
            total_dissipated_energy=0.0,
            energy_status="UNAVAILABLE",
            is_predominantly_rigid=False,
            solver_status="NO_STEPS",
            solver_outcome="failed",
            iterations=0,
        )
        empty_res = ClassificationResult(
            category=CollapseCategory.NUMERICAL_OR_UNCERTAIN,
            confidence_score=0.99,
            review_priority=ReviewPriority.HIGH,
            primary_mechanism_description="Execution contains zero committed steps.",
            rationale=("Analysis failed or was aborted before committing any step.",),
            evidence=empty_evidence,
            critical_step=0,
        )
        return ExecutionClassificationReport(
            analysis_key=execution.analysis_key,
            analysis_name=execution.analysis_name,
            result=empty_res,
            critical_step_index=0,
            peak_load_factor=0.0,
            terminal_load_factor=0.0,
            max_displacement=0.0,
            outcome="no_steps",
            summary={"status": "NO_COMMITTED_STEPS"},
        )

    # Scan load-displacement history to locate peak and max drop
    load_factors: list[float] = []
    displacements: list[float] = []
    for s in committed:
        lf = float(s.get("load_factor", 0.0)) if isinstance(s, Mapping) else float(getattr(s, "load_factor", 0.0))
        disp = float(s.get("displacement", 0.0)) if isinstance(s, Mapping) else float(getattr(s, "displacement", 0.0))
        load_factors.append(lf)
        displacements.append(disp)

    peak_lf = max(load_factors, default=0.0)
    terminal_lf = load_factors[-1]
    peak_idx = load_factors.index(peak_lf)

    # Locate critical step:
    # 1. Step with maximum load drop after peak
    # 2. Or the terminal step if solver non-converged/failed
    # 3. Or peak step if analysis is ascending/elastic
    post_peak_drops = [
        (idx, (peak_lf - lf) / max(1e-6, peak_lf))
        for idx, lf in enumerate(load_factors[peak_idx:], start=peak_idx)
    ]
    max_drop_idx, max_drop_ratio = max(post_peak_drops, key=lambda x: x[1])

    is_failed = execution.outcome in (AnalysisOutcome.NONCONVERGED, AnalysisOutcome.FAILED)

    if max_drop_ratio >= thresholds.load_drop_trigger:
        critical_idx = max_drop_idx
    elif is_failed:
        critical_idx = len(committed) - 1
    else:
        critical_idx = len(committed) - 1

    crit_step = committed[critical_idx]

    def extract_u(step: Any) -> np.ndarray:
        if isinstance(step, Mapping):
            return np.asarray(step.get("u", np.zeros(0)), dtype=float)
        return np.asarray(getattr(step, "u", np.zeros(0)), dtype=float)

    u_crit = extract_u(crit_step)
    step_num = int(crit_step.get("step", critical_idx + 1)) if isinstance(crit_step, Mapping) else int(getattr(crit_step, "step", critical_idx + 1))
    lf_crit = load_factors[critical_idx]
    disp_crit = displacements[critical_idx]
    status_crit = str(crit_step.get("status", "OK")) if isinstance(crit_step, Mapping) else str(getattr(crit_step, "status", "OK"))
    iters = int(crit_step.get("iterations", 1)) if isinstance(crit_step, Mapping) else int(getattr(crit_step, "iterations", 1))
    outcome_str = str(execution.outcome.value if execution.outcome else "unknown")

    result = classify_collapse_mechanism(
        model,
        displacement_vector=u_crit,
        step_number=step_num,
        load_current=lf_crit,
        load_peak=peak_lf,
        monitored_displacement=disp_crit,
        solver_status=status_crit,
        solver_outcome=outcome_str,
        iterations=iters,
        classification=classification,
        intf_classification=intf_classification,
        thresholds=thresholds,
    )

    summary = {
        "analysis_key": execution.analysis_key,
        "analysis_name": execution.analysis_name,
        "category": result.category.value,
        "confidence_score": result.confidence_score,
        "review_priority": result.review_priority.value,
        "primary_description": result.primary_mechanism_description,
        "critical_step": step_num,
        "peak_load_factor": peak_lf,
        "terminal_load_factor": terminal_lf,
        "max_displacement": max(displacements, key=abs, default=0.0),
        "total_committed_steps": len(committed),
    }

    return ExecutionClassificationReport(
        analysis_key=execution.analysis_key,
        analysis_name=execution.analysis_name,
        result=result,
        critical_step_index=critical_idx,
        peak_load_factor=peak_lf,
        terminal_load_factor=terminal_lf,
        max_displacement=max(displacements, key=abs, default=0.0),
        outcome=outcome_str,
        summary=summary,
    )
