#!/usr/bin/env python3
"""CI failure diagnosis — check, reproduce, and fix CI failures locally.

Usage: python scripts/diagnose_ci.py [--pr N] [--last] [--local] [--fix]
Exit codes: 0=pass, 1=failure, 2=tool error
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VENV_PY = str(REPO_ROOT / ".venv" / "bin" / "python")
REACT_APP = str(REPO_ROOT / "react_app")

_DIRS = ["Python/", "fastapi_app/", "scripts/"]
LOCAL_CHECKS: list[dict] = [
    {
        "name": "Format Check (black)",
        "cmd": [VENV_PY, "-m", "black", "--check", "--quiet"] + _DIRS,
        "fix": [VENV_PY, "-m", "black"] + _DIRS,
    },
    {
        "name": "Ruff Lint",
        "cmd": [VENV_PY, "-m", "ruff", "check"] + _DIRS,
        "fix": [VENV_PY, "-m", "ruff", "check", "--fix"] + _DIRS,
    },
    {
        "name": "Python Tests",
        "cmd": [
            VENV_PY,
            "-m",
            "pytest",
            "Python/tests/",
            "-x",
            "-q",
            "--tb=short",
            "--no-header",
        ],
        "fix": None,
    },
    {
        "name": "Import Validation",
        "cmd": [VENV_PY, "scripts/validate_imports.py", "--scope", "structural_lib"],
        "fix": None,
    },
    {
        "name": "React Build",
        "cmd": ["npm", "run", "build", "--prefix", REACT_APP],
        "fix": None,
    },
    {
        "name": "Type Check (mypy)",
        "cmd": [
            VENV_PY,
            "-m",
            "mypy",
            "Python/structural_lib/",
            "--ignore-missing-imports",
            "--no-error-summary",
        ],
        "fix": None,
    },
]

CI_JOB_MAP = {
    "format": "Format Check (black)",
    "black": "Format Check (black)",
    "lint": "Ruff Lint",
    "ruff": "Ruff Lint",
    "test": "Python Tests",
    "pytest": "Python Tests",
    "import": "Import Validation",
    "build": "React Build",
    "react": "React Build",
    "mypy": "Type Check (mypy)",
    "type": "Type Check (mypy)",
}


def run_cmd(
    cmd: list[str], cwd: str | Path | None = None, timeout: int = 300
) -> tuple[int, str, str]:
    try:
        r = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=cwd or REPO_ROOT,
            timeout=timeout,
        )
        return r.returncode, r.stdout, r.stderr
    except FileNotFoundError:
        return 127, "", f"Command not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return 124, "", f"Timed out after {timeout}s"


def gh_ok() -> bool:
    return run_cmd(["gh", "auth", "status"])[0] == 0


def current_branch() -> str:
    rc, out, _ = run_cmd(["git", "branch", "--show-current"])
    return out.strip() if rc == 0 else "unknown"


def truncate(text: str, n: int = 20) -> str:
    lines = text.strip().splitlines()
    if len(lines) <= n:
        return text.strip()
    return "\n".join(lines[:n]) + f"\n   ... ({len(lines) - n} more lines)"


def _json(cmd: list[str]) -> list | dict | None:
    rc, out, _ = run_cmd(cmd)
    if rc != 0:
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return None


def ci_runs_for_pr(pr: int) -> list[dict]:
    data = _json(
        ["gh", "pr", "checks", str(pr), "--json", "name,state,completedAt,detailsUrl"]
    )
    return data if isinstance(data, list) else []


def ci_runs_for_branch(branch: str | None = None) -> list[dict]:
    cmd = [
        "gh",
        "run",
        "list",
        "--limit",
        "1",
        "--json",
        "databaseId,status,conclusion",
    ]
    if branch:
        cmd += ["--branch", branch]
    runs = _json(cmd)
    if not isinstance(runs, list) or not runs:
        return []
    data = _json(["gh", "run", "view", str(runs[0]["databaseId"]), "--json", "jobs"])
    if not isinstance(data, dict):
        return []
    return [
        {
            "name": j.get("name", "?"),
            "conclusion": j.get("conclusion", "?"),
            "status": j.get("status", "?"),
            "url": j.get("url", ""),
        }
        for j in data.get("jobs", [])
    ]


def latest_run_id(branch: str | None = None) -> int | None:
    cmd = ["gh", "run", "list", "--limit", "1", "--json", "databaseId"]
    if branch:
        cmd += ["--branch", branch]
    data = _json(cmd)
    if isinstance(data, list) and data:
        return data[0].get("databaseId")
    return None


def failed_logs(run_id: int | None = None) -> str:
    cmd = ["gh", "run", "view"]
    if run_id:
        cmd.append(str(run_id))
    cmd.append("--log-failed")
    rc, out, err = run_cmd(cmd, timeout=30)
    return (
        truncate(out, 30) if rc == 0 else f"(Could not fetch logs: {err.strip()[:100]})"
    )


def run_check(chk: dict, fix: bool = False) -> dict:
    name = chk["name"]
    cmd = chk["fix"] if (fix and chk["fix"]) else chk["cmd"]
    if cmd is None:
        return {"name": name, "passed": True, "skipped": True, "output": ""}
    rc, out, err = run_cmd(cmd)
    result = {"name": name, "passed": rc == 0, "output": (out + "\n" + err).strip()}
    if not result["passed"] and fix and chk["fix"] and cmd != chk["fix"]:
        frc, fo, fe = run_cmd(chk["fix"])
        result["fix_applied"] = frc == 0
    return result


def run_all_local(fix: bool = False) -> list[dict]:
    results = []
    for chk in LOCAL_CHECKS:
        print(f"  Running: {chk['name']}...", flush=True)
        results.append(run_check(chk, fix))
    return results


def _find_local(job_name: str) -> dict | None:
    low = job_name.lower()
    for kw, ln in CI_JOB_MAP.items():
        if kw in low:
            return next((c for c in LOCAL_CHECKS if c["name"] == ln), None)
    return None


def print_ci_report(jobs: list[dict], source: str) -> int:
    print(f"\n{'=' * 50}\n  CI Diagnosis Report \u2014 {source}\n{'=' * 50}\n")
    fails = 0
    for j in jobs:
        conc = j.get("conclusion", j.get("state", "?"))
        name = j.get("name", "?")
        if conc in ("success", "SUCCESS", "skipped", "SKIPPED"):
            print(f"  \u2705 PASSED: {name}")
        else:
            fails += 1
            print(f"  \u274c FAILED: {name}")
            chk = _find_local(name)
            if chk:
                print(f"   Reproduce: {' '.join(chk['cmd'][:4])}...")
                if chk["fix"]:
                    print("   Auto-fix: Run with --fix flag")
            url = j.get("url") or j.get("detailsUrl", "")
            if url:
                print(f"   Details: {url}")
            print()
    sep = "\u2500" * 50
    print(f"\n{sep}")
    print(f"  {fails} failed." if fails else "  All checks passed!")
    print()
    return fails


def print_local_report(results: list[dict], fix: bool = False) -> int:
    print(f"\n{'=' * 50}\n  Local CI Report{' (--fix)' if fix else ''}\n{'=' * 50}\n")
    fails = 0
    for r in results:
        if r.get("skipped"):
            print(f"  \u23ed\ufe0f  SKIPPED: {r['name']}")
        elif r["passed"]:
            print(f"  \u2705 PASSED: {r['name']}")
        else:
            fails += 1
            print(f"  \u274c FAILED: {r['name']}")
            for ln in truncate(r["output"], 15).splitlines():
                print(f"     {ln}")
            if r.get("fix_applied"):
                print("   \u2705 Auto-fix applied")
            elif r.get("fix_applied") is False:
                print("   \u274c Auto-fix failed")
            chk = next((c for c in LOCAL_CHECKS if c["name"] == r["name"]), None)
            if chk and chk["fix"] and not fix:
                print(f"   Fix: {' '.join(chk['fix'][:5])}...")
                print("   Auto-fix: Run with --fix flag")
            print()
    sep = "\u2500" * 50
    print(f"\n{sep}")
    print(f"  {fails} failed." if fails else "  All checks passed!")
    print()
    return fails


def _show_failed_logs(branch: str | None = None) -> None:
    rid = latest_run_id(branch)
    logs = failed_logs(rid)
    if logs and "(Could not" not in logs:
        print("  Failed job logs:\n")
        for ln in logs.splitlines():
            print(f"    {ln}")
        print()


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Diagnose CI failures \u2014 check remote status, reproduce locally, auto-fix.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
        "  %(prog)s                 Current branch CI\n"
        "  %(prog)s --pr 42         PR #42 CI\n"
        "  %(prog)s --local         Run checks locally\n"
        "  %(prog)s --local --fix   Auto-fix lint/format\n",
    )
    ap.add_argument("--pr", type=int, metavar="N", help="Check a specific PR's CI")
    ap.add_argument("--last", action="store_true", help="Last CI run on current branch")
    ap.add_argument("--local", action="store_true", help="Run all CI checks locally")
    ap.add_argument("--fix", action="store_true", help="Auto-fix formatting and lint")
    args = ap.parse_args()

    if args.local:
        print("Running all CI checks locally...")
        return 1 if print_local_report(run_all_local(args.fix), args.fix) else 0

    if not gh_ok():
        print("Error: gh CLI not available or not authenticated.", file=sys.stderr)
        print("Install: https://cli.github.com/  then: gh auth login", file=sys.stderr)
        if args.fix:
            print("\nFalling back to local checks with --fix...")
            return 1 if print_local_report(run_all_local(True), True) else 0
        return 2

    if args.pr:
        jobs = ci_runs_for_pr(args.pr)
        if not jobs:
            print(f"No CI checks found for PR #{args.pr}", file=sys.stderr)
            return 2
        fails = print_ci_report(jobs, f"PR #{args.pr}")
        if fails:
            _show_failed_logs()
        return 1 if fails else 0

    branch = current_branch()
    src = branch if args.last else None
    jobs = ci_runs_for_branch(src)
    if not jobs:
        print(f"No CI runs found for branch '{branch}'.", file=sys.stderr)
        print("Tip: Run with --local to check locally.", file=sys.stderr)
        return 2

    fails = print_ci_report(jobs, f"branch '{branch}'")
    if fails:
        _show_failed_logs(src)
        if args.fix:
            print("\nRunning auto-fixes...\n")
            print_local_report(run_all_local(True), True)
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
