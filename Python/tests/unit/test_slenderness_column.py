# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for column slenderness and IS 456 preparation functions.

References:
- IS 456:2000 Cl. 25.1.2 (column slenderness classification)
- IS 456:2000 Cl. 25.3, Table 28 (effective length factors)
- IS 456:2000 Cl. 38.1 (stress block parameters)
"""
import pytest

from structural_lib.codes.is456.slenderness import (
    check_column_slenderness,
    get_effective_length_factor,
)
from structural_lib.codes.is456.materials import get_stress_block_params
from structural_lib.codes.is456.tables import get_xu_max_ratio


# =============================================================================
# Column Slenderness Tests (IS 456 Cl. 25.1.2)
# =============================================================================


def test_check_column_slenderness_short_square():
    """Test short column classification for square section.

    IS 456 Cl. 25.1.2: Short column if le/b <= 12 AND le/D <= 12.
    """
    result = check_column_slenderness(
        b_mm=300,
        D_mm=300,
        unsupported_length_mm=3000,
        effective_length_factor=1.0
    )

    # le = 1.0 × 3000 = 3000 mm
    # le/b = 3000/300 = 10 <= 12 ✓
    # le/D = 3000/300 = 10 <= 12 ✓
    assert result.is_ok is True
    assert result.is_slender is False
    assert result.slenderness_ratio == pytest.approx(10.0, rel=1e-2)
    assert result.slenderness_limit == 12.0
    assert result.utilization < 1.0
    assert "SHORT" in result.remarks


def test_check_column_slenderness_long_square():
    """Test long column classification for square section.

    IS 456 Cl. 25.1.2: Long column if le/b > 12 OR le/D > 12.
    """
    result = check_column_slenderness(
        b_mm=300,
        D_mm=300,
        unsupported_length_mm=5000,
        effective_length_factor=1.0
    )

    # le = 1.0 × 5000 = 5000 mm
    # le/b = 5000/300 = 16.67 > 12 ✗
    # le/D = 5000/300 = 16.67 > 12 ✗
    assert result.is_ok is False
    assert result.is_slender is True
    assert result.slenderness_ratio == pytest.approx(16.67, rel=1e-2)
    assert result.utilization > 1.0
    assert "LONG" in result.remarks or "SLENDER" in result.remarks
    assert len(result.warnings) > 0


def test_check_column_slenderness_borderline():
    """Test borderline case: le/b = 12 exactly (should be short)."""
    result = check_column_slenderness(
        b_mm=300,
        D_mm=300,
        unsupported_length_mm=3600,
        effective_length_factor=1.0
    )

    # le = 1.0 × 3600 = 3600 mm
    # le/b = 3600/300 = 12.0 (exactly at limit)
    assert result.is_ok is True
    assert result.is_slender is False
    assert result.slenderness_ratio == pytest.approx(12.0, rel=1e-2)
    assert result.utilization == pytest.approx(1.0, rel=1e-3)


def test_check_column_slenderness_rectangular_short():
    """Test rectangular column with different b and D (short)."""
    result = check_column_slenderness(
        b_mm=200,
        D_mm=400,
        unsupported_length_mm=3000,
        effective_length_factor=1.0
    )

    # le = 1.0 × 3000 = 3000 mm
    # le/b = 3000/200 = 15.0 > 12 ✗
    # le/D = 3000/400 = 7.5 <= 12 ✓
    # Governs: le/b = 15.0 → LONG
    assert result.is_ok is False
    assert result.is_slender is True
    assert result.slenderness_ratio == pytest.approx(15.0, rel=1e-2)
    assert result.depth_to_width_ratio == pytest.approx(2.0, rel=1e-2)


def test_check_column_slenderness_with_effective_length_factor():
    """Test with effective length factor < 1.0 (both ends fixed)."""
    result = check_column_slenderness(
        b_mm=300,
        D_mm=300,
        unsupported_length_mm=3000,
        effective_length_factor=0.65
    )

    # le = 0.65 × 3000 = 1950 mm
    # le/b = 1950/300 = 6.5 <= 12 ✓
    # le/D = 1950/300 = 6.5 <= 12 ✓
    assert result.is_ok is True
    assert result.is_slender is False
    assert result.slenderness_ratio == pytest.approx(6.5, rel=1e-2)
    assert result.computed["le_mm"] == pytest.approx(1950.0, rel=1e-2)


def test_check_column_slenderness_cantilever():
    """Test cantilever column (effective length factor = 2.0).

    Cantilever columns have le = 2.0 × unsupported length.
    """
    result = check_column_slenderness(
        b_mm=300,
        D_mm=300,
        unsupported_length_mm=3000,
        effective_length_factor=2.0
    )

    # le = 2.0 × 3000 = 6000 mm
    # le/b = 6000/300 = 20 > 12 ✗
    assert result.is_ok is False
    assert result.is_slender is True
    assert result.slenderness_ratio == pytest.approx(20.0, rel=1e-2)
    assert result.computed["le_mm"] == pytest.approx(6000.0, rel=1e-2)


def test_check_column_slenderness_invalid_zero_width():
    """Test error handling for invalid input (b = 0)."""
    result = check_column_slenderness(
        b_mm=0,
        D_mm=300,
        unsupported_length_mm=3000,
        effective_length_factor=1.0
    )

    assert result.is_ok is False
    assert len(result.errors) > 0
    assert any("width" in err.lower() for err in result.errors)


def test_check_column_slenderness_invalid_negative_length():
    """Test error handling for invalid input (negative length)."""
    result = check_column_slenderness(
        b_mm=300,
        D_mm=300,
        unsupported_length_mm=-3000,
        effective_length_factor=1.0
    )

    assert result.is_ok is False
    assert len(result.errors) > 0
    assert any("length" in err.lower() for err in result.errors)


def test_check_column_slenderness_minimum_dimension_warning():
    """Test warning for column width below recommended minimum (200mm).

    IS 456 Cl. 26.5.3.1: Minimum lateral dimension should be 200mm.
    """
    result = check_column_slenderness(
        b_mm=150,
        D_mm=300,
        unsupported_length_mm=2000,
        effective_length_factor=1.0
    )

    assert len(result.warnings) > 0
    assert any("minimum" in warn.lower() for warn in result.warnings)


# =============================================================================
# Effective Length Factor Tests (IS 456 Table 28)
# =============================================================================


def test_get_effective_length_factor_both_fixed():
    """Test effective length factor for both ends fixed.

    IS 456 Table 28: Both ends fixed → k = 0.65
    """
    factor = get_effective_length_factor("fixed", "fixed")
    assert factor == pytest.approx(0.65, rel=1e-6)


def test_get_effective_length_factor_one_fixed_one_hinged():
    """Test effective length factor for one end fixed, one hinged.

    IS 456 Table 28: One fixed, one hinged → k = 0.80
    """
    factor = get_effective_length_factor("fixed", "hinged")
    assert factor == pytest.approx(0.80, rel=1e-6)

    factor_reversed = get_effective_length_factor("hinged", "fixed")
    assert factor_reversed == pytest.approx(0.80, rel=1e-6)


def test_get_effective_length_factor_both_hinged():
    """Test effective length factor for both ends hinged.

    IS 456 Table 28: Both ends hinged → k = 1.0
    """
    factor = get_effective_length_factor("hinged", "hinged")
    assert factor == pytest.approx(1.0, rel=1e-6)


def test_get_effective_length_factor_fixed_and_free():
    """Test effective length factor for fixed at one end, free at other (cantilever).

    IS 456 Table 28: One fixed, one free → k = 2.0
    """
    factor = get_effective_length_factor("fixed", "free")
    assert factor == pytest.approx(2.0, rel=1e-6)

    factor_reversed = get_effective_length_factor("free", "fixed")
    assert factor_reversed == pytest.approx(2.0, rel=1e-6)


def test_get_effective_length_factor_case_insensitive():
    """Test that end condition strings are case-insensitive."""
    factor1 = get_effective_length_factor("FIXED", "HINGED")
    factor2 = get_effective_length_factor("Fixed", "Hinged")
    factor3 = get_effective_length_factor("fixed", "hinged")

    assert factor1 == factor2 == factor3 == pytest.approx(0.80, rel=1e-6)


def test_get_effective_length_factor_invalid_condition():
    """Test error handling for invalid end condition."""
    with pytest.raises(ValueError) as exc_info:
        get_effective_length_factor("fixed", "invalid_condition")

    assert "Invalid end conditions" in str(exc_info.value)


# =============================================================================
# Stress Block Parameters Tests (IS 456 Cl. 38.1)
# =============================================================================


def test_get_stress_block_params_m25():
    """Test stress block parameters for M25 concrete.

    IS 456 Cl. 38.1:
    - Average stress = 0.36fck
    - Depth factor = 0.42
    """
    params = get_stress_block_params(fck=25)

    assert params['average_stress'] == pytest.approx(0.36, rel=1e-6)
    assert params['depth_factor'] == pytest.approx(0.42, rel=1e-6)
    assert params['force_factor'] == pytest.approx(0.36, rel=1e-6)
    assert params['fck'] == 25


def test_get_stress_block_params_m30():
    """Test stress block parameters for M30 concrete.

    Parameters should be the same ratios (0.36 and 0.42 are constants).
    """
    params = get_stress_block_params(fck=30)

    assert params['average_stress'] == pytest.approx(0.36, rel=1e-6)
    assert params['depth_factor'] == pytest.approx(0.42, rel=1e-6)
    assert params['force_factor'] == pytest.approx(0.36, rel=1e-6)
    assert params['fck'] == 30


def test_get_stress_block_params_high_grade():
    """Test stress block parameters for high-grade concrete (M60).

    Stress block parameters remain constant regardless of fck grade.
    """
    params = get_stress_block_params(fck=60)

    assert params['average_stress'] == pytest.approx(0.36, rel=1e-6)
    assert params['depth_factor'] == pytest.approx(0.42, rel=1e-6)
    assert params['force_factor'] == pytest.approx(0.36, rel=1e-6)
    assert params['fck'] == 60


def test_get_stress_block_params_invalid_zero_fck():
    """Test error handling for invalid fck = 0."""
    with pytest.raises(ValueError) as exc_info:
        get_stress_block_params(fck=0)

    assert "positive" in str(exc_info.value).lower()


def test_get_stress_block_params_invalid_negative_fck():
    """Test error handling for invalid fck < 0."""
    with pytest.raises(ValueError) as exc_info:
        get_stress_block_params(fck=-25)

    assert "positive" in str(exc_info.value).lower()


# =============================================================================
# xu_max/d Ratio Tests (IS 456 Cl. 38.1)
# =============================================================================


def test_get_xu_max_ratio_fe250():
    """Test xu_max/d ratio for Fe250 steel.

    IS 456 Cl. 38.1: For fy=250, xu_max/d = 0.53
    """
    ratio = get_xu_max_ratio(fy=250)
    assert ratio == pytest.approx(0.53, rel=1e-6)


def test_get_xu_max_ratio_fe415():
    """Test xu_max/d ratio for Fe415 steel.

    IS 456 Cl. 38.1: For fy=415, xu_max/d = 0.48
    """
    ratio = get_xu_max_ratio(fy=415)
    assert ratio == pytest.approx(0.48, rel=1e-6)


def test_get_xu_max_ratio_fe500():
    """Test xu_max/d ratio for Fe500 steel.

    IS 456 Cl. 38.1: For fy=500, xu_max/d = 0.46
    """
    ratio = get_xu_max_ratio(fy=500)
    assert ratio == pytest.approx(0.46, rel=1e-6)


def test_get_xu_max_ratio_fe550():
    """Test xu_max/d ratio for Fe550 steel (uses formula).

    For grades not in table, uses formula: 700 / (1100 + 0.87×fy)
    """
    ratio = get_xu_max_ratio(fy=550)
    expected = 700 / (1100 + 0.87 * 550)
    assert ratio == pytest.approx(expected, rel=1e-6)


def test_get_xu_max_ratio_invalid_zero_fy():
    """Test error handling for invalid fy = 0."""
    with pytest.raises(ValueError):
        get_xu_max_ratio(fy=0)


def test_get_xu_max_ratio_invalid_negative_fy():
    """Test error handling for invalid fy < 0."""
    with pytest.raises(ValueError):
        get_xu_max_ratio(fy=-415)


# =============================================================================
# Integration Tests
# =============================================================================


def test_column_slenderness_with_table_28_factor():
    """Integration test: Use get_effective_length_factor() with check_column_slenderness()."""
    k = get_effective_length_factor("fixed", "hinged")

    result = check_column_slenderness(
        b_mm=300,
        D_mm=300,
        unsupported_length_mm=4000,
        effective_length_factor=k
    )

    # le = 0.80 × 4000 = 3200 mm
    # le/b = 3200/300 = 10.67 <= 12 ✓
    assert result.is_ok is True
    assert result.is_slender is False
    assert result.computed["le_mm"] == pytest.approx(3200.0, rel=1e-2)


def test_stress_block_params_keys():
    """Test that stress block params dict contains all required keys."""
    params = get_stress_block_params(fck=25)

    required_keys = {'average_stress', 'depth_factor', 'force_factor', 'fck'}
    assert set(params.keys()) == required_keys
