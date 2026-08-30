"""W3H immutable, vendor-neutral comparison inputs; no installed-app access.

Reference normalization and engineering acceptance remain external duties.
An equality/digest check proves identity, not the truth of a supplied model.
"""

from __future__ import annotations

from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .analysis_contracts import (
    BeamActionRowV1,
    EvidenceValueV1,
    JointDisplacementRowV1,
    JointReactionRowV1,
)
from .beam_line import BeamLineAnalysisResultV1, BeamLineIssueV1

_Id = Annotated[str, Field(min_length=1, max_length=160)]
_Sha = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
_Text = Annotated[str, Field(min_length=1, max_length=1000)]
BeamLineComparisonComponentV1 = Literal[
    "SHEAR_KN",
    "MOMENT_KNM",
    "DISPLACEMENT_MM",
    "ROTATION_RAD",
    "REACTION_KN",
    "REACTION_KNM",
]


class _ComparisonModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        allow_inf_nan=False,
        validate_default=True,
        str_strip_whitespace=True,
    )


class BeamLineReferenceIdentityV1(_ComparisonModel):
    """Exact invalidation key; current identity is supplied independently.

    Topology binds geometry, releases, offsets, modifiers, supports and slab basis;
    scenario binds ordered load/combo definitions. Settings/version/file are separate.
    """

    model_file_sha256: _Sha
    model_identity_sha256: _Sha
    baseline_sha256: _Sha
    catalogue_sha256: _Sha
    model_definition_sha256: _Sha
    scenario_definition_sha256: _Sha
    analysis_settings_sha256: _Sha
    etabs_version: _Id
    selection_id: _Id
    result_kind: Literal["CASE", "COMBINATION"]
    result_name: _Id
    step_type: _Id
    step_number: float


class BeamLineReferenceV1(_ComparisonModel):
    """Caller-normalized retained rows, not an ETABS extractor or attestation.

    Full six-component signed rows survive even though V1 compares only a plane.
    Reviews must cite evidence for the exact frozen identity, never generic defaults.
    """

    identity: BeamLineReferenceIdentityV1
    source_basis: Literal["SYNTHETIC_REFERENCE", "ETABS_NORMALIZED_REFERENCE"]
    topology_review: EvidenceValueV1[str]
    linear_response_review: EvidenceValueV1[str]
    source_references: tuple[_Text, ...] = Field(min_length=1, max_length=64)
    actions: tuple[BeamActionRowV1, ...] = Field(min_length=1, max_length=2000)
    displacements: EvidenceValueV1[tuple[JointDisplacementRowV1, ...]]
    reactions: EvidenceValueV1[tuple[JointReactionRowV1, ...]]
    reference_sha256: _Sha


class BeamLineActionMappingV1(_ComparisonModel):
    reference_row_id: _Id
    member_id: _Id
    span_id: _Id
    solver_station_index: int = Field(ge=0, le=1999)
    station_side: Literal["LEFT", "RIGHT", "CONTINUOUS"]
    source_station_origin_mm: float
    source_distance_direction: Literal[-1, 1]
    local_axis_basis: _Text
    shear_component: Literal["v2_kn", "v3_kn"]
    moment_component: Literal["m2_knm", "m3_knm"]
    shear_sign: Literal[-1, 1]
    moment_sign: Literal[-1, 1]


class BeamLineJointMappingV1(_ComparisonModel):
    reference_row_id: _Id
    joint_id: _Id
    node_id: _Id
    coordinate_system: _Text
    translation_axis: Literal[1, 2, 3]
    rotation_axis: Literal[1, 2, 3]
    translation_sign: Literal[-1, 1]
    rotation_sign: Literal[-1, 1]


class BeamLineReferenceMappingV1(_ComparisonModel):
    """Complete declared row domain; no nearest station or silent interpolation."""

    solver_scenario_id: _Id
    solver_result_id: _Id
    reference_selection_id: _Id

    actions: tuple[BeamLineActionMappingV1, ...] = Field(min_length=1, max_length=2000)
    displacements: tuple[BeamLineJointMappingV1, ...] = Field(max_length=6)
    reactions: tuple[BeamLineJointMappingV1, ...] = Field(max_length=6)
    assumptions: tuple[_Text, ...] = Field(min_length=1, max_length=64)
    reviewed_basis: EvidenceValueV1[str]


class BeamLineComponentToleranceV1(_ComparisonModel):
    component: BeamLineComparisonComponentV1
    absolute: float = Field(ge=0)
    relative: float = Field(ge=0)


class BeamLineComparisonCriteriaV1(_ComparisonModel):
    """Caller-predeclared criteria, never defaults inferred from solver numerics.

    Pass is abs(local-reference) <= absolute + relative*abs(reference).
    Absolute units are the component suffix; relative is dimensionless.
    """

    criteria_id: _Id
    declaration_reference: _Text
    declared_before_comparison: Literal[True]
    station_distance_tolerance_mm: float = Field(ge=0)
    tolerances: tuple[BeamLineComponentToleranceV1, ...] = Field(
        min_length=2, max_length=6
    )


class BeamLineComparisonRequestV1(_ComparisonModel):
    schema_version: Literal["beam-line-comparison-request/v1"] = (
        "beam-line-comparison-request/v1"
    )
    solver_result: BeamLineAnalysisResultV1
    current_identity: EvidenceValueV1[BeamLineReferenceIdentityV1]
    reference: EvidenceValueV1[BeamLineReferenceV1]
    mapping: EvidenceValueV1[BeamLineReferenceMappingV1]
    criteria: EvidenceValueV1[BeamLineComparisonCriteriaV1]


class BeamLineComponentComparisonV1(_ComparisonModel):
    reference_row_id: _Id
    reference_row_sha256: _Sha
    local_entity_id: _Id
    component: BeamLineComparisonComponentV1
    reference_value: float
    local_value: float
    signed_error: float
    absolute_error: float = Field(ge=0)
    allowed_error: float = Field(ge=0)
    within_tolerance: bool


class BeamLineCalibrationV1(_ComparisonModel):
    schema_version: Literal["beam-line-calibration/v1"] = "beam-line-calibration/v1"
    status: Literal["CALIBRATED", "OUT_OF_BAND", "NOT_COMPARABLE"]
    capability: Literal["SURROGATE_ONLY"] = "SURROGATE_ONLY"
    independent_frame_analysis: Literal["HELD_NOT_SUPPORTED"] = "HELD_NOT_SUPPORTED"
    evidence_claim: Literal["NUMERIC_COMPARISON_ONLY"] = "NUMERIC_COMPARISON_ONLY"
    professional_approval: Literal["NOT_PROVIDED"] = "NOT_PROVIDED"
    request_sha256: _Sha
    bindings: EvidenceValueV1[BeamLineReferenceIdentityV1]
    reference_sha256: EvidenceValueV1[str]
    station_mapping_sha256: EvidenceValueV1[str]
    criteria_sha256: EvidenceValueV1[str]
    reference_basis: EvidenceValueV1[str]
    comparisons: tuple[BeamLineComponentComparisonV1, ...] = Field(max_length=4024)
    issues: tuple[BeamLineIssueV1, ...]
    limitations: tuple[_Text, ...]
    calibration_sha256: _Sha

    @model_validator(mode="after")
    def validate_outcome(self) -> Self:
        if self.status == "NOT_COMPARABLE":
            if self.comparisons or not self.issues:
                raise ValueError(
                    "NOT_COMPARABLE requires issues and no partial comparisons"
                )
        elif self.issues or not self.comparisons:
            raise ValueError(
                "Comparable outcomes require comparisons and no structural issues"
            )
        elif (self.status == "CALIBRATED") != all(
            row.within_tolerance for row in self.comparisons
        ):
            raise ValueError("Calibration status must agree with every comparison")
        return self
