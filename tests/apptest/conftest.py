"""
AppTest Fixtures for Streamlit Page Testing
============================================

Provides pytest fixtures for testing Streamlit pages using the official
st.testing.v1.AppTest framework.

NOTE: These tests are in tests/apptest (NOT streamlit_app/tests/apptest)
to avoid the Streamlit mock that's applied in streamlit_app/tests/conftest.py.

Reference: https://docs.streamlit.io/develop/api-reference/app-testing
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Add Python directory for structural_lib imports
PYTHON_DIR = PROJECT_ROOT / "Python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

# Check if AppTest is available (Streamlit >= 1.28.0)
def _check_apptest_available() -> bool:
    """Check if Streamlit AppTest is available."""
    try:
        from streamlit.testing.v1 import AppTest as _AppTest  # noqa: F401

        return True
    except ImportError:
        return False
    except Exception:
        return False


HAS_APPTEST = _check_apptest_available()

# Import AppTest only if available
if HAS_APPTEST:
    from streamlit.testing.v1 import AppTest
else:
    AppTest = None  # type: ignore

# Get pages directory
PAGES_DIR = PROJECT_ROOT / "streamlit_app" / "pages"
STREAMLIT_APP_DIR = PROJECT_ROOT / "streamlit_app"


def get_all_page_files() -> list[Path]:
    """Get all Python page files from the pages directory.

    Returns:
        List of Path objects for each page file.
    """
    if not PAGES_DIR.exists():
        return []
    return sorted(PAGES_DIR.glob("*.py"))


def get_page_names() -> list[str]:
    """Get page names (filenames) for parameterized tests.

    Returns:
        List of page filenames.
    """
    return [p.name for p in get_all_page_files()]


# Skip decorator for tests that require AppTest
skip_if_no_apptest = pytest.mark.skipif(
    not HAS_APPTEST,
    reason="streamlit.testing.v1.AppTest not available (requires Streamlit >= 1.28.0)",
)


@pytest.fixture(scope="session")
def apptest_available() -> bool:
    """Check if AppTest is available."""
    return HAS_APPTEST


@pytest.fixture
def pages_dir() -> Path:
    """Return the pages directory path."""
    return PAGES_DIR


@pytest.fixture
def all_page_files() -> list[Path]:
    """Return list of all page files."""
    return get_all_page_files()


@pytest.fixture
def create_app_test():
    """Factory fixture to create AppTest instances.

    Usage:
        def test_page(create_app_test):
            at = create_app_test("01_🏗️_beam_design.py")
            at.run()
            assert not at.exception
    """
    if not HAS_APPTEST:
        pytest.skip("AppTest not available")

    def _create(page_name: str) -> "AppTest":
        page_path = PAGES_DIR / page_name
        if not page_path.exists():
            raise FileNotFoundError(f"Page not found: {page_path}")

        # Change to streamlit_app directory for proper imports
        original_cwd = os.getcwd()
        os.chdir(STREAMLIT_APP_DIR)

        try:
            at = AppTest.from_file(str(page_path))
        finally:
            os.chdir(original_cwd)

        return at

    return _create


@pytest.fixture
def beam_design_app(create_app_test) -> "AppTest":
    """Pre-configured AppTest for beam design page."""
    return create_app_test("01_🏗️_beam_design.py")


@pytest.fixture
def analysis_app(create_app_test) -> "AppTest":
    """Pre-configured AppTest for analysis page."""
    return create_app_test("02_📊_analysis.py")


@pytest.fixture
def cost_app(create_app_test) -> "AppTest":
    """Pre-configured AppTest for cost optimizer page."""
    return create_app_test("03_💰_cost_optimizer.py")


@pytest.fixture
def bbs_app(create_app_test) -> "AppTest":
    """Pre-configured AppTest for BBS page."""
    return create_app_test("04_📋_bbs.py")


@pytest.fixture
def learning_app(create_app_test) -> "AppTest":
    """Pre-configured AppTest for learning page."""
    return create_app_test("05_📚_learning.py")


@pytest.fixture
def settings_app(create_app_test) -> "AppTest":
    """Pre-configured AppTest for settings page."""
    return create_app_test("06_⚙️_settings.py")


@pytest.fixture
def report_app(create_app_test) -> "AppTest":
    """Pre-configured AppTest for report generator page."""
    return create_app_test("07_📄_report_generator.py")
