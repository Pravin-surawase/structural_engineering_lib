"""Direct contract coverage for routes identified by the MAINT-004 parity audit."""

import pytest
from fastapi.testclient import TestClient

from fastapi_app.tests.conftest import unwrap


def test_column_classify_route(client: TestClient):
    response = client.post(
        "/api/v1/design/column/classify",
        json={"le_mm": 3000.0, "D_mm": 400.0},
    )

    assert response.status_code == 200
    data = unwrap(response)
    assert data == {"classification": "SHORT", "slenderness_ratio": 7.5}


def test_column_eccentricity_route(client: TestClient):
    response = client.post(
        "/api/v1/design/column/eccentricity",
        json={"l_unsupported_mm": 3000.0, "D_mm": 400.0},
    )

    assert response.status_code == 200
    assert unwrap(response)["e_min_mm"] == 20.0


def test_column_axial_route(client: TestClient):
    response = client.post(
        "/api/v1/design/column/axial",
        json={
            "fck": 25.0,
            "fy": 415.0,
            "Ag_mm2": 120000.0,
            "Asc_mm2": 2400.0,
        },
    )

    assert response.status_code == 200
    data = unwrap(response)
    assert data["Pu_kN"] == pytest.approx(1843.32)
    assert data["steel_ratio"] == pytest.approx(0.02)
    assert data["is_safe"] is True


def test_long_column_route(client: TestClient):
    response = client.post(
        "/api/v1/design/column/long-column",
        json={
            "Pu_kN": 1000.0,
            "M1x_kNm": 20.0,
            "M2x_kNm": 50.0,
            "M1y_kNm": 10.0,
            "M2y_kNm": 30.0,
            "b_mm": 300.0,
            "D_mm": 450.0,
            "lex_mm": 6000.0,
            "ley_mm": 5000.0,
            "fck": 25.0,
            "fy": 415.0,
            "Asc_mm2": 3000.0,
            "d_prime_mm": 50.0,
            "braced": True,
        },
    )

    assert response.status_code == 200
    data = unwrap(response)
    assert data["is_slender_x"] is True
    assert data["is_slender_y"] is True
    assert data["governing_check"] == "biaxial"
    assert data["interaction_ratio"] < 1.0


def test_helical_check_route(client: TestClient):
    response = client.post(
        "/api/v1/design/column/helical-check",
        json={
            "D_mm": 450.0,
            "D_core_mm": 350.0,
            "fck": 25.0,
            "fy": 415.0,
            "d_helix_mm": 8.0,
            "pitch_mm": 50.0,
            "Pu_axial_kN": 2000.0,
        },
    )

    assert response.status_code == 200
    data = unwrap(response)
    assert data["pitch_ok"] is True
    assert data["enhancement_factor"] == pytest.approx(1.05)
    assert data["clause_ref"] == "Cl. 39.4"


def test_column_ductile_detailing_route(client: TestClient):
    response = client.post(
        "/api/v1/design/column/ductile-detailing",
        json={
            "b_mm": 400.0,
            "D_mm": 500.0,
            "clear_height_mm": 3000.0,
            "bar_dia_mm": 20.0,
            "fck": 25.0,
            "fy": 415.0,
        },
    )

    assert response.status_code == 200
    data = unwrap(response)
    assert data["is_geometry_valid"] is True
    assert data["is_compliant"] is True
    assert data["errors"] == []


def _valid_rebar_payload() -> dict:
    return {
        "beam": {"width": 300.0, "depth": 500.0, "cover": 40.0, "span": 5000.0},
        "config": {
            "bar_count": 3,
            "bar_dia": 16.0,
            "stirrup_dia": 8.0,
            "layers": 1,
        },
    }


def test_rebar_validate_route(client: TestClient):
    response = client.post("/api/v1/rebar/validate", json=_valid_rebar_payload())

    assert response.status_code == 200
    data = unwrap(response)
    assert data["success"] is True
    assert data["validation"]["ok"] is True
    assert data["validation"]["details"]["spacing_mm"] == pytest.approx(94.0)


def test_rebar_apply_route(client: TestClient):
    response = client.post("/api/v1/rebar/apply", json=_valid_rebar_payload())

    assert response.status_code == 200
    data = unwrap(response)
    assert data["success"] is True
    assert data["ast_provided_mm2"] == pytest.approx(603.2)
    assert len(data["geometry"]["rebars"]) == 3
    assert data["geometry"]["stirrups"]
