"""
Tests for POST /api/v1/design/column/effective-length endpoint.

Tests cover:
- Happy path: recommended and theoretical values
- Validation: invalid end_condition returns 422
- Validation: out-of-range l_mm returns 422
- Response field completeness
"""

from fastapi.testclient import TestClient

from fastapi_app.main import app

client = TestClient(app)

ENDPOINT = "/api/v1/design/column/effective-length"


class TestEffectiveLengthHappyPath:
    """Tests for successful effective length calculations."""

    def test_fixed_fixed_recommended(self):
        resp = client.post(
            ENDPOINT,
            json={
                "l_mm": 3000.0,
                "end_condition": "FIXED_FIXED",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["le_mm"] == 1950.0
        assert data["ratio"] == 0.65
        assert data["end_condition"] == "FIXED_FIXED"
        assert data["method"] == "recommended"

    def test_hinged_hinged_recommended(self):
        resp = client.post(
            ENDPOINT,
            json={
                "l_mm": 4000.0,
                "end_condition": "HINGED_HINGED",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["le_mm"] == 4000.0
        assert data["ratio"] == 1.0
        assert data["method"] == "recommended"

    def test_fixed_free_cantilever(self):
        resp = client.post(
            ENDPOINT,
            json={
                "l_mm": 3000.0,
                "end_condition": "FIXED_FREE",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["le_mm"] == 6000.0
        assert data["ratio"] == 2.0

    def test_theoretical_values(self):
        resp = client.post(
            ENDPOINT,
            json={
                "l_mm": 4000.0,
                "end_condition": "HINGED_HINGED",
                "use_theoretical": True,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["method"] == "theoretical"
        assert data["ratio"] == 1.0

    def test_fixed_hinged(self):
        resp = client.post(
            ENDPOINT,
            json={
                "l_mm": 5000.0,
                "end_condition": "FIXED_HINGED",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["end_condition"] == "FIXED_HINGED"
        assert data["le_mm"] > 0
        assert data["ratio"] > 0

    def test_response_contains_all_fields(self):
        resp = client.post(
            ENDPOINT,
            json={
                "l_mm": 3000.0,
                "end_condition": "FIXED_FIXED",
            },
        )
        data = resp.json()
        expected_fields = {"le_mm", "ratio", "end_condition", "method"}
        assert expected_fields == set(data.keys())


class TestEffectiveLengthValidation:
    """Tests for input validation and error handling."""

    def test_invalid_end_condition_returns_422(self):
        resp = client.post(
            ENDPOINT,
            json={
                "l_mm": 3000.0,
                "end_condition": "INVALID_CONDITION",
            },
        )
        assert resp.status_code == 422

    def test_l_mm_zero_returns_422(self):
        resp = client.post(
            ENDPOINT,
            json={
                "l_mm": 0,
                "end_condition": "FIXED_FIXED",
            },
        )
        assert resp.status_code == 422

    def test_l_mm_negative_returns_422(self):
        resp = client.post(
            ENDPOINT,
            json={
                "l_mm": -1000.0,
                "end_condition": "FIXED_FIXED",
            },
        )
        assert resp.status_code == 422

    def test_l_mm_too_large_returns_422(self):
        resp = client.post(
            ENDPOINT,
            json={
                "l_mm": 60000.0,
                "end_condition": "FIXED_FIXED",
            },
        )
        assert resp.status_code == 422

    def test_missing_required_fields_returns_422(self):
        resp = client.post(
            ENDPOINT,
            json={
                "l_mm": 3000.0,
            },
        )
        assert resp.status_code == 422

    def test_default_use_theoretical_is_false(self):
        resp = client.post(
            ENDPOINT,
            json={
                "l_mm": 3000.0,
                "end_condition": "FIXED_FIXED",
            },
        )
        assert resp.status_code == 200
        assert resp.json()["method"] == "recommended"
