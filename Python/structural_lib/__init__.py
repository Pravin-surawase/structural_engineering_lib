# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Package:      structural_lib
Description:  IS 456:2000 Structural Engineering Library
License:      MIT

Version is read dynamically from pyproject.toml via importlib.metadata.
Use api.get_library_version() to get the current version.
"""

from __future__ import annotations

import importlib
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _get_version
from types import ModuleType as _ModuleType

# Dynamic version from installed package metadata
try:
    __version__ = _get_version("structural-lib-is456")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"  # Not installed, development mode

# Expose key modules
from . import (
    api,
    compliance,
    detailing,
    flexure,
    imports,
    inputs,
    models,
    rebar,
    result_base,
    serviceability,
    shear,
    types,
)

# Import EndCondition enum (needed for calculate_effective_length_is456)
from .core.data_types import EndCondition

# Import geometry and frame types from core.models
from .core.models import BeamGeometry, DesignDefaults, FrameType

# Import all public API functions from services.api
from .services.api import (  # Audit & Verification; Input dataclasses; Calculation Report; Self-validation (TASK-724); Return types (for type annotations); Load Analysis; ETABS Integration; Multi-objective optimization; Torsion Design; Column Design; Serviceability; Outputs; Core design functions; Shear; Version; Smart features; Diagnostics (TASK-725); Footing Design (IS 456 Cl 34); Validation
    AuditLogEntry,
    AuditTrail,
    BeamGeometryInput,
    BeamInput,
    BearingPressureCheckResult,
    BearingStressEnhancementResult,
    CalculationHash,
    CalculationReport,
    CheckCodeReport,
    CompleteOneWaySlabDesignResult,
    ComplianceCaseResult,
    ComplianceReport,
    ConcentricIsolatedFootingInput,
    ConcentricIsolatedFootingResult,
    ContinuousOneWaySlabDesignResult,
    CostProfile,
    CriticalPoint,
    DesignAndDetailResult,
    DetailingConfigInput,
    ETABSEnvelopeResult,
    ETABSForceRow,
    FlangedBeamDesignResult,
    FootingBearingResult,
    FootingDepthCandidate,
    FootingDirectionalReinforcementDemand,
    FootingFlexureResult,
    FootingOneWayShearResult,
    FootingProvenance,
    FootingPunchingResult,
    InputSection,
    IS456Capability,
    LoadCaseInput,
    LoadDefinition,
    LoadDiagramResult,
    LoadsInput,
    LoadTransferResult,
    LoadType,
    MaterialsInput,
    OneWaySlabDesignResult,
    ParetoCandidate,
    ParetoOptimizationResult,
    ProjectInfo,
    ResultSection,
    StraightFlightStaircaseInput,
    StraightFlightStaircaseProvenance,
    StraightFlightStaircaseResult,
    TorsionResult,
    TwoWaySlabPanelWorkflowResult,
    ValidationReport,
    VersionInfo,
    bearing_stress_enhancement,
    biaxial_bending_check_is456,
    build_detailing_input,
    calculate_additional_moment_is456,
    calculate_development_length,
    calculate_effective_length_is456,
    calculate_equivalent_moment,
    calculate_equivalent_shear,
    calculate_longitudinal_torsion_steel,
    calculate_torsion_shear_stress,
    calculate_torsion_stirrup_area,
    check_anchorage_at_simple_support,
    check_beam_ductility,
    check_beam_is456,
    check_beam_slenderness,
    check_bearing_pressure,
    check_code,
    check_column_ductility_is13920,
    check_compliance_report,
    check_crack_width,
    check_deflection_span_depth,
    check_helical_reinforcement_is456,
    check_isolated_footing_load_transfer,
    classify_column_is456,
    compute_bbs,
    compute_bmd_sfd,
    compute_critical,
    compute_detailing,
    compute_dxf,
    compute_hash,
    compute_report,
    create_calculation_certificate,
    create_job_from_etabs,
    create_jobs_from_etabs_csv,
    design_and_detail_beam_is456,
    design_beam_is456,
    design_column_axial_is456,
    design_column_is456,
    design_complete_one_way_slab_is456,
    design_concentric_isolated_footing_is456,
    design_continuous_one_way_slab_builtin_is456,
    design_continuous_one_way_slab_is456,
    design_flanged_beam_is456,
    design_from_input,
    design_long_column_is456,
    design_one_way_slab_is456,
    design_short_column_uniaxial_is456,
    design_straight_flight_staircase_is456,
    design_torsion,
    design_two_way_slab_is456,
    design_two_way_slab_panel_builtin_is456,
    design_two_way_slab_panel_is456,
    detail_beam_is456,
    detail_column_is456,
    enhanced_shear_strength_is456,
    export_bbs,
    footing_flexure,
    footing_one_way_shear,
    footing_punching_shear,
    generate_calculation_report,
    get_library_version,
    get_supported_is456_capabilities,
    get_supported_is456_capability_document,
    get_supported_is456_semantic_contract,
    load_etabs_csv,
    min_eccentricity_is456,
    normalize_etabs_forces,
    optimize_beam_cost,
    optimize_pareto_front,
    pm_interaction_curve_is456,
    show_versions,
    size_footing,
    smart_analyze_design,
    suggest_beam_design_improvements,
    validate_design_results,
    validate_etabs_csv,
    validate_job_spec,
    verify_calculation,
)

# Import 3D visualization from visualization.geometry_3d
from .visualization.geometry_3d import (
    Beam3DGeometry,
    Point3D,
    RebarPath,
    RebarSegment,
    StirrupLoop,
    beam_to_3d_geometry,
    compute_beam_outline,
    compute_rebar_positions,
    compute_stirrup_path,
    compute_stirrup_positions,
)

# Lazy-loaded modules (imported on first access, not at package load)
_LAZY_MODULES = {
    "adapters",
    "etabs_import",
    "batch",
    "costing",
    "testing_strategies",
    "audit",
    "serialization",
}

# DXF export is optional (requires ezdxf)
dxf_export: _ModuleType | None
try:
    dxf_export = importlib.import_module(f"{__name__}.services.dxf_export")
except ImportError:
    dxf_export = None

# Reports module is optional (requires jinja2)
reports: _ModuleType | None
try:
    reports = importlib.import_module(f"{__name__}.reports")
except ImportError:
    reports = None

__all__ = [
    "__version__",
    # Modules
    "adapters",
    "api",
    "audit",
    "batch",
    "compliance",
    "costing",
    "detailing",
    "dxf_export",
    "etabs_import",
    "flexure",
    "imports",
    "inputs",
    "models",
    "rebar",
    "reports",
    "result_base",
    "serialization",
    "serviceability",
    "shear",
    "testing_strategies",
    "types",
    # Version
    "get_library_version",
    # Diagnostics (TASK-725)
    "show_versions",
    "VersionInfo",
    # Validation
    "validate_job_spec",
    "validate_design_results",
    # Core design functions
    "design_beam_is456",
    "design_flanged_beam_is456",
    "check_beam_is456",
    "detail_beam_is456",
    "design_and_detail_beam_is456",
    # Return types
    "ComplianceCaseResult",
    "ComplianceReport",
    "DesignAndDetailResult",
    "FlangedBeamDesignResult",
    # Input dataclasses
    "BeamInput",
    "BeamGeometryInput",
    "MaterialsInput",
    "LoadsInput",
    "LoadCaseInput",
    "DetailingConfigInput",
    "design_from_input",
    # Audit & Verification
    "AuditTrail",
    "AuditLogEntry",
    "CalculationHash",
    "compute_hash",
    "create_calculation_certificate",
    "verify_calculation",
    # Calculation Report
    "CalculationReport",
    "ProjectInfo",
    "InputSection",
    "ResultSection",
    "generate_calculation_report",
    # Outputs
    "compute_detailing",
    "build_detailing_input",
    "calculate_development_length",
    "check_anchorage_at_simple_support",
    "compute_bbs",
    "export_bbs",
    "compute_dxf",
    "compute_report",
    "compute_critical",
    # Serviceability
    "check_beam_ductility",
    "check_beam_slenderness",
    "check_deflection_span_depth",
    "check_crack_width",
    "check_compliance_report",
    # Validation
    "ValidationReport",
    # Shear (IS 456 Clause 40)
    "enhanced_shear_strength_is456",
    # Smart features
    "CostProfile",
    "optimize_beam_cost",
    "suggest_beam_design_improvements",
    "smart_analyze_design",
    # Multi-objective optimization
    "optimize_pareto_front",
    "ParetoOptimizationResult",
    "ParetoCandidate",
    # Torsion Design (IS 456 Clause 41)
    "design_torsion",
    "calculate_equivalent_shear",
    "calculate_equivalent_moment",
    "calculate_torsion_shear_stress",
    "calculate_torsion_stirrup_area",
    "calculate_longitudinal_torsion_steel",
    "TorsionResult",
    # ETABS Integration (CSV Import)
    "validate_etabs_csv",
    "load_etabs_csv",
    "normalize_etabs_forces",
    "create_job_from_etabs",
    "create_jobs_from_etabs_csv",
    "ETABSForceRow",
    "ETABSEnvelopeResult",
    # Load Analysis (BMD/SFD)
    "compute_bmd_sfd",
    "LoadType",
    "LoadDefinition",
    "CriticalPoint",
    "LoadDiagramResult",
    # 3D Visualization
    "Point3D",
    "BeamGeometry",
    "FrameType",
    "DesignDefaults",
    "RebarSegment",
    "RebarPath",
    "StirrupLoop",
    "Beam3DGeometry",
    "compute_rebar_positions",
    "compute_stirrup_path",
    "compute_stirrup_positions",
    "compute_beam_outline",
    "beam_to_3d_geometry",
    # Column Design (IS 456 Cl 25, 39.3, 39.5, 39.7)
    "calculate_additional_moment_is456",
    "calculate_effective_length_is456",
    "classify_column_is456",
    "min_eccentricity_is456",
    "design_column_axial_is456",
    "design_column_is456",
    "design_long_column_is456",
    "design_short_column_uniaxial_is456",
    "pm_interaction_curve_is456",
    "biaxial_bending_check_is456",
    "check_helical_reinforcement_is456",
    "detail_column_is456",
    "EndCondition",
    # IS 13920 Ductile Detailing
    "check_column_ductility_is13920",
    # Footing Design (IS 456 Cl 34)
    "size_footing",
    "bearing_stress_enhancement",
    "check_bearing_pressure",
    "footing_flexure",
    "footing_one_way_shear",
    "footing_punching_shear",
    "FootingBearingResult",
    "BearingPressureCheckResult",
    "BearingStressEnhancementResult",
    "FootingFlexureResult",
    "FootingOneWayShearResult",
    "FootingPunchingResult",
    "check_isolated_footing_load_transfer",
    "LoadTransferResult",
    "design_concentric_isolated_footing_is456",
    "ConcentricIsolatedFootingInput",
    "ConcentricIsolatedFootingResult",
    "FootingDepthCandidate",
    "FootingDirectionalReinforcementDemand",
    "FootingProvenance",
    # Solid slab design (bounded supported cases)
    "design_one_way_slab_is456",
    "design_complete_one_way_slab_is456",
    "design_continuous_one_way_slab_builtin_is456",
    "design_continuous_one_way_slab_is456",
    "design_two_way_slab_is456",
    "design_two_way_slab_panel_is456",
    "design_two_way_slab_panel_builtin_is456",
    "OneWaySlabDesignResult",
    "CompleteOneWaySlabDesignResult",
    "ContinuousOneWaySlabDesignResult",
    "TwoWaySlabPanelWorkflowResult",
    # Straight-flight staircase (bounded supported case)
    "design_straight_flight_staircase_is456",
    "StraightFlightStaircaseInput",
    "StraightFlightStaircaseProvenance",
    "StraightFlightStaircaseResult",
    # Capability discovery
    "get_supported_is456_capability_document",
    "get_supported_is456_capabilities",
    "get_supported_is456_semantic_contract",
    "IS456Capability",
    # Self-validation (TASK-724)
    "check_code",
    "CheckCodeReport",
]


def __getattr__(name: str) -> _ModuleType:
    if name in _LAZY_MODULES:
        mod = importlib.import_module(f".{name}", __name__)
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
