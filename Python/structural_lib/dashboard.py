# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Insights module for dashboard aggregation and live code checks.

This module provides high-level wrappers around the library's design,
compliance, and optimization functions for convenient UI consumption.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DashboardSummary:
    """Aggregated summary for a batch of design results."""

    total_beams: int = 0
    passed: int = 0
    failed: int = 0
    warnings_count: int = 0
    avg_utilization: float = 0.0
    max_utilization: float = 0.0
    min_utilization: float = float("inf")
    total_steel_kg: float = 0.0
    total_concrete_m3: float = 0.0
    critical_beams: list[str] = field(default_factory=list)
    by_story: dict[str, dict[str, int]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_beams": self.total_beams,
            "passed": self.passed,
            "failed": self.failed,
            "warnings_count": self.warnings_count,
            "pass_rate": round(self.passed / max(self.total_beams, 1) * 100, 1),
            "avg_utilization": round(self.avg_utilization, 2),
            "max_utilization": round(self.max_utilization, 2),
            "min_utilization": (
                round(self.min_utilization, 2)
                if self.min_utilization != float("inf")
                else 0.0
            ),
            "total_steel_kg": round(self.total_steel_kg, 1),
            "total_concrete_m3": round(self.total_concrete_m3, 3),
            "critical_beams": self.critical_beams[:10],
            "by_story": self.by_story,
        }


@dataclass
class CodeCheckResult:
    """Result of a fast IS 456 code check."""

    passed: bool
    checks: list[dict[str, Any]] = field(default_factory=list)
    critical_failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    utilization: float = 0.0
    governing_check: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "checks": self.checks,
            "critical_failures": self.critical_failures,
            "warnings": self.warnings,
            "utilization": round(self.utilization, 2),
            "governing_check": self.governing_check,
        }


@dataclass
class RebarSuggestion:
    """A single rebar optimization suggestion."""

    id: str
    title: str
    description: str
    impact: str  # LOW, MEDIUM, HIGH
    savings_percent: float = 0.0
    suggested_config: dict[str, Any] = field(default_factory=dict)
    rationale: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "impact": self.impact,
            "savings_percent": round(self.savings_percent, 1),
            "suggested_config": self.suggested_config,
            "rationale": self.rationale,
        }


@dataclass
class RebarSuggestionsResult:
    """Collection of rebar suggestions for a beam."""

    beam_id: str
    suggestions: list[RebarSuggestion] = field(default_factory=list)
    current_ast_mm2: float = 0.0
    min_ast_mm2: float = 0.0
    max_savings_percent: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "beam_id": self.beam_id,
            "suggestions": [s.to_dict() for s in self.suggestions],
            "suggestion_count": len(self.suggestions),
            "current_ast_mm2": round(self.current_ast_mm2, 1),
            "min_ast_mm2": round(self.min_ast_mm2, 1),
            "max_savings_percent": round(self.max_savings_percent, 1),
        }


def _safe_get(obj: Any, keys: list[str], default: Any = None) -> Any:
    """Safely extract a value from an object using multiple possible keys."""
    if isinstance(obj, dict):
        for key in keys:
            if key in obj and obj[key] is not None:
                return obj[key]
        return default
    for key in keys:
        if hasattr(obj, key) and getattr(obj, key, None) is not None:
            return getattr(obj, key)
    return default


def generate_dashboard(
    design_results: Sequence[Mapping[str, Any]],
) -> DashboardSummary:
    """Generate an aggregated dashboard summary from multiple design results.

    Args:
        design_results: List of design result dictionaries or objects.
            Each should have beam_id, is_valid, utilization, story, etc.

    Returns:
        DashboardSummary with aggregated statistics.

    Example:
        >>> results = [design_beam_1, design_beam_2, ...]
        >>> dashboard = generate_dashboard(results)
        >>> print(f"Pass rate: {dashboard.to_dict()['pass_rate']}%")
    """
    summary = DashboardSummary()
    utilizations: list[float] = []

    for result in design_results:
        summary.total_beams += 1

        is_valid = _safe_get(result, ["is_valid", "valid", "success"], True)
        utilization = _safe_get(result, ["utilization", "util"], 0.0)
        beam_id = _safe_get(
            result, ["beam_id", "id", "name"], f"beam_{summary.total_beams}"
        )
        story = _safe_get(result, ["story", "floor", "level"], "Unknown")

        if is_valid:
            summary.passed += 1
        else:
            summary.failed += 1

        # Track utilization
        if isinstance(utilization, (int, float)) and utilization > 0:
            utilizations.append(float(utilization))
            summary.max_utilization = max(summary.max_utilization, float(utilization))
            summary.min_utilization = min(summary.min_utilization, float(utilization))

        # Critical beams (utilization > 0.95 or failed)
        if not is_valid or (
            isinstance(utilization, (int, float)) and utilization > 0.95
        ):
            summary.critical_beams.append(str(beam_id))

        # Warnings
        warnings = _safe_get(result, ["warnings", "remarks"], [])
        if isinstance(warnings, list):
            summary.warnings_count += len(warnings)

        # Steel quantity (approximate from Ast)
        ast_mm2 = _safe_get(result, ["ast_provided", "ast_provided_mm2", "ast"], 0.0)
        span_mm = _safe_get(result, ["span_mm", "span"], 5000.0)
        if ast_mm2 and span_mm:
            # Approximate: Ast * span * density (7850 kg/m³)
            steel_kg = float(ast_mm2) * float(span_mm) / 1e6 * 7.85
            summary.total_steel_kg += steel_kg

        # Concrete volume
        b_mm = _safe_get(result, ["b_mm", "width_mm", "width"], 300.0)
        d_mm = _safe_get(result, ["D_mm", "depth_mm", "depth"], 500.0)
        if b_mm and d_mm and span_mm:
            volume_m3 = float(b_mm) * float(d_mm) * float(span_mm) / 1e9
            summary.total_concrete_m3 += volume_m3

        # By story tracking
        story_str = str(story)
        if story_str not in summary.by_story:
            summary.by_story[story_str] = {"total": 0, "passed": 0, "failed": 0}
        summary.by_story[story_str]["total"] += 1
        if is_valid:
            summary.by_story[story_str]["passed"] += 1
        else:
            summary.by_story[story_str]["failed"] += 1

    # Calculate averages
    if utilizations:
        summary.avg_utilization = sum(utilizations) / len(utilizations)

    return summary


def code_checks_live(
    beam: Mapping[str, Any],
    config: Mapping[str, Any] | None = None,
) -> CodeCheckResult:
    """Perform fast IS 456 code checks on a beam with optional rebar config.

    This is designed for real-time UI updates during editing.

    Args:
        beam: Beam parameters (b_mm, D_mm, span_mm, etc.)
        config: Optional rebar configuration to check

    Returns:
        CodeCheckResult with pass/fail status and check details.

    Example:
        >>> result = code_checks_live(beam_data, rebar_config)
        >>> if not result.passed:
        ...     print(result.critical_failures)
    """
    checks: list[dict[str, Any]] = []
    failures: list[str] = []
    warnings: list[str] = []

    # Extract beam parameters
    b_mm = float(_safe_get(beam, ["b_mm", "width_mm", "width", "b"], 300))
    D_mm = float(_safe_get(beam, ["D_mm", "depth_mm", "depth", "D"], 500))
    d_mm = float(_safe_get(beam, ["d_mm", "effective_depth"], D_mm - 50))
    span_mm = float(_safe_get(beam, ["span_mm", "span"], 5000))
    _fck = float(_safe_get(beam, ["fck_mpa", "fck", "fck_nmm2"], 25))  # noqa: F841
    fy = float(_safe_get(beam, ["fy_mpa", "fy", "fy_nmm2"], 500))
    mu_knm = float(_safe_get(beam, ["mu_knm", "moment"], 100))
    _vu_kn = float(_safe_get(beam, ["vu_kn", "shear"], 50))  # noqa: F841 - reserved for future shear checks

    # Config parameters
    if config:
        ast_mm2 = float(_safe_get(config, ["ast_mm2", "ast_provided", "ast"], 0))
        bar_count = int(_safe_get(config, ["bar_count", "bars"], 0))
        bar_dia = float(_safe_get(config, ["bar_dia_mm", "bar_dia"], 16))
        if ast_mm2 == 0 and bar_count > 0:
            ast_mm2 = bar_count * math.pi * (bar_dia / 2) ** 2
    else:
        ast_mm2 = 0.0
        bar_count = 0
        bar_dia = 16.0

    max_utilization = 0.0
    governing = ""

    # Check 1: Minimum steel (Cl. 26.5.1.1)
    ast_min = 0.85 * b_mm * d_mm / fy
    if ast_mm2 > 0:
        if ast_mm2 >= ast_min:
            checks.append(
                {
                    "name": "Minimum Steel",
                    "clause": "26.5.1.1",
                    "passed": True,
                    "value": round(ast_mm2, 1),
                    "limit": round(ast_min, 1),
                }
            )
        else:
            checks.append(
                {
                    "name": "Minimum Steel",
                    "clause": "26.5.1.1",
                    "passed": False,
                    "value": round(ast_mm2, 1),
                    "limit": round(ast_min, 1),
                }
            )
            failures.append(
                f"Ast {ast_mm2:.0f} < Ast_min {ast_min:.0f} mm² (Cl. 26.5.1.1)"
            )

    # Check 2: Maximum steel (Cl. 26.5.1.1)
    ast_max = 0.04 * b_mm * D_mm
    if ast_mm2 > 0:
        if ast_mm2 <= ast_max:
            checks.append(
                {
                    "name": "Maximum Steel",
                    "clause": "26.5.1.1",
                    "passed": True,
                    "value": round(ast_mm2, 1),
                    "limit": round(ast_max, 1),
                }
            )
        else:
            checks.append(
                {
                    "name": "Maximum Steel",
                    "clause": "26.5.1.1",
                    "passed": False,
                    "value": round(ast_mm2, 1),
                    "limit": round(ast_max, 1),
                }
            )
            failures.append(
                f"Ast {ast_mm2:.0f} > Ast_max {ast_max:.0f} mm² (Cl. 26.5.1.1)"
            )

    # Check 3: Span/Depth ratio (Cl. 23.2.1)
    span_depth_ratio = span_mm / D_mm
    limit_ratio = 20.0  # Simply supported
    if span_depth_ratio <= limit_ratio:
        checks.append(
            {
                "name": "Span/Depth Ratio",
                "clause": "23.2.1",
                "passed": True,
                "value": round(span_depth_ratio, 1),
                "limit": limit_ratio,
            }
        )
    else:
        checks.append(
            {
                "name": "Span/Depth Ratio",
                "clause": "23.2.1",
                "passed": False,
                "value": round(span_depth_ratio, 1),
                "limit": limit_ratio,
            }
        )
        warnings.append(
            f"L/D = {span_depth_ratio:.1f} > {limit_ratio} (Cl. 23.2.1) - check deflection"
        )

    # Check 4: Moment capacity (approximate)
    if ast_mm2 > 0:
        # Simplified capacity calculation
        lever_arm = d_mm * 0.87  # Approximate
        mu_capacity = ast_mm2 * fy * lever_arm / 1e6 * 0.87  # kN·m
        moment_util = mu_knm / max(mu_capacity, 1)
        max_utilization = max(max_utilization, moment_util)
        if moment_util <= 1.0:
            checks.append(
                {
                    "name": "Moment Capacity",
                    "clause": "Annex G",
                    "passed": True,
                    "value": round(mu_knm, 1),
                    "limit": round(mu_capacity, 1),
                    "utilization": round(moment_util, 2),
                }
            )
        else:
            checks.append(
                {
                    "name": "Moment Capacity",
                    "clause": "Annex G",
                    "passed": False,
                    "value": round(mu_knm, 1),
                    "limit": round(mu_capacity, 1),
                    "utilization": round(moment_util, 2),
                }
            )
            failures.append(f"Mu {mu_knm:.0f} kN·m > Capacity {mu_capacity:.0f} kN·m")
            governing = "Moment Capacity"

    # Check 5: Width check (Cl. 26.5.1.2)
    if b_mm < 200:
        warnings.append(f"Width {b_mm:.0f}mm < 200mm minimum recommended")
        checks.append(
            {
                "name": "Minimum Width",
                "clause": "26.5.1.2",
                "passed": False,
                "value": b_mm,
                "limit": 200,
            }
        )
    else:
        checks.append(
            {
                "name": "Minimum Width",
                "clause": "26.5.1.2",
                "passed": True,
                "value": b_mm,
                "limit": 200,
            }
        )

    passed = len(failures) == 0

    return CodeCheckResult(
        passed=passed,
        checks=checks,
        critical_failures=failures,
        warnings=warnings,
        utilization=max_utilization,
        governing_check=governing,
    )


def suggest_rebar_options(
    beam: Mapping[str, Any],
    targets: Mapping[str, Any] | None = None,
) -> RebarSuggestionsResult:
    """Suggest optimized rebar configurations for a beam.

    Args:
        beam: Beam parameters including required Ast, dimensions
        targets: Optional optimization targets (minimize_cost, minimize_bars, etc.)

    Returns:
        RebarSuggestionsResult with suggested configurations.

    Example:
        >>> result = suggest_rebar_options(beam_data)
        >>> for sug in result.suggestions:
        ...     print(f"{sug.title}: saves {sug.savings_percent}%")
    """
    suggestions: list[RebarSuggestion] = []

    beam_id = str(_safe_get(beam, ["beam_id", "id", "name"], "beam"))
    ast_required = float(_safe_get(beam, ["ast_required", "ast_req", "ast"], 0))
    ast_provided = float(_safe_get(beam, ["ast_provided", "ast_prov"], 0))
    current_bar_count = int(_safe_get(beam, ["bar_count", "bars"], 0))
    current_bar_dia = float(_safe_get(beam, ["bar_dia_mm", "bar_dia"], 16))
    b_mm = float(_safe_get(beam, ["b_mm", "width_mm", "width"], 300))
    cover_mm = float(_safe_get(beam, ["cover_mm", "cover"], 40))

    # Standard bar diameters
    bar_dias = [10, 12, 16, 20, 25, 32]

    # Calculate current Ast if not provided
    if ast_provided == 0 and current_bar_count > 0:
        ast_provided = current_bar_count * math.pi * (current_bar_dia / 2) ** 2

    max_savings = 0.0

    # Generate alternative configurations
    for dia in bar_dias:
        bar_area = math.pi * (dia / 2) ** 2
        bars_needed = math.ceil(ast_required / bar_area) if ast_required > 0 else 2

        # Check if bars fit
        available_width = b_mm - 2 * cover_mm - 2 * 8 - dia  # 8mm stirrups
        min_spacing = max(dia, 20, 25)  # IS 456 min spacing
        max_bars = int(available_width / (dia + min_spacing)) + 1

        if bars_needed > max_bars:
            continue  # Won't fit in single layer

        ast_new = bars_needed * bar_area
        if ast_new < ast_required * 0.99:
            continue  # Doesn't meet requirement

        excess = ast_new - ast_required
        savings = (
            (ast_provided - ast_new) / max(ast_provided, 1) * 100
            if ast_provided > 0
            else 0
        )

        if savings > 1:  # Only suggest if meaningful savings
            impact = "HIGH" if savings > 10 else ("MEDIUM" if savings > 5 else "LOW")
            suggestions.append(
                RebarSuggestion(
                    id=f"opt_{dia}mm_{bars_needed}bars",
                    title=f"{bars_needed}Ø{dia}mm",
                    description=f"Use {bars_needed} bars of {dia}mm diameter",
                    impact=impact,
                    savings_percent=savings,
                    suggested_config={
                        "bar_count": bars_needed,
                        "bar_dia_mm": dia,
                        "ast_provided_mm2": round(ast_new, 1),
                        "excess_mm2": round(excess, 1),
                    },
                    rationale=f"Provides {ast_new:.0f} mm² ({excess:.0f} mm² excess). Saves {savings:.1f}% steel.",
                )
            )
            max_savings = max(max_savings, savings)

    # Sort by savings (descending)
    suggestions.sort(key=lambda s: s.savings_percent, reverse=True)

    return RebarSuggestionsResult(
        beam_id=beam_id,
        suggestions=suggestions[:5],  # Top 5 suggestions
        current_ast_mm2=ast_provided,
        min_ast_mm2=ast_required,
        max_savings_percent=max_savings,
    )
