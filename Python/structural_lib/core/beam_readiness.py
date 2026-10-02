"""Strict interchange records for native beam input readiness, not a design engine."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from structural_lib.core.analysis_snapshot import AnalysisSnapshotV1


class _Record(BaseModel):
    model_config = ConfigDict(
        frozen=True, strict=True, extra="forbid", allow_inf_nan=False
    )


class _Edit(_Record):
    id: str
    key: str
    scope: Literal[
        "project", "material", "story", "physical_span", "member", "selection"
    ]
    scope_id: str
    model_binding: str | None
    entered_text: str
    sequence: int


class _Field(_Record):
    subject_id: str
    key: str
    unit: str
    source_text: str | None
    entered_text: str | None
    value: str
    origin: Literal[
        "source",
        "preset",
        "rule",
        "override",
        "last_valid",
        "conflict_fallback",
        "derived",
    ]
    reason: str
    rule_revision: str
    preset_revision: str
    edit_ids: tuple[str, ...]
    last_valid_override: str | None
    source_state: Literal["absent", "blank", "zero", "supplied"]
    entered_state: Literal["absent", "blank", "zero", "supplied", "conflicting"]
    state: Literal[
        "absent", "blank", "zero", "supplied", "defaulted", "derived", "conflicting"
    ]


class BeamInputLedgerV1(_Record):
    schema_version: Literal["beam-input-ledger/v1"]
    model_binding: str
    snapshot_sha256: str
    preset_revision: str
    member_ids: tuple[str, ...]
    edits: tuple[_Edit, ...]
    fields: tuple[_Field, ...]
    revision: str


class _Preset(_Record):
    id: str
    revision: str
    values: dict[str, str]


class _Project(_Record):
    project_id: str
    revision_id: str
    origin: str
    evidence_reference: str
    values_accepted: bool
    professional_approval_accepted: bool


class _Material(_Record):
    material_id: str
    concrete_strength_n_per_mm2: float
    steel_yield_strength_n_per_mm2: float
    link_steel_yield_strength_n_per_mm2: float
    steel_modulus_n_per_mm2: float


class _Catalogue(_Record):
    revision_id: str
    longitudinal_diameters_mm: tuple[float, ...]
    link_diameters_mm: tuple[float, ...]
    link_spacings_mm: tuple[float, ...]
    bar_counts: tuple[int, ...]
    layers: tuple[int, ...]
    stock_lengths_mm: tuple[float, ...]
    maximum_candidates: int


class _Fire(_Record):
    requirement: Literal["unspecified", "not_required", "required"]
    decision_reference: str
    required_minutes: float | None


class _Restraints(_Record):
    restraint_stations_mm: tuple[float, ...]
    evidence_reference: str


class _Context(_Record):
    member_id: str
    source_member_id: str
    physical_span_id: str
    support_condition: Literal["simply_supported", "continuous", "unknown"]
    left_support_face_x_mm: float
    right_support_face_x_mm: float
    left_support_centre_x_mm: float
    right_support_centre_x_mm: float
    effective_span_mm: float
    anchorage_start_x_mm: float
    anchorage_end_x_mm: float
    nominal_cover_mm: float
    maximum_aggregate_size_mm: float
    exposure: str
    cracking_harmful: bool
    ordinary_seismic: bool
    screening_permitted: bool
    horizontal: bool
    top_mapping_normal: bool
    evidence_revision_id: str
    fire_basis: _Fire | None
    lateral_restraints: _Restraints | None


class _Role(_Record):
    selection_id: str
    role: Literal["uls", "sls_total", "sls_sustained"]


class _Inputs(_Record):
    project: _Project
    materials: tuple[_Material, ...]
    catalogue: _Catalogue
    member_contexts: tuple[_Context, ...]
    selection_roles: tuple[_Role, ...]


class _Acceptance(_Record):
    ledger_revision: str
    inputs: _Inputs


class _Request(_Record):
    cohort_id: str
    member_ids: tuple[str, ...]
    snapshot: AnalysisSnapshotV1 | None
    preset: _Preset
    saved_ledger: BeamInputLedgerV1 | None
    edits: tuple[_Edit, ...]
    acceptance: _Acceptance | None


class _Diagnostic(_Record):
    code: str
    severity: Literal["information", "warning", "error"]
    message: str
    operation_semantic_id: str
    field_or_location: str | None
    source: str
    remediation: str | None


class BeamMemberReadinessV1(_Record):
    member_id: str
    state: Literal[
        "complete",
        "needs_input",
        "unsupported",
        "failed",
        "stale",
        "incomplete",
        "no_feasible_arrangement",
        "cancelled",
    ]
    ready_for_selected_profile: bool
    effective_input_id: str | None
    diagnostics: tuple[_Diagnostic, ...]


class BeamReadinessDocumentV1(_Record):
    """Native-produced evidence. Parsing proves transport/binding integrity, not native rule execution."""

    schema_version: Literal["beam-readiness/v1"]
    profile_id: Literal["is456-ordinary-rectangular-simple-span-baseline-v1"]
    policy_revision: Literal["beam-readiness-lnv01-v1"]
    engine_identity: str
    request_id: str
    document_id: str
    request: _Request
    ledger: BeamInputLedgerV1 | None
    members: tuple[BeamMemberReadinessV1, ...]
    engineering: Literal["not_evaluated"]
    approval: Literal["unreviewed"]
    source_qualification: Literal[
        "offline_replay_only;physical_material_and_current_installed_qualification=HOLD;engineering_acceptance=not_granted"
    ]


__all__ = ["BeamInputLedgerV1", "BeamMemberReadinessV1", "BeamReadinessDocumentV1"]
