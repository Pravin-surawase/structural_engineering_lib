# SPDX-License-Identifier: MIT
"""Offline acceptance for ETABS leases, brokers, and durable evidence."""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from structural_lib.services.etabs_operation_control import (
    ETABSBrokerResultV1,
    ETABSCallLedgerV1,
    acquire_etabs_operation_lease_v1,
    build_etabs_operation_outcome_v1,
    finalize_etabs_evidence_bundle_v1,
    invoke_recorded_etabs_call_v1,
    run_etabs_sta_broker_v1,
    verify_etabs_call_ledger_v1,
    verify_etabs_evidence_bundle_v1,
)
from structural_lib.services.etabs_session_guard import (
    ProcessObservationV1,
    discover_etabs_processes_v1,
)

T0 = datetime(2026, 9, 1, 12, 0, tzinfo=UTC)
HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64


def _broker_echo(value: str) -> dict[str, str]:
    return {"echo": value}


def _broker_hang(seconds: float) -> None:
    time.sleep(seconds)


def _broker_fail() -> None:
    raise RuntimeError("offline injected operation failure")


def _process(tmp_path: Path):
    executable = tmp_path / "ETABS.exe"
    executable.write_bytes(b"offline fake executable")
    return discover_etabs_processes_v1(
        process_provider=lambda: (
            ProcessObservationV1(
                pid=5100,
                start_time_utc=T0 - timedelta(hours=1),
                executable_path=str(executable),
                executable_version="22.7.0",
                architecture="x86_64",
            ),
        ),
        observed_at_utc=T0,
    )[0]


def _ledger(tmp_path: Path, name: str = "calls.jsonl") -> ETABSCallLedgerV1:
    return ETABSCallLedgerV1(
        tmp_path / name,
        transaction_id="TX-1",
        storage_identity="local-test-store",
        redaction_policy="arguments-redacted-v1",
    )


def _record_one_call(ledger: ETABSCallLedgerV1) -> None:
    result = invoke_recorded_etabs_call_v1(
        ledger,
        call_id="CALL-1",
        method="SapModel.Results.FrameForce",
        reviewed_signature="FrameForce(name, item_type) -> (..., ret)",
        redacted_arguments={"name_sha256": HASH_A},
        invoke=lambda: ("B1", [0.0, 1.0], 0),
        decode=lambda raw: raw[0],
        decoder_name="frame-force-v1",
    )
    assert result == "B1"


def test_lease_is_exclusive_monotonic_and_reacquirable_after_release(
    tmp_path: Path,
) -> None:
    process = _process(tmp_path)
    lease_directory = tmp_path / "leases"
    first = acquire_etabs_operation_lease_v1(
        process,
        "TX-1",
        lease_directory=lease_directory,
        acquired_at_utc=T0,
        duration=timedelta(minutes=5),
        lease_id="LEASE-1",
    )

    with pytest.raises(RuntimeError, match="LEASE_CONTENDED"):
        acquire_etabs_operation_lease_v1(
            process,
            "TX-2",
            lease_directory=lease_directory,
            acquired_at_utc=T0,
        )

    first.heartbeat(observed_at_utc=T0 + timedelta(seconds=1), worker_pid=1234)
    with pytest.raises(RuntimeError, match="HEARTBEAT_REGRESSION"):
        first.heartbeat(observed_at_utc=T0)
    receipt = first.release(released_at_utc=T0 + timedelta(seconds=2))

    assert receipt.disposition == "RELEASED"
    assert not first.path.exists()
    assert first.path.with_name("LEASE-1.released.json").is_file()
    second = acquire_etabs_operation_lease_v1(
        process,
        "TX-2",
        lease_directory=lease_directory,
        acquired_at_utc=T0 + timedelta(seconds=3),
        lease_id="LEASE-2",
    )
    second.release(released_at_utc=T0 + timedelta(seconds=4))


def test_fenced_lease_is_durable_and_never_stolen(tmp_path: Path) -> None:
    process = _process(tmp_path)
    lease_directory = tmp_path / "leases"
    handle = acquire_etabs_operation_lease_v1(
        process,
        "TX-FENCED",
        lease_directory=lease_directory,
        acquired_at_utc=T0,
        lease_id="LEASE-FENCED",
    )

    fenced = handle.fence("RESTORATION_UNVERIFIED", observed_at_utc=T0)

    assert fenced.disposition == "FENCED"
    assert handle.path.is_file()
    with pytest.raises(RuntimeError, match="LEASE_CONTENDED"):
        acquire_etabs_operation_lease_v1(
            process,
            "TX-OTHER",
            lease_directory=lease_directory,
            acquired_at_utc=T0,
        )


def test_lease_loss_fails_before_another_heartbeat(tmp_path: Path) -> None:
    process = _process(tmp_path)
    handle = acquire_etabs_operation_lease_v1(
        process,
        "TX-LOST",
        lease_directory=tmp_path / "leases",
        acquired_at_utc=T0,
    )
    handle.path.unlink()

    with pytest.raises(RuntimeError, match="LEASE_LOST"):
        handle.heartbeat(observed_at_utc=T0 + timedelta(seconds=1))


def test_call_ledger_persists_started_and_raw_returned_before_decode(
    tmp_path: Path,
) -> None:
    ledger = _ledger(tmp_path)
    decoder_saw: list[dict[str, object]] = []

    def decode(raw: object) -> str:
        rows = [json.loads(line) for line in ledger.path.read_text().splitlines()]
        decoder_saw.extend(rows)
        assert raw == ("B1", [0.0, 1.0], 0)
        return "decoded"

    result = invoke_recorded_etabs_call_v1(
        ledger,
        call_id="CALL-1",
        method="SapModel.Results.FrameForce",
        reviewed_signature="FrameForce(name, item_type) -> (..., ret)",
        redacted_arguments={"name_sha256": HASH_A},
        invoke=lambda: ("B1", [0.0, 1.0], 0),
        decode=decode,
        decoder_name="frame-force-v1",
    )
    identity = ledger.close()

    assert result == "decoded"
    assert [row["stage"] for row in decoder_saw] == ["STARTED", "RETURNED"]
    assert decoder_saw[1]["raw_projection"] == ["B1", [0.0, 1.0], 0]
    assert decoder_saw[1]["return_code"] == 0
    assert identity.record_count == 2
    assert identity.head_record_sha256 == decoder_saw[1]["record_sha256"]


def test_decode_failure_still_leaves_a_finalized_raw_call_boundary(
    tmp_path: Path,
) -> None:
    ledger = _ledger(tmp_path)

    def reject(_raw: object) -> None:
        assert len(ledger.path.read_text().splitlines()) == 2
        raise ValueError("strict decoder rejected shape")

    with pytest.raises(ValueError, match="strict decoder"):
        invoke_recorded_etabs_call_v1(
            ledger,
            call_id="CALL-1",
            method="SapModel.Results.FrameForce",
            reviewed_signature="FrameForce(name, item_type) -> (..., ret)",
            redacted_arguments={},
            invoke=lambda: ("unexpected", 0),
            decode=reject,
            decoder_name="frame-force-v1",
        )

    assert ledger.close().record_count == 2


def test_operation_failure_is_recorded_once_without_replay(tmp_path: Path) -> None:
    ledger = _ledger(tmp_path)
    invocation_count = 0

    def fail() -> None:
        nonlocal invocation_count
        invocation_count += 1
        raise RuntimeError("offline injected call failure")

    with pytest.raises(RuntimeError, match="injected call failure"):
        invoke_recorded_etabs_call_v1(
            ledger,
            call_id="CALL-FAIL",
            method="SapModel.Analyze.RunAnalysis",
            reviewed_signature="RunAnalysis() -> ret",
            redacted_arguments={},
            invoke=fail,
            decode=lambda raw: raw,
            decoder_name="return-code-v1",
        )

    assert invocation_count == 1
    assert ledger.close().record_count == 2
    returned = json.loads(ledger.path.read_text().splitlines()[1])
    assert returned["raw_shape"] == "CALL_RAISED"
    assert "offline injected call failure" in returned["error"]


def test_unmatched_started_and_truncated_ledger_are_rejected(tmp_path: Path) -> None:
    ledger = _ledger(tmp_path, "unmatched.jsonl")
    ledger.start(
        call_id="CALL-HANG",
        method="SapModel.Analyze.RunAnalysis",
        reviewed_signature="RunAnalysis() -> ret",
        redacted_arguments={},
    )
    ledger.abandon()

    with pytest.raises(RuntimeError, match="UNFINALIZED_CALL"):
        verify_etabs_call_ledger_v1(
            ledger.path,
            transaction_id="TX-1",
            storage_identity="local-test-store",
            redaction_policy="arguments-redacted-v1",
        )

    good = _ledger(tmp_path, "truncated.jsonl")
    _record_one_call(good)
    good.close()
    good.path.write_bytes(good.path.read_bytes().rstrip(b"\n"))
    with pytest.raises(RuntimeError, match="TRUNCATED"):
        verify_etabs_call_ledger_v1(
            good.path,
            transaction_id="TX-1",
            storage_identity="local-test-store",
            redaction_policy="arguments-redacted-v1",
        )


def test_evidence_bundle_verifies_ledger_and_retained_artifact(tmp_path: Path) -> None:
    ledger = _ledger(tmp_path)
    _record_one_call(ledger)
    ledger.close()
    artifact = tmp_path / "safe-projection.json"
    artifact.write_text('{"beam_count":1}\n', encoding="utf-8")
    manifest = tmp_path / "manifest.json"

    created = finalize_etabs_evidence_bundle_v1(
        manifest,
        evidence_root=tmp_path,
        ledger_path=ledger.path,
        transaction_id="TX-1",
        storage_identity="local-test-store",
        redaction_policy="arguments-redacted-v1",
        retention_policy="retain-30-days",
        target_observation_sha256=HASH_A,
        runtime_fingerprint_sha256=HASH_B,
        model_identity_sha256=HASH_C,
        result_epoch_sha256=None,
        artifact_paths=(artifact,),
        finalized_at_utc=T0,
    )

    verified = verify_etabs_evidence_bundle_v1(
        manifest,
        evidence_root=tmp_path,
    )
    assert verified.manifest_sha256 == created.manifest_sha256
    artifact.write_text('{"beam_count":2}\n', encoding="utf-8")
    with pytest.raises(RuntimeError, match="ARTIFACT_HASH_MISMATCH"):
        verify_etabs_evidence_bundle_v1(manifest, evidence_root=tmp_path)


def test_operation_outcome_requires_closed_ledger_and_equal_attached_state(
    tmp_path: Path,
) -> None:
    ledger = _ledger(tmp_path)
    _record_one_call(ledger)
    ledger_identity = ledger.close()
    broker = ETABSBrokerResultV1(
        transaction_id="TX-1",
        status="COMPLETED",
        worker_pid=1234,
        started_at_utc=T0,
        completed_at_utc=T0 + timedelta(seconds=1),
        payload={"rows": 1},
        error=None,
        process_instance_fenced=False,
    )

    completed = build_etabs_operation_outcome_v1(
        broker_result=broker,
        access_mode="ATTACHED_OBSERVE",
        primary_outcome="COMPLETED",
        restoration_outcome="VERIFIED_EQUAL",
        deadline_seconds=5,
        call_ledger=ledger_identity,
        pre_state_sha256=HASH_A,
        post_state_sha256=HASH_A,
    )
    blocked = build_etabs_operation_outcome_v1(
        broker_result=broker,
        access_mode="ATTACHED_OBSERVE",
        primary_outcome="COMPLETED",
        restoration_outcome="NOT_ATTEMPTED",
        deadline_seconds=5,
        call_ledger=None,
        pre_state_sha256=HASH_A,
        post_state_sha256=None,
    )

    assert completed.disposition == "COMPLETED"
    assert blocked.disposition == "BLOCKED"


def test_supervised_broker_returns_serializable_payload_and_keeps_lease_active(
    tmp_path: Path,
) -> None:
    process = _process(tmp_path)
    lease = acquire_etabs_operation_lease_v1(
        process,
        "TX-BROKER-OK",
        lease_directory=tmp_path / "leases",
        duration=timedelta(seconds=10),
    )

    result = run_etabs_sta_broker_v1(
        _broker_echo,
        args=("ready",),
        deadline_seconds=15,
        heartbeat_seconds=0.05,
        lease=lease,
    )

    assert result.status == "COMPLETED"
    assert result.payload == {"echo": "ready"}
    assert not result.process_instance_fenced
    assert lease.lease.worker_pid == result.worker_pid
    lease.release()


def test_supervised_broker_timeout_terminates_only_worker_and_fences_instance(
    tmp_path: Path,
) -> None:
    process = _process(tmp_path)
    lease = acquire_etabs_operation_lease_v1(
        process,
        "TX-BROKER-HANG",
        lease_directory=tmp_path / "leases",
        duration=timedelta(seconds=10),
    )

    result = run_etabs_sta_broker_v1(
        _broker_hang,
        args=(5.0,),
        deadline_seconds=0.2,
        heartbeat_seconds=0.03,
        lease=lease,
    )

    assert result.status == "TIMED_OUT"
    assert result.process_instance_fenced
    assert lease.lease.disposition == "FENCED"
    assert lease.lease.fence_reason == (
        "RESTORATION_UNVERIFIED: BROKER_DEADLINE_EXPIRED"
    )
    assert lease.path.is_file()
    outcome = build_etabs_operation_outcome_v1(
        broker_result=result,
        access_mode="ATTACHED_OBSERVE",
        primary_outcome="TIMED_OUT",
        restoration_outcome="NOT_ATTEMPTED",
        deadline_seconds=0.2,
        call_ledger=None,
        fence_reason=lease.lease.fence_reason,
    )
    assert outcome.disposition == "RESTORATION_UNVERIFIED"


def test_supervised_broker_reports_operation_failure_without_retry(
    tmp_path: Path,
) -> None:
    process = _process(tmp_path)
    lease = acquire_etabs_operation_lease_v1(
        process,
        "TX-BROKER-ERROR",
        lease_directory=tmp_path / "leases",
        duration=timedelta(seconds=15),
    )

    result = run_etabs_sta_broker_v1(
        _broker_fail,
        deadline_seconds=15,
        heartbeat_seconds=0.05,
        lease=lease,
    )

    assert result.status == "ERROR"
    assert "offline injected operation failure" in (result.error or "")
    assert not result.process_instance_fenced
    lease.release()
