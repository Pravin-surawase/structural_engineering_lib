"""
Tests for Plotly Enhancement Utilities
=======================================

Tests for advanced visualization features:
- Animation configurations
- Export settings
- Hover templates
- Responsive layouts
- Dark mode themes

Author: STREAMLIT UI SPECIALIST (Agent 6)
Status: ✅ IMPLEMENTED (STREAMLIT-UI-003)
"""

import pytest
import plotly.graph_objects as go
from utils.plotly_enhancements import (
    add_animation_config,
    add_export_config,
    create_rich_hover_template,
    add_responsive_layout,
    add_gridlines,
    add_annotations_layer,
    add_loading_skeleton,
    apply_dark_mode_theme,
    ENGINEERING_CHART_CONFIG,
    PRESENTATION_CHART_CONFIG,
    PRINT_CHART_CONFIG,
)


class TestAnimationConfig:
    """Tests for animation configuration."""

    def test_add_animation_default_duration(self):
        """Test adding animation with default duration."""
        fig = go.Figure()
        fig_animated = add_animation_config(fig)

        assert "transition" in fig_animated.layout
        assert fig_animated.layout.transition.duration == 300
        assert fig_animated.layout.transition.easing == "cubic-in-out"

    def test_add_animation_custom_duration(self):
        """Test adding animation with custom duration."""
        fig = go.Figure()
        fig_animated = add_animation_config(fig, duration_ms=500)

        assert fig_animated.layout.transition.duration == 500

    def test_animation_has_play_button(self):
        """Test that animation config includes play button."""
        fig = go.Figure()
        fig_animated = add_animation_config(fig)

        assert hasattr(fig_animated.layout, "updatemenus")
        assert len(fig_animated.layout.updatemenus) > 0
        assert fig_animated.layout.updatemenus[0].type == "buttons"


class TestExportConfig:
    """Tests for export configuration."""

    def test_add_export_config_default(self):
        """Test adding export config with defaults."""
        fig = go.Figure()
        fig_export, config = add_export_config(fig)

        assert "toImageButtonOptions" in config
        assert config["toImageButtonOptions"]["format"] == "png"
        assert config["toImageButtonOptions"]["scale"] == 2
        assert config["displaylogo"] is False

    def test_add_export_config_custom_filename(self):
        """Test custom filename in export."""
        fig = go.Figure()
        fig_export, config = add_export_config(fig, filename="my_chart")

        assert config["toImageButtonOptions"]["filename"] == "my_chart"

    def test_modebar_configuration(self):
        """Test modebar styling."""
        fig = go.Figure()
        fig_export, config = add_export_config(fig)

        assert hasattr(fig_export.layout, "modebar")
        assert fig_export.layout.modebar.orientation == "v"


class TestHoverTemplates:
    """Tests for rich hover template creation."""

    def test_create_basic_hover_template(self):
        """Test basic hover template."""
        template = create_rich_hover_template(
            "Test Title", {"Field1": "value1", "Field2": "value2"}
        )

        assert "<b>Test Title</b>" in template
        assert "Field1:" in template
        assert "Field2:" in template
        assert "<extra></extra>" in template

    def test_hover_template_with_formatting(self):
        """Test hover template with value formatting."""
        template = create_rich_hover_template(
            "Cost Analysis", {"Cost": "₹%{x:.2f}/m", "Area": "%{customdata}mm²"}
        )

        assert "₹%{x:.2f}/m" in template
        assert "%{customdata}mm²" in template

    def test_hover_template_show_extra(self):
        """Test hover template with extra info."""
        template = create_rich_hover_template(
            "Title", {"Field": "value"}, show_extra=True
        )

        assert "<extra></extra>" not in template


class TestResponsiveLayout:
    """Tests for responsive layout configuration."""

    def test_add_responsive_layout_default(self):
        """Test default responsive layout."""
        fig = go.Figure()
        fig_responsive = add_responsive_layout(fig)

        assert fig_responsive.layout.autosize is True
        assert fig_responsive.layout.margin.l == 60
        assert fig_responsive.layout.margin.r == 40

    def test_add_responsive_layout_fixed_height(self):
        """Test responsive layout with fixed height."""
        fig = go.Figure()
        fig_responsive = add_responsive_layout(fig, height_px=600)

        assert fig_responsive.layout.height == 600

    def test_add_responsive_layout_aspect_ratio(self):
        """Test responsive layout with aspect ratio."""
        fig = go.Figure()
        fig_responsive = add_responsive_layout(fig, aspect_ratio=16 / 9)

        assert hasattr(fig_responsive.layout, "yaxis")
        assert fig_responsive.layout.yaxis.scaleanchor == "x"


class TestGridlines:
    """Tests for gridline styling."""

    def test_add_gridlines_default(self):
        """Test default gridlines."""
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1, 2], y=[1, 2]))
        fig_grid = add_gridlines(fig)

        assert fig_grid.layout.xaxis.showgrid is True
        assert fig_grid.layout.yaxis.showgrid is True

    def test_add_gridlines_x_only(self):
        """Test x-axis gridlines only."""
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1, 2], y=[1, 2]))
        fig_grid = add_gridlines(fig, x_grid=True, y_grid=False)

        assert fig_grid.layout.xaxis.showgrid is True
        assert fig_grid.layout.yaxis.showgrid is False

    def test_add_gridlines_custom_color(self):
        """Test custom grid color."""
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1, 2], y=[1, 2]))
        fig_grid = add_gridlines(fig, grid_color="#CCCCCC", grid_width=2)

        assert fig_grid.layout.xaxis.gridcolor == "#CCCCCC"
        assert fig_grid.layout.xaxis.gridwidth == 2


class TestAnnotations:
    """Tests for annotation layer."""

    def test_add_single_annotation(self):
        """Test adding single annotation."""
        fig = go.Figure()
        annotations = [{"text": "Point A", "x": 1, "y": 1}]
        fig_ann = add_annotations_layer(fig, annotations)

        assert len(fig_ann.layout.annotations) == 1
        assert fig_ann.layout.annotations[0].text == "Point A"

    def test_add_multiple_annotations(self):
        """Test adding multiple annotations."""
        fig = go.Figure()
        annotations = [
            {"text": "Point A", "x": 1, "y": 1},
            {"text": "Point B", "x": 2, "y": 2},
            {"text": "Point C", "x": 3, "y": 3},
        ]
        fig_ann = add_annotations_layer(fig, annotations)

        assert len(fig_ann.layout.annotations) == 3

    def test_annotation_with_custom_styling(self):
        """Test annotation with custom font and arrow."""
        fig = go.Figure()
        annotations = [
            {
                "text": "Custom",
                "x": 1,
                "y": 1,
                "font_size": 16,
                "font_color": "#FF0000",
                "showarrow": True,
                "arrowhead": 3,
            }
        ]
        fig_ann = add_annotations_layer(fig, annotations)

        ann = fig_ann.layout.annotations[0]
        assert ann.font.size == 16
        assert ann.font.color == "#FF0000"
        assert ann.showarrow is True
        assert ann.arrowhead == 3


class TestLoadingSkeleton:
    """Tests for loading skeleton."""

    def test_create_loading_skeleton_default(self):
        """Test default loading skeleton."""
        fig = add_loading_skeleton()

        assert fig.layout.xaxis.visible is False
        assert fig.layout.yaxis.visible is False
        assert len(fig.layout.annotations) == 1
        assert "⏳" in fig.layout.annotations[0].text

    def test_create_loading_skeleton_custom_message(self):
        """Test loading skeleton with custom message."""
        fig = add_loading_skeleton("Custom loading...")

        assert "Custom loading..." in fig.layout.annotations[0].text


class TestDarkMode:
    """Tests for dark mode theme."""

    def test_apply_dark_mode_theme(self):
        """Test dark mode application."""
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1, 2], y=[1, 2]))
        fig_dark = apply_dark_mode_theme(fig)

        # Check dark backgrounds
        assert fig_dark.layout.plot_bgcolor == "#0F1419"
        assert fig_dark.layout.paper_bgcolor == "#1A1F26"

        # Check dark text
        assert fig_dark.layout.font.color == "#E5E7EB"

    def test_dark_mode_gridlines(self):
        """Test dark mode affects gridlines."""
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1, 2], y=[1, 2]))
        fig = add_gridlines(fig)  # Add gridlines first
        fig_dark = apply_dark_mode_theme(fig)

        # Check grid colors are updated
        assert fig_dark.layout.xaxis.gridcolor == "#374151"
        assert fig_dark.layout.yaxis.gridcolor == "#374151"


class TestPresetConfigs:
    """Tests for preset configurations."""

    def test_engineering_chart_config(self):
        """Test engineering chart preset."""
        config = ENGINEERING_CHART_CONFIG

        assert config["displayModeBar"] is True
        assert config["scrollZoom"] is True
        assert config["responsive"] is True
        assert config["toImageButtonOptions"]["format"] == "png"
        assert config["toImageButtonOptions"]["scale"] == 2

    def test_presentation_chart_config(self):
        """Test presentation chart preset."""
        config = PRESENTATION_CHART_CONFIG

        assert config["displayModeBar"] is False
        assert config["staticPlot"] is False
        assert config["responsive"] is True

    def test_print_chart_config(self):
        """Test print chart preset."""
        config = PRINT_CHART_CONFIG

        assert config["toImageButtonOptions"]["format"] == "svg"
        assert config["staticPlot"] is True


class TestIntegration:
    """Integration tests combining multiple enhancements."""

    def test_full_enhancement_pipeline(self):
        """Test applying multiple enhancements together."""
        # Create base figure
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1, 2, 3], y=[1, 4, 2], mode="lines+markers"))

        # Apply enhancements
        fig = add_gridlines(fig)
        fig = add_responsive_layout(fig, height_px=500)
        fig = add_animation_config(fig, duration_ms=400)
        fig, config = add_export_config(fig, filename="test_chart")

        # Verify all enhancements applied
        assert fig.layout.height == 500
        assert fig.layout.transition.duration == 400
        assert fig.layout.xaxis.showgrid is True
        assert config["toImageButtonOptions"]["filename"] == "test_chart"

    def test_dark_mode_with_annotations(self):
        """Test dark mode with annotations."""
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1, 2], y=[1, 2]))

        annotations = [{"text": "Test", "x": 1, "y": 1}]
        fig = add_annotations_layer(fig, annotations)
        fig = apply_dark_mode_theme(fig)

        # Both should work together
        assert len(fig.layout.annotations) == 1
        assert fig.layout.plot_bgcolor == "#0F1419"
