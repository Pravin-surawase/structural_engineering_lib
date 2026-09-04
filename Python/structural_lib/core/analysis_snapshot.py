# SPDX-License-Identifier: MIT
"""Portable contracts for host-free ETABS capture and analysis snapshots.

The records in this module contain no COM, CSI, Excel, filesystem, solver, or
optimizer behavior.  A Windows adapter may populate them later; ordinary
Python callers can validate and replay the same immutable evidence offline.
"""

from __future__ import annotations

import re
from enum import StrEnum
from typing import Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

SHA256_PATTERN = r"^[0-9a-f]{64}$"
UTC_PATTERN = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$"
SEMANTIC_ID = "etabs.beam_snapshot.import/v1"
SNAPSHOT_SCHEMA_VERSION = "structural.analysis_snapshot/v1"
RAW_CAPTURE_SCHEMA_VERSION = "structural.analysis_raw_capture/v1"
REQUEST_SCHEMA_VERSION = "etabs.beam_snapshot.import-request/v1"
RESULT_SCHEMA_VERSION = "etabs.beam_snapshot.import-result/v1"


class _StrictModel(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        allow_inf_nan=False,
    )


class OptionalEvidenceState(StrEnum):
    SUPPLIED = "supplied"
    NOT_REQUESTED = "not_requested"
    UNAVAILABLE = "unavailable"
    NOT_APPLICABLE = "not_applicable"


class MemberSelectionMode(StrEnum):
    ALL_BEAMS = "all_beams"
    EXPLICIT = "explicit"


class StationSelectionMode(StrEnum):
    ALL_AVAILABLE = "all_available"
    EXPLICIT = "explicit"


class ResultKind(StrEnum):
    FRAME_FORCE = "frame_force"


class CallStage(StrEnum):
    STARTED = "started"
    RETURNED = "returned"


class CallEffect(StrEnum):
    GETTER = "getter"


class RawModelRecordKind(StrEnum):
    MODEL_METADATA = "model_metadata"
    POINT = "point"
    MATERIAL = "material"
    SECTION = "section"
    MEMBER = "member"
    LOAD_CASE = "load_case"
    LOAD_COMBINATION = "load_combination"
    RESULT_SELECTION = "result_selection"
    STATION = "station"


class SectionShape(StrEnum):
    RECTANGULAR = "rectangular"
    GENERAL = "general"


class SectionAssignmentKind(StrEnum):
    DIRECT = "direct"
    AUTO_SELECT = "auto_select"


class LoadCaseKind(StrEnum):
    LINEAR_STATIC = "linear_static"
    MODAL = "modal"
    RESPONSE_SPECTRUM = "response_spectrum"
    OTHER = "other"


class AnalysisCaseStatus(StrEnum):
    FINISHED = "finished"
    NOT_FINISHED = "not_finished"


class CombinationKind(StrEnum):
    LINEAR_ADD = "linear_add"
    ENVELOPE = "envelope"
    OTHER = "other"


class ResultSelectionKind(StrEnum):
    LOAD_CASE = "load_case"
    LOAD_COMBINATION = "load_combination"


class ActionBasis(StrEnum):
    STATIC_CONCURRENT = "static_concurrent"
    STAGED_STEP = "staged_step"
    RESPONSE_RESULT = "response_result"
    COMPONENT_ENVELOPE = "component_envelope"
    DESIGN_ENVELOPE = "design_envelope"


class StationSide(StrEnum):
    CONTINUOUS = "continuous"
    BEFORE = "before"
    AFTER = "after"


class RowDisposition(StrEnum):
    ACCEPTED = "accepted"
    APPROVED_EXCLUSION = "approved_exclusion"
    BLOCKED = "blocked"


class SnapshotOperationState(StrEnum):
    PREFLIGHT_ACCEPTED = "preflight_accepted"
    COMPLETED = "completed"
    PREFLIGHT_REJECTED = "preflight_rejected"
    FENCED = "fenced"
    TRANSACTION_UNCERTAIN = "transaction_uncertain"
    CANCELLED = "cancelled"


class PortableOptionalTextV1(_StrictModel):
    state: OptionalEvidenceState = Field(strict=False)
    value: str | None
    reason_code: str | None

    @model_validator(mode="after")
    def validate_state(self) -> Self:
        if self.state is OptionalEvidenceState.SUPPLIED:
            if (
                self.value is None
                or not self.value.strip()
                or self.reason_code is not None
            ):
                raise ValueError("supplied optional evidence requires only a value")
        elif (
            self.value is not None
            or self.reason_code is None
            or not self.reason_code.strip()
        ):
            raise ValueError("non-supplied optional evidence requires only a reason")
        return self


class PortableOptionalSha256V1(PortableOptionalTextV1):
    @model_validator(mode="after")
    def validate_supplied_sha256(self) -> Self:
        if self.state is OptionalEvidenceState.SUPPLIED and not re.fullmatch(
            SHA256_PATTERN, self.value or ""
        ):
            raise ValueError("supplied SHA-256 evidence must be lowercase hex")
        return self


class EtabsSourceExpectationV1(_StrictModel):
    source_system: Literal["etabs"] = "etabs"
    source_version: str = Field(min_length=1)
    model_revision_id: str = Field(min_length=1)
    process_identity: PortableOptionalTextV1
    model_file_sha256: PortableOptionalSha256V1


class MemberSelectionV1(_StrictModel):
    mode: MemberSelectionMode = Field(strict=False)
    member_ids: tuple[str, ...]

    @model_validator(mode="after")
    def validate_mode(self) -> Self:
        if self.mode is MemberSelectionMode.EXPLICIT and not self.member_ids:
            raise ValueError("explicit member selection requires member_ids")
        if self.mode is MemberSelectionMode.ALL_BEAMS and self.member_ids:
            raise ValueError("all_beams member selection cannot carry member_ids")
        if len(set(self.member_ids)) != len(self.member_ids):
            raise ValueError("member_ids must be unique")
        return self


class StationSelectionV1(_StrictModel):
    mode: StationSelectionMode = Field(strict=False)
    station_ids: tuple[str, ...]

    @model_validator(mode="after")
    def validate_mode(self) -> Self:
        if self.mode is StationSelectionMode.EXPLICIT and not self.station_ids:
            raise ValueError("explicit station selection requires station_ids")
        if self.mode is StationSelectionMode.ALL_AVAILABLE and self.station_ids:
            raise ValueError("all_available station selection cannot carry station_ids")
        if len(set(self.station_ids)) != len(self.station_ids):
            raise ValueError("station_ids must be unique")
        return self


class EtabsImportScopeV1(_StrictModel):
    project_id: str = Field(min_length=1)
    members: MemberSelectionV1
    result_selection_ids: tuple[str, ...] = Field(min_length=1)
    result_kinds: tuple[ResultKind, ...] = Field(min_length=1)
    stations: StationSelectionV1

    @model_validator(mode="after")
    def validate_unique(self) -> Self:
        if len(set(self.result_selection_ids)) != len(self.result_selection_ids):
            raise ValueError("result_selection_ids must be unique")
        if len(set(self.result_kinds)) != len(self.result_kinds):
            raise ValueError("result_kinds must be unique")
        return self


class EtabsImportRequestV1(_StrictModel):
    schema_version: Literal["etabs.beam_snapshot.import-request/v1"] = (
        "etabs.beam_snapshot.import-request/v1"
    )
    operation_semantic_id: Literal["etabs.beam_snapshot.import/v1"] = (
        "etabs.beam_snapshot.import/v1"
    )
    request_id: str = Field(min_length=1)
    source_expectation: EtabsSourceExpectationV1
    scope: EtabsImportScopeV1
    required_provenance: tuple[str, ...] = Field(min_length=1)
    deadline_utc: str = Field(pattern=UTC_PATTERN)

    @model_validator(mode="after")
    def validate_provenance(self) -> Self:
        if len(set(self.required_provenance)) != len(self.required_provenance):
            raise ValueError("required_provenance must be unique")
        return self


class SourceUnitBasisV1(_StrictModel):
    length: str = Field(min_length=1)
    force: str = Field(min_length=1)
    moment: str = Field(min_length=1)
    stress: str = Field(min_length=1)
    mass_density: str = Field(min_length=1)


class UnitConversionV1(_StrictModel):
    length_to_mm: float = Field(gt=0)
    force_to_kn: float = Field(gt=0)
    moment_to_knm: float = Field(gt=0)
    stress_to_n_per_mm2: float = Field(gt=0)
    mass_density_to_kg_per_m3: float = Field(gt=0)


class SnapshotUnitBasisV1(_StrictModel):
    length: Literal["mm"] = "mm"
    force: Literal["kN"] = "kN"
    moment: Literal["kNm"] = "kNm"
    stress: Literal["N/mm2"] = "N/mm2"
    mass_density: Literal["kg/m3"] = "kg/m3"
    original_source_units: SourceUnitBasisV1
    conversion_to_canonical: UnitConversionV1


class SnapshotCallRecordV1(_StrictModel):
    schema_version: Literal["structural.analysis_call_record/v1"] = (
        "structural.analysis_call_record/v1"
    )
    operation_id: str = Field(min_length=1)
    call_id: str = Field(min_length=1)
    sequence: int = Field(ge=1)
    previous_record_sha256: str | None = Field(default=None, pattern=SHA256_PATTERN)
    stage: CallStage = Field(strict=False)
    method: str = Field(min_length=1)
    signature_authority_sha256: str = Field(pattern=SHA256_PATTERN)
    effect: CallEffect = Field(strict=False)
    arguments_sha256: str = Field(pattern=SHA256_PATTERN)
    return_code: int | None
    raw_shape: str | None
    recorded_at_utc: str = Field(pattern=UTC_PATTERN)
    record_sha256: str = Field(pattern=SHA256_PATTERN)

    @model_validator(mode="after")
    def validate_stage(self) -> Self:
        if self.stage is CallStage.STARTED:
            if self.return_code is not None or self.raw_shape is not None:
                raise ValueError("started call records cannot carry returned values")
        elif self.return_code is None or self.raw_shape is None or not self.raw_shape:
            raise ValueError("returned call records require return_code and raw_shape")
        return self


class SnapshotCallLedgerV1(_StrictModel):
    schema_version: Literal["structural.analysis_call_ledger/v1"] = (
        "structural.analysis_call_ledger/v1"
    )
    operation_id: str = Field(min_length=1)
    record_count: int = Field(ge=0)
    head_record_sha256: str | None = Field(default=None, pattern=SHA256_PATTERN)
    ledger_sha256: str = Field(pattern=SHA256_PATTERN)
    records: tuple[SnapshotCallRecordV1, ...]


class RawModelRecordV1(_StrictModel):
    record_kind: RawModelRecordKind = Field(strict=False)
    source_record_id: str = Field(min_length=1)
    fields: dict[str, Any]


class RawForceRowV1(_StrictModel):
    source_row_id: str = Field(min_length=1)
    source_row_index: int = Field(ge=0)
    object_id: str = Field(min_length=1)
    analysis_element_id: str = Field(min_length=1)
    object_station: float
    element_station: float
    output_case_name: str = Field(min_length=1)
    step_type: str = Field(min_length=1)
    step_number: float | None
    p: float
    v2: float
    v3: float
    t: float
    m2: float
    m3: float


class RawAnalysisCaptureV1(_StrictModel):
    schema_version: Literal["structural.analysis_raw_capture/v1"] = (
        "structural.analysis_raw_capture/v1"
    )
    raw_capture_id: str = Field(min_length=1)
    raw_capture_sha256: str = Field(pattern=SHA256_PATTERN)
    acquisition_id: str = Field(min_length=1)
    model_revision_id: str = Field(min_length=1)
    analysis_revision_id: str = Field(min_length=1)
    result_epoch_id: str = Field(min_length=1)
    source_units: SourceUnitBasisV1
    call_ledger: SnapshotCallLedgerV1
    model_records: tuple[RawModelRecordV1, ...] = Field(min_length=1)
    force_rows: tuple[RawForceRowV1, ...] = Field(min_length=1)


class SnapshotSourceIdentityV1(_StrictModel):
    source_system: Literal["etabs"] = "etabs"
    source_version: str = Field(min_length=1)
    adapter_semantic_id: Literal["etabs.beam_snapshot.import/v1"] = (
        "etabs.beam_snapshot.import/v1"
    )
    adapter_build_id: str = Field(min_length=1)
    acquisition_id: str = Field(min_length=1)
    raw_capture_id: str = Field(min_length=1)
    raw_capture_sha256: str = Field(pattern=SHA256_PATTERN)
    model_revision_id: str = Field(min_length=1)
    analysis_revision_id: str = Field(min_length=1)
    result_epoch_id: str = Field(min_length=1)
    runtime_fingerprint: str = Field(min_length=1)
    process_identity: PortableOptionalTextV1
    model_file_sha256: PortableOptionalSha256V1


class SnapshotMetadataV1(_StrictModel):
    project_id: str = Field(min_length=1)
    model_name: str = Field(min_length=1)
    model_guid: PortableOptionalTextV1
    model_locked: bool
    analysis_status: AnalysisCaseStatus = Field(strict=False)
    evidence_reference: str = Field(min_length=1)


class Vector3V1(_StrictModel):
    x: float
    y: float
    z: float


class Matrix3V1(_StrictModel):
    row_1: tuple[float, float, float]
    row_2: tuple[float, float, float]
    row_3: tuple[float, float, float]


class SnapshotAxisV1(_StrictModel):
    axis_id: str = Field(min_length=1)
    e1: Vector3V1
    e2: Vector3V1
    e3: Vector3V1
    source_to_common: Matrix3V1
    physical_top_face: Literal["positive_local_2", "negative_local_2"]
    physical_left_face: Literal["positive_local_3", "negative_local_3"]
    evidence_reference: str = Field(min_length=1)


class SnapshotPointV1(_StrictModel):
    point_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    x_mm: float
    y_mm: float
    z_mm: float
    story_id: str = Field(min_length=1)
    evidence_reference: str = Field(min_length=1)


class SnapshotMaterialV1(_StrictModel):
    material_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    material_kind: str = Field(min_length=1)
    elastic_modulus_n_per_mm2: float = Field(gt=0)
    poisson_ratio: float = Field(gt=-1, lt=0.5)
    mass_density_kg_per_m3: float = Field(ge=0)
    evidence_reference: str = Field(min_length=1)


class SnapshotSectionV1(_StrictModel):
    section_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    shape: SectionShape = Field(strict=False)
    material_id: str = Field(min_length=1)
    area_mm2: float = Field(gt=0)
    torsional_constant_mm4: float = Field(gt=0)
    inertia_2_mm4: float = Field(gt=0)
    inertia_3_mm4: float = Field(gt=0)
    width_mm: float | None
    depth_mm: float | None
    evidence_reference: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_dimensions(self) -> Self:
        rectangular = self.shape is SectionShape.RECTANGULAR
        if rectangular != (self.width_mm is not None and self.depth_mm is not None):
            raise ValueError("rectangular sections require width and depth only")
        if self.width_mm is not None and self.width_mm <= 0:
            raise ValueError("section width must be positive")
        if self.depth_mm is not None and self.depth_mm <= 0:
            raise ValueError("section depth must be positive")
        return self


class SnapshotModifiersV1(_StrictModel):
    axial_area: float = Field(ge=0)
    shear_area_2: float = Field(ge=0)
    shear_area_3: float = Field(ge=0)
    torsion: float = Field(ge=0)
    inertia_2: float = Field(ge=0)
    inertia_3: float = Field(ge=0)
    mass: float = Field(ge=0)
    weight: float = Field(ge=0)


class SnapshotOffsetsV1(_StrictModel):
    automatic: bool
    end_i_mm: float = Field(ge=0)
    end_j_mm: float = Field(ge=0)
    rigid_zone_factor: float = Field(ge=0, le=1)


class SnapshotEndReleasesV1(_StrictModel):
    u1: bool
    u2: bool
    u3: bool
    r1: bool
    r2: bool
    r3: bool


class SnapshotReleasesV1(_StrictModel):
    end_i: SnapshotEndReleasesV1
    end_j: SnapshotEndReleasesV1


class SnapshotMemberV1(_StrictModel):
    member_id: str = Field(min_length=1)
    object_id: str = Field(min_length=1)
    source_label: str = Field(min_length=1)
    story_id: str = Field(min_length=1)
    point_i_id: str = Field(min_length=1)
    point_j_id: str = Field(min_length=1)
    section_id: str = Field(min_length=1)
    axis_id: str = Field(min_length=1)
    assignment_kind: SectionAssignmentKind = Field(strict=False)
    auto_select_list_id: str | None
    modifiers: SnapshotModifiersV1
    offsets: SnapshotOffsetsV1
    releases: SnapshotReleasesV1
    analysis_element_ids: tuple[str, ...] = Field(min_length=1)
    evidence_reference: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_assignment(self) -> Self:
        if self.assignment_kind is SectionAssignmentKind.AUTO_SELECT:
            if self.auto_select_list_id is None or not self.auto_select_list_id:
                raise ValueError("auto-select assignment requires list identity")
        elif self.auto_select_list_id is not None:
            raise ValueError("direct assignment cannot carry an auto-select list")
        return self


class SnapshotLoadCaseV1(_StrictModel):
    case_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    case_kind: LoadCaseKind = Field(strict=False)
    status: AnalysisCaseStatus = Field(strict=False)
    evidence_reference: str = Field(min_length=1)


class SnapshotCombinationFactorV1(_StrictModel):
    ordinal: int = Field(ge=0)
    source_kind: ResultSelectionKind = Field(strict=False)
    source_id: str = Field(min_length=1)
    scale_factor: float


class SnapshotLoadCombinationV1(_StrictModel):
    combination_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    combination_kind: CombinationKind = Field(strict=False)
    factors: tuple[SnapshotCombinationFactorV1, ...] = Field(min_length=1)
    evidence_reference: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_ordinals(self) -> Self:
        if tuple(item.ordinal for item in self.factors) != tuple(
            range(len(self.factors))
        ):
            raise ValueError("combination-factor ordinals must be contiguous")
        return self


class SnapshotResultSelectionV1(_StrictModel):
    selection_id: str = Field(min_length=1)
    kind: ResultSelectionKind = Field(strict=False)
    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    selected_for_output: bool
    action_basis: ActionBasis = Field(strict=False)
    result_epoch_id: str = Field(min_length=1)
    evidence_reference: str = Field(min_length=1)


class SnapshotStationV1(_StrictModel):
    station_id: str = Field(min_length=1)
    member_id: str = Field(min_length=1)
    object_id: str = Field(min_length=1)
    analysis_element_id: str = Field(min_length=1)
    physical_station_mm: float = Field(ge=0)
    object_station_mm: float = Field(ge=0)
    element_station_mm: float = Field(ge=0)
    normalized_ratio: float = Field(ge=0, le=1)
    side: StationSide = Field(strict=False)
    evidence_reference: str = Field(min_length=1)


class ForceResultProvenanceV1(_StrictModel):
    getter_method: str = Field(min_length=1)
    signature_authority_sha256: str = Field(pattern=SHA256_PATTERN)
    call_id: str = Field(min_length=1)
    source_row_index: int = Field(ge=0)
    concurrency_basis: str = Field(min_length=1)
    evidence_reference: str = Field(min_length=1)


class SnapshotActionRowV1(_StrictModel):
    row_id: str = Field(min_length=1)
    source_row_id: str = Field(min_length=1)
    member_id: str = Field(min_length=1)
    object_id: str = Field(min_length=1)
    analysis_element_id: str = Field(min_length=1)
    station_id: str = Field(min_length=1)
    selection_id: str = Field(min_length=1)
    output_case_name: str = Field(min_length=1)
    step_type: str = Field(min_length=1)
    step_number: float | None
    action_basis: ActionBasis = Field(strict=False)
    p_kn: float
    v2_kn: float
    v3_kn: float
    t_knm: float
    m2_knm: float
    m3_knm: float
    force_unit: Literal["kN"] = "kN"
    moment_unit: Literal["kNm"] = "kNm"
    provenance: ForceResultProvenanceV1

    @model_validator(mode="after")
    def validate_step(self) -> Self:
        requires_step = self.action_basis in (
            ActionBasis.STAGED_STEP,
            ActionBasis.RESPONSE_RESULT,
        )
        if requires_step != (self.step_number is not None):
            raise ValueError("only staged/response actions require step_number")
        return self


class SnapshotRowDispositionV1(_StrictModel):
    source_record_id: str = Field(min_length=1)
    record_kind: str = Field(min_length=1)
    disposition: RowDisposition = Field(strict=False)
    canonical_id: str | None
    reason_code: str | None
    approval_reference: str | None
    diagnostic_codes: tuple[str, ...]

    @model_validator(mode="after")
    def validate_disposition(self) -> Self:
        if self.disposition is RowDisposition.ACCEPTED:
            if (
                self.canonical_id is None
                or self.reason_code is not None
                or self.approval_reference is not None
                or self.diagnostic_codes
            ):
                raise ValueError("accepted rows require only canonical_id")
        elif self.disposition is RowDisposition.APPROVED_EXCLUSION:
            if (
                self.canonical_id is not None
                or not self.reason_code
                or not self.approval_reference
                or self.diagnostic_codes
            ):
                raise ValueError("approved exclusions require reason and approval")
        elif (
            self.canonical_id is not None
            or not self.reason_code
            or not self.diagnostic_codes
        ):
            raise ValueError("blocked rows require reason and diagnostics")
        return self


class SnapshotRowLedgerV1(_StrictModel):
    source_row_count: int = Field(ge=0)
    accepted_count: int = Field(ge=0)
    approved_exclusion_count: int = Field(ge=0)
    blocked_count: int = Field(ge=0)
    rows: tuple[SnapshotRowDispositionV1, ...]

    @model_validator(mode="after")
    def validate_counts(self) -> Self:
        counts = {
            RowDisposition.ACCEPTED: self.accepted_count,
            RowDisposition.APPROVED_EXCLUSION: self.approved_exclusion_count,
            RowDisposition.BLOCKED: self.blocked_count,
        }
        if self.source_row_count != len(self.rows) or self.source_row_count != sum(
            counts.values()
        ):
            raise ValueError("row-ledger totals must conserve every source row")
        if any(
            sum(row.disposition is state for row in self.rows) != count
            for state, count in counts.items()
        ):
            raise ValueError("row-ledger disposition counts do not match rows")
        return self


class SnapshotNormalizationV1(_StrictModel):
    rule_id: Literal["structural.analysis_snapshot.normalize/v1"] = (
        "structural.analysis_snapshot.normalize/v1"
    )
    conversion_performed_once: Literal[True] = True
    source_units_sha256: str = Field(pattern=SHA256_PATTERN)


class SnapshotFreshnessV1(_StrictModel):
    state: Literal["current", "stale", "unbound"]
    model_revision_id: str = Field(min_length=1)
    analysis_revision_id: str = Field(min_length=1)
    result_epoch_id: str = Field(min_length=1)
    selection_ids: tuple[str, ...] = Field(min_length=1)


class SnapshotDiagnosticV1(_StrictModel):
    code: str = Field(min_length=1)
    severity: Literal["error", "warning", "info"]
    field_or_location: str = Field(min_length=1)
    message: str = Field(min_length=1)
    remediation: str | None


class SnapshotProvenanceV1(_StrictModel):
    contract_revision_id: Literal["wp10-analysis-snapshot-contract-v1"] = (
        "wp10-analysis-snapshot-contract-v1"
    )
    source_references: tuple[str, ...] = Field(min_length=1)
    limitations: tuple[str, ...]


class AnalysisSnapshotV1(_StrictModel):
    schema_version: Literal["structural.analysis_snapshot/v1"] = (
        "structural.analysis_snapshot/v1"
    )
    operation_semantic_id: Literal["etabs.beam_snapshot.import/v1"] = (
        "etabs.beam_snapshot.import/v1"
    )
    snapshot_id: str = Field(min_length=1)
    snapshot_sha256: str = Field(pattern=SHA256_PATTERN)
    created_at_utc: str = Field(pattern=UTC_PATTERN)
    source_identity: SnapshotSourceIdentityV1
    metadata: SnapshotMetadataV1
    units: SnapshotUnitBasisV1
    axes: tuple[SnapshotAxisV1, ...] = Field(min_length=1)
    points: tuple[SnapshotPointV1, ...] = Field(min_length=2)
    materials: tuple[SnapshotMaterialV1, ...] = Field(min_length=1)
    sections: tuple[SnapshotSectionV1, ...] = Field(min_length=1)
    members: tuple[SnapshotMemberV1, ...] = Field(min_length=1)
    load_cases: tuple[SnapshotLoadCaseV1, ...] = Field(min_length=1)
    load_combinations: tuple[SnapshotLoadCombinationV1, ...]
    result_selections: tuple[SnapshotResultSelectionV1, ...] = Field(min_length=1)
    stations: tuple[SnapshotStationV1, ...] = Field(min_length=1)
    action_rows: tuple[SnapshotActionRowV1, ...] = Field(min_length=1)
    row_ledger: SnapshotRowLedgerV1
    normalization: SnapshotNormalizationV1
    freshness: SnapshotFreshnessV1
    diagnostics: tuple[SnapshotDiagnosticV1, ...]
    provenance: SnapshotProvenanceV1
    evidence_manifest_sha256: str = Field(pattern=SHA256_PATTERN)
    raw_capture: RawAnalysisCaptureV1


class EtabsSnapshotResultV1(_StrictModel):
    schema_version: Literal["etabs.beam_snapshot.import-result/v1"] = (
        "etabs.beam_snapshot.import-result/v1"
    )
    operation_semantic_id: Literal["etabs.beam_snapshot.import/v1"] = (
        "etabs.beam_snapshot.import/v1"
    )
    operation_state: SnapshotOperationState = Field(strict=False)
    execution: Literal[
        "completed", "rejected_input", "not_run", "software_error", "cancelled"
    ]
    applicability: Literal["applicable", "not_applicable", "unknown"]
    engineering: Literal["pass", "fail", "not_evaluated"]
    completeness: Literal["complete_for_scope", "partial"]
    freshness: Literal["current", "stale", "unbound"]
    approval: Literal["unreviewed", "checked", "approved", "rejected"]
    request_id: str | None
    snapshot: AnalysisSnapshotV1 | None
    diagnostics: tuple[SnapshotDiagnosticV1, ...]
    provenance: SnapshotProvenanceV1

    @model_validator(mode="after")
    def validate_snapshot_state(self) -> Self:
        if self.operation_state is SnapshotOperationState.COMPLETED:
            if self.snapshot is None or self.completeness != "complete_for_scope":
                raise ValueError("completed result requires a complete snapshot")
        elif self.snapshot is not None:
            raise ValueError("non-completed result cannot expose a snapshot")
        return self


__all__ = [name for name in globals() if name.endswith("V1")] + [
    "ActionBasis",
    "AnalysisCaseStatus",
    "CallEffect",
    "CallStage",
    "CombinationKind",
    "LoadCaseKind",
    "MemberSelectionMode",
    "OptionalEvidenceState",
    "RawModelRecordKind",
    "ResultKind",
    "ResultSelectionKind",
    "RowDisposition",
    "SectionAssignmentKind",
    "SectionShape",
    "SnapshotOperationState",
    "StationSelectionMode",
    "StationSide",
]
