#!/usr/bin/env python3
"""Validate pre-release checklist structure and required sections."""

from __future__ import annotations

from pathlib import Path

CHECKLIST_PATH = Path("docs/planning/pre-release-checklist.md")

REQUIRED_HEADINGS = [
    "# Pre-Release Checklist",
    "## Current State",
    "## Beta Readiness Checklist",
    "### Required Before Beta",
    "### Required Before 1.0",
]


def _find_heading(lines: list[str], heading: str) -> int:
    for idx, line in enumerate(lines):
        if line.strip().startswith(heading):
            return idx
    return -1


def _section(lines: list[str], start_idx: int) -> list[str]:
    end_idx = len(lines)
    for idx in range(start_idx + 1, len(lines)):
        if lines[idx].startswith("## ") or lines[idx].startswith("### "):
            end_idx = idx
            break
    return lines[start_idx + 1 : end_idx]


def _has_checkboxes(section_lines: list[str]) -> bool:
    return any(line.strip().startswith("- [") for line in section_lines)


def main() -> int:
    if not CHECKLIST_PATH.exists():
        print("ERROR: docs/planning/pre-release-checklist.md not found")
        return 1

    lines = CHECKLIST_PATH.read_text(encoding="utf-8").splitlines()

    for heading in REQUIRED_HEADINGS:
        if _find_heading(lines, heading) == -1:
            print(f"ERROR: Missing heading: {heading}")
            return 1

    required_beta_idx = _find_heading(lines, "### Required Before Beta")
    required_1_idx = _find_heading(lines, "### Required Before 1.0")

    if required_beta_idx != -1:
        beta_lines = _section(lines, required_beta_idx)
        if not _has_checkboxes(beta_lines):
            print("ERROR: 'Required Before Beta' must include checklist items")
            return 1

    if required_1_idx != -1:
        one_lines = _section(lines, required_1_idx)
        if not _has_checkboxes(one_lines):
            print("ERROR: 'Required Before 1.0' must include checklist items")
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
