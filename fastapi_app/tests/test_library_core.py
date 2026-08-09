"""Request-to-public-library evidence for the new footing and slab consumers."""

from __future__ import annotations

import pytest


def _footing_load_transfer_payload(**overrides):
    payload = {
        "Pu_kN": 3000,
        "loaded_area_A2_mm2": 160000,
        "effective_supporting_area_A1_mm2": 640000,
        "effective_supporting_area_basis": "largest_frustum_1v_2h",
        "effective_supporting_area_is_approved": True,
        "supporting_concrete_fck_nmm2": 20,
        "supported_concrete_fck_nmm2": 25,
        "steel_fy_nmm2": 415,
        "dowel_count": 8,
        "dowel_diameter_mm": 25,
        "column_longitudinal_bar_diameter_mm": 32,
        "available_dowel_development_length_into_footing_mm": 1176,
        "available_dowel_development_length_into_supported_member_mm": 1010,
        "dowel_bar_type": "deformed",
    }
    payload.update(overrides)
    return payload


def _unwrap(response):
    body = response.json()
    assert body["success"] is True, body
    return body["data"]


def test_footing_load_transfer_endpoint_calls_supported_public_workflow(client):
    response = client.post(
        "/api/v1/design/footing/load-transfer",
        json=_footing_load_transfer_payload(),
    )

    assert response.status_code == 200
    data = _unwrap(response)
    assert data["governing_concrete_bearing_capacity_kN"] == 1800
    assert data["is_safe"] is True
    assert data["effective_supporting_area_basis"] == "largest_frustum_1v_2h"


@pytest.mark.parametrize("dowel_count", [6.8, True, 0])
def test_footing_load_transfer_endpoint_rejects_non_integral_or_invalid_count(
    client, dowel_count
):
    response = client.post(
        "/api/v1/design/footing/load-transfer",
        json=_footing_load_transfer_payload(dowel_count=dowel_count),
    )

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["data"] is None
    assert body["error"]["code"] == "REQUEST_VALIDATION_ERROR"
    assert body["error"]["details"]


def test_footing_load_transfer_endpoint_accepts_four_integral_dowels(client):
    response = client.post(
        "/api/v1/design/footing/load-transfer",
        json=_footing_load_transfer_payload(dowel_count=4),
    )

    assert response.status_code == 200
    assert _unwrap(response)["provided_bar_count"] == 4


def test_one_way_slab_endpoint_calls_supported_public_workflow(client):
    response = client.post(
        "/api/v1/design/slab/one-way",
        json={
            "short_effective_span_mm": 3000,
            "long_effective_span_mm": 7500,
            "thickness_mm": 150,
            "d_mm": 125,
            "factored_area_load_kn_per_m2": 10,
            "fck_n_per_mm2": 20,
            "fy_n_per_mm2": 415,
            "main_bar_diameter_mm": 10,
            "main_bar_spacing_mm": 250,
            "distribution_bar_diameter_mm": 8,
            "distribution_bar_spacing_mm": 250,
        },
    )

    assert response.status_code == 200
    data = _unwrap(response)
    assert data["flexure"]["factored_moment_knm"] == 11.25
    assert data["detailing"]["detailing_adequacy"] == "adequate"
    assert data["detailing"]["review_requirement"] == "qualified_review_required"


def test_one_way_slab_endpoint_rejects_two_way_geometry(client):
    response = client.post(
        "/api/v1/design/slab/one-way",
        json={
            "short_effective_span_mm": 3000,
            "long_effective_span_mm": 6000,
            "thickness_mm": 150,
            "d_mm": 125,
            "factored_area_load_kn_per_m2": 10,
            "fck_n_per_mm2": 20,
            "fy_n_per_mm2": 415,
            "main_bar_diameter_mm": 10,
            "main_bar_spacing_mm": 250,
            "distribution_bar_diameter_mm": 8,
            "distribution_bar_spacing_mm": 250,
        },
    )

    assert response.status_code == 422
    assert response.json()["success"] is False


def test_library_core_pydantic_422_uses_standard_envelope(client):
    response = client.post("/api/v1/design/slab/one-way", json={})

    assert response.status_code == 422
    body = response.json()
    assert set(body) == {"success", "data", "error"}
    assert body["success"] is False
    assert body["data"] is None
    assert body["error"]["code"] == "REQUEST_VALIDATION_ERROR"
    assert body["error"]["details"]
    assert body["error"]["details"][0]["loc"][0] == "body"


def test_existing_endpoint_pydantic_422_uses_same_envelope(client):
    response = client.post(
        "/api/v1/design/beam",
        json={"width": -100, "depth": 500, "moment": 150},
    )

    assert response.status_code == 422
    body = response.json()
    assert set(body) == {"success", "data", "error"}
    assert body["success"] is False
    assert body["data"] is None
    assert body["error"]["code"] == "REQUEST_VALIDATION_ERROR"
    locations = [detail["loc"] for detail in body["error"]["details"]]
    assert ["body", "width"] in locations


def test_openapi_documents_the_maintained_422_envelope(client):
    schema = client.get("/openapi.json").json()

    for path in (
        "/api/v1/design/slab/one-way",
        "/api/v1/design/beam",
    ):
        response_schema = schema["paths"][path]["post"]["responses"]["422"]
        assert response_schema["description"] == "Request validation failed"
        assert response_schema["content"]["application/json"]["schema"] == {
            "$ref": "#/components/schemas/RequestValidationErrorResponse"
        }
