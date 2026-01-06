# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Heuristic pre-checks for quick design guidance (advisory only)."""

from __future__ import annotations

import time

from ..errors import Severity
from ..serviceability import check_deflection_span_depth
from ..types import SupportCondition
from .data_types import HeuristicWarning, PredictiveCheckResult

_HEURISTICS_VERSION = "1.0"


def _add_warning(
    warnings: list[HeuristicWarning],
    *,
    warning_type: str,
    severity: Severity,
    message: str,
    suggestion: str,
    rule_basis: str,
) -> None:
    warnings.append(
        HeuristicWarning(
            type=warning_type,
            severity=severity,
            message=message,
            suggestion=suggestion,
            rule_basis=rule_basis,
        )
    )


def quick_precheck(
    *,
    span_mm: float,
    b_mm: float,
    d_mm: float,
    D_mm: float,
    mu_knm: float,
    fck_nmm2: float,
    fy_nmm2: float = 500.0,
    support_condition: SupportCondition = SupportCondition.SIMPLY_SUPPORTED,
) -> PredictiveCheckResult:
    """Fast heuristic validation before full design.

    Safety note: Advisory only. Does not affect pass/fail or required steel.
    """

    start = time.perf_counter()
    warnings: list[HeuristicWarning] = []

    # Rule 1: Span/depth ratio (Table 23 guidance)
    deflection = check_deflection_span_depth(
        span_mm=span_mm,
        d_mm=d_mm,
        support_condition=support_condition,
    )
    ld_ratio = deflection.computed.get("ld_ratio") if deflection.computed else None
    allowable_ld = (
        deflection.computed.get("allowable_ld") if deflection.computed else None
    )

    if ld_ratio and allowable_ld:
        if ld_ratio > allowable_ld:
            _add_warning(
                warnings,
                warning_type="deflection_risk",
                severity=Severity.WARNING,
                message=(
                    f"L/d={ld_ratio:.2f} exceeds allowable {allowable_ld:.2f} "
                    "(deflection risk)"
                ),
                suggestion="Increase depth or review serviceability modifiers.",
                rule_basis="IS 456 Table 23 (span/depth guidance)",
            )
        elif ld_ratio > 0.85 * allowable_ld:
            _add_warning(
                warnings,
                warning_type="deflection_watch",
                severity=Severity.INFO,
                message=(f"L/d={ld_ratio:.2f} is near allowable {allowable_ld:.2f}"),
                suggestion="Consider a deflection check with modifiers.",
                rule_basis="IS 456 Table 23 (span/depth guidance)",
            )

    # Rule 2: Quick steel estimate
    if b_mm > 0 and d_mm > 0 and fy_nmm2 > 0:
        mu_nmm = mu_knm * 1_000_000.0
        ast_estimate = mu_nmm / (0.87 * fy_nmm2 * 0.9 * d_mm)
        pt_estimate = (ast_estimate / (b_mm * d_mm)) * 100.0

        if pt_estimate > 4.0:
            _add_warning(
                warnings,
                warning_type="doubly_reinforced_likely",
                severity=Severity.WARNING,
                message=(
                    f"Estimated steel % {pt_estimate:.2f} > 4% "
                    "(compression steel likely)"
                ),
                suggestion="Increase depth or concrete grade to reduce steel demand.",
                rule_basis="Typical singly reinforced steel < 4%",
            )
        elif pt_estimate > 2.0:
            _add_warning(
                warnings,
                warning_type="steel_congestion",
                severity=Severity.INFO,
                message=(
                    f"Estimated steel % {pt_estimate:.2f} > 2% "
                    "(spacing may be tight)"
                ),
                suggestion="Review bar spacing and constructability.",
                rule_basis="Practical congestion threshold (~2%)",
            )
        elif pt_estimate < 0.3:
            _add_warning(
                warnings,
                warning_type="low_steel",
                severity=Severity.INFO,
                message=f"Estimated steel % {pt_estimate:.2f} < 0.30%",
                suggestion="Confirm minimum steel per IS 456 Cl. 26.5.1.1.",
                rule_basis="Typical beam steel: 0.5%-1.5%",
            )

    # Rule 3: Width adequacy
    if b_mm > 0 and b_mm < 150:
        _add_warning(
            warnings,
            warning_type="narrow_beam",
            severity=Severity.WARNING,
            message=f"Beam width {b_mm:.0f}mm is narrow for bar placement",
            suggestion="Consider increasing width to ease spacing.",
            rule_basis="Constructability guidance",
        )

    # Rule 4: Cover sanity
    cover_mm = D_mm - d_mm
    if cover_mm <= 0:
        _add_warning(
            warnings,
            warning_type="invalid_cover",
            severity=Severity.WARNING,
            message="Effective depth is greater than total depth (cover <= 0)",
            suggestion="Check D_mm and d_mm inputs.",
            rule_basis="Geometry sanity check",
        )
    elif cover_mm < 25:
        _add_warning(
            warnings,
            warning_type="low_cover",
            severity=Severity.WARNING,
            message=f"Implied cover {cover_mm:.0f}mm < 25mm",
            suggestion="Review cover against IS 456 Table 16.",
            rule_basis="IS 456 Cl. 26.4 (minimum cover)",
        )
    elif D_mm > 0 and (cover_mm / D_mm) > 0.25:
        _add_warning(
            warnings,
            warning_type="cover_ratio",
            severity=Severity.INFO,
            message=(f"Cover ratio {cover_mm / D_mm:.2f} is high for a beam"),
            suggestion="Verify D_mm and d_mm values.",
            rule_basis="Typical cover ratio 0.10-0.15",
        )

    # Rule 5: Concrete grade range (Table 19 bounds)
    if fck_nmm2 < 15 or fck_nmm2 > 40:
        _add_warning(
            warnings,
            warning_type="fck_out_of_range",
            severity=Severity.WARNING,
            message=f"fck {fck_nmm2:.0f} outside Table 19 range (15-40)",
            suggestion="Expect clamping in shear table; confirm grade.",
            rule_basis="IS 456 Table 19 range",
        )

    risk_level = "LOW"
    recommended_action = "proceed"

    if any(w.severity == Severity.WARNING for w in warnings):
        risk_level = "MEDIUM"
        recommended_action = "review_geometry"

    if any(w.type in {"deflection_risk", "doubly_reinforced_likely"} for w in warnings):
        risk_level = "HIGH"
        recommended_action = "review_geometry"

    if not warnings:
        recommended_action = "proceed"
    elif risk_level == "LOW":
        recommended_action = "proceed_with_caution"

    elapsed_ms = (time.perf_counter() - start) * 1000.0

    return PredictiveCheckResult(
        check_time_ms=elapsed_ms,
        risk_level=risk_level,
        warnings=warnings,
        recommended_action=recommended_action,
        heuristics_version=_HEURISTICS_VERSION,
    )
