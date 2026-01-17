# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Advisory insights (opt-in) for IS 456 beam designs."""

from .comparison import (
    ComparisonMetrics,
    ComparisonResult,
    CostSensitivityResult,
    DesignAlternative,
    compare_designs,
    cost_aware_sensitivity,
)
from .constructability import calculate_constructability_score
from .cost_optimization import CostOptimizationResult, CostProfile, optimize_beam_design
from .data_types import (
    ConstructabilityFactor,
    ConstructabilityScore,
    HeuristicWarning,
    PredictiveCheckResult,
    RobustnessScore,
    SensitivityResult,
)
from .design_suggestions import (
    DesignSuggestion,
    ImpactLevel,
    SuggestionCategory,
    SuggestionReport,
    suggest_improvements,
)
from .precheck import quick_precheck
from .sensitivity import calculate_robustness, sensitivity_analysis
from .smart_designer import (
    ConstructabilityInsights,
    CostAnalysis,
    DashboardReport,
    DesignSuggestions,
    SensitivityInsights,
    SmartAnalysisSummary,
    SmartDesigner,
    quick_analysis,
)

__all__ = [
    "calculate_constructability_score",
    "calculate_robustness",
    "compare_designs",
    "cost_aware_sensitivity",
    "quick_analysis",
    "quick_precheck",
    "sensitivity_analysis",
    "optimize_beam_design",
    "suggest_improvements",
    "ComparisonMetrics",
    "ComparisonResult",
    "ConstructabilityInsights",
    "CostAnalysis",
    "CostProfile",
    "CostOptimizationResult",
    "CostSensitivityResult",
    "ConstructabilityFactor",
    "ConstructabilityScore",
    "DashboardReport",
    "DesignAlternative",
    "DesignSuggestion",
    "DesignSuggestions",
    "HeuristicWarning",
    "ImpactLevel",
    "PredictiveCheckResult",
    "RobustnessScore",
    "SensitivityInsights",
    "SensitivityResult",
    "SmartAnalysisSummary",
    "SmartDesigner",
    "SuggestionCategory",
    "SuggestionReport",
]
