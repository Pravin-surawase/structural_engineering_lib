#!/usr/bin/env python3
"""Add 'from __future__ import annotations' to files that need it."""

import os
import sys

# Files that need __future__ import
FILES = [
    "Python/structural_lib/costing.py",
    "Python/structural_lib/insights/cost_optimization.py",
    "Python/structural_lib/insights/smart_designer.py",
    "Python/structural_lib/api_results.py",
    "Python/structural_lib/excel_integration.py",
    "Python/structural_lib/optimization.py",
    "Python/structural_lib/dxf_export.py",
    "Python/structural_lib/api.py",
    "Python/structural_lib/excel_bridge.py",
    "Python/structural_lib/codes/is456/detailing.py",
    "Python/structural_lib/codes/is456/traceability.py",
    "Python/structural_lib/codes/is456/flexure.py",
    "Python/structural_lib/__main__.py",
    "Python/structural_lib/report.py",
    "Python/structural_lib/validation.py",
]


def add_future_import(fpath: str) -> bool:
    """Add future import to a file. Returns True if modified."""
    if not os.path.exists(fpath):
        print(f"SKIP (not found): {fpath}")
        return False

    with open(fpath, "r") as f:
        content = f.read()

    # Check if already has future import
    if "from __future__ import annotations" in content:
        print(f"SKIP (already has): {fpath}")
        return False

    # Find the right place to insert - after license and docstring
    lines = content.split("\n")
    insert_idx = 0

    # Skip SPDX and copyright
    for i, line in enumerate(lines):
        if line.startswith("#"):
            insert_idx = i + 1
        else:
            break

    # Skip docstring if present
    in_docstring = False
    for i, line in enumerate(lines[insert_idx:], start=insert_idx):
        stripped = line.strip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            if in_docstring:
                insert_idx = i + 1
                break
            elif stripped.count('"""') >= 2 or stripped.count("'''") >= 2:
                # Single line docstring
                insert_idx = i + 1
                break
            else:
                in_docstring = True
        elif in_docstring:
            if '"""' in stripped or "'''" in stripped:
                insert_idx = i + 1
                break

    # Insert the future import
    lines.insert(insert_idx, "")
    lines.insert(insert_idx + 1, "from __future__ import annotations")

    with open(fpath, "w") as f:
        f.write("\n".join(lines))
    print(f"ADDED: {fpath}")
    return True


def main() -> int:
    """Main entry point."""
    modified = 0
    for fpath in FILES:
        if add_future_import(fpath):
            modified += 1

    print(f"\nModified {modified} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
