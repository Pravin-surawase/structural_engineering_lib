# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       api
Description:  Public facing API functions — re-export hub.

Domain logic split into (ARCH-NEW-12):
  - beam_api.py    (beam design, detailing, outputs, smart features)
  - column_api.py  (column design, IS 456 Cl 39)
  - common_api.py  (shared validators, version, validation utilities)
"""

from __future__ import annotations

# ── Re-exported symbols (not defined in this package) ──────────────────
from structural_lib.codes.is456.beam.torsion import (  # noqa: F401
    TorsionResult,
    calculate_equivalent_moment,
    calculate_equivalent_shear,
    calculate_longitudinal_torsion_steel,
    calculate_torsion_shear_stress,
    calculate_torsion_stirrup_area,
    design_torsion,
)
from structural_lib.codes.is456.load_analysis import compute_bmd_sfd  # noqa: F401
from structural_lib.core.data_types import (  # noqa: F401
    ComplianceCaseResult,
    ComplianceReport,
    CriticalPoint,
    LoadDefinition,
    LoadDiagramResult,
    LoadType,
    ValidationReport,
)
from structural_lib.core.inputs import (  # noqa: F401
    BeamGeometryInput,
    BeamInput,
    DetailingConfigInput,
    LoadCaseInput,
    LoadsInput,
    MaterialsInput,
)
from structural_lib.core.models import (
    BeamGeometry,
    DesignDefaults,
    FrameType,
)  # noqa: F401

# ── Domain modules (beam, column, common) ──────────────────────────────
from structural_lib.services.beam_api import (  # noqa: F401
    _detailing_result_to_dict,
    _extract_beam_params_from_schema,
    build_detailing_input,
    check_anchorage_at_simple_support,
    check_beam_ductility,
    check_beam_is456,
    check_beam_slenderness,
    check_compliance_report,
    check_crack_width,
    check_deflection_span_depth,
    compute_bbs,
    compute_critical,
    compute_detailing,
    compute_dxf,
    compute_report,
    design_and_detail_beam_is456,
    design_beam_is456,
    design_from_input,
    detail_beam_is456,
    enhanced_shear_strength_is456,
    export_bbs,
    optimize_beam_cost,
    smart_analyze_design,
    suggest_beam_design_improvements,
)
from structural_lib.services.calculation_report import (  # noqa: F401
    CalculationReport,
    InputSection,
    ProjectInfo,
    ResultSection,
    generate_calculation_report,
)
from structural_lib.services.column_api import (  # noqa: F401
    biaxial_bending_check_is456,
    calculate_additional_moment_is456,
    calculate_effective_length_is456,
    check_column_ductility_is13920,
    check_helical_reinforcement_is456,
    classify_column_is456,
    design_column_axial_is456,
    design_column_is456,
    design_long_column_is456,
    design_short_column_uniaxial_is456,
    detail_column_is456,
    min_eccentricity_is456,
    pm_interaction_curve_is456,
)
from structural_lib.services.common_api import (  # noqa: F401
    _require_is456_units,
    _validate_plausibility,
    get_library_version,
    validate_design_results,
    validate_job_spec,
)
from structural_lib.visualization.geometry_3d import (  # noqa: F401
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

from .api_results import DesignAndDetailResult  # noqa: F401
from .audit import (  # noqa: F401
    AuditLogEntry,
    AuditTrail,
    CalculationHash,
    compute_hash,
    create_calculation_certificate,
    verify_calculation,
)
from .etabs_import import (  # noqa: F401
    ETABSEnvelopeResult,
    ETABSForceRow,
    create_job_from_etabs,
    create_jobs_from_etabs_csv,
    load_etabs_csv,
    normalize_etabs_forces,
    validate_etabs_csv,
)

__all__ = [
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
    # Input dataclasses (TASK-276)
    "BeamInput",
    "BeamGeometryInput",
    "MaterialsInput",
    "LoadsInput",
    "LoadCaseInput",
    "DetailingConfigInput",
    "design_from_input",
    # Audit & Verification (TASK-278)
    "AuditTrail",
    "AuditLogEntry",
    "CalculationHash",
    "compute_hash",
    "create_calculation_certificate",
    "verify_calculation",
    # Calculation Report (TASK-277)
    "CalculationReport",
    "ProjectInfo",
    "InputSection",
    "ResultSection",
    "generate_calculation_report",
    # Outputs
    "compute_detailing",
    "build_detailing_input",
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
    # Column Design (IS 456 Clause 39)
    "calculate_effective_length_is456",
    "calculate_additional_moment_is456",
    "classify_column_is456",
    "min_eccentricity_is456",
    "design_column_axial_is456",
    "design_short_column_uniaxial_is456",
    "pm_interaction_curve_is456",
    "biaxial_bending_check_is456",
    "design_long_column_is456",
    "check_helical_reinforcement_is456",
    "design_column_is456",
    "detail_column_is456",
    # IS 13920 Ductile Detailing
    "check_column_ductility_is13920",
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
    # Load Analysis (BMD/SFD) (TASK-145)
    "compute_bmd_sfd",
    "LoadType",
    "LoadDefinition",
    "CriticalPoint",
    "LoadDiagramResult",
    # 3D Visualization (TASK-3D-03)
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
]
