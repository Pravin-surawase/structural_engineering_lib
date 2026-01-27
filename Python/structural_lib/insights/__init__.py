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
from .dashboard import (
    CodeCheck,
    CodeCheckResult,
    DashboardData,
    RebarSuggestion,
    code_checks_live,
    generate_dashboard,
    suggest_rebar_options,
)
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
    "code_checks_live",
    "compare_designs",
    "cost_aware_sensitivity",
    "generate_dashboard",
    "quick_analysis",
    "quick_precheck",
    "sensitivity_analysis",
    "optimize_beam_design",
    "suggest_improvements",
    "suggest_rebar_options",
    "CodeCheck",
    "CodeCheckResult",
    "ComparisonMetrics",
    "ComparisonResult",
    "ConstructabilityInsights",
    "CostAnalysis",
    "CostProfile",
    "CostOptimizationResult",
    "CostSensitivityResult",
    "ConstructabilityFactor",
    "ConstructabilityScore",
    "DashboardData",
    "DashboardReport",
    "DesignAlternative",
    "DesignSuggestion",
    "DesignSuggestions",
    "HeuristicWarning",
    "ImpactLevel",
    "PredictiveCheckResult",
    "RebarSuggestion",
    "RobustnessScore",
    "SensitivityInsights",
    "SensitivityResult",
    "SmartAnalysisSummary",
    "SmartDesigner",
    "SuggestionCategory",
    "SuggestionReport",
]
