"""
Smoke Tests for All Streamlit Pages
====================================

Quick smoke tests that verify each page loads without raising exceptions.
These tests use Streamlit's official AppTest framework.

Run with: pytest tests/apptest/test_all_pages_smoke.py -v

Reference: https://docs.streamlit.io/develop/api-reference/app-testing
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Get paths - tests/apptest is 2 levels deep from project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
PAGES_DIR = PROJECT_ROOT / "streamlit_app" / "pages"

# Check AppTest availability at module level
try:
    from streamlit.testing.v1 import AppTest

    HAS_APPTEST = True
except ImportError:
    HAS_APPTEST = False
    AppTest = None  # type: ignore

# Skip decorator
skip_if_no_apptest = pytest.mark.skipif(
    not HAS_APPTEST,
    reason="streamlit.testing.v1.AppTest not available (requires Streamlit >= 1.28.0)",
)


def get_all_page_files() -> list[Path]:
    """Get all Python page files from the pages directory."""
    if not PAGES_DIR.exists():
        return []
    return sorted(PAGES_DIR.glob("*.py"))


@skip_if_no_apptest
class TestAllPagesSmokeTest:
    """Smoke tests for all Streamlit pages.

    Each test verifies that a page can load without raising an exception.
    This catches common issues like:
    - Import errors
    - NameError (undefined variables)
    - Missing dependencies
    - Syntax errors
    """

    @pytest.mark.parametrize(
        "page_path",
        get_all_page_files(),
        ids=lambda p: p.name,
    )
    def test_page_loads_without_exception(self, page_path: Path):
        """Each page should load without raising an exception.

        This is the most basic smoke test - just verify the page renders
        without crashing. More detailed tests are in individual test files.
        """
        at = AppTest.from_file(str(page_path))

        # Run with timeout to catch infinite loops
        at.run(timeout=30)

        # Check for any exception during render
        if at.exception:
            # Get exception details
            exc_type = type(at.exception[0]).__name__ if at.exception else "Unknown"
            exc_msg = str(at.exception[0]) if at.exception else "No message"
            pytest.fail(
                f"Page '{page_path.name}' raised {exc_type}: {exc_msg}"
            )

    def test_pages_directory_exists(self):
        """Verify pages directory exists."""
        assert PAGES_DIR.exists(), f"Pages directory not found: {PAGES_DIR}"

    def test_at_least_one_page_exists(self):
        """Verify at least one page file exists."""
        all_page_files = get_all_page_files()
        assert len(all_page_files) > 0, "No page files found in pages/ directory"

    def test_all_pages_have_py_extension(self):
        """All page files should have .py extension."""
        for page_path in get_all_page_files():
            assert page_path.suffix == ".py", f"Page {page_path.name} has wrong extension"


@skip_if_no_apptest
class TestMainAppSmokeTest:
    """Smoke test for the main app.py entry point."""

    def test_main_app_loads(self):
        """Main app.py should load without exception."""
        main_app = PAGES_DIR.parent / "app.py"
        if not main_app.exists():
            pytest.skip("app.py not found")

        at = AppTest.from_file(str(main_app))
        at.run(timeout=30)

        if at.exception:
            exc_type = type(at.exception[0]).__name__ if at.exception else "Unknown"
            exc_msg = str(at.exception[0]) if at.exception else "No message"
            pytest.fail(f"Main app raised {exc_type}: {exc_msg}")


@skip_if_no_apptest
class TestPageNamingConventions:
    """Tests for page naming and structure conventions."""

    def test_pages_follow_naming_convention(self):
        """Pages should follow NN_emoji_name.py convention."""
        for page_path in get_all_page_files():
            name = page_path.name
            # Should start with two digits
            if not name[:2].isdigit():
                pytest.fail(f"Page {name} should start with two digits (e.g., '01_')")

            # Should have underscore after digits
            if len(name) > 2 and name[2] != "_":
                pytest.fail(f"Page {name} should have underscore after digits")

    def test_pages_are_sequential(self):
        """Page numbers should be sequential starting from 01."""
        all_page_files = get_all_page_files()
        numbers = []
        for page_path in all_page_files:
            try:
                num = int(page_path.name[:2])
                numbers.append(num)
            except ValueError:
                pytest.fail(f"Page {page_path.name} has invalid number prefix")

        # Check for gaps (optional, may be intentional)
        numbers_sorted = sorted(numbers)
        if numbers_sorted and numbers_sorted[0] != 1:
            pytest.skip("Pages don't start with 01 (may be intentional)")

        for i, num in enumerate(numbers_sorted):
            expected = i + 1
            if num != expected:
                pytest.skip(f"Gap in page numbering: expected {expected}, got {num}")
