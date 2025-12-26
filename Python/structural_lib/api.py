"""
Module:       api
Description:  Public facing API functions
"""

from importlib.metadata import PackageNotFoundError, version

from typing import Any, Dict, Optional, Sequence

from . import compliance
from . import detailing
from . import ductile
from . import serviceability
from .types import ComplianceCaseResult, ComplianceReport


_IS456_UNITS_ALIASES = {
    "IS456",
    "IS 456",
    "is456",
    "mm-kN-kNm-Nmm2",
    "mm,kN,kN-m,N/mm2",
}


def _require_is456_units(units: str) -> None:
    if not isinstance(units, str) or units.strip() == "":
        raise ValueError(
            "units must be a non-empty string (e.g., 'IS456' or 'mm-kN-kNm-Nmm2')."
        )

    if units.strip() not in _IS456_UNITS_ALIASES:
        raise ValueError(
            "Invalid units for IS456 entrypoint. Expected one of: "
            + ", ".join(sorted(_IS456_UNITS_ALIASES))
        )


def get_library_version() -> str:
    """Return the current library version."""
    try:
        return version("structural-lib-is456")
    except PackageNotFoundError:
        return "0.9.4"


def check_beam_ductility(
    b: float, D: float, d: float, fck: float, fy: float, min_long_bar_dia: float
):
    """
    Wrapper for ductile.check_beam_ductility
    """
    return ductile.check_beam_ductility(b, D, d, fck, fy, min_long_bar_dia)


def check_deflection_span_depth(
    span_mm: float,
    d_mm: float,
    support_condition="simply_supported",
    base_allowable_ld=None,
    mf_tension_steel=None,
    mf_compression_steel=None,
    mf_flanged=None,
):
    """Wrapper for serviceability.check_deflection_span_depth."""

    return serviceability.check_deflection_span_depth(
        span_mm=span_mm,
        d_mm=d_mm,
        support_condition=support_condition,
        base_allowable_ld=base_allowable_ld,
        mf_tension_steel=mf_tension_steel,
        mf_compression_steel=mf_compression_steel,
        mf_flanged=mf_flanged,
    )


def check_crack_width(
    exposure_class="moderate",
    limit_mm=None,
    acr_mm=None,
    cmin_mm=None,
    h_mm=None,
    x_mm=None,
    epsilon_m=None,
    fs_service_nmm2=None,
    es_nmm2=200000.0,
):
    """Wrapper for serviceability.check_crack_width."""

    return serviceability.check_crack_width(
        exposure_class=exposure_class,
        limit_mm=limit_mm,
        acr_mm=acr_mm,
        cmin_mm=cmin_mm,
        h_mm=h_mm,
        x_mm=x_mm,
        epsilon_m=epsilon_m,
        fs_service_nmm2=fs_service_nmm2,
        es_nmm2=es_nmm2,
    )


def check_compliance_report(
    cases,
    b_mm,
    D_mm,
    d_mm,
    fck_nmm2,
    fy_nmm2,
    d_dash_mm=50.0,
    asv_mm2=100.0,
    pt_percent=None,
    deflection_defaults=None,
    crack_width_defaults=None,
):
    """Wrapper for compliance.check_compliance_report."""

    return compliance.check_compliance_report(
        cases=cases,
        b_mm=b_mm,
        D_mm=D_mm,
        d_mm=d_mm,
        fck_nmm2=fck_nmm2,
        fy_nmm2=fy_nmm2,
        d_dash_mm=d_dash_mm,
        asv_mm2=asv_mm2,
        pt_percent=pt_percent,
        deflection_defaults=deflection_defaults,
        crack_width_defaults=crack_width_defaults,
    )


def design_beam_is456(
    *,
    units: str,
    case_id: str = "CASE-1",
    mu_knm: float,
    vu_kn: float,
    b_mm: float,
    D_mm: float,
    d_mm: float,
    fck_nmm2: float,
    fy_nmm2: float,
    d_dash_mm: float = 50.0,
    asv_mm2: float = 100.0,
    pt_percent: Optional[float] = None,
    ast_mm2_for_shear: Optional[float] = None,
    deflection_params: Optional[Dict[str, Any]] = None,
    crack_width_params: Optional[Dict[str, Any]] = None,
) -> ComplianceCaseResult:
    """Design/check a single IS 456 beam case (strength + optional serviceability).

    This is a *public entrypoint* intended to stay stable even if internals evolve.

    Units (IS456):
    - Mu: kN·m (factored)
    - Vu: kN (factored)
    - b_mm, D_mm, d_mm, d_dash_mm: mm
    - fck_nmm2, fy_nmm2: N/mm² (MPa)
    """

    _require_is456_units(units)

    return compliance.check_compliance_case(
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
        ast_mm2_for_shear=ast_mm2_for_shear,
        deflection_params=deflection_params,
        crack_width_params=crack_width_params,
    )


def check_beam_is456(
    *,
    units: str,
    cases: Sequence[Dict[str, Any]],
    b_mm: float,
    D_mm: float,
    d_mm: float,
    fck_nmm2: float,
    fy_nmm2: float,
    d_dash_mm: float = 50.0,
    asv_mm2: float = 100.0,
    pt_percent: Optional[float] = None,
    deflection_defaults: Optional[Dict[str, Any]] = None,
    crack_width_defaults: Optional[Dict[str, Any]] = None,
) -> ComplianceReport:
    """Run an IS 456 compliance report across multiple cases.

    This is the stable multi-case entrypoint for IS456.
    """

    _require_is456_units(units)

    return compliance.check_compliance_report(
        cases=cases,
        b_mm=b_mm,
        D_mm=D_mm,
        d_mm=d_mm,
        fck_nmm2=fck_nmm2,
        fy_nmm2=fy_nmm2,
        d_dash_mm=d_dash_mm,
        asv_mm2=asv_mm2,
        pt_percent=pt_percent,
        deflection_defaults=deflection_defaults,
        crack_width_defaults=crack_width_defaults,
    )


def detail_beam_is456(
    *,
    units: str,
    beam_id: str,
    story: str,
    b_mm: float,
    D_mm: float,
    span_mm: float,
    cover_mm: float,
    fck_nmm2: float,
    fy_nmm2: float,
    ast_start_mm2: float,
    ast_mid_mm2: float,
    ast_end_mm2: float,
    asc_start_mm2: float = 0.0,
    asc_mid_mm2: float = 0.0,
    asc_end_mm2: float = 0.0,
    stirrup_dia_mm: float = 8.0,
    stirrup_spacing_start_mm: float = 150.0,
    stirrup_spacing_mid_mm: float = 200.0,
    stirrup_spacing_end_mm: float = 150.0,
    is_seismic: bool = False,
):
    """Create IS456/SP34 detailing outputs from design Ast/Asc and stirrup spacing."""

    _require_is456_units(units)

    return detailing.create_beam_detailing(
        beam_id=beam_id,
        story=story,
        b=b_mm,
        D=D_mm,
        span=span_mm,
        cover=cover_mm,
        fck=fck_nmm2,
        fy=fy_nmm2,
        ast_start=ast_start_mm2,
        ast_mid=ast_mid_mm2,
        ast_end=ast_end_mm2,
        asc_start=asc_start_mm2,
        asc_mid=asc_mid_mm2,
        asc_end=asc_end_mm2,
        stirrup_dia=stirrup_dia_mm,
        stirrup_spacing_start=stirrup_spacing_start_mm,
        stirrup_spacing_mid=stirrup_spacing_mid_mm,
        stirrup_spacing_end=stirrup_spacing_end_mm,
        is_seismic=is_seismic,
    )
