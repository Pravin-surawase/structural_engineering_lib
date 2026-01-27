# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Wrapper helpers for dashboard + live code checks."""

from __future__ import annotations

from typing import Any

from .precheck import quick_precheck
from .smart_designer import DashboardReport, SmartDesigner


def generate_dashboard(
    *,
    design: Any,
    span_mm: float,
    mu_knm: float,
    vu_kn: float,
    include_cost: bool = True,
    include_suggestions: bool = True,
    include_sensitivity: bool = True,
    include_constructability: bool = True,
    cost_profile: Any | None = None,
    weights: dict[str, float] | None = None,
) -> DashboardReport:
    """Generate a SmartDesigner dashboard report from a design result."""
    return SmartDesigner.analyze(
        design=design,
        span_mm=span_mm,
        mu_knm=mu_knm,
        vu_kn=vu_kn,
        include_cost=include_cost,
        include_suggestions=include_suggestions,
        include_sensitivity=include_sensitivity,
        include_constructability=include_constructability,
        cost_profile=cost_profile,
        weights=weights,
    )


def code_checks_live(
    *,
    span_mm: float,
    b_mm: float,
    D_mm: float,
    d_mm: float,
    mu_knm: float,
    fck_nmm2: float,
    fy_nmm2: float = 500.0,
) -> dict[str, Any]:
    """Fast, advisory code checks suitable for live UI feedback."""
    result = quick_precheck(
        span_mm=span_mm,
        b_mm=b_mm,
        d_mm=d_mm,
        D_mm=D_mm,
        mu_knm=mu_knm,
        fck_nmm2=fck_nmm2,
        fy_nmm2=fy_nmm2,
    )
    return result.to_dict()
