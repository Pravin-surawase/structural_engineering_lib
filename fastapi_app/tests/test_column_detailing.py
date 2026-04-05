"""
Tests for POST /api/v1/design/column/detailing endpoint.

Tests cover:
- Happy path: valid rectangular column detailing
- Validation: b_mm below minimum returns 422
- Defaults: omitting optional fields works
- Circular: is_circular=True returns valid response
- Lap section: at_lap_section=True returns valid response
"""

from fastapi.testclient import TestClient

from fastapi_app.main import app
from fastapi_app.tests.conftest import unwrap

client = TestClient(app)

ENDPOINT = "/api/v1/design/column/detailing"


class TestColumnDetailingValidInput:
    """Tests for successful column detailing checks."""

    def test_column_detailing_valid_input(self):
        resp = client.post(
            ENDPOINT,
            json={
                "b_mm": 300.0,
                "D_mm": 450.0,
                "cover_mm": 40.0,
                "fck": 25.0,
                "fy": 415.0,
                "num_bars": 6,
                "bar_dia_mm": 16.0,
            },
        )
        assert resp.status_code == 200
        data = unwrap(resp)
        assert "is_valid" in data
        assert isinstance(data["is_valid"], bool)
        assert data["b_mm"] == 300.0
        assert data["D_mm"] == 450.0
        assert data["num_bars"] == 6
        assert data["bar_dia_mm"] == 16.0
        assert "clause_ref" in data
        assert "warnings" in data
        assert isinstance(data["warnings"], list)
        assert data["Ag_mm2"] > 0
        assert data["Asc_provided_mm2"] > 0
        assert data["steel_ratio"] > 0


class TestColumnDetailingValidation:
    """Tests for input validation (422 errors)."""

    def test_column_detailing_invalid_width(self):
        resp = client.post(
            ENDPOINT,
            json={
                "b_mm": 50.0,
                "D_mm": 450.0,
                "num_bars": 4,
                "bar_dia_mm": 16.0,
            },
        )
        assert resp.status_code == 422

    def test_column_detailing_invalid_num_bars(self):
        resp = client.post(
            ENDPOINT,
            json={
                "b_mm": 300.0,
                "D_mm": 450.0,
                "num_bars": 1,
                "bar_dia_mm": 16.0,
            },
        )
        assert resp.status_code == 422

    def test_column_detailing_missing_required(self):
        resp = client.post(
            ENDPOINT,
            json={
                "b_mm": 300.0,
                "D_mm": 450.0,
            },
        )
        assert resp.status_code == 422


class TestColumnDetailingDefaults:
    """Tests for default values on optional fields."""

    def test_column_detailing_defaults(self):
        resp = client.post(
            ENDPOINT,
            json={
                "b_mm": 400.0,
                "D_mm": 400.0,
                "num_bars": 4,
                "bar_dia_mm": 20.0,
            },
        )
        assert resp.status_code == 200
        data = unwrap(resp)
        assert data["is_valid"] is not None
        assert data["tie_dia_mm"] > 0
        assert data["tie_spacing_mm"] > 0


class TestColumnDetailingCircular:
    """Tests for circular column detailing."""

    def test_column_detailing_circular(self):
        resp = client.post(
            ENDPOINT,
            json={
                "b_mm": 400.0,
                "D_mm": 400.0,
                "num_bars": 6,
                "bar_dia_mm": 16.0,
                "is_circular": True,
            },
        )
        assert resp.status_code == 200
        data = unwrap(resp)
        assert isinstance(data["is_valid"], bool)
        assert isinstance(data["cross_ties_needed"], bool)


class TestColumnDetailingAtLap:
    """Tests for detailing at lap splice location."""

    def test_column_detailing_at_lap(self):
        resp = client.post(
            ENDPOINT,
            json={
                "b_mm": 300.0,
                "D_mm": 450.0,
                "num_bars": 6,
                "bar_dia_mm": 20.0,
                "at_lap_section": True,
            },
        )
        assert resp.status_code == 200
        data = unwrap(resp)
        assert isinstance(data["is_valid"], bool)
        assert data["max_tie_spacing_mm"] > 0
