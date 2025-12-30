#!/usr/bin/env python3
"""
Pre-handoff documentation freshness checker.

Run before ending a session to catch stale docs:
    python scripts/check_handoff_ready.py

Auto-fix mode (updates counts/dates):
    python scripts/check_handoff_ready.py --fix
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Docs that should have today's date when modified
DATE_SENSITIVE_DOCS = [
    "docs/TASKS.md",
    "docs/SESSION_LOG.md",
    "docs/planning/next-session-brief.md",
]

# Docs that contain test counts
TEST_COUNT_DOCS = [
    "docs/TASKS.md",
    "docs/AI_CONTEXT_PACK.md",
    "docs/planning/v0.20-stabilization-checklist.md",
    "docs/RELEASES.md",
]

# Docs that contain version numbers
VERSION_DOCS = [
    "docs/TASKS.md",
    "docs/AI_CONTEXT_PACK.md",
    "docs/planning/next-session-brief.md",
]


def get_project_root() -> Path:
    """Get project root directory."""
    return Path(__file__).parent.parent


def get_current_version() -> str:
    """Get current version from pyproject.toml."""
    pyproject = get_project_root() / "Python" / "pyproject.toml"
    content = pyproject.read_text()
    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    return match.group(1) if match else "unknown"


def get_test_counts() -> tuple[int, int]:
    """Run pytest and get pass/skip counts."""
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/",
                "--tb=no",
                "--disable-warnings",
            ],
            cwd=get_project_root() / "Python",
            capture_output=True,
            text=True,
            timeout=120,
        )
        # Parse output like "1810 passed, 91 skipped in 12.34s"
        output = result.stdout + result.stderr
        match = re.search(r"(\d+) passed", output)
        passed = int(match.group(1)) if match else 0
        match = re.search(r"(\d+) skipped", output)
        skipped = int(match.group(1)) if match else 0
        return passed, skipped
    except Exception as e:
        print(f"  ⚠️  Could not run tests: {e}")
        return 0, 0


def check_date_freshness(fix: bool = False) -> list[str]:
    """Check if date-sensitive docs have recent dates."""
    issues = []
    today = datetime.now().strftime("%Y-%m-%d")
    root = get_project_root()

    for doc_path in DATE_SENSITIVE_DOCS:
        full_path = root / doc_path
        if not full_path.exists():
            continue

        content = full_path.read_text()

        # Check for "Updated" or "Date" field
        has_today = today in content

        if not has_today:
            # Find the most recent date in the doc
            dates = re.findall(r"20\d{2}-\d{2}-\d{2}", content)
            most_recent = max(dates) if dates else "no date found"
            issues.append(f"{doc_path}: Last date is {most_recent}, not today ({today})")

    return issues


def check_test_counts(fix: bool = False) -> list[str]:
    """Check if test counts in docs match actual."""
    issues = []
    root = get_project_root()

    print("  Running tests to get current counts...")
    passed, skipped = get_test_counts()

    if passed == 0:
        return ["Could not determine test counts (tests may have failed)"]

    expected_patterns = [
        rf"{passed}\s*(passed|pass)",
        rf"{skipped}\s*(skipped|skip)",
    ]

    for doc_path in TEST_COUNT_DOCS:
        full_path = root / doc_path
        if not full_path.exists():
            continue

        content = full_path.read_text()

        # Look for test count patterns
        found_passed = re.search(r"(\d+)\s*(passed|pass)", content)
        found_skipped = re.search(r"(\d+)\s*(skipped|skip)", content)

        if found_passed:
            doc_passed = int(found_passed.group(1))
            if doc_passed != passed:
                if fix:
                    content = re.sub(
                        r"(\d+)(\s*)(passed|pass)",
                        f"{passed}\\2\\3",
                        content,
                    )
                    full_path.write_text(content)
                    print(f"  ✅ Fixed {doc_path}")
                else:
                    issues.append(
                        f"{doc_path}: Shows {doc_passed} passed, actual is {passed}"
                    )

        if found_skipped:
            doc_skipped = int(found_skipped.group(1))
            if doc_skipped != skipped:
                if fix:
                    content = re.sub(
                        r"(\d+)(\s*)(skipped|skip)",
                        f"{skipped}\\2\\3",
                        content,
                    )
                    full_path.write_text(content)
                    print(f"  ✅ Fixed {doc_path}")
                else:
                    issues.append(
                        f"{doc_path}: Shows {doc_skipped} skipped, actual is {skipped}"
                    )

    return issues


def check_version_consistency(fix: bool = False) -> list[str]:
    """Check if version numbers are consistent across docs."""
    root = get_project_root()
    checker = root / "scripts" / "check_doc_versions.py"
    if not checker.exists():
        return []

    cmd = [sys.executable, str(checker)]
    if fix:
        cmd.append("--fix")
    cmd.append("--ci")

    result = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
    if result.returncode == 0:
        return []

    output = (result.stdout or "") + "\n" + (result.stderr or "")
    issues = []
    for line in output.splitlines():
        # Example line: "  docs/planning/next-session-brief.md:3"
        match = re.match(r"\s*(docs/[^:]+\.md:\d+)\s*$", line)
        if match:
            issues.append(f"Version drift: {match.group(1)}")

    return issues or ["Version drift detected (see scripts/check_doc_versions.py output)"]


def check_active_tasks() -> list[str]:
    """Check if TASKS.md Active section has any items."""
    issues = []
    root = get_project_root()
    tasks_path = root / "docs" / "TASKS.md"

    if not tasks_path.exists():
        return ["docs/TASKS.md not found"]

    content = tasks_path.read_text()

    # Check if Active section exists and has content
    active_match = re.search(
        r"## 🔴 Active\s*\n(.*?)(?=\n## |\Z)", content, re.DOTALL
    )
    if active_match:
        active_content = active_match.group(1)
        if "Nothing" in active_content or active_content.strip() == "":
            issues.append("TASKS.md: Active section is empty (update before handoff)")

    return issues


def check_session_log_entry() -> list[str]:
    """Check if SESSION_LOG has an entry for today."""
    issues = []
    root = get_project_root()
    log_path = root / "docs" / "SESSION_LOG.md"
    today = datetime.now().strftime("%Y-%m-%d")

    if not log_path.exists():
        return ["docs/SESSION_LOG.md not found"]

    content = log_path.read_text()

    if today not in content:
        issues.append(f"SESSION_LOG.md: No entry for today ({today})")

    return issues


def main():
    parser = argparse.ArgumentParser(
        description="Check documentation freshness before handoff"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix test counts where possible",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip running tests (faster, but can't verify counts)",
    )
    args = parser.parse_args()

    print("🔍 Pre-Handoff Documentation Check\n")
    print(f"   Current version: {get_current_version()}")
    print(f"   Date: {datetime.now().strftime('%Y-%m-%d')}\n")

    all_issues = []

    # Check 1: Date freshness
    print("📅 Checking date freshness...")
    issues = check_date_freshness(args.fix)
    all_issues.extend(issues)
    if not issues:
        print("   ✅ All date-sensitive docs look current")
    else:
        for issue in issues:
            print(f"   ⚠️  {issue}")

    # Check 2: Test counts
    if not args.skip_tests:
        print("\n🧪 Checking test counts...")
        issues = check_test_counts(args.fix)
        all_issues.extend(issues)
        if not issues:
            print("   ✅ Test counts are accurate")
        else:
            for issue in issues:
                print(f"   ⚠️  {issue}")

    # Check 3: Version consistency
    print("\n🏷️  Checking version consistency...")
    issues = check_version_consistency(args.fix)
    all_issues.extend(issues)
    if not issues:
        print("   ✅ Versions are consistent")
    else:
        for issue in issues:
            print(f"   ⚠️  {issue}")

    # Check 4: Active tasks
    print("\n📋 Checking TASKS.md...")
    issues = check_active_tasks()
    all_issues.extend(issues)
    if not issues:
        print("   ✅ Active section has content")
    else:
        for issue in issues:
            print(f"   ⚠️  {issue}")

    # Check 5: Session log
    print("\n📝 Checking SESSION_LOG.md...")
    issues = check_session_log_entry()
    all_issues.extend(issues)
    if not issues:
        print("   ✅ Has entry for today")
    else:
        for issue in issues:
            print(f"   ⚠️  {issue}")

    # Summary
    print("\n" + "=" * 50)
    if all_issues:
        print(f"❌ Found {len(all_issues)} issue(s) to fix before handoff:\n")
        for i, issue in enumerate(all_issues, 1):
            print(f"   {i}. {issue}")
        print("\nRun with --fix to auto-fix test counts.")
        return 1
    else:
        print("✅ All checks passed! Ready for handoff.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
