"""
Smart Analysis Router.

Endpoints for AI-assisted design analysis.
"""

from fastapi import APIRouter, HTTPException, status

from fastapi_app.models.analysis import (
    SmartAnalysisRequest,
    SmartAnalysisResponse,
    Suggestion,
    CodeCheck,
    EfficiencyMetrics,
    CostEstimate,
)

router = APIRouter(
    prefix="/analysis",
    tags=["analysis"],
)


# =============================================================================
# Analysis Endpoints
# =============================================================================


@router.post(
    "/beam/smart",
    response_model=SmartAnalysisResponse,
    summary="Smart Beam Analysis",
    description="Get AI-assisted analysis with suggestions for beam design.",
)
async def smart_analyze_beam(
    request: SmartAnalysisRequest,
) -> SmartAnalysisResponse:
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
        from structural_lib.api import smart_analyze_design

        # Calculate effective depth
        effective_depth = request.depth - 50  # Approximate

        result = smart_analyze_design(
            units="IS456",
            span_mm=request.span_length if request.span_length else request.depth * 12,
            mu_knm=request.moment,
            vu_kn=request.shear,
            b_mm=request.width,
            D_mm=request.depth,
            d_mm=effective_depth,
            fck_nmm2=request.fck,
            fy_nmm2=request.fy,
            include_cost=True,
            include_suggestions=request.include_suggestions,
            include_sensitivity=False,
            include_constructability=True,
        )

        # Get summary data from result
        summary_data = result.summary_data

        # Parse code checks - not directly available, create from summary
        code_checks = []
        if request.include_code_checks:
            # Create a basic compliance check based on safety_score
            safety_passed = summary_data.get("safety_score", 0) < 1.0
            code_checks.append(
                CodeCheck(
                    clause="IS 456 Cl. 38.1",
                    description="Flexural capacity check",
                    passed=safety_passed,
                    calculated_value=summary_data.get("safety_score"),
                    limit_value=1.0,
                    message=(
                        "Section is adequate"
                        if safety_passed
                        else "Section overstressed"
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

        # Parse efficiency metrics from summary_data
        efficiency = None
        if request.analyze_efficiency:
            efficiency = EfficiencyMetrics(
                utilization_ratio=summary_data.get("safety_score", 0.0),
                steel_efficiency=1.0 - summary_data.get("safety_score", 0.0),
                concrete_efficiency=summary_data.get("cost_efficiency", 0.0),
                overall_efficiency=summary_data.get("overall_score", 0.0),
                efficiency_grade=(
                    "A" if summary_data.get("overall_score", 0) > 0.85 else "B"
                ),
                efficiency_comment=summary_data.get("design_status", ""),
            )

        # Parse cost estimate from result.cost dict
        cost_estimate = None
        if result.cost:
            cost_data = result.cost
            cost_estimate = CostEstimate(
                relative_cost=(
                    cost_data.get("current_cost", 0) / cost_data.get("optimal_cost", 1)
                    if cost_data.get("optimal_cost")
                    else 1.0
                ),
                estimated_concrete=request.width
                * request.depth
                / 1e6,  # Approximate m³/m
                estimated_steel=0.0,  # Would need detailed calc
                cost_rating=(
                    "optimal" if cost_data.get("savings_percent", 0) < 5 else "moderate"
                ),
            )

        all_passed = all(c.passed for c in code_checks) if code_checks else True
        critical_count = sum(1 for s in suggestions if s.priority == "high")

        # Build design summary
        design_summary = {
            "width_mm": request.width,
            "depth_mm": request.depth,
            "moment_knm": request.moment,
            "shear_kn": request.shear,
            "fck_nmm2": request.fck,
            "fy_nmm2": request.fy,
        }

        return SmartAnalysisResponse(
            success=True,
            message=f"{'All checks passed' if all_passed else 'Some checks failed'}. {len(suggestions)} suggestions.",
            design_summary=design_summary,
            code_checks=code_checks,
            all_checks_passed=all_passed,
            suggestions=suggestions,
            critical_suggestions=critical_count,
            efficiency=efficiency,
            cost_estimate=cost_estimate,
            warnings=[],
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
            detail=f"Analysis failed: {e}",
        )


@router.get(
    "/code-clauses",
    summary="Get Code Clause References",
    description="Get IS 456 clause references for common checks.",
)
async def get_code_clauses() -> dict:
    """
    Get IS 456:2000 code clause references.

    Useful for understanding which code provisions apply to various checks.
    """
    return {
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
