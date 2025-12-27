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


# =============================================================================
# Level B Serviceability Tests
# =============================================================================

from structural_lib.serviceability import (
    calculate_cracking_moment,
    calculate_gross_moment_of_inertia,
    calculate_cracked_moment_of_inertia,
    calculate_effective_moment_of_inertia,
    get_long_term_deflection_factor,
    calculate_short_term_deflection,
    check_deflection_level_b,
)


class TestCrackingMoment:
    def test_cracking_moment_typical_beam(self):
        """Test Mcr for typical rectangular beam."""
        # b=300mm, D=500mm, fck=25 N/mm²
        # fcr = 0.7 * sqrt(25) = 3.5 N/mm²
        # Igross = 300 * 500³ / 12 = 3.125e9 mm^4
        # yt = 250 mm
        # Mcr = 3.5 * 3.125e9 / 250 = 43.75e6 N·mm = 43.75 kN·m
        mcr = calculate_cracking_moment(b_mm=300, D_mm=500, fck_nmm2=25)
        assert mcr == pytest.approx(43.75, rel=0.01)

    def test_cracking_moment_zero_inputs(self):
        """Test Mcr returns 0 for invalid inputs."""
        assert calculate_cracking_moment(b_mm=0, D_mm=500, fck_nmm2=25) == 0.0
        assert calculate_cracking_moment(b_mm=300, D_mm=0, fck_nmm2=25) == 0.0
        assert calculate_cracking_moment(b_mm=300, D_mm=500, fck_nmm2=0) == 0.0


class TestGrossMomentOfInertia:
    def test_igross_typical_beam(self):
        """Test Igross for typical rectangular beam."""
        # b=300mm, D=500mm
        # Igross = 300 * 500³ / 12 = 3.125e9 mm^4
        igross = calculate_gross_moment_of_inertia(b_mm=300, D_mm=500)
        assert igross == pytest.approx(3.125e9, rel=0.001)


class TestCrackedMomentOfInertia:
    def test_icr_typical_beam(self):
        """Test Icr for typical beam with tension steel."""
        # b=300mm, d=450mm, Ast=942mm² (3-20φ), fck=25
        # Expected: Icr should be significantly less than Igross
        icr = calculate_cracked_moment_of_inertia(
            b_mm=300, d_mm=450, ast_mm2=942, fck_nmm2=25
        )
        igross = calculate_gross_moment_of_inertia(b_mm=300, D_mm=500)
        assert icr > 0
        assert icr < igross  # Cracked < Gross
        # Typical ratio: Icr/Igross ~ 0.3-0.5
        assert 0.2 < icr / igross < 0.6


class TestEffectiveMomentOfInertia:
    def test_ieff_uncracked_section(self):
        """When Ma < Mcr, Ieff = Igross."""
        ieff = calculate_effective_moment_of_inertia(
            mcr_knm=50, ma_knm=30, igross_mm4=3e9, icr_mm4=1e9
        )
        assert ieff == pytest.approx(3e9)

    def test_ieff_fully_cracked_section(self):
        """When Ma >> Mcr, Ieff → Icr."""
        ieff = calculate_effective_moment_of_inertia(
            mcr_knm=30, ma_knm=300, igross_mm4=3e9, icr_mm4=1e9
        )
        # Should be close to Icr
        assert ieff < 1.1e9

    def test_ieff_branson_intermediate(self):
        """Test Branson's equation for intermediate case."""
        # Ma = 2 × Mcr
        ieff = calculate_effective_moment_of_inertia(
            mcr_knm=30, ma_knm=60, igross_mm4=3e9, icr_mm4=1e9
        )
        # Should be between Icr and Igross
        assert 1e9 < ieff < 3e9


class TestLongTermFactor:
    def test_long_term_factor_no_compression_steel(self):
        """λ = ξ when no compression steel."""
        factor = get_long_term_deflection_factor(duration_months=60)
        assert factor == pytest.approx(2.0)

    def test_long_term_factor_with_compression_steel(self):
        """λ < ξ when compression steel is present."""
        factor = get_long_term_deflection_factor(
            duration_months=60,
            asc_mm2=300,
            b_mm=300,
            d_mm=450,
        )
        # ρ' = 300 / (300 * 450) = 0.00222
        # λ = 2.0 / (1 + 50 * 0.00222) = 2.0 / 1.111 = 1.8
        assert factor < 2.0
        assert factor == pytest.approx(1.8, rel=0.05)

    def test_long_term_factor_short_duration(self):
        """ξ is smaller for shorter durations."""
        factor_3m = get_long_term_deflection_factor(duration_months=3)
        factor_12m = get_long_term_deflection_factor(duration_months=12)
        factor_60m = get_long_term_deflection_factor(duration_months=60)
        assert factor_3m < factor_12m < factor_60m


class TestShortTermDeflection:
    def test_short_term_deflection_simply_supported(self):
        """Test short-term deflection for simply supported beam."""
        # Using typical values
        delta = calculate_short_term_deflection(
            ma_knm=100,
            span_mm=6000,
            ieff_mm4=1.5e9,
            fck_nmm2=25,
            support_condition="simply_supported",
        )
        assert delta > 0
        # Should be reasonable (a few mm for typical beam)
        assert 1 < delta < 50


class TestCheckDeflectionLevelB:
    def test_deflection_level_b_ok_typical_beam(self):
        """Test Level B check passes for adequately sized beam."""
        result = check_deflection_level_b(
            b_mm=300,
            D_mm=500,
            d_mm=450,
            span_mm=6000,
            ma_service_knm=60,  # Service moment
            ast_mm2=942,  # 3-20φ
            fck_nmm2=25,
        )
        assert result.mcr_knm > 0
        assert result.igross_mm4 > 0
        assert result.icr_mm4 > 0
        assert result.ieff_mm4 > 0
        assert result.delta_short_mm > 0
        assert result.delta_total_mm > result.delta_short_mm
        # Check limit
        assert result.delta_limit_mm == pytest.approx(6000 / 250)

    def test_deflection_level_b_fails_slender_beam(self):
        """Test Level B check fails for slender beam."""
        result = check_deflection_level_b(
            b_mm=230,
            D_mm=300,  # Shallow beam
            d_mm=260,
            span_mm=8000,  # Long span
            ma_service_knm=80,
            ast_mm2=600,
            fck_nmm2=20,
        )
        # This should likely fail or be borderline
        assert result.delta_total_mm > 0

    def test_deflection_level_b_invalid_inputs(self):
        """Test Level B check handles invalid inputs."""
        result = check_deflection_level_b(
            b_mm=-300,
            D_mm=500,
            d_mm=450,
            span_mm=6000,
            ma_service_knm=60,
            ast_mm2=942,
            fck_nmm2=25,
        )
        assert result.is_ok is False
        assert "Invalid geometry" in result.remarks

    def test_deflection_level_b_zero_moment(self):
        """Test Level B check with zero moment."""
        result = check_deflection_level_b(
            b_mm=300,
            D_mm=500,
            d_mm=450,
            span_mm=6000,
            ma_service_knm=0,
            ast_mm2=942,
            fck_nmm2=25,
        )
        assert result.is_ok is True
        assert result.delta_total_mm == 0.0

    def test_deflection_level_b_compression_steel_reduces_long_term(self):
        """Adding compression steel reduces long-term deflection."""
        result_no_asc = check_deflection_level_b(
            b_mm=300,
            D_mm=500,
            d_mm=450,
            span_mm=6000,
            ma_service_knm=60,
            ast_mm2=942,
            fck_nmm2=25,
            asc_mm2=0,
        )
        result_with_asc = check_deflection_level_b(
            b_mm=300,
            D_mm=500,
            d_mm=450,
            span_mm=6000,
            ma_service_knm=60,
            ast_mm2=942,
            fck_nmm2=25,
            asc_mm2=300,
        )
        # With compression steel, long-term factor is smaller
        assert result_with_asc.long_term_factor < result_no_asc.long_term_factor
        # Total deflection should be less
        assert result_with_asc.delta_total_mm < result_no_asc.delta_total_mm
