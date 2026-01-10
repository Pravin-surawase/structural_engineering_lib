#!/usr/bin/env python3
"""Safe file delete script with reference checking.

This script safely deletes files by:
1. Checking for all references in docs and code
2. Showing what would break
3. Optionally creating backup
4. Running link validation after delete

Usage:
    python scripts/safe_file_delete.py <file> [--force] [--dry-run]

Examples:
    python scripts/safe_file_delete.py docs/old.md --dry-run
    python scripts/safe_file_delete.py docs/old.md --force
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def find_references(file_path: Path, project_root: Path) -> list[tuple[Path, str, int]]:
    """Find all references to a file in docs and code.

    Returns list of (file, line_content, line_number) tuples.
    """
    references = []
    filename = file_path.name
    stem = file_path.stem  # filename without extension

    try:
        relative_path = str(file_path.relative_to(project_root))
    except ValueError:
        relative_path = str(file_path)

    # Patterns to search for
    patterns = [
        filename,
        stem,
        relative_path,
        relative_path.replace("/", "\\"),
    ]

    # Search directories
    search_dirs = ["docs", "agents", "Python", "VBA", "streamlit_app", ".github"]
    extensions = [".md", ".py", ".bas", ".txt", ".json", ".yml", ".yaml"]

    for search_dir in search_dirs:
        search_path = project_root / search_dir
        if not search_path.exists():
            continue

        for ext in extensions:
            for file in search_path.rglob(f"*{ext}"):
                if file == file_path:
                    continue
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    for i, line in enumerate(content.split("\n"), 1):
                        for pattern in patterns:
                            if pattern in line:
                                references.append((file, line.strip()[:100], i))
                                break
                except (OSError, UnicodeDecodeError):
                    continue

    return references


def check_git_history(file_path: Path, project_root: Path) -> dict:
    """Get git history info for the file."""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-5", "--", str(file_path)],
            cwd=project_root,
            capture_output=True,
            text=True
        )

        commits = result.stdout.strip().split("\n") if result.stdout.strip() else []

        # Get last modified date
        result2 = subprocess.run(
            ["git", "log", "-1", "--format=%ci", "--", str(file_path)],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        last_modified = result2.stdout.strip() if result2.stdout.strip() else "Unknown"

        return {
            "recent_commits": len(commits),
            "last_modified": last_modified,
            "commits": commits[:3]
        }
    except (OSError, subprocess.CalledProcessError):
        return {"recent_commits": 0, "last_modified": "Unknown", "commits": []}


def create_backup(file_path: Path, project_root: Path) -> Path:
    """Create a backup of the file before deletion."""
    backup_dir = project_root / "tmp" / "deleted_backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
    backup_path = backup_dir / backup_name

    shutil.copy2(file_path, backup_path)
    return backup_path


def run_link_check(project_root: Path) -> tuple[bool, str]:
    """Run the link checker and return (success, output)."""
    check_script = project_root / "scripts" / "check_links.py"
    if not check_script.exists():
        return True, "check_links.py not found, skipped"

    result = subprocess.run(
        [sys.executable, str(check_script)],
        cwd=project_root,
        capture_output=True,
        text=True
    )

    success = "Broken links: 0" in result.stdout or result.returncode == 0
    return success, result.stdout


def main():
    parser = argparse.ArgumentParser(
        description="Safely delete files with reference checking"
    )
    parser.add_argument("file", help="File to delete")
    parser.add_argument(
        "--force", action="store_true",
        help="Delete even if references exist"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would happen without deleting"
    )
    parser.add_argument(
        "--no-backup", action="store_true",
        help="Skip creating backup"
    )

    args = parser.parse_args()

    # Determine project root
    project_root = Path(__file__).parent.parent.resolve()

    file_path = Path(args.file)
    if not file_path.is_absolute():
        file_path = project_root / file_path
    file_path = file_path.resolve()

    # Validate
    if not file_path.exists():
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)

    if not file_path.is_file():
        print(f"❌ Error: Not a file: {file_path}")
        sys.exit(1)

    try:
        relative_path = file_path.relative_to(project_root)
    except ValueError:
        print(f"❌ Error: File must be within project: {project_root}")
        sys.exit(1)

    print("=" * 60)
    print("🗑️  Safe File Delete")
    print("=" * 60)
    print(f"File: {relative_path}")
    print(f"Size: {file_path.stat().st_size:,} bytes")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print()

    # Step 1: Check git history
    print("📜 Step 1: Checking git history...")
    history = check_git_history(file_path, project_root)
    print(f"   Last modified: {history['last_modified']}")
    print(f"   Recent commits: {history['recent_commits']}")
    if history['commits']:
        for commit in history['commits']:
            print(f"     - {commit}")
    print()

    # Step 2: Find references
    print("🔍 Step 2: Finding references...")
    references = find_references(file_path, project_root)

    if references:
        print(f"   ⚠️  Found {len(references)} reference(s):")
        for ref_file, ref_line, ref_lineno in references[:15]:
            try:
                rel_file = ref_file.relative_to(project_root)
            except ValueError:
                rel_file = ref_file
            print(f"     {rel_file}:{ref_lineno}")
            print(f"       {ref_line[:80]}...")
        if len(references) > 15:
            print(f"     ... and {len(references) - 15} more")
        print()

        if not args.force and not args.dry_run:
            print("❌ Cannot delete: References exist!")
            print("   Use --force to delete anyway")
            print("   Or fix references first")
            sys.exit(1)
    else:
        print("   ✅ No references found - safe to delete")
    print()

    # Step 3: Create backup
    if not args.no_backup:
        print("💾 Step 3: Creating backup...")
        if args.dry_run:
            print(f"   Would backup to: tmp/deleted_backups/")
        else:
            backup_path = create_backup(file_path, project_root)
            print(f"   Backed up to: {backup_path.relative_to(project_root)}")
    else:
        print("💾 Step 3: Backup skipped (--no-backup)")
    print()

    # Step 4: Delete file
    print("🗑️  Step 4: Deleting file...")
    if args.dry_run:
        print(f"   Would delete: {relative_path}")
    else:
        file_path.unlink()
        print(f"   Deleted: {relative_path}")
    print()

    # Step 5: Validate links
    print("✅ Step 5: Validating links...")
    if args.dry_run:
        print("   Skipped (dry run)")
    else:
        success, output = run_link_check(project_root)
        if success:
            print("   All links still valid!")
        else:
            print("   ⚠️  Some links may be broken:")
            # Extract broken links from output
            for line in output.split("\n"):
                if "broken" in line.lower() or "error" in line.lower():
                    print(f"     {line}")

    print()
    print("=" * 60)
    if args.dry_run:
        print("✨ Dry run complete. No changes made.")
        if references:
            print()
            print("⚠️  Warning: This file has references that would break!")
    else:
        print("✨ Delete complete!")
        print()
        print("Next steps:")
        print("  1. Review: git status")
        print("  2. Commit: ./scripts/ai_commit.sh 'chore: remove unused file'")
        if references:
            print("  3. Fix broken references!")
    print("=" * 60)


if __name__ == "__main__":
    main()
