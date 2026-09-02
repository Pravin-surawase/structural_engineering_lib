"""Offline-first ETABS process, target, freshness, and result-epoch guard.

This module measures operating-system and file identities only.  Process
discovery never imports or creates an ETABS COM object; installed attachment is
owned by the separately authorized A1 packet.  Every live consumer must carry
the immutable values defined here and revalidate them before and after use.
"""

from __future__ import annotations

import hashlib
import hmac
import importlib.metadata
import json
import platform
import secrets
import shutil
import struct

# Security: subprocess is limited to the fixed OS process-inventory command below.
import subprocess  # nosec B404
import sys
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from pathlib import Path
from typing import Any, Literal, Protocol, Self

from pydantic import Field, model_validator

from structural_lib.core.version import get_runtime_version
from structural_lib.services.contracts.common import StrictPublicModel
from structural_lib.services.evidence import get_library_content_identity

__all__ = [
    "ETABSAccessModeV1",
    "ETABSBridgeCapabilityV1",
    "ETABSExpectedModelIntentV1",
    "ETABSFileIdentityV1",
    "ETABSInstalledReadOnlyPreflightV1",
    "ETABSModelFreshnessDispositionV1",
    "ETABSModelFreshnessV1",
    "ETABSProcessInstanceV1",
    "ETABSResultEpochDispositionV1",
    "ETABSResultEpochV1",
    "ETABSRuntimeArtifactV1",
    "ETABSRuntimeFingerprintV1",
    "ETABSSavedCheckpointV1",
    "ETABSSessionIdentityV1",
    "ETABSStateSnapshotV1",
    "ETABSTargetObservationV1",
    "ETABSAttachedStateReaderV1",
    "ProcessObservationV1",
    "build_etabs_result_epoch_v1",
    "build_etabs_runtime_fingerprint_v1",
    "build_etabs_saved_checkpoint_v1",
    "build_etabs_session_identity_v1",
    "capture_attached_etabs_state_v1",
    "capture_etabs_state_v1",
    "assess_attached_output_readiness_v1",
    "classify_etabs_model_freshness_v1",
    "compare_attached_etabs_state_v1",
    "discover_etabs_processes_v1",
    "file_identity_v1",
    "issue_etabs_bridge_capability_v1",
    "observe_etabs_target_v1",
    "preflight_installed_etabs_readonly_v1",
    "verify_etabs_bridge_capability_v1",
    "verify_etabs_target_observation_v1",
]


_SHA256_PATTERN = r"^[0-9a-f]{64}$"
_UTC = UTC
_DEFAULT_TARGET_TTL = timedelta(minutes=2)
_DEFAULT_CAPABILITY_TTL = timedelta(seconds=45)


def _utc(value: datetime, name: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(_UTC)


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


def _model_digest(
    model: StrictPublicModel,
    digest_field: str,
    *,
    exclude: frozenset[str] = frozenset(),
) -> str:
    return _digest(model.model_dump(mode="json", exclude={digest_field, *exclude}))


def _require_digest(
    model: StrictPublicModel,
    digest_field: str,
    *,
    exclude: frozenset[str] = frozenset(),
) -> None:
    actual = str(getattr(model, digest_field))
    expected = _model_digest(model, digest_field, exclude=exclude)
    if not hmac.compare_digest(actual, expected):
        raise ValueError(f"{digest_field} does not match the canonical payload")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class ETABSAccessModeV1(StrEnum):
    """Closed live-access modes; attached observation is always getter-only."""

    ATTACHED_OBSERVE = "ATTACHED_OBSERVE"
    OWNED_COPY_MUTATION = "OWNED_COPY_MUTATION"


class ETABSModelFreshnessDispositionV1(StrEnum):
    SAVED_CLEAN_CONFIRMED = "SAVED_CLEAN_CONFIRMED"
    SESSION_UNSAVED_OR_UNKNOWN = "SESSION_UNSAVED_OR_UNKNOWN"
    FILE_DRIFT = "FILE_DRIFT"
    FILE_UNAVAILABLE = "FILE_UNAVAILABLE"


class ETABSResultEpochDispositionV1(StrEnum):
    ACCEPTED = "ACCEPTED"
    BLOCKED = "BLOCKED"


ETABSRuntimeArtifactNameV1 = Literal[
    "ETABS_EXECUTABLE",
    "ETABSV1_TYPE_LIBRARY",
    "COMTYPES_GENERATED_WRAPPER",
    "MANAGED_ASSEMBLY",
    "INSTALLED_CHM",
]


class ETABSFileIdentityV1(StrictPublicModel):
    """One immutable saved-file observation."""

    canonical_path: str = Field(min_length=1, max_length=1024)
    size_bytes: int = Field(ge=0)
    modified_at_utc: datetime
    sha256: str = Field(pattern=_SHA256_PATTERN)

    @model_validator(mode="after")
    def validate_time(self) -> Self:
        _utc(self.modified_at_utc, "modified_at_utc")
        return self


class ProcessObservationV1(StrictPublicModel):
    """Raw OS process row used by the pure discovery builder."""

    pid: int = Field(gt=0)
    start_time_utc: datetime
    executable_path: str = Field(min_length=1, max_length=1024)
    executable_version: str = Field(min_length=1, max_length=240)
    architecture: Literal["x86", "x86_64", "arm64", "unknown"]

    @model_validator(mode="after")
    def validate_time(self) -> Self:
        _utc(self.start_time_utc, "start_time_utc")
        return self


class ETABSProcessInstanceV1(StrictPublicModel):
    """PID-reuse-resistant ETABS process identity measured without COM."""

    schema_version: Literal["etabs-process-instance/v1"] = "etabs-process-instance/v1"
    pid: int = Field(gt=0)
    start_time_utc: datetime
    canonical_executable_path: str = Field(min_length=1, max_length=1024)
    executable_version: str = Field(min_length=1, max_length=240)
    executable_sha256: str = Field(pattern=_SHA256_PATTERN)
    architecture: Literal["x86", "x86_64", "arm64", "unknown"]
    observed_at_utc: datetime
    instance_sha256: str = Field(pattern=_SHA256_PATTERN)

    @model_validator(mode="after")
    def validate_identity(self) -> Self:
        start = _utc(self.start_time_utc, "start_time_utc")
        observed = _utc(self.observed_at_utc, "observed_at_utc")
        if observed < start:
            raise ValueError("observed_at_utc must not precede process start")
        _require_digest(
            self,
            "instance_sha256",
            exclude=frozenset({"observed_at_utc"}),
        )
        return self


class ETABSRuntimeArtifactV1(StrictPublicModel):
    """Measured runtime/support artifact, including explicit absence."""

    name: ETABSRuntimeArtifactNameV1
    disposition: Literal["PRESENT", "UNAVAILABLE", "NOT_USED"]
    canonical_path: str | None = Field(default=None, max_length=1024)
    version: str | None = Field(default=None, max_length=240)
    sha256: str | None = Field(default=None, pattern=_SHA256_PATTERN)
    limitation: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_disposition(self) -> Self:
        if self.disposition == "PRESENT":
            if not self.canonical_path or not self.sha256:
                raise ValueError("PRESENT runtime artifacts require path and sha256")
        elif self.canonical_path is not None or self.sha256 is not None:
            raise ValueError("absent runtime artifacts cannot carry path or sha256")
        if self.disposition == "UNAVAILABLE" and not self.limitation:
            raise ValueError("UNAVAILABLE runtime artifacts require a limitation")
        return self


class ETABSRuntimeFingerprintV1(StrictPublicModel):
    """Measured bridge/Python/COM-shape/installed runtime identity."""

    schema_version: Literal["etabs-runtime-fingerprint/v1"] = (
        "etabs-runtime-fingerprint/v1"
    )
    library_version: str = Field(min_length=1, max_length=80)
    library_content_sha256: str = Field(pattern=_SHA256_PATTERN)
    python_executable: str = Field(min_length=1, max_length=1024)
    python_version: str = Field(min_length=1, max_length=160)
    python_architecture: str = Field(min_length=1, max_length=80)
    com_shape_runtime: Literal["comtypes", "managed-wrapper", "unavailable"]
    comtypes_version: str | None = Field(default=None, max_length=80)
    process_instance_sha256: str = Field(pattern=_SHA256_PATTERN)
    artifacts: tuple[ETABSRuntimeArtifactV1, ...]
    observed_at_utc: datetime
    fingerprint_sha256: str = Field(pattern=_SHA256_PATTERN)

    @model_validator(mode="after")
    def validate_identity(self) -> Self:
        _utc(self.observed_at_utc, "observed_at_utc")
        names = [artifact.name for artifact in self.artifacts]
        if len(names) != len(set(names)):
            raise ValueError("runtime artifact names must be unique")
        executable = [
            artifact
            for artifact in self.artifacts
            if artifact.name == "ETABS_EXECUTABLE"
        ]
        if len(executable) != 1 or executable[0].disposition != "PRESENT":
            raise ValueError("runtime fingerprint requires one ETABS executable")
        if self.com_shape_runtime == "comtypes" and not self.comtypes_version:
            raise ValueError("comtypes runtime requires its installed version")
        _require_digest(
            self,
            "fingerprint_sha256",
            exclude=frozenset({"observed_at_utc"}),
        )
        return self


class ETABSExpectedModelIntentV1(StrictPublicModel):
    """Operator-selected target intent; never process authority by itself."""

    expected_model_path: str | None = Field(default=None, max_length=1024)
    expected_model_name: str | None = Field(default=None, max_length=260)
    expected_etabs_version: str | None = Field(default=None, max_length=240)
    allowed_access: ETABSAccessModeV1 = Field(strict=False)


class ETABSSessionIdentityV1(StrictPublicModel):
    """Visible model/session identity returned by a separately invoked probe."""

    schema_version: Literal["etabs-session-identity/v1"] = "etabs-session-identity/v1"
    process_instance_sha256: str = Field(pattern=_SHA256_PATTERN)
    connection_origin: Literal["ATTACHED_EXISTING", "STARTED_OWNED"]
    model_name: str = Field(min_length=1, max_length=260)
    model_path: str | None = Field(default=None, max_length=1024)
    etabs_version: str = Field(min_length=1, max_length=240)
    present_units: str = Field(min_length=1, max_length=120)
    model_locked: bool
    saved_file_identity: ETABSFileIdentityV1 | None = None
    observed_at_utc: datetime
    session_sha256: str = Field(pattern=_SHA256_PATTERN)

    @model_validator(mode="after")
    def validate_identity(self) -> Self:
        _utc(self.observed_at_utc, "observed_at_utc")
        if self.saved_file_identity is not None:
            if self.model_path != self.saved_file_identity.canonical_path:
                raise ValueError(
                    "saved file identity must match the visible model path"
                )
        _require_digest(
            self,
            "session_sha256",
            exclude=frozenset({"observed_at_utc"}),
        )
        return self


class ETABSSavedCheckpointV1(StrictPublicModel):
    """Operator/API save receipt bound to one process, session, and file."""

    schema_version: Literal["etabs-saved-checkpoint/v1"] = "etabs-saved-checkpoint/v1"
    process_instance_sha256: str = Field(pattern=_SHA256_PATTERN)
    session_sha256: str = Field(pattern=_SHA256_PATTERN)
    file_identity: ETABSFileIdentityV1
    saved_at_utc: datetime
    observed_at_utc: datetime
    save_call_id: str = Field(min_length=1, max_length=120)
    checkpoint_sha256: str = Field(pattern=_SHA256_PATTERN)

    @model_validator(mode="after")
    def validate_checkpoint(self) -> Self:
        saved = _utc(self.saved_at_utc, "saved_at_utc")
        observed = _utc(self.observed_at_utc, "observed_at_utc")
        if saved > observed:
            raise ValueError("saved checkpoint observation cannot precede save")
        if self.file_identity.modified_at_utc > observed:
            raise ValueError("saved file timestamp cannot follow its observation")
        _require_digest(self, "checkpoint_sha256")
        return self


class ETABSModelFreshnessV1(StrictPublicModel):
    """Separate live-session versus persisted-file freshness disposition."""

    schema_version: Literal["etabs-model-freshness/v1"] = "etabs-model-freshness/v1"
    disposition: ETABSModelFreshnessDispositionV1 = Field(strict=False)
    process_instance_sha256: str = Field(pattern=_SHA256_PATTERN)
    session_sha256: str = Field(pattern=_SHA256_PATTERN)
    observation_source: Literal[
        "ATTACHED_DEFAULT",
        "API_CLEAN_SIGNAL",
        "OPERATOR_SAVED_CHECKPOINT",
        "FILE_COMPARISON",
    ]
    session_model_path: str | None = Field(default=None, max_length=1024)
    before_file: ETABSFileIdentityV1 | None = None
    after_file: ETABSFileIdentityV1 | None = None
    api_clean_signal_call_id: str | None = Field(default=None, max_length=120)
    saved_checkpoint: ETABSSavedCheckpointV1 | None = None
    observed_at_utc: datetime
    hash_bound_baseline_allowed: bool
    limitations: tuple[str, ...]

    @model_validator(mode="after")
    def validate_disposition(self) -> Self:
        observed = _utc(self.observed_at_utc, "observed_at_utc")
        if self.disposition is ETABSModelFreshnessDispositionV1.SAVED_CLEAN_CONFIRMED:
            if self.observation_source == "ATTACHED_DEFAULT":
                raise ValueError("attached default cannot prove a saved clean model")
            if self.before_file is None or self.after_file is None:
                raise ValueError("saved clean confirmation requires before/after files")
            if self.before_file != self.after_file:
                raise ValueError(
                    "saved clean confirmation requires equal file identities"
                )
            if not self.hash_bound_baseline_allowed:
                raise ValueError("saved clean confirmation must allow a hash baseline")
            if self.observation_source == "API_CLEAN_SIGNAL":
                if (
                    not self.api_clean_signal_call_id
                    or self.saved_checkpoint is not None
                ):
                    raise ValueError("API cleanliness requires one call identity only")
            elif self.observation_source == "OPERATOR_SAVED_CHECKPOINT":
                checkpoint = self.saved_checkpoint
                if checkpoint is None or self.api_clean_signal_call_id is not None:
                    raise ValueError("saved cleanliness requires one checkpoint only")
                if (
                    checkpoint.process_instance_sha256 != self.process_instance_sha256
                    or checkpoint.session_sha256 != self.session_sha256
                    or checkpoint.file_identity != self.after_file
                    or checkpoint.observed_at_utc > observed
                ):
                    raise ValueError(
                        "saved checkpoint is not bound to this observation"
                    )
        elif self.hash_bound_baseline_allowed:
            raise ValueError("only SAVED_CLEAN_CONFIRMED permits a hash baseline")
        elif (
            self.api_clean_signal_call_id is not None
            or self.saved_checkpoint is not None
        ):
            raise ValueError("non-clean freshness cannot carry clean evidence")
        if not self.limitations:
            raise ValueError("freshness must publish at least one limitation")
        return self


class ETABSTargetObservationV1(StrictPublicModel):
    """Short-lived, exact process/runtime/model observation."""

    schema_version: Literal["etabs-target-observation/v1"] = (
        "etabs-target-observation/v1"
    )
    observation_id: str = Field(min_length=1, max_length=120)
    process_instance: ETABSProcessInstanceV1
    expected_intent: ETABSExpectedModelIntentV1
    session_identity: ETABSSessionIdentityV1
    runtime_fingerprint: ETABSRuntimeFingerprintV1
    model_freshness: ETABSModelFreshnessV1
    allowed_access: ETABSAccessModeV1 = Field(strict=False)
    observed_at_utc: datetime
    expires_at_utc: datetime
    observation_sha256: str = Field(pattern=_SHA256_PATTERN)

    @model_validator(mode="after")
    def validate_binding(self) -> Self:
        observed = _utc(self.observed_at_utc, "observed_at_utc")
        expires = _utc(self.expires_at_utc, "expires_at_utc")
        if expires <= observed:
            raise ValueError("target observation must expire after observation")
        if self.allowed_access is not self.expected_intent.allowed_access:
            raise ValueError("allowed access must match the selected intent")
        if self.session_identity.process_instance_sha256 != (
            self.process_instance.instance_sha256
        ):
            raise ValueError("session identity is bound to another process instance")
        if self.runtime_fingerprint.process_instance_sha256 != (
            self.process_instance.instance_sha256
        ):
            raise ValueError("runtime fingerprint is bound to another process instance")
        if (
            self.model_freshness.process_instance_sha256
            != self.process_instance.instance_sha256
            or self.model_freshness.session_sha256
            != self.session_identity.session_sha256
        ):
            raise ValueError("model freshness is bound to another process/session")
        nested_observations = (
            self.process_instance.observed_at_utc,
            self.runtime_fingerprint.observed_at_utc,
            self.session_identity.observed_at_utc,
            self.model_freshness.observed_at_utc,
        )
        if any(value > observed for value in nested_observations):
            raise ValueError("target observation cannot precede nested observations")
        _require_digest(self, "observation_sha256")
        return self


class ETABSInstalledReadOnlyPreflightV1(StrictPublicModel):
    """No-COM decision for one exact installed getter-only attachment target."""

    schema_version: Literal["etabs-installed-readonly-preflight/v1"] = (
        "etabs-installed-readonly-preflight/v1"
    )
    disposition: Literal["READY_FOR_GETTER_ONLY_ATTACH", "HOLD"]
    selected_pid: int | None = Field(default=None, gt=0)
    selected_start_time_utc: datetime | None = None
    expected_intent: ETABSExpectedModelIntentV1
    discovered_processes: tuple[ETABSProcessInstanceV1, ...]
    selected_process: ETABSProcessInstanceV1 | None = None
    runtime_fingerprint: ETABSRuntimeFingerprintV1 | None = None
    observed_at_utc: datetime
    blocked_reasons: tuple[str, ...] = ()
    preflight_sha256: str = Field(pattern=_SHA256_PATTERN)

    @model_validator(mode="after")
    def validate_preflight(self) -> Self:
        _utc(self.observed_at_utc, "observed_at_utc")
        if self.selected_start_time_utc is not None:
            _utc(self.selected_start_time_utc, "selected_start_time_utc")
        identities = tuple(
            (process.start_time_utc, process.pid, process.instance_sha256)
            for process in self.discovered_processes
        )
        if identities != tuple(sorted(identities)):
            raise ValueError("discovered processes must retain deterministic order")
        if len(identities) != len(set(identities)):
            raise ValueError("discovered process identities must be unique")
        if len(self.blocked_reasons) != len(set(self.blocked_reasons)):
            raise ValueError("blocked reasons must be unique")
        if (
            self.expected_intent.allowed_access
            is not ETABSAccessModeV1.ATTACHED_OBSERVE
        ):
            raise ValueError(
                "installed read-only preflight requires attached observation"
            )
        if self.disposition == "READY_FOR_GETTER_ONLY_ATTACH":
            if self.blocked_reasons:
                raise ValueError("ready preflight cannot carry blocked reasons")
            if (
                self.selected_pid is None
                or self.selected_start_time_utc is None
                or self.selected_process is None
                or self.runtime_fingerprint is None
            ):
                raise ValueError(
                    "ready preflight requires exact process/runtime identity"
                )
            if (
                self.expected_intent.expected_model_path is None
                or self.expected_intent.expected_model_name is None
                or self.expected_intent.expected_etabs_version is None
            ):
                raise ValueError("ready preflight requires exact model intent")
            if (
                self.selected_process.pid != self.selected_pid
                or self.selected_process.start_time_utc != self.selected_start_time_utc
            ):
                raise ValueError("selected process differs from the requested instance")
            if self.selected_process not in self.discovered_processes:
                raise ValueError("selected process is absent from discovery")
            if self.runtime_fingerprint.process_instance_sha256 != (
                self.selected_process.instance_sha256
            ):
                raise ValueError("runtime fingerprint is bound to another process")
        else:
            if not self.blocked_reasons:
                raise ValueError("held preflight requires blocked reasons")
            if (
                self.selected_process is not None
                or self.runtime_fingerprint is not None
            ):
                raise ValueError("held preflight cannot authorize a process/runtime")
        _require_digest(self, "preflight_sha256")
        return self


class ETABSBridgeCapabilityV1(StrictPublicModel):
    """Server-issued, expiring target/access/transaction capability."""

    schema_version: Literal["etabs-bridge-capability/v1"] = "etabs-bridge-capability/v1"
    capability_id: str = Field(min_length=1, max_length=120)
    target_observation_sha256: str = Field(pattern=_SHA256_PATTERN)
    process_instance_sha256: str = Field(pattern=_SHA256_PATTERN)
    transaction_id: str = Field(min_length=1, max_length=120)
    allowed_access: ETABSAccessModeV1 = Field(strict=False)
    single_use: bool
    issued_at_utc: datetime
    expires_at_utc: datetime
    nonce: str = Field(min_length=16, max_length=128)
    signature_sha256: str = Field(pattern=_SHA256_PATTERN)

    @model_validator(mode="after")
    def validate_expiry(self) -> Self:
        issued = _utc(self.issued_at_utc, "issued_at_utc")
        expires = _utc(self.expires_at_utc, "expires_at_utc")
        if expires <= issued:
            raise ValueError("capability must expire after issuance")
        if self.allowed_access is ETABSAccessModeV1.OWNED_COPY_MUTATION:
            if not self.single_use:
                raise ValueError("mutation capability must be single-use")
        return self


class ETABSStateSnapshotV1(StrictPublicModel):
    """Declared getter-only state captured before/after an operation."""

    schema_version: Literal["etabs-state-snapshot/v1"] = "etabs-state-snapshot/v1"
    session_sha256: str = Field(pattern=_SHA256_PATTERN)
    present_units: str = Field(min_length=1, max_length=120)
    model_locked: bool
    selected_output_cases: tuple[str, ...]
    selected_output_combinations: tuple[str, ...]
    case_statuses: tuple[tuple[str, str], ...]
    run_flags: tuple[tuple[str, bool], ...]
    table_display_selection_sha256: str | None = Field(
        default=None, pattern=_SHA256_PATTERN
    )
    observed_at_utc: datetime
    state_sha256: str = Field(pattern=_SHA256_PATTERN)

    @model_validator(mode="after")
    def validate_state(self) -> Self:
        _utc(self.observed_at_utc, "observed_at_utc")
        for values, name in (
            (self.selected_output_cases, "selected_output_cases"),
            (self.selected_output_combinations, "selected_output_combinations"),
        ):
            if tuple(sorted(set(values))) != values:
                raise ValueError(f"{name} must be unique and sorted")
        for keys, name in (
            (tuple(key for key, _value in self.case_statuses), "case_statuses"),
            (tuple(key for key, _value in self.run_flags), "run_flags"),
        ):
            if tuple(sorted(set(keys))) != keys:
                raise ValueError(f"{name} keys must be unique and sorted")
        _require_digest(self, "state_sha256")
        return self


class ETABSResultEpochV1(StrictPublicModel):
    """Evidence that results belong to one uninterrupted model transaction."""

    schema_version: Literal["etabs-result-epoch/v1"] = "etabs-result-epoch/v1"
    disposition: ETABSResultEpochDispositionV1 = Field(strict=False)
    model_identity_sha256: str = Field(pattern=_SHA256_PATTERN)
    copy_identity_sha256: str | None = Field(default=None, pattern=_SHA256_PATTERN)
    change_set_sha256: str | None = Field(default=None, pattern=_SHA256_PATTERN)
    runtime_fingerprint_sha256: str = Field(pattern=_SHA256_PATTERN)
    process_instance_sha256: str = Field(pattern=_SHA256_PATTERN)
    transaction_id: str = Field(min_length=1, max_length=120)
    uninterrupted_process: bool
    uninterrupted_runtime: bool
    authorized_cases: tuple[str, ...]
    case_dependency_closure: tuple[str, ...]
    pre_statuses: tuple[tuple[str, str], ...]
    post_statuses: tuple[tuple[str, str], ...]
    run_flags: tuple[tuple[str, bool], ...]
    analysis_call_ids: tuple[str, ...]
    design_call_ids: tuple[str, ...]
    selection_sha256: str = Field(pattern=_SHA256_PATTERN)
    result_sha256: str = Field(pattern=_SHA256_PATTERN)
    design_basis_sha256: str | None = Field(default=None, pattern=_SHA256_PATTERN)
    observed_at_utc: datetime
    blocked_reasons: tuple[str, ...] = ()
    epoch_sha256: str = Field(pattern=_SHA256_PATTERN)

    @model_validator(mode="after")
    def validate_epoch(self) -> Self:
        _utc(self.observed_at_utc, "observed_at_utc")
        for values, name in (
            (self.authorized_cases, "authorized_cases"),
            (self.case_dependency_closure, "case_dependency_closure"),
            (self.analysis_call_ids, "analysis_call_ids"),
            (self.design_call_ids, "design_call_ids"),
            (self.blocked_reasons, "blocked_reasons"),
        ):
            if len(values) != len(set(values)):
                raise ValueError(f"{name} must be unique")
        closure = set(self.case_dependency_closure)
        status_domains = (
            {name for name, _status in self.pre_statuses},
            {name for name, _status in self.post_statuses},
            {name for name, _flag in self.run_flags},
        )
        if self.disposition is ETABSResultEpochDispositionV1.ACCEPTED:
            if not self.authorized_cases:
                raise ValueError("accepted result epoch requires authorized cases")
            if not set(self.authorized_cases).issubset(closure):
                raise ValueError(
                    "accepted epoch case closure must contain authorized cases"
                )
            if any(domain != closure for domain in status_domains):
                raise ValueError("accepted epoch status/run domains must equal closure")
            if any(status != "FINISHED" for _name, status in self.post_statuses):
                raise ValueError("accepted epoch post statuses must be FINISHED")
            if any(not flag for _name, flag in self.run_flags):
                raise ValueError("accepted epoch run flags must all be enabled")
            if not self.analysis_call_ids:
                raise ValueError("accepted epoch requires analysis call evidence")
            if self.design_basis_sha256 is not None and not self.design_call_ids:
                raise ValueError("design result epoch requires design call evidence")
            if not self.uninterrupted_process or not self.uninterrupted_runtime:
                raise ValueError("accepted result epoch must be uninterrupted")
            if self.blocked_reasons:
                raise ValueError("accepted result epoch cannot carry blocked reasons")
        elif not self.blocked_reasons:
            raise ValueError("blocked result epoch requires reasons")
        _require_digest(self, "epoch_sha256")
        return self


class ETABSSessionProbeV1(Protocol):
    """Getter-only A1 adapter shape consumed by the offline observation builder."""

    def read_session_identity(
        self, process_instance: ETABSProcessInstanceV1, observed_at_utc: datetime
    ) -> ETABSSessionIdentityV1: ...


class ETABSAttachedStateReaderV1(Protocol):
    """Getter-only state surface permitted for an attached user session."""

    def get_present_units(self) -> str: ...

    def get_model_locked(self) -> bool: ...

    def get_selected_output_cases(self) -> Sequence[str]: ...

    def get_selected_output_combinations(self) -> Sequence[str]: ...

    def get_case_statuses(self) -> Mapping[str, str]: ...

    def get_run_flags(self) -> Mapping[str, bool]: ...

    def get_table_display_selection_sha256(self) -> str | None: ...


ProcessProviderV1 = Callable[[], Sequence[ProcessObservationV1]]


def file_identity_v1(path: str | Path) -> ETABSFileIdentityV1:
    """Measure one existing regular file without opening an application."""

    resolved = Path(path).resolve(strict=True)
    if not resolved.is_file():
        raise ValueError(f"expected a regular file: {resolved}")
    stat = resolved.stat()
    return ETABSFileIdentityV1(
        canonical_path=str(resolved),
        size_bytes=stat.st_size,
        modified_at_utc=datetime.fromtimestamp(stat.st_mtime, tz=_UTC),
        sha256=_sha256_file(resolved),
    )


def _pe_architecture(path: Path) -> Literal["x86", "x86_64", "arm64", "unknown"]:
    try:
        with path.open("rb") as handle:
            handle.seek(0x3C)
            pe_offset = struct.unpack("<I", handle.read(4))[0]
            handle.seek(pe_offset)
            if handle.read(4) != b"PE\x00\x00":
                return "unknown"
            machine = struct.unpack("<H", handle.read(2))[0]
    except (OSError, struct.error):
        return "unknown"
    architectures: dict[int, Literal["x86", "x86_64", "arm64", "unknown"]] = {
        0x014C: "x86",
        0x8664: "x86_64",
        0xAA64: "arm64",
    }
    return architectures.get(machine, "unknown")


def _windows_etabs_processes() -> tuple[ProcessObservationV1, ...]:
    if platform.system() != "Windows":
        return ()
    command = (
        "$ErrorActionPreference='Stop';"
        "$items=@(Get-Process -Name ETABS -ErrorAction SilentlyContinue | "
        "ForEach-Object {[PSCustomObject]@{pid=$_.Id;"
        "start_time_utc=$_.StartTime.ToUniversalTime().ToString('o');"
        "executable_path=$_.Path;"
        "executable_version=$_.MainModule.FileVersionInfo.FileVersion}});"
        "$items | ConvertTo-Json -Compress"
    )
    powershell = shutil.which("powershell.exe")
    if powershell is None:
        raise RuntimeError("PowerShell is required for Windows process discovery")
    # The absolute executable and command are fixed; no request data reaches the shell.
    completed = subprocess.run(  # nosec B603
        [powershell, "-NoProfile", "-NonInteractive", "-Command", command],
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    )
    raw = completed.stdout.strip()
    if not raw:
        return ()
    payload = json.loads(raw)
    rows = payload if isinstance(payload, list) else [payload]
    observations: list[ProcessObservationV1] = []
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError("ETABS process discovery returned a non-object row")
        path = Path(str(row["executable_path"])).resolve(strict=True)
        observations.append(
            ProcessObservationV1(
                pid=int(row["pid"]),
                start_time_utc=datetime.fromisoformat(str(row["start_time_utc"])),
                executable_path=str(path),
                executable_version=str(row["executable_version"]),
                architecture=_pe_architecture(path),
            )
        )
    return tuple(observations)


def discover_etabs_processes_v1(
    *,
    process_provider: ProcessProviderV1 | None = None,
    observed_at_utc: datetime | None = None,
) -> tuple[ETABSProcessInstanceV1, ...]:
    """Return deterministic PID/start-time identities without importing COM."""

    observed = _utc(observed_at_utc or datetime.now(_UTC), "observed_at_utc")
    provider = process_provider or _windows_etabs_processes
    candidates: list[ETABSProcessInstanceV1] = []
    seen: set[tuple[int, datetime]] = set()
    for row in provider():
        if not isinstance(row, ProcessObservationV1):
            raise TypeError("process_provider must return ProcessObservationV1 values")
        key = (row.pid, row.start_time_utc)
        if key in seen:
            raise ValueError("process provider returned a duplicate PID/start time")
        seen.add(key)
        executable = Path(row.executable_path).resolve(strict=True)
        if not executable.is_file():
            raise ValueError(f"ETABS executable is not a regular file: {executable}")
        basis = {
            "schema_version": "etabs-process-instance/v1",
            "pid": row.pid,
            "start_time_utc": _json_time(row.start_time_utc),
            "canonical_executable_path": str(executable),
            "executable_version": row.executable_version,
            "executable_sha256": _sha256_file(executable),
            "architecture": row.architecture,
            "observed_at_utc": _json_time(observed),
        }
        identity_basis = {
            key: value for key, value in basis.items() if key != "observed_at_utc"
        }
        candidates.append(
            ETABSProcessInstanceV1.model_validate(
                {
                    **basis,
                    "start_time_utc": row.start_time_utc,
                    "observed_at_utc": observed,
                    "instance_sha256": _digest(identity_basis),
                }
            )
        )
    return tuple(
        sorted(
            candidates,
            key=lambda item: (
                item.start_time_utc,
                item.pid,
                item.canonical_executable_path.casefold(),
            ),
        )
    )


def _runtime_artifact(
    name: ETABSRuntimeArtifactNameV1,
    path: str | Path | None,
    *,
    version: str | None = None,
    not_used: bool = False,
) -> ETABSRuntimeArtifactV1:
    if not_used:
        return ETABSRuntimeArtifactV1(name=name, disposition="NOT_USED")
    if path is None:
        return ETABSRuntimeArtifactV1(
            name=name,
            disposition="UNAVAILABLE",
            limitation=f"{name} was not resolved by the runtime probe.",
        )
    try:
        identity = file_identity_v1(path)
    except (FileNotFoundError, OSError, ValueError) as exc:
        return ETABSRuntimeArtifactV1(
            name=name,
            disposition="UNAVAILABLE",
            limitation=f"{name} could not be measured: {exc}",
        )
    return ETABSRuntimeArtifactV1(
        name=name,
        disposition="PRESENT",
        canonical_path=identity.canonical_path,
        version=version,
        sha256=identity.sha256,
    )


def build_etabs_runtime_fingerprint_v1(
    process_instance: ETABSProcessInstanceV1,
    *,
    type_library_path: str | Path | None = None,
    generated_wrapper_path: str | Path | None = None,
    managed_assembly_path: str | Path | None = None,
    installed_chm_path: str | Path | None = None,
    com_shape_runtime: Literal[
        "comtypes", "managed-wrapper", "unavailable"
    ] = "comtypes",
    observed_at_utc: datetime | None = None,
) -> ETABSRuntimeFingerprintV1:
    """Measure runtime artifacts; callers supply paths, never trusted hashes."""

    if not isinstance(process_instance, ETABSProcessInstanceV1):
        raise TypeError("process_instance must be ETABSProcessInstanceV1")
    observed = _utc(observed_at_utc or datetime.now(_UTC), "observed_at_utc")
    try:
        comtypes_version = importlib.metadata.version("comtypes")
    except importlib.metadata.PackageNotFoundError:
        comtypes_version = None
    if com_shape_runtime == "comtypes" and comtypes_version is None:
        raise RuntimeError("comtypes runtime was selected but is not installed")
    artifacts = (
        ETABSRuntimeArtifactV1(
            name="ETABS_EXECUTABLE",
            disposition="PRESENT",
            canonical_path=process_instance.canonical_executable_path,
            version=process_instance.executable_version,
            sha256=process_instance.executable_sha256,
        ),
        _runtime_artifact("ETABSV1_TYPE_LIBRARY", type_library_path),
        _runtime_artifact(
            "COMTYPES_GENERATED_WRAPPER",
            generated_wrapper_path,
            not_used=com_shape_runtime != "comtypes",
        ),
        _runtime_artifact(
            "MANAGED_ASSEMBLY",
            managed_assembly_path,
            not_used=com_shape_runtime != "managed-wrapper",
        ),
        _runtime_artifact("INSTALLED_CHM", installed_chm_path),
    )
    basis = {
        "schema_version": "etabs-runtime-fingerprint/v1",
        "library_version": get_runtime_version(),
        "library_content_sha256": get_library_content_identity(),
        "python_executable": str(Path(sys.executable).resolve()),
        "python_version": platform.python_version(),
        "python_architecture": platform.machine() or "unknown",
        "com_shape_runtime": com_shape_runtime,
        "comtypes_version": comtypes_version,
        "process_instance_sha256": process_instance.instance_sha256,
        "artifacts": [artifact.model_dump(mode="json") for artifact in artifacts],
        "observed_at_utc": _json_time(observed),
    }
    identity_basis = {
        key: value for key, value in basis.items() if key != "observed_at_utc"
    }
    return ETABSRuntimeFingerprintV1.model_validate(
        {
            **basis,
            "artifacts": artifacts,
            "observed_at_utc": observed,
            "fingerprint_sha256": _digest(identity_basis),
        }
    )


def preflight_installed_etabs_readonly_v1(
    expected_intent: ETABSExpectedModelIntentV1,
    /,
    *,
    selected_pid: int | None,
    selected_start_time_utc: datetime | None,
    type_library_path: str | Path | None = None,
    generated_wrapper_path: str | Path | None = None,
    installed_chm_path: str | Path | None = None,
    process_provider: ProcessProviderV1 | None = None,
    observed_at_utc: datetime | None = None,
) -> ETABSInstalledReadOnlyPreflightV1:
    """Fail closed before COM unless one exact attached target is selectable."""

    if expected_intent.allowed_access is not ETABSAccessModeV1.ATTACHED_OBSERVE:
        raise ValueError("installed read-only preflight requires attached observation")
    observed = _utc(observed_at_utc or datetime.now(_UTC), "observed_at_utc")
    processes = discover_etabs_processes_v1(
        process_provider=process_provider,
        observed_at_utc=observed,
    )
    reasons: list[str] = []
    selected: ETABSProcessInstanceV1 | None = None
    normalized_selected_start = (
        _utc(selected_start_time_utc, "selected_start_time_utc")
        if selected_start_time_utc is not None
        else None
    )

    if not processes:
        reasons.append("NO_ETABS_PROCESS_RUNNING")
    if selected_pid is None or normalized_selected_start is None:
        reasons.append("EXACT_PROCESS_SELECTION_MISSING")
    else:
        selected = next(
            (
                process
                for process in processes
                if process.pid == selected_pid
                and process.start_time_utc == normalized_selected_start
            ),
            None,
        )
        if selected is None:
            if any(process.pid == selected_pid for process in processes):
                reasons.append("SELECTED_PROCESS_START_TIME_MISMATCH")
            elif processes:
                reasons.append("SELECTED_PROCESS_NOT_RUNNING")

    if expected_intent.expected_model_path is None:
        reasons.append("EXPECTED_MODEL_PATH_MISSING")
    else:
        expected_path = Path(expected_intent.expected_model_path).resolve(strict=False)
        if not expected_path.is_file():
            reasons.append("EXPECTED_MODEL_FILE_NOT_AVAILABLE")
        if (
            expected_intent.expected_model_name is not None
            and expected_path.name.casefold()
            != expected_intent.expected_model_name.casefold()
        ):
            reasons.append("EXPECTED_MODEL_NAME_PATH_MISMATCH")
    if expected_intent.expected_model_name is None:
        reasons.append("EXPECTED_MODEL_NAME_MISSING")
    if expected_intent.expected_etabs_version is None:
        reasons.append("EXPECTED_ETABS_VERSION_MISSING")

    runtime: ETABSRuntimeFingerprintV1 | None = None
    disposition: Literal["READY_FOR_GETTER_ONLY_ATTACH", "HOLD"] = "HOLD"
    if not reasons:
        if selected is None:  # pragma: no cover - guarded by the reasons above
            raise RuntimeError("exact selected process was not resolved")
        runtime = build_etabs_runtime_fingerprint_v1(
            selected,
            type_library_path=type_library_path,
            generated_wrapper_path=generated_wrapper_path,
            installed_chm_path=installed_chm_path,
            com_shape_runtime="comtypes",
            observed_at_utc=observed,
        )
        required_artifacts = {
            "ETABSV1_TYPE_LIBRARY",
            "COMTYPES_GENERATED_WRAPPER",
            "INSTALLED_CHM",
        }
        unavailable = {
            artifact.name
            for artifact in runtime.artifacts
            if artifact.name in required_artifacts and artifact.disposition != "PRESENT"
        }
        reasons.extend(f"{name}_UNAVAILABLE" for name in sorted(unavailable))
    blocked_reasons = tuple(sorted(set(reasons)))
    if not blocked_reasons:
        disposition = "READY_FOR_GETTER_ONLY_ATTACH"
    else:
        runtime = None

    basis = {
        "schema_version": "etabs-installed-readonly-preflight/v1",
        "disposition": disposition,
        "selected_pid": selected_pid,
        "selected_start_time_utc": (
            _json_time(normalized_selected_start)
            if normalized_selected_start is not None
            else None
        ),
        "expected_intent": expected_intent.model_dump(mode="json"),
        "discovered_processes": [
            process.model_dump(mode="json") for process in processes
        ],
        "selected_process": (
            selected.model_dump(mode="json")
            if selected is not None and not blocked_reasons
            else None
        ),
        "runtime_fingerprint": (
            runtime.model_dump(mode="json") if runtime is not None else None
        ),
        "observed_at_utc": _json_time(observed),
        "blocked_reasons": list(blocked_reasons),
    }
    return ETABSInstalledReadOnlyPreflightV1.model_validate(
        {
            **basis,
            "selected_start_time_utc": normalized_selected_start,
            "expected_intent": expected_intent,
            "discovered_processes": processes,
            "selected_process": selected if not blocked_reasons else None,
            "runtime_fingerprint": runtime,
            "observed_at_utc": observed,
            "blocked_reasons": blocked_reasons,
            "preflight_sha256": _digest(basis),
        }
    )


def build_etabs_session_identity_v1(
    *,
    process_instance: ETABSProcessInstanceV1,
    connection_origin: Literal["ATTACHED_EXISTING", "STARTED_OWNED"],
    model_name: str,
    model_path: str | None,
    etabs_version: str,
    present_units: str,
    model_locked: bool,
    saved_file_identity: ETABSFileIdentityV1 | None,
    observed_at_utc: datetime | None = None,
) -> ETABSSessionIdentityV1:
    """Build one stable visible-session identity from getter-only observations."""

    observed = _utc(observed_at_utc or datetime.now(_UTC), "observed_at_utc")
    basis = {
        "schema_version": "etabs-session-identity/v1",
        "process_instance_sha256": process_instance.instance_sha256,
        "connection_origin": connection_origin,
        "model_name": model_name,
        "model_path": model_path,
        "etabs_version": etabs_version,
        "present_units": present_units,
        "model_locked": model_locked,
        "saved_file_identity": (
            saved_file_identity.model_dump(mode="json")
            if saved_file_identity is not None
            else None
        ),
        "observed_at_utc": _json_time(observed),
    }
    identity_basis = {
        key: value for key, value in basis.items() if key != "observed_at_utc"
    }
    return ETABSSessionIdentityV1.model_validate(
        {
            **basis,
            "saved_file_identity": saved_file_identity,
            "observed_at_utc": observed,
            "session_sha256": _digest(identity_basis),
        }
    )


def build_etabs_saved_checkpoint_v1(
    *,
    process_instance: ETABSProcessInstanceV1,
    session_identity: ETABSSessionIdentityV1,
    file_identity: ETABSFileIdentityV1,
    save_call_id: str,
    saved_at_utc: datetime,
    observed_at_utc: datetime,
) -> ETABSSavedCheckpointV1:
    """Build a measured save receipt; this function performs no save itself."""

    saved = _utc(saved_at_utc, "saved_at_utc")
    observed = _utc(observed_at_utc, "observed_at_utc")
    if session_identity.process_instance_sha256 != process_instance.instance_sha256:
        raise ValueError("saved checkpoint session is bound to another process")
    if session_identity.model_path != file_identity.canonical_path:
        raise ValueError("saved checkpoint file does not match the visible model")
    basis = {
        "schema_version": "etabs-saved-checkpoint/v1",
        "process_instance_sha256": process_instance.instance_sha256,
        "session_sha256": session_identity.session_sha256,
        "file_identity": file_identity.model_dump(mode="json"),
        "saved_at_utc": _json_time(saved),
        "observed_at_utc": _json_time(observed),
        "save_call_id": save_call_id,
    }
    return ETABSSavedCheckpointV1.model_validate(
        {
            **basis,
            "file_identity": file_identity,
            "saved_at_utc": saved,
            "observed_at_utc": observed,
            "checkpoint_sha256": _digest(basis),
        }
    )


def classify_etabs_model_freshness_v1(
    *,
    session_identity: ETABSSessionIdentityV1,
    before_file: ETABSFileIdentityV1 | None,
    after_file: ETABSFileIdentityV1 | None,
    observed_at_utc: datetime,
    attached_session: bool,
    api_clean_signal_call_id: str | None = None,
    saved_checkpoint: ETABSSavedCheckpointV1 | None = None,
) -> ETABSModelFreshnessV1:
    """Classify live-session/file truth without saving an attached model."""

    observed = _utc(observed_at_utc, "observed_at_utc")
    if session_identity.model_path is None or before_file is None or after_file is None:
        disposition = ETABSModelFreshnessDispositionV1.FILE_UNAVAILABLE
        source: Literal[
            "ATTACHED_DEFAULT",
            "API_CLEAN_SIGNAL",
            "OPERATOR_SAVED_CHECKPOINT",
            "FILE_COMPARISON",
        ] = "FILE_COMPARISON"
        limitations = (
            "The visible saved file was unavailable; no hash-bound baseline is permitted.",
        )
    elif (
        before_file != after_file
        or before_file.canonical_path != session_identity.model_path
    ):
        disposition = ETABSModelFreshnessDispositionV1.FILE_DRIFT
        source = "FILE_COMPARISON"
        limitations = ("The persisted model changed across the observation window.",)
    elif api_clean_signal_call_id is None and saved_checkpoint is None:
        disposition = ETABSModelFreshnessDispositionV1.SESSION_UNSAVED_OR_UNKNOWN
        source = "ATTACHED_DEFAULT"
        limitations = (
            (
                "Attached-session memory may differ from the saved file; bounded getters only."
                if attached_session
                else "Owned-session cleanliness lacks a reviewed save or API signal."
            ),
        )
    else:
        if api_clean_signal_call_id is not None and saved_checkpoint is not None:
            raise ValueError("provide one clean-evidence source, not both")
        if saved_checkpoint is not None:
            if (
                saved_checkpoint.process_instance_sha256
                != session_identity.process_instance_sha256
                or saved_checkpoint.session_sha256 != session_identity.session_sha256
                or saved_checkpoint.file_identity != after_file
                or saved_checkpoint.observed_at_utc > observed
            ):
                raise ValueError("saved checkpoint does not match the live observation")
        disposition = ETABSModelFreshnessDispositionV1.SAVED_CLEAN_CONFIRMED
        source = (
            "API_CLEAN_SIGNAL"
            if api_clean_signal_call_id is not None
            else "OPERATOR_SAVED_CHECKPOINT"
        )
        limitations = (
            "Saved-clean evidence applies only to this PID/path/hash/observation window.",
        )
    return ETABSModelFreshnessV1(
        disposition=disposition,
        observation_source=source,
        process_instance_sha256=session_identity.process_instance_sha256,
        session_sha256=session_identity.session_sha256,
        session_model_path=session_identity.model_path,
        before_file=before_file,
        after_file=after_file,
        api_clean_signal_call_id=(
            api_clean_signal_call_id
            if disposition is ETABSModelFreshnessDispositionV1.SAVED_CLEAN_CONFIRMED
            else None
        ),
        saved_checkpoint=(
            saved_checkpoint
            if disposition is ETABSModelFreshnessDispositionV1.SAVED_CLEAN_CONFIRMED
            else None
        ),
        observed_at_utc=observed,
        hash_bound_baseline_allowed=(
            disposition is ETABSModelFreshnessDispositionV1.SAVED_CLEAN_CONFIRMED
        ),
        limitations=limitations,
    )


def _check_expected_intent(
    intent: ETABSExpectedModelIntentV1,
    session: ETABSSessionIdentityV1,
) -> None:
    if intent.expected_model_path is not None:
        expected = str(Path(intent.expected_model_path).resolve(strict=False))
        observed = (
            str(Path(session.model_path).resolve(strict=False))
            if session.model_path is not None
            else None
        )
        if observed != expected:
            raise ValueError("observed ETABS model path does not match intent")
    if intent.expected_model_name is not None:
        if session.model_name.casefold() != intent.expected_model_name.casefold():
            raise ValueError("observed ETABS model name does not match intent")
    if intent.expected_etabs_version is not None:
        if session.etabs_version != intent.expected_etabs_version:
            raise ValueError("observed ETABS version does not match intent")
    if (
        intent.allowed_access is ETABSAccessModeV1.ATTACHED_OBSERVE
        and session.connection_origin != "ATTACHED_EXISTING"
    ):
        raise ValueError("attached observation requires ATTACHED_EXISTING origin")
    if (
        intent.allowed_access is ETABSAccessModeV1.OWNED_COPY_MUTATION
        and session.connection_origin != "STARTED_OWNED"
    ):
        raise ValueError("mutation access requires a library-owned process")


def observe_etabs_target_v1(
    process_instance: ETABSProcessInstanceV1,
    expected_intent: ETABSExpectedModelIntentV1,
    runtime_fingerprint: ETABSRuntimeFingerprintV1,
    session_identity: ETABSSessionIdentityV1,
    model_freshness: ETABSModelFreshnessV1,
    *,
    observed_at_utc: datetime | None = None,
    ttl: timedelta = _DEFAULT_TARGET_TTL,
    observation_id: str | None = None,
) -> ETABSTargetObservationV1:
    """Build a short-lived target after a separate getter-only identity probe."""

    observed = _utc(observed_at_utc or datetime.now(_UTC), "observed_at_utc")
    if ttl <= timedelta(0) or ttl > timedelta(minutes=10):
        raise ValueError("target observation ttl must be within (0, 10 minutes]")
    _check_expected_intent(expected_intent, session_identity)
    basis = {
        "schema_version": "etabs-target-observation/v1",
        "observation_id": observation_id or secrets.token_hex(16),
        "process_instance": process_instance.model_dump(mode="json"),
        "expected_intent": expected_intent.model_dump(mode="json"),
        "session_identity": session_identity.model_dump(mode="json"),
        "runtime_fingerprint": runtime_fingerprint.model_dump(mode="json"),
        "model_freshness": model_freshness.model_dump(mode="json"),
        "allowed_access": expected_intent.allowed_access.value,
        "observed_at_utc": _json_time(observed),
        "expires_at_utc": _json_time(observed + ttl),
    }
    return ETABSTargetObservationV1.model_validate(
        {
            **basis,
            "process_instance": process_instance,
            "expected_intent": expected_intent,
            "session_identity": session_identity,
            "runtime_fingerprint": runtime_fingerprint,
            "model_freshness": model_freshness,
            "allowed_access": expected_intent.allowed_access,
            "observed_at_utc": observed,
            "expires_at_utc": observed + ttl,
            "observation_sha256": _digest(basis),
        }
    )


def verify_etabs_target_observation_v1(
    observation: ETABSTargetObservationV1,
    *,
    current_process: ETABSProcessInstanceV1,
    current_runtime: ETABSRuntimeFingerprintV1,
    current_session: ETABSSessionIdentityV1,
    verified_at_utc: datetime | None = None,
    maximum_revalidation_age: timedelta = timedelta(seconds=15),
) -> None:
    """Fail on expiry, PID reuse, runtime drift, or visible target drift."""

    verified = _utc(verified_at_utc or datetime.now(_UTC), "verified_at_utc")
    if maximum_revalidation_age <= timedelta(0):
        raise ValueError("maximum_revalidation_age must be positive")
    if verified < observation.observed_at_utc:
        raise RuntimeError("ETABS_TARGET_OBSERVATION_NOT_YET_VALID")
    if verified > observation.expires_at_utc:
        raise RuntimeError("ETABS_TARGET_OBSERVATION_EXPIRED")
    current_observations = (
        current_process.observed_at_utc,
        current_runtime.observed_at_utc,
        current_session.observed_at_utc,
    )
    if any(
        value < observation.observed_at_utc
        or value > verified
        or verified - value > maximum_revalidation_age
        for value in current_observations
    ):
        raise RuntimeError("ETABS_TARGET_REVALIDATION_STALE")
    if current_process.instance_sha256 != observation.process_instance.instance_sha256:
        raise RuntimeError("ETABS_PROCESS_INSTANCE_DRIFT")
    if current_runtime.fingerprint_sha256 != (
        observation.runtime_fingerprint.fingerprint_sha256
    ):
        raise RuntimeError("ETABS_RUNTIME_FINGERPRINT_DRIFT")
    if current_session.session_sha256 != observation.session_identity.session_sha256:
        raise RuntimeError("ETABS_SESSION_IDENTITY_DRIFT")
    _check_expected_intent(observation.expected_intent, current_session)


def _capability_payload(
    capability: ETABSBridgeCapabilityV1 | Mapping[str, Any],
) -> dict[str, Any]:
    if isinstance(capability, ETABSBridgeCapabilityV1):
        return capability.model_dump(mode="json", exclude={"signature_sha256"})
    return {
        key: value for key, value in capability.items() if key != "signature_sha256"
    }


def _capability_signature(payload: Mapping[str, Any], signing_key: bytes) -> str:
    if len(signing_key) < 32:
        raise ValueError("capability signing key must contain at least 32 bytes")
    return hmac.new(
        signing_key,
        _canonical_json(dict(payload)).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def issue_etabs_bridge_capability_v1(
    observation: ETABSTargetObservationV1,
    *,
    transaction_id: str,
    signing_key: bytes,
    issued_at_utc: datetime | None = None,
    ttl: timedelta = _DEFAULT_CAPABILITY_TTL,
    capability_id: str | None = None,
    nonce: str | None = None,
) -> ETABSBridgeCapabilityV1:
    """Issue an HMAC-bound capability; request data cannot self-authorize."""

    issued = _utc(issued_at_utc or datetime.now(_UTC), "issued_at_utc")
    if issued > observation.expires_at_utc:
        raise ValueError("cannot issue a capability from an expired observation")
    if ttl <= timedelta(0):
        raise ValueError("capability ttl must be positive")
    expires = min(issued + ttl, observation.expires_at_utc)
    payload = {
        "schema_version": "etabs-bridge-capability/v1",
        "capability_id": capability_id or secrets.token_hex(16),
        "target_observation_sha256": observation.observation_sha256,
        "process_instance_sha256": observation.process_instance.instance_sha256,
        "transaction_id": transaction_id,
        "allowed_access": observation.allowed_access.value,
        "single_use": observation.allowed_access
        is ETABSAccessModeV1.OWNED_COPY_MUTATION,
        "issued_at_utc": _json_time(issued),
        "expires_at_utc": _json_time(expires),
        "nonce": nonce or secrets.token_hex(16),
    }
    return ETABSBridgeCapabilityV1.model_validate(
        {
            **payload,
            "allowed_access": observation.allowed_access,
            "issued_at_utc": issued,
            "expires_at_utc": expires,
            "signature_sha256": _capability_signature(payload, signing_key),
        }
    )


def verify_etabs_bridge_capability_v1(
    capability: ETABSBridgeCapabilityV1,
    observation: ETABSTargetObservationV1,
    *,
    transaction_id: str,
    required_access: ETABSAccessModeV1,
    signing_key: bytes,
    verified_at_utc: datetime | None = None,
    consume_single_use: (
        Callable[[ETABSBridgeCapabilityV1, datetime], None] | None
    ) = None,
) -> None:
    """Verify signature, expiry, exact target, access, and transaction binding."""

    expected = _capability_signature(_capability_payload(capability), signing_key)
    if not hmac.compare_digest(capability.signature_sha256, expected):
        raise RuntimeError("ETABS_CAPABILITY_SIGNATURE_INVALID")
    verified = _utc(verified_at_utc or datetime.now(_UTC), "verified_at_utc")
    if verified < capability.issued_at_utc or verified > capability.expires_at_utc:
        raise RuntimeError("ETABS_CAPABILITY_EXPIRED_OR_NOT_YET_VALID")
    if capability.target_observation_sha256 != observation.observation_sha256:
        raise RuntimeError("ETABS_CAPABILITY_TARGET_MISMATCH")
    if (
        capability.process_instance_sha256
        != observation.process_instance.instance_sha256
    ):
        raise RuntimeError("ETABS_CAPABILITY_PROCESS_MISMATCH")
    if capability.transaction_id != transaction_id:
        raise RuntimeError("ETABS_CAPABILITY_TRANSACTION_MISMATCH")
    if capability.allowed_access is not required_access:
        raise RuntimeError("ETABS_CAPABILITY_ACCESS_MISMATCH")
    if capability.single_use:
        if consume_single_use is None:
            raise RuntimeError("ETABS_CAPABILITY_SINGLE_USE_CONSUMER_REQUIRED")
        consume_single_use(capability, verified)


def capture_etabs_state_v1(
    *,
    session_sha256: str,
    present_units: str,
    model_locked: bool,
    selected_output_cases: Sequence[str],
    selected_output_combinations: Sequence[str],
    case_statuses: Mapping[str, str],
    run_flags: Mapping[str, bool],
    table_display_selection_sha256: str | None = None,
    observed_at_utc: datetime | None = None,
) -> ETABSStateSnapshotV1:
    """Build a normalized state snapshot from getter results only."""

    observed = _utc(observed_at_utc or datetime.now(_UTC), "observed_at_utc")
    basis = {
        "schema_version": "etabs-state-snapshot/v1",
        "session_sha256": session_sha256,
        "present_units": present_units,
        "model_locked": model_locked,
        "selected_output_cases": sorted(set(selected_output_cases)),
        "selected_output_combinations": sorted(set(selected_output_combinations)),
        "case_statuses": sorted(case_statuses.items()),
        "run_flags": sorted(run_flags.items()),
        "table_display_selection_sha256": table_display_selection_sha256,
        "observed_at_utc": _json_time(observed),
    }
    normalized_cases = tuple(sorted(set(selected_output_cases)))
    normalized_combinations = tuple(sorted(set(selected_output_combinations)))
    normalized_statuses = tuple(sorted(case_statuses.items()))
    normalized_flags = tuple(sorted(run_flags.items()))
    return ETABSStateSnapshotV1.model_validate(
        {
            **basis,
            "selected_output_cases": normalized_cases,
            "selected_output_combinations": normalized_combinations,
            "case_statuses": normalized_statuses,
            "run_flags": normalized_flags,
            "observed_at_utc": observed,
            "state_sha256": _digest(basis),
        }
    )


def capture_attached_etabs_state_v1(
    reader: ETABSAttachedStateReaderV1,
    *,
    session_sha256: str,
    observed_at_utc: datetime | None = None,
) -> ETABSStateSnapshotV1:
    """Capture attached state exclusively through the declared getter surface."""

    return capture_etabs_state_v1(
        session_sha256=session_sha256,
        present_units=reader.get_present_units(),
        model_locked=reader.get_model_locked(),
        selected_output_cases=reader.get_selected_output_cases(),
        selected_output_combinations=reader.get_selected_output_combinations(),
        case_statuses=reader.get_case_statuses(),
        run_flags=reader.get_run_flags(),
        table_display_selection_sha256=(reader.get_table_display_selection_sha256()),
        observed_at_utc=observed_at_utc,
    )


def assess_attached_output_readiness_v1(
    snapshot: ETABSStateSnapshotV1,
    *,
    required_cases: Sequence[str] = (),
    required_combinations: Sequence[str] = (),
) -> Literal["READY", "HOLD"]:
    """Hold instead of changing output selection, run flags, or analysis state."""

    cases = set(required_cases)
    combinations = set(required_combinations)
    if not cases.issubset(snapshot.selected_output_cases):
        return "HOLD"
    if not combinations.issubset(snapshot.selected_output_combinations):
        return "HOLD"
    statuses = dict(snapshot.case_statuses)
    flags = dict(snapshot.run_flags)
    if any(statuses.get(name) != "FINISHED" for name in cases | combinations):
        return "HOLD"
    if any(flags.get(name) is not True for name in cases):
        return "HOLD"
    return "READY"


def compare_attached_etabs_state_v1(
    before: ETABSStateSnapshotV1,
    after: ETABSStateSnapshotV1,
) -> Literal["COMPLETED", "RESTORATION_UNVERIFIED"]:
    """Compare attached state; never call a setter to restore it."""

    if before.session_sha256 != after.session_sha256:
        return "RESTORATION_UNVERIFIED"
    before_payload = before.model_dump(
        mode="json", exclude={"observed_at_utc", "state_sha256"}
    )
    after_payload = after.model_dump(
        mode="json", exclude={"observed_at_utc", "state_sha256"}
    )
    return "COMPLETED" if before_payload == after_payload else "RESTORATION_UNVERIFIED"


def build_etabs_result_epoch_v1(
    *,
    model_identity_sha256: str,
    runtime_fingerprint: ETABSRuntimeFingerprintV1,
    process_instance: ETABSProcessInstanceV1,
    transaction_id: str,
    authorized_cases: Sequence[str],
    case_dependency_closure: Sequence[str],
    pre_statuses: Mapping[str, str],
    post_statuses: Mapping[str, str],
    run_flags: Mapping[str, bool],
    analysis_call_ids: Sequence[str],
    design_call_ids: Sequence[str],
    selection_sha256: str,
    result_sha256: str,
    uninterrupted_process: bool,
    uninterrupted_runtime: bool,
    copy_identity_sha256: str | None = None,
    change_set_sha256: str | None = None,
    design_basis_sha256: str | None = None,
    blocked_reasons: Sequence[str] = (),
    observed_at_utc: datetime | None = None,
) -> ETABSResultEpochV1:
    """Accept only an exact uninterrupted result epoch; otherwise block it."""

    reasons = list(blocked_reasons)
    authorized = set(authorized_cases)
    closure = set(case_dependency_closure)
    if runtime_fingerprint.process_instance_sha256 != process_instance.instance_sha256:
        reasons.append("RUNTIME_PROCESS_BINDING_MISMATCH")
    if not uninterrupted_process:
        reasons.append("PROCESS_INTERRUPTED")
    if not uninterrupted_runtime:
        reasons.append("RUNTIME_INTERRUPTED")
    if not authorized:
        reasons.append("AUTHORIZED_CASES_EMPTY")
    if authorized - closure:
        reasons.append("CASE_DEPENDENCY_CLOSURE_INCOMPLETE")
    if any(
        set(values) != closure for values in (pre_statuses, post_statuses, run_flags)
    ):
        reasons.append("CASE_STATUS_OR_RUN_FLAG_DOMAIN_MISMATCH")
    if any(status != "FINISHED" for status in post_statuses.values()):
        reasons.append("POST_STATUS_NOT_FINISHED")
    if any(not flag for flag in run_flags.values()):
        reasons.append("RUN_FLAG_NOT_ENABLED")
    if not analysis_call_ids:
        reasons.append("ANALYSIS_CALL_EVIDENCE_MISSING")
    if design_basis_sha256 is not None and not design_call_ids:
        reasons.append("DESIGN_CALL_EVIDENCE_MISSING")
    all_call_ids = tuple(analysis_call_ids) + tuple(design_call_ids)
    if len(all_call_ids) != len(set(all_call_ids)):
        reasons.append("DUPLICATE_CALL_ID")
    observed = _utc(observed_at_utc or datetime.now(_UTC), "observed_at_utc")
    disposition = (
        ETABSResultEpochDispositionV1.BLOCKED
        if reasons
        else ETABSResultEpochDispositionV1.ACCEPTED
    )
    basis = {
        "schema_version": "etabs-result-epoch/v1",
        "disposition": disposition.value,
        "model_identity_sha256": model_identity_sha256,
        "copy_identity_sha256": copy_identity_sha256,
        "change_set_sha256": change_set_sha256,
        "runtime_fingerprint_sha256": runtime_fingerprint.fingerprint_sha256,
        "process_instance_sha256": process_instance.instance_sha256,
        "transaction_id": transaction_id,
        "uninterrupted_process": uninterrupted_process,
        "uninterrupted_runtime": uninterrupted_runtime,
        "authorized_cases": sorted(set(authorized_cases)),
        "case_dependency_closure": sorted(set(case_dependency_closure)),
        "pre_statuses": sorted(pre_statuses.items()),
        "post_statuses": sorted(post_statuses.items()),
        "run_flags": sorted(run_flags.items()),
        "analysis_call_ids": list(analysis_call_ids),
        "design_call_ids": list(design_call_ids),
        "selection_sha256": selection_sha256,
        "result_sha256": result_sha256,
        "design_basis_sha256": design_basis_sha256,
        "observed_at_utc": _json_time(observed),
        "blocked_reasons": sorted(set(reasons)),
    }
    normalized_authorized_cases = tuple(sorted(set(authorized_cases)))
    normalized_dependency_closure = tuple(sorted(set(case_dependency_closure)))
    normalized_pre_statuses = tuple(sorted(pre_statuses.items()))
    normalized_post_statuses = tuple(sorted(post_statuses.items()))
    normalized_run_flags = tuple(sorted(run_flags.items()))
    normalized_blocked_reasons = tuple(sorted(set(reasons)))
    return ETABSResultEpochV1.model_validate(
        {
            **basis,
            "disposition": disposition,
            "runtime_fingerprint_sha256": runtime_fingerprint.fingerprint_sha256,
            "process_instance_sha256": process_instance.instance_sha256,
            "authorized_cases": normalized_authorized_cases,
            "case_dependency_closure": normalized_dependency_closure,
            "pre_statuses": normalized_pre_statuses,
            "post_statuses": normalized_post_statuses,
            "run_flags": normalized_run_flags,
            "analysis_call_ids": tuple(analysis_call_ids),
            "design_call_ids": tuple(design_call_ids),
            "observed_at_utc": observed,
            "blocked_reasons": normalized_blocked_reasons,
            "epoch_sha256": _digest(basis),
        }
    )
