import os
import sys

import pytest

# Add parent directory to path to import structural_lib
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from structural_lib.flexure import calculate_mu_lim, design_doubly_reinforced
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
    assert res.Asc_required == 0.0
    assert res.Ast_required > 0
    assert res.Mu_lim == pytest.approx(mu_lim, rel=1e-3)


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
    assert res.Asc_required > 0
    assert res.Ast_required > 0
    assert res.Mu_lim == pytest.approx(mu_lim, rel=1e-3)

    # Check logic manually
    # Mu2 = 0.5 * Mu_lim
    # Asc approx Mu2 / (fsc * (d-d'))
    # fsc for Fe415 is usually around 350-360 depending on d'/d


def test_steel_stress_fe415():
    """
    Test stress interpolation for Fe415.
    """
    # Source-defined design vertices; rounded Table A strains are not exact nodes.
    strength = 415 / 1.15
    first = 0.8 * strength / 200000
    second = 0.0001 + 0.85 * strength / 200000
    assert get_steel_stress(first, 415) == pytest.approx(0.8 * strength, abs=1e-10)

    # Test interpolation
    mid_strain = (first + second) / 2
    expected_stress = 0.825 * strength
    assert get_steel_stress(mid_strain, 415) == pytest.approx(
        expected_stress, abs=1e-10
    )

    # Test yield plateau
    assert get_steel_stress(0.005, 415) == pytest.approx(strength, abs=1e-10)


def test_steel_stress_fe500():
    """
    Test stress interpolation for Fe500.
    """
    # Point 1: 0.00174, 347.8

    assert get_steel_stress(0.00174, 500) == pytest.approx(347.8, rel=1e-3)
    assert get_steel_stress(0.005, 500) == pytest.approx(434.8, rel=1e-3)
