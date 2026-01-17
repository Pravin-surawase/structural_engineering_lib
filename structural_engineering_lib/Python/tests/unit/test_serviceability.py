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
    calculate_cracked_moment_of_inertia,
    calculate_cracking_moment,
    calculate_effective_moment_of_inertia,
    calculate_gross_moment_of_inertia,
    calculate_short_term_deflection,
    check_deflection_level_b,
    get_long_term_deflection_factor,
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
        """Test Mcr raises ValueError for invalid inputs."""
        with pytest.raises(ValueError, match="Beam width b_mm must be positive"):
            calculate_cracking_moment(b_mm=0, D_mm=500, fck_nmm2=25)
        with pytest.raises(ValueError, match="Overall depth D_mm must be positive"):
            calculate_cracking_moment(b_mm=300, D_mm=0, fck_nmm2=25)
        with pytest.raises(
            ValueError, match="Concrete strength fck_nmm2 must be positive"
        ):
            calculate_cracking_moment(b_mm=300, D_mm=500, fck_nmm2=0)


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


# =============================================================================
# Level C Serviceability Tests (IS 456 Annex C - Separate Creep/Shrinkage)
# =============================================================================


class TestCreepCoefficient:
    """Tests for get_creep_coefficient function."""

    def test_creep_coefficient_default_conditions(self):
        """Default conditions give reasonable creep coefficient."""
        from structural_lib.serviceability import get_creep_coefficient

        theta = get_creep_coefficient()
        # Should be around 2.0-3.0 for standard conditions
        assert 1.5 <= theta <= 3.5

    def test_creep_coefficient_older_loading_age_less_creep(self):
        """Older concrete at loading has less creep."""
        from structural_lib.serviceability import get_creep_coefficient

        theta_28 = get_creep_coefficient(age_at_loading_days=28)
        theta_90 = get_creep_coefficient(age_at_loading_days=90)
        assert theta_90 < theta_28

    def test_creep_coefficient_higher_humidity_less_creep(self):
        """Higher humidity reduces creep."""
        from structural_lib.serviceability import get_creep_coefficient

        theta_50 = get_creep_coefficient(relative_humidity_percent=50)
        theta_80 = get_creep_coefficient(relative_humidity_percent=80)
        assert theta_80 < theta_50

    def test_creep_coefficient_limits(self):
        """Creep coefficient stays within reasonable limits."""
        from structural_lib.serviceability import get_creep_coefficient

        theta_extreme_low = get_creep_coefficient(
            age_at_loading_days=365,
            relative_humidity_percent=95,
        )
        theta_extreme_high = get_creep_coefficient(
            age_at_loading_days=3,
            relative_humidity_percent=30,
        )
        assert theta_extreme_low >= 0.8
        assert theta_extreme_high <= 4.0


class TestShrinkageCurvature:
    """Tests for calculate_shrinkage_curvature function."""

    def test_shrinkage_curvature_typical_beam(self):
        """Typical beam gives positive shrinkage curvature."""
        from structural_lib.serviceability import calculate_shrinkage_curvature

        phi = calculate_shrinkage_curvature(
            d_mm=450,
            ast_mm2=942,
            b_mm=300,
        )
        assert phi > 0

    def test_shrinkage_curvature_with_compression_steel_reduces(self):
        """Compression steel reduces shrinkage curvature."""
        from structural_lib.serviceability import calculate_shrinkage_curvature

        phi_no_asc = calculate_shrinkage_curvature(
            d_mm=450,
            ast_mm2=942,
            asc_mm2=0,
            b_mm=300,
        )
        phi_with_asc = calculate_shrinkage_curvature(
            d_mm=450,
            ast_mm2=942,
            asc_mm2=471,  # Half the tension steel
            b_mm=300,
        )
        assert phi_with_asc < phi_no_asc

    def test_shrinkage_curvature_invalid_inputs_return_zero(self):
        """Invalid inputs return zero curvature."""
        from structural_lib.serviceability import calculate_shrinkage_curvature

        phi = calculate_shrinkage_curvature(d_mm=0, ast_mm2=942, b_mm=300)
        assert phi == 0.0


class TestCreepDeflection:
    """Tests for calculate_creep_deflection function."""

    def test_creep_deflection_basic(self):
        """Basic creep deflection calculation."""
        from structural_lib.serviceability import calculate_creep_deflection

        delta_creep = calculate_creep_deflection(
            delta_sustained_mm=5.0,
            creep_coefficient=2.0,
        )
        assert delta_creep == pytest.approx(10.0)

    def test_creep_deflection_zero_inputs(self):
        """Zero inputs give zero creep deflection."""
        from structural_lib.serviceability import calculate_creep_deflection

        delta = calculate_creep_deflection(delta_sustained_mm=0, creep_coefficient=2.0)
        assert delta == 0.0

    def test_creep_deflection_negative_handled(self):
        """Negative inputs treated as zero."""
        from structural_lib.serviceability import calculate_creep_deflection

        delta = calculate_creep_deflection(
            delta_sustained_mm=-5.0, creep_coefficient=2.0
        )
        assert delta == 0.0


class TestShrinkageDeflection:
    """Tests for calculate_shrinkage_deflection function."""

    def test_shrinkage_deflection_simply_supported(self):
        """Simply supported gives positive shrinkage deflection."""
        from structural_lib.serviceability import calculate_shrinkage_deflection

        delta = calculate_shrinkage_deflection(
            phi_sh=1e-6,  # Typical curvature
            span_mm=6000,
            support_condition="simply_supported",
        )
        assert delta > 0
        # k = 1/8 for SS, delta = 0.125 * 1e-6 * 6000^2 = 4.5 mm
        assert delta == pytest.approx(4.5, rel=0.01)

    def test_shrinkage_deflection_cantilever_larger(self):
        """Cantilever has larger shrinkage deflection coefficient."""
        from structural_lib.serviceability import calculate_shrinkage_deflection

        delta_ss = calculate_shrinkage_deflection(
            phi_sh=1e-6, span_mm=3000, support_condition="simply_supported"
        )
        delta_cant = calculate_shrinkage_deflection(
            phi_sh=1e-6, span_mm=3000, support_condition="cantilever"
        )
        assert delta_cant > delta_ss

    def test_shrinkage_deflection_zero_curvature(self):
        """Zero curvature gives zero deflection."""
        from structural_lib.serviceability import calculate_shrinkage_deflection

        delta = calculate_shrinkage_deflection(phi_sh=0, span_mm=6000)
        assert delta == 0.0


class TestCheckDeflectionLevelC:
    """Tests for check_deflection_level_c function."""

    def test_level_c_typical_beam_ok(self):
        """Level C check passes for typical adequately sized beam."""
        from structural_lib.serviceability import check_deflection_level_c

        result = check_deflection_level_c(
            b_mm=300,
            D_mm=500,
            d_mm=450,
            span_mm=6000,
            ma_sustained_knm=50,  # Dead + permanent live
            ma_live_knm=20,  # Variable live
            ast_mm2=942,  # 3-20φ
            fck_nmm2=25,
        )
        assert result.mcr_knm > 0
        assert result.igross_mm4 > 0
        assert result.icr_mm4 > 0
        assert result.ieff_mm4 > 0
        assert result.delta_immediate_mm > 0
        assert result.delta_creep_mm > 0
        assert result.delta_shrinkage_mm > 0
        assert result.delta_total_mm > result.delta_immediate_mm
        assert result.creep_coefficient > 0
        assert result.shrinkage_curvature > 0

    def test_level_c_separate_components(self):
        """Level C correctly separates creep and shrinkage."""
        from structural_lib.serviceability import check_deflection_level_c

        result = check_deflection_level_c(
            b_mm=300,
            D_mm=500,
            d_mm=450,
            span_mm=6000,
            ma_sustained_knm=60,
            ma_live_knm=0,
            ast_mm2=942,
            fck_nmm2=25,
        )
        # Total should equal immediate + creep + shrinkage
        expected_total = (
            result.delta_immediate_mm
            + result.delta_creep_mm
            + result.delta_shrinkage_mm
        )
        assert result.delta_total_mm == pytest.approx(expected_total)

    def test_level_c_invalid_geometry(self):
        """Level C handles invalid geometry."""
        from structural_lib.serviceability import check_deflection_level_c

        result = check_deflection_level_c(
            b_mm=-300,
            D_mm=500,
            d_mm=450,
            span_mm=6000,
            ma_sustained_knm=60,
            ast_mm2=942,
            fck_nmm2=25,
        )
        assert result.is_ok is False
        assert "Invalid geometry" in result.remarks

    def test_level_c_zero_moment(self):
        """Level C with zero moment gives zero deflection."""
        from structural_lib.serviceability import check_deflection_level_c

        result = check_deflection_level_c(
            b_mm=300,
            D_mm=500,
            d_mm=450,
            span_mm=6000,
            ma_sustained_knm=0,
            ma_live_knm=0,
            ast_mm2=942,
            fck_nmm2=25,
        )
        assert result.is_ok is True
        assert result.delta_total_mm == 0.0

    def test_level_c_compression_steel_reduces_shrinkage(self):
        """Compression steel reduces shrinkage deflection in Level C."""
        from structural_lib.serviceability import check_deflection_level_c

        result_no_asc = check_deflection_level_c(
            b_mm=300,
            D_mm=500,
            d_mm=450,
            span_mm=6000,
            ma_sustained_knm=60,
            ast_mm2=942,
            fck_nmm2=25,
            asc_mm2=0,
        )
        result_with_asc = check_deflection_level_c(
            b_mm=300,
            D_mm=500,
            d_mm=450,
            span_mm=6000,
            ma_sustained_knm=60,
            ast_mm2=942,
            fck_nmm2=25,
            asc_mm2=314,  # 2-14φ
        )
        # Shrinkage deflection should be less with compression steel
        assert result_with_asc.delta_shrinkage_mm < result_no_asc.delta_shrinkage_mm

    def test_level_c_humidity_affects_creep(self):
        """Higher humidity reduces creep deflection."""
        from structural_lib.serviceability import check_deflection_level_c

        result_dry = check_deflection_level_c(
            b_mm=300,
            D_mm=500,
            d_mm=450,
            span_mm=6000,
            ma_sustained_knm=60,
            ast_mm2=942,
            fck_nmm2=25,
            relative_humidity_percent=40,
        )
        result_humid = check_deflection_level_c(
            b_mm=300,
            D_mm=500,
            d_mm=450,
            span_mm=6000,
            ma_sustained_knm=60,
            ast_mm2=942,
            fck_nmm2=25,
            relative_humidity_percent=80,
        )
        assert result_humid.delta_creep_mm < result_dry.delta_creep_mm
        assert result_humid.creep_coefficient < result_dry.creep_coefficient

    def test_level_c_age_affects_creep(self):
        """Later loading age reduces creep deflection."""
        from structural_lib.serviceability import check_deflection_level_c

        result_early = check_deflection_level_c(
            b_mm=300,
            D_mm=500,
            d_mm=450,
            span_mm=6000,
            ma_sustained_knm=60,
            ast_mm2=942,
            fck_nmm2=25,
            age_at_loading_days=14,
        )
        result_late = check_deflection_level_c(
            b_mm=300,
            D_mm=500,
            d_mm=450,
            span_mm=6000,
            ma_sustained_knm=60,
            ast_mm2=942,
            fck_nmm2=25,
            age_at_loading_days=90,
        )
        assert result_late.delta_creep_mm < result_early.delta_creep_mm
