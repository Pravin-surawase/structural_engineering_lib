"""PID-specific, getter-only installed ETABS observation transport.

The public runner accepts only an A1 preflight that selected one exact process
instance and model intent.  The worker exposes getters only, records every COM
call durably, and brackets the observation with process, runtime, model-file,
and application-state checks.  It never opens a model or invokes a model/session
setter, save, analysis, design, unlock, or application-exit method.
"""

from __future__ import annotations

import hashlib
import importlib
import json
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime, timedelta
from functools import partial
from pathlib import Path
from typing import Any, Literal, Protocol, Self

from pydantic import Field, model_validator

from structural_lib.services.contracts.common import StrictPublicModel
from structural_lib.services.etabs_operation_control import (
    ETABSBrokerResultV1,
    ETABSCallLedgerIdentityV1,
    ETABSCallLedgerV1,
    ETABSOperationLeaseV1,
    ETABSOperationOutcomeV1,
    acquire_etabs_operation_lease_v1,
    build_etabs_operation_outcome_v1,
    invoke_recorded_etabs_call_v1,
    run_etabs_sta_broker_v1,
    verify_etabs_call_ledger_v1,
)
from structural_lib.services.etabs_session_guard import (
    ETABSAccessModeV1,
    ETABSInstalledReadOnlyPreflightV1,
    ETABSProcessInstanceV1,
    ETABSRuntimeFingerprintV1,
    ETABSSessionIdentityV1,
    ETABSStateSnapshotV1,
    ETABSTargetObservationV1,
    ProcessObservationV1,
    assess_attached_output_readiness_v1,
    build_etabs_runtime_fingerprint_v1,
    build_etabs_session_identity_v1,
    capture_attached_etabs_state_v1,
    classify_etabs_model_freshness_v1,
    compare_attached_etabs_state_v1,
    discover_etabs_processes_v1,
    file_identity_v1,
    observe_etabs_target_v1,
    verify_etabs_target_observation_v1,
)

__all__ = [
    "ETABSInstalledReadOnlyCaptureV1",
    "ETABSInstalledReadOnlyReaderV1",
    "ETABSInstalledReadOnlyRunV1",
    "capture_etabs_installed_readonly_v1",
    "etabs_state_content_sha256_v1",
    "run_etabs_installed_readonly_v1",
]

_SHA = r"^[0-9a-f]{64}$"
_ATTACH_TYPE_NAME = "CSI.ETABS.API.ETABSObject"


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _utc(value: datetime, field: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field} must be timezone-aware")
    return value.astimezone(UTC)


def etabs_state_content_sha256_v1(snapshot: ETABSStateSnapshotV1, /) -> str:
    """Hash normalized state content while excluding observation time."""

    return _digest(
        snapshot.model_dump(
            mode="json",
            exclude={"observed_at_utc", "state_sha256"},
        )
    )


class ETABSInstalledReadOnlyReaderV1(Protocol):
    """The complete getter-only surface accepted by the A1 capture."""

    def read_session_identity(
        self,
        process_instance: ETABSProcessInstanceV1,
        observed_at_utc: datetime,
    ) -> ETABSSessionIdentityV1: ...

    def get_present_units(self) -> str: ...

    def get_model_locked(self) -> bool: ...

    def get_selected_output_cases(self) -> Sequence[str]: ...

    def get_selected_output_combinations(self) -> Sequence[str]: ...

    def get_case_statuses(self) -> Mapping[str, str]: ...

    def get_run_flags(self) -> Mapping[str, bool]: ...

    def get_table_display_selection_sha256(self) -> str | None: ...


class ETABSInstalledReadOnlyCaptureV1(StrictPublicModel):
    schema_version: Literal["etabs-installed-readonly-capture/v1"] = (
        "etabs-installed-readonly-capture/v1"
    )
    disposition: Literal["READONLY_ACCEPTED_WITH_FRESHNESS_HOLD"] = (
        "READONLY_ACCEPTED_WITH_FRESHNESS_HOLD"
    )
    preflight_sha256: str = Field(pattern=_SHA)
    target_observation: ETABSTargetObservationV1
    session_before: ETABSSessionIdentityV1
    session_after: ETABSSessionIdentityV1
    state_before: ETABSStateSnapshotV1
    state_after: ETABSStateSnapshotV1
    state_content_sha256: str = Field(pattern=_SHA)
    output_readiness: Literal["READY", "HOLD"]
    comparison_basis_allowed: Literal[False] = False
    no_setter_save_analysis_design_unlock_or_exit_call: Literal[True] = True
    limitations: tuple[str, ...] = Field(min_length=1)
    capture_sha256: str = Field(pattern=_SHA)

    @model_validator(mode="after")
    def validate_capture(self) -> Self:
        target = self.target_observation
        if target.allowed_access is not ETABSAccessModeV1.ATTACHED_OBSERVE:
            raise ValueError("installed read-only capture requires attached access")
        if target.model_freshness.hash_bound_baseline_allowed:
            raise ValueError("attached A1 capture cannot claim a hash-bound baseline")
        if (
            self.session_before.session_sha256 != self.session_after.session_sha256
            or target.session_identity.session_sha256
            != self.session_before.session_sha256
        ):
            raise ValueError("installed read-only capture session changed")
        if (
            self.state_before.session_sha256 != self.session_before.session_sha256
            or self.state_after.session_sha256 != self.session_before.session_sha256
        ):
            raise ValueError("installed read-only state is bound to another session")
        if compare_attached_etabs_state_v1(self.state_before, self.state_after) != (
            "COMPLETED"
        ):
            raise ValueError("installed read-only capture state changed")
        before_content = etabs_state_content_sha256_v1(self.state_before)
        after_content = etabs_state_content_sha256_v1(self.state_after)
        if (
            before_content != after_content
            or self.state_content_sha256 != before_content
        ):
            raise ValueError("installed read-only state content digest differs")
        before_file = self.session_before.saved_file_identity
        after_file = self.session_after.saved_file_identity
        if before_file is None or before_file != after_file:
            raise ValueError("installed read-only capture requires equal saved files")
        expected = _digest(self.model_dump(mode="json", exclude={"capture_sha256"}))
        if self.capture_sha256 != expected:
            raise ValueError("capture_sha256 does not match canonical capture")
        return self


class ETABSInstalledReadOnlyRunV1(StrictPublicModel):
    schema_version: Literal["etabs-installed-readonly-run/v1"] = (
        "etabs-installed-readonly-run/v1"
    )
    disposition: Literal["COMPLETED", "HOLD", "RESTORATION_UNVERIFIED"]
    preflight: ETABSInstalledReadOnlyPreflightV1
    broker_result: ETABSBrokerResultV1
    operation_outcome: ETABSOperationOutcomeV1
    capture: ETABSInstalledReadOnlyCaptureV1 | None = None
    lease_receipt: ETABSOperationLeaseV1
    run_sha256: str = Field(pattern=_SHA)

    @model_validator(mode="after")
    def validate_run(self) -> Self:
        if self.preflight.disposition != "READY_FOR_GETTER_ONLY_ATTACH":
            raise ValueError("installed run requires a ready preflight")
        if self.disposition == "COMPLETED":
            if (
                self.capture is None
                or self.broker_result.status != "COMPLETED"
                or self.operation_outcome.disposition != "COMPLETED"
                or self.lease_receipt.disposition != "RELEASED"
            ):
                raise ValueError("completed installed run requires closed evidence")
        elif self.capture is not None:
            raise ValueError(
                "non-completed installed run cannot expose partial capture"
            )
        if self.disposition == "RESTORATION_UNVERIFIED":
            if self.operation_outcome.disposition != "RESTORATION_UNVERIFIED":
                raise ValueError("unverified run requires an unverified outcome")
        elif self.disposition == "HOLD" and self.operation_outcome.disposition != (
            "BLOCKED"
        ):
            raise ValueError("held run requires a blocked operation outcome")
        expected = _digest(self.model_dump(mode="json", exclude={"run_sha256"}))
        if self.run_sha256 != expected:
            raise ValueError("run_sha256 does not match canonical installed run")
        return self


ProcessProviderV1 = Callable[[], Sequence[ProcessObservationV1]]


def _runtime_artifact_path(
    runtime: ETABSRuntimeFingerprintV1,
    name: str,
) -> str | None:
    artifact = next((item for item in runtime.artifacts if item.name == name), None)
    return artifact.canonical_path if artifact is not None else None


def _current_exact_process(
    expected: ETABSProcessInstanceV1,
    *,
    process_provider: ProcessProviderV1 | None,
    observed_at_utc: datetime,
) -> ETABSProcessInstanceV1:
    processes = discover_etabs_processes_v1(
        process_provider=process_provider,
        observed_at_utc=observed_at_utc,
    )
    current = next(
        (
            process
            for process in processes
            if process.pid == expected.pid
            and process.start_time_utc == expected.start_time_utc
        ),
        None,
    )
    if current is None:
        raise RuntimeError("ETABS_SELECTED_PROCESS_INSTANCE_NOT_RUNNING")
    return current


def _rebuild_runtime(
    expected: ETABSRuntimeFingerprintV1,
    current_process: ETABSProcessInstanceV1,
    observed_at_utc: datetime,
) -> ETABSRuntimeFingerprintV1:
    return build_etabs_runtime_fingerprint_v1(
        current_process,
        type_library_path=_runtime_artifact_path(
            expected,
            "ETABSV1_TYPE_LIBRARY",
        ),
        generated_wrapper_path=_runtime_artifact_path(
            expected,
            "COMTYPES_GENERATED_WRAPPER",
        ),
        installed_chm_path=_runtime_artifact_path(expected, "INSTALLED_CHM"),
        com_shape_runtime=expected.com_shape_runtime,
        observed_at_utc=observed_at_utc,
    )


def capture_etabs_installed_readonly_v1(
    preflight: ETABSInstalledReadOnlyPreflightV1,
    reader: ETABSInstalledReadOnlyReaderV1,
    /,
    *,
    required_cases: Sequence[str] = (),
    required_combinations: Sequence[str] = (),
    process_provider: ProcessProviderV1 | None = None,
    observed_at_utc: datetime | None = None,
    verified_at_utc: datetime | None = None,
) -> ETABSInstalledReadOnlyCaptureV1:
    """Capture and revalidate one attached getter-only observation."""

    if preflight.disposition != "READY_FOR_GETTER_ONLY_ATTACH":
        raise RuntimeError("ETABS_INSTALLED_READONLY_PREFLIGHT_HOLD")
    process = preflight.selected_process
    runtime = preflight.runtime_fingerprint
    if process is None or runtime is None:  # protected by the preflight model
        raise RuntimeError("ETABS_INSTALLED_READONLY_PREFLIGHT_INCOMPLETE")
    started = _utc(observed_at_utc or datetime.now(UTC), "observed_at_utc")
    session_before = reader.read_session_identity(process, started)
    file_before = session_before.saved_file_identity
    if file_before is None:
        raise RuntimeError("ETABS_ATTACHED_MODEL_FILE_UNAVAILABLE")
    freshness_file = file_identity_v1(file_before.canonical_path)
    if freshness_file != file_before:
        raise RuntimeError("ETABS_ATTACHED_MODEL_FILE_CHANGED_BEFORE_CAPTURE")
    target_time = (
        max(started, datetime.now(UTC)) if observed_at_utc is None else started
    )
    freshness = classify_etabs_model_freshness_v1(
        session_identity=session_before,
        before_file=file_before,
        after_file=freshness_file,
        observed_at_utc=target_time,
        attached_session=True,
    )
    target = observe_etabs_target_v1(
        process,
        preflight.expected_intent,
        runtime,
        session_before,
        freshness,
        observed_at_utc=target_time,
    )
    state_before = capture_attached_etabs_state_v1(
        reader,
        session_sha256=session_before.session_sha256,
        observed_at_utc=target_time,
    )
    completed = _utc(verified_at_utc or datetime.now(UTC), "verified_at_utc")
    if completed < target_time:
        raise ValueError("verified_at_utc cannot precede observation")
    state_after = capture_attached_etabs_state_v1(
        reader,
        session_sha256=session_before.session_sha256,
        observed_at_utc=completed,
    )
    session_after = reader.read_session_identity(process, completed)
    file_after = session_after.saved_file_identity
    if file_after is None or file_before != file_after:
        raise RuntimeError("ETABS_ATTACHED_MODEL_FILE_CHANGED")
    current_process = _current_exact_process(
        process,
        process_provider=process_provider,
        observed_at_utc=completed,
    )
    current_runtime = _rebuild_runtime(runtime, current_process, completed)
    verify_etabs_target_observation_v1(
        target,
        current_process=current_process,
        current_runtime=current_runtime,
        current_session=session_after,
        verified_at_utc=completed,
        maximum_revalidation_age=timedelta(minutes=2),
    )
    if compare_attached_etabs_state_v1(state_before, state_after) != "COMPLETED":
        raise RuntimeError("ETABS_ATTACHED_STATE_CHANGED")
    state_content = etabs_state_content_sha256_v1(state_before)
    output_readiness = assess_attached_output_readiness_v1(
        state_after,
        required_cases=required_cases,
        required_combinations=required_combinations,
    )
    limitations = (
        "Attached-session memory freshness is unknown without a reviewed clean signal.",
        "Table-display selection is unobserved because its installed getter is not accepted on this model/host.",
        "A1 proves getter-only identity and preservation, not result validity or approval.",
    )
    basis = {
        "schema_version": "etabs-installed-readonly-capture/v1",
        "disposition": "READONLY_ACCEPTED_WITH_FRESHNESS_HOLD",
        "preflight_sha256": preflight.preflight_sha256,
        "target_observation": target.model_dump(mode="json"),
        "session_before": session_before.model_dump(mode="json"),
        "session_after": session_after.model_dump(mode="json"),
        "state_before": state_before.model_dump(mode="json"),
        "state_after": state_after.model_dump(mode="json"),
        "state_content_sha256": state_content,
        "output_readiness": output_readiness,
        "comparison_basis_allowed": False,
        "no_setter_save_analysis_design_unlock_or_exit_call": True,
        "limitations": list(limitations),
    }
    return ETABSInstalledReadOnlyCaptureV1.model_validate(
        {
            **basis,
            "target_observation": target,
            "session_before": session_before,
            "session_after": session_after,
            "state_before": state_before,
            "state_after": state_after,
            "limitations": limitations,
            "capture_sha256": _digest(basis),
        }
    )


def _decode_scalar_string(operation: str, raw: object) -> str:
    value = str(raw).strip()
    if not value:
        raise RuntimeError(f"{operation} returned a blank value")
    return value


def _decode_scalar_bool(operation: str, raw: object) -> bool:
    if not isinstance(raw, bool):
        raise RuntimeError(f"{operation} returned a non-boolean value")
    return raw


def _decode_scalar_int(operation: str, raw: object) -> int:
    if isinstance(raw, bool) or not isinstance(raw, int):
        raise RuntimeError(f"{operation} returned a non-integer value")
    return raw


def _decode_outputs(operation: str, raw: object, count: int) -> tuple[Any, ...]:
    if not isinstance(raw, (list, tuple)) or len(raw) != count + 1:
        raise RuntimeError(f"{operation} returned an unexpected COM shape")
    code = raw[-1]
    if isinstance(code, bool) or not isinstance(code, int) or code != 0:
        raise RuntimeError(f"{operation} returned CSI status {code!r}")
    return tuple(raw[:-1])


class _ETABSPIDGetterOnlyReader:
    """Private getter projection; the underlying SapModel never escapes."""

    def __init__(
        self,
        process: ETABSProcessInstanceV1,
        ledger: ETABSCallLedgerV1,
        *,
        com_client: Any | None = None,
    ) -> None:
        self._process = process
        self._ledger = ledger
        self._call_number = 0
        client = com_client or importlib.import_module("comtypes.client")
        call_id = self._next_call_id()
        method = "cHelper.GetObjectProcess"
        signature = "GetObjectProcess(typeName: str, pid: int) -> cOAPI"
        arguments = {"type_name": _ATTACH_TYPE_NAME, "pid": process.pid}
        ledger.start(
            call_id=call_id,
            method=method,
            reviewed_signature=signature,
            redacted_arguments=arguments,
        )
        try:
            helper = client.CreateObject("ETABSv1.Helper")
            etabs_object = helper.GetObjectProcess(_ATTACH_TYPE_NAME, process.pid)
            sap_model = etabs_object.SapModel if etabs_object is not None else None
        except Exception as exc:
            ledger.returned(
                call_id=call_id,
                method=method,
                reviewed_signature=signature,
                redacted_arguments=arguments,
                raw_projection=None,
                raw_shape="CALL_RAISED",
                return_code=None,
                decoder=None,
                error=f"{type(exc).__name__}: {exc}",
            )
            raise
        ledger.returned(
            call_id=call_id,
            method=method,
            reviewed_signature=signature,
            redacted_arguments=arguments,
            raw_projection={"attached": sap_model is not None},
            raw_shape="COM_INTERFACE",
            return_code=None,
            decoder="pid-attach-v1",
            error=None,
        )
        if sap_model is None:
            raise RuntimeError("ETABS_SELECTED_PROCESS_HAS_NO_MODEL")
        self._helper = helper
        self._etabs_object = etabs_object
        self._sap_model = sap_model

    def _next_call_id(self) -> str:
        self._call_number += 1
        return f"CALL-{self._call_number:05d}"

    def _call(
        self,
        *,
        method: str,
        signature: str,
        arguments: Mapping[str, object],
        invoke: Callable[[], object],
        decode: Callable[[object], Any],
    ) -> Any:
        return invoke_recorded_etabs_call_v1(
            self._ledger,
            call_id=self._next_call_id(),
            method=method,
            reviewed_signature=signature,
            redacted_arguments=arguments,
            invoke=invoke,
            decode=decode,
            decoder_name="strict-installed-getter-v1",
        )

    def _name_list(self, owner: str, provider: Callable[[], object]) -> tuple[str, ...]:
        outputs = self._call(
            method=f"{owner}.GetNameList",
            signature="GetNameList() -> (NumberNames, Names, ret)",
            arguments={},
            invoke=provider,
            decode=lambda raw: _decode_outputs(f"{owner}.GetNameList", raw, 2),
        )
        count = _decode_scalar_int(f"{owner}.GetNameList", outputs[0])
        raw_names = outputs[1]
        if count < 0 or not isinstance(raw_names, (list, tuple)):
            raise RuntimeError(f"{owner}.GetNameList returned invalid names")
        names = tuple(
            _decode_scalar_string(f"{owner}.GetNameList", item) for item in raw_names
        )
        if len(names) != count or len(names) != len(set(names)):
            raise RuntimeError(f"{owner}.GetNameList returned inconsistent names")
        return names

    def read_session_identity(
        self,
        process_instance: ETABSProcessInstanceV1,
        observed_at_utc: datetime,
    ) -> ETABSSessionIdentityV1:
        if process_instance.instance_sha256 != self._process.instance_sha256:
            raise RuntimeError("ETABS_READER_PROCESS_BINDING_MISMATCH")
        model_path = self._call(
            method="SapModel.GetModelFilename",
            signature="GetModelFilename(IncludePath=True) -> str",
            arguments={"include_path": True},
            invoke=lambda: self._sap_model.GetModelFilename(True),
            decode=lambda raw: _decode_scalar_string("SapModel.GetModelFilename", raw),
        )
        version_outputs = self._call(
            method="SapModel.GetVersion",
            signature="GetVersion() -> (Version, MyVersionNumber, ret)",
            arguments={},
            invoke=self._sap_model.GetVersion,
            decode=lambda raw: _decode_outputs("SapModel.GetVersion", raw, 2),
        )
        version = _decode_scalar_string("SapModel.GetVersion", version_outputs[0])
        try:
            float(version_outputs[1])
        except (TypeError, ValueError) as exc:
            raise RuntimeError(
                "SapModel.GetVersion returned an invalid number"
            ) from exc
        units = self.get_present_units()
        locked = self.get_model_locked()
        saved_file = file_identity_v1(model_path)
        return build_etabs_session_identity_v1(
            process_instance=process_instance,
            connection_origin="ATTACHED_EXISTING",
            model_name=Path(model_path).name,
            model_path=saved_file.canonical_path,
            etabs_version=version,
            present_units=units,
            model_locked=locked,
            saved_file_identity=saved_file,
            observed_at_utc=observed_at_utc,
        )

    def get_present_units(self) -> str:
        value = self._call(
            method="SapModel.GetPresentUnits",
            signature="GetPresentUnits() -> eUnits",
            arguments={},
            invoke=self._sap_model.GetPresentUnits,
            decode=lambda raw: _decode_scalar_int("SapModel.GetPresentUnits", raw),
        )
        if value <= 0:
            raise RuntimeError("SapModel.GetPresentUnits returned an invalid enum")
        return f"eUnits:{value}"

    def get_model_locked(self) -> bool:
        value = self._call(
            method="SapModel.GetModelIsLocked",
            signature="GetModelIsLocked() -> bool",
            arguments={},
            invoke=self._sap_model.GetModelIsLocked,
            decode=lambda raw: _decode_scalar_bool("SapModel.GetModelIsLocked", raw),
        )
        return _decode_scalar_bool("SapModel.GetModelIsLocked", value)

    def get_selected_output_cases(self) -> Sequence[str]:
        names = self._name_list("LoadCases", self._sap_model.LoadCases.GetNameList)
        selected: list[str] = []
        for name in names:
            (value,) = self._call(
                method="Results.Setup.GetCaseSelectedForOutput",
                signature="GetCaseSelectedForOutput(Name) -> (Selected, ret)",
                arguments={"name": name},
                invoke=partial(
                    self._sap_model.Results.Setup.GetCaseSelectedForOutput,
                    name,
                ),
                decode=lambda raw: _decode_outputs(
                    "Results.Setup.GetCaseSelectedForOutput",
                    raw,
                    1,
                ),
            )
            if _decode_scalar_bool("GetCaseSelectedForOutput", value):
                selected.append(name)
        return tuple(selected)

    def get_selected_output_combinations(self) -> Sequence[str]:
        names = self._name_list("RespCombo", self._sap_model.RespCombo.GetNameList)
        selected: list[str] = []
        for name in names:
            (value,) = self._call(
                method="Results.Setup.GetComboSelectedForOutput",
                signature="GetComboSelectedForOutput(Name) -> (Selected, ret)",
                arguments={"name": name},
                invoke=partial(
                    self._sap_model.Results.Setup.GetComboSelectedForOutput,
                    name,
                ),
                decode=lambda raw: _decode_outputs(
                    "Results.Setup.GetComboSelectedForOutput",
                    raw,
                    1,
                ),
            )
            if _decode_scalar_bool("GetComboSelectedForOutput", value):
                selected.append(name)
        return tuple(selected)

    def get_case_statuses(self) -> Mapping[str, str]:
        count, raw_names, raw_statuses = self._call(
            method="Analyze.GetCaseStatus",
            signature="GetCaseStatus() -> (NumberItems, CaseNames, Statuses, ret)",
            arguments={},
            invoke=self._sap_model.Analyze.GetCaseStatus,
            decode=lambda raw: _decode_outputs("Analyze.GetCaseStatus", raw, 3),
        )
        number = _decode_scalar_int("Analyze.GetCaseStatus", count)
        if (
            number < 0
            or not isinstance(raw_names, (list, tuple))
            or not isinstance(raw_statuses, (list, tuple))
            or len(raw_names) != number
            or len(raw_statuses) != number
        ):
            raise RuntimeError("Analyze.GetCaseStatus returned inconsistent arrays")
        result: dict[str, str] = {}
        for raw_name, raw_status in zip(raw_names, raw_statuses, strict=True):
            name = _decode_scalar_string("Analyze.GetCaseStatus", raw_name)
            status = _decode_scalar_int("Analyze.GetCaseStatus", raw_status)
            if name in result:
                raise RuntimeError("Analyze.GetCaseStatus returned duplicate names")
            result[name] = "FINISHED" if status == 4 else f"RAW_STATUS:{status}"
        return result

    def get_run_flags(self) -> Mapping[str, bool]:
        count, raw_names, raw_flags = self._call(
            method="Analyze.GetRunCaseFlag",
            signature="GetRunCaseFlag() -> (NumberItems, CaseNames, Run, ret)",
            arguments={},
            invoke=self._sap_model.Analyze.GetRunCaseFlag,
            decode=lambda raw: _decode_outputs("Analyze.GetRunCaseFlag", raw, 3),
        )
        number = _decode_scalar_int("Analyze.GetRunCaseFlag", count)
        if (
            number < 0
            or not isinstance(raw_names, (list, tuple))
            or not isinstance(raw_flags, (list, tuple))
            or len(raw_names) != number
            or len(raw_flags) != number
        ):
            raise RuntimeError("Analyze.GetRunCaseFlag returned inconsistent arrays")
        result: dict[str, bool] = {}
        for raw_name, raw_flag in zip(raw_names, raw_flags, strict=True):
            name = _decode_scalar_string("Analyze.GetRunCaseFlag", raw_name)
            if name in result:
                raise RuntimeError("Analyze.GetRunCaseFlag returned duplicate names")
            result[name] = _decode_scalar_bool("Analyze.GetRunCaseFlag", raw_flag)
        return result

    def get_table_display_selection_sha256(self) -> str | None:
        return None


def _installed_readonly_worker(
    preflight_payload: Mapping[str, object],
    transaction_id: str,
    ledger_path: str,
    storage_identity: str,
    required_cases: tuple[str, ...],
    required_combinations: tuple[str, ...],
) -> dict[str, object]:
    preflight = ETABSInstalledReadOnlyPreflightV1.model_validate(preflight_payload)
    process = preflight.selected_process
    runtime = preflight.runtime_fingerprint
    if process is None or runtime is None:
        raise RuntimeError("ETABS_INSTALLED_READONLY_PREFLIGHT_INCOMPLETE")
    pre_attach = datetime.now(UTC)
    if (
        pre_attach < preflight.observed_at_utc
        or pre_attach - preflight.observed_at_utc > timedelta(seconds=15)
    ):
        raise RuntimeError("ETABS_INSTALLED_READONLY_PREFLIGHT_STALE")
    current_process = _current_exact_process(
        process,
        process_provider=None,
        observed_at_utc=pre_attach,
    )
    current_runtime = _rebuild_runtime(runtime, current_process, pre_attach)
    if current_runtime.fingerprint_sha256 != runtime.fingerprint_sha256:
        raise RuntimeError("ETABS_RUNTIME_FINGERPRINT_DRIFT")
    ledger = ETABSCallLedgerV1(
        ledger_path,
        transaction_id=transaction_id,
        storage_identity=storage_identity,
        redaction_policy="exact-pid-and-names-no-model-data-v1",
    )
    try:
        reader = _ETABSPIDGetterOnlyReader(process, ledger)
        capture = capture_etabs_installed_readonly_v1(
            preflight,
            reader,
            required_cases=required_cases,
            required_combinations=required_combinations,
        )
        ledger_identity = ledger.close()
    except BaseException:
        ledger.abandon()
        raise
    return {
        "capture": capture.model_dump(mode="json"),
        "call_ledger": ledger_identity.model_dump(mode="json"),
    }


def _build_run(
    *,
    disposition: Literal["COMPLETED", "HOLD", "RESTORATION_UNVERIFIED"],
    preflight: ETABSInstalledReadOnlyPreflightV1,
    broker_result: ETABSBrokerResultV1,
    operation_outcome: ETABSOperationOutcomeV1,
    capture: ETABSInstalledReadOnlyCaptureV1 | None,
    lease_receipt: ETABSOperationLeaseV1,
) -> ETABSInstalledReadOnlyRunV1:
    basis = {
        "schema_version": "etabs-installed-readonly-run/v1",
        "disposition": disposition,
        "preflight": preflight.model_dump(mode="json"),
        "broker_result": broker_result.model_dump(mode="json"),
        "operation_outcome": operation_outcome.model_dump(mode="json"),
        "capture": capture.model_dump(mode="json") if capture is not None else None,
        "lease_receipt": lease_receipt.model_dump(mode="json"),
    }
    return ETABSInstalledReadOnlyRunV1.model_validate(
        {
            **basis,
            "preflight": preflight,
            "broker_result": broker_result,
            "operation_outcome": operation_outcome,
            "capture": capture,
            "lease_receipt": lease_receipt,
            "run_sha256": _digest(basis),
        }
    )


def run_etabs_installed_readonly_v1(
    preflight: ETABSInstalledReadOnlyPreflightV1,
    /,
    *,
    transaction_id: str,
    evidence_directory: str | Path,
    lease_directory: str | Path,
    required_cases: Sequence[str] = (),
    required_combinations: Sequence[str] = (),
    deadline_seconds: float = 90.0,
) -> ETABSInstalledReadOnlyRunV1:
    """Run one supervised PID-specific getter-only observation."""

    if preflight.disposition != "READY_FOR_GETTER_ONLY_ATTACH":
        raise RuntimeError("ETABS_INSTALLED_READONLY_PREFLIGHT_HOLD")
    process = preflight.selected_process
    if process is None:
        raise RuntimeError("ETABS_INSTALLED_READONLY_PREFLIGHT_INCOMPLETE")
    if not 0.05 <= deadline_seconds <= 300:
        raise ValueError("deadline_seconds must be within [0.05, 300]")
    evidence_root = Path(evidence_directory).resolve(strict=False)
    evidence_root.mkdir(parents=True, exist_ok=True)
    if not evidence_root.is_dir():
        raise ValueError("evidence_directory must be a directory")
    transaction_key = hashlib.sha256(transaction_id.encode("utf-8")).hexdigest()
    ledger_path = evidence_root / f"etabs-a1-{transaction_key}.calls.jsonl"
    lease = acquire_etabs_operation_lease_v1(
        process,
        transaction_id,
        lease_directory=lease_directory,
    )
    capture: ETABSInstalledReadOnlyCaptureV1 | None = None
    ledger_identity: ETABSCallLedgerIdentityV1 | None = None
    broker: ETABSBrokerResultV1
    try:
        broker = run_etabs_sta_broker_v1(
            _installed_readonly_worker,
            args=(
                preflight.model_dump(mode="json"),
                transaction_id,
                str(ledger_path),
                str(evidence_root),
                tuple(required_cases),
                tuple(required_combinations),
            ),
            deadline_seconds=deadline_seconds,
            lease=lease,
            initialize_com=True,
        )
        if broker.status == "COMPLETED":
            if not isinstance(broker.payload, Mapping):
                raise RuntimeError("ETABS_INSTALLED_READONLY_BROKER_PAYLOAD_INVALID")
            capture = ETABSInstalledReadOnlyCaptureV1.model_validate(
                broker.payload.get("capture")
            )
            ledger_identity = ETABSCallLedgerIdentityV1.model_validate(
                broker.payload.get("call_ledger")
            )
            verified_ledger = verify_etabs_call_ledger_v1(
                ledger_path,
                transaction_id=transaction_id,
                storage_identity=str(evidence_root),
                redaction_policy="exact-pid-and-names-no-model-data-v1",
            )
            if verified_ledger != ledger_identity:
                raise RuntimeError("ETABS_INSTALLED_READONLY_LEDGER_IDENTITY_MISMATCH")
    finally:
        if lease.lease.disposition == "ACTIVE":
            lease_receipt = lease.release()
        else:
            lease_receipt = lease.lease

    if capture is not None and ledger_identity is not None:
        state_content = capture.state_content_sha256
        primary: Literal["COMPLETED", "ERROR", "TIMED_OUT"] = "COMPLETED"
        restoration: Literal["VERIFIED_EQUAL", "NOT_ATTEMPTED"] = "VERIFIED_EQUAL"
    else:
        state_content = None
        primary = "TIMED_OUT" if broker.status == "TIMED_OUT" else "ERROR"
        restoration = "NOT_ATTEMPTED"
    operation_outcome = build_etabs_operation_outcome_v1(
        broker_result=broker,
        access_mode="ATTACHED_OBSERVE",
        primary_outcome=primary,
        restoration_outcome=restoration,
        deadline_seconds=deadline_seconds,
        call_ledger=ledger_identity,
        pre_state_sha256=state_content,
        post_state_sha256=state_content,
        fence_reason=lease_receipt.fence_reason,
    )
    disposition: Literal["COMPLETED", "HOLD", "RESTORATION_UNVERIFIED"]
    if operation_outcome.disposition == "COMPLETED":
        disposition = "COMPLETED"
    elif operation_outcome.disposition == "BLOCKED":
        disposition = "HOLD"
    else:
        disposition = "RESTORATION_UNVERIFIED"
    return _build_run(
        disposition=disposition,
        preflight=preflight,
        broker_result=broker,
        operation_outcome=operation_outcome,
        capture=capture,
        lease_receipt=lease_receipt,
    )
