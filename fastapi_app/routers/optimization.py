"""
Cost Optimization Router.

Endpoints for beam cost optimization calculations.
"""

import logging
import math
from typing import Any

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from structural_lib.services.optimization import OptimizationInfeasibleError

from fastapi_app.error_utils import sanitize_error, sanitize_float
from fastapi_app.models.response import APIResponse, error_response, success_response
from fastapi_app.models.optimization import (
    CostOptimizationRequest,
    CostOptimizationResponse,
    OptimalDesign,
    CostBreakdown,
    ParetoRequest,
    ParetoResponse,
    ParetoCandidateResponse,
)
from fastapi_app.models.metadata import CostRatesResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/optimization",
    tags=["optimization"],
)


# =============================================================================
# Optimization Endpoints
# =============================================================================


@router.post(
    "/beam/cost",
    response_model=APIResponse[CostOptimizationResponse],
    summary="Optimize Beam Cost",
    description="Find the most cost-effective beam section for given loading.",
)
async def optimize_beam_cost(
    request: CostOptimizationRequest,
):
    """
    Optimize beam section for minimum cost.

    Evaluates multiple width/depth combinations and returns:
    - Optimal solution with lowest cost
    - Alternative solutions ranked by cost
    - Cost breakdown (concrete, steel, formwork)

    The endpoint uses the request's exact material grade, effective-depth
    basis, search grid, unit costs, and factored actions. It performs maintained
    flexure and shear design; the reported L/d ratio is descriptive and is not
    a deflection check.
    """
    try:
        from structural_lib.services.api import CostProfile
        from structural_lib.services.api import OptimizationConstraints
        from structural_lib.services.api import optimize_beam_cost as optimize_func

        cost_profile = CostProfile(
            currency=request.cost_params.currency.upper(),
            concrete_costs={request.fck: request.cost_params.concrete_cost},
            steel_cost_per_kg=request.cost_params.steel_cost,
            formwork_cost_per_m2=request.cost_params.formwork_cost,
            congestion_threshold_pt=request.cost_params.congestion_threshold_pt,
            congestion_multiplier=request.cost_params.congestion_multiplier,
            location_factor=request.cost_params.location_factor,
        )
        constraints = OptimizationConstraints(
            min_width_mm=request.constraints.min_width,
            max_width_mm=request.constraints.max_width,
            min_depth_mm=request.constraints.min_depth,
            max_depth_mm=request.constraints.max_depth,
            width_step_mm=request.constraints.width_step,
            depth_step_mm=request.constraints.depth_step,
            min_flexural_utilization=request.constraints.min_utilization,
        )
        effective_depth_deduction_mm = (
            request.clear_cover
            + request.stirrup_diameter
            + 0.5 * request.main_bar_diameter
        )
        asv_mm2 = request.stirrup_legs * math.pi * request.stirrup_diameter**2 / 4.0

        result = optimize_func(
            units="IS456",
            span_mm=request.span_length,
            mu_knm=request.moment,
            vu_kn=request.shear,
            cost_profile=cost_profile,
            effective_depth_deduction_mm=effective_depth_deduction_mm,
            fck_nmm2=request.fck,
            fy_nmm2=request.fy,
            constraints=constraints,
            asv_mm2=asv_mm2,
            max_alternatives=request.max_alternatives,
        )

        optimal = _to_response_design(
            result.optimal_design,
            rank=1,
            span_mm=request.span_length,
            clear_cover_mm=request.clear_cover,
            main_bar_diameter_mm=request.main_bar_diameter,
            stirrup_diameter_mm=request.stirrup_diameter,
            stirrup_legs=request.stirrup_legs,
            location_factor=request.cost_params.location_factor,
        )

        alternatives = []
        if request.include_alternatives and result.alternatives:
            for i, alt in enumerate(
                result.alternatives[: request.max_alternatives], start=2
            ):
                alternatives.append(
                    _to_response_design(
                        alt,
                        rank=i,
                        span_mm=request.span_length,
                        clear_cover_mm=request.clear_cover,
                        main_bar_diameter_mm=request.main_bar_diameter,
                        stirrup_diameter_mm=request.stirrup_diameter,
                        stirrup_legs=request.stirrup_legs,
                        location_factor=request.cost_params.location_factor,
                    )
                )

        return success_response(
            CostOptimizationResponse(
                success=True,
                message=(
                    f"Optimal: {optimal.width:.0f}×{optimal.depth:.0f} mm; "
                    f"total longitudinal-reinforcement basis cost "
                    f"{optimal.cost_breakdown.currency} "
                    f"{optimal.cost_breakdown.total_cost:.0f}"
                ),
                optimal=optimal,
                alternatives=alternatives,
                total_combinations_evaluated=result.candidates_evaluated,
                valid_solutions_found=result.candidates_valid,
                savings_vs_baseline=result.savings_percent,
                warnings=[
                    "Longitudinal reinforcement quantity and cost exclude stirrup "
                    "mass; shear safety and spacing use the supplied stirrup basis."
                ],
            )
        )

    except ImportError as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=error_response(sanitize_error(e, "cost optimization")),
        )
    except OptimizationInfeasibleError:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(
                {
                    "code": "OPTIMIZATION_INFEASIBLE",
                    "message": (
                        "No beam candidate satisfies the supplied materials, "
                        "actions, reinforcement basis, and search constraints."
                    ),
                }
            ),
        )
    except (ValueError, TypeError):
        logger.exception("Invalid input for cost optimization")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response("Invalid input parameters"),
        )
    except (RuntimeError, KeyError, AttributeError):
        logger.exception("Internal error in optimize_beam_cost")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response("Internal calculation error"),
        )


def _to_response_design(
    candidate: Any,
    *,
    rank: int,
    span_mm: float,
    clear_cover_mm: float,
    main_bar_diameter_mm: float,
    stirrup_diameter_mm: float,
    stirrup_legs: int,
    location_factor: float,
) -> OptimalDesign:
    """Map one stable optimizer candidate without engineering arithmetic."""
    span_m = span_mm / 1000.0
    cost = candidate.cost_breakdown
    cost_breakdown = CostBreakdown(
        concrete_cost=cost.concrete_cost,
        steel_cost=cost.steel_cost,
        formwork_cost=cost.formwork_cost,
        labor_adjustment=cost.labor_adjustment,
        location_factor=location_factor,
        total_cost=cost.total_cost,
        cost_per_meter=cost.total_cost / span_m,
        currency=cost.currency,
    )
    return OptimalDesign(
        width=candidate.b_mm,
        depth=candidate.D_mm,
        effective_depth=candidate.d_mm,
        effective_depth_deduction=candidate.effective_depth_deduction_mm,
        clear_cover=clear_cover_mm,
        main_bar_diameter=main_bar_diameter_mm,
        stirrup_diameter=stirrup_diameter_mm,
        stirrup_legs=stirrup_legs,
        fck=candidate.fck_nmm2,
        fy=candidate.fy_nmm2,
        ast_required=candidate.ast_required_mm2,
        asc_required=candidate.asc_required_mm2,
        utilization=candidate.flexural_utilization,
        shear_utilization=candidate.shear_utilization,
        stirrup_utilization=candidate.stirrup_utilization,
        shear_stress=candidate.shear_tau_v_nmm2,
        concrete_shear_strength=candidate.shear_tau_c_nmm2,
        maximum_shear_stress=candidate.shear_tau_c_max_nmm2,
        stirrup_spacing=candidate.stirrup_spacing_mm,
        shear_reinforcement_area=candidate.shear_reinforcement_area_mm2,
        ld_ratio=span_mm / candidate.d_mm,
        concrete_volume=candidate.b_mm * candidate.D_mm / 1_000_000.0,
        steel_weight=candidate.longitudinal_steel_weight_kg / span_m,
        steel_weight_total=candidate.longitudinal_steel_weight_kg,
        formwork_area=(candidate.b_mm + 2.0 * candidate.D_mm) / 1000.0,
        cost_breakdown=cost_breakdown,
        rank=rank,
        score=cost.total_cost,
        is_safe=candidate.is_valid,
        code_edition=candidate.code_edition,
        clause_refs=dict(candidate.clause_refs),
        quantity_basis=candidate.quantity_basis,
    )


@router.get(
    "/cost-rates",
    response_model=APIResponse[CostRatesResponse],
    summary="Get Default Cost Rates",
    description="Get default material and labor cost rates.",
)
async def get_cost_rates():
    """
    Get default cost rates for optimization.

    Returns typical Indian market rates (can be overridden in requests).
    """
    return success_response(
        {
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
    )


@router.post(
    "/beam/pareto",
    response_model=APIResponse[ParetoResponse],
    summary="Pareto Multi-Objective Beam Optimization",
    description="Find Pareto-optimal flexure-and-shear-feasible beam designs balancing cost, weight, and governing utilization using an NSGA-II inspired algorithm.",
)
async def optimize_beam_pareto(
    request: ParetoRequest,
):
    """
    Multi-objective Pareto optimization for beam design.

    Generates diverse beam designs varying width, depth, and material grades,
    then identifies the Pareto front for the specified objectives.

    Returns:
    - Pareto-optimal designs (rank 1 front)
    - Best design by each objective
    - Total candidates evaluated
    """
    try:
        from structural_lib import optimize_pareto_front, CostProfile

        result = optimize_pareto_front(
            span_mm=request.span_mm,
            mu_knm=request.mu_knm,
            vu_kn=request.vu_kn,
            objectives=request.objectives,
            cost_profile=CostProfile(),
            cover_mm=request.cover_mm,
            max_candidates=request.max_candidates,
            asv_mm2=request.asv_mm2,
        )

        def _candidate_to_response(c) -> ParetoCandidateResponse:
            d = c.to_dict()
            d["crowding_distance"] = sanitize_float(d["crowding_distance"])
            return ParetoCandidateResponse(**d)

        pareto_front = [_candidate_to_response(c) for c in result.pareto_front]

        response = ParetoResponse(
            pareto_front=pareto_front,
            pareto_count=len(result.pareto_front),
            total_candidates=len(result.all_candidates),
            objectives_used=result.objectives_used,
            computation_time_sec=round(result.computation_time_sec, 3),
            best_by_cost=(
                _candidate_to_response(result.best_by_cost)
                if result.best_by_cost
                else None
            ),
            best_by_utilization=(
                _candidate_to_response(result.best_by_utilization)
                if result.best_by_utilization
                else None
            ),
            best_by_weight=(
                _candidate_to_response(result.best_by_weight)
                if result.best_by_weight
                else None
            ),
            limitations=list(result.limitations),
        )

        return success_response(response.model_dump())

    except ImportError as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=error_response(sanitize_error(e, "pareto optimization")),
        )
    except (ValueError, TypeError):
        logger.exception("Invalid input for pareto optimization")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response("Invalid input parameters"),
        )
    except (RuntimeError, KeyError, AttributeError):
        logger.exception("Internal error in optimize_pareto_front")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response("Internal calculation error"),
        )
