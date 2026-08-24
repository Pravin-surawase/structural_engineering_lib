# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       _common
Description:  Shared helpers for column design modules per IS 456:2000.

Contains functions used by two or more column sub-modules (biaxial,
slenderness, long_column) to avoid code duplication.
"""

from __future__ import annotations

import math

from structural_lib.codes.is456.common.constants import (
    COLUMN_MAX_STEEL_RATIO,
    COLUMN_MIN_STEEL_RATIO,
)
from structural_lib.core.errors import DimensionError

# ---------------------------------------------------------------------------
# IS 456 Cl 39.6a: Puz coefficients
# Puz = 0.45 * fck * Ac + 0.75 * fy * Asc
# These are IS 456 specified constants — do NOT parameterize.
# 0.45 = 0.67 * fck / gamma_c where gamma_c = 1.5
# 0.75 = fy / (gamma_s * factor) — IS 456 specified
# ---------------------------------------------------------------------------
_PUZ_CONCRETE_COEFF: float = 0.45
_PUZ_STEEL_COEFF: float = 0.75
_STEEL_RATIO_BOUNDARY_ABS_TOL = 1e-12


def _require_column_steel_ratio(
    gross_area_mm2: float,
    steel_area_mm2: float,
    *,
    clause_ref: str = "Cl. 26.5.3.1",
) -> float:
    """Require the maintained 0.8-4.0% longitudinal-steel domain."""
    ratio = steel_area_mm2 / gross_area_mm2
    if math.isclose(
        ratio,
        COLUMN_MIN_STEEL_RATIO,
        rel_tol=0.0,
        abs_tol=_STEEL_RATIO_BOUNDARY_ABS_TOL,
    ):
        ratio = COLUMN_MIN_STEEL_RATIO
    elif math.isclose(
        ratio,
        COLUMN_MAX_STEEL_RATIO,
        rel_tol=0.0,
        abs_tol=_STEEL_RATIO_BOUNDARY_ABS_TOL,
    ):
        ratio = COLUMN_MAX_STEEL_RATIO
    if not COLUMN_MIN_STEEL_RATIO <= ratio <= COLUMN_MAX_STEEL_RATIO:
        raise DimensionError(
            "Column longitudinal steel ratio must be within 0.8-4.0%",
            details={
                "gross_area_mm2": gross_area_mm2,
                "steel_area_mm2": steel_area_mm2,
                "steel_ratio": ratio,
                "minimum_ratio": COLUMN_MIN_STEEL_RATIO,
                "maximum_ratio": COLUMN_MAX_STEEL_RATIO,
            },
            clause_ref=clause_ref,
        )
    return ratio


def _calculate_puz(
    b_mm: float,
    D_mm: float,
    fck: float,
    fy: float,
    Asc_mm2: float,
) -> float:
    """Calculate pure axial crush capacity per IS 456 Cl 39.6a.

    IS 456 Cl 39.6a: Puz = 0.45 * fck * Ac + 0.75 * fy * Asc

    Args:
        b_mm: Column width (mm).
        D_mm: Column depth (mm).
        fck: Concrete compressive strength (N/mm²).
        fy: Steel yield strength (N/mm²).
        Asc_mm2: Total steel area (mm²).

    Returns:
        Puz in kN.

    Raises:
        ValueError: If dimensions, materials, or steel area are invalid.
    """
    if b_mm <= 0 or D_mm <= 0:
        raise ValueError(f"Dimensions must be positive: b_mm={b_mm}, D_mm={D_mm}")
    if fck <= 0 or fy <= 0:
        raise ValueError(f"Material strengths must be positive: fck={fck}, fy={fy}")
    if Asc_mm2 < 0:
        raise ValueError(f"Steel area must be non-negative: Asc_mm2={Asc_mm2}")
    Ag_mm2 = b_mm * D_mm
    if Asc_mm2 >= Ag_mm2:
        raise ValueError(
            f"Steel area ({Asc_mm2:.1f} mm²) must be less than gross area ({Ag_mm2:.1f} mm²)"
        )

    # IS 456 Cl 39.6a: Ac = b * D - Asc (net concrete area)
    Ag_mm2 = b_mm * D_mm
    Ac_mm2 = Ag_mm2 - Asc_mm2

    # IS 456 Cl 39.6a: Puz = 0.45 * fck * Ac + 0.75 * fy * Asc
    Puz_N = _PUZ_CONCRETE_COEFF * fck * Ac_mm2 + _PUZ_STEEL_COEFF * fy * Asc_mm2

    return Puz_N / 1000.0  # Convert N to kN
