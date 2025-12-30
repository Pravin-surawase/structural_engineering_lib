"""Sensitivity analysis for beam designs (advisory only)."""

from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, List, Tuple

from .types import RobustnessScore, SensitivityResult


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
    base_params: Dict[str, Any],
    parameters_to_vary: Iterable[str] | None = None,
    perturbation: float = 0.10,
) -> Tuple[List[SensitivityResult], RobustnessScore]:
    """Analyze parameter sensitivity via one-at-a-time perturbation.

    The design function must return a ComplianceCaseResult with
    governing_utilization and is_ok.
    """

    if perturbation <= 0:
        raise ValueError("perturbation must be > 0")

    base_result = design_function(**base_params)
    base_utilization = getattr(base_result, "governing_utilization", None)
    if base_utilization is None:
        raise ValueError("design_function must return governing_utilization")

    parameters = list(parameters_to_vary or base_params.keys())
    sensitivities: List[SensitivityResult] = []

    for param in parameters:
        if param not in base_params:
            continue

        base_value = base_params[param]
        if not isinstance(base_value, (int, float)):
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
    sensitivities: List[SensitivityResult],
    base_utilization: float,
) -> RobustnessScore:
    """Calculate design robustness score (0-1)."""

    if not sensitivities:
        return RobustnessScore(
            score=0.5,
            rating="unknown",
            vulnerable_parameters=[],
            base_utilization=base_utilization,
            sensitivity_count=0,
        )

    high_impact = sum(1 for s in sensitivities if s.impact in {"high", "critical"})
    medium_impact = sum(1 for s in sensitivities if s.impact == "medium")

    score = 1.0
    score -= high_impact * 0.15
    score -= medium_impact * 0.05
    score -= max(0.0, (base_utilization - 0.5) * 0.2)

    score = max(0.0, min(1.0, score))

    if score >= 0.80:
        rating = "excellent"
    elif score >= 0.65:
        rating = "good"
    elif score >= 0.50:
        rating = "acceptable"
    else:
        rating = "poor"

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
