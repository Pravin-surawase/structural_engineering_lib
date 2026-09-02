# SPDX-License-Identifier: MIT
"""C0 generic acquisition contracts; no ETABS, UI, or SQLite parsing."""

from __future__ import annotations

import builtins
import hashlib
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from pydantic import ValidationError

from structural_lib.services.etabs_acquisition_contracts import (
    ETABSConcreteDesignBasisDraftV1,
    ETABSDesignSettingV1,
    ETABSExportBoundsV1,
    ETABSRequestedTableV1,
    ETABSSQLiteExportManifestDraftV1,
    build_etabs_concrete_design_basis_v1,
    build_etabs_installed_sqlite_evidence_v1,
    finalize_etabs_sqlite_export_manifest_v1,
    inventory_etabs_sqlite_export_v1,
)
from structural_lib.services.etabs_session_guard import (
    ProcessObservationV1,
    build_etabs_result_epoch_v1,
    build_etabs_runtime_fingerprint_v1,
    discover_etabs_processes_v1,
)

T0 = datetime(2026, 9, 2, 0, 0, tzinfo=UTC)
HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64


def _epoch(tmp_path: Path):
    executable = tmp_path / "ETABS.exe"
    executable.write_bytes(b"offline executable fixture")
    process = discover_etabs_processes_v1(
        process_provider=lambda: (
            ProcessObservationV1(
                pid=6100,
                start_time_utc=T0 - timedelta(hours=1),
                executable_path=str(executable),
                executable_version="23.3.1",
                architecture="x86_64",
            ),
        ),
        observed_at_utc=T0,
    )[0]
    runtime = build_etabs_runtime_fingerprint_v1(
        process,
        com_shape_runtime="unavailable",
        observed_at_utc=T0,
    )
    epoch = build_etabs_result_epoch_v1(
        model_identity_sha256=HASH_A,
        runtime_fingerprint=runtime,
        process_instance=process,
        transaction_id="TX-C0-1",
        authorized_cases=("ULS",),
        case_dependency_closure=("ULS",),
        pre_statuses={"ULS": "NOT_RUN"},
        post_statuses={"ULS": "FINISHED"},
        run_flags={"ULS": True},
        analysis_call_ids=("CALL-ANALYSIS-1",),
        design_call_ids=("CALL-DESIGN-1",),
        selection_sha256=HASH_B,
        result_sha256=HASH_C,
        uninterrupted_process=True,
        uninterrupted_runtime=True,
        design_basis_sha256=HASH_C,
        observed_at_utc=T0,
    )
    return runtime, epoch


def _table() -> ETABSRequestedTableV1:
    return ETABSRequestedTableV1(
        request_id="request:design-summary",
        requested_table_key="UNOBSERVED_C1_TABLE_KEY",
        requested_fields=("UNOBSERVED_FIELD_A", "UNOBSERVED_FIELD_B"),
        comparison_row_by_field=(
            ("UNOBSERVED_FIELD_A", "comparison:design-a"),
            ("UNOBSERVED_FIELD_B", "comparison:design-b"),
        ),
        request_basis="Generic C0 fixture names; not an ETABS schema claim.",
    )


def _manifest_draft(tmp_path: Path, artifact: Path):
    runtime, epoch = _epoch(tmp_path)
    return ETABSSQLiteExportManifestDraftV1(
        export_id="fixture:c0-export-1",
        artifact_scope="GENERIC_C0_FIXTURE",
        target_observation_sha256=HASH_B,
        runtime_fingerprint_sha256=runtime.fingerprint_sha256,
        model_identity_sha256=HASH_A,
        result_epoch=epoch,
        requested_tables=(_table(),),
        filter_selection_state_sha256=HASH_C,
        destination_path=str(artifact.resolve()),
        started_at_utc=T0,
        pre_state_sha256=HASH_A,
        bounds=ETABSExportBoundsV1(
            maximum_file_bytes=1024,
            maximum_requested_tables=2,
            maximum_fields_per_table=4,
            maximum_rows_per_table=100,
        ),
        retention_policy="Retain generic fixture for test duration only.",
        limitations=(
            "C0 does not claim any installed ETABS table, column, type, or parser support.",
        ),
    )


def test_concrete_design_basis_binds_epoch_combinations_and_separate_grades(
    tmp_path: Path,
) -> None:
    runtime, epoch = _epoch(tmp_path)
    draft = ETABSConcreteDesignBasisDraftV1(
        basis_id="fixture:design-basis-1",
        basis_status="COMPLETE",
        target_observation_sha256=HASH_B,
        runtime_fingerprint_sha256=runtime.fingerprint_sha256,
        model_identity_sha256=HASH_A,
        result_epoch=epoch,
        design_code="IS 456:2000",
        etabs_build="23.3.1",
        design_combination_ids=("combo:uls",),
        preferences=(
            ETABSDesignSettingV1(
                name="DesignCode",
                disposition="EXPLICIT",
                value="IS456",
                source_call_id="CALL-PREF-1",
            ),
        ),
        overwrites=(
            ETABSDesignSettingV1(
                name="LiveLoadReduction",
                disposition="ETABS_DEFAULT",
                value=False,
                source_call_id="CALL-OVERWRITE-1",
            ),
        ),
        object_design_procedure="CONCRETE_FRAME_DESIGN",
        resolved_assigned_section="R300x500",
        auto_select_state="NOT_AUTO_SELECT",
        section_rebar_definition="BEAM",
        concrete_material="M25",
        fck_nmm2=25.0,
        longitudinal_rebar_material="HYSD500",
        transverse_rebar_material="MS250",
        fy_longitudinal_nmm2=500.0,
        fy_transverse_nmm2=250.0,
        result_item_type="OBJECT_ELEMENT",
        warnings=("Generic fixture warning.",),
        issues=(),
        source_references=("fixture:design-basis-source",),
        limitations=("Diagnostic comparison only; no approval claim.",),
    )

    first = build_etabs_concrete_design_basis_v1(draft)
    second = build_etabs_concrete_design_basis_v1(draft)

    assert first == second
    assert first.fy_longitudinal_nmm2 == 500.0
    assert first.fy_transverse_nmm2 == 250.0
    assert first.result_epoch.epoch_sha256 == epoch.epoch_sha256


def test_generic_manifest_measures_identity_without_schema_or_parser_claim(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact = tmp_path / "generic-fixture.sqlite"
    artifact.write_bytes(b"generic bytes; intentionally not an ETABS SQLite schema")
    draft = _manifest_draft(tmp_path, artifact)
    real_import = builtins.__import__

    def reject_sqlite(name: str, *args, **kwargs):
        if name == "sqlite3" or name.startswith("sqlite3."):
            raise AssertionError("C0 attempted to open or parse SQLite")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", reject_sqlite)
    manifest = finalize_etabs_sqlite_export_manifest_v1(
        draft,
        artifact_path=artifact,
        completed_at_utc=T0 + timedelta(seconds=10),
        post_state_sha256=HASH_A,
    )

    assert manifest.schema_support_status == "UNOBSERVED"
    assert manifest.actual_schema_inventory_sha256 is None
    assert manifest.parser_support_claimed is False
    assert manifest.artifact_sha256 == hashlib.sha256(artifact.read_bytes()).hexdigest()
    assert manifest.artifact_size_bytes == artifact.stat().st_size


def test_manifest_rejects_pending_wal_and_state_drift(tmp_path: Path) -> None:
    artifact = tmp_path / "generic-fixture.sqlite"
    artifact.write_bytes(b"generic fixture")
    draft = _manifest_draft(tmp_path, artifact)
    wal = Path(str(artifact) + "-wal")
    wal.write_bytes(b"pending")

    with pytest.raises(RuntimeError, match="PENDING_WAL_OR_SHM"):
        finalize_etabs_sqlite_export_manifest_v1(
            draft,
            artifact_path=artifact,
            completed_at_utc=T0 + timedelta(seconds=10),
            post_state_sha256=HASH_A,
        )
    wal.unlink()
    with pytest.raises(ValidationError, match="equal pre/post"):
        finalize_etabs_sqlite_export_manifest_v1(
            draft,
            artifact_path=artifact,
            completed_at_utc=T0 + timedelta(seconds=10),
            post_state_sha256=HASH_B,
        )


def test_requested_fields_require_exact_comparison_rows_and_bounds() -> None:
    with pytest.raises(ValidationError, match="every requested field"):
        ETABSRequestedTableV1(
            request_id="bad",
            requested_table_key="UNOBSERVED",
            requested_fields=("A", "B"),
            comparison_row_by_field=(("A", "row:a"),),
            request_basis="Negative generic fixture.",
        )


def _installed_manifest(
    tmp_path: Path,
    artifact: Path,
    *,
    maximum_rows_per_table: int = 100,
):
    runtime, epoch = _epoch(tmp_path)
    requested_tables = (
        ETABSRequestedTableV1(
            request_id="request:beam-forces",
            requested_table_key="Beam Forces",
            requested_fields=("Frame", "Station", "M3", "Missing Field"),
            comparison_row_by_field=(
                ("Frame", "comparison:frame"),
                ("Station", "comparison:station"),
                ("M3", "comparison:m3"),
                ("Missing Field", "comparison:explicit-rejection"),
            ),
            request_basis="Offline C1 schema-inventory fixture.",
        ),
        ETABSRequestedTableV1(
            request_id="request:missing-table",
            requested_table_key="Missing Table",
            requested_fields=("Missing Column",),
            comparison_row_by_field=(("Missing Column", "comparison:missing"),),
            request_basis="Prove explicit table rejection.",
        ),
    )
    draft = ETABSSQLiteExportManifestDraftV1(
        export_id="fixture:c1-export-1",
        artifact_scope="INSTALLED_C1_EXPORT",
        target_observation_sha256=HASH_B,
        runtime_fingerprint_sha256=runtime.fingerprint_sha256,
        model_identity_sha256=HASH_A,
        result_epoch=epoch,
        requested_tables=requested_tables,
        filter_selection_state_sha256=HASH_C,
        destination_path=str(artifact.resolve()),
        started_at_utc=T0,
        pre_state_sha256=HASH_A,
        bounds=ETABSExportBoundsV1(
            maximum_file_bytes=1024 * 1024,
            maximum_requested_tables=4,
            maximum_fields_per_table=16,
            maximum_rows_per_table=maximum_rows_per_table,
        ),
        retention_policy="Retain the offline SQLite fixture for one test only.",
        limitations=(
            "Offline fixture proves inventory mechanics, not an ETABS schema.",
        ),
    )
    with sqlite3.connect(artifact) as connection:
        connection.execute(
            'CREATE TABLE "Beam Forces" ('
            '"Frame" TEXT NOT NULL, "Station" REAL NOT NULL, "M3" REAL, '
            'PRIMARY KEY ("Frame", "Station"))'
        )
        connection.executemany(
            'INSERT INTO "Beam Forces" ("Frame", "Station", "M3") ' "VALUES (?, ?, ?)",
            (("B1", 0.0, -12.5), ("B1", 1.0, 10.25)),
        )
        connection.execute('CREATE TABLE "Metadata" ("Name" TEXT, "Value" TEXT)')
        connection.execute(
            'CREATE TABLE "Odd"" Name; DROP TABLE Metadata;--" ("Value" TEXT)'
        )
    return finalize_etabs_sqlite_export_manifest_v1(
        draft,
        artifact_path=artifact,
        completed_at_utc=T0 + timedelta(seconds=10),
        post_state_sha256=HASH_A,
    )


def test_installed_inventory_binds_complete_schema_and_explicit_rejections(
    tmp_path: Path,
) -> None:
    artifact = tmp_path / "installed-export.sqlite"
    manifest = _installed_manifest(tmp_path, artifact)
    before = (artifact.stat().st_size, artifact.stat().st_mtime_ns)

    inventory = inventory_etabs_sqlite_export_v1(
        manifest,
        artifact_path=artifact,
        inspected_at_utc=T0 + timedelta(seconds=20),
    )
    evidence = build_etabs_installed_sqlite_evidence_v1(manifest, inventory)

    assert tuple(table.table_name for table in inventory.tables) == (
        "Beam Forces",
        "Metadata",
        'Odd" Name; DROP TABLE Metadata;--',
    )
    beam_table = inventory.tables[0]
    assert beam_table.row_count == 2
    assert beam_table.primary_key_columns == ("Frame", "Station")
    assert tuple(column.declared_type for column in beam_table.columns) == (
        "TEXT",
        "REAL",
        "REAL",
    )
    found, missing = inventory.request_resolutions
    assert found.disposition == "FOUND"
    assert tuple(field.disposition for field in found.fields) == (
        "FOUND",
        "FOUND",
        "FOUND",
        "REJECTED",
    )
    assert missing.disposition == "REJECTED"
    assert missing.fields[0].reason == "REQUESTED_TABLE_NOT_FOUND"
    assert inventory.parser_support_claimed is False
    assert evidence.parser_support_claimed is False
    assert evidence.schema_inventory.inventory_sha256 == inventory.inventory_sha256
    assert inventory.tables[1].table_name == "Metadata"
    assert inventory.tables[2].row_count == 0
    assert (artifact.stat().st_size, artifact.stat().st_mtime_ns) == before


def test_installed_inventory_rejects_generic_manifest_before_sqlite_open(
    tmp_path: Path,
) -> None:
    artifact = tmp_path / "generic-fixture.sqlite"
    artifact.write_bytes(b"not SQLite")
    manifest = finalize_etabs_sqlite_export_manifest_v1(
        _manifest_draft(tmp_path, artifact),
        artifact_path=artifact,
        completed_at_utc=T0 + timedelta(seconds=10),
        post_state_sha256=HASH_A,
    )

    with pytest.raises(ValueError, match="installed C1 export"):
        inventory_etabs_sqlite_export_v1(manifest, artifact_path=artifact)


def test_installed_inventory_rejects_artifact_drift_and_row_bound(
    tmp_path: Path,
) -> None:
    drifted_artifact = tmp_path / "drifted.sqlite"
    drifted_manifest = _installed_manifest(tmp_path, drifted_artifact)
    with drifted_artifact.open("ab") as handle:
        handle.write(b"drift")
    with pytest.raises(RuntimeError, match="IDENTITY_MISMATCH"):
        inventory_etabs_sqlite_export_v1(
            drifted_manifest,
            artifact_path=drifted_artifact,
        )

    bounded_artifact = tmp_path / "bounded.sqlite"
    bounded_manifest = _installed_manifest(
        tmp_path,
        bounded_artifact,
        maximum_rows_per_table=1,
    )
    with pytest.raises(RuntimeError, match="ROW_BOUND_EXCEEDED"):
        inventory_etabs_sqlite_export_v1(
            bounded_manifest,
            artifact_path=bounded_artifact,
        )
