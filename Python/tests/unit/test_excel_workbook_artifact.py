"""Static identity and macro-free checks for the tracked E1 workbook."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path
from xml.etree import ElementTree

REPO_ROOT = Path(__file__).resolve().parents[3]
ARTIFACT_DIR = (
    REPO_ROOT
    / "Python"
    / "structural_lib"
    / "data"
    / "excel"
    / "outputs"
    / "e1-excel-routine-workbench"
)
WORKBOOK = ARTIFACT_DIR / "structural-lib-rectangular-beam-workbench-v1.xlsx"
MANIFEST = ARTIFACT_DIR / "workbook-manifest.json"

EXPECTED_SHEETS = [
    "Workbook_Info",
    "Beam_Workbench",
    "Mapping_Preview",
    "Row_Ledger",
    "Results",
    "Passports",
]
EXPECTED_INPUT_HEADERS = [
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


def _xml(archive: zipfile.ZipFile, name: str) -> ElementTree.Element:
    return ElementTree.fromstring(archive.read(name))


def test_tracked_workbook_matches_frozen_artifact_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    payload = WORKBOOK.read_bytes()

    assert manifest["schema_version"] == "excel-workbook-artifact-manifest/v1"
    assert manifest["artifact"] == str(WORKBOOK.relative_to(REPO_ROOT))
    assert manifest["artifact_size_bytes"] == len(payload)
    assert manifest["artifact_sha256"] == hashlib.sha256(payload).hexdigest()
    assert manifest["installed_windows_excel_evidence"] == "TO_VERIFY_WINDOWS"


def test_workbook_has_exact_sheets_tables_headers_and_no_structural_formulas() -> None:
    main_ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    with zipfile.ZipFile(WORKBOOK) as archive:
        names = set(archive.namelist())
        assert not any("vbaProject" in name or "macrosheet" in name for name in names)

        book = _xml(archive, "xl/workbook.xml")
        sheets = book.find(f"{{{main_ns}}}sheets")
        assert sheets is not None
        assert [item.attrib["name"] for item in sheets] == EXPECTED_SHEETS

        table_files = sorted(
            name for name in names if name.startswith("xl/tables/table")
        )
        tables = [_xml(archive, name) for name in table_files]
        assert {table.attrib["name"] for table in tables} == {
            "tbl_Beam_Workbench_V1",
            "tbl_Mapping_Preview_V1",
            "tbl_Row_Ledger_V1",
            "tbl_Results_V1",
            "tbl_Passports_V1",
        }
        input_table = next(
            table for table in tables if table.attrib["name"] == "tbl_Beam_Workbench_V1"
        )
        assert input_table.attrib["ref"] == "A4:Q7"
        columns = input_table.find(f"{{{main_ns}}}tableColumns")
        assert columns is not None
        assert [item.attrib["name"] for item in columns] == EXPECTED_INPUT_HEADERS

        worksheet_xml = [
            archive.read(name)
            for name in names
            if name.startswith("xl/worksheets/sheet") and name.endswith(".xml")
        ]
        assert all(b"<f" not in payload for payload in worksheet_xml)
        assert all(
            marker not in payload
            for payload in worksheet_xml
            for marker in (b"#REF!", b"#DIV/0!", b"#VALUE!", b"#NAME?", b"#N/A")
        )
        assert b"dataValidations" in archive.read("xl/worksheets/sheet2.xml")

        all_xml = b"\n".join(
            archive.read(name) for name in names if name.endswith(".xml")
        )
        assert b"structural-lib-rectangular-beam-workbench" in all_xml
        assert b"MACRO_FREE_OFFICE_JS" in all_xml
        assert b"TO_VERIFY_WINDOWS" in all_xml
