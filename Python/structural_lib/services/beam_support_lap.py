"""Bounded evidence check for top steel continuous through an interior support.

This deliberately checks only the signed ULS evidence needed to credit top
steel across an interior support.  Lap placement, development and section
capacity remain the responsibility of their respective operations.
"""

from __future__ import annotations

import math
from typing import Any

from structural_lib.beam.detailing import LongitudinalBarPath, ReinforcementRole
from structural_lib.core.result_contract import StructuralIssueV1
from structural_lib.services.beam_continuous import BeamContinuousRowResultV1
from structural_lib.services.contracts.beam_continuous import (
    BeamLayeredContinuousCheckRequestV1,
)

_ZERO_MOMENT_TOLERANCE_KNM = 1e-9


def _held(message: str) -> tuple[None, StructuralIssueV1]:
    return (
        None,
        StructuralIssueV1(
            "BEAM.LAP_CONTINUITY_HELD", "negative_steel_continuity", message
        ),
    )


def check_support_lap_continuity(
    member: BeamLayeredContinuousCheckRequestV1,
    rows: tuple[BeamContinuousRowResultV1, ...],
    bars: tuple[LongitudinalBarPath, ...],
    *,
    end_tolerance_mm: float,
    depth_tolerance_mm: float,
) -> tuple[dict[str, Any] | None, StructuralIssueV1 | None]:
    """Check the limited negative-steel continuity evidence at support B.

    Every declared ULS combination must provide passing signed rows at both
    faces of B, a zero-moment station in each clear span, and positive moment
    beyond each root.  Differing roots use the outward-most roots, which is
    conservative for the required uninterrupted top bars.
    """
    if end_tolerance_mm < 0 or depth_tolerance_mm < 0:
        raise ValueError("Continuity tolerances must be non-negative.")

    uls_required = {
        combination.combination_id: set(combination.required_station_ids)
        for combination in member.combinations
        if combination.kind == "ULS"
    }
    if not uls_required:
        return _held("Declare at least one ULS combination for continuity evidence.")

    by_combination: dict[str, list[BeamContinuousRowResultV1]] = {
        identifier: [] for identifier in uls_required
    }
    for row in rows:
        if row.kind == "ULS" and row.action.combination_id in by_combination:
            by_combination[row.action.combination_id].append(row)

    left_support, support_b, right_support = member.supports
    left_face = support_b.left_face_mm
    right_face = support_b.right_face_mm
    left_clear_start = left_support.right_face_mm
    right_clear_end = right_support.left_face_mm
    roots: dict[str, tuple[float, float]] = {}
    for combination_id, combination_rows in by_combination.items():
        # Only completed, passing ULS rows are signed position evidence.
        if {row.station.station_id for row in combination_rows} != uls_required[
            combination_id
        ] or any(row.section_status != "PASS" for row in combination_rows):
            return _held(
                f"Combination {combination_id} lacks complete verified ULS row evidence."
            )
        left_faces = [
            row
            for row in combination_rows
            if math.isclose(row.station.x_mm, left_face, abs_tol=1e-9)
        ]
        right_faces = [
            row
            for row in combination_rows
            if math.isclose(row.station.x_mm, right_face, abs_tol=1e-9)
        ]
        if (
            len(left_faces) != 1
            or len(right_faces) != 1
            or left_faces[0].action.mu_knm >= 0
            or right_faces[0].action.mu_knm >= 0
        ):
            return _held(
                f"Combination {combination_id} must show negative moment at both B faces."
            )
        left_roots = [
            row.station.x_mm
            for row in combination_rows
            if left_clear_start < row.station.x_mm < left_face
            and abs(row.action.mu_knm) <= _ZERO_MOMENT_TOLERANCE_KNM
        ]
        right_roots = [
            row.station.x_mm
            for row in combination_rows
            if right_face < row.station.x_mm < right_clear_end
            and abs(row.action.mu_knm) <= _ZERO_MOMENT_TOLERANCE_KNM
        ]
        if len(left_roots) != 1 or len(right_roots) != 1:
            return _held(
                f"Combination {combination_id} must supply one zero-moment station in each clear span."
            )
        left_root, right_root = left_roots[0], right_roots[0]
        if not any(
            left_clear_start < row.station.x_mm < left_root and row.action.mu_knm > 0
            for row in combination_rows
        ) or not any(
            right_root < row.station.x_mm < right_clear_end and row.action.mu_knm > 0
            for row in combination_rows
        ):
            return _held(
                f"Combination {combination_id} lacks positive signed stations beyond both inflection roots."
            )
        roots[combination_id] = (left_root, right_root)

    # The roots should normally coincide.  When they do not, credit only the
    # outward-most roots: leftward in the first span and rightward in the second.
    left_root = min(value[0] for value in roots.values())
    right_root = max(value[1] for value in roots.values())
    top_bars = tuple(
        bar for bar in bars if bar.role is ReinforcementRole.TOP_LONGITUDINAL
    )
    support_bars_by_face = tuple(
        tuple(
            bar
            for bar in top_bars
            if bar.start_station_mm + end_tolerance_mm
            <= face
            <= bar.end_station_mm - end_tolerance_mm
        )
        for face in (left_face, right_face)
    )
    if not all(support_bars_by_face):
        return _held("Identify active top longitudinal steel at both support faces.")
    support_area = max(
        sum(bar.area_mm2 for bar in support_bars)
        for support_bars in support_bars_by_face
    )
    continuous = tuple(
        bar
        for bar in top_bars
        if bar.start_station_mm + end_tolerance_mm <= left_root
        and bar.end_station_mm - end_tolerance_mm >= right_root
    )
    continuous_area = sum(bar.area_mm2 for bar in continuous)
    area_fraction = continuous_area / support_area
    minimum_extension = (
        min(
            min(
                left_root - (bar.start_station_mm + end_tolerance_mm),
                (bar.end_station_mm - end_tolerance_mm) - right_root,
            )
            for bar in continuous
        )
        if continuous
        else 0.0
    )
    adverse_top_depth = max(
        member.depth_mm - bar.y_from_top_mm
        for support_bars in support_bars_by_face
        for bar in support_bars
    )
    required_extension = max(
        adverse_top_depth + depth_tolerance_mm,
        12 * max(bar.diameter_mm for bar in continuous or top_bars),
        max(left_face - left_clear_start, right_clear_end - right_face) / 16,
    )
    result = {
        "bar_ids": [bar.bar_id for bar in continuous],
        "area_fraction": area_fraction,
        "minimum_extension_mm": minimum_extension,
        "required_extension_mm": required_extension,
        "inflection_stations_mm": [left_root, right_root],
    }
    if area_fraction < 1 / 3 or minimum_extension < required_extension:
        return (
            result,
            StructuralIssueV1(
                "BEAM.LAP_CONTINUITY_FAIL",
                "negative_steel_continuity",
                "Continuous top steel does not satisfy the required area or extension beyond both inflection roots.",
            ),
        )
    return result, None
