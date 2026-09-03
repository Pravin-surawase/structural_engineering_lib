"""IS 456 beam serviceability limits and explicit-basis checks."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

from .reinforcement import BarPosition, Face
from .semantics import (
    Diagnostic,
    EngineeringState,
    OperationResult,
    Provenance,
    completed_result,
    effective_inputs,
    not_evaluated_result,
    rejected_result,
)

DEFLECTION_LIMIT_OPERATION = "is456.beam.deflection_limit/v1"
CRACK_WIDTH_LIMIT_OPERATION = "is456.beam.crack_width_limit/v1"
DEFLECTION_CHECK_OPERATION = "is456.beam.deflection.check/v1"
CRACK_WIDTH_CHECK_OPERATION = "is456.beam.crack_width.check/v1"
CODE_DATA_REVISION = "is456-wp04-v1"


class LimitSource(StrEnum):
    CODE = "code"
    PROJECT = "project"
    SUPPLIED = "supplied"


class DeflectionCriterion(StrEnum):
    TOTAL_FINAL = "total_final"
    AFTER_FINISHES = "after_finishes"


class SupportCondition(StrEnum):
    CANTILEVER = "cantilever"
    SIMPLY_SUPPORTED = "simply_supported"
    CONTINUOUS = "continuous"


class DeflectionMethod(StrEnum):
    SPAN_DEPTH_SCREENING = "span_depth_screening"
    CALCULATED_COMPONENTS = "calculated_components"


class ExposureClass(StrEnum):
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    VERY_SEVERE = "very_severe"
    EXTREME = "extreme"


@dataclass(frozen=True)
class DeflectionLimitRequest:
    profile_id: str
    span_mm: float
    criterion: DeflectionCriterion
    selected_source: LimitSource = LimitSource.CODE
    project_limit_mm: float | None = None
    supplied_limit_mm: float | None = None
    code_data_revision_id: str = CODE_DATA_REVISION


@dataclass(frozen=True)
class CrackWidthLimitRequest:
    profile_id: str
    exposure_class: ExposureClass
    cracking_harmful: bool
    selected_source: LimitSource = LimitSource.CODE
    project_limit_mm: float | None = None
    supplied_limit_mm: float | None = None
    code_data_revision_id: str = CODE_DATA_REVISION


@dataclass(frozen=True)
class DeflectionScreeningBasis:
    effective_span_mm: float
    effective_depth_mm: float
    support_condition: SupportCondition
    tension_steel_modification_factor: float
    compression_steel_modification_factor: float
    flanged_section_modification_factor: float
    span_support_reference: str
    modification_factors_reference: str


@dataclass(frozen=True)
class CalculatedDeflectionBasis:
    service_action_snapshot_id: str
    total_service_action_row_ids: tuple[str, ...]
    sustained_service_action_row_ids: tuple[str, ...]
    analysis_result_id: str
    reinforcement_revision_id: str
    effective_span_mm: float
    instantaneous_total_deflection_mm: float
    instantaneous_sustained_deflection_mm: float
    creep_multiplier: float
    shrinkage_deflection_mm: float
    finish_installation_age_days: float | None
    deflection_at_finish_installation_mm: float | None
    age_at_loading_days: float | None
    assessment_age_days: float | None
    sustained_duration_days: float | None
    relative_humidity_percent: float | None
    notional_size_mm: float | None
    stiffness_method: str | None
    cracking_method: str | None
    creep_method: str | None
    shrinkage_method: str | None


@dataclass(frozen=True)
class DeflectionCheckRequest:
    profile_id: str
    method: DeflectionMethod
    screening: DeflectionScreeningBasis | None = None
    calculated: CalculatedDeflectionBasis | None = None
    total_limit: DeflectionLimitRequest | None = None
    after_finishes_limit: DeflectionLimitRequest | None = None
    code_data_revision_id: str = CODE_DATA_REVISION


@dataclass(frozen=True)
class CrackWidthCheckRequest:
    profile_id: str
    member_id: str
    station_id: str
    service_action_row_id: str
    reinforcement_revision_id: str
    section_width_mm: float
    section_depth_mm: float
    neutral_axis_depth_from_compression_face_mm: float
    tension_face: Face
    bars: tuple[BarPosition, ...]
    surface_point_x_from_left_mm: float
    service_steel_stress_n_per_mm2: float
    steel_yield_strength_n_per_mm2: float
    steel_modulus_n_per_mm2: float
    mean_strain_at_tension_surface: float | None
    limit: CrackWidthLimitRequest
    code_data_revision_id: str = CODE_DATA_REVISION


def _provenance(method: str, revision: str = CODE_DATA_REVISION) -> Provenance:
    return Provenance(
        revision,
        method,
        (
            "IS 456:2000 serviceability provisions with Amendment 4 exposure ceiling",
            "IS 456 Annex F flexural crack-width relationship",
        ),
    )


def _diagnostic(
    operation: str,
    code: str,
    message: str,
    field: str,
    remediation: str,
) -> Diagnostic:
    return Diagnostic(
        code,
        "error",
        message,
        operation,
        field,
        "is456-serviceability",
        remediation,
    )


def _positive(value: float | None) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(value) and value > 0


def _nonnegative(value: float | None) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(value) and value >= 0


def _select_limit(
    operation: str,
    source: LimitSource,
    code_limit: float,
    project_limit: float | None,
    supplied_limit: float | None,
    *,
    ceiling: float | None = None,
) -> tuple[float, str] | Diagnostic:
    if not isinstance(source, LimitSource):
        return _diagnostic(operation, "INPUT.ENUM", "selected_source is invalid.", "selected_source", "Select code, project, or supplied.")
    if source is LimitSource.CODE:
        if project_limit is not None or supplied_limit is not None:
            return _diagnostic(operation, "INPUT.CONFLICT", "Code source cannot be selected while an override value is supplied.", "selected_source", "Remove overrides or explicitly select their source.")
        return code_limit, "code"
    selected = project_limit if source is LimitSource.PROJECT else supplied_limit
    other = supplied_limit if source is LimitSource.PROJECT else project_limit
    field = "project_limit_mm" if source is LimitSource.PROJECT else "supplied_limit_mm"
    if not _positive(selected) or other is not None:
        return _diagnostic(operation, "INPUT.CONFLICT", "Exactly one positive limit must match the explicitly selected source.", field, "Supply one limit and select its source.")
    if ceiling is not None and selected > ceiling:
        return _diagnostic(operation, "LIMIT.EXCEEDS_CODE", "The selected limit exceeds the applicable code ceiling.", field, "Use the code ceiling or a stricter project limit.")
    return float(selected), source.value


def deflection_limit(request: DeflectionLimitRequest) -> OperationResult:
    inputs = effective_inputs(request=request)
    provenance = _provenance("is456-deflection-limit-wp04-v1", request.code_data_revision_id)
    if (
        not request.profile_id
        or request.code_data_revision_id != CODE_DATA_REVISION
        or not _positive(request.span_mm)
        or not isinstance(request.criterion, DeflectionCriterion)
    ):
        return rejected_result(
            DEFLECTION_LIMIT_OPERATION,
            inputs,
            (_diagnostic(DEFLECTION_LIMIT_OPERATION, "INPUT.INVALID", "Profile, code revision, positive span, and criterion are required.", "request", "Supply the complete limit request."),),
            provenance=provenance,
        )
    code_limit = (
        request.span_mm / 250.0
        if request.criterion is DeflectionCriterion.TOTAL_FINAL
        else min(request.span_mm / 350.0, 20.0)
    )
    selected = _select_limit(
        DEFLECTION_LIMIT_OPERATION,
        request.selected_source,
        code_limit,
        request.project_limit_mm,
        request.supplied_limit_mm,
        ceiling=code_limit,
    )
    if isinstance(selected, Diagnostic):
        return rejected_result(
            DEFLECTION_LIMIT_OPERATION,
            inputs,
            (selected,),
            provenance=provenance,
        )
    limit_mm, source = selected
    return completed_result(
        DEFLECTION_LIMIT_OPERATION,
        inputs,
        {
            "criterion": request.criterion,
            "limit_mm": limit_mm,
            "code_limit_mm": code_limit,
            "selected_source": source,
        },
        provenance=provenance,
    )


def _crack_ceiling(request: CrackWidthLimitRequest) -> float:
    if request.exposure_class in (ExposureClass.VERY_SEVERE, ExposureClass.EXTREME):
        return 0.1
    if request.cracking_harmful or request.exposure_class is not ExposureClass.MILD:
        return 0.2
    return 0.3


def crack_width_limit(request: CrackWidthLimitRequest) -> OperationResult:
    inputs = effective_inputs(request=request)
    provenance = _provenance("is456-crack-width-limit-wp04-v1", request.code_data_revision_id)
    if (
        not request.profile_id
        or request.code_data_revision_id != CODE_DATA_REVISION
        or not isinstance(request.exposure_class, ExposureClass)
        or not isinstance(request.cracking_harmful, bool)
    ):
        return rejected_result(
            CRACK_WIDTH_LIMIT_OPERATION,
            inputs,
            (_diagnostic(CRACK_WIDTH_LIMIT_OPERATION, "INPUT.INVALID", "Profile, code revision, exposure, and harmful-cracking classification are required.", "request", "Supply the complete crack-limit request."),),
            provenance=provenance,
        )
    ceiling = _crack_ceiling(request)
    selected = _select_limit(
        CRACK_WIDTH_LIMIT_OPERATION,
        request.selected_source,
        ceiling,
        request.project_limit_mm,
        request.supplied_limit_mm,
        ceiling=ceiling,
    )
    if isinstance(selected, Diagnostic):
        return rejected_result(
            CRACK_WIDTH_LIMIT_OPERATION,
            inputs,
            (selected,),
            provenance=provenance,
        )
    limit_mm, source = selected
    return completed_result(
        CRACK_WIDTH_LIMIT_OPERATION,
        inputs,
        {
            "exposure_class": request.exposure_class,
            "cracking_harmful": request.cracking_harmful,
            "limit_mm": limit_mm,
            "code_ceiling_mm": ceiling,
            "selected_source": source,
        },
        provenance=provenance,
    )


def _not_evaluated(
    operation: str,
    inputs: dict[str, dict[str, object]],
    provenance: Provenance,
    message: str,
    field: str,
) -> OperationResult:
    return not_evaluated_result(
        operation,
        inputs,
        _diagnostic(operation, "EVIDENCE.REQUIRED", message, field, "Supply the named serviceability evidence."),
        provenance=provenance,
    )


def check_deflection(request: DeflectionCheckRequest) -> OperationResult:
    inputs = effective_inputs(request=request)
    provenance = _provenance("is456-deflection-check-wp04-v1", request.code_data_revision_id)
    if not request.profile_id or request.code_data_revision_id != CODE_DATA_REVISION or not isinstance(request.method, DeflectionMethod):
        return rejected_result(
            DEFLECTION_CHECK_OPERATION,
            inputs,
            (_diagnostic(DEFLECTION_CHECK_OPERATION, "INPUT.INVALID", "Profile, method, and code-data revision are required.", "request", "Supply the complete deflection request."),),
            provenance=provenance,
        )
    if request.method is DeflectionMethod.SPAN_DEPTH_SCREENING:
        if request.screening is None:
            return _not_evaluated(DEFLECTION_CHECK_OPERATION, inputs, provenance, "The screening basis is missing.", "screening")
        if (
            request.calculated is not None
            or request.total_limit is not None
            or request.after_finishes_limit is not None
        ):
            return rejected_result(
                DEFLECTION_CHECK_OPERATION,
                inputs,
                (_diagnostic(DEFLECTION_CHECK_OPERATION, "INPUT.CONFLICT", "A screening request cannot also contain calculated-deflection inputs or displacement limits.", "calculated/limits", "Select one method and its matching input branch."),),
                provenance=provenance,
            )
        basis = request.screening
        factors = (
            basis.tension_steel_modification_factor,
            basis.compression_steel_modification_factor,
            basis.flanged_section_modification_factor,
        )
        if (
            not _positive(basis.effective_span_mm)
            or basis.effective_span_mm > 10_000
            or not _positive(basis.effective_depth_mm)
            or not isinstance(basis.support_condition, SupportCondition)
            or not all(_positive(value) for value in factors)
            or not basis.span_support_reference
            or not basis.modification_factors_reference
        ):
            return rejected_result(
                DEFLECTION_CHECK_OPERATION,
                inputs,
                (_diagnostic(DEFLECTION_CHECK_OPERATION, "SCREENING.INVALID", "Screening requires an eligible span, depth, support, explicit positive factors, and references.", "screening", "Correct the bounded screening basis."),),
                provenance=provenance,
            )
        basic = {
            SupportCondition.CANTILEVER: 7.0,
            SupportCondition.SIMPLY_SUPPORTED: 20.0,
            SupportCondition.CONTINUOUS: 26.0,
        }[basis.support_condition]
        actual = basis.effective_span_mm / basis.effective_depth_mm
        allowable = basic * math.prod(factors)
        passed = actual <= allowable
        diagnostics = () if passed else (
            _diagnostic(DEFLECTION_CHECK_OPERATION, "DEFLECTION.SCREENING_EXCEEDED", "The actual span/depth ratio exceeds the declared modified limit.", "screening", "Increase effective depth or revise the supported design."),
        )
        return completed_result(
            DEFLECTION_CHECK_OPERATION,
            inputs,
            {
                "method": request.method,
                "result_kind": "screening_not_calculated_displacement",
                "actual_span_depth_ratio": actual,
                "basic_span_depth_ratio": basic,
                "allowable_span_depth_ratio": allowable,
                "passed": passed,
            },
            engineering=EngineeringState.PASS if passed else EngineeringState.FAIL,
            diagnostics=diagnostics,
            provenance=provenance,
        )
    if request.screening is not None:
        return rejected_result(
            DEFLECTION_CHECK_OPERATION,
            inputs,
            (_diagnostic(DEFLECTION_CHECK_OPERATION, "INPUT.CONFLICT", "A calculated request cannot also contain screening inputs.", "screening", "Select one method and its matching input branch."),),
            provenance=provenance,
        )
    if request.calculated is None or request.total_limit is None or request.after_finishes_limit is None:
        return _not_evaluated(DEFLECTION_CHECK_OPERATION, inputs, provenance, "Calculated deflection requires component evidence and both limits.", "calculated/limits")
    basis = request.calculated
    required_strings = (
        basis.service_action_snapshot_id,
        basis.analysis_result_id,
        basis.reinforcement_revision_id,
        basis.stiffness_method,
        basis.cracking_method,
        basis.creep_method,
        basis.shrinkage_method,
    )
    history = (
        basis.age_at_loading_days,
        basis.finish_installation_age_days,
        basis.assessment_age_days,
        basis.sustained_duration_days,
        basis.relative_humidity_percent,
        basis.notional_size_mm,
        basis.deflection_at_finish_installation_mm,
    )
    if (
        not all(required_strings)
        or not basis.total_service_action_row_ids
        or not all(basis.total_service_action_row_ids)
        or not basis.sustained_service_action_row_ids
        or not all(basis.sustained_service_action_row_ids)
        or any(value is None for value in history)
    ):
        return _not_evaluated(DEFLECTION_CHECK_OPERATION, inputs, provenance, "The calculated route is missing action, method, load-history, environment, finish, or reinforcement evidence.", "calculated")
    components = (
        basis.instantaneous_total_deflection_mm,
        basis.instantaneous_sustained_deflection_mm,
        basis.creep_multiplier,
        basis.shrinkage_deflection_mm,
        basis.deflection_at_finish_installation_mm,
    )
    if (
        not all(_nonnegative(value) for value in components)
        or not _positive(basis.effective_span_mm)
        or not all(_positive(value) for value in history[:4])
        or not 0 < float(basis.relative_humidity_percent) <= 100
        or not _positive(basis.notional_size_mm)
        or not float(basis.age_at_loading_days)
        <= float(basis.finish_installation_age_days)
        <= float(basis.assessment_age_days)
    ):
        return rejected_result(
            DEFLECTION_CHECK_OPERATION,
            inputs,
            (_diagnostic(DEFLECTION_CHECK_OPERATION, "CALCULATION_BASIS.INVALID", "Deflection components/history must be finite, nonnegative, and chronologically valid.", "calculated", "Correct the explicit calculation basis."),),
            provenance=provenance,
        )
    total_limit_result = deflection_limit(request.total_limit)
    finish_limit_result = deflection_limit(request.after_finishes_limit)
    if total_limit_result.execution != "completed" or finish_limit_result.execution != "completed":
        diagnostic = next(iter(total_limit_result.diagnostics or finish_limit_result.diagnostics))
        return rejected_result(DEFLECTION_CHECK_OPERATION, inputs, (diagnostic,), provenance=provenance)
    if request.total_limit.criterion is not DeflectionCriterion.TOTAL_FINAL or request.after_finishes_limit.criterion is not DeflectionCriterion.AFTER_FINISHES or request.total_limit.span_mm != request.after_finishes_limit.span_mm or request.total_limit.span_mm != basis.effective_span_mm:
        return rejected_result(
            DEFLECTION_CHECK_OPERATION,
            inputs,
            (_diagnostic(DEFLECTION_CHECK_OPERATION, "LIMIT.CONFLICT", "Calculated deflection requires matching-span total-final and after-finishes limits.", "limits", "Supply both criteria for the same effective span."),),
            provenance=provenance,
        )
    creep = basis.instantaneous_sustained_deflection_mm * basis.creep_multiplier
    total = basis.instantaneous_total_deflection_mm + creep + basis.shrinkage_deflection_mm
    after_finishes = max(0.0, total - float(basis.deflection_at_finish_installation_mm))
    total_limit_mm = float(total_limit_result.outputs["limit_mm"])
    finish_limit_mm = float(finish_limit_result.outputs["limit_mm"])
    passed = total <= total_limit_mm and after_finishes <= finish_limit_mm
    diagnostics = () if passed else (
        _diagnostic(DEFLECTION_CHECK_OPERATION, "DEFLECTION.LIMIT_EXCEEDED", "A calculated total or after-finishes deflection exceeds its limit.", "calculated", "Revise stiffness, geometry, reinforcement, or service response."),
    )
    return completed_result(
        DEFLECTION_CHECK_OPERATION,
        inputs,
        {
            "method": request.method,
            "result_kind": "calculated_component_aggregation",
            "instantaneous_total_deflection_mm": basis.instantaneous_total_deflection_mm,
            "instantaneous_sustained_deflection_mm": basis.instantaneous_sustained_deflection_mm,
            "creep_additional_deflection_mm": creep,
            "shrinkage_deflection_mm": basis.shrinkage_deflection_mm,
            "total_final_deflection_mm": total,
            "deflection_at_finish_installation_mm": basis.deflection_at_finish_installation_mm,
            "after_finishes_deflection_mm": after_finishes,
            "total_limit_mm": total_limit_mm,
            "after_finishes_limit_mm": finish_limit_mm,
            "total_pass": total <= total_limit_mm,
            "after_finishes_pass": after_finishes <= finish_limit_mm,
            "passed": passed,
            "service_action_snapshot_id": basis.service_action_snapshot_id,
            "total_service_action_row_ids": basis.total_service_action_row_ids,
            "sustained_service_action_row_ids": basis.sustained_service_action_row_ids,
            "analysis_result_id": basis.analysis_result_id,
            "reinforcement_revision_id": basis.reinforcement_revision_id,
        },
        engineering=EngineeringState.PASS if passed else EngineeringState.FAIL,
        diagnostics=diagnostics,
        provenance=provenance,
    )


def check_crack_width(request: CrackWidthCheckRequest) -> OperationResult:
    inputs = effective_inputs(request=request)
    provenance = _provenance("is456-annex-f-crack-width-wp04-v1", request.code_data_revision_id)
    identity = (
        request.profile_id,
        request.member_id,
        request.station_id,
        request.service_action_row_id,
        request.reinforcement_revision_id,
    )
    if not all(identity) or request.code_data_revision_id != CODE_DATA_REVISION:
        return _not_evaluated(CRACK_WIDTH_CHECK_OPERATION, inputs, provenance, "Member, service-row, and reinforcement-revision evidence is required.", "identity")
    if request.mean_strain_at_tension_surface is None:
        return _not_evaluated(CRACK_WIDTH_CHECK_OPERATION, inputs, provenance, "A supplied mean tension-surface strain is required; it is not inferred from fs/Es.", "mean_strain_at_tension_surface")
    if not request.bars:
        return _not_evaluated(CRACK_WIDTH_CHECK_OPERATION, inputs, provenance, "Actual positioned reinforcement is required.", "bars")
    limit_result = crack_width_limit(request.limit)
    if limit_result.execution != "completed":
        return rejected_result(CRACK_WIDTH_CHECK_OPERATION, inputs, limit_result.diagnostics, provenance=provenance)
    dimensions = (
        request.section_width_mm,
        request.section_depth_mm,
        request.neutral_axis_depth_from_compression_face_mm,
        request.steel_yield_strength_n_per_mm2,
        request.steel_modulus_n_per_mm2,
    )
    if not all(_positive(value) for value in dimensions) or not _nonnegative(request.service_steel_stress_n_per_mm2) or not _nonnegative(request.mean_strain_at_tension_surface) or not isinstance(request.tension_face, Face) or not 0 <= request.surface_point_x_from_left_mm <= request.section_width_mm:
        return rejected_result(
            CRACK_WIDTH_CHECK_OPERATION,
            inputs,
            (_diagnostic(CRACK_WIDTH_CHECK_OPERATION, "INPUT.INVALID", "Section, material, stress/strain, tension face, and surface point must be finite and physically valid.", "request", "Correct the declared crack calculation inputs."),),
            provenance=provenance,
        )
    tension_bars = tuple(bar for bar in request.bars if bar.face is request.tension_face)
    if not tension_bars:
        return _not_evaluated(CRACK_WIDTH_CHECK_OPERATION, inputs, provenance, "No actual bars are assigned to the physical tension face.", "bars")
    for bar in request.bars:
        radius = bar.diameter_mm / 2.0
        if not bar.bar_id or not isinstance(bar.face, Face) or not _positive(bar.diameter_mm) or bar.layer < 1 or not radius <= bar.x_from_left_mm <= request.section_width_mm - radius or not radius <= bar.y_from_top_mm <= request.section_depth_mm - radius:
            return rejected_result(
                CRACK_WIDTH_CHECK_OPERATION,
                inputs,
                (_diagnostic(CRACK_WIDTH_CHECK_OPERATION, "BAR.GEOMETRY", "Every bar surface must fit within the section and retain identity/layer.", f"bars[{bar.bar_id}]", "Correct the actual reinforcement arrangement."),),
                provenance=provenance,
            )
    areas = [math.pi * bar.diameter_mm**2 / 4.0 for bar in tension_bars]
    if request.tension_face is Face.BOTTOM:
        depths = [bar.y_from_top_mm for bar in tension_bars]
        covers = [request.section_depth_mm - bar.y_from_top_mm - bar.diameter_mm / 2.0 for bar in tension_bars]
        surface_y = request.section_depth_mm
    else:
        depths = [request.section_depth_mm - bar.y_from_top_mm for bar in tension_bars]
        covers = [bar.y_from_top_mm - bar.diameter_mm / 2.0 for bar in tension_bars]
        surface_y = 0.0
    effective_depth = math.fsum(area * depth for area, depth in zip(areas, depths, strict=True)) / math.fsum(areas)
    neutral_axis = request.neutral_axis_depth_from_compression_face_mm
    if not 0 < neutral_axis < effective_depth < request.section_depth_mm or min(covers) <= 0:
        return rejected_result(
            CRACK_WIDTH_CHECK_OPERATION,
            inputs,
            (_diagnostic(CRACK_WIDTH_CHECK_OPERATION, "SECTION.GEOMETRY", "Require 0 < neutral-axis depth < tension-steel effective depth < section depth and positive cover.", "neutral_axis/bars", "Correct the service section analysis or reinforcement geometry."),),
            provenance=provenance,
        )
    stress_limit = 0.8 * request.steel_yield_strength_n_per_mm2
    if request.service_steel_stress_n_per_mm2 > stress_limit:
        return rejected_result(
            CRACK_WIDTH_CHECK_OPERATION,
            inputs,
            (_diagnostic(CRACK_WIDTH_CHECK_OPERATION, "STRESS.OUTSIDE_PROFILE", "Service steel stress exceeds the bounded 0.8fy profile.", "service_steel_stress_n_per_mm2", "Supply a supported service state or use another method."),),
            provenance=provenance,
        )
    elastic_surface_strain = (
        request.service_steel_stress_n_per_mm2
        / request.steel_modulus_n_per_mm2
        * (request.section_depth_mm - neutral_axis)
        / (effective_depth - neutral_axis)
    )
    if request.mean_strain_at_tension_surface > elastic_surface_strain + 1e-12:
        return rejected_result(
            CRACK_WIDTH_CHECK_OPERATION,
            inputs,
            (_diagnostic(CRACK_WIDTH_CHECK_OPERATION, "STRAIN.OUTSIDE_PROFILE", "Mean strain exceeds the unmodified elastic tension-surface strain.", "mean_strain_at_tension_surface", "Reconcile the supplied strain with the service section analysis."),),
            provenance=provenance,
        )
    distances = [
        (
            math.hypot(bar.x_from_left_mm - request.surface_point_x_from_left_mm, bar.y_from_top_mm - surface_y) - bar.diameter_mm / 2.0,
            bar,
        )
        for bar in tension_bars
    ]
    acr, nearest = min(distances, key=lambda item: item[0])
    cmin = min(covers)
    denominator = 1.0 + 2.0 * (acr - cmin) / (request.section_depth_mm - neutral_axis)
    if acr < cmin or denominator <= 0:
        return rejected_result(
            CRACK_WIDTH_CHECK_OPERATION,
            inputs,
            (_diagnostic(CRACK_WIDTH_CHECK_OPERATION, "CRACK_GEOMETRY.INVALID", "Derived surface-to-bar geometry is outside the Annex F profile.", "surface_point/bars", "Correct the surface point and actual bar geometry."),),
            provenance=provenance,
        )
    width = 3.0 * acr * request.mean_strain_at_tension_surface / denominator
    limit_mm = float(limit_result.outputs["limit_mm"])
    passed = width <= limit_mm
    diagnostics = () if passed else (
        _diagnostic(CRACK_WIDTH_CHECK_OPERATION, "CRACK_WIDTH.LIMIT_EXCEEDED", "Calculated flexural crack width exceeds the selected limit.", "calculated_crack_width_mm", "Revise the actual reinforcement arrangement or section/service response."),
    )
    return completed_result(
        CRACK_WIDTH_CHECK_OPERATION,
        inputs,
        {
            "member_id": request.member_id,
            "station_id": request.station_id,
            "service_action_row_id": request.service_action_row_id,
            "reinforcement_revision_id": request.reinforcement_revision_id,
            "tension_face": request.tension_face,
            "nearest_bar_id": nearest.bar_id,
            "effective_depth_mm": effective_depth,
            "acr_mm": acr,
            "cmin_mm": cmin,
            "neutral_axis_depth_mm": neutral_axis,
            "service_steel_stress_n_per_mm2": request.service_steel_stress_n_per_mm2,
            "elastic_surface_strain": elastic_surface_strain,
            "mean_strain_at_tension_surface": request.mean_strain_at_tension_surface,
            "denominator": denominator,
            "calculated_crack_width_mm": width,
            "limit_mm": limit_mm,
            "utilization": width / limit_mm,
            "passed": passed,
        },
        engineering=EngineeringState.PASS if passed else EngineeringState.FAIL,
        diagnostics=diagnostics,
        provenance=provenance,
    )


__all__ = [
    "CODE_DATA_REVISION",
    "CalculatedDeflectionBasis",
    "CrackWidthCheckRequest",
    "CrackWidthLimitRequest",
    "DeflectionCheckRequest",
    "DeflectionCriterion",
    "DeflectionLimitRequest",
    "DeflectionMethod",
    "DeflectionScreeningBasis",
    "ExposureClass",
    "LimitSource",
    "SupportCondition",
    "check_crack_width",
    "check_deflection",
    "crack_width_limit",
    "deflection_limit",
]
