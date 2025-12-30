#!/usr/bin/env python3
"""Ensure next-session-brief.md stays concise."""

from __future__ import annotations

from pathlib import Path

BRIEF_PATH = Path("docs/planning/next-session-brief.md")
MAX_LINES = 150


def main() -> int:
    if not BRIEF_PATH.exists():
        print("ERROR: docs/planning/next-session-brief.md not found")
        return 1

    lines = BRIEF_PATH.read_text(encoding="utf-8").splitlines()
    line_count = len(lines)

    if line_count > MAX_LINES:
        print(
            f"ERROR: next-session-brief.md is {line_count} lines (max {MAX_LINES})."
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
