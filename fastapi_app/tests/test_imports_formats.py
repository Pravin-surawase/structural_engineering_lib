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
from structural_lib.services.batch import design_project_beams_v1


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


@pytest.mark.parametrize("transport", ["file", "text", "dual"])
def test_imported_depth_reaches_project_design(client, transport):
    geometry_header = "beam_id,b_mm,D_mm,d_mm,span_mm,fck,fy,cover_mm"
    geometry_values = "B1,300,500,470,6000,25,500,40"
    combined = f"{geometry_header},mu_knm,vu_kn\n{geometry_values},100,70\n"
    defaults = {
        "fck_mpa": 25,
        "fy_mpa": 500,
        "cover_mm": 40,
        "stirrup_diameter_mm": 8,
        "tension_bar_diameter_mm": 16,
    }
    if transport == "text":
        response = client.post(
            "/api/v1/import/csv/text",
            params={
                **defaults,
                "csv_text": combined,
                "format_hint": "generic",
            },
        )
    elif transport == "file":
        response = client.post(
            "/api/v1/import/csv",
            data={
                **defaults,
                "format_hint": "generic",
            },
            files={"file": ("beams.csv", combined, "text/csv")},
        )
    else:
        response = client.post(
            "/api/v1/import/dual-csv",
            params={"format_hint": "generic"},
            data=defaults,
            files={
                "geometry_file": (
                    "geometry.csv",
                    f"{geometry_header}\n{geometry_values}\n",
                    "text/csv",
                ),
                "forces_file": (
                    "forces.csv",
                    "beam_id,mu_knm,vu_kn\nB1,100,70\n",
                    "text/csv",
                ),
            },
        )
    assert response.status_code == 200, response.text
    beam = unwrap(response)["beams"][0]
    assert beam["depth_mm"] == 500
    assert beam["d_mm"] == 470
    assert beam["source_metadata"]["d_mm"] == 470
    assert "effective_depth_basis" not in beam["source_metadata"]
    request = {
        "schema_version": "project-beam-design/v1",
        "member_id": beam["source_id"],
        "b_mm": beam["width_mm"],
        "D_mm": beam["depth_mm"],
        "d_mm": beam["d_mm"],
        "fck_nmm2": beam["fck_mpa"],
        "fy_nmm2": beam["fy_mpa"],
        "mu_knm": beam["mu_knm"],
        "vu_kn": beam["vu_kn"],
    }
    response = client.post("/api/v1/import/project-beams", json=[request])
    assert response.status_code == 200, response.text
    actual = unwrap(response)["members"][0]
    expected = design_project_beams_v1([request]).to_dict()["members"][0]
    assert actual["input"]["d_mm"] == 470
    assert actual["calculation"]["flexure"] == expected["calculation"]["flexure"]


def test_invalid_source_depth_returns_no_importable_beams(client):
    response = client.post(
        "/api/v1/import/csv/text",
        params={
            "csv_text": (
                "beam_id,b_mm,D_mm,d_mm,fck,fy,cover_mm,mu_knm,vu_kn\n"
                "B1,300,500,470,25,500,40,100,70\n"
                "B2,300,500,500,25,500,40,100,70\n"
            ),
            "format_hint": "generic",
            "fck_mpa": 25,
            "fy_mpa": 500,
            "cover_mm": 40,
            "stirrup_diameter_mm": 8,
            "tension_bar_diameter_mm": 16,
        },
    )
    assert response.status_code == 422
    assert "CSV row 3" in response.text
