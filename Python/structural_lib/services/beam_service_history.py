"""Finite-age gravity service history using prescribed material inputs."""

from __future__ import annotations

import html
import math
from dataclasses import replace
from typing import Any, Literal

from pydantic import Field

from structural_lib.beam.reinforcement import Face
from structural_lib.beam.semantics import ExecutionState
from structural_lib.beam.serviceability import (
    CalculatedDeflectionBasis,
    DeflectionCheckRequest,
    DeflectionCriterion,
    DeflectionLimitRequest,
    DeflectionMethod,
    check_deflection,
)
from structural_lib.codes.is456.beam.serviceability import (
    calculate_shrinkage_curvature,
    calculate_shrinkage_deflection,
)
from structural_lib.codes.is456.beam.torsion_serviceability import (
    cracked_service_section,
    uniform_flexural_deflection,
)
from structural_lib.core.result_contract import (
    CalculationStatus,
    EngineeringStatus,
    FreshnessStatus,
    StructuralIssueV1,
)
from structural_lib.services.beam_instantaneous_service import (
    BeamInstantaneousLoadV1,
    _BeamServiceInput,
    _evaluate_instantaneous_service,
    _face_crack,
    _service_bars,
)
from structural_lib.services.canonical_family import (
    CanonicalFamilyResultV1,
    canonical_family_result,
    require_request_type,
)
from structural_lib.services.contracts.beam_continuous import (
    BeamSectionCheckRequestV1,
    Reference,
)
from structural_lib.services.contracts.common import StrictPublicModel

WORKFLOW = "is456.beam.finite-service-history/v1"


class BeamServiceAgeV1(StrictPublicModel):
    """Cumulative finite-age creep and free shrinkage since sustained loading."""

    age_days: float = Field(gt=0, le=36500)
    creep_coefficient: float = Field(ge=0, le=10)
    shrinkage_strain: float = Field(ge=0, le=0.003)


class BeamServiceHistoryV1(StrictPublicModel):
    """One sustained UDL followed by an assessment-only transient UDL."""

    sustained_load: BeamInstantaneousLoadV1 | None = None
    loading_age_days: float = Field(gt=0, le=36500)
    at_finishes: BeamServiceAgeV1
    at_assessment: BeamServiceAgeV1
    relative_humidity_percent: float = Field(gt=0, le=100)
    notional_size_mm: float = Field(gt=0, le=3000)
    finish_added_load_kn_per_m: float = Field(ge=0, le=1000)
    source_reference: Reference
    bending_basis: Literal["downward_gravity", "reverse"]


class BeamServiceHistoryInputV1(_BeamServiceInput):
    """The instantaneous physical member plus an explicit finite-age history."""

    schema_version: Literal["is456-beam-finite-service-history-input/v1"] = (
        "is456-beam-finite-service-history-input/v1"
    )
    history: BeamServiceHistoryV1 | None = None


def _history_issue(request: BeamServiceHistoryInputV1) -> StructuralIssueV1 | None:
    history, total = request.history, request.service_load
    if history is None or history.sustained_load is None or total is None:
        return StructuralIssueV1(
            "BEAM.SUSTAINED_LOAD_HELD",
            "history",
            "Supply both total and sustained service load cases.",
        )
    sustained = history.sustained_load
    if (
        sustained.analysis_revision != request.member.current_analysis_revision
        or sustained.reinforcement_revision != request.member.reinforcement_revision
        or total.analysis_revision != request.member.current_analysis_revision
        or total.reinforcement_revision != request.member.reinforcement_revision
        or request.member.analysis_revision != request.member.current_analysis_revision
    ):
        return StructuralIssueV1(
            "BEAM.SERVICE_REVISION_STALE",
            "history.sustained_load",
            "Service cases must use the current analysis and reinforcement revisions.",
        )
    if (
        not isinstance(request.member, BeamSectionCheckRequestV1)
        or request.member.flange is not None
        or history.bending_basis != "downward_gravity"
        or history.finish_added_load_kn_per_m != 0
        or total.midpoint_load_kn
        or sustained.midpoint_load_kn
        or total.combination_id == sustained.combination_id
        or not 0 < sustained.uniform_load_kn_per_m <= total.uniform_load_kn_per_m
    ):
        return StructuralIssueV1(
            "BEAM.HISTORY_PROFILE_HELD",
            "history",
            "The history requires a simply supported rectangle and separate downward UDL cases with zero finish added load.",
        )
    finish, final = history.at_finishes, history.at_assessment
    if not (
        history.loading_age_days < finish.age_days < final.age_days
        and finish.creep_coefficient <= final.creep_coefficient
        and finish.shrinkage_strain <= final.shrinkage_strain
    ):
        return StructuralIssueV1(
            "BEAM.HISTORY_CHRONOLOGY_HELD",
            "history",
            "Supply ordered ages and nondecreasing cumulative material inputs.",
        )
    return None


def _resolve_history(
    request: BeamServiceHistoryInputV1,
    instantaneous: dict[str, Any],
    input_hash: str,
) -> tuple[dict[str, Any] | None, StructuralIssueV1 | None]:
    history, total = request.history, request.service_load
    assert (
        history is not None and history.sustained_load is not None and total is not None
    )
    sustained = history.sustained_load
    member, span = request.member, request.span_mm
    b, depth = member.width_mm, member.depth_mm
    ec, es = 5000 * math.sqrt(member.fck_nmm2), 200000.0
    bars = _service_bars(request)
    layers = tuple(
        (bar.y_from_top_mm, math.pi * bar.diameter_mm**2 / 4) for bar in bars
    )
    ast = math.fsum(
        area
        for bar, (_, area) in zip(bars, layers, strict=True)
        if bar.face is Face.BOTTOM
    )
    asc = math.fsum(
        area
        for bar, (_, area) in zip(bars, layers, strict=True)
        if bar.face is Face.TOP
    )
    d = (
        math.fsum(
            y * area
            for bar, (y, area) in zip(bars, layers, strict=True)
            if bar.face is Face.BOTTOM
        )
        / ast
    )
    initial = instantaneous["sections"][0]
    axis, inertia = initial["neutral_axis_mm"], initial["cracked_inertia_mm4"]
    immediate_sustained = uniform_flexural_deflection(
        sustained.uniform_load_kn_per_m, span, ec, inertia
    )
    immediate_total = instantaneous["deflection_mm"]
    stages = {}
    for name, stage in (
        ("at_finishes", history.at_finishes),
        ("at_assessment", history.at_assessment),
    ):
        effective = ec / (1 + stage.creep_coefficient)
        effective_axis, effective_inertia = cracked_service_section(
            b, depth, layers, effective, es
        )
        sustained_displacement = uniform_flexural_deflection(
            sustained.uniform_load_kn_per_m, span, effective, effective_inertia
        )
        try:
            shrinkage_curvature = calculate_shrinkage_curvature(
                eps_cs=stage.shrinkage_strain,
                d_mm=d,
                ast_mm2=ast,
                asc_mm2=asc,
                b_mm=b,
                D_mm=depth,
                fck_nmm2=member.fck_nmm2,
            )
        except ValueError as exc:
            return None, StructuralIssueV1(
                "BEAM.SHRINKAGE_MODEL_HELD", "history", str(exc)
            )
        shrinkage = calculate_shrinkage_deflection(
            phi_sh=shrinkage_curvature, span_mm=span
        )
        stages[name] = {
            "age_days": stage.age_days,
            "concrete_modulus_nmm2": effective,
            "neutral_axis_mm": effective_axis,
            "cracked_inertia_mm4": effective_inertia,
            "sustained_deflection_mm": sustained_displacement,
            "shrinkage_deflection_mm": shrinkage,
            "total_deflection_mm": sustained_displacement
            + shrinkage
            + (
                immediate_total - immediate_sustained
                if name == "at_assessment"
                else 0.0
            ),
        }
    finish, final = stages["at_finishes"], stages["at_assessment"]
    g_curvature = (
        sustained.uniform_load_kn_per_m
        * span**2
        / 8
        / (final["concrete_modulus_nmm2"] * final["cracked_inertia_mm4"])
    )
    q_curvature = (
        (total.uniform_load_kn_per_m - sustained.uniform_load_kn_per_m)
        * span**2
        / 8
        / (ec * inertia)
    )
    curvature = g_curvature + q_curvature
    final_axis = (
        g_curvature * final["neutral_axis_mm"] + q_curvature * axis
    ) / curvature
    strain = curvature * (depth - final_axis)
    crack = (
        _face_crack(
            request,
            bars,
            initial["station_id"],
            Face.BOTTOM,
            final_axis,
            es * curvature * (d - final_axis),
            strain,
        )
        if initial["cracked"]
        else None
    )
    deflection = check_deflection(
        DeflectionCheckRequest(
            WORKFLOW,
            DeflectionMethod.CALCULATED_COMPONENTS,
            calculated=CalculatedDeflectionBasis(
                input_hash,
                (f"{total.combination_id}/{initial['station_id']}",),
                (f"{sustained.combination_id}/{initial['station_id']}",),
                instantaneous["analysis"]["result_id"],
                member.reinforcement_revision,
                span,
                immediate_total,
                immediate_sustained,
                final["sustained_deflection_mm"] / immediate_sustained - 1,
                final["shrinkage_deflection_mm"],
                history.at_finishes.age_days,
                finish["total_deflection_mm"],
                history.loading_age_days,
                history.at_assessment.age_days,
                history.at_assessment.age_days - history.loading_age_days,
                history.relative_humidity_percent,
                history.notional_size_mm,
                "fully cracked actual layers",
                "Annex F flexural width",
                "supplied finite-age Ec/(1+phi)",
                "supplied finite-age strain; Annex C-3",
            ),
            total_limit=DeflectionLimitRequest(
                WORKFLOW, span, DeflectionCriterion.TOTAL_FINAL
            ),
            after_finishes_limit=DeflectionLimitRequest(
                WORKFLOW, span, DeflectionCriterion.AFTER_FINISHES
            ),
        )
    )
    return {
        "initial_total_mm": immediate_total,
        "initial_sustained_mm": immediate_sustained,
        **stages,
        "flexural_neutral_axis_mm": final_axis,
        "flexural_surface_strain": strain,
        "flexural_bars": [
            {
                "bar_id": bar.bar_id,
                "steel_stress_nmm2": es * curvature * (final_axis - y),
            }
            for bar, (y, _) in zip(bars, layers, strict=True)
        ],
        "deflection": deflection.to_dict(),
        "crack": crack.to_dict() if crack is not None else None,
    }, None


def check_finite_service_history(
    request: BeamServiceHistoryInputV1,
) -> CanonicalFamilyResultV1[dict[str, Any]]:
    """Check final and after-finishes deflection for one prescribed history.

    Parameters
    ----------
    request : BeamServiceHistoryInputV1
        Physical rectangular beam, total and sustained UDL and finite-age data.

    Returns
    -------
    CanonicalFamilyResultV1
        Recorded age stages, deflection criteria and flexural crack width.

    Raises
    ------
    InputContractError
        The request is not a validated finite history input.

    Examples
    --------
    >>> callable(check_finite_service_history)
    True

    Limitations
    -----------
    One simply supported gravity beam and supplied finite-age material inputs.

    Provenance
    ----------
    IS 456 Annex C-3, C-4 and Annex F with actual bar layers and supplied history.
    """
    require_request_type(request, BeamServiceHistoryInputV1)
    initial = _evaluate_instantaneous_service(request)
    issue = _history_issue(request)
    state = None
    status = EngineeringStatus.HOLD
    instantaneous = initial.calculation["instantaneous"]
    if issue is None and instantaneous is not None:
        identity = initial.envelope.result_identity
        assert identity is not None and identity.input_hash is not None
        state, issue = _resolve_history(request, instantaneous, identity.input_hash)
    if state is not None:
        checks = [
            item for item in (state["deflection"], state["crack"]) if item is not None
        ]
        if initial.engineering_status is EngineeringStatus.FAIL or any(
            item["engineering"] == "fail" for item in checks
        ):
            status = EngineeringStatus.FAIL
            issue = StructuralIssueV1(
                "BEAM.HISTORY_LIMIT_EXCEEDED",
                "history",
                "At least one serviceability limit is exceeded.",
            )
        elif initial.engineering_status is EngineeringStatus.PASS and all(
            item["execution"] == ExecutionState.COMPLETED
            and item["engineering"] == "pass"
            for item in checks
        ):
            status = EngineeringStatus.PASS
        else:
            issue = StructuralIssueV1(
                "BEAM.HISTORY_CALCULATION_HELD",
                "history",
                "A required service check is outside the admitted model.",
            )
    if issue is None and state is None:
        issue = initial.issues[0]
    result = canonical_family_result(
        request,
        {"instantaneous": instantaneous, "history": state},
        workflow_id=WORKFLOW,
        engineering_status=status,
        limitations=(
            "Prescribed finite-age creep and shrinkage inputs. Humidity and size are recorded context.",
            "Sustained UDL acts from loading age and transient UDL acts at assessment only.",
            "Crack width covers flexural strain with no tension-stiffening credit; shrinkage is included in deflection.",
            "Member design acceptance, finish loads, reverse bending and continuous history require separate evidence.",
        ),
        provenance=(
            "IS 456:2000 Cl. 23.2, Annex C-3, C-4 and Annex F; current physical reinforcement and supplied history.",
        ),
    )
    return replace(
        result,
        envelope=replace(
            result.envelope,
            issues=(issue,) if issue is not None else (),
            calculation_status=(
                CalculationStatus.COMPLETED
                if state is not None
                else CalculationStatus.NOT_EVALUATED
            ),
            freshness_status=(
                FreshnessStatus.STALE
                if issue and issue.code == "BEAM.SERVICE_REVISION_STALE"
                else FreshnessStatus.CURRENT
            ),
        ),
    )


def render_finite_service_history_html(
    result: CanonicalFamilyResultV1[dict[str, Any]],
) -> str:
    """Render the checked age stages and service limits.

    Parameters
    ----------
    result : CanonicalFamilyResultV1
        A calculated finite history result.

    Returns
    -------
    str
        HTML report tied to the same physical member and history input hash.

    Raises
    ------
    TypeError
        The result belongs to a different calculation.

    Examples
    --------
    >>> callable(render_finite_service_history_html)
    True

    Limitations
    -----------
    Rendering uses the recorded history without recalculation.

    Provenance
    ----------
    The report uses the age and action evidence in the checked JSON result.
    """
    if (
        not isinstance(result, CanonicalFamilyResultV1)
        or result.workflow_id != WORKFLOW
    ):
        raise TypeError("result must be a finite beam service history result")
    identity = result.envelope.result_identity
    state = result.calculation["history"]
    content = "<p>History held.</p>"
    if state is not None:
        finish, final = state["at_finishes"], state["at_assessment"]
        deflection = state["deflection"]["outputs"]
        after = deflection.get("after_finishes_deflection_mm")
        after_text = f"{after:.5f} mm" if after is not None else "HOLD"
        crack = state["crack"]
        width = crack["outputs"].get("calculated_crack_width_mm") if crack else 0
        width_text = f"{width:.5f} mm" if width is not None else "HOLD"
        request = result.request
        assert isinstance(request, BeamServiceHistoryInputV1)
        history, total = request.history, request.service_load
        assert (
            history is not None
            and history.sustained_load is not None
            and total is not None
        )
        sustained = history.sustained_load
        content = (
            f"<p>Source {html.escape(history.source_reference)}.</p>"
            f"<p>Sustained case {html.escape(sustained.combination_id)} at "
            f"{sustained.uniform_load_kn_per_m:.3f} kN/m from day {history.loading_age_days:g}. "
            f"Total case {html.escape(total.combination_id)} at {total.uniform_load_kn_per_m:.3f} kN/m.</p>"
            f"<p>Day {finish['age_days']:g} deflection {finish['total_deflection_mm']:.5f} mm.</p>"
            f"<p>Day {final['age_days']:g} deflection {final['total_deflection_mm']:.5f} mm.</p>"
            f"<p>After-finishes deflection {after_text}.</p>"
            f"<p>Assessment flexural crack width {width_text}.</p>"
        )
    issues = "".join(
        f"<li>{html.escape(issue.message)}</li>" for issue in result.issues
    )
    limitations = "".join(
        f"<li>{html.escape(item)}</li>" for item in result.limitations
    )
    return f"""<!doctype html>
<html lang="en"><meta charset="utf-8"><title>Beam finite service history</title>
<h1>Beam finite service history · {html.escape(result.identity.case_id)}</h1>
<p>{result.engineering_status.value} · Qualified review required</p>
<p>Input identity <code>{identity.input_hash if identity else ''}</code></p>
{content}<ul>{issues}{limitations}</ul></html>"""
