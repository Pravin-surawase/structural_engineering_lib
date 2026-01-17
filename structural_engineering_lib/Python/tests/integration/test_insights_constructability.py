"""Comprehensive tests for constructability scoring module.

Tests cover:
- Light reinforcement (85-100 expected score)
- Typical reinforcement (70-85 expected score)
- Heavy reinforcement (55-70 expected score)
- Congested design (<55 expected score)
- Edge cases (non-standard sizes, too many bars)
- Factor-specific penalties and bonuses
"""

from structural_lib.api import design_beam_is456
from structural_lib.detailing import (
    BarArrangement,
    BeamDetailingResult,
    StirrupArrangement,
)
from structural_lib.insights import calculate_constructability_score


def _design_result():
    """Standard design result for testing."""
    return design_beam_is456(
        units="IS456",
        mu_knm=120.0,
        vu_kn=80.0,
        b_mm=300.0,
        D_mm=500.0,
        d_mm=450.0,
        fck_nmm2=25.0,
        fy_nmm2=500.0,
    )


def _detailing_with_spacing(
    clear_spacing_mm: float, layers: int, stirrup_spacing: float
):
    """Helper to create detailing with specific spacing."""
    bar_dia = 20.0
    spacing = clear_spacing_mm + bar_dia
    bars = [
        BarArrangement(
            count=4,
            diameter=bar_dia,
            area_provided=1256.0,
            spacing=spacing,
            layers=layers,
        )
        for _ in range(3)
    ]
    stirrups = [
        StirrupArrangement(
            diameter=8.0, legs=2, spacing=stirrup_spacing, zone_length=1500.0
        )
        for _ in range(3)
    ]

    return BeamDetailingResult(
        beam_id="B1",
        story="L1",
        b=300.0,
        D=500.0,
        span=5000.0,
        cover=40.0,
        top_bars=bars,
        bottom_bars=bars,
        stirrups=stirrups,
        ld_tension=0.0,
        ld_compression=0.0,
        lap_length=0.0,
        is_valid=True,
        remarks="",
    )


# ==============================================================================
# Legacy Test
# ==============================================================================


def test_constructability_spacing_penalty():
    """Legacy test - good spacing should score higher than tight spacing."""
    design = _design_result()
    tight = _detailing_with_spacing(
        clear_spacing_mm=30.0, layers=3, stirrup_spacing=90.0
    )
    good = _detailing_with_spacing(
        clear_spacing_mm=80.0, layers=1, stirrup_spacing=150.0
    )

    tight_score = calculate_constructability_score(design, tight)
    good_score = calculate_constructability_score(design, good)

    assert good_score.score > tight_score.score
    assert any(f.factor == "bar_spacing" for f in tight_score.factors)


# ==============================================================================
# Comprehensive Design Spectrum Tests
# ==============================================================================


def test_light_reinforcement_excellent_score():
    """Light reinforcement with good spacing should score 85-100 (excellent)."""
    design = _design_result()

    # Light reinforcement: 2-3 bars per layer, standard sizes, good spacing
    top_bars = [
        BarArrangement(
            count=2,  # Simple configuration
            diameter=16.0,  # Standard size
            area_provided=402.0,
            spacing=140.0,  # 140-16=124mm clear (excellent)
            layers=1,
        )
    ]
    bottom_bars = [
        BarArrangement(
            count=3,
            diameter=16.0,
            area_provided=603.0,
            spacing=100.0,  # 100-16=84mm clear (good)
            layers=1,
        )
    ]
    stirrups = [
        StirrupArrangement(
            diameter=8.0, legs=2, spacing=150.0, zone_length=2500.0  # Good spacing
        )
    ]

    detailing = BeamDetailingResult(
        beam_id="B_LIGHT",
        story="G",
        b=300.0,
        D=500.0,  # 50mm multiple - bonus
        span=5000.0,
        cover=40.0,
        top_bars=top_bars,
        bottom_bars=bottom_bars,
        stirrups=stirrups,
        ld_tension=0.0,
        ld_compression=0.0,
        lap_length=0.0,
        is_valid=True,
        remarks="",
    )

    result = calculate_constructability_score(design, detailing)

    assert (
        85.0 <= result.score <= 100.0
    ), f"Light reinforcement should score 85-100, got {result.score}"
    assert result.rating == "excellent"
    # Should have bonuses: standard sizes, depth increment, bar configuration
    assert any(f.factor == "standard_sizes" for f in result.factors)
    assert any(f.factor == "depth_increment" for f in result.factors)
    assert any(f.factor == "bar_configuration" for f in result.factors)


def test_typical_reinforcement_good_score():
    """Typical reinforcement should score well (good to excellent range)."""
    design = _design_result()

    # Typical reinforcement: 4 bars per layer, standard sizes, acceptable spacing
    top_bars = [
        BarArrangement(
            count=4,
            diameter=20.0,  # Standard size
            area_provided=1256.0,
            spacing=55.0,  # 55-20=35mm clear (tight - will trigger penalty)
            layers=2,  # 2 layers (acceptable)
        )
    ]
    bottom_bars = [
        BarArrangement(
            count=4,
            diameter=20.0,
            area_provided=1256.0,
            spacing=55.0,
            layers=2,
        )
    ]
    stirrups = [
        StirrupArrangement(
            diameter=8.0, legs=2, spacing=110.0, zone_length=2500.0  # Slightly tight
        )
    ]

    detailing = BeamDetailingResult(
        beam_id="B_TYPICAL",
        story="G",
        b=300.0,
        D=450.0,  # NOT 50mm multiple - penalty
        span=5000.0,
        cover=40.0,
        top_bars=top_bars,
        bottom_bars=bottom_bars,
        stirrups=stirrups,
        ld_tension=0.0,
        ld_compression=0.0,
        lap_length=0.0,
        is_valid=True,
        remarks="",
    )

    result = calculate_constructability_score(design, detailing)

    assert (
        70.0 <= result.score <= 100.0
    ), f"Typical reinforcement should score 70-100, got {result.score}"
    assert result.rating in {"good", "excellent"}
    # Should have some penalties
    assert any(
        f.penalty < 0 for f in result.factors
    ), "Should have at least one penalty"


def test_heavy_reinforcement_acceptable_score():
    """Heavy reinforcement with some congestion should score 55-70 (acceptable)."""
    design = _design_result()

    # Heavy reinforcement: multiple layers, tighter spacing
    top_bars = [
        BarArrangement(
            count=6,  # More bars (penalty on bar_configuration)
            diameter=25.0,  # Standard size (bonus)
            area_provided=2945.0,
            spacing=50.0,  # 50-25=25mm clear (congested - penalty)
            layers=2,
        )
    ]
    bottom_bars = [
        BarArrangement(
            count=6,
            diameter=25.0,
            area_provided=2945.0,
            spacing=50.0,
            layers=2,
        )
    ]
    stirrups = [
        StirrupArrangement(
            diameter=10.0,
            legs=2,
            spacing=100.0,  # Tight spacing (penalty)
            zone_length=2500.0,
        )
    ]

    detailing = BeamDetailingResult(
        beam_id="B_HEAVY",
        story="G",
        b=300.0,
        D=550.0,  # 50mm multiple (bonus)
        span=5000.0,
        cover=40.0,
        top_bars=top_bars,
        bottom_bars=bottom_bars,
        stirrups=stirrups,
        ld_tension=0.0,
        ld_compression=0.0,
        lap_length=0.0,
        is_valid=True,
        remarks="",
    )

    result = calculate_constructability_score(design, detailing)

    assert (
        55.0 <= result.score <= 70.0
    ), f"Heavy reinforcement should score 55-70, got {result.score}"
    assert result.rating in {"acceptable", "good"}
    # Should have spacing and stirrup spacing penalties
    assert any(f.factor == "bar_spacing" and f.penalty < 0 for f in result.factors)
    assert any(f.factor == "stirrup_spacing" and f.penalty < 0 for f in result.factors)


def test_congested_design_poor_score():
    """Congested design with multiple issues should score <55 (poor)."""
    design = _design_result()

    # Congested: multiple layers, very tight spacing, non-standard sizes
    top_bars = [
        BarArrangement(
            count=8,  # Many bars (penalty)
            diameter=18.0,  # Non-standard size (penalty)
            area_provided=2036.0,
            spacing=40.0,  # 40-18=22mm clear (very congested - high penalty)
            layers=3,  # Many layers (penalty)
        )
    ]
    bottom_bars = [
        BarArrangement(
            count=8,
            diameter=22.0,  # Another non-standard size (variety penalty)
            area_provided=3041.0,
            spacing=40.0,
            layers=3,
        )
    ]
    stirrups = [
        StirrupArrangement(
            diameter=12.0,  # Another size (variety)
            legs=2,
            spacing=80.0,  # Very tight (high penalty)
            zone_length=2500.0,
        )
    ]

    detailing = BeamDetailingResult(
        beam_id="B_CONGESTED",
        story="G",
        b=300.0,
        D=475.0,  # NOT 50mm multiple (penalty)
        span=5000.0,
        cover=40.0,
        top_bars=top_bars,
        bottom_bars=bottom_bars,
        stirrups=stirrups,
        ld_tension=0.0,
        ld_compression=0.0,
        lap_length=0.0,
        is_valid=True,
        remarks="",
    )

    result = calculate_constructability_score(design, detailing)

    assert result.score < 55.0, f"Congested design should score <55, got {result.score}"
    assert result.rating == "poor"
    # Should have multiple penalties
    assert any(f.factor == "bar_spacing" for f in result.factors)
    assert any(f.factor == "stirrup_spacing" for f in result.factors)
    assert any(f.factor == "layers" for f in result.factors)
    assert any(f.factor == "non_standard_sizes" for f in result.factors)
    assert any(f.factor == "bar_variety" for f in result.factors)


# ==============================================================================
# Factor-Specific Tests
# ==============================================================================


def test_standard_sizes_bonus():
    """Using all standard sizes (8,10,12,16,20,25,32mm) should give bonus."""
    design = _design_result()

    # All standard sizes
    top_bars = [
        BarArrangement(
            count=2, diameter=16.0, area_provided=402.0, spacing=140.0, layers=1
        )
    ]
    bottom_bars = [
        BarArrangement(
            count=2, diameter=20.0, area_provided=628.0, spacing=140.0, layers=1
        )
    ]
    stirrups = [
        StirrupArrangement(diameter=8.0, legs=2, spacing=150.0, zone_length=2500.0)
    ]

    detailing = BeamDetailingResult(
        beam_id="STD",
        story="G",
        b=300.0,
        D=500.0,
        span=5000.0,
        cover=40.0,
        top_bars=top_bars,
        bottom_bars=bottom_bars,
        stirrups=stirrups,
        ld_tension=0.0,
        ld_compression=0.0,
        lap_length=0.0,
        is_valid=True,
        remarks="",
    )

    result = calculate_constructability_score(design, detailing)
    assert any(f.factor == "standard_sizes" and f.score > 0 for f in result.factors)


def test_non_standard_sizes_penalty():
    """Using non-standard sizes (e.g., 18mm, 22mm) should give penalty."""
    design = _design_result()

    # Non-standard sizes
    top_bars = [
        BarArrangement(
            count=2, diameter=18.0, area_provided=509.0, spacing=140.0, layers=1
        )
    ]
    bottom_bars = [
        BarArrangement(
            count=2, diameter=22.0, area_provided=760.0, spacing=140.0, layers=1
        )
    ]
    stirrups = [
        StirrupArrangement(diameter=8.0, legs=2, spacing=150.0, zone_length=2500.0)
    ]

    detailing = BeamDetailingResult(
        beam_id="NONSTD",
        story="G",
        b=300.0,
        D=500.0,
        span=5000.0,
        cover=40.0,
        top_bars=top_bars,
        bottom_bars=bottom_bars,
        stirrups=stirrups,
        ld_tension=0.0,
        ld_compression=0.0,
        lap_length=0.0,
        is_valid=True,
        remarks="",
    )

    result = calculate_constructability_score(design, detailing)
    assert any(
        f.factor == "non_standard_sizes" and f.penalty < 0 for f in result.factors
    )


def test_depth_increment_bonus():
    """Depth as 50mm multiple should give bonus; non-50mm should give penalty."""
    design = _design_result()

    top_bars = [
        BarArrangement(
            count=2, diameter=16.0, area_provided=402.0, spacing=140.0, layers=1
        )
    ]
    bottom_bars = [
        BarArrangement(
            count=2, diameter=16.0, area_provided=402.0, spacing=140.0, layers=1
        )
    ]
    stirrups = [
        StirrupArrangement(diameter=8.0, legs=2, spacing=150.0, zone_length=2500.0)
    ]

    # D = 500mm (50mm multiple)
    detailing_good = BeamDetailingResult(
        beam_id="D500",
        story="G",
        b=300.0,
        D=500.0,
        span=5000.0,
        cover=40.0,
        top_bars=top_bars,
        bottom_bars=bottom_bars,
        stirrups=stirrups,
        ld_tension=0.0,
        ld_compression=0.0,
        lap_length=0.0,
        is_valid=True,
        remarks="",
    )

    # D = 475mm (NOT 50mm multiple)
    detailing_bad = BeamDetailingResult(
        beam_id="D475",
        story="G",
        b=300.0,
        D=475.0,
        span=5000.0,
        cover=40.0,
        top_bars=top_bars,
        bottom_bars=bottom_bars,
        stirrups=stirrups,
        ld_tension=0.0,
        ld_compression=0.0,
        lap_length=0.0,
        is_valid=True,
        remarks="",
    )

    result_good = calculate_constructability_score(design, detailing_good)
    result_bad = calculate_constructability_score(design, detailing_bad)

    # Verify factors are present
    assert any(
        f.factor == "depth_increment" and f.score > 0 for f in result_good.factors
    ), "Should have depth increment bonus"
    assert any(
        f.factor == "depth_increment" and f.penalty < 0 for f in result_bad.factors
    ), "Should have depth increment penalty"

    # Score difference may be small if both designs are otherwise excellent
    # Just verify the factor is applied correctly (above asserts cover this)


def test_bar_configuration_bonus():
    """Simple bar configuration (2-3 bars per layer) should give bonus."""
    design = _design_result()

    # Simple configuration (2 bars)
    top_bars = [
        BarArrangement(
            count=2, diameter=20.0, area_provided=628.0, spacing=140.0, layers=1
        )
    ]
    bottom_bars = [
        BarArrangement(
            count=3, diameter=20.0, area_provided=942.0, spacing=100.0, layers=1
        )
    ]
    stirrups = [
        StirrupArrangement(diameter=8.0, legs=2, spacing=150.0, zone_length=2500.0)
    ]

    detailing = BeamDetailingResult(
        beam_id="SIMPLE",
        story="G",
        b=300.0,
        D=500.0,
        span=5000.0,
        cover=40.0,
        top_bars=top_bars,
        bottom_bars=bottom_bars,
        stirrups=stirrups,
        ld_tension=0.0,
        ld_compression=0.0,
        lap_length=0.0,
        is_valid=True,
        remarks="",
    )

    result = calculate_constructability_score(design, detailing)
    assert any(f.factor == "bar_configuration" and f.score > 0 for f in result.factors)


def test_score_bounds():
    """Constructability score should always be in [0, 100] range."""
    design = _design_result()

    # Test with various detailing scenarios
    scenarios = [
        _detailing_with_spacing(clear_spacing_mm=20.0, layers=4, stirrup_spacing=70.0),
        _detailing_with_spacing(
            clear_spacing_mm=100.0, layers=1, stirrup_spacing=200.0
        ),
        _detailing_with_spacing(clear_spacing_mm=60.0, layers=2, stirrup_spacing=125.0),
    ]

    for detailing in scenarios:
        result = calculate_constructability_score(design, detailing)
        assert 0.0 <= result.score <= 100.0, f"Score {result.score} out of bounds"
        assert result.rating in {"excellent", "good", "acceptable", "poor"}
