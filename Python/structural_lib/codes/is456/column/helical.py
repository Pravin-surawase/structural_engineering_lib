# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       helical
Description:  Helical reinforcement check for circular columns per IS 456:2000 Cl 39.4.
Traceability: Functions are decorated with @clause for IS 456 clause references.

Implements:
- Helical reinforcement adequacy check
- Enhancement factor (1.05) for axial capacity
- Pitch limits per IS 456 Cl 26.5.3.2

References:
    IS 456:2000, Cl. 39.4, 26.5.3.2
    SP:16:1980 Design Aids for Reinforced Concrete
    Pillai & Menon, "Reinforced Concrete Design", 3rd Ed., Ch. 13
"""

from __future__ import annotations

import math

from structural_lib.codes.is456.traceability import clause
from structural_lib.core.data_types import HelicalReinforcementResult
from structural_lib.core.errors import DimensionError, MaterialError

__all__ = [
    "check_helical_reinforcement",
]

# ---------------------------------------------------------------------------
# IS 456 Cl 39.4: Enhancement factor for helical reinforcement
# ---------------------------------------------------------------------------
_HELICAL_ENHANCEMENT_FACTOR: float = 1.05

# ---------------------------------------------------------------------------
# IS 456 Cl 39.4: Helical ratio coefficient
# V_helix / V_core >= 0.36 × (Ag/Ac - 1) × fck/fy
# ---------------------------------------------------------------------------
_HELICAL_RATIO_COEFF: float = 0.36

# ---------------------------------------------------------------------------
# IS 456 Cl 26.5.3.2: Pitch limits for helical reinforcement
# ---------------------------------------------------------------------------
_MIN_PITCH_MM: float = 25.0  # Minimum pitch floor (mm)
_MIN_PITCH_BAR_FACTOR: float = 3.0  # Minimum pitch = 3 × bar diameter
_MAX_PITCH_MM: float = 75.0  # Maximum pitch ceiling (mm)
_MAX_PITCH_CORE_FACTOR: float = 6.0  # Maximum pitch = D_core / 6


@clause("39.4")
def check_helical_reinforcement(
    D_mm: float,
    D_core_mm: float,
    fck: float,
    fy: float,
    d_helix_mm: float,
    pitch_mm: float,
    Pu_axial_kN: float,
) -> HelicalReinforcementResult:
    """Check helical reinforcement for circular column per IS 456 Cl 39.4.

    IS 456 Cl 39.4 permits a 1.05 enhancement factor on the short column
    axial capacity (Cl 39.3) when helical reinforcement meets the minimum
    ratio requirement:

        V_helix / V_core >= 0.36 × (Ag/Ac - 1) × fck/fy

    This enhancement applies ONLY to axial capacity, NOT to bending.

    Args:
        D_mm: Column outer diameter (mm). Must be > 0. Column must be circular.
        D_core_mm: Core diameter inside helix (mm). Must be > 0 and < D_mm.
        fck: Concrete compressive strength (N/mm²). Must be > 0.
        fy: Steel yield strength (N/mm²). Must be > 0.
        d_helix_mm: Helix bar diameter (mm). Must be > 0.
        pitch_mm: Helix pitch (mm). Must be > 0.
        Pu_axial_kN: Short column axial capacity from Cl 39.3 (kN). Must be > 0.

    Returns:
        HelicalReinforcementResult with adequacy check and enhanced capacity.

    Raises:
        DimensionError: If geometric dimensions are invalid.
        MaterialError: If material properties are out of range.

    References:
        IS 456:2000, Cl. 39.4 (helical enhancement)
        IS 456:2000, Cl. 26.5.3.2 (pitch limits)
    """
    # ===========================================================
    # 1. Input validation
    # ===========================================================
    if D_mm <= 0:
        raise DimensionError(
            f"Column diameter D_mm must be > 0, got {D_mm}",
            details={"D_mm": D_mm},
            clause_ref="Cl. 39.4",
        )
    if D_core_mm <= 0:
        raise DimensionError(
            f"Core diameter D_core_mm must be > 0, got {D_core_mm}",
            details={"D_core_mm": D_core_mm},
            clause_ref="Cl. 39.4",
        )
    if D_core_mm >= D_mm:
        raise DimensionError(
            f"Core diameter D_core_mm ({D_core_mm}) must be < "
            f"column diameter D_mm ({D_mm})",
            details={"D_core_mm": D_core_mm, "D_mm": D_mm},
            clause_ref="Cl. 39.4",
        )
    if fck <= 0:
        raise MaterialError(
            f"fck must be > 0, got {fck}",
            details={"fck": fck},
            clause_ref="Cl. 39.4",
        )
    if fy <= 0:
        raise MaterialError(
            f"fy must be > 0, got {fy}",
            details={"fy": fy},
            clause_ref="Cl. 39.4",
        )
    if d_helix_mm <= 0:
        raise DimensionError(
            f"Helix bar diameter d_helix_mm must be > 0, got {d_helix_mm}",
            details={"d_helix_mm": d_helix_mm},
            clause_ref="Cl. 39.4",
        )
    if pitch_mm <= 0:
        raise DimensionError(
            f"Helix pitch pitch_mm must be > 0, got {pitch_mm}",
            details={"pitch_mm": pitch_mm},
            clause_ref="Cl. 39.4",
        )
    if Pu_axial_kN <= 0:
        raise DimensionError(
            f"Axial capacity Pu_axial_kN must be > 0, got {Pu_axial_kN}",
            details={"Pu_axial_kN": Pu_axial_kN},
            clause_ref="Cl. 39.4",
        )

    warnings: list[str] = []

    # ===========================================================
    # 2. Gross and core areas (circular section)
    # ===========================================================
    # IS 456 Cl 39.4: Ag = π/4 × D² (gross area)
    Ag_mm2 = math.pi / 4.0 * D_mm * D_mm
    # IS 456 Cl 39.4: Ac = π/4 × D_core² (core area)
    Ac_mm2 = math.pi / 4.0 * D_core_mm * D_core_mm

    # ===========================================================
    # 3. Pitch limits (IS 456 Cl 26.5.3.2)
    # ===========================================================
    # IS 456 Cl 26.5.3.2: min pitch = max(25mm, 3 × d_helix)
    min_pitch_mm = max(_MIN_PITCH_MM, _MIN_PITCH_BAR_FACTOR * d_helix_mm)
    # IS 456 Cl 26.5.3.2: max pitch = min(75mm, D_core/6)
    max_pitch_mm = min(_MAX_PITCH_MM, D_core_mm / _MAX_PITCH_CORE_FACTOR)

    pitch_ok = min_pitch_mm <= pitch_mm <= max_pitch_mm

    if not pitch_ok:
        if pitch_mm < min_pitch_mm:
            warnings.append(
                f"Helix pitch {pitch_mm:.1f}mm is below minimum "
                f"{min_pitch_mm:.1f}mm per Cl 26.5.3.2"
            )
        if pitch_mm > max_pitch_mm:
            warnings.append(
                f"Helix pitch {pitch_mm:.1f}mm exceeds maximum "
                f"{max_pitch_mm:.1f}mm per Cl 26.5.3.2"
            )

    # ===========================================================
    # 4. Helical ratio check (IS 456 Cl 39.4)
    # ===========================================================
    # IS 456 Cl 39.4: V_helix per turn = π × D_core × A_helix_bar / pitch
    # where A_helix_bar = π/4 × d_helix²
    A_helix_bar_mm2 = math.pi / 4.0 * d_helix_mm * d_helix_mm

    # Volume of helix per unit height of core
    # V_helix per mm height = π × D_core × A_helix_bar / pitch
    V_helix_per_mm = math.pi * D_core_mm * A_helix_bar_mm2 / pitch_mm

    # Volume of core per unit height = Ac = π/4 × D_core²
    V_core_per_mm = Ac_mm2

    # IS 456 Cl 39.4: helical ratio = V_helix / V_core
    helical_ratio_provided = V_helix_per_mm / V_core_per_mm

    # IS 456 Cl 39.4: required ratio = 0.36 × (Ag/Ac - 1) × fck/fy
    Ag_Ac_minus_1 = (Ag_mm2 / Ac_mm2) - 1.0
    helical_ratio_required = _HELICAL_RATIO_COEFF * Ag_Ac_minus_1 * fck / fy

    ratio_ok = helical_ratio_provided >= helical_ratio_required

    if not ratio_ok:
        warnings.append(
            f"Helical ratio {helical_ratio_provided:.4f} is below required "
            f"{helical_ratio_required:.4f} per Cl 39.4"
        )

    # ===========================================================
    # 5. Enhanced capacity
    # ===========================================================
    # IS 456 Cl 39.4: 1.05 enhancement on axial capacity
    Pu_enhanced_kN = _HELICAL_ENHANCEMENT_FACTOR * Pu_axial_kN

    # IS 456 Cl 39.4: enhancement applies only when ratio is adequate
    is_adequate = ratio_ok and pitch_ok

    # NaN/Inf guard
    if (
        math.isnan(helical_ratio_provided)
        or math.isinf(helical_ratio_provided)
        or math.isnan(helical_ratio_required)
        or math.isinf(helical_ratio_required)
    ):
        is_adequate = False
        warnings.append("Numerical issue in helical ratio calculation")

    return HelicalReinforcementResult(
        is_adequate=is_adequate,
        enhancement_factor=_HELICAL_ENHANCEMENT_FACTOR,
        Pu_enhanced_kN=round(Pu_enhanced_kN, 2),
        helical_ratio_provided=round(helical_ratio_provided, 6),
        helical_ratio_required=round(helical_ratio_required, 6),
        pitch_mm=pitch_mm,
        min_pitch_mm=round(min_pitch_mm, 1),
        max_pitch_mm=round(max_pitch_mm, 1),
        pitch_ok=pitch_ok,
        D_core_mm=D_core_mm,
        warnings=tuple(warnings),
    )
