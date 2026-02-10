#!/usr/bin/env python3
"""
Session End Script — Run before ending each coding session.

USAGE:
    python scripts/end_session.py          # Full end-of-session checks
    python scripts/end_session.py --fix    # Auto-fix what can be fixed
    python scripts/end_session.py --quick  # Skip test count verification

This script:
1. Runs handoff checker (date freshness, test counts, versions)
2. Checks for uncommitted changes
3. Prompts to update SESSION_LOG if incomplete
4. Verifies no broken links in docs
5. Shows summary of what was accomplished
"""

import argparse
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SESSION_LOG = REPO_ROOT / "docs" / "SESSION_LOG.md"


def get_uncommitted_changes() -> list[str]:
    """Get list of uncommitted files."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        if not result.stdout.strip():
            return []
        return [line.strip() for line in result.stdout.strip().split("\n")]
    except Exception:
        return []


def check_session_log_complete() -> tuple[bool, list[str]]:
    """Check if today's SESSION_LOG entry looks complete."""
    today = date.today()
    today_str = today.strftime("%Y-%m-%d")
    today_display = today.strftime("%B %d, %Y")

    issues = []

    try:
        content = SESSION_LOG.read_text()

        if today_str not in content and today_display not in content:
            issues.append("No entry for today")
            return False, issues

        # Find today's section and check for placeholders
        lines = content.split("\n")
        in_today = False
        has_focus = False
        has_completed = False

        for line in lines:
            if today_str in line or today_display in line:
                in_today = True
            elif in_today and line.startswith("## Session:"):
                break  # Next session
            elif in_today:
                if "**Focus:**" in line and "<!--" not in line:
                    if len(line.split("**Focus:**")[1].strip()) > 5:
                        has_focus = True
                if "**Completed:**" in line:
                    has_completed = True
                if (
                    has_completed
                    and line.strip().startswith("-")
                    and len(line.strip()) > 2
                ):
                    if "<!--" not in line:
                        has_completed = True

        if not has_focus:
            issues.append("SESSION_LOG: Focus not filled in")
        if not has_completed:
            issues.append("SESSION_LOG: No completed items listed")

        return len(issues) == 0, issues
    except Exception as e:
        return False, [f"Error reading SESSION_LOG: {e}"]


def run_handoff_checker(
    fix: bool = False, skip_tests: bool = False
) -> tuple[bool, str]:
    """Run the handoff checker script."""
    check_script = REPO_ROOT / "scripts" / "check_handoff_ready.py"
    if not check_script.exists():
        return True, "Handoff checker not found"

    venv_python = REPO_ROOT / ".venv" / "bin" / "python"
    python_exe = str(venv_python) if venv_python.exists() else sys.executable

    cmd = [python_exe, str(check_script)]
    if fix:
        cmd.append("--fix")
    if skip_tests:
        cmd.append("--skip-tests")

    try:
        result = subprocess.run(
            cmd,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )

        if "All checks passed" in result.stdout:
            return True, "All handoff checks passed"
        else:
            return False, result.stdout
    except Exception as e:
        return False, f"Error: {e}"


def run_handoff_update() -> tuple[bool, str]:
    """Update next-session-brief.md from the latest SESSION_LOG entry."""
    update_script = REPO_ROOT / "scripts" / "update_handoff.py"
    if not update_script.exists():
        return True, "Handoff updater not found (skipping)"

    venv_python = REPO_ROOT / ".venv" / "bin" / "python"
    python_exe = str(venv_python) if venv_python.exists() else sys.executable

    try:
        result = subprocess.run(
            [python_exe, str(update_script)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            return True, "Updated next-session-brief.md handoff block"
        output = result.stdout.strip() or result.stderr.strip()
        return False, output or "Handoff updater failed"
    except Exception as e:
        return False, f"Error: {e}"


def check_links() -> tuple[bool, str]:
    """Run link checker if available."""
    link_script = REPO_ROOT / "scripts" / "check_links.py"
    if not link_script.exists():
        return True, "Link checker not found (skipping)"

    venv_python = REPO_ROOT / ".venv" / "bin" / "python"
    python_exe = str(venv_python) if venv_python.exists() else sys.executable

    try:
        result = subprocess.run(
            [python_exe, str(link_script)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            return True, "All doc links valid"
        else:
            # Extract broken links
            broken = []
            for line in result.stdout.split("\n"):
                if "BROKEN" in line or "❌" in line:
                    broken.append(line.strip())
            return False, f"{len(broken)} broken link(s) found"
    except Exception as e:
        return True, f"Link check skipped: {e}"


def get_changed_doc_folders() -> list[Path]:
    """Get list of docs/ folders that had file changes (staged or modified)."""
    try:
        # Get changed files from git
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~5", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )

        changed_files = (
            result.stdout.strip().split("\n") if result.stdout.strip() else []
        )

        # Also check uncommitted changes
        result2 = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        for line in result2.stdout.strip().split("\n"):
            if line.strip():
                # Extract filename from status line
                parts = line.strip().split(maxsplit=1)
                if len(parts) > 1:
                    changed_files.append(parts[1])

        # Filter to docs/ folders and get unique parent folders
        doc_folders = set()
        for f in changed_files:
            if f.startswith("docs/") and f.endswith(".md"):
                folder = Path(f).parent
                # Only consider folders with significant depth
                if len(folder.parts) >= 2:
                    doc_folders.add(REPO_ROOT / folder)

        return list(doc_folders)
    except Exception:
        return []


def update_folder_readmes(folders: list[Path], fix: bool = False) -> int:
    """Update README.md for specified folders using generate_folder_index.py."""
    if not fix:
        return 0

    gen_script = REPO_ROOT / "scripts" / "generate_folder_index.py"
    if not gen_script.exists():
        return 0

    venv_python = REPO_ROOT / ".venv" / "bin" / "python"
    python_exe = str(venv_python) if venv_python.exists() else sys.executable

    updated = 0
    for folder in folders:
        if not folder.exists():
            continue
        try:
            # Check if folder has enough files to warrant an index
            md_files = list(folder.glob("*.md"))
            if len(md_files) < 3:
                continue

            result = subprocess.run(
                [python_exe, str(gen_script), str(folder)],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                updated += 1
        except Exception:
            pass

    return updated


def get_today_prs() -> list[str]:
    """Get PRs merged today (from git log)."""
    try:
        today = date.today().strftime("%Y-%m-%d")
        result = subprocess.run(
            ["git", "log", "--oneline", f"--since={today}", "--merges", "-n", "10"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        if not result.stdout.strip():
            # Try non-merge commits
            result = subprocess.run(
                ["git", "log", "--oneline", f"--since={today}", "-n", "10"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )

        lines = result.stdout.strip().split("\n") if result.stdout.strip() else []
        return [line for line in lines if line][:5]  # Max 5
    except Exception:
        return []


def main():
    parser = argparse.ArgumentParser(description="End-of-session checks")
    parser.add_argument(
        "--fix", action="store_true", help="Auto-fix issues where possible"
    )
    parser.add_argument(
        "--quick", action="store_true", help="Skip test count verification"
    )
    args = parser.parse_args()

    print()
    print("=" * 60)
    print("🏁 SESSION END CHECK")
    print("=" * 60)
    print()

    all_passed = True

    # 1. Uncommitted changes
    print("📁 Uncommitted Changes:")
    uncommitted = get_uncommitted_changes()
    if uncommitted:
        print(f"  ⚠️  {len(uncommitted)} uncommitted file(s):")
        for f in uncommitted[:5]:
            print(f"     {f}")
        if len(uncommitted) > 5:
            print(f"     ... and {len(uncommitted) - 5} more")
        all_passed = False
    else:
        print("  ✅ Working tree clean")
    print()

    # 2. Handoff checks
    if args.fix:
        print("🧭 Handoff Brief:")
        passed, msg = run_handoff_update()
        if passed:
            print(f"  ✅ {msg}")
        else:
            print(f"  ⚠️  {msg}")
            all_passed = False
        print()

    # 2. Handoff checks
    print("🔍 Handoff Checks:")
    passed, msg = run_handoff_checker(fix=args.fix, skip_tests=args.quick)
    if passed:
        print(f"  ✅ {msg}")
    else:
        print("  ⚠️  Issues found:")
        for line in msg.split("\n"):
            if line.strip():
                print(f"     {line}")
        all_passed = False
    print()

    # 3. Session log completeness
    print("📝 Session Log:")
    complete, issues = check_session_log_complete()
    if complete:
        print("  ✅ Today's entry looks complete")
    else:
        for issue in issues:
            print(f"  ⚠️  {issue}")
        all_passed = False
    print()

    # 4. Link check
    print("🔗 Doc Links:")
    passed, msg = check_links()
    if passed:
        print(f"  ✅ {msg}")
    else:
        print(f"  ⚠️  {msg}")
    print()

    # 4.5 README Auto-Update (NEW - Session 19P12)
    print("📚 README Index Updates:")
    changed_folders = get_changed_doc_folders()
    if changed_folders:
        print(f"  📂 {len(changed_folders)} folder(s) with changes detected")
        updated = update_folder_readmes(changed_folders, fix=args.fix)
        if args.fix and updated:
            print(f"  ✅ Updated {updated} README file(s)")
        elif not args.fix:
            print("  ℹ️  Run with --fix to auto-update READMEs")
    else:
        print("  ✅ No doc folder changes detected")
    print()

    # 5. Governance compliance check (NEW - Session 12)
    print("📋 Governance Compliance:")
    gov_script = REPO_ROOT / "scripts" / "check_governance.py"
    if gov_script.exists():
        venv_python = REPO_ROOT / ".venv" / "bin" / "python"
        python_exe = str(venv_python) if venv_python.exists() else sys.executable
        try:
            result = subprocess.run(
                [python_exe, str(gov_script)],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                print("  ✅ All governance checks passed")
            else:
                # Extract issues count
                critical = result.stdout.count("CRITICAL")
                high = result.stdout.count("HIGH")
                if critical > 0:
                    print(f"  🔴 {critical} CRITICAL issue(s) found")
                    all_passed = False
                if high > 0:
                    print(f"  🟠 {high} HIGH severity issue(s)")
                if critical == 0 and high == 0:
                    print("  ✅ Only minor issues (MEDIUM/LOW)")
        except Exception as e:
            print(f"  ⚠️  Could not run governance check: {e}")
    else:
        print("  ⏭️  Governance checker not found (skipping)")
    print()

    # 6. Today's activity summary
    print("📊 Today's Activity:")
    prs = get_today_prs()
    if prs:
        for pr in prs:
            print(f"  • {pr}")
    else:
        print("  (No commits today)")
    print()

    # Final status
    print("=" * 60)
    if all_passed:
        print("✅ All checks passed! Safe to end session.")
    else:
        print("⚠️  Some issues found. Consider fixing before handoff.")
        if not args.fix:
            print("   Run with --fix to auto-fix what's possible.")
        print()
        print("💡 Tip: Collect diagnostics for troubleshooting:")
        print("   .venv/bin/python scripts/collect_diagnostics.py > diagnostics.txt")
    print("=" * 60)
    print()

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
