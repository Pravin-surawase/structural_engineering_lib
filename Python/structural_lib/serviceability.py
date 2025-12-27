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
from typing import Any, Dict, Optional, Tuple, Union

from .types import (
    CrackWidthResult,
    DeflectionResult,
    DeflectionLevelBResult,
    ExposureClass,
    SupportCondition,
)


_DEFAULT_BASE_LD: Dict[SupportCondition, float] = {
    SupportCondition.CANTILEVER: 7.0,
    SupportCondition.SIMPLY_SUPPORTED: 20.0,
    SupportCondition.CONTINUOUS: 26.0,
}

_DEFAULT_CRACK_LIMITS_MM: Dict[ExposureClass, float] = {
    ExposureClass.MILD: 0.3,
    ExposureClass.MODERATE: 0.3,
    ExposureClass.SEVERE: 0.2,
    ExposureClass.VERY_SEVERE: 0.2,
}


def _normalize_support_condition(
    value: Any,
) -> Tuple[SupportCondition, Optional[str]]:
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
) -> Tuple[ExposureClass, Optional[str]]:
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
    support_condition: Union[SupportCondition, str] = SupportCondition.SIMPLY_SUPPORTED,
    base_allowable_ld: Optional[float] = None,
    mf_tension_steel: Optional[float] = None,
    mf_compression_steel: Optional[float] = None,
    mf_flanged: Optional[float] = None,
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

    computed: Dict[str, Any] = {
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
    exposure_class: Union[ExposureClass, str] = ExposureClass.MODERATE,
    limit_mm: Optional[float] = None,
    # Annex-F-style parameters
    acr_mm: Optional[float] = None,
    cmin_mm: Optional[float] = None,
    h_mm: Optional[float] = None,
    x_mm: Optional[float] = None,
    epsilon_m: Optional[float] = None,
    fs_service_nmm2: Optional[float] = None,
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

    computed: Dict[str, Any] = {
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


def _as_dict(result: Union[DeflectionResult, CrackWidthResult]) -> Dict[str, Any]:
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
    yt_mm: Optional[float] = None,
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

    if b_mm <= 0 or D_mm <= 0 or fck_nmm2 <= 0:
        return 0.0

    fcr = 0.7 * math.sqrt(fck_nmm2)  # N/mm²
    igross = b_mm * (D_mm**3) / 12  # mm^4

    if yt_mm is None:
        yt_mm = D_mm / 2

    if yt_mm <= 0:
        return 0.0

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
    """
    if b_mm <= 0 or D_mm <= 0:
        return 0.0

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

    if b_mm <= 0 or d_mm <= 0 or ast_mm2 <= 0 or fck_nmm2 <= 0:
        return 0.0

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
        return 0.0

    xc = (-b_coeff + math.sqrt(discriminant)) / (2 * a_coeff)

    if xc <= 0 or xc >= d_mm:
        return 0.0

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
    support_condition: Union[SupportCondition, str] = SupportCondition.SIMPLY_SUPPORTED,
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
    support_condition: Union[SupportCondition, str] = SupportCondition.SIMPLY_SUPPORTED,
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
