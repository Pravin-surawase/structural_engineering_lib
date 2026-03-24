#!/usr/bin/env python3
"""Ensure scripts/index.json and automation-map.json match the scripts folder contents.

When to use: After adding or removing scripts from the scripts/ folder.
Verifies every script is indexed in both index.json and automation-map.json.
"""

from __future__ import annotations

import argparse
import ast
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

    # Support old format: {categories: {cat: {scripts: {name: ...}}}}
    for category in data.get("categories", {}).values():
        for name in category.get("scripts", {}):
            indexed.add(name)

    for name in data.get("deprecated", {}).get("scripts", {}):
        indexed.add(name)

    # Support new format from generate_enhanced_index.py: {files: [{name: ...}]}
    for entry in data.get("files", []):
        name = entry.get("name", "")
        if any(name.endswith(ext) for ext in SCRIPT_EXTENSIONS):
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Machine-readable JSON output")
    args = parser.parse_args()

    errors = 0
    actual = _scan_script_files()
    report: dict = {"total_scripts": len(actual), "checks": {}}

    # Check index.json
    if not INDEX_PATH.exists():
        if not args.json:
            print("WARNING: scripts/index.json not found (skipping)")
        report["checks"]["index_json"] = {"status": "skipped", "reason": "file not found"}
    else:
        indexed = _load_indexed_scripts()
        missing = sorted(actual - indexed)
        extra = sorted(indexed - actual)
        report["checks"]["index_json"] = {
            "status": "fail" if (missing or extra) else "pass",
            "indexed": len(indexed),
            "missing": missing,
            "extra": extra,
        }
        if missing or extra:
            if not args.json:
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
        if not args.json:
            print("WARNING: scripts/automation-map.json not found (skipping)")
        report["checks"]["automation_map"] = {"status": "skipped", "reason": "file not found"}
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
        report["checks"]["automation_map"] = {
            "status": "fail" if (unmapped or phantom) else "pass",
            "mapped": len(mapped_scripts),
            "total": len(actual),
            "unmapped": unmapped,
            "phantom": phantom,
        }
        if unmapped:
            if not args.json:
                print(f"ERROR: {len(unmapped)} script(s) not in automation-map.json:")
                for name in unmapped:
                    print(f"    - {name}")
            errors += 1
        if phantom:
            if not args.json:
                print(f"ERROR: {len(phantom)} phantom script(s) in automation-map.json:")
                for name in phantom:
                    print(f"    - {name}")
            errors += 1
        if not unmapped and not phantom and not args.json:
            print(f"✓ automation-map.json: {len(mapped_scripts)}/{len(actual)} scripts covered")

    # Check "When to use:" in Python script docstrings
    py_scripts = sorted(s for s in actual if s.endswith(".py"))
    missing_when = []
    for name in py_scripts:
        path = SCRIPTS_DIR / name
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            doc = ast.get_docstring(tree) or ""
            if "when to use" not in doc.lower():
                missing_when.append(name)
        except SyntaxError:
            pass
    report["checks"]["when_to_use"] = {
        "status": "pass" if not missing_when else "info",
        "total_python": len(py_scripts),
        "missing": missing_when,
    }
    if not args.json:
        if missing_when:
            print(f"INFO: {len(missing_when)}/{len(py_scripts)} Python scripts missing 'When to use:' in docstring")
        else:
            print(f"✓ All {len(py_scripts)} Python scripts have 'When to use:' in docstring")

    if args.json:
        report["errors"] = errors
        print(json.dumps(report, indent=2))

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
