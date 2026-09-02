# SPDX-License-Identifier: MIT
"""Offline acceptance for the PID-specific installed read-only transport."""

# ruff: noqa: N802 - fakes intentionally mirror the installed COM method names.

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from structural_lib.services import etabs_installed_readonly as installed_readonly
from structural_lib.services.etabs_installed_readonly import (
    _ETABSPIDGetterOnlyReader,
    _installed_readonly_worker_payload,
    capture_etabs_installed_readonly_v1,
)
from structural_lib.services.etabs_operation_control import (
    ETABSCallLedgerIdentityV1,
    ETABSCallLedgerV1,
)
from structural_lib.services.etabs_session_guard import (
    ETABSAccessModeV1,
    ETABSExpectedModelIntentV1,
    ETABSInstalledReadOnlyPreflightV1,
    ProcessObservationV1,
    preflight_installed_etabs_readonly_v1,
)

T0 = datetime(2026, 9, 2, 4, 0, tzinfo=UTC)
T1 = T0 + timedelta(seconds=30)


class _FakeSetup:
    def GetCaseSelectedForOutput(self, name: str):
        return [name == "DL", 0]

    def GetComboSelectedForOutput(self, name: str):
        return [name == "ULS", 0]


class _FakeResults:
    def __init__(self) -> None:
        self.Setup = _FakeSetup()


class _FakeLoadCases:
    def GetNameList(self):
        return [1, ("DL",), 0]


class _FakeRespCombo:
    def GetNameList(self):
        return [1, ("ULS",), 0]


class _FakeAnalyze:
    def GetCaseStatus(self):
        return [2, ("DL", "ULS"), (4, 4), 0]

    def GetRunCaseFlag(self):
        return [1, ("DL",), (True,), 0]


class _FakeSapModel:
    def __init__(self, model_path: Path) -> None:
        self._model_path = model_path
        self.LoadCases = _FakeLoadCases()
        self.RespCombo = _FakeRespCombo()
        self.Analyze = _FakeAnalyze()
        self.Results = _FakeResults()

    def GetModelFilename(self, include_path: bool):
        assert include_path is True
        return str(self._model_path.resolve())

    def GetVersion(self):
        return ["23.3.1", 23.3, 0]

    def GetPresentUnits(self):
        return 6

    def GetModelIsLocked(self):
        return True


class _FakeETABSObject:
    def __init__(self, sap_model: _FakeSapModel) -> None:
        self.SapModel = sap_model


class _FakeHelper:
    def __init__(self, sap_model: _FakeSapModel) -> None:
        self._sap_model = sap_model
        self.calls: list[tuple[str, int]] = []

    def GetObjectProcess(self, type_name: str, pid: int):
        self.calls.append((type_name, pid))
        return _FakeETABSObject(self._sap_model)


class _FakeCOMClient:
    def __init__(self, helper: _FakeHelper) -> None:
        self._helper = helper
        self.prog_ids: list[str] = []

    def CreateObject(self, prog_id: str):
        self.prog_ids.append(prog_id)
        return self._helper


def _ready_preflight(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    executable = tmp_path / "ETABS.exe"
    executable.write_bytes(b"offline executable")
    model = tmp_path / "selected.edb"
    model.write_bytes(b"offline saved model")
    type_library = tmp_path / "ETABSv1.tlb"
    type_library.write_bytes(b"offline type library")
    wrapper = tmp_path / "ETABSv1_wrapper.py"
    wrapper.write_bytes(b"offline generated wrapper")
    installed_chm = tmp_path / "ETABS.chm"
    installed_chm.write_bytes(b"offline installed help")
    start = T0 - timedelta(hours=1)

    def provider():
        return (
            ProcessObservationV1(
                pid=7300,
                start_time_utc=start,
                executable_path=str(executable),
                executable_version="23.3.1.4563",
                architecture="x86_64",
            ),
        )

    monkeypatch.setattr(
        "structural_lib.services.etabs_session_guard.importlib.metadata.version",
        lambda _name: "1.4.16",
    )
    preflight = preflight_installed_etabs_readonly_v1(
        ETABSExpectedModelIntentV1(
            expected_model_path=str(model.resolve()),
            expected_model_name=model.name,
            expected_etabs_version="23.3.1",
            allowed_access=ETABSAccessModeV1.ATTACHED_OBSERVE,
        ),
        selected_pid=7300,
        selected_start_time_utc=start,
        type_library_path=type_library,
        generated_wrapper_path=wrapper,
        installed_chm_path=installed_chm,
        process_provider=provider,
        observed_at_utc=T0,
    )
    return preflight, model, provider


def test_pid_reader_captures_equal_state_with_only_reviewed_getters(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    preflight, model, provider = _ready_preflight(tmp_path, monkeypatch)
    helper = _FakeHelper(_FakeSapModel(model))
    client = _FakeCOMClient(helper)
    ledger_path = tmp_path / "calls.jsonl"
    ledger = ETABSCallLedgerV1(
        ledger_path,
        transaction_id="TX-A1-FAKE",
        storage_identity="offline-test",
        redaction_policy="exact-pid-and-names-no-model-data-v1",
    )
    reader = _ETABSPIDGetterOnlyReader(
        preflight.selected_process,
        ledger,
        com_client=client,
    )

    capture = capture_etabs_installed_readonly_v1(
        preflight,
        reader,
        required_cases=("DL",),
        required_combinations=("ULS",),
        process_provider=provider,
        observed_at_utc=T0,
        verified_at_utc=T1,
    )
    ledger_identity = ledger.close()
    worker_payload = _installed_readonly_worker_payload(capture, ledger_identity)

    assert client.prog_ids == ["ETABSv1.Helper"]
    assert helper.calls == [("CSI.ETABS.API.ETABSObject", 7300)]
    assert capture.output_readiness == "READY"
    assert capture.comparison_basis_allowed is False
    assert capture.state_before.state_sha256 != capture.state_after.state_sha256
    assert capture.state_content_sha256
    assert ledger_identity.record_count > 2
    methods = {
        json.loads(line)["method"]
        for line in ledger_path.read_text(encoding="utf-8").splitlines()
    }
    assert methods == {
        "Analyze.GetCaseStatus",
        "Analyze.GetRunCaseFlag",
        "LoadCases.GetNameList",
        "RespCombo.GetNameList",
        "Results.Setup.GetCaseSelectedForOutput",
        "Results.Setup.GetComboSelectedForOutput",
        "SapModel.GetModelFilename",
        "SapModel.GetModelIsLocked",
        "SapModel.GetPresentUnits",
        "SapModel.GetVersion",
        "cHelper.GetObjectProcess",
    }
    method_names = {method.rsplit(".", 1)[-1] for method in methods}
    assert all(name.startswith("Get") for name in method_names)
    assert type(capture).model_validate(worker_payload["capture"]) == capture
    assert (
        ETABSCallLedgerIdentityV1.model_validate(worker_payload["call_ledger"])
        == ledger_identity
    )


def test_installed_capture_detects_state_drift(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    preflight, model, provider = _ready_preflight(tmp_path, monkeypatch)
    sap_model = _FakeSapModel(model)
    unit_values = iter((6, 6, 7, 6))
    sap_model.GetPresentUnits = lambda: next(unit_values)
    helper = _FakeHelper(sap_model)
    ledger = ETABSCallLedgerV1(
        tmp_path / "drift-calls.jsonl",
        transaction_id="TX-A1-DRIFT",
        storage_identity="offline-test",
        redaction_policy="exact-pid-and-names-no-model-data-v1",
    )
    reader = _ETABSPIDGetterOnlyReader(
        preflight.selected_process,
        ledger,
        com_client=_FakeCOMClient(helper),
    )

    with pytest.raises(RuntimeError, match="ATTACHED_STATE_CHANGED"):
        capture_etabs_installed_readonly_v1(
            preflight,
            reader,
            process_provider=provider,
            observed_at_utc=T0,
            verified_at_utc=T1,
        )
    ledger.close()


def test_installed_capture_refuses_held_preflight_before_evidence_write(
    tmp_path: Path,
) -> None:
    preflight = preflight_installed_etabs_readonly_v1(
        ETABSExpectedModelIntentV1(
            allowed_access=ETABSAccessModeV1.ATTACHED_OBSERVE,
        ),
        selected_pid=None,
        selected_start_time_utc=None,
        process_provider=lambda: (),
        observed_at_utc=T0,
    )

    with pytest.raises(RuntimeError, match="PREFLIGHT_HOLD"):
        capture_etabs_installed_readonly_v1(preflight, object())


def test_supervised_run_sends_python_native_preflight_to_spawned_worker(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    preflight, _model, _provider = _ready_preflight(tmp_path, monkeypatch)
    received: list[ETABSInstalledReadOnlyPreflightV1] = []

    def broker_sentinel(_operation, *, args, **_kwargs):
        received.append(ETABSInstalledReadOnlyPreflightV1.model_validate(args[0]))
        raise RuntimeError("BROKER_SENTINEL")

    monkeypatch.setattr(
        installed_readonly,
        "run_etabs_sta_broker_v1",
        broker_sentinel,
    )

    with pytest.raises(RuntimeError, match="BROKER_SENTINEL"):
        installed_readonly.run_etabs_installed_readonly_v1(
            preflight,
            transaction_id="TX-A1-SPAWN-PAYLOAD",
            evidence_directory=tmp_path / "evidence",
            lease_directory=tmp_path / "leases",
        )

    assert received == [preflight]
