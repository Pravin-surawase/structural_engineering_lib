# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Design suggestion engine for beam design optimization.

This module provides rule-based expert guidance to improve beam designs
beyond basic code compliance. Suggestions focus on:
- Cost optimization
- Constructability improvements
- Steel congestion reduction
- Serviceability enhancements
- Material efficiency
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

from ..beam_pipeline import BeamDesignOutput
from ..costing import CostProfile
from ..detailing import BeamDetailingResult


class SuggestionCategory(Enum):
    """Categories of design suggestions."""

    GEOMETRY = "geometry"
    STEEL = "steel"
    COST = "cost"
    CONSTRUCTABILITY = "constructability"
    SERVICEABILITY = "serviceability"
    MATERIALS = "materials"


class ImpactLevel(Enum):
    """Impact level of a suggestion."""

    LOW = "low"  # <5% improvement
    MEDIUM = "medium"  # 5-15% improvement
    HIGH = "high"  # >15% improvement


@dataclass(frozen=True)
class DesignSuggestion:
    """A single design improvement suggestion."""

    category: SuggestionCategory
    impact: ImpactLevel
    confidence: float  # 0.0-1.0
    title: str
    description: str
    rationale: str
    estimated_benefit: str  # e.g., "12% cost reduction", "+15% constructability"
    action_steps: list[str]
    rule_id: str
    priority_score: float  # Combined metric for sorting

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "category": self.category.value,
            "impact": self.impact.value,
            "confidence": self.confidence,
            "title": self.title,
            "description": self.description,
            "rationale": self.rationale,
            "estimated_benefit": self.estimated_benefit,
            "action_steps": self.action_steps,
            "rule_id": self.rule_id,
            "priority_score": self.priority_score,
        }


@dataclass(frozen=True)
class SuggestionReport:
    """Complete set of design suggestions."""

    suggestions: list[DesignSuggestion]
    analysis_time_ms: float
    suggestions_count: int
    high_impact_count: int
    medium_impact_count: int
    low_impact_count: int
    engine_version: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "suggestions": [s.to_dict() for s in self.suggestions],
            "analysis_time_ms": self.analysis_time_ms,
            "suggestions_count": self.suggestions_count,
            "high_impact_count": self.high_impact_count,
            "medium_impact_count": self.medium_impact_count,
            "low_impact_count": self.low_impact_count,
            "engine_version": self.engine_version,
        }


_ENGINE_VERSION = "1.0.0"


def suggest_improvements(
    design: BeamDesignOutput,
    detailing: BeamDetailingResult | None = None,
    cost_profile: CostProfile | None = None,
    span_mm: float | None = None,
    mu_knm: float | None = None,
    vu_kn: float | None = None,
) -> SuggestionReport:
    """Generate design improvement suggestions.

    Analyzes a completed beam design and provides actionable recommendations
    to improve cost, constructability, and performance.

    Args:
        design: Completed beam design output
        detailing: Optional detailing result (enables constructability rules)
        cost_profile: Regional cost data for optimization suggestions
        span_mm: Beam span (enables serviceability rules)
        mu_knm: Factored moment (enables optimization suggestions)
        vu_kn: Factored shear (enables optimization suggestions)

    Returns:
        SuggestionReport with prioritized improvements

    Example:
        >>> from structural_lib.api import design_beam_is456
        >>> design = design_beam_is456(...)
        >>> suggestions = suggest_improvements(design, span_mm=5000, mu_knm=120)
        >>> for s in suggestions.suggestions[:3]:  # Top 3 suggestions
        ...     print(f"{s.title} ({s.impact.value}) - {s.estimated_benefit}")
    """
    start_time = time.time()
    suggestions: list[DesignSuggestion] = []

    # Extract design parameters
    b_mm = design.geometry.b_mm
    D_mm = design.geometry.D_mm
    d_mm = design.geometry.d_mm
    fck_nmm2 = design.materials.fck_nmm2
    fy_nmm2 = design.materials.fy_nmm2

    # Extract design results
    flexure = design.flexure
    shear = design.shear

    # Run all suggestion rules
    suggestions.extend(_check_geometry_rules(b_mm, D_mm, d_mm, span_mm, flexure))
    suggestions.extend(_check_steel_rules(flexure, shear, b_mm, d_mm, fy_nmm2))
    suggestions.extend(_check_cost_rules(design, cost_profile, span_mm, mu_knm, vu_kn))

    if detailing:
        suggestions.extend(_check_constructability_rules(detailing, b_mm, d_mm))

    suggestions.extend(_check_serviceability_rules(span_mm, d_mm, flexure, design))
    suggestions.extend(_check_materials_rules(fck_nmm2, fy_nmm2, flexure, shear))

    # Sort by priority score (descending)
    suggestions.sort(key=lambda s: s.priority_score, reverse=True)

    # Count by impact
    high_count = sum(1 for s in suggestions if s.impact == ImpactLevel.HIGH)
    medium_count = sum(1 for s in suggestions if s.impact == ImpactLevel.MEDIUM)
    low_count = sum(1 for s in suggestions if s.impact == ImpactLevel.LOW)

    elapsed_ms = (time.time() - start_time) * 1000

    return SuggestionReport(
        suggestions=suggestions,
        analysis_time_ms=elapsed_ms,
        suggestions_count=len(suggestions),
        high_impact_count=high_count,
        medium_impact_count=medium_count,
        low_impact_count=low_count,
        engine_version=_ENGINE_VERSION,
    )


def _check_geometry_rules(
    b_mm: float,
    D_mm: float,
    d_mm: float,
    span_mm: float | None,
    flexure: Any,
) -> list[DesignSuggestion]:
    """Check geometry-related improvement opportunities."""
    suggestions = []

    # Rule G1: Oversized section (low utilization)
    if flexure and hasattr(flexure, "utilization"):
        utilization = flexure.utilization
        if utilization < 0.5:
            savings_estimate = int((1 - utilization) * 30)  # Rough estimate
            suggestions.append(
                DesignSuggestion(
                    category=SuggestionCategory.GEOMETRY,
                    impact=ImpactLevel.HIGH,
                    confidence=0.85,
                    title="Reduce section size",
                    description=f"Section is oversized (utilization: {utilization:.1%})",
                    rationale=(
                        "Low moment utilization indicates excessive concrete. "
                        "Smaller section reduces material cost and self-weight."
                    ),
                    estimated_benefit=f"~{savings_estimate}% cost reduction",
                    action_steps=[
                        f"Try reducing depth by {int((1-utilization)*D_mm*0.3)}mm",
                        "Re-run design with smaller section",
                        "Verify serviceability limits",
                    ],
                    rule_id="G1",
                    priority_score=9.0,
                )
            )

    # Rule G2: Non-standard width
    standard_widths = [230, 300, 400, 500]
    if b_mm not in standard_widths:
        nearest = min(standard_widths, key=lambda x: abs(x - b_mm))
        suggestions.append(
            DesignSuggestion(
                category=SuggestionCategory.GEOMETRY,
                impact=ImpactLevel.LOW,
                confidence=0.90,
                title="Use standard beam width",
                description=f"Current width {b_mm}mm is non-standard",
                rationale=(
                    "Standard widths (230, 300, 400, 500mm) are easier to form "
                    "and align with typical column dimensions."
                ),
                estimated_benefit="+5% constructability",
                action_steps=[
                    f"Change width to {nearest}mm",
                    "Verify steel arrangement still fits",
                ],
                rule_id="G2",
                priority_score=3.5,
            )
        )

    # Rule G3: Depth not in 50mm increments
    if D_mm % 50 != 0:
        next_50 = int((D_mm + 25) // 50 * 50)
        suggestions.append(
            DesignSuggestion(
                category=SuggestionCategory.GEOMETRY,
                impact=ImpactLevel.LOW,
                confidence=0.95,
                title="Round depth to 50mm increment",
                description=f"Current depth {D_mm}mm not in standard increments",
                rationale="Depths in 50mm steps simplify formwork and reduce errors.",
                estimated_benefit="+3% constructability",
                action_steps=[f"Round depth to {next_50}mm"],
                rule_id="G3",
                priority_score=2.0,
            )
        )

    # Rule G4: Excessive depth-to-width ratio
    if b_mm > 0 and D_mm / b_mm > 4.0:
        suggestions.append(
            DesignSuggestion(
                category=SuggestionCategory.GEOMETRY,
                impact=ImpactLevel.MEDIUM,
                confidence=0.75,
                title="Increase beam width for stability",
                description=f"Depth/width ratio {D_mm/b_mm:.1f} is very high",
                rationale=(
                    "Deep narrow beams have lateral stability issues and "
                    "require additional bracing during construction. "
                    "IS 456:2000 doesn't mandate D/b limits, but practical "
                    "range is 2.0-3.5 for lateral stability."
                ),
                estimated_benefit="+10% constructability",
                action_steps=[
                    f"Consider increasing width to {int(D_mm/3)}mm minimum",
                    "Verify lateral stability",
                ],
                rule_id="G4",
                priority_score=6.0,
            )
        )

    # Rule G5: Shallow beam for span
    if span_mm and span_mm > 0 and d_mm / span_mm < 0.05:
        min_d = int(span_mm * 0.06)
        suggestions.append(
            DesignSuggestion(
                category=SuggestionCategory.GEOMETRY,
                impact=ImpactLevel.HIGH,
                confidence=0.80,
                title="Increase depth for span",
                description=f"Depth/span ratio {d_mm/span_mm:.3f} is very low",
                rationale=(
                    "Shallow beams relative to span will likely fail deflection "
                    "checks and require excessive reinforcement. "
                    "IS 456:2000 Cl 23.2.1 provides span/depth ratios: "
                    "simply supported beams typically need d ≥ span/20."
                ),
                estimated_benefit="+20% serviceability margin",
                action_steps=[
                    f"Increase effective depth to at least {min_d}mm",
                    "Target d/span ≥ 0.06 for simply supported beams",
                ],
                rule_id="G5",
                priority_score=8.5,
            )
        )

    return suggestions


def _check_steel_rules(
    flexure: Any, shear: Any, b_mm: float, d_mm: float, fy_nmm2: float
) -> list[DesignSuggestion]:
    """Check steel-related improvement opportunities."""
    suggestions = []

    # Rule S1: High steel percentage (congestion risk)
    if flexure and hasattr(flexure, "ast_required_mm2"):
        ast_req = flexure.ast_required_mm2
        if ast_req > 0 and b_mm > 0 and d_mm > 0:
            pt = (ast_req / (b_mm * d_mm)) * 100
            if pt > 2.5:
                suggestions.append(
                    DesignSuggestion(
                        category=SuggestionCategory.STEEL,
                        impact=ImpactLevel.HIGH,
                        confidence=0.90,
                        title="Reduce steel congestion",
                        description=f"Steel percentage {pt:.2f}% exceeds comfortable limit",
                        rationale=(
                            "High steel % (>2.5%) makes bar placement difficult "
                            "and increases concrete compaction issues. "
                            "IS 456:2000 Cl 26.5.1.1 limits max reinforcement to 4% "
                            "but practical limit is 2.5% for constructability."
                        ),
                        estimated_benefit="+25% constructability",
                        action_steps=[
                            "Increase section depth by 50-100mm",
                            "Consider compression reinforcement",
                            "Verify spacing requirements",
                        ],
                        rule_id="S1",
                        priority_score=9.5,
                    )
                )

    # Rule S2: Very low steel percentage (deflection risk)
    if flexure and hasattr(flexure, "ast_required_mm2"):
        ast_req = flexure.ast_required_mm2
        if ast_req > 0 and b_mm > 0 and d_mm > 0:
            pt = (ast_req / (b_mm * d_mm)) * 100
            if pt < 0.3:
                suggestions.append(
                    DesignSuggestion(
                        category=SuggestionCategory.STEEL,
                        impact=ImpactLevel.MEDIUM,
                        confidence=0.75,
                        title="Consider minimum steel for deflection",
                        description=f"Very low steel percentage ({pt:.2f}%)",
                        rationale=(
                            "Very low steel may lead to excessive deflection even if "
                            "code minimums are met. IS 456:2000 Cl 26.5.1.1 requires "
                            "min 0.85% (Fe 250) but typical practice uses ≥0.5% for "
                            "deflection control."
                        ),
                        estimated_benefit="+15% serviceability",
                        action_steps=[
                            "Verify deflection with actual steel provided",
                            "Consider using Fe 415 instead of Fe 500",
                        ],
                        rule_id="S2",
                        priority_score=5.0,
                    )
                )

    # Rule S3: Higher grade steel available
    if fy_nmm2 == 415:
        suggestions.append(
            DesignSuggestion(
                category=SuggestionCategory.STEEL,
                impact=ImpactLevel.MEDIUM,
                confidence=0.80,
                title="Use Fe 500 steel for efficiency",
                description="Currently using Fe 415",
                rationale=(
                    "Fe 500 steel reduces required area by ~17% and is "
                    "widely available in modern construction. "
                    "IS 456:2000 Annex B covers Fe 415, Fe 500 grades. "
                    "Higher grade improves economy without compromising safety."
                ),
                estimated_benefit="~10% steel cost reduction",
                action_steps=[
                    "Switch material grade to Fe 500",
                    "Re-run design",
                    "Verify local availability",
                ],
                rule_id="S3",
                priority_score=6.5,
            )
        )

    # Rule S4: Stirrup spacing can be optimized
    if shear and hasattr(shear, "sv_required_mm"):
        sv = shear.sv_required_mm
        if sv and sv < 100:
            suggestions.append(
                DesignSuggestion(
                    category=SuggestionCategory.STEEL,
                    impact=ImpactLevel.LOW,
                    confidence=0.70,
                    title="Very close stirrup spacing",
                    description=f"Stirrup spacing {sv}mm is very tight",
                    rationale=(
                        "Stirrup spacing < 100mm is difficult to achieve "
                        "and increases labor costs significantly. "
                        "IS 456:2000 Cl 26.5.1.5 sets min spacing (0.75d, 300mm) "
                        "but practical limit is ~100mm for good concrete flow."
                    ),
                    estimated_benefit="+8% labor efficiency",
                    action_steps=[
                        "Consider increasing stirrup diameter",
                        "Use 4-legged stirrups if space permits",
                        "Increase section depth to reduce shear stress",
                    ],
                    rule_id="S4",
                    priority_score=4.0,
                )
            )

    return suggestions


def _check_cost_rules(
    design: BeamDesignOutput,
    cost_profile: CostProfile | None,
    span_mm: float | None,
    mu_knm: float | None,
    vu_kn: float | None,
) -> list[DesignSuggestion]:
    """Check cost optimization opportunities."""
    suggestions = []

    # Rule C1: Run cost optimization if parameters available
    if span_mm and mu_knm and vu_kn and span_mm > 0:
        # Only suggest if section seems conservative (not already optimized)
        flexure = design.flexure
        if flexure and hasattr(flexure, "utilization"):
            utilization = flexure.utilization
            if utilization < 0.7:  # Not well-utilized
                suggestions.append(
                    DesignSuggestion(
                        category=SuggestionCategory.COST,
                        impact=ImpactLevel.HIGH,
                        confidence=0.85,
                        title="Explore cost-optimized designs",
                        description="Current design may not be cost-optimal",
                        rationale=(
                            "Cost optimization algorithm can find cheaper "
                            "section with same safety."
                        ),
                        estimated_benefit="8-20% cost reduction typical",
                        action_steps=[
                            "Run optimize_beam_cost() function",
                            "Compare with current design",
                            "Verify serviceability of optimal design",
                        ],
                        rule_id="C1",
                        priority_score=9.0,
                    )
                )

    # Rule C2: Concrete grade optimization
    fck = design.materials.fck_nmm2
    if fck > 30:
        suggestions.append(
            DesignSuggestion(
                category=SuggestionCategory.COST,
                impact=ImpactLevel.MEDIUM,
                confidence=0.70,
                title="Consider lower concrete grade",
                description=f"Using M{fck} concrete",
                rationale=(
                    "Higher grades cost more and require stricter QC. "
                    "M25-M30 are most economical for typical beams."
                ),
                estimated_benefit="~5% concrete cost reduction",
                action_steps=[
                    "Try M25 or M30 grade",
                    "Verify section is adequate",
                ],
                rule_id="C2",
                priority_score=5.5,
            )
        )

    return suggestions


def _check_constructability_rules(
    detailing: BeamDetailingResult, b_mm: float, d_mm: float
) -> list[DesignSuggestion]:
    """Check constructability improvement opportunities."""
    suggestions = []

    # Rule CT1: Excessive bar count
    if hasattr(detailing, "main_steel") and detailing.main_steel:
        for location, bars in [
            ("bottom", detailing.main_steel.get("bottom")),
            ("top", detailing.main_steel.get("top")),
        ]:
            if bars and hasattr(bars, "count"):
                n = bars.count
                if n > 6:
                    suggestions.append(
                        DesignSuggestion(
                            category=SuggestionCategory.CONSTRUCTABILITY,
                            impact=ImpactLevel.MEDIUM,
                            confidence=0.80,
                            title=f"Reduce {location} bar count",
                            description=f"{n} bars at {location} is excessive",
                            rationale=(
                                "More than 6 bars in single layer increases "
                                "congestion and placement errors. "
                                "IS 456:2000 Cl 26.3 requires clear spacing ≥max(bar dia, 25mm), "
                                "limiting practical bar count in typical widths."
                            ),
                            estimated_benefit="+12% placement efficiency",
                            action_steps=[
                                "Use larger diameter bars",
                                "Consider 2-layer arrangement",
                            ],
                            rule_id="CT1",
                            priority_score=6.0,
                        )
                    )

    # Rule CT2: Mixed bar diameters
    if hasattr(detailing, "main_steel") and detailing.main_steel:
        diameters = set()
        for bars in detailing.main_steel.values():
            if bars and hasattr(bars, "diameter"):
                diameters.add(bars.diameter)
        if len(diameters) > 2:
            suggestions.append(
                DesignSuggestion(
                    category=SuggestionCategory.CONSTRUCTABILITY,
                    impact=ImpactLevel.LOW,
                    confidence=0.75,
                    title="Standardize bar diameters",
                    description=f"Using {len(diameters)} different diameters",
                    rationale=(
                        "Multiple bar sizes increase procurement complexity "
                        "and on-site confusion."
                    ),
                    estimated_benefit="+5% procurement efficiency",
                    action_steps=[
                        "Limit to 2 bar sizes maximum",
                        "Use 16mm, 20mm as primary sizes",
                    ],
                    rule_id="CT2",
                    priority_score=3.0,
                )
            )

    return suggestions


def _check_serviceability_rules(
    span_mm: float | None, d_mm: float, flexure: Any, design: BeamDesignOutput
) -> list[DesignSuggestion]:
    """Check serviceability improvement opportunities."""
    suggestions = []

    # Rule SV1: Span-depth ratio approaching limits
    if span_mm and span_mm > 0:
        ld_ratio = span_mm / d_mm
        # Typical limit for simply supported: 20
        if 18 < ld_ratio <= 20:
            suggestions.append(
                DesignSuggestion(
                    category=SuggestionCategory.SERVICEABILITY,
                    impact=ImpactLevel.MEDIUM,
                    confidence=0.80,
                    title="Increase depth for deflection comfort",
                    description=f"L/d ratio {ld_ratio:.1f} is near code limit",
                    rationale=(
                        "While code-compliant, ratios near limits may show "
                        "visible deflection or require modification factors. "
                        "IS 456:2000 Cl 23.2.1 allows L/d = 20 for simply supported "
                        "beams but recommends lower ratios for visible comfort."
                    ),
                    estimated_benefit="+20% deflection margin",
                    action_steps=[
                        "Increase depth by 50mm",
                        "Provides comfort margin for long-term deflection",
                    ],
                    rule_id="SV1",
                    priority_score=6.0,
                )
            )

    # Rule SV2: Check crack width if serviceability not run
    if not hasattr(design, "serviceability") or design.serviceability is None:
        suggestions.append(
            DesignSuggestion(
                category=SuggestionCategory.SERVICEABILITY,
                impact=ImpactLevel.LOW,
                confidence=0.60,
                title="Run serviceability checks",
                description="Deflection and crack width not verified",
                rationale=(
                    "Code compliance requires both deflection and crack width "
                    "checks for critical exposure conditions. "
                    "IS 456:2000 Cl 23.2 (deflection) and Cl 35.3.2 (crack width) "
                    "mandate serviceability verification for durability."
                ),
                estimated_benefit="+Full code compliance",
                action_steps=[
                    "Run deflection check with fs calculation",
                    "Run crack width check for exposure class",
                ],
                rule_id="SV2",
                priority_score=4.5,
            )
        )

    return suggestions


def _check_materials_rules(
    fck_nmm2: float, fy_nmm2: float, flexure: Any, shear: Any
) -> list[DesignSuggestion]:
    """Check materials-related improvement opportunities."""
    suggestions = []

    # Rule M1: Using uncommon concrete grade
    common_grades = [20, 25, 30, 35]
    if fck_nmm2 not in common_grades:
        nearest = min(common_grades, key=lambda x: abs(x - fck_nmm2))
        suggestions.append(
            DesignSuggestion(
                category=SuggestionCategory.MATERIALS,
                impact=ImpactLevel.LOW,
                confidence=0.70,
                title="Use standard concrete grade",
                description=f"M{fck_nmm2} is uncommon",
                rationale=(
                    "Standard grades (M20, M25, M30) have better quality control "
                    "and availability."
                ),
                estimated_benefit="+5% QC reliability",
                action_steps=[f"Switch to M{nearest}"],
                rule_id="M1",
                priority_score=2.5,
            )
        )

    # Rule M2: Material cost vs strength trade-off
    if fck_nmm2 == 20 and flexure and hasattr(flexure, "ast_required_mm2"):
        suggestions.append(
            DesignSuggestion(
                category=SuggestionCategory.MATERIALS,
                impact=ImpactLevel.MEDIUM,
                confidence=0.65,
                title="Consider M25 for better balance",
                description="M20 requires more steel",
                rationale=(
                    "M25 concrete costs ~8% more but reduces steel by ~15%, "
                    "often resulting in net savings."
                ),
                estimated_benefit="~5-8% total cost reduction",
                action_steps=[
                    "Re-run design with M25",
                    "Compare total material cost",
                ],
                rule_id="M2",
                priority_score=6.0,
            )
        )

    return suggestions
