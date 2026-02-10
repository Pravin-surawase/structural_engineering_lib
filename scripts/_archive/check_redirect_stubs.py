#!/usr/bin/env python3
"""
Check for redirect stub files and optionally fix references.

A redirect stub is a small markdown file (<500 bytes) that contains
"moved to" or similar redirect language.

Usage:
    python scripts/check_redirect_stubs.py          # List stubs
    python scripts/check_redirect_stubs.py --fix    # Update references and remove stubs
    python scripts/check_redirect_stubs.py --dry-run # Show what --fix would do
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Directories to skip
SKIP_DIRS = {"_archive", "node_modules", ".git", "__pycache__", ".venv"}

# Patterns that indicate a redirect stub
REDIRECT_PATTERNS = [
    r"has moved",
    r"moved to",
    r"redirected to",
    r"new location:",
    r"this document has moved",
]


def find_redirect_stubs(docs_dir: Path) -> list[dict]:
    """Find all redirect stub files."""
    stubs = []

    for md_file in docs_dir.rglob("*.md"):
        # Skip archive and other excluded directories
        if any(skip in md_file.parts for skip in SKIP_DIRS):
            continue

        # Only check small files
        if md_file.stat().st_size > 500:
            continue

        content = md_file.read_text(encoding="utf-8")
        content_lower = content.lower()

        # Check for redirect patterns
        is_redirect = any(re.search(p, content_lower) for p in REDIRECT_PATTERNS)

        if is_redirect:
            # Extract target link
            link_match = re.search(r"\[([^\]]*)\]\(([^)]+)\)", content)
            target = link_match.group(2) if link_match else None

            stubs.append(
                {
                    "file": md_file,
                    "size": md_file.stat().st_size,
                    "target": target,
                    "content": content[:200],
                }
            )

    return stubs


def find_references_to_stub(stub_path: Path, docs_dir: Path) -> list[tuple[Path, str]]:
    """Find all files that reference the stub."""
    references = []
    stub_name = stub_path.name

    for md_file in docs_dir.rglob("*.md"):
        if md_file == stub_path:
            continue
        if any(skip in md_file.parts for skip in SKIP_DIRS):
            continue

        content = md_file.read_text(encoding="utf-8")
        if stub_name in content:
            references.append((md_file, content))

    return references


def resolve_target_path(
    stub_path: Path, target: str | None, docs_dir: Path
) -> Path | None:
    """Resolve the target path from a redirect stub."""
    if not target:
        return None

    # Handle relative paths
    if target.startswith("../"):
        resolved = (stub_path.parent / target).resolve()
    elif target.startswith("./"):
        resolved = (stub_path.parent / target[2:]).resolve()
    else:
        resolved = (stub_path.parent / target).resolve()

    # Check for self-reference (stub points to itself)
    if resolved == stub_path.resolve():
        return None  # Treat as invalid - self-reference

    if resolved.exists():
        return resolved

    # Try without the leading ../
    alt_path = docs_dir / target.lstrip("../").lstrip("./")
    if alt_path.exists():
        return alt_path

    return None


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Check and clean redirect stubs")
    parser.add_argument(
        "--fix", action="store_true", help="Update references and remove stubs"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what --fix would do"
    )
    args = parser.parse_args()

    docs_dir = Path(__file__).parent.parent / "docs"

    print("🔍 Scanning for redirect stubs...")
    stubs = find_redirect_stubs(docs_dir)

    if not stubs:
        print("✅ No redirect stubs found!")
        return 0

    print(f"\n📋 Found {len(stubs)} redirect stubs:\n")

    safe_to_remove = []
    has_references = []

    for stub in stubs:
        rel_path = stub["file"].relative_to(docs_dir.parent)
        target = stub["target"] or "unknown"
        resolved = resolve_target_path(stub["file"], stub["target"], docs_dir)

        refs = find_references_to_stub(stub["file"], docs_dir)

        status = "✅ Safe" if not refs else f"⚠️  {len(refs)} refs"
        target_status = "→ exists" if resolved else "→ MISSING"

        print(f"  {rel_path}")
        print(f"    Target: {target} {target_status}")
        print(f"    Status: {status}")

        if refs:
            for ref_file, _ in refs[:3]:
                print(f"      - {ref_file.relative_to(docs_dir.parent)}")
            if len(refs) > 3:
                print(f"      ... and {len(refs) - 3} more")
            has_references.append((stub, refs, resolved))
        else:
            safe_to_remove.append(stub)
        print()

    print("\n📊 Summary:")
    print(f"  Safe to remove: {len(safe_to_remove)}")
    print(f"  Has references: {len(has_references)}")

    if args.fix or args.dry_run:
        action = "Would" if args.dry_run else "Will"
        print(f"\n🔧 {action} remove {len(safe_to_remove)} stubs without references...")

        for stub in safe_to_remove:
            rel_path = stub["file"].relative_to(docs_dir.parent)
            print(f"  {'[DRY-RUN] ' if args.dry_run else ''}Removing: {rel_path}")
            if not args.dry_run:
                stub["file"].unlink()

        if has_references:
            print(
                f"\n⚠️  {len(has_references)} stubs have references - manual review needed:"
            )
            for stub, refs, resolved in has_references:
                rel_path = stub["file"].relative_to(docs_dir.parent)
                print(f"  {rel_path}: {len(refs)} references")

    return 1 if stubs else 0


if __name__ == "__main__":
    sys.exit(main())
