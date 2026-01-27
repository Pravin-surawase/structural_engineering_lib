"""
Insights Router — Design analytics and code checks.

Endpoints:
- POST /insights/dashboard — Generate dashboard from design result
- POST /insights/code-checks — Live IS 456 code checks
- POST /insights/rebar-suggest — Suggest optimal rebar configurations
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from fastapi_app.models.insights import (
    BeamParams,
    CodeChecksRequest,
    CodeChecksResponse,
    DashboardRequest,
    DashboardResponse,
    RebarSuggestRequest,
    RebarSuggestResponse,
    RebarSuggestion,
    SingleCodeCheck,
    UtilizationData,
    SteelData,
    CapacityData,
    AppliedData,
    CodeChecksData,
)

router = APIRouter(
    prefix="/insights",
    tags=["insights"],
)


# =============================================================================
# Dashboard Endpoint
# =============================================================================


@router.post(
    "/dashboard",
    response_model=DashboardResponse,
    summary="Generate Dashboard",
    description="Generate aggregated dashboard data from a design result.",
)
async def generate_dashboard(request: DashboardRequest) -> DashboardResponse:
    """
    Generate dashboard data from design result.

    Returns aggregated metrics including:
    - Utilization ratios (moment, shear, overall)
    - Steel quantities (required, provided, ratio)
    - Capacity vs applied loads
    - Code checks summary
    """
    try:
        from structural_lib.insights import generate_dashboard as gen_dashboard

        beam_params = request.beam_params.model_dump() if request.beam_params else None
        dashboard = gen_dashboard(request.design_result, beam_params)
        data = dashboard.to_dict()

        return DashboardResponse(
            beamId=data["beamId"],
            status=data["status"],
            utilization=UtilizationData(**data["utilization"]),
            steel=SteelData(**data["steel"]),
            capacity=CapacityData(**data["capacity"]),
            applied=AppliedData(**data["applied"]),
            codeChecks=CodeChecksData(**data["codeChecks"]),
            messages=data.get("messages", []),
        )

    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"structural_lib.insights not available: {e}",
        )
    except (ValueError, KeyError, TypeError) as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid design result: {e}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dashboard generation failed: {e}",
        )


# =============================================================================
# Code Checks Endpoint
# =============================================================================


@router.post(
    "/code-checks",
    response_model=CodeChecksResponse,
    summary="Live Code Checks",
    description="Perform real-time IS 456 code compliance checks.",
)
async def code_checks(request: CodeChecksRequest) -> CodeChecksResponse:
    """
    Perform live IS 456 code checks.

    Checks include:
    - Minimum bar count (Cl 26.5.1.1)
    - Clear bar spacing (Cl 26.3.2)
    - Steel ratio limits (Cl 26.5.1.1)
    - Effective depth ratio (Cl 23.2.1)
    - Bar diameter limits (Cl 26.3.3)
    - Cover adequacy (Cl 26.4.1)
    """
    try:
        from structural_lib.insights import code_checks_live

        result = code_checks_live(
            request.beam.model_dump(),
            request.config.model_dump(),
        )
        data = result.to_dict()

        checks = [SingleCodeCheck(**c) for c in data["checks"]]

        return CodeChecksResponse(
            overallPass=data["overallPass"],
            checks=checks,
            errors=data.get("errors", []),
            warnings=data.get("warnings", []),
            passCount=data["passCount"],
            failCount=data["failCount"],
        )

    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"structural_lib.insights not available: {e}",
        )
    except (ValueError, KeyError, TypeError) as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid request: {e}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Code checks failed: {e}",
        )


# =============================================================================
# Rebar Suggestions Endpoint
# =============================================================================


@router.post(
    "/rebar-suggest",
    response_model=RebarSuggestResponse,
    summary="Suggest Rebar Options",
    description="Suggest optimal rebar configurations for given requirements.",
)
async def rebar_suggest(request: RebarSuggestRequest) -> RebarSuggestResponse:
    """
    Suggest optimal rebar configurations.

    Returns configurations ranked by:
    1. Spacing compliance (valid configurations first)
    2. Cost index (lower is better)
    3. Steel utilization (higher is better)

    Each suggestion includes bar count, diameter, layers, and cost index.
    """
    try:
        from structural_lib.insights import suggest_rebar_options

        suggestions = suggest_rebar_options(
            request.beam.model_dump(),
            {
                "ast_required_mm2": request.ast_required_mm2,
                "min_bars": request.min_bars,
                "max_layers": request.max_layers,
            },
            max_options=request.max_options,
        )

        result_suggestions = [
            RebarSuggestion(
                barCount=s.bar_count,
                barDia=s.bar_dia_mm,
                layers=s.layers,
                astProvided=round(s.ast_provided_mm2, 1),
                utilization=round(s.utilization, 3),
                costIndex=round(s.cost_index, 3),
                spacingOk=s.spacing_ok,
                message=s.message,
            )
            for s in suggestions
        ]

        best = suggestions[0] if suggestions else None
        msg = (
            f"Found {len(suggestions)} options. "
            f"Best: {best.bar_count}-{best.bar_dia_mm}φ ({best.ast_provided_mm2:.0f}mm²)"
            if best
            else "No valid configurations found"
        )

        return RebarSuggestResponse(
            success=len(suggestions) > 0,
            suggestions=result_suggestions,
            target_ast_mm2=request.ast_required_mm2,
            message=msg,
        )

    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"structural_lib.insights not available: {e}",
        )
    except (ValueError, KeyError, TypeError) as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid request: {e}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Rebar suggestion failed: {e}",
        )
