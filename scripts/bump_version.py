#!/usr/bin/env python3
"""
Version Bump Script — Single Source of Truth

This script updates version numbers across the codebase from ONE location.

USAGE:
    python scripts/bump_version.py 0.9.2
    python scripts/bump_version.py 0.10.0 --dry-run

The single source of truth is Python/pyproject.toml.
This script updates all other files that need the version.
"""

import argparse
import re
import sys
from pathlib import Path

# Root of the repository
REPO_ROOT = Path(__file__).parent.parent

# Files that need version updates (relative to repo root)
# MINIMAL SET: Only files that MUST have hardcoded versions
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

# Files where version should be REMOVED or made evergreen
EVERGREEN_NOTES = """
Version is now managed in only 3 places:
  - Python/pyproject.toml (source of truth)
  - Python/api.py (dev mode fallback)
  - VBA/M08_API.bas (VBA runtime)

All other files should use dynamic version or say "see CHANGELOG".
"""


def read_current_version() -> str:
    """Read current version from pyproject.toml."""
    pyproject = REPO_ROOT / "Python" / "pyproject.toml"
    content = pyproject.read_text()
    match = re.search(r'^version = "([^"]+)"', content, re.MULTILINE)
    if match:
        return match.group(1)
    raise ValueError("Could not find version in pyproject.toml")


def update_file(filepath: Path, patterns: list, new_version: str, dry_run: bool) -> bool:
    """Update version patterns in a file. Returns True if changes made."""
    if not filepath.exists():
        print(f"  SKIP (not found): {filepath}")
        return False
    
    content = filepath.read_text()
    original = content
    
    for pattern, replacement in patterns:
        replacement_str = replacement.format(version=new_version)
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
    
    args = parser.parse_args()
    
    current = read_current_version()
    
    if args.current:
        print(f"Current version: {current}")
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
        if update_file(filepath, patterns, new_version, args.dry_run):
            changes += 1
    
    print()
    if args.dry_run:
        print(f"Would update {changes} file(s)")
    else:
        print(f"Updated {changes} file(s)")
        print("\nRemember to also:")
        print("  1. Add entry to CHANGELOG.md")
        print("  2. Update docs/RELEASES.md")
        print("  3. Commit and tag: git tag v" + new_version)
    
    print(EVERGREEN_NOTES)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
