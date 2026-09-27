# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Tests for anchorage check at simple supports.

Per IS 456:2000 Clause 26.2.3.3.
"""

from __future__ import annotations

import pytest

from structural_lib.codes.is456.beam.detailing import (
    AnchorageCheckResult,
    check_anchorage_at_simple_support,
)


class TestAnchorageCheckAtSimpleSupport:
    """Tests for check_anchorage_at_simple_support function."""

    def test_anchorage_with_standard_bend_wide_support(self):
        """Test adequate anchorage with 90° bend and wide support."""
        # Wide support with bend should provide good anchorage
        result = check_anchorage_at_simple_support(
            bar_dia=12,
            fck=25,
            fy=415,
            vu_kn=50,
            support_width=450,  # Wide support
            cover=40,
            bar_type="deformed",
            has_standard_bend=True,
        )

        assert isinstance(result, AnchorageCheckResult)
        assert result.ld_available > 0
        # With 12mm bar: Lo = max(8*12=96, 450/2=225) = 225mm
        assert result.ld_available == 225.0

    def test_anchorage_inadequate_small_support(self):
        """Test inadequate anchorage with small support."""
        result = check_anchorage_at_simple_support(
            bar_dia=20,
            fck=20,
            fy=500,
            vu_kn=100,
            support_width=200,  # Small support
            cover=40,
            bar_type="deformed",
            has_standard_bend=True,
        )

        # 20mm bar in M20 concrete needs ~900mm Ld
        # Available: max(8*20=160, 200/2=100) = 160mm
        assert result.is_adequate is False
        assert result.ld_required > result.ld_available
        assert len(result.errors) > 0

    def test_anchorage_straight_extension(self):
        """Test anchorage with straight bar (no bend)."""
        result = check_anchorage_at_simple_support(
            bar_dia=16,
            fck=25,
            fy=500,
            vu_kn=80,
            support_width=230,
            cover=40,
            bar_type="deformed",
            has_standard_bend=False,  # No bend
        )

        # Without bend: Lo = 230/2 - 40 = 75mm
        assert result.ld_available == 75.0
        assert result.is_adequate is False  # Much less anchorage

    def test_anchorage_cover_exceeds_half_support(self):
        """Test warning when cover exceeds half support width."""
        result = check_anchorage_at_simple_support(
            bar_dia=12,
            fck=25,
            fy=415,
            vu_kn=50,
            support_width=60,  # Very small support
            cover=40,  # 40 > 30 (60/2)
            bar_type="deformed",
            has_standard_bend=False,
        )

        # Should warn that cover exceeds half support
        assert len(result.warnings) > 0
        assert "Cover" in result.warnings[0]

    def test_anchorage_invalid_bar_diameter(self):
        """Test error handling for invalid bar diameter."""
        result = check_anchorage_at_simple_support(
            bar_dia=0,  # Invalid
            fck=25,
            fy=500,
            vu_kn=80,
            support_width=230,
        )

        assert result.is_adequate is False
        assert len(result.errors) > 0
        assert "bar diameter" in result.errors[0].lower()

    def test_anchorage_invalid_shear_force(self):
        """Negative shear is outside the magnitude-only support check."""
        result = check_anchorage_at_simple_support(
            bar_dia=16,
            fck=25,
            fy=500,
            vu_kn=-1,  # Invalid
            support_width=230,
        )

        assert result.is_adequate is False
        assert len(result.errors) > 0
        assert "Shear" in result.errors[0]

    @pytest.mark.parametrize("width,adequate", [(724.0, False), (726.0, True)])
    def test_zero_shear_still_checks_unrounded_full_development_length(
        self, width, adequate
    ):
        from structural_lib.services.beam_api import (
            check_anchorage_at_simple_support as public_check,
        )

        result = public_check(
            bar_dia_mm=8,
            fck_nmm2=25,
            fy_nmm2=415,
            vu_kn=0,
            support_width_mm=width,
            cover_mm=40,
            has_standard_bend=False,
        )
        # 8 * 361.05 / (4 * 2.24) = 322.366071...; rounding to 322 hid failure.
        assert result.ld_required == pytest.approx(322.36607142857144, rel=0, abs=1e-9)
        assert result.ld_available == width / 2 - 40
        assert result.is_adequate is adequate
        positive_shear = check_anchorage_at_simple_support(
            8, 25, 415, 60, width, 40, has_standard_bend=False
        )
        assert result == positive_shear

    def test_anchorage_utilization_calculation(self):
        """Test that utilization is correctly calculated."""
        result = check_anchorage_at_simple_support(
            bar_dia=10,
            fck=30,
            fy=415,
            vu_kn=50,
            support_width=300,
            has_standard_bend=True,
        )

        # Utilization = ld_required / ld_available
        if result.ld_available > 0:
            expected_utilization = result.ld_required / result.ld_available
            assert abs(result.utilization - expected_utilization) < 0.01

    @pytest.mark.parametrize("fck", [45.0, 50.0])
    def test_high_grade_bond_correction_reaches_public_support_wrapper(self, fck):
        from structural_lib.services.beam_api import (
            check_anchorage_at_simple_support as public_check,
        )

        result = public_check(
            bar_dia_mm=20,
            fck_nmm2=fck,
            fy_nmm2=500,
            vu_kn=60,
            support_width_mm=1360,
        )
        assert not result.is_adequate
        assert result.ld_required == pytest.approx(715.4605263157895, rel=0, abs=1e-9)
        assert result.ld_available == 680.0

    def test_anchorage_plain_bars(self):
        """Test with plain bars (higher Ld required)."""
        result_deformed = check_anchorage_at_simple_support(
            bar_dia=16,
            fck=25,
            fy=415,
            vu_kn=80,
            support_width=300,
            bar_type="deformed",
        )

        result_plain = check_anchorage_at_simple_support(
            bar_dia=16,
            fck=25,
            fy=415,
            vu_kn=80,
            support_width=300,
            bar_type="plain",
        )

        # Plain bars have lower bond stress -> higher Ld required
        assert result_plain.ld_required > result_deformed.ld_required


class TestAnchorageCheckEdgeCases:
    """Edge case tests for anchorage check."""

    def test_very_small_bar(self):
        """Test with 8mm bar (smallest common size)."""
        result = check_anchorage_at_simple_support(
            bar_dia=8,
            fck=25,
            fy=415,
            vu_kn=30,
            support_width=230,
            has_standard_bend=True,
        )

        # 8mm bar: Lo = max(8*8=64, 230/2=115) = 115mm
        assert result.ld_available == 115.0
        # Should still need to check if adequate
        assert isinstance(result.is_adequate, bool)

    def test_high_strength_concrete(self):
        """Test with high strength concrete (better bond)."""
        result_m25 = check_anchorage_at_simple_support(
            bar_dia=16,
            fck=25,
            vu_kn=80,
            fy=500,
            support_width=300,
        )

        result_m40 = check_anchorage_at_simple_support(
            bar_dia=16,
            fck=40,
            vu_kn=80,
            fy=500,
            support_width=300,
        )

        # Higher grade concrete -> lower Ld required
        assert result_m40.ld_required < result_m25.ld_required

    def test_high_strength_steel(self):
        """Test with high strength steel (higher Ld required)."""
        result_fe415 = check_anchorage_at_simple_support(
            bar_dia=16,
            fck=25,
            vu_kn=80,
            fy=415,
            support_width=300,
        )

        result_fe500 = check_anchorage_at_simple_support(
            bar_dia=16,
            fck=25,
            vu_kn=80,
            fy=500,
            support_width=300,
        )

        # Higher fy -> higher Ld required
        assert result_fe500.ld_required > result_fe415.ld_required
