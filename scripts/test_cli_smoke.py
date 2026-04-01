#!/usr/bin/env python3
"""CLI Smoke Tests — validate all key scripts work correctly.

Runs actual CLI commands via subprocess and checks exit codes / output.
Standalone script (not pytest) — can run in CI.

Usage:
    python scripts/test_cli_smoke.py              # Run all smoke tests
    python scripts/test_cli_smoke.py --json        # JSON output
    python scripts/test_cli_smoke.py --filter session  # Run matching tests
    python scripts/test_cli_smoke.py --verbose     # Show stdout/stderr
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
VENV = str(REPO_ROOT / ".venv" / "bin" / "python")

# ---------------------------------------------------------------------------
# Test definitions
# ---------------------------------------------------------------------------

SMOKE_TESTS: list[dict[str, Any]] = [
    # Session commands
    {
        "name": "session_start_fast",
        "cmd": [VENV, "scripts/session.py", "start", "--fast"],
        "expect_rc": 0,
        "expect_output": "SESSION START",
    },
    # Tool registry
    {
        "name": "tool_registry_list",
        "cmd": [VENV, "scripts/tool_registry.py", "--list"],
        "expect_rc": 0,
        "expect_output": "Agent",
    },
    {
        "name": "tool_registry_stats",
        "cmd": [VENV, "scripts/tool_registry.py", "--stats"],
        "expect_rc": 0,
    },
    {
        "name": "tool_registry_find",
        "cmd": [VENV, "scripts/tool_registry.py", "--find", "beam"],
        "expect_rc": 0,
    },
    # Prompt router
    {
        "name": "prompt_router_beam",
        "cmd": [VENV, "scripts/prompt_router.py", "design beam 300x500"],
        "expect_rc": 0,
        "expect_output": "Agent",
    },
    {
        "name": "prompt_router_json",
        "cmd": [VENV, "scripts/prompt_router.py", "--json", "fix test"],
        "expect_rc": 0,
    },
    # Permission tools
    {
        "name": "permissions_check_read",
        "cmd": [
            VENV,
            "scripts/tool_permissions.py",
            "check",
            "--agent",
            "reviewer",
            "--op",
            "read",
        ],
        "expect_rc": 0,
    },
    {
        "name": "permissions_audit",
        "cmd": [VENV, "scripts/audit_permissions.py"],
        "expect_rc": 0,
        "expect_output": "Permission",
    },
    # Pipeline state
    {
        "name": "pipeline_list",
        "cmd": [VENV, "scripts/pipeline_state.py", "list"],
        "expect_rc": 0,
    },
    # Session store
    {
        "name": "session_store_list",
        "cmd": [VENV, "scripts/session_store.py", "list"],
        "expect_rc": 0,
    },
    # Existing tools (regression)
    {
        "name": "find_automation",
        "cmd": [VENV, "scripts/find_automation.py", "beam"],
        "expect_rc": 0,
    },
    {
        "name": "discover_api",
        "cmd": [VENV, "scripts/discover_api_signatures.py", "design_beam_is456"],
        "expect_rc": 0,
    },
    # Session costs
    {
        "name": "session_costs",
        "cmd": [VENV, "scripts/session.py", "costs"],
        "expect_rc": 0,
    },
]

# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


def run_test(spec: dict[str, Any], *, verbose: bool = False) -> dict[str, Any]:
    """Run a single smoke test and return its result."""
    name = spec["name"]
    cmd = spec["cmd"]
    expect_rc = spec.get("expect_rc", 0)
    expect_output = spec.get("expect_output")

    t0 = time.monotonic()
    try:
        result = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        elapsed = time.monotonic() - t0
        rc = result.returncode
        stdout = result.stdout
        stderr = result.stderr
    except subprocess.TimeoutExpired:
        elapsed = time.monotonic() - t0
        return {
            "name": name,
            "passed": False,
            "elapsed": round(elapsed, 1),
            "reason": "Timed out (30s)",
            "stdout": "",
            "stderr": "",
        }
    except Exception as exc:
        elapsed = time.monotonic() - t0
        return {
            "name": name,
            "passed": False,
            "elapsed": round(elapsed, 1),
            "reason": str(exc),
            "stdout": "",
            "stderr": "",
        }

    passed = True
    reason = ""

    # Check return code
    if rc != expect_rc:
        passed = False
        reason = f"Exit code {rc}, expected {expect_rc}"

    # Check output substring
    if passed and expect_output:
        combined = stdout + stderr
        if expect_output not in combined:
            passed = False
            reason = f'Expected "{expect_output}" in output'

    entry: dict[str, Any] = {
        "name": name,
        "passed": passed,
        "elapsed": round(elapsed, 1),
        "reason": reason,
    }
    if verbose:
        entry["stdout"] = stdout
        entry["stderr"] = stderr

    return entry


def run_all(
    tests: list[dict[str, Any]],
    *,
    verbose: bool = False,
    as_json: bool = False,
    filter_str: str | None = None,
) -> int:
    """Run all smoke tests and print results. Returns 0 on all-pass, 1 otherwise."""

    # Filter
    if filter_str:
        tests = [t for t in tests if filter_str.lower() in t["name"].lower()]

    if not tests:
        print("No tests matched the filter.")
        return 1

    results: list[dict[str, Any]] = []
    total_start = time.monotonic()

    if not as_json:
        print("\n\U0001f9ea CLI Smoke Tests")
        print("\u2501" * 45)
        print()

    for spec in tests:
        entry = run_test(spec, verbose=verbose)
        results.append(entry)
        if not as_json:
            icon = "\u2705" if entry["passed"] else "\u274c"
            line = f"  {icon} {entry['name']:<30} ({entry['elapsed']}s)"
            if entry.get("reason"):
                line += f" \u2014 {entry['reason']}"
            print(line)
            if verbose and (entry.get("stdout") or entry.get("stderr")):
                for stream_name in ("stdout", "stderr"):
                    text = entry.get(stream_name, "")
                    if text:
                        for ln in text.strip().splitlines()[:10]:
                            print(f"      [{stream_name}] {ln}")

    total_elapsed = round(time.monotonic() - total_start, 1)
    passed_count = sum(1 for r in results if r["passed"])
    failed_count = len(results) - passed_count

    if as_json:
        output = {
            "tests": results,
            "summary": {
                "total": len(results),
                "passed": passed_count,
                "failed": failed_count,
                "elapsed_s": total_elapsed,
            },
        }
        print(json.dumps(output, indent=2))
    else:
        print()
        print("\u2501" * 45)
        print(
            f"  Passed: {passed_count}/{len(results)}   "
            f"Failed: {failed_count}   "
            f"Time: {total_elapsed}s"
        )
        print()

    return 0 if failed_count == 0 else 1


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="CLI Smoke Tests")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument(
        "--filter", type=str, default=None, help="Filter tests by name substring"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Show stdout/stderr for each test"
    )
    args = parser.parse_args()

    rc = run_all(
        SMOKE_TESTS,
        verbose=args.verbose,
        as_json=args.json,
        filter_str=args.filter,
    )
    sys.exit(rc)


if __name__ == "__main__":
    main()
