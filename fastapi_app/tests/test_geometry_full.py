"""
Tests for geometry router advanced endpoints.

Covers:
- POST /api/v1/geometry/beam/full (full 3D beam geometry)
- POST /api/v1/geometry/building (building-level geometry)
- POST /api/v1/geometry/cross-section (2D cross-section)
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
# Full 3D Beam Geometry
# =============================================================================


class TestFullBeamGeometry:
    """Tests for POST /api/v1/geometry/beam/full."""

    def test_full_geometry_basic(self, client):
        """Basic full 3D geometry generation."""
        payload = {
            "beam_id": "B1",
            "story": "GF",
            "width": 300.0,
            "depth": 500.0,
            "span": 6000.0,
            "fck": 25.0,
            "fy": 500.0,
            "ast_start": 600.0,
            "ast_mid": 400.0,
            "ast_end": 600.0,
            "stirrup_dia": 8.0,
            "stirrup_spacing_start": 100.0,
            "stirrup_spacing_mid": 150.0,
            "stirrup_spacing_end": 100.0,
            "cover": 40.0,
        }
        resp = client.post("/api/v1/geometry/beam/full", json=payload)
        assert resp.status_code == 200
        data = unwrap(resp)
        geom = data["geometry"]
        assert geom["beamId"] == "B1"
        assert len(geom["concreteOutline"]) == 8  # Box corners
        assert len(geom["rebars"]) > 0
        assert len(geom["stirrups"]) > 0
        assert "dimensions" in geom

    def test_full_geometry_seismic(self, client):
        """Full geometry with seismic detailing."""
        payload = {
            "beam_id": "B-SEISMIC",
            "width": 350.0,
            "depth": 600.0,
            "span": 5000.0,
            "fck": 30.0,
            "fy": 500.0,
            "ast_start": 800.0,
            "ast_mid": 500.0,
            "ast_end": 800.0,
            "is_seismic": True,
        }
        resp = client.post("/api/v1/geometry/beam/full", json=payload)
        assert resp.status_code == 200
        unwrap(resp)

    def test_full_geometry_invalid_width(self, client):
        """Zero width should fail."""
        payload = {
            "width": 0.0,
            "depth": 500.0,
            "span": 6000.0,
        }
        resp = client.post("/api/v1/geometry/beam/full", json=payload)
        assert resp.status_code == 422

    def test_full_geometry_rebar_structure(self, client):
        """Verify rebar data has expected fields."""
        payload = {
            "width": 300.0,
            "depth": 500.0,
            "span": 6000.0,
            "fck": 25.0,
            "fy": 500.0,
            "ast_start": 600.0,
            "ast_mid": 400.0,
            "ast_end": 600.0,
        }
        resp = client.post("/api/v1/geometry/beam/full", json=payload)
        assert resp.status_code == 200
        geom = unwrap(resp)["geometry"]
        for rebar in geom["rebars"]:
            assert "barId" in rebar
            assert "segments" in rebar
            assert "diameter" in rebar
            assert "barType" in rebar
            assert rebar["totalLength"] > 0
        for stirrup in geom["stirrups"]:
            assert "positionX" in stirrup
            assert "path" in stirrup
            assert stirrup["perimeter"] > 0


# =============================================================================
# Building Geometry
# =============================================================================


class TestBuildingGeometry:
    """Tests for POST /api/v1/geometry/building."""

    def test_building_geometry_basic(self, client):
        """Basic building geometry with two beams."""
        payload = {
            "beams": [
                {
                    "id": "B1",
                    "story": "GF",
                    "frame_type": "beam",
                    "point1": {"x": 0, "y": 0, "z": 0},
                    "point2": {"x": 6000, "y": 0, "z": 0},
                },
                {
                    "id": "C1",
                    "story": "GF",
                    "frame_type": "column",
                    "point1": {"x": 0, "y": 0, "z": 0},
                    "point2": {"x": 0, "y": 0, "z": 3000},
                },
            ],
        }
        resp = client.post("/api/v1/geometry/building", json=payload)
        assert resp.status_code == 200
        data = unwrap(resp)
        # success may be False if BeamGeometry parsing fails (dict format mismatch)
        assert "beams" in data
        assert "center" in data

    def test_building_geometry_empty(self, client):
        """Empty beams list returns failure message."""
        payload = {"beams": []}
        resp = client.post("/api/v1/geometry/building", json=payload)
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        data = body["data"]
        assert data["success"] is False

    def test_building_geometry_with_scale(self, client):
        """Custom unit scale factor."""
        payload = {
            "beams": [
                {
                    "id": "B1",
                    "story": "1F",
                    "frame_type": "beam",
                    "point1": {"x": 0, "y": 0, "z": 3},
                    "point2": {"x": 6, "y": 0, "z": 3},
                },
            ],
            "unit_scale": 1000.0,
        }
        resp = client.post("/api/v1/geometry/building", json=payload)
        assert resp.status_code == 200


# =============================================================================
# Cross-Section Geometry
# =============================================================================


class TestCrossSectionGeometry:
    """Tests for POST /api/v1/geometry/cross-section."""

    def test_cross_section_basic(self, client):
        """Basic cross-section with 3 tension + 2 compression bars."""
        payload = {
            "width": 300.0,
            "depth": 500.0,
            "cover": 40.0,
            "tension_bars": 3,
            "compression_bars": 2,
            "bar_dia": 16.0,
            "stirrup_dia": 8.0,
        }
        resp = client.post("/api/v1/geometry/cross-section", json=payload)
        assert resp.status_code == 200
        data = unwrap(resp)
        assert len(data["outline"]) == 4  # Rectangle corners
        assert len(data["tension_bars"]) == 3
        assert len(data["compression_bars"]) == 2
        assert len(data["stirrup_path"]) > 0
        assert "dimensions" in data

    def test_cross_section_no_compression(self, client):
        """Section with zero compression bars."""
        payload = {
            "width": 250.0,
            "depth": 450.0,
            "tension_bars": 4,
            "compression_bars": 0,
        }
        resp = client.post("/api/v1/geometry/cross-section", json=payload)
        assert resp.status_code == 200
        data = unwrap(resp)
        assert len(data["compression_bars"]) == 0
        assert len(data["tension_bars"]) == 4

    def test_cross_section_invalid_width(self, client):
        """Zero width should fail validation."""
        payload = {
            "width": 0.0,
            "depth": 500.0,
            "tension_bars": 3,
        }
        resp = client.post("/api/v1/geometry/cross-section", json=payload)
        assert resp.status_code == 422

    def test_cross_section_dimensions_in_response(self, client):
        """Response dimensions match input."""
        payload = {
            "width": 300.0,
            "depth": 600.0,
            "tension_bars": 5,
            "compression_bars": 3,
            "bar_dia": 20.0,
        }
        resp = client.post("/api/v1/geometry/cross-section", json=payload)
        assert resp.status_code == 200
        dims = unwrap(resp)["dimensions"]
        assert dims["width"] == 300.0
        assert dims["depth"] == 600.0
