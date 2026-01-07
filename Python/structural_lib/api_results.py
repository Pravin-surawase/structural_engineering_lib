# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       api_results
Description:  Result dataclasses for API functions.

This module provides result objects for API functions that previously returned dicts.
All result classes inherit from BaseResult to ensure consistent interface.

Related:
- TASK-210 (Apply API Guidelines to api.py)
- docs/guidelines/result-object-standard.md
"""

from dataclasses import dataclass
from typing import Any, Optional

from .result_base import BaseResult

# =============================================================================
# Cost Optimization Results
# =============================================================================


@dataclass(frozen=True)
class CostBreakdown:
    """Cost breakdown for a beam design.

    Attributes:
        concrete_cost: Cost of concrete (currency units)
        steel_cost: Cost of steel reinforcement (currency units)
        formwork_cost: Cost of formwork (currency units)
        labor_adjustment: Labor cost adjustment (currency units)
        total_cost: Total cost (currency units)
        currency: Currency code (e.g., "INR", "USD")
    """

    concrete_cost: float
    steel_cost: float
    formwork_cost: float
    labor_adjustment: float
    total_cost: float
    currency: str


@dataclass(frozen=True)
class OptimalDesign:
    """Optimal beam design candidate.

    Attributes:
        b_mm: Beam width (mm)
        D_mm: Overall depth (mm)
        d_mm: Effective depth (mm)
        fck_nmm2: Concrete strength (N/mm²)
        fy_nmm2: Steel yield strength (N/mm²)
        cost_breakdown: Detailed cost breakdown
        is_valid: Whether design meets all requirements
        failure_reason: Reason for failure if not valid
    """

    b_mm: float
    D_mm: float
    d_mm: float
    fck_nmm2: float
    fy_nmm2: float
    cost_breakdown: CostBreakdown
    is_valid: bool
    failure_reason: Optional[str] = None


@dataclass(frozen=True)
class CostOptimizationResult(BaseResult):
    """Result from optimize_beam_cost().

    Provides the most cost-effective beam design that meets IS 456:2000
    requirements, along with alternatives and savings analysis.

    Attributes:
        optimal_design: Best design found
        baseline_cost: Conservative design cost for comparison
        savings_amount: Cost saved vs baseline (currency units)
        savings_percent: Percentage cost saved
        alternatives: Next 3 cheapest valid designs
        candidates_evaluated: Total candidates evaluated
        candidates_valid: Number of valid candidates
        computation_time_sec: Time taken for optimization

    Example:
        >>> result = optimize_beam_cost(...)
        >>> print(result.summary())
        'Optimal: 300×500mm, Cost: INR 45,230, Savings: 18.5%'
        >>> print(f"Width: {result.optimal_design.b_mm}mm")
        >>> print(f"Savings: {result.optimal_design.cost_breakdown.currency}"
        ...       f"{result.savings_amount:,.0f}")
    """

    optimal_design: OptimalDesign
    baseline_cost: float
    savings_amount: float
    savings_percent: float
    alternatives: list[OptimalDesign]
    candidates_evaluated: int
    candidates_valid: int
    computation_time_sec: float

    def summary(self) -> str:
        """Human-readable summary of optimization result."""
        design = self.optimal_design
        return (
            f"Optimal: {design.b_mm:.0f}×{design.D_mm:.0f}mm, "
            f"Cost: {design.cost_breakdown.currency}{design.cost_breakdown.total_cost:,.0f}, "
            f"Savings: {self.savings_percent:.1f}%"
        )


# =============================================================================
# Design Suggestions Results
# =============================================================================


@dataclass(frozen=True)
class Suggestion:
    """Single design improvement suggestion.

    Attributes:
        category: Category (e.g., "geometry", "steel", "cost")
        title: Brief title
        impact: Impact level - "LOW", "MEDIUM", or "HIGH"
        confidence: Confidence score (0.0-1.0)
        rationale: Detailed explanation with reasoning
        estimated_benefit: Quantified benefit if possible
        action_steps: Concrete steps to implement
        clause_refs: IS 456 clause references
    """

    category: str
    title: str
    impact: str  # LOW, MEDIUM, HIGH
    confidence: float  # 0.0-1.0
    rationale: str
    estimated_benefit: Optional[str]
    action_steps: list[str]
    clause_refs: list[str]


@dataclass(frozen=True)
class DesignSuggestionsResult(BaseResult):
    """Result from suggest_beam_design_improvements().

    Provides AI-driven suggestions for improving a beam design across
    multiple dimensions: geometry, steel detailing, cost, constructability,
    serviceability, and materials.

    Attributes:
        suggestions: List of suggestions sorted by priority
        total_count: Total number of suggestions
        high_impact_count: Number of HIGH impact suggestions
        medium_impact_count: Number of MEDIUM impact suggestions
        low_impact_count: Number of LOW impact suggestions
        analysis_time_ms: Time taken for analysis
        engine_version: Suggestion engine version

    Example:
        >>> result = suggest_beam_design_improvements(...)
        >>> print(result.summary())
        'Found 8 suggestions: 2 high, 4 medium, 2 low impact'
        >>> for sug in result.suggestions[:3]:
        ...     print(f"  • [{sug.impact}] {sug.title}")
    """

    suggestions: list[Suggestion]
    total_count: int
    high_impact_count: int
    medium_impact_count: int
    low_impact_count: int
    analysis_time_ms: float
    engine_version: str

    def summary(self) -> str:
        """Human-readable summary of suggestions."""
        return (
            f"Found {self.total_count} suggestions: "
            f"{self.high_impact_count} high, "
            f"{self.medium_impact_count} medium, "
            f"{self.low_impact_count} low impact"
        )

    def high_impact_suggestions(self) -> list[Suggestion]:
        """Get only HIGH impact suggestions."""
        return [s for s in self.suggestions if s.impact == "HIGH"]

    def by_category(self, category: str) -> list[Suggestion]:
        """Get suggestions for a specific category."""
        return [s for s in self.suggestions if s.category == category]


# =============================================================================
# Smart Analysis Results
# =============================================================================


@dataclass(frozen=True)
class SmartAnalysisResult(BaseResult):
    """Result from smart_analyze_design().

    Unified dashboard combining cost optimization, design suggestions,
    sensitivity analysis, and constructability assessment.

    Attributes:
        summary_data: Overall summary (overall_score, recommendations_count, etc.)
        metadata: Analysis metadata (analysis_time, modules_run, etc.)
        cost: Cost optimization results (optional)
        suggestions: Design improvement suggestions (optional)
        sensitivity: Sensitivity analysis results (optional)
        constructability: Constructability assessment (optional)

    Example:
        >>> result = smart_analyze_design(...)
        >>> print(result.summary())
        'Analysis Score: 78.5/100'
        >>> print(result.to_json())  # JSON string
        >>> print(result.to_text())  # Formatted text report
    """

    summary_data: dict[str, Any]
    metadata: dict[str, Any]
    cost: Optional[dict[str, Any]] = None
    suggestions: Optional[dict[str, Any]] = None
    sensitivity: Optional[dict[str, Any]] = None
    constructability: Optional[dict[str, Any]] = None

    def summary(self) -> str:
        """Human-readable summary of analysis."""
        score = self.summary_data.get("overall_score", 0)
        return f"Analysis Score: {score:.1f}/100"

    def to_json(self) -> str:
        """Convert to JSON string.

        Returns:
            JSON-formatted string of the complete analysis

        Example:
            >>> result = smart_analyze_design(...)
            >>> json_str = result.to_json()
            >>> print(json_str[:100])
        """
        import json

        return json.dumps(self.to_dict(), indent=2)

    def to_text(self) -> str:
        """Convert to formatted text report.

        Returns:
            Multi-line text report with sections

        Example:
            >>> result = smart_analyze_design(...)
            >>> print(result.to_text())
            === Smart Design Analysis Report ===
            Overall Score: 78.5/100
            ...
        """
        lines = ["=== Smart Design Analysis Report ===", ""]

        # Summary section
        score = self.summary_data.get("overall_score", 0)
        lines.append(f"Overall Score: {score:.1f}/100")
        lines.append("")

        # Cost section
        if self.cost:
            lines.append("Cost Optimization:")
            savings = self.cost.get("savings_percent", 0)
            lines.append(f"  Savings: {savings:.1f}%")
            lines.append("")

        # Suggestions section
        if self.suggestions:
            lines.append("Design Suggestions:")
            high = self.suggestions.get("high_impact_count", 0)
            med = self.suggestions.get("medium_impact_count", 0)
            low = self.suggestions.get("low_impact_count", 0)
            lines.append(f"  {high} high, {med} medium, {low} low impact")
            lines.append("")

        # Sensitivity section
        if self.sensitivity:
            lines.append("Sensitivity Analysis: Available")
            lines.append("")

        # Constructability section
        if self.constructability:
            lines.append("Constructability Assessment: Available")
            score = self.constructability.get("overall_score", 0)
            lines.append(f"  Score: {score:.1f}/100")
            lines.append("")

        return "\n".join(lines)
