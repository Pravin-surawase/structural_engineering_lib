"""Constructability scoring (advisory only)."""

from __future__ import annotations

from typing import List

from ..detailing import BeamDetailingResult
from ..types import ComplianceCaseResult
from .types import ConstructabilityFactor, ConstructabilityScore


def calculate_constructability_score(
    design_result: ComplianceCaseResult,
    detailing: BeamDetailingResult,
) -> ConstructabilityScore:
    """Assess construction ease on 0-10 scale (heuristic)."""

    score = 10.0
    factors: List[ConstructabilityFactor] = []

    bars = detailing.top_bars + detailing.bottom_bars
    bar_sizes = [bar.diameter for bar in bars if bar.count > 0]
    stirrup_sizes = [stirrup.diameter for stirrup in detailing.stirrups]

    min_clear_spacing = None
    max_layers = 1
    if bars:
        clear_spacings = [bar.spacing - bar.diameter for bar in bars if bar.spacing > 0]
        if clear_spacings:
            min_clear_spacing = min(clear_spacings)
        max_layers = max(bar.layers for bar in bars)

    min_stirrup_spacing = None
    if detailing.stirrups:
        min_stirrup_spacing = min(s.spacing for s in detailing.stirrups)

    # Factor 1: Bar clear spacing
    if min_clear_spacing is not None and min_clear_spacing < 40:
        penalty = 2.0
        factors.append(
            ConstructabilityFactor(
                factor="bar_spacing",
                score=0,
                penalty=-penalty,
                message=f"Clear spacing {min_clear_spacing:.0f}mm < 40mm (congested)",
                recommendation="Increase width or reduce bar diameter.",
            )
        )
        score -= penalty
    elif min_clear_spacing is not None and min_clear_spacing < 60:
        penalty = 1.0
        factors.append(
            ConstructabilityFactor(
                factor="bar_spacing",
                score=0,
                penalty=-penalty,
                message=f"Clear spacing {min_clear_spacing:.0f}mm is tight",
                recommendation="Consider spacing >= 60mm for easier placement.",
            )
        )
        score -= penalty

    # Factor 2: Stirrup spacing
    if min_stirrup_spacing is not None and min_stirrup_spacing < 100:
        penalty = 2.0
        factors.append(
            ConstructabilityFactor(
                factor="stirrup_spacing",
                score=0,
                penalty=-penalty,
                message=(
                    f"Stirrup spacing {min_stirrup_spacing:.0f}mm < 100mm "
                    "(very tight)"
                ),
                recommendation="Increase stirrup diameter or review shear demand.",
            )
        )
        score -= penalty
    elif min_stirrup_spacing is not None and min_stirrup_spacing < 125:
        penalty = 1.5
        factors.append(
            ConstructabilityFactor(
                factor="stirrup_spacing",
                score=0,
                penalty=-penalty,
                message=(
                    f"Stirrup spacing {min_stirrup_spacing:.0f}mm < 125mm " "(tight)"
                ),
                recommendation="Spacing >= 125mm improves concrete vibration.",
            )
        )
        score -= penalty

    # Factor 3: Bar variety
    unique_sizes = len(set(bar_sizes + stirrup_sizes))
    if unique_sizes > 2:
        penalty = 1.0
        factors.append(
            ConstructabilityFactor(
                factor="bar_variety",
                score=0,
                penalty=-penalty,
                message=f"{unique_sizes} bar sizes used (procurement complexity)",
                recommendation="Limit to 2 bar sizes where possible.",
            )
        )
        score -= penalty

    # Factor 4: Standard sizes bonus
    standard_sizes = {12, 16, 20, 25}
    if bar_sizes and all(size in standard_sizes for size in bar_sizes):
        bonus = 1.0
        factors.append(
            ConstructabilityFactor(
                factor="standard_sizes",
                score=1.0,
                penalty=0,
                message="All main bars are standard sizes.",
                recommendation="",
            )
        )
        score += bonus

    # Factor 5: Layer count
    if max_layers > 2:
        penalty = 1.0
        factors.append(
            ConstructabilityFactor(
                factor="layers",
                score=0,
                penalty=-penalty,
                message=f"{max_layers} layers used (congestion risk)",
                recommendation="Reduce bar count or increase width to keep <=2 layers.",
            )
        )
        score -= penalty

    score = max(0.0, min(10.0, score))

    if score >= 8.0:
        rating = "excellent"
    elif score >= 6.0:
        rating = "good"
    elif score >= 4.0:
        rating = "acceptable"
    else:
        rating = "poor"

    overall_message = f"Constructability: {score:.1f}/10 ({rating})"

    return ConstructabilityScore(
        score=score,
        rating=rating,
        factors=factors,
        overall_message=overall_message,
        version="1.0",
    )
