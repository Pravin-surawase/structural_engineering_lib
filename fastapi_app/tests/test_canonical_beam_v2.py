"""Canonical Python/FastAPI v2 parity tests for LIB-PRO-013 B0."""

from __future__ import annotations

import math

from structural_lib.design.is456 import beam


def _payload() -> dict:
    return {
        "identity": {"member_id": "B1", "story": "GF", "case_id": "ULS-1"},
        "section": {"span_mm": 5000, "b_mm": 300, "D_mm": 550, "d_mm": 500},
        "materials": {"fck_nmm2": 25, "fy_nmm2": 500},
        "actions": {"mu_knm": 150, "vu_kn": 80, "tu_knm": 0},
        "calculation_basis": {"d_dash_mm": 50, "asv_mm2": 32 * math.pi},
    }


def test_v2_matches_canonical_python_result(client):
    payload = _payload()
    payload["detailing"] = {
        "standard": "IS456",
        "clear_cover_mm": 40,
        "tension_bar_diameter_mm": 20,
        "compression_bar_diameter_mm": 16,
        "nominal_top_steel_ratio": 0.25,
        "stirrup_diameter_mm": 8,
        "stirrup_legs": 2,
        "stirrup_spacing_support_mm": 150,
        "stirrup_spacing_mid_mm": 200,
    }
    python_result = beam.design(beam.load(payload)).to_dict()

    response = client.post("/api/v2/design/beam", json=payload)

    assert response.status_code == 200
    assert response.json() == python_result
    assert response.json()["envelope"]["overall_status"] == "PASS"


def test_v2_rejects_invalid_input_with_canonical_code_and_path(client):
    payload = _payload()
    payload["actions"]["mu_knm"] = "150"

    response = client.post("/api/v2/design/beam", json=payload)

    assert response.status_code == 422
    problem = response.json()["error"]
    assert problem["schema_version"] == "structural-problem/v1"
    assert problem["code"] == "INPUT_CONTRACT_INVALID"
    assert problem["details"]["issues"][0]["path"] == "actions.mu_knm"
    assert problem["details"]["issues"][0]["code"] == "INPUT_TYPE_INVALID"


def test_v2_openapi_exposes_nested_canonical_request(client):
    schema = client.get("/openapi.json").json()
    operation = schema["paths"]["/api/v2/design/beam"]["post"]

    assert operation["requestBody"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/BeamDesignInputV1"
    }
    request_schema = schema["components"]["schemas"]["BeamDesignInputV1"]
    assert set(request_schema["required"]) == {
        "identity",
        "section",
        "materials",
        "actions",
        "calculation_basis",
    }


def test_v2_preserves_centroid_and_transverse_grade_through_calculation(client):
    payload = _payload()
    payload["section"].pop("d_mm")
    payload["section"]["effective_depth_basis"] = {"centroid_cover_mm": 40}
    payload["materials"]["fy_transverse_nmm2"] = 415
    expected = beam.design(beam.load(payload)).to_dict()
    response = client.post("/api/v2/design/beam", json=payload)
    assert response.status_code == 200
    assert response.json() == expected
    assert response.json()["calculation"]["effective_depth_resolution"]["d_mm"] == 510
