# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Cost optimization feature for beam design.

This module provides AI-driven cost optimization that finds the cheapest
beam design meeting IS 456:2000 requirements.
"""

from __future__ import annotations

from structural_lib.services.costing import CostProfile
from structural_lib.services.optimization import (
    CostOptimizationResult,
    OptimizationConstraints,
    optimize_beam_cost,
)

__all__ = ["optimize_beam_design", "CostProfile", "CostOptimizationResult"]


def optimize_beam_design(
    span_mm: float,
    mu_knm: float,
    vu_kn: float,
    cost_profile: CostProfile | None = None,
    *,
    effective_depth_deduction_mm: float = 40,
    fck_options: tuple[int, ...] = (25, 30),
    fy_options: tuple[int, ...] = (500,),
    constraints: OptimizationConstraints | None = None,
    asv_mm2: float = 100.53,
    max_alternatives: int = 3,
) -> CostOptimizationResult:
    """Find the most cost-effective beam design.

    This function automatically finds the cheapest beam dimensions and
    materials that meet IS 456:2000 safety requirements.

    Args:
        span_mm: Beam span in millimeters
        mu_knm: Factored bending moment in kNm
        vu_kn: Factored shear force in kN
        cost_profile: Regional cost data (defaults to India CPWD 2023)
        effective_depth_deduction_mm: Total ``D - d`` deduction in mm.
        fck_options: Exact concrete grades to evaluate.
        fy_options: Exact reinforcement grades to evaluate.
        constraints: Explicit width/depth grid and utilization threshold.
        asv_mm2: Area of effective vertical stirrup legs in mm².
        max_alternatives: Maximum number of ranked alternatives.

    Returns:
        CostOptimizationResult containing:
            - Optimal design (b, D, fck, fy)
            - Cost breakdown
            - Savings vs conservative design
            - Alternative designs

    Example:
        >>> from structural_lib.insights import optimize_beam_design, CostProfile
        >>>
        >>> # Use default India costs
        >>> result = optimize_beam_design(
        ...     span_mm=5000,
        ...     mu_knm=120,
        ...     vu_kn=80
        ... )
        >>>
        >>> print(f"Optimal: {result.optimal_candidate.b_mm}×{result.optimal_candidate.D_mm}mm")
        >>> print(f"Cost: ₹{result.optimal_candidate.cost_breakdown.total_cost:,.0f}")
        >>> print(f"Savings: {result.savings_percent:.1f}%")
        >>>
        >>> # Custom regional costs
        >>> custom_costs = CostProfile(
        ...     concrete_costs={25: 7000, 30: 7500},
        ...     steel_cost_per_kg=75,
        ...     location_factor=1.1  # 10% higher than national avg
        ... )
        >>> result = optimize_beam_design(5000, 120, 80, custom_costs)
    """
    return optimize_beam_cost(
        span_mm,
        mu_knm,
        vu_kn,
        cost_profile,
        cover_mm=effective_depth_deduction_mm,
        fck_options=fck_options,
        fy_options=fy_options,
        constraints=constraints,
        asv_mm2=asv_mm2,
        max_alternatives=max_alternatives,
    )
