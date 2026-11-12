"""
Tests for export router endpoints.

Covers:
- POST /api/v1/export/bbs (CSV download)
- POST /api/v1/export/dxf (DXF download)
- POST /api/v1/export/building-summary (building-level summary)
"""

import csv
import io
import json
from copy import deepcopy

import pytest

from fastapi.testclient import TestClient

from fastapi_app.main import app

ezdxf = pytest.importorskip("ezdxf")


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
        assert "9 line items" in content

    def test_bbs_export_with_compression(self, client):
        """BBS export with compression steel."""
        payload = {
            "beam_id": "B-DBL",
            "width": 300.0,
            "depth": 600.0,
            "span_length": 6000.0,
            "fck": 25.0,
            "fy": 500.0,
            "ast_required": 1200.0,
            "asc_required": 400.0,
        }
        resp = client.post("/api/v1/export/bbs", json=payload)
        assert resp.status_code == 200

    def test_bbs_export_zero_steel(self, client):
        """BBS export rejects zero steel before detailing or schedule creation."""
        payload = {
            "width": 300.0,
            "depth": 500.0,
            "span_length": 6000.0,
            "fck": 25.0,
            "fy": 500.0,
            "ast_required": 0.0,
        }
        resp = client.post("/api/v1/export/bbs", json=payload)
        assert resp.status_code == 422
        assert resp.json()["error"]["details"][0]["loc"] == [
            "body",
            "ast_required",
        ]

    @pytest.mark.parametrize("endpoint", ["bbs", "dxf"])
    @pytest.mark.parametrize("span", [None, 0.0])
    def test_beam_artifact_export_requires_explicit_positive_span(
        self, client, sample_beam_export, endpoint, span
    ):
        """Invalid or missing span stops before detailing and BBS creation."""
        payload = dict(sample_beam_export)
        if span is None:
            del payload["span_length"]
        else:
            payload["span_length"] = span

        resp = client.post(f"/api/v1/export/{endpoint}", json=payload)

        assert resp.status_code == 422
        assert resp.json()["error"]["details"][0]["loc"] == [
            "body",
            "span_length",
        ]

    @pytest.mark.parametrize("endpoint", ["bbs", "dxf"])
    @pytest.mark.parametrize(
        "change",
        [
            {"width": "300"},
            {"include_serviceability": "false"},
            {"unexpected_engineering_field": 999},
        ],
    )
    def test_beam_artifact_export_rejects_coercion_and_unknown_fields(
        self, client, sample_beam_export, endpoint, change
    ):
        resp = client.post(
            f"/api/v1/export/{endpoint}", json={**sample_beam_export, **change}
        )

        assert resp.status_code == 422


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
            "span_length": 5000.0,
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


def test_imported_workbench_downloads_replay_one_checked_layout(client):
    imported = {
        "schema_version": "project-beam-design/v1",
        "member_id": "B1",
        "b_mm": 300,
        "D_mm": 550,
        "d_mm": 492,
        "mu_knm": 160,
        "vu_kn": 90,
        "fck_nmm2": 25,
        "fy_nmm2": 500,
        "source_metadata": {
            "span_mm": 6000,
            "workbench_detailing": {
                "clear_cover_mm": 40,
                "stirrup_diameter_mm": 8,
                "tension_bar_diameter_mm": 20,
            },
        },
    }

    def check():
        response = client.post("/stream/batch-design", json=[imported])
        assert response.status_code == 200
        return next(
            event["workbench"]
            for line in response.text.splitlines()
            if line.startswith("data: ")
            and "workbench" in (event := json.loads(line[6:]))
        )

    layout = check()
    assert layout["status"] == "PASS"
    assert [zone["zone"] for zone in layout["zones"]] == ["start", "mid", "end"]
    request = {key: layout[key] for key in ("checked_request", "checked_layout_id")}
    geometry_response = client.post("/api/v1/geometry/beam/full", json=request)
    assert geometry_response.status_code == 200
    geometry = geometry_response.json()["data"]["geometry"]
    assert geometry["beamId"] == "B1"
    assert sorted((bar["barType"], bar["diameter"]) for bar in geometry["rebars"]) == [
        ("bottom", 20),
        ("bottom", 20),
        ("bottom", 20),
        ("top", 20),
        ("top", 20),
    ]
    assert {tie["diameter"] for tie in geometry["stirrups"]} == {8}
    assert [tie["positionX"] for tie in geometry["stirrups"]] == list(
        range(150, 6000, 300)
    )

    responses = {
        kind: client.post(f"/api/v1/export/{kind}", json=request)
        for kind in ("bbs", "dxf", "report")
    }
    for response in responses.values():
        assert response.status_code == 200
        assert response.headers["X-Checked-Layout-Id"] == layout["checked_layout_id"]
    report = responses["report"].text
    assert layout["checked_layout_id"] in report
    assert "B1" in report
    assert "&quot;mu_knm&quot;: 160.0" in report
    assert "&quot;vu_kn&quot;: 90.0" in report

    schedule = list(csv.DictReader(io.StringIO(responses["bbs"].text.split("\n\n")[0])))
    assert len(schedule) == 9
    drawing = ezdxf.read(io.StringIO(responses["dxf"].text)).modelspace()
    labels = [entity.dxf.text for entity in drawing.query("TEXT")]
    tie_lines = [
        entity
        for entity in drawing.query("LINE")
        if entity.dxf.layer == "REBAR_STIRRUP"
        and entity.dxf.start.x == entity.dxf.end.x
        and entity.dxf.end.y - entity.dxf.start.y == 470
    ]
    tie_x = sorted(entity.dxf.start.x for entity in tie_lines)
    assert len(tie_x) == 20
    assert [x - tie_x[0] for x in tie_x] == list(range(0, 6000, 300))

    for zone, count in zip(layout["zones"], (5, 10, 5), strict=True):
        name = zone["zone"].capitalize()
        letter = name[0]
        assert zone["tension"]["count"] == 3
        assert zone["compression"]["count"] == 2
        assert zone["stirrup"] == {
            "diameter_mm": 8,
            "spacing_mm": 300,
            "legs": 2,
            "count": count,
        }
        for face, prefix, diameter, quantity, label in (
            ("Bottom", "B", 20, 3, "3-20φ"),
            ("Top", "T", 20, 2, "2-20φ"),
            ("Stirrup", "S", 8, count, "2L-8φ@300"),
        ):
            row = next(
                row
                for row in schedule
                if row["bar_mark"].startswith(f"B1-{prefix}-{letter}-")
            )
            assert int(row["no_of_bars"]) == quantity
            assert float(row["diameter_mm"]) == diameter
            assert f"{face} {name}: {row['bar_mark']} {label}" in labels

    imported["source_metadata"]["project_revision"] = 2
    revised = check()
    stale = deepcopy(request)
    stale["checked_request"] = revised["checked_request"]
    assert revised["checked_layout_id"] != layout["checked_layout_id"]
    for kind in ("bbs", "dxf", "report"):
        assert client.post(f"/api/v1/export/{kind}", json=stale).status_code == 409
    assert client.post("/api/v1/geometry/beam/full", json=stale).status_code == 409

    imported["d_mm"] = 490
    assert check()["status"] == "HOLD"
