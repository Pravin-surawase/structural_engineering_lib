# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Constructability scoring (advisory only).

Based on Singapore Building Designers Appraisal Scheme (BDAS) framework
for assessing ease of construction (Poh & Chen, 1998).

Scoring factors:
- Bar spacing (clear spacing >= 60mm ideal)
- Stirrup spacing (>=125mm ideal for concrete vibration)
- Bar variety (minimize number of different sizes)
- Standard sizes (8,10,12,16,20,25,32mm)
- Layer count (<=2 layers ideal)
- Depth increments (50mm multiples for formwork reuse)
- Bar configuration simplicity (2-3 bars per layer)
"""

from __future__ import annotations

from ..detailing import BeamDetailingResult
from ..types import ComplianceCaseResult
from .data_types import ConstructabilityFactor, ConstructabilityScore


def calculate_constructability_score(
    design_result: ComplianceCaseResult,
    detailing: BeamDetailingResult,
) -> ConstructabilityScore:
    """Assess construction ease on 0-100 scale (heuristic-based).

    Higher scores indicate easier construction (lower labor cost, better quality).

    Args:
        design_result: Design result with utilization and compliance data
        detailing: Detailing result with bar layouts and stirrup configuration

    Returns:
        ConstructabilityScore with overall score (0-100) and factor breakdown

    Score interpretation:
        85-100: Excellent (easy construction, low labor cost)
        70-84:  Good (typical construction complexity)
        55-69:  Acceptable (requires experienced crew)
        <55:    Poor (congested, high rework risk)

    Based on Singapore BDAS framework (Poh & Chen 1998, CME).
    """

    score = 100.0
    factors: list[ConstructabilityFactor] = []

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

    # Factor 1: Bar clear spacing (critical for concrete placement)
    if min_clear_spacing is not None and min_clear_spacing < 40:
        penalty = 20.0
        factors.append(
            ConstructabilityFactor(
                factor="bar_spacing",
                score=0,
                penalty=-penalty,
                message=f"Clear spacing {min_clear_spacing:.0f}mm < 40mm (congested)",
                recommendation="Increase width or reduce bar diameter. Impact: High rework risk, poor concrete consolidation.",
            )
        )
        score -= penalty
    elif min_clear_spacing is not None and min_clear_spacing < 60:
        penalty = 10.0
        factors.append(
            ConstructabilityFactor(
                factor="bar_spacing",
                score=0,
                penalty=-penalty,
                message=f"Clear spacing {min_clear_spacing:.0f}mm is tight",
                recommendation="Consider spacing >= 60mm for easier placement. Impact: Increased labor time.",
            )
        )
        score -= penalty

    # Factor 2: Stirrup spacing (affects concrete vibration)
    if min_stirrup_spacing is not None and min_stirrup_spacing < 100:
        penalty = 20.0
        factors.append(
            ConstructabilityFactor(
                factor="stirrup_spacing",
                score=0,
                penalty=-penalty,
                message=(
                    f"Stirrup spacing {min_stirrup_spacing:.0f}mm < 100mm "
                    "(very tight)"
                ),
                recommendation="Increase stirrup diameter or review shear demand. Impact: Poor vibration access.",
            )
        )
        score -= penalty
    elif min_stirrup_spacing is not None and min_stirrup_spacing < 125:
        penalty = 15.0
        factors.append(
            ConstructabilityFactor(
                factor="stirrup_spacing",
                score=0,
                penalty=-penalty,
                message=(
                    f"Stirrup spacing {min_stirrup_spacing:.0f}mm < 125mm " "(tight)"
                ),
                recommendation="Spacing >= 125mm improves concrete vibration. Impact: Moderate labor increase.",
            )
        )
        score -= penalty

    # Factor 3: Bar variety (procurement and site management)
    unique_sizes = len(set(bar_sizes + stirrup_sizes))
    if unique_sizes > 2:
        penalty = 10.0
        factors.append(
            ConstructabilityFactor(
                factor="bar_variety",
                score=0,
                penalty=-penalty,
                message=f"{unique_sizes} bar sizes used (procurement complexity)",
                recommendation="Limit to 2 bar sizes where possible. Impact: Procurement delays, site confusion risk.",
            )
        )
        score -= penalty

    # Factor 4: Standard sizes (inventory and tooling)
    standard_sizes = {8, 10, 12, 16, 20, 25, 32}
    non_standard = [size for size in bar_sizes if size not in standard_sizes]
    if non_standard:
        penalty = 10.0
        factors.append(
            ConstructabilityFactor(
                factor="non_standard_sizes",
                score=0,
                penalty=-penalty,
                message=f"Non-standard sizes used: {non_standard}mm",
                recommendation="Use standard sizes (8,10,12,16,20,25,32mm). Impact: Higher procurement cost, tooling issues.",
            )
        )
        score -= penalty
    elif bar_sizes:
        # Bonus for using standard sizes
        bonus = 5.0
        factors.append(
            ConstructabilityFactor(
                factor="standard_sizes",
                score=bonus,
                penalty=0,
                message="All bars are standard sizes",
                recommendation="",
            )
        )
        score += bonus

    # Factor 5: Layer count (congestion and placement difficulty)
    if max_layers > 2:
        penalty = 15.0
        factors.append(
            ConstructabilityFactor(
                factor="layers",
                score=0,
                penalty=-penalty,
                message=f"{max_layers} layers used (congestion risk)",
                recommendation="Reduce bar count or increase width to keep <=2 layers. Impact: High placement difficulty.",
            )
        )
        score -= penalty

    # Factor 6: Depth increments (formwork reuse)
    # Check if D (total depth) is a multiple of 50mm
    D_mm = detailing.D if hasattr(detailing, "D") else None
    if D_mm is not None:
        if D_mm % 50 == 0:
            bonus = 5.0
            factors.append(
                ConstructabilityFactor(
                    factor="depth_increment",
                    score=bonus,
                    penalty=0,
                    message=f"Depth {D_mm:.0f}mm is 50mm multiple (formwork reuse)",
                    recommendation="",
                )
            )
            score += bonus
        else:
            penalty = 5.0
            factors.append(
                ConstructabilityFactor(
                    factor="depth_increment",
                    score=0,
                    penalty=-penalty,
                    message=f"Depth {D_mm:.0f}mm not 50mm multiple",
                    recommendation="Use 50mm increments (250, 300, 350...) for formwork reuse. Impact: Higher formwork cost.",
                )
            )
            score -= penalty

    # Factor 7: Bar configuration simplicity (2-3 bars per layer ideal)
    if bars:
        bar_counts = [bar.count for bar in bars if bar.count > 0]
        if bar_counts:
            max_bars_per_layer = max(bar_counts)
            if max_bars_per_layer <= 3:
                bonus = 5.0
                factors.append(
                    ConstructabilityFactor(
                        factor="bar_configuration",
                        score=bonus,
                        penalty=0,
                        message="Simple bar configuration (<=3 bars per layer)",
                        recommendation="",
                    )
                )
                score += bonus
            elif max_bars_per_layer > 5:
                penalty = 10.0
                factors.append(
                    ConstructabilityFactor(
                        factor="bar_configuration",
                        score=0,
                        penalty=-penalty,
                        message=f"{max_bars_per_layer} bars in one layer (complex)",
                        recommendation="Consider increasing depth or using larger bars. Impact: Placement complexity.",
                    )
                )
                score -= penalty

    score = max(0.0, min(100.0, score))

    if score >= 85.0:
        rating = "excellent"
    elif score >= 70.0:
        rating = "good"
    elif score >= 55.0:
        rating = "acceptable"
    else:
        rating = "poor"

    overall_message = f"Constructability: {score:.0f}/100 ({rating})"

    return ConstructabilityScore(
        score=score,
        rating=rating,
        factors=factors,
        overall_message=overall_message,
        version="1.0",
    )
