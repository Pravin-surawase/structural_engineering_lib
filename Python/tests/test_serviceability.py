import pytest

from structural_lib.serviceability import check_crack_width, check_deflection_span_depth
from structural_lib.types import ExposureClass, SupportCondition


def test_deflection_ok_simple_defaults_recorded():
    res = check_deflection_span_depth(
        span_mm=4000.0,
        d_mm=500.0,
        support_condition=SupportCondition.SIMPLY_SUPPORTED,
    )
    assert res.is_ok is True
    assert res.computed["ld_ratio"] == pytest.approx(8.0)
    assert res.computed["allowable_ld"] > res.computed["ld_ratio"]
    assert any("default base allowable" in a.lower() for a in res.assumptions)


def test_deflection_not_ok_when_span_depth_exceeds_allowable():
    res = check_deflection_span_depth(
        span_mm=4000.0,
        d_mm=100.0,
        support_condition="simply_supported",
        base_allowable_ld=20.0,
        mf_tension_steel=1.0,
        mf_compression_steel=1.0,
        mf_flanged=1.0,
    )
    assert res.is_ok is False
    assert "NOT OK" in res.remarks
    assert res.computed["ld_ratio"] == pytest.approx(40.0)
    assert res.computed["allowable_ld"] == pytest.approx(20.0)


def test_deflection_invalid_inputs_fail_gracefully():
    res = check_deflection_span_depth(span_mm=-1.0, d_mm=450.0)
    assert res.is_ok is False
    assert "Invalid input" in res.remarks


def test_crack_width_requires_core_parameters_or_fails():
    res = check_crack_width(exposure_class=ExposureClass.MODERATE, limit_mm=0.3)
    assert res.is_ok is False
    assert "Missing" in res.remarks


def test_crack_width_computation_with_explicit_strain_and_params():
    # Choose parameters to produce a stable, positive denominator.
    res = check_crack_width(
        exposure_class="moderate",
        limit_mm=0.3,
        acr_mm=50.0,
        cmin_mm=25.0,
        h_mm=500.0,
        x_mm=200.0,
        epsilon_m=0.001,
    )
    assert res.computed["denom"] > 0
    assert res.computed["wcr_mm"] == pytest.approx(0.15 / res.computed["denom"], rel=1e-12)
    assert res.is_ok is True


def test_crack_width_strain_estimated_from_service_stress():
    res = check_crack_width(
        exposure_class=ExposureClass.SEVERE,
        limit_mm=0.2,
        acr_mm=60.0,
        cmin_mm=30.0,
        h_mm=500.0,
        x_mm=200.0,
        fs_service_nmm2=200.0,
        es_nmm2=200000.0,
    )
    assert any("estimated epsilon_m" in a.lower() for a in res.assumptions)
    assert res.computed["epsilon_m"] == pytest.approx(0.001)


def test_crack_width_invalid_geometry_h_le_x_fails():
    res = check_crack_width(
        exposure_class=ExposureClass.MODERATE,
        limit_mm=0.3,
        acr_mm=50.0,
        cmin_mm=25.0,
        h_mm=200.0,
        x_mm=200.0,
        epsilon_m=0.001,
    )
    assert res.is_ok is False
    assert "h_mm > x_mm" in res.remarks
