#!/usr/bin/env python3
"""Validate docs/TASKS.md structure and WIP rules."""

from __future__ import annotations

from pathlib import Path
import re

TASKS_PATH = Path("docs/TASKS.md")
TASK_ID_RE = re.compile(r"TASK-\\d{3}", re.IGNORECASE)

REQUIRED_HEADINGS = [
    "## Rules (read first)",
    "## Current Release",
    "## Active",
    "## Up Next",
    "## Backlog",
    "## Recently Done",
    "## Archive",
]


def _find_heading(lines: list[str], heading: str) -> int:
    for idx, line in enumerate(lines):
        if line.strip() == heading:
            return idx
    return -1


def _section(lines: list[str], start_idx: int) -> list[str]:
    end_idx = len(lines)
    for idx in range(start_idx + 1, len(lines)):
        if lines[idx].startswith("## "):
            end_idx = idx
            break
    return lines[start_idx + 1 : end_idx]


def _table_rows(section_lines: list[str]) -> list[str]:
    rows = [line for line in section_lines if line.strip().startswith("|")]
    if not rows:
        return []
    # Drop header + separator if present.
    data_rows = []
    for line in rows:
        if "| ID |" in line and "| Task |" in line:
            continue
        if set(line.strip()) <= {"|", "-", " "}:
            continue
        data_rows.append(line)
    return data_rows


def _parse_row_columns(line: str) -> list[str]:
    return [part.strip() for part in line.strip().strip("|").split("|")]


def _extract_task_id(text: str) -> str | None:
    match = TASK_ID_RE.search(text)
    if match:
        return match.group(0).upper()
    return None


def _task_ids_in_text(text: str) -> list[str]:
    return [match.group(0).upper() for match in TASK_ID_RE.finditer(text)]


def main() -> int:
    if not TASKS_PATH.exists():
        print(f"ERROR: Missing {TASKS_PATH}")
        return 1

    lines = TASKS_PATH.read_text(encoding="utf-8").splitlines()

    # Headings present and ordered.
    positions = []
    for heading in REQUIRED_HEADINGS:
        pos = _find_heading(lines, heading)
        if pos == -1:
            print(f"ERROR: Missing heading: {heading}")
            return 1
        positions.append(pos)

    if positions != sorted(positions):
        print("ERROR: Headings are out of order.")
        return 1

    # Rules section contains WIP rule (allow WIP = 1 or WIP = 2).
    rules_lines = _section(lines, positions[0])
    if not any("WIP = 1" in line or "WIP = 2" in line for line in rules_lines):
        print("ERROR: Rules section must include 'WIP = 1' or 'WIP = 2'.")
        return 1

    # Determine WIP limit.
    wip_limit = 2 if any("WIP = 2" in line for line in rules_lines) else 1

    # Active section WIP count.
    active_lines = _section(lines, positions[2])
    active_rows = _table_rows(active_lines)
    if len(active_rows) > wip_limit:
        print(
            f"ERROR: Active section must have at most {wip_limit} task(s) (WIP={wip_limit})."
        )
        return 1

    # Up Next table header.
    up_next_lines = _section(lines, positions[3])
    if not any(
        "| ID | Task | Agent | Est | Priority | Status |" in line
        for line in up_next_lines
    ):
        print("ERROR: Up Next table header missing or malformed.")
        return 1

    # Recently Done table header.
    done_lines = _section(lines, positions[5])
    if not any("| ID | Task | Agent | Status |" in line for line in done_lines):
        print("ERROR: Recently Done table header missing or malformed.")
        return 1

    # Umbrella tasks must list included TASK IDs in the description.
    for start_idx in positions[2:6]:
        section_lines = _section(lines, start_idx)
        for row in _table_rows(section_lines):
            columns = _parse_row_columns(row)
            if len(columns) < 2:
                continue
            task_id = _extract_task_id(columns[0])
            if not task_id:
                continue
            task_desc = columns[1]
            if "umbrella" not in task_desc.lower():
                continue
            included_ids = [
                included
                for included in _task_ids_in_text(task_desc)
                if included != task_id
            ]
            if not included_ids:
                print(
                    "ERROR: Umbrella task must list included TASK IDs in its description "
                    f"({task_id})."
                )
                return 1

    # Archive link.
    archive_lines = _section(lines, positions[6])
    if not any("docs/_archive/tasks-history.md" in line for line in archive_lines):
        print("ERROR: Archive link missing (docs/_archive/tasks-history.md).")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
