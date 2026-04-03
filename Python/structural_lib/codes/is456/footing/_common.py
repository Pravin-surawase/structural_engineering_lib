# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""IS 456:2000 — Footing shared utilities.

Common calculations used across footing sub-modules:
- Net upward pressure distribution
- Punching shear perimeter geometry
- Effective depth helpers
"""

from __future__ import annotations

from structural_lib.core.errors import (
    E_FOOTING_001,
    E_FOOTING_005,
    E_FOOTING_007,
    DimensionError,
    ValidationError,
)


def validate_footing_inputs(
    L_mm: float,
    B_mm: float,
    d_mm: float,
    a_mm: float,
    b_mm: float,
) -> None:
    """Validate footing geometry inputs.

    Args:
        L_mm: Footing length (mm)
        B_mm: Footing width (mm)
        d_mm: Effective depth (mm)
        a_mm: Column dimension parallel to L (mm)
        b_mm: Column dimension parallel to B (mm)

    Raises:
        DimensionError: If any dimension is non-positive
        DimensionError: If column larger than footing
    """
    if L_mm <= 0 or B_mm <= 0 or d_mm <= 0:
        raise DimensionError(
            E_FOOTING_001.message,
            details={"L_mm": L_mm, "B_mm": B_mm, "d_mm": d_mm},
            clause_ref=E_FOOTING_001.clause,
        )
    if a_mm <= 0 or b_mm <= 0:
        raise DimensionError(
            "Column dimensions must be positive",
            details={"a_mm": a_mm, "b_mm": b_mm},
        )
    if a_mm >= L_mm or b_mm >= B_mm:
        raise DimensionError(
            E_FOOTING_007.message,
            details={"a_mm": a_mm, "b_mm": b_mm, "L_mm": L_mm, "B_mm": B_mm},
            clause_ref=E_FOOTING_007.clause,
        )
    if d_mm < 150:
        raise DimensionError(
            E_FOOTING_005.message,
            details={"d_mm": d_mm, "minimum": 150},
            clause_ref=E_FOOTING_005.clause,
        )


def net_upward_pressure_nmm2(Pu_kN: float, L_mm: float, B_mm: float) -> float:
    """Calculate net upward factored pressure on footing.

    Args:
        Pu_kN: Factored axial load (kN) — for structural design
        L_mm: Footing length (mm)
        B_mm: Footing width (mm)

    Returns:
        Uniform net upward pressure (N/mm²)
    """
    if Pu_kN <= 0:
        raise ValidationError(
            "Factored load must be positive",
            details={"Pu_kN": Pu_kN},
        )
    return (Pu_kN * 1000.0) / (L_mm * B_mm)  # kN → N


def punching_perimeter_mm(a_mm: float, b_mm: float, d_mm: float) -> float:
    """Critical perimeter for punching shear at d/2 from column face per Cl 31.6.1.

    Args:
        a_mm: Column dimension parallel to L (mm)
        b_mm: Column dimension parallel to B (mm)
        d_mm: Effective depth (mm)

    Returns:
        Perimeter (mm) of the critical section
    """
    return 2.0 * ((a_mm + d_mm) + (b_mm + d_mm))


def punching_area_mm2(a_mm: float, b_mm: float, d_mm: float) -> float:
    """Area within punching perimeter at d/2 from column face.

    Args:
        a_mm: Column dimension parallel to L (mm)
        b_mm: Column dimension parallel to B (mm)
        d_mm: Effective depth (mm)

    Returns:
        Area (mm²) within critical perimeter
    """
    return (a_mm + d_mm) * (b_mm + d_mm)
