import math
import sys
import os

import pytest

# Add parent directory to path to import structural_lib
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from structural_lib import flexure, shear, materials


def test_calculate_tv_converts_kn_to_n():
    # Vu in kN should be converted to N inside shear.calculate_tv
    tv = shear.calculate_tv(vu_kn=100.0, b=200.0, d=400.0)
    expected = (100.0 * 1000.0) / (200.0 * 400.0)
    assert tv == pytest.approx(expected, rel=1e-9)


def test_calculate_ast_required_uses_knm_conversion():
    # Validate mu_knm -> N·mm conversion (x1,000,000)
    b, d = 300.0, 500.0
    fck, fy = 25.0, 500.0
    mu_knm = 100.0

    mu_nmm = mu_knm * 1_000_000.0
    term1 = 0.5 * fck / fy
    term2 = (4.6 * mu_nmm) / (fck * b * d * d)
    if term2 > 1.0:
        term2 = 1.0
    expected = term1 * (1.0 - math.sqrt(1.0 - term2)) * b * d

    ast = flexure.calculate_ast_required(b, d, mu_knm, fck, fy)
    assert ast == pytest.approx(expected, rel=1e-9)


def test_calculate_mu_lim_returns_knm():
    b, d = 300.0, 500.0
    fck, fy = 25.0, 500.0

    xu_max_d = materials.get_xu_max_d(fy)
    k = 0.36 * xu_max_d * (1 - 0.42 * xu_max_d)
    expected_nmm = k * fck * b * d * d
    expected_knm = expected_nmm / 1_000_000.0

    mu_lim = flexure.calculate_mu_lim(b, d, fck, fy)
    assert mu_lim == pytest.approx(expected_knm, rel=1e-9)
