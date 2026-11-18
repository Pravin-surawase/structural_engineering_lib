# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""F01: keep one ETABS force basis through import and snapshot intake."""

from pathlib import Path

import pytest

from structural_lib.core.models import DesignDefaults
from structural_lib.imports import (
    ETABSBeamRequestBasisV1,
    ETABSExportUnitsV1,
    ETABSLocalAxisMappingV1,
    ETABSProjectExportIdentityV1,
    ETABSResultIdentityV1,
    ETABSSnapshotStatus,
    build_etabs_canonical_snapshot_v1,
    parse_dual_csv_lossless,
)
from structural_lib.services.adapters import ETABSAdapter
from structural_lib.services.import_ledger import ImportIssueCode, ImportStatus


def _defaults() -> DesignDefaults:
    return DesignDefaults(fck_mpa=25, fy_mpa=500, cover_mm=40)


def _files(tmp_path: Path, header: str, values: str, *, rows: int = 1):
    geometry, forces, model = (
        tmp_path / name for name in ("geometry.csv", "forces.csv", "model.e2k")
    )
    geometry.write_text(
        "Story,Label,UniqueName,ObjType,AnalSect,XI,YI,ZI,XJ,YJ,ZJ\n"
        "L1,B1,101,Beam,B300X500,0,0,0,5,0,0\n",
        encoding="utf-8",
    )
    forces.write_text(
        "Story,Label,UniqueName,"
        + header
        + "\n"
        + "".join(
            "L1,B1,101," + values.replace("ULS-1,2,", f"ULS-1,{2 + index},") + "\n"
            for index in range(rows)
        ),
        encoding="utf-8",
    )
    model.write_text(
        "$ Synthetic identity marker; no ETABS analysis.\n", encoding="utf-8"
    )
    return geometry, forces, model


def _snapshot(geometry: Path, forces: Path, model: Path, *, precomputed: bool = False):
    return build_etabs_canonical_snapshot_v1(
        geometry,
        forces,
        model,
        project_export_identity=ETABSProjectExportIdentityV1(
            project_id="F01-SYNTHETIC",
            export_id="F01-EXPORT",
            source_edb_name="synthetic.edb",
            source_edb_sha256="0" * 64,
            exported_at_utc="2026-11-18T00:00:00Z",
            etabs_version="23.0.0",
        ),
        units=ETABSExportUnitsV1(
            coordinate_length="m",
            station_length="m",
            force="kN",
            moment="kN-m",
            section_dimension="mm",
            material_stress="N/mm2",
        ),
        local_axis_mapping=ETABSLocalAxisMappingV1(
            moment_source_component="M3",
            moment_destination="mu_knm",
            shear_source_component="V2",
            shear_destination="vu_kn",
            extrema_operation="ABSOLUTE_EXTREMA_WITH_SIGNED_CONCURRENT_VALUES",
            mapping_reference="Synthetic F01 orientation",
        ),
        result_identity=ETABSResultIdentityV1(
            kind="SOURCE_ENVELOPE" if precomputed else "LOAD_COMBINATION",
            name="Envelope" if precomputed else "ULS-1",
            source_table_name="Element Forces - Frames",
            envelope_basis=(
                "SOURCE_PRECOMPUTED_EXTREMA"
                if precomputed
                else "INDEPENDENT_ABSOLUTE_EXTREMA_WITH_CONCURRENT_VALUES"
            ),
            selection_reference="Synthetic F01 mode control",
        ),
        defaults=_defaults(),
        beam_request_basis=ETABSBeamRequestBasisV1(
            stirrup_diameter_mm=8, tension_bar_diameter_mm=20
        ),
    )


@pytest.mark.parametrize("precomputed", [False, True], ids=["raw", "precomputed"])
def test_supported_force_formats_retain_actions_and_provenance(
    tmp_path: Path, precomputed: bool
) -> None:
    header = "Output Case,Station," + (
        "Mu_max_kNm,Vu_max_kN" if precomputed else "M3,V2"
    )
    geometry, forces, model = _files(tmp_path, header, "ULS-1,2,-120,-75")
    result = parse_dual_csv_lossless(
        geometry, forces, format_hint="etabs", defaults=_defaults()
    )
    assert result.status is ImportStatus.ACCEPTED
    assert result.issues == ()
    assert result.batch is not None
    (force,) = result.batch.forces
    assert ETABSAdapter().load_forces(forces) == [force]
    assert (force.mu_knm, force.vu_kn) == (120, 75)
    assert (force.moment_signed_knm, force.shear_signed_kn) == (-120, -75)
    assert force.load_case == ("Envelope" if precomputed else "ULS-1")
    assert (force.moment_station, force.shear_station) == (
        (None, None) if precomputed else (2, 2)
    )
    assert force.envelope_basis == (
        "source_precomputed_extrema_provenance_unavailable"
        if precomputed
        else "independent_absolute_extrema_with_concurrent_values"
    )
    assert (force.shear_at_moment_station_kn, force.moment_at_shear_station_knm) == (
        (None, None) if precomputed else (-75, -120)
    )
    snapshot = _snapshot(geometry, forces, model, precomputed=precomputed)
    assert snapshot.status is ETABSSnapshotStatus.ACCEPTED
    assert not snapshot.issues and not snapshot.ambiguities
    (request,) = snapshot.beam_requests
    assert (request.mu_knm, request.vu_kn) == (120, 75)
    assert request.source_metadata["result_identity"]["kind"] == (
        "SOURCE_ENVELOPE" if precomputed else "LOAD_COMBINATION"
    )


@pytest.mark.parametrize(
    ("header", "values"),
    [
        ("Output Case,Station,M3,V2,Mu_max_kNm", "ULS-1,2,-120,-75,120"),
        ("Output Case,Station,M3,V2,Vu_max_kN", "ULS-1,2,-120,-75,75"),
        ("Output Case,Station,M3,V2,Mu_min_kNm", "ULS-1,2,-120,-75,-120"),
        ("Output Case,Station,M3,Vu_max_kN", "ULS-1,2,-120,75"),
        ("Output Case,Station,Moment,Shear,MuMax", "ULS-1,2,-120,-75,120"),
    ],
    ids=[
        "F01-missing-envelope-shear",
        "shear-extremum",
        "minimum",
        "partial",
        "aliases",
    ],
)
def test_mixed_force_formats_block_every_row_before_batch_or_request(
    tmp_path: Path, header: str, values: str
) -> None:
    geometry, forces, model = _files(tmp_path, header, values, rows=2)
    with pytest.raises(ValueError, match="Conflicting ETABS force formats"):
        ETABSAdapter().load_forces(forces)
    result = parse_dual_csv_lossless(
        geometry, forces, format_hint="etabs", defaults=_defaults()
    )
    assert result.status is ImportStatus.BLOCKED
    assert result.batch is None
    assert result.ledger.totals.source_rows == 3
    force_rows = [row for row in result.ledger.rows if row.artifact_role == "forces"]
    assert [row.source_row_number for row in force_rows] == [2, 3]
    assert all(row.status is ImportStatus.BLOCKED for row in force_rows)
    assert all(
        ImportIssueCode.CONFLICTING_HEADER in row.issue_codes for row in force_rows
    )
    assert {issue.code for issue in result.issues} == {
        ImportIssueCode.CONFLICTING_HEADER
    }
    issue = next(issue for issue in result.issues if issue.path == "forces.headers")
    assert issue.code is ImportIssueCode.CONFLICTING_HEADER
    assert "Conflicting ETABS force formats" in issue.message
    assert all(name in issue.message for name in header.split(","))
    if "V2" in header:
        assert all(
            next(
                field for field in row.fields if field.canonical_field == "v2"
            ).raw_value
            == "-75"
            for row in force_rows
        )
    snapshot = _snapshot(geometry, forces, model)
    assert snapshot.status is ETABSSnapshotStatus.BLOCKED
    assert snapshot.snapshot is None and snapshot.beam_requests == ()
    assert snapshot.row_accounting.source_rows == 3
    assert snapshot.row_accounting.blocked_rows == 2
    assert "import.conflicting_header" in {issue.code for issue in snapshot.issues}
    assert "etabs.force_export_shape_mixed" in {
        issue.code for issue in snapshot.ambiguities
    }


@pytest.mark.parametrize(
    ("header", "values", "expected"),
    [
        ("Mu_max_kNm", "-120", (120, 0)),
        ("Vu_max_kN", "-75", (0, 75)),
        ("Mu,Vu", "-120,-75", (120, 75)),
    ],
)
def test_direct_precomputed_compatibility_is_preserved(
    tmp_path: Path, header: str, values: str, expected: tuple[float, float]
) -> None:
    _, forces, _ = _files(tmp_path, header, values)
    (force,) = ETABSAdapter().load_forces(forces)
    assert (force.mu_knm, force.vu_kn) == expected
    assert force.load_case == "Envelope"
