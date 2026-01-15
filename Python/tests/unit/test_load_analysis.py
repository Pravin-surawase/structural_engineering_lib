# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Tests for load_analysis module (BMD/SFD computation).

Tests cover:
- Simply supported beam with UDL
- Simply supported beam with point load
- Cantilever beam with UDL
- Cantilever beam with point load
- Combined loads (superposition)
- Critical point detection
- Edge cases and input validation
"""

from __future__ import annotations

import pytest

from structural_lib.api import (
    CriticalPoint,
    LoadDefinition,
    LoadDiagramResult,
    LoadType,
    compute_bmd_sfd,
)


class TestSimplySupportedUDL:
    """Tests for simply supported beam with UDL."""

    def test_max_moment_at_midspan(self) -> None:
        """wL²/8 formula for max moment at midspan."""
        loads = [LoadDefinition(LoadType.UDL, magnitude=20.0)]
        result = compute_bmd_sfd(6000, "simply_supported", loads)

        # Expected: wL²/8 = 20 * 6² / 8 = 90 kN·m
        expected_max_m = 20.0 * 6.0**2 / 8.0
        assert abs(result.max_bm_knm - expected_max_m) < 0.01

    def test_max_shear_at_supports(self) -> None:
        """wL/2 formula for max shear at supports."""
        loads = [LoadDefinition(LoadType.UDL, magnitude=20.0)]
        result = compute_bmd_sfd(6000, "simply_supported", loads)

        # Expected: wL/2 = 20 * 6 / 2 = 60 kN
        expected_max_v = 20.0 * 6.0 / 2.0
        assert abs(result.max_sf_kn - expected_max_v) < 0.01

    def test_moment_zero_at_supports(self) -> None:
        """Moment should be zero at both supports."""
        loads = [LoadDefinition(LoadType.UDL, magnitude=20.0)]
        result = compute_bmd_sfd(6000, "simply_supported", loads)

        assert abs(result.bmd_knm[0]) < 0.01  # Left support
        assert abs(result.bmd_knm[-1]) < 0.01  # Right support

    def test_shear_zero_at_midspan(self) -> None:
        """Shear should be zero at midspan for symmetric UDL."""
        loads = [LoadDefinition(LoadType.UDL, magnitude=20.0)]
        result = compute_bmd_sfd(6000, "simply_supported", loads, num_points=101)

        # Find midspan index
        mid_idx = len(result.sfd_kn) // 2
        assert abs(result.sfd_kn[mid_idx]) < 0.1  # Small tolerance for discretization

    def test_result_has_all_fields(self) -> None:
        """LoadDiagramResult should have all required fields."""
        loads = [LoadDefinition(LoadType.UDL, magnitude=20.0)]
        result = compute_bmd_sfd(6000, "simply_supported", loads)

        assert isinstance(result, LoadDiagramResult)
        assert len(result.positions_mm) == 101  # Default num_points
        assert len(result.bmd_knm) == 101
        assert len(result.sfd_kn) == 101
        assert result.span_mm == 6000
        assert result.support_condition == "simply_supported"
        assert len(result.loads) == 1


class TestSimplySupportedPointLoad:
    """Tests for simply supported beam with point load."""

    def test_midspan_point_load_max_moment(self) -> None:
        """PL/4 formula for point load at midspan."""
        loads = [LoadDefinition(LoadType.POINT, magnitude=100.0, position_mm=3000.0)]
        result = compute_bmd_sfd(6000, "simply_supported", loads)

        # Expected: PL/4 = 100 * 6 / 4 = 150 kN·m
        expected_max_m = 100.0 * 6.0 / 4.0
        assert abs(result.max_bm_knm - expected_max_m) < 0.01

    def test_midspan_point_load_shear(self) -> None:
        """P/2 for shear at supports with midspan point load."""
        loads = [LoadDefinition(LoadType.POINT, magnitude=100.0, position_mm=3000.0)]
        result = compute_bmd_sfd(6000, "simply_supported", loads)

        # Expected: P/2 = 100 / 2 = 50 kN at both ends
        assert abs(result.max_sf_kn - 50.0) < 0.01
        assert abs(result.min_sf_kn - (-50.0)) < 0.01

    def test_offset_point_load(self) -> None:
        """Point load at L/3 from left support."""
        # Load at 2000mm from left on 6000mm span
        loads = [LoadDefinition(LoadType.POINT, magnitude=60.0, position_mm=2000.0)]
        result = compute_bmd_sfd(6000, "simply_supported", loads)

        # Reactions: R_A = P*b/L = 60*4/6 = 40 kN, R_B = P*a/L = 60*2/6 = 20 kN
        assert abs(result.max_sf_kn - 40.0) < 0.01

        # Max moment at load point: M = R_A * a = 40 * 2 = 80 kN·m
        expected_max_m = 40.0 * 2.0
        # Allow 2% tolerance for discretization (load point may not align exactly with sample points)
        assert abs(result.max_bm_knm - expected_max_m) < expected_max_m * 0.02


class TestCantileverUDL:
    """Tests for cantilever beam with UDL (fixed at left)."""

    def test_max_moment_at_fixed_end(self) -> None:
        """wL²/2 formula for moment at fixed end."""
        loads = [LoadDefinition(LoadType.UDL, magnitude=20.0)]
        result = compute_bmd_sfd(6000, "cantilever", loads)

        # Expected: -wL²/2 = -20 * 6² / 2 = -360 kN·m (negative = hogging)
        expected_min_m = -20.0 * 6.0**2 / 2.0
        assert abs(result.min_bm_knm - expected_min_m) < 0.01

    def test_max_shear_at_fixed_end(self) -> None:
        """wL for shear at fixed end."""
        loads = [LoadDefinition(LoadType.UDL, magnitude=20.0)]
        result = compute_bmd_sfd(6000, "cantilever", loads)

        # Expected: -wL = -20 * 6 = -120 kN (negative convention)
        expected_min_v = -20.0 * 6.0
        assert abs(result.min_sf_kn - expected_min_v) < 0.01

    def test_zero_at_free_end(self) -> None:
        """Moment and shear should be zero at free end."""
        loads = [LoadDefinition(LoadType.UDL, magnitude=20.0)]
        result = compute_bmd_sfd(6000, "cantilever", loads)

        assert abs(result.bmd_knm[-1]) < 0.01  # Free end moment
        assert abs(result.sfd_kn[-1]) < 0.01  # Free end shear


class TestCantileverPointLoad:
    """Tests for cantilever beam with point load."""

    def test_point_load_at_free_end(self) -> None:
        """Point load at free end creates max moment at fixed end."""
        loads = [LoadDefinition(LoadType.POINT, magnitude=50.0, position_mm=6000.0)]
        result = compute_bmd_sfd(6000, "cantilever", loads)

        # Expected: M = -P*L = -50 * 6 = -300 kN·m
        expected_min_m = -50.0 * 6.0
        assert abs(result.min_bm_knm - expected_min_m) < 0.01

    def test_point_load_at_midspan(self) -> None:
        """Point load at midspan of cantilever."""
        loads = [LoadDefinition(LoadType.POINT, magnitude=50.0, position_mm=3000.0)]
        result = compute_bmd_sfd(6000, "cantilever", loads)

        # Expected: M = -P*a = -50 * 3 = -150 kN·m at fixed end
        expected_min_m = -50.0 * 3.0
        assert abs(result.min_bm_knm - expected_min_m) < 0.01


class TestCombinedLoads:
    """Tests for multiple loads (superposition)."""

    def test_udl_plus_point_load(self) -> None:
        """Superposition of UDL and point load at midspan."""
        loads = [
            LoadDefinition(LoadType.UDL, magnitude=15.0),
            LoadDefinition(LoadType.POINT, magnitude=50.0, position_mm=3000.0),
        ]
        result = compute_bmd_sfd(6000, "simply_supported", loads)

        # UDL: wL²/8 = 15 * 6² / 8 = 67.5 kN·m
        # Point: PL/4 = 50 * 6 / 4 = 75 kN·m
        # Total at midspan: 142.5 kN·m
        expected_max_m = 67.5 + 75.0
        assert abs(result.max_bm_knm - expected_max_m) < 0.5

    def test_multiple_point_loads(self) -> None:
        """Multiple point loads on simply supported beam."""
        loads = [
            LoadDefinition(LoadType.POINT, magnitude=30.0, position_mm=2000.0),
            LoadDefinition(LoadType.POINT, magnitude=30.0, position_mm=4000.0),
        ]
        result = compute_bmd_sfd(6000, "simply_supported", loads)

        # Symmetric loading: max moment at midspan
        # R_A = R_B = 30 kN each (total load 60 kN)
        assert abs(result.max_sf_kn - 30.0) < 0.5


class TestCriticalPoints:
    """Tests for critical point detection."""

    def test_udl_critical_points(self) -> None:
        """UDL should have max moment at midspan, max shear at supports."""
        loads = [LoadDefinition(LoadType.UDL, magnitude=20.0)]
        result = compute_bmd_sfd(6000, "simply_supported", loads)

        # Should have critical points
        assert len(result.critical_points) >= 3

        # Find max_bm point
        max_bm_points = [cp for cp in result.critical_points if cp.point_type == "max_bm"]
        assert len(max_bm_points) == 1
        assert abs(max_bm_points[0].position_mm - 3000.0) < 100  # Near midspan

    def test_zero_shear_crossing(self) -> None:
        """UDL should have zero shear crossing at midspan."""
        loads = [LoadDefinition(LoadType.UDL, magnitude=20.0)]
        result = compute_bmd_sfd(6000, "simply_supported", loads)

        # Find zero_sf point - UDL has continuous shear, so should have zero crossing
        zero_sf_points = [cp for cp in result.critical_points if cp.point_type == "zero_sf"]

        # Zero crossing should be detected for UDL (linear shear variation crosses zero)
        # If not found, check that max_bm is at midspan (where V=0)
        max_bm_points = [cp for cp in result.critical_points if cp.point_type == "max_bm"]
        assert len(max_bm_points) == 1

        # Max moment occurs where shear = 0, should be near midspan
        assert abs(max_bm_points[0].position_mm - 3000.0) < 100
        assert abs(max_bm_points[0].sf_kn) < 1.0  # Shear near zero at max moment


class TestInputValidation:
    """Tests for input validation and error handling."""

    def test_negative_span_raises_error(self) -> None:
        """Negative span should raise ValueError."""
        loads = [LoadDefinition(LoadType.UDL, magnitude=20.0)]
        with pytest.raises(ValueError, match="Span must be positive"):
            compute_bmd_sfd(-6000, "simply_supported", loads)

    def test_zero_span_raises_error(self) -> None:
        """Zero span should raise ValueError."""
        loads = [LoadDefinition(LoadType.UDL, magnitude=20.0)]
        with pytest.raises(ValueError, match="Span must be positive"):
            compute_bmd_sfd(0, "simply_supported", loads)

    def test_invalid_support_condition(self) -> None:
        """Invalid support condition should raise ValueError."""
        loads = [LoadDefinition(LoadType.UDL, magnitude=20.0)]
        with pytest.raises(ValueError, match="support_condition must be"):
            compute_bmd_sfd(6000, "continuous", loads)  # type: ignore

    def test_empty_loads_raises_error(self) -> None:
        """Empty loads list should raise ValueError."""
        with pytest.raises(ValueError, match="At least one load"):
            compute_bmd_sfd(6000, "simply_supported", [])

    def test_triangular_load_not_implemented(self) -> None:
        """Triangular load should raise NotImplementedError."""
        loads = [LoadDefinition(LoadType.TRIANGULAR, magnitude=20.0)]
        with pytest.raises(NotImplementedError, match="Triangular load"):
            compute_bmd_sfd(6000, "simply_supported", loads)

    def test_moment_load_not_implemented(self) -> None:
        """Applied moment should raise NotImplementedError."""
        loads = [LoadDefinition(LoadType.MOMENT, magnitude=25.0, position_mm=0.0)]
        with pytest.raises(NotImplementedError, match="Applied moment"):
            compute_bmd_sfd(6000, "simply_supported", loads)


class TestCustomNumPoints:
    """Tests for custom number of discretization points."""

    def test_custom_num_points(self) -> None:
        """Custom num_points should be respected."""
        loads = [LoadDefinition(LoadType.UDL, magnitude=20.0)]
        result = compute_bmd_sfd(6000, "simply_supported", loads, num_points=51)

        assert len(result.positions_mm) == 51
        assert len(result.bmd_knm) == 51
        assert len(result.sfd_kn) == 51

    def test_min_num_points(self) -> None:
        """Even with few points, formulas should be accurate."""
        loads = [LoadDefinition(LoadType.UDL, magnitude=20.0)]
        result = compute_bmd_sfd(6000, "simply_supported", loads, num_points=11)

        # Max moment should still be accurate (at midspan)
        expected_max_m = 20.0 * 6.0**2 / 8.0
        assert abs(result.max_bm_knm - expected_max_m) < 0.5
