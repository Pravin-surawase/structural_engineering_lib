from structural_lib.core.errors import Severity
from structural_lib.insights import quick_precheck


def test_precheck_deflection_risk():
    result = quick_precheck(
        span_mm=6000,
        b_mm=230,
        d_mm=250,
        D_mm=300,
        mu_knm=120,
        fck_nmm2=25,
    )
    assert any(w.type == "deflection_risk" for w in result.warnings)
    assert result.risk_level in {"MEDIUM", "HIGH"}


def test_precheck_normal_beam():
    result = quick_precheck(
        span_mm=5000,
        b_mm=300,
        d_mm=450,
        D_mm=500,
        mu_knm=120,
        fck_nmm2=25,
    )
    assert result.risk_level == "LOW"
    assert result.warnings == []


def test_precheck_no_error_severity():
    result = quick_precheck(
        span_mm=5000,
        b_mm=230,
        d_mm=450,
        D_mm=500,
        mu_knm=120,
        fck_nmm2=25,
    )
    assert all(w.severity != Severity.ERROR for w in result.warnings)
