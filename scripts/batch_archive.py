#!/usr/bin/env python3
"""Batch Archive Script - Move multiple files to archive folder.

Safely archives multiple files at once with link updates.

Usage:
    python scripts/batch_archive.py --files file1.md file2.md --dest docs/_archive/2026-01/
    python scripts/batch_archive.py --pattern "streamlit_app/AGENT-*.md" --dest streamlit_app/docs/_archive/
    python scripts/batch_archive.py --list-from orphans.txt --dest docs/_archive/
    python scripts/batch_archive.py --streamlit-cleanup  # Archive streamlit orphans
    python scripts/batch_archive.py --dry-run --pattern "*.md"
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Project root
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent


def get_all_markdown_files() -> list[Path]:
    """Get all markdown files in the project."""
    files = []
    for pattern in ["docs/**/*.md", "agents/**/*.md", "streamlit_app/**/*.md", "*.md"]:
        files.extend(PROJECT_ROOT.glob(pattern))
    return files


def find_references(file_path: Path) -> list[tuple[Path, int, str]]:
    """Find all references to a file in markdown files.

    Returns list of (file, line_number, line_content) tuples.
    """
    references = []
    file_name = file_path.name
    rel_path = file_path.relative_to(PROJECT_ROOT)

    # Patterns to match
    patterns = [
        re.compile(rf"\[.*?\]\([^)]*{re.escape(file_name)}[^)]*\)"),
        re.compile(rf"\[.*?\]\([^)]*{re.escape(str(rel_path))}[^)]*\)"),
    ]

    for md_file in get_all_markdown_files():
        if md_file == file_path:
            continue
        try:
            content = md_file.read_text()
            for i, line in enumerate(content.splitlines(), 1):
                for pattern in patterns:
                    if pattern.search(line):
                        references.append((md_file, i, line.strip()[:80]))
                        break
        except Exception:
            pass

    return references


def update_links(old_path: Path, new_path: Path, dry_run: bool = False) -> int:
    """Update all links from old path to new path.

    Returns number of files updated.
    """
    old_rel = old_path.relative_to(PROJECT_ROOT)
    new_rel = new_path.relative_to(PROJECT_ROOT)
    updated = 0

    for md_file in get_all_markdown_files():
        if md_file == old_path or md_file == new_path:
            continue
        try:
            content = md_file.read_text()
            new_content = content

            # Update absolute-style references
            new_content = new_content.replace(f"]({old_rel})", f"]({new_rel})")
            new_content = new_content.replace(f"]({old_path.name})", f"]({new_rel})")

            if new_content != content:
                if not dry_run:
                    md_file.write_text(new_content)
                updated += 1
        except Exception:
            pass

    return updated


def archive_file(
    file_path: Path,
    dest_dir: Path,
    dry_run: bool = False,
    use_git: bool = True,
) -> bool:
    """Archive a single file.

    Returns True if successful.
    """
    if not file_path.exists():
        print(f"  ⚠️  File not found: {file_path}")
        return False

    dest_file = dest_dir / file_path.name

    if dest_file.exists():
        print(f"  ⚠️  Destination exists: {dest_file}")
        return False

    # Check for references
    refs = find_references(file_path)
    if refs:
        print(f"  📎 Found {len(refs)} reference(s) - will update links")

    if dry_run:
        print(f"  [DRY-RUN] Would move: {file_path} → {dest_file}")
        return True

    # Create destination directory
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Move file (use git mv if available)
    if use_git:
        try:
            result = subprocess.run(
                ["git", "mv", str(file_path), str(dest_file)],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT,
            )
            if result.returncode != 0:
                # Fall back to regular move
                shutil.move(str(file_path), str(dest_file))
        except Exception:
            shutil.move(str(file_path), str(dest_file))
    else:
        shutil.move(str(file_path), str(dest_file))

    # Update links
    if refs:
        updated = update_links(file_path, dest_file, dry_run=False)
        print(f"  ✅ Moved and updated {updated} link(s)")
    else:
        print("  ✅ Moved (no links to update)")

    return True


def get_streamlit_orphans() -> list[Path]:
    """Get list of streamlit app orphan files to archive."""
    streamlit_root = PROJECT_ROOT / "streamlit_app"
    orphans = []

    patterns = [
        "AGENT-*.md",
        "AGENT_*.txt",
        "UI-*.md",
        "DELIVERABLES-*.txt",
        "DELIVERY_*.md",
        "FINAL_*.md",
        "HANDOFF-*.md",
        "WORK_*.md",
        "RESEARCH-*.txt",
        "SETUP_AND_MAINTENANCE_GUIDE.md",
        "VERIFY_*.sh",
    ]

    for pattern in patterns:
        orphans.extend(streamlit_root.glob(pattern))

    return sorted(set(orphans))


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Batch archive files with link updates"
    )
    parser.add_argument(
        "--files",
        nargs="+",
        help="List of files to archive",
    )
    parser.add_argument(
        "--pattern",
        help="Glob pattern to match files",
    )
    parser.add_argument(
        "--list-from",
        help="Read file list from a text file",
    )
    parser.add_argument(
        "--dest",
        help="Destination archive directory",
    )
    parser.add_argument(
        "--streamlit-cleanup",
        action="store_true",
        help="Archive streamlit app orphan files",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without doing it",
    )
    parser.add_argument(
        "--no-git",
        action="store_true",
        help="Don't use git mv",
    )

    args = parser.parse_args()

    # Determine files to archive
    files: list[Path] = []

    if args.streamlit_cleanup:
        files = get_streamlit_orphans()
        dest_dir = PROJECT_ROOT / "streamlit_app" / "docs" / "_archive"
    elif args.files:
        files = [PROJECT_ROOT / f for f in args.files]
        if not args.dest:
            parser.error("--dest is required with --files")
        dest_dir = PROJECT_ROOT / args.dest
    elif args.pattern:
        files = list(PROJECT_ROOT.glob(args.pattern))
        if not args.dest:
            parser.error("--dest is required with --pattern")
        dest_dir = PROJECT_ROOT / args.dest
    elif args.list_from:
        list_file = Path(args.list_from)
        if list_file.exists():
            files = [
                PROJECT_ROOT / line.strip()
                for line in list_file.read_text().splitlines()
                if line.strip() and not line.startswith("#")
            ]
        if not args.dest:
            parser.error("--dest is required with --list-from")
        dest_dir = PROJECT_ROOT / args.dest
    else:
        parser.print_help()
        return 1

    if not files:
        print("No files found to archive")
        return 0

    # Print summary
    print("=" * 60)
    print("📦 Batch Archive")
    print("=" * 60)
    print(f"Files to archive: {len(files)}")
    print(f"Destination: {dest_dir}")
    if args.dry_run:
        print("Mode: DRY RUN (no changes will be made)")
    print()

    # Process each file
    success = 0
    failed = 0

    for file_path in files:
        rel_path = (
            file_path.relative_to(PROJECT_ROOT)
            if file_path.is_relative_to(PROJECT_ROOT)
            else file_path
        )
        print(f"📄 {rel_path}")

        if archive_file(file_path, dest_dir, args.dry_run, not args.no_git):
            success += 1
        else:
            failed += 1

    # Print summary
    print()
    print("=" * 60)
    print(f"✅ Archived: {success}")
    if failed:
        print(f"❌ Failed: {failed}")
    print("=" * 60)

    if args.dry_run:
        print("\n💡 Run without --dry-run to execute")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
