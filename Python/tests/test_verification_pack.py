import os
import sys

# Add parent directory to path to import structural_lib
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from structural_lib import flexure, shear, serviceability, types
from structural_lib.compliance import check_compliance_report


def r9(value: float) -> float:
    return round(float(value), 9)


def test_verification_flexure_singly_rectangular_case_01():
    """Pinned regression target: singly reinforced rectangular beam."""
    b_mm, d_mm, d_total_mm = 230.0, 450.0, 500.0
    mu_knm = 100.0
    fck_nmm2, fy_nmm2 = 20.0, 415.0

    res = flexure.design_singly_reinforced(
        b_mm, d_mm, d_total_mm, mu_knm, fck_nmm2, fy_nmm2
    )

    assert res.is_safe is True
    assert res.section_type == types.DesignSectionType.UNDER_REINFORCED
    assert res.error_message == ""

    assert r9(res.mu_lim) == 128.51301888
    assert r9(res.ast_required) == 719.616175169
    assert r9(res.pt_provided) == 0.695281329
    assert r9(res.xu) == 156.894577322
    assert r9(res.xu_max) == 216.0


def test_verification_flexure_doubly_rectangular_case_02():
    """Pinned regression target: doubly reinforced rectangular beam."""
    b_mm, d_mm, d_dash_mm, d_total_mm = 300.0, 450.0, 50.0, 500.0
    mu_knm = 250.0
    fck_nmm2, fy_nmm2 = 25.0, 500.0

    res = flexure.design_doubly_reinforced(
        b_mm, d_mm, d_dash_mm, d_total_mm, mu_knm, fck_nmm2, fy_nmm2
    )

    assert res.is_safe is True
    assert res.section_type == types.DesignSectionType.OVER_REINFORCED

    assert r9(res.mu_lim) == 202.914234
    assert r9(res.ast_required) == 1550.355138609
    assert r9(res.asc_required) == 296.55513585
    assert r9(res.xu) == 207.0
    assert r9(res.xu_max) == 207.0


def test_verification_flexure_flanged_case_03():
    """Pinned regression target: flanged beam flexure (T-beam style inputs)."""
    bw_mm, bf_mm, d_mm, Df_mm, d_total_mm = 300.0, 1000.0, 500.0, 150.0, 550.0
    mu_knm = 200.0
    fck_nmm2, fy_nmm2 = 25.0, 500.0

    res = flexure.design_flanged_beam(
        bw_mm, bf_mm, d_mm, Df_mm, d_total_mm, mu_knm, fck_nmm2, fy_nmm2
    )

    assert res.is_safe is True
    assert res.section_type == types.DesignSectionType.UNDER_REINFORCED

    assert r9(res.mu_lim) == 835.038
    assert r9(res.ast_required) == 956.603619385
    assert r9(res.pt_provided) == 0.191320724
    assert r9(res.xu) == 46.235841604
    assert r9(res.xu_max) == 230.0


def test_verification_shear_case_04():
    """Pinned regression target: shear design with required reinforcement."""
    vu_kn = 150.0
    b_mm, d_mm = 230.0, 450.0
    fck_nmm2, fy_nmm2 = 20.0, 415.0
    asv_mm2 = 100.0
    pt_percent = 1.0

    res = shear.design_shear(
        vu_kn=vu_kn,
        b=b_mm,
        d=d_mm,
        fck=fck_nmm2,
        fy=fy_nmm2,
        asv=asv_mm2,
        pt=pt_percent,
    )

    assert res.is_safe is True

    assert r9(res.tv) == 1.449275362
    assert r9(res.tc) == 0.62
    assert r9(res.tc_max) == 2.8
    assert r9(res.vus) == 85.83
    assert r9(res.spacing) == 189.295700804


def test_verification_serviceability_deflection_case_05():
    """Pinned regression target: deflection span/depth check (simplified)."""
    res = serviceability.check_deflection_span_depth(
        span_mm=4000.0, d_mm=450.0, support_condition="simply_supported"
    )

    assert res.is_ok is True
    assert r9(res.computed["ld_ratio"]) == 8.888888889
    assert r9(res.computed["allowable_ld"]) == 20.0


def test_verification_serviceability_crack_width_case_06():
    """Pinned regression target: crack width check (Annex-F-style)."""
    res = serviceability.check_crack_width(
        exposure_class="moderate",
        limit_mm=0.3,
        acr_mm=50.0,
        cmin_mm=25.0,
        h_mm=500.0,
        x_mm=200.0,
        epsilon_m=0.001,
    )

    assert res.is_ok is True
    assert r9(res.computed["wcr_mm"]) == 0.128571429
    assert r9(res.computed["limit_mm"]) == 0.3


def test_verification_compliance_report_case_07():
    """Pinned regression target: end-to-end compliance report orchestration."""
    report = check_compliance_report(
        cases=[
            {"case_id": "C1", "mu_knm": 10.0, "vu_kn": 10.0},
            {"case_id": "C2", "mu_knm": 50.0, "vu_kn": 10.0},
        ],
        b_mm=230.0,
        D_mm=500.0,
        d_mm=450.0,
        fck_nmm2=25.0,
        fy_nmm2=500.0,
        asv_mm2=100.0,
        deflection_defaults={
            "span_mm": 4000.0,
            "d_mm": 450.0,
            "support_condition": "simply_supported",
        },
    )

    assert report.is_ok is True
    assert report.governing_case_id == "C2"
    assert r9(report.governing_utilization) == 0.444444444

    assert report.summary["num_cases"] == 2
    assert report.summary["governing_worst_check"] == "deflection"
    assert r9(report.summary["max_util_deflection"]) == 0.444444444
