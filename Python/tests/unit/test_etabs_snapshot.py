# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""LIB-PRO-007-P5 deterministic ETABS exported-snapshot tests."""

from __future__ import annotations

from pathlib import Path

from structural_lib.core.models import DesignDefaults
from structural_lib.imports import (
    ETABSApprovedExclusionV1,
    ETABSArchivedTableInputV1,
    ETABSBeamRequestBasisV1,
    ETABSCanonicalSnapshotV1,
    ETABSExportUnitsV1,
    ETABSLocalAxisMappingV1,
    ETABSProjectExportIdentityV1,
    ETABSResultIdentityV1,
    ETABSRowDisposition,
    ETABSSnapshotStatus,
    build_etabs_canonical_snapshot_v1,
    verify_etabs_canonical_snapshot_hash_v1,
)
from structural_lib.services.project_beam import ProjectBeamDesignInputV1

FIXTURE_ROOT = Path(__file__).parents[1] / "fixtures" / "etabs" / "p5_trial_export"


def _identity() -> ETABSProjectExportIdentityV1:
    return ETABSProjectExportIdentityV1(
        project_id="P5-TRIAL-HALL",
        export_id="P5-EXPORT-001",
        source_edb_name="trial-hall-model.edb",
        source_edb_sha256="b" * 64,
        exported_at_utc="2026-08-23T12:00:00Z",
        etabs_version="23.0.0 Trial",
    )


def _units() -> ETABSExportUnitsV1:
    return ETABSExportUnitsV1(
        coordinate_length="m",
        station_length="m",
        force="kN",
        moment="kN-m",
        section_dimension="mm",
        material_stress="N/mm2",
    )


def _axis_mapping() -> ETABSLocalAxisMappingV1:
    return ETABSLocalAxisMappingV1(
        moment_source_component="M3",
        moment_destination="mu_knm",
        shear_source_component="V2",
        shear_destination="vu_kn",
        extrema_operation="ABSOLUTE_EXTREMA_WITH_SIGNED_CONCURRENT_VALUES",
        mapping_reference="P5-EXPORT-001 local-axis review",
    )


def _result_identity(name: str = "ULS-DL-LL") -> ETABSResultIdentityV1:
    return ETABSResultIdentityV1(
        kind="LOAD_COMBINATION",
        name=name,
        source_table_name="Element Forces - Frames",
        envelope_basis="INDEPENDENT_ABSOLUTE_EXTREMA_WITH_CONCURRENT_VALUES",
        selection_reference="P5-EXPORT-001 selected combination",
    )


def _approval() -> ETABSApprovedExclusionV1:
    return ETABSApprovedExclusionV1(
        artifact_role="geometry",
        source_row_number=4,
        reason_code="NON_BEAM_FRAME",
        reason="Column row is outside the P5 beam-request scope",
        approval_reference="LIB-PRO-007-P5 fixture scope",
    )


def _archive() -> ETABSArchivedTableInputV1:
    return ETABSArchivedTableInputV1(
        path=FIXTURE_ROOT / "selected-table-catalog.xml",
        table_name="Selected table catalog",
        export_format="XML",
    )


def _build(
    *,
    approvals: tuple[ETABSApprovedExclusionV1, ...] = (_approval(),),
    archives: tuple[ETABSArchivedTableInputV1, ...] = (_archive(),),
    result_identity: ETABSResultIdentityV1 | None = None,
    units: ETABSExportUnitsV1 | None = None,
):
    return build_etabs_canonical_snapshot_v1(
        FIXTURE_ROOT / "connectivity-frame.csv",
        FIXTURE_ROOT / "element-forces-frames.csv",
        FIXTURE_ROOT / "trial-hall-model.e2k",
        project_export_identity=_identity(),
        units=units or _units(),
        local_axis_mapping=_axis_mapping(),
        result_identity=result_identity or _result_identity(),
        defaults=DesignDefaults(
            fck_mpa=25,
            fy_mpa=500,
            cover_mm=40,
            min_bar_dia_mm=12,
            max_bar_dia_mm=32,
            stirrup_dia_mm=8,
        ),
        beam_request_basis=ETABSBeamRequestBasisV1(
            stirrup_diameter_mm=8,
            tension_bar_diameter_mm=20,
        ),
        approved_exclusions=approvals,
        archived_tables=archives,
    )


def test_snapshot_is_deterministic_and_emits_canonical_beam_requests() -> None:
    first = _build()
    second = _build()

    assert first.status is ETABSSnapshotStatus.ACCEPTED
    assert first.snapshot is not None
    assert second.snapshot is not None
    assert first.snapshot.snapshot_sha256 == second.snapshot.snapshot_sha256
    assert (
        first.snapshot.snapshot_sha256
        == "a82d927d347108f56aa3fcdd559c1aa45ba8d87673cb3feec61a03d5eadbf4f8"
    )
    assert verify_etabs_canonical_snapshot_hash_v1(first.snapshot)
    restored = ETABSCanonicalSnapshotV1.model_validate_json(
        first.snapshot.model_dump_json()
    )
    assert verify_etabs_canonical_snapshot_hash_v1(restored)
    assert len(first.beam_requests) == 2
    assert all(
        isinstance(request, ProjectBeamDesignInputV1) for request in first.beam_requests
    )
    assert [request.member_id for request in first.beam_requests] == [
        "etabs:P5-TRIAL-HALL:101",
        "etabs:P5-TRIAL-HALL:102",
    ]
    assert [request.mu_knm for request in first.beam_requests] == [150.0, 130.0]
    assert [request.vu_kn for request in first.beam_requests] == [75.0, 65.0]
    assert all(
        request.source_metadata is not None
        and request.source_metadata["snapshot_sha256"] == first.snapshot.snapshot_sha256
        for request in first.beam_requests
    )


def test_snapshot_accounts_every_source_row_with_exact_dispositions() -> None:
    result = _build()

    assert result.status is ETABSSnapshotStatus.ACCEPTED
    accounting = result.row_accounting
    assert accounting.source_rows == 7
    assert accounting.accepted_rows == 6
    assert accounting.approved_exclusion_rows == 1
    assert accounting.blocked_rows == 0
    assert {row.disposition for row in accounting.rows} == {
        ETABSRowDisposition.ACCEPTED,
        ETABSRowDisposition.APPROVED_EXCLUSION,
    }
    excluded = next(
        row
        for row in accounting.rows
        if row.disposition is ETABSRowDisposition.APPROVED_EXCLUSION
    )
    assert excluded.source_record_id == "C1_L1"
    assert excluded.approval_reference == "LIB-PRO-007-P5 fixture scope"
    assert result.snapshot is not None
    assert result.snapshot.ambiguities == ()


def test_unapproved_exclusion_blocks_without_exposing_requests() -> None:
    result = _build(approvals=())

    assert result.status is ETABSSnapshotStatus.BLOCKED
    assert result.snapshot is None
    assert result.beam_requests == ()
    assert result.row_accounting.source_rows == 7
    assert result.row_accounting.blocked_rows == 1
    assert "etabs.unapproved_exclusion" in {issue.code for issue in result.issues}


def test_result_identity_mismatch_blocks_affected_force_rows() -> None:
    result = _build(result_identity=_result_identity("OTHER-COMBINATION"))

    assert result.status is ETABSSnapshotStatus.BLOCKED
    assert result.snapshot is None
    assert result.row_accounting.source_rows == 7
    assert result.row_accounting.blocked_rows == 4
    assert "etabs.result_identity_mismatch" in {issue.code for issue in result.issues}


def test_unsupported_units_block_without_implicit_conversion() -> None:
    result = _build(units=_units().model_copy(update={"coordinate_length": "mm"}))

    assert result.status is ETABSSnapshotStatus.BLOCKED
    assert result.snapshot is None
    assert result.row_accounting.source_rows == 7
    assert result.row_accounting.blocked_rows == 0
    assert "etabs.unsupported_export_units" in {issue.code for issue in result.issues}


def test_archive_order_does_not_change_snapshot_identity() -> None:
    xml_archive = _archive()
    csv_archive = ETABSArchivedTableInputV1(
        path=FIXTURE_ROOT / "connectivity-frame.csv",
        table_name="Connectivity archive copy",
        export_format="CSV",
    )

    first = _build(archives=(xml_archive, csv_archive))
    second = _build(archives=(csv_archive, xml_archive))

    assert first.status is ETABSSnapshotStatus.ACCEPTED
    assert second.status is ETABSSnapshotStatus.ACCEPTED
    assert first.snapshot is not None
    assert second.snapshot is not None
    assert first.snapshot.snapshot_sha256 == second.snapshot.snapshot_sha256


def test_raw_station_export_blocks_source_envelope_ambiguity() -> None:
    source_envelope = _result_identity().model_copy(
        update={
            "kind": "SOURCE_ENVELOPE",
            "envelope_basis": "SOURCE_PRECOMPUTED_EXTREMA",
        }
    )

    result = _build(result_identity=source_envelope)

    assert result.status is ETABSSnapshotStatus.BLOCKED
    assert result.snapshot is None
    assert result.row_accounting.source_rows == 7
    assert {item.code for item in result.ambiguities} == {
        "etabs.result_kind_mismatch",
        "etabs.envelope_basis_mismatch",
    }


def test_direct_edb_intake_is_rejected_without_parsing(tmp_path: Path) -> None:
    edb = tmp_path / "model.edb"
    edb.write_bytes(b"synthetic sentinel; never parse")

    result = build_etabs_canonical_snapshot_v1(
        FIXTURE_ROOT / "connectivity-frame.csv",
        FIXTURE_ROOT / "element-forces-frames.csv",
        edb,
        project_export_identity=_identity(),
        units=_units(),
        local_axis_mapping=_axis_mapping(),
        result_identity=_result_identity(),
        defaults=DesignDefaults(
            fck_mpa=25,
            fy_mpa=500,
            cover_mm=40,
            min_bar_dia_mm=12,
            max_bar_dia_mm=32,
            stirrup_dia_mm=8,
        ),
        beam_request_basis=ETABSBeamRequestBasisV1(
            stirrup_diameter_mm=8,
            tension_bar_diameter_mm=20,
        ),
        approved_exclusions=(_approval(),),
    )

    assert result.status is ETABSSnapshotStatus.BLOCKED
    assert result.snapshot is None
    assert "etabs.direct_edb_forbidden" in {issue.code for issue in result.issues}
