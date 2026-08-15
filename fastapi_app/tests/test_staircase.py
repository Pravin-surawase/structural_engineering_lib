"""Contract tests for the straight-flight staircase FastAPI slice."""

from __future__ import annotations

from copy import deepcopy

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_app.routers.staircase import router


def _app() -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    return app


def _payload() -> dict[str, object]:
    return {
        "case_id": "STAIR-INDIA-2-NPTEL-EX9.1",
        "lower_landing_effective_length_mm": 750.0,
        "going_mm": 2700.0,
        "upper_landing_effective_length_mm": 1650.0,
        "flight_width_mm": 1500.0,
        "riser_mm": 160.0,
        "tread_mm": 270.0,
        "waist_thickness_mm": 250.0,
        "landing_thickness_mm": 200.0,
        "lower_landing_superimposed_service_load_kn_per_m2": 6.0,
        "flight_superimposed_service_load_kn_per_m2": 6.0,
        "upper_landing_superimposed_service_load_kn_per_m2": 6.0,
        "lower_landing_load_share": 0.5,
        "upper_landing_load_share": 1.0,
        "concrete_unit_weight_kn_per_m3": 25.0,
        "ultimate_load_factor": 1.5,
        "load_basis_reference": "NPTEL-M9L20-EX9.1",
        "effective_depth_mm": 224.0,
        "fck_n_per_mm2": 20.0,
        "fy_n_per_mm2": 415.0,
        "main_bar_diameter_mm": 12.0,
        "main_bar_spacing_mm": 120.0,
        "distribution_bar_diameter_mm": 8.0,
        "distribution_bar_spacing_mm": 160.0,
    }


def test_staircase_benchmark_is_typed_review_required() -> None:
    response = TestClient(_app()).post(
        "/api/v1/design/staircase/straight-flight", json=_payload()
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == data["design"]["status"] == "REVIEW_REQUIRED"
    assert data["geometry"]["effective_span_mm"] == 5100.0
    assert data["actions"]["maximum_factored_moment_knm_per_m"] == pytest.approx(
        68.048997, abs=1e-6
    )
    assert data["design"]["ast_required_mm2_per_m"] == pytest.approx(920.64, abs=2.0)
    assert data["provenance"]["load_basis_reference"] == "NPTEL-M9L20-EX9.1"
    assert data["held_cases"] and data["qualified_review_required"] is True
    assert data["complete_engineering_design_approved"] is False


def test_staircase_rejects_unknown_nonfinite_and_unsupported_scope() -> None:
    client = TestClient(_app())
    invalid_requests: list[dict[str, object]] = []

    extra = deepcopy(_payload())
    extra["not_a_contract_field"] = True
    invalid_requests.append(extra)
    nonfinite = deepcopy(_payload())
    nonfinite["going_mm"] = "NaN"
    invalid_requests.append(nonfinite)
    alternate = deepcopy(_payload())
    alternate["support_case"] = "stringer_supported"
    invalid_requests.append(alternate)

    for invalid in invalid_requests:
        response = client.post("/api/v1/design/staircase/straight-flight", json=invalid)
        assert response.status_code == 422


def test_staircase_service_validation_uses_safe_error_envelope() -> None:
    invalid = deepcopy(_payload())
    invalid["effective_depth_mm"] = 250.0

    response = TestClient(_app()).post(
        "/api/v1/design/staircase/straight-flight", json=invalid
    )

    assert response.status_code == 422
    body = response.json()
    assert set(body) == {"success", "data", "error"}
    assert body["success"] is False and body["data"] is None
    assert body["error"]["code"] == "REQUEST_VALIDATION_ERROR"
    assert body["error"]["message"] == "Request validation failed"
    assert "effective_depth_mm" in body["error"]["details"][0]["msg"]


def test_staircase_capacity_failure_remains_json_safe_fail() -> None:
    payload = deepcopy(_payload())
    payload["ultimate_load_factor"] = 5.0

    response = TestClient(_app()).post(
        "/api/v1/design/staircase/straight-flight", json=payload
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "FAIL"
    main_check = next(
        item
        for item in data["design"]["governing_checks"]
        if item["check_id"] == "INDIA-2C-MAIN-STEEL-01"
    )
    assert main_check["limit"] is None


def test_staircase_openapi_exposes_typed_success_schema() -> None:
    schema = _app().openapi()
    operation = schema["paths"]["/api/v1/design/staircase/straight-flight"]["post"]

    assert operation["responses"]["200"]["content"]["application/json"]["schema"][
        "$ref"
    ].endswith("APIResponse_StraightFlightStaircaseResponse_")
    response_schema = schema["components"]["schemas"]["StraightFlightStaircaseResponse"]
    assert response_schema["properties"]["geometry"]
    assert response_schema["properties"]["design"]


def test_staircase_is_mounted_in_main_app(client: TestClient) -> None:
    response = client.post("/api/v1/design/staircase/straight-flight", json=_payload())
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "REVIEW_REQUIRED"

    invalid = deepcopy(_payload())
    invalid["support_case"] = "stringer_supported"
    invalid_response = client.post(
        "/api/v1/design/staircase/straight-flight", json=invalid
    )
    assert invalid_response.status_code == 422
    assert invalid_response.json()["error"]["code"] == "REQUEST_VALIDATION_ERROR"
