"""Cross-layer tests for the thin workflow catalogue transport."""

from __future__ import annotations

from fastapi.testclient import TestClient

from structural_lib.services.workflow_catalog import get_workflow_catalog_document


def test_catalog_route_round_trips_library_document(client: TestClient) -> None:
    response = client.get("/api/v1/catalog/workflows")

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": get_workflow_catalog_document(),
    }
    assert response.headers["cache-control"] == "public, max-age=300"
    assert response.headers["etag"].startswith('"')


def test_catalog_route_supports_additive_alias_and_rejects_breaking_version(
    client: TestClient,
) -> None:
    compatible = client.get("/api/v1/catalog/workflows?version=1.0")
    breaking = client.get("/api/v1/catalog/workflows?version=2.0.0")

    assert compatible.status_code == 200
    assert compatible.json()["data"] == get_workflow_catalog_document()
    assert breaking.status_code == 409
    assert breaking.json()["error"]["code"] == "UNSUPPORTED_CATALOG_VERSION"


def test_catalog_openapi_success_shape_is_typed(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    operation = schema["paths"]["/api/v1/catalog/workflows"]["get"]

    success = operation["responses"]["200"]["content"]["application/json"]["schema"]
    assert "$ref" in success
    assert "WorkflowCatalogDocumentModel" in str(schema["components"]["schemas"])
