"""
Tests for detailing router anchorage endpoint.

Covers:
- POST /api/v1/detailing/anchorage-check (IS 456 Cl 26.2.3.3)
"""

import pytest
from fastapi.testclient import TestClient

from fastapi_app.main import app
from fastapi_app.tests.conftest import unwrap


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


class TestAnchorageCheck:
    """Tests for POST /api/v1/detailing/anchorage-check."""

    def test_anchorage_adequate(self, client):
        """Adequate anchorage with wide support."""
        payload = {
            "bar_dia_mm": 16.0,
            "fck": 25.0,
            "fy": 500.0,
            "vu_kn": 80.0,
            "support_width_mm": 400.0,
            "cover_mm": 40.0,
            "bar_type": "deformed",
            "has_standard_bend": True,
        }
        resp = client.post("/api/v1/detailing/anchorage-check", json=payload)
        assert resp.status_code == 200
        data = unwrap(resp)
        assert "is_adequate" in data
        assert data["ld_required"] > 0
        assert data["ld_available"] > 0
        assert data["utilization"] > 0

    def test_anchorage_inadequate_narrow_support(self, client):
        """Narrow support may not provide adequate anchorage."""
        payload = {
            "bar_dia_mm": 25.0,
            "fck": 20.0,
            "fy": 500.0,
            "vu_kn": 200.0,
            "support_width_mm": 150.0,
            "cover_mm": 40.0,
            "bar_type": "deformed",
            "has_standard_bend": False,
        }
        resp = client.post("/api/v1/detailing/anchorage-check", json=payload)
        assert resp.status_code == 200
        data = unwrap(resp)
        # With narrow support and large bar, anchorage may be inadequate
        assert data["ld_required"] > 0

    def test_anchorage_plain_bars(self, client):
        """Plain bars have lower bond stress → longer Ld."""
        payload = {
            "bar_dia_mm": 12.0,
            "fck": 25.0,
            "fy": 415.0,
            "vu_kn": 60.0,
            "support_width_mm": 300.0,
            "cover_mm": 40.0,
            "bar_type": "plain",
            "has_standard_bend": True,
        }
        resp = client.post("/api/v1/detailing/anchorage-check", json=payload)
        assert resp.status_code == 200

    def test_anchorage_invalid_bar_dia(self, client):
        """Bar diameter below minimum should fail validation."""
        payload = {
            "bar_dia_mm": 4.0,
            "fck": 25.0,
            "fy": 500.0,
            "vu_kn": 80.0,
            "support_width_mm": 300.0,
        }
        resp = client.post("/api/v1/detailing/anchorage-check", json=payload)
        assert resp.status_code == 422

    def test_anchorage_missing_required_field(self, client):
        """Missing required fields should return 422."""
        payload = {
            "bar_dia_mm": 16.0,
            "fck": 25.0,
            # Missing vu_kn and support_width_mm
        }
        resp = client.post("/api/v1/detailing/anchorage-check", json=payload)
        assert resp.status_code == 422
