"""Configuration and usability options for collapse screening and mechanism diagnostics.

This module implements Task 12:
- Non-breaking configuration schema for automated collapse screening.
- Enable/disable collapse screening toggle.
- Configurable active-displacement tolerances.
- Configurable significant-load-drop thresholds.
- Configurable component & material mappings between existing model identifiers
  (material keys, material names, quad IDs, layers, groups) and structural categories:
  arch, pier, backfill, abutment, and other.
- Explicit visibility into unmapped, ambiguous, and missing component mappings.
- Reusable mapping definitions across thousands of batch simulations.
- Selection of detailed incremental histories vs fast single-state screening.
- Enable/disable toggle for expensive interface and energy dissipation calculations.
- Master execution entry point: screen_analysis_collapse().
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import fnmatch
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from histra.collapse.active_mass import ActiveMassCriteria
from histra.collapse.classifier import (
    ClassifierThresholds,
    CollapseCategory,
    ExecutionClassificationReport,
    ReviewPriority,
    classify_execution,
)
from histra.collapse.evolution import (
    MechanismEvolutionHistory,
    track_mechanism_evolution,
)
from histra.collapse.interface_damage import (
    InterfaceCriteria,
    classify_bridge_interfaces,
)
from histra.collapse.load_drop import (
    LoadDropAnalysisReport,
    LoadDropCriteria,
    evaluate_load_drop_analysis,
)
from histra.collapse.participation import (
    BridgeClassification,
    classify_bridge_components,
)
from histra.model.model import Model
from histra.solver.outcomes import AnalysisExecution


# Valid standard structural categories
VALID_CATEGORIES = ("arch", "pier", "backfill", "abutment", "other")


# =============================================================================
# Component & Material Mapping Configuration
# =============================================================================

@dataclass(frozen=True)
class ComponentMappingConfig:
    """Reusable mapping from existing model identifiers to bridge component categories.

    Categories:
    -----------
    - 'arch': Masonry vault and barrel elements.
    - 'pier': Vertical support piers and pilasters.
    - 'backfill': Soil, granular fill, and roadbed material above the vault.
    - 'abutment': Massive end masonry abutments and springings.
    - 'other': Wing walls, parapets, spandrel masonry, or unclassified elements.
    """

    material_keys: dict[str, tuple[int, ...]] = field(default_factory=dict)
    """Map category to sequence of integer material keys, e.g. {'arch': (1, 2), 'backfill': (3,)}."""

    material_names: dict[str, tuple[str, ...]] = field(default_factory=dict)
    """Map category to string patterns (case-insensitive glob), e.g. {'backfill': ('*soil*', '*fill*')}."""

    quad_keys: dict[str, tuple[int, ...]] = field(default_factory=dict)
    """Map category to explicit quad element IDs, e.g. {'arch': (100, 101, 102)}."""

    layer_keys: dict[str, tuple[int, ...]] = field(default_factory=dict)
    """Map category to Layer integer keys, e.g. {'arch': (0,), 'backfill': (1,)}."""

    group_names: dict[str, tuple[str, ...]] = field(default_factory=dict)
    """Map category to group name patterns, e.g. {'pier': ('*Pier*',)}."""

    arch_spans: dict[str, tuple[int, ...]] = field(default_factory=dict)
    """Explicit quad allocation per span, e.g. {'span_1': (100, 101), 'span_2': (102, 103)}."""

    backfill_spans: dict[str, tuple[int, ...]] = field(default_factory=dict)
    """Explicit backfill quad allocation per span."""

    fallback_to_heuristics: bool = True
    """If True, elements not covered by mapping fall back to model name & elevation heuristics."""

    strict: bool = False
    """If True, any unmapped or ambiguous element raises a ValueError."""

    def to_dict(self) -> dict[str, Any]:
        return {
            "material_keys": {k: list(v) for k, v in self.material_keys.items()},
            "material_names": {k: list(v) for k, v in self.material_names.items()},
            "quad_keys": {k: list(v) for k, v in self.quad_keys.items()},
            "layer_keys": {k: list(v) for k, v in self.layer_keys.items()},
            "group_names": {k: list(v) for k, v in self.group_names.items()},
            "arch_spans": {k: list(v) for k, v in self.arch_spans.items()},
            "backfill_spans": {k: list(v) for k, v in self.backfill_spans.items()},
            "fallback_to_heuristics": self.fallback_to_heuristics,
            "strict": self.strict,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> ComponentMappingConfig:
        def _to_int_tuple_dict(d: Mapping[str, Any]) -> dict[str, tuple[int, ...]]:
            return {str(k): tuple(int(x) for x in v) for k, v in d.items()}

        def _to_str_tuple_dict(d: Mapping[str, Any]) -> dict[str, tuple[str, ...]]:
            return {str(k): tuple(str(x) for x in v) for k, v in d.items()}

        return cls(
            material_keys=_to_int_tuple_dict(data.get("material_keys", {})),
            material_names=_to_str_tuple_dict(data.get("material_names", {})),
            quad_keys=_to_int_tuple_dict(data.get("quad_keys", {})),
            layer_keys=_to_int_tuple_dict(data.get("layer_keys", {})),
            group_names=_to_str_tuple_dict(data.get("group_names", {})),
            arch_spans=_to_int_tuple_dict(data.get("arch_spans", {})),
            backfill_spans=_to_int_tuple_dict(data.get("backfill_spans", {})),
            fallback_to_heuristics=bool(data.get("fallback_to_heuristics", True)),
            strict=bool(data.get("strict", False)),
        )

    def to_json(self, path_or_file: str | Path) -> None:
        """Serialize configuration to a JSON file."""
        path = Path(path_or_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def from_json(cls, path_or_str: str | Path) -> ComponentMappingConfig:
        """Load configuration from a JSON file or JSON string."""
        path = Path(path_or_str)
        if path.exists() and path.is_file():
            text = path.read_text(encoding="utf-8")
        else:
            text = str(path_or_str)
        data = json.loads(text)
        return cls.from_dict(data)


# =============================================================================
# Component Mapping Resolution Algorithm
# =============================================================================

def resolve_component_mapping(
    model: Model,
    mapping_config: ComponentMappingConfig | None = None,
) -> BridgeClassification:
    """Map model Quad macro-elements to structural categories with diagnostics.

    Evaluates explicit mappings, validates ties, identifies unmapped elements,
    and returns a fully diagnosed BridgeClassification.
    """
    if mapping_config is None:
        mapping_config = ComponentMappingConfig()

    if model.collections is None:
        return BridgeClassification((), (), (), (), (), ())

    all_quads = list(model.collections.quads.values())
    all_keys = tuple(sorted(q.key for q in all_quads))
    materials = {k: v.name.lower() for k, v in model.collections.materials.items()}

    # Category buckets
    arch_keys: set[int] = set()
    pier_keys: set[int] = set()
    backfill_keys: set[int] = set()
    abutment_keys: set[int] = set()
    other_keys: set[int] = set()

    ambiguous: dict[int, list[str]] = {}
    mapping_warnings: list[str] = []

    # Build reverse lookup for explicit quad_keys
    quad_key_to_cat: dict[int, list[str]] = {}
    for cat, qkeys in mapping_config.quad_keys.items():
        cat_lower = cat.lower()
        for qk in qkeys:
            quad_key_to_cat.setdefault(int(qk), []).append(cat_lower)

    # Build lookup for material_keys
    mat_key_to_cat: dict[int, list[str]] = {}
    for cat, mkeys in mapping_config.material_keys.items():
        cat_lower = cat.lower()
        for mk in mkeys:
            mat_key_to_cat.setdefault(int(mk), []).append(cat_lower)

    # Build lookup for layer_keys
    layer_to_cat: dict[int, list[str]] = {}
    for cat, lkeys in mapping_config.layer_keys.items():
        cat_lower = cat.lower()
        for lk in lkeys:
            layer_to_cat.setdefault(int(lk), []).append(cat_lower)

    # Track matched materials
    matched_material_keys: set[int] = set()

    # Precedence order when resolving ties: arch > pier > abutment > backfill > other
    precedence = {"arch": 0, "pier": 1, "abutment": 2, "backfill": 3, "other": 4}

    for q in all_quads:
        qk = int(q.key)
        mk = int(q.material_key)
        mat_name = materials.get(mk, "")
        q_name = str(q.name).lower()
        layer_k = int(getattr(q, "layer_key", -1))

        matched_cats: list[str] = []

        # 1. Check explicit quad keys
        if qk in quad_key_to_cat:
            matched_cats.extend(quad_key_to_cat[qk])

        # 2. Check layer keys
        if layer_k in layer_to_cat:
            matched_cats.extend(layer_to_cat[layer_k])

        # 3. Check explicit material keys
        if mk in mat_key_to_cat:
            matched_cats.extend(mat_key_to_cat[mk])
            matched_material_keys.add(mk)

        # 4. Check material name patterns
        for cat, patterns in mapping_config.material_names.items():
            cat_lower = cat.lower()
            for pat in patterns:
                if fnmatch.fnmatch(mat_name, pat.lower()):
                    matched_cats.append(cat_lower)
                    matched_material_keys.add(mk)
                    break

        # 5. Check group name patterns
        for cat, patterns in mapping_config.group_names.items():
            cat_lower = cat.lower()
            for pat in patterns:
                if fnmatch.fnmatch(q_name, pat.lower()):
                    matched_cats.append(cat_lower)
                    break

        # Deduplicate matched categories
        unique_matches = list(dict.fromkeys(matched_cats))

        if len(unique_matches) > 1:
            ambiguous[qk] = unique_matches
            mapping_warnings.append(
                f"Quad {qk} (material '{mat_name}') matched conflicting categories: {unique_matches}. "
                f"Resolved using precedence."
            )
            # Pick by precedence
            chosen_cat = min(unique_matches, key=lambda c: precedence.get(c, 99))
        elif len(unique_matches) == 1:
            chosen_cat = unique_matches[0]
        else:
            chosen_cat = None

        # Fallback to heuristics if unmapped
        if chosen_cat is None and mapping_config.fallback_to_heuristics:
            if any(t in mat_name for t in ("backfill", "soil", "riempimento", "sand")):
                chosen_cat = "backfill"
            elif any(t in mat_name for t in ("pier", "pila")) or any(t in q_name for t in ("pier", "pila")):
                chosen_cat = "pier"
            elif any(t in mat_name for t in ("abutment", "spalla")) or any(t in q_name for t in ("abutment", "spalla")):
                chosen_cat = "abutment"
            elif layer_k == 0 or "masonry" in mat_name or "arch" in q_name or "vault" in q_name:
                chosen_cat = "arch"
            else:
                chosen_cat = "other"

        # Bucket assignment
        if chosen_cat == "arch":
            arch_keys.add(qk)
        elif chosen_cat == "pier":
            pier_keys.add(qk)
        elif chosen_cat == "backfill":
            backfill_keys.add(qk)
        elif chosen_cat == "abutment":
            abutment_keys.add(qk)
        else:
            other_keys.add(qk)

    # Identify unmapped elements
    unmapped_quads: list[int] = sorted(other_keys) if not mapping_config.fallback_to_heuristics else []
    all_mat_keys = set(model.collections.materials.keys())
    unmapped_materials: list[int] = sorted(all_mat_keys - matched_material_keys)

    if unmapped_quads:
        mapping_warnings.append(
            f"{len(unmapped_quads)} Quad elements could not be mapped to arch, pier, backfill, or abutment "
            f"and were assigned to 'other'."
        )

    if mapping_config.strict and (unmapped_quads or ambiguous):
        raise ValueError(
            f"Strict component mapping failed: {len(unmapped_quads)} unmapped quads, "
            f"{len(ambiguous)} ambiguous assignments. Warnings: {mapping_warnings}"
        )

    # Multi-span allocation
    arch_spans = {str(k): tuple(sorted(v)) for k, v in mapping_config.arch_spans.items()}
    backfill_spans = {str(k): tuple(sorted(v)) for k, v in mapping_config.backfill_spans.items()}

    # If spans were not explicitly supplied, run topological clustering
    if not arch_spans and arch_keys:
        arch_spans = _cluster_arch_spans(model, arch_keys)
    if not backfill_spans and backfill_keys:
        backfill_spans = _allocate_backfill_to_spans(model, backfill_keys, arch_spans)

    # Total structure = arch + pier + abutment + other (everything excluding backfill)
    total_structure = tuple(sorted(arch_keys | pier_keys | abutment_keys | other_keys))

    return BridgeClassification(
        total_structure_quad_keys=total_structure,
        backfill_quad_keys=tuple(sorted(backfill_keys)),
        arch_quad_keys=tuple(sorted(arch_keys)),
        pier_quad_keys=tuple(sorted(pier_keys)),
        other_quad_keys=tuple(sorted(other_keys)),
        all_quad_keys=all_keys,
        arch_spans=arch_spans,
        backfill_spans=backfill_spans,
        abutment_quad_keys=tuple(sorted(abutment_keys)),
        unmapped_quad_keys=tuple(unmapped_quads),
        unmapped_material_keys=tuple(unmapped_materials),
        ambiguous_quad_keys={k: tuple(v) for k, v in ambiguous.items()},
        mapping_warnings=tuple(mapping_warnings),
    )


def _cluster_arch_spans(model: Model, arch_keys: set[int]) -> dict[str, tuple[int, ...]]:
    """Cluster arch quads into distinct bridge spans using interface connectivity."""
    adj: dict[int, set[int]] = {k: set() for k in arch_keys}
    arch_quads = [model.collections.quads[k] for k in arch_keys]

    for q in arch_quads:
        for face_keys in q.interface_keys:
            for ikey in face_keys:
                intf = model.collections.interfaces.get(ikey)
                if intf:
                    p1, p2 = intf.parent_element_key1, intf.parent_element_key2
                    other = p2 if p1 == q.key else p1
                    if other in adj:
                        adj[q.key].add(other)

    visited: set[int] = set()
    components: list[list[int]] = []
    for k in sorted(arch_keys):
        if k not in visited:
            comp: list[int] = []
            st = [k]
            visited.add(k)
            while st:
                curr = st.pop()
                comp.append(curr)
                for nb in adj[curr]:
                    if nb not in visited:
                        visited.add(nb)
                        st.append(nb)
            components.append(comp)

    # Sort spans by longitudinal centroid coordinate (X)
    def _mean_x(qkeys: list[int]) -> float:
        return float(np.mean([model.collections.quads[k].g.x for k in qkeys]))

    components.sort(key=_mean_x)
    return {f"span_{idx+1}": tuple(sorted(c)) for idx, c in enumerate(components)}


def _allocate_backfill_to_spans(
    model: Model,
    backfill_keys: set[int],
    arch_spans: dict[str, tuple[int, ...]],
) -> dict[str, tuple[int, ...]]:
    """Partition backfill quads by span according to longitudinal proximity."""
    if not arch_spans:
        return {"span_1": tuple(sorted(backfill_keys))} if backfill_keys else {}

    span_x_bounds: dict[str, tuple[float, float]] = {}
    for sname, qkeys in arch_spans.items():
        xs = [model.collections.quads[k].g.x for k in qkeys]
        span_x_bounds[sname] = (min(xs), max(xs))

    bf_spans: dict[str, list[int]] = {s: [] for s in arch_spans}
    for bk in backfill_keys:
        bx = model.collections.quads[bk].g.x
        assigned = False
        for sname, (xmin, xmax) in span_x_bounds.items():
            if xmin <= bx <= xmax:
                bf_spans[sname].append(bk)
                assigned = True
                break
        if not assigned:
            # Nearest span centroid
            nearest_span = min(
                span_x_bounds.keys(),
                key=lambda s: abs(bx - 0.5 * (span_x_bounds[s][0] + span_x_bounds[s][1])),
            )
            bf_spans[nearest_span].append(bk)

    return {s: tuple(sorted(keys)) for s, keys in bf_spans.items() if keys}


# =============================================================================
# Master Collapse Configuration
# =============================================================================

@dataclass(frozen=True)
class CollapseConfig:
    """Master configuration for automated push-down collapse mechanism screening."""

    enabled: bool = True
    """Master toggle to enable or disable collapse screening."""

    # 1. Active-displacement tolerances (Feature 2)
    relative_active_tolerance: float = 0.10
    """Fraction of peak displacement (theta_rel) to define an active point (default 10%)."""

    min_absolute_displacement: float = 1.0e-4
    """Minimum displacement threshold (cm) to filter out numerical precision noise."""

    motion_tolerance: float = 1.0e-9
    """Displacement cutoff below which motion is treated as NO_MOTION for K index."""

    kinematic_mode: str = "volume_8point"
    """Displacement sampling mode: 'volume_8point', 'midsurface_4point', or 'centroid'."""

    # 2. Significant load-drop thresholds (Feature 5)
    load_drop_trigger: float = 0.05
    """Fractional drop from peak (5%) to flag a capacity-loss event."""

    significant_load_drop: float = 0.15
    """Fractional drop (15%) signifying a major or severe collapse event."""

    sharp_step_limit: int = 3
    """Maximum number of increments for a capacity reduction to be deemed rapid/sharp."""

    min_absolute_resistance: float = 1.0e-4
    """Noise cutoff below which load or reaction is treated as zero."""

    resistance_metric: str = "auto"
    """'auto' chooses reaction for displacement control, load factor for load control / arc length."""

    # 3. Structural & interface thresholds (Feature 3 & 4)
    arch_hinge_mechanism_count: int = 3
    """Minimum arch hinges required for a complete flexural collapse mechanism."""

    arch_hinge_opening_tolerance: float = 0.02
    """Crack opening threshold (cm = 0.2 mm) for flexural hinge candidacy."""

    arch_hinge_rotation_tolerance: float = 1.0e-3
    """Relative rotation threshold across hinge joint (rad = 1 mrad)."""

    backfill_sliding_fraction_threshold: float = 0.20
    """Fraction of backfill contact area sliding to indicate backfill mobilization."""

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

    # 4. Performance & computational expense controls
    compute_interface_kinematics: bool = True
    """Enable or disable interface crack opening and relative sliding evaluations."""

    compute_energy_dissipation: bool = False
    """Enable or disable more expensive hysteretic energy dissipation calculations."""

    export_incremental_history: bool = True
    """Select whether detailed incremental histories (EvolutionStepRecord) are exported."""

    export_csv_path: str | None = None
    """Optional file path to auto-export step evolution history as CSV."""

    # 5. Reusable component mapping
    mapping: ComponentMappingConfig = field(default_factory=ComponentMappingConfig)
    """Configurable mapping from existing model identifiers to component categories."""

    def to_thresholds(self) -> ClassifierThresholds:
        return ClassifierThresholds(
            load_drop_trigger=self.load_drop_trigger,
            significant_load_drop=self.significant_load_drop,
            arch_hinge_mechanism_count=self.arch_hinge_mechanism_count,
            arch_hinge_opening_tolerance=self.arch_hinge_opening_tolerance,
            arch_hinge_rotation_tolerance=self.arch_hinge_rotation_tolerance,
            backfill_sliding_fraction_threshold=self.backfill_sliding_fraction_threshold,
            backfill_disp_dominance_ratio=self.backfill_disp_dominance_ratio,
            backfill_dissipation_dominance_ratio=self.backfill_dissipation_dominance_ratio,
            masonry_active_mass_low=self.masonry_active_mass_low,
            masonry_active_mass_high=self.masonry_active_mass_high,
            single_span_dominance_ratio=self.single_span_dominance_ratio,
            rigid_body_strain_cutoff=self.rigid_body_strain_cutoff,
        )

    def to_drop_criteria(self) -> LoadDropCriteria:
        return LoadDropCriteria(
            drop_threshold=self.load_drop_trigger,
            sharp_drop_threshold=self.significant_load_drop,
            sharp_step_limit=self.sharp_step_limit,
            min_absolute_resistance=self.min_absolute_resistance,
            resistance_metric=self.resistance_metric,
        )

    def to_active_criteria(self) -> ActiveMassCriteria:
        return ActiveMassCriteria(
            relative_threshold=self.relative_active_tolerance,
            absolute_threshold=self.min_absolute_displacement,
        )

    def to_interface_criteria(self) -> InterfaceCriteria:
        return InterfaceCriteria(
            hinge_opening_tolerance=self.arch_hinge_opening_tolerance,
            hinge_rotation_tolerance=self.arch_hinge_rotation_tolerance,
        )

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["mapping"] = self.mapping.to_dict()
        return d

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> CollapseConfig:
        d = dict(data)
        mapping_data = d.pop("mapping", None)
        mapping = (
            ComponentMappingConfig.from_dict(mapping_data)
            if isinstance(mapping_data, Mapping)
            else ComponentMappingConfig()
        )
        return cls(mapping=mapping, **d)

    def to_json(self, path_or_file: str | Path) -> None:
        path = Path(path_or_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def from_json(cls, path_or_str: str | Path) -> CollapseConfig:
        path = Path(path_or_str)
        if path.exists() and path.is_file():
            text = path.read_text(encoding="utf-8")
        else:
            text = str(path_or_str)
        return cls.from_dict(json.loads(text))

    @classmethod
    def fast_screening(cls, **kwargs: Any) -> CollapseConfig:
        """Fast configuration for screening thousands of simulations."""
        return cls(
            compute_energy_dissipation=False,
            export_incremental_history=False,
            **kwargs,
        )

    @classmethod
    def detailed_audit(cls, **kwargs: Any) -> CollapseConfig:
        """In-depth diagnostic configuration with full histories and energy audits."""
        return cls(
            compute_energy_dissipation=True,
            export_incremental_history=True,
            **kwargs,
        )

    @classmethod
    def disabled(cls) -> CollapseConfig:
        """Disabled configuration that skips screening with zero overhead."""
        return cls(enabled=False)


# =============================================================================
# Comprehensive Collapse Screening Report
# =============================================================================

@dataclass(frozen=True)
class CollapseScreeningReport:
    """Master engineering report of automated collapse screening for an analysis."""

    analysis_key: int
    analysis_name: str
    status: str
    is_screened: bool
    category: CollapseCategory
    confidence_score: float
    review_priority: ReviewPriority
    primary_diagnosis: str
    has_significant_load_drop: bool
    has_local_to_global_transition: bool
    peak_resistance: float
    displacement_at_peak: float
    terminal_resistance: float
    terminal_displacement: float
    mapping_diagnostics: dict[str, Any]
    classification_report: ExecutionClassificationReport | None = None
    load_drop_report: LoadDropAnalysisReport | None = None
    evolution_history: MechanismEvolutionHistory | None = None
    summary_row: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "analysis_key": self.analysis_key,
            "analysis_name": self.analysis_name,
            "status": self.status,
            "is_screened": self.is_screened,
            "category": self.category.value,
            "confidence_score": self.confidence_score,
            "review_priority": self.review_priority.value,
            "primary_diagnosis": self.primary_diagnosis,
            "has_significant_load_drop": self.has_significant_load_drop,
            "has_local_to_global_transition": self.has_local_to_global_transition,
            "peak_resistance": self.peak_resistance,
            "displacement_at_peak": self.displacement_at_peak,
            "terminal_resistance": self.terminal_resistance,
            "terminal_displacement": self.terminal_displacement,
            "mapping_diagnostics": self.mapping_diagnostics,
            "summary_row": self.summary_row,
            "classification_report": (
                self.classification_report.to_dict() if self.classification_report else None
            ),
            "load_drop_report": (
                self.load_drop_report.to_dict() if self.load_drop_report else None
            ),
            "evolution_history": (
                self.evolution_history.to_dict() if self.evolution_history else None
            ),
        }


# =============================================================================
# High-Level Automated Screening Function
# =============================================================================

def screen_analysis_collapse(
    model: Model,
    execution: AnalysisExecution,
    config: CollapseConfig | None = None,
) -> CollapseScreeningReport:
    """Screen an executed push-down analysis for collapse mechanism and load drops.

    This is the primary high-level entry point for batch simulation pipelines.
    """
    if config is None:
        config = CollapseConfig()

    if not config.enabled:
        return CollapseScreeningReport(
            analysis_key=execution.analysis_key,
            analysis_name=execution.analysis_name,
            status="DISABLED",
            is_screened=False,
            category=CollapseCategory.NUMERICAL_OR_UNCERTAIN,
            confidence_score=0.0,
            review_priority=ReviewPriority.LOW,
            primary_diagnosis="Collapse screening disabled by user configuration.",
            has_significant_load_drop=False,
            has_local_to_global_transition=False,
            peak_resistance=0.0,
            displacement_at_peak=0.0,
            terminal_resistance=0.0,
            terminal_displacement=0.0,
            mapping_diagnostics={"status": "SKIPPED"},
            summary_row={
                "analysis_key": execution.analysis_key,
                "analysis_name": execution.analysis_name,
                "status": "DISABLED",
            },
        )

    # 1. Resolve component and material mapping
    classification = resolve_component_mapping(model, config.mapping)
    intf_classification = classify_bridge_interfaces(model, classification)

    mapping_diag = {
        "total_quads": len(classification.all_quad_keys),
        "arch_quads": len(classification.arch_quad_keys),
        "pier_quads": len(classification.pier_quad_keys),
        "backfill_quads": len(classification.backfill_quad_keys),
        "abutment_quads": len(classification.abutment_quad_keys),
        "other_quads": len(classification.other_quad_keys),
        "unmapped_quads_count": len(classification.unmapped_quad_keys),
        "unmapped_quad_keys": list(classification.unmapped_quad_keys),
        "ambiguous_quads_count": len(classification.ambiguous_quad_keys),
        "ambiguous_quad_keys": {str(k): list(v) for k, v in classification.ambiguous_quad_keys.items()},
        "unmapped_materials_count": len(classification.unmapped_material_keys),
        "unmapped_material_keys": list(classification.unmapped_material_keys),
        "warnings": list(classification.mapping_warnings),
    }

    thresholds = config.to_thresholds()
    drop_crit = config.to_drop_criteria()

    # 2. Evaluate load drop response
    load_drop_rep = evaluate_load_drop_analysis(
        model,
        execution,
        criteria=drop_crit,
        thresholds=thresholds,
        classification=classification,
        intf_classification=intf_classification,
    )

    # 3. Classify execution
    class_rep = classify_execution(
        model,
        execution,
        classification=classification,
        intf_classification=intf_classification,
        thresholds=thresholds,
    )

    # 4. Incremental evolution history (if enabled)
    evol_hist: MechanismEvolutionHistory | None = None
    has_loc_to_glob = False
    if config.export_incremental_history:
        evol_hist = track_mechanism_evolution(
            model,
            execution,
            thresholds=thresholds,
            drop_criteria=drop_crit,
            active_criteria=config.to_active_criteria(),
            intf_criteria=config.to_interface_criteria(),
            classification=classification,
            intf_classification=intf_classification,
        )
        has_loc_to_glob = evol_hist.has_local_to_global_transition
        if config.export_csv_path:
            evol_hist.export_csv(config.export_csv_path)

    # Primary diagnosis text
    if load_drop_rep.has_significant_drop and load_drop_rep.primary_event:
        diag = load_drop_rep.primary_event.diagnosis
    else:
        diag = class_rep.result.primary_mechanism_description

    ev = class_rep.result.evidence
    summary_row = {
        "analysis_key": execution.analysis_key,
        "analysis_name": execution.analysis_name,
        "status": "COMPLETED" if execution.completed else "NONCONVERGED",
        "category": class_rep.result.category.value,
        "confidence": class_rep.result.confidence_score,
        "priority": class_rep.result.review_priority.value,
        "peak_resistance": load_drop_rep.curve.peak_load,
        "displacement_at_peak": load_drop_rep.curve.displacement_at_peak_load,
        "terminal_resistance": load_drop_rep.curve.terminal_load,
        "terminal_displacement": load_drop_rep.curve.terminal_displacement,
        "has_significant_load_drop": load_drop_rep.has_significant_drop,
        "has_local_to_global_transition": has_loc_to_glob,
        "k_structure": ev.k_total_structure,
        "k_backfill": ev.k_backfill,
        "m_active_structure": ev.active_mass_structure,
        "m_active_backfill": ev.active_mass_backfill,
        "arch_hinges": ev.arch_hinge_count,
        "max_arch_opening": ev.max_arch_opening,
        "max_arch_rotation": ev.max_arch_rotation,
        "backfill_sliding_fraction": ev.backfill_sliding_area_fraction,
        "unmapped_quads_count": len(classification.unmapped_quad_keys),
        "ambiguous_quads_count": len(classification.ambiguous_quad_keys),
        "warnings_count": len(classification.mapping_warnings),
        "diagnosis": diag,
    }

    return CollapseScreeningReport(
        analysis_key=execution.analysis_key,
        analysis_name=execution.analysis_name,
        status="COMPLETED" if execution.completed else "NONCONVERGED",
        is_screened=True,
        category=class_rep.result.category,
        confidence_score=class_rep.result.confidence_score,
        review_priority=class_rep.result.review_priority,
        primary_diagnosis=diag,
        has_significant_load_drop=load_drop_rep.has_significant_drop,
        has_local_to_global_transition=has_loc_to_glob,
        peak_resistance=load_drop_rep.curve.peak_load,
        displacement_at_peak=load_drop_rep.curve.displacement_at_peak_load,
        terminal_resistance=load_drop_rep.curve.terminal_load,
        terminal_displacement=load_drop_rep.curve.terminal_displacement,
        mapping_diagnostics=mapping_diag,
        classification_report=class_rep,
        load_drop_report=load_drop_rep,
        evolution_history=evol_hist,
        summary_row=summary_row,
    )
