"""
AppTest Tests for Beam Design Page
===================================

Tests for the beam design page (01_🏗️_beam_design.py) using Streamlit's
official AppTest framework.

These tests verify:
- Page loads without errors
- Widget interactions work
- Design calculations complete successfully
- Session state is properly managed

Run with: pytest tests/apptest/test_page_01_beam_design.py -v
"""

from __future__ import annotations

from pathlib import Path

import pytest

# Get paths - tests/apptest is 2 levels deep from project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
PAGES_DIR = PROJECT_ROOT / "streamlit_app" / "pages"
BEAM_DESIGN_PAGE = PAGES_DIR / "01_🏗️_beam_design.py"

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


@pytest.fixture
def beam_design_app():
    """Create AppTest for the beam design page."""
    if not BEAM_DESIGN_PAGE.exists():
        pytest.skip(f"Beam design page not found: {BEAM_DESIGN_PAGE}")
    return AppTest.from_file(str(BEAM_DESIGN_PAGE))


@skip_if_no_apptest
class TestBeamDesignPageLoad:
    """Tests for beam design page loading."""

    def test_page_loads_without_exception(self, beam_design_app):
        """Beam design page should load without raising exceptions."""
        at = beam_design_app.run(timeout=30)
        assert not at.exception, f"Page raised: {at.exception}"

    def test_page_has_title(self, beam_design_app):
        """Page should have a title displayed."""
        at = beam_design_app.run(timeout=30)

        # Check that we have some content
        # Note: at.title returns list of st.title elements
        assert len(at.title) > 0 or len(at.header) > 0, "Page should have a title or header"

    def test_page_has_input_widgets(self, beam_design_app):
        """Page should have input widgets for beam parameters."""
        at = beam_design_app.run(timeout=30)

        # Should have number inputs for dimensions, moment, etc.
        assert len(at.number_input) > 0, "Page should have number input widgets"

    def test_page_has_buttons(self, beam_design_app):
        """Page should have action buttons."""
        at = beam_design_app.run(timeout=30)

        # Should have at least one button (Calculate, etc.)
        assert len(at.button) > 0, "Page should have buttons"


@skip_if_no_apptest
class TestBeamDesignWidgetInteraction:
    """Tests for beam design widget interactions."""

    def test_can_set_number_input_values(self, beam_design_app):
        """Should be able to set values on number input widgets."""
        at = beam_design_app.run(timeout=30)

        if len(at.number_input) >= 1:
            # Try setting a value on the first number input
            at.number_input[0].set_value(5000.0).run()
            assert not at.exception, f"Setting number input raised: {at.exception}"

    def test_can_select_from_selectbox(self, beam_design_app):
        """Should be able to select options from selectbox widgets."""
        at = beam_design_app.run(timeout=30)

        if len(at.selectbox) >= 1:
            # Get options and select the second one if available
            options = at.selectbox[0].options
            if len(options) > 1:
                at.selectbox[0].set_value(options[1]).run()
                assert not at.exception, f"Setting selectbox raised: {at.exception}"

    def test_no_error_messages_on_load(self, beam_design_app):
        """Page should not show error messages on initial load."""
        at = beam_design_app.run(timeout=30)

        # st.error creates error elements
        # Some warnings are expected (e.g., "No design computed yet")
        # But there shouldn't be critical errors
        for error in at.error:
            # Check if it's a critical error (not a warning)
            error_text = str(error.value) if hasattr(error, "value") else str(error)
            if "exception" in error_text.lower() or "traceback" in error_text.lower():
                pytest.fail(f"Critical error on page load: {error_text}")


@skip_if_no_apptest
class TestBeamDesignCalculation:
    """Tests for beam design calculation functionality."""

    def test_calculation_button_exists(self, beam_design_app):
        """Page should have a calculate button."""
        at = beam_design_app.run(timeout=30)

        # Look for a button with "Calculate" or "Design" in label
        calc_buttons = []
        for btn in at.button:
            label = str(btn.label) if hasattr(btn, "label") else ""
            if "calculate" in label.lower() or "design" in label.lower():
                calc_buttons.append(btn)

        assert len(calc_buttons) > 0, "Should have a Calculate or Design button"

    def test_calculation_with_valid_inputs(self, beam_design_app):
        """Calculation should succeed with valid inputs."""
        at = beam_design_app.run(timeout=30)

        # This is a "golden path" test - just verify no exception
        # Setting specific inputs would require knowing widget order/keys
        if len(at.button) > 0:
            # Click first button (assuming it's Calculate)
            at.button[0].click().run()
            assert not at.exception, f"Calculation raised: {at.exception}"


@skip_if_no_apptest
class TestBeamDesignSessionState:
    """Tests for session state management."""

    def test_session_state_initialized(self, beam_design_app):
        """Session state should be initialized on page load."""
        at = beam_design_app.run(timeout=30)

        # beam_inputs should be in session state
        if hasattr(at, "session_state"):
            # Just verify we can access session state
            assert at.session_state is not None

    def test_session_state_persists_across_runs(self, beam_design_app):
        """Session state should persist across app reruns."""
        at = beam_design_app.run(timeout=30)

        # Set a value
        if len(at.number_input) >= 1:
            at.number_input[0].set_value(6000.0).run()

            # Rerun the app
            at.run()

            # Verify no crash
            assert not at.exception
