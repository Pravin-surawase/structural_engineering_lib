#!/usr/bin/env python3
"""Ensure script indexes and the canonical control plane match scripts on disk.

When to use: After adding or removing scripts from the scripts/ folder.
Verifies every top-level script is indexed and registered, and that the legacy
automation map is the exact deterministic compatibility projection.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from control_plane import (  # noqa: E402
    LEGACY_PATH,
    REGISTRY_PATH,
    ControlPlaneError,
    legacy_is_current,
    legacy_projection,
    load_registry,
    referenced_top_level_scripts,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
INDEX_PATH = SCRIPTS_DIR / "index.json"
AUTOMATION_MAP_PATH = LEGACY_PATH
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


def _automation_semantic_issues(data: dict) -> dict[str, list[str]]:
    """Validate the single-source task/group discovery contract."""
    tasks = data.get("tasks", {})
    legacy_categories = sorted(data.get("categories", {}))
    missing_group: list[str] = []
    removed_without_deprecation: list[str] = []
    temporary_targets: list[str] = []

    for task_name, info in tasks.items():
        if info.get("deprecated", False):
            continue
        group = info.get("group")
        if not isinstance(group, str) or not group.strip():
            missing_group.append(task_name)
        description = str(info.get("description", "")).lower()
        if "(removed)" in description:
            removed_without_deprecation.append(task_name)
        if "scripts/_tmp_" in str(info.get("script", "")):
            temporary_targets.append(task_name)

    return {
        "legacy_categories": legacy_categories,
        "missing_group": sorted(missing_group),
        "removed_without_deprecation": sorted(removed_without_deprecation),
        "temporary_targets": sorted(temporary_targets),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json", action="store_true", help="Machine-readable JSON output"
    )
    args = parser.parse_args()

    errors = 0
    actual = _scan_script_files()
    report: dict = {"total_scripts": len(actual), "checks": {}}

    # Check index.json
    if not INDEX_PATH.exists():
        if not args.json:
            print("WARNING: scripts/index.json not found (skipping)")
        report["checks"]["index_json"] = {
            "status": "skipped",
            "reason": "file not found",
        }
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

    # Check canonical control plane and exact compatibility projection.
    try:
        control_registry = load_registry()
    except ControlPlaneError as exc:
        report["checks"]["control_plane"] = {
            "status": "fail",
            "reason": str(exc),
        }
        if not args.json:
            print(f"ERROR: canonical control plane is invalid: {exc}")
        errors += 1
    else:
        mapped_scripts = referenced_top_level_scripts(control_registry)
        unmapped = sorted(actual - mapped_scripts)
        phantom = sorted(mapped_scripts - actual)
        report["checks"]["control_plane"] = {
            "status": "fail" if (unmapped or phantom) else "pass",
            "mapped": len(mapped_scripts),
            "total": len(actual),
            "unmapped": unmapped,
            "phantom": phantom,
        }
        if unmapped or phantom:
            errors += 1
            if not args.json:
                print("ERROR: scripts/control-plane.json script coverage differs.")
                for name in unmapped:
                    print(f"  Unmapped: {name}")
                for name in phantom:
                    print(f"  Phantom: {name}")
        elif not args.json:
            print(
                f"✓ control plane: {len(mapped_scripts)}/{len(actual)} scripts covered"
            )

        projection_current = legacy_is_current(control_registry)
        report["checks"]["automation_projection"] = {
            "status": "pass" if projection_current else "fail",
            "source": str(REGISTRY_PATH.relative_to(REPO_ROOT)),
            "target": str(AUTOMATION_MAP_PATH.relative_to(REPO_ROOT)),
        }
        if not projection_current:
            errors += 1
            if not args.json:
                print(
                    "ERROR: automation-map.json is not the exact generated projection."
                )
        elif not args.json:
            print("✓ automation-map.json: deterministic compatibility projection")

        projected = legacy_projection(control_registry)
        semantic_issues = _automation_semantic_issues(projected)
        semantic_failed = any(semantic_issues.values())
        report["checks"]["automation_semantics"] = {
            "status": "fail" if semantic_failed else "pass",
            **semantic_issues,
        }
        if semantic_failed:
            errors += 1
            if not args.json:
                print("ERROR: operation discovery metadata is inconsistent.")
                for issue_name, values in semantic_issues.items():
                    if values:
                        print(f"  {issue_name}: {', '.join(values)}")
        elif not args.json:
            print(
                f"✓ operation discovery: {len(projected.get('tasks', {}))} grouped tasks"
            )

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
            print(
                f"INFO: {len(missing_when)}/{len(py_scripts)} Python scripts missing 'When to use:' in docstring"
            )
        else:
            print(
                f"✓ All {len(py_scripts)} Python scripts have 'When to use:' in docstring"
            )

    if args.json:
        report["errors"] = errors
        print(json.dumps(report, indent=2))

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
