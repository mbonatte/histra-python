"""Kinematic Participation Index for masonry arch bridge collapse analysis.

This module implements a dimensionless kinematic participation index inspired by
effective modal mass participation, adapted for static nonlinear push-down analyses:

    K = [Σ(m_i × a_i)]² / [Σ(m_i) × Σ(m_i × a_i²)]

where:
    m_i  = mass (or mass weight) assigned to integration / sampling point i
    a_i  = displacement magnitude of point i:
           a_i = sqrt(ux_i² + uy_i² + uz_i²)   (or directional |u_{d, i}|)

Properties of K:
    - Bounded in [0, 1] for all valid nonzero displacement fields (by Cauchy-Schwarz).
    - K = 1.0 represents uniform translation of the entire mass group.
    - K << 1.0 represents spatially concentrated, localized movement.
    - If max(a_i) is below motion_tolerance, returns status "NO_MOTION".

Important Engineering Interpretation Rules:
    - High K indicates distributed kinematic motion across the structure, NOT necessarily
      structural collapse (e.g. distributed elastic settlement or uniform deformation).
    - Low K indicates spatially concentrated or non-uniform deformation (e.g. localized
      backfill punch-through, localized hinge formation, or single-pier sliding).
    - The index MUST NOT be presented as a literal percentage of failed mass.
    - Whole-structure rigid-body displacement or rotation must not automatically be
      classified as structural collapse; relative internal deformations (shear strains,
      interface crack openings, and frictional slips) must be examined alongside K.
    - Both incremental displacements (Δu) and cumulative displacements (u) are evaluated
      and clearly distinguished.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any, Mapping, Sequence

import numpy as np

from histra.elements.quad import Quad
from histra.model.model import Model
from histra.postprocessing import quad_node_displacement, _quad_local_displacement
from histra.solver.mass_matrix import GRAVITY_ACCELERATION
from histra.solver.outcomes import AnalysisExecution, AnalysisStep


@dataclass(frozen=True)
class KinematicParticipationIndex:
    """Dimensionless kinematic participation index for a single region or direction."""

    k: float | None
    status: str
    total_mass: float
    max_disp: float
    mean_disp: float
    direction: str = "all"
    disp_variance: float = 0.0

    @property
    def is_valid(self) -> bool:
        """True if the index was computed from measurable movement."""
        return self.status == "VALID" and self.k is not None

    @property
    def has_motion(self) -> bool:
        """True if measurable motion was detected in this region."""
        return self.status not in {"NO_MOTION", "NO_MASS", "NOT_PRESENT"}

    @property
    def k_or_zero(self) -> float:
        """Return numeric K if valid, or 0.0."""
        return float(self.k) if self.k is not None else 0.0

    @property
    def active_mass(self) -> float:
        """Effective mass participating in the motion: K * total_mass."""
        return self.k_or_zero * self.total_mass

    @property
    def concentration_ratio(self) -> float:
        """Ratio of maximum displacement to mean displacement (1.0 = uniform, >> 1.0 = localized)."""
        if self.mean_disp > 1.0e-30:
            return float(self.max_disp / self.mean_disp)
        return 1.0 if self.max_disp < 1.0e-30 else float("inf")

    @property
    def spatial_distribution(self) -> str:
        """Qualitative description of spatial movement distribution."""
        if not self.is_valid:
            return self.status
        val = self.k_or_zero
        if val >= 0.60:
            return "DISTRIBUTED"
        if val >= 0.25:
            return "MODERATE"
        return "LOCALIZED"

    def to_dict(self) -> dict[str, Any]:
        return {
            "k": self.k,
            "status": self.status,
            "total_mass": self.total_mass,
            "active_mass": self.active_mass,
            "max_disp": self.max_disp,
            "mean_disp": self.mean_disp,
            "disp_variance": self.disp_variance,
            "concentration_ratio": self.concentration_ratio,
            "direction": self.direction,
            "spatial_distribution": self.spatial_distribution,
        }


@dataclass(frozen=True)
class RegionDeformationMetrics:
    """Relative and internal deformation indicators for a structural region."""

    max_disp: float
    mean_disp: float
    max_shear_strain: float
    max_interface_opening: float
    max_interface_sliding: float
    dissipated_energy: float = 0.0
    is_predominantly_rigid: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_disp": self.max_disp,
            "mean_disp": self.mean_disp,
            "max_shear_strain": self.max_shear_strain,
            "max_interface_opening": self.max_interface_opening,
            "max_interface_sliding": self.max_interface_sliding,
            "dissipated_energy": self.dissipated_energy,
            "is_predominantly_rigid": self.is_predominantly_rigid,
        }


@dataclass(frozen=True)
class BridgeClassification:
    """Mapping of bridge elements into structural and component subsets."""

    total_structure_quad_keys: tuple[int, ...]
    backfill_quad_keys: tuple[int, ...]
    arch_quad_keys: tuple[int, ...]
    pier_quad_keys: tuple[int, ...]
    other_quad_keys: tuple[int, ...] = ()
    all_quad_keys: tuple[int, ...] = ()

    @property
    def has_piers(self) -> bool:
        return len(self.pier_quad_keys) > 0

    @property
    def has_backfill(self) -> bool:
        return len(self.backfill_quad_keys) > 0

    @property
    def has_arch(self) -> bool:
        return len(self.arch_quad_keys) > 0


@dataclass(frozen=True)
class RegionalParticipationSummary:
    """Summary of kinematic participation and deformation across all components."""

    k_total_structure: KinematicParticipationIndex
    k_backfill: KinematicParticipationIndex
    k_arch: KinematicParticipationIndex
    k_piers: KinematicParticipationIndex
    k_global: KinematicParticipationIndex
    k_x: KinematicParticipationIndex
    k_y: KinematicParticipationIndex
    k_z: KinematicParticipationIndex
    deformation_total_structure: RegionDeformationMetrics
    deformation_backfill: RegionDeformationMetrics
    deformation_arch: RegionDeformationMetrics
    deformation_piers: RegionDeformationMetrics
    backfill_to_structure_disp_ratio: float = 0.0
    backfill_to_arch_disp_ratio: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "k_total_structure": self.k_total_structure.to_dict(),
            "k_backfill": self.k_backfill.to_dict(),
            "k_arch": self.k_arch.to_dict(),
            "k_piers": self.k_piers.to_dict(),
            "k_global": self.k_global.to_dict(),
            "k_x": self.k_x.to_dict(),
            "k_y": self.k_y.to_dict(),
            "k_z": self.k_z.to_dict(),
            "deformation_total_structure": self.deformation_total_structure.to_dict(),
            "deformation_backfill": self.deformation_backfill.to_dict(),
            "deformation_arch": self.deformation_arch.to_dict(),
            "deformation_piers": self.deformation_piers.to_dict(),
            "backfill_to_structure_disp_ratio": self.backfill_to_structure_disp_ratio,
            "backfill_to_arch_disp_ratio": self.backfill_to_arch_disp_ratio,
        }


@dataclass(frozen=True)
class StepParticipationReport:
    """Complete kinematic participation evaluation for one converged analysis step."""

    step: int
    load_factor: float
    monitored_displacement: float
    incremental: RegionalParticipationSummary
    cumulative: RegionalParticipationSummary
    interpretation_notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "step": self.step,
            "load_factor": self.load_factor,
            "monitored_displacement": self.monitored_displacement,
            "incremental": self.incremental.to_dict(),
            "cumulative": self.cumulative.to_dict(),
            "interpretation_notes": list(self.interpretation_notes),
        }


@dataclass(frozen=True)
class ExecutionParticipationReport:
    """Kinematic participation history across all committed steps of an analysis."""

    analysis_key: int
    analysis_name: str
    steps: tuple[StepParticipationReport, ...]
    summary: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "analysis_key": self.analysis_key,
            "analysis_name": self.analysis_name,
            "steps": [s.to_dict() for s in self.steps],
            "summary": self.summary,
        }


# =============================================================================
# Core Mathematical Participation Function
# =============================================================================

def compute_kinematic_participation(
    masses: np.ndarray,
    displacements: np.ndarray,
    *,
    motion_tolerance: float = 1.0e-9,
    direction: str = "all",
) -> KinematicParticipationIndex:
    """Compute the dimensionless kinematic participation index K.

    K = [Σ(m_i × a_i)]² / [Σ(m_i) × Σ(m_i × a_i²)]

    Parameters
    ----------
    masses : np.ndarray
        1D array of positive mass weights for each point.
    displacements : np.ndarray
        Array of point displacements. Can be:
        - 1D scalar magnitudes a_i >= 0
        - 2D vectors of shape (N, 3) for (ux, uy, uz)
    motion_tolerance : float
        Displacement threshold below which motion is treated as negligible ("NO_MOTION").
    direction : str
        Direction label: "all", "x", "y", "z".
    """
    m = np.asarray(masses, dtype=np.float64).ravel()
    d = np.asarray(displacements, dtype=np.float64)

    if m.size == 0 or np.all(m <= 0.0):
        return KinematicParticipationIndex(
            k=None,
            status="NO_MASS",
            total_mass=0.0,
            max_disp=0.0,
            mean_disp=0.0,
            direction=direction,
        )

    # Determine scalar magnitudes a_i
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
        raise ValueError(f"Size mismatch: {m.size} mass points vs {a.size} displacement points")

    total_mass = float(np.sum(m))
    max_disp = float(np.max(a)) if a.size > 0 else 0.0

    if max_disp < motion_tolerance:
        return KinematicParticipationIndex(
            k=None,
            status="NO_MOTION",
            total_mass=total_mass,
            max_disp=max_disp,
            mean_disp=0.0,
            direction=direction,
        )

    # Weighted sums: S1 = Σ(m_i * a_i), S2 = Σ(m_i * a_i²)
    s1 = float(np.sum(m * a))
    s2 = float(np.sum(m * (a ** 2)))

    denominator = total_mass * s2
    if denominator <= 1.0e-30:
        return KinematicParticipationIndex(
            k=None,
            status="NO_MOTION",
            total_mass=total_mass,
            max_disp=max_disp,
            mean_disp=0.0,
            direction=direction,
        )

    k_val = (s1 * s1) / denominator
    # Clamp to [0, 1] to guard against floating-point roundoff exceeding 1.0
    k_clamped = min(1.0, max(0.0, k_val))

    mean_disp = s1 / total_mass
    variance = float(np.sum(m * ((a - mean_disp) ** 2)) / total_mass)

    return KinematicParticipationIndex(
        k=k_clamped,
        status="VALID",
        total_mass=total_mass,
        max_disp=max_disp,
        mean_disp=mean_disp,
        direction=direction,
        disp_variance=variance,
    )


# =============================================================================
# Macro-Element Geometry, Volume Mass Points, and Kinematics
# =============================================================================

def compute_quad_mass(quad: Quad, model: Model) -> float:
    """Compute physically consistent mass weight for a Quad macro-element.

    Uses material specific weight w and element volume:
        M = (w / g) * Volume
    If w <= 0 or missing, volume serves as the consistent geometric weight.
    """
    volume = float(quad.compute_volume())
    if volume <= 0.0:
        # Fallback to quadrilateral area * mean thickness
        l0, l1 = float(quad.length[0]), float(quad.length[1])
        mean_t = float(np.mean(quad.thickness)) if quad.thickness else 1.0
        volume = max(1.0, l0 * l1 * mean_t)

    material = None
    if model.collections and quad.material_key in model.collections.materials:
        material = model.collections.materials[quad.material_key]

    w = float(getattr(material, "w", 0.0)) if material is not None else 0.0
    if w > 0.0:
        return float((w / GRAVITY_ACCELERATION) * volume)
    return float(volume)


def sample_quad_displacements_and_masses(
    quad: Quad,
    model: Model,
    global_u: np.ndarray,
    *,
    kinematic_mode: str = "volume_8point",
) -> tuple[np.ndarray, np.ndarray]:
    """Sample the 3D displacement field and mass points of a Quad macro-element.

    Kinematic Modes:
    ----------------
    - "volume_8point": Evaluates 8 3D volume vertices (top and bottom surfaces at
      each corner node). Fully accounts for:
        1. Centroid rigid translations (ux, uy, uz)
        2. In-plane and out-of-plane rigid rotations (phi_x, phi_y, phi_z)
        3. Internal warping / diagonal shear distortion mode (gamma = u_6)
        4. Thickness variation across the element
    - "midsurface_4point": Evaluates 4 corner nodes on the element mid-surface.
      Accounts for translations, in-plane rotations, and warping distortion.
    - "centroid": Single point at the element centroid.

    Returns
    -------
    displacements : np.ndarray
        Array of shape (N_points, 3) representing 3D translations (ux, uy, uz).
    masses : np.ndarray
        1D array of shape (N_points,) representing mass weights for each point.
    """
    total_quad_mass = compute_quad_mass(quad, model)

    if kinematic_mode == "centroid":
        local_u = _quad_local_displacement(quad, global_u)
        disp = np.asarray([local_u[0], local_u[1], local_u[2]], dtype=np.float64).reshape(1, 3)
        masses = np.asarray([total_quad_mass], dtype=np.float64)
        return disp, masses

    # Mid-surface nodal translations including centroid translation, rotation, and warping
    assert model.collections is not None
    nodes = [model.collections.nodes[k].point for k in quad.node_keys]
    midsurface_disps = [
        quad_node_displacement(quad, node, idx, global_u)
        for idx, node in enumerate(nodes)
    ]

    if kinematic_mode == "midsurface_4point":
        masses = np.full(4, total_quad_mass / 4.0, dtype=np.float64)
        return np.asarray(midsurface_disps, dtype=np.float64), masses

    # Default "volume_8point": top (+t/2 * normal) and bottom (-t/2 * normal)
    local_u = _quad_local_displacement(quad, global_u)
    rotation = np.asarray(local_u[3:6], dtype=np.float32)  # (phi_x, phi_y, phi_z)

    disps_8: list[np.ndarray] = []
    for idx in range(4):
        u_mid = midsurface_disps[idx].astype(np.float32)
        n = np.asarray((quad.normal[idx].x, quad.normal[idx].y, quad.normal[idx].z), dtype=np.float32)
        t = float(quad.thickness[idx]) if idx < len(quad.thickness) else 1.0
        arm_top = (0.5 * t) * n
        arm_bot = (-0.5 * t) * n
        # Cross product phi_G x arm
        rot_disp_top = np.cross(rotation, arm_top)
        rot_disp_bot = np.cross(rotation, arm_bot)

        u_top = u_mid + rot_disp_top
        u_bot = u_mid + rot_disp_bot

        disps_8.append(u_top)
        disps_8.append(u_bot)

    masses_8 = np.full(8, total_quad_mass / 8.0, dtype=np.float64)
    return np.asarray(disps_8, dtype=np.float64), masses_8


# =============================================================================
# Bridge Component Classification
# =============================================================================

def classify_bridge_components(
    model: Model,
    custom_regions: Mapping[str, Sequence[int]] | None = None,
) -> BridgeClassification:
    """Classify model Quad elements into structural components.

    Recognizes:
    - backfill: Material name containing 'backfill', 'soil', 'riempimento', or custom override.
    - piers: Material name containing 'pier', 'pila', or quad name containing 'pier',
             or elements located at lower elevations below arch springing.
    - arch: Masonry vault elements along the bridge span (Layer 0 in bridge wizard models,
            or material name 'masonry' not in piers/backfill).
    - total_structure: All elements excluding backfill.
    """
    if custom_regions is not None:
        all_keys = tuple(sorted(model.collections.quads.keys())) if model.collections else ()
        total_struct = tuple(sorted(custom_regions.get("total_structure", ())))
        backfill = tuple(sorted(custom_regions.get("backfill", ())))
        arch = tuple(sorted(custom_regions.get("arch", ())))
        piers = tuple(sorted(custom_regions.get("piers", ())))
        other = tuple(sorted(set(all_keys) - set(total_struct) - set(backfill)))
        return BridgeClassification(
            total_structure_quad_keys=total_struct,
            backfill_quad_keys=backfill,
            arch_quad_keys=arch,
            pier_quad_keys=piers,
            other_quad_keys=other,
            all_quad_keys=all_keys,
        )

    if model.collections is None:
        return BridgeClassification((), (), (), (), (), ())

    materials = {k: v.name.lower() for k, v in model.collections.materials.items()}
    all_quads = list(model.collections.quads.values())

    backfill_keys: list[int] = []
    arch_keys: list[int] = []
    pier_keys: list[int] = []
    other_keys: list[int] = []

    # Identify elevation of arch springings if piers exist
    z_coords = [q.g.z for q in all_quads]
    min_z, max_z = (min(z_coords), max(z_coords)) if z_coords else (0.0, 0.0)

    for q in all_quads:
        mat_name = materials.get(q.material_key, "")
        q_name = str(q.name).lower()
        q_key = int(q.key)

        # 1. Backfill identification
        if any(term in mat_name for term in ("backfill", "soil", "riempimento", "sand")):
            backfill_keys.append(q_key)
            continue

        # 2. Pier identification
        if any(term in mat_name for term in ("pier", "pila")) or any(term in q_name for term in ("pier", "pila")):
            pier_keys.append(q_key)
            continue

        # Geometric check for piers: if bridge has subterranean or low-Z masonry below the main arch
        if q.g.z < 0.0 and (max_z - min_z) > 100.0 and q.layer_key != 0:
            pier_keys.append(q_key)
            continue

        # 3. Arch identification (Layer 0 in bridge wizard, or masonry along span)
        if q.layer_key == 0 or "masonry" in mat_name or "arch" in q_name or "vault" in q_name:
            arch_keys.append(q_key)
            continue

        other_keys.append(q_key)

    # Total structure = everything excluding backfill
    total_structure_keys = sorted(set(arch_keys) | set(pier_keys) | set(other_keys))

    return BridgeClassification(
        total_structure_quad_keys=tuple(total_structure_keys),
        backfill_quad_keys=tuple(sorted(backfill_keys)),
        arch_quad_keys=tuple(sorted(arch_keys)),
        pier_quad_keys=tuple(sorted(pier_keys)),
        other_quad_keys=tuple(sorted(other_keys)),
        all_quad_keys=tuple(sorted(q.key for q in all_quads)),
    )


# =============================================================================
# Relative / Internal Deformation Indicators
# =============================================================================

def compute_region_deformation_metrics(
    model: Model,
    quad_keys: Sequence[int],
    global_u: np.ndarray,
    point_displacements: np.ndarray,
) -> RegionDeformationMetrics:
    """Calculate internal shear strains, interface openings, and slips for a region."""
    if not quad_keys or point_displacements.size == 0 or model.collections is None:
        return RegionDeformationMetrics(
            max_disp=0.0,
            mean_disp=0.0,
            max_shear_strain=0.0,
            max_interface_opening=0.0,
            max_interface_sliding=0.0,
        )

    a = np.sqrt(np.sum(point_displacements ** 2, axis=1)) if point_displacements.ndim == 2 else np.abs(point_displacements)
    max_disp = float(np.max(a)) if a.size > 0 else 0.0
    mean_disp = float(np.mean(a)) if a.size > 0 else 0.0

    # 1. Macro-element internal diagonal shear distortion
    max_shear_strain = 0.0
    key_set = set(quad_keys)
    for key in quad_keys:
        quad = model.collections.quads.get(key)
        if quad is None:
            continue
        local_u = _quad_local_displacement(quad, global_u)
        dalfa = quad.d_alfa_2d_diag()
        shear_strain = abs(float(local_u[6] * dalfa)) if len(local_u) > 6 else 0.0
        if shear_strain > max_shear_strain:
            max_shear_strain = shear_strain

    # 2. Interface crack opening and sliding slip on interfaces connected to these quads
    max_opening = 0.0
    max_sliding = 0.0
    dissipated_energy = 0.0
    visited_interfaces: set[int] = set()

    for key in quad_keys:
        quad = model.collections.quads.get(key)
        if quad is None:
            continue
        for face_intf_keys in quad.interface_keys:
            for intf_key in face_intf_keys:
                if intf_key in visited_interfaces:
                    continue
                visited_interfaces.add(intf_key)
                intf = model.collections.interfaces.get(intf_key)
                if intf is None:
                    continue
                # Transverse crack opening (positive u = opening)
                for sp in intf.trasv_1:
                    u_val = float(getattr(sp, "u", 0.0))
                    if u_val > max_opening:
                        max_opening = u_val
                    dissipated_energy += float(getattr(sp, "cenergy_d", 0.0))
                # Sliding slip
                for sp in intf.slid:
                    u_slip = abs(float(getattr(sp, "u", 0.0)))
                    cup = abs(float(getattr(sp, "_cup", 0.0)))
                    slip = max(u_slip, cup)
                    if slip > max_sliding:
                        max_sliding = slip
                    dissipated_energy += float(getattr(sp, "cenergy_d", 0.0))
                for sp in intf.slid_out_plan:
                    u_slip = abs(float(getattr(sp, "u", 0.0)))
                    if u_slip > max_sliding:
                        max_sliding = u_slip
                    dissipated_energy += float(getattr(sp, "cenergy_d", 0.0))

    # Rigid-body heuristic: measurable overall displacement with negligible internal strain/opening
    is_rigid = bool(
        max_disp > 1.0e-3
        and max_shear_strain < 1.0e-5
        and max_opening < 1.0e-3
        and max_sliding < 1.0e-3
    )

    return RegionDeformationMetrics(
        max_disp=max_disp,
        mean_disp=mean_disp,
        max_shear_strain=max_shear_strain,
        max_interface_opening=max_opening,
        max_interface_sliding=max_sliding,
        dissipated_energy=dissipated_energy,
        is_predominantly_rigid=is_rigid,
    )


# =============================================================================
# High-Level Step and Execution Participation Evaluators
# =============================================================================

def evaluate_regional_participation(
    model: Model,
    displacement_vector: np.ndarray,
    classification: BridgeClassification,
    *,
    kinematic_mode: str = "volume_8point",
    motion_tolerance: float = 1.0e-9,
) -> RegionalParticipationSummary:
    """Evaluate kinematic participation and deformation across all components."""
    assert model.collections is not None

    # Pre-sample all elements
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
    d_global, m_global = gather(classification.all_quad_keys)

    # Compute K indices
    k_struct = compute_kinematic_participation(
        m_struct, d_struct, motion_tolerance=motion_tolerance, direction="all"
    )
    k_backfill = compute_kinematic_participation(
        m_backfill, d_backfill, motion_tolerance=motion_tolerance, direction="all"
    )
    k_arch = compute_kinematic_participation(
        m_arch, d_arch, motion_tolerance=motion_tolerance, direction="all"
    )
    k_piers = (
        compute_kinematic_participation(
            m_piers, d_piers, motion_tolerance=motion_tolerance, direction="all"
        )
        if classification.has_piers
        else KinematicParticipationIndex(None, "NOT_PRESENT", 0.0, 0.0, 0.0)
    )
    k_global = compute_kinematic_participation(
        m_global, d_global, motion_tolerance=motion_tolerance, direction="all"
    )

    # Directional participation on total structure (or global if structure is empty)
    d_target, m_target = (d_struct, m_struct) if m_struct.size > 0 else (d_global, m_global)
    k_x = compute_kinematic_participation(
        m_target, d_target, motion_tolerance=motion_tolerance, direction="x"
    )
    k_y = compute_kinematic_participation(
        m_target, d_target, motion_tolerance=motion_tolerance, direction="y"
    )
    k_z = compute_kinematic_participation(
        m_target, d_target, motion_tolerance=motion_tolerance, direction="z"
    )

    # Deformation metrics
    def_struct = compute_region_deformation_metrics(
        model, classification.total_structure_quad_keys, displacement_vector, d_struct
    )
    def_backfill = compute_region_deformation_metrics(
        model, classification.backfill_quad_keys, displacement_vector, d_backfill
    )
    def_arch = compute_region_deformation_metrics(
        model, classification.arch_quad_keys, displacement_vector, d_arch
    )
    def_piers = compute_region_deformation_metrics(
        model, classification.pier_quad_keys, displacement_vector, d_piers
    )

    # Displacement ratios
    b_to_s = float(def_backfill.max_disp / max(def_struct.max_disp, 1.0e-30))
    b_to_a = float(def_backfill.max_disp / max(def_arch.max_disp, 1.0e-30))

    return RegionalParticipationSummary(
        k_total_structure=k_struct,
        k_backfill=k_backfill,
        k_arch=k_arch,
        k_piers=k_piers,
        k_global=k_global,
        k_x=k_x,
        k_y=k_y,
        k_z=k_z,
        deformation_total_structure=def_struct,
        deformation_backfill=def_backfill,
        deformation_arch=def_arch,
        deformation_piers=def_piers,
        backfill_to_structure_disp_ratio=b_to_s,
        backfill_to_arch_disp_ratio=b_to_a,
    )


def evaluate_step_participation(
    model: Model,
    current_step: AnalysisStep | Mapping[str, Any] | np.ndarray,
    previous_step: AnalysisStep | Mapping[str, Any] | np.ndarray | None = None,
    initial_step: AnalysisStep | Mapping[str, Any] | np.ndarray | None = None,
    *,
    classification: BridgeClassification | None = None,
    kinematic_mode: str = "volume_8point",
    motion_tolerance: float = 1.0e-9,
) -> StepParticipationReport:
    """Evaluate kinematic participation for one committed analysis step.

    Distinguishes:
    - incremental: participation in the step increment Δu = u_current - u_previous
    - cumulative: participation in total displacement u_current - u_initial
    """
    if classification is None:
        classification = classify_bridge_components(model)

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

    # Evaluate summaries
    incremental_summary = evaluate_regional_participation(
        model, delta_u, classification, kinematic_mode=kinematic_mode, motion_tolerance=motion_tolerance
    )
    cumulative_summary = evaluate_regional_participation(
        model, cumul_u, classification, kinematic_mode=kinematic_mode, motion_tolerance=motion_tolerance
    )

    # Synthesize engineering interpretation notes
    notes: list[str] = []
    step_num = int(current_step.get("step", 0)) if isinstance(current_step, Mapping) else 0
    lf = float(current_step.get("load_factor", 0.0)) if isinstance(current_step, Mapping) else 0.0
    mon_disp = float(current_step.get("displacement", 0.0)) if isinstance(current_step, Mapping) else 0.0

    # Incremental mechanism insights
    k_struct = incremental_summary.k_total_structure
    k_back = incremental_summary.k_backfill
    if k_struct.is_valid:
        if k_struct.k_or_zero >= 0.60:
            notes.append(
                f"Step {step_num}: Broad spatial motion across structural components "
                f"(K_total_structure={k_struct.k:.3f})."
            )
        elif k_struct.k_or_zero < 0.25:
            notes.append(
                f"Step {step_num}: Concentrated/localized kinematic activity in structure "
                f"(K_total_structure={k_struct.k:.3f}, max={k_struct.max_disp:.3e})."
            )

    if k_back.is_valid and incremental_summary.backfill_to_structure_disp_ratio > 3.0:
        notes.append(
            f"Step {step_num}: Localized backfill movement dominates structural motion "
            f"(backfill/structure displacement ratio={incremental_summary.backfill_to_structure_disp_ratio:.1f})."
        )

    if incremental_summary.deformation_total_structure.is_predominantly_rigid:
        notes.append(
            f"Step {step_num}: Structure motion is predominantly rigid-body displacement; "
            "internal relative strains and interface openings remain negligible."
        )

    return StepParticipationReport(
        step=step_num,
        load_factor=lf,
        monitored_displacement=mon_disp,
        incremental=incremental_summary,
        cumulative=cumulative_summary,
        interpretation_notes=tuple(notes),
    )


def evaluate_execution_participation(
    model: Model,
    execution: AnalysisExecution,
    *,
    classification: BridgeClassification | None = None,
    kinematic_mode: str = "volume_8point",
    motion_tolerance: float = 1.0e-9,
) -> ExecutionParticipationReport:
    """Evaluate kinematic participation across all committed steps of an analysis execution."""
    if classification is None:
        classification = classify_bridge_components(model)

    committed = execution.committed_steps
    if not committed:
        return ExecutionParticipationReport(
            analysis_key=execution.analysis_key,
            analysis_name=execution.analysis_name,
            steps=(),
            summary={"committed_steps": 0, "status": "NO_COMMITTED_STEPS"},
        )

    initial_step = execution.initial_step
    step_reports: list[StepParticipationReport] = []

    prev_step = initial_step
    for step in committed:
        report = evaluate_step_participation(
            model,
            step,
            previous_step=prev_step,
            initial_step=initial_step,
            classification=classification,
            kinematic_mode=kinematic_mode,
            motion_tolerance=motion_tolerance,
        )
        step_reports.append(report)
        prev_step = step

    # Compile executive summary
    terminal = step_reports[-1]
    peak_k_struct = max((s.incremental.k_total_structure.k_or_zero for s in step_reports), default=0.0)
    terminal_k_struct = terminal.incremental.k_total_structure.k_or_zero
    terminal_k_back = terminal.incremental.k_backfill.k_or_zero
    peak_backfill_ratio = max((s.incremental.backfill_to_structure_disp_ratio for s in step_reports), default=0.0)

    summary = {
        "analysis_key": execution.analysis_key,
        "analysis_name": execution.analysis_name,
        "outcome": str(execution.outcome.value if execution.outcome else "unknown"),
        "committed_step_count": len(step_reports),
        "peak_k_total_structure_incremental": peak_k_struct,
        "terminal_k_total_structure_incremental": terminal_k_struct,
        "terminal_k_backfill_incremental": terminal_k_back,
        "terminal_k_total_structure_cumulative": terminal.cumulative.k_total_structure.k_or_zero,
        "terminal_k_backfill_cumulative": terminal.cumulative.k_backfill.k_or_zero,
        "peak_backfill_to_structure_disp_ratio": peak_backfill_ratio,
        "terminal_backfill_to_structure_disp_ratio": terminal.incremental.backfill_to_structure_disp_ratio,
        "terminal_is_rigid_motion": terminal.incremental.deformation_total_structure.is_predominantly_rigid,
    }

    return ExecutionParticipationReport(
        analysis_key=execution.analysis_key,
        analysis_name=execution.analysis_name,
        steps=tuple(step_reports),
        summary=summary,
    )
