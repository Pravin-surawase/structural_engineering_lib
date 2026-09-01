"""B1A project beam criteria, catalogue, and initial schedule contracts.

These immutable builders freeze caller-owned project choices before candidate
inspection.  Authored fixtures remain explicitly held and cannot become actual
project evidence merely because their hashes are valid.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Literal, Self

from pydantic import Field, model_validator

from structural_lib.services.contracts.common import StrictPublicModel

__all__ = [
    "BeamCriteriaScenarioV1",
    "BeamCriteriaStopPolicyV1",
    "BeamExistingPropertyDraftV1",
    "BeamExistingPropertyV1",
    "BeamLongitudinalLayerV1",
    "BeamLongitudinalStockV1",
    "BeamMemberReinforcementScheduleDraftV1",
    "BeamMemberReinforcementScheduleV1",
    "BeamPropertyCostBasisV1",
    "BeamTransverseStockV1",
    "BeamTransverseZoneV1",
    "ProjectBeamCandidateCatalogueDraftV1",
    "ProjectBeamCandidateCatalogueV1",
    "ProjectBeamCriteriaDraftV1",
    "ProjectBeamCriteriaV1",
    "build_beam_existing_property_v1",
    "build_beam_member_reinforcement_schedule_v1",
    "build_project_beam_candidate_catalogue_v1",
    "build_project_beam_criteria_v1",
]

_SHA = r"^[0-9a-f]{64}$"


def _json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def _digest(value: object) -> str:
    return hashlib.sha256(_json(value).encode("utf-8")).hexdigest()


def _utc(value: datetime, field: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field} must be timezone-aware")
    return value.astimezone(UTC)


class BeamCriteriaScenarioV1(StrictPublicModel):
    scenario_id: str = Field(min_length=1, max_length=160)
    purpose: Literal["STRENGTH", "SERVICEABILITY"]
    selection_ids: tuple[str, ...] = Field(min_length=1)
    action_components: tuple[Literal["P", "V2", "V3", "T", "M2", "M3"], ...] = Field(
        min_length=1, max_length=6
    )
    source_reference: str = Field(min_length=1, max_length=500)

    @model_validator(mode="after")
    def validate_domain(self) -> Self:
        if len(self.selection_ids) != len(set(self.selection_ids)):
            raise ValueError("scenario selection_ids must be unique")
        if len(self.action_components) != len(set(self.action_components)):
            raise ValueError("scenario action_components must be unique")
        if self.purpose == "STRENGTH" and not {"V2", "M3"}.issubset(
            self.action_components
        ):
            raise ValueError("strength scenarios require signed V2 and M3")
        return self


class BeamCriteriaStopPolicyV1(StrictPublicModel):
    maximum_generated_candidates: int = Field(ge=1, le=1_000_000)
    maximum_evaluated_candidates: int = Field(ge=1, le=1_000_000)
    allow_incomplete_shortlist: bool
    incomplete_optimality_claim: Literal[False] = False

    @model_validator(mode="after")
    def validate_limits(self) -> Self:
        if self.maximum_evaluated_candidates > self.maximum_generated_candidates:
            raise ValueError("evaluated candidate bound cannot exceed generated bound")
        return self


class ProjectBeamCriteriaDraftV1(StrictPublicModel):
    criteria_id: str = Field(min_length=1, max_length=160)
    criteria_status: Literal["PROJECT_REVIEWED", "AUTHORED_FIXTURE_HOLD"]
    code_standard: Literal["IS456"] = "IS456"
    code_revision: str = Field(min_length=1, max_length=120)
    source_references: tuple[str, ...] = Field(min_length=1)
    reviewed_by: str | None = Field(default=None, max_length=240)
    strength_scenarios: tuple[BeamCriteriaScenarioV1, ...] = Field(min_length=1)
    service_scenarios: tuple[BeamCriteriaScenarioV1, ...] = ()
    positive_m3_tension_face: Literal["TOP", "BOTTOM"]
    negative_m3_tension_face: Literal["TOP", "BOTTOM"]
    max_abs_axial_kn: float = Field(ge=0)
    max_abs_minor_shear_kn: float = Field(ge=0)
    max_abs_minor_moment_knm: float = Field(ge=0)
    torsion_disposition: Literal["MANDATORY", "NOT_APPLICABLE_WITH_BASIS"]
    excluded_effects: tuple[str, ...]
    mandatory_checks: tuple[
        Literal[
            "FLEXURE",
            "SHEAR",
            "TORSION",
            "SERVICEABILITY",
            "DETAILING",
            "ANCHORAGE",
            "LAP",
            "SUPPORT",
            "AGGREGATE",
            "CONSTRUCTABILITY",
        ],
        ...,
    ] = Field(min_length=1)
    scope_dispositions: tuple[tuple[str, Literal["MANDATORY", "HELD", "N_A"]], ...]
    sensitivity_scenarios: tuple[str, ...] = Field(min_length=1)
    objectives: tuple[Literal["STEEL_MASS", "COST", "CONGESTION"], ...] = Field(
        min_length=1
    )
    tie_breaks: tuple[
        Literal["LOWER_UTILIZATION", "FEWER_BAR_MARKS", "PROPERTY_ID"], ...
    ] = Field(min_length=1)
    stop_policy: BeamCriteriaStopPolicyV1
    serviceability_mandatory: bool
    hidden_fallbacks_allowed: Literal[False] = False
    declared_at_utc: datetime
    candidate_inspection_started_at_utc: datetime | None = None
    assumptions: tuple[str, ...] = Field(min_length=1)
    limitations: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_criteria(self) -> Self:
        declared = _utc(self.declared_at_utc, "declared_at_utc")
        inspected = self.candidate_inspection_started_at_utc
        if (
            inspected is not None
            and _utc(inspected, "candidate_inspection_started_at_utc") < declared
        ):
            raise ValueError("criteria must be declared before candidate inspection")
        if self.criteria_status == "PROJECT_REVIEWED" and not self.reviewed_by:
            raise ValueError("project-reviewed criteria require reviewer identity")
        if self.positive_m3_tension_face == self.negative_m3_tension_face:
            raise ValueError("opposite M3 signs require opposite physical faces")
        if any(item.purpose != "STRENGTH" for item in self.strength_scenarios):
            raise ValueError("strength_scenarios may contain only STRENGTH rows")
        if any(item.purpose != "SERVICEABILITY" for item in self.service_scenarios):
            raise ValueError("service_scenarios may contain only SERVICEABILITY rows")
        ids = tuple(
            item.scenario_id
            for item in self.strength_scenarios + self.service_scenarios
        )
        if len(ids) != len(set(ids)):
            raise ValueError("criteria scenario IDs must be unique")
        if self.serviceability_mandatory and not self.service_scenarios:
            raise ValueError("mandatory serviceability requires service scenarios")
        for values, name in (
            (self.source_references, "source_references"),
            (self.mandatory_checks, "mandatory_checks"),
            (self.sensitivity_scenarios, "sensitivity_scenarios"),
            (self.objectives, "objectives"),
            (self.tie_breaks, "tie_breaks"),
        ):
            if len(values) != len(set(values)):
                raise ValueError(f"{name} must be unique")
        scope_names = tuple(name for name, _value in self.scope_dispositions)
        if len(scope_names) != len(set(scope_names)):
            raise ValueError("scope disposition names must be unique")
        if self.torsion_disposition == "MANDATORY" and "TORSION" not in (
            self.mandatory_checks
        ):
            raise ValueError("mandatory torsion must appear in mandatory_checks")
        return self


class ProjectBeamCriteriaV1(ProjectBeamCriteriaDraftV1):
    schema_version: Literal["project-beam-criteria/v1"] = "project-beam-criteria/v1"
    criteria_sha256: str = Field(pattern=_SHA)

    @model_validator(mode="after")
    def validate_digest(self) -> Self:
        expected = _digest(self.model_dump(mode="json", exclude={"criteria_sha256"}))
        if self.criteria_sha256 != expected:
            raise ValueError("criteria_sha256 does not match canonical criteria")
        return self


def build_project_beam_criteria_v1(
    draft: ProjectBeamCriteriaDraftV1, /
) -> ProjectBeamCriteriaV1:
    json_payload = {
        "schema_version": "project-beam-criteria/v1",
        **draft.model_dump(mode="json"),
    }
    return ProjectBeamCriteriaV1.model_validate(
        {
            "schema_version": "project-beam-criteria/v1",
            **draft.model_dump(mode="python"),
            "criteria_sha256": _digest(json_payload),
        }
    )


class BeamExistingPropertyDraftV1(StrictPublicModel):
    property_id: str = Field(min_length=1, max_length=160)
    source_property_name: str = Field(min_length=1, max_length=160)
    width_t2_mm: float = Field(gt=0, le=2000)
    depth_t3_mm: float = Field(gt=0, le=3000)
    concrete_material: str = Field(min_length=1, max_length=160)
    fck_nmm2: float = Field(ge=15, le=40)
    longitudinal_rebar_material: str = Field(min_length=1, max_length=160)
    transverse_rebar_material: str = Field(min_length=1, max_length=160)
    fy_longitudinal_nmm2: float = Field(ge=250, le=500)
    fy_transverse_nmm2: float = Field(ge=250, le=500)
    modifiers: tuple[tuple[str, float], ...] = Field(min_length=1)
    rebar_type: Literal["BEAM"] = "BEAM"
    auto_select_state: Literal["NOT_AUTO_SELECT", "AUTO_SELECT_HELD"]
    source_reference: str = Field(min_length=1, max_length=500)

    @model_validator(mode="after")
    def validate_modifiers(self) -> Self:
        names = tuple(name for name, _value in self.modifiers)
        if names != tuple(sorted(set(names))):
            raise ValueError("property modifiers must have unique sorted names")
        if any(value <= 0 for _name, value in self.modifiers):
            raise ValueError("property modifiers must be positive")
        return self


class BeamExistingPropertyV1(BeamExistingPropertyDraftV1):
    property_sha256: str = Field(pattern=_SHA)

    @model_validator(mode="after")
    def validate_digest(self) -> Self:
        expected = _digest(self.model_dump(mode="json", exclude={"property_sha256"}))
        if self.property_sha256 != expected:
            raise ValueError("property_sha256 does not match canonical property")
        return self


def build_beam_existing_property_v1(
    draft: BeamExistingPropertyDraftV1, /
) -> BeamExistingPropertyV1:
    payload = draft.model_dump(mode="json")
    return BeamExistingPropertyV1.model_validate(
        {**draft.model_dump(mode="python"), "property_sha256": _digest(payload)}
    )


class BeamLongitudinalStockV1(StrictPublicModel):
    diameter_mm: float = Field(ge=8, le=40)
    grade_nmm2: float = Field(ge=250, le=500)
    stock_revision: str = Field(min_length=1, max_length=120)


class BeamTransverseStockV1(StrictPublicModel):
    diameter_mm: float = Field(ge=6, le=20)
    grade_nmm2: float = Field(ge=250, le=500)
    permitted_legs: tuple[int, ...] = Field(min_length=1)
    permitted_spacing_mm: tuple[float, ...] = Field(min_length=1)
    stock_revision: str = Field(min_length=1, max_length=120)

    @model_validator(mode="after")
    def validate_stock(self) -> Self:
        if any(value < 2 or value > 8 for value in self.permitted_legs):
            raise ValueError("stirrup legs must be within [2, 8]")
        if any(value <= 0 for value in self.permitted_spacing_mm):
            raise ValueError("stirrup spacing must be positive")
        if tuple(sorted(set(self.permitted_legs))) != self.permitted_legs:
            raise ValueError("permitted stirrup legs must be unique and sorted")
        if tuple(sorted(set(self.permitted_spacing_mm))) != (self.permitted_spacing_mm):
            raise ValueError("permitted stirrup spacing must be unique and sorted")
        return self


class BeamPropertyCostBasisV1(StrictPublicModel):
    currency: str = Field(min_length=3, max_length=12)
    concrete_per_m3: float = Field(ge=0)
    longitudinal_steel_per_kg: float = Field(ge=0)
    transverse_steel_per_kg: float = Field(ge=0)
    formwork_per_m2: float = Field(ge=0)
    cost_revision: str = Field(min_length=1, max_length=120)
    exclusions: tuple[str, ...] = Field(min_length=1)


class ProjectBeamCandidateCatalogueDraftV1(StrictPublicModel):
    catalogue_id: str = Field(min_length=1, max_length=160)
    catalogue_status: Literal["PROJECT_REVIEWED", "AUTHORED_FIXTURE_HOLD"]
    criteria_sha256: str = Field(pattern=_SHA)
    catalogue_revision: str = Field(min_length=1, max_length=120)
    existing_beam_properties: tuple[BeamExistingPropertyV1, ...] = Field(min_length=1)
    longitudinal_stock: tuple[BeamLongitudinalStockV1, ...] = Field(min_length=1)
    transverse_stock: tuple[BeamTransverseStockV1, ...] = Field(min_length=1)
    cost_basis: BeamPropertyCostBasisV1
    source_references: tuple[str, ...] = Field(min_length=1)
    reviewed_by: str | None = Field(default=None, max_length=240)
    declared_at_utc: datetime
    candidate_generation_started_at_utc: datetime | None = None
    limitations: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_catalogue(self) -> Self:
        declared = _utc(self.declared_at_utc, "declared_at_utc")
        started = self.candidate_generation_started_at_utc
        if (
            started is not None
            and _utc(started, "candidate_generation_started_at_utc") < declared
        ):
            raise ValueError("catalogue must be declared before candidate generation")
        if self.catalogue_status == "PROJECT_REVIEWED" and not self.reviewed_by:
            raise ValueError("project-reviewed catalogue requires reviewer identity")
        property_ids = tuple(item.property_id for item in self.existing_beam_properties)
        if len(property_ids) != len(set(property_ids)):
            raise ValueError("existing beam property IDs must be unique")
        longitudinal = tuple(
            (item.diameter_mm, item.grade_nmm2) for item in self.longitudinal_stock
        )
        transverse = tuple(
            (item.diameter_mm, item.grade_nmm2) for item in self.transverse_stock
        )
        if longitudinal != tuple(sorted(set(longitudinal))):
            raise ValueError("longitudinal stock must be unique and sorted")
        if transverse != tuple(sorted(set(transverse))):
            raise ValueError("transverse stock must be unique and sorted")
        if len(self.source_references) != len(set(self.source_references)):
            raise ValueError("catalogue source references must be unique")
        return self


class ProjectBeamCandidateCatalogueV1(ProjectBeamCandidateCatalogueDraftV1):
    schema_version: Literal["project-beam-candidate-catalogue/v1"] = (
        "project-beam-candidate-catalogue/v1"
    )
    catalogue_sha256: str = Field(pattern=_SHA)

    @model_validator(mode="after")
    def validate_digest(self) -> Self:
        expected = _digest(self.model_dump(mode="json", exclude={"catalogue_sha256"}))
        if self.catalogue_sha256 != expected:
            raise ValueError("catalogue_sha256 does not match canonical catalogue")
        return self


def build_project_beam_candidate_catalogue_v1(
    draft: ProjectBeamCandidateCatalogueDraftV1,
    /,
    *,
    criteria: ProjectBeamCriteriaV1,
) -> ProjectBeamCandidateCatalogueV1:
    if draft.criteria_sha256 != criteria.criteria_sha256:
        raise ValueError("catalogue criteria identity does not match supplied criteria")
    json_payload = {
        "schema_version": "project-beam-candidate-catalogue/v1",
        **draft.model_dump(mode="json"),
    }
    return ProjectBeamCandidateCatalogueV1.model_validate(
        {
            "schema_version": "project-beam-candidate-catalogue/v1",
            **draft.model_dump(mode="python"),
            "catalogue_sha256": _digest(json_payload),
        }
    )


class BeamLongitudinalLayerV1(StrictPublicModel):
    face: Literal["TOP", "BOTTOM"]
    layer_index: Literal[1] = 1
    extent: Literal["FULL_SPAN"] = "FULL_SPAN"
    bar_count: int = Field(ge=2, le=20)
    bar_diameter_mm: float = Field(ge=8, le=40)
    grade_nmm2: float = Field(ge=250, le=500)


class BeamTransverseZoneV1(StrictPublicModel):
    zone_id: str = Field(min_length=1, max_length=120)
    start_mm: float = Field(ge=0)
    end_mm: float = Field(gt=0)
    stirrup_diameter_mm: float = Field(ge=6, le=20)
    grade_nmm2: float = Field(ge=250, le=500)
    legs: int = Field(ge=2, le=8)
    spacing_mm: float = Field(gt=0)

    @model_validator(mode="after")
    def validate_interval(self) -> Self:
        if self.end_mm <= self.start_mm:
            raise ValueError("transverse zone end must follow start")
        return self


class BeamMemberReinforcementScheduleDraftV1(StrictPublicModel):
    schedule_id: str = Field(min_length=1, max_length=160)
    schedule_status: Literal["COMPLETE", "AUTHORED_FIXTURE_HOLD"]
    schedule_revision: str = Field(min_length=1, max_length=120)
    member_id: str = Field(min_length=1, max_length=160)
    span_mm: float = Field(gt=0)
    existing_property_id: str = Field(min_length=1, max_length=160)
    criteria_sha256: str = Field(pattern=_SHA)
    catalogue_sha256: str = Field(pattern=_SHA)
    longitudinal_layers: tuple[BeamLongitudinalLayerV1, ...] = Field(
        min_length=2, max_length=2
    )
    transverse_zones: tuple[BeamTransverseZoneV1, ...] = Field(min_length=1)
    side_face_disposition: Literal["NOT_APPLICABLE", "HELD_UNTYPED"]
    curtailment_supported: Literal[False] = False
    mixed_longitudinal_diameters_supported: Literal[False] = False
    multiple_longitudinal_layers_supported: Literal[False] = False
    source_references: tuple[str, ...] = Field(min_length=1)
    limitations: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_schedule(self) -> Self:
        if {layer.face for layer in self.longitudinal_layers} != {"TOP", "BOTTOM"}:
            raise ValueError("schedule requires exactly one TOP and one BOTTOM layer")
        ordered = tuple(sorted(self.transverse_zones, key=lambda item: item.start_mm))
        if ordered != self.transverse_zones:
            raise ValueError("transverse zones must be ordered by start")
        if ordered[0].start_mm != 0 or ordered[-1].end_mm != self.span_mm:
            raise ValueError("transverse zones must cover the full member span")
        if any(
            left.end_mm != right.start_mm
            for left, right in zip(ordered, ordered[1:], strict=False)
        ):
            raise ValueError("transverse zones must be contiguous without overlap")
        if len({zone.zone_id for zone in ordered}) != len(ordered):
            raise ValueError("transverse zone IDs must be unique")
        return self


class BeamMemberReinforcementScheduleV1(BeamMemberReinforcementScheduleDraftV1):
    schema_version: Literal["beam-member-reinforcement-schedule/v1"] = (
        "beam-member-reinforcement-schedule/v1"
    )
    schedule_sha256: str = Field(pattern=_SHA)

    @model_validator(mode="after")
    def validate_digest(self) -> Self:
        expected = _digest(self.model_dump(mode="json", exclude={"schedule_sha256"}))
        if self.schedule_sha256 != expected:
            raise ValueError("schedule_sha256 does not match canonical schedule")
        return self


def build_beam_member_reinforcement_schedule_v1(
    draft: BeamMemberReinforcementScheduleDraftV1,
    /,
    *,
    criteria: ProjectBeamCriteriaV1,
    catalogue: ProjectBeamCandidateCatalogueV1,
) -> BeamMemberReinforcementScheduleV1:
    if draft.criteria_sha256 != criteria.criteria_sha256:
        raise ValueError("schedule criteria identity mismatch")
    if draft.catalogue_sha256 != catalogue.catalogue_sha256:
        raise ValueError("schedule catalogue identity mismatch")
    properties = {item.property_id: item for item in catalogue.existing_beam_properties}
    property_value = properties.get(draft.existing_property_id)
    if property_value is None:
        raise ValueError("schedule property is not in the permitted catalogue")
    longitudinal_stock = {
        (item.diameter_mm, item.grade_nmm2) for item in catalogue.longitudinal_stock
    }
    transverse_stock = {
        (
            item.diameter_mm,
            item.grade_nmm2,
            item.permitted_legs,
            item.permitted_spacing_mm,
        )
        for item in catalogue.transverse_stock
    }
    if any(
        (layer.bar_diameter_mm, layer.grade_nmm2) not in longitudinal_stock
        for layer in draft.longitudinal_layers
    ):
        raise ValueError("schedule longitudinal layer is outside approved stock")
    for zone in draft.transverse_zones:
        if not any(
            zone.stirrup_diameter_mm == diameter
            and zone.grade_nmm2 == grade
            and zone.legs in legs
            and zone.spacing_mm in spacings
            for diameter, grade, legs, spacings in transverse_stock
        ):
            raise ValueError("schedule transverse zone is outside approved stock")
    if any(
        layer.grade_nmm2 != property_value.fy_longitudinal_nmm2
        for layer in draft.longitudinal_layers
    ) or any(
        zone.grade_nmm2 != property_value.fy_transverse_nmm2
        for zone in draft.transverse_zones
    ):
        raise ValueError("schedule grades must match the permitted property materials")
    json_payload = {
        "schema_version": "beam-member-reinforcement-schedule/v1",
        **draft.model_dump(mode="json"),
    }
    return BeamMemberReinforcementScheduleV1.model_validate(
        {
            "schema_version": "beam-member-reinforcement-schedule/v1",
            **draft.model_dump(mode="python"),
            "schedule_sha256": _digest(json_payload),
        }
    )
