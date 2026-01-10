#!/usr/bin/env python3
"""Update codes/is456/__init__.py to export all migrated modules.

This script automatically:
1. Detects all migrated modules in codes/is456/
2. Updates __init__.py imports
3. Updates __all__ exports
4. Preserves IS456Code class

Usage:
    python scripts/update_is456_init.py           # Preview changes
    python scripts/update_is456_init.py --apply   # Apply changes
    python scripts/update_is456_init.py --verify  # Verify current state

Author: Session 6 (2026-01-11)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Project paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
PYTHON_DIR = PROJECT_ROOT / "Python"
STRUCTURAL_LIB = PYTHON_DIR / "structural_lib"
CODES_IS456 = STRUCTURAL_LIB / "codes" / "is456"
INIT_FILE = CODES_IS456 / "__init__.py"

# Module order (dependencies first)
MODULE_ORDER = [
    "tables",
    "shear",
    "flexure",
    "detailing",
    "serviceability",
    "compliance",
    "ductile",
]


def get_migrated_modules() -> list[str]:
    """Detect which modules have been migrated to codes/is456/."""
    migrated = []
    for module_name in MODULE_ORDER:
        module_path = CODES_IS456 / f"{module_name}.py"
        if module_path.exists():
            # Check it's not just a stub (has actual code)
            content = module_path.read_text()
            # A real migrated module will have function definitions
            if "def " in content and len(content) > 500:
                migrated.append(module_name)
    return migrated


def generate_init_content(migrated_modules: list[str]) -> str:
    """Generate the new __init__.py content."""

    # Build module import lines
    module_imports = "\n".join([
        f"from structural_lib.codes.is456 import {m}"
        for m in migrated_modules
    ])

    # Build __all__ list
    all_items = ['    "IS456Code",']
    for m in migrated_modules:
        all_items.append(f'    "{m}",')
    all_list = "\n".join(all_items)

    content = f'''"""IS 456:2000 - Indian Standard for Plain and Reinforced Concrete.

This module provides IS 456-specific implementations of:
- Flexure design (Cl. 38.1)
- Shear design (Cl. 40)
- Detailing rules (Cl. 26)
- Serviceability checks (Cl. 42, 43)
- Compliance verification

All existing functionality from the main library is preserved.
This package acts as a namespace for IS 456-specific code.

Migration Status (Session 5-6):
{chr(10).join([f"- {m}.py: ✅ Migrated" for m in migrated_modules])}
"""

from __future__ import annotations

# Import migrated modules
{module_imports}

# Import base classes for IS456Code
from structural_lib.core.base import DesignCode
from structural_lib.core.registry import register_code


@register_code("IS456")
class IS456Code(DesignCode):
    """IS 456:2000 design code implementation.

    This class provides code-specific constants and methods.
    The actual design functions are in the submodules:
    - tables: Table 19/23 lookups
    - shear: Shear design per Cl. 40
    - flexure: Flexure design per Cl. 38.1
    - detailing: Reinforcement detailing per Cl. 26
    - serviceability: Deflection/crack width per Cl. 42/43
    - compliance: Compliance checking orchestration
    - ductile: Ductile detailing per IS 13920
    """

    @property
    def code_id(self) -> str:
        return "IS456"

    @property
    def code_name(self) -> str:
        return "Indian Standard IS 456:2000"

    @property
    def code_version(self) -> str:
        return "2000"

    # Material partial safety factors (Cl. 36.4.2)
    GAMMA_C = 1.5  # Concrete
    GAMMA_S = 1.15  # Steel

    # Stress block parameters (Cl. 38.1)
    STRESS_BLOCK_DEPTH = 0.42  # xu/d for balanced section
    STRESS_BLOCK_FACTOR = 0.36  # For rectangular stress block

    def get_design_strength_concrete(self, fck: float) -> float:
        """Design compressive strength of concrete (0.67*fck/γc)."""
        return 0.67 * fck / self.GAMMA_C

    def get_design_strength_steel(self, fy: float) -> float:
        """Design yield strength of steel (fy/γs)."""
        return fy / self.GAMMA_S

    # Convenience methods that delegate to submodules
    # These provide a unified interface through IS456Code instance

    def get_tau_c(self, fck: float, pt: float) -> float:
        """Get design shear strength τc from Table 19."""
        return tables.get_tau_c(fck, pt)

    def get_tau_c_max(self, fck: float) -> float:
        """Get maximum shear stress τc,max from Table 20."""
        return tables.get_tau_c_max(fck)


# Convenience exports
__all__ = [
{all_list}
]
'''
    return content


def verify_init() -> bool:
    """Verify the current __init__.py is correct."""
    if not INIT_FILE.exists():
        print("❌ __init__.py does not exist")
        return False

    migrated = get_migrated_modules()
    content = INIT_FILE.read_text()

    issues = []
    for module in migrated:
        # Check import
        if f"from structural_lib.codes.is456 import {module}" not in content:
            issues.append(f"Missing import for '{module}'")
        # Check __all__
        if f'"{module}"' not in content:
            issues.append(f"Missing __all__ entry for '{module}'")

    if issues:
        print(f"❌ Found {len(issues)} issue(s):")
        for issue in issues:
            print(f"   - {issue}")
        return False

    print(f"✅ __init__.py correctly exports {len(migrated)} modules:")
    for m in migrated:
        print(f"   - {m}")
    return True


def preview_changes():
    """Preview what changes would be made."""
    migrated = get_migrated_modules()
    print(f"📦 Detected {len(migrated)} migrated modules:")
    for m in migrated:
        print(f"   - {m}")

    print("\n📝 Generated __init__.py content:")
    print("-" * 60)
    new_content = generate_init_content(migrated)
    print(new_content)
    print("-" * 60)

    print("\n💡 To apply changes, run:")
    print("   python scripts/update_is456_init.py --apply")


def apply_changes():
    """Apply the changes to __init__.py."""
    migrated = get_migrated_modules()
    print(f"📦 Detected {len(migrated)} migrated modules")

    new_content = generate_init_content(migrated)

    # Backup existing
    if INIT_FILE.exists():
        backup_path = INIT_FILE.with_suffix(".py.bak")
        backup_path.write_text(INIT_FILE.read_text())
        print(f"📋 Backed up to {backup_path.name}")

    # Write new content
    INIT_FILE.write_text(new_content)
    print(f"✅ Updated {INIT_FILE}")

    # Verify
    print("\n🔍 Verifying...")
    return verify_init()


def main():
    parser = argparse.ArgumentParser(
        description="Update codes/is456/__init__.py exports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes to __init__.py",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify current __init__.py is correct",
    )

    args = parser.parse_args()

    if args.verify:
        success = verify_init()
    elif args.apply:
        success = apply_changes()
    else:
        preview_changes()
        success = True

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
