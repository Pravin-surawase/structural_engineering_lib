#!/usr/bin/env python3
"""Parity dashboard across declared Indian-code scope and application layers.

Uses the generated INDIA-0 manifest and source scans for four dimensions:
  1. Declared Indian-code capability families — supported vs explicitly held
  2. API → Endpoint Coverage — library functions with FastAPI routes
  3. Endpoint → Test Coverage — FastAPI endpoints with tests
  4. React Hook → API Coverage — hooks connected to API endpoints

Capability-family percentages are planning indicators only. They are not
clause coverage, whole-standard completeness, or engineering approval.

When to use: after cross-layer API changes or before parity planning and release review.

Usage:
    ./scripts/python_runtime.sh scripts/parity_dashboard.py
    ./scripts/python_runtime.sh scripts/parity_dashboard.py --json
    ./scripts/python_runtime.sh scripts/parity_dashboard.py --section capabilities
    ./scripts/python_runtime.sh scripts/parity_dashboard.py --missing
"""

from __future__ import annotations

import argparse
import ast
import inspect
import json
import re
import sys
from pathlib import Path
from typing import Any

from _lib.indian_code_manifest import load_manifest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
API_PY = REPO_ROOT / "Python" / "structural_lib" / "services" / "api.py"
ROUTERS_DIR = REPO_ROOT / "fastapi_app" / "routers"
FASTAPI_TESTS = REPO_ROOT / "fastapi_app" / "tests"
HOOKS_DIR = REPO_ROOT / "react_app" / "src" / "hooks"
LOCAL_ONLY_HOOKS = {"useReducedMotion", "useWebGLContextLoss"}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _progress_bar(fraction: float, width: int = 23) -> str:
    """Render a simple ASCII progress bar."""
    filled = int(round(fraction * width))
    return "\u2588" * filled + "\u2591" * (width - filled)


def _scan_public_functions(_path: Path) -> list[str]:
    """Return callable functions exported by the public API hub.

    ``services/api.py`` is now a re-export module, so scanning only local
    ``def`` statements incorrectly reports 0/0 coverage.
    """
    python_root = REPO_ROOT / "Python"
    sys.path.insert(0, str(python_root))
    from structural_lib import api  # type: ignore

    return sorted(
        name
        for name in getattr(api, "__all__", [])
        if inspect.isfunction(getattr(api, name, None))
        or inspect.isbuiltin(getattr(api, name, None))
    )


def _scan_router_endpoints(routers_dir: Path) -> list[dict[str, str]]:
    """Scan FastAPI router files for @router.METHOD("/path") decorators."""
    endpoints: list[dict[str, str]] = []
    if not routers_dir.is_dir():
        return endpoints
    for py in sorted(routers_dir.glob("*.py")):
        if py.name.startswith("_"):
            continue
        router_name = py.stem
        text = py.read_text()
        prefix_match = re.search(
            r"APIRouter\((?:(?!\)\s*$).)*?prefix\s*=\s*[\"']([^\"']*)[\"']",
            text,
            re.MULTILINE | re.DOTALL,
        )
        prefix = prefix_match.group(1).rstrip("/") if prefix_match else ""
        for m in re.finditer(
            r'@router\.(get|post|put|delete|patch|websocket)\(\s*["\']([^"\']*)["\']',
            text,
        ):
            method = m.group(1).upper()
            path = f"{prefix}/{m.group(2).lstrip('/')}" or "/"
            endpoints.append({"router": router_name, "method": method, "path": path})
    return endpoints


def _scan_test_functions(tests_dir: Path) -> list[dict[str, str]]:
    """Scan test directory for test functions."""
    tests: list[dict[str, str]] = []
    if not tests_dir.is_dir():
        return tests
    for py in sorted(tests_dir.glob("test_*.py")):
        text = py.read_text()
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(
                node, (ast.FunctionDef, ast.AsyncFunctionDef)
            ) and node.name.startswith("test_"):
                tests.append({"file": py.name, "name": node.name})
    return tests


def _scan_hooks(hooks_dir: Path) -> list[str]:
    """List React hook files (use*.ts)."""
    if not hooks_dir.is_dir():
        return []
    return sorted(
        f.stem for f in hooks_dir.glob("use*.ts") if not f.name.startswith("__")
    )


# ---------------------------------------------------------------------------
# Parity checks
# ---------------------------------------------------------------------------


def check_clause_coverage() -> dict[str, Any]:
    """Dimension 1: declared Indian-code capability-family coverage.

    The historical function name remains as a compatibility shim for callers;
    the returned metric is explicitly not clause coverage.
    """
    manifest = load_manifest()
    summary = manifest["capability_summary"]
    items = [
        {
            "capability_id": family["capability_id"],
            "standard": standard["namespace"],
            "family": family["family"],
            "scope_status": family["scope_status"],
            "implementation_status": family["implementation_status"],
            "claim": family["claim"],
        }
        for standard in manifest["standards"]
        for family in standard["capability_families"]
    ]
    return {
        "name": "Declared Indian-code Capability Families",
        "metric_kind": "DECLARED_CAPABILITY_FAMILY_COVERAGE",
        "claim_boundary": manifest["claim_boundaries"]["capability_status"],
        "informational": True,
        "gap_label": "Held (declared)",
        "supported": summary["supported_families"],
        "held": summary["held_families"],
        "total": summary["total_declared_families"],
        "pct": round(summary["supported_pct"]),
        "items": items,
        "missing_items": [
            f"{item['capability_id']}: {item['claim']}"
            for item in items
            if item["scope_status"] == "HELD"
        ],
    }


def check_api_endpoint_coverage() -> dict[str, Any]:
    """Dimension 2: public API functions used directly by FastAPI routers.

    This is an exposure metric, not a completeness gate. Many public library
    functions are intentionally available only to Python consumers or are
    composed by higher-level service functions before reaching a router.
    """
    api_funcs = _scan_public_functions(API_PY)

    # Build a set of "covered" API function names by looking for imports/references
    # in router files
    covered: set[str] = set()
    uncovered: list[str] = []

    router_text = ""
    if ROUTERS_DIR.is_dir():
        for py in ROUTERS_DIR.glob("*.py"):
            router_text += py.read_text() + "\n"

    for func in api_funcs:
        if func in router_text:
            covered.add(func)
        else:
            uncovered.append(func)

    total = len(api_funcs)
    covered_count = len(covered)
    return {
        "name": "Public API \u2192 Direct Router Wiring",
        "covered": covered_count,
        "library_only": len(uncovered),
        "total": total,
        "pct": round(covered_count / total * 100) if total else 0,
        "library_only_items": uncovered,
        "gap_label": "Library-only",
        "informational": True,
    }


def check_endpoint_test_coverage() -> dict[str, Any]:
    """Dimension 3: FastAPI endpoints → test coverage."""
    endpoints = _scan_router_endpoints(ROUTERS_DIR)
    test_funcs = _scan_test_functions(FASTAPI_TESTS)

    # Build lookup from router name to test coverage
    test_text = ""
    if FASTAPI_TESTS.is_dir():
        for py in FASTAPI_TESTS.glob("test_*.py"):
            test_text += py.read_text() + "\n"

    untested: list[dict[str, str]] = []

    for ep in endpoints:
        # Match literal paths and parameterized routes against concrete test
        # URLs (for example, ``/{bar_diameter}`` should match ``/16``).
        path_fragment = (
            ep["path"].strip("/").replace("/", "_").replace("{", "").replace("}", "")
        )
        route_pattern = re.escape(ep["path"])
        route_pattern = re.sub(r"\\\{[^{}]+\\\}", r"[^/\"'\\s?]+", route_pattern)
        if not (re.search(route_pattern, test_text) or path_fragment in test_text):
            untested.append(ep)

    total = len(endpoints)
    tested_count = total - len(untested)
    return {
        "name": "Endpoint \u2192 Test Coverage",
        "tested": tested_count,
        "missing": len(untested),
        "total": total,
        "pct": round(tested_count / total * 100) if total else 0,
        "test_count": len(test_funcs),
        "missing_items": [f"{e['method']} {e['path']}" for e in untested],
    }


def check_hook_api_coverage() -> dict[str, Any]:
    """Dimension 4: React hooks → API route connectivity."""
    hooks = [hook for hook in _scan_hooks(HOOKS_DIR) if hook not in LOCAL_ONLY_HOOKS]
    endpoints = _scan_router_endpoints(ROUTERS_DIR)

    # Build set of endpoint paths for rough matching
    endpoint_keywords: set[str] = set()
    for ep in endpoints:
        parts = ep["path"].strip("/").split("/")
        for part in parts:
            if not part.startswith("{"):
                endpoint_keywords.add(part.lower())

    connected: list[str] = []
    disconnected: list[str] = []

    # Read each hook file and check for fetch/api calls
    for hook_name in hooks:
        hook_file = HOOKS_DIR / f"{hook_name}.ts"
        if not hook_file.is_file():
            disconnected.append(hook_name)
            continue
        text = hook_file.read_text().lower()
        # Check for API call patterns: fetch, axios, /api/, endpoint paths
        has_api = any(
            pattern in text
            for pattern in [
                "/api/",
                "fetch(",
                "axios",
                "websocket",
                "usemutation",
                "usequery",
                "post(",
                ".get(",
            ]
        )
        if has_api:
            connected.append(hook_name)
        else:
            disconnected.append(hook_name)

    total = len(hooks)
    conn_count = len(connected)
    return {
        "name": "React Hook \u2192 API Coverage",
        "connected": conn_count,
        "missing": len(disconnected),
        "total": total,
        "pct": round(conn_count / total * 100) if total else 0,
        "missing_items": disconnected,
    }


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def _print_section(data: dict[str, Any], *, show_missing: bool = False) -> None:
    """Print a single parity section."""
    name = data["name"]
    pct = data["pct"]
    total = data["total"]

    # Determine numerator key
    if "supported" in data:
        num = data["supported"]
        label1 = "Supported"
    elif "implemented" in data:
        num = data["implemented"]
        label1 = "Implemented"
    elif "covered" in data:
        num = data["covered"]
        label1 = "Covered"
    elif "tested" in data:
        num = data["tested"]
        label1 = "Tested"
    elif "connected" in data:
        num = data["connected"]
        label1 = "Connected"
    else:
        num = 0
        label1 = "Done"

    gap = data.get(
        "missing",
        data.get("held", data.get("planned", data.get("library_only", total - num))),
    )

    print(f"  {name}")
    print("  \u2501" * 24)
    print(f"  {label1}:{num:>5}/{total}  ({pct}%)")
    gap_label = data.get(
        "gap_label",
        "Held" if "held" in data else "Planned" if "planned" in data else "Missing",
    )
    print(f"  {gap_label}:{gap:>6}/{total}  ({100 - pct}%)")
    print(f"  {_progress_bar(pct / 100)}  {pct}%")

    if show_missing:
        items = data.get("missing_items", [])
        if not items and "items" in data:
            items = [
                f"{it.get('clause', it.get('capability_id'))}: "
                f"{it.get('desc', it.get('claim'))}"
                for it in data["items"]
                if it.get("status") != "implemented"
                and it.get("scope_status") != "SUPPORTED"
            ]
        if items:
            print()
            for item in items[:15]:
                if isinstance(item, dict):
                    print(f"    \u2022 {item}")
                else:
                    print(f"    \u2022 {item}")
    print()


def _overall_score(sections: list[dict[str, Any]]) -> int | None:
    """Average actionable parity dimensions.

    Informational exposure metrics are displayed but do not lower the score.
    """
    actionable = [section for section in sections if not section.get("informational")]
    if not actionable:
        return None
    total_pct = sum(s["pct"] for s in actionable)
    return round(total_pct / len(actionable))


def run_dashboard(
    *,
    as_json: bool = False,
    section_filter: str | None = None,
    show_missing: bool = False,
) -> int:
    """Run all parity checks and display results."""

    checks = {
        "capabilities": check_clause_coverage,
        "api": check_api_endpoint_coverage,
        "tests": check_endpoint_test_coverage,
        "hooks": check_hook_api_coverage,
    }

    if section_filter:
        key = section_filter.lower()
        if key == "clauses":
            key = "capabilities"
        if key not in checks:
            print(f"Unknown section: {key}. Available: {', '.join(checks.keys())}")
            return 1
        checks = {key: checks[key]}

    results: list[dict[str, Any]] = []
    for _key, fn in checks.items():
        results.append(fn())

    if as_json:
        output = {
            "sections": results,
            "overall_pct": _overall_score(results),
            "overall_scope": (
                "Actionable non-informational cross-layer sections only; "
                "declared capability scope and public API exposure are excluded."
            ),
        }
        print(json.dumps(output, indent=2))
        return 0

    print()
    print("\U0001f4ca Parity Dashboard")
    print("\u2501" * 45)
    print()

    for section in results:
        _print_section(section, show_missing=show_missing)

    if len(results) > 1:
        score = _overall_score(results)
        print(f"  Actionable Cross-Layer Score: {score}%")
        print("  (Declared capability scope and API exposure are excluded.)")
    print("\u2501" * 45)
    print()
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Parity Dashboard")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument(
        "--section",
        type=str,
        default=None,
        help="Show single section: capabilities, api, tests, hooks (clauses is a legacy alias)",
    )
    parser.add_argument(
        "--missing", action="store_true", help="Show only gaps/missing items"
    )
    args = parser.parse_args()

    rc = run_dashboard(
        as_json=args.json, section_filter=args.section, show_missing=args.missing
    )
    sys.exit(rc)


if __name__ == "__main__":
    main()
