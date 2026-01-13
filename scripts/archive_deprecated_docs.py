#!/usr/bin/env python3
"""Archive deprecated documentation files.

This script implements Phase 1 of the documentation consolidation plan:
- Identifies files with Status: Deprecated or Status: Archived
- Moves them to _archive/ using safe_file_move.py
- Updates all internal links automatically
- Validates link integrity after operation

**Usage:**
    python scripts/archive_deprecated_docs.py --dry-run  # Preview
    python scripts/archive_deprecated_docs.py            # Execute

**Safety:**
- Uses safe_file_move.py (updates links automatically)
- Always creates backups before moving
- Runs check_links.py after completion
- Git tracks all changes (easy rollback)
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
ARCHIVE_DIR = DOCS_DIR / "_archive" / "deprecated-2026-01-13"


def find_deprecated_files() -> List[Tuple[Path, str]]:
    """Find all files marked as deprecated or archived."""
    deprecated = []

    for filepath in DOCS_DIR.rglob("*.md"):
        # Skip already archived files
        if "_archive" in str(filepath):
            continue

        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            # Check for deprecation indicators
            reasons = []

            if "**Status:**" in content:
                # Extract status line
                for line in content.split("\n"):
                    if "**Status:**" in line:
                        if "Deprecated" in line:
                            reasons.append("Status: Deprecated")
                        elif "Archived" in line:
                            reasons.append("Status: Archived")
                        break

            # Check if this file itself is superseded (in metadata section)
            # Look in first 50 lines only (metadata region)
            first_lines = content.split("\n")[:50]
            first_section = "\n".join(first_lines).lower()

            if ("superseded by:" in first_section or "replaced by:" in first_section or
                "this document is superseded" in first_section):
                reasons.append("Superseded")

            if reasons:
                deprecated.append((filepath, ", ".join(reasons)))

        except Exception as e:
            print(f"⚠ Error reading {filepath}: {e}")

    return deprecated


def archive_file(filepath: Path, reason: str, dry_run: bool = False) -> bool:
    """Archive a single file using safe_file_move.py."""
    relative_path = filepath.relative_to(DOCS_DIR)
    target_path = ARCHIVE_DIR / relative_path

    if dry_run:
        print(f"   Would move: {relative_path}")
        print(f"           to: {target_path.relative_to(PROJECT_ROOT)}")
        return True

    # Ensure target directory exists
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # Use safe_file_move.py
    try:
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "safe_file_move.py"),
                str(filepath),
                str(target_path),
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            print(f"   ✓ Moved: {relative_path}")
            return True
        else:
            print(f"   ✗ Failed: {relative_path}")
            print(f"      Error: {result.stderr}")
            return False

    except Exception as e:
        print(f"   ✗ Error moving {relative_path}: {e}")
        return False


def validate_links() -> bool:
    """Run check_links.py to validate all internal links."""
    try:
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "check_links.py"),
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            print("\n✓ Link validation passed")
            return True
        else:
            print("\n⚠ Link validation found issues:")
            print(result.stdout)
            return False

    except Exception as e:
        print(f"\n✗ Link validation error: {e}")
        return False


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(description="Archive deprecated documentation files")
    parser.add_argument("--dry-run", action="store_true", help="Preview without making changes")
    args = parser.parse_args()

    print("=" * 80)
    print("ARCHIVE DEPRECATED DOCUMENTATION FILES")
    print("=" * 80)
    print()

    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be moved")
        print()

    # Find deprecated files
    print("📂 Scanning for deprecated files...")
    deprecated_files = find_deprecated_files()

    if not deprecated_files:
        print("✓ No deprecated files found")
        return

    print(f"   Found {len(deprecated_files)} deprecated files")
    print()

    # Group by reason
    by_reason = {}
    for filepath, reason in deprecated_files:
        if reason not in by_reason:
            by_reason[reason] = []
        by_reason[reason].append(filepath)

    # Show summary
    print("📊 Breakdown by reason:")
    for reason, files in sorted(by_reason.items()):
        print(f"   {reason}: {len(files)} files")
    print()

    # Show files to be archived
    print("📦 Files to archive:")
    for filepath, reason in sorted(deprecated_files, key=lambda x: str(x[0])):
        rel_path = filepath.relative_to(PROJECT_ROOT)
        print(f"   • {rel_path}")
        print(f"     Reason: {reason}")
    print()

    if args.dry_run:
        print("=" * 80)
        print("DRY RUN COMPLETE")
        print(f"Would archive {len(deprecated_files)} files to:")
        print(f"  {ARCHIVE_DIR.relative_to(PROJECT_ROOT)}/")
        print("=" * 80)
        return

    # Confirm before proceeding
    response = input(f"\nArchive {len(deprecated_files)} files? [y/N]: ")
    if response.lower() != "y":
        print("Aborted")
        return

    # Archive files
    print("\n📦 Archiving files...")
    success_count = 0
    for filepath, reason in deprecated_files:
        if archive_file(filepath, reason, dry_run=False):
            success_count += 1

    print()
    print(f"✓ Successfully archived {success_count}/{len(deprecated_files)} files")
    print()

    # Validate links
    print("🔍 Validating internal links...")
    validate_links()

    print()
    print("=" * 80)
    print("ARCHIVE COMPLETE")
    print(f"Archived: {success_count} files")
    print(f"Location: {ARCHIVE_DIR.relative_to(PROJECT_ROOT)}/")
    print()
    print("Next steps:")
    print("1. Review changes: git status")
    print("2. Test navigation in VS Code")
    print("3. Commit: ./scripts/ai_commit.sh 'docs: archive deprecated files (Phase 1)'")
    print("=" * 80)


if __name__ == "__main__":
    main()
