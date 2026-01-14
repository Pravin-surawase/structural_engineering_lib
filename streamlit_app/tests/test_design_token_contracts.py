"""
Design Token Contract Tests
============================

Purpose: Validate that ALL code usage of design tokens matches actual definitions.
Root Cause Prevention: Catches AttributeError before runtime by static code analysis.

This test file implements the core error prevention strategy:
"Tests must validate USAGE, not just DEFINITIONS."

History:
- 2026-01-08: Three AttributeError incidents (shadow_sm, body_md, duration_normal)
- Root cause: Tests checked design_system.py had correct attributes
- Root cause: Tests DIDN'T check components/*.py used correct attribute names
- Solution: This file validates the contract between definitions and usage

Test Strategy:
1. Find ALL Python files in streamlit_app/
2. Extract ALL design token references (COLORS.*, TYPOGRAPHY.*, etc.)
3. Verify EVERY reference matches an actual attribute
4. Fail fast with detailed error messages

Benefits:
- One test file catches ALL token mismatches
- Runs in <1 second (static analysis)
- Finds issues before runtime
- Works for future tokens too
- Zero maintenance overhead
"""

import ast
import glob
import re
from pathlib import Path
from typing import Dict, List, Tuple

import pytest

from utils.design_system import (
    ANIMATION,
    COLORS,
    ELEVATION,
    SPACING,
    TYPOGRAPHY,
)


def get_all_python_files() -> List[Path]:
    """
    Get all .py files in streamlit_app/ except tests/ and __pycache__.

    Returns:
        List of Path objects for all production Python files
    """
    root = Path(__file__).parent.parent
    files = []

    for pattern in ["*.py", "**/*.py"]:
        for filepath in root.glob(pattern):
            # Exclude test files and cache
            if "tests/" in str(filepath) or "__pycache__" in str(filepath):
                continue
            files.append(filepath)

    return files


def extract_design_token_usages(
    filepath: Path,
) -> Dict[str, List[Tuple[str, int, str]]]:
    """
    Extract all COLORS.*, TYPOGRAPHY.*, etc. usages from a file.

    Args:
        filepath: Path to Python file

    Returns:
        Dict mapping token class name to list of (attr_name, line_number, context) tuples

    Example:
        {
            "COLORS": [("primary_500", 42, "background=COLORS.primary_500")],
            "ANIMATION": [("duration_normal", 322, "transition=ANIMATION.duration_normal")]
        }
    """
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")
    except (IOError, UnicodeDecodeError):
        return {}

    tokens = {
        "COLORS": [],
        "TYPOGRAPHY": [],
        "SPACING": [],
        "ELEVATION": [],
        "ANIMATION": [],
    }

    # Extract usages with line numbers and context
    for line_num, line in enumerate(lines, start=1):
        for token_name in tokens.keys():
            # Match patterns like: COLORS.primary_500, ANIMATION.duration_normal
            # But exclude DARK_COLORS, LIGHT_COLORS (theme variants)
            pattern = rf"(?<!DARK_)(?<!LIGHT_){token_name}\.(\w+)"
            for match in re.finditer(pattern, line):
                attr_name = match.group(1)
                context = line.strip()[:80]  # First 80 chars for context
                tokens[token_name].append((attr_name, line_num, context))

    return tokens


class TestDesignTokenContracts:
    """
    Core test class for design token contract validation.

    Each test method validates one token class (COLORS, TYPOGRAPHY, etc.)
    across ALL Python files in the codebase.
    """

    def test_colors_usage_valid(self):
        """
        Validate ALL COLORS.* usages reference existing attributes.

        Prevents errors like:
        - COLORS.primary (should be COLORS.primary_500)
        - COLORS.text (should be COLORS.text_primary)
        """
        errors = []
        for py_file in get_all_python_files():
            usages = extract_design_token_usages(py_file)
            for attr_name, line_num, context in usages["COLORS"]:
                if not hasattr(COLORS, attr_name):
                    errors.append(
                        f"\n  File: {py_file.name}:{line_num}\n"
                        f"  Invalid: COLORS.{attr_name}\n"
                        f"  Context: {context}\n"
                    )

        assert not errors, (
            f"❌ Found {len(errors)} invalid COLORS usage(s):\n"
            + "".join(errors)
            + "\n💡 Fix: Use valid COLORS attributes from design_system.py"
        )

    def test_typography_usage_valid(self):
        """
        Validate ALL TYPOGRAPHY.* usages reference existing attributes.

        Prevents errors like:
        - TYPOGRAPHY.text_base (should be TYPOGRAPHY.body_md)
        - TYPOGRAPHY.heading (should be TYPOGRAPHY.display_lg)
        """
        errors = []
        for py_file in get_all_python_files():
            usages = extract_design_token_usages(py_file)
            for attr_name, line_num, context in usages["TYPOGRAPHY"]:
                if not hasattr(TYPOGRAPHY, attr_name):
                    errors.append(
                        f"\n  File: {py_file.name}:{line_num}\n"
                        f"  Invalid: TYPOGRAPHY.{attr_name}\n"
                        f"  Context: {context}\n"
                    )

        assert not errors, (
            f"❌ Found {len(errors)} invalid TYPOGRAPHY usage(s):\n"
            + "".join(errors)
            + "\n💡 Fix: Use valid TYPOGRAPHY attributes from design_system.py"
        )

    def test_spacing_usage_valid(self):
        """
        Validate ALL SPACING.* usages reference existing attributes.

        Prevents errors like:
        - SPACING.medium (should be SPACING.md)
        - SPACING.large (should be SPACING.lg)
        """
        errors = []
        for py_file in get_all_python_files():
            usages = extract_design_token_usages(py_file)
            for attr_name, line_num, context in usages["SPACING"]:
                if not hasattr(SPACING, attr_name):
                    errors.append(
                        f"\n  File: {py_file.name}:{line_num}\n"
                        f"  Invalid: SPACING.{attr_name}\n"
                        f"  Context: {context}\n"
                    )

        assert not errors, (
            f"❌ Found {len(errors)} invalid SPACING usage(s):\n"
            + "".join(errors)
            + "\n💡 Fix: Use valid SPACING attributes from design_system.py"
        )

    def test_elevation_usage_valid(self):
        """
        Validate ALL ELEVATION.* usages reference existing attributes.

        Prevents errors like:
        - ELEVATION.shadow_small (should be ELEVATION.shadow_sm)
        - ELEVATION.shadow_1 (should be ELEVATION.shadow_xs)
        """
        errors = []
        for py_file in get_all_python_files():
            usages = extract_design_token_usages(py_file)
            for attr_name, line_num, context in usages["ELEVATION"]:
                if not hasattr(ELEVATION, attr_name):
                    errors.append(
                        f"\n  File: {py_file.name}:{line_num}\n"
                        f"  Invalid: ELEVATION.{attr_name}\n"
                        f"  Context: {context}\n"
                    )

        assert not errors, (
            f"❌ Found {len(errors)} invalid ELEVATION usage(s):\n"
            + "".join(errors)
            + "\n💡 Fix: Use valid ELEVATION attributes from design_system.py"
        )

    def test_animation_usage_valid(self):
        """
        Validate ALL ANIMATION.* usages reference existing attributes.

        Prevents errors like:
        - ANIMATION.duration_normal (should be ANIMATION.normal)
        - ANIMATION.easing_ease_in (should be ANIMATION.cubic_bezier)

        This test would have caught the 2026-01-08 incident where
        visualizations.py used ANIMATION.duration_normal (doesn't exist)
        instead of ANIMATION.normal (exists).
        """
        errors = []
        for py_file in get_all_python_files():
            usages = extract_design_token_usages(py_file)
            for attr_name, line_num, context in usages["ANIMATION"]:
                if not hasattr(ANIMATION, attr_name):
                    errors.append(
                        f"\n  File: {py_file.name}:{line_num}\n"
                        f"  Invalid: ANIMATION.{attr_name}\n"
                        f"  Context: {context}\n"
                    )

        assert not errors, (
            f"❌ Found {len(errors)} invalid ANIMATION usage(s):\n"
            + "".join(errors)
            + "\n💡 Fix: Use valid ANIMATION attributes from design_system.py"
        )


class TestDesignTokenCoverage:
    """
    Validate that design tokens are actually being used.

    Prevents situations where tokens are defined but never used,
    or where code uses magic strings instead of design tokens.
    """

    def test_colors_are_used(self):
        """Verify COLORS tokens are actually used in codebase."""
        usage_count = 0
        for py_file in get_all_python_files():
            usages = extract_design_token_usages(py_file)
            usage_count += len(usages["COLORS"])

        # Should have at least some COLORS usage
        assert usage_count > 0, "COLORS tokens not used anywhere"

    def test_typography_are_used(self):
        """Verify TYPOGRAPHY tokens are actually used in codebase."""
        usage_count = 0
        for py_file in get_all_python_files():
            usages = extract_design_token_usages(py_file)
            usage_count += len(usages["TYPOGRAPHY"])

        # Should have at least some TYPOGRAPHY usage
        assert usage_count > 0, "TYPOGRAPHY tokens not used anywhere"

    def test_animation_are_used(self):
        """Verify ANIMATION tokens are actually used in codebase."""
        usage_count = 0
        for py_file in get_all_python_files():
            usages = extract_design_token_usages(py_file)
            usage_count += len(usages["ANIMATION"])

        # Should have at least some ANIMATION usage
        assert usage_count > 0, "ANIMATION tokens not used anywhere"


class TestDesignTokenConsistency:
    """
    Validate consistency of design token usage patterns.

    Ensures that similar contexts use similar tokens.
    """

    def test_no_hardcoded_colors(self):
        """
        Warn if hex colors are used instead of COLORS tokens.

        Not a hard failure, but suggests improvement opportunities.
        """
        warnings = []
        for py_file in get_all_python_files():
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split("\n")
            except (IOError, UnicodeDecodeError):
                continue

            # Look for hex colors like #FF5733
            for line_num, line in enumerate(lines, start=1):
                hex_colors = re.findall(r"#[0-9A-Fa-f]{6}", line)
                if hex_colors:
                    for color in hex_colors:
                        warnings.append(
                            f"  {py_file.name}:{line_num} uses hardcoded {color}"
                        )

        # Don't fail, just log warnings
        if warnings:
            print(f"\n⚠️ Found {len(warnings)} hardcoded color(s):")
            for warning in warnings[:10]:  # Show first 10
                print(warning)

    def test_design_token_imports(self):
        """
        Verify files that use design tokens actually import them.

        Catches cases where tokens are referenced but not imported.
        """
        errors = []
        for py_file in get_all_python_files():
            usages = extract_design_token_usages(py_file)

            # Check if file uses any design tokens
            has_usage = any(len(v) > 0 for v in usages.values())
            if not has_usage:
                continue

            # Skip files that define the tokens
            if py_file.name in [
                "design_system.py",
                "theme_manager.py",
                "plotly_theme.py",
                "global_styles.py",
                "styled_components.py",
                "design_system_demo.py",
            ]:
                continue

            # Verify imports
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()
            except (IOError, UnicodeDecodeError):
                continue

            # Check for design_system imports
            has_import = (
                "from utils.design_system import" in content
                or "import utils.design_system" in content
            )

            if not has_import:
                errors.append(f"  {py_file.name} uses tokens but doesn't import")

        assert (
            not errors
        ), f"❌ Found {len(errors)} file(s) using tokens without import:\n" + "\n".join(
            errors
        )


class TestRegressionPrevention:
    """
    Specific regression tests for past AttributeError incidents.

    These tests document historical issues and ensure they never happen again.
    """

    def test_2026_01_08_shadow_sm_regression(self):
        """
        Regression test for 2026-01-08 14:30 incident.

        Issue: layout.py used ELEVATION.shadow_sm which didn't exist
        Root cause: Used semantic alias before it was defined
        """
        # This should now pass because we added shadow_sm
        assert hasattr(
            ELEVATION, "shadow_sm"
        ), "REGRESSION: ELEVATION.shadow_sm removed"

    def test_2026_01_08_body_md_regression(self):
        """
        Regression test for 2026-01-08 20:25 incident.

        Issue: layout.py used TYPOGRAPHY.body_md which didn't exist
        Root cause: Used semantic alias before it was defined
        """
        # This should now pass because we added body_md
        assert hasattr(TYPOGRAPHY, "body_md"), "REGRESSION: TYPOGRAPHY.body_md removed"

    def test_2026_01_08_duration_normal_regression(self):
        """
        Regression test for 2026-01-08 20:45 incident.

        Issue: visualizations.py used ANIMATION.duration_normal which didn't exist
        Root cause: Used duration_* prefix but tokens don't have that prefix

        This test validates THE ACTUAL USAGE PATTERN, not just definitions.
        """
        # Find all ANIMATION.duration_* usages
        errors = []
        for py_file in get_all_python_files():
            usages = extract_design_token_usages(py_file)
            for attr_name, line_num, context in usages["ANIMATION"]:
                if attr_name.startswith("duration_"):
                    # duration_* pattern used - verify it exists
                    if not hasattr(ANIMATION, attr_name):
                        errors.append(
                            f"  {py_file.name}:{line_num} uses ANIMATION.{attr_name}"
                        )

        assert not errors, (
            "REGRESSION: Code uses ANIMATION.duration_* pattern:\n"
            + "\n".join(errors)
            + "\n💡 Either add duration_* aliases OR fix code to use 'normal', 'fast', etc."
        )


# Export test count for documentation
__all__ = [
    "TestDesignTokenContracts",
    "TestDesignTokenCoverage",
    "TestDesignTokenConsistency",
    "TestRegressionPrevention",
]

# Test counts:
# - TestDesignTokenContracts: 5 tests (one per token class)
# - TestDesignTokenCoverage: 3 tests (usage validation)
# - TestDesignTokenConsistency: 2 tests (patterns)
# - TestRegressionPrevention: 3 tests (historical issues)
# TOTAL: 13 critical contract tests
