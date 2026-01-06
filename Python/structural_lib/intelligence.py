# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Compatibility shim for legacy imports.

Use `structural_lib.insights` for new code. This module re-exports the
advisory insights without changing core APIs.
"""

from .insights import (
    calculate_constructability_score,
    calculate_robustness,
    quick_precheck,
    sensitivity_analysis,
)
from .insights.types import (
    ConstructabilityFactor,
    ConstructabilityScore,
    HeuristicWarning,
    PredictiveCheckResult,
    RobustnessScore,
    SensitivityResult,
)

__all__ = [
    "calculate_constructability_score",
    "calculate_robustness",
    "quick_precheck",
    "sensitivity_analysis",
    "ConstructabilityFactor",
    "ConstructabilityScore",
    "HeuristicWarning",
    "PredictiveCheckResult",
    "RobustnessScore",
    "SensitivityResult",
]
