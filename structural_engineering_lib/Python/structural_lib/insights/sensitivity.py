# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Sensitivity analysis for beam designs (advisory only)."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from .data_types import RobustnessScore, SensitivityResult


def _classify_impact(sensitivity: float, critical: bool = False) -> str:
    if critical:
        return "critical"
    abs_sens = abs(sensitivity)
    if abs_sens > 0.5:
        return "high"
    if abs_sens > 0.2:
        return "medium"
    return "low"


def sensitivity_analysis(
    design_function: Callable[..., Any],
    base_params: dict[str, Any],
    parameters_to_vary: Iterable[str] | None = None,
    perturbation: float = 0.10,
) -> tuple[list[SensitivityResult], RobustnessScore]:
    """Analyze parameter sensitivity via one-at-a-time perturbation.

    Uses finite difference method with normalized sensitivity coefficient:
        S = (ΔU/U) / (Δp/p)

    where U = utilization ratio, p = parameter value.

    This produces dimensionless coefficients that can be compared across
    different parameter types (mm, MPa, kNm, etc.).

    Args:
        design_function: Function that takes **params and returns
                        ComplianceCaseResult with governing_utilization and is_ok
        base_params: Baseline parameter values (dict)
        parameters_to_vary: List of parameter names to analyze.
                           Defaults to all numeric parameters in base_params.
        perturbation: Fractional perturbation (default 0.10 = 10%)

    Returns:
        Tuple of:
        - List[SensitivityResult]: Per-parameter sensitivities, sorted by |sensitivity|
        - RobustnessScore: Overall design robustness assessment

    Example:
        >>> from structural_lib.api import design_beam_is456
        >>> sens, robust = sensitivity_analysis(
        ...     design_beam_is456,
        ...     {"units": "IS456", "mu_knm": 120, "b_mm": 300, "d_mm": 450, ...},
        ...     ["d_mm", "b_mm", "fck_nmm2"]
        ... )
        >>> print(f"Most critical: {sens[0].parameter} (S={sens[0].sensitivity:.3f})")
        >>> print(f"Robustness: {robust.score:.2f} ({robust.rating})")

    The design function must return a ComplianceCaseResult with
    governing_utilization and is_ok attributes.
    """

    if perturbation <= 0:
        raise ValueError("perturbation must be > 0")

    base_result = design_function(**base_params)
    base_utilization = getattr(base_result, "governing_utilization", None)
    if base_utilization is None:
        raise ValueError("design_function must return governing_utilization")

    parameters = list(parameters_to_vary or base_params.keys())
    sensitivities: list[SensitivityResult] = []

    for param in parameters:
        if param not in base_params:
            continue

        base_value = base_params[param]
        if not isinstance(base_value, int | float):
            continue

        perturbed_value = base_value * (1 + perturbation)
        perturbed_params = dict(base_params)
        perturbed_params[param] = perturbed_value

        critical = False
        try:
            perturbed_result = design_function(**perturbed_params)
            perturbed_util = getattr(
                perturbed_result, "governing_utilization", base_utilization
            )
            if not getattr(perturbed_result, "is_ok", True):
                critical = True
                perturbed_util = max(float(perturbed_util), 1.0)
        except Exception:
            critical = True
            perturbed_util = max(float(base_utilization), 1.0)

        delta_util = perturbed_util - float(base_utilization)
        # Normalized sensitivity coefficient (dimensionless)
        # S = (ΔU/U) / (Δp/p) where U=utilization, p=parameter
        # This makes sensitivities comparable across different parameter units
        if base_utilization != 0:
            sensitivity = (delta_util / float(base_utilization)) / perturbation
        else:
            # Edge case: base utilization is zero (cannot normalize)
            sensitivity = delta_util / perturbation
        impact = _classify_impact(sensitivity, critical=critical)

        sensitivities.append(
            SensitivityResult(
                parameter=param,
                base_value=base_value,
                perturbed_value=perturbed_value,
                base_utilization=float(base_utilization),
                perturbed_utilization=float(perturbed_util),
                delta_utilization=float(delta_util),
                sensitivity=float(sensitivity),
                impact=impact,
            )
        )

    sensitivities.sort(key=lambda item: abs(item.sensitivity), reverse=True)
    robustness = calculate_robustness(sensitivities, float(base_utilization))

    return sensitivities, robustness


def calculate_robustness(
    sensitivities: list[SensitivityResult],
    base_utilization: float,
    failure_threshold: float = 1.0,
) -> RobustnessScore:
    """Calculate design robustness score (0-1) using margin-based method.

    Robustness measures how much parameters can vary before design fails.
    Uses normalized sensitivity coefficients to compute allowable variations.

    Method:
        1. For each parameter, compute allowable variation before failure
        2. Robustness = min(allowable_variations) / 0.20 (normalized to 0-1)
        3. 0.20 (20%) variation threshold defines "very robust"

    Args:
        sensitivities: List of sensitivity results (sorted by |sensitivity|)
        base_utilization: Current utilization ratio (e.g., 0.78)
        failure_threshold: Utilization threshold for failure (default 1.0)

    Returns:
        RobustnessScore with:
        - score: 0-1 (1.0 = very robust, can tolerate 20%+ variations)
        - rating: "excellent" | "good" | "acceptable" | "poor"
        - vulnerable_parameters: Parameters with lowest margin

    Example:
        >>> # Design at 78% utilization, failure at 100%
        >>> # Margin to failure: 22 percentage points
        >>> # If depth sensitivity = -0.237, can increase depth by 22/78/0.237 ≈ 12%
        >>> robustness = calculate_robustness(sens, 0.78)
        >>> print(f"Can tolerate depth variation of {allowable_d*100:.1f}%")
    """

    if not sensitivities:
        return RobustnessScore(
            score=0.5,
            rating="unknown",
            vulnerable_parameters=[],
            base_utilization=base_utilization,
            sensitivity_count=0,
        )

    # Edge case: already at or above failure threshold
    if base_utilization >= failure_threshold:
        return RobustnessScore(
            score=0.0,
            rating="poor",
            vulnerable_parameters=[s.parameter for s in sensitivities[:3]],
            base_utilization=base_utilization,
            sensitivity_count=len(sensitivities),
        )

    # Margin to failure (as fraction of current utilization)
    margin = failure_threshold - base_utilization

    # Calculate allowable variation for each parameter
    allowable_variations = []

    for s in sensitivities:
        if s.sensitivity >= 0:
            # Increasing this parameter increases utilization (bad)
            # Most critical in decreasing direction
            # For now, focus on parameters that help when increased
            continue

        # Sensitivity is negative (increasing parameter decreases utilization)
        # How much can we DECREASE parameter before failure?
        # (Decreasing parameter increases utilization)

        abs_sensitivity = abs(s.sensitivity)
        if abs_sensitivity < 1e-6:
            # Negligible sensitivity, effectively infinite margin
            continue

        # Allowable fractional decrease in parameter before hitting failure
        # delta_util_to_fail = margin
        # delta_util = sensitivity × delta_param_fraction
        # margin = |sensitivity| × delta_param_decrease
        # delta_param_decrease = margin / (base_util × |sensitivity|)
        allowable_decrease = margin / (base_utilization * abs_sensitivity)
        allowable_variations.append(allowable_decrease)

    if not allowable_variations:
        # No parameters help when increased (all increase utilization)
        # Design is fragile
        score = 0.3  # Base score for unfavorable sensitivity profile
    else:
        # Robustness based on minimum allowable variation
        min_variation = min(allowable_variations)

        # Normalize: 0.20 (20%) variation = score 1.0
        score = min(min_variation / 0.20, 1.0)

    # Ensure score is in [0, 1]
    score = max(0.0, min(1.0, score))

    # Rating based on score
    if score >= 0.80:
        rating = "excellent"
    elif score >= 0.65:
        rating = "good"
    elif score >= 0.50:
        rating = "acceptable"
    else:
        rating = "poor"

    # Identify vulnerable parameters (high or critical impact)
    vulnerable = [
        s.parameter for s in sensitivities if s.impact in {"high", "medium", "critical"}
    ]

    return RobustnessScore(
        score=score,
        rating=rating,
        vulnerable_parameters=vulnerable,
        base_utilization=base_utilization,
        sensitivity_count=len(sensitivities),
    )
