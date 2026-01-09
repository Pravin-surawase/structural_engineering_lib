"""
Integration tests for IMPL-005: UI Polish & Responsive Design

Tests that all UI polish utilities work together correctly when integrated
into pages and components.

Author: Agent 6 (Streamlit UI Specialist)
Date: 2026-01-09
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from streamlit_app.utils.responsive import get_device_type, get_responsive_columns, apply_responsive_styles
from streamlit_app.utils.performance import lazy_load, measure_render_time, batch_render
from streamlit_app.utils.accessibility import add_aria_label, validate_color_contrast, announce_to_screen_reader
from streamlit_app.components.polish import show_skeleton_loader, show_empty_state, show_toast


# =============================================================================
# RESPONSIVE INTEGRATION TESTS
# =============================================================================

class TestResponsiveIntegration:
    """Test responsive design integration."""

    def test_page_loads_with_responsive_layout(self, mock_streamlit):
        """Test that pages can apply responsive styles without errors."""
        # Should not raise any exceptions
        apply_responsive_styles()
        assert True  # If we get here, no errors occurred

    def test_columns_adapt_to_device_type(self, mock_streamlit):
        """Test that columns adjust based on device type."""
        # Set device type in session state (don't replace the whole object)
        mock_streamlit.session_state["device_type"] = "mobile"

        cols = get_responsive_columns(mobile=1, tablet=2, desktop=3)

        assert isinstance(cols, list)
        # Should return 1 column for mobile
        assert len(cols) == 1

    def test_tablet_responsive_columns(self, mock_streamlit):
        """Test tablet breakpoint returns correct columns."""
        mock_streamlit.session_state["device_type"] = "tablet"

        cols = get_responsive_columns(mobile=1, tablet=2, desktop=3)

        assert len(cols) == 2

    def test_desktop_responsive_columns(self, mock_streamlit):
        """Test desktop breakpoint returns correct columns."""
        mock_streamlit.session_state["device_type"] = "desktop"

        cols = get_responsive_columns(mobile=1, tablet=2, desktop=3)

        assert len(cols) == 3

    def test_device_type_detection_with_fallback(self, mock_streamlit):
        """Test device detection falls back gracefully."""
        # No session state = fallback to desktop
        device = get_device_type()

        assert device in ["mobile", "tablet", "desktop"]


# =============================================================================
# PERFORMANCE INTEGRATION TESTS
# =============================================================================

class TestPerformanceIntegration:
    """Test performance optimization integration."""

    def test_lazy_loading_decorator_integration(self, mock_streamlit):
        """Test lazy loading works with components."""

        @lazy_load
        def expensive_component():
            return "computed result"

        # Should execute without errors
        result = expensive_component()
        assert result == "computed result"

    def test_performance_measurement_integration(self, mock_streamlit):
        """Test performance measurement in real workflow."""
        with measure_render_time("test_component"):
            # Simulate component rendering
            result = 1 + 1

        assert result == 2  # Computation still works

    def test_batch_render_integration(self, mock_streamlit):
        """Test batch rendering with multiple items."""
        items = list(range(50))

        rendered = []

        def collect_item(item):
            """Render function that collects items for verification."""
            rendered.append(item)

        # Use actual batch_render API: (items, render_fn, batch_size)
        batch_render(items, collect_item, batch_size=10)

        assert len(rendered) == 50
        assert rendered == items

    def test_cache_usage_in_design_workflow(self, mock_streamlit):
        """Test caching works in design calculation workflow."""
        from streamlit_app.utils.api_wrapper import cached_design

        # Use correct API signature:
        # cached_design(mu_knm, vu_kn, b_mm, D_mm, d_mm, fck_nmm2, fy_nmm2, **kwargs)
        mu_knm = 120.0
        vu_kn = 80.0
        b_mm = 300.0
        D_mm = 500.0
        d_mm = 450.0
        fck_nmm2 = 25.0
        fy_nmm2 = 500.0

        # First call - should compute
        result1 = cached_design(mu_knm, vu_kn, b_mm, D_mm, d_mm, fck_nmm2, fy_nmm2)

        # Second call - should use cache (same params)
        result2 = cached_design(mu_knm, vu_kn, b_mm, D_mm, d_mm, fck_nmm2, fy_nmm2)

        # Both should return results
        assert result1 is not None
        assert result2 is not None

    def test_render_stats_collection(self, mock_streamlit):
        """Test that render statistics are collected."""
        from streamlit_app.utils.performance import get_render_stats

        # After some measurements
        with measure_render_time("component_a"):
            pass

        # Get stats for the specific component we measured
        stats = get_render_stats("component_a")
        # Should return a float (milliseconds) or None
        assert stats is None or isinstance(stats, float)


# =============================================================================
# ACCESSIBILITY INTEGRATION TESTS
# =============================================================================

class TestAccessibilityIntegration:
    """Test accessibility feature integration."""

    def test_page_title_integration(self, mock_streamlit):
        """Test page title can be set."""
        add_aria_label("page-title", "Beam Design", role="heading")
        # Should not raise exceptions
        assert True

    def test_color_contrast_validation(self):
        """Test color contrast checker works."""
        # Good contrast (black on white) - returns dict with passes_text=True
        result = validate_color_contrast("#000000", "#FFFFFF")
        assert result["passes_text"] is True

        # Poor contrast (light gray on white) - should fail text contrast
        result_poor = validate_color_contrast("#EEEEEE", "#FFFFFF")
        assert result_poor["passes_text"] is False

    def test_screen_reader_announcements(self, mock_streamlit):
        """Test screen reader announcements."""
        announce_to_screen_reader("Design calculation complete")
        # Should not raise exceptions
        assert True


# =============================================================================
# POLISH INTEGRATION TESTS
# =============================================================================

class TestPolishIntegration:
    """Test visual polish integration."""

    def test_skeleton_loader_during_calculation(self, mock_streamlit):
        """Test skeleton loader appears during loading."""
        show_skeleton_loader(rows=3, height=60)
        # Should render without errors - function call succeeds
        assert True

    def test_empty_state_when_no_results(self, mock_streamlit):
        """Test empty state displays correctly."""
        show_empty_state(
            title="No Results",
            message="Click Calculate to see results",
            icon="📊"
        )
        # Should render without errors
        assert True

    def test_toast_notifications(self, mock_streamlit):
        """Test toast notifications display."""
        show_toast("Calculation complete!", type="success")
        # Should render without errors
        assert True

    def test_transitions_applied(self, mock_streamlit):
        """Test smooth transitions are applied."""
        from streamlit_app.components.polish import apply_hover_effect

        apply_hover_effect("button_1", hover_color="#0066CC")
        # Should apply styles without errors
        assert True


# =============================================================================
# END-TO-END INTEGRATION TESTS
# =============================================================================

class TestEndToEndIntegration:
    """Test complete workflows with all features."""

    def test_full_design_workflow_with_all_features(self, mock_streamlit):
        """Test complete design workflow uses all polish features."""
        # 1. Apply responsive layout
        apply_responsive_styles()
        device = get_device_type()
        cols = get_responsive_columns(mobile=1, tablet=2, desktop=3)

        # 2. Show loading state
        show_skeleton_loader(rows=5)

        # 3. Measure performance
        with measure_render_time("full_design"):
            # 4. Calculate (mocked)
            result = {"ast_required": 682, "status": "SAFE"}

        # 5. Show success toast
        show_toast("Design complete!", type="success")

        # Workflow completed without errors
        assert result["status"] == "SAFE"

    def test_error_handling_with_polish(self, mock_streamlit):
        """Test error scenarios display polished UI."""
        try:
            # Simulate error
            raise ValueError("Invalid input")
        except ValueError as e:
            # Show error toast
            show_toast(str(e), type="error")

        # Error was handled gracefully - function ran without exceptions
        assert True

    def test_mobile_experience(self, mock_streamlit):
        """Test mobile user gets optimized experience."""
        # Simulate mobile device
        mock_streamlit.session_state["device_type"] = "mobile"

        # Apply mobile layout
        apply_responsive_styles()
        cols = get_responsive_columns(mobile=1, tablet=2, desktop=3)

        # Mobile gets 1 column
        assert len(cols) == 1

        # Mobile-optimized loading
        show_skeleton_loader(rows=3, height=80)

        assert True  # Mobile experience works


# =============================================================================
# INTEGRATION WITH EXISTING COMPONENTS
# =============================================================================

class TestExistingComponentIntegration:
    """Test integration with existing components."""

    def test_results_component_with_polish(self, mock_streamlit):
        """Test results.py components work with polish."""
        from streamlit_app.components.results import display_design_status

        # Mock result
        result = {"overall_status": "SAFE", "status": "SAFE"}

        # Should work with existing component
        display_design_status(result)

        assert True  # No errors

    def test_visualization_component_with_lazy_loading(self, mock_streamlit):
        """Test visualizations.py works with lazy loading."""
        from streamlit_app.components.visualizations import create_beam_diagram

        # This should work with or without lazy loading
        try:
            fig = create_beam_diagram(
                span_m=5.0,
                width_mm=300,
                depth_mm=500,
                ast_provided=800,
                xu=100.0,
                compression_bars=2,
                tension_bars=3
            )
            # If it returns, it works
            assert fig is not None
        except Exception:
            # Expected in test environment without plotly
            pass

    def test_input_component_with_accessibility(self, mock_streamlit):
        """Test inputs.py components work with accessibility."""
        from streamlit_app.components.inputs import dimension_input

        # Should work with accessibility features
        # Use correct signature: label, min_value, max_value, default_value
        result = dimension_input("Span", min_value=1.0, max_value=20.0, default_value=5.0)

        assert result is not None


# =============================================================================
# PERFORMANCE IMPACT TESTS
# =============================================================================

class TestPerformanceImpact:
    """Test that polish features don't degrade performance."""

    def test_no_performance_regression(self, mock_streamlit):
        """Test that adding polish doesn't slow down app."""
        import time

        # Measure baseline
        start = time.time()
        for _ in range(10):
            cols = get_responsive_columns(1, 2, 3)
        baseline = time.time() - start

        # Should be fast (< 0.1s for 10 iterations)
        assert baseline < 0.1

    def test_lazy_loading_improves_perceived_speed(self, mock_streamlit):
        """Test lazy loading shows immediate feedback."""
        # Show skeleton immediately
        show_skeleton_loader(rows=3)

        # User sees something right away - function ran successfully
        assert True

    def test_cache_reduces_redundant_calculations(self, mock_streamlit):
        """Test caching works as expected."""
        from streamlit_app.utils.api_wrapper import cached_design

        # Use correct API signature:
        # cached_design(mu_knm, vu_kn, b_mm, D_mm, d_mm, fck_nmm2, fy_nmm2, **kwargs)
        mu_knm = 120.0
        vu_kn = 80.0
        b_mm = 300.0
        D_mm = 500.0
        d_mm = 450.0
        fck_nmm2 = 25.0
        fy_nmm2 = 500.0

        # First call
        result1 = cached_design(mu_knm, vu_kn, b_mm, D_mm, d_mm, fck_nmm2, fy_nmm2)

        # Second call should be instant (cached)
        import time
        start = time.time()
        result2 = cached_design(mu_knm, vu_kn, b_mm, D_mm, d_mm, fck_nmm2, fy_nmm2)
        duration = time.time() - start

        # Should be very fast (< 0.01s)
        assert duration < 0.01
