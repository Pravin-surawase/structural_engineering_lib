# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Multi-design comparison and cost-aware sensitivity analysis.

This module provides tools to compare multiple design alternatives and
analyze sensitivity with cost considerations.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from ..data_types import ComplianceCaseResult
from .cost_optimization import CostProfile
from .sensitivity import sensitivity_analysis


@dataclass
class DesignAlternative:
    """A single design alternative for comparison.

    Attributes:
        name: Human-readable name (e.g., "Option A: 300x450")
        parameters: Design parameters dict
        result: Design result (ComplianceCaseResult)
        cost: Total cost (optional)
        cost_breakdown: Detailed cost breakdown (optional)
    """

    name: str
    parameters: dict[str, Any]
    result: ComplianceCaseResult
    cost: float | None = None
    cost_breakdown: dict[str, float] | None = None


@dataclass
class ComparisonMetrics:
    """Metrics for comparing designs.

    All metrics normalized to 0.0-1.0 scale (higher is better).
    """

    structural_safety: float  # Based on utilization (1.0 - util)
    cost_efficiency: float  # Inverse of normalized cost
    constructability: float  # From constructability scoring
    robustness: float  # From sensitivity analysis
    overall_score: float  # Weighted combination

    # Weights used for overall score
    weights: dict[str, float] = field(default_factory=dict)


@dataclass
class ComparisonResult:
    """Result of multi-design comparison.

    Attributes:
        alternatives: List of design alternatives compared
        metrics: Metrics for each alternative
        ranking: Indices sorted by overall score (best first)
        best_alternative_idx: Index of best design
        trade_offs: Key trade-offs between designs
    """

    alternatives: list[DesignAlternative]
    metrics: list[ComparisonMetrics]
    ranking: list[int]
    best_alternative_idx: int
    trade_offs: list[str] = field(default_factory=list)


@dataclass
class CostSensitivityResult:
    """Sensitivity analysis with cost implications.

    Extends standard sensitivity with cost impact.
    """

    parameter: str
    sensitivity: float  # Standard sensitivity coefficient
    impact: str  # "critical", "high", "medium", "low"
    cost_impact_per_percent: float  # $/% change in parameter
    cost_sensitivity: float  # Cost change / parameter change (normalized)
    recommendation: str  # Action recommendation based on cost/benefit


def compare_designs(
    alternatives: list[DesignAlternative],
    *,
    cost_weight: float = 0.3,
    safety_weight: float = 0.4,
    constructability_weight: float = 0.2,
    robustness_weight: float = 0.1,
) -> ComparisonResult:
    """Compare multiple design alternatives.

    Args:
        alternatives: List of design alternatives to compare
        cost_weight: Weight for cost efficiency (0.0-1.0)
        safety_weight: Weight for structural safety (0.0-1.0)
        constructability_weight: Weight for constructability (0.0-1.0)
        robustness_weight: Weight for robustness (0.0-1.0)

    Returns:
        ComparisonResult with ranking and metrics

    Raises:
        ValueError: If alternatives list is empty or weights don't sum to 1.0

    Example:
        >>> from structural_lib.api import design_beam_is456
        >>> from structural_lib.insights import compare_designs, DesignAlternative
        >>>
        >>> # Define alternatives
        >>> alt1_params = {"b_mm": 300, "d_mm": 450, "mu_knm": 120, ...}
        >>> alt1_result = design_beam_is456(**alt1_params).cases[0]
        >>> alt1 = DesignAlternative("Option A", alt1_params, alt1_result, cost=15000)
        >>>
        >>> alt2_params = {"b_mm": 350, "d_mm": 400, "mu_knm": 120, ...}
        >>> alt2_result = design_beam_is456(**alt2_params).cases[0]
        >>> alt2 = DesignAlternative("Option B", alt2_params, alt2_result, cost=16000)
        >>>
        >>> # Compare
        >>> comparison = compare_designs([alt1, alt2])
        >>> best = comparison.alternatives[comparison.best_alternative_idx]
        >>> print(f"Best design: {best.name}")
    """
    if not alternatives:
        raise ValueError("alternatives list cannot be empty")

    weights = {
        "cost": cost_weight,
        "safety": safety_weight,
        "constructability": constructability_weight,
        "robustness": robustness_weight,
    }

    weight_sum = sum(weights.values())
    if abs(weight_sum - 1.0) > 0.01:
        raise ValueError(
            f"Weights must sum to 1.0, got {weight_sum:.3f}. "
            f"Adjust weights: {weights}"
        )

    # Calculate metrics for each alternative
    metrics_list: list[ComparisonMetrics] = []

    # Find min/max for normalization
    costs = [alt.cost for alt in alternatives if alt.cost is not None]
    if costs:
        min_cost = min(costs)
        max_cost = max(costs)
        cost_range = max_cost - min_cost if max_cost > min_cost else 1.0
    else:
        min_cost = 0.0
        cost_range = 1.0

    for alt in alternatives:
        # Structural safety: 1.0 - utilization (capped at 0)
        util = alt.result.governing_utilization
        safety = max(0.0, min(1.0, 1.0 - util))

        # Cost efficiency: inverse of normalized cost
        if alt.cost is not None and costs:
            norm_cost = (alt.cost - min_cost) / cost_range
            cost_eff = 1.0 - norm_cost
        else:
            cost_eff = 0.5  # Neutral if no cost data

        # Constructability: Integration deferred to v0.16 (requires full BeamDesignOutput)
        # Uses conservative default (0.7) until constructability API stabilizes
        constructability = 0.7

        # Robustness: Integration deferred to v0.16 (requires sensitivity analysis API)
        # Uses conservative default (0.6) until sensitivity scoring stabilizes
        robustness = 0.6

        # Overall score
        overall = (
            cost_eff * weights["cost"]
            + safety * weights["safety"]
            + constructability * weights["constructability"]
            + robustness * weights["robustness"]
        )

        metrics_list.append(
            ComparisonMetrics(
                structural_safety=safety,
                cost_efficiency=cost_eff,
                constructability=constructability,
                robustness=robustness,
                overall_score=overall,
                weights=weights.copy(),
            )
        )

    # Rank by overall score
    ranking = sorted(
        range(len(alternatives)),
        key=lambda i: metrics_list[i].overall_score,
        reverse=True,
    )
    best_idx = ranking[0]

    # Identify trade-offs
    trade_offs = _identify_trade_offs(alternatives, metrics_list, ranking)

    return ComparisonResult(
        alternatives=alternatives,
        metrics=metrics_list,
        ranking=ranking,
        best_alternative_idx=best_idx,
        trade_offs=trade_offs,
    )


def cost_aware_sensitivity(
    design_function: Callable[..., ComplianceCaseResult],
    base_params: dict[str, Any],
    cost_profile: CostProfile,
    parameters_to_vary: list[str] | None = None,
    perturbation: float = 0.10,
) -> tuple[list[CostSensitivityResult], float]:
    """Sensitivity analysis with cost implications.

    Combines standard sensitivity analysis with cost impact assessment.

    Args:
        design_function: Design function returning ComplianceCaseResult
        base_params: Baseline design parameters
        cost_profile: Cost profile with unit costs
        parameters_to_vary: Parameters to analyze (default: all numeric)
        perturbation: Perturbation magnitude (default 0.10 = 10%)

    Returns:
        Tuple of:
        - List[CostSensitivityResult]: Sensitivity with cost impact
        - float: Total cost of base design

    Example:
        >>> from structural_lib.insights import cost_aware_sensitivity, CostProfile
        >>> from structural_lib.api import design_beam_is456
        >>>
        >>> params = {"b_mm": 300, "d_mm": 450, "mu_knm": 120, ...}
        >>> costs = CostProfile(
        ...     concrete_per_m3=5000,
        ...     steel_per_kg=50,
        ...     formwork_per_m2=200
        ... )
        >>>
        >>> results, base_cost = cost_aware_sensitivity(
        ...     design_beam_is456,
        ...     params,
        ...     costs,
        ...     parameters_to_vary=["d_mm", "b_mm"]
        ... )
        >>>
        >>> for r in results:
        ...     print(f"{r.parameter}: {r.recommendation}")
    """
    # Run standard sensitivity analysis
    sensitivities, _ = sensitivity_analysis(
        design_function, base_params, parameters_to_vary, perturbation
    )

    # Calculate base cost
    base_cost = _estimate_design_cost(base_params, cost_profile)

    # Enhance with cost information
    cost_sensitivities: list[CostSensitivityResult] = []

    for sens in sensitivities:
        param = sens.parameter
        base_value = base_params.get(param, 0.0)

        # Perturb and calculate cost impact
        perturbed_params = base_params.copy()
        if isinstance(base_value, int | float) and base_value != 0:
            perturbed_params[param] = base_value * (1.0 + perturbation)
            perturbed_cost = _estimate_design_cost(perturbed_params, cost_profile)
            cost_delta = perturbed_cost - base_cost
            cost_impact_per_pct = cost_delta / (perturbation * 100)  # Per 1%
            cost_sensitivity_norm = (cost_delta / base_cost) / perturbation
        else:
            cost_impact_per_pct = 0.0
            cost_sensitivity_norm = 0.0

        # Generate recommendation
        recommendation = _generate_cost_recommendation(
            cost_sensitivity_norm, sens.impact
        )

        cost_sensitivities.append(
            CostSensitivityResult(
                parameter=param,
                sensitivity=sens.sensitivity,
                impact=sens.impact,
                cost_impact_per_percent=cost_impact_per_pct,
                cost_sensitivity=cost_sensitivity_norm,
                recommendation=recommendation,
            )
        )

    return cost_sensitivities, base_cost


def _estimate_design_cost(
    params: dict[str, Any], cost_profile: CostProfile, span_mm: float = 5000.0
) -> float:
    """Estimate design cost from parameters.

    Simplified cost estimation for sensitivity analysis.
    """
    b_mm = params.get("b_mm", 300.0)
    d_mm = params.get("d_mm", 450.0)
    D_mm = params.get("D_mm", d_mm + 50.0)  # Assume 50mm cover if D not given

    # Get concrete grade and cost
    fck_nmm2 = int(params.get("fck_nmm2", 25))
    concrete_cost_per_m3 = cost_profile.concrete_costs.get(fck_nmm2, 6700.0)

    # Volume calculations
    concrete_vol_m3 = (b_mm / 1000.0) * (D_mm / 1000.0) * (span_mm / 1000.0)
    formwork_area_m2 = 2 * ((D_mm / 1000.0) * (span_mm / 1000.0)) + (b_mm / 1000.0) * (
        span_mm / 1000.0
    )

    # Steel estimate (rough - would need actual design)
    steel_kg = concrete_vol_m3 * 100  # ~100 kg/m³ typical

    # Total cost
    cost: float = (
        concrete_vol_m3 * concrete_cost_per_m3
        + steel_kg * cost_profile.steel_cost_per_kg
        + formwork_area_m2 * cost_profile.formwork_cost_per_m2
    )

    return cost


def _generate_cost_recommendation(cost_sens: float, impact: str) -> str:
    """Generate recommendation based on cost sensitivity and impact level."""
    if impact == "critical":
        if cost_sens < 0:
            return "CRITICAL: Increase this parameter (improves safety, reduces cost)"
        else:
            return "CRITICAL: Increase carefully (improves safety but adds cost)"
    elif impact == "high":
        if abs(cost_sens) < 0.1:
            return "HIGH: Adjust this parameter (low cost impact)"
        elif cost_sens < 0:
            return "HIGH: Favorable parameter (improves safety, reduces cost)"
        else:
            return "HIGH: Trade-off parameter (safety vs cost)"
    elif impact == "medium":
        return "MEDIUM: Moderate impact on both safety and cost"
    else:
        return "LOW: Minor impact on safety and cost"


def _identify_trade_offs(
    alternatives: list[DesignAlternative],
    metrics: list[ComparisonMetrics],
    ranking: list[int],
) -> list[str]:
    """Identify key trade-offs between design alternatives."""
    trade_offs: list[str] = []

    if len(alternatives) < 2:
        return trade_offs

    best_idx = ranking[0]
    second_idx = ranking[1]

    best = metrics[best_idx]
    second = metrics[second_idx]

    # Check for Pareto trade-offs
    if best.cost_efficiency < second.cost_efficiency:
        trade_offs.append(
            f"{alternatives[second_idx].name} is more cost-effective, "
            f"but {alternatives[best_idx].name} scores higher overall"
        )

    if best.structural_safety < second.structural_safety:
        trade_offs.append(
            f"{alternatives[second_idx].name} has higher safety margin, "
            f"but {alternatives[best_idx].name} balances all factors better"
        )

    return trade_offs
