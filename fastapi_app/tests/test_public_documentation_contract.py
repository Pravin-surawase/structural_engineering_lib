"""Executable contracts for the public REST documentation.

These tests intentionally mirror the high-traffic examples in
``docs/reference/api-levels.md`` and
``docs/reference/fastapi-rest-api.md``. Calculation regression tests own exact
engineering values; this module owns the public request fields, response
envelope, and documented access path.
"""

from pathlib import Path

from fastapi.testclient import TestClient

from fastapi_app import __version__

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_documented_beam_request_and_response_path(client: TestClient):
    """The documented raw-HTTP beam quick start is copyable."""
    response = client.post(
        "/api/v1/design/beam",
        json={
            "width": 300,
            "depth": 500,
            "moment": 150,
            "shear": 75,
            "fck": 25,
            "fy": 500,
            "clear_cover": 25,
        },
    )

    assert response.status_code == 200
    envelope = response.json()
    assert envelope["success"] is True
    design = envelope["data"]
    assert design["success"] is True
    assert design["result_envelope"]["engineering_status"] == "PASS"
    assert design["effective_depth_basis"]["source"] == "DERIVED"
    assert design["flexure"]["ast_required"] > 0
    assert 0 <= design["utilization_ratio"] <= 1


def test_documented_health_version_matches_application(client: TestClient):
    """The version shown in the public health reference is current."""
    health = client.get("/health")
    info = client.get("/health/info")

    assert health.status_code == 200
    assert info.status_code == 200
    assert health.json()["version"] == __version__
    assert info.json()["api_version"] == __version__
    assert info.json()["structural_lib_available"] is True


def test_public_guides_retain_the_maintained_contract_language():
    """Known stale field and response paths must not return to public guides."""
    api_levels = (REPO_ROOT / "docs/reference/api-levels.md").read_text(
        encoding="utf-8"
    )
    rest_reference = (REPO_ROOT / "docs/reference/fastapi-rest-api.md").read_text(
        encoding="utf-8"
    )

    assert "sl.design_column_is456(" in api_levels
    assert '"width": 300' in api_levels
    assert "`.is_safe()`" not in api_levels
    assert 'design = payload["data"]' in rest_reference
    assert "It is not an engineering PASS" in rest_reference
    assert "structural-problem/v1" in rest_reference
    assert "result['flexure']" not in rest_reference
    assert '"version": "0.1.0"' not in rest_reference
