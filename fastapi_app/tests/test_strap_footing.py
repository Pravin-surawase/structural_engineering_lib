"""Contract tests for the bounded property-line strap-footing FastAPI slice."""

from __future__ import annotations

import dataclasses
from copy import deepcopy

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_app.routers.strap_footing import router
from tests.codes.is456.strap_footing.test_strength import _design_input


def _app() -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    return app


def _payload() -> dict[str, object]:
    return {
        "case_id": "INDIA-2-STRAP-HAND-01",
        "footing": dataclasses.asdict(_design_input()),
        "qualified_review_required": True,
    }


def test_strap_footing_benchmark_returns_typed_pass_with_provenance() -> None:
    response = TestClient(_app()).post(
        "/api/v1/design/strap-footing/property-line", json=_payload()
    )

    assert response.status_code == 200
    data = response.json()["data"]
    strength = data["strength"]
    assert data["status"] == "PASS"
    assert strength["actions"]["service"]["exterior_reaction_kn"] == pytest.approx(
        1200.0
    )
    assert strength["actions"]["service"]["interior_reaction_kn"] == pytest.approx(
        1600.0
    )
    assert strength["flexure"]["exact_flexural_steel_required_mm2"] == pytest.approx(
        2788.774499810215
    )
    assert strength["flexure"]["top_moment_capacity_kn_m"] == pytest.approx(
        961.337320139164
    )
    assert strength["shear"]["stirrup_carried_shear_required_kn"] == pytest.approx(
        19.6274979428445
    )
    assert data["provenance"]["workflow"] == (
        "design_property_line_strap_footing_is456"
    )
    assert data["provenance"]["strap_isolation_basis_reference"].endswith("-ISOLATION")
    assert data["qualified_review_required"] is True
    assert data["complete_engineering_design_approved"] is False


def test_strap_footing_rejects_unknown_nonfinite_and_held_scope() -> None:
    invalid_requests: list[dict[str, object]] = []

    extra = deepcopy(_payload())
    extra["not_a_contract_field"] = True
    invalid_requests.append(extra)
    nonfinite = deepcopy(_payload())
    nonfinite["footing"]["analysis"]["geometry"][  # type: ignore[index]
        "strap_overall_depth_mm"
    ] = "NaN"
    invalid_requests.append(nonfinite)
    soil_contact = deepcopy(_payload())
    soil_contact["footing"]["analysis"]["geometry"][  # type: ignore[index]
        "strap_soil_contact"
    ] = True
    invalid_requests.append(soil_contact)
    unapproved_transfer = deepcopy(_payload())
    unapproved_transfer["footing"]["analysis"]["approvals"][  # type: ignore[index]
        "column_and_strap_transfer_verified"
    ] = False
    invalid_requests.append(unapproved_transfer)
    non_boolean_review = deepcopy(_payload())
    non_boolean_review["qualified_review_required"] = 1
    invalid_requests.append(non_boolean_review)

    client = TestClient(_app())
    for invalid in invalid_requests:
        response = client.post(
            "/api/v1/design/strap-footing/property-line", json=invalid
        )
        assert response.status_code == 422


def test_strap_footing_service_validation_uses_safe_error_envelope() -> None:
    invalid = deepcopy(_payload())
    invalid["footing"]["analysis"]["geometry"][  # type: ignore[index]
        "strap_effective_depth_mm"
    ] = 950.0

    response = TestClient(_app()).post(
        "/api/v1/design/strap-footing/property-line", json=invalid
    )

    assert response.status_code == 422
    body = response.json()
    assert set(body) == {"success", "data", "error"}
    assert body["success"] is False and body["data"] is None
    assert body["error"]["code"] == "REQUEST_VALIDATION_ERROR"
    assert body["error"]["details"][0]["msg"] == (
        "strap_effective_depth_mm must be less than strap_overall_depth_mm"
    )


def test_strap_footing_valid_inadequacy_remains_json_safe_fail() -> None:
    inadequate = deepcopy(_payload())
    inadequate["footing"]["analysis"]["actions"][  # type: ignore[index]
        "allowable_gross_bearing_pressure_kn_per_m2"
    ] = 210.0

    response = TestClient(_app()).post(
        "/api/v1/design/strap-footing/property-line", json=inadequate
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert (
        data["strength"]["actions"]["gross_service_bearing_within_allowable"] is False
    )
    assert data["status"] == "FAIL"


def test_strap_footing_openapi_exposes_typed_success_schema() -> None:
    schema = _app().openapi()
    operation = schema["paths"]["/api/v1/design/strap-footing/property-line"]["post"]

    assert operation["responses"]["200"]["content"]["application/json"]["schema"][
        "$ref"
    ].endswith("APIResponse_PropertyLineStrapFootingResponse_")
    response_schema = schema["components"]["schemas"][
        "PropertyLineStrapFootingResponse"
    ]
    assert response_schema["properties"]["strength"]
    assert response_schema["properties"]["provenance"]


def test_strap_footing_is_mounted_in_main_app(client: TestClient) -> None:
    response = client.post(
        "/api/v1/design/strap-footing/property-line", json=_payload()
    )

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "PASS"
