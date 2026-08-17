"""REST semantic vectors for Building Gravity Workflow V1."""

from structural_lib.core.gravity_workflow import GravityWorkflowRequestV1
from tests.unit.test_building_gravity_v1 import _building, _loads


def _request_payload() -> dict:
    building = _building()
    loads = _loads(building)
    request = GravityWorkflowRequestV1(
        model_hash=building.accepted_model_hash,
        load_model_hash=loads.load_model_hash,
        building=building,
        loads=loads,
    )
    return request.model_dump(
        mode="json",
        exclude={
            "building": {"accepted_model_hash": True},
            "loads": {"load_model_hash": True},
        },
    )


def test_building_gravity_definition_declares_all_product_surfaces(client) -> None:
    response = client.get("/api/v1/building-gravity/v1/definition")

    assert response.status_code == 200
    definition = response.json()["data"]
    assert definition["capability_id"] == "building.gravity.dead-live.v1"
    assert definition["product_surfaces"] == {
        "python": "structural_lib.services.gravity_workflow.run_gravity_workflow_v1",
        "cli": "python -m structural_lib gravity-v1 REQUEST.json",
        "rest": "POST /api/v1/building-gravity/v1/run",
        "review_ui": "/workbench/building-gravity/v1",
    }
    assert definition["qualified_review_required"] is True


def test_building_gravity_route_preserves_actions_holds_and_calculation_book(
    client,
) -> None:
    response = client.post("/api/v1/building-gravity/v1/run", json=_request_payload())

    assert response.status_code == 200
    data = response.json()["data"]
    workflow = data["workflow_result"]
    book = data["calculation_book"]
    assert workflow["result_envelope"]["overall_status"] == "HOLD"
    assert len(workflow["actions"]) == 22
    assert len(workflow["components"]) == 11
    assert book["workflow_result_hash"] == workflow["workflow_result_hash"]
    assert book["reconciliation"] == {
        "all_balanced": True,
        "boundary_count": 26,
        "maximum_absolute_residual_kn": 0.0,
        "balance_tolerance_kn": 1e-09,
        "accepted_entry_count": 41,
        "blocked_entry_count": 0,
    }
    footing = next(
        item
        for item in workflow["actions"]
        if item["action_id"] == "action:ULS_1_5_DL_LL:F1"
    )
    assert footing["axial_kn"] == 101.25


def test_building_gravity_route_rejects_unknown_input_without_calculation(
    client,
) -> None:
    payload = _request_payload()
    payload["building"]["unexpected"] = "not accepted"

    response = client.post("/api/v1/building-gravity/v1/run", json=payload)

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "REQUEST_VALIDATION_ERROR"
