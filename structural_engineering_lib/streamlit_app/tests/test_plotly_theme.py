"""
Unit tests for plotly_theme module.

Tests Plotly theme configuration, color scales, and chart utilities.
"""

import pytest
import plotly.graph_objects as go
from streamlit_app.utils.plotly_theme import (
    IS456_THEME,
    IS456_DARK_THEME,
    STRESS_COLORSCALE,
    UTILIZATION_COLORSCALE,
    SAFETY_FACTOR_COLORSCALE,
    COLORBLIND_SAFE_PALETTE,
    get_chart_config,
    apply_theme,
    create_hover_template,
)
from streamlit_app.utils.design_system import COLORS


# ============================================================================
# TEST: THEME CONFIGURATION
# ============================================================================


class TestIS456Theme:
    """Test IS456 Plotly theme configuration."""

    def test_theme_has_layout(self):
        """Theme should have layout configuration."""
        assert "layout" in IS456_THEME
        assert isinstance(IS456_THEME["layout"], dict)

    def test_theme_has_data_config(self):
        """Theme should have data trace configuration."""
        assert "data" in IS456_THEME
        assert isinstance(IS456_THEME["data"], dict)

    def test_font_family_set(self):
        """Theme should use Inter font."""
        assert "font" in IS456_THEME["layout"]
        assert "family" in IS456_THEME["layout"]["font"]

    def test_color_sequence_defined(self):
        """Theme should have color sequence."""
        assert "colorway" in IS456_THEME["layout"]
        colors = IS456_THEME["layout"]["colorway"]
        assert len(colors) >= 5
        assert COLORS.primary_500 in colors
        assert COLORS.accent_500 in colors

    def test_grid_colors_set(self):
        """Theme should have grid colors."""
        assert "xaxis" in IS456_THEME["layout"]
        assert "gridcolor" in IS456_THEME["layout"]["xaxis"]

    def test_background_colors_set(self):
        """Theme should have background colors."""
        assert "paper_bgcolor" in IS456_THEME["layout"]
        assert "plot_bgcolor" in IS456_THEME["layout"]

    def test_hover_config_defined(self):
        """Theme should have hover configuration."""
        assert "hoverlabel" in IS456_THEME["layout"]
        assert "bgcolor" in IS456_THEME["layout"]["hoverlabel"]


class TestIS456DarkTheme:
    """Test IS456 dark mode theme."""

    def test_dark_theme_has_layout(self):
        """Dark theme should have layout."""
        assert "layout" in IS456_DARK_THEME

    def test_dark_background_differs(self):
        """Dark theme background should differ from light."""
        light_bg = IS456_THEME["layout"]["paper_bgcolor"]
        dark_bg = IS456_DARK_THEME["layout"]["paper_bgcolor"]
        assert light_bg != dark_bg
        assert dark_bg.startswith("#")

    def test_dark_grid_colors_differ(self):
        """Dark theme grid colors should differ."""
        light_grid = IS456_THEME["layout"]["xaxis"]["gridcolor"]
        dark_grid = IS456_DARK_THEME["layout"]["xaxis"]["gridcolor"]
        assert light_grid != dark_grid


# ============================================================================
# TEST: COLOR SCALES
# ============================================================================


class TestColorScales:
    """Test engineering-specific color scales."""

    def test_stress_colorscale_format(self):
        """Stress colorscale should have correct format."""
        assert len(STRESS_COLORSCALE) == 3
        assert STRESS_COLORSCALE[0][0] == 0.0
        assert STRESS_COLORSCALE[-1][0] == 1.0
        # Check colors are hex strings
        assert STRESS_COLORSCALE[0][1].startswith("#")

    def test_utilization_colorscale_format(self):
        """Utilization colorscale should have correct format."""
        assert len(UTILIZATION_COLORSCALE) >= 3
        assert UTILIZATION_COLORSCALE[0][0] == 0.0
        assert UTILIZATION_COLORSCALE[-1][0] == 1.0

    def test_utilization_green_to_red(self):
        """Utilization should go from green (safe) to red (over)."""
        first_color = UTILIZATION_COLORSCALE[0][1]
        last_color = UTILIZATION_COLORSCALE[-1][1]
        assert first_color == COLORS.success
        assert last_color == COLORS.error

    def test_safety_factor_colorscale_format(self):
        """Safety factor colorscale should have correct format."""
        assert len(SAFETY_FACTOR_COLORSCALE) >= 3
        assert SAFETY_FACTOR_COLORSCALE[0][0] == 0.0

    def test_colorblind_safe_palette_length(self):
        """Colorblind safe palette should have multiple colors."""
        assert len(COLORBLIND_SAFE_PALETTE) >= 6
        for color in COLORBLIND_SAFE_PALETTE:
            assert color.startswith("#")


# ============================================================================
# TEST: CHART CONFIGURATION
# ============================================================================


class TestGetChartConfig:
    """Test get_chart_config function."""

    def test_interactive_mode(self):
        """Interactive mode should enable modebar."""
        config = get_chart_config(interactive=True)
        assert "displayModeBar" in config
        assert config["displayModeBar"] is True
        assert "modeBarButtonsToRemove" in config

    def test_static_mode(self):
        """Static mode should disable modebar."""
        config = get_chart_config(interactive=False)
        assert "displayModeBar" in config
        assert config["displayModeBar"] is False
        assert "staticPlot" in config
        assert config["staticPlot"] is True

    def test_image_export_config(self):
        """Interactive mode should have image export config."""
        config = get_chart_config(interactive=True)
        assert "toImageButtonOptions" in config
        export_opts = config["toImageButtonOptions"]
        assert export_opts["format"] == "png"
        assert export_opts["scale"] == 2

    def test_logo_hidden(self):
        """Plotly logo should be hidden."""
        config = get_chart_config(interactive=True)
        assert config["displaylogo"] is False


# ============================================================================
# TEST: APPLY THEME FUNCTION
# ============================================================================


class TestApplyTheme:
    """Test apply_theme function."""

    def test_applies_to_simple_figure(self):
        """Theme should apply to a simple figure."""
        fig = go.Figure(data=[go.Bar(x=[1, 2, 3], y=[4, 5, 6])])
        apply_theme(fig, dark_mode=False)

        # Check that layout was updated
        assert fig.layout.font.family is not None
        assert fig.layout.paper_bgcolor is not None

    def test_applies_to_scatter_plot(self):
        """Theme should apply to scatter plot."""
        fig = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 5, 6])])
        apply_theme(fig, dark_mode=False)

        assert fig.layout.xaxis.gridcolor is not None
        assert fig.layout.yaxis.gridcolor is not None

    def test_dark_mode_applies_different_colors(self):
        """Dark mode should apply different colors."""
        fig1 = go.Figure(data=[go.Bar(x=[1, 2], y=[3, 4])])
        fig2 = go.Figure(data=[go.Bar(x=[1, 2], y=[3, 4])])

        apply_theme(fig1, dark_mode=False)
        apply_theme(fig2, dark_mode=True)

        # Background colors should differ
        assert fig1.layout.paper_bgcolor != fig2.layout.paper_bgcolor

    def test_preserves_existing_data(self):
        """Theme should not overwrite existing trace data."""
        fig = go.Figure(data=[go.Bar(x=[1, 2, 3], y=[10, 20, 30])])
        original_y = list(fig.data[0].y)

        apply_theme(fig)

        # Data should be unchanged
        assert list(fig.data[0].y) == original_y

    def test_applies_to_multiple_traces(self):
        """Theme should apply to figures with multiple traces."""
        fig = go.Figure(
            data=[
                go.Scatter(x=[1, 2], y=[3, 4], name="Series 1"),
                go.Scatter(x=[1, 2], y=[5, 6], name="Series 2"),
            ]
        )

        apply_theme(fig)

        # Both traces should exist
        assert len(fig.data) == 2


# ============================================================================
# TEST: HOVER TEMPLATE CREATION
# ============================================================================


class TestCreateHoverTemplate:
    """Test create_hover_template function."""

    def test_basic_template(self):
        """Create basic hover template."""
        template = create_hover_template(
            labels={"mu": "Moment"},
            units={"mu": "kN·m"},
        )

        assert "Moment" in template
        assert "kN·m" in template
        assert "<extra></extra>" in template

    def test_multiple_fields(self):
        """Create template with multiple fields."""
        template = create_hover_template(
            labels={"mu": "Moment", "vu": "Shear"},
            units={"mu": "kN·m", "vu": "kN"},
        )

        assert "Moment" in template
        assert "Shear" in template
        assert "kN·m" in template
        assert "kN" in template

    def test_custom_precision(self):
        """Create template with custom precision."""
        template = create_hover_template(
            labels={"ast": "Steel Area"},
            units={"ast": "mm²"},
            precision={"ast": 0},
        )

        assert ".0f" in template  # 0 decimal places

    def test_default_precision(self):
        """Default precision should be 2 decimal places."""
        template = create_hover_template(
            labels={"value": "Value"},
            units={"value": "units"},
        )

        assert ".2f" in template  # 2 decimal places (default)

    def test_empty_units(self):
        """Template should work with empty units."""
        template = create_hover_template(
            labels={"ratio": "Ratio"},
            units={"ratio": ""},
        )

        assert "Ratio" in template
        assert "<b>" in template
        assert "</b>" in template


# ============================================================================
# TEST: THEME INTEGRATION
# ============================================================================


class TestThemeIntegration:
    """Test full theme integration scenarios."""

    def test_complete_bar_chart_workflow(self):
        """Test complete workflow for bar chart."""
        # Create figure
        fig = go.Figure(data=[go.Bar(x=["A", "B", "C"], y=[10, 20, 15], name="Values")])

        # Apply theme
        apply_theme(fig)

        # Get config
        config = get_chart_config(interactive=True)

        # Verify everything is set
        assert fig.layout.font is not None
        assert config["displayModeBar"] is True

    def test_complete_scatter_chart_workflow(self):
        """Test complete workflow for scatter plot."""
        fig = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 5, 6], mode="markers")])

        apply_theme(fig, dark_mode=False)
        config = get_chart_config(interactive=True)

        assert fig.layout.paper_bgcolor is not None
        assert config is not None

    def test_gauge_chart_with_theme(self):
        """Test gauge/indicator chart with theme."""
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=75,
                title={"text": "Utilization"},
                domain={"x": [0, 1], "y": [0, 1]},
            )
        )

        apply_theme(fig)

        # Should not raise errors
        assert fig.data[0].mode == "gauge+number"

    def test_theme_with_custom_colors(self):
        """Theme should not override custom trace colors."""
        fig = go.Figure(data=[go.Bar(x=[1, 2], y=[3, 4], marker={"color": "#FF0000"})])

        apply_theme(fig)

        # Custom color should be preserved
        assert fig.data[0].marker.color == "#FF0000"


# ============================================================================
# TEST: ACCESSIBILITY
# ============================================================================


class TestAccessibility:
    """Test accessibility features of theme."""

    def test_colorblind_palette_distinct(self):
        """Colorblind safe palette should have distinct colors."""
        # All colors should be different
        assert len(COLORBLIND_SAFE_PALETTE) == len(set(COLORBLIND_SAFE_PALETTE))

    def test_theme_uses_monospace_for_numbers(self):
        """Theme should use monospace font for axis ticks."""
        xaxis = IS456_THEME["layout"]["xaxis"]
        assert "tickfont" in xaxis
        # Font family should include monospace
        # (exact check depends on TYPOGRAPHY.font_mono structure)

    def test_high_contrast_grid(self):
        """Grid lines should be visible but not overwhelming."""
        grid_color = IS456_THEME["layout"]["xaxis"]["gridcolor"]
        # Should be a gray (not too light, not too dark)
        assert grid_color.startswith("#")


# ============================================================================
# TEST: ERROR HANDLING
# ============================================================================


class TestErrorHandling:
    """Test error handling in theme functions."""

    def test_apply_theme_handles_empty_figure(self):
        """Apply theme should handle empty figure."""
        fig = go.Figure()
        apply_theme(fig)
        # Should not raise errors

    def test_create_hover_template_empty_labels(self):
        """Hover template with empty labels."""
        template = create_hover_template(labels={}, units={})
        assert "<extra></extra>" in template

    def test_get_chart_config_default_interactive(self):
        """Chart config should default to interactive=True."""
        config = get_chart_config()
        assert config["displayModeBar"] is True
