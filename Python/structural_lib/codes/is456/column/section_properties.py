"""Gross and elastic transformed properties of a physical column section."""

from __future__ import annotations

from dataclasses import dataclass
from math import fsum, pi

from .positioned_biaxial import PositionedColumnBar


@dataclass(frozen=True)
class ColumnSectionProperties:
    area_mm2: float
    cx_mm: float
    cy_mm: float
    ix_mm4: float
    iy_mm4: float
    ixy_mm4: float


def rectangular_properties(b_mm: float, D_mm: float) -> ColumnSectionProperties:
    return ColumnSectionProperties(
        b_mm * D_mm,
        b_mm / 2,
        D_mm / 2,
        b_mm * D_mm**3 / 12,
        D_mm * b_mm**3 / 12,
        0.0,
    )


def circular_properties(diameter_mm: float) -> ColumnSectionProperties:
    inertia = pi * diameter_mm**4 / 64
    return ColumnSectionProperties(
        pi * diameter_mm**2 / 4,
        diameter_mm / 2,
        diameter_mm / 2,
        inertia,
        inertia,
        0.0,
    )


def transformed_properties(
    gross: ColumnSectionProperties,
    bars: tuple[PositionedColumnBar, ...],
    modular_ratio: float,
) -> ColumnSectionProperties:
    """Add the net equivalent concrete area of the steel and shift to its centroid."""
    ratio = modular_ratio - 1
    components = [
        (gross.area_mm2, gross.cx_mm, gross.cy_mm, gross.ix_mm4, gross.iy_mm4)
    ]
    for bar in bars:
        local_inertia = ratio * pi * bar.diameter_mm**4 / 64
        components.append(
            (
                ratio * bar.area_mm2,
                bar.x_from_left_mm,
                bar.y_from_top_mm,
                local_inertia,
                local_inertia,
            )
        )
    area = fsum(item[0] for item in components)
    cx = fsum(a * x for a, x, _, _, _ in components) / area
    cy = fsum(a * y for a, _, y, _, _ in components) / area
    return ColumnSectionProperties(
        area,
        cx,
        cy,
        fsum(ix + a * (y - cy) ** 2 for a, _, y, ix, _ in components),
        fsum(iy + a * (x - cx) ** 2 for a, x, _, _, iy in components),
        fsum(a * (x - cx) * (y - cy) for a, x, y, _, _ in components),
    )
