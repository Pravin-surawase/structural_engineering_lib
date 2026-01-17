#!/usr/bin/env python3
"""Validate Python library folder structure for multi-code architecture.

Purpose:
    Ensures structural_lib follows the enterprise folder structure:
    - core/ module with base classes
    - codes/ module with code-specific implementations
    - Proper __init__.py files
    - Required exports

Usage:
    python scripts/check_folder_structure.py          # Check structure
    python scripts/check_folder_structure.py --json   # JSON output
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
STRUCTURAL_LIB = PROJECT_ROOT / "Python" / "structural_lib"

# Required structure
REQUIRED_FOLDERS = [
    "core",
    "codes",
    "codes/is456",
]

REQUIRED_FILES = {
    "core/__init__.py": ["CodeRegistry", "RectangularSection", "MaterialFactory"],
    "core/base.py": ["DesignCode", "DesignResult", "FlexureDesigner"],
    "core/materials.py": ["Concrete", "Steel", "MaterialFactory"],
    "core/geometry.py": ["Section", "RectangularSection", "TSection"],
    "core/registry.py": ["CodeRegistry", "register_code"],
    "codes/__init__.py": ["is456"],
    "codes/is456/__init__.py": ["IS456Code"],
}

OPTIONAL_FOLDERS = [
    "codes/aci318",
    "codes/ec2",
    "integration",
    "utils",
]


def check_folder_exists(folder: str) -> tuple[bool, str]:
    """Check if required folder exists."""
    path = STRUCTURAL_LIB / folder
    if path.exists() and path.is_dir():
        return True, f"✅ {folder}/"
    return False, f"❌ {folder}/ MISSING"


def check_file_exports(file_path: str, required_exports: list[str]) -> tuple[bool, str]:
    """Check if file exists and has required exports."""
    path = STRUCTURAL_LIB / file_path
    if not path.exists():
        return False, f"❌ {file_path} MISSING"

    content = path.read_text()
    missing = []
    for export in required_exports:
        # Check for class, function, or import
        if export not in content:
            missing.append(export)

    if missing:
        return False, f"⚠️  {file_path} missing exports: {', '.join(missing)}"

    return True, f"✅ {file_path}"


def check_code_registration() -> tuple[bool, str]:
    """Check if IS456 code is properly registered."""
    try:
        # Import to trigger registration
        sys.path.insert(0, str(PROJECT_ROOT / "Python"))
        from structural_lib.core import CodeRegistry
        from structural_lib.codes import is456  # noqa: F401

        if CodeRegistry.is_registered("IS456"):
            return True, "✅ IS456 registered in CodeRegistry"
        return False, "❌ IS456 not registered in CodeRegistry"
    except ImportError as e:
        return False, f"❌ Import error: {e}"


def run_checks() -> dict:
    """Run all structure checks."""
    results = {
        "folders": {"required": [], "optional": []},
        "files": [],
        "registration": None,
        "summary": {"passed": 0, "failed": 0, "warnings": 0},
    }

    # Check required folders
    for folder in REQUIRED_FOLDERS:
        passed, msg = check_folder_exists(folder)
        results["folders"]["required"].append(
            {"folder": folder, "passed": passed, "message": msg}
        )
        if passed:
            results["summary"]["passed"] += 1
        else:
            results["summary"]["failed"] += 1

    # Check optional folders
    for folder in OPTIONAL_FOLDERS:
        passed, msg = check_folder_exists(folder)
        if passed:
            msg = msg.replace("✅", "✓")  # Different marker for optional
        else:
            msg = f"○ {folder}/ (optional, not yet created)"
        results["folders"]["optional"].append(
            {"folder": folder, "passed": passed, "message": msg}
        )

    # Check required files and exports
    for file_path, exports in REQUIRED_FILES.items():
        passed, msg = check_file_exports(file_path, exports)
        results["files"].append({"file": file_path, "passed": passed, "message": msg})
        if passed:
            results["summary"]["passed"] += 1
        elif "⚠️" in msg:
            results["summary"]["warnings"] += 1
        else:
            results["summary"]["failed"] += 1

    # Check code registration
    passed, msg = check_code_registration()
    results["registration"] = {"passed": passed, "message": msg}
    if passed:
        results["summary"]["passed"] += 1
    else:
        results["summary"]["failed"] += 1

    return results


def print_report(results: dict) -> None:
    """Print human-readable report."""
    print("🏗️  Folder Structure Validation")
    print("=" * 50)

    print("\n📁 Required Folders:")
    for item in results["folders"]["required"]:
        print(f"   {item['message']}")

    print("\n📁 Optional Folders:")
    for item in results["folders"]["optional"]:
        print(f"   {item['message']}")

    print("\n📄 Required Files & Exports:")
    for item in results["files"]:
        print(f"   {item['message']}")

    print("\n🔌 Code Registration:")
    print(f"   {results['registration']['message']}")

    print("\n" + "=" * 50)
    summary = results["summary"]
    total = summary["passed"] + summary["failed"] + summary["warnings"]
    print(f"Summary: {summary['passed']}/{total} passed", end="")
    if summary["warnings"]:
        print(f", {summary['warnings']} warnings", end="")
    if summary["failed"]:
        print(f", {summary['failed']} failed", end="")
    print()

    if summary["failed"] == 0:
        print("\n✅ All structure checks passed!")
    else:
        print("\n❌ Some checks failed. See above for details.")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate folder structure")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    results = run_checks()

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_report(results)

    # Exit code: 0 if no failures, 1 if failures
    return 1 if results["summary"]["failed"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
