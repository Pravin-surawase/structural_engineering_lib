#!/usr/bin/env python3
"""Validate folder structure against governance rules.

This script checks if the project folder structure follows the rules defined in:
docs/governance/FOLDER_STRUCTURE_GOVERNANCE.md

Usage:
    python scripts/validate_folder_structure.py
    python scripts/validate_folder_structure.py --fix  # Auto-fix some issues
    python scripts/validate_folder_structure.py --report  # Detailed report

Exit codes:
    0: All checks passed
    1: Violations found
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict
import argparse

# Governance rules
RULES = {
    "root": {
        "max_files": 10,
        "allowed_extensions": [".md", ".txt", ".toml", ".yaml", ".yml", ".json", ".cfg", ".ini"],
        "allowed_files": [
            "README.md",
            "CHANGELOG.md",
            "CONTRIBUTING.md",
            "LICENSE",
            "LICENSE_ENGINEERING.md",
            "CODE_OF_CONDUCT.md",
            "SECURITY.md",
            "SUPPORT.md",
            "pyproject.toml",
            ".gitignore",
            ".pre-commit-config.yaml",
        ],
    },
    "docs_root": {
        "max_files": 5,
        "allowed_files": [
            "README.md",
            "TASKS.md",
            "SESSION_LOG.md",
            "CHANGELOG.md",
            "TODO.md",
        ],
    },
    "agents_root": {
        "max_files": 1,
        "allowed_files": ["README.md"],
    },
    "category_folders": {
        "required": [
            "docs/getting-started",
            "docs/reference",
            "docs/contributing",
            "docs/architecture",
            "docs/governance",
            "docs/agents",
        ],
        "must_have_readme": True,
    },
    "naming": {
        "docs_pattern": r"^[a-z0-9\-_]+\.md$",  # kebab-case or snake_case
        "docs_preferred": r"^[a-z0-9\-]+\.md$",  # kebab-case preferred
        "folder_pattern": r"^[a-z0-9\-_]+$",  # kebab-case or snake_case
        "folder_preferred": r"^[a-z0-9\-]+$",  # kebab-case preferred
    },
    "dated_files": {
        "allowed_locations": ["docs/_active", "docs/_archive"],
        "pattern": r"-202[0-9]-",  # Files with dates in name
    },
}


class FolderValidator:
    """Validates project folder structure."""

    def __init__(self, project_root: Path, fix: bool = False):
        self.project_root = project_root
        self.fix = fix
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []

    def validate_all(self) -> bool:
        """Run all validation checks."""
        print("🔍 Validating folder structure...")
        print()

        self.check_root_files()
        self.check_docs_root_files()
        self.check_agents_root_files()
        self.check_category_folders()
        self.check_dated_files()
        self.check_naming_conventions()
        self.check_duplicate_folders()

        return self.print_results()

    def check_root_files(self):
        """Check project root file count and content."""
        root_files = [
            f
            for f in self.project_root.iterdir()
            if f.is_file() and not f.name.startswith(".")
        ]

        if len(root_files) > RULES["root"]["max_files"]:
            self.errors.append(
                f"Root directory has {len(root_files)} files, "
                f"max is {RULES['root']['max_files']}"
            )

        # Check for unexpected files
        allowed = RULES["root"]["allowed_files"]
        for file in root_files:
            if file.name not in allowed:
                # Check if extension is allowed
                if file.suffix not in RULES["root"]["allowed_extensions"]:
                    self.warnings.append(
                        f"Unexpected file in root: {file.name} "
                        f"(not in allowed list and extension not recognized)"
                    )

    def check_docs_root_files(self):
        """Check docs/ root file count."""
        docs_path = self.project_root / "docs"
        if not docs_path.exists():
            self.errors.append("docs/ directory not found")
            return

        docs_files = [
            f for f in docs_path.iterdir() if f.is_file() and f.suffix == ".md"
        ]

        if len(docs_files) > RULES["docs_root"]["max_files"]:
            self.errors.append(
                f"docs/ root has {len(docs_files)} files, "
                f"max is {RULES['docs_root']['max_files']}"
            )
            self.errors.append(f"  Files: {[f.name for f in docs_files]}")

        # Check for unexpected files
        allowed = RULES["docs_root"]["allowed_files"]
        unexpected = [f for f in docs_files if f.name not in allowed]
        if unexpected:
            self.warnings.append(
                f"Unexpected files in docs/ root: {[f.name for f in unexpected]}"
            )

    def check_agents_root_files(self):
        """Check agents/ root file count."""
        agents_path = self.project_root / "agents"
        if not agents_path.exists():
            self.warnings.append("agents/ directory not found")
            return

        agents_files = [
            f for f in agents_path.iterdir() if f.is_file() and f.suffix == ".md"
        ]

        if len(agents_files) > RULES["agents_root"]["max_files"]:
            self.errors.append(
                f"agents/ root has {len(agents_files)} files, "
                f"max is {RULES['agents_root']['max_files']}"
            )
            self.errors.append(f"  Files: {[f.name for f in agents_files]}")

    def check_category_folders(self):
        """Check required category folders exist and have README."""
        for folder in RULES["category_folders"]["required"]:
            folder_path = self.project_root / folder
            if not folder_path.exists():
                self.warnings.append(f"Required folder not found: {folder}/")
            elif RULES["category_folders"]["must_have_readme"]:
                readme = folder_path / "README.md"
                if not readme.exists():
                    self.warnings.append(
                        f"Category folder missing README.md: {folder}/"
                    )

    def check_dated_files(self):
        """Check dated files are in allowed locations."""
        pattern = re.compile(RULES["dated_files"]["pattern"])
        allowed_locations = RULES["dated_files"]["allowed_locations"]

        # Search all markdown files
        for md_file in self.project_root.rglob("*.md"):
            if pattern.search(md_file.name):
                # Check if in allowed location
                rel_path = md_file.relative_to(self.project_root)
                in_allowed = any(
                    str(rel_path).startswith(loc) for loc in allowed_locations
                )

                if not in_allowed:
                    self.errors.append(
                        f"Dated file in wrong location: {rel_path} "
                        f"(should be in {' or '.join(allowed_locations)}/)"
                    )

    def check_naming_conventions(self):
        """Check file and folder naming conventions."""
        docs_pattern = re.compile(RULES["naming"]["docs_pattern"])
        docs_preferred = re.compile(RULES["naming"]["docs_preferred"])
        folder_pattern = re.compile(RULES["naming"]["folder_pattern"])
        folder_preferred = re.compile(RULES["naming"]["folder_preferred"])

        # Check markdown files in docs/
        docs_path = self.project_root / "docs"
        if docs_path.exists():
            for md_file in docs_path.rglob("*.md"):
                filename = md_file.name

                # Skip special files
                if filename in ["README.md", "TASKS.md", "SESSION_LOG.md", "CHANGELOG.md"]:
                    continue

                # Check if matches pattern
                if not docs_pattern.match(filename):
                    self.errors.append(
                        f"Invalid doc filename (must be kebab-case or snake_case): {md_file.relative_to(self.project_root)}"
                    )
                elif not docs_preferred.match(filename):
                    self.warnings.append(
                        f"Doc filename should use kebab-case (not snake_case): {md_file.relative_to(self.project_root)}"
                    )

        # Check folder names
        for folder in docs_path.rglob("*"):
            if folder.is_dir() and not folder.name.startswith("."):
                folder_name = folder.name

                # Skip special folders
                if folder_name in ["images", "assets", "_active", "_archive", "adr"]:
                    continue

                if not folder_pattern.match(folder_name):
                    self.errors.append(
                        f"Invalid folder name: {folder.relative_to(self.project_root)} "
                        f"(must be kebab-case or snake_case)"
                    )
                elif not folder_preferred.match(folder_name):
                    self.warnings.append(
                        f"Folder should use kebab-case (not snake_case): {folder.relative_to(self.project_root)}"
                    )

    def check_duplicate_folders(self):
        """Check for duplicate folder concepts."""
        docs_path = self.project_root / "docs"
        if not docs_path.exists():
            return

        # Check for old problematic folders
        problematic = [
            "_internal",
            "_references",
            "planning",
            "research",
        ]

        for folder_name in problematic:
            folder = docs_path / folder_name
            if folder.exists():
                # Check if it has files
                files = list(folder.rglob("*"))
                if files:
                    self.warnings.append(
                        f"Legacy folder still has content: docs/{folder_name}/ "
                        f"({len(files)} items) - should be migrated"
                    )

    def print_results(self) -> bool:
        """Print validation results."""
        print()
        print("=" * 60)

        if self.errors:
            print(f"❌ {len(self.errors)} ERROR(S) FOUND:")
            for error in self.errors:
                print(f"  • {error}")
            print()

        if self.warnings:
            print(f"⚠️  {len(self.warnings)} WARNING(S):")
            for warning in self.warnings:
                print(f"  • {warning}")
            print()

        if self.info:
            print(f"ℹ️  {len(self.info)} INFO:")
            for info_msg in self.info:
                print(f"  • {info_msg}")
            print()

        if not self.errors and not self.warnings:
            print("✅ Folder structure is valid!")
            print()
            return True
        elif not self.errors:
            print("✅ No errors (only warnings)")
            print()
            return True
        else:
            print("❌ Folder structure has errors")
            print()
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate folder structure against governance rules"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Attempt to auto-fix some issues (not implemented yet)",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate detailed report",
    )
    args = parser.parse_args()

    # Find project root (where README.md and docs/ exist)
    # First check if we're already in project root
    script_path = Path(__file__).resolve()

    # Try from script location first (scripts/ folder)
    project_root = script_path.parent.parent

    # If that doesn't work, search up from cwd
    if not ((project_root / "README.md").exists() and (project_root / "docs").exists()):
        current = Path.cwd()
        project_root = current
        while project_root != project_root.parent:
            if (project_root / "README.md").exists() and (project_root / "docs").exists():
                break
            project_root = project_root.parent

    if not ((project_root / "README.md").exists() and (project_root / "docs").exists()):
        print("❌ Could not find project root (no README.md or docs/)")
        print(f"   Searched from: {Path.cwd()}")
        print(f"   Script location: {script_path}")
        sys.exit(1)

    print(f"Project root: {project_root}")
    print()

    validator = FolderValidator(project_root, fix=args.fix)
    success = validator.validate_all()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
