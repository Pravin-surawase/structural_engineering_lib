# SPDX-License-Identifier: MIT
"""Getter-only Windows transport for one complete W3 ETABS catalogue.

The service attaches only to an already-open saved copied model, verifies the
caller-frozen file/runtime/getter identity, invokes the transport-neutral W3C
adapter, and proves file, lock, units, statuses, and output selections are
unchanged.  It contains no setter, result-force, analysis, design, save, Excel,
or professional-approval operation.
"""

from __future__ import annotations

from collections.abc import Callable
from hashlib import sha256
from pathlib import PureWindowsPath
from typing import Any, Literal, Self

from pydantic import Field, model_validator

from structural_lib.services.contracts.common import StrictPublicModel
from structural_lib.services.contracts.etabs_w3 import (
    W3BuildStatusV1,
    canonical_etabs_result_catalogue_hash_basis_json_v1,
)
from structural_lib.services.etabs_beam_baseline import ETABSModelFileSnapshotV1
from structural_lib.services.etabs_beam_bridge import observe_etabs_model_file_v1
from structural_lib.services.etabs_live_bridge import (
    ETABSConnectionError,
    ETABSDataError,
    SessionFactory,
    _decode_com_outputs,
    _default_session_factory,
    etabs_com_operation_v1,
)
from structural_lib.services.etabs_result_catalogue_adapter import (
    ETABSCatalogueAdapterRequestV1,
    ETABSCatalogueAdapterResultV1,
    ETABSCatalogueSelectionRequestV1,
    extract_etabs_result_catalogue_v1,
)

__all__ = [
    "ETABSLiveCaseStatusV1",
    "ETABSLiveCatalogueRunRequestV1",
    "ETABSLiveCatalogueStateV1",
    "ETABSLiveCatalogueTransportV1",
    "ETABSLiveSelectionStateV1",
    "run_etabs_live_catalogue_v1",
]

_SHA256_PATTERN = r"^[0-9a-f]{64}$"
_UTC_PATTERN = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$"


class ETABSLiveCaseStatusV1(StrictPublicModel):
    name: str = Field(min_length=1, max_length=160)
    raw_status: int = Field(ge=0)


class ETABSLiveSelectionStateV1(StrictPublicModel):
    kind: Literal["CASE", "COMBINATION"]
    name: str = Field(min_length=1, max_length=160)
    selected: bool


class ETABSLiveCatalogueStateV1(StrictPublicModel):
    model_path: str = Field(min_length=1)
    etabs_version: str = Field(min_length=1)
    etabs_version_number: float
    model_locked: bool
    present_units_enum: int = Field(ge=1)
    case_statuses: tuple[ETABSLiveCaseStatusV1, ...] = Field(min_length=1)
    output_selections: tuple[ETABSLiveSelectionStateV1, ...] = Field(min_length=1)


class ETABSLiveCatalogueRunRequestV1(StrictPublicModel):
    """Exact direct-evidence request replayed through localhost REST."""

    schema_version: Literal["etabs-live-catalogue-run-request/v1"] = (
        "etabs-live-catalogue-run-request/v1"
    )
    authorized_model_file: ETABSModelFileSnapshotV1
    expected_etabs_version: str = Field(min_length=1)
    expected_etabs_version_number: float
    expected_present_units_enum: int = Field(ge=1)
    runtime_identity_sha256: str = Field(pattern=_SHA256_PATTERN)
    getter_matrix_sha256: str = Field(pattern=_SHA256_PATTERN)
    model_observation_before: str = Field(min_length=1, max_length=500)
    model_observation_after: str = Field(min_length=1, max_length=500)
    observed_at_utc: str = Field(pattern=_UTC_PATTERN)
    result_selections: list[ETABSCatalogueSelectionRequestV1] = Field(
        min_length=1,
        max_length=1_000,
    )
    capacity_limit: int = Field(default=100_000, ge=1, le=100_000)
    require_locked_model: Literal[True] = True
    approved_copy_confirmed: Literal[True]

    @model_validator(mode="after")
    def validate_selection_identity(self) -> Self:
        identities = [
            (selection.kind.value, selection.name)
            for selection in self.result_selections
        ]
        if len(identities) != len(set(identities)):
            raise ValueError("result selections must be unique and ordered")
        return self


class ETABSLiveCatalogueTransportV1(StrictPublicModel):
    schema_version: Literal["etabs-live-catalogue-transport/v1"] = (
        "etabs-live-catalogue-transport/v1"
    )
    adapter_result: ETABSCatalogueAdapterResultV1
    model_file_before: ETABSModelFileSnapshotV1
    model_file_after: ETABSModelFileSnapshotV1
    live_state_before: ETABSLiveCatalogueStateV1
    live_state_after: ETABSLiveCatalogueStateV1
    catalogue_hash_basis_json: str | None
    catalogue_hash_basis_utf8_bytes: int = Field(ge=0)
    no_setter_force_analysis_design_save_or_excel_call: Literal[True] = True
    frame_analysis_verdict: Literal["HELD_NOT_SUPPORTED"] = "HELD_NOT_SUPPORTED"
    professional_approval: Literal[False] = False

    @model_validator(mode="after")
    def validate_complete_transport(self) -> Self:
        if self.live_state_before != self.live_state_after:
            raise ValueError("live catalogue transport requires unchanged ETABS state")
        if not _same_snapshot(self.model_file_before, self.model_file_after):
            raise ValueError("live catalogue transport requires unchanged model file")
        if self.adapter_result.status is W3BuildStatusV1.ACCEPTED:
            catalogue = self.adapter_result.catalogue
            if catalogue is None or self.catalogue_hash_basis_json is None:
                raise ValueError("accepted transport requires the complete catalogue")
            encoded = self.catalogue_hash_basis_json.encode("utf-8")
            if len(encoded) != self.catalogue_hash_basis_utf8_bytes:
                raise ValueError("catalogue hash-basis byte count does not match")
            if sha256(encoded).hexdigest() != catalogue.catalogue_sha256:
                raise ValueError("catalogue hash basis does not match catalogue digest")
        elif (
            self.catalogue_hash_basis_json is not None
            or self.catalogue_hash_basis_utf8_bytes
        ):
            raise ValueError("blocked transport forbids a partial catalogue hash basis")
        return self


ModelFileObserver = Callable[[str], ETABSModelFileSnapshotV1]


def _same_snapshot(
    expected: ETABSModelFileSnapshotV1,
    observed: ETABSModelFileSnapshotV1,
) -> bool:
    return (
        PureWindowsPath(expected.model_path) == PureWindowsPath(observed.model_path)
        and expected.model_name == observed.model_name
        and expected.sha256 == observed.sha256
        and expected.byte_count == observed.byte_count
        and expected.modified_at_utc == observed.modified_at_utc
    )


def _name_list(operation: str, provider: Callable[[], Any]) -> tuple[str, ...]:
    count, raw_names = _decode_com_outputs(operation, provider(), output_count=2)
    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        raise ETABSDataError(
            "ETABS_CATALOGUE_STATE_INVALID",
            f"{operation} returned an invalid count.",
        )
    if not isinstance(raw_names, (list, tuple)) or len(raw_names) != count:
        raise ETABSDataError(
            "ETABS_CATALOGUE_STATE_INVALID",
            f"{operation} returned a count/container mismatch.",
        )
    names = tuple(str(value).strip() for value in raw_names)
    if any(not name for name in names) or len(names) != len(set(names)):
        raise ETABSDataError(
            "ETABS_CATALOGUE_STATE_INVALID",
            f"{operation} returned blank or duplicate names.",
        )
    return names


def _selection_state(
    sap_model: Any,
    kind: Literal["CASE", "COMBINATION"],
    name: str,
) -> ETABSLiveSelectionStateV1:
    operation = (
        "Results.Setup.GetCaseSelectedForOutput"
        if kind == "CASE"
        else "Results.Setup.GetComboSelectedForOutput"
    )
    provider = (
        sap_model.Results.Setup.GetCaseSelectedForOutput
        if kind == "CASE"
        else sap_model.Results.Setup.GetComboSelectedForOutput
    )
    (selected,) = _decode_com_outputs(
        operation,
        provider(name),
        output_count=1,
    )
    if not isinstance(selected, bool):
        raise ETABSDataError(
            "ETABS_CATALOGUE_STATE_INVALID",
            f"{operation} did not return a boolean.",
        )
    return ETABSLiveSelectionStateV1(kind=kind, name=name, selected=selected)


def _read_state(sap_model: Any) -> ETABSLiveCatalogueStateV1:
    model_path = str(sap_model.GetModelFilename(True) or "").strip()
    parsed = PureWindowsPath(model_path)
    if not model_path or not parsed.is_absolute() or parsed.suffix.casefold() != ".edb":
        raise ETABSConnectionError(
            "ETABS_MODEL_PATH_INVALID",
            "ETABS did not return the full path of a saved .edb model.",
        )
    version, version_number = _decode_com_outputs(
        "SapModel.GetVersion",
        sap_model.GetVersion(),
        output_count=2,
    )
    locked = sap_model.GetModelIsLocked()
    units = sap_model.GetPresentUnits()
    if not isinstance(locked, bool):
        raise ETABSDataError(
            "ETABS_MODEL_LOCK_STATE_INVALID",
            "SapModel.GetModelIsLocked did not return a boolean.",
        )
    if isinstance(units, bool) or not isinstance(units, int) or units <= 0:
        raise ETABSDataError(
            "ETABS_PRESENT_UNITS_INVALID",
            "SapModel.GetPresentUnits did not return a valid eUnits integer.",
        )
    status_count, raw_status_names, raw_status_values = _decode_com_outputs(
        "Analyze.GetCaseStatus",
        sap_model.Analyze.GetCaseStatus(),
        output_count=3,
    )
    if (
        isinstance(status_count, bool)
        or not isinstance(status_count, int)
        or status_count <= 0
        or not isinstance(raw_status_names, (list, tuple))
        or not isinstance(raw_status_values, (list, tuple))
        or len(raw_status_names) != status_count
        or len(raw_status_values) != status_count
    ):
        raise ETABSDataError(
            "ETABS_CATALOGUE_STATE_INVALID",
            "Analyze.GetCaseStatus returned an invalid shape.",
        )
    case_statuses = tuple(
        ETABSLiveCaseStatusV1(
            name=str(raw_status_names[index]).strip(),
            raw_status=raw_status_values[index],
        )
        for index in range(status_count)
    )
    if any(not item.name for item in case_statuses) or len(
        {item.name for item in case_statuses}
    ) != len(case_statuses):
        raise ETABSDataError(
            "ETABS_CATALOGUE_STATE_INVALID",
            "Analyze.GetCaseStatus returned blank or duplicate names.",
        )
    case_names = _name_list("LoadCases.GetNameList", sap_model.LoadCases.GetNameList)
    combo_names = _name_list("RespCombo.GetNameList", sap_model.RespCombo.GetNameList)
    selections = tuple(
        [
            _selection_state(sap_model, "CASE", name)
            for name in case_names
        ]
        + [
            _selection_state(sap_model, "COMBINATION", name)
            for name in combo_names
        ]
    )
    return ETABSLiveCatalogueStateV1(
        model_path=model_path,
        etabs_version=str(version),
        etabs_version_number=float(version_number),
        model_locked=locked,
        present_units_enum=units,
        case_statuses=case_statuses,
        output_selections=selections,
    )


def _expected_model_observation(snapshot: ETABSModelFileSnapshotV1) -> str:
    return (
        f"model-file-sha256:{snapshot.sha256};"
        f"bytes:{snapshot.byte_count};mtime:{snapshot.modified_at_utc}"
    )


def _verify_preflight(
    request: ETABSLiveCatalogueRunRequestV1,
    snapshot: ETABSModelFileSnapshotV1,
    state: ETABSLiveCatalogueStateV1,
) -> None:
    if not _same_snapshot(request.authorized_model_file, snapshot):
        raise ETABSDataError(
            "ETABS_MODEL_FILE_IDENTITY_MISMATCH",
            "The authorized copied-model file identity changed before extraction.",
        )
    if PureWindowsPath(state.model_path) != PureWindowsPath(snapshot.model_path):
        raise ETABSDataError(
            "ETABS_MODEL_IDENTITY_MISMATCH",
            "The open ETABS model is not the authorized copied model.",
        )
    if (
        state.etabs_version != request.expected_etabs_version
        or state.etabs_version_number != request.expected_etabs_version_number
    ):
        raise ETABSDataError(
            "ETABS_VERSION_MISMATCH",
            "The attached ETABS runtime differs from the frozen request.",
        )
    if not state.model_locked:
        raise ETABSDataError(
            "ETABS_MODEL_NOT_LOCKED",
            "The copied ETABS model must remain locked with current results.",
        )
    if state.present_units_enum != request.expected_present_units_enum:
        raise ETABSDataError(
            "ETABS_PRESENT_UNITS_MISMATCH",
            "ETABS present units differ from the frozen request.",
        )
    expected_observation = _expected_model_observation(snapshot)
    if (
        request.model_observation_before != expected_observation
        or request.model_observation_after != expected_observation
    ):
        raise ETABSDataError(
            "ETABS_MODEL_OBSERVATION_MISMATCH",
            "The catalogue request is not bound to the current model-file identity.",
        )


def run_etabs_live_catalogue_v1(
    request: ETABSLiveCatalogueRunRequestV1,
    *,
    session_factory: SessionFactory | None = None,
    observe_model_file: ModelFileObserver | None = None,
) -> ETABSLiveCatalogueTransportV1:
    """Run one complete getter-only W3 catalogue extraction and state bracket."""

    resolved_session_factory = session_factory or _default_session_factory
    resolved_model_observer = observe_model_file or observe_etabs_model_file_v1
    model_file_before = resolved_model_observer(
        request.authorized_model_file.model_path
    )
    with etabs_com_operation_v1():
        with resolved_session_factory() as session:
            state_before = _read_state(session.sap_model)
            _verify_preflight(request, model_file_before, state_before)
            adapter_result = extract_etabs_result_catalogue_v1(
                session.sap_model,
                ETABSCatalogueAdapterRequestV1(
                    model_identity_sha256=model_file_before.sha256,
                    runtime_identity_sha256=request.runtime_identity_sha256,
                    getter_matrix_sha256=request.getter_matrix_sha256,
                    model_observation_before=request.model_observation_before,
                    model_observation_after=request.model_observation_after,
                    observed_at_utc=request.observed_at_utc,
                    result_selections=tuple(request.result_selections),
                    capacity_limit=request.capacity_limit,
                ),
            )
            state_after = _read_state(session.sap_model)
    model_file_after = resolved_model_observer(request.authorized_model_file.model_path)
    if state_before != state_after:
        raise ETABSDataError(
            "ETABS_CATALOGUE_STATE_CHANGED",
            "ETABS lock, units, statuses, or output selections changed during extraction.",
        )
    if not _same_snapshot(model_file_before, model_file_after):
        raise ETABSDataError(
            "ETABS_MODEL_FILE_CHANGED",
            "The authorized copied model file changed during extraction.",
        )
    catalogue = adapter_result.catalogue
    hash_basis = (
        canonical_etabs_result_catalogue_hash_basis_json_v1(catalogue)
        if catalogue is not None
        else None
    )
    return ETABSLiveCatalogueTransportV1(
        adapter_result=adapter_result,
        model_file_before=model_file_before,
        model_file_after=model_file_after,
        live_state_before=state_before,
        live_state_after=state_after,
        catalogue_hash_basis_json=hash_basis,
        catalogue_hash_basis_utf8_bytes=(
            len(hash_basis.encode("utf-8")) if hash_basis is not None else 0
        ),
    )
