"""IS 456 WP01 flexural capacity and supplied-member check operations."""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from enum import StrEnum

from structural_lib.codes.is456.materials import get_steel_stress, get_xu_max_d

from .reinforcement import BarPosition, Face
from .semantics import (
    ApplicabilityState,
    Diagnostic,
    EngineeringState,
    ExecutionState,
    OperationResult,
    Provenance,
    completed_result,
    effective_inputs,
    not_applicable_result,
    rejected_result,
)

FLEXURAL_CAPACITY_OPERATION = "is456.beam.flexural_capacity/v1"
FLEXURE_CHECK_OPERATION = "is456.beam.flexure.check/v1"
CODE_DATA_REVISION = "is456-wp01-v1"


class SectionKind(StrEnum):
    RECTANGULAR = "rectangular"
    T_BEAM = "t_beam"
    L_BEAM = "l_beam"


@dataclass(frozen=True)
class FlexuralCapacityRequest:
    profile_id: str
    section_kind: SectionKind
    web_width_mm: float
    depth_mm: float
    concrete_strength_n_per_mm2: float
    steel_yield_strength_n_per_mm2: float
    bars: tuple[BarPosition, ...]
    tension_face: Face
    flange_width_mm: float | None = None
    flange_thickness_mm: float | None = None
    axial_force_kn: float = 0.0
    code_data_revision_id: str = CODE_DATA_REVISION


@dataclass(frozen=True)
class FlexureCheckRequest:
    capacity: FlexuralCapacityRequest
    positive_design_moment_knm: float | None = None
    negative_design_moment_knm: float | None = None


def _provenance(revision: str, method: str) -> Provenance:
    return Provenance(
        revision,
        method,
        ("IS 456:2000 normalized WP01 flexure rules",),
    )


def _diagnostic(
    operation: str,
    code: str,
    message: str,
    field: str,
    remediation: str,
    *,
    severity: str = "error",
) -> Diagnostic:
    return Diagnostic(
        code,
        severity,
        message,
        operation,
        field,
        "is456-flexure",
        remediation,
    )


def _inputs(request: FlexuralCapacityRequest) -> dict[str, dict[str, object]]:
    return effective_inputs(
        profile_id=request.profile_id,
        section_kind=request.section_kind,
        web_width_mm=request.web_width_mm,
        depth_mm=request.depth_mm,
        concrete_strength_n_per_mm2=request.concrete_strength_n_per_mm2,
        steel_yield_strength_n_per_mm2=request.steel_yield_strength_n_per_mm2,
        bars=request.bars,
        tension_face=request.tension_face,
        flange_width_mm=request.flange_width_mm,
        flange_thickness_mm=request.flange_thickness_mm,
        axial_force_kn=request.axial_force_kn,
        code_data_revision_id=request.code_data_revision_id,
    )


def _bar_area(bar: BarPosition) -> float:
    return math.pi * bar.diameter_mm**2 / 4.0


def _depth_from_compression_face(
    depth_mm: float,
    tension_face: Face,
    bars: tuple[BarPosition, ...],
) -> float:
    area = sum(_bar_area(bar) for bar in bars)
    y_from_top = sum(_bar_area(bar) * bar.y_from_top_mm for bar in bars) / area
    return y_from_top if tension_face is Face.BOTTOM else depth_mm - y_from_top


def _concrete_block(
    request: FlexuralCapacityRequest,
    x_mm: float,
    d_mm: float,
) -> tuple[float, float, bool]:
    """Return concrete compression force N, moment Nmm, flange-used state."""

    fck = request.concrete_strength_n_per_mm2
    bw = request.web_width_mm
    compression_at_top = request.tension_face is Face.BOTTOM
    flanged = request.section_kind is not SectionKind.RECTANGULAR and compression_at_top
    if not flanged:
        force = 0.36 * fck * bw * x_mm
        return force, force * (d_mm - 0.42 * x_mm), False
    bf = request.flange_width_mm or 0.0
    df = request.flange_thickness_mm or 0.0
    if x_mm <= df:
        force = 0.36 * fck * bf * x_mm
        return force, force * (d_mm - 0.42 * x_mm), True
    yf = min(df, 0.15 * x_mm + 0.65 * df)
    web_force = 0.36 * fck * bw * x_mm
    flange_force = 0.45 * fck * (bf - bw) * yf
    moment = web_force * (d_mm - 0.42 * x_mm) + flange_force * (d_mm - 0.5 * yf)
    return web_force + flange_force, moment, True


def _compression_steel(
    request: FlexuralCapacityRequest,
    x_mm: float,
    d_mm: float,
    d_prime_mm: float | None,
    area_mm2: float,
) -> tuple[float, float]:
    if d_prime_mm is None or area_mm2 <= 0 or x_mm <= d_prime_mm:
        return 0.0, 0.0
    strain = 0.0035 * (x_mm - d_prime_mm) / x_mm
    steel_stress = get_steel_stress(strain, request.steel_yield_strength_n_per_mm2)
    displaced_concrete_stress = 0.446 * request.concrete_strength_n_per_mm2
    net_stress = max(0.0, steel_stress - displaced_concrete_stress)
    force = net_stress * area_mm2
    return force, force * (d_mm - d_prime_mm)


def flexural_capacity(request: FlexuralCapacityRequest) -> OperationResult:
    inputs = _inputs(request)
    provenance = _provenance(
        request.code_data_revision_id, "is456-flexural-capacity-wp01-v1"
    )
    numeric = {
        "web_width_mm": request.web_width_mm,
        "depth_mm": request.depth_mm,
        "concrete_strength_n_per_mm2": request.concrete_strength_n_per_mm2,
        "steel_yield_strength_n_per_mm2": request.steel_yield_strength_n_per_mm2,
    }
    bad = next(
        (
            field
            for field, value in numeric.items()
            if not math.isfinite(value) or value <= 0
        ),
        None,
    )
    if bad or not request.bars:
        field = bad or "bars"
        return rejected_result(
            FLEXURAL_CAPACITY_OPERATION,
            inputs,
            (
                _diagnostic(
                    FLEXURAL_CAPACITY_OPERATION,
                    "INPUT.REQUIRED" if not request.bars else "INPUT.RANGE",
                    "Section, materials, and actual reinforcement must be finite and positive.",
                    field,
                    "Supply the complete supported capacity request.",
                ),
            ),
            provenance=provenance,
        )
    if not math.isfinite(request.axial_force_kn):
        return rejected_result(
            FLEXURAL_CAPACITY_OPERATION,
            inputs,
            (
                _diagnostic(
                    FLEXURAL_CAPACITY_OPERATION,
                    "INPUT.NON_FINITE",
                    "Axial force must be finite.",
                    "axial_force_kn",
                    "Supply a finite axial force.",
                ),
            ),
            provenance=provenance,
        )
    if abs(request.axial_force_kn) > 1e-12:
        return not_applicable_result(
            FLEXURAL_CAPACITY_OPERATION,
            inputs,
            _diagnostic(
                FLEXURAL_CAPACITY_OPERATION,
                "PROFILE.UNSUPPORTED",
                "The WP01 flexure profile excludes axial-force interaction.",
                "axial_force_kn",
                "Use a profile that implements axial-flexural interaction.",
                severity="information",
            ),
            provenance=provenance,
        )
    if request.section_kind is not SectionKind.RECTANGULAR:
        bf = request.flange_width_mm
        df = request.flange_thickness_mm
        if (
            bf is None
            or df is None
            or not math.isfinite(bf)
            or not math.isfinite(df)
            or bf < request.web_width_mm
            or not 0 < df < request.depth_mm
        ):
            return rejected_result(
                FLEXURAL_CAPACITY_OPERATION,
                inputs,
                (
                    _diagnostic(
                        FLEXURAL_CAPACITY_OPERATION,
                        "INPUT.RANGE",
                        "A flanged section requires an eligible flange width and thickness.",
                        "flange_width_mm",
                        "Supply bf >= bw and 0 < Df < D.",
                    ),
                ),
                provenance=provenance,
            )
    fy = request.steel_yield_strength_n_per_mm2
    if fy < 250 or fy > 550:
        return not_applicable_result(
            FLEXURAL_CAPACITY_OPERATION,
            inputs,
            _diagnostic(
                FLEXURAL_CAPACITY_OPERATION,
                "PROFILE.UNSUPPORTED",
                "Steel grade is outside the WP01 IS 456 material domain.",
                "steel_yield_strength_n_per_mm2",
                "Use a supported 250-550 N/mm2 grade or another profile.",
                severity="information",
            ),
            provenance=provenance,
        )
    invalid_bar = next(
        (
            bar
            for bar in request.bars
            if not bar.bar_id.strip()
            or not math.isfinite(bar.diameter_mm)
            or bar.diameter_mm <= 0
            or not math.isfinite(bar.y_from_top_mm)
        ),
        None,
    )
    if invalid_bar:
        return rejected_result(
            FLEXURAL_CAPACITY_OPERATION,
            inputs,
            (
                _diagnostic(
                    FLEXURAL_CAPACITY_OPERATION,
                    "INPUT.RANGE",
                    "Every bar requires a positive diameter and finite coordinate.",
                    f"bars[{invalid_bar.bar_id}]",
                    "Resolve the actual physical bar geometry.",
                ),
            ),
            provenance=provenance,
        )
    tension = tuple(bar for bar in request.bars if bar.face is request.tension_face)
    compression_face = Face.TOP if request.tension_face is Face.BOTTOM else Face.BOTTOM
    compression = tuple(bar for bar in request.bars if bar.face is compression_face)
    if not tension:
        return rejected_result(
            FLEXURAL_CAPACITY_OPERATION,
            inputs,
            (
                _diagnostic(
                    FLEXURAL_CAPACITY_OPERATION,
                    "AXIS.UNRESOLVED",
                    "The requested tension face has no actual bars.",
                    "tension_face",
                    "Assign bars to the physical tension face.",
                ),
            ),
            provenance=provenance,
        )
    ast = sum(_bar_area(bar) for bar in tension)
    asc = sum(_bar_area(bar) for bar in compression)
    d_mm = _depth_from_compression_face(request.depth_mm, request.tension_face, tension)
    d_prime_mm = (
        _depth_from_compression_face(
            request.depth_mm, request.tension_face, compression
        )
        if compression
        else None
    )
    if (
        d_mm <= 0
        or d_mm >= request.depth_mm
        or (d_prime_mm is not None and d_prime_mm >= d_mm)
    ):
        return rejected_result(
            FLEXURAL_CAPACITY_OPERATION,
            inputs,
            (
                _diagnostic(
                    FLEXURAL_CAPACITY_OPERATION,
                    "AXIS.UNRESOLVED",
                    "Bar coordinates do not resolve valid tension and compression depths.",
                    "bars",
                    "Correct the physical face and y-coordinate assignments.",
                ),
            ),
            provenance=provenance,
        )
    tension_force = 0.87 * fy * ast

    def residual(x_mm: float) -> float:
        concrete_force, _, _ = _concrete_block(request, x_mm, d_mm)
        steel_force, _ = _compression_steel(request, x_mm, d_mm, d_prime_mm, asc)
        return concrete_force + steel_force - tension_force

    low = 1e-9
    high = request.depth_mm
    if residual(high) < 0:
        return not_applicable_result(
            FLEXURAL_CAPACITY_OPERATION,
            inputs,
            _diagnostic(
                FLEXURAL_CAPACITY_OPERATION,
                "PROFILE.UNSUPPORTED",
                "Supplied tension force cannot equilibrate inside the supported section depth.",
                "bars",
                "Revise the arrangement or use a fuller strain-compatibility profile.",
                severity="information",
            ),
            provenance=provenance,
        )
    for _ in range(100):
        mid = (low + high) / 2.0
        if residual(mid) >= 0:
            high = mid
        else:
            low = mid
    equilibrium_x = (low + high) / 2.0
    xu_max = get_xu_max_d(fy) * d_mm
    over_reinforced = equilibrium_x > xu_max + 1e-8
    used_x = min(equilibrium_x, xu_max)
    concrete_force, concrete_moment, uses_flange = _concrete_block(
        request, used_x, d_mm
    )
    compression_force, compression_moment = _compression_steel(
        request, used_x, d_mm, d_prime_mm, asc
    )
    capacity_knm = (concrete_moment + compression_moment) / 1_000_000.0
    max_area = 0.04 * request.web_width_mm * request.depth_mm
    min_area = 0.85 * request.web_width_mm * d_mm / fy
    diagnostics: list[Diagnostic] = []
    if over_reinforced:
        diagnostics.append(
            _diagnostic(
                FLEXURAL_CAPACITY_OPERATION,
                "FLEXURE.OVER_REINFORCED",
                "The equilibrium neutral axis exceeds the limiting depth.",
                "bars",
                "Revise the supplied longitudinal reinforcement or section.",
            )
        )
    return completed_result(
        FLEXURAL_CAPACITY_OPERATION,
        inputs,
        {
            "tension_face": request.tension_face,
            "capacity_knm": capacity_knm,
            "equilibrium_neutral_axis_depth_mm": equilibrium_x,
            "limiting_neutral_axis_depth_mm": xu_max,
            "capacity_neutral_axis_depth_mm": used_x,
            "effective_depth_mm": d_mm,
            "compression_steel_depth_mm": d_prime_mm,
            "tension_steel_area_mm2": ast,
            "compression_steel_area_mm2": asc,
            "minimum_tension_steel_area_mm2": min_area,
            "maximum_total_steel_area_mm2": max_area,
            "concrete_compression_force_n": concrete_force,
            "compression_steel_force_n": compression_force,
            "over_reinforced": over_reinforced,
            "uses_compression_flange": uses_flange,
        },
        engineering=EngineeringState.FAIL if over_reinforced else EngineeringState.PASS,
        diagnostics=diagnostics,
        provenance=provenance,
    )


def check_flexure(request: FlexureCheckRequest) -> OperationResult:
    base = request.capacity
    operation_inputs = effective_inputs(
        capacity_request=base,
        positive_design_moment_knm=request.positive_design_moment_knm,
        negative_design_moment_knm=request.negative_design_moment_knm,
    )
    provenance = _provenance(base.code_data_revision_id, "is456-flexure-check-wp01-v1")
    demands: list[tuple[str, Face, float]] = []
    if request.positive_design_moment_knm is not None:
        value = request.positive_design_moment_knm
        if not math.isfinite(value) or value < 0:
            return rejected_result(
                FLEXURE_CHECK_OPERATION,
                operation_inputs,
                (
                    _diagnostic(
                        FLEXURE_CHECK_OPERATION,
                        "INPUT.RANGE",
                        "Positive design moment must be finite and nonnegative.",
                        "positive_design_moment_knm",
                        "Supply the positive-moment magnitude in kNm.",
                    ),
                ),
                provenance=provenance,
            )
        demands.append(("positive", Face.BOTTOM, value))
    if request.negative_design_moment_knm is not None:
        value = request.negative_design_moment_knm
        if not math.isfinite(value) or value > 0:
            return rejected_result(
                FLEXURE_CHECK_OPERATION,
                operation_inputs,
                (
                    _diagnostic(
                        FLEXURE_CHECK_OPERATION,
                        "INPUT.RANGE",
                        "Negative design moment must be finite and nonpositive.",
                        "negative_design_moment_knm",
                        "Supply the signed negative moment in kNm.",
                    ),
                ),
                provenance=provenance,
            )
        demands.append(("negative", Face.TOP, abs(value)))
    if not demands:
        return rejected_result(
            FLEXURE_CHECK_OPERATION,
            operation_inputs,
            (
                _diagnostic(
                    FLEXURE_CHECK_OPERATION,
                    "INPUT.REQUIRED",
                    "At least one signed bending demand is required.",
                    "design_moment",
                    "Supply a positive and/or negative design moment.",
                ),
            ),
            provenance=provenance,
        )
    checks: list[dict[str, object]] = []
    diagnostics: list[Diagnostic] = []
    any_not_applicable = False
    any_rejected = False
    all_pass = True
    for sign, face, demand in demands:
        capacity = flexural_capacity(replace(base, tension_face=face))
        if capacity.execution is ExecutionState.REJECTED_INPUT:
            any_rejected = True
            diagnostics.extend(capacity.diagnostics)
            all_pass = False
            continue
        if capacity.applicability is ApplicabilityState.NOT_APPLICABLE:
            any_not_applicable = True
            diagnostics.extend(capacity.diagnostics)
            all_pass = False
            continue
        output = capacity.outputs
        ast = float(output["tension_steel_area_mm2"])
        total_area = ast + float(output["compression_steel_area_mm2"])
        minimum_ok = ast + 1e-9 >= float(output["minimum_tension_steel_area_mm2"])
        maximum_ok = total_area <= float(output["maximum_total_steel_area_mm2"]) + 1e-9
        capacity_value = float(output["capacity_knm"])
        utilization = demand / capacity_value if capacity_value > 0 else math.inf
        passed = (
            capacity.engineering is EngineeringState.PASS
            and minimum_ok
            and maximum_ok
            and demand <= capacity_value + 1e-9
        )
        all_pass = all_pass and passed
        checks.append(
            {
                "sign": sign,
                "tension_face": face,
                "demand_knm": demand,
                "capacity_knm": capacity_value,
                "utilization": utilization,
                "minimum_steel_pass": minimum_ok,
                "maximum_steel_pass": maximum_ok,
                "capacity_result_id": capacity.result_id,
                "engineering": "pass" if passed else "fail",
            }
        )
        diagnostics.extend(capacity.diagnostics)
        if not passed:
            diagnostics.append(
                _diagnostic(
                    FLEXURE_CHECK_OPERATION,
                    "FLEXURE.FAIL",
                    f"The {sign} bending check does not satisfy every capacity and reinforcement criterion.",
                    f"{sign}_design_moment_knm",
                    "Revise the section or actual reinforcement.",
                )
            )
    if any_rejected:
        return rejected_result(
            FLEXURE_CHECK_OPERATION,
            operation_inputs,
            diagnostics,
            provenance=provenance,
        )
    if any_not_applicable:
        return not_applicable_result(
            FLEXURE_CHECK_OPERATION,
            operation_inputs,
            diagnostics[0],
            provenance=provenance,
        )
    return completed_result(
        FLEXURE_CHECK_OPERATION,
        operation_inputs,
        {
            "checks": checks,
            "governing_utilization": max(
                float(check["utilization"]) for check in checks
            ),
        },
        engineering=EngineeringState.PASS if all_pass else EngineeringState.FAIL,
        diagnostics=diagnostics,
        provenance=provenance,
    )


__all__ = [
    "CODE_DATA_REVISION",
    "FLEXURAL_CAPACITY_OPERATION",
    "FLEXURE_CHECK_OPERATION",
    "FlexuralCapacityRequest",
    "FlexureCheckRequest",
    "SectionKind",
    "check_flexure",
    "flexural_capacity",
]
