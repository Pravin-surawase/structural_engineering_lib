#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Check API backward compatibility.

Compares the current public API surface of services/api.py against the
saved manifest to detect breaking changes (removed functions, renamed
params, changed param order).

Usage:
    .venv/bin/python scripts/check_api_compat.py              # Check for breaking changes
    .venv/bin/python scripts/check_api_compat.py --update      # Update the manifest
"""

from __future__ import annotations

import argparse
import inspect
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = (
    PROJECT_ROOT / "Python" / "structural_lib" / "services" / "api_manifest.json"
)
sys.path.insert(0, str(PROJECT_ROOT / "Python"))


def get_current_api() -> dict:
    """Introspect the current public API surface."""
    from structural_lib.services import api as api_mod

    manifest: dict = {}
    for name in sorted(dir(api_mod)):
        obj = getattr(api_mod, name)
        if inspect.isfunction(obj) and not name.startswith("_"):
            sig = inspect.signature(obj)
            params = []
            for pname, param in sig.parameters.items():
                p: dict = {"name": pname}
                if param.default is not inspect.Parameter.empty:
                    p["has_default"] = True
                params.append(p)
            entry: dict = {
                "params": [p["name"] for p in params],
                "param_details": params,
            }
            ret = sig.return_annotation
            if ret is not inspect.Parameter.empty:
                entry["returns"] = str(ret)
            manifest[name] = entry
    return manifest


def check_compat(saved: dict, current: dict) -> list[str]:
    """Compare saved manifest against current API. Return list of breaking changes."""
    issues: list[str] = []

    # Check for removed functions
    for func_name in saved:
        if func_name not in current:
            issues.append(f"REMOVED: {func_name}() was removed from public API")

    # Check for changed signatures
    for func_name, saved_entry in saved.items():
        if func_name not in current:
            continue
        current_entry = current[func_name]

        saved_params = saved_entry["params"]
        current_params = current_entry["params"]

        # Check for removed required params
        saved_required = [
            p["name"]
            for p in saved_entry.get("param_details", [])
            if not p.get("has_default")
        ]
        current_all = set(current_params)
        for param in saved_required:
            if param not in current_all:
                issues.append(
                    f"BREAKING: {func_name}() — required param '{param}' was removed"
                )

        # Check for new required params (added without default)
        current_required = [
            p["name"]
            for p in current_entry.get("param_details", [])
            if not p.get("has_default")
        ]
        saved_all = set(saved_params)
        for param in current_required:
            if param not in saved_all:
                issues.append(
                    f"BREAKING: {func_name}() — new required param '{param}' added (needs default)"
                )

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Check API backward compatibility")
    parser.add_argument(
        "--update", action="store_true", help="Update the manifest to current state"
    )
    args = parser.parse_args()

    current = get_current_api()

    if args.update:
        MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST_PATH.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n")
        print(
            f"✅ Updated {MANIFEST_PATH.relative_to(PROJECT_ROOT)} ({len(current)} functions)"
        )
        return 0

    if not MANIFEST_PATH.exists():
        print(f"⚠️  No manifest found at {MANIFEST_PATH.relative_to(PROJECT_ROOT)}")
        print("   Run: .venv/bin/python scripts/check_api_compat.py --update")
        return 1

    saved = json.loads(MANIFEST_PATH.read_text())
    issues = check_compat(saved, current)

    # Also report new functions (non-breaking, informational)
    new_funcs = [f for f in current if f not in saved]

    if new_funcs:
        print(f"ℹ️  New functions added ({len(new_funcs)}):")
        for f in new_funcs:
            print(f"   + {f}()")

    if issues:
        print(f"\n❌ {len(issues)} breaking change(s) detected:")
        for issue in issues:
            print(f"   {issue}")
        print(
            "\n   If intentional, bump the version and run: .venv/bin/python scripts/check_api_compat.py --update"
        )
        return 1

    print(f"✅ API compatible ({len(current)} functions, {len(new_funcs)} new)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
