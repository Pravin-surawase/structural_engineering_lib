# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Module: serviceability

Serviceability checks (v0.8 Level A):
- Deflection check using span/depth ratio with explicit modifiers.
- Crack width check using an Annex-F-style crack width estimate.

Design constraints:
- Deterministic outputs.
- Units must be explicit (mm, N/mm²).
- No silent defaults: when a value is assumed, it is recorded in the result.

Note: This module intentionally avoids embedding copyrighted clause text.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from structural_lib.data_types import (
    CrackWidthResult,
    DeflectionLevelBResult,
    DeflectionLevelCResult,
    DeflectionResult,
    ExposureClass,
    SupportCondition,
)

__all__ = [
    "check_deflection_span_depth",
    "check_crack_width",
    "calculate_cracking_moment",
    "calculate_gross_moment_of_inertia",
    "calculate_cracked_moment_of_inertia",
    "calculate_effective_moment_of_inertia",
    "get_long_term_deflection_factor",
    "calculate_short_term_deflection",
    "check_deflection_level_b",
    # Level C functions
    "get_creep_coefficient",
    "calculate_shrinkage_curvature",
    "calculate_creep_deflection",
    "calculate_shrinkage_deflection",
    "check_deflection_level_c",
]

_DEFAULT_BASE_LD: dict[SupportCondition, float] = {
    SupportCondition.CANTILEVER: 7.0,
    SupportCondition.SIMPLY_SUPPORTED: 20.0,
    SupportCondition.CONTINUOUS: 26.0,
}

_DEFAULT_CRACK_LIMITS_MM: dict[ExposureClass, float] = {
    ExposureClass.MILD: 0.3,
    ExposureClass.MODERATE: 0.3,
    ExposureClass.SEVERE: 0.2,
    ExposureClass.VERY_SEVERE: 0.2,
}


def _normalize_support_condition(
    value: Any,
) -> tuple[SupportCondition, str | None]:
    """Normalize support condition input to enum.

    Accepts SupportCondition enum or string aliases ('cantilever', 'ss', etc.).
    Returns tuple of (normalized_enum, warning_message_or_None).
    """
    if isinstance(value, SupportCondition):
        return value, None

    if not isinstance(value, str):
        return (
            SupportCondition.SIMPLY_SUPPORTED,
            f"Invalid support condition '{value}'. Defaulted to SIMPLY_SUPPORTED.",
        )

    normalized = value.strip().lower()
    if normalized in {"cantilever", "cant"}:
        return SupportCondition.CANTILEVER, None
    if normalized in {"simply_supported", "simply", "ss"}:
        return SupportCondition.SIMPLY_SUPPORTED, None
    if normalized in {"continuous", "cont"}:
        return SupportCondition.CONTINUOUS, None

    return (
        SupportCondition.SIMPLY_SUPPORTED,
        f"Unknown support condition '{value}'. Defaulted to SIMPLY_SUPPORTED.",
    )


def _normalize_exposure_class(
    value: Any,
) -> tuple[ExposureClass, str | None]:
    """Normalize exposure class input to enum.

    Accepts ExposureClass enum or string aliases ('mild', 'mod', 'vs', etc.).
    Returns tuple of (normalized_enum, warning_message_or_None).
    """
    if isinstance(value, ExposureClass):
        return value, None

    if not isinstance(value, str):
        return (
            ExposureClass.MODERATE,
            f"Invalid exposure class '{value}'. Defaulted to MODERATE.",
        )

    normalized = value.strip().lower()
    if normalized in {"mild"}:
        return ExposureClass.MILD, None
    if normalized in {"moderate", "mod"}:
        return ExposureClass.MODERATE, None
    if normalized in {"severe"}:
        return ExposureClass.SEVERE, None
    if normalized in {"very severe", "very_severe", "very-severe", "vs"}:
        return ExposureClass.VERY_SEVERE, None

    return (
        ExposureClass.MODERATE,
        f"Unknown exposure class '{value}'. Defaulted to MODERATE.",
    )


def check_deflection_span_depth(
    *,
    span_mm: float,
    d_mm: float,
    support_condition: SupportCondition | str = SupportCondition.SIMPLY_SUPPORTED,
    base_allowable_ld: float | None = None,
    mf_tension_steel: float | None = None,
    mf_compression_steel: float | None = None,
    mf_flanged: float | None = None,
) -> DeflectionResult:
    """Level A deflection check using span/depth ratio.

    Units:
    - span_mm: mm
    - d_mm: mm

    Inputs are treated as purely geometric/serviceability. No moment/shear inputs are accepted.

    Behavior:
    - Computes L/d.
    - Computes allowable L/d = base_allowable_ld × mf_tension_steel × mf_compression_steel × mf_flanged.
    - Records any assumed defaults in `assumptions`.
    """

    assumptions = []

    if span_mm <= 0 or d_mm <= 0:
        return DeflectionResult(
            is_ok=False,
            remarks="Invalid input: span_mm and d_mm must be > 0.",
            support_condition=SupportCondition.SIMPLY_SUPPORTED,
            assumptions=["Invalid inputs provided"],
            inputs={
                "span_mm": span_mm,
                "d_mm": d_mm,
                "support_condition": str(support_condition),
            },
            computed={},
        )

    support, support_note = _normalize_support_condition(support_condition)
    if support_note:
        assumptions.append(support_note)

    if base_allowable_ld is None:
        base_allowable_ld = _DEFAULT_BASE_LD[support]
        assumptions.append(
            f"Used default base allowable L/d for {support.name} (base_allowable_ld={base_allowable_ld})."
        )

    if mf_tension_steel is None:
        mf_tension_steel = 1.0
        assumptions.append("Assumed mf_tension_steel=1.0 (not provided).")

    if mf_compression_steel is None:
        mf_compression_steel = 1.0
        assumptions.append("Assumed mf_compression_steel=1.0 (not provided).")

    if mf_flanged is None:
        mf_flanged = 1.0
        assumptions.append("Assumed mf_flanged=1.0 (not provided).")

    ld_ratio = span_mm / d_mm
    allowable_ld = (
        base_allowable_ld * mf_tension_steel * mf_compression_steel * mf_flanged
    )

    is_ok = ld_ratio <= allowable_ld
    remarks = (
        f"OK: L/d={ld_ratio:.3f} ≤ allowable={allowable_ld:.3f}"
        if is_ok
        else f"NOT OK: L/d={ld_ratio:.3f} > allowable={allowable_ld:.3f}"
    )

    computed: dict[str, Any] = {
        "ld_ratio": ld_ratio,
        "allowable_ld": allowable_ld,
        "base_allowable_ld": base_allowable_ld,
        "mf_tension_steel": mf_tension_steel,
        "mf_compression_steel": mf_compression_steel,
        "mf_flanged": mf_flanged,
    }

    return DeflectionResult(
        is_ok=is_ok,
        remarks=remarks,
        support_condition=support,
        assumptions=assumptions,
        inputs={
            "span_mm": span_mm,
            "d_mm": d_mm,
            "support_condition": support.name,
        },
        computed=computed,
    )


def check_crack_width(
    *,
    exposure_class: ExposureClass | str = ExposureClass.MODERATE,
    limit_mm: float | None = None,
    # Annex-F-style parameters
    acr_mm: float | None = None,
    cmin_mm: float | None = None,
    h_mm: float | None = None,
    x_mm: float | None = None,
    epsilon_m: float | None = None,
    fs_service_nmm2: float | None = None,
    es_nmm2: float = 200000.0,
) -> CrackWidthResult:
    """Level A crack width check.

    Units:
    - geometry: mm
    - stresses: N/mm²

    Calculation uses a documented Annex-F-style relationship:
    wcr = 3 * acr * epsilon_m / (1 + 2(acr - cmin)/(h - x))

    Notes:
    - `epsilon_m` can be supplied directly, or estimated as fs_service_nmm2 / es_nmm2.
    - This function is strict about required inputs: if core parameters are missing,
      it returns is_ok=False with a clear remark (rather than guessing).
    """

    assumptions = []

    exposure, exposure_note = _normalize_exposure_class(exposure_class)
    if exposure_note:
        assumptions.append(exposure_note)

    if limit_mm is None:
        limit_mm = _DEFAULT_CRACK_LIMITS_MM[exposure]
        assumptions.append(
            f"Used default crack width limit for {exposure.name} (limit_mm={limit_mm})."
        )

    if epsilon_m is None:
        if fs_service_nmm2 is None:
            return CrackWidthResult(
                is_ok=False,
                remarks="Missing epsilon_m or fs_service_nmm2 to estimate service steel strain.",
                exposure_class=exposure,
                assumptions=assumptions,
                inputs={
                    "exposure_class": exposure.name,
                    "limit_mm": limit_mm,
                },
                computed={},
            )
        epsilon_m = fs_service_nmm2 / es_nmm2
        assumptions.append("Estimated epsilon_m = fs_service_nmm2 / es_nmm2.")

    missing = [
        name
        for name, val in (
            ("acr_mm", acr_mm),
            ("cmin_mm", cmin_mm),
            ("h_mm", h_mm),
            ("x_mm", x_mm),
        )
        if val is None
    ]
    if missing:
        return CrackWidthResult(
            is_ok=False,
            remarks=f"Missing required inputs for crack width calculation: {', '.join(missing)}.",
            exposure_class=exposure,
            assumptions=assumptions,
            inputs={
                "exposure_class": exposure.name,
                "limit_mm": limit_mm,
                "epsilon_m": epsilon_m,
                "fs_service_nmm2": fs_service_nmm2,
                "es_nmm2": es_nmm2,
            },
            computed={},
        )

    if h_mm <= x_mm:  # type: ignore[operator]
        return CrackWidthResult(
            is_ok=False,
            remarks="Invalid geometry: require h_mm > x_mm.",
            exposure_class=exposure,
            assumptions=assumptions,
            inputs={
                "exposure_class": exposure.name,
                "limit_mm": limit_mm,
                "acr_mm": acr_mm,
                "cmin_mm": cmin_mm,
                "h_mm": h_mm,
                "x_mm": x_mm,
                "epsilon_m": epsilon_m,
            },
            computed={},
        )

    denom = 1.0 + 2.0 * ((acr_mm - cmin_mm) / (h_mm - x_mm))  # type: ignore[operator]
    if denom <= 0:
        return CrackWidthResult(
            is_ok=False,
            remarks="Invalid computed denominator in crack width formula (<= 0).",
            exposure_class=exposure,
            assumptions=assumptions,
            inputs={
                "exposure_class": exposure.name,
                "limit_mm": limit_mm,
                "acr_mm": acr_mm,
                "cmin_mm": cmin_mm,
                "h_mm": h_mm,
                "x_mm": x_mm,
                "epsilon_m": epsilon_m,
            },
            computed={"denom": denom},
        )

    wcr_mm = 3.0 * acr_mm * epsilon_m / denom  # type: ignore[operator]

    is_ok = wcr_mm <= limit_mm
    remarks = (
        f"OK: wcr={wcr_mm:.4f} mm ≤ limit={limit_mm:.4f} mm"
        if is_ok
        else f"NOT OK: wcr={wcr_mm:.4f} mm > limit={limit_mm:.4f} mm"
    )

    computed: dict[str, Any] = {
        "wcr_mm": wcr_mm,
        "limit_mm": limit_mm,
        "acr_mm": acr_mm,
        "cmin_mm": cmin_mm,
        "h_mm": h_mm,
        "x_mm": x_mm,
        "epsilon_m": epsilon_m,
        "denom": denom,
    }

    return CrackWidthResult(
        is_ok=is_ok,
        remarks=remarks,
        exposure_class=exposure,
        assumptions=assumptions,
        inputs={
            "exposure_class": exposure.name,
            "limit_mm": limit_mm,
            "acr_mm": acr_mm,
            "cmin_mm": cmin_mm,
            "h_mm": h_mm,
            "x_mm": x_mm,
            "epsilon_m": epsilon_m,
            "fs_service_nmm2": fs_service_nmm2,
            "es_nmm2": es_nmm2,
        },
        computed=computed,
    )


def _as_dict(result: DeflectionResult | CrackWidthResult) -> dict[str, Any]:
    """Convert a result dataclass to a plain dictionary.

    Convenience function useful for Excel/JSON exports.
    """
    return asdict(result)


# =============================================================================
# Level B Serviceability — Full Deflection Calculation (IS 456 Cl 23.2 / Annex C)
# =============================================================================


def calculate_cracking_moment(
    *,
    b_mm: float,
    D_mm: float,
    fck_nmm2: float,
    yt_mm: float | None = None,
) -> float:
    """Calculate cracking moment Mcr per IS 456 Annex C.

    Mcr = (fcr × Igross) / yt

    where:
    - fcr = 0.7 × √fck (modulus of rupture, N/mm²)
    - Igross = b × D³ / 12 (for rectangular section)
    - yt = D / 2 (distance to extreme tension fiber)

    Args:
        b_mm: Beam width (mm)
        D_mm: Overall depth (mm)
        fck_nmm2: Characteristic concrete strength (N/mm²)
        yt_mm: Distance to extreme tension fiber (mm). Defaults to D/2.

    Returns:
        Cracking moment in kN·m
    """
    import math

    if b_mm <= 0:
        raise ValueError(f"Beam width b_mm must be positive, got {b_mm}")
    if D_mm <= 0:
        raise ValueError(f"Overall depth D_mm must be positive, got {D_mm}")
    if fck_nmm2 <= 0:
        raise ValueError(f"Concrete strength fck_nmm2 must be positive, got {fck_nmm2}")

    fcr = 0.7 * math.sqrt(fck_nmm2)  # N/mm²
    igross = b_mm * (D_mm**3) / 12  # mm^4

    if yt_mm is None:
        yt_mm = D_mm / 2

    if yt_mm <= 0:
        raise ValueError(
            f"Distance to tension fiber yt_mm must be positive, got {yt_mm}"
        )

    mcr_nmm = fcr * igross / yt_mm  # N·mm
    mcr_knm = mcr_nmm / 1e6  # kN·m

    return mcr_knm


def calculate_gross_moment_of_inertia(
    *,
    b_mm: float,
    D_mm: float,
) -> float:
    """Calculate gross moment of inertia Igross for rectangular section.

    Igross = b × D³ / 12

    Args:
        b_mm: Beam width (mm)
        D_mm: Overall depth (mm)

    Returns:
        Gross moment of inertia in mm^4

    Raises:
        ValueError: If dimensions are not positive
    """
    if b_mm <= 0:
        raise ValueError(f"Beam width b_mm must be positive, got {b_mm}")
    if D_mm <= 0:
        raise ValueError(f"Overall depth D_mm must be positive, got {D_mm}")

    return b_mm * (D_mm**3) / 12


def calculate_cracked_moment_of_inertia(
    *,
    b_mm: float,
    d_mm: float,
    ast_mm2: float,
    fck_nmm2: float,
    es_nmm2: float = 200000.0,
) -> float:
    """Calculate cracked moment of inertia Icr for rectangular section.

    Uses transformed section method:
    - m = Es / Ec (modular ratio)
    - Ec = 5000 × √fck (IS 456 Cl 6.2.3.1)

    The neutral axis depth xc for cracked section is found by solving:
    b × xc² / 2 = m × Ast × (d - xc)

    Icr = b × xc³ / 3 + m × Ast × (d - xc)²

    Args:
        b_mm: Beam width (mm)
        d_mm: Effective depth (mm)
        ast_mm2: Area of tension steel (mm²)
        fck_nmm2: Characteristic concrete strength (N/mm²)
        es_nmm2: Elastic modulus of steel (N/mm²). Default 200000.

    Returns:
        Cracked moment of inertia in mm^4
    """
    import math

    if b_mm <= 0:
        raise ValueError(f"Beam width b_mm must be positive, got {b_mm}")
    if d_mm <= 0:
        raise ValueError(f"Effective depth d_mm must be positive, got {d_mm}")
    if ast_mm2 <= 0:
        raise ValueError(f"Steel area ast_mm2 must be positive, got {ast_mm2}")
    if fck_nmm2 <= 0:
        raise ValueError(f"Concrete strength fck_nmm2 must be positive, got {fck_nmm2}")

    ec = 5000 * math.sqrt(fck_nmm2)  # N/mm²
    m = es_nmm2 / ec  # modular ratio

    # Solve for neutral axis depth xc using quadratic formula
    # b × xc² / 2 = m × Ast × (d - xc)
    # b × xc² / 2 + m × Ast × xc - m × Ast × d = 0
    # (b/2) × xc² + (m × Ast) × xc - (m × Ast × d) = 0

    a_coeff = b_mm / 2
    b_coeff = m * ast_mm2
    c_coeff = -m * ast_mm2 * d_mm

    discriminant = b_coeff**2 - 4 * a_coeff * c_coeff
    if discriminant < 0:
        raise ValueError(
            f"Negative discriminant in neutral axis calculation: {discriminant}"
        )

    xc = (-b_coeff + math.sqrt(discriminant)) / (2 * a_coeff)

    if xc <= 0:
        raise ValueError(f"Neutral axis depth xc must be positive, got {xc}")
    if xc >= d_mm:
        raise ValueError(f"Neutral axis depth xc={xc} exceeds effective depth d={d_mm}")

    # Icr = b × xc³ / 3 + m × Ast × (d - xc)²
    icr = b_mm * (xc**3) / 3 + m * ast_mm2 * ((d_mm - xc) ** 2)

    return icr


def calculate_effective_moment_of_inertia(
    *,
    mcr_knm: float,
    ma_knm: float,
    igross_mm4: float,
    icr_mm4: float,
) -> float:
    """Calculate effective moment of inertia Ieff per IS 456 Annex C.

    Branson's equation:
    Ieff = Icr + (Igross - Icr) × (Mcr / Ma)³

    For Ma < Mcr, section is uncracked: Ieff = Igross

    Args:
        mcr_knm: Cracking moment (kN·m)
        ma_knm: Applied service moment (kN·m), absolute value
        igross_mm4: Gross moment of inertia (mm^4)
        icr_mm4: Cracked moment of inertia (mm^4)

    Returns:
        Effective moment of inertia in mm^4
    """
    ma_abs = abs(ma_knm)

    if igross_mm4 <= 0:
        raise ValueError(
            f"Gross moment of inertia igross_mm4 must be positive, got {igross_mm4}"
        )
    if icr_mm4 <= 0:
        raise ValueError(
            f"Cracked moment of inertia icr_mm4 must be positive, got {icr_mm4}"
        )

    if ma_abs <= 0:
        return igross_mm4

    if ma_abs <= mcr_knm:
        # Uncracked section
        return igross_mm4

    # Branson's equation
    ratio = mcr_knm / ma_abs
    ratio_cubed = ratio**3

    ieff = icr_mm4 + (igross_mm4 - icr_mm4) * ratio_cubed

    # Ieff should not be less than Icr
    return max(ieff, icr_mm4)


def get_long_term_deflection_factor(
    *,
    duration_months: int = 60,
    asc_mm2: float = 0.0,
    b_mm: float = 0.0,
    d_mm: float = 0.0,
) -> float:
    """Calculate long-term deflection multiplier per IS 456 Cl 23.2.1.

    The multiplier accounts for creep and shrinkage:
    λ = ξ / (1 + 50 × ρ')

    where:
    - ξ = time-dependent factor (Table below)
    - ρ' = Asc / (b × d) = compression steel ratio

    ξ values (IS 456 Cl 23.2.1):
    - 3 months: 1.0
    - 6 months: 1.2
    - 12 months: 1.4
    - 60 months (5 years) or more: 2.0

    Args:
        duration_months: Duration of load in months. Default 60 (5 years).
        asc_mm2: Area of compression steel (mm²). Default 0.
        b_mm: Beam width (mm). Required if asc_mm2 > 0.
        d_mm: Effective depth (mm). Required if asc_mm2 > 0.

    Returns:
        Long-term deflection multiplier (λ)
    """
    # Time-dependent factor ξ
    if duration_months >= 60:
        xi = 2.0
    elif duration_months >= 12:
        xi = 1.4
    elif duration_months >= 6:
        xi = 1.2
    elif duration_months >= 3:
        xi = 1.0
    else:
        xi = 0.5  # Very short term

    # Compression steel ratio
    rho_prime = 0.0
    if asc_mm2 > 0 and b_mm > 0 and d_mm > 0:
        rho_prime = asc_mm2 / (b_mm * d_mm)

    # Long-term factor
    denominator = 1 + 50 * rho_prime
    if denominator <= 0:
        denominator = 1.0

    lambda_factor = xi / denominator

    return lambda_factor


def calculate_short_term_deflection(
    *,
    ma_knm: float,
    span_mm: float,
    ieff_mm4: float,
    fck_nmm2: float,
    support_condition: SupportCondition | str = SupportCondition.SIMPLY_SUPPORTED,
) -> float:
    """Calculate short-term (immediate) deflection using elastic analysis.

    For simply supported beam with UDL:
    δ = 5 × M × L² / (48 × Ec × Ieff)

    where M is at midspan.

    For cantilever with point load at end:
    δ = M × L² / (2 × Ec × Ieff)

    For continuous beam (approximation):
    δ = 0.6 × simply supported deflection

    Args:
        ma_knm: Applied service moment at critical section (kN·m)
        span_mm: Span length (mm)
        ieff_mm4: Effective moment of inertia (mm^4)
        fck_nmm2: Characteristic concrete strength (N/mm²)
        support_condition: Support type

    Returns:
        Short-term deflection in mm
    """
    import math

    if ma_knm <= 0 or span_mm <= 0 or ieff_mm4 <= 0 or fck_nmm2 <= 0:
        return 0.0

    ec = 5000 * math.sqrt(fck_nmm2)  # N/mm²

    # Convert moment to N·mm
    ma_nmm = abs(ma_knm) * 1e6

    support, _ = _normalize_support_condition(support_condition)

    if support == SupportCondition.CANTILEVER:
        # Cantilever: δ = M × L² / (2 × Ec × Ieff)
        # Using equivalent formula
        delta = ma_nmm * (span_mm**2) / (2 * ec * ieff_mm4)
    elif support == SupportCondition.CONTINUOUS:
        # Continuous: approximately 60% of simply supported
        delta = 0.6 * 5 * ma_nmm * (span_mm**2) / (48 * ec * ieff_mm4)
    else:
        # Simply supported: δ = 5 × M × L² / (48 × Ec × Ieff)
        delta = 5 * ma_nmm * (span_mm**2) / (48 * ec * ieff_mm4)

    return delta


def check_deflection_level_b(
    *,
    b_mm: float,
    D_mm: float,
    d_mm: float,
    span_mm: float,
    ma_service_knm: float,
    ast_mm2: float,
    fck_nmm2: float,
    support_condition: SupportCondition | str = SupportCondition.SIMPLY_SUPPORTED,
    asc_mm2: float = 0.0,
    duration_months: int = 60,
    deflection_limit_ratio: float = 250.0,
    es_nmm2: float = 200000.0,
) -> DeflectionLevelBResult:
    """Level B deflection check with full curvature-based calculation.

    IS 456 Cl 23.2 / Annex C method:
    1. Calculate cracking moment Mcr
    2. Calculate effective moment of inertia Ieff (Branson's equation)
    3. Calculate short-term deflection
    4. Apply long-term factor for creep/shrinkage
    5. Compare total deflection against limit (span/250 or span/350)

    Units:
    - All dimensions: mm
    - Areas: mm²
    - Stresses: N/mm²
    - Moments: kN·m
    - Deflections: mm

    Args:
        b_mm: Beam width (mm)
        D_mm: Overall depth (mm)
        d_mm: Effective depth (mm)
        span_mm: Span length (mm)
        ma_service_knm: Service moment at critical section (kN·m), unfactored
        ast_mm2: Area of tension steel (mm²)
        fck_nmm2: Characteristic concrete strength (N/mm²)
        support_condition: Support type
        asc_mm2: Area of compression steel (mm²). Default 0.
        duration_months: Duration of sustained load in months. Default 60.
        deflection_limit_ratio: Limit as span/ratio. Default 250 (total).
        es_nmm2: Elastic modulus of steel (N/mm²). Default 200000.

    Returns:
        DeflectionLevelBResult with detailed outputs
    """
    assumptions = []
    inputs = {
        "b_mm": b_mm,
        "D_mm": D_mm,
        "d_mm": d_mm,
        "span_mm": span_mm,
        "ma_service_knm": ma_service_knm,
        "ast_mm2": ast_mm2,
        "fck_nmm2": fck_nmm2,
        "asc_mm2": asc_mm2,
        "duration_months": duration_months,
        "deflection_limit_ratio": deflection_limit_ratio,
    }

    # Validate inputs
    if b_mm <= 0 or D_mm <= 0 or d_mm <= 0 or span_mm <= 0:
        return DeflectionLevelBResult(
            is_ok=False,
            remarks="Invalid geometry: all dimensions must be > 0.",
            support_condition=SupportCondition.SIMPLY_SUPPORTED,
            assumptions=["Invalid inputs"],
            inputs=inputs,
            computed={},
        )

    if ast_mm2 <= 0:
        return DeflectionLevelBResult(
            is_ok=False,
            remarks="Invalid input: ast_mm2 must be > 0.",
            support_condition=SupportCondition.SIMPLY_SUPPORTED,
            assumptions=["Invalid inputs"],
            inputs=inputs,
            computed={},
        )

    if ma_service_knm <= 0:
        assumptions.append("Service moment is zero or negative; deflection = 0.")
        return DeflectionLevelBResult(
            is_ok=True,
            remarks="No load applied (Ma ≤ 0). Deflection = 0.",
            support_condition=SupportCondition.SIMPLY_SUPPORTED,
            assumptions=assumptions,
            inputs=inputs,
            computed={"delta_total_mm": 0.0},
            delta_total_mm=0.0,
            delta_limit_mm=span_mm / deflection_limit_ratio,
        )

    support, support_note = _normalize_support_condition(support_condition)
    if support_note:
        assumptions.append(support_note)

    # Step 1: Cracking moment
    mcr_knm = calculate_cracking_moment(b_mm=b_mm, D_mm=D_mm, fck_nmm2=fck_nmm2)

    # Step 2: Gross moment of inertia
    igross = calculate_gross_moment_of_inertia(b_mm=b_mm, D_mm=D_mm)

    # Step 3: Cracked moment of inertia
    icr = calculate_cracked_moment_of_inertia(
        b_mm=b_mm, d_mm=d_mm, ast_mm2=ast_mm2, fck_nmm2=fck_nmm2, es_nmm2=es_nmm2
    )

    # Step 4: Effective moment of inertia (Branson's equation)
    ieff = calculate_effective_moment_of_inertia(
        mcr_knm=mcr_knm, ma_knm=ma_service_knm, igross_mm4=igross, icr_mm4=icr
    )

    if ma_service_knm <= mcr_knm:
        assumptions.append(
            f"Section uncracked (Ma={ma_service_knm:.2f} ≤ Mcr={mcr_knm:.2f}). Using Igross."
        )

    # Step 5: Short-term deflection
    delta_short = calculate_short_term_deflection(
        ma_knm=ma_service_knm,
        span_mm=span_mm,
        ieff_mm4=ieff,
        fck_nmm2=fck_nmm2,
        support_condition=support,
    )

    # Step 6: Long-term factor
    long_term_factor = get_long_term_deflection_factor(
        duration_months=duration_months,
        asc_mm2=asc_mm2,
        b_mm=b_mm,
        d_mm=d_mm,
    )

    # Step 7: Long-term deflection (additional due to creep/shrinkage)
    delta_long = delta_short * long_term_factor

    # Step 8: Total deflection
    delta_total = delta_short + delta_long

    # Step 9: Allowable deflection
    delta_limit = span_mm / deflection_limit_ratio

    # Step 10: Check
    is_ok = delta_total <= delta_limit

    if is_ok:
        remarks = f"OK: δ_total={delta_total:.2f} mm ≤ limit={delta_limit:.2f} mm (span/{deflection_limit_ratio:.0f})"
    else:
        remarks = f"NOT OK: δ_total={delta_total:.2f} mm > limit={delta_limit:.2f} mm (span/{deflection_limit_ratio:.0f})"

    computed = {
        "mcr_knm": mcr_knm,
        "igross_mm4": igross,
        "icr_mm4": icr,
        "ieff_mm4": ieff,
        "delta_short_mm": delta_short,
        "long_term_factor": long_term_factor,
        "delta_long_mm": delta_long,
        "delta_total_mm": delta_total,
        "delta_limit_mm": delta_limit,
    }

    return DeflectionLevelBResult(
        is_ok=is_ok,
        remarks=remarks,
        support_condition=support,
        assumptions=assumptions,
        inputs=inputs,
        computed=computed,
        mcr_knm=mcr_knm,
        igross_mm4=igross,
        icr_mm4=icr,
        ieff_mm4=ieff,
        delta_short_mm=delta_short,
        delta_long_mm=delta_long,
        delta_total_mm=delta_total,
        delta_limit_mm=delta_limit,
        long_term_factor=long_term_factor,
    )


# =============================================================================
# Level C Serviceability Functions (IS 456 Annex C - Detailed Method)
# =============================================================================


def get_creep_coefficient(
    *,
    age_at_loading_days: int = 28,
    relative_humidity_percent: float = 50.0,
    notional_size_mm: float = 150.0,
) -> float:
    """Calculate creep coefficient (θ) per IS 456 Annex C.

    The creep coefficient depends on:
    - Age of concrete at loading
    - Relative humidity of environment
    - Notional size of member (2 * Ac / u, where u = perimeter exposed)

    IS 456 Table C.2 provides values for different conditions.
    This function interpolates based on the simplified model.

    Args:
        age_at_loading_days: Age of concrete when load is applied (days). Default 28.
        relative_humidity_percent: Ambient relative humidity (%). Default 50.
        notional_size_mm: Notional size = 2 * Ac / u (mm). Default 150.

    Returns:
        Creep coefficient θ (dimensionless)

    Reference:
        IS 456:2000, Annex C, Table C.2
    """
    # Base creep coefficient at 28 days loading, 50% RH, h0 = 150mm
    # θ0 ≈ 2.5 for normal conditions

    # Age factor: older concrete has less creep
    # θ(t0) = θ0 / (0.1 + t0^0.2) where t0 = age in days
    if age_at_loading_days < 1:
        age_at_loading_days = 1
    age_factor = 1.0 / (0.1 + (age_at_loading_days**0.2))

    # Humidity factor: higher humidity = less creep
    # φRH = 1 + (1 - RH/100) / (0.1 * h0^(1/3))
    if relative_humidity_percent < 20:
        relative_humidity_percent = 20
    if relative_humidity_percent > 100:
        relative_humidity_percent = 100

    rh_factor = 1.0 + (1.0 - relative_humidity_percent / 100.0) / (
        0.1 * (notional_size_mm ** (1 / 3))
    )

    # Base coefficient
    theta_0 = 2.5

    # Final creep coefficient
    theta = theta_0 * age_factor * rh_factor

    # Limit to reasonable range (0.8 to 4.0)
    result: float = max(0.8, min(4.0, theta))
    return result


def calculate_shrinkage_curvature(
    *,
    eps_cs: float = 0.0003,
    d_mm: float,
    ast_mm2: float,
    asc_mm2: float = 0.0,
    b_mm: float,
    es_nmm2: float = 200000.0,
    fck_nmm2: float = 25.0,
) -> float:
    """Calculate shrinkage curvature per IS 456 Annex C.

    Shrinkage causes curvature due to unequal shrinkage restraint from
    tension and compression steel.

    Shrinkage curvature: φsh = εcs × S / Ieff

    where:
    - εcs = shrinkage strain (typically 0.0003 for normal conditions)
    - S = first moment of area of reinforcement about centroid
    - Ieff = effective moment of inertia

    Simplified approach using steel ratio:
    φsh ≈ εcs × (ρ - ρ') / d × correction factor

    Args:
        eps_cs: Shrinkage strain (dimensionless). Default 0.0003.
        d_mm: Effective depth (mm)
        ast_mm2: Area of tension steel (mm²)
        asc_mm2: Area of compression steel (mm²). Default 0.
        b_mm: Beam width (mm)
        es_nmm2: Elastic modulus of steel (N/mm²). Default 200000.
        fck_nmm2: Characteristic concrete strength (N/mm²). Default 25.

    Returns:
        Shrinkage curvature (1/mm)

    Reference:
        IS 456:2000, Annex C, Cl C-3
    """
    if d_mm <= 0 or b_mm <= 0 or ast_mm2 <= 0:
        return 0.0

    # Steel ratios
    rho_t = ast_mm2 / (b_mm * d_mm)  # Tension steel ratio
    rho_c = asc_mm2 / (b_mm * d_mm)  # Compression steel ratio

    # Modular ratio
    ec_nmm2 = 5000 * (fck_nmm2**0.5)
    m = es_nmm2 / ec_nmm2

    # Shrinkage curvature per IS 456 Annex C
    # φsh = εcs × m × (ρ - ρ') / (1 + m × ρ) × (1/d)
    numerator = eps_cs * m * (rho_t - rho_c)
    denominator = (1 + m * rho_t) * d_mm

    if denominator <= 0:
        return 0.0

    phi_sh = numerator / denominator

    result: float = abs(phi_sh)
    return result


def calculate_creep_deflection(
    *,
    delta_sustained_mm: float,
    creep_coefficient: float,
) -> float:
    """Calculate creep deflection component.

    Creep deflection = Immediate deflection under sustained load × θ

    Args:
        delta_sustained_mm: Immediate deflection under sustained load (mm)
        creep_coefficient: Creep coefficient θ (dimensionless)

    Returns:
        Creep deflection (mm)

    Reference:
        IS 456:2000, Annex C, Cl C-2
    """
    if delta_sustained_mm < 0:
        delta_sustained_mm = 0.0
    if creep_coefficient < 0:
        creep_coefficient = 0.0

    return delta_sustained_mm * creep_coefficient


def calculate_shrinkage_deflection(
    *,
    phi_sh: float,
    span_mm: float,
    support_condition: SupportCondition | str = SupportCondition.SIMPLY_SUPPORTED,
) -> float:
    """Calculate shrinkage deflection from shrinkage curvature.

    Shrinkage deflection depends on curvature distribution and support.

    For simply supported: δsh = k × φsh × L²
    where k depends on curvature distribution (typically 0.125 for uniform)

    Args:
        phi_sh: Shrinkage curvature (1/mm)
        span_mm: Span length (mm)
        support_condition: Support type

    Returns:
        Shrinkage deflection (mm)

    Reference:
        IS 456:2000, Annex C, Cl C-3
    """
    if phi_sh <= 0 or span_mm <= 0:
        return 0.0

    support, _ = _normalize_support_condition(support_condition)

    # Deflection coefficient based on support
    # For parabolic curvature distribution:
    # Simply supported: k = 1/8
    # Cantilever: k = 1/2
    # Continuous: k = 1/12 (approximate)
    if support == SupportCondition.CANTILEVER:
        k = 0.5
    elif support == SupportCondition.CONTINUOUS:
        k = 1 / 12
    else:
        k = 1 / 8

    delta_sh = k * phi_sh * span_mm * span_mm

    return delta_sh


def check_deflection_level_c(
    *,
    b_mm: float,
    D_mm: float,
    d_mm: float,
    span_mm: float,
    ma_sustained_knm: float,
    ma_live_knm: float = 0.0,
    ast_mm2: float,
    fck_nmm2: float,
    support_condition: SupportCondition | str = SupportCondition.SIMPLY_SUPPORTED,
    asc_mm2: float = 0.0,
    age_at_loading_days: int = 28,
    relative_humidity_percent: float = 50.0,
    shrinkage_strain: float = 0.0003,
    deflection_limit_ratio: float = 250.0,
    es_nmm2: float = 200000.0,
) -> DeflectionLevelCResult:
    """Level C deflection check with separate creep and shrinkage.

    IS 456 Annex C detailed method with:
    - Separate creep and shrinkage components
    - Sustained vs live load differentiation
    - Humidity and age of loading factors

    Total deflection = δi,sus + δi,live + δcreep + δshrinkage

    where:
    - δi,sus = immediate deflection under sustained load
    - δi,live = immediate deflection under live load
    - δcreep = creep deflection = θ × δi,sus
    - δshrinkage = shrinkage deflection from curvature

    Units:
    - All dimensions: mm
    - Areas: mm²
    - Stresses: N/mm²
    - Moments: kN·m
    - Deflections: mm

    Args:
        b_mm: Beam width (mm)
        D_mm: Overall depth (mm)
        d_mm: Effective depth (mm)
        span_mm: Span length (mm)
        ma_sustained_knm: Service moment under sustained load (kN·m), unfactored
        ma_live_knm: Service moment under live load (kN·m), unfactored. Default 0.
        ast_mm2: Area of tension steel (mm²)
        fck_nmm2: Characteristic concrete strength (N/mm²)
        support_condition: Support type
        asc_mm2: Area of compression steel (mm²). Default 0.
        age_at_loading_days: Age of concrete at loading (days). Default 28.
        relative_humidity_percent: Ambient relative humidity (%). Default 50.
        shrinkage_strain: Shrinkage strain εcs. Default 0.0003.
        deflection_limit_ratio: Limit as span/ratio. Default 250 (total).
        es_nmm2: Elastic modulus of steel (N/mm²). Default 200000.

    Returns:
        DeflectionLevelCResult with detailed outputs including separate components

    Reference:
        IS 456:2000, Annex C
    """
    assumptions = []
    inputs = {
        "b_mm": b_mm,
        "D_mm": D_mm,
        "d_mm": d_mm,
        "span_mm": span_mm,
        "ma_sustained_knm": ma_sustained_knm,
        "ma_live_knm": ma_live_knm,
        "ast_mm2": ast_mm2,
        "fck_nmm2": fck_nmm2,
        "asc_mm2": asc_mm2,
        "age_at_loading_days": age_at_loading_days,
        "relative_humidity_percent": relative_humidity_percent,
        "shrinkage_strain": shrinkage_strain,
        "deflection_limit_ratio": deflection_limit_ratio,
    }

    # Validate inputs
    if b_mm <= 0 or D_mm <= 0 or d_mm <= 0 or span_mm <= 0:
        return DeflectionLevelCResult(
            is_ok=False,
            remarks="Invalid geometry: all dimensions must be > 0.",
            support_condition=SupportCondition.SIMPLY_SUPPORTED,
            assumptions=["Invalid inputs"],
            inputs=inputs,
            computed={},
        )

    if ast_mm2 <= 0:
        return DeflectionLevelCResult(
            is_ok=False,
            remarks="Invalid input: ast_mm2 must be > 0.",
            support_condition=SupportCondition.SIMPLY_SUPPORTED,
            assumptions=["Invalid inputs"],
            inputs=inputs,
            computed={},
        )

    ma_total_knm = ma_sustained_knm + ma_live_knm
    if ma_total_knm <= 0:
        assumptions.append("Total service moment is zero or negative; deflection = 0.")
        return DeflectionLevelCResult(
            is_ok=True,
            remarks="No load applied (Ma ≤ 0). Deflection = 0.",
            support_condition=SupportCondition.SIMPLY_SUPPORTED,
            assumptions=assumptions,
            inputs=inputs,
            computed={"delta_total_mm": 0.0},
            delta_total_mm=0.0,
            delta_limit_mm=span_mm / deflection_limit_ratio,
        )

    support, support_note = _normalize_support_condition(support_condition)
    if support_note:
        assumptions.append(support_note)

    # Notional size for creep calculation
    # h0 = 2 * Ac / u ≈ 2 * b * D / (2 * (b + D)) = b * D / (b + D)
    notional_size = b_mm * D_mm / (b_mm + D_mm)

    # Step 1: Cracking moment
    mcr_knm = calculate_cracking_moment(b_mm=b_mm, D_mm=D_mm, fck_nmm2=fck_nmm2)

    # Step 2: Gross moment of inertia
    igross = calculate_gross_moment_of_inertia(b_mm=b_mm, D_mm=D_mm)

    # Step 3: Cracked moment of inertia
    icr = calculate_cracked_moment_of_inertia(
        b_mm=b_mm, d_mm=d_mm, ast_mm2=ast_mm2, fck_nmm2=fck_nmm2, es_nmm2=es_nmm2
    )

    # Step 4: Effective moment of inertia at total load
    ieff = calculate_effective_moment_of_inertia(
        mcr_knm=mcr_knm, ma_knm=ma_total_knm, igross_mm4=igross, icr_mm4=icr
    )

    if ma_total_knm <= mcr_knm:
        assumptions.append(
            f"Section uncracked (Ma={ma_total_knm:.2f} ≤ Mcr={mcr_knm:.2f}). Using Igross."
        )

    # Step 5: Immediate deflection under sustained load
    delta_i_sus = 0.0
    if ma_sustained_knm > 0:
        delta_i_sus = calculate_short_term_deflection(
            ma_knm=ma_sustained_knm,
            span_mm=span_mm,
            ieff_mm4=ieff,
            fck_nmm2=fck_nmm2,
            support_condition=support,
        )

    # Step 6: Immediate deflection under live load
    delta_i_live = 0.0
    if ma_live_knm > 0:
        delta_i_live = calculate_short_term_deflection(
            ma_knm=ma_live_knm,
            span_mm=span_mm,
            ieff_mm4=ieff,
            fck_nmm2=fck_nmm2,
            support_condition=support,
        )

    # Total immediate deflection
    delta_immediate = delta_i_sus + delta_i_live

    # Step 7: Creep coefficient
    theta = get_creep_coefficient(
        age_at_loading_days=age_at_loading_days,
        relative_humidity_percent=relative_humidity_percent,
        notional_size_mm=notional_size,
    )

    # Step 8: Creep deflection (only on sustained load)
    delta_creep = calculate_creep_deflection(
        delta_sustained_mm=delta_i_sus,
        creep_coefficient=theta,
    )

    # Step 9: Shrinkage curvature
    phi_sh = calculate_shrinkage_curvature(
        eps_cs=shrinkage_strain,
        d_mm=d_mm,
        ast_mm2=ast_mm2,
        asc_mm2=asc_mm2,
        b_mm=b_mm,
        es_nmm2=es_nmm2,
        fck_nmm2=fck_nmm2,
    )

    # Step 10: Shrinkage deflection
    delta_shrinkage = calculate_shrinkage_deflection(
        phi_sh=phi_sh,
        span_mm=span_mm,
        support_condition=support,
    )

    # Step 11: Total deflection
    delta_total = delta_immediate + delta_creep + delta_shrinkage

    # Step 12: Allowable deflection
    delta_limit = span_mm / deflection_limit_ratio

    # Step 13: Check
    is_ok = delta_total <= delta_limit

    if is_ok:
        remarks = (
            f"OK: δ_total={delta_total:.2f} mm ≤ limit={delta_limit:.2f} mm "
            f"(span/{deflection_limit_ratio:.0f}). "
            f"Components: δ_imm={delta_immediate:.2f}, δ_creep={delta_creep:.2f}, "
            f"δ_shrink={delta_shrinkage:.2f}"
        )
    else:
        remarks = (
            f"NOT OK: δ_total={delta_total:.2f} mm > limit={delta_limit:.2f} mm "
            f"(span/{deflection_limit_ratio:.0f}). "
            f"Components: δ_imm={delta_immediate:.2f}, δ_creep={delta_creep:.2f}, "
            f"δ_shrink={delta_shrinkage:.2f}"
        )

    computed = {
        "mcr_knm": mcr_knm,
        "igross_mm4": igross,
        "icr_mm4": icr,
        "ieff_mm4": ieff,
        "delta_i_sustained_mm": delta_i_sus,
        "delta_i_live_mm": delta_i_live,
        "delta_immediate_mm": delta_immediate,
        "creep_coefficient": theta,
        "delta_creep_mm": delta_creep,
        "shrinkage_curvature": phi_sh,
        "delta_shrinkage_mm": delta_shrinkage,
        "delta_total_mm": delta_total,
        "delta_limit_mm": delta_limit,
    }

    return DeflectionLevelCResult(
        is_ok=is_ok,
        remarks=remarks,
        support_condition=support,
        assumptions=assumptions,
        inputs=inputs,
        computed=computed,
        mcr_knm=mcr_knm,
        igross_mm4=igross,
        icr_mm4=icr,
        ieff_mm4=ieff,
        delta_immediate_mm=delta_immediate,
        delta_creep_mm=delta_creep,
        delta_shrinkage_mm=delta_shrinkage,
        delta_total_mm=delta_total,
        delta_limit_mm=delta_limit,
        creep_coefficient=theta,
        shrinkage_curvature=phi_sh,
    )
