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


@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize(
    ("stations", "second_actions", "kind"),
    [
        (("2", "2"), "-120,-75", "Duplicate"),
        (("2", "2.0"), "-120,-75", "Duplicate"),
        (("2", "2.0"), "-40,-150", "Ambiguous"),
        (("2", "2e0"), "-40,-150", "Ambiguous"),
    ],
)
def test_station_collisions_block_before_reduction_and_preserve_rows(
    tmp_path: Path, monkeypatch, reverse: bool, stations, second_actions: str, kind: str
) -> None:
    geometry, forces, model = _files(tmp_path, "M3,V2", "-120,-75")
    with geometry.open("a", encoding="utf-8") as output:
        output.write("L1,B2,202,Beam,B300X500,5,0,0,10,0,0\n")
    samples = [(stations[0], "-120,-75"), (stations[1], second_actions)]
    if reverse:
        samples.reverse()
    forces.write_text(
        "Story,Label,UniqueName,Output Case,Station,M3,V2\n"
        + "".join(
            f"L1,B1,101,ULS-1,{station},{actions}\n" for station, actions in samples
        )
        + "L1,B2,202,ULS-1,2,-10,-5\n",
        encoding="utf-8",
    )

    def unexpected_reduction(*args, **kwargs):
        raise AssertionError("Station collision reached force reduction")

    monkeypatch.setattr(ETABSAdapter, "load_forces", unexpected_reduction)
    result = parse_dual_csv_lossless(
        geometry, forces, format_hint="etabs", defaults=_defaults()
    )
    assert result.status is ImportStatus.BLOCKED and result.batch is None
    assert result.ledger.totals.source_rows == 5
    force_rows = [row for row in result.ledger.rows if row.artifact_role == "forces"]
    assert len(force_rows) == 3
    for row, (station, actions) in zip(force_rows[:2], samples, strict=True):
        assert row.status is ImportStatus.BLOCKED
        assert row.issue_codes == (ImportIssueCode.DUPLICATE_RECORD_ID,)
        assert row.source_record_id == f"B1_L1:ULS-1:{station}"
        fields = {field.canonical_field: field for field in row.fields}
        assert fields["station"].raw_value == station
        assert fields["station"].parsed_value == 2
        assert (fields["m3"].raw_value, fields["v2"].raw_value) == tuple(
            actions.split(",")
        )
    assert force_rows[2].status is ImportStatus.ACCEPTED
    assert len(result.issues) == 2
    assert all(
        issue.message.startswith(kind + " ETABS force rows") for issue in result.issues
    )
    assert {issue.source_row_number for issue in result.issues} == {2, 3}
    snapshot = _snapshot(geometry, forces, model)
    assert snapshot.status is ETABSSnapshotStatus.BLOCKED
    assert snapshot.snapshot is None and not snapshot.beam_requests
    assert snapshot.row_accounting.source_rows == 5
    assert snapshot.row_accounting.blocked_rows == 2


@pytest.mark.parametrize("nearby", ["2.000001", "2.0000000000000004"])
def test_distinct_numeric_stations_keep_governing_signed_companions(
    tmp_path: Path, nearby: str
) -> None:
    geometry, forces, model = _files(tmp_path, "M3,V2", "-120,-75")
    forces.write_text(
        "Story,Label,UniqueName,Output Case,Station,M3,V2\n"
        "L1,B1,101,ULS-1,2,-120,-75\n"
        f"L1,B1,101,ULS-1,{nearby},-40,-150\n",
        encoding="utf-8",
    )
    result = parse_dual_csv_lossless(
        geometry, forces, format_hint="etabs", defaults=_defaults()
    )
    assert result.status is ImportStatus.ACCEPTED and result.batch is not None
    assert not result.issues
    (force,) = result.batch.forces
    assert force.station_count == 2
    assert (force.mu_knm, force.vu_kn) == (120, 150)
    assert (force.moment_station, force.shear_at_moment_station_kn) == (2, -75)
    assert (force.shear_station, force.moment_at_shear_station_knm) == (
        float(nearby),
        -40,
    )
    snapshot = _snapshot(geometry, forces, model)
    assert snapshot.status is ETABSSnapshotStatus.ACCEPTED
    (request,) = snapshot.beam_requests
    assert (request.mu_knm, request.vu_kn) == (120, 150)


def test_station_identity_keeps_exact_cases_distinct(tmp_path: Path) -> None:
    geometry, forces, _ = _files(tmp_path, "M3,V2", "-120,-75")
    forces.write_text(
        "Story,Label,UniqueName,Output Case,Station,M3,V2\n"
        "L1,B1,101,ULS-A,2,-120,-75\n"
        "L1,B1,101,uls-a,2.0,-40,-150\n",
        encoding="utf-8",
    )
    result = parse_dual_csv_lossless(
        geometry, forces, format_hint="etabs", defaults=_defaults()
    )
    assert all(row.status is ImportStatus.ACCEPTED for row in result.ledger.rows)
    # The existing member-only batch still refuses two envelopes for one member.
    assert result.status is ImportStatus.BLOCKED and result.batch is None
    assert {issue.path for issue in result.issues} == {"adapter.output"}


@pytest.mark.parametrize("station", ["NaN", "inf", "not-a-station"])
def test_invalid_station_is_refused_with_original_token(
    tmp_path: Path, station: str
) -> None:
    geometry, forces, model = _files(
        tmp_path, "Output Case,Station,M3,V2", f"ULS-1,{station},-120,-75"
    )
    result = parse_dual_csv_lossless(
        geometry, forces, format_hint="etabs", defaults=_defaults()
    )
    assert result.status is ImportStatus.BLOCKED and result.batch is None
    row = result.ledger.rows[-1]
    field = next(field for field in row.fields if field.canonical_field == "station")
    assert field.raw_value == station and field.parsed_value is None
    assert row.issue_codes == (
        (
            ImportIssueCode.MALFORMED_NUMBER
            if station == "not-a-station"
            else ImportIssueCode.NON_FINITE_NUMBER
        ),
    )
    snapshot = _snapshot(geometry, forces, model)
    assert snapshot.status is ETABSSnapshotStatus.BLOCKED and not snapshot.beam_requests


@pytest.mark.parametrize("force_unique", [None, "101", "202"])
def test_joined_member_alias_cannot_bind_another_label_story(
    tmp_path: Path, force_unique: str | None
) -> None:
    geometry, forces, model = _files(tmp_path, "M3,V2", "-120,-75")
    geometry.write_text(
        "Story,Label,UniqueName,ObjType,AnalSect,XI,YI,ZI,XJ,YJ,ZJ\n"
        "C,A_B,101,Beam,B300X500,0,0,0,5,0,0\n",
        encoding="utf-8",
    )
    forces.write_text(
        "Story,Label,"
        + ("UniqueName," if force_unique else "")
        + "Output Case,Station,M3,V2\nB_C,A,"
        + (force_unique + "," if force_unique else "")
        + "ULS-1,2,-120,-75\n",
        encoding="utf-8",
    )
    result = parse_dual_csv_lossless(
        geometry, forces, format_hint="etabs", defaults=_defaults()
    )
    assert result.status is ImportStatus.BLOCKED and result.batch is None
    (issue,) = result.issues
    assert issue.code is ImportIssueCode.SOURCE_ID_MISMATCH
    assert issue.path.endswith("unique_name" if force_unique == "202" else "beam_id")
    assert result.ledger.rows[-1].source_record_id == "A_B_C:ULS-1:2"
    snapshot = _snapshot(geometry, forces, model)
    assert snapshot.status is ETABSSnapshotStatus.BLOCKED
    assert snapshot.snapshot is None and not snapshot.beam_requests


@pytest.mark.parametrize(("label", "story"), [("A_B", "C"), ("A", "B_C")])
def test_matching_underscore_member_keeps_legacy_public_id(
    tmp_path: Path, label: str, story: str
) -> None:
    geometry, forces, model = _files(
        tmp_path, "Output Case,Station,M3,V2", "ULS-1,2,-120,-75"
    )
    geometry.write_text(
        geometry.read_text(encoding="utf-8").replace("L1,B1", f"{story},{label}"),
        encoding="utf-8",
    )
    forces.write_text(
        forces.read_text(encoding="utf-8").replace("L1,B1", f"{story},{label}"),
        encoding="utf-8",
    )
    result = parse_dual_csv_lossless(
        geometry, forces, format_hint="etabs", defaults=_defaults()
    )
    assert result.status is ImportStatus.ACCEPTED and result.batch is not None
    assert result.batch.beams[0].id == result.batch.forces[0].id == "A_B_C"
    assert _snapshot(geometry, forces, model).status is ETABSSnapshotStatus.ACCEPTED
