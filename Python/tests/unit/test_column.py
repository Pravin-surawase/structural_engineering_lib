# SPDX-License-Identifier: MIT
"""Tests for IS 456 column design module (Cl 39.1-39.5)."""
import pytest
from structural_lib.codes.is456.column import (
    ColumnDesignResult,
    calculate_axial_capacity,
    calculate_pm_interaction_point,
    check_reinforcement_limits,
    design_short_column,
)


def test_calculate_axial_capacity_standard_case():
    """Test axial capacity for standard 300×300 column with M25, Fe500."""
    b_mm = 300.0
    D_mm = 300.0
    fck = 25.0
    fy = 500.0
    ast_mm2 = 1440.0  # 1.6% of gross area

    Ag = 90000.0
    Ac = Ag - ast_mm2 # = 88560 mm²
    expected_kn = (0.4 * fck * Ac + 0.67 * fy * ast_mm2) / 1000.0

    result = calculate_axial_capacity(b_mm, D_mm, fck, fy, ast_mm2)

    assert result == pytest.approx(expected_kn, abs=2.0)  # Allow ±2kN for rounding
    assert result == pytest.approx(1366.8, abs=2.0)


def test_calculate_axial_capacity_zero_steel():
    """Test axial capacity with zero steel (pure concrete)."""
    b_mm = 250.0
    D_mm = 400.0
    fck = 20.0
    fy = 415.0
    ast_mm2 = 0.0

    Ag = 100000.0
    expected_kn = (0.4 * fck * Ag) / 1000.0  # = 800 kN

    result = calculate_axial_capacity(b_mm, D_mm, fck, fy, ast_mm2)

    assert result == pytest.approx(800.0, abs=0.1)


def test_calculate_axial_capacity_invalid_dimensions():
    """Test that invalid dimensions raise ValueError."""
    with pytest.raises(ValueError, match='must be positive'):
        calculate_axial_capacity(-300, 300, 25, 500, 1440)

    with pytest.raises(ValueError, match='must be positive'):
        calculate_axial_capacity(300, 0, 25, 500, 1440)


def test_calculate_axial_capacity_invalid_materials():
    """Test that invalid material properties raise ValueError."""
    with pytest.raises(ValueError, match='must be positive'):
        calculate_axial_capacity(300, 300, -25, 500, 1440)

    with pytest.raises(ValueError, match='must be positive'):
        calculate_axial_capacity(300, 300, 25, 0, 1440)


def test_calculate_axial_capacity_steel_exceeds_gross_area():
    """Test that steel area exceeding gross area raises ValueError."""
    with pytest.raises(ValueError, match='exceeds gross area'):
        calculate_axial_capacity(300, 300, 25, 500, 100000)


def test_calculate_pm_interaction_point_balanced_failure():
    """Test P-M interaction at balanced failure (xu_max/d)."""
    b_mm = 300.0
    D_mm = 400.0
    fck = 25.0
    fy = 500.0
    ast_mm2 = 2000.0
    cover_mm = 40.0

    Pu_kn, Mu_knm = calculate_pm_interaction_point(
        b_mm, D_mm, fck, fy, ast_mm2, cover_mm, xu_d_ratio=0.46
    )

    assert Pu_kn > 0
    assert Mu_knm > 0
    assert isinstance(Pu_kn, float)
    assert isinstance(Mu_knm, float)


def test_calculate_pm_interaction_point_default_xu_ratio():
    """Test P-M interaction with default xu_max/d ratio."""
    b_mm = 300.0
    D_mm = 300.0
    fck = 25.0
    fy = 500.0
    ast_mm2 = 1440.0

    Pu_kn, Mu_knm = calculate_pm_interaction_point(b_mm, D_mm, fck, fy, ast_mm2)

    assert Pu_kn > 0
    assert Mu_knm > 0


def test_check_reinforcement_limits_valid_steel():
    """Test reinforcement check with valid steel (1.5% of Ag)."""
    b_mm = 300.0
    D_mm = 300.0
    ast_mm2 = 1350.0  # 1.5% of Ag

    result = check_reinforcement_limits(b_mm, D_mm, ast_mm2)

    assert result['is_ok'] is True
    assert result['p_percent'] == pytest.approx(1.5, abs=0.01)
    assert result['ast_min_mm2'] == pytest.approx(720.0, abs=1.0)
    assert result['ast_max_mm2'] == pytest.approx(5400.0, abs=1.0)
    assert len(result['errors']) == 0


def test_check_reinforcement_limits_below_minimum():
    """Test reinforcement check when steel < 0.8% Ag."""
    b_mm = 300.0
    D_mm = 300.0
    ast_mm2 = 500.0

    result = check_reinforcement_limits(b_mm, D_mm, ast_mm2)

    assert result['is_ok'] is False
    assert len(result['errors']) == 1
    assert 'minimum' in result['errors'][0].lower()
    assert '0.8%' in result['errors'][0]


def test_check_reinforcement_limits_above_maximum():
    """Test reinforcement check when steel > 6% Ag."""
    b_mm = 300.0
    D_mm = 300.0
    ast_mm2 = 6000.0

    result = check_reinforcement_limits(b_mm, D_mm, ast_mm2)

    assert result['is_ok'] is False
    assert len(result['errors']) == 1
    assert 'maximum' in result['errors'][0].lower()


def test_check_reinforcement_limits_warning_4_to_6_percent():
    """Test warning when steel is between 4-6% (lap zone concern)."""
    b_mm = 300.0
    D_mm = 300.0
    ast_mm2 = 4500.0  # 5% of Ag

    result = check_reinforcement_limits(b_mm, D_mm, ast_mm2)

    assert result['is_ok'] is True  # Still valid
    assert result['p_percent'] == pytest.approx(5.0, abs=0.01)
    assert len(result['warnings']) >= 1
    assert any('4.0%' in w for w in result['warnings'])


def test_design_short_column_light_load():
    """Test short column design with light axial load."""
    b_mm = 300.0
    D_mm = 300.0
    Pu_kn = 800.0
    Mu_knm = 40.0
    fck = 25.0
    fy = 500.0

    result = design_short_column(b_mm, D_mm, Pu_kn, Mu_knm, fck, fy)

    assert isinstance(result, ColumnDesignResult)
    assert result.is_safe is True
    assert result.Pu_capacity_kn >= Pu_kn
    assert result.Mu_capacity_knm >= Mu_knm
    assert result.utilization <= 1.0
    assert result.ast_required_mm2 >= result.ast_min_mm2
    assert result.ast_required_mm2 <= result.ast_max_mm2
    assert result.p_percent >= 0.8
    assert result.p_percent <= 6.0
    assert len(result.errors) == 0


def test_design_short_column_heavy_load():
    """Test short column design with heavy load (may be unsafe)."""
    b_mm = 300.0
    D_mm = 300.0
    Pu_kn = 2500.0
    Mu_knm = 200.0
    fck = 25.0
    fy = 500.0

    result = design_short_column(b_mm, D_mm, Pu_kn, Mu_knm, fck, fy)

    assert isinstance(result, ColumnDesignResult)
    if not result.is_safe:
        assert result.utilization > 1.0
        assert len(result.errors) >= 1


def test_design_short_column_minimum_eccentricity():
    """Test that minimum eccentricity is enforced per Cl 25.4."""
    b_mm = 300.0
    D_mm = 300.0
    Pu_kn = 1000.0
    Mu_knm = 1.0
    fck = 25.0
    fy = 500.0

    result = design_short_column(b_mm, D_mm, Pu_kn, Mu_knm, fck, fy)

    assert result.e_min_mm >= 10.0
    assert len(result.warnings) >= 1
    assert any('minimum' in w.lower() and 'eccentricity' in w.lower() for w in result.warnings)


def test_design_short_column_invalid_dimensions():
    """Test design function with invalid dimensions."""
    result = design_short_column(
        b_mm=-300,
        D_mm=300,
        Pu_kn=1000,
        Mu_knm=50,
        fck=25,
        fy=500,
    )

    assert result.is_safe is False
    assert len(result.errors) >= 1
    assert 'width' in result.errors[0].lower()
