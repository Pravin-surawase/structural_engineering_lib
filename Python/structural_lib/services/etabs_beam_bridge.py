# SPDX-License-Identifier: MIT
"""Bounded Windows orchestration and transport contract for the W2 baseline.

This service owns one COM apartment for each call, attaches only to an already-open
ETABS process, and delegates extraction to the frozen W2A adapter. It never launches
ETABS, selects output cases, runs analysis/design, saves, or mutates the model. The
only setter remains W2A's temporary present-unit normalization and restoration.
"""

from __future__ import annotations

import importlib.metadata
import platform
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path, PureWindowsPath
from typing import Any, Literal

from pydantic import Field, model_validator

from structural_lib.services.contracts.common import StrictPublicModel
from structural_lib.services.etabs_beam_baseline import (
    ETABSBaselineBuildResultV1,
    ETABSBaselineBuildStatus,
    ETABSBeamBaselineRequestV1,
    ETABSModelFileSnapshotV1,
    ETABSRuntimeProvenanceV1,
    canonical_etabs_beam_baseline_hash_basis_json_v1,
    etabs_w2a_getter_matrix_sha256_v1,
    extract_etabs_beam_baseline_v1,
)
from structural_lib.services.etabs_live_bridge import (
    ETABSConnectionError,
    ETABSDataError,
    ETABSResultSelectionV1,
    SessionFactory,
    _decode_com_outputs,
    _default_session_factory,
    _library_identity,
    etabs_com_operation_v1,
)

__all__ = [
    "ETABS_BASELINE_MAX_CONNECTIONS",
    "ETABS_BASELINE_MAX_DISPOSITIONS",
    "ETABS_BASELINE_MAX_FRAMES",
    "ETABS_BASELINE_MAX_HASH_BASIS_BYTES",
    "ETABS_BASELINE_MAX_PROJECTED_EXCEL_ROWS",
    "ETABS_BASELINE_MAX_RESULT_STATIONS",
    "ETABSBeamBaselineCapacityError",
    "ETABSBeamBaselineCapacityV1",
    "ETABSBeamBaselineCountsV1",
    "ETABSBeamBaselinePreflightV1",
    "ETABSBeamBaselineRunRequestV1",
    "ETABSBeamBaselineTransportV1",
    "inspect_etabs_beam_baseline_v1",
    "observe_etabs_model_file_v1",
    "run_etabs_beam_baseline_v1",
]


ETABS_BASELINE_MAX_FRAMES: Literal[10_000] = 10_000
ETABS_BASELINE_MAX_CONNECTIONS: Literal[25_000] = 25_000
ETABS_BASELINE_MAX_RESULT_STATIONS: Literal[50_000] = 50_000
ETABS_BASELINE_MAX_DISPOSITIONS: Literal[75_000] = 75_000
ETABS_BASELINE_MAX_PROJECTED_EXCEL_ROWS: Literal[100_000] = 100_000
ETABS_BASELINE_MAX_HASH_BASIS_BYTES: Literal[25_000_000] = 25_000_000
ETABS_BASELINE_JSON_CHUNK_CHARACTERS: Literal[15_000] = 15_000
_HASH_PATTERN = r"^[0-9a-f]{64}$"


class ETABSBeamBaselineCapacityError(ETABSDataError):
    """A complete baseline exceeds the frozen W2B response/review limits."""


class ETABSBeamBaselineCapacityV1(StrictPublicModel):
    max_frames: Literal[10_000] = ETABS_BASELINE_MAX_FRAMES
    max_connectivity_rows: Literal[25_000] = ETABS_BASELINE_MAX_CONNECTIONS
    max_result_station_rows: Literal[50_000] = ETABS_BASELINE_MAX_RESULT_STATIONS
    max_disposition_rows: Literal[75_000] = ETABS_BASELINE_MAX_DISPOSITIONS
    max_projected_excel_rows: Literal[100_000] = ETABS_BASELINE_MAX_PROJECTED_EXCEL_ROWS
    max_hash_basis_utf8_bytes: Literal[25_000_000] = ETABS_BASELINE_MAX_HASH_BASIS_BYTES
    excel_json_chunk_characters: Literal[15_000] = ETABS_BASELINE_JSON_CHUNK_CHARACTERS
    truncation_permitted: Literal[False] = False


class ETABSBeamBaselineCountsV1(StrictPublicModel):
    stories: int = Field(ge=0)
    frames: int = Field(ge=0)
    connectivity_rows: int = Field(ge=0)
    result_sets: int = Field(ge=0)
    result_station_rows: int = Field(ge=0)
    disposition_rows: int = Field(ge=0)
    projected_excel_rows: int = Field(ge=0)


class ETABSBeamBaselinePreflightV1(StrictPublicModel):
    """Getter-only identity shown to the operator before a W2 baseline read."""

    schema_version: Literal["etabs-beam-baseline-preflight/v1"] = (
        "etabs-beam-baseline-preflight/v1"
    )
    observed_model_file: ETABSModelFileSnapshotV1
    etabs_version: str = Field(min_length=1)
    etabs_version_number: float
    model_locked: bool
    present_units_enum: int = Field(ge=1)
    runtime_provenance: ETABSRuntimeProvenanceV1
    getter_matrix_sha256: str = Field(pattern=_HASH_PATTERN)
    capacity: ETABSBeamBaselineCapacityV1 = Field(
        default_factory=ETABSBeamBaselineCapacityV1
    )
    approved_copy_confirmation_required: Literal[True] = True
    result_selections_are_getter_verified_only: Literal[True] = True
    frame_analysis_verdict: Literal["HELD_NOT_SUPPORTED"] = "HELD_NOT_SUPPORTED"


class ETABSBeamBaselineRunRequestV1(StrictPublicModel):
    """Exact preflight-bound request for one read-only W2 baseline extraction."""

    schema_version: Literal["etabs-beam-baseline-run-request/v1"] = (
        "etabs-beam-baseline-run-request/v1"
    )
    authorized_model_file: ETABSModelFileSnapshotV1
    expected_etabs_version: str = Field(min_length=1)
    expected_etabs_version_number: float
    expected_present_units_enum: int = Field(ge=1)
    expected_runtime_provenance: ETABSRuntimeProvenanceV1
    expected_getter_matrix_sha256: str = Field(pattern=_HASH_PATTERN)
    result_selections: list[ETABSResultSelectionV1] = Field(min_length=1, max_length=20)
    orientation_tolerance_mm: float = Field(default=1.0, gt=0, le=10.0)
    require_locked_model: Literal[True] = True
    approved_copy_confirmed: Literal[True]

    @model_validator(mode="after")
    def _selection_names_are_unique(self) -> ETABSBeamBaselineRunRequestV1:
        names = [selection.name for selection in self.result_selections]
        if len(names) != len(set(names)):
            raise ValueError("result selection names must be unique")
        return self


class ETABSBeamBaselineTransportV1(StrictPublicModel):
    """Bounded REST/Excel payload preserving the exact W2A hash basis."""

    schema_version: Literal["etabs-beam-baseline-transport/v1"] = (
        "etabs-beam-baseline-transport/v1"
    )
    build_result: ETABSBaselineBuildResultV1
    counts: ETABSBeamBaselineCountsV1
    capacity: ETABSBeamBaselineCapacityV1
    baseline_hash_basis_json: str | None
    baseline_hash_basis_utf8_bytes: int = Field(ge=0)
    frame_analysis_verdict: Literal["HELD_NOT_SUPPORTED"] = "HELD_NOT_SUPPORTED"

    @model_validator(mode="after")
    def _accepted_payload_is_complete(self) -> ETABSBeamBaselineTransportV1:
        baseline = self.build_result.baseline
        if self.build_result.status is ETABSBaselineBuildStatus.ACCEPTED:
            if baseline is None or self.baseline_hash_basis_json is None:
                raise ValueError(
                    "accepted transport requires the complete baseline hash basis"
                )
            encoded = self.baseline_hash_basis_json.encode("utf-8")
            if len(encoded) != self.baseline_hash_basis_utf8_bytes:
                raise ValueError("baseline hash-basis byte count does not match")
            if sha256(encoded).hexdigest() != baseline.baseline_sha256:
                raise ValueError("baseline hash-basis digest does not match W2A")
        elif (
            self.baseline_hash_basis_json is not None
            or self.baseline_hash_basis_utf8_bytes
        ):
            raise ValueError(
                "blocked transport must not expose a partial baseline hash basis"
            )
        return self


ModelFileObserver = Callable[[str], ETABSModelFileSnapshotV1]


def _utc_text(value: float | None = None) -> str:
    instant = datetime.now(UTC) if value is None else datetime.fromtimestamp(value, UTC)
    return instant.isoformat(timespec="microseconds").replace("+00:00", "Z")


def observe_etabs_model_file_v1(model_path: str) -> ETABSModelFileSnapshotV1:
    """Hash one exact saved EDB file without opening it through ETABS."""

    parsed = PureWindowsPath(model_path)
    if not parsed.is_absolute() or parsed.suffix.casefold() != ".edb":
        raise ETABSDataError(
            "ETABS_MODEL_PATH_INVALID",
            "The authorized model path must be an absolute Windows .edb path.",
        )
    path = Path(model_path)
    try:
        before = path.stat()
        digest = sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        after = path.stat()
    except OSError as exc:
        raise ETABSDataError(
            "ETABS_MODEL_FILE_UNREADABLE",
            "The authorized copied model could not be read for identity evidence.",
        ) from exc
    before_identity = (before.st_size, before.st_mtime_ns)
    after_identity = (after.st_size, after.st_mtime_ns)
    if before_identity != after_identity or after.st_size <= 0:
        raise ETABSDataError(
            "ETABS_MODEL_FILE_OBSERVATION_UNSTABLE",
            "The copied model changed while its read-only identity was being observed.",
        )
    return ETABSModelFileSnapshotV1(
        model_path=str(path),
        model_name=path.name,
        sha256=digest.hexdigest(),
        byte_count=after.st_size,
        modified_at_utc=_utc_text(after.st_mtime),
        observed_at_utc=_utc_text(),
    )


def _runtime_provenance() -> ETABSRuntimeProvenanceV1:
    library_version, library_content_identity = _library_identity()
    try:
        comtypes_version = importlib.metadata.version("comtypes")
    except importlib.metadata.PackageNotFoundError:
        comtypes_version = "not-installed"
    return ETABSRuntimeProvenanceV1(
        library_version=library_version,
        library_content_identity=library_content_identity,
        python_version=platform.python_version(),
        platform=platform.platform(),
        com_provider=f"comtypes/{comtypes_version};{sys.maxsize.bit_length() + 1}-bit",
    )


def _direct_model_values(sap_model: Any) -> tuple[str, str, float, bool, int]:
    model_path = str(sap_model.GetModelFilename(True) or "").strip()
    if not model_path:
        raise ETABSConnectionError(
            "ETABS_MODEL_PATH_MISSING",
            "The already-open copied ETABS model must be saved before W2 inspection.",
        )
    parsed = PureWindowsPath(model_path)
    if not parsed.is_absolute() or parsed.suffix.casefold() != ".edb":
        raise ETABSConnectionError(
            "ETABS_MODEL_PATH_INVALID",
            "ETABS did not return the full path of a saved .edb model.",
        )
    version, version_number = _decode_com_outputs(
        "SapModel.GetVersion", sap_model.GetVersion(), output_count=2
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
    return model_path, str(version), float(version_number), locked, units


def inspect_etabs_beam_baseline_v1(
    *,
    session_factory: SessionFactory = _default_session_factory,
    observe_model_file: ModelFileObserver = observe_etabs_model_file_v1,
) -> ETABSBeamBaselinePreflightV1:
    """Attach getter-only and return the exact source/runtime identity for approval."""

    runtime = _runtime_provenance()
    with etabs_com_operation_v1():
        with session_factory() as session:
            model_path, version, version_number, locked, units = _direct_model_values(
                session.sap_model
            )
            snapshot = observe_model_file(model_path)
    return ETABSBeamBaselinePreflightV1(
        observed_model_file=snapshot,
        etabs_version=version,
        etabs_version_number=version_number,
        model_locked=locked,
        present_units_enum=units,
        runtime_provenance=runtime,
        getter_matrix_sha256=etabs_w2a_getter_matrix_sha256_v1(),
    )


def _same_snapshot(
    expected: ETABSModelFileSnapshotV1, observed: ETABSModelFileSnapshotV1
) -> bool:
    return (
        PureWindowsPath(expected.model_path) == PureWindowsPath(observed.model_path)
        and expected.model_name == observed.model_name
        and expected.sha256 == observed.sha256
        and expected.byte_count == observed.byte_count
        and expected.modified_at_utc == observed.modified_at_utc
    )


def _enforce_capacity(
    build_result: ETABSBaselineBuildResultV1,
) -> tuple[ETABSBeamBaselineCountsV1, str | None, int]:
    baseline = build_result.baseline
    if baseline is None:
        disposition_count = len(build_result.dispositions)
        if disposition_count > ETABS_BASELINE_MAX_DISPOSITIONS:
            raise ETABSBeamBaselineCapacityError(
                "ETABS_BASELINE_ROW_LIMIT_EXCEEDED",
                "Blocked baseline dispositions exceed the frozen W2B transport limit.",
            )
        return (
            ETABSBeamBaselineCountsV1(
                stories=0,
                frames=0,
                connectivity_rows=0,
                result_sets=0,
                result_station_rows=0,
                disposition_rows=disposition_count,
                projected_excel_rows=0,
            ),
            None,
            0,
        )

    station_count = sum(len(result.stations) for result in baseline.results)
    counts_by_name = {
        "frames": len(baseline.frames),
        "connectivity rows": len(baseline.connectivity),
        "result station rows": station_count,
        "disposition rows": len(baseline.dispositions),
    }
    limits_by_name = {
        "frames": ETABS_BASELINE_MAX_FRAMES,
        "connectivity rows": ETABS_BASELINE_MAX_CONNECTIONS,
        "result station rows": ETABS_BASELINE_MAX_RESULT_STATIONS,
        "disposition rows": ETABS_BASELINE_MAX_DISPOSITIONS,
    }
    exceeded = [
        f"{name}={counts_by_name[name]}>{limit}"
        for name, limit in limits_by_name.items()
        if counts_by_name[name] > limit
    ]
    basis_json = canonical_etabs_beam_baseline_hash_basis_json_v1(baseline)
    basis_bytes = len(basis_json.encode("utf-8"))
    chunk_count = max(
        1,
        (len(basis_json) + ETABS_BASELINE_JSON_CHUNK_CHARACTERS - 1)
        // ETABS_BASELINE_JSON_CHUNK_CHARACTERS,
    )
    projected_rows = (
        1
        + len(baseline.stories)
        + len(baseline.frames)
        + len(baseline.connectivity)
        + station_count
        + len(baseline.dispositions)
        + chunk_count
    )
    if projected_rows > ETABS_BASELINE_MAX_PROJECTED_EXCEL_ROWS:
        exceeded.append(
            "projected Excel rows="
            f"{projected_rows}>{ETABS_BASELINE_MAX_PROJECTED_EXCEL_ROWS}"
        )
    if basis_bytes > ETABS_BASELINE_MAX_HASH_BASIS_BYTES:
        exceeded.append(
            "hash-basis UTF-8 bytes="
            f"{basis_bytes}>{ETABS_BASELINE_MAX_HASH_BASIS_BYTES}"
        )
    if exceeded:
        raise ETABSBeamBaselineCapacityError(
            "ETABS_BASELINE_ROW_LIMIT_EXCEEDED",
            "The complete baseline exceeds W2B limits: " + "; ".join(exceeded),
        )
    return (
        ETABSBeamBaselineCountsV1(
            stories=len(baseline.stories),
            frames=len(baseline.frames),
            connectivity_rows=len(baseline.connectivity),
            result_sets=len(baseline.results),
            result_station_rows=station_count,
            disposition_rows=len(baseline.dispositions),
            projected_excel_rows=projected_rows,
        ),
        basis_json,
        basis_bytes,
    )


def run_etabs_beam_baseline_v1(
    request: ETABSBeamBaselineRunRequestV1,
    *,
    session_factory: SessionFactory = _default_session_factory,
    observe_model_file: ModelFileObserver = observe_etabs_model_file_v1,
) -> ETABSBeamBaselineTransportV1:
    """Run one complete preflight-bound W2 extraction in a single COM apartment."""

    runtime = _runtime_provenance()
    getter_hash = etabs_w2a_getter_matrix_sha256_v1()
    if runtime != request.expected_runtime_provenance:
        raise ETABSDataError(
            "ETABS_RUNTIME_IDENTITY_MISMATCH",
            "The Python/library/COM runtime differs from the approved W2 preflight.",
        )
    if getter_hash != request.expected_getter_matrix_sha256:
        raise ETABSDataError(
            "ETABS_GETTER_MATRIX_IDENTITY_MISMATCH",
            "The W2A getter matrix differs from the approved W2 preflight.",
        )

    with etabs_com_operation_v1():
        with session_factory() as session:
            model_path, version, version_number, locked, units = _direct_model_values(
                session.sap_model
            )
            if PureWindowsPath(model_path) != PureWindowsPath(
                request.authorized_model_file.model_path
            ):
                raise ETABSDataError(
                    "ETABS_MODEL_IDENTITY_MISMATCH",
                    "The open ETABS model path differs from the approved copied model.",
                )
            if (
                version != request.expected_etabs_version
                or version_number != request.expected_etabs_version_number
            ):
                raise ETABSDataError(
                    "ETABS_VERSION_IDENTITY_MISMATCH",
                    "The attached ETABS version differs from the approved W2 preflight.",
                )
            if units != request.expected_present_units_enum:
                raise ETABSDataError(
                    "ETABS_PRESENT_UNITS_IDENTITY_MISMATCH",
                    "The present units differ from the approved W2 preflight.",
                )
            if not locked:
                raise ETABSDataError(
                    "ETABS_MODEL_NOT_LOCKED",
                    "W2 baseline extraction requires the approved copied model to remain locked.",
                )
            observed = observe_model_file(model_path)
            if not _same_snapshot(request.authorized_model_file, observed):
                raise ETABSDataError(
                    "ETABS_MODEL_AUTHORIZATION_MISMATCH",
                    "The copied model path, hash, size, or timestamp differs from the approved W2 preflight.",
                )
            w2a_request = ETABSBeamBaselineRequestV1(
                authorized_model_file=request.authorized_model_file,
                runtime_provenance=runtime,
                result_selections=tuple(request.result_selections),
                orientation_tolerance_mm=request.orientation_tolerance_mm,
            )
            build_result = extract_etabs_beam_baseline_v1(
                session.sap_model,
                w2a_request,
                observe_model_file=observe_model_file,
            )
            post_locked = session.sap_model.GetModelIsLocked()
            post_units = session.sap_model.GetPresentUnits()
            if post_locked is not True:
                raise ETABSDataError(
                    "ETABS_MODEL_LOCK_STATE_CHANGED",
                    "The copied model did not remain locked through W2 extraction.",
                )
            if post_units != units:
                raise ETABSDataError(
                    "ETABS_UNIT_RESTORATION_FAILED",
                    "The original present units were not restored after W2 extraction.",
                )

    counts, basis_json, basis_bytes = _enforce_capacity(build_result)
    return ETABSBeamBaselineTransportV1(
        build_result=build_result,
        counts=counts,
        capacity=ETABSBeamBaselineCapacityV1(),
        baseline_hash_basis_json=basis_json,
        baseline_hash_basis_utf8_bytes=basis_bytes,
    )
