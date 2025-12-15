import pytest

from structural_lib import flexure


def test_design_singly_reinforced_applies_minimum_steel_message():
    b, d, d_total = 230, 450, 500
    fck, fy = 25, 500

    res = flexure.design_singly_reinforced(b, d, d_total, mu_knm=1.0, fck=fck, fy=fy)
    assert res.is_safe is True
    assert res.ast_required > 0
    assert "Minimum steel" in res.error_message


def test_calculate_ast_required_returns_minus_one_when_over_reinforced():
    b, d = 230, 450
    fck, fy = 20, 415
    mu_lim = flexure.calculate_mu_lim(b, d, fck, fy)

    ast = flexure.calculate_ast_required(b, d, mu_lim * 1.01, fck, fy)
    assert ast == -1.0


def test_calculate_ast_required_at_mu_lim_is_finite():
    # Regression guard: avoid math-domain errors near the limit.
    b, d = 230, 450
    fck, fy = 20, 415
    mu_lim = flexure.calculate_mu_lim(b, d, fck, fy)

    ast = flexure.calculate_ast_required(b, d, mu_lim, fck, fy)
    assert ast > 0
    assert ast != float("inf")


def test_design_doubly_reinforced_invalid_geometry_guard():
    # Force denom <= 0 by setting d' ~= xu_max so strain_sc ~ 0 => fsc <= fcc.
    b, d, d_total = 230, 450, 500
    fck, fy = 25, 415

    mu_lim = flexure.calculate_mu_lim(b, d, fck, fy)
    mu = mu_lim * 1.5

    xu_max = flexure.materials.get_xu_max_d(fy) * d
    d_dash_bad = xu_max  # makes strain_sc = 0

    res = flexure.design_doubly_reinforced(b, d, d_dash_bad, d_total, mu, fck, fy)
    assert res.is_safe is False
    assert res.ast_required == 0.0
    assert "Invalid section geometry" in res.error_message


def test_design_doubly_reinforced_invalid_when_d_dash_exceeds_d():
    b, d, d_total = 230, 450, 500
    fck, fy = 25, 415

    mu_lim = flexure.calculate_mu_lim(b, d, fck, fy)
    mu = mu_lim * 1.5

    res = flexure.design_doubly_reinforced(
        b, d, d_dash=d + 10.0, d_total=d_total, mu_knm=mu, fck=fck, fy=fy
    )
    assert res.is_safe is False
    assert "Invalid section geometry" in res.error_message


def test_design_doubly_reinforced_flags_when_total_ast_exceeds_max():
    # Pick a small section so the 4% bD limit is low and easy to exceed.
    b, d, d_total = 80, 200, 220
    fck, fy = 20, 415

    mu_lim = flexure.calculate_mu_lim(b, d, fck, fy)
    # Increase demand until we deterministically hit the max-steel check.
    res = None
    for factor in [3.0, 5.0, 7.0, 10.0, 15.0, 20.0, 30.0]:
        res = flexure.design_doubly_reinforced(
            b=b,
            d=d,
            d_dash=25.0,
            d_total=d_total,
            mu_knm=mu_lim * factor,
            fck=fck,
            fy=fy,
        )
        if res.is_safe is False and "maximum" in res.error_message.lower():
            break

    assert res is not None
    assert res.is_safe is False
    assert "maximum" in res.error_message.lower()


def test_design_flanged_beam_neutral_axis_in_flange_matches_rectangular_design():
    bw, bf = 300, 900
    d, Df, d_total = 450, 100, 500
    fck, fy = 25, 500

    mu = 10.0  # small => NA in flange

    flanged = flexure.design_flanged_beam(
        bw=bw,
        bf=bf,
        d=d,
        Df=Df,
        d_total=d_total,
        mu_knm=mu,
        fck=fck,
        fy=fy,
    )
    rect = flexure.design_singly_reinforced(
        b=bf, d=d, d_total=d_total, mu_knm=mu, fck=fck, fy=fy
    )

    assert flanged.section_type == rect.section_type
    assert flanged.ast_required == pytest.approx(rect.ast_required)


def test_calculate_mu_lim_flanged_clamps_yf_to_df_near_boundary():
    # Choose d slightly below 5*Df so Df/d > 0.2, and set parameters so yf would exceed Df before clamping.
    bw, bf = 300, 900
    d, Df = 490, 100
    fck, fy = 25, 415

    mu_lim_t = flexure.calculate_mu_lim_flanged(
        bw=bw, bf=bf, d=d, Df=Df, fck=fck, fy=fy
    )
    assert mu_lim_t > 0


def test_design_flanged_beam_bisection_breaks_on_exact_target():
    # Craft a target Mu exactly equal to moment at the first bisection mid-point.
    bw, bf = 300, 900
    d, Df, d_total = 450, 120, 500
    fck, fy = 25, 415

    # Ensure we land in the singly-reinforced T-beam branch: mu_capacity_at_df < Mu <= mu_lim_t
    xu_max = flexure.materials.get_xu_max_d(fy) * d
    low = Df
    high = xu_max
    mid = (low + high) / 2.0

    # Replicate get_moment_t(mid) exactly.
    if (Df / d) <= 0.2:
        yf_val = Df
    else:
        yf_val = 0.15 * mid + 0.65 * Df
        if yf_val > Df:
            yf_val = Df

    c_web = 0.36 * fck * bw * mid
    m_web = c_web * (d - 0.42 * mid)
    c_flange_val = 0.45 * fck * (bf - bw) * yf_val
    m_flange = c_flange_val * (d - yf_val / 2.0)
    mu_target_knm = (m_web + m_flange) / 1000000.0

    # Nudge if needed to avoid the NA-in-flange path.
    mu_capacity_at_df_knm = (0.36 * fck * bf * Df * (d - 0.42 * Df)) / 1000000.0
    if mu_target_knm <= mu_capacity_at_df_knm:
        mu_target_knm = mu_capacity_at_df_knm * 1.05

    mu_lim_t = flexure.calculate_mu_lim_flanged(
        bw=bw, bf=bf, d=d, Df=Df, fck=fck, fy=fy
    )
    assert mu_target_knm < mu_lim_t

    res = flexure.design_flanged_beam(
        bw=bw,
        bf=bf,
        d=d,
        Df=Df,
        d_total=d_total,
        mu_knm=mu_target_knm,
        fck=fck,
        fy=fy,
    )

    # When the target matches the first mid-point exactly, the solver should hit the early-break path.
    assert res.xu == pytest.approx(mid)
