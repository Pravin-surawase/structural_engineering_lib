"""Focused actions, prerequisite, and fail-closed tests for Gravity Workflow V1."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from structural_lib.core.building_gravity import (
    BuildingModelV1,
    GravityMemberKindV1,
    GravityPracticalActionV1,
)
from structural_lib.core.gravity_workflow import (
    GravityBeamDesignBasisV1,
    GravityBeamReinforcementBasisV1,
    GravityColumnDesignBasisV1,
    GravityFootingDesignBasisV1,
    GravityLongitudinalBarLayersV1,
    GravitySlabDesignBasisV1,
    GravityWorkflowRequestV1,
)
from structural_lib.services.gravity_calculation_book import (
    GravityCalculationBookV1,
    build_gravity_calculation_book_v1,
    render_gravity_calculation_book_markdown_v1,
    run_gravity_workflow_with_book_v1,
)
from structural_lib.services.gravity_loads import build_gravity_load_ledger_v1
from structural_lib.services.gravity_workflow import (
    build_component_applicability_matrix_v1,
    build_gravity_member_actions_v1,
    run_gravity_workflow_v1,
)
from tests.unit.test_building_gravity_v1 import _building, _loads, _practical_actions


def _request(
    building: BuildingModelV1 | None = None,
    *,
    with_supported_component_bases: bool = False,
    beam_effective_depth_mm: float = 450,
    superimposed_dead_load_kn_m2: float = 1.5,
    live_load_kn_m2: float = 3.0,
    beam_reinforcement_basis: GravityBeamReinforcementBasisV1 | None = None,
    practical_actions: tuple[GravityPracticalActionV1, ...] = (),
) -> GravityWorkflowRequestV1:
    building = building or _building()
    loads = _loads(
        building,
        superimposed_dead_load_kn_m2=superimposed_dead_load_kn_m2,
        live_load_kn_m2=live_load_kn_m2,
        practical_actions=practical_actions,
    )
    slab_bases: tuple[GravitySlabDesignBasisV1, ...] = ()
    beam_bases: tuple[GravityBeamDesignBasisV1, ...] = ()
    column_bases: tuple[GravityColumnDesignBasisV1, ...] = ()
    if with_supported_component_bases:
        column_section = next(
            item for item in building.sections if item.id == "S_COLUMN"
        )
        column_steel_area_mm2 = max(
            1800.0,
            0.01 * float(column_section.width_mm) * float(column_section.depth_mm),
        )
        slab_bases = (
            GravitySlabDesignBasisV1(
                panel_id="P1",
                d_mm=125,
                fy_nmm2=415,
                main_bar_diameter_mm=10,
                main_bar_spacing_mm=100,
                distribution_bar_diameter_mm=8,
                distribution_bar_spacing_mm=150,
                reviewed_base_span_depth_limit=20,
                reviewed_aggregate_modification_factor=2,
                serviceability_limit_source_reference="Reviewed IS 456 span-depth basis",
                serviceability_limit_source_is_approved=True,
                qualified_serviceability_acceptance_reference=(
                    "Qualified review acknowledgement for test vector"
                ),
                qualified_serviceability_acceptance_acknowledged=True,
                effective_depth_source_reference="125 mm reviewed effective depth",
            ),
        )
        beam_bases = tuple(
            GravityBeamDesignBasisV1(
                beam_id=member.id,
                d_mm=beam_effective_depth_mm,
                fy_nmm2=415,
                asv_mm2=100,
                ast_mm2_for_shear=1500,
                cover_mm=25 if beam_reinforcement_basis is not None else None,
                effective_depth_source_reference="450 mm reviewed effective depth",
                reinforcement_basis=beam_reinforcement_basis,
            )
            for member in building.members
            if member.kind is GravityMemberKindV1.BEAM
        )
        column_bases = tuple(
            GravityColumnDesignBasisV1(
                column_id=member.id,
                fy_nmm2=415,
                Asc_mm2=column_steel_area_mm2,
                d_prime_mm=50,
                end_condition="FIXED_FIXED",
                end_condition_source_reference="Reviewed braced fixed-fixed basis",
                reinforcement_source_reference="Reviewed 1800 mm2 steel basis",
                braced_acknowledged=True,
                axial_only_action_acknowledged=True,
            )
            for member in building.members
            if member.kind is GravityMemberKindV1.COLUMN
        )
    return GravityWorkflowRequestV1(
        model_hash=building.accepted_model_hash,
        load_model_hash=loads.load_model_hash,
        building=building,
        loads=loads,
        slab_design_bases=slab_bases,
        beam_design_bases=beam_bases,
        column_design_bases=column_bases,
    )


def _beam_reinforcement_basis(
    *, supplied: bool, tension_count: int = 5
) -> GravityBeamReinforcementBasisV1:
    supply = (
        {
            "supplied_tension": GravityLongitudinalBarLayersV1(
                diameter_mm=16,
                bars_per_layer=(tension_count,),
            ),
            "supplied_compression_or_hanger": GravityLongitudinalBarLayersV1(
                diameter_mm=12,
                bars_per_layer=(2,),
            ),
            "supplied_reinforcement_source_reference": (
                "Reviewed B1/B2 test bar schedule"
            ),
            "has_standard_bend_at_start": True,
            "has_standard_bend_at_end": True,
        }
        if supplied
        else {}
    )
    return GravityBeamReinforcementBasisV1(
        permitted_diameters_mm=(12, 16, 20),
        maximum_layers=2,
        maximum_bars_per_layer=8,
        nominal_max_aggregate_size_mm=20,
        effective_depth_tolerance_mm=5,
        objective="min_area",
        selection_source_reference="Reviewed test selection constraints",
        **supply,
    )


def _building_with_square_column_width(width_mm: float) -> BuildingModelV1:
    payload = _building().model_dump(mode="python", exclude={"accepted_model_hash"})
    payload["sections"] = tuple(
        (
            {**section, "width_mm": width_mm, "depth_mm": width_mm}
            if section["id"] == "S_COLUMN"
            else section
        )
        for section in payload["sections"]
    )
    return BuildingModelV1.model_validate(payload)


def _building_with_x_span(x_span_mm: float) -> BuildingModelV1:
    payload = _building().model_dump(mode="python", exclude={"accepted_model_hash"})
    payload["nodes"] = tuple(
        {**node, "x_mm": x_span_mm} if node["id"] in {"N2", "N4", "N6", "N8"} else node
        for node in payload["nodes"]
    )
    return BuildingModelV1.model_validate(payload)


def _footing_basis(
    *, service_axial_kn: float, factored_axial_kn: float
) -> GravityFootingDesignBasisV1:
    return GravityFootingDesignBasisV1(
        footing_id="F1",
        complete_service_axial_load_kn=service_axial_kn,
        service_load_combination_id="SERVICE_DL_LL_WITH_EXTERNAL_FOOTING_ACTIONS",
        service_load_basis="includes_footing_self_weight_and_overburden",
        service_load_origin="verified",
        complete_factored_axial_load_kn=factored_axial_kn,
        factored_load_combination_id="ULS_WITH_EXTERNAL_FOOTING_ACTIONS",
        allowable_soil_pressure_kpa=200,
        allowable_soil_pressure_source_reference="Approved geotechnical test basis",
        allowable_soil_pressure_origin="verified",
        allowable_soil_pressure_is_externally_approved=True,
        footing_type="SQUARE",
        minimum_overall_thickness_mm=300,
        maximum_overall_thickness_mm=600,
        thickness_increment_mm=50,
        effective_depth_offset_l_mm=75,
        effective_depth_offset_b_mm=75,
        footing_concrete_fck_nmm2=25,
        steel_fy_nmm2=415,
        effective_supporting_area_a1_mm2=360_000,
        effective_supporting_area_basis="largest_frustum_1v_2h",
        effective_supporting_area_origin="verified",
        effective_supporting_area_is_approved=True,
        dowel_count=4,
        dowel_diameter_mm=16,
        column_longitudinal_bar_diameter_mm=20,
        available_dowel_development_length_into_footing_mm=600,
        available_dowel_development_length_into_column_mm=600,
    )


def test_request_binds_exact_model_load_hashes_and_known_component_ids() -> None:
    request = _request()
    with pytest.raises(ValidationError, match="model_hash must match"):
        GravityWorkflowRequestV1(
            model_hash="f" * 64,
            load_model_hash=request.load_model_hash,
            building=request.building,
            loads=request.loads,
        )

    with pytest.raises(ValidationError, match="unknown beam design basis IDs"):
        GravityWorkflowRequestV1(
            model_hash=request.model_hash,
            load_model_hash=request.load_model_hash,
            building=request.building,
            loads=request.loads,
            beam_design_bases=(
                GravityBeamDesignBasisV1(
                    beam_id="UNKNOWN",
                    d_mm=450,
                    fy_nmm2=415,
                    asv_mm2=100,
                    effective_depth_source_reference="reviewed test basis",
                ),
            ),
        )


def test_beam_reinforcement_basis_rejects_partial_supply_and_missing_cover() -> None:
    with pytest.raises(ValidationError, match="must be supplied together"):
        GravityBeamReinforcementBasisV1(
            selection_source_reference="Reviewed test selection constraints",
            supplied_tension=GravityLongitudinalBarLayersV1(
                diameter_mm=16,
                bars_per_layer=(4,),
            ),
        )

    with pytest.raises(ValidationError, match="cover_mm is required"):
        GravityBeamDesignBasisV1(
            beam_id="B1",
            d_mm=450,
            fy_nmm2=415,
            asv_mm2=100,
            effective_depth_source_reference="Reviewed test depth",
            reinforcement_basis=_beam_reinforcement_basis(supplied=False),
        )


def test_hand_example_actions_match_exact_ledger_and_closed_form_values() -> None:
    request = _request()
    actions = build_gravity_member_actions_v1(
        request, build_gravity_load_ledger_v1(request.building, request.loads)
    )

    assert len(actions) == 22
    by_id = {item.action_id: item for item in actions}
    service_beam = by_id["action:SERVICE_DL_LL:B1"]
    factored_beam = by_id["action:ULS_1_5_DL_LL:B1"]
    slab = by_id["action:ULS_1_5_DL_LL:P1"]
    footing = by_id["action:ULS_1_5_DL_LL:F1"]

    assert service_beam.line_load_kn_m == pytest.approx(20.25)
    assert service_beam.moment_knm == pytest.approx(91.125)
    assert service_beam.shear_kn == pytest.approx(60.75)
    assert factored_beam.line_load_kn_m == pytest.approx(30.375)
    assert factored_beam.moment_knm == pytest.approx(136.6875)
    assert factored_beam.shear_kn == pytest.approx(91.125)
    assert slab.area_load_kn_m2 == pytest.approx(12.375)
    assert footing.axial_kn == pytest.approx(101.25)
    assert footing.source_entry_ids == ("footing:DL:F1", "footing:LL:F1")


def test_practical_actions_flow_through_exact_member_actions_and_result() -> None:
    request = _request(practical_actions=_practical_actions())
    result = run_gravity_workflow_v1(request)
    by_id = {item.action_id: item for item in result.actions}

    service_beam = by_id["action:SERVICE_DL_LL:B1"]
    factored_slab = by_id["action:ULS_1_5_DL_LL:P1"]
    factored_footing = by_id["action:ULS_1_5_DL_LL:F1"]
    assert service_beam.line_load_kn_m == pytest.approx(27.25)
    assert service_beam.moment_knm == pytest.approx(134.91857798165137)
    assert service_beam.shear_kn == pytest.approx(89.75)
    assert "apply:DL:practical:EQUIPMENT_B1_DL" in (service_beam.source_entry_ids)
    assert factored_slab.area_load_kn_m2 == pytest.approx(13.875)
    assert factored_footing.axial_kn == pytest.approx(144.75)

    reconciliation = {
        item.action_id: item for item in result.practical_action_reconciliation
    }
    assert set(reconciliation) == {
        "WALL_B1_DL",
        "FACADE_B2_DL",
        "EQUIPMENT_B1_DL",
        "ROOF_SPECIAL_P1_LL",
    }
    assert all(
        item.reconciled and item.residual_kn == 0 for item in reconciliation.values()
    )
    point = reconciliation["EQUIPMENT_B1_DL"]
    assert point.source_identity == "equipment:item:01"
    assert point.source_ref_id == "PROJECT_BASIS"
    assert point.destination_id == "B1"
    assert point.units.value == "kN"
    assert point.point_position_mm == 2000
    assert point.source_total_kn == 12
    assert point.destination_total_kn == 12

    bundle = run_gravity_workflow_with_book_v1(request)
    assert bundle.calculation_book.reconciliation["boundary_count"] == 30
    assert bundle.calculation_book.reconciliation["maximum_absolute_residual_kn"] == 0
    assert (
        bundle.calculation_book.practical_action_reconciliation
        == result.practical_action_reconciliation
    )


@pytest.mark.parametrize(
    ("span_mm", "station_mm", "reversed_beam", "end_transfer_kn", "ledger_hash"),
    [
        (
            6000,
            0,
            False,
            0.0,
            "dcfacc1a557b3c4e3eb6ceaab85773a5c0fbe1b05016b98f86429c9aa555515f",
        ),
        (
            6000,
            6000,
            False,
            12.0,
            "d2302f674dbd7d931bfa97657d936a51512aff66e881270c95f70f1ba4f1f52f",
        ),
        (
            8001,
            0,
            False,
            0.0,
            "aefc34266031e9a7cb629d3b62567ff1c5411649241286a6e11d08a98684ccb5",
        ),
        (
            8001,
            8000,
            False,
            12 * 8000 / 8001,
            "3aa2e1c99513222ccce19d1d133c2b0d872a631a89658bdb3723c014439e3bb0",
        ),
        (8001, 8001, False, 12.0, None),
        (8001.25, 8001.25, False, 12.0, None),
        (8001, 8001, True, 12.0, None),
    ],
)
def test_point_station_uses_exact_span_and_physical_beam_ends(
    span_mm: float,
    station_mm: float,
    reversed_beam: bool,
    end_transfer_kn: float,
    ledger_hash: str | None,
) -> None:
    building = _building_with_x_span(span_mm)
    if reversed_beam:
        payload = building.model_dump(mode="python", exclude={"accepted_model_hash"})
        beam = next(item for item in payload["members"] if item["id"] == "B1")
        beam["start_node_id"], beam["end_node_id"] = (
            beam["end_node_id"],
            beam["start_node_id"],
        )
        building = BuildingModelV1.model_validate(payload)

    point = GravityPracticalActionV1.model_validate(
        {
            **_practical_actions()[2].model_dump(),
            "point_position_mm": station_mm,
            "assignment_basis": f"Equipment at {station_mm} mm from B1 start.",
        }
    )
    baseline = run_gravity_workflow_with_book_v1(_request(building))
    bundle = run_gravity_workflow_with_book_v1(
        _request(building, practical_actions=(point,))
    )
    result = bundle.workflow_result
    book = bundle.calculation_book
    transfer = result.practical_action_reconciliation[0]
    assert transfer.reconciled and transfer.residual_kn == 0
    assert transfer.destination_total_kn == 12
    assert book.reconciliation["all_balanced"]
    if ledger_hash is not None:
        assert result.ledger_hash == ledger_hash

    end_footing = "F1" if reversed_beam else "F2"
    start_footing = "F2" if reversed_beam else "F1"
    expected_transfer = {
        start_footing: 12 - end_transfer_kn,
        end_footing: end_transfer_kn,
    }
    original_dead_loads = {
        entry["destination_id"]: entry["magnitude_kn"]
        for entry in baseline.calculation_book.ledger_snapshot["entries"]
        if entry["stage"] == "FOOTING_ACTION" and entry["case_id"] == "DL"
    }
    for entry in book.ledger_snapshot["entries"]:
        if entry["stage"] == "FOOTING_ACTION" and entry["case_id"] == "DL":
            footing = entry["destination_id"]
            assert entry["magnitude_kn"] - original_dead_loads[
                footing
            ] == pytest.approx(expected_transfer.get(footing, 0))

    original_actions = {
        item.action_id: item for item in baseline.workflow_result.actions
    }
    if station_mm in (0.0, span_mm):
        for combination in ("SERVICE_DL_LL", "ULS_1_5_DL_LL"):
            action_id = f"action:{combination}:B1"
            beam = next(item for item in result.actions if item.action_id == action_id)
            assert beam.moment_knm == original_actions[action_id].moment_knm
            assert beam.shear_kn == original_actions[action_id].shear_kn
            assert "apply:DL:practical:EQUIPMENT_B1_DL" in beam.source_entry_ids

    for action in result.actions:
        if action.kind.value == "FOOTING" and action.combination_id == "ULS_1_5_DL_LL":
            assert action.axial_kn == pytest.approx(
                original_actions[action.action_id].axial_kn
                + 1.5 * expected_transfer.get(action.component_id, 0)
            )


def test_practical_action_destination_and_point_station_fail_closed() -> None:
    building = _building()
    point = _practical_actions()[2]
    payload = point.model_dump(mode="python")
    payload["destination_id"] = "P1"
    wrong_destination = GravityPracticalActionV1.model_validate(payload)
    with pytest.raises(ValidationError, match="known beam destination"):
        _request(building, practical_actions=(wrong_destination,))

    payload = point.model_dump(mode="python")
    payload["point_position_mm"] = 8002
    outside_span = GravityPracticalActionV1.model_validate(payload)
    with pytest.raises(ValidationError, match="position must lie within"):
        _request(_building_with_x_span(8001), practical_actions=(outside_span,))


def test_missing_prerequisites_preserve_every_component_as_hold() -> None:
    result = run_gravity_workflow_v1(_request())

    assert len(result.components) == 11
    assert result.result_envelope["overall_status"] == "HOLD"
    assert {item.result_envelope["overall_status"] for item in result.components} == {
        "HOLD"
    }
    assert result.result_envelope["issues"]
    panel = next(
        item for item in result.applicability.entries if item.component_id == "P1"
    )
    assert panel.hold_reasons == (
        "SLAB_DESIGN_BASIS_NOT_SUPPLIED",
        "SLAB_COMPONENT_REQUIRES_EFFECTIVE_ASPECT_RATIO_GT_2",
    )
    assert all(item.result is None for item in result.components)


def test_one_way_slab_direction_must_itself_have_supported_aspect_ratio() -> None:
    request = _request(_building_with_x_span(10_000))
    matrix = build_component_applicability_matrix_v1(request)
    panel = next(item for item in matrix.entries if item.component_id == "P1")
    assert panel.hold_reasons == ("SLAB_DESIGN_BASIS_NOT_SUPPLIED",)

    request = _request(_building_with_x_span(3_000))
    matrix = build_component_applicability_matrix_v1(request)
    panel = next(item for item in matrix.entries if item.component_id == "P1")
    assert "SLAB_COMPONENT_REQUIRES_EFFECTIVE_ASPECT_RATIO_GT_2" in panel.hold_reasons


def test_supported_slab_beam_and_column_bases_call_canonical_components() -> None:
    request = _request(
        _building_with_x_span(10_000), with_supported_component_bases=True
    )
    result = run_gravity_workflow_v1(request)
    by_id = {item.component_id: item for item in result.components}

    for component_id in ("P1", "C1", "C2", "C3", "C4"):
        assert by_id[component_id].result is not None
        assert by_id[component_id].result_envelope["overall_status"] in {
            "PASS",
            "FAIL",
        }
    for component_id in ("B1", "B2"):
        assert by_id[component_id].result is not None
        assert by_id[component_id].result_envelope["overall_status"] == "HOLD"
        assert by_id[component_id].result["reinforcement_evaluation"]["status"] == (
            "HOLD"
        )
        assert by_id[component_id].result_envelope["issues"][0]["code"] == (
            "BEAM_REINFORCEMENT_BASIS_NOT_SUPPLIED"
        )
    for component_id in ("F1", "F2", "F3", "F4"):
        assert by_id[component_id].result is None
        assert by_id[component_id].result_envelope["overall_status"] == "HOLD"
    assert result.result_envelope["overall_status"] == "HOLD"


@pytest.mark.parametrize("end_condition", ["FIXED_FIXED_SWAY", "FIXED_FREE"])
def test_incompatible_column_restraint_holds_before_design(
    end_condition: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    from structural_lib.services import gravity_workflow

    request = _request(with_supported_component_bases=True)
    baseline = run_gravity_workflow_v1(request)
    baseline_column = next(
        item for item in baseline.components if item.component_id == "C1"
    )
    assert baseline_column.result_envelope["overall_status"] == "PASS"
    assert baseline_column.result["le_x_mm"] == 1950

    original_design = gravity_workflow.design_column_is456

    def design_braced_column(**kwargs):
        assert kwargs["end_condition"] == "FIXED_FIXED"
        return original_design(**kwargs)

    monkeypatch.setattr(gravity_workflow, "design_column_is456", design_braced_column)
    first, *siblings = request.column_design_bases
    incompatible = GravityColumnDesignBasisV1.model_validate(
        {**first.model_dump(), "end_condition": end_condition}
    )
    request = request.model_copy(
        update={"column_design_bases": (incompatible, *siblings)}
    )
    bundle = run_gravity_workflow_with_book_v1(request)
    result = bundle.workflow_result
    columns = {
        item.component_id: item
        for item in result.components
        if item.kind.value == "COLUMN"
    }
    assert columns["C1"].result is None
    assert columns["C1"].action_ids == baseline_column.action_ids
    assert columns["C1"].result_envelope["overall_status"] == "HOLD"
    assert columns["C1"].result_envelope["issues"][0]["code"] == (
        "COLUMN_RESTRAINT_OUTSIDE_BRACED_SCOPE"
    )
    entry = next(
        item for item in result.applicability.entries if item.component_id == "C1"
    )
    assert entry.disposition.value == "HOLD"
    assert entry.hold_reasons == ("COLUMN_RESTRAINT_OUTSIDE_BRACED_SCOPE",)
    assert columns["C2"].result_envelope["overall_status"] == "PASS"
    assert result.actions == baseline.actions
    assert result.model_hash == baseline.model_hash
    assert result.load_model_hash == baseline.load_model_hash
    assert result.ledger_hash == baseline.ledger_hash
    assert bundle.calculation_book.design_basis_snapshot["COLUMN"]["C1"] == (
        incompatible.model_dump(mode="json")
    )


def test_beam_selection_basis_recommends_bars_but_missing_supply_holds() -> None:
    request = _request(
        with_supported_component_bases=True,
        beam_reinforcement_basis=_beam_reinforcement_basis(supplied=False),
    )
    result = run_gravity_workflow_v1(request)
    beam = next(item for item in result.components if item.component_id == "B1")

    evaluation = beam.result["reinforcement_evaluation"]
    assert beam.result_envelope["overall_status"] == "HOLD"
    assert evaluation["recommended_tension"] is not None
    assert evaluation["supplied_tension"] is None
    assert beam.result_envelope["calculation_status"] == "COMPLETED"
    assert beam.result_envelope["issues"][0]["code"] == (
        "BEAM_SUPPLIED_REINFORCEMENT_NOT_SUPPLIED"
    )


def test_source_referenced_supplied_beam_bars_can_reach_bounded_pass() -> None:
    request = _request(
        _building_with_square_column_width(1600),
        with_supported_component_bases=True,
        beam_effective_depth_mm=459,
        beam_reinforcement_basis=_beam_reinforcement_basis(supplied=True),
    )
    result = run_gravity_workflow_v1(request)
    beams = [item for item in result.components if item.kind.value == "BEAM"]

    assert {item.result_envelope["overall_status"] for item in beams} == {"PASS"}
    assert {item.result["reinforcement_evaluation"]["status"] for item in beams} == {
        "PASS"
    }


def test_inadequate_source_referenced_beam_bars_fail() -> None:
    request = _request(
        _building_with_square_column_width(1600),
        with_supported_component_bases=True,
        beam_effective_depth_mm=459,
        beam_reinforcement_basis=_beam_reinforcement_basis(
            supplied=True, tension_count=2
        ),
    )
    result = run_gravity_workflow_v1(request)
    beam = next(item for item in result.components if item.component_id == "B1")

    assert beam.result_envelope["overall_status"] == "FAIL"
    assert beam.result["reinforcement_evaluation"]["status"] == "FAIL"
    assert beam.result_envelope["issues"][0]["code"] == (
        "BEAM_TENSION_REINFORCEMENT_AREA_INSUFFICIENT"
    )


def test_excessive_supplied_compression_area_reaches_gravity_envelope() -> None:
    reinforcement = _beam_reinforcement_basis(supplied=True).model_copy(
        update={
            "permitted_diameters_mm": (12, 16, 20, 32),
            "maximum_layers": 3,
            "supplied_compression_or_hanger": GravityLongitudinalBarLayersV1(
                diameter_mm=32,
                bars_per_layer=(3, 3, 3),
                vertical_center_spacings_mm=(64, 64),
            ),
        }
    )
    request = _request(
        _building_with_square_column_width(1600),
        with_supported_component_bases=True,
        beam_effective_depth_mm=459,
        beam_reinforcement_basis=reinforcement,
    )
    result = run_gravity_workflow_v1(request)
    beam_result = next(item for item in result.components if item.component_id == "B1")

    assert beam_result.result_envelope["overall_status"] == "FAIL"
    evaluation = beam_result.result["reinforcement_evaluation"]
    assert evaluation["checks"]["compression_area"]["maximum_mm2"] == 6000.0
    assert [issue["code"] for issue in evaluation["issues"]] == [
        "BEAM_COMPRESSION_REINFORCEMENT_AREA_EXCESSIVE"
    ]


def test_component_failure_remains_fail_while_other_missing_basis_holds_aggregate() -> (
    None
):
    request = _request(
        _building_with_x_span(10_000),
        with_supported_component_bases=True,
        beam_effective_depth_mm=200,
        beam_reinforcement_basis=_beam_reinforcement_basis(supplied=True),
    )
    result = run_gravity_workflow_v1(request)
    by_id = {item.component_id: item for item in result.components}

    assert by_id["B1"].result_envelope["overall_status"] == "FAIL"
    assert by_id["B2"].result_envelope["overall_status"] == "FAIL"
    assert by_id["B1"].result_envelope["issues"][0]["code"] == (
        "BEAM_DESIGN_CHECK_FAILED"
    )
    assert by_id["B1"].result["reinforcement_evaluation"]["status"] == "HOLD"
    assert by_id["F1"].result_envelope["overall_status"] == "HOLD"
    assert result.result_envelope["overall_status"] == "HOLD"
    assert result.result_envelope["issues"]


def test_slab_capacity_failure_remains_structured_component_fail() -> None:
    request = _request(
        _building_with_x_span(10_000),
        with_supported_component_bases=True,
        superimposed_dead_load_kn_m2=50,
        live_load_kn_m2=50,
    )

    result = run_gravity_workflow_v1(request)
    slab = next(item for item in result.components if item.component_id == "P1")

    assert slab.result_envelope["intake_status"] == "VALID"
    assert slab.result_envelope["calculation_status"] == "COMPLETED"
    assert slab.result_envelope["engineering_status"] == "FAIL"
    assert slab.result_envelope["issues"][0]["code"] == "SLAB_GOVERNING_FAIL"
    assert slab.result is not None
    assert slab.result["reinforcement"]["flexure"]["status"] == "FAIL"
    assert slab.result["shear"] is None
    assert slab.result["serviceability"] is None


def test_footing_cannot_relabel_superstructure_handoff_as_complete_external_action() -> (
    None
):
    base = _request()
    request = GravityWorkflowRequestV1(
        model_hash=base.model_hash,
        load_model_hash=base.load_model_hash,
        building=base.building,
        loads=base.loads,
        footing_design_bases=(
            _footing_basis(service_axial_kn=67.5, factored_axial_kn=101.25),
        ),
    )

    result = run_gravity_workflow_v1(request)
    footing = next(item for item in result.components if item.component_id == "F1")
    assert footing.result is None
    assert footing.result_envelope["overall_status"] == "HOLD"
    assert footing.result_envelope["issues"][0]["code"] == (
        "FOOTING_EXTERNAL_ACTION_NOT_ADDED"
    )


def test_complete_external_footing_basis_calls_canonical_footing_component() -> None:
    base = _request()
    request = GravityWorkflowRequestV1(
        model_hash=base.model_hash,
        load_model_hash=base.load_model_hash,
        building=base.building,
        loads=base.loads,
        footing_design_bases=(
            _footing_basis(service_axial_kn=75, factored_axial_kn=112.5),
        ),
    )

    result = run_gravity_workflow_v1(request)
    footing = next(item for item in result.components if item.component_id == "F1")
    assert footing.canonical_function == "design_concentric_isolated_footing_is456"
    assert footing.result is not None
    assert footing.result_envelope["overall_status"] == "FAIL"
    assert footing.result_envelope["issues"][0]["code"] == ("FOOTING_GOVERNING_FAIL")
    assert footing.result["status"] == "FAIL"


def test_result_and_action_hashes_are_deterministic_for_same_accepted_request() -> None:
    first = run_gravity_workflow_v1(_request())
    second = run_gravity_workflow_v1(_request())

    assert first.actions == second.actions
    assert first.ledger_hash == second.ledger_hash
    assert first.workflow_result_hash == second.workflow_result_hash


def test_calculation_book_binds_reconciliation_holds_and_review_disposition() -> None:
    bundle = run_gravity_workflow_with_book_v1(_request())
    book = bundle.calculation_book

    assert book.workflow_result_hash == bundle.workflow_result.workflow_result_hash
    assert book.reconciliation["all_balanced"] is True
    assert book.reconciliation["boundary_count"] == 26
    assert book.reconciliation["maximum_absolute_residual_kn"] == 0.0
    assert book.review_disposition == "QUALIFIED_REVIEW_REQUIRED"
    assert len(book.issues) == 11
    markdown = render_gravity_calculation_book_markdown_v1(book)
    assert "# Building Gravity Workflow V1 Calculation Book" in markdown
    assert "| F1 | FOOTING | HOLD |" in markdown
    assert "Qualified structural-engineering review remains required" in markdown


def test_book_binds_typed_design_inputs_and_retains_references_on_hold() -> None:
    request = _request(with_supported_component_bases=True)
    footing = _footing_basis(service_axial_kn=200, factored_axial_kn=300)
    request = request.model_copy(update={"footing_design_bases": (footing,)})
    first, *other_beams = request.beam_design_bases
    revised_beam = first.model_copy(
        update={"effective_depth_source_reference": "Reviewed B1 drawing revision B"}
    )
    revised = request.model_copy(
        update={"beam_design_bases": (revised_beam, *other_beams)}
    )
    original_bundle = run_gravity_workflow_with_book_v1(request)
    revised_bundle = run_gravity_workflow_with_book_v1(revised)
    result = original_bundle.workflow_result
    revised_result = revised_bundle.workflow_result
    book = revised_bundle.calculation_book

    assert result.model_hash == revised_result.model_hash
    assert result.load_model_hash == revised_result.load_model_hash
    assert result.ledger_hash == revised_result.ledger_hash
    assert result.workflow_result_hash == revised_result.workflow_result_hash
    assert result.design_basis_hash != revised_result.design_basis_hash
    assert book.design_basis_hash == revised_result.design_basis_hash
    assert book.design_basis_snapshot["BEAM"]["B1"] == revised_beam.model_dump(
        mode="json"
    )
    assert book.design_basis_snapshot["SLAB"]["P1"] == revised.slab_design_bases[
        0
    ].model_dump(mode="json")
    assert book.design_basis_snapshot["COLUMN"]["C1"] == revised.column_design_bases[
        0
    ].model_dump(mode="json")
    assert book.design_basis_snapshot["FOOTING"]["F1"] == footing.model_dump(
        mode="json"
    )
    slab = next(item for item in book.components if item.component_id == "P1")
    assert slab.result_envelope["overall_status"] == "HOLD"
    round_trip = GravityCalculationBookV1.model_validate_json(book.model_dump_json())
    markdown = render_gravity_calculation_book_markdown_v1(round_trip)
    assert round_trip == book
    assert "Reviewed B1 drawing revision B" in markdown
    assert "125 mm reviewed effective depth" in markdown

    with pytest.raises(ValueError, match="design basis identity does not match"):
        build_gravity_calculation_book_v1(revised, result)
    shallower_beam = first.model_copy(update={"d_mm": 400})
    different_depth = request.model_copy(
        update={"beam_design_bases": (shallower_beam, *other_beams)}
    )
    assert different_depth.load_model_hash == request.load_model_hash
    with pytest.raises(ValueError, match="design basis identity does not match"):
        build_gravity_calculation_book_v1(different_depth, result)
    with pytest.raises(ValueError, match="no design basis identity; rerun"):
        build_gravity_calculation_book_v1(
            request, result.model_copy(update={"design_basis_hash": None})
        )


def test_member_actions_reject_stale_model_or_load_ledger() -> None:
    request = _request()
    ledger = build_gravity_load_ledger_v1(request.building, request.loads)
    for revised in (_request(live_load_kn_m2=6), _request(_building_with_x_span(8001))):
        with pytest.raises(ValueError, match="ledger model or load-model identity"):
            build_gravity_member_actions_v1(revised, ledger)

    current = _request(live_load_kn_m2=6)
    actions = build_gravity_member_actions_v1(
        current, build_gravity_load_ledger_v1(current.building, current.loads)
    )
    beam = next(item for item in actions if item.action_id == "action:ULS_1_5_DL_LL:B1")
    assert beam.moment_knm == pytest.approx(177.1875)


def test_cli_emits_same_versioned_bundle_from_json_request(tmp_path: Path) -> None:
    from structural_lib.__main__ import main

    request = _request(with_supported_component_bases=True)
    request_path = tmp_path / "request.json"
    output_path = tmp_path / "calculation-book.json"
    request_path.write_text(
        json.dumps(
            request.model_dump(
                mode="json",
                exclude={
                    "building": {"accepted_model_hash": True},
                    "loads": {"load_model_hash": True},
                },
            )
        ),
        encoding="utf-8",
    )

    assert main(["gravity-v1", str(request_path), "-o", str(output_path)]) == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "gravity-workflow-run-bundle/v1"
    assert payload["workflow_result"]["result_envelope"]["overall_status"] == "HOLD"
    assert payload["calculation_book"]["reconciliation"]["all_balanced"] is True
    book = payload["calculation_book"]
    assert book["design_basis_hash"] == payload["workflow_result"]["design_basis_hash"]
    assert book["design_basis_snapshot"]["BEAM"]["B1"][
        "effective_depth_source_reference"
    ] == ("450 mm reviewed effective depth")

    markdown_path = tmp_path / "calculation-book.md"
    assert (
        main(
            [
                "gravity-v1",
                str(request_path),
                "--format",
                "markdown",
                "-o",
                str(markdown_path),
            ]
        )
        == 0
    )
    assert "450 mm reviewed effective depth" in markdown_path.read_text(
        encoding="utf-8"
    )
