# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""IS 456:2000 — Footing one-way shear check per Cl. 34.2.4.1(a).

Critical section: at distance d from the face of the column.
Uses FACTORED loads for structural design.
"""

from __future__ import annotations

from structural_lib.codes.is456.footing._common import (
    net_upward_pressure_nmm2,
    validate_footing_inputs,
)
from structural_lib.codes.is456.tables import get_tc_value
from structural_lib.core.data_types import FootingOneWayShearResult
from structural_lib.core.errors import ValidationError


def footing_one_way_shear(
    Pu_kN: float,
    L_mm: float,
    B_mm: float,
    d_mm: float,
    a_mm: float,
    b_mm: float,
    fck: float,
    pt: float = 0.15,
) -> FootingOneWayShearResult:
    """Check one-way shear at distance d from column face per IS 456 Cl 34.2.4.1(a).

    Critical section at distance d from the face of the column.
    Vu = qu × B × ((L - a)/2 - d)
    τv = Vu / (B × d)
    Compare with τc from Table 19.

    If (L - a)/2 ≤ d, shear is automatically satisfied (critical section
    is at or beyond footing edge).

    Args:
        Pu_kN: Factored axial load (kN)
        L_mm: Footing length (mm)
        B_mm: Footing width (mm)
        d_mm: Effective depth (mm)
        a_mm: Column dimension parallel to L (mm)
        b_mm: Column dimension parallel to B (mm)
        fck: Characteristic concrete strength (N/mm²)
        pt: Steel percentage for Table 19 lookup (default 0.15%)

    Returns:
        FootingOneWayShearResult

    Raises:
        DimensionError: If geometry is invalid
        ValidationError: If material properties are invalid
    """
    validate_footing_inputs(L_mm, B_mm, d_mm, a_mm, b_mm)

    if fck <= 0:
        raise ValidationError(
            "Concrete strength must be positive",
            details={"fck": fck},
        )

    qu = net_upward_pressure_nmm2(Pu_kN, L_mm, B_mm)
    warnings: list[str] = []

    # Cantilever minus d
    cant = (L_mm - a_mm) / 2.0
    shear_span = cant - d_mm

    if shear_span <= 0:
        # Critical section at or beyond footing edge — shear auto-passes
        warnings.append(
            f"Cantilever {cant:.0f}mm ≤ d={d_mm:.0f}mm: "
            f"one-way shear automatically satisfied"
        )
        return FootingOneWayShearResult(
            tau_v_nmm2=0.0,
            tau_c_nmm2=get_tc_value(fck, pt),
            Vu_kN=0.0,
            d_mm=d_mm,
            critical_section_mm=d_mm,
            utilization_ratio=0.0,
            is_safe=True,
            warnings=tuple(warnings),
        )

    # IS 456 Cl 34.2.4.1(a): Shear force at critical section
    Vu_N = qu * B_mm * shear_span
    Vu_kN = Vu_N / 1000.0

    # Nominal shear stress
    tau_v = Vu_N / (B_mm * d_mm)

    # Design shear strength from Table 19
    tau_c = get_tc_value(fck, pt)

    utilization = tau_v / tau_c if tau_c > 0 else float("inf")
    is_safe = tau_v <= tau_c

    if not is_safe:
        warnings.append(
            f"One-way shear τv={tau_v:.3f} N/mm² exceeds τc={tau_c:.3f} N/mm². "
            f"Increase footing depth."
        )

    return FootingOneWayShearResult(
        tau_v_nmm2=tau_v,
        tau_c_nmm2=tau_c,
        Vu_kN=Vu_kN,
        d_mm=d_mm,
        critical_section_mm=d_mm,
        utilization_ratio=utilization,
        is_safe=is_safe,
        warnings=tuple(warnings),
    )
