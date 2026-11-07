"""Actual-bar elastic T service section, in mm and N/mm².

IS456 6.2.3, 23.2.1 and Annex F. Tension concrete is ignored; concrete
displaced by compression steel is removed. No rectangular stiffness,
tension-stiffening credit or Annex-C time-dependent result is implied.
"""

from __future__ import annotations

import math

from structural_lib.codes.is456.tables import _get_tc_value_for_derived_reinforcement


def cracked_t_section(
    web_width_mm: float,
    flange_width_mm: float,
    flange_thickness_mm: float,
    depth_mm: float,
    layers: tuple[tuple[float, float], ...],
    concrete_modulus_nmm2: float,
    steel_modulus_nmm2: float,
) -> tuple[float, float]:
    """Neutral axis and transformed Icr, allowing NA in flange or web.

    ``layers`` contains actual (depth from flange top, steel area), with no
    face-based inference about whether a layer is in tension/compression.
    """
    dimensions = (
        web_width_mm,
        flange_width_mm,
        flange_thickness_mm,
        depth_mm,
        concrete_modulus_nmm2,
        steel_modulus_nmm2,
    )
    if (
        not all(math.isfinite(v) and v > 0 for v in dimensions)
        or flange_width_mm < web_width_mm
        or flange_thickness_mm >= depth_mm
        or steel_modulus_nmm2 <= concrete_modulus_nmm2
        or not layers
        or any(
            not math.isfinite(y)
            or not 0 < y < depth_mm
            or not math.isfinite(a)
            or a <= 0
            for y, a in layers
        )
    ):
        raise ValueError(
            "A finite physical T section and actual steel layers are required"
        )
    ratio = steel_modulus_nmm2 / concrete_modulus_nmm2

    def concrete_first(axis: float) -> float:
        flange_depth = min(axis, flange_thickness_mm)
        return (
            flange_width_mm * flange_depth * (axis - flange_depth / 2)
            + web_width_mm * max(0.0, axis - flange_thickness_mm) ** 2 / 2
        )

    lo, hi = 0.0, depth_mm
    for _ in range(140):
        axis = (lo + hi) / 2
        residual = concrete_first(axis) + math.fsum(
            (ratio - int(y < axis)) * area * (axis - y) for y, area in layers
        )
        if residual > 0:
            hi = axis
        else:
            lo = axis
    axis = (lo + hi) / 2
    web_compression = max(0.0, axis - flange_thickness_mm)
    inertia = (
        flange_width_mm * (axis**3 - web_compression**3) / 3
        + web_width_mm * web_compression**3 / 3
        + math.fsum(
            (ratio - int(y < axis)) * area * (y - axis) ** 2 for y, area in layers
        )
    )
    if inertia <= 0:
        raise ValueError("No positive cracked T stiffness for the supplied layers")
    return axis, inertia


def gross_t_section(
    web_width_mm: float,
    flange_width_mm: float,
    flange_thickness_mm: float,
    depth_mm: float,
) -> tuple[float, float, float]:
    """Concrete gross area, centroid from flange top, and centroidal inertia."""
    af = flange_width_mm * flange_thickness_mm
    aw = web_width_mm * (depth_mm - flange_thickness_mm)
    yf, yw = flange_thickness_mm / 2, (depth_mm + flange_thickness_mm) / 2
    centroid = (af * yf + aw * yw) / (af + aw)
    inertia = (
        flange_width_mm * flange_thickness_mm**3 / 12
        + af * (yf - centroid) ** 2
        + web_width_mm * (depth_mm - flange_thickness_mm) ** 3 / 12
        + aw * (yw - centroid) ** 2
    )
    return af + aw, centroid, inertia


def flange_strip_limits(depth_mm: float, effective_depth_mm: float) -> dict[str, float]:
    """IS456 26.5.2.1,26.5.2.2 and26.3.3 high-strength slab-strip limits."""
    if not 0 < effective_depth_mm < depth_mm:
        raise ValueError(
            "Require actual slab-strip effective depth within its thickness"
        )
    return {
        "minimum_area_per_m_each_direction_mm2": 0.0012 * 1000 * depth_mm,
        "maximum_main_spacing_mm": min(3 * effective_depth_mm, 300),
        "maximum_distribution_spacing_mm": min(5 * effective_depth_mm, 450),
        "maximum_bar_diameter_mm": depth_mm / 8,
    }


def conservative_strip_shear(
    line_load_n_per_mm: float,
    span_mm: float,
    width_mm: float,
    effective_depth_mm: float,
    tension_area_mm2: float,
) -> tuple[float, float]:
    """M25 local slab strip,40.2/Table19; no beneficial depth enhancement.

    Full load on one span bounds the selected two-span shear reaction. The
    slab strip does not acquire the beam minimum-transverse-link obligation.
    """
    percentage = 100 * tension_area_mm2 / (width_mm * effective_depth_mm)
    return (
        line_load_n_per_mm * span_mm / (width_mm * effective_depth_mm),
        _get_tc_value_for_derived_reinforcement(25, percentage),
    )


def lateral_stability_length_limit(
    breadth_mm: float, effective_depth_mm: float
) -> float:
    """IS45623.3 ordinary simply-supported/continuous clear restraint limit."""
    if min(breadth_mm, effective_depth_mm) <= 0:
        raise ValueError("Positive actual breadth and effective depth are required")
    return min(60 * breadth_mm, 250 * breadth_mm**2 / effective_depth_mm)
