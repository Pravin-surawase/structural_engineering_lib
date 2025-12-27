"""Module: compliance

Compliance checker (TASK-042): Orchestrates strength + serviceability checks.

MVP contract:
- Accepts already-factored actions per case (Mu in kN·m, Vu in kN).
- Produces per-case results + a deterministic governing case.

Design constraints:
- Deterministic outputs.
- Units explicit at the API boundary.
- No silent defaults: when a value is assumed, it is recorded in result remarks/assumptions.
"""

from __future__ import annotations

import logging
from dataclasses import asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence

_logger = logging.getLogger(__name__)

from . import flexure, shear, serviceability
from .types import (
    ComplianceCaseResult,
    ComplianceReport,
    CrackWidthResult,
    DeflectionResult,
    ExposureClass,
    DesignSectionType,
    FlexureResult,
    ShearResult,
    SupportCondition,
)


def _utilization_safe(numer: float, denom: float) -> float:
    """Compute utilization ratio with safe division.

    Returns inf if denominator ≤ 0 and numerator > 0, else 0 for zero/zero.
    """
    if denom <= 0:
        return float("inf") if numer > 0 else 0.0
    return numer / denom


def _compute_flexure_utilization(mu_knm: float, flex: FlexureResult) -> float:
    """Compute a stable, interpretable flexure utilization ratio.

    For singly reinforced results, we use $|Mu|/Mu_{lim}$. For doubly reinforced
    cases, FlexureResult does not currently expose a computed capacity, so we
    use a conservative/acceptance-friendly convention:
    - if the design is safe and Mu is nonzero, return 1.0
    - if unsafe, fall back to $|Mu|/Mu_{lim}$ (typically > 1)
    """

    mu_abs = abs(mu_knm)
    if mu_abs == 0:
        return 0.0

    if flex.section_type == DesignSectionType.OVER_REINFORCED:
        # Doubly reinforced design path (or flagged as such): capacity isn't exposed.
        if flex.is_safe:
            return 1.0

    if flex.mu_lim <= 0:
        return float("inf")
    return mu_abs / flex.mu_lim


def _compute_shear_utilization(sh: ShearResult) -> float:
    """Compute shear utilization as tv / tc_max."""
    if (not sh.is_safe) and sh.tc_max <= 0:
        return float("inf")
    return _utilization_safe(sh.tv, sh.tc_max)


def _compute_deflection_utilization(defl: DeflectionResult) -> float:
    """Compute deflection utilization as (L/d) / allowable_ld."""
    if not defl.is_ok:
        allowable = float(defl.computed.get("allowable_ld", 0.0))
        if allowable <= 0:
            return float("inf")
    ld_ratio = float(defl.computed.get("ld_ratio", 0.0))
    allowable = float(defl.computed.get("allowable_ld", 0.0))
    return _utilization_safe(ld_ratio, allowable)


def _compute_crack_utilization(cr: CrackWidthResult) -> float:
    """Compute crack width utilization as wcr / limit."""
    if not cr.is_ok:
        limit_mm = float(cr.computed.get("limit_mm", 0.0))
        if limit_mm <= 0:
            return float("inf")
    wcr = float(cr.computed.get("wcr_mm", 0.0))
    limit_mm = float(cr.computed.get("limit_mm", 0.0))
    return _utilization_safe(wcr, limit_mm)


def _safe_deflection_check(params: Any) -> DeflectionResult:
    """Run deflection check with exception safety.

    Returns a failed DeflectionResult on invalid input or exception.
    """
    if not isinstance(params, dict):
        return DeflectionResult(
            is_ok=False,
            remarks="Invalid deflection_params: expected a dict.",
            support_condition=SupportCondition.SIMPLY_SUPPORTED,
            assumptions=["deflection_params was not a dict"],
            inputs={"deflection_params": params},
            computed={"ld_ratio": 1.0, "allowable_ld": 0.0},
        )

    try:
        return serviceability.check_deflection_span_depth(**params)
    except Exception as exc:
        _logger.exception("Deflection check failed for params=%s", params)
        return DeflectionResult(
            is_ok=False,
            remarks=f"Deflection check failed: {exc}",
            support_condition=SupportCondition.SIMPLY_SUPPORTED,
            assumptions=["deflection check raised an exception"],
            inputs={"deflection_params": params},
            computed={"ld_ratio": 1.0, "allowable_ld": 0.0},
        )


def _safe_crack_width_check(params: Any) -> CrackWidthResult:
    """Run crack width check with exception safety.

    Returns a failed CrackWidthResult on invalid input or exception.
    """
    if not isinstance(params, dict):
        return CrackWidthResult(
            is_ok=False,
            remarks="Invalid crack_width_params: expected a dict.",
            exposure_class=ExposureClass.MODERATE,
            assumptions=["crack_width_params was not a dict"],
            inputs={"crack_width_params": params},
            computed={"wcr_mm": 1.0, "limit_mm": 0.0},
        )

    try:
        return serviceability.check_crack_width(**params)
    except Exception as exc:
        _logger.exception("Crack width check failed for params=%s", params)
        return CrackWidthResult(
            is_ok=False,
            remarks=f"Crack width check failed: {exc}",
            exposure_class=ExposureClass.MODERATE,
            assumptions=["crack width check raised an exception"],
            inputs={"crack_width_params": params},
            computed={"wcr_mm": 1.0, "limit_mm": 0.0},
        )


def check_compliance_case(
    *,
    case_id: str,
    mu_knm: float,
    vu_kn: float,
    b_mm: float,
    D_mm: float,
    d_mm: float,
    fck_nmm2: float,
    fy_nmm2: float,
    d_dash_mm: float = 50.0,
    # Shear reinforcement input
    asv_mm2: float = 100.0,
    pt_percent: Optional[float] = None,
    ast_mm2_for_shear: Optional[float] = None,
    # Optional serviceability checks
    deflection_params: Optional[Dict[str, Any]] = None,
    crack_width_params: Optional[Dict[str, Any]] = None,
) -> ComplianceCaseResult:
    """Run a single compliance case.

    Units:
    - Mu: kN·m (factored)
    - Vu: kN (factored)
    - b_mm, D_mm, d_mm, d_dash_mm: mm
    - fck_nmm2, fy_nmm2: N/mm²
    - asv_mm2: mm² (area of stirrup legs)
    - pt_percent: %

    Notes:
    - If pt_percent is not provided, it is computed from ast_mm2_for_shear when available,
      else falls back to using flexure-required Ast (recorded as an assumption).
    """

    failed_checks: List[str] = []
    assumptions: List[str] = []

    flex = flexure.design_doubly_reinforced(
        b=b_mm,
        d=d_mm,
        d_dash=d_dash_mm,
        d_total=D_mm,
        mu_knm=mu_knm,
        fck=fck_nmm2,
        fy=fy_nmm2,
    )

    # Determine pt for shear table lookup.
    if pt_percent is None:
        if ast_mm2_for_shear is not None and ast_mm2_for_shear > 0:
            pt_percent = (ast_mm2_for_shear * 100.0) / (b_mm * d_mm)
            assumptions.append("Computed pt_percent for shear using ast_mm2_for_shear.")
        elif flex.ast_required > 0:
            pt_percent = (flex.ast_required * 100.0) / (b_mm * d_mm)
            assumptions.append(
                "Computed pt_percent for shear using flexure ast_required."
            )
        else:
            pt_percent = 0.0
            assumptions.append(
                "pt_percent not provided; using 0.0 (tables clamp internally)."
            )

    sh = shear.design_shear(
        vu_kn=vu_kn,
        b=b_mm,
        d=d_mm,
        fck=fck_nmm2,
        fy=fy_nmm2,
        asv=asv_mm2,
        pt=pt_percent,
    )

    defl: Optional[DeflectionResult] = None
    crack: Optional[CrackWidthResult] = None

    if deflection_params is not None:
        defl = _safe_deflection_check(deflection_params)

    if crack_width_params is not None:
        crack = _safe_crack_width_check(crack_width_params)

    # Determine pass/fail.
    if not flex.is_safe:
        failed_checks.append("flexure")
    if not sh.is_safe:
        failed_checks.append("shear")
    if defl is not None and not defl.is_ok:
        failed_checks.append("deflection")
    if crack is not None and not crack.is_ok:
        failed_checks.append("crack_width")

    utilizations: Dict[str, float] = {
        "flexure": _compute_flexure_utilization(mu_knm, flex),
        "shear": _compute_shear_utilization(sh),
    }
    if defl is not None:
        utilizations["deflection"] = _compute_deflection_utilization(defl)
    if crack is not None:
        utilizations["crack_width"] = _compute_crack_utilization(crack)

    governing_util = max(utilizations.values()) if utilizations else 0.0
    is_ok = len(failed_checks) == 0

    remarks = "OK" if is_ok else ("FAIL: " + ", ".join(failed_checks))
    if assumptions:
        remarks = remarks + " | " + " | ".join(assumptions)

    return ComplianceCaseResult(
        case_id=case_id,
        mu_knm=mu_knm,
        vu_kn=vu_kn,
        flexure=flex,
        shear=sh,
        deflection=defl,
        crack_width=crack,
        is_ok=is_ok,
        governing_utilization=governing_util,
        utilizations=utilizations,
        failed_checks=failed_checks,
        remarks=remarks,
    )


def check_compliance_report(
    *,
    cases: Sequence[Dict[str, Any]],
    b_mm: float,
    D_mm: float,
    d_mm: float,
    fck_nmm2: float,
    fy_nmm2: float,
    d_dash_mm: float = 50.0,
    asv_mm2: float = 100.0,
    pt_percent: Optional[float] = None,
    # Optional global serviceability defaults (can be overridden per case)
    deflection_defaults: Optional[Dict[str, Any]] = None,
    crack_width_defaults: Optional[Dict[str, Any]] = None,
) -> ComplianceReport:
    """Run multiple cases and pick a deterministic governing case.

    Governing-case rule:
    - For each case compute per-check utilization ratios (demand/limit).
    - Case governing utilization is max(utilizations).
    - Report governing case as the case with the highest governing utilization.
      Ties are broken by case order.

    Each case dict must include:
    - case_id: str
    - mu_knm: float
    - vu_kn: float

    Optional per-case overrides:
    - deflection_params: dict
    - crack_width_params: dict
    - ast_mm2_for_shear: float
    """

    results: List[ComplianceCaseResult] = []

    if deflection_defaults is not None and not isinstance(deflection_defaults, dict):
        raise ValueError("deflection_defaults must be a dict when provided.")
    if crack_width_defaults is not None and not isinstance(crack_width_defaults, dict):
        raise ValueError("crack_width_defaults must be a dict when provided.")

    for i, c in enumerate(cases):
        if not isinstance(c, dict):
            raise ValueError("Each case must be a dict.")

        case_id = str(c.get("case_id", "") or f"CASE_{i + 1}")

        mu_raw = c.get("mu_knm")
        vu_raw = c.get("vu_kn")
        if mu_raw is None or vu_raw is None:
            raise ValueError(
                "Each case must include 'mu_knm' and 'vu_kn' (already-factored actions)."
            )

        mu_knm = float(mu_raw)
        vu_kn = float(vu_raw)

        defl_params = c.get("deflection_params", deflection_defaults)
        crack_params = c.get("crack_width_params", crack_width_defaults)
        ast_for_shear = c.get("ast_mm2_for_shear")

        results.append(
            check_compliance_case(
                case_id=case_id,
                mu_knm=mu_knm,
                vu_kn=vu_kn,
                b_mm=b_mm,
                D_mm=D_mm,
                d_mm=d_mm,
                fck_nmm2=fck_nmm2,
                fy_nmm2=fy_nmm2,
                d_dash_mm=d_dash_mm,
                asv_mm2=asv_mm2,
                pt_percent=pt_percent,
                ast_mm2_for_shear=(
                    float(ast_for_shear) if ast_for_shear is not None else None
                ),
                deflection_params=defl_params,
                crack_width_params=crack_params,
            )
        )

    def _governing_key(
        index_and_result: tuple[int, ComplianceCaseResult],
    ) -> tuple[float, float, float, float, int]:
        """Sort key for finding governing case by max utilization."""
        idx, r = index_and_result
        utils = list(r.utilizations.values())
        # Sort descending so secondary checks break ties deterministically.
        # Pad to a fixed length (max expected checks in MVP is 4).
        sorted_utils = sorted(utils, reverse=True)
        while len(sorted_utils) < 4:
            sorted_utils.append(float("-inf"))
        # Final deterministic tie-break: earlier case order wins.
        return (
            sorted_utils[0],
            sorted_utils[1],
            sorted_utils[2],
            sorted_utils[3],
            -idx,
        )

    governing = max(enumerate(results), key=_governing_key)[1] if results else None
    governing_case_id = governing.case_id if governing else ""
    governing_util = governing.governing_utilization if governing else 0.0

    is_ok = all(r.is_ok for r in results)

    # Compact summary row (Excel/JSON friendly).
    max_utils_by_check: Dict[str, float] = {}
    for r in results:
        for k, v in r.utilizations.items():
            if k not in max_utils_by_check:
                max_utils_by_check[k] = v
            else:
                max_utils_by_check[k] = max(max_utils_by_check[k], v)

    worst_check = ""
    worst_util = 0.0
    if governing and governing.utilizations:
        # Deterministic: sort by utilization desc, then key asc.
        worst_check, worst_util = sorted(
            governing.utilizations.items(), key=lambda kv: (-kv[1], kv[0])
        )[0]

    summary: Dict[str, Any] = {
        "is_ok": is_ok,
        "num_cases": len(results),
        "num_failed_cases": sum(1 for r in results if not r.is_ok),
        "governing_case_id": governing_case_id,
        "governing_utilization": governing_util,
        "governing_worst_check": worst_check,
        "governing_worst_utilization": worst_util,
        # Fixed columns (None if not evaluated anywhere).
        "max_util_flexure": max_utils_by_check.get("flexure"),
        "max_util_shear": max_utils_by_check.get("shear"),
        "max_util_deflection": max_utils_by_check.get("deflection"),
        "max_util_crack_width": max_utils_by_check.get("crack_width"),
    }

    return ComplianceReport(
        is_ok=is_ok,
        governing_case_id=governing_case_id,
        governing_utilization=governing_util,
        cases=results,
        summary=summary,
    )


def report_to_dict(report: ComplianceReport) -> Dict[str, Any]:
    """Serialize report to a JSON/Excel-friendly dict."""

    def _jsonable(obj: Any) -> Any:
        """Recursively convert enums and nested structures to JSON-safe types."""
        if isinstance(obj, Enum):
            return obj.name
        if isinstance(obj, dict):
            return {k: _jsonable(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_jsonable(v) for v in obj]
        if isinstance(obj, tuple):
            return [_jsonable(v) for v in obj]
        return obj

    return _jsonable(asdict(report))
