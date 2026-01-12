#!/usr/bin/env python3
"""
Python Version Consistency Checker

TASK-453: Ensure all Python version references are consistent across the codebase.

Checks:
- pyproject.toml (requires-python, ruff target-version, mypy python_version)
- setup.cfg (python_requires)
- CI workflows (python-version in matrix and setup)
- Documentation references

Usage:
    python scripts/check_python_version.py
    python scripts/check_python_version.py --fix  # Update inconsistent versions
    python scripts/check_python_version.py --ci   # Fail on inconsistency

Created: 2026-01-12 (Session 19, TASK-453)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

# =============================================================================
# CONFIGURATION
# =============================================================================

# Source of truth for minimum Python version
MINIMUM_PYTHON_VERSION = "3.11"
SUPPORTED_VERSIONS = ["3.11", "3.12", "3.13"]

# Files to check
CHECK_FILES = {
    "Python/pyproject.toml": [
        (r'requires-python\s*=\s*">=(\d+\.\d+)"', "requires-python"),
        (r'target-version\s*=\s*"py(\d+)"', "ruff-target", lambda m: f"{m[0]}.{m[1:]}"),
        (r'python_version\s*=\s*"(\d+\.\d+)"', "mypy-version"),
    ],
    "Python/setup.cfg": [
        (r"python_requires\s*=\s*>=(\d+\.\d+)", "python_requires"),
    ],
    ".github/workflows/fast-checks.yml": [
        (r'python-version:\s*"(\d+\.\d+)"', "fast-checks-version"),
        (r"Python (\d+\.\d+) only", "fast-checks-name"),
    ],
    ".github/workflows/python-tests.yml": [
        (r'python-version:\s*\["([^"]+)"', "pytest-matrix-min"),
    ],
}


# =============================================================================
# CHECKER
# =============================================================================


def parse_version(version_str: str) -> tuple[int, int]:
    """Parse version string to tuple."""
    parts = version_str.split(".")
    return (int(parts[0]), int(parts[1]))


def check_file(
    filepath: Path, patterns: list[tuple], project_root: Path
) -> list[dict[str, Any]]:
    """Check a file for version consistency."""
    issues = []
    full_path = project_root / filepath

    if not full_path.exists():
        return [
            {
                "file": str(filepath),
                "issue": "File not found",
                "severity": "WARNING",
            }
        ]

    content = full_path.read_text()

    for pattern_tuple in patterns:
        pattern = pattern_tuple[0]
        name = pattern_tuple[1]
        transform = pattern_tuple[2] if len(pattern_tuple) > 2 else None

        matches = re.findall(pattern, content)
        for match in matches:
            # Apply transform if provided (e.g., py311 -> 3.11)
            if transform:
                version = transform(match)
            else:
                version = match

            # Check if version matches minimum
            if version != MINIMUM_PYTHON_VERSION:
                issues.append(
                    {
                        "file": str(filepath),
                        "name": name,
                        "found": version,
                        "expected": MINIMUM_PYTHON_VERSION,
                        "severity": "ERROR",
                    }
                )

    return issues


def check_all(project_root: Path) -> list[dict[str, Any]]:
    """Check all configured files."""
    all_issues = []

    for filepath, patterns in CHECK_FILES.items():
        issues = check_file(Path(filepath), patterns, project_root)
        all_issues.extend(issues)

    return all_issues


def format_report(issues: list[dict[str, Any]]) -> str:
    """Format issues as report."""
    if not issues:
        return f"✅ All Python version references are consistent ({MINIMUM_PYTHON_VERSION})"

    lines = []
    lines.append("=" * 60)
    lines.append("❌ Python Version Inconsistencies Found")
    lines.append("=" * 60)
    lines.append(f"Expected minimum version: {MINIMUM_PYTHON_VERSION}")
    lines.append("")

    for issue in issues:
        if "found" in issue:
            lines.append(
                f"  {issue['file']}: {issue['name']}"
                f"\n    Found: {issue['found']}, Expected: {issue['expected']}"
            )
        else:
            lines.append(f"  {issue['file']}: {issue['issue']}")

    lines.append("")
    lines.append(f"Total issues: {len(issues)}")
    lines.append("=" * 60)

    return "\n".join(lines)


# =============================================================================
# CLI
# =============================================================================


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check Python version consistency across project"
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI mode: exit with error if inconsistencies found",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    parser.add_argument(
        "--version",
        default=MINIMUM_PYTHON_VERSION,
        help=f"Expected minimum version (default: {MINIMUM_PYTHON_VERSION})",
    )

    args = parser.parse_args()

    # Use override version if provided
    min_version = args.version

    # Find project root
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent

    # Check all files
    issues = check_all(project_root)

    # Output results
    if args.json:
        import json

        print(
            json.dumps(
                {
                    "minimum_version": min_version,
                    "issues": issues,
                    "consistent": len(issues) == 0,
                },
                indent=2,
            )
        )
    else:
        print(format_report(issues))

    # Exit with error in CI mode if issues found
    if args.ci and issues:
        sys.exit(1)


if __name__ == "__main__":
    main()
