"""REST semantics for the bounded live ETABS bridge."""

from __future__ import annotations

from fastapi_app.routers import etabs_bridge
from fastapi_app.tests.conftest import unwrap
from structural_lib.services.etabs_live_bridge import (
    ETABSBridgeStatusV1,
    ETABSConnectionError,
    ETABSDataError,
)


def test_status_exposes_python_library_and_bridge_readiness(client, monkeypatch):
    monkeypatch.setattr(
        etabs_bridge,
        "get_etabs_bridge_status_v1",
        lambda: ETABSBridgeStatusV1(
            bridge_status="READY_TO_CONNECT",
            platform="Windows",
            com_dependency="INSTALLED",
            library_version="0.24.0",
            library_content_identity="a" * 64,
        ),
    )

    response = client.get("/api/v1/etabs-bridge/v1/status")

    assert response.status_code == 200
    assert unwrap(response)["bridge_status"] == "READY_TO_CONNECT"
    assert unwrap(response)["library_content_identity"] == "a" * 64


def test_connect_maps_missing_open_etabs_to_conflict(client, monkeypatch):
    def fail():
        raise ETABSConnectionError(
            "ETABS_OPEN_INSTANCE_NOT_FOUND", "Open ETABS before connecting."
        )

    monkeypatch.setattr(etabs_bridge, "connect_etabs_v1", fail)

    response = client.post("/api/v1/etabs-bridge/v1/connect")

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "ETABS_OPEN_INSTANCE_NOT_FOUND"


def test_pilot_maps_unsupported_model_data_to_unprocessable(client, monkeypatch):
    def fail(_request):
        raise ETABSDataError(
            "ETABS_SECTION_NOT_RECTANGULAR", "The first beam is not rectangular."
        )

    monkeypatch.setattr(etabs_bridge, "run_etabs_beam_pilot_v1", fail)
    response = client.post(
        "/api/v1/etabs-bridge/v1/beam-pilot",
        json={
            "result_selection": {"kind": "COMBINATION", "name": "ULS-1"},
            "design_basis": {
                "materials": {"fck_nmm2": 25.0, "fy_nmm2": 500.0},
                "effective_depth_basis": {
                    "clear_cover_mm": 40.0,
                    "stirrup_diameter_mm": 8.0,
                    "tension_bar_diameter_mm": 20.0,
                },
                "d_dash_mm": 40.0,
                "detailing": {
                    "standard": "IS456",
                    "clear_cover_mm": 40.0,
                    "tension_bar_diameter_mm": 20.0,
                    "compression_bar_diameter_mm": 16.0,
                    "nominal_top_steel_ratio": 0.25,
                    "stirrup_diameter_mm": 8.0,
                    "stirrup_legs": 2,
                    "stirrup_spacing_support_mm": 150.0,
                    "stirrup_spacing_mid_mm": 200.0,
                },
            },
            "limit": 5,
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "ETABS_SECTION_NOT_RECTANGULAR"


def test_openapi_exposes_three_typed_etabs_operations(client):
    paths = client.app.openapi()["paths"]
    assert "/api/v1/etabs-bridge/v1/status" in paths
    assert "/api/v1/etabs-bridge/v1/connect" in paths
    assert "/api/v1/etabs-bridge/v1/beam-pilot" in paths
