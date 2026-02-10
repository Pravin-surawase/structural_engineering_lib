#!/usr/bin/env python3
"""Fix relative imports in services/ that reference non-services modules.

After moving files from structural_lib/ root to structural_lib/services/,
relative imports like `from .models import X` now resolve to
`services.models` instead of the root `structural_lib.models`.

This script converts those broken relative imports to absolute imports.
"""
from __future__ import annotations

import re
from pathlib import Path

LIB = Path("Python/structural_lib")
SERVICES = LIB / "services"

# Modules that actually live in services/
SERVICES_MODULES = {
    "api", "api_results", "beam_pipeline", "adapters", "batch", "imports",
    "etabs_import", "rebar", "rebar_optimizer", "optimization",
    "multi_objective_optimizer", "audit", "intelligence", "costing",
    "serialization", "dashboard", "testing_strategies",
}

# Modules that moved to core/
CORE_MODULES = {
    "constants", "types", "data_types", "models", "errors", "error_messages",
    "validation", "inputs", "result_base", "utilities",
}

# Subpackages that stay in root
ROOT_SUBPACKAGES = {"codes", "insights", "visualization"}

# Root modules (not moved)
ROOT_MODULES = {
    "calculation_report", "torsion", "detailing", "materials",
    "serviceability", "slenderness", "flexure", "shear", "ductile",
    "tables", "compliance",
}


def fix_file(filepath: Path) -> int:
    """Fix broken relative imports in a single services/ file."""
    text = filepath.read_text()
    original = text
    lines = text.split("\n")
    fixed_lines = []
    fixes = 0

    for line in lines:
        # Match: from .module import ... or from .module.sub import ...
        m = re.match(r"^(\s*)(from \.)(\w+)(.*)", line)
        if m:
            indent, _prefix, module, rest = m.groups()

            if module in SERVICES_MODULES:
                # Valid relative import within services/
                fixed_lines.append(line)
                continue
            elif module in CORE_MODULES:
                # Moved to core/ - make absolute
                new_line = f"{indent}from structural_lib.core.{module}{rest}"
                fixed_lines.append(new_line)
                fixes += 1
                print(f"  {filepath.name}:{len(fixed_lines)}: .{module} -> core.{module}")
                continue
            elif module in ROOT_SUBPACKAGES:
                # Subpackage at root level
                new_line = f"{indent}from structural_lib.{module}{rest}"
                fixed_lines.append(new_line)
                fixes += 1
                print(f"  {filepath.name}:{len(fixed_lines)}: .{module} -> structural_lib.{module}")
                continue
            elif module in ROOT_MODULES:
                # Root module (shim or real)
                new_line = f"{indent}from structural_lib.{module}{rest}"
                fixed_lines.append(new_line)
                fixes += 1
                print(f"  {filepath.name}:{len(fixed_lines)}: .{module} -> structural_lib.{module}")
                continue

        fixed_lines.append(line)

    new_text = "\n".join(fixed_lines)
    if new_text != original:
        filepath.write_text(new_text)
    return fixes


def main() -> None:
    """Fix all services/ files."""
    total = 0
    for py_file in sorted(SERVICES.glob("*.py")):
        if py_file.name == "__init__.py":
            continue
        fixes = fix_file(py_file)
        total += fixes

    print(f"\nTotal fixes: {total}")


if __name__ == "__main__":
    main()
