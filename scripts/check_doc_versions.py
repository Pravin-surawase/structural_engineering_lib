#!/usr/bin/env python3
"""
Doc Version Drift Check — Validate no stale version strings.

USAGE:
    python scripts/check_doc_versions.py          # Check against current version
    python scripts/check_doc_versions.py --fix    # Auto-fix with bump_version.py --sync-docs
    python scripts/check_doc_versions.py --ci     # Exit with error code if drift found

This script scans docs for version patterns and reports mismatches.
Used in CI to prevent stale docs from shipping.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
BUMP_SCRIPT = REPO_ROOT / "scripts" / "bump_version.py"

# Patterns to check for version drift
VERSION_PATTERNS = [
    # Pattern, file glob, description
    (r"Document Version: ([0-9]+\.[0-9]+\.[0-9]+)", "docs/**/*.md", "Document Version header"),
    (r"\*\*Document Version:\*\* ([0-9]+\.[0-9]+\.[0-9]+)", "docs/**/*.md", "Document Version (bold)"),
    (r"\*\*Version:\*\*\s*v?([0-9]+\.[0-9]+\.[0-9]+)", "docs/**/*.md", "Version header"),
    (r"\|\s*\*\*Current Release\*\*\s*\|\s*v?([0-9]+\.[0-9]+\.[0-9]+)", "docs/AI_CONTEXT_PACK.md", "AI_CONTEXT_PACK version table"),
    (r"\|\s*\*\*Current\*\*\s*\|\s*v?([0-9]+\.[0-9]+\.[0-9]+)", "docs/TASKS.md", "TASKS version table"),
    (r"\|\s*\*\*Current\*\*\s*\|\s*v?([0-9]+\.[0-9]+\.[0-9]+)", "docs/planning/next-session-brief.md", "next-session-brief version table"),
    (r"@v([0-9]+\.[0-9]+\.[0-9]+)", "docs/**/*.md", "Git tag reference"),
    (r"structural-lib-is456==([0-9]+\.[0-9]+\.[0-9]+)", "**/*.md", "PyPI pin"),
]

# Files to skip (always allowed to have old versions for historical context)
SKIP_FILES = [
    "CHANGELOG.md",
    "RELEASES.md",
    "SESSION_LOG.md",
    "docs/_archive/",
]


def read_current_version() -> str:
    """Read current version from pyproject.toml."""
    pyproject = REPO_ROOT / "Python" / "pyproject.toml"
    content = pyproject.read_text()
    match = re.search(r'^version = "([^"]+)"', content, re.MULTILINE)
    if match:
        return match.group(1)
    raise ValueError("Could not find version in pyproject.toml")


def should_skip(filepath: Path) -> bool:
    """Check if file should be skipped."""
    rel_path = str(filepath.relative_to(REPO_ROOT))
    for skip in SKIP_FILES:
        if skip in rel_path:
            return True
    return False


def find_version_drift(current_version: str) -> list:
    """Find all files with version drift."""
    issues = []

    for pattern, glob_pattern, description in VERSION_PATTERNS:
        for filepath in REPO_ROOT.glob(glob_pattern):
            if not filepath.is_file():
                continue
            if should_skip(filepath):
                continue

            try:
                content = filepath.read_text()
            except Exception:
                continue

            for match in re.finditer(pattern, content):
                found_version = match.group(1)
                if found_version != current_version:
                    rel_path = filepath.relative_to(REPO_ROOT)
                    issues.append({
                        "file": str(rel_path),
                        "pattern": description,
                        "found": found_version,
                        "expected": current_version,
                        "line": content[:match.start()].count("\n") + 1,
                    })

    return issues


def main():
    parser = argparse.ArgumentParser(description="Check for doc version drift")
    parser.add_argument("--fix", action="store_true", help="Auto-fix with bump_version.py --sync-docs")
    parser.add_argument("--ci", action="store_true", help="Exit with error code if drift found")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show all checked patterns")

    args = parser.parse_args()

    current = read_current_version()
    print(f"Current version: {current}")
    print()

    if args.verbose:
        print("Checking patterns:")
        for pattern, glob_pat, desc in VERSION_PATTERNS:
            print(f"  - {desc}: {glob_pat}")
        print()
        print("Skipping:")
        for skip in SKIP_FILES:
            print(f"  - {skip}")
        print()

    issues = find_version_drift(current)

    if not issues:
        print("✓ No version drift found")
        return 0

    print(f"✗ Found {len(issues)} version drift issue(s):")
    print()

    for issue in issues:
        print(f"  {issue['file']}:{issue['line']}")
        print(f"    Pattern: {issue['pattern']}")
        print(f"    Found: {issue['found']} (expected: {issue['expected']})")
        print()

    if args.fix:
        print("Attempting auto-fix with bump_version.py --sync-docs...")
        result = subprocess.run(
            [sys.executable, str(BUMP_SCRIPT), "--sync-docs"],
            capture_output=True, text=True
        )
        print(result.stdout)
        if result.returncode == 0:
            print("✓ Auto-fix complete. Re-run to verify.")
        else:
            print(f"✗ Auto-fix failed: {result.stderr}")
            return 1
        return 0

    if args.ci:
        print("CI mode: failing due to version drift.")
        print("Run: python scripts/check_doc_versions.py --fix")
        return 1

    print("To fix: python scripts/check_doc_versions.py --fix")
    print("Or run: python scripts/bump_version.py --sync-docs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
