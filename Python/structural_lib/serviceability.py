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

from .types import CrackWidthResult, DeflectionResult, ExposureClass, SupportCondition


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
    # Convenience: useful for Excel/JSON exports.
    return asdict(result)
