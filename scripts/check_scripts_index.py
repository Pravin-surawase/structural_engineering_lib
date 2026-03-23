#!/usr/bin/env python3
"""Ensure scripts/index.json and automation-map.json match the scripts folder contents."""

from __future__ import annotations

import json
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
INDEX_PATH = SCRIPTS_DIR / "index.json"
AUTOMATION_MAP_PATH = SCRIPTS_DIR / "automation-map.json"
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
    errors = 0
    actual = _scan_script_files()

    # Check index.json
    if not INDEX_PATH.exists():
        print("WARNING: scripts/index.json not found (skipping)")
    else:
        indexed = _load_indexed_scripts()
        missing = sorted(actual - indexed)
        extra = sorted(indexed - actual)
        if missing or extra:
            print("ERROR: scripts/index.json is out of sync.")
            if missing:
                print("  Missing from index.json:")
                for name in missing:
                    print(f"    - {name}")
            if extra:
                print("  In index.json but not on disk:")
                for name in extra:
                    print(f"    - {name}")
            errors += 1

    # Check automation-map.json
    if not AUTOMATION_MAP_PATH.exists():
        print("WARNING: scripts/automation-map.json not found (skipping)")
    else:
        data = json.loads(AUTOMATION_MAP_PATH.read_text(encoding="utf-8"))
        mapped_scripts: set[str] = set()
        for _task, info in data.get("tasks", {}).items():
            script = info.get("script", "")
            for part in script.split():
                if "scripts/" in part:
                    mapped_scripts.add(os.path.basename(part))
                    break
        unmapped = sorted(actual - mapped_scripts)
        phantom = sorted(mapped_scripts - actual)
        if unmapped:
            print(f"ERROR: {len(unmapped)} script(s) not in automation-map.json:")
            for name in unmapped:
                print(f"    - {name}")
            errors += 1
        if phantom:
            print(f"ERROR: {len(phantom)} phantom script(s) in automation-map.json:")
            for name in phantom:
                print(f"    - {name}")
            errors += 1
        if not unmapped and not phantom:
            print(f"✓ automation-map.json: {len(mapped_scripts)}/{len(actual)} scripts covered")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
