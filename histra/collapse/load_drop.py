"""Automatic detection and diagnosis of sharp load drops in push-down analyses.

This module implements Feature 5:
- Extracts resistance history from LoadControl, DisplacementControl, and ArcLength analyses.
- Identifies maximum load (P_peak), displacement at maximum load, drop onset, and trough.
- Distinguishes legitimate post-peak softening from numerical chatter, cyclic reversals,
  and nonconverged iterations.
- Detects sharp/sudden load drops vs gradual ductile softening.
- Automatically evaluates collapse indicators at surrounding converged increments (pre-drop,
  post-drop, and incremental across the drop).
- Explicitly answers the engineering question:
    "This analysis has a significant drop in load capacity. Is it mainly caused by
     localized backfill failure, by a structural collapse mechanism, or is the result uncertain?"
"""
from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any, Mapping, Sequence

import numpy as np

from histra.collapse.classifier import (
    ClassificationResult,
    ClassifierThresholds,
    CollapseCategory,
    ReviewPriority,
    classify_collapse_mechanism,
)
from histra.collapse.interface_damage import (
    InterfaceClassification,
    classify_bridge_interfaces,
)
from histra.collapse.participation import (
    BridgeClassification,
    classify_bridge_components,
)
from histra.model.model import Model
from histra.solver.model_manager import ModelManager
from histra.solver.outcomes import AnalysisExecution, AnalysisOutcome, AnalysisStep


@dataclass(frozen=True)
class LoadDropCriteria:
    """Configurable criteria for detecting and characterizing load drops."""

    drop_threshold: float = 0.05
    """Fractional load drop from peak (default 0.05 = 5%) to flag a capacity reduction."""

    sharp_drop_threshold: float = 0.15
    """Fractional load drop (default 0.15 = 15%) indicating a major or sudden capacity loss."""

    sharp_step_limit: int = 3
    """Maximum number of increments for a drop to be classified as rapid/sharp."""

    min_absolute_resistance: float = 1.0e-4
    """Noise cutoff below which load values are deemed zero."""

    resistance_metric: str = "auto"
    """'auto' chooses reaction for displacement control, load factor for load control / arc length.
    Can also be explicitly set to 'load_factor', 'reaction', or 'reaction_z'."""


@dataclass(frozen=True)
class LoadHistoryCurve:
    """Extracted load-displacement response history of the analysis."""

    steps: tuple[int, ...]
    displacements: tuple[float, ...]
    load_factors: tuple[float, ...]
    reactions_z: tuple[float, ...]
    resistance_values: tuple[float, ...]
    control_method: str
    peak_load: float
    displacement_at_peak_load: float
    peak_step: int
    terminal_load: float
    terminal_displacement: float
    terminal_step: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "steps": list(self.steps),
            "displacements": list(self.displacements),
            "load_factors": list(self.load_factors),
            "reactions_z": list(self.reactions_z),
            "resistance_values": list(self.resistance_values),
            "control_method": self.control_method,
            "peak_load": self.peak_load,
            "displacement_at_peak_load": self.displacement_at_peak_load,
            "peak_step": self.peak_step,
            "terminal_load": self.terminal_load,
            "terminal_displacement": self.terminal_displacement,
            "terminal_step": self.terminal_step,
        }


@dataclass(frozen=True)
class LoadDropEvent:
    """A detected reduction in load capacity along the solution path."""

    event_id: int
    onset_step: int
    trough_step: int
    peak_load: float
    peak_displacement: float
    onset_load: float
    onset_displacement: float
    trough_load: float
    trough_displacement: float
    absolute_drop: float
    relative_drop_ratio: float
    step_duration: int
    is_sharp: bool
    coincides_with_failure: bool
    pre_drop_classification: ClassificationResult
    post_drop_classification: ClassificationResult
    incremental_classification: ClassificationResult
    primary_cause: str
    diagnosis: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "onset_step": self.onset_step,
            "trough_step": self.trough_step,
            "peak_load": self.peak_load,
            "peak_displacement": self.peak_displacement,
            "onset_load": self.onset_load,
            "onset_displacement": self.onset_displacement,
            "trough_load": self.trough_load,
            "trough_displacement": self.trough_displacement,
            "absolute_drop": self.absolute_drop,
            "relative_drop_ratio": self.relative_drop_ratio,
            "step_duration": self.step_duration,
            "is_sharp": self.is_sharp,
            "coincides_with_failure": self.coincides_with_failure,
            "primary_cause": self.primary_cause,
            "diagnosis": self.diagnosis,
            "pre_drop": self.pre_drop_classification.to_dict(),
            "post_drop": self.post_drop_classification.to_dict(),
            "incremental": self.incremental_classification.to_dict(),
        }


@dataclass(frozen=True)
class LoadDropAnalysisReport:
    """Comprehensive load-drop analysis report for an execution."""

    analysis_key: int
    analysis_name: str
    curve: LoadHistoryCurve
    events: tuple[LoadDropEvent, ...]
    has_significant_drop: bool
    primary_event: LoadDropEvent | None
    overall_diagnosis: str
    summary: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "analysis_key": self.analysis_key,
            "analysis_name": self.analysis_name,
            "curve": self.curve.to_dict(),
            "has_significant_drop": self.has_significant_drop,
            "events_count": len(self.events),
            "events": [e.to_dict() for e in self.events],
            "primary_event": self.primary_event.to_dict() if self.primary_event else None,
            "overall_diagnosis": self.overall_diagnosis,
            "summary": self.summary,
        }


# =============================================================================
# Extraction & Detection
# =============================================================================

def extract_load_history(
    model: Model,
    execution: AnalysisExecution,
    criteria: LoadDropCriteria | None = None,
) -> LoadHistoryCurve:
    """Extract and normalize the capacity response curve across committed steps."""
    if criteria is None:
        criteria = LoadDropCriteria()

    all_steps = execution.steps if execution.steps else execution.committed_steps
    if not all_steps:
        return LoadHistoryCurve(
            steps=(),
            displacements=(),
            load_factors=(),
            reactions_z=(),
            resistance_values=(),
            control_method="Unknown",
            peak_load=0.0,
            displacement_at_peak_load=0.0,
            peak_step=0,
            terminal_load=0.0,
            terminal_displacement=0.0,
            terminal_step=0,
        )

    # Determine analysis control method from model definition
    control_method = "LoadControl"
    if model.collections and execution.analysis_key in model.collections.analyses:
        an = model.collections.analyses[execution.analysis_key]
        type_integ = str(getattr(an, "type_integration", "")).lower()
        if "displacement" in type_integ:
            control_method = "DisplacementControl"
        elif "arc" in type_integ:
            control_method = "ArcLength"

    steps_list: list[int] = []
    disps_list: list[float] = []
    lfs_list: list[float] = []
    rz_list: list[float] = []
    resist_list: list[float] = []

    for idx, s in enumerate(all_steps):
        step_num = int(s.get("step", idx + 1)) if isinstance(s, Mapping) else int(getattr(s, "step", idx + 1))
        disp = float(s.get("displacement", 0.0)) if isinstance(s, Mapping) else float(getattr(s, "displacement", 0.0))
        lf = float(s.get("load_factor", 0.0)) if isinstance(s, Mapping) else float(getattr(s, "load_factor", 0.0))

        # Vertical reaction (balancing or reaction_z)
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

        steps_list.append(step_num)
        disps_list.append(disp)
        lfs_list.append(lf)
        rz_list.append(rz)

        # Select resistance metric
        metric = criteria.resistance_metric.lower()
        if metric in ("reaction", "reaction_z") and rz > criteria.min_absolute_resistance:
            val = rz
        elif metric == "load_factor":
            val = max(0.0, lf)
        else:  # auto
            if control_method == "DisplacementControl" and rz > criteria.min_absolute_resistance:
                val = rz
            else:
                val = max(0.0, lf)

        resist_list.append(val)

    peak_load = max(resist_list, default=0.0)
    peak_idx = resist_list.index(peak_load) if peak_load > 0 else 0
    disp_at_peak = disps_list[peak_idx]
    peak_step = steps_list[peak_idx]

    return LoadHistoryCurve(
        steps=tuple(steps_list),
        displacements=tuple(disps_list),
        load_factors=tuple(lfs_list),
        reactions_z=tuple(rz_list),
        resistance_values=tuple(resist_list),
        control_method=control_method,
        peak_load=peak_load,
        displacement_at_peak_load=disp_at_peak,
        peak_step=peak_step,
        terminal_load=resist_list[-1],
        terminal_displacement=disps_list[-1],
        terminal_step=steps_list[-1],
    )


def detect_load_drop_events(
    curve: LoadHistoryCurve,
    criteria: LoadDropCriteria | None = None,
) -> list[tuple[int, int]]:
    """Detect onset and trough step indices for significant capacity drops.

    Distinguishes legitimate post-peak softening from numerical chatter
    by enforcing drop thresholds and filtering out single-step micro-oscillations.
    """
    if criteria is None:
        criteria = LoadDropCriteria()

    values = curve.resistance_values
    n = len(values)
    if n < 2 or curve.peak_load <= criteria.min_absolute_resistance:
        return []

    peak_val = curve.peak_load
    drop_ranges: list[tuple[int, int]] = []

    # Find the global or prominent local peaks
    in_drop = False
    onset_idx = 0
    current_trough_idx = 0

    running_peak = values[0]
    running_peak_idx = 0

    for i in range(1, n):
        val = values[i]
        if val > running_peak:
            running_peak = val
            running_peak_idx = i
            in_drop = False
            continue

        drop_from_peak = (running_peak - val) / max(1e-6, running_peak)

        if not in_drop and drop_from_peak >= criteria.drop_threshold:
            # Drop initiates
            in_drop = True
            onset_idx = running_peak_idx
            current_trough_idx = i
        elif in_drop:
            if val <= values[current_trough_idx]:
                current_trough_idx = i
            elif val > values[current_trough_idx] * 1.02:
                # Reload / recovery of more than 2% closes the drop event
                tot_drop = (values[onset_idx] - values[current_trough_idx]) / max(1e-6, peak_val)
                if tot_drop >= criteria.drop_threshold:
                    drop_ranges.append((onset_idx, current_trough_idx))
                in_drop = False
                running_peak = val
                running_peak_idx = i

    if in_drop:
        tot_drop = (values[onset_idx] - values[current_trough_idx]) / max(1e-6, peak_val)
        if tot_drop >= criteria.drop_threshold:
            drop_ranges.append((onset_idx, current_trough_idx))

    return drop_ranges


# =============================================================================
# Full Load-Drop Analysis Evaluator
# =============================================================================

def evaluate_load_drop_analysis(
    model: Model,
    execution: AnalysisExecution,
    *,
    criteria: LoadDropCriteria | None = None,
    thresholds: ClassifierThresholds | None = None,
    classification: BridgeClassification | None = None,
    intf_classification: InterfaceClassification | None = None,
) -> LoadDropAnalysisReport:
    """Analyze the load-displacement response, detect drops, and diagnose their causes."""
    if criteria is None:
        criteria = LoadDropCriteria()
    if thresholds is None:
        thresholds = ClassifierThresholds()
    if classification is None:
        classification = classify_bridge_components(model)
    if intf_classification is None:
        intf_classification = classify_bridge_interfaces(model, classification)

    curve = extract_load_history(model, execution, criteria=criteria)
    all_steps = execution.steps if execution.steps else execution.committed_steps

    if not all_steps or curve.peak_load <= criteria.min_absolute_resistance:
        return LoadDropAnalysisReport(
            analysis_key=execution.analysis_key,
            analysis_name=execution.analysis_name,
            curve=curve,
            events=(),
            has_significant_drop=False,
            primary_event=None,
            overall_diagnosis="NO_SIGNIFICANT_DROP: Analysis terminated before developing measurable resistance.",
            summary={"status": "INSUFFICIENT_DATA"},
        )

    drop_indices = detect_load_drop_events(curve, criteria=criteria)

    def extract_u(step: Any) -> np.ndarray:
        if isinstance(step, Mapping):
            return np.asarray(step.get("u", np.zeros(0)), dtype=float)
        return np.asarray(getattr(step, "u", np.zeros(0)), dtype=float)

    events: list[LoadDropEvent] = []

    for event_id, (onset_idx, trough_idx) in enumerate(drop_indices, start=1):
        step_onset = all_steps[onset_idx]
        step_trough = all_steps[trough_idx]

        u_onset = extract_u(step_onset)
        u_trough = extract_u(step_trough)
        delta_u = u_trough - u_onset

        p_peak = curve.peak_load
        p_onset = curve.resistance_values[onset_idx]
        p_trough = curve.resistance_values[trough_idx]
        d_peak = curve.displacement_at_peak_load
        d_onset = curve.displacements[onset_idx]
        d_trough = curve.displacements[trough_idx]

        abs_drop = p_onset - p_trough
        rel_drop = abs_drop / max(1e-6, p_peak)
        step_duration = trough_idx - onset_idx
        is_sharp = (step_duration <= criteria.sharp_step_limit and rel_drop >= criteria.sharp_drop_threshold)

        # Check if trough coincides with nonconvergence or failure
        status_trough = str(
            step_trough.get("status", "OK")
            if isinstance(step_trough, Mapping)
            else getattr(step_trough, "status", "OK")
        )
        coincides_fail = (
            (trough_idx == len(all_steps) - 1 and execution.outcome in (AnalysisOutcome.NONCONVERGED, AnalysisOutcome.FAILED))
            or status_trough != "OK"
        )

        # 1. Pre-drop classification
        pre_class = classify_collapse_mechanism(
            model,
            displacement_vector=u_onset,
            step_number=curve.steps[onset_idx],
            load_current=p_onset,
            load_peak=p_peak,
            monitored_displacement=d_onset,
            classification=classification,
            intf_classification=intf_classification,
            thresholds=thresholds,
        )

        # 2. Post-drop classification
        post_class = classify_collapse_mechanism(
            model,
            displacement_vector=u_trough,
            step_number=curve.steps[trough_idx],
            load_current=p_trough,
            load_peak=p_peak,
            monitored_displacement=d_trough,
            solver_status=status_trough,
            solver_outcome=str(execution.outcome.value if execution.outcome else "completed"),
            classification=classification,
            intf_classification=intf_classification,
            thresholds=thresholds,
        )

        # 3. Incremental across drop
        inc_class = classify_collapse_mechanism(
            model,
            displacement_vector=delta_u,
            step_number=curve.steps[trough_idx],
            load_current=p_trough,
            load_peak=p_peak,
            monitored_displacement=d_trough - d_onset,
            classification=classification,
            intf_classification=intf_classification,
            thresholds=thresholds,
        )

        # Determine primary cause and answer the core question
        if post_class.is_local_backfill or inc_class.is_local_backfill:
            cause = "LOCAL_BACKFILL"
            diag = (
                f"LOCAL_BACKFILL_FAILURE: The {rel_drop*100:.1f}% load capacity drop "
                f"(from {p_onset:.2f} to {p_trough:.2f}) is driven by localized backfill punch-through "
                f"and interface sliding beneath the load, while the masonry arch barrel remains intact "
                f"with {post_class.evidence.arch_hinge_count} hinges."
            )
        elif post_class.category == CollapseCategory.SINGLE_SPAN_MECHANISM:
            cause = "SINGLE_SPAN_COLLAPSE"
            diag = (
                f"SINGLE_SPAN_MECHANISM: The {rel_drop*100:.1f}% load capacity drop is caused by "
                f"a structural arch hinge collapse mechanism isolated to one bridge span "
                f"({post_class.evidence.arch_hinge_count} hinges, max opening = {post_class.evidence.max_arch_opening:.3f} cm)."
            )
        elif post_class.is_global or inc_class.is_global:
            cause = "STRUCTURAL_COLLAPSE"
            diag = (
                f"GLOBAL_BRIDGE_MECHANISM: The {rel_drop*100:.1f}% load capacity drop is caused by "
                f"the formation of a structural collapse mechanism in the bridge "
                f"({post_class.evidence.arch_hinge_count} arch hinges detected, "
                f"max opening = {post_class.evidence.max_arch_opening:.3f} cm, "
                f"max rotation = {post_class.evidence.max_arch_rotation:.4f} rad)."
            )
        elif post_class.category == CollapseCategory.MIXED_OR_PROGRESSIVE_FAILURE:
            cause = "MIXED_PROGRESSIVE"
            diag = (
                f"MIXED_OR_PROGRESSIVE_FAILURE: The {rel_drop*100:.1f}% load capacity drop is driven "
                f"by progressive interaction between backfill sliding ({post_class.evidence.backfill_sliding_area_fraction*100:.1f}%) "
                f"and arch hinge initiation ({post_class.evidence.arch_hinge_count} hinge(s))."
            )
        elif coincides_fail and post_class.evidence.arch_hinge_count == 0:
            cause = "NUMERICAL_UNCERTAINTY"
            diag = (
                f"NUMERICAL_UNCERTAINTY: The {rel_drop*100:.1f}% load reduction coincided with solver "
                f"divergence without clear evidence of a physical collapse mechanism."
            )
        else:
            cause = "LOCAL_MASONRY"
            diag = (
                f"LOCAL_MASONRY_FAILURE: The {rel_drop*100:.1f}% load reduction represents localized "
                f"masonry cracking without developing a complete collapse mechanism."
            )

        events.append(
            LoadDropEvent(
                event_id=event_id,
                onset_step=curve.steps[onset_idx],
                trough_step=curve.steps[trough_idx],
                peak_load=p_peak,
                peak_displacement=d_peak,
                onset_load=p_onset,
                onset_displacement=d_onset,
                trough_load=p_trough,
                trough_displacement=d_trough,
                absolute_drop=abs_drop,
                relative_drop_ratio=rel_drop,
                step_duration=step_duration,
                is_sharp=is_sharp,
                coincides_with_failure=coincides_fail,
                pre_drop_classification=pre_class,
                post_drop_classification=post_class,
                incremental_classification=inc_class,
                primary_cause=cause,
                diagnosis=diag,
            )
        )

    has_sig_drop = len(events) > 0
    primary_event = max(events, key=lambda e: e.relative_drop_ratio) if events else None

    if primary_event is not None:
        overall_diag = primary_event.diagnosis
    else:
        overall_diag = (
            f"NO_SIGNIFICANT_DROP: Analysis completed with peak resistance {curve.peak_load:.2f} "
            f"and terminal resistance {curve.terminal_load:.2f} without capacity reductions "
            f"exceeding the {criteria.drop_threshold*100:.1f}% threshold."
        )

    summary = {
        "analysis_key": execution.analysis_key,
        "analysis_name": execution.analysis_name,
        "control_method": curve.control_method,
        "peak_load": curve.peak_load,
        "displacement_at_peak_load": curve.displacement_at_peak_load,
        "terminal_load": curve.terminal_load,
        "has_significant_drop": has_sig_drop,
        "total_drop_events": len(events),
        "primary_cause": primary_event.primary_cause if primary_event else "NONE",
        "primary_drop_ratio": primary_event.relative_drop_ratio if primary_event else 0.0,
        "overall_diagnosis": overall_diag,
    }

    return LoadDropAnalysisReport(
        analysis_key=execution.analysis_key,
        analysis_name=execution.analysis_name,
        curve=curve,
        events=tuple(events),
        has_significant_drop=has_sig_drop,
        primary_event=primary_event,
        overall_diagnosis=overall_diag,
        summary=summary,
    )
