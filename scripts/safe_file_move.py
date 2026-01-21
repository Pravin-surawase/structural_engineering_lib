#!/usr/bin/env python3
"""Safe file move script with automatic link updates.

This script safely moves/renames files by:
1. Checking for references in docs and code
2. Updating all internal links
3. Optionally creating redirect stubs
4. Running link validation

Usage:
    python scripts/safe_file_move.py <source> <destination> [--stub] [--dry-run]

Examples:
    python scripts/safe_file_move.py docs/old.md docs/new.md
    python scripts/safe_file_move.py docs/old.md docs/archive/old.md --stub
    python scripts/safe_file_move.py docs/old.md docs/new.md --dry-run
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


def find_references(file_path: Path, project_root: Path) -> list[tuple[Path, str, int]]:
    """Find all references to a file in docs and code.

    Returns list of (file, line_content, line_number) tuples.
    """
    references = []
    filename = file_path.name
    relative_path = str(file_path.relative_to(project_root))

    # Patterns to search for
    patterns = [
        filename,
        relative_path,
        relative_path.replace("/", "\\"),  # Windows paths
    ]

    # Search in docs and agents
    search_dirs = ["docs", "agents", "Python", "VBA", "streamlit_app"]
    extensions = [".md", ".py", ".bas", ".txt", ".json"]

    # Directories to exclude (performance optimization)
    exclude_dirs = {
        ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache",
        "build", "dist", "htmlcov", ".mypy_cache", ".ruff_cache",
        "*.egg-info", ".git", ".github", "logs", "tmp"
    }

    for search_dir in search_dirs:
        search_path = project_root / search_dir
        if not search_path.exists():
            continue

        for ext in extensions:
            for file in search_path.rglob(f"*{ext}"):
                # Skip if file is in excluded directory
                if any(excluded in file.parts for excluded in exclude_dirs):
                    continue
                if file == file_path:
                    continue
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    for i, line in enumerate(content.split("\n"), 1):
                        for pattern in patterns:
                            if pattern in line:
                                references.append((file, line.strip(), i))
                                break
                except (OSError, UnicodeDecodeError):
                    continue

    return references


def update_links(
    old_path: Path, new_path: Path, project_root: Path, dry_run: bool = False
) -> int:
    """Update all links from old_path to new_path.

    Returns number of files updated.
    """
    updated_count = 0
    old_relative = old_path.relative_to(project_root)
    new_relative = new_path.relative_to(project_root)

    # Patterns to replace
    old_patterns = [
        str(old_relative),
        old_path.name,
    ]

    search_dirs = ["docs", "agents", "Python", "streamlit_app"]

    for search_dir in search_dirs:
        search_path = project_root / search_dir
        if not search_path.exists():
            continue

        for file in search_path.rglob("*.md"):
            if file == old_path or file == new_path:
                continue

            try:
                content = file.read_text(encoding="utf-8")
                original_content = content

                # Update relative links
                # Calculate relative path from this file to old and new locations
                file_dir = file.parent

                try:
                    old_rel_from_file = old_path.relative_to(file_dir)
                except ValueError:
                    old_rel_from_file = Path("..") / old_relative

                try:
                    new_rel_from_file = new_path.relative_to(file_dir)
                except ValueError:
                    new_rel_from_file = Path("..") / new_relative

                # Replace patterns in markdown links
                # [text](old_path) -> [text](new_path)
                link_pattern = rf"\]\({re.escape(str(old_rel_from_file))}(\)?)"
                content = re.sub(link_pattern, f"]({new_rel_from_file}\\1", content)

                # Also replace exact filename matches in links
                content = content.replace(f"]({old_path.name})", f"]({new_path.name})")

                if content != original_content:
                    if dry_run:
                        print(f"  Would update: {file}")
                    else:
                        file.write_text(content, encoding="utf-8")
                        print(f"  Updated: {file}")
                    updated_count += 1

            except (OSError, UnicodeDecodeError) as e:
                print(f"  Warning: Could not process {file}: {e}")

    return updated_count


def create_redirect_stub(old_path: Path, new_path: Path, project_root: Path) -> None:
    """Create a redirect stub at the old location."""
    new_relative = new_path.relative_to(project_root)

    stub_content = f"""# Moved

This document has been moved to a new location.

**New location:** [{new_path.name}]({new_relative})

*Redirect created: {Path(__file__).name}*
"""
    old_path.write_text(stub_content, encoding="utf-8")
    print(f"  Created redirect stub at: {old_path}")


def run_link_check(project_root: Path) -> bool:
    """Run the link checker and return True if all links are valid."""
    check_script = project_root / "scripts" / "check_links.py"
    if not check_script.exists():
        print("  Warning: check_links.py not found, skipping validation")
        return True

    result = subprocess.run(
        [sys.executable, str(check_script)],
        cwd=project_root,
        capture_output=True,
        text=True,
    )

    if "Broken links: 0" in result.stdout or result.returncode == 0:
        return True
    else:
        print(result.stdout)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Safely move files with automatic link updates"
    )
    parser.add_argument("source", help="Source file path")
    parser.add_argument("destination", help="Destination file path")
    parser.add_argument(
        "--stub", action="store_true", help="Create redirect stub at old location"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without making changes",
    )
    parser.add_argument(
        "--force", action="store_true", help="Proceed even if references are found"
    )

    args = parser.parse_args()

    # Determine project root
    project_root = Path(__file__).parent.parent.resolve()

    source = Path(args.source)
    if not source.is_absolute():
        source = project_root / source
    source = source.resolve()

    destination = Path(args.destination)
    if not destination.is_absolute():
        destination = project_root / destination
    destination = destination.resolve()

    # Validate
    if not source.exists():
        print(f"❌ Error: Source file not found: {source}")
        sys.exit(1)

    if destination.exists() and not args.force:
        print(f"❌ Error: Destination already exists: {destination}")
        print("   Use --force to overwrite")
        sys.exit(1)

    print("=" * 60)
    print("🔄 Safe File Move")
    print("=" * 60)
    print(f"Source:      {source.relative_to(project_root)}")
    print(f"Destination: {destination.relative_to(project_root)}")
    print(f"Mode:        {'DRY RUN' if args.dry_run else 'LIVE'}")
    print()

    # Step 1: Find references
    print("📍 Step 1: Finding references...")
    references = find_references(source, project_root)

    if references:
        print(f"   Found {len(references)} reference(s):")
        for ref_file, ref_line, ref_lineno in references[:10]:
            rel_file = ref_file.relative_to(project_root)
            print(f"     - {rel_file}:{ref_lineno}")
        if len(references) > 10:
            print(f"     ... and {len(references) - 10} more")
    else:
        print("   No references found")

    # Step 2: Move file
    print()
    print("📦 Step 2: Moving file...")
    if args.dry_run:
        print(f"   Would move: {source.name} → {destination}")
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        source.rename(destination)
        print(f"   Moved: {source.name} → {destination}")

    # Step 3: Update links
    print()
    print("🔗 Step 3: Updating links...")
    updated = update_links(source, destination, project_root, args.dry_run)
    print(f"   Updated {updated} file(s)")

    # Step 4: Create redirect stub if requested
    if args.stub:
        print()
        print("📝 Step 4: Creating redirect stub...")
        if args.dry_run:
            print(f"   Would create stub at: {source}")
        else:
            create_redirect_stub(source, destination, project_root)

    # Step 5: Validate
    print()
    print("✅ Step 5: Validating links...")
    if args.dry_run:
        print("   Skipped (dry run)")
    else:
        if run_link_check(project_root):
            print("   All links valid!")
        else:
            print("   ⚠️  Some links may be broken. Review above.")

    print()
    print("=" * 60)
    if args.dry_run:
        print("✨ Dry run complete. No changes made.")
    else:
        print("✨ Move complete!")
        print()
        print("Next steps:")
        print("  1. Review changes: git diff")
        print("  2. Commit: ./scripts/ai_commit.sh 'refactor: move file'")
    print("=" * 60)


if __name__ == "__main__":
    main()
