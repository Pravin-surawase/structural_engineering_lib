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

from structural_lib.core.data_types import TorsionResult
from structural_lib.core.error_messages import material_property_out_of_range
from structural_lib.core.errors import (
    E_TORSION_001,
    DesignError,
    DimensionError,
    MaterialError,
)

from .. import tables
from .._validation import require_finite_real
from ..traceability import clause
from . import flexure

__all__ = [
    "TorsionResult",
    "calculate_equivalent_shear",
    "calculate_equivalent_moment",
    "calculate_torsion_shear_stress",
    "calculate_torsion_stirrup_area",
    "calculate_longitudinal_torsion_steel",
    "design_torsion",
]


def _require_nonnegative_action(name: str, value: object) -> float:
    """Require the documented non-negative magnitude convention."""
    numeric = require_finite_real(name, value)
    if numeric < 0:
        raise ValueError(f"{name} must be >= 0 as a design-action magnitude")
    return numeric


def _require_positive_dimension(name: str, value: object, clause_ref: str) -> float:
    """Require a strictly positive dimension with an exclusive-bound message."""
    numeric = require_finite_real(name, value)
    if numeric <= 0:
        raise DimensionError(
            f"{name} must be > 0 mm (got {numeric:g} mm).",
            details={name: numeric, "minimum_exclusive": 0},
            clause_ref=clause_ref,
        )
    return numeric


def _require_supported_material(
    name: str,
    value: object,
    *,
    minimum: float,
    maximum: float,
    clause_ref: str,
) -> float:
    """Require a material value inside the maintained torsion domain."""
    numeric = require_finite_real(name, value)
    if not minimum <= numeric <= maximum:
        raise MaterialError(
            material_property_out_of_range(name, numeric, minimum, maximum, " N/mm²"),
            details={name: numeric, "minimum": minimum, "maximum": maximum},
            clause_ref=clause_ref,
        )
    return numeric


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
    vu_kn = _require_nonnegative_action("vu_kn", vu_kn)
    tu_knm = _require_nonnegative_action("tu_knm", tu_knm)
    b = _require_positive_dimension("b", b, "Cl. 41.3.1")

    # Tu is in kN·m, b is in mm
    # Convert Tu to kN·mm for dimensional consistency
    tu_kn_mm = tu_knm * 1000  # kN·mm
    ve = vu_kn + 1.6 * tu_kn_mm / b

    return ve


@clause("41.4.2")
def calculate_equivalent_moment(
    mu_knm: float,
    tu_knm: float,
    d: float,
    b: float,
    D_mm: float | None = None,
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
        D_mm: Overall depth (mm). If None, falls back to d + 50
            (deprecated — always pass the actual overall depth).

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
    mu_knm = _require_nonnegative_action("mu_knm", mu_knm)
    tu_knm = _require_nonnegative_action("tu_knm", tu_knm)
    d = _require_positive_dimension("d", d, "Cl. 41.4.2")
    b = _require_positive_dimension("b", b, "Cl. 41.4.2")

    # IS 456 Cl 41.4.2: D is the overall depth of the beam
    if D_mm is not None:
        D = _require_positive_dimension("D_mm", D_mm, "Cl. 41.4.2")
        if d >= D:
            raise DimensionError(
                f"d must be less than D_mm (got d={d:g} mm, D_mm={D:g} mm).",
                details={"d": d, "D_mm": D},
                clause_ref="Cl. 41.4.2",
            )
    else:
        import warnings

        warnings.warn(
            "calculate_equivalent_moment(): D_mm not provided, falling back "
            "to D = d + 50. Pass the actual overall depth D_mm explicitly.",
            DeprecationWarning,
            stacklevel=2,
        )
        D = d + 50

    # IS 456 Cl 41.4.2: Mt = Tu × (1 + D/b) / 1.7
    mt = tu_knm * (1 + D / b) / 1.7

    # IS 456 Cl 41.4.2: Me = Mu + Mt
    me = mu_knm + mt

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
    ve_kn = _require_nonnegative_action("ve_kn", ve_kn)
    b = _require_positive_dimension("b", b, "Cl. 41.3")
    d = _require_positive_dimension("d", d, "Cl. 41.3")

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
        Asv/sv (shear) = Vu / (2.5 × d1 × 0.87 × fy)
        Total is at least (tau_ve - tau_c) × b / (0.87 × fy).

    Reference:
        IS 456:2000, Clause 41.4.3
    """
    tu_knm = _require_nonnegative_action("tu_knm", tu_knm)
    vu_kn = _require_nonnegative_action("vu_kn", vu_kn)
    b = _require_positive_dimension("b", b, "Cl. 41.4.3")
    d = _require_positive_dimension("d", d, "Cl. 41.4.3")
    b1 = _require_positive_dimension("b1", b1, "Cl. 41.4.3")
    d1 = _require_positive_dimension("d1", d1, "Cl. 41.4.3")
    fy = _require_supported_material(
        "fy", fy, minimum=250, maximum=500, clause_ref="Cl. 41.4.3"
    )
    tc = require_finite_real("tc", tc)
    if tc < 0:
        raise ValueError("tc must be >= 0")

    # Torsion component: Asv/sv = Tu / (b1 × d1 × 0.87 × fy)
    # Tu in kN·m, convert to N·mm
    tu_nmm = tu_knm * 1e6
    asv_torsion = tu_nmm / (b1 * d1 * 0.87 * fy)

    # Cl. 41.4.3 uses total Vu in this term, not residual Vu - Vc.
    asv_shear = vu_kn * 1000 / (2.5 * d1 * 0.87 * fy)
    tau_ve = calculate_equivalent_shear(vu_kn, tu_knm, b) * 1000 / (b * d)
    equivalent_floor = max(0.0, (tau_ve - tc) * b / (0.87 * fy))
    asv_total = max(asv_torsion + asv_shear, equivalent_floor)

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
    Retained legacy signature; nonzero torsion requires the complete design route.

    Args:
        tu_knm: Factored torsional moment (kN·m)
        vu_kn: Factored shear force (kN)
        b1: Center-to-center distance between corner bars (width) (mm)
        d1: Center-to-center distance between corner bars (depth) (mm)
        fy: Steel yield strength (N/mm²)
        sv: Stirrup spacing (mm)

    Returns:
        Longitudinal steel area Al (mm²)

    This signature cannot evaluate the equivalent-moment section checks in
    Cl. 41.4.2. It returns zero only for zero torsion and otherwise raises a
    basis-required error. Use ``design_torsion`` with explicit geometry.

    Reference:
        IS 456:2000, Clause 41.4.2.1
    """
    tu_knm = _require_nonnegative_action("tu_knm", tu_knm)
    _require_nonnegative_action("vu_kn", vu_kn)
    b1 = _require_positive_dimension("b1", b1, "Cl. 41.4.2")
    d1 = _require_positive_dimension("d1", d1, "Cl. 41.4.2")
    fy = _require_supported_material(
        "fy", fy, minimum=250, maximum=500, clause_ref="Cl. 41.4.2"
    )
    _require_positive_dimension("sv", sv, "Cl. 41.4.2")

    if tu_knm == 0:
        return 0.0
    raise ValueError(
        "TORSION_LONGITUDINAL_BASIS_REQUIRED: this legacy signature lacks Mu, "
        "section and concrete data needed for Cl. 41.4.2; use design_torsion "
        "with explicit corner-bar geometry and opposite-face effective depth."
    )


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
    *,
    fy_transverse_nmm2: float | None = None,
    corner_bar_centres_mm: tuple[float, float] | None = None,
    d_opposite_mm: float | None = None,
) -> TorsionResult:
    """
    Design beam for combined torsion, shear, and bending.

    Evaluate equivalent actions and required reinforcement per Clause 41.
    This does not generate or accept perimeter reinforcement distribution.

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
        fy_transverse_nmm2: Explicit stirrup grade; legacy omission uses fy.
        corner_bar_centres_mm: Required longitudinal corner-bar b1,d1 (mm).
        d_opposite_mm: Required effective depth for opposite-face tension (mm).

    Returns:
        TorsionResult with complete design output

    Notes:
        - Closed stirrups are mandatory for torsion (Cl 41.4.3)
        - Perimeter distribution per Cl 26.5.1.7 requires separate detailing.
        - Both equivalent moments must fit singly reinforced capacity.
        - If τve > τc,max, section is unsafe and must be redesigned

    Reference:
        IS 456:2000, Clause 41

    Limitations:
        - Rectangular solid sections only; hollow sections, box girders,
          and flanged sections under torsion require different treatment
          (thin-walled torsion theory).
        - Uses IS 456 equivalent shear/moment approach (Cl. 41.3-41.4);
          does not implement the more rigorous space-truss analogy used
          in Eurocode 2 or ACI 318.
        - Compatibility torsion is not distinguished from equilibrium
          torsion; the caller must determine if the applied torsion can
          be redistributed (Cl. 41.1 Note).
        - Does not handle combined torsion with axial load; for
          columns or prestressed members under torsion, separate
          analysis is required.
        - Stirrup design assumes two-legged closed stirrups; multi-leg
          stirrup arrangements are not generated.
        - Valid for fck = 15–40 N/mm² (Table 19/20 range) and
          fy ≤ 500 N/mm².
    """
    tu_knm = _require_nonnegative_action("tu_knm", tu_knm)
    vu_kn = _require_nonnegative_action("vu_kn", vu_kn)
    mu_knm = _require_nonnegative_action("mu_knm", mu_knm)
    b = _require_positive_dimension("b", b, "Cl. 41")
    D = _require_positive_dimension("D", D, "Cl. 41")
    d = _require_positive_dimension("d", d, "Cl. 41")
    fck = _require_supported_material(
        "fck", fck, minimum=15, maximum=40, clause_ref="Cl. 41"
    )
    fy = _require_supported_material(
        "fy", fy, minimum=250, maximum=500, clause_ref="Cl. 41"
    )
    cover = _require_positive_dimension("cover", cover, "Cl. 41")
    stirrup_dia = _require_positive_dimension("stirrup_dia", stirrup_dia, "Cl. 41")
    pt = require_finite_real("pt", pt)

    errors: list[DesignError] = []
    clause_refs = {
        "Ve": "IS 456 Cl 41.3.1",
        "Me": "IS 456 Cl 41.4.2",
        "tau_ve": "IS 456 Cl 41.3.1",
        "Asv_torsion": "IS 456 Cl 41.4.3",
        "Al_torsion": "IS 456 Cl 41.4.2",
        "sv_max": "IS 456 Cl 26.5.1.5 and 26.5.1.7",
    }

    if d >= D:
        raise DimensionError(
            f"d must be less than D (got d={d:g} mm, D={D:g} mm).",
            details={"d": d, "D": D},
            clause_ref="Cl. 41",
        )
    if not 0.15 <= pt <= 3.0:
        raise ValueError("pt must be between 0.15 and 3.0 percent")

    if b - 2 * (cover + stirrup_dia / 2) <= 0 or D - 2 * (cover + stirrup_dia / 2) <= 0:
        raise DimensionError(
            "cover and stirrup_dia must leave a positive closed-stirrup core.",
            details={"cover": cover},
            clause_ref="Cl. 41.4.3",
        )
    if corner_bar_centres_mm is None:
        raise ValueError(
            "TORSION_CORNER_GEOMETRY_REQUIRED: supply b1,d1 between longitudinal "
            "corner-bar centres; clear cover and stirrup diameter are insufficient."
        )
    b1, d1 = corner_bar_centres_mm
    b1 = _require_positive_dimension("b1", b1, "Cl. 41.4.3")
    d1 = _require_positive_dimension("d1", d1, "Cl. 41.4.3")
    if b1 >= b - 2 * (cover + stirrup_dia) or d1 >= D - 2 * (cover + stirrup_dia):
        raise ValueError("corner-bar centres must lie inside the closed stirrup")
    fy_stirrup = _require_supported_material(
        "fy_transverse_nmm2",
        fy if fy_transverse_nmm2 is None else fy_transverse_nmm2,
        minimum=250,
        maximum=500,
        clause_ref="Cl. 41.4.3",
    )
    if d_opposite_mm is None:
        raise ValueError(
            "TORSION_OPPOSITE_DEPTH_REQUIRED: supply opposite-face effective depth"
        )
    d_opposite_mm = _require_positive_dimension(
        "d_opposite_mm", d_opposite_mm, "Cl. 41.4.2"
    )
    if d_opposite_mm >= D:
        raise ValueError("d_opposite_mm must be less than D")

    # Step 1: Calculate equivalent shear (Cl 41.3.1)
    ve_kn = calculate_equivalent_shear(vu_kn, tu_knm, b)

    # Step 2: Calculate equivalent moment (Cl 41.4.2)
    me_knm = calculate_equivalent_moment(mu_knm, tu_knm, d, b, D_mm=D)

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
            Tu_knm=tu_knm,
            Vu_kn=vu_kn,
            Mu_knm=mu_knm,
            Ve_kn=ve_kn,
            Me_knm=me_knm,
            tau_ve=tv_equiv,
            tau_c=tc,
            tau_c_max=tc_max,
            Asv_torsion=0,
            Asv_shear=0,
            Asv_total=0,
            stirrup_spacing=0,
            Al_torsion=0,
            is_safe=False,
            requires_closed_stirrups=True,
            errors=errors,
            clause_refs=clause_refs,
        )

    # Step 6: Calculate stirrup reinforcement
    asv_torsion, asv_shear, asv_total = calculate_torsion_stirrup_area(
        tu_knm, vu_kn, b, d, b1, d1, fy_stirrup, tc
    )
    # Cl. 26.5.1.6 also governs small torsion/equivalent shear.
    asv_total = max(asv_total, 0.4 * b / (0.87 * min(fy_stirrup, 415.0)))

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
    # Cl. 26.5.1.7 uses stirrup dimensions x1,y1, distinct from the
    # longitudinal corner-bar centre dimensions b1,d1 in Cl. 41.4.3.
    x1 = b - 2 * (cover + stirrup_dia / 2)
    y1 = D - 2 * (cover + stirrup_dia / 2)
    sv_max_torsion = min(x1, y1, (x1 + y1) / 4, 300)

    sv = min(sv_calc, sv_max_1, sv_max_2, sv_max_torsion)

    # Round down to practical spacing
    sv = min(300, 25 * math.floor(sv / 25))
    if sv <= 0:
        raise DimensionError(
            "Required closed-stirrup spacing is below the supported 25 mm increment.",
            details={"calculated_spacing": sv_calc},
            clause_ref="Cl. 41.4.3",
        )

    # Cl. 41.4.2: design both equivalent bending moments using the existing
    # flexural owner. This bounded route requires singly reinforced capacity
    # on each face; doubly reinforced coupled torsion is not accepted.
    me_opposite = max(0.0, me_knm - 2 * mu_knm)
    primary = flexure.design_singly_reinforced(
        b=b, d=d, d_total=D, mu_knm=me_knm, fck=fck, fy=fy
    )
    opposite = (
        flexure.design_singly_reinforced(
            b=b, d=d_opposite_mm, d_total=D, mu_knm=me_opposite, fck=fck, fy=fy
        )
        if me_opposite > 0
        else None
    )
    errors.extend(primary.errors)
    if opposite is not None:
        errors.extend(opposite.errors)
    opposite_ast = opposite.Ast_required if opposite is not None else 0.0
    al = primary.Ast_required + opposite_ast

    return TorsionResult(
        Tu_knm=tu_knm,
        Vu_kn=vu_kn,
        Mu_knm=mu_knm,
        Ve_kn=ve_kn,
        Me_knm=me_knm,
        tau_ve=round(tv_equiv, 3),
        tau_c=round(tc, 3),
        tau_c_max=round(tc_max, 3),
        Asv_torsion=round(asv_torsion, 4),
        Asv_shear=round(asv_shear, 4),
        Asv_total=round(asv_total, 4),
        stirrup_spacing=round(sv, 0),
        Al_torsion=round(al, 0),
        is_safe=primary.is_safe and (opposite is None or opposite.is_safe),
        requires_closed_stirrups=True,
        errors=errors,
        clause_refs=clause_refs,
        Me_opposite_knm=me_opposite,
        Ast_opposite_mm2=opposite_ast,
        corner_bar_centres_mm=(b1, d1),
        fy_transverse_nmm2=fy_stirrup,
    )
