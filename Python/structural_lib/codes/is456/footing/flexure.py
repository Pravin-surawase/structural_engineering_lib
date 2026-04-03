# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""IS 456:2000 — Footing flexural design per Cl. 34.2.3.1.

Critical section for bending moment is at the FACE of the column.
Uses FACTORED loads for structural design.
"""

from __future__ import annotations

from structural_lib.codes.is456.beam.flexure import calculate_ast_required
from structural_lib.codes.is456.footing._common import (
    net_upward_pressure_nmm2,
    validate_footing_inputs,
)
from structural_lib.core.data_types import FootingFlexureResult
from structural_lib.core.errors import ValidationError


def footing_flexure(
    Pu_kN: float,
    L_mm: float,
    B_mm: float,
    d_mm: float,
    a_mm: float,
    b_mm: float,
    fck: float,
    fy: float,
) -> FootingFlexureResult:
    """Calculate bending moment and required steel at column face per IS 456 Cl 34.2.3.1.

    Critical section: face of column.
    Cantilever projection = (L - a) / 2.
    Mu = qu × B × l² / 2  (for uniform pressure, concentric load).

    Note: This function uses FACTORED load Pu_kN for structural design,
    distinct from service loads used for sizing (see bearing.py).

    Args:
        Pu_kN: Factored axial load (kN)
        L_mm: Footing length (mm)
        B_mm: Footing width (mm)
        d_mm: Effective depth (mm)
        a_mm: Column dimension parallel to L (mm)
        b_mm: Column dimension parallel to B (mm)
        fck: Characteristic concrete strength (N/mm²)
        fy: Steel yield strength (N/mm²)

    Returns:
        FootingFlexureResult with moment, steel area, and percentage

    Raises:
        DimensionError: If geometry is invalid
        ValidationError: If material properties are invalid
    """
    validate_footing_inputs(L_mm, B_mm, d_mm, a_mm, b_mm)

    if fck <= 0 or fy <= 0:
        raise ValidationError(
            "Material strengths must be positive",
            details={"fck": fck, "fy": fy},
        )

    # Net factored upward pressure (N/mm²)
    qu = net_upward_pressure_nmm2(Pu_kN, L_mm, B_mm)

    # Cantilever projection from column face (both directions)
    cant_L = (L_mm - a_mm) / 2.0  # Along length
    cant_B = (B_mm - b_mm) / 2.0  # Along width

    warnings: list[str] = []

    # IS 456 Cl 34.2.3.1: Moment at face along L (steel in B direction)
    # M_u = qu × B × cant_L² / 2
    Mu_L_Nmm = qu * B_mm * cant_L**2 / 2.0
    Mu_L_kNm = Mu_L_Nmm / 1e6  # N·mm → kN·m

    # Moment at face along B (steel in L direction)
    Mu_B_Nmm = qu * L_mm * cant_B**2 / 2.0
    Mu_B_kNm = Mu_B_Nmm / 1e6

    # Design steel for the critical (larger) moment
    # For square footing with square column, both are equal
    Mu_design_kNm = max(Mu_L_kNm, Mu_B_kNm)
    cant_design = cant_L if Mu_L_kNm >= Mu_B_kNm else cant_B
    b_design = B_mm if Mu_L_kNm >= Mu_B_kNm else L_mm

    # Required steel area using beam flexure formula
    Ast_mm2 = calculate_ast_required(b_design, d_mm, Mu_design_kNm, fck, fy)

    if Ast_mm2 < 0:
        # Moment exceeds section capacity
        raise ValidationError(
            "Footing depth insufficient — moment exceeds singly reinforced capacity",
            details={"Mu_kNm": Mu_design_kNm, "d_mm": d_mm, "b_mm": b_design},
            suggestion="Increase footing depth",
            clause_ref="Cl. 34.2.3.1",
        )

    # Steel percentage
    pt = (Ast_mm2 / (b_design * d_mm)) * 100.0

    # Minimum steel check (0.12% for HYSD, 0.15% for mild steel)
    pt_min = 0.12 if fy >= 415 else 0.15
    if pt < pt_min:
        Ast_mm2 = pt_min * b_design * d_mm / 100.0
        pt = pt_min
        warnings.append(f"Steel increased to minimum {pt_min}% per Cl 26.5.2.1")

    return FootingFlexureResult(
        Mu_kNm=Mu_design_kNm,
        Ast_mm2=Ast_mm2,
        pt_percent=pt,
        cantilever_mm=cant_design,
        d_mm=d_mm,
        is_safe=True,
        warnings=tuple(warnings),
    )
