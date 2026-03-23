#!/usr/bin/env python3
"""Check OpenAPI spec against baseline snapshot to detect API drift.

When to use: After modifying FastAPI routers, Pydantic models, or endpoint signatures.
Compares current OpenAPI schema to fastapi_app/openapi_baseline.json and reports
added/removed/changed endpoints and schemas.

Usage:
    .venv/bin/python scripts/check_openapi_snapshot.py              # Check for drift
    .venv/bin/python scripts/check_openapi_snapshot.py --update     # Update baseline
    .venv/bin/python scripts/check_openapi_snapshot.py --json       # Machine-readable output
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.utils import REPO_ROOT

BASELINE_PATH = REPO_ROOT / "fastapi_app" / "openapi_baseline.json"


def _get_current_spec() -> dict:
    """Generate current OpenAPI spec from the FastAPI app."""
    # Add the project root so fastapi_app is importable
    sys.path.insert(0, str(REPO_ROOT))
    from fastapi_app.main import app

    return app.openapi()


def _extract_endpoints(spec: dict) -> dict[str, set[str]]:
    """Extract {path: set(methods)} from an OpenAPI spec."""
    endpoints: dict[str, set[str]] = {}
    for path, methods in spec.get("paths", {}).items():
        endpoints[path] = {m.upper() for m in methods if m.upper() in {"GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"}}
    return endpoints


def _extract_schemas(spec: dict) -> set[str]:
    """Extract schema names from an OpenAPI spec."""
    return set(spec.get("components", {}).get("schemas", {}).keys())


def _diff_specs(baseline: dict, current: dict) -> dict:
    """Compare baseline and current specs, return structured diff."""
    b_endpoints = _extract_endpoints(baseline)
    c_endpoints = _extract_endpoints(current)
    b_schemas = _extract_schemas(baseline)
    c_schemas = _extract_schemas(current)

    # Endpoint diffs
    all_paths = set(b_endpoints.keys()) | set(c_endpoints.keys())
    added_endpoints = []
    removed_endpoints = []
    changed_endpoints = []

    for path in sorted(all_paths):
        b_methods = b_endpoints.get(path, set())
        c_methods = c_endpoints.get(path, set())
        if path not in b_endpoints:
            for m in sorted(c_methods):
                added_endpoints.append(f"{m} {path}")
        elif path not in c_endpoints:
            for m in sorted(b_methods):
                removed_endpoints.append(f"{m} {path}")
        elif b_methods != c_methods:
            added = c_methods - b_methods
            removed = b_methods - c_methods
            for m in sorted(added):
                added_endpoints.append(f"{m} {path}")
            for m in sorted(removed):
                removed_endpoints.append(f"{m} {path}")

    # Schema diffs
    added_schemas = sorted(c_schemas - b_schemas)
    removed_schemas = sorted(b_schemas - c_schemas)

    # Schema field-level changes (detect modified schemas)
    changed_schemas = []
    for name in sorted(b_schemas & c_schemas):
        b_schema = baseline.get("components", {}).get("schemas", {}).get(name, {})
        c_schema = current.get("components", {}).get("schemas", {}).get(name, {})
        if b_schema != c_schema:
            changed_schemas.append(name)

    return {
        "endpoints": {
            "added": added_endpoints,
            "removed": removed_endpoints,
            "changed": changed_endpoints,
        },
        "schemas": {
            "added": added_schemas,
            "removed": removed_schemas,
            "changed": changed_schemas,
        },
        "baseline_endpoints": sum(len(v) for v in b_endpoints.values()),
        "current_endpoints": sum(len(v) for v in c_endpoints.values()),
        "baseline_schemas": len(b_schemas),
        "current_schemas": len(c_schemas),
    }


def _has_changes(diff: dict) -> bool:
    """Check if any changes were detected."""
    return any([
        diff["endpoints"]["added"],
        diff["endpoints"]["removed"],
        diff["schemas"]["added"],
        diff["schemas"]["removed"],
        diff["schemas"]["changed"],
    ])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--update", action="store_true", help="Update baseline to current spec")
    parser.add_argument("--json", action="store_true", help="Machine-readable JSON output")
    args = parser.parse_args()

    # Generate current spec
    try:
        current = _get_current_spec()
    except Exception as e:
        if args.json:
            print(json.dumps({"error": f"Failed to load FastAPI app: {e}"}))
        else:
            print(f"ERROR: Failed to load FastAPI app: {e}")
        return 1

    # Update mode
    if args.update:
        BASELINE_PATH.write_text(
            json.dumps(current, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        if args.json:
            endpoints = _extract_endpoints(current)
            schemas = _extract_schemas(current)
            print(json.dumps({
                "status": "updated",
                "endpoints": sum(len(v) for v in endpoints.values()),
                "schemas": len(schemas),
            }))
        else:
            endpoints = _extract_endpoints(current)
            schemas = _extract_schemas(current)
            print(f"✓ Baseline updated: {sum(len(v) for v in endpoints.values())} endpoints, {len(schemas)} schemas")
        return 0

    # Check mode — compare against baseline
    if not BASELINE_PATH.exists():
        if args.json:
            print(json.dumps({"error": "No baseline found. Run with --update first."}))
        else:
            print("ERROR: No baseline found at fastapi_app/openapi_baseline.json")
            print("  Run: .venv/bin/python scripts/check_openapi_snapshot.py --update")
        return 1

    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    diff = _diff_specs(baseline, current)

    if args.json:
        diff["has_changes"] = _has_changes(diff)
        print(json.dumps(diff, indent=2))
        return 1 if _has_changes(diff) else 0

    # Human-readable output
    if not _has_changes(diff):
        print(f"✓ OpenAPI spec matches baseline ({diff['current_endpoints']} endpoints, {diff['current_schemas']} schemas)")
        return 0

    print("OpenAPI spec has drifted from baseline:")
    print()

    if diff["endpoints"]["added"]:
        print("  Added endpoints:")
        for ep in diff["endpoints"]["added"]:
            print(f"    + {ep}")
    if diff["endpoints"]["removed"]:
        print("  Removed endpoints:")
        for ep in diff["endpoints"]["removed"]:
            print(f"    - {ep}")

    if diff["schemas"]["added"]:
        print(f"  Added schemas: {', '.join(diff['schemas']['added'])}")
    if diff["schemas"]["removed"]:
        print(f"  Removed schemas: {', '.join(diff['schemas']['removed'])}")
    if diff["schemas"]["changed"]:
        print(f"  Changed schemas: {', '.join(diff['schemas']['changed'])}")

    print()
    print(f"  Baseline: {diff['baseline_endpoints']} endpoints, {diff['baseline_schemas']} schemas")
    print(f"  Current:  {diff['current_endpoints']} endpoints, {diff['current_schemas']} schemas")
    print()
    print("  To update baseline: .venv/bin/python scripts/check_openapi_snapshot.py --update")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
