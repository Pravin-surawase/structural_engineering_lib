"""Focused contracts for the rectangular-column check-and-review slice."""

import json
from pathlib import Path

import pytest
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

AXIS_REFERENCE = json.loads(
    (
        Path(__file__).resolve().parents[2]
        / "Python/tests/data/benchmark_vectors/column_strain_compatibility.json"
    ).read_text(encoding="utf-8")
)["consumers"]["long_column_axes"]


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


@pytest.mark.parametrize(
    ("moment", "expected_design", "expected_ratio"),
    ((170.0, 206.17, 1.0504), (-170.0, 206.17, 1.0504), (165.0, 201.17, 1.0185)),
)
def test_long_column_http_preserves_independent_safety_reversals(
    moment, expected_design, expected_ratio
):
    # Independent Cl39.7 benchmark, frozen in column_strain_compatibility.json.
    response = client.post(
        "/api/v1/design/column/long-column",
        json={
            "Pu_kN": 1000,
            "M1x_kNm": moment,
            "M2x_kNm": moment,
            "M1y_kNm": 0,
            "M2y_kNm": 0,
            "b_mm": 300,
            "D_mm": 450,
            "lex_mm": 6300,
            "ley_mm": 3000,
            "fck": 25,
            "fy": 415,
            "Asc_mm2": 2700,
            "d_prime_mm": 50,
            "l_unsupported_mm": 6300,
            "braced": True,
        },
    )
    assert response.status_code == 200
    data = unwrap(response)
    assert data["Pb_kN"] == 708.61
    assert data["k"] == 0.8201
    assert data["Mux_design_kNm"] == expected_design
    assert data["interaction_ratio"] == expected_ratio
    assert data["is_safe"] is False


@pytest.mark.parametrize("expected", AXIS_REFERENCE)
def test_http_long_and_additional_moment_use_independent_plane_factors(expected):
    section = expected["inputs"]
    common = {
        "Pu_kN": expected["Pu_kN"],
        "b_mm": section["width"],
        "D_mm": section["depth"],
        "fck": section["fck"],
        "fy": section["fy"],
        "Asc_mm2": section["steel_area"],
        "d_prime_mm": section["cover"],
        "lex_mm": expected["lex_mm"],
        "ley_mm": expected["ley_mm"],
    }
    request = {
        **common,
        **{
            name: expected[name]
            for name in (
                "M1x_kNm",
                "M2x_kNm",
                "M1y_kNm",
                "M2y_kNm",
                "braced",
                "l_unsupported_mm",
            )
        },
    }
    response = client.post("/api/v1/design/column/long-column", json=request)
    additional_response = client.post(
        "/api/v1/design/column/additional-moment", json=common
    )
    assert response.status_code == additional_response.status_code == 200
    data, additional = unwrap(response), unwrap(additional_response)
    for name in ("k_x", "k_y"):
        assert data[name] == pytest.approx(expected[name], abs=0.00005)
        assert additional[name] == pytest.approx(expected[name], abs=1e-12)
    for name in ("Pb_x_kN", "Pb_y_kN", "Max_reduced_kNm", "May_reduced_kNm"):
        assert data[name] == pytest.approx(expected[name], abs=0.005)
        assert additional[name] == pytest.approx(expected[name], abs=1e-8)
    for result in (data, additional):
        assert result["k"] == result["k_x"]
        assert result["Pb_kN"] == result["Pb_x_kN"]
        assert result["reduction_method"] == "IS456_39_7_1_1_PER_AXIS_V1"
    for name in ("Mux_design_kNm", "Muy_design_kNm"):
        assert data[name] == pytest.approx(expected[name], abs=0.005)
    assert data["interaction_ratio"] == pytest.approx(
        expected["interaction_ratio"], abs=0.00005
    )
    assert data["is_safe"] == expected["is_safe"]
