"""REST semantic vectors for Excel Routine Workbench V1."""

from __future__ import annotations

from fastapi_app.tests.conftest import unwrap

HEADERS = [
    "Row ID",
    "Beam ID",
    "Case ID",
    "Mu (kN·m)",
    "Vu (kN)",
    "b (mm)",
    "D (mm)",
    "Depth Basis",
    "d (mm)",
    "Clear Cover (mm)",
    "Stirrup Dia (mm)",
    "Tension Bar Dia (mm)",
    "d' (mm)",
    "Asv (mm²)",
    "fck (N/mm²)",
    "fy (N/mm²)",
    "Shear Basis",
]


def _preview_payload():
    return {
        "selection": {
            "workbook_instance_id": "REST-WORKBOOK-001",
            "first_data_row_number": 2,
            "locale": "en-IN",
            "calculation_mode": "AUTOMATIC",
        },
        "headers": HEADERS,
        "rows": [
            [
                "R1",
                "B1",
                "ULS-1",
                150.0,
                100.0,
                300.0,
                500.0,
                "DERIVED_FROM_BARS",
                None,
                40.0,
                8.0,
                18.0,
                None,
                100.0,
                25.0,
                500.0,
                "AUTO_FROM_FLEXURE",
            ],
            [None] * len(HEADERS),
        ],
    }


def test_definition_keeps_installed_windows_excel_evidence_held(client):
    response = client.get("/api/v1/excel-workbench/v1/definition")
    assert response.status_code == 200
    data = unwrap(response)
    assert data["canonical_function"] == "design_beam_is456"
    assert data["installed_windows_excel_evidence"] == "TO_VERIFY_WINDOWS"
    assert data["workbook_artifact_name"].endswith("-v1.xlsx")
    assert len(data["workbook_artifact_sha256"]) == 64
    assert data["library_version"]
    assert len(data["library_content_identity"]) == 64


def test_preview_then_run_preserves_row_accounting_and_canonical_status(client):
    payload = _preview_payload()
    preview_response = client.post(
        "/api/v1/excel-workbench/v1/mapping-preview", json=payload
    )
    assert preview_response.status_code == 200
    preview = unwrap(preview_response)
    assert preview["is_blocked"] is False

    run_payload = {
        **payload,
        "schema_version": "excel-workbook-run-request/v1",
        "confirmed_mapping_hash": preview["mapping_hash"],
    }
    run_response = client.post("/api/v1/excel-workbench/v1/run", json=run_payload)
    assert run_response.status_code == 200
    result = unwrap(run_response)
    assert result["counts"] == {
        "source_rows": 2,
        "accepted_rows": 1,
        "blocked_rows": 0,
        "excluded_rows": 1,
    }
    assert result["row_ledger"][0]["result_envelope"]["overall_status"] == "PASS"
    assert result["row_ledger"][1]["disposition"] == "EXCLUDED"

    freshness_response = client.post(
        "/api/v1/excel-workbench/v1/freshness",
        json={
            "previous_evidence": {
                "bundle_hash": result["bundle_hash"],
                "source_table_hash": result["source_table_hash"],
                "mapping_hash": result["mapping"]["mapping_hash"],
                "library_content_identity": result["library_content_identity"],
            },
            "current_request": payload,
        },
    )
    assert freshness_response.status_code == 200
    assert unwrap(freshness_response)["freshness_status"] == "CURRENT"


def test_run_rejects_unreviewed_or_changed_mapping(client):
    payload = {
        **_preview_payload(),
        "schema_version": "excel-workbook-run-request/v1",
        "confirmed_mapping_hash": "0" * 64,
    }
    response = client.post("/api/v1/excel-workbench/v1/run", json=payload)
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["data"] is None
    assert "mapping" in body["error"]["message"].lower()
