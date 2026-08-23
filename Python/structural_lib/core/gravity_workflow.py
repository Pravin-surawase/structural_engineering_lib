# SPDX-License-Identifier: MIT
"""Versioned request, applicability, action, and result types for Gravity V1."""

from __future__ import annotations

import hashlib
import json
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

from structural_lib.core.building_gravity import BuildingModelV1, LoadModelV1

__all__ = [
    "ComponentApplicabilityMatrixV1",
    "GravityBeamDesignBasisV1",
    "GravityBeamReinforcementBasisV1",
    "GravityColumnDesignBasisV1",
    "GravityComponentApplicabilityV1",
    "GravityComponentKindV1",
    "GravityComponentResultV1",
    "GravityFootingDesignBasisV1",
    "GravityMemberActionV1",
    "GravityLongitudinalBarLayersV1",
    "GravityPrerequisiteDispositionV1",
    "GravitySlabDesignBasisV1",
    "GravityWorkflowRequestV1",
    "GravityWorkflowResultV1",
]

_ID_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9_.:-]*$"
_SHA256_PATTERN = r"^[0-9a-f]{64}$"


class _FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", allow_inf_nan=False)


class GravityComponentKindV1(StrEnum):
    SLAB = "SLAB"
    BEAM = "BEAM"
    COLUMN = "COLUMN"
    FOOTING = "FOOTING"


class GravityPrerequisiteDispositionV1(StrEnum):
    READY = "READY"
    HOLD = "HOLD"


class GravitySlabDesignBasisV1(_FrozenModel):
    panel_id: str = Field(pattern=_ID_PATTERN)
    d_mm: float = Field(gt=0)
    fy_nmm2: float = Field(gt=0)
    main_bar_diameter_mm: float = Field(gt=0)
    main_bar_spacing_mm: float = Field(gt=0)
    distribution_bar_diameter_mm: float = Field(gt=0)
    distribution_bar_spacing_mm: float = Field(gt=0)
    reviewed_base_span_depth_limit: float = Field(gt=0)
    reviewed_aggregate_modification_factor: float = Field(gt=0)
    serviceability_limit_source_reference: str = Field(min_length=1, max_length=512)
    serviceability_limit_source_is_approved: Literal[True]
    qualified_serviceability_acceptance_reference: str = Field(
        min_length=1, max_length=512
    )
    qualified_serviceability_acceptance_acknowledged: Literal[True]
    effective_depth_source_reference: str = Field(min_length=1, max_length=512)


class GravityLongitudinalBarLayersV1(_FrozenModel):
    """Exact one-diameter bar layers, ordered from the relevant face inward."""

    diameter_mm: float = Field(gt=0)
    bars_per_layer: tuple[int, ...] = Field(min_length=1)
    vertical_center_spacings_mm: tuple[float, ...] = ()

    @model_validator(mode="after")
    def validate_layers(self) -> GravityLongitudinalBarLayersV1:
        if any(count < 2 for count in self.bars_per_layer):
            raise ValueError("bars_per_layer requires at least two bars per layer")
        if len(self.vertical_center_spacings_mm) != len(self.bars_per_layer) - 1:
            raise ValueError(
                "vertical_center_spacings_mm requires one value between layers"
            )
        if any(value <= 0 for value in self.vertical_center_spacings_mm):
            raise ValueError("vertical center spacings must be positive")
        return self


class GravityBeamReinforcementBasisV1(_FrozenModel):
    """Selection limits plus optional source-referenced supplied beam bars."""

    permitted_diameters_mm: tuple[float, ...] = (12.0, 16.0, 20.0, 25.0, 32.0)
    maximum_layers: int = Field(default=2, gt=0)
    maximum_bars_per_layer: int = Field(default=8, gt=0)
    nominal_max_aggregate_size_mm: float = Field(default=20.0, gt=0)
    effective_depth_tolerance_mm: float = Field(default=5.0, ge=0)
    objective: Literal["min_area", "min_bar_count", "max_spacing"] = "min_area"
    selection_source_reference: str = Field(min_length=1, max_length=512)
    supplied_tension: GravityLongitudinalBarLayersV1 | None = None
    supplied_compression_or_hanger: GravityLongitudinalBarLayersV1 | None = None
    bar_type: Literal["deformed", "plain"] = "deformed"
    has_standard_bend_at_start: bool = False
    has_standard_bend_at_end: bool = False
    supplied_reinforcement_source_reference: str | None = Field(
        default=None, min_length=1, max_length=512
    )

    @model_validator(mode="after")
    def validate_selection_and_supply(self) -> GravityBeamReinforcementBasisV1:
        normalized = tuple(float(value) for value in self.permitted_diameters_mm)
        if not normalized or normalized != tuple(sorted(set(normalized))):
            raise ValueError(
                "permitted_diameters_mm must be unique and strictly increasing"
            )
        supplied_values = (
            self.supplied_tension,
            self.supplied_compression_or_hanger,
            self.supplied_reinforcement_source_reference,
        )
        if any(value is not None for value in supplied_values) and any(
            value is None for value in supplied_values
        ):
            raise ValueError(
                "tension bars, compression or hanger bars, and their source "
                "reference must be supplied together"
            )
        return self


class GravityBeamDesignBasisV1(_FrozenModel):
    beam_id: str = Field(pattern=_ID_PATTERN)
    d_mm: float = Field(gt=0)
    fy_nmm2: float = Field(gt=0)
    d_dash_mm: float | None = Field(default=None, gt=0)
    asv_mm2: float = Field(gt=0)
    pt_percent: float | None = Field(default=None, gt=0)
    ast_mm2_for_shear: float | None = Field(default=None, gt=0)
    cover_mm: float | None = Field(default=None, gt=0)
    stirrup_dia_mm: float = Field(default=8.0, gt=0)
    effective_depth_source_reference: str = Field(min_length=1, max_length=512)
    reinforcement_basis: GravityBeamReinforcementBasisV1 | None = None

    @model_validator(mode="after")
    def validate_reinforcement_geometry(self) -> GravityBeamDesignBasisV1:
        if self.reinforcement_basis is not None and self.cover_mm is None:
            raise ValueError(
                "cover_mm is required when a reinforcement basis is supplied"
            )
        return self


class GravityColumnDesignBasisV1(_FrozenModel):
    column_id: str = Field(pattern=_ID_PATTERN)
    fy_nmm2: float = Field(gt=0)
    Asc_mm2: float = Field(gt=0)
    d_prime_mm: float = Field(gt=0)
    end_condition: Literal[
        "FIXED_FIXED",
        "FIXED_HINGED",
        "FIXED_FIXED_SWAY",
        "FIXED_FREE",
        "HINGED_HINGED",
        "FIXED_PARTIAL",
        "HINGED_PARTIAL",
    ]
    end_condition_source_reference: str = Field(min_length=1, max_length=512)
    reinforcement_source_reference: str = Field(min_length=1, max_length=512)
    braced_acknowledged: Literal[True]
    axial_only_action_acknowledged: Literal[True]


class GravityFootingDesignBasisV1(_FrozenModel):
    """External basis needed to advance one footing handoff beyond HOLD."""

    footing_id: str = Field(pattern=_ID_PATTERN)
    complete_service_axial_load_kn: float = Field(gt=0)
    service_load_combination_id: str = Field(min_length=1, max_length=128)
    service_load_basis: Literal["includes_footing_self_weight_and_overburden"]
    service_load_origin: Literal["provided", "verified"]
    complete_factored_axial_load_kn: float = Field(gt=0)
    factored_load_combination_id: str = Field(min_length=1, max_length=128)
    allowable_soil_pressure_kpa: float = Field(gt=0)
    allowable_soil_pressure_source_reference: str = Field(min_length=1, max_length=512)
    allowable_soil_pressure_origin: Literal["provided", "verified"]
    allowable_soil_pressure_is_externally_approved: Literal[True]
    footing_type: Literal["SQUARE", "RECTANGULAR"]
    minimum_overall_thickness_mm: float = Field(gt=0)
    maximum_overall_thickness_mm: float = Field(gt=0)
    thickness_increment_mm: float = Field(gt=0)
    effective_depth_offset_l_mm: float = Field(gt=0)
    effective_depth_offset_b_mm: float = Field(gt=0)
    footing_concrete_fck_nmm2: float = Field(gt=0)
    steel_fy_nmm2: float = Field(gt=0)
    effective_supporting_area_a1_mm2: float = Field(gt=0)
    effective_supporting_area_basis: Literal["largest_frustum_1v_2h"]
    effective_supporting_area_origin: Literal["provided", "verified"]
    effective_supporting_area_is_approved: Literal[True]
    dowel_count: int = Field(gt=0)
    dowel_diameter_mm: float = Field(gt=0)
    column_longitudinal_bar_diameter_mm: float = Field(gt=0)
    available_dowel_development_length_into_footing_mm: float = Field(gt=0)
    available_dowel_development_length_into_column_mm: float = Field(gt=0)
    dowel_bar_type: Literal["deformed", "plain"] = "deformed"
    nominal_cover_mm: float | None = Field(default=None, gt=0)
    cover_exposure_basis: str | None = Field(default=None, min_length=1, max_length=512)
    cover_exposure_basis_is_approved: bool = False
    nominal_max_aggregate_size_mm: float | None = Field(default=None, gt=0)
    lower_bottom_bar_direction: Literal["L", "B"] | None = None
    upper_bottom_bar_direction: Literal["L", "B"] | None = None
    permitted_bottom_bar_diameters_mm: tuple[int, ...] = ()
    footing_bottom_bar_type: Literal["deformed", "plain"] | None = None

    @model_validator(mode="after")
    def validate_external_basis(self) -> GravityFootingDesignBasisV1:
        if self.maximum_overall_thickness_mm < self.minimum_overall_thickness_mm:
            raise ValueError(
                "maximum_overall_thickness_mm must be at least the minimum"
            )
        if bool(self.cover_exposure_basis) != self.cover_exposure_basis_is_approved:
            raise ValueError(
                "cover exposure reference and approval must be supplied together"
            )
        detailing_values = (
            self.nominal_cover_mm,
            self.nominal_max_aggregate_size_mm,
            self.lower_bottom_bar_direction,
            self.upper_bottom_bar_direction,
            self.footing_bottom_bar_type,
        )
        if any(value is not None for value in detailing_values) and (
            any(value is None for value in detailing_values)
            or not self.permitted_bottom_bar_diameters_mm
            or not self.cover_exposure_basis_is_approved
        ):
            raise ValueError(
                "footing detailing inputs must be supplied as one complete approved set"
            )
        return self


class GravityWorkflowRequestV1(_FrozenModel):
    schema_version: Literal["gravity-workflow-request/v1"] = (
        "gravity-workflow-request/v1"
    )
    workflow_version: Literal["building-gravity-workflow/v1"] = (
        "building-gravity-workflow/v1"
    )
    formula_version: Literal["gravity-load-path/v1"] = "gravity-load-path/v1"
    model_hash: str = Field(pattern=_SHA256_PATTERN)
    load_model_hash: str = Field(pattern=_SHA256_PATTERN)
    building: BuildingModelV1
    loads: LoadModelV1
    slab_design_bases: tuple[GravitySlabDesignBasisV1, ...] = ()
    beam_design_bases: tuple[GravityBeamDesignBasisV1, ...] = ()
    column_design_bases: tuple[GravityColumnDesignBasisV1, ...] = ()
    footing_design_bases: tuple[GravityFootingDesignBasisV1, ...] = ()

    @model_validator(mode="after")
    def validate_identity_and_component_ids(self) -> GravityWorkflowRequestV1:
        if self.model_hash != self.building.accepted_model_hash:
            raise ValueError("model_hash must match building.accepted_model_hash")
        if self.load_model_hash != self.loads.load_model_hash:
            raise ValueError("load_model_hash must match loads.load_model_hash")
        if self.loads.model_hash != self.model_hash:
            raise ValueError("loads.model_hash must match the accepted building")

        expected = {
            "slab": {item.id for item in self.building.panels},
            "beam": {
                item.id for item in self.building.members if item.kind.value == "BEAM"
            },
            "column": {
                item.id for item in self.building.members if item.kind.value == "COLUMN"
            },
            "footing": {item.id for item in self.building.footing_destinations},
        }
        supplied = {
            "slab": [item.panel_id for item in self.slab_design_bases],
            "beam": [item.beam_id for item in self.beam_design_bases],
            "column": [item.column_id for item in self.column_design_bases],
            "footing": [item.footing_id for item in self.footing_design_bases],
        }
        for kind, ids in supplied.items():
            if len(ids) != len(set(ids)):
                raise ValueError(f"duplicate {kind} design basis")
            unknown = set(ids) - expected[kind]
            if unknown:
                raise ValueError(f"unknown {kind} design basis IDs: {sorted(unknown)}")
        return self


class GravityComponentApplicabilityV1(_FrozenModel):
    component_id: str = Field(pattern=_ID_PATTERN)
    kind: GravityComponentKindV1
    canonical_function: str = Field(min_length=1, max_length=256)
    supported_case_id: str = Field(min_length=1, max_length=256)
    required_generated_inputs: tuple[str, ...]
    required_supplied_inputs: tuple[str, ...]
    disposition: GravityPrerequisiteDispositionV1
    hold_reasons: tuple[str, ...] = ()


class ComponentApplicabilityMatrixV1(_FrozenModel):
    schema_version: Literal["component-applicability-matrix/v1"] = (
        "component-applicability-matrix/v1"
    )
    entries: tuple[GravityComponentApplicabilityV1, ...]


class GravityMemberActionV1(_FrozenModel):
    action_id: str = Field(min_length=1, max_length=256)
    component_id: str = Field(pattern=_ID_PATTERN)
    kind: GravityComponentKindV1
    combination_id: Literal["SERVICE_DL_LL", "ULS_1_5_DL_LL"]
    state: Literal["SERVICE", "FACTORED"]
    area_load_kn_m2: float | None = Field(default=None, ge=0)
    line_load_kn_m: float | None = Field(default=None, ge=0)
    moment_knm: float | None = Field(default=None, ge=0)
    shear_kn: float | None = Field(default=None, ge=0)
    axial_kn: float | None = Field(default=None, ge=0)
    source_entry_ids: tuple[str, ...]
    sign_convention: str = Field(min_length=1, max_length=256)

    @model_validator(mode="after")
    def validate_action_shape(self) -> GravityMemberActionV1:
        present = {
            "area": self.area_load_kn_m2 is not None,
            "line": self.line_load_kn_m is not None,
            "moment": self.moment_knm is not None,
            "shear": self.shear_kn is not None,
            "axial": self.axial_kn is not None,
        }
        expected = {
            GravityComponentKindV1.SLAB: {"area"},
            GravityComponentKindV1.BEAM: {"line", "moment", "shear"},
            GravityComponentKindV1.COLUMN: {"axial"},
            GravityComponentKindV1.FOOTING: {"axial"},
        }[self.kind]
        if {name for name, exists in present.items() if exists} != expected:
            raise ValueError(f"{self.kind.value} action fields do not match V1")
        return self


class GravityComponentResultV1(_FrozenModel):
    component_id: str = Field(pattern=_ID_PATTERN)
    kind: GravityComponentKindV1
    canonical_function: str = Field(min_length=1, max_length=256)
    action_ids: tuple[str, ...]
    result_envelope: dict[str, Any]
    result: dict[str, Any] | None = None


class GravityWorkflowResultV1(_FrozenModel):
    schema_version: Literal["gravity-workflow-result/v1"] = "gravity-workflow-result/v1"
    workflow_version: Literal["building-gravity-workflow/v1"] = (
        "building-gravity-workflow/v1"
    )
    formula_version: Literal["gravity-load-path/v1"] = "gravity-load-path/v1"
    model_hash: str = Field(pattern=_SHA256_PATTERN)
    load_model_hash: str = Field(pattern=_SHA256_PATTERN)
    ledger_hash: str = Field(pattern=_SHA256_PATTERN)
    applicability: ComponentApplicabilityMatrixV1
    actions: tuple[GravityMemberActionV1, ...]
    components: tuple[GravityComponentResultV1, ...]
    result_envelope: dict[str, Any]
    limitations: tuple[str, ...]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def workflow_result_hash(self) -> str:
        payload = self.model_dump(mode="json", exclude={"workflow_result_hash"})
        encoded = json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()
