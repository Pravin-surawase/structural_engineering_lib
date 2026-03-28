"""
Beam Design Router.

Endpoints for beam flexure and shear design calculations.
"""

from fastapi import APIRouter, HTTPException, status

from fastapi_app.models.beam import (
    BeamDesignRequest,
    BeamDesignResponse,
    BeamCheckRequest,
    BeamCheckResponse,
    FlexureResult,
    ShearResult,
    TorsionDesignRequest,
    TorsionDesignResponse,
    ColumnSlendernessRequest,
    ColumnSlendernessResponse,
)

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
            # Assume 50mm from face to center of tension steel
            effective_depth = request.depth - request.clear_cover - 25  # ~bar_dia/2

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
            d_dash_mm=request.clear_cover + 25,  # Compression steel depth
        )

        # Extract flexure results directly from ComplianceCaseResult
        flexure_result = result.flexure

        # Calculate min/max steel per IS 456
        ast_min = 0.85 * request.width * effective_depth / request.fy
        ast_max = 0.04 * request.width * request.depth

        # Build flexure result
        flexure = FlexureResult(
            ast_required=flexure_result.ast_required,
            ast_min=ast_min,
            ast_max=ast_max,
            xu=flexure_result.xu,
            xu_max=flexure_result.xu_max,
            is_under_reinforced=flexure_result.xu <= flexure_result.xu_max,
            moment_capacity=flexure_result.mu_lim,
            asc_required=flexure_result.asc_required,
        )

        # Build shear result if shear was provided
        shear_result = None
        if request.shear > 0 and result.shear:
            shear = result.shear
            shear_result = ShearResult(
                tau_v=shear.tv,
                tau_c=shear.tc,
                tau_c_max=shear.tc_max,
                asv_required=(
                    shear.vus / (0.87 * request.fy) * 1000 if shear.vus > 0 else 0.0
                ),
                stirrup_spacing=shear.spacing,
                sv_max=300.0,
                shear_capacity=(
                    shear.tc * request.width * effective_depth / 1000 + shear.vus
                    if shear.vus > 0
                    else request.shear
                ),
            )

        # Calculate utilization
        moment_capacity = flexure_result.mu_lim
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
            warnings=warnings,
        )

    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"structural_lib not available: {e}",
        )
    except (ValueError, AttributeError, TypeError) as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Design calculation failed: {e}",
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

        moment_capacity = flexure.mu_lim
        shear_capacity = (
            shear.tc * request.width * effective_depth / 1000
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
    except (ValueError, AttributeError, TypeError) as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Check calculation failed: {e}",
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
                f"Section unsafe: τve ({result.tv_equiv:.2f}) > τc,max ({result.tc_max:.2f}). "
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
                f"Sv = {result.stirrup_spacing:.0f} mm, Al = {result.al_torsion:.0f} mm²"
            ),
            tu_knm=result.tu_knm,
            vu_kn=result.vu_kn,
            mu_knm=result.mu_knm,
            ve_kn=round(result.ve_kn, 2),
            me_knm=round(result.me_knm, 2),
            tv_equiv=result.tv_equiv,
            tc=result.tc,
            tc_max=result.tc_max,
            asv_torsion=result.asv_torsion,
            asv_shear=result.asv_shear,
            asv_total=result.asv_total,
            stirrup_spacing=result.stirrup_spacing,
            al_torsion=result.al_torsion,
            is_safe=result.is_safe,
            requires_closed_stirrups=result.requires_closed_stirrups,
            warnings=warnings,
        )

    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"structural_lib not available: {e}",
        )
    except (ValueError, AttributeError, TypeError) as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Torsion design calculation failed: {e}",
        )


# =============================================================================
# Column Slenderness Endpoint
# =============================================================================


@router.post(
    "/column/slenderness",
    response_model=ColumnSlendernessResponse,
    summary="Check Column Slenderness",
    description="Classify a column as short or long per IS 456:2000 Cl 25.1.2.",
)
async def check_column_slenderness(
    request: ColumnSlendernessRequest,
) -> ColumnSlendernessResponse:
    """
    Classify column as short or long per IS 456 Cl 25.1.2.

    A column is SHORT if both le/b ≤ 12 AND le/D ≤ 12.
    Otherwise it is LONG (slender) and additional moment per Cl 39.7.1 applies.

    Optionally provide end conditions (top, bottom) to auto-calculate
    the effective length factor from IS 456 Table 28.
    """
    try:
        from structural_lib.services.api import (
            check_column_slenderness as api_check_column,
            get_effective_length_factor,
        )

        # Determine effective length factor
        eff_factor = request.effective_length_factor
        if request.end_condition_top and request.end_condition_bottom:
            eff_factor = get_effective_length_factor(
                end_condition_top=request.end_condition_top,
                end_condition_bottom=request.end_condition_bottom,
            )

        result = api_check_column(
            b_mm=request.width,
            D_mm=request.depth,
            unsupported_length_mm=request.unsupported_length,
            effective_length_factor=eff_factor,
        )

        return ColumnSlendernessResponse(
            success=result.is_ok or not result.errors,
            message=result.remarks,
            column_type=result.column_type.value,
            is_short=result.is_ok,
            is_slender=result.is_slender,
            slenderness_ratio=result.slenderness_ratio,
            slenderness_limit=result.slenderness_limit,
            utilization=result.utilization,
            le_by_b=result.le_by_b,
            le_by_D=result.le_by_D,
            effective_length_mm=result.computed.get("le_mm", 0.0),
            effective_length_factor=eff_factor,
            depth_to_width_ratio=result.depth_to_width_ratio,
            remarks=result.remarks,
            warnings=result.warnings,
        )

    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"structural_lib not available: {e}",
        )
    except (ValueError, AttributeError, TypeError) as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Column slenderness check failed: {e}",
        )
