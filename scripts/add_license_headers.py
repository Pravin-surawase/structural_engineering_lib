#!/usr/bin/env python3
"""
Script to add standardized license headers to Python and VBA files.

Usage:
    python scripts/add_license_headers.py --check    # Dry run
    python scripts/add_license_headers.py --apply    # Apply changes
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple

# Python license header template (SPDX format)
PYTHON_HEADER = """# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""

# VBA license header template (aligned with VBA comment style)
VBA_HEADER = """
' ==============================================================================
' SPDX-License-Identifier: MIT
' Copyright (c) 2024-2026 Pravin Surawase
' ==============================================================================
"""


def has_spdx_header(content: str) -> bool:
    """Check if file already has SPDX license identifier."""
    # Check first 2000 chars (some VBA files have long comments before header)
    return "SPDX-License-Identifier" in content[:2000]


def add_python_header(filepath: Path) -> Tuple[bool, str]:
    """
    Add license header to Python file.

    Returns:
        (modified, message)
    """
    content = filepath.read_text(encoding="utf-8")

    if has_spdx_header(content):
        return False, "Already has SPDX header"

    lines = content.split("\n")

    # Find docstring start
    docstring_start = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            docstring_start = i
            break

    if docstring_start is None:
        # No docstring, add header at top
        new_content = PYTHON_HEADER + content
    else:
        # Insert header before docstring
        lines_before = lines[:docstring_start]
        lines_after = lines[docstring_start:]
        new_content = (
            "\n".join(lines_before)
            + ("\n" if lines_before else "")
            + PYTHON_HEADER
            + "\n".join(lines_after)
        )

    return True, new_content


def add_vba_header(filepath: Path) -> Tuple[bool, str]:
    """
    Add license header to VBA file.

    Returns:
        (modified, message)
    """
    content = filepath.read_text(encoding="utf-8", errors="ignore")

    if has_spdx_header(content):
        return False, "Already has SPDX header"

    lines = content.split("\n")

    # VBA files structure:
    # 1. Attribute VB_Name
    # 2. Option Explicit
    # 3. [Blank line]
    # 4. Existing module header (if any) - PRESERVE but remove old License line
    # 5. Insert SPDX header after Attribute/Option, before or in place of old header

    # Find insertion point (after Option Explicit)
    insert_index = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("Option "):
            insert_index = i + 1
            break
        elif stripped.startswith("Attribute "):
            insert_index = i + 1

    # Clean up old standalone License lines
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        # Remove standalone old-style license lines
        if stripped in ["' License:      MIT", "' License: MIT"]:
            continue
        cleaned_lines.append(line)

    # Insert SPDX header after Attribute/Option block
    new_lines = (
        cleaned_lines[:insert_index]
        + ["", ""]
        + [
            "' ==============================================================================",
            "' SPDX-License-Identifier: MIT",
            "' Copyright (c) 2024-2026 Pravin Surawase",
            "' ==============================================================================",
        ]
        + cleaned_lines[insert_index:]
    )

    new_content = "\n".join(new_lines)

    return True, new_content


def process_files(file_pattern: str, processor_func, apply: bool = False) -> List[str]:
    """Process files matching pattern with given processor function."""
    project_root = Path(__file__).parent.parent
    files = sorted(project_root.glob(file_pattern))

    results = []
    modified_count = 0

    for filepath in files:
        try:
            modified, result = processor_func(filepath)

            if modified:
                modified_count += 1
                if apply:
                    filepath.write_text(result, encoding="utf-8")
                    results.append(f"✅ {filepath.relative_to(project_root)}")
                else:
                    results.append(
                        f"📝 {filepath.relative_to(project_root)} (would be modified)"
                    )
            else:
                results.append(f"⏭️  {filepath.relative_to(project_root)} ({result})")
        except Exception as e:
            results.append(f"❌ {filepath.relative_to(project_root)}: {e}")

    return results, modified_count


def main():
    parser = argparse.ArgumentParser(description="Add license headers to source files")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--check", action="store_true", help="Dry run (show what would change)"
    )
    group.add_argument("--apply", action="store_true", help="Apply changes")

    args = parser.parse_args()
    apply_changes = args.apply

    print("=" * 80)
    print("License Header Standardization")
    print("=" * 80)
    print(f"Mode: {'APPLY CHANGES' if apply_changes else 'DRY RUN'}")
    print()

    # Process Python files
    print("Processing Python files...")
    print("-" * 80)
    py_results, py_modified = process_files(
        "Python/structural_lib/**/*.py", add_python_header, apply_changes
    )
    for result in py_results:
        print(result)

    print()
    print(f"Python: {py_modified} files modified")
    print()

    # Process VBA files
    print("Processing VBA files...")
    print("-" * 80)
    vba_results, vba_modified = process_files(
        "VBA/**/*.bas", add_vba_header, apply_changes
    )
    for result in vba_results:
        print(result)

    print()
    print(f"VBA: {vba_modified} files modified")
    print()

    # Summary
    print("=" * 80)
    print("Summary:")
    print(f"  Python files: {py_modified} modified")
    print(f"  VBA files: {vba_modified} modified")
    print(f"  Total: {py_modified + vba_modified} modified")
    print("=" * 80)

    if not apply_changes and (py_modified > 0 or vba_modified > 0):
        print()
        print("Run with --apply to make changes")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
