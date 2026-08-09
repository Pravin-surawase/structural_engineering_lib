"""OpenAPI and envelope contracts for the typed column and library-core routes."""

from __future__ import annotations


_SUCCESS_RESPONSE_SCHEMAS = {
    "/api/v1/design/column": "APIResponse_ColumnDesignResponse_",
    "/api/v1/design/column/additional-moment": "APIResponse_AdditionalMomentResponse_",
    "/api/v1/design/column/axial": "APIResponse_ColumnAxialResponse_",
    "/api/v1/design/column/biaxial-check": "APIResponse_BiaxialCheckResponse_",
    "/api/v1/design/column/classify": "APIResponse_ColumnClassifyResponse_",
    "/api/v1/design/column/detailing": "APIResponse_ColumnDetailingResponse_",
    "/api/v1/design/column/ductile-detailing": (
        "APIResponse_ColumnDuctileDetailingResponse_"
    ),
    "/api/v1/design/column/eccentricity": "APIResponse_ColumnEccentricityResponse_",
    "/api/v1/design/column/effective-length": "APIResponse_EffectiveLengthResponse_",
    "/api/v1/design/column/helical-check": "APIResponse_HelicalCheckResponse_",
    "/api/v1/design/column/interaction-curve": "APIResponse_PMInteractionResponse_",
    "/api/v1/design/column/long-column": "APIResponse_LongColumnResponse_",
    "/api/v1/design/column/uniaxial": "APIResponse_ColumnUniaxialResponse_",
    "/api/v1/design/footing/load-transfer": "APIResponse_FootingLoadTransferResponse_",
    "/api/v1/design/slab/one-way": "APIResponse_OneWaySlabDesignResponse_",
}


def test_target_routes_expose_typed_success_contracts(client):
    """Every maintained JSON target route exposes its concrete payload schema."""
    schema = client.get("/openapi.json").json()

    for path, response_schema in _SUCCESS_RESPONSE_SCHEMAS.items():
        operation = schema["paths"][path]["post"]
        response = operation["responses"]["200"]["content"]["application/json"]
        assert response["schema"] == {"$ref": f"#/components/schemas/{response_schema}"}


def test_typed_success_responses_preserve_existing_envelope_shape(client):
    """Response filtering must not add optional envelope fields to JSON 2xx output."""
    column_response = client.post(
        "/api/v1/design/column/effective-length",
        json={"l_mm": 3000, "end_condition": "FIXED_FIXED"},
    )
    library_response = client.post(
        "/api/v1/design/slab/one-way",
        json={
            "short_effective_span_mm": 3000,
            "long_effective_span_mm": 7500,
            "thickness_mm": 150,
            "d_mm": 125,
            "factored_area_load_kn_per_m2": 10,
            "fck_n_per_mm2": 20,
            "fy_n_per_mm2": 415,
            "main_bar_diameter_mm": 10,
            "main_bar_spacing_mm": 250,
            "distribution_bar_diameter_mm": 8,
            "distribution_bar_spacing_mm": 250,
        },
    )

    for response in (column_response, library_response):
        assert response.status_code == 200
        assert set(response.json()) == {"success", "data"}


def test_typed_import_format_metadata_does_not_add_null_fields(client):
    """Optional schema fields stay absent when the existing payload omits them."""
    response = client.get("/api/v1/import/formats")

    assert response.status_code == 200
    formats = response.json()["data"]["formats"]
    assert "example" not in formats[0]
    assert "example" in formats[-1]
