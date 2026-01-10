#!/usr/bin/env python3
"""
Version Bump Script — Single Source of Truth

This script updates version numbers across the codebase from ONE location.

USAGE:
    python scripts/bump_version.py 0.9.2
    python scripts/bump_version.py 0.10.0 --dry-run
    python scripts/bump_version.py --sync-docs

The single source of truth is Python/pyproject.toml.
This script updates all other files that need the version.
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path

# Root of the repository
REPO_ROOT = Path(__file__).parent.parent

# Files that need version updates (relative to repo root)
# MINIMAL SET: Only files that MUST have hardcoded versions
# Core version pins (required)
VERSION_FILES = {
    # Python source of truth (packaging)
    "Python/pyproject.toml": [
        (r'^version = "[^"]+"', 'version = "{version}"'),
    ],

    # Python fallback for dev mode (when package not installed)
    "Python/structural_lib/api.py": [
        (r'return "[0-9]+\.[0-9]+\.[0-9]+"', 'return "{version}"'),
    ],

    # VBA runtime (VBA can't read external files)
    "VBA/Modules/M08_API.bas": [
        (r'Get_Library_Version = "[^"]+"', 'Get_Library_Version = "{version}"'),
    ],
}

# Documentation references that should track the library version.
DOC_VERSION_FILES = {
    "README.md": [
        (r"structural-lib-is456==[0-9]+\.[0-9]+\.[0-9]+", "structural-lib-is456=={version}"),
        (r"^🚀 \*\*Active \(v[0-9]+\.[0-9]+\.[0-9]+\)\*\*", "🚀 **Active (v{version})**"),
        (r"^\*\*What's new in v[0-9]+\.[0-9]+\.[0-9]+:\*\*", "**What's new in v{version}:**"),
    ],
    "Python/README.md": [
        (r"^\*\*Version:\*\* [0-9]+\.[0-9]+\.[0-9]+", "**Version:** {version}"),
        (r"@v[0-9]+\.[0-9]+\.[0-9]+", "@v{version}"),
        (r"^## New in v[0-9]+\.[0-9]+\.[0-9]+", "## New in v{version}"),
    ],
    "docs/README.md": [
        # Now links to TASKS.md, no version to update
    ],
    "docs/ai-context-pack.md": [
        (r"^\|\s*\*\*Current Release\*\*\s*\|\s*v[0-9]+\.[0-9]+\.[0-9]+", "| **Current Release** | v{version}"),
    ],
    "docs/planning/production-roadmap.md": [
        (r"^(> \*\*Current Status:\*\* )v[0-9]+\.[0-9]+\.[0-9]+", r"\g<1>v{version}"),
    ],
    "docs/planning/current-state-and-goals.md": [
        (r"^(Current release tag: )v[0-9]+\.[0-9]+\.[0-9]+", r"\g<1>v{version}"),
    ],
    "docs/getting-started/python-quickstart.md": [
        (r"@v[0-9]+\.[0-9]+\.[0-9]+", "@v{version}"),
    ],
    "docs/contributing/vba-testing-guide.md": [
        (r"^\*\*Version:\*\* [0-9]+\.[0-9]+\.[0-9]+", "**Version:** {version}"),
        (r"(Version: )[0-9]+\.[0-9]+\.[0-9]+", r"\g<1>{version}"),
    ],
    "docs/reference/api.md": [
        (r"^\*\*Document Version:\*\* [0-9]+\.[0-9]+\.[0-9]+", "**Document Version:** {version}"),
    ],
    "docs/getting-started/user-guide.md": [
        (r"^\*\*Version:\*\* [0-9]+\.[0-9]+\.[0-9]+", "**Version:** {version}"),
    ],
    "docs/planning/pre-release-checklist.md": [
        (r"^(Version: )[0-9]+\.[0-9]+\.[0-9]+(.*)$", r"\g<1>{version}\g<2>"),
    ],
    "docs/reference/api-stability.md": [
        (r"structural-lib-is456==[0-9]+\.[0-9]+\.[0-9]+", "structural-lib-is456=={version}"),
    ],
    "docs/verification/validation-pack.md": [
        (r"^\*\*Version:\*\* [0-9]+\.[0-9]+\.[0-9]+", "**Version:** {version}"),
    ],
    "docs/verification/examples.md": [
        (r"^\*\*Version:\*\* [0-9]+\.[0-9]+\.[0-9]+", "**Version:** {version}"),
    ],
    "docs/TASKS.md": [
        (r"^\|\s*\*\*Current\*\*\s*\|\s*v[0-9]+\.[0-9]+\.[0-9]+", "| **Current** | v{version}"),
    ],
    "docs/planning/next-session-brief.md": [
        (r"^\|\s*\*\*Current\*\*\s*\|\s*v[0-9]+\.[0-9]+\.[0-9]+", "| **Current** | v{version}"),
    ],
    "docs/planning/v0.20-stabilization-checklist.md": [
        # Now links to TASKS.md, no version to update
    ],
}

# Documentation "Last Updated" stamps (normalized to YYYY-MM-DD).
DOC_DATE_FILES = {
    "docs/planning/research-ai-enhancements.md": [
        (r"^\*\*Last Updated:\*\* .+", "**Last Updated:** {date}<br>"),
    ],
    "docs/planning/next-session-brief.md": [
        (r"^\*\*Last Updated:\*\* .+", "**Last Updated:** {date}<br>"),
    ],
    "docs/reference/api.md": [
        (r"^\*\*Document Version:\*\* [0-9]+\.[0-9]+\.[0-9]+", "**Document Version:** {version}"),
        (r"^\*\*Last Updated:\*\* .+", "**Last Updated:** {date}<br>"),
    ],
    "docs/verification/examples.md": [
        (r"^\*\*Last Updated:\*\* .+", "**Last Updated:** {date}<br>"),
    ],
    "docs/TASKS.md": [
        (r"^- \*\*Last Updated\*\*: .+", "- **Last Updated**: {date}"),
    ],
    "docs/getting-started/beginners-guide.md": [
        (r"(Document Version: )[0-9]+\.[0-9]+\.[0-9]+", r"\g<1>{version}"),
        (r"(Last Updated: ).+", r"\g<1>{date}"),
    ],
    "docs/getting-started/excel-tutorial.md": [
        (r"(Document Version: )[0-9]+\.[0-9]+\.[0-9]+", r"\g<1>{version}"),
        (r"(Last Updated: ).+", r"\g<1>{date}"),
    ],
    "docs/contributing/vba-testing-guide.md": [
        (r"^\*\*Last Updated:\*\* .+", "**Last Updated:** {date}<br>"),
    ],
    "docs/contributing/development-guide.md": [
        (r"^\*\*Document Version:\*\* [0-9]+\.[0-9]+\.[0-9]+", "**Document Version:** {version}"),
        (r"^\*\*Last Updated:\*\* .+", "**Last Updated:** {date}<br>"),
    ],
    "docs/planning/pre-release-checklist.md": [
        (r"^(Date: ).+", r"\g<1>{date}"),
    ],
}

# Files where version should be REMOVED or made evergreen
EVERGREEN_NOTES = """
Version is managed in these files:
  - Python/pyproject.toml (source of truth)
  - Python/api.py (dev mode fallback)
  - VBA/M08_API.bas (VBA runtime)

Doc references are synced via: python scripts/bump_version.py --sync-docs
"""


def read_current_version() -> str:
    """Read current version from pyproject.toml."""
    pyproject = REPO_ROOT / "Python" / "pyproject.toml"
    content = pyproject.read_text()
    match = re.search(r'^version = "([^"]+)"', content, re.MULTILINE)
    if match:
        return match.group(1)
    raise ValueError("Could not find version in pyproject.toml")


def update_file(
    filepath: Path, patterns: list, format_kwargs: dict, dry_run: bool
) -> bool:
    """Update version patterns in a file. Returns True if changes made."""
    if not filepath.exists():
        print(f"  SKIP (not found): {filepath}")
        return False

    content = filepath.read_text()
    original = content

    for pattern, replacement in patterns:
        replacement_str = replacement.format(**format_kwargs)
        content = re.sub(pattern, replacement_str, content, flags=re.MULTILINE)

    if content != original:
        if dry_run:
            print(f"  WOULD UPDATE: {filepath}")
        else:
            filepath.write_text(content)
            print(f"  UPDATED: {filepath}")
        return True
    else:
        print(f"  (no change): {filepath}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Bump version across codebase")
    parser.add_argument("version", nargs="?", help="New version (e.g., 0.9.2)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change")
    parser.add_argument("--current", action="store_true", help="Show current version")
    parser.add_argument(
        "--sync-docs",
        action="store_true",
        help="Sync doc version references to the current version",
    )
    parser.add_argument(
        "--sync-dates",
        action="store_true",
        help="Sync doc 'Last Updated' stamps to today's date",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Print the version/log update checklist",
    )
    parser.add_argument(
        "--check-docs",
        action="store_true",
        help="Fail if doc version references are out of sync",
    )

    args = parser.parse_args()

    current = read_current_version()

    if args.current:
        print(f"Current version: {current}")
        return 0

    if args.report:
        print("Version update checklist")
        print()
        print("Core version pins:")
        for rel_path in VERSION_FILES:
            print(f"  - {rel_path}")
        print()
        print("Doc version references:")
        for rel_path in DOC_VERSION_FILES:
            print(f"  - {rel_path}")
        print()
        print("Doc last-updated stamps:")
        for rel_path in DOC_DATE_FILES:
            print(f"  - {rel_path}")
        print()
        print("Release logs (manual):")
        print("  - CHANGELOG.md")
        print("  - docs/releases.md")
        print("  - docs/SESSION_LOG.md")
        return 0

    today = date.today().isoformat()

    if args.check_docs:
        print("Checking doc version references against current version...")
        print()
        changes = 0
        for rel_path, patterns in DOC_VERSION_FILES.items():
            filepath = REPO_ROOT / rel_path
            if update_file(
                filepath, patterns, {"version": current, "date": today}, dry_run=True
            ):
                changes += 1
        print()
        if changes:
            print(f"Found {changes} doc file(s) with stale version references.")
            print("Run: python scripts/bump_version.py --sync-docs")
            return 1
        print("All doc version references are up to date.")
        return 0

    if args.sync_docs:
        print(f"{'[DRY RUN] ' if args.dry_run else ''}Syncing docs to: {current}")
        print()
        changes = 0
        for rel_path, patterns in DOC_VERSION_FILES.items():
            filepath = REPO_ROOT / rel_path
            if update_file(
                filepath, patterns, {"version": current, "date": today}, args.dry_run
            ):
                changes += 1
        for rel_path, patterns in DOC_DATE_FILES.items():
            filepath = REPO_ROOT / rel_path
            if update_file(
                filepath, patterns, {"version": current, "date": today}, args.dry_run
            ):
                changes += 1
        print()
        if args.dry_run:
            print(f"Would update {changes} doc file(s)")
        else:
            print(f"Updated {changes} doc file(s)")
        print(EVERGREEN_NOTES)
        return 0

    if args.sync_dates:
        print(f"{'[DRY RUN] ' if args.dry_run else ''}Syncing doc dates to: {today}")
        print()
        changes = 0
        for rel_path, patterns in DOC_DATE_FILES.items():
            filepath = REPO_ROOT / rel_path
            if update_file(
                filepath, patterns, {"version": current, "date": today}, args.dry_run
            ):
                changes += 1
        print()
        if args.dry_run:
            print(f"Would update {changes} doc file(s)")
        else:
            print(f"Updated {changes} doc file(s)")
        return 0

    if not args.version:
        print(f"Current version: {current}")
        print("\nUsage: python scripts/bump_version.py <new_version>")
        print("Example: python scripts/bump_version.py 0.9.2")
        return 1

    new_version = args.version

    # Validate version format
    if not re.match(r"^\d+\.\d+\.\d+$", new_version):
        print(f"ERROR: Invalid version format: {new_version}")
        print("Expected: X.Y.Z (e.g., 0.9.2, 1.0.0)")
        return 1

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Bumping version: {current} → {new_version}")
    print()

    changes = 0
    for rel_path, patterns in VERSION_FILES.items():
        filepath = REPO_ROOT / rel_path
        if update_file(
            filepath, patterns, {"version": new_version, "date": today}, args.dry_run
        ):
            changes += 1

    doc_changes = 0
    for rel_path, patterns in DOC_VERSION_FILES.items():
        filepath = REPO_ROOT / rel_path
        if update_file(
            filepath, patterns, {"version": new_version, "date": today}, args.dry_run
        ):
            doc_changes += 1
    for rel_path, patterns in DOC_DATE_FILES.items():
        filepath = REPO_ROOT / rel_path
        if update_file(
            filepath, patterns, {"version": new_version, "date": today}, args.dry_run
        ):
            doc_changes += 1

    print()
    if args.dry_run:
        print(f"Would update {changes} core file(s)")
        print(f"Would update {doc_changes} doc file(s)")
    else:
        print(f"Updated {changes} core file(s)")
        print(f"Updated {doc_changes} doc file(s)")
        print("\nRemember to also:")
        print("  1. Add entry to CHANGELOG.md")
        print("  2. Update docs/releases.md")
        print("  3. Commit and tag: git tag v" + new_version)

    print(EVERGREEN_NOTES)

    return 0


if __name__ == "__main__":
    sys.exit(main())
