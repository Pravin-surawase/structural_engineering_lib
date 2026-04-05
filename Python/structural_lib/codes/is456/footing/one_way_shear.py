# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""IS 456:2000 — Footing one-way shear check per Cl. 34.2.4.1(a).

Critical section: at distance d from the face of the column.
Checks BOTH directions and reports the governing (worse) one.
Uses FACTORED loads for structural design.
"""

from __future__ import annotations

from structural_lib.codes.is456.footing._common import (
    net_upward_pressure_nmm2,
    validate_footing_inputs,
)
from structural_lib.codes.is456.tables import get_tc_value
from structural_lib.codes.is456.traceability import clause
from structural_lib.core.data_types import FootingOneWayShearResult
from structural_lib.core.errors import ValidationError


def _check_direction(
    qu: float,
    cant_mm: float,
    d_mm: float,
    width_mm: float,
    fck: float,
    pt: float,
    direction_label: str,
) -> tuple[float, float, float, float, bool, list[str]]:
    """Check one-way shear for a single direction.

    Args:
        qu: Net upward pressure (N/mm²)
        cant_mm: Cantilever from column face (mm)
        d_mm: Effective depth (mm)
        width_mm: Width perpendicular to shear direction (mm)
        fck: Concrete strength (N/mm²)
        pt: Steel percentage for Table 19
        direction_label: "L" or "B"

    Returns:
        (tau_v, tau_c, Vu_kN, utilization, is_safe, warnings)
    """
    warnings: list[str] = []
    tau_c = get_tc_value(fck, pt)

    # IS 456 Cl 34.2.4.1(a): critical length = cantilever - d
    Lv_mm = cant_mm - d_mm

    if Lv_mm <= 0:
        warnings.append(
            f"{direction_label}-direction: cantilever {cant_mm:.0f}mm ≤ "
            f"d={d_mm:.0f}mm — one-way shear automatically satisfied"
        )
        return 0.0, tau_c, 0.0, 0.0, True, warnings

    # IS 456 Cl 34.2.4.1(a): Shear force at critical section
    Vu_N = qu * width_mm * Lv_mm
    Vu_kN = Vu_N / 1000.0

    # Nominal shear stress
    tau_v = Vu_N / (width_mm * d_mm)

    utilization = tau_v / tau_c if tau_c > 0 else float("inf")
    is_safe = tau_v <= tau_c

    if not is_safe:
        warnings.append(
            f"{direction_label}-direction: τv={tau_v:.3f} N/mm² exceeds "
            f"τc={tau_c:.3f} N/mm². Increase footing depth."
        )

    return tau_v, tau_c, Vu_kN, utilization, is_safe, warnings


@clause("34.2.4.1")
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

    Checks BOTH directions independently:
    - L-direction: cant = (L-a)/2, Lv = cant - d, Vu = qu × B × Lv
    - B-direction: cant = (B-b)/2, Lv = cant - d, Vu = qu × L × Lv

    Reports the governing (worse utilization) direction.
    is_safe is True only if BOTH directions pass.

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
        FootingOneWayShearResult with governing direction info

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

    # Check both directions
    cant_L = (L_mm - a_mm) / 2.0
    cant_B = (B_mm - b_mm) / 2.0

    tau_v_L, tau_c_L, Vu_L, util_L, safe_L, warn_L = _check_direction(
        qu, cant_L, d_mm, B_mm, fck, pt, "L"
    )
    tau_v_B, tau_c_B, Vu_B, util_B, safe_B, warn_B = _check_direction(
        qu, cant_B, d_mm, L_mm, fck, pt, "B"
    )

    # is_safe only if BOTH directions pass
    is_safe = safe_L and safe_B
    warnings = warn_L + warn_B

    # Report governing (higher utilization) direction
    if util_L >= util_B:
        governing = "L"
        tau_v, tau_c, Vu_kN, utilization = tau_v_L, tau_c_L, Vu_L, util_L
    else:
        governing = "B"
        tau_v, tau_c, Vu_kN, utilization = tau_v_B, tau_c_B, Vu_B, util_B

    return FootingOneWayShearResult(
        tau_v_nmm2=tau_v,
        tau_c_nmm2=tau_c,
        Vu_kN=Vu_kN,
        d_mm=d_mm,
        critical_section_mm=d_mm,
        utilization_ratio=utilization,
        is_safe=is_safe,
        governing_direction=governing,
        warnings=tuple(warnings),
    )
