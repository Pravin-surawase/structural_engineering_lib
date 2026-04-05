"""
Tests for export router endpoints.

Covers:
- POST /api/v1/export/bbs (CSV download)
- POST /api/v1/export/dxf (DXF download)
- POST /api/v1/export/building-summary (building-level summary)
"""

import pytest

pytest.importorskip("ezdxf")
from fastapi.testclient import TestClient

from fastapi_app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_beam_export():
    """Standard beam data for export endpoints."""
    return {
        "beam_id": "BEAM-T1",
        "width": 300.0,
        "depth": 500.0,
        "span_length": 6000.0,
        "clear_cover": 40.0,
        "fck": 25.0,
        "fy": 500.0,
        "ast_required": 850.0,
        "asc_required": 0.0,
        "moment": 150.0,
        "shear": 80.0,
    }


# =============================================================================
# BBS Export
# =============================================================================


class TestBBSExport:
    """Tests for POST /api/v1/export/bbs."""

    def test_bbs_export_csv(self, client, sample_beam_export):
        """BBS export returns CSV with correct headers."""
        resp = client.post("/api/v1/export/bbs", json=sample_beam_export)
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "text/csv; charset=utf-8"
        assert "Content-Disposition" in resp.headers
        assert "BBS_" in resp.headers["Content-Disposition"]

        # Verify CSV content
        content = resp.text
        assert "bar_mark" in content
        assert "diameter_mm" in content
        assert "total_weight_kg" in content

    def test_bbs_export_with_compression(self, client):
        """BBS export with compression steel."""
        payload = {
            "beam_id": "B-DBL",
            "width": 300.0,
            "depth": 600.0,
            "fck": 25.0,
            "fy": 500.0,
            "ast_required": 1200.0,
            "asc_required": 400.0,
        }
        resp = client.post("/api/v1/export/bbs", json=payload)
        assert resp.status_code == 200

    def test_bbs_export_zero_steel(self, client):
        """BBS export with zero steel area."""
        payload = {
            "width": 300.0,
            "depth": 500.0,
            "fck": 25.0,
            "fy": 500.0,
            "ast_required": 0.0,
        }
        resp = client.post("/api/v1/export/bbs", json=payload)
        assert resp.status_code == 200


# =============================================================================
# DXF Export
# =============================================================================


class TestDXFExport:
    """Tests for POST /api/v1/export/dxf."""

    def test_dxf_export_basic(self, client, sample_beam_export):
        """DXF export returns binary file."""
        resp = client.post("/api/v1/export/dxf", json=sample_beam_export)
        assert resp.status_code == 200
        assert "application/octet-stream" in resp.headers["content-type"]
        assert ".dxf" in resp.headers["Content-Disposition"]
        # DXF file should have some content
        assert len(resp.content) > 0

    def test_dxf_export_custom_beam_id(self, client):
        """DXF filename uses beam_id."""
        payload = {
            "beam_id": "MYBEAM-001",
            "width": 250.0,
            "depth": 450.0,
            "fck": 30.0,
            "fy": 500.0,
            "ast_required": 600.0,
        }
        resp = client.post("/api/v1/export/dxf", json=payload)
        assert resp.status_code == 200
        assert "MYBEAM-001" in resp.headers["Content-Disposition"]


# =============================================================================
# Building Summary Export
# =============================================================================


class TestBuildingSummaryExport:
    """Tests for POST /api/v1/export/building-summary."""

    def test_building_summary_html(self, client):
        """Building summary as HTML."""
        payload = {
            "project_name": "Test Building",
            "beams": [
                {
                    "beam_id": "B1",
                    "story": "GF",
                    "width": 300.0,
                    "depth": 500.0,
                    "fck": 25.0,
                    "fy": 500.0,
                    "moment": 150.0,
                    "shear": 80.0,
                    "ast_required": 850.0,
                    "ast_provided": 942.0,
                    "utilization": 0.75,
                    "is_safe": True,
                },
                {
                    "beam_id": "B2",
                    "story": "1F",
                    "width": 300.0,
                    "depth": 500.0,
                    "fck": 25.0,
                    "fy": 500.0,
                    "moment": 200.0,
                    "shear": 100.0,
                    "ast_required": 1100.0,
                    "ast_provided": 1256.0,
                    "utilization": 0.85,
                    "is_safe": True,
                },
            ],
            "format": "html",
        }
        resp = client.post("/api/v1/export/building-summary", json=payload)
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]

    def test_building_summary_csv(self, client):
        """Building summary as CSV."""
        payload = {
            "project_name": "CSV Test",
            "beams": [
                {
                    "beam_id": "B1",
                    "story": "GF",
                    "width": 300.0,
                    "depth": 500.0,
                    "fck": 25.0,
                    "fy": 500.0,
                    "ast_required": 500.0,
                    "ast_provided": 603.0,
                    "is_safe": True,
                },
            ],
            "format": "csv",
        }
        resp = client.post("/api/v1/export/building-summary", json=payload)
        assert resp.status_code == 200

    def test_building_summary_empty_beams(self, client):
        """Empty beams should return 400."""
        payload = {
            "project_name": "Empty",
            "beams": [],
            "format": "html",
        }
        resp = client.post("/api/v1/export/building-summary", json=payload)
        assert resp.status_code == 400
