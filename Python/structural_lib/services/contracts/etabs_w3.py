# SPDX-License-Identifier: MIT
"""Strict W3 result-catalogue and beam-demand service contracts.

W3A consumes normalized immutable inputs only.  It neither imports COM nor
opens ETABS/Excel, and it links the accepted W2 baseline without changing it.
"""

from __future__ import annotations

import json
from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from enum import StrEnum
from hashlib import sha256
from typing import Any, Literal, Self

from pydantic import Field, model_validator

from structural_lib.core.analysis_contracts import (
    AnalysisStateV1,
    AnalysisStatusIdentityV1,
    BeamActionComponentV1,
    BeamActionRowV1,
    BeamDemandEnvelopeModeV1,
    BeamDemandEnvelopeRuleV1,
    BeamDemandScenarioV1,
    BeamDemandSnapshotV1,
    BeamGoverningReferenceV1,
    BeamGoverningSignV1,
    EvidenceStateV1,
    LoadCaseDefinitionV1,
    LoadPatternDefinitionV1,
    ResponseCombinationDefinitionV1,
    ResponseCombinationSourceKindV1,
    ResultSelectionIdentityV1,
    ResultSelectionKindV1,
    UnsupportedCaseParametersV1,
)
from structural_lib.services.contracts.common import StrictPublicModel
from structural_lib.services.etabs_beam_baseline import (
    ETABSBeamBaselineV1,
    ETABSForceStationV1,
    verify_etabs_beam_baseline_hash_v1,
)

__all__ = [
    "BeamActionPageV1",
    "BeamDemandBuildResultV1",
    "BeamDemandDerivationRequestV1",
    "ETABSResultCatalogueBuildRequestV1",
    "ETABSResultCatalogueBuildResultV1",
    "ETABSResultCatalogueCapacityV1",
    "ETABSResultCatalogueV1",
    "W3BuildIssueV1",
    "W3BuildStatusV1",
    "build_etabs_result_catalogue_v1",
    "canonical_beam_demand_snapshot_hash_basis_json_v1",
    "canonical_etabs_result_catalogue_hash_basis_json_v1",
    "derive_beam_demand_snapshot_v1",
    "query_beam_action_rows_v1",
    "verify_beam_demand_snapshot_hash_v1",
    "verify_etabs_result_catalogue_hash_v1",
]

_SHA256_PATTERN = r"^[0-9a-f]{64}$"
_MAX_CATALOGUE_ROWS = 100_000
_MAX_BASELINE_ACTION_ROWS = 500_000
_ACTION_VALUES = {
    BeamActionComponentV1.P: "p_kn",
    BeamActionComponentV1.V2: "v2_kn",
    BeamActionComponentV1.V3: "v3_kn",
    BeamActionComponentV1.T: "t_knm",
    BeamActionComponentV1.M2: "m2_knm",
    BeamActionComponentV1.M3: "m3_knm",
}


class W3BuildStatusV1(StrEnum):
    ACCEPTED = "ACCEPTED"
    BLOCKED = "BLOCKED"


class W3BuildIssueV1(StrictPublicModel):
    code: str = Field(min_length=1, max_length=120)
    path: str = Field(min_length=1, max_length=500)
    message: str = Field(min_length=1, max_length=1000)


class ETABSResultCatalogueCapacityV1(StrictPublicModel):
    load_pattern_count: int = Field(ge=0)
    load_case_count: int = Field(ge=0)
    analysis_status_count: int = Field(ge=0)
    response_combination_count: int = Field(ge=0)
    combination_factor_count: int = Field(ge=0)
    result_selection_count: int = Field(ge=0)
    total_source_row_count: int = Field(ge=0)
    accepted_capacity_limit: int = Field(ge=1, le=_MAX_CATALOGUE_ROWS)


class ETABSResultCatalogueBuildRequestV1(StrictPublicModel):
    schema_version: Literal["etabs-result-catalogue-build-request/v1"] = (
        "etabs-result-catalogue-build-request/v1"
    )
    model_identity_sha256: str = Field(pattern=_SHA256_PATTERN)
    runtime_identity_sha256: str = Field(pattern=_SHA256_PATTERN)
    getter_matrix_sha256: str = Field(pattern=_SHA256_PATTERN)
    load_patterns: tuple[LoadPatternDefinitionV1, ...]
    load_cases: tuple[LoadCaseDefinitionV1, ...]
    analysis_statuses: tuple[AnalysisStatusIdentityV1, ...]
    response_combinations: tuple[ResponseCombinationDefinitionV1, ...]
    result_selections: tuple[ResultSelectionIdentityV1, ...]
    capacity_limit: int = Field(
        default=_MAX_CATALOGUE_ROWS, ge=1, le=_MAX_CATALOGUE_ROWS
    )


class ETABSResultCatalogueV1(StrictPublicModel):
    schema_version: Literal["etabs-result-catalogue/v1"] = "etabs-result-catalogue/v1"
    hash_basis_version: Literal["etabs-result-catalogue-hash/v1"] = (
        "etabs-result-catalogue-hash/v1"
    )
    model_identity_sha256: str = Field(pattern=_SHA256_PATTERN)
    runtime_identity_sha256: str = Field(pattern=_SHA256_PATTERN)
    getter_matrix_sha256: str = Field(pattern=_SHA256_PATTERN)
    load_patterns: tuple[LoadPatternDefinitionV1, ...]
    load_cases: tuple[LoadCaseDefinitionV1, ...]
    analysis_statuses: tuple[AnalysisStatusIdentityV1, ...]
    response_combinations: tuple[ResponseCombinationDefinitionV1, ...]
    result_selections: tuple[ResultSelectionIdentityV1, ...]
    capacity: ETABSResultCatalogueCapacityV1
    catalogue_sha256: str = Field(pattern=_SHA256_PATTERN)


class ETABSResultCatalogueBuildResultV1(StrictPublicModel):
    schema_version: Literal["etabs-result-catalogue-build-result/v1"] = (
        "etabs-result-catalogue-build-result/v1"
    )
    status: W3BuildStatusV1 = Field(strict=False)
    issues: tuple[W3BuildIssueV1, ...]
    catalogue: ETABSResultCatalogueV1 | None

    @model_validator(mode="after")
    def validate_outcome(self) -> Self:
        if self.status is W3BuildStatusV1.ACCEPTED:
            if self.catalogue is None or self.issues:
                raise ValueError(
                    "accepted catalogue builds require one value and no issues"
                )
        elif self.catalogue is not None or not self.issues:
            raise ValueError(
                "blocked catalogue builds require issues and no partial value"
            )
        return self


class BeamDemandDerivationRequestV1(StrictPublicModel):
    schema_version: Literal["beam-demand-derivation-request/v1"] = (
        "beam-demand-derivation-request/v1"
    )
    baseline: ETABSBeamBaselineV1
    catalogue: ETABSResultCatalogueV1
    scenario: BeamDemandScenarioV1
    envelope_rules: tuple[BeamDemandEnvelopeRuleV1, ...] = Field(min_length=1)


class BeamDemandBuildResultV1(StrictPublicModel):
    schema_version: Literal["beam-demand-build-result/v1"] = (
        "beam-demand-build-result/v1"
    )
    status: W3BuildStatusV1 = Field(strict=False)
    issues: tuple[W3BuildIssueV1, ...]
    snapshot: BeamDemandSnapshotV1 | None

    @model_validator(mode="after")
    def validate_outcome(self) -> Self:
        if self.status is W3BuildStatusV1.ACCEPTED:
            if self.snapshot is None or self.issues:
                raise ValueError(
                    "accepted demand builds require one value and no issues"
                )
        elif self.snapshot is not None or not self.issues:
            raise ValueError(
                "blocked demand builds require issues and no partial value"
            )
        return self


class BeamActionPageV1(StrictPublicModel):
    """Lossless bounded page of retained W2 station rows.

    The exact public query accepts only a W2 baseline, so it cannot truthfully
    manufacture the catalogue-bound ``BeamActionRowV1`` projection.  Demand
    derivation creates that projection after both source hashes are available.
    """

    schema_version: Literal["beam-action-page/v1"] = "beam-action-page/v1"
    baseline_sha256: str = Field(pattern=_SHA256_PATTERN)
    total_count: int = Field(ge=0)
    returned_count: int = Field(ge=0)
    cursor: str | None
    next_cursor: str | None
    rows: tuple[ETABSForceStationV1, ...]

    @model_validator(mode="after")
    def validate_page(self) -> Self:
        if self.returned_count != len(self.rows):
            raise ValueError("returned_count must equal the number of rows")
        if self.returned_count > self.total_count:
            raise ValueError("returned_count cannot exceed total_count")
        return self


def _canonical_json(value: Mapping[str, Any] | Sequence[Any]) -> str:
    return json.dumps(value, allow_nan=False, separators=(",", ":"), sort_keys=True)


def _sha(value: Mapping[str, Any] | Sequence[Any]) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _stable_id(prefix: str, value: Mapping[str, Any]) -> str:
    return f"{prefix}:{_sha(value)[:24]}"


def _selection_id(kind: str, name: str) -> str:
    return _stable_id("result-selection", {"kind": kind, "name": name})


def _definition_sha(
    value: LoadCaseDefinitionV1 | ResponseCombinationDefinitionV1,
) -> str:
    payload = value.model_dump(mode="json")
    payload.pop("definition_sha256", None)
    return _sha(payload)


def _issue(code: str, path: str, message: str) -> W3BuildIssueV1:
    return W3BuildIssueV1(code=code, path=path, message=message)


def _duplicates(values: Iterable[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return tuple(sorted(duplicates))


def _validate_inventory_identity(
    label: str,
    ids: Sequence[str],
    names: Sequence[str],
    issues: list[W3BuildIssueV1],
) -> None:
    for value in _duplicates(ids):
        issues.append(
            _issue("DUPLICATE_STABLE_ID", label, f"duplicate stable ID {value!r}")
        )
    for value in _duplicates(names):
        issues.append(
            _issue("DUPLICATE_SOURCE_NAME", label, f"duplicate source name {value!r}")
        )


def _combination_cycles(
    combinations: Sequence[ResponseCombinationDefinitionV1],
) -> tuple[tuple[str, ...], ...]:
    graph = {
        combo.combination_id: tuple(
            factor.source_id
            for factor in combo.factors
            if factor.source_kind is ResponseCombinationSourceKindV1.COMBINATION
        )
        for combo in combinations
    }
    cycles: set[tuple[str, ...]] = set()
    visited: set[str] = set()
    stack: list[str] = []
    active: set[str] = set()

    def visit(node: str) -> None:
        if node in active:
            start = stack.index(node)
            cycle = tuple(stack[start:] + [node])
            rotations = [
                cycle[index:-1] + cycle[:index] for index in range(len(cycle) - 1)
            ]
            canonical = min(rotations)
            cycles.add(canonical + (canonical[0],))
            return
        if node in visited or node not in graph:
            return
        active.add(node)
        stack.append(node)
        for child in graph[node]:
            visit(child)
        stack.pop()
        active.remove(node)
        visited.add(node)

    for node in sorted(graph):
        visit(node)
    return tuple(sorted(cycles))


def build_etabs_result_catalogue_v1(
    request: ETABSResultCatalogueBuildRequestV1, /
) -> ETABSResultCatalogueBuildResultV1:
    """Validate normalized definition evidence and build one complete catalogue."""

    issues: list[W3BuildIssueV1] = []
    patterns = request.load_patterns
    cases = request.load_cases
    statuses = request.analysis_statuses
    combinations = request.response_combinations
    selections = request.result_selections

    _validate_inventory_identity(
        "load_patterns",
        [item.pattern_id for item in patterns],
        [item.name for item in patterns],
        issues,
    )
    _validate_inventory_identity(
        "load_cases",
        [item.case_id for item in cases],
        [item.name for item in cases],
        issues,
    )
    _validate_inventory_identity(
        "analysis_statuses",
        [item.status_id for item in statuses],
        [item.case_id for item in statuses],
        issues,
    )
    _validate_inventory_identity(
        "response_combinations",
        [item.combination_id for item in combinations],
        [item.name for item in combinations],
        issues,
    )
    _validate_inventory_identity(
        "result_selections",
        [item.selection_id for item in selections],
        [f"{item.kind.value}:{item.name}" for item in selections],
        issues,
    )

    for label, ordinals in (
        ("load_patterns", tuple(item.source_ordinal for item in patterns)),
        ("load_cases", tuple(item.source_ordinal for item in cases)),
        (
            "response_combinations",
            tuple(item.source_ordinal for item in combinations),
        ),
    ):
        if ordinals != tuple(range(len(ordinals))):
            issues.append(
                _issue(
                    "SOURCE_ORDINAL_GAP",
                    label,
                    "source ordinals must be unique, ordered, and contiguous from zero",
                )
            )

    status_by_id = {item.status_id: item for item in statuses}
    case_by_id = {item.case_id: item for item in cases}
    case_by_name = {item.name: item for item in cases}
    combo_by_id = {item.combination_id: item for item in combinations}
    combo_by_name = {item.name: item for item in combinations}

    for case in cases:
        status = status_by_id.get(case.analysis_status_id)
        if status is None or status.case_id != case.case_id:
            issues.append(
                _issue(
                    "ANALYSIS_STATUS_IDENTITY_MISSING",
                    f"load_cases:{case.case_id}",
                    "load case does not link to its exact analysis-status identity",
                )
            )
        if case.definition_sha256 != _definition_sha(case):
            issues.append(
                _issue(
                    "DEFINITION_DIGEST_MISMATCH",
                    f"load_cases:{case.case_id}",
                    "load-case definition digest does not match its canonical fields",
                )
            )

    for status in statuses:
        if status.case_id not in case_by_id:
            issues.append(
                _issue(
                    "ANALYSIS_STATUS_TARGET_MISSING",
                    f"analysis_statuses:{status.status_id}",
                    f"analysis status targets missing case {status.case_id!r}",
                )
            )

    for combination in combinations:
        if combination.definition_sha256 != _definition_sha(combination):
            issues.append(
                _issue(
                    "DEFINITION_DIGEST_MISMATCH",
                    f"response_combinations:{combination.combination_id}",
                    "response-combination digest does not match ordered canonical factors",
                )
            )
        for factor in combination.factors:
            if factor.source_kind is ResponseCombinationSourceKindV1.CASE:
                target_name = (
                    case_by_id[factor.source_id].name
                    if factor.source_id in case_by_id
                    else None
                )
            else:
                target_name = (
                    combo_by_id[factor.source_id].name
                    if factor.source_id in combo_by_id
                    else None
                )
            if target_name != factor.source_name:
                issues.append(
                    _issue(
                        "COMBINATION_FACTOR_TARGET_MISSING",
                        f"response_combinations:{combination.combination_id}.factors:{factor.ordinal}",
                        f"factor target {factor.source_kind.value}:{factor.source_id} is absent or name-mismatched",
                    )
                )

    for cycle in _combination_cycles(combinations):
        issues.append(
            _issue(
                "NESTED_COMBINATION_CYCLE",
                "response_combinations",
                "nested combination cycle: " + " -> ".join(cycle),
            )
        )

    for selection in selections:
        path = f"result_selections:{selection.selection_id}"
        expected_selection_id = _selection_id(selection.kind.value, selection.name)
        if selection.selection_id != expected_selection_id:
            issues.append(
                _issue(
                    "SELECTION_STABLE_ID_MISMATCH",
                    path,
                    f"selection_id must be {expected_selection_id!r} for lossless baseline paging",
                )
            )
        if selection.model_identity_sha256 != request.model_identity_sha256:
            issues.append(
                _issue(
                    "MODEL_IDENTITY_MISMATCH",
                    path,
                    "selection model identity differs from catalogue request",
                )
            )
        if selection.runtime_identity_sha256 != request.runtime_identity_sha256:
            issues.append(
                _issue(
                    "RUNTIME_IDENTITY_MISMATCH",
                    path,
                    "selection runtime identity differs from catalogue request",
                )
            )
        selected = selection.selected_for_output
        if selected.state is not EvidenceStateV1.PRESENT or selected.value is not True:
            issues.append(
                _issue(
                    "RESULT_SELECTION_NOT_ACTIVE",
                    path,
                    "accepted selections must prove selected_for_output=true",
                )
            )
        if selection.kind is ResultSelectionKindV1.CASE:
            selected_case = case_by_name.get(selection.name)
            status_id = selection.case_status_id.value
            status = status_by_id.get(status_id) if isinstance(status_id, str) else None
            if (
                selected_case is None
                or status is None
                or status.case_id != selected_case.case_id
            ):
                issues.append(
                    _issue(
                        "SELECTED_CASE_DEFINITION_UNPROVED",
                        path,
                        "selected case does not link to its exact definition and status",
                    )
                )
            elif status.state is not AnalysisStateV1.FINISHED:
                issues.append(
                    _issue(
                        "SELECTED_CASE_NOT_FINISHED",
                        path,
                        f"selected case status is {status.state.value}",
                    )
                )
        else:
            selected_combination = combo_by_name.get(selection.name)
            if (
                selected_combination is None
                or selection.combination_definition_id.value
                != selected_combination.combination_id
            ):
                issues.append(
                    _issue(
                        "SELECTED_COMBINATION_DEFINITION_UNPROVED",
                        path,
                        "selected combination does not link to its exact definition",
                    )
                )

    factor_count = sum(len(item.factors) for item in combinations)
    total_source_rows = (
        len(patterns)
        + len(cases)
        + len(statuses)
        + len(combinations)
        + factor_count
        + len(selections)
    )
    if total_source_rows > request.capacity_limit:
        issues.append(
            _issue(
                "CATALOGUE_CAPACITY_EXCEEDED",
                "capacity_limit",
                f"{total_source_rows} normalized rows exceed the declared limit {request.capacity_limit}",
            )
        )

    if issues:
        return ETABSResultCatalogueBuildResultV1(
            status=W3BuildStatusV1.BLOCKED,
            issues=tuple(issues),
            catalogue=None,
        )

    capacity = ETABSResultCatalogueCapacityV1(
        load_pattern_count=len(patterns),
        load_case_count=len(cases),
        analysis_status_count=len(statuses),
        response_combination_count=len(combinations),
        combination_factor_count=factor_count,
        result_selection_count=len(selections),
        total_source_row_count=total_source_rows,
        accepted_capacity_limit=request.capacity_limit,
    )
    provisional = ETABSResultCatalogueV1(
        model_identity_sha256=request.model_identity_sha256,
        runtime_identity_sha256=request.runtime_identity_sha256,
        getter_matrix_sha256=request.getter_matrix_sha256,
        load_patterns=patterns,
        load_cases=cases,
        analysis_statuses=statuses,
        response_combinations=combinations,
        result_selections=selections,
        capacity=capacity,
        catalogue_sha256="0" * 64,
    )
    catalogue = provisional.model_copy(
        update={
            "catalogue_sha256": sha256(
                canonical_etabs_result_catalogue_hash_basis_json_v1(provisional).encode(
                    "utf-8"
                )
            ).hexdigest()
        }
    )
    return ETABSResultCatalogueBuildResultV1(
        status=W3BuildStatusV1.ACCEPTED,
        issues=(),
        catalogue=catalogue,
    )


def canonical_etabs_result_catalogue_hash_basis_json_v1(
    catalogue: ETABSResultCatalogueV1, /
) -> str:
    payload = catalogue.model_dump(mode="json")
    payload.pop("catalogue_sha256", None)
    return _canonical_json(payload)


def verify_etabs_result_catalogue_hash_v1(catalogue: ETABSResultCatalogueV1, /) -> bool:
    digest = sha256(
        canonical_etabs_result_catalogue_hash_basis_json_v1(catalogue).encode("utf-8")
    ).hexdigest()
    return digest == catalogue.catalogue_sha256


def _baseline_rows(baseline: ETABSBeamBaselineV1) -> tuple[ETABSForceStationV1, ...]:
    rows = tuple(station for result in baseline.results for station in result.stations)
    if len(rows) > _MAX_BASELINE_ACTION_ROWS:
        raise ValueError(
            f"BEAM_ACTION_CAPACITY_EXCEEDED: {len(rows)} rows exceed {_MAX_BASELINE_ACTION_ROWS}"
        )
    return rows


def _decode_cursor(cursor: str | None, total: int) -> int:
    if cursor is None:
        return 0
    prefix = "beam-action-offset:"
    if not cursor.startswith(prefix):
        raise ValueError("BEAM_ACTION_CURSOR_INVALID: cursor prefix is invalid")
    raw = cursor.removeprefix(prefix)
    if not raw.isdecimal():
        raise ValueError("BEAM_ACTION_CURSOR_INVALID: cursor offset is invalid")
    offset = int(raw)
    if offset < 0 or offset > total:
        raise ValueError("BEAM_ACTION_CURSOR_INVALID: cursor is outside the result set")
    return offset


def query_beam_action_rows_v1(
    baseline: ETABSBeamBaselineV1,
    *,
    member_ids: tuple[str, ...] = (),
    selection_ids: tuple[str, ...] = (),
    cursor: str | None = None,
    limit: int = 1000,
) -> BeamActionPageV1:
    """Page retained W2 station rows without truncation or reinterpretation."""

    if not verify_etabs_beam_baseline_hash_v1(baseline):
        raise ValueError("ETABS_BASELINE_HASH_INVALID")
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 1000:
        raise ValueError(
            "BEAM_ACTION_LIMIT_INVALID: limit must be an integer from 1 to 1000"
        )
    if len(member_ids) != len(set(member_ids)) or len(selection_ids) != len(
        set(selection_ids)
    ):
        raise ValueError(
            "BEAM_ACTION_FILTER_INVALID: filters must be unique and ordered"
        )
    member_filter = set(member_ids)
    selection_filter = set(selection_ids)
    rows = tuple(
        row
        for row in _baseline_rows(baseline)
        if (not member_filter or row.member_id in member_filter)
        and (
            not selection_filter
            or _selection_id(row.selection.kind.value, row.selection.name)
            in selection_filter
        )
    )
    offset = _decode_cursor(cursor, len(rows))
    page_rows = rows[offset : offset + limit]
    next_offset = offset + len(page_rows)
    next_cursor = (
        f"beam-action-offset:{next_offset}" if next_offset < len(rows) else None
    )
    return BeamActionPageV1(
        baseline_sha256=baseline.baseline_sha256,
        total_count=len(rows),
        returned_count=len(page_rows),
        cursor=cursor,
        next_cursor=next_cursor,
        rows=page_rows,
    )


def _action_row_sha(row: BeamActionRowV1) -> str:
    payload = row.model_dump(mode="json")
    payload.pop("row_sha256", None)
    return _sha(payload)


def _project_action_rows(
    baseline: ETABSBeamBaselineV1,
    catalogue: ETABSResultCatalogueV1,
    scenario: BeamDemandScenarioV1,
) -> tuple[BeamActionRowV1, ...]:
    selection_by_key = {
        (item.kind.value, item.name): item for item in catalogue.result_selections
    }
    wanted_selections = set(scenario.included_selection_ids)
    wanted_members = set(scenario.member_ids)
    projected: list[BeamActionRowV1] = []
    for station in _baseline_rows(baseline):
        selection = selection_by_key.get(
            (station.selection.kind.value, station.selection.name)
        )
        if selection is None or selection.selection_id not in wanted_selections:
            continue
        if wanted_members and station.member_id not in wanted_members:
            continue
        provisional = BeamActionRowV1(
            row_id=station.station_id,
            model_identity_sha256=catalogue.model_identity_sha256,
            baseline_sha256=baseline.baseline_sha256,
            catalogue_sha256=catalogue.catalogue_sha256,
            member_id=station.member_id,
            source_frame_name=station.source_frame_name,
            station_id=station.station_id,
            selection_id=selection.selection_id,
            selection_kind=selection.kind,
            selection_name=selection.name,
            output_case_name=station.selection.name,
            object_name=station.object_name,
            object_station_mm=station.object_station_mm,
            element_name=station.element_name,
            element_station_mm=station.element_station_mm,
            step_type=station.step_type,
            step_number=station.step_number,
            source_row_index=station.source_row_index,
            p_kn=station.p_kn,
            v2_kn=station.v2_kn,
            v3_kn=station.v3_kn,
            t_knm=station.t_knm,
            m2_knm=station.m2_knm,
            m3_knm=station.m3_knm,
            local_axis_basis="ETABS retained frame local axes; signed components are not transformed",
            row_sha256="0" * 64,
        )
        projected.append(
            provisional.model_copy(update={"row_sha256": _action_row_sha(provisional)})
        )
    return tuple(projected)


def _component_value(row: BeamActionRowV1, component: BeamActionComponentV1) -> float:
    return float(getattr(row, _ACTION_VALUES[component]))


def _reference(
    *,
    scenario: BeamDemandScenarioV1,
    member_id: str,
    component: BeamActionComponentV1,
    sign: BeamGoverningSignV1,
    rule: BeamDemandEnvelopeRuleV1,
    value: float,
    rows: Sequence[BeamActionRowV1],
    concurrent: bool,
) -> BeamGoverningReferenceV1:
    row_ids = tuple(row.row_id for row in rows)
    selection_ids = tuple(dict.fromkeys(row.selection_id for row in rows))
    identity = {
        "scenario_id": scenario.scenario_id,
        "member_id": member_id,
        "component": component.value,
        "sign": sign.value,
        "rule_id": rule.rule_id,
        "action_row_ids": row_ids,
    }
    return BeamGoverningReferenceV1(
        reference_id=_stable_id("beam-governing", identity),
        scenario_id=scenario.scenario_id,
        member_id=member_id,
        component=component,
        sign=sign,
        rule_id=rule.rule_id,
        governing_value=value,
        action_row_ids=row_ids,
        selection_ids=selection_ids,
        is_concurrent=concurrent,
        tie_break_policy=scenario.tie_break_policy,
        tie_break_basis="lowest source_row_index, then lexical row_id",
    )


def _ordered_rows(rows: Sequence[BeamActionRowV1]) -> tuple[BeamActionRowV1, ...]:
    return tuple(sorted(rows, key=lambda row: (row.source_row_index, row.row_id)))


def _governing_references(
    scenario: BeamDemandScenarioV1,
    rules: Sequence[BeamDemandEnvelopeRuleV1],
    action_rows: Sequence[BeamActionRowV1],
) -> tuple[BeamGoverningReferenceV1, ...]:
    by_member: dict[str, list[BeamActionRowV1]] = defaultdict(list)
    for row in action_rows:
        by_member[row.member_id].append(row)
    references: list[BeamGoverningReferenceV1] = []
    row_by_id = {row.row_id: row for row in action_rows}
    for member_id in sorted(by_member):
        rows = _ordered_rows(by_member[member_id])
        for rule in rules:
            if rule.mode is BeamDemandEnvelopeModeV1.SAME_ROW_CONCURRENT:
                assert rule.primary_component is not None
                primary_component = rule.primary_component
                selected = min(
                    rows,
                    key=lambda row: (
                        -abs(_component_value(row, primary_component)),
                        row.source_row_index,
                        row.row_id,
                    ),
                )
                for component in rule.components:
                    references.append(
                        _reference(
                            scenario=scenario,
                            member_id=member_id,
                            component=component,
                            sign=BeamGoverningSignV1.CONCURRENT,
                            rule=rule,
                            value=_component_value(selected, component),
                            rows=(selected,),
                            concurrent=True,
                        )
                    )
            elif rule.mode is BeamDemandEnvelopeModeV1.SIGNED_COMPONENT_EXTREMA:
                for component in rule.components:
                    positive = min(
                        rows,
                        key=lambda row: (
                            -_component_value(row, component),
                            row.source_row_index,
                            row.row_id,
                        ),
                    )
                    negative = min(
                        rows,
                        key=lambda row: (
                            _component_value(row, component),
                            row.source_row_index,
                            row.row_id,
                        ),
                    )
                    for sign, selected in (
                        (BeamGoverningSignV1.POSITIVE, positive),
                        (BeamGoverningSignV1.NEGATIVE, negative),
                    ):
                        references.append(
                            _reference(
                                scenario=scenario,
                                member_id=member_id,
                                component=component,
                                sign=sign,
                                rule=rule,
                                value=_component_value(selected, component),
                                rows=(selected,),
                                concurrent=True,
                            )
                        )
            elif rule.mode is BeamDemandEnvelopeModeV1.INDEPENDENT_ABSOLUTE_COMPONENTS:
                for component in rule.components:
                    selected = min(
                        rows,
                        key=lambda row: (
                            -abs(_component_value(row, component)),
                            row.source_row_index,
                            row.row_id,
                        ),
                    )
                    references.append(
                        _reference(
                            scenario=scenario,
                            member_id=member_id,
                            component=component,
                            sign=BeamGoverningSignV1.ABSOLUTE,
                            rule=rule,
                            value=_component_value(selected, component),
                            rows=(selected,),
                            concurrent=False,
                        )
                    )
            else:
                selected_rows = tuple(
                    row_by_id[row_id]
                    for row_id in rule.contributing_action_row_ids
                    if row_id in row_by_id and row_by_id[row_id].member_id == member_id
                )
                if not selected_rows:
                    continue
                for component in rule.components:
                    selected = min(
                        selected_rows,
                        key=lambda row: (
                            -abs(_component_value(row, component)),
                            row.source_row_index,
                            row.row_id,
                        ),
                    )
                    references.append(
                        _reference(
                            scenario=scenario,
                            member_id=member_id,
                            component=component,
                            sign=BeamGoverningSignV1.CALLER_DEFINED,
                            rule=rule,
                            value=_component_value(selected, component),
                            rows=selected_rows,
                            concurrent=len(selected_rows) == 1,
                        )
                    )
    return tuple(references)


def _selected_case_ids(
    selection: ResultSelectionIdentityV1,
    catalogue: ETABSResultCatalogueV1,
) -> set[str]:
    if selection.kind is ResultSelectionKindV1.CASE:
        status_id = selection.case_status_id.value
        status = next(
            (
                item
                for item in catalogue.analysis_statuses
                if item.status_id == status_id
            ),
            None,
        )
        return {status.case_id} if status is not None else set()
    root = selection.combination_definition_id.value
    combinations = {
        item.combination_id: item for item in catalogue.response_combinations
    }
    result: set[str] = set()
    pending = [root] if isinstance(root, str) else []
    visited: set[str] = set()
    while pending:
        combination_id = pending.pop()
        if combination_id in visited:
            continue
        visited.add(combination_id)
        combination = combinations.get(combination_id)
        if combination is None:
            continue
        for factor in combination.factors:
            if factor.source_kind is ResponseCombinationSourceKindV1.CASE:
                result.add(factor.source_id)
            else:
                pending.append(factor.source_id)
    return result


def derive_beam_demand_snapshot_v1(
    request: BeamDemandDerivationRequestV1, /
) -> BeamDemandBuildResultV1:
    """Derive deterministic governing references from retained same-row actions."""

    baseline = request.baseline
    catalogue = request.catalogue
    scenario = request.scenario
    issues: list[W3BuildIssueV1] = []
    if not verify_etabs_beam_baseline_hash_v1(baseline):
        issues.append(
            _issue(
                "ETABS_BASELINE_HASH_INVALID",
                "baseline",
                "W2 baseline canonical hash verification failed",
            )
        )
    if not verify_etabs_result_catalogue_hash_v1(catalogue):
        issues.append(
            _issue(
                "ETABS_CATALOGUE_HASH_INVALID",
                "catalogue",
                "catalogue canonical hash verification failed",
            )
        )
    if scenario.baseline_sha256 != baseline.baseline_sha256:
        issues.append(
            _issue(
                "BASELINE_IDENTITY_MISMATCH",
                "scenario.baseline_sha256",
                "scenario does not bind the supplied baseline",
            )
        )
    if scenario.catalogue_sha256 != catalogue.catalogue_sha256:
        issues.append(
            _issue(
                "CATALOGUE_IDENTITY_MISMATCH",
                "scenario.catalogue_sha256",
                "scenario does not bind the supplied catalogue",
            )
        )
    if (
        baseline.model.file_evidence.before_read.sha256
        != catalogue.model_identity_sha256
    ):
        issues.append(
            _issue(
                "MODEL_IDENTITY_MISMATCH",
                "catalogue.model_identity_sha256",
                "catalogue model digest differs from the W2 authorized model digest",
            )
        )

    selection_by_id = {item.selection_id: item for item in catalogue.result_selections}
    for selection_id in scenario.included_selection_ids:
        selection = selection_by_id.get(selection_id)
        if selection is None:
            issues.append(
                _issue(
                    "SCENARIO_SELECTION_MISSING",
                    f"scenario.included_selection_ids:{selection_id}",
                    "scenario references an absent catalogue selection",
                )
            )
            continue
        for case_id in sorted(_selected_case_ids(selection, catalogue)):
            case = next(
                (item for item in catalogue.load_cases if item.case_id == case_id), None
            )
            if case is None or isinstance(case.parameters, UnsupportedCaseParametersV1):
                issues.append(
                    _issue(
                        "SCENARIO_CASE_PARAMETERS_BLOCKED",
                        f"load_cases:{case_id}",
                        "accepted scenarios require PRESENT supported case parameters",
                    )
                )

    rule_by_id = {rule.rule_id: rule for rule in request.envelope_rules}
    if len(rule_by_id) != len(request.envelope_rules):
        issues.append(
            _issue(
                "DUPLICATE_ENVELOPE_RULE_ID",
                "envelope_rules",
                "envelope rule IDs must be unique",
            )
        )
    selected_rules: list[BeamDemandEnvelopeRuleV1] = []
    for rule_id in scenario.envelope_rule_ids:
        rule = rule_by_id.get(rule_id)
        if rule is None:
            issues.append(
                _issue(
                    "SCENARIO_RULE_MISSING",
                    f"scenario.envelope_rule_ids:{rule_id}",
                    "scenario references an absent envelope rule",
                )
            )
        else:
            selected_rules.append(rule)
    covered = {component for rule in selected_rules for component in rule.components}
    missing_components = [
        component.value
        for component in scenario.required_components
        if component not in covered
    ]
    if missing_components:
        issues.append(
            _issue(
                "SCENARIO_COMPONENT_UNCOVERED",
                "scenario.required_components",
                "no selected rule covers: " + ", ".join(missing_components),
            )
        )
    if issues:
        return BeamDemandBuildResultV1(
            status=W3BuildStatusV1.BLOCKED, issues=tuple(issues), snapshot=None
        )

    action_rows = _project_action_rows(baseline, catalogue, scenario)
    if not action_rows:
        return BeamDemandBuildResultV1(
            status=W3BuildStatusV1.BLOCKED,
            issues=(
                _issue(
                    "SCENARIO_ACTION_ROWS_MISSING",
                    "baseline.results",
                    "no retained W2 station rows match the scenario member/selection domain",
                ),
            ),
            snapshot=None,
        )
    referenced_ids = {row.row_id for row in action_rows}
    for rule in selected_rules:
        missing = [
            row_id
            for row_id in rule.contributing_action_row_ids
            if row_id not in referenced_ids
        ]
        if missing:
            issues.append(
                _issue(
                    "CALLER_DEFINED_ACTION_ROW_MISSING",
                    f"envelope_rules:{rule.rule_id}",
                    "caller-defined rule references rows outside the scenario: "
                    + ", ".join(missing),
                )
            )
    if issues:
        return BeamDemandBuildResultV1(
            status=W3BuildStatusV1.BLOCKED, issues=tuple(issues), snapshot=None
        )

    references = _governing_references(scenario, selected_rules, action_rows)
    if not references:
        return BeamDemandBuildResultV1(
            status=W3BuildStatusV1.BLOCKED,
            issues=(
                _issue(
                    "GOVERNING_REFERENCE_MISSING",
                    "envelope_rules",
                    "selected rules produced no governing reference",
                ),
            ),
            snapshot=None,
        )
    limitations = tuple(
        dict.fromkeys(
            "Independent absolute component references are screening-only and are not concurrent."
            for rule in selected_rules
            if rule.mode is BeamDemandEnvelopeModeV1.INDEPENDENT_ABSOLUTE_COMPONENTS
        )
    )
    provisional = BeamDemandSnapshotV1(
        scenario=scenario,
        model_identity_sha256=catalogue.model_identity_sha256,
        baseline_sha256=baseline.baseline_sha256,
        catalogue_sha256=catalogue.catalogue_sha256,
        retained_action_row_count=len(action_rows),
        member_count=len({row.member_id for row in action_rows}),
        governing_references=references,
        limitations=limitations,
        snapshot_sha256="0" * 64,
    )
    snapshot = provisional.model_copy(
        update={
            "snapshot_sha256": sha256(
                canonical_beam_demand_snapshot_hash_basis_json_v1(provisional).encode(
                    "utf-8"
                )
            ).hexdigest()
        }
    )
    return BeamDemandBuildResultV1(
        status=W3BuildStatusV1.ACCEPTED, issues=(), snapshot=snapshot
    )


def canonical_beam_demand_snapshot_hash_basis_json_v1(
    snapshot: BeamDemandSnapshotV1, /
) -> str:
    payload = snapshot.model_dump(mode="json")
    payload.pop("snapshot_sha256", None)
    return _canonical_json(payload)


def verify_beam_demand_snapshot_hash_v1(snapshot: BeamDemandSnapshotV1, /) -> bool:
    digest = sha256(
        canonical_beam_demand_snapshot_hash_basis_json_v1(snapshot).encode("utf-8")
    ).hexdigest()
    return digest == snapshot.snapshot_sha256
