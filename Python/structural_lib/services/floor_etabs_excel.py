# SPDX-License-Identifier: MIT
"""Project one explicitly named literal .xlsx worksheet onto the CSV intake."""

from __future__ import annotations

import csv
import io
import math
from pathlib import Path
from zipfile import BadZipFile


def project_etabs_worksheet_v1(path: Path, *, worksheet: str) -> bytes:
    """Preserve literal cell values and physical worksheet lines as UTF-8 CSV."""
    if path.suffix.casefold() != ".xlsx":
        raise ValueError("Only .xlsx workbooks are supported.")
    try:
        from openpyxl import load_workbook
        from openpyxl.utils.exceptions import InvalidFileException
    except ImportError as exc:
        raise ValueError(
            "ETABS workbook intake needs the optional [xlsx] extra."
        ) from exc

    rows: list[list[str]] = []
    try:
        workbook = load_workbook(
            path, read_only=True, data_only=False, keep_links=False
        )
        try:
            if worksheet not in workbook.sheetnames:
                raise ValueError(f"Worksheet {worksheet!r} was not found.")
            sheet = workbook[worksheet]
            sheet.reset_dimensions()
            for row in sheet.iter_rows():
                values: list[str] = []
                for cell in row:
                    if cell.value is None:
                        values.append("")
                        continue
                    if cell.data_type == "f":
                        raise ValueError(
                            f"Formula cells require reviewed literal values: {worksheet}!{cell.coordinate}."
                        )
                    if cell.data_type == "e":
                        raise ValueError(
                            f"Error cells cannot be projected: {worksheet}!{cell.coordinate}."
                        )
                    value = cell.value
                    if (
                        type(value) not in (str, int, float)
                        or isinstance(value, float)
                        and not math.isfinite(value)
                        or isinstance(value, str)
                        and any(char in value for char in "\r\n")
                    ):
                        raise ValueError(
                            f"Unsupported ETABS cell value: {worksheet}!{cell.coordinate}."
                        )
                    values.append(str(value))
                while values and not values[-1]:
                    values.pop()
                rows.append(values)
        finally:
            workbook.close()
    except (BadZipFile, InvalidFileException, KeyError, OSError, SyntaxError) as exc:
        raise ValueError(f"Could not read ETABS workbook {path.name!r}.") from exc

    while rows and not rows[-1]:
        rows.pop()
    if not rows:
        raise ValueError(f"Worksheet {worksheet!r} contains no literal table.")
    width = max(map(len, rows))
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    for index, values in enumerate(rows):
        # Native title records and interior blank lines retain their own shapes.
        if values and not (index == 0 and values[0].startswith("TABLE:")):
            values = values + [""] * (width - len(values))
        writer.writerow(values)
    return output.getvalue().encode("utf-8")
