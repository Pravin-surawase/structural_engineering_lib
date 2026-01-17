# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Dataclasses for advisory insights (precheck, sensitivity, constructability).

All dataclasses provide `.to_dict()` methods for JSON serialization.
"""

from dataclasses import dataclass
from typing import Any

from ..errors import Severity


@dataclass(frozen=True)
class HeuristicWarning:
    """Warning from heuristic pre-check."""

    type: str
    severity: Severity
    message: str
    suggestion: str
    rule_basis: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "type": self.type,
            "severity": self.severity.value,  # Convert enum to string
            "message": self.message,
            "suggestion": self.suggestion,
            "rule_basis": self.rule_basis,
        }


@dataclass(frozen=True)
class PredictiveCheckResult:
    """Results from quick heuristic validation."""

    check_time_ms: float
    risk_level: str
    warnings: list[HeuristicWarning]
    recommended_action: str
    heuristics_version: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "check_time_ms": self.check_time_ms,
            "risk_level": self.risk_level,
            "warnings": [w.to_dict() for w in self.warnings],
            "recommended_action": self.recommended_action,
            "heuristics_version": self.heuristics_version,
        }


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

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "parameter": self.parameter,
            "base_value": self.base_value,
            "perturbed_value": self.perturbed_value,
            "base_utilization": self.base_utilization,
            "perturbed_utilization": self.perturbed_utilization,
            "delta_utilization": self.delta_utilization,
            "sensitivity": self.sensitivity,
            "impact": self.impact,
        }


@dataclass(frozen=True)
class RobustnessScore:
    """Overall design robustness assessment."""

    score: float
    rating: str
    vulnerable_parameters: list[str]
    base_utilization: float
    sensitivity_count: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "score": self.score,
            "rating": self.rating,
            "vulnerable_parameters": self.vulnerable_parameters,
            "base_utilization": self.base_utilization,
            "sensitivity_count": self.sensitivity_count,
        }


@dataclass(frozen=True)
class ConstructabilityFactor:
    """One factor in constructability assessment."""

    factor: str
    score: float
    penalty: float
    message: str
    recommendation: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "factor": self.factor,
            "score": self.score,
            "penalty": self.penalty,
            "message": self.message,
            "recommendation": self.recommendation,
        }


@dataclass(frozen=True)
class ConstructabilityScore:
    """Overall constructability assessment."""

    score: float
    rating: str
    factors: list[ConstructabilityFactor]
    overall_message: str
    version: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "score": self.score,
            "rating": self.rating,
            "factors": [f.to_dict() for f in self.factors],
            "overall_message": self.overall_message,
            "version": self.version,
        }
