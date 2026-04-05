"""Tests for IS 456:2000 common modules - stress_blocks, reinforcement, validation.

Covers stress_blocks.py (3 functions), reinforcement.py (4 functions),
and validation.py (2 functions).
Related: TASK-612
"""

from __future__ import annotations

import pytest

from structural_lib.codes.is456.common.constants import (
    FLANGE_STRESS_FACTOR,
    MAX_STEEL_RATIO,
    MIN_STEEL_FACTOR,
    STRESS_BLOCK_DEPTH,
    STRESS_BLOCK_FACTOR,
    STRESS_RATIO,
)
from structural_lib.codes.is456.common.reinforcement import (
    design_steel_stress,
    max_steel_area,
    min_steel_area,
    steel_force,
)
from structural_lib.codes.is456.common.stress_blocks import (
    concrete_compressive_force,
    concrete_moment_capacity,
    flange_compressive_force,
    steel_stress_from_strain,
    steel_stress_from_strain_5point,
)
from structural_lib.codes.is456.common.validation import (
    validate_beam_dimensions,
    validate_material_grades,
)
from structural_lib.codes.is456.materials import get_ec, get_fcr, get_xu_max_d
from structural_lib.core.errors import DimensionError, MaterialError
from structural_lib.services.api import _validate_plausibility, design_beam_is456

# ===========================================================================
# stress_blocks.py
# ===========================================================================


class TestConcreteCompressiveForce:
    """Tests for concrete_compressive_force() - IS 456 Cl. 38.1."""

    def test_standard_values(self):
        """Cu = 0.36 * 25 * 300 * 100 = 270000 N."""
        result = concrete_compressive_force(fck=25, b=300, xu=100)
        assert result == pytest.approx(270_000.0)

    def test_uses_stress_block_factor(self):
        """Verify the function uses STRESS_BLOCK_FACTOR constant."""
        result = concrete_compressive_force(fck=25, b=300, xu=100)
        expected = STRESS_BLOCK_FACTOR * 25 * 300 * 100
        assert result == expected

    def test_zero_xu_gives_zero_force(self):
        """Edge case: xu = 0 -> force = 0."""
        assert concrete_compressive_force(fck=25, b=300, xu=0) == 0.0

    def test_higher_fck_gives_higher_force(self):
        """Monotonicity: higher fck -> higher compressive force."""
        f1 = concrete_compressive_force(fck=20, b=300, xu=100)
        f2 = concrete_compressive_force(fck=30, b=300, xu=100)
        assert f2 > f1


class TestConcreteMomentCapacity:
    """Tests for concrete_moment_capacity() - IS 456 Cl. 38.1."""

    def test_standard_values(self):
        """Mu = 0.36 * 25 * 300 * 100 * (450 - 0.42 * 100)."""
        expected = 0.36 * 25 * 300 * 100 * (450 - 0.42 * 100)
        result = concrete_moment_capacity(fck=25, b=300, xu=100, d=450)
        assert result == pytest.approx(expected)

    def test_uses_both_constants(self):
        """Verify uses STRESS_BLOCK_FACTOR and STRESS_BLOCK_DEPTH."""
        result = concrete_moment_capacity(fck=25, b=300, xu=100, d=450)
        expected = (
            STRESS_BLOCK_FACTOR * 25 * 300 * 100 * (450 - STRESS_BLOCK_DEPTH * 100)
        )
        assert result == expected

    def test_zero_xu_gives_zero_moment(self):
        """Edge case: xu = 0 -> moment = 0."""
        assert concrete_moment_capacity(fck=25, b=300, xu=0, d=450) == 0.0

    def test_moment_increases_with_depth(self):
        """Monotonicity: larger d -> larger moment for same xu."""
        m1 = concrete_moment_capacity(fck=25, b=300, xu=100, d=400)
        m2 = concrete_moment_capacity(fck=25, b=300, xu=100, d=500)
        assert m2 > m1


class TestFlangeCompressiveForce:
    """Tests for flange_compressive_force() - IS 456 Annex G."""

    def test_standard_values(self):
        """Cf = 0.45 * 25 * (800 - 300) * 100 = 562500 N."""
        result = flange_compressive_force(fck=25, bf=800, bw=300, yf=100)
        expected = FLANGE_STRESS_FACTOR * 25 * (800 - 300) * 100
        assert result == pytest.approx(expected)

    def test_bf_equals_bw_gives_zero(self):
        """Edge case: bf == bw -> no flange overhang -> force = 0."""
        assert flange_compressive_force(fck=25, bf=300, bw=300, yf=100) == 0.0

    def test_zero_yf_gives_zero(self):
        """Edge case: yf = 0 -> force = 0."""
        assert flange_compressive_force(fck=25, bf=800, bw=300, yf=0) == 0.0

    def test_wider_flange_gives_higher_force(self):
        """Monotonicity: wider flange -> higher force."""
        f1 = flange_compressive_force(fck=25, bf=600, bw=300, yf=100)
        f2 = flange_compressive_force(fck=25, bf=900, bw=300, yf=100)
        assert f2 > f1


# ===========================================================================
# reinforcement.py
# ===========================================================================


class TestDesignSteelStress:
    """Tests for design_steel_stress() - IS 456 Cl. 36.1."""

    def test_fe415(self):
        """fd = 0.87 * 415 = 361.05 N/mm2."""
        assert design_steel_stress(415) == pytest.approx(361.05)

    def test_fe500(self):
        """fd = 0.87 * 500 = 435.0 N/mm2."""
        assert design_steel_stress(500) == pytest.approx(435.0)

    def test_fe250(self):
        """fd = 0.87 * 250 = 217.5 N/mm2."""
        assert design_steel_stress(250) == pytest.approx(217.5)

    def test_uses_stress_ratio(self):
        """Verify uses STRESS_RATIO constant."""
        result = design_steel_stress(415)
        assert result == STRESS_RATIO * 415


class TestSteelForce:
    """Tests for steel_force()."""

    def test_standard_values(self):
        """T = 0.87 * 415 * 1000 = 361050 N."""
        result = steel_force(fy=415, ast=1000)
        assert result == pytest.approx(361_050.0)

    def test_zero_area_gives_zero_force(self):
        assert steel_force(fy=415, ast=0) == 0.0

    def test_uses_stress_ratio(self):
        result = steel_force(fy=500, ast=800)
        assert result == STRESS_RATIO * 500 * 800


class TestMinSteelArea:
    """Tests for min_steel_area() - IS 456 Cl. 26.5.1.1."""

    def test_standard_values(self):
        """As_min = 0.85 * 300 * 450 / 415."""
        expected = MIN_STEEL_FACTOR * 300 * 450 / 415
        result = min_steel_area(b=300, d=450, fy=415)
        assert result == pytest.approx(expected)

    def test_higher_fy_gives_less_min_steel(self):
        """Monotonicity: higher fy -> less minimum steel required."""
        a1 = min_steel_area(b=300, d=450, fy=415)
        a2 = min_steel_area(b=300, d=450, fy=500)
        assert a2 < a1

    def test_fy_zero_raises(self):
        """fy = 0 should raise ValueError."""
        with pytest.raises(ValueError, match="fy must be > 0"):
            min_steel_area(b=300, d=450, fy=0)

    def test_fy_negative_raises(self):
        """fy < 0 should raise ValueError."""
        with pytest.raises(ValueError, match="fy must be > 0"):
            min_steel_area(b=300, d=450, fy=-415)


class TestMaxSteelArea:
    """Tests for max_steel_area() - IS 456 Cl. 26.5.1.1."""

    def test_standard_values(self):
        """As_max = 0.04 * 300 * 500 = 6000 mm2."""
        result = max_steel_area(b=300, D=500)
        assert result == pytest.approx(6000.0)

    def test_uses_max_steel_ratio(self):
        result = max_steel_area(b=300, D=500)
        assert result == MAX_STEEL_RATIO * 300 * 500

    def test_wider_beam_more_max_steel(self):
        """Monotonicity: wider beam -> higher max steel area."""
        a1 = max_steel_area(b=250, D=500)
        a2 = max_steel_area(b=350, D=500)
        assert a2 > a1


# ===========================================================================
# validation.py
# ===========================================================================


class TestValidateBeamDimensions:
    """Tests for validate_beam_dimensions()."""

    def test_valid_dimensions_no_raise(self):
        """Normal dimensions should not raise."""
        validate_beam_dimensions(300, 450)  # should not raise

    def test_zero_width_raises(self):
        with pytest.raises(DimensionError, match="width b must be > 0"):
            validate_beam_dimensions(0, 450)

    def test_negative_depth_raises(self):
        with pytest.raises(DimensionError, match="effective depth d must be > 0"):
            validate_beam_dimensions(300, -1)

    def test_both_invalid_catches_width_first(self):
        """When both are invalid, width is checked first."""
        with pytest.raises(DimensionError, match="width b must be > 0"):
            validate_beam_dimensions(-1, -1)

    def test_custom_label_in_error(self):
        """Custom label should appear in the error message."""
        with pytest.raises(DimensionError, match="column"):
            validate_beam_dimensions(0, 450, label="column")

    def test_very_small_positive_ok(self):
        """Tiny but positive dimensions should pass."""
        validate_beam_dimensions(0.001, 0.001)  # should not raise


class TestValidateMaterialGrades:
    """Tests for validate_material_grades()."""

    def test_valid_grades_no_raise(self):
        """Standard IS 456 grades should not raise."""
        validate_material_grades(25, 415)  # should not raise

    def test_zero_fck_raises(self):
        with pytest.raises(MaterialError, match="fck must be > 0"):
            validate_material_grades(0, 415)

    def test_zero_fy_raises(self):
        with pytest.raises(MaterialError, match="fy must be > 0"):
            validate_material_grades(25, 0)

    def test_negative_fck_raises(self):
        with pytest.raises(MaterialError, match="fck must be > 0"):
            validate_material_grades(-5, 415)

    def test_negative_fy_raises(self):
        with pytest.raises(MaterialError, match="fy must be > 0"):
            validate_material_grades(25, -500)

    def test_non_standard_positive_grades_ok(self):
        """Non-standard but positive values should not raise (research use)."""
        validate_material_grades(28, 420)  # should not raise

    def test_both_invalid_catches_fck_first(self):
        """When both are invalid, fck is checked first."""
        with pytest.raises(MaterialError, match="fck must be > 0"):
            validate_material_grades(-5, -415)


# ===========================================================================
# steel_stress_from_strain() — bilinear model, IS 456 Fig. 23
# ===========================================================================


class TestSteelStressFromStrain:
    """Tests for bilinear steel stress-strain model (IS 456 Fig. 23)."""

    def test_zero_strain_gives_zero(self):
        """Zero strain should give zero stress."""
        result = steel_stress_from_strain(0.0, 415.0)
        assert result == 0.0

    def test_elastic_region_fe415(self):
        """Strain in elastic region: stress = E_s × strain."""
        # E_s = 200000, strain = 0.001 → stress = 200.0
        result = steel_stress_from_strain(0.001, 415.0)
        assert abs(result - 200.0) < 0.01

    def test_yield_plateau_fe415(self):
        """Strain beyond yield: stress = 0.87 × fy = 361.05."""
        result = steel_stress_from_strain(0.003, 415.0)
        assert abs(result - 361.05) < 0.01

    def test_exact_yield_strain_boundary_fe415(self):
        """At exactly yield strain, stress should equal f_yd."""
        # f_yd = 0.87 * 415 = 361.05
        # eps_yd = 361.05 / 200000 = 0.00180525
        eps_yd = 0.87 * 415.0 / 200000.0
        result = steel_stress_from_strain(eps_yd, 415.0)
        assert abs(result - 361.05) < 0.01

    def test_negative_strain_elastic(self):
        """Negative strain in elastic region: negative stress."""
        result = steel_stress_from_strain(-0.001, 415.0)
        assert abs(result - (-200.0)) < 0.01

    def test_negative_strain_yield(self):
        """Negative strain beyond yield: negative f_yd."""
        result = steel_stress_from_strain(-0.003, 415.0)
        assert abs(result - (-361.05)) < 0.01

    def test_fe500_yield_plateau(self):
        """Fe 500 steel: f_yd = 0.87 * 500 = 435.0."""
        result = steel_stress_from_strain(0.003, 500.0)
        assert abs(result - 435.0) < 0.01


# ===========================================================================
# steel_stress_from_strain_5point() — IS 456 Fig. 23 / SP:16 Table F
# TASK-642
# ===========================================================================

# Pre-computed SP:16 Table F data for Fe 415 and Fe 500
# stress_i = ratio_i × 0.87 × fy
# total_strain_i = inelastic_strain_i + stress_i / 200000
_ES = 200_000.0

# Fe 415 — 5 points
_FE415_FYD = 0.87 * 415  # 361.05
_FE415_POINTS = [
    # (ratio, inelastic_strain, expected_stress, expected_total_strain)
    (0.80, 0.0000, 0.80 * _FE415_FYD, 0.0000 + 0.80 * _FE415_FYD / _ES),
    (0.85, 0.0001, 0.85 * _FE415_FYD, 0.0001 + 0.85 * _FE415_FYD / _ES),
    (0.90, 0.0003, 0.90 * _FE415_FYD, 0.0003 + 0.90 * _FE415_FYD / _ES),
    (0.95, 0.0007, 0.95 * _FE415_FYD, 0.0007 + 0.95 * _FE415_FYD / _ES),
    (1.00, 0.0020, 1.00 * _FE415_FYD, 0.0020 + 1.00 * _FE415_FYD / _ES),
]

# Fe 500 — selected points
_FE500_FYD = 0.87 * 500  # 435.0
_FE500_POINT1 = (0.80, 0.0000, 0.80 * _FE500_FYD, 0.0000 + 0.80 * _FE500_FYD / _ES)
_FE500_POINT5 = (1.00, 0.0020, 1.00 * _FE500_FYD, 0.0020 + 1.00 * _FE500_FYD / _ES)


class TestSteelStress5Point:
    """Tests for steel_stress_from_strain_5point() — IS 456 Fig. 23 / SP:16 Table F.

    TASK-642: Comprehensive 6-type test coverage.
    """

    # -----------------------------------------------------------------------
    # 1. Unit tests — All 5 Fe 415 points (±0.1%)
    # -----------------------------------------------------------------------

    @pytest.mark.parametrize(
        "point_idx, ratio, inelastic, expected_stress, total_strain",
        [(i + 1, *p) for i, p in enumerate(_FE415_POINTS)],
        ids=[f"Fe415_Point{i+1}" for i in range(5)],
    )
    def test_fe415_all_5_points(
        self, point_idx, ratio, inelastic, expected_stress, total_strain
    ):
        """SP:16 Table F: Fe 415 point {point_idx} stress = {ratio} × 0.87 × 415."""
        result = steel_stress_from_strain_5point(total_strain, 415)
        assert result == pytest.approx(expected_stress, rel=0.001)

    def test_fe415_point1_exact_values(self):
        """SP:16 Table F: Fe 415 Point 1 — stress=288.84, strain≈0.00144."""
        stress = 0.80 * 0.87 * 415  # 288.84
        strain = 0.0 + stress / 200000  # 0.0014442
        result = steel_stress_from_strain_5point(strain, 415)
        assert result == pytest.approx(stress, rel=0.001)

    def test_fe415_point5_exact_values(self):
        """SP:16 Table F: Fe 415 Point 5 — stress=361.05, strain≈0.00380."""
        stress = 1.00 * 0.87 * 415  # 361.05
        strain = 0.0020 + stress / 200000  # 0.0038053
        result = steel_stress_from_strain_5point(strain, 415)
        assert result == pytest.approx(stress, rel=0.001)

    # -----------------------------------------------------------------------
    # 2. Edge cases — strain=0, large strain, exact boundaries
    # -----------------------------------------------------------------------

    def test_zero_strain_gives_zero(self):
        """Edge: strain=0 → stress=0."""
        assert steel_stress_from_strain_5point(0.0, 415) == 0.0

    def test_very_large_strain_gives_yield_plateau(self):
        """Edge: very large strain → plateau at 0.87*fy."""
        result = steel_stress_from_strain_5point(0.01, 415)
        assert result == pytest.approx(0.87 * 415, rel=0.001)

    def test_strain_at_yield_plateau(self):
        """Edge: strain far above Point 5 → f_yd."""
        result = steel_stress_from_strain_5point(0.05, 500)
        assert result == pytest.approx(0.87 * 500, rel=0.001)

    def test_strain_exactly_at_point1_boundary(self):
        """Edge: strain exactly at Point 1 total strain for Fe 415."""
        stress_1 = 0.80 * 0.87 * 415
        strain_1 = stress_1 / _ES
        result = steel_stress_from_strain_5point(strain_1, 415)
        assert result == pytest.approx(stress_1, rel=0.001)

    def test_strain_just_below_point1(self):
        """Edge: strain slightly below Point 1 → elastic response."""
        stress_1 = 0.80 * 0.87 * 415
        strain_1 = stress_1 / _ES
        strain_below = strain_1 * 0.5
        result = steel_stress_from_strain_5point(strain_below, 415)
        expected = _ES * strain_below
        assert result == pytest.approx(expected, rel=0.001)

    # -----------------------------------------------------------------------
    # 3. Degenerate cases — tiny strain, interpolation between points
    # -----------------------------------------------------------------------

    def test_very_small_strain_elastic(self):
        """Degenerate: strain=1e-10 → elastic (E_s × strain)."""
        strain = 1e-10
        result = steel_stress_from_strain_5point(strain, 415)
        expected = _ES * strain  # 0.00002 N/mm²
        assert result == pytest.approx(expected, rel=0.001)

    def test_interpolation_between_point2_and_point3_fe415(self):
        """Interpolation: strain 0.00178 between Points 2 and 3 for Fe 415.

        Point 2: strain=0.0001 + 0.85*361.05/200000 ≈ 0.001634
                 stress=0.85*361.05 = 306.8925
        Point 3: strain=0.0003 + 0.90*361.05/200000 ≈ 0.001925
                 stress=0.90*361.05 = 324.945
        At strain=0.00178: t = (0.00178 - 0.001634) / (0.001925 - 0.001634)
        """
        strain_test = 0.00178
        # Compute point 2 and 3 values
        s2 = 0.85 * 0.87 * 415
        e2 = 0.0001 + s2 / _ES
        s3 = 0.90 * 0.87 * 415
        e3 = 0.0003 + s3 / _ES
        t = (strain_test - e2) / (e3 - e2)
        expected = s2 + t * (s3 - s2)
        result = steel_stress_from_strain_5point(strain_test, 415)
        assert result == pytest.approx(expected, rel=0.005)

    def test_interpolation_midpoint_between_point4_and_point5(self):
        """Degenerate: midpoint between Points 4 and 5 for Fe 415."""
        s4 = 0.95 * 0.87 * 415
        e4 = 0.0007 + s4 / _ES
        s5 = 1.00 * 0.87 * 415
        e5 = 0.0020 + s5 / _ES
        strain_mid = (e4 + e5) / 2
        t = (strain_mid - e4) / (e5 - e4)
        expected = s4 + t * (s5 - s4)
        result = steel_stress_from_strain_5point(strain_mid, 415)
        assert result == pytest.approx(expected, rel=0.005)

    # -----------------------------------------------------------------------
    # 4. SP:16 benchmark — golden tests (±0.1%)
    # -----------------------------------------------------------------------

    @pytest.mark.golden
    def test_sp16_table_f_fe415_point5(self):
        """GOLDEN: SP:16 Table F — Fe 415 Point 5.
        Source: SP:16:1980, Table F
        Values: fy=415, ratio=1.00, stress=361.05, total_strain≈0.003805
        """
        stress = 1.00 * 0.87 * 415
        strain = 0.0020 + stress / _ES
        result = steel_stress_from_strain_5point(strain, 415)
        assert result == pytest.approx(stress, rel=0.001)

    @pytest.mark.golden
    def test_sp16_table_f_fe500_point5(self):
        """GOLDEN: SP:16 Table F — Fe 500 Point 5.
        Source: SP:16:1980, Table F
        Values: fy=500, ratio=1.00, stress=435.0, total_strain≈0.004175
        """
        stress = 1.00 * 0.87 * 500
        strain = 0.0020 + stress / _ES
        result = steel_stress_from_strain_5point(strain, 500)
        assert result == pytest.approx(stress, rel=0.001)

    @pytest.mark.golden
    def test_sp16_table_f_fe500_point1(self):
        """GOLDEN: SP:16 Table F — Fe 500 Point 1.
        Source: SP:16:1980, Table F
        Values: fy=500, ratio=0.80, stress=348.0, total_strain≈0.00174
        """
        stress = 0.80 * 0.87 * 500
        strain = 0.0 + stress / _ES
        result = steel_stress_from_strain_5point(strain, 500)
        assert result == pytest.approx(stress, rel=0.001)

    # -----------------------------------------------------------------------
    # 5. Sign preservation — negative strain → negative stress
    # -----------------------------------------------------------------------

    def test_negative_strain_gives_negative_stress(self):
        """Sign: negative strain (tension) → negative stress."""
        strain = -0.003
        result = steel_stress_from_strain_5point(strain, 415)
        assert result < 0.0

    def test_positive_strain_gives_positive_stress(self):
        """Sign: positive strain (compression) → positive stress."""
        strain = 0.003
        result = steel_stress_from_strain_5point(strain, 415)
        assert result > 0.0

    def test_negative_strain_same_magnitude_as_positive(self):
        """Sign: |stress(-strain)| == |stress(+strain)|."""
        strain = 0.002
        pos = steel_stress_from_strain_5point(strain, 415)
        neg = steel_stress_from_strain_5point(-strain, 415)
        assert abs(neg) == pytest.approx(abs(pos))

    def test_negative_strain_at_each_point(self):
        """Sign: negative strain at each Fe 415 point gives negative stress."""
        for _, _, expected_stress, total_strain in _FE415_POINTS:
            result = steel_stress_from_strain_5point(-total_strain, 415)
            assert result == pytest.approx(-expected_stress, rel=0.001)

    # -----------------------------------------------------------------------
    # 6. Monotonicity — increasing |strain| → non-decreasing |stress|
    # -----------------------------------------------------------------------

    def test_monotonicity_positive_strains(self):
        """Monotonicity: increasing strain → non-decreasing stress."""
        strains = [0.0005, 0.001, 0.0015, 0.002, 0.0025, 0.003, 0.004, 0.005]
        stresses = [steel_stress_from_strain_5point(s, 415) for s in strains]
        for i in range(len(stresses) - 1):
            assert stresses[i + 1] >= stresses[i], (
                f"Monotonicity violated: stress({strains[i+1]})={stresses[i+1]} "
                f"< stress({strains[i]})={stresses[i]}"
            )

    def test_monotonicity_negative_strains(self):
        """Monotonicity: increasing |negative strain| → non-decreasing |stress|."""
        strains = [-0.0005, -0.001, -0.0015, -0.002, -0.0025, -0.003, -0.004]
        stresses = [steel_stress_from_strain_5point(s, 415) for s in strains]
        abs_stresses = [abs(s) for s in stresses]
        for i in range(len(abs_stresses) - 1):
            assert (
                abs_stresses[i + 1] >= abs_stresses[i]
            ), "Monotonicity violated for negative strains"

    def test_monotonicity_fe500(self):
        """Monotonicity: Fe 500 — increasing strain → non-decreasing stress."""
        strains = [0.0005, 0.001, 0.002, 0.003, 0.004, 0.005, 0.01]
        stresses = [steel_stress_from_strain_5point(s, 500) for s in strains]
        for i in range(len(stresses) - 1):
            assert stresses[i + 1] >= stresses[i]

    # -----------------------------------------------------------------------
    # Additional: 5-point vs bilinear divergence in transition zone
    # -----------------------------------------------------------------------

    def test_5point_differs_from_bilinear_in_transition(self):
        """5-point curve gives different results than bilinear in transition zone.

        In the transition zone between elastic and yield, the 5-point model
        diverges from the simpler bilinear model.
        """
        # Pick a strain in the transition zone (between point 1 and point 5)
        s3 = 0.90 * 0.87 * 415
        strain_transition = 0.0003 + s3 / _ES  # Point 3 strain

        result_5pt = steel_stress_from_strain_5point(strain_transition, 415)
        result_bilinear = steel_stress_from_strain(strain_transition, 415)

        # The bilinear model should already be at yield plateau at this strain
        # while 5-point gives 0.90 × f_yd (lower)
        assert result_5pt == pytest.approx(s3, rel=0.001)
        # Bilinear at this strain should be at f_yd (0.87*415 = 361.05)
        assert result_bilinear == pytest.approx(0.87 * 415, rel=0.001)
        # They are different in the transition zone
        assert abs(result_5pt - result_bilinear) > 1.0


# ===========================================================================
# SM-1: fck=0 / fy=0 rejection guards
# ===========================================================================


class TestGetEcZeroGuard:
    """SM-1: get_ec must reject fck <= 0."""

    def test_fck_zero_raises(self):
        """get_ec(0) must raise ValueError — division by zero guard."""
        with pytest.raises(ValueError, match="fck must be positive"):
            get_ec(0)

    def test_fck_negative_raises(self):
        """get_ec(-5) must raise ValueError."""
        with pytest.raises(ValueError, match="fck must be positive"):
            get_ec(-5)


class TestGetFcrZeroGuard:
    """SM-1: get_fcr must reject fck <= 0."""

    def test_fck_zero_raises(self):
        """get_fcr(0) must raise ValueError — sqrt(0) guard."""
        with pytest.raises(ValueError, match="fck must be positive"):
            get_fcr(0)

    def test_fck_negative_raises(self):
        """get_fcr(-5) must raise ValueError."""
        with pytest.raises(ValueError, match="fck must be positive"):
            get_fcr(-5)


class TestValidatePlausibilityZeroGuards:
    """SM-1: _validate_plausibility must reject zero/negative fck and fy."""

    def test_fck_zero_raises(self):
        """fck=0 must raise ValueError."""
        with pytest.raises(ValueError, match="fck_nmm2=0"):
            _validate_plausibility(fck_nmm2=0)

    def test_fck_negative_raises(self):
        """fck=-5 must raise ValueError."""
        with pytest.raises(ValueError, match="fck_nmm2=-5"):
            _validate_plausibility(fck_nmm2=-5)

    def test_fy_zero_raises(self):
        """fy=0 must raise ValueError."""
        with pytest.raises(ValueError, match="fy_nmm2=0"):
            _validate_plausibility(fy_nmm2=0)


# ===========================================================================
# UX-01: _validate_plausibility rejects d_mm >= D_mm
# ===========================================================================


class TestValidatePlausibilityDepthGuards:
    """UX-01: _validate_plausibility must reject d_mm >= D_mm."""

    def test_d_mm_greater_than_depth_raises(self):
        """UX-01: d_mm > D_mm must raise ValueError."""
        with pytest.raises(ValueError, match="must be less than overall depth"):
            _validate_plausibility(d_mm=500, D_mm=400)

    def test_d_mm_equal_to_overall_depth_raises(self):
        """UX-01: d_mm == D_mm must also raise (zero cover impossible)."""
        with pytest.raises(ValueError, match="must be less than overall depth"):
            _validate_plausibility(d_mm=400, D_mm=400)

    def test_d_mm_less_than_overall_depth_passes(self):
        """Normal case: d_mm < D_mm should not raise."""
        _validate_plausibility(d_mm=450, D_mm=500)  # Should not raise

    def test_d_mm_only_no_overall_depth_passes(self):
        """d_mm alone (no D_mm) should not raise."""
        _validate_plausibility(d_mm=450)  # Should not raise

    def test_overall_depth_only_no_d_mm_passes(self):
        """D_mm alone (no d_mm) should not raise."""
        _validate_plausibility(D_mm=500)  # Should not raise


# ===========================================================================
# UX-01: design_beam_is456 integration — d_mm >= D_mm rejected
# ===========================================================================


class TestDesignBeamDepthValidation:
    """UX-01: design_beam_is456 must reject d_mm >= D_mm at the API level."""

    def test_design_beam_rejects_d_greater_than_overall_depth(self):
        """UX-01: d_mm > D_mm must raise ValueError, not return Ast=0 silently."""
        with pytest.raises(ValueError, match="must be less than overall depth"):
            design_beam_is456(
                units="IS456",
                b_mm=230,
                d_mm=500,
                D_mm=400,  # d > D — impossible
                mu_knm=100,
                vu_kn=50,
                fck_nmm2=25,
                fy_nmm2=500,
            )

    def test_design_beam_rejects_d_equal_to_overall_depth(self):
        """UX-01: d_mm == D_mm must also raise (zero cover impossible)."""
        with pytest.raises(ValueError, match="must be less than overall depth"):
            design_beam_is456(
                units="IS456",
                b_mm=230,
                d_mm=400,
                D_mm=400,  # d == D — no cover
                mu_knm=100,
                vu_kn=50,
                fck_nmm2=25,
                fy_nmm2=500,
            )

    def test_design_beam_accepts_valid_d_mm(self):
        """Normal case: d < D should work fine."""
        result = design_beam_is456(
            units="IS456",
            b_mm=230,
            d_mm=450,
            D_mm=500,  # d < D — valid
            mu_knm=100,
            vu_kn=50,
            fck_nmm2=25,
            fy_nmm2=500,
        )
        assert result is not None


# ===========================================================================
# SM-2: Float tolerance for fy dispatch in get_xu_max_d
# ===========================================================================


class TestXuMaxDFloatTolerance:
    """SM-2: get_xu_max_d uses abs(fy - grade) < 0.5 tolerance."""

    def test_fe415_tolerance_match(self):
        """414.999 should match Fe 415 -> 0.48."""
        assert get_xu_max_d(414.999) == get_xu_max_d(415.0)
        assert get_xu_max_d(414.999) == 0.48

    def test_fe500_tolerance_match(self):
        """499.7 should match Fe 500 -> 0.46."""
        assert get_xu_max_d(499.7) == get_xu_max_d(500.0)
        assert get_xu_max_d(499.7) == 0.46

    def test_fe415_outside_tolerance_general_formula(self):
        """416.0 is outside ±0.5 of 415 -> falls to general formula."""
        result = get_xu_max_d(416.0)
        expected = 700 / (1100 + 0.87 * 416.0)
        assert result == pytest.approx(expected)
        assert result != 0.48  # Not the Fe 415 table value
