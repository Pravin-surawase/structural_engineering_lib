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

from structural_lib.codes.is456.load_analysis import (
    compute_applied_moment_bmd_sfd,
    compute_triangular_load_bmd_sfd,
)
from structural_lib.services.api import (
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
        max_bm_points = [
            cp for cp in result.critical_points if cp.point_type == "max_bm"
        ]
        assert len(max_bm_points) == 1
        assert abs(max_bm_points[0].position_mm - 3000.0) < 100  # Near midspan

    def test_zero_shear_crossing(self) -> None:
        """UDL should have zero shear crossing at midspan."""
        loads = [LoadDefinition(LoadType.UDL, magnitude=20.0)]
        result = compute_bmd_sfd(6000, "simply_supported", loads)

        # Zero crossing should be detected for UDL (linear shear variation crosses zero)
        # If not found, check that max_bm is at midspan (where V=0)
        max_bm_points = [
            cp for cp in result.critical_points if cp.point_type == "max_bm"
        ]
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

    def test_triangular_load_works(self) -> None:
        """Triangular load should compute valid results."""
        loads = [LoadDefinition(LoadType.TRIANGULAR, magnitude=20.0)]
        result = compute_bmd_sfd(6000, "simply_supported", loads)

        # w_max * L^2 / (9*sqrt(3)) ≈ 46.19 kNm
        assert result.max_bm_knm > 40.0
        assert len(result.bmd_knm) == 101

    def test_moment_load_works(self) -> None:
        """Applied moment should compute valid results."""
        loads = [LoadDefinition(LoadType.MOMENT, magnitude=25.0, position_mm=3000.0)]
        result = compute_bmd_sfd(6000, "simply_supported", loads)

        # Max |BM| = M/2 = 12.5 for midspan moment
        assert abs(result.max_bm_knm - 12.5) < 0.1
        assert len(result.bmd_knm) == 101


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


# =============================================================================
# Triangular Load Tests
# =============================================================================


class TestTriangularLoadAscending:
    """Tests for simply supported beam with ascending triangular load (0 → w_max)."""

    def test_reactions(self) -> None:
        """R_A = wL/6, R_B = wL/3 for ascending triangular load."""
        span_mm, w = 6000.0, 20.0
        span_m = span_mm / 1000.0
        pos, bmd, sfd, _ = compute_triangular_load_bmd_sfd(span_mm, w, ascending=True)

        # R_A = V(0) = wL/6
        assert abs(sfd[0] - w * span_m / 6.0) < 0.01
        # R_B = -V(L) = wL/3 → V(L) = -wL/3
        assert abs(sfd[-1] - (-w * span_m / 3.0)) < 0.01

    def test_max_moment_value(self) -> None:
        """M_max = wL^2 / (9*sqrt(3))."""
        import math

        span_mm, w = 6000.0, 20.0
        span_m = span_mm / 1000.0
        pos, bmd, sfd, x_mmax = compute_triangular_load_bmd_sfd(
            span_mm, w, ascending=True
        )

        expected_mmax = w * span_m**2 / (9.0 * math.sqrt(3.0))
        # Discretization gives slight undershoot; 0.1% tolerance
        assert abs(max(bmd) - expected_mmax) < expected_mmax * 0.002

    def test_max_moment_location(self) -> None:
        """M_max occurs at x = L / sqrt(3)."""
        import math

        span_mm = 8000.0
        _, _, _, x_mmax = compute_triangular_load_bmd_sfd(span_mm, 15.0, ascending=True)
        expected_x = span_mm / math.sqrt(3.0)
        assert abs(x_mmax - expected_x) < 0.01

    def test_moment_zero_at_supports(self) -> None:
        """Moment should be zero at both supports."""
        pos, bmd, sfd, _ = compute_triangular_load_bmd_sfd(6000, 20.0, ascending=True)
        assert abs(bmd[0]) < 1e-10
        assert abs(bmd[-1]) < 1e-10

    def test_total_load_equilibrium(self) -> None:
        """R_A + R_B should equal total load W = wL/2."""
        span_mm, w = 6000.0, 20.0
        span_m = span_mm / 1000.0
        pos, bmd, sfd, _ = compute_triangular_load_bmd_sfd(span_mm, w, ascending=True)

        r_a = sfd[0]  # V(0) = R_A
        r_b = -sfd[-1]  # V(L) = R_A - W = -(R_B), so R_B = -V(L)
        total_load = w * span_m / 2.0
        assert abs(r_a + r_b - total_load) < 0.01


class TestTriangularLoadDescending:
    """Tests for simply supported beam with descending triangular load (w_max → 0)."""

    def test_reactions(self) -> None:
        """R_A = wL/3, R_B = wL/6 for descending triangular load."""
        span_mm, w = 6000.0, 20.0
        span_m = span_mm / 1000.0
        pos, bmd, sfd, _ = compute_triangular_load_bmd_sfd(span_mm, w, ascending=False)

        assert abs(sfd[0] - w * span_m / 3.0) < 0.01

    def test_max_moment_matches_ascending(self) -> None:
        """M_max descending should equal M_max ascending (by symmetry)."""
        span_mm, w = 6000.0, 20.0
        _, bmd_asc, _, _ = compute_triangular_load_bmd_sfd(span_mm, w, ascending=True)
        _, bmd_desc, _, _ = compute_triangular_load_bmd_sfd(span_mm, w, ascending=False)
        assert abs(max(bmd_asc) - max(bmd_desc)) < 0.01

    def test_max_moment_location_mirrored(self) -> None:
        """M_max location for descending = L - (L/sqrt(3)) = L*(1 - 1/sqrt(3))."""
        import math

        span_mm = 6000.0
        _, _, _, x_mmax = compute_triangular_load_bmd_sfd(
            span_mm, 20.0, ascending=False
        )
        expected_x = span_mm * (1.0 - 1.0 / math.sqrt(3.0))
        assert abs(x_mmax - expected_x) < 0.01

    def test_moment_zero_at_supports(self) -> None:
        """Moment should be zero at both supports."""
        pos, bmd, sfd, _ = compute_triangular_load_bmd_sfd(6000, 20.0, ascending=False)
        assert abs(bmd[0]) < 1e-10
        assert abs(bmd[-1]) < 1e-10


class TestTriangularLoadValidation:
    """Input validation tests for triangular load."""

    def test_negative_span_raises(self) -> None:
        with pytest.raises(ValueError, match="Span must be positive"):
            compute_triangular_load_bmd_sfd(-1000, 20.0)

    def test_zero_span_raises(self) -> None:
        with pytest.raises(ValueError, match="Span must be positive"):
            compute_triangular_load_bmd_sfd(0, 20.0)

    def test_negative_load_raises(self) -> None:
        with pytest.raises(ValueError, match="w_max must be positive"):
            compute_triangular_load_bmd_sfd(6000, -10.0)

    def test_zero_load_raises(self) -> None:
        with pytest.raises(ValueError, match="w_max must be positive"):
            compute_triangular_load_bmd_sfd(6000, 0.0)


# =============================================================================
# Applied Moment Tests
# =============================================================================


class TestAppliedMoment:
    """Tests for simply supported beam with applied concentrated moment."""

    def test_constant_shear(self) -> None:
        """V(x) = -M/L is constant for all x."""
        span_mm, moment_val = 6000.0, 30.0
        span_m = span_mm / 1000.0
        pos, bmd, sfd = compute_applied_moment_bmd_sfd(span_mm, moment_val, a_mm=3000.0)

        expected_v = -moment_val / span_m
        for v in sfd:
            assert abs(v - expected_v) < 1e-10

    def test_moment_jump_at_application_point(self) -> None:
        """BMD should jump by M at the application point."""
        span_mm, moment_val = 6000.0, 30.0
        pos, bmd, sfd = compute_applied_moment_bmd_sfd(span_mm, moment_val, a_mm=3000.0)

        # Find the index closest to a=3000 from left and right
        a_loc = 3000.0
        left_idx = max(i for i, x in enumerate(pos) if x < a_loc)
        right_idx = min(i for i, x in enumerate(pos) if x >= a_loc)

        # The jump should be approximately M
        jump = bmd[right_idx] - bmd[left_idx]
        # Jump depends on grid spacing; for 101 points it's close to M
        assert (
            abs(jump - moment_val) < moment_val * 0.02
        )  # 2% tolerance for grid effects

    def test_moment_zero_at_supports(self) -> None:
        """Moment should be zero at both supports."""
        pos, bmd, sfd = compute_applied_moment_bmd_sfd(6000, 30.0, a_mm=3000.0)
        assert abs(bmd[0]) < 1e-10
        assert abs(bmd[-1]) < 1e-10

    def test_midspan_default(self) -> None:
        """a_mm=None should default to midspan."""
        span_mm, moment_val = 6000.0, 30.0
        pos1, bmd1, sfd1 = compute_applied_moment_bmd_sfd(
            span_mm, moment_val, a_mm=None
        )
        pos2, bmd2, sfd2 = compute_applied_moment_bmd_sfd(
            span_mm, moment_val, a_mm=3000.0
        )

        for m1, m2 in zip(bmd1, bmd2, strict=True):
            assert abs(m1 - m2) < 1e-10

    def test_max_bm_at_midspan(self) -> None:
        """For moment at midspan, max |BM| = M/2."""
        span_mm, moment_val = 6000.0, 30.0
        pos, bmd, sfd = compute_applied_moment_bmd_sfd(span_mm, moment_val)

        max_abs_bm = max(abs(m) for m in bmd)
        assert abs(max_abs_bm - moment_val / 2.0) < 0.1

    def test_moment_at_left_support(self) -> None:
        """Applied moment at left support: BM jumps at x=0."""
        span_mm, moment_val = 6000.0, 30.0
        pos, bmd, sfd = compute_applied_moment_bmd_sfd(span_mm, moment_val, a_mm=0.0)

        # At x=0: M(0) = R_A*0 + M = M (since x >= a=0 for all points)
        assert abs(bmd[0] - moment_val) < 0.01
        # At x=L: M(L) = M*(1 - 1) = 0
        assert abs(bmd[-1]) < 0.01

    def test_moment_at_right_support(self) -> None:
        """Applied moment at right support."""
        span_mm, moment_val = 6000.0, 30.0
        pos, bmd, sfd = compute_applied_moment_bmd_sfd(span_mm, moment_val, a_mm=6000.0)

        # At x=0: M(0) = -M*0/L = 0 (all points x < a=L)
        assert abs(bmd[0]) < 0.01
        # At x=L: M(L) = -M*L/L + M = 0 (last point is x=a)
        assert abs(bmd[-1]) < 0.01


class TestAppliedMomentValidation:
    """Input validation tests for applied moment."""

    def test_negative_span_raises(self) -> None:
        with pytest.raises(ValueError, match="Span must be positive"):
            compute_applied_moment_bmd_sfd(-1000, 30.0)

    def test_position_out_of_range_raises(self) -> None:
        with pytest.raises(ValueError, match="Moment position"):
            compute_applied_moment_bmd_sfd(6000, 30.0, a_mm=7000.0)

    def test_negative_position_raises(self) -> None:
        with pytest.raises(ValueError, match="Moment position"):
            compute_applied_moment_bmd_sfd(6000, 30.0, a_mm=-100.0)
