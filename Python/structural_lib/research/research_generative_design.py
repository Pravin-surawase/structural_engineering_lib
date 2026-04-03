# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
RESEARCH PROTOTYPE — NOT FOR STRUCTURAL DESIGN

Research Prototype: Generative Design Intelligence
Innovation Cycle: 2
Status: Prototype
Author: innovator agent
Date: 2026-04-03

Problem:
    Every structural engineering tool returns ONE design for given inputs.
    Engineers never see the full design landscape, can't compare trade-offs
    quantitatively, and spend 30-40% of time on manual comparison and
    documentation. No tool generates all valid designs, finds the Pareto
    frontier across cost/carbon/utilization, and explains WHY.

Approach:
    1. Generate ALL feasible (b, D, fck, fy) combinations for a given load
    2. Design each via design_beam_is456() — IS 456 hard constraints enforced
    3. Score each on three objectives: cost, carbon, utilization
    4. Extract Pareto front (non-dominated set)
    5. Recommend designs for different engineer "personas"
    6. Generate engineering narratives explaining trade-offs

Validation:
    - All designs must pass IS 456 flexure + shear checks
    - Pareto front must contain no dominated points
    - Cheapest design must approximately match optimize_beam_cost() result
    - Monotonicity: higher concrete grade → higher cost and carbon
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from structural_lib.research.research_sustainability import score_beam_carbon
from structural_lib.services.api import design_beam_is456
from structural_lib.services.costing import (
    CostBreakdown,
    CostProfile,
    calculate_beam_cost,
)

# Safety factors are HARDCODED constants — NEVER parameters
# IS 456:2000 Table 18:  γc = 1.5 (concrete), γs = 1.15 (steel)
_GAMMA_C = 1.5
_GAMMA_S = 1.15


# =============================================================================
# Design Space Configuration
# =============================================================================

# Standard beam widths (mm) — Indian practice
STANDARD_WIDTHS = [200, 230, 250, 300, 350, 400]

# Concrete grades (fck in N/mm²)
CONCRETE_GRADES = [20, 25, 30, 35, 40]

# Steel grades (fy in N/mm²)
STEEL_GRADES = [415, 500]

# Depth step (mm)
DEPTH_STEP_MM = 25

# Cover (mm) — IS 456 Table 16 nominal cover for moderate exposure
DEFAULT_COVER_MM = 40


# =============================================================================
# Design Personas — Pre-built Preference Profiles
# =============================================================================


@dataclass(frozen=True)
class DesignPersona:
    """An engineer preference profile for design selection."""

    name: str
    description: str
    weight_cost: float  # Weight for cost objective (0-1)
    weight_carbon: float  # Weight for carbon objective (0-1)
    weight_util: float  # Weight for utilization objective (0-1)


PERSONAS: dict[str, DesignPersona] = {
    "cost_engineer": DesignPersona(
        name="Cost Engineer",
        description="Minimize cost — accept higher utilization & carbon",
        weight_cost=0.7,
        weight_carbon=0.1,
        weight_util=0.2,
    ),
    "green_engineer": DesignPersona(
        name="Green Engineer",
        description="Minimize carbon footprint — accept higher cost",
        weight_cost=0.15,
        weight_carbon=0.70,
        weight_util=0.15,
    ),
    "conservative_engineer": DesignPersona(
        name="Conservative Engineer",
        description="Maximize safety margin — generous reserve capacity",
        weight_cost=0.1,
        weight_carbon=0.1,
        weight_util=0.8,
    ),
    "balanced_engineer": DesignPersona(
        name="Balanced Engineer",
        description="Equal weight to cost, carbon, and safety",
        weight_cost=0.34,
        weight_carbon=0.33,
        weight_util=0.33,
    ),
}


# =============================================================================
# Data Types
# =============================================================================


@dataclass
class DesignCandidate:
    """A single candidate beam design with multi-objective scores."""

    # Geometry
    b_mm: int
    D_mm: int
    d_mm: int
    fck: int
    fy: int

    # Structural results
    ast_required_mm2: float
    asc_required_mm2: float
    xu: float
    xu_max: float
    mu_lim_knm: float
    shear_spacing_mm: float

    # Objectives (lower is better for all three)
    cost_inr: float
    carbon_kgco2e: float
    utilization: float  # xu / xu_max (0 to 1)

    # Detailed breakdowns
    cost_breakdown: CostBreakdown | None = None
    carbon_rating: str = ""

    # Pareto membership
    is_pareto: bool = False
    pareto_rank: int = 0  # 0 = on Pareto front

    def steel_percentage(self) -> float:
        """pt = 100 * Ast / (b * d)."""
        return 100.0 * self.ast_required_mm2 / (self.b_mm * self.d_mm)


@dataclass
class PersonaRecommendation:
    """A design recommendation for a specific engineer persona."""

    persona: DesignPersona
    recommended: DesignCandidate
    score: float
    narrative: str  # Engineering explanation


@dataclass
class DesignSpaceStats:
    """Summary statistics of the design space exploration."""

    total_candidates: int
    valid_candidates: int
    pareto_front_size: int
    cheapest: DesignCandidate | None
    greenest: DesignCandidate | None
    most_conservative: DesignCandidate | None
    cost_range_inr: tuple[float, float]
    carbon_range_kgco2e: tuple[float, float]
    utilization_range: tuple[float, float]


@dataclass
class GenerativeDesignResult:
    """Complete result of generative design exploration.

    RESEARCH PROTOTYPE — NOT FOR STRUCTURAL DESIGN
    """

    # Input echo
    span_mm: float
    mu_knm: float
    vu_kn: float

    # All valid designs
    candidates: list[DesignCandidate]

    # Pareto front
    pareto_front: list[DesignCandidate]

    # Persona recommendations
    recommendations: dict[str, PersonaRecommendation]

    # Statistics
    stats: DesignSpaceStats

    # Metadata
    computation_time_sec: float

    def summary(self) -> str:
        """Generate a comprehensive human-readable summary."""
        lines = [
            "═" * 78,
            "  GENERATIVE DESIGN INTELLIGENCE — BEAM DESIGN EXPLORER",
            "  RESEARCH PROTOTYPE — NOT FOR STRUCTURAL DESIGN",
            "═" * 78,
            "",
            f"  Load Case: Mu = {self.mu_knm} kNm, Vu = {self.vu_kn} kN, "
            f"Span = {self.span_mm:.0f} mm",
            "",
            "─" * 78,
            "  DESIGN SPACE OVERVIEW",
            "─" * 78,
            f"  Candidates evaluated:  {self.stats.total_candidates}",
            f"  Valid designs (IS 456): {self.stats.valid_candidates}",
            f"  Pareto-optimal designs: {self.stats.pareto_front_size}",
            "",
            f"  Cost range:        ₹{self.stats.cost_range_inr[0]:,.0f} — "
            f"₹{self.stats.cost_range_inr[1]:,.0f}",
            f"  Carbon range:      {self.stats.carbon_range_kgco2e[0]:.1f} — "
            f"{self.stats.carbon_range_kgco2e[1]:.1f} kgCO₂e",
            f"  Utilization range: {self.stats.utilization_range[0]:.2f} — "
            f"{self.stats.utilization_range[1]:.2f}",
        ]

        # Pareto front summary
        lines.extend(
            [
                "",
                "─" * 78,
                "  PARETO FRONT (non-dominated designs)",
                "─" * 78,
                f"  {'b×D':>10}  {'fck':>4}  {'fy':>4}  {'Cost(₹)':>10}  "
                f"{'CO₂(kg)':>9}  {'Util':>6}  {'pt%':>5}  {'Rating':>6}",
                "  " + "─" * 70,
            ]
        )
        for c in self.pareto_front:
            lines.append(
                f"  {c.b_mm}×{c.D_mm:>4}  M{c.fck:>2}  {c.fy:>4}  "
                f"₹{c.cost_inr:>9,.0f}  {c.carbon_kgco2e:>8.1f}  "
                f"{c.utilization:>5.3f}  {c.steel_percentage():>5.2f}  "
                f"{c.carbon_rating:>6}"
            )

        # Persona recommendations
        lines.extend(
            [
                "",
                "─" * 78,
                "  RECOMMENDATIONS BY ENGINEER PROFILE",
                "─" * 78,
            ]
        )
        for _key, rec in self.recommendations.items():
            lines.extend(
                [
                    "",
                    f"  ▸ {rec.persona.name} ({rec.persona.description})",
                    f"    → {rec.recommended.b_mm}×{rec.recommended.D_mm} "
                    f"M{rec.recommended.fck} Fe{rec.recommended.fy}  |  "
                    f"₹{rec.recommended.cost_inr:,.0f}  |  "
                    f"{rec.recommended.carbon_kgco2e:.1f} kgCO₂e  |  "
                    f"util={rec.recommended.utilization:.3f}",
                    f"    {rec.narrative}",
                ]
            )

        lines.extend(
            [
                "",
                "─" * 78,
                f"  Computation time: {self.computation_time_sec:.2f}s",
                "═" * 78,
            ]
        )
        return "\n".join(lines)


# =============================================================================
# Core Algorithm
# =============================================================================


def _compute_pareto_front(
    candidates: list[DesignCandidate],
) -> list[DesignCandidate]:
    """Extract the Pareto front from candidates.

    A candidate is Pareto-optimal if no other candidate dominates it on
    ALL three objectives (cost, carbon, utilization). Lower is better for all.
    """
    n = len(candidates)
    is_dominated = [False] * n

    for i in range(n):
        if is_dominated[i]:
            continue
        for j in range(n):
            if i == j or is_dominated[j]:
                continue
            ci = candidates[i]
            cj = candidates[j]

            # Check if j dominates i (j is better or equal in ALL, strictly
            # better in at least one)
            if (
                cj.cost_inr <= ci.cost_inr
                and cj.carbon_kgco2e <= ci.carbon_kgco2e
                and cj.utilization <= ci.utilization
                and (
                    cj.cost_inr < ci.cost_inr
                    or cj.carbon_kgco2e < ci.carbon_kgco2e
                    or cj.utilization < ci.utilization
                )
            ):
                is_dominated[i] = True
                break

    front = []
    for i, c in enumerate(candidates):
        if not is_dominated[i]:
            c.is_pareto = True
            c.pareto_rank = 0
            front.append(c)

    # Sort Pareto front by cost
    front.sort(key=lambda c: c.cost_inr)
    return front


def _score_candidate(
    candidate: DesignCandidate,
    persona: DesignPersona,
    cost_range: tuple[float, float],
    carbon_range: tuple[float, float],
    util_range: tuple[float, float],
) -> float:
    """Score a candidate for a persona (lower is better).

    Normalizes all objectives to [0, 1] then applies persona weights.
    """

    # Normalize to [0, 1] — handle degenerate ranges
    def _normalize(val: float, lo: float, hi: float) -> float:
        if hi <= lo:
            return 0.0
        return (val - lo) / (hi - lo)

    cost_norm = _normalize(candidate.cost_inr, cost_range[0], cost_range[1])
    carbon_norm = _normalize(candidate.carbon_kgco2e, carbon_range[0], carbon_range[1])
    util_norm = _normalize(candidate.utilization, util_range[0], util_range[1])

    return (
        persona.weight_cost * cost_norm
        + persona.weight_carbon * carbon_norm
        + persona.weight_util * util_norm
    )


def _generate_narrative(
    rec: DesignCandidate,
    cheapest: DesignCandidate,
    greenest: DesignCandidate,
    most_conservative: DesignCandidate,
    persona: DesignPersona,
) -> str:
    """Generate an engineering narrative explaining WHY this design.

    Returns plain-language explanation a junior engineer can understand.
    """
    parts: list[str] = []

    # Comparison deltas
    cost_vs_cheapest = (
        (rec.cost_inr - cheapest.cost_inr) / cheapest.cost_inr * 100
        if cheapest.cost_inr > 0
        else 0
    )
    carbon_vs_greenest = (
        (rec.carbon_kgco2e - greenest.carbon_kgco2e) / greenest.carbon_kgco2e * 100
        if greenest.carbon_kgco2e > 0
        else 0
    )
    # Identity check — is this THE cheapest/greenest/most conservative?
    is_cheapest = abs(rec.cost_inr - cheapest.cost_inr) < 1.0
    is_greenest = abs(rec.carbon_kgco2e - greenest.carbon_kgco2e) < 0.1
    is_most_conservative = abs(rec.utilization - most_conservative.utilization) < 0.001

    if is_cheapest and is_greenest and is_most_conservative:
        return (
            "This design dominates all others — it's simultaneously "
            "the cheapest, greenest, and most conservative option. "
            "A rare find where no trade-off is needed."
        )

    # Build explanation based on persona
    if persona.weight_cost >= 0.5:
        if is_cheapest:
            parts.append(f"This is the lowest-cost design at ₹{rec.cost_inr:,.0f}.")
        else:
            parts.append(
                f"At ₹{rec.cost_inr:,.0f}, this is "
                f"{cost_vs_cheapest:+.1f}% vs the cheapest option."
            )
        if not is_greenest:
            parts.append(
                f"Carbon is {carbon_vs_greenest:+.1f}% vs the greenest — "
                f"an acceptable trade-off for the cost saving."
            )
    elif persona.weight_carbon >= 0.5:
        if is_greenest:
            parts.append(
                f"This is the lowest-carbon design at "
                f"{rec.carbon_kgco2e:.1f} kgCO₂e."
            )
        else:
            parts.append(
                f"At {rec.carbon_kgco2e:.1f} kgCO₂e, this is "
                f"{carbon_vs_greenest:+.1f}% vs the greenest option."
            )
        if not is_cheapest:
            parts.append(
                f"It costs ₹{rec.cost_inr:,.0f} "
                f"({cost_vs_cheapest:+.1f}% vs cheapest) — "
                f"worth the premium for sustainability."
            )
    elif persona.weight_util >= 0.5:
        if is_most_conservative:
            parts.append(
                f"This is the most conservative design with "
                f"utilization={rec.utilization:.3f} (xu/xu_max)."
            )
        else:
            parts.append(
                f"Utilization={rec.utilization:.3f} gives "
                f"{(1 - rec.utilization)*100:.0f}% reserve capacity."
            )
        parts.append(
            "The generous safety margin means this beam can handle "
            "load increases without redesign."
        )
    else:
        # Balanced
        parts.append(
            f"This design balances all three objectives: "
            f"₹{rec.cost_inr:,.0f} cost, "
            f"{rec.carbon_kgco2e:.1f} kgCO₂e carbon, "
            f"{rec.utilization:.3f} utilization."
        )
        # Explain what was traded off
        tradeoffs = []
        if cost_vs_cheapest > 5:
            tradeoffs.append(f"{cost_vs_cheapest:.0f}% more than cheapest")
        if carbon_vs_greenest > 5:
            tradeoffs.append(f"{carbon_vs_greenest:.0f}% more carbon " "than greenest")
        if tradeoffs:
            parts.append(
                f"Trade-offs: {'; '.join(tradeoffs)} — "
                f"but no single metric is extreme."
            )

    # Rebar detail
    parts.append(
        f"Requires {rec.ast_required_mm2:.0f} mm² tension steel "
        f"(pt={rec.steel_percentage():.2f}%)."
    )

    return " ".join(parts)


# =============================================================================
# Main Entry Point
# =============================================================================


def explore_design_space(
    span_mm: float,
    mu_knm: float,
    vu_kn: float,
    cost_profile: CostProfile | None = None,
    cover_mm: int = DEFAULT_COVER_MM,
    widths: list[int] | None = None,
    grades: list[int] | None = None,
    steel_grades: list[int] | None = None,
) -> GenerativeDesignResult:
    """Explore the full beam design space and find Pareto-optimal solutions.

    RESEARCH PROTOTYPE — NOT FOR STRUCTURAL DESIGN.

    Generates all feasible beam designs for a given load case, evaluates
    each on cost, carbon, and utilization, extracts the Pareto front, and
    recommends designs for different engineer personas with engineering
    narrative explanations.

    Safety factors (γc=1.5, γs=1.15) are hardcoded in IS 456 — NEVER
    parameters. All designs must pass IS 456 checks. This function does
    NOT modify or relax any code requirements.

    Args:
        span_mm: Beam span (mm).
        mu_knm: Factored bending moment (kN·m).
        vu_kn: Factored shear force (kN).
        cost_profile: Regional cost data (defaults to India CPWD 2023).
        cover_mm: Nominal cover (mm, default 40 per IS 456 Table 16).
        widths: Custom width options (mm). Defaults to STANDARD_WIDTHS.
        grades: Custom concrete grade options. Defaults to CONCRETE_GRADES.
        steel_grades: Custom steel grade options. Defaults to STEEL_GRADES.

    Returns:
        GenerativeDesignResult with full design space, Pareto front,
        persona recommendations, and engineering narratives.

    Example:
        >>> result = explore_design_space(
        ...     span_mm=5000, mu_knm=120, vu_kn=80
        ... )
        >>> print(result.summary())
        >>> for rec in result.recommendations.values():
        ...     print(f"{rec.persona.name}: {rec.narrative}")
    """
    start_time = time.time()

    if cost_profile is None:
        cost_profile = CostProfile()

    width_options = widths or STANDARD_WIDTHS
    grade_options = grades or CONCRETE_GRADES
    fy_options = steel_grades or STEEL_GRADES

    # Depth range: IS 456 guidance span/20 to span/8
    depth_min = max(300, int(span_mm / 20))
    # Round up to nearest DEPTH_STEP_MM
    depth_min = (depth_min + DEPTH_STEP_MM - 1) // DEPTH_STEP_MM * DEPTH_STEP_MM
    depth_max = min(1000, int(span_mm / 8))

    candidates: list[DesignCandidate] = []
    total_evaluated = 0

    for b in width_options:
        for D in range(depth_min, depth_max + 1, DEPTH_STEP_MM):
            d = D - cover_mm

            # Quick feasibility: d must be positive, b/D ratio sensible
            if d <= 0 or b > D:
                continue

            for fck in grade_options:
                for fy in fy_options:
                    total_evaluated += 1

                    try:
                        result = design_beam_is456(
                            units="IS456",
                            b_mm=float(b),
                            D_mm=float(D),
                            d_mm=float(d),
                            fck_nmm2=float(fck),
                            fy_nmm2=float(fy),
                            mu_knm=mu_knm,
                            vu_kn=vu_kn,
                        )
                    except Exception:
                        continue

                    # Must pass both flexure and shear
                    if not result.flexure.is_safe or not result.shear.is_safe:
                        continue

                    ast = result.flexure.ast_required
                    asc = result.flexure.asc_required or 0.0
                    xu = result.flexure.xu
                    xu_max = result.flexure.xu_max

                    # Skip doubly-reinforced for now (compression steel > 0)
                    # These are valid but make comparison complex
                    if asc > 0:
                        continue

                    utilization = xu / xu_max if xu_max > 0 else 1.0

                    # Calculate cost
                    pt = 100.0 * ast / (b * d)
                    cost_bd = calculate_beam_cost(
                        b_mm=float(b),
                        D_mm=float(D),
                        span_mm=span_mm,
                        ast_mm2=ast,
                        fck_nmm2=fck,
                        steel_percentage=pt,
                        cost_profile=cost_profile,
                    )

                    # Calculate carbon
                    carbon = score_beam_carbon(
                        b_mm=float(b),
                        D_mm=float(D),
                        span_mm=span_mm,
                        fck=fck,
                        ast_mm2=ast,
                        asc_mm2=asc,
                        mu_knm=mu_knm,
                    )

                    candidate = DesignCandidate(
                        b_mm=b,
                        D_mm=D,
                        d_mm=d,
                        fck=fck,
                        fy=fy,
                        ast_required_mm2=ast,
                        asc_required_mm2=asc,
                        xu=xu,
                        xu_max=xu_max,
                        mu_lim_knm=result.flexure.mu_lim,
                        shear_spacing_mm=result.shear.spacing,
                        cost_inr=cost_bd.total_cost,
                        carbon_kgco2e=carbon.total_kgco2e,
                        utilization=utilization,
                        cost_breakdown=cost_bd,
                        carbon_rating=carbon.rating,
                    )
                    candidates.append(candidate)

    if not candidates:
        raise ValueError(
            f"No valid designs found for Mu={mu_knm} kNm, Vu={vu_kn} kN, "
            f"span={span_mm} mm. Check if the loading is feasible for the "
            f"given dimension ranges."
        )

    # ── Extract Pareto front ──
    pareto_front = _compute_pareto_front(candidates)

    # ── Compute ranges for normalization ──
    costs = [c.cost_inr for c in candidates]
    carbons = [c.carbon_kgco2e for c in candidates]
    utils = [c.utilization for c in candidates]

    cost_range = (min(costs), max(costs))
    carbon_range = (min(carbons), max(carbons))
    util_range = (min(utils), max(utils))

    # ── Find extremes ──
    cheapest = min(candidates, key=lambda c: c.cost_inr)
    greenest = min(candidates, key=lambda c: c.carbon_kgco2e)
    most_conservative = min(candidates, key=lambda c: c.utilization)

    # ── Persona recommendations ──
    recommendations: dict[str, PersonaRecommendation] = {}

    for key, persona in PERSONAS.items():
        # Score only Pareto-optimal designs
        best = min(
            pareto_front,
            key=lambda c: _score_candidate(
                c, persona, cost_range, carbon_range, util_range
            ),
        )
        score = _score_candidate(best, persona, cost_range, carbon_range, util_range)
        narrative = _generate_narrative(
            best, cheapest, greenest, most_conservative, persona
        )
        recommendations[key] = PersonaRecommendation(
            persona=persona,
            recommended=best,
            score=score,
            narrative=narrative,
        )

    # ── Build stats ──
    stats = DesignSpaceStats(
        total_candidates=total_evaluated,
        valid_candidates=len(candidates),
        pareto_front_size=len(pareto_front),
        cheapest=cheapest,
        greenest=greenest,
        most_conservative=most_conservative,
        cost_range_inr=cost_range,
        carbon_range_kgco2e=carbon_range,
        utilization_range=util_range,
    )

    computation_time = time.time() - start_time

    return GenerativeDesignResult(
        span_mm=span_mm,
        mu_knm=mu_knm,
        vu_kn=vu_kn,
        candidates=candidates,
        pareto_front=pareto_front,
        recommendations=recommendations,
        stats=stats,
        computation_time_sec=computation_time,
    )


# =============================================================================
# Demo
# =============================================================================


def _demo() -> None:
    """Run a demo of the generative design explorer."""
    print()
    print("RESEARCH PROTOTYPE — NOT FOR STRUCTURAL DESIGN")
    print()

    result = explore_design_space(
        span_mm=5000.0,
        mu_knm=120.0,
        vu_kn=80.0,
    )
    print(result.summary())

    # Show detailed narratives
    print()
    print("═" * 78)
    print("  DETAILED ENGINEERING NARRATIVES")
    print("═" * 78)
    for _key, rec in result.recommendations.items():
        print()
        print(f"  ━━━ {rec.persona.name} ━━━")
        print(f"  {rec.narrative}")
        print(
            f"  Design: {rec.recommended.b_mm}×{rec.recommended.D_mm} "
            f"M{rec.recommended.fck} Fe{rec.recommended.fy}"
        )
        print(
            f"  Ast = {rec.recommended.ast_required_mm2:.0f} mm² "
            f"(pt = {rec.recommended.steel_percentage():.2f}%)"
        )
        print(
            f"  xu/xu_max = {rec.recommended.utilization:.3f} "
            f"→ {(1 - rec.recommended.utilization)*100:.0f}% reserve"
        )
        print(
            f"  Shear stirrup spacing = " f"{rec.recommended.shear_spacing_mm:.0f} mm"
        )


if __name__ == "__main__":
    _demo()
