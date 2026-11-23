# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Prepared-floor v1 adapters for engineer-supplied controlling beam actions.

The prepared profile is intentionally distinct from ETABS snapshot and paired-force
profiles.  It accepts supplied design action pairs only; it does not invent a
source combination or station.
"""

from __future__ import annotations

import hashlib
from io import BytesIO
from pathlib import Path
from typing import Any, Literal
from xml.etree.ElementTree import ParseError
from zipfile import BadZipFile

from . import cli_design

PREPARED_WORKSHEET_NAME = "Beams"
PREPARED_WORKSHEET_HEADERS = (
    "beam_id",
    "story",
    "b_mm",
    "D_mm",
    "tension_bar_diameter_mm",
    "span_mm",
    "cover_mm",
    "fck_nmm2",
    "fy_nmm2",
    "mu_knm",
    "vu_kn",
    "stirrup_diameter_mm",
    "stirrup_spacing_mm",
)

_WORKSHEET_TO_CLI_FIELD = {
    "beam_id": "member_id",
    "story": "story",
    "b_mm": "b_mm",
    "D_mm": "D_mm",
    "tension_bar_diameter_mm": "tension_bar_diameter_mm",
    "span_mm": "span_mm",
    "cover_mm": "clear_cover_mm",
    "fck_nmm2": "fck_nmm2",
    "fy_nmm2": "fy_nmm2",
    "mu_knm": "mu_knm",
    "vu_kn": "vu_kn",
    "stirrup_diameter_mm": "stirrup_diameter_mm",
    "stirrup_spacing_mm": "stirrup_spacing_mm",
}


def _blocked(code: str, path: str, message: str) -> cli_design.CLIDesignBlockedError:
    return cli_design.CLIDesignBlockedError(
        [cli_design.CLIDesignIssueV1(code, path, message)]
    )


def _load_xlsx(path: Path) -> cli_design.CLIDesignIntakeV1:
    try:
        from openpyxl import load_workbook
        from openpyxl.utils.exceptions import InvalidFileException
    except ImportError as exc:  # pragma: no cover - depends on optional install
        raise _blocked(
            "PREPARED_FLOOR_XLSX_DEPENDENCY_MISSING",
            "input",
            "XLSX intake needs the optional dependency: pip install structural-lib-is456[xlsx].",
        ) from exc

    raw = path.read_bytes()
    try:
        workbook = load_workbook(BytesIO(raw), data_only=False, keep_links=False)
    except (
        OSError,
        ValueError,
        KeyError,
        BadZipFile,
        InvalidFileException,
        ParseError,
    ) as exc:
        raise _blocked("PREPARED_FLOOR_INVALID_WORKBOOK", "input", str(exc)) from exc
    if PREPARED_WORKSHEET_NAME not in workbook.sheetnames:
        available = ", ".join(workbook.sheetnames) or "none"
        raise _blocked(
            "PREPARED_FLOOR_WORKSHEET_REQUIRED",
            "workbook",
            f"Expected worksheet {PREPARED_WORKSHEET_NAME!r}; found {available}. Export or map the office sheet to the prepared-floor v1 template.",
        )
    worksheet = workbook[PREPARED_WORKSHEET_NAME]
    actual_headers = tuple(
        worksheet.cell(row=1, column=index).value
        for index in range(1, len(PREPARED_WORKSHEET_HEADERS) + 1)
    )
    extra_headers = [
        worksheet.cell(row=1, column=index).value
        for index in range(
            len(PREPARED_WORKSHEET_HEADERS) + 1, worksheet.max_column + 1
        )
        if worksheet.cell(row=1, column=index).value is not None
    ]
    if actual_headers != PREPARED_WORKSHEET_HEADERS or extra_headers:
        raise _blocked(
            "PREPARED_FLOOR_WORKSHEET_HEADERS",
            f"{PREPARED_WORKSHEET_NAME}!1:1",
            "Expected exact prepared-floor v1 headers: "
            + ", ".join(PREPARED_WORKSHEET_HEADERS)
            + ". Office-specific sheets must be explicitly mapped before intake.",
        )

    issues: list[cli_design.CLIDesignIssueV1] = []
    records: list[cli_design.CLIDesignRecordV1] = []
    source_sha256 = hashlib.sha256(raw).hexdigest()
    source_rows = 0
    for row_number in range(2, worksheet.max_row + 1):
        cells = [
            worksheet.cell(row=row_number, column=column)
            for column in range(1, worksheet.max_column + 1)
        ]
        if all(cell.value is None for cell in cells):
            continue
        source_rows += 1
        if any(
            cell.value is not None for cell in cells[len(PREPARED_WORKSHEET_HEADERS) :]
        ):
            issues.append(
                cli_design.CLIDesignIssueV1(
                    "PREPARED_FLOOR_WORKSHEET_SHAPE",
                    f"{PREPARED_WORKSHEET_NAME}!{row_number}",
                    "Only the declared prepared-floor v1 columns may contain values.",
                )
            )
            continue
        formula_cell = next((cell for cell in cells if cell.data_type == "f"), None)
        if formula_cell is not None:
            issues.append(
                cli_design.CLIDesignIssueV1(
                    "PREPARED_FLOOR_FORMULA_NOT_ALLOWED",
                    f"{PREPARED_WORKSHEET_NAME}!{formula_cell.coordinate}",
                    "Prepared-floor v1 accepts literal cell values only; replace formulas with reviewed literal values.",
                )
            )
            continue
        error_cell = next((cell for cell in cells if cell.data_type == "e"), None)
        if error_cell is not None:
            issues.append(
                cli_design.CLIDesignIssueV1(
                    "PREPARED_FLOOR_UNUSABLE_CELL",
                    f"{PREPARED_WORKSHEET_NAME}!{error_cell.coordinate}",
                    "Excel error cells are not usable prepared-floor inputs.",
                )
            )
            continue
        values: dict[str, Any] = {
            _WORKSHEET_TO_CLI_FIELD[header]: cell.value
            for header, cell in zip(
                PREPARED_WORKSHEET_HEADERS,
                cells[: len(PREPARED_WORKSHEET_HEADERS)],
                strict=True,
            )
        }
        record, record_issues = cli_design._build_record(
            values,
            path=f"{PREPARED_WORKSHEET_NAME}!{row_number}",
            source_sha256=source_sha256,
            source_row_number=row_number,
        )
        issues.extend(record_issues)
        if record is not None:
            metadata = dict(record.project_payload["source_metadata"])
            metadata.update(
                {
                    "source_format": "xlsx",
                    "worksheet": PREPARED_WORKSHEET_NAME,
                    "worksheet_row_number": row_number,
                }
            )
            payload = {**record.project_payload, "source_metadata": metadata}
            records.append(
                cli_design.CLIDesignRecordV1(
                    **{**record.__dict__, "project_payload": payload}
                )
            )
    if source_rows == 0:
        issues.append(
            cli_design.CLIDesignIssueV1(
                "CLI_DESIGN_EMPTY_PROJECT",
                PREPARED_WORKSHEET_NAME,
                "A non-empty prepared-floor Beams worksheet is required.",
            )
        )
    if issues:
        raise cli_design.CLIDesignBlockedError(issues)
    return cli_design.CLIDesignIntakeV1(
        source_sha256=source_sha256,
        source_rows=source_rows,
        records=tuple(records),
    )


def load_prepared_floor_v1(
    path: Path, *, source_format: Literal["csv", "xlsx", "json"] | str
) -> cli_design.CLIDesignIntakeV1:
    """Load one prepared-floor batch without defaults or invented analysis provenance."""

    input_path = Path(path)
    normalized_format = source_format.strip().lower()
    expected_suffixes = {"csv": ".csv", "xlsx": ".xlsx", "json": ".json"}
    if normalized_format not in expected_suffixes:
        raise _blocked(
            "PREPARED_FLOOR_UNSUPPORTED_SOURCE_FORMAT",
            "source_format",
            "Expected one of: csv, xlsx, json.",
        )
    if input_path.suffix.lower() != expected_suffixes[normalized_format]:
        raise _blocked(
            "PREPARED_FLOOR_EXTENSION_MISMATCH",
            "input",
            f"source_format {normalized_format!r} requires {expected_suffixes[normalized_format]!r}.",
        )
    if normalized_format == "xlsx":
        return _load_xlsx(input_path)
    return cli_design.load_cli_design_input_v1(input_path, input_format="generic")


__all__ = [
    "PREPARED_WORKSHEET_HEADERS",
    "PREPARED_WORKSHEET_NAME",
    "load_prepared_floor_v1",
]
