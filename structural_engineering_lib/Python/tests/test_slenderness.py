# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Unit tests for slenderness module.

Tests cover:
- Slenderness ratio calculation
- Slenderness limit lookup
- Beam slenderness check (IS 456 Cl 23.3)
- Edge cases and error handling
"""

from __future__ import annotations

import pytest

from structural_lib.codes.is456.slenderness import (
    BeamType,
    SlendernessResult,
    calculate_slenderness_ratio,
    check_beam_slenderness,
    get_slenderness_limit,
)


class TestGetSlendernessLimit:
    """Tests for get_slenderness_limit function."""

    def test_simply_supported_limit(self) -> None:
        """IS 456 Cl 23.3: Simply supported beam limit = 60."""
        assert get_slenderness_limit(BeamType.SIMPLY_SUPPORTED) == 60.0

    def test_continuous_limit(self) -> None:
        """IS 456 Cl 23.3: Continuous beam limit = 60."""
        assert get_slenderness_limit(BeamType.CONTINUOUS) == 60.0

    def test_cantilever_limit(self) -> None:
        """IS 456 Cl 23.3: Cantilever beam limit = 25."""
        assert get_slenderness_limit(BeamType.CANTILEVER) == 25.0

    def test_string_alias_ss(self) -> None:
        """String alias 'ss' maps to simply supported."""
        assert get_slenderness_limit("ss") == 60.0

    def test_string_alias_cant(self) -> None:
        """String alias 'cant' maps to cantilever."""
        assert get_slenderness_limit("cant") == 25.0

    def test_string_alias_cont(self) -> None:
        """String alias 'cont' maps to continuous."""
        assert get_slenderness_limit("cont") == 60.0

    def test_invalid_beam_type_raises(self) -> None:
        """Invalid beam type raises ValueError."""
        with pytest.raises(ValueError, match="Unknown beam type"):
            get_slenderness_limit("invalid_type")


class TestCalculateSlendernessRatio:
    """Tests for calculate_slenderness_ratio function."""

    def test_basic_calculation(self) -> None:
        """Basic slenderness ratio: l_eff / b."""
        # 6000mm span, 250mm width → ratio = 24
        ratio = calculate_slenderness_ratio(6000, 250)
        assert ratio == 24.0

    def test_typical_beam(self) -> None:
        """Typical beam: 8m span, 300mm width."""
        ratio = calculate_slenderness_ratio(8000, 300)
        assert pytest.approx(ratio, rel=0.01) == 26.67

    def test_slender_beam(self) -> None:
        """Slender beam: 12m span, 200mm width → ratio = 60."""
        ratio = calculate_slenderness_ratio(12000, 200)
        assert ratio == 60.0

    def test_zero_length_raises(self) -> None:
        """Zero effective length raises ValueError."""
        with pytest.raises(ValueError, match="Effective length must be positive"):
            calculate_slenderness_ratio(0, 300)

    def test_negative_length_raises(self) -> None:
        """Negative effective length raises ValueError."""
        with pytest.raises(ValueError, match="Effective length must be positive"):
            calculate_slenderness_ratio(-1000, 300)

    def test_zero_width_raises(self) -> None:
        """Zero width raises ValueError."""
        with pytest.raises(ValueError, match="Beam width must be positive"):
            calculate_slenderness_ratio(6000, 0)

    def test_negative_width_raises(self) -> None:
        """Negative width raises ValueError."""
        with pytest.raises(ValueError, match="Beam width must be positive"):
            calculate_slenderness_ratio(6000, -200)


class TestCheckBeamSlenderness:
    """Tests for check_beam_slenderness function."""

    def test_short_beam_ok(self) -> None:
        """Short beam (low slenderness ratio) passes check."""
        # 6m span, 300mm wide, 600mm deep → ratio = 20 < 60
        result = check_beam_slenderness(
            b_mm=300,
            d_mm=600,
            l_eff_mm=6000,
            beam_type="simply_supported",
        )
        assert result.is_ok is True
        assert result.is_slender is False
        assert result.slenderness_ratio == 20.0
        assert result.slenderness_limit == 60.0
        assert result.utilization < 1.0
        assert "OK" in result.remarks

    def test_slender_beam_warning(self) -> None:
        """Slender beam (high ratio but within limit) triggers warning state."""
        # 15m span, 300mm wide → ratio = 50 (>80% of 60 limit)
        result = check_beam_slenderness(
            b_mm=300,
            d_mm=600,
            l_eff_mm=15000,
            beam_type="simply_supported",
        )
        assert result.is_ok is True  # Still OK (under limit)
        assert result.is_slender is True  # But classified as slender
        assert result.slenderness_ratio == 50.0
        assert result.utilization < 1.0

    def test_exceeds_slenderness_limit_fails(self) -> None:
        """Beam exceeding slenderness limit fails check."""
        # 20m span, 300mm wide → ratio = 66.67 > 60
        result = check_beam_slenderness(
            b_mm=300,
            d_mm=600,
            l_eff_mm=20000,
            beam_type="simply_supported",
        )
        assert result.is_ok is False
        assert result.slenderness_ratio > 60.0
        assert result.utilization > 1.0
        assert "FAIL" in result.remarks

    def test_cantilever_stricter_limit(self) -> None:
        """Cantilever uses stricter limit of 25."""
        # 5m cantilever, 200mm wide → ratio = 25 (at limit)
        result = check_beam_slenderness(
            b_mm=200,
            d_mm=500,
            l_eff_mm=5000,
            beam_type="cantilever",
        )
        assert result.is_ok is True
        assert result.slenderness_limit == 25.0
        assert result.slenderness_ratio == 25.0

        # 6m cantilever, 200mm wide → ratio = 30 > 25 (fails)
        result_fail = check_beam_slenderness(
            b_mm=200,
            d_mm=500,
            l_eff_mm=6000,
            beam_type="cantilever",
        )
        assert result_fail.is_ok is False
        assert result_fail.slenderness_ratio == 30.0

    def test_lateral_restraint_assumption(self) -> None:
        """Laterally restrained beam records assumption."""
        result = check_beam_slenderness(
            b_mm=300,
            d_mm=600,
            l_eff_mm=6000,
            has_lateral_restraint=True,
        )
        assert result.is_ok is True
        assert any("restrained" in a.lower() for a in result.assumptions)

    def test_deep_narrow_beam_warning(self) -> None:
        """Deep narrow beam (D/b > 4) triggers warning."""
        # 200mm wide, 1000mm deep → D/b = 5
        result = check_beam_slenderness(
            b_mm=200,
            d_mm=1000,
            l_eff_mm=6000,
            beam_type="simply_supported",
        )
        assert result.is_ok is True  # Still OK (within slenderness)
        assert result.depth_to_width_ratio == 5.0
        assert len(result.warnings) > 0
        assert any("D/b" in w for w in result.warnings)

    def test_very_deep_narrow_beam_fails(self) -> None:
        """Very deep narrow beam (D/b > 6) fails check."""
        # 150mm wide, 1000mm deep → D/b = 6.67
        result = check_beam_slenderness(
            b_mm=150,
            d_mm=1000,
            l_eff_mm=6000,
            beam_type="simply_supported",
            has_lateral_restraint=False,
        )
        assert result.is_ok is False
        assert result.depth_to_width_ratio > 6.0
        assert len(result.errors) > 0

    def test_invalid_width_returns_error_result(self) -> None:
        """Zero width returns error result (not exception)."""
        result = check_beam_slenderness(
            b_mm=0,
            d_mm=600,
            l_eff_mm=6000,
        )
        assert result.is_ok is False
        assert len(result.errors) > 0
        assert "width" in result.errors[0].lower()

    def test_invalid_depth_returns_error_result(self) -> None:
        """Zero depth returns error result."""
        result = check_beam_slenderness(
            b_mm=300,
            d_mm=0,
            l_eff_mm=6000,
        )
        assert result.is_ok is False
        assert len(result.errors) > 0

    def test_invalid_length_returns_error_result(self) -> None:
        """Negative length returns error result."""
        result = check_beam_slenderness(
            b_mm=300,
            d_mm=600,
            l_eff_mm=-1000,
        )
        assert result.is_ok is False
        assert len(result.errors) > 0

    def test_result_has_all_fields(self) -> None:
        """Result includes all expected fields."""
        result = check_beam_slenderness(
            b_mm=300,
            d_mm=600,
            l_eff_mm=6000,
        )
        assert isinstance(result, SlendernessResult)
        assert hasattr(result, "is_ok")
        assert hasattr(result, "is_slender")
        assert hasattr(result, "slenderness_ratio")
        assert hasattr(result, "slenderness_limit")
        assert hasattr(result, "utilization")
        assert hasattr(result, "depth_to_width_ratio")
        assert hasattr(result, "remarks")
        assert hasattr(result, "inputs")
        assert hasattr(result, "computed")

    def test_inputs_recorded(self) -> None:
        """Input values are recorded in result."""
        result = check_beam_slenderness(
            b_mm=300,
            d_mm=600,
            l_eff_mm=6000,
            beam_type="continuous",
        )
        assert result.inputs.get("b_mm") == 300
        assert result.inputs.get("d_mm") == 600
        assert result.inputs.get("l_eff_mm") == 6000
        assert result.inputs.get("beam_type") == "continuous"

    def test_computed_values_recorded(self) -> None:
        """Computed values are recorded in result."""
        result = check_beam_slenderness(
            b_mm=300,
            d_mm=600,
            l_eff_mm=6000,
        )
        assert "slenderness_ratio" in result.computed
        assert "slenderness_limit" in result.computed
        assert "depth_width_ratio" in result.computed
        assert "utilization" in result.computed


class TestBeamTypeEnum:
    """Tests for BeamType enum."""

    def test_enum_values(self) -> None:
        """BeamType has expected values."""
        assert BeamType.SIMPLY_SUPPORTED.value == "simply_supported"
        assert BeamType.CONTINUOUS.value == "continuous"
        assert BeamType.CANTILEVER.value == "cantilever"

    def test_enum_iteration(self) -> None:
        """Can iterate over BeamType values."""
        types = list(BeamType)
        assert len(types) == 3


class TestEdgeCases:
    """Edge case tests for slenderness functions."""

    def test_exactly_at_limit(self) -> None:
        """Beam exactly at slenderness limit passes."""
        # Exactly at limit = 60
        result = check_beam_slenderness(
            b_mm=200,
            d_mm=600,
            l_eff_mm=12000,  # 12000/200 = 60
            beam_type="simply_supported",
        )
        assert result.is_ok is True
        assert result.slenderness_ratio == 60.0
        assert result.utilization == 1.0

    def test_just_over_limit(self) -> None:
        """Beam just over slenderness limit fails."""
        result = check_beam_slenderness(
            b_mm=200,
            d_mm=600,
            l_eff_mm=12100,  # 12100/200 = 60.5 > 60
            beam_type="simply_supported",
        )
        assert result.is_ok is False
        assert result.slenderness_ratio == 60.5
        assert result.utilization > 1.0

    def test_minimum_practical_dimensions(self) -> None:
        """Minimum practical beam dimensions work."""
        result = check_beam_slenderness(
            b_mm=150,  # Minimum practical width
            d_mm=300,  # Minimum practical depth
            l_eff_mm=3000,
            beam_type="simply_supported",
        )
        assert result.is_ok is True
        assert result.slenderness_ratio == 20.0

    def test_large_span_beam(self) -> None:
        """Large span beam with adequate width passes."""
        # 20m span, 500mm wide → ratio = 40 < 60
        result = check_beam_slenderness(
            b_mm=500,
            d_mm=1200,
            l_eff_mm=20000,
            beam_type="continuous",
        )
        assert result.is_ok is True
        assert result.slenderness_ratio == 40.0

    def test_laterally_restrained_deep_beam(self) -> None:
        """Laterally restrained deep beam doesn't get D/b warning."""
        result = check_beam_slenderness(
            b_mm=200,
            d_mm=1000,  # D/b = 5
            l_eff_mm=6000,
            beam_type="simply_supported",
            has_lateral_restraint=True,
        )
        assert result.is_ok is True
        # With lateral restraint, deep beam is OK
        assert "restrained" in result.remarks.lower()
