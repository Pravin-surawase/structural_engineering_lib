import pytest
import sys
import os

# Add parent directory to path to import structural_lib
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from structural_lib.flexure import (
    design_flanged_beam,
    design_singly_reinforced,
)
from structural_lib.types import DesignSectionType


def test_flanged_beam_neutral_axis_in_flange():
    # Case 1: Xu <= Df
    # Use a very deep flange or small moment
    # bf=1000, Df=150, d=500, bw=300
    # Mu capacity at Df approx 0.36*25*1000*150*(500-0.42*150) ~ 589 kNm
    # Let's use Mu = 200 kNm. Should be in flange.

    bf = 1000
    Df = 150
    bw = 300
    d = 500
    d_total = 550
    fck = 25
    fy = 500
    mu = 200

    res = design_flanged_beam(bw, bf, d, Df, d_total, mu, fck, fy)

    # Should match rectangular beam of width bf
    res_rect = design_singly_reinforced(bf, d, d_total, mu, fck, fy)

    assert res.ast_required == pytest.approx(res_rect.ast_required, rel=1e-4)
    assert res.xu == pytest.approx(res_rect.xu, rel=1e-4)
    assert res.xu <= Df


def test_flanged_beam_neutral_axis_in_web_singly_reinforced():
    # Case 2: Xu > Df but Mu < Mu_lim_T
    # bf=1000, Df=100, d=500, bw=300
    # Mu capacity at Df approx 0.36*25*1000*100*(500-42) ~ 412 kNm
    # Mu_lim_T approx...
    # Let's try Mu = 500 kNm.

    bf = 1000
    Df = 100
    bw = 300
    d = 500
    d_total = 550
    fck = 25
    fy = 500
    mu = 500

    res = design_flanged_beam(bw, bf, d, Df, d_total, mu, fck, fy)

    assert res.xu > Df
    assert (
        res.section_type == DesignSectionType.UNDER_REINFORCED
        or res.section_type == DesignSectionType.BALANCED
    )
    assert res.asc_required == 0.0

    # Check equilibrium roughly
    # C = T
    # yf check
    xu = res.xu
    if (Df / d) <= 0.2:
        yf = Df
    else:
        yf = 0.15 * xu + 0.65 * Df
        if yf > Df:
            yf = Df

    C = 0.36 * fck * bw * xu + 0.45 * fck * (bf - bw) * yf
    T = 0.87 * fy * res.ast_required

    assert C == pytest.approx(T, rel=1e-3)


def test_flanged_beam_doubly_reinforced():
    # Case 3: Mu > Mu_lim_T
    # bf=1000, Df=100, d=500, bw=300
    # Mu_lim_T is around 600-700 kNm?
    # Let's use Mu = 1000 kNm.

    bf = 1000
    Df = 100
    bw = 300
    d = 500
    d_total = 550
    fck = 25
    fy = 500
    mu = 1000

    res = design_flanged_beam(bw, bf, d, Df, d_total, mu, fck, fy)

    assert res.section_type == DesignSectionType.OVER_REINFORCED  # Doubly Reinforced
    assert res.asc_required > 0.0
    assert res.ast_required > 0.0
    assert res.xu == pytest.approx(res.xu_max, rel=1e-4)


def test_flanged_beam_combined_max_steel_is_not_reported_safe():
    # Regression for combined Ast max check in doubly-reinforced T-beams.
    # This case produces a web design that alone can be safe, but the combined
    # (web + flange) Ast exceeds the 4% bw*d_total cap.
    res = design_flanged_beam(
        150,  # bw
        800,  # bf
        450,  # d
        80,  # Df
        500,  # d_total
        600,  # mu_knm
        20,  # fck
        415,  # fy
    )
    assert res.is_safe is False
    assert "combined t-beam" in res.error_message.lower()


def test_flanged_beam_invalid_geometry_fails_gracefully():
    res = design_flanged_beam(
        300,
        250,  # bf < bw invalid
        450,
        100,
        500,
        200,
        25,
        500,
    )
    assert res.is_safe is False
    assert "bf" in res.error_message.lower()
    assert any(err.code == "E_INPUT_015" for err in res.errors)
