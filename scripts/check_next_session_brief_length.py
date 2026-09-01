#!/usr/bin/env python3
"""Ensure next-session-brief.md remains a readable handoff artifact.

The former 150-line cap was an arbitrary proxy for handoff quality and could
reject useful durable context. Session structure/freshness checks own handoff
quality; this compatibility command now checks only file presence, UTF-8
readability, and non-empty content.
"""

from __future__ import annotations

from pathlib import Path

BRIEF_PATH = Path("docs/planning/next-session-brief.md")


def main() -> int:
    if not BRIEF_PATH.exists():
        print("ERROR: docs/planning/next-session-brief.md not found")
        return 1

    try:
        content = BRIEF_PATH.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        print(f"ERROR: next-session-brief.md is not valid UTF-8: {exc}")
        return 1
    if not content.strip():
        print("ERROR: next-session-brief.md is empty")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
