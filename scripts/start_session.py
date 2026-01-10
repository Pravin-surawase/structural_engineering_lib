#!/usr/bin/env python3
"""
Session Start Script — Run at the beginning of each coding session.

USAGE:
    python scripts/start_session.py          # Full session start
    python scripts/start_session.py --quick  # Skip test count check

This script:
1. Shows current version and branch
2. Checks if SESSION_LOG.md has today's entry (adds skeleton if not)
3. Shows Active tasks from TASKS.md
4. Runs handoff checks to verify docs are fresh
5. Shows any uncommitted changes
"""

import argparse
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).parent.parent
SESSION_LOG = REPO_ROOT / "docs" / "SESSION_LOG.md"
TASKS_MD = REPO_ROOT / "docs" / "TASKS.md"
PYPROJECT = REPO_ROOT / "Python" / "pyproject.toml"


def get_version() -> str:
    """Get current version from pyproject.toml."""
    try:
        content = PYPROJECT.read_text()
        match = re.search(r'^version = "([^"]+)"', content, re.MULTILINE)
        return match.group(1) if match else "unknown"
    except Exception:
        return "unknown"


def get_branch() -> str:
    """Get current git branch."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def get_uncommitted_status() -> str:
    """Get git status summary."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        lines = result.stdout.strip().split("\n") if result.stdout.strip() else []
        if not lines:
            return "Clean working tree"
        return f"{len(lines)} uncommitted change(s)"
    except Exception:
        return "Unable to check"


def check_session_log_entry() -> tuple[bool, str]:
    """Check if SESSION_LOG.md has an entry for today."""
    today = date.today()
    today_str = today.strftime("%Y-%m-%d")

    try:
        content = SESSION_LOG.read_text()
        if re.search(rf"^##\s+{re.escape(today_str)}\b", content, re.MULTILINE):
            return True, f"Entry exists for {today_str}"
        return False, f"No entry for {today_str}"
    except Exception as e:
        return False, f"Error reading SESSION_LOG: {e}"


def add_session_log_entry() -> bool:
    """Add a skeleton entry for today to SESSION_LOG.md."""
    today = date.today()
    today_str = today.strftime("%Y-%m-%d")

    skeleton_lines = [
        "",
        f"## {today_str} — Session",
        "",
        "### Summary",
        "-",
        "",
        "### PRs Merged",
        "| PR | Summary |",
        "|----|---------|",
        "| #XX | - |",
        "",
        "### Key Deliverables",
        "-",
        "",
        "### Notes",
        "-",
        "",
    ]

    try:
        content = SESSION_LOG.read_text()

        # Find the first "---" after the header section and insert after it
        # Header is typically: # Session Log\n\n> ...\n\n---
        lines = content.split("\n")
        insert_index = None

        for i, line in enumerate(lines):
            # Find the first "---" separator after any header content
            if line.strip() == "---" and i > 2:
                insert_index = i + 1
                break

        if insert_index is None:
            # Fallback: append after first blank line after header
            insert_index = 5

        # Insert the skeleton
        new_lines = lines[:insert_index] + skeleton_lines + lines[insert_index:]
        SESSION_LOG.write_text("\n".join(new_lines))
        return True
    except Exception as e:
        print(f"  Error adding entry: {e}")
        return False


def get_active_tasks() -> list[tuple[str, str, str]]:
    """Extract Active tasks from TASKS.md.

    Returns list of (task_id, description, status_hint) tuples.
    """
    try:
        content = TASKS_MD.read_text()

        # Find the Active section
        active_match = re.search(
            r"## 🔴 Active\s*\n(.*?)(?=\n## |\Z)", content, re.DOTALL
        )

        if not active_match:
            return [("", "No Active section found", "")]

        active_section = active_match.group(1)

        # Extract task IDs and descriptions from table rows
        tasks = []
        for line in active_section.split("\n"):
            # Match table rows like "| **S-007** | External engineer CLI test | CLIENT | ⏳ Waiting |"
            match = re.match(
                r"\|\s*\*\*([^*]+)\*\*\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)", line
            )
            if match:
                task_id = match.group(1).strip()
                task_desc = match.group(2).strip()
                status = match.group(4).strip()
                # Detect if this is a blocker (requires human, waiting, etc.)
                hint = ""
                status_lower = status.lower()
                if (
                    "human" in status_lower
                    or "waiting" in status_lower
                    or "manual" in status_lower
                ):
                    hint = "BLOCKER - requires human"
                elif "⏳" in status:
                    hint = "waiting"
                tasks.append((task_id, task_desc, hint))

        return tasks if tasks else [("", "No active tasks in table", "")]
    except Exception as e:
        return [("", f"Error reading TASKS.md: {e}", "")]


def get_key_blocker() -> Optional[str]:
    """Get the key blocker from active tasks (if any)."""
    tasks = get_active_tasks()
    for task_id, desc, hint in tasks:
        if "BLOCKER" in hint:
            return f"{task_id}: {desc}"
    return None


def run_handoff_check(skip_tests: bool = True) -> tuple[bool, str]:
    """Run the handoff checker."""
    check_script = REPO_ROOT / "scripts" / "check_handoff_ready.py"
    if not check_script.exists():
        return True, "Handoff checker not found (skipping)"

    venv_python = REPO_ROOT / ".venv" / "bin" / "python"
    python_exe = str(venv_python) if venv_python.exists() else sys.executable

    cmd = [python_exe, str(check_script)]
    if skip_tests:
        cmd.append("--skip-tests")

    try:
        result = subprocess.run(
            cmd,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=60 if skip_tests else 240,
        )

        output = (result.stdout or "") + "\n" + (result.stderr or "")

        # Check for pass/fail in output
        if "All checks passed" in output:
            return True, "All handoff checks passed"
        else:
            # Extract issues
            issues = []
            for line in output.split("\n"):
                if "❌" in line or "⚠️" in line:
                    issues.append(line.strip())
            return False, "\n".join(issues) if issues else "Some checks failed"
    except Exception as e:
        return False, f"Error running handoff check: {e}"


def main():
    parser = argparse.ArgumentParser(description="Start a coding session")
    parser.add_argument(
        "--quick", action="store_true", help="Skip test count verification"
    )
    parser.add_argument(
        "--no-add", action="store_true", help="Don't add SESSION_LOG entry"
    )
    args = parser.parse_args()

    version = get_version()
    branch = get_branch()
    uncommitted = get_uncommitted_status()

    print()
    print("=" * 60)
    print("🚀 SESSION START")
    print("=" * 60)
    print()
    print(f"  Version:  v{version}")
    print(f"  Branch:   {branch}")
    print(f"  Date:     {date.today().strftime('%Y-%m-%d')}")
    print(f"  Git:      {uncommitted}")
    print()

    # Check/add SESSION_LOG entry
    print("📝 Session Log:")
    has_entry, entry_msg = check_session_log_entry()
    if has_entry:
        print(f"  ✅ {entry_msg}")
    else:
        print(f"  ⚠️  {entry_msg}")
        if not args.no_add:
            print("  📝 Adding skeleton entry...")
            if add_session_log_entry():
                print("  ✅ Entry added to SESSION_LOG.md")
            else:
                print("  ❌ Failed to add entry")
    print()

    # Show active tasks with blocker detection
    print("📋 Active Tasks:")
    tasks = get_active_tasks()
    for task_id, desc, hint in tasks:
        if task_id:
            if hint:
                print(f"  • {task_id}: {desc} ({hint})")
            else:
                print(f"  • {task_id}: {desc}")
        else:
            print(f"  • {desc}")

    # Show key blocker prominently
    blocker = get_key_blocker()
    if blocker:
        print()
        print(f"  ⚠️  Key Blocker: {blocker}")
    print()

    # Run handoff checks
    print("🔍 Doc Freshness:")
    passed, check_msg = run_handoff_check(skip_tests=args.quick)
    if passed:
        print(f"  ✅ {check_msg}")
    else:
        for line in check_msg.split("\n"):
            print(f"  {line}")
    print()

    # Suggested action based on blocker
    print("=" * 60)
    if blocker:
        print(f"⚠️  Blocker detected: {blocker}")
        print("   → Ask user to resolve, or pick from Up Next in TASKS.md")
    else:
        print("Ready to work! Pick a task from Active or Up Next.")
    print()
    print("📖 Read first: docs/handoff.md → docs/agent-bootstrap.md → docs/ai-context-pack.md")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
