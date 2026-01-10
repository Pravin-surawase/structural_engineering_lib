#!/usr/bin/env python3
"""
Check for duplicate document filenames in the docs folder.

Duplicate filenames cause confusion about which is the canonical version.
Excludes README.md and index.md which are expected to have duplicates.

Usage:
    python scripts/check_duplicate_docs.py          # List duplicates
    python scripts/check_duplicate_docs.py --json   # Output as JSON
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

# Expected duplicates (per-folder files)
EXPECTED_DUPLICATES = {"README.md", "index.md", "__init__.py"}

# Directories to skip
SKIP_DIRS = {"_archive", "node_modules", ".git", "__pycache__", ".venv"}


def find_duplicate_docs(docs_dir: Path) -> dict[str, list[Path]]:
    """Find all duplicate markdown filenames."""
    files_by_name: dict[str, list[Path]] = defaultdict(list)

    for md_file in docs_dir.rglob("*.md"):
        # Skip excluded directories
        if any(skip in md_file.parts for skip in SKIP_DIRS):
            continue

        files_by_name[md_file.name].append(md_file)

    # Filter to only actual duplicates (excluding expected ones)
    duplicates = {
        name: paths
        for name, paths in files_by_name.items()
        if len(paths) > 1 and name not in EXPECTED_DUPLICATES
    }

    return duplicates


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Check for duplicate doc filenames")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    docs_dir = Path(__file__).parent.parent / "docs"

    duplicates = find_duplicate_docs(docs_dir)

    if args.json:
        result = {
            name: [str(p.relative_to(docs_dir.parent)) for p in paths]
            for name, paths in duplicates.items()
        }
        print(json.dumps(result, indent=2))
        return 1 if duplicates else 0

    if not duplicates:
        print("✅ No duplicate document filenames found!")
        return 0

    print(f"⚠️  Found {len(duplicates)} duplicate filenames:\n")

    for name, paths in sorted(duplicates.items()):
        print(f"  📄 {name} ({len(paths)} copies)")
        for path in paths:
            rel_path = path.relative_to(docs_dir.parent)
            size = path.stat().st_size
            print(f"      - {rel_path} ({size} bytes)")
        print()

    print("📋 Recommended actions:")
    print("  1. Identify the canonical (most up-to-date) version")
    print("  2. Archive or delete other versions")
    print("  3. Update references to point to canonical version")

    return 1


if __name__ == "__main__":
    sys.exit(main())
