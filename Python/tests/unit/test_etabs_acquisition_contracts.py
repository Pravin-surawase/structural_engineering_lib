# SPDX-License-Identifier: MIT
"""C0 generic acquisition contracts; no ETABS, UI, or SQLite parsing."""

from __future__ import annotations

import builtins
import hashlib
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
    finalize_etabs_sqlite_export_manifest_v1,
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
