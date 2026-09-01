"""REST semantics for the bounded live ETABS bridge."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_app.auth import (
    require_etabs_live_mutation,
    require_etabs_live_read,
    require_loopback_request,
)
from fastapi_app.main import app as default_app
from fastapi_app.routers import etabs_bridge
from fastapi_app.tests.conftest import unwrap
from structural_lib.services.etabs_beam_baseline import (
    ETABSBaselineBuildResultV1,
    ETABSBaselineBuildStatus,
    ETABSBaselineDisposition,
    ETABSBaselineDispositionV1,
    ETABSBaselineIssueV1,
    ETABSBaselineRowKind,
)
from structural_lib.services.etabs_beam_bridge import (
    ETABSBeamBaselineCapacityError,
    ETABSBeamBaselineCapacityV1,
    ETABSBeamBaselineCountsV1,
    ETABSBeamBaselineTransportV1,
)
from structural_lib.services.contracts.etabs_w3 import (
    W3BuildIssueV1,
    W3BuildStatusV1,
)
from structural_lib.services.etabs_beam_baseline import ETABSModelFileSnapshotV1
from structural_lib.services.etabs_catalogue_bridge import (
    ETABSLiveCaseStatusV1,
    ETABSLiveCatalogueStateV1,
    ETABSLiveCatalogueTransportV1,
    ETABSLiveSelectionStateV1,
)
from structural_lib.services.etabs_live_bridge import (
    ETABSBridgeStatusV1,
    ETABSConnectionError,
    ETABSDataError,
)
from structural_lib.services.etabs_result_catalogue_adapter import (
    ETABSCatalogueAdapterResultV1,
)


@pytest.fixture
def client():
    """Mount every bridge class while bypassing policy for transport unit tests."""

    test_app = FastAPI()
    test_app.dependency_overrides[require_loopback_request] = lambda: None
    test_app.dependency_overrides[require_etabs_live_read] = lambda: None
    test_app.dependency_overrides[require_etabs_live_mutation] = lambda: None
    test_app.include_router(etabs_bridge.offline_router, prefix="/api/v1")
    test_app.include_router(etabs_bridge.live_read_router, prefix="/api/v1")
    test_app.include_router(etabs_bridge.live_mutation_router, prefix="/api/v1")
    with TestClient(test_app) as test_client:
        yield test_client


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

    assert response.status_code == 200, response.text
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


def test_baseline_preflight_maps_unreadable_model_to_unprocessable(client, monkeypatch):
    def fail():
        raise ETABSDataError(
            "ETABS_MODEL_FILE_UNREADABLE", "The copied model could not be read."
        )

    monkeypatch.setattr(etabs_bridge, "inspect_etabs_beam_baseline_v1", fail)

    response = client.post("/api/v1/etabs-bridge/v1/beam-baseline/preflight")

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "ETABS_MODEL_FILE_UNREADABLE"


def test_blocked_baseline_is_a_complete_domain_result_not_partial_success(
    client, monkeypatch
):
    disposition = ETABSBaselineDispositionV1(
        row_id="etabs-row:123",
        row_kind=ETABSBaselineRowKind.RESULT_SELECTION,
        source_id="ULS-1",
        disposition=ETABSBaselineDisposition.BLOCKED,
        reason_code="RESULT_SELECTION_NOT_ACTIVE",
        message="The requested combination is not selected for output.",
    )
    issue = ETABSBaselineIssueV1(
        code=disposition.reason_code,
        path="result_selection:ULS-1",
        message=disposition.message,
    )
    transport = ETABSBeamBaselineTransportV1(
        build_result=ETABSBaselineBuildResultV1(
            status=ETABSBaselineBuildStatus.BLOCKED,
            dispositions=(disposition,),
            issues=(issue,),
            baseline=None,
        ),
        counts=ETABSBeamBaselineCountsV1(
            stories=0,
            frames=0,
            connectivity_rows=0,
            result_sets=0,
            result_station_rows=0,
            disposition_rows=1,
            projected_excel_rows=0,
        ),
        capacity=ETABSBeamBaselineCapacityV1(),
        baseline_hash_basis_json=None,
        baseline_hash_basis_utf8_bytes=0,
    )
    monkeypatch.setattr(
        etabs_bridge, "run_etabs_beam_baseline_v1", lambda _request: transport
    )

    response = client.post(
        "/api/v1/etabs-bridge/v1/beam-baseline",
        json={
            "authorized_model_file": {
                "model_path": r"C:\Models\W2.edb",
                "model_name": "W2.edb",
                "sha256": "a" * 64,
                "byte_count": 10,
                "modified_at_utc": "2026-08-29T05:00:00Z",
                "observed_at_utc": "2026-08-29T05:01:00Z",
            },
            "expected_etabs_version": "ETABS 23.3.1",
            "expected_etabs_version_number": 23.31,
            "expected_present_units_enum": 6,
            "expected_runtime_provenance": {
                "library_version": "0.24.0",
                "library_content_identity": "b" * 64,
                "python_version": "3.11.15",
                "platform": "Windows-11",
                "com_provider": "comtypes/1.4.16;64-bit",
            },
            "expected_getter_matrix_sha256": "c" * 64,
            "result_selections": [{"kind": "COMBINATION", "name": "ULS-1"}],
            "approved_copy_confirmed": True,
        },
    )

    assert response.status_code == 200, response.text
    data = unwrap(response)
    assert data["build_result"]["status"] == "BLOCKED"
    assert data["build_result"]["baseline"] is None
    assert data["baseline_hash_basis_json"] is None


def test_baseline_capacity_error_maps_to_payload_too_large(client, monkeypatch):
    def fail(_request):
        raise ETABSBeamBaselineCapacityError(
            "ETABS_BASELINE_ROW_LIMIT_EXCEEDED", "The complete baseline is too large."
        )

    monkeypatch.setattr(etabs_bridge, "run_etabs_beam_baseline_v1", fail)
    payload = {
        "authorized_model_file": {
            "model_path": r"C:\Models\W2.edb",
            "model_name": "W2.edb",
            "sha256": "a" * 64,
            "byte_count": 10,
            "modified_at_utc": "2026-08-29T05:00:00Z",
            "observed_at_utc": "2026-08-29T05:01:00Z",
        },
        "expected_etabs_version": "ETABS 23.3.1",
        "expected_etabs_version_number": 23.31,
        "expected_present_units_enum": 6,
        "expected_runtime_provenance": {
            "library_version": "0.24.0",
            "library_content_identity": "b" * 64,
            "python_version": "3.11.15",
            "platform": "Windows-11",
            "com_provider": "comtypes/1.4.16;64-bit",
        },
        "expected_getter_matrix_sha256": "c" * 64,
        "result_selections": [{"kind": "COMBINATION", "name": "ULS-1"}],
        "approved_copy_confirmed": True,
    }

    response = client.post("/api/v1/etabs-bridge/v1/beam-baseline", json=payload)

    assert response.status_code == 413, response.text
    assert response.json()["error"]["code"] == "ETABS_BASELINE_ROW_LIMIT_EXCEEDED"


def test_result_catalogue_returns_complete_blocked_domain_result(client, monkeypatch):
    snapshot = ETABSModelFileSnapshotV1(
        model_path=r"C:\Models\W3.edb",
        model_name="W3.edb",
        sha256="a" * 64,
        byte_count=10,
        modified_at_utc="2026-08-29T05:00:00Z",
        observed_at_utc="2026-08-29T05:01:00Z",
    )
    state = ETABSLiveCatalogueStateV1(
        model_path=snapshot.model_path,
        etabs_version="ETABS 23.3.1",
        etabs_version_number=23.31,
        model_locked=True,
        present_units_enum=6,
        case_statuses=(ETABSLiveCaseStatusV1(name="DEAD", raw_status=4),),
        output_selections=(
            ETABSLiveSelectionStateV1(
                kind="COMBINATION",
                name="ULS-1",
                selected=True,
            ),
        ),
    )
    transport = ETABSLiveCatalogueTransportV1(
        adapter_result=ETABSCatalogueAdapterResultV1(
            status=W3BuildStatusV1.BLOCKED,
            issues=(
                W3BuildIssueV1(
                    code="CASE_FAMILY_NOT_MODELED",
                    path="LoadCases.GetTypeOAPI_1",
                    message="The selected case family is not modeled.",
                ),
            ),
            operation_evidence=(),
            normalized_request=None,
            catalogue=None,
        ),
        model_file_before=snapshot,
        model_file_after=snapshot,
        live_state_before=state,
        live_state_after=state,
        catalogue_hash_basis_json=None,
        catalogue_hash_basis_utf8_bytes=0,
    )
    monkeypatch.setattr(
        etabs_bridge,
        "run_etabs_live_catalogue_v1",
        lambda _request: transport,
    )
    response = client.post(
        "/api/v1/etabs-bridge/v1/result-catalogue",
        json={
            "authorized_model_file": snapshot.model_dump(mode="json"),
            "expected_etabs_version": "ETABS 23.3.1",
            "expected_etabs_version_number": 23.31,
            "expected_present_units_enum": 6,
            "runtime_identity_sha256": "b" * 64,
            "getter_matrix_sha256": "c" * 64,
            "model_observation_before": "model-file-sha256:" + "a" * 64,
            "model_observation_after": "model-file-sha256:" + "a" * 64,
            "observed_at_utc": "2026-08-29T05:01:00Z",
            "result_selections": [{"kind": "COMBINATION", "name": "ULS-1"}],
            "approved_copy_confirmed": True,
        },
    )

    assert response.status_code == 200, response.text
    data = unwrap(response)
    assert data["adapter_result"]["status"] == "BLOCKED"
    assert data["adapter_result"]["catalogue"] is None
    assert data["catalogue_hash_basis_json"] is None


def test_beam_demand_rejects_incomplete_transport_payload(client):
    response = client.post("/api/v1/etabs-bridge/v1/beam-demand", json={})

    assert response.status_code == 422


def test_default_openapi_exposes_offline_etabs_operations_only():
    paths = default_app.openapi()["paths"]
    assert "/api/v1/etabs-bridge/v1/status" in paths
    assert "/api/v1/etabs-bridge/v1/beam-demand" in paths
    assert "/api/v1/etabs-bridge/v1/connect" not in paths
    assert "/api/v1/etabs-bridge/v1/beam-pilot" not in paths
    assert "/api/v1/etabs-bridge/v1/beam-baseline/preflight" not in paths
    assert "/api/v1/etabs-bridge/v1/beam-baseline" not in paths
    assert "/api/v1/etabs-bridge/v1/result-catalogue" not in paths
