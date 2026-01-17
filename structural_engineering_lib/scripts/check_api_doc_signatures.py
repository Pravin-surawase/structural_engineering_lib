#!/usr/bin/env python3
"""Ensure api.__all__ functions are documented in docs/reference/api.md."""

from __future__ import annotations

from pathlib import Path
import re
import sys

DOC_PATH = Path("docs/reference/api.md")


def _load_api_module():
    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root / "Python"))
    from structural_lib import api  # type: ignore

    return api


def _documented_names(doc_text: str) -> set[str]:
    names: set[str] = set()
    for match in re.finditer(r"\bapi\.([a-zA-Z_][a-zA-Z0-9_]*)", doc_text):
        names.add(match.group(1))
    for match in re.finditer(
        r"^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", doc_text, re.M
    ):
        names.add(match.group(1))
    return names


def main() -> int:
    if not DOC_PATH.exists():
        print("ERROR: docs/reference/api.md not found")
        return 1

    doc_text = DOC_PATH.read_text(encoding="utf-8")
    documented = _documented_names(doc_text)

    api = _load_api_module()
    exported = [
        name for name in getattr(api, "__all__", []) if not name.startswith("_")
    ]

    missing = [name for name in exported if name not in documented]
    if missing:
        print("ERROR: api.__all__ symbols missing from docs/reference/api.md:")
        for name in missing:
            print(f"  - {name}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
