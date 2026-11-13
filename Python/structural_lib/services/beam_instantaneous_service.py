"""Bounded elastic deflection and flexural cracking for actual rectangular bars."""

from __future__ import annotations

import html
import math
from dataclasses import replace
from typing import Annotated, Any, Literal, Self

from pydantic import Field, model_validator

from structural_lib.beam.analysis import (
    BeamElement,
    BeamLineRequest,
    BeamNode,
    BeamPointLoad,
    solve_beam_line,
)
from structural_lib.beam.reinforcement import (
    BarPosition,
    Face,
    ReinforcementGeometryRequest,
    evaluate_geometry,
)
from structural_lib.beam.semantics import (
    EngineeringState,
    ExecutionState,
    OperationResult,
)
from structural_lib.beam.serviceability import (
    CrackWidthCheckRequest,
    CrackWidthLimitRequest,
    ExposureClass,
    LimitSource,
    check_crack_width,
    crack_width_limit,
)
from structural_lib.codes.is456.beam.serviceability import calculate_cracking_moment
from structural_lib.codes.is456.beam.torsion_serviceability import (
    cracked_service_section,
)
from structural_lib.core.result_contract import (
    CalculationStatus,
    EngineeringStatus,
    FreshnessStatus,
    StructuralIssueV1,
)
from structural_lib.services.canonical_family import (
    CanonicalFamilyResultV1,
    FamilyIdentityV1,
    canonical_family_result,
    require_request_type,
)
from structural_lib.services.contracts.beam_continuous import (
    BeamContinuousCheckRequestV1,
    BeamSectionBarV1,
    BeamSectionCheckRequestV1,
    Identifier,
    Reference,
)
from structural_lib.services.contracts.common import StrictPublicModel

WORKFLOW = "is456.beam.instantaneous-service/v1"


class BeamInstantaneousLoadV1(StrictPublicModel):
    """One symmetric service load case applied to each declared span."""

    combination_id: Identifier
    analysis_revision: Identifier
    reinforcement_revision: Identifier
    source_reference: Reference
    uniform_load_kn_per_m: float = Field(ge=0, le=1000)
    midpoint_load_kn: float = Field(ge=0, le=2000)


class BeamInstantaneousServiceInputV1(StrictPublicModel):
    """Actual reinforcement and limits for a bounded instantaneous service check."""

    schema_version: Literal["is456-beam-instantaneous-service-input/v1"] = (
        "is456-beam-instantaneous-service-input/v1"
    )
    identity: FamilyIdentityV1
    member: Annotated[
        BeamContinuousCheckRequestV1 | BeamSectionCheckRequestV1,
        Field(discriminator="schema_version"),
    ]
    span_mm: float = Field(ge=1000, le=15000)
    service_load: BeamInstantaneousLoadV1 | None = None
    exposure: Literal["mild", "moderate", "severe", "very_severe", "extreme"]
    instantaneous_deflection_limit_mm: float | None = Field(default=None, gt=0)
    crack_width_limit_mm: float | None = Field(default=None, gt=0, le=0.3)

    @model_validator(mode="after")
    def validate_member_identity(self) -> Self:
        if self.identity.member_id != self.member.member_id:
            raise ValueError("The service and physical member identities must agree.")
        return self


def _same_faces(bars: tuple[BarPosition, ...], depth: float) -> bool:
    def pattern(face: Face) -> list[tuple[float, float]]:
        return sorted(
            (
                bar.diameter_mm,
                round(
                    (
                        bar.y_from_top_mm
                        if face is Face.TOP
                        else depth - bar.y_from_top_mm
                    ),
                    9,
                ),
            )
            for bar in bars
            if bar.face is face
        )

    return pattern(Face.TOP) == pattern(Face.BOTTOM)


def _service_domain(
    request: BeamInstantaneousServiceInputV1, bars: tuple[BarPosition, ...]
) -> StructuralIssueV1 | None:
    member, load = request.member, request.service_load
    if load is None:
        return StructuralIssueV1(
            "BEAM.SERVICE_LOAD_HELD",
            "service_load",
            "Supply the current symmetric service load case for each span.",
        )
    if (
        load.analysis_revision != member.current_analysis_revision
        or member.analysis_revision != member.current_analysis_revision
        or load.reinforcement_revision != member.reinforcement_revision
    ):
        return StructuralIssueV1(
            "BEAM.SERVICE_REVISION_STALE",
            "service_load",
            "The service load and physical member revisions must agree and be current.",
        )
    if (
        request.instantaneous_deflection_limit_mm is None
        or request.crack_width_limit_mm is None
    ):
        return StructuralIssueV1(
            "BEAM.SERVICE_LIMIT_HELD",
            "limits",
            "Declare both instantaneous deflection and flexural crack limits.",
        )
    for face in Face:
        outer = {
            bar.x_from_left_mm: bar.diameter_mm
            for bar in bars
            if bar.face is face and bar.layer == 1
        }
        if len(set(outer.values())) != 1 or any(
            bar.diameter_mm > outer.get(bar.x_from_left_mm, 0)
            for bar in bars
            if bar.face is face and bar.layer > 1
        ):
            return StructuralIssueV1(
                "BEAM.SERVICE_CRACK_GEOMETRY_HELD",
                "member.bars",
                "The crack profile needs equal outer diameters and inner bars aligned behind outer bars of equal or greater diameter.",
            )
    if isinstance(member, BeamContinuousCheckRequestV1):
        centres = [support.centre_mm for support in member.supports]
        if (
            any(
                abs(right - left - request.span_mm) > 1e-8
                for left, right in zip(centres[:-1], centres[1:], strict=True)
            )
            or not _same_faces(bars, member.depth_mm)
            or member.straight_bars is None
        ):
            return StructuralIssueV1(
                "BEAM.SERVICE_TOPOLOGY_HELD",
                "member",
                "The two-span model requires equal spans, continuous bars and mirrored reinforcement depths.",
            )
    elif member.flange is not None or request.span_mm < 4 * member.depth_mm:
        return StructuralIssueV1(
            "BEAM.SERVICE_TOPOLOGY_HELD",
            "member",
            "The simply supported model requires a solid rectangle and span at least four times the depth.",
        )
    limit = crack_width_limit(
        CrackWidthLimitRequest(
            WORKFLOW,
            ExposureClass(request.exposure),
            False,
            LimitSource.SUPPLIED,
            supplied_limit_mm=request.crack_width_limit_mm,
        )
    )
    if limit.execution is not ExecutionState.COMPLETED:
        return StructuralIssueV1(
            "BEAM.SERVICE_CRACK_LIMIT_HELD",
            "crack_width_limit_mm",
            "The supplied crack limit exceeds the exposure ceiling.",
        )
    return None


def _analyze_line(
    request: BeamInstantaneousServiceInputV1, ec: float, inertia: float
) -> OperationResult:
    member, load = request.member, request.service_load
    assert load is not None
    if isinstance(member, BeamContinuousCheckRequestV1):
        nodes = tuple(
            BeamNode(item.support_id, item.centre_mm, True, False)
            for item in member.supports
        )
    else:
        nodes = (
            BeamNode("A", 0, True, False),
            BeamNode("B", request.span_mm, True, False),
        )
    elements = tuple(
        BeamElement(
            f"SPAN-{index}",
            f"SPAN-{index}",
            left.node_id,
            right.node_id,
            ec,
            inertia,
            -load.uniform_load_kn_per_m,
        )
        for index, (left, right) in enumerate(
            zip(nodes[:-1], nodes[1:], strict=True), 1
        )
    )
    point_loads = tuple(
        BeamPointLoad(
            item.analysis_element_id, request.span_mm / 2, -1000 * load.midpoint_load_kn
        )
        for item in elements
        if load.midpoint_load_kn
    )
    return solve_beam_line(
        BeamLineRequest(
            member.member_id, load.combination_id, nodes, elements, point_loads, 100
        )
    )


def _section_state(
    request: BeamInstantaneousServiceInputV1,
    bars: tuple[BarPosition, ...],
    ec: float,
    mcr: float,
    station_id: str,
    moment: float,
) -> dict[str, Any]:
    member, load = request.member, request.service_load
    assert load is not None
    face = Face.BOTTOM if moment >= 0 else Face.TOP
    b, depth = member.width_mm, member.depth_mm
    layers = tuple(
        (
            bar.y_from_top_mm if face is Face.BOTTOM else depth - bar.y_from_top_mm,
            math.pi * bar.diameter_mm**2 / 4,
        )
        for bar in bars
    )
    axis, inertia = cracked_service_section(b, depth, layers, ec, 200000)
    tension = [
        layer for bar, layer in zip(bars, layers, strict=True) if bar.face is face
    ]
    d_eff = sum(y * area for y, area in tension) / sum(area for _, area in tension)
    curvature = abs(moment) * 1e6 / (ec * inertia)
    stress = curvature * (d_eff - axis) * 200000
    bar_response = [
        {
            "bar_id": bar.bar_id,
            "strain_compression_positive": curvature * (axis - y),
            "stress_nmm2_compression_positive": curvature * (axis - y) * 200000,
        }
        for bar, (y, _) in zip(bars, layers, strict=True)
    ]
    # With a common outer layer the furthest face point from an outer bar
    # is an edge or a midpoint of the gap between adjacent bar centres.
    outer = sorted(
        bar.x_from_left_mm for bar in bars if bar.face is face and bar.layer == 1
    )
    surface_points = [
        0.0,
        b,
        *((a + c) / 2 for a, c in zip(outer[:-1], outer[1:], strict=True)),
    ]
    crack = None
    if abs(moment) > mcr:
        checks = tuple(
            check_crack_width(
                CrackWidthCheckRequest(
                    WORKFLOW,
                    member.member_id,
                    station_id,
                    f"{load.combination_id}/{station_id}",
                    member.reinforcement_revision,
                    b,
                    depth,
                    axis,
                    face,
                    bars,
                    surface_x,
                    stress,
                    member.fy_nmm2,
                    200000,
                    curvature * (depth - axis),
                    CrackWidthLimitRequest(
                        WORKFLOW,
                        ExposureClass(request.exposure),
                        False,
                        LimitSource.SUPPLIED,
                        supplied_limit_mm=request.crack_width_limit_mm,
                    ),
                )
            )
            for surface_x in surface_points
        )
        crack = max(
            checks,
            key=lambda item: (
                item.execution is not ExecutionState.COMPLETED,
                item.outputs.get("calculated_crack_width_mm", 0),
            ),
        )
    return {
        "station_id": station_id,
        "moment_knm": moment,
        "tension_face": face.value,
        "cracking_moment_knm": mcr,
        "cracked": abs(moment) > mcr,
        "neutral_axis_mm": axis,
        "cracked_inertia_mm4": inertia,
        "bars": bar_response,
        "crack": crack.to_dict() if crack is not None else None,
    }


def check_instantaneous_service(
    request: BeamInstantaneousServiceInputV1,
) -> CanonicalFamilyResultV1[dict[str, Any]]:
    """Check elastic instantaneous deflection and flexural crack width.

    Parameters
    ----------
    request : BeamInstantaneousServiceInputV1
        Rectangular section, physical bars, service load case and limits.

    Returns
    -------
    CanonicalFamilyResultV1
        Beam-line result and signed service section states.

    Raises
    ------
    InputContractError
        The request is not a validated instantaneous service input.

    Examples
    --------
    >>> callable(check_instantaneous_service)
    True

    Limitations
    -----------
    Simply supported rectangles or two equal spans with symmetric loading
    and mirrored reinforcement depths. Long-term effects remain separate.

    Provenance
    ----------
    Euler-Bernoulli stiffness, transformed cracked section and IS 456 Annex F.
    """
    require_request_type(request, BeamInstantaneousServiceInputV1)
    member = request.member
    bars = tuple(
        BarPosition(
            bar.bar_id,
            bar.diameter_mm,
            bar.x_from_left_mm,
            bar.y_from_top_mm,
            Face(bar.face),
            bar.layer if isinstance(bar, BeamSectionBarV1) else 1,
        )
        for bar in member.bars
    )
    issue = _service_domain(request, bars)
    status = EngineeringStatus.HOLD
    data: dict[str, Any] = {"instantaneous": None, "long_term_status": "HOLD"}
    if issue is None:
        fit = evaluate_geometry(
            ReinforcementGeometryRequest(
                WORKFLOW,
                member.width_mm,
                member.depth_mm,
                member.clear_cover_mm,
                member.link_diameter_mm,
                max(member.aggregate_size_mm + 5, max(bar.diameter_mm for bar in bars)),
                bars,
            )
        )
        if fit.engineering is not EngineeringState.PASS:
            issue = StructuralIssueV1(
                "BEAM.SERVICE_GEOMETRY_HELD",
                "member.bars",
                "The supplied reinforcement does not pass the physical section geometry checks.",
            )
            data["geometry"] = fit.to_dict()
        else:
            status, issue, data["instantaneous"] = _check_response(request, bars)
    result = canonical_family_result(
        request,
        data,
        workflow_id=WORKFLOW,
        engineering_status=status,
        limitations=(
            "Uses a fully cracked flexural inertia for the instantaneous beam-line calculation.",
            "Flexural crack width uses the unmodified surface strain and gives no tension-stiffening credit.",
            "Long-term deflection, torsional and shear cracks, and complete member acceptance require separate evidence.",
        ),
        provenance=(
            "Euler-Bernoulli direct stiffness, IS 456:2000 Cl. 6.2.3.1, Cl. 6.2.2 and Annex F.",
        ),
    )
    if issue is None:
        return result
    return replace(
        result,
        envelope=replace(
            result.envelope,
            issues=(issue,),
            freshness_status=(
                FreshnessStatus.STALE
                if issue.code == "BEAM.SERVICE_REVISION_STALE"
                else FreshnessStatus.CURRENT
            ),
            calculation_status=(
                CalculationStatus.NOT_EVALUATED
                if data["instantaneous"] is None
                else CalculationStatus.COMPLETED
            ),
        ),
    )


def _critical_response(
    line: OperationResult,
    ei: float,
    udl: float,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Include extrema between output stations from the element's exact polynomials."""
    samples: list[dict[str, Any]] = line.outputs["stations"]
    extremes = list(samples)
    for left, right in zip(samples[:-1], samples[1:], strict=True):
        if left["analysis_element_id"] != right["analysis_element_id"]:
            continue
        length = right["x_mm"] - left["x_mm"]
        if length <= 0:
            continue
        rotation, moment, shear = left["rotation_rad"], left["m3_nmm"], left["v2_n"]

        def slope(
            x: float,
            rotation: float = rotation,
            moment: float = moment,
            shear: float = shear,
        ) -> float:
            return rotation + (moment * x + shear * x * x / 2 - udl * x**3 / 6) / ei

        positions = []
        if slope(0) * slope(length) < 0:
            a, b = 0.0, length
            for _ in range(45):
                mid = (a + b) / 2
                if slope(a) * slope(mid) > 0:
                    a = mid
                else:
                    b = mid
            positions.append((a + b) / 2)
        if udl > 0 and 0 < shear / udl < length:
            positions.append(shear / udl)
        for x in positions:
            extremes.append(
                {
                    **left,
                    "x_mm": left["x_mm"] + x,
                    "distance_from_start_mm": left["distance_from_start_mm"] + x,
                    "rotation_rad": slope(x),
                    "v2_n": shear - udl * x,
                    "m3_nmm": moment + shear * x - udl * x * x / 2,
                    "vertical_displacement_mm": left["vertical_displacement_mm"]
                    + rotation * x
                    + (moment * x * x / 2 + shear * x**3 / 6 - udl * x**4 / 24) / ei,
                }
            )
    return (
        max(extremes, key=lambda item: abs(item["vertical_displacement_mm"])),
        max(extremes, key=lambda item: item["m3_nmm"]),
        min(extremes, key=lambda item: item["m3_nmm"]),
    )


def _check_response(
    request: BeamInstantaneousServiceInputV1,
    bars: tuple[BarPosition, ...],
) -> tuple[EngineeringStatus, StructuralIssueV1 | None, dict[str, Any] | None]:
    member = request.member
    b, depth = member.width_mm, member.depth_mm
    ec = 5000 * math.sqrt(member.fck_nmm2)
    mcr = calculate_cracking_moment(b_mm=b, D_mm=depth, fck_nmm2=member.fck_nmm2)
    layers = tuple(
        (bar.y_from_top_mm, math.pi * bar.diameter_mm**2 / 4) for bar in bars
    )
    _, inertia = cracked_service_section(b, depth, layers, ec, 200000)
    line = _analyze_line(request, ec, inertia)
    if line.execution is not ExecutionState.COMPLETED:
        return (
            EngineeringStatus.HOLD,
            StructuralIssueV1(
                "BEAM.SERVICE_ANALYSIS_HELD",
                "service_load",
                "The declared beam-line calculation could not be resolved.",
            ),
            None,
        )
    assert request.service_load is not None
    deflection, sagging, hogging = _critical_response(
        line,
        ec * inertia,
        request.service_load.uniform_load_kn_per_m,
    )
    deflection_mm = abs(deflection["vertical_displacement_mm"])
    limit = request.instantaneous_deflection_limit_mm
    assert limit is not None
    critical = [sagging]
    if isinstance(member, BeamContinuousCheckRequestV1):
        critical.append(hogging)
    states = [
        {
            **_section_state(
                request,
                bars,
                ec,
                mcr,
                f"{item['physical_span_id']}@{item['x_mm']:g}",
                item["m3_nmm"] / 1e6,
            ),
            "x_mm": item["x_mm"],
        }
        for item in critical
    ]
    cracks = [state["crack"] for state in states if state["crack"] is not None]
    status = EngineeringStatus.PASS
    issue = None
    if deflection_mm > limit or any(item["engineering"] == "fail" for item in cracks):
        status = EngineeringStatus.FAIL
        issue = StructuralIssueV1(
            "BEAM.SERVICE_LIMIT_EXCEEDED",
            "instantaneous",
            "At least one instantaneous service limit is exceeded.",
        )
    elif any(item["engineering"] != "pass" for item in cracks):
        status = EngineeringStatus.HOLD
        issue = StructuralIssueV1(
            "BEAM.SERVICE_CRACK_HELD",
            "crack_width",
            "The service stress or reinforcement falls outside the admitted crack-width model.",
        )
    return (
        status,
        issue,
        {
            "analysis": line.to_dict(),
            "deflection_mm": deflection_mm,
            "deflection_x_mm": deflection["x_mm"],
            "deflection_limit_mm": limit,
            "crack_width_limit_mm": request.crack_width_limit_mm,
            "sections": states,
        },
    )


def render_instantaneous_service_html(
    result: CanonicalFamilyResultV1[dict[str, Any]],
) -> str:
    """Render the checked beam service result.

    Parameters
    ----------
    result : CanonicalFamilyResultV1
        Checked instantaneous service result.

    Returns
    -------
    str
        HTML with deflection, crack checks and the input identity.

    Raises
    ------
    TypeError
        The supplied result belongs to another workflow.

    Examples
    --------
    >>> callable(render_instantaneous_service_html)
    True

    Limitations
    -----------
    The report renders the supplied result without recalculation.

    Provenance
    ----------
    Uses the same load case, actual bars and input identity as the JSON result.
    """
    if (
        not isinstance(result, CanonicalFamilyResultV1)
        or result.workflow_id != WORKFLOW
    ):
        raise TypeError("result must be an instantaneous beam service result")
    identity = result.envelope.result_identity
    data = result.calculation["instantaneous"]
    body = "<p>Instantaneous calculation held.</p>"
    if data is not None:
        rows = []
        for section in data["sections"]:
            crack = section["crack"]
            width = crack["outputs"].get("calculated_crack_width_mm") if crack else 0
            width_text = f"{width:.5f}" if width is not None else "HOLD"
            rows.append(
                f"<tr><th>{html.escape(section['station_id'])}</th>"
                f"<td>{section['moment_knm']:.3f}</td><td>{section['tension_face']}</td>"
                f"<td>{section['neutral_axis_mm']:.3f}</td><td>{width_text}</td></tr>"
            )
        body = f"""<p>Instantaneous deflection {data['deflection_mm']:.4f} mm
at {data['deflection_x_mm']:.1f} mm. Limit {data['deflection_limit_mm']:.4f} mm.</p>
<table><thead><tr><th>Station</th><th>M (kN·m)</th><th>Tension face</th>
<th>Cracked neutral axis (mm)</th><th>Flexural crack width (mm)</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>"""
    issues = "".join(
        f"<li>{html.escape(issue.message)}</li>" for issue in result.issues
    )
    limits = "".join(f"<li>{html.escape(limit)}</li>" for limit in result.limitations)
    return f"""<!doctype html>
<html lang="en"><meta charset="utf-8"><title>Beam instantaneous service</title>
<h1>Beam instantaneous service · {html.escape(result.identity.case_id)}</h1>
<p>{result.engineering_status.value} · Long-term HOLD · Qualified review required</p>
<p>Input identity <code>{identity.input_hash if identity else ''}</code></p>
{body}<ul>{issues}{limits}</ul></html>"""
