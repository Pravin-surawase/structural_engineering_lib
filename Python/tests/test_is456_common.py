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
)
from structural_lib.codes.is456.common.validation import (
    validate_beam_dimensions,
    validate_material_grades,
)
from structural_lib.core.errors import DimensionError, MaterialError

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
