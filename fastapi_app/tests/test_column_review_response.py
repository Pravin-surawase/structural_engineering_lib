"""Focused contracts for the rectangular-column check-and-review slice."""

from fastapi.testclient import TestClient

from fastapi_app.main import app
from fastapi_app.tests.conftest import unwrap

client = TestClient(app)
UNIFIED_ENDPOINT = "/api/v1/design/column"

BASE_REQUEST = {
    "Pu_kN": 800.0,
    "Mux_kNm": 120.0,
    "Muy_kNm": 40.0,
    "b_mm": 300.0,
    "D_mm": 450.0,
    "l_mm": 3000.0,
    "end_condition": "FIXED_FIXED",
    "fck": 25.0,
    "fy": 415.0,
    "Asc_mm2": 2400.0,
    "d_prime_mm": 50.0,
}


def test_short_axial_capacity_route_remains_available():
    response = client.post(
        "/api/v1/design/column/axial",
        json={
            "fck": 25.0,
            "fy": 415.0,
            "Ag_mm2": 135000.0,
            "Asc_mm2": 2400.0,
        },
    )

    assert response.status_code == 200
    data = unwrap(response)
    assert data["Pu_kN"] > 0.0
    assert data["is_safe"] is True


def test_short_uniaxial_route_reports_capacity_and_classification():
    response = client.post(
        "/api/v1/design/column/uniaxial",
        json={
            "Pu_kN": 1200.0,
            "Mu_kNm": 150.0,
            "b_mm": 300.0,
            "D_mm": 450.0,
            "le_mm": 3000.0,
            "fck": 25.0,
            "fy": 415.0,
            "Asc_mm2": 2700.0,
            "d_prime_mm": 50.0,
            "l_unsupported_mm": 3000.0,
        },
    )

    assert response.status_code == 200
    data = unwrap(response)
    assert data["classification"] == "SHORT"
    assert data["Pu_cap_kN"] > 0.0
    assert data["Mu_cap_kNm"] > 0.0


def test_short_biaxial_unified_route_retains_review_fields():
    response = client.post(UNIFIED_ENDPOINT, json=BASE_REQUEST)

    assert response.status_code == 200
    data = unwrap(response)
    assert data["classification"] == "SHORT"
    assert data["classification_x"] == "SHORT"
    assert data["classification_y"] == "SHORT"
    assert data["governing_check"] == "biaxial"
    assert data["checks"]["biaxial"]["classification"] == "SHORT"
    assert data["checks"]["biaxial"]["clause_ref"] == "Cl. 39.6"
    assert data["clause_refs"] == ["Cl. 25.2", "Cl. 25.1.2", "Cl. 25.4", "Cl. 39.6"]
    assert data["qualified_review_required"] is True
    assert data["review_status"] == "QUALIFIED_REVIEW_REQUIRED"
    assert data["result_envelope"]["engineering_status"] == (
        "PASS" if data["is_safe"] else "FAIL"
    )

    review_fields = {
        "Pu_kN",
        "Mux_applied_kNm",
        "Muy_applied_kNm",
        "Mux_design_kNm",
        "Muy_design_kNm",
        "Mux_min_kNm",
        "Muy_min_kNm",
        "emin_x_mm",
        "emin_y_mm",
        "le_x_mm",
        "le_y_mm",
        "slenderness_x",
        "slenderness_y",
        "classification_x",
        "classification_y",
        "governing_check",
        "checks",
        "is_safe",
        "warnings",
        "clause_refs",
    }
    assert review_fields.issubset(data)


def test_unified_project_route_rejects_missing_materials():
    request = dict(BASE_REQUEST)
    del request["fck"]
    del request["fy"]

    response = client.post(UNIFIED_ENDPOINT, json=request)

    assert response.status_code == 422
    missing_paths = {item["loc"][-1] for item in response.json()["error"]["details"]}
    assert missing_paths == {"fck", "fy"}


def test_slender_route_retains_additional_moments_and_axis_disposition():
    response = client.post(
        UNIFIED_ENDPOINT,
        json={
            **BASE_REQUEST,
            "l_mm": 6000.0,
            "end_condition": "HINGED_HINGED",
            "Mux_kNm": 80.0,
            "Muy_kNm": 60.0,
        },
    )

    assert response.status_code == 200
    data = unwrap(response)
    assert data["classification"] == "SLENDER"
    assert data["classification_x"] == "SLENDER"
    assert data["classification_y"] == "SLENDER"
    assert data["governing_check"] == "long_column"
    assert data["Ma_x_kNm"] > 0.0
    assert data["Ma_y_kNm"] > 0.0
    assert data["checks"]["long_column"]["classification_x"] == "SLENDER"
    assert data["checks"]["long_column"]["clause_ref"] == "Cl. 39.7"


def test_inadequate_column_remains_an_explicit_failed_check():
    response = client.post(
        UNIFIED_ENDPOINT,
        json={**BASE_REQUEST, "Mux_kNm": 1000.0, "Muy_kNm": 800.0},
    )

    assert response.status_code == 200
    data = unwrap(response)
    assert data["is_safe"] is False
    assert data["checks"]["biaxial"]["is_safe"] is False
    assert data["checks"]["biaxial"]["interaction_ratio"] > 1.0
