# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for structural_lib.imports helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from structural_lib.core.models import DesignDefaults
from structural_lib.services.import_ledger import (
    ImportFieldAction,
    ImportIssueCode,
    ImportStatus,
)
from structural_lib.services.imports import (
    LosslessImportBlockedError,
    parse_dual_csv,
    parse_dual_csv_lossless,
    parse_single_csv_lossless,
    validate_import,
)


def _write_csv(path: Path, text: str) -> None:
    path.write_text(text.strip() + "\n", encoding="utf-8")


def test_parse_dual_csv_generic(tmp_path: Path) -> None:
    geometry_csv = tmp_path / "geometry.csv"
    forces_csv = tmp_path / "forces.csv"

    _write_csv(
        geometry_csv,
        """
BeamID,b (mm),D (mm),Span (mm),fck,fy,Cover (mm)
B1,300,500,5000,25,500,40
B2,300,450,4500,25,500,40
""",
    )

    _write_csv(
        forces_csv,
        """
BeamID,Mu (kN-m),Vu (kN),Load Case
B1,150,80,1.5(DL+LL)
B2,120,60,1.5(DL+LL)
""",
    )

    batch, warnings = parse_dual_csv(geometry_csv, forces_csv, format_hint="generic")

    assert len(batch.beams) == 2
    assert len(batch.forces) == 2
    assert warnings.warnings == []

    report = validate_import(batch)
    assert report.ok is True
    assert report.details.get("matched") == 2


def test_single_csv_lossless_accounts_each_physical_row_once(tmp_path: Path) -> None:
    combined = tmp_path / "combined.csv"
    _write_csv(
        combined,
        (
            "BeamID,b (mm),D (mm),Span (mm),fck,fy,Cover (mm),"
            "Mu (kN-m),Vu (kN),Notes\n"
            "B1,300,500,5000,25,500,40,150,80,primary\n"
            "B2,300,450,4500,25,500,40,120,60,secondary"
        ),
    )

    result = parse_single_csv_lossless(combined, format_hint="generic")

    assert result.status is ImportStatus.ACCEPTED
    assert result.batch is not None
    assert (
        result.ledger.geometry_artifact.sha256 == result.ledger.forces_artifact.sha256
    )
    assert result.ledger.totals.source_rows == 2
    assert result.ledger.totals.accepted_rows == 2
    assert len(result.ledger.rows) == 2
    assert all(row.artifact_role == "combined" for row in result.ledger.rows)


def test_single_csv_lossless_blocks_malformed_action_without_zero(
    tmp_path: Path,
) -> None:
    combined = tmp_path / "combined.csv"
    _write_csv(
        combined,
        (
            "BeamID,b (mm),D (mm),fck,fy,Cover (mm),Mu (kN-m),Vu (kN)\n"
            "B1,300,500,25,500,40,not-a-number,80"
        ),
    )

    result = parse_single_csv_lossless(combined, format_hint="generic")

    assert result.status is ImportStatus.BLOCKED
    assert result.batch is None
    assert result.ledger.totals.source_rows == 1
    assert result.ledger.totals.blocked_rows == 1
    assert ImportIssueCode.MALFORMED_NUMBER in {issue.code for issue in result.issues}


def test_parse_dual_csv_unmatched_warns(tmp_path: Path) -> None:
    geometry_csv = tmp_path / "geometry.csv"
    forces_csv = tmp_path / "forces.csv"

    _write_csv(
        geometry_csv,
        """
BeamID,b (mm),D (mm),Span (mm),fck,fy,Cover (mm)
B1,300,500,5000,25,500,40
B2,300,450,4500,25,500,40
""",
    )

    _write_csv(
        forces_csv,
        """
BeamID,Mu (kN-m),Vu (kN)
B1,150,80
""",
    )

    result = parse_dual_csv_lossless(geometry_csv, forces_csv, format_hint="generic")

    assert result.status is ImportStatus.BLOCKED
    assert result.batch is None
    assert result.ledger.totals.unmatched_geometry == 1
    assert ImportIssueCode.UNMATCHED_GEOMETRY in {issue.code for issue in result.issues}

    with pytest.raises(LosslessImportBlockedError):
        parse_dual_csv(geometry_csv, forces_csv, format_hint="generic")


def test_lossless_import_accounts_every_row_and_field(tmp_path: Path) -> None:
    geometry_csv = tmp_path / "geometry.csv"
    forces_csv = tmp_path / "forces.csv"
    _write_csv(
        geometry_csv,
        """
BeamID,b (mm),D (mm),Span (mm),fck,fy,Cover (mm),Notes
B1,300,500,5000,25,500,40,primary
B2,300,450,4500,25,500,40,secondary
""",
    )
    _write_csv(
        forces_csv,
        """
BeamID,Mu (kN-m),Vu (kN),Load Case
B1,150,80,1.5(DL+LL)
B2,120,60,1.5(DL+LL)
""",
    )

    result = parse_dual_csv_lossless(geometry_csv, forces_csv, format_hint="generic")

    assert result.status is ImportStatus.ACCEPTED
    assert result.batch is not None
    assert result.ledger.totals.source_rows == 4
    assert result.ledger.totals.accepted_rows == 4
    assert result.ledger.totals.blocked_rows == 0
    assert all(len(row.fields) > 0 for row in result.ledger.rows)
    notes = [
        field
        for row in result.ledger.rows
        for field in row.fields
        if field.raw_header == "Notes"
    ]
    assert notes and notes[0].action is ImportFieldAction.METADATA_ONLY


@pytest.mark.parametrize("bad_value", ["not-a-number", "NaN", "inf", "-inf"])
def test_malformed_or_non_finite_force_blocks_without_zero_substitution(
    tmp_path: Path, bad_value: str
) -> None:
    geometry_csv = tmp_path / "geometry.csv"
    forces_csv = tmp_path / "forces.csv"
    _write_csv(
        geometry_csv,
        "BeamID,b (mm),D (mm),fck,fy,Cover (mm)\nB1,300,500,25,500,40",
    )
    _write_csv(
        forces_csv,
        f"BeamID,Mu (kN-m),Vu (kN)\nB1,{bad_value},80",
    )

    result = parse_dual_csv_lossless(geometry_csv, forces_csv, format_hint="generic")

    assert result.status is ImportStatus.BLOCKED
    assert result.batch is None
    assert result.ledger.totals.source_rows == 2
    assert result.ledger.totals.accepted_rows == 1
    assert result.ledger.totals.blocked_rows == 1
    expected = (
        ImportIssueCode.MALFORMED_NUMBER
        if bad_value == "not-a-number"
        else ImportIssueCode.NON_FINITE_NUMBER
    )
    assert expected in {issue.code for issue in result.issues}


def test_unknown_calculation_header_blocks_but_reports_field(tmp_path: Path) -> None:
    geometry_csv = tmp_path / "geometry.csv"
    forces_csv = tmp_path / "forces.csv"
    _write_csv(
        geometry_csv,
        (
            "BeamID,b (mm),D (mm),fck,fy,Cover (mm),Mystery Depth\n"
            "B1,300,500,25,500,40,450"
        ),
    )
    _write_csv(
        forces_csv,
        "BeamID,Mu (kN-m),Vu (kN)\nB1,150,80",
    )

    result = parse_dual_csv_lossless(geometry_csv, forces_csv, format_hint="generic")

    assert result.status is ImportStatus.BLOCKED
    assert ImportIssueCode.UNKNOWN_CALCULATION_HEADER in {
        issue.code for issue in result.issues
    }
    mystery = next(
        field
        for row in result.ledger.rows
        for field in row.fields
        if field.raw_header == "Mystery Depth"
    )
    assert mystery.action is ImportFieldAction.REJECTED


def test_duplicate_member_identity_blocks_every_duplicate(tmp_path: Path) -> None:
    geometry_csv = tmp_path / "geometry.csv"
    forces_csv = tmp_path / "forces.csv"
    _write_csv(
        geometry_csv,
        (
            "BeamID,b (mm),D (mm),fck,fy,Cover (mm)\n"
            "B1,300,500,25,500,40\nB1,350,550,25,500,40"
        ),
    )
    _write_csv(
        forces_csv,
        "BeamID,Mu (kN-m),Vu (kN)\nB1,150,80",
    )

    result = parse_dual_csv_lossless(geometry_csv, forces_csv, format_hint="generic")

    duplicate_rows = [
        row
        for row in result.ledger.rows
        if ImportIssueCode.DUPLICATE_RECORD_ID in row.issue_codes
    ]
    assert result.status is ImportStatus.BLOCKED
    assert len(duplicate_rows) == 2
    assert all(row.status is ImportStatus.BLOCKED for row in duplicate_rows)


def test_auto_detection_blocks_when_multiple_adapters_match(tmp_path: Path) -> None:
    geometry_csv = tmp_path / "geometry.csv"
    forces_csv = tmp_path / "forces.csv"
    combined = "Story,Label,b (mm),D (mm),Mu (kN-m),Vu (kN)\nL1,B1,300,500,150,80"
    _write_csv(geometry_csv, combined)
    _write_csv(forces_csv, combined)

    result = parse_dual_csv_lossless(geometry_csv, forces_csv, format_hint="auto")

    assert result.status is ImportStatus.BLOCKED
    assert result.batch is None
    assert len(result.ledger.adapter_selection.candidates) > 1
    assert ImportIssueCode.AMBIGUOUS_FORMAT in {issue.code for issue in result.issues}


@pytest.mark.parametrize(
    ("format_hint", "geometry", "forces"),
    [
        (
            "safe",
            (
                "Strip,Story,StartX,StartY,EndX,EndY,Width,Depth,fck,fy\n"
                "S1,Slab,0,0,5,0,1000,200,30,500"
            ),
            ("Strip,Story,LoadCombo,Position,M22,V23\nS1,Slab,1.5DL+1.5LL,0,120,80"),
        ),
        (
            "staad",
            ("Member,X1,Y1,X2,Y2,Width,Depth,fck,fy\nB1,0,0,5,0,300,500,30,500"),
            "Member,LC,Dist,My,Fy\nB1,101,0,120,80",
        ),
    ],
)
def test_explicit_safe_and_staad_adapters_remain_lossless(
    tmp_path: Path,
    format_hint: str,
    geometry: str,
    forces: str,
) -> None:
    geometry_csv = tmp_path / "geometry.csv"
    forces_csv = tmp_path / "forces.csv"
    _write_csv(geometry_csv, geometry)
    _write_csv(forces_csv, forces)

    result = parse_dual_csv_lossless(
        geometry_csv,
        forces_csv,
        format_hint=format_hint,
        defaults=DesignDefaults(fck_mpa=30, fy_mpa=500, cover_mm=40),
    )

    assert result.status is ImportStatus.ACCEPTED
    assert result.batch is not None
    assert result.ledger.adapter_selection.reason == "explicit"
    assert result.ledger.totals.source_rows == 2
    assert result.ledger.totals.accepted_rows == 2
    assert result.ledger.totals.matched_records == 1


def test_non_generic_adapter_blocks_without_explicit_project_defaults(
    tmp_path: Path,
) -> None:
    geometry_csv = tmp_path / "geometry.csv"
    forces_csv = tmp_path / "forces.csv"
    _write_csv(
        geometry_csv,
        (
            "Strip,Story,StartX,StartY,EndX,EndY,Width,Depth,fck,fy\n"
            "S1,Slab,0,0,5,0,1000,200,30,500"
        ),
    )
    _write_csv(
        forces_csv,
        "Strip,Story,LoadCombo,Position,M22,V23\nS1,Slab,1.5DL+1.5LL,0,120,80",
    )

    result = parse_dual_csv_lossless(geometry_csv, forces_csv, format_hint="safe")

    assert result.status is ImportStatus.BLOCKED
    assert result.batch is None
    assert ImportIssueCode.MISSING_PROJECT_DEFAULTS in {
        issue.code for issue in result.issues
    }


def test_etabs_lossless_import_ledgers_malformed_force_without_substitution(
    tmp_path: Path,
) -> None:
    geometry_csv = tmp_path / "geometry.csv"
    forces_csv = tmp_path / "forces.csv"
    _write_csv(
        geometry_csv,
        (
            "Story,Label,ObjType,AnalSect,XI,YI,ZI,XJ,YJ,ZJ\n"
            "Ground,B1,Beam,B300X500,0,0,0,5,0,0"
        ),
    )
    _write_csv(
        forces_csv,
        ("Story,Label,Output Case,Station,M3,V2\nGround,B1,ULS,0,not-a-number,50"),
    )

    result = parse_dual_csv_lossless(
        geometry_csv,
        forces_csv,
        format_hint="etabs",
        defaults=DesignDefaults(fck_mpa=25, fy_mpa=500, cover_mm=40),
    )

    assert result.status is ImportStatus.BLOCKED
    assert result.batch is None
    assert result.ledger.totals.source_rows == 2
    assert result.ledger.totals.accepted_rows == 1
    assert result.ledger.totals.blocked_rows == 1
    assert ImportIssueCode.MALFORMED_NUMBER in {issue.code for issue in result.issues}


def test_etabs_lossless_import_blocks_unknown_section_dimensions(
    tmp_path: Path,
) -> None:
    geometry_csv = tmp_path / "geometry.csv"
    forces_csv = tmp_path / "forces.csv"
    _write_csv(
        geometry_csv,
        (
            "Story,Label,ObjType,AnalSect,XI,YI,ZI,XJ,YJ,ZJ\n"
            "Ground,B1,Beam,UNKNOWN_SECTION,0,0,0,5,0,0"
        ),
    )
    _write_csv(
        forces_csv,
        "Story,Label,Output Case,Station,M3,V2\nGround,B1,ULS,0,120,50",
    )

    result = parse_dual_csv_lossless(
        geometry_csv,
        forces_csv,
        format_hint="etabs",
        defaults=DesignDefaults(fck_mpa=25, fy_mpa=500, cover_mm=40),
    )

    assert result.status is ImportStatus.BLOCKED
    assert result.batch is None
    assert ImportIssueCode.ADAPTER_PARSE_ERROR in {
        issue.code for issue in result.issues
    }


def test_etabs_lossless_ledger_requires_case_station_and_section_identity(
    tmp_path: Path,
) -> None:
    geometry_csv = tmp_path / "geometry.csv"
    forces_csv = tmp_path / "forces.csv"
    _write_csv(
        geometry_csv,
        "Story,Label,XI,YI,ZI,XJ,YJ,ZJ\nGround,B1,0,0,0,5,0,0",
    )
    _write_csv(
        forces_csv,
        "Story,Label,M3,V2\nGround,B1,120,50",
    )

    result = parse_dual_csv_lossless(
        geometry_csv,
        forces_csv,
        format_hint="etabs",
        defaults=DesignDefaults(fck_mpa=25, fy_mpa=500, cover_mm=40),
    )

    assert result.status is ImportStatus.BLOCKED
    missing_paths = {
        issue.path
        for issue in result.issues
        if issue.code is ImportIssueCode.MISSING_REQUIRED_HEADER
    }
    assert "geometry.headers.section_name" in missing_paths
    assert "forces.headers.case_id" in missing_paths
    assert "forces.headers.station" in missing_paths
