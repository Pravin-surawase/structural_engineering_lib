# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""IS 456:2000 — Footing flexural design per Cl. 34.2.3.1.

Critical section for bending moment is at the FACE of the column.
Uses FACTORED loads for structural design.
Designs steel in BOTH directions independently.
Applies Cl 34.3.1 steel distribution for rectangular footings.
"""

from __future__ import annotations

from structural_lib.codes.is456.beam.flexure import calculate_ast_required
from structural_lib.codes.is456.footing._common import (
    net_upward_pressure_nmm2,
    validate_footing_inputs,
)
from structural_lib.codes.is456.traceability import clause
from structural_lib.core.data_types import FootingFlexureResult
from structural_lib.core.errors import ValidationError


def _design_direction(
    qu: float,
    width_mm: float,
    cant_mm: float,
    d_mm: float,
    fck: float,
    fy: float,
    direction_label: str,
) -> tuple[float, float, float, list[str]]:
    """Design flexural steel for one direction.

    Args:
        qu: Net upward pressure (N/mm²)
        width_mm: Width perpendicular to cantilever (mm) — the steel-spread width
        cant_mm: Cantilever projection from column face (mm)
        d_mm: Effective depth (mm)
        fck: Concrete strength (N/mm²)
        fy: Steel yield strength (N/mm²)
        direction_label: "L" or "B" for warning messages

    Returns:
        (Mu_kNm, Ast_mm2, pt_percent, warnings)
    """
    warnings: list[str] = []

    # IS 456 Cl 34.2.3.1: Mu = qu × width × cant² / 2
    Mu_Nmm = qu * width_mm * cant_mm**2 / 2.0
    Mu_kNm = Mu_Nmm / 1e6  # N·mm → kN·m

    # Required steel area using beam flexure formula
    Ast_mm2 = calculate_ast_required(width_mm, d_mm, Mu_kNm, fck, fy)

    if Ast_mm2 < 0:
        raise ValidationError(
            f"Footing depth insufficient — moment exceeds singly reinforced "
            f"capacity in {direction_label}-direction",
            details={"Mu_kNm": Mu_kNm, "d_mm": d_mm, "width_mm": width_mm},
            suggestion="Increase footing depth",
            clause_ref="Cl. 34.2.3.1",
        )

    # Steel percentage
    pt = (Ast_mm2 / (width_mm * d_mm)) * 100.0

    # IS 456 Cl 26.5.2.1: Minimum steel check
    pt_min = 0.12 if fy >= 415 else 0.15
    if pt < pt_min:
        Ast_mm2 = pt_min * width_mm * d_mm / 100.0
        pt = pt_min
        warnings.append(
            f"{direction_label}-direction: steel increased to minimum "
            f"{pt_min}% per Cl 26.5.2.1"
        )

    return Mu_kNm, Ast_mm2, pt, warnings


@clause("34.2.3.1")
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

    Designs steel in BOTH directions independently:
    - L-direction: Mu_L = qu × B × cant_L² / 2, steel spread over width B
    - B-direction: Mu_B = qu × L × cant_B² / 2, steel spread over width L

    For rectangular footings (L ≠ B), applies Cl 34.3.1 steel distribution:
    fraction 2/(β+1) of short-direction steel in central band of width = short dim.

    Note: Uses FACTORED load Pu_kN for structural design,
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
        FootingFlexureResult with moment and steel area for both directions

    Raises:
        DimensionError: If geometry is invalid
        ValidationError: If material properties are invalid

    Limitations:
        - Isolated footings only; combined and raft footings require
          continuous beam/plate analysis.
        - Uniform pressure distribution assumed (concentric load); for
          eccentric loading, the trapezoidal or partial pressure
          distribution must be handled externally.
        - Singly reinforced section only; if the calculated moment
          exceeds singly reinforced capacity, a ValidationError is raised—
          increase footing depth rather than using compression steel.
        - Does not account for footing self-weight or soil overburden
          in the moment calculation (conservative for gravity loads).
        - One-directional bending per direction; does not consider
          biaxial moment effects on steel distribution.
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

    # IS 456 Cl 34.2.3.1: Design BOTH directions independently
    # L-direction: moment about B-axis, steel runs parallel to L, spread over width B
    Mu_L_kNm, Ast_L_mm2, pt_L, warn_L = _design_direction(
        qu, B_mm, cant_L, d_mm, fck, fy, "L"
    )
    # B-direction: moment about L-axis, steel runs parallel to B, spread over width L
    Mu_B_kNm, Ast_B_mm2, pt_B, warn_B = _design_direction(
        qu, L_mm, cant_B, d_mm, fck, fy, "B"
    )

    warnings = warn_L + warn_B

    # IS 456 Cl 34.3.1: Steel distribution for rectangular footings
    # In the short direction, fraction 2/(β+1) goes in central band = short dim
    central_band_fraction = 1.0
    long_side = max(L_mm, B_mm)
    short_side = min(L_mm, B_mm)
    if abs(long_side - short_side) > 1.0:  # Not square (tolerance 1mm)
        beta = long_side / short_side  # β = L_long / L_short
        central_band_fraction = 2.0 / (beta + 1.0)
        short_dir = "B" if B_mm < L_mm else "L"
        warnings.append(
            f"Cl 34.3.1: Rectangular footing β={beta:.2f}. "
            f"In {short_dir}-direction (short), {central_band_fraction:.3f} "
            f"of total steel in central band of width {short_side:.0f}mm."
        )

    return FootingFlexureResult(
        Mu_L_kNm=Mu_L_kNm,
        Ast_L_mm2=Ast_L_mm2,
        pt_L_percent=pt_L,
        cantilever_L_mm=cant_L,
        Mu_B_kNm=Mu_B_kNm,
        Ast_B_mm2=Ast_B_mm2,
        pt_B_percent=pt_B,
        cantilever_B_mm=cant_B,
        d_mm=d_mm,
        is_safe=True,
        central_band_fraction=central_band_fraction,
        warnings=tuple(warnings),
    )
