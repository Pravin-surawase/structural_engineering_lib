# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       axial
Description:  Column axial capacity and classification per IS 456:2000.
Traceability: Functions are decorated with @clause for IS 456 clause references.

Implements:
- Column classification (short vs slender) per Cl. 25.1.2
- Minimum eccentricity per Cl. 25.4
- Short column axial capacity per Cl. 39.3

References:
    IS 456:2000, Cl. 25, 39
    SP:16 Design Aids for Reinforced Concrete (Charts 25–27)
"""

from __future__ import annotations

import math

from structural_lib.codes.is456.common.constants import (
    COLUMN_CONCRETE_COEFF,
    COLUMN_MAX_STEEL_RATIO,
    COLUMN_MIN_STEEL_RATIO,
    COLUMN_STEEL_COEFF,
    MIN_ECCENTRICITY_MM,
    SHORT_COLUMN_SLENDERNESS_LIMIT,
)
from structural_lib.codes.is456.traceability import clause
from structural_lib.core.data_types import (
    ColumnAxialResult,
    ColumnClassification,
    EndCondition,
)
from structural_lib.core.errors import DimensionError, MaterialError

__all__ = [
    "classify_column",
    "effective_length",
    "min_eccentricity",
    "short_axial_capacity",
]

# ---------------------------------------------------------------------------
# IS 456 Table 28 — Effective length ratios (le/l)
# ---------------------------------------------------------------------------
# Key: EndCondition → le/l ratio
# Cases 6 & 7 have no theoretical value (None → fall back to recommended).

_TABLE_28_THEORETICAL: dict[EndCondition, float | None] = {
    EndCondition.FIXED_FIXED: 0.50,
    EndCondition.FIXED_HINGED: 0.70,
    EndCondition.FIXED_FIXED_SWAY: 1.00,
    EndCondition.FIXED_FREE: 2.00,
    EndCondition.HINGED_HINGED: 1.00,
    EndCondition.FIXED_PARTIAL: None,  # No theoretical value per Table 28
    EndCondition.HINGED_PARTIAL: None,  # No theoretical value per Table 28
}

_TABLE_28_RECOMMENDED: dict[EndCondition, float] = {
    EndCondition.FIXED_FIXED: 0.65,
    EndCondition.FIXED_HINGED: 0.80,
    EndCondition.FIXED_FIXED_SWAY: 1.20,
    EndCondition.FIXED_FREE: 2.00,
    EndCondition.HINGED_HINGED: 1.00,
    EndCondition.FIXED_PARTIAL: 1.50,
    EndCondition.HINGED_PARTIAL: 2.00,
}


@clause("25.2")
def effective_length(
    l_mm: float,
    end_condition: EndCondition,
    use_theoretical: bool = False,
) -> float:
    """Calculate effective length of column per IS 456 Cl 25.2, Table 28.

    IS 456 Cl 25.2: The effective length le of a column depends on end
    restraint conditions. Table 28 gives the ratio le/l for seven standard
    cases, both as theoretical Euler values and as recommended design values.

    Cases 6 (FIXED_PARTIAL) and 7 (HINGED_PARTIAL) have NO theoretical
    value — only recommended. If ``use_theoretical=True`` is requested for
    these cases, the recommended value is used instead (with a warning
    attached to the return via the caller's responsibility to log).

    Args:
        l_mm: Unsupported length of column (mm). Must be > 0.
        end_condition: End condition from IS 456 Table 28.
        use_theoretical: If True, use theoretical values where available;
            otherwise use recommended values (default).

    Returns:
        Effective length le (mm).

    Raises:
        DimensionError: If l_mm <= 0.

    References:
        IS 456:2000 Cl. 25.2, Table 28
    """
    if l_mm <= 0:
        raise DimensionError(
            f"Unsupported length l_mm must be > 0, got {l_mm}",
            details={"l_mm": l_mm},
            clause_ref="Cl. 25.2",
        )

    if use_theoretical:
        # IS 456 Table 28: theoretical value (may be None for cases 6 & 7)
        ratio = _TABLE_28_THEORETICAL[end_condition]
        if ratio is None:
            # Fall back to recommended for cases without theoretical values
            ratio = _TABLE_28_RECOMMENDED[end_condition]
    else:
        # IS 456 Table 28: recommended value (always available)
        ratio = _TABLE_28_RECOMMENDED[end_condition]

    # IS 456 Cl 25.2: le = ratio × l
    le_mm = ratio * l_mm

    return le_mm


@clause("25.1.2")
def classify_column(le_mm: float, D_mm: float) -> ColumnClassification:
    """Classify column as short or slender per IS 456 Cl 25.1.2.

    IS 456 Cl 25.1.2: A compression member is short when le/D < 12,
    otherwise slender. The boundary (le/D = 12) is SLENDER (strict less-than).

    Args:
        le_mm: Effective length of column (mm). Must be > 0.
            NOTE: This is the EFFECTIVE length, not unsupported length.
            Caller must compute le from unsupported length and end conditions.
        D_mm: Depth of column in the direction considered (mm). Must be > 0.

    Returns:
        ColumnClassification.SHORT or ColumnClassification.SLENDER

    Raises:
        DimensionError: If le_mm <= 0 or D_mm <= 0.

    References:
        IS 456:2000, Cl 25.1.2
        SP:16 Design Aids
    """
    if le_mm <= 0:
        raise DimensionError(
            f"Effective length le_mm must be > 0, got {le_mm}",
            details={"le_mm": le_mm},
            clause_ref="Cl. 25.1.2",
        )
    if D_mm <= 0:
        raise DimensionError(
            f"Column depth D_mm must be > 0, got {D_mm}",
            details={"D_mm": D_mm},
            clause_ref="Cl. 25.1.2",
        )

    # IS 456 Cl 25.1.2: slenderness ratio = le / D
    ratio = le_mm / D_mm

    # IS 456 Cl 25.3.1: max slenderness ratio = 60
    # Note: ratio >= 60 is still classified correctly as SLENDER.
    # Warning about exceeding max ratio should be handled by caller if needed.

    # IS 456 Cl 25.1.2: short when le/D < 12 (strict less-than)
    if ratio < SHORT_COLUMN_SLENDERNESS_LIMIT:
        return ColumnClassification.SHORT

    return ColumnClassification.SLENDER


@clause("25.4")
def min_eccentricity(l_unsupported_mm: float, D_mm: float) -> float:
    """Calculate minimum eccentricity per IS 456 Cl 25.4.

    IS 456 Cl 25.4: e_min = max(l/500 + D/30, 20) mm

    All columns must be designed for this minimum eccentricity.
    For biaxial bending, check one axis at a time (call this function twice).

    Note: l is the UNSUPPORTED length (not effective length).

    Args:
        l_unsupported_mm: Unsupported length of column (mm). Must be > 0.
        D_mm: Lateral dimension in the direction considered (mm). Must be > 0.

    Returns:
        Minimum eccentricity in mm (always >= 20.0).

    Raises:
        DimensionError: If l_unsupported_mm <= 0 or D_mm <= 0.

    References:
        IS 456:2000, Cl 25.4
    """
    if l_unsupported_mm <= 0:
        raise DimensionError(
            f"Unsupported length l_unsupported_mm must be > 0, got {l_unsupported_mm}",
            details={"l_unsupported_mm": l_unsupported_mm},
            clause_ref="Cl. 25.4",
        )
    if D_mm <= 0:
        raise DimensionError(
            f"Column dimension D_mm must be > 0, got {D_mm}",
            details={"D_mm": D_mm},
            clause_ref="Cl. 25.4",
        )

    # IS 456 Cl 25.4: e_min = max(l/500 + D/30, 20)
    e_calc = l_unsupported_mm / 500.0 + D_mm / 30.0

    return max(e_calc, MIN_ECCENTRICITY_MM)


@clause("39.3")
def short_axial_capacity(
    fck: float,
    fy: float,
    Ag_mm2: float,
    Asc_mm2: float,
) -> ColumnAxialResult:
    """Calculate axial load capacity of a short column per IS 456 Cl 39.3.

    IS 456 Cl 39.3: Pu = 0.4 * fck * Ac + 0.67 * fy * Asc
    where Ac = Ag - Asc

    Applicable only when e_min <= 0.05 * D (minimum eccentricity condition).
    Caller must verify this condition before using the result.

    The coefficients 0.4 and 0.67 are IS 456 prescribed constants that
    already incorporate material safety factors (gamma_c=1.5, gamma_s=1.15)
    and strain compatibility.

    Args:
        fck: Characteristic compressive strength of concrete (N/mm²). Must be > 0.
        fy: Characteristic yield strength of steel (N/mm²). Must be > 0.
        Ag_mm2: Gross cross-sectional area (mm²). Must be > 0.
        Asc_mm2: Area of longitudinal reinforcement (mm²). Must be >= 0.

    Returns:
        ColumnAxialResult with capacity, steel ratio, warnings.

    Raises:
        MaterialError: If fck <= 0 or fy <= 0.
        DimensionError: If Ag_mm2 <= 0 or Asc_mm2 > Ag_mm2 or Asc_mm2 < 0.

    References:
        IS 456:2000, Cl 39.3
        SP:16 Design Aids, Chart 27
    """
    # --- Validate material properties ---
    if fck <= 0:
        raise MaterialError(
            f"fck must be > 0, got {fck}",
            details={"fck": fck},
            clause_ref="Cl. 39.3",
        )
    if fy <= 0:
        raise MaterialError(
            f"fy must be > 0, got {fy}",
            details={"fy": fy},
            clause_ref="Cl. 39.3",
        )

    # --- Validate section areas ---
    if Ag_mm2 <= 0:
        raise DimensionError(
            f"Gross area Ag_mm2 must be > 0, got {Ag_mm2}",
            details={"Ag_mm2": Ag_mm2},
            clause_ref="Cl. 39.3",
        )
    if Asc_mm2 < 0:
        raise DimensionError(
            f"Steel area Asc_mm2 must be >= 0, got {Asc_mm2}",
            details={"Asc_mm2": Asc_mm2},
            clause_ref="Cl. 39.3",
        )
    if Asc_mm2 > Ag_mm2:
        raise DimensionError(
            f"Steel area Asc_mm2={Asc_mm2} exceeds gross area Ag_mm2={Ag_mm2}",
            details={"Asc_mm2": Asc_mm2, "Ag_mm2": Ag_mm2},
            clause_ref="Cl. 39.3",
        )

    # --- Collect warnings ---
    warnings: list[str] = []

    # IS 456 Cl 26.5.3.1: steel ratio limits
    steel_ratio = Asc_mm2 / Ag_mm2
    if steel_ratio < COLUMN_MIN_STEEL_RATIO:
        warnings.append(
            f"Steel ratio {steel_ratio:.4f} below minimum "
            f"{COLUMN_MIN_STEEL_RATIO} (0.8%) per Cl 26.5.3.1"
        )
    if steel_ratio > COLUMN_MAX_STEEL_RATIO:
        warnings.append(
            f"Steel ratio {steel_ratio:.4f} exceeds maximum "
            f"{COLUMN_MAX_STEEL_RATIO} (4%) per Cl 26.5.3.1"
        )

    # IS 456 scope warning for high-performance concrete
    if fck > 60:
        warnings.append(
            f"fck={fck} N/mm² exceeds IS 456 scope (max 60 N/mm²). "
            "Results may not be code-compliant."
        )

    # --- IS 456 Cl 39.3: Pu = 0.4 * fck * Ac + 0.67 * fy * Asc ---
    Ac_mm2 = Ag_mm2 - Asc_mm2

    concrete_contribution_N = COLUMN_CONCRETE_COEFF * fck * Ac_mm2
    steel_contribution_N = COLUMN_STEEL_COEFF * fy * Asc_mm2
    Pu_N = concrete_contribution_N + steel_contribution_N

    # Check for numerical issues
    if math.isnan(Pu_N) or math.isinf(Pu_N):
        raise DimensionError(
            "Computed axial capacity is NaN or Inf — check inputs",
            details={"fck": fck, "fy": fy, "Ag_mm2": Ag_mm2, "Asc_mm2": Asc_mm2},
            clause_ref="Cl. 39.3",
        )

    # Convert to kN
    Pu_kN = Pu_N / 1000.0

    return ColumnAxialResult(
        Pu_kN=Pu_kN,
        fck=fck,
        fy=fy,
        Ag_mm2=Ag_mm2,
        Asc_mm2=Asc_mm2,
        Ac_mm2=Ac_mm2,
        steel_ratio=steel_ratio,
        classification=ColumnClassification.SHORT,
        is_safe=True,
        warnings=warnings,
    )
