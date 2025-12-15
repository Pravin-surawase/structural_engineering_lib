"""
Module:       api
Description:  Public facing API functions
"""

from importlib.metadata import PackageNotFoundError, version

from . import compliance
from . import ductile
from . import serviceability


def get_library_version() -> str:
    """Return the current library version."""
    try:
        return version("structural-lib-is456")
    except PackageNotFoundError:
        return "0.7.1"


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
