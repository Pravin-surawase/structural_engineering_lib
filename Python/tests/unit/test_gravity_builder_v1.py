"""Maintained onboarding and governing-result tests for Gravity Workflow V1."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import structural_lib
from structural_lib.__main__ import main
from structural_lib.core.gravity_workflow import GravityWorkflowRequestV1
from structural_lib.services.gravity_builder import (
    RectangularGravityWorkflowBuilderInputV1,
    get_gravity_workflow_example_document_v1,
    get_gravity_workflow_example_request_v1,
)
from structural_lib.services.gravity_calculation_book import (
    get_gravity_workflow_definition_v1,
    render_gravity_calculation_book_markdown_v1,
    run_gravity_workflow_with_book_v1,
)


def test_builder_has_no_hidden_engineering_defaults() -> None:
    optional_fields = {
        name
        for name, field in RectangularGravityWorkflowBuilderInputV1.model_fields.items()
        if not field.is_required()
    }

    assert optional_fields == {"schema_version"}


def test_maintained_example_reproduces_the_practical_open_hall() -> None:
    request = get_gravity_workflow_example_request_v1()
    bundle = run_gravity_workflow_with_book_v1(request)
    result = bundle.workflow_result
    actions = {item.action_id: item for item in result.actions}
    components = {item.component_id: item for item in result.components}

    assert request.building.nodes[-1].x_mm == 10_000
    assert request.building.nodes[-1].y_mm == 4_000
    assert request.building.nodes[-1].z_mm == 3_000
    assert actions["action:ULS_1_5_DL_LL:P1"].area_load_kn_m2 == pytest.approx(12.375)
    assert actions["action:ULS_1_5_DL_LL:B1"].line_load_kn_m == pytest.approx(32.625)
    assert actions["action:ULS_1_5_DL_LL:B1"].moment_knm == pytest.approx(407.8125)
    assert actions["action:ULS_1_5_DL_LL:B1"].shear_kn == pytest.approx(163.125)
    assert actions["action:ULS_1_5_DL_LL:C1"].axial_kn == pytest.approx(173.25)

    assert {
        components[item].result_envelope["overall_status"]
        for item in ("P1", "B1", "B2", "C1", "C2", "C3", "C4")
    } == {"PASS"}
    assert {
        components[item].result_envelope["overall_status"]
        for item in ("F1", "F2", "F3", "F4")
    } == {"HOLD"}
    footing = components["F1"].result
    assert footing is not None
    assert footing["calculation_status"] == "PASS"
    assert footing["detailing_status"] == "HOLD"
    assert footing["bearing"]["q_max_kPa"] == pytest.approx(179.93079584775086)
    assert footing["flexure"]["Mu_L_kNm"] == pytest.approx(8.674632352941178)

    governing = result.result_envelope["issues"][0]
    assert result.result_envelope["overall_status"] == "HOLD"
    assert governing["code"] == "FOOTING_GOVERNING_HOLD"
    assert governing["path"] == "$.components.F1"
    assert "hooks or bends" in governing["message"]
    assert bundle.calculation_book.reconciliation == {
        "all_balanced": True,
        "boundary_count": 26,
        "maximum_absolute_residual_kn": 0.0,
        "balance_tolerance_kn": 1e-9,
        "accepted_entry_count": 41,
        "blocked_entry_count": 0,
    }
    markdown = render_gravity_calculation_book_markdown_v1(bundle.calculation_book)
    assert "Governing reason: `FOOTING_GOVERNING_HOLD`" in markdown


def test_example_document_round_trips_as_strict_request() -> None:
    document = get_gravity_workflow_example_document_v1()
    request = GravityWorkflowRequestV1.model_validate(document)

    assert "accepted_model_hash" not in document["building"]
    assert "load_model_hash" not in document["loads"]
    assert request == get_gravity_workflow_example_request_v1()
    assert get_gravity_workflow_definition_v1().example_request == document


def test_package_root_exports_the_complete_gravity_onboarding_surface() -> None:
    request = structural_lib.get_gravity_workflow_example_request_v1()
    result = structural_lib.run_gravity_workflow_with_book_v1(request)

    assert isinstance(request, structural_lib.GravityWorkflowRequestV1)
    assert result.workflow_result.result_envelope["overall_status"] == "HOLD"
    assert structural_lib.get_gravity_workflow_example_document_v1() == (
        get_gravity_workflow_example_document_v1()
    )


def test_cli_example_is_runnable_without_repository_fixtures(tmp_path: Path) -> None:
    request_path = tmp_path / "gravity-example.json"
    result_path = tmp_path / "gravity-result.json"

    assert main(["gravity-v1", "example", "-o", str(request_path)]) == 0
    emitted = json.loads(request_path.read_text(encoding="utf-8"))
    assert GravityWorkflowRequestV1.model_validate(emitted)
    assert main(["gravity-v1", str(request_path), "-o", str(result_path)]) == 0

    result = json.loads(result_path.read_text(encoding="utf-8"))
    assert result["workflow_result"]["result_envelope"]["issues"][0]["code"] == (
        "FOOTING_GOVERNING_HOLD"
    )
