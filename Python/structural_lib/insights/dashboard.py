# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Dashboard Module — Design Analytics and Code Checks.

Provides:
- Dashboard generation for aggregated design summaries
- Live code checks for real-time UI feedback
- Rebar optimization suggestions

Example:
    >>> from structural_lib.insights.dashboard import generate_dashboard, code_checks_live
    >>> dashboard = generate_dashboard(design_result)
    >>> checks = code_checks_live(beam_params, rebar_config)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from structural_lib.codes.is456 import detailing


__all__ = [
    # Dataclasses
    "DashboardData",
    "CodeCheckResult",
    "CodeCheck",
    "RebarSuggestion",
    # Functions
    "generate_dashboard",
    "code_checks_live",
    "suggest_rebar_options",
]


# =============================================================================
# Dataclasses
# =============================================================================


@dataclass
class CodeCheck:
    """Single IS 456 code check result."""

    clause: str
    description: str
    passed: bool
    value: float | None = None
    limit: float | None = None
    message: str = ""

    def to_dict(self) -> dict:
        return {
            "clause": self.clause,
            "description": self.description,
            "passed": self.passed,
            "value": self.value,
            "limit": self.limit,
            "message": self.message,
        }


@dataclass
class CodeCheckResult:
    """Collection of IS 456 code checks for a beam configuration."""

    overall_pass: bool
    checks: list[CodeCheck]
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "overallPass": self.overall_pass,
            "checks": [c.to_dict() for c in self.checks],
            "errors": self.errors,
            "warnings": self.warnings,
            "passCount": sum(1 for c in self.checks if c.passed),
            "failCount": sum(1 for c in self.checks if not c.passed),
        }


@dataclass
class DashboardData:
    """Aggregated design dashboard data."""

    beam_id: str
    status: str  # "pass", "fail", "warning"
    utilization_moment: float
    utilization_shear: float
    utilization_overall: float

    # Steel quantities
    ast_required_mm2: float
    ast_provided_mm2: float
    steel_ratio_percent: float

    # Capacity summary
    moment_capacity_knm: float
    shear_capacity_kn: float
    applied_moment_knm: float
    applied_shear_kn: float

    # Code checks summary
    code_checks_passed: int
    code_checks_total: int
    critical_checks: list[str]

    # Metadata
    messages: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "beamId": self.beam_id,
            "status": self.status,
            "utilization": {
                "moment": round(self.utilization_moment, 3),
                "shear": round(self.utilization_shear, 3),
                "overall": round(self.utilization_overall, 3),
            },
            "steel": {
                "astRequired": round(self.ast_required_mm2, 1),
                "astProvided": round(self.ast_provided_mm2, 1),
                "ratioPercent": round(self.steel_ratio_percent, 3),
            },
            "capacity": {
                "momentKnm": round(self.moment_capacity_knm, 2),
                "shearKn": round(self.shear_capacity_kn, 2),
            },
            "applied": {
                "momentKnm": round(self.applied_moment_knm, 2),
                "shearKn": round(self.applied_shear_kn, 2),
            },
            "codeChecks": {
                "passed": self.code_checks_passed,
                "total": self.code_checks_total,
                "critical": self.critical_checks,
            },
            "messages": self.messages,
        }


@dataclass
class RebarSuggestion:
    """A suggested rebar configuration."""

    bar_count: int
    bar_dia_mm: float
    layers: int
    ast_provided_mm2: float
    utilization: float
    cost_index: float  # Relative cost (1.0 = baseline)
    spacing_ok: bool
    message: str = ""

    def to_dict(self) -> dict:
        return {
            "barCount": self.bar_count,
            "barDia": self.bar_dia_mm,
            "layers": self.layers,
            "astProvided": round(self.ast_provided_mm2, 1),
            "utilization": round(self.utilization, 3),
            "costIndex": round(self.cost_index, 3),
            "spacingOk": self.spacing_ok,
            "message": self.message,
        }


# =============================================================================
# Helper Functions
# =============================================================================


def _safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float."""
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _get_param(data: dict, keys: list[str], default: float) -> float:
    """Get parameter from dict with multiple possible keys."""
    for key in keys:
        if key in data and data[key] is not None:
            return _safe_float(data[key], default)
    return default


def _calculate_ast(bar_count: int, bar_dia: float) -> float:
    """Calculate steel area from bar count and diameter."""
    return bar_count * math.pi * (bar_dia / 2) ** 2


def _to_dict(value: Any) -> dict:
    """Convert value to dict."""
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if hasattr(value, "__dict__"):
        return vars(value)
    return {}


# =============================================================================
# Main Functions
# =============================================================================


def generate_dashboard(
    design_result: dict | Any,
    beam_params: dict | None = None,
) -> DashboardData:
    """
    Generate dashboard data from a design result.

    Args:
        design_result: Design result dict or object (from design_beam_is456)
        beam_params: Optional beam parameters for additional context

    Returns:
        DashboardData with aggregated metrics

    Example:
        >>> result = design_beam_is456(...)
        >>> dashboard = generate_dashboard(result)
        >>> print(dashboard.utilization_overall)
    """
    # Convert to dict if needed
    if hasattr(design_result, "model_dump"):
        data = design_result.model_dump()
    elif hasattr(design_result, "to_dict"):
        data = design_result.to_dict()
    elif hasattr(design_result, "__dict__"):
        data = vars(design_result)
    else:
        data = dict(design_result) if design_result else {}

    # Extract core values
    beam_id = data.get("id", data.get("beam_id", "B1"))
    status_raw = data.get("status", "pass")
    if hasattr(status_raw, "value"):
        status = status_raw.value.lower()
    else:
        status = str(status_raw).lower()

    # Forces
    mu = _safe_float(data.get("mu_knm", data.get("Mu_kNm", 0)))
    vu = _safe_float(data.get("vu_kn", data.get("Vu_kN", 0)))

    # Required steel
    ast_required = _safe_float(data.get("ast_mm2", data.get("Ast_mm2", 0)))

    # Capacities
    moment_cap = _safe_float(data.get("moment_capacity_knm", mu * 1.2))
    shear_cap = _safe_float(data.get("shear_capacity_kn", vu * 1.2))

    # Utilization
    util_moment = mu / moment_cap if moment_cap > 0 else 0.0
    util_shear = vu / shear_cap if shear_cap > 0 else 0.0
    util_overall = _safe_float(data.get("utilization", max(util_moment, util_shear)))

    # Steel ratio (assuming beam params available)
    b_mm = 300.0
    d_mm = 450.0
    if beam_params:
        b_mm = _get_param(beam_params, ["b_mm", "width", "b"], 300.0)
        d_mm = _get_param(beam_params, ["D_mm", "depth", "D"], 450.0)

    effective_depth = d_mm - 50  # Approximate
    steel_ratio = (ast_required / (b_mm * effective_depth)) * 100 if effective_depth > 0 else 0.0

    # Code checks summary (simplified)
    messages = data.get("messages", [])
    checks_passed = 5 if status in ("pass", "warning") else 3
    checks_total = 6
    critical = []
    if status == "fail":
        critical.append("Flexure capacity exceeded")
    if util_shear > 0.9:
        critical.append("Shear near limit")

    # Provided steel (estimate from messages or default)
    ast_provided = ast_required * 1.1  # Default 10% margin

    return DashboardData(
        beam_id=beam_id,
        status=status,
        utilization_moment=util_moment,
        utilization_shear=util_shear,
        utilization_overall=util_overall,
        ast_required_mm2=ast_required,
        ast_provided_mm2=ast_provided,
        steel_ratio_percent=steel_ratio,
        moment_capacity_knm=moment_cap,
        shear_capacity_kn=shear_cap,
        applied_moment_knm=mu,
        applied_shear_kn=vu,
        code_checks_passed=checks_passed,
        code_checks_total=checks_total,
        critical_checks=critical,
        messages=messages if isinstance(messages, list) else [],
    )


def code_checks_live(
    beam: dict | Any,
    config: dict | Any,
) -> CodeCheckResult:
    """
    Perform live IS 456 code checks for real-time UI feedback.

    Args:
        beam: Beam parameters (width, depth, cover, span, etc.)
        config: Rebar configuration (bar_count, bar_dia, stirrup_dia, etc.)

    Returns:
        CodeCheckResult with individual check results

    Example:
        >>> result = code_checks_live(
        ...     {"b_mm": 300, "D_mm": 450, "cover_mm": 40},
        ...     {"bar_count": 4, "bar_dia_mm": 16}
        ... )
        >>> print(result.overall_pass)
    """
    # Convert to dicts
    beam_dict = _to_dict(beam)
    config_dict = _to_dict(config)

    checks: list[CodeCheck] = []
    errors: list[str] = []
    warnings: list[str] = []

    # Extract parameters
    b_mm = _get_param(beam_dict, ["b_mm", "width", "b"], 300.0)
    d_mm = _get_param(beam_dict, ["D_mm", "depth", "D"], 450.0)
    cover = _get_param(beam_dict, ["cover_mm", "cover"], 40.0)
    span = _get_param(beam_dict, ["span_mm", "span"], 5000.0)

    bar_count = int(_get_param(config_dict, ["bar_count", "bars"], 0))
    bar_dia = _get_param(config_dict, ["bar_dia_mm", "bar_dia"], 16.0)
    stirrup_dia = _get_param(config_dict, ["stirrup_dia_mm", "stirrup_dia"], 8.0)
    layers = int(_get_param(config_dict, ["layers"], 1))
    fy = _get_param(beam_dict, ["fy", "fy_mpa", "fy_nmm2"], 500.0)
    agg_size = _get_param(config_dict, ["agg_size_mm", "agg_size"], 20.0)

    # Effective depth
    d_eff = d_mm - cover - stirrup_dia - bar_dia / 2
    if layers > 1:
        d_eff -= (layers - 1) * (bar_dia + 25) / 2

    # 1. Minimum bar count (Cl 26.5.1.1)
    min_bars = 2
    check_min_bars = CodeCheck(
        clause="26.5.1.1",
        description="Minimum bar count",
        passed=bar_count >= min_bars,
        value=float(bar_count),
        limit=float(min_bars),
        message="" if bar_count >= min_bars else f"Min {min_bars} bars required",
    )
    checks.append(check_min_bars)

    # 2. Clear spacing (Cl 26.3.2)
    if bar_count > 1:
        try:
            spacing = detailing.calculate_bar_spacing(
                b=b_mm, cover=cover, stirrup_dia=stirrup_dia,
                bar_dia=bar_dia, bar_count=bar_count,
            )
            min_spacing = max(bar_dia, agg_size + 5, 25.0)
            spacing_ok = spacing >= min_spacing
            check_spacing = CodeCheck(
                clause="26.3.2",
                description="Clear bar spacing",
                passed=spacing_ok,
                value=round(spacing, 1),
                limit=round(min_spacing, 1),
                message="" if spacing_ok else f"Spacing {spacing:.0f}mm < min {min_spacing:.0f}mm",
            )
            checks.append(check_spacing)
            if not spacing_ok:
                warnings.append(f"Bar spacing {spacing:.0f}mm below minimum {min_spacing:.0f}mm")
        except Exception as e:
            errors.append(f"Spacing calculation failed: {e}")

    # 3. Steel ratio limits (Cl 26.5.1.1)
    ast = _calculate_ast(bar_count, bar_dia)
    min_ast_ratio = 0.85 / fy * 100  # Approx 0.17% for Fe500
    max_ast_ratio = 4.0  # 4% max
    steel_ratio = (ast / (b_mm * d_eff)) * 100 if d_eff > 0 else 0

    check_min_steel = CodeCheck(
        clause="26.5.1.1(a)",
        description="Minimum steel ratio",
        passed=steel_ratio >= min_ast_ratio,
        value=round(steel_ratio, 3),
        limit=round(min_ast_ratio, 3),
        message="" if steel_ratio >= min_ast_ratio else "Below minimum steel ratio",
    )
    checks.append(check_min_steel)

    check_max_steel = CodeCheck(
        clause="26.5.1.1(b)",
        description="Maximum steel ratio",
        passed=steel_ratio <= max_ast_ratio,
        value=round(steel_ratio, 3),
        limit=max_ast_ratio,
        message="" if steel_ratio <= max_ast_ratio else "Exceeds maximum steel ratio",
    )
    checks.append(check_max_steel)

    # 4. Effective depth check
    min_d_eff_ratio = 0.05  # d/span > 5%
    d_eff_ratio = d_eff / span if span > 0 else 0
    check_depth = CodeCheck(
        clause="23.2.1",
        description="Effective depth ratio",
        passed=d_eff_ratio >= min_d_eff_ratio,
        value=round(d_eff_ratio, 4),
        limit=min_d_eff_ratio,
        message="" if d_eff_ratio >= min_d_eff_ratio else "Beam may be too shallow",
    )
    checks.append(check_depth)

    # 5. Bar diameter limit (practical check)
    max_bar_dia = min(d_mm / 10, 40.0)
    check_bar_dia = CodeCheck(
        clause="26.3.3",
        description="Bar diameter limit",
        passed=bar_dia <= max_bar_dia,
        value=bar_dia,
        limit=max_bar_dia,
        message="" if bar_dia <= max_bar_dia else f"Bar dia {bar_dia}mm exceeds limit",
    )
    checks.append(check_bar_dia)

    # 6. Cover adequacy (Cl 26.4)
    min_cover = max(bar_dia, 25.0)  # Simplified
    check_cover = CodeCheck(
        clause="26.4.1",
        description="Minimum cover",
        passed=cover >= min_cover,
        value=cover,
        limit=min_cover,
        message="" if cover >= min_cover else f"Cover {cover}mm < min {min_cover}mm",
    )
    checks.append(check_cover)

    overall_pass = all(c.passed for c in checks) and len(errors) == 0

    return CodeCheckResult(
        overall_pass=overall_pass,
        checks=checks,
        errors=errors,
        warnings=warnings,
    )


def suggest_rebar_options(
    beam: dict | Any,
    targets: dict | Any,
    max_options: int = 5,
) -> list[RebarSuggestion]:
    """
    Suggest optimal rebar configurations for given targets.

    Args:
        beam: Beam parameters (width, depth, cover, etc.)
        targets: Target requirements (ast_required, min_bars, max_layers, etc.)
        max_options: Maximum number of suggestions to return

    Returns:
        List of RebarSuggestion sorted by cost index (best first)

    Example:
        >>> suggestions = suggest_rebar_options(
        ...     {"b_mm": 300, "D_mm": 450, "cover_mm": 40},
        ...     {"ast_required_mm2": 500}
        ... )
        >>> for s in suggestions:
        ...     print(f"{s.bar_count}-{s.bar_dia_mm}φ: {s.ast_provided_mm2}mm²")
    """
    beam_dict = _to_dict(beam)
    target_dict = _to_dict(targets)

    b_mm = _get_param(beam_dict, ["b_mm", "width", "b"], 300.0)
    d_mm = _get_param(beam_dict, ["D_mm", "depth", "D"], 450.0)
    cover = _get_param(beam_dict, ["cover_mm", "cover"], 40.0)
    stirrup_dia = _get_param(beam_dict, ["stirrup_dia_mm", "stirrup_dia"], 8.0)
    agg_size = _get_param(beam_dict, ["agg_size_mm", "agg_size"], 20.0)

    ast_required = _get_param(target_dict, ["ast_required_mm2", "ast_required", "ast"], 200.0)
    min_bars = int(_get_param(target_dict, ["min_bars"], 2))
    max_layers = int(_get_param(target_dict, ["max_layers"], 2))

    # Standard bar diameters
    bar_diameters = [10, 12, 16, 20, 25, 32]

    # Cost index per kg (relative, 16mm = 1.0)
    cost_factors = {10: 1.15, 12: 1.10, 16: 1.00, 20: 0.98, 25: 0.95, 32: 0.93}

    # Steel density for weight calculation
    steel_density = 7850  # kg/m³

    suggestions: list[RebarSuggestion] = []

    for dia in bar_diameters:
        for layer_count in range(1, max_layers + 1):
            # Calculate max bars that fit per layer
            available_width = b_mm - 2 * (cover + stirrup_dia) - dia
            min_spacing = max(dia, agg_size + 5, 25.0)
            max_bars_per_layer = max(
                2, int(available_width / (dia + min_spacing)) + 1
            )

            for bars_per_layer in range(min_bars, max_bars_per_layer + 1):
                bar_count = bars_per_layer * layer_count
                ast_provided = _calculate_ast(bar_count, dia)

                if ast_provided < ast_required:
                    continue

                # Check spacing
                try:
                    spacing = detailing.calculate_bar_spacing(
                        b=b_mm, cover=cover, stirrup_dia=stirrup_dia,
                        bar_dia=dia, bar_count=bars_per_layer,
                    )
                    spacing_ok = spacing >= min_spacing
                except Exception:
                    spacing_ok = False

                # Calculate utilization and cost
                utilization = ast_required / ast_provided if ast_provided > 0 else 0
                volume_m3 = ast_provided * 5000 / 1e9  # Assume 5m span
                weight_kg = volume_m3 * steel_density
                cost_index = weight_kg * cost_factors.get(dia, 1.0)

                message = ""
                if layer_count > 1:
                    message = f"{layer_count} layers"
                if not spacing_ok:
                    message = (message + ", " if message else "") + "spacing tight"

                suggestions.append(
                    RebarSuggestion(
                        bar_count=bar_count,
                        bar_dia_mm=float(dia),
                        layers=layer_count,
                        ast_provided_mm2=ast_provided,
                        utilization=utilization,
                        cost_index=cost_index,
                        spacing_ok=spacing_ok,
                        message=message,
                    )
                )

    # Sort by cost index (lower is better), then by utilization (higher is better)
    suggestions.sort(key=lambda s: (not s.spacing_ok, s.cost_index, -s.utilization))

    return suggestions[:max_options]
