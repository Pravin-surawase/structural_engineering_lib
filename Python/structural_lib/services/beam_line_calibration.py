"""Pure W3H comparison of an explicit frozen plane to normalized reference rows.

No COM, filesystem, interpolation, sign guessing, defaults or model approval.
All supplied rows are required: a missing mapping never becomes a partial pass.
"""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from structural_lib.core.analysis_contracts import EvidenceStateV1, EvidenceValueV1
from structural_lib.core.beam_line import BeamLineIssueV1
from structural_lib.core.beam_line_calibration import (
    BeamLineCalibrationV1,
    BeamLineComparisonRequestV1,
    BeamLineComponentComparisonV1,
)

_T = TypeVar("_T")
_LIMITATIONS = (
    "Numeric comparison of the exact supplied scope only; external normalized evidence and engineering criteria require independent acceptance.",
    "Synthetic references are L1 software evidence, never installed/model-specific L5 calibration.",
    "No general ETABS parity, final actions, torsion/3D calibration, professional approval or candidate-screening authorization.",
)


def _digest(model: BaseModel, omit: str | None = None) -> str:
    return hashlib.sha256(
        json.dumps(
            model.model_dump(mode="json", exclude={omit} if omit else set()),
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


class _NotComparableError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def _require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise _NotComparableError(code, message)


def _present(evidence: EvidenceValueV1[_T], label: str) -> _T:
    _require(
        evidence.state is EvidenceStateV1.PRESENT,
        "MISSING_EVIDENCE",
        f"{label}: {evidence.state.value}",
    )
    assert evidence.value is not None
    return evidence.value


def _seen_unique(values: list[Any], label: str) -> None:
    _require(len(values) == len(set(values)), "DUPLICATE_MAPPING", label)


def _compare(
    request: BeamLineComparisonRequestV1,
) -> tuple[BeamLineComponentComparisonV1, ...]:
    current = _present(request.current_identity, "current_identity")
    ref = _present(request.reference, "reference")
    mapping = _present(request.mapping, "mapping")
    criteria = _present(request.criteria, "criteria")
    _present(ref.topology_review, "reference.topology_review")
    _present(ref.linear_response_review, "reference.linear_response_review")
    _present(mapping.reviewed_basis, "mapping.reviewed_basis")
    result = request.solver_result
    req = result.request
    identity = ref.identity
    _require(
        current == identity,
        "REFERENCE_INVALIDATED",
        "Current model/definitions/settings/version/selection differ from reference",
    )
    _require(
        _digest(ref, "reference_sha256") == ref.reference_sha256,
        "REFERENCE_HASH",
        "Reference bytes changed",
    )
    _require(
        _digest(req) == result.request_sha256
        and _digest(result, "result_sha256") == result.result_sha256,
        "SOLVER_HASH",
        "Solver request/result bytes changed",
    )
    _require(
        req.model_definition_sha256 == identity.model_definition_sha256
        and req.catalogue_sha256 == identity.catalogue_sha256
        and req.scenario_definition_sha256 == identity.scenario_definition_sha256
        and req.scenario.result_kind == identity.result_kind
        and req.scenario.result_id == mapping.solver_result_id
        and req.scenario.scenario_id == mapping.solver_scenario_id
        and identity.selection_id == mapping.reference_selection_id,
        "SOLVER_REFERENCE_BINDING",
        "Solver model/catalogue/scenario/selection differs from reference",
    )
    _require(
        (req.source_basis == "SYNTHETIC_REFERENCE")
        == (ref.source_basis == "SYNTHETIC_REFERENCE"),
        "SOURCE_BASIS",
        "Synthetic and model-specific evidence cannot be interchanged",
    )
    tolerances = {item.component: item for item in criteria.tolerances}
    _require(
        len(tolerances) == len(criteria.tolerances),
        "DUPLICATE_CRITERIA",
        "Each component needs one tolerance",
    )
    _require(
        {"SHEAR_KN", "MOMENT_KNM"} <= tolerances.keys(),
        "ACTION_CRITERIA_REQUIRED",
        "Both signed shear and moment are mandatory",
    )
    spans = {item.span_id: item for item in result.spans}
    nodes = {item.node_id: item for item in result.nodes}
    _require(
        len(spans) == len(result.spans) and len(nodes) == len(result.nodes),
        "SOLVER_DOMAIN",
        "Duplicate solver entities",
    )
    _require(
        result.station_row_count == sum(len(span.stations) for span in result.spans),
        "SOLVER_DOMAIN",
        "Solver station count differs",
    )
    rows = {row.row_id: row for row in ref.actions}
    _seen_unique([row.row_id for row in ref.actions], "Reference action IDs")
    _seen_unique(
        [item.reference_row_id for item in mapping.actions], "Action row mapping"
    )
    _seen_unique(
        [(item.span_id, item.solver_station_index) for item in mapping.actions],
        "Action station mapping",
    )
    _require(
        set(rows) == {item.reference_row_id for item in mapping.actions},
        "INCOMPLETE_MAPPING",
        "Every retained action row needs exactly one mapping",
    )
    _require(
        set(spans) == {item.span_id for item in mapping.actions},
        "INCOMPLETE_MAPPING",
        "Every solver span needs reference actions",
    )
    member_spans: dict[str, str] = {}
    frame_bases: dict[str, tuple[Any, ...]] = {}
    for item in mapping.actions:
        _require(
            (item.shear_component, item.moment_component)
            in (("v2_kn", "m3_knm"), ("v3_kn", "m2_knm")),
            "PLANE_MAPPING",
            "Shear and moment must belong to the same bending plane",
        )
        basis = (
            item.source_station_origin_mm,
            item.source_distance_direction,
            item.local_axis_basis,
            item.shear_component,
            item.moment_component,
            item.shear_sign,
            item.moment_sign,
        )
        _require(
            frame_bases.setdefault(item.span_id, basis) == basis,
            "INCONSISTENT_FRAME_BASIS",
            "One span cannot change axes/signs/origin between rows",
        )
        previous = member_spans.setdefault(item.member_id, item.span_id)
        _require(
            previous == item.span_id,
            "MEMBER_SPAN_MAPPING",
            "One member cannot map to different spans",
        )
    _require(
        len(set(member_spans.values())) == len(member_spans),
        "MEMBER_SPAN_MAPPING",
        "One span cannot map to different members",
    )
    comparisons: list[BeamLineComponentComparisonV1] = []

    def add(
        row: Any, entity: str, component: Any, local: float, reference: float
    ) -> None:
        tolerance = tolerances[component]
        error = local - reference
        allowed = tolerance.absolute + tolerance.relative * abs(reference)
        _require(
            all(math.isfinite(value) for value in (error, allowed)),
            "NONFINITE_COMPARISON",
            "Comparison overflow",
        )
        comparisons.append(
            BeamLineComponentComparisonV1(
                reference_row_id=row.row_id,
                reference_row_sha256=row.row_sha256,
                local_entity_id=entity,
                component=component,
                reference_value=reference,
                local_value=local,
                signed_error=error,
                absolute_error=abs(error),
                allowed_error=allowed,
                within_tolerance=abs(error) <= allowed,
            )
        )

    def check_row(row: Any) -> None:
        _require(
            _digest(row, "row_sha256") == row.row_sha256,
            "ROW_HASH",
            "Reference row changed",
        )
        _require(
            row.model_identity_sha256 == identity.model_identity_sha256
            and row.baseline_sha256 == identity.baseline_sha256
            and row.catalogue_sha256 == identity.catalogue_sha256
            and row.selection_id == identity.selection_id
            and row.output_case_name == identity.result_name
            and row.step_type == identity.step_type
            and row.step_number == identity.step_number,
            "ROW_IDENTITY",
            "Row model/baseline/catalogue/selection/step mismatch",
        )

    for item in mapping.actions:
        row = rows[item.reference_row_id]
        check_row(row)
        _require(
            row.member_id == item.member_id
            and row.local_axis_basis == item.local_axis_basis,
            "ACTION_MAPPING",
            "Member or explicit axis basis differs",
        )
        _require(
            row.selection_kind.value == identity.result_kind
            and row.selection_name == identity.result_name,
            "ROW_IDENTITY",
            "Action selection differs",
        )
        span = spans[item.span_id]
        _require(
            item.solver_station_index < len(span.stations),
            "STATION_MAPPING",
            "Solver station index is absent",
        )
        station = span.stations[item.solver_station_index]
        distance_mm = (
            row.object_station_mm - item.source_station_origin_mm
        ) * item.source_distance_direction
        _require(
            station.span_id == item.span_id
            and station.side == item.station_side
            and abs(distance_mm - station.distance_from_flexible_start_m * 1000.0)
            <= criteria.station_distance_tolerance_mm,
            "STATION_MAPPING",
            "Station distance or discontinuity side differs; no interpolation",
        )
        add(
            row,
            item.span_id,
            "SHEAR_KN",
            station.shear_kn,
            getattr(row, item.shear_component) * item.shear_sign,
        )
        add(
            row,
            item.span_id,
            "MOMENT_KNM",
            station.moment_knm,
            getattr(row, item.moment_component) * item.moment_sign,
        )

    for label, evidence, joint_mapping, components in (
        (
            "displacements",
            ref.displacements,
            mapping.displacements,
            ("DISPLACEMENT_MM", "ROTATION_RAD"),
        ),
        (
            "reactions",
            ref.reactions,
            mapping.reactions,
            ("REACTION_KN", "REACTION_KNM"),
        ),
    ):
        requested = set(components) & tolerances.keys()
        if not requested:
            _require(
                not joint_mapping,
                "UNDECLARED_COMPARISON",
                f"{label} mapping has no criteria",
            )
            # Missing reference evidence remains explicit, never replaced by zero.
            continue
        _require(
            evidence.state is EvidenceStateV1.PRESENT,
            "MISSING_EVIDENCE",
            f"{label}: {evidence.state.value}",
        )
        joint_rows = evidence.value
        assert joint_rows is not None
        _require(
            bool(joint_rows) and len(joint_rows) <= 6,
            "JOINT_DOMAIN",
            f"{label}: bounded nonempty node domain required",
        )
        by_id = {row.row_id: row for row in joint_rows}
        _seen_unique([row.row_id for row in joint_rows], label)
        _seen_unique([item.reference_row_id for item in joint_mapping], label)
        _seen_unique([item.node_id for item in joint_mapping], label)
        _seen_unique([item.joint_id for item in joint_mapping], label)
        _require(
            set(by_id) == {item.reference_row_id for item in joint_mapping}
            and set(nodes) == {item.node_id for item in joint_mapping},
            "INCOMPLETE_MAPPING",
            f"{label}: every reference row and solver node needs a mapping",
        )
        for joint_item in joint_mapping:
            _require(
                joint_item.translation_axis != joint_item.rotation_axis,
                "PLANE_MAPPING",
                "Translation and rotation must be distinct axes",
            )
            joint_row = by_id[joint_item.reference_row_id]
            check_row(joint_row)
            _require(
                joint_row.joint_id == joint_item.joint_id
                and joint_row.coordinate_system == joint_item.coordinate_system,
                "JOINT_MAPPING",
                "Joint or coordinate basis differs",
            )
            node = nodes[joint_item.node_id]
            for component in components:
                if component not in requested:
                    continue
                if component == "DISPLACEMENT_MM":
                    local = node.vertical_displacement_m * 1000.0
                    value = (
                        getattr(joint_row, f"u{joint_item.translation_axis}_mm")
                        * joint_item.translation_sign
                    )
                elif component == "ROTATION_RAD":
                    local = _present(node.rotation_rad, "solver node rotation")
                    value = (
                        getattr(joint_row, f"r{joint_item.rotation_axis}_rad")
                        * joint_item.rotation_sign
                    )
                elif component == "REACTION_KN":
                    local = node.vertical_reaction_kn
                    value = (
                        getattr(joint_row, f"f{joint_item.translation_axis}_kn")
                        * joint_item.translation_sign
                    )
                else:
                    local = node.reaction_moment_knm
                    value = (
                        getattr(joint_row, f"m{joint_item.rotation_axis}_knm")
                        * joint_item.rotation_sign
                    )
                add(joint_row, joint_item.node_id, component, local, value)
    return tuple(comparisons)


def compare_beam_line_to_reference_v1(
    request: BeamLineComparisonRequestV1, /
) -> BeamLineCalibrationV1:
    """Compare the exact caller-declared scope; never infer engineering criteria.

    CALIBRATED means all declared numerical comparisons meet supplied tolerances.
    It is not external acceptance of the input mappings or model applicability.
    Missing/invalid evidence yields NOT_COMPARABLE with no partial comparison.
    """
    comparisons: tuple[BeamLineComponentComparisonV1, ...] = ()
    issues: tuple[BeamLineIssueV1, ...] = ()
    status: Any = "NOT_COMPARABLE"
    try:
        request = BeamLineComparisonRequestV1.model_validate(request.model_dump())
        comparisons = _compare(request)
        status = (
            "CALIBRATED"
            if all(row.within_tolerance for row in comparisons)
            else "OUT_OF_BAND"
        )
    except _NotComparableError as exc:
        issues = (BeamLineIssueV1(reason_code=exc.code, message=str(exc)),)
    except (ValidationError, ArithmeticError, ValueError, KeyError, IndexError):
        issues = (
            BeamLineIssueV1(
                reason_code="INVALID_COMPARISON_INPUT",
                message="Invalid, nonfinite or inconsistent comparison input",
            ),
        )

    def binding(
        value: BaseModel | None, field: str | None = None
    ) -> EvidenceValueV1[str]:
        if value is None:
            return EvidenceValueV1[str](
                state=EvidenceStateV1.UNAVAILABLE,
                reason_code="MISSING_BINDING",
                message="No valid comparison binding supplied",
                source_references=("comparison-request",),
            )
        return EvidenceValueV1[str](
            state=EvidenceStateV1.PRESENT,
            value=getattr(value, field) if field else _digest(value),
            source_references=("comparison-request",),
        )

    # A malformed constructed request may not have serializable finite bytes.
    try:
        request_sha = _digest(request)
        reference = request.reference.value
        output = BeamLineCalibrationV1(
            status=status,
            request_sha256=request_sha,
            bindings=request.current_identity,
            reference_sha256=binding(reference, "reference_sha256"),
            station_mapping_sha256=binding(request.mapping.value),
            criteria_sha256=binding(request.criteria.value),
            reference_basis=binding(reference, "source_basis"),
            comparisons=comparisons,
            issues=issues,
            limitations=_LIMITATIONS,
            calibration_sha256="0" * 64,
        )
    except (ValidationError, ValueError):
        # No false digest for an unserializable request; reject it as invalid.
        raise ValueError("Comparison input has no valid canonical identity") from None
    return output.model_copy(
        update={"calibration_sha256": _digest(output, "calibration_sha256")}
    )
