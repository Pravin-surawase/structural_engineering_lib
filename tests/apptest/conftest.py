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
from typing import Any

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

# Page mapping (filename -> description)
PAGE_CONFIG = {
    "01_🏗️_beam_design.py": {"name": "Beam Design", "has_calculation": True},
    "02_💰_cost_optimizer.py": {"name": "Cost Optimizer", "has_calculation": True},
    "03_✅_compliance.py": {"name": "Compliance", "has_calculation": False},
    "04_📚_documentation.py": {"name": "Documentation", "has_calculation": False},
    "05_📋_bbs_generator.py": {"name": "BBS Generator", "has_calculation": True},
    "06_📐_dxf_export.py": {"name": "DXF Export", "has_calculation": False},
    "07_📄_report_generator.py": {"name": "Report Generator", "has_calculation": False},
    "08_📊_batch_design.py": {"name": "Batch Design", "has_calculation": True},
    "09_🔬_advanced_analysis.py": {
        "name": "Advanced Analysis",
        "has_calculation": True,
    },
    "10_📚_learning_center.py": {"name": "Learning Center", "has_calculation": False},
    "11_🎬_demo_showcase.py": {"name": "Demo Showcase", "has_calculation": True},
    "12_📖_clause_traceability.py": {
        "name": "Clause Traceability",
        "has_calculation": False,
    },
}


def get_all_page_files() -> list[Path]:
    """Get all Python page files from the pages directory.

    Returns:
        List of Path objects for each page file.
    """
    if not PAGES_DIR.exists():
        return []
    # Filter out backup files
    return sorted([p for p in PAGES_DIR.glob("*.py") if not p.name.endswith(".bak")])


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
def page_config() -> dict[str, dict[str, Any]]:
    """Return page configuration dict."""
    return PAGE_CONFIG


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

    def _create(page_name: str, default_timeout: int = 30) -> "AppTest":
        # Check main pages directory first
        page_path = PAGES_DIR / page_name
        if not page_path.exists():
            # Check _hidden directory for hidden pages (prefixed with _)
            hidden_path = PAGES_DIR / "_hidden" / page_name
            if hidden_path.exists():
                page_path = hidden_path
            else:
                raise FileNotFoundError(f"Page not found: {page_path} or {hidden_path}")

        # Change to streamlit_app directory for proper imports
        original_cwd = os.getcwd()
        os.chdir(STREAMLIT_APP_DIR)

        try:
            at = AppTest.from_file(str(page_path), default_timeout=default_timeout)
        finally:
            os.chdir(original_cwd)

        return at

    return _create


class AppTestHelper:
    """Helper class for AppTest assertions and utilities."""

    def __init__(self, app_test: "AppTest"):
        self.at = app_test

    def get_error_messages(self) -> list[str]:
        """Get all error messages displayed on the page."""
        errors = []
        for err in self.at.error:
            if hasattr(err, "value"):
                errors.append(str(err.value))
            else:
                errors.append(str(err))
        return errors

    def get_warning_messages(self) -> list[str]:
        """Get all warning messages displayed on the page."""
        warnings = []
        for warn in self.at.warning:
            if hasattr(warn, "value"):
                warnings.append(str(warn.value))
            else:
                warnings.append(str(warn))
        return warnings

    def has_critical_error(self) -> bool:
        """Check if page has critical errors (exceptions, tracebacks)."""
        if self.at.exception:
            return True
        for msg in self.get_error_messages():
            if any(kw in msg.lower() for kw in ["exception", "traceback", "error:"]):
                return True
        return False

    def get_button_by_label(self, label_contains: str) -> Any | None:
        """Find a button by partial label match."""
        for btn in self.at.button:
            btn_label = str(btn.label) if hasattr(btn, "label") else ""
            if label_contains.lower() in btn_label.lower():
                return btn
        return None

    def get_number_input_by_label(self, label_contains: str) -> Any | None:
        """Find a number input by partial label match."""
        for inp in self.at.number_input:
            inp_label = str(inp.label) if hasattr(inp, "label") else ""
            if label_contains.lower() in inp_label.lower():
                return inp
        return None

    def get_selectbox_by_label(self, label_contains: str) -> Any | None:
        """Find a selectbox by partial label match."""
        for sb in self.at.selectbox:
            sb_label = str(sb.label) if hasattr(sb, "label") else ""
            if label_contains.lower() in sb_label.lower():
                return sb
        return None


@pytest.fixture
def app_helper():
    """Factory fixture to create AppTestHelper instances."""

    def _create(app_test: "AppTest") -> AppTestHelper:
        return AppTestHelper(app_test)

    return _create


# Page-specific fixtures - updated to match actual page names
@pytest.fixture
def beam_design_app(create_app_test) -> "AppTest":
    """Pre-configured AppTest for beam design page."""
    return create_app_test("01_🏗️_beam_design.py")


@pytest.fixture
def cost_optimizer_app(create_app_test) -> "AppTest":
    """Pre-configured AppTest for cost optimizer page."""
    return create_app_test("02_💰_cost_optimizer.py")


@pytest.fixture
def compliance_app(create_app_test) -> "AppTest":
    """Pre-configured AppTest for compliance page."""
    return create_app_test("03_✅_compliance.py")


@pytest.fixture
def documentation_app(create_app_test) -> "AppTest":
    """Pre-configured AppTest for documentation page."""
    return create_app_test("04_📚_documentation.py")


@pytest.fixture
def bbs_app(create_app_test) -> "AppTest":
    """Pre-configured AppTest for BBS generator page."""
    return create_app_test("05_📋_bbs_generator.py")


@pytest.fixture
def dxf_app(create_app_test) -> "AppTest":
    """Pre-configured AppTest for DXF export page."""
    return create_app_test("06_📐_dxf_export.py")


@pytest.fixture
def report_app(create_app_test) -> "AppTest":
    """Pre-configured AppTest for report generator page (now hidden with _ prefix)."""
    return create_app_test("_07_📄_report_generator.py")


@pytest.fixture
def batch_design_app(create_app_test) -> "AppTest":
    """Pre-configured AppTest for batch design page."""
    return create_app_test("08_📊_batch_design.py")


@pytest.fixture
def advanced_analysis_app(create_app_test) -> "AppTest":
    """Pre-configured AppTest for advanced analysis page."""
    return create_app_test("09_🔬_advanced_analysis.py")


@pytest.fixture
def learning_app(create_app_test) -> "AppTest":
    """Pre-configured AppTest for learning center page."""
    return create_app_test("10_📚_learning_center.py")


@pytest.fixture
def demo_app(create_app_test) -> "AppTest":
    """Pre-configured AppTest for demo showcase page."""
    return create_app_test("11_🎬_demo_showcase.py")


@pytest.fixture
def clause_traceability_app(create_app_test) -> "AppTest":
    """Pre-configured AppTest for clause traceability page."""
    return create_app_test("12_📖_clause_traceability.py")
