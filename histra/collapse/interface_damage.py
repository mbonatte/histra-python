"""Nonlinear interface activity, kinematic measures, and damage participation.

This module implements Feature 3 for masonry arch bridge collapse analysis:
- Per-interface relative opening, sliding, in-plane rotation, and flexural curvature.
- Flexural hinge candidate detection for masonry arch collapse mechanisms.
- Area-weighted spatial concentration indices for opening, sliding, and dissipation.
- Tensile cracking damage (D_t), compressive crushing damage (D_c), and plastic slip.
- Component-level irreversible energy dissipation ratios:
    D_backfill = Irreversible dissipation in backfill / Total irreversible dissipation
    D_masonry  = Irreversible dissipation in masonry / Total irreversible dissipation
    D_arch     = Irreversible dissipation in arch / Total irreversible dissipation
    D_piers    = Irreversible dissipation in piers / Total irreversible dissipation
    D_contacts = Irreversible dissipation in contacts / Total irreversible dissipation
- Distinguishes recoverable elastic deformation from irreversible behaviour.
- Gracefully degrades to purely kinematic indicators when constitutive state is unavailable.

Key Structural Engineering Rules:
- A masonry arch may fail globally through a small number of localized hinges (3 to 4 hinges);
  a global failure does not require damage to be spatially widespread.
- High backfill sliding/dissipation with quiescent arch interfaces indicates local backfill failure.
- Active arch hinges accompanied by structural kinematic mobilization indicate global collapse.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any, Mapping, Sequence

import numpy as np

from histra.collapse.participation import (
    BridgeClassification,
    classify_bridge_components,
)
from histra.model.model import Model
from histra.solver.model_manager import ModelManager
from histra.solver.outcomes import AnalysisExecution, AnalysisStep
from histra.types.phase_enum import PhaseEnum

# Constitutive state indices from hysteretic batch kernels
try:
    from histra.solver.hysteretic_kernels.interface_coulomb import (
        CCENERGY,
        CCPHASE,
        CCPLASTIC_C,
        CCPLASTIC_T,
        CCSTRAIN,
        CCSTRESS,
        CCUP,
    )
    from histra.solver.hysteretic_kernels.quad_takeda import QCENERGY
except ImportError:
    CCENERGY = 8
    CCPHASE = 9
    CCPLASTIC_T = 2
    CCPLASTIC_C = 3
    CCSTRAIN = 6
    CCSTRESS = 5
    CCUP = 2
    QCENERGY = 18


# =============================================================================
# Interface Classification
# =============================================================================

@dataclass(frozen=True)
class InterfaceClassification:
    """Structural component categorization of all model interfaces."""

    masonry_structure_interface_keys: tuple[int, ...]
    """All internal arch, pier, arch-pier, and masonry foundation interfaces."""

    arch_interface_keys: tuple[int, ...]
    """Internal arch vault interfaces."""

    pier_interface_keys: tuple[int, ...]
    """Internal pier interfaces."""

    backfill_interface_keys: tuple[int, ...]
    """Internal backfill-to-backfill interfaces."""

    backfill_contact_interface_keys: tuple[int, ...]
    """Contact interfaces between backfill and masonry (arch, spandrels, piers)."""

    foundation_interface_keys: tuple[int, ...]
    """Interfaces connected to base restraints."""

    other_interface_keys: tuple[int, ...]
    """Other structural interfaces (e.g. spandrels, abutments)."""

    arch_spans: dict[str, tuple[int, ...]] = field(default_factory=dict)
    """Arch interfaces partitioned per bridge span."""

    backfill_spans: dict[str, tuple[int, ...]] = field(default_factory=dict)
    """Backfill interfaces partitioned per bridge span."""

    interface_regions: dict[int, str] = field(default_factory=dict)
    """Mapping from interface key to primary region category."""

    interface_spans: dict[int, str] = field(default_factory=dict)
    """Mapping from interface key to span name (or None)."""

    all_interface_keys: tuple[int, ...] = ()
    """All interface keys in the model."""


def classify_bridge_interfaces(
    model: Model,
    classification: BridgeClassification | None = None,
) -> InterfaceClassification:
    """Classify model interfaces into structural regions and spans."""
    if classification is None:
        classification = classify_bridge_components(model)

    if model.collections is None:
        return InterfaceClassification(
            masonry_structure_interface_keys=(),
            arch_interface_keys=(),
            pier_interface_keys=(),
            backfill_interface_keys=(),
            backfill_contact_interface_keys=(),
            foundation_interface_keys=(),
            other_interface_keys=(),
        )

    arch_s = set(classification.arch_quad_keys)
    pier_s = set(classification.pier_quad_keys)
    back_s = set(classification.backfill_quad_keys)
    other_s = set(classification.other_quad_keys)

    arch_keys: list[int] = []
    pier_keys: list[int] = []
    backfill_keys: list[int] = []
    backfill_contact_keys: list[int] = []
    foundation_keys: list[int] = []
    other_keys: list[int] = []
    masonry_structure_keys: list[int] = []

    interface_regions: dict[int, str] = {}
    interface_spans: dict[int, str] = {}
    all_keys: list[int] = []

    # Map quad keys to span names
    quad_arch_span: dict[int, str] = {}
    for span_name, qkeys in classification.arch_spans.items():
        for qk in qkeys:
            quad_arch_span[qk] = span_name

    quad_backfill_span: dict[int, str] = {}
    for span_name, qkeys in classification.backfill_spans.items():
        for qk in qkeys:
            quad_backfill_span[qk] = span_name

    arch_spans_intf: dict[str, list[int]] = {s: [] for s in classification.arch_spans}
    backfill_spans_intf: dict[str, list[int]] = {s: [] for s in classification.backfill_spans}

    for key, intf in sorted(model.collections.interfaces.items()):
        all_keys.append(key)
        p1 = intf.parent_element_key1
        p2 = intf.parent_element_key2
        t1 = intf.parent_type_element1
        t2 = intf.parent_type_element2

        is_restraint = (t1 == "Restraint" or t2 == "Restraint" or intf.interfaccia_vincolata_computed())

        if is_restraint:
            foundation_keys.append(key)
            masonry_structure_keys.append(key)
            interface_regions[key] = "foundation"
            # Attribute foundation to span if adjacent quad is in an arch span
            other_qk = p2 if t1 == "Restraint" else p1
            if other_qk in quad_arch_span:
                sp = quad_arch_span[other_qk]
                interface_spans[key] = sp
                if sp in arch_spans_intf:
                    arch_spans_intf[sp].append(key)
            continue

        if p1 in back_s and p2 in back_s:
            backfill_keys.append(key)
            interface_regions[key] = "backfill"
            sp1 = quad_backfill_span.get(p1)
            sp2 = quad_backfill_span.get(p2)
            if sp1 and sp1 == sp2:
                interface_spans[key] = sp1
                if sp1 in backfill_spans_intf:
                    backfill_spans_intf[sp1].append(key)
        elif p1 in arch_s and p2 in arch_s:
            arch_keys.append(key)
            masonry_structure_keys.append(key)
            interface_regions[key] = "arch"
            sp1 = quad_arch_span.get(p1)
            sp2 = quad_arch_span.get(p2)
            if sp1 and sp1 == sp2:
                interface_spans[key] = sp1
                if sp1 in arch_spans_intf:
                    arch_spans_intf[sp1].append(key)
        elif p1 in pier_s and p2 in pier_s:
            pier_keys.append(key)
            masonry_structure_keys.append(key)
            interface_regions[key] = "pier"
        elif (p1 in back_s and (p2 in (arch_s | pier_s | other_s))) or (
            p2 in back_s and (p1 in (arch_s | pier_s | other_s))
        ):
            backfill_contact_keys.append(key)
            interface_regions[key] = "backfill_contact"
            # Associate contact with arch span if one parent is arch
            arch_qk = p2 if p1 in back_s else p1
            if arch_qk in quad_arch_span:
                interface_spans[key] = quad_arch_span[arch_qk]
        elif (p1 in arch_s and p2 in pier_s) or (p2 in arch_s and p1 in pier_s):
            # Arch-pier junction is part of masonry structure
            arch_keys.append(key)
            masonry_structure_keys.append(key)
            interface_regions[key] = "arch_pier"
            arch_qk = p1 if p1 in arch_s else p2
            if arch_qk in quad_arch_span:
                interface_spans[key] = quad_arch_span[arch_qk]
        else:
            other_keys.append(key)
            masonry_structure_keys.append(key)
            interface_regions[key] = "other"

    return InterfaceClassification(
        masonry_structure_interface_keys=tuple(masonry_structure_keys),
        arch_interface_keys=tuple(arch_keys),
        pier_interface_keys=tuple(pier_keys),
        backfill_interface_keys=tuple(backfill_keys),
        backfill_contact_interface_keys=tuple(backfill_contact_keys),
        foundation_interface_keys=tuple(foundation_keys),
        other_interface_keys=tuple(other_keys),
        arch_spans={k: tuple(v) for k, v in arch_spans_intf.items()},
        backfill_spans={k: tuple(v) for k, v in backfill_spans_intf.items()},
        interface_regions=interface_regions,
        interface_spans=interface_spans,
        all_interface_keys=tuple(all_keys),
    )


# =============================================================================
# Criteria & Dataclasses
# =============================================================================

@dataclass(frozen=True)
class InterfaceCriteria:
    """Configurable thresholds for interface activity, damage, and hinges."""

    opening_tolerance: float = 1.0e-3
    """Minimum opening (cm) to flag joint opening (1.0e-3 cm = 10 um)."""

    sliding_tolerance: float = 1.0e-3
    """Minimum relative sliding (cm) to flag interface sliding (10 um)."""

    rotation_tolerance: float = 1.0e-4
    """Minimum in-plane rotation (rad) to flag flexural opening/closing."""

    hinge_opening_tolerance: float = 0.02
    """Threshold opening (cm = 0.2 mm) required for flexural hinge candidacy."""

    hinge_rotation_tolerance: float = 1.0e-3
    """Threshold relative rotation (rad = 1 mrad) for flexural hinge candidacy."""

    damage_tolerance: float = 0.05
    """Minimum damage variable D_t or D_c to flag material damage (5%)."""

    dissipation_tolerance: float = 1.0e-6
    """Minimum dissipated energy (kN*cm) to consider dissipation non-zero."""


@dataclass(frozen=True)
class InterfaceKinematics:
    """Relative kinematics across an interface joint."""

    opening_max: float
    """Peak relative normal opening across the interface (cm). Positive = open."""

    opening_mean: float
    """Mean relative normal opening across the interface (cm)."""

    opening_min: float
    """Minimum relative normal opening across the interface (cm). Negative = compression."""

    sliding_in_plane: float
    """In-plane relative sliding displacement along local tangent (cm)."""

    sliding_out_of_plane: float
    """Out-of-plane relative sliding displacement (cm)."""

    sliding_magnitude: float
    """Total resultant relative sliding magnitude sqrt(s_in^2 + s_out^2) (cm)."""

    rotation_in_plane: float
    """Relative in-plane rotation across the joint theta = (w2 - w1) / L (rad)."""

    flexural_curvature_diff: float
    """Difference in flexural rotation/curvature local_u[5] - local_u[4] (rad/cm)."""

    is_opening: bool
    """True if peak opening exceeds opening_tolerance."""

    is_sliding: bool
    """True if sliding magnitude exceeds sliding_tolerance."""

    is_hinge_candidate: bool
    """True if interface exhibits one-sided opening with opposite compression and rotation."""

    def to_dict(self) -> dict[str, Any]:
        return {
            "opening_max": self.opening_max,
            "opening_mean": self.opening_mean,
            "opening_min": self.opening_min,
            "sliding_in_plane": self.sliding_in_plane,
            "sliding_out_of_plane": self.sliding_out_of_plane,
            "sliding_magnitude": self.sliding_magnitude,
            "rotation_in_plane": self.rotation_in_plane,
            "flexural_curvature_diff": self.flexural_curvature_diff,
            "is_opening": self.is_opening,
            "is_sliding": self.is_sliding,
            "is_hinge_candidate": self.is_hinge_candidate,
        }


@dataclass(frozen=True)
class InterfaceForces:
    """Local resultant forces and moments on the interface."""

    normal_force: float | None = None
    """Resultant normal force (kN). Positive = tension, negative = compression."""

    shear_force_in_plane: float | None = None
    """In-plane resultant shear force (kN)."""

    shear_force_out_of_plane: float | None = None
    """Out-of-plane resultant shear force (kN)."""

    resultant_shear: float | None = None
    """Resultant shear force magnitude (kN)."""

    bending_moment: float | None = None
    """In-plane bending moment (kN*cm)."""

    status: str = "AVAILABLE"
    """'AVAILABLE' or 'UNAVAILABLE'."""

    def to_dict(self) -> dict[str, Any]:
        return {
            "normal_force": self.normal_force,
            "shear_force_in_plane": self.shear_force_in_plane,
            "shear_force_out_of_plane": self.shear_force_out_of_plane,
            "resultant_shear": self.resultant_shear,
            "bending_moment": self.bending_moment,
            "status": self.status,
        }


@dataclass(frozen=True)
class InterfaceConstitutiveState:
    """Nonlinear constitutive damage, plastic strain, and energy dissipation."""

    tensile_damage: float | None
    """Area-weighted tensile cracking damage D_t in [0.0, 1.0]."""

    compressive_damage: float | None
    """Area-weighted compressive crushing damage D_c in [0.0, 1.0]."""

    plastic_sliding_deformation: float | None
    """Accumulated plastic shear slip from Coulomb friction (cm)."""

    is_yielding_tension: bool
    """True if any transverse fiber is in plastic tension or rupture."""

    is_yielding_compression: bool
    """True if any transverse fiber is in plastic compression or crushing."""

    is_slipping: bool
    """True if Coulomb spring is in frictional slip phase or has plastic slip."""

    cracked_fiber_fraction: float
    """Fraction of transverse fiber springs that have exceeded tensile yield."""

    crushed_fiber_fraction: float
    """Fraction of transverse fiber springs that have exceeded compressive yield."""

    dissipated_energy_normal: float | None
    """Irreversible energy dissipated in normal/flexural fiber springs (kN*cm)."""

    dissipated_energy_shear: float | None
    """Irreversible energy dissipated in Coulomb sliding springs (kN*cm)."""

    dissipated_energy_total: float | None
    """Total irreversible energy dissipated in this interface (kN*cm)."""

    nonlinear_status: str
    """'ELASTIC', 'PLASTIC_TENSION', 'PLASTIC_COMPRESSION', 'SLIP', 'RUPTURE', or 'UNAVAILABLE'."""

    energy_status: str
    """'AVAILABLE' or 'UNAVAILABLE'."""

    def to_dict(self) -> dict[str, Any]:
        return {
            "tensile_damage": self.tensile_damage,
            "compressive_damage": self.compressive_damage,
            "plastic_sliding_deformation": self.plastic_sliding_deformation,
            "is_yielding_tension": self.is_yielding_tension,
            "is_yielding_compression": self.is_yielding_compression,
            "is_slipping": self.is_slipping,
            "cracked_fiber_fraction": self.cracked_fiber_fraction,
            "crushed_fiber_fraction": self.crushed_fiber_fraction,
            "dissipated_energy_normal": self.dissipated_energy_normal,
            "dissipated_energy_shear": self.dissipated_energy_shear,
            "dissipated_energy_total": self.dissipated_energy_total,
            "nonlinear_status": self.nonlinear_status,
            "energy_status": self.energy_status,
        }


@dataclass(frozen=True)
class InterfaceActivityRecord:
    """Complete activity record for a single interface at a specific state."""

    interface_key: int
    area: float
    length: float
    region: str
    span: str | None
    parent_1_key: int
    parent_1_type: str
    parent_2_key: int
    parent_2_type: str
    kinematics: InterfaceKinematics
    forces: InterfaceForces
    constitutive: InterfaceConstitutiveState
    is_active: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "interface_key": self.interface_key,
            "area": self.area,
            "length": self.length,
            "region": self.region,
            "span": self.span,
            "parent_1": {"key": self.parent_1_key, "type": self.parent_1_type},
            "parent_2": {"key": self.parent_2_key, "type": self.parent_2_type},
            "kinematics": self.kinematics.to_dict(),
            "forces": self.forces.to_dict(),
            "constitutive": self.constitutive.to_dict(),
            "is_active": self.is_active,
        }


@dataclass(frozen=True)
class RegionalInterfaceSummary:
    """Aggregated interface activity, hinges, and energy for a component region."""

    total_interface_count: int
    total_area: float
    open_interface_count: int
    open_area_fraction: float
    sliding_interface_count: int
    sliding_area_fraction: float
    damaged_interface_count: int
    damaged_area_fraction: float
    hinge_candidate_count: int
    max_opening: float
    max_sliding: float
    max_rotation: float
    dissipated_energy: float
    dissipation_ratio: float
    spatial_concentration_opening: float
    spatial_concentration_sliding: float
    spatial_concentration_dissipation: float
    energy_status: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_interface_count": self.total_interface_count,
            "total_area": self.total_area,
            "open_interface_count": self.open_interface_count,
            "open_area_fraction": self.open_area_fraction,
            "sliding_interface_count": self.sliding_interface_count,
            "sliding_area_fraction": self.sliding_area_fraction,
            "damaged_interface_count": self.damaged_interface_count,
            "damaged_area_fraction": self.damaged_area_fraction,
            "hinge_candidate_count": self.hinge_candidate_count,
            "max_opening": self.max_opening,
            "max_sliding": self.max_sliding,
            "max_rotation": self.max_rotation,
            "dissipated_energy": self.dissipated_energy,
            "dissipation_ratio": self.dissipation_ratio,
            "spatial_concentration_opening": self.spatial_concentration_opening,
            "spatial_concentration_sliding": self.spatial_concentration_sliding,
            "spatial_concentration_dissipation": self.spatial_concentration_dissipation,
            "energy_status": self.energy_status,
        }


@dataclass(frozen=True)
class DamageParticipationSummary:
    """Comprehensive failure and damage participation across bridge components."""

    entire_masonry_structure: RegionalInterfaceSummary
    arch_barrel: RegionalInterfaceSummary
    piers: RegionalInterfaceSummary
    backfill: RegionalInterfaceSummary
    backfill_contacts: RegionalInterfaceSummary
    foundations: RegionalInterfaceSummary
    other_regions: RegionalInterfaceSummary
    arch_spans: dict[str, RegionalInterfaceSummary] = field(default_factory=dict)
    backfill_spans: dict[str, RegionalInterfaceSummary] = field(default_factory=dict)
    d_backfill: float = 0.0
    d_masonry: float = 0.0
    d_arch: float = 0.0
    d_piers: float = 0.0
    d_contacts: float = 0.0
    total_dissipated_energy: float = 0.0
    quad_dissipated_energy: float = 0.0
    energy_status: str = "AVAILABLE"
    hinge_candidate_keys: tuple[int, ...] = ()
    dominant_mechanism: str = "UNDEFINED"

    def to_dict(self) -> dict[str, Any]:
        return {
            "entire_masonry_structure": self.entire_masonry_structure.to_dict(),
            "arch_barrel": self.arch_barrel.to_dict(),
            "piers": self.piers.to_dict(),
            "backfill": self.backfill.to_dict(),
            "backfill_contacts": self.backfill_contacts.to_dict(),
            "foundations": self.foundations.to_dict(),
            "other_regions": self.other_regions.to_dict(),
            "arch_spans": {k: v.to_dict() for k, v in self.arch_spans.items()},
            "backfill_spans": {k: v.to_dict() for k, v in self.backfill_spans.items()},
            "d_backfill": self.d_backfill,
            "d_masonry": self.d_masonry,
            "d_arch": self.d_arch,
            "d_piers": self.d_piers,
            "d_contacts": self.d_contacts,
            "total_dissipated_energy": self.total_dissipated_energy,
            "quad_dissipated_energy": self.quad_dissipated_energy,
            "energy_status": self.energy_status,
            "hinge_candidate_keys": list(self.hinge_candidate_keys),
            "dominant_mechanism": self.dominant_mechanism,
        }


@dataclass(frozen=True)
class StepInterfaceReport:
    """Nonlinear interface activity and damage evaluation for a committed step."""

    step: int
    load_factor: float
    monitored_displacement: float
    incremental: DamageParticipationSummary
    cumulative: DamageParticipationSummary
    criteria: InterfaceCriteria
    interpretation_notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "step": self.step,
            "load_factor": self.load_factor,
            "monitored_displacement": self.monitored_displacement,
            "incremental": self.incremental.to_dict(),
            "cumulative": self.cumulative.to_dict(),
            "criteria": {
                "opening_tolerance": self.criteria.opening_tolerance,
                "sliding_tolerance": self.criteria.sliding_tolerance,
                "rotation_tolerance": self.criteria.rotation_tolerance,
                "hinge_opening_tolerance": self.criteria.hinge_opening_tolerance,
                "hinge_rotation_tolerance": self.criteria.hinge_rotation_tolerance,
            },
            "interpretation_notes": list(self.interpretation_notes),
        }


@dataclass(frozen=True)
class ExecutionInterfaceReport:
    """Nonlinear interface activity and damage history across all committed steps."""

    analysis_key: int
    analysis_name: str
    steps: tuple[StepInterfaceReport, ...]
    criteria: InterfaceCriteria
    summary: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "analysis_key": self.analysis_key,
            "analysis_name": self.analysis_name,
            "steps": [s.to_dict() for s in self.steps],
            "criteria": {
                "opening_tolerance": self.criteria.opening_tolerance,
                "sliding_tolerance": self.criteria.sliding_tolerance,
                "rotation_tolerance": self.criteria.rotation_tolerance,
            },
            "summary": self.summary,
        }


# =============================================================================
# Core Kinematics & Extraction Routines
# =============================================================================

def compute_spatial_concentration(areas: np.ndarray, activities: np.ndarray) -> float:
    """Compute area-weighted spatial concentration index C in [0.0, 1.0].

    C = [Σ(A_i * a_i)]^2 / [Σ(A_i) * Σ(A_i * a_i^2)]
    Returns 0.0 when no measurable activity exists.
    """
    if len(areas) == 0 or len(activities) == 0:
        return 0.0
    act = np.maximum(activities, 0.0)
    sum_a = float(np.sum(act))
    if sum_a <= 1.0e-14 or not math.isfinite(sum_a):
        return 0.0

    weighted_act = areas * act
    weighted_act2 = areas * (act * act)
    numerator = float(np.sum(weighted_act)) ** 2
    denominator = float(np.sum(areas)) * float(np.sum(weighted_act2))

    if denominator <= 1.0e-30:
        return 0.0
    val = numerator / denominator
    return float(max(0.0, min(1.0, val)))


def extract_interface_kinematics(
    intf: Any,
    displacement_vector: np.ndarray,
    *,
    criteria: InterfaceCriteria | None = None,
) -> InterfaceKinematics:
    """Extract local opening, sliding, in-plane rotation, and hinge indicators."""
    if criteria is None:
        criteria = InterfaceCriteria()

    intf._ensure_performance_cache()
    local_u = intf._local_increment(displacement_vector)
    L = float(intf.length) if intf.length > 0 else 1.0

    if not intf._perf_constrained:
        w1 = float(local_u[3] - local_u[0])
        w2 = float(local_u[2] - local_u[1])
    else:
        hl = float(intf._perf_half_length if intf._perf_half_length is not None else 0.5 * L)
        w1 = float(local_u[3] - (local_u[0] - local_u[1] * hl))
        w2 = float(local_u[2] - (local_u[0] + local_u[1] * hl))

    w_max = max(w1, w2)
    w_min = min(w1, w2)
    w_mean = 0.5 * (w1 + w2)
    theta = (w2 - w1) / L
    delta_phi = float(local_u[5] - local_u[4])

    d0 = intf._perf_d0 if intf._perf_d0 is not None else 6
    s1 = float(local_u[d0] - local_u[d0 + 1])
    s2_a = float(local_u[d0 + 2] - local_u[d0 + 4]) if len(local_u) > d0 + 4 else 0.0
    s2_b = float(local_u[d0 + 3] - local_u[d0 + 5]) if len(local_u) > d0 + 5 else 0.0
    s2 = 0.5 * (s2_a + s2_b)
    s_mag = math.sqrt(s1 * s1 + s2 * s2)

    is_open = w_max >= criteria.opening_tolerance
    is_slide = s_mag >= criteria.sliding_tolerance

    # Hinge candidate: significant opening on one edge, compression or closure on the other,
    # with relative in-plane rotation
    is_hinge = (
        w_max >= criteria.hinge_opening_tolerance
        and abs(theta) >= criteria.hinge_rotation_tolerance
        and (w_min <= 0.0 or w_min < 0.25 * w_max)
    )

    return InterfaceKinematics(
        opening_max=w_max,
        opening_mean=w_mean,
        opening_min=w_min,
        sliding_in_plane=abs(s1),
        sliding_out_of_plane=abs(s2),
        sliding_magnitude=s_mag,
        rotation_in_plane=theta,
        flexural_curvature_diff=delta_phi,
        is_opening=is_open,
        is_sliding=is_slide,
        is_hinge_candidate=is_hinge,
    )


def extract_interface_constitutive(
    intf: Any,
    runtime: Any | None = None,
    record_index: int | None = None,
    *,
    criteria: InterfaceCriteria | None = None,
) -> InterfaceConstitutiveState:
    """Extract constitutive damage variables, plastic slip, and dissipated energy."""
    if criteria is None:
        criteria = InterfaceCriteria()

    # Case 1: Active compiled batch runtime
    if runtime is not None and getattr(runtime, "committed", None) is not None:
        if record_index is None:
            record_index = getattr(runtime, "_record_by_id", {}).get(id(intf))

        if record_index is not None and 0 <= record_index < len(runtime.records):
            start = int(runtime._starts[record_index])
            stop = int(runtime._stops[record_index])
            fibers = runtime.committed[start:stop]
            fiber_count = stop - start

            e_norm = float(np.sum(fibers[:, 4]))  # col 4 is cenergy_d
            e_shear = 0.0
            p_slip = 0.0
            is_slip = False

            for s_idx in (
                int(runtime._slid_index[record_index]),
                int(runtime._oop0_index[record_index]),
                int(runtime._oop1_index[record_index]),
            ):
                if s_idx >= 0 and s_idx < len(runtime.coulomb_state):
                    c_row = runtime.coulomb_state[s_idx]
                    e_shear += float(c_row[CCENERGY])
                    slip_val = abs(float(c_row[CCUP]))
                    p_slip = max(p_slip, slip_val)
                    if int(c_row[CCPHASE]) == int(PhaseEnum.Slip) or slip_val > criteria.sliding_tolerance:
                        is_slip = True

            # Fiber damage variables
            plastic_t_count = 0
            plastic_c_count = 0
            rupture_count = 0
            tensile_damages: list[float] = []
            compressive_damages: list[float] = []

            for i in range(fiber_count):
                row = fibers[i]
                phase = int(row[8])
                prot_t = float(row[2])  # plastic strain tension
                prot_c = float(row[3])  # plastic strain compression

                # Tensile damage indicator
                if phase in (int(PhaseEnum.Plastic_t), int(PhaseEnum.RuptureTraz), int(PhaseEnum.Rupture)) or prot_t > 0:
                    plastic_t_count += 1
                    t_dam = 1.0 if phase in (int(PhaseEnum.RuptureTraz), int(PhaseEnum.Rupture)) else min(1.0, prot_t * 100.0)
                    tensile_damages.append(max(0.05, t_dam))
                else:
                    tensile_damages.append(0.0)

                # Compressive damage indicator
                if phase in (int(PhaseEnum.Plastic_c), int(PhaseEnum.RuptureComp), int(PhaseEnum.Rupture)) or prot_c > 0:
                    plastic_c_count += 1
                    c_dam = 1.0 if phase in (int(PhaseEnum.RuptureComp), int(PhaseEnum.Rupture)) else min(1.0, prot_c * 50.0)
                    compressive_damages.append(max(0.05, c_dam))
                else:
                    compressive_damages.append(0.0)

                if phase in (int(PhaseEnum.Rupture), int(PhaseEnum.RuptureTraz), int(PhaseEnum.RuptureComp)):
                    rupture_count += 1

            d_t = float(np.mean(tensile_damages)) if tensile_damages else 0.0
            d_c = float(np.mean(compressive_damages)) if compressive_damages else 0.0
            cracked_frac = float(plastic_t_count / fiber_count) if fiber_count > 0 else 0.0
            crushed_frac = float(plastic_c_count / fiber_count) if fiber_count > 0 else 0.0

            # Determine dominant nonlinear status
            if rupture_count > 0:
                nl_status = "RUPTURE"
            elif is_slip:
                nl_status = "SLIP"
            elif plastic_t_count > 0:
                nl_status = "PLASTIC_TENSION"
            elif plastic_c_count > 0:
                nl_status = "PLASTIC_COMPRESSION"
            else:
                nl_status = "ELASTIC"

            e_tot = e_norm + e_shear
            return InterfaceConstitutiveState(
                tensile_damage=d_t,
                compressive_damage=d_c,
                plastic_sliding_deformation=p_slip,
                is_yielding_tension=plastic_t_count > 0,
                is_yielding_compression=plastic_c_count > 0,
                is_slipping=is_slip,
                cracked_fiber_fraction=cracked_frac,
                crushed_fiber_fraction=crushed_frac,
                dissipated_energy_normal=e_norm,
                dissipated_energy_shear=e_shear,
                dissipated_energy_total=e_tot,
                nonlinear_status=nl_status,
                energy_status="AVAILABLE",
            )

    # Case 2: Object-level inspection (springs on interface)
    if hasattr(intf, "trasv_1") and len(intf.trasv_1) > 0:
        first_sp = intf.trasv_1[0]
        if hasattr(first_sp, "cenergy_d") or hasattr(first_sp, "phase"):
            e_norm = sum(float(getattr(s, "cenergy_d", 0.0)) for s in intf.trasv_1)
            e_shear = sum(float(getattr(s, "cenergy_d", 0.0)) for s in getattr(intf, "slid", []))
            e_shear += sum(float(getattr(s, "cenergy_d", 0.0)) for s in getattr(intf, "slid_out_plan", []))

            p_slip = 0.0
            is_slip = False
            for s in getattr(intf, "slid", []):
                slip = abs(float(getattr(s, "_cup", 0.0)))
                p_slip = max(p_slip, slip)
                if int(getattr(s, "phase", 0)) == int(PhaseEnum.Slip) or slip > criteria.sliding_tolerance:
                    is_slip = True

            cracked = sum(1 for s in intf.trasv_1 if int(getattr(s, "phase", 0)) in (int(PhaseEnum.Plastic_t), int(PhaseEnum.RuptureTraz), int(PhaseEnum.Rupture)))
            crushed = sum(1 for s in intf.trasv_1 if int(getattr(s, "phase", 0)) in (int(PhaseEnum.Plastic_c), int(PhaseEnum.RuptureComp), int(PhaseEnum.Rupture)))
            n_fib = len(intf.trasv_1)

            nl_status = "ELASTIC"
            if is_slip:
                nl_status = "SLIP"
            elif cracked > 0:
                nl_status = "PLASTIC_TENSION"
            elif crushed > 0:
                nl_status = "PLASTIC_COMPRESSION"

            return InterfaceConstitutiveState(
                tensile_damage=float(cracked / n_fib) if n_fib > 0 else 0.0,
                compressive_damage=float(crushed / n_fib) if n_fib > 0 else 0.0,
                plastic_sliding_deformation=p_slip,
                is_yielding_tension=cracked > 0,
                is_yielding_compression=crushed > 0,
                is_slipping=is_slip,
                cracked_fiber_fraction=float(cracked / n_fib) if n_fib > 0 else 0.0,
                crushed_fiber_fraction=float(crushed / n_fib) if n_fib > 0 else 0.0,
                dissipated_energy_normal=e_norm,
                dissipated_energy_shear=e_shear,
                dissipated_energy_total=e_norm + e_shear,
                nonlinear_status=nl_status,
                energy_status="AVAILABLE",
            )

    # Case 3: Constitutive state unavailable (purely kinematic evaluation)
    return InterfaceConstitutiveState(
        tensile_damage=None,
        compressive_damage=None,
        plastic_sliding_deformation=None,
        is_yielding_tension=False,
        is_yielding_compression=False,
        is_slipping=False,
        cracked_fiber_fraction=0.0,
        crushed_fiber_fraction=0.0,
        dissipated_energy_normal=None,
        dissipated_energy_shear=None,
        dissipated_energy_total=None,
        nonlinear_status="UNAVAILABLE",
        energy_status="UNAVAILABLE",
    )


def extract_interface_forces(
    intf: Any,
    runtime: Any | None = None,
    record_index: int | None = None,
) -> InterfaceForces:
    """Extract physical resultant forces on an interface."""
    # From compiled runtime resultants
    if runtime is not None and hasattr(runtime, "all_resultant_forces"):
        if record_index is None:
            record_index = getattr(runtime, "_record_by_id", {}).get(id(intf))
        if record_index is not None:
            all_res = runtime.all_resultant_forces()
            if 0 <= record_index < len(all_res):
                res = all_res[record_index]
                fx, fy, fz = float(res[0]), float(res[1]), float(res[2])
                s_res = math.sqrt(fx * fx + fz * fz)
                return InterfaceForces(
                    normal_force=fy,
                    shear_force_in_plane=fx,
                    shear_force_out_of_plane=fz,
                    resultant_shear=s_res,
                    status="AVAILABLE",
                )

    # From interface status forces
    if hasattr(intf, "status") and hasattr(intf.status, "forces"):
        forces = intf.status.forces
        if forces and len(forces) >= 3:
            fx, fy, fz = float(forces[0]), float(forces[1]), float(forces[2])
            s_res = math.sqrt(fx * fx + fz * fz)
            return InterfaceForces(
                normal_force=fy,
                shear_force_in_plane=fx,
                shear_force_out_of_plane=fz,
                resultant_shear=s_res,
                status="AVAILABLE",
            )

    return InterfaceForces(status="UNAVAILABLE")


# =============================================================================
# Regional Aggregation & Damage Participation
# =============================================================================

def evaluate_damage_participation(
    model: Model,
    displacement_vector: np.ndarray,
    *,
    classification: BridgeClassification | None = None,
    intf_classification: InterfaceClassification | None = None,
    runtime: Any | None = None,
    criteria: InterfaceCriteria | None = None,
) -> DamageParticipationSummary:
    """Evaluate interface kinematics, hinges, damage, and dissipation across all components."""
    if classification is None:
        classification = classify_bridge_components(model)
    if intf_classification is None:
        intf_classification = classify_bridge_interfaces(model, classification)
    if criteria is None:
        criteria = InterfaceCriteria()
    if runtime is None:
        runtime = ModelManager.hysteretic_batch_for(model)

    records: dict[int, InterfaceActivityRecord] = {}
    assert model.collections is not None

    for key in intf_classification.all_interface_keys:
        intf = model.collections.interfaces.get(key)
        if intf is None:
            continue

        kin = extract_interface_kinematics(intf, displacement_vector, criteria=criteria)
        rec_idx = getattr(runtime, "_record_by_id", {}).get(id(intf)) if runtime else None
        forces = extract_interface_forces(intf, runtime, rec_idx)
        const = extract_interface_constitutive(intf, runtime, rec_idx, criteria=criteria)

        reg = intf_classification.interface_regions.get(key, "other")
        span = intf_classification.interface_spans.get(key)
        area = float(intf.area())
        length = float(intf.length)

        is_act = kin.is_opening or kin.is_sliding or kin.is_hinge_candidate or const.is_yielding_tension or const.is_slipping

        records[key] = InterfaceActivityRecord(
            interface_key=key,
            area=area,
            length=length,
            region=reg,
            span=span,
            parent_1_key=int(intf.parent_element_key1),
            parent_1_type=str(intf.parent_type_element1),
            parent_2_key=int(intf.parent_element_key2),
            parent_2_type=str(intf.parent_type_element2),
            kinematics=kin,
            forces=forces,
            constitutive=const,
            is_active=is_act,
        )

    # Extract quad dissipated energy from runtime if available
    quad_energy = 0.0
    if runtime is not None and getattr(runtime, "quad_state", None) is not None:
        quad_energy = float(np.sum(runtime.quad_state[:, QCENERGY]))

    # Total dissipated energy across all interfaces
    intf_energy_sum = sum(
        (r.constitutive.dissipated_energy_total or 0.0) for r in records.values() if r.constitutive.dissipated_energy_total is not None
    )
    total_energy = intf_energy_sum + quad_energy
    has_energy = any(r.constitutive.energy_status == "AVAILABLE" for r in records.values())

    def summarize_group(keys: Sequence[int]) -> RegionalInterfaceSummary:
        group_records = [records[k] for k in keys if k in records]
        cnt = len(group_records)
        if cnt == 0:
            return RegionalInterfaceSummary(
                total_interface_count=0,
                total_area=0.0,
                open_interface_count=0,
                open_area_fraction=0.0,
                sliding_interface_count=0,
                sliding_area_fraction=0.0,
                damaged_interface_count=0,
                damaged_area_fraction=0.0,
                hinge_candidate_count=0,
                max_opening=0.0,
                max_sliding=0.0,
                max_rotation=0.0,
                dissipated_energy=0.0,
                dissipation_ratio=0.0,
                spatial_concentration_opening=0.0,
                spatial_concentration_sliding=0.0,
                spatial_concentration_dissipation=0.0,
                energy_status="UNAVAILABLE",
            )

        areas = np.array([r.area for r in group_records], dtype=float)
        tot_area = float(np.sum(areas))

        open_cnt = sum(1 for r in group_records if r.kinematics.is_opening)
        open_area = sum(r.area for r in group_records if r.kinematics.is_opening)

        slide_cnt = sum(1 for r in group_records if r.kinematics.is_sliding)
        slide_area = sum(r.area for r in group_records if r.kinematics.is_sliding)

        dam_cnt = sum(
            1 for r in group_records
            if (r.constitutive.tensile_damage or 0.0) >= criteria.damage_tolerance
            or (r.constitutive.compressive_damage or 0.0) >= criteria.damage_tolerance
            or r.constitutive.is_slipping
        )
        dam_area = sum(
            r.area for r in group_records
            if (r.constitutive.tensile_damage or 0.0) >= criteria.damage_tolerance
            or (r.constitutive.compressive_damage or 0.0) >= criteria.damage_tolerance
            or r.constitutive.is_slipping
        )

        hinge_cnt = sum(1 for r in group_records if r.kinematics.is_hinge_candidate)

        max_w = max((r.kinematics.opening_max for r in group_records), default=0.0)
        max_s = max((r.kinematics.sliding_magnitude for r in group_records), default=0.0)
        max_rot = max((abs(r.kinematics.rotation_in_plane) for r in group_records), default=0.0)

        e_group = sum((r.constitutive.dissipated_energy_total or 0.0) for r in group_records)
        ratio = (e_group / total_energy) if total_energy > criteria.dissipation_tolerance else 0.0

        # Spatial concentration calculations
        openings = np.array([max(0.0, r.kinematics.opening_max) for r in group_records], dtype=float)
        slidings = np.array([r.kinematics.sliding_magnitude for r in group_records], dtype=float)
        energies = np.array([r.constitutive.dissipated_energy_total or 0.0 for r in group_records], dtype=float)

        c_open = compute_spatial_concentration(areas, openings)
        c_slide = compute_spatial_concentration(areas, slidings)
        c_diss = compute_spatial_concentration(areas, energies)

        return RegionalInterfaceSummary(
            total_interface_count=cnt,
            total_area=tot_area,
            open_interface_count=open_cnt,
            open_area_fraction=float(open_area / tot_area) if tot_area > 0 else 0.0,
            sliding_interface_count=slide_cnt,
            sliding_area_fraction=float(slide_area / tot_area) if tot_area > 0 else 0.0,
            damaged_interface_count=dam_cnt,
            damaged_area_fraction=float(dam_area / tot_area) if tot_area > 0 else 0.0,
            hinge_candidate_count=hinge_cnt,
            max_opening=max_w,
            max_sliding=max_s,
            max_rotation=max_rot,
            dissipated_energy=e_group,
            dissipation_ratio=ratio,
            spatial_concentration_opening=c_open,
            spatial_concentration_sliding=c_slide,
            spatial_concentration_dissipation=c_diss,
            energy_status="AVAILABLE" if has_energy else "UNAVAILABLE",
        )

    sum_struct = summarize_group(intf_classification.masonry_structure_interface_keys)
    sum_arch = summarize_group(intf_classification.arch_interface_keys)
    sum_piers = summarize_group(intf_classification.pier_interface_keys)
    sum_back = summarize_group(intf_classification.backfill_interface_keys)
    sum_contacts = summarize_group(intf_classification.backfill_contact_interface_keys)
    sum_found = summarize_group(intf_classification.foundation_interface_keys)
    sum_other = summarize_group(intf_classification.other_interface_keys)

    arch_spans = {k: summarize_group(v) for k, v in intf_classification.arch_spans.items()}
    backfill_spans = {k: summarize_group(v) for k, v in intf_classification.backfill_spans.items()}

    hinge_keys = tuple(k for k, r in records.items() if r.kinematics.is_hinge_candidate)

    # Classify dominant failure mechanism
    d_back = sum_back.dissipation_ratio
    d_mas = sum_struct.dissipation_ratio
    d_arch_val = sum_arch.dissipation_ratio
    d_piers_val = sum_piers.dissipation_ratio
    d_cont_val = sum_contacts.dissipation_ratio

    if sum_arch.hinge_candidate_count >= 3 or (sum_arch.hinge_candidate_count >= 2 and sum_arch.max_rotation > 0.005):
        dom_mech = "GLOBAL_ARCH_HINGE_COLLAPSE"
    elif sum_piers.hinge_candidate_count >= 2 or sum_piers.sliding_area_fraction > 0.40:
        dom_mech = "PIER_SHEAR_OR_FLEXURAL_COLLAPSE"
    elif (
        d_back > 0.60
        or (sum_back.sliding_area_fraction >= 0.15 and sum_arch.hinge_candidate_count == 0 and sum_arch.max_opening < 0.01)
        or (sum_back.sliding_interface_count >= 2 and sum_arch.hinge_candidate_count == 0 and sum_arch.max_opening < 0.01)
    ):
        dom_mech = "LOCAL_BACKFILL_FAILURE"
    elif d_cont_val > 0.50 or sum_contacts.sliding_area_fraction > 0.40:
        dom_mech = "BACKFILL_ARCH_CONTACT_SLIP"
    elif d_mas > 0.25 and d_back > 0.25:
        dom_mech = "MIXED_PROGRESSIVE_COLLAPSE"
    else:
        dom_mech = "DISTRIBUTED_OR_ELASTIC"

    return DamageParticipationSummary(
        entire_masonry_structure=sum_struct,
        arch_barrel=sum_arch,
        piers=sum_piers,
        backfill=sum_back,
        backfill_contacts=sum_contacts,
        foundations=sum_found,
        other_regions=sum_other,
        arch_spans=arch_spans,
        backfill_spans=backfill_spans,
        d_backfill=d_back,
        d_masonry=d_mas,
        d_arch=d_arch_val,
        d_piers=d_piers_val,
        d_contacts=d_cont_val,
        total_dissipated_energy=total_energy,
        quad_dissipated_energy=quad_energy,
        energy_status="AVAILABLE" if has_energy else "UNAVAILABLE",
        hinge_candidate_keys=hinge_keys,
        dominant_mechanism=dom_mech,
    )


# =============================================================================
# Step and Execution Evaluators
# =============================================================================

def evaluate_step_interface_damage(
    model: Model,
    current_step: AnalysisStep | Mapping[str, Any],
    *,
    previous_step: AnalysisStep | Mapping[str, Any] | None = None,
    initial_step: AnalysisStep | Mapping[str, Any] | None = None,
    classification: BridgeClassification | None = None,
    intf_classification: InterfaceClassification | None = None,
    criteria: InterfaceCriteria | None = None,
) -> StepInterfaceReport:
    """Evaluate interface kinematics and damage for one committed analysis step."""
    if classification is None:
        classification = classify_bridge_components(model)
    if intf_classification is None:
        intf_classification = classify_bridge_interfaces(model, classification)
    if criteria is None:
        criteria = InterfaceCriteria()

    def extract_u(step: Any) -> np.ndarray:
        if isinstance(step, Mapping):
            return np.asarray(step.get("u", np.zeros(0)), dtype=float)
        return np.asarray(getattr(step, "u", np.zeros(0)), dtype=float)

    u_curr = extract_u(current_step)
    u_prev = extract_u(previous_step) if previous_step is not None else np.zeros_like(u_curr)
    u_init = extract_u(initial_step) if initial_step is not None else np.zeros_like(u_curr)

    delta_u = u_curr - u_prev
    cumul_u = u_curr - u_init

    runtime = ModelManager.hysteretic_batch_for(model)

    incremental = evaluate_damage_participation(
        model, delta_u, classification=classification, intf_classification=intf_classification, runtime=runtime, criteria=criteria
    )
    cumulative = evaluate_damage_participation(
        model, cumul_u, classification=classification, intf_classification=intf_classification, runtime=runtime, criteria=criteria
    )

    step_num = int(current_step.get("step", 0)) if isinstance(current_step, Mapping) else int(getattr(current_step, "step", 0))
    lf = float(current_step.get("load_factor", 0.0)) if isinstance(current_step, Mapping) else float(getattr(current_step, "load_factor", 0.0))
    mon_disp = float(current_step.get("displacement", 0.0)) if isinstance(current_step, Mapping) else float(getattr(current_step, "displacement", 0.0))

    notes: list[str] = []

    # Mechanism notes
    if cumulative.arch_barrel.hinge_candidate_count >= 3:
        notes.append(
            f"Step {step_num}: Global arch hinge mechanism activated "
            f"({cumulative.arch_barrel.hinge_candidate_count} hinges identified; "
            f"max opening={cumulative.arch_barrel.max_opening:.3f} cm, max rotation={cumulative.arch_barrel.max_rotation:.4f} rad)."
        )
    elif cumulative.arch_barrel.hinge_candidate_count > 0:
        notes.append(
            f"Step {step_num}: Localized arch hinge formation "
            f"({cumulative.arch_barrel.hinge_candidate_count} hinge(s) detected; "
            f"max opening={cumulative.arch_barrel.max_opening:.3f} cm)."
        )

    # Backfill localization notes
    if (
        (cumulative.backfill.sliding_area_fraction > 0.15 or cumulative.backfill.sliding_interface_count > 0)
        or (cumulative.backfill_contacts.sliding_area_fraction > 0.20 or cumulative.backfill_contacts.sliding_interface_count > 0)
    ) and cumulative.arch_barrel.hinge_candidate_count == 0:
        notes.append(
            f"Step {step_num}: Localized backfill failure without arch hinge formation "
            f"({cumulative.backfill.sliding_area_fraction * 100:.1f}% backfill sliding area, "
            f"{cumulative.backfill_contacts.sliding_interface_count} contact sliding joints; "
            f"arch opening={cumulative.arch_barrel.max_opening:.4e} cm)."
        )

    # Dissipation notes
    if cumulative.energy_status == "AVAILABLE" and cumulative.total_dissipated_energy > criteria.dissipation_tolerance:
        if cumulative.d_backfill > 0.65:
            notes.append(
                f"Step {step_num}: Irreversible dissipation dominated by backfill "
                f"(D_backfill={cumulative.d_backfill * 100:.1f}%, D_masonry={cumulative.d_masonry * 100:.1f}%)."
            )
        elif cumulative.d_masonry > 0.65:
            notes.append(
                f"Step {step_num}: Irreversible dissipation dominated by masonry structure "
                f"(D_masonry={cumulative.d_masonry * 100:.1f}%, D_backfill={cumulative.d_backfill * 100:.1f}%)."
            )

    return StepInterfaceReport(
        step=step_num,
        load_factor=lf,
        monitored_displacement=mon_disp,
        incremental=incremental,
        cumulative=cumulative,
        criteria=criteria,
        interpretation_notes=tuple(notes),
    )


def evaluate_execution_interface_damage(
    model: Model,
    execution: AnalysisExecution,
    *,
    classification: BridgeClassification | None = None,
    intf_classification: InterfaceClassification | None = None,
    criteria: InterfaceCriteria | None = None,
) -> ExecutionInterfaceReport:
    """Evaluate interface activity and damage history across all committed steps."""
    if classification is None:
        classification = classify_bridge_components(model)
    if intf_classification is None:
        intf_classification = classify_bridge_interfaces(model, classification)
    if criteria is None:
        criteria = InterfaceCriteria()

    committed = execution.committed_steps
    if not committed:
        return ExecutionInterfaceReport(
            analysis_key=execution.analysis_key,
            analysis_name=execution.analysis_name,
            steps=(),
            criteria=criteria,
            summary={"committed_steps": 0, "status": "NO_COMMITTED_STEPS"},
        )

    initial_step = execution.initial_step
    step_reports: list[StepInterfaceReport] = []

    prev_step = initial_step
    for step in committed:
        rep = evaluate_step_interface_damage(
            model,
            step,
            previous_step=prev_step,
            initial_step=initial_step,
            classification=classification,
            intf_classification=intf_classification,
            criteria=criteria,
        )
        step_reports.append(rep)
        prev_step = step

    terminal = step_reports[-1]
    terminal_cumul = terminal.cumulative

    summary = {
        "analysis_key": execution.analysis_key,
        "analysis_name": execution.analysis_name,
        "outcome": str(execution.outcome.value if execution.outcome else "unknown"),
        "committed_step_count": len(step_reports),
        "terminal_dominant_mechanism": terminal_cumul.dominant_mechanism,
        "terminal_arch_hinges": terminal_cumul.arch_barrel.hinge_candidate_count,
        "terminal_max_arch_opening": terminal_cumul.arch_barrel.max_opening,
        "terminal_max_arch_rotation": terminal_cumul.arch_barrel.max_rotation,
        "terminal_backfill_sliding_fraction": terminal_cumul.backfill.sliding_area_fraction,
        "terminal_d_backfill": terminal_cumul.d_backfill,
        "terminal_d_masonry": terminal_cumul.d_masonry,
        "terminal_d_arch": terminal_cumul.d_arch,
        "terminal_total_dissipated_energy": terminal_cumul.total_dissipated_energy,
        "terminal_energy_status": terminal_cumul.energy_status,
    }

    return ExecutionInterfaceReport(
        analysis_key=execution.analysis_key,
        analysis_name=execution.analysis_name,
        steps=tuple(step_reports),
        criteria=criteria,
        summary=summary,
    )
