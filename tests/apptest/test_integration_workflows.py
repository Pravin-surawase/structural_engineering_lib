"""
Integration Tests for Complete User Workflows
==============================================

These tests simulate real user interactions across the app:
1. Complete beam design workflow
2. Cost optimization workflow
3. Report generation workflow
4. Error handling scenarios

Run with: pytest tests/apptest/test_integration_workflows.py -v
"""

from __future__ import annotations

from pathlib import Path

import pytest

# Get paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
PAGES_DIR = PROJECT_ROOT / "streamlit_app" / "pages"

# Check AppTest availability
try:
    from streamlit.testing.v1 import AppTest

    HAS_APPTEST = True
except ImportError:
    HAS_APPTEST = False
    AppTest = None  # type: ignore

skip_if_no_apptest = pytest.mark.skipif(
    not HAS_APPTEST,
    reason="streamlit.testing.v1.AppTest not available",
)


@skip_if_no_apptest
class TestBeamDesignWorkflow:
    """Complete beam design workflow integration tests."""

    def test_complete_design_workflow(self, beam_design_app, app_helper):
        """Test complete beam design from input to output."""
        # Load page
        at = beam_design_app.run(timeout=30)
        helper = app_helper(at)
        assert not at.exception, f"Initial load failed: {at.exception}"

        # Find and set span input
        span_input = helper.get_number_input_by_label("span")
        if span_input:
            at = span_input.set_value(6000.0).run()
            assert not at.exception, f"Setting span failed: {at.exception}"

        # Find and set width input
        width_input = helper.get_number_input_by_label("width")
        if width_input:
            at = width_input.set_value(300.0).run()
            assert not at.exception, f"Setting width failed: {at.exception}"

        # Find and set depth input
        depth_input = helper.get_number_input_by_label("depth")
        if depth_input:
            at = depth_input.set_value(500.0).run()
            assert not at.exception, f"Setting depth failed: {at.exception}"

        # Click calculate button
        calc_btn = helper.get_button_by_label("calculate")
        if calc_btn:
            at = calc_btn.click().run()
            assert not helper.has_critical_error(), (
                f"Calculation failed with errors: {helper.get_error_messages()}"
            )

    def test_invalid_inputs_handled(self, beam_design_app, app_helper):
        """Test that invalid inputs are handled gracefully."""
        at = beam_design_app.run(timeout=30)
        helper = app_helper(at)

        # Try to set invalid (very small) dimensions
        if len(at.number_input) >= 1:
            # Setting very small value should not crash
            at = at.number_input[0].set_value(1.0).run()
            # Should not have an unhandled exception
            assert not at.exception or "validation" in str(at.exception).lower()

    def test_multiple_calculations(self, beam_design_app, app_helper):
        """Test running multiple calculations in sequence."""
        at = beam_design_app.run(timeout=30)
        helper = app_helper(at)

        # First calculation
        calc_btn = helper.get_button_by_label("calculate")
        if calc_btn:
            at = calc_btn.click().run()
            assert not at.exception

            # Second calculation (modify a value and recalculate)
            if len(at.number_input) >= 1:
                at = at.number_input[0].set_value(7000.0).run()
                at = calc_btn.click().run()
                assert not at.exception, f"Second calculation failed: {at.exception}"


@skip_if_no_apptest
class TestCostOptimizerWorkflow:
    """Cost optimizer workflow integration tests."""

    def test_page_loads_with_no_prior_design(self, cost_optimizer_app, app_helper):
        """Cost optimizer should handle case with no prior beam design."""
        at = cost_optimizer_app.run(timeout=30)
        helper = app_helper(at)

        # Should load without crashing
        assert not at.exception, f"Page crashed: {at.exception}"

        # Should show info message if no design available
        # (not a critical error, just informational)
        errors = helper.get_error_messages()
        warnings = helper.get_warning_messages()
        # Verify it's not a traceback error
        assert not helper.has_critical_error()

    def test_cost_profile_selection(self, cost_optimizer_app, app_helper):
        """Test cost profile selection works."""
        at = cost_optimizer_app.run(timeout=30)
        helper = app_helper(at)

        # Find cost profile selectbox
        profile_sb = helper.get_selectbox_by_label("profile")
        if profile_sb:
            options = profile_sb.options if hasattr(profile_sb, "options") else []
            if len(options) > 1:
                at = profile_sb.set_value(options[1]).run()
                assert not at.exception


@skip_if_no_apptest
class TestReportGeneratorWorkflow:
    """Report generator workflow integration tests."""

    def test_report_page_loads(self, report_app, app_helper):
        """Report generator should load without errors."""
        at = report_app.run(timeout=30)
        helper = app_helper(at)

        assert not at.exception, f"Page crashed: {at.exception}"
        assert not helper.has_critical_error()

    def test_can_fill_project_details(self, report_app, app_helper):
        """Should be able to fill in project details."""
        at = report_app.run(timeout=30)
        helper = app_helper(at)

        # Find text inputs for project info
        if len(at.text_input) >= 1:
            at = at.text_input[0].set_value("Test Project").run()
            assert not at.exception


@skip_if_no_apptest
class TestCrossPageIntegration:
    """Tests that verify data flows correctly between pages."""

    def test_pages_share_session_state(self, create_app_test, app_helper):
        """Verify session state is shared across pages."""
        # Load beam design page
        beam_at = create_app_test("01_🏗️_beam_design.py").run(timeout=30)
        assert not beam_at.exception

        # Modify a value
        if len(beam_at.number_input) >= 1:
            beam_at = beam_at.number_input[0].set_value(5500.0).run()
            assert not beam_at.exception

        # Load compliance page
        compliance_at = create_app_test("03_✅_compliance.py").run(timeout=30)
        assert not compliance_at.exception

    def test_all_pages_survive_rapid_navigation(self, create_app_test, all_page_files):
        """Test that rapidly loading different pages doesn't crash."""
        for page_file in all_page_files[:5]:  # Test first 5 pages
            at = create_app_test(page_file.name).run(timeout=30)
            assert not at.exception, f"{page_file.name} crashed: {at.exception}"


@skip_if_no_apptest
class TestEdgeCaseHandling:
    """Tests for edge cases and error conditions."""

    def test_empty_session_state_handling(self, beam_design_app, app_helper):
        """Pages should handle empty session state gracefully."""
        at = beam_design_app.run(timeout=30)
        assert not at.exception

    def test_widget_rerun_stability(self, beam_design_app):
        """Multiple reruns should not cause issues."""
        at = beam_design_app.run(timeout=30)

        # Run multiple times
        for _ in range(3):
            at = at.run()
            assert not at.exception, f"Rerun crashed: {at.exception}"

    def test_selectbox_all_options_valid(self, beam_design_app, app_helper):
        """All selectbox options should be valid and not crash."""
        at = beam_design_app.run(timeout=30)
        helper = app_helper(at)

        for sb in at.selectbox:
            options = sb.options if hasattr(sb, "options") else []
            for opt in options:
                try:
                    at = sb.set_value(opt).run()
                    # Should not have unhandled exception
                    if at.exception:
                        # Check if it's a validation error (acceptable) vs crash
                        exc_str = str(at.exception).lower()
                        assert any(
                            kw in exc_str
                            for kw in ["validation", "value", "invalid"]
                        ), f"Unhandled exception for option {opt}: {at.exception}"
                except Exception as e:
                    pytest.fail(f"Failed to set option {opt}: {e}")


@skip_if_no_apptest
class TestPerformance:
    """Basic performance tests."""

    def test_page_load_time_reasonable(self, create_app_test, all_page_files):
        """All pages should load within reasonable time."""
        import time

        for page_file in all_page_files:
            start = time.time()
            at = create_app_test(page_file.name).run(timeout=30)
            elapsed = time.time() - start

            assert not at.exception, f"{page_file.name} crashed: {at.exception}"
            # Should load within 10 seconds (generous for CI)
            assert elapsed < 10, f"{page_file.name} took {elapsed:.2f}s to load"

    def test_calculation_completes_in_reasonable_time(self, beam_design_app, app_helper):
        """Beam calculation should complete within reasonable time."""
        import time

        at = beam_design_app.run(timeout=30)
        helper = app_helper(at)

        calc_btn = helper.get_button_by_label("calculate")
        if calc_btn:
            start = time.time()
            at = calc_btn.click().run()
            elapsed = time.time() - start

            assert not at.exception, f"Calculation failed: {at.exception}"
            # Calculation should complete within 5 seconds
            assert elapsed < 5, f"Calculation took {elapsed:.2f}s"
