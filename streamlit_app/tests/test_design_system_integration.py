"""
Integration Tests for Design System
====================================

Comprehensive tests to ensure design tokens are correctly defined
and accessible by all components and layouts.

Purpose: Prevent AttributeError issues by verifying all expected
attributes exist before runtime.

Author: Main Agent
Created: 2026-01-08
Status: Production
"""

import pytest
from utils.design_system import (
    COLORS,
    TYPOGRAPHY,
    SPACING,
    ELEVATION,
    ANIMATION,
)


class TestColorPalette:
    """Test all color tokens are accessible."""

    def test_primary_colors(self):
        """Primary color scale (navy blue)."""
        assert COLORS.primary_50 == "#E6EDF5"
        assert COLORS.primary_500 == "#003366"
        assert COLORS.primary_900 == "#000A14"

    def test_accent_colors(self):
        """Accent color scale (orange)."""
        assert COLORS.accent_50 == "#FFF3E6"
        assert COLORS.accent_500 == "#FF6600"
        assert COLORS.accent_900 == "#331400"

    def test_semantic_colors(self):
        """Semantic status colors."""
        assert COLORS.success == "#10B981"
        assert COLORS.warning == "#F59E0B"
        assert COLORS.error == "#EF4444"
        assert COLORS.info == "#3B82F6"

    def test_gray_scale(self):
        """Neutral gray scale."""
        assert COLORS.gray_50 == "#FAFAFA"
        assert COLORS.gray_500 == "#737373"
        assert COLORS.gray_900 == "#171717"


class TestTypographyScale:
    """Test all typography tokens are accessible."""

    def test_font_families(self):
        """Font family definitions."""
        assert "Inter" in TYPOGRAPHY.font_ui
        assert "JetBrains Mono" in TYPOGRAPHY.font_mono

    def test_display_sizes(self):
        """Display/hero text."""
        assert TYPOGRAPHY.display_size == "48px"
        assert TYPOGRAPHY.display_line_height == "56px"
        assert TYPOGRAPHY.display_weight == 700

    def test_heading_sizes(self):
        """Heading hierarchy."""
        assert TYPOGRAPHY.h1_size == "36px"
        assert TYPOGRAPHY.h2_size == "28px"
        assert TYPOGRAPHY.h3_size == "24px"
        assert TYPOGRAPHY.h4_size == "20px"

    def test_body_sizes(self):
        """Body text sizes."""
        assert TYPOGRAPHY.body_lg_size == "18px"
        assert TYPOGRAPHY.body_size == "16px"
        assert TYPOGRAPHY.body_sm_size == "14px"
        assert TYPOGRAPHY.caption_size == "12px"

    def test_button_typography(self):
        """Button text."""
        assert TYPOGRAPHY.button_size == "14px"
        assert TYPOGRAPHY.button_weight == 500

    def test_semantic_aliases(self):
        """Semantic aliases for layout.py compatibility."""
        # These are CRITICAL - layout.py depends on these
        assert hasattr(TYPOGRAPHY, "display_sm")
        assert hasattr(TYPOGRAPHY, "heading_xl")
        assert hasattr(TYPOGRAPHY, "heading_lg")
        assert hasattr(TYPOGRAPHY, "heading_sm")
        assert hasattr(TYPOGRAPHY, "body_sm")

        # Verify values match
        assert TYPOGRAPHY.display_sm == "36px"
        assert TYPOGRAPHY.heading_xl == "28px"
        assert TYPOGRAPHY.heading_lg == "24px"
        assert TYPOGRAPHY.heading_sm == "20px"
        assert TYPOGRAPHY.body_sm == "14px"


class TestSpacingScale:
    """Test all spacing tokens are accessible."""

    def test_spacing_scale(self):
        """8px-based spacing system."""
        assert SPACING.space_0 == "0px"
        assert SPACING.space_1 == "4px"
        assert SPACING.space_2 == "8px"
        assert SPACING.space_3 == "12px"
        assert SPACING.space_4 == "16px"
        assert SPACING.space_5 == "24px"
        assert SPACING.space_6 == "32px"
        assert SPACING.space_7 == "40px"
        assert SPACING.space_8 == "48px"
        assert SPACING.space_9 == "64px"
        assert SPACING.space_10 == "80px"


class TestElevationSystem:
    """Test all shadow/elevation tokens are accessible."""

    def test_elevation_levels(self):
        """4-level shadow system."""
        assert ELEVATION.level_0 == "none"
        assert "rgba" in ELEVATION.level_1
        assert "rgba" in ELEVATION.level_2
        assert "rgba" in ELEVATION.level_3
        assert "rgba" in ELEVATION.level_4

    def test_shadow_aliases(self):
        """Semantic shadow aliases for layout.py compatibility."""
        # These are CRITICAL - layout.py depends on these
        assert hasattr(ELEVATION, "shadow_sm")
        assert hasattr(ELEVATION, "shadow_md")
        assert hasattr(ELEVATION, "shadow_lg")

        # Verify values match levels
        assert ELEVATION.shadow_sm == ELEVATION.level_1
        assert ELEVATION.shadow_md == ELEVATION.level_2
        assert ELEVATION.shadow_lg == ELEVATION.level_3


class TestAnimationTimings:
    """Test all animation tokens are accessible."""

    def test_durations(self):
        """Animation durations."""
        assert ANIMATION.instant == "100ms"
        assert ANIMATION.fast == "200ms"
        assert ANIMATION.normal == "300ms"
        assert ANIMATION.slow == "500ms"

    def test_easing_functions(self):
        """Easing functions."""
        assert "cubic-bezier" in ANIMATION.ease_in_out
        assert "cubic-bezier" in ANIMATION.ease_in
        assert "cubic-bezier" in ANIMATION.ease_out


class TestLayoutCompatibility:
    """Test compatibility with layout.py expectations."""

    def test_inject_modern_css_requirements(self):
        """Verify all tokens used in inject_modern_css() exist."""
        # These are referenced in layout.py inject_modern_css()

        # Colors
        assert hasattr(COLORS, "primary_500")
        assert hasattr(COLORS, "accent_500")
        assert hasattr(COLORS, "gray_900")
        assert hasattr(COLORS, "gray_600")
        assert hasattr(COLORS, "gray_50")
        assert hasattr(COLORS, "gray_200")

        # Elevation (shadows)
        assert hasattr(ELEVATION, "shadow_sm")
        assert hasattr(ELEVATION, "shadow_md")
        assert hasattr(ELEVATION, "shadow_lg")

        # Typography
        assert hasattr(TYPOGRAPHY, "font_ui")
        assert hasattr(TYPOGRAPHY, "font_mono")
        assert hasattr(TYPOGRAPHY, "display_sm")
        assert hasattr(TYPOGRAPHY, "heading_xl")
        assert hasattr(TYPOGRAPHY, "heading_lg")
        assert hasattr(TYPOGRAPHY, "body_sm")

        # Spacing
        assert hasattr(SPACING, "space_4")
        assert hasattr(SPACING, "space_5")
        assert hasattr(SPACING, "space_6")

    def test_card_component_requirements(self):
        """Verify all tokens used in card() function exist."""
        assert hasattr(ELEVATION, "level_1")
        assert hasattr(ELEVATION, "level_2")
        assert hasattr(SPACING, "space_4")
        assert hasattr(SPACING, "space_5")

    def test_section_header_requirements(self):
        """Verify all tokens used in section_header() exist."""
        assert hasattr(TYPOGRAPHY, "heading_xl")
        assert hasattr(SPACING, "space_5")

    def test_info_panel_requirements(self):
        """Verify all tokens used in info_panel() exist."""
        assert hasattr(COLORS, "info_light")
        assert hasattr(COLORS, "info")
        assert hasattr(SPACING, "space_4")


class TestImmutability:
    """Test that design tokens are immutable (frozen dataclasses)."""

    def test_colors_immutable(self):
        """COLORS should be immutable."""
        with pytest.raises(AttributeError):
            COLORS.primary_500 = "#000000"

    def test_typography_immutable(self):
        """TYPOGRAPHY should be immutable."""
        with pytest.raises(AttributeError):
            TYPOGRAPHY.body_size = "20px"

    def test_spacing_immutable(self):
        """SPACING should be immutable."""
        with pytest.raises(AttributeError):
            SPACING.space_4 = "20px"

    def test_elevation_immutable(self):
        """ELEVATION should be immutable."""
        with pytest.raises(AttributeError):
            ELEVATION.level_1 = "none"


class TestValueFormats:
    """Test that token values follow expected formats."""

    def test_color_hex_format(self):
        """Colors should be valid hex codes."""
        import re
        hex_pattern = re.compile(r'^#[0-9A-Fa-f]{6}$')

        assert hex_pattern.match(COLORS.primary_500)
        assert hex_pattern.match(COLORS.accent_500)
        assert hex_pattern.match(COLORS.gray_500)

    def test_spacing_px_format(self):
        """Spacing should end with 'px'."""
        assert SPACING.space_4.endswith("px")
        assert SPACING.space_6.endswith("px")

    def test_typography_px_format(self):
        """Typography sizes should end with 'px'."""
        assert TYPOGRAPHY.body_size.endswith("px")
        assert TYPOGRAPHY.h1_size.endswith("px")

    def test_animation_ms_format(self):
        """Animation durations should end with 'ms'."""
        assert ANIMATION.fast.endswith("ms")
        assert ANIMATION.normal.endswith("ms")


class TestRegressionPrevention:
    """Regression tests for previously discovered issues."""

    def test_issue_2026_01_08_shadow_attrs(self):
        """Regression: shadow_sm, shadow_md, shadow_lg must exist."""
        # Issue: AttributeError: 'ElevationSystem' object has no attribute 'shadow_sm'
        # Fixed: 2026-01-08 by adding semantic aliases
        assert hasattr(ELEVATION, "shadow_sm")
        assert hasattr(ELEVATION, "shadow_md")
        assert hasattr(ELEVATION, "shadow_lg")
        assert ELEVATION.shadow_sm is not None
        assert ELEVATION.shadow_md is not None
        assert ELEVATION.shadow_lg is not None

    def test_issue_2026_01_08_typography_attrs(self):
        """Regression: display_sm, heading_xl, heading_lg must exist."""
        # Issue: AttributeError: 'TypographyScale' object has no attribute 'display_sm'
        # Fixed: 2026-01-08 by adding semantic aliases
        assert hasattr(TYPOGRAPHY, "display_sm")
        assert hasattr(TYPOGRAPHY, "heading_xl")
        assert hasattr(TYPOGRAPHY, "heading_lg")
        assert hasattr(TYPOGRAPHY, "heading_sm")
        assert hasattr(TYPOGRAPHY, "body_sm")
        assert TYPOGRAPHY.display_sm is not None
        assert TYPOGRAPHY.heading_xl is not None
        assert TYPOGRAPHY.heading_lg is not None


# Test Discovery
def test_all_tokens_discoverable():
    """Ensure all design system modules are importable."""
    from utils import design_system

    assert hasattr(design_system, "COLORS")
    assert hasattr(design_system, "TYPOGRAPHY")
    assert hasattr(design_system, "SPACING")
    assert hasattr(design_system, "ELEVATION")
    assert hasattr(design_system, "ANIMATION")
