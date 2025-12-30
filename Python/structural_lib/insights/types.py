"""
Dataclasses for advisory insights (precheck, sensitivity, constructability).
"""

from dataclasses import dataclass
from typing import List

from ..errors import Severity


@dataclass(frozen=True)
class HeuristicWarning:
    """Warning from heuristic pre-check."""

    type: str
    severity: Severity
    message: str
    suggestion: str
    rule_basis: str


@dataclass(frozen=True)
class PredictiveCheckResult:
    """Results from quick heuristic validation."""

    check_time_ms: float
    risk_level: str
    warnings: List[HeuristicWarning]
    recommended_action: str
    heuristics_version: str


@dataclass(frozen=True)
class SensitivityResult:
    """Sensitivity of one parameter."""

    parameter: str
    base_value: float
    perturbed_value: float
    base_utilization: float
    perturbed_utilization: float
    delta_utilization: float
    sensitivity: float
    impact: str


@dataclass(frozen=True)
class RobustnessScore:
    """Overall design robustness assessment."""

    score: float
    rating: str
    vulnerable_parameters: List[str]
    base_utilization: float
    sensitivity_count: int


@dataclass(frozen=True)
class ConstructabilityFactor:
    """One factor in constructability assessment."""

    factor: str
    score: float
    penalty: float
    message: str
    recommendation: str


@dataclass(frozen=True)
class ConstructabilityScore:
    """Overall constructability assessment."""

    score: float
    rating: str
    factors: List[ConstructabilityFactor]
    overall_message: str
    version: str
