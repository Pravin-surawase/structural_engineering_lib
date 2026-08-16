"""Transport models for the bounded concentric isolated-footing workflow."""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt

from fastapi_app.models.library_core import FootingLoadTransferResponse


class FootingPlanType(str, Enum):
    """Stable public footing-plan identifiers; mapped by the router."""

    ISOLATED_SQUARE = "ISOLATED_SQUARE"
    ISOLATED_RECTANGULAR = "ISOLATED_RECTANGULAR"


class ConcentricIsolatedFootingRequest(BaseModel):
    """Explicit inputs for the sole supported concentric isolated footing case."""

    model_config = ConfigDict(
        extra="forbid",
        allow_inf_nan=False,
        str_strip_whitespace=True,
    )

    case_id: str = Field(min_length=1)
    service_axial_load_kN: float = Field(gt=0)
    service_load_combination_id: str = Field(min_length=1)
    service_load_basis: Literal["includes_footing_self_weight_and_overburden"]
    service_load_origin: Literal["provided", "assumed", "verified"]
    factored_axial_load_kN: float = Field(gt=0)
    factored_load_combination_id: str = Field(min_length=1)
    allowable_soil_pressure_kPa: float = Field(gt=0)
    allowable_soil_pressure_source_reference: str = Field(min_length=1)
    allowable_soil_pressure_origin: Literal["provided", "assumed", "verified"]
    allowable_soil_pressure_is_externally_approved: Literal[True]
    footing_type: FootingPlanType
    column_L_mm: float = Field(gt=0)
    column_B_mm: float = Field(gt=0)
    minimum_overall_thickness_mm: float = Field(ge=150)
    maximum_overall_thickness_mm: float = Field(gt=0)
    thickness_increment_mm: float = Field(gt=0)
    effective_depth_offset_L_mm: float = Field(gt=0)
    effective_depth_offset_B_mm: float = Field(gt=0)
    footing_concrete_fck_nmm2: float = Field(gt=0)
    column_concrete_fck_nmm2: float = Field(gt=0)
    steel_fy_nmm2: float = Field(gt=0)
    effective_supporting_area_A1_mm2: float = Field(gt=0)
    effective_supporting_area_basis: Literal["largest_frustum_1v_2h"]
    effective_supporting_area_origin: Literal["provided", "assumed", "verified"]
    effective_supporting_area_is_approved: Literal[True]
    dowel_count: StrictInt = Field(gt=0)
    dowel_diameter_mm: float = Field(gt=0)
    column_longitudinal_bar_diameter_mm: float = Field(gt=0)
    available_dowel_development_length_into_footing_mm: float = Field(gt=0)
    available_dowel_development_length_into_column_mm: float = Field(gt=0)
    dowel_bar_type: Literal["deformed", "plain"] = "deformed"
    nominal_cover_mm: float | None = Field(default=None, gt=0)
    cover_exposure_basis: str | None = Field(default=None, min_length=1)
    cover_exposure_basis_is_approved: bool = False
    nominal_max_aggregate_size_mm: float | None = Field(default=None, gt=0)
    lower_bottom_bar_direction: Literal["L", "B"] | None = None
    upper_bottom_bar_direction: Literal["L", "B"] | None = None
    permitted_bottom_bar_diameters_mm: tuple[StrictInt, ...] = ()
    footing_bottom_bar_type: Literal["deformed", "plain"] | None = None


class FootingBearingResponse(BaseModel):
    L_mm: float
    B_mm: float
    q_max_kPa: float
    q_min_kPa: float
    q_safe_kPa: float
    pressure_type: str
    utilization_ratio: float
    is_safe: bool
    clause_ref: str
    warnings: tuple[str, ...]


class FootingFlexureResponse(BaseModel):
    Mu_L_kNm: float
    Ast_L_mm2: float
    pt_L_percent: float
    cantilever_L_mm: float
    Mu_B_kNm: float
    Ast_B_mm2: float
    pt_B_percent: float
    cantilever_B_mm: float
    d_mm: float
    is_safe: bool
    central_band_fraction: float
    clause_ref: str
    warnings: tuple[str, ...]


class FootingOneWayShearResponse(BaseModel):
    tau_v_nmm2: float
    tau_c_nmm2: float
    Vu_kN: float
    d_mm: float
    critical_section_mm: float
    utilization_ratio: float
    is_safe: bool
    governing_direction: str
    clause_ref: str
    warnings: tuple[str, ...]


class FootingPunchingResponse(BaseModel):
    tau_v_nmm2: float
    tau_c_nmm2: float
    perimeter_mm: float
    Vu_punch_kN: float
    d_mm: float
    beta_c: float
    ks: float
    utilization_ratio: float
    is_safe: bool
    clause_ref: str
    warnings: tuple[str, ...]


class FootingDepthCandidateResponse(BaseModel):
    overall_thickness_mm: float
    effective_depth_L_mm: float
    effective_depth_B_mm: float
    structural_status: Literal["PASS", "FAIL", "HOLD"]
    one_way_shear_utilization: float | None
    punching_shear_utilization: float | None
    reasons: tuple[str, ...]


class FootingReinforcementDemandResponse(BaseModel):
    direction: Literal["L", "B"]
    effective_depth_mm: float
    moment_kNm: float
    required_steel_area_mm2: float
    required_steel_percent: float
    central_band_fraction: float | None
    required_steel_basis: str
    provided_steel_area_mm2: float | None
    provided_steel_percent: float | None
    detailing_status: Literal["PASS", "FAIL", "HOLD"]


class FootingReinforcementZoneResponse(BaseModel):
    zone: Literal["full_width", "central_band", "outer_band_each"]
    width_mm: float
    required_area_mm2: float
    provided_area_mm2: float
    bar_count: int
    spacing_mm: float
    clear_spacing_mm: float


class FootingDirectionDetailResponse(BaseModel):
    direction: Literal["L", "B"]
    layer: Literal["lower", "upper"]
    layout: Literal["uniform", "central_band"]
    diameter_mm: int
    physical_effective_depth_mm: float
    analysis_effective_depth_mm: float
    Mu_kNm: float
    flexure_result_area_mm2: float
    analysis_screening_area_mm2: float
    minimum_area_mm2: float
    required_area_mm2: float
    provided_area_mm2: float
    bar_count: int
    spacing_mm: float
    clear_spacing_mm: float
    max_spacing_mm: float
    minimum_clear_spacing_mm: float
    max_diameter_mm: float
    development_length_mm: float
    development_length_unrounded_mm: float
    straight_anchorage_available_each_end_mm: float
    straight_bar_length_mm: float
    zones: tuple[FootingReinforcementZoneResponse, ...]


class FootingDowelScheduleLinkResponse(BaseModel):
    bar_count: int
    diameter_mm: float
    required_area_mm2: float
    provided_area_mm2: float
    required_development_length_into_footing_mm: float
    available_development_length_into_footing_mm: float
    required_development_length_into_supported_member_mm: float
    available_development_length_into_supported_member_mm: float
    is_safe: bool
    source_ids: tuple[str, ...]


class FootingDetailingResponse(BaseModel):
    status: Literal["PASS", "FAIL", "HOLD"]
    qualified_review_required: bool
    reasons: tuple[str, ...]
    contract_version: str
    supported_case: str
    exclusions: tuple[str, ...]
    units: dict[str, str]
    source_ids: tuple[str, ...]
    clause_refs: tuple[str, ...]
    lower_direction: Literal["L", "B"]
    upper_direction: Literal["L", "B"]
    lower: FootingDirectionDetailResponse | None
    upper: FootingDirectionDetailResponse | None
    actual_provided_pt_percent: dict[str, float]
    final_one_way_shear: FootingOneWayShearResponse | None
    dowel_schedule_link: FootingDowelScheduleLinkResponse
    accepted_load_transfer: FootingLoadTransferResponse


class FootingProvenanceResponse(BaseModel):
    schema_version: str
    code_edition: str
    units: dict[str, str]
    service_load_combination_id: str
    service_load_basis: str
    service_load_origin: str
    factored_load_combination_id: str
    allowable_soil_pressure_source_reference: str
    allowable_soil_pressure_origin: str
    allowable_soil_pressure_is_externally_approved: bool
    allowable_soil_pressure_role: str
    loaded_area_A2_basis: str
    effective_supporting_area_basis: str
    effective_supporting_area_origin: str
    effective_supporting_area_is_approved: bool
    core_function_ids: tuple[str, ...]
    clause_bases: dict[str, str]
    source_ids: tuple[str, ...]
    arithmetic_input_hash: str
    assumption_identity_hash: str
    library_content_identity: str
    replay_receipt_hash: str
    qualified_review_requirement: str


class ConcentricIsolatedFootingResponse(BaseModel):
    """Typed evidence returned by the bounded C1 design service."""

    case_id: str
    status: Literal["PASS", "FAIL", "HOLD"]
    calculation_status: Literal["PASS", "FAIL", "NOT_EVALUATED"]
    detailing_status: Literal["PASS", "FAIL", "HOLD"]
    detailing_hold_reason: str | None
    qualified_review_required: bool
    supported_case: str
    exclusions: tuple[str, ...]
    service_axial_load_kN: float
    factored_axial_load_kN: float
    selected_overall_thickness_mm: float | None
    selected_effective_depth_L_mm: float | None
    selected_effective_depth_B_mm: float | None
    depth_candidates: tuple[FootingDepthCandidateResponse, ...]
    bearing: FootingBearingResponse
    flexure: FootingFlexureResponse | None
    one_way_shear: FootingOneWayShearResponse | None
    one_way_shear_basis: Literal[
        "not_evaluated", "required_pt_screening", "actual_provided_pt_final"
    ]
    one_way_shear_screening: FootingOneWayShearResponse | None
    screening_pt_passed_to_one_way_shear_percent: dict[str, float]
    punching: FootingPunchingResponse | None
    load_transfer: FootingLoadTransferResponse
    detailing: FootingDetailingResponse | None
    reinforcement_demands: tuple[FootingReinforcementDemandResponse, ...]
    pt_passed_to_one_way_shear_percent: dict[str, float]
    failed_checks: tuple[str, ...]
    hold_reasons: tuple[str, ...]
    provenance: FootingProvenanceResponse
