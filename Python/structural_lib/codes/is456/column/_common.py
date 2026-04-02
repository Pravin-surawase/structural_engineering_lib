# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       _common
Description:  Shared helpers for column design modules per IS 456:2000.

Contains functions used by two or more column sub-modules (biaxial,
slenderness, long_column) to avoid code duplication.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# IS 456 Cl 39.6a: Puz coefficients
# Puz = 0.45 * fck * Ac + 0.75 * fy * Asc
# These are IS 456 specified constants — do NOT parameterize.
# 0.45 = 0.67 * fck / gamma_c where gamma_c = 1.5
# 0.75 = fy / (gamma_s * factor) — IS 456 specified
# ---------------------------------------------------------------------------
_PUZ_CONCRETE_COEFF: float = 0.45
_PUZ_STEEL_COEFF: float = 0.75


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
    """
    # IS 456 Cl 39.6a: Ac = b * D - Asc (net concrete area)
    Ag_mm2 = b_mm * D_mm
    Ac_mm2 = Ag_mm2 - Asc_mm2

    # IS 456 Cl 39.6a: Puz = 0.45 * fck * Ac + 0.75 * fy * Asc
    Puz_N = _PUZ_CONCRETE_COEFF * fck * Ac_mm2 + _PUZ_STEEL_COEFF * fy * Asc_mm2

    return Puz_N / 1000.0  # Convert N to kN
