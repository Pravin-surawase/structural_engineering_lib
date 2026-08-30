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
from structural_lib.codes.is456.beam.detailing import (  # noqa: F401
    TensionBarAnchorageResultV1,
    calculate_development_length_unrounded,
    evaluate_tension_bar_anchorage_v1,
)
from structural_lib.codes.is456.beam.torsion import (  # noqa: F401
    TorsionResult,
    calculate_equivalent_moment,
    calculate_equivalent_shear,
    calculate_longitudinal_torsion_steel,
    calculate_torsion_shear_stress,
    calculate_torsion_stirrup_area,
    design_torsion,
)
from structural_lib.codes.is456.footing.bearing import (  # noqa: F401
    bearing_stress_enhancement,
    check_bearing_pressure,
    size_footing,
)
from structural_lib.codes.is456.footing.flexure import footing_flexure  # noqa: F401
from structural_lib.codes.is456.footing.load_transfer import (  # noqa: F401
    LoadTransferResult,
    check_isolated_footing_load_transfer,
)
from structural_lib.codes.is456.footing.one_way_shear import (  # noqa: F401
    footing_one_way_shear,
)
from structural_lib.codes.is456.footing.punching_shear import (  # noqa: F401
    footing_punching_shear,
)
from structural_lib.codes.is456.load_analysis import compute_bmd_sfd  # noqa: F401
from structural_lib.core.building_gravity import (  # noqa: F401
    GravityPracticalActionKindV1,
    GravityPracticalActionUnitsV1,
    GravityPracticalActionV1,
)
from structural_lib.core.data_types import (  # noqa: F401  # noqa: F401
    BearingPressureCheckResult,
    BearingStressEnhancementResult,
    CheckCodeReport,
    ComplianceCaseResult,
    ComplianceReport,
    CriticalPoint,
    FootingBearingResult,
    FootingFlexureResult,
    FootingOneWayShearResult,
    FootingPunchingResult,
    LoadDefinition,
    LoadDiagramResult,
    LoadType,
    ValidationReport,
    VersionInfo,
)
from structural_lib.core.gravity_workflow import (  # noqa: F401
    GravityBeamDesignBasisV1,
    GravityBeamReinforcementBasisV1,
    GravityLongitudinalBarLayersV1,
    GravityPracticalActionReconciliationV1,
)
from structural_lib.core.inputs import (  # noqa: F401
    BeamGeometryInput,
    BeamInput,
    DetailingConfigInput,
    LoadCaseInput,
    LoadsInput,
    MaterialsInput,
)
from structural_lib.core.models import (  # noqa: F401
    BeamGeometry,
    DesignDefaults,
    FrameType,
)
from structural_lib.services.beam_api import (  # noqa: F401
    _detailing_result_to_dict,
    _extract_beam_params_from_schema,
    build_detailing_input,
    calculate_development_length,
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
    design_flanged_beam_is456,
    design_from_input,
    detail_beam_is456,
    enhanced_shear_strength_is456,
    export_bbs,
    optimize_beam_cost,
    smart_analyze_design,
    suggest_beam_design_improvements,
)
from structural_lib.services.beam_reinforcement import (  # noqa: F401
    BeamReinforcementEvaluationV1,
    BeamReinforcementSelectionConstraintsV1,
    LongitudinalBarLayersV1,
    SuppliedBeamReinforcementV1,
    evaluate_supplied_beam_reinforcement_v1,
)
from structural_lib.services.calculation_report import (  # noqa: F401
    CalculationReport,
    InputSection,
    ProjectInfo,
    ResultSection,
    generate_calculation_report,
)
from structural_lib.services.capabilities import (  # noqa: F401
    IS456Capability,
    get_supported_is456_capabilities,
    get_supported_is456_capability_document,
    get_supported_is456_semantic_contract,
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

# ── Domain modules (beam, column, common) ──────────────────────────────
from structural_lib.services.combined_footing_api import (  # noqa: F401
    SymmetricCombinedFootingDesignInput,
    SymmetricCombinedFootingDesignProvenance,
    SymmetricCombinedFootingDesignResult,
    SymmetricCombinedFootingDesignStatus,
    design_symmetric_combined_footing_is456,
)
from structural_lib.services.common_api import (  # noqa: F401
    _require_is456_units,
    _validate_plausibility,
    check_code,
    get_library_version,
    show_versions,
    validate_design_results,
    validate_job_spec,
)
from structural_lib.services.costing import CostProfile  # noqa: F401
from structural_lib.services.deep_beam_api import (  # noqa: F401
    SimplySupportedDeepBeamDesignInput,
    SimplySupportedDeepBeamDesignProvenance,
    SimplySupportedDeepBeamDesignResult,
    design_simply_supported_deep_beam_is456,
)
from structural_lib.services.flat_slab_api import (  # noqa: F401
    RegularInteriorFlatSlabDesignInput,
    RegularInteriorFlatSlabDesignProvenance,
    RegularInteriorFlatSlabDesignResult,
    RegularInteriorFlatSlabDesignStatus,
    design_regular_interior_flat_slab_is456,
)
from structural_lib.services.footing_api import (  # noqa: F401
    ConcentricIsolatedFootingInput,
    ConcentricIsolatedFootingResult,
    FootingDepthCandidate,
    FootingDirectionalReinforcementDemand,
    FootingProvenance,
    design_concentric_isolated_footing_is456,
)
from structural_lib.services.gravity_builder import (  # noqa: F401
    RectangularGravityWorkflowBuilderInputV1,
    build_rectangular_gravity_workflow_request_v1,
    get_gravity_workflow_example_document_v1,
    get_gravity_workflow_example_request_v1,
)
from structural_lib.services.gravity_calculation_book import (  # noqa: F401
    GravityWorkflowDefinitionV1,
    GravityWorkflowRunBundleV1,
    get_gravity_workflow_definition_v1,
    run_gravity_workflow_with_book_v1,
)
from structural_lib.services.gravity_workflow import (  # noqa: F401
    GravityWorkflowRequestV1,
    GravityWorkflowResultV1,
    run_gravity_workflow_v1,
)

# ── Multi-objective optimization ────────────────────────────────────────
from structural_lib.services.multi_objective_optimizer import (  # noqa: F401
    ParetoCandidate,
    ParetoOptimizationResult,
    optimize_pareto_front,
)
from structural_lib.services.optimization import (  # noqa: F401
    OptimizationConstraints,
    OptimizationInfeasibleError,
)
from structural_lib.services.project_beam import (  # noqa: F401
    EffectiveDepthBasisV1,
    EffectiveDepthResolutionV1,
)
from structural_lib.services.slab_api import (  # noqa: F401
    CompleteOneWaySlabDesignResult,
    ContinuousOneWaySlabDesignResult,
    OneWaySlabDesignResult,
    TwoWaySlabPanelWorkflowResult,
    design_complete_one_way_slab_is456,
    design_continuous_one_way_slab_builtin_is456,
    design_continuous_one_way_slab_is456,
    design_one_way_slab_is456,
    design_two_way_slab_is456,
    design_two_way_slab_panel_builtin_is456,
    design_two_way_slab_panel_is456,
)
from structural_lib.services.staircase_api import (  # noqa: F401
    StraightFlightStaircaseInput,
    StraightFlightStaircaseProvenance,
    StraightFlightStaircaseResult,
    design_straight_flight_staircase_is456,
)
from structural_lib.services.strap_footing_api import (  # noqa: F401
    PropertyLineStrapFootingDesignInput,
    PropertyLineStrapFootingDesignProvenance,
    PropertyLineStrapFootingDesignResult,
    PropertyLineStrapFootingDesignStatus,
    design_property_line_strap_footing_is456,
)
from structural_lib.services.wall_api import (  # noqa: F401
    BracedWallDesignInput,
    BracedWallDesignProvenance,
    BracedWallDesignResult,
    design_braced_wall_is456,
)
from structural_lib.services.workflow_catalog import (  # noqa: F401
    ComposedWorkflowCapability,
    WorkflowCatalog,
    get_workflow_catalog,
    get_workflow_catalog_document,
    serialize_workflow_catalog,
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

from .api_results import (
    DesignAndDetailResult,  # noqa: F401
    FlangedBeamDesignResult,  # noqa: F401
)
from .audit import (  # noqa: F401
    AuditLogEntry,
    AuditTrail,
    CalculationHash,
    compute_hash,
    create_calculation_certificate,
    verify_calculation,
)
from .contracts.etabs_w3 import (  # noqa: F401
    BeamActionPageV1,
    BeamDemandBuildResultV1,
    BeamDemandDerivationRequestV1,
    ETABSDisplacementBuildRequestV1,
    ETABSDisplacementBuildResultV1,
    ETABSDisplacementSnapshotV1,
    ETABSModelContextV1,
    ETABSModelDefinitionBuildRequestV1,
    ETABSModelDefinitionBuildResultV1,
    ETABSModelDefinitionSnapshotV1,
    ETABSOutputSelectionStateV1,
    ETABSReactionBuildRequestV1,
    ETABSReactionBuildResultV1,
    ETABSReactionSnapshotV1,
    ETABSResultCatalogueBuildRequestV1,
    ETABSResultCatalogueBuildResultV1,
    ETABSResultCatalogueCapacityV1,
    ETABSResultCatalogueV1,
    W3BuildIssueV1,
    W3BuildStatusV1,
    build_etabs_displacement_snapshot_v1,
    build_etabs_model_definition_snapshot_v1,
    build_etabs_reaction_snapshot_v1,
    build_etabs_result_catalogue_v1,
    canonical_beam_demand_snapshot_hash_basis_json_v1,
    canonical_etabs_result_catalogue_hash_basis_json_v1,
    derive_beam_demand_snapshot_v1,
    query_beam_action_rows_v1,
    verify_beam_demand_snapshot_hash_v1,
    verify_etabs_displacement_snapshot_hash_v1,
    verify_etabs_model_definition_snapshot_hash_v1,
    verify_etabs_reaction_snapshot_hash_v1,
    verify_etabs_result_catalogue_hash_v1,
)
from .etabs_catalogue_bridge import (  # noqa: F401
    ETABSLiveCaseStatusV1,
    ETABSLiveCatalogueRunRequestV1,
    ETABSLiveCatalogueStateV1,
    ETABSLiveCatalogueTransportV1,
    ETABSLiveSelectionStateV1,
    run_etabs_live_catalogue_v1,
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
from .etabs_result_catalogue_adapter import (  # noqa: F401
    ETABSCatalogueAdapterRequestV1,
    ETABSCatalogueAdapterResultV1,
    ETABSCatalogueSelectionRequestV1,
    ETABSGetterCallEvidenceV1,
    ETABSGetterContainerKindV1,
    ETABSGetterOutcomeV1,
    extract_etabs_result_catalogue_v1,
)

__all__ = [
    "ETABSModelContextV1",
    "ETABSOutputSelectionStateV1",
    "ETABSModelDefinitionBuildRequestV1",
    "ETABSModelDefinitionBuildResultV1",
    "ETABSModelDefinitionSnapshotV1",
    "ETABSDisplacementBuildRequestV1",
    "ETABSDisplacementBuildResultV1",
    "ETABSDisplacementSnapshotV1",
    "ETABSReactionBuildRequestV1",
    "ETABSReactionBuildResultV1",
    "ETABSReactionSnapshotV1",
    "build_etabs_model_definition_snapshot_v1",
    "build_etabs_displacement_snapshot_v1",
    "build_etabs_reaction_snapshot_v1",
    "verify_etabs_model_definition_snapshot_hash_v1",
    "verify_etabs_displacement_snapshot_hash_v1",
    "verify_etabs_reaction_snapshot_hash_v1",
    # W3 result catalogue and beam demand
    "BeamActionPageV1",
    "BeamDemandBuildResultV1",
    "BeamDemandDerivationRequestV1",
    "ETABSCatalogueAdapterRequestV1",
    "ETABSCatalogueAdapterResultV1",
    "ETABSCatalogueSelectionRequestV1",
    "ETABSGetterCallEvidenceV1",
    "ETABSGetterContainerKindV1",
    "ETABSGetterOutcomeV1",
    "ETABSLiveCaseStatusV1",
    "ETABSLiveCatalogueRunRequestV1",
    "ETABSLiveCatalogueStateV1",
    "ETABSLiveCatalogueTransportV1",
    "ETABSLiveSelectionStateV1",
    "ETABSResultCatalogueBuildRequestV1",
    "ETABSResultCatalogueBuildResultV1",
    "ETABSResultCatalogueCapacityV1",
    "ETABSResultCatalogueV1",
    "W3BuildIssueV1",
    "W3BuildStatusV1",
    "build_etabs_result_catalogue_v1",
    "canonical_beam_demand_snapshot_hash_basis_json_v1",
    "canonical_etabs_result_catalogue_hash_basis_json_v1",
    "derive_beam_demand_snapshot_v1",
    "extract_etabs_result_catalogue_v1",
    "query_beam_action_rows_v1",
    "run_etabs_live_catalogue_v1",
    "verify_beam_demand_snapshot_hash_v1",
    "verify_etabs_result_catalogue_hash_v1",
    # Version
    "get_library_version",
    # Diagnostics (TASK-725)
    "show_versions",
    "VersionInfo",
    # Validation
    "validate_job_spec",
    "validate_design_results",
    # Self-validation (TASK-724)
    "check_code",
    "CheckCodeReport",
    # Core design functions
    "design_beam_is456",
    "EffectiveDepthBasisV1",
    "EffectiveDepthResolutionV1",
    "design_flanged_beam_is456",
    "FlangedBeamDesignResult",
    "check_beam_is456",
    "detail_beam_is456",
    "design_and_detail_beam_is456",
    "ComplianceCaseResult",
    "ComplianceReport",
    "DesignAndDetailResult",
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
    "calculate_development_length",
    "calculate_development_length_unrounded",
    "check_anchorage_at_simple_support",
    "evaluate_tension_bar_anchorage_v1",
    "TensionBarAnchorageResultV1",
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
    # Costing
    "CostProfile",
    "OptimizationConstraints",
    "OptimizationInfeasibleError",
    # Smart features
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
    # Symmetric combined footing (bounded supported case)
    "design_symmetric_combined_footing_is456",
    "SymmetricCombinedFootingDesignInput",
    "SymmetricCombinedFootingDesignProvenance",
    "SymmetricCombinedFootingDesignResult",
    "SymmetricCombinedFootingDesignStatus",
    # Building Gravity Workflow V1
    "BeamReinforcementEvaluationV1",
    "BeamReinforcementSelectionConstraintsV1",
    "LongitudinalBarLayersV1",
    "SuppliedBeamReinforcementV1",
    "evaluate_supplied_beam_reinforcement_v1",
    "GravityBeamDesignBasisV1",
    "GravityBeamReinforcementBasisV1",
    "GravityLongitudinalBarLayersV1",
    "GravityPracticalActionKindV1",
    "GravityPracticalActionUnitsV1",
    "GravityPracticalActionV1",
    "GravityPracticalActionReconciliationV1",
    "GravityWorkflowRequestV1",
    "GravityWorkflowResultV1",
    "GravityWorkflowRunBundleV1",
    "GravityWorkflowDefinitionV1",
    "RectangularGravityWorkflowBuilderInputV1",
    "build_rectangular_gravity_workflow_request_v1",
    "get_gravity_workflow_example_document_v1",
    "get_gravity_workflow_example_request_v1",
    "get_gravity_workflow_definition_v1",
    "run_gravity_workflow_v1",
    "run_gravity_workflow_with_book_v1",
    # Property-line strap footing (bounded supported case)
    "design_property_line_strap_footing_is456",
    "PropertyLineStrapFootingDesignInput",
    "PropertyLineStrapFootingDesignProvenance",
    "PropertyLineStrapFootingDesignResult",
    "PropertyLineStrapFootingDesignStatus",
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
    # Braced wall (bounded supported case)
    "design_braced_wall_is456",
    "BracedWallDesignInput",
    "BracedWallDesignProvenance",
    "BracedWallDesignResult",
    # Simply supported deep beam (bounded supported case)
    "design_simply_supported_deep_beam_is456",
    "SimplySupportedDeepBeamDesignInput",
    "SimplySupportedDeepBeamDesignProvenance",
    "SimplySupportedDeepBeamDesignResult",
    # Regular interior flat slab (bounded supported case)
    "design_regular_interior_flat_slab_is456",
    "RegularInteriorFlatSlabDesignInput",
    "RegularInteriorFlatSlabDesignProvenance",
    "RegularInteriorFlatSlabDesignResult",
    "RegularInteriorFlatSlabDesignStatus",
    # Capability discovery
    "get_supported_is456_capability_document",
    "get_supported_is456_capabilities",
    "get_supported_is456_semantic_contract",
    "ComposedWorkflowCapability",
    "WorkflowCatalog",
    "get_workflow_catalog",
    "get_workflow_catalog_document",
    "serialize_workflow_catalog",
    "IS456Capability",
]
