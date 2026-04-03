# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for multi-layer rebar data types (RebarLayer, RebarArrangement).

Fix 3: Multi-layer rebar support in core/data_types.py.
"""

from __future__ import annotations

import math

import pytest

from structural_lib.codes.is456.beam.flexure import calculate_effective_depth_multilayer
from structural_lib.core.data_types import RebarArrangement, RebarLayer

# =============================================================================
# RebarLayer Tests
# =============================================================================


class TestRebarLayer:
    """Tests for RebarLayer dataclass."""

    def test_rebar_layer_area(self) -> None:
        """Test area calculation for a single layer."""
        layer = RebarLayer(bar_dia_mm=20, count=4, distance_from_bottom_mm=60)
        expected = 4 * math.pi / 4 * 20**2  # 1256.64
        assert abs(layer.area_mm2 - expected) < 0.01

    def test_rebar_layer_invalid_dia(self) -> None:
        """Negative bar diameter must raise ValueError."""
        with pytest.raises(ValueError):
            RebarLayer(bar_dia_mm=-5, count=2, distance_from_bottom_mm=60)

    def test_rebar_layer_invalid_count(self) -> None:
        """Zero bar count must raise ValueError."""
        with pytest.raises(ValueError):
            RebarLayer(bar_dia_mm=20, count=0, distance_from_bottom_mm=60)

    def test_rebar_layer_negative_distance(self) -> None:
        """Negative distance must raise ValueError."""
        with pytest.raises(ValueError):
            RebarLayer(bar_dia_mm=20, count=2, distance_from_bottom_mm=-10)


# =============================================================================
# RebarArrangement Tests
# =============================================================================


class TestRebarArrangement:
    """Tests for RebarArrangement dataclass."""

    def test_single_layer(self) -> None:
        """Single-layer arrangement centroid equals layer distance."""
        layer = RebarLayer(bar_dia_mm=20, count=4, distance_from_bottom_mm=60)
        arr = RebarArrangement(layers=(layer,))
        assert arr.centroid_from_bottom_mm == pytest.approx(60.0)
        assert arr.layer_count == 1

    def test_two_layers_equal_bars(self) -> None:
        """Two-layer arrangement with same bar sizes."""
        l1 = RebarLayer(bar_dia_mm=20, count=4, distance_from_bottom_mm=60)
        l2 = RebarLayer(bar_dia_mm=20, count=2, distance_from_bottom_mm=110)
        arr = RebarArrangement(layers=(l1, l2))
        # Weighted: (4*314.16*60 + 2*314.16*110) / (4*314.16 + 2*314.16)
        # = (75398.4 + 69115.2) / (1256.64 + 628.32) = 144513.6 / 1884.96 = 76.67
        assert abs(arr.centroid_from_bottom_mm - 76.67) < 0.1
        assert abs(arr.effective_depth(500) - 423.33) < 0.1

    def test_mixed_bar_sizes(self) -> None:
        """Two-layer arrangement with different bar diameters."""
        l1 = RebarLayer(bar_dia_mm=25, count=3, distance_from_bottom_mm=65)
        l2 = RebarLayer(bar_dia_mm=16, count=2, distance_from_bottom_mm=115)
        arr = RebarArrangement(layers=(l1, l2))
        assert arr.layer_count == 2
        d = arr.effective_depth(500)
        assert 420 < d < 430  # Should be ~424.3mm

    def test_empty_raises(self) -> None:
        """Empty layers tuple must raise ValueError."""
        with pytest.raises(ValueError, match="At least one"):
            RebarArrangement(layers=())

    def test_total_area(self) -> None:
        """Total area is sum of all layer areas."""
        l1 = RebarLayer(bar_dia_mm=20, count=4, distance_from_bottom_mm=60)
        l2 = RebarLayer(bar_dia_mm=20, count=2, distance_from_bottom_mm=110)
        arr = RebarArrangement(layers=(l1, l2))
        expected = 6 * math.pi / 4 * 20**2
        assert abs(arr.total_area_mm2 - expected) < 0.01


# =============================================================================
# calculate_effective_depth_multilayer Tests
# =============================================================================


class TestCalculateEffectiveDepthMultilayer:
    """Tests for flexure.calculate_effective_depth_multilayer."""

    def test_single_layer(self) -> None:
        """Single layer: d = D - distance_from_bottom."""
        d = calculate_effective_depth_multilayer(500, [(20, 4, 60)])
        assert abs(d - 440.0) < 0.01

    def test_two_layers(self) -> None:
        """Two layers: weighted centroid calculation."""
        d = calculate_effective_depth_multilayer(500, [(20, 4, 60), (20, 2, 110)])
        assert abs(d - 423.33) < 0.1

    def test_empty_raises(self) -> None:
        """Empty layers list must raise ValueError."""
        with pytest.raises(ValueError):
            calculate_effective_depth_multilayer(500, [])
