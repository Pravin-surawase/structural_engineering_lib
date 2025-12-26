from structural_lib import api
from structural_lib import compliance
from structural_lib import serviceability
from structural_lib.types import (
    CrackWidthResult,
    DeflectionResult,
    ExposureClass,
    ShearResult,
    SupportCondition,
)


def test_api_get_library_version_package_not_found(monkeypatch):
    """Test fallback version when package metadata is unavailable."""

    def _raise(_name: str):
        raise api.PackageNotFoundError

    monkeypatch.setattr(api, "version", _raise)
    # Should return a valid semver string (don't hardcode specific version)
    result = api.get_library_version()
    assert isinstance(result, str)
    assert len(result.split(".")) >= 2  # At least X.Y format


def test_api_wrappers_exercise_serviceability_paths():
    d = api.check_deflection_span_depth(span_mm=4000.0, d_mm=450.0)
    assert d.is_ok is True

    c = api.check_crack_width(
        exposure_class="moderate",
        epsilon_m=0.001,
        acr_mm=50.0,
        cmin_mm=25.0,
        h_mm=500.0,
        x_mm=200.0,
    )
    assert c.exposure_class.name == "MODERATE"


def test_api_check_compliance_report_smoke():
    report = api.check_compliance_report(
        cases=[{"case_id": "C1", "mu_knm": 20.0, "vu_kn": 20.0}],
        b_mm=230.0,
        D_mm=500.0,
        d_mm=450.0,
        fck_nmm2=25.0,
        fy_nmm2=500.0,
        asv_mm2=100.0,
    )
    assert report.cases[0].case_id == "C1"


def test_serviceability_deflection_unknown_support_condition_records_assumption():
    res = serviceability.check_deflection_span_depth(
        span_mm=4000.0, d_mm=450.0, support_condition="weird"
    )
    assert any("Unknown support condition" in a for a in res.assumptions)


def test_serviceability_deflection_invalid_inputs():
    res = serviceability.check_deflection_span_depth(span_mm=0.0, d_mm=450.0)
    assert res.is_ok is False
    assert "Invalid input" in res.remarks


def test_serviceability_crack_width_missing_strain_inputs():
    res = serviceability.check_crack_width(exposure_class="mild")
    assert res.is_ok is False
    assert "Missing epsilon_m" in res.remarks


def test_serviceability_crack_width_missing_required_geometry_inputs():
    res = serviceability.check_crack_width(
        exposure_class="mild",
        epsilon_m=0.001,
        # missing acr/cmin/h/x
    )
    assert res.is_ok is False
    assert "Missing required inputs" in res.remarks


def test_serviceability_crack_width_invalid_geometry_h_le_x():
    res = serviceability.check_crack_width(
        exposure_class="mild",
        epsilon_m=0.001,
        acr_mm=50.0,
        cmin_mm=25.0,
        h_mm=200.0,
        x_mm=200.0,
    )
    assert res.is_ok is False
    assert "h_mm > x_mm" in res.remarks


def test_serviceability_crack_width_denom_nonpositive():
    res = serviceability.check_crack_width(
        exposure_class="mild",
        epsilon_m=0.001,
        acr_mm=1.0,
        cmin_mm=100.0,
        h_mm=101.0,
        x_mm=100.0,
    )
    assert res.is_ok is False
    assert "denominator" in res.remarks.lower()


def test_serviceability_as_dict_helper():
    d = serviceability.check_deflection_span_depth(span_mm=4000.0, d_mm=450.0)
    as_dict = serviceability._as_dict(d)
    assert as_dict["is_ok"] is True


def test_compliance_internal_utilization_safe_infinite():
    assert compliance._utilization_safe(1.0, 0.0) == float("inf")


def test_compliance_safe_wrappers_handle_type_error_exception_paths():
    # Force TypeError inside serviceability functions by passing incomplete dicts.
    d = compliance._safe_deflection_check({})
    assert d.is_ok is False
    assert "failed" in d.remarks.lower()

    c = compliance._safe_crack_width_check({})
    assert c.is_ok is False
    assert ("failed" in c.remarks.lower()) or ("missing" in c.remarks.lower())


def test_compliance_utilization_for_failed_deflection_and_crack_is_infinite():
    d = DeflectionResult(
        is_ok=False,
        remarks="bad",
        support_condition=SupportCondition.SIMPLY_SUPPORTED,
        assumptions=[],
        inputs={},
        computed={"ld_ratio": 1.0, "allowable_ld": 0.0},
    )
    assert compliance._compute_deflection_utilization(d) == float("inf")

    c = CrackWidthResult(
        is_ok=False,
        remarks="bad",
        exposure_class=ExposureClass.MODERATE,
        assumptions=[],
        inputs={},
        computed={"wcr_mm": 1.0, "limit_mm": 0.0},
    )
    assert compliance._compute_crack_utilization(c) == float("inf")


def test_compliance_shear_utilization_infinite_when_failed_and_tcmax_zero():
    sh = ShearResult(tv=1.0, tc=0.0, tc_max=0.0, vus=0.0, spacing=0.0, is_safe=False)
    assert compliance._compute_shear_utilization(sh) == float("inf")


def test_compliance_report_tie_break_by_case_order_is_deterministic():
    common = dict(b_mm=230.0, D_mm=500.0, d_mm=450.0, fck_nmm2=25.0, fy_nmm2=500.0)

    # Same actions -> same utilizations; governing should be first case.
    report = compliance.check_compliance_report(
        cases=[
            {"case_id": "A", "mu_knm": 20.0, "vu_kn": 20.0},
            {"case_id": "B", "mu_knm": 20.0, "vu_kn": 20.0},
        ],
        asv_mm2=100.0,
        **common,
    )

    assert report.governing_case_id == "A"
