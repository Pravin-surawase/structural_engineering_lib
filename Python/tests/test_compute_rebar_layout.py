# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for the unified compute_rebar_layout function.

This function combines bar selection, position computation, and
stirrup layout into a single call for visualization.
"""

from __future__ import annotations

import pytest

from structural_lib.visualization.geometry_3d import (
    RebarLayoutResult,
    compute_rebar_layout,
)


class TestRebarLayoutResult:
    """Tests for RebarLayoutResult dataclass."""

    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = RebarLayoutResult(
            bottom_bars=[(0, -96, 52), (0, 0, 52), (0, 96, 52)],
            top_bars=[(0, -96, 398), (0, 96, 398)],
            stirrup_positions=[50, 150, 250],
            bar_diameter=16,
            bar_count=3,
            stirrup_diameter=8,
            summary="3T16 (603 mm²)",
            spacing_summary="Stirrups: Ø8@150mm (ends), @200mm (mid)",
            ast_provided_mm2=603.3,
            ast_required_mm2=500.0,
        )
        d = result.to_dict()
        assert len(d["bottom_bars"]) == 3
        assert d["bar_diameter"] == 16
        assert d["bar_count"] == 3


class TestComputeRebarLayout:
    """Tests for compute_rebar_layout function."""

    def test_basic_layout(self):
        """Test basic rebar layout computation."""
        result = compute_rebar_layout(
            ast_mm2=500,
            b_mm=300,
            D_mm=450,
            span_mm=4000,
        )
        assert isinstance(result, RebarLayoutResult)
        assert result.bar_count >= 2
        assert result.bar_diameter in [12, 16, 20, 25, 32]
        assert len(result.bottom_bars) == result.bar_count
        assert len(result.top_bars) == 2  # Nominal top bars
        assert len(result.stirrup_positions) > 0

    def test_minimum_two_bars(self):
        """Test minimum 2 bars even for low steel area."""
        result = compute_rebar_layout(
            ast_mm2=50,  # Very low
            b_mm=300,
            D_mm=450,
            span_mm=4000,
        )
        assert result.bar_count >= 2

    def test_ast_provided_exceeds_required(self):
        """Test that provided steel >= required steel."""
        result = compute_rebar_layout(
            ast_mm2=750,
            b_mm=300,
            D_mm=450,
            span_mm=4000,
        )
        assert result.ast_provided_mm2 >= result.ast_required_mm2

    def test_bottom_bar_positions_symmetric(self):
        """Test that bar positions are symmetric about center."""
        result = compute_rebar_layout(
            ast_mm2=600,
            b_mm=300,
            D_mm=450,
            span_mm=4000,
        )
        y_positions = [bar[1] for bar in result.bottom_bars]
        # Check symmetry: sum should be near zero
        assert abs(sum(y_positions)) < 1.0  # Tolerance

    def test_z_coordinate_bottom_bars(self):
        """Test Z coordinate is near soffit."""
        result = compute_rebar_layout(
            ast_mm2=600,
            b_mm=300,
            D_mm=450,
            span_mm=4000,
            cover_mm=40,
            stirrup_dia=8,
        )
        # Z should be about cover + stirrup + bar/2
        for bar in result.bottom_bars:
            assert bar[2] > 40  # Above cover
            assert bar[2] < 100  # But near soffit

    def test_z_coordinate_top_bars(self):
        """Test Z coordinate is near top."""
        result = compute_rebar_layout(
            ast_mm2=600,
            b_mm=300,
            D_mm=450,
            span_mm=4000,
        )
        for bar in result.top_bars:
            assert bar[2] > 350  # Near top
            assert bar[2] < 450  # But within beam

    def test_stirrup_positions_cover_span(self):
        """Test stirrups are distributed along span."""
        result = compute_rebar_layout(
            ast_mm2=600,
            b_mm=300,
            D_mm=450,
            span_mm=4000,
        )
        positions = result.stirrup_positions
        assert positions[0] > 0  # Not at face
        assert positions[-1] < 4000  # Not beyond span
        assert all(positions[i] < positions[i + 1] for i in range(len(positions) - 1))

    def test_high_shear_reduces_spacing(self):
        """Test that high shear force reduces stirrup spacing."""
        result_low_shear = compute_rebar_layout(
            ast_mm2=600,
            b_mm=300,
            D_mm=450,
            span_mm=4000,
            vu_kn=30,
        )
        result_high_shear = compute_rebar_layout(
            ast_mm2=600,
            b_mm=300,
            D_mm=450,
            span_mm=4000,
            vu_kn=150,
        )
        # High shear should have more stirrups (closer spacing)
        assert len(result_high_shear.stirrup_positions) >= len(
            result_low_shear.stirrup_positions
        )

    def test_summary_format(self):
        """Test summary string format."""
        result = compute_rebar_layout(
            ast_mm2=600,
            b_mm=300,
            D_mm=450,
            span_mm=4000,
        )
        # Should be in format "NTdia (area mm²)"
        assert "T" in result.summary
        assert "mm²" in result.summary

    def test_spacing_summary_format(self):
        """Test spacing summary includes stirrup info."""
        result = compute_rebar_layout(
            ast_mm2=600,
            b_mm=300,
            D_mm=450,
            span_mm=4000,
        )
        assert "Stirrups" in result.spacing_summary
        assert "mm" in result.spacing_summary

    def test_larger_beam_more_steel(self):
        """Test larger steel area results in more bars or larger dia."""
        result_small = compute_rebar_layout(
            ast_mm2=400, b_mm=300, D_mm=450, span_mm=4000
        )
        result_large = compute_rebar_layout(
            ast_mm2=1500, b_mm=300, D_mm=450, span_mm=4000
        )
        assert result_large.ast_provided_mm2 > result_small.ast_provided_mm2

    def test_narrow_beam_fewer_bars(self):
        """Test narrow beam uses fewer bars per layer."""
        result = compute_rebar_layout(
            ast_mm2=800,
            b_mm=200,  # Narrow
            D_mm=450,
            span_mm=4000,
        )
        assert result.bar_count >= 2  # Still minimum 2
        assert result.bar_count <= 6  # Prefer single layer

    def test_to_dict_roundtrip(self):
        """Test that to_dict produces valid JSON-like dict."""
        result = compute_rebar_layout(
            ast_mm2=700,
            b_mm=300,
            D_mm=450,
            span_mm=4000,
        )
        d = result.to_dict()

        # All keys should be present
        expected_keys = {
            "bottom_bars",
            "top_bars",
            "stirrup_positions",
            "bar_diameter",
            "bar_count",
            "stirrup_diameter",
            "summary",
            "spacing_summary",
            "ast_provided_mm2",
            "ast_required_mm2",
        }
        assert set(d.keys()) == expected_keys

        # Values should be JSON-serializable types
        import json

        json.dumps(d)  # Should not raise

    def test_custom_cover(self):
        """Test with custom cover value."""
        result = compute_rebar_layout(
            ast_mm2=600,
            b_mm=300,
            D_mm=450,
            span_mm=4000,
            cover_mm=50,  # Larger cover
        )
        # Z position should be higher
        for bar in result.bottom_bars:
            assert bar[2] > 50  # Above cover
