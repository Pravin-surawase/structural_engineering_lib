# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Optimization algorithms for structural design."""

from __future__ import annotations

import time
from dataclasses import dataclass

from structural_lib import flexure
from structural_lib.costing import CostBreakdown, CostProfile, calculate_beam_cost
from structural_lib.data_types import FlexureResult


@dataclass
class OptimizationCandidate:
    """A candidate beam design with cost."""

    b_mm: int
    D_mm: int
    d_mm: int
    fck_nmm2: int
    fy_nmm2: int
    design_result: FlexureResult | None
    cost_breakdown: CostBreakdown | None
    is_valid: bool
    failure_reason: str | None = None


@dataclass
class CostOptimizationResult:
    """Result of cost optimization."""

    # Best design
    optimal_candidate: OptimizationCandidate

    # Comparison with conservative baseline
    baseline_cost: float
    savings_amount: float
    savings_percent: float

    # Alternatives (top 3 designs)
    alternatives: list[OptimizationCandidate]

    # Metadata
    candidates_evaluated: int
    candidates_valid: int
    computation_time_sec: float


def optimize_beam_cost(
    span_mm: float,
    mu_knm: float,
    vu_kn: float,
    cost_profile: CostProfile | None = None,
    cover_mm: int = 40,
) -> CostOptimizationResult:
    """Find cheapest beam design meeting IS 456:2000.

    Uses brute force with intelligent pruning.

    Args:
        span_mm: Beam span (mm)
        mu_knm: Factored bending moment (kNm)
        vu_kn: Factored shear force (kN)
        cost_profile: Regional cost data (defaults to India CPWD 2023)
        cover_mm: Concrete cover (default 40mm)

    Returns:
        CostOptimizationResult with optimal design and alternatives

    Example:
        >>> profile = CostProfile()  # India rates
        >>> result = optimize_beam_cost(5000, 120, 80, profile)
        >>> print(f"Optimal design costs ₹{result.optimal_candidate.cost_breakdown.total_cost}")
        >>> print(f"Savings: {result.savings_percent:.1f}%")
    """
    start_time = time.time()

    if cost_profile is None:
        cost_profile = CostProfile()

    candidates: list[OptimizationCandidate] = []

    # Smart search ranges
    # NOTE: Limited search space for v1.0 (most common grades/steel)
    # Future enhancement: Add M20, M35, Fe415 for comprehensive optimization
    # Current: ~30-50 combinations, Full spec: ~300-500 combinations
    width_options = [230, 300, 400]  # Standard widths (mm)
    depth_min = max(300, int(span_mm / 20))  # span/20 minimum
    depth_max = min(900, int(span_mm / 8))  # span/8 maximum
    depth_options = range(depth_min, depth_max + 1, 50)
    grade_options = [25, 30]  # Most common (M20, M35 reserved for v2.0)
    steel_options = [500]  # Modern standard (Fe415 reserved for v2.0)

    evaluated = 0
    valid = 0

    # Brute force search
    for b in width_options:
        for D in depth_options:
            d = D - cover_mm

            # Quick feasibility check
            if not _quick_feasibility(b, d, mu_knm, span_mm):
                continue

            for fck in grade_options:
                for fy in steel_options:
                    evaluated += 1

                    # Design beam
                    try:
                        design = flexure.design_singly_reinforced(
                            b=b, d=d, d_total=D, mu_knm=mu_knm, fck=fck, fy=fy
                        )
                    except Exception as e:
                        candidates.append(
                            OptimizationCandidate(
                                b_mm=b,
                                D_mm=D,
                                d_mm=d,
                                fck_nmm2=fck,
                                fy_nmm2=fy,
                                design_result=None,
                                cost_breakdown=None,
                                is_valid=False,
                                failure_reason=f"Design failed: {str(e)}",
                            )
                        )
                        continue

                    # Check compliance
                    is_compliant, violations = _check_compliance(design, b, d, fck, fy)
                    if not is_compliant:
                        candidates.append(
                            OptimizationCandidate(
                                b_mm=b,
                                D_mm=D,
                                d_mm=d,
                                fck_nmm2=fck,
                                fy_nmm2=fy,
                                design_result=design,
                                cost_breakdown=None,
                                is_valid=False,
                                failure_reason=f"Compliance violations: {violations}",
                            )
                        )
                        continue

                    # Calculate cost
                    steel_pct = 100 * design.ast_required / (b * d)
                    cost = calculate_beam_cost(
                        b_mm=b,
                        D_mm=D,
                        span_mm=span_mm,
                        ast_mm2=design.ast_required,
                        fck_nmm2=fck,
                        steel_percentage=steel_pct,
                        cost_profile=cost_profile,
                    )

                    valid += 1
                    candidates.append(
                        OptimizationCandidate(
                            b_mm=b,
                            D_mm=D,
                            d_mm=d,
                            fck_nmm2=fck,
                            fy_nmm2=fy,
                            design_result=design,
                            cost_breakdown=cost,
                            is_valid=True,
                        )
                    )

    # Sort by cost (ascending)
    valid_candidates = [c for c in candidates if c.is_valid]
    if not valid_candidates:
        raise ValueError("No valid designs found. Check inputs or loosen constraints.")

    valid_candidates.sort(
        key=lambda c: c.cost_breakdown.total_cost if c.cost_breakdown else float("inf")
    )

    # Best design
    optimal = valid_candidates[0]

    # Calculate baseline (conservative design: span/12 depth)
    # Try M25 first, upgrade to M30 if needed, increase depth if still failing
    baseline_D = int(span_mm / 12)
    baseline_d = baseline_D - cover_mm
    baseline_fck = 25
    baseline_design = flexure.design_singly_reinforced(
        b=300, d=baseline_d, d_total=baseline_D, mu_knm=mu_knm, fck=baseline_fck, fy=500
    )

    # If baseline fails with M25, try M30
    if not baseline_design.is_safe or baseline_design.ast_required == 0:
        baseline_fck = 30
        baseline_design = flexure.design_singly_reinforced(
            b=300,
            d=baseline_d,
            d_total=baseline_D,
            mu_knm=mu_knm,
            fck=baseline_fck,
            fy=500,
        )

        # If still fails, increase depth until it works (span/10)
        if not baseline_design.is_safe or baseline_design.ast_required == 0:
            baseline_D = int(span_mm / 10)  # More conservative
            baseline_d = baseline_D - cover_mm
            baseline_design = flexure.design_singly_reinforced(
                b=300,
                d=baseline_d,
                d_total=baseline_D,
                mu_knm=mu_knm,
                fck=baseline_fck,
                fy=500,
            )

    # Verify baseline is actually valid before using it
    if not baseline_design.is_safe or baseline_design.ast_required == 0:
        # Baseline itself is infeasible - use optimal cost as baseline (no savings)
        baseline_cost_breakdown = optimal.cost_breakdown
    else:
        baseline_pct = 100 * baseline_design.ast_required / (300 * baseline_d)
        baseline_cost_breakdown = calculate_beam_cost(
            b_mm=300,
            D_mm=baseline_D,
            span_mm=span_mm,
            ast_mm2=baseline_design.ast_required,
            fck_nmm2=baseline_fck,
            steel_percentage=baseline_pct,
            cost_profile=cost_profile,
        )

    # Calculate savings
    if baseline_cost_breakdown and optimal.cost_breakdown:
        savings = baseline_cost_breakdown.total_cost - optimal.cost_breakdown.total_cost
        savings_pct = 100 * savings / baseline_cost_breakdown.total_cost
        baseline_cost = baseline_cost_breakdown.total_cost
    else:
        savings = 0.0
        savings_pct = 0.0
        baseline_cost = 0.0

    # Top 3 alternatives
    alternatives = valid_candidates[1:4]  # Skip optimal (index 0), get next 3

    computation_time = time.time() - start_time

    return CostOptimizationResult(
        optimal_candidate=optimal,
        baseline_cost=baseline_cost,
        savings_amount=round(savings, 2),
        savings_percent=round(savings_pct, 2),
        alternatives=alternatives,
        candidates_evaluated=evaluated,
        candidates_valid=valid,
        computation_time_sec=round(computation_time, 3),
    )


def _quick_feasibility(b: float, d: float, mu_knm: float, span_mm: float) -> bool:
    """Quick check if dimensions are feasible before full design."""
    # Check if Mu_lim > Mu for HIGHEST grade we're testing (M30)
    # If it fails for M30, it will fail for all grades (IS 456:2000)
    mu_lim = flexure.calculate_mu_lim(b, d, 30, 500)  # Use M30 (highest grade)
    if mu_lim < mu_knm:
        return False  # Would need doubly reinforced even with M30

    # Check practical span/depth ratio (8 to 20)
    span_d_ratio = span_mm / d
    if span_d_ratio < 8 or span_d_ratio > 20:
        return False

    return True


def _check_compliance(
    design: FlexureResult, b: float, d: float, fck: int, fy: int
) -> tuple[bool, list[str]]:
    """Check if design meets IS 456 requirements."""
    violations = []

    # Check if design was successful
    if design.ast_required <= 0 and design.mu_lim > 0:
        violations.append("Design failed to provide steel area")
        return False, violations

    # Check minimum steel
    pt = 100 * design.ast_required / (b * d)
    pt_min = 100 * 0.85 / fy  # IS 456 Cl 26.5.1.1
    if pt < pt_min:
        violations.append(f"pt ({pt:.3f}%) < pt_min ({pt_min:.3f}%)")

    # Check maximum steel
    pt_max = 4.0  # IS 456 Cl 26.5.1.1
    if pt > pt_max:
        violations.append(f"pt ({pt:.3f}%) > pt_max ({pt_max:.3f}%)")

    return (len(violations) == 0, violations)


# =============================================================================
# Session 34: Rebar Optimization Functions (Phase 2 - Library Refactoring)
# Extracted from ai_workspace.py for framework-agnostic reuse
# =============================================================================


@dataclass
class ConstructabilityResult:
    """Result of constructability scoring.

    Attributes:
        score: Overall score 0-100 (higher = easier to build)
        summary: Short text summary of key factors
        notes: Detailed list of all factors considered
    """

    score: int
    summary: str
    notes: list[str]

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return {
            "score": self.score,
            "summary": self.summary,
            "notes": self.notes,
        }


@dataclass
class RebarOptimizationResult:
    """Result of rebar optimization.

    Attributes:
        bottom_layer1_dia: Bottom layer 1 bar diameter (mm)
        bottom_layer1_count: Number of bars in layer 1
        bottom_layer2_dia: Bottom layer 2 bar diameter (mm), 0 if single layer
        bottom_layer2_count: Number of bars in layer 2, 0 if single layer
        top_dia: Top bar diameter (mm)
        top_count: Number of top bars
        stirrup_dia: Stirrup diameter (mm)
        stirrup_spacing: Stirrup spacing (mm)
        ast_provided_mm2: Total bottom steel area provided
        ast_required_mm2: Steel area required by design
        constructability_score: Score 0-100
    """

    bottom_layer1_dia: int
    bottom_layer1_count: int
    bottom_layer2_dia: int
    bottom_layer2_count: int
    top_dia: int
    top_count: int
    stirrup_dia: int
    stirrup_spacing: int
    ast_provided_mm2: float
    ast_required_mm2: float
    constructability_score: int

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return {
            "bottom_layer1_dia": self.bottom_layer1_dia,
            "bottom_layer1_count": self.bottom_layer1_count,
            "bottom_layer2_dia": self.bottom_layer2_dia,
            "bottom_layer2_count": self.bottom_layer2_count,
            "top_dia": self.top_dia,
            "top_count": self.top_count,
            "stirrup_dia": self.stirrup_dia,
            "stirrup_spacing": self.stirrup_spacing,
            "ast_provided_mm2": self.ast_provided_mm2,
            "ast_required_mm2": self.ast_required_mm2,
            "constructability_score": self.constructability_score,
        }

    def to_session_state_dict(self) -> dict:
        """Convert to format compatible with Streamlit session state."""
        return {
            "bottom_layer1_dia": self.bottom_layer1_dia,
            "bottom_layer1_count": self.bottom_layer1_count,
            "bottom_layer2_dia": self.bottom_layer2_dia,
            "bottom_layer2_count": self.bottom_layer2_count,
            "stirrup_dia": self.stirrup_dia,
            "stirrup_spacing": self.stirrup_spacing,
        }


def calculate_constructability_score(
    *,
    bottom_bars: list[tuple[int, int]],
    top_bars: list[tuple[int, int]],
    stirrup_spacing_mm: int,
    b_mm: float,
) -> ConstructabilityResult:
    """Calculate constructability score for rebar configuration.

    Higher scores indicate easier construction. Factors considered:
    - Fewer bars = easier to place (up to +20 points)
    - Same diameter = easier cutting (up to +20 points)
    - Wider stirrup spacing = easier (up to +20 points)
    - Single layer = easier (up to +20 points)
    - Good width/bar ratio = easier (up to +20 points)

    Args:
        bottom_bars: List of (diameter_mm, count) tuples for bottom reinforcement
        top_bars: List of (diameter_mm, count) tuples for top reinforcement
        stirrup_spacing_mm: Stirrup spacing in mm
        b_mm: Section width in mm

    Returns:
        ConstructabilityResult with score (0-100), summary, and detailed notes.

    Example:
        >>> result = calculate_constructability_score(
        ...     bottom_bars=[(16, 4)],
        ...     top_bars=[(12, 2)],
        ...     stirrup_spacing_mm=150,
        ...     b_mm=300,
        ... )
        >>> result.score
        75

    References:
        - General construction practice guidelines
        - IS 456:2000, Cl 26.3 (Spacing of reinforcement)
    """
    import math

    score = 0
    notes: list[str] = []

    # Count total bottom bars
    total_bottom = sum(count for _, count in bottom_bars)
    if total_bottom <= 3:
        score += 20
        notes.append("Few bars")
    elif total_bottom <= 5:
        score += 10
        notes.append("Moderate bars")
    else:
        notes.append("Many bars - harder placement")

    # Check if all same diameter
    diameters = set(dia for dia, count in bottom_bars if count > 0)
    top_dias = set(dia for dia, count in top_bars if count > 0)
    if len(diameters) == 1:
        score += 20
        notes.append("Uniform dia")
    elif len(diameters) <= 2:
        score += 10

    if top_dias and diameters.intersection(top_dias):
        score += 5
        notes.append("Same as top")

    # Stirrup spacing
    if stirrup_spacing_mm >= 200:
        score += 20
        notes.append("Wide stirrups")
    elif stirrup_spacing_mm >= 150:
        score += 15
        notes.append("OK stirrups")
    elif stirrup_spacing_mm >= 100:
        score += 5
        notes.append("Tight stirrups")
    else:
        notes.append("Very tight stirrups")

    # Single layer bonus
    if len(bottom_bars) == 1 or (len(bottom_bars) == 2 and bottom_bars[1][1] == 0):
        score += 20
        notes.append("Single layer")
    else:
        notes.append("Multi-layer")

    # Width/bar ratio
    bar_spacing_approx = b_mm / max(total_bottom, 1)
    if bar_spacing_approx >= 80:
        score += 20
        notes.append("Good spacing")
    elif bar_spacing_approx >= 50:
        score += 10

    summary = " | ".join(notes[:3])  # First 3 notes
    return ConstructabilityResult(
        score=min(score, 100),
        summary=summary,
        notes=notes,
    )


def suggest_optimal_rebar(
    *,
    b_mm: float,
    D_mm: float,
    mu_knm: float,
    vu_kn: float,
    fck: float = 25.0,
    fy: float = 500.0,
    cover_mm: float = 40.0,
    bar_diameters: list[int] | None = None,
    stirrup_diameters: list[int] | None = None,
    stirrup_spacings: list[int] | None = None,
) -> RebarOptimizationResult | None:
    """Suggest optimal reinforcement for given loads.

    Tries to minimize steel while maintaining IS 456 safety requirements
    and good constructability. Includes shear reinforcement optimization.

    Args:
        b_mm: Section width in mm
        D_mm: Section depth in mm
        mu_knm: Design moment in kN·m
        vu_kn: Design shear in kN
        fck: Characteristic concrete strength (N/mm²), default 25
        fy: Steel yield strength (N/mm²), default 500
        cover_mm: Clear cover in mm, default 40
        bar_diameters: List of available bar diameters (mm), default [10,12,16,20,25,32]
        stirrup_diameters: List of stirrup diameters (mm), default [8,10,12]
        stirrup_spacings: List of spacing options (mm), default [100,125,...,300]

    Returns:
        RebarOptimizationResult with optimized configuration, or None if invalid input.

    Example:
        >>> result = suggest_optimal_rebar(
        ...     b_mm=300, D_mm=450, mu_knm=80, vu_kn=60,
        ...     fck=25, fy=500, cover_mm=40,
        ... )
        >>> result.bottom_layer1_dia
        16
        >>> result.bottom_layer1_count >= 2
        True

    References:
        - IS 456:2000, Cl 26.5.1.1 (Minimum reinforcement)
        - IS 456:2000, Cl 26.3 (Spacing requirements)
        - IS 456:2000, Cl 40.4 (Shear reinforcement design)
    """
    import math

    # Set defaults for options
    if bar_diameters is None:
        bar_diameters = [10, 12, 16, 20, 25, 32]
    if stirrup_diameters is None:
        stirrup_diameters = [8, 10, 12]
    if stirrup_spacings is None:
        stirrup_spacings = [100, 125, 150, 175, 200, 250, 300]

    # Calculate effective depth
    assumed_stirrup = stirrup_diameters[0] if stirrup_diameters else 8
    assumed_bar = bar_diameters[2] if len(bar_diameters) > 2 else 16
    d_eff = D_mm - cover_mm - assumed_stirrup - assumed_bar / 2

    if d_eff <= 0 or fy <= 0:
        return None

    # Calculate required steel area (IS 456 simplified)
    ast_req = mu_knm * 1e6 / (0.87 * fy * 0.9 * d_eff)

    # Ensure minimum steel (IS 456 Cl 26.5.1.1)
    ast_min = 0.85 * b_mm * d_eff / fy
    ast_target = max(ast_req * 1.1, ast_min)  # 10% margin or minimum

    # Try different bar configurations - prefer smaller bars first (economy)
    best_config: dict | None = None
    best_waste = float("inf")

    for dia in bar_diameters:
        area_per_bar = math.pi * (dia / 2) ** 2
        count = max(2, math.ceil(ast_target / area_per_bar))

        # Check if fits in width (clear spacing >= max(dia, 25mm) per IS 456)
        clear_cover = cover_mm + assumed_stirrup
        available = b_mm - 2 * clear_cover - 2 * (dia / 2)
        min_spacing = max(dia, 25)
        max_bars_single = int(available / (dia + min_spacing)) + 1

        if count <= max_bars_single and count <= 6:
            # Single layer works
            waste = count * area_per_bar - ast_target
            if waste >= 0 and waste < best_waste:
                best_waste = waste
                best_config = {
                    "bottom_layer1_dia": dia,
                    "bottom_layer1_count": count,
                    "bottom_layer2_dia": 0,
                    "bottom_layer2_count": 0,
                }
        elif count > max_bars_single:
            # Need 2 layers
            layer1 = min(count // 2 + count % 2, 6)
            layer2 = count - layer1
            if layer1 >= 2 and layer2 >= 0 and layer2 <= 4:
                total = layer1 + layer2
                waste = total * area_per_bar - ast_target
                if waste >= 0 and waste < best_waste:
                    best_waste = waste
                    best_config = {
                        "bottom_layer1_dia": dia,
                        "bottom_layer1_count": layer1,
                        "bottom_layer2_dia": dia if layer2 > 0 else 0,
                        "bottom_layer2_count": layer2,
                    }

    # Fallback: if nothing found, use a safe default
    if best_config is None:
        best_config = {
            "bottom_layer1_dia": 16,
            "bottom_layer1_count": 4,
            "bottom_layer2_dia": 0,
            "bottom_layer2_count": 0,
        }

    # =========================================================================
    # SHEAR REINFORCEMENT (Stirrup) Optimization (IS 456 Cl 40)
    # =========================================================================
    tau_v = (vu_kn * 1000) / (b_mm * d_eff) if d_eff > 0 else 0  # N/mm²

    # Calculate steel provided
    ast_provided = (
        best_config["bottom_layer1_count"]
        * math.pi
        * (best_config["bottom_layer1_dia"] ** 2)
        / 4
    )
    if best_config.get("bottom_layer2_count", 0) > 0:
        ast_provided += (
            best_config["bottom_layer2_count"]
            * math.pi
            * (best_config.get("bottom_layer2_dia", 0) ** 2)
            / 4
        )

    pt = 100 * ast_provided / (b_mm * d_eff) if d_eff > 0 else 0

    # Simplified tau_c calculation (IS 456 Table 19 for fck=25)
    if pt <= 0.15:
        tau_c = 0.28
    elif pt <= 0.25:
        tau_c = 0.36
    elif pt <= 0.50:
        tau_c = 0.48
    elif pt <= 0.75:
        tau_c = 0.56
    elif pt <= 1.00:
        tau_c = 0.62
    elif pt <= 1.50:
        tau_c = 0.71
    else:
        tau_c = 0.79

    # Adjust for concrete grade
    if fck != 25:
        tau_c = tau_c * (fck / 25) ** 0.5

    # Shear to be resisted by stirrups
    vus = (tau_v - tau_c) * b_mm * d_eff / 1000  # kN

    # Select stirrup configuration
    best_stirrup_dia = stirrup_diameters[0] if stirrup_diameters else 8
    best_stirrup_spacing = 150  # Default

    if vus > 0:
        # Need calculated stirrups
        found = False
        for st_dia in stirrup_diameters:
            if found:
                break
            asv = 2 * math.pi * (st_dia / 2) ** 2  # 2-legged stirrup
            for sv in stirrup_spacings:
                # Capacity: Vus = 0.87 * fy * Asv * d / sv (IS 456 Cl 40.4)
                capacity = 0.87 * fy * asv * d_eff / sv / 1000  # kN
                if capacity >= vus:
                    # Check maximum spacing (IS 456 Cl 26.5.1.5)
                    max_sv = min(0.75 * d_eff, 300)
                    if sv <= max_sv:
                        best_stirrup_dia = st_dia
                        best_stirrup_spacing = sv
                        found = True
                        break
    else:
        # Minimum stirrups only (IS 456 Cl 26.5.1.6)
        found = False
        for st_dia in stirrup_diameters:
            if found:
                break
            asv = 2 * math.pi * (st_dia / 2) ** 2
            for sv in stirrup_spacings:
                ratio = asv / (b_mm * sv)
                min_ratio = 0.4 / fy
                max_sv = min(0.75 * d_eff, 300)
                if ratio >= min_ratio and sv <= max_sv:
                    best_stirrup_dia = st_dia
                    best_stirrup_spacing = sv
                    found = True
                    break

    # Calculate constructability
    constr = calculate_constructability_score(
        bottom_bars=[
            (best_config["bottom_layer1_dia"], best_config["bottom_layer1_count"]),
            (
                best_config.get("bottom_layer2_dia", 0),
                best_config.get("bottom_layer2_count", 0),
            ),
        ],
        top_bars=[(12, 2)],  # Assume nominal top bars
        stirrup_spacing_mm=best_stirrup_spacing,
        b_mm=b_mm,
    )

    return RebarOptimizationResult(
        bottom_layer1_dia=best_config["bottom_layer1_dia"],
        bottom_layer1_count=best_config["bottom_layer1_count"],
        bottom_layer2_dia=best_config.get("bottom_layer2_dia", 0),
        bottom_layer2_count=best_config.get("bottom_layer2_count", 0),
        top_dia=12,
        top_count=2,
        stirrup_dia=best_stirrup_dia,
        stirrup_spacing=int(best_stirrup_spacing),
        ast_provided_mm2=ast_provided,
        ast_required_mm2=ast_target,
        constructability_score=constr.score,
    )
