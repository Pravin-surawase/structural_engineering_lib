# SPDX-License-Identifier: MIT
"""B1B signed, layer-aware candidate feasibility acceptance."""

from __future__ import annotations

import math

import pytest
from pydantic import ValidationError

from structural_lib.core.analysis_contracts import BeamActionRowV1
from structural_lib.services.beam_audit import canonical_beam_action_row_sha256_v1
from structural_lib.services.beam_candidate_evaluator import (
    BeamCandidateCheckEvidenceV2,
    BeamCandidateDefinitionDraftV2,
    build_beam_candidate_definition_v2,
    check_beam_candidate_composition_v2,
    evaluate_beam_candidate_v2,
)
from structural_lib.services.beam_project_contracts import (
    BeamLongitudinalLayerV1,
    BeamMemberReinforcementScheduleDraftV1,
    ProjectBeamCandidateCatalogueDraftV1,
    build_beam_member_reinforcement_schedule_v1,
    build_project_beam_candidate_catalogue_v1,
    build_project_beam_criteria_v1,
)
from structural_lib.services.contracts.beam import MemberIdentityV1
from structural_lib.services.contracts.beam_supplied_check import BeamSupportBasisV2
from tests.unit.test_beam_project_contracts import (
    _catalogue,
    _criteria_draft,
    _schedule_draft,
)


def _owners(*, reviewed: bool):
    criteria_draft = _criteria_draft()
    if reviewed:
        criteria_draft = criteria_draft.model_copy(
            update={
                "criteria_status": "PROJECT_REVIEWED",
                "reviewed_by": "fixture:qualified-reviewer",
            }
        )
    criteria = build_project_beam_criteria_v1(criteria_draft)
    catalogue = _catalogue(criteria)
    if reviewed:
        catalogue_draft = ProjectBeamCandidateCatalogueDraftV1.model_validate(
            {
                **catalogue.model_dump(
                    mode="python", exclude={"schema_version", "catalogue_sha256"}
                ),
                "catalogue_status": "PROJECT_REVIEWED",
                "reviewed_by": "fixture:qualified-reviewer",
            }
        )
        catalogue = build_project_beam_candidate_catalogue_v1(
            catalogue_draft, criteria=criteria
        )
    schedule_draft = _schedule_draft(criteria, catalogue)
    if reviewed:
        schedule_draft = schedule_draft.model_copy(
            update={"schedule_status": "COMPLETE"}
        )
    schedule = build_beam_member_reinforcement_schedule_v1(
        schedule_draft, criteria=criteria, catalogue=catalogue
    )
    return criteria, catalogue, schedule


def _action_row(*, m3_knm: float = 100.0) -> BeamActionRowV1:
    row = BeamActionRowV1(
        row_id=f"row:{m3_knm:+g}",
        model_identity_sha256="1" * 64,
        baseline_sha256="2" * 64,
        catalogue_sha256="3" * 64,
        member_id="B1",
        source_frame_name="B1",
        station_id="B1@500",
        selection_id="selection:uls-1",
        selection_kind="COMBINATION",
        selection_name="ULS-1",
        output_case_name="ULS-1",
        object_name="B1",
        object_station_mm=500.0,
        element_name="B1-1",
        element_station_mm=500.0,
        step_type="Max",
        step_number=0.0,
        source_row_index=0,
        p_kn=1.0,
        v2_kn=20.0,
        v3_kn=1.0,
        t_knm=1.0,
        m2_knm=1.0,
        m3_knm=m3_knm,
        local_axis_basis="fixture retained ETABS local axes",
        row_sha256="0" * 64,
    )
    return row.model_copy(
        update={"row_sha256": canonical_beam_action_row_sha256_v1(row)}
    )


def _supplemental(*, service_status: str = "PASS"):
    return (
        BeamCandidateCheckEvidenceV2(
            check="TORSION",
            status="PASS",
            scenario_ids=("ULS-1",),
            source_references=("fixture:torsion-check",),
            basis="Fixture result from the maintained torsion owner.",
        ),
        BeamCandidateCheckEvidenceV2(
            check="SERVICEABILITY",
            status=service_status,
            scenario_ids=("SLS-1",),
            source_references=("fixture:serviceability-check",),
            basis="Fixture result from the maintained serviceability owner.",
        ),
        BeamCandidateCheckEvidenceV2(
            check="LAP",
            status="PASS",
            source_references=("fixture:lap-review",),
            basis="No lap occurs in the full-span fixture schedule.",
        ),
    )


def _candidate(*, reviewed: bool = True, m3_knm: float = 100.0):
    criteria, catalogue, schedule = _owners(reviewed=reviewed)
    row = _action_row(m3_knm=m3_knm)
    draft = BeamCandidateDefinitionDraftV2(
        candidate_id=f"candidate:{m3_knm:+g}",
        member_identity=MemberIdentityV1(
            member_id="B1", story="L1", case_id="selection:uls-1"
        ),
        action_row=row,
        strength_scenario_id="ULS-1",
        primary_tension_face="BOTTOM" if m3_knm >= 0 else "TOP",
        existing_property_id=schedule.existing_property_id,
        existing_property_sha256=(
            catalogue.existing_beam_properties[0].property_sha256
        ),
        criteria_sha256=criteria.criteria_sha256,
        catalogue_sha256=catalogue.catalogue_sha256,
        schedule=schedule,
        clear_cover_mm=40.0,
        nominal_max_aggregate_size_mm=20.0,
        support=BeamSupportBasisV2(
            start_width_mm=5000.0,
            end_width_mm=5000.0,
            source_reference="fixture:supports",
        ),
        service_scenario_ids=("SLS-1",),
        supplemental_checks=_supplemental(),
        has_standard_bend_at_start=True,
        has_standard_bend_at_end=True,
        side_face_disposition=schedule.side_face_disposition,
        source_references=("fixture:candidate",),
        limitations=("Software acceptance fixture only.",),
    )
    candidate = build_beam_candidate_definition_v2(
        draft, criteria=criteria, catalogue=catalogue
    )
    return criteria, catalogue, candidate


def test_candidate_recomputes_442_mm_depth_and_composes_maintained_check() -> None:
    criteria, catalogue, candidate = _candidate()

    result = evaluate_beam_candidate_v2(
        candidate, criteria=criteria, catalogue=catalogue
    )

    assert result.verdict == "PASS"
    assert result.composition.effective_depth_mm == pytest.approx(442.0)
    assert result.supplied_check["effective_depth_resolution"]["d_mm"] == pytest.approx(
        442.0
    )
    assert result.supplied_check["request"]["section"]["d_mm"] is None
    assert result.supplied_check["primary_tension_face"] == "BOTTOM"
    assert {item.status for item in result.checks} == {"PASS"}
    assert (
        result.evaluation_sha256
        == evaluate_beam_candidate_v2(
            candidate, criteria=criteria, catalogue=catalogue
        ).evaluation_sha256
    )


def test_authored_fixture_and_missing_mandatory_evidence_can_never_pass() -> None:
    criteria, catalogue, candidate = _candidate(reviewed=False)
    fixture_result = evaluate_beam_candidate_v2(
        candidate, criteria=criteria, catalogue=catalogue
    )
    assert fixture_result.verdict == "HOLD"
    assert fixture_result.fixture_evidence_held is True

    reviewed_criteria, reviewed_catalogue, reviewed = _candidate()
    draft = BeamCandidateDefinitionDraftV2.model_validate(
        reviewed.model_dump(
            mode="python", exclude={"schema_version", "candidate_sha256"}
        )
    ).model_copy(
        update={
            "supplemental_checks": tuple(
                item
                for item in reviewed.supplemental_checks
                if item.check != "SERVICEABILITY"
            )
        }
    )
    missing = build_beam_candidate_definition_v2(
        draft, criteria=reviewed_criteria, catalogue=reviewed_catalogue
    )
    held = evaluate_beam_candidate_v2(
        missing, criteria=reviewed_criteria, catalogue=reviewed_catalogue
    )
    assert held.verdict == "HOLD"
    assert (
        next(item for item in held.checks if item.check == "SERVICEABILITY").owner
        == "B1B_BINDING"
    )


def test_signed_face_and_every_sealed_identity_fail_closed() -> None:
    criteria, catalogue, candidate = _candidate()
    draft = BeamCandidateDefinitionDraftV2.model_validate(
        candidate.model_dump(
            mode="python", exclude={"schema_version", "candidate_sha256"}
        )
    )
    with pytest.raises(ValueError, match="signed M3"):
        build_beam_candidate_definition_v2(
            draft.model_copy(update={"primary_tension_face": "TOP"}),
            criteria=criteria,
            catalogue=catalogue,
        )

    tampered_row = draft.action_row.model_copy(update={"m3_knm": 101.0})
    with pytest.raises(ValueError, match="action-row digest"):
        build_beam_candidate_definition_v2(
            draft.model_copy(update={"action_row": tampered_row}),
            criteria=criteria,
            catalogue=catalogue,
        )

    tampered = candidate.model_copy(update={"candidate_sha256": "f" * 64})
    with pytest.raises(ValidationError, match="candidate_sha256"):
        evaluate_beam_candidate_v2(tampered, criteria=criteria, catalogue=catalogue)


def test_independent_composition_recomputes_exact_schedule_quantities() -> None:
    _criteria, catalogue, candidate = _candidate()
    composition = check_beam_candidate_composition_v2(candidate, catalogue=catalogue)

    assert composition.status == "PASS"
    assert composition.bottom_area_mm2 == pytest.approx(4 * math.pi * 20**2 / 4)
    assert composition.top_area_mm2 == pytest.approx(3 * math.pi * 16**2 / 4)
    assert composition.stirrup_count == 36
    assert composition.total_steel_mass_kg == pytest.approx(
        composition.longitudinal_mass_kg + composition.transverse_mass_kg
    )
    assert composition.total_cost > 0
    assert composition == check_beam_candidate_composition_v2(
        candidate, catalogue=catalogue
    )


def test_untyped_multi_leg_link_geometry_holds_quantity_and_feasibility() -> None:
    criteria, catalogue, candidate = _candidate()
    schedule_draft = BeamMemberReinforcementScheduleDraftV1.model_validate(
        candidate.schedule.model_dump(
            mode="python", exclude={"schema_version", "schedule_sha256"}
        )
    ).model_copy(
        update={
            "schedule_id": "fixture:schedule-B1-four-leg",
            "transverse_zones": tuple(
                zone.model_copy(update={"legs": 4})
                for zone in candidate.schedule.transverse_zones
            ),
        }
    )
    schedule = build_beam_member_reinforcement_schedule_v1(
        schedule_draft, criteria=criteria, catalogue=catalogue
    )
    draft = BeamCandidateDefinitionDraftV2.model_validate(
        candidate.model_dump(
            mode="python", exclude={"schema_version", "candidate_sha256"}
        )
    ).model_copy(update={"schedule": schedule})
    held_candidate = build_beam_candidate_definition_v2(
        draft, criteria=criteria, catalogue=catalogue
    )

    result = evaluate_beam_candidate_v2(
        held_candidate, criteria=criteria, catalogue=catalogue
    )

    assert result.verdict == "HOLD"
    assert result.composition.status == "HOLD"
    assert "multi-leg link geometry" in result.composition.issues[0]


def test_top_bottom_mirror_preserves_logical_capacity_and_quantity() -> None:
    criteria, catalogue, positive = _candidate(m3_knm=100.0)
    positive_result = evaluate_beam_candidate_v2(
        positive, criteria=criteria, catalogue=catalogue
    )
    schedule = positive.schedule
    mirrored_schedule_draft = BeamMemberReinforcementScheduleDraftV1.model_validate(
        schedule.model_dump(
            mode="python", exclude={"schema_version", "schedule_sha256"}
        )
    ).model_copy(
        update={
            "schedule_id": "fixture:schedule-B1-mirrored",
            "longitudinal_layers": tuple(
                BeamLongitudinalLayerV1(
                    face="TOP" if layer.face == "BOTTOM" else "BOTTOM",
                    bar_count=layer.bar_count,
                    bar_diameter_mm=layer.bar_diameter_mm,
                    grade_nmm2=layer.grade_nmm2,
                )
                for layer in schedule.longitudinal_layers
            ),
        }
    )
    mirrored_schedule = build_beam_member_reinforcement_schedule_v1(
        mirrored_schedule_draft, criteria=criteria, catalogue=catalogue
    )
    row = _action_row(m3_knm=-100.0)
    mirrored_draft = BeamCandidateDefinitionDraftV2.model_validate(
        positive.model_dump(
            mode="python", exclude={"schema_version", "candidate_sha256"}
        )
    ).model_copy(
        update={
            "candidate_id": "candidate:-100",
            "action_row": row,
            "primary_tension_face": "TOP",
            "schedule": mirrored_schedule,
            "side_face_disposition": mirrored_schedule.side_face_disposition,
        }
    )
    mirrored = build_beam_candidate_definition_v2(
        mirrored_draft, criteria=criteria, catalogue=catalogue
    )
    mirrored_result = evaluate_beam_candidate_v2(
        mirrored, criteria=criteria, catalogue=catalogue
    )

    assert mirrored_result.verdict == positive_result.verdict == "PASS"
    assert mirrored_result.composition.effective_depth_mm == pytest.approx(
        positive_result.composition.effective_depth_mm
    )
    assert mirrored_result.composition.total_cost == pytest.approx(
        positive_result.composition.total_cost
    )
    assert mirrored_result.supplied_check["shear"]["utilization"] == pytest.approx(
        positive_result.supplied_check["shear"]["utilization"]
    )
    assert mirrored_result.supplied_check["longitudinal"]["ast_required_mm2"] == (
        pytest.approx(
            positive_result.supplied_check["longitudinal"]["ast_required_mm2"]
        )
    )
