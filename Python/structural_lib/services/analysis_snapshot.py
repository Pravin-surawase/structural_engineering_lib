# SPDX-License-Identifier: MIT
"""Host-free validation and deterministic replay of analysis snapshots."""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Iterable, Mapping
from enum import StrEnum
from typing import Any, Literal

from pydantic import ValidationError

from structural_lib.core.analysis_snapshot import (
    AnalysisCaseStatus,
    AnalysisSnapshotV1,
    CallEffect,
    CallStage,
    EtabsImportRequestV1,
    EtabsSnapshotResultV1,
    RawModelRecordKind,
    ResultSelectionKind,
    RowDisposition,
    SnapshotDiagnosticV1,
    SnapshotOperationState,
    SnapshotProvenanceV1,
)

CANONICALIZATION_VERSION = "pf4-canonical-json-v1"
MAXIMUM_SNAPSHOT_BYTES = 25_000_000
_PROVENANCE = SnapshotProvenanceV1(
    source_references=(
        "PF4 engineering semantic model",
        "PF8 portable analysis snapshot contract",
        "WP10-01 shared conformance fixture",
    ),
    limitations=(
        "Offline validation proves portable evidence integrity, not live ETABS compatibility.",
        "Snapshot acceptance is not structural analysis validation or engineering approval.",
    ),
)


class _DuplicateKeyError(ValueError):
    pass


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKeyError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number: {value}")


def _plain(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return _plain(value.model_dump(mode="json"))
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_plain(item) for item in value]
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("canonical snapshot numbers must be finite")
        if value == 0:
            return 0
        if value.is_integer() and abs(value) <= 9_007_199_254_740_991:
            return int(value)
    return value


def canonical_snapshot_json_bytes(value: Any) -> bytes:
    """Return compact PF4 canonical JSON for a portable snapshot value."""

    return json.dumps(
        _plain(value),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(canonical_snapshot_json_bytes(value)).hexdigest()


def _hash_basis(value: Any, *excluded: str) -> dict[str, Any]:
    payload = dict(_plain(value))
    for key in excluded:
        payload.pop(key, None)
    return payload


def call_record_sha256(record: Any) -> str:
    return _sha256(_hash_basis(record, "record_sha256"))


def call_ledger_sha256(ledger: Any) -> str:
    return _sha256(_hash_basis(ledger, "ledger_sha256"))


def raw_capture_sha256(capture: Any) -> str:
    return _sha256(_hash_basis(capture, "raw_capture_id", "raw_capture_sha256"))


def analysis_snapshot_sha256(snapshot: AnalysisSnapshotV1) -> str:
    return _sha256(_hash_basis(snapshot, "snapshot_id", "snapshot_sha256"))


def analysis_action_row_id(row: Any) -> str:
    digest = _sha256(_hash_basis(row, "row_id"))
    return f"analysis_action_row_id:{CANONICALIZATION_VERSION}:{digest}"


def canonical_analysis_snapshot_json(snapshot: AnalysisSnapshotV1) -> str:
    """Serialize a validated snapshot deterministically, including identities."""

    return canonical_snapshot_json_bytes(snapshot).decode("utf-8")


def parse_etabs_import_request_json(payload: str | bytes) -> EtabsImportRequestV1:
    """Parse one strict portable AO16 request without contacting a host."""

    text = _checked_json_text(payload)
    _decode_json(text)
    return EtabsImportRequestV1.model_validate_json(text)


def _checked_json_text(payload: str | bytes) -> str:
    if isinstance(payload, bytes):
        if len(payload) > MAXIMUM_SNAPSHOT_BYTES:
            raise ValueError("snapshot JSON exceeds the portable size limit")
        return payload.decode("utf-8")
    encoded = payload.encode("utf-8")
    if len(encoded) > MAXIMUM_SNAPSHOT_BYTES:
        raise ValueError("snapshot JSON exceeds the portable size limit")
    return payload


def _decode_json(text: str) -> dict[str, Any]:
    value = json.loads(
        text,
        object_pairs_hook=_reject_duplicate_keys,
        parse_constant=_reject_constant,
    )
    if not isinstance(value, dict):
        raise ValueError("snapshot JSON root must be an object")
    return value


def _diagnostic(
    code: str, path: str, message: str, remediation: str
) -> SnapshotDiagnosticV1:
    return SnapshotDiagnosticV1(
        code=code,
        severity="error",
        field_or_location=path,
        message=message,
        remediation=remediation,
    )


def _result(
    *,
    state: SnapshotOperationState,
    execution: Literal[
        "completed", "rejected_input", "not_run", "software_error", "cancelled"
    ],
    completeness: Literal["complete_for_scope", "partial"],
    freshness: Literal["current", "stale", "unbound"],
    diagnostic: SnapshotDiagnosticV1 | None,
    snapshot: AnalysisSnapshotV1 | None = None,
    provenance: SnapshotProvenanceV1 = _PROVENANCE,
) -> EtabsSnapshotResultV1:
    return EtabsSnapshotResultV1(
        operation_state=state,
        execution=execution,
        applicability="applicable" if snapshot is not None else "unknown",
        engineering="not_evaluated",
        completeness=completeness,
        freshness=freshness,
        approval="unreviewed",
        request_id=None,
        snapshot=snapshot,
        diagnostics=() if diagnostic is None else (diagnostic,),
        provenance=provenance,
    )


def _rejected(
    code: str, path: str, message: str, remediation: str
) -> EtabsSnapshotResultV1:
    return _result(
        state=SnapshotOperationState.PREFLIGHT_REJECTED,
        execution="rejected_input",
        completeness="partial",
        freshness="unbound",
        diagnostic=_diagnostic(code, path, message, remediation),
    )


def _blocked(
    code: str, path: str, message: str, remediation: str
) -> EtabsSnapshotResultV1:
    return _result(
        state=SnapshotOperationState.FENCED,
        execution="completed",
        completeness="partial",
        freshness="current",
        diagnostic=_diagnostic(code, path, message, remediation),
    )


def _uncertain(
    code: str, path: str, message: str, remediation: str
) -> EtabsSnapshotResultV1:
    return _result(
        state=SnapshotOperationState.TRANSACTION_UNCERTAIN,
        execution="not_run",
        completeness="partial",
        freshness="unbound",
        diagnostic=_diagnostic(code, path, message, remediation),
    )


def parse_analysis_snapshot_json(payload: str | bytes) -> EtabsSnapshotResultV1:
    """Strictly decode and validate a captured snapshot with no host access."""

    try:
        text = _checked_json_text(payload)
        _decode_json(text)
        snapshot = AnalysisSnapshotV1.model_validate_json(text)
    except (UnicodeDecodeError, ValueError, ValidationError) as exc:
        return _rejected(
            "INPUT.SCHEMA",
            "$",
            f"The portable snapshot does not match the strict version-1 schema: {exc}",
            "Correct the required fields, enum tokens, value types, and unknown fields.",
        )
    return validate_analysis_snapshot(snapshot)


def _ids(values: Iterable[Any], attribute: str) -> list[str]:
    return [str(getattr(value, attribute)) for value in values]


def _unique_ordered(values: Iterable[Any], attribute: str) -> bool:
    ids = _ids(values, attribute)
    return len(ids) == len(set(ids)) and ids == sorted(ids)


def _vector(value: Any) -> tuple[float, float, float]:
    return (value.x, value.y, value.z)


def _dot(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return sum(x * y for x, y in zip(a, b, strict=True))


def _cross(
    a: tuple[float, float, float], b: tuple[float, float, float]
) -> tuple[float, float, float]:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _valid_axes(axis: Any, tolerance: float = 1e-9) -> bool:
    vectors = (_vector(axis.e1), _vector(axis.e2), _vector(axis.e3))
    if any(abs(_dot(item, item) - 1) > tolerance for item in vectors):
        return False
    if any(
        abs(_dot(vectors[i], vectors[j])) > tolerance
        for i in range(3)
        for j in range(i + 1, 3)
    ):
        return False
    if any(
        abs(a - b) > tolerance
        for a, b in zip(_cross(vectors[0], vectors[1]), vectors[2], strict=True)
    ):
        return False
    rows = (
        axis.source_to_common.row_1,
        axis.source_to_common.row_2,
        axis.source_to_common.row_3,
    )
    if any(abs(_dot(item, item) - 1) > tolerance for item in rows):
        return False
    if any(
        abs(_dot(rows[i], rows[j])) > tolerance
        for i in range(3)
        for j in range(i + 1, 3)
    ):
        return False
    return all(
        abs(a - b) <= tolerance
        for a, b in zip(_cross(rows[0], rows[1]), rows[2], strict=True)
    )


def _validate_ledger(snapshot: AnalysisSnapshotV1) -> EtabsSnapshotResultV1 | None:
    ledger = snapshot.raw_capture.call_ledger
    records = ledger.records
    if (
        ledger.operation_id != snapshot.source_identity.acquisition_id
        or ledger.operation_id != snapshot.raw_capture.acquisition_id
    ):
        return _uncertain(
            "ETABS.LEDGER_UNFINALIZED",
            "raw_capture.call_ledger.operation_id",
            "The call ledger is not bound to the acquisition.",
            "Retain the exact acquisition identity in every call record and ledger.",
        )
    if ledger.record_count != len(records) or tuple(
        record.sequence for record in records
    ) != tuple(range(1, len(records) + 1)):
        return _uncertain(
            "ETABS.LEDGER_UNFINALIZED",
            "raw_capture.call_ledger.records",
            "The call ledger is truncated or has a sequence gap.",
            "Retain every started and returned record in sequence.",
        )
    previous: str | None = None
    pending: str | None = None
    for record in records:
        if (
            record.operation_id != ledger.operation_id
            or record.effect is not CallEffect.GETTER
        ):
            return _uncertain(
                "ETABS.LEDGER_UNFINALIZED",
                "raw_capture.call_ledger.records",
                "The call ledger contains an unbound or non-getter call.",
                "Capture getter-only calls under the same operation identity.",
            )
        if record.previous_record_sha256 != previous:
            return _uncertain(
                "ETABS.LEDGER_UNFINALIZED",
                "raw_capture.call_ledger.records",
                "The call-ledger chain is discontinuous.",
                "Preserve the previous record hash for every call stage.",
            )
        if record.stage is CallStage.STARTED:
            if pending is not None:
                return _uncertain(
                    "ETABS.LEDGER_UNFINALIZED",
                    "raw_capture.call_ledger.records",
                    "A second call started before the first returned.",
                    "Close each getter record before starting the next call.",
                )
            pending = record.call_id
        elif pending != record.call_id or record.return_code != 0:
            return _uncertain(
                "ETABS.LEDGER_UNFINALIZED",
                "raw_capture.call_ledger.records",
                "A getter did not return successfully against its started call.",
                "Retain the exact paired successful getter result.",
            )
        else:
            pending = None
        previous = record.record_sha256
    if pending is not None or ledger.head_record_sha256 != previous:
        return _uncertain(
            "ETABS.LEDGER_UNFINALIZED",
            "raw_capture.call_ledger",
            "The call ledger has an unmatched start or incorrect head.",
            "Finalize the durable getter ledger before normalization.",
        )
    for record in records:
        if call_record_sha256(record) != record.record_sha256:
            return _uncertain(
                "ETABS.LEDGER_INVALID",
                "raw_capture.call_ledger.records",
                "A call-record digest does not match its canonical payload.",
                "Reject or recapture the tampered call ledger.",
            )
    if call_ledger_sha256(ledger) != ledger.ledger_sha256:
        return _uncertain(
            "ETABS.LEDGER_INVALID",
            "raw_capture.call_ledger.ledger_sha256",
            "The call-ledger digest does not match its canonical payload.",
            "Reject or recapture the tampered call ledger.",
        )
    return None


def _validate_source(snapshot: AnalysisSnapshotV1) -> EtabsSnapshotResultV1 | None:
    source = snapshot.source_identity
    raw = snapshot.raw_capture
    for name in (
        "acquisition_id",
        "model_revision_id",
        "analysis_revision_id",
        "result_epoch_id",
    ):
        if getattr(source, name) != getattr(raw, name):
            return _blocked(
                "ETABS.IDENTITY_DRIFT",
                f"source_identity.{name}",
                "Source and raw-capture identities disagree.",
                "Reacquire one internally consistent source artifact.",
            )
    if (
        source.raw_capture_id != raw.raw_capture_id
        or source.raw_capture_sha256 != raw.raw_capture_sha256
    ):
        return _blocked(
            "ETABS.IDENTITY_DRIFT",
            "source_identity.raw_capture_id",
            "The snapshot does not bind its embedded raw capture.",
            "Bind the exact raw artifact id and digest.",
        )
    freshness = snapshot.freshness
    if freshness.state != "current" or any(
        getattr(freshness, name) != getattr(source, name)
        for name in ("model_revision_id", "analysis_revision_id", "result_epoch_id")
    ):
        return _blocked(
            "ETABS.RESULT_EPOCH_INVALID",
            "freshness",
            "The normalized snapshot is stale or bound to another analysis/result epoch.",
            "Acquire current completed results and rebuild the snapshot.",
        )
    if snapshot.metadata.analysis_status is not AnalysisCaseStatus.FINISHED:
        return _blocked(
            "ETABS.RESULT_EPOCH_INVALID",
            "metadata.analysis_status",
            "The source analysis is not recorded as finished.",
            "Select a completed result epoch before acquisition.",
        )
    selection_ids = _ids(snapshot.result_selections, "selection_id")
    if freshness.selection_ids != tuple(selection_ids):
        return _blocked(
            "ETABS.SELECTION_UNPROVED",
            "freshness.selection_ids",
            "Freshness does not bind the complete selected-result set.",
            "Retain the ordered selected-result identities.",
        )
    if any(not item.selected_for_output for item in snapshot.result_selections):
        return _blocked(
            "ETABS.SELECTION_UNPROVED",
            "result_selections",
            "A declared result source was not selected for output.",
            "Stop before force acquisition when selection is absent.",
        )
    if any(
        item.result_epoch_id != source.result_epoch_id
        for item in snapshot.result_selections
    ):
        return _blocked(
            "ETABS.RESULT_EPOCH_INVALID",
            "result_selections",
            "A selected result belongs to another result epoch.",
            "Reacquire selections and results under one epoch.",
        )
    return None


def _validate_units_axes(snapshot: AnalysisSnapshotV1) -> EtabsSnapshotResultV1 | None:
    units = snapshot.units
    if units.original_source_units != snapshot.raw_capture.source_units:
        return _blocked(
            "UNITS.INVALID",
            "units.original_source_units",
            "Snapshot and raw-capture source units differ.",
            "Record source units once and apply the declared conversion once.",
        )
    if (
        _sha256(units.original_source_units)
        != snapshot.normalization.source_units_sha256
    ):
        return _blocked(
            "UNITS.INVALID",
            "normalization.source_units_sha256",
            "The normalization record does not bind the source units.",
            "Hash the exact original unit record before conversion.",
        )
    if not all(_valid_axes(axis) for axis in snapshot.axes):
        return _blocked(
            "AXIS.UNRESOLVED",
            "axes",
            "An axis or source-to-common transform is not orthonormal and right-handed.",
            "Resolve axes and physical faces from retained geometry evidence.",
        )
    return None


def _validate_mapping(snapshot: AnalysisSnapshotV1) -> EtabsSnapshotResultV1 | None:
    ordered = (
        (snapshot.axes, "axis_id"),
        (snapshot.points, "point_id"),
        (snapshot.materials, "material_id"),
        (snapshot.sections, "section_id"),
        (snapshot.members, "member_id"),
        (snapshot.load_cases, "case_id"),
        (snapshot.load_combinations, "combination_id"),
        (snapshot.result_selections, "selection_id"),
        (snapshot.stations, "station_id"),
        (snapshot.action_rows, "row_id"),
    )
    if any(not _unique_ordered(values, key) for values, key in ordered):
        return _blocked(
            "SNAPSHOT.ORDER_INVALID",
            "$",
            "Portable arrays must have unique identities in deterministic order.",
            "Sort each identity-bearing collection before serialization.",
        )
    raw_model = snapshot.raw_capture.model_records
    if [record.source_record_id for record in raw_model] != sorted(
        record.source_record_id for record in raw_model
    ):
        return _blocked(
            "SNAPSHOT.ORDER_INVALID",
            "raw_capture.model_records",
            "Raw model records are not deterministically ordered.",
            "Sort raw model records by source_record_id.",
        )
    raw_forces = snapshot.raw_capture.force_rows
    if [(row.source_row_index, row.source_row_id) for row in raw_forces] != sorted(
        (row.source_row_index, row.source_row_id) for row in raw_forces
    ):
        return _blocked(
            "SNAPSHOT.ORDER_INVALID",
            "raw_capture.force_rows",
            "Raw force rows are not in source order.",
            "Preserve source-row ordinal then identity order.",
        )
    required_kinds = set(RawModelRecordKind)
    if {record.record_kind for record in raw_model} != required_kinds:
        return _blocked(
            "ETABS.MAPPING_UNRESOLVED",
            "raw_capture.model_records",
            "The raw capture omits a required model-fact record kind.",
            "Capture metadata, geometry, assignments, cases, combinations, selections, and stations.",
        )
    raw_ids = {record.source_record_id for record in raw_model}
    evidence_values = [snapshot.metadata.evidence_reference]
    for values in (
        snapshot.axes,
        snapshot.points,
        snapshot.materials,
        snapshot.sections,
        snapshot.members,
        snapshot.load_cases,
        snapshot.load_combinations,
        snapshot.result_selections,
        snapshot.stations,
    ):
        evidence_values.extend(item.evidence_reference for item in values)
    if any(value not in raw_ids for value in evidence_values):
        return _blocked(
            "ETABS.MAPPING_UNRESOLVED",
            "$",
            "A normalized model fact lacks a retained raw-record reference.",
            "Bind every normalized fact to one raw model record.",
        )
    axes = {item.axis_id: item for item in snapshot.axes}
    points = {item.point_id: item for item in snapshot.points}
    materials = {item.material_id: item for item in snapshot.materials}
    sections = {item.section_id: item for item in snapshot.sections}
    members = {item.member_id: item for item in snapshot.members}
    cases = {item.case_id: item for item in snapshot.load_cases}
    combinations = {item.combination_id: item for item in snapshot.load_combinations}
    selections = {item.selection_id: item for item in snapshot.result_selections}
    stations = {item.station_id: item for item in snapshot.stations}
    for section in snapshot.sections:
        if section.material_id not in materials:
            return _blocked(
                "ETABS.MAPPING_UNRESOLVED",
                "sections.material_id",
                "A section material assignment is unresolved.",
                "Retain the assigned material in the same snapshot.",
            )
    for member in snapshot.members:
        if (
            member.point_i_id not in points
            or member.point_j_id not in points
            or member.point_i_id == member.point_j_id
            or member.section_id not in sections
            or member.axis_id not in axes
        ):
            return _blocked(
                "ETABS.MAPPING_UNRESOLVED",
                "members",
                "A member geometry, section, or axis reference is unresolved.",
                "Retain complete member connectivity and assignments.",
            )
    for combination in snapshot.load_combinations:
        for factor in combination.factors:
            source = (
                cases
                if factor.source_kind is ResultSelectionKind.LOAD_CASE
                else combinations
            )
            if factor.source_id not in source:
                return _blocked(
                    "ETABS.MAPPING_UNRESOLVED",
                    "load_combinations.factors",
                    "A combination factor source is unresolved.",
                    "Retain every referenced case or combination.",
                )
    for selection in snapshot.result_selections:
        source = (
            cases if selection.kind is ResultSelectionKind.LOAD_CASE else combinations
        )
        if selection.source_id not in source:
            return _blocked(
                "ETABS.SELECTION_UNPROVED",
                "result_selections.source_id",
                "A selected case/combination definition is missing.",
                "Retain the selected result definition.",
            )
    for station in snapshot.stations:
        mapped_member = members.get(station.member_id)
        if (
            mapped_member is None
            or station.object_id != mapped_member.object_id
            or station.analysis_element_id not in mapped_member.analysis_element_ids
        ):
            return _blocked(
                "ETABS.MAPPING_UNRESOLVED",
                "stations",
                "A station's physical/object/element mapping is unresolved.",
                "Resolve all three station identities from retained topology evidence.",
            )
    call_records = snapshot.raw_capture.call_ledger.records
    returned = {
        item.call_id: item for item in call_records if item.stage is CallStage.RETURNED
    }
    raw_rows = {item.source_row_id: item for item in raw_forces}
    conversion = snapshot.units.conversion_to_canonical
    for row in snapshot.action_rows:
        mapped_station = stations.get(row.station_id)
        mapped_selection = selections.get(row.selection_id)
        raw = raw_rows.get(row.source_row_id)
        call = returned.get(row.provenance.call_id)
        if (
            mapped_station is None
            or mapped_selection is None
            or raw is None
            or call is None
        ):
            return _blocked(
                "ETABS.MAPPING_UNRESOLVED",
                "action_rows",
                "An action row lacks station, selection, raw-row, or getter evidence.",
                "Retain the complete provenance chain for each force row.",
            )
        if (row.member_id, row.object_id, row.analysis_element_id) != (
            mapped_station.member_id,
            mapped_station.object_id,
            mapped_station.analysis_element_id,
        ) or row.action_basis is not mapped_selection.action_basis:
            return _blocked(
                "ETABS.MAPPING_UNRESOLVED",
                "action_rows",
                "An action row conflicts with its station or selection mapping.",
                "Normalize from one mapped source row without rewriting identity.",
            )
        raw_identity = (
            raw.object_id,
            raw.analysis_element_id,
            raw.output_case_name,
            raw.step_type,
            raw.step_number,
        )
        normalized_identity = (
            row.object_id,
            row.analysis_element_id,
            row.output_case_name,
            row.step_type,
            row.step_number,
        )
        if (
            raw_identity != normalized_identity
            or row.output_case_name != mapped_selection.source_name
        ):
            return _blocked(
                "ETABS.MAPPING_UNRESOLVED",
                "action_rows",
                "An action row changes its source object, case, or step identity.",
                "Retain object, element, output case, step type, and step number from one source row.",
            )
        if (
            row.provenance.signature_authority_sha256 != call.signature_authority_sha256
            or row.provenance.source_row_index != raw.source_row_index
            or row.provenance.getter_method != call.method
            or row.provenance.evidence_reference != raw.source_row_id
        ):
            return _blocked(
                "ETABS.MAPPING_UNRESOLVED",
                "action_rows.provenance",
                "Force provenance conflicts with the raw getter evidence.",
                "Bind the exact returned getter call and source-row ordinal.",
            )
        expected_stations = (
            raw.object_station * conversion.length_to_mm,
            raw.element_station * conversion.length_to_mm,
        )
        actual_stations = (
            mapped_station.object_station_mm,
            mapped_station.element_station_mm,
        )
        if any(
            abs(left - right) > 1e-12
            for left, right in zip(expected_stations, actual_stations, strict=True)
        ):
            return _blocked(
                "ETABS.MAPPING_UNRESOLVED",
                "stations",
                "A normalized station conflicts with the retained source row.",
                "Convert object and element station from the same source row exactly once.",
            )
        expected = (
            raw.p * conversion.force_to_kn,
            raw.v2 * conversion.force_to_kn,
            raw.v3 * conversion.force_to_kn,
            raw.t * conversion.moment_to_knm,
            raw.m2 * conversion.moment_to_knm,
            raw.m3 * conversion.moment_to_knm,
        )
        actual = (row.p_kn, row.v2_kn, row.v3_kn, row.t_knm, row.m2_knm, row.m3_knm)
        if any(
            abs(left - right) > 1e-12
            for left, right in zip(expected, actual, strict=True)
        ):
            return _blocked(
                "UNITS.INVALID",
                "action_rows",
                "A normalized force component does not match the one-time source conversion.",
                "Normalize all six signed components from the same raw row.",
            )
        if analysis_action_row_id(row) != row.row_id:
            return _blocked(
                "SNAPSHOT.HASH_MISMATCH",
                "action_rows.row_id",
                "An action-row identity does not match its canonical payload.",
                "Regenerate the row identity from the complete same-row payload.",
            )
    return None


def _validate_row_ledger(snapshot: AnalysisSnapshotV1) -> EtabsSnapshotResultV1 | None:
    ledger = snapshot.row_ledger
    if ledger.blocked_count or any(
        row.disposition is RowDisposition.BLOCKED for row in ledger.rows
    ):
        return _blocked(
            "ETABS.ROW_BLOCKED",
            "row_ledger",
            "At least one required source row is blocked.",
            "Resolve or explicitly approve the row before creating a complete snapshot.",
        )
    source_ids = {
        item.source_record_id for item in snapshot.raw_capture.model_records
    } | {item.source_row_id for item in snapshot.raw_capture.force_rows}
    ledger_ids = [item.source_record_id for item in ledger.rows]
    if len(ledger_ids) != len(set(ledger_ids)) or set(ledger_ids) != source_ids:
        return _blocked(
            "ETABS.ROW_ACCOUNTING",
            "row_ledger.rows",
            "The row ledger does not account for every raw record exactly once.",
            "Reconcile raw and disposition identities without omission or duplication.",
        )
    action_source_ids = [item.source_row_id for item in snapshot.action_rows]
    if len(action_source_ids) != len(set(action_source_ids)):
        return _blocked(
            "ETABS.ROW_ACCOUNTING",
            "action_rows.source_row_id",
            "More than one canonical action row is bound to the same raw force row.",
            "Bind every raw force row to at most one canonical action row.",
        )
    action_by_source = {
        item.source_row_id: item.row_id for item in snapshot.action_rows
    }
    model_bindings = {
        RawModelRecordKind.MODEL_METADATA: (
            (snapshot.metadata.evidence_reference, snapshot.metadata.project_id),
        ),
        RawModelRecordKind.POINT: tuple(
            (item.evidence_reference, item.point_id) for item in snapshot.points
        ),
        RawModelRecordKind.MATERIAL: tuple(
            (item.evidence_reference, item.material_id) for item in snapshot.materials
        ),
        RawModelRecordKind.SECTION: tuple(
            (item.evidence_reference, item.section_id) for item in snapshot.sections
        ),
        RawModelRecordKind.MEMBER: tuple(
            (item.evidence_reference, item.member_id) for item in snapshot.members
        ),
        RawModelRecordKind.LOAD_CASE: tuple(
            (item.evidence_reference, item.case_id) for item in snapshot.load_cases
        ),
        RawModelRecordKind.LOAD_COMBINATION: tuple(
            (item.evidence_reference, item.combination_id)
            for item in snapshot.load_combinations
        ),
        RawModelRecordKind.RESULT_SELECTION: tuple(
            (item.evidence_reference, item.selection_id)
            for item in snapshot.result_selections
        ),
        RawModelRecordKind.STATION: tuple(
            (item.evidence_reference, item.station_id) for item in snapshot.stations
        ),
    }
    expected_model_rows: dict[str, tuple[str, str]] = {}
    for raw in snapshot.raw_capture.model_records:
        matches = [
            canonical_id
            for evidence_reference, canonical_id in model_bindings[raw.record_kind]
            if evidence_reference == raw.source_record_id
        ]
        if len(matches) != 1:
            return _blocked(
                "ETABS.ROW_ACCOUNTING",
                "row_ledger.rows",
                "A raw model row is not bound to exactly one canonical model fact.",
                "Bind each raw model row to one fact of the matching record kind.",
            )
        expected_model_rows[raw.source_record_id] = (
            raw.record_kind.value,
            matches[0],
        )
    for item in ledger.rows:
        if item.source_record_id in expected_model_rows:
            expected_kind, expected_id = expected_model_rows[item.source_record_id]
            if (
                item.record_kind != expected_kind
                or item.disposition is not RowDisposition.ACCEPTED
                or item.canonical_id != expected_id
            ):
                return _blocked(
                    "ETABS.ROW_ACCOUNTING",
                    "row_ledger.rows",
                    "An accepted model row is not bound to its canonical kind and identity.",
                    "Bind each accepted raw model row to its matching canonical model fact.",
                )
        elif item.source_record_id in action_by_source:
            if (
                item.record_kind != "force_row"
                or item.disposition is not RowDisposition.ACCEPTED
                or item.canonical_id != action_by_source[item.source_record_id]
            ):
                return _blocked(
                    "ETABS.ROW_ACCOUNTING",
                    "row_ledger.rows",
                    "An accepted action row is not bound to its canonical identity.",
                    "Bind each accepted raw force row to its action-row identity.",
                )
        elif (
            item.record_kind == "force_row"
            and item.disposition is RowDisposition.ACCEPTED
        ):
            return _blocked(
                "ETABS.ROW_ACCOUNTING",
                "row_ledger.rows",
                "An accepted raw force row has no canonical action row.",
                "Normalize or explicitly exclude every force row.",
            )
    return None


def validate_analysis_snapshot(snapshot: AnalysisSnapshotV1) -> EtabsSnapshotResultV1:
    """Validate cross-record invariants and return no partial accepted payload."""

    for validator in (
        _validate_ledger,
        _validate_source,
        _validate_row_ledger,
        _validate_units_axes,
        _validate_mapping,
    ):
        result = validator(snapshot)
        if result is not None:
            return result
    raw_sha = raw_capture_sha256(snapshot.raw_capture)
    expected_raw_id = f"raw_capture_id:{CANONICALIZATION_VERSION}:{raw_sha}"
    if (
        snapshot.raw_capture.raw_capture_sha256 != raw_sha
        or snapshot.raw_capture.raw_capture_id != expected_raw_id
    ):
        return _rejected(
            "RAW_CAPTURE.HASH_MISMATCH",
            "raw_capture",
            "The raw-capture identity or digest does not match its canonical bytes.",
            "Reject the artifact and recapture or restore the exact bytes.",
        )
    snapshot_sha = analysis_snapshot_sha256(snapshot)
    expected_snapshot_id = (
        f"analysis_snapshot_id:{CANONICALIZATION_VERSION}:{snapshot_sha}"
    )
    if (
        snapshot.snapshot_sha256 != snapshot_sha
        or snapshot.snapshot_id != expected_snapshot_id
    ):
        return _rejected(
            "SNAPSHOT.HASH_MISMATCH",
            "snapshot_sha256",
            "The snapshot identity or digest does not match its canonical hash basis.",
            "Reject the payload and replay from the intact raw capture.",
        )
    if snapshot.diagnostics:
        return _blocked(
            "SNAPSHOT.DIAGNOSTIC_BLOCK",
            "diagnostics",
            "An accepted snapshot cannot retain unresolved diagnostics.",
            "Resolve every diagnostic before accepting the snapshot.",
        )
    return _result(
        state=SnapshotOperationState.COMPLETED,
        execution="completed",
        completeness="complete_for_scope",
        freshness="current",
        diagnostic=None,
        snapshot=snapshot,
        provenance=snapshot.provenance,
    )


__all__ = [
    "analysis_action_row_id",
    "analysis_snapshot_sha256",
    "call_ledger_sha256",
    "call_record_sha256",
    "canonical_analysis_snapshot_json",
    "canonical_snapshot_json_bytes",
    "parse_analysis_snapshot_json",
    "parse_etabs_import_request_json",
    "raw_capture_sha256",
    "validate_analysis_snapshot",
]
