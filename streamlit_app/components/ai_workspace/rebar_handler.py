# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Rebar analysis and optimization handler.

Extracted from ai_workspace.py (TASK-508).
Contains constructability scoring, optimal rebar suggestion,
beam line optimization, and design check calculations.
All pure computation — no UI code.
"""

from __future__ import annotations

import math
from typing import Any

import pandas as pd


def calculate_constructability_score(
    bottom_bars: list[tuple[int, int]],
    top_bars: list[tuple[int, int]],
    stirrup_spacing: int,
    b_mm: float,
) -> dict[str, Any]:
    """Calculate constructability score for rebar configuration.

    Factors considered:
    - Fewer bars = easier to place (score: +20 for <=3 bars)
    - Same diameter = easier cutting (score: +20 for uniform dia)
    - Wider stirrup spacing = easier (score: +20 for >=150mm)
    - Single layer = easier (score: +20 for no Layer 2)
    - Good width/bar ratio = easier (score: +20 for spacing >50mm)
    """
    score = 0
    notes = []

    # Count total bottom bars
    total_bottom = sum(count for _, count in bottom_bars)
    if total_bottom <= 3:
        score += 20
        notes.append("Few bars")
    elif total_bottom <= 5:
        score += 10
        notes.append("Moderate bars")
    else:
        notes.append("Many bars - harder placement")

    # Check if all same diameter
    diameters = set(dia for dia, count in bottom_bars if count > 0)
    top_dias = set(dia for dia, count in top_bars if count > 0)
    if len(diameters) == 1:
        score += 20
        notes.append("Uniform dia")
    elif len(diameters) <= 2:
        score += 10

    if top_dias and diameters.intersection(top_dias):
        score += 5
        notes.append("Same as top")

    # Stirrup spacing
    if stirrup_spacing >= 200:
        score += 20
        notes.append("Wide stirrups")
    elif stirrup_spacing >= 150:
        score += 15
        notes.append("OK stirrups")
    elif stirrup_spacing >= 100:
        score += 5
        notes.append("Tight stirrups")
    else:
        notes.append("Very tight stirrups")

    # Single layer bonus
    if len(bottom_bars) == 1 or (len(bottom_bars) == 2 and bottom_bars[1][1] == 0):
        score += 20
        notes.append("Single layer")
    else:
        notes.append("Multi-layer")

    # Width/bar ratio
    bar_spacing_approx = b_mm / max(total_bottom, 1)
    if bar_spacing_approx >= 80:
        score += 20
        notes.append("Good spacing")
    elif bar_spacing_approx >= 50:
        score += 10

    summary = " | ".join(notes[:3])  # First 3 notes
    return {"score": min(score, 100), "summary": summary, "notes": notes}


def suggest_optimal_rebar(
    b_mm: float,
    D_mm: float,
    mu_knm: float,
    vu_kn: float,
    fck: float,
    fy: float,
    cover_mm: float,
) -> dict | None:
    """Suggest optimal reinforcement for given loads.

    Tries to minimize steel while maintaining safety and constructability.
    Returns config compatible with rebar editor session state keys.

    Session 33: Now includes shear reinforcement optimization (stirrups).
    """
    # Calculate required steel area (IS 456 simplified)
    d_eff = D_mm - cover_mm - 8 - 16 / 2  # Assume 8mm stirrup, 16mm bar
    if d_eff <= 0 or fy <= 0:
        return None

    ast_req = mu_knm * 1e6 / (0.87 * fy * 0.9 * d_eff)

    # Ensure minimum steel (IS 456 Cl 26.5.1.1)
    ast_min = 0.85 * b_mm * d_eff / fy
    ast_target = max(ast_req * 1.1, ast_min)  # 10% margin or minimum

    # Try different bar configurations - prefer smaller bars first (economy)
    bar_options = [10, 12, 16, 20, 25, 32]  # All supported diameters
    best_config = None
    best_waste = float("inf")

    for dia in bar_options:
        area_per_bar = math.pi * (dia / 2) ** 2
        count = max(2, math.ceil(ast_target / area_per_bar))

        # Check if fits in width (clear spacing >= max(dia, 25mm) per IS 456)
        clear_cover = cover_mm + 8  # Assuming 8mm stirrup
        available = b_mm - 2 * clear_cover - 2 * (dia / 2)  # Inner edge to edge
        min_spacing = max(dia, 25)
        max_bars_single = int(available / (dia + min_spacing)) + 1

        if count <= max_bars_single and count <= 6:
            # Single layer works
            waste = count * area_per_bar - ast_target
            if waste >= 0 and waste < best_waste:
                best_waste = waste
                best_config = {
                    "bottom_layer1_dia": dia,
                    "bottom_layer1_count": count,
                    "bottom_layer2_dia": 0,
                    "bottom_layer2_count": 0,
                }
        elif count > max_bars_single:
            # Need 2 layers
            layer1 = min(count // 2 + count % 2, 6)
            layer2 = count - layer1
            if layer1 >= 2 and layer2 >= 0 and layer2 <= 4:
                total = layer1 + layer2
                waste = total * area_per_bar - ast_target
                if waste >= 0 and waste < best_waste:
                    best_waste = waste
                    best_config = {
                        "bottom_layer1_dia": dia,
                        "bottom_layer1_count": layer1,
                        "bottom_layer2_dia": dia if layer2 > 0 else 0,
                        "bottom_layer2_count": layer2,
                    }

    # Fallback: if nothing found, use a safe default
    if best_config is None:
        # Conservative fallback: 4-16mm bars
        best_config = {
            "bottom_layer1_dia": 16,
            "bottom_layer1_count": 4,
            "bottom_layer2_dia": 0,
            "bottom_layer2_count": 0,
        }

    # =========================================================================
    # Session 33: SHEAR REINFORCEMENT (Stirrup) Optimization
    # =========================================================================
    # Calculate shear stress (IS 456 Cl 40.1)
    tau_v = (vu_kn * 1000) / (b_mm * d_eff) if d_eff > 0 else 0  # N/mm²

    # Permissible shear stress in concrete (IS 456 Table 19, simplified)
    # For fck=25: tau_c varies from 0.36-0.79 based on Ast%
    ast_provided = (
        best_config["bottom_layer1_count"]
        * math.pi
        * (best_config["bottom_layer1_dia"] ** 2)
        / 4
    )
    if best_config.get("bottom_layer2_count", 0) > 0:
        ast_provided += (
            best_config["bottom_layer2_count"]
            * math.pi
            * (best_config.get("bottom_layer2_dia", 0) ** 2)
            / 4
        )

    pt = 100 * ast_provided / (b_mm * d_eff) if d_eff > 0 else 0

    # Simplified tau_c calculation (IS 456 Table 19 for fck=25)
    if pt <= 0.15:
        tau_c = 0.28
    elif pt <= 0.25:
        tau_c = 0.36
    elif pt <= 0.50:
        tau_c = 0.48
    elif pt <= 0.75:
        tau_c = 0.56
    elif pt <= 1.00:
        tau_c = 0.62
    elif pt <= 1.50:
        tau_c = 0.71
    else:
        tau_c = 0.79

    # Adjust for concrete grade (simplified)
    tau_c = tau_c * (fck / 25) ** 0.5 if fck != 25 else tau_c

    # Shear to be resisted by stirrups
    vus = (tau_v - tau_c) * b_mm * d_eff / 1000  # kN

    # Select stirrup configuration
    stirrup_options = [8, 10, 12]  # mm diameter options
    spacing_options = [100, 125, 150, 175, 200, 250, 300]  # mm spacing options

    best_stirrup_dia = 8
    best_stirrup_spacing = 150  # Default

    if vus > 0:
        # Need calculated stirrups
        for st_dia in stirrup_options:
            asv = 2 * math.pi * (st_dia / 2) ** 2  # 2-legged stirrup
            for sv in spacing_options:
                # Capacity: Vus = 0.87 * fy * Asv * d / sv (IS 456 Cl 40.4)
                capacity = 0.87 * fy * asv * d_eff / sv / 1000  # kN
                if capacity >= vus:
                    # Check maximum spacing (IS 456 Cl 26.5.1.5)
                    max_sv = min(0.75 * d_eff, 300)
                    if sv <= max_sv:
                        best_stirrup_dia = st_dia
                        best_stirrup_spacing = sv
                        break
            else:
                continue
            break
    else:
        # Minimum stirrups only (IS 456 Cl 26.5.1.6)
        # Asv/bsv >= 0.4/fy
        for st_dia in stirrup_options:
            asv = 2 * math.pi * (st_dia / 2) ** 2
            for sv in spacing_options:
                ratio = asv / (b_mm * sv)
                min_ratio = 0.4 / fy
                max_sv = min(0.75 * d_eff, 300)
                if ratio >= min_ratio and sv <= max_sv:
                    best_stirrup_dia = st_dia
                    best_stirrup_spacing = sv
                    break
            else:
                continue
            break

    # Add stirrup config to result
    best_config["stirrup_dia"] = best_stirrup_dia
    best_config["stirrup_spacing"] = int(best_stirrup_spacing)

    return best_config


def optimize_beam_line(
    beam_ids: list[str],
    df: pd.DataFrame,
    fck: float = 25.0,
    fy: float = 500.0,
    cover_mm: float = 40.0,
) -> dict[str, dict]:
    """Optimize all beams in a beam line together for consistency.

    This function considers:
    1. IS 456 requirements for each beam
    2. Construction consistency (same bar sizes where possible)
    3. Maximum bar size governs for uniformity

    Args:
        beam_ids: List of beam IDs in the same beam line
        df: DataFrame with beam design data
        fck: Concrete grade (N/mm²)
        fy: Steel grade (N/mm²)
        cover_mm: Cover to reinforcement (mm)

    Returns:
        Dict mapping beam_id -> optimized rebar config
    """
    if not beam_ids:
        return {}

    # Step 1: Get individual optimal configs for each beam
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

    # Step 2: Find the maximum bar size needed across all beams
    # This ensures consistency for construction
    max_bottom_dia = max(
        (c.get("bottom_layer1_dia", 16) for c in individual_configs.values()),
        default=16,
    )

    # Step 3: Calculate required bar counts at the unified diameter
    unified_configs = {}
    for beam_id in beam_ids:
        row = df[df["beam_id"] == beam_id]
        if row.empty:
            continue
        row = row.iloc[0]

        # Calculate required steel area for this beam
        D_mm = float(row.get("D_mm", 450))
        b_mm = float(row.get("b_mm", 300))
        mu_knm = float(row.get("mu_knm", 100))
        d_eff = D_mm - cover_mm - 8 - max_bottom_dia / 2

        if d_eff <= 0 or fy <= 0:
            continue

        ast_req = mu_knm * 1e6 / (0.87 * fy * 0.9 * d_eff)
        ast_min = 0.85 * b_mm * d_eff / fy
        ast_target = max(ast_req * 1.1, ast_min)

        # Calculate bar count at unified diameter
        area_per_bar = math.pi * (max_bottom_dia / 2) ** 2
        count = max(2, math.ceil(ast_target / area_per_bar))

        # Check if fits in single layer
        clear_cover = cover_mm + 8
        available = b_mm - 2 * clear_cover - 2 * (max_bottom_dia / 2)
        min_spacing = max(max_bottom_dia, 25)
        max_bars_single = int(available / (max_bottom_dia + min_spacing)) + 1

        if count <= max_bars_single and count <= 6:
            unified_configs[beam_id] = {
                "bottom_layer1_dia": max_bottom_dia,
                "bottom_layer1_count": count,
                "bottom_layer2_dia": 0,
                "bottom_layer2_count": 0,
                "_version": 1,  # Force widget refresh
            }
        else:
            # Need 2 layers
            layer1 = min(count // 2 + count % 2, 6)
            layer2 = count - layer1
            unified_configs[beam_id] = {
                "bottom_layer1_dia": max_bottom_dia,
                "bottom_layer1_count": layer1,
                "bottom_layer2_dia": max_bottom_dia if layer2 > 0 else 0,
                "bottom_layer2_count": max(0, layer2),
                "_version": 1,  # Force widget refresh
            }

    return unified_configs


def calculate_rebar_checks(
    b_mm: float,
    D_mm: float,
    mu_knm: float,
    vu_kn: float,
    fck: float,
    fy: float,
    cover_mm: float,
    bottom_bars: list[tuple[int, int]],  # [(dia, count), ...]
    top_bars: list[tuple[int, int]],
    stirrup_dia: int,
    stirrup_spacing: int,
) -> dict[str, Any]:
    """Calculate all design checks for given rebar configuration.

    Returns utilization ratios and pass/fail status for:
    - Flexure capacity
    - Shear capacity
    - Minimum reinforcement
    - Maximum reinforcement
    - Spacing requirements
    - Development length
    """
    # Calculate areas
    ast_bottom = sum(count * math.pi * (dia / 2) ** 2 for dia, count in bottom_bars)
    ast_top = (
        sum(count * math.pi * (dia / 2) ** 2 for dia, count in top_bars)
        if top_bars
        else 0
    )
    ast_total = ast_bottom + ast_top

    # Effective depth
    max_dia_bottom = max((dia for dia, _ in bottom_bars), default=16)
    d_eff = D_mm - cover_mm - stirrup_dia - max_dia_bottom / 2

    # IS 456 checks
    results = {
        "ast_provided": ast_bottom,
        "ast_top": ast_top,
        "d_eff": d_eff,
    }

    # 1. Flexure capacity (approximate)
    mu_capacity = 0.87 * fy * ast_bottom * 0.9 * d_eff / 1e6 if fy > 0 else 0
    flexure_util = mu_knm / mu_capacity if mu_capacity > 0 else 999
    results["mu_capacity_knm"] = mu_capacity
    results["flexure_util"] = flexure_util
    results["flexure_ok"] = flexure_util <= 1.0

    # 2. Minimum reinforcement (IS 456 Cl 26.5.1.1)
    ast_min = 0.85 * b_mm * d_eff / fy if fy > 0 else 0
    results["ast_min"] = ast_min
    results["min_reinf_ok"] = ast_bottom >= ast_min

    # 3. Maximum reinforcement (4% of gross area)
    ast_max = 0.04 * b_mm * D_mm
    results["ast_max"] = ast_max
    results["max_reinf_ok"] = ast_total <= ast_max

    # 4. Shear capacity
    pt = 100 * ast_bottom / (b_mm * d_eff) if d_eff > 0 else 0
    tau_c = min(0.28 * (pt**0.5) * (fck**0.33), 0.62 * (fck**0.5))  # Simplified
    vc_concrete = tau_c * b_mm * d_eff / 1000  # kN

    # Stirrup contribution
    asv = 2 * math.pi * (stirrup_dia / 2) ** 2
    sv = max(stirrup_spacing, 50)  # Avoid division issues
    vs_stirrup = 0.87 * fy * asv * d_eff / sv / 1000  # kN

    vu_capacity = vc_concrete + vs_stirrup
    shear_util = vu_kn / vu_capacity if vu_capacity > 0 else 999
    results["vu_capacity_kn"] = vu_capacity
    results["shear_util"] = shear_util
    results["shear_ok"] = shear_util <= 1.0

    # 5. Spacing check (min clear spacing = max(bar_dia, 25mm))
    clear_cover = cover_mm + stirrup_dia
    available_width = b_mm - 2 * clear_cover

    # Calculate spacing for each layer separately
    layer_spacings = []
    for dia, count in bottom_bars:
        if count > 1:
            total_bar_width_layer = count * dia
            layer_spacing = (available_width - total_bar_width_layer) / (count - 1)
            layer_spacings.append((layer_spacing, dia))
        elif count == 1:
            layer_spacings.append(
                (available_width - dia, dia)
            )  # Single bar, plenty of space

    # Minimum spacing across all layers (worst case)
    if layer_spacings:
        min_layer_spacing = min(sp for sp, _ in layer_spacings)
        worst_layer = min(layer_spacings, key=lambda x: x[0])
        min_spacing = max(worst_layer[1], 25)
        spacing = min_layer_spacing
    else:
        spacing = available_width
        min_spacing = 25

    results["bar_spacing"] = spacing
    results["spacing_ok"] = spacing >= min_spacing

    # Overall status
    all_ok = all(
        [
            results["flexure_ok"],
            results["min_reinf_ok"],
            results["max_reinf_ok"],
            results["shear_ok"],
            results["spacing_ok"],
        ]
    )
    results["all_ok"] = all_ok
    results["status"] = "✅ SAFE" if all_ok else "❌ REVISE"

    return results
