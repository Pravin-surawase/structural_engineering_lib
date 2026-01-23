# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Shared rebar optimization utilities using library functions.

This module provides UI-friendly wrappers around the library's bar selection
and optimization functions. It consolidates duplicate implementations from:
- components/ai_workspace.py:2059 (suggest_optimal_rebar)
- components/ai_workspace.py:2222 (optimize_beam_line)

The library already has `select_bar_arrangement()` in codes/is456/detailing.py.
This wrapper converts library dataclasses to widget-compatible dicts.

Created: Session 63 (Jan 23, 2026)
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd

# Try to import library functions
try:
    from structural_lib.codes.is456.detailing import (
        select_bar_arrangement,
        STANDARD_BAR_DIAMETERS,
    )
    from structural_lib.codes.is456.shear import design_shear

    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False
    STANDARD_BAR_DIAMETERS = [8, 10, 12, 16, 20, 25, 32]


def suggest_optimal_rebar(
    b_mm: float,
    D_mm: float,
    mu_knm: float,
    vu_kn: float,
    fck: float = 25.0,
    fy: float = 500.0,
    cover_mm: float = 40.0,
) -> dict[str, Any] | None:
    """Suggest optimal reinforcement for given loads.

    Uses library's `select_bar_arrangement()` internally for bar selection,
    then formats the result for UI widgets (session state keys).

    Args:
        b_mm: Beam width in mm
        D_mm: Beam depth in mm
        mu_knm: Ultimate moment in kN·m
        vu_kn: Ultimate shear in kN
        fck: Concrete strength (N/mm²)
        fy: Steel yield strength (N/mm²)
        cover_mm: Clear cover in mm

    Returns:
        Dict with keys compatible with rebar editor session state:
        - bottom_layer1_dia, bottom_layer1_count
        - bottom_layer2_dia, bottom_layer2_count
        - top_layer1_dia, top_layer1_count
        - stirrup_dia, stirrup_spacing
    """
    # Calculate effective depth
    stirrup_dia_assumed = 8.0
    bar_dia_assumed = 16.0
    d_eff = D_mm - cover_mm - stirrup_dia_assumed - bar_dia_assumed / 2

    if d_eff <= 0 or fy <= 0 or b_mm <= 0:
        return None

    # Calculate required steel area (simplified IS 456)
    # Ast = Mu / (0.87 * fy * 0.9 * d)
    # Guards: fy > 0, d_eff > 0 checked above
    lever_arm = 0.87 * fy * 0.9 * d_eff
    ast_req = (mu_knm * 1e6 / lever_arm) if mu_knm > 0 and lever_arm > 0 else 0

    # Minimum steel (IS 456 Cl 26.5.1.1)
    # Guard: fy > 0 checked above
    ast_min = (0.85 * b_mm * d_eff / fy) if fy > 0 else 0
    ast_target = max(ast_req * 1.1, ast_min)  # 10% margin

    # Use library function if available
    if LIBRARY_AVAILABLE:
        arrangement = select_bar_arrangement(
            ast_required=ast_target,
            b=b_mm,
            cover=cover_mm,
            stirrup_dia=stirrup_dia_assumed,
            max_layers=2,
        )

        # Convert BarArrangement to widget-compatible dict
        if arrangement.layers == 1:
            bottom_config = {
                "bottom_layer1_dia": int(arrangement.diameter),
                "bottom_layer1_count": arrangement.count,
                "bottom_layer2_dia": 0,
                "bottom_layer2_count": 0,
            }
        else:
            # Two layers - split count
            layer1_count = (arrangement.count + 1) // 2
            layer2_count = arrangement.count - layer1_count
            bottom_config = {
                "bottom_layer1_dia": int(arrangement.diameter),
                "bottom_layer1_count": layer1_count,
                "bottom_layer2_dia": int(arrangement.diameter),
                "bottom_layer2_count": layer2_count,
            }
    else:
        # Fallback implementation
        bottom_config = _fallback_bar_selection(ast_target, b_mm, cover_mm)

    # Top steel (minimum hanger bars)
    top_config = {
        "top_layer1_dia": 12,
        "top_layer1_count": 2,
    }

    # Stirrup design
    stirrup_config = _design_stirrups(
        b_mm=b_mm,
        d_eff=d_eff,
        vu_kn=vu_kn,
        fck=fck,
        fy=fy,
        ast_provided=_calculate_ast(bottom_config),
    )

    return {**bottom_config, **top_config, **stirrup_config}


def _calculate_ast(config: dict) -> float:
    """Calculate provided steel area from config dict."""
    ast = 0.0
    for layer in ["bottom_layer1", "bottom_layer2"]:
        dia = config.get(f"{layer}_dia", 0)
        count = config.get(f"{layer}_count", 0)
        if dia > 0 and count > 0:
            ast += count * math.pi * (dia / 2) ** 2
    return ast


def _fallback_bar_selection(
    ast_required: float,
    b: float,
    cover: float,
) -> dict[str, Any]:
    """Fallback bar selection when library not available."""
    bar_options = [12, 16, 20, 25, 32]
    best_config = {"bottom_layer1_dia": 16, "bottom_layer1_count": 4,
                   "bottom_layer2_dia": 0, "bottom_layer2_count": 0}

    for dia in bar_options:
        area = math.pi * (dia / 2) ** 2
        count = max(2, math.ceil(ast_required / area)) if area > 0 else 2
        if count <= 6:
            best_config = {
                "bottom_layer1_dia": dia,
                "bottom_layer1_count": count,
                "bottom_layer2_dia": 0,
                "bottom_layer2_count": 0,
            }
            break

    return best_config


def _design_stirrups(
    b_mm: float,
    d_eff: float,
    vu_kn: float,
    fck: float,
    fy: float,
    ast_provided: float,
) -> dict[str, Any]:
    """Design stirrup configuration.

    Returns dict with stirrup_dia and stirrup_spacing.
    """
    # Calculate shear stress
    # Guard: b_mm * d_eff must be > 0
    denom = b_mm * d_eff
    tau_v = (vu_kn * 1000 / denom) if denom > 0 else 0

    # Permissible shear stress (simplified IS 456 Table 19)
    pt = (100 * ast_provided / denom) if denom > 0 else 0
    if pt <= 0.25:
        tau_c = 0.36
    elif pt <= 0.50:
        tau_c = 0.48
    elif pt <= 0.75:
        tau_c = 0.56
    elif pt <= 1.00:
        tau_c = 0.62
    else:
        tau_c = min(0.71 + (pt - 1.50) * 0.08, 0.82)

    # Adjust for concrete grade (25 is reference grade, never zero)
    tau_c *= (fck / 25.0) ** 0.5

    # Shear to be resisted by stirrups
    vus = max(0, (tau_v - tau_c) * b_mm * d_eff / 1000)

    # Select stirrup configuration
    stirrup_options = [8, 10, 12]
    spacing_options = [100, 125, 150, 175, 200, 250, 300]

    best_dia = 8
    best_spacing = 150

    for st_dia in stirrup_options:
        asv = 2 * math.pi * (st_dia / 2) ** 2  # 2-legged
        for sv in spacing_options:
            if vus > 0 and sv > 0:
                capacity = (0.87 * fy * asv * d_eff / sv / 1000) if sv > 0 else 0
                if capacity >= vus:
                    max_sv = min(0.75 * d_eff, 300)
                    if sv <= max_sv:
                        best_dia = st_dia
                        best_spacing = sv
                        break
            else:
                # Minimum stirrups
                sv_denom = b_mm * sv
                ratio = (asv / sv_denom) if sv_denom > 0 else 0
                min_ratio = (0.4 / fy) if fy > 0 else 0
                max_sv = min(0.75 * d_eff, 300)
                if ratio >= min_ratio and sv <= max_sv:
                    best_dia = st_dia
                    best_spacing = sv
                    break
        else:
            continue
        break

    return {"stirrup_dia": best_dia, "stirrup_spacing": best_spacing}


def optimize_beam_line(
    beam_ids: list[str],
    df: "pd.DataFrame",
    fck: float = 25.0,
    fy: float = 500.0,
    cover_mm: float = 40.0,
) -> dict[str, dict]:
    """Optimize all beams in a beam line for consistency.

    Uses library's `select_bar_arrangement()` for each beam, then unifies
    bar sizes across the line for construction consistency.

    Args:
        beam_ids: List of beam IDs in the same beam line
        df: DataFrame with beam data (b_mm, D_mm, mu_knm, vu_kn columns)
        fck: Concrete strength (N/mm²)
        fy: Steel yield strength (N/mm²)
        cover_mm: Clear cover (mm)

    Returns:
        Dict mapping beam_id -> optimized rebar config
    """
    if not beam_ids:
        return {}

    # Step 1: Get individual optimal configs
    individual_configs = {}
    for beam_id in beam_ids:
        row = df[df["beam_id"] == beam_id]
        if row.empty:
            continue
        row = row.iloc[0]

        config = suggest_optimal_rebar(
            b_mm=float(row.get("b_mm", 300)),
            D_mm=float(row.get("D_mm", 450)),
            mu_knm=float(row.get("mu_knm", 100)),
            vu_kn=float(row.get("vu_kn", 50)),
            fck=fck,
            fy=fy,
            cover_mm=cover_mm,
        )
        if config:
            individual_configs[beam_id] = config

    if not individual_configs:
        return {}

    # Step 2: Unify bar sizes (use max diameter for consistency)
    max_bottom_dia = max(
        (c.get("bottom_layer1_dia", 16) for c in individual_configs.values()),
        default=16
    )
    max_stirrup_dia = max(
        (c.get("stirrup_dia", 8) for c in individual_configs.values()),
        default=8
    )
    min_stirrup_spacing = min(
        (c.get("stirrup_spacing", 150) for c in individual_configs.values()),
        default=150
    )

    # Step 3: Recalculate with unified bar size
    unified_configs = {}
    for beam_id, config in individual_configs.items():
        row = df[df["beam_id"] == beam_id].iloc[0]
        b_mm = float(row.get("b_mm", 300))
        D_mm = float(row.get("D_mm", 450))
        mu_knm = float(row.get("mu_knm", 100))

        # Recalculate count with unified diameter
        d_eff = D_mm - cover_mm - 8 - max_bottom_dia / 2.0
        if d_eff <= 0 or fy <= 0:
            continue  # Skip invalid beams

        lever_arm = 0.87 * fy * 0.9 * d_eff
        ast_req = (mu_knm * 1e6 / lever_arm) if mu_knm > 0 and lever_arm > 0 else 0
        ast_min = (0.85 * b_mm * d_eff / fy) if fy > 0 else 0
        ast_target = max(ast_req * 1.1, ast_min)

        bar_area = math.pi * (max_bottom_dia / 2.0) ** 2
        count = max(2, math.ceil(ast_target / bar_area)) if bar_area > 0 else 2

        unified_configs[beam_id] = {
            "bottom_layer1_dia": max_bottom_dia,
            "bottom_layer1_count": min(count, 6),
            "bottom_layer2_dia": max_bottom_dia if count > 6 else 0,
            "bottom_layer2_count": max(0, count - 6),
            "top_layer1_dia": 12,
            "top_layer1_count": 2,
            "stirrup_dia": max_stirrup_dia,
            "stirrup_spacing": min_stirrup_spacing,
        }

    return unified_configs
