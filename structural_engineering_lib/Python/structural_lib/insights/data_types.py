# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Compatibility shim for the renamed insights types module.

This preserves imports like `structural_lib.insights.data_types`.
"""

from __future__ import annotations

from .types import (
    ConstructabilityFactor,
    ConstructabilityScore,
    HeuristicWarning,
    PredictiveCheckResult,
    RobustnessScore,
    SensitivityResult,
)

__all__ = [
    "HeuristicWarning",
    "PredictiveCheckResult",
    "SensitivityResult",
    "RobustnessScore",
    "ConstructabilityFactor",
    "ConstructabilityScore",
]
