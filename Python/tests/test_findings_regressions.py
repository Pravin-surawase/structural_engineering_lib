from structural_lib.compliance import check_compliance_report
from structural_lib.detailing import select_bar_arrangement
from structural_lib.flexure import design_flanged_beam
from structural_lib.serviceability import check_crack_width, check_deflection_span_depth


def test_detailing_select_bar_arrangement_invalid_geometry_is_deterministic():
    arr = select_bar_arrangement(ast_required=800, b=0, cover=25)
    assert arr.count == 2
    assert arr.diameter == 12


def test_compliance_flexure_utilization_zero_mu_is_zero():
    report = check_compliance_report(
        cases=[{"case_id": "ZERO", "mu_knm": 0.0, "vu_kn": 10.0}],
        b_mm=230.0,
        D_mm=500.0,
        d_mm=450.0,
        fck_nmm2=25.0,
        fy_nmm2=500.0,
        asv_mm2=100.0,
    )
    assert report.cases[0].utilizations["flexure"] == 0.0


def test_serviceability_unknown_strings_are_not_errors():
    res = check_deflection_span_depth(
        span_mm=4000.0,
        d_mm=500.0,
        support_condition="not_a_real_support",
    )
    assert res.is_ok is True
    assert any("unknown support condition" in a.lower() for a in res.assumptions)

    cr = check_crack_width(exposure_class="not_a_real_exposure", limit_mm=0.3)
    assert cr.is_ok is False
    assert any("unknown exposure class" in a.lower() for a in cr.assumptions)


def test_flanged_beam_invalid_df_ge_d_fails():
    res = design_flanged_beam(
        bw=300,
        bf=500,
        d=450,
        Df=450,
        d_total=500,
        mu_knm=200,
        fck=25,
        fy=500,
    )
    assert res.is_safe is False
    assert "df" in res.error_message.lower()


def test_flanged_beam_invalid_d_total_le_d_fails():
    res = design_flanged_beam(
        bw=300,
        bf=500,
        d=450,
        Df=100,
        d_total=450,
        mu_knm=200,
        fck=25,
        fy=500,
    )
    assert res.is_safe is False
    assert "d_total" in res.error_message.lower()


# ============================================================================
# Q-002, Q-003: Input validation edge cases
# ============================================================================


def test_development_length_invalid_inputs():
    """Q-002: calculate_development_length returns 0 for invalid inputs."""
    from structural_lib.detailing import calculate_development_length

    assert calculate_development_length(bar_dia=0, fck=25, fy=500) == 0.0
    assert calculate_development_length(bar_dia=16, fck=0, fy=500) == 0.0
    assert calculate_development_length(bar_dia=16, fck=25, fy=0) == 0.0
    assert calculate_development_length(bar_dia=-16, fck=25, fy=500) == 0.0


def test_xu_max_d_invalid_fy():
    """Q-003: get_xu_max_d returns 0 for invalid fy."""
    from structural_lib.materials import get_xu_max_d

    assert get_xu_max_d(0) == 0.0
    assert get_xu_max_d(-500) == 0.0
