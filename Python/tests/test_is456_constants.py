"""Tests for IS 456:2000 named design constants.

GOLDEN TESTS - these can never be deleted. Each constant is verified
against its IS 456 clause reference.
Related: TASK-613
"""

from __future__ import annotations

import pytest

from structural_lib.codes.is456.common.constants import (
    CONCRETE_EC_FACTOR,
    CONCRETE_FCR_FACTOR,
    FLANGE_STRESS_FACTOR,
    MAX_SPACING_FACTOR,
    MAX_SPACING_MM,
    MAX_STEEL_RATIO,
    MIN_CLEAR_COVER_MM,
    MIN_SHEAR_REINF_FACTOR,
    MIN_STEEL_FACTOR,
    SIDE_FACE_AREA_RATIO,
    SIDE_FACE_DEPTH_THRESHOLD_MM,
    STANDARD_BAR_DIAMETERS,
    STANDARD_STIRRUP_DIAMETERS,
    STANDARD_STIRRUP_SPACINGS,
    STRESS_BLOCK_DEPTH,
    STRESS_BLOCK_FACTOR,
    STRESS_BLOCK_PEAK,
    STRESS_RATIO,
    TORSION_MOMENT_DIVISOR,
    TORSION_SHEAR_FACTOR,
    XU_MAX_DENOM_BASE,
    XU_MAX_NUMERATOR,
)


@pytest.mark.golden
class TestIS456Constants:
    """GOLDEN: IS 456:2000 constant values - never delete these tests."""

    # --- Steel stress ratio --- IS 456 Cl. 36.1 ---

    def test_stress_ratio(self):
        """IS 456 Cl. 36.1: fd = 0.87 * fy (gamma_s = 1.15)."""
        assert STRESS_RATIO == 0.87

    # --- Rectangular stress-block --- IS 456 Cl. 38.1 ---

    def test_stress_block_factor(self):
        """IS 456 Cl. 38.1: Cu = 0.36 * fck * b * xu."""
        assert STRESS_BLOCK_FACTOR == 0.36

    def test_stress_block_depth(self):
        """IS 456 Cl. 38.1: centroid at 0.42 * xu from top."""
        assert STRESS_BLOCK_DEPTH == 0.42

    def test_stress_block_peak(self):
        """IS 456 Cl. 38.1: peak compressive stress = 0.446 * fck."""
        assert STRESS_BLOCK_PEAK == 0.446

    # --- Limiting neutral axis --- IS 456 Cl. 38.1 ---

    def test_xu_max_numerator(self):
        """IS 456 Cl. 38.1: xu_max/d = 700 / (1100 + 0.87*fy)."""
        assert XU_MAX_NUMERATOR == 700.0

    def test_xu_max_denom_base(self):
        """IS 456 Cl. 38.1: denominator base = 1100."""
        assert XU_MAX_DENOM_BASE == 1100.0

    # --- Flanged beam --- IS 456 Annex G ---

    def test_flange_stress_factor(self):
        """IS 456 Annex G, G-2.2: average flange stress = 0.45 * fck."""
        assert FLANGE_STRESS_FACTOR == 0.45

    # --- Reinforcement limits --- IS 456 Cl. 26.5.1.1 ---

    def test_min_steel_factor(self):
        """IS 456 Cl. 26.5.1.1: As_min = 0.85 * b * d / fy."""
        assert MIN_STEEL_FACTOR == 0.85

    def test_max_steel_ratio(self):
        """IS 456 Cl. 26.5.1.1: As_max = 0.04 * b * D."""
        assert MAX_STEEL_RATIO == 0.04

    # --- Stirrup spacing --- IS 456 Cl. 26.5.1.5 ---

    def test_max_spacing_factor(self):
        """IS 456 Cl. 26.5.1.5: s_max = 0.75 * d."""
        assert MAX_SPACING_FACTOR == 0.75

    def test_max_spacing_mm(self):
        """IS 456 Cl. 26.5.1.5: s_max <= 300 mm."""
        assert MAX_SPACING_MM == 300.0

    # --- Minimum shear reinforcement --- IS 456 Cl. 26.5.1.6 ---

    def test_min_shear_reinf_factor(self):
        """IS 456 Cl. 26.5.1.6: Asv/(b*sv) >= 0.4/(0.87*fy)."""
        assert MIN_SHEAR_REINF_FACTOR == 0.4

    # --- Torsion --- IS 456 Cl. 41.3.1, 41.4.2 ---

    def test_torsion_shear_factor(self):
        """IS 456 Cl. 41.3.1: Ve = Vu + 1.6 * Tu/b."""
        assert TORSION_SHEAR_FACTOR == 1.6

    def test_torsion_moment_divisor(self):
        """IS 456 Cl. 41.4.2: Mt = Tu * (1 + D/b) / 1.7."""
        assert TORSION_MOMENT_DIVISOR == 1.7

    # --- Concrete properties --- IS 456 Cl. 6.2.3.1, 6.2.2 ---

    def test_concrete_ec_factor(self):
        """IS 456 Cl. 6.2.3.1: Ec = 5000 * sqrt(fck)."""
        assert CONCRETE_EC_FACTOR == 5000.0

    def test_concrete_fcr_factor(self):
        """IS 456 Cl. 6.2.2: fcr = 0.7 * sqrt(fck)."""
        assert CONCRETE_FCR_FACTOR == 0.7

    # --- Side-face reinforcement --- IS 456 Cl. 26.5.1.3 ---

    def test_side_face_depth_threshold(self):
        """IS 456 Cl. 26.5.1.3: required when web > 750 mm."""
        assert SIDE_FACE_DEPTH_THRESHOLD_MM == 750.0

    def test_side_face_area_ratio(self):
        """IS 456 Cl. 26.5.1.3: area >= 0.1% of web area."""
        assert SIDE_FACE_AREA_RATIO == 0.001

    # --- Cover --- IS 456 Cl. 26.4.1 ---

    def test_min_clear_cover(self):
        """IS 456 Cl. 26.4.1: moderate exposure = 25 mm."""
        assert MIN_CLEAR_COVER_MM == 25.0

    # --- Standard diameters ---

    def test_standard_bar_diameters(self):
        """Standard bar diameters include common sizes."""
        for dia in (8, 10, 12, 16, 20, 25, 32):
            assert dia in STANDARD_BAR_DIAMETERS

    def test_standard_stirrup_diameters(self):
        """Standard stirrup diameters include common sizes."""
        for dia in (6, 8, 10, 12):
            assert dia in STANDARD_STIRRUP_DIAMETERS

    def test_standard_stirrup_spacings(self):
        """Standard spacings include 75 to 300 in 25 mm increments."""
        assert STANDARD_STIRRUP_SPACINGS[0] == 75
        assert STANDARD_STIRRUP_SPACINGS[-1] == 300

    # --- Derived xu_max/d check for Fe415 ---

    def test_xu_max_ratio_fe415(self):
        """SP:16 Table 4.1: xu_max/d for Fe 415 = 700/(1100+0.87*415) = 0.4791."""
        ratio = XU_MAX_NUMERATOR / (XU_MAX_DENOM_BASE + STRESS_RATIO * 415)
        assert ratio == pytest.approx(0.4791, rel=1e-3)
