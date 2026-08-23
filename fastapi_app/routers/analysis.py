"""
Smart Analysis Router.

Endpoints for AI-assisted design analysis and load calculations.
"""

import logging

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from fastapi_app.error_utils import sanitize_error
from fastapi_app.models.response import APIResponse, error_response, success_response
from fastapi_app.models.analysis import (
    LoadAnalysisRequest,
    LoadAnalysisResponse,
    CriticalPointResponse,
    SmartAnalysisRequest,
    SmartAnalysisResponse,
    Suggestion,
    CodeCheck,
    SmartScoreMetrics,
    SmartCostAnalysis,
)
from fastapi_app.models.metadata import CodeClausesResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/analysis",
    tags=["analysis"],
)


# =============================================================================
# Load Analysis Endpoint
# =============================================================================


@router.post(
    "/loads/simple",
    response_model=APIResponse[LoadAnalysisResponse],
    summary="Simple Load Analysis (BMD/SFD)",
    description="Compute BMD and SFD for a beam with UDL and/or point loads. "
    "Returns discretized diagrams + critical points (max moment, max shear).",
)
async def analyze_loads(request: LoadAnalysisRequest):
    """Compute bending moment and shear force diagrams.

    Supports simply supported and cantilever beams with UDL / point loads.
    Uses principle of superposition for multiple loads.
    """
    try:
        from structural_lib.services.api import (
            compute_bmd_sfd,
            LoadDefinition,
            LoadType,
        )
    except ImportError as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=error_response(sanitize_error(e, "load analysis")),
        )

    # Map request loads to library LoadDefinition objects
    load_defs = []
    for load in request.loads:
        lt = LoadType.UDL if load.load_type == "udl" else LoadType.POINT
        load_defs.append(
            LoadDefinition(
                load_type=lt,
                magnitude=load.magnitude,
                position_mm=load.position_mm,
                end_position_mm=load.end_position_mm,
            )
        )

    try:
        result = compute_bmd_sfd(
            span_mm=request.span_mm,
            support_condition=request.support_condition,
            loads=load_defs,
            num_points=request.num_points,
        )
    except ValueError:
        logger.exception("Invalid input for load analysis")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response("Invalid input parameters"),
        )
    except (RuntimeError, KeyError, ZeroDivisionError):
        logger.exception("Internal error in analyze_loads")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response("Internal calculation error"),
        )

    return success_response(
        LoadAnalysisResponse(
            span_mm=result.span_mm,
            support_condition=result.support_condition,
            positions_mm=result.positions_mm,
            bmd_knm=result.bmd_knm,
            sfd_kn=result.sfd_kn,
            max_bm_knm=result.max_bm_knm,
            min_bm_knm=result.min_bm_knm,
            max_sf_kn=result.max_sf_kn,
            min_sf_kn=result.min_sf_kn,
            critical_points=[
                CriticalPointResponse(
                    position_mm=cp.position_mm,
                    point_type=cp.point_type,
                    bm_knm=cp.bm_knm,
                    sf_kn=cp.sf_kn,
                )
                for cp in result.critical_points
            ],
        )
    )


# =============================================================================
# Analysis Endpoints
# =============================================================================


@router.post(
    "/beam/smart",
    response_model=APIResponse[SmartAnalysisResponse],
    summary="Smart Beam Analysis",
    description="Get AI-assisted analysis with suggestions for beam design.",
)
async def smart_analyze_beam(
    request: SmartAnalysisRequest,
):
    """
    Perform smart analysis on a beam design.

    Provides:
    - Code compliance checks (IS 456, IS 13920)
    - Design efficiency metrics
    - Improvement suggestions with priorities
    - Cost estimates

    Useful for:
    - Design review and validation
    - Optimization opportunity identification
    - Code compliance verification
    """
    try:
        from structural_lib.services.api import smart_analyze_design

        result = smart_analyze_design(
            units="IS456",
            span_mm=request.span_length,
            mu_knm=request.moment,
            vu_kn=request.shear,
            b_mm=request.width,
            D_mm=request.depth,
            d_mm=request.effective_depth,
            fck_nmm2=request.fck,
            fy_nmm2=request.fy,
            include_cost=True,
            include_suggestions=request.include_suggestions,
            include_sensitivity=False,
            include_constructability=True,
        )

        # Get summary data from result
        summary_data = result.summary_data

        # The core smart-analysis result owns check identity and arithmetic.
        # The transport only serializes those canonical checks.
        summary_checks = summary_data.get("checks", [])
        code_checks = []
        if request.include_code_checks:
            for check in summary_checks:
                passed = bool(check["passed"])
                code_checks.append(
                    CodeCheck(
                        clause=check["clause_ref"],
                        description=f"{check['check_id'].title()} capacity check",
                        passed=passed,
                        calculated_value=check["utilization"],
                        limit_value=1.0,
                        message=(
                            "Section is adequate" if passed else "Section overstressed"
                        ),
                    )
                )

        # Parse suggestions from result.suggestions dict
        suggestions = []
        if request.include_suggestions and result.suggestions:
            sug_data = result.suggestions
            for sug in sug_data.get("suggestions", []):
                suggestions.append(
                    Suggestion(
                        category=sug.get("category", "general"),
                        priority=sug.get("impact", "medium"),
                        title=sug.get("title", ""),
                        description=sug.get("description", ""),
                        potential_savings=sug.get("savings_percent"),
                        action_required=sug.get("impact") == "high",
                    )
                )

        # Translate the core-owned score names without reinterpreting them.
        scores = None
        if request.analyze_efficiency:
            scores = SmartScoreMetrics(
                cost_efficiency=summary_data["cost_efficiency"],
                constructability=summary_data["constructability"],
                robustness=summary_data["robustness"],
                overall_score=summary_data["overall_score"],
            )

        # Serialize only values produced by the core cost analysis.
        cost_analysis = None
        if result.cost:
            cost_data = result.cost
            cost_analysis = SmartCostAnalysis(
                current_cost=cost_data["current_cost"],
                optimal_cost=cost_data["optimal_cost"],
                savings_percent=cost_data["savings_percent"],
                baseline_alternative=cost_data.get("baseline_alternative"),
                optimal_alternative=cost_data.get("optimal_alternative"),
                alternatives=cost_data.get("alternatives", []),
            )

        all_passed = bool(summary_checks) and all(
            bool(check["passed"]) for check in summary_checks
        )
        critical_count = sum(1 for s in suggestions if s.priority == "high")

        # Build design summary
        design_summary = {
            "width_mm": request.width,
            "depth_mm": request.depth,
            "effective_depth_mm": request.effective_depth,
            "span_mm": request.span_length,
            "moment_knm": request.moment,
            "shear_kn": request.shear,
            "fck_nmm2": request.fck,
            "fy_nmm2": request.fy,
            "design_status": summary_data["design_status"],
            "governing_utilization": summary_data.get("governing_utilization"),
            "capacity_margin": summary_data.get("safety_score"),
            "governing_check": summary_data.get("governing_check"),
            "key_issues": summary_data.get("key_issues", []),
            "quick_wins": summary_data.get("quick_wins", []),
        }

        return success_response(
            SmartAnalysisResponse(
                success=True,
                message=f"{'All checks passed' if all_passed else 'Some checks failed'}. {len(suggestions)} suggestions.",
                design_summary=design_summary,
                code_checks=code_checks,
                all_checks_passed=all_passed,
                suggestions=suggestions,
                critical_suggestions=critical_count,
                scores=scores,
                cost_analysis=cost_analysis,
                warnings=list(result.metadata.get("warnings", [])),
            )
        )

    except ImportError as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=error_response(sanitize_error(e, "smart analysis")),
        )
    except (ValueError, TypeError):
        logger.exception("Invalid input for smart analysis")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response("Invalid input parameters"),
        )
    except (RuntimeError, KeyError, ZeroDivisionError):
        logger.exception("Internal error in smart_analyze_beam")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response("Internal calculation error"),
        )


@router.get(
    "/code-clauses",
    response_model=APIResponse[CodeClausesResponse],
    summary="Get Code Clause References",
    description="Get IS 456 clause references for common checks.",
)
async def get_code_clauses():
    """
    Get IS 456:2000 code clause references.

    Useful for understanding which code provisions apply to various checks.
    """
    return success_response(
        {
            "flexure": {
                "assumptions": "Cl. 38.1",
                "stress_block": "Cl. 38.1 & Annex G",
                "limiting_xu": "Cl. 38.1(c)",
                "minimum_steel": "Cl. 26.5.1.1",
                "maximum_steel": "Cl. 26.5.1.2",
            },
            "shear": {
                "nominal_stress": "Cl. 40.1",
                "design_stress": "Cl. 40.2 & Table 19",
                "maximum_stress": "Cl. 40.2.3 & Table 20",
                "stirrup_requirements": "Cl. 40.4",
                "spacing_limits": "Cl. 26.5.1.5",
            },
            "detailing": {
                "development_length": "Cl. 26.2.1",
                "bond_stress": "Cl. 26.2.1.1 & Table 26",
                "bar_spacing": "Cl. 26.3.2",
                "cover": "Cl. 26.4 & Table 16",
                "curtailment": "Cl. 26.2.3",
                "anchorage": "Cl. 26.2.2",
            },
            "serviceability": {
                "deflection": "Cl. 23.2",
                "span_depth_ratio": "Cl. 23.2.1 & Table 5",
                "crack_width": "Cl. 35.3.2 & Annex F",
            },
            "seismic": {
                "ductile_detailing": "IS 13920",
                "beam_requirements": "IS 13920 Cl. 6",
                "confinement": "IS 13920 Cl. 6.3",
            },
        }
    )
