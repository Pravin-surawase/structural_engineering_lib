"""IS 456 reinforcement area and stress helpers.

Pure functions --- no I/O, no side effects. All units in N and mm.
Uses named constants from :mod:`.constants`.

References:
    IS 456:2000 Cl. 26.5.1.1 (min/max steel), Cl. 36.1 (design stress)
"""

from __future__ import annotations

from structural_lib.codes.is456.common.constants import (
    MAX_STEEL_RATIO,
    MIN_STEEL_FACTOR,
    STRESS_RATIO,
)


def design_steel_stress(fy: float) -> float:
    """Design yield stress of reinforcement.

    fd = 0.87 * fy  (IS 456 Cl. 36.1, i.e. fy / gamma_s where gamma_s = 1.15)

    Args:
        fy: Characteristic yield strength (N/mm2).

    Returns:
        Design steel stress (N/mm2).
    """
    return STRESS_RATIO * fy


def steel_force(fy: float, ast: float) -> float:
    """Tensile force in reinforcement at design yield stress.

    T = 0.87 * fy * Ast

    Args:
        fy: Characteristic yield strength (N/mm2).
        ast: Area of tension steel (mm2).

    Returns:
        Steel tensile force (N).
    """
    return STRESS_RATIO * fy * ast


def min_steel_area(b: float, d: float, fy: float) -> float:
    """Minimum area of tension reinforcement (IS 456 Cl. 26.5.1.1).

    As_min = 0.85 * b * d / fy

    Args:
        b: Width of the beam (mm).
        d: Effective depth (mm).
        fy: Characteristic yield strength (N/mm2).

    Returns:
        Minimum steel area (mm2).

    Raises:
        ValueError: If fy <= 0.
    """
    if fy <= 0:
        raise ValueError(f"fy must be > 0, got {fy}")
    return MIN_STEEL_FACTOR * b * d / fy


def max_steel_area(b: float, D: float) -> float:
    """Maximum area of tension reinforcement (IS 456 Cl. 26.5.1.1).

    As_max = 0.04 * b * D  (4% of gross area)

    Args:
        b: Width of the beam (mm).
        D: Overall depth (mm).

    Returns:
        Maximum steel area (mm2).
    """
    return MAX_STEEL_RATIO * b * D
