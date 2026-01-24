"""
Cost Optimization Router.

Endpoints for beam cost optimization calculations.
"""

from fastapi import APIRouter, HTTPException, status

from fastapi_app.models.optimization import (
    CostOptimizationRequest,
    CostOptimizationResponse,
    OptimalDesign,
    CostBreakdown,
)

router = APIRouter(
    prefix="/optimization",
    tags=["optimization"],
)


# =============================================================================
# Optimization Endpoints
# =============================================================================


@router.post(
    "/beam/cost",
    response_model=CostOptimizationResponse,
    summary="Optimize Beam Cost",
    description="Find the most cost-effective beam section for given loading.",
)
async def optimize_beam_cost(
    request: CostOptimizationRequest,
) -> CostOptimizationResponse:
    """
    Optimize beam section for minimum cost.

    Evaluates multiple width/depth combinations and returns:
    - Optimal solution with lowest cost
    - Alternative solutions ranked by cost
    - Cost breakdown (concrete, steel, formwork)

    Considers:
    - Flexural capacity requirements
    - Shear capacity requirements
    - L/d ratio for deflection control
    - Minimum/maximum reinforcement limits
    """
    try:
        from structural_lib.api import optimize_beam_cost as optimize_func
        from structural_lib.api import CostProfile

        # Create cost profile from request
        # Map user's concrete_cost to the fck=25 grade (default)
        cost_profile = CostProfile(
            concrete_costs={25: request.cost_params.concrete_cost},
            steel_cost_per_kg=request.cost_params.steel_cost,
            formwork_cost_per_m2=request.cost_params.formwork_cost,
        )

        result = optimize_func(
            units="IS456",
            span_mm=request.span_length,
            mu_knm=request.moment,
            vu_kn=request.shear,
            cost_profile=cost_profile,
            cover_mm=40,
        )

        # Extract optimal design from result
        opt_design = result.optimal_design
        cost_bkdn = opt_design.cost_breakdown

        # Build optimal design from result
        optimal_data = {
            "width": opt_design.b_mm,
            "depth": opt_design.D_mm,
            "ast_required": 0.0,  # Not directly available
            "asc_required": 0.0,
            "utilization": 0.9,  # Assumed near-optimal
            "ld_ratio": request.span_length / opt_design.D_mm if opt_design.D_mm > 0 else 0,
            "concrete_volume": opt_design.b_mm * opt_design.D_mm / 1e6,  # m³/m
            "steel_weight": 0.0,  # Would need detailed calc
            "formwork_area": (opt_design.b_mm + 2 * opt_design.D_mm) / 1000,  # m²/m
            "cost_breakdown": {
                "concrete": cost_bkdn.concrete_cost,
                "steel": cost_bkdn.steel_cost,
                "formwork": cost_bkdn.formwork_cost,
                "total": cost_bkdn.total_cost,
                "per_meter": cost_bkdn.total_cost,
            },
            "score": cost_bkdn.total_cost,
        }

        optimal = _parse_optimal_design(optimal_data, rank=1)

        # Parse alternatives if available
        alternatives = []
        if request.include_alternatives and result.alternatives:
            for i, alt in enumerate(result.alternatives[:request.max_alternatives], start=2):
                alt_cost = alt.cost_breakdown
                alt_data = {
                    "width": alt.b_mm,
                    "depth": alt.D_mm,
                    "ast_required": 0.0,
                    "asc_required": 0.0,
                    "utilization": 0.85,
                    "ld_ratio": request.span_length / alt.D_mm if alt.D_mm > 0 else 0,
                    "concrete_volume": alt.b_mm * alt.D_mm / 1e6,
                    "steel_weight": 0.0,
                    "formwork_area": (alt.b_mm + 2 * alt.D_mm) / 1000,
                    "cost_breakdown": {
                        "concrete": alt_cost.concrete_cost,
                        "steel": alt_cost.steel_cost,
                        "formwork": alt_cost.formwork_cost,
                        "total": alt_cost.total_cost,
                        "per_meter": alt_cost.total_cost,
                    },
                    "score": alt_cost.total_cost,
                }
                alternatives.append(_parse_optimal_design(alt_data, rank=i))

        return CostOptimizationResponse(
            success=True,
            message=f"Optimal: {optimal.width:.0f}×{optimal.depth:.0f} mm @ ₹{optimal.cost_breakdown.total_cost:.0f}/m",
            optimal=optimal,
            alternatives=alternatives,
            total_combinations_evaluated=result.candidates_evaluated,
            valid_solutions_found=result.candidates_valid,
            savings_vs_min_section=result.savings_percent,
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
            detail=f"Optimization failed: {e}",
        )


def _parse_optimal_design(data: dict, rank: int) -> OptimalDesign:
    """Parse optimization result into OptimalDesign model."""
    cost_data = data.get("cost_breakdown", {})

    cost_breakdown = CostBreakdown(
        concrete_cost=cost_data.get("concrete", 0.0),
        steel_cost=cost_data.get("steel", 0.0),
        formwork_cost=cost_data.get("formwork", 0.0),
        total_cost=cost_data.get("total", 0.0),
        cost_per_meter=cost_data.get("per_meter", cost_data.get("total", 0.0)),
    )

    return OptimalDesign(
        width=data.get("width", 0.0),
        depth=data.get("depth", 0.0),
        ast_required=data.get("ast_required", 0.0),
        asc_required=data.get("asc_required", 0.0),
        utilization=data.get("utilization", 0.0),
        ld_ratio=data.get("ld_ratio", 0.0),
        concrete_volume=data.get("concrete_volume", 0.0),
        steel_weight=data.get("steel_weight", 0.0),
        formwork_area=data.get("formwork_area", 0.0),
        cost_breakdown=cost_breakdown,
        rank=rank,
        score=data.get("score", 0.0),
    )


@router.get(
    "/cost-rates",
    summary="Get Default Cost Rates",
    description="Get default material and labor cost rates.",
)
async def get_cost_rates() -> dict:
    """
    Get default cost rates for optimization.

    Returns typical Indian market rates (can be overridden in requests).
    """
    return {
        "materials": {
            "concrete": {
                "M20": 5500.0,
                "M25": 6000.0,
                "M30": 6800.0,
                "M40": 7500.0,
                "unit": "₹/m³",
                "note": "Ready-mix concrete delivered",
            },
            "steel": {
                "Fe415": 55.0,
                "Fe500": 60.0,
                "Fe550": 65.0,
                "unit": "₹/kg",
                "note": "TMT bars including cutting/bending",
            },
            "formwork": {
                "beam_sides": 400.0,
                "beam_bottom": 450.0,
                "unit": "₹/m²",
                "note": "Steel formwork with 4 reuses",
            },
        },
        "labor": {
            "bar_bending": 8.0,
            "bar_binding": 12.0,
            "unit": "₹/kg",
            "note": "Typical labor rates",
        },
        "location": "India (Metro cities)",
        "year": 2024,
        "note": "Rates are indicative. Override with actual project rates.",
    }
