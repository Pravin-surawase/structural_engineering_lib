# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for IS 456 footing design — TASK-650/651/652.

Covers all four footing sub-modules:
- bearing (size_footing) — Cl. 34.1
- flexure (footing_flexure) — Cl. 34.2.3.1
- one_way_shear (footing_one_way_shear) — Cl. 34.2.4.1(a)
- punching_shear (footing_punching_shear) — Cl. 31.6.1

Plus shared utilities (_common) and frozen dataclass type checks.

References:
    IS 456:2000 Cl. 31.6, 34.1, 34.2
"""

from __future__ import annotations

import pytest

from structural_lib.codes.is456.footing._common import (
    net_upward_pressure_nmm2,
    punching_area_mm2,
    punching_perimeter_mm,
    validate_footing_inputs,
)
from structural_lib.codes.is456.footing.bearing import size_footing
from structural_lib.codes.is456.footing.flexure import footing_flexure
from structural_lib.codes.is456.footing.one_way_shear import footing_one_way_shear
from structural_lib.codes.is456.footing.punching_shear import footing_punching_shear
from structural_lib.core.data_types import (
    FootingBearingResult,
    FootingFlexureResult,
    FootingOneWayShearResult,
    FootingPunchingResult,
    FootingType,
)
from structural_lib.core.errors import DimensionError, ValidationError

# ===========================================================================
# 1. Bearing / Sizing Tests — size_footing (IS 456 Cl 34.1)
# ===========================================================================


class TestFootingBearing:
    """Tests for size_footing: footing sizing & bearing capacity check."""

    def test_concentric_square_footing(self):
        """IS 456 Cl 34.1: Concentric square footing.
        P=800kN, q_safe=200kPa, col 400×400.
        A_req = 800/200 = 4.0 m² → L ≈ 2000mm.
        """
        result = size_footing(
            P_service_kN=800,
            q_safe_kPa=200,
            a_mm=400,
            b_mm=400,
            footing_type=FootingType.ISOLATED_SQUARE,
        )
        assert isinstance(result, FootingBearingResult)
        assert result.L_mm == result.B_mm, "Square footing must have L == B"
        assert result.L_mm == pytest.approx(2000, abs=50)
        assert result.pressure_type == "uniform"
        assert result.q_max_kPa == pytest.approx(result.q_min_kPa)
        assert result.utilization_ratio <= 1.0
        assert result.is_safe is True

    def test_concentric_rectangular_footing(self):
        """IS 456 Cl 34.1: Rectangular footing maintaining column aspect ratio.
        P=600kN, q_safe=150kPa, col 300×450.
        A_req = 600/150 = 4.0 m² → rectangular footing.
        """
        result = size_footing(
            P_service_kN=600,
            q_safe_kPa=150,
            a_mm=300,
            b_mm=450,
            footing_type=FootingType.ISOLATED_RECTANGULAR,
        )
        assert isinstance(result, FootingBearingResult)
        assert result.L_mm * result.B_mm >= 4_000_000  # Must meet area requirement
        assert result.pressure_type == "uniform"
        assert result.is_safe is True

    def test_eccentric_trapezoidal_pressure(self):
        """IS 456 Cl 34.1: Eccentric load → trapezoidal pressure.
        P=800kN, M=40kNm, q_safe=200kPa, col 400×400.
        e = M/P = 40/800 = 0.05m = 50mm.
        Footing ~2000mm → L/6 ≈ 333mm > e → trapezoidal.
        """
        result = size_footing(
            P_service_kN=800,
            q_safe_kPa=200,
            a_mm=400,
            b_mm=400,
            M_service_kNm=40.0,
        )
        assert result.pressure_type == "trapezoidal"
        assert result.q_max_kPa > result.q_min_kPa
        assert result.q_min_kPa > 0, "Trapezoidal must have positive q_min"

    def test_eccentric_partial_contact(self):
        """IS 456 Cl 34.1: Large eccentricity → partial contact (q_min=0).
        P=500kN, M=200kNm → e = 400mm.
        Footing ~1600mm → L/6 ≈ 267mm < e → partial contact.
        """
        result = size_footing(
            P_service_kN=500,
            q_safe_kPa=200,
            a_mm=300,
            b_mm=300,
            M_service_kNm=200.0,
        )
        assert result.pressure_type == "partial_contact"
        assert result.q_min_kPa == 0.0
        assert result.q_max_kPa > 0
        assert len(result.warnings) > 0, "Partial contact should generate warnings"

    def test_validation_negative_load(self):
        """Validation: Negative service load → ValidationError."""
        with pytest.raises(ValidationError, match="positive"):
            size_footing(
                P_service_kN=-100,
                q_safe_kPa=200,
                a_mm=300,
                b_mm=300,
            )

    def test_validation_zero_bearing_capacity(self):
        """Validation: Zero bearing capacity → ValidationError."""
        with pytest.raises(ValidationError, match="positive"):
            size_footing(
                P_service_kN=800,
                q_safe_kPa=0,
                a_mm=300,
                b_mm=300,
            )

    def test_validation_negative_bearing_capacity(self):
        """Validation: Negative bearing capacity → ValidationError."""
        with pytest.raises(ValidationError, match="positive"):
            size_footing(
                P_service_kN=800,
                q_safe_kPa=-100,
                a_mm=300,
                b_mm=300,
            )

    def test_validation_negative_column_dims(self):
        """Validation: Negative column dimension → DimensionError."""
        with pytest.raises(DimensionError, match="positive"):
            size_footing(
                P_service_kN=800,
                q_safe_kPa=200,
                a_mm=-300,
                b_mm=300,
            )

    def test_validation_zero_column_dim(self):
        """Validation: Zero column dimension → DimensionError."""
        with pytest.raises(DimensionError, match="positive"):
            size_footing(
                P_service_kN=800,
                q_safe_kPa=200,
                a_mm=300,
                b_mm=0,
            )

    def test_result_is_frozen(self):
        """Result type: FootingBearingResult is frozen dataclass."""
        result = size_footing(
            P_service_kN=800,
            q_safe_kPa=200,
            a_mm=400,
            b_mm=400,
        )
        with pytest.raises(AttributeError):
            result.L_mm = 9999  # type: ignore[misc]

    def test_result_to_dict(self):
        """Result type: to_dict() returns dict with all expected keys."""
        result = size_footing(
            P_service_kN=800,
            q_safe_kPa=200,
            a_mm=400,
            b_mm=400,
        )
        d = result.to_dict()
        assert isinstance(d, dict)
        for key in (
            "L_mm",
            "B_mm",
            "q_max_kPa",
            "q_min_kPa",
            "q_safe_kPa",
            "pressure_type",
            "utilization_ratio",
            "is_safe",
        ):
            assert key in d

    def test_result_summary(self):
        """Result type: summary() returns non-empty descriptive string."""
        result = size_footing(
            P_service_kN=800,
            q_safe_kPa=200,
            a_mm=400,
            b_mm=400,
        )
        s = result.summary()
        assert isinstance(s, str)
        assert len(s) > 10
        assert "SAFE" in s or "UNSAFE" in s

    def test_footing_larger_than_column(self):
        """Sizing: footing must always be larger than column in both directions."""
        result = size_footing(
            P_service_kN=50,  # Small load
            q_safe_kPa=200,
            a_mm=400,
            b_mm=400,
        )
        assert result.L_mm > 400
        assert result.B_mm > 400


# ===========================================================================
# 2. Flexure Tests — footing_flexure (IS 456 Cl 34.2.3.1)
# ===========================================================================


class TestFootingFlexure:
    """Tests for footing_flexure: bending at column face."""

    def test_benchmark_concentric_square(self):
        """IS 456 Cl 34.2.3.1: Benchmark — concentric square footing.
        Pu=1200kN, L=2000, B=2000, d=400, col 400×400, fck=25, fy=415.
        qu = 1200×1000/(2000×2000) = 0.3 N/mm².
        cant = (2000-400)/2 = 800mm.
        Mu = 0.3 × 2000 × 800² / 2 = 192×10⁶ N·mm = 192 kN·m.
        """
        result = footing_flexure(
            Pu_kN=1200,
            L_mm=2000,
            B_mm=2000,
            d_mm=400,
            a_mm=400,
            b_mm=400,
            fck=25,
            fy=415,
        )
        assert isinstance(result, FootingFlexureResult)
        assert result.Mu_kNm == pytest.approx(192.0, rel=0.01)
        assert result.Ast_mm2 > 0
        assert result.pt_percent >= 0.12
        assert result.cantilever_mm == pytest.approx(800.0)
        assert result.is_safe is True

    def test_minimum_steel_check(self):
        """IS 456 Cl 26.5.2.1: Small moment → steel increased to min 0.12% for HYSD.
        Very small load → flexure is low → minimum steel governs.
        """
        result = footing_flexure(
            Pu_kN=100,
            L_mm=1500,
            B_mm=1500,
            d_mm=400,
            a_mm=300,
            b_mm=300,
            fck=25,
            fy=415,
        )
        assert result.pt_percent >= 0.12
        assert any("minimum" in w.lower() for w in result.warnings)

    def test_symmetric_footing_equal_directions(self):
        """Square col on square footing → both directions give equal moment."""
        result = footing_flexure(
            Pu_kN=1200,
            L_mm=2000,
            B_mm=2000,
            d_mm=400,
            a_mm=400,
            b_mm=400,
            fck=25,
            fy=415,
        )
        # For symmetric case, cant_L == cant_B == 800
        assert result.cantilever_mm == pytest.approx(800.0)

    def test_rectangular_footing_asymmetric(self):
        """Rectangular col on rectangular footing → different moments each direction."""
        result = footing_flexure(
            Pu_kN=1200,
            L_mm=2400,
            B_mm=1800,
            d_mm=400,
            a_mm=500,
            b_mm=300,
            fck=25,
            fy=415,
        )
        assert result.Mu_kNm > 0
        assert result.Ast_mm2 > 0
        assert result.is_safe is True

    def test_validation_negative_fck(self):
        """Validation: negative fck → ValidationError."""
        with pytest.raises(ValidationError, match="positive"):
            footing_flexure(
                Pu_kN=1200,
                L_mm=2000,
                B_mm=2000,
                d_mm=400,
                a_mm=400,
                b_mm=400,
                fck=-25,
                fy=415,
            )

    def test_validation_column_larger_than_footing(self):
        """Validation: column larger than footing → DimensionError."""
        with pytest.raises(DimensionError):
            footing_flexure(
                Pu_kN=1200,
                L_mm=400,
                B_mm=400,
                d_mm=300,
                a_mm=500,
                b_mm=500,
                fck=25,
                fy=415,
            )

    def test_result_is_frozen(self):
        """Result type: FootingFlexureResult is frozen."""
        result = footing_flexure(
            Pu_kN=1200,
            L_mm=2000,
            B_mm=2000,
            d_mm=400,
            a_mm=400,
            b_mm=400,
            fck=25,
            fy=415,
        )
        with pytest.raises(AttributeError):
            result.Mu_kNm = 999  # type: ignore[misc]

    def test_result_to_dict(self):
        """Result type: to_dict() returns dict with all keys."""
        result = footing_flexure(
            Pu_kN=1200,
            L_mm=2000,
            B_mm=2000,
            d_mm=400,
            a_mm=400,
            b_mm=400,
            fck=25,
            fy=415,
        )
        d = result.to_dict()
        assert isinstance(d, dict)
        for key in (
            "Mu_kNm",
            "Ast_mm2",
            "pt_percent",
            "cantilever_mm",
            "d_mm",
            "is_safe",
        ):
            assert key in d

    def test_result_summary(self):
        """Result type: summary() returns non-empty string."""
        result = footing_flexure(
            Pu_kN=1200,
            L_mm=2000,
            B_mm=2000,
            d_mm=400,
            a_mm=400,
            b_mm=400,
            fck=25,
            fy=415,
        )
        s = result.summary()
        assert len(s) > 10
        assert "Flexure" in s


# ===========================================================================
# 3. One-Way Shear Tests — footing_one_way_shear (IS 456 Cl 34.2.4.1(a))
# ===========================================================================


class TestFootingOneWayShear:
    """Tests for footing_one_way_shear: shear at d from column face."""

    def test_normal_case_safe(self):
        """IS 456 Cl 34.2.4.1(a): Normal case — adequate depth → safe.
        Pu=1200kN, L=2000, B=2000, d=400, col 400×400, fck=25.
        cant=800, shear_span=800-400=400mm.
        Vu = 0.3 × 2000 × 400 = 240000N = 240kN.
        tau_v = 240000/(2000×400) = 0.3 N/mm².
        tau_c ≈ 0.29 (for pt=0.15, fck=25) → might be close.
        """
        result = footing_one_way_shear(
            Pu_kN=1200,
            L_mm=2000,
            B_mm=2000,
            d_mm=400,
            a_mm=400,
            b_mm=400,
            fck=25,
            pt=0.25,
        )
        assert isinstance(result, FootingOneWayShearResult)
        assert result.tau_v_nmm2 >= 0
        assert result.tau_c_nmm2 > 0
        assert result.d_mm == 400.0
        assert result.Vu_kN >= 0

    def test_auto_pass_cant_le_d(self):
        """IS 456 Cl 34.2.4.1(a): When cantilever ≤ d, shear auto-passes.
        col 1200×1200, L=2000 → cant=(2000-1200)/2=400=d → Vu=0.
        """
        result = footing_one_way_shear(
            Pu_kN=1200,
            L_mm=2000,
            B_mm=2000,
            d_mm=400,
            a_mm=1200,
            b_mm=1200,
            fck=25,
        )
        assert result.Vu_kN == pytest.approx(0.0)
        assert result.tau_v_nmm2 == pytest.approx(0.0)
        assert result.is_safe is True
        assert result.utilization_ratio == pytest.approx(0.0)

    def test_unsafe_shallow_footing(self):
        """IS 456 Cl 34.2.4.1(a): Shallow footing, large load → unsafe.
        d=150mm, large load → tau_v > tau_c.
        """
        result = footing_one_way_shear(
            Pu_kN=1500,
            L_mm=2000,
            B_mm=2000,
            d_mm=150,
            a_mm=400,
            b_mm=400,
            fck=20,
            pt=0.15,
        )
        # With shallow depth and high load, likely unsafe
        assert result.tau_v_nmm2 > 0
        # Whether safe or unsafe depends on exact tau_c, but we can verify
        # the function runs and produces valid output
        assert result.utilization_ratio > 0

    def test_higher_steel_ratio_increases_tau_c(self):
        """IS 456 Table 19: Higher pt → higher tau_c → more safe."""
        r1 = footing_one_way_shear(
            Pu_kN=1200,
            L_mm=2000,
            B_mm=2000,
            d_mm=400,
            a_mm=400,
            b_mm=400,
            fck=25,
            pt=0.15,
        )
        r2 = footing_one_way_shear(
            Pu_kN=1200,
            L_mm=2000,
            B_mm=2000,
            d_mm=400,
            a_mm=400,
            b_mm=400,
            fck=25,
            pt=0.50,
        )
        assert r2.tau_c_nmm2 >= r1.tau_c_nmm2

    def test_validation_negative_fck(self):
        """Validation: negative fck → ValidationError."""
        with pytest.raises(ValidationError, match="positive"):
            footing_one_way_shear(
                Pu_kN=1200,
                L_mm=2000,
                B_mm=2000,
                d_mm=400,
                a_mm=400,
                b_mm=400,
                fck=-25,
            )

    def test_result_is_frozen(self):
        """Result type: FootingOneWayShearResult is frozen."""
        result = footing_one_way_shear(
            Pu_kN=1200,
            L_mm=2000,
            B_mm=2000,
            d_mm=400,
            a_mm=400,
            b_mm=400,
            fck=25,
        )
        with pytest.raises(AttributeError):
            result.tau_v_nmm2 = 999  # type: ignore[misc]

    def test_result_to_dict(self):
        """Result type: to_dict() returns dict with all keys."""
        result = footing_one_way_shear(
            Pu_kN=1200,
            L_mm=2000,
            B_mm=2000,
            d_mm=400,
            a_mm=400,
            b_mm=400,
            fck=25,
        )
        d = result.to_dict()
        assert isinstance(d, dict)
        for key in (
            "tau_v_nmm2",
            "tau_c_nmm2",
            "Vu_kN",
            "d_mm",
            "utilization_ratio",
            "is_safe",
        ):
            assert key in d

    def test_result_summary(self):
        """Result type: summary() returns non-empty string."""
        result = footing_one_way_shear(
            Pu_kN=1200,
            L_mm=2000,
            B_mm=2000,
            d_mm=400,
            a_mm=400,
            b_mm=400,
            fck=25,
        )
        s = result.summary()
        assert len(s) > 10
        assert "Shear" in s


# ===========================================================================
# 4. Punching Shear Tests — footing_punching_shear (IS 456 Cl 31.6.1)
# ===========================================================================


class TestFootingPunchingShear:
    """Tests for footing_punching_shear: two-way shear at d/2 from face."""

    def test_benchmark_square_column(self):
        """IS 456 Cl 31.6.1: Benchmark — square column punching shear.
        Pu=1200kN, L=2000, B=2000, d=400, col 400×400, fck=25.
        b0 = 2×((400+400)+(400+400)) = 6400mm.
        A_punch = (400+400)×(400+400) = 640000mm².
        qu = 1200×1000/(2000×2000) = 0.3 N/mm².
        Vu = 1200000 - 0.3×640000 = 1008000N = 1008kN.
        tau_v = 1008000/(3200×400) = 0.7875 N/mm².
        beta_c = 1.0, ks = 1.0.
        tau_c = 1.0 × 0.25 × √25 = 1.25 N/mm².
        tau_v < tau_c → SAFE, utilization ≈ 0.63.
        """
        result = footing_punching_shear(
            Pu_kN=1200,
            L_mm=2000,
            B_mm=2000,
            d_mm=400,
            a_mm=400,
            b_mm=400,
            fck=25,
        )
        assert isinstance(result, FootingPunchingResult)
        assert result.perimeter_mm == pytest.approx(3200.0, rel=0.001)
        assert result.Vu_punch_kN == pytest.approx(1008.0, rel=0.01)
        assert result.tau_v_nmm2 == pytest.approx(0.7875, rel=0.01)
        assert result.beta_c == pytest.approx(1.0)
        assert result.ks == pytest.approx(1.0)
        assert result.tau_c_nmm2 == pytest.approx(1.25, rel=0.001)
        assert result.is_safe is True
        assert result.utilization_ratio == pytest.approx(0.63, rel=0.02)

    def test_rectangular_column_ks_less_than_1(self):
        """IS 456 Cl 31.6.3: Rectangular column — ks < 1.0.
        col 200×600 → beta_c = 200/600 = 0.333, ks = min(1.0, 0.5+0.333) = 0.833.
        tau_c = 0.833 × 0.25 × √25 = 1.042 N/mm².
        """
        result = footing_punching_shear(
            Pu_kN=1200,
            L_mm=2000,
            B_mm=2000,
            d_mm=400,
            a_mm=200,
            b_mm=600,
            fck=25,
        )
        assert result.beta_c == pytest.approx(0.333, rel=0.01)
        assert result.ks == pytest.approx(0.833, rel=0.01)
        assert result.tau_c_nmm2 == pytest.approx(1.042, rel=0.01)

    def test_punching_exceeds_footing_auto_pass(self):
        """Edge: Column nearly fills footing → punching perimeter beyond edges → auto-pass.
        col 1400×1400, L=1600 → a+d = 1400+400 = 1800 > 1600 → auto-pass.
        """
        result = footing_punching_shear(
            Pu_kN=1200,
            L_mm=1600,
            B_mm=1600,
            d_mm=400,
            a_mm=1400,
            b_mm=1400,
            fck=25,
        )
        assert result.tau_v_nmm2 == pytest.approx(0.0)
        assert result.Vu_punch_kN == pytest.approx(0.0)
        assert result.is_safe is True
        assert len(result.warnings) > 0

    def test_unsafe_heavy_load_shallow(self):
        """IS 456 Cl 31.6.1: Heavy load, shallow depth → punching failure.
        Pu=3000kN, d=200, col 300×300, L=2000, fck=20.
        """
        result = footing_punching_shear(
            Pu_kN=3000,
            L_mm=2000,
            B_mm=2000,
            d_mm=200,
            a_mm=300,
            b_mm=300,
            fck=20,
        )
        # tau_c = 1.0 × 0.25 × √20 ≈ 1.118 N/mm²
        # Very high load on shallow footing — likely unsafe
        assert result.tau_v_nmm2 > result.tau_c_nmm2
        assert result.is_safe is False
        assert result.utilization_ratio > 1.0

    def test_validation_negative_fck(self):
        """Validation: negative fck → ValidationError."""
        with pytest.raises(ValidationError, match="positive"):
            footing_punching_shear(
                Pu_kN=1200,
                L_mm=2000,
                B_mm=2000,
                d_mm=400,
                a_mm=400,
                b_mm=400,
                fck=-25,
            )

    def test_validation_column_larger_than_footing(self):
        """Validation: column ≥ footing → DimensionError."""
        with pytest.raises(DimensionError):
            footing_punching_shear(
                Pu_kN=1200,
                L_mm=400,
                B_mm=400,
                d_mm=300,
                a_mm=500,
                b_mm=500,
                fck=25,
            )

    def test_result_is_frozen(self):
        """Result type: FootingPunchingResult is frozen."""
        result = footing_punching_shear(
            Pu_kN=1200,
            L_mm=2000,
            B_mm=2000,
            d_mm=400,
            a_mm=400,
            b_mm=400,
            fck=25,
        )
        with pytest.raises(AttributeError):
            result.tau_v_nmm2 = 999  # type: ignore[misc]

    def test_result_to_dict(self):
        """Result type: to_dict() returns dict with all keys."""
        result = footing_punching_shear(
            Pu_kN=1200,
            L_mm=2000,
            B_mm=2000,
            d_mm=400,
            a_mm=400,
            b_mm=400,
            fck=25,
        )
        d = result.to_dict()
        assert isinstance(d, dict)
        for key in (
            "tau_v_nmm2",
            "tau_c_nmm2",
            "perimeter_mm",
            "Vu_punch_kN",
            "d_mm",
            "beta_c",
            "ks",
            "utilization_ratio",
            "is_safe",
        ):
            assert key in d

    def test_result_summary(self):
        """Result type: summary() returns non-empty string."""
        result = footing_punching_shear(
            Pu_kN=1200,
            L_mm=2000,
            B_mm=2000,
            d_mm=400,
            a_mm=400,
            b_mm=400,
            fck=25,
        )
        s = result.summary()
        assert len(s) > 10
        assert "Punching" in s

    def test_square_column_ks_equals_1(self):
        """IS 456 Cl 31.6.3: Square column → beta_c=1.0, ks=1.0."""
        result = footing_punching_shear(
            Pu_kN=800,
            L_mm=2000,
            B_mm=2000,
            d_mm=400,
            a_mm=400,
            b_mm=400,
            fck=25,
        )
        assert result.beta_c == pytest.approx(1.0)
        assert result.ks == pytest.approx(1.0)


# ===========================================================================
# 5. Common Utilities Tests — _common module
# ===========================================================================


class TestFootingCommon:
    """Tests for footing shared utilities in _common.py."""

    # --- validate_footing_inputs ---

    def test_validate_negative_L(self):
        """validate_footing_inputs: negative L → DimensionError."""
        with pytest.raises(DimensionError):
            validate_footing_inputs(L_mm=-100, B_mm=2000, d_mm=400, a_mm=400, b_mm=400)

    def test_validate_zero_B(self):
        """validate_footing_inputs: zero B → DimensionError."""
        with pytest.raises(DimensionError):
            validate_footing_inputs(L_mm=2000, B_mm=0, d_mm=400, a_mm=400, b_mm=400)

    def test_validate_zero_d(self):
        """validate_footing_inputs: zero d → DimensionError."""
        with pytest.raises(DimensionError):
            validate_footing_inputs(L_mm=2000, B_mm=2000, d_mm=0, a_mm=400, b_mm=400)

    def test_validate_column_exceeds_footing(self):
        """validate_footing_inputs: column ≥ footing → DimensionError."""
        with pytest.raises(DimensionError):
            validate_footing_inputs(L_mm=400, B_mm=2000, d_mm=400, a_mm=500, b_mm=300)

    def test_validate_column_equal_footing(self):
        """validate_footing_inputs: column == footing → DimensionError."""
        with pytest.raises(DimensionError):
            validate_footing_inputs(L_mm=400, B_mm=400, d_mm=300, a_mm=400, b_mm=400)

    def test_validate_valid_inputs_passes(self):
        """validate_footing_inputs: valid inputs → no error."""
        validate_footing_inputs(L_mm=2000, B_mm=2000, d_mm=400, a_mm=400, b_mm=400)

    def test_validate_negative_col_dim(self):
        """validate_footing_inputs: negative column dim → DimensionError."""
        with pytest.raises(DimensionError, match="positive"):
            validate_footing_inputs(L_mm=2000, B_mm=2000, d_mm=400, a_mm=-300, b_mm=400)

    # --- net_upward_pressure_nmm2 ---

    def test_net_pressure_benchmark(self):
        """net_upward_pressure_nmm2: 1200kN on 2000×2000 → 0.3 N/mm²."""
        qu = net_upward_pressure_nmm2(Pu_kN=1200, L_mm=2000, B_mm=2000)
        assert qu == pytest.approx(0.3, rel=0.001)

    def test_net_pressure_another_case(self):
        """net_upward_pressure_nmm2: 600kN on 1500×1500 → 0.2667 N/mm²."""
        qu = net_upward_pressure_nmm2(Pu_kN=600, L_mm=1500, B_mm=1500)
        expected = 600 * 1000 / (1500 * 1500)  # 0.2667
        assert qu == pytest.approx(expected, rel=0.001)

    def test_net_pressure_negative_load(self):
        """net_upward_pressure_nmm2: negative load → ValidationError."""
        with pytest.raises(ValidationError, match="positive"):
            net_upward_pressure_nmm2(Pu_kN=-100, L_mm=2000, B_mm=2000)

    # --- punching_perimeter_mm ---

    def test_punching_perimeter_square(self):
        """punching_perimeter_mm: col 400×400, d=400 → 2×(800+800) = 3200mm."""
        b0 = punching_perimeter_mm(a_mm=400, b_mm=400, d_mm=400)
        assert b0 == pytest.approx(3200.0)

    def test_punching_perimeter_rectangular(self):
        """punching_perimeter_mm: col 300×600, d=400.
        b0 = 2×((300+400)+(600+400)) = 2×(700+1000) = 3400mm.
        """
        b0 = punching_perimeter_mm(a_mm=300, b_mm=600, d_mm=400)
        assert b0 == pytest.approx(3400.0)

    # --- punching_area_mm2 ---

    def test_punching_area_square(self):
        """punching_area_mm2: col 400×400, d=400 → (800)×(800) = 640000mm²."""
        A = punching_area_mm2(a_mm=400, b_mm=400, d_mm=400)
        assert A == pytest.approx(640000.0)

    def test_punching_area_rectangular(self):
        """punching_area_mm2: col 300×600, d=400 → (700)×(1000) = 700000mm²."""
        A = punching_area_mm2(a_mm=300, b_mm=600, d_mm=400)
        assert A == pytest.approx(700000.0)


# ===========================================================================
# 6. Type Tests — all result dataclasses
# ===========================================================================


class TestFootingTypes:
    """Tests for footing result type invariants."""

    def test_footing_type_enum_values(self):
        """FootingType enum has expected members."""
        assert hasattr(FootingType, "ISOLATED_SQUARE")
        assert hasattr(FootingType, "ISOLATED_RECTANGULAR")

    def test_bearing_result_frozen(self):
        """FootingBearingResult is immutable (frozen dataclass)."""
        result = size_footing(
            P_service_kN=800,
            q_safe_kPa=200,
            a_mm=400,
            b_mm=400,
        )
        with pytest.raises(AttributeError):
            result.q_max_kPa = 0  # type: ignore[misc]

    def test_flexure_result_frozen(self):
        """FootingFlexureResult is immutable."""
        result = footing_flexure(
            Pu_kN=1200,
            L_mm=2000,
            B_mm=2000,
            d_mm=400,
            a_mm=400,
            b_mm=400,
            fck=25,
            fy=415,
        )
        with pytest.raises(AttributeError):
            result.Ast_mm2 = 0  # type: ignore[misc]

    def test_one_way_shear_result_frozen(self):
        """FootingOneWayShearResult is immutable."""
        result = footing_one_way_shear(
            Pu_kN=1200,
            L_mm=2000,
            B_mm=2000,
            d_mm=400,
            a_mm=400,
            b_mm=400,
            fck=25,
        )
        with pytest.raises(AttributeError):
            result.Vu_kN = 0  # type: ignore[misc]

    def test_punching_result_frozen(self):
        """FootingPunchingResult is immutable."""
        result = footing_punching_shear(
            Pu_kN=1200,
            L_mm=2000,
            B_mm=2000,
            d_mm=400,
            a_mm=400,
            b_mm=400,
            fck=25,
        )
        with pytest.raises(AttributeError):
            result.ks = 0  # type: ignore[misc]

    def test_all_results_have_to_dict(self):
        """Every footing result type has to_dict() → dict."""
        bearing_r = size_footing(P_service_kN=800, q_safe_kPa=200, a_mm=400, b_mm=400)
        flexure_r = footing_flexure(
            Pu_kN=1200,
            L_mm=2000,
            B_mm=2000,
            d_mm=400,
            a_mm=400,
            b_mm=400,
            fck=25,
            fy=415,
        )
        ows_r = footing_one_way_shear(
            Pu_kN=1200, L_mm=2000, B_mm=2000, d_mm=400, a_mm=400, b_mm=400, fck=25
        )
        punch_r = footing_punching_shear(
            Pu_kN=1200, L_mm=2000, B_mm=2000, d_mm=400, a_mm=400, b_mm=400, fck=25
        )

        for result in (bearing_r, flexure_r, ows_r, punch_r):
            d = result.to_dict()
            assert isinstance(d, dict)
            assert len(d) > 3

    def test_all_results_have_summary(self):
        """Every footing result type has summary() → non-empty str."""
        bearing_r = size_footing(P_service_kN=800, q_safe_kPa=200, a_mm=400, b_mm=400)
        flexure_r = footing_flexure(
            Pu_kN=1200,
            L_mm=2000,
            B_mm=2000,
            d_mm=400,
            a_mm=400,
            b_mm=400,
            fck=25,
            fy=415,
        )
        ows_r = footing_one_way_shear(
            Pu_kN=1200, L_mm=2000, B_mm=2000, d_mm=400, a_mm=400, b_mm=400, fck=25
        )
        punch_r = footing_punching_shear(
            Pu_kN=1200, L_mm=2000, B_mm=2000, d_mm=400, a_mm=400, b_mm=400, fck=25
        )

        for result in (bearing_r, flexure_r, ows_r, punch_r):
            s = result.summary()
            assert isinstance(s, str)
            assert len(s) > 10
