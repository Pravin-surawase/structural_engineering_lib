"""Executable contracts for the public REST documentation.

These tests intentionally mirror the high-traffic examples in
``docs/reference/api-levels.md`` and
``docs/reference/fastapi-rest-api.md``. Calculation regression tests own exact
engineering values; this module owns the public request fields, response
envelope, and documented access path.
"""

import json
import re
import tomllib
from pathlib import Path

from fastapi.testclient import TestClient
from structural_lib import __version__ as structural_lib_version

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
            "stirrup_dia_mm": 8,
            "main_bar_dia_mm": 20,
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


def test_release_version_matches_every_advertised_surface(client: TestClient):
    """Release metadata, OpenAPI, and maintained clients share one API version."""
    health = client.get("/health")
    info = client.get("/health/info")
    root = client.get("/")
    openapi = client.get("/openapi.json")

    pyproject = tomllib.loads(
        (REPO_ROOT / "Python/pyproject.toml").read_text(encoding="utf-8")
    )
    release_version = pyproject["project"]["version"]
    python_client = (
        REPO_ROOT / "clients/python/structural_client/client.py"
    ).read_text(encoding="utf-8")
    typescript_client = (REPO_ROOT / "clients/typescript/src/index.ts").read_text(
        encoding="utf-8"
    )
    react_package = json.loads(
        (REPO_ROOT / "react_app/package.json").read_text(encoding="utf-8")
    )

    assert health.status_code == 200
    assert info.status_code == 200
    assert root.status_code == 200
    assert openapi.status_code == 200
    assert release_version == __version__ == structural_lib_version
    assert health.json()["version"] == release_version
    assert info.json()["api_version"] == release_version
    assert root.json()["version"] == release_version
    assert openapi.json()["info"]["version"] == release_version
    assert re.search(
        rf'^API_VERSION = "{re.escape(release_version)}"$',
        python_client,
        re.MULTILINE,
    )
    assert re.search(
        rf"^export const API_VERSION = '{re.escape(release_version)}' as const;$",
        typescript_client,
        re.MULTILINE,
    )
    assert react_package["version"] == release_version
    assert info.json()["structural_lib_available"] is True


def test_supplied_beam_openapi_contract_is_exact_and_stable(client: TestClient):
    """The supplied-check request, response, and operation identity are public."""
    schema = client.get("/openapi.json").json()
    operation = schema["paths"]["/api/v1/design/beam/check"]["post"]

    assert operation["operationId"] == "check_beam_api_v1_design_beam_check_post"
    assert operation["requestBody"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/BeamSuppliedCheckRequestV2"
    }
    assert operation["responses"]["200"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/APIResponse_BeamSuppliedCheckResponseV2_"
    }
    request_schema = schema["components"]["schemas"]["BeamSuppliedCheckRequestV2"]
    assert request_schema["properties"]["schema_version"]["const"] == (
        "beam-supplied-check/v2"
    )


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
