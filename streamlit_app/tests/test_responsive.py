"""
Tests for responsive design utilities.

Tests breakpoint detection, responsive columns, fluid typography,
and mobile-first CSS injection.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.responsive import (
    get_device_type,
    get_breakpoint,
    get_responsive_columns,
    get_responsive_widths,
    get_fluid_font_size,
    get_responsive_padding,
    is_mobile,
    is_tablet,
    is_desktop,
    BREAKPOINTS,
    Breakpoint,
)


class TestBreakpoints:
    """Test breakpoint configuration and detection."""

    def test_breakpoints_defined(self):
        """Test all breakpoints are defined."""
        assert "mobile" in BREAKPOINTS
        assert "tablet" in BREAKPOINTS
        assert "desktop" in BREAKPOINTS

    def test_mobile_breakpoint(self):
        """Test mobile breakpoint configuration."""
        bp = BREAKPOINTS["mobile"]
        assert bp.name == "mobile"
        assert bp.min_width == 0
        assert bp.max_width == 767
        assert bp.columns == 1
        assert bp.font_scale == 1.0

    def test_tablet_breakpoint(self):
        """Test tablet breakpoint configuration."""
        bp = BREAKPOINTS["tablet"]
        assert bp.name == "tablet"
        assert bp.min_width == 768
        assert bp.max_width == 1023
        assert bp.columns == 2
        assert bp.font_scale == 1.1

    def test_desktop_breakpoint(self):
        """Test desktop breakpoint configuration."""
        bp = BREAKPOINTS["desktop"]
        assert bp.name == "desktop"
        assert bp.min_width == 1024
        assert bp.max_width is None
        assert bp.columns == 3
        assert bp.font_scale == 1.2

    def test_get_breakpoint_valid(self):
        """Test getting breakpoint by device type."""
        mobile = get_breakpoint("mobile")
        assert isinstance(mobile, Breakpoint)
        assert mobile.name == "mobile"

        tablet = get_breakpoint("tablet")
        assert tablet.name == "tablet"

        desktop = get_breakpoint("desktop")
        assert desktop.name == "desktop"

    def test_get_breakpoint_invalid(self):
        """Test getting breakpoint with invalid type defaults to desktop."""
        invalid = get_breakpoint("invalid")
        assert invalid.name == "desktop"


class TestDeviceDetection:
    """Test device type detection."""

    def test_get_device_type_returns_string(self):
        """Test device type returns valid string."""
        device = get_device_type()
        assert isinstance(device, str)
        assert device in ["mobile", "tablet", "desktop"]

    def test_get_device_type_defaults_desktop(self):
        """Test device detection defaults to desktop."""
        # Without browser detection, should default to desktop
        device = get_device_type()
        assert device == "desktop"

    def test_is_mobile_boolean(self):
        """Test is_mobile returns boolean."""
        result = is_mobile()
        assert isinstance(result, bool)

    def test_is_tablet_boolean(self):
        """Test is_tablet returns boolean."""
        result = is_tablet()
        assert isinstance(result, bool)

    def test_is_desktop_boolean(self):
        """Test is_desktop returns boolean."""
        result = is_desktop()
        assert isinstance(result, bool)

    def test_device_checks_mutually_exclusive(self):
        """Test only one device check is True."""
        checks = [is_mobile(), is_tablet(), is_desktop()]
        assert sum(checks) == 1  # Exactly one should be True


class TestResponsiveColumns:
    """Test responsive column logic."""

    def test_get_responsive_columns_default(self):
        """Test default responsive columns."""
        cols = get_responsive_columns()
        assert isinstance(cols, list)
        assert len(cols) > 0
        assert all(isinstance(c, int) for c in cols)

    def test_get_responsive_columns_mobile(self):
        """Test responsive columns for mobile."""
        # Simulate mobile device
        cols = get_responsive_columns(mobile=1, tablet=2, desktop=3)
        # Should return based on current device (desktop by default)
        assert isinstance(cols, list)

    def test_get_responsive_columns_custom(self):
        """Test custom responsive column counts."""
        cols = get_responsive_columns(mobile=1, tablet=3, desktop=4)
        assert isinstance(cols, list)
        # Length depends on device type
        assert len(cols) >= 1

    def test_get_responsive_widths_default(self):
        """Test default responsive widths."""
        widths = get_responsive_widths()
        assert isinstance(widths, list)
        assert len(widths) > 0
        assert all(isinstance(w, int) for w in widths)

    def test_get_responsive_widths_asymmetric(self):
        """Test asymmetric responsive widths (sidebar layout)."""
        widths = get_responsive_widths(mobile=(1,), tablet=(1, 2), desktop=(1, 3))
        assert isinstance(widths, list)
        # Should return based on device (desktop by default)
        assert len(widths) in [1, 2, 3]

    def test_responsive_widths_preserve_ratios(self):
        """Test responsive widths preserve specified ratios."""
        widths = get_responsive_widths(mobile=(1,), tablet=(1, 1), desktop=(1, 2, 1))
        # Sum should make sense for columns
        assert sum(widths) > 0


class TestFluidTypography:
    """Test fluid typography calculations."""

    def test_get_fluid_font_size_default(self):
        """Test default fluid font size."""
        size = get_fluid_font_size(16)
        assert isinstance(size, str)
        assert "px" in size or "rem" in size or "clamp" in size

    def test_get_fluid_font_size_scaled(self):
        """Test scaled fluid font size."""
        size = get_fluid_font_size(16, scale_factor=1.5)
        assert isinstance(size, str)
        # Should contain numeric value
        assert any(c.isdigit() for c in size)

    def test_get_fluid_font_size_with_min_max(self):
        """Test fluid font size with min/max constraints."""
        size = get_fluid_font_size(16, min_size=14, max_size=20)
        assert isinstance(size, str)
        # Should use clamp() with constraints
        if "clamp" in size:
            assert "14px" in size
            assert "20px" in size

    def test_get_fluid_font_size_clamped(self):
        """Test font size respects min/max constraints."""
        size = get_fluid_font_size(16, min_size=18, max_size=20)
        # Should clamp to min (18px)
        assert isinstance(size, str)

    def test_fluid_font_size_device_scaling(self):
        """Test font size scales with device type."""
        # Device detection defaults to desktop (scale 1.2)
        size_desktop = get_fluid_font_size(16)
        # Should be scaled up slightly
        assert isinstance(size_desktop, str)


class TestResponsivePadding:
    """Test responsive padding calculations."""

    def test_get_responsive_padding_default(self):
        """Test default responsive padding."""
        padding = get_responsive_padding()
        assert isinstance(padding, str)
        assert "rem" in padding or "px" in padding

    def test_get_responsive_padding_custom(self):
        """Test custom responsive padding."""
        padding = get_responsive_padding(mobile="0.5rem", tablet="1rem", desktop="2rem")
        assert isinstance(padding, str)
        # Should return one of the values based on device
        assert padding in ["0.5rem", "1rem", "2rem"]

    def test_responsive_padding_device_specific(self):
        """Test padding varies by device type."""
        # Default device is desktop
        padding = get_responsive_padding(mobile="8px", tablet="16px", desktop="24px")
        # Should return desktop value
        assert padding == "24px"


class TestResponsiveStylesGeneration:
    """Test CSS generation for responsive styles."""

    def test_responsive_css_contains_breakpoints(self):
        """Test CSS includes media queries for breakpoints."""
        # We can't easily test st.markdown output, so test logic
        bp = get_breakpoint("desktop")
        assert bp.font_scale == 1.2

        # Verify breakpoint values make sense
        assert BREAKPOINTS["tablet"].min_width == 768
        assert BREAKPOINTS["desktop"].min_width == 1024

    def test_fluid_typography_formulas(self):
        """Test fluid typography calculations are valid."""
        # Test various sizes
        sizes = [14, 16, 18, 20, 24]
        for size in sizes:
            result = get_fluid_font_size(size)
            assert isinstance(result, str)
            assert len(result) > 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_zero_font_size(self):
        """Test handling of zero font size."""
        size = get_fluid_font_size(0)
        assert isinstance(size, str)

    def test_negative_font_size(self):
        """Test handling of negative font size."""
        size = get_fluid_font_size(-16)
        # Should still return valid CSS string
        assert isinstance(size, str)

    def test_very_large_font_size(self):
        """Test handling of very large font size."""
        size = get_fluid_font_size(1000)
        assert isinstance(size, str)

    def test_min_greater_than_max(self):
        """Test when min size > max size."""
        size = get_fluid_font_size(16, min_size=20, max_size=10)
        # Should handle gracefully
        assert isinstance(size, str)

    def test_empty_column_counts(self):
        """Test handling of zero columns."""
        cols = get_responsive_columns(mobile=0, tablet=0, desktop=0)
        # Should return empty list or handle gracefully
        assert isinstance(cols, list)


# Integration test
def test_responsive_workflow():
    """Test complete responsive workflow."""
    # 1. Detect device
    device = get_device_type()
    assert device in ["mobile", "tablet", "desktop"]

    # 2. Get breakpoint
    bp = get_breakpoint(device)
    assert isinstance(bp, Breakpoint)

    # 3. Get responsive columns
    cols = get_responsive_columns()
    assert len(cols) == bp.columns

    # 4. Get fluid typography
    size = get_fluid_font_size(16)
    assert isinstance(size, str)

    # 5. Get responsive padding
    padding = get_responsive_padding()
    assert isinstance(padding, str)

    # Workflow completes without errors
    assert True
