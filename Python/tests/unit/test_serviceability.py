import pytest

from structural_lib.core.types import ExposureClass, SupportCondition
from structural_lib.serviceability import check_crack_width, check_deflection_span_depth


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


def test_deflection_support_condition_non_string_does_not_raise():
    res = check_deflection_span_depth(
        span_mm=4000.0, d_mm=500.0, support_condition=None
    )
    assert res.is_ok is True
    assert any("invalid support condition" in a.lower() for a in res.assumptions)


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
    assert res.computed["wcr_mm"] == pytest.approx(
        0.15 / res.computed["denom"], rel=1e-12
    )
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


def test_crack_width_exposure_class_non_string_does_not_raise():
    res = check_crack_width(exposure_class=None, limit_mm=0.3)
    assert res.is_ok is False
    assert any("invalid exposure class" in a.lower() for a in res.assumptions)


def test_deflection_support_condition_string_variants():
    res = check_deflection_span_depth(
        span_mm=4000.0,
        d_mm=500.0,
        support_condition="cant",
    )
    assert res.support_condition == SupportCondition.CANTILEVER

    res2 = check_deflection_span_depth(
        span_mm=4000.0,
        d_mm=500.0,
        support_condition="cont",
    )
    assert res2.support_condition == SupportCondition.CONTINUOUS


def test_crack_width_exposure_class_string_variants():
    res = check_crack_width(exposure_class="severe", limit_mm=0.2)
    assert res.exposure_class == ExposureClass.SEVERE

    res2 = check_crack_width(exposure_class="vs", limit_mm=0.2)
    assert res2.exposure_class == ExposureClass.VERY_SEVERE


# Source-qualified legacy scalar serviceability helpers. Full component
# benchmarks live in test_sls_annexc_equilibrium.py and its frozen fixture.
from structural_lib.serviceability import (
    calculate_cracked_moment_of_inertia,
    calculate_cracking_moment,
    calculate_effective_moment_of_inertia,
    calculate_gross_moment_of_inertia,
    calculate_short_term_deflection,
    calculate_shrinkage_curvature,
    calculate_shrinkage_deflection,
    check_deflection_level_b,
    check_deflection_level_c,
    get_creep_coefficient,
    get_long_term_deflection_factor,
)


def test_rectangular_cracking_and_gross_inertia_hand_anchor():
    assert calculate_cracking_moment(b_mm=300, D_mm=500, fck_nmm2=25) == pytest.approx(
        43.75, abs=1e-12
    )
    assert calculate_gross_moment_of_inertia(b_mm=300, D_mm=500) == 3125000000
    assert (
        calculate_cracked_moment_of_inertia(
            b_mm=300, d_mm=450, ast_mm2=1200, fck_nmm2=25
        )
        > 0
    )


@pytest.mark.parametrize(
    "kwargs",
    (
        {"b_mm": 0, "D_mm": 500, "fck_nmm2": 25},
        {"b_mm": 300, "D_mm": 0, "fck_nmm2": 25},
    ),
)
def test_cracking_moment_requires_section_dimensions(kwargs):
    with pytest.raises(ValueError):
        calculate_cracking_moment(**kwargs)


def test_annexc_inertia_requires_geometry_and_respects_source_bounds():
    values = {
        "mcr_knm": 40,
        "igross_mm4": 3000000000,
        "icr_mm4": 1000000000,
        "d_mm": 450,
        "x_mm": 150,
    }
    assert calculate_effective_moment_of_inertia(**values, ma_knm=20) == 3000000000
    # Direct C2.1: z/d=8/9, 1-x/d=2/3, Mr/M=.5.
    assert calculate_effective_moment_of_inertia(**values, ma_knm=80) == pytest.approx(
        1000000000 / (1.2 - 0.5 * (8 / 9) * (2 / 3)), rel=1e-14
    )
    assert calculate_effective_moment_of_inertia(**values, ma_knm=100000) == 1000000000


@pytest.mark.parametrize("moment", [60, -60])
def test_declared_ss_udl_deflection_hand_anchor(moment):
    # 5*M*L²/(48*Ec*Ig) with Ec25,000, Ig3.125e9.
    actual = calculate_short_term_deflection(
        ma_knm=moment, span_mm=6000, ieff_mm4=3125000000, fck_nmm2=25
    )
    assert actual == pytest.approx(2.88, abs=1e-12)


@pytest.mark.parametrize("moment", [60, -60])
def test_cantilever_end_point_deflection_from_virtual_work(moment):
    # Integrate P*(L-x)*(L-x)/(EI): P=M/L, giving ML²/(3EI).
    actual = calculate_short_term_deflection(
        ma_knm=moment,
        span_mm=3000,
        ieff_mm4=3125000000,
        fck_nmm2=25,
        support_condition="cantilever",
    )
    assert actual == pytest.approx(2.304, abs=1e-12)


def test_generic_continuous_support_has_no_inferred_load_pattern():
    with pytest.raises(ValueError, match="support/midspan"):
        calculate_short_term_deflection(
            ma_knm=60,
            span_mm=6000,
            ieff_mm4=3125000000,
            fck_nmm2=25,
            support_condition="continuous",
        )
    with pytest.raises(ValueError, match="support/midspan"):
        calculate_shrinkage_deflection(
            phi_sh=1e-6, span_mm=6000, support_condition="continuous"
        )


@pytest.mark.parametrize(("age", "theta"), [(7, 2.2), (28, 1.6), (365, 1.1)])
def test_source_default_ultimate_creep_anchors(age, theta):
    assert get_creep_coefficient(age_at_loading_days=age) == theta
    assert (
        get_creep_coefficient(
            age_at_loading_days=age, relative_humidity_percent=80, notional_size_mm=300
        )
        == theta
    )


@pytest.mark.parametrize("age", [3, 14, 90])
def test_default_creep_does_not_invent_age_interpolation(age):
    with pytest.raises(ValueError, match="no interpolation"):
        get_creep_coefficient(age_at_loading_days=age)


@pytest.mark.parametrize(
    ("ast", "asc", "factor"),
    [
        (675, 0, 0.72 * (0.5**0.5)),
        (1350, 0, 0.65),
        (4000, 0, 1),
        (1200, 600, 0.72 * (100 * 600 / 135000) / (100 * 1200 / 135000) ** 0.5),
    ],
)
def test_shrinkage_source_percentage_branches_and_cap(ast, asc, factor):
    phi = calculate_shrinkage_curvature(
        d_mm=450, D_mm=500, ast_mm2=ast, asc_mm2=asc, b_mm=300
    )
    assert phi == pytest.approx(factor * 0.0003 / 500, rel=1e-14)


@pytest.mark.parametrize(
    ("support", "coefficient"), [("simply_supported", 0.125), ("cantilever", 0.5)]
)
def test_uniform_shrinkage_deflection_source_support_coefficient(support, coefficient):
    assert calculate_shrinkage_deflection(
        phi_sh=1e-6, span_mm=6000, support_condition=support
    ) == pytest.approx(coefficient * 36, abs=1e-12)


def test_legacy_multiplier_is_compatibility_only():
    assert get_long_term_deflection_factor(duration_months=60) == 2
    assert get_long_term_deflection_factor(duration_months=12) == 1.4
    assert get_long_term_deflection_factor(
        duration_months=60, asc_mm2=300, b_mm=300, d_mm=450
    ) == pytest.approx(1.8)
    assert not hasattr(get_long_term_deflection_factor, "_is456_clauses")


def test_level_b_missing_long_term_basis_is_not_a_total_pass():
    result = check_deflection_level_b(
        b_mm=300,
        D_mm=500,
        d_mm=450,
        span_mm=6000,
        ma_service_knm=60,
        ast_mm2=942,
        fck_nmm2=25,
    )
    assert not result.is_ok
    assert result.delta_short_mm > 0
    assert result.computed["status"] == "HOLD_UNSUPPORTED"


def test_level_c_zero_load_retains_the_source_shrinkage_estimate():
    result = check_deflection_level_c(
        b_mm=300,
        D_mm=500,
        d_mm=450,
        span_mm=6000,
        ma_sustained_knm=0,
        ast_mm2=1200,
        fck_nmm2=25,
    )
    assert result.delta_immediate_mm == result.delta_creep_mm == 0
    assert result.delta_total_mm == result.delta_shrinkage_mm > 0
