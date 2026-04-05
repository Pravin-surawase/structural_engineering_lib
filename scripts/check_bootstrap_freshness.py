#!/usr/bin/env python3
"""Check if bootstrap docs are stale compared to actual codebase.

When to use: After adding new React hooks, FastAPI endpoints, components, or
public API functions. Detects items that exist in code but are missing from
agent-bootstrap.md, copilot-instructions.md, or CLAUDE.md.

Usage:
    python scripts/check_bootstrap_freshness.py           # Check all
    python scripts/check_bootstrap_freshness.py --hooks    # React hooks only
    python scripts/check_bootstrap_freshness.py --routes   # FastAPI routes only
    python scripts/check_bootstrap_freshness.py --json     # Machine-readable output
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP_DOC = REPO_ROOT / "docs" / "getting-started" / "agent-bootstrap.md"
COPILOT_INSTRUCTIONS = REPO_ROOT / ".github" / "copilot-instructions.md"
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"


def _scan_react_hooks() -> set[str]:
    """Scan react_app/src/hooks/ for exported hook names."""
    hooks_dir = REPO_ROOT / "react_app" / "src" / "hooks"
    hooks: set[str] = set()
    if not hooks_dir.exists():
        return hooks
    for path in hooks_dir.glob("*.ts"):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for match in re.finditer(
            r"^export\s+(?:function|const)\s+(use\w+)", text, re.MULTILINE
        ):
            hooks.add(match.group(1))
    return hooks


def _scan_fastapi_routers() -> dict[str, int]:
    """Scan fastapi_app/routers/ for router files and endpoint counts."""
    routers_dir = REPO_ROOT / "fastapi_app" / "routers"
    routers: dict[str, int] = {}
    if not routers_dir.exists():
        return routers
    for path in sorted(routers_dir.glob("*.py")):
        if path.name.startswith("_"):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        count = len(
            re.findall(r"@router\.(get|post|put|delete|patch|websocket)\(", text)
        )
        if count > 0:
            name = path.stem
            routers[name] = count
    return routers


def _scan_react_components() -> set[str]:
    """Scan react_app/src/components/ for exported components."""
    comps_dir = REPO_ROOT / "react_app" / "src" / "components"
    components: set[str] = set()
    if not comps_dir.exists():
        return components
    for path in comps_dir.rglob("*.tsx"):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for match in re.finditer(
            r"^export\s+(?:default\s+)?(?:function|const)\s+([A-Z]\w+)",
            text,
            re.MULTILINE,
        ):
            components.add(match.group(1))
    return components


def _read_doc(path: Path) -> str:
    """Read a doc file, return empty string if missing."""
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def _extract_documented_hooks(text: str) -> set[str]:
    """Extract hook names mentioned in doc text (only real hooks, not stores)."""
    all_use = set(re.findall(r"`(use\w+)`", text))
    # Exclude Zustand stores and shorthand aliases
    return {h for h in all_use if not h.endswith("Store")}


def _extract_documented_routers(text: str) -> set[str]:
    """Extract router names from bootstrap doc router table."""
    names: set[str] = set()
    # Only match router names in the endpoint table (bold name | endpoint pattern)
    for match in re.finditer(
        r"\*\*(\w+)\*\*\s*\|\s*`?(?:POST|GET|PUT|DELETE|WS|PATCH)", text
    ):
        names.add(match.group(1))
    return names


def _extract_documented_components(text: str) -> set[str]:
    """Extract component names from doc text."""
    return set(re.findall(r"`([A-Z]\w+)`", text))


def check_hooks(bootstrap_text: str, json_mode: bool = False) -> list[dict]:
    """Check React hooks coverage."""
    actual = _scan_react_hooks()
    documented = _extract_documented_hooks(bootstrap_text)
    missing = sorted(actual - documented)
    # Only flag stale if the documented name doesn't match any prefix of actual hooks
    # OR the filename of a hook file (e.g. "useInsights" -> useInsights.ts)
    hooks_dir = REPO_ROOT / "react_app" / "src" / "hooks"
    hook_files = (
        {p.stem for p in hooks_dir.glob("*.ts")} if hooks_dir.exists() else set()
    )
    stale = []
    for name in sorted(documented - actual):
        if any(a.startswith(name) for a in actual):
            continue
        if name in hook_files:
            continue
        stale.append(name)

    issues = []
    for name in missing:
        issues.append({"type": "hook", "status": "undocumented", "name": name})
    for name in stale:
        issues.append({"type": "hook", "status": "stale_reference", "name": name})

    if not json_mode:
        if issues:
            print(
                f"\nReact Hooks: {len(actual)} actual, {len(documented & actual)} documented"
            )
            for issue in issues:
                if issue["status"] == "undocumented":
                    print(
                        f"  + {issue['name']} — exists in code but not in bootstrap docs"
                    )
                else:
                    print(f"  - {issue['name']} — in docs but not found in code")
        else:
            print(f"✓ React Hooks: {len(actual)} hooks, all documented")

    return issues


def check_routers(bootstrap_text: str, json_mode: bool = False) -> list[dict]:
    """Check FastAPI router coverage."""
    actual = _scan_fastapi_routers()
    documented = _extract_documented_routers(bootstrap_text)
    actual_names = set(actual.keys())
    total_endpoints = sum(actual.values())

    missing = sorted(actual_names - documented)
    stale = sorted(documented - actual_names)

    issues = []
    for name in missing:
        issues.append(
            {
                "type": "router",
                "status": "undocumented",
                "name": name,
                "endpoints": actual[name],
            }
        )
    for name in stale:
        issues.append({"type": "router", "status": "stale_reference", "name": name})

    if not json_mode:
        if issues:
            print(
                f"\nFastAPI Routers: {len(actual)} routers, {total_endpoints} endpoints"
            )
            for issue in issues:
                if issue["status"] == "undocumented":
                    print(
                        f"  + {issue['name']} ({issue['endpoints']} endpoints) — not in bootstrap docs"
                    )
                else:
                    print(f"  - {issue['name']} — in docs but router not found")
        else:
            print(
                f"✓ FastAPI Routers: {len(actual)} routers, {total_endpoints} endpoints, all documented"
            )

    return issues


def check_components(bootstrap_text: str, json_mode: bool = False) -> list[dict]:
    """Check React component coverage."""
    actual = _scan_react_components()
    documented = _extract_documented_components(bootstrap_text)
    # Only flag significant components (>3 char names, uppercase start)
    significant_actual = {c for c in actual if len(c) > 3}
    missing = sorted(significant_actual - documented)

    issues = []
    for name in missing:
        issues.append({"type": "component", "status": "undocumented", "name": name})

    if not json_mode:
        if issues:
            print(
                f"\nReact Components: {len(significant_actual)} actual, {len(documented & significant_actual)} documented"
            )
            # Only show first 10 to avoid noise
            shown = issues[:10]
            for issue in shown:
                print(f"  + {issue['name']} — exists in code but not in bootstrap docs")
            if len(issues) > 10:
                print(f"  ... and {len(issues) - 10} more")
        else:
            print(
                f"✓ React Components: {len(significant_actual)} components, all documented"
            )

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hooks", action="store_true", help="Check React hooks only")
    parser.add_argument(
        "--routes", action="store_true", help="Check FastAPI routes only"
    )
    parser.add_argument(
        "--components", action="store_true", help="Check React components only"
    )
    parser.add_argument(
        "--json", action="store_true", help="Machine-readable JSON output"
    )
    args = parser.parse_args()

    check_all = not (args.hooks or args.routes or args.components)

    # Read all bootstrap docs
    bootstrap = _read_doc(BOOTSTRAP_DOC)
    copilot = _read_doc(COPILOT_INSTRUCTIONS)
    claude = _read_doc(CLAUDE_MD)
    combined_text = "\n".join([bootstrap, copilot, claude])

    all_issues: list[dict] = []

    if not args.json:
        print("Bootstrap Doc Freshness Check")
        print("=" * 40)

    if check_all or args.hooks:
        all_issues.extend(check_hooks(combined_text, args.json))

    if check_all or args.routes:
        all_issues.extend(check_routers(combined_text, args.json))

    if check_all or args.components:
        all_issues.extend(check_components(combined_text, args.json))

    if args.json:
        result = {
            "total_issues": len(all_issues),
            "issues": all_issues,
        }
        print(json.dumps(result, indent=2))
    else:
        undocumented = [i for i in all_issues if i["status"] == "undocumented"]
        stale = [i for i in all_issues if i["status"] == "stale_reference"]
        print(
            f"\nSummary: {len(undocumented)} undocumented, {len(stale)} stale references"
        )

    return 1 if any(i["status"] == "stale_reference" for i in all_issues) else 0


if __name__ == "__main__":
    raise SystemExit(main())
