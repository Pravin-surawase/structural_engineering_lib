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

from structural_lib.core.errors import ConfigurationError
from structural_lib.detailing import (
    BarArrangement,
    calculate_bar_spacing,
    calculate_development_length,
    calculate_lap_length,
    check_min_spacing,
    check_side_face_reinforcement,
    create_beam_detailing,
    format_bar_callout,
    format_stirrup_callout,
    get_bond_stress,
    get_stirrup_legs,
    select_bar_arrangement,
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
        """Single bar should raise ConfigurationError (can't calculate spacing)."""
        with pytest.raises(ConfigurationError, match="Bar count must be > 1"):
            calculate_bar_spacing(230, 25, 8, 16, 1)

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


class TestSideFaceReinforcement:
    """Tests for side-face reinforcement check (IS 456 Cl 26.5.1.3)."""

    def test_not_required_for_small_depth(self):
        """Side-face reinforcement not required when D ≤ 750 mm."""
        is_required, area, spacing = check_side_face_reinforcement(
            D=500, b=230, cover=25
        )
        assert is_required is False
        assert area == 0.0
        assert spacing == 0.0

    def test_not_required_at_threshold(self):
        """Side-face reinforcement not required exactly at D = 750 mm."""
        is_required, area, spacing = check_side_face_reinforcement(
            D=750, b=230, cover=25
        )
        assert is_required is False
        assert area == 0.0
        assert spacing == 0.0

    def test_required_above_threshold(self):
        """Side-face reinforcement required when D > 750 mm."""
        is_required, area, spacing = check_side_face_reinforcement(
            D=800, b=300, cover=40
        )
        assert is_required is True
        assert area > 0
        assert spacing == 300.0

    def test_area_calculation_800mm_depth(self):
        """
        Test area calculation for D=800mm, b=300mm, cover=40mm.

        Web height = 800 - 2*40 = 720 mm
        Web area per face = 300 * 720 = 216,000 mm²
        Required area = 0.1% = 0.001 * 216,000 = 216 mm²
        """
        is_required, area, spacing = check_side_face_reinforcement(
            D=800, b=300, cover=40
        )

        # Expected calculation
        web_height = 800 - 2 * 40  # 720 mm
        web_area = 300 * web_height  # 216,000 mm²
        expected_area = 0.001 * web_area  # 216 mm²

        assert is_required is True
        assert area == pytest.approx(expected_area, abs=0.5)
        assert spacing == 300.0

    def test_area_calculation_1000mm_depth(self):
        """
        Test area calculation for D=1000mm, b=400mm, cover=50mm.

        Web height = 1000 - 2*50 = 900 mm
        Web area per face = 400 * 900 = 360,000 mm²
        Required area = 0.1% = 0.001 * 360,000 = 360 mm²
        """
        is_required, area, spacing = check_side_face_reinforcement(
            D=1000, b=400, cover=50
        )

        web_height = 1000 - 2 * 50  # 900 mm
        web_area = 400 * web_height  # 360,000 mm²
        expected_area = 0.001 * web_area  # 360 mm²

        assert is_required is True
        assert area == pytest.approx(expected_area, abs=0.5)
        assert spacing == 300.0

    def test_typical_beam_750mm_boundary(self):
        """Test at exact 750mm boundary (not required)."""
        is_required, area, spacing = check_side_face_reinforcement(
            D=750, b=300, cover=30
        )
        assert is_required is False

    def test_typical_beam_751mm_just_above(self):
        """Test just above 750mm threshold (required)."""
        is_required, area, spacing = check_side_face_reinforcement(
            D=751, b=300, cover=30
        )

        web_height = 751 - 2 * 30  # 691 mm
        web_area = 300 * web_height  # 207,300 mm²
        expected_area = 0.001 * web_area  # 207.3 mm²

        assert is_required is True
        assert area == pytest.approx(expected_area, abs=0.5)
        assert spacing == 300.0

    def test_large_depth_beam(self):
        """Test for a deep transfer beam (D=1500mm)."""
        is_required, area, spacing = check_side_face_reinforcement(
            D=1500, b=600, cover=50
        )

        web_height = 1500 - 2 * 50  # 1400 mm
        web_area = 600 * web_height  # 840,000 mm²
        expected_area = 0.001 * web_area  # 840 mm²

        assert is_required is True
        assert area == pytest.approx(expected_area, abs=0.5)
        assert spacing == 300.0

    def test_spacing_always_300mm_when_required(self):
        """Maximum spacing is always 300mm per IS 456 Cl 26.5.1.3."""
        _, _, spacing1 = check_side_face_reinforcement(D=800, b=300, cover=40)
        _, _, spacing2 = check_side_face_reinforcement(D=1200, b=400, cover=50)
        _, _, spacing3 = check_side_face_reinforcement(D=2000, b=600, cover=60)

        assert spacing1 == 300.0
        assert spacing2 == 300.0
        assert spacing3 == 300.0


# =============================================================================
# Tests for Anchorage Functions (IS 456 Cl 26.2.2)
# =============================================================================


class TestMinBendRadius:
    """Tests for minimum bend radius per IS 456 Cl 26.2.2.1."""

    def test_small_deformed_bar(self):
        """Bars ≤ 25mm: 2φ internal radius."""
        from structural_lib.detailing import get_min_bend_radius

        assert get_min_bend_radius(16, "deformed") == 32  # 2 × 16
        assert get_min_bend_radius(20, "deformed") == 40  # 2 × 20
        assert get_min_bend_radius(25, "deformed") == 50  # 2 × 25

    def test_large_deformed_bar(self):
        """Bars > 25mm: 3φ internal radius."""
        from structural_lib.detailing import get_min_bend_radius

        assert get_min_bend_radius(32, "deformed") == 96  # 3 × 32

    def test_plain_bar(self):
        """Plain bars always use 2φ radius."""
        from structural_lib.detailing import get_min_bend_radius

        assert get_min_bend_radius(32, "plain") == 64  # 2 × 32

    def test_invalid_diameter(self):
        """Should raise MaterialError for invalid diameter."""
        from structural_lib.core.errors import MaterialError
        from structural_lib.detailing import get_min_bend_radius

        with pytest.raises(MaterialError):
            get_min_bend_radius(0)
        with pytest.raises(MaterialError):
            get_min_bend_radius(-10)


class TestStandardHook:
    """Tests for standard hook dimensions per IS 456 Cl 26.2.2."""

    def test_180_hook_deformed_16mm(self):
        """180° hook for 16mm deformed bar."""
        from structural_lib.detailing import calculate_standard_hook

        hook = calculate_standard_hook(16, "180", "deformed")
        assert hook.hook_type == "180"
        assert hook.bar_dia == 16
        assert hook.internal_radius == 32  # 2 × 16
        assert hook.extension == 65  # max(4×16=64, 65) = 65
        assert hook.equivalent_length == 128  # 8 × 16

    def test_90_hook_extension(self):
        """90° hook has 12φ extension."""
        from structural_lib.detailing import calculate_standard_hook

        hook = calculate_standard_hook(20, "90", "deformed")
        assert hook.hook_type == "90"
        assert hook.extension == 240  # 12 × 20

    def test_135_hook_seismic(self):
        """135° hook with 6φ extension (seismic)."""
        from structural_lib.detailing import calculate_standard_hook

        hook = calculate_standard_hook(12, "135", "deformed")
        assert hook.hook_type == "135"
        assert hook.extension == 72  # 6 × 12

    def test_plain_bar_equivalent_length(self):
        """Plain bar hooks have 16φ equivalent length."""
        from structural_lib.detailing import calculate_standard_hook

        hook = calculate_standard_hook(16, "180", "plain")
        assert hook.equivalent_length == 256  # 16 × 16

    def test_invalid_hook_type(self):
        """Should raise ValueError for invalid hook type."""
        from structural_lib.detailing import calculate_standard_hook

        with pytest.raises(ValueError, match="Invalid hook_type"):
            calculate_standard_hook(16, "45")

    def test_invalid_bar_diameter(self):
        """Should raise MaterialError for invalid diameter."""
        from structural_lib.core.errors import MaterialError
        from structural_lib.detailing import calculate_standard_hook

        with pytest.raises(MaterialError):
            calculate_standard_hook(0, "180")


class TestAnchorageLength:
    """Tests for anchorage length calculation per IS 456 Cl 26.2.3."""

    def test_adequate_straight_length(self):
        """When straight length >= Ld, no hook needed."""
        from structural_lib.detailing import calculate_anchorage_length

        result = calculate_anchorage_length(
            bar_dia=16,
            fck=25,
            fy=500,
            available_length=800,  # More than required
            use_hook=False,
        )
        assert result["is_adequate"] is True
        assert result["hook"] is None

    def test_shortfall_with_hook(self):
        """When straight length < Ld, hook makes up difference."""
        from structural_lib.detailing import calculate_anchorage_length

        result = calculate_anchorage_length(
            bar_dia=16,
            fck=25,
            fy=500,
            available_length=400,  # Less than required
            use_hook=True,
            hook_type="180",
        )
        assert result["shortfall"] > 0
        assert result["hook"] is not None
        assert result["total_provided"] == 400 + 128  # 400 + 8×16

    def test_utilization_ratio(self):
        """Utilization ratio should be total/required."""
        from structural_lib.detailing import calculate_anchorage_length

        result = calculate_anchorage_length(
            bar_dia=16,
            fck=25,
            fy=500,
            available_length=600,
            use_hook=True,
        )
        expected_util = result["total_provided"] / result["required_ld"]
        assert result["utilization"] == pytest.approx(expected_util, rel=0.01)


class TestStirrupAnchorage:
    """Tests for stirrup anchorage hooks per IS 456 Cl 26.2.2.2."""

    def test_regular_stirrup(self):
        """Regular stirrup: 90° hook, 8d extension."""
        from structural_lib.detailing import calculate_stirrup_anchorage

        result = calculate_stirrup_anchorage(8, is_seismic=False)
        assert result["hook_type"] == "90"
        assert result["internal_radius"] == 16  # 2 × 8
        assert result["extension"] == 75  # max(8×8=64, 75) = 75

    def test_seismic_stirrup(self):
        """Seismic stirrup: 135° hook, 6d ≥ 75mm."""
        from structural_lib.detailing import calculate_stirrup_anchorage

        result = calculate_stirrup_anchorage(10, is_seismic=True)
        assert result["hook_type"] == "135"
        assert result["extension"] == 75  # max(6×10=60, 75) = 75
        assert "IS 13920" in result["remarks"]

    def test_invalid_diameter(self):
        """Should raise MaterialError for invalid diameter."""
        from structural_lib.core.errors import MaterialError
        from structural_lib.detailing import calculate_stirrup_anchorage

        with pytest.raises(MaterialError):
            calculate_stirrup_anchorage(0)
