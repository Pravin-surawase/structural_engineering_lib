"""
Test Suite for Detailing Module

Tests cover:
- Development length calculations (IS 456 Cl 26.2.1)
- Lap length calculations (IS 456 Cl 26.2.5)
- Bar spacing checks (IS 456 Cl 26.3)
- Bar arrangement selection
- Complete beam detailing
"""

import pytest

from structural_lib.detailing import (
    get_bond_stress,
    calculate_development_length,
    calculate_lap_length,
    calculate_bar_spacing,
    check_min_spacing,
    select_bar_arrangement,
    get_stirrup_legs,
    format_bar_callout,
    format_stirrup_callout,
    create_beam_detailing,
    BarArrangement,
)


class TestBondStress:
    """Tests for bond stress lookup."""

    def test_m20_deformed(self):
        """M20 deformed bar: τbd = 1.92 N/mm²"""
        tau = get_bond_stress(20, "deformed")
        assert tau == pytest.approx(1.92, rel=0.01)

    def test_m25_deformed(self):
        """M25 deformed bar: τbd = 2.24 N/mm²"""
        tau = get_bond_stress(25, "deformed")
        assert tau == pytest.approx(2.24, rel=0.01)

    def test_m30_deformed(self):
        """M30 deformed bar: τbd = 2.40 N/mm²"""
        tau = get_bond_stress(30, "deformed")
        assert tau == pytest.approx(2.40, rel=0.01)

    def test_m20_plain(self):
        """M20 plain bar: τbd = 1.2 N/mm² (1.92/1.6)"""
        tau = get_bond_stress(20, "plain")
        assert tau == pytest.approx(1.2, rel=0.01)

    def test_intermediate_grade_uses_lower(self):
        """M22 should use M20 values (nearest lower)."""
        tau = get_bond_stress(22, "deformed")
        assert tau == pytest.approx(1.92, rel=0.01)


class TestDevelopmentLength:
    """Tests for development length calculation."""

    def test_16mm_m25_fe500(self):
        """
        16mm bar, M25, Fe500:
        Ld = (16 × 0.87 × 500) / (4 × 2.24) = 776 mm
        Simplified: ~40φ = 640 mm (approx)
        """
        ld = calculate_development_length(16, 25, 500)
        # φ × σs / (4 × τbd) = 16 × 0.87 × 500 / (4 × 2.24)
        expected = (16 * 0.87 * 500) / (4 * 2.24)
        assert ld == pytest.approx(expected, abs=5)

    def test_20mm_m20_fe500(self):
        """20mm bar, M20, Fe500."""
        ld = calculate_development_length(20, 20, 500)
        expected = (20 * 0.87 * 500) / (4 * 1.92)
        assert ld == pytest.approx(expected, abs=5)

    def test_12mm_m30_fe415(self):
        """12mm bar, M30, Fe415."""
        ld = calculate_development_length(12, 30, 415)
        expected = (12 * 0.87 * 415) / (4 * 2.40)
        assert ld == pytest.approx(expected, abs=5)


class TestLapLength:
    """Tests for lap splice length calculation."""

    def test_tension_lap_50_percent(self):
        """Tension lap with ≤50% bars spliced: α = 1.0"""
        ld = calculate_development_length(16, 25, 500)
        lap = calculate_lap_length(16, 25, 500, splice_percent=50)
        assert lap == pytest.approx(ld, abs=5)

    def test_tension_lap_more_than_50_percent(self):
        """Tension lap with >50% bars spliced: α = 1.3"""
        ld = calculate_development_length(16, 25, 500)
        lap = calculate_lap_length(16, 25, 500, splice_percent=75)
        assert lap == pytest.approx(1.3 * ld, abs=5)

    def test_seismic_lap(self):
        """Seismic lap: α = 1.5"""
        ld = calculate_development_length(16, 25, 500)
        lap = calculate_lap_length(16, 25, 500, is_seismic=True)
        assert lap == pytest.approx(1.5 * ld, abs=5)

    def test_compression_lap(self):
        """Compression lap = Ld (no enhancement)."""
        ld = calculate_development_length(16, 25, 500)
        lap = calculate_lap_length(16, 25, 500, in_tension=False)
        assert lap == pytest.approx(ld, abs=5)


class TestBarSpacing:
    """Tests for bar spacing calculations."""

    def test_basic_spacing(self):
        """3 bars of 16mm in 230mm beam."""
        # Available = 230 - 2*(25+8) - 16 = 230 - 66 - 16 = 148
        # Spacing = 148 / 2 = 74 mm
        spacing = calculate_bar_spacing(230, 25, 8, 16, 3)
        assert spacing == pytest.approx(74, abs=2)

    def test_single_bar(self):
        """Single bar has no spacing."""
        spacing = calculate_bar_spacing(230, 25, 8, 16, 1)
        assert spacing == 0

    def test_min_spacing_ok(self):
        """Spacing > min is valid."""
        is_valid, _ = check_min_spacing(60, 16)
        assert is_valid is True

    def test_min_spacing_fail(self):
        """Spacing < min is invalid."""
        is_valid, msg = check_min_spacing(20, 25)
        assert is_valid is False
        assert "FAIL" in msg


class TestBarArrangement:
    """Tests for bar arrangement selection."""

    def test_small_area_uses_12mm(self):
        """Small area should use 12mm bars."""
        arr = select_bar_arrangement(300, 230, 25)
        assert arr.diameter == 12
        assert arr.count >= 2

    def test_medium_area_uses_16mm(self):
        """Medium area should use 16mm bars."""
        arr = select_bar_arrangement(800, 230, 25)
        assert arr.diameter == 16

    def test_large_area_uses_20mm(self):
        """Large area should use 20mm bars."""
        arr = select_bar_arrangement(1500, 300, 30)
        assert arr.diameter == 20

    def test_min_two_bars(self):
        """Should always provide at least 2 bars."""
        arr = select_bar_arrangement(100, 230, 25)
        assert arr.count >= 2

    def test_area_provided_sufficient(self):
        """Provided area should meet or exceed required."""
        arr = select_bar_arrangement(1000, 300, 30)
        assert arr.area_provided >= 1000

    def test_spacing_rechecked_after_layering_or_dia_change(self):
        """If one-layer spacing fails, selection should re-check and improve."""
        arr = select_bar_arrangement(
            ast_required=2000,
            b=150,
            cover=25,
            stirrup_dia=8,
            preferred_dia=12,
            max_layers=2,
        )
        assert arr.layers == 2
        is_valid, _ = check_min_spacing(arr.spacing, arr.diameter)
        assert is_valid is True

    def test_callout_format(self):
        """Callout should be in standard format."""
        arr = BarArrangement(3, 16, 603, 60, 1)
        assert arr.callout() == "3-16φ"


class TestStirrupLegs:
    """Tests for stirrup leg determination."""

    def test_narrow_beam(self):
        """Narrow beam (≤300) uses 2 legs."""
        assert get_stirrup_legs(230) == 2

    def test_medium_beam(self):
        """Medium beam (300-450) uses 2 legs."""
        assert get_stirrup_legs(400) == 2

    def test_wide_beam(self):
        """Wide beam (>450) uses 4 legs."""
        assert get_stirrup_legs(500) == 4

    def test_very_wide_beam(self):
        """Very wide beam (>600) uses 6 legs."""
        assert get_stirrup_legs(700) == 6


class TestFormatHelpers:
    """Tests for formatting functions."""

    def test_bar_callout(self):
        assert format_bar_callout(3, 16) == "3-16φ"
        assert format_bar_callout(4, 20) == "4-20φ"

    def test_stirrup_callout(self):
        assert format_stirrup_callout(2, 8, 150) == "2L-8φ@150 c/c"
        assert format_stirrup_callout(4, 10, 200) == "4L-10φ@200 c/c"


class TestBeamDetailingResult:
    """Tests for complete beam detailing."""

    def test_basic_detailing(self):
        """Create detailing for a typical beam."""
        result = create_beam_detailing(
            beam_id="B1",
            story="S1",
            b=230,
            D=450,
            span=4000,
            cover=25,
            fck=25,
            fy=500,
            ast_start=800,
            ast_mid=1200,
            ast_end=800,
        )

        assert result.is_valid is True
        assert result.beam_id == "B1"
        assert result.ld_tension > 0
        assert result.lap_length >= result.ld_tension
        assert len(result.top_bars) == 3
        assert len(result.bottom_bars) == 3
        assert len(result.stirrups) == 3
        assert "0.25" in result.remarks

    def test_seismic_lap_longer(self):
        """Seismic detailing should have longer lap."""
        non_seismic = create_beam_detailing(
            beam_id="B1",
            story="S1",
            b=230,
            D=450,
            span=4000,
            cover=25,
            fck=25,
            fy=500,
            ast_start=800,
            ast_mid=1200,
            ast_end=800,
            is_seismic=False,
        )

        seismic = create_beam_detailing(
            beam_id="B1",
            story="S1",
            b=230,
            D=450,
            span=4000,
            cover=25,
            fck=25,
            fy=500,
            ast_start=800,
            ast_mid=1200,
            ast_end=800,
            is_seismic=True,
        )

        assert seismic.lap_length > non_seismic.lap_length

    def test_stirrup_zones(self):
        """Stirrups should have different zones."""
        result = create_beam_detailing(
            beam_id="B1",
            story="S1",
            b=230,
            D=450,
            span=4000,
            cover=25,
            fck=25,
            fy=500,
            ast_start=800,
            ast_mid=1200,
            ast_end=800,
            stirrup_spacing_start=150,
            stirrup_spacing_mid=200,
            stirrup_spacing_end=150,
        )

        assert result.stirrups[0].spacing == 150  # Start
        assert result.stirrups[1].spacing == 200  # Mid
        assert result.stirrups[2].spacing == 150  # End
