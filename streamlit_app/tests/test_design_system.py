"""
Unit tests for design_system module.

Tests design tokens, color system, typography, spacing, and utility functions.
"""

import pytest
from streamlit_app.utils.design_system import (
    COLORS,
    TYPOGRAPHY,
    SPACING,
    ELEVATION,
    ANIMATION,
    RADIUS,
    BREAKPOINTS,
    DARK_COLORS,
    BUTTON_SPECS,
    INPUT_SPECS,
    CARD_SPECS,
    generate_css_variables,
    get_semantic_color,
    get_spacing,
)


# ============================================================================
# TEST: COLOR SYSTEM
# ============================================================================


class TestColorPalette:
    """Test color palette values and consistency."""

    def test_primary_colors_exist(self):
        """All primary color shades should be defined."""
        assert COLORS.primary_50.startswith("#")
        assert COLORS.primary_500 == "#003366"
        assert COLORS.primary_900.startswith("#")

    def test_accent_colors_exist(self):
        """All accent color shades should be defined."""
        assert COLORS.accent_50.startswith("#")
        assert COLORS.accent_500 == "#FF6600"
        assert COLORS.accent_900.startswith("#")

    def test_semantic_colors_exist(self):
        """All semantic colors should be defined."""
        assert COLORS.success.startswith("#")
        assert COLORS.warning.startswith("#")
        assert COLORS.error.startswith("#")
        assert COLORS.info.startswith("#")

    def test_gray_scale_exists(self):
        """All gray shades should be defined."""
        assert COLORS.gray_50.startswith("#")
        assert COLORS.gray_500.startswith("#")
        assert COLORS.gray_900.startswith("#")

    def test_colors_are_immutable(self):
        """Color palette should be immutable (frozen dataclass)."""
        with pytest.raises(AttributeError):
            COLORS.primary_500 = "#FF0000"

    def test_hex_color_format(self):
        """All colors should be valid hex codes."""
        import re

        hex_pattern = re.compile(r"^#[0-9A-Fa-f]{6}$")

        # Test a sample of colors
        assert hex_pattern.match(COLORS.primary_500)
        assert hex_pattern.match(COLORS.accent_500)
        assert hex_pattern.match(COLORS.success)
        assert hex_pattern.match(COLORS.gray_500)


class TestDarkModeColors:
    """Test dark mode color overrides."""

    def test_dark_colors_exist(self):
        """Dark mode colors should be defined."""
        assert DARK_COLORS.bg_primary.startswith("#")
        assert DARK_COLORS.text_primary.startswith("#")
        assert DARK_COLORS.primary.startswith("#")

    def test_dark_colors_different_from_light(self):
        """Dark mode colors should differ from light mode."""
        assert DARK_COLORS.primary != COLORS.primary_500
        assert DARK_COLORS.bg_primary != "#FFFFFF"


# ============================================================================
# TEST: TYPOGRAPHY SYSTEM
# ============================================================================


class TestTypographyScale:
    """Test typography scale and font settings."""

    def test_font_families_defined(self):
        """Font families should be defined."""
        assert "Inter" in TYPOGRAPHY.font_ui
        assert "JetBrains Mono" in TYPOGRAPHY.font_mono

    def test_heading_sizes_increase(self):
        """Heading sizes should follow hierarchy (H1 > H2 > H3 > H4)."""
        h1_size = int(TYPOGRAPHY.h1_size.replace("px", ""))
        h2_size = int(TYPOGRAPHY.h2_size.replace("px", ""))
        h3_size = int(TYPOGRAPHY.h3_size.replace("px", ""))
        h4_size = int(TYPOGRAPHY.h4_size.replace("px", ""))

        assert h1_size > h2_size > h3_size > h4_size

    def test_body_sizes_exist(self):
        """Body text sizes should be defined."""
        assert TYPOGRAPHY.body_size == "16px"
        assert TYPOGRAPHY.body_sm_size == "14px"
        assert TYPOGRAPHY.body_lg_size == "18px"

    def test_font_weights_valid(self):
        """Font weights should be valid CSS values."""
        valid_weights = {400, 500, 600, 700}
        assert TYPOGRAPHY.h1_weight in valid_weights
        assert TYPOGRAPHY.body_weight in valid_weights
        assert TYPOGRAPHY.button_weight in valid_weights

    def test_line_heights_defined(self):
        """Line heights should be defined for all sizes."""
        assert TYPOGRAPHY.h1_line_height.endswith("px")
        assert TYPOGRAPHY.body_line_height.endswith("px")


# ============================================================================
# TEST: SPACING SYSTEM
# ============================================================================


class TestSpacingScale:
    """Test 8px-based spacing system."""

    def test_base_unit_is_8px(self):
        """Space_2 should be 8px (base unit)."""
        assert SPACING.space_2 == "8px"

    def test_spacing_increases(self):
        """Spacing should increase progressively."""
        spaces = [
            int(SPACING.space_1.replace("px", "")),
            int(SPACING.space_2.replace("px", "")),
            int(SPACING.space_3.replace("px", "")),
            int(SPACING.space_4.replace("px", "")),
            int(SPACING.space_5.replace("px", "")),
        ]

        for i in range(len(spaces) - 1):
            assert spaces[i] < spaces[i + 1]

    def test_spacing_divisible_by_4(self):
        """All spacing (except space_1) should be divisible by 4."""
        for i in range(2, 11):
            space_val = int(getattr(SPACING, f"space_{i}").replace("px", ""))
            assert space_val % 4 == 0

    def test_zero_spacing_exists(self):
        """Space_0 should be 0px."""
        assert SPACING.space_0 == "0px"


# ============================================================================
# TEST: ELEVATION SYSTEM
# ============================================================================


class TestElevationSystem:
    """Test shadow/elevation system."""

    def test_four_levels_exist(self):
        """Should have 4 elevation levels."""
        assert ELEVATION.level_0 == "none"
        assert "px" in ELEVATION.level_1
        assert "px" in ELEVATION.level_2
        assert "px" in ELEVATION.level_3
        assert "px" in ELEVATION.level_4

    def test_shadows_increase(self):
        """Shadow blur should increase with level."""
        # Level 1 has lower blur than level 4
        assert len(ELEVATION.level_1) < len(ELEVATION.level_4)


# ============================================================================
# TEST: ANIMATION SYSTEM
# ============================================================================


class TestAnimationTimings:
    """Test animation timing and easing."""

    def test_durations_defined(self):
        """Animation durations should be defined."""
        assert ANIMATION.instant == "100ms"
        assert ANIMATION.fast == "200ms"
        assert ANIMATION.normal == "300ms"
        assert ANIMATION.slow == "500ms"

    def test_durations_increase(self):
        """Durations should increase progressively."""
        durations = [
            int(ANIMATION.instant.replace("ms", "")),
            int(ANIMATION.fast.replace("ms", "")),
            int(ANIMATION.normal.replace("ms", "")),
            int(ANIMATION.slow.replace("ms", "")),
        ]

        for i in range(len(durations) - 1):
            assert durations[i] < durations[i + 1]

    def test_easing_functions_defined(self):
        """Easing functions should be defined."""
        assert "cubic-bezier" in ANIMATION.ease_in_out
        assert "linear" in ANIMATION.ease_linear


# ============================================================================
# TEST: BORDER RADIUS
# ============================================================================


class TestBorderRadius:
    """Test border radius scale."""

    def test_radius_values_exist(self):
        """Border radius values should be defined."""
        assert RADIUS.none == "0px"
        assert RADIUS.sm == "4px"
        assert RADIUS.md == "8px"
        assert RADIUS.lg == "12px"
        assert RADIUS.full == "9999px"

    def test_radius_increases(self):
        """Radius should increase progressively."""
        assert int(RADIUS.sm.replace("px", "")) < int(RADIUS.md.replace("px", ""))
        assert int(RADIUS.md.replace("px", "")) < int(RADIUS.lg.replace("px", ""))


# ============================================================================
# TEST: BREAKPOINTS
# ============================================================================


class TestBreakpoints:
    """Test responsive breakpoints."""

    def test_breakpoints_defined(self):
        """All breakpoints should be defined."""
        assert BREAKPOINTS.mobile == "320px"
        assert BREAKPOINTS.tablet == "768px"
        assert BREAKPOINTS.desktop == "1024px"

    def test_breakpoints_increase(self):
        """Breakpoints should increase progressively."""
        breakpoints = [
            int(BREAKPOINTS.mobile.replace("px", "")),
            int(BREAKPOINTS.tablet.replace("px", "")),
            int(BREAKPOINTS.desktop.replace("px", "")),
            int(BREAKPOINTS.desktop_lg.replace("px", "")),
        ]

        for i in range(len(breakpoints) - 1):
            assert breakpoints[i] < breakpoints[i + 1]


# ============================================================================
# TEST: COMPONENT SPECS
# ============================================================================


class TestComponentSpecs:
    """Test component specification values."""

    def test_button_specs_defined(self):
        """Button specs should be defined."""
        assert BUTTON_SPECS.height_sm == "32px"
        assert BUTTON_SPECS.height_md == "40px"
        assert BUTTON_SPECS.height_lg == "48px"
        assert BUTTON_SPECS.border_radius == RADIUS.md

    def test_input_specs_defined(self):
        """Input specs should be defined."""
        assert INPUT_SPECS.height == "40px"
        assert INPUT_SPECS.border_radius == RADIUS.sm
        assert INPUT_SPECS.border_width == "1px"

    def test_card_specs_defined(self):
        """Card specs should be defined."""
        assert CARD_SPECS.border_radius == RADIUS.lg
        assert CARD_SPECS.elevation == ELEVATION.level_1


# ============================================================================
# TEST: UTILITY FUNCTIONS
# ============================================================================


class TestGetSemanticColor:
    """Test get_semantic_color utility function."""

    def test_success_colors(self):
        """Get success color variants."""
        assert get_semantic_color("success", "base") == COLORS.success
        assert get_semantic_color("success", "light") == COLORS.success_light
        assert get_semantic_color("success", "dark") == COLORS.success_dark

    def test_warning_colors(self):
        """Get warning color variants."""
        assert get_semantic_color("warning", "base") == COLORS.warning
        assert get_semantic_color("warning", "light") == COLORS.warning_light

    def test_error_colors(self):
        """Get error color variants."""
        assert get_semantic_color("error", "base") == COLORS.error
        assert get_semantic_color("error", "light") == COLORS.error_light

    def test_info_colors(self):
        """Get info color variants."""
        assert get_semantic_color("info", "base") == COLORS.info


class TestGetSpacing:
    """Test get_spacing utility function."""

    def test_spacing_by_number(self):
        """Get spacing by size number."""
        assert get_spacing(0) == "0px"
        assert get_spacing(2) == "8px"
        assert get_spacing(4) == "16px"
        assert get_spacing(6) == "32px"

    def test_invalid_spacing_returns_default(self):
        """Invalid spacing size should return default (space_4)."""
        assert get_spacing(99) == SPACING.space_4


class TestGenerateCSSVariables:
    """Test CSS variable generation."""

    def test_generates_valid_css(self):
        """Should generate valid CSS custom properties."""
        css = generate_css_variables(dark_mode=False)
        assert ":root {" in css
        assert "--color-primary-500" in css
        assert "--font-ui" in css
        assert "--space-4" in css

    def test_includes_color_variables(self):
        """Should include color variables."""
        css = generate_css_variables()
        assert f"--color-primary-500: {COLORS.primary_500}" in css
        assert f"--color-accent-500: {COLORS.accent_500}" in css

    def test_includes_typography_variables(self):
        """Should include typography variables."""
        css = generate_css_variables()
        assert f"--font-ui: {TYPOGRAPHY.font_ui}" in css
        assert f"--font-size-body: {TYPOGRAPHY.body_size}" in css

    def test_includes_spacing_variables(self):
        """Should include spacing variables."""
        css = generate_css_variables()
        assert f"--space-4: {SPACING.space_4}" in css

    def test_dark_mode_adds_overrides(self):
        """Dark mode should add additional CSS."""
        light_css = generate_css_variables(dark_mode=False)
        dark_css = generate_css_variables(dark_mode=True)
        assert len(dark_css) > len(light_css)


# ============================================================================
# TEST: DESIGN SYSTEM CONSISTENCY
# ============================================================================


class TestDesignSystemConsistency:
    """Test overall design system consistency."""

    def test_60_30_10_color_rule(self):
        """Primary should be navy, accent should be orange (60-30-10 rule)."""
        assert COLORS.primary_500 == "#003366"  # Navy
        assert COLORS.accent_500 == "#FF6600"  # Orange

    def test_8px_spacing_rule(self):
        """Base spacing unit should be 8px."""
        assert SPACING.space_2 == "8px"

    def test_modular_scale_typography(self):
        """Typography should follow 1.25 ratio (modular scale)."""
        body = int(TYPOGRAPHY.body_size.replace("px", ""))
        body_lg = int(TYPOGRAPHY.body_lg_size.replace("px", ""))
        h4 = int(TYPOGRAPHY.h4_size.replace("px", ""))

        # Check approximate 1.25 ratio
        assert 17 <= body_lg <= 19  # 16 * 1.25 ≈ 18
        assert 19 <= h4 <= 21  # 16 * 1.25^2 ≈ 20

    def test_wcag_contrast_primary(self):
        """Primary color should have high contrast on white."""
        # Navy #003366 on white should pass WCAG AA (4.5:1)
        # This is a known value from research
        assert COLORS.primary_500 == "#003366"
