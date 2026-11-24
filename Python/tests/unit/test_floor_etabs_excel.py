"""Literal worksheet projection fidelity for a native ETABS table."""

import csv
import io
from pathlib import Path

import pytest

from structural_lib.services.floor_etabs_excel import project_etabs_worksheet_v1

SHEET = "Element Forces - Beams"
REFERENCE_CSV = """TABLE:  Element Forces - Beams
Story,Beam,Unique Name,Output Case,Case Type,Step Type,Station,P,V2,V3,T,M2,M3,Element,Elem Station
,,,,,,m,kN,kN,kN,kN-m,kN-m,kN-m,,m

L2,B1,00101,U1,Combination,,1.25,0,-32.5,0,-2.25,0,18.75,00101,1.25
"""


def _workbook(path: Path, *, invalid: str | None = None) -> None:
    openpyxl = pytest.importorskip("openpyxl")
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = SHEET
    for row in csv.reader(io.StringIO(REFERENCE_CSV)):
        if row and row[0] == "L2":
            row[6] = 1.25
            row[8] = -32.5
        sheet.append(row)
    if invalid:
        sheet["F5"] = invalid
    workbook.save(path)


def test_projects_native_table_cells_and_preserves_worksheet_rows(
    tmp_path: Path,
) -> None:
    workbook = tmp_path / "element-forces.xlsx"
    _workbook(workbook)
    projected = project_etabs_worksheet_v1(workbook, worksheet=SHEET)
    assert projected.decode("utf-8") == REFERENCE_CSV


@pytest.mark.parametrize(
    "value, message",
    (
        ("=1+1", "Formula cells"),
        ("#DIV/0!", "Error cells"),
        ("multi\nline", "Unsupported ETABS cell"),
    ),
)
def test_rejects_non_literal_or_unusable_cells(
    tmp_path: Path, value: str, message: str
) -> None:
    workbook = tmp_path / "invalid.xlsx"
    _workbook(workbook, invalid=value)
    with pytest.raises(ValueError, match=message + ".*F5"):
        project_etabs_worksheet_v1(workbook, worksheet=SHEET)


def test_rejects_unknown_worksheet_and_non_xlsx(tmp_path: Path) -> None:
    workbook = tmp_path / "table.xlsx"
    _workbook(workbook)
    with pytest.raises(ValueError, match="was not found"):
        project_etabs_worksheet_v1(workbook, worksheet="Wrong table")
    with pytest.raises(ValueError, match="Only .xlsx"):
        project_etabs_worksheet_v1(tmp_path / "table.csv", worksheet="Wrong table")
