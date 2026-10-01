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

import math
from dataclasses import asdict
from typing import Any

from structural_lib.codes.is456.traceability import clause
from structural_lib.core.data_types import (
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
    ExposureClass.VERY_SEVERE: 0.1,
    ExposureClass.EXTREME: 0.1,
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
    if normalized == "extreme":
        return ExposureClass.EXTREME, None

    return (
        ExposureClass.MODERATE,
        f"Unknown exposure class '{value}'. Defaulted to MODERATE.",
    )


@clause("23.2.1")
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

    Limitations:
        - Rectangular beams and one-way slabs only; two-way slabs use
          different span/depth ratios (IS 456 Cl. 24.1).
        - Modification factors must be supplied by the caller; if omitted,
          defaults to 1.0 which may be unconservative for high steel
          percentages (Cl. 23.2.1, Fig. 4).
        - Does not compute actual deflection; this is a deemed-to-satisfy
          check only. For precise deflection values use
          ``check_deflection_level_b`` or ``check_deflection_level_c``.
        - Continuous beams use a single base L/d; does not distinguish
          between end span and interior span values.
        - Does not account for construction loading or propping conditions.
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


@clause("43.1")
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

    Limitations:
        - Rectangular sections only; flanged sections require modified
          acr calculations for the flange region.
        - Uses simplified Annex-F formula; does not implement the full
          CEB-FIP or Eurocode crack spacing model.
        - Service (unfactored) stresses must be supplied by the caller;
          this function does not perform load factoring.
        - Applicable to flexural cracks only; does not cover shear cracks
          or cracks due to restrained shrinkage/thermal effects.
        - Does not account for bar coating (epoxy-coated bars have
          different bond characteristics affecting crack width).
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


@clause("C-2")
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


@clause("C-2")
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


@clause("C-2")
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


@clause("C-2")
def calculate_effective_moment_of_inertia(
    *,
    mcr_knm: float,
    ma_knm: float,
    igross_mm4: float,
    icr_mm4: float,
    d_mm: float | None = None,
    x_mm: float | None = None,
) -> float:
    """Annex C-2.1 effective inertia for a singly reinforced rectangle.

    For cracked sections z=d-x/3 and bw/b=1. The source expression is
    Icr/[1.2-(Mr/|M|)(z/d)(1-x/d)], bounded by Icr and Ig. The formerly
    used cubic Branson expression is a different model. Calls without the
    required geometry can determine an uncracked Ig, but cannot qualify a
    cracked-section IS456 result. Moments are unfactored service moments.
    """
    if not all(math.isfinite(v) and v > 0 for v in (igross_mm4, icr_mm4)):
        raise ValueError("Gross and cracked inertias must be finite and positive.")
    if icr_mm4 > igross_mm4:
        raise ValueError("Annex C bounds require Icr <= Ig for this section model.")
    if not math.isfinite(mcr_knm) or mcr_knm <= 0 or not math.isfinite(ma_knm):
        raise ValueError("Cracking moment must be positive; service moment finite.")
    ma_abs = abs(ma_knm)
    if ma_abs <= mcr_knm:
        return igross_mm4
    if d_mm is None or x_mm is None:
        raise ValueError("Annex C-2.1 requires d_mm and cracked neutral axis x_mm.")
    if not (math.isfinite(d_mm) and math.isfinite(x_mm) and 0 < x_mm < d_mm):
        raise ValueError("Require finite 0 < x_mm < d_mm.")
    z_mm = d_mm - x_mm / 3
    denominator = 1.2 - (mcr_knm / ma_abs) * (z_mm / d_mm) * (1 - x_mm / d_mm)
    return min(igross_mm4, max(icr_mm4, icr_mm4 / denominator))


def get_long_term_deflection_factor(
    *,
    duration_months: int = 60,
    asc_mm2: float = 0.0,
    b_mm: float = 0.0,
    d_mm: float = 0.0,
) -> float:
    """Legacy empirical multiplier retained for compatibility, without IS attribution.

    xi/(1+50*rho') and the 3/6/12/60 month xi values are not the source
    Annex C-3/C-4 procedure. This helper does not qualify an IS456 long-term
    check and is not used by Level B/C. No code-derived accuracy is claimed.
    """
    if duration_months >= 60:
        xi = 2.0
    elif duration_months >= 12:
        xi = 1.4
    elif duration_months >= 6:
        xi = 1.2
    elif duration_months >= 3:
        xi = 1.0
    else:
        xi = 0.5
    rho_prime = (
        asc_mm2 / (b_mm * d_mm) if asc_mm2 > 0 and b_mm > 0 and d_mm > 0 else 0.0
    )
    return xi / (1 + 50 * rho_prime)


def _sls_support(value: SupportCondition | str) -> SupportCondition:
    support, note = _normalize_support_condition(value)
    if note:
        raise ValueError(
            "Unsupported support condition; no assumed boundary condition."
        )
    if support == SupportCondition.CONTINUOUS:
        raise ValueError(
            "Continuous Annex C checks require support/midspan moments and Table 25 averaging."
        )
    return support


def _elastic_deflection(
    moment_knm: float,
    span_mm: float,
    ec_nmm2: float,
    inertia_mm4: float,
    support: SupportCondition,
) -> float:
    # Double integration of EI*v''=M(x): SS UDL, or cantilever end point load.
    coefficient = 1 / 3 if support == SupportCondition.CANTILEVER else 5 / 48
    return coefficient * abs(moment_knm) * 1e6 * span_mm**2 / (ec_nmm2 * inertia_mm4)


@clause("23.2")
def calculate_short_term_deflection(
    *,
    ma_knm: float,
    span_mm: float,
    ieff_mm4: float,
    fck_nmm2: float,
    support_condition: SupportCondition | str = SupportCondition.SIMPLY_SUPPORTED,
) -> float:
    """Elastic deflection magnitude for the declared service load pattern.

    SS uniformly distributed load: 5*|Mmid|*L²/(48*Ec*I).
    Cantilever end point load: |Mroot|*L²/(3*Ec*I), from P*L³/(3*Ec*I).
    A continuous frame or another load pattern cannot be inferred from one M.
    Ec=5000*sqrt(fck); no ultimate material factors enter this SLS calculation.
    """
    if not all(
        math.isfinite(v) and v > 0 for v in (span_mm, ieff_mm4, fck_nmm2)
    ) or not math.isfinite(ma_knm):
        raise ValueError(
            "Require finite service moment and positive span, inertia and fck."
        )
    return _elastic_deflection(
        ma_knm,
        span_mm,
        5000 * math.sqrt(fck_nmm2),
        ieff_mm4,
        _sls_support(support_condition),
    )


SLS_METHOD = "IS456_ANNEX_C_RECT_SINGLE_V1"


def _sls_geometry(
    b_mm: float,
    D_mm: float,
    d_mm: float,
    span_mm: float,
    ast_mm2: float,
    asc_mm2: float,
    fck_nmm2: float,
    es_nmm2: float,
    limit_ratio: float,
) -> None:
    if (
        not all(math.isfinite(v) and v > 0 for v in (b_mm, D_mm, d_mm, span_mm))
        or d_mm >= D_mm
    ):
        raise ValueError(
            "Invalid geometry: require positive dimensions and d_mm < D_mm."
        )
    if (
        not math.isfinite(ast_mm2)
        or ast_mm2 <= 0
        or not math.isfinite(asc_mm2)
        or asc_mm2 < 0
    ):
        raise ValueError("Invalid input: require Ast > 0 and Asc >= 0.")
    if asc_mm2:
        raise ValueError(
            "Compression steel requires its depth/layout for the cracked section; this scalar API lacks it."
        )
    if not math.isfinite(fck_nmm2) or not 15 <= fck_nmm2 <= 55:
        raise ValueError(
            "Default IS456 SLS material parameters require 15 <= fck <= 55; higher grades need additional data."
        )
    if not all(math.isfinite(v) and v > 0 for v in (es_nmm2, limit_ratio)):
        raise ValueError("Require positive finite Es and deflection limit ratio.")


def _sls_section(
    b_mm: float,
    D_mm: float,
    d_mm: float,
    ast_mm2: float,
    ec_nmm2: float,
    es_nmm2: float,
    mcr_knm: float,
    moment_knm: float,
) -> dict[str, float]:
    transformed_steel = (es_nmm2 / ec_nmm2) * ast_mm2
    x = (
        2
        * transformed_steel
        * d_mm
        / (
            transformed_steel
            + math.sqrt(transformed_steel**2 + 2 * b_mm * transformed_steel * d_mm)
        )
    )
    icr = b_mm * x**3 / 3 + transformed_steel * (d_mm - x) ** 2
    ig = b_mm * D_mm**3 / 12
    ieff = calculate_effective_moment_of_inertia(
        mcr_knm=mcr_knm,
        ma_knm=moment_knm,
        igross_mm4=ig,
        icr_mm4=icr,
        d_mm=d_mm,
        x_mm=x,
    )
    return {
        "ec_nmm2": ec_nmm2,
        "x_mm": x,
        "z_mm": d_mm - x / 3,
        "icr_mm4": icr,
        "igross_mm4": ig,
        "ieff_mm4": ieff,
    }


def _sls_hold(
    result_type: type[DeflectionLevelBResult] | type[DeflectionLevelCResult],
    inputs: dict[str, Any],
    reason: str,
    support: SupportCondition = SupportCondition.SIMPLY_SUPPORTED,
    computed: dict[str, Any] | None = None,
    **values: float,
) -> DeflectionLevelBResult | DeflectionLevelCResult:
    details = {
        "method": SLS_METHOD,
        "status": "HOLD_UNSUPPORTED",
        "reason": reason,
        **(computed or {}),
    }
    ratio = inputs["deflection_limit_ratio"]
    span = inputs["span_mm"]
    limit = (
        span / ratio
        if math.isfinite(ratio) and ratio > 0 and math.isfinite(span) and span > 0
        else 0.0
    )
    return result_type(
        is_ok=False,
        remarks=f"HOLD_UNSUPPORTED: {reason}",
        support_condition=support,
        assumptions=[
            "No qualified total deflection is available for this input domain."
        ],
        inputs=inputs,
        computed=details,
        delta_total_mm=math.inf,
        delta_limit_mm=limit,
        **values,
    )


@clause("23.2", "C-2")
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
    """Report Annex C immediate deflection; hold the unqualified long-term check.

    One service moment and a duration cannot identify permanent load, loading
    age or shrinkage. The previous duration multiplier was not the IS456
    Annex C method. This retained API returns is_ok=False/HOLD_UNSUPPORTED,
    with qualified immediate outputs where possible. Use Level C for its
    explicitly supported permanent/live service-load and shrinkage domain.
    """
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
        "es_nmm2": es_nmm2,
        "support_condition": str(support_condition),
    }
    support = SupportCondition.SIMPLY_SUPPORTED
    try:
        _sls_geometry(
            b_mm,
            D_mm,
            d_mm,
            span_mm,
            ast_mm2,
            asc_mm2,
            fck_nmm2,
            es_nmm2,
            deflection_limit_ratio,
        )
        support = _sls_support(support_condition)
        if not math.isfinite(ma_service_knm):
            raise ValueError("Service moment must be finite.")
        mcr = calculate_cracking_moment(b_mm=b_mm, D_mm=D_mm, fck_nmm2=fck_nmm2)
        section = _sls_section(
            b_mm,
            D_mm,
            d_mm,
            ast_mm2,
            5000 * math.sqrt(fck_nmm2),
            es_nmm2,
            mcr,
            ma_service_knm,
        )
        short = _elastic_deflection(
            ma_service_knm, span_mm, section["ec_nmm2"], section["ieff_mm4"], support
        )
    except ValueError as exc:
        return _sls_hold(DeflectionLevelBResult, inputs, str(exc), support)  # type: ignore[return-value]
    return _sls_hold(DeflectionLevelBResult, inputs, "Long-term basis missing: permanent load, loading age and shrinkage cannot be inferred from duration_months.", support, computed={**section, "mcr_knm": mcr, "delta_short_mm": short, "load_basis": "UNFACTORED_SERVICE"}, mcr_knm=mcr, igross_mm4=section["igross_mm4"], icr_mm4=section["icr_mm4"], ieff_mm4=section["ieff_mm4"], delta_short_mm=short, delta_long_mm=math.inf, long_term_factor=math.inf)  # type: ignore[return-value]


@clause("6.2.5.1")
def get_creep_coefficient(
    *,
    age_at_loading_days: int = 28,
    relative_humidity_percent: float = 50.0,
    notional_size_mm: float = 150.0,
) -> float:
    """Ultimate default theta at the three source loading ages: 7/28/365 days.

    IS456 Cl6.2.5.1 gives 2.2/1.6/1.1 in the absence of experimental data.
    It does not give the former humidity/size equation or an interpolation
    rule. Humidity and size are retained context inputs, not calibrated
    modifiers. An intermediate age requires a separately established model.
    These are ultimate coefficients, not a finite-time creep history.
    """
    if (
        not math.isfinite(relative_humidity_percent)
        or not 0 < relative_humidity_percent <= 100
        or not math.isfinite(notional_size_mm)
        or notional_size_mm <= 0
    ):
        raise ValueError("Require valid humidity and positive notional size.")
    values = {7: 2.2, 28: 1.6, 365: 1.1}
    if age_at_loading_days not in values:
        raise ValueError(
            "Source default creep coefficients exist only at loading ages 7, 28 and 365 days; no interpolation model is selected."
        )
    return values[age_at_loading_days]


@clause("C-3")
def calculate_shrinkage_curvature(
    *,
    eps_cs: float = 0.0003,
    d_mm: float,
    ast_mm2: float,
    asc_mm2: float = 0.0,
    b_mm: float,
    es_nmm2: float = 200000.0,
    fck_nmm2: float = 25.0,
    D_mm: float | None = None,
) -> float:
    """Annex C-3.1: phi_sh=k4*eps_cs/D, with percentages pt/pc=100*A/(b*d).

    The listed empirical k4 branches (.72 or .65, capped at 1) apply when
    pt-pc >= .25 percent. Overall D is required; d is not a substitute.
    Es/fck remain compatibility inputs but do not enter the source k4 formula.
    The source does not specify the lower imbalance domain; no extrapolation
    or absolute-value workaround is applied there.
    """
    if D_mm is None:
        raise ValueError("Annex C-3.1 requires overall depth D_mm.")
    if (
        not all(math.isfinite(v) and v > 0 for v in (b_mm, d_mm, D_mm, ast_mm2))
        or d_mm >= D_mm
        or not math.isfinite(asc_mm2)
        or asc_mm2 < 0
        or not math.isfinite(eps_cs)
        or eps_cs < 0
    ):
        raise ValueError("Invalid shrinkage geometry, steel area or strain.")
    pt = 100 * ast_mm2 / (b_mm * d_mm)
    pc = 100 * asc_mm2 / (b_mm * d_mm)
    imbalance = pt - pc
    if imbalance < 0.25:
        raise ValueError(
            "Annex C-3.1 k4 domain requires pt-pc >= .25 percent; lower imbalance is unsupported."
        )
    k4 = min(1.0, (0.72 if imbalance < 1.0 else 0.65) * imbalance / math.sqrt(pt))
    return k4 * eps_cs / D_mm


@clause("C-4")
def calculate_creep_deflection(
    *,
    delta_sustained_mm: float,
    creep_coefficient: float,
    delta_long_term_mm: float | None = None,
) -> float:
    """Additional creep is the permanent-load long-term minus initial deflection.

    C-4.1 requires Ec/(1+theta), including the changed transformed section.
    A scalar theta and initial deflection do not determine cracked stiffness.
    The caller must supply the recomputed long-term permanent-load deflection.
    """
    if delta_long_term_mm is None:
        raise ValueError(
            "C-4.1 requires permanent-load deflection recomputed with effective Ec."
        )
    if (
        not all(
            math.isfinite(v) and v >= 0
            for v in (delta_sustained_mm, creep_coefficient, delta_long_term_mm)
        )
        or delta_long_term_mm < delta_sustained_mm
    ):
        raise ValueError("Require nonnegative deflections and long-term >= initial.")
    return delta_long_term_mm - delta_sustained_mm


@clause("C-3")
def calculate_shrinkage_deflection(
    *,
    phi_sh: float,
    span_mm: float,
    support_condition: SupportCondition | str = SupportCondition.SIMPLY_SUPPORTED,
) -> float:
    """Uniform shrinkage curvature: SS k3=1/8, cantilever k3=1/2.

    Continuous-one-end and fully continuous k3 are distinct source cases;
    the generic CONTINUOUS enum cannot select one, so it is unsupported here.
    """
    if (
        not math.isfinite(phi_sh)
        or phi_sh < 0
        or not math.isfinite(span_mm)
        or span_mm <= 0
    ):
        raise ValueError("Require nonnegative finite curvature and positive span.")
    support = _sls_support(support_condition)
    return (
        (0.5 if support == SupportCondition.CANTILEVER else 0.125) * phi_sh * span_mm**2
    )


@clause("C-2", "C-3", "C-4", "6.2.5.1")
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
    """Annex C default ultimate deflection for a singly reinforced rectangle.

    Unfactored permanent and variable service moments must have the same
    direction. SS means UDL; cantilever means end point load. Immediate
    stiffness uses the total moment. Creep uses independent initial and
    Ec/(1+theta) permanent-load paths, recalculating neutral axis and inertia.
    Shrinkage uses C-3.1's k4 and overall D. All reported components are
    magnitudes; shrinkage is added in the adverse direction.

    Missing compression-bar depth, continuous support moments, opposing load
    history, non-source loading ages or nonlinear concrete creep stress return
    HOLD_UNSUPPORTED. Default ultimate creep/shrinkage are estimates without
    experimental data, not a finite-time or construction-history analysis.
    """
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
        "es_nmm2": es_nmm2,
        "support_condition": str(support_condition),
    }
    support = SupportCondition.SIMPLY_SUPPORTED
    try:
        _sls_geometry(
            b_mm,
            D_mm,
            d_mm,
            span_mm,
            ast_mm2,
            asc_mm2,
            fck_nmm2,
            es_nmm2,
            deflection_limit_ratio,
        )
        support = _sls_support(support_condition)
        if not all(math.isfinite(v) for v in (ma_sustained_knm, ma_live_knm)):
            raise ValueError("Service moments must be finite.")
        if ma_sustained_knm * ma_live_knm < 0:
            raise ValueError(
                "Opposing permanent/live moments need a cracking and load-history model."
            )
        mcr = calculate_cracking_moment(b_mm=b_mm, D_mm=D_mm, fck_nmm2=fck_nmm2)
        ec = 5000 * math.sqrt(fck_nmm2)
        immediate = _sls_section(
            b_mm, D_mm, d_mm, ast_mm2, ec, es_nmm2, mcr, ma_sustained_knm + ma_live_knm
        )
        permanent = _sls_section(
            b_mm, D_mm, d_mm, ast_mm2, ec, es_nmm2, mcr, ma_sustained_knm
        )
        stress = (
            abs(ma_sustained_knm)
            * 1e6
            * (
                D_mm / 2 / permanent["igross_mm4"]
                if abs(ma_sustained_knm) <= mcr
                else permanent["x_mm"] / permanent["icr_mm4"]
            )
        )
        if stress > fck_nmm2 / 3:
            raise ValueError(
                "Permanent-load concrete stress exceeds fck/3; default proportional creep is unsupported (Cl6.2.5)."
            )
        theta = (
            get_creep_coefficient(
                age_at_loading_days=age_at_loading_days,
                relative_humidity_percent=relative_humidity_percent,
            )
            if ma_sustained_knm
            else 0.0
        )
        long_term = _sls_section(
            b_mm, D_mm, d_mm, ast_mm2, ec / (1 + theta), es_nmm2, mcr, ma_sustained_knm
        )
        delta_initial = _elastic_deflection(
            ma_sustained_knm + ma_live_knm, span_mm, ec, immediate["ieff_mm4"], support
        )
        delta_permanent = _elastic_deflection(
            ma_sustained_knm, span_mm, ec, permanent["ieff_mm4"], support
        )
        delta_permanent_long = _elastic_deflection(
            ma_sustained_knm,
            span_mm,
            long_term["ec_nmm2"],
            long_term["ieff_mm4"],
            support,
        )
        creep = calculate_creep_deflection(
            delta_sustained_mm=delta_permanent,
            creep_coefficient=theta,
            delta_long_term_mm=delta_permanent_long,
        )
        phi = calculate_shrinkage_curvature(
            eps_cs=shrinkage_strain,
            d_mm=d_mm,
            D_mm=D_mm,
            ast_mm2=ast_mm2,
            asc_mm2=asc_mm2,
            b_mm=b_mm,
            es_nmm2=es_nmm2,
            fck_nmm2=fck_nmm2,
        )
        shrink = calculate_shrinkage_deflection(
            phi_sh=phi, span_mm=span_mm, support_condition=support
        )
    except ValueError as exc:
        return _sls_hold(DeflectionLevelCResult, inputs, str(exc), support)  # type: ignore[return-value]
    total = delta_initial + creep + shrink
    limit = span_mm / deflection_limit_ratio
    is_ok = total <= limit
    computed = {
        "method": SLS_METHOD,
        "status": "PASS" if is_ok else "FAIL",
        "load_basis": "UNFACTORED_SERVICE",
        "load_pattern": (
            "CANTILEVER_END_POINT"
            if support == SupportCondition.CANTILEVER
            else "SIMPLY_SUPPORTED_UDL"
        ),
        "mcr_knm": mcr,
        **immediate,
        "permanent_initial_section": permanent,
        "permanent_long_term_section": long_term,
        "permanent_concrete_stress_nmm2": stress,
        "delta_permanent_initial_mm": delta_permanent,
        "delta_permanent_long_term_mm": delta_permanent_long,
        "delta_immediate_mm": delta_initial,
        "delta_creep_mm": creep,
        "delta_shrinkage_mm": shrink,
        "delta_total_mm": total,
        "delta_limit_mm": limit,
        "creep_coefficient": theta,
        "shrinkage_curvature": phi,
        "clause_refs": [
            "6.2.3.1",
            "6.2.4.1",
            "6.2.5/6.2.5.1",
            "C-2.1",
            "C-3.1",
            "C-4.1",
        ],
    }
    return DeflectionLevelCResult(
        is_ok=is_ok,
        remarks=f"{'OK' if is_ok else 'NOT OK'}: ultimate estimated δ_total={total:.3f} mm; limit={limit:.3f} mm.",
        support_condition=support,
        assumptions=[
            "Singly reinforced rectangular section; service moments are supplied unfactored.",
            "Concrete Ec=5000*sqrt(fck); elastic steel and transformed cracked section, without ULS factors.",
            "Source default ultimate creep and supplied shrinkage strain; no finite-time humidity/size calibration.",
            "Common declared load pattern and direction; shrinkage magnitude acts adversely.",
            "Continuous/other load patterns and construction history require a separate analysis basis.",
        ],
        inputs=inputs,
        computed=computed,
        mcr_knm=mcr,
        igross_mm4=immediate["igross_mm4"],
        icr_mm4=immediate["icr_mm4"],
        ieff_mm4=immediate["ieff_mm4"],
        delta_immediate_mm=delta_initial,
        delta_creep_mm=creep,
        delta_shrinkage_mm=shrink,
        delta_total_mm=total,
        delta_limit_mm=limit,
        creep_coefficient=theta,
        shrinkage_curvature=phi,
    )
