# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
RESEARCH PROTOTYPE — NOT FOR STRUCTURAL DESIGN

Research Prototype: Sustainability Scoring — Embodied Carbon per Beam Design
Innovation Cycle: 1
Status: Prototype
Author: innovator agent
Date: 2026-04-03

Problem:
    RC beam designs produce structural and cost results but zero environmental
    impact data. Engineers have no way to compare designs by embodied carbon
    or track against net-zero targets.

Approach:
    Calculate embodied carbon (kgCO₂e) using ICE Database v4.1 emission
    factors for concrete grades and steel rebar. Score each design with a
    letter rating (A+ to E) based on carbon efficiency (kgCO₂e per kN·m
    capacity). Reuse existing costing utilities for volume/weight.

Validation:
    Cross-check against IStructE Structural Carbon Tool methodology.
    Verify monotonicity (higher grade → higher carbon for same dimensions).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from structural_lib.services.costing import (
    calculate_concrete_volume,
    calculate_steel_weight,
)

# =============================================================================
# Emission Factors — ICE Database v4.1 (Oct 2025)
# =============================================================================
# Source: Inventory of Carbon and Energy, Circular Ecology / University of Bath
# Units: kgCO₂e per m³ (concrete) or kgCO₂e per kg (steel)
#
# Indian concrete factors are adjusted upward from European values due to
# higher clinker ratio and older kilns in many Indian cement plants.
# These are HARDCODED — emission factors are scientific data, not parameters.
# =============================================================================

CONCRETE_EMISSION_FACTORS: dict[int, float] = {
    # fck (N/mm²) → kgCO₂e per m³ of concrete
    20: 240.0,
    25: 290.0,
    30: 340.0,
    35: 390.0,
    40: 440.0,
}

# Steel rebar emission factors (kgCO₂e per kg)
STEEL_REBAR_EMISSION_FACTOR_GLOBAL = 1.40  # Global average (BOS + EAF mix)
STEEL_REBAR_EMISSION_FACTOR_INDIA = 1.10  # India (higher EAF share)

# Default: Use India factor for this library's IS 456 focus
STEEL_REBAR_EMISSION_FACTOR = STEEL_REBAR_EMISSION_FACTOR_INDIA

# Concrete density (kg/m³) — standard reinforced concrete
CONCRETE_DENSITY_KG_PER_M3 = 2400.0


# =============================================================================
# Carbon Rating Thresholds
# =============================================================================
# Based on kgCO₂e per kN·m of moment capacity
# Benchmarked against typical Indian beam designs (M25, Fe500)

CARBON_RATINGS: list[tuple[str, float, str]] = [
    ("A+", 1.5, "Exceptional — minimal carbon footprint"),
    ("A", 2.5, "Excellent — well-optimized design"),
    ("B", 4.0, "Good — typical efficient design"),
    ("C", 6.0, "Average — room for improvement"),
    ("D", 10.0, "Below average — review design choices"),
    ("E", float("inf"), "Poor — significant optimization needed"),
]


# =============================================================================
# Data Types
# =============================================================================


@dataclass
class CarbonScore:
    """Embodied carbon score for a single beam design.

    All values in kgCO₂e (carbon dioxide equivalent).
    """

    # Absolute emissions
    total_kgco2e: float
    concrete_kgco2e: float
    steel_kgco2e: float

    # Normalized metrics
    carbon_per_meter: float  # kgCO₂e per meter of beam length
    carbon_per_knm: float  # kgCO₂e per kN·m of moment capacity

    # Breakdown percentages
    concrete_share_pct: float  # % of total from concrete
    steel_share_pct: float  # % of total from steel

    # Rating
    rating: str  # "A+" to "E"
    rating_description: str

    # Input echo (for traceability)
    inputs: dict[str, float] = field(default_factory=dict)

    def summary(self) -> str:
        """Human-readable summary."""
        lines = [
            "═" * 60,
            "  EMBODIED CARBON SCORE",
            "  RESEARCH PROTOTYPE — NOT FOR STRUCTURAL DESIGN",
            "═" * 60,
            f"  Rating:        {self.rating} — {self.rating_description}",
            f"  Total Carbon:  {self.total_kgco2e:.1f} kgCO₂e",
            f"    Concrete:    {self.concrete_kgco2e:.1f} kgCO₂e "
            f"({self.concrete_share_pct:.0f}%)",
            f"    Steel:       {self.steel_kgco2e:.1f} kgCO₂e "
            f"({self.steel_share_pct:.0f}%)",
            "─" * 60,
            f"  Per meter:     {self.carbon_per_meter:.2f} kgCO₂e/m",
            f"  Per kN·m:      {self.carbon_per_knm:.2f} kgCO₂e/kN·m",
            "═" * 60,
        ]
        return "\n".join(lines)


@dataclass
class CarbonComparison:
    """Comparison of multiple designs by carbon footprint."""

    scores: list[CarbonScore]
    labels: list[str]
    best_idx: int
    savings_vs_worst_pct: float
    savings_vs_worst_kgco2e: float


# =============================================================================
# Core Functions
# =============================================================================


def _get_concrete_emission_factor(fck: int) -> float:
    """Get emission factor for a concrete grade.

    Args:
        fck: Characteristic compressive strength (N/mm²).
             Must be one of: 20, 25, 30, 35, 40.

    Returns:
        Emission factor in kgCO₂e per m³.

    Raises:
        ValueError: If fck is not a recognized grade.
    """
    if fck not in CONCRETE_EMISSION_FACTORS:
        known = sorted(CONCRETE_EMISSION_FACTORS.keys())
        raise ValueError(
            f"Unknown concrete grade fck={fck} N/mm². "
            f"Supported grades: {known}. "
            f"Interpolation is not used — only tested grades are allowed."
        )
    return CONCRETE_EMISSION_FACTORS[fck]


def _assign_rating(carbon_per_knm: float) -> tuple[str, str]:
    """Assign a carbon rating based on efficiency.

    Args:
        carbon_per_knm: Carbon efficiency in kgCO₂e per kN·m capacity.

    Returns:
        Tuple of (rating letter, description).
    """
    for rating, threshold, description in CARBON_RATINGS:
        if carbon_per_knm <= threshold:
            return rating, description
    # Should never reach here due to inf threshold
    return "E", "Poor — significant optimization needed"


def score_beam_carbon(
    b_mm: float,
    D_mm: float,
    span_mm: float,
    fck: int,
    ast_mm2: float,
    asc_mm2: float = 0.0,
    mu_knm: float | None = None,
) -> CarbonScore:
    """Calculate the embodied carbon score for a beam design.

    Uses ICE Database v4.1 emission factors. This is a RESEARCH PROTOTYPE
    and must NOT be used for actual carbon reporting without validation.

    Args:
        b_mm: Beam width (mm).
        D_mm: Beam overall depth (mm).
        span_mm: Beam span (mm).
        fck: Concrete grade — characteristic compressive strength (N/mm²).
             Must be one of: 20, 25, 30, 35, 40.
        ast_mm2: Area of tension reinforcement (mm²).
        asc_mm2: Area of compression reinforcement (mm², default 0).
        mu_knm: Moment capacity (kN·m). If provided, used for carbon
                 efficiency rating. If None, rating is based on per-meter
                 metric only.

    Returns:
        CarbonScore with full breakdown and rating.

    Example:
        >>> score = score_beam_carbon(
        ...     b_mm=300, D_mm=500, span_mm=5000,
        ...     fck=25, ast_mm2=1200, mu_knm=180
        ... )
        >>> print(score.summary())
    """
    # Validate inputs
    if b_mm <= 0 or D_mm <= 0 or span_mm <= 0:
        raise ValueError("All dimensions must be positive")
    if ast_mm2 < 0 or asc_mm2 < 0:
        raise ValueError("Steel areas must be non-negative")

    # --- Concrete carbon ---
    concrete_vol_m3 = calculate_concrete_volume(b_mm, D_mm, span_mm)
    ef_concrete = _get_concrete_emission_factor(fck)
    concrete_kgco2e = concrete_vol_m3 * ef_concrete

    # --- Steel carbon ---
    total_steel_mm2 = ast_mm2 + asc_mm2
    steel_weight_kg = calculate_steel_weight(total_steel_mm2, span_mm)
    steel_kgco2e = steel_weight_kg * STEEL_REBAR_EMISSION_FACTOR

    # --- Totals ---
    total_kgco2e = concrete_kgco2e + steel_kgco2e

    # --- Normalized metrics ---
    span_m = span_mm / 1000.0
    carbon_per_meter = total_kgco2e / span_m if span_m > 0 else 0.0

    # Carbon efficiency (per unit capacity)
    if mu_knm is not None and mu_knm > 0:
        carbon_per_knm = total_kgco2e / mu_knm
    else:
        # Fallback: use per-meter metric scaled to a reference capacity
        # This is approximate — mu_knm should be provided for accurate rating
        carbon_per_knm = carbon_per_meter / 30.0  # ~30 kN·m/m is typical

    # --- Shares ---
    if total_kgco2e > 0:
        concrete_share = (concrete_kgco2e / total_kgco2e) * 100.0
        steel_share = (steel_kgco2e / total_kgco2e) * 100.0
    else:
        concrete_share = 0.0
        steel_share = 0.0

    # --- Rating ---
    rating, rating_desc = _assign_rating(carbon_per_knm)

    return CarbonScore(
        total_kgco2e=round(total_kgco2e, 2),
        concrete_kgco2e=round(concrete_kgco2e, 2),
        steel_kgco2e=round(steel_kgco2e, 2),
        carbon_per_meter=round(carbon_per_meter, 2),
        carbon_per_knm=round(carbon_per_knm, 2),
        concrete_share_pct=round(concrete_share, 1),
        steel_share_pct=round(steel_share, 1),
        rating=rating,
        rating_description=rating_desc,
        inputs={
            "b_mm": b_mm,
            "D_mm": D_mm,
            "span_mm": span_mm,
            "fck": fck,
            "ast_mm2": ast_mm2,
            "asc_mm2": asc_mm2,
            "mu_knm": mu_knm if mu_knm is not None else 0.0,
        },
    )


def compare_carbon(
    designs: list[dict],
    labels: list[str] | None = None,
) -> CarbonComparison:
    """Compare multiple beam designs by embodied carbon.

    Each design dict must include: b_mm, D_mm, span_mm, fck, ast_mm2.
    Optional: asc_mm2, mu_knm.

    Args:
        designs: List of design parameter dicts.
        labels: Optional labels for each design (e.g., "Option A").

    Returns:
        CarbonComparison with scores, rankings, and savings potential.

    Example:
        >>> designs = [
        ...     {"b_mm": 300, "D_mm": 500, "span_mm": 5000,
        ...      "fck": 25, "ast_mm2": 1200, "mu_knm": 180},
        ...     {"b_mm": 230, "D_mm": 600, "span_mm": 5000,
        ...      "fck": 30, "ast_mm2": 900, "mu_knm": 185},
        ... ]
        >>> result = compare_carbon(designs, ["Wide-shallow", "Narrow-deep"])
    """
    if not designs:
        raise ValueError("At least one design is required")

    if labels is None:
        labels = [f"Design {i + 1}" for i in range(len(designs))]

    if len(labels) != len(designs):
        raise ValueError("Number of labels must match number of designs")

    scores = []
    for d in designs:
        score = score_beam_carbon(
            b_mm=d["b_mm"],
            D_mm=d["D_mm"],
            span_mm=d["span_mm"],
            fck=d["fck"],
            ast_mm2=d["ast_mm2"],
            asc_mm2=d.get("asc_mm2", 0.0),
            mu_knm=d.get("mu_knm"),
        )
        scores.append(score)

    # Find best (lowest carbon)
    totals = [s.total_kgco2e for s in scores]
    best_idx = totals.index(min(totals))
    worst_total = max(totals)
    best_total = min(totals)

    if worst_total > 0:
        savings_pct = ((worst_total - best_total) / worst_total) * 100.0
    else:
        savings_pct = 0.0

    return CarbonComparison(
        scores=scores,
        labels=labels,
        best_idx=best_idx,
        savings_vs_worst_pct=round(savings_pct, 1),
        savings_vs_worst_kgco2e=round(worst_total - best_total, 2),
    )


def print_comparison(comparison: CarbonComparison) -> None:
    """Print a formatted comparison table.

    Args:
        comparison: Result from compare_carbon().
    """
    print("═" * 78)
    print("  EMBODIED CARBON COMPARISON")
    print("  RESEARCH PROTOTYPE — NOT FOR STRUCTURAL DESIGN")
    print("═" * 78)
    print(
        f"  {'Design':<20} {'Total kgCO₂e':>14} {'Per meter':>12} "
        f"{'Rating':>8} {'Concrete%':>10}"
    )
    print("─" * 78)

    for i, (label, score) in enumerate(
        zip(comparison.labels, comparison.scores, strict=False)
    ):
        marker = " ★" if i == comparison.best_idx else ""
        print(
            f"  {label:<20} {score.total_kgco2e:>12.1f}   "
            f"{score.carbon_per_meter:>10.2f}   "
            f"{score.rating:>6}   "
            f"{score.concrete_share_pct:>7.0f}%{marker}"
        )

    print("─" * 78)
    print(
        f"  Best option: {comparison.labels[comparison.best_idx]} "
        f"(saves {comparison.savings_vs_worst_kgco2e:.1f} kgCO₂e, "
        f"{comparison.savings_vs_worst_pct:.0f}% vs worst)"
    )
    print("═" * 78)


# =============================================================================
# Demo / Self-Test
# =============================================================================


def _demo() -> None:
    """Run a demonstration of the sustainability scoring prototype."""
    print("\n" + "=" * 78)
    print("  SUSTAINABILITY SCORING — INNOVATION PROTOTYPE DEMO")
    print("  RESEARCH PROTOTYPE — NOT FOR STRUCTURAL DESIGN")
    print("=" * 78)

    # --- Demo 1: Single beam score ---
    print("\n▸ Demo 1: Single beam carbon score")
    print("  Beam: 300×500mm, span 5m, M25, Ast=1200mm², Mu=180 kN·m")
    score = score_beam_carbon(
        b_mm=300,
        D_mm=500,
        span_mm=5000,
        fck=25,
        ast_mm2=1200,
        mu_knm=180,
    )
    print(score.summary())

    # --- Demo 2: Grade comparison ---
    print("\n▸ Demo 2: Same beam, different concrete grades")
    designs = [
        {
            "b_mm": 300,
            "D_mm": 500,
            "span_mm": 5000,
            "fck": 20,
            "ast_mm2": 1400,
            "mu_knm": 175,
        },
        {
            "b_mm": 300,
            "D_mm": 500,
            "span_mm": 5000,
            "fck": 25,
            "ast_mm2": 1200,
            "mu_knm": 180,
        },
        {
            "b_mm": 300,
            "D_mm": 500,
            "span_mm": 5000,
            "fck": 30,
            "ast_mm2": 1050,
            "mu_knm": 185,
        },
        {
            "b_mm": 300,
            "D_mm": 500,
            "span_mm": 5000,
            "fck": 35,
            "ast_mm2": 950,
            "mu_knm": 188,
        },
    ]
    labels = ["M20 + more steel", "M25 baseline", "M30 less steel", "M35 least steel"]
    comparison = compare_carbon(designs, labels)
    print_comparison(comparison)

    # --- Demo 3: Cross-section alternatives ---
    print("\n▸ Demo 3: Different cross-sections for same moment")
    alt_designs = [
        {
            "b_mm": 230,
            "D_mm": 600,
            "span_mm": 6000,
            "fck": 25,
            "ast_mm2": 900,
            "mu_knm": 200,
        },
        {
            "b_mm": 300,
            "D_mm": 500,
            "span_mm": 6000,
            "fck": 25,
            "ast_mm2": 1300,
            "mu_knm": 200,
        },
        {
            "b_mm": 400,
            "D_mm": 450,
            "span_mm": 6000,
            "fck": 25,
            "ast_mm2": 1600,
            "mu_knm": 200,
        },
    ]
    alt_labels = [
        "230×600 (narrow-deep)",
        "300×500 (balanced)",
        "400×450 (wide-shallow)",
    ]
    alt_comparison = compare_carbon(alt_designs, alt_labels)
    print_comparison(alt_comparison)

    # --- Demo 4: Carbon vs Cost insight ---
    print("\n▸ Demo 4: Carbon breakdown analysis")
    for grade in [20, 25, 30, 35, 40]:
        s = score_beam_carbon(
            b_mm=300,
            D_mm=500,
            span_mm=5000,
            fck=grade,
            ast_mm2=1200,
        )
        print(
            f"  M{grade}: {s.total_kgco2e:6.1f} kgCO₂e  "
            f"(concrete: {s.concrete_share_pct:.0f}%, "
            f"steel: {s.steel_share_pct:.0f}%)"
        )


if __name__ == "__main__":
    _demo()
