"""
Insights Router.

Endpoints for dashboard insights and live code checks.
"""

from fastapi import APIRouter, HTTPException, status

from fastapi_app.models.insights import (
    CodeChecksRequest,
    CodeChecksResponse,
    DashboardRequest,
    DashboardResponse,
)

router = APIRouter(
    prefix="/insights",
    tags=["insights"],
)


@router.post(
    "/dashboard",
    response_model=DashboardResponse,
    summary="Generate dashboard insights",
    description="Generate smart dashboard insights from beam inputs.",
)
async def generate_dashboard(
    request: DashboardRequest,
) -> DashboardResponse:
    try:
        from structural_lib.insights import generate_dashboard as dashboard_fn
        from structural_lib.beam_pipeline import design_single_beam

        d_mm = request.depth - request.cover
        if d_mm <= 0:
            raise ValueError("Effective depth must be positive")

        # Run full pipeline for BeamDesignOutput
        design = design_single_beam(
            units="IS456",
            b_mm=request.width,
            D_mm=request.depth,
            d_mm=d_mm,
            cover_mm=request.cover,
            fck_nmm2=request.fck,
            fy_nmm2=request.fy,
            mu_knm=request.moment,
            vu_kn=request.shear,
            beam_id="dashboard",
            story="N/A",
            span_mm=request.span,
            d_dash_mm=50.0,
            asv_mm2=100.0,
        )

        dashboard = dashboard_fn(
            design=design,
            span_mm=request.span,
            mu_knm=request.moment,
            vu_kn=request.shear,
            include_cost=request.include_cost,
            include_suggestions=request.include_suggestions,
            include_sensitivity=request.include_sensitivity,
            include_constructability=request.include_constructability,
        )

        return DashboardResponse(
            success=True,
            message="Dashboard generated",
            dashboard=dashboard.to_dict(),
            warnings=[],
        )
    except (ValueError, AttributeError, TypeError) as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dashboard generation failed: {e}",
        )


@router.post(
    "/code-checks",
    response_model=CodeChecksResponse,
    summary="Run live code checks",
    description="Run fast, advisory code checks for live UI feedback.",
)
async def run_code_checks(
    request: CodeChecksRequest,
) -> CodeChecksResponse:
    try:
        from structural_lib.insights import code_checks_live

        d_mm = request.depth - request.cover
        if d_mm <= 0:
            raise ValueError("Effective depth must be positive")

        checks = code_checks_live(
            span_mm=request.span,
            b_mm=request.width,
            D_mm=request.depth,
            d_mm=d_mm,
            mu_knm=request.moment,
            fck_nmm2=request.fck,
            fy_nmm2=request.fy,
        )

        return CodeChecksResponse(
            success=True,
            message="Code checks completed",
            checks=checks,
            warnings=[],
        )
    except (ValueError, AttributeError, TypeError) as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Code checks failed: {e}",
        )
