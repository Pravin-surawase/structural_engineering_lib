"""Reusable reinforcement value and actual-coordinate geometry operations."""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum

from .semantics import (
    Diagnostic,
    EngineeringState,
    OperationResult,
    Provenance,
    completed_result,
    effective_inputs,
    rejected_result,
)

BAR_AREA_OPERATION = "structural.reinforcement.bar_area/v1"
MASS_PER_LENGTH_OPERATION = "structural.reinforcement.mass_per_length/v1"
EFFECTIVE_DEPTH_OPERATION = "structural.reinforcement.effective_depth/v1"
GEOMETRY_OPERATION = "structural.reinforcement_geometry.evaluate/v1"
CODE_DATA_REVISION = "is456-wp01-v1"


class Face(StrEnum):
    TOP = "top"
    BOTTOM = "bottom"


@dataclass(frozen=True)
class BarPosition:
    bar_id: str
    diameter_mm: float
    x_from_left_mm: float
    y_from_top_mm: float
    face: Face
    layer: int = 1


@dataclass(frozen=True)
class ReinforcementGeometryRequest:
    profile_id: str
    width_mm: float
    depth_mm: float
    nominal_cover_mm: float
    link_diameter_mm: float
    minimum_clear_spacing_mm: float
    bars: tuple[BarPosition, ...]
    code_data_revision_id: str = CODE_DATA_REVISION


def _provenance(method: str, revision: str = CODE_DATA_REVISION) -> Provenance:
    return Provenance(
        code_data_revision_id=revision,
        method_revision_id=method,
        source_references=("IS 456:2000 normalized WP01 rules",),
    )


def _diagnostic(
    operation: str,
    code: str,
    message: str,
    field: str,
    remediation: str,
) -> Diagnostic:
    return Diagnostic(
        code=code,
        severity="error",
        message=message,
        operation_semantic_id=operation,
        field_or_location=field,
        source="input-validation" if code.startswith("INPUT") else "geometry",
        remediation=remediation,
    )


def _positive(value: float) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(value) and value > 0


def bar_area(diameter_mm: float, *, profile_id: str = "IS456-WP01") -> OperationResult:
    inputs = effective_inputs(profile_id=profile_id, diameter_mm=diameter_mm)
    provenance = _provenance("reinforcement-bar-area-v1")
    if not _positive(diameter_mm):
        return rejected_result(
            BAR_AREA_OPERATION,
            inputs,
            (
                _diagnostic(
                    BAR_AREA_OPERATION,
                    "INPUT.RANGE",
                    "Diameter must be finite and greater than zero.",
                    "diameter_mm",
                    "Supply a positive bar diameter in mm.",
                ),
            ),
            provenance=provenance,
        )
    return completed_result(
        BAR_AREA_OPERATION,
        inputs,
        {"area_mm2": math.pi * diameter_mm**2 / 4.0},
        provenance=provenance,
    )


def mass_per_length(
    diameter_mm: float,
    density_kg_per_m3: float,
    *,
    profile_id: str = "IS456-WP01",
) -> OperationResult:
    inputs = effective_inputs(
        profile_id=profile_id,
        diameter_mm=diameter_mm,
        density_kg_per_m3=density_kg_per_m3,
    )
    provenance = _provenance("reinforcement-mass-per-length-v1")
    bad_field = None
    if not _positive(diameter_mm):
        bad_field = "diameter_mm"
    elif not _positive(density_kg_per_m3):
        bad_field = "density_kg_per_m3"
    if bad_field:
        return rejected_result(
            MASS_PER_LENGTH_OPERATION,
            inputs,
            (
                _diagnostic(
                    MASS_PER_LENGTH_OPERATION,
                    "INPUT.RANGE",
                    f"{bad_field} must be finite and greater than zero.",
                    bad_field,
                    "Supply the required positive value in its declared unit.",
                ),
            ),
            provenance=provenance,
        )
    area_mm2 = math.pi * diameter_mm**2 / 4.0
    return completed_result(
        MASS_PER_LENGTH_OPERATION,
        inputs,
        {"mass_kg_per_m": area_mm2 * density_kg_per_m3 / 1_000_000.0},
        provenance=provenance,
    )


def _request_inputs(
    request: ReinforcementGeometryRequest,
) -> dict[str, dict[str, object]]:
    return effective_inputs(
        profile_id=request.profile_id,
        width_mm=request.width_mm,
        depth_mm=request.depth_mm,
        nominal_cover_mm=request.nominal_cover_mm,
        link_diameter_mm=request.link_diameter_mm,
        minimum_clear_spacing_mm=request.minimum_clear_spacing_mm,
        bars=request.bars,
        code_data_revision_id=request.code_data_revision_id,
    )


def _validate_geometry(
    operation: str,
    request: ReinforcementGeometryRequest,
) -> tuple[dict[str, dict[str, object]], Provenance, list[Diagnostic]]:
    inputs = _request_inputs(request)
    provenance = _provenance(
        "reinforcement-actual-geometry-v1", request.code_data_revision_id
    )
    diagnostics: list[Diagnostic] = []
    for field, value, allow_zero in (
        ("width_mm", request.width_mm, False),
        ("depth_mm", request.depth_mm, False),
        ("nominal_cover_mm", request.nominal_cover_mm, True),
        ("link_diameter_mm", request.link_diameter_mm, True),
        ("minimum_clear_spacing_mm", request.minimum_clear_spacing_mm, True),
    ):
        valid = isinstance(value, (int, float)) and math.isfinite(value)
        valid = valid and (value >= 0 if allow_zero else value > 0)
        if not valid:
            diagnostics.append(
                _diagnostic(
                    operation,
                    "INPUT.RANGE",
                    f"{field} is outside its finite range.",
                    field,
                    "Supply a value in mm within the declared range.",
                )
            )
    if not request.bars:
        diagnostics.append(
            _diagnostic(
                operation,
                "INPUT.REQUIRED",
                "At least one actual bar coordinate is required.",
                "bars",
                "Supply resolved physical bars.",
            )
        )
    ids: set[str] = set()
    for index, bar in enumerate(request.bars):
        location = f"bars[{index}]"
        if not bar.bar_id.strip():
            diagnostics.append(
                _diagnostic(
                    operation,
                    "INPUT.REQUIRED",
                    "Every bar requires an identifier.",
                    f"{location}.bar_id",
                    "Supply a unique non-blank bar identifier.",
                )
            )
        elif bar.bar_id in ids:
            diagnostics.append(
                _diagnostic(
                    operation,
                    "INPUT.CONFLICT",
                    "Bar identifiers must be unique.",
                    f"{location}.bar_id",
                    "Assign a unique identifier to every physical bar.",
                )
            )
        ids.add(bar.bar_id)
        if not _positive(bar.diameter_mm):
            diagnostics.append(
                _diagnostic(
                    operation,
                    "INPUT.RANGE",
                    "Bar diameter must be finite and positive.",
                    f"{location}.diameter_mm",
                    "Supply a positive diameter in mm.",
                )
            )
        if not math.isfinite(bar.x_from_left_mm) or not math.isfinite(
            bar.y_from_top_mm
        ):
            diagnostics.append(
                _diagnostic(
                    operation,
                    "INPUT.NON_FINITE",
                    "Bar coordinates must be finite.",
                    location,
                    "Resolve both physical coordinates in mm.",
                )
            )
        if bar.layer < 1:
            diagnostics.append(
                _diagnostic(
                    operation,
                    "INPUT.RANGE",
                    "Bar layer numbers start at one.",
                    f"{location}.layer",
                    "Supply a positive layer number.",
                )
            )
    return inputs, provenance, diagnostics


def _face_output(
    depth_mm: float, face: Face, bars: Iterable[BarPosition]
) -> dict[str, object]:
    group = tuple(bars)
    areas = tuple(math.pi * bar.diameter_mm**2 / 4.0 for bar in group)
    area = sum(areas)
    x = sum(a * bar.x_from_left_mm for a, bar in zip(areas, group, strict=True)) / area
    y = sum(a * bar.y_from_top_mm for a, bar in zip(areas, group, strict=True)) / area
    effective_depth_mm = y if face is Face.BOTTOM else depth_mm - y
    return {
        "face": face,
        "area_mm2": area,
        "centroid_x_from_left_mm": x,
        "centroid_y_from_top_mm": y,
        "effective_depth_mm": effective_depth_mm,
        "bar_ids": tuple(bar.bar_id for bar in group),
    }


def effective_depth(
    request: ReinforcementGeometryRequest,
    tension_face: Face,
) -> OperationResult:
    inputs, provenance, diagnostics = _validate_geometry(
        EFFECTIVE_DEPTH_OPERATION, request
    )
    inputs = dict(inputs)
    inputs["tension_face"] = effective_inputs(tension_face=tension_face)[
        "tension_face"
    ]
    if diagnostics:
        return rejected_result(
            EFFECTIVE_DEPTH_OPERATION, inputs, diagnostics, provenance=provenance
        )
    bars = tuple(bar for bar in request.bars if bar.face is tension_face)
    if not bars:
        return rejected_result(
            EFFECTIVE_DEPTH_OPERATION,
            inputs,
            (
                _diagnostic(
                    EFFECTIVE_DEPTH_OPERATION,
                    "AXIS.UNRESOLVED",
                    "No bars are assigned to the requested physical tension face.",
                    "tension_face",
                    "Resolve physical faces before calculating effective depth.",
                ),
            ),
            provenance=provenance,
        )
    return completed_result(
        EFFECTIVE_DEPTH_OPERATION,
        inputs,
        _face_output(request.depth_mm, tension_face, bars),
        provenance=provenance,
    )


def evaluate_geometry(request: ReinforcementGeometryRequest) -> OperationResult:
    inputs, provenance, diagnostics = _validate_geometry(GEOMETRY_OPERATION, request)
    if diagnostics:
        return rejected_result(
            GEOMETRY_OPERATION, inputs, diagnostics, provenance=provenance
        )
    checks: list[Diagnostic] = []
    inset = request.nominal_cover_mm + request.link_diameter_mm
    for index, bar in enumerate(request.bars):
        radius = bar.diameter_mm / 2.0
        if (
            bar.x_from_left_mm - radius < inset
            or bar.x_from_left_mm + radius > request.width_mm - inset
            or bar.y_from_top_mm - radius < inset
            or bar.y_from_top_mm + radius > request.depth_mm - inset
        ):
            checks.append(
                _diagnostic(
                    GEOMETRY_OPERATION,
                    "GEOMETRY.COVER",
                    "Bar crosses the clear rectangle inside nominal cover and links.",
                    f"bars[{index}]",
                    "Move the bar or revise the section, cover, link, or diameter.",
                )
            )
    minimum_gap: float | None = None
    governing_pair: tuple[str, str] | None = None
    for index, bar in enumerate(request.bars):
        for other in request.bars[:index]:
            if bar.face is not other.face:
                continue
            distance = math.hypot(
                bar.x_from_left_mm - other.x_from_left_mm,
                bar.y_from_top_mm - other.y_from_top_mm,
            )
            gap = distance - (bar.diameter_mm + other.diameter_mm) / 2.0
            if minimum_gap is None or gap < minimum_gap:
                minimum_gap = gap
                governing_pair = (other.bar_id, bar.bar_id)
            if gap < request.minimum_clear_spacing_mm:
                checks.append(
                    _diagnostic(
                        GEOMETRY_OPERATION,
                        "GEOMETRY.SPACING",
                        "Clear spacing is below the declared minimum.",
                        f"bars[{other.bar_id},{bar.bar_id}]",
                        "Increase the bar separation or revise the arrangement.",
                    )
                )
    groups = {
        face.value: _face_output(
            request.depth_mm,
            face,
            (bar for bar in request.bars if bar.face is face),
        )
        for face in Face
        if any(bar.face is face for bar in request.bars)
    }
    return completed_result(
        GEOMETRY_OPERATION,
        inputs,
        {
            "faces": groups,
            "minimum_clear_spacing_mm": minimum_gap,
            "governing_spacing_pair": governing_pair,
            "bar_count": len(request.bars),
        },
        engineering=EngineeringState.FAIL if checks else EngineeringState.PASS,
        diagnostics=checks,
        provenance=provenance,
    )


__all__ = [
    "BAR_AREA_OPERATION",
    "CODE_DATA_REVISION",
    "EFFECTIVE_DEPTH_OPERATION",
    "GEOMETRY_OPERATION",
    "MASS_PER_LENGTH_OPERATION",
    "BarPosition",
    "Face",
    "ReinforcementGeometryRequest",
    "bar_area",
    "effective_depth",
    "evaluate_geometry",
    "mass_per_length",
]
