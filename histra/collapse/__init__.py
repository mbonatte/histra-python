"""Collapse mechanism identification and kinematic diagnostics for HiStrA."""
from __future__ import annotations

from histra.collapse.active_mass import (
    ActiveMassCriteria,
    ActiveMassIndex,
    ExecutionActiveMassReport,
    RegionalActiveMassSummary,
    StepActiveMassReport,
    compute_active_mass_fraction,
    compute_active_mass_sensitivity,
    evaluate_execution_active_mass,
    evaluate_regional_active_mass,
    evaluate_step_active_mass,
)
from histra.collapse.participation import (
    BridgeClassification,
    ExecutionParticipationReport,
    KinematicParticipationIndex,
    RegionDeformationMetrics,
    RegionalParticipationSummary,
    StepParticipationReport,
    classify_bridge_components,
    compute_kinematic_participation,
    compute_quad_mass,
    evaluate_execution_participation,
    evaluate_regional_participation,
    evaluate_step_participation,
    sample_quad_displacements_and_masses,
)

__all__ = [
    "ActiveMassCriteria",
    "ActiveMassIndex",
    "BridgeClassification",
    "ExecutionActiveMassReport",
    "ExecutionParticipationReport",
    "KinematicParticipationIndex",
    "RegionDeformationMetrics",
    "RegionalActiveMassSummary",
    "RegionalParticipationSummary",
    "StepActiveMassReport",
    "StepParticipationReport",
    "classify_bridge_components",
    "compute_active_mass_fraction",
    "compute_active_mass_sensitivity",
    "compute_kinematic_participation",
    "compute_quad_mass",
    "evaluate_execution_active_mass",
    "evaluate_execution_participation",
    "evaluate_regional_active_mass",
    "evaluate_regional_participation",
    "evaluate_step_active_mass",
    "evaluate_step_participation",
    "sample_quad_displacements_and_masses",
]

