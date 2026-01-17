# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Smart Designer — Unified intelligent design analysis dashboard.

This module provides a unified interface to all smart library features:
- Cost optimization
- Design suggestions
- Sensitivity analysis
- Constructability scoring
- Design comparison

Example:
    >>> from structural_lib.insights import SmartDesigner
    >>> from structural_lib.api import design_beam_is456
    >>>
    >>> # Basic design
    >>> result = design_beam_is456(
    ...     units="IS456", b_mm=300, D_mm=500, d_mm=450,
    ...     fck_nmm2=25, fy_nmm2=500, mu_knm=120, vu_kn=80
    ... )
    >>>
    >>> # Comprehensive smart analysis
    >>> dashboard = SmartDesigner.analyze(
    ...     design=result,
    ...     span_mm=5000,
    ...     mu_knm=120,
    ...     vu_kn=80,
    ...     include_cost=True,
    ...     include_suggestions=True,
    ...     include_sensitivity=True
    ... )
    >>>
    >>> # Dashboard includes all insights in one place
    >>> print(dashboard.summary())
    >>> dashboard.to_json("smart_analysis.json")
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..beam_pipeline import BeamDesignOutput
from ..costing import CostProfile
from . import cost_optimization, design_suggestions, sensitivity


@dataclass
class SmartAnalysisSummary:
    """Summary of smart analysis for quick overview."""

    design_status: str  # "PASS", "FAIL", "WARNING"
    safety_score: float  # 0.0-1.0 (1.0 = perfect safety margin)
    cost_efficiency: float  # 0.0-1.0 (1.0 = optimal)
    constructability: float  # 0.0-1.0 (1.0 = excellent)
    robustness: float  # 0.0-1.0 (1.0 = very robust)
    overall_score: float  # 0.0-1.0 weighted combination
    key_issues: list[str] = field(default_factory=list)
    quick_wins: list[str] = field(default_factory=list)


@dataclass
class CostAnalysis:
    """Cost optimization results."""

    current_cost: float  # Current design cost (Rs)
    optimal_cost: float  # Best achievable cost (Rs)
    savings_percent: float  # Potential savings
    baseline_alternative: dict[str, Any] | None = None
    optimal_alternative: dict[str, Any] | None = None
    alternatives: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class DesignSuggestions:
    """Design improvement suggestions."""

    total_count: int
    high_impact: int
    medium_impact: int
    low_impact: int
    suggestions: list[dict[str, Any]] = field(default_factory=list)
    top_3: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class SensitivityInsights:
    """Sensitivity and robustness analysis."""

    critical_parameters: list[str]  # Parameters with highest sensitivity
    robustness_score: float  # 0.0-1.0
    robustness_level: str  # "excellent", "good", "fair", "poor"
    sensitivities: list[dict[str, Any]] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


@dataclass
class ConstructabilityInsights:
    """Constructability assessment."""

    score: float  # 0.0-1.0
    level: str  # "excellent", "good", "fair", "poor"
    bar_complexity: str
    congestion_risk: str
    issues: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


@dataclass
class DashboardReport:
    """
    Unified smart design dashboard report.

    Contains all intelligent insights in one structured format:
    - Executive summary
    - Cost optimization
    - Design suggestions
    - Sensitivity analysis
    - Constructability assessment

    Attributes:
        summary: Quick overview of design health
        cost: Cost optimization results (if requested)
        suggestions: Design improvement suggestions (if requested)
        sensitivity: Sensitivity and robustness (if requested)
        constructability: Constructability assessment (if requested)
        design_result: Original design result
        metadata: Analysis metadata (timestamp, version, etc.)
    """

    summary: SmartAnalysisSummary
    design_result: BeamDesignOutput
    metadata: dict[str, Any]
    cost: CostAnalysis | None = None
    suggestions: DesignSuggestions | None = None
    sensitivity: SensitivityInsights | None = None
    constructability: ConstructabilityInsights | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert dashboard to dictionary for JSON serialization."""
        from dataclasses import asdict

        return asdict(self)

    def to_json(self, path: str) -> None:
        """Save dashboard to JSON file."""
        import json
        from pathlib import Path

        data = self.to_dict()
        Path(path).write_text(json.dumps(data, indent=2))

    def summary_text(self) -> str:
        """Generate human-readable summary text."""
        lines = []
        lines.append("=" * 70)
        lines.append("SMART DESIGN DASHBOARD")
        lines.append("=" * 70)
        lines.append("")

        # Summary section
        s = self.summary
        lines.append(f"📊 Overall Score: {s.overall_score:.1%}")
        lines.append(f"   • Safety:          {s.safety_score:.1%}")
        lines.append(f"   • Cost Efficiency: {s.cost_efficiency:.1%}")
        lines.append(f"   • Constructability: {s.constructability:.1%}")
        lines.append(f"   • Robustness:     {s.robustness:.1%}")
        lines.append("")
        lines.append(f"✅ Status: {s.design_status}")
        lines.append("")

        if s.key_issues:
            lines.append("⚠️  Key Issues:")
            for issue in s.key_issues:
                lines.append(f"   • {issue}")
            lines.append("")

        if s.quick_wins:
            lines.append("💡 Quick Wins:")
            for win in s.quick_wins:
                lines.append(f"   • {win}")
            lines.append("")

        # Cost section
        if self.cost:
            c = self.cost
            lines.append("-" * 70)
            lines.append("💰 COST ANALYSIS")
            lines.append("-" * 70)
            lines.append(f"Current Cost:  ₹{c.current_cost:,.0f}")
            lines.append(f"Optimal Cost:  ₹{c.optimal_cost:,.0f}")
            lines.append(f"Savings:       {c.savings_percent:.1f}%")
            lines.append("")

        # Suggestions section
        if self.suggestions:
            sg = self.suggestions
            lines.append("-" * 70)
            lines.append("🔍 DESIGN SUGGESTIONS")
            lines.append("-" * 70)
            lines.append(
                f"Total: {sg.total_count} | High: {sg.high_impact} | "
                f"Medium: {sg.medium_impact} | Low: {sg.low_impact}"
            )
            lines.append("")
            if sg.top_3:
                lines.append("Top 3 Recommendations:")
                for i, sug in enumerate(sg.top_3, 1):
                    lines.append(
                        f"{i}. [{sug.get('impact', 'MEDIUM')}] {sug.get('category', 'general')}"
                    )
                    lines.append(f"   {sug.get('message', '')}")
                lines.append("")

        # Sensitivity section
        if self.sensitivity:
            sens = self.sensitivity
            lines.append("-" * 70)
            lines.append("📈 SENSITIVITY ANALYSIS")
            lines.append("-" * 70)
            lines.append(
                f"Robustness: {sens.robustness_score:.1%} ({sens.robustness_level})"
            )
            if sens.critical_parameters:
                lines.append("Critical Parameters:")
                for param in sens.critical_parameters[:3]:
                    lines.append(f"   • {param}")
            lines.append("")

        # Constructability section
        if self.constructability:
            cons = self.constructability
            lines.append("-" * 70)
            lines.append("🏗️  CONSTRUCTABILITY")
            lines.append("-" * 70)
            lines.append(f"Score: {cons.score:.1%} ({cons.level})")
            lines.append(f"Bar Complexity: {cons.bar_complexity}")
            lines.append(f"Congestion Risk: {cons.congestion_risk}")
            if cons.issues:
                lines.append("Issues:")
                for issue in cons.issues[:3]:
                    lines.append(f"   • {issue}")
            lines.append("")

        lines.append("=" * 70)
        return "\n".join(lines)


class SmartDesigner:
    """
    Unified intelligent design analyzer.

    Provides comprehensive design analysis by integrating:
    - Cost optimization
    - Design suggestions
    - Sensitivity analysis
    - Constructability scoring

    Example:
        >>> dashboard = SmartDesigner.analyze(
        ...     design=result,
        ...     span_mm=5000,
        ...     mu_knm=120,
        ...     vu_kn=80
        ... )
        >>> print(dashboard.summary_text())
        >>> dashboard.to_json("analysis.json")
    """

    @staticmethod
    def analyze(
        *,
        design: BeamDesignOutput,
        span_mm: float,
        mu_knm: float,
        vu_kn: float,
        include_cost: bool = True,
        include_suggestions: bool = True,
        include_sensitivity: bool = True,
        include_constructability: bool = True,
        cost_profile: CostProfile | None = None,
        weights: dict[str, float] | None = None,
    ) -> DashboardReport:
        """
        Perform comprehensive smart design analysis.

        Args:
            design: Design result from design_beam_is456
            span_mm: Beam span in mm
            mu_knm: Design moment in kN·m
            vu_kn: Design shear in kN
            include_cost: Include cost optimization (default: True)
            include_suggestions: Include design suggestions (default: True)
            include_sensitivity: Include sensitivity analysis (default: True)
            include_constructability: Include constructability (default: True)
            cost_profile: Custom cost profile (default: use library defaults)
            weights: Custom weights for overall score (default: equal weights)

        Returns:
            DashboardReport with all requested analyses

        Raises:
            ValueError: If design result is invalid
        """
        import time
        from datetime import datetime

        from ..api import get_library_version

        # Validate inputs
        if not design or not design.is_ok:
            raise ValueError("Design must be a valid passing design result")

        # Default weights
        if weights is None:
            weights = {
                "safety": 0.3,
                "cost": 0.25,
                "constructability": 0.25,
                "robustness": 0.2,
            }

        # Default cost profile
        if cost_profile is None:
            cost_profile = CostProfile()

        start_time = time.time()

        # Cost optimization analysis
        cost_analysis = None
        if include_cost:
            cost_result = cost_optimization.optimize_beam_cost(
                span_mm=span_mm,
                mu_knm=mu_knm,
                vu_kn=vu_kn,
                cost_profile=cost_profile,
            )

            # Extract current design parameters
            b_mm = design.geometry.b_mm
            D_mm = design.geometry.D_mm
            fck_nmm2 = design.materials.fck_nmm2

            # Estimate current cost
            from .comparison import _estimate_design_cost

            current_params = {
                "b_mm": b_mm,
                "D_mm": D_mm,
                "fck_nmm2": fck_nmm2,
            }
            current_cost = _estimate_design_cost(current_params, cost_profile, span_mm)

            cost_analysis = CostAnalysis(
                current_cost=current_cost,
                optimal_cost=(
                    cost_result.optimal_candidate.cost_breakdown.total_cost
                    if cost_result.optimal_candidate.cost_breakdown
                    else 0.0
                ),
                savings_percent=cost_result.savings_percent,
                baseline_alternative=None,  # Not in CostOptimizationResult
                optimal_alternative=None,  # Not in CostOptimizationResult
                alternatives=[],  # Simplified for now
            )

        # Design suggestions
        suggestions_analysis = None
        if include_suggestions:
            sug_result = design_suggestions.suggest_improvements(
                design=design,
                span_mm=span_mm,
                mu_knm=mu_knm,
                vu_kn=vu_kn,
            )

            suggestions_list = sug_result.suggestions
            high = sum(1 for s in suggestions_list if s.impact.value == "high")
            medium = sum(1 for s in suggestions_list if s.impact.value == "medium")
            low = sum(1 for s in suggestions_list if s.impact.value == "low")

            # Convert to dict format
            suggestions_dicts = [
                {
                    "category": (
                        s.category.value if hasattr(s.category, "value") else s.category
                    ),
                    "impact": (
                        s.impact.value if hasattr(s.impact, "value") else s.impact
                    ),
                    "title": s.title,
                    "description": s.description,
                    "rationale": s.rationale,
                    "estimated_benefit": s.estimated_benefit,
                    "action_steps": s.action_steps,
                }
                for s in suggestions_list
            ]

            suggestions_analysis = DesignSuggestions(
                total_count=len(suggestions_list),
                high_impact=high,
                medium_impact=medium,
                low_impact=low,
                suggestions=suggestions_dicts,
                top_3=suggestions_dicts[:3],
            )

        # Sensitivity analysis
        sensitivity_analysis = None
        if include_sensitivity:
            # Need a design function for sensitivity analysis
            from ..api import design_beam_is456

            # Extract parameters for sensitivity
            base_params = {
                "units": "IS456",
                "b_mm": design.geometry.b_mm,
                "D_mm": design.geometry.D_mm,
                "d_mm": design.geometry.d_mm,
                "fck_nmm2": design.materials.fck_nmm2,
                "fy_nmm2": design.materials.fy_nmm2,
                "mu_knm": mu_knm,
                "vu_kn": vu_kn,
            }

            sens_results, robust_score = sensitivity.sensitivity_analysis(
                design_beam_is456, base_params
            )

            # Identify critical parameters (top 3 by sensitivity)
            sorted_sens = sorted(
                sens_results, key=lambda x: abs(x.sensitivity), reverse=True
            )
            critical = [s.parameter for s in sorted_sens[:3]]

            # Generate recommendations
            recommendations = []
            for s in sorted_sens[:3]:
                if abs(s.sensitivity) > 0.3:
                    recommendations.append(
                        f"Tight control needed for {s.parameter} "
                        f"(sensitivity: {s.sensitivity:.2f})"
                    )

            sensitivity_analysis = SensitivityInsights(
                critical_parameters=critical,
                robustness_score=robust_score.score,
                robustness_level=robust_score.rating,
                sensitivities=[
                    {
                        "parameter": s.parameter,
                        "sensitivity": s.sensitivity,
                        "impact": s.impact,
                    }
                    for s in sens_results
                ],
                recommendations=recommendations,
            )

        # Constructability assessment
        constructability_analysis = None
        if include_constructability:
            # Need detailing for constructability - simplified without actual detailing
            # In real usage, detailing would be computed first
            # For now, estimate based on design parameters

            b_mm = design.geometry.b_mm
            ast_mm2 = design.flexure.ast_required_mm2
            steel_pt = (ast_mm2 / (b_mm * design.geometry.d_mm)) * 100

            # Simple heuristics
            if steel_pt > 2.0:
                level = "poor"
                bar_complexity = "high"
                congestion_risk = "high"
                issues = [
                    "High steel percentage (>2%)",
                    "Congestion risk at supports",
                    "Difficult bar placement",
                ]
                recs = [
                    "Consider increasing section depth",
                    "Use higher grade concrete",
                    "Review support detailing",
                ]
                score = 0.4
            elif steel_pt > 1.5:
                level = "fair"
                bar_complexity = "medium"
                congestion_risk = "medium"
                issues = ["Moderate steel congestion"]
                recs = ["Monitor bar spacing at supports"]
                score = 0.6
            elif steel_pt > 1.0:
                level = "good"
                bar_complexity = "low"
                congestion_risk = "low"
                issues = []
                recs = []
                score = 0.8
            else:
                level = "excellent"
                bar_complexity = "very low"
                congestion_risk = "very low"
                issues = []
                recs = []
                score = 1.0

            constructability_analysis = ConstructabilityInsights(
                score=score,
                level=level,
                bar_complexity=bar_complexity,
                congestion_risk=congestion_risk,
                issues=issues,
                recommendations=recs,
            )

        # Calculate overall scores
        safety_score = (
            min(design.governing_utilization, 1.0)
            if design.governing_utilization > 0
            else 1.0
        )
        cost_efficiency = (
            1.0 - (cost_analysis.savings_percent / 100.0) if cost_analysis else 0.8
        )
        constructability_score = (
            constructability_analysis.score if constructability_analysis else 0.75
        )
        robustness_score = (
            sensitivity_analysis.robustness_score if sensitivity_analysis else 0.7
        )

        overall_score = (
            weights["safety"] * safety_score
            + weights["cost"] * cost_efficiency
            + weights["constructability"] * constructability_score
            + weights["robustness"] * robustness_score
        )

        # Identify key issues and quick wins
        key_issues = []
        quick_wins = []

        if safety_score < 0.7:
            key_issues.append("Low safety margin - review design")
        if cost_analysis and cost_analysis.savings_percent > 15:
            quick_wins.append(
                f"Potential {cost_analysis.savings_percent:.0f}% cost savings"
            )
        if suggestions_analysis and suggestions_analysis.high_impact > 0:
            quick_wins.append(
                f"{suggestions_analysis.high_impact} high-impact improvements available"
            )
        if constructability_score < 0.6:
            key_issues.append("Constructability concerns - congestion risk")

        # Design status
        if design.is_ok and safety_score > 0.8:
            status = "PASS"
        elif design.is_ok:
            status = "WARNING"
        else:
            status = "FAIL"

        # Create summary
        summary = SmartAnalysisSummary(
            design_status=status,
            safety_score=safety_score,
            cost_efficiency=cost_efficiency,
            constructability=constructability_score,
            robustness=robustness_score,
            overall_score=overall_score,
            key_issues=key_issues,
            quick_wins=quick_wins,
        )

        # Metadata
        elapsed = time.time() - start_time
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "library_version": get_library_version(),
            "analysis_time_ms": round(elapsed * 1000, 1),
            "included_analyses": {
                "cost": include_cost,
                "suggestions": include_suggestions,
                "sensitivity": include_sensitivity,
                "constructability": include_constructability,
            },
            "weights": weights,
        }

        return DashboardReport(
            summary=summary,
            design_result=design,
            metadata=metadata,
            cost=cost_analysis,
            suggestions=suggestions_analysis,
            sensitivity=sensitivity_analysis,
            constructability=constructability_analysis,
        )


def quick_analysis(
    design: BeamDesignOutput,
    span_mm: float,
    mu_knm: float,
    vu_kn: float,
) -> str:
    """
    Quick text-based smart analysis (simplified).

    Args:
        design: Design result
        span_mm: Span in mm
        mu_knm: Moment in kN·m
        vu_kn: Shear in kN

    Returns:
        Human-readable analysis text
    """
    dashboard = SmartDesigner.analyze(
        design=design,
        span_mm=span_mm,
        mu_knm=mu_knm,
        vu_kn=vu_kn,
        include_cost=True,
        include_suggestions=True,
        include_sensitivity=False,  # Skip for quick analysis
        include_constructability=False,
    )

    return dashboard.summary_text()
