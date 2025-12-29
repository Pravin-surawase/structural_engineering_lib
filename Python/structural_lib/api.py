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

__all__ = [
    "get_library_version",
    "check_beam_ductility",
    "check_deflection_span_depth",
    "check_crack_width",
    "check_compliance_report",
    "design_beam_is456",
    "check_beam_is456",
    "detail_beam_is456",
]


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
    """Return the installed package version.

    Returns:
        Package version string. Falls back to a default when package metadata
        is unavailable (e.g., running from a source checkout).
    """
    try:
        return version("structural-lib-is456")
    except PackageNotFoundError:
        return "0.10.7"


def check_beam_ductility(
    b: float, D: float, d: float, fck: float, fy: float, min_long_bar_dia: float
) -> ductile.DuctileBeamResult:
    """
    Run IS 13920 beam ductility checks for a single section.

    Args:
        b: Beam width (mm).
        D: Overall depth (mm).
        d: Effective depth (mm).
        fck: Concrete strength (N/mm²).
        fy: Steel yield strength (N/mm²).
        min_long_bar_dia: Minimum longitudinal bar diameter (mm).

    Returns:
        DuctileBeamResult with pass/fail flags and limiting values.
    """
    return ductile.check_beam_ductility(b, D, d, fck, fy, min_long_bar_dia)


def check_deflection_span_depth(
    span_mm: float,
    d_mm: float,
    support_condition: str = "simply_supported",
    base_allowable_ld: Optional[float] = None,
    mf_tension_steel: Optional[float] = None,
    mf_compression_steel: Optional[float] = None,
    mf_flanged: Optional[float] = None,
) -> serviceability.DeflectionResult:
    """Check deflection using span/depth ratio (Level A).

    Args:
        span_mm: Clear span (mm).
        d_mm: Effective depth (mm).
        support_condition: Support condition string or enum.
        base_allowable_ld: Base L/d limit (optional).
        mf_tension_steel: Tension steel modification factor (optional).
        mf_compression_steel: Compression steel modification factor (optional).
        mf_flanged: Flanged beam modification factor (optional).

    Returns:
        DeflectionResult with computed L/d and allowable ratio.
    """

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
    exposure_class: str = "moderate",
    limit_mm: Optional[float] = None,
    acr_mm: Optional[float] = None,
    cmin_mm: Optional[float] = None,
    h_mm: Optional[float] = None,
    x_mm: Optional[float] = None,
    epsilon_m: Optional[float] = None,
    fs_service_nmm2: Optional[float] = None,
    es_nmm2: float = 200000.0,
) -> serviceability.CrackWidthResult:
    """Check crack width using an Annex-F-style estimate.

    Args:
        exposure_class: Exposure class string or enum.
        limit_mm: Crack width limit (mm), overrides defaults.
        acr_mm: Distance from point considered to nearest bar surface (mm).
        cmin_mm: Minimum cover to bar surface (mm).
        h_mm: Member depth (mm).
        x_mm: Neutral axis depth (mm).
        epsilon_m: Mean strain at reinforcement level.
        fs_service_nmm2: Steel stress at service (N/mm²).
        es_nmm2: Modulus of elasticity of steel (N/mm²).

    Returns:
        CrackWidthResult with computed width and pass/fail.
    """

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
    """Run a multi-case IS 456 compliance report.

    Args:
        cases: List of dicts with at least `case_id`, `mu_knm`, `vu_kn`.
        b_mm: Beam width (mm).
        D_mm: Overall depth (mm).
        d_mm: Effective depth (mm).
        fck_nmm2: Concrete strength (N/mm²).
        fy_nmm2: Steel yield strength (N/mm²).
        d_dash_mm: Compression steel depth from top (mm).
        asv_mm2: Area of stirrup legs (mm²).
        pt_percent: Percentage steel for shear table lookup (optional).
        deflection_defaults: Default deflection params (optional).
        crack_width_defaults: Default crack width params (optional).

    Returns:
        ComplianceReport with per-case results and governing case.
    """

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

    Args:
        units: Units label (must be one of the IS456 aliases).
        case_id: Case identifier for reporting.
        mu_knm: Factored bending moment (kN·m).
        vu_kn: Factored shear (kN).
        b_mm: Beam width (mm).
        D_mm: Overall depth (mm).
        d_mm: Effective depth (mm).
        fck_nmm2: Concrete strength (N/mm²).
        fy_nmm2: Steel yield strength (N/mm²).
        d_dash_mm: Compression steel depth from top (mm).
        asv_mm2: Area of stirrup legs (mm²).
        pt_percent: Percentage steel for shear table lookup (optional).
        ast_mm2_for_shear: Use this Ast for shear table lookup (optional).
        deflection_params: Per-case deflection params (optional).
        crack_width_params: Per-case crack width params (optional).

    Returns:
        ComplianceCaseResult with flexure, shear, and optional serviceability checks.

    Raises:
        ValueError: If units is not one of the accepted IS456 aliases.

    Units (IS456):
    - Mu: kN·m (factored)
    - Vu: kN (factored)
    - b_mm, D_mm, d_mm, d_dash_mm: mm
    - fck_nmm2, fy_nmm2: N/mm² (MPa)

    Example:
        result = design_beam_is456(
            units="IS456",
            case_id="DL+LL",
            mu_knm=150,
            vu_kn=100,
            b_mm=300,
            D_mm=500,
            d_mm=450,
            fck_nmm2=25,
            fy_nmm2=500,
        )
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

    Args:
        units: Units label (must be one of the IS456 aliases).
        cases: List of dicts with at least `case_id`, `mu_knm`, `vu_kn`.
        b_mm: Beam width (mm).
        D_mm: Overall depth (mm).
        d_mm: Effective depth (mm).
        fck_nmm2: Concrete strength (N/mm²).
        fy_nmm2: Steel yield strength (N/mm²).
        d_dash_mm: Compression steel depth from top (mm).
        asv_mm2: Area of stirrup legs (mm²).
        pt_percent: Percentage steel for shear table lookup (optional).
        deflection_defaults: Default deflection params (optional).
        crack_width_defaults: Default crack width params (optional).

    Returns:
        ComplianceReport with per-case results and governing case.

    Raises:
        ValueError: If units is not one of the accepted IS456 aliases.

    Example:
        cases = [
            {"case_id": "DL+LL", "mu_knm": 80, "vu_kn": 60},
            {"case_id": "1.5(DL+LL)", "mu_knm": 120, "vu_kn": 90},
        ]
        report = check_beam_is456(
            units="IS456",
            cases=cases,
            b_mm=300,
            D_mm=500,
            d_mm=450,
            fck_nmm2=25,
            fy_nmm2=500,
        )
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
    """Create IS456/SP34 detailing outputs from design Ast/Asc and stirrups.

    Args:
        units: Units label (must be one of the IS456 aliases).
        beam_id: Beam identifier.
        story: Story/level name.
        b_mm: Beam width (mm).
        D_mm: Overall depth (mm).
        span_mm: Beam span (mm).
        cover_mm: Clear cover (mm).
        fck_nmm2: Concrete strength (N/mm²).
        fy_nmm2: Steel yield strength (N/mm²).
        ast_start_mm2: Tension steel at start (mm²).
        ast_mid_mm2: Tension steel at midspan (mm²).
        ast_end_mm2: Tension steel at end (mm²).
        asc_start_mm2: Compression steel at start (mm²).
        asc_mid_mm2: Compression steel at midspan (mm²).
        asc_end_mm2: Compression steel at end (mm²).
        stirrup_dia_mm: Stirrup diameter (mm).
        stirrup_spacing_start_mm: Stirrup spacing at start (mm).
        stirrup_spacing_mid_mm: Stirrup spacing at midspan (mm).
        stirrup_spacing_end_mm: Stirrup spacing at end (mm).
        is_seismic: Apply IS 13920 detailing rules if True.

    Returns:
        BeamDetailingResult with bars, stirrups, and development lengths.
    """

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
