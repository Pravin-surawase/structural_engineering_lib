# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""IS 456:2000 — Footing punching shear check per Cl. 31.6.1.

Critical section: at distance d/2 from the face of the column.
Permissible stress: ks × 0.25 × √fck, where ks = min(1.0, 0.5 + βc).
Uses FACTORED loads for structural design.

Note: Unlike beams, shear reinforcement is NOT practical in footings
for punching shear. The only remedies are increasing depth or footing size.
"""

from __future__ import annotations

import math

from structural_lib.codes.is456.footing._common import (
    net_upward_pressure_nmm2,
    punching_area_mm2,
    punching_perimeter_mm,
    validate_footing_inputs,
)
from structural_lib.codes.is456.traceability import clause
from structural_lib.core.data_types import FootingPunchingResult
from structural_lib.core.errors import ValidationError


@clause("31.6.1")
def footing_punching_shear(
    Pu_kN: float,
    L_mm: float,
    B_mm: float,
    d_mm: float,
    a_mm: float,
    b_mm: float,
    fck: float,
) -> FootingPunchingResult:
    """Check punching (two-way) shear per IS 456 Cl 31.6.1.

    Critical perimeter at d/2 from column face:
        b0 = 2 × ((a + d) + (b + d))

    Shear force on critical section:
        Vu = Pu - qu × (a + d) × (b + d)

    Nominal shear stress:
        τv = Vu / (b0 × d)

    Permissible stress:
        τc = ks × 0.25 × √fck
        where ks = min(1.0, 0.5 + βc)
        βc = min(a, b) / max(a, b)  (column aspect ratio)

    Args:
        Pu_kN: Factored axial load (kN)
        L_mm: Footing length (mm)
        B_mm: Footing width (mm)
        d_mm: Effective depth (mm)
        a_mm: Column dimension parallel to L (mm)
        b_mm: Column dimension parallel to B (mm)
        fck: Characteristic concrete strength (N/mm²)

    Returns:
        FootingPunchingResult

    Raises:
        DimensionError: If geometry is invalid
        ValidationError: If material properties are invalid

    Limitations:
        - Interior columns only (full punching perimeter); edge and
          corner columns have partial perimeters and require modified
          critical sections not handled here.
        - Concentric load only; does not account for unbalanced moment
          transfer at the column-slab interface (Cl. 31.6.2.2).
        - Shear reinforcement for punching is NOT designed; the only
          remedies are increasing depth, footing size, or using a
          pedestal/drop panel (shear studs outside IS 456 scope).
        - Uniform footing depth assumed; stepped or sloped footings
          are not handled.
        - Does not consider prestress or axial tension effects on
          punching capacity.
    """
    validate_footing_inputs(L_mm, B_mm, d_mm, a_mm, b_mm)

    if fck <= 0:
        raise ValidationError(
            "Concrete strength must be positive",
            details={"fck": fck},
        )

    warnings: list[str] = []

    # Net factored upward pressure
    qu = net_upward_pressure_nmm2(Pu_kN, L_mm, B_mm)

    # Critical perimeter at d/2 from column face
    b0 = punching_perimeter_mm(a_mm, b_mm, d_mm)

    # Area within punching perimeter
    A_punch = punching_area_mm2(a_mm, b_mm, d_mm)

    # Column aspect ratio
    beta_c = min(a_mm, b_mm) / max(a_mm, b_mm)

    # Size effect factor per Cl 31.6.3
    ks = min(1.0, 0.5 + beta_c)

    # Check if punching perimeter exceeds footing
    if (a_mm + d_mm) >= L_mm or (b_mm + d_mm) >= B_mm:
        warnings.append(
            "Punching perimeter extends beyond footing edges — "
            "punching shear is not a concern for this geometry"
        )
        return FootingPunchingResult(
            tau_v_nmm2=0.0,
            tau_c_nmm2=ks * 0.25 * math.sqrt(fck),
            perimeter_mm=b0,
            Vu_punch_kN=0.0,
            d_mm=d_mm,
            beta_c=beta_c,
            ks=ks,
            utilization_ratio=0.0,
            is_safe=True,
            warnings=tuple(warnings),
        )

    # IS 456 Cl 31.6.1: Shear force = total load minus load within punching perimeter
    Vu_N = (Pu_kN * 1000.0) - qu * A_punch
    Vu_kN = Vu_N / 1000.0

    # Nominal shear stress
    tau_v = Vu_N / (b0 * d_mm)

    # IS 456 Cl 31.6.1: Permissible punching shear stress
    # τc = ks × 0.25 × √fck
    tau_c = ks * 0.25 * math.sqrt(fck)

    utilization = tau_v / tau_c if tau_c > 0 else float("inf")
    is_safe = tau_v <= tau_c

    if not is_safe:
        warnings.append(
            f"Punching shear τv={tau_v:.3f} N/mm² exceeds "
            f"τc={tau_c:.3f} N/mm². Increase footing depth or size. "
            f"Shear reinforcement is NOT practical in footings."
        )

    return FootingPunchingResult(
        tau_v_nmm2=tau_v,
        tau_c_nmm2=tau_c,
        perimeter_mm=b0,
        Vu_punch_kN=Vu_kN,
        d_mm=d_mm,
        beta_c=beta_c,
        ks=ks,
        utilization_ratio=utilization,
        is_safe=is_safe,
        warnings=tuple(warnings),
    )
