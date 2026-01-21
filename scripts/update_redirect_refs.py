#!/usr/bin/env python3
"""
Automated redirect reference updater.

This script:
1. Finds all redirect stubs and their target files
2. Finds all references to each stub
3. Calculates the correct new path for each reference
4. Updates all references automatically
5. Optionally removes the stub after updating

Usage:
    python scripts/update_redirect_refs.py              # Dry run - show what would change
    python scripts/update_redirect_refs.py --fix        # Actually update references
    python scripts/update_redirect_refs.py --fix --remove-stubs  # Update refs AND remove stubs

Created: 2026-01-10
Author: AI Agent (Phase C.2)
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path


def find_redirect_stubs(docs_dir: Path) -> dict[Path, Path]:
    """Find redirect stubs and their target files.

    Returns:
        Dict mapping stub path to canonical target path (absolute)
    """
    stubs: dict[Path, Path] = {}
    skip_dirs = {"_archive", "node_modules", ".git", "__pycache__", ".venv"}

    # Patterns that indicate a redirect stub (content patterns)
    redirect_patterns = [
        r"has moved",
        r"moved to",
        r"redirected to",
        r"new location:",
        r"this document has moved",
    ]

    for md_file in docs_dir.rglob("*.md"):
        # Skip archives and other excluded directories
        if any(skip in md_file.parts for skip in skip_dirs):
            continue
        try:
            stat = md_file.stat()
            if stat.st_size > 500:
                continue
            content = md_file.read_text(encoding="utf-8")
        except Exception:
            continue

        content_lower = content.lower()

        # Check for redirect patterns
        is_redirect = any(re.search(p, content_lower) for p in redirect_patterns)

        if is_redirect:
            # Extract target link from markdown link syntax
            link_match = re.search(r"\[([^\]]*)\]\(([^)]+)\)", content)
            if link_match:
                target_ref = link_match.group(2).strip()
                # Resolve target path relative to stub location
                stub_dir = md_file.parent
                target_path = (stub_dir / target_ref).resolve()

                if target_path.exists():
                    stubs[md_file] = target_path

    return stubs


def find_references(docs_dir: Path, stub_path: Path) -> list[tuple[Path, str, str]]:
    """Find all references to a stub file.

    Returns:
        List of (file_path, old_link, line_content) tuples
    """
    refs: list[tuple[Path, str, str]] = []
    stub_name = stub_path.name

    # Pattern to match markdown links containing the stub filename
    link_pattern = re.compile(
        r"\[([^\]]*)\]\(([^)]*" + re.escape(stub_name) + r"[^)]*)\)"
    )

    for md_file in docs_dir.rglob("*.md"):
        if md_file == stub_path:
            continue
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception:
            continue

        for match in link_pattern.finditer(content):
            link_target = match.group(2)
            # Verify this link actually points to our stub
            ref_dir = md_file.parent
            try:
                resolved = (ref_dir / link_target.split("#")[0]).resolve()
                if resolved == stub_path.resolve():
                    refs.append((md_file, match.group(0), link_target))
            except Exception:
                pass

    return refs


def calculate_new_path(from_file: Path, to_file: Path) -> str:
    """Calculate relative path from one file to another."""
    from_dir = from_file.parent
    rel_path = os.path.relpath(to_file, from_dir)
    # Use forward slashes for markdown
    return rel_path.replace("\\", "/")


def update_references(
    docs_dir: Path,
    stubs: dict[Path, Path],
    fix: bool = False,
    remove_stubs: bool = False,
) -> tuple[int, int, int]:
    """Update all references from stubs to canonical targets.

    Returns:
        (refs_updated, files_modified, stubs_removed)
    """
    refs_updated = 0
    files_modified = set()
    stubs_removed = 0

    for stub_path, target_path in stubs.items():
        refs = find_references(docs_dir, stub_path)

        if not refs:
            print(f"\n📄 {stub_path.relative_to(docs_dir)}")
            print(f"   → Target: {target_path.relative_to(docs_dir)}")
            print("   ✅ No references found - safe to remove")
            if fix and remove_stubs:
                stub_path.unlink()
                stubs_removed += 1
                print("   🗑️  Removed stub")
            continue

        print(f"\n📄 {stub_path.relative_to(docs_dir)}")
        print(f"   → Target: {target_path.relative_to(docs_dir)}")
        print(f"   📎 {len(refs)} reference(s):")

        # Group refs by file for batch updates
        refs_by_file: dict[Path, list[tuple[str, str]]] = {}
        for ref_file, old_link, link_target in refs:
            if ref_file not in refs_by_file:
                refs_by_file[ref_file] = []

            # Calculate new path
            new_path = calculate_new_path(ref_file, target_path)

            # Preserve anchor if present
            if "#" in link_target:
                anchor = "#" + link_target.split("#", 1)[1]
                new_path += anchor

            # Build new link (preserve link text)
            link_text_match = re.match(r"\[([^\]]*)\]", old_link)
            link_text = link_text_match.group(1) if link_text_match else ""
            new_link = f"[{link_text}]({new_path})"

            refs_by_file[ref_file].append((old_link, new_link))
            refs_updated += 1  # Count in dry run too

            rel_ref = ref_file.relative_to(docs_dir)
            print(f"      {rel_ref}")
            print(f"        - {old_link}")
            print(f"        + {new_link}")

        # Track files that would be modified
        files_modified.update(refs_by_file.keys())

        # Apply updates
        if fix:
            for ref_file, replacements in refs_by_file.items():
                try:
                    content = ref_file.read_text(encoding="utf-8")
                    for old_link, new_link in replacements:
                        content = content.replace(old_link, new_link)
                    ref_file.write_text(content, encoding="utf-8")
                except Exception as e:
                    print(f"   ❌ Error updating {ref_file}: {e}")

            # Check if we can remove stub now
            remaining_refs = find_references(docs_dir, stub_path)
            if not remaining_refs and remove_stubs:
                stub_path.unlink()
                stubs_removed += 1
                print("   🗑️  Removed stub (all refs updated)")

    return refs_updated, len(files_modified), stubs_removed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Update redirect stub references to canonical targets"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Actually update the references (default: dry run)",
    )
    parser.add_argument(
        "--remove-stubs",
        action="store_true",
        help="Remove stubs after updating all their references",
    )
    args = parser.parse_args()

    # Find docs directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    docs_dir = project_root / "docs"

    if not docs_dir.exists():
        print(f"❌ docs directory not found: {docs_dir}")
        return 1

    print("🔍 Finding redirect stubs...")
    stubs = find_redirect_stubs(docs_dir)

    if not stubs:
        print("✅ No redirect stubs found!")
        return 0

    print(f"📋 Found {len(stubs)} redirect stubs")

    mode = "🔧 FIX MODE" if args.fix else "👀 DRY RUN (use --fix to apply)"
    print(f"\n{mode}\n")

    refs_updated, files_modified, stubs_removed = update_references(
        docs_dir, stubs, fix=args.fix, remove_stubs=args.remove_stubs
    )

    print(f"\n{'=' * 50}")
    if args.fix:
        print(f"✅ Updated {refs_updated} references in {files_modified} files")
        if args.remove_stubs:
            print(f"🗑️  Removed {stubs_removed} stubs")
    else:
        print(f"📊 Would update {refs_updated} references in {files_modified} files")
        print("   Run with --fix to apply changes")
        print("   Run with --fix --remove-stubs to also remove stubs")

    return 0


if __name__ == "__main__":
    sys.exit(main())
