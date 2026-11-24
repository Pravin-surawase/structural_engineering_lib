# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Prepared-floor v1 adapters retain strict CLI input behavior."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from structural_lib.services.cli_design import CLIDesignBlockedError
from structural_lib.services.floor_prepared import (
    PREPARED_WORKSHEET_HEADERS,
    load_prepared_floor_v1,
)

EXAMPLES = Path(__file__).resolve().parents[2] / "examples" / "floor_review"


def _canonical_records(intake):
    return [
        (
            record.beam_id,
            record.story,
            record.b,
            record.D,
            record.d,
            record.span,
            record.cover,
            record.fck,
            record.fy,
            record.Mu,
            record.Vu,
            record.stirrup_dia,
            record.stirrup_spacing,
        )
        for record in intake.records
    ]


def test_csv_and_json_templates_produce_equivalent_prepared_records():
    csv_intake = load_prepared_floor_v1(EXAMPLES / "prepared.csv", source_format="csv")
    json_intake = load_prepared_floor_v1(
        EXAMPLES / "prepared.json", source_format="json"
    )

    assert _canonical_records(csv_intake) == _canonical_records(json_intake)
    assert [record.Mu for record in csv_intake.records] == [-180.0, 145.0]
    assert [record.Vu for record in csv_intake.records] == [120.0, -95.0]


def test_xlsx_template_is_equivalent_and_retains_file_and_excel_row_provenance():
    pytest.importorskip("openpyxl")
    xlsx_path = EXAMPLES / "prepared.xlsx"
    csv_intake = load_prepared_floor_v1(EXAMPLES / "prepared.csv", source_format="csv")
    xlsx_intake = load_prepared_floor_v1(xlsx_path, source_format="xlsx")

    assert _canonical_records(xlsx_intake) == _canonical_records(csv_intake)
    assert (
        xlsx_intake.source_sha256 == hashlib.sha256(xlsx_path.read_bytes()).hexdigest()
    )
    assert xlsx_intake.records[0].project_payload["source_metadata"] == {
        "input_artifact_sha256": xlsx_intake.source_sha256,
        "source_row_number": 2,
        "source_format": "xlsx",
        "worksheet": "Beams",
        "worksheet_row_number": 2,
    }


@pytest.mark.parametrize(
    ("mutation", "expected_code"),
    [
        ("formula", "PREPARED_FLOOR_FORMULA_NOT_ALLOWED"),
        ("error", "PREPARED_FLOOR_UNUSABLE_CELL"),
        ("shape", "PREPARED_FLOOR_WORKSHEET_HEADERS"),
    ],
)
def test_xlsx_rejects_formula_errors_and_unsupported_office_sheet_shapes(
    tmp_path, mutation, expected_code
):
    openpyxl = pytest.importorskip("openpyxl")
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Beams"
    sheet.append(PREPARED_WORKSHEET_HEADERS)
    sheet.append(
        ["B-101", "Level 01", 300, 500, 20, 6000, 40, 25, 500, -180, 120, 8, 150]
    )
    if mutation == "formula":
        sheet["J2"] = "=0-180"
    elif mutation == "error":
        sheet["J2"] = "#VALUE!"
        sheet["J2"].data_type = "e"
    else:
        sheet["A1"] = "Office Beam"
    path = tmp_path / "prepared.xlsx"
    workbook.save(path)

    with pytest.raises(CLIDesignBlockedError) as error:
        load_prepared_floor_v1(path, source_format="xlsx")

    assert expected_code in {issue.code for issue in error.value.issues}


def test_source_format_must_match_a_supported_file_extension():
    with pytest.raises(CLIDesignBlockedError) as error:
        load_prepared_floor_v1(EXAMPLES / "prepared.csv", source_format="xlsx")

    assert error.value.issues[0].code == "PREPARED_FLOOR_EXTENSION_MISMATCH"


def test_prepared_malformed_workbook_returns_source_issue(tmp_path: Path) -> None:
    pytest.importorskip("openpyxl")
    path = tmp_path / "corrupt.xlsx"
    path.write_bytes(b"Not an Excel workbook")
    with pytest.raises(CLIDesignBlockedError) as caught:
        load_prepared_floor_v1(path, source_format="xlsx")
    assert caught.value.issues[0].code == "PREPARED_FLOOR_INVALID_WORKBOOK"
