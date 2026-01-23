"""Shared rebar layout calculations for 3D visualization.

This module consolidates duplicate implementations from:
- components/ai_workspace.py:606 (calculate_rebar_layout)
- pages/06_multi_format_import.py:292 (calculate_rebar_layout_for_beam)
- pages/_hidden/_10_ai_assistant.py:175 (calculate_rebar_layout)

All three had the same logic with minor variations. This is the canonical version
that combines the best features from all implementations:
- Development length calculation from _10_ai_assistant.py
- Tau_v > 1.0 check from 06_multi_format_import.py
- Compact structure from ai_workspace.py

Created: Session 63 (Jan 23, 2026)
Related: TASK-350
"""

from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any

# Add Python library to path for IS 456 imports
_lib_path = Path(__file__).resolve().parents[2] / "Python"
if str(_lib_path) not in sys.path:
    sys.path.insert(0, str(_lib_path))

# Try to import development length from library (preferred)
_HAS_LIBRARY = False
try:
    from structural_lib.codes.is456.detailing import calculate_development_length

    _HAS_LIBRARY = True
except ImportError:
    pass


# Standard bar diameters and areas (mm² per bar)
BAR_OPTIONS: list[tuple[int, float]] = [
    (12, 113.1),
    (16, 201.1),
    (20, 314.2),
    (25, 490.9),
    (32, 804.2),
]


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
    """Calculate rebar layout for beam visualization.

    This is the consolidated version combining features from 3 duplicate implementations.
    Returns data suitable for 3D rendering (bar positions, stirrup positions, summary).

    Args:
        ast_mm2: Required steel area in mm²
        b_mm: Beam width in mm
        D_mm: Beam depth in mm
        span_mm: Beam span in mm
        vu_kn: Shear force in kN (affects stirrup spacing)
        cover_mm: Clear cover in mm
        stirrup_dia: Stirrup diameter in mm
        fck: Concrete strength in N/mm²
        fy: Steel yield strength in N/mm²

    Returns:
        dict with:
            - bottom_bars: List of (x, y, z) positions
            - top_bars: List of (x, y, z) positions
            - stirrup_positions: List of x positions
            - bar_diameter: Selected bar size (mm)
            - stirrup_diameter: Stirrup diameter (mm)
            - summary: Text summary (e.g., "4T16 (804 mm²)")
            - spacing_summary: Stirrup spacing description
            - ld_tension: Development length (mm) - IS 456 Cl 26.2.1
            - lap_length: Lap splice length (mm) - IS 456 Cl 26.2.5.1
    """
    # Find optimal bar combination (prefer 3-5 bars)
    best_config = None
    for dia, area in BAR_OPTIONS:
        num_bars = math.ceil(ast_mm2 / area) if ast_mm2 > 0 and area > 0 else 2
        if 2 <= num_bars <= 6:
            ast_provided = num_bars * area
            best_config = (dia, num_bars, ast_provided)
            break

    if best_config is None:
        # Fallback to 4T16
        best_config = (16, 4, 4 * 201.1)

    bar_dia, num_bars, ast_provided = best_config

    # Calculate development length per IS 456 Cl 26.2.1
    if _HAS_LIBRARY:
        try:
            ld_tension = calculate_development_length(
                bar_dia=bar_dia,
                fck=fck,
                fy=fy,
                bar_type="deformed",
            )
        except Exception:
            ld_tension = 47 * bar_dia  # Fallback: ~47φ for Fe500 with M25
    else:
        ld_tension = 47 * bar_dia

    # Lap length = 1.3 × Ld for tension splices (IS 456 Cl 26.2.5.1)
    lap_length = 1.3 * ld_tension

    # Calculate bar positions
    edge_dist = cover_mm + stirrup_dia + bar_dia / 2
    z_bottom = edge_dist
    z_top = D_mm - edge_dist
    available_width = b_mm - 2 * edge_dist

    # Bottom bars
    bottom_bars: list[tuple[float, float, float]] = []
    if num_bars == 1:
        bottom_bars = [(0, 0, z_bottom)]
    elif num_bars == 2:
        bottom_bars = [
            (0, -available_width / 2, z_bottom),
            (0, available_width / 2, z_bottom),
        ]
    else:
        spacing = available_width / max(num_bars - 1, 1)
        for i in range(num_bars):
            y = -available_width / 2 + i * spacing
            bottom_bars.append((0, y, z_bottom))

    # Top bars (2 hanger bars)
    top_bars: list[tuple[float, float, float]] = [
        (0, -available_width / 2, z_top),
        (0, available_width / 2, z_top),
    ]

    # Calculate stirrup spacing zones (IS 456 ductile detailing)
    d_mm = D_mm - cover_mm - stirrup_dia - bar_dia / 2
    sv_base = min(200, max(100, 0.75 * d_mm))

    # Adjust for shear stress level
    tau_v = (vu_kn * 1000) / max(b_mm * d_mm, 1)
    if tau_v > 0.5:
        sv_base = min(sv_base, 150)
    if tau_v > 1.0:
        sv_base = min(sv_base, 100)

    # Generate stirrup positions with variable zones
    stirrup_positions: list[float] = []
    zone_2d = 2 * d_mm
    sv_support = sv_base * 0.75  # Tighter at supports

    x = 50.0
    # Zone 1: Near left support
    while x < min(zone_2d, span_mm - 50):
        stirrup_positions.append(x)
        x += sv_support

    # Zone 2: Mid-span
    while x < max(span_mm - zone_2d, zone_2d):
        stirrup_positions.append(x)
        x += sv_base

    # Zone 3: Near right support
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
        "ld_tension": ld_tension,
        "lap_length": lap_length,
        "ast_provided": ast_provided,
    }


def calculate_rebar_layout_simple(
    ast_mm2: float,
    b_mm: float,
    D_mm: float,
    cover_mm: float = 40.0,
    stirrup_dia: float = 8.0,
) -> dict[str, Any]:
    """Simplified rebar layout for quick UI display (no stirrup calculation).

    Use this when you only need bar positions and don't need stirrup zones.

    Args:
        ast_mm2: Required steel area in mm²
        b_mm: Beam width in mm
        D_mm: Beam depth in mm
        cover_mm: Clear cover in mm
        stirrup_dia: Stirrup diameter in mm

    Returns:
        dict with:
            - bar_dia: Selected bar diameter
            - num_bars: Number of bars
            - ast_provided: Actual steel area provided
            - summary: Text summary
    """
    # Find optimal bar combination
    for dia, area in BAR_OPTIONS:
        num_bars = math.ceil(ast_mm2 / area) if ast_mm2 > 0 and area > 0 else 2
        if 2 <= num_bars <= 6:
            ast_provided = num_bars * area
            return {
                "bar_dia": dia,
                "num_bars": num_bars,
                "ast_provided": ast_provided,
                "summary": f"{num_bars}T{dia}",
            }

    # Fallback
    return {
        "bar_dia": 16,
        "num_bars": 4,
        "ast_provided": 4 * 201.1,
        "summary": "4T16",
    }
