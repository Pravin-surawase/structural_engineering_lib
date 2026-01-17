#!/usr/bin/env python3
"""Check that all folders have README.md files.

This script ensures folder documentation by:
1. Scanning all directories in the project
2. Checking for README.md (or index.md) presence
3. Reporting missing documentation
4. Optionally creating template READMEs

Usage:
    python scripts/check_folder_readmes.py           # Check all
    python scripts/check_folder_readmes.py --fix     # Create missing READMEs
    python scripts/check_folder_readmes.py --verbose # Show all folders
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

# Folders to skip (build artifacts, caches, etc.)
SKIP_FOLDERS = {
    ".git",
    ".venv",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    "__pycache__",
    "node_modules",
    ".benchmarks",
    "htmlcov",
    "build",
    "dist",
    ".egg-info",
    "UNKNOWN.egg-info",
    "structural_lib_is456.egg-info",
    "snapshots",  # Excel snapshots
}

# Folders that MUST have README
REQUIRED_FOLDERS = {
    "docs",
    "docs/reference",
    "docs/getting-started",
    "docs/architecture",
    "docs/research",
    "docs/planning",
    "Python",
    "Python/structural_lib",
    "Python/tests",
    "Python/examples",
    "VBA",
    "VBA/Modules",
    "scripts",
    "agents",
    "streamlit_app",
    "learning-materials",
}

# README template
README_TEMPLATE = """# {folder_name}

> **Purpose:** [Describe the purpose of this folder]
> **Last Updated:** {date}

## Contents

[List what belongs in this folder]

## Guidelines

[Any specific rules for this folder]

## For AI Agents

When working with files in this folder:
- [Guideline 1]
- [Guideline 2]
"""


def should_skip(folder: Path, project_root: Path) -> bool:
    """Check if folder should be skipped."""
    # Check folder name
    if folder.name in SKIP_FOLDERS:
        return True

    # Check if any parent is in skip list
    for parent in folder.relative_to(project_root).parts:
        if parent in SKIP_FOLDERS:
            return True

    # Skip hidden folders (except specific ones)
    if folder.name.startswith(".") and folder.name not in {".github"}:
        return True

    return False


def has_readme(folder: Path) -> bool:
    """Check if folder has README.md or index.md."""
    return (folder / "README.md").exists() or (folder / "index.md").exists()


def get_folder_type(folder: Path, project_root: Path) -> str:
    """Categorize folder by type."""
    rel_path = str(folder.relative_to(project_root))

    if rel_path.startswith("docs/"):
        return "documentation"
    elif rel_path.startswith("Python/"):
        return "python"
    elif rel_path.startswith("VBA/"):
        return "vba"
    elif rel_path.startswith("agents/"):
        return "agents"
    elif rel_path.startswith("scripts/"):
        return "scripts"
    elif rel_path.startswith("streamlit_app/"):
        return "streamlit"
    else:
        return "other"


def create_readme(folder: Path) -> None:
    """Create a template README in the folder."""
    readme_path = folder / "README.md"

    content = README_TEMPLATE.format(
        folder_name=folder.name.replace("-", " ").replace("_", " ").title(),
        date=datetime.now().strftime("%Y-%m-%d"),
    )

    readme_path.write_text(content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Check that all folders have README.md files"
    )
    parser.add_argument(
        "--fix", action="store_true", help="Create template READMEs for missing folders"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show all folders, not just missing",
    )
    parser.add_argument(
        "--required-only", action="store_true", help="Only check required folders"
    )

    args = parser.parse_args()

    # Determine project root
    project_root = Path(__file__).parent.parent.resolve()

    print("=" * 60)
    print("📁 Folder README Check")
    print("=" * 60)
    print(f"Project: {project_root.name}")
    print(f"Mode: {'FIX' if args.fix else 'CHECK'}")
    print()

    # Collect all folders
    all_folders: list[Path] = []
    for folder in project_root.rglob("*"):
        if folder.is_dir() and not should_skip(folder, project_root):
            all_folders.append(folder)

    # Also add project root
    all_folders.insert(0, project_root)

    # Filter to required only if requested
    if args.required_only:
        all_folders = [
            f
            for f in all_folders
            if str(f.relative_to(project_root)) in REQUIRED_FOLDERS or f == project_root
        ]

    # Check each folder
    missing: list[Path] = []
    has_readme_list: list[Path] = []
    required_missing: list[Path] = []

    for folder in sorted(all_folders):
        rel_path = (
            folder.relative_to(project_root) if folder != project_root else Path(".")
        )
        is_required = str(rel_path) in REQUIRED_FOLDERS

        if has_readme(folder):
            has_readme_list.append(folder)
            if args.verbose:
                status = "✅ Required" if is_required else "✅"
                print(f"  {status} {rel_path}/")
        else:
            missing.append(folder)
            if is_required:
                required_missing.append(folder)
            status = "❌ REQUIRED" if is_required else "⚠️  Missing"
            print(f"  {status} {rel_path}/")

    print()
    print("=" * 60)
    print("📊 Summary")
    print("=" * 60)
    print(f"  Total folders scanned: {len(all_folders)}")
    print(f"  Folders with README:   {len(has_readme_list)}")
    print(f"  Folders missing README: {len(missing)}")
    print(f"  Required missing:      {len(required_missing)}")
    print()

    # Fix if requested
    if args.fix and missing:
        print("🔧 Creating missing READMEs...")
        created = 0
        for folder in missing:
            rel_path = (
                folder.relative_to(project_root)
                if folder != project_root
                else Path(".")
            )
            create_readme(folder)
            print(f"  Created: {rel_path}/README.md")
            created += 1
        print(f"  Created {created} README files")
        print()

    # Exit code
    if required_missing:
        print("❌ Required folders are missing README!")
        print("   Run with --fix to create templates")
        sys.exit(1)
    else:
        print("✅ All required folders have READMEs")
        if missing and not args.fix:
            print(f"   ({len(missing)} optional folders missing - use --fix to add)")
        sys.exit(0)


if __name__ == "__main__":
    main()
