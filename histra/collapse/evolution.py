"""Mechanism evolution tracking across push-down analysis increments.

This module implements Feature 6:
- Computes participation and collapse metrics throughout the entire analysis history,
  not only at the terminal increment.
- Exports complete time histories / load-increment histories for:
    - Load factor, applied force / vertical reaction, and resistance
    - Control displacement
    - Kinematic participation: K_total_structure, K_backfill, K_arch, K_piers, K_global
    - Active mass fractions: M_active_structure, M_active_backfill, M_active_arch, M_active_piers
    - Relevant interface activity: max opening, max rotation, hinge count, sliding fraction,
      and spatial concentration indices
    - Dissipation ratios: D_backfill, D_masonry, D_arch, D_piers (when available)
    - Active load-drop event detection along the solution path
    - Current mechanism classification at each increment
- Automatically detects mechanism transitions, specifically identifying the progression
  from localized backfill punch-through to wider structural arch/pier mechanisms.
- Features an incremental streaming tracker (MechanismEvolutionTracker) with low
  computational overhead that avoids storing full displacement or interface arrays in memory.
- Supports tabular DataFrame-compatible record export and clean CSV export.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
import io
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from histra.collapse.active_mass import (
    ActiveMassCriteria,
    evaluate_regional_active_mass,
)
from histra.collapse.classifier import (
    ClassificationResult,
    ClassifierThresholds,
    CollapseCategory,
    EvidenceBundle,
    ReviewPriority,
    classify_collapse_mechanism,
)
from histra.collapse.interface_damage import (
    InterfaceClassification,
    InterfaceCriteria,
    classify_bridge_interfaces,
)
from histra.collapse.load_drop import (
    LoadDropCriteria,
    LoadDropEvent,
    detect_load_drop_events,
    extract_load_history,
)
from histra.collapse.participation import (
    BridgeClassification,
    classify_bridge_components,
    evaluate_regional_participation,
)
from histra.model.model import Model
from histra.solver.model_manager import ModelManager
from histra.solver.outcomes import AnalysisExecution, AnalysisOutcome, AnalysisStep


# Categories considered local vs wider structural collapse
_LOCAL_CATEGORIES = {
    CollapseCategory.NO_SIGNIFICANT_FAILURE_EVENT,
    CollapseCategory.LOCAL_BACKFILL_FAILURE,
    CollapseCategory.LOCAL_MASONRY_FAILURE,
}

_WIDER_CATEGORIES = {
    CollapseCategory.MIXED_OR_PROGRESSIVE_FAILURE,
    CollapseCategory.SINGLE_SPAN_MECHANISM,
    CollapseCategory.GLOBAL_BRIDGE_MECHANISM,
}


# =============================================================================
# Step Record Data Structure
# =============================================================================

@dataclass(frozen=True)
class EvolutionStepRecord:
    """Lightweight scalar summary of collapse metrics at a single analysis increment."""

    step: int
    status: str
    load_factor: float
    applied_force: float
    resistance: float
    control_displacement: float
    is_peak: bool
    running_peak_resistance: float

    # Kinematic participation (K)
    k_total_structure: float | None
    k_backfill: float | None
    k_arch: float | None
    k_piers: float | None
    k_global: float | None

    # Active mass fraction (M_active)
    m_active_structure: float
    m_active_backfill: float
    m_active_arch: float
    m_active_piers: float
    m_active_spans: dict[str, float]

    # Interface activity
    max_arch_opening: float
    max_arch_rotation: float
    arch_hinge_count: int
    arch_hinges_per_span: dict[str, int]
    backfill_sliding_area_fraction: float
    backfill_to_structure_disp_ratio: float
    spatial_concentration_opening: float
    spatial_concentration_sliding: float

    # Dissipation ratios (if available)
    d_backfill: float
    d_masonry: float
    d_arch: float
    d_piers: float
    total_dissipated_energy: float
    energy_status: str

    # Load drop tracking
    is_in_load_drop: bool
    relative_drop_ratio: float
    drop_event_id: int | None
    is_sharp_drop: bool

    # Current mechanism classification
    classification: CollapseCategory
    confidence_score: float
    review_priority: ReviewPriority
    mechanism_summary: str

    @property
    def is_local_backfill(self) -> bool:
        return self.classification == CollapseCategory.LOCAL_BACKFILL_FAILURE

    @property
    def is_global(self) -> bool:
        return self.classification in (
            CollapseCategory.GLOBAL_BRIDGE_MECHANISM,
            CollapseCategory.SINGLE_SPAN_MECHANISM,
        )

    @property
    def is_single_span(self) -> bool:
        return self.classification == CollapseCategory.SINGLE_SPAN_MECHANISM

    def to_dict(self) -> dict[str, Any]:
        return {
            "step": self.step,
            "status": self.status,
            "load_factor": self.load_factor,
            "applied_force": self.applied_force,
            "resistance": self.resistance,
            "control_displacement": self.control_displacement,
            "is_peak": self.is_peak,
            "running_peak_resistance": self.running_peak_resistance,
            "k_total_structure": self.k_total_structure,
            "k_backfill": self.k_backfill,
            "k_arch": self.k_arch,
            "k_piers": self.k_piers,
            "k_global": self.k_global,
            "m_active_structure": self.m_active_structure,
            "m_active_backfill": self.m_active_backfill,
            "m_active_arch": self.m_active_arch,
            "m_active_piers": self.m_active_piers,
            "m_active_spans": self.m_active_spans,
            "max_arch_opening": self.max_arch_opening,
            "max_arch_rotation": self.max_arch_rotation,
            "arch_hinge_count": self.arch_hinge_count,
            "arch_hinges_per_span": self.arch_hinges_per_span,
            "backfill_sliding_area_fraction": self.backfill_sliding_area_fraction,
            "backfill_to_structure_disp_ratio": self.backfill_to_structure_disp_ratio,
            "spatial_concentration_opening": self.spatial_concentration_opening,
            "spatial_concentration_sliding": self.spatial_concentration_sliding,
            "d_backfill": self.d_backfill,
            "d_masonry": self.d_masonry,
            "d_arch": self.d_arch,
            "d_piers": self.d_piers,
            "total_dissipated_energy": self.total_dissipated_energy,
            "energy_status": self.energy_status,
            "is_in_load_drop": self.is_in_load_drop,
            "relative_drop_ratio": self.relative_drop_ratio,
            "drop_event_id": self.drop_event_id,
            "is_sharp_drop": self.is_sharp_drop,
            "classification": self.classification.value,
            "confidence_score": self.confidence_score,
            "review_priority": self.review_priority.value,
            "mechanism_summary": self.mechanism_summary,
        }

    def to_flat_dict(self) -> dict[str, Any]:
        """Flatten nested dicts into simple scalar key-values for CSV or DataFrame rows."""
        d = self.to_dict()
        # Flatten span dictionaries
        del d["m_active_spans"]
        del d["arch_hinges_per_span"]
        for sp, val in self.m_active_spans.items():
            d[f"m_active_{sp}"] = val
        for sp, cnt in self.arch_hinges_per_span.items():
            d[f"hinges_{sp}"] = cnt
        return d


# =============================================================================
# Mechanism Transition Event
# =============================================================================

@dataclass(frozen=True)
class MechanismTransition:
    """A detected shift in failure mechanism along the analysis history."""

    transition_id: int
    from_step: int
    to_step: int
    from_category: CollapseCategory
    to_category: CollapseCategory
    load_factor: float
    applied_force: float
    control_displacement: float
    delta_displacement: float
    trigger_reason: str
    is_local_to_global: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "transition_id": self.transition_id,
            "from_step": self.from_step,
            "to_step": self.to_step,
            "from_category": self.from_category.value,
            "to_category": self.to_category.value,
            "load_factor": self.load_factor,
            "applied_force": self.applied_force,
            "control_displacement": self.control_displacement,
            "delta_displacement": self.delta_displacement,
            "trigger_reason": self.trigger_reason,
            "is_local_to_global": self.is_local_to_global,
        }


# =============================================================================
# Mechanism Evolution History Container
# =============================================================================

@dataclass(frozen=True)
class MechanismEvolutionHistory:
    """Complete time history of collapse mechanism indicators and transitions."""

    analysis_key: int
    analysis_name: str
    steps: tuple[EvolutionStepRecord, ...]
    transitions: tuple[MechanismTransition, ...]
    load_drop_events: tuple[LoadDropEvent, ...]
    control_method: str
    peak_resistance: float
    displacement_at_peak: float
    peak_step: int
    terminal_resistance: float
    terminal_displacement: float
    terminal_step: int
    initial_mechanism: CollapseCategory
    terminal_mechanism: CollapseCategory
    dominant_mechanism: CollapseCategory
    has_local_to_global_transition: bool
    local_to_global_transition: MechanismTransition | None
    evolution_narrative: str
    summary: dict[str, Any] = field(default_factory=dict)

    @property
    def step_count(self) -> int:
        return len(self.steps)

    @property
    def transition_count(self) -> int:
        return len(self.transitions)

    def to_records(self) -> list[dict[str, Any]]:
        """Return row dictionaries suitable for Pandas DataFrame construction."""
        return [s.to_flat_dict() for s in self.steps]

    def to_dict(self) -> dict[str, Any]:
        return {
            "analysis_key": self.analysis_key,
            "analysis_name": self.analysis_name,
            "step_count": self.step_count,
            "control_method": self.control_method,
            "peak_resistance": self.peak_resistance,
            "displacement_at_peak": self.displacement_at_peak,
            "peak_step": self.peak_step,
            "terminal_resistance": self.terminal_resistance,
            "terminal_displacement": self.terminal_displacement,
            "terminal_step": self.terminal_step,
            "initial_mechanism": self.initial_mechanism.value,
            "terminal_mechanism": self.terminal_mechanism.value,
            "dominant_mechanism": self.dominant_mechanism.value,
            "has_local_to_global_transition": self.has_local_to_global_transition,
            "local_to_global_transition": (
                self.local_to_global_transition.to_dict()
                if self.local_to_global_transition
                else None
            ),
            "transitions_count": len(self.transitions),
            "transitions": [t.to_dict() for t in self.transitions],
            "load_drop_events_count": len(self.load_drop_events),
            "load_drop_events": [e.to_dict() for e in self.load_drop_events],
            "evolution_narrative": self.evolution_narrative,
            "summary": self.summary,
            "steps": [s.to_dict() for s in self.steps],
        }

    def export_csv(self, filepath: str | Path) -> None:
        """Export the step evolution history to a CSV file."""
        records = self.to_records()
        if not records:
            Path(filepath).write_text("", encoding="utf-8")
            return

        headers = list(records[0].keys())
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for r in records:
                # Format None values as NA
                row = {k: ("NA" if v is None else v) for k, v in r.items()}
                writer.writerow(row)

    def to_csv_string(self) -> str:
        """Export the step evolution history to a CSV-formatted string."""
        records = self.to_records()
        if not records:
            return ""
        headers = list(records[0].keys())
        out = io.StringIO()
        writer = csv.DictWriter(out, fieldnames=headers)
        writer.writeheader()
        for r in records:
            row = {k: ("NA" if v is None else v) for k, v in r.items()}
            writer.writerow(row)
        return out.getvalue()


# =============================================================================
# Incremental Streaming Tracker
# =============================================================================

class MechanismEvolutionTracker:
    """Streaming, incremental evaluator of mechanism evolution with low memory overhead.

    Avoids keeping full displacement or interface arrays in memory by computing
    scalar indicators on the fly and storing only lightweight summary records.
    """

    def __init__(
        self,
        model: Model,
        *,
        analysis_key: int = 0,
        analysis_name: str = "",
        control_method: str = "auto",
        thresholds: ClassifierThresholds | None = None,
        drop_criteria: LoadDropCriteria | None = None,
        active_criteria: ActiveMassCriteria | None = None,
        intf_criteria: InterfaceCriteria | None = None,
        classification: BridgeClassification | None = None,
        intf_classification: InterfaceClassification | None = None,
    ) -> None:
        self.model = model
        self.analysis_key = int(analysis_key)
        self.analysis_name = str(analysis_name)
        self.control_method = control_method

        self.thresholds = thresholds or ClassifierThresholds()
        self.drop_criteria = drop_criteria or LoadDropCriteria()
        self.active_criteria = active_criteria or ActiveMassCriteria(
            relative_threshold=0.10, absolute_threshold=1.0e-4
        )
        self.intf_criteria = intf_criteria or InterfaceCriteria(
            hinge_opening_tolerance=self.thresholds.arch_hinge_opening_tolerance,
            hinge_rotation_tolerance=self.thresholds.arch_hinge_rotation_tolerance,
        )

        # Precompute and cache geometric classifications once
        self.classification = classification or classify_bridge_components(model)
        self.intf_classification = intf_classification or classify_bridge_interfaces(
            model, self.classification
        )
        self.runtime = ModelManager.hysteretic_batch_for(model)

        # State tracking
        self._records: list[EvolutionStepRecord] = []
        self._transitions: list[MechanismTransition] = []
        self._running_peak_res: float = 0.0
        self._running_peak_step: int = 0
        self._running_peak_disp: float = 0.0
        self._running_trough_res: float = 0.0

        self._in_drop: bool = False
        self._active_drop_id: int = 0
        self._drop_onset_step: int = 0

        self._prev_category: CollapseCategory | None = None
        self._prev_disp: float = 0.0
        self._prev_lf: float = 0.0
        self._prev_fz: float = 0.0

    def process_step(
        self,
        *,
        step_number: int,
        u: np.ndarray,
        load_factor: float = 0.0,
        displacement: float = 0.0,
        reaction_z: float = 0.0,
        status: str = "OK",
        iterations: int = 1,
        solver_outcome: str = "in_progress",
    ) -> EvolutionStepRecord:
        """Process a single analysis step incrementally and append to history."""
        # Normalize applied force / reaction
        fz = abs(float(reaction_z))
        lf = float(load_factor)
        disp = float(displacement)

        # Resistance metric
        if self.control_method.lower() in ("displacement", "displacementcontrol") and fz > 1.0e-4:
            resistance = fz
        elif self.control_method.lower() in ("load", "loadcontrol", "arclength"):
            resistance = max(0.0, lf)
        else:
            # Auto
            resistance = fz if fz > 1.0e-4 and "disp" in self.control_method.lower() else max(0.0, lf)

        # Update running peak and load drop detection
        if resistance > self._running_peak_res:
            self._running_peak_res = resistance
            self._running_peak_step = step_number
            self._running_peak_disp = disp
            self._running_trough_res = resistance
            is_peak = True
            if self._in_drop and (resistance > self._running_trough_res * 1.02):
                self._in_drop = False
        else:
            is_peak = False
            drop_ratio = (self._running_peak_res - resistance) / max(1e-6, self._running_peak_res)
            if drop_ratio >= self.drop_criteria.drop_threshold:
                if not self._in_drop:
                    self._in_drop = True
                    self._active_drop_id += 1
                    self._drop_onset_step = self._running_peak_step
                if resistance < self._running_trough_res:
                    self._running_trough_res = resistance
            elif self._in_drop and (resistance > self._running_trough_res * 1.02):
                self._in_drop = False

        rel_drop = (
            (self._running_peak_res - resistance) / max(1e-6, self._running_peak_res)
            if self._running_peak_res > 1.0e-4
            else 0.0
        )
        is_sharp = bool(self._in_drop and rel_drop >= self.drop_criteria.sharp_drop_threshold)

        # Classify current step mechanism
        result = classify_collapse_mechanism(
            self.model,
            displacement_vector=u,
            step_number=step_number,
            load_current=resistance,
            load_peak=self._running_peak_res,
            monitored_displacement=disp,
            solver_status=status,
            solver_outcome=solver_outcome,
            iterations=iterations,
            classification=self.classification,
            intf_classification=self.intf_classification,
            thresholds=self.thresholds,
            runtime=self.runtime,
        )

        ev = result.evidence

        # Check for mechanism transition
        if self._prev_category is not None and result.category != self._prev_category:
            from_cat = self._prev_category
            to_cat = result.category
            is_loc_to_glob = (from_cat in _LOCAL_CATEGORIES and to_cat in _WIDER_CATEGORIES)

            # Build rationale for trigger
            reasons: list[str] = []
            if ev.arch_hinge_count > 0:
                reasons.append(f"arch hinges reached {ev.arch_hinge_count}")
            if ev.backfill_sliding_area_fraction > 0.10:
                reasons.append(f"backfill sliding fraction = {ev.backfill_sliding_area_fraction*100:.1f}%")
            if rel_drop >= self.drop_criteria.drop_threshold:
                reasons.append(f"capacity dropped by {rel_drop*100:.1f}%")
            if not reasons:
                reasons.append(result.primary_mechanism_description)

            trans = MechanismTransition(
                transition_id=len(self._transitions) + 1,
                from_step=self._records[-1].step if self._records else step_number - 1,
                to_step=step_number,
                from_category=from_cat,
                to_category=to_cat,
                load_factor=lf,
                applied_force=fz,
                control_displacement=disp,
                delta_displacement=disp - self._prev_disp,
                trigger_reason="; ".join(reasons),
                is_local_to_global=is_loc_to_glob,
            )
            self._transitions.append(trans)

        # Build lightweight step record
        rec = EvolutionStepRecord(
            step=step_number,
            status=status,
            load_factor=lf,
            applied_force=fz,
            resistance=resistance,
            control_displacement=disp,
            is_peak=is_peak,
            running_peak_resistance=self._running_peak_res,
            k_total_structure=ev.k_total_structure if ev.k_total_structure > 0 else None,
            k_backfill=ev.k_backfill if ev.k_backfill > 0 else None,
            k_arch=ev.k_arch if ev.k_arch > 0 else None,
            k_piers=ev.k_piers if ev.k_piers > 0 else None,
            k_global=ev.k_total_structure,  # fallback to structure
            m_active_structure=ev.active_mass_structure,
            m_active_backfill=ev.active_mass_backfill,
            m_active_arch=ev.active_mass_arch,
            m_active_piers=ev.active_mass_piers,
            m_active_spans=dict(ev.active_mass_per_span),
            max_arch_opening=ev.max_arch_opening,
            max_arch_rotation=ev.max_arch_rotation,
            arch_hinge_count=ev.arch_hinge_count,
            arch_hinges_per_span=dict(ev.arch_hinges_per_span),
            backfill_sliding_area_fraction=ev.backfill_sliding_area_fraction,
            backfill_to_structure_disp_ratio=ev.backfill_to_structure_disp_ratio,
            spatial_concentration_opening=ev.spatial_concentration_opening if hasattr(ev, "spatial_concentration_opening") else 0.0,
            spatial_concentration_sliding=ev.spatial_concentration_sliding if hasattr(ev, "spatial_concentration_sliding") else 0.0,
            d_backfill=ev.d_backfill,
            d_masonry=ev.d_masonry,
            d_arch=ev.d_arch,
            d_piers=ev.d_piers,
            total_dissipated_energy=ev.total_dissipated_energy,
            energy_status=ev.energy_status,
            is_in_load_drop=self._in_drop,
            relative_drop_ratio=rel_drop,
            drop_event_id=self._active_drop_id if self._in_drop else None,
            is_sharp_drop=is_sharp,
            classification=result.category,
            confidence_score=result.confidence_score,
            review_priority=result.review_priority,
            mechanism_summary=result.primary_mechanism_description,
        )

        self._records.append(rec)
        self._prev_category = result.category
        self._prev_disp = disp
        self._prev_lf = lf
        self._prev_fz = fz

        return rec

    def finalize(
        self,
        load_drop_events: Sequence[LoadDropEvent] | None = None,
    ) -> MechanismEvolutionHistory:
        """Finalize the history and compile narrative and transition summary."""
        if not self._records:
            return MechanismEvolutionHistory(
                analysis_key=self.analysis_key,
                analysis_name=self.analysis_name,
                steps=(),
                transitions=(),
                load_drop_events=(),
                control_method=self.control_method,
                peak_resistance=0.0,
                displacement_at_peak=0.0,
                peak_step=0,
                terminal_resistance=0.0,
                terminal_displacement=0.0,
                terminal_step=0,
                initial_mechanism=CollapseCategory.NUMERICAL_OR_UNCERTAIN,
                terminal_mechanism=CollapseCategory.NUMERICAL_OR_UNCERTAIN,
                dominant_mechanism=CollapseCategory.NUMERICAL_OR_UNCERTAIN,
                has_local_to_global_transition=False,
                local_to_global_transition=None,
                evolution_narrative="Analysis contains no steps.",
                summary={"status": "EMPTY"},
            )

        steps = tuple(self._records)
        transitions = tuple(self._transitions)
        drop_events = tuple(load_drop_events or ())

        # Locate peak step
        peak_rec = max(steps, key=lambda s: s.resistance)
        term_rec = steps[-1]

        init_mech = steps[0].classification
        term_mech = term_rec.classification

        # Dominant mechanism: highest-severity mechanism encountered
        severity_order = [
            CollapseCategory.GLOBAL_BRIDGE_MECHANISM,
            CollapseCategory.SINGLE_SPAN_MECHANISM,
            CollapseCategory.MIXED_OR_PROGRESSIVE_FAILURE,
            CollapseCategory.LOCAL_BACKFILL_FAILURE,
            CollapseCategory.LOCAL_MASONRY_FAILURE,
            CollapseCategory.NO_SIGNIFICANT_FAILURE_EVENT,
            CollapseCategory.NUMERICAL_OR_UNCERTAIN,
        ]
        dominant_mech = term_mech
        for cat in severity_order:
            if any(s.classification == cat for s in steps):
                dominant_mech = cat
                break

        # Check local-to-global transition
        loc_to_glob_trans: MechanismTransition | None = None
        for t in transitions:
            if t.is_local_to_global:
                loc_to_glob_trans = t
                break

        has_loc_to_glob = loc_to_glob_trans is not None

        # Build evolution narrative
        narrative_lines: list[str] = [
            f"Mechanism Evolution for Analysis {self.analysis_key} ('{self.analysis_name}'):",
            f"- Total Increments: {len(steps)} | Peak Resistance: {peak_rec.resistance:.3f} at step {peak_rec.step} (disp = {peak_rec.control_displacement:.3f} cm) | Terminal: {term_rec.resistance:.3f} (disp = {term_rec.control_displacement:.3f} cm).",
            f"- Initial Mechanism: {init_mech.value} | Terminal Mechanism: {term_mech.value} | Dominant: {dominant_mech.value}.",
        ]

        if transitions:
            narrative_lines.append(f"- Detected {len(transitions)} mechanism transition(s):")
            for t in transitions:
                loc_flag = " [LOCAL-TO-GLOBAL TRANSITION]" if t.is_local_to_global else ""
                narrative_lines.append(
                    f"  * Step {t.to_step} (LF={t.load_factor:.2f}, disp={t.control_displacement:.2f} cm): "
                    f"{t.from_category.value} -> {t.to_category.value}{loc_flag} ({t.trigger_reason})"
                )
        else:
            narrative_lines.append(f"- No mechanism transitions detected along the equilibrium path; response remained {dominant_mech.value} throughout.")

        if has_loc_to_glob and loc_to_glob_trans is not None:
            narrative_lines.append(
                f"- Progression Assessment: Bridge underwent a verified transition from localized failure "
                f"to a structural mechanism at Step {loc_to_glob_trans.to_step} (disp = {loc_to_glob_trans.control_displacement:.2f} cm)."
            )
        else:
            narrative_lines.append("- Progression Assessment: No local-to-global transition occurred.")

        narrative = "\n".join(narrative_lines)

        return MechanismEvolutionHistory(
            analysis_key=self.analysis_key,
            analysis_name=self.analysis_name,
            steps=steps,
            transitions=transitions,
            load_drop_events=drop_events,
            control_method=self.control_method,
            peak_resistance=peak_rec.resistance,
            displacement_at_peak=peak_rec.control_displacement,
            peak_step=peak_rec.step,
            terminal_resistance=term_rec.resistance,
            terminal_displacement=term_rec.control_displacement,
            terminal_step=term_rec.step,
            initial_mechanism=init_mech,
            terminal_mechanism=term_mech,
            dominant_mechanism=dominant_mech,
            has_local_to_global_transition=has_loc_to_glob,
            local_to_global_transition=loc_to_glob_trans,
            evolution_narrative=narrative,
            summary={
                "step_count": len(steps),
                "peak_resistance": peak_rec.resistance,
                "terminal_resistance": term_rec.resistance,
                "has_local_to_global": has_loc_to_glob,
                "dominant_mechanism": dominant_mech.value,
            },
        )


# =============================================================================
# High-Level Evolution Tracking Function
# =============================================================================

def track_mechanism_evolution(
    model: Model,
    execution: AnalysisExecution,
    *,
    thresholds: ClassifierThresholds | None = None,
    drop_criteria: LoadDropCriteria | None = None,
    active_criteria: ActiveMassCriteria | None = None,
    intf_criteria: InterfaceCriteria | None = None,
    classification: BridgeClassification | None = None,
    intf_classification: InterfaceClassification | None = None,
) -> MechanismEvolutionHistory:
    """Track the full mechanism evolution across all steps of an executed analysis.

    Uses the streaming tracker to process increments with low memory overhead.
    """
    raw_steps = execution.steps if execution.steps else execution.committed_steps

    # Infer control method
    control_method = "LoadControl"
    if model.collections and execution.analysis_key in model.collections.analyses:
        an = model.collections.analyses[execution.analysis_key]
        type_integ = str(getattr(an, "type_integration", "")).lower()
        if "displacement" in type_integ:
            control_method = "DisplacementControl"
        elif "arc" in type_integ:
            control_method = "ArcLength"

    # Pre-extract load drops for correlation
    history_curve = extract_load_history(model, execution, criteria=drop_criteria)
    drop_ranges = detect_load_drop_events(history_curve, criteria=drop_criteria)

    # Initialize streaming tracker
    tracker = MechanismEvolutionTracker(
        model,
        analysis_key=execution.analysis_key,
        analysis_name=execution.analysis_name,
        control_method=control_method,
        thresholds=thresholds,
        drop_criteria=drop_criteria,
        active_criteria=active_criteria,
        intf_criteria=intf_criteria,
        classification=classification,
        intf_classification=intf_classification,
    )

    for idx, s in enumerate(raw_steps):
        step_num = int(s.get("step", idx + 1) if isinstance(s, Mapping) else getattr(s, "step", idx + 1))
        status = str(s.get("status", "OK") if isinstance(s, Mapping) else getattr(s, "status", "OK"))
        lf = float(s.get("load_factor", 0.0) if isinstance(s, Mapping) else getattr(s, "load_factor", 0.0))
        disp = float(s.get("displacement", 0.0) if isinstance(s, Mapping) else getattr(s, "displacement", 0.0))

        # Vertical reaction
        rz = 0.0
        if isinstance(s, Mapping):
            if "balancing_reaction_z" in s and s["balancing_reaction_z"] is not None:
                rz = float(s["balancing_reaction_z"])
            elif "reaction_z" in s and s["reaction_z"] is not None:
                rz = abs(float(s["reaction_z"]))
        else:
            if hasattr(s, "balancing_reaction_z") and getattr(s, "balancing_reaction_z") is not None:
                rz = float(getattr(s, "balancing_reaction_z"))
            elif hasattr(s, "reaction_z") and getattr(s, "reaction_z") is not None:
                rz = abs(float(getattr(s, "reaction_z")))

        u = np.asarray(s.get("u", np.zeros(0)) if isinstance(s, Mapping) else getattr(s, "u", np.zeros(0)), dtype=float)
        iters = int(s.get("iterations", 1) if isinstance(s, Mapping) else getattr(s, "iterations", 1))

        tracker.process_step(
            step_number=step_num,
            u=u,
            load_factor=lf,
            displacement=disp,
            reaction_z=rz,
            status=status,
            iterations=iters,
            solver_outcome=str(execution.outcome.value if execution.outcome else "completed"),
        )

    return tracker.finalize()
