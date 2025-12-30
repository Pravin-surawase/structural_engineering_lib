#!/usr/bin/env python3
"""Ensure CLI reference includes required commands."""

from __future__ import annotations

from pathlib import Path
import re

CLI_REF = Path("docs/cookbook/cli-reference.md")

REQUIRED_COMMANDS = {
    "design",
    "bbs",
    "detail",
    "dxf",
    "job",
    "validate",
    "critical",
    "report",
    "mark-diff",
}

CMD_RE = re.compile(r"python\s+-m\s+structural_lib\s+(\S+)")


def main() -> int:
    if not CLI_REF.exists():
        print("ERROR: docs/cookbook/cli-reference.md not found")
        return 1

    text = CLI_REF.read_text(encoding="utf-8")
    commands = set(match.group(1) for match in CMD_RE.finditer(text))

    missing = sorted(REQUIRED_COMMANDS - commands)
    if missing:
        print("ERROR: CLI reference missing commands:")
        for cmd in missing:
            print(f"  - {cmd}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
