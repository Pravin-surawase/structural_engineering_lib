import pytest

from structural_lib import check_compliance_report as check_public_compliance_report
from structural_lib.compliance import check_compliance_case, check_compliance_report

COMMON = {
    "b_mm": 230.0,
    "D_mm": 500.0,
    "d_mm": 450.0,
    "fck_nmm2": 25.0,
    "fy_nmm2": 500.0,
    "asv_mm2": 100.0,
}


def test_public_compliance_report_rejects_empty_cases():
    with pytest.raises(ValueError, match="at least one compliance case"):
        check_public_compliance_report(cases=[], **COMMON)


@pytest.mark.parametrize("invalid", [float("nan"), float("inf"), float("-inf"), True])
def test_compliance_case_rejects_non_finite_actions_before_calculation(invalid):
    with pytest.raises(ValueError, match="mu_knm must be a finite real number"):
        check_compliance_case(
            case_id="NONFINITE",
            mu_knm=invalid,
            vu_kn=20.0,
            **COMMON,
        )


@pytest.mark.parametrize("field", ["pt_percent", "ast_mm2_for_shear"])
def test_compliance_case_rejects_non_finite_optional_shear_inputs(field):
    kwargs = {
        "case_id": "NONFINITE_OPTIONAL",
        "mu_knm": 20.0,
        "vu_kn": 20.0,
        **COMMON,
        field: float("nan"),
    }
    with pytest.raises(ValueError, match=field):
        check_compliance_case(**kwargs)


def test_public_compliance_report_rejects_numeric_text_nan():
    with pytest.raises(ValueError, match="mu_knm must be a finite real number"):
        check_public_compliance_report(
            cases=[{"case_id": "TEXT_NAN", "mu_knm": "nan", "vu_kn": 20.0}],
            **COMMON,
        )


def test_compliance_report_handles_bad_deflection_defaults_without_crashing():
    # Missing required keys like span_mm should not crash the report.
    common = {
        "b_mm": 230.0,
        "D_mm": 500.0,
        "d_mm": 450.0,
        "fck_nmm2": 25.0,
        "fy_nmm2": 500.0,
    }
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
    common = {
        "b_mm": 230.0,
        "D_mm": 500.0,
        "d_mm": 450.0,
        "fck_nmm2": 25.0,
        "fy_nmm2": 500.0,
    }
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
    common = {
        "b_mm": 230.0,
        "D_mm": 500.0,
        "d_mm": 450.0,
        "fck_nmm2": 25.0,
        "fy_nmm2": 500.0,
    }

    with pytest.raises(ValueError, match="Each case must be a dict"):
        check_compliance_report(
            cases=["not-a-dict"],
            asv_mm2=100.0,
            **common,
        )


def test_compliance_report_assigns_default_case_id_when_missing():
    common = {
        "b_mm": 230.0,
        "D_mm": 500.0,
        "d_mm": 450.0,
        "fck_nmm2": 25.0,
        "fy_nmm2": 500.0,
    }

    report = check_compliance_report(
        cases=[{"mu_knm": 20.0, "vu_kn": 20.0}],
        asv_mm2=100.0,
        **common,
    )

    assert report.cases[0].case_id == "CASE_1"
