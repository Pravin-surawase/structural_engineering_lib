"""
Preview Component Tests
=======================

Tests for real-time preview functionality.

Priority: HIGH (new code must have tests)
Coverage Target: 80%
"""

import pytest
from unittest.mock import Mock, patch

# Import preview functions
from components.preview import (
    create_beam_preview_diagram,
    calculate_quick_checks,
    calculate_rough_cost,
    _get_min_cover
)
from utils.design_system import ANIMATION


class TestCreateBeamPreviewDiagram:
    """Tests for beam preview diagram generation."""

    def test_returns_figure(self):
        """Should return a Plotly Figure object."""
        import plotly.graph_objects as go

        fig = create_beam_preview_diagram(
            span_mm=5000.0,
            b_mm=300.0,
            D_mm=500.0,
            support_condition="Simply Supported"
        )

        assert isinstance(fig, go.Figure)

    def test_uses_numeric_duration(self):
        """CRITICAL: Must use integer duration for Plotly."""
        fig = create_beam_preview_diagram(
            span_mm=5000.0,
            b_mm=300.0,
            D_mm=500.0,
            support_condition="Simply Supported"
        )

        # Check transition duration is integer
        duration = fig.layout.transition.duration
        assert isinstance(duration, int), f"Expected int, got {type(duration)}"
        assert duration == ANIMATION.duration_normal_ms

    def test_different_support_conditions(self):
        """Should handle all support conditions."""
        conditions = ["Simply Supported", "Cantilever", "Fixed-Fixed", "Unknown"]

        for condition in conditions:
            fig = create_beam_preview_diagram(
                span_mm=5000.0,
                b_mm=300.0,
                D_mm=500.0,
                support_condition=condition
            )
            assert fig is not None

    def test_has_beam_shape(self):
        """Figure should contain beam rectangle shape."""
        fig = create_beam_preview_diagram(
            span_mm=5000.0,
            b_mm=300.0,
            D_mm=500.0,
            support_condition="Simply Supported"
        )

        # Check for at least one shape (beam rectangle)
        assert len(fig.layout.shapes) >= 1


class TestCalculateQuickChecks:
    """Tests for design check calculations."""

    def test_returns_list(self):
        """Should return a list of checks."""
        checks = calculate_quick_checks(
            span_mm=5000.0,
            d_mm=450.0,
            b_mm=300.0,
            D_mm=500.0,
            exposure="Moderate"
        )

        assert isinstance(checks, list)
        assert len(checks) >= 4  # At least 4 checks

    def test_check_structure(self):
        """Each check should have required fields."""
        checks = calculate_quick_checks(
            span_mm=5000.0,
            d_mm=450.0,
            b_mm=300.0,
            D_mm=500.0,
            exposure="Moderate"
        )

        required_fields = ["name", "status", "value", "limit", "message"]
        for check in checks:
            for field in required_fields:
                assert field in check, f"Missing {field} in check {check.get('name')}"

    def test_status_values(self):
        """Status should be one of: pass, warning, fail."""
        checks = calculate_quick_checks(
            span_mm=5000.0,
            d_mm=450.0,
            b_mm=300.0,
            D_mm=500.0,
            exposure="Moderate"
        )

        valid_statuses = {"pass", "warning", "fail"}
        for check in checks:
            assert check["status"] in valid_statuses

    def test_span_d_pass(self):
        """Good span/d should pass."""
        checks = calculate_quick_checks(
            span_mm=5000.0,
            d_mm=450.0,  # span/d = 11.1, well under 20
            b_mm=300.0,
            D_mm=500.0,
            exposure="Moderate"
        )

        span_d_check = next(c for c in checks if c["name"] == "Span/d Ratio")
        assert span_d_check["status"] == "pass"

    def test_span_d_fail(self):
        """Bad span/d should fail."""
        checks = calculate_quick_checks(
            span_mm=10000.0,
            d_mm=300.0,  # span/d = 33.3, over 20
            b_mm=300.0,
            D_mm=350.0,
            exposure="Moderate"
        )

        span_d_check = next(c for c in checks if c["name"] == "Span/d Ratio")
        assert span_d_check["status"] == "fail"

    def test_d_less_than_D(self):
        """d < D check should work."""
        # Valid case
        checks_valid = calculate_quick_checks(
            span_mm=5000.0,
            d_mm=450.0,
            b_mm=300.0,
            D_mm=500.0,
            exposure="Moderate"
        )
        d_D_check = next(c for c in checks_valid if c["name"] == "d < D")
        assert d_D_check["status"] == "pass"

        # Invalid case (d >= D)
        checks_invalid = calculate_quick_checks(
            span_mm=5000.0,
            d_mm=500.0,  # d == D, invalid
            b_mm=300.0,
            D_mm=500.0,
            exposure="Moderate"
        )
        d_D_check = next(c for c in checks_invalid if c["name"] == "d < D")
        assert d_D_check["status"] == "fail"


class TestGetMinCover:
    """Tests for minimum cover lookup."""

    def test_known_exposures(self):
        """Should return correct cover for known exposures."""
        assert _get_min_cover("Mild") == 20
        assert _get_min_cover("Moderate") == 30
        assert _get_min_cover("Severe") == 45
        assert _get_min_cover("Very Severe") == 50
        assert _get_min_cover("Extreme") == 75

    def test_unknown_exposure(self):
        """Should return default for unknown exposure."""
        assert _get_min_cover("Unknown") == 30
        assert _get_min_cover("") == 30


class TestCalculateRoughCost:
    """Tests for cost estimation."""

    def test_returns_dict(self):
        """Should return a cost dict."""
        cost = calculate_rough_cost(
            b_mm=300.0,
            D_mm=500.0,
            span_mm=5000.0,
            concrete_grade="M25",
            mu_knm=120.0
        )

        assert isinstance(cost, dict)

    def test_cost_structure(self):
        """Cost dict should have required fields."""
        cost = calculate_rough_cost(
            b_mm=300.0,
            D_mm=500.0,
            span_mm=5000.0,
            concrete_grade="M25",
            mu_knm=120.0
        )

        required = ["concrete_m3", "concrete_cost", "steel_kg", "steel_cost", "total_cost"]
        for field in required:
            assert field in cost, f"Missing {field}"

    def test_positive_values(self):
        """All costs should be positive."""
        cost = calculate_rough_cost(
            b_mm=300.0,
            D_mm=500.0,
            span_mm=5000.0,
            concrete_grade="M25",
            mu_knm=120.0
        )

        assert cost["concrete_cost"] > 0
        assert cost["steel_cost"] > 0
        assert cost["total_cost"] > 0

    def test_total_is_sum(self):
        """Total should be concrete + steel."""
        cost = calculate_rough_cost(
            b_mm=300.0,
            D_mm=500.0,
            span_mm=5000.0,
            concrete_grade="M25",
            mu_knm=120.0
        )

        expected_total = cost["concrete_cost"] + cost["steel_cost"]
        assert cost["total_cost"] == expected_total

    def test_higher_moment_more_steel(self):
        """Higher moment should estimate more steel."""
        cost_low = calculate_rough_cost(
            b_mm=300.0,
            D_mm=500.0,
            span_mm=5000.0,
            concrete_grade="M25",
            mu_knm=50.0  # Low moment
        )

        cost_high = calculate_rough_cost(
            b_mm=300.0,
            D_mm=500.0,
            span_mm=5000.0,
            concrete_grade="M25",
            mu_knm=200.0  # High moment
        )

        assert cost_high["steel_kg"] > cost_low["steel_kg"]


class TestIntegration:
    """Integration tests for preview pipeline."""

    def test_full_preview_flow(self):
        """Test complete preview generation without errors."""
        # This simulates what render_real_time_preview does
        fig = create_beam_preview_diagram(
            span_mm=5000.0,
            b_mm=300.0,
            D_mm=500.0,
            support_condition="Simply Supported"
        )
        assert fig is not None

        checks = calculate_quick_checks(
            span_mm=5000.0,
            d_mm=450.0,
            b_mm=300.0,
            D_mm=500.0,
            exposure="Moderate"
        )
        assert len(checks) >= 4

        cost = calculate_rough_cost(
            b_mm=300.0,
            D_mm=500.0,
            span_mm=5000.0,
            concrete_grade="M25",
            mu_knm=120.0
        )
        assert cost["total_cost"] > 0

    def test_preview_with_design_system_tokens(self):
        """Verify design system tokens are used correctly."""
        fig = create_beam_preview_diagram(
            span_mm=5000.0,
            b_mm=300.0,
            D_mm=500.0,
            support_condition="Simply Supported"
        )

        # CRITICAL: Verify Plotly gets integer duration
        assert isinstance(fig.layout.transition.duration, int)
        assert fig.layout.transition.duration == ANIMATION.duration_normal_ms
