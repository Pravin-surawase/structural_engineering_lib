#!/usr/bin/env python3
"""Validate docs/README.md structure."""

from __future__ import annotations

from pathlib import Path
import sys

DOC_PATH = Path("docs/README.md")

REQUIRED_HEADINGS = [
    "# Docs Index (Start Here)",
    "## Quick CLI Reference",
    "## For Most Users",
    "## Visual Outputs",
    "## For Contributors / Maintainers",
    "## Planning / Research",
    "## Release History",
    "## Internal (multi-agent workflow)",
]


def main() -> int:
    if not DOC_PATH.exists():
        print("ERROR: docs/README.md not found")
        return 1

    text = DOC_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()

    for heading in REQUIRED_HEADINGS:
        if not any(line.startswith(heading) for line in lines):
            print(f"ERROR: Missing heading: {heading}")
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
