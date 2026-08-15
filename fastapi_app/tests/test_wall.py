"""Contract tests for the bounded braced-wall FastAPI slice."""

from __future__ import annotations

from copy import deepcopy

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_app.routers.wall import router


def _app() -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    return app


def _payload() -> dict[str, object]:
    return {
        "case_id": "INDIA-2-WALL-HAND-01",
        "unsupported_height_mm": 3000.0,
        "lateral_restraint_spacing_mm": 4000.0,
        "wall_length_mm": 4000.0,
        "wall_thickness_mm": 150.0,
        "concrete_grade_nmm2": 20.0,
        "factored_axial_load_kn": 2000.0,
        "supplied_eccentricity_mm": 0.0,
        "vertical_bar_diameter_mm": 8.0,
        "vertical_bar_spacing_mm": 250.0,
        "horizontal_bar_diameter_mm": 10.0,
        "horizontal_bar_spacing_mm": 250.0,
        "bracing_basis_reference": "INDIA-2-WALL-HAND-01-BRACING",
        "action_basis_reference": "INDIA-2-WALL-HAND-01-ACTIONS",
        "reinforcement_basis_reference": ("INDIA-2-WALL-HAND-01-REINFORCEMENT"),
    }


def test_wall_benchmark_returns_typed_pass_with_provenance() -> None:
    response = TestClient(_app()).post(
        "/api/v1/design/wall/braced-axial",
        json=_payload(),
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "PASS"
    assert data["axial"]["effective_height_mm"] == pytest.approx(2250.0)
    assert data["axial"]["axial_capacity_n_per_mm"] == pytest.approx(684.0)
    assert data["axial"]["utilization_ratio"] == pytest.approx(0.7309941520)
    assert data["reinforcement"]["vertical"][
        "provided_area_mm2_per_m"
    ] == pytest.approx(201.06192983)
    assert data["reinforcement"]["horizontal"][
        "provided_area_mm2_per_m"
    ] == pytest.approx(314.15926536)
    assert data["provenance"]["workflow"] == "design_braced_wall_is456"
    assert data["provenance"]["clause_refs"] == [
        "32.2.1",
        "32.2.2",
        "32.2.3",
        "32.2.4",
        "32.2.5",
        "32.5",
        "32.5.1",
        "32.5.2",
    ]
    assert data["held_cases"] and data["qualified_review_required"] is True
    assert data["complete_engineering_design_approved"] is False


def test_wall_rejects_unknown_nonfinite_and_unsupported_scope() -> None:
    client = TestClient(_app())
    invalid_requests: list[dict[str, object]] = []

    extra = deepcopy(_payload())
    extra["not_a_contract_field"] = True
    invalid_requests.append(extra)
    nonfinite = deepcopy(_payload())
    nonfinite["wall_length_mm"] = "NaN"
    invalid_requests.append(nonfinite)
    alternate = deepcopy(_payload())
    alternate["bracing_elements_in_two_directions"] = False
    invalid_requests.append(alternate)
    two_grid = deepcopy(_payload())
    two_grid["wall_thickness_mm"] = 201.0
    invalid_requests.append(two_grid)

    for invalid in invalid_requests:
        response = client.post("/api/v1/design/wall/braced-axial", json=invalid)
        assert response.status_code == 422


def test_wall_service_validation_uses_safe_error_envelope() -> None:
    invalid = deepcopy(_payload())
    invalid["unsupported_height_mm"] = 6100.0
    invalid["lateral_restraint_spacing_mm"] = 6100.0
    invalid["wall_thickness_mm"] = 150.0

    response = TestClient(_app()).post(
        "/api/v1/design/wall/braced-axial",
        json=invalid,
    )

    assert response.status_code == 422
    body = response.json()
    assert set(body) == {"success", "data", "error"}
    assert body["success"] is False and body["data"] is None
    assert body["error"]["code"] == "REQUEST_VALIDATION_ERROR"
    assert body["error"]["message"] == "Request validation failed"
    assert body["error"]["details"][0]["msg"].startswith(
        "Error during braced wall. Reference:"
    )


def test_wall_valid_overload_and_inadequate_steel_remain_json_safe_fail() -> None:
    overloaded = deepcopy(_payload())
    overloaded["factored_axial_load_kn"] = 3000.0
    overload_response = TestClient(_app()).post(
        "/api/v1/design/wall/braced-axial",
        json=overloaded,
    )
    assert overload_response.status_code == 200
    assert overload_response.json()["data"]["axial"]["status"] == "FAIL"
    assert overload_response.json()["data"]["status"] == "FAIL"

    inadequate = deepcopy(_payload())
    inadequate.update(
        {
            "vertical_bar_diameter_mm": 6.0,
            "vertical_bar_spacing_mm": 450.0,
            "horizontal_bar_diameter_mm": 6.0,
            "horizontal_bar_spacing_mm": 450.0,
        }
    )
    inadequate_response = TestClient(_app()).post(
        "/api/v1/design/wall/braced-axial",
        json=inadequate,
    )
    assert inadequate_response.status_code == 200
    assert inadequate_response.json()["data"]["reinforcement"]["status"] == "FAIL"
    assert inadequate_response.json()["data"]["status"] == "FAIL"


def test_wall_openapi_exposes_typed_success_schema() -> None:
    schema = _app().openapi()
    operation = schema["paths"]["/api/v1/design/wall/braced-axial"]["post"]

    assert operation["responses"]["200"]["content"]["application/json"]["schema"][
        "$ref"
    ].endswith("APIResponse_BracedWallResponse_")
    response_schema = schema["components"]["schemas"]["BracedWallResponse"]
    assert response_schema["properties"]["axial"]
    assert response_schema["properties"]["reinforcement"]


def test_wall_is_mounted_in_main_app(client: TestClient) -> None:
    response = client.post("/api/v1/design/wall/braced-axial", json=_payload())

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "PASS"
