# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Insights Router.

Endpoints for dashboard aggregation, code checks, and optimization suggestions.
Uses structural_lib.dashboard for canonical computations.
"""

import logging

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from fastapi_app.models.boq import (
    ConcreteSummaryResponse,
    ProjectBOQRequest,
    ProjectBOQResponse,
    SteelSummaryResponse,
    StorySummaryResponse,
)

from fastapi_app.models.response import error_response, success_response

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/insights",
    tags=["insights"],
)


# =============================================================================
# Request/Response Models
# =============================================================================


class BeamResult(BaseModel):
    """A single beam design result for dashboard aggregation."""

    beam_id: str = Field(max_length=200, description="Beam identifier")
    story: str = Field(default="Unknown", max_length=200, description="Story/floor")
    is_valid: bool = Field(default=True, description="Whether design passed")
    utilization: float = Field(
        default=0.0, ge=0.0, le=2.0, description="Utilization ratio"
    )
    ast_provided: float = Field(default=0.0, description="Steel area provided (mm²)")
    b_mm: float = Field(default=300.0, description="Beam width (mm)")
    D_mm: float = Field(default=500.0, description="Beam depth (mm)")
    span_mm: float = Field(default=5000.0, description="Beam span (mm)")
    warnings: list[str] = Field(default_factory=list, description="Warning messages")


class DashboardRequest(BaseModel):
    """Request model for dashboard generation."""

    results: list[BeamResult] = Field(
        min_length=1, description="List of beam design results"
    )


class StoryStats(BaseModel):
    """Per-story statistics."""

    total: int = Field(default=0, description="Total beams in story")
    passed: int = Field(default=0, description="Passed beams")
    failed: int = Field(default=0, description="Failed beams")


class DashboardResponse(BaseModel):
    """Response model for dashboard with aggregated statistics."""

    success: bool = Field(description="Whether generation succeeded")
    message: str = Field(description="Summary message")
    total_beams: int = Field(description="Total number of beams")
    passed: int = Field(description="Number of passed beams")
    failed: int = Field(description="Number of failed beams")
    pass_rate: float = Field(description="Pass rate percentage")
    warnings_count: int = Field(description="Total warning count")
    avg_utilization: float = Field(description="Average utilization")
    max_utilization: float = Field(description="Maximum utilization")
    min_utilization: float = Field(description="Minimum utilization")
    total_steel_kg: float = Field(description="Total steel quantity (kg)")
    total_concrete_m3: float = Field(description="Total concrete volume (m³)")
    critical_beams: list[str] = Field(description="List of critical beam IDs")
    by_story: dict[str, StoryStats] = Field(description="Statistics by story")


class BeamParams(BaseModel):
    """Beam parameters for code checks."""

    b_mm: float = Field(default=300.0, description="Beam width (mm)")
    D_mm: float = Field(default=500.0, description="Beam depth (mm)")
    d_mm: float | None = Field(default=None, description="Effective depth (mm)")
    span_mm: float = Field(default=5000.0, description="Beam span (mm)")
    fck_mpa: float = Field(default=25.0, description="Concrete grade (MPa)")
    fy_mpa: float = Field(default=500.0, description="Steel grade (MPa)")
    mu_knm: float = Field(default=100.0, description="Design moment (kN·m)")
    vu_kn: float = Field(default=50.0, description="Design shear (kN)")


class RebarParams(BaseModel):
    """Rebar configuration for code checks."""

    ast_mm2: float = Field(default=0.0, description="Steel area (mm²)")
    bar_count: int = Field(default=0, description="Number of bars")
    bar_dia_mm: float = Field(default=16.0, description="Bar diameter (mm)")


class CodeChecksRequest(BaseModel):
    """Request model for live code checks."""

    beam: BeamParams = Field(description="Beam parameters")
    config: RebarParams | None = Field(
        default=None, description="Optional rebar config"
    )


class CheckDetail(BaseModel):
    """Individual check result."""

    name: str = Field(description="Check name")
    clause: str = Field(description="IS 456 clause reference")
    passed: bool = Field(description="Whether check passed")
    value: float = Field(description="Actual value")
    limit: float = Field(description="Code limit")
    utilization: float | None = Field(
        default=None, description="Utilization if applicable"
    )


class CodeChecksResponse(BaseModel):
    """Response model for code checks."""

    success: bool = Field(description="Whether check completed")
    message: str = Field(description="Summary message")
    passed: bool = Field(description="All checks passed")
    checks: list[CheckDetail] = Field(description="Individual check results")
    critical_failures: list[str] = Field(description="Critical failure messages")
    warnings: list[str] = Field(description="Warning messages")
    utilization: float = Field(description="Governing utilization")
    governing_check: str = Field(description="Name of governing check")


class RebarSuggestRequest(BaseModel):
    """Request model for rebar optimization suggestions."""

    beam_id: str = Field(default="beam", max_length=200, description="Beam identifier")
    ast_required: float = Field(ge=0, description="Required steel area (mm²)")
    ast_provided: float = Field(default=0.0, description="Current steel area (mm²)")
    bar_count: int = Field(default=0, description="Current bar count")
    bar_dia_mm: float = Field(default=16.0, description="Current bar diameter (mm)")
    b_mm: float = Field(default=300.0, description="Beam width (mm)")
    cover_mm: float = Field(default=40.0, description="Clear cover (mm)")


class SuggestionItem(BaseModel):
    """A single optimization suggestion."""

    id: str = Field(description="Suggestion identifier")
    title: str = Field(description="Short title (e.g., '4Ø16mm')")
    description: str = Field(description="Full description")
    impact: str = Field(description="Impact level: LOW, MEDIUM, HIGH")
    savings_percent: float = Field(description="Steel savings percentage")
    suggested_config: dict = Field(description="Suggested rebar configuration")
    rationale: str = Field(description="Explanation of suggestion")


class RebarSuggestResponse(BaseModel):
    """Response model for rebar suggestions."""

    success: bool = Field(description="Whether suggestion generation succeeded")
    message: str = Field(description="Summary message")
    beam_id: str = Field(description="Beam identifier")
    suggestion_count: int = Field(description="Number of suggestions")
    suggestions: list[SuggestionItem] = Field(description="Optimization suggestions")
    current_ast_mm2: float = Field(description="Current steel area (mm²)")
    min_ast_mm2: float = Field(description="Minimum required steel area (mm²)")
    max_savings_percent: float = Field(description="Maximum possible savings")


# =============================================================================
# Endpoints
# =============================================================================


@router.post(
    "/dashboard",
    summary="Generate Dashboard Summary",
    description="Generate aggregated statistics from multiple beam design results.",
)
async def generate_dashboard(request: DashboardRequest):
    """
    Generate an aggregated dashboard from beam design results.

    Provides:
    - Pass/fail counts and rates
    - Utilization statistics (min/avg/max)
    - Steel and concrete quantities
    - Critical beam identification
    - Per-story breakdown
    """
    try:
        from structural_lib.services.dashboard import (
            generate_dashboard as lib_dashboard,
        )

        # Convert Pydantic models to dicts for library
        results_dicts = [r.model_dump() for r in request.results]

        # Generate dashboard
        summary = lib_dashboard(results_dicts)
        summary_dict = summary.to_dict()

        # Convert by_story to Pydantic models
        by_story_models = {
            story: StoryStats(**stats)
            for story, stats in summary_dict.get("by_story", {}).items()
        }

        return success_response(
            DashboardResponse(
                success=True,
                message=f"Dashboard generated for {summary.total_beams} beams",
                total_beams=summary.total_beams,
                passed=summary.passed,
                failed=summary.failed,
                pass_rate=summary_dict.get("pass_rate", 0.0),
                warnings_count=summary.warnings_count,
                avg_utilization=summary_dict.get("avg_utilization", 0.0),
                max_utilization=summary_dict.get("max_utilization", 0.0),
                min_utilization=summary_dict.get("min_utilization", 0.0),
                total_steel_kg=summary_dict.get("total_steel_kg", 0.0),
                total_concrete_m3=summary_dict.get("total_concrete_m3", 0.0),
                critical_beams=summary.critical_beams[:10],
                by_story=by_story_models,
            )
        )
    except ImportError:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=error_response("Dashboard module not available"),
        )
    except (RuntimeError, KeyError, ImportError):
        logger.exception("Internal error in generate_dashboard")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response("Internal calculation error"),
        )


@router.post(
    "/code-checks",
    summary="Live IS 456 Code Checks",
    description="Perform fast code checks for real-time UI updates during editing.",
)
async def code_checks_live(request: CodeChecksRequest):
    """
    Perform live IS 456 code checks on a beam.

    Designed for real-time UI feedback during editing.
    Returns pass/fail status with detailed check results.

    Checks include:
    - Minimum/maximum steel (Cl. 26.5.1.1)
    - Span/depth ratio (Cl. 23.2.1)
    - Moment capacity (Annex G)
    - Width requirements
    """
    try:
        from structural_lib.services.dashboard import code_checks_live as lib_checks

        beam_dict = request.beam.model_dump()
        config_dict = request.config.model_dump() if request.config else None

        result = lib_checks(beam_dict, config_dict)
        result_dict = result.to_dict()

        # Convert checks to Pydantic models
        check_models = [
            CheckDetail(
                name=c.get("name", ""),
                clause=c.get("clause", ""),
                passed=c.get("passed", True),
                value=c.get("value", 0.0),
                limit=c.get("limit", 0.0),
                utilization=c.get("utilization"),
            )
            for c in result_dict.get("checks", [])
        ]

        status_msg = (
            "All checks passed"
            if result.passed
            else f"{len(result.critical_failures)} check(s) failed"
        )

        return success_response(
            CodeChecksResponse(
                success=True,
                message=status_msg,
                passed=result.passed,
                checks=check_models,
                critical_failures=result.critical_failures,
                warnings=result.warnings,
                utilization=result_dict.get("utilization", 0.0),
                governing_check=result.governing_check,
            )
        )
    except ImportError:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=error_response("Dashboard module not available"),
        )
    except (RuntimeError, KeyError, ImportError):
        logger.exception("Internal error in code_checks_live")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response("Internal calculation error"),
        )


@router.post(
    "/rebar-suggest",
    summary="Suggest Rebar Optimizations",
    description="Generate optimized rebar configuration suggestions for a beam.",
)
async def suggest_rebar_options(request: RebarSuggestRequest):
    """
    Suggest optimized rebar configurations for a beam.

    Generates alternative bar combinations that:
    - Meet the required steel area
    - Fit within the beam width
    - Reduce steel quantity where possible

    Returns up to 5 suggestions sorted by savings.
    """
    try:
        from structural_lib.services.dashboard import (
            suggest_rebar_options as lib_suggest,
        )

        beam_dict = request.model_dump()
        result = lib_suggest(beam_dict)
        result_dict = result.to_dict()

        # Convert suggestions to Pydantic models
        suggestion_models = [
            SuggestionItem(
                id=s.get("id", ""),
                title=s.get("title", ""),
                description=s.get("description", ""),
                impact=s.get("impact", "LOW"),
                savings_percent=s.get("savings_percent", 0.0),
                suggested_config=s.get("suggested_config", {}),
                rationale=s.get("rationale", ""),
            )
            for s in result_dict.get("suggestions", [])
        ]

        count = len(suggestion_models)
        msg = (
            f"Found {count} optimization suggestion(s)"
            if count > 0
            else "No optimization opportunities found"
        )

        return success_response(
            RebarSuggestResponse(
                success=True,
                message=msg,
                beam_id=result.beam_id,
                suggestion_count=count,
                suggestions=suggestion_models,
                current_ast_mm2=result_dict.get("current_ast_mm2", 0.0),
                min_ast_mm2=result_dict.get("min_ast_mm2", 0.0),
                max_savings_percent=result_dict.get("max_savings_percent", 0.0),
            )
        )
    except ImportError:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=error_response("Dashboard module not available"),
        )
    except (RuntimeError, KeyError, ImportError):
        logger.exception("Internal error in suggest_rebar_options")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response("Internal calculation error"),
        )


@router.post(
    "/project-boq",
    summary="Project Bill of Quantities",
    description="Aggregate project BOQ from beam metadata with steel/concrete costs.",
)
async def project_boq(request: ProjectBOQRequest):
    """Aggregate project Bill of Quantities from beam metadata.

    Calculates total steel weight, concrete volume, and costs
    across all beams, grouped by story and material grade.
    """
    try:
        from structural_lib.services.boq import DEFAULT_CONCRETE_COSTS

        concrete_costs = (
            request.concrete_costs
            if request.concrete_costs is not None
            else dict(DEFAULT_CONCRETE_COSTS)
        )
        steel_rate = request.steel_cost_per_kg

        # Accumulators
        story_acc: dict[str, dict] = {}
        concrete_by_grade: dict[str, dict] = {}
        total_steel = 0.0
        total_concrete = 0.0
        total_cost = 0.0

        for beam in request.beams:
            # Concrete volume: b × D × span (mm³ → m³)
            concrete_vol = beam.b_mm * beam.D_mm * beam.span_mm / 1e9
            c_rate = concrete_costs.get(beam.fck, 6000.0)
            c_cost = c_rate * concrete_vol
            s_cost = steel_rate * beam.steel_weight_kg

            # Story accumulation
            if beam.story not in story_acc:
                story_acc[beam.story] = {
                    "beam_count": 0,
                    "steel_kg": 0.0,
                    "concrete_m3": 0.0,
                    "cost_inr": 0.0,
                }
            sa = story_acc[beam.story]
            sa["beam_count"] += 1
            sa["steel_kg"] += beam.steel_weight_kg
            sa["concrete_m3"] += concrete_vol
            sa["cost_inr"] += c_cost + s_cost

            # Concrete by grade
            grade_key = f"M{beam.fck}"
            if grade_key not in concrete_by_grade:
                concrete_by_grade[grade_key] = {"volume": 0.0, "cost": 0.0}
            concrete_by_grade[grade_key]["volume"] += concrete_vol
            concrete_by_grade[grade_key]["cost"] += c_cost

            total_steel += beam.steel_weight_kg
            total_concrete += concrete_vol
            total_cost += c_cost + s_cost

        # Build response lists
        steel_total_cost = total_steel * steel_rate
        steel_list = (
            [
                SteelSummaryResponse(
                    grade="Fe500",
                    total_weight_kg=round(total_steel, 2),
                    cost_inr=round(steel_total_cost, 2),
                )
            ]
            if total_steel > 0
            else []
        )

        concrete_list = [
            ConcreteSummaryResponse(
                grade=g,
                total_volume_m3=round(d["volume"], 4),
                cost_inr=round(d["cost"], 2),
            )
            for g, d in sorted(concrete_by_grade.items())
        ]

        story_list = [
            StorySummaryResponse(
                story=s,
                beam_count=d["beam_count"],
                steel_kg=round(d["steel_kg"], 2),
                concrete_m3=round(d["concrete_m3"], 4),
                cost_inr=round(d["cost_inr"], 2),
            )
            for s, d in sorted(story_acc.items())
        ]

        return success_response(
            ProjectBOQResponse(
                success=True,
                project_name=request.project_name,
                total_beams=len(request.beams),
                steel=steel_list,
                concrete=concrete_list,
                by_story=story_list,
                grand_total_steel_kg=round(total_steel, 2),
                grand_total_concrete_m3=round(total_concrete, 4),
                grand_total_cost_inr=round(total_cost, 2),
            )
        )
    except (RuntimeError, KeyError, ImportError):
        logger.exception("Internal error in project_boq")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response("Internal calculation error"),
        )
