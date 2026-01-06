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

__all__ = [
    "calculate_constructability_score",
    "calculate_robustness",
    "compare_designs",
    "cost_aware_sensitivity",
    "quick_precheck",
    "sensitivity_analysis",
    "optimize_beam_design",
    "suggest_improvements",
    "ComparisonMetrics",
    "ComparisonResult",
    "CostProfile",
    "CostOptimizationResult",
    "CostSensitivityResult",
    "ConstructabilityFactor",
    "ConstructabilityScore",
    "DesignAlternative",
    "DesignSuggestion",
    "HeuristicWarning",
    "ImpactLevel",
    "PredictiveCheckResult",
    "RobustnessScore",
    "SensitivityResult",
    "SuggestionCategory",
    "SuggestionReport",
]
