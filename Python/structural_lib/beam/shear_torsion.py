"""IS 456 supplied-link shear and concurrent torsion operations."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

from structural_lib.codes.is456 import tables

from .flexure import (
    FlexuralCapacityRequest,
    FlexureCheckRequest,
    SectionKind,
    check_flexure,
)
from .reinforcement import Face
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
    not_evaluated_result,
    rejected_result,
)

SHEAR_CAPACITY_OPERATION = "is456.beam.shear_capacity/v1"
SHEAR_CHECK_OPERATION = "is456.beam.shear.check/v1"
TORSION_CHECK_OPERATION = "is456.beam.torsion.check/v1"
CODE_DATA_REVISION = "is456-wp02-v1"


class ShearAxis(StrEnum):
    V2 = "v2"
    V3 = "v3"


class ActionBasis(StrEnum):
    STATIC_CONCURRENT = "static_concurrent"
    STAGED_STEP = "staged_step"
    COMPONENT_ENVELOPE = "component_envelope"
    DESIGN_ENVELOPE = "design_envelope"


@dataclass(frozen=True)
class TransverseLink:
    link_id: str
    diameter_mm: float
    legs_v2: int
    legs_v3: int
    spacing_mm: float
    steel_yield_strength_n_per_mm2: float
    closed: bool
    centre_width_mm: float
    centre_depth_mm: float


@dataclass(frozen=True)
class ShearCapacityRequest:
    profile_id: str
    axis: ShearAxis
    resisting_width_mm: float
    effective_depth_mm: float
    concrete_strength_n_per_mm2: float
    longitudinal_tension_area_mm2: float
    link: TransverseLink | None
    code_data_revision_id: str = CODE_DATA_REVISION


@dataclass(frozen=True)
class ShearDemand:
    station_id: str
    axis: ShearAxis
    shear_kn: float


@dataclass(frozen=True)
class ShearCheckRequest:
    capacities: tuple[ShearCapacityRequest, ...]
    demands: tuple[ShearDemand, ...]


@dataclass(frozen=True)
class ConcurrentActionRow:
    row_id: str
    station_id: str
    action_basis: ActionBasis
    v2_kn: float
    v3_kn: float
    torsion_knm: float
    m2_knm: float
    m3_knm: float
    source_identity: str


@dataclass(frozen=True)
class TorsionCheckRequest:
    profile_id: str
    action: ConcurrentActionRow
    flexural_capacity: FlexuralCapacityRequest
    link: TransverseLink | None
    perimeter_bar_ids: tuple[str, ...]
    code_data_revision_id: str = CODE_DATA_REVISION


def _provenance(method: str, revision: str = CODE_DATA_REVISION) -> Provenance:
    return Provenance(
        revision,
        method,
        ("IS 456:2000 normalized WP02 shear and torsion rules",),
    )


def _diagnostic(
    operation: str,
    code: str,
    message: str,
    field: str,
    remediation: str,
    severity: str = "error",
) -> Diagnostic:
    return Diagnostic(
        code,
        severity,
        message,
        operation,
        field,
        "is456-shear-torsion",
        remediation,
    )


def _finite_positive(value: float) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(value) and value > 0


def _link_area(link: TransverseLink, axis: ShearAxis) -> float:
    legs = link.legs_v2 if axis is ShearAxis.V2 else link.legs_v3
    return legs * math.pi * link.diameter_mm**2 / 4.0


def _capacity_inputs(request: ShearCapacityRequest) -> dict[str, dict[str, object]]:
    return effective_inputs(
        profile_id=request.profile_id,
        axis=request.axis,
        resisting_width_mm=request.resisting_width_mm,
        effective_depth_mm=request.effective_depth_mm,
        concrete_strength_n_per_mm2=request.concrete_strength_n_per_mm2,
        longitudinal_tension_area_mm2=request.longitudinal_tension_area_mm2,
        link=request.link,
        code_data_revision_id=request.code_data_revision_id,
    )


def shear_capacity(request: ShearCapacityRequest) -> OperationResult:
    inputs = _capacity_inputs(request)
    provenance = _provenance("is456-shear-capacity-wp02-v1", request.code_data_revision_id)
    for field, value in (
        ("resisting_width_mm", request.resisting_width_mm),
        ("effective_depth_mm", request.effective_depth_mm),
        ("concrete_strength_n_per_mm2", request.concrete_strength_n_per_mm2),
        ("longitudinal_tension_area_mm2", request.longitudinal_tension_area_mm2),
    ):
        if not _finite_positive(value):
            return rejected_result(
                SHEAR_CAPACITY_OPERATION,
                inputs,
                (_diagnostic(SHEAR_CAPACITY_OPERATION, "INPUT.RANGE", f"{field} must be finite and positive.", field, "Supply the required value in its declared unit."),),
                provenance=provenance,
            )
    fck = request.concrete_strength_n_per_mm2
    if not 15 <= fck <= 40:
        return not_applicable_result(
            SHEAR_CAPACITY_OPERATION,
            inputs,
            _diagnostic(SHEAR_CAPACITY_OPERATION, "PROFILE.UNSUPPORTED", "Concrete grade is outside the WP02 Table 19/20 domain.", "concrete_strength_n_per_mm2", "Use fck from 15 through 40 N/mm2 or another profile.", "information"),
            provenance=provenance,
        )
    if request.link is None:
        return not_evaluated_result(
            SHEAR_CAPACITY_OPERATION,
            inputs,
            _diagnostic(SHEAR_CAPACITY_OPERATION, "REINFORCEMENT.REQUIRED", "Provided shear capacity requires an actual transverse link.", "link", "Supply the link diameter, active legs, spacing, grade, closure, and centre dimensions."),
            provenance=provenance,
        )
    link = request.link
    active_legs = link.legs_v2 if request.axis is ShearAxis.V2 else link.legs_v3
    invalid_link = (
        not link.link_id.strip()
        or not _finite_positive(link.diameter_mm)
        or not _finite_positive(link.spacing_mm)
        or not _finite_positive(link.steel_yield_strength_n_per_mm2)
        or active_legs < 2
    )
    if invalid_link:
        return rejected_result(
            SHEAR_CAPACITY_OPERATION,
            inputs,
            (_diagnostic(SHEAR_CAPACITY_OPERATION, "INPUT.RANGE", "The actual link requires an id, positive dimensions and grade, and at least two active legs.", "link", "Resolve a valid link for the requested shear axis."),),
            provenance=provenance,
        )
    if not 250 <= link.steel_yield_strength_n_per_mm2 <= 500:
        return not_applicable_result(
            SHEAR_CAPACITY_OPERATION,
            inputs,
            _diagnostic(SHEAR_CAPACITY_OPERATION, "PROFILE.UNSUPPORTED", "Link steel grade is outside the WP02 material domain.", "link.steel_yield_strength_n_per_mm2", "Use fy from 250 through 500 N/mm2 or another profile.", "information"),
            provenance=provenance,
        )
    b = request.resisting_width_mm
    d = request.effective_depth_mm
    pt_actual = 100.0 * request.longitudinal_tension_area_mm2 / (b * d)
    pt_table = min(3.0, max(0.15, pt_actual))
    tau_c = tables.get_tc_value(fck, pt_table)
    tau_c_max = tables.get_tc_max_value(fck)
    asv = _link_area(link, request.axis)
    design_fy = min(415.0, link.steel_yield_strength_n_per_mm2)
    concrete_capacity_kn = tau_c * b * d / 1000.0
    link_capacity_kn = 0.87 * design_fy * asv * d / link.spacing_mm / 1000.0
    limiting_capacity_kn = tau_c_max * b * d / 1000.0
    provided_capacity_kn = min(concrete_capacity_kn + link_capacity_kn, limiting_capacity_kn)
    maximum_spacing_mm = min(0.75 * d, 300.0)
    provided_ratio = asv / (b * link.spacing_mm)
    required_minimum_ratio = 0.4 / (0.87 * design_fy)
    spacing_pass = link.spacing_mm <= maximum_spacing_mm + 1e-9
    minimum_link_pass = provided_ratio + 1e-12 >= required_minimum_ratio
    diagnostics: list[Diagnostic] = []
    if not spacing_pass:
        diagnostics.append(_diagnostic(SHEAR_CAPACITY_OPERATION, "SHEAR.SPACING", "Actual link spacing exceeds the permitted maximum.", "link.spacing_mm", "Reduce the link spacing."))
    if not minimum_link_pass:
        diagnostics.append(_diagnostic(SHEAR_CAPACITY_OPERATION, "SHEAR.MINIMUM_REINFORCEMENT", "Actual link provision is below minimum shear reinforcement.", "link", "Increase active link area or reduce spacing."))
    return completed_result(
        SHEAR_CAPACITY_OPERATION,
        inputs,
        {
            "axis": request.axis,
            "longitudinal_percentage_actual": pt_actual,
            "longitudinal_percentage_table": pt_table,
            "tau_c_n_per_mm2": tau_c,
            "tau_c_max_n_per_mm2": tau_c_max,
            "link_area_mm2": asv,
            "link_design_strength_n_per_mm2": design_fy,
            "concrete_capacity_kn": concrete_capacity_kn,
            "link_capacity_kn": link_capacity_kn,
            "limiting_capacity_kn": limiting_capacity_kn,
            "provided_capacity_kn": provided_capacity_kn,
            "maximum_spacing_mm": maximum_spacing_mm,
            "spacing_pass": spacing_pass,
            "minimum_link_pass": minimum_link_pass,
        },
        engineering=EngineeringState.PASS if spacing_pass and minimum_link_pass else EngineeringState.FAIL,
        diagnostics=diagnostics,
        provenance=provenance,
    )


def check_shear(request: ShearCheckRequest) -> OperationResult:
    inputs = effective_inputs(capacities=request.capacities, demands=request.demands)
    provenance = _provenance("is456-shear-check-wp02-v1")
    if not request.capacities or not request.demands:
        return rejected_result(
            SHEAR_CHECK_OPERATION,
            inputs,
            (_diagnostic(SHEAR_CHECK_OPERATION, "INPUT.REQUIRED", "At least one capacity and station demand are required.", "capacities", "Supply axis-qualified capacity requests and demands."),),
            provenance=provenance,
        )
    capacity_by_axis: dict[ShearAxis, OperationResult] = {}
    for capacity_request in request.capacities:
        if capacity_request.axis in capacity_by_axis:
            return rejected_result(SHEAR_CHECK_OPERATION, inputs, (_diagnostic(SHEAR_CHECK_OPERATION, "INPUT.CONFLICT", "Only one supplied capacity basis is allowed per shear axis.", "capacities", "Remove the duplicate axis capacity."),), provenance=provenance)
        capacity_by_axis[capacity_request.axis] = shear_capacity(capacity_request)
    for capacity in capacity_by_axis.values():
        if capacity.execution is ExecutionState.REJECTED_INPUT:
            return rejected_result(SHEAR_CHECK_OPERATION, inputs, capacity.diagnostics, provenance=provenance)
        if capacity.engineering is EngineeringState.NOT_EVALUATED:
            diagnostic = capacity.diagnostics[0]
            return not_evaluated_result(SHEAR_CHECK_OPERATION, inputs, diagnostic, provenance=provenance)
        if capacity.applicability is ApplicabilityState.NOT_APPLICABLE:
            return not_applicable_result(SHEAR_CHECK_OPERATION, inputs, capacity.diagnostics[0], provenance=provenance)
    checks: list[dict[str, object]] = []
    diagnostics: list[Diagnostic] = []
    all_pass = True
    for demand in request.demands:
        if not demand.station_id.strip() or not math.isfinite(demand.shear_kn):
            return rejected_result(SHEAR_CHECK_OPERATION, inputs, (_diagnostic(SHEAR_CHECK_OPERATION, "INPUT.RANGE", "Each station demand requires an id and finite shear.", "demands", "Resolve the station and signed shear in kN."),), provenance=provenance)
        capacity = capacity_by_axis.get(demand.axis)
        if capacity is None:
            return not_evaluated_result(SHEAR_CHECK_OPERATION, inputs, _diagnostic(SHEAR_CHECK_OPERATION, "SHEAR.CAPACITY_MISSING", "No supplied capacity basis exists for a demanded axis.", demand.axis, "Supply the actual section and link capacity basis for this axis."), provenance=provenance)
        output = capacity.outputs
        magnitude = abs(demand.shear_kn)
        capacity_kn = float(output["provided_capacity_kn"])
        passed = capacity.engineering is EngineeringState.PASS and magnitude <= capacity_kn + 1e-9
        all_pass = all_pass and passed
        utilization = magnitude / capacity_kn
        checks.append({"station_id": demand.station_id, "axis": demand.axis, "signed_demand_kn": demand.shear_kn, "capacity_kn": capacity_kn, "utilization": utilization, "capacity_result_id": capacity.result_id, "engineering": "pass" if passed else "fail"})
        if not passed:
            diagnostics.append(_diagnostic(SHEAR_CHECK_OPERATION, "SHEAR.FAIL", "Station shear exceeds supplied capacity or the link arrangement fails.", demand.station_id, "Revise the section or actual transverse reinforcement."))
    return completed_result(
        SHEAR_CHECK_OPERATION,
        inputs,
        {"checks": checks, "governing_utilization": max(float(check["utilization"]) for check in checks)},
        engineering=EngineeringState.PASS if all_pass else EngineeringState.FAIL,
        diagnostics=diagnostics,
        provenance=provenance,
    )


def check_torsion(request: TorsionCheckRequest) -> OperationResult:
    inputs = effective_inputs(
        profile_id=request.profile_id,
        action=request.action,
        flexural_capacity=request.flexural_capacity,
        link=request.link,
        perimeter_bar_ids=request.perimeter_bar_ids,
        code_data_revision_id=request.code_data_revision_id,
    )
    provenance = _provenance("is456-torsion-check-wp02-v1", request.code_data_revision_id)
    action = request.action
    if action.action_basis not in (ActionBasis.STATIC_CONCURRENT, ActionBasis.STAGED_STEP):
        return rejected_result(
            TORSION_CHECK_OPERATION,
            inputs,
            (_diagnostic(TORSION_CHECK_OPERATION, "ACTION.CONCURRENCY", "Torsion interaction requires one concurrent action row.", "action.action_basis", "Supply a static concurrent or staged-step row; do not combine component envelopes."),),
            provenance=provenance,
        )
    if not action.row_id.strip() or not action.station_id.strip() or not action.source_identity.strip() or any(not math.isfinite(value) for value in (action.v2_kn, action.v3_kn, action.torsion_knm, action.m2_knm, action.m3_knm)):
        return rejected_result(TORSION_CHECK_OPERATION, inputs, (_diagnostic(TORSION_CHECK_OPERATION, "INPUT.RANGE", "The concurrent action row requires identity and finite components.", "action", "Resolve the complete source row."),), provenance=provenance)
    if abs(action.v3_kn) > 1e-12 or abs(action.m2_knm) > 1e-12:
        return not_applicable_result(
            TORSION_CHECK_OPERATION,
            inputs,
            _diagnostic(TORSION_CHECK_OPERATION, "PROFILE.UNSUPPORTED", "WP02 does not ignore nonzero minor-axis shear or bending interaction.", "action", "Use a profile supporting biaxial torsion interaction.", "information"),
            provenance=provenance,
        )
    if request.flexural_capacity.section_kind is not SectionKind.RECTANGULAR:
        return not_applicable_result(TORSION_CHECK_OPERATION, inputs, _diagnostic(TORSION_CHECK_OPERATION, "PROFILE.UNSUPPORTED", "WP02 torsion is limited to solid rectangular sections.", "flexural_capacity.section_kind", "Use a supported rectangular section or another profile.", "information"), provenance=provenance)
    if request.link is None:
        return not_evaluated_result(TORSION_CHECK_OPERATION, inputs, _diagnostic(TORSION_CHECK_OPERATION, "REINFORCEMENT.REQUIRED", "Torsion checking requires an actual closed link.", "link", "Supply the closed-link geometry, spacing, active legs, and grade."), provenance=provenance)
    link = request.link
    if not link.closed:
        return completed_result(TORSION_CHECK_OPERATION, inputs, {"action_row_id": action.row_id}, engineering=EngineeringState.FAIL, diagnostics=(_diagnostic(TORSION_CHECK_OPERATION, "TORSION.CLOSED_LINK_REQUIRED", "Actual transverse reinforcement is not a closed torsion link.", "link.closed", "Provide a closed link around the perimeter reinforcement."),), provenance=provenance)
    if not all(_finite_positive(value) for value in (link.diameter_mm, link.spacing_mm, link.steel_yield_strength_n_per_mm2, link.centre_width_mm, link.centre_depth_mm)) or link.legs_v2 < 2 or link.legs_v3 < 2:
        return rejected_result(TORSION_CHECK_OPERATION, inputs, (_diagnostic(TORSION_CHECK_OPERATION, "INPUT.RANGE", "Closed-link dimensions, active legs, spacing, and grade must be valid.", "link", "Resolve the actual closed-link geometry."),), provenance=provenance)
    if not 250 <= link.steel_yield_strength_n_per_mm2 <= 500:
        return not_applicable_result(TORSION_CHECK_OPERATION, inputs, _diagnostic(TORSION_CHECK_OPERATION, "PROFILE.UNSUPPORTED", "Link grade is outside the WP02 torsion domain.", "link.steel_yield_strength_n_per_mm2", "Use fy from 250 through 500 N/mm2 or another profile.", "information"), provenance=provenance)
    bars = request.flexural_capacity.bars
    section_width = request.flexural_capacity.web_width_mm
    section_depth = request.flexural_capacity.depth_mm
    if link.centre_width_mm >= section_width or link.centre_depth_mm >= section_depth:
        return rejected_result(TORSION_CHECK_OPERATION, inputs, (_diagnostic(TORSION_CHECK_OPERATION, "GEOMETRY.RANGE", "Closed-link centre dimensions must fit inside the section.", "link", "Resolve link centre dimensions within the concrete section."),), provenance=provenance)
    bar_ids = {bar.bar_id for bar in bars}
    perimeter_ids = set(request.perimeter_bar_ids)
    perimeter_resolved = len(perimeter_ids) >= 4 and perimeter_ids <= bar_ids
    perimeter_bars = tuple(bar for bar in bars if bar.bar_id in perimeter_ids)
    top_perimeter = tuple(bar for bar in perimeter_bars if bar.face is Face.TOP)
    bottom_perimeter = tuple(bar for bar in perimeter_bars if bar.face is Face.BOTTOM)
    has_four_corners = (
        len(top_perimeter) >= 2
        and len(bottom_perimeter) >= 2
        and min(bar.x_from_left_mm for bar in top_perimeter) < section_width / 2
        and max(bar.x_from_left_mm for bar in top_perimeter) > section_width / 2
        and min(bar.x_from_left_mm for bar in bottom_perimeter) < section_width / 2
        and max(bar.x_from_left_mm for bar in bottom_perimeter) > section_width / 2
    ) if top_perimeter and bottom_perimeter else False
    perimeter_pass = perimeter_resolved and has_four_corners
    b = section_width
    depth = section_depth
    active_tension_face = Face.BOTTOM if action.m3_knm >= 0 else Face.TOP
    active_bars = tuple(bar for bar in bars if bar.face is active_tension_face)
    if not active_bars:
        return not_evaluated_result(TORSION_CHECK_OPERATION, inputs, _diagnostic(TORSION_CHECK_OPERATION, "REINFORCEMENT.REQUIRED", "The primary bending face has no resolved longitudinal bars.", "flexural_capacity.bars", "Supply actual bars on the primary tension face."), provenance=provenance)
    active_area = sum(math.pi * bar.diameter_mm**2 / 4.0 for bar in active_bars)
    active_y = sum(math.pi * bar.diameter_mm**2 / 4.0 * bar.y_from_top_mm for bar in active_bars) / active_area
    d = active_y if active_tension_face is Face.BOTTOM else depth - active_y
    torsion = abs(action.torsion_knm)
    shear = abs(action.v2_kn)
    bending = abs(action.m3_knm)
    equivalent_shear_kn = shear + 1.6 * torsion * 1000.0 / b
    torsion_moment_knm = torsion * (1.0 + depth / b) / 1.7
    primary_moment_knm = bending + torsion_moment_knm
    opposite_moment_knm = max(0.0, torsion_moment_knm - bending)
    primary_positive = action.m3_knm >= 0
    flexure_request = FlexureCheckRequest(
        request.flexural_capacity,
        positive_design_moment_knm=primary_moment_knm if primary_positive else opposite_moment_knm,
        negative_design_moment_knm=-opposite_moment_knm if primary_positive else -primary_moment_knm,
    )
    flexure_result = check_flexure(flexure_request)
    if flexure_result.execution is ExecutionState.REJECTED_INPUT:
        return rejected_result(TORSION_CHECK_OPERATION, inputs, flexure_result.diagnostics, provenance=provenance)
    if flexure_result.applicability is ApplicabilityState.NOT_APPLICABLE:
        return not_applicable_result(TORSION_CHECK_OPERATION, inputs, flexure_result.diagnostics[0], provenance=provenance)
    if flexure_result.engineering is EngineeringState.NOT_EVALUATED:
        return not_evaluated_result(TORSION_CHECK_OPERATION, inputs, flexure_result.diagnostics[0], provenance=provenance)
    tension_area = sum(math.pi * bar.diameter_mm**2 / 4.0 for bar in bars if bar.face is active_tension_face)
    pt_table = min(3.0, max(0.15, 100.0 * tension_area / (b * d)))
    tau_c = tables.get_tc_value(request.flexural_capacity.concrete_strength_n_per_mm2, pt_table)
    tau_c_max = tables.get_tc_max_value(request.flexural_capacity.concrete_strength_n_per_mm2)
    tau_ve = equivalent_shear_kn * 1000.0 / (b * d)
    design_fy = min(415.0, link.steel_yield_strength_n_per_mm2)
    required_torsion = torsion * 1e6 / (link.centre_width_mm * link.centre_depth_mm * 0.87 * design_fy)
    required_shear = shear * 1000.0 / (2.5 * link.centre_depth_mm * 0.87 * design_fy)
    required_floor = max(0.0, (tau_ve - tau_c) * b / (0.87 * design_fy))
    required_area_per_spacing = max(required_torsion + required_shear, required_floor, 0.4 * b / (0.87 * design_fy))
    provided_area_per_spacing = _link_area(link, ShearAxis.V2) / link.spacing_mm
    maximum_spacing = min(0.75 * d, 300.0, link.centre_width_mm, link.centre_depth_mm, (link.centre_width_mm + link.centre_depth_mm) / 4.0)
    stress_pass = tau_ve <= tau_c_max + 1e-12
    transverse_pass = provided_area_per_spacing + 1e-12 >= required_area_per_spacing and link.spacing_mm <= maximum_spacing + 1e-9
    flexure_pass = flexure_result.engineering is EngineeringState.PASS
    passed = stress_pass and transverse_pass and flexure_pass and perimeter_pass
    diagnostics: list[Diagnostic] = []
    if not stress_pass:
        diagnostics.append(_diagnostic(TORSION_CHECK_OPERATION, "TORSION.SECTION_STRESS", "Equivalent shear stress exceeds the section limit.", action.station_id, "Increase the section or concrete grade."))
    if not transverse_pass:
        diagnostics.append(_diagnostic(TORSION_CHECK_OPERATION, "TORSION.TRANSVERSE_REINFORCEMENT", "Actual closed links do not satisfy required area per spacing and spacing limits.", "link", "Increase closed-link area or reduce spacing."))
    if not flexure_pass:
        diagnostics.append(_diagnostic(TORSION_CHECK_OPERATION, "TORSION.LONGITUDINAL_REINFORCEMENT", "Actual longitudinal reinforcement does not satisfy both equivalent moments.", "flexural_capacity.bars", "Revise physical top and bottom longitudinal bars."))
    if not perimeter_pass:
        diagnostics.append(_diagnostic(TORSION_CHECK_OPERATION, "TORSION.PERIMETER_REINFORCEMENT", "Perimeter reinforcement must resolve at least four identified bars across top and bottom faces.", "perimeter_bar_ids", "Identify the actual perimeter corner bars enclosed by the closed link."))
    return completed_result(
        TORSION_CHECK_OPERATION,
        inputs,
        {
            "action_row_id": action.row_id,
            "station_id": action.station_id,
            "equivalent_shear_kn": equivalent_shear_kn,
            "torsion_moment_knm": torsion_moment_knm,
            "primary_equivalent_moment_knm": primary_moment_knm,
            "opposite_equivalent_moment_knm": opposite_moment_knm,
            "tau_ve_n_per_mm2": tau_ve,
            "tau_c_n_per_mm2": tau_c,
            "tau_c_max_n_per_mm2": tau_c_max,
            "required_link_area_per_spacing_mm": required_area_per_spacing,
            "provided_link_area_per_spacing_mm": provided_area_per_spacing,
            "maximum_spacing_mm": maximum_spacing,
            "perimeter_bar_ids": tuple(sorted(perimeter_ids)),
            "flexure_result_id": flexure_result.result_id,
            "stress_pass": stress_pass,
            "transverse_pass": transverse_pass,
            "longitudinal_pass": flexure_pass,
            "perimeter_pass": perimeter_pass,
        },
        engineering=EngineeringState.PASS if passed else EngineeringState.FAIL,
        diagnostics=diagnostics,
        provenance=provenance,
    )


__all__ = [
    "ActionBasis",
    "ConcurrentActionRow",
    "ShearAxis",
    "ShearCapacityRequest",
    "ShearCheckRequest",
    "ShearDemand",
    "TorsionCheckRequest",
    "TransverseLink",
    "check_shear",
    "check_torsion",
    "shear_capacity",
]
