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

from structural_lib.data_types import (
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
        >>> from structural_lib.data_types import LoadDefinition, LoadType
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
            # Triangular load approximated as series of point loads
            # Future: implement proper closed-form solution
            raise NotImplementedError("Triangular load not yet implemented")

        elif load.load_type == LoadType.MOMENT:
            # Applied moment (future implementation)
            raise NotImplementedError("Applied moment not yet implemented")

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
