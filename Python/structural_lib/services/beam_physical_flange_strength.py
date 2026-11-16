"""Bind the physical flange strength and anchorage to current supplied actions."""

from __future__ import annotations

import math
from dataclasses import replace
from typing import Any

from structural_lib.beam.detailing import (
    BarSurface,
    DevelopmentLengthRequest,
    StressState,
    development_length,
)
from structural_lib.beam.flexure import (
    FlexuralCapacityRequest,
    SectionKind,
    flexural_capacity,
)
from structural_lib.beam.reinforcement import BarPosition, Face
from structural_lib.beam.semantics import EngineeringState, OperationResult
from structural_lib.codes.is456.beam.flexure import calculate_effective_flange_width
from structural_lib.core.result_contract import StructuralIssueV1
from structural_lib.services.beam_continuous import (
    _bar_positions,
    _check_row,
    _coverage_issues,
    _governing_rows,
    _positive_support_web_capacity,
    _row_issues,
    _sections,
    _support_faces,
)
from structural_lib.services.beam_physical_flange_geometry import (
    BeamPhysicalFlangeDetailV1,
    flange_issue,
)
from structural_lib.services.contracts.beam_continuous import (
    BeamLayeredContinuousCheckRequestV1,
)


def _same(a: float, b: float) -> bool:
    return math.isclose(a, b, abs_tol=1e-6, rel_tol=0)


def bind_physical_flange_actions(
    member: BeamLayeredContinuousCheckRequestV1,
    detail: BeamPhysicalFlangeDetailV1,
) -> tuple[dict[str, Any], tuple[StructuralIssueV1, ...]]:
    """Require matched, concurrent beam and two-span strip rows."""
    strip, flange = detail.slab_strip, member.flange
    assert strip is not None and flange is not None
    if not strip.combinations:
        return {}, (
            flange_issue(
                "STRIP_ACTIONS_HELD",
                "slab_strip.combinations",
                "Supply each concurrent beam and slab ULS load row.",
            ),
        )

    stations = {row.station_id: row for row in member.stations}
    coverage, _ = _coverage_issues(member, stations, require_all_uls_stations=True)
    if coverage:
        return {}, tuple(coverage)
    left, centre, right = member.supports
    span = centre.centre_mm - left.centre_mm
    slab_left, slab_centre, slab_right = strip.transverse_support_x_mm
    slab_span = slab_centre - slab_left
    w0, wc, w1 = strip.transverse_support_widths_mm
    neighbour_cap = slab_span + (wc - (w0 + w1) / 2) / 2
    flange_physical_width = (
        member.width_mm + flange.left_overhang_mm + flange.right_overhang_mm
    )
    peak = 3 * span / 8
    if not (
        _same(right.centre_mm - centre.centre_mm, span)
        and _same(flange.zero_moment_distance_mm, 0.75 * span)
        and _same(slab_centre, member.width_mm / 2)
        and _same(wc, member.width_mm)
        and _same(slab_right - slab_centre, slab_span)
        and _same(w0, w1)
        and 0 < w0 < 2 * slab_span - wc
        and flange_physical_width <= neighbour_cap + 1e-6
        and all(
            any(_same(station.x_mm, x) for station in stations.values())
            for x in (left.centre_mm + peak, right.centre_mm - peak)
        )
    ):
        return {}, (
            flange_issue(
                "ACTION_BASIS_HELD",
                "member.stations",
                "Bind the equal spans, both positive peaks, actual adjacent widths and the signed zero-moment distance.",
            ),
        )

    loads = {row.combination_id: row for row in strip.combinations}
    if len(loads) != len(strip.combinations) or set(loads) != {
        row.combination_id for row in member.combinations if row.kind == "ULS"
    }:
        return {}, (
            flange_issue(
                "STRIP_ACTIONS_HELD",
                "slab_strip.combinations",
                "The load rows must match the declared beam ULS combinations one for one.",
            ),
        )

    for item in loads.values():
        if not _same(
            item.beam_udl_kn_per_m,
            item.other_beam_line_load_kn_per_m
            + 1.25 * slab_span / 1000 * item.slab_udl_kn_per_m2,
        ):
            return {}, (
                flange_issue(
                    "LOAD_BALANCE_HELD",
                    "slab_strip.combinations",
                    "The slab reaction and other line load must reconcile with the beam ULS load.",
                ),
            )
    for row in member.actions:
        if row.combination_id not in loads:
            continue
        station = stations[row.station_id]
        reflect = station.x_mm > centre.centre_mm or (
            station.x_mm == centre.centre_mm and station.side == "RIGHT"
        )
        s = (
            (right.centre_mm - station.x_mm)
            if reflect
            else (station.x_mm - left.centre_mm)
        ) / 1000
        q = loads[row.combination_id].beam_udl_kn_per_m
        outer_reaction = 0.375 * q * span / 1000
        m, v = outer_reaction * s - q * s**2 / 2, outer_reaction - q * s
        if (
            row.tu_knm
            or not _same(row.mu_knm, m)
            or not _same(row.vu_kn, -v if reflect else v)
        ):
            return {}, (
                flange_issue(
                    "ACTION_BASIS_HELD",
                    "member.actions",
                    f"The signed moment and shear in {row.row_id} must match the bound two-span load case.",
                ),
            )

    effective = calculate_effective_flange_width(
        bw_mm=member.width_mm,
        span_mm=flange.zero_moment_distance_mm,
        df_mm=flange.thickness_mm,
        flange_overhang_left_mm=flange.left_overhang_mm,
        flange_overhang_right_mm=flange.right_overhang_mm,
        beam_type=flange.kind,
    )
    band = min(effective, span / 10)
    return {
        "effective_width_mm": effective,
        "adjacency_cap_mm": neighbour_cap,
        "hogging_distribution_width_mm": band,
        "negative_moment_limits_mm": (
            left.centre_mm + 0.75 * span,
            right.centre_mm - 0.75 * span,
        ),
    }, ()


def check_physical_flange_anchorage(
    member: BeamLayeredContinuousCheckRequestV1,
    detail: BeamPhysicalFlangeDetailV1,
    basis: dict[str, Any],
) -> tuple[dict[str, Any], tuple[StructuralIssueV1, ...]]:
    """Check the beam-owned flange bars from both sides of the support."""
    strip, flange = detail.slab_strip, member.flange
    assert strip is not None and flange is not None
    middle = member.supports[1]
    left_zero, right_zero = basis["negative_moment_limits_mm"]
    band = basis["hogging_distribution_width_mm"]
    centre = member.width_mm / 2
    tol = detail.placement.maximum_assembly_translation_per_axis_mm
    dist = strip.distribution
    band_min, band_max = centre - band / 2, centre + band / 2
    if not (
        any(
            -flange.left_overhang_mm + dist.diameter_mm / 2 + tol <= x < band_min - tol
            for x in dist.x_axes_mm
        )
        and any(
            band_max + tol
            < x
            <= member.width_mm + flange.right_overhang_mm - dist.diameter_mm / 2 - tol
            for x in dist.x_axes_mm
        )
    ):
        return {}, (
            flange_issue(
                "OUTER_STEEL_FAIL",
                "slab_strip.distribution",
                "Retain actual nominal longitudinal slab steel on each outer portion of the flange.",
            ),
        )
    checks = []
    issues = []
    for bar in detail.flange_bars:
        available = min(
            middle.left_face_mm - bar.start_mm, bar.end_mm - middle.right_face_mm
        )
        extension = min(left_zero - bar.start_mm, bar.end_mm - right_zero)
        depth = member.depth_mm - bar.y_from_top_mm + tol
        requirement = development_length(
            DevelopmentLengthRequest(
                member.schema_version,
                bar.diameter_mm,
                0.87 * member.fy_nmm2,
                member.fy_nmm2,
                member.fck_nmm2,
                BarSurface.DEFORMED,
                StressState.TENSION,
            )
        )
        required = float(requirement.outputs["required_development_length_mm"])
        covered = (
            abs(bar.x_from_left_mm - centre) + bar.diameter_mm / 2 + tol <= band / 2
        )
        if not covered:
            issues.append(
                flange_issue(
                    "WIDTH_FAIL",
                    f"flange_bars.{bar.bar_id}",
                    "The full bar and placement allowance must remain within the hogging distribution width.",
                )
            )
        if available - tol < required or extension - tol < max(
            depth, 12 * bar.diameter_mm
        ):
            issues.append(
                flange_issue(
                    "DEVELOPMENT_FAIL",
                    f"flange_bars.{bar.bar_id}",
                    "The flange bar has inadequate development at a support face or extension past the negative-moment region.",
                )
            )
        checks.append(
            {
                "bar_id": bar.bar_id,
                "mark": bar.mark,
                "required_development_mm": required,
                "available_at_support_mm": available,
                "available_after_tolerance_mm": available - tol,
                "beyond_zero_moment_mm": extension,
                "inside_distribution_band": covered,
            }
        )
    return {"bars": checks}, tuple(issues)


def check_physical_flange_strength(
    member: BeamLayeredContinuousCheckRequestV1,
    detail: BeamPhysicalFlangeDetailV1,
) -> tuple[dict[str, Any], dict[str, Any], tuple[StructuralIssueV1, ...]]:
    """Use the slab-independent web shear and the resolved beam flange bars."""
    web = _bar_positions(member)
    outboard = tuple(
        BarPosition(
            b.bar_id, b.diameter_mm, b.x_from_left_mm, b.y_from_top_mm, Face.TOP
        )
        for b in detail.flange_bars
    )
    web_geometry, nominal_web, nominal_shear = _sections(member, web)
    tol = detail.placement.maximum_assembly_translation_per_axis_mm
    shifted = tuple(
        replace(
            b, y_from_top_mm=b.y_from_top_mm + (tol if b.face is Face.TOP else -tol)
        )
        for b in web + outboard
    )
    _, adverse_web, adverse_shear = _sections(member, shifted[: len(web)])

    def hogging(bars: tuple[BarPosition, ...]) -> OperationResult:
        return flexural_capacity(
            FlexuralCapacityRequest(
                member.schema_version,
                SectionKind.RECTANGULAR,
                member.width_mm,
                member.depth_mm,
                member.fck_nmm2,
                member.fy_nmm2,
                bars,
                Face.TOP,
            )
        )

    nominal_flexure = {**nominal_web, Face.TOP: hogging(web + outboard)}
    adverse_flexure = {**adverse_web, Face.TOP: hogging(shifted)}
    if any(
        "capacity_knm" not in res.outputs
        for res in (*nominal_flexure.values(), *adverse_flexure.values())
    ) or set(adverse_shear) != set(Face):
        return (
            {},
            {},
            (
                flange_issue(
                    "SECTION_FAIL",
                    "flange_bars",
                    "The actual beam steel does not resolve an admissible section at the placement limits.",
                ),
            ),
        )

    stations = {item.station_id: item for item in member.stations}
    faces = _support_faces(member)
    kinds = {item.combination_id: item.kind for item in member.combinations}
    end_capacity = _positive_support_web_capacity(member, shifted[: len(web)])
    # This independently bound case includes both centreline sides as
    # conservative solid-section checks alongside the physical faces.
    rows = tuple(
        _check_row(
            member,
            web,
            row,
            stations[row.station_id],
            kinds[row.combination_id],
            False,
            faces.get(stations[row.station_id].x_mm),
            adverse_flexure,
            adverse_shear,
            end_capacity,
        )
        for row in sorted(member.actions, key=lambda action: action.row_id)
    )
    failed, held = _row_issues(rows, faces, layered=True)
    if web_geometry.engineering is not EngineeringState.PASS:
        failed.extend(
            StructuralIssueV1(
                item.code, item.field_or_location or "member.bars", item.message
            )
            for item in web_geometry.diagnostics
        )
    governing = _governing_rows(rows)
    status = "FAIL" if failed else "HOLD" if held else "PASS"
    cell = {
        "rows": [row.to_dict() for row in rows],
        "governing_rows": governing,
        "flexural_sections": {
            face.value: res.to_dict() for face, res in adverse_flexure.items()
        },
        "shear_sections": {
            face.value: res.to_dict() for face, res in adverse_shear.items()
        },
        "ultimate_status": status,
        "serviceability_status": "NOT_EVALUATED",
    }
    nominal = {
        "nominal_capacity_knm": {
            face.value: float(res.outputs["capacity_knm"])
            for face, res in nominal_flexure.items()
        },
        "web_only_hogging_capacity_knm": float(
            nominal_web[Face.TOP].outputs["capacity_knm"]
        ),
        "nominal_web_shear_capacity_kn": {
            face.value: float(res.outputs["provided_capacity_kn"])
            for face, res in nominal_shear.items()
        },
        "adverse_capacity_knm": {
            face.value: float(res.outputs["capacity_knm"])
            for face, res in adverse_flexure.items()
        },
        "adverse_web_shear_capacity_kn": {
            face.value: float(res.outputs["provided_capacity_kn"])
            for face, res in adverse_shear.items()
        },
        "governing_rows": governing,
        "credited_flange_bar_ids": [b.bar_id for b in outboard],
    }
    return cell, nominal, (*failed, *held)
