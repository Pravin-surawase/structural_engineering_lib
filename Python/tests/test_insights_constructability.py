from structural_lib.api import design_beam_is456
from structural_lib.detailing import (
    BarArrangement,
    BeamDetailingResult,
    StirrupArrangement,
)
from structural_lib.insights import calculate_constructability_score


def _design_result():
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


def test_constructability_spacing_penalty():
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
