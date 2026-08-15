"""Transport models for the bounded straight-flight staircase workflow."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StraightFlightStaircaseRequest(BaseModel):
    """Explicit inputs for the sole supported staircase case."""

    model_config = ConfigDict(
        extra="forbid",
        allow_inf_nan=False,
        str_strip_whitespace=True,
    )

    case_id: str = Field(min_length=1)
    lower_landing_effective_length_mm: float = Field(gt=0)
    going_mm: float = Field(gt=0)
    upper_landing_effective_length_mm: float = Field(gt=0)
    flight_width_mm: float = Field(gt=0)
    riser_mm: float = Field(gt=0)
    tread_mm: float = Field(gt=0)
    waist_thickness_mm: float = Field(gt=0)
    landing_thickness_mm: float = Field(gt=0)
    lower_landing_superimposed_service_load_kn_per_m2: float = Field(ge=0)
    flight_superimposed_service_load_kn_per_m2: float = Field(ge=0)
    upper_landing_superimposed_service_load_kn_per_m2: float = Field(ge=0)
    lower_landing_load_share: float = Field(gt=0, le=1)
    upper_landing_load_share: float = Field(gt=0, le=1)
    concrete_unit_weight_kn_per_m3: float = Field(gt=0)
    ultimate_load_factor: float = Field(gt=0)
    load_basis_reference: str = Field(min_length=1)
    effective_depth_mm: float = Field(gt=0)
    fck_n_per_mm2: float = Field(ge=20, le=40)
    fy_n_per_mm2: Literal[250.0, 415.0, 500.0]
    main_bar_diameter_mm: float = Field(gt=0)
    main_bar_spacing_mm: float = Field(gt=0)
    distribution_bar_diameter_mm: float = Field(gt=0)
    distribution_bar_spacing_mm: float = Field(gt=0)
    support_case: Literal["landings_span_with_flight"] = "landings_span_with_flight"
    span_direction: Literal["longitudinal"] = "longitudinal"
    landings_collinear: Literal[True] = True
    has_stringer_beams: Literal[False] = False
    is_cast_in_situ_solid: Literal[True] = True


class StraightFlightGeometryResponse(BaseModel):
    effective_span_mm: float
    inclined_step_length_mm: float
    slope_factor: float
    slope_angle_degrees: float
    inclined_going_length_mm: float
    source_refs: tuple[str, ...]


class StraightFlightActionResponse(BaseModel):
    waist_self_weight_kn_per_m2: float
    step_self_weight_kn_per_m2: float
    landing_self_weight_kn_per_m2: float
    flight_service_load_kn_per_m2: float
    lower_landing_factored_load_kn_per_m2: float
    flight_factored_load_kn_per_m2: float
    upper_landing_factored_load_kn_per_m2: float
    total_factored_load_kn: float
    lower_support_reaction_kn: float
    upper_support_reaction_kn: float
    maximum_factored_shear_kn_per_m: float
    maximum_moment_location_mm: float
    maximum_factored_moment_knm_per_m: float
    equilibrium_residual_kn: float
    source_refs: tuple[str, ...]
    load_generation_status: str


class StaircaseShearResponse(BaseModel):
    tau_v_n_per_mm2: float
    design_tau_c_n_per_mm2: float
    status: str


class StaircaseDesignCheckResponse(BaseModel):
    check_id: str
    actual: float
    limit: float | None
    unit: str
    comparison: str
    passed: bool


class StraightFlightDesignResponse(BaseModel):
    factored_moment_knm_per_m: float
    factored_shear_kn_per_m: float
    limiting_moment_knm_per_m: float
    ast_required_mm2_per_m: float | None
    minimum_reinforcement_mm2_per_m: float
    main_reinforcement_required_mm2_per_m: float | None
    main_reinforcement_provided_mm2_per_m: float
    distribution_reinforcement_required_mm2_per_m: float
    distribution_reinforcement_provided_mm2_per_m: float
    shear: StaircaseShearResponse
    actual_span_to_depth_ratio: float
    basic_span_to_depth_limit: float
    serviceability_status: str
    governing_checks: tuple[StaircaseDesignCheckResponse, ...]
    status: Literal["PASS", "REVIEW_REQUIRED", "FAIL"]
    source_refs: tuple[str, ...]
    limitations: tuple[str, ...]
    complete_engineering_design_approved: Literal[False]


class StraightFlightStaircaseProvenanceResponse(BaseModel):
    schema_version: str
    code_edition: str
    workflow: str
    case_id: str
    load_basis_reference: str
    load_generation_status: str
    benchmark_id: str
    clause_refs: tuple[str, ...]
    source_refs: tuple[str, ...]


class StraightFlightStaircaseResponse(BaseModel):
    """Typed transport subset of the composed service result."""

    case_id: str
    status: Literal["PASS", "REVIEW_REQUIRED", "FAIL"]
    geometry: StraightFlightGeometryResponse
    actions: StraightFlightActionResponse
    design: StraightFlightDesignResponse
    supported_case: str
    held_cases: tuple[str, ...]
    provenance: StraightFlightStaircaseProvenanceResponse
    qualified_review_required: Literal[True]
    complete_engineering_design_approved: Literal[False]
