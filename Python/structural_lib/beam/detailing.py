"""IS 456/IS 13920 beam detailing and constructability operations."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

from .semantics import (
    ApplicabilityState,
    CompletenessState,
    Diagnostic,
    EngineeringState,
    ExecutionState,
    FreshnessState,
    OperationResult,
    Provenance,
    completed_result,
    effective_inputs,
    not_applicable_result,
    not_evaluated_result,
    rejected_result,
)

DEVELOPMENT_LENGTH_OPERATION = "is456.reinforcement.development_length/v1"
ANCHORAGE_CHECK_OPERATION = "is456.beam.anchorage.check/v1"
LAP_CURTAILMENT_CHECK_OPERATION = "is456.beam.lap_curtailment.check/v1"
SEISMIC_DETAILING_CHECK_OPERATION = "is456.beam.seismic_detailing.check/v1"
ARRANGEMENT_CHECK_OPERATION = "structural.reinforcement_arrangement.check/v1"
IS456_CODE_DATA_REVISION = "is456-amd6-wp05-v1"
IS13920_CODE_DATA_REVISION = "is13920-2016-amd2-wp05-v1"


class BarSurface(StrEnum):
    PLAIN = "plain"
    DEFORMED = "deformed"
    FUSION_BONDED_EPOXY_DEFORMED = "fusion_bonded_epoxy_deformed"


class StressState(StrEnum):
    TENSION = "tension"
    COMPRESSION = "compression"


class AnchorageDirection(StrEnum):
    INCREASING_X = "increasing_x"
    DECREASING_X = "decreasing_x"


class AnchorageLocation(StrEnum):
    SIMPLE_SUPPORT = "simple_support"
    CONTINUOUS_SUPPORT = "continuous_support"
    DISCONTINUITY = "discontinuity"


class SpliceKind(StrEnum):
    LAP = "lap"
    QUALIFIED_COUPLER = "qualified_coupler"


class ReinforcementRole(StrEnum):
    TOP_LONGITUDINAL = "top_longitudinal"
    BOTTOM_LONGITUDINAL = "bottom_longitudinal"
    SIDE_LEFT = "side_left"
    SIDE_RIGHT = "side_right"
    CORNER = "corner"


class BeamEnd(StrEnum):
    LEFT = "left"
    RIGHT = "right"


class SeismicApplicability(StrEnum):
    ORDINARY_IS456 = "ordinary_is456"
    IS13920_2016 = "is13920_2016"


@dataclass(frozen=True)
class DevelopmentLengthRequest:
    profile_id: str
    bar_diameter_mm: float
    bar_stress_n_per_mm2: float
    steel_yield_strength_n_per_mm2: float
    concrete_grade_n_per_mm2: float
    bar_surface: BarSurface
    stress_state: StressState
    bundle_size: int = 1
    code_data_revision_id: str = IS456_CODE_DATA_REVISION


@dataclass(frozen=True)
class AnchorageBend:
    bend_id: str
    angle_degrees: int


@dataclass(frozen=True)
class SimpleSupportAnchorageEvidence:
    moment_resistance_nmm: float
    support_shear_n: float
    action_row_ids: tuple[str, ...]


@dataclass(frozen=True)
class AnchoragePath:
    bar_id: str
    critical_section_id: str
    location: AnchorageLocation
    direction: AnchorageDirection
    path_start_x_mm: float
    path_end_x_mm: float
    critical_section_x_mm: float
    support_id: str | None
    support_near_face_x_mm: float | None
    support_centre_x_mm: float | None
    bends: tuple[AnchorageBend, ...]
    bend_schedule_reference: str | None
    development: DevelopmentLengthRequest
    simple_support_evidence: SimpleSupportAnchorageEvidence | None = None


@dataclass(frozen=True)
class AnchorageCheckRequest:
    profile_id: str
    member_id: str
    reinforcement_revision_id: str
    paths: tuple[AnchoragePath, ...]
    code_data_revision_id: str = IS456_CODE_DATA_REVISION


@dataclass(frozen=True)
class QualifiedCheckReference:
    operation_semantic_id: str
    result_id: str
    execution: ExecutionState
    applicability: ApplicabilityState
    engineering: EngineeringState
    completeness: CompletenessState
    freshness: FreshnessState

    def qualifies(self) -> bool:
        return (
            bool(self.operation_semantic_id)
            and bool(self.result_id)
            and self.execution is ExecutionState.COMPLETED
            and self.applicability is ApplicabilityState.APPLICABLE
            and self.engineering is EngineeringState.PASS
            and self.completeness is CompletenessState.COMPLETE_FOR_SCOPE
            and self.freshness is FreshnessState.CURRENT
        )


def _qualifies_as(
    reference: QualifiedCheckReference,
    operation_semantic_id: str,
) -> bool:
    return (
        reference.operation_semantic_id == operation_semantic_id
        and reference.qualifies()
    )


@dataclass(frozen=True)
class LongitudinalBarPath:
    bar_id: str
    bar_mark: str
    role: ReinforcementRole
    diameter_mm: float
    layer: int
    x_from_left_mm: float
    y_from_top_mm: float
    start_station_mm: float
    end_station_mm: float
    design_stress_n_per_mm2: float
    bundle_size: int = 1

    @property
    def area_mm2(self) -> float:
        return math.pi * self.diameter_mm**2 / 4


@dataclass(frozen=True)
class StationSteelDemand:
    station_id: str
    station_x_mm: float
    role: ReinforcementRole
    required_area_mm2: float
    shear_demand_n: float
    shear_capacity_n: float
    action_row_id: str


@dataclass(frozen=True)
class StationZone:
    zone_id: str
    start_x_mm: float
    end_x_mm: float


@dataclass(frozen=True)
class SpliceDetail:
    splice_id: str
    kind: SpliceKind
    bar_ids: tuple[str, ...]
    start_x_mm: float
    end_x_mm: float
    stress_state: StressState
    direct_tension: bool
    percentage_spliced_at_section: float
    stagger_group: str
    coupler_qualification_reference: str | None = None
    installation_reference: str | None = None


@dataclass(frozen=True)
class CurtailmentDetail:
    cutoff_id: str
    bar_id: str
    theoretical_cutoff_x_mm: float
    actual_end_x_mm: float
    direction: AnchorageDirection
    demand_station_id: str
    required_extension_mm: float
    continuing_bar_ids: tuple[str, ...]
    anchorage_check: QualifiedCheckReference
    shear_cutoff_check: QualifiedCheckReference
    extra_links_required: bool
    extra_links_check: QualifiedCheckReference | None = None


@dataclass(frozen=True)
class LapCurtailmentCheckRequest:
    profile_id: str
    member_id: str
    physical_span_id: str
    demand_revision_id: str
    reinforcement_revision_id: str
    member_start_x_mm: float
    member_end_x_mm: float
    effective_depth_mm: float
    concrete_grade_n_per_mm2: float
    steel_yield_strength_n_per_mm2: float
    bar_surface: BarSurface
    bars: tuple[LongitudinalBarPath, ...]
    demands: tuple[StationSteelDemand, ...]
    splices: tuple[SpliceDetail, ...]
    curtailments: tuple[CurtailmentDetail, ...]
    prohibited_splice_zones: tuple[StationZone, ...] = ()
    code_data_revision_id: str = IS456_CODE_DATA_REVISION


@dataclass(frozen=True)
class SeismicLinkZone:
    zone_id: str
    start_x_mm: float
    end_x_mm: float
    spacing_mm: float
    link_diameter_mm: float
    closed: bool
    hook_angle_degrees: int
    first_hoop_offset_from_joint_face_mm: float | None


@dataclass(frozen=True)
class SeismicAnchorageCheck:
    beam_end: BeamEnd
    role: ReinforcementRole
    check: QualifiedCheckReference


@dataclass(frozen=True)
class DependentJointCheck:
    joint_id: str
    check: QualifiedCheckReference


@dataclass(frozen=True)
class SeismicBeamContext:
    system_id: str
    seismic_design_revision_id: str
    member_id: str
    physical_span_id: str
    left_joint_id: str
    right_joint_id: str
    left_joint_face_x_mm: float
    right_joint_face_x_mm: float
    width_mm: float
    overall_depth_mm: float
    effective_depth_mm: float
    concrete_grade_n_per_mm2: float
    steel_yield_strength_n_per_mm2: float
    bars: tuple[LongitudinalBarPath, ...]
    link_zones: tuple[SeismicLinkZone, ...]
    splices: tuple[SpliceDetail, ...]
    imported_analysis_shear_n: float
    gravity_shear_n: float
    left_positive_probable_moment_nmm: float
    left_negative_probable_moment_nmm: float
    right_positive_probable_moment_nmm: float
    right_negative_probable_moment_nmm: float
    provided_shear_capacity_n: float
    shear_check: QualifiedCheckReference
    anchorage_checks: tuple[SeismicAnchorageCheck, ...]
    dependent_joint_checks: tuple[DependentJointCheck, ...]


@dataclass(frozen=True)
class SeismicDetailingCheckRequest:
    profile_id: str
    applicability: SeismicApplicability
    context: SeismicBeamContext | None = None
    code_data_revision_id: str = IS13920_CODE_DATA_REVISION


@dataclass(frozen=True)
class LinkCage:
    link_id: str
    diameter_mm: float
    left_centre_x_mm: float
    right_centre_x_mm: float
    top_centre_y_mm: float
    bottom_centre_y_mm: float
    internal_bend_radius_mm: float
    closed: bool


@dataclass(frozen=True)
class CircularObstacle:
    obstacle_id: str
    x_from_left_mm: float
    y_from_top_mm: float
    diameter_mm: float
    required_clearance_mm: float


@dataclass(frozen=True)
class PlacementOpening:
    opening_id: str
    clear_width_mm: float
    clear_height_mm: float
    sequence_reference: str


@dataclass(frozen=True)
class ReinforcementArrangementCheckRequest:
    profile_id: str
    member_id: str
    station_id: str
    reinforcement_revision_id: str
    section_width_mm: float
    section_depth_mm: float
    nominal_cover_mm: float
    maximum_aggregate_size_mm: float
    bars: tuple[LongitudinalBarPath, ...]
    links: tuple[LinkCage, ...]
    required_roles: tuple[ReinforcementRole, ...]
    vertical_alignment_tolerance_mm: float
    obstacles: tuple[CircularObstacle, ...] = ()
    placement_opening: PlacementOpening | None = None
    require_placement_plan: bool = False
    code_data_revision_id: str = IS456_CODE_DATA_REVISION


def _provenance(
    method: str,
    revision: str,
    *,
    seismic: bool = False,
) -> Provenance:
    references = (
        (
            "IS 13920:2016 with Amendments 1 and 2; bounded beam detailing profile",
            "IS 456:2000 with Amendment 6; development, anchorage, laps and spacing",
        )
        if seismic
        else (
            "IS 456:2000 with Amendment 6 (2024)",
            "IS 456 clauses 26.2, 26.3 and 26.4 normalized for WP05",
        )
    )
    return Provenance(revision, method, references)


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
        "is456-detailing",
        remediation,
    )


def _positive(value: float | None) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(value) and value > 0


def _nonnegative(value: float | None) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(value) and value >= 0


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
        _diagnostic(
            operation,
            "EVIDENCE.REQUIRED",
            message,
            field,
            "Supply the named detailing evidence.",
        ),
        provenance=provenance,
    )


def _bond_stress_plain_tension(concrete_grade: float) -> float | None:
    if concrete_grade == 20:
        return 1.2
    if concrete_grade == 25:
        return 1.4
    if concrete_grade == 30:
        return 1.5
    if concrete_grade == 35:
        return 1.7
    if concrete_grade >= 40:
        return 1.9
    return None


def development_length(request: DevelopmentLengthRequest) -> OperationResult:
    inputs = effective_inputs(request=request)
    provenance = _provenance(
        "is456-development-length-amd6-wp05-v1",
        request.code_data_revision_id,
    )
    if (
        not request.profile_id
        or request.code_data_revision_id != IS456_CODE_DATA_REVISION
        or not _positive(request.bar_diameter_mm)
        or not _positive(request.bar_stress_n_per_mm2)
        or not _positive(request.steel_yield_strength_n_per_mm2)
        or not _positive(request.concrete_grade_n_per_mm2)
        or not isinstance(request.bar_surface, BarSurface)
        or not isinstance(request.stress_state, StressState)
        or request.bundle_size not in (1, 2, 3, 4)
    ):
        return rejected_result(
            DEVELOPMENT_LENGTH_OPERATION,
            inputs,
            (
                _diagnostic(
                    DEVELOPMENT_LENGTH_OPERATION,
                    "INPUT.INVALID",
                    "Development length requires explicit positive material, bar, stress-state, surface, and bundle inputs.",
                    "request",
                    "Correct the declared development-length basis.",
                ),
            ),
            provenance=provenance,
        )
    if request.bar_stress_n_per_mm2 > (
        0.87 * request.steel_yield_strength_n_per_mm2 + 1e-12
    ):
        return rejected_result(
            DEVELOPMENT_LENGTH_OPERATION,
            inputs,
            (
                _diagnostic(
                    DEVELOPMENT_LENGTH_OPERATION,
                    "STRESS.OUTSIDE_PROFILE",
                    "Bar stress exceeds the bounded 0.87fy limit-state profile.",
                    "bar_stress_n_per_mm2",
                    "Supply the actual supported bar stress up to 0.87fy.",
                ),
            ),
            provenance=provenance,
        )
    plain_tension = _bond_stress_plain_tension(request.concrete_grade_n_per_mm2)
    if plain_tension is None:
        return not_applicable_result(
            DEVELOPMENT_LENGTH_OPERATION,
            inputs,
            _diagnostic(
                DEVELOPMENT_LENGTH_OPERATION,
                "PROFILE.CONCRETE_GRADE",
                "The WP05 IS 456 profile supports M20, M25, M30, M35, and M40 or higher.",
                "concrete_grade_n_per_mm2",
                "Use a supported concrete grade or another code profile.",
                "information",
            ),
            provenance=provenance,
        )

    surface_factor = {
        BarSurface.PLAIN: 1.0,
        BarSurface.DEFORMED: 1.6,
        BarSurface.FUSION_BONDED_EPOXY_DEFORMED: 1.6 * 0.8,
    }[request.bar_surface]
    compression_factor = (
        1.25 if request.stress_state is StressState.COMPRESSION else 1.0
    )
    design_bond_stress = plain_tension * surface_factor * compression_factor
    unbundled = (
        request.bar_diameter_mm
        * request.bar_stress_n_per_mm2
        / (4 * design_bond_stress)
    )
    bundle_factor = {1: 1.0, 2: 1.1, 3: 1.2, 4: 1.33}[request.bundle_size]
    required = unbundled * bundle_factor
    return completed_result(
        DEVELOPMENT_LENGTH_OPERATION,
        inputs,
        {
            "plain_bar_tension_bond_stress_n_per_mm2": plain_tension,
            "surface_factor": surface_factor,
            "stress_state_factor": compression_factor,
            "design_bond_stress_n_per_mm2": design_bond_stress,
            "unbundled_development_length_mm": unbundled,
            "bundle_factor": bundle_factor,
            "required_development_length_mm": required,
        },
        provenance=provenance,
    )


def _anchorage_bend_value(
    path: AnchoragePath,
) -> tuple[float, Diagnostic | None]:
    if not path.bends:
        return 0.0, None
    if not path.bend_schedule_reference:
        return 0.0, _diagnostic(
            ANCHORAGE_CHECK_OPERATION,
            "BEND.EVIDENCE",
            "Bend credit requires a fabrication schedule reference.",
            f"paths[{path.bar_id}].bend_schedule_reference",
            "Bind the bends to the current fabrication detail.",
        )
    if any(
        not bend.bend_id or bend.angle_degrees not in (45, 90, 135, 180)
        for bend in path.bends
    ):
        return 0.0, _diagnostic(
            ANCHORAGE_CHECK_OPERATION,
            "BEND.INVALID",
            "Every credited bend requires identity and a supported 45-degree increment.",
            f"paths[{path.bar_id}].bends",
            "Correct the actual bend schedule.",
        )
    diameter = path.development.bar_diameter_mm
    value = math.fsum(4 * diameter * bend.angle_degrees / 45 for bend in path.bends)
    return min(16 * diameter, value), None


def check_anchorage(request: AnchorageCheckRequest) -> OperationResult:
    inputs = effective_inputs(request=request)
    provenance = _provenance(
        "is456-anchorage-path-check-wp05-v1",
        request.code_data_revision_id,
    )
    if (
        not request.profile_id
        or not request.member_id
        or not request.reinforcement_revision_id
        or request.code_data_revision_id != IS456_CODE_DATA_REVISION
    ):
        return _not_evaluated(
            ANCHORAGE_CHECK_OPERATION,
            inputs,
            provenance,
            "Member and reinforcement-revision identity is required.",
            "identity",
        )
    if not request.paths:
        return _not_evaluated(
            ANCHORAGE_CHECK_OPERATION,
            inputs,
            provenance,
            "Actual longitudinal bar-end paths are required.",
            "paths",
        )
    bar_ids = [path.bar_id for path in request.paths]
    if any(not item for item in bar_ids) or len(bar_ids) != len(set(bar_ids)):
        return rejected_result(
            ANCHORAGE_CHECK_OPERATION,
            inputs,
            (
                _diagnostic(
                    ANCHORAGE_CHECK_OPERATION,
                    "PATH.IDENTITY",
                    "Anchorage paths require unique nonblank bar ids.",
                    "paths",
                    "Correct the bar-path identities.",
                ),
            ),
            provenance=provenance,
        )

    checks: list[dict[str, object]] = []
    diagnostics: list[Diagnostic] = []
    for path in request.paths:
        if (
            not path.critical_section_id
            or not isinstance(path.location, AnchorageLocation)
            or not isinstance(path.direction, AnchorageDirection)
            or not all(
                math.isfinite(value)
                for value in (
                    path.path_start_x_mm,
                    path.path_end_x_mm,
                    path.critical_section_x_mm,
                )
            )
            or path.path_start_x_mm >= path.path_end_x_mm
            or not (
                path.path_start_x_mm <= path.critical_section_x_mm <= path.path_end_x_mm
            )
        ):
            return rejected_result(
                ANCHORAGE_CHECK_OPERATION,
                inputs,
                (
                    _diagnostic(
                        ANCHORAGE_CHECK_OPERATION,
                        "PATH.GEOMETRY",
                        "Each bar needs an ordered path, critical section, direction, and location.",
                        f"paths[{path.bar_id}]",
                        "Correct the actual bar path and critical section.",
                    ),
                ),
                provenance=provenance,
            )
        at_support = path.location in (
            AnchorageLocation.SIMPLE_SUPPORT,
            AnchorageLocation.CONTINUOUS_SUPPORT,
        )
        support_values = (
            path.support_near_face_x_mm,
            path.support_centre_x_mm,
        )
        if at_support and (
            not path.support_id
            or any(
                value is None or not math.isfinite(value) for value in support_values
            )
            or not math.isclose(
                path.critical_section_x_mm,
                float(path.support_near_face_x_mm),
                abs_tol=1e-9,
            )
        ):
            return rejected_result(
                ANCHORAGE_CHECK_OPERATION,
                inputs,
                (
                    _diagnostic(
                        ANCHORAGE_CHECK_OPERATION,
                        "SUPPORT.FACE_REQUIRED",
                        "Support anchorage requires separate support identity, near-face, and centre coordinates; the critical section is the near face.",
                        f"paths[{path.bar_id}].support",
                        "Supply the resolved physical support geometry.",
                    ),
                ),
                provenance=provenance,
            )
        bend_value, bend_error = _anchorage_bend_value(path)
        if bend_error is not None:
            return rejected_result(
                ANCHORAGE_CHECK_OPERATION,
                inputs,
                (bend_error,),
                provenance=provenance,
            )
        development = development_length(path.development)
        if development.execution is not ExecutionState.COMPLETED:
            return rejected_result(
                ANCHORAGE_CHECK_OPERATION,
                inputs,
                development.diagnostics,
                provenance=provenance,
            )
        if development.applicability is not ApplicabilityState.APPLICABLE:
            return not_applicable_result(
                ANCHORAGE_CHECK_OPERATION,
                inputs,
                development.diagnostics[0],
                provenance=provenance,
            )
        required = float(development.outputs["required_development_length_mm"])
        if path.direction is AnchorageDirection.INCREASING_X:
            straight = path.path_end_x_mm - path.critical_section_x_mm
        else:
            straight = path.critical_section_x_mm - path.path_start_x_mm
        available = straight + bend_value
        criterion = "direct_development"
        moment_shear_contribution = 0.0
        anchorage_beyond_centre = 0.0
        if path.location is AnchorageLocation.SIMPLE_SUPPORT:
            evidence = path.simple_support_evidence
            if (
                evidence is None
                or not _nonnegative(evidence.moment_resistance_nmm)
                or not _positive(evidence.support_shear_n)
                or not evidence.action_row_ids
                or not all(evidence.action_row_ids)
            ):
                return _not_evaluated(
                    ANCHORAGE_CHECK_OPERATION,
                    inputs,
                    provenance,
                    "Simple-support anchorage requires moment resistance, support shear, and source action rows.",
                    f"paths[{path.bar_id}].simple_support_evidence",
                )
            centre = float(path.support_centre_x_mm)
            anchorage_beyond_centre = (
                path.path_end_x_mm - centre
                if path.direction is AnchorageDirection.INCREASING_X
                else centre - path.path_start_x_mm
            )
            anchorage_beyond_centre = max(0.0, anchorage_beyond_centre) + bend_value
            moment_shear_contribution = (
                evidence.moment_resistance_nmm / evidence.support_shear_n
            )
            available = moment_shear_contribution + anchorage_beyond_centre
            criterion = "simple_support_moment_shear_plus_lo"
        passed = required <= available + 1e-9
        if not passed:
            diagnostics.append(
                _diagnostic(
                    ANCHORAGE_CHECK_OPERATION,
                    "ANCHORAGE.DEFICIT",
                    "Actual straight path and credited bends do not satisfy the applicable development criterion.",
                    f"paths[{path.bar_id}]",
                    "Extend the bar path or revise the supported bend/anchorage detail.",
                )
            )
        checks.append(
            {
                "bar_id": path.bar_id,
                "critical_section_id": path.critical_section_id,
                "location": path.location,
                "criterion": criterion,
                "development_result_id": development.result_id,
                "required_development_length_mm": required,
                "available_straight_length_mm": straight,
                "bend_anchorage_value_mm": bend_value,
                "moment_shear_contribution_mm": moment_shear_contribution,
                "anchorage_beyond_support_centre_mm": anchorage_beyond_centre,
                "available_for_criterion_mm": available,
                "deficit_mm": max(0.0, required - available),
                "utilization": required / available if available > 0 else None,
                "passed": passed,
            }
        )

    passed = not diagnostics
    utilizations = [
        float(check["utilization"])
        for check in checks
        if check["utilization"] is not None
    ]
    return completed_result(
        ANCHORAGE_CHECK_OPERATION,
        inputs,
        {
            "member_id": request.member_id,
            "reinforcement_revision_id": request.reinforcement_revision_id,
            "checks": checks,
            "governing_utilization": max(utilizations) if utilizations else None,
            "passed": passed,
        },
        engineering=EngineeringState.PASS if passed else EngineeringState.FAIL,
        diagnostics=diagnostics,
        provenance=provenance,
    )


def _intervals_overlap(
    first_start: float,
    first_end: float,
    second_start: float,
    second_end: float,
) -> bool:
    return max(first_start, second_start) < min(first_end, second_end)


def _validate_bar_path(bar: LongitudinalBarPath) -> bool:
    return (
        bool(bar.bar_id)
        and bool(bar.bar_mark)
        and isinstance(bar.role, ReinforcementRole)
        and _positive(bar.diameter_mm)
        and isinstance(bar.layer, int)
        and bar.layer >= 1
        and all(
            math.isfinite(value)
            for value in (
                bar.x_from_left_mm,
                bar.y_from_top_mm,
                bar.start_station_mm,
                bar.end_station_mm,
                bar.design_stress_n_per_mm2,
            )
        )
        and bar.start_station_mm < bar.end_station_mm
        and bar.design_stress_n_per_mm2 >= 0
        and bar.bundle_size in (1, 2, 3, 4)
    )


def _lap_required_length(
    request: LapCurtailmentCheckRequest,
    bar: LongitudinalBarPath,
    stress_state: StressState,
    direct_tension: bool,
) -> tuple[float | None, OperationResult]:
    development = development_length(
        DevelopmentLengthRequest(
            profile_id=request.profile_id,
            bar_diameter_mm=bar.diameter_mm,
            bar_stress_n_per_mm2=0.87 * request.steel_yield_strength_n_per_mm2,
            steel_yield_strength_n_per_mm2=(request.steel_yield_strength_n_per_mm2),
            concrete_grade_n_per_mm2=request.concrete_grade_n_per_mm2,
            bar_surface=request.bar_surface,
            stress_state=stress_state,
            bundle_size=bar.bundle_size,
            code_data_revision_id=request.code_data_revision_id,
        )
    )
    if development.execution is not ExecutionState.COMPLETED:
        return None, development
    if development.applicability is not ApplicabilityState.APPLICABLE:
        return None, development
    required_development = float(development.outputs["required_development_length_mm"])
    if stress_state is StressState.COMPRESSION:
        return max(required_development, 24 * bar.diameter_mm), development
    development_factor = 2.0 if direct_tension else 1.0
    return (
        max(development_factor * required_development, 30 * bar.diameter_mm),
        development,
    )


def check_laps_and_curtailment(
    request: LapCurtailmentCheckRequest,
) -> OperationResult:
    inputs = effective_inputs(request=request)
    provenance = _provenance(
        "is456-lap-curtailment-evidence-check-wp05-v1",
        request.code_data_revision_id,
    )
    if (
        not request.profile_id
        or not request.member_id
        or not request.physical_span_id
        or not request.demand_revision_id
        or not request.reinforcement_revision_id
        or request.code_data_revision_id != IS456_CODE_DATA_REVISION
        or not _positive(request.effective_depth_mm)
        or not _positive(request.concrete_grade_n_per_mm2)
        or not _positive(request.steel_yield_strength_n_per_mm2)
        or not isinstance(request.bar_surface, BarSurface)
        or not all(
            math.isfinite(value)
            for value in (request.member_start_x_mm, request.member_end_x_mm)
        )
        or request.member_start_x_mm >= request.member_end_x_mm
    ):
        return rejected_result(
            LAP_CURTAILMENT_CHECK_OPERATION,
            inputs,
            (
                _diagnostic(
                    LAP_CURTAILMENT_CHECK_OPERATION,
                    "INPUT.INVALID",
                    "The lap and curtailment check requires complete identities, member geometry, materials, and revision binding.",
                    "request",
                    "Correct the declared member and material basis.",
                ),
            ),
            provenance=provenance,
        )
    if not request.bars or not request.demands:
        return _not_evaluated(
            LAP_CURTAILMENT_CHECK_OPERATION,
            inputs,
            provenance,
            "Actual bar paths and the current station steel-demand envelope are required.",
            "bars,demands",
        )
    if not request.splices and not request.curtailments:
        return _not_evaluated(
            LAP_CURTAILMENT_CHECK_OPERATION,
            inputs,
            provenance,
            "At least one actual splice or curtailment detail is required.",
            "splices,curtailments",
        )

    bar_ids = [bar.bar_id for bar in request.bars]
    demand_ids = [demand.station_id for demand in request.demands]
    detail_ids = [splice.splice_id for splice in request.splices] + [
        cutoff.cutoff_id for cutoff in request.curtailments
    ]
    if (
        any(not _validate_bar_path(bar) for bar in request.bars)
        or len(bar_ids) != len(set(bar_ids))
        or len(demand_ids) != len(set(demand_ids))
        or any(not item for item in demand_ids + detail_ids)
        or len(detail_ids) != len(set(detail_ids))
    ):
        return rejected_result(
            LAP_CURTAILMENT_CHECK_OPERATION,
            inputs,
            (
                _diagnostic(
                    LAP_CURTAILMENT_CHECK_OPERATION,
                    "DETAIL.IDENTITY_OR_GEOMETRY",
                    "Bars, demands, splices, and curtailments require valid geometry and unique identities.",
                    "bars,demands,splices,curtailments",
                    "Correct the actual detailing records.",
                ),
            ),
            provenance=provenance,
        )
    bar_by_id = {bar.bar_id: bar for bar in request.bars}
    demand_by_id = {demand.station_id: demand for demand in request.demands}
    if any(
        not demand.action_row_id
        or not isinstance(demand.role, ReinforcementRole)
        or not (
            request.member_start_x_mm <= demand.station_x_mm <= request.member_end_x_mm
        )
        or not _nonnegative(demand.required_area_mm2)
        or not _nonnegative(demand.shear_demand_n)
        or not _nonnegative(demand.shear_capacity_n)
        for demand in request.demands
    ):
        return rejected_result(
            LAP_CURTAILMENT_CHECK_OPERATION,
            inputs,
            (
                _diagnostic(
                    LAP_CURTAILMENT_CHECK_OPERATION,
                    "DEMAND.INVALID",
                    "Each demand station requires a role, source action row, member station, steel area, shear demand, and shear capacity.",
                    "demands",
                    "Correct the station demand envelope.",
                ),
            ),
            provenance=provenance,
        )
    if any(
        not zone.zone_id
        or not all(math.isfinite(value) for value in (zone.start_x_mm, zone.end_x_mm))
        or zone.start_x_mm >= zone.end_x_mm
        for zone in request.prohibited_splice_zones
    ):
        return rejected_result(
            LAP_CURTAILMENT_CHECK_OPERATION,
            inputs,
            (
                _diagnostic(
                    LAP_CURTAILMENT_CHECK_OPERATION,
                    "ZONE.INVALID",
                    "Every prohibited splice zone requires identity and an ordered interval.",
                    "prohibited_splice_zones",
                    "Correct the prohibited-zone schedule.",
                ),
            ),
            provenance=provenance,
        )

    diagnostics: list[Diagnostic] = []
    splice_checks: list[dict[str, object]] = []
    for splice in request.splices:
        if (
            not isinstance(splice.kind, SpliceKind)
            or not isinstance(splice.stress_state, StressState)
            or not splice.bar_ids
            or len(splice.bar_ids) != len(set(splice.bar_ids))
            or any(bar_id not in bar_by_id for bar_id in splice.bar_ids)
            or not all(
                math.isfinite(value) for value in (splice.start_x_mm, splice.end_x_mm)
            )
            or splice.start_x_mm >= splice.end_x_mm
            or not (0 < splice.percentage_spliced_at_section <= 100)
            or not splice.stagger_group
            or (
                splice.direct_tension and splice.stress_state is not StressState.TENSION
            )
            or not (
                request.member_start_x_mm
                <= splice.start_x_mm
                < splice.end_x_mm
                <= request.member_end_x_mm
            )
        ):
            return rejected_result(
                LAP_CURTAILMENT_CHECK_OPERATION,
                inputs,
                (
                    _diagnostic(
                        LAP_CURTAILMENT_CHECK_OPERATION,
                        "SPLICE.INVALID",
                        "Every splice requires an ordered zone, actual bar ids, stress state, percentage, and stagger group.",
                        f"splices[{splice.splice_id}]",
                        "Correct the splice schedule record.",
                    ),
                ),
                provenance=provenance,
            )
        zone_allowed = not any(
            _intervals_overlap(
                splice.start_x_mm,
                splice.end_x_mm,
                zone.start_x_mm,
                zone.end_x_mm,
            )
            for zone in request.prohibited_splice_zones
        )
        percentage_allowed = splice.percentage_spliced_at_section <= 50
        actual_length = splice.end_x_mm - splice.start_x_mm
        bars = [bar_by_id[bar_id] for bar_id in splice.bar_ids]
        maximum_diameter = max(bar.diameter_mm for bar in bars)
        required_length: float | None = None
        development_result_ids: list[str] = []
        lap_permitted = (
            all(bar.diameter_mm <= 36 for bar in bars)
            if splice.kind is SpliceKind.LAP
            else True
        )
        qualification_ok = True
        if splice.kind is SpliceKind.LAP:
            required_values: list[float] = []
            for bar in bars:
                required, development = _lap_required_length(
                    request,
                    bar,
                    splice.stress_state,
                    splice.direct_tension,
                )
                if required is None:
                    if development.applicability is ApplicabilityState.NOT_APPLICABLE:
                        return not_applicable_result(
                            LAP_CURTAILMENT_CHECK_OPERATION,
                            inputs,
                            development.diagnostics[0],
                            provenance=provenance,
                        )
                    return rejected_result(
                        LAP_CURTAILMENT_CHECK_OPERATION,
                        inputs,
                        development.diagnostics,
                        provenance=provenance,
                    )
                required_values.append(required)
                development_result_ids.append(development.result_id)
            required_length = max(required_values)
            qualification_ok = actual_length + 1e-9 >= required_length
        else:
            qualification_ok = bool(
                splice.coupler_qualification_reference and splice.installation_reference
            )
        passed = (
            zone_allowed and percentage_allowed and lap_permitted and qualification_ok
        )
        if not passed:
            diagnostics.append(
                _diagnostic(
                    LAP_CURTAILMENT_CHECK_OPERATION,
                    "SPLICE.NONCOMPLIANT",
                    "The splice fails its length or qualification, permitted bar diameter, percentage, staggering, or zone rule.",
                    f"splices[{splice.splice_id}]",
                    "Revise the splice type, length, location, percentage, or qualification evidence.",
                )
            )
        splice_checks.append(
            {
                "splice_id": splice.splice_id,
                "kind": splice.kind,
                "bar_ids": splice.bar_ids,
                "maximum_bar_diameter_mm": maximum_diameter,
                "actual_length_mm": actual_length,
                "required_length_mm": required_length,
                "development_result_ids": development_result_ids,
                "lap_permitted_for_diameter": lap_permitted,
                "percentage_allowed": percentage_allowed,
                "stagger_group": splice.stagger_group,
                "zone_allowed": zone_allowed,
                "qualification_and_installation_evidence": qualification_ok,
                "passed": passed,
            }
        )

    curtailment_checks: list[dict[str, object]] = []
    for cutoff in request.curtailments:
        if (
            cutoff.bar_id not in bar_by_id
            or cutoff.demand_station_id not in demand_by_id
            or not isinstance(cutoff.direction, AnchorageDirection)
            or not _positive(cutoff.required_extension_mm)
            or not cutoff.continuing_bar_ids
            or len(cutoff.continuing_bar_ids) != len(set(cutoff.continuing_bar_ids))
            or any(bar_id not in bar_by_id for bar_id in cutoff.continuing_bar_ids)
            or cutoff.bar_id in cutoff.continuing_bar_ids
            or not isinstance(cutoff.extra_links_required, bool)
            or not all(
                math.isfinite(value)
                for value in (
                    cutoff.theoretical_cutoff_x_mm,
                    cutoff.actual_end_x_mm,
                )
            )
        ):
            return rejected_result(
                LAP_CURTAILMENT_CHECK_OPERATION,
                inputs,
                (
                    _diagnostic(
                        LAP_CURTAILMENT_CHECK_OPERATION,
                        "CURTAILMENT.INVALID",
                        "Every curtailment requires its actual bar, demand station, direction, required extension, and identified continuing bars.",
                        f"curtailments[{cutoff.cutoff_id}]",
                        "Correct the curtailment schedule and criterion binding.",
                    ),
                ),
                provenance=provenance,
            )
        if cutoff.direction is AnchorageDirection.INCREASING_X:
            actual_extension = cutoff.actual_end_x_mm - cutoff.theoretical_cutoff_x_mm
        else:
            actual_extension = cutoff.theoretical_cutoff_x_mm - cutoff.actual_end_x_mm
        demand = demand_by_id[cutoff.demand_station_id]
        continuing = [bar_by_id[bar_id] for bar_id in cutoff.continuing_bar_ids]
        continuing_area = math.fsum(
            bar.area_mm2
            for bar in continuing
            if bar.role is demand.role
            and bar.start_station_mm <= demand.station_x_mm <= bar.end_station_mm
        )
        extension_ok = actual_extension + 1e-9 >= cutoff.required_extension_mm
        remaining_steel_ok = continuing_area + 1e-9 >= demand.required_area_mm2
        anchorage_ok = _qualifies_as(
            cutoff.anchorage_check,
            ANCHORAGE_CHECK_OPERATION,
        )
        shear_ok = _qualifies_as(
            cutoff.shear_cutoff_check,
            "is456.beam.shear.check/v1",
        )
        extra_links_ok = not cutoff.extra_links_required or (
            cutoff.extra_links_check is not None
            and _qualifies_as(
                cutoff.extra_links_check,
                "is456.beam.shear.check/v1",
            )
        )
        passed = all(
            (
                extension_ok,
                remaining_steel_ok,
                anchorage_ok,
                shear_ok,
                extra_links_ok,
            )
        )
        if not passed:
            diagnostics.append(
                _diagnostic(
                    LAP_CURTAILMENT_CHECK_OPERATION,
                    "CURTAILMENT.NONCOMPLIANT",
                    "The actual termination fails extension, remaining-steel, anchorage, shear-at-cutoff, or extra-link evidence.",
                    f"curtailments[{cutoff.cutoff_id}]",
                    "Revise the termination or supply passing current detailing checks.",
                )
            )
        curtailment_checks.append(
            {
                "cutoff_id": cutoff.cutoff_id,
                "bar_id": cutoff.bar_id,
                "demand_station_id": cutoff.demand_station_id,
                "action_row_id": demand.action_row_id,
                "actual_extension_mm": actual_extension,
                "required_extension_mm": cutoff.required_extension_mm,
                "extension_ok": extension_ok,
                "continuing_bar_ids": cutoff.continuing_bar_ids,
                "continuing_area_mm2": continuing_area,
                "required_area_mm2": demand.required_area_mm2,
                "remaining_steel_ok": remaining_steel_ok,
                "anchorage_result_id": cutoff.anchorage_check.result_id,
                "anchorage_ok": anchorage_ok,
                "shear_cutoff_result_id": cutoff.shear_cutoff_check.result_id,
                "shear_cutoff_ok": shear_ok,
                "extra_links_required": cutoff.extra_links_required,
                "extra_links_result_id": (
                    cutoff.extra_links_check.result_id
                    if cutoff.extra_links_check is not None
                    else None
                ),
                "extra_links_ok": extra_links_ok,
                "passed": passed,
            }
        )

    passed = not diagnostics
    return completed_result(
        LAP_CURTAILMENT_CHECK_OPERATION,
        inputs,
        {
            "member_id": request.member_id,
            "physical_span_id": request.physical_span_id,
            "demand_revision_id": request.demand_revision_id,
            "reinforcement_revision_id": request.reinforcement_revision_id,
            "splice_checks": splice_checks,
            "curtailment_checks": curtailment_checks,
            "passed": passed,
        },
        engineering=EngineeringState.PASS if passed else EngineeringState.FAIL,
        diagnostics=diagnostics,
        provenance=provenance,
    )


def _active_role_bars(
    bars: tuple[LongitudinalBarPath, ...],
    role: ReinforcementRole,
    station_x_mm: float,
) -> list[LongitudinalBarPath]:
    return [
        bar
        for bar in bars
        if bar.role is role
        and bar.start_station_mm <= station_x_mm <= bar.end_station_mm
    ]


def check_seismic_detailing(
    request: SeismicDetailingCheckRequest,
) -> OperationResult:
    inputs = effective_inputs(request=request)
    provenance = _provenance(
        "is13920-beam-detailing-amd2-wp05-v1",
        request.code_data_revision_id,
        seismic=True,
    )
    if (
        not request.profile_id
        or not isinstance(request.applicability, SeismicApplicability)
        or request.code_data_revision_id != IS13920_CODE_DATA_REVISION
    ):
        return rejected_result(
            SEISMIC_DETAILING_CHECK_OPERATION,
            inputs,
            (
                _diagnostic(
                    SEISMIC_DETAILING_CHECK_OPERATION,
                    "INPUT.INVALID",
                    "The seismic detailing request requires a supported profile, applicability, and exact code-data revision.",
                    "request",
                    "Correct the seismic detailing profile binding.",
                ),
            ),
            provenance=provenance,
        )
    if request.applicability is SeismicApplicability.ORDINARY_IS456:
        return not_applicable_result(
            SEISMIC_DETAILING_CHECK_OPERATION,
            inputs,
            _diagnostic(
                SEISMIC_DETAILING_CHECK_OPERATION,
                "PROFILE.NOT_SEISMIC",
                "The selected member is outside the IS 13920 beam detailing profile.",
                "applicability",
                "Run the applicable ordinary IS 456 detailing checks.",
                "information",
            ),
            provenance=provenance,
        )
    context = request.context
    if context is None:
        return _not_evaluated(
            SEISMIC_DETAILING_CHECK_OPERATION,
            inputs,
            provenance,
            "A complete member, system, joint, reinforcement, and capacity-design context is required.",
            "context",
        )
    identity_values = (
        context.system_id,
        context.seismic_design_revision_id,
        context.member_id,
        context.physical_span_id,
        context.left_joint_id,
        context.right_joint_id,
    )
    numeric_values = (
        context.left_joint_face_x_mm,
        context.right_joint_face_x_mm,
        context.width_mm,
        context.overall_depth_mm,
        context.effective_depth_mm,
        context.concrete_grade_n_per_mm2,
        context.steel_yield_strength_n_per_mm2,
        context.imported_analysis_shear_n,
        context.gravity_shear_n,
        context.left_positive_probable_moment_nmm,
        context.left_negative_probable_moment_nmm,
        context.right_positive_probable_moment_nmm,
        context.right_negative_probable_moment_nmm,
        context.provided_shear_capacity_n,
    )
    if (
        any(not value for value in identity_values)
        or not all(math.isfinite(value) for value in numeric_values)
        or context.left_joint_face_x_mm >= context.right_joint_face_x_mm
        or not all(
            _positive(value)
            for value in (
                context.width_mm,
                context.overall_depth_mm,
                context.effective_depth_mm,
                context.concrete_grade_n_per_mm2,
                context.steel_yield_strength_n_per_mm2,
                context.provided_shear_capacity_n,
            )
        )
        or context.effective_depth_mm >= context.overall_depth_mm
        or any(
            value < 0
            for value in (
                context.left_positive_probable_moment_nmm,
                context.left_negative_probable_moment_nmm,
                context.right_positive_probable_moment_nmm,
                context.right_negative_probable_moment_nmm,
            )
        )
    ):
        return rejected_result(
            SEISMIC_DETAILING_CHECK_OPERATION,
            inputs,
            (
                _diagnostic(
                    SEISMIC_DETAILING_CHECK_OPERATION,
                    "CONTEXT.INVALID",
                    "The seismic member requires valid identities, joint faces, section/material values, actions, strengths, and effective depth.",
                    "context",
                    "Correct the resolved seismic beam context.",
                ),
            ),
            provenance=provenance,
        )
    if not any(
        math.isclose(context.steel_yield_strength_n_per_mm2, grade)
        for grade in (415.0, 500.0, 550.0)
    ):
        return not_applicable_result(
            SEISMIC_DETAILING_CHECK_OPERATION,
            inputs,
            _diagnostic(
                SEISMIC_DETAILING_CHECK_OPERATION,
                "PROFILE.STEEL_GRADE",
                "The WP05 seismic profile supports Fe 415, Fe 500, and Fe 550 reinforcement.",
                "context.steel_yield_strength_n_per_mm2",
                "Select a supported grade or another qualified profile.",
                "information",
            ),
            provenance=provenance,
        )
    if (
        not context.bars
        or not context.link_zones
        or len(context.anchorage_checks) < 4
        or len(context.dependent_joint_checks) < 2
    ):
        return _not_evaluated(
            SEISMIC_DETAILING_CHECK_OPERATION,
            inputs,
            provenance,
            "Actual bars, link zones, four face anchorage results, and both dependent joint checks are required.",
            "context.bars,context.link_zones,context.anchorage_checks,context.dependent_joint_checks",
        )
    expected_anchorage_locations = {
        (BeamEnd.LEFT, ReinforcementRole.TOP_LONGITUDINAL),
        (BeamEnd.LEFT, ReinforcementRole.BOTTOM_LONGITUDINAL),
        (BeamEnd.RIGHT, ReinforcementRole.TOP_LONGITUDINAL),
        (BeamEnd.RIGHT, ReinforcementRole.BOTTOM_LONGITUDINAL),
    }
    actual_anchorage_locations = [
        (binding.beam_end, binding.role) for binding in context.anchorage_checks
    ]
    actual_joint_ids = [binding.joint_id for binding in context.dependent_joint_checks]
    if (
        len(actual_anchorage_locations) != 4
        or set(actual_anchorage_locations) != expected_anchorage_locations
        or len(actual_joint_ids) != 2
        or set(actual_joint_ids) != {context.left_joint_id, context.right_joint_id}
    ):
        return rejected_result(
            SEISMIC_DETAILING_CHECK_OPERATION,
            inputs,
            (
                _diagnostic(
                    SEISMIC_DETAILING_CHECK_OPERATION,
                    "DEPENDENCY.BINDING_INVALID",
                    "Seismic dependencies must bind one anchorage result to each beam-end/face pair and one joint result to each named joint.",
                    "context.anchorage_checks,context.dependent_joint_checks",
                    "Supply exactly left/right top/bottom anchorage bindings and the named left/right joint bindings.",
                ),
            ),
            provenance=provenance,
        )
    if any(not _validate_bar_path(bar) for bar in context.bars):
        return rejected_result(
            SEISMIC_DETAILING_CHECK_OPERATION,
            inputs,
            (
                _diagnostic(
                    SEISMIC_DETAILING_CHECK_OPERATION,
                    "BAR.INVALID",
                    "Every seismic longitudinal bar requires valid identity, role, geometry, and stress data.",
                    "context.bars",
                    "Correct the actual seismic reinforcement paths.",
                ),
            ),
            provenance=provenance,
        )
    bar_ids = [bar.bar_id for bar in context.bars]
    zone_ids = [zone.zone_id for zone in context.link_zones]
    splice_ids = [splice.splice_id for splice in context.splices]
    if (
        len(bar_ids) != len(set(bar_ids))
        or any(not item for item in zone_ids + splice_ids)
        or len(zone_ids) != len(set(zone_ids))
        or len(splice_ids) != len(set(splice_ids))
        or any(
            not all(
                math.isfinite(value)
                for value in (
                    zone.start_x_mm,
                    zone.end_x_mm,
                    zone.spacing_mm,
                    zone.link_diameter_mm,
                )
            )
            or zone.start_x_mm >= zone.end_x_mm
            or not _positive(zone.spacing_mm)
            or not _positive(zone.link_diameter_mm)
            or zone.first_hoop_offset_from_joint_face_mm is not None
            and not _nonnegative(zone.first_hoop_offset_from_joint_face_mm)
            for zone in context.link_zones
        )
        or any(
            not isinstance(splice.kind, SpliceKind)
            or not isinstance(splice.stress_state, StressState)
            or not splice.bar_ids
            or any(bar_id not in bar_ids for bar_id in splice.bar_ids)
            or not all(
                math.isfinite(value) for value in (splice.start_x_mm, splice.end_x_mm)
            )
            or splice.start_x_mm >= splice.end_x_mm
            or not (0 < splice.percentage_spliced_at_section <= 100)
            or not splice.stagger_group
            for splice in context.splices
        )
    ):
        return rejected_result(
            SEISMIC_DETAILING_CHECK_OPERATION,
            inputs,
            (
                _diagnostic(
                    SEISMIC_DETAILING_CHECK_OPERATION,
                    "DETAIL.INVALID",
                    "Seismic bars, link zones, and splices require valid unique identities and ordered physical geometry.",
                    "context.bars,context.link_zones,context.splices",
                    "Correct the actual seismic reinforcement detail.",
                ),
            ),
            provenance=provenance,
        )

    diagnostics: list[Diagnostic] = []
    rule_checks: list[dict[str, object]] = []

    def add_rule(
        rule_id: str,
        passed: bool,
        actual: object,
        limit: object,
        field: str,
        message: str,
    ) -> None:
        rule_checks.append(
            {
                "rule_id": rule_id,
                "actual": actual,
                "limit": limit,
                "passed": passed,
            }
        )
        if not passed:
            diagnostics.append(
                _diagnostic(
                    SEISMIC_DETAILING_CHECK_OPERATION,
                    f"SEISMIC.{rule_id}",
                    message,
                    field,
                    "Revise the actual seismic detail or its qualified dependent evidence.",
                )
            )

    width_depth_ratio = context.width_mm / context.overall_depth_mm
    add_rule(
        "GEOMETRY_WIDTH",
        context.width_mm >= 200,
        context.width_mm,
        200.0,
        "context.width_mm",
        "Beam width is below the supported IS 13920 minimum.",
    )
    add_rule(
        "GEOMETRY_RATIO",
        width_depth_ratio > 0.3,
        width_depth_ratio,
        ">0.3",
        "context.width_mm,context.overall_depth_mm",
        "Beam width-to-depth ratio does not exceed 0.3.",
    )

    minimum_ratio = (
        0.24
        * math.sqrt(context.concrete_grade_n_per_mm2)
        / context.steel_yield_strength_n_per_mm2
    )
    maximum_ratio = 0.025
    steel_face_checks: list[dict[str, object]] = []
    for face_name, station in (
        ("left", context.left_joint_face_x_mm),
        ("right", context.right_joint_face_x_mm),
    ):
        for role in (
            ReinforcementRole.TOP_LONGITUDINAL,
            ReinforcementRole.BOTTOM_LONGITUDINAL,
        ):
            active = _active_role_bars(context.bars, role, station)
            area = math.fsum(bar.area_mm2 for bar in active)
            ratio = area / (context.width_mm * context.effective_depth_mm)
            passed = minimum_ratio <= ratio <= maximum_ratio
            steel_face_checks.append(
                {
                    "face": face_name,
                    "role": role,
                    "bar_ids": [bar.bar_id for bar in active],
                    "area_mm2": area,
                    "ratio": ratio,
                    "minimum_ratio": minimum_ratio,
                    "maximum_ratio": maximum_ratio,
                    "passed": passed,
                }
            )
            add_rule(
                f"STEEL_{face_name.upper()}_{role.value.upper()}",
                passed,
                ratio,
                {"minimum": minimum_ratio, "maximum": maximum_ratio},
                f"context.bars[{face_name},{role.value}]",
                "Actual face reinforcement is outside the permitted longitudinal-steel range.",
            )

    continuous_top = [
        bar.bar_id
        for bar in context.bars
        if bar.role is ReinforcementRole.TOP_LONGITUDINAL
        and bar.start_station_mm <= context.left_joint_face_x_mm
        and bar.end_station_mm >= context.right_joint_face_x_mm
    ]
    continuous_bottom = [
        bar.bar_id
        for bar in context.bars
        if bar.role is ReinforcementRole.BOTTOM_LONGITUDINAL
        and bar.start_station_mm <= context.left_joint_face_x_mm
        and bar.end_station_mm >= context.right_joint_face_x_mm
    ]
    add_rule(
        "TOP_CONTINUITY",
        len(continuous_top) >= 2,
        continuous_top,
        "at least two continuous bars",
        "context.bars",
        "Fewer than two top bars continue through the clear span.",
    )
    add_rule(
        "BOTTOM_CONTINUITY",
        len(continuous_bottom) >= 2,
        continuous_bottom,
        "at least two continuous bars",
        "context.bars",
        "Fewer than two bottom bars continue through the clear span.",
    )

    minimum_bar_diameter = min(bar.diameter_mm for bar in context.bars)
    maximum_end_spacing = min(
        context.effective_depth_mm / 4,
        6 * minimum_bar_diameter,
        100.0,
    )
    required_zone_length = 2 * context.effective_depth_mm
    left_zones = [
        zone
        for zone in context.link_zones
        if zone.start_x_mm <= context.left_joint_face_x_mm
        and zone.end_x_mm >= context.left_joint_face_x_mm + required_zone_length
    ]
    right_zones = [
        zone
        for zone in context.link_zones
        if zone.start_x_mm <= context.right_joint_face_x_mm - required_zone_length
        and zone.end_x_mm >= context.right_joint_face_x_mm
    ]
    for side, zones in (("LEFT", left_zones), ("RIGHT", right_zones)):
        zone_passed = bool(zones) and all(
            _positive(zone.spacing_mm)
            and _positive(zone.link_diameter_mm)
            and zone.spacing_mm <= maximum_end_spacing + 1e-9
            and zone.closed
            and zone.hook_angle_degrees >= 135
            and zone.first_hoop_offset_from_joint_face_mm is not None
            and 0 <= zone.first_hoop_offset_from_joint_face_mm <= 50
            for zone in zones
        )
        add_rule(
            f"{side}_END_LINK_ZONE",
            zone_passed,
            [zone.zone_id for zone in zones],
            {
                "minimum_zone_length_mm": required_zone_length,
                "maximum_spacing_mm": maximum_end_spacing,
                "maximum_first_offset_mm": 50.0,
                "minimum_hook_angle_degrees": 135,
            },
            "context.link_zones",
            f"The {side.lower()} end lacks a complete qualifying close-link zone.",
        )

    anchorage_ok = all(
        _qualifies_as(binding.check, ANCHORAGE_CHECK_OPERATION)
        for binding in context.anchorage_checks
    )
    joint_checks_ok = all(
        binding.check.qualifies() for binding in context.dependent_joint_checks
    )
    add_rule(
        "ANCHORAGE_RESULTS",
        anchorage_ok,
        [
            {
                "beam_end": binding.beam_end.value,
                "role": binding.role.value,
                "result_id": binding.check.result_id,
            }
            for binding in context.anchorage_checks
        ],
        "one current passing complete anchorage result per left/right top/bottom pair",
        "context.anchorage_checks",
        "One or more required face anchorage results do not qualify.",
    )
    add_rule(
        "JOINT_RESULTS",
        joint_checks_ok,
        [
            {
                "joint_id": binding.joint_id,
                "result_id": binding.check.result_id,
            }
            for binding in context.dependent_joint_checks
        ],
        "one current passing complete result for each named joint",
        "context.dependent_joint_checks",
        "One or more dependent joint/system results do not qualify.",
    )

    forbidden_left_end = (
        context.left_joint_face_x_mm,
        context.left_joint_face_x_mm + required_zone_length,
    )
    forbidden_right_end = (
        context.right_joint_face_x_mm - required_zone_length,
        context.right_joint_face_x_mm,
    )
    splice_checks: list[dict[str, object]] = []
    for splice in context.splices:
        outside_end_zones = not (
            _intervals_overlap(
                splice.start_x_mm,
                splice.end_x_mm,
                *forbidden_left_end,
            )
            or _intervals_overlap(
                splice.start_x_mm,
                splice.end_x_mm,
                *forbidden_right_end,
            )
        )
        percentage_ok = 0 < splice.percentage_spliced_at_section <= 50
        evidence_ok = splice.kind is SpliceKind.LAP or bool(
            splice.coupler_qualification_reference and splice.installation_reference
        )
        passed = outside_end_zones and percentage_ok and evidence_ok
        splice_checks.append(
            {
                "splice_id": splice.splice_id,
                "outside_end_zones": outside_end_zones,
                "percentage_ok": percentage_ok,
                "qualification_and_installation_evidence": evidence_ok,
                "passed": passed,
            }
        )
        add_rule(
            f"SPLICE_{splice.splice_id}",
            passed,
            splice_checks[-1],
            "outside end zones, at most 50 percent, qualified if mechanical",
            f"context.splices[{splice.splice_id}]",
            "A longitudinal splice is in an end zone, exceeds the permitted percentage, or lacks mechanical-splice evidence.",
        )

    clear_span = context.right_joint_face_x_mm - context.left_joint_face_x_mm
    capacity_shear_positive_n = (
        abs(context.gravity_shear_n)
        + 1.4
        * (
            context.left_positive_probable_moment_nmm
            + context.right_negative_probable_moment_nmm
        )
        / clear_span
    )
    capacity_shear_negative_n = (
        abs(context.gravity_shear_n)
        + 1.4
        * (
            context.left_negative_probable_moment_nmm
            + context.right_positive_probable_moment_nmm
        )
        / clear_span
    )
    governing_shear_n = max(
        abs(context.imported_analysis_shear_n),
        capacity_shear_positive_n,
        capacity_shear_negative_n,
    )
    shear_reference_ok = _qualifies_as(
        context.shear_check,
        "is456.beam.shear.check/v1",
    )
    shear_capacity_ok = context.provided_shear_capacity_n + 1e-9 >= governing_shear_n
    add_rule(
        "CAPACITY_SHEAR",
        shear_reference_ok and shear_capacity_ok,
        {
            "imported_analysis_shear_n": abs(context.imported_analysis_shear_n),
            "capacity_shear_positive_n": capacity_shear_positive_n,
            "capacity_shear_negative_n": capacity_shear_negative_n,
            "governing_shear_n": governing_shear_n,
            "provided_shear_capacity_n": context.provided_shear_capacity_n,
            "shear_result_id": context.shear_check.result_id,
        },
        "provided capacity at least governing capacity-design shear with qualified shear result",
        "context.shear_check,context.provided_shear_capacity_n",
        "The qualified provided shear capacity is below the governing imported or capacity-design shear.",
    )

    passed = not diagnostics
    return completed_result(
        SEISMIC_DETAILING_CHECK_OPERATION,
        inputs,
        {
            "system_id": context.system_id,
            "seismic_design_revision_id": context.seismic_design_revision_id,
            "member_id": context.member_id,
            "physical_span_id": context.physical_span_id,
            "minimum_longitudinal_ratio": minimum_ratio,
            "maximum_longitudinal_ratio": maximum_ratio,
            "steel_face_checks": steel_face_checks,
            "continuous_top_bar_ids": continuous_top,
            "continuous_bottom_bar_ids": continuous_bottom,
            "required_end_zone_length_mm": required_zone_length,
            "maximum_end_link_spacing_mm": maximum_end_spacing,
            "splice_checks": splice_checks,
            "capacity_shear_positive_n": capacity_shear_positive_n,
            "capacity_shear_negative_n": capacity_shear_negative_n,
            "governing_shear_n": governing_shear_n,
            "rule_checks": rule_checks,
            "passed": passed,
        },
        engineering=EngineeringState.PASS if passed else EngineeringState.FAIL,
        diagnostics=diagnostics,
        provenance=provenance,
    )


def _point_to_segment_distance(
    point_x: float,
    point_y: float,
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
) -> float:
    dx = end_x - start_x
    dy = end_y - start_y
    length_squared = dx * dx + dy * dy
    if length_squared == 0:
        return math.hypot(point_x - start_x, point_y - start_y)
    projection = ((point_x - start_x) * dx + (point_y - start_y) * dy) / length_squared
    parameter = min(1.0, max(0.0, projection))
    nearest_x = start_x + parameter * dx
    nearest_y = start_y + parameter * dy
    return math.hypot(point_x - nearest_x, point_y - nearest_y)


def check_reinforcement_arrangement(
    request: ReinforcementArrangementCheckRequest,
) -> OperationResult:
    inputs = effective_inputs(request=request)
    provenance = _provenance(
        "reinforcement-arrangement-coordinate-check-wp05-v1",
        request.code_data_revision_id,
    )
    if (
        not request.profile_id
        or not request.member_id
        or not request.station_id
        or not request.reinforcement_revision_id
        or request.code_data_revision_id != IS456_CODE_DATA_REVISION
        or not all(
            _positive(value)
            for value in (
                request.section_width_mm,
                request.section_depth_mm,
                request.nominal_cover_mm,
                request.maximum_aggregate_size_mm,
            )
        )
        or not _nonnegative(request.vertical_alignment_tolerance_mm)
    ):
        return rejected_result(
            ARRANGEMENT_CHECK_OPERATION,
            inputs,
            (
                _diagnostic(
                    ARRANGEMENT_CHECK_OPERATION,
                    "INPUT.INVALID",
                    "The arrangement check requires complete identities, positive section/cover/aggregate geometry, and an alignment tolerance.",
                    "request",
                    "Correct the full reinforcement-arrangement basis.",
                ),
            ),
            provenance=provenance,
        )
    full_roles = {
        ReinforcementRole.TOP_LONGITUDINAL,
        ReinforcementRole.BOTTOM_LONGITUDINAL,
    }
    if (
        not request.bars
        or not request.links
        or not request.required_roles
        or not full_roles.issubset(set(request.required_roles))
    ):
        return _not_evaluated(
            ARRANGEMENT_CHECK_OPERATION,
            inputs,
            provenance,
            "A full arrangement requires actual bars, links, and both top and bottom longitudinal roles.",
            "bars,links,required_roles",
        )
    if request.require_placement_plan and (
        request.placement_opening is None
        or not request.placement_opening.sequence_reference
    ):
        return _not_evaluated(
            ARRANGEMENT_CHECK_OPERATION,
            inputs,
            provenance,
            "The selected construction-fit scope requires a placement opening and sequence reference.",
            "placement_opening",
        )

    bar_ids = [bar.bar_id for bar in request.bars]
    link_ids = [link.link_id for link in request.links]
    obstacle_ids = [obstacle.obstacle_id for obstacle in request.obstacles]
    if (
        any(not _validate_bar_path(bar) for bar in request.bars)
        or len(bar_ids) != len(set(bar_ids))
        or any(not item for item in link_ids + obstacle_ids)
        or len(link_ids) != len(set(link_ids))
        or len(obstacle_ids) != len(set(obstacle_ids))
        or any(
            not isinstance(role, ReinforcementRole) for role in request.required_roles
        )
        or len(request.required_roles) != len(set(request.required_roles))
    ):
        return rejected_result(
            ARRANGEMENT_CHECK_OPERATION,
            inputs,
            (
                _diagnostic(
                    ARRANGEMENT_CHECK_OPERATION,
                    "ARRANGEMENT.INVALID",
                    "Bars, links, obstacles, and required roles need valid geometry and unique identities.",
                    "bars,links,obstacles,required_roles",
                    "Correct the complete arrangement records.",
                ),
            ),
            provenance=provenance,
        )

    diagnostics: list[Diagnostic] = []

    def fail(code: str, message: str, field: str, remediation: str) -> None:
        diagnostics.append(
            _diagnostic(
                ARRANGEMENT_CHECK_OPERATION,
                code,
                message,
                field,
                remediation,
            )
        )

    link_checks: list[dict[str, object]] = []
    for link in request.links:
        valid = (
            _positive(link.diameter_mm)
            and _nonnegative(link.internal_bend_radius_mm)
            and all(
                math.isfinite(value)
                for value in (
                    link.left_centre_x_mm,
                    link.right_centre_x_mm,
                    link.top_centre_y_mm,
                    link.bottom_centre_y_mm,
                )
            )
            and link.left_centre_x_mm < link.right_centre_x_mm
            and link.top_centre_y_mm < link.bottom_centre_y_mm
        )
        if not valid:
            return rejected_result(
                ARRANGEMENT_CHECK_OPERATION,
                inputs,
                (
                    _diagnostic(
                        ARRANGEMENT_CHECK_OPERATION,
                        "LINK.INVALID",
                        "Every link cage requires an ordered centreline rectangle, diameter, and nonnegative bend radius.",
                        f"links[{link.link_id}]",
                        "Correct the link cage geometry.",
                    ),
                ),
                provenance=provenance,
            )
        radius = link.diameter_mm / 2
        surface_covers = {
            "left": link.left_centre_x_mm - radius,
            "right": request.section_width_mm - (link.right_centre_x_mm + radius),
            "top": link.top_centre_y_mm - radius,
            "bottom": request.section_depth_mm - (link.bottom_centre_y_mm + radius),
        }
        cover_ok = min(surface_covers.values()) + 1e-9 >= request.nominal_cover_mm
        centreline_width = link.right_centre_x_mm - link.left_centre_x_mm
        centreline_height = link.bottom_centre_y_mm - link.top_centre_y_mm
        minimum_bend_extent = 2 * (link.internal_bend_radius_mm + link.diameter_mm / 2)
        bend_fit_ok = (
            centreline_width + 1e-9 >= minimum_bend_extent
            and centreline_height + 1e-9 >= minimum_bend_extent
        )
        passed = cover_ok and bend_fit_ok and link.closed
        if not passed:
            fail(
                "LINK.NONCOMPLIANT",
                "A link cage fails cover to its steel surface, bend enclosure, or closure.",
                f"links[{link.link_id}]",
                "Revise the cage dimensions, cover, bend radius, or closure.",
            )
        link_checks.append(
            {
                "link_id": link.link_id,
                "surface_covers_mm": surface_covers,
                "required_cover_mm": request.nominal_cover_mm,
                "cover_ok": cover_ok,
                "centreline_width_mm": centreline_width,
                "centreline_height_mm": centreline_height,
                "minimum_bend_extent_mm": minimum_bend_extent,
                "bend_fit_ok": bend_fit_ok,
                "closed": link.closed,
                "passed": passed,
            }
        )

    missing_roles = [
        role
        for role in request.required_roles
        if not any(bar.role is role for bar in request.bars)
    ]
    if missing_roles:
        fail(
            "ROLE.MISSING",
            "One or more declared reinforcement roles have no actual bars.",
            "required_roles",
            "Supply every required top, bottom, side, or corner group.",
        )

    enclosure_checks: list[dict[str, object]] = []
    for bar in request.bars:
        radius = bar.diameter_mm / 2
        within_section = (
            radius <= bar.x_from_left_mm <= request.section_width_mm - radius
            and radius <= bar.y_from_top_mm <= request.section_depth_mm - radius
        )
        enclosing_links = [
            link.link_id
            for link in request.links
            if bar.x_from_left_mm - radius
            >= link.left_centre_x_mm + link.diameter_mm / 2 - 1e-9
            and bar.x_from_left_mm + radius
            <= link.right_centre_x_mm - link.diameter_mm / 2 + 1e-9
            and bar.y_from_top_mm - radius
            >= link.top_centre_y_mm + link.diameter_mm / 2 - 1e-9
            and bar.y_from_top_mm + radius
            <= link.bottom_centre_y_mm - link.diameter_mm / 2 + 1e-9
        ]
        passed = within_section and bool(enclosing_links)
        if not passed:
            fail(
                "BAR.NOT_ENCLOSED",
                "A longitudinal bar lies outside the section or is not enclosed by a supplied closed link cage.",
                f"bars[{bar.bar_id}]",
                "Move the bar or revise the enclosing link cage.",
            )
        enclosure_checks.append(
            {
                "bar_id": bar.bar_id,
                "within_section": within_section,
                "enclosing_link_ids": enclosing_links,
                "passed": passed,
            }
        )

    pair_collision_checks: list[dict[str, object]] = []
    for index, first in enumerate(request.bars):
        for second in request.bars[index + 1 :]:
            centre_distance = math.hypot(
                first.x_from_left_mm - second.x_from_left_mm,
                first.y_from_top_mm - second.y_from_top_mm,
            )
            required_distance = (first.diameter_mm + second.diameter_mm) / 2
            passed = centre_distance + 1e-9 >= required_distance
            if not passed:
                fail(
                    "BAR.COLLISION",
                    "Two longitudinal bar circles overlap.",
                    f"bars[{first.bar_id},{second.bar_id}]",
                    "Separate the bar centres.",
                )
            pair_collision_checks.append(
                {
                    "first_bar_id": first.bar_id,
                    "second_bar_id": second.bar_id,
                    "centre_distance_mm": centre_distance,
                    "minimum_nonoverlap_distance_mm": required_distance,
                    "passed": passed,
                }
            )

    horizontal_clearance_checks: list[dict[str, object]] = []
    grouped_layers: dict[tuple[ReinforcementRole, int], list[LongitudinalBarPath]] = {}
    for bar in request.bars:
        grouped_layers.setdefault((bar.role, bar.layer), []).append(bar)
    for index, first in enumerate(request.bars):
        for second in request.bars[index + 1 :]:
            if (
                abs(first.y_from_top_mm - second.y_from_top_mm)
                > request.vertical_alignment_tolerance_mm + 1e-9
            ):
                continue
            actual = (
                abs(second.x_from_left_mm - first.x_from_left_mm)
                - (first.diameter_mm + second.diameter_mm) / 2
            )
            required = max(
                first.diameter_mm,
                second.diameter_mm,
                request.maximum_aggregate_size_mm + 5,
            )
            passed = actual + 1e-9 >= required
            if not passed:
                fail(
                    "SPACING.HORIZONTAL",
                    "Adjacent bars in one layer lack the required horizontal clear distance.",
                    f"bars[{first.bar_id},{second.bar_id}]",
                    "Increase the horizontal bar spacing or revise the aggregate/bar arrangement.",
                )
            horizontal_clearance_checks.append(
                {
                    "first_role": first.role,
                    "first_layer": first.layer,
                    "second_role": second.role,
                    "second_layer": second.layer,
                    "first_bar_id": first.bar_id,
                    "second_bar_id": second.bar_id,
                    "actual_clear_mm": actual,
                    "required_clear_mm": required,
                    "passed": passed,
                }
            )

    vertical_clearance_checks: list[dict[str, object]] = []
    for index, first in enumerate(request.bars):
        for second in request.bars[index + 1 :]:
            if (
                abs(first.x_from_left_mm - second.x_from_left_mm)
                > request.vertical_alignment_tolerance_mm + 1e-9
            ):
                continue
            actual = (
                abs(second.y_from_top_mm - first.y_from_top_mm)
                - (first.diameter_mm + second.diameter_mm) / 2
            )
            required = max(
                15.0,
                2 * request.maximum_aggregate_size_mm / 3,
                first.diameter_mm,
                second.diameter_mm,
            )
            passed = actual + 1e-9 >= required
            if not passed:
                fail(
                    "SPACING.VERTICAL",
                    "Vertically aligned bars lack the required clear distance.",
                    f"bars[{first.bar_id},{second.bar_id}]",
                    "Increase the vertical bar spacing.",
                )
            vertical_clearance_checks.append(
                {
                    "kind": "aligned_pair",
                    "first_bar_id": first.bar_id,
                    "second_bar_id": second.bar_id,
                    "actual_clear_mm": actual,
                    "required_clear_mm": required,
                    "alignment_tolerance_mm": request.vertical_alignment_tolerance_mm,
                    "passed": passed,
                }
            )

    for role in {bar.role for bar in request.bars}:
        physical_rows = sorted(
            (
                (layer, grouped_layers[(role, layer)])
                for layer in {bar.layer for bar in request.bars if bar.role is role}
            ),
            key=lambda item: math.fsum(bar.y_from_top_mm for bar in item[1])
            / len(item[1]),
        )
        for (upper_layer, upper), (lower_layer, lower) in zip(
            physical_rows, physical_rows[1:], strict=False
        ):
            upper_bottom = max(bar.y_from_top_mm + bar.diameter_mm / 2 for bar in upper)
            lower_top = min(bar.y_from_top_mm - bar.diameter_mm / 2 for bar in lower)
            actual = lower_top - upper_bottom
            largest_diameter = max(bar.diameter_mm for bar in (*upper, *lower))
            required = max(
                15.0,
                2 * request.maximum_aggregate_size_mm / 3,
                largest_diameter,
            )
            passed = actual + 1e-9 >= required
            if not passed:
                fail(
                    "SPACING.VERTICAL",
                    "Adjacent physical bar rows lack the required vertical clearance.",
                    f"bars[{role.value},layers {upper_layer}-{lower_layer}]",
                    "Increase the physical row spacing.",
                )
            vertical_clearance_checks.append(
                {
                    "kind": "physical_layer_gap",
                    "role": role,
                    "upper_layer": upper_layer,
                    "lower_layer": lower_layer,
                    "actual_clear_mm": actual,
                    "required_clear_mm": required,
                    "passed": passed,
                }
            )

    role_centroids: list[dict[str, object]] = []
    for role in sorted({bar.role for bar in request.bars}, key=lambda item: item.value):
        bars = [bar for bar in request.bars if bar.role is role]
        area = math.fsum(bar.area_mm2 for bar in bars)
        role_centroids.append(
            {
                "role": role,
                "bar_ids": [bar.bar_id for bar in bars],
                "area_mm2": area,
                "centroid_x_from_left_mm": math.fsum(
                    bar.area_mm2 * bar.x_from_left_mm for bar in bars
                )
                / area,
                "centroid_y_from_top_mm": math.fsum(
                    bar.area_mm2 * bar.y_from_top_mm for bar in bars
                )
                / area,
            }
        )

    obstacle_checks: list[dict[str, object]] = []
    for obstacle in request.obstacles:
        if (
            not _positive(obstacle.diameter_mm)
            or not _nonnegative(obstacle.required_clearance_mm)
            or not all(
                math.isfinite(value)
                for value in (
                    obstacle.x_from_left_mm,
                    obstacle.y_from_top_mm,
                )
            )
        ):
            return rejected_result(
                ARRANGEMENT_CHECK_OPERATION,
                inputs,
                (
                    _diagnostic(
                        ARRANGEMENT_CHECK_OPERATION,
                        "OBSTACLE.INVALID",
                        "Every construction obstacle requires a circle and nonnegative required clearance.",
                        f"obstacles[{obstacle.obstacle_id}]",
                        "Correct the resolved obstacle geometry.",
                    ),
                ),
                provenance=provenance,
            )
        for bar in request.bars:
            centre_distance = math.hypot(
                obstacle.x_from_left_mm - bar.x_from_left_mm,
                obstacle.y_from_top_mm - bar.y_from_top_mm,
            )
            required = (
                obstacle.diameter_mm / 2
                + bar.diameter_mm / 2
                + obstacle.required_clearance_mm
            )
            passed = centre_distance + 1e-9 >= required
            if not passed:
                fail(
                    "OBSTACLE.CLASH",
                    "A reinforcement bar clashes with a resolved joint or construction obstacle.",
                    f"obstacles[{obstacle.obstacle_id}],bars[{bar.bar_id}]",
                    "Move the bar/obstacle or revise the construction detail.",
                )
            obstacle_checks.append(
                {
                    "obstacle_id": obstacle.obstacle_id,
                    "reinforcement_kind": "bar",
                    "bar_id": bar.bar_id,
                    "centre_distance_mm": centre_distance,
                    "required_distance_mm": required,
                    "passed": passed,
                }
            )
        for link in request.links:
            corners = (
                (link.left_centre_x_mm, link.top_centre_y_mm),
                (link.right_centre_x_mm, link.top_centre_y_mm),
                (link.right_centre_x_mm, link.bottom_centre_y_mm),
                (link.left_centre_x_mm, link.bottom_centre_y_mm),
            )
            for segment_index, (start, end) in enumerate(
                zip(corners, (*corners[1:], corners[0]), strict=True),
                start=1,
            ):
                centre_distance = _point_to_segment_distance(
                    obstacle.x_from_left_mm,
                    obstacle.y_from_top_mm,
                    *start,
                    *end,
                )
                required = (
                    obstacle.diameter_mm / 2
                    + link.diameter_mm / 2
                    + obstacle.required_clearance_mm
                )
                passed = centre_distance + 1e-9 >= required
                if not passed:
                    fail(
                        "OBSTACLE.CLASH",
                        "A link cage clashes with a resolved joint or construction obstacle.",
                        f"obstacles[{obstacle.obstacle_id}],links[{link.link_id}]",
                        "Move the cage/obstacle or revise the construction detail.",
                    )
                obstacle_checks.append(
                    {
                        "obstacle_id": obstacle.obstacle_id,
                        "reinforcement_kind": "link_segment",
                        "link_id": link.link_id,
                        "segment_index": segment_index,
                        "centre_distance_mm": centre_distance,
                        "required_distance_mm": required,
                        "passed": passed,
                    }
                )

    placement_check: dict[str, object] | None = None
    if request.placement_opening is not None:
        opening = request.placement_opening
        if (
            not opening.opening_id
            or not _positive(opening.clear_width_mm)
            or not _positive(opening.clear_height_mm)
            or not opening.sequence_reference
        ):
            return rejected_result(
                ARRANGEMENT_CHECK_OPERATION,
                inputs,
                (
                    _diagnostic(
                        ARRANGEMENT_CHECK_OPERATION,
                        "PLACEMENT.INVALID",
                        "A placement opening requires identity, positive clear dimensions, and a sequence reference.",
                        "placement_opening",
                        "Correct the construction placement record.",
                    ),
                ),
                provenance=provenance,
            )
        required_width = max(
            link.right_centre_x_mm - link.left_centre_x_mm + link.diameter_mm
            for link in request.links
        )
        required_height = max(
            link.bottom_centre_y_mm - link.top_centre_y_mm + link.diameter_mm
            for link in request.links
        )
        passed = (
            opening.clear_width_mm + 1e-9 >= required_width
            and opening.clear_height_mm + 1e-9 >= required_height
        )
        if not passed:
            fail(
                "PLACEMENT.DOES_NOT_FIT",
                "The resolved link cage cannot pass through the supplied placement opening.",
                "placement_opening",
                "Revise the opening, cage assembly, or placement sequence.",
            )
        placement_check = {
            "opening_id": opening.opening_id,
            "sequence_reference": opening.sequence_reference,
            "clear_width_mm": opening.clear_width_mm,
            "clear_height_mm": opening.clear_height_mm,
            "required_width_mm": required_width,
            "required_height_mm": required_height,
            "passed": passed,
        }

    passed = not diagnostics
    return completed_result(
        ARRANGEMENT_CHECK_OPERATION,
        inputs,
        {
            "member_id": request.member_id,
            "station_id": request.station_id,
            "reinforcement_revision_id": request.reinforcement_revision_id,
            "link_checks": link_checks,
            "bar_enclosure_checks": enclosure_checks,
            "pair_collision_checks": pair_collision_checks,
            "horizontal_clearance_checks": horizontal_clearance_checks,
            "vertical_clearance_checks": vertical_clearance_checks,
            "role_centroids": role_centroids,
            "obstacle_checks": obstacle_checks,
            "placement_check": placement_check,
            "passed": passed,
        },
        engineering=EngineeringState.PASS if passed else EngineeringState.FAIL,
        diagnostics=diagnostics,
        provenance=provenance,
    )
