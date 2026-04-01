# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for IS 456 Cl 39.6 biaxial bending check — TASK-635.

Tests cover:
- _calculate_puz: Pure axial crush capacity (Cl 39.6a)
- _calculate_alpha_n: Bresler exponent interpolation
- _moment_at_axial_load: P-M curve interpolation
- biaxial_bending_check: Full Bresler load contour check

References:
    IS 456:2000, Cl. 39.6
    SP:16:1980 Design Aids
"""

from __future__ import annotations

import pytest

from structural_lib.codes.is456.column.axial import classify_column
from structural_lib.codes.is456.column.biaxial import (
    _calculate_alpha_n,
    _calculate_puz,
    _moment_at_axial_load,
    biaxial_bending_check,
)
from structural_lib.codes.is456.column.uniaxial import pm_interaction_curve
from structural_lib.core.data_types import (
    ColumnBiaxialResult,
    ColumnClassification,
    PMInteractionResult,
)
from structural_lib.core.errors import (
    DimensionError,
    MaterialError,
)

# ============================================================================
# Constants reused across tests
# ============================================================================
_PUZ_CONCRETE_COEFF = 0.45
_PUZ_STEEL_COEFF = 0.75


# ============================================================================
# Helper: hand-calculated Puz
# ============================================================================
def _hand_puz(b_mm: float, D_mm: float, fck: float, fy: float, Asc_mm2: float) -> float:
    """Hand-compute Puz in kN for test verification."""
    Ac = b_mm * D_mm - Asc_mm2
    return (_PUZ_CONCRETE_COEFF * fck * Ac + _PUZ_STEEL_COEFF * fy * Asc_mm2) / 1000.0


# ============================================================================
# Test: _calculate_puz
# ============================================================================
class TestCalculatePuz:
    """Tests for _calculate_puz helper — IS 456 Cl 39.6a."""

    def test_standard_case_300x500_m25_fe415(self):
        """Standard: 300x500mm, M25, Fe415, Asc=2000mm2.
        IS 456 Cl 39.6a
        Ac = 300x500 - 2000 = 148000
        Puz = 0.45*25*148000 + 0.75*415*2000 = 1665000 + 622500 = 2287500 N = 2287.5 kN
        """
        result = _calculate_puz(b_mm=300, D_mm=500, fck=25, fy=415, Asc_mm2=2000)
        assert result == pytest.approx(2287.5, rel=0.001)

    def test_square_column_400x400_m25_fe415(self):
        """Square column: 400x400mm, M25, Fe415, Asc=3200mm2.
        IS 456 Cl 39.6a
        Ac = 160000 - 3200 = 156800
        Puz = 0.45*25*156800 + 0.75*415*3200 = 1764000 + 996000 = 2760000 N = 2760 kN
        """
        result = _calculate_puz(b_mm=400, D_mm=400, fck=25, fy=415, Asc_mm2=3200)
        assert result == pytest.approx(2760.0, rel=0.001)

    def test_m20_fe415(self):
        """M20/Fe415: 300x400mm, Asc=1800mm2.
        IS 456 Cl 39.6a
        Ac = 120000 - 1800 = 118200
        Puz = 0.45*20*118200 + 0.75*415*1800 = 1063800 + 560250 = 1624050 N = 1624.05 kN
        """
        result = _calculate_puz(b_mm=300, D_mm=400, fck=20, fy=415, Asc_mm2=1800)
        assert result == pytest.approx(1624.05, rel=0.001)

    def test_m30_fe500(self):
        """M30/Fe500: 400x600mm, Asc=4800mm2.
        IS 456 Cl 39.6a
        Ac = 240000 - 4800 = 235200
        Puz = 0.45*30*235200 + 0.75*500*4800 = 3175200 + 1800000 = 4975200 N = 4975.2 kN
        """
        result = _calculate_puz(b_mm=400, D_mm=600, fck=30, fy=500, Asc_mm2=4800)
        assert result == pytest.approx(4975.2, rel=0.001)

    def test_m40_fe500(self):
        """M40/Fe500: 500x500mm, Asc=6000mm2.
        IS 456 Cl 39.6a
        Ac = 250000 - 6000 = 244000
        Puz = 0.45*40*244000 + 0.75*500*6000 = 4392000 + 2250000 = 6642000 N = 6642.0 kN
        """
        result = _calculate_puz(b_mm=500, D_mm=500, fck=40, fy=500, Asc_mm2=6000)
        assert result == pytest.approx(6642.0, rel=0.001)

    def test_near_zero_reinforcement(self):
        """Minimal reinforcement: Puz dominated by concrete.
        IS 456 Cl 39.6a
        """
        result = _calculate_puz(b_mm=300, D_mm=500, fck=25, fy=415, Asc_mm2=1.0)
        expected = _hand_puz(300, 500, 25, 415, 1.0)
        assert result == pytest.approx(expected, rel=0.001)

    def test_max_reinforcement_6_percent(self):
        """6% steel ratio (IS 456 Cl 26.5.3.1 maximum).
        Asc = 0.06 * 300 * 500 = 9000mm2
        Ac = 150000 - 9000 = 141000
        Puz = 0.45*25*141000 + 0.75*415*9000 = 1586250 + 2801250 = 4387500 N = 4387.5 kN
        """
        Asc = 0.06 * 300 * 500
        result = _calculate_puz(b_mm=300, D_mm=500, fck=25, fy=415, Asc_mm2=Asc)
        assert result == pytest.approx(4387.5, rel=0.001)

    def test_returns_kn_units(self):
        """Output must be in kN (not N)."""
        result = _calculate_puz(b_mm=300, D_mm=500, fck=25, fy=415, Asc_mm2=2000)
        # The N value = 2287500; kN value should be ~2287.5
        assert 1000 < result < 10000  # Reasonable kN range, not N range


# ============================================================================
# Test: _calculate_alpha_n
# ============================================================================
class TestCalculateAlphaN:
    """Tests for _calculate_alpha_n helper — IS 456 Cl 39.6."""

    def test_at_lower_boundary_0_2(self):
        """IS 456 Cl 39.6: Pu/Puz = 0.2 -> alpha_n = 1.0 exactly."""
        result = _calculate_alpha_n(Pu_kN=200, Puz_kN=1000)
        assert result == pytest.approx(1.0, abs=0.001)

    def test_at_upper_boundary_0_8(self):
        """IS 456 Cl 39.6: Pu/Puz = 0.8 -> alpha_n = 2.0 exactly."""
        result = _calculate_alpha_n(Pu_kN=800, Puz_kN=1000)
        assert result == pytest.approx(2.0, abs=0.001)

    def test_below_lower_boundary_clamped(self):
        """IS 456 Cl 39.6: Pu/Puz = 0.0 -> alpha_n clamped to 1.0."""
        result = _calculate_alpha_n(Pu_kN=0, Puz_kN=1000)
        assert result == pytest.approx(1.0, abs=0.001)

    def test_above_upper_boundary_clamped(self):
        """IS 456 Cl 39.6: Pu/Puz = 1.0 -> alpha_n clamped to 2.0."""
        result = _calculate_alpha_n(Pu_kN=1000, Puz_kN=1000)
        assert result == pytest.approx(2.0, abs=0.001)

    def test_midpoint_0_5(self):
        """IS 456 Cl 39.6: Pu/Puz = 0.5 -> alpha_n = 1.0 + (0.5-0.2)/0.6 = 1.5."""
        result = _calculate_alpha_n(Pu_kN=500, Puz_kN=1000)
        assert result == pytest.approx(1.5, abs=0.001)

    def test_interpolation_0_35(self):
        """IS 456 Cl 39.6: Pu/Puz = 0.35 -> alpha_n = 1.0 + (0.35-0.2)/0.6 = 1.25."""
        result = _calculate_alpha_n(Pu_kN=350, Puz_kN=1000)
        assert result == pytest.approx(1.25, abs=0.001)

    def test_interpolation_0_65(self):
        """IS 456 Cl 39.6: Pu/Puz = 0.65 -> alpha_n = 1.0 + (0.65-0.2)/0.6 = 1.75."""
        result = _calculate_alpha_n(Pu_kN=650, Puz_kN=1000)
        assert result == pytest.approx(1.75, abs=0.001)

    def test_small_load_ratio_0_1(self):
        """IS 456 Cl 39.6: Pu/Puz = 0.1 -> alpha_n clamped to 1.0."""
        result = _calculate_alpha_n(Pu_kN=100, Puz_kN=1000)
        assert result == pytest.approx(1.0, abs=0.001)

    def test_high_load_ratio_0_9(self):
        """IS 456 Cl 39.6: Pu/Puz = 0.9 -> alpha_n clamped to 2.0."""
        result = _calculate_alpha_n(Pu_kN=900, Puz_kN=1000)
        assert result == pytest.approx(2.0, abs=0.001)

    def test_puz_zero_returns_clamped(self):
        """Puz=0: safe_divide returns 0, ratio=0 < 0.2, alpha_n = 1.0."""
        result = _calculate_alpha_n(Pu_kN=100, Puz_kN=0)
        assert result == pytest.approx(1.0, abs=0.001)

    def test_both_zero(self):
        """Pu=0, Puz=0: safe_divide returns 0, alpha_n = 1.0."""
        result = _calculate_alpha_n(Pu_kN=0, Puz_kN=0)
        assert result == pytest.approx(1.0, abs=0.001)


# ============================================================================
# Test: _moment_at_axial_load
# ============================================================================
class TestMomentAtAxialLoad:
    """Tests for _moment_at_axial_load — P-M curve interpolation."""

    @pytest.fixture
    def simple_pm_curve(self) -> PMInteractionResult:
        """Simple triangular P-M curve for testing interpolation.
        Points: (0, 100), (500, 200), (1000, 0)
        Pure bending: 100 kNm, Pure axial: 1000 kN, balanced: ~500 kN at 200 kNm
        """
        return PMInteractionResult(
            points=((0.0, 100.0), (500.0, 200.0), (1000.0, 0.0)),
            Pu_0_kN=1000.0,
            Mu_0_kNm=100.0,
            Pu_bal_kN=500.0,
            Mu_bal_kNm=200.0,
            fck=25,
            fy=415,
            b_mm=300,
            D_mm=500,
            Asc_mm2=2000,
            d_prime_mm=50,
        )

    @pytest.fixture
    def real_pm_curve(self) -> PMInteractionResult:
        """Generate a real P-M interaction curve for 300x500mm, M25, Fe415."""
        return pm_interaction_curve(
            b_mm=300, D_mm=500, fck=25, fy=415, Asc_mm2=2000, d_prime_mm=50
        )

    def test_at_zero_load_returns_pure_bending(self, simple_pm_curve):
        """Pu=0 -> returns Mu_0_kNm."""
        result = _moment_at_axial_load(simple_pm_curve, Pu_kN=0.0)
        assert result == pytest.approx(100.0, rel=0.01)

    def test_at_pure_axial_returns_zero(self, simple_pm_curve):
        """Pu = Pu_0 -> returns 0."""
        result = _moment_at_axial_load(simple_pm_curve, Pu_kN=1000.0)
        assert result == pytest.approx(0.0, abs=0.01)

    def test_exceeds_pure_axial_returns_zero(self, simple_pm_curve):
        """Pu > Pu_0 -> returns 0."""
        result = _moment_at_axial_load(simple_pm_curve, Pu_kN=1500.0)
        assert result == pytest.approx(0.0, abs=0.01)

    def test_negative_load_returns_pure_bending(self, simple_pm_curve):
        """Pu < 0 -> returns Mu_0_kNm."""
        result = _moment_at_axial_load(simple_pm_curve, Pu_kN=-10.0)
        assert result == pytest.approx(100.0, rel=0.01)

    def test_midpoint_interpolation(self, simple_pm_curve):
        """Pu=250 (midpoint of first segment) -> M ~ 150 kNm."""
        result = _moment_at_axial_load(simple_pm_curve, Pu_kN=250.0)
        assert result == pytest.approx(150.0, rel=0.01)

    def test_balanced_point(self, simple_pm_curve):
        """At balanced load, moment should be maximum."""
        result = _moment_at_axial_load(simple_pm_curve, Pu_kN=500.0)
        assert result == pytest.approx(200.0, rel=0.01)

    def test_empty_points_returns_zero(self):
        """Empty P-M curve -> 0."""
        pm = PMInteractionResult(
            points=(),
            Pu_0_kN=0,
            Mu_0_kNm=0,
            Pu_bal_kN=0,
            Mu_bal_kNm=0,
            fck=25,
            fy=415,
            b_mm=300,
            D_mm=500,
            Asc_mm2=2000,
            d_prime_mm=50,
        )
        assert _moment_at_axial_load(pm, 100.0) == 0.0

    def test_real_pm_curve_has_positive_capacity(self, real_pm_curve):
        """Real P-M curve should give positive moment at moderate load."""
        Pu_test = real_pm_curve.Pu_0_kN * 0.5
        result = _moment_at_axial_load(real_pm_curve, Pu_test)
        assert result > 0

    def test_real_pm_curve_balanced_is_maximum(self, real_pm_curve):
        """Moment capacity at balanced point should be near peak of envelope."""
        M_bal = _moment_at_axial_load(real_pm_curve, real_pm_curve.Pu_bal_kN)
        M_above = _moment_at_axial_load(real_pm_curve, real_pm_curve.Pu_bal_kN * 1.3)
        M_below = _moment_at_axial_load(real_pm_curve, real_pm_curve.Pu_bal_kN * 0.7)
        # Balanced moment should be >= neighbours (peak of envelope)
        assert M_bal >= M_above * 0.95  # allow 5% tolerance for discrete curve
        assert M_bal >= M_below * 0.95


# ============================================================================
# Test: biaxial_bending_check — main function
# ============================================================================
class TestBiaxialBendingCheck:
    """Tests for main biaxial_bending_check function — IS 456 Cl 39.6."""

    # Standard parameters for a 300x500mm column
    BASE_PARAMS = dict(
        b_mm=300,
        D_mm=500,
        le_mm=3000,
        fck=25,
        fy=415,
        Asc_mm2=4000,
        d_prime_mm=50,
    )

    def test_returns_column_biaxial_result(self):
        """Return type must be ColumnBiaxialResult."""
        result = biaxial_bending_check(
            Pu_kN=500, Mux_kNm=50, Muy_kNm=30, **self.BASE_PARAMS
        )
        assert isinstance(result, ColumnBiaxialResult)

    def test_clearly_safe_loading(self):
        """Low biaxial moments -> interaction_ratio < 1.0, is_safe=True."""
        result = biaxial_bending_check(
            Pu_kN=500, Mux_kNm=20, Muy_kNm=15, **self.BASE_PARAMS
        )
        assert result.is_safe is True
        assert result.interaction_ratio < 1.0

    def test_puz_computed_correctly(self):
        """Puz field should match hand calculation. IS 456 Cl 39.6a."""
        result = biaxial_bending_check(
            Pu_kN=500, Mux_kNm=50, Muy_kNm=30, **self.BASE_PARAMS
        )
        expected_puz = _hand_puz(300, 500, 25, 415, 4000)
        assert result.Puz_kN == pytest.approx(expected_puz, rel=0.001)

    def test_alpha_n_consistent_with_ratio(self):
        """alpha_n should match Pu/Puz-based interpolation. IS 456 Cl 39.6."""
        result = biaxial_bending_check(
            Pu_kN=500, Mux_kNm=50, Muy_kNm=30, **self.BASE_PARAMS
        )
        Puz = result.Puz_kN
        ratio = 500 / Puz
        if ratio <= 0.2:
            expected_alpha = 1.0
        elif ratio >= 0.8:
            expected_alpha = 2.0
        else:
            expected_alpha = 1.0 + (ratio - 0.2) / 0.6
        assert result.alpha_n == pytest.approx(expected_alpha, abs=0.01)

    def test_mux1_positive(self):
        """Mux1 (uniaxial x-axis capacity) should be positive."""
        result = biaxial_bending_check(
            Pu_kN=500, Mux_kNm=50, Muy_kNm=30, **self.BASE_PARAMS
        )
        assert result.Mux1_kNm > 0

    def test_muy1_positive(self):
        """Muy1 (uniaxial y-axis capacity) should be positive."""
        result = biaxial_bending_check(
            Pu_kN=500, Mux_kNm=50, Muy_kNm=30, **self.BASE_PARAMS
        )
        assert result.Muy1_kNm > 0

    def test_rectangular_column_mux1_ne_muy1(self):
        """For b != D, Mux1 and Muy1 must differ (axis swap)."""
        result = biaxial_bending_check(
            Pu_kN=500, Mux_kNm=50, Muy_kNm=30, **self.BASE_PARAMS
        )
        # b=300, D=500 -> Mux1 (bending about D) != Muy1 (bending about b)
        assert result.Mux1_kNm != pytest.approx(result.Muy1_kNm, rel=0.05)

    def test_square_column_mux1_equals_muy1(self):
        """For b = D (square column), Mux1 == Muy1."""
        result = biaxial_bending_check(
            Pu_kN=500,
            Mux_kNm=50,
            Muy_kNm=50,
            b_mm=400,
            D_mm=400,
            le_mm=3000,
            fck=25,
            fy=415,
            Asc_mm2=4000,
            d_prime_mm=50,
        )
        assert result.Mux1_kNm == pytest.approx(result.Muy1_kNm, rel=0.01)

    def test_interaction_ratio_formula(self):
        """IS 456 Cl 39.6: ratio = (Mux/Mux1)^alpha_n + (Muy/Muy1)^alpha_n."""
        result = biaxial_bending_check(
            Pu_kN=500, Mux_kNm=50, Muy_kNm=30, **self.BASE_PARAMS
        )
        ratio_x = result.Mux_kNm / result.Mux1_kNm
        ratio_y = result.Muy_kNm / result.Muy1_kNm
        expected_ir = ratio_x**result.alpha_n + ratio_y**result.alpha_n
        assert result.interaction_ratio == pytest.approx(expected_ir, rel=0.01)

    def test_clause_ref(self):
        """clause_ref should be 'Cl. 39.6'."""
        result = biaxial_bending_check(
            Pu_kN=500, Mux_kNm=50, Muy_kNm=30, **self.BASE_PARAMS
        )
        assert result.clause_ref == "Cl. 39.6"

    def test_short_column_classification(self):
        """le/D < 12 -> SHORT classification. IS 456 Cl 25.1.2."""
        result = biaxial_bending_check(
            Pu_kN=500, Mux_kNm=50, Muy_kNm=30, **self.BASE_PARAMS
        )
        # le=3000, max(b,D)=500 -> le/D = 6.0 < 12 -> SHORT
        assert result.classification == ColumnClassification.SHORT

    def test_slender_column_has_warning(self):
        """le/D >= 12 -> SLENDER classification with warning."""
        result = biaxial_bending_check(
            Pu_kN=500,
            Mux_kNm=20,
            Muy_kNm=15,
            b_mm=300,
            D_mm=500,
            le_mm=7000,  # le/D = 7000/500 = 14 > 12
            fck=25,
            fy=415,
            Asc_mm2=4000,
            d_prime_mm=50,
        )
        assert result.classification == ColumnClassification.SLENDER
        assert any("slender" in w.lower() for w in result.warnings)

    def test_different_materials_m30_fe500(self):
        """M30/Fe500 column should compute without errors."""
        result = biaxial_bending_check(
            Pu_kN=800,
            Mux_kNm=60,
            Muy_kNm=40,
            b_mm=400,
            D_mm=600,
            le_mm=4000,
            fck=30,
            fy=500,
            Asc_mm2=6000,
            d_prime_mm=60,
        )
        assert isinstance(result, ColumnBiaxialResult)
        assert result.Puz_kN > 0

    def test_to_dict_has_all_keys(self):
        """to_dict() should produce all expected keys."""
        result = biaxial_bending_check(
            Pu_kN=500, Mux_kNm=50, Muy_kNm=30, **self.BASE_PARAMS
        )
        d = result.to_dict()
        expected_keys = {
            "Pu_kN",
            "Mux_kNm",
            "Muy_kNm",
            "Mux1_kNm",
            "Muy1_kNm",
            "Puz_kN",
            "alpha_n",
            "interaction_ratio",
            "is_safe",
            "classification",
            "clause_ref",
            "warnings",
        }
        assert expected_keys.issubset(d.keys())

    def test_summary_string(self):
        """summary() should contain SAFE/UNSAFE status."""
        result = biaxial_bending_check(
            Pu_kN=500, Mux_kNm=20, Muy_kNm=15, **self.BASE_PARAMS
        )
        s = result.summary()
        assert "SAFE" in s or "UNSAFE" in s


# ============================================================================
# Test: Edge cases and degenerate inputs
# ============================================================================
class TestBiaxialEdgeCases:
    """Edge cases and degenerate inputs."""

    BASE = dict(
        b_mm=300,
        D_mm=500,
        le_mm=3000,
        fck=25,
        fy=415,
        Asc_mm2=4000,
        d_prime_mm=50,
    )

    def test_zero_moments_is_safe(self):
        """Mux=0, Muy=0, Pu>0 -> interaction_ratio=0, is_safe=True."""
        result = biaxial_bending_check(Pu_kN=500, Mux_kNm=0, Muy_kNm=0, **self.BASE)
        assert result.is_safe is True
        assert result.interaction_ratio == pytest.approx(0.0, abs=0.01)

    def test_uniaxial_x_only(self):
        """Muy=0 -> reduces to uniaxial about x, ratio = (Mux/Mux1)^alpha_n."""
        result = biaxial_bending_check(Pu_kN=500, Mux_kNm=50, Muy_kNm=0, **self.BASE)
        expected_ir = (result.Mux_kNm / result.Mux1_kNm) ** result.alpha_n
        assert result.interaction_ratio == pytest.approx(expected_ir, rel=0.01)

    def test_uniaxial_y_only(self):
        """Mux=0 -> reduces to uniaxial about y, ratio = (Muy/Muy1)^alpha_n."""
        result = biaxial_bending_check(Pu_kN=500, Mux_kNm=0, Muy_kNm=30, **self.BASE)
        expected_ir = (result.Muy_kNm / result.Muy1_kNm) ** result.alpha_n
        assert result.interaction_ratio == pytest.approx(expected_ir, rel=0.01)

    def test_pu_zero_pure_bending(self):
        """Pu=0 (pure bending) -> alpha_n=1.0, should still work."""
        result = biaxial_bending_check(Pu_kN=0, Mux_kNm=30, Muy_kNm=20, **self.BASE)
        assert result.alpha_n == pytest.approx(1.0, abs=0.01)
        assert result.interaction_ratio >= 0

    def test_pu_exceeds_puz_is_unsafe(self):
        """Pu >= Puz -> is_safe=False, interaction_ratio=inf."""
        Puz = _hand_puz(300, 500, 25, 415, 4000)
        result = biaxial_bending_check(
            Pu_kN=Puz + 10, Mux_kNm=50, Muy_kNm=30, **self.BASE
        )
        assert result.is_safe is False
        assert result.interaction_ratio == float("inf")

    def test_pu_equals_puz_is_unsafe(self):
        """Pu = Puz exactly -> is_safe=False, interaction_ratio=inf."""
        Puz = _hand_puz(300, 500, 25, 415, 4000)
        result = biaxial_bending_check(Pu_kN=Puz, Mux_kNm=50, Muy_kNm=30, **self.BASE)
        assert result.is_safe is False
        assert result.interaction_ratio == float("inf")

    def test_small_eccentricity(self):
        """Very small moments -> interaction ratio near 0, safe."""
        result = biaxial_bending_check(Pu_kN=500, Mux_kNm=0.1, Muy_kNm=0.1, **self.BASE)
        assert result.is_safe is True
        assert result.interaction_ratio < 0.1

    def test_l_unsupported_mm_accepted(self):
        """Optional l_unsupported_mm should be accepted without error."""
        result = biaxial_bending_check(
            Pu_kN=500,
            Mux_kNm=50,
            Muy_kNm=30,
            l_unsupported_mm=3500,
            **self.BASE,
        )
        assert isinstance(result, ColumnBiaxialResult)


# ============================================================================
# Test: Validation / error raising
# ============================================================================
class TestBiaxialValidation:
    """Validation: invalid inputs should raise appropriate errors."""

    BASE = dict(
        Pu_kN=500,
        Mux_kNm=50,
        Muy_kNm=30,
        b_mm=300,
        D_mm=500,
        le_mm=3000,
        fck=25,
        fy=415,
        Asc_mm2=4000,
        d_prime_mm=50,
    )

    def test_negative_b_mm_raises(self):
        """b_mm < 0 -> DimensionError."""
        with pytest.raises(DimensionError, match="b_mm"):
            biaxial_bending_check(**{**self.BASE, "b_mm": -100})

    def test_zero_b_mm_raises(self):
        """b_mm = 0 -> DimensionError."""
        with pytest.raises(DimensionError, match="b_mm"):
            biaxial_bending_check(**{**self.BASE, "b_mm": 0})

    def test_negative_d_mm_raises(self):
        """D_mm < 0 -> DimensionError."""
        with pytest.raises(DimensionError, match="D_mm"):
            biaxial_bending_check(**{**self.BASE, "D_mm": -100})

    def test_zero_d_mm_raises(self):
        """D_mm = 0 -> DimensionError."""
        with pytest.raises(DimensionError, match="D_mm"):
            biaxial_bending_check(**{**self.BASE, "D_mm": 0})

    def test_negative_le_mm_raises(self):
        """le_mm < 0 -> DimensionError."""
        with pytest.raises(DimensionError, match="le_mm"):
            biaxial_bending_check(**{**self.BASE, "le_mm": -100})

    def test_zero_le_mm_raises(self):
        """le_mm = 0 -> DimensionError."""
        with pytest.raises(DimensionError, match="le_mm"):
            biaxial_bending_check(**{**self.BASE, "le_mm": 0})

    def test_negative_fck_raises(self):
        """fck < 0 -> MaterialError."""
        with pytest.raises(MaterialError, match="fck"):
            biaxial_bending_check(**{**self.BASE, "fck": -5})

    def test_zero_fck_raises(self):
        """fck = 0 -> MaterialError."""
        with pytest.raises(MaterialError, match="fck"):
            biaxial_bending_check(**{**self.BASE, "fck": 0})

    def test_negative_fy_raises(self):
        """fy < 0 -> MaterialError."""
        with pytest.raises(MaterialError, match="fy"):
            biaxial_bending_check(**{**self.BASE, "fy": -415})

    def test_zero_fy_raises(self):
        """fy = 0 -> MaterialError."""
        with pytest.raises(MaterialError, match="fy"):
            biaxial_bending_check(**{**self.BASE, "fy": 0})

    def test_negative_pu_raises(self):
        """Pu_kN < 0 -> DimensionError."""
        with pytest.raises(DimensionError, match="Pu_kN"):
            biaxial_bending_check(**{**self.BASE, "Pu_kN": -100})

    def test_negative_mux_raises(self):
        """Mux_kNm < 0 -> DimensionError."""
        with pytest.raises(DimensionError, match="Mux_kNm"):
            biaxial_bending_check(**{**self.BASE, "Mux_kNm": -50})

    def test_negative_muy_raises(self):
        """Muy_kNm < 0 -> DimensionError."""
        with pytest.raises(DimensionError, match="Muy_kNm"):
            biaxial_bending_check(**{**self.BASE, "Muy_kNm": -30})

    def test_zero_asc_raises(self):
        """Asc_mm2 = 0 -> DimensionError."""
        with pytest.raises(DimensionError, match="Asc_mm2"):
            biaxial_bending_check(**{**self.BASE, "Asc_mm2": 0})

    def test_negative_asc_raises(self):
        """Asc_mm2 < 0 -> DimensionError."""
        with pytest.raises(DimensionError, match="Asc_mm2"):
            biaxial_bending_check(**{**self.BASE, "Asc_mm2": -100})

    def test_d_prime_zero_raises(self):
        """d_prime_mm = 0 -> DimensionError."""
        with pytest.raises(DimensionError, match="d_prime_mm"):
            biaxial_bending_check(**{**self.BASE, "d_prime_mm": 0})

    def test_d_prime_exceeds_half_min_dim_raises(self):
        """d_prime_mm >= min(b,D)/2 -> DimensionError."""
        # min(300,500)/2 = 150
        with pytest.raises(DimensionError, match="d_prime_mm"):
            biaxial_bending_check(**{**self.BASE, "d_prime_mm": 150})

    def test_d_prime_negative_raises(self):
        """d_prime_mm < 0 -> DimensionError."""
        with pytest.raises(DimensionError, match="d_prime_mm"):
            biaxial_bending_check(**{**self.BASE, "d_prime_mm": -10})

    def test_fck_above_80_gives_warning(self):
        """fck > 80 -> should add warning but NOT raise."""
        result = biaxial_bending_check(**{**self.BASE, "fck": 90})
        assert any("fck" in w and "80" in w for w in result.warnings)

    def test_fy_above_550_gives_warning(self):
        """fy > 550 -> should add warning but NOT raise."""
        result = biaxial_bending_check(**{**self.BASE, "fy": 600})
        assert any("fy" in w and "550" in w for w in result.warnings)


# ============================================================================
# Test: Integration with effective_length, classify, pm_interaction
# ============================================================================
class TestBiaxialIntegration:
    """Integration tests: biaxial uses classify_column and pm_interaction_curve."""

    def test_classification_matches_standalone(self):
        """Column classification in result should match standalone classify_column()."""
        result = biaxial_bending_check(
            Pu_kN=500,
            Mux_kNm=50,
            Muy_kNm=30,
            b_mm=300,
            D_mm=500,
            le_mm=3000,
            fck=25,
            fy=415,
            Asc_mm2=4000,
            d_prime_mm=50,
        )
        expected_class = classify_column(3000, max(300, 500))
        assert result.classification == expected_class

    def test_mux1_matches_pm_curve_interpolation(self):
        """Mux1 from biaxial should match direct P-M curve query (x-axis)."""
        Pu_kN = 500
        result = biaxial_bending_check(
            Pu_kN=Pu_kN,
            Mux_kNm=50,
            Muy_kNm=30,
            b_mm=300,
            D_mm=500,
            le_mm=3000,
            fck=25,
            fy=415,
            Asc_mm2=4000,
            d_prime_mm=50,
        )
        # Bending about x: b=300, D=500
        pm_x = pm_interaction_curve(
            b_mm=300, D_mm=500, fck=25, fy=415, Asc_mm2=4000, d_prime_mm=50
        )
        expected_mux1 = _moment_at_axial_load(pm_x, Pu_kN)
        assert result.Mux1_kNm == pytest.approx(expected_mux1, rel=0.01)

    def test_muy1_matches_pm_curve_interpolation_swapped(self):
        """Muy1 from biaxial should match P-M curve with swapped b,D (y-axis)."""
        Pu_kN = 500
        result = biaxial_bending_check(
            Pu_kN=Pu_kN,
            Mux_kNm=50,
            Muy_kNm=30,
            b_mm=300,
            D_mm=500,
            le_mm=3000,
            fck=25,
            fy=415,
            Asc_mm2=4000,
            d_prime_mm=50,
        )
        # Bending about y: b_mm=D_mm=500, D_mm=b_mm=300 (swap)
        pm_y = pm_interaction_curve(
            b_mm=500, D_mm=300, fck=25, fy=415, Asc_mm2=4000, d_prime_mm=50
        )
        expected_muy1 = _moment_at_axial_load(pm_y, Pu_kN)
        assert result.Muy1_kNm == pytest.approx(expected_muy1, rel=0.01)

    def test_full_pipeline_short_column(self):
        """Full pipeline: classify -> pm_interaction -> biaxial for short column."""
        b, D, le = 400, 400, 3000
        classification = classify_column(le, max(b, D))
        assert classification == ColumnClassification.SHORT

        result = biaxial_bending_check(
            Pu_kN=600,
            Mux_kNm=40,
            Muy_kNm=40,
            b_mm=b,
            D_mm=D,
            le_mm=le,
            fck=25,
            fy=415,
            Asc_mm2=4800,
            d_prime_mm=50,
        )
        assert result.classification == ColumnClassification.SHORT
        assert isinstance(result.interaction_ratio, float)

    def test_full_pipeline_slender_column(self):
        """Full pipeline: classify -> biaxial for slender column (le/D >= 12)."""
        b, D, le = 300, 400, 5000
        classification = classify_column(le, max(b, D))
        assert classification == ColumnClassification.SLENDER

        result = biaxial_bending_check(
            Pu_kN=400,
            Mux_kNm=30,
            Muy_kNm=20,
            b_mm=b,
            D_mm=D,
            le_mm=le,
            fck=25,
            fy=415,
            Asc_mm2=3600,
            d_prime_mm=50,
        )
        assert result.classification == ColumnClassification.SLENDER


# ============================================================================
# Test: Structural benchmarks — known results
# ============================================================================
class TestBiaxialStructuralBenchmarks:
    """Structural benchmark tests with hand-verified expectations.

    IS 456 Cl 39.6: Bresler load contour
    Reference: Pillai & Menon, 3rd Ed., Ch. 13
    """

    def test_safe_loading_300x500_moderate(self):
        """300x500, M25/Fe415, Asc=4000mm2, moderate loading -> safe.
        IS 456 Cl 39.6a:
        Puz = 0.45*25*(150000-4000) + 0.75*415*4000
             = 0.45*25*146000 + 0.75*415*4000
             = 1642500 + 1245000 = 2887500 N = 2887.5 kN
        Pu=500 -> Pu/Puz ~ 0.173 -> alpha_n = 1.0 (clamped below 0.2)
        Small moments relative to capacity -> clearly safe.
        """
        result = biaxial_bending_check(
            Pu_kN=500,
            Mux_kNm=30,
            Muy_kNm=20,
            b_mm=300,
            D_mm=500,
            le_mm=3000,
            fck=25,
            fy=415,
            Asc_mm2=4000,
            d_prime_mm=50,
        )
        assert result.is_safe is True
        assert result.Puz_kN == pytest.approx(2887.5, rel=0.001)
        assert result.interaction_ratio < 1.0

    def test_high_loading_300x500_unsafe(self):
        """300x500, M25/Fe415, Asc=2000mm2, heavy moments -> unsafe.
        Puz = 0.45*25*(150000-2000) + 0.75*415*2000
             = 1665000 + 622500 = 2287500 N = 2287.5 kN
        Large Mux, Muy relative to small section -> likely unsafe.
        """
        result = biaxial_bending_check(
            Pu_kN=1000,
            Mux_kNm=200,
            Muy_kNm=150,
            b_mm=300,
            D_mm=500,
            le_mm=3000,
            fck=25,
            fy=415,
            Asc_mm2=2000,
            d_prime_mm=50,
        )
        assert result.is_safe is False
        assert result.interaction_ratio > 1.0

    def test_alpha_n_at_ratio_0_5(self):
        """Engineer Pu/Puz ~ 0.5 -> alpha_n ~ 1.5.
        IS 456 Cl 39.6.
        Use 400x400, M25, Fe415, Asc=4800mm2.
        Puz = 0.45*25*(160000-4800) + 0.75*415*4800
             = 0.45*25*155200 + 0.75*415*4800
             = 1746000 + 1494000 = 3240000 N = 3240.0 kN
        Target Pu ~ 0.5 * 3240 = 1620 kN -> Pu/Puz = 0.5 -> alpha_n ~ 1.5
        """
        Puz = 3240.0
        Pu = Puz * 0.5
        result = biaxial_bending_check(
            Pu_kN=Pu,
            Mux_kNm=30,
            Muy_kNm=30,
            b_mm=400,
            D_mm=400,
            le_mm=3000,
            fck=25,
            fy=415,
            Asc_mm2=4800,
            d_prime_mm=50,
        )
        assert result.Puz_kN == pytest.approx(Puz, rel=0.001)
        assert result.alpha_n == pytest.approx(1.5, abs=0.02)

    def test_interaction_ratio_monotonicity_increasing_mux(self):
        """Monotonicity: increasing Mux -> increasing interaction_ratio."""
        params = dict(
            Pu_kN=500,
            Muy_kNm=20,
            b_mm=300,
            D_mm=500,
            le_mm=3000,
            fck=25,
            fy=415,
            Asc_mm2=4000,
            d_prime_mm=50,
        )
        r1 = biaxial_bending_check(Mux_kNm=20, **params)
        r2 = biaxial_bending_check(Mux_kNm=50, **params)
        r3 = biaxial_bending_check(Mux_kNm=80, **params)
        assert r1.interaction_ratio < r2.interaction_ratio
        assert r2.interaction_ratio < r3.interaction_ratio

    def test_interaction_ratio_monotonicity_increasing_muy(self):
        """Monotonicity: increasing Muy -> increasing interaction_ratio."""
        params = dict(
            Pu_kN=500,
            Mux_kNm=30,
            b_mm=300,
            D_mm=500,
            le_mm=3000,
            fck=25,
            fy=415,
            Asc_mm2=4000,
            d_prime_mm=50,
        )
        r1 = biaxial_bending_check(Muy_kNm=10, **params)
        r2 = biaxial_bending_check(Muy_kNm=30, **params)
        r3 = biaxial_bending_check(Muy_kNm=50, **params)
        assert r1.interaction_ratio < r2.interaction_ratio
        assert r2.interaction_ratio < r3.interaction_ratio

    def test_higher_fck_gives_higher_puz(self):
        """Higher fck -> higher Puz capacity."""
        params = dict(
            Pu_kN=500,
            Mux_kNm=50,
            Muy_kNm=30,
            b_mm=300,
            D_mm=500,
            le_mm=3000,
            fy=415,
            Asc_mm2=4000,
            d_prime_mm=50,
        )
        r25 = biaxial_bending_check(fck=25, **params)
        r30 = biaxial_bending_check(fck=30, **params)
        r40 = biaxial_bending_check(fck=40, **params)
        # Higher fck -> Puz increases
        assert r25.Puz_kN < r30.Puz_kN < r40.Puz_kN

    def test_larger_section_is_safer(self):
        """Larger section -> lower interaction ratio (more capacity)."""
        params = dict(
            Pu_kN=500,
            Mux_kNm=50,
            Muy_kNm=30,
            le_mm=3000,
            fck=25,
            fy=415,
            Asc_mm2=4000,
            d_prime_mm=50,
        )
        r_small = biaxial_bending_check(b_mm=300, D_mm=400, **params)
        r_large = biaxial_bending_check(b_mm=400, D_mm=600, **params)
        assert r_large.interaction_ratio < r_small.interaction_ratio

    def test_more_steel_reduces_ratio(self):
        """More reinforcement -> higher capacity -> lower interaction ratio."""
        params = dict(
            Pu_kN=500,
            Mux_kNm=50,
            Muy_kNm=30,
            b_mm=300,
            D_mm=500,
            le_mm=3000,
            fck=25,
            fy=415,
            d_prime_mm=50,
        )
        r_low = biaxial_bending_check(Asc_mm2=2000, **params)
        r_high = biaxial_bending_check(Asc_mm2=6000, **params)
        assert r_high.Puz_kN > r_low.Puz_kN
        assert r_high.interaction_ratio < r_low.interaction_ratio
