"""
Beam Design Router.

Endpoints for beam flexure and shear design calculations.
"""

import logging
import math

from fastapi import APIRouter, HTTPException, status

from fastapi_app.models.beam import (
    BeamDesignRequest,
    BeamDesignResponse,
    BeamCheckRequest,
    BeamCheckResponse,
    EnhancedShearRequest,
    EnhancedShearResponse,
    FlexureResult,
    ShearResult,
    TorsionDesignRequest,
    TorsionDesignResponse,
)
from fastapi_app.models.compliance import (
    DuctilityCheckRequest,
    DuctilityCheckResponse,
    SlendernessCheckRequest,
    SlendernessCheckResponse,
    DeflectionCheckRequest,
    DeflectionCheckResponse,
    CrackWidthCheckRequest,
    CrackWidthCheckResponse,
    ComplianceReportRequest,
    ComplianceReportResponse,
    ComplianceCaseOutput,
)

logger = logging.getLogger(__name__)


def _sanitize_float(v: float) -> float:
    """Replace non-finite floats for JSON safety (RFC 8259)."""
    if math.isfinite(v):
        return v
    if math.isnan(v):
        return 0.0
    return 9999.0 if v > 0 else -9999.0


router = APIRouter(
    prefix="/design",
    tags=["design"],
)


# =============================================================================
# Design Endpoints
# =============================================================================


@router.post(
    "/beam",
    response_model=BeamDesignResponse,
    summary="Design Beam Section",
    description="Calculate required reinforcement for a beam section under given loading.",
)
async def design_beam(request: BeamDesignRequest) -> BeamDesignResponse:
    """
    Design a beam section for flexure and shear.

    Calculates:
    - Required tension reinforcement (Ast)
    - Required compression reinforcement (Asc) if doubly reinforced
    - Required shear reinforcement (stirrups)
    - Neutral axis depth and capacity checks

    Per IS 456:2000 clauses 38.1 (flexure) and 40 (shear).
    """
    try:
        from structural_lib.services.api import design_beam_is456

        # Calculate effective depth if not provided
        effective_depth = request.effective_depth
        if effective_depth is None:
            stirrup = request.stirrup_dia_mm
            bar = request.main_bar_dia_mm
            effective_depth = request.depth - request.clear_cover - stirrup - bar / 2

        # Call the design function with actual API parameter names
        result = design_beam_is456(
            units="IS456",
            b_mm=request.width,
            D_mm=request.depth,
            d_mm=effective_depth,
            mu_knm=request.moment,
            vu_kn=request.shear if request.shear > 0 else 0.0,
            fck_nmm2=request.fck,
            fy_nmm2=request.fy,
            d_dash_mm=request.clear_cover
            + request.stirrup_dia_mm
            + request.main_bar_dia_mm / 2,
        )

        # Extract flexure results directly from ComplianceCaseResult
        flexure_result = result.flexure

        # Build flexure result
        flexure = FlexureResult(
            ast_required=flexure_result.Ast_required,
            ast_min=flexure_result.Ast_min,
            ast_max=flexure_result.Ast_max,
            xu=flexure_result.xu,
            xu_max=flexure_result.xu_max,
            is_under_reinforced=flexure_result.xu <= flexure_result.xu_max,
            moment_capacity=flexure_result.Mu_lim,
            asc_required=flexure_result.Asc_required,
        )

        # Build shear result if shear was provided
        shear_result = None
        if request.shear > 0 and result.shear:
            shear = result.shear
            shear_result = ShearResult(
                tau_v=shear.tau_v,
                tau_c=shear.tau_c,
                tau_c_max=shear.tau_c_max,
                asv_required=(
                    shear.Vus / (0.87 * request.fy) * 1000 if shear.Vus > 0 else 0.0
                ),
                stirrup_spacing=shear.spacing,
                sv_max=300.0,
                shear_capacity=(
                    shear.tau_c * request.width * effective_depth / 1000 + shear.Vus
                    if shear.Vus > 0
                    else request.shear
                ),
            )

        # Calculate utilization
        moment_capacity = flexure_result.Mu_lim
        utilization = request.moment / moment_capacity if moment_capacity > 0 else 1.0

        # Collect warnings
        warnings = []
        if utilization > 1.0:
            warnings.append(
                "Section is overstressed - increase section or use compression steel"
            )
        if flexure_result.xu > flexure_result.xu_max:
            warnings.append("Section is over-reinforced - consider increasing depth")

        return BeamDesignResponse(
            success=True,
            message=f"Design complete: Ast = {flexure.ast_required:.0f} mm²",
            flexure=flexure,
            shear=shear_result,
            ast_total=flexure.ast_required,
            asc_total=flexure.asc_required,
            utilization_ratio=min(utilization, 2.0),
            effective_depth_used=effective_depth,
            warnings=warnings,
        )

    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"structural_lib not available: {e}",
        )
    except (ValueError, AttributeError, TypeError):
        logger.exception("Invalid input for beam design")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid input parameters",
        )
    except Exception:
        logger.exception("Design calculation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal calculation error",
        )


@router.post(
    "/beam/check",
    response_model=BeamCheckResponse,
    summary="Check Beam Adequacy",
    description="Check if a beam with given reinforcement is adequate for the applied loads.",
)
async def check_beam(request: BeamCheckRequest) -> BeamCheckResponse:
    """
    Check adequacy of a beam section with provided reinforcement.

    Verifies:
    - Moment capacity vs applied moment
    - Shear capacity vs applied shear
    - Code compliance checks

    Returns utilization ratios and pass/fail status.
    """
    try:
        from structural_lib.services.api import check_beam_is456

        # Calculate effective depth
        effective_depth = request.depth - request.clear_cover - 25  # ~bar_dia/2

        # Build cases list for check_beam_is456
        # API expects: label, mu_knm, vu_kn, ast_provided
        cases = [
            {
                "label": "CHECK-1",
                "mu_knm": request.moment,
                "vu_kn": request.shear,
                "ast_provided": request.ast_provided,
            }
        ]

        result = check_beam_is456(
            units="IS456",
            cases=cases,
            b_mm=request.width,
            D_mm=request.depth,
            d_mm=effective_depth,
            fck_nmm2=request.fck,
            fy_nmm2=request.fy,
            d_dash_mm=request.clear_cover + 25,
            asv_mm2=request.stirrup_area,
            pt_percent=request.ast_provided / (request.width * effective_depth) * 100,
        )

        # Extract first case result from ComplianceReport.cases
        case_result = result.cases[0] if result.cases else None
        if not case_result:
            raise ValueError("No results returned from check")

        # Get flexure and shear from case result
        flexure = case_result.flexure
        shear = case_result.shear

        moment_capacity = flexure.Mu_lim
        shear_capacity = (
            shear.tau_c * request.width * effective_depth / 1000
            if shear
            else request.shear * 1.5
        )

        moment_util = request.moment / moment_capacity if moment_capacity > 0 else 1.0
        shear_util = request.shear / shear_capacity if shear_capacity > 0 else 0.0

        flexure_ok = moment_util <= 1.0
        shear_ok = shear_util <= 1.0

        warnings = []
        if moment_util > 0.9:
            warnings.append("Flexure utilization >90% - limited reserve capacity")
        if shear_util > 0.9:
            warnings.append("Shear utilization >90% - limited reserve capacity")

        return BeamCheckResponse(
            is_adequate=flexure_ok and shear_ok,
            success=True,
            message=(
                "Beam is adequate"
                if (flexure_ok and shear_ok)
                else "Beam is NOT adequate"
            ),
            moment_capacity=moment_capacity,
            shear_capacity=shear_capacity,
            moment_utilization=min(moment_util, 2.0),
            shear_utilization=min(shear_util, 2.0),
            flexure_adequate=flexure_ok,
            shear_adequate=shear_ok,
            warnings=warnings,
        )

    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"structural_lib not available: {e}",
        )
    except (ValueError, AttributeError, TypeError):
        logger.exception("Invalid input for beam check")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid input parameters",
        )
    except Exception:
        logger.exception("Check calculation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal calculation error",
        )


@router.get(
    "/limits",
    summary="Get Design Limits",
    description="Get IS 456 design limits and constraints.",
)
async def get_design_limits() -> dict:
    """
    Get IS 456 design limits and typical values.

    Returns limits for:
    - Material strengths (fck, fy)
    - Reinforcement ratios (min, max)
    - Clear cover requirements
    - Shear stress limits
    """
    return {
        "concrete": {
            "fck_min": 15.0,
            "fck_max": 80.0,
            "typical_grades": [20, 25, 30, 40, 50],
            "unit": "N/mm²",
        },
        "steel": {
            "fy_min": 250.0,
            "fy_max": 600.0,
            "typical_grades": [415, 500, 550],
            "unit": "N/mm²",
        },
        "reinforcement": {
            "pt_min": 0.12,
            "pt_max": 4.0,
            "unit": "% of bd",
            "note": "Minimum is 0.12% for Fe 500, 0.085As/bd else",
        },
        "clear_cover": {
            "mild": 20,
            "moderate": 30,
            "severe": 45,
            "very_severe": 50,
            "extreme": 75,
            "unit": "mm",
        },
        "tau_c_max": {
            "M20": 2.8,
            "M25": 3.1,
            "M30": 3.5,
            "M35": 3.7,
            "M40": 4.0,
            "unit": "N/mm²",
        },
    }


# =============================================================================
# Torsion Design Endpoint
# =============================================================================


@router.post(
    "/beam/torsion",
    response_model=TorsionDesignResponse,
    summary="Design Beam for Torsion",
    description="Design a beam for combined torsion, shear, and bending per IS 456 Cl 41.",
)
async def design_beam_torsion(
    request: TorsionDesignRequest,
) -> TorsionDesignResponse:
    """
    Design beam for combined torsion + shear + bending.

    Calculates per IS 456:2000 Clause 41:
    - Equivalent shear Ve and equivalent moment Me
    - Required closed stirrups for torsion + shear
    - Longitudinal steel for torsion
    - Safety check (τve vs τc,max)
    """
    try:
        from structural_lib.services.api import design_torsion

        # Calculate effective depth if not provided
        d = request.effective_depth
        if d is None:
            d = request.depth - request.clear_cover - 25

        result = design_torsion(
            tu_knm=request.torsion,
            vu_kn=request.shear,
            mu_knm=request.moment,
            b=request.width,
            D=request.depth,
            d=d,
            fck=request.fck,
            fy=request.fy,
            cover=request.clear_cover,
            stirrup_dia=request.stirrup_dia,
            pt=request.pt,
        )

        warnings: list[str] = []
        if not result.is_safe:
            warnings.append(
                f"Section unsafe: τve ({result.tau_ve:.2f}) > τc,max ({result.tau_c_max:.2f}). "
                "Increase section size."
            )
        if result.requires_closed_stirrups:
            warnings.append("Closed stirrups mandatory for torsion (IS 456 Cl 41.4.3)")
        for err in result.errors:
            warnings.append(str(err))

        return TorsionDesignResponse(
            success=result.is_safe,
            message=(
                f"Torsion design {'safe' if result.is_safe else 'UNSAFE'}: "
                f"Sv = {result.stirrup_spacing:.0f} mm, Al = {result.Al_torsion:.0f} mm²"
            ),
            tu_knm=result.Tu_knm,
            vu_kn=result.Vu_kn,
            mu_knm=result.Mu_knm,
            ve_kn=round(result.Ve_kn, 2),
            me_knm=round(result.Me_knm, 2),
            tv_equiv=result.tau_ve,
            tc=result.tau_c,
            tc_max=result.tau_c_max,
            asv_torsion=result.Asv_torsion,
            asv_shear=result.Asv_shear,
            asv_total=result.Asv_total,
            stirrup_spacing=result.stirrup_spacing,
            al_torsion=result.Al_torsion,
            is_safe=result.is_safe,
            requires_closed_stirrups=result.requires_closed_stirrups,
            warnings=warnings,
        )

    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"structural_lib not available: {e}",
        )
    except (ValueError, AttributeError, TypeError):
        logger.exception("Invalid input for torsion design")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid input parameters",
        )
    except Exception:
        logger.exception("Torsion design calculation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal calculation error",
        )


# =============================================================================
# Enhanced Shear Strength Endpoint (IS 456 Cl 40.3)
# =============================================================================


@router.post(
    "/beam/enhanced-shear",
    response_model=EnhancedShearResponse,
    summary="Enhanced Shear Strength Near Supports",
    description=(
        "Calculate enhanced design shear strength τc' for sections close to supports "
        "per IS 456:2000 Cl 40.3. Applies when a concentrated load acts within 2d "
        "of the face of support."
    ),
)
async def enhanced_shear(
    request: EnhancedShearRequest,
) -> EnhancedShearResponse:
    """
    Enhanced shear strength for sections near supports.

    When a concentrated load acts within 2d of a support face,
    IS 456 Cl 40.3 allows enhancing τc to τc' = (2d/av) × τc,
    capped at τc,max (Table 20).

    NOTE: Enhancement applies ONLY to concentrated loads, NOT distributed loads.
    """
    try:
        from structural_lib.codes.is456.beam import tables
        from structural_lib.services.api import enhanced_shear_strength_is456

        # Call the API function
        tau_c_enhanced = enhanced_shear_strength_is456(
            fck_nmm2=request.fck,
            pt_percent=request.pt_percent,
            d_mm=request.d_mm,
            av_mm=request.av_mm,
        )

        # Get base values for the response
        tau_c_base = tables.get_tc_value(request.fck, request.pt_percent)
        tau_c_max = tables.get_tc_max_value(request.fck)

        # Compute enhancement factor
        if request.av_mm >= 2.0 * request.d_mm:
            enhancement_factor = 1.0
        else:
            enhancement_factor = (2.0 * request.d_mm) / request.av_mm

        is_capped = (enhancement_factor * tau_c_base) > tau_c_max

        return EnhancedShearResponse(
            tau_c_enhanced=round(tau_c_enhanced, 4),
            tau_c_base=round(tau_c_base, 4),
            enhancement_factor=round(enhancement_factor, 4),
            tau_c_max=round(tau_c_max, 4),
            is_capped=is_capped,
            clause="IS 456 Cl 40.3",
        )

    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"structural_lib not available: {e}",
        )
    except (ValueError, AttributeError, TypeError):
        logger.exception("Invalid input for enhanced shear")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid input parameters",
        )
    except Exception:
        logger.exception("Enhanced shear calculation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal calculation error",
        )


# =============================================================================
# Ductility Check Endpoint (IS 13920)
# =============================================================================


@router.post(
    "/beam/ductility-check",
    response_model=DuctilityCheckResponse,
    summary="Beam Ductility Check (IS 13920)",
    description=(
        "Run IS 13920 beam ductility checks for a single section. "
        "Checks geometry (Cl 6.1), min/max steel (Cl 6.2), "
        "and confinement spacing (Cl 6.3.5)."
    ),
)
async def check_ductility(
    request: DuctilityCheckRequest,
) -> DuctilityCheckResponse:
    """Check beam ductility per IS 13920 for seismic design."""
    try:
        from structural_lib.services.api import check_beam_ductility

        result = check_beam_ductility(
            b=request.b,
            D=request.D,
            d=request.d,
            fck=request.fck,
            fy=request.fy,
            min_long_bar_dia=request.min_long_bar_dia,
        )

        return DuctilityCheckResponse(
            is_geometry_valid=result.is_geometry_valid,
            min_pt=result.min_pt,
            max_pt=result.max_pt,
            confinement_spacing=result.confinement_spacing,
            remarks=result.remarks,
            errors=[
                (
                    {"code": str(e.code), "message": e.message}
                    if hasattr(e, "code")
                    else {"message": str(e)}
                )
                for e in result.errors
            ],
        )

    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"structural_lib not available: {e}",
        )
    except (ValueError, TypeError):
        logger.exception("Invalid input for ductility check")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid input parameters",
        )
    except Exception:
        logger.exception("Ductility check failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal calculation error",
        )


# =============================================================================
# Slenderness Check Endpoint (IS 456 Cl 23.3)
# =============================================================================


@router.post(
    "/beam/slenderness-check",
    response_model=SlendernessCheckResponse,
    summary="Beam Slenderness Check (IS 456 Cl 23.3)",
    description=(
        "Check beam slenderness for lateral stability per IS 456:2000 Cl 23.3. "
        "Verifies slenderness ratio l_eff/b against code limits."
    ),
)
async def check_slenderness(
    request: SlendernessCheckRequest,
) -> SlendernessCheckResponse:
    """Check beam slenderness / lateral stability per IS 456 Cl 23.3."""
    try:
        from structural_lib.services.api import check_beam_slenderness

        result = check_beam_slenderness(
            b_mm=request.b_mm,
            d_mm=request.d_mm,
            l_eff_mm=request.l_eff_mm,
            beam_type=request.beam_type,
            has_lateral_restraint=request.has_lateral_restraint,
        )

        return SlendernessCheckResponse(
            is_ok=result.is_ok,
            is_slender=result.is_slender,
            slenderness_ratio=result.slenderness_ratio,
            slenderness_limit=result.slenderness_limit,
            utilization=result.utilization,
            depth_to_width_ratio=result.depth_to_width_ratio,
            remarks=result.remarks,
            errors=result.errors,
            warnings=result.warnings,
        )

    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"structural_lib not available: {e}",
        )
    except (ValueError, TypeError):
        logger.exception("Invalid input for slenderness check")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid input parameters",
        )
    except Exception:
        logger.exception("Slenderness check failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal calculation error",
        )


# =============================================================================
# Deflection Span/Depth Check Endpoint (IS 456 Cl 23.2)
# =============================================================================


@router.post(
    "/beam/deflection-check",
    response_model=DeflectionCheckResponse,
    summary="Deflection Span/Depth Check (IS 456 Cl 23.2)",
    description=(
        "Check deflection using span/depth ratio (Level A) per IS 456:2000 Cl 23.2. "
        "Compares actual L/d against allowable ratios with modification factors."
    ),
)
async def check_deflection(
    request: DeflectionCheckRequest,
) -> DeflectionCheckResponse:
    """Check deflection via span/depth ratio per IS 456 Cl 23.2."""
    try:
        from structural_lib.services.api import check_deflection_span_depth

        result = check_deflection_span_depth(
            span_mm=request.span_mm,
            d_mm=request.d_mm,
            support_condition=request.support_condition,
            base_allowable_ld=request.base_allowable_ld,
            mf_tension_steel=request.mf_tension_steel,
            mf_compression_steel=request.mf_compression_steel,
            mf_flanged=request.mf_flanged,
        )

        return DeflectionCheckResponse(
            is_ok=result.is_ok,
            remarks=result.remarks,
            support_condition=(
                result.support_condition.value
                if hasattr(result.support_condition, "value")
                else str(result.support_condition)
            ),
            assumptions=result.assumptions,
            inputs=result.inputs,
            computed=result.computed,
        )

    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"structural_lib not available: {e}",
        )
    except (ValueError, TypeError):
        logger.exception("Invalid input for deflection check")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid input parameters",
        )
    except Exception:
        logger.exception("Deflection check failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal calculation error",
        )


# =============================================================================
# Crack Width Check Endpoint (IS 456 Annex F)
# =============================================================================


@router.post(
    "/beam/crack-width-check",
    response_model=CrackWidthCheckResponse,
    summary="Crack Width Check (IS 456 Annex F)",
    description=(
        "Check crack width using an Annex-F-style estimate per IS 456:2000. "
        "Computes estimated crack width and compares against exposure-class limits."
    ),
)
async def check_crack_width_endpoint(
    request: CrackWidthCheckRequest,
) -> CrackWidthCheckResponse:
    """Check crack width per IS 456 Annex F."""
    try:
        from structural_lib.services.api import check_crack_width

        result = check_crack_width(
            exposure_class=request.exposure_class,
            limit_mm=request.limit_mm,
            acr_mm=request.acr_mm,
            cmin_mm=request.cmin_mm,
            h_mm=request.h_mm,
            x_mm=request.x_mm,
            epsilon_m=request.epsilon_m,
            fs_service_nmm2=request.fs_service_nmm2,
            es_nmm2=request.es_nmm2,
        )

        return CrackWidthCheckResponse(
            is_ok=result.is_ok,
            remarks=result.remarks,
            exposure_class=(
                result.exposure_class.value
                if hasattr(result.exposure_class, "value")
                else str(result.exposure_class)
            ),
            assumptions=result.assumptions,
            inputs=result.inputs,
            computed=result.computed,
        )

    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"structural_lib not available: {e}",
        )
    except (ValueError, TypeError):
        logger.exception("Invalid input for crack width check")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid input parameters",
        )
    except Exception:
        logger.exception("Crack width check failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal calculation error",
        )


# =============================================================================
# Compliance Report Endpoint (Multi-case IS 456)
# =============================================================================


@router.post(
    "/beam/compliance",
    response_model=ComplianceReportResponse,
    summary="Multi-case Compliance Report",
    description=(
        "Run a multi-case IS 456 compliance report. "
        "Checks flexure, shear, deflection, and crack width for each load case "
        "and identifies the governing case."
    ),
)
async def compliance_report(
    request: ComplianceReportRequest,
) -> ComplianceReportResponse:
    """Run multi-case IS 456 compliance report."""
    try:
        from structural_lib.services.api import check_compliance_report

        # Convert Pydantic case models to dicts
        cases = [c.model_dump() for c in request.cases]

        # Convert optional param models to TypedDicts
        deflection_defaults = None
        if request.deflection_defaults:
            deflection_defaults = {
                k: v
                for k, v in request.deflection_defaults.model_dump().items()
                if v is not None
            }

        crack_width_defaults = None
        if request.crack_width_defaults:
            crack_width_defaults = {
                k: v
                for k, v in request.crack_width_defaults.model_dump().items()
                if v is not None
            }

        result = check_compliance_report(
            cases=cases,
            b_mm=request.b_mm,
            D_mm=request.D_mm,
            d_mm=request.d_mm,
            fck_nmm2=request.fck_nmm2,
            fy_nmm2=request.fy_nmm2,
            d_dash_mm=request.d_dash_mm,
            asv_mm2=request.asv_mm2,
            pt_percent=request.pt_percent,
            deflection_defaults=deflection_defaults,
            crack_width_defaults=crack_width_defaults,
        )

        return ComplianceReportResponse(
            is_ok=result.is_ok,
            governing_case_id=result.governing_case_id,
            governing_utilization=_sanitize_float(result.governing_utilization),
            cases=[
                ComplianceCaseOutput(
                    case_id=c.case_id,
                    mu_knm=c.Mu_knm,
                    vu_kn=c.Vu_kn,
                    is_ok=c.is_ok,
                    governing_utilization=_sanitize_float(c.governing_utilization),
                    utilizations={
                        k: _sanitize_float(v) for k, v in c.utilizations.items()
                    },
                    failed_checks=c.failed_checks,
                    remarks=c.remarks,
                )
                for c in result.cases
            ],
            summary=result.summary,
        )

    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"structural_lib not available: {e}",
        )
    except (ValueError, TypeError):
        logger.exception("Invalid input for compliance report")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid input parameters",
        )
    except Exception:
        logger.exception("Compliance report failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal calculation error",
        )
