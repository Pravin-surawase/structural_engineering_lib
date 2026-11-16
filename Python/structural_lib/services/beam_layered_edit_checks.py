"""Strength, development and instantaneous service evidence for the placed cage."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

from pydantic import Field

from structural_lib.beam.analysis import (
    BeamElement,
    BeamLineRequest,
    BeamNode,
    solve_beam_line,
)
from structural_lib.beam.detailing import (
    BarSurface,
    DevelopmentLengthRequest,
    StressState,
    development_length,
)
from structural_lib.beam.reinforcement import Face
from structural_lib.beam.semantics import ExecutionState
from structural_lib.codes.is456.beam.serviceability import (
    calculate_cracking_moment,
    calculate_gross_moment_of_inertia,
)
from structural_lib.core.result_contract import EngineeringStatus, StructuralIssueV1
from structural_lib.services.beam_continuous import (
    BeamContinuousCheckResultV1,
    check_continuous_beam,
)
from structural_lib.services.beam_instantaneous_service import _critical_response
from structural_lib.services.contracts.beam_continuous import (
    BeamLayeredContinuousCheckRequestV1,
    Reference,
)
from structural_lib.services.contracts.common import StrictPublicModel

if TYPE_CHECKING:
    from structural_lib.services.beam_layered_edit_placement import (
        BeamLayeredCagePlacementV1,
    )


class BeamLayeredEditServiceV1(StrictPublicModel):
    """One symmetric gravity service UDL on an uncracked, simply ended two-span member."""

    uniform_load_kn_per_m: float = Field(gt=0, le=1000)
    analysis_revision: Reference
    source_reference: Reference


def _governing_flexure(checked: BeamContinuousCheckResultV1) -> str | None:
    # Keep support centreline demand as a diagnostic envelope as well as the
    # normal face-based acceptance rows already recorded by the beam checker.
    choices = [
        (row.flexure_utilization, row.action.row_id)
        for row in checked.rows
        if row.kind == "ULS" and row.flexure_utilization is not None
    ]
    return min(choices, key=lambda item: (-item[0], item[1]))[1] if choices else None


def _check_placed_sections(
    member: BeamLayeredContinuousCheckRequestV1, axis_shift: float, maximum_pitch: float
) -> tuple[list[dict[str, Any]], EngineeringStatus]:
    evidence = []
    statuses = set()
    for shift in (-axis_shift, axis_shift):
        bars = tuple(
            bar.model_copy(update={"y_from_top_mm": bar.y_from_top_mm + shift})
            for bar in member.bars
        )
        checked = check_continuous_beam(
            member.model_copy(update={"bars": bars, "link_spacing_mm": maximum_pitch})
        )
        status = EngineeringStatus(checked.ultimate_status)
        statuses.add(status)
        record: dict[str, Any] = {
            "common_vertical_axis_shift_mm": shift,
            "outer_link_pitch_mm": maximum_pitch,
            "governing_flexure_row_id": _governing_flexure(checked),
            "governing_acceptance_shear_row_id": checked.governing_rows.get("shear"),
            "status": status.value,
        }
        if status is EngineeringStatus.PASS:
            record["face_checks"] = {
                face.value: {
                    "effective_depth_mm": checked.flexural_sections[face].outputs[
                        "effective_depth_mm"
                    ],
                    "capacity_knm": checked.flexural_sections[face].outputs[
                        "capacity_knm"
                    ],
                    "shear_capacity_kn": checked.shear_sections[face].outputs[
                        "provided_capacity_kn"
                    ],
                }
                for face in (Face.TOP, Face.BOTTOM)
            }
        else:
            record["issues"] = [
                item.to_dict() for item in checked.result_envelope.issues
            ]
        evidence.append(record)
    status = next(
        (
            candidate
            for candidate in (EngineeringStatus.FAIL, EngineeringStatus.HOLD)
            if candidate in statuses
        ),
        EngineeringStatus.PASS,
    )
    return evidence, status


def _check_end_placement(
    member: BeamLayeredContinuousCheckRequestV1,
    placement: BeamLayeredCagePlacementV1,
) -> tuple[dict[str, Any], EngineeringStatus, StructuralIssueV1 | None]:
    assert member.straight_bars is not None
    left, _, right = member.supports
    path = member.straight_bars
    extension = min(
        left.right_face_mm - path.start_mm, path.end_mm - right.left_face_mm
    )
    cover = min(path.start_mm - left.left_face_mm, right.right_face_mm - path.end_mm)
    worst_extension = extension - placement.bar_end_tolerance_mm
    worst_cover = cover - placement.bar_end_tolerance_mm
    output: dict[str, Any] = {
        "nominal_left_and_right_development_available_mm": extension,
        "worst_development_available_mm": worst_extension,
        "minimum_end_cover_mm": worst_cover,
        "required_by_bar_id_mm": {},
    }
    for bar in member.bars:
        bond = development_length(
            DevelopmentLengthRequest(
                member.schema_version,
                bar.diameter_mm + placement.bar_diameter_allowance_mm,
                0.87 * member.fy_nmm2,
                member.fy_nmm2,
                member.fck_nmm2,
                BarSurface.DEFORMED,
                StressState.TENSION,
            )
        )
        if bond.execution is not ExecutionState.COMPLETED:
            return (
                output,
                EngineeringStatus.HOLD,
                StructuralIssueV1(
                    "BEAM.EDIT_DEVELOPMENT_BASIS_HELD",
                    "member.straight_bars",
                    "Supply the bond basis for the bars under the stated end placement tolerance.",
                ),
            )
        output["required_by_bar_id_mm"][bar.bar_id] = bond.outputs[
            "required_development_length_mm"
        ]
    if (
        worst_extension < max(output["required_by_bar_id_mm"].values())
        or worst_cover < placement.required_cover_mm
    ):
        return (
            output,
            EngineeringStatus.FAIL,
            StructuralIssueV1(
                "BEAM.EDIT_DEVELOPMENT_FAIL",
                "member.straight_bars",
                "The placed bar ends cannot maintain both cover and full tension development.",
            ),
        )
    return output, EngineeringStatus.PASS, None


def _instantaneous_service(
    member: BeamLayeredContinuousCheckRequestV1,
    service: BeamLayeredEditServiceV1 | None,
    sagging_depth: float,
) -> dict[str, Any] | None:
    left, centre, right = member.supports
    span = centre.centre_mm - left.centre_mm
    if (
        service is None
        or service.analysis_revision != member.analysis_revision
        or not math.isclose(
            span, right.centre_mm - centre.centre_mm, rel_tol=0, abs_tol=1e-6
        )
    ):
        return None
    q = service.uniform_load_kn_per_m
    ec = 5000 * math.sqrt(member.fck_nmm2)
    inertia = calculate_gross_moment_of_inertia(
        b_mm=member.width_mm, D_mm=member.depth_mm
    )
    cracking_moment = calculate_cracking_moment(
        b_mm=member.width_mm, D_mm=member.depth_mm, fck_nmm2=member.fck_nmm2
    )
    nodes = tuple(
        BeamNode(support.support_id, support.centre_mm, True, False)
        for support in member.supports
    )
    elements = tuple(
        BeamElement(
            f"SPAN-{index}", f"SPAN-{index}", a.node_id, b.node_id, ec, inertia, -q
        )
        for index, (a, b) in enumerate(zip(nodes[:-1], nodes[1:], strict=True), start=1)
    )
    line = solve_beam_line(
        BeamLineRequest(
            member.member_id, service.analysis_revision, nodes, elements, (), 100
        )
    )
    if line.execution is not ExecutionState.COMPLETED:
        return None
    peak, sagging, hogging = _critical_response(line, ec * inertia, q)
    moment = max(abs(sagging["m3_nmm"]), abs(hogging["m3_nmm"])) / 1e6
    data: dict[str, Any] = {
        "unfactored_udl_kn_per_m_per_span": q,
        "source_reference": service.source_reference,
        "analysis_revision": member.analysis_revision,
        "reinforcement_revision": member.reinforcement_revision,
        "sagging_effective_depth_mm": sagging_depth,
        "effective_span_to_depth": span / sagging_depth,
        "maximum_moment_magnitude_knm": moment,
        "cracking_moment_knm": cracking_moment,
        "status": "PASS" if moment <= cracking_moment else "HOLD",
    }
    if moment <= cracking_moment:
        x = peak["x_mm"]
        data.update(
            flexural_crack_width_mm=0.0,
            maximum_instantaneous_deflection_mm=abs(peak["vertical_displacement_mm"]),
            controlling_station_x_mm=sorted((x, left.centre_mm + right.centre_mm - x)),
        )
    return data


def check_layered_edit_actions(
    member: BeamLayeredContinuousCheckRequestV1,
    checked: BeamContinuousCheckResultV1,
    placement: BeamLayeredCagePlacementV1,
    maximum_pitch: float,
    service: BeamLayeredEditServiceV1 | None,
) -> tuple[dict[str, Any], EngineeringStatus, StructuralIssueV1 | None]:
    """Check the placement extremes, both support ends and the supplied service UDL."""
    checks: dict[str, Any] = {
        "governing_flexure_row_id": _governing_flexure(checked),
        "governing_acceptance_shear_row_id": checked.governing_rows.get("shear"),
    }
    end, status, issue = _check_end_placement(member, placement)
    checks["end_anchorage"] = end
    if issue is not None:
        return checks, status, issue
    vertical_tolerance = (
        placement.cage_location_tolerance_mm + placement.bar_axis_tolerance_mm
    )
    extremes, status = _check_placed_sections(member, vertical_tolerance, maximum_pitch)
    checks["placement_limit_section_rechecks"] = extremes
    if status is not EngineeringStatus.PASS:
        return (
            checks,
            status,
            StructuralIssueV1(
                "BEAM.EDIT_PLACED_SECTION_CHECK",
                "layered_cage.placement",
                "The signed section checks require a passing result at both vertical placement limits and maximum link pitch.",
            ),
        )
    depth = checked.flexural_sections[Face.BOTTOM].outputs["effective_depth_mm"]
    checks["service"] = response = _instantaneous_service(member, service, depth)
    if response is None or response["status"] != "PASS":
        return (
            checks,
            EngineeringStatus.HOLD,
            StructuralIssueV1(
                "BEAM.EDIT_SERVICE_HELD",
                "layered_cage.service",
                "The supplied service load must resolve to an uncracked response on the current equal-span member.",
            ),
        )
    return checks, EngineeringStatus.PASS, None
