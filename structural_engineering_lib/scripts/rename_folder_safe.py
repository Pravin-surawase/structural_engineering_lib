#!/usr/bin/env python3
"""Safely Rename Folder Script - Rename folder with link updates.

Safely renames a folder and updates all references in markdown files.

Usage:
    python scripts/rename_folder_safe.py "files from external yser" external_data
    python scripts/rename_folder_safe.py old_folder new_folder --dry-run
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
    for pattern in ["**/*.md"]:
        files.extend(PROJECT_ROOT.glob(pattern))
    # Exclude .venv, node_modules, etc.
    files = [
        f
        for f in files
        if ".venv" not in str(f)
        and "node_modules" not in str(f)
        and ".git" not in str(f)
    ]
    return files


def find_folder_references(folder_path: Path) -> list[tuple[Path, int, str]]:
    """Find all references to a folder in markdown files.

    Returns list of (file, line_number, line_content) tuples.
    """
    references = []
    folder_name = folder_path.name
    rel_path = folder_path.relative_to(PROJECT_ROOT)

    # Patterns to match folder references
    patterns = [
        re.compile(rf"\[.*?\]\([^)]*{re.escape(folder_name)}[/][^)]*\)"),
        re.compile(rf"\[.*?\]\([^)]*{re.escape(str(rel_path))}[^)]*\)"),
        re.compile(rf"`{re.escape(folder_name)}/`"),
        re.compile(rf"`{re.escape(str(rel_path))}`"),
    ]

    for md_file in get_all_markdown_files():
        try:
            content = md_file.read_text()
            for i, line in enumerate(content.splitlines(), 1):
                for pattern in patterns:
                    if pattern.search(line):
                        references.append((md_file, i, line.strip()[:100]))
                        break
        except Exception:
            pass

    return references


def update_folder_links(
    old_path: Path,
    new_path: Path,
    dry_run: bool = False,
) -> int:
    """Update all links from old folder to new folder.

    Returns number of files updated.
    """
    old_name = old_path.name
    new_name = new_path.name
    old_rel = str(old_path.relative_to(PROJECT_ROOT))
    new_rel = str(new_path.relative_to(PROJECT_ROOT))
    updated = 0

    for md_file in get_all_markdown_files():
        try:
            content = md_file.read_text()
            new_content = content

            # Update various reference patterns
            # Relative path references
            new_content = re.sub(
                rf"\](\([^)]*){re.escape(old_rel)}([^)]*\))",
                rf"]\1{new_rel}\2",
                new_content,
            )

            # Folder name references (with trailing slash)
            new_content = re.sub(
                rf"\](\([^)]*){re.escape(old_name)}/",
                rf"]\1{new_name}/",
                new_content,
            )

            # Backtick references
            new_content = new_content.replace(f"`{old_name}/`", f"`{new_name}/`")
            new_content = new_content.replace(f"`{old_rel}`", f"`{new_rel}`")

            if new_content != content:
                if not dry_run:
                    md_file.write_text(new_content)
                updated += 1
                rel_md = md_file.relative_to(PROJECT_ROOT)
                print(f"  📝 Updated: {rel_md}")
        except Exception as e:
            print(f"  ⚠️  Error processing {md_file}: {e}")

    return updated


def rename_folder(
    old_path: Path,
    new_path: Path,
    dry_run: bool = False,
    use_git: bool = True,
) -> bool:
    """Rename folder safely.

    Returns True if successful.
    """
    if not old_path.exists():
        print(f"❌ Source folder not found: {old_path}")
        return False

    if not old_path.is_dir():
        print(f"❌ Source is not a directory: {old_path}")
        return False

    if new_path.exists():
        print(f"❌ Destination already exists: {new_path}")
        return False

    # Check for references
    refs = find_folder_references(old_path)
    print(f"\n📎 Found {len(refs)} reference(s) to this folder")
    if refs:
        for ref_file, line_num, line in refs[:10]:
            rel_file = ref_file.relative_to(PROJECT_ROOT)
            print(f"   {rel_file}:{line_num}")
        if len(refs) > 10:
            print(f"   ... and {len(refs) - 10} more")

    if dry_run:
        print(f"\n[DRY-RUN] Would rename: {old_path.name} → {new_path.name}")
        print(f"[DRY-RUN] Would update {len(refs)} link(s)")
        return True

    # Rename folder
    print(f"\n🔄 Renaming folder...")
    if use_git:
        try:
            result = subprocess.run(
                ["git", "mv", str(old_path), str(new_path)],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT,
            )
            if result.returncode != 0:
                # Fall back to regular rename
                print(f"   git mv failed, using shutil.move")
                shutil.move(str(old_path), str(new_path))
        except Exception:
            shutil.move(str(old_path), str(new_path))
    else:
        shutil.move(str(old_path), str(new_path))

    print(f"   ✅ Renamed: {old_path.name} → {new_path.name}")

    # Update links
    if refs:
        print(f"\n🔗 Updating links...")
        updated = update_folder_links(old_path, new_path, dry_run=False)
        print(f"   ✅ Updated {updated} file(s)")

    return True


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Safely rename a folder with link updates"
    )
    parser.add_argument(
        "old_name",
        help="Current folder name or path",
    )
    parser.add_argument(
        "new_name",
        help="New folder name",
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

    # Resolve paths
    old_path = PROJECT_ROOT / args.old_name
    if not old_path.exists():
        # Try as relative path
        old_path = Path(args.old_name)
        if not old_path.exists():
            print(f"❌ Folder not found: {args.old_name}")
            return 1

    # New path is sibling of old path
    new_path = old_path.parent / args.new_name

    # Print header
    print("=" * 60)
    print("📁 Safe Folder Rename")
    print("=" * 60)
    print(f"From: {old_path}")
    print(f"To:   {new_path}")
    if args.dry_run:
        print("Mode: DRY RUN (no changes will be made)")

    # Execute rename
    success = rename_folder(
        old_path,
        new_path,
        args.dry_run,
        not args.no_git,
    )

    if success:
        print("\n" + "=" * 60)
        if args.dry_run:
            print("💡 Run without --dry-run to execute")
        else:
            print("✅ Folder renamed successfully!")
            print("\n💡 Next steps:")
            print("   1. Run: python scripts/check_links.py")
            print("   2. Verify no broken links")
            print("   3. Commit changes")
        print("=" * 60)
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
