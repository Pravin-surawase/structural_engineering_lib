"""
Tests for import router extended endpoints.

Covers:
- GET /api/v1/import/formats
- POST /api/v1/import/csv/text
"""

import pytest
from fastapi.testclient import TestClient

from fastapi_app.main import app
from fastapi_app.tests.conftest import unwrap


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


# =============================================================================
# Supported Formats
# =============================================================================


class TestImportFormats:
    """Tests for GET /api/v1/import/formats."""

    def test_formats_endpoint(self, client):
        """Formats endpoint returns supported formats."""
        resp = client.get("/api/v1/import/formats")
        assert resp.status_code == 200
        data = unwrap(resp)
        assert "formats" in data
        assert len(data["formats"]) >= 3  # ETABS, SAFE, STAAD, Generic
        format_names = [f["name"] for f in data["formats"]]
        assert "ETABS" in format_names
        assert "Generic" in format_names

    def test_formats_have_indicators(self, client):
        """Each format has indicators for auto-detection."""
        resp = client.get("/api/v1/import/formats")
        data = unwrap(resp)
        for fmt in data["formats"]:
            assert "name" in fmt
            assert "indicators" in fmt
            assert "columns" in fmt


# =============================================================================
# CSV Text Import
# =============================================================================


class TestCSVTextImport:
    """Tests for POST /api/v1/import/csv/text."""

    def test_csv_text_generic(self, client):
        """Import generic CSV from text content."""
        csv_content = (
            "beam_id,b_mm,D_mm,span_mm,mu_knm,vu_kn,fck,fy,cover_mm\n"
            "B1,300,500,5000,150,80,25,500,40\n"
            "B2,250,450,4500,120,60,25,500,40\n"
        )
        resp = client.post(
            "/api/v1/import/csv/text",
            params={
                "csv_text": csv_content,
                "format_hint": "generic",
                "fck_mpa": 25,
                "fy_mpa": 500,
                "cover_mm": 40,
                "stirrup_diameter_mm": 8,
                "tension_bar_diameter_mm": 16,
            },
        )
        assert resp.status_code == 200
        data = unwrap(resp)
        assert data["beam_count"] >= 1

    def test_csv_text_empty(self, client):
        """Empty CSV text."""
        resp = client.post(
            "/api/v1/import/csv/text",
            params={
                "csv_text": "",
                "format_hint": "auto",
                "fck_mpa": 25,
                "fy_mpa": 500,
                "cover_mm": 40,
                "stirrup_diameter_mm": 8,
                "tension_bar_diameter_mm": 16,
            },
        )
        # Empty CSV should fail gracefully
        assert resp.status_code in (200, 422)
