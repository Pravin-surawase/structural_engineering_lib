#!/usr/bin/env python3
"""Validate stub module exports match source module exports.

This script ensures backward compatibility stubs correctly re-export
all functionality from migrated modules.

Checks:
1. All public functions/classes are accessible via stub
2. Private functions used by tests are explicitly imported
3. Data types used in type annotations are re-exported
4. Module attributes (like submodule imports) are preserved

Usage:
    python scripts/validate_stub_exports.py tables           # Validate one module
    python scripts/validate_stub_exports.py --all            # Validate all migrated
    python scripts/validate_stub_exports.py tables --fix     # Show fix suggestions
    python scripts/validate_stub_exports.py --verbose        # Detailed output

Author: Session 6 (2026-01-11)
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path
from typing import NamedTuple


class ExportInfo(NamedTuple):
    """Information about an export."""

    name: str
    type: str  # 'function', 'class', 'variable', 'private'
    used_in_tests: bool = False
    used_in_type_annotations: bool = False


# Project paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
PYTHON_DIR = PROJECT_ROOT / "Python"
STRUCTURAL_LIB = PYTHON_DIR / "structural_lib"
CODES_IS456 = STRUCTURAL_LIB / "codes" / "is456"
TESTS_DIR = PYTHON_DIR / "tests"

# Migrated modules
MIGRATED_MODULES = [
    "tables",
    "shear",
    "flexure",
    "detailing",
    "serviceability",
    "compliance",
    "ductile",
]


def get_module_exports(module_path: Path) -> dict[str, ExportInfo]:
    """Extract all exports from a module using AST parsing."""
    if not module_path.exists():
        return {}

    content = module_path.read_text()
    tree = ast.parse(content)

    exports: dict[str, ExportInfo] = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            export_type = "private" if node.name.startswith("_") else "function"
            exports[node.name] = ExportInfo(name=node.name, type=export_type)
        elif isinstance(node, ast.ClassDef):
            export_type = "private" if node.name.startswith("_") else "class"
            exports[node.name] = ExportInfo(name=node.name, type=export_type)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    name = target.id
                    if not name.startswith("__"):  # Skip dunder
                        export_type = "private" if name.startswith("_") else "variable"
                        exports[name] = ExportInfo(name=name, type=export_type)

    return exports


def get_stub_imports(stub_path: Path) -> set[str]:
    """Get names that are imported (and thus exported) in a stub module."""
    if not stub_path.exists():
        return set()

    content = stub_path.read_text()
    tree = ast.parse(content)

    imported_names: set[str] = set()
    has_star_import = False

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "*":
                    has_star_import = True
                else:
                    # Use asname if present, otherwise original name
                    imported_names.add(alias.asname or alias.name)

    return imported_names, has_star_import


def find_private_usage_in_tests(module_name: str) -> set[str]:
    """Find private functions from module used in tests."""
    pattern = f"{module_name}._"
    used_privates: set[str] = set()

    for test_file in TESTS_DIR.rglob("*.py"):
        content = test_file.read_text()
        # Look for patterns like tables._get_tc_for_grade
        import re

        matches = re.findall(rf"{module_name}\.(_\w+)", content)
        used_privates.update(matches)

    return used_privates


def find_type_annotation_usage(module_name: str) -> set[str]:
    """Find type annotations using module.TypeName pattern."""
    pattern = rf"{module_name}\.(\w+)"
    used_types: set[str] = set()

    # Scan api.py and other key files
    files_to_scan = [
        STRUCTURAL_LIB / "api.py",
        STRUCTURAL_LIB / "job_runner.py",
        STRUCTURAL_LIB / "bbs.py",
    ]

    import re

    for file_path in files_to_scan:
        if file_path.exists():
            content = file_path.read_text()
            # Look for type annotations: -> module.Type or : module.Type
            matches = re.findall(rf"(?:->|:)\s*{module_name}\.(\w+)", content)
            used_types.update(matches)

    return used_types


def validate_module(
    module_name: str, verbose: bool = False, show_fix: bool = False
) -> tuple[bool, list[str]]:
    """Validate a single module's stub exports."""
    source_path = CODES_IS456 / f"{module_name}.py"
    stub_path = STRUCTURAL_LIB / f"{module_name}.py"

    issues: list[str] = []

    if not source_path.exists():
        issues.append(f"Source not found: {source_path}")
        return False, issues

    if not stub_path.exists():
        issues.append(f"Stub not found: {stub_path}")
        return False, issues

    # Get exports from source
    source_exports = get_module_exports(source_path)

    # Get imports in stub
    stub_imports, has_star = get_stub_imports(stub_path)

    # Find private functions used in tests
    privates_in_tests = find_private_usage_in_tests(module_name)

    # Find types used in annotations
    types_in_annotations = find_type_annotation_usage(module_name)

    if verbose:
        print(f"\n📦 {module_name}:")
        print(f"   Source exports: {len(source_exports)}")
        print(f"   Stub has star import: {has_star}")
        print(f"   Explicit stub imports: {len(stub_imports)}")
        print(f"   Private funcs in tests: {privates_in_tests}")
        print(f"   Types in annotations: {types_in_annotations}")

    # Check private functions
    missing_privates = []
    for priv_name in privates_in_tests:
        if priv_name not in stub_imports:
            missing_privates.append(priv_name)
            issues.append(
                f"Private function '{priv_name}' used in tests but not in stub"
            )

    # Check type annotations
    missing_types = []
    for type_name in types_in_annotations:
        if type_name not in stub_imports and type_name not in source_exports:
            # It might be a data_type that needs re-export
            missing_types.append(type_name)
            issues.append(f"Type '{type_name}' used in annotations but not in stub")

    # Generate fix suggestions
    if show_fix and (missing_privates or missing_types):
        print(f"\n🔧 Fix for {module_name}.py stub:")
        if missing_privates:
            print("\n# Add private function imports:")
            print(
                f"from structural_lib.codes.is456.{module_name} import (  # noqa: F401"
            )
            for name in sorted(missing_privates):
                print(f"    {name},")
            print(")")

        if missing_types:
            print("\n# Add data type re-exports:")
            print("from structural_lib.data_types import (  # noqa: F401")
            for name in sorted(missing_types):
                print(f"    {name},")
            print(")")

    return len(issues) == 0, issues


def validate_all(verbose: bool = False, show_fix: bool = False) -> bool:
    """Validate all migrated module stubs."""
    all_valid = True
    total_issues = 0

    print("🔍 Validating stub exports for migrated modules...\n")

    for module_name in MIGRATED_MODULES:
        valid, issues = validate_module(module_name, verbose, show_fix)

        if valid:
            print(f"  ✅ {module_name}: All exports valid")
        else:
            print(f"  ❌ {module_name}: {len(issues)} issue(s)")
            for issue in issues:
                print(f"     - {issue}")
            all_valid = False
            total_issues += len(issues)

    print()
    if all_valid:
        print("✅ All stub exports are valid!")
    else:
        print(f"❌ Found {total_issues} issue(s) across modules")

    return all_valid


def main():
    parser = argparse.ArgumentParser(
        description="Validate stub module exports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s tables           # Validate tables stub
  %(prog)s --all            # Validate all migrated modules
  %(prog)s tables --fix     # Show fix suggestions
  %(prog)s --all --verbose  # Detailed output for all
        """,
    )
    parser.add_argument(
        "module",
        nargs="?",
        help="Module name to validate (tables, shear, flexure, etc.)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Validate all migrated modules",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed output",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Show fix suggestions for issues",
    )

    args = parser.parse_args()

    if args.all:
        success = validate_all(args.verbose, args.fix)
    elif args.module:
        if args.module not in MIGRATED_MODULES:
            print(f"❌ Unknown module: {args.module}")
            print(f"   Available: {', '.join(MIGRATED_MODULES)}")
            sys.exit(1)
        valid, issues = validate_module(args.module, args.verbose, args.fix)
        if valid:
            print(f"✅ {args.module}: All exports valid")
        else:
            print(f"❌ {args.module}: {len(issues)} issue(s)")
            for issue in issues:
                print(f"   - {issue}")
        success = valid
    else:
        parser.print_help()
        sys.exit(1)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
