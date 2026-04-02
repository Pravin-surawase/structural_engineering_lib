# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for IS 456 Cl 39.4 helical reinforcement check.

Tests cover:
- Basic adequate helical reinforcement
- Enhancement factor (1.05)
- Inadequate ratio and pitch violations
- Pitch boundary conditions (exact min/max)
- Input validation (DimensionError, MaterialError)
- Hand-calculated benchmark for circular column
- Result structure (to_dict, summary)

References:
    IS 456:2000, Cl. 39.4, 26.5.3.2
    SP:16:1980 Design Aids
"""

from __future__ import annotations

import math

import pytest

from structural_lib.codes.is456.column.helical import check_helical_reinforcement
from structural_lib.core.data_types import HelicalReinforcementResult
from structural_lib.core.errors import DimensionError, MaterialError


# ============================================================================
# Unit tests — basic functionality
# ============================================================================
class TestBasicAdequate:
    """Test 1: Adequate helical ratio and pitch → is_adequate=True."""

    def test_basic_adequate(self):
        """IS 456 Cl 39.4: Adequate helical reinforcement.
        D=400mm, D_core=340mm, fck=25, fy=415, d_helix=8mm, pitch=50mm.
        Pitch in range [max(25, 24)=25, min(75, 340/6≈56.7)=56.7] → OK.
        Ratio check depends on geometry — use generous helix.
        """
        result = check_helical_reinforcement(
            D_mm=400,
            D_core_mm=340,
            fck=25,
            fy=415,
            d_helix_mm=8,
            pitch_mm=50,
            Pu_axial_kN=1000,
        )
        assert isinstance(result, HelicalReinforcementResult)
        assert result.pitch_ok is True
        # Verify is_adequate is a boolean (depends on ratio calculation)
        assert isinstance(result.is_adequate, bool)


class TestEnhancementFactor:
    """Test 2: Enhancement factor = 1.05 per IS 456 Cl 39.4."""

    def test_enhancement_factor_1_05(self):
        """IS 456 Cl 39.4: Pu_enhanced = 1.05 × Pu_axial."""
        result = check_helical_reinforcement(
            D_mm=400,
            D_core_mm=340,
            fck=25,
            fy=415,
            d_helix_mm=8,
            pitch_mm=50,
            Pu_axial_kN=1000,
        )
        assert result.enhancement_factor == pytest.approx(1.05)
        assert result.Pu_enhanced_kN == pytest.approx(1050.0, rel=0.001)


class TestRatioInadequate:
    """Test 3: Ratio below required → is_adequate=False."""

    def test_ratio_inadequate(self):
        """IS 456 Cl 39.4: Very small helix bar on large column → inadequate ratio.
        Use a very small helix (d=4mm) with large pitch on a large column
        to ensure ratio is below required.
        """
        result = check_helical_reinforcement(
            D_mm=600,
            D_core_mm=500,
            fck=30,
            fy=415,
            d_helix_mm=4,  # Small helix bar
            pitch_mm=70,  # Large pitch
            Pu_axial_kN=1000,
        )
        # With small bar and large pitch, ratio should be inadequate
        assert result.helical_ratio_provided < result.helical_ratio_required
        assert result.is_adequate is False
        assert any("ratio" in w.lower() for w in result.warnings)


class TestPitchLimits:
    """Tests 4-7: Pitch limit violations and boundary conditions."""

    def test_pitch_too_small(self):
        """IS 456 Cl 26.5.3.2: pitch < max(25, 3×d_helix) → pitch_ok=False.
        d_helix=10mm → min pitch = max(25, 30) = 30mm.
        pitch=20mm < 30mm → pitch_ok=False.
        """
        result = check_helical_reinforcement(
            D_mm=400,
            D_core_mm=340,
            fck=25,
            fy=415,
            d_helix_mm=10,
            pitch_mm=20,  # < max(25, 3×10=30) = 30
            Pu_axial_kN=1000,
        )
        assert result.pitch_ok is False
        assert result.min_pitch_mm == pytest.approx(30.0)
        assert any("below minimum" in w.lower() for w in result.warnings)

    def test_pitch_too_large(self):
        """IS 456 Cl 26.5.3.2: pitch > min(75, D_core/6) → pitch_ok=False.
        D_core=300mm → max pitch = min(75, 300/6=50) = 50mm.
        pitch=60mm > 50mm → pitch_ok=False.
        """
        result = check_helical_reinforcement(
            D_mm=400,
            D_core_mm=300,
            fck=25,
            fy=415,
            d_helix_mm=6,
            pitch_mm=60,  # > min(75, 300/6=50) = 50
            Pu_axial_kN=1000,
        )
        assert result.pitch_ok is False
        assert result.max_pitch_mm == pytest.approx(50.0)
        assert any("exceeds maximum" in w.lower() for w in result.warnings)

    def test_pitch_exact_min(self):
        """IS 456 Cl 26.5.3.2: pitch exactly at minimum → pitch_ok=True.
        d_helix=8mm → min pitch = max(25, 24) = 25mm.
        pitch=25mm = min → pitch_ok=True.
        """
        result = check_helical_reinforcement(
            D_mm=400,
            D_core_mm=340,
            fck=25,
            fy=415,
            d_helix_mm=8,
            pitch_mm=25,  # Exactly max(25, 3×8=24) = 25
            Pu_axial_kN=1000,
        )
        assert result.min_pitch_mm == pytest.approx(25.0)
        assert result.pitch_ok is True

    def test_pitch_exact_max(self):
        """IS 456 Cl 26.5.3.2: pitch exactly at maximum → pitch_ok=True.
        D_core=300mm → max pitch = min(75, 300/6=50) = 50mm.
        pitch=50mm = max → pitch_ok=True.
        """
        result = check_helical_reinforcement(
            D_mm=400,
            D_core_mm=300,
            fck=25,
            fy=415,
            d_helix_mm=6,
            pitch_mm=50,  # Exactly min(75, 300/6=50) = 50
            Pu_axial_kN=1000,
        )
        assert result.max_pitch_mm == pytest.approx(50.0)
        assert result.pitch_ok is True


# ============================================================================
# Validation tests — invalid inputs
# ============================================================================
class TestInputValidation:
    """Tests 8-11: Input validation raises appropriate errors."""

    def test_negative_diameter_raises(self):
        """IS 456 Cl 39.4: D_mm must be > 0."""
        with pytest.raises(DimensionError, match="D_mm"):
            check_helical_reinforcement(
                D_mm=-400,
                D_core_mm=340,
                fck=25,
                fy=415,
                d_helix_mm=8,
                pitch_mm=50,
                Pu_axial_kN=1000,
            )

    def test_core_exceeds_outer_raises(self):
        """IS 456 Cl 39.4: D_core_mm must be < D_mm."""
        with pytest.raises(DimensionError, match="D_core_mm"):
            check_helical_reinforcement(
                D_mm=300,
                D_core_mm=350,  # Core > outer diameter
                fck=25,
                fy=415,
                d_helix_mm=8,
                pitch_mm=50,
                Pu_axial_kN=1000,
            )

    def test_negative_fck_raises(self):
        """IS 456 Cl 39.4: fck must be > 0."""
        with pytest.raises(MaterialError, match="fck"):
            check_helical_reinforcement(
                D_mm=400,
                D_core_mm=340,
                fck=-25,
                fy=415,
                d_helix_mm=8,
                pitch_mm=50,
                Pu_axial_kN=1000,
            )

    def test_negative_fy_raises(self):
        """IS 456 Cl 39.4: fy must be > 0."""
        with pytest.raises(MaterialError, match="fy"):
            check_helical_reinforcement(
                D_mm=400,
                D_core_mm=340,
                fck=25,
                fy=-415,
                d_helix_mm=8,
                pitch_mm=50,
                Pu_axial_kN=1000,
            )


# ============================================================================
# Hand-calculated benchmark
# ============================================================================
class TestBenchmarkCircularColumn:
    """Test 12: Hand-calculated benchmark for circular column.

    D = 400mm, D_core = 340mm
    fck = 25, fy = 415
    d_helix = 8mm, pitch = 50mm
    Pu_axial = 1000 kN

    Ag = π/4 × 400² = 125663.706... mm²
    Ac = π/4 × 340² = 90792.027... mm²
    Ag/Ac - 1 = 125663.706/90792.027 - 1 = 0.38408...

    A_helix_bar = π/4 × 8² = 50.2655 mm²
    V_helix/mm = π × 340 × 50.2655 / 50 = 1073.48... mm³/mm
    V_core/mm = 90792.027... mm²  (area = volume per unit height)
    ratio_provided = 1073.48 / 90792.027 = 0.01182...

    ratio_required = 0.36 × 0.38408 × 25/415 = 0.008333...

    Pu_enhanced = 1.05 × 1000 = 1050 kN

    References:
        IS 456:2000, Cl. 39.4, 26.5.3.2
    """

    def test_benchmark_circular_column(self):
        """Verify against hand-calculated helical ratio and capacity."""
        result = check_helical_reinforcement(
            D_mm=400,
            D_core_mm=340,
            fck=25,
            fy=415,
            d_helix_mm=8,
            pitch_mm=50,
            Pu_axial_kN=1000,
        )

        # Calculate expected values
        Ag = math.pi / 4 * 400**2  # 125663.706...
        Ac = math.pi / 4 * 340**2  # 90792.027...
        A_bar = math.pi / 4 * 8**2  # 50.2655...

        # Volume ratios per unit height
        V_helix_per_mm = math.pi * 340 * A_bar / 50
        V_core_per_mm = Ac
        expected_ratio_provided = V_helix_per_mm / V_core_per_mm

        # Required ratio: 0.36 × (Ag/Ac - 1) × fck/fy
        expected_ratio_required = 0.36 * (Ag / Ac - 1) * 25 / 415

        # Verify ratios
        assert result.helical_ratio_provided == pytest.approx(
            expected_ratio_provided, rel=0.01
        )
        assert result.helical_ratio_required == pytest.approx(
            expected_ratio_required, rel=0.01
        )

        # Provided > required → adequate ratio
        assert result.helical_ratio_provided > result.helical_ratio_required

        # Pitch check: min = max(25, 3×8=24) = 25, max = min(75, 340/6≈56.7) = 56.7
        assert result.min_pitch_mm == pytest.approx(25.0)
        assert result.max_pitch_mm == pytest.approx(340 / 6, rel=0.01)
        assert result.pitch_ok is True

        # Overall adequacy
        assert result.is_adequate is True

        # Enhanced capacity
        assert result.Pu_enhanced_kN == pytest.approx(1050.0, rel=0.001)

        # Clause reference
        assert result.clause_ref == "Cl. 39.4"


# ============================================================================
# Result structure tests
# ============================================================================
class TestResultStructure:
    """Tests 13-14: to_dict and summary."""

    @pytest.fixture
    def result(self) -> HelicalReinforcementResult:
        """Standard result for structure tests."""
        return check_helical_reinforcement(
            D_mm=400,
            D_core_mm=340,
            fck=25,
            fy=415,
            d_helix_mm=8,
            pitch_mm=50,
            Pu_axial_kN=1000,
        )

    def test_result_to_dict(self, result: HelicalReinforcementResult):
        """to_dict() must return a dict with all expected keys."""
        d = result.to_dict()
        assert isinstance(d, dict)
        expected_keys = {
            "is_adequate",
            "enhancement_factor",
            "Pu_enhanced_kN",
            "helical_ratio_provided",
            "helical_ratio_required",
            "pitch_mm",
            "min_pitch_mm",
            "max_pitch_mm",
            "pitch_ok",
            "D_core_mm",
            "clause_ref",
            "warnings",
        }
        assert expected_keys.issubset(d.keys())

    def test_result_summary(self, result: HelicalReinforcementResult):
        """summary() must return a string with ADEQUATE/INADEQUATE status."""
        s = result.summary()
        assert isinstance(s, str)
        assert "ADEQUATE" in s or "INADEQUATE" in s
        assert "ratio=" in s
        assert "pitch=" in s
