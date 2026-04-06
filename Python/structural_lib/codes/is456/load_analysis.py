# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       load_analysis
Description:  BMD/SFD computation for simply supported and cantilever beams
IS456:        Structural analysis fundamentals (Chapter 22)

This module provides pure functions for computing Bending Moment Diagrams (BMD)
and Shear Force Diagrams (SFD) for common beam configurations and load cases.

Supported load types:
- UDL (Uniformly Distributed Load)
- Point Load (Concentrated Load)
- Triangular Load (Varying intensity)
- Applied Moment

Supported support conditions:
- Simply Supported
- Cantilever

Sign Conventions (standard structural engineering):
- Bending moment: Positive = sagging (tension at bottom)
- Shear force: Positive = upward force on left face of section

Units: All functions use explicit mm/kN/kN·m units.
"""

from __future__ import annotations

from typing import Literal

from structural_lib.core.data_types import (
    CriticalPoint,
    LoadDefinition,
    LoadDiagramResult,
    LoadType,
)

# =============================================================================
# Constants
# =============================================================================

DEFAULT_NUM_POINTS = 101  # Default number of points for discretization


# =============================================================================
# Core Computation Functions
# =============================================================================


def compute_udl_bmd_sfd(
    span_mm: float,
    w_kn_per_m: float,
    num_points: int = DEFAULT_NUM_POINTS,
) -> tuple[list[float], list[float], list[float]]:
    """Compute BMD and SFD for UDL on simply supported beam.

    Standard formulas:
    - Reactions: R_A = R_B = wL/2
    - Shear: V(x) = R_A - w·x = wL/2 - w·x
    - Moment: M(x) = R_A·x - w·x²/2 = wLx/2 - wx²/2

    Args:
        span_mm: Span length (mm)
        w_kn_per_m: UDL intensity (kN/m)
        num_points: Number of discretization points

    Returns:
        Tuple of (positions_mm, bmd_knm, sfd_kn)

    Example:
        >>> pos, bmd, sfd = compute_udl_bmd_sfd(6000, 20)
        >>> max(bmd)  # Max moment at midspan
        90.0
    """
    span_m = span_mm / 1000.0  # Convert to meters
    reaction = w_kn_per_m * span_m / 2.0  # kN

    positions_mm = [span_mm * i / (num_points - 1) for i in range(num_points)]
    bmd_knm: list[float] = []
    sfd_kn: list[float] = []

    for x_mm in positions_mm:
        x_m = x_mm / 1000.0
        # Shear: V(x) = wL/2 - w·x
        shear = reaction - w_kn_per_m * x_m
        sfd_kn.append(shear)

        # Moment: M(x) = wLx/2 - wx²/2
        moment = reaction * x_m - w_kn_per_m * x_m * x_m / 2.0
        bmd_knm.append(moment)

    return positions_mm, bmd_knm, sfd_kn


def compute_point_load_bmd_sfd(
    span_mm: float,
    p_kn: float,
    a_mm: float,
    num_points: int = DEFAULT_NUM_POINTS,
) -> tuple[list[float], list[float], list[float]]:
    """Compute BMD and SFD for point load on simply supported beam.

    Load P at distance a from left support (position a, b = L - a).

    Standard formulas:
    - R_A = Pb/L, R_B = Pa/L
    - Shear: V(x) = R_A for x < a, V(x) = R_A - P for x > a
    - Moment: M(x) = R_A·x for x < a, M(x) = R_A·x - P(x-a) for x > a

    Args:
        span_mm: Span length (mm)
        p_kn: Point load magnitude (kN)
        a_mm: Distance from left support (mm)
        num_points: Number of discretization points

    Returns:
        Tuple of (positions_mm, bmd_knm, sfd_kn)
    """
    span_m = span_mm / 1000.0
    a_m = a_mm / 1000.0
    b_m = span_m - a_m

    # Reactions
    r_a = p_kn * b_m / span_m
    # r_b = p_kn * a_m / span_m  # Not used directly

    positions_mm = [span_mm * i / (num_points - 1) for i in range(num_points)]
    bmd_knm: list[float] = []
    sfd_kn: list[float] = []

    for x_mm in positions_mm:
        x_m = x_mm / 1000.0

        if x_m <= a_m:
            shear = r_a
            moment = r_a * x_m
        else:
            shear = r_a - p_kn
            moment = r_a * x_m - p_kn * (x_m - a_m)

        sfd_kn.append(shear)
        bmd_knm.append(moment)

    return positions_mm, bmd_knm, sfd_kn


def compute_cantilever_udl_bmd_sfd(
    span_mm: float,
    w_kn_per_m: float,
    num_points: int = DEFAULT_NUM_POINTS,
) -> tuple[list[float], list[float], list[float]]:
    """Compute BMD and SFD for UDL on cantilever beam (fixed at x=0).

    Standard formulas (fixed at left, free at right):
    - Shear: V(x) = -w(L-x)
    - Moment: M(x) = -w(L-x)²/2

    Sign convention: Fixed at left (x=0), free at right (x=L).
    Moment is negative (hogging) throughout for downward load.

    Args:
        span_mm: Span length (mm)
        w_kn_per_m: UDL intensity (kN/m)
        num_points: Number of discretization points

    Returns:
        Tuple of (positions_mm, bmd_knm, sfd_kn)
    """
    span_m = span_mm / 1000.0

    positions_mm = [span_mm * i / (num_points - 1) for i in range(num_points)]
    bmd_knm: list[float] = []
    sfd_kn: list[float] = []

    for x_mm in positions_mm:
        x_m = x_mm / 1000.0
        remaining = span_m - x_m

        # Shear: V(x) = -w(L-x) (negative = downward)
        shear = -w_kn_per_m * remaining
        sfd_kn.append(shear)

        # Moment: M(x) = -w(L-x)²/2 (negative = hogging)
        moment = -w_kn_per_m * remaining * remaining / 2.0
        bmd_knm.append(moment)

    return positions_mm, bmd_knm, sfd_kn


def compute_cantilever_point_load_bmd_sfd(
    span_mm: float,
    p_kn: float,
    a_mm: float,
    num_points: int = DEFAULT_NUM_POINTS,
) -> tuple[list[float], list[float], list[float]]:
    """Compute BMD and SFD for point load on cantilever beam.

    Fixed at left (x=0), point load at distance a from fixed end.

    Standard formulas:
    - Shear: V(x) = -P for x < a, V(x) = 0 for x > a
    - Moment: M(x) = -P(a-x) for x < a, M(x) = 0 for x > a

    Args:
        span_mm: Span length (mm)
        p_kn: Point load magnitude (kN)
        a_mm: Distance from fixed end (mm)
        num_points: Number of discretization points

    Returns:
        Tuple of (positions_mm, bmd_knm, sfd_kn)
    """
    # span_m not needed for cantilever point load
    a_m = a_mm / 1000.0

    positions_mm = [span_mm * i / (num_points - 1) for i in range(num_points)]
    bmd_knm: list[float] = []
    sfd_kn: list[float] = []

    for x_mm in positions_mm:
        x_m = x_mm / 1000.0

        if x_m <= a_m:
            shear = -p_kn
            moment = -p_kn * (a_m - x_m)
        else:
            shear = 0.0
            moment = 0.0

        sfd_kn.append(shear)
        bmd_knm.append(moment)

    return positions_mm, bmd_knm, sfd_kn


def compute_triangular_load_bmd_sfd(
    span_mm: float,
    w_max_kn_per_m: float,
    ascending: bool = True,
    num_points: int = DEFAULT_NUM_POINTS,
) -> tuple[list[float], list[float], list[float], float]:
    """Compute BMD and SFD for triangular load on simply supported beam.

    Linearly varying load from zero at one end to w_max at the other.

    Ascending (0 -> w_max, left to right):
    - w(x) = w_max * x / L
    - Total load W = w_max * L / 2
    - R_A = w_max * L / 6,  R_B = w_max * L / 3
    - V(x) = R_A - w_max * x^2 / (2L)
    - M(x) = R_A * x - w_max * x^3 / (6L)
    - M_max at x = L / sqrt(3),  M_max = w_max * L^2 / (9 * sqrt(3))

    Descending (w_max -> 0, left to right):
    - w(x) = w_max * (1 - x/L)
    - R_A = w_max * L / 3,  R_B = w_max * L / 6
    - V(x) = R_A - w_max * x + w_max * x^2 / (2L)
    - M(x) = R_A * x - w_max * x^2 / 2 + w_max * x^3 / (6L)
    - M_max at x = L * (1 - 1/sqrt(3))

    Args:
        span_mm: Span length (mm), must be > 0
        w_max_kn_per_m: Maximum load intensity (kN/m), must be > 0
        ascending: If True, load increases left to right (0 -> w_max).
                   If False, load decreases left to right (w_max -> 0).
        num_points: Number of discretization points

    Returns:
        Tuple of (positions_mm, bmd_knm, sfd_kn, x_mmax_mm) where
        x_mmax_mm is the position of maximum bending moment (mm).

    Raises:
        ValueError: If span_mm <= 0 or w_max_kn_per_m <= 0
    """
    if span_mm <= 0:
        raise ValueError(f"Span must be positive, got {span_mm}")
    if w_max_kn_per_m <= 0:
        raise ValueError(f"w_max must be positive, got {w_max_kn_per_m}")

    import math

    span_m = span_mm / 1000.0

    positions_mm = [span_mm * i / (num_points - 1) for i in range(num_points)]
    bmd_knm: list[float] = []
    sfd_kn: list[float] = []

    if ascending:
        # Ascending: load goes from 0 at left to w_max at right
        # R_A = w_max * L / 6, R_B = w_max * L / 3
        r_a_kn = w_max_kn_per_m * span_m / 6.0

        for x_mm in positions_mm:
            x_m = x_mm / 1000.0

            # V(x) = R_A - w_max * x^2 / (2L)
            shear = r_a_kn - w_max_kn_per_m * x_m * x_m / (2.0 * span_m)
            sfd_kn.append(shear)

            # M(x) = R_A * x - w_max * x^3 / (6L)
            moment = r_a_kn * x_m - w_max_kn_per_m * x_m**3 / (6.0 * span_m)
            bmd_knm.append(moment)

        # M_max at x = L / sqrt(3)
        x_mmax_mm = span_mm / math.sqrt(3.0)

    else:
        # Descending: load goes from w_max at left to 0 at right
        # R_A = w_max * L / 3, R_B = w_max * L / 6
        r_a_kn = w_max_kn_per_m * span_m / 3.0

        for x_mm in positions_mm:
            x_m = x_mm / 1000.0

            # V(x) = R_A - w_max * x + w_max * x^2 / (2L)
            shear = (
                r_a_kn
                - w_max_kn_per_m * x_m
                + w_max_kn_per_m * x_m * x_m / (2.0 * span_m)
            )
            sfd_kn.append(shear)

            # M(x) = R_A * x - w_max * x^2 / 2 + w_max * x^3 / (6L)
            moment = (
                r_a_kn * x_m
                - w_max_kn_per_m * x_m * x_m / 2.0
                + w_max_kn_per_m * x_m**3 / (6.0 * span_m)
            )
            bmd_knm.append(moment)

        # M_max at x = L * (1 - 1/sqrt(3))
        x_mmax_mm = span_mm * (1.0 - 1.0 / math.sqrt(3.0))

    return positions_mm, bmd_knm, sfd_kn, x_mmax_mm


def compute_applied_moment_bmd_sfd(
    span_mm: float,
    m_knm: float,
    a_mm: float | None = None,
    num_points: int = DEFAULT_NUM_POINTS,
) -> tuple[list[float], list[float], list[float]]:
    """Compute BMD and SFD for applied concentrated moment on simply supported beam.

    A clockwise moment M applied at distance a from left support.

    Standard formulas:
    - Reactions: R_A = -M/L (down), R_B = M/L (up)
    - V(x) = R_A = -M/L  (constant, no discontinuity)
    - M(x) = R_A * x = -M*x/L            for 0 <= x < a
    - M(x) = R_A * x + M = M*(1 - x/L)   for a <= x <= L

    The BMD is piecewise linear with a jump of magnitude M at x = a.

    Args:
        span_mm: Span length (mm), must be > 0
        m_knm: Applied moment magnitude (kN*m). Positive = clockwise.
        a_mm: Position from left support (mm). Defaults to midspan (L/2).
              Must satisfy 0 <= a_mm <= span_mm.
        num_points: Number of discretization points

    Returns:
        Tuple of (positions_mm, bmd_knm, sfd_kn)

    Raises:
        ValueError: If span_mm <= 0 or a_mm outside [0, span_mm]
    """
    if span_mm <= 0:
        raise ValueError(f"Span must be positive, got {span_mm}")

    if a_mm is None:
        a_mm = span_mm / 2.0

    if a_mm < 0 or a_mm > span_mm:
        raise ValueError(f"Moment position a_mm must be in [0, {span_mm}], got {a_mm}")

    span_m = span_mm / 1000.0
    a_m = a_mm / 1000.0

    # R_A = -M/L (downward), R_B = M/L (upward)
    r_a_kn = -m_knm / span_m  # kN (negative = downward)

    positions_mm = [span_mm * i / (num_points - 1) for i in range(num_points)]
    bmd_knm: list[float] = []
    sfd_kn: list[float] = []

    for x_mm in positions_mm:
        x_m = x_mm / 1000.0

        # Shear is constant: V(x) = R_A = -M/L
        sfd_kn.append(r_a_kn)

        if x_m < a_m:
            # BM(x) = R_A * x = -M*x/L
            moment = r_a_kn * x_m
        else:
            # BM(x) = R_A * x + M = M*(1 - x/L)
            moment = r_a_kn * x_m + m_knm

        bmd_knm.append(moment)

    return positions_mm, bmd_knm, sfd_kn


# =============================================================================
# Combined Load Analysis
# =============================================================================


def _superimpose_diagrams(
    base_bmd: list[float],
    base_sfd: list[float],
    add_bmd: list[float],
    add_sfd: list[float],
) -> tuple[list[float], list[float]]:
    """Superimpose two sets of BMD/SFD diagrams (principle of superposition)."""
    combined_bmd = [b + a for b, a in zip(base_bmd, add_bmd, strict=True)]
    combined_sfd = [b + a for b, a in zip(base_sfd, add_sfd, strict=True)]
    return combined_bmd, combined_sfd


def _find_critical_points(
    positions_mm: list[float],
    bmd_knm: list[float],
    sfd_kn: list[float],
) -> list[CriticalPoint]:
    """Find critical points (max, min, zero crossings) on BMD/SFD."""
    critical_points: list[CriticalPoint] = []

    if not positions_mm:
        return critical_points

    # Find max/min BMD
    max_bm_idx = max(range(len(bmd_knm)), key=lambda i: bmd_knm[i])
    min_bm_idx = min(range(len(bmd_knm)), key=lambda i: bmd_knm[i])

    critical_points.append(
        CriticalPoint(
            position_mm=positions_mm[max_bm_idx],
            point_type="max_bm",
            bm_knm=bmd_knm[max_bm_idx],
            sf_kn=sfd_kn[max_bm_idx],
        )
    )

    if min_bm_idx != max_bm_idx:
        critical_points.append(
            CriticalPoint(
                position_mm=positions_mm[min_bm_idx],
                point_type="min_bm",
                bm_knm=bmd_knm[min_bm_idx],
                sf_kn=sfd_kn[min_bm_idx],
            )
        )

    # Find max/min SF
    max_sf_idx = max(range(len(sfd_kn)), key=lambda i: sfd_kn[i])
    min_sf_idx = min(range(len(sfd_kn)), key=lambda i: sfd_kn[i])

    critical_points.append(
        CriticalPoint(
            position_mm=positions_mm[max_sf_idx],
            point_type="max_sf",
            bm_knm=bmd_knm[max_sf_idx],
            sf_kn=sfd_kn[max_sf_idx],
        )
    )

    if min_sf_idx != max_sf_idx:
        critical_points.append(
            CriticalPoint(
                position_mm=positions_mm[min_sf_idx],
                point_type="min_sf",
                bm_knm=bmd_knm[min_sf_idx],
                sf_kn=sfd_kn[min_sf_idx],
            )
        )

    # Find zero crossing of SFD (location of max moment for simply supported)
    for i in range(len(sfd_kn) - 1):
        if sfd_kn[i] * sfd_kn[i + 1] < 0:  # Sign change
            # Linear interpolation for more accurate position
            x1, x2 = positions_mm[i], positions_mm[i + 1]
            v1, v2 = sfd_kn[i], sfd_kn[i + 1]
            x_zero = x1 - v1 * (x2 - x1) / (v2 - v1)

            # Interpolate moment at this point
            m1, m2 = bmd_knm[i], bmd_knm[i + 1]
            m_zero = m1 + (m2 - m1) * (x_zero - x1) / (x2 - x1)

            critical_points.append(
                CriticalPoint(
                    position_mm=x_zero,
                    point_type="zero_sf",
                    bm_knm=m_zero,
                    sf_kn=0.0,
                )
            )

    return critical_points


# =============================================================================
# Public API Function
# =============================================================================


def compute_bmd_sfd(
    span_mm: float,
    support_condition: Literal["simply_supported", "cantilever"],
    loads: list[LoadDefinition],
    num_points: int = DEFAULT_NUM_POINTS,
) -> LoadDiagramResult:
    """Compute BMD and SFD for a beam with specified loads.

    Uses principle of superposition to combine multiple load effects.

    Args:
        span_mm: Span length (mm)
        support_condition: "simply_supported" or "cantilever"
        loads: List of LoadDefinition objects
        num_points: Number of discretization points (default 101)

    Returns:
        LoadDiagramResult with positions, BMD, SFD, and critical points

    Raises:
        ValueError: If span is non-positive or support_condition invalid

    Example:
        >>> from structural_lib.core.data_types import LoadDefinition, LoadType
        >>> loads = [LoadDefinition(LoadType.UDL, magnitude=20.0)]
        >>> result = compute_bmd_sfd(6000, "simply_supported", loads)
        >>> print(f"Max moment: {result.max_bm_knm:.1f} kN·m")
        Max moment: 90.0 kN·m

        >>> # Multiple loads (superposition)
        >>> loads = [
        ...     LoadDefinition(LoadType.UDL, magnitude=15.0),
        ...     LoadDefinition(LoadType.POINT, magnitude=50.0, position_mm=3000.0),
        ... ]
        >>> result = compute_bmd_sfd(6000, "simply_supported", loads)
    """
    # Input validation
    if span_mm <= 0:
        raise ValueError(f"Span must be positive, got {span_mm}")

    if support_condition not in ("simply_supported", "cantilever"):
        raise ValueError(
            f"support_condition must be 'simply_supported' or 'cantilever', "
            f"got '{support_condition}'"
        )

    if not loads:
        raise ValueError("At least one load must be specified")

    # Initialize with zeros
    positions_mm = [span_mm * i / (num_points - 1) for i in range(num_points)]
    combined_bmd = [0.0] * num_points
    combined_sfd = [0.0] * num_points

    # Process each load
    for load in loads:
        if load.load_type == LoadType.UDL:
            if support_condition == "simply_supported":
                _, bmd, sfd = compute_udl_bmd_sfd(span_mm, load.magnitude, num_points)
            else:  # cantilever
                _, bmd, sfd = compute_cantilever_udl_bmd_sfd(
                    span_mm, load.magnitude, num_points
                )

        elif load.load_type == LoadType.POINT:
            if support_condition == "simply_supported":
                _, bmd, sfd = compute_point_load_bmd_sfd(
                    span_mm, load.magnitude, load.position_mm, num_points
                )
            else:  # cantilever
                _, bmd, sfd = compute_cantilever_point_load_bmd_sfd(
                    span_mm, load.magnitude, load.position_mm, num_points
                )

        elif load.load_type == LoadType.TRIANGULAR:
            # Ascending by default; position_mm=0 → ascending, else descending
            ascending = load.position_mm == 0.0
            _, bmd, sfd, _ = compute_triangular_load_bmd_sfd(
                span_mm, load.magnitude, ascending=ascending, num_points=num_points
            )

        elif load.load_type == LoadType.MOMENT:
            position = load.position_mm if load.position_mm > 0 else None
            _, bmd, sfd = compute_applied_moment_bmd_sfd(
                span_mm, load.magnitude, a_mm=position, num_points=num_points
            )

        else:
            raise ValueError(f"Unknown load type: {load.load_type}")

        # Superimpose
        combined_bmd, combined_sfd = _superimpose_diagrams(
            combined_bmd, combined_sfd, bmd, sfd
        )

    # Find critical points
    critical_points = _find_critical_points(positions_mm, combined_bmd, combined_sfd)

    # Compute max/min values
    max_bm = max(combined_bmd)
    min_bm = min(combined_bmd)
    max_sf = max(combined_sfd)
    min_sf = min(combined_sfd)

    return LoadDiagramResult(
        positions_mm=positions_mm,
        bmd_knm=combined_bmd,
        sfd_kn=combined_sfd,
        critical_points=critical_points,
        span_mm=span_mm,
        support_condition=support_condition,
        loads=loads,
        max_bm_knm=max_bm,
        min_bm_knm=min_bm,
        max_sf_kn=max_sf,
        min_sf_kn=min_sf,
    )
