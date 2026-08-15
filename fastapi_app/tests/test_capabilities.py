"""Cross-surface tests for canonical capability discovery."""

from __future__ import annotations

from fastapi.testclient import TestClient

from structural_lib.services.api import get_supported_is456_capability_document


def test_capability_route_matches_python_contract(client: TestClient):
    response = client.get("/api/v1/library/capabilities")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"] == get_supported_is456_capability_document()
    assert body["data"]["code_edition"] == "IS 456:2000"
    assert all(
        item["qualified_review_required"] for item in body["data"]["capabilities"]
    )
    wall = next(
        item for item in body["data"]["capabilities"] if item["element"] == "wall"
    )
    assert wall["public_workflows"] == ["design_braced_wall_is456"]
    assert "100-200 mm" in wall["supported_case"]


def test_capability_route_has_a_typed_openapi_success_schema(client: TestClient):
    schema = client.get("/openapi.json").json()
    operation = schema["paths"]["/api/v1/library/capabilities"]["get"]

    success_schema = operation["responses"]["200"]["content"]["application/json"][
        "schema"
    ]
    assert "$ref" in success_schema
    assert "IS456CapabilityDocumentModel" in str(schema["components"]["schemas"])
