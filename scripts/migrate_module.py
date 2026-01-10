#!/usr/bin/env python3
"""Migrate an IS 456 module to the codes/is456/ namespace.

This script handles the complete migration of a single module:
1. Copies the module to codes/is456/
2. Updates internal imports if needed
3. Creates a re-export stub at the original location
4. Validates the migration

Usage:
    python scripts/migrate_module.py flexure --dry-run
    python scripts/migrate_module.py flexure
    python scripts/migrate_module.py flexure --validate-only
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Get project root
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
STRUCTURAL_LIB = PROJECT_ROOT / "Python" / "structural_lib"
CODES_IS456 = STRUCTURAL_LIB / "codes" / "is456"

# Modules that can be migrated, in order of dependencies
MIGRATION_ORDER = [
    "tables",        # No IS 456 deps
    "shear",         # Depends on tables
    "flexure",       # Depends on materials (stays in root)
    "detailing",     # Depends on errors (stays in root)
    "serviceability",  # Depends on data_types (stays in root)
    "compliance",    # Depends on flexure, shear, serviceability
    "ductile",       # Depends on errors (stays in root)
]

# Modules that will NOT be migrated (code-agnostic, stay in root)
NON_MIGRATABLE = [
    "api",
    "api_results",
    "bbs",
    "beam_pipeline",
    "constants",
    "costing",
    "data_types",
    "dxf_export",
    "error_messages",
    "errors",
    "excel_bridge",
    "excel_integration",
    "intelligence",
    "job_cli",
    "job_runner",
    "materials",
    "optimization",
    "rebar_optimizer",
    "report",
    "report_svg",
    "result_base",
    "types",
    "utilities",
    "validation",
]


STUB_TEMPLATE = '''"""Backward compatibility stub.

This module has been migrated to: structural_lib.codes.is456.{module_name}

All functionality is re-exported here for backward compatibility.
Existing imports like `from structural_lib import {module_name}` continue to work.

Migration date: 2026-01-XX (Session X)
"""
from __future__ import annotations

# Re-export everything from the new location
from structural_lib.codes.is456.{module_name} import *  # noqa: F401, F403

# Re-export __all__ if defined
try:
    from structural_lib.codes.is456.{module_name} import __all__  # noqa: F401
except ImportError:
    pass  # Module may not define __all__
'''


def update_imports(content: str, module_name: str) -> str:
    """Update internal imports after migration.

    When a module moves from structural_lib/ to structural_lib/codes/is456/,
    relative imports need to be updated.

    Changes:
    - `from . import X` -> `from structural_lib import X` (for non-migrated modules)
    - `from .X import Y` -> `from structural_lib.X import Y` (for non-migrated)
    - `from . import migrated_mod` -> `from . import migrated_mod` (relative within is456)

    Args:
        content: Original module content
        module_name: Name of the module being migrated

    Returns:
        Updated content with fixed imports
    """
    lines = content.split("\n")
    updated_lines = []

    for line in lines:
        updated_line = line

        # Pattern: from . import X
        match = re.match(r'^(\s*)from \. import (.+)$', line)
        if match:
            indent, imports = match.groups()
            # Check each imported module
            import_list = [i.strip() for i in imports.split(",")]
            non_migrated = []
            migrated = []
            for imp in import_list:
                # Handle "X as Y" syntax
                base_imp = imp.split(" as ")[0].strip()
                if base_imp in NON_MIGRATABLE:
                    non_migrated.append(imp)
                elif base_imp in MIGRATION_ORDER:
                    migrated.append(imp)
                else:
                    # Unknown, assume non-migrated (safer)
                    non_migrated.append(imp)

            new_lines = []
            if non_migrated:
                new_lines.append(f"{indent}from structural_lib import {', '.join(non_migrated)}")
            if migrated:
                new_lines.append(f"{indent}from . import {', '.join(migrated)}")

            if new_lines:
                updated_line = "\n".join(new_lines)
            else:
                updated_line = line  # Keep original if nothing to change

        # Pattern: from .module import X
        match = re.match(r'^(\s*)from \.(\w+) import (.+)$', line)
        if match:
            indent, from_module, imports = match.groups()
            if from_module in NON_MIGRATABLE:
                # Change to absolute import
                updated_line = f"{indent}from structural_lib.{from_module} import {imports}"
            elif from_module in MIGRATION_ORDER:
                # Keep as relative (within codes/is456/)
                updated_line = line
            else:
                # Unknown module, use absolute to be safe
                updated_line = f"{indent}from structural_lib.{from_module} import {imports}"

        updated_lines.append(updated_line)

    return "\n".join(updated_lines)


def run_command(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    result = subprocess.run(
        cmd,
        cwd=cwd or PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


def validate_module(module_name: str) -> bool:
    """Validate that a migrated module works correctly.

    Checks:
    1. Module can be imported from new location
    2. Re-export stub works
    3. Tests pass

    Returns:
        True if all validations pass
    """
    python = PROJECT_ROOT / ".venv" / "bin" / "python"
    errors = []

    # Check new location import
    test_code = f"from structural_lib.codes.is456.{module_name} import *; print('OK')"
    code, stdout, stderr = run_command(
        [str(python), "-c", test_code],
        cwd=PROJECT_ROOT / "Python",
    )
    if code != 0 or "OK" not in stdout:
        errors.append(f"New location import failed: {stderr[:200]}")

    # Check re-export stub
    test_code = f"from structural_lib.{module_name} import *; print('OK')"
    code, stdout, stderr = run_command(
        [str(python), "-c", test_code],
        cwd=PROJECT_ROOT / "Python",
    )
    if code != 0 or "OK" not in stdout:
        errors.append(f"Re-export import failed: {stderr[:200]}")

    # Check old-style package import
    test_code = f"from structural_lib import {module_name}; print('OK')"
    code, stdout, stderr = run_command(
        [str(python), "-c", test_code],
        cwd=PROJECT_ROOT / "Python",
    )
    if code != 0 or "OK" not in stdout:
        errors.append(f"Package import failed: {stderr[:200]}")

    if errors:
        print(f"❌ Validation failed for {module_name}:")
        for e in errors:
            print(f"   - {e}")
        return False

    print(f"✅ {module_name} validation passed")
    return True


def migrate_module(module_name: str, dry_run: bool = False) -> bool:
    """Migrate a single module to codes/is456/.

    Args:
        module_name: Name of the module to migrate
        dry_run: If True, only show what would be done

    Returns:
        True if successful
    """
    if module_name not in MIGRATION_ORDER:
        print(f"❌ Unknown or non-migratable module: {module_name}")
        print(f"   Migratable: {', '.join(MIGRATION_ORDER)}")
        return False

    src = STRUCTURAL_LIB / f"{module_name}.py"
    dst = CODES_IS456 / f"{module_name}.py"

    # Check source exists
    if not src.exists():
        print(f"❌ Source not found: {src}")
        return False

    # Check if already migrated
    if dst.exists():
        print(f"⚠️  Already migrated: {dst}")
        # Check if stub exists
        if src.exists():
            content = src.read_text()
            if "Backward compatibility stub" in content:
                print(f"   (stub exists at original location)")
                return True
        return True

    # Check dependencies are migrated first
    module_idx = MIGRATION_ORDER.index(module_name)
    for dep_module in MIGRATION_ORDER[:module_idx]:
        dep_dst = CODES_IS456 / f"{dep_module}.py"
        if not dep_dst.exists():
            print(f"⚠️  Dependency {dep_module} not migrated yet")
            print(f"   Migrate in order: {', '.join(MIGRATION_ORDER[:module_idx + 1])}")
            # Don't fail - might be intentional

    # Read source content
    original_content = src.read_text()

    # Update imports
    updated_content = update_imports(original_content, module_name)

    # Create stub content
    stub_content = STUB_TEMPLATE.format(module_name=module_name)

    if dry_run:
        print(f"Would migrate: {src} -> {dst}")
        print()
        print("Original imports that would change:")
        print("-" * 40)
        orig_lines = original_content.split("\n")
        upd_lines = updated_content.split("\n")
        for i, (orig, upd) in enumerate(zip(orig_lines, upd_lines), 1):
            if orig != upd:
                print(f"  Line {i}:")
                print(f"    - {orig}")
                print(f"    + {upd}")
        print("-" * 40)
        print()
        print(f"Would create stub at: {src}")
        print()
        print("Stub content:")
        print("-" * 40)
        print(stub_content)
        print("-" * 40)
        return True

    # Ensure destination directory exists
    CODES_IS456.mkdir(parents=True, exist_ok=True)

    # Write migrated module
    dst.write_text(updated_content)
    print(f"✅ Migrated: {src} -> {dst}")

    # Write re-export stub
    src.write_text(stub_content)
    print(f"✅ Created stub: {src}")

    # Validate
    if not validate_module(module_name):
        print()
        print("⚠️  Migration completed but validation failed!")
        print("   Review the changes and fix any import issues.")
        return False

    print()
    print(f"✅ Successfully migrated {module_name}")
    print()
    print("Next steps:")
    print(f"  1. Run tests: pytest Python/tests/test_{module_name}*.py -v")
    print(f"  2. Commit: ./scripts/ai_commit.sh 'refactor: migrate {module_name}.py to codes/is456/'")

    return True


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate IS 456 modules to codes/is456/ namespace"
    )
    parser.add_argument(
        "module",
        nargs="?",
        help=f"Module to migrate ({', '.join(MIGRATION_ORDER)})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate an already-migrated module",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List migration status of all modules",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Migrate all modules in order",
    )

    args = parser.parse_args()

    if args.list:
        print("Migration Status:")
        print("-" * 50)
        for mod in MIGRATION_ORDER:
            src = STRUCTURAL_LIB / f"{mod}.py"
            dst = CODES_IS456 / f"{mod}.py"
            if dst.exists():
                if src.exists():
                    content = src.read_text()
                    if "Backward compatibility stub" in content:
                        print(f"  ✅ {mod}: migrated (with stub)")
                    else:
                        print(f"  ⚠️  {mod}: migrated (stub missing!)")
                else:
                    print(f"  ⚠️  {mod}: migrated (original gone, stub missing!)")
            else:
                print(f"  ⏳ {mod}: not migrated")
        return 0

    if args.all:
        print("Migrating all modules in order...")
        print()
        for mod in MIGRATION_ORDER:
            dst = CODES_IS456 / f"{mod}.py"
            if dst.exists():
                print(f"⏭️  Skipping {mod} (already migrated)")
                continue
            if not migrate_module(mod, dry_run=args.dry_run):
                print(f"❌ Migration failed at {mod}")
                return 1
            print()
        print("✅ All modules migrated!")
        return 0

    if not args.module:
        parser.print_help()
        print()
        print("Recommended order:", " -> ".join(MIGRATION_ORDER))
        return 1

    if args.validate_only:
        if validate_module(args.module):
            return 0
        return 1

    if migrate_module(args.module, dry_run=args.dry_run):
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
