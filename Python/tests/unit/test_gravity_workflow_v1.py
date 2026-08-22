"""Focused actions, prerequisite, and fail-closed tests for Gravity Workflow V1."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from structural_lib.core.building_gravity import BuildingModelV1, GravityMemberKindV1
from structural_lib.core.gravity_workflow import (
    GravityBeamDesignBasisV1,
    GravityColumnDesignBasisV1,
    GravityFootingDesignBasisV1,
    GravitySlabDesignBasisV1,
    GravityWorkflowRequestV1,
)
from structural_lib.services.gravity_calculation_book import (
    render_gravity_calculation_book_markdown_v1,
    run_gravity_workflow_with_book_v1,
)
from structural_lib.services.gravity_loads import build_gravity_load_ledger_v1
from structural_lib.services.gravity_workflow import (
    build_component_applicability_matrix_v1,
    build_gravity_member_actions_v1,
    run_gravity_workflow_v1,
)
from tests.unit.test_building_gravity_v1 import _building, _loads


def _request(
    building: BuildingModelV1 | None = None,
    *,
    with_supported_component_bases: bool = False,
    beam_effective_depth_mm: float = 450,
    superimposed_dead_load_kn_m2: float = 1.5,
    live_load_kn_m2: float = 3.0,
) -> GravityWorkflowRequestV1:
    building = building or _building()
    loads = _loads(
        building,
        superimposed_dead_load_kn_m2=superimposed_dead_load_kn_m2,
        live_load_kn_m2=live_load_kn_m2,
    )
    slab_bases: tuple[GravitySlabDesignBasisV1, ...] = ()
    beam_bases: tuple[GravityBeamDesignBasisV1, ...] = ()
    column_bases: tuple[GravityColumnDesignBasisV1, ...] = ()
    if with_supported_component_bases:
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
                effective_depth_source_reference="450 mm reviewed effective depth",
            )
            for member in building.members
            if member.kind is GravityMemberKindV1.BEAM
        )
        column_bases = tuple(
            GravityColumnDesignBasisV1(
                column_id=member.id,
                fy_nmm2=415,
                Asc_mm2=1800,
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


def test_missing_prerequisites_preserve_every_component_as_hold() -> None:
    result = run_gravity_workflow_v1(_request())

    assert len(result.components) == 11
    assert result.result_envelope["overall_status"] == "HOLD"
    assert {item.result_envelope["overall_status"] for item in result.components} == {
        "HOLD"
    }
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

    for component_id in ("P1", "B1", "B2", "C1", "C2", "C3", "C4"):
        assert by_id[component_id].result is not None
        assert by_id[component_id].result_envelope["overall_status"] in {
            "PASS",
            "FAIL",
        }
    for component_id in ("F1", "F2", "F3", "F4"):
        assert by_id[component_id].result is None
        assert by_id[component_id].result_envelope["overall_status"] == "HOLD"
    assert result.result_envelope["overall_status"] == "HOLD"


def test_component_failure_remains_fail_while_other_missing_basis_holds_aggregate() -> (
    None
):
    request = _request(
        _building_with_x_span(10_000),
        with_supported_component_bases=True,
        beam_effective_depth_mm=200,
    )
    result = run_gravity_workflow_v1(request)
    by_id = {item.component_id: item for item in result.components}

    assert by_id["B1"].result_envelope["overall_status"] == "FAIL"
    assert by_id["B2"].result_envelope["overall_status"] == "FAIL"
    assert by_id["F1"].result_envelope["overall_status"] == "HOLD"
    assert result.result_envelope["overall_status"] == "HOLD"


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


def test_cli_emits_same_versioned_bundle_from_json_request(tmp_path: Path) -> None:
    from structural_lib.__main__ import main

    request = _request()
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
