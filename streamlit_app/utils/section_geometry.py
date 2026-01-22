"""Shared section geometry calculations for consistent bar positioning.

This module centralizes bar position calculations to prevent code duplication
and ensure consistent behavior across all section views:
- Rebar Editor live preview
- Unified Editor 2D/3D view
- Table View section preview

Created: Session 32 (Jan 22, 2026)
Issue: Bars appeared outside stirrups due to inconsistent formulas.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import NamedTuple

    class BarPosition(NamedTuple):
        """Bar position and diameter."""

        x: float
        y: float
        dia: float


def calculate_bar_positions(
    b_mm: float,
    D_mm: float,
    cover_mm: float,
    stirrup_dia: float,
    l1_count: int,
    l1_dia: float,
    l2_count: int = 0,
    l2_dia: float = 0,
    top_count: int = 2,
    top_dia: float = 12,
    layer_gap: float = 25.0,
) -> tuple[list[tuple[float, float, float]], list[tuple[float, float, float]]]:
    """Calculate bar positions for cross-section visualization.

    Args:
        b_mm: Section width in mm
        D_mm: Section depth in mm
        cover_mm: Clear cover in mm
        stirrup_dia: Stirrup diameter in mm (actual value, not hardcoded!)
        l1_count: Number of bars in bottom layer 1
        l1_dia: Diameter of bottom layer 1 bars in mm
        l2_count: Number of bars in bottom layer 2 (optional)
        l2_dia: Diameter of bottom layer 2 bars in mm (optional)
        top_count: Number of top bars
        top_dia: Diameter of top bars in mm
        layer_gap: Vertical gap between bar layers in mm (default 25)

    Returns:
        Tuple of (bottom_bars, top_bars) where each is a list of (x, y, dia) tuples.

    Example:
        >>> bottom, top = calculate_bar_positions(
        ...     b_mm=300, D_mm=450, cover_mm=40, stirrup_dia=8,
        ...     l1_count=3, l1_dia=16, l2_count=0, l2_dia=0,
        ...     top_count=2, top_dia=12
        ... )
        >>> len(bottom)
        3
        >>> len(top)
        2
    """
    bottom_bars: list[tuple[float, float, float]] = []
    top_bars: list[tuple[float, float, float]] = []

    # ----- Bottom Layer 1 -----
    layer1_y = cover_mm + stirrup_dia + l1_dia / 2
    x_start_1 = cover_mm + stirrup_dia + l1_dia / 2
    x_end_1 = b_mm - cover_mm - stirrup_dia - l1_dia / 2

    if l1_count > 1:
        spacing_1 = (x_end_1 - x_start_1) / (l1_count - 1)
        for i in range(l1_count):
            bottom_bars.append((x_start_1 + i * spacing_1, layer1_y, l1_dia))
    elif l1_count == 1:
        bottom_bars.append((b_mm / 2, layer1_y, l1_dia))

    # ----- Bottom Layer 2 -----
    if l2_count > 0 and l2_dia > 0:
        layer2_y = layer1_y + l1_dia / 2 + layer_gap + l2_dia / 2
        x_start_2 = cover_mm + stirrup_dia + l2_dia / 2
        x_end_2 = b_mm - cover_mm - stirrup_dia - l2_dia / 2

        if l2_count > 1:
            spacing_2 = (x_end_2 - x_start_2) / (l2_count - 1)
            for i in range(l2_count):
                bottom_bars.append((x_start_2 + i * spacing_2, layer2_y, l2_dia))
        elif l2_count == 1:
            bottom_bars.append((b_mm / 2, layer2_y, l2_dia))

    # ----- Top Bars -----
    top_y = D_mm - cover_mm - stirrup_dia - top_dia / 2
    x_start_t = cover_mm + stirrup_dia + top_dia / 2
    x_end_t = b_mm - cover_mm - stirrup_dia - top_dia / 2

    if top_count > 1:
        spacing_t = (x_end_t - x_start_t) / (top_count - 1)
        for i in range(top_count):
            top_bars.append((x_start_t + i * spacing_t, top_y, top_dia))
    elif top_count == 1:
        top_bars.append((b_mm / 2, top_y, top_dia))

    return bottom_bars, top_bars


def calculate_utilization(mu_actual: float, mu_capacity: float) -> float:
    """Calculate utilization ratio as percentage.

    Args:
        mu_actual: Applied moment (kN·m)
        mu_capacity: Moment capacity (kN·m)

    Returns:
        Utilization percentage (0-100+). Values >100 indicate failure.
    """
    if mu_capacity <= 0:
        return 999.0  # Indicates error
    return (mu_actual / mu_capacity) * 100


def get_utilization_color(utilization: float) -> str:
    """Get color code for utilization value.

    Args:
        utilization: Utilization percentage

    Returns:
        Hex color code:
        - Green (#10b981): 0-70% (efficient)
        - Yellow (#f59e0b): 70-90% (good)
        - Orange (#f97316): 90-100% (borderline)
        - Red (#ef4444): >100% (fail)
    """
    if utilization <= 70:
        return "#10b981"  # Green - efficient
    elif utilization <= 90:
        return "#f59e0b"  # Yellow - good
    elif utilization <= 100:
        return "#f97316"  # Orange - borderline
    else:
        return "#ef4444"  # Red - fail
