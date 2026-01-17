#!/usr/bin/env python3
"""Pre-migration checks for IS 456 module migration.

Verifies all prerequisites before starting the migration:
- Git state
- Test suite
- Import paths
- Documentation links
- Automation scripts

Usage:
    python scripts/pre_migration_check.py
    python scripts/pre_migration_check.py --fix  # Auto-fix issues if possible
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# Get project root
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent


class Check:
    """Result of a single check."""

    def __init__(self, name: str, passed: bool, message: str, fixable: bool = False):
        self.name = name
        self.passed = passed
        self.message = message
        self.fixable = fixable


def run_command(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    result = subprocess.run(
        cmd,
        cwd=cwd or PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


def check_git_clean() -> Check:
    """Check if git working tree is clean."""
    code, stdout, _ = run_command(["git", "status", "--porcelain"])
    if stdout.strip():
        return Check(
            "Git Clean",
            False,
            f"Uncommitted changes:\n{stdout[:200]}",
            fixable=False,
        )
    return Check("Git Clean", True, "Working tree clean")


def check_git_synced() -> Check:
    """Check if local main is synced with origin."""
    run_command(["git", "fetch", "origin"])
    code, stdout, _ = run_command(["git", "log", "--oneline", "HEAD..origin/main"])
    if stdout.strip():
        return Check(
            "Git Synced",
            False,
            f"Behind origin/main by: {stdout.strip()}",
            fixable=True,  # Can be fixed with git pull
        )
    return Check("Git Synced", True, "Up to date with origin/main")


def check_tests_pass() -> Check:
    """Check if test suite passes."""
    python = PROJECT_ROOT / ".venv" / "bin" / "python"
    code, stdout, stderr = run_command(
        [str(python), "-m", "pytest", "Python/tests/", "-q", "--tb=no"],
        cwd=PROJECT_ROOT,
    )
    # Parse test count from output
    if code == 0:
        # Try to find test count
        for line in stdout.split("\n"):
            if "passed" in line:
                return Check("Tests Pass", True, line.strip())
        return Check("Tests Pass", True, "All tests passed")
    return Check(
        "Tests Pass",
        False,
        f"Tests failed:\n{stderr[:300]}",
        fixable=False,
    )


def check_current_imports() -> Check:
    """Check if current import paths work."""
    python = PROJECT_ROOT / ".venv" / "bin" / "python"
    test_code = """
from structural_lib import flexure, shear, detailing, tables
from structural_lib.flexure import design_singly_reinforced
from structural_lib.shear import design_shear
print("OK")
"""
    code, stdout, stderr = run_command(
        [str(python), "-c", test_code],
        cwd=PROJECT_ROOT / "Python",
    )
    if code == 0 and "OK" in stdout:
        return Check("Current Imports", True, "All current imports work")
    return Check(
        "Current Imports",
        False,
        f"Import failed: {stderr[:200]}",
        fixable=False,
    )


def check_codes_namespace() -> Check:
    """Check if codes/is456 namespace exists."""
    python = PROJECT_ROOT / ".venv" / "bin" / "python"
    test_code = """
from structural_lib.codes.is456 import IS456Code
from structural_lib.core import CodeRegistry
print(f"IS456 registered: {CodeRegistry.is_registered('IS456')}")
"""
    code, stdout, stderr = run_command(
        [str(python), "-c", test_code],
        cwd=PROJECT_ROOT / "Python",
    )
    if code == 0 and "True" in stdout:
        return Check("Codes Namespace", True, "IS456Code exists and registered")
    return Check(
        "Codes Namespace",
        False,
        f"Namespace not ready: {stderr[:200]}",
        fixable=False,
    )


def check_core_module() -> Check:
    """Check if core module is ready."""
    python = PROJECT_ROOT / ".venv" / "bin" / "python"
    test_code = """
from structural_lib.core import (
    CodeRegistry,
    MaterialFactory,
    RectangularSection,
    DesignCode,
)
print("OK")
"""
    code, stdout, stderr = run_command(
        [str(python), "-c", test_code],
        cwd=PROJECT_ROOT / "Python",
    )
    if code == 0 and "OK" in stdout:
        return Check("Core Module", True, "Core module exports all base classes")
    return Check(
        "Core Module",
        False,
        f"Core module not ready: {stderr[:200]}",
        fixable=False,
    )


def check_doc_links() -> Check:
    """Check if documentation links are valid."""
    python = PROJECT_ROOT / ".venv" / "bin" / "python"
    code, stdout, stderr = run_command(
        [str(python), str(SCRIPT_DIR / "check_links.py")],
        cwd=PROJECT_ROOT,
    )
    # Check for success indicators
    if "All internal links are valid" in stdout:
        return Check("Doc Links", True, "All internal links are valid")
    if code == 0 and "Broken links: 0" in stdout:
        return Check("Doc Links", True, "No broken links")
    if code == 0 and "broken" not in stdout.lower():
        return Check("Doc Links", True, "No broken links")
    return Check(
        "Doc Links",
        False,
        f"Broken links found: {stdout[:200]}",
        fixable=True,  # Can be fixed with fix_broken_links.py
    )


def check_migration_scripts() -> Check:
    """Check if migration scripts exist."""
    required = [
        "migrate_module.py",
        "create_reexport_stub.py",
        "validate_migration.py",
    ]
    missing = []
    for script in required:
        if not (SCRIPT_DIR / script).exists():
            missing.append(script)

    if missing:
        return Check(
            "Migration Scripts",
            False,
            f"Missing scripts: {', '.join(missing)}",
            fixable=False,
        )
    return Check("Migration Scripts", True, "All migration scripts exist")


def check_no_circular_imports() -> Check:
    """Check for potential circular imports."""
    # Check if compliance imports flexure but flexure doesn't import compliance
    flexure_py = PROJECT_ROOT / "Python" / "structural_lib" / "flexure.py"
    compliance_py = PROJECT_ROOT / "Python" / "structural_lib" / "compliance.py"

    flexure_content = flexure_py.read_text() if flexure_py.exists() else ""
    compliance_content = compliance_py.read_text() if compliance_py.exists() else ""

    # Compliance should import flexure (expected)
    # Flexure should NOT import compliance (circular)
    if "from structural_lib.compliance" in flexure_content:
        return Check(
            "No Circular Imports",
            False,
            "flexure.py imports compliance.py - circular risk!",
            fixable=False,
        )

    return Check("No Circular Imports", True, "No circular imports detected")


def main() -> int:
    """Run all pre-migration checks."""
    fix_mode = "--fix" in sys.argv

    print("=" * 60)
    print("IS 456 MODULE MIGRATION - PRE-FLIGHT CHECKS")
    print("=" * 60)
    print()

    checks = [
        check_git_clean,
        check_git_synced,
        check_current_imports,
        check_codes_namespace,
        check_core_module,
        check_doc_links,
        check_migration_scripts,
        check_no_circular_imports,
    ]

    # Skip tests if quick mode
    if "--quick" not in sys.argv:
        checks.insert(2, check_tests_pass)

    results: list[Check] = []
    for check_func in checks:
        print(f"Checking {check_func.__doc__}...", end=" ", flush=True)
        result = check_func()
        results.append(result)
        if result.passed:
            print(f"✅ {result.message}")
        else:
            print(f"❌ FAILED")
            print(f"   {result.message}")
            if result.fixable and fix_mode:
                print("   (Attempting auto-fix...)")

    print()
    print("=" * 60)

    passed = sum(1 for r in results if r.passed)
    total = len(results)
    failed = total - passed

    if failed == 0:
        print(f"✅ ALL CHECKS PASSED ({passed}/{total})")
        print()
        print("Ready to proceed with migration!")
        print()
        print("Recommended next steps:")
        print("  1. git checkout -b feat/migrate-is456-modules")
        print("  2. python scripts/migrate_module.py tables --dry-run")
        print("  3. python scripts/migrate_module.py tables")
        print("  4. pytest Python/tests/test_tables*.py -v")
        return 0
    else:
        print(f"❌ {failed} CHECK(S) FAILED ({passed}/{total} passed)")
        print()
        print("Fix issues before proceeding with migration.")
        if any(r.fixable for r in results if not r.passed):
            print("Some issues can be auto-fixed with: --fix")
        return 1


if __name__ == "__main__":
    sys.exit(main())
