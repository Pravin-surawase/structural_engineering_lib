# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Tests for anchorage check at simple supports.

Per IS 456:2000 Clause 26.2.3.3.
"""

from __future__ import annotations

from structural_lib.codes.is456.detailing import (
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
        """Test error handling for zero/negative shear."""
        result = check_anchorage_at_simple_support(
            bar_dia=16,
            fck=25,
            fy=500,
            vu_kn=0,  # Invalid
            support_width=230,
        )

        assert result.is_adequate is False
        assert len(result.errors) > 0
        assert "Shear" in result.errors[0]

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
