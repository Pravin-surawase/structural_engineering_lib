#!/usr/bin/env python3
"""Validate IS 456 module migration status.

Comprehensive validation that checks:
1. All expected modules are migrated
2. Re-export stubs work correctly
3. Old import paths still work
4. New import paths work
5. Tests pass

Usage:
    python scripts/validate_migration.py
    python scripts/validate_migration.py --verbose
    python scripts/validate_migration.py --run-tests
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

# Get project root
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
STRUCTURAL_LIB = PROJECT_ROOT / "Python" / "structural_lib"
CODES_IS456 = STRUCTURAL_LIB / "codes" / "is456"

# Modules that should be migrated
EXPECTED_MODULES = [
    "tables",
    "shear",
    "flexure",
    "detailing",
    "serviceability",
    "compliance",
    "ductile",
]

# Key functions to verify for each module
KEY_EXPORTS = {
    "flexure": [
        "calculate_ast_required",
        "calculate_mu_lim",
        "design_singly_reinforced",
        "design_doubly_reinforced",
        "design_flanged_beam",
    ],
    "shear": [
        "calculate_tv",
        "design_shear",
    ],
    "detailing": [
        "calculate_development_length",
        "calculate_lap_length",
        "calculate_bar_spacing",
        "check_min_spacing",
    ],
    "tables": [
        "lookup_tc",
        "lookup_tcmax",
    ],
    "serviceability": [
        "check_deflection_span_depth",
        "check_crack_width",
    ],
    "compliance": [
        "check_compliance_report",
    ],
    "ductile": [
        "check_ductile_detailing",
    ],
}


def run_command(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    result = subprocess.run(
        cmd,
        cwd=cwd or PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


class ValidationResult:
    """Container for validation results."""

    def __init__(self):
        self.passed: list[str] = []
        self.failed: list[str] = []
        self.skipped: list[str] = []

    def add_pass(self, msg: str) -> None:
        self.passed.append(msg)

    def add_fail(self, msg: str) -> None:
        self.failed.append(msg)

    def add_skip(self, msg: str) -> None:
        self.skipped.append(msg)

    @property
    def success(self) -> bool:
        return len(self.failed) == 0


def validate_file_structure(result: ValidationResult, verbose: bool) -> None:
    """Validate that files exist in expected locations."""
    print("\n📁 Validating file structure...")

    for mod in EXPECTED_MODULES:
        migrated = CODES_IS456 / f"{mod}.py"
        stub = STRUCTURAL_LIB / f"{mod}.py"

        if not migrated.exists():
            result.add_fail(f"{mod}.py not in codes/is456/")
            if verbose:
                print(f"  ❌ Missing: {migrated}")
            continue

        result.add_pass(f"{mod}.py in codes/is456/")
        if verbose:
            print(f"  ✅ Found: {migrated}")

        if not stub.exists():
            result.add_fail(f"{mod}.py stub missing at root")
            if verbose:
                print(f"  ❌ Missing stub: {stub}")
            continue

        # Check stub content
        content = stub.read_text()
        if "Backward compatibility stub" not in content:
            result.add_fail(f"{mod}.py is original, not stub")
            if verbose:
                print(f"  ❌ Not a stub: {stub}")
        else:
            result.add_pass(f"{mod}.py has proper stub")
            if verbose:
                print(f"  ✅ Stub OK: {stub}")


def validate_imports(result: ValidationResult, verbose: bool) -> None:
    """Validate that all import patterns work."""
    print("\n📦 Validating imports...")

    python = PROJECT_ROOT / ".venv" / "bin" / "python"

    for mod in EXPECTED_MODULES:
        # Test 1: from structural_lib import mod
        test_code = f"from structural_lib import {mod}; print('OK')"
        code, stdout, stderr = run_command(
            [str(python), "-c", test_code],
            cwd=PROJECT_ROOT / "Python",
        )
        if code == 0 and "OK" in stdout:
            result.add_pass(f"from structural_lib import {mod}")
            if verbose:
                print(f"  ✅ from structural_lib import {mod}")
        else:
            result.add_fail(f"from structural_lib import {mod}")
            if verbose:
                print(f"  ❌ from structural_lib import {mod}: {stderr[:100]}")
            continue

        # Test 2: from structural_lib.mod import *
        test_code = f"from structural_lib.{mod} import *; print('OK')"
        code, stdout, stderr = run_command(
            [str(python), "-c", test_code],
            cwd=PROJECT_ROOT / "Python",
        )
        if code == 0 and "OK" in stdout:
            result.add_pass(f"from structural_lib.{mod} import *")
            if verbose:
                print(f"  ✅ from structural_lib.{mod} import *")
        else:
            result.add_fail(f"from structural_lib.{mod} import *")
            if verbose:
                print(f"  ❌ from structural_lib.{mod} import *: {stderr[:100]}")

        # Test 3: from structural_lib.codes.is456.mod import *
        test_code = f"from structural_lib.codes.is456.{mod} import *; print('OK')"
        code, stdout, stderr = run_command(
            [str(python), "-c", test_code],
            cwd=PROJECT_ROOT / "Python",
        )
        if code == 0 and "OK" in stdout:
            result.add_pass(f"from structural_lib.codes.is456.{mod} import *")
            if verbose:
                print(f"  ✅ from structural_lib.codes.is456.{mod} import *")
        else:
            result.add_fail(f"from structural_lib.codes.is456.{mod} import *")
            if verbose:
                print(
                    f"  ❌ from structural_lib.codes.is456.{mod} import *: {stderr[:100]}"
                )


def validate_key_exports(result: ValidationResult, verbose: bool) -> None:
    """Validate that key functions are accessible."""
    print("\n🔧 Validating key exports...")

    python = PROJECT_ROOT / ".venv" / "bin" / "python"

    for mod, funcs in KEY_EXPORTS.items():
        migrated = CODES_IS456 / f"{mod}.py"
        if not migrated.exists():
            result.add_skip(f"Skipping {mod} exports (not migrated)")
            continue

        for func in funcs:
            # Test via old path
            test_code = f"from structural_lib.{mod} import {func}; print('OK')"
            code, stdout, stderr = run_command(
                [str(python), "-c", test_code],
                cwd=PROJECT_ROOT / "Python",
            )
            if code == 0 and "OK" in stdout:
                result.add_pass(f"{mod}.{func} via old path")
                if verbose:
                    print(f"  ✅ {mod}.{func}")
            else:
                result.add_fail(f"{mod}.{func} via old path")
                if verbose:
                    print(f"  ❌ {mod}.{func}: {stderr[:100]}")


def validate_code_registry(result: ValidationResult, verbose: bool) -> None:
    """Validate that CodeRegistry works."""
    print("\n📋 Validating CodeRegistry...")

    python = PROJECT_ROOT / ".venv" / "bin" / "python"

    # Check IS456 is registered
    test_code = """
from structural_lib.core import CodeRegistry
from structural_lib.codes.is456 import IS456Code

is_reg = CodeRegistry.is_registered("IS456")
print(f"IS456 registered: {is_reg}")

if is_reg:
    code = CodeRegistry.get("IS456")
    print(f"Code: {code.code_name}")
"""
    code, stdout, stderr = run_command(
        [str(python), "-c", test_code],
        cwd=PROJECT_ROOT / "Python",
    )

    if "IS456 registered: True" in stdout:
        result.add_pass("CodeRegistry.is_registered('IS456')")
        if verbose:
            print("  ✅ IS456 registered in CodeRegistry")
    else:
        result.add_fail("CodeRegistry.is_registered('IS456')")
        if verbose:
            print(f"  ❌ CodeRegistry issue: {stderr[:200]}")

    if "Indian Standard" in stdout:
        result.add_pass("CodeRegistry.get('IS456') works")
        if verbose:
            print("  ✅ CodeRegistry.get('IS456') returns valid code")
    elif "IS456 registered: True" in stdout:
        result.add_fail("CodeRegistry.get('IS456') failed")


def validate_tests(result: ValidationResult, verbose: bool) -> None:
    """Run the test suite."""
    print("\n🧪 Running test suite...")

    python = PROJECT_ROOT / ".venv" / "bin" / "python"
    code, stdout, stderr = run_command(
        [str(python), "-m", "pytest", "Python/tests/", "-q", "--tb=no"],
        cwd=PROJECT_ROOT,
    )

    if code == 0:
        # Extract pass count
        for line in stdout.split("\n"):
            if "passed" in line:
                result.add_pass(f"Tests: {line.strip()}")
                if verbose:
                    print(f"  ✅ {line.strip()}")
                return
        result.add_pass("All tests passed")
    else:
        # Extract failure info
        result.add_fail(f"Tests failed")
        if verbose:
            print(f"  ❌ Test failures detected")
            for line in stderr.split("\n")[:10]:
                print(f"     {line}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate IS 456 module migration")
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed output",
    )
    parser.add_argument(
        "--run-tests",
        action="store_true",
        help="Also run the full test suite",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick validation (skip tests)",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("IS 456 MODULE MIGRATION VALIDATION")
    print("=" * 60)

    result = ValidationResult()

    # Run validations
    validate_file_structure(result, args.verbose)
    validate_imports(result, args.verbose)
    validate_key_exports(result, args.verbose)
    validate_code_registry(result, args.verbose)

    if args.run_tests and not args.quick:
        validate_tests(result, args.verbose)

    # Summary
    print()
    print("=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"  ✅ Passed:  {len(result.passed)}")
    print(f"  ❌ Failed:  {len(result.failed)}")
    print(f"  ⏭️  Skipped: {len(result.skipped)}")
    print()

    if result.failed:
        print("Failed checks:")
        for fail in result.failed:
            print(f"  ❌ {fail}")
        print()
        return 1

    print("✅ All validations passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
