import json
import math

import pytest

from structural_lib.compliance import check_compliance_report
from structural_lib.core.errors import CalculationError
from structural_lib.services.serialization import to_transport_value


def test_compliance_report_picks_governing_by_utilization():
    common = {
        "b_mm": 230.0,
        "D_mm": 500.0,
        "d_mm": 450.0,
        "fck_nmm2": 25.0,
        "fy_nmm2": 500.0,
    }

    cases = [
        {"case_id": "C1", "mu_knm": 10.0, "vu_kn": 10.0},
        {"case_id": "C2", "mu_knm": 50.0, "vu_kn": 10.0},
    ]

    report = check_compliance_report(
        cases=cases,
        asv_mm2=100.0,
        **common,
        deflection_defaults={
            "span_mm": 4000.0,
            "d_mm": 450.0,
            "support_condition": "simply_supported",
        },
    )

    assert report.governing_case_id == "C2"
    assert report.governing_utilization >= report.cases[0].governing_utilization
    assert report.summary["governing_case_id"] == "C2"
    assert report.summary["num_cases"] == 2


def test_compliance_report_failure_propagation_and_governing():
    # Make shear fail in the second case by pushing Vu high.
    common = {
        "b_mm": 230.0,
        "D_mm": 500.0,
        "d_mm": 450.0,
        "fck_nmm2": 20.0,
        "fy_nmm2": 415.0,
    }

    cases = [
        {"case_id": "OK1", "mu_knm": 20.0, "vu_kn": 10.0},
        {"case_id": "BAD_SHEAR", "mu_knm": 20.0, "vu_kn": 500.0},
    ]

    report = check_compliance_report(cases=cases, asv_mm2=100.0, **common)

    assert report.is_ok is False
    assert report.governing_case_id == "BAD_SHEAR"
    assert report.summary["num_failed_cases"] == 1
    assert report.summary["governing_worst_check"] in {
        "shear",
        "flexure",
        "deflection",
        "crack_width",
    }

    bad = [c for c in report.cases if c.case_id == "BAD_SHEAR"][0]
    assert bad.is_ok is False
    # Check that shear failure is in failed_checks
    # Format may include error details: "shear (tv exceeds tc_max)"
    assert any("shear" in check for check in bad.failed_checks)


def test_compliance_report_ok_when_all_checks_pass():
    common = {
        "b_mm": 300.0,
        "D_mm": 500.0,
        "d_mm": 450.0,
        "fck_nmm2": 25.0,
        "fy_nmm2": 500.0,
    }

    cases = [{"case_id": "SLS1", "mu_knm": 30.0, "vu_kn": 30.0}]

    report = check_compliance_report(
        cases=cases,
        asv_mm2=100.0,
        **common,
        deflection_defaults={
            "span_mm": 4000.0,
            "d_mm": 450.0,
            "support_condition": "simply_supported",
        },
        crack_width_defaults={
            "exposure_class": "moderate",
            "limit_mm": 0.3,
            "acr_mm": 50.0,
            "cmin_mm": 25.0,
            "h_mm": 500.0,
            "x_mm": 200.0,
            "epsilon_m": 0.001,
        },
    )

    assert report.is_ok is True
    assert report.governing_case_id == "SLS1"
    assert report.cases[0].is_ok is True

    # Compact summary row (Excel-friendly)
    assert report.summary["is_ok"] is True
    assert report.summary["governing_case_id"] == "SLS1"
    assert report.summary["num_cases"] == 1
    assert report.summary["max_util_flexure"] is not None
    assert report.summary["max_util_shear"] is not None
    assert report.summary["max_util_deflection"] is not None
    assert report.summary["max_util_crack_width"] is not None


def test_compliance_flexure_utilization_safe_doubly_is_one():
    # Mu above Mu_lim triggers doubly reinforced design, which can still be safe.
    # Utilization should not be >1 in a safe case.
    report = check_compliance_report(
        cases=[{"case_id": "DR", "mu_knm": 186.68109528, "vu_kn": 10.0}],
        b_mm=230.0,
        D_mm=500.0,
        d_mm=450.0,
        fck_nmm2=25.0,
        fy_nmm2=500.0,
        asv_mm2=100.0,
    )
    assert report.cases[0].flexure.is_safe is True
    assert report.cases[0].utilizations["flexure"] == 1.0


def test_unavailable_check_serializes_without_changing_failure_or_case_ranking():
    """The actual overloaded beam remains governing; no finite ratio is invented."""
    from structural_lib.compliance import report_to_dict

    report = check_compliance_report(
        cases=[
            {"case_id": "NOMINAL", "mu_knm": 150.0, "vu_kn": 75.0},
            {"case_id": "OVERLOADED", "mu_knm": 2000.0, "vu_kn": 75.0},
        ],
        b_mm=300.0,
        D_mm=500.0,
        d_mm=457.0,
        fck_nmm2=25.0,
        fy_nmm2=500.0,
        d_dash_mm=43.0,
    )
    failed = report.cases[1]
    assert report.is_ok is False
    assert report.governing_case_id == "OVERLOADED"
    assert math.isinf(failed.governing_utilization)
    assert failed.utilizations["flexure"] == pytest.approx(2000 / 209.2762215144)
    assert any("Table 19" in check for check in failed.failed_checks)

    payload = report_to_dict(report)
    transported = to_transport_value(report)
    assert transported["governing_utilization"] is None
    assert transported["cases"][1]["utilizations"]["shear"] is None
    assert json.loads(json.dumps(transported, allow_nan=False)) == transported
    assert json.loads(json.dumps(payload, allow_nan=False)) == payload
    assert payload["is_ok"] is False
    assert payload["governing_case_id"] == "OVERLOADED"
    assert payload["governing_utilization"] is None
    assert payload["summary"]["max_util_shear"] is None
    assert payload["summary"]["governing_worst_utilization"] is None
    assert payload["cases"][1]["utilizations"]["shear"] is None
    assert (
        "Table 19"
        in payload["cases"][1]["unavailable_utilizations"]["utilizations.shear"][
            "reason"
        ]
    )
    assert payload["cases"][1]["failed_checks"] == failed.failed_checks
    assert failed.governing_utilization == math.inf  # native compatibility preserved


@pytest.mark.parametrize("invalid", [math.nan, -math.inf, math.inf])
def test_unexplained_nonfinite_ratio_is_still_a_calculation_error(invalid):
    report = check_compliance_report(
        cases=[{"case_id": "NOMINAL", "mu_knm": 150.0, "vu_kn": 75.0}],
        b_mm=300.0,
        D_mm=500.0,
        d_mm=457.0,
        fck_nmm2=25.0,
        fy_nmm2=500.0,
        d_dash_mm=43.0,
    )
    report.cases[0].utilizations["shear"] = invalid
    with pytest.raises(CalculationError, match="unexplained non-finite"):
        to_transport_value(report)
