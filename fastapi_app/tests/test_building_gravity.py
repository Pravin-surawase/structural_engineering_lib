"""REST semantic vectors for Building Gravity Workflow V1."""

from structural_lib.core.building_gravity import (
    BuildingModelV1,
    ExcludedGravityActionV1,
    LoadModelV1,
)
from structural_lib.services.gravity_workflow import GravityWorkflowRequestV1


def _building_model() -> BuildingModelV1:
    nodes = [
        {"id": "N1", "x_mm": 0, "y_mm": 0, "z_mm": 0},
        {"id": "N2", "x_mm": 6000, "y_mm": 0, "z_mm": 0},
        {"id": "N3", "x_mm": 0, "y_mm": 4000, "z_mm": 0},
        {"id": "N4", "x_mm": 6000, "y_mm": 4000, "z_mm": 0},
        {"id": "N5", "x_mm": 0, "y_mm": 0, "z_mm": 3000},
        {"id": "N6", "x_mm": 6000, "y_mm": 0, "z_mm": 3000},
        {"id": "N7", "x_mm": 0, "y_mm": 4000, "z_mm": 3000},
        {"id": "N8", "x_mm": 6000, "y_mm": 4000, "z_mm": 3000},
    ]
    materials = [{"id": "M_CONC", "unit_weight_kn_m3": 25, "fck_nmm2": 25}]
    sections = [
        {
            "id": "S_SLAB",
            "kind": "SLAB",
            "material_id": "M_CONC",
            "thickness_mm": 150,
        },
        {
            "id": "S_BEAM",
            "kind": "BEAM",
            "material_id": "M_CONC",
            "width_mm": 300,
            "depth_mm": 500,
        },
        {
            "id": "S_COLUMN",
            "kind": "COLUMN",
            "material_id": "M_CONC",
            "width_mm": 300,
            "depth_mm": 300,
        },
    ]
    panels = [
        {
            "id": "P1",
            "corner_node_ids": ["N5", "N6", "N7", "N8"],
            "section_id": "S_SLAB",
            "supporting_beam_ids": ["B1", "B2"],
            "load_path_id": "LP_PANEL_P1",
            "render_id": "RENDER_PANEL_P1",
        }
    ]
    members = [
        {
            "id": "B1",
            "kind": "BEAM",
            "start_node_id": "N5",
            "end_node_id": "N6",
            "section_id": "S_BEAM",
            "support_idealization": "BEAM_SIMPLY_SUPPORTED",
            "load_path_id": "LP_BEAM_B1",
            "render_id": "RENDER_BEAM_B1",
        },
        {
            "id": "B2",
            "kind": "BEAM",
            "start_node_id": "N7",
            "end_node_id": "N8",
            "section_id": "S_BEAM",
            "support_idealization": "BEAM_SIMPLY_SUPPORTED",
            "load_path_id": "LP_BEAM_B2",
            "render_id": "RENDER_BEAM_B2",
        },
        *[
            {
                "id": f"C{index}",
                "kind": "COLUMN",
                "start_node_id": f"N{index}",
                "end_node_id": f"N{index + 4}",
                "section_id": "S_COLUMN",
                "support_idealization": "COLUMN_BRACED_AXIAL_ONLY",
                "load_path_id": f"LP_COLUMN_C{index}",
                "render_id": f"RENDER_COLUMN_C{index}",
            }
            for index in range(1, 5)
        ],
    ]
    footings = [
        {
            "id": f"F{index}",
            "column_id": f"C{index}",
            "node_id": f"N{index}",
            "load_path_id": f"LP_FOOTING_F{index}",
        }
        for index in range(1, 5)
    ]
    entity_ids = [
        item["id"]
        for group in (nodes, materials, sections, panels, members, footings)
        for item in group
    ]
    return BuildingModelV1.model_validate(
        {
            "model_id": "FASTAPI_HAND_MODEL_01",
            "project_id": "FASTAPI_HAND_PROJECT_01",
            "raw_source_hash": "1" * 64,
            "nodes": nodes,
            "materials": materials,
            "sections": sections,
            "panels": panels,
            "members": members,
            "footing_destinations": footings,
            "source_records": [
                {
                    "source_index": index,
                    "source_id": f"fastapi-input-row-{index}",
                    "disposition": "ACCEPTED",
                    "canonical_id": entity_id,
                }
                for index, entity_id in enumerate(entity_ids)
            ],
        }
    )


def _load_model(building: BuildingModelV1) -> LoadModelV1:
    inclusions = (
        ("SLAB_SELF_WEIGHT", "GENERATED"),
        ("SLAB_SUPERIMPOSED_DEAD", "SUPPLIED"),
        ("BEAM_SELF_WEIGHT", "GENERATED"),
        ("COLUMN_SELF_WEIGHT", "GENERATED"),
        ("LIVE_OCCUPANCY", "SUPPLIED"),
    )
    return LoadModelV1.model_validate(
        {
            "model_hash": building.accepted_model_hash,
            "raw_source_hash": "4" * 64,
            "superimposed_dead_load_kn_m2": 1.5,
            "live_load_kn_m2": 3.0,
            "live_load_category": "OFFICE_UNREDUCED",
            "source_references": [
                {
                    "id": "PROJECT_BASIS",
                    "title": "FastAPI hand example load basis",
                    "reference": "B2 REST semantic vector",
                    "source_hash": "2" * 64,
                },
                {
                    "id": "COMBINATION_BASIS",
                    "title": "V1 dead and live combinations",
                    "reference": "Approved B1 combination contract",
                    "source_hash": "3" * 64,
                },
            ],
            "inclusion_rules": [
                {
                    "category": category,
                    "disposition": disposition,
                    "source_ref_id": "PROJECT_BASIS",
                }
                for category, disposition in inclusions
            ],
            "combinations": [
                {
                    "id": "SERVICE_DL_LL",
                    "state": "SERVICE",
                    "factors": [
                        {"case_id": "DL", "factor": 1.0},
                        {"case_id": "LL", "factor": 1.0},
                    ],
                    "source_ref_id": "COMBINATION_BASIS",
                },
                {
                    "id": "ULS_1_5_DL_LL",
                    "state": "FACTORED",
                    "factors": [
                        {"case_id": "DL", "factor": 1.5},
                        {"case_id": "LL", "factor": 1.5},
                    ],
                    "source_ref_id": "COMBINATION_BASIS",
                },
            ],
            "approved_exclusions": [
                {
                    "category": category.value,
                    "reason": f"{category.value} is outside bounded V1 REST scope",
                    "source_ref_id": "PROJECT_BASIS",
                }
                for category in ExcludedGravityActionV1
            ],
        }
    )


def _request_payload() -> dict:
    building = _building_model()
    loads = _load_model(building)
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
        "python": "structural_lib.run_gravity_workflow_with_book_v1",
        "python_builder": "structural_lib.build_rectangular_gravity_workflow_request_v1",
        "python_example": "structural_lib.get_gravity_workflow_example_request_v1",
        "cli_example": "python -m structural_lib gravity-v1 example",
        "cli_run": "python -m structural_lib gravity-v1 REQUEST.json",
        "rest": "POST /api/v1/building-gravity/v1/run",
        "review_ui": "/workbench/building-gravity/v1",
    }
    assert GravityWorkflowRequestV1.model_validate(definition["example_request"])
    assert "accepted_model_hash" not in definition["example_request"]["building"]
    assert "load_model_hash" not in definition["example_request"]["loads"]
    assert definition["qualified_review_required"] is True

    run = client.post(
        "/api/v1/building-gravity/v1/run", json=definition["example_request"]
    )
    assert run.status_code == 200
    envelope = run.json()["data"]["workflow_result"]["result_envelope"]
    assert envelope["overall_status"] == "HOLD"
    assert envelope["issues"][0]["code"] == ("BEAM_SUPPLIED_REINFORCEMENT_NOT_SUPPLIED")


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
