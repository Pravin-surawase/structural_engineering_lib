"""C0 generic ETABS design/export acquisition contracts without schema claims.

The builders are offline and perform file identity checks only.  They do not
attach to ETABS, drive its UI, open SQLite, or claim support for any table or
column until a separately authorized C1 inventory is accepted.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal, Self

from pydantic import Field, model_validator

from structural_lib.services.contracts.common import StrictPublicModel
from structural_lib.services.etabs_session_guard import ETABSResultEpochV1

__all__ = [
    "ETABSConcreteDesignBasisDraftV1",
    "ETABSConcreteDesignBasisV1",
    "ETABSDesignSettingV1",
    "ETABSExportBoundsV1",
    "ETABSRequestedTableV1",
    "ETABSSQLiteExportManifestDraftV1",
    "ETABSSQLiteExportManifestV1",
    "build_etabs_concrete_design_basis_v1",
    "finalize_etabs_sqlite_export_manifest_v1",
]

_SHA = r"^[0-9a-f]{64}$"


def _json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def _digest(value: object) -> str:
    return hashlib.sha256(_json(value).encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _utc(value: datetime, field: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field} must be timezone-aware")
    return value.astimezone(UTC)


class ETABSDesignSettingV1(StrictPublicModel):
    name: str = Field(min_length=1, max_length=160)
    disposition: Literal["EXPLICIT", "ETABS_DEFAULT", "UNAVAILABLE"]
    value: str | int | float | bool | None
    source_call_id: str | None = Field(default=None, max_length=160)

    @model_validator(mode="after")
    def validate_setting(self) -> Self:
        if self.disposition == "UNAVAILABLE":
            if self.value is not None or self.source_call_id is not None:
                raise ValueError("unavailable design setting cannot carry a value")
        elif self.value is None or not self.source_call_id:
            raise ValueError("resolved design setting requires value and call identity")
        return self


class ETABSConcreteDesignBasisDraftV1(StrictPublicModel):
    basis_id: str = Field(min_length=1, max_length=160)
    basis_status: Literal["COMPLETE", "HOLD"]
    target_observation_sha256: str = Field(pattern=_SHA)
    runtime_fingerprint_sha256: str = Field(pattern=_SHA)
    model_identity_sha256: str = Field(pattern=_SHA)
    result_epoch: ETABSResultEpochV1
    design_code: str = Field(min_length=1, max_length=160)
    etabs_build: str = Field(min_length=1, max_length=160)
    design_combination_ids: tuple[str, ...] = Field(min_length=1)
    preferences: tuple[ETABSDesignSettingV1, ...]
    overwrites: tuple[ETABSDesignSettingV1, ...]
    object_design_procedure: str = Field(min_length=1, max_length=160)
    resolved_assigned_section: str = Field(min_length=1, max_length=160)
    auto_select_state: Literal["NOT_AUTO_SELECT", "AUTO_SELECT_HELD"]
    section_rebar_definition: Literal["BEAM", "COLUMN", "UNAVAILABLE"]
    concrete_material: str = Field(min_length=1, max_length=160)
    fck_nmm2: float = Field(ge=15, le=100)
    longitudinal_rebar_material: str = Field(min_length=1, max_length=160)
    transverse_rebar_material: str = Field(min_length=1, max_length=160)
    fy_longitudinal_nmm2: float = Field(ge=250, le=700)
    fy_transverse_nmm2: float = Field(ge=250, le=700)
    result_item_type: str = Field(min_length=1, max_length=160)
    warnings: tuple[str, ...]
    issues: tuple[str, ...]
    source_references: tuple[str, ...] = Field(min_length=1)
    limitations: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_basis(self) -> Self:
        if self.result_epoch.runtime_fingerprint_sha256 != (
            self.runtime_fingerprint_sha256
        ):
            raise ValueError("design basis runtime differs from result epoch")
        if self.result_epoch.model_identity_sha256 != self.model_identity_sha256:
            raise ValueError("design basis model differs from result epoch")
        if len(self.design_combination_ids) != len(set(self.design_combination_ids)):
            raise ValueError("design combination identities must be unique")
        for values, name in (
            (self.preferences, "preferences"),
            (self.overwrites, "overwrites"),
        ):
            names = tuple(value.name for value in values)
            if len(names) != len(set(names)):
                raise ValueError(f"{name} names must be unique")
        if self.basis_status == "COMPLETE":
            if self.result_epoch.disposition.value != "ACCEPTED":
                raise ValueError("complete design basis requires accepted result epoch")
            if self.issues:
                raise ValueError("complete design basis cannot carry issues")
            if self.auto_select_state != "NOT_AUTO_SELECT":
                raise ValueError(
                    "complete design basis cannot retain auto-select ambiguity"
                )
            if self.section_rebar_definition != "BEAM":
                raise ValueError("complete design basis requires BEAM rebar definition")
            if any(
                value.disposition == "UNAVAILABLE"
                for value in self.preferences + self.overwrites
            ):
                raise ValueError("complete design basis cannot omit requested settings")
        elif not self.issues:
            raise ValueError("held design basis requires explicit issues")
        return self


class ETABSConcreteDesignBasisV1(ETABSConcreteDesignBasisDraftV1):
    schema_version: Literal["etabs-concrete-design-basis/v1"] = (
        "etabs-concrete-design-basis/v1"
    )
    design_basis_sha256: str = Field(pattern=_SHA)

    @model_validator(mode="after")
    def validate_digest(self) -> Self:
        expected = _digest(
            self.model_dump(mode="json", exclude={"design_basis_sha256"})
        )
        if self.design_basis_sha256 != expected:
            raise ValueError("design_basis_sha256 does not match canonical basis")
        return self


def build_etabs_concrete_design_basis_v1(
    draft: ETABSConcreteDesignBasisDraftV1, /
) -> ETABSConcreteDesignBasisV1:
    json_payload = {
        "schema_version": "etabs-concrete-design-basis/v1",
        **draft.model_dump(mode="json"),
    }
    return ETABSConcreteDesignBasisV1.model_validate(
        {
            "schema_version": "etabs-concrete-design-basis/v1",
            **draft.model_dump(mode="python"),
            "design_basis_sha256": _digest(json_payload),
        }
    )


class ETABSRequestedTableV1(StrictPublicModel):
    request_id: str = Field(min_length=1, max_length=160)
    requested_table_key: str = Field(min_length=1, max_length=240)
    requested_fields: tuple[str, ...] = Field(min_length=1)
    comparison_row_by_field: tuple[tuple[str, str], ...] = Field(min_length=1)
    request_basis: str = Field(min_length=1, max_length=500)

    @model_validator(mode="after")
    def validate_fields(self) -> Self:
        if len(self.requested_fields) != len(set(self.requested_fields)):
            raise ValueError("requested fields must be unique")
        mapping_fields = tuple(field for field, _row in self.comparison_row_by_field)
        if len(mapping_fields) != len(set(mapping_fields)):
            raise ValueError("comparison field mappings must be unique")
        if set(mapping_fields) != set(self.requested_fields):
            raise ValueError("every requested field must map to one comparison row")
        return self


class ETABSExportBoundsV1(StrictPublicModel):
    maximum_file_bytes: int = Field(ge=1, le=10_000_000_000)
    maximum_requested_tables: int = Field(ge=1, le=10_000)
    maximum_fields_per_table: int = Field(ge=1, le=10_000)
    maximum_rows_per_table: int = Field(ge=1, le=10_000_000)


class ETABSSQLiteExportManifestDraftV1(StrictPublicModel):
    export_id: str = Field(min_length=1, max_length=160)
    acquisition_mode: Literal["OPERATOR_UI_EXPORT"] = "OPERATOR_UI_EXPORT"
    artifact_scope: Literal["GENERIC_C0_FIXTURE", "INSTALLED_C1_EXPORT"]
    schema_support_status: Literal["UNOBSERVED"] = "UNOBSERVED"
    target_observation_sha256: str = Field(pattern=_SHA)
    runtime_fingerprint_sha256: str = Field(pattern=_SHA)
    model_identity_sha256: str = Field(pattern=_SHA)
    result_epoch: ETABSResultEpochV1
    requested_tables: tuple[ETABSRequestedTableV1, ...] = Field(min_length=1)
    filter_selection_state_sha256: str = Field(pattern=_SHA)
    destination_path: str = Field(min_length=1, max_length=1024)
    destination_was_absent_at_start: Literal[True] = True
    started_at_utc: datetime
    pre_state_sha256: str = Field(pattern=_SHA)
    bounds: ETABSExportBoundsV1
    retention_policy: str = Field(min_length=1, max_length=500)
    limitations: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_request(self) -> Self:
        _utc(self.started_at_utc, "started_at_utc")
        if self.result_epoch.runtime_fingerprint_sha256 != (
            self.runtime_fingerprint_sha256
        ):
            raise ValueError("export runtime differs from result epoch")
        if self.result_epoch.model_identity_sha256 != self.model_identity_sha256:
            raise ValueError("export model differs from result epoch")
        if len(self.requested_tables) > self.bounds.maximum_requested_tables:
            raise ValueError("requested table count exceeds explicit bound")
        keys = tuple(item.requested_table_key for item in self.requested_tables)
        if len(keys) != len(set(keys)):
            raise ValueError("requested table keys must be unique")
        if any(
            len(item.requested_fields) > self.bounds.maximum_fields_per_table
            for item in self.requested_tables
        ):
            raise ValueError("requested field count exceeds explicit bound")
        return self


class ETABSSQLiteExportManifestV1(ETABSSQLiteExportManifestDraftV1):
    schema_version: Literal["etabs-sqlite-export-manifest/v1"] = (
        "etabs-sqlite-export-manifest/v1"
    )
    completion_status: Literal["COMPLETED"] = "COMPLETED"
    completed_at_utc: datetime
    artifact_size_bytes: int = Field(ge=1)
    artifact_sha256: str = Field(pattern=_SHA)
    post_state_sha256: str = Field(pattern=_SHA)
    source_stable_during_hash: Literal[True] = True
    pending_wal_present: Literal[False] = False
    pending_shm_present: Literal[False] = False
    actual_schema_inventory_sha256: None = None
    parser_support_claimed: Literal[False] = False
    manifest_sha256: str = Field(pattern=_SHA)

    @model_validator(mode="after")
    def validate_completion(self) -> Self:
        started = _utc(self.started_at_utc, "started_at_utc")
        completed = _utc(self.completed_at_utc, "completed_at_utc")
        if completed < started:
            raise ValueError("export completion cannot precede its start")
        if self.artifact_size_bytes > self.bounds.maximum_file_bytes:
            raise ValueError("export artifact exceeds explicit file bound")
        if self.pre_state_sha256 != self.post_state_sha256:
            raise ValueError("completed export requires equal pre/post operation state")
        expected = _digest(self.model_dump(mode="json", exclude={"manifest_sha256"}))
        if self.manifest_sha256 != expected:
            raise ValueError("manifest_sha256 does not match canonical manifest")
        return self


def finalize_etabs_sqlite_export_manifest_v1(
    draft: ETABSSQLiteExportManifestDraftV1,
    /,
    *,
    artifact_path: str | Path,
    completed_at_utc: datetime,
    post_state_sha256: str,
) -> ETABSSQLiteExportManifestV1:
    """Measure a completed artifact; do not open SQLite or infer its schema."""

    completed = _utc(completed_at_utc, "completed_at_utc")
    artifact = Path(artifact_path).resolve(strict=True)
    expected = Path(draft.destination_path).resolve(strict=True)
    if artifact != expected or not artifact.is_file():
        raise ValueError("artifact must equal the declared regular-file destination")
    wal = Path(str(artifact) + "-wal")
    shm = Path(str(artifact) + "-shm")
    if wal.exists() or shm.exists():
        raise RuntimeError("ETABS_SQLITE_EXPORT_PENDING_WAL_OR_SHM")
    before = artifact.stat()
    artifact_sha256 = _sha256_file(artifact)
    after = artifact.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise RuntimeError("ETABS_SQLITE_EXPORT_CHANGED_DURING_HASH")
    if after.st_size <= 0 or after.st_size > draft.bounds.maximum_file_bytes:
        raise ValueError("export artifact size is outside the explicit bound")
    json_payload = {
        "schema_version": "etabs-sqlite-export-manifest/v1",
        **draft.model_dump(mode="json"),
        "completion_status": "COMPLETED",
        "completed_at_utc": completed.isoformat().replace("+00:00", "Z"),
        "artifact_size_bytes": after.st_size,
        "artifact_sha256": artifact_sha256,
        "post_state_sha256": post_state_sha256,
        "source_stable_during_hash": True,
        "pending_wal_present": False,
        "pending_shm_present": False,
        "actual_schema_inventory_sha256": None,
        "parser_support_claimed": False,
    }
    return ETABSSQLiteExportManifestV1.model_validate(
        {
            "schema_version": "etabs-sqlite-export-manifest/v1",
            **draft.model_dump(mode="python"),
            "completion_status": "COMPLETED",
            "completed_at_utc": completed,
            "artifact_size_bytes": after.st_size,
            "artifact_sha256": artifact_sha256,
            "post_state_sha256": post_state_sha256,
            "source_stable_during_hash": True,
            "pending_wal_present": False,
            "pending_shm_present": False,
            "actual_schema_inventory_sha256": None,
            "parser_support_claimed": False,
            "manifest_sha256": _digest(json_payload),
        }
    )
