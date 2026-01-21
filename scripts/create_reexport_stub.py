#!/usr/bin/env python3
"""Create a re-export stub for backward compatibility.

Creates a stub file that re-exports everything from the migrated location,
ensuring backward compatibility with existing imports.

Usage:
    python scripts/create_reexport_stub.py flexure
    python scripts/create_reexport_stub.py flexure --dry-run
    python scripts/create_reexport_stub.py --all
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Get project root
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
STRUCTURAL_LIB = PROJECT_ROOT / "Python" / "structural_lib"

# Modules that will be migrated
MIGRATABLE_MODULES = [
    "flexure",
    "shear",
    "detailing",
    "tables",
    "serviceability",
    "compliance",
    "ductile",
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


def create_stub(module_name: str, dry_run: bool = False) -> bool:
    """Create a re-export stub for a module.

    Args:
        module_name: Name of the module (e.g., 'flexure')
        dry_run: If True, only show what would be done

    Returns:
        True if successful, False otherwise
    """
    if module_name not in MIGRATABLE_MODULES:
        print(f"❌ Unknown module: {module_name}")
        print(f"   Available: {', '.join(MIGRATABLE_MODULES)}")
        return False

    stub_path = STRUCTURAL_LIB / f"{module_name}.py"
    migrated_path = STRUCTURAL_LIB / "codes" / "is456" / f"{module_name}.py"

    # Check if migration target exists
    if not migrated_path.exists():
        print(f"❌ Migration target not found: {migrated_path}")
        print("   Run migrate_module.py first to move the module")
        return False

    # Check if stub already exists and is a stub
    if stub_path.exists():
        content = stub_path.read_text()
        if "Backward compatibility stub" in content:
            print(f"⚠️  Stub already exists: {stub_path}")
            return True
        # Original module exists, need to backup first
        if not dry_run:
            print(f"⚠️  Original module exists at {stub_path}")
            print("   This should have been moved by migrate_module.py")
            return False

    # Generate stub content
    stub_content = STUB_TEMPLATE.format(module_name=module_name)

    if dry_run:
        print(f"Would create stub: {stub_path}")
        print()
        print("Content:")
        print("-" * 40)
        print(stub_content)
        print("-" * 40)
        return True

    # Write stub
    stub_path.write_text(stub_content)
    print(f"✅ Created stub: {stub_path}")

    # Verify import works
    import subprocess

    python = PROJECT_ROOT / ".venv" / "bin" / "python"
    test_code = f"from structural_lib import {module_name}; print('OK')"
    result = subprocess.run(
        [str(python), "-c", test_code],
        cwd=PROJECT_ROOT / "Python",
        capture_output=True,
        text=True,
    )

    if result.returncode == 0 and "OK" in result.stdout:
        print(f"✅ Import verified: from structural_lib import {module_name}")
        return True
    else:
        print(f"❌ Import verification failed: {result.stderr[:200]}")
        return False


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Create re-export stubs for backward compatibility"
    )
    parser.add_argument(
        "module",
        nargs="?",
        help=f"Module name ({', '.join(MIGRATABLE_MODULES)})",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Create stubs for all migratable modules",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all migratable modules",
    )

    args = parser.parse_args()

    if args.list:
        print("Migratable modules:")
        for mod in MIGRATABLE_MODULES:
            stub = STRUCTURAL_LIB / f"{mod}.py"
            migrated = STRUCTURAL_LIB / "codes" / "is456" / f"{mod}.py"
            status = []
            if migrated.exists():
                status.append("migrated")
            if stub.exists():
                content = stub.read_text()
                if "Backward compatibility stub" in content:
                    status.append("stub")
                else:
                    status.append("original")
            print(f"  {mod}: {', '.join(status) or 'not started'}")
        return 0

    if args.all:
        success = True
        for mod in MIGRATABLE_MODULES:
            migrated = STRUCTURAL_LIB / "codes" / "is456" / f"{mod}.py"
            if not migrated.exists():
                print(f"⏭️  Skipping {mod} (not migrated yet)")
                continue
            if not create_stub(mod, dry_run=args.dry_run):
                success = False
        return 0 if success else 1

    if not args.module:
        parser.print_help()
        return 1

    if create_stub(args.module, dry_run=args.dry_run):
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
