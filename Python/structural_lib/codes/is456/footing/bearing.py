# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""IS 456:2000 — Footing bearing capacity and sizing per Cl. 34.1, 34.4.

IMPORTANT: Footing SIZING uses SERVICE (unfactored) loads per IS 456 Cl 34.1.
Structural design (flexure, shear) uses FACTORED loads.

Functions:
    size_footing: Calculate required footing dimensions for bearing capacity
    bearing_stress_enhancement: Enhanced permissible bearing stress per Cl 34.4
"""

from __future__ import annotations

import math

from structural_lib.codes.is456.traceability import clause
from structural_lib.core.data_types import (
    BearingPressureCheckResult,
    BearingStressEnhancementResult,
    FootingBearingResult,
    FootingType,
)
from structural_lib.core.errors import (
    DimensionError,
    ValidationError,
)


@clause("34.1")
def size_footing(
    P_service_kN: float,
    q_safe_kPa: float,
    a_mm: float,
    b_mm: float,
    M_service_kNm: float = 0.0,
    footing_type: FootingType = FootingType.ISOLATED_SQUARE,
) -> FootingBearingResult:
    """Size an isolated footing for safe bearing capacity per IS 456 Cl 34.1.

    Uses SERVICE (unfactored) loads for sizing as required by IS 456 Cl 34.1:
    "In calculating the bearing pressure ... the loads and reactions shall
    be taken as the service values."

    Args:
        P_service_kN: Service (unfactored) axial load (kN)
        q_safe_kPa: Safe bearing capacity of soil (kPa = kN/m²)
        a_mm: Column dimension parallel to footing length (mm)
        b_mm: Column dimension parallel to footing width (mm)
        M_service_kNm: Service moment (kN·m), default 0 (concentric)
        footing_type: ISOLATED_SQUARE or ISOLATED_RECTANGULAR

    Returns:
        FootingBearingResult with sized footing dimensions and bearing check

    Raises:
        ValidationError: If load or bearing capacity is non-positive
        DimensionError: If column dimensions are non-positive

    Limitations:
        - Isolated footings only (square or rectangular); does not handle
          combined footings, strap footings, or raft/mat foundations.
        - Concentric or uniaxial eccentric loading only; biaxial moment
          (Mx + My simultaneously) is not considered.
        - Self-weight of footing and soil overburden are NOT included;
          caller should add 10-15% to P_service_kN to account for these
          (common practice).
        - Does not handle inclined or horizontal loads; for footings
          with lateral loads, sliding and overturning checks must be
          performed separately.
        - Assumes uniform soil bearing capacity; stratified or varying
          soil conditions are not modelled.
        - Dimensions are rounded up to nearest 50mm for constructability.
    """
    if P_service_kN <= 0:
        raise ValidationError(
            "Service load must be positive for footing sizing",
            details={"P_service_kN": P_service_kN},
            clause_ref="Cl. 34.1",
        )
    if q_safe_kPa <= 0:
        raise ValidationError(
            "Safe bearing capacity must be positive",
            details={"q_safe_kPa": q_safe_kPa},
            clause_ref="Cl. 34.1",
        )
    if a_mm <= 0 or b_mm <= 0:
        raise DimensionError(
            "Column dimensions must be positive",
            details={"a_mm": a_mm, "b_mm": b_mm},
        )

    # Required area in mm²  (q_safe_kPa = kN/m² → convert to kN/mm²)
    q_safe_knmm2 = q_safe_kPa / 1e6  # kPa → kN/mm²
    A_req_mm2 = P_service_kN / q_safe_knmm2

    warnings: list[str] = []

    if footing_type == FootingType.ISOLATED_SQUARE:
        L_mm = math.ceil(math.sqrt(A_req_mm2) / 50) * 50  # Round up to 50mm
        B_mm = L_mm
    else:
        # Rectangular: maintain column aspect ratio
        aspect = a_mm / b_mm if b_mm > 0 else 1.0
        B_mm_raw = math.sqrt(A_req_mm2 / aspect)
        B_mm = math.ceil(B_mm_raw / 50) * 50
        L_mm = math.ceil((A_req_mm2 / B_mm) / 50) * 50
        # Ensure area is sufficient after rounding
        if L_mm * B_mm < A_req_mm2:
            L_mm += 50

    # Ensure footing is larger than column
    if L_mm <= a_mm:
        L_mm = math.ceil((a_mm + 200) / 50) * 50  # Min 200mm projection
    if B_mm <= b_mm:
        B_mm = math.ceil((b_mm + 200) / 50) * 50

    # Bearing pressure check (at service loads)
    A_provided_mm2 = L_mm * B_mm

    if abs(M_service_kNm) < 1e-3:
        # Concentric: uniform pressure
        q_max_kPa = (P_service_kN / A_provided_mm2) * 1e6  # kN/mm² → kPa
        q_min_kPa = q_max_kPa
        pressure_type = "uniform"
    else:
        # Eccentric: trapezoidal or partial contact
        e_mm = abs(M_service_kNm * 1e6 / (P_service_kN * 1e3))  # mm
        kern_limit = L_mm / 6.0

        if e_mm <= kern_limit:
            # Trapezoidal pressure
            q_max_kPa = (
                (P_service_kN / A_provided_mm2) * (1.0 + 6.0 * e_mm / L_mm) * 1e6
            )
            q_min_kPa = (
                (P_service_kN / A_provided_mm2) * (1.0 - 6.0 * e_mm / L_mm) * 1e6
            )
            pressure_type = "trapezoidal"
        else:
            # Partial contact — triangular (no tension in soil)
            x = L_mm / 2.0 - e_mm  # Distance from edge to resultant location
            if x <= 0:
                raise ValidationError(
                    "Eccentricity too large — footing lifts off completely",
                    details={"e_mm": e_mm, "L_mm": L_mm, "x": x},
                    clause_ref="Cl. 34.1",
                )
            q_max_kPa = (2.0 * P_service_kN / (3.0 * B_mm * x)) * 1e6
            q_min_kPa = 0.0
            pressure_type = "partial_contact"
            warnings.append(
                f"Eccentricity e={e_mm:.1f}mm exceeds kern limit L/6={kern_limit:.1f}mm. "
                f"Partial contact with soil — consider increasing footing size."
            )

    utilization = q_max_kPa / q_safe_kPa
    is_safe = utilization <= 1.0

    if not is_safe:
        warnings.append(
            f"Bearing pressure q_max={q_max_kPa:.1f}kPa exceeds "
            f"q_safe={q_safe_kPa:.1f}kPa. Increase footing size."
        )

    return FootingBearingResult(
        L_mm=L_mm,
        B_mm=B_mm,
        q_max_kPa=q_max_kPa,
        q_min_kPa=q_min_kPa,
        q_safe_kPa=q_safe_kPa,
        pressure_type=pressure_type,
        utilization_ratio=utilization,
        is_safe=is_safe,
        warnings=tuple(warnings),
    )


@clause("34.4")
def bearing_stress_enhancement(
    fck: float,
    A1_mm2: float,
    A2_mm2: float,
) -> BearingStressEnhancementResult:
    """Enhanced permissible bearing stress per IS 456 Cl 34.4.

    When the supporting area (largest frustum of the footing) is larger
    than the loaded area (column footprint), the permissible bearing
    stress may be enhanced by a factor √(A1/A2), capped at 2.0.

    Args:
        fck: Characteristic compressive strength of concrete (N/mm²).
        A1_mm2: Supporting area — largest frustum of the pyramid that fits
                within the footing and has the loaded area as its upper
                base (mm²).
        A2_mm2: Loaded area — column footprint at the footing top (mm²).

    Returns:
        BearingStressEnhancementResult with enhancement factor and
        permissible bearing stress.

    Raises:
        ValidationError: If fck is non-positive.
        ValidationError: If areas are non-positive.
        ValidationError: If A1 < A2 (supporting area must be ≥ loaded area).

    References:
        IS 456:2000 Cl 34.4
        SP 16:1980 §3.5 — Bearing stress on concrete
    """
    # --- Input validation ---
    if fck <= 0:
        raise ValidationError(
            "Concrete strength fck must be positive",
            details={"fck": fck},
            clause_ref="Cl. 34.4",
        )
    if A1_mm2 <= 0 or A2_mm2 <= 0:
        raise ValidationError(
            "Areas A1 and A2 must be positive",
            details={"A1_mm2": A1_mm2, "A2_mm2": A2_mm2},
            clause_ref="Cl. 34.4",
        )
    if A1_mm2 < A2_mm2:
        raise ValidationError(
            "Supporting area A1 must be ≥ loaded area A2",
            details={"A1_mm2": A1_mm2, "A2_mm2": A2_mm2},
            clause_ref="Cl. 34.4",
        )

    # IS 456 Cl 34.4: Basic permissible bearing stress = 0.45 × fck
    basic_stress_mpa = 0.45 * fck

    # IS 456 Cl 34.4: Enhancement factor = √(A1/A2), capped at 2.0
    ratio = A1_mm2 / A2_mm2
    enhancement_factor = min(math.sqrt(ratio), 2.0)

    # IS 456 Cl 34.4: Enhanced permissible bearing stress
    permissible_stress_mpa = basic_stress_mpa * enhancement_factor

    return BearingStressEnhancementResult(
        basic_stress_mpa=basic_stress_mpa,
        enhancement_factor=enhancement_factor,
        permissible_stress_mpa=permissible_stress_mpa,
        A1_mm2=A1_mm2,
        A2_mm2=A2_mm2,
    )


@clause("34.4")
def check_bearing_pressure(
    Pu_kN: float,
    fck: float,
    column_b_mm: float,
    column_D_mm: float,
    footing_B_mm: float,
    footing_L_mm: float,
) -> BearingPressureCheckResult:
    """Check bearing pressure at column-footing interface per IS 456 Cl 34.4.

    Verifies that the actual bearing stress on the column footprint does not
    exceed the permissible bearing stress enhanced by sqrt(A1/A2).

    Args:
        Pu_kN: Factored axial load on column (kN).
        fck: Characteristic compressive strength of concrete (N/mm²).
        column_b_mm: Column width (mm).
        column_D_mm: Column depth (mm).
        footing_B_mm: Footing width (mm).
        footing_L_mm: Footing length (mm).

    Returns:
        BearingPressureCheckResult with actual stress, permissible stress,
        enhancement factor, utilization ratio, and safety status.

    Raises:
        ValidationError: If Pu_kN or fck is non-positive.
        DimensionError: If column or footing dimensions are non-positive.
        DimensionError: If footing is smaller than column in any direction.

    References:
        IS 456:2000 Cl 34.4
        SP 16:1980 Section 3.5 -- Bearing stress on concrete

    Limitations:
        - Concentric axial load only; does not account for moment
          transfer or eccentric loading at the column-footing interface.
        - Assumes column is centred on footing; edge or corner columns
          with asymmetric frustum geometry are not handled.
        - Does not check dowel bar requirements for load transfer
          (Cl. 34.4.1); use detailing checks separately.
    """
    # --- Input validation ---
    if Pu_kN <= 0:
        raise ValidationError(
            "Factored axial load Pu must be positive",
            details={"Pu_kN": Pu_kN},
            clause_ref="Cl. 34.4",
        )
    if fck <= 0:
        raise ValidationError(
            "Concrete strength fck must be positive",
            details={"fck": fck},
            clause_ref="Cl. 34.4",
        )
    if column_b_mm <= 0 or column_D_mm <= 0:
        raise DimensionError(
            "Column dimensions must be positive",
            details={"column_b_mm": column_b_mm, "column_D_mm": column_D_mm},
        )
    if footing_B_mm <= 0 or footing_L_mm <= 0:
        raise DimensionError(
            "Footing dimensions must be positive",
            details={"footing_B_mm": footing_B_mm, "footing_L_mm": footing_L_mm},
        )
    if footing_B_mm < column_b_mm or footing_L_mm < column_D_mm:
        raise DimensionError(
            "Footing must be larger than or equal to column in both directions",
            details={
                "column_b_mm": column_b_mm,
                "column_D_mm": column_D_mm,
                "footing_B_mm": footing_B_mm,
                "footing_L_mm": footing_L_mm,
            },
        )

    # IS 456 Cl 34.4: Loaded area A2 = column footprint
    A2_mm2 = column_b_mm * column_D_mm

    # IS 456 Cl 34.4: Supporting area A1 = footing area
    A1_mm2 = footing_B_mm * footing_L_mm

    # IS 456 Cl 34.4: Actual bearing stress = Pu / A2
    Pu_N = Pu_kN * 1e3
    actual_stress_mpa = Pu_N / A2_mm2

    # Delegate enhancement factor calculation to existing function
    enhancement_result = bearing_stress_enhancement(
        fck=fck, A1_mm2=A1_mm2, A2_mm2=A2_mm2
    )
    enhancement_factor = enhancement_result.enhancement_factor
    permissible_stress_mpa = enhancement_result.permissible_stress_mpa

    # IS 456 Cl 34.4: Check actual <= permissible
    utilization_ratio = actual_stress_mpa / permissible_stress_mpa
    is_safe = actual_stress_mpa <= permissible_stress_mpa

    return BearingPressureCheckResult(
        actual_stress_mpa=actual_stress_mpa,
        permissible_stress_mpa=permissible_stress_mpa,
        enhancement_factor=enhancement_factor,
        utilization_ratio=utilization_ratio,
        is_safe=is_safe,
        A1_mm2=A1_mm2,
        A2_mm2=A2_mm2,
        Pu_kN=Pu_kN,
    )
