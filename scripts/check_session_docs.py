#!/usr/bin/env python3
"""Validate next-session-brief.md and SESSION_log.md consistency."""

from __future__ import annotations

from pathlib import Path
import re

NEXT_PATH = Path("docs/planning/next-session-brief.md")
SESSION_PATH = Path("docs/SESSION_log.md")

DATE_RE = re.compile(r"Date:\*\*?\s*(\d{4}-\d{2}-\d{2})")
HANDOFF_DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
HANDOFF_START = "<!-- HANDOFF:START -->"
HANDOFF_END = "<!-- HANDOFF:END -->"


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


def _handoff_date(lines: list[str]) -> str | None:
    start_idx = -1
    end_idx = -1
    for idx, line in enumerate(lines):
        if HANDOFF_START in line:
            start_idx = idx
        if HANDOFF_END in line and start_idx != -1:
            end_idx = idx
            break
    if start_idx == -1 or end_idx == -1 or end_idx <= start_idx:
        return None

    for line in lines[start_idx:end_idx]:
        if line.strip().startswith("- Date:"):
            match = HANDOFF_DATE_RE.search(line)
            if match:
                return match.group(1)
    return None


def main() -> int:
    if not NEXT_PATH.exists():
        print("ERROR: docs/planning/next-session-brief.md not found")
        return 1
    if not SESSION_PATH.exists():
        print("ERROR: docs/SESSION_log.md not found")
        return 1

    next_lines = NEXT_PATH.read_text(encoding="utf-8").splitlines()
    session_lines = SESSION_PATH.read_text(encoding="utf-8").splitlines()

    if _find_heading(next_lines, "# Next Session Briefing") == -1:
        print("ERROR: next-session-brief.md missing '# Next Session Briefing'")
        return 1

    if not any("Required Reading" in line for line in next_lines):
        print("ERROR: next-session-brief.md missing 'Required Reading' section")
        return 1

    if not any("| **Current** |" in line for line in next_lines):
        print("ERROR: next-session-brief.md missing Current release row")
        return 1
    if not any("| **Next** |" in line for line in next_lines):
        print("ERROR: next-session-brief.md missing Next release row")
        return 1

    date_match = None
    for line in next_lines:
        match = DATE_RE.search(line)
        if match:
            date_match = match
            break

    if not date_match:
        print("ERROR: next-session-brief.md missing Date field")
        return 1

    date_str = date_match.group(1)
    handoff_date = _handoff_date(next_lines)
    if not handoff_date:
        print("ERROR: next-session-brief.md missing Latest Handoff block")
        print("Run: python scripts/update_handoff.py")
        return 1
    if handoff_date != date_str:
        print("ERROR: Latest Handoff date does not match next-session-brief Date field")
        print(f"Expected {date_str}, found {handoff_date}")
        return 1

    # Check session log has matching date header.
    session_heading = f"## {date_str}"
    first_session_line = None
    session_idx = -1
    for idx, line in enumerate(session_lines):
        if line.startswith("## ") and first_session_line is None:
            first_session_line = line
        if line.startswith(session_heading) and "Session" in line:
            session_idx = idx
            break

    if session_idx == -1:
        print(f"ERROR: SESSION_log.md missing session entry for {date_str}")
        return 1

    if first_session_line is not None and not first_session_line.startswith(session_heading):
        print("ERROR: SESSION_log.md newest session must be at the top (append-only).")
        print(f"Expected first session header to start with {session_heading}.")
        return 1

    # Ensure Focus appears near the session header.
    window = session_lines[session_idx : session_idx + 25]
    if not any("Focus:" in line for line in window):
        print(f"ERROR: SESSION_log.md entry for {date_str} missing 'Focus:' line")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
