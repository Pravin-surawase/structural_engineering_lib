"""Contract tests for the bounded simply supported deep-beam FastAPI slice."""

from __future__ import annotations

from copy import deepcopy

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_app.routers.deep_beam import router


def _app() -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    return app


def _payload() -> dict[str, object]:
    return {
        "case_id": "INDIA-2-DEEP-HAND-01",
        "centre_to_centre_span_mm": 3000.0,
        "clear_span_mm": 2800.0,
        "overall_depth_mm": 2000.0,
        "beam_width_mm": 300.0,
        "concrete_grade_nmm2": 30,
        "steel_grade_nmm2": 500,
        "factored_positive_moment_knm": 900.0,
        "main_bar_count": 4,
        "main_bar_diameter_mm": 22.0,
        "furthest_main_bar_from_tension_face_mm": 250.0,
        "main_bars_continuous_between_supports": True,
        "main_bars_bundled": False,
        "main_bar_splices_present": False,
        "left_support_embedment_mm": 850.0,
        "right_support_embedment_mm": 850.0,
        "face_grid_count": 2,
        "vertical_side_bar_diameter_mm": 10.0,
        "vertical_side_bar_spacing_mm": 300.0,
        "horizontal_side_bar_diameter_mm": 10.0,
        "horizontal_side_bar_spacing_mm": 250.0,
        "geometry_basis_reference": "INDIA-2-DEEP-HAND-01-GEOMETRY",
        "bearing_nodal_zone_reference": "INDIA-2-DEEP-HAND-01-BEARING",
        "action_basis_reference": "INDIA-2-DEEP-HAND-01-ACTIONS",
        "reinforcement_basis_reference": "INDIA-2-DEEP-HAND-01-REINFORCEMENT",
        "support_type": "simply_supported",
        "solid_rectangular_section": True,
        "openings_present": False,
        "dapped_ends_present": False,
        "top_loaded": True,
        "hanging_action_required": False,
        "bearing_nodal_zone_verified": True,
    }


def test_deep_beam_benchmark_returns_typed_pass_with_provenance() -> None:
    response = TestClient(_app()).post(
        "/api/v1/design/deep-beam/simply-supported", json=_payload()
    )

    assert response.status_code == 200
    data = response.json()["data"]
    reinforcement = data["reinforcement"]
    assert data["status"] == "PASS"
    assert reinforcement["geometry"]["effective_span_mm"] == pytest.approx(3000.0)
    assert reinforcement["geometry"]["lever_arm_mm"] == pytest.approx(1400.0)
    assert reinforcement["positive_tie"]["required_area_mm2"] == pytest.approx(
        1477.832512315271, abs=1e-6
    )
    assert reinforcement["anchorage"]["required_embedment_mm"] == pytest.approx(797.5)
    assert reinforcement["vertical_side_face"][
        "provided_area_mm2_per_m"
    ] == pytest.approx(523.598775598299, abs=1e-6)
    assert data["provenance"]["workflow"] == ("design_simply_supported_deep_beam_is456")
    assert "29.3.4" in data["provenance"]["clause_refs"]
    assert data["shear_deemed_satisfied_within_clause_29_scope"] is True
    assert data["qualified_review_required"] is True
    assert data["complete_engineering_design_approved"] is False


def test_deep_beam_rejects_unknown_nonfinite_and_unsupported_scope() -> None:
    client = TestClient(_app())
    invalid_requests: list[dict[str, object]] = []

    extra = deepcopy(_payload())
    extra["not_a_contract_field"] = True
    invalid_requests.append(extra)
    nonfinite = deepcopy(_payload())
    nonfinite["overall_depth_mm"] = "NaN"
    invalid_requests.append(nonfinite)
    opening = deepcopy(_payload())
    opening["openings_present"] = True
    invalid_requests.append(opening)
    unverified = deepcopy(_payload())
    unverified["bearing_nodal_zone_verified"] = False
    invalid_requests.append(unverified)
    wrong_grid = deepcopy(_payload())
    wrong_grid["face_grid_count"] = 1
    invalid_requests.append(wrong_grid)
    non_boolean_continuity = deepcopy(_payload())
    non_boolean_continuity["main_bars_continuous_between_supports"] = 1
    invalid_requests.append(non_boolean_continuity)

    for invalid in invalid_requests:
        response = client.post(
            "/api/v1/design/deep-beam/simply-supported", json=invalid
        )
        assert response.status_code == 422


def test_deep_beam_service_validation_uses_safe_error_envelope() -> None:
    invalid = deepcopy(_payload())
    invalid["overall_depth_mm"] = 1500.0

    response = TestClient(_app()).post(
        "/api/v1/design/deep-beam/simply-supported", json=invalid
    )

    assert response.status_code == 422
    body = response.json()
    assert set(body) == {"success", "data", "error"}
    assert body["success"] is False and body["data"] is None
    assert body["error"]["code"] == "REQUEST_VALIDATION_ERROR"
    assert body["error"]["details"][0]["msg"].startswith(
        "Error during deep beam. Reference:"
    )


def test_deep_beam_valid_inadequacy_remains_json_safe_fail() -> None:
    inadequate = deepcopy(_payload())
    inadequate["main_bar_count"] = 3

    response = TestClient(_app()).post(
        "/api/v1/design/deep-beam/simply-supported", json=inadequate
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["reinforcement"]["positive_tie"]["status"] == "FAIL"
    assert data["status"] == "FAIL"
    assert data["shear_deemed_satisfied_within_clause_29_scope"] is False


def test_deep_beam_openapi_exposes_typed_success_schema() -> None:
    schema = _app().openapi()
    operation = schema["paths"]["/api/v1/design/deep-beam/simply-supported"]["post"]

    assert operation["responses"]["200"]["content"]["application/json"]["schema"][
        "$ref"
    ].endswith("APIResponse_SimplySupportedDeepBeamResponse_")
    response_schema = schema["components"]["schemas"]["SimplySupportedDeepBeamResponse"]
    assert response_schema["properties"]["reinforcement"]
    assert response_schema["properties"]["provenance"]


def test_deep_beam_is_mounted_in_main_app(client: TestClient) -> None:
    response = client.post("/api/v1/design/deep-beam/simply-supported", json=_payload())

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "PASS"
