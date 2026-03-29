#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Generate docs/reference/error-codes.md from core/errors.py.

Scans all E_* DesignError constants and produces a markdown reference table
grouped by category (INPUT, FLEXURE, SHEAR, etc.).

Usage:
    .venv/bin/python scripts/generate_error_docs.py
    .venv/bin/python scripts/generate_error_docs.py --check  # verify up-to-date
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

# Add project root so structural_lib is importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "Python"))

from structural_lib.core.errors import DesignError  # noqa: E402


def collect_error_codes() -> list[DesignError]:
    """Import core.errors and collect all E_* DesignError constants."""
    import structural_lib.core.errors as errors_mod

    codes: list[DesignError] = []
    for name in sorted(dir(errors_mod)):
        if name.startswith("E_"):
            obj = getattr(errors_mod, name)
            if isinstance(obj, DesignError):
                codes.append(obj)
    return codes


def group_by_category(codes: list[DesignError]) -> dict[str, list[DesignError]]:
    """Group error codes by their category prefix (INPUT, FLEXURE, etc.)."""
    groups: dict[str, list[DesignError]] = {}
    for code in codes:
        # E_INPUT_001 -> INPUT, E_FLEXURE_001 -> FLEXURE
        parts = code.code.split("_")
        category = parts[1] if len(parts) >= 3 else "OTHER"
        groups.setdefault(category, []).append(code)
    return groups


def generate_markdown(codes: list[DesignError]) -> str:
    """Generate the full markdown document."""
    groups = group_by_category(codes)

    lines: list[str] = []
    lines.append("# Error Code Reference")
    lines.append("")
    lines.append("**Type:** Reference")
    lines.append("**Audience:** Developers, API Consumers")
    lines.append("**Status:** Auto-generated")
    lines.append(f"**Last Updated:** {date.today().isoformat()}")
    lines.append("")
    lines.append("> Auto-generated from `Python/structural_lib/core/errors.py`.")
    lines.append("> Run `scripts/generate_error_docs.py` to regenerate.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"**Total error codes:** {len(codes)}")
    lines.append("")

    # Table of contents
    lines.append("## Categories")
    lines.append("")
    for category in groups:
        count = len(groups[category])
        lines.append(f"- [{category}](#{category.lower()}) ({count} codes)")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Per-category tables
    for category, category_codes in groups.items():
        lines.append(f"## {category}")
        lines.append("")
        lines.append("| Code | Severity | Message | Field | Hint | IS 456 Clause |")
        lines.append("|------|----------|---------|-------|------|---------------|")
        for c in category_codes:
            sev = c.severity.value if c.severity else ""
            field = c.field or "—"
            hint = c.hint or "—"
            clause = c.clause or "—"
            msg = c.message.replace("|", "\\|")
            lines.append(
                f"| `{c.code}` | {sev} | {msg} | {field} | {hint} | {clause} |"
            )
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate error code reference docs")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if docs are up-to-date (exit 1 if stale)",
    )
    args = parser.parse_args()

    codes = collect_error_codes()
    content = generate_markdown(codes)

    output_path = PROJECT_ROOT / "docs" / "reference" / "error-codes.md"

    if args.check:
        if output_path.exists() and output_path.read_text() == content:
            print(
                f"✅ {output_path.relative_to(PROJECT_ROOT)} is up-to-date ({len(codes)} codes)"
            )
            return 0
        else:
            print(
                f"❌ {output_path.relative_to(PROJECT_ROOT)} is stale. Run: .venv/bin/python scripts/generate_error_docs.py"
            )
            return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content)
    print(
        f"✅ Generated {output_path.relative_to(PROJECT_ROOT)} with {len(codes)} error codes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
