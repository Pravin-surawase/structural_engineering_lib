# SPDX-License-Identifier: MIT
"""B1A deterministic criteria, catalogue, and schedule acceptance."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from structural_lib.services.beam_project_contracts import (
    BeamCriteriaScenarioV1,
    BeamCriteriaStopPolicyV1,
    BeamExistingPropertyDraftV1,
    BeamLongitudinalLayerV1,
    BeamLongitudinalStockV1,
    BeamMemberReinforcementScheduleDraftV1,
    BeamPropertyCostBasisV1,
    BeamTransverseStockV1,
    BeamTransverseZoneV1,
    ProjectBeamCandidateCatalogueDraftV1,
    ProjectBeamCriteriaDraftV1,
    build_beam_existing_property_v1,
    build_beam_member_reinforcement_schedule_v1,
    build_project_beam_candidate_catalogue_v1,
    build_project_beam_criteria_v1,
)

T0 = datetime(2026, 9, 2, 0, 0, tzinfo=UTC)


def _criteria_draft():
    return ProjectBeamCriteriaDraftV1(
        criteria_id="fixture:beam-criteria-1",
        criteria_status="AUTHORED_FIXTURE_HOLD",
        code_revision="IS 456:2000 with reviewed project amendments",
        source_references=("fixture:criteria-source",),
        reviewed_by=None,
        strength_scenarios=(
            BeamCriteriaScenarioV1(
                scenario_id="ULS-1",
                purpose="STRENGTH",
                selection_ids=("selection:uls-1",),
                action_components=("P", "V2", "V3", "T", "M2", "M3"),
                source_reference="fixture:strength-domain",
            ),
        ),
        service_scenarios=(
            BeamCriteriaScenarioV1(
                scenario_id="SLS-1",
                purpose="SERVICEABILITY",
                selection_ids=("selection:sls-1",),
                action_components=("M3",),
                source_reference="fixture:service-domain",
            ),
        ),
        positive_m3_tension_face="BOTTOM",
        negative_m3_tension_face="TOP",
        max_abs_axial_kn=5.0,
        max_abs_minor_shear_kn=5.0,
        max_abs_minor_moment_knm=5.0,
        torsion_disposition="MANDATORY",
        excluded_effects=("No seismic capacity-design claim in this fixture.",),
        mandatory_checks=(
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
        ),
        scope_dispositions=(
            ("anchorage", "MANDATORY"),
            ("capacity_design", "HELD"),
            ("side_face", "N_A"),
        ),
        sensitivity_scenarios=("cover:+5mm", "steel-cost:+10pct"),
        objectives=("STEEL_MASS", "COST", "CONGESTION"),
        tie_breaks=("LOWER_UTILIZATION", "FEWER_BAR_MARKS", "PROPERTY_ID"),
        stop_policy=BeamCriteriaStopPolicyV1(
            maximum_generated_candidates=1000,
            maximum_evaluated_candidates=1000,
            allow_incomplete_shortlist=False,
        ),
        serviceability_mandatory=True,
        declared_at_utc=T0,
        candidate_inspection_started_at_utc=T0 + timedelta(minutes=1),
        assumptions=("Authored software fixture; not actual project criteria.",),
        limitations=("Actual project review remains required.",),
    )


def _catalogue(criteria):
    property_value = build_beam_existing_property_v1(
        BeamExistingPropertyDraftV1(
            property_id="property:R300x500",
            source_property_name="R300x500",
            width_t2_mm=300.0,
            depth_t3_mm=500.0,
            concrete_material="M25",
            fck_nmm2=25.0,
            longitudinal_rebar_material="HYSD500",
            transverse_rebar_material="MS250",
            fy_longitudinal_nmm2=500.0,
            fy_transverse_nmm2=250.0,
            modifiers=(("A", 1.0), ("I22", 1.0), ("I33", 1.0)),
            auto_select_state="NOT_AUTO_SELECT",
            source_reference="fixture:property-inventory",
        )
    )
    draft = ProjectBeamCandidateCatalogueDraftV1(
        catalogue_id="fixture:catalogue-1",
        catalogue_status="AUTHORED_FIXTURE_HOLD",
        criteria_sha256=criteria.criteria_sha256,
        catalogue_revision="fixture-r1",
        existing_beam_properties=(property_value,),
        longitudinal_stock=(
            BeamLongitudinalStockV1(
                diameter_mm=16.0,
                grade_nmm2=500.0,
                stock_revision="bars-r1",
            ),
            BeamLongitudinalStockV1(
                diameter_mm=20.0,
                grade_nmm2=500.0,
                stock_revision="bars-r1",
            ),
        ),
        transverse_stock=(
            BeamTransverseStockV1(
                diameter_mm=8.0,
                grade_nmm2=250.0,
                permitted_legs=(2, 4),
                permitted_spacing_mm=(100.0, 150.0, 200.0),
                stock_revision="stirrups-r1",
            ),
        ),
        cost_basis=BeamPropertyCostBasisV1(
            currency="INR",
            concrete_per_m3=8000.0,
            longitudinal_steel_per_kg=75.0,
            transverse_steel_per_kg=80.0,
            formwork_per_m2=900.0,
            cost_revision="cost-r1",
            exclusions=("Taxes and escalation excluded.",),
        ),
        source_references=("fixture:catalogue-source",),
        reviewed_by=None,
        declared_at_utc=T0,
        candidate_generation_started_at_utc=T0 + timedelta(minutes=2),
        limitations=("Authored fixture cannot authorize ETABS mutation.",),
    )
    return build_project_beam_candidate_catalogue_v1(draft, criteria=criteria)


def _schedule_draft(criteria, catalogue):
    return BeamMemberReinforcementScheduleDraftV1(
        schedule_id="fixture:schedule-B1-r1",
        schedule_status="AUTHORED_FIXTURE_HOLD",
        schedule_revision="r1",
        member_id="B1",
        span_mm=5000.0,
        existing_property_id="property:R300x500",
        criteria_sha256=criteria.criteria_sha256,
        catalogue_sha256=catalogue.catalogue_sha256,
        longitudinal_layers=(
            BeamLongitudinalLayerV1(
                face="BOTTOM", bar_count=4, bar_diameter_mm=20.0, grade_nmm2=500.0
            ),
            BeamLongitudinalLayerV1(
                face="TOP", bar_count=3, bar_diameter_mm=16.0, grade_nmm2=500.0
            ),
        ),
        transverse_zones=(
            BeamTransverseZoneV1(
                zone_id="I",
                start_mm=0.0,
                end_mm=1000.0,
                stirrup_diameter_mm=8.0,
                grade_nmm2=250.0,
                legs=2,
                spacing_mm=100.0,
            ),
            BeamTransverseZoneV1(
                zone_id="MID",
                start_mm=1000.0,
                end_mm=4000.0,
                stirrup_diameter_mm=8.0,
                grade_nmm2=250.0,
                legs=2,
                spacing_mm=200.0,
            ),
            BeamTransverseZoneV1(
                zone_id="J",
                start_mm=4000.0,
                end_mm=5000.0,
                stirrup_diameter_mm=8.0,
                grade_nmm2=250.0,
                legs=2,
                spacing_mm=100.0,
            ),
        ),
        side_face_disposition="NOT_APPLICABLE",
        source_references=("fixture:schedule-source",),
        limitations=("Full-span single-layer bars only.",),
    )


def test_criteria_catalogue_and_schedule_hashes_are_deterministic_and_bound() -> None:
    criteria = build_project_beam_criteria_v1(_criteria_draft())
    catalogue = _catalogue(criteria)
    schedule = build_beam_member_reinforcement_schedule_v1(
        _schedule_draft(criteria, catalogue),
        criteria=criteria,
        catalogue=catalogue,
    )

    assert build_project_beam_criteria_v1(_criteria_draft()) == criteria
    assert _catalogue(criteria) == catalogue
    assert schedule.schedule_status == "AUTHORED_FIXTURE_HOLD"
    assert schedule.criteria_sha256 == criteria.criteria_sha256
    assert schedule.catalogue_sha256 == catalogue.catalogue_sha256
    assert {layer.face for layer in schedule.longitudinal_layers} == {"TOP", "BOTTOM"}
    assert catalogue.existing_beam_properties[0].fy_longitudinal_nmm2 == 500.0
    assert catalogue.existing_beam_properties[0].fy_transverse_nmm2 == 250.0


def test_any_criteria_change_invalidates_catalogue_binding() -> None:
    criteria = build_project_beam_criteria_v1(_criteria_draft())
    changed = build_project_beam_criteria_v1(
        _criteria_draft().model_copy(update={"max_abs_axial_kn": 6.0})
    )
    catalogue = _catalogue(criteria)

    assert changed.criteria_sha256 != criteria.criteria_sha256
    with pytest.raises(ValueError, match="criteria identity"):
        build_project_beam_candidate_catalogue_v1(
            ProjectBeamCandidateCatalogueDraftV1.model_validate(
                catalogue.model_dump(exclude={"schema_version", "catalogue_sha256"})
            ),
            criteria=changed,
        )


def test_declaration_chronology_and_service_domain_fail_closed() -> None:
    with pytest.raises(ValidationError, match="declared before candidate inspection"):
        ProjectBeamCriteriaDraftV1.model_validate(
            {
                **_criteria_draft().model_dump(),
                "candidate_inspection_started_at_utc": T0 - timedelta(seconds=1),
            }
        )
    with pytest.raises(ValidationError, match="service scenarios"):
        ProjectBeamCriteriaDraftV1.model_validate(
            {**_criteria_draft().model_dump(), "service_scenarios": ()}
        )


def test_schedule_rejects_zone_gap_and_unapproved_stock() -> None:
    criteria = build_project_beam_criteria_v1(_criteria_draft())
    catalogue = _catalogue(criteria)
    draft = _schedule_draft(criteria, catalogue)
    zones = list(draft.transverse_zones)
    zones[1] = zones[1].model_copy(update={"start_mm": 1100.0})
    with pytest.raises(ValidationError, match="contiguous"):
        BeamMemberReinforcementScheduleDraftV1.model_validate(
            {**draft.model_dump(), "transverse_zones": tuple(zones)}
        )
    changed_layer = draft.longitudinal_layers[0].model_copy(
        update={"bar_diameter_mm": 25.0}
    )
    outside_stock = draft.model_copy(
        update={"longitudinal_layers": (changed_layer, draft.longitudinal_layers[1])}
    )
    with pytest.raises(ValueError, match="outside approved stock"):
        build_beam_member_reinforcement_schedule_v1(
            outside_stock,
            criteria=criteria,
            catalogue=catalogue,
        )
