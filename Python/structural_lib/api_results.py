"""Backward compatibility stub.

This module has been migrated to: structural_lib.services.api_results
All functionality is re-exported here for backward compatibility.
Prefer importing directly from structural_lib.services.api_results."""

from __future__ import annotations

from structural_lib.services.api_results import (  # noqa: F401, E402
    CostBreakdown,
    CostOptimizationResult,
    DesignAndDetailResult,
    DesignSuggestionsResult,
    OptimalDesign,
    SmartAnalysisResult,
    Suggestion,
)
