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

# Import geometry and frame types from core.models
from .core.models import BeamGeometry, DesignDefaults, FrameType

# Import all public API functions from services.api
from .services.api import (
    # Audit & Verification
    AuditLogEntry,
    AuditTrail,
    # Input dataclasses
    BeamGeometryInput,
    BeamInput,
    CalculationHash,
    # Calculation Report
    CalculationReport,
    # Return types (for type annotations)
    ComplianceCaseResult,
    ComplianceReport,
    # Load Analysis
    CriticalPoint,
    DesignAndDetailResult,
    DetailingConfigInput,
    # ETABS Integration
    ETABSEnvelopeResult,
    ETABSForceRow,
    InputSection,
    LoadCaseInput,
    LoadDefinition,
    LoadDiagramResult,
    LoadsInput,
    LoadType,
    MaterialsInput,
    ProjectInfo,
    ResultSection,
    # Torsion Design
    TorsionResult,
    ValidationReport,
    build_detailing_input,
    # Column Design
    calculate_additional_moment_is456,
    calculate_equivalent_moment,
    calculate_equivalent_shear,
    calculate_longitudinal_torsion_steel,
    calculate_torsion_shear_stress,
    calculate_torsion_stirrup_area,
    # Serviceability
    check_beam_ductility,
    check_beam_is456,
    check_beam_slenderness,
    check_column_ductility_is13920,
    check_compliance_report,
    check_crack_width,
    check_deflection_span_depth,
    classify_column_is456,
    compute_bbs,
    compute_bmd_sfd,
    compute_critical,
    # Outputs
    compute_detailing,
    compute_dxf,
    compute_hash,
    compute_report,
    create_calculation_certificate,
    create_job_from_etabs,
    create_jobs_from_etabs_csv,
    # Core design functions
    design_and_detail_beam_is456,
    design_beam_is456,
    design_column_axial_is456,
    design_from_input,
    design_short_column_uniaxial_is456,
    design_torsion,
    detail_beam_is456,
    # Shear
    enhanced_shear_strength_is456,
    export_bbs,
    generate_calculation_report,
    # Version
    get_library_version,
    load_etabs_csv,
    min_eccentricity_is456,
    normalize_etabs_forces,
    # Smart features
    optimize_beam_cost,
    pm_interaction_curve_is456,
    smart_analyze_design,
    suggest_beam_design_improvements,
    validate_design_results,
    # Validation
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
    # Validation
    "validate_job_spec",
    "validate_design_results",
    # Core design functions
    "design_beam_is456",
    "check_beam_is456",
    "detail_beam_is456",
    "design_and_detail_beam_is456",
    # Return types
    "ComplianceCaseResult",
    "ComplianceReport",
    "DesignAndDetailResult",
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
    "optimize_beam_cost",
    "suggest_beam_design_improvements",
    "smart_analyze_design",
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
    "classify_column_is456",
    "min_eccentricity_is456",
    "design_column_axial_is456",
    "design_short_column_uniaxial_is456",
    "pm_interaction_curve_is456",
    # IS 13920 Ductile Detailing
    "check_column_ductility_is13920",
]


def __getattr__(name: str) -> _ModuleType:
    if name in _LAZY_MODULES:
        mod = importlib.import_module(f".{name}", __name__)
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
