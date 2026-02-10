"""Backward compatibility stub.

This module has been migrated to: structural_lib.services.intelligence
All functionality is re-exported here for backward compatibility.
Prefer importing directly from structural_lib.services.intelligence."""

from __future__ import annotations

from structural_lib.services.intelligence import (  # noqa: F401, E402
    ConstructabilityFactor,
    ConstructabilityScore,
    HeuristicWarning,
    PredictiveCheckResult,
    RobustnessScore,
    SensitivityResult,
    calculate_constructability_score,
    calculate_robustness,
    quick_precheck,
    sensitivity_analysis,
)
