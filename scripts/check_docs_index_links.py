#!/usr/bin/env python3
"""Ensure docs/README.md links resolve to real files/dirs."""

from __future__ import annotations

from pathlib import Path
import re

DOCS_INDEX = Path("docs/README.md")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
FENCE_RE = re.compile(r"^```")


def _strip_code_blocks(text: str) -> str:
    lines = []
    in_fence = False
    for line in text.splitlines():
        if FENCE_RE.match(line.strip()):
            in_fence = not in_fence
            continue
        if not in_fence:
            lines.append(line)
    return "\n".join(lines)


def _is_external(link: str) -> bool:
    return (
        link.startswith("http://")
        or link.startswith("https://")
        or link.startswith("mailto:")
    )


def main() -> int:
    if not DOCS_INDEX.exists():
        print("ERROR: docs/README.md not found")
        return 1

    text = _strip_code_blocks(DOCS_INDEX.read_text(encoding="utf-8"))
    base = DOCS_INDEX.parent

    errors: list[str] = []
    for match in LINK_RE.finditer(text):
        link = match.group(1).strip()
        if not link or _is_external(link) or link.startswith("#"):
            continue

        link_path = link.split("#", 1)[0]
        if not link_path:
            continue

        resolved = (base / link_path).resolve()
        if not resolved.exists():
            errors.append(f"Missing: {link_path}")

    if errors:
        print("ERROR: docs/README.md contains broken local links:")
        for err in errors:
            print(f"  - {err}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
