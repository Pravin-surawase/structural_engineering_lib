"""Common W3 beam-candidate feasibility and composition owner.

The evaluator binds one sealed signed action row to one exact B1A schedule,
rebuilds the accepted supplied-beam request from that serialized schedule, and
is the only service in the W3 candidate path allowed to emit feasibility.
Candidate generators remain recommendations and never bypass this module.
"""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any, Literal, Self

from pydantic import Field, model_validator

from structural_lib.core.analysis_contracts import BeamActionRowV1
from structural_lib.services.beam_audit import canonical_beam_action_row_sha256_v1
from structural_lib.services.beam_project_contracts import (
    BeamExistingPropertyV1,
    BeamLongitudinalLayerV1,
    BeamMemberReinforcementScheduleV1,
    BeamTransverseZoneV1,
    ProjectBeamCandidateCatalogueV1,
    ProjectBeamCriteriaV1,
)
from structural_lib.services.contracts.beam import (
    CentroidCoverDepthRequestV1,
    IS456ReinforcementMaterialsV1,
    MemberIdentityV1,
)
from structural_lib.services.contracts.beam_supplied_check import (
    BeamBarLayersV2,
    BeamReinforcementSelectionV2,
    BeamSuppliedCheckActionsV2,
    BeamSuppliedCheckRequestV2,
    BeamSuppliedCheckSectionV2,
    BeamSuppliedReinforcementV2,
    BeamSupportBasisV2,
)
from structural_lib.services.contracts.common import StrictPublicModel
from structural_lib.services.supplied_beam_check import check_supplied_beam_v2

__all__ = [
    "BeamCandidateCheckEvidenceV2",
    "BeamCandidateCheckResultV2",
    "BeamCandidateCompositionV2",
    "BeamCandidateDefinitionDraftV2",
    "BeamCandidateDefinitionV2",
    "BeamCandidateEvaluationResultV2",
    "build_beam_candidate_definition_v2",
    "check_beam_candidate_composition_v2",
    "evaluate_beam_candidate_v2",
]

_SHA = r"^[0-9a-f]{64}$"
_DENSITY_KG_PER_MM3 = 7850.0e-9
_MANDATORY_CHECK = Literal[
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
]
CandidateVerdict = Literal["PASS", "FAIL", "HOLD"]


def _json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
        default=(
            lambda item: (
                item.model_dump(mode="json")
                if isinstance(item, StrictPublicModel)
                else _raise_json_type(item)
            )
        ),
    )


def _raise_json_type(value: object):
    raise TypeError(f"{type(value).__name__} is not canonically JSON serializable")


def _digest(value: object) -> str:
    return hashlib.sha256(_json(value).encode("utf-8")).hexdigest()


def _validated(model: type[StrictPublicModel], value: StrictPublicModel):
    return model.model_validate(value.model_dump(mode="python"))


class BeamCandidateCheckEvidenceV2(StrictPublicModel):
    """Caller-owned result for a mandatory domain not owned by B1B."""

    check: _MANDATORY_CHECK
    status: CandidateVerdict
    scenario_ids: tuple[str, ...] = ()
    source_references: tuple[str, ...] = Field(min_length=1)
    basis: str = Field(min_length=1, max_length=1000)

    @model_validator(mode="after")
    def validate_evidence(self) -> Self:
        if len(self.scenario_ids) != len(set(self.scenario_ids)):
            raise ValueError("check evidence scenario_ids must be unique")
        if len(self.source_references) != len(set(self.source_references)):
            raise ValueError("check evidence source_references must be unique")
        return self


class BeamCandidateDefinitionDraftV2(StrictPublicModel):
    """Exact row-bound candidate before its canonical identity is sealed."""

    candidate_id: str = Field(min_length=1, max_length=160)
    member_identity: MemberIdentityV1
    action_row: BeamActionRowV1
    strength_scenario_id: str = Field(min_length=1, max_length=160)
    primary_tension_face: Literal["TOP", "BOTTOM"]
    existing_property_id: str = Field(min_length=1, max_length=160)
    existing_property_sha256: str = Field(pattern=_SHA)
    criteria_sha256: str = Field(pattern=_SHA)
    catalogue_sha256: str = Field(pattern=_SHA)
    schedule: BeamMemberReinforcementScheduleV1
    clear_cover_mm: float = Field(gt=0, le=100)
    nominal_max_aggregate_size_mm: float = Field(gt=0, le=80)
    support: BeamSupportBasisV2 | None = None
    service_scenario_ids: tuple[str, ...] = ()
    supplemental_checks: tuple[BeamCandidateCheckEvidenceV2, ...] = ()
    bar_type: Literal["deformed", "plain"] = "deformed"
    has_standard_bend_at_start: bool
    has_standard_bend_at_end: bool
    side_face_disposition: Literal["NOT_APPLICABLE", "HELD_UNTYPED"]
    source_references: tuple[str, ...] = Field(min_length=1)
    limitations: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_candidate_shape(self) -> Self:
        if len(self.service_scenario_ids) != len(set(self.service_scenario_ids)):
            raise ValueError("service_scenario_ids must be unique")
        checks = tuple(item.check for item in self.supplemental_checks)
        if len(checks) != len(set(checks)):
            raise ValueError("supplemental check names must be unique")
        if len(self.source_references) != len(set(self.source_references)):
            raise ValueError("candidate source references must be unique")
        return self


class BeamCandidateDefinitionV2(BeamCandidateDefinitionDraftV2):
    schema_version: Literal["beam-candidate-definition/v2"] = (
        "beam-candidate-definition/v2"
    )
    candidate_sha256: str = Field(pattern=_SHA)

    @model_validator(mode="after")
    def validate_digest(self) -> Self:
        expected = _digest(self.model_dump(mode="json", exclude={"candidate_sha256"}))
        if self.candidate_sha256 != expected:
            raise ValueError("candidate_sha256 does not match canonical candidate")
        return self


class BeamCandidateCompositionV2(StrictPublicModel):
    """Independent quantities recomputed only from the serialized candidate."""

    schema_version: Literal["beam-candidate-composition/v2"] = (
        "beam-candidate-composition/v2"
    )
    status: CandidateVerdict
    primary_tension_face: Literal["TOP", "BOTTOM"]
    top_area_mm2: float = Field(gt=0)
    bottom_area_mm2: float = Field(gt=0)
    effective_depth_mm: float = Field(gt=0)
    top_centroid_cover_mm: float = Field(gt=0)
    bottom_centroid_cover_mm: float = Field(gt=0)
    top_horizontal_clear_spacing_mm: float
    bottom_horizontal_clear_spacing_mm: float
    between_faces_clear_spacing_mm: float
    longitudinal_mass_kg: float = Field(gt=0)
    transverse_mass_kg: float = Field(gt=0)
    total_steel_mass_kg: float = Field(gt=0)
    stirrup_count: int = Field(ge=2)
    concrete_volume_m3: float = Field(gt=0)
    formwork_area_m2: float = Field(gt=0)
    total_cost: float = Field(ge=0)
    currency: str = Field(min_length=3, max_length=12)
    congestion_score: float = Field(gt=0)
    bar_mark_count: int = Field(ge=3)
    quantity_basis: tuple[str, ...] = Field(min_length=1)
    issues: tuple[str, ...]
    composition_sha256: str = Field(pattern=_SHA)

    @model_validator(mode="after")
    def validate_digest(self) -> Self:
        expected = _digest(self.model_dump(mode="json", exclude={"composition_sha256"}))
        if self.composition_sha256 != expected:
            raise ValueError("composition_sha256 does not match composition")
        if self.status == "PASS" and self.issues:
            raise ValueError("passing composition cannot contain issues")
        if self.status != "PASS" and not self.issues:
            raise ValueError("non-passing composition requires issues")
        return self


class BeamCandidateCheckResultV2(StrictPublicModel):
    check: _MANDATORY_CHECK
    status: CandidateVerdict
    owner: Literal["SUPPLIED_BEAM_V2", "SUPPLEMENTAL_EVIDENCE", "B1B_BINDING"]
    scenario_ids: tuple[str, ...] = ()
    source_references: tuple[str, ...] = ()
    basis: str = Field(min_length=1, max_length=1000)


class BeamCandidateEvaluationResultV2(StrictPublicModel):
    """Terminal B1B verdict and immutable evidence identity."""

    schema_version: Literal["beam-candidate-evaluation/v2"] = (
        "beam-candidate-evaluation/v2"
    )
    candidate_id: str
    candidate_sha256: str = Field(pattern=_SHA)
    criteria_sha256: str = Field(pattern=_SHA)
    catalogue_sha256: str = Field(pattern=_SHA)
    schedule_sha256: str = Field(pattern=_SHA)
    action_row_sha256: str = Field(pattern=_SHA)
    primary_tension_face: Literal["TOP", "BOTTOM"]
    verdict: CandidateVerdict
    checks: tuple[BeamCandidateCheckResultV2, ...] = Field(min_length=1)
    supplied_check_sha256: str = Field(pattern=_SHA)
    supplied_check: dict[str, Any]
    composition: BeamCandidateCompositionV2
    fixture_evidence_held: bool
    limitations: tuple[str, ...] = Field(min_length=1)
    evaluation_sha256: str = Field(pattern=_SHA)

    @model_validator(mode="after")
    def validate_result(self) -> Self:
        expected = _digest(self.model_dump(mode="json", exclude={"evaluation_sha256"}))
        if self.evaluation_sha256 != expected:
            raise ValueError("evaluation_sha256 does not match evaluation")
        names = tuple(item.check for item in self.checks)
        if len(names) != len(set(names)):
            raise ValueError("evaluation check names must be unique")
        if self.verdict == "PASS" and (
            self.fixture_evidence_held
            or self.composition.status != "PASS"
            or any(item.status != "PASS" for item in self.checks)
        ):
            raise ValueError("PASS requires complete non-fixture passing evidence")
        return self


def _property(
    candidate: BeamCandidateDefinitionDraftV2,
    catalogue: ProjectBeamCandidateCatalogueV1,
) -> BeamExistingPropertyV1:
    properties = {item.property_id: item for item in catalogue.existing_beam_properties}
    value = properties.get(candidate.existing_property_id)
    if value is None:
        raise ValueError("candidate property is not in the permitted catalogue")
    if value.property_sha256 != candidate.existing_property_sha256:
        raise ValueError("candidate existing-property identity mismatch")
    return value


def _expected_face(row: BeamActionRowV1, criteria: ProjectBeamCriteriaV1) -> str:
    return (
        criteria.positive_m3_tension_face
        if row.m3_knm >= 0
        else criteria.negative_m3_tension_face
    )


def build_beam_candidate_definition_v2(
    draft: BeamCandidateDefinitionDraftV2,
    /,
    *,
    criteria: ProjectBeamCriteriaV1,
    catalogue: ProjectBeamCandidateCatalogueV1,
) -> BeamCandidateDefinitionV2:
    """Bind one exact schedule and sealed signed row to the accepted B1A owners."""

    criteria = _validated(ProjectBeamCriteriaV1, criteria)
    catalogue = _validated(ProjectBeamCandidateCatalogueV1, catalogue)
    schedule = _validated(BeamMemberReinforcementScheduleV1, draft.schedule)
    if catalogue.criteria_sha256 != criteria.criteria_sha256:
        raise ValueError("catalogue criteria identity mismatch")
    if draft.criteria_sha256 != criteria.criteria_sha256:
        raise ValueError("candidate criteria identity mismatch")
    if draft.catalogue_sha256 != catalogue.catalogue_sha256:
        raise ValueError("candidate catalogue identity mismatch")
    if schedule.criteria_sha256 != criteria.criteria_sha256:
        raise ValueError("candidate schedule criteria identity mismatch")
    if schedule.catalogue_sha256 != catalogue.catalogue_sha256:
        raise ValueError("candidate schedule catalogue identity mismatch")
    if schedule.member_id != draft.member_identity.member_id:
        raise ValueError("candidate member and schedule member differ")
    if draft.action_row.member_id != draft.member_identity.member_id:
        raise ValueError("candidate member and action-row member differ")
    if draft.member_identity.case_id != draft.action_row.selection_id:
        raise ValueError("candidate case identity must equal action-row selection_id")
    if canonical_beam_action_row_sha256_v1(draft.action_row) != (
        draft.action_row.row_sha256
    ):
        raise ValueError("action-row digest does not match the sealed signed row")
    scenarios = {item.scenario_id: item for item in criteria.strength_scenarios}
    scenario = scenarios.get(draft.strength_scenario_id)
    if scenario is None or draft.action_row.selection_id not in scenario.selection_ids:
        raise ValueError("action row is outside the declared strength scenario")
    if draft.primary_tension_face != _expected_face(draft.action_row, criteria):
        raise ValueError("primary tension face disagrees with signed M3 criteria")
    expected_service = tuple(item.scenario_id for item in criteria.service_scenarios)
    if draft.service_scenario_ids != expected_service:
        raise ValueError("candidate must bind the complete ordered service domain")
    property_value = _property(draft, catalogue)
    if schedule.existing_property_id != property_value.property_id:
        raise ValueError("candidate schedule and property identity differ")
    if draft.side_face_disposition != schedule.side_face_disposition:
        raise ValueError("candidate and schedule side-face dispositions differ")
    payload = {
        "schema_version": "beam-candidate-definition/v2",
        **draft.model_dump(mode="json"),
    }
    return BeamCandidateDefinitionV2.model_validate(
        {
            "schema_version": "beam-candidate-definition/v2",
            **draft.model_dump(mode="python"),
            "schedule": schedule,
            "candidate_sha256": _digest(payload),
        }
    )


def _face_layer(
    schedule: BeamMemberReinforcementScheduleV1, face: Literal["TOP", "BOTTOM"]
) -> BeamLongitudinalLayerV1:
    return next(item for item in schedule.longitudinal_layers if item.face == face)


def _zone_at(
    schedule: BeamMemberReinforcementScheduleV1, station_mm: float
) -> BeamTransverseZoneV1:
    if not 0 <= station_mm <= schedule.span_mm:
        raise ValueError("action-row station is outside the schedule span")
    for index, zone in enumerate(schedule.transverse_zones):
        if zone.start_mm <= station_mm < zone.end_mm or (
            index == len(schedule.transverse_zones) - 1 and station_mm == zone.end_mm
        ):
            return zone
    raise ValueError("action-row station is not covered by a transverse zone")


def _bar_area(layer: BeamLongitudinalLayerV1) -> float:
    return layer.bar_count * math.pi * layer.bar_diameter_mm**2 / 4.0


def _horizontal_clear_spacing(
    layer: BeamLongitudinalLayerV1,
    *,
    width_mm: float,
    cover_mm: float,
    stirrup_diameter_mm: float,
) -> float:
    available_centres = width_mm - 2.0 * (
        cover_mm + stirrup_diameter_mm + layer.bar_diameter_mm / 2.0
    )
    return available_centres / (layer.bar_count - 1) - layer.bar_diameter_mm


def check_beam_candidate_composition_v2(
    candidate: BeamCandidateDefinitionV2,
    /,
    *,
    catalogue: ProjectBeamCandidateCatalogueV1,
) -> BeamCandidateCompositionV2:
    """Independently recompute geometry, quantities, and cost from the candidate."""

    candidate = _validated(BeamCandidateDefinitionV2, candidate)
    catalogue = _validated(ProjectBeamCandidateCatalogueV1, catalogue)
    property_value = _property(candidate, catalogue)
    schedule = candidate.schedule
    top = _face_layer(schedule, "TOP")
    bottom = _face_layer(schedule, "BOTTOM")
    active_zone = _zone_at(schedule, candidate.action_row.object_station_mm)
    top_centroid = (
        candidate.clear_cover_mm
        + active_zone.stirrup_diameter_mm
        + top.bar_diameter_mm / 2.0
    )
    bottom_centroid = (
        candidate.clear_cover_mm
        + active_zone.stirrup_diameter_mm
        + bottom.bar_diameter_mm / 2.0
    )
    effective_depth = property_value.depth_t3_mm - (
        top_centroid if candidate.primary_tension_face == "TOP" else bottom_centroid
    )
    top_clear = _horizontal_clear_spacing(
        top,
        width_mm=property_value.width_t2_mm,
        cover_mm=candidate.clear_cover_mm,
        stirrup_diameter_mm=active_zone.stirrup_diameter_mm,
    )
    bottom_clear = _horizontal_clear_spacing(
        bottom,
        width_mm=property_value.width_t2_mm,
        cover_mm=candidate.clear_cover_mm,
        stirrup_diameter_mm=active_zone.stirrup_diameter_mm,
    )
    between_faces = (
        property_value.depth_t3_mm
        - top_centroid
        - bottom_centroid
        - top.bar_diameter_mm / 2.0
        - bottom.bar_diameter_mm / 2.0
    )
    top_area = _bar_area(top)
    bottom_area = _bar_area(bottom)
    longitudinal_mass = (
        (top_area + bottom_area) * schedule.span_mm * _DENSITY_KG_PER_MM3
    )
    stirrup_count = 1 + sum(
        math.ceil((zone.end_mm - zone.start_mm) / zone.spacing_mm)
        for zone in schedule.transverse_zones
    )
    transverse_mass = 0.0
    for zone in schedule.transverse_zones:
        zone_spaces = math.ceil((zone.end_mm - zone.start_mm) / zone.spacing_mm)
        zone_count = zone_spaces + (1 if zone is schedule.transverse_zones[0] else 0)
        centre_cover = candidate.clear_cover_mm + zone.stirrup_diameter_mm / 2.0
        perimeter_mm = 2.0 * (
            property_value.width_t2_mm
            - 2.0 * centre_cover
            + property_value.depth_t3_mm
            - 2.0 * centre_cover
        )
        transverse_mass += (
            zone_count
            * zone.legs
            / 2.0
            * perimeter_mm
            * math.pi
            * zone.stirrup_diameter_mm**2
            / 4.0
            * _DENSITY_KG_PER_MM3
        )
    span_m = schedule.span_mm / 1000.0
    width_m = property_value.width_t2_mm / 1000.0
    depth_m = property_value.depth_t3_mm / 1000.0
    concrete_volume = width_m * depth_m * span_m
    formwork_area = (width_m + 2.0 * depth_m) * span_m
    cost = catalogue.cost_basis
    total_cost = (
        concrete_volume * cost.concrete_per_m3
        + longitudinal_mass * cost.longitudinal_steel_per_kg
        + transverse_mass * cost.transverse_steel_per_kg
        + formwork_area * cost.formwork_per_m2
    )
    issues: list[str] = []
    status: CandidateVerdict = "PASS"
    if min(top_clear, bottom_clear) <= 0:
        issues.append("longitudinal bars do not fit within the section width")
        status = "FAIL"
    if between_faces <= 0:
        issues.append("top and bottom longitudinal groups overlap")
        status = "FAIL"
    if effective_depth <= 0:
        issues.append("primary layer centroid leaves no positive effective depth")
        status = "FAIL"
    if any(zone.legs != 2 for zone in schedule.transverse_zones):
        issues.append(
            "transverse mass is held because multi-leg link geometry is not typed"
        )
        if status != "FAIL":
            status = "HOLD"
    total_mass = longitudinal_mass + transverse_mass
    congestion = top.bar_count + bottom.bar_count + stirrup_count / max(span_m, 1e-9)
    payload: dict[str, Any] = {
        "schema_version": "beam-candidate-composition/v2",
        "status": status,
        "primary_tension_face": candidate.primary_tension_face,
        "top_area_mm2": top_area,
        "bottom_area_mm2": bottom_area,
        "effective_depth_mm": effective_depth,
        "top_centroid_cover_mm": top_centroid,
        "bottom_centroid_cover_mm": bottom_centroid,
        "top_horizontal_clear_spacing_mm": top_clear,
        "bottom_horizontal_clear_spacing_mm": bottom_clear,
        "between_faces_clear_spacing_mm": between_faces,
        "longitudinal_mass_kg": longitudinal_mass,
        "transverse_mass_kg": transverse_mass,
        "total_steel_mass_kg": total_mass,
        "stirrup_count": stirrup_count,
        "concrete_volume_m3": concrete_volume,
        "formwork_area_m2": formwork_area,
        "total_cost": total_cost,
        "currency": cost.currency,
        "congestion_score": congestion,
        "bar_mark_count": 2 + len(schedule.transverse_zones),
        "quantity_basis": (
            "Longitudinal layers are full-span with no curtailment or lap allowance.",
            "Two-leg transverse zones use one closed centreline perimeter per link.",
            "Zone spacing is a maximum: one start link plus ceil(zone length / spacing) intervals, with shared boundaries counted once.",
            "Catalogue cost exclusions are retained without hidden allowances.",
        ),
        "issues": tuple(issues),
    }
    return BeamCandidateCompositionV2.model_validate(
        {**payload, "composition_sha256": _digest(payload)}
    )


def _supplied_request(
    candidate: BeamCandidateDefinitionV2,
    *,
    property_value: BeamExistingPropertyV1,
    catalogue: ProjectBeamCandidateCatalogueV1,
    composition: BeamCandidateCompositionV2,
) -> BeamSuppliedCheckRequestV2:
    tension = _face_layer(candidate.schedule, candidate.primary_tension_face)
    opposite_face: Literal["TOP", "BOTTOM"] = (
        "BOTTOM" if candidate.primary_tension_face == "TOP" else "TOP"
    )
    compression = _face_layer(candidate.schedule, opposite_face)
    zone = _zone_at(candidate.schedule, candidate.action_row.object_station_mm)
    permitted_diameters = tuple(
        item.diameter_mm
        for item in catalogue.longitudinal_stock
        if item.grade_nmm2 == property_value.fy_longitudinal_nmm2
    )
    return BeamSuppliedCheckRequestV2(
        correlation_id=candidate.candidate_id,
        identity=candidate.member_identity,
        section=BeamSuppliedCheckSectionV2(
            b_mm=property_value.width_t2_mm,
            D_mm=property_value.depth_t3_mm,
            effective_depth_basis=CentroidCoverDepthRequestV1(
                centroid_cover_mm=(
                    property_value.depth_t3_mm - composition.effective_depth_mm
                )
            ),
        ),
        materials=IS456ReinforcementMaterialsV1(
            fck_nmm2=property_value.fck_nmm2,
            fy_nmm2=property_value.fy_longitudinal_nmm2,
            fy_transverse_nmm2=property_value.fy_transverse_nmm2,
        ),
        actions=BeamSuppliedCheckActionsV2(
            mu_knm=abs(candidate.action_row.m3_knm),
            vu_kn=abs(candidate.action_row.v2_kn),
            primary_tension_face=candidate.primary_tension_face,
        ),
        reinforcement=BeamSuppliedReinforcementV2(
            clear_cover_mm=candidate.clear_cover_mm,
            tension=BeamBarLayersV2(
                diameter_mm=tension.bar_diameter_mm,
                bars_per_layer=(tension.bar_count,),
            ),
            compression_or_hanger=BeamBarLayersV2(
                diameter_mm=compression.bar_diameter_mm,
                bars_per_layer=(compression.bar_count,),
            ),
            stirrup_diameter_mm=zone.stirrup_diameter_mm,
            stirrup_legs=zone.legs,
            stirrup_spacing_mm=zone.spacing_mm,
            bar_type=candidate.bar_type,
            has_standard_bend_at_start=candidate.has_standard_bend_at_start,
            has_standard_bend_at_end=candidate.has_standard_bend_at_end,
            source_reference=candidate.schedule.schedule_id,
        ),
        selection=BeamReinforcementSelectionV2(
            permitted_diameters_mm=permitted_diameters,
            maximum_layers=1,
            maximum_bars_per_layer=20,
            nominal_max_aggregate_size_mm=candidate.nominal_max_aggregate_size_mm,
            effective_depth_tolerance_mm=1e-6,
            objective="min_area",
            source_reference=catalogue.catalogue_id,
        ),
        support=candidate.support,
        source_provenance=candidate.schedule.schedule_id,
    )


def _bool_status(value: bool | None) -> CandidateVerdict:
    if value is None:
        return "HOLD"
    return "PASS" if value else "FAIL"


def _native_check(
    name: str,
    *,
    supplied: dict[str, Any],
    candidate: BeamCandidateDefinitionV2,
) -> BeamCandidateCheckResultV2 | None:
    longitudinal = supplied["longitudinal"]
    shear = supplied["shear"]
    checks = longitudinal["checks"]
    source = (candidate.schedule.schedule_id,)
    scenario = (candidate.strength_scenario_id,)
    if name == "FLEXURE":
        passed = bool(checks["tension_area"]["is_adequate"]) and bool(
            checks["compression_area"]["is_adequate"]
        )
        return BeamCandidateCheckResultV2(
            check=name,
            status=_bool_status(passed),
            owner="SUPPLIED_BEAM_V2",
            scenario_ids=scenario,
            source_references=source,
            basis="Required and supplied tension/compression areas from the maintained supplied-beam check.",
        )
    if name == "SHEAR":
        return BeamCandidateCheckResultV2(
            check=name,
            status=shear["status"],
            owner="SUPPLIED_BEAM_V2",
            scenario_ids=scenario,
            source_references=source,
            basis="Maintained concrete-plus-stirrup shear check at the signed row station.",
        )
    if name in {"DETAILING", "CONSTRUCTABILITY"}:
        return BeamCandidateCheckResultV2(
            check=name,
            status=longitudinal["status"],
            owner="SUPPLIED_BEAM_V2",
            scenario_ids=scenario,
            source_references=source,
            basis="Layer spacing, group clearance, areas, depth identity, and anchorage from the maintained detailing owner.",
        )
    if name == "AGGREGATE":
        passed = bool(checks["tension_spacing"]["is_adequate"]) and bool(
            checks["compression_spacing"]["is_adequate"]
        )
        return BeamCandidateCheckResultV2(
            check=name,
            status=_bool_status(passed),
            owner="SUPPLIED_BEAM_V2",
            scenario_ids=scenario,
            source_references=source,
            basis="Maintained bar-spacing checks consume the declared nominal maximum aggregate size.",
        )
    if name in {"ANCHORAGE", "SUPPORT"}:
        start = checks["start_anchorage"]
        end = checks["end_anchorage"]
        if start is None or end is None:
            status: CandidateVerdict = "HOLD"
        else:
            status = _bool_status(
                bool(start["is_adequate"]) and bool(end["is_adequate"])
            )
        return BeamCandidateCheckResultV2(
            check=name,
            status=status,
            owner="SUPPLIED_BEAM_V2",
            scenario_ids=scenario,
            source_references=(
                (candidate.support.source_reference,)
                if candidate.support is not None
                else ()
            ),
            basis="Source-bound support widths and maintained simple-support anchorage checks.",
        )
    return None


def evaluate_beam_candidate_v2(
    candidate: BeamCandidateDefinitionV2,
    /,
    *,
    criteria: ProjectBeamCriteriaV1,
    catalogue: ProjectBeamCandidateCatalogueV1,
) -> BeamCandidateEvaluationResultV2:
    """Return the single B1B feasibility verdict for an exact candidate."""

    candidate = _validated(BeamCandidateDefinitionV2, candidate)
    criteria = _validated(ProjectBeamCriteriaV1, criteria)
    catalogue = _validated(ProjectBeamCandidateCatalogueV1, catalogue)
    build_beam_candidate_definition_v2(
        BeamCandidateDefinitionDraftV2.model_validate(
            candidate.model_dump(
                mode="python", exclude={"schema_version", "candidate_sha256"}
            )
        ),
        criteria=criteria,
        catalogue=catalogue,
    )
    property_value = _property(candidate, catalogue)
    composition = check_beam_candidate_composition_v2(candidate, catalogue=catalogue)
    request = _supplied_request(
        candidate,
        property_value=property_value,
        catalogue=catalogue,
        composition=composition,
    )
    supplied_result = check_supplied_beam_v2(request)
    supplied = supplied_result.to_dict()
    supplied_sha = _digest(supplied)
    supplemental = {item.check: item for item in candidate.supplemental_checks}
    required_service = tuple(item.scenario_id for item in criteria.service_scenarios)
    results: list[BeamCandidateCheckResultV2] = []
    for name in criteria.mandatory_checks:
        native = _native_check(name, supplied=supplied, candidate=candidate)
        if native is not None:
            results.append(native)
            continue
        evidence = supplemental.get(name)
        if evidence is None:
            results.append(
                BeamCandidateCheckResultV2(
                    check=name,
                    status="HOLD",
                    owner="B1B_BINDING",
                    basis="Mandatory check has no typed maintained-owner evidence.",
                )
            )
            continue
        status = evidence.status
        if name == "SERVICEABILITY" and evidence.scenario_ids != required_service:
            status = "HOLD"
        if name == "TORSION" and candidate.strength_scenario_id not in (
            evidence.scenario_ids
        ):
            status = "HOLD"
        results.append(
            BeamCandidateCheckResultV2(
                check=name,
                status=status,
                owner="SUPPLEMENTAL_EVIDENCE",
                scenario_ids=evidence.scenario_ids,
                source_references=evidence.source_references,
                basis=evidence.basis,
            )
        )
    applicability_held = (
        abs(candidate.action_row.p_kn) > criteria.max_abs_axial_kn
        or abs(candidate.action_row.v3_kn) > criteria.max_abs_minor_shear_kn
        or abs(candidate.action_row.m2_knm) > criteria.max_abs_minor_moment_knm
        or candidate.side_face_disposition == "HELD_UNTYPED"
        or property_value.auto_select_state != "NOT_AUTO_SELECT"
    )
    if applicability_held:
        results.append(
            BeamCandidateCheckResultV2(
                check="CONSTRUCTABILITY",
                status="HOLD",
                owner="B1B_BINDING",
                scenario_ids=(candidate.strength_scenario_id,),
                source_references=candidate.source_references,
                basis="Excluded-action, side-face, or mutation-readiness applicability is outside the accepted candidate slice.",
            )
        )
        deduplicated: dict[str, BeamCandidateCheckResultV2] = {}
        for result in results:
            previous = deduplicated.get(result.check)
            if previous is None or result.status == "HOLD":
                deduplicated[result.check] = result
        results = [deduplicated[name] for name in criteria.mandatory_checks]
    fixture_held = any(
        status == "AUTHORED_FIXTURE_HOLD"
        for status in (
            criteria.criteria_status,
            catalogue.catalogue_status,
            candidate.schedule.schedule_status,
        )
    )
    statuses = {item.status for item in results}
    if "FAIL" in statuses or composition.status == "FAIL":
        verdict: CandidateVerdict = "FAIL"
    elif (
        "HOLD" in statuses
        or composition.status == "HOLD"
        or fixture_held
        or applicability_held
    ):
        verdict = "HOLD"
    else:
        verdict = "PASS"
    payload: dict[str, Any] = {
        "schema_version": "beam-candidate-evaluation/v2",
        "candidate_id": candidate.candidate_id,
        "candidate_sha256": candidate.candidate_sha256,
        "criteria_sha256": criteria.criteria_sha256,
        "catalogue_sha256": catalogue.catalogue_sha256,
        "schedule_sha256": candidate.schedule.schedule_sha256,
        "action_row_sha256": candidate.action_row.row_sha256,
        "primary_tension_face": candidate.primary_tension_face,
        "verdict": verdict,
        "checks": tuple(results),
        "supplied_check_sha256": supplied_sha,
        "supplied_check": supplied,
        "composition": composition,
        "fixture_evidence_held": fixture_held,
        "limitations": (
            "Only full-span single-layer TOP/BOTTOM reinforcement and exact transverse zones are supported.",
            "Supplemental evidence is identity-bound input; B1B does not duplicate torsion, serviceability, or lap calculations.",
            "A software PASS is not professional approval; qualified project review remains required.",
        ),
    }
    return BeamCandidateEvaluationResultV2.model_validate(
        {**payload, "evaluation_sha256": _digest(payload)}
    )
