#!/usr/bin/env python3
"""Pre-flight check — catch common mistakes BEFORE they happen.

Usage:
    .venv/bin/python scripts/preflight.py          # Run all checks
    .venv/bin/python scripts/preflight.py --fix     # Auto-fix what's possible

Checks:
    1. On correct branch (not detached HEAD)
    2. No uncommitted changes (warn, not block)
    3. .venv is active and correct
    4. No merge conflicts in progress
    5. Key files exist (run.sh, services/api.py, etc.)
    6. Port conflicts (8000, 5173)
"""

import os
import subprocess
import sys
import socket

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
DIM = "\033[2m"
BOLD = "\033[1m"
NC = "\033[0m"

passed = 0
warned = 0
failed = 0


def _run(cmd: list[str], cwd: str | None = None) -> tuple[int, str]:
    """Run command, return (returncode, stdout)."""
    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd=cwd or REPO_ROOT
    )
    return result.returncode, result.stdout.strip()


def _pass(msg: str) -> None:
    global passed
    passed += 1
    print(f"  {GREEN}✓{NC} {msg}")


def _warn(msg: str, fix: str = "") -> None:
    global warned
    warned += 1
    hint = f" {DIM}({fix}){NC}" if fix else ""
    print(f"  {YELLOW}⚠{NC} {msg}{hint}")


def _fail(msg: str, fix: str = "") -> None:
    global failed
    failed += 1
    hint = f" {DIM}({fix}){NC}" if fix else ""
    print(f"  {RED}✗{NC} {msg}{hint}")


def check_branch() -> None:
    """Ensure we're on a real branch, not detached HEAD."""
    rc, branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    if rc != 0:
        _fail("Not a git repository")
    elif branch == "HEAD":
        _fail("Detached HEAD — not on a branch", "git checkout main")
    else:
        _pass(f"On branch: {branch}")


def check_uncommitted() -> None:
    """Warn about uncommitted changes."""
    rc, status = _run(["git", "status", "--porcelain"])
    if status:
        count = len(status.strip().split("\n"))
        _warn(f"{count} uncommitted change(s)", "./run.sh commit 'type: msg'")
    else:
        _pass("Working tree clean")


def check_venv() -> None:
    """Ensure .venv exists and Python is correct."""
    venv_python = os.path.join(REPO_ROOT, ".venv", "bin", "python")
    if not os.path.isfile(venv_python):
        _fail(".venv/bin/python not found", "python3 -m venv .venv && .venv/bin/pip install -e Python/")
        return

    rc, version = _run([venv_python, "--version"])
    if rc == 0:
        _pass(f".venv active: {version}")
    else:
        _fail(".venv/bin/python broken", "rm -rf .venv && python3 -m venv .venv")


def check_merge_conflicts() -> None:
    """Detect unresolved merge conflicts."""
    rc, _ = _run(["git", "merge", "HEAD", "--no-commit", "--no-ff"], cwd=REPO_ROOT)
    # Instead check for conflict markers
    rc2, output = _run(
        ["git", "diff", "--check"],
    )
    if output and "conflict" in output.lower():
        _fail("Merge conflicts detected", "./scripts/recover_git_state.sh")
    else:
        # Also check for MERGE_HEAD
        merge_head = os.path.join(REPO_ROOT, ".git", "MERGE_HEAD")
        if os.path.exists(merge_head):
            _fail("Unfinished merge in progress", "./scripts/recover_git_state.sh")
        else:
            _pass("No merge conflicts")


def check_key_files() -> None:
    """Ensure critical files exist."""
    critical = [
        "run.sh",
        "Python/structural_lib/services/api.py",
        "Python/structural_lib/__init__.py",
        "fastapi_app/main.py",
        "react_app/package.json",
        "scripts/ai_commit.sh",
    ]
    missing = [f for f in critical if not os.path.exists(os.path.join(REPO_ROOT, f))]
    if missing:
        _fail(f"Missing critical files: {', '.join(missing)}")
    else:
        _pass(f"All {len(critical)} critical files present")


def check_port(port: int, service: str) -> None:
    """Check if a port is already in use."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.settimeout(1)
        result = sock.connect_ex(("127.0.0.1", port))
        if result == 0:
            _warn(f"Port {port} in use ({service})", f"lsof -i :{port}")
        else:
            _pass(f"Port {port} available ({service})")
    finally:
        sock.close()


def check_node_modules() -> None:
    """Ensure react_app/node_modules exists."""
    nm = os.path.join(REPO_ROOT, "react_app", "node_modules")
    if os.path.isdir(nm):
        _pass("react_app/node_modules installed")
    else:
        _warn("react_app/node_modules missing", "cd react_app && npm install")


def check_stub_not_modified() -> None:
    """Warn if the stub api.py was recently modified (common mistake)."""
    stub = os.path.join("Python", "structural_lib", "api.py")
    rc, log = _run(["git", "log", "-1", "--format=%cr", "--", stub])
    if rc == 0 and log:
        # If modified in last day, warn
        if "second" in log or "minute" in log or "hour" in log:
            _warn(
                f"Stub api.py was modified {log} — is this intentional?",
                "Real code is in services/api.py"
            )
        else:
            _pass("Stub api.py not recently modified")
    else:
        _pass("Stub api.py not recently modified")


def main() -> None:
    print(f"\n{BOLD}Pre-flight Check{NC}\n")

    check_branch()
    check_uncommitted()
    check_venv()
    check_merge_conflicts()
    check_key_files()
    check_port(8000, "FastAPI")
    check_port(5173, "React dev")
    check_node_modules()
    check_stub_not_modified()

    print()
    total = passed + warned + failed
    summary = f"{passed}/{total} passed"
    if warned:
        summary += f", {warned} warnings"
    if failed:
        summary += f", {RED}{failed} failed{NC}"
        print(f"{RED}{BOLD}Pre-flight FAILED{NC}: {summary}")
        sys.exit(1)
    elif warned:
        print(f"{YELLOW}{BOLD}Pre-flight OK (with warnings){NC}: {summary}")
    else:
        print(f"{GREEN}{BOLD}Pre-flight OK{NC}: {summary}")


if __name__ == "__main__":
    main()
