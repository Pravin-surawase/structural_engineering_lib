#!/usr/bin/env python3
"""Find orphan files that are not referenced anywhere.

This script helps identify files that may be safe to archive or delete by:
1. Scanning all markdown/doc files
2. Checking which ones are never linked to
3. Reporting potential orphans for review

Usage:
    python scripts/find_orphan_files.py              # Check docs/
    python scripts/find_orphan_files.py --all        # Check all folders
    python scripts/find_orphan_files.py --verbose    # Show reference counts
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

# Folders to scan for orphans
DOC_FOLDERS = ["docs", "agents"]

# Files that are expected to not be linked (entry points, configs)
EXPECTED_UNLINKED = {
    "README.md",
    "index.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "LICENSE.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    "SUPPORT.md",
    "AUTHORS.md",
    "TASKS.md",
    "SESSION_LOG.md",
}

# Folders to skip when looking for references
SKIP_FOLDERS = {
    ".git",
    ".venv",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    "htmlcov",
    "build",
    "dist",
}


def should_skip(path: Path) -> bool:
    """Check if path should be skipped."""
    for part in path.parts:
        if part in SKIP_FOLDERS:
            return True
    return False


def find_all_links(project_root: Path) -> dict[str, list[Path]]:
    """Find all internal links in markdown files.

    Returns dict mapping filename/path patterns to list of files that link to them.
    """
    links: dict[str, list[Path]] = defaultdict(list)

    for md_file in project_root.rglob("*.md"):
        if should_skip(md_file):
            continue

        try:
            content = md_file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        # Find markdown links: [text](path)
        link_pattern = r"\[([^\]]*)\]\(([^)]+)\)"
        for match in re.finditer(link_pattern, content):
            link_target = match.group(2)

            # Skip external links and anchors
            if link_target.startswith(("http://", "https://", "#", "mailto:")):
                continue

            # Extract filename from path
            # Handle relative paths and anchors
            clean_target = link_target.split("#")[0].split("?")[0]
            if clean_target:
                links[clean_target].append(md_file)

                # Also track just the filename
                filename = Path(clean_target).name
                if filename:
                    links[filename].append(md_file)

    return links


def find_orphans(
    project_root: Path,
    scan_folders: list[str],
    links: dict[str, list[Path]],
    verbose: bool = False,
) -> list[tuple[Path, int]]:
    """Find files that are not linked to.

    Returns list of (file_path, reference_count) tuples.
    """
    orphans: list[tuple[Path, int]] = []

    for folder_name in scan_folders:
        folder = project_root / folder_name
        if not folder.exists():
            continue

        for md_file in folder.rglob("*.md"):
            if should_skip(md_file):
                continue

            rel_path = md_file.relative_to(project_root)
            filename = md_file.name

            # Skip expected unlinked files
            if filename in EXPECTED_UNLINKED:
                continue

            # Check if file is referenced
            ref_count = 0

            # Check various ways file might be referenced
            patterns_to_check = [
                str(rel_path),
                filename,
                md_file.stem,  # Without extension
                str(rel_path).replace("/", "\\"),
            ]

            for pattern in patterns_to_check:
                if pattern in links:
                    ref_count = max(ref_count, len(links[pattern]))

            if ref_count == 0:
                orphans.append((md_file, 0))
            elif verbose:
                print(f"  📎 {rel_path}: {ref_count} reference(s)")

    return orphans


def get_file_age_info(file_path: Path, project_root: Path) -> str:
    """Get age info from git."""
    import subprocess

    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cr", "--", str(file_path)],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() if result.stdout.strip() else "Unknown"
    except (subprocess.SubprocessError, OSError):
        return "Unknown"


def main():
    parser = argparse.ArgumentParser(
        description="Find orphan files not referenced anywhere"
    )
    parser.add_argument(
        "--all", action="store_true", help="Scan all folders, not just docs/"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show reference counts for all files",
    )
    parser.add_argument("--age", action="store_true", help="Show age of orphan files")

    args = parser.parse_args()

    # Determine project root
    project_root = Path(__file__).parent.parent.resolve()

    # Determine folders to scan
    if args.all:
        scan_folders = ["docs", "agents", "streamlit_app", "learning-materials"]
    else:
        scan_folders = DOC_FOLDERS

    print("=" * 60)
    print("🔍 Orphan File Finder")
    print("=" * 60)
    print(f"Scanning: {', '.join(scan_folders)}")
    print()

    # Find all links
    print("📎 Step 1: Indexing all internal links...")
    links = find_all_links(project_root)
    unique_targets = len(set(links.keys()))
    print(f"   Found {unique_targets} unique link targets")
    print()

    # Find orphans
    print("🔍 Step 2: Finding orphan files...")
    orphans = find_orphans(project_root, scan_folders, links, args.verbose)
    print()

    if not orphans:
        print("✅ No orphan files found!")
        print("   All documentation files are properly linked.")
        sys.exit(0)

    # Report orphans
    print("=" * 60)
    print(f"📋 Found {len(orphans)} potential orphan(s)")
    print("=" * 60)
    print()

    # Group by folder
    by_folder: dict[str, list[Path]] = defaultdict(list)
    for file_path, _ in orphans:
        folder = file_path.parent.relative_to(project_root)
        by_folder[str(folder)].append(file_path)

    for folder, files in sorted(by_folder.items()):
        print(f"📁 {folder}/")
        for file_path in sorted(files):
            rel_path = file_path.relative_to(project_root)
            if args.age:
                age = get_file_age_info(file_path, project_root)
                print(f"   ⚠️  {file_path.name} ({age})")
            else:
                print(f"   ⚠️  {file_path.name}")
        print()

    print("=" * 60)
    print("💡 Recommendations:")
    print("=" * 60)
    print("  1. Review each orphan - it may be:")
    print("     - Entry point that should be linked from README")
    print("     - Outdated doc that should be archived")
    print("     - Work-in-progress that will be linked later")
    print()
    print("  2. For files to archive:")
    print("     python scripts/safe_file_move.py <file> docs/_archive/<file>")
    print()
    print("  3. For files to delete:")
    print("     python scripts/safe_file_delete.py <file> --dry-run")
    print()

    # Return count for CI integration
    sys.exit(0)  # Don't fail - orphans need manual review


if __name__ == "__main__":
    main()
