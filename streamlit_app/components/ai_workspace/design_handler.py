# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Beam design computation handler.

Extracted from ai_workspace.py (TASK-508).
Contains rebar layout calculation, single beam design,
and batch beam design functions.
"""

from __future__ import annotations

import math
from typing import Any

import pandas as pd
import streamlit as st

from .workspace_state import BAR_OPTIONS

# Import shared utilities (Session 63 consolidation)
try:
    from utils.rebar_layout import calculate_rebar_layout as shared_rebar_layout

    SHARED_REBAR_AVAILABLE = True
except ImportError:
    SHARED_REBAR_AVAILABLE = False

# Import shared batch design utilities (Session 63 consolidation)
try:
    from utils.batch_design import (
        design_beam_row as shared_design_beam_row,
        design_all_beams_df as shared_design_all_beams,
    )

    SHARED_BATCH_DESIGN_AVAILABLE = True
except ImportError:
    SHARED_BATCH_DESIGN_AVAILABLE = False

# Import cached design from api_wrapper (used by multi-format import)
try:
    from utils.api_wrapper import cached_design

    CACHED_DESIGN_AVAILABLE = True
except ImportError:
    CACHED_DESIGN_AVAILABLE = False


def calculate_rebar_layout(
    ast_mm2: float,
    b_mm: float,
    D_mm: float,
    span_mm: float,
    vu_kn: float = 50.0,
    cover_mm: float = 40.0,
    stirrup_dia: float = 8.0,
    fck: float = 25.0,
    fy: float = 500.0,
) -> dict[str, Any]:
    """Calculate rebar layout for visualization.

    Session 63: Now uses shared implementation from utils/rebar_layout.py
    """
    if SHARED_REBAR_AVAILABLE:
        return shared_rebar_layout(
            ast_mm2=ast_mm2,
            b_mm=b_mm,
            D_mm=D_mm,
            span_mm=span_mm,
            vu_kn=vu_kn,
            cover_mm=cover_mm,
            stirrup_dia=stirrup_dia,
            fck=fck,
            fy=fy,
        )

    # Fallback implementation (legacy, for backward compatibility)
    # Uses module-level BAR_OPTIONS (imported from workspace_state)
    best_config = None
    for dia, area in BAR_OPTIONS:
        num_bars = math.ceil(ast_mm2 / area) if ast_mm2 > 0 else 2
        if 2 <= num_bars <= 6:
            best_config = (dia, num_bars, num_bars * area)
            break

    if best_config is None:
        best_config = (16, 3, 3 * 201.1)

    bar_dia, num_bars, ast_provided = best_config

    edge_dist = cover_mm + stirrup_dia + bar_dia / 2
    z_bottom = edge_dist
    z_top = D_mm - edge_dist
    available_width = b_mm - 2 * edge_dist

    bottom_bars = []
    spacing = available_width / max(num_bars - 1, 1)
    for i in range(num_bars):
        y = -available_width / 2 + i * spacing
        bottom_bars.append((0, y, z_bottom))

    top_bars = [
        (0, -available_width / 2, z_top),
        (0, available_width / 2, z_top),
    ]

    d_mm = D_mm - cover_mm - stirrup_dia - bar_dia / 2
    sv_base = min(200, max(100, 0.75 * d_mm))
    tau_v = (vu_kn * 1000) / max(b_mm * d_mm, 1)
    if tau_v > 0.5:
        sv_base = min(sv_base, 150)

    stirrup_positions = []
    zone_2d = 2 * d_mm
    sv_support = sv_base * 0.75

    x = 50
    while x < min(zone_2d, span_mm - 50):
        stirrup_positions.append(x)
        x += sv_support
    while x < max(span_mm - zone_2d, zone_2d):
        stirrup_positions.append(x)
        x += sv_base
    while x < span_mm - 50:
        stirrup_positions.append(x)
        x += sv_support

    return {
        "bottom_bars": bottom_bars,
        "top_bars": top_bars,
        "stirrup_positions": stirrup_positions,
        "bar_diameter": bar_dia,
        "stirrup_diameter": stirrup_dia,
        "summary": f"{num_bars}T{bar_dia} ({ast_provided:.0f} mm²)",
        "spacing_summary": f"Stirrups: Ø{stirrup_dia}@{sv_support:.0f}mm (ends), @{sv_base:.0f}mm (mid)",
    }


def design_beam_row(row: pd.Series) -> dict[str, Any]:
    """Design a single beam and return results.

    Uses shared batch_design implementation when available.
    Falls back to local implementation for robustness.

    Session 63: Consolidated to use utils/batch_design.py
    """
    # Use shared implementation when available
    if SHARED_BATCH_DESIGN_AVAILABLE:
        result = shared_design_beam_row(row)
        # Ensure backward-compatible format (simpler keys for local use)
        return {
            "is_safe": result.get("is_safe", False),
            "ast_req": result.get("ast_req", 0),
            "utilization": result.get("utilization", 0),
            "status": result.get("status", "❌ Error"),
        }

    # Fallback to local implementation
    try:
        b_mm = float(row["b_mm"])
        D_mm = float(row["D_mm"])
        d_mm = D_mm - float(row.get("cover_mm", 50)) - 8  # cover + stirrup radius
        fck = float(row["fck"])
        fy = float(row["fy"])
        mu_knm = float(row["mu_knm"])
        vu_kn = float(row["vu_kn"])

        # Validate dimensions before design
        if D_mm < 100 or b_mm < 100:
            return {
                "is_safe": False,
                "ast_req": 0,
                "utilization": float("inf"),
                "status": f"❌ Invalid dims: {b_mm}x{D_mm}",
            }

        # Use cached_design if available (consistent with multi-format import)
        if CACHED_DESIGN_AVAILABLE:
            result = cached_design(
                mu_knm=mu_knm,
                vu_kn=vu_kn,
                b_mm=b_mm,
                D_mm=D_mm,
                d_mm=d_mm,
                fck_nmm2=fck,
                fy_nmm2=fy,
            )
            # cached_design returns dict, not object
            is_safe = result.get("is_safe", False)
            flexure = result.get("flexure", {})
            ast_req = flexure.get("ast_required", 0) if isinstance(flexure, dict) else 0
            utilization = result.get("governing_utilization", 0)
        else:
            # Fallback to direct API call
            from structural_lib import api as structural_api

            result = structural_api.design_beam_is456(
                units="IS456",
                b_mm=b_mm,
                D_mm=D_mm,
                d_mm=d_mm,
                fck_nmm2=fck,
                fy_nmm2=fy,
                mu_knm=mu_knm,
                vu_kn=vu_kn,
            )
            # API returns object with attributes
            is_safe = result.is_ok
            ast_req = result.flexure.ast_required
            utilization = result.governing_utilization

        return {
            "is_safe": is_safe,
            "ast_req": ast_req,
            "utilization": utilization,
            "status": "✅ OK" if is_safe else "❌ FAIL",
        }
    except Exception as e:
        return {
            "is_safe": False,
            "ast_req": 0,
            "utilization": 0,
            "status": f"❌ {str(e)[:30]}",
        }


def design_all_beams_ws() -> pd.DataFrame:
    """Design all beams in the workspace."""
    df = st.session_state.ws_beams_df
    if df is None or df.empty:
        return pd.DataFrame()

    results = []
    for idx, row in df.iterrows():
        design = design_beam_row(row)
        result_row = {
            "beam_id": row["beam_id"],
            "story": row["story"],
            "b_mm": row["b_mm"],
            "D_mm": row["D_mm"],
            "span_mm": row["span_mm"],
            "mu_knm": row["mu_knm"],
            "vu_kn": row["vu_kn"],
            "fck": row["fck"],
            "fy": row["fy"],
            "cover_mm": row["cover_mm"],
            "ast_req": design["ast_req"],
            "utilization": design["utilization"],
            "is_safe": design["is_safe"],
            "status": design["status"],
        }
        # Preserve coordinate columns for 3D view
        for coord in ["x1", "y1", "z1", "x2", "y2", "z2"]:
            if coord in row:
                result_row[coord] = row[coord]
        results.append(result_row)

    return pd.DataFrame(results)
