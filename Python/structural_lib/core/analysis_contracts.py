# SPDX-License-Identifier: MIT
"""Vendor-neutral immutable analysis, evidence, and demand contracts.

These contracts deliberately contain no ETABS, COM, Excel, design-code, solver,
or optimizer dependency.  Source adapters normalize their evidence into these
types; downstream services may then derive auditable demand views without
changing the retained source rows.
"""

from __future__ import annotations

import re
from enum import StrEnum
from typing import Annotated, Generic, Literal, Self, TypeVar

from pydantic import BaseModel, ConfigDict, Field, model_validator

__all__ = [
    "AnalysisStateV1",
    "AnalysisStatusIdentityV1",
    "BeamActionComponentV1",
    "BeamActionRowV1",
    "BeamDemandEnvelopeModeV1",
    "BeamDemandEnvelopeRuleV1",
    "BeamDemandPurposeV1",
    "BeamDemandScenarioV1",
    "BeamDemandSnapshotV1",
    "BeamGoverningReferenceV1",
    "BeamGoverningSignV1",
    "BeamStationDomainV1",
    "DeterministicTieBreakV1",
    "EvidenceStateV1",
    "EvidenceValueV1",
    "LinearStaticCaseParametersV1",
    "LinearStaticInitialConditionV1",
    "LinearStaticLoadItemV1",
    "LoadCaseDefinitionV1",
    "LoadCaseParameterSetV1",
    "LoadCaseParameterSetKindV1",
    "LoadPatternDefinitionV1",
    "ResponseCombinationDefinitionV1",
    "ResponseCombinationFactorV1",
    "ResponseCombinationSourceKindV1",
    "ResultSelectionIdentityV1",
    "ResultSelectionKindV1",
    "UnsupportedCaseParametersV1",
]

_SHA256_PATTERN = r"^[0-9a-f]{64}$"
_UTC_PATTERN = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$"
_IDENTITY_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:/@+() -]{0,159}$")


class _AnalysisContractModel(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        str_strip_whitespace=True,
        allow_inf_nan=False,
        validate_default=True,
    )


class EvidenceStateV1(StrEnum):
    """Exhaustive public meaning of a calculation-bearing optional value."""

    PRESENT = "PRESENT"
    UNAVAILABLE = "UNAVAILABLE"
    NOT_REQUESTED = "NOT_REQUESTED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    BLOCKED = "BLOCKED"


EvidenceT = TypeVar("EvidenceT")


class EvidenceValueV1(_AnalysisContractModel, Generic[EvidenceT]):
    """Typed value plus an explicit, non-null-overloaded evidence state."""

    state: EvidenceStateV1 = Field(strict=False)
    value: EvidenceT | None = None
    reason_code: str | None = Field(default=None, min_length=1, max_length=120)
    message: str | None = Field(default=None, min_length=1, max_length=500)
    source_references: tuple[str, ...] = Field(min_length=1, max_length=64)

    @model_validator(mode="after")
    def validate_state_value_contract(self) -> Self:
        if self.state is EvidenceStateV1.PRESENT:
            if self.value is None:
                raise ValueError("PRESENT evidence requires a non-null value")
            if self.reason_code is not None or self.message is not None:
                raise ValueError("PRESENT evidence forbids reason_code and message")
        else:
            if self.value is not None:
                raise ValueError("non-PRESENT evidence requires a null value")
            if self.reason_code is None or self.message is None:
                raise ValueError(
                    "non-PRESENT evidence requires a stable reason_code and message"
                )
        if len(set(self.source_references)) != len(self.source_references):
            raise ValueError("source_references must be unique and ordered")
        return self


class LoadCaseParameterSetKindV1(StrEnum):
    LINEAR_STATIC = "LINEAR_STATIC"
    UNSUPPORTED = "UNSUPPORTED"


class AnalysisStateV1(StrEnum):
    NOT_RUN = "NOT_RUN"
    COULD_NOT_START = "COULD_NOT_START"
    NOT_FINISHED = "NOT_FINISHED"
    FINISHED = "FINISHED"
    UNKNOWN = "UNKNOWN"


class ResponseCombinationSourceKindV1(StrEnum):
    CASE = "CASE"
    COMBINATION = "COMBINATION"


class ResultSelectionKindV1(StrEnum):
    CASE = "CASE"
    COMBINATION = "COMBINATION"


class BeamDemandPurposeV1(StrEnum):
    STRENGTH = "STRENGTH"
    SERVICE = "SERVICE"
    COMPARISON = "COMPARISON"


class BeamDemandEnvelopeModeV1(StrEnum):
    SAME_ROW_CONCURRENT = "SAME_ROW_CONCURRENT"
    SIGNED_COMPONENT_EXTREMA = "SIGNED_COMPONENT_EXTREMA"
    INDEPENDENT_ABSOLUTE_COMPONENTS = "INDEPENDENT_ABSOLUTE_COMPONENTS"
    CALLER_DEFINED_CODE_ENVELOPE = "CALLER_DEFINED_CODE_ENVELOPE"


class BeamActionComponentV1(StrEnum):
    P = "P"
    V2 = "V2"
    V3 = "V3"
    T = "T"
    M2 = "M2"
    M3 = "M3"


class BeamGoverningSignV1(StrEnum):
    CONCURRENT = "CONCURRENT"
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    ABSOLUTE = "ABSOLUTE"
    CALLER_DEFINED = "CALLER_DEFINED"


class DeterministicTieBreakV1(StrEnum):
    SOURCE_ROW_INDEX_THEN_ROW_ID = "SOURCE_ROW_INDEX_THEN_ROW_ID"


class BeamStationDomainV1(StrEnum):
    ALL_RETAINED = "ALL_RETAINED"


class LoadPatternDefinitionV1(_AnalysisContractModel):
    pattern_id: str = Field(min_length=1, max_length=160)
    name: str = Field(min_length=1, max_length=160)
    raw_type: str = Field(min_length=1, max_length=160)
    normalized_type: str = Field(min_length=1, max_length=160)
    self_weight_multiplier: float
    source_ordinal: int = Field(ge=0)
    evidence_reference: str = Field(min_length=1, max_length=500)


class LinearStaticLoadItemV1(_AnalysisContractModel):
    ordinal: int = Field(ge=0)
    load_type: str = Field(min_length=1, max_length=160)
    load_name: str = Field(min_length=1, max_length=160)
    scale_factor: float
    evidence_reference: str = Field(min_length=1, max_length=500)


class LinearStaticInitialConditionV1(_AnalysisContractModel):
    """Installed zero-state sentinel retained without accepting prior cases."""

    raw_initial_case: str = Field(max_length=160)
    normalized_condition: Literal["ZERO_UNSTRESSED"] = "ZERO_UNSTRESSED"
    evidence_reference: str = Field(min_length=1, max_length=500)

    @model_validator(mode="after")
    def validate_zero_state_sentinel(self) -> Self:
        if self.raw_initial_case.strip().casefold() not in {"", "none"}:
            raise ValueError(
                "zero-state linear-static initial condition accepts only blank or None"
            )
        return self


class LinearStaticCaseParametersV1(_AnalysisContractModel):
    parameter_kind: Literal[LoadCaseParameterSetKindV1.LINEAR_STATIC] = (
        LoadCaseParameterSetKindV1.LINEAR_STATIC
    )
    initial_condition: LinearStaticInitialConditionV1
    load_items: tuple[LinearStaticLoadItemV1, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_order(self) -> Self:
        if tuple(item.ordinal for item in self.load_items) != tuple(
            range(len(self.load_items))
        ):
            raise ValueError(
                "linear-static load-item ordinals must be contiguous from zero"
            )
        return self


class UnsupportedCaseParametersV1(_AnalysisContractModel):
    parameter_kind: Literal[LoadCaseParameterSetKindV1.UNSUPPORTED] = (
        LoadCaseParameterSetKindV1.UNSUPPORTED
    )
    raw_type: str = Field(min_length=1, max_length=160)
    raw_subtype: str = Field(min_length=1, max_length=160)
    parameter_evidence: EvidenceValueV1[bool]

    @model_validator(mode="after")
    def reject_false_present_support(self) -> Self:
        if self.parameter_evidence.state is EvidenceStateV1.PRESENT:
            raise ValueError("unsupported case parameters cannot use PRESENT evidence")
        return self


LoadCaseParameterSetV1 = Annotated[
    LinearStaticCaseParametersV1 | UnsupportedCaseParametersV1,
    Field(discriminator="parameter_kind"),
]


class AnalysisStatusIdentityV1(_AnalysisContractModel):
    status_id: str = Field(min_length=1, max_length=160)
    case_id: str = Field(min_length=1, max_length=160)
    raw_status_code: int = Field(ge=0)
    state: AnalysisStateV1 = Field(strict=False)
    getter_identity: str = Field(min_length=1, max_length=500)
    signature_identity: str = Field(pattern=_SHA256_PATTERN)
    model_observation_before: str = Field(min_length=1, max_length=500)
    model_observation_after: str = Field(min_length=1, max_length=500)
    observed_at_utc: str = Field(pattern=_UTC_PATTERN)
    evidence_reference: str = Field(min_length=1, max_length=500)


class LoadCaseDefinitionV1(_AnalysisContractModel):
    case_id: str = Field(min_length=1, max_length=160)
    name: str = Field(min_length=1, max_length=160)
    raw_type: str = Field(min_length=1, max_length=160)
    raw_subtype: str = Field(min_length=1, max_length=160)
    raw_design_type: str = Field(min_length=1, max_length=160)
    raw_auto_flag: int
    is_auto: EvidenceValueV1[bool]
    parameters: LoadCaseParameterSetV1
    analysis_status_id: str = Field(min_length=1, max_length=160)
    source_ordinal: int = Field(ge=0)
    evidence_reference: str = Field(min_length=1, max_length=500)
    definition_sha256: str = Field(pattern=_SHA256_PATTERN)


class ResponseCombinationFactorV1(_AnalysisContractModel):
    ordinal: int = Field(ge=0)
    source_kind: ResponseCombinationSourceKindV1 = Field(strict=False)
    source_id: str = Field(min_length=1, max_length=160)
    source_name: str = Field(min_length=1, max_length=160)
    scale_factor: float
    evidence_reference: str = Field(min_length=1, max_length=500)


class ResponseCombinationDefinitionV1(_AnalysisContractModel):
    combination_id: str = Field(min_length=1, max_length=160)
    name: str = Field(min_length=1, max_length=160)
    raw_type: str = Field(min_length=1, max_length=160)
    normalized_type: str = Field(min_length=1, max_length=160)
    factors: tuple[ResponseCombinationFactorV1, ...] = Field(min_length=1)
    design_purpose: EvidenceValueV1[str]
    source_ordinal: int = Field(ge=0)
    evidence_reference: str = Field(min_length=1, max_length=500)
    definition_sha256: str = Field(pattern=_SHA256_PATTERN)

    @model_validator(mode="after")
    def validate_order(self) -> Self:
        if tuple(item.ordinal for item in self.factors) != tuple(
            range(len(self.factors))
        ):
            raise ValueError("combination-factor ordinals must be contiguous from zero")
        return self


class ResultSelectionIdentityV1(_AnalysisContractModel):
    selection_id: str = Field(min_length=1, max_length=160)
    kind: ResultSelectionKindV1 = Field(strict=False)
    name: str = Field(min_length=1, max_length=160)
    selected_for_output: EvidenceValueV1[bool]
    case_status_id: EvidenceValueV1[str]
    combination_definition_id: EvidenceValueV1[str]
    model_identity_sha256: str = Field(pattern=_SHA256_PATTERN)
    runtime_identity_sha256: str = Field(pattern=_SHA256_PATTERN)
    getter_identity_sha256: str = Field(pattern=_SHA256_PATTERN)
    model_observation_before: str = Field(min_length=1, max_length=500)
    model_observation_after: str = Field(min_length=1, max_length=500)
    evidence_reference: str = Field(min_length=1, max_length=500)

    @model_validator(mode="after")
    def validate_link_kind(self) -> Self:
        if self.kind is ResultSelectionKindV1.CASE:
            expected = self.case_status_id
            other = self.combination_definition_id
        else:
            expected = self.combination_definition_id
            other = self.case_status_id
        if expected.state is not EvidenceStateV1.PRESENT:
            raise ValueError("selection kind requires its linked definition identity")
        if other.state is not EvidenceStateV1.NOT_APPLICABLE:
            raise ValueError(
                "selection kind requires the other linked identity to be NOT_APPLICABLE"
            )
        return self


class BeamActionRowV1(_AnalysisContractModel):
    row_id: str = Field(min_length=1, max_length=160)
    model_identity_sha256: str = Field(pattern=_SHA256_PATTERN)
    baseline_sha256: str = Field(pattern=_SHA256_PATTERN)
    catalogue_sha256: str = Field(pattern=_SHA256_PATTERN)
    member_id: str = Field(min_length=1, max_length=160)
    source_frame_name: str = Field(min_length=1, max_length=160)
    station_id: str = Field(min_length=1, max_length=160)
    selection_id: str = Field(min_length=1, max_length=160)
    selection_kind: ResultSelectionKindV1 = Field(strict=False)
    selection_name: str = Field(min_length=1, max_length=160)
    output_case_name: str = Field(min_length=1, max_length=160)
    object_name: str = Field(min_length=1, max_length=160)
    object_station_mm: float
    element_name: str = Field(min_length=1, max_length=160)
    element_station_mm: float
    step_type: str = Field(min_length=1, max_length=160)
    step_number: float
    source_row_index: int = Field(ge=0)
    p_kn: float
    v2_kn: float
    v3_kn: float
    t_knm: float
    m2_knm: float
    m3_knm: float
    force_unit: Literal["kN"] = "kN"
    moment_unit: Literal["kN.m"] = "kN.m"
    length_unit: Literal["mm"] = "mm"
    local_axis_basis: str = Field(min_length=1, max_length=500)
    row_sha256: str = Field(pattern=_SHA256_PATTERN)


class BeamDemandEnvelopeRuleV1(_AnalysisContractModel):
    rule_id: str = Field(min_length=1, max_length=160)
    mode: BeamDemandEnvelopeModeV1 = Field(strict=False)
    components: tuple[BeamActionComponentV1, ...] = Field(min_length=1, max_length=6)
    primary_component: BeamActionComponentV1 | None = Field(default=None, strict=False)
    caller_defined_basis: EvidenceValueV1[str]
    contributing_action_row_ids: tuple[str, ...] = Field(default=(), max_length=10_000)

    @model_validator(mode="after")
    def validate_mode_basis(self) -> Self:
        if len(set(self.components)) != len(self.components):
            raise ValueError("envelope components must be unique and ordered")
        if self.mode is BeamDemandEnvelopeModeV1.SAME_ROW_CONCURRENT:
            if self.primary_component is None:
                raise ValueError("same-row rules require primary_component")
            if self.primary_component not in self.components:
                raise ValueError("primary_component must be in components")
        elif self.primary_component is not None:
            raise ValueError("primary_component applies only to same-row rules")
        if self.mode is BeamDemandEnvelopeModeV1.CALLER_DEFINED_CODE_ENVELOPE:
            if self.caller_defined_basis.state is not EvidenceStateV1.PRESENT:
                raise ValueError("caller-defined rules require a PRESENT typed basis")
            if not self.contributing_action_row_ids:
                raise ValueError(
                    "caller-defined rules require contributing action rows"
                )
        else:
            if self.caller_defined_basis.state is not EvidenceStateV1.NOT_APPLICABLE:
                raise ValueError(
                    "non-caller-defined rules require a NOT_APPLICABLE basis"
                )
            if self.contributing_action_row_ids:
                raise ValueError(
                    "only caller-defined rules accept contributing action rows"
                )
        return self


class BeamDemandScenarioV1(_AnalysisContractModel):
    scenario_id: str = Field(min_length=1, max_length=160)
    revision: int = Field(ge=1)
    purpose: BeamDemandPurposeV1 = Field(strict=False)
    catalogue_sha256: str = Field(pattern=_SHA256_PATTERN)
    baseline_sha256: str = Field(pattern=_SHA256_PATTERN)
    included_selection_ids: tuple[str, ...] = Field(min_length=1, max_length=1_000)
    member_ids: tuple[str, ...] = Field(default=(), max_length=10_000)
    station_domain: BeamStationDomainV1 = Field(
        default=BeamStationDomainV1.ALL_RETAINED,
        strict=False,
    )
    required_components: tuple[BeamActionComponentV1, ...] = Field(
        min_length=1,
        max_length=6,
    )
    envelope_rule_ids: tuple[str, ...] = Field(min_length=1, max_length=64)
    tie_break_policy: DeterministicTieBreakV1 = Field(
        default=DeterministicTieBreakV1.SOURCE_ROW_INDEX_THEN_ROW_ID,
        strict=False,
    )
    held_checks: tuple[EvidenceValueV1[str], ...] = ()

    @model_validator(mode="after")
    def validate_unique_ordered_ids(self) -> Self:
        for label, values in (
            ("included_selection_ids", self.included_selection_ids),
            ("member_ids", self.member_ids),
            ("required_components", self.required_components),
            ("envelope_rule_ids", self.envelope_rule_ids),
        ):
            if len(set(values)) != len(values):
                raise ValueError(f"{label} must be unique and ordered")
        for held in self.held_checks:
            if held.state is EvidenceStateV1.PRESENT:
                raise ValueError("held checks cannot use PRESENT evidence")
        return self


class BeamGoverningReferenceV1(_AnalysisContractModel):
    reference_id: str = Field(min_length=1, max_length=160)
    scenario_id: str = Field(min_length=1, max_length=160)
    member_id: str = Field(min_length=1, max_length=160)
    component: BeamActionComponentV1 = Field(strict=False)
    sign: BeamGoverningSignV1 = Field(strict=False)
    rule_id: str = Field(min_length=1, max_length=160)
    governing_value: float
    action_row_ids: tuple[str, ...] = Field(min_length=1, max_length=10_000)
    selection_ids: tuple[str, ...] = Field(min_length=1, max_length=1_000)
    is_concurrent: bool
    tie_break_policy: DeterministicTieBreakV1 = Field(strict=False)
    tie_break_basis: str = Field(min_length=1, max_length=500)

    @model_validator(mode="after")
    def validate_concurrency(self) -> Self:
        if self.is_concurrent and len(self.action_row_ids) != 1:
            raise ValueError("concurrent governing references require exactly one row")
        if len(set(self.action_row_ids)) != len(self.action_row_ids):
            raise ValueError("governing action-row references must be unique")
        return self


class BeamDemandSnapshotV1(_AnalysisContractModel):
    schema_version: Literal["beam-demand-snapshot/v1"] = "beam-demand-snapshot/v1"
    hash_basis_version: Literal["beam-demand-snapshot-hash/v1"] = (
        "beam-demand-snapshot-hash/v1"
    )
    scenario: BeamDemandScenarioV1
    model_identity_sha256: str = Field(pattern=_SHA256_PATTERN)
    baseline_sha256: str = Field(pattern=_SHA256_PATTERN)
    catalogue_sha256: str = Field(pattern=_SHA256_PATTERN)
    retained_action_row_count: int = Field(ge=1)
    member_count: int = Field(ge=1)
    governing_references: tuple[BeamGoverningReferenceV1, ...] = Field(min_length=1)
    limitations: tuple[str, ...]
    snapshot_sha256: str = Field(pattern=_SHA256_PATTERN)
