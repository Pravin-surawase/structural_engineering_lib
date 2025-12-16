import pytest

from structural_lib.compliance import check_compliance_report


def test_compliance_report_handles_bad_deflection_defaults_without_crashing():
    # Missing required keys like span_mm should not crash the report.
    common = dict(b_mm=230.0, D_mm=500.0, d_mm=450.0, fck_nmm2=25.0, fy_nmm2=500.0)
    cases = [{"case_id": "C1", "mu_knm": 20.0, "vu_kn": 20.0}]

    report = check_compliance_report(
        cases=cases,
        asv_mm2=100.0,
        **common,
        deflection_defaults={"d_mm": 450.0},  # span_mm missing
    )

    assert report.is_ok is False
    assert report.cases[0].deflection is not None
    assert report.cases[0].deflection.is_ok is False
    assert "deflection" in report.cases[0].failed_checks


def test_compliance_report_handles_bad_crack_width_defaults_without_crashing():
    common = dict(b_mm=230.0, D_mm=500.0, d_mm=450.0, fck_nmm2=25.0, fy_nmm2=500.0)
    cases = [{"case_id": "C1", "mu_knm": 20.0, "vu_kn": 20.0}]

    report = check_compliance_report(
        cases=cases,
        asv_mm2=100.0,
        **common,
        crack_width_defaults={"epsilon_m": 0.001},  # missing geometry inputs
    )

    assert report.is_ok is False
    assert report.cases[0].crack_width is not None
    assert report.cases[0].crack_width.is_ok is False
    assert "crack_width" in report.cases[0].failed_checks


def test_compliance_report_rejects_non_dict_cases():
    common = dict(b_mm=230.0, D_mm=500.0, d_mm=450.0, fck_nmm2=25.0, fy_nmm2=500.0)

    with pytest.raises(ValueError, match="Each case must be a dict"):
        check_compliance_report(
            cases=["not-a-dict"],
            asv_mm2=100.0,
            **common,
        )


def test_compliance_report_assigns_default_case_id_when_missing():
    common = dict(b_mm=230.0, D_mm=500.0, d_mm=450.0, fck_nmm2=25.0, fy_nmm2=500.0)

    report = check_compliance_report(
        cases=[{"mu_knm": 20.0, "vu_kn": 20.0}],
        asv_mm2=100.0,
        **common,
    )

    assert report.cases[0].case_id == "CASE_1"
