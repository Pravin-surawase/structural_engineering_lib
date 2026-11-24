"""Local-only upload seam for the floor-review demonstration."""

from __future__ import annotations

import base64
import csv
import io
import json
import re
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from zipfile import BadZipFile

from structural_lib.services.floor_etabs_excel import project_etabs_worksheet_v1
from structural_lib.services.floor_review import review_floor_v1

_MAX_FILES = 8
_MAX_BYTES = 2_000_000
_MAX_ROWS = 120
_MAX_COLUMNS = 32
_ALLOWED_SUFFIXES = {".csv", ".xlsx", ".json", ".e2k"}
_UNSAFE_NAME = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_WINDOWS_DEVICES = {
    "con",
    "prn",
    "aux",
    "nul",
    *(f"com{i}" for i in range(1, 10)),
    *(f"lpt{i}" for i in range(1, 10)),
}


def _error(message: str) -> dict[str, Any]:
    return {"kind": "error", "message": message}


def _issue(code: str, message: str, **extra: Any) -> dict[str, Any]:
    return {"code": code, "message": message, **extra}


def _files(payload: object, folder: Path) -> list[Path]:
    if (
        not isinstance(payload, dict)
        or not isinstance(payload.get("mode"), str)
        or payload["mode"] not in {"preview", "review"}
    ):
        raise ValueError("Request requires mode 'preview' or 'review'.")
    entries = payload.get("files")
    if not isinstance(entries, list) or not entries or len(entries) > _MAX_FILES:
        raise ValueError(f"Supply from 1 to {_MAX_FILES} files.")
    result: list[Path] = []
    names: set[str] = set()
    for entry in entries:
        if (
            not isinstance(entry, dict)
            or not isinstance(entry.get("name"), str)
            or not isinstance(entry.get("data"), str)
        ):
            raise ValueError("Each file needs string name and base64 data.")
        name = entry["name"]
        stem = name.partition(".")[0].rstrip().casefold()
        suffix = Path(name).suffix.casefold()
        normalized = name.casefold()
        if (
            not 1 <= len(name) <= 128
            or name.endswith((".", " "))
            or _UNSAFE_NAME.search(name)
            or stem in _WINDOWS_DEVICES
            or normalized in names
        ):
            raise ValueError("File names must be unique basenames without traversal.")
        if suffix == ".edb":
            raise ValueError(
                "EDB binary content is not accepted; retain it in licensed ETABS."
            )
        if suffix not in _ALLOWED_SUFFIXES:
            raise ValueError(f"{name}: unsupported file type.")
        try:
            raw = base64.b64decode(entry["data"], validate=True)
        except ValueError as exc:
            raise ValueError(f"{name}: invalid base64 data.") from exc
        if len(raw) > _MAX_BYTES:
            raise ValueError(
                f"{name}: file exceeds the {_MAX_BYTES} byte intake limit."
            )
        path = folder / name
        path.write_bytes(raw)
        result.append(path)
        names.add(normalized)
    return result


def _table(name: str, raw: bytes, worksheet: str | None = None) -> dict[str, Any]:
    try:
        rows = list(csv.reader(io.StringIO(raw.decode("utf-8-sig")), strict=True))
    except (UnicodeDecodeError, csv.Error) as exc:
        raise ValueError(f"{name}: not a readable UTF-8 CSV table.") from exc
    truncated = len(rows) > _MAX_ROWS or any(len(row) > _MAX_COLUMNS for row in rows)
    visible = [row[:_MAX_COLUMNS] for row in rows[:_MAX_ROWS]]
    first = next(
        (
            index
            for index, row in enumerate(visible)
            if any(cell.strip() for cell in row)
        ),
        None,
    )
    if first is None:
        return {
            "file": name,
            **({"worksheet": worksheet} if worksheet else {}),
            "title": None,
            "headers": [],
            "rows": [],
            "row_count": len(rows),
            "first_row_number": None,
            "truncated": truncated,
        }
    native_title = len(visible[first]) == 1 and visible[first][0].strip().startswith(
        "TABLE:"
    )
    title = visible[first][0] if native_title else None
    header = first + 1 if native_title else first
    headers = visible[header] if header < len(visible) else []
    return {
        "file": name,
        **({"worksheet": worksheet} if worksheet else {}),
        "title": title,
        "headers": headers,
        "rows": visible[header + 1 :],
        "row_count": len(rows),
        "first_row_number": header + 2,
        "truncated": truncated,
    }


def _raw_xlsx(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    try:
        from openpyxl import load_workbook
    except ImportError:
        return [], [
            _issue(
                "XLSX_DEPENDENCY_MISSING",
                "XLSX preview needs the optional [xlsx] dependency.",
                file=path.name,
            )
        ]
    workbook = load_workbook(path, read_only=True, data_only=False, keep_links=False)
    try:
        tables, issues = [], []
        for sheet in workbook.worksheets:
            if sheet.sheet_state != "visible":
                continue
            try:
                tables.append(
                    _table(
                        path.name,
                        project_etabs_worksheet_v1(path, worksheet=sheet.title),
                        sheet.title,
                    )
                )
            except ValueError as exc:
                issues.append(
                    _issue(
                        "XLSX_SHEET_UNAVAILABLE",
                        str(exc),
                        file=path.name,
                        worksheet=sheet.title,
                    )
                )
        return tables, issues
    finally:
        workbook.close()


def _json_schema(path: Path) -> str | None:
    if path.suffix.casefold() != ".json":
        return None
    try:
        version = json.loads(path.read_text(encoding="utf-8")).get("schema_version")
    except (OSError, json.JSONDecodeError, AttributeError):
        return None
    if not isinstance(version, str):
        return None
    return version


def _review(
    path: Path, profile: str, mode: str, *, identified: bool = False
) -> dict[str, Any] | None:
    result = review_floor_v1(path, profile=profile, evaluate=mode == "review")
    return (
        {"kind": "review", "result": result}
        if identified or result["intake_status"] == "ACCEPTED"
        else None
    )


def handle_demo_intake(payload: object) -> dict[str, Any]:
    """Accept a bounded local upload and return review JSON or read-only tables."""
    try:
        with TemporaryDirectory() as directory:
            paths = _files(payload, Path(directory))
            assert isinstance(payload, dict)
            mode = payload["mode"]
            manifest_profiles = {
                "floor-etabs-snapshot-packet/v1": "etabs-snapshot",
                "floor-etabs-paired-packet/v1": "etabs-paired",
            }
            manifests = [
                (path, profile)
                for path in paths
                if (profile := manifest_profiles.get(_json_schema(path)))
            ]
            if len(manifests) > 1:
                return _error(
                    "Select one review manifest and the files for that capture."
                )
            if manifests:
                path, profile = manifests[0]
                response = _review(path, profile, "preview", identified=True)
                assert response is not None
                preview = response["result"]
                if preview["intake_status"] != "ACCEPTED":
                    return response
                selected = {item.name for item in paths}
                used = {item["file"] for item in preview["artifacts"]}
                extra = sorted(selected - used)
                if extra:
                    return _error(
                        "Remove files outside this capture: " + ", ".join(extra)
                    )
                if mode == "review":
                    return _review(path, profile, mode, identified=True) or response
                return response
            if len(paths) == 1:
                suffix = paths[0].suffix.casefold()
                profile = {
                    ".csv": "prepared-csv",
                    ".xlsx": "prepared-xlsx",
                    ".json": "prepared-json",
                }.get(suffix)
                if profile:
                    schema = _json_schema(paths[0])
                    result = _review(
                        paths[0],
                        profile,
                        mode,
                        identified=schema == "cli-beam-design-input/v1",
                    )
                    if result:
                        return result
            tables: list[dict[str, Any]] = []
            issues: list[dict[str, Any]] = []
            for path in paths:
                suffix = path.suffix.casefold()
                if suffix == ".csv":
                    tables.append(_table(path.name, path.read_bytes()))
                elif suffix == ".xlsx":
                    found, warnings = _raw_xlsx(path)
                    tables.extend(found)
                    issues.extend(warnings)
                elif suffix == ".e2k":
                    issues.append(
                        _issue(
                            "E2K_ARCHIVAL_ONLY",
                            "E2K is retained as archival metadata, not parsed as an engineering input.",
                            file=path.name,
                        )
                    )
                else:
                    issues.append(
                        _issue(
                            "UNBOUND_FILE_NOT_PREVIEWED",
                            "Upload a CSV/XLSX table or a versioned manifest packet for review.",
                            file=path.name,
                        )
                    )
            if not tables and not issues:
                return _error("No previewable local table was supplied.")
            if mode == "review":
                issues.append(
                    _issue(
                        "UNBOUND_EXPORT_INTAKE_ONLY",
                        "Review is unavailable until a versioned manifest binds geometry, actions, units, axes, and revision identity.",
                    )
                )
            return {"kind": "tables", "tables": tables, "issues": issues}
    except (BadZipFile, OSError, SyntaxError, TypeError, ValueError) as exc:
        return _error(str(exc))
