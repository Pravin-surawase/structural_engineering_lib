# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Deterministic, read-only ETABS exported-data snapshot boundary.

This service consumes exported files only. It never opens or parses an EDB,
connects to ETABS, starts analysis, unlocks a model, or writes back to a model.
The maintained lossless CSV import service remains the parsing authority.
"""

from __future__ import annotations

import json
import math
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from structural_lib.core.models import DesignDefaults
from structural_lib.services.import_ledger import (
    ImportRowLedgerV1,
    ImportStatus,
    LosslessImportResultV1,
)
from structural_lib.services.imports import parse_dual_csv_lossless
from structural_lib.services.project_beam import (
    PROJECT_BEAM_SCHEMA_VERSION,
    EffectiveDepthBasisV1,
    ProjectBeamDesignInputV1,
    validate_project_beam_design_input_v1,
)

_SHA256_PATTERN = r"^[0-9a-f]{64}$"
_UTC_EXPORT_PATTERN = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
_ARCHIVE_FORMATS: dict[str, tuple[str, str]] = {
    ".csv": ("CSV", "text/csv"),
    ".xml": ("XML", "application/xml"),
    ".xls": ("EXCEL", "application/vnd.ms-excel"),
    ".xlsx": (
        "EXCEL",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ),
}
_ROLE_ORDER = {
    "SOURCE_EDB_IDENTITY": 0,
    "E2K_MODEL_DEFINITION": 1,
    "GEOMETRY_TABLE": 2,
    "FRAME_FORCE_TABLE": 3,
    "ARCHIVED_TABLE": 4,
}
_ROW_ROLE_ORDER = {"geometry": 0, "forces": 1}


class ETABSSnapshotStatus(StrEnum):
    """Fail-closed status for the complete snapshot build."""

    ACCEPTED = "ACCEPTED"
    BLOCKED = "BLOCKED"


class ETABSRowDisposition(StrEnum):
    """Exhaustive disposition for every physical calculation-source row."""

    ACCEPTED = "ACCEPTED"
    APPROVED_EXCLUSION = "APPROVED_EXCLUSION"
    BLOCKED = "BLOCKED"


class ETABSProjectExportIdentityV1(BaseModel):
    """Immutable project, EDB, and export-session identity."""

    model_config = ConfigDict(frozen=True, extra="forbid", str_strip_whitespace=True)

    project_id: str = Field(min_length=1, max_length=200)
    export_id: str = Field(min_length=1, max_length=200)
    source_edb_name: str = Field(min_length=1, max_length=255)
    source_edb_sha256: str = Field(pattern=_SHA256_PATTERN)
    exported_at_utc: str = Field(pattern=_UTC_EXPORT_PATTERN)
    etabs_version: str = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def _edb_identity_is_a_name_only(self) -> ETABSProjectExportIdentityV1:
        if Path(self.source_edb_name).name != self.source_edb_name:
            raise ValueError("source_edb_name must be a file name, not a path")
        if Path(self.source_edb_name).suffix.casefold() != ".edb":
            raise ValueError("source_edb_name must identify an EDB file")
        return self


class ETABSExportUnitsV1(BaseModel):
    """Exact units active for the selected ETABS table exports."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    coordinate_length: str
    station_length: str
    force: str
    moment: str
    section_dimension: str
    material_stress: str


class ETABSLocalAxisMappingV1(BaseModel):
    """Explicit mapping from selected ETABS local components to beam actions."""

    model_config = ConfigDict(frozen=True, extra="forbid", str_strip_whitespace=True)

    moment_source_component: str = Field(min_length=1)
    moment_destination: str = Field(min_length=1)
    shear_source_component: str = Field(min_length=1)
    shear_destination: str = Field(min_length=1)
    extrema_operation: str = Field(min_length=1)
    mapping_reference: str = Field(min_length=1)


class ETABSResultIdentityV1(BaseModel):
    """Selected load case, combination, or source envelope identity."""

    model_config = ConfigDict(frozen=True, extra="forbid", str_strip_whitespace=True)

    kind: Literal["LOAD_CASE", "LOAD_COMBINATION", "SOURCE_ENVELOPE"]
    name: str = Field(min_length=1, max_length=200)
    source_table_name: str = Field(min_length=1, max_length=300)
    envelope_basis: Literal[
        "INDEPENDENT_ABSOLUTE_EXTREMA_WITH_CONCURRENT_VALUES",
        "SOURCE_PRECOMPUTED_EXTREMA",
    ]
    selection_reference: str = Field(min_length=1)


class ETABSBeamRequestBasisV1(BaseModel):
    """Caller-owned detailing basis needed to derive effective depth."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    stirrup_diameter_mm: float = Field(gt=0)
    tension_bar_diameter_mm: float = Field(gt=0)


class ETABSApprovedExclusionV1(BaseModel):
    """Exact approval for excluding one non-calculation source row."""

    model_config = ConfigDict(frozen=True, extra="forbid", str_strip_whitespace=True)

    artifact_role: Literal["geometry", "forces"]
    source_row_number: int = Field(ge=2)
    reason_code: Literal["NON_BEAM_FRAME"]
    reason: str = Field(min_length=1)
    approval_reference: str = Field(min_length=1)


class ETABSArchivedTableInputV1(BaseModel):
    """One additional exported table retained as hash-bound evidence."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    path: Path
    table_name: str = Field(min_length=1, max_length=300)
    export_format: Literal["CSV", "XML", "EXCEL"]


class ETABSSourceArtifactV1(BaseModel):
    """Hash-bound source or exported-table artifact identity."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    role: Literal[
        "SOURCE_EDB_IDENTITY",
        "E2K_MODEL_DEFINITION",
        "GEOMETRY_TABLE",
        "FRAME_FORCE_TABLE",
        "ARCHIVED_TABLE",
    ]
    name: str
    table_name: str | None = None
    media_type: str
    sha256: str = Field(pattern=_SHA256_PATTERN)
    byte_count: int | None = Field(default=None, ge=0)
    hash_verification: Literal["WINDOWS_RECORDED", "LOCAL_BYTES_VERIFIED"]


class ETABSSnapshotIssueV1(BaseModel):
    """Stable machine issue for a blocked snapshot."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    code: str
    path: str
    message: str


class ETABSSnapshotAmbiguityV1(BaseModel):
    """Explicit unresolved meaning; any ambiguity blocks the snapshot."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    code: str
    path: str
    message: str


class ETABSRowDispositionV1(BaseModel):
    """Canonical disposition of one physical CSV source row."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    artifact_role: Literal["geometry", "forces"]
    source_row_number: int = Field(ge=2)
    source_record_id: str
    disposition: ETABSRowDisposition
    canonical_member_id: str | None = None
    reason_code: str | None = None
    reason: str | None = None
    approval_reference: str | None = None
    import_issue_codes: tuple[str, ...] = ()


class ETABSRowAccountingV1(BaseModel):
    """Conservation proof for all calculation-source rows."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    source_rows: int = Field(ge=0)
    accepted_rows: int = Field(ge=0)
    approved_exclusion_rows: int = Field(ge=0)
    blocked_rows: int = Field(ge=0)
    rows: tuple[ETABSRowDispositionV1, ...]

    @model_validator(mode="after")
    def _rows_are_exhaustive(self) -> ETABSRowAccountingV1:
        if self.source_rows != len(self.rows):
            raise ValueError("source_rows must equal the number of row dispositions")
        if self.source_rows != (
            self.accepted_rows + self.approved_exclusion_rows + self.blocked_rows
        ):
            raise ValueError(
                "source_rows must equal accepted plus approved-exclusion plus blocked rows"
            )
        return self


class ETABSMemberIdentityV1(BaseModel):
    """Stable ETABS UniqueName to canonical request-member mapping."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    canonical_member_id: str
    source_unique_name: str
    source_member_id: str
    label: str
    story: str


class ETABSCanonicalSnapshotV1(BaseModel):
    """Accepted deterministic ETABS exported-data snapshot."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        arbitrary_types_allowed=True,
    )

    schema_version: Literal["etabs-exported-snapshot/v1"] = "etabs-exported-snapshot/v1"
    hash_basis_version: Literal["etabs-exported-snapshot-hash/v1"] = (
        "etabs-exported-snapshot-hash/v1"
    )
    project_export_identity: ETABSProjectExportIdentityV1
    units: ETABSExportUnitsV1
    local_axis_mapping: ETABSLocalAxisMappingV1
    result_identity: ETABSResultIdentityV1
    source_artifacts: tuple[ETABSSourceArtifactV1, ...]
    normalization_ledger_sha256: str = Field(pattern=_SHA256_PATTERN)
    member_identities: tuple[ETABSMemberIdentityV1, ...]
    row_accounting: ETABSRowAccountingV1
    approved_exclusions: tuple[ETABSApprovedExclusionV1, ...]
    ambiguities: tuple[ETABSSnapshotAmbiguityV1, ...]
    beam_requests: tuple[ProjectBeamDesignInputV1, ...]
    snapshot_sha256: str = Field(pattern=_SHA256_PATTERN)


class ETABSSnapshotBuildResultV1(BaseModel):
    """Fail-closed snapshot result with evidence even when blocked."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        arbitrary_types_allowed=True,
    )

    schema_version: Literal["etabs-snapshot-build-result/v1"] = (
        "etabs-snapshot-build-result/v1"
    )
    status: ETABSSnapshotStatus
    source_artifacts: tuple[ETABSSourceArtifactV1, ...]
    normalization_ledger_sha256: str | None = Field(
        default=None, pattern=_SHA256_PATTERN
    )
    row_accounting: ETABSRowAccountingV1
    ambiguities: tuple[ETABSSnapshotAmbiguityV1, ...]
    issues: tuple[ETABSSnapshotIssueV1, ...]
    snapshot: ETABSCanonicalSnapshotV1 | None
    beam_requests: tuple[ProjectBeamDesignInputV1, ...]

    @model_validator(mode="after")
    def _blocked_results_expose_no_requests(self) -> ETABSSnapshotBuildResultV1:
        if self.status is ETABSSnapshotStatus.BLOCKED:
            if self.snapshot is not None or self.beam_requests:
                raise ValueError("blocked snapshot builds expose no canonical requests")
        elif self.snapshot is None or not self.beam_requests:
            raise ValueError("accepted snapshot builds require a snapshot and requests")
        return self


@dataclass(frozen=True)
class _ArtifactRead:
    artifact: ETABSSourceArtifactV1 | None
    issue: ETABSSnapshotIssueV1 | None


def _canonical_sha256(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def _issue(code: str, path: str, message: str) -> ETABSSnapshotIssueV1:
    return ETABSSnapshotIssueV1(code=code, path=path, message=message)


def _ambiguity(code: str, path: str, message: str) -> ETABSSnapshotAmbiguityV1:
    return ETABSSnapshotAmbiguityV1(code=code, path=path, message=message)


def _read_artifact(
    path_value: Path | str,
    *,
    role: Literal[
        "E2K_MODEL_DEFINITION",
        "GEOMETRY_TABLE",
        "FRAME_FORCE_TABLE",
        "ARCHIVED_TABLE",
    ],
    table_name: str | None,
    allowed_suffixes: set[str],
) -> _ArtifactRead:
    path = Path(path_value)
    suffix = path.suffix.casefold()
    if suffix == ".edb":
        return _ArtifactRead(
            None,
            _issue(
                "etabs.direct_edb_forbidden",
                f"source_artifacts.{role}",
                "EDB files may be opened only through ETABS on Windows; direct EDB intake is forbidden",
            ),
        )
    if suffix not in allowed_suffixes:
        return _ArtifactRead(
            None,
            _issue(
                "etabs.unsupported_artifact_format",
                f"source_artifacts.{role}",
                f"Unsupported {role} artifact suffix {suffix!r}",
            ),
        )
    try:
        raw = path.read_bytes()
    except OSError as exc:
        return _ArtifactRead(
            None,
            _issue(
                "etabs.artifact_unreadable",
                f"source_artifacts.{role}",
                f"Could not read {path.name!r}: {exc}",
            ),
        )
    media_type = (
        "text/plain"
        if suffix == ".e2k"
        else _ARCHIVE_FORMATS.get(suffix, ("", "application/octet-stream"))[1]
    )
    return _ArtifactRead(
        ETABSSourceArtifactV1(
            role=role,
            name=path.name,
            table_name=table_name,
            media_type=media_type,
            sha256=sha256(raw).hexdigest(),
            byte_count=len(raw),
            hash_verification="LOCAL_BYTES_VERIFIED",
        ),
        None,
    )


def _field_value(row: ImportRowLedgerV1, canonical_field: str) -> str:
    for field in row.fields:
        if field.canonical_field == canonical_field:
            return field.raw_value.strip()
    return ""


def _sorted_artifacts(
    artifacts: Sequence[ETABSSourceArtifactV1],
) -> tuple[ETABSSourceArtifactV1, ...]:
    return tuple(
        sorted(
            artifacts,
            key=lambda item: (
                _ROLE_ORDER[item.role],
                item.table_name or "",
                item.name,
                item.sha256,
            ),
        )
    )


def _row_accounting(
    rows: Sequence[ETABSRowDispositionV1],
) -> ETABSRowAccountingV1:
    ordered = tuple(
        sorted(
            rows,
            key=lambda item: (
                _ROW_ROLE_ORDER[item.artifact_role],
                item.source_row_number,
            ),
        )
    )
    counts = Counter(row.disposition for row in ordered)
    return ETABSRowAccountingV1(
        source_rows=len(ordered),
        accepted_rows=counts[ETABSRowDisposition.ACCEPTED],
        approved_exclusion_rows=counts[ETABSRowDisposition.APPROVED_EXCLUSION],
        blocked_rows=counts[ETABSRowDisposition.BLOCKED],
        rows=ordered,
    )


def _replace_row(
    rows: list[ETABSRowDispositionV1],
    *,
    artifact_role: str,
    source_row_number: int,
    **updates: Any,
) -> None:
    for index, row in enumerate(rows):
        if (
            row.artifact_role == artifact_role
            and row.source_row_number == source_row_number
        ):
            rows[index] = row.model_copy(update=updates)
            return


def _empty_accounting() -> ETABSRowAccountingV1:
    return ETABSRowAccountingV1(
        source_rows=0,
        accepted_rows=0,
        approved_exclusion_rows=0,
        blocked_rows=0,
        rows=(),
    )


def _blocked_result(
    *,
    artifacts: Sequence[ETABSSourceArtifactV1],
    rows: Sequence[ETABSRowDispositionV1],
    issues: Sequence[ETABSSnapshotIssueV1],
    ambiguities: Sequence[ETABSSnapshotAmbiguityV1],
    ledger_hash: str | None,
) -> ETABSSnapshotBuildResultV1:
    return ETABSSnapshotBuildResultV1(
        status=ETABSSnapshotStatus.BLOCKED,
        source_artifacts=_sorted_artifacts(artifacts),
        normalization_ledger_sha256=ledger_hash,
        row_accounting=_row_accounting(rows) if rows else _empty_accounting(),
        ambiguities=tuple(ambiguities),
        issues=tuple(issues),
        snapshot=None,
        beam_requests=(),
    )


def _snapshot_hash_payload(
    *,
    identity: ETABSProjectExportIdentityV1,
    units: ETABSExportUnitsV1,
    local_axis_mapping: ETABSLocalAxisMappingV1,
    result_identity: ETABSResultIdentityV1,
    source_artifacts: Sequence[ETABSSourceArtifactV1],
    ledger_hash: str,
    members: Sequence[ETABSMemberIdentityV1],
    accounting: ETABSRowAccountingV1,
    exclusions: Sequence[ETABSApprovedExclusionV1],
    ambiguities: Sequence[ETABSSnapshotAmbiguityV1],
    requests: Sequence[ProjectBeamDesignInputV1],
) -> dict[str, Any]:
    return {
        "schema_version": "etabs-exported-snapshot/v1",
        "hash_basis_version": "etabs-exported-snapshot-hash/v1",
        "project_export_identity": identity.model_dump(mode="json"),
        "units": units.model_dump(mode="json"),
        "local_axis_mapping": local_axis_mapping.model_dump(mode="json"),
        "result_identity": result_identity.model_dump(mode="json"),
        "source_artifacts": [
            artifact.model_dump(mode="json") for artifact in source_artifacts
        ],
        "normalization_ledger_sha256": ledger_hash,
        "member_identities": [member.model_dump(mode="json") for member in members],
        "row_accounting": accounting.model_dump(mode="json"),
        "approved_exclusions": [
            exclusion.model_dump(mode="json") for exclusion in exclusions
        ],
        "ambiguities": [item.model_dump(mode="json") for item in ambiguities],
        "canonical_beam_request_payloads": [
            {
                key: value
                for key, value in request.to_dict().items()
                if key != "source_metadata"
            }
            for request in requests
        ],
    }


def verify_etabs_canonical_snapshot_hash_v1(
    snapshot: ETABSCanonicalSnapshotV1,
) -> bool:
    """Verify the snapshot hash over its documented identity payload."""

    expected = _canonical_sha256(
        _snapshot_hash_payload(
            identity=snapshot.project_export_identity,
            units=snapshot.units,
            local_axis_mapping=snapshot.local_axis_mapping,
            result_identity=snapshot.result_identity,
            source_artifacts=snapshot.source_artifacts,
            ledger_hash=snapshot.normalization_ledger_sha256,
            members=snapshot.member_identities,
            accounting=snapshot.row_accounting,
            exclusions=snapshot.approved_exclusions,
            ambiguities=snapshot.ambiguities,
            requests=snapshot.beam_requests,
        )
    )
    return expected == snapshot.snapshot_sha256


def build_etabs_canonical_snapshot_v1(
    geometry_csv: Path | str,
    forces_csv: Path | str,
    e2k_model_definition: Path | str,
    *,
    project_export_identity: ETABSProjectExportIdentityV1,
    units: ETABSExportUnitsV1,
    local_axis_mapping: ETABSLocalAxisMappingV1,
    result_identity: ETABSResultIdentityV1,
    defaults: DesignDefaults,
    beam_request_basis: ETABSBeamRequestBasisV1,
    approved_exclusions: Sequence[ETABSApprovedExclusionV1] = (),
    archived_tables: Sequence[ETABSArchivedTableInputV1] = (),
) -> ETABSSnapshotBuildResultV1:
    """Build one deterministic snapshot and canonical beam-request sequence.

    Manual ETABS table exports and trial-API table exports enter through this
    same exported-file boundary. The function performs no ETABS or EDB access.
    """

    issues: list[ETABSSnapshotIssueV1] = []
    ambiguities: list[ETABSSnapshotAmbiguityV1] = []
    artifacts: list[ETABSSourceArtifactV1] = [
        ETABSSourceArtifactV1(
            role="SOURCE_EDB_IDENTITY",
            name=project_export_identity.source_edb_name,
            media_type="application/vnd.csi.etabs.edb",
            sha256=project_export_identity.source_edb_sha256,
            byte_count=None,
            hash_verification="WINDOWS_RECORDED",
        )
    ]

    requested_artifacts = (
        (
            e2k_model_definition,
            "E2K_MODEL_DEFINITION",
            "ETABS model definition",
            {".e2k"},
        ),
        (geometry_csv, "GEOMETRY_TABLE", "Connectivity - Frame", {".csv"}),
        (
            forces_csv,
            "FRAME_FORCE_TABLE",
            result_identity.source_table_name,
            {".csv"},
        ),
    )
    for path, role, table_name, suffixes in requested_artifacts:
        read = _read_artifact(
            path,
            role=role,  # type: ignore[arg-type]
            table_name=table_name,
            allowed_suffixes=suffixes,
        )
        if read.artifact is not None:
            artifacts.append(read.artifact)
        if read.issue is not None:
            issues.append(read.issue)

    for index, archive in enumerate(archived_tables):
        suffix = archive.path.suffix.casefold()
        detected_format = _ARCHIVE_FORMATS.get(suffix, ("", ""))[0]
        if detected_format != archive.export_format:
            issues.append(
                _issue(
                    "etabs.archive_format_mismatch",
                    f"archived_tables[{index}].export_format",
                    (
                        f"Declared {archive.export_format!r} does not match "
                        f"artifact suffix {suffix!r}"
                    ),
                )
            )
            continue
        read = _read_artifact(
            archive.path,
            role="ARCHIVED_TABLE",
            table_name=archive.table_name,
            allowed_suffixes=set(_ARCHIVE_FORMATS),
        )
        if read.artifact is not None:
            artifacts.append(read.artifact)
        if read.issue is not None:
            issues.append(read.issue)

    expected_units = {
        "coordinate_length": "m",
        "station_length": "m",
        "force": "kN",
        "moment": "kN-m",
        "section_dimension": "mm",
        "material_stress": "N/mm2",
    }
    for field, expected in expected_units.items():
        actual = getattr(units, field)
        if actual != expected:
            issues.append(
                _issue(
                    "etabs.unsupported_export_units",
                    f"units.{field}",
                    f"Expected {expected!r}; no implicit conversion is permitted",
                )
            )

    expected_axis = {
        "moment_source_component": "M3",
        "moment_destination": "mu_knm",
        "shear_source_component": "V2",
        "shear_destination": "vu_kn",
        "extrema_operation": "ABSOLUTE_EXTREMA_WITH_SIGNED_CONCURRENT_VALUES",
    }
    for field, expected in expected_axis.items():
        actual = getattr(local_axis_mapping, field)
        if actual != expected:
            issues.append(
                _issue(
                    "etabs.local_axis_mapping_mismatch",
                    f"local_axis_mapping.{field}",
                    f"Expected explicit mapping value {expected!r}",
                )
            )

    if not math.isclose(
        beam_request_basis.stirrup_diameter_mm,
        float(defaults.stirrup_dia_mm),
        rel_tol=0.0,
        abs_tol=0.0,
    ):
        issues.append(
            _issue(
                "etabs.detailing_basis_mismatch",
                "beam_request_basis.stirrup_diameter_mm",
                "Request stirrup diameter must match the explicit import defaults",
            )
        )

    required_artifact_roles = {
        "E2K_MODEL_DEFINITION",
        "GEOMETRY_TABLE",
        "FRAME_FORCE_TABLE",
    }
    observed_required_roles = {
        artifact.role
        for artifact in artifacts
        if artifact.role in required_artifact_roles
    }
    if observed_required_roles != required_artifact_roles:
        issues.append(
            _issue(
                "etabs.required_export_artifact_missing",
                "source_artifacts",
                "E2K, geometry CSV, and frame-force CSV are all required",
            )
        )

    if observed_required_roles != required_artifact_roles:
        return _blocked_result(
            artifacts=artifacts,
            rows=(),
            issues=issues,
            ambiguities=ambiguities,
            ledger_hash=None,
        )

    try:
        import_result: LosslessImportResultV1 = parse_dual_csv_lossless(
            geometry_csv,
            forces_csv,
            format_hint="etabs",
            defaults=defaults,
            geometry_artifact_name=Path(geometry_csv).name,
            forces_artifact_name=Path(forces_csv).name,
        )
    except (OSError, TypeError, ValueError, KeyError) as exc:
        return _blocked_result(
            artifacts=artifacts,
            rows=(),
            issues=(
                _issue(
                    "etabs.lossless_import_unavailable",
                    "lossless_import",
                    f"Lossless ETABS import failed before row accounting: {exc}",
                ),
            ),
            ambiguities=ambiguities,
            ledger_hash=None,
        )

    ledger_payload = import_result.ledger.model_dump(mode="json")
    ledger_hash = _canonical_sha256(ledger_payload)
    approval_by_row: dict[tuple[str, int], ETABSApprovedExclusionV1] = {}
    for approval in approved_exclusions:
        approval_key = (approval.artifact_role, approval.source_row_number)
        if approval_key in approval_by_row:
            issues.append(
                _issue(
                    "etabs.duplicate_exclusion_approval",
                    f"approved_exclusions.{approval_key[0]}[{approval_key[1]}]",
                    "Each source row may have at most one exclusion approval",
                )
            )
        approval_by_row[approval_key] = approval

    used_approvals: set[tuple[str, int]] = set()
    rows: list[ETABSRowDispositionV1] = []
    source_rows_by_key: dict[tuple[str, int], ImportRowLedgerV1] = {}
    for row in import_result.ledger.rows:
        if row.artifact_role == "combined":
            issues.append(
                _issue(
                    "etabs.combined_csv_not_canonical",
                    f"rows[{row.source_row_number}]",
                    "P5 requires separate ETABS geometry and frame-force tables",
                )
            )
            continue
        row_key = (row.artifact_role, row.source_row_number)
        source_rows_by_key[row_key] = row
        issue_codes = tuple(code.value for code in row.issue_codes)
        if row.status is ImportStatus.BLOCKED:
            rows.append(
                ETABSRowDispositionV1(
                    artifact_role=row.artifact_role,
                    source_row_number=row.source_row_number,
                    source_record_id=row.source_record_id,
                    disposition=ETABSRowDisposition.BLOCKED,
                    reason_code="LOSSLESS_IMPORT_BLOCKED",
                    reason="The maintained lossless import ledger blocked this row",
                    import_issue_codes=issue_codes,
                )
            )
        elif row.exclusion_reason is not None:
            matched_approval = approval_by_row.get(row_key)
            if matched_approval is None:
                rows.append(
                    ETABSRowDispositionV1(
                        artifact_role=row.artifact_role,
                        source_row_number=row.source_row_number,
                        source_record_id=row.source_record_id,
                        disposition=ETABSRowDisposition.BLOCKED,
                        reason_code="UNAPPROVED_EXCLUSION",
                        reason=row.exclusion_reason,
                        import_issue_codes=issue_codes,
                    )
                )
                issues.append(
                    _issue(
                        "etabs.unapproved_exclusion",
                        f"{row.artifact_role}.rows[{row.source_row_number}]",
                        f"Excluded row requires exact approval: {row.exclusion_reason}",
                    )
                )
            else:
                used_approvals.add(row_key)
                rows.append(
                    ETABSRowDispositionV1(
                        artifact_role=row.artifact_role,
                        source_row_number=row.source_row_number,
                        source_record_id=row.source_record_id,
                        disposition=ETABSRowDisposition.APPROVED_EXCLUSION,
                        reason_code=matched_approval.reason_code,
                        reason=matched_approval.reason,
                        approval_reference=matched_approval.approval_reference,
                        import_issue_codes=issue_codes,
                    )
                )
        else:
            rows.append(
                ETABSRowDispositionV1(
                    artifact_role=row.artifact_role,
                    source_row_number=row.source_row_number,
                    source_record_id=row.source_record_id,
                    disposition=ETABSRowDisposition.ACCEPTED,
                    import_issue_codes=issue_codes,
                )
            )

    for unused_approval_key in sorted(set(approval_by_row) - used_approvals):
        issues.append(
            _issue(
                "etabs.unused_exclusion_approval",
                (
                    "approved_exclusions."
                    f"{unused_approval_key[0]}[{unused_approval_key[1]}]"
                ),
                "Approval does not match an excluded source row",
            )
        )

    if import_result.status is ImportStatus.BLOCKED:
        issues.extend(
            _issue(issue.code.value, issue.path, issue.message)
            for issue in import_result.issues
        )

    force_fields = {
        field.canonical_field
        for row in import_result.ledger.rows
        if row.artifact_role == "forces"
        for field in row.fields
        if field.canonical_field is not None
    }
    raw_station_export = {"case_id", "station", "m3", "v2"} <= force_fields
    source_envelope_export = bool({"mu_max", "vu_max"} & force_fields)
    if raw_station_export:
        if result_identity.kind == "SOURCE_ENVELOPE":
            ambiguities.append(
                _ambiguity(
                    "etabs.result_kind_mismatch",
                    "result_identity.kind",
                    "Raw M3/V2 station rows require a load case or load combination identity",
                )
            )
        if (
            result_identity.envelope_basis
            != "INDEPENDENT_ABSOLUTE_EXTREMA_WITH_CONCURRENT_VALUES"
        ):
            ambiguities.append(
                _ambiguity(
                    "etabs.envelope_basis_mismatch",
                    "result_identity.envelope_basis",
                    "Raw station rows use the maintained independent-extrema envelope basis",
                )
            )
    elif source_envelope_export:
        if result_identity.kind != "SOURCE_ENVELOPE":
            ambiguities.append(
                _ambiguity(
                    "etabs.result_kind_mismatch",
                    "result_identity.kind",
                    "Precomputed Mu/Vu rows require an explicit source-envelope identity",
                )
            )
        if result_identity.envelope_basis != "SOURCE_PRECOMPUTED_EXTREMA":
            ambiguities.append(
                _ambiguity(
                    "etabs.envelope_basis_mismatch",
                    "result_identity.envelope_basis",
                    "Precomputed rows require SOURCE_PRECOMPUTED_EXTREMA",
                )
            )
    else:
        ambiguities.append(
            _ambiguity(
                "etabs.force_export_shape_unknown",
                "forces.headers",
                "Could not identify raw station rows or a precomputed source envelope",
            )
        )

    canonical_by_source_member: dict[str, str] = {}
    source_unique_by_member: dict[str, str] = {}
    geometry_rows_by_unique: dict[str, list[tuple[str, int]]] = {}
    for source_row_key, row in source_rows_by_key.items():
        if row.artifact_role != "geometry":
            continue
        disposition = next(
            item
            for item in rows
            if item.artifact_role == source_row_key[0]
            and item.source_row_number == source_row_key[1]
        )
        if disposition.disposition is not ETABSRowDisposition.ACCEPTED:
            continue
        label = _field_value(row, "label")
        story = _field_value(row, "story")
        unique_name = _field_value(row, "unique_name")
        source_member_id = f"{label}_{story}" if story else label
        if not unique_name:
            _replace_row(
                rows,
                artifact_role=row.artifact_role,
                source_row_number=row.source_row_number,
                disposition=ETABSRowDisposition.BLOCKED,
                reason_code="STABLE_MEMBER_ID_MISSING",
                reason="ETABS UniqueName is required for a stable canonical member ID",
            )
            issues.append(
                _issue(
                    "etabs.stable_member_id_missing",
                    f"geometry.rows[{row.source_row_number}].unique_name",
                    "ETABS UniqueName is required for every accepted beam row",
                )
            )
            continue
        geometry_rows_by_unique.setdefault(unique_name, []).append(source_row_key)
        canonical_member_id = (
            f"etabs:{project_export_identity.project_id}:{unique_name}"
        )
        canonical_by_source_member[source_member_id] = canonical_member_id
        source_unique_by_member[source_member_id] = unique_name
        _replace_row(
            rows,
            artifact_role=row.artifact_role,
            source_row_number=row.source_row_number,
            canonical_member_id=canonical_member_id,
        )

    for unique_name, duplicate_rows in geometry_rows_by_unique.items():
        if len(duplicate_rows) <= 1:
            continue
        issues.append(
            _issue(
                "etabs.stable_member_id_duplicate",
                f"geometry.unique_name.{unique_name}",
                "ETABS UniqueName must map to exactly one accepted geometry row",
            )
        )
        for artifact_role, row_number in duplicate_rows:
            _replace_row(
                rows,
                artifact_role=artifact_role,
                source_row_number=row_number,
                disposition=ETABSRowDisposition.BLOCKED,
                reason_code="STABLE_MEMBER_ID_DUPLICATE",
                reason="ETABS UniqueName is duplicated",
                canonical_member_id=None,
            )

    for source_row_key, row in source_rows_by_key.items():
        if row.artifact_role != "forces":
            continue
        disposition = next(
            item
            for item in rows
            if item.artifact_role == source_row_key[0]
            and item.source_row_number == source_row_key[1]
        )
        if disposition.disposition is not ETABSRowDisposition.ACCEPTED:
            continue
        label = _field_value(row, "beam_id")
        story = _field_value(row, "story")
        source_member_id = f"{label}_{story}" if story else label
        force_canonical_member_id = canonical_by_source_member.get(source_member_id)
        if force_canonical_member_id is None:
            _replace_row(
                rows,
                artifact_role=row.artifact_role,
                source_row_number=row.source_row_number,
                disposition=ETABSRowDisposition.BLOCKED,
                reason_code="STABLE_MEMBER_MAPPING_MISSING",
                reason="Force row has no accepted stable geometry-member mapping",
            )
            issues.append(
                _issue(
                    "etabs.stable_member_mapping_missing",
                    f"forces.rows[{row.source_row_number}]",
                    f"No stable geometry mapping for {source_member_id!r}",
                )
            )
            continue
        force_unique_name = _field_value(row, "unique_name")
        if force_unique_name and force_unique_name != source_unique_by_member.get(
            source_member_id
        ):
            _replace_row(
                rows,
                artifact_role=row.artifact_role,
                source_row_number=row.source_row_number,
                disposition=ETABSRowDisposition.BLOCKED,
                reason_code="STABLE_MEMBER_MAPPING_CONFLICT",
                reason="Force-row UniqueName conflicts with the geometry mapping",
            )
            issues.append(
                _issue(
                    "etabs.stable_member_mapping_conflict",
                    f"forces.rows[{row.source_row_number}].unique_name",
                    "Force and geometry ETABS UniqueName values do not match",
                )
            )
            continue
        if raw_station_export:
            case_id = _field_value(row, "case_id")
            if case_id != result_identity.name:
                _replace_row(
                    rows,
                    artifact_role=row.artifact_role,
                    source_row_number=row.source_row_number,
                    disposition=ETABSRowDisposition.BLOCKED,
                    reason_code="RESULT_IDENTITY_MISMATCH",
                    reason="Force-row output case differs from the selected result identity",
                )
                issues.append(
                    _issue(
                        "etabs.result_identity_mismatch",
                        f"forces.rows[{row.source_row_number}].case_id",
                        f"Expected exact output case {result_identity.name!r}",
                    )
                )
                continue
        _replace_row(
            rows,
            artifact_role=row.artifact_role,
            source_row_number=row.source_row_number,
            canonical_member_id=force_canonical_member_id,
        )

    accounting = _row_accounting(rows)
    if accounting.source_rows != import_result.ledger.totals.source_rows:
        issues.append(
            _issue(
                "etabs.row_accounting_mismatch",
                "row_accounting.source_rows",
                "P5 row dispositions do not conserve the lossless import source total",
            )
        )
    if accounting.blocked_rows:
        issues.append(
            _issue(
                "etabs.blocked_source_rows",
                "row_accounting.blocked_rows",
                f"{accounting.blocked_rows} source row(s) remain blocked",
            )
        )

    if import_result.batch is None:
        issues.append(
            _issue(
                "etabs.canonical_batch_unavailable",
                "lossless_import.batch",
                "The lossless import did not expose a canonical beam batch",
            )
        )

    if issues or ambiguities or import_result.batch is None:
        return _blocked_result(
            artifacts=artifacts,
            rows=rows,
            issues=issues,
            ambiguities=ambiguities,
            ledger_hash=ledger_hash,
        )

    batch = import_result.batch
    forces_by_id = {force.id: force for force in batch.forces}
    members: list[ETABSMemberIdentityV1] = []
    preliminary_requests: list[ProjectBeamDesignInputV1] = []
    for beam in sorted(batch.beams, key=lambda item: item.id):
        canonical_member_id = canonical_by_source_member[beam.id]
        source_unique_name = source_unique_by_member[beam.id]
        force = forces_by_id[beam.id]
        members.append(
            ETABSMemberIdentityV1(
                canonical_member_id=canonical_member_id,
                source_unique_name=source_unique_name,
                source_member_id=beam.id,
                label=beam.label,
                story=beam.story,
            )
        )
        request = ProjectBeamDesignInputV1(
            schema_version=PROJECT_BEAM_SCHEMA_VERSION,
            member_id=canonical_member_id,
            b_mm=beam.section.width_mm,
            D_mm=beam.section.depth_mm,
            mu_knm=force.mu_knm,
            vu_kn=force.vu_kn,
            fck_nmm2=beam.section.fck_mpa,
            fy_nmm2=beam.section.fy_mpa,
            effective_depth_basis=EffectiveDepthBasisV1(
                clear_cover_mm=beam.section.cover_mm,
                stirrup_diameter_mm=beam_request_basis.stirrup_diameter_mm,
                tension_bar_diameter_mm=beam_request_basis.tension_bar_diameter_mm,
            ),
        )
        validation = validate_project_beam_design_input_v1(request)
        if not validation.is_valid:
            issues.extend(
                _issue(issue.code, issue.path, issue.message)
                for issue in validation.issues
            )
        preliminary_requests.append(request)

    if issues:
        return _blocked_result(
            artifacts=artifacts,
            rows=rows,
            issues=issues,
            ambiguities=ambiguities,
            ledger_hash=ledger_hash,
        )

    sorted_artifacts = _sorted_artifacts(artifacts)
    sorted_members = tuple(sorted(members, key=lambda item: item.canonical_member_id))
    sorted_exclusions = tuple(
        sorted(
            approved_exclusions,
            key=lambda item: (item.artifact_role, item.source_row_number),
        )
    )
    snapshot_sha256 = _canonical_sha256(
        _snapshot_hash_payload(
            identity=project_export_identity,
            units=units,
            local_axis_mapping=local_axis_mapping,
            result_identity=result_identity,
            source_artifacts=sorted_artifacts,
            ledger_hash=ledger_hash,
            members=sorted_members,
            accounting=accounting,
            exclusions=sorted_exclusions,
            ambiguities=(),
            requests=preliminary_requests,
        )
    )
    source_hashes = {
        f"{artifact.role}:{artifact.name}": artifact.sha256
        for artifact in sorted_artifacts
    }
    member_by_id = {member.canonical_member_id: member for member in sorted_members}
    beam_requests = tuple(
        ProjectBeamDesignInputV1(
            schema_version=request.schema_version,
            member_id=request.member_id,
            b_mm=request.b_mm,
            D_mm=request.D_mm,
            mu_knm=request.mu_knm,
            vu_kn=request.vu_kn,
            fck_nmm2=request.fck_nmm2,
            fy_nmm2=request.fy_nmm2,
            d_mm=request.d_mm,
            effective_depth_basis=request.effective_depth_basis,
            source_metadata={
                "source_system": "ETABS_EXPORTED_FILES",
                "snapshot_sha256": snapshot_sha256,
                "project_id": project_export_identity.project_id,
                "export_id": project_export_identity.export_id,
                "source_unique_name": member_by_id[
                    request.member_id
                ].source_unique_name,
                "source_member_id": member_by_id[request.member_id].source_member_id,
                "source_artifact_hashes": source_hashes,
                "result_identity": result_identity.model_dump(mode="json"),
                "local_axis_mapping": local_axis_mapping.model_dump(mode="json"),
            },
        )
        for request in preliminary_requests
    )
    snapshot = ETABSCanonicalSnapshotV1(
        project_export_identity=project_export_identity,
        units=units,
        local_axis_mapping=local_axis_mapping,
        result_identity=result_identity,
        source_artifacts=sorted_artifacts,
        normalization_ledger_sha256=ledger_hash,
        member_identities=sorted_members,
        row_accounting=accounting,
        approved_exclusions=sorted_exclusions,
        ambiguities=(),
        beam_requests=beam_requests,
        snapshot_sha256=snapshot_sha256,
    )
    if not verify_etabs_canonical_snapshot_hash_v1(snapshot):
        return _blocked_result(
            artifacts=artifacts,
            rows=rows,
            issues=(
                _issue(
                    "etabs.snapshot_hash_verification_failed",
                    "snapshot_sha256",
                    "Canonical snapshot hash did not verify after construction",
                ),
            ),
            ambiguities=(),
            ledger_hash=ledger_hash,
        )
    return ETABSSnapshotBuildResultV1(
        status=ETABSSnapshotStatus.ACCEPTED,
        source_artifacts=sorted_artifacts,
        normalization_ledger_sha256=ledger_hash,
        row_accounting=accounting,
        ambiguities=(),
        issues=(),
        snapshot=snapshot,
        beam_requests=beam_requests,
    )


__all__ = [
    "ETABSApprovedExclusionV1",
    "ETABSArchivedTableInputV1",
    "ETABSBeamRequestBasisV1",
    "ETABSCanonicalSnapshotV1",
    "ETABSExportUnitsV1",
    "ETABSLocalAxisMappingV1",
    "ETABSMemberIdentityV1",
    "ETABSProjectExportIdentityV1",
    "ETABSResultIdentityV1",
    "ETABSRowAccountingV1",
    "ETABSRowDisposition",
    "ETABSRowDispositionV1",
    "ETABSSnapshotAmbiguityV1",
    "ETABSSnapshotBuildResultV1",
    "ETABSSnapshotIssueV1",
    "ETABSSnapshotStatus",
    "ETABSSourceArtifactV1",
    "build_etabs_canonical_snapshot_v1",
    "verify_etabs_canonical_snapshot_hash_v1",
]
