# SPDX-License-Identifier: MIT
"""Transport-neutral W2A ETABS beam-baseline contract and COM-shape adapter.

The adapter receives an already-supplied ``SapModel``-shaped object. It does not
connect to ETABS, open a model, run analysis, save, design, optimize, or expose a
REST/Excel surface. The only permitted setter is a temporary present-unit change,
which is restored before an accepted or blocked result is returned.
"""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from collections.abc import Callable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from hashlib import sha256
from pathlib import PureWindowsPath
from typing import Any, Literal

from pydantic import Field, model_validator

from structural_lib.services.contracts.common import StrictPublicModel
from structural_lib.services.etabs_live_bridge import (
    ETABSDataError,
    ETABSResultSelectionKind,
    ETABSResultSelectionV1,
    _decode_com_outputs,
    _require_zero_return,
)

__all__ = [
    "ETABS_BEAM_BASELINE_HASH_VERSION",
    "ETABS_BEAM_BASELINE_REQUEST_VERSION",
    "ETABS_BEAM_BASELINE_SCHEMA_VERSION",
    "ETABSBaselineBuildResultV1",
    "ETABSBaselineBuildStatus",
    "ETABSBaselineDisposition",
    "ETABSBaselineDispositionV1",
    "ETABSBaselineIssueV1",
    "ETABSBaselineRowKind",
    "ETABSBeamBaselineRequestV1",
    "ETABSBeamBaselineV1",
    "ETABSFrameAnalysisVerdict",
    "ETABSConnectivityKind",
    "ETABSConnectivityV1",
    "ETABSForceStationV1",
    "ETABSFrameKind",
    "ETABSFrameResultV1",
    "ETABSFrameV1",
    "ETABSGetterSignatureV1",
    "ETABSLocalAxisV1",
    "ETABSModelFileEvidenceV1",
    "ETABSModelFileObserverV1",
    "ETABSModelFileSnapshotV1",
    "ETABSModelIdentityV1",
    "ETABSPointV1",
    "ETABSRectangularSectionV1",
    "ETABSResultSelectionEvidenceV1",
    "ETABSRuntimeProvenanceV1",
    "ETABSStoryV1",
    "ETABSUnitProofV1",
    "ETABSUnitMutationPolicyV1",
    "canonical_etabs_beam_baseline_hash_basis_json_v1",
    "etabs_w2a_getter_matrix_v1",
    "etabs_w2a_getter_matrix_sha256_v1",
    "etabs_w2a_unit_mutation_policy_v1",
    "extract_etabs_beam_baseline_v1",
    "verify_etabs_beam_baseline_hash_v1",
]


ETABS_BEAM_BASELINE_SCHEMA_VERSION: Literal["etabs-beam-baseline/v1"] = (
    "etabs-beam-baseline/v1"
)
ETABS_BEAM_BASELINE_HASH_VERSION: Literal["etabs-beam-baseline-hash/v1"] = (
    "etabs-beam-baseline-hash/v1"
)
ETABS_BEAM_BASELINE_REQUEST_VERSION: Literal["etabs-beam-baseline-request/v1"] = (
    "etabs-beam-baseline-request/v1"
)
ETABS_KN_MM_C_UNITS: Literal[5] = 5
ETABS_OBJECT_ITEM_TYPE = 0
MAX_FORCE_ROWS_PER_FRAME = 100_000
_SHA256_PATTERN = r"^[0-9a-f]{64}$"
_UTC_PATTERN = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$"


def _parse_utc(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
    except ValueError as exc:
        raise ValueError(f"Invalid UTC timestamp {value!r}") from exc


class ETABSBaselineBuildStatus(StrEnum):
    """Fail-closed outcome for one complete W2A extraction."""

    ACCEPTED = "ACCEPTED"
    BLOCKED = "BLOCKED"


class ETABSBaselineDisposition(StrEnum):
    """Exhaustive decision for one topology or result source row."""

    ACCEPTED = "ACCEPTED"
    EXCLUDED = "EXCLUDED"
    BLOCKED = "BLOCKED"


class ETABSBaselineRowKind(StrEnum):
    STORY = "STORY"
    FRAME = "FRAME"
    CONNECTIVITY = "CONNECTIVITY"
    RESULT_SELECTION = "RESULT_SELECTION"
    RESULT_STATION = "RESULT_STATION"


class ETABSFrameKind(StrEnum):
    BEAM = "BEAM"
    COLUMN = "COLUMN"


class ETABSConnectivityKind(StrEnum):
    BEAM_TO_BEAM = "BEAM_TO_BEAM"
    BEAM_TO_COLUMN = "BEAM_TO_COLUMN"


class ETABSFrameAnalysisVerdict(StrEnum):
    SUPPORTED_BOUNDED = "SUPPORTED_BOUNDED"
    ADAPTER_REQUIRED = "ADAPTER_REQUIRED"
    HELD_NOT_SUPPORTED = "HELD_NOT_SUPPORTED"


class ETABSGetterSignatureV1(StrictPublicModel):
    """Frozen ETABS getter call/shape/return-code contract."""

    operation: str = Field(min_length=1)
    call_signature: str = Field(min_length=1)
    output_count: int | None = Field(default=None, ge=0)
    accepted_shapes: tuple[Literal["tuple", "list", "scalar"], ...]
    return_code_contract: Literal["TRAILING_ZERO", "DIRECT_VALUE"]


class ETABSUnitMutationPolicyV1(StrictPublicModel):
    """The only W2A-permitted ETABS setter and its restoration obligations."""

    operation: Literal["SapModel.SetPresentUnits"] = "SapModel.SetPresentUnits"
    normalized_units_enum: Literal[5] = ETABS_KN_MM_C_UNITS
    only_allowed_setter: Literal[True] = True
    restore_on_success: Literal[True] = True
    restore_on_failure: Literal[True] = True
    return_code_contract: Literal["ZERO"] = "ZERO"


class ETABSModelFileSnapshotV1(StrictPublicModel):
    """One exact filesystem identity observation of the authorized EDB copy."""

    model_path: str = Field(min_length=1)
    model_name: str = Field(min_length=1)
    sha256: str = Field(pattern=_SHA256_PATTERN)
    byte_count: int = Field(ge=1)
    modified_at_utc: str = Field(pattern=_UTC_PATTERN)
    observed_at_utc: str = Field(pattern=_UTC_PATTERN)

    @model_validator(mode="after")
    def _path_is_exact_saved_edb(self) -> ETABSModelFileSnapshotV1:
        path = PureWindowsPath(self.model_path)
        if not path.is_absolute() or path.suffix.casefold() != ".edb":
            raise ValueError("model_path must be an absolute Windows .edb path")
        if path.name != self.model_name:
            raise ValueError("model_name must match model_path")
        _parse_utc(self.modified_at_utc)
        _parse_utc(self.observed_at_utc)
        return self


ETABSModelFileObserverV1 = Callable[[str], ETABSModelFileSnapshotV1]


class ETABSModelFileEvidenceV1(StrictPublicModel):
    """Pre/post identity proof that the authorized model file stayed unchanged."""

    before_read: ETABSModelFileSnapshotV1
    after_read: ETABSModelFileSnapshotV1
    freshness_verdict: Literal["VERIFIED_UNCHANGED"] = "VERIFIED_UNCHANGED"

    @model_validator(mode="after")
    def _before_after_match(self) -> ETABSModelFileEvidenceV1:
        before = self.before_read
        after = self.after_read
        if PureWindowsPath(before.model_path) != PureWindowsPath(after.model_path):
            raise ValueError("before/after model paths must match")
        if (
            before.sha256 != after.sha256
            or before.byte_count != after.byte_count
            or before.modified_at_utc != after.modified_at_utc
        ):
            raise ValueError("before/after model hash, size, and timestamp must match")
        if _parse_utc(after.observed_at_utc) < _parse_utc(before.observed_at_utc):
            raise ValueError("after_read observation must not precede before_read")
        return self


class ETABSRuntimeProvenanceV1(StrictPublicModel):
    """Deterministic identity of the source/runtime used for extraction."""

    adapter_version: Literal["etabs-beam-baseline-adapter/v1"] = (
        "etabs-beam-baseline-adapter/v1"
    )
    library_version: str = Field(min_length=1)
    library_content_identity: str = Field(pattern=_SHA256_PATTERN)
    python_version: str = Field(min_length=1)
    platform: str = Field(min_length=1)
    com_provider: str = Field(min_length=1)


class ETABSBeamBaselineRequestV1(StrictPublicModel):
    """Explicit W2A request; result selection is verified, never changed."""

    schema_version: Literal["etabs-beam-baseline-request/v1"] = (
        ETABS_BEAM_BASELINE_REQUEST_VERSION
    )
    authorized_model_file: ETABSModelFileSnapshotV1
    runtime_provenance: ETABSRuntimeProvenanceV1
    result_selections: tuple[ETABSResultSelectionV1, ...] = Field(min_length=1)
    orientation_tolerance_mm: float = Field(default=1.0, gt=0)

    @model_validator(mode="after")
    def _selection_names_are_unique(self) -> ETABSBeamBaselineRequestV1:
        names = [selection.name for selection in self.result_selections]
        if len(names) != len(set(names)):
            raise ValueError(
                "result selection names must be unique because FrameForce rows do not retain the selection kind"
            )
        return self


class ETABSModelIdentityV1(StrictPublicModel):
    model_name: str
    model_path: str
    file_evidence: ETABSModelFileEvidenceV1
    etabs_version: str
    etabs_version_number: float
    model_locked: bool


class ETABSUnitProofV1(StrictPublicModel):
    original_present_units_enum: int = Field(ge=1)
    extraction_present_units_enum: Literal[5] = ETABS_KN_MM_C_UNITS
    restored_present_units_enum: int = Field(ge=1)
    restoration_status: Literal["RESTORED"] = "RESTORED"
    length: Literal["mm"] = "mm"
    force: Literal["kN"] = "kN"
    moment: Literal["kN.m"] = "kN.m"


class ETABSStoryV1(StrictPublicModel):
    story_id: str
    name: str
    elevation_mm: float
    height_mm: float = Field(ge=0)
    is_master_story: bool
    similar_to_story: str
    splice_above: bool
    splice_height_mm: float = Field(ge=0)


class ETABSPointV1(StrictPublicModel):
    point_name: str
    x_mm: float
    y_mm: float
    z_mm: float


class ETABSLocalAxisV1(StrictPublicModel):
    local_axis_rotation_deg: float
    advanced_axes_active: bool
    direction_x: float
    direction_y: float
    direction_z: float
    length_mm: float = Field(gt=0)


class ETABSRectangularSectionV1(StrictPublicModel):
    section_name: str
    auto_select_list: str
    material_property_label: str
    depth_t3_mm: float = Field(gt=0)
    width_t2_mm: float = Field(gt=0)


class ETABSFrameV1(StrictPublicModel):
    member_id: str
    source_unique_name: str
    label: str
    story: str
    kind: ETABSFrameKind
    point_i: ETABSPointV1
    point_j: ETABSPointV1
    local_axis: ETABSLocalAxisV1
    section: ETABSRectangularSectionV1


class ETABSConnectivityV1(StrictPublicModel):
    connection_id: str
    kind: ETABSConnectivityKind
    point_name: str
    member_a_id: str
    member_b_id: str


class ETABSResultSelectionEvidenceV1(StrictPublicModel):
    selection: ETABSResultSelectionV1
    available: Literal[True] = True
    selected_for_output: Literal[True] = True
    case_status_code: int | None = Field(default=None, ge=1, le=4)
    status: Literal["FINISHED", "COMBINATION_ROWS_REQUIRED"]


class ETABSForceStationV1(StrictPublicModel):
    station_id: str
    member_id: str
    source_frame_name: str
    source_row_index: int = Field(ge=0)
    selection: ETABSResultSelectionV1
    object_name: str
    object_station_mm: float
    element_name: str
    element_station_mm: float
    step_type: str
    step_number: float
    p_kn: float
    v2_kn: float
    v3_kn: float
    t_knm: float
    m2_knm: float
    m3_knm: float


class ETABSFrameResultV1(StrictPublicModel):
    member_id: str
    source_frame_name: str
    selection_evidence: ETABSResultSelectionEvidenceV1
    stations: tuple[ETABSForceStationV1, ...] = Field(min_length=1)


class ETABSBaselineDispositionV1(StrictPublicModel):
    row_id: str
    row_kind: ETABSBaselineRowKind
    source_id: str
    disposition: ETABSBaselineDisposition
    reason_code: str
    canonical_id: str | None = None
    message: str


class ETABSBaselineIssueV1(StrictPublicModel):
    code: str
    path: str
    message: str


class ETABSBeamBaselineV1(StrictPublicModel):
    """Accepted complete W2A beam/model/result baseline."""

    schema_version: Literal["etabs-beam-baseline/v1"] = (
        ETABS_BEAM_BASELINE_SCHEMA_VERSION
    )
    hash_basis_version: Literal["etabs-beam-baseline-hash/v1"] = (
        ETABS_BEAM_BASELINE_HASH_VERSION
    )
    model: ETABSModelIdentityV1
    units: ETABSUnitProofV1
    stories: tuple[ETABSStoryV1, ...]
    frames: tuple[ETABSFrameV1, ...]
    connectivity: tuple[ETABSConnectivityV1, ...]
    results: tuple[ETABSFrameResultV1, ...]
    dispositions: tuple[ETABSBaselineDispositionV1, ...]
    runtime_provenance: ETABSRuntimeProvenanceV1
    getter_matrix_sha256: str = Field(pattern=_SHA256_PATTERN)
    frame_analysis_verdict: Literal["HELD_NOT_SUPPORTED"] = "HELD_NOT_SUPPORTED"
    frame_analysis_basis: tuple[str, ...]
    limitations: tuple[str, ...]
    baseline_sha256: str = Field(pattern=_SHA256_PATTERN)


class ETABSBaselineBuildResultV1(StrictPublicModel):
    """Fail-closed W2A extraction result with complete decision evidence."""

    schema_version: Literal["etabs-beam-baseline-build-result/v1"] = (
        "etabs-beam-baseline-build-result/v1"
    )
    status: ETABSBaselineBuildStatus
    units_restored: Literal[True] = True
    dispositions: tuple[ETABSBaselineDispositionV1, ...]
    issues: tuple[ETABSBaselineIssueV1, ...]
    baseline: ETABSBeamBaselineV1 | None

    @model_validator(mode="after")
    def _status_matches_baseline(self) -> ETABSBaselineBuildResultV1:
        if self.status is ETABSBaselineBuildStatus.ACCEPTED:
            if self.baseline is None or self.issues:
                raise ValueError("accepted builds require a baseline and no issues")
        elif self.baseline is not None or not self.issues:
            raise ValueError("blocked builds require issues and expose no baseline")
        return self


_GETTER_MATRIX = (
    ETABSGetterSignatureV1(
        operation="SapModel.GetModelFilename",
        call_signature="GetModelFilename(IncludePath=True) -> str",
        accepted_shapes=("scalar",),
        return_code_contract="DIRECT_VALUE",
    ),
    ETABSGetterSignatureV1(
        operation="SapModel.GetVersion",
        call_signature="GetVersion() -> (Version, VersionNumber, ret)",
        output_count=2,
        accepted_shapes=("tuple", "list"),
        return_code_contract="TRAILING_ZERO",
    ),
    ETABSGetterSignatureV1(
        operation="SapModel.GetModelIsLocked",
        call_signature="GetModelIsLocked() -> bool",
        accepted_shapes=("scalar",),
        return_code_contract="DIRECT_VALUE",
    ),
    ETABSGetterSignatureV1(
        operation="SapModel.GetPresentUnits",
        call_signature="GetPresentUnits() -> eUnits",
        accepted_shapes=("scalar",),
        return_code_contract="DIRECT_VALUE",
    ),
    ETABSGetterSignatureV1(
        operation="Story.GetStories",
        call_signature=(
            "GetStories() -> (NumberStories, StoryNames, StoryElevations, "
            "StoryHeights, IsMasterStory, SimilarToStory, SpliceAbove, SpliceHeight, ret)"
        ),
        output_count=8,
        accepted_shapes=("tuple", "list"),
        return_code_contract="TRAILING_ZERO",
    ),
    ETABSGetterSignatureV1(
        operation="FrameObj.GetNameList",
        call_signature="GetNameList() -> (NumberNames, Names, ret)",
        output_count=2,
        accepted_shapes=("tuple", "list"),
        return_code_contract="TRAILING_ZERO",
    ),
    ETABSGetterSignatureV1(
        operation="FrameObj.GetLabelFromName",
        call_signature="GetLabelFromName(Name) -> (Label, Story, ret)",
        output_count=2,
        accepted_shapes=("tuple", "list"),
        return_code_contract="TRAILING_ZERO",
    ),
    ETABSGetterSignatureV1(
        operation="FrameObj.GetPoints",
        call_signature="GetPoints(Name) -> (Point1, Point2, ret)",
        output_count=2,
        accepted_shapes=("tuple", "list"),
        return_code_contract="TRAILING_ZERO",
    ),
    ETABSGetterSignatureV1(
        operation="FrameObj.GetSection",
        call_signature="GetSection(Name) -> (PropName, SAuto, ret)",
        output_count=2,
        accepted_shapes=("tuple", "list"),
        return_code_contract="TRAILING_ZERO",
    ),
    ETABSGetterSignatureV1(
        operation="FrameObj.GetLocalAxes",
        call_signature="GetLocalAxes(Name) -> (Angle, Advanced, ret)",
        output_count=2,
        accepted_shapes=("tuple", "list"),
        return_code_contract="TRAILING_ZERO",
    ),
    ETABSGetterSignatureV1(
        operation="PointObj.GetCoordCartesian",
        call_signature="GetCoordCartesian(Name, CSys='Global') -> (X, Y, Z, ret)",
        output_count=3,
        accepted_shapes=("tuple", "list"),
        return_code_contract="TRAILING_ZERO",
    ),
    ETABSGetterSignatureV1(
        operation="PropFrame.GetRectangle",
        call_signature=(
            "GetRectangle(Name) -> (FileName, MatProp, T3, T2, Color, Notes, GUID, ret)"
        ),
        output_count=7,
        accepted_shapes=("tuple", "list"),
        return_code_contract="TRAILING_ZERO",
    ),
    ETABSGetterSignatureV1(
        operation="LoadCases.GetNameList",
        call_signature="GetNameList() -> (NumberNames, Names, ret)",
        output_count=2,
        accepted_shapes=("tuple", "list"),
        return_code_contract="TRAILING_ZERO",
    ),
    ETABSGetterSignatureV1(
        operation="RespCombo.GetNameList",
        call_signature="GetNameList() -> (NumberNames, Names, ret)",
        output_count=2,
        accepted_shapes=("tuple", "list"),
        return_code_contract="TRAILING_ZERO",
    ),
    ETABSGetterSignatureV1(
        operation="Analyze.GetCaseStatus",
        call_signature="GetCaseStatus() -> (NumberItems, CaseNames, Statuses, ret)",
        output_count=3,
        accepted_shapes=("tuple", "list"),
        return_code_contract="TRAILING_ZERO",
    ),
    ETABSGetterSignatureV1(
        operation="Results.Setup.GetCaseSelectedForOutput",
        call_signature="GetCaseSelectedForOutput(Name) -> (Selected, ret)",
        output_count=1,
        accepted_shapes=("tuple", "list"),
        return_code_contract="TRAILING_ZERO",
    ),
    ETABSGetterSignatureV1(
        operation="Results.Setup.GetComboSelectedForOutput",
        call_signature="GetComboSelectedForOutput(Name) -> (Selected, ret)",
        output_count=1,
        accepted_shapes=("tuple", "list"),
        return_code_contract="TRAILING_ZERO",
    ),
    ETABSGetterSignatureV1(
        operation="Results.FrameForce",
        call_signature=(
            "FrameForce(Name, ItemTypeElm=0) -> (NumberResults, Obj, ObjSta, Elm, "
            "ElmSta, LoadCase, StepType, StepNum, P, V2, V3, T, M2, M3, ret)"
        ),
        output_count=14,
        accepted_shapes=("tuple", "list"),
        return_code_contract="TRAILING_ZERO",
    ),
)


def etabs_w2a_getter_matrix_v1() -> tuple[ETABSGetterSignatureV1, ...]:
    """Return the immutable W2A getter matrix in canonical operation order."""

    return _GETTER_MATRIX


def etabs_w2a_unit_mutation_policy_v1() -> ETABSUnitMutationPolicyV1:
    """Return the sole temporary mutation permitted by W2A."""

    return ETABSUnitMutationPolicyV1()


def _canonical_sha256(value: Mapping[str, Any] | Sequence[Any]) -> str:
    encoded = json.dumps(
        value,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def _stable_id(prefix: str, payload: Mapping[str, Any]) -> str:
    return f"{prefix}:{_canonical_sha256(payload)[:24]}"


def _exact_array(
    operation: str, name: str, value: object, *, expected_count: int
) -> Sequence[Any]:
    if not isinstance(value, (tuple, list)):
        raise ETABSDataError(
            "ETABS_COM_SIGNATURE_MISMATCH",
            f"{operation} did not return the expected {name} tuple/list array.",
        )
    if len(value) != expected_count:
        raise ETABSDataError(
            "ETABS_RESULT_ARRAY_MISMATCH",
            f"{operation} returned {len(value)} {name} values for {expected_count} rows.",
        )
    return value


def _finite_float(operation: str, name: str, value: object) -> float:
    if isinstance(value, bool):
        raise ETABSDataError("ETABS_VALUE_INVALID", f"{operation} {name} is invalid.")
    if not isinstance(value, (int, float, str)):
        raise ETABSDataError(
            "ETABS_VALUE_INVALID", f"{operation} {name} is not numeric."
        )
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ETABSDataError(
            "ETABS_VALUE_INVALID", f"{operation} {name} is not numeric."
        ) from exc
    if not math.isfinite(result):
        raise ETABSDataError(
            "ETABS_VALUE_INVALID", f"{operation} {name} is not finite."
        )
    return result


def _exact_int(operation: str, name: str, value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ETABSDataError(
            "ETABS_VALUE_INVALID", f"{operation} {name} is not an integer."
        )
    return value


def _nonblank(operation: str, name: str, value: object) -> str:
    result = str(value).strip()
    if not result:
        raise ETABSDataError(
            "ETABS_VALUE_INVALID", f"{operation} returned a blank {name}."
        )
    return result


@contextmanager
def _normalized_units(sap_model: Any) -> Iterator[int]:
    original = sap_model.GetPresentUnits()
    if isinstance(original, bool) or not isinstance(original, int) or original <= 0:
        raise ETABSDataError(
            "ETABS_PRESENT_UNITS_INVALID",
            "SapModel.GetPresentUnits did not return a valid eUnits integer.",
        )
    try:
        _require_zero_return(
            "SapModel.SetPresentUnits(kN_mm_C)",
            sap_model.SetPresentUnits(ETABS_KN_MM_C_UNITS),
        )
    except ETABSDataError:
        _require_zero_return(
            "SapModel.SetPresentUnits(restore after normalization failure)",
            sap_model.SetPresentUnits(original),
        )
        raise
    try:
        yield original
    finally:
        _require_zero_return(
            "SapModel.SetPresentUnits(restore)", sap_model.SetPresentUnits(original)
        )


def _disposition(
    *,
    row_kind: ETABSBaselineRowKind,
    source_id: str,
    disposition: ETABSBaselineDisposition,
    reason_code: str,
    message: str,
    canonical_id: str | None = None,
) -> ETABSBaselineDispositionV1:
    row_payload = {
        "row_kind": row_kind.value,
        "source_id": source_id,
        "disposition": disposition.value,
        "reason_code": reason_code,
        "canonical_id": canonical_id,
    }
    return ETABSBaselineDispositionV1(
        row_id=_stable_id("etabs-row", row_payload),
        row_kind=row_kind,
        source_id=source_id,
        disposition=disposition,
        reason_code=reason_code,
        canonical_id=canonical_id,
        message=message,
    )


def _same_model_file_identity(
    left: ETABSModelFileSnapshotV1, right: ETABSModelFileSnapshotV1
) -> bool:
    return (
        PureWindowsPath(left.model_path) == PureWindowsPath(right.model_path)
        and left.model_name == right.model_name
        and left.sha256 == right.sha256
        and left.byte_count == right.byte_count
        and left.modified_at_utc == right.modified_at_utc
    )


def _read_model_identity(
    sap_model: Any, before_read: ETABSModelFileSnapshotV1
) -> ETABSModelIdentityV1:
    model_path = _nonblank(
        "SapModel.GetModelFilename", "model path", sap_model.GetModelFilename(True)
    )
    expected_path = before_read.model_path
    if PureWindowsPath(model_path) != PureWindowsPath(expected_path):
        raise ETABSDataError(
            "ETABS_MODEL_IDENTITY_MISMATCH",
            f"Open ETABS model {model_path!r} does not match authorized evidence {expected_path!r}.",
        )
    version, version_number = _decode_com_outputs(
        "SapModel.GetVersion", sap_model.GetVersion(), output_count=2
    )
    locked = sap_model.GetModelIsLocked()
    if not isinstance(locked, bool):
        raise ETABSDataError(
            "ETABS_MODEL_LOCK_STATE_INVALID",
            "SapModel.GetModelIsLocked did not return a boolean.",
        )
    return ETABSModelIdentityV1(
        model_name=before_read.model_name,
        model_path=model_path,
        file_evidence=ETABSModelFileEvidenceV1(
            before_read=before_read,
            after_read=before_read,
        ),
        etabs_version=_nonblank("SapModel.GetVersion", "version", version),
        etabs_version_number=_finite_float(
            "SapModel.GetVersion", "version number", version_number
        ),
        model_locked=locked,
    )


def _read_stories(
    sap_model: Any,
) -> tuple[tuple[ETABSStoryV1, ...], list[ETABSBaselineDispositionV1]]:
    outputs = _decode_com_outputs(
        "Story.GetStories", sap_model.Story.GetStories(), output_count=8
    )
    count = _exact_int("Story.GetStories", "count", outputs[0])
    if count <= 0:
        raise ETABSDataError(
            "ETABS_STORY_INVENTORY_EMPTY", "Story.GetStories returned no stories."
        )
    array_names = (
        "names",
        "elevations",
        "heights",
        "is_master_story",
        "similar_to_story",
        "splice_above",
        "splice_height",
    )
    # CSI documents that NumberStories excludes the leading "Base" row while
    # every GetStories output array includes it.
    returned_count = count + 1
    arrays = {
        name: _exact_array(
            "Story.GetStories", name, outputs[index], expected_count=returned_count
        )
        for index, name in enumerate(array_names, start=1)
    }
    stories: list[ETABSStoryV1] = []
    dispositions: list[ETABSBaselineDispositionV1] = []
    base_name = _nonblank("Story.GetStories", "base row name", arrays["names"][0])
    if base_name.casefold() != "base":
        raise ETABSDataError(
            "ETABS_STORY_BASE_ROW_INVALID",
            "Story.GetStories did not return the documented leading Base row.",
        )
    dispositions.append(
        _disposition(
            row_kind=ETABSBaselineRowKind.STORY,
            source_id=base_name,
            disposition=ETABSBaselineDisposition.EXCLUDED,
            reason_code="STORY_BASE_NOT_A_STORY",
            message=(
                "CSI GetStories includes Base in every output array but excludes it "
                "from NumberStories; the non-story row is retained as an exclusion."
            ),
        )
    )
    seen: set[str] = set()
    for index in range(1, returned_count):
        name = _nonblank("Story.GetStories", "story name", arrays["names"][index])
        if name in seen:
            raise ETABSDataError(
                "ETABS_STORY_ID_DUPLICATE", f"Duplicate ETABS story name {name!r}."
            )
        seen.add(name)
        story_id = _stable_id("etabs-story", {"name": name})
        is_master = arrays["is_master_story"][index]
        splice_above = arrays["splice_above"][index]
        if not isinstance(is_master, bool) or not isinstance(splice_above, bool):
            raise ETABSDataError(
                "ETABS_VALUE_INVALID",
                f"Story {name!r} master/splice flags must be booleans.",
            )
        story = ETABSStoryV1(
            story_id=story_id,
            name=name,
            elevation_mm=_finite_float(
                "Story.GetStories", "elevation", arrays["elevations"][index]
            ),
            height_mm=_finite_float(
                "Story.GetStories", "height", arrays["heights"][index]
            ),
            is_master_story=is_master,
            similar_to_story=str(arrays["similar_to_story"][index]).strip(),
            splice_above=splice_above,
            splice_height_mm=_finite_float(
                "Story.GetStories", "splice height", arrays["splice_height"][index]
            ),
        )
        stories.append(story)
        dispositions.append(
            _disposition(
                row_kind=ETABSBaselineRowKind.STORY,
                source_id=name,
                disposition=ETABSBaselineDisposition.ACCEPTED,
                reason_code="STORY_ACCEPTED",
                canonical_id=story_id,
                message="Story getter row retained without inference.",
            )
        )
    return (
        tuple(sorted(stories, key=lambda item: (item.elevation_mm, item.name))),
        dispositions,
    )


@dataclass(frozen=True)
class _FrameCandidate:
    source_name: str
    point_i_name: str
    point_j_name: str
    kind: ETABSFrameKind | None
    frame: ETABSFrameV1 | None


def _point(sap_model: Any, point_name: str) -> ETABSPointV1:
    x, y, z = _decode_com_outputs(
        "PointObj.GetCoordCartesian",
        sap_model.PointObj.GetCoordCartesian(point_name),
        output_count=3,
    )
    return ETABSPointV1(
        point_name=point_name,
        x_mm=_finite_float("PointObj.GetCoordCartesian", "X", x),
        y_mm=_finite_float("PointObj.GetCoordCartesian", "Y", y),
        z_mm=_finite_float("PointObj.GetCoordCartesian", "Z", z),
    )


def _read_frames(
    sap_model: Any,
    *,
    model_sha256: str,
    story_names: frozenset[str],
    tolerance_mm: float,
) -> tuple[
    tuple[ETABSFrameV1, ...],
    tuple[_FrameCandidate, ...],
    list[ETABSBaselineDispositionV1],
]:
    number, raw_names = _decode_com_outputs(
        "FrameObj.GetNameList", sap_model.FrameObj.GetNameList(), output_count=2
    )
    count = _exact_int("FrameObj.GetNameList", "count", number)
    if count <= 0:
        raise ETABSDataError(
            "ETABS_FRAME_INVENTORY_EMPTY", "FrameObj.GetNameList returned no frames."
        )
    names = _exact_array(
        "FrameObj.GetNameList", "names", raw_names, expected_count=count
    )
    source_names = [
        _nonblank("FrameObj.GetNameList", "frame name", value) for value in names
    ]
    if len(source_names) != len(set(source_names)):
        raise ETABSDataError(
            "ETABS_FRAME_ID_DUPLICATE",
            "FrameObj.GetNameList returned duplicate unique frame names.",
        )

    frames: list[ETABSFrameV1] = []
    candidates: list[_FrameCandidate] = []
    dispositions: list[ETABSBaselineDispositionV1] = []
    for source_name in sorted(source_names):
        label, story = _decode_com_outputs(
            "FrameObj.GetLabelFromName",
            sap_model.FrameObj.GetLabelFromName(source_name),
            output_count=2,
        )
        point_i_name, point_j_name = _decode_com_outputs(
            "FrameObj.GetPoints",
            sap_model.FrameObj.GetPoints(source_name),
            output_count=2,
        )
        section_name, auto_select = _decode_com_outputs(
            "FrameObj.GetSection",
            sap_model.FrameObj.GetSection(source_name),
            output_count=2,
        )
        rotation, advanced = _decode_com_outputs(
            "FrameObj.GetLocalAxes",
            sap_model.FrameObj.GetLocalAxes(source_name),
            output_count=2,
        )
        frame_label = _nonblank("FrameObj.GetLabelFromName", "label", label)
        frame_story = _nonblank("FrameObj.GetLabelFromName", "story", story)
        if frame_story not in story_names:
            raise ETABSDataError(
                "ETABS_FRAME_STORY_NOT_IN_INVENTORY",
                f"Frame {source_name!r} reports story {frame_story!r}, which is absent from Story.GetStories.",
            )
        point_i_name = _nonblank("FrameObj.GetPoints", "point I", point_i_name)
        point_j_name = _nonblank("FrameObj.GetPoints", "point J", point_j_name)
        if point_i_name == point_j_name:
            raise ETABSDataError(
                "ETABS_FRAME_ENDPOINTS_INVALID",
                f"Frame {source_name!r} uses the same point at both ends.",
            )
        point_i = _point(sap_model, point_i_name)
        point_j = _point(sap_model, point_j_name)
        dx = point_j.x_mm - point_i.x_mm
        dy = point_j.y_mm - point_i.y_mm
        dz = point_j.z_mm - point_i.z_mm
        length = math.sqrt(dx * dx + dy * dy + dz * dz)
        if length <= 0:
            raise ETABSDataError(
                "ETABS_FRAME_LENGTH_INVALID", f"Frame {source_name!r} has zero length."
            )
        if abs(dz) <= tolerance_mm and math.hypot(dx, dy) > tolerance_mm:
            kind: ETABSFrameKind | None = ETABSFrameKind.BEAM
        elif math.hypot(dx, dy) <= tolerance_mm and abs(dz) > tolerance_mm:
            kind = ETABSFrameKind.COLUMN
        else:
            kind = None

        member_id = _stable_id(
            "etabs-member", {"model_sha256": model_sha256, "name": source_name}
        )
        if kind is None:
            dispositions.append(
                _disposition(
                    row_kind=ETABSBaselineRowKind.FRAME,
                    source_id=source_name,
                    disposition=ETABSBaselineDisposition.EXCLUDED,
                    reason_code="FRAME_ORIENTATION_UNSUPPORTED",
                    canonical_id=member_id,
                    message="Frame is neither horizontal beam nor vertical column within the explicit tolerance.",
                )
            )
            candidates.append(
                _FrameCandidate(source_name, point_i_name, point_j_name, None, None)
            )
            continue
        if not isinstance(advanced, bool):
            raise ETABSDataError(
                "ETABS_VALUE_INVALID",
                f"Frame {source_name!r} advanced-axis flag is not boolean.",
            )
        if advanced:
            dispositions.append(
                _disposition(
                    row_kind=ETABSBaselineRowKind.FRAME,
                    source_id=source_name,
                    disposition=ETABSBaselineDisposition.EXCLUDED,
                    reason_code="FRAME_ADVANCED_LOCAL_AXES_UNSUPPORTED",
                    canonical_id=member_id,
                    message="Advanced local-axis definitions require a separately frozen getter contract.",
                )
            )
            candidates.append(
                _FrameCandidate(source_name, point_i_name, point_j_name, kind, None)
            )
            continue
        try:
            rectangle = _decode_com_outputs(
                "PropFrame.GetRectangle",
                sap_model.PropFrame.GetRectangle(
                    _nonblank("FrameObj.GetSection", "section name", section_name)
                ),
                output_count=7,
            )
        except ETABSDataError as exc:
            if exc.code != "ETABS_API_CALL_FAILED":
                raise
            dispositions.append(
                _disposition(
                    row_kind=ETABSBaselineRowKind.FRAME,
                    source_id=source_name,
                    disposition=ETABSBaselineDisposition.EXCLUDED,
                    reason_code="SECTION_NOT_RECTANGULAR_OR_UNAVAILABLE",
                    canonical_id=member_id,
                    message="Frame section could not be read through PropFrame.GetRectangle.",
                )
            )
            candidates.append(
                _FrameCandidate(source_name, point_i_name, point_j_name, kind, None)
            )
            continue
        _file_name, material, t3, t2, _color, _notes, _guid = rectangle
        frame = ETABSFrameV1(
            member_id=member_id,
            source_unique_name=source_name,
            label=frame_label,
            story=frame_story,
            kind=kind,
            point_i=point_i,
            point_j=point_j,
            local_axis=ETABSLocalAxisV1(
                local_axis_rotation_deg=_finite_float(
                    "FrameObj.GetLocalAxes", "rotation", rotation
                ),
                advanced_axes_active=advanced,
                direction_x=dx / length,
                direction_y=dy / length,
                direction_z=dz / length,
                length_mm=length,
            ),
            section=ETABSRectangularSectionV1(
                section_name=_nonblank(
                    "FrameObj.GetSection", "section name", section_name
                ),
                auto_select_list=str(auto_select).strip(),
                material_property_label=_nonblank(
                    "PropFrame.GetRectangle", "material property", material
                ),
                depth_t3_mm=_finite_float("PropFrame.GetRectangle", "T3", t3),
                width_t2_mm=_finite_float("PropFrame.GetRectangle", "T2", t2),
            ),
        )
        frames.append(frame)
        candidates.append(
            _FrameCandidate(source_name, point_i_name, point_j_name, kind, frame)
        )
        dispositions.append(
            _disposition(
                row_kind=ETABSBaselineRowKind.FRAME,
                source_id=source_name,
                disposition=ETABSBaselineDisposition.ACCEPTED,
                reason_code=f"FRAME_ACCEPTED_{kind.value}",
                canonical_id=member_id,
                message="Frame identity, endpoints, local axes, and rectangular section retained.",
            )
        )
    return (
        tuple(sorted(frames, key=lambda item: item.member_id)),
        tuple(candidates),
        dispositions,
    )


def _read_connectivity(
    candidates: Sequence[_FrameCandidate],
) -> tuple[tuple[ETABSConnectivityV1, ...], list[ETABSBaselineDispositionV1]]:
    by_point: dict[str, list[_FrameCandidate]] = defaultdict(list)
    for candidate in candidates:
        by_point[candidate.point_i_name].append(candidate)
        by_point[candidate.point_j_name].append(candidate)

    connections: dict[str, ETABSConnectivityV1] = {}
    dispositions: list[ETABSBaselineDispositionV1] = []
    for point_name, connected in sorted(by_point.items()):
        beams = [
            item
            for item in connected
            if item.kind is ETABSFrameKind.BEAM and item.frame is not None
        ]
        for beam in beams:
            beam_frame = beam.frame
            if beam_frame is None:  # Defensive guard for static/runtime narrowing.
                continue
            others = [
                item for item in connected if item.source_name != beam.source_name
            ]
            if not others:
                dispositions.append(
                    _disposition(
                        row_kind=ETABSBaselineRowKind.CONNECTIVITY,
                        source_id=f"{point_name}:{beam.source_name}",
                        disposition=ETABSBaselineDisposition.EXCLUDED,
                        reason_code="NO_FRAME_ENDPOINT_CONNECTION",
                        canonical_id=beam_frame.member_id,
                        message="No beam/column frame shares this ETABS endpoint; no support type is inferred.",
                    )
                )
                continue
            for other in others:
                source_id = ":".join(
                    (point_name, *sorted((beam.source_name, other.source_name)))
                )
                if other.frame is None:
                    dispositions.append(
                        _disposition(
                            row_kind=ETABSBaselineRowKind.CONNECTIVITY,
                            source_id=source_id,
                            disposition=ETABSBaselineDisposition.BLOCKED,
                            reason_code="CONNECTED_FRAME_EXCLUDED",
                            canonical_id=beam_frame.member_id,
                            message="Beam endpoint reaches an excluded frame, so complete topology is unavailable.",
                        )
                    )
                    continue
                other_frame = other.frame
                if other_frame is None:  # Defensive guard for static/runtime narrowing.
                    continue
                if other.kind is ETABSFrameKind.BEAM:
                    kind = ETABSConnectivityKind.BEAM_TO_BEAM
                elif other.kind is ETABSFrameKind.COLUMN:
                    kind = ETABSConnectivityKind.BEAM_TO_COLUMN
                else:
                    continue
                member_ids = sorted((beam_frame.member_id, other_frame.member_id))
                connection_id = _stable_id(
                    "etabs-connection",
                    {"point_name": point_name, "member_ids": member_ids},
                )
                if connection_id in connections:
                    continue
                connection = ETABSConnectivityV1(
                    connection_id=connection_id,
                    kind=kind,
                    point_name=point_name,
                    member_a_id=member_ids[0],
                    member_b_id=member_ids[1],
                )
                connections[connection_id] = connection
                dispositions.append(
                    _disposition(
                        row_kind=ETABSBaselineRowKind.CONNECTIVITY,
                        source_id=source_id,
                        disposition=ETABSBaselineDisposition.ACCEPTED,
                        reason_code=f"CONNECTIVITY_ACCEPTED_{kind.value}",
                        canonical_id=connection_id,
                        message="Shared ETABS endpoint retained without geometric proximity inference.",
                    )
                )
    return tuple(connections[key] for key in sorted(connections)), dispositions


def _name_list(operation: str, value: object) -> set[str]:
    number, raw_names = _decode_com_outputs(operation, value, output_count=2)
    count = _exact_int(operation, "count", number)
    if count < 0:
        raise ETABSDataError("ETABS_VALUE_INVALID", f"{operation} count is negative.")
    names = _exact_array(operation, "names", raw_names, expected_count=count)
    decoded = [_nonblank(operation, "name", item) for item in names]
    if len(decoded) != len(set(decoded)):
        raise ETABSDataError(
            "ETABS_NAME_LIST_DUPLICATE", f"{operation} returned duplicate names."
        )
    return set(decoded)


def _selection_evidence(
    sap_model: Any,
    selections: Sequence[ETABSResultSelectionV1],
    dispositions: list[ETABSBaselineDispositionV1],
) -> tuple[ETABSResultSelectionEvidenceV1, ...]:
    cases = _name_list("LoadCases.GetNameList", sap_model.LoadCases.GetNameList())
    combinations = _name_list(
        "RespCombo.GetNameList", sap_model.RespCombo.GetNameList()
    )
    status_outputs = _decode_com_outputs(
        "Analyze.GetCaseStatus", sap_model.Analyze.GetCaseStatus(), output_count=3
    )
    status_count = _exact_int("Analyze.GetCaseStatus", "count", status_outputs[0])
    if status_count < 0:
        raise ETABSDataError(
            "ETABS_VALUE_INVALID", "Analyze.GetCaseStatus count is negative."
        )
    status_names = _exact_array(
        "Analyze.GetCaseStatus",
        "case names",
        status_outputs[1],
        expected_count=status_count,
    )
    status_values = _exact_array(
        "Analyze.GetCaseStatus",
        "statuses",
        status_outputs[2],
        expected_count=status_count,
    )
    decoded_status_names = [
        _nonblank("Analyze.GetCaseStatus", "case name", name) for name in status_names
    ]
    if len(decoded_status_names) != len(set(decoded_status_names)):
        raise ETABSDataError(
            "ETABS_CASE_STATUS_DUPLICATE",
            "Analyze.GetCaseStatus returned duplicate case names.",
        )
    statuses = {
        name: _exact_int("Analyze.GetCaseStatus", "status", status_values[index])
        for index, name in enumerate(decoded_status_names)
    }

    evidence: list[ETABSResultSelectionEvidenceV1] = []
    for selection in selections:
        source_id = f"{selection.kind.value}:{selection.name}"
        available = selection.name in (
            cases if selection.kind is ETABSResultSelectionKind.CASE else combinations
        )
        if not available:
            dispositions.append(
                _disposition(
                    row_kind=ETABSBaselineRowKind.RESULT_SELECTION,
                    source_id=source_id,
                    disposition=ETABSBaselineDisposition.BLOCKED,
                    reason_code="RESULT_SELECTION_NOT_AVAILABLE",
                    message="Explicit requested result case/combination is absent from its getter inventory.",
                )
            )
            continue
        if selection.kind is ETABSResultSelectionKind.CASE:
            (selected,) = _decode_com_outputs(
                "Results.Setup.GetCaseSelectedForOutput",
                sap_model.Results.Setup.GetCaseSelectedForOutput(selection.name),
                output_count=1,
            )
            status_code = statuses.get(selection.name)
            finished = status_code == 4
        else:
            (selected,) = _decode_com_outputs(
                "Results.Setup.GetComboSelectedForOutput",
                sap_model.Results.Setup.GetComboSelectedForOutput(selection.name),
                output_count=1,
            )
            status_code = None
            finished = True
        if not isinstance(selected, bool):
            raise ETABSDataError(
                "ETABS_VALUE_INVALID",
                f"Output-selection getter for {source_id} did not return a boolean.",
            )
        if not selected:
            dispositions.append(
                _disposition(
                    row_kind=ETABSBaselineRowKind.RESULT_SELECTION,
                    source_id=source_id,
                    disposition=ETABSBaselineDisposition.BLOCKED,
                    reason_code="RESULT_SELECTION_NOT_ACTIVE",
                    message="W2A is setter-free and will not change ETABS output selections.",
                )
            )
            continue
        if not finished:
            dispositions.append(
                _disposition(
                    row_kind=ETABSBaselineRowKind.RESULT_SELECTION,
                    source_id=source_id,
                    disposition=ETABSBaselineDisposition.BLOCKED,
                    reason_code="RESULT_CASE_NOT_FINISHED",
                    message=f"Analyze.GetCaseStatus returned {status_code!r}; status 4 is required.",
                )
            )
            continue
        record = ETABSResultSelectionEvidenceV1(
            selection=selection,
            case_status_code=status_code,
            status=(
                "FINISHED"
                if selection.kind is ETABSResultSelectionKind.CASE
                else "COMBINATION_ROWS_REQUIRED"
            ),
        )
        evidence.append(record)
        dispositions.append(
            _disposition(
                row_kind=ETABSBaselineRowKind.RESULT_SELECTION,
                source_id=source_id,
                disposition=ETABSBaselineDisposition.ACCEPTED,
                reason_code="RESULT_SELECTION_ACCEPTED",
                canonical_id=_stable_id(
                    "etabs-result-selection",
                    {"kind": selection.kind.value, "name": selection.name},
                ),
                message="Explicit result selection exists, is already active, and satisfies its status contract.",
            )
        )
    return tuple(sorted(evidence, key=lambda item: item.selection.name))


def _read_results(
    sap_model: Any,
    frames: Sequence[ETABSFrameV1],
    selection_evidence: Sequence[ETABSResultSelectionEvidenceV1],
    dispositions: list[ETABSBaselineDispositionV1],
) -> tuple[ETABSFrameResultV1, ...]:
    requested = {item.selection.name: item for item in selection_evidence}
    results: list[ETABSFrameResultV1] = []
    for frame in sorted(
        (item for item in frames if item.kind is ETABSFrameKind.BEAM),
        key=lambda item: item.member_id,
    ):
        outputs = _decode_com_outputs(
            "Results.FrameForce",
            sap_model.Results.FrameForce(
                frame.source_unique_name, ETABS_OBJECT_ITEM_TYPE
            ),
            output_count=14,
        )
        count = _exact_int("Results.FrameForce", "count", outputs[0])
        if count < 0 or count > MAX_FORCE_ROWS_PER_FRAME:
            raise ETABSDataError(
                "ETABS_FRAME_RESULTS_COUNT_INVALID",
                f"Frame {frame.source_unique_name!r} returned invalid count {count}.",
            )
        names = (
            "object_name",
            "object_station_mm",
            "element_name",
            "element_station_mm",
            "load_case",
            "step_type",
            "step_number",
            "p_kn",
            "v2_kn",
            "v3_kn",
            "t_knmm",
            "m2_knmm",
            "m3_knmm",
        )
        arrays = {
            name: _exact_array(
                "Results.FrameForce", name, outputs[index], expected_count=count
            )
            for index, name in enumerate(names, start=1)
        }
        stations_by_selection: dict[str, list[ETABSForceStationV1]] = defaultdict(list)
        occurrences: Counter[str] = Counter()
        for index in range(count):
            load_case = _nonblank(
                "Results.FrameForce", "load case", arrays["load_case"][index]
            )
            object_name = _nonblank(
                "Results.FrameForce", "object name", arrays["object_name"][index]
            )
            if object_name != frame.source_unique_name:
                raise ETABSDataError(
                    "ETABS_RESULT_MEMBER_MISMATCH",
                    f"FrameForce requested {frame.source_unique_name!r} but returned object {object_name!r}.",
                )
            object_station_mm = _finite_float(
                "Results.FrameForce",
                "object station",
                arrays["object_station_mm"][index],
            )
            element_name = _nonblank(
                "Results.FrameForce", "element name", arrays["element_name"][index]
            )
            element_station_mm = _finite_float(
                "Results.FrameForce",
                "element station",
                arrays["element_station_mm"][index],
            )
            step_type = str(arrays["step_type"][index])
            step_number = _finite_float(
                "Results.FrameForce", "step number", arrays["step_number"][index]
            )
            p_kn = _finite_float("Results.FrameForce", "P", arrays["p_kn"][index])
            v2_kn = _finite_float("Results.FrameForce", "V2", arrays["v2_kn"][index])
            v3_kn = _finite_float("Results.FrameForce", "V3", arrays["v3_kn"][index])
            t_knm = (
                _finite_float("Results.FrameForce", "T", arrays["t_knmm"][index])
                / 1000.0
            )
            m2_knm = (
                _finite_float("Results.FrameForce", "M2", arrays["m2_knmm"][index])
                / 1000.0
            )
            m3_knm = (
                _finite_float("Results.FrameForce", "M3", arrays["m3_knmm"][index])
                / 1000.0
            )
            raw_payload = {
                "member_id": frame.member_id,
                "load_case": load_case,
                "object_name": object_name,
                "object_station_mm": object_station_mm,
                "element_name": element_name,
                "element_station_mm": element_station_mm,
                "step_type": step_type,
                "step_number": step_number,
                "p_kn": p_kn,
                "v2_kn": v2_kn,
                "v3_kn": v3_kn,
                "t_knm": t_knm,
                "m2_knm": m2_knm,
                "m3_knm": m3_knm,
            }
            content_hash = _canonical_sha256(raw_payload)
            occurrence = occurrences[content_hash]
            occurrences[content_hash] += 1
            source_id = f"{frame.source_unique_name}:{index}:{load_case}"
            selection_record = requested.get(load_case)
            if selection_record is None:
                dispositions.append(
                    _disposition(
                        row_kind=ETABSBaselineRowKind.RESULT_STATION,
                        source_id=source_id,
                        disposition=ETABSBaselineDisposition.EXCLUDED,
                        reason_code="RESULT_SELECTION_NOT_REQUESTED",
                        canonical_id=frame.member_id,
                        message="FrameForce row belongs to an unrequested active output selection.",
                    )
                )
                continue
            station_id = _stable_id(
                "etabs-station",
                {"content_sha256": content_hash, "occurrence": occurrence},
            )
            station = ETABSForceStationV1(
                station_id=station_id,
                member_id=frame.member_id,
                source_frame_name=frame.source_unique_name,
                source_row_index=index,
                selection=selection_record.selection,
                object_name=object_name,
                object_station_mm=object_station_mm,
                element_name=element_name,
                element_station_mm=element_station_mm,
                step_type=step_type,
                step_number=step_number,
                p_kn=p_kn,
                v2_kn=v2_kn,
                v3_kn=v3_kn,
                t_knm=t_knm,
                m2_knm=m2_knm,
                m3_knm=m3_knm,
            )
            stations_by_selection[load_case].append(station)
            dispositions.append(
                _disposition(
                    row_kind=ETABSBaselineRowKind.RESULT_STATION,
                    source_id=source_id,
                    disposition=ETABSBaselineDisposition.ACCEPTED,
                    reason_code="RESULT_STATION_ACCEPTED",
                    canonical_id=station_id,
                    message="Complete FrameForce station retained with signed components and explicit selection.",
                )
            )
        for selection_name, evidence in requested.items():
            stations = stations_by_selection.get(selection_name, [])
            if not stations:
                dispositions.append(
                    _disposition(
                        row_kind=ETABSBaselineRowKind.RESULT_STATION,
                        source_id=f"{frame.source_unique_name}:{selection_name}",
                        disposition=ETABSBaselineDisposition.BLOCKED,
                        reason_code="RESULT_SELECTION_EMPTY_FOR_BEAM",
                        canonical_id=frame.member_id,
                        message="No FrameForce station was returned for this explicit beam/result selection.",
                    )
                )
                continue
            results.append(
                ETABSFrameResultV1(
                    member_id=frame.member_id,
                    source_frame_name=frame.source_unique_name,
                    selection_evidence=evidence,
                    stations=tuple(
                        sorted(
                            stations,
                            key=lambda item: (
                                item.object_station_mm,
                                item.element_name,
                                item.element_station_mm,
                                item.step_type,
                                item.step_number,
                                item.station_id,
                            ),
                        )
                    ),
                )
            )
    return tuple(
        sorted(
            results,
            key=lambda item: (item.member_id, item.selection_evidence.selection.name),
        )
    )


def _getter_matrix_sha256() -> str:
    return _canonical_sha256(
        [item.model_dump(mode="json") for item in etabs_w2a_getter_matrix_v1()]
    )


def etabs_w2a_getter_matrix_sha256_v1() -> str:
    """Return the deterministic identity of the frozen W2A getter matrix."""

    return _getter_matrix_sha256()


def _baseline_hash_payload(baseline: ETABSBeamBaselineV1) -> dict[str, Any]:
    payload = baseline.model_dump(mode="json")
    payload.pop("baseline_sha256", None)
    return payload


def canonical_etabs_beam_baseline_hash_basis_json_v1(
    baseline: ETABSBeamBaselineV1,
) -> str:
    """Serialize the exact UTF-8 JSON text whose digest is ``baseline_sha256``."""

    return json.dumps(
        _baseline_hash_payload(baseline),
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def verify_etabs_beam_baseline_hash_v1(baseline: ETABSBeamBaselineV1) -> bool:
    """Verify the canonical SHA-256 over every retained W2A field."""

    encoded = canonical_etabs_beam_baseline_hash_basis_json_v1(baseline).encode("utf-8")
    return sha256(encoded).hexdigest() == baseline.baseline_sha256


def _blocked_issues(
    dispositions: Sequence[ETABSBaselineDispositionV1],
) -> tuple[ETABSBaselineIssueV1, ...]:
    return tuple(
        ETABSBaselineIssueV1(
            code=row.reason_code,
            path=f"{row.row_kind.value.lower()}:{row.source_id}",
            message=row.message,
        )
        for row in dispositions
        if row.disposition is ETABSBaselineDisposition.BLOCKED
    )


def extract_etabs_beam_baseline_v1(
    sap_model: Any,
    request: ETABSBeamBaselineRequestV1,
    *,
    observe_model_file: ETABSModelFileObserverV1,
) -> ETABSBaselineBuildResultV1:
    """Extract the complete local W2A baseline from a supplied SapModel shape.

    Result cases/combinations must already be selected for output. W2A verifies
    their state with getters and never calls the result-selection setters. The
    supplied read-only observer is called immediately before and after COM reads
    so the authorized model hash, size, timestamp, and path bracket extraction.
    """

    authorized = request.authorized_model_file
    before_read = observe_model_file(authorized.model_path)
    if not isinstance(before_read, ETABSModelFileSnapshotV1):
        raise ETABSDataError(
            "ETABS_MODEL_FILE_OBSERVER_INVALID",
            "The model-file observer must return ETABSModelFileSnapshotV1.",
        )
    if not _same_model_file_identity(authorized, before_read):
        raise ETABSDataError(
            "ETABS_MODEL_AUTHORIZATION_MISMATCH",
            "The current model file identity does not match the authorized path, hash, size, and timestamp.",
        )
    model = _read_model_identity(sap_model, before_read)
    dispositions: list[ETABSBaselineDispositionV1] = []
    with _normalized_units(sap_model) as original_units:
        stories, story_dispositions = _read_stories(sap_model)
        dispositions.extend(story_dispositions)
        frames, candidates, frame_dispositions = _read_frames(
            sap_model,
            model_sha256=before_read.sha256,
            story_names=frozenset(story.name for story in stories),
            tolerance_mm=request.orientation_tolerance_mm,
        )
        dispositions.extend(frame_dispositions)
        connectivity, connection_dispositions = _read_connectivity(candidates)
        dispositions.extend(connection_dispositions)
        selection_evidence = _selection_evidence(
            sap_model, request.result_selections, dispositions
        )
        accepted_beams = [
            frame for frame in frames if frame.kind is ETABSFrameKind.BEAM
        ]
        if not accepted_beams:
            dispositions.append(
                _disposition(
                    row_kind=ETABSBaselineRowKind.FRAME,
                    source_id="beam-inventory",
                    disposition=ETABSBaselineDisposition.BLOCKED,
                    reason_code="BEAM_INVENTORY_EMPTY",
                    message="No rectangular horizontal beams remain after explicit dispositions.",
                )
            )
        pre_result_blocked = any(
            row.disposition is ETABSBaselineDisposition.BLOCKED for row in dispositions
        )
        results = (
            ()
            if pre_result_blocked
            else _read_results(sap_model, frames, selection_evidence, dispositions)
        )

    after_read = observe_model_file(authorized.model_path)
    if not isinstance(after_read, ETABSModelFileSnapshotV1):
        raise ETABSDataError(
            "ETABS_MODEL_FILE_OBSERVER_INVALID",
            "The model-file observer must return ETABSModelFileSnapshotV1.",
        )
    if not _same_model_file_identity(before_read, after_read):
        raise ETABSDataError(
            "ETABS_MODEL_FRESHNESS_FAILED",
            "The model file path, hash, size, or timestamp changed during extraction.",
        )
    if _parse_utc(after_read.observed_at_utc) < _parse_utc(before_read.observed_at_utc):
        raise ETABSDataError(
            "ETABS_MODEL_FRESHNESS_FAILED",
            "The post-read model observation precedes the pre-read observation.",
        )
    model = model.model_copy(
        update={
            "file_evidence": ETABSModelFileEvidenceV1(
                before_read=before_read,
                after_read=after_read,
            )
        }
    )

    ordered_dispositions = tuple(
        sorted(
            dispositions,
            key=lambda item: (
                item.row_kind.value,
                item.source_id,
                item.reason_code,
                item.row_id,
            ),
        )
    )
    issues = _blocked_issues(ordered_dispositions)
    if issues:
        return ETABSBaselineBuildResultV1(
            status=ETABSBaselineBuildStatus.BLOCKED,
            dispositions=ordered_dispositions,
            issues=issues,
            baseline=None,
        )

    unit_proof = ETABSUnitProofV1(
        original_present_units_enum=original_units,
        restored_present_units_enum=original_units,
    )
    frame_analysis_basis = (
        "gravity_workflow uses closed-form simply supported actions and declares no stiffness/frame solver",
        "gravity_loads performs closed-form vertical load transfer and declares it is not a frame solver",
        "beam serviceability holds multi-span continuous behavior for frame analysis",
    )
    limitations = (
        "W2A local contract only: no ETABS connection, launch, analysis, design, save, or write-back.",
        "No REST or Excel W2 transport surface is included.",
        "Only horizontal/vertical rectangular frame members are retained; every other frame is explicitly dispositioned.",
        "Material-property labels are identities only; concrete grade, steel grade, cover, bars, and design standard are not inferred.",
        "Area/slab adjacency is not claimed because no deterministic W2A association getter is frozen.",
        "Qualified structural-engineering review remains required before engineering or construction use.",
    )
    provisional = ETABSBeamBaselineV1(
        model=model,
        units=unit_proof,
        stories=stories,
        frames=frames,
        connectivity=connectivity,
        results=results,
        dispositions=ordered_dispositions,
        runtime_provenance=request.runtime_provenance,
        getter_matrix_sha256=_getter_matrix_sha256(),
        frame_analysis_basis=frame_analysis_basis,
        limitations=limitations,
        baseline_sha256="0" * 64,
    )
    baseline = provisional.model_copy(
        update={
            "baseline_sha256": _canonical_sha256(_baseline_hash_payload(provisional))
        }
    )
    if not verify_etabs_beam_baseline_hash_v1(baseline):
        raise ETABSDataError(
            "ETABS_BASELINE_HASH_INVALID",
            "Internal W2A baseline hash verification failed.",
        )
    return ETABSBaselineBuildResultV1(
        status=ETABSBaselineBuildStatus.ACCEPTED,
        dispositions=ordered_dispositions,
        issues=(),
        baseline=baseline,
    )
