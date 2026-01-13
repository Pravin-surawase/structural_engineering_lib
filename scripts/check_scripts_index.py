#!/usr/bin/env python3
"""Ensure scripts/index.json matches the scripts folder contents."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
INDEX_PATH = SCRIPTS_DIR / "index.json"
SCRIPT_EXTENSIONS = {".py", ".sh"}


def _load_indexed_scripts() -> set[str]:
    data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    indexed: set[str] = set()

    for category in data.get("categories", {}).values():
        for name in category.get("scripts", {}):
            indexed.add(name)

    for name in data.get("deprecated", {}).get("scripts", {}):
        indexed.add(name)

    return indexed


def _scan_script_files() -> set[str]:
    scripts: set[str] = set()
    for path in SCRIPTS_DIR.iterdir():
        if path.is_dir():
            continue
        if path.suffix not in SCRIPT_EXTENSIONS:
            continue
        if path.name.startswith("."):
            continue
        scripts.add(path.name)
    return scripts


def main() -> int:
    if not INDEX_PATH.exists():
        print("ERROR: scripts/index.json not found")
        return 1

    indexed = _load_indexed_scripts()
    actual = _scan_script_files()

    missing = sorted(actual - indexed)
    extra = sorted(indexed - actual)

    if missing or extra:
        print("ERROR: scripts/index.json is out of sync.")
        if missing:
            print("Missing from index.json:")
            for name in missing:
                print(f"  - {name}")
        if extra:
            print("Missing on disk:")
            for name in extra:
                print(f"  - {name}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
