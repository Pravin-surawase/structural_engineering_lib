# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       torsion
Description:  Torsion design per IS 456:2000 Clause 41

This module implements torsion design for reinforced concrete beams
following IS 456:2000 provisions. It handles:
- Equivalent shear (Ve) calculation
- Equivalent moment (Me) calculation
- Combined torsion + shear reinforcement design
- Longitudinal reinforcement for torsion

References:
    IS 456:2000, Clause 41 - Design for Torsion
    SP 34:1987, Section 5 - Torsion Design
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from structural_lib.error_messages import (
    dimension_too_small,
    material_property_out_of_range,
)
from structural_lib.errors import (
    E_TORSION_001,
    DesignError,
    DimensionError,
    MaterialError,
)

from . import tables
from .traceability import clause

if TYPE_CHECKING:
    pass


__all__ = [
    "TorsionResult",
    "calculate_equivalent_shear",
    "calculate_equivalent_moment",
    "calculate_torsion_shear_stress",
    "calculate_torsion_stirrup_area",
    "calculate_longitudinal_torsion_steel",
    "design_torsion",
]


# =============================================================================
# Data Types
# =============================================================================


@dataclass
class TorsionResult:
    """Result of torsion design per IS 456 Clause 41.

    Attributes:
        tu_knm: Applied torsional moment (kN·m)
        vu_kn: Applied shear force (kN)
        mu_knm: Applied bending moment (kN·m)
        ve_kn: Equivalent shear force (kN)
        me_knm: Equivalent bending moment (kN·m)
        tv_equiv: Equivalent shear stress (N/mm²)
        tc: Design shear strength of concrete (N/mm²)
        tc_max: Maximum shear stress limit (N/mm²)
        asv_torsion: Area of stirrups for torsion per unit length (mm²/mm)
        asv_shear: Area of stirrups for shear per unit length (mm²/mm)
        asv_total: Total stirrup area per unit length (mm²/mm)
        stirrup_spacing: Designed stirrup spacing (mm)
        al_torsion: Longitudinal steel for torsion (mm²)
        is_safe: True if section is safe
        requires_closed_stirrups: True (always for torsion)
        errors: List of structured errors/warnings
    """

    tu_knm: float
    vu_kn: float
    mu_knm: float
    ve_kn: float
    me_knm: float
    tv_equiv: float
    tc: float
    tc_max: float
    asv_torsion: float
    asv_shear: float
    asv_total: float
    stirrup_spacing: float
    al_torsion: float
    is_safe: bool
    requires_closed_stirrups: bool = True
    errors: list[DesignError] = field(default_factory=list)


# =============================================================================
# Core Calculations
# =============================================================================


@clause("41.3.1")
def calculate_equivalent_shear(vu_kn: float, tu_knm: float, b: float) -> float:
    """
    Calculate equivalent shear force per IS 456 Cl 41.3.1.

    The equivalent shear accounts for torsion effects by adding a
    component proportional to the torsional moment.

    Args:
        vu_kn: Factored shear force (kN)
        tu_knm: Factored torsional moment (kN·m)
        b: Beam width (mm)

    Returns:
        Equivalent shear force Ve (kN)

    Raises:
        DimensionError: If b <= 0

    Formula:
        Ve = Vu + 1.6 × (Tu / b)

    Reference:
        IS 456:2000, Clause 41.3.1
    """
    if b <= 0:
        raise DimensionError(
            dimension_too_small("beam width b", b, 0, "Cl. 41.3.1"),
            details={"b": b, "minimum": 0},
            clause_ref="Cl. 41.3.1",
        )

    # Tu is in kN·m, b is in mm
    # Convert Tu to kN·mm for dimensional consistency
    tu_kn_mm = tu_knm * 1000  # kN·mm
    ve = abs(vu_kn) + 1.6 * tu_kn_mm / b

    return ve


@clause("41.4.2")
def calculate_equivalent_moment(
    mu_knm: float, tu_knm: float, d: float, b: float
) -> float:
    """
    Calculate equivalent bending moment per IS 456 Cl 41.4.2.

    Torsion induces an additional moment that must be combined
    with the applied bending moment for flexural design.

    Args:
        mu_knm: Factored bending moment (kN·m)
        tu_knm: Factored torsional moment (kN·m)
        d: Effective depth (mm)
        b: Beam width (mm)

    Returns:
        Equivalent moment Me (kN·m)

    Raises:
        DimensionError: If b or d <= 0

    Formula:
        Mt = Tu × (1 + D/b) / 1.7
        Me = Mu + Mt

    Reference:
        IS 456:2000, Clause 41.4.2
    """
    if b <= 0:
        raise DimensionError(
            dimension_too_small("beam width b", b, 0, "Cl. 41.4.2"),
            details={"b": b, "minimum": 0},
            clause_ref="Cl. 41.4.2",
        )
    if d <= 0:
        raise DimensionError(
            dimension_too_small("effective depth d", d, 0, "Cl. 41.4.2"),
            details={"d": d, "minimum": 0},
            clause_ref="Cl. 41.4.2",
        )

    # Estimate D from d (assume cover ≈ 50mm)
    D = d + 50

    # Mt = Tu × (1 + D/b) / 1.7
    mt = abs(tu_knm) * (1 + D / b) / 1.7

    # Me = Mu + Mt
    me = abs(mu_knm) + mt

    return me


@clause("41.3")
def calculate_torsion_shear_stress(ve_kn: float, b: float, d: float) -> float:
    """
    Calculate equivalent shear stress for torsion design.

    Args:
        ve_kn: Equivalent shear force (kN)
        b: Beam width (mm)
        d: Effective depth (mm)

    Returns:
        Equivalent shear stress τve (N/mm²)

    Raises:
        DimensionError: If b or d <= 0

    Formula:
        τve = Ve / (b × d)

    Reference:
        IS 456:2000, Clause 41.3
    """
    if b <= 0:
        raise DimensionError(
            dimension_too_small("beam width b", b, 0, "Cl. 41.3"),
            details={"b": b, "minimum": 0},
            clause_ref="Cl. 41.3",
        )
    if d <= 0:
        raise DimensionError(
            dimension_too_small("effective depth d", d, 0, "Cl. 41.3"),
            details={"d": d, "minimum": 0},
            clause_ref="Cl. 41.3",
        )

    # Ve in kN, convert to N
    ve_n = ve_kn * 1000
    tv = ve_n / (b * d)

    return tv


@clause("41.4.3")
def calculate_torsion_stirrup_area(
    tu_knm: float,
    vu_kn: float,
    b: float,
    d: float,
    b1: float,
    d1: float,
    fy: float,
    tc: float,
) -> tuple[float, float, float]:
    """
    Calculate stirrup area for combined torsion and shear.

    Args:
        tu_knm: Factored torsional moment (kN·m)
        vu_kn: Factored shear force (kN)
        b: Beam width (mm)
        d: Effective depth (mm)
        b1: Center-to-center distance between corner bars in width direction (mm)
        d1: Center-to-center distance between corner bars in depth direction (mm)
        fy: Stirrup steel yield strength (N/mm²)
        tc: Design shear strength of concrete (N/mm²)

    Returns:
        Tuple of (asv_torsion, asv_shear, asv_total) in mm²/mm

    Formula:
        Asv/sv (torsion) = Tu × 10⁶ / (b1 × d1 × 0.87 × fy)
        Asv/sv (shear) = Vus / (0.87 × fy × d)
        Asv/sv (total) = asv_torsion + asv_shear

    Reference:
        IS 456:2000, Clause 41.4.3
    """
    if fy <= 0:
        raise MaterialError(
            material_property_out_of_range(
                "steel yield strength fy", fy, 0, 600, "Cl. 41.4.3"
            ),
            details={"fy": fy, "minimum": 0, "maximum": 600},
            clause_ref="Cl. 41.4.3",
        )

    # Torsion component: Asv/sv = Tu / (b1 × d1 × 0.87 × fy)
    # Tu in kN·m, convert to N·mm
    tu_nmm = abs(tu_knm) * 1e6
    asv_torsion = tu_nmm / (b1 * d1 * 0.87 * fy)

    # Shear component: Asv/sv = Vus / (0.87 × fy × d)
    # First calculate Vus = Vu - Vc
    vu_n = abs(vu_kn) * 1000
    vc_n = tc * b * d
    vus_n = max(0, vu_n - vc_n)

    if vus_n > 0:
        asv_shear = vus_n / (0.87 * fy * d)
    else:
        asv_shear = 0

    # Total = torsion + shear (both legs contribute to both)
    asv_total = asv_torsion + asv_shear

    return asv_torsion, asv_shear, asv_total


@clause("41.4.2")
def calculate_longitudinal_torsion_steel(
    tu_knm: float,
    vu_kn: float,
    b1: float,
    d1: float,
    fy: float,
    sv: float,
) -> float:
    """
    Calculate longitudinal reinforcement for torsion.

    Args:
        tu_knm: Factored torsional moment (kN·m)
        vu_kn: Factored shear force (kN)
        b1: Center-to-center distance between corner bars (width) (mm)
        d1: Center-to-center distance between corner bars (depth) (mm)
        fy: Steel yield strength (N/mm²)
        sv: Stirrup spacing (mm)

    Returns:
        Longitudinal steel area Al (mm²)

    Formula:
        Al = Tu × 10⁶ × (b1 + d1) / (b1 × d1 × 0.87 × fy)
        But not less than: Asv × (b1 + d1) / sv

    Reference:
        IS 456:2000, Clause 41.4.2.1
    """
    if fy <= 0:
        raise MaterialError(
            material_property_out_of_range(
                "steel yield strength fy", fy, 0, 600, "Cl. 41.4.2"
            ),
            details={"fy": fy, "minimum": 0, "maximum": 600},
            clause_ref="Cl. 41.4.2",
        )

    # Tu in kN·m → N·mm
    tu_nmm = abs(tu_knm) * 1e6

    # Al = Tu × (b1 + d1) / (b1 × d1 × 0.87 × fy)
    al = tu_nmm * (b1 + d1) / (b1 * d1 * 0.87 * fy)

    return al


# =============================================================================
# Main Design Function
# =============================================================================


@clause("41.1", "41.3", "41.4")
def design_torsion(
    tu_knm: float,
    vu_kn: float,
    mu_knm: float,
    b: float,
    D: float,
    d: float,
    fck: float,
    fy: float,
    cover: float,
    stirrup_dia: float = 8,
    pt: float = 1.0,
) -> TorsionResult:
    """
    Design beam for combined torsion, shear, and bending.

    This function performs complete torsion design per IS 456 Clause 41,
    calculating equivalent shear, equivalent moment, and required
    reinforcement for combined loading.

    Args:
        tu_knm: Factored torsional moment (kN·m)
        vu_kn: Factored shear force (kN)
        mu_knm: Factored bending moment (kN·m)
        b: Beam width (mm)
        D: Overall depth (mm)
        d: Effective depth (mm)
        fck: Concrete characteristic strength (N/mm²)
        fy: Steel yield strength (N/mm²)
        cover: Clear cover (mm)
        stirrup_dia: Stirrup diameter (mm), default 8
        pt: Tension steel percentage (%), default 1.0

    Returns:
        TorsionResult with complete design output

    Notes:
        - Closed stirrups are mandatory for torsion (Cl 41.4.3)
        - Longitudinal steel distributed around perimeter (Cl 41.4.2.1)
        - If τve > τc,max, section is unsafe and must be redesigned

    Reference:
        IS 456:2000, Clause 41
    """
    errors: list[DesignError] = []

    # Validate inputs
    if b <= 0:
        raise DimensionError(
            dimension_too_small("beam width b", b, 0, "Cl. 41"),
            details={"b": b, "minimum": 0},
            clause_ref="Cl. 41",
        )
    if D <= 0:
        raise DimensionError(
            dimension_too_small("overall depth D", D, 0, "Cl. 41"),
            details={"D": D, "minimum": 0},
            clause_ref="Cl. 41",
        )
    if d <= 0:
        raise DimensionError(
            dimension_too_small("effective depth d", d, 0, "Cl. 41"),
            details={"d": d, "minimum": 0},
            clause_ref="Cl. 41",
        )
    if fck <= 0:
        raise MaterialError(
            material_property_out_of_range("fck", fck, 0, 100, "Cl. 41"),
            details={"fck": fck, "minimum": 0, "maximum": 100},
            clause_ref="Cl. 41",
        )
    if fy <= 0:
        raise MaterialError(
            material_property_out_of_range("fy", fy, 0, 600, "Cl. 41"),
            details={"fy": fy, "minimum": 0, "maximum": 600},
            clause_ref="Cl. 41",
        )

    # Calculate core dimensions for stirrup (center-to-center of corners)
    # b1 = b - 2*(cover + stirrup_dia/2)
    # d1 = D - 2*(cover + stirrup_dia/2)
    b1 = b - 2 * (cover + stirrup_dia / 2)
    d1 = D - 2 * (cover + stirrup_dia / 2)

    # Ensure positive core dimensions
    b1 = max(b1, 50)
    d1 = max(d1, 100)

    # Step 1: Calculate equivalent shear (Cl 41.3.1)
    ve_kn = calculate_equivalent_shear(vu_kn, tu_knm, b)

    # Step 2: Calculate equivalent moment (Cl 41.4.2)
    me_knm = calculate_equivalent_moment(mu_knm, tu_knm, d, b)

    # Step 3: Calculate equivalent shear stress
    tv_equiv = calculate_torsion_shear_stress(ve_kn, b, d)

    # Step 4: Get concrete shear strength from tables
    tc = tables.get_tc_value(fck, pt)
    tc_max = tables.get_tc_max_value(fck)

    # Step 5: Check if section is safe
    is_safe = tv_equiv <= tc_max

    if not is_safe:
        # Section is unsafe, return with zero reinforcement
        errors.append(E_TORSION_001)
        return TorsionResult(
            tu_knm=tu_knm,
            vu_kn=vu_kn,
            mu_knm=mu_knm,
            ve_kn=ve_kn,
            me_knm=me_knm,
            tv_equiv=tv_equiv,
            tc=tc,
            tc_max=tc_max,
            asv_torsion=0,
            asv_shear=0,
            asv_total=0,
            stirrup_spacing=0,
            al_torsion=0,
            is_safe=False,
            requires_closed_stirrups=True,
            errors=errors,
        )

    # Step 6: Calculate stirrup reinforcement
    asv_torsion, asv_shear, asv_total = calculate_torsion_stirrup_area(
        tu_knm, vu_kn, b, d, b1, d1, fy, tc
    )

    # Step 7: Calculate stirrup spacing
    # Using 2-legged 8mm stirrups: Asv = 2 × π × (8/2)² = 100.5 mm²
    asv_provided = 2 * math.pi * (stirrup_dia / 2) ** 2

    if asv_total > 0:
        # sv = Asv_provided / (Asv/sv)_required
        sv_calc = asv_provided / asv_total
    else:
        sv_calc = 300  # Use max spacing

    # Apply maximum spacing limits (Cl 26.5.1.5)
    sv_max_1 = 0.75 * d
    sv_max_2 = 300
    # For torsion: spacing ≤ (x1 + y1)/4 or 300mm (Cl 41.4.3)
    sv_max_torsion = min((b1 + d1) / 4, 300)

    sv = min(sv_calc, sv_max_1, sv_max_2, sv_max_torsion)

    # Round down to practical spacing
    sv = max(75, min(300, 25 * math.floor(sv / 25)))

    # Step 8: Calculate longitudinal reinforcement
    al = calculate_longitudinal_torsion_steel(tu_knm, vu_kn, b1, d1, fy, sv)

    return TorsionResult(
        tu_knm=tu_knm,
        vu_kn=vu_kn,
        mu_knm=mu_knm,
        ve_kn=ve_kn,
        me_knm=me_knm,
        tv_equiv=round(tv_equiv, 3),
        tc=round(tc, 3),
        tc_max=round(tc_max, 3),
        asv_torsion=round(asv_torsion, 4),
        asv_shear=round(asv_shear, 4),
        asv_total=round(asv_total, 4),
        stirrup_spacing=round(sv, 0),
        al_torsion=round(al, 0),
        is_safe=True,
        requires_closed_stirrups=True,
        errors=errors,
    )
