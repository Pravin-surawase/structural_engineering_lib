import pytest
import sys
import os

# Add parent directory to path to import structural_lib
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from structural_lib.flexure import design_doubly_reinforced, calculate_mu_lim
from structural_lib.materials import get_steel_stress


def test_singly_reinforced_fallback():
    """
    Test that design_doubly_reinforced falls back to singly reinforced
    when Mu < Mu_lim.
    """
    b, d, d_dash, d_total = 230, 450, 40, 500
    fck, fy = 25, 500

    # Calculate Mu_lim
    mu_lim = calculate_mu_lim(b, d, fck, fy)

    # Design for 0.8 * Mu_lim
    mu_design = 0.8 * mu_lim

    res = design_doubly_reinforced(b, d, d_dash, d_total, mu_design, fck, fy)

    assert res.is_safe
    assert res.asc_required == 0.0
    assert res.ast_required > 0
    assert res.mu_lim == pytest.approx(mu_lim, rel=1e-3)


def test_doubly_reinforced_needed():
    """
    Test design for Mu > Mu_lim.
    """
    b, d, d_dash, d_total = 230, 450, 40, 500
    fck, fy = 25, 415

    mu_lim = calculate_mu_lim(b, d, fck, fy)

    # Design for 1.5 * Mu_lim
    mu_design = 1.5 * mu_lim

    res = design_doubly_reinforced(b, d, d_dash, d_total, mu_design, fck, fy)

    assert res.is_safe
    assert res.asc_required > 0
    assert res.ast_required > 0
    assert res.mu_lim == pytest.approx(mu_lim, rel=1e-3)

    # Check logic manually
    # Mu2 = 0.5 * Mu_lim
    # Asc approx Mu2 / (fsc * (d-d'))
    # fsc for Fe415 is usually around 350-360 depending on d'/d


def test_steel_stress_fe415():
    """
    Test stress interpolation for Fe415.
    """
    # Point 1: 0.00144, 288.7
    # Point 2: 0.00163, 306.7

    # Test exact point
    assert get_steel_stress(0.00144, 415) == pytest.approx(288.7, rel=1e-3)

    # Test interpolation
    mid_strain = (0.00144 + 0.00163) / 2
    expected_stress = (288.7 + 306.7) / 2
    assert get_steel_stress(mid_strain, 415) == pytest.approx(expected_stress, rel=1e-3)

    # Test yield plateau
    assert get_steel_stress(0.005, 415) == pytest.approx(360.9, rel=1e-3)


def test_steel_stress_fe500():
    """
    Test stress interpolation for Fe500.
    """
    # Point 1: 0.00174, 347.8

    assert get_steel_stress(0.00174, 500) == pytest.approx(347.8, rel=1e-3)
    assert get_steel_stress(0.005, 500) == pytest.approx(434.8, rel=1e-3)
