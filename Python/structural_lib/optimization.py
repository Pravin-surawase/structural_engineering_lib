"""Optimization algorithms for structural design."""

import time
from dataclasses import dataclass
from typing import List, Tuple, Optional
from structural_lib import flexure
from structural_lib.costing import CostProfile, CostBreakdown, calculate_beam_cost
from structural_lib.data_types import FlexureResult


@dataclass
class OptimizationCandidate:
    """A candidate beam design with cost."""

    b_mm: int
    D_mm: int
    d_mm: int
    fck_nmm2: int
    fy_nmm2: int
    design_result: Optional[FlexureResult]
    cost_breakdown: Optional[CostBreakdown]
    is_valid: bool
    failure_reason: Optional[str] = None


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
    alternatives: List[OptimizationCandidate]

    # Metadata
    candidates_evaluated: int
    candidates_valid: int
    computation_time_sec: float


def optimize_beam_cost(
    span_mm: float,
    mu_knm: float,
    vu_kn: float,
    cost_profile: Optional[CostProfile] = None,
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

    candidates: List[OptimizationCandidate] = []

    # Smart search ranges
    width_options = [230, 300, 400]  # Standard widths (mm)
    depth_min = max(300, int(span_mm / 20))  # span/20 minimum
    depth_max = min(900, int(span_mm / 8))  # span/8 maximum
    depth_options = range(depth_min, depth_max + 1, 50)
    grade_options = [25, 30]  # Most common (start with these)
    steel_options = [500]  # Modern standard

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

    valid_candidates.sort(key=lambda c: c.cost_breakdown.total_cost)

    # Best design
    optimal = valid_candidates[0]

    # Calculate baseline (conservative design: span/12 depth)
    baseline_D = int(span_mm / 12)
    baseline_d = baseline_D - cover_mm
    baseline_design = flexure.design_singly_reinforced(
        b=300, d=baseline_d, d_total=baseline_D, mu_knm=mu_knm, fck=25, fy=500
    )
    baseline_pct = 100 * baseline_design.ast_required / (300 * baseline_d)
    baseline_cost_breakdown = calculate_beam_cost(
        b_mm=300,
        D_mm=baseline_D,
        span_mm=span_mm,
        ast_mm2=baseline_design.ast_required,
        fck_nmm2=25,
        steel_percentage=baseline_pct,
        cost_profile=cost_profile,
    )

    # Calculate savings
    savings = baseline_cost_breakdown.total_cost - optimal.cost_breakdown.total_cost
    savings_pct = 100 * savings / baseline_cost_breakdown.total_cost

    # Top 3 alternatives
    alternatives = valid_candidates[1:4]  # Skip optimal (index 0), get next 3

    computation_time = time.time() - start_time

    return CostOptimizationResult(
        optimal_candidate=optimal,
        baseline_cost=baseline_cost_breakdown.total_cost,
        savings_amount=round(savings, 2),
        savings_percent=round(savings_pct, 2),
        alternatives=alternatives,
        candidates_evaluated=evaluated,
        candidates_valid=valid,
        computation_time_sec=round(computation_time, 3),
    )


def _quick_feasibility(b: float, d: float, mu_knm: float, span_mm: float) -> bool:
    """Quick check if dimensions are feasible before full design."""
    # Check if Mu_lim > Mu (singly reinforced possible)
    mu_lim = flexure.calculate_mu_lim(b, d, 25, 500)  # Assume M25, Fe500
    if mu_lim < mu_knm:
        return False  # Would need doubly reinforced

    # Check practical span/depth ratio (8 to 20)
    span_d_ratio = span_mm / d
    if span_d_ratio < 8 or span_d_ratio > 20:
        return False

    return True


def _check_compliance(
    design: FlexureResult, b: float, d: float, fck: int, fy: int
) -> Tuple[bool, List[str]]:
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
