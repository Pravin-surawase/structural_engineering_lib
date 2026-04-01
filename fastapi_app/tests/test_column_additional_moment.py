"""Tests for POST /api/v1/design/column/additional-moment endpoint."""

import pytest
from fastapi.testclient import TestClient

from fastapi_app.main import app

client = TestClient(app)

URL = "/api/v1/design/column/additional-moment"


class TestAdditionalMomentEndpoint:
    """FastAPI endpoint tests for additional moment (Cl 39.7.1)."""

    def test_happy_path_200(self):
        """Standard slender column returns 200 OK."""
        resp = client.post(
            URL,
            json={
                "Pu_kN": 1500,
                "b_mm": 300,
                "D_mm": 450,
                "lex_mm": 6000,
                "ley_mm": 4500,
                "fck": 25,
                "fy": 415,
                "Asc_mm2": 2400,
                "d_prime_mm": 50,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert pytest.approx(data["eadd_x_mm"], rel=0.01) == 40.0
        assert pytest.approx(data["Max_kNm"], rel=0.01) == 60.0
        assert data["is_slender_x"] is True

    def test_response_has_all_fields(self):
        """Response contains all expected fields."""
        resp = client.post(
            URL,
            json={
                "Pu_kN": 1000,
                "b_mm": 300,
                "D_mm": 400,
                "lex_mm": 5000,
                "ley_mm": 4000,
                "fck": 25,
                "fy": 415,
                "Asc_mm2": 1600,
                "d_prime_mm": 50,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        required = [
            "eadd_x_mm",
            "Max_kNm",
            "slenderness_ratio_x",
            "is_slender_x",
            "eadd_y_mm",
            "May_kNm",
            "slenderness_ratio_y",
            "is_slender_y",
            "k",
            "Max_reduced_kNm",
            "May_reduced_kNm",
            "Puz_kN",
            "Pb_kN",
            "Pu_kN",
            "b_mm",
            "D_mm",
            "lex_mm",
            "ley_mm",
            "clause_ref",
            "warnings",
        ]
        for field in required:
            assert field in data, f"Missing field: {field}"

    def test_short_column_zero_moment(self):
        """Short column (le/D < 12) returns zero additional moment."""
        resp = client.post(
            URL,
            json={
                "Pu_kN": 1000,
                "b_mm": 400,
                "D_mm": 400,
                "lex_mm": 4000,
                "ley_mm": 4000,
                "fck": 25,
                "fy": 415,
                "Asc_mm2": 2400,
                "d_prime_mm": 50,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["Max_kNm"] == 0.0
        assert data["May_kNm"] == 0.0
        assert data["is_slender_x"] is False
        assert data["is_slender_y"] is False

    def test_zero_pu_returns_zero(self):
        """Pu=0 gives zero additional moment."""
        resp = client.post(
            URL,
            json={
                "Pu_kN": 0,
                "b_mm": 300,
                "D_mm": 450,
                "lex_mm": 6000,
                "ley_mm": 4500,
                "fck": 25,
                "fy": 415,
                "Asc_mm2": 2400,
                "d_prime_mm": 50,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["Max_kNm"] == 0.0
        assert data["May_kNm"] == 0.0

    def test_invalid_D_422(self):
        """D_mm below minimum gives 422."""
        resp = client.post(
            URL,
            json={
                "Pu_kN": 1000,
                "b_mm": 300,
                "D_mm": 50,
                "lex_mm": 6000,
                "ley_mm": 4500,
                "fck": 25,
                "fy": 415,
                "Asc_mm2": 2400,
                "d_prime_mm": 50,
            },
        )
        assert resp.status_code == 422

    def test_negative_pu_422(self):
        """Negative Pu gives 422."""
        resp = client.post(
            URL,
            json={
                "Pu_kN": -100,
                "b_mm": 300,
                "D_mm": 450,
                "lex_mm": 6000,
                "ley_mm": 4500,
                "fck": 25,
                "fy": 415,
                "Asc_mm2": 2400,
                "d_prime_mm": 50,
            },
        )
        assert resp.status_code == 422

    def test_clause_ref_present(self):
        """Response includes IS 456 clause reference."""
        resp = client.post(
            URL,
            json={
                "Pu_kN": 1000,
                "b_mm": 300,
                "D_mm": 450,
                "lex_mm": 6000,
                "ley_mm": 4500,
                "fck": 25,
                "fy": 415,
                "Asc_mm2": 2400,
                "d_prime_mm": 50,
            },
        )
        assert resp.status_code == 200
        assert resp.json()["clause_ref"] == "Cl. 39.7.1"

    def test_k_factor_in_response(self):
        """Response includes k-factor and reduced moments."""
        resp = client.post(
            URL,
            json={
                "Pu_kN": 1500,
                "b_mm": 300,
                "D_mm": 450,
                "lex_mm": 6000,
                "ley_mm": 4500,
                "fck": 25,
                "fy": 415,
                "Asc_mm2": 2400,
                "d_prime_mm": 50,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "k" in data
        assert 0 <= data["k"] <= 1.0
        assert "Max_reduced_kNm" in data
        assert "May_reduced_kNm" in data
