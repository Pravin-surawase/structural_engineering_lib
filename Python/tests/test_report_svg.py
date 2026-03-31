# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for the SVG report generation module."""

import pytest

from structural_lib.services.report_svg import (
    _clamp,
    _fmt,
    _render_error_svg,
    _safe_float,
    render_section_svg,
    render_section_svg_from_beam,
)


class TestRenderSectionSvg:
    """Tests for render_section_svg function."""

    def test_basic_valid_section(self):
        """Valid beam produces SVG with expected elements."""
        svg = render_section_svg(b_mm=300, D_mm=500)

        assert "<svg" in svg
        assert "viewBox" in svg
        assert "<rect" in svg
        assert "b = 300 mm" in svg
        assert "D = 500 mm" in svg

    def test_invalid_zero_width(self):
        """Zero width produces error SVG."""
        svg = render_section_svg(b_mm=0, D_mm=500)

        assert "<svg" in svg
        assert "Invalid beam geometry" in svg

    def test_invalid_negative_depth(self):
        """Negative depth produces error SVG."""
        svg = render_section_svg(b_mm=300, D_mm=-100)

        assert "Invalid beam geometry" in svg

    def test_with_effective_depth(self):
        """Providing d_mm draws depth marker line."""
        svg = render_section_svg(b_mm=300, D_mm=500, d_mm=450)

        assert ">d<" in svg or "d</text>" in svg

    def test_with_compression_cover(self):
        """Providing d_dash_mm draws compression depth marker."""
        svg = render_section_svg(b_mm=300, D_mm=500, d_dash_mm=50)

        assert "d'" in svg

    def test_custom_dimensions(self):
        """Custom width/height are applied to SVG."""
        svg = render_section_svg(b_mm=300, D_mm=500, width=400, height=600)

        assert 'width="400"' in svg
        assert 'height="600"' in svg

    def test_accessibility_attributes(self):
        """SVG has role and aria-label for accessibility."""
        svg = render_section_svg(b_mm=300, D_mm=500)

        assert 'role="img"' in svg
        assert "aria-label" in svg


class TestRenderSectionSvgFromBeam:
    """Tests for render_section_svg_from_beam function."""

    def test_valid_beam_dict(self):
        """BeamGeometry-like dict produces valid SVG."""
        beam = {"b_mm": 250, "D_mm": 400, "d_mm": 350, "d_dash_mm": 40}
        svg = render_section_svg_from_beam(beam)

        assert "<svg" in svg
        assert "b = 250 mm" in svg

    def test_missing_dimensions(self):
        """Missing b_mm/D_mm produces error SVG."""
        beam = {"d_mm": 350}
        svg = render_section_svg_from_beam(beam)

        assert "Missing b_mm or D_mm" in svg

    def test_partial_beam_dict(self):
        """Beam with only b_mm and D_mm still works."""
        beam = {"b_mm": 300, "D_mm": 500}
        svg = render_section_svg_from_beam(beam)

        assert "<svg" in svg
        assert "D = 500 mm" in svg


class TestHelperFunctions:
    """Tests for internal helper functions."""

    def test_fmt_default_decimals(self):
        """_fmt formats to 1 decimal by default."""
        assert _fmt(3.14159) == "3.1"

    def test_fmt_custom_decimals(self):
        """_fmt respects custom decimal count."""
        assert _fmt(3.14159, 3) == "3.142"

    def test_safe_float_valid(self):
        """_safe_float returns float for valid input."""
        assert _safe_float(42) == 42.0
        assert _safe_float("3.14") == pytest.approx(3.14)

    def test_safe_float_invalid(self):
        """_safe_float returns None for invalid input."""
        assert _safe_float(None) is None
        assert _safe_float("abc") is None

    def test_clamp_within_range(self):
        """_clamp returns value when within range."""
        assert _clamp(5.0, 0.0, 10.0) == 5.0

    def test_clamp_below_minimum(self):
        """_clamp returns low when value is below."""
        assert _clamp(-1.0, 0.0, 10.0) == 0.0

    def test_clamp_above_maximum(self):
        """_clamp returns high when value is above."""
        assert _clamp(15.0, 0.0, 10.0) == 10.0


class TestRenderErrorSvg:
    """Tests for _render_error_svg function."""

    def test_error_svg_contains_message(self):
        """Error SVG includes the error message text."""
        svg = _render_error_svg("Something went wrong", width=300, height=400)

        assert "<svg" in svg
        assert "Something went wrong" in svg
        assert "#cc0000" in svg
