# SPDX-License-Identifier: MIT
"""Offline acceptance for the ETABS process/runtime/target guard."""

from __future__ import annotations

import builtins
import hashlib
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from structural_lib.services.etabs_session_guard import (
    ETABSAccessModeV1,
    ETABSExpectedModelIntentV1,
    ETABSModelFreshnessDispositionV1,
    ETABSResultEpochDispositionV1,
    ETABSRuntimeFingerprintV1,
    ProcessObservationV1,
    assess_attached_output_readiness_v1,
    build_etabs_result_epoch_v1,
    build_etabs_runtime_fingerprint_v1,
    build_etabs_saved_checkpoint_v1,
    build_etabs_session_identity_v1,
    capture_attached_etabs_state_v1,
    capture_etabs_state_v1,
    classify_etabs_model_freshness_v1,
    compare_attached_etabs_state_v1,
    discover_etabs_processes_v1,
    file_identity_v1,
    issue_etabs_bridge_capability_v1,
    observe_etabs_target_v1,
    preflight_installed_etabs_readonly_v1,
    verify_etabs_bridge_capability_v1,
    verify_etabs_target_observation_v1,
)

T0 = datetime(2026, 9, 1, 12, 0, tzinfo=UTC)
T1 = T0 + timedelta(minutes=1)
HASH_A = "a" * 64
HASH_B = "b" * 64


class _GetterOnlyStateFake:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def _return(self, name: str, value):
        self.calls.append(name)
        return value

    def get_present_units(self) -> str:
        return self._return("get_present_units", "kN_mm_C")

    def get_model_locked(self) -> bool:
        return self._return("get_model_locked", True)

    def get_selected_output_cases(self):
        return self._return("get_selected_output_cases", ("DL", "LL"))

    def get_selected_output_combinations(self):
        return self._return("get_selected_output_combinations", ("ULS",))

    def get_case_statuses(self):
        return self._return(
            "get_case_statuses",
            {"DL": "FINISHED", "LL": "FINISHED", "ULS": "FINISHED"},
        )

    def get_run_flags(self):
        return self._return("get_run_flags", {"DL": True, "LL": True})

    def get_table_display_selection_sha256(self):
        return self._return("get_table_display_selection_sha256", HASH_A)


def _write(path: Path, content: bytes) -> Path:
    path.write_bytes(content)
    timestamp = (T0 - timedelta(minutes=5)).timestamp()
    os.utime(path, (timestamp, timestamp))
    return path


def _process_provider(executable: Path, *, pid: int = 4100):
    return lambda: (
        ProcessObservationV1(
            pid=pid,
            start_time_utc=T0 - timedelta(hours=1),
            executable_path=str(executable),
            executable_version="22.7.0",
            architecture="x86_64",
        ),
    )


def _process(executable: Path, *, observed: datetime = T0, pid: int = 4100):
    return discover_etabs_processes_v1(
        process_provider=_process_provider(executable, pid=pid),
        observed_at_utc=observed,
    )[0]


def _runtime(
    executable: Path,
    *,
    observed: datetime = T0,
    pid: int = 4100,
) -> ETABSRuntimeFingerprintV1:
    process = _process(executable, observed=observed, pid=pid)
    return build_etabs_runtime_fingerprint_v1(
        process,
        com_shape_runtime="unavailable",
        observed_at_utc=observed,
    )


def _target(tmp_path: Path):
    executable = _write(tmp_path / "ETABS.exe", b"offline fake executable")
    model_path = _write(tmp_path / "building.edb", b"offline fake model")
    process = _process(executable)
    runtime = _runtime(executable)
    saved_file = file_identity_v1(model_path)
    session = build_etabs_session_identity_v1(
        process_instance=process,
        connection_origin="ATTACHED_EXISTING",
        model_name=model_path.name,
        model_path=str(model_path.resolve()),
        etabs_version="22.7.0",
        present_units="kN_mm_C",
        model_locked=True,
        saved_file_identity=saved_file,
        observed_at_utc=T0,
    )
    freshness = classify_etabs_model_freshness_v1(
        session_identity=session,
        before_file=saved_file,
        after_file=saved_file,
        observed_at_utc=T0,
        attached_session=True,
    )
    intent = ETABSExpectedModelIntentV1(
        expected_model_path=str(model_path.resolve()),
        expected_model_name=model_path.name,
        expected_etabs_version="22.7.0",
        allowed_access=ETABSAccessModeV1.ATTACHED_OBSERVE,
    )
    target = observe_etabs_target_v1(
        process,
        intent,
        runtime,
        session,
        freshness,
        observed_at_utc=T0,
        ttl=timedelta(minutes=2),
        observation_id="OBS-BUILDING-1",
    )
    return executable, model_path, process, runtime, session, target


def test_process_discovery_is_deterministic_and_observation_time_is_not_identity(
    tmp_path: Path,
) -> None:
    executable = _write(tmp_path / "ETABS.exe", b"offline fake executable")

    first = _process(executable, observed=T0)
    second = _process(executable, observed=T1)

    assert first.observed_at_utc != second.observed_at_utc
    assert first.instance_sha256 == second.instance_sha256
    assert (
        first.executable_sha256 == hashlib.sha256(executable.read_bytes()).hexdigest()
    )


def test_process_discovery_rejects_duplicate_pid_and_start_time(tmp_path: Path) -> None:
    executable = _write(tmp_path / "ETABS.exe", b"offline fake executable")
    row = _process_provider(executable)()[0]

    with pytest.raises(ValueError, match="duplicate PID/start time"):
        discover_etabs_processes_v1(
            process_provider=lambda: (row, row),
            observed_at_utc=T0,
        )


def test_installed_readonly_preflight_holds_before_com_without_exact_target() -> None:
    intent = ETABSExpectedModelIntentV1(
        allowed_access=ETABSAccessModeV1.ATTACHED_OBSERVE,
    )

    result = preflight_installed_etabs_readonly_v1(
        intent,
        selected_pid=None,
        selected_start_time_utc=None,
        process_provider=lambda: (),
        observed_at_utc=T0,
    )

    assert result.disposition == "HOLD"
    assert result.selected_process is None
    assert result.runtime_fingerprint is None
    assert set(result.blocked_reasons) == {
        "EXACT_PROCESS_SELECTION_MISSING",
        "EXPECTED_ETABS_VERSION_MISSING",
        "EXPECTED_MODEL_NAME_MISSING",
        "EXPECTED_MODEL_PATH_MISSING",
        "NO_ETABS_PROCESS_RUNNING",
    }


def test_installed_readonly_preflight_binds_exact_process_runtime_and_model(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    executable = _write(tmp_path / "ETABS.exe", b"offline fake executable")
    model = _write(tmp_path / "selected.edb", b"offline fake model")
    type_library = _write(tmp_path / "ETABSv1.tlb", b"offline fake typelib")
    wrapper = _write(tmp_path / "ETABSv1.py", b"offline fake wrapper")
    installed_chm = _write(tmp_path / "ETABS.chm", b"offline fake help")
    start = T0 - timedelta(hours=1)
    monkeypatch.setattr(
        "structural_lib.services.etabs_session_guard.importlib.metadata.version",
        lambda _name: "1.4.16",
    )
    intent = ETABSExpectedModelIntentV1(
        expected_model_path=str(model.resolve()),
        expected_model_name=model.name,
        expected_etabs_version="23.3.1",
        allowed_access=ETABSAccessModeV1.ATTACHED_OBSERVE,
    )

    result = preflight_installed_etabs_readonly_v1(
        intent,
        selected_pid=4100,
        selected_start_time_utc=start,
        type_library_path=type_library,
        generated_wrapper_path=wrapper,
        installed_chm_path=installed_chm,
        process_provider=lambda: (
            ProcessObservationV1(
                pid=4100,
                start_time_utc=start,
                executable_path=str(executable),
                executable_version="23.3.1.4563",
                architecture="x86_64",
            ),
        ),
        observed_at_utc=T0,
    )

    assert result.disposition == "READY_FOR_GETTER_ONLY_ATTACH"
    assert result.blocked_reasons == ()
    assert result.selected_process is not None
    assert result.runtime_fingerprint is not None
    assert result.runtime_fingerprint.process_instance_sha256 == (
        result.selected_process.instance_sha256
    )
    assert result.runtime_fingerprint.com_shape_runtime == "comtypes"


def test_installed_readonly_preflight_rejects_pid_reuse_without_runtime_probe(
    tmp_path: Path,
) -> None:
    executable = _write(tmp_path / "ETABS.exe", b"offline fake executable")
    model = _write(tmp_path / "selected.edb", b"offline fake model")
    current_start = T0 - timedelta(minutes=30)
    intent = ETABSExpectedModelIntentV1(
        expected_model_path=str(model.resolve()),
        expected_model_name=model.name,
        expected_etabs_version="23.3.1",
        allowed_access=ETABSAccessModeV1.ATTACHED_OBSERVE,
    )

    result = preflight_installed_etabs_readonly_v1(
        intent,
        selected_pid=4100,
        selected_start_time_utc=current_start - timedelta(hours=1),
        process_provider=lambda: (
            ProcessObservationV1(
                pid=4100,
                start_time_utc=current_start,
                executable_path=str(executable),
                executable_version="23.3.1.4563",
                architecture="x86_64",
            ),
        ),
        observed_at_utc=T0,
    )

    assert result.disposition == "HOLD"
    assert result.blocked_reasons == ("SELECTED_PROCESS_START_TIME_MISMATCH",)
    assert result.selected_process is None
    assert result.runtime_fingerprint is None


def test_runtime_fingerprint_is_measured_and_stable_across_reobservation(
    tmp_path: Path,
) -> None:
    executable = _write(tmp_path / "ETABS.exe", b"offline fake executable")
    chm = _write(tmp_path / "CSI API ETABS v1.chm", b"offline help identity")
    process_first = _process(executable, observed=T0)
    process_second = _process(executable, observed=T1)

    first = build_etabs_runtime_fingerprint_v1(
        process_first,
        installed_chm_path=chm,
        com_shape_runtime="unavailable",
        observed_at_utc=T0,
    )
    second = build_etabs_runtime_fingerprint_v1(
        process_second,
        installed_chm_path=chm,
        com_shape_runtime="unavailable",
        observed_at_utc=T1,
    )

    assert first.fingerprint_sha256 == second.fingerprint_sha256
    installed_help = next(
        item for item in first.artifacts if item.name == "INSTALLED_CHM"
    )
    assert installed_help.disposition == "PRESENT"
    assert installed_help.sha256 == hashlib.sha256(chm.read_bytes()).hexdigest()


def test_attached_session_defaults_to_unknown_even_when_file_is_stable(
    tmp_path: Path,
) -> None:
    _exe, _model, _process_value, _runtime_value, _session, target = _target(tmp_path)
    freshness = target.model_freshness

    assert freshness.disposition is (
        ETABSModelFreshnessDispositionV1.SESSION_UNSAVED_OR_UNKNOWN
    )
    assert freshness.hash_bound_baseline_allowed is False


def test_saved_checkpoint_can_confirm_clean_but_file_drift_blocks_it(
    tmp_path: Path,
) -> None:
    _exe, model, process, _runtime_value, session, _target_value = _target(tmp_path)
    before = file_identity_v1(model)
    checkpoint = build_etabs_saved_checkpoint_v1(
        process_instance=process,
        session_identity=session,
        file_identity=before,
        save_call_id="CALL-SAVE-1",
        saved_at_utc=T0 - timedelta(seconds=2),
        observed_at_utc=T0 - timedelta(seconds=1),
    )
    clean = classify_etabs_model_freshness_v1(
        session_identity=session,
        before_file=before,
        after_file=before,
        observed_at_utc=T0,
        attached_session=True,
        saved_checkpoint=checkpoint,
    )
    model.write_bytes(b"changed saved model")
    changed_timestamp = (T0 + timedelta(seconds=30)).timestamp()
    os.utime(model, (changed_timestamp, changed_timestamp))
    after = file_identity_v1(model)
    drift = classify_etabs_model_freshness_v1(
        session_identity=session,
        before_file=before,
        after_file=after,
        observed_at_utc=T1,
        attached_session=True,
        saved_checkpoint=checkpoint,
    )

    assert clean.disposition is ETABSModelFreshnessDispositionV1.SAVED_CLEAN_CONFIRMED
    assert clean.hash_bound_baseline_allowed is True
    assert drift.disposition is ETABSModelFreshnessDispositionV1.FILE_DRIFT
    assert drift.hash_bound_baseline_allowed is False


def test_target_revalidation_accepts_same_instance_and_rejects_pid_reuse(
    tmp_path: Path,
) -> None:
    executable, model_path, process, _runtime_value, _session, target = _target(
        tmp_path
    )
    current_at = T0 + timedelta(seconds=10)
    current_process = _process(executable, observed=current_at)
    current_runtime = _runtime(executable, observed=current_at)
    current_session = build_etabs_session_identity_v1(
        process_instance=current_process,
        connection_origin="ATTACHED_EXISTING",
        model_name=model_path.name,
        model_path=str(model_path.resolve()),
        etabs_version="22.7.0",
        present_units="kN_mm_C",
        model_locked=True,
        saved_file_identity=file_identity_v1(model_path),
        observed_at_utc=current_at,
    )

    verify_etabs_target_observation_v1(
        target,
        current_process=current_process,
        current_runtime=current_runtime,
        current_session=current_session,
        verified_at_utc=current_at,
    )

    reused_pid = _process(executable, observed=current_at, pid=process.pid + 1)
    with pytest.raises(RuntimeError, match="PROCESS_INSTANCE_DRIFT"):
        verify_etabs_target_observation_v1(
            target,
            current_process=reused_pid,
            current_runtime=current_runtime,
            current_session=current_session,
            verified_at_utc=current_at,
        )


def test_target_expiry_and_runtime_drift_fail_closed(tmp_path: Path) -> None:
    executable, _model_path, process, runtime, session, target = _target(tmp_path)
    with pytest.raises(RuntimeError, match="TARGET_OBSERVATION_EXPIRED"):
        verify_etabs_target_observation_v1(
            target,
            current_process=process,
            current_runtime=runtime,
            current_session=session,
            verified_at_utc=T0 + timedelta(minutes=3),
        )

    changed_runtime = runtime.model_copy(update={"fingerprint_sha256": "f" * 64})
    with pytest.raises(RuntimeError, match="RUNTIME_FINGERPRINT_DRIFT"):
        verify_etabs_target_observation_v1(
            target,
            current_process=process,
            current_runtime=changed_runtime,
            current_session=session,
            verified_at_utc=T0 + timedelta(seconds=10),
        )


def test_capability_is_signed_and_bound_to_target_access_and_transaction(
    tmp_path: Path,
) -> None:
    _executable, _model_path, _process_value, _runtime_value, _session, target = (
        _target(tmp_path)
    )
    signing_key = b"k" * 32
    capability = issue_etabs_bridge_capability_v1(
        target,
        transaction_id="TX-1",
        signing_key=signing_key,
        issued_at_utc=T0,
        ttl=timedelta(seconds=30),
        capability_id="CAP-1",
        nonce="0011223344556677",
    )

    verify_etabs_bridge_capability_v1(
        capability,
        target,
        transaction_id="TX-1",
        required_access=ETABSAccessModeV1.ATTACHED_OBSERVE,
        signing_key=signing_key,
        verified_at_utc=T0 + timedelta(seconds=5),
    )

    with pytest.raises(RuntimeError, match="TRANSACTION_MISMATCH"):
        verify_etabs_bridge_capability_v1(
            capability,
            target,
            transaction_id="TX-2",
            required_access=ETABSAccessModeV1.ATTACHED_OBSERVE,
            signing_key=signing_key,
            verified_at_utc=T0 + timedelta(seconds=5),
        )


def test_mutation_capability_requires_atomic_single_use_consumption(
    tmp_path: Path,
) -> None:
    executable, model_path, process, runtime, _attached_session, _target_value = (
        _target(tmp_path)
    )
    saved_file = file_identity_v1(model_path)
    owned_session = build_etabs_session_identity_v1(
        process_instance=process,
        connection_origin="STARTED_OWNED",
        model_name=model_path.name,
        model_path=str(model_path.resolve()),
        etabs_version="22.7.0",
        present_units="kN_mm_C",
        model_locked=True,
        saved_file_identity=saved_file,
        observed_at_utc=T0,
    )
    freshness = classify_etabs_model_freshness_v1(
        session_identity=owned_session,
        before_file=saved_file,
        after_file=saved_file,
        observed_at_utc=T0,
        attached_session=False,
        api_clean_signal_call_id="CALL-CLEAN-1",
    )
    intent = ETABSExpectedModelIntentV1(
        expected_model_path=str(model_path.resolve()),
        expected_model_name=model_path.name,
        expected_etabs_version="22.7.0",
        allowed_access=ETABSAccessModeV1.OWNED_COPY_MUTATION,
    )
    target = observe_etabs_target_v1(
        process,
        intent,
        runtime,
        owned_session,
        freshness,
        observed_at_utc=T0,
        observation_id="OBS-OWNED-1",
    )
    signing_key = b"m" * 32
    capability = issue_etabs_bridge_capability_v1(
        target,
        transaction_id="TX-MUTATE-1",
        signing_key=signing_key,
        issued_at_utc=T0,
        capability_id="CAP-MUTATE-1",
        nonce="8899aabbccddeeff",
    )
    used: set[str] = set()

    def consume_once(value, _used_at: datetime) -> None:
        if value.signature_sha256 in used:
            raise RuntimeError("ETABS_CAPABILITY_REPLAYED")
        used.add(value.signature_sha256)

    with pytest.raises(RuntimeError, match="SINGLE_USE_CONSUMER_REQUIRED"):
        verify_etabs_bridge_capability_v1(
            capability,
            target,
            transaction_id="TX-MUTATE-1",
            required_access=ETABSAccessModeV1.OWNED_COPY_MUTATION,
            signing_key=signing_key,
            verified_at_utc=T0 + timedelta(seconds=1),
        )
    verify_etabs_bridge_capability_v1(
        capability,
        target,
        transaction_id="TX-MUTATE-1",
        required_access=ETABSAccessModeV1.OWNED_COPY_MUTATION,
        signing_key=signing_key,
        verified_at_utc=T0 + timedelta(seconds=1),
        consume_single_use=consume_once,
    )
    with pytest.raises(RuntimeError, match="CAPABILITY_REPLAYED"):
        verify_etabs_bridge_capability_v1(
            capability,
            target,
            transaction_id="TX-MUTATE-1",
            required_access=ETABSAccessModeV1.OWNED_COPY_MUTATION,
            signing_key=signing_key,
            verified_at_utc=T0 + timedelta(seconds=2),
            consume_single_use=consume_once,
        )


def test_offline_guard_does_not_import_comtypes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_import = builtins.__import__

    def reject_comtypes(name: str, *args, **kwargs):
        if name == "comtypes" or name.startswith("comtypes."):
            raise AssertionError("offline guard imported comtypes")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", reject_comtypes)
    _target(tmp_path)


def test_attached_state_is_compared_without_restoration(tmp_path: Path) -> None:
    _executable, _model_path, _process_value, _runtime_value, session, _target_value = (
        _target(tmp_path)
    )
    before = capture_etabs_state_v1(
        session_sha256=session.session_sha256,
        present_units="kN_mm_C",
        model_locked=True,
        selected_output_cases=["DL", "LL", "DL"],
        selected_output_combinations=["ULS"],
        case_statuses={"DL": "FINISHED", "LL": "FINISHED"},
        run_flags={"DL": True, "LL": True},
        observed_at_utc=T0,
    )
    same = capture_etabs_state_v1(
        session_sha256=session.session_sha256,
        present_units="kN_mm_C",
        model_locked=True,
        selected_output_cases=["LL", "DL"],
        selected_output_combinations=["ULS"],
        case_statuses={"LL": "FINISHED", "DL": "FINISHED"},
        run_flags={"LL": True, "DL": True},
        observed_at_utc=T1,
    )
    drift = capture_etabs_state_v1(
        session_sha256=session.session_sha256,
        present_units="N_mm_C",
        model_locked=True,
        selected_output_cases=["DL", "LL"],
        selected_output_combinations=["ULS"],
        case_statuses={"DL": "FINISHED", "LL": "FINISHED"},
        run_flags={"DL": True, "LL": True},
        observed_at_utc=T1,
    )

    assert compare_attached_etabs_state_v1(before, same) == "COMPLETED"
    assert compare_attached_etabs_state_v1(before, drift) == ("RESTORATION_UNVERIFIED")


def test_attached_capture_uses_getters_only_and_holds_instead_of_selecting() -> None:
    fake = _GetterOnlyStateFake()

    snapshot = capture_attached_etabs_state_v1(
        fake,
        session_sha256=HASH_A,
        observed_at_utc=T0,
    )

    assert fake.calls == [
        "get_present_units",
        "get_model_locked",
        "get_selected_output_cases",
        "get_selected_output_combinations",
        "get_case_statuses",
        "get_run_flags",
        "get_table_display_selection_sha256",
    ]
    assert (
        assess_attached_output_readiness_v1(
            snapshot,
            required_cases=("DL",),
            required_combinations=("ULS",),
        )
        == "READY"
    )
    assert (
        assess_attached_output_readiness_v1(
            snapshot,
            required_combinations=("MISSING",),
        )
        == "HOLD"
    )


def test_result_epoch_requires_uninterrupted_runtime_and_case_closure(
    tmp_path: Path,
) -> None:
    executable = _write(tmp_path / "ETABS.exe", b"offline fake executable")
    process = _process(executable)
    runtime = _runtime(executable)
    accepted = build_etabs_result_epoch_v1(
        model_identity_sha256=HASH_A,
        runtime_fingerprint=runtime,
        process_instance=process,
        transaction_id="TX-RESULT-1",
        authorized_cases=["ULS"],
        case_dependency_closure=["DL", "LL", "ULS"],
        pre_statuses={"DL": "FINISHED", "LL": "FINISHED", "ULS": "NOT_RUN"},
        post_statuses={"DL": "FINISHED", "LL": "FINISHED", "ULS": "FINISHED"},
        run_flags={"DL": True, "LL": True, "ULS": True},
        analysis_call_ids=["CALL-ANALYSIS-1"],
        design_call_ids=[],
        selection_sha256=HASH_A,
        result_sha256=HASH_B,
        uninterrupted_process=True,
        uninterrupted_runtime=True,
        observed_at_utc=T0,
    )
    blocked = build_etabs_result_epoch_v1(
        model_identity_sha256=HASH_A,
        runtime_fingerprint=runtime,
        process_instance=process,
        transaction_id="TX-RESULT-2",
        authorized_cases=["ULS"],
        case_dependency_closure=["DL", "LL"],
        pre_statuses={"ULS": "FINISHED"},
        post_statuses={"ULS": "FINISHED"},
        run_flags={"ULS": True},
        analysis_call_ids=[],
        design_call_ids=[],
        selection_sha256=HASH_A,
        result_sha256=HASH_B,
        uninterrupted_process=False,
        uninterrupted_runtime=True,
        observed_at_utc=T0,
    )

    assert accepted.disposition is ETABSResultEpochDispositionV1.ACCEPTED
    assert blocked.disposition is ETABSResultEpochDispositionV1.BLOCKED
    assert "PROCESS_INTERRUPTED" in blocked.blocked_reasons
    assert "CASE_DEPENDENCY_CLOSURE_INCOMPLETE" in blocked.blocked_reasons
