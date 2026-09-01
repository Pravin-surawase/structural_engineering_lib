"""Cross-process ETABS lease, supervised STA broker, and durable call evidence.

The parent process owns the lease and deadline.  A timeout terminates only the
short-lived broker process and leaves a fenced lease receipt; this module never
terminates an ETABS process.  Call evidence is append-only and records STARTED
before invocation and RETURNED raw projection before decoding.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import multiprocessing
import os
import queue
import secrets
import time
import traceback
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Literal, Self

from pydantic import Field, model_validator

from structural_lib.services.contracts.common import StrictPublicModel
from structural_lib.services.etabs_session_guard import ETABSProcessInstanceV1

__all__ = [
    "ETABSArtifactIdentityV1",
    "ETABSBrokerResultV1",
    "ETABSCallLedgerIdentityV1",
    "ETABSCallLedgerV1",
    "ETABSCallRecordV1",
    "ETABSEvidenceBundleV1",
    "ETABSLeaseHandleV1",
    "ETABSOperationLeaseV1",
    "ETABSOperationOutcomeV1",
    "acquire_etabs_operation_lease_v1",
    "build_etabs_operation_outcome_v1",
    "finalize_etabs_evidence_bundle_v1",
    "invoke_recorded_etabs_call_v1",
    "run_etabs_sta_broker_v1",
    "verify_etabs_call_ledger_v1",
    "verify_etabs_evidence_bundle_v1",
]


_SHA256_PATTERN = r"^[0-9a-f]{64}$"
_MAX_CALL_RECORD_BYTES = 64 * 1024
_MAX_LEDGER_RECORDS = 100_000
_MAX_MANIFEST_BYTES = 16 * 1024 * 1024
_MAX_ARTIFACTS = 10_000


def _utc(value: datetime, name: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


def _json_time(value: datetime) -> str:
    return _utc(value, "datetime").isoformat().replace("+00:00", "Z")


def _canonical_json(value: Any) -> str:
    if isinstance(value, StrictPublicModel):
        value = value.model_dump(mode="json")
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _load_json_object(text: str, *, maximum_bytes: int) -> dict[str, Any]:
    if len(text.encode("utf-8")) > maximum_bytes:
        raise ValueError("JSON evidence exceeds its bounded size")
    value = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    if not isinstance(value, dict):
        raise ValueError("JSON evidence must be an object")
    return value


def _decode_canonical_time(
    payload: dict[str, Any], field: str, *, optional: bool = False
) -> None:
    raw = payload.get(field)
    if raw is None and optional:
        return
    if not isinstance(raw, str) or not raw.endswith("Z"):
        raise ValueError(f"{field} must be a canonical UTC timestamp")
    try:
        parsed = datetime.fromisoformat(raw.removesuffix("Z") + "+00:00")
    except ValueError as exc:
        raise ValueError(f"{field} must be a canonical UTC timestamp") from exc
    if _json_time(parsed) != raw:
        raise ValueError(f"{field} must be a canonical UTC timestamp")
    payload[field] = parsed


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_exclusive_json(path: Path, payload: Mapping[str, Any]) -> None:
    data = (_canonical_json(dict(payload)) + "\n").encode("utf-8")
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=False) as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    finally:
        os.close(descriptor)


def _replace_json(path: Path, payload: Mapping[str, Any]) -> None:
    temporary = path.with_name(f".{path.name}.{secrets.token_hex(8)}.tmp")
    try:
        _write_exclusive_json(temporary, payload)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


class ETABSOperationLeaseV1(StrictPublicModel):
    """OS-visible exclusive lease keyed by PID plus process start time."""

    schema_version: Literal["etabs-operation-lease/v1"] = "etabs-operation-lease/v1"
    lease_id: str = Field(min_length=1, max_length=120)
    lease_key_sha256: str = Field(pattern=_SHA256_PATTERN)
    transaction_id: str = Field(min_length=1, max_length=120)
    process_instance_sha256: str = Field(pattern=_SHA256_PATTERN)
    process_pid: int = Field(gt=0)
    process_start_time_utc: datetime
    supervisor_pid: int = Field(gt=0)
    worker_pid: int | None = Field(default=None, gt=0)
    acquired_at_utc: datetime
    expires_at_utc: datetime
    heartbeat_at_utc: datetime
    disposition: Literal["ACTIVE", "RELEASED", "FENCED"]
    fence_reason: str | None = Field(default=None, max_length=500)
    lease_sha256: str = Field(pattern=_SHA256_PATTERN)

    @model_validator(mode="after")
    def validate_lease(self) -> Self:
        acquired = _utc(self.acquired_at_utc, "acquired_at_utc")
        expires = _utc(self.expires_at_utc, "expires_at_utc")
        heartbeat = _utc(self.heartbeat_at_utc, "heartbeat_at_utc")
        _utc(self.process_start_time_utc, "process_start_time_utc")
        if not acquired <= heartbeat <= expires:
            raise ValueError("lease heartbeat must lie within its active interval")
        if self.disposition == "FENCED" and not self.fence_reason:
            raise ValueError("fenced lease requires a reason")
        if self.disposition != "FENCED" and self.fence_reason is not None:
            raise ValueError("only fenced lease may carry a fence reason")
        expected = _digest(self.model_dump(mode="json", exclude={"lease_sha256"}))
        if self.lease_sha256 != expected:
            raise ValueError("lease_sha256 does not match canonical lease")
        return self


def _lease_model(payload: dict[str, Any]) -> ETABSOperationLeaseV1:
    basis = {
        **payload,
        "process_start_time_utc": _json_time(payload["process_start_time_utc"]),
        "acquired_at_utc": _json_time(payload["acquired_at_utc"]),
        "expires_at_utc": _json_time(payload["expires_at_utc"]),
        "heartbeat_at_utc": _json_time(payload["heartbeat_at_utc"]),
    }
    return ETABSOperationLeaseV1(
        **payload,
        lease_sha256=_digest(basis),
    )


class ETABSLeaseHandleV1:
    """Mutable local handle whose every transition writes a durable receipt."""

    def __init__(self, path: Path, lease: ETABSOperationLeaseV1) -> None:
        self.path = path
        self.lease = lease

    def _read_exact(self) -> ETABSOperationLeaseV1:
        if not self.path.is_file():
            raise RuntimeError("ETABS_OPERATION_LEASE_LOST")
        payload = _load_json_object(
            self.path.read_text(encoding="utf-8"),
            maximum_bytes=_MAX_CALL_RECORD_BYTES,
        )
        for field in (
            "process_start_time_utc",
            "acquired_at_utc",
            "expires_at_utc",
            "heartbeat_at_utc",
        ):
            _decode_canonical_time(payload, field)
        current = ETABSOperationLeaseV1.model_validate(payload)
        if current.lease_id != self.lease.lease_id:
            raise RuntimeError("ETABS_OPERATION_LEASE_REPLACED")
        return current

    def heartbeat(
        self,
        *,
        observed_at_utc: datetime | None = None,
        worker_pid: int | None = None,
    ) -> ETABSOperationLeaseV1:
        current = self._read_exact()
        if current.disposition != "ACTIVE":
            raise RuntimeError("ETABS_OPERATION_LEASE_NOT_ACTIVE")
        observed = _utc(observed_at_utc or datetime.now(UTC), "observed_at_utc")
        if observed < current.heartbeat_at_utc:
            raise RuntimeError("ETABS_OPERATION_LEASE_HEARTBEAT_REGRESSION")
        if observed > current.expires_at_utc:
            raise RuntimeError("ETABS_OPERATION_LEASE_EXPIRED")
        payload = current.model_dump(exclude={"lease_sha256"})
        payload.update(
            heartbeat_at_utc=observed,
            worker_pid=worker_pid if worker_pid is not None else current.worker_pid,
        )
        updated = _lease_model(payload)
        _replace_json(self.path, updated.model_dump(mode="json"))
        self.lease = updated
        return updated

    def fence(
        self,
        reason: str,
        *,
        observed_at_utc: datetime | None = None,
    ) -> ETABSOperationLeaseV1:
        current = self._read_exact()
        observed = _utc(observed_at_utc or datetime.now(UTC), "observed_at_utc")
        if observed < current.heartbeat_at_utc:
            observed = current.heartbeat_at_utc
        if observed > current.expires_at_utc:
            observed = current.expires_at_utc
        payload = current.model_dump(exclude={"lease_sha256"})
        payload.update(
            heartbeat_at_utc=observed,
            disposition="FENCED",
            fence_reason=reason,
        )
        fenced = _lease_model(payload)
        _replace_json(self.path, fenced.model_dump(mode="json"))
        self.lease = fenced
        return fenced

    def release(
        self, *, released_at_utc: datetime | None = None
    ) -> ETABSOperationLeaseV1:
        current = self._read_exact()
        if current.disposition != "ACTIVE":
            raise RuntimeError("ETABS_OPERATION_LEASE_CANNOT_RELEASE")
        released = _utc(released_at_utc or datetime.now(UTC), "released_at_utc")
        if released < current.heartbeat_at_utc:
            released = current.heartbeat_at_utc
        if released > current.expires_at_utc:
            released = current.expires_at_utc
        payload = current.model_dump(exclude={"lease_sha256"})
        payload.update(
            heartbeat_at_utc=released,
            disposition="RELEASED",
        )
        receipt = _lease_model(payload)
        _replace_json(self.path, receipt.model_dump(mode="json"))
        receipt_path = self.path.with_name(f"{receipt.lease_id}.released.json")
        if receipt_path.exists():
            raise RuntimeError("ETABS_OPERATION_RELEASE_RECEIPT_EXISTS")
        os.replace(self.path, receipt_path)
        self.lease = receipt
        return receipt


def acquire_etabs_operation_lease_v1(
    process_instance: ETABSProcessInstanceV1,
    transaction_id: str,
    *,
    lease_directory: str | Path,
    acquired_at_utc: datetime | None = None,
    duration: timedelta = timedelta(minutes=5),
    lease_id: str | None = None,
) -> ETABSLeaseHandleV1:
    """Acquire an atomic cross-process file lease; never steal stale/fenced state."""

    if duration <= timedelta(0) or duration > timedelta(hours=1):
        raise ValueError("lease duration must be within (0, 1 hour]")
    directory = Path(lease_directory).resolve(strict=False)
    directory.mkdir(parents=True, exist_ok=True)
    if not directory.is_dir():
        raise ValueError("lease_directory must be a directory")
    acquired = _utc(acquired_at_utc or datetime.now(UTC), "acquired_at_utc")
    key_basis = {
        "pid": process_instance.pid,
        "start_time_utc": _json_time(process_instance.start_time_utc),
    }
    lease_key = _digest(key_basis)
    path = directory / f"etabs-{lease_key}.lease.json"
    payload: dict[str, Any] = {
        "schema_version": "etabs-operation-lease/v1",
        "lease_id": lease_id or secrets.token_hex(16),
        "lease_key_sha256": lease_key,
        "transaction_id": transaction_id,
        "process_instance_sha256": process_instance.instance_sha256,
        "process_pid": process_instance.pid,
        "process_start_time_utc": process_instance.start_time_utc,
        "supervisor_pid": os.getpid(),
        "worker_pid": None,
        "acquired_at_utc": acquired,
        "expires_at_utc": acquired + duration,
        "heartbeat_at_utc": acquired,
        "disposition": "ACTIVE",
        "fence_reason": None,
    }
    lease = _lease_model(payload)
    try:
        _write_exclusive_json(path, lease.model_dump(mode="json"))
    except FileExistsError as exc:
        raise RuntimeError("ETABS_OPERATION_LEASE_CONTENDED") from exc
    return ETABSLeaseHandleV1(path, lease)


class ETABSCallRecordV1(StrictPublicModel):
    """One hash-chained durable STARTED or RETURNED call-stage record."""

    schema_version: Literal["etabs-call-record/v1"] = "etabs-call-record/v1"
    transaction_id: str = Field(min_length=1, max_length=120)
    call_id: str = Field(min_length=1, max_length=120)
    sequence: int = Field(ge=1, le=_MAX_LEDGER_RECORDS)
    previous_record_sha256: str | None = Field(default=None, pattern=_SHA256_PATTERN)
    stage: Literal["STARTED", "RETURNED"]
    method: str = Field(min_length=1, max_length=500)
    reviewed_signature: str = Field(min_length=1, max_length=1000)
    redacted_arguments: dict[str, Any]
    raw_projection: Any | None = None
    raw_shape: str | None = Field(default=None, max_length=500)
    return_code: int | None = None
    started_at_utc: datetime
    completed_at_utc: datetime | None = None
    durable_flush: Literal[True] = True
    decoder: str | None = Field(default=None, max_length=500)
    error: str | None = Field(default=None, max_length=2000)
    record_sha256: str = Field(pattern=_SHA256_PATTERN)

    @model_validator(mode="after")
    def validate_record(self) -> Self:
        started = _utc(self.started_at_utc, "started_at_utc")
        if self.stage == "STARTED":
            if any(
                value is not None
                for value in (
                    self.raw_projection,
                    self.raw_shape,
                    self.return_code,
                    self.completed_at_utc,
                    self.decoder,
                    self.error,
                )
            ):
                raise ValueError("STARTED record cannot carry return fields")
        else:
            if self.completed_at_utc is None or self.raw_shape is None:
                raise ValueError("RETURNED record requires completion time and shape")
            if _utc(self.completed_at_utc, "completed_at_utc") < started:
                raise ValueError("call completion cannot precede its start")
        expected = _digest(self.model_dump(mode="json", exclude={"record_sha256"}))
        if self.record_sha256 != expected:
            raise ValueError("record_sha256 does not match canonical call record")
        return self


def _call_record(payload: dict[str, Any]) -> ETABSCallRecordV1:
    basis = {
        **payload,
        "started_at_utc": _json_time(payload["started_at_utc"]),
        "completed_at_utc": (
            _json_time(payload["completed_at_utc"])
            if payload.get("completed_at_utc") is not None
            else None
        ),
    }
    return ETABSCallRecordV1(**payload, record_sha256=_digest(basis))


class ETABSCallLedgerIdentityV1(StrictPublicModel):
    """Verified bounded ledger head used by an evidence bundle."""

    schema_version: Literal["etabs-call-ledger-identity/v1"] = (
        "etabs-call-ledger-identity/v1"
    )
    transaction_id: str = Field(min_length=1, max_length=120)
    storage_identity: str = Field(min_length=1, max_length=240)
    redaction_policy: str = Field(min_length=1, max_length=500)
    record_count: int = Field(ge=0, le=_MAX_LEDGER_RECORDS)
    head_record_sha256: str | None = Field(default=None, pattern=_SHA256_PATTERN)
    ledger_sha256: str = Field(pattern=_SHA256_PATTERN)


def verify_etabs_call_ledger_v1(
    path: str | Path,
    *,
    transaction_id: str,
    storage_identity: str,
    redaction_policy: str,
) -> ETABSCallLedgerIdentityV1:
    """Reject gaps, stage mismatch, truncation, or hash-chain corruption."""

    ledger_path = Path(path).resolve(strict=True)
    records: list[ETABSCallRecordV1] = []
    pending_call: str | None = None
    previous: str | None = None
    with ledger_path.open("r", encoding="utf-8") as handle:
        for index, line in enumerate(handle, start=1):
            if index > _MAX_LEDGER_RECORDS:
                raise RuntimeError("ETABS_CALL_LEDGER_TOO_LARGE")
            if not line.endswith("\n"):
                raise RuntimeError("ETABS_CALL_LEDGER_TRUNCATED")
            payload = _load_json_object(
                line,
                maximum_bytes=_MAX_CALL_RECORD_BYTES,
            )
            _decode_canonical_time(payload, "started_at_utc")
            _decode_canonical_time(payload, "completed_at_utc", optional=True)
            record = ETABSCallRecordV1.model_validate(payload)
            if record.transaction_id != transaction_id:
                raise RuntimeError("ETABS_CALL_LEDGER_TRANSACTION_MISMATCH")
            if record.sequence != index or record.previous_record_sha256 != previous:
                raise RuntimeError("ETABS_CALL_LEDGER_CHAIN_MISMATCH")
            if record.stage == "STARTED":
                if pending_call is not None:
                    raise RuntimeError("ETABS_CALL_LEDGER_UNMATCHED_STARTED")
                pending_call = record.call_id
            else:
                if pending_call != record.call_id:
                    raise RuntimeError("ETABS_CALL_LEDGER_RETURNED_WITHOUT_STARTED")
                pending_call = None
            previous = record.record_sha256
            records.append(record)
    if pending_call is not None:
        raise RuntimeError("ETABS_CALL_LEDGER_UNFINALIZED_CALL")
    return ETABSCallLedgerIdentityV1(
        transaction_id=transaction_id,
        storage_identity=storage_identity,
        redaction_policy=redaction_policy,
        record_count=len(records),
        head_record_sha256=previous,
        ledger_sha256=_sha256_file(ledger_path),
    )


class ETABSCallLedgerV1:
    """Exclusive append-only ledger with fsync after every stage."""

    def __init__(
        self,
        path: str | Path,
        *,
        transaction_id: str,
        storage_identity: str,
        redaction_policy: str,
    ) -> None:
        self.path = Path(path).resolve(strict=False)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(
            self.path,
            os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_APPEND,
            0o600,
        )
        self._handle = os.fdopen(descriptor, "ab", buffering=0)
        self.transaction_id = transaction_id
        self.storage_identity = storage_identity
        self.redaction_policy = redaction_policy
        self._sequence = 0
        self._head: str | None = None
        self._pending: tuple[str, datetime] | None = None
        self._closed = False

    def _append(self, record: ETABSCallRecordV1) -> None:
        data = (_canonical_json(record.model_dump(mode="json")) + "\n").encode("utf-8")
        if len(data) > _MAX_CALL_RECORD_BYTES:
            raise ValueError("ETABS call record exceeds the bounded record size")
        self._handle.write(data)
        self._handle.flush()
        os.fsync(self._handle.fileno())
        self._sequence = record.sequence
        self._head = record.record_sha256

    def start(
        self,
        *,
        call_id: str,
        method: str,
        reviewed_signature: str,
        redacted_arguments: Mapping[str, Any],
        started_at_utc: datetime | None = None,
    ) -> ETABSCallRecordV1:
        if self._closed or self._pending is not None:
            raise RuntimeError("ETABS_CALL_LEDGER_NOT_READY")
        started = _utc(started_at_utc or datetime.now(UTC), "started_at_utc")
        record = _call_record(
            {
                "schema_version": "etabs-call-record/v1",
                "transaction_id": self.transaction_id,
                "call_id": call_id,
                "sequence": self._sequence + 1,
                "previous_record_sha256": self._head,
                "stage": "STARTED",
                "method": method,
                "reviewed_signature": reviewed_signature,
                "redacted_arguments": dict(redacted_arguments),
                "raw_projection": None,
                "raw_shape": None,
                "return_code": None,
                "started_at_utc": started,
                "completed_at_utc": None,
                "durable_flush": True,
                "decoder": None,
                "error": None,
            }
        )
        self._append(record)
        self._pending = (call_id, started)
        return record

    def returned(
        self,
        *,
        call_id: str,
        method: str,
        reviewed_signature: str,
        redacted_arguments: Mapping[str, Any],
        raw_projection: Any | None,
        raw_shape: str,
        return_code: int | None,
        decoder: str | None,
        error: str | None,
        completed_at_utc: datetime | None = None,
    ) -> ETABSCallRecordV1:
        if self._closed or self._pending is None or self._pending[0] != call_id:
            raise RuntimeError("ETABS_CALL_LEDGER_NO_MATCHING_STARTED")
        completed = _utc(completed_at_utc or datetime.now(UTC), "completed_at_utc")
        record = _call_record(
            {
                "schema_version": "etabs-call-record/v1",
                "transaction_id": self.transaction_id,
                "call_id": call_id,
                "sequence": self._sequence + 1,
                "previous_record_sha256": self._head,
                "stage": "RETURNED",
                "method": method,
                "reviewed_signature": reviewed_signature,
                "redacted_arguments": dict(redacted_arguments),
                "raw_projection": raw_projection,
                "raw_shape": raw_shape,
                "return_code": return_code,
                "started_at_utc": self._pending[1],
                "completed_at_utc": completed,
                "durable_flush": True,
                "decoder": decoder,
                "error": error,
            }
        )
        self._append(record)
        self._pending = None
        return record

    def close(self) -> ETABSCallLedgerIdentityV1:
        if self._closed:
            raise RuntimeError("ETABS_CALL_LEDGER_ALREADY_CLOSED")
        self._handle.flush()
        os.fsync(self._handle.fileno())
        self._handle.close()
        self._closed = True
        return verify_etabs_call_ledger_v1(
            self.path,
            transaction_id=self.transaction_id,
            storage_identity=self.storage_identity,
            redaction_policy=self.redaction_policy,
        )

    def abandon(self) -> None:
        """Durably close while retaining an unmatched STARTED failure boundary."""

        if self._closed:
            return
        self._handle.flush()
        os.fsync(self._handle.fileno())
        self._handle.close()
        self._closed = True


def _json_projection(value: Any) -> Any:
    encoded = _canonical_json(value)
    if len(encoded.encode("utf-8")) > _MAX_CALL_RECORD_BYTES // 2:
        raise ValueError("raw projection exceeds the bounded call payload")
    return json.loads(encoded)


def invoke_recorded_etabs_call_v1(
    ledger: ETABSCallLedgerV1,
    *,
    call_id: str,
    method: str,
    reviewed_signature: str,
    redacted_arguments: Mapping[str, Any],
    invoke: Callable[[], Any],
    decode: Callable[[Any], Any],
    decoder_name: str,
) -> Any:
    """Persist STARTED, invoke once, persist raw RETURNED, then decode."""

    ledger.start(
        call_id=call_id,
        method=method,
        reviewed_signature=reviewed_signature,
        redacted_arguments=redacted_arguments,
    )
    try:
        raw = invoke()
    except Exception as exc:
        ledger.returned(
            call_id=call_id,
            method=method,
            reviewed_signature=reviewed_signature,
            redacted_arguments=redacted_arguments,
            raw_projection=None,
            raw_shape="CALL_RAISED",
            return_code=None,
            decoder=None,
            error=f"{type(exc).__name__}: {exc}",
        )
        raise
    try:
        projection = _json_projection(raw)
    except Exception as exc:
        ledger.returned(
            call_id=call_id,
            method=method,
            reviewed_signature=reviewed_signature,
            redacted_arguments=redacted_arguments,
            raw_projection=None,
            raw_shape=type(raw).__name__,
            return_code=None,
            decoder=decoder_name,
            error=f"RAW_PROJECTION_FAILED: {type(exc).__name__}: {exc}",
        )
        raise
    return_code = (
        raw[-1]
        if isinstance(raw, (list, tuple))
        and raw
        and isinstance(raw[-1], int)
        and not isinstance(raw[-1], bool)
        else None
    )
    ledger.returned(
        call_id=call_id,
        method=method,
        reviewed_signature=reviewed_signature,
        redacted_arguments=redacted_arguments,
        raw_projection=projection,
        raw_shape=type(raw).__name__,
        return_code=return_code,
        decoder=decoder_name,
        error=None,
    )
    return decode(raw)


class ETABSArtifactIdentityV1(StrictPublicModel):
    relative_path: str = Field(min_length=1, max_length=1024)
    size_bytes: int = Field(ge=0)
    sha256: str = Field(pattern=_SHA256_PATTERN)
    retention: str = Field(min_length=1, max_length=500)


class ETABSEvidenceBundleV1(StrictPublicModel):
    """Atomic final manifest for reviewed, retained ETABS evidence."""

    schema_version: Literal["etabs-evidence-bundle/v1"] = "etabs-evidence-bundle/v1"
    transaction_id: str = Field(min_length=1, max_length=120)
    disposition: Literal["FINALIZED"] = "FINALIZED"
    ledger_relative_path: str = Field(min_length=1, max_length=1024)
    ledger_sha256: str = Field(pattern=_SHA256_PATTERN)
    ledger_head_sha256: str | None = Field(default=None, pattern=_SHA256_PATTERN)
    call_record_count: int = Field(ge=0, le=_MAX_LEDGER_RECORDS)
    target_observation_sha256: str = Field(pattern=_SHA256_PATTERN)
    runtime_fingerprint_sha256: str = Field(pattern=_SHA256_PATTERN)
    model_identity_sha256: str = Field(pattern=_SHA256_PATTERN)
    result_epoch_sha256: str | None = Field(default=None, pattern=_SHA256_PATTERN)
    artifacts: tuple[ETABSArtifactIdentityV1, ...] = Field(max_length=_MAX_ARTIFACTS)
    storage_identity: str = Field(min_length=1, max_length=240)
    redaction_policy: str = Field(min_length=1, max_length=500)
    retention_policy: str = Field(min_length=1, max_length=500)
    finalized_at_utc: datetime
    manifest_sha256: str = Field(pattern=_SHA256_PATTERN)

    @model_validator(mode="after")
    def validate_manifest(self) -> Self:
        _utc(self.finalized_at_utc, "finalized_at_utc")
        paths = [artifact.relative_path for artifact in self.artifacts]
        if len(paths) != len(set(paths)):
            raise ValueError("evidence artifact paths must be unique")
        expected = _digest(self.model_dump(mode="json", exclude={"manifest_sha256"}))
        if self.manifest_sha256 != expected:
            raise ValueError("manifest_sha256 does not match canonical manifest")
        return self


def _contained_file(root: Path, path: str | Path) -> tuple[Path, str]:
    resolved = Path(path).resolve(strict=True)
    if not resolved.is_file() or not resolved.is_relative_to(root):
        raise ValueError("evidence file must be a regular file within evidence_root")
    return resolved, resolved.relative_to(root).as_posix()


def finalize_etabs_evidence_bundle_v1(
    manifest_path: str | Path,
    *,
    evidence_root: str | Path,
    ledger_path: str | Path,
    transaction_id: str,
    storage_identity: str,
    redaction_policy: str,
    retention_policy: str,
    target_observation_sha256: str,
    runtime_fingerprint_sha256: str,
    model_identity_sha256: str,
    result_epoch_sha256: str | None,
    artifact_paths: Sequence[str | Path] = (),
    finalized_at_utc: datetime | None = None,
) -> ETABSEvidenceBundleV1:
    """Write one create-new atomic manifest after verifying ledger/artifacts."""

    root = Path(evidence_root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("evidence_root must be an existing directory")
    manifest = Path(manifest_path).resolve(strict=False)
    if not manifest.is_relative_to(root) or manifest.exists():
        raise ValueError("manifest must be a new path within evidence_root")
    ledger, ledger_relative = _contained_file(root, ledger_path)
    ledger_identity = verify_etabs_call_ledger_v1(
        ledger,
        transaction_id=transaction_id,
        storage_identity=storage_identity,
        redaction_policy=redaction_policy,
    )
    artifacts = tuple(
        ETABSArtifactIdentityV1(
            relative_path=relative,
            size_bytes=resolved.stat().st_size,
            sha256=_sha256_file(resolved),
            retention=retention_policy,
        )
        for resolved, relative in (
            _contained_file(root, path) for path in artifact_paths
        )
    )
    finalized = _utc(finalized_at_utc or datetime.now(UTC), "finalized_at_utc")
    basis = {
        "schema_version": "etabs-evidence-bundle/v1",
        "transaction_id": transaction_id,
        "disposition": "FINALIZED",
        "ledger_relative_path": ledger_relative,
        "ledger_sha256": ledger_identity.ledger_sha256,
        "ledger_head_sha256": ledger_identity.head_record_sha256,
        "call_record_count": ledger_identity.record_count,
        "target_observation_sha256": target_observation_sha256,
        "runtime_fingerprint_sha256": runtime_fingerprint_sha256,
        "model_identity_sha256": model_identity_sha256,
        "result_epoch_sha256": result_epoch_sha256,
        "artifacts": [artifact.model_dump(mode="json") for artifact in artifacts],
        "storage_identity": storage_identity,
        "redaction_policy": redaction_policy,
        "retention_policy": retention_policy,
        "finalized_at_utc": _json_time(finalized),
    }
    bundle = ETABSEvidenceBundleV1.model_validate(
        {
            **basis,
            "artifacts": artifacts,
            "finalized_at_utc": finalized,
            "manifest_sha256": _digest(basis),
        }
    )
    manifest.parent.mkdir(parents=True, exist_ok=True)
    temporary = manifest.with_name(f".{manifest.name}.{secrets.token_hex(8)}.tmp")
    try:
        _write_exclusive_json(temporary, bundle.model_dump(mode="json"))
        try:
            os.link(temporary, manifest)
        except FileExistsError as exc:
            raise RuntimeError("ETABS_EVIDENCE_MANIFEST_ALREADY_EXISTS") from exc
    finally:
        temporary.unlink(missing_ok=True)
    return bundle


def verify_etabs_evidence_bundle_v1(
    manifest_path: str | Path,
    *,
    evidence_root: str | Path,
) -> ETABSEvidenceBundleV1:
    """Reject a corrupt manifest, ledger, artifact, or path escape."""

    root = Path(evidence_root).resolve(strict=True)
    manifest, _relative = _contained_file(root, manifest_path)
    payload = _load_json_object(
        manifest.read_text(encoding="utf-8"),
        maximum_bytes=_MAX_MANIFEST_BYTES,
    )
    _decode_canonical_time(payload, "finalized_at_utc")
    raw_artifacts = payload.get("artifacts")
    if not isinstance(raw_artifacts, list):
        raise ValueError("artifacts must be a JSON array")
    payload["artifacts"] = tuple(
        ETABSArtifactIdentityV1.model_validate(item) for item in raw_artifacts
    )
    bundle = ETABSEvidenceBundleV1.model_validate(payload)
    ledger = (root / bundle.ledger_relative_path).resolve(strict=True)
    if not ledger.is_relative_to(root):
        raise RuntimeError("ETABS_EVIDENCE_LEDGER_PATH_ESCAPE")
    identity = verify_etabs_call_ledger_v1(
        ledger,
        transaction_id=bundle.transaction_id,
        storage_identity=bundle.storage_identity,
        redaction_policy=bundle.redaction_policy,
    )
    if (
        identity.ledger_sha256 != bundle.ledger_sha256
        or identity.head_record_sha256 != bundle.ledger_head_sha256
        or identity.record_count != bundle.call_record_count
    ):
        raise RuntimeError("ETABS_EVIDENCE_LEDGER_IDENTITY_MISMATCH")
    for artifact in bundle.artifacts:
        path = (root / artifact.relative_path).resolve(strict=True)
        if not path.is_file() or not path.is_relative_to(root):
            raise RuntimeError("ETABS_EVIDENCE_ARTIFACT_MISSING")
        if path.stat().st_size != artifact.size_bytes:
            raise RuntimeError("ETABS_EVIDENCE_ARTIFACT_SIZE_MISMATCH")
        if _sha256_file(path) != artifact.sha256:
            raise RuntimeError("ETABS_EVIDENCE_ARTIFACT_HASH_MISMATCH")
    return bundle


class ETABSBrokerResultV1(StrictPublicModel):
    """Parent-observed outcome of one supervised broker process."""

    schema_version: Literal["etabs-sta-broker-result/v1"] = "etabs-sta-broker-result/v1"
    transaction_id: str = Field(min_length=1, max_length=120)
    status: Literal["COMPLETED", "ERROR", "TIMED_OUT"]
    worker_pid: int | None = Field(default=None, gt=0)
    started_at_utc: datetime
    completed_at_utc: datetime
    payload: Any | None = None
    error: str | None = Field(default=None, max_length=4000)
    process_instance_fenced: bool


class ETABSOperationOutcomeV1(StrictPublicModel):
    """One explicit operation/postflight outcome bound to durable call evidence."""

    schema_version: Literal["etabs-operation-outcome/v1"] = "etabs-operation-outcome/v1"
    transaction_id: str = Field(min_length=1, max_length=120)
    access_mode: Literal["ATTACHED_OBSERVE", "OWNED_COPY_MUTATION"]
    disposition: Literal[
        "COMPLETED", "BLOCKED", "RESTORATION_UNVERIFIED", "TRANSACTION_UNCERTAIN"
    ]
    primary_outcome: Literal["COMPLETED", "BLOCKED", "ERROR", "TIMED_OUT"]
    restoration_outcome: Literal[
        "NOT_REQUIRED", "VERIFIED_EQUAL", "FAILED", "NOT_ATTEMPTED"
    ]
    broker_status: Literal["COMPLETED", "ERROR", "TIMED_OUT"]
    deadline_seconds: float = Field(gt=0, le=300)
    process_instance_fenced: bool
    pre_state_sha256: str | None = Field(default=None, pattern=_SHA256_PATTERN)
    post_state_sha256: str | None = Field(default=None, pattern=_SHA256_PATTERN)
    call_ledger: ETABSCallLedgerIdentityV1 | None = None
    fence_reason: str | None = Field(default=None, max_length=500)
    started_at_utc: datetime
    completed_at_utc: datetime
    outcome_sha256: str = Field(pattern=_SHA256_PATTERN)

    @model_validator(mode="after")
    def validate_outcome(self) -> Self:
        started = _utc(self.started_at_utc, "started_at_utc")
        completed = _utc(self.completed_at_utc, "completed_at_utc")
        if completed < started:
            raise ValueError("operation completion cannot precede its start")
        if self.process_instance_fenced != (self.fence_reason is not None):
            raise ValueError("fenced outcome and fence reason must agree")
        if self.disposition == "COMPLETED":
            if (
                self.primary_outcome != "COMPLETED"
                or self.broker_status != "COMPLETED"
                or self.call_ledger is None
                or self.process_instance_fenced
            ):
                raise ValueError(
                    "completed outcome requires closed evidence and no fence"
                )
            if self.access_mode == "ATTACHED_OBSERVE" and (
                self.restoration_outcome != "VERIFIED_EQUAL"
                or self.pre_state_sha256 is None
                or self.pre_state_sha256 != self.post_state_sha256
            ):
                raise ValueError("attached completion requires equal pre/post state")
        if self.disposition in {"RESTORATION_UNVERIFIED", "TRANSACTION_UNCERTAIN"}:
            if not self.process_instance_fenced:
                raise ValueError("uncertain operation outcome must fence the instance")
        expected = _digest(self.model_dump(mode="json", exclude={"outcome_sha256"}))
        if self.outcome_sha256 != expected:
            raise ValueError("outcome_sha256 does not match canonical outcome")
        return self


def build_etabs_operation_outcome_v1(
    *,
    broker_result: ETABSBrokerResultV1,
    access_mode: Literal["ATTACHED_OBSERVE", "OWNED_COPY_MUTATION"],
    primary_outcome: Literal["COMPLETED", "BLOCKED", "ERROR", "TIMED_OUT"],
    restoration_outcome: Literal[
        "NOT_REQUIRED", "VERIFIED_EQUAL", "FAILED", "NOT_ATTEMPTED"
    ],
    deadline_seconds: float,
    call_ledger: ETABSCallLedgerIdentityV1 | None,
    pre_state_sha256: str | None = None,
    post_state_sha256: str | None = None,
    fence_reason: str | None = None,
) -> ETABSOperationOutcomeV1:
    """Derive fail-closed disposition from broker, evidence, and postflight state."""

    fenced = broker_result.process_instance_fenced or fence_reason is not None
    if broker_result.status == "TIMED_OUT" or (
        access_mode == "OWNED_COPY_MUTATION" and fenced
    ):
        disposition = (
            "TRANSACTION_UNCERTAIN"
            if access_mode == "OWNED_COPY_MUTATION"
            else "RESTORATION_UNVERIFIED"
        )
    elif fenced or restoration_outcome == "FAILED":
        disposition = "RESTORATION_UNVERIFIED"
    elif (
        primary_outcome == "COMPLETED"
        and broker_result.status == "COMPLETED"
        and call_ledger is not None
        and (
            access_mode != "ATTACHED_OBSERVE"
            or (
                restoration_outcome == "VERIFIED_EQUAL"
                and pre_state_sha256 is not None
                and pre_state_sha256 == post_state_sha256
            )
        )
    ):
        disposition = "COMPLETED"
    else:
        disposition = "BLOCKED"
    effective_fence_reason = fence_reason
    if fenced and effective_fence_reason is None:
        effective_fence_reason = broker_result.error or "RESTORATION_UNVERIFIED"
    basis = {
        "schema_version": "etabs-operation-outcome/v1",
        "transaction_id": broker_result.transaction_id,
        "access_mode": access_mode,
        "disposition": disposition,
        "primary_outcome": primary_outcome,
        "restoration_outcome": restoration_outcome,
        "broker_status": broker_result.status,
        "deadline_seconds": float(deadline_seconds),
        "process_instance_fenced": fenced,
        "pre_state_sha256": pre_state_sha256,
        "post_state_sha256": post_state_sha256,
        "call_ledger": (
            call_ledger.model_dump(mode="json") if call_ledger is not None else None
        ),
        "fence_reason": effective_fence_reason,
        "started_at_utc": _json_time(broker_result.started_at_utc),
        "completed_at_utc": _json_time(broker_result.completed_at_utc),
    }
    return ETABSOperationOutcomeV1.model_validate(
        {
            **basis,
            "call_ledger": call_ledger,
            "started_at_utc": broker_result.started_at_utc,
            "completed_at_utc": broker_result.completed_at_utc,
            "outcome_sha256": _digest(basis),
        }
    )


def _broker_entry(
    operation: Callable[..., Any],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    messages: Any,
    initialize_com: bool,
) -> None:
    comtypes_runtime: Any | None = None
    try:
        if initialize_com:
            comtypes_runtime = importlib.import_module("comtypes")
            comtypes_runtime.CoInitialize()
        messages.put(("STARTED", os.getpid(), datetime.now(UTC)))
        payload = operation(*args, **kwargs)
        messages.put(("RETURNED", payload, datetime.now(UTC)))
    except BaseException as exc:  # broker must report every worker failure
        error_text = (f"{type(exc).__name__}: {exc}\n{traceback.format_exc(limit=10)}")[
            :4000
        ]
        messages.put(
            (
                "ERROR",
                error_text,
                datetime.now(UTC),
            )
        )
    finally:
        if comtypes_runtime is not None:
            comtypes_runtime.CoUninitialize()


def run_etabs_sta_broker_v1(
    operation: Callable[..., Any],
    *,
    args: Sequence[Any] = (),
    kwargs: Mapping[str, Any] | None = None,
    deadline_seconds: float,
    lease: ETABSLeaseHandleV1,
    heartbeat_seconds: float = 0.25,
    initialize_com: bool = False,
) -> ETABSBrokerResultV1:
    """Run one operation in a supervised process and fence on timeout."""

    if not 0.05 <= deadline_seconds <= 300:
        raise ValueError("deadline_seconds must be within [0.05, 300]")
    if not 0.01 <= heartbeat_seconds <= min(deadline_seconds, 5):
        raise ValueError("heartbeat_seconds is outside the supported interval")
    context = multiprocessing.get_context("spawn")
    messages = context.Queue()
    worker = context.Process(
        target=_broker_entry,
        args=(operation, tuple(args), dict(kwargs or {}), messages, initialize_com),
        daemon=True,
    )
    started_at = datetime.now(UTC)
    deadline = time.monotonic() + deadline_seconds
    worker.start()
    worker_pid = worker.pid
    try:
        lease.heartbeat(observed_at_utc=started_at, worker_pid=worker_pid)
    except Exception:
        worker.terminate()
        worker.join(timeout=2)
        raise
    payload: Any | None = None
    error: str | None = None
    status: Literal["COMPLETED", "ERROR", "TIMED_OUT"] | None = None
    completed_at = started_at
    while time.monotonic() < deadline and status is None:
        remaining = deadline - time.monotonic()
        try:
            message = messages.get(timeout=min(heartbeat_seconds, remaining))
        except queue.Empty:
            try:
                lease.heartbeat(worker_pid=worker_pid)
            except Exception as exc:
                status = "ERROR"
                error = f"Lease heartbeat failed: {type(exc).__name__}: {exc}"
                completed_at = datetime.now(UTC)
                worker.terminate()
                worker.join(timeout=2)
                try:
                    lease.fence(
                        "RESTORATION_UNVERIFIED: LEASE_HEARTBEAT_FAILED",
                        observed_at_utc=completed_at,
                    )
                except Exception as fence_exc:
                    error += f" Fence failed: {type(fence_exc).__name__}: {fence_exc}"
            if status is None and not worker.is_alive() and worker.exitcode is not None:
                status = "ERROR"
                error = f"Broker exited with code {worker.exitcode} without a result."
                completed_at = datetime.now(UTC)
                lease.fence(
                    "RESTORATION_UNVERIFIED: BROKER_RESULT_UNAVAILABLE",
                    observed_at_utc=completed_at,
                )
            continue
        kind = message[0]
        if kind == "RETURNED":
            status = "COMPLETED"
            payload = message[1]
            completed_at = message[2]
        elif kind == "ERROR":
            status = "ERROR"
            error = str(message[1])
            completed_at = message[2]
    if status is None:
        status = "TIMED_OUT"
        completed_at = datetime.now(UTC)
        worker.terminate()
        worker.join(timeout=2)
        lease.fence(
            "RESTORATION_UNVERIFIED: BROKER_DEADLINE_EXPIRED",
            observed_at_utc=completed_at,
        )
    else:
        worker.join(timeout=2)
        if worker.is_alive():
            worker.terminate()
            worker.join(timeout=2)
            status = "ERROR"
            error = "Broker returned a message but did not terminate."
            completed_at = datetime.now(UTC)
            lease.fence(
                "RESTORATION_UNVERIFIED: BROKER_TERMINATION_UNVERIFIED",
                observed_at_utc=completed_at,
            )
    try:
        return ETABSBrokerResultV1(
            transaction_id=lease.lease.transaction_id,
            status=status,
            worker_pid=worker_pid,
            started_at_utc=started_at,
            completed_at_utc=completed_at,
            payload=payload,
            error=error,
            process_instance_fenced=lease.lease.disposition == "FENCED",
        )
    finally:
        messages.close()
        messages.join_thread()
