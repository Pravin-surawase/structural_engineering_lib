"""Offline ETABS design/export acquisition contracts and C1 schema inventory.

The C0 builders perform file identity checks only.  The C1 inventory opens an
operator-created export read-only and records schema metadata plus row counts;
it does not attach to ETABS, drive its UI, interpret table data, or claim parser
support.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
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
    "ETABSInstalledSQLiteEvidenceV1",
    "ETABSRequestedTableV1",
    "ETABSSQLiteColumnInventoryV1",
    "ETABSSQLiteExportManifestDraftV1",
    "ETABSSQLiteExportManifestV1",
    "ETABSSQLiteRequestedFieldResolutionV1",
    "ETABSSQLiteRequestedTableResolutionV1",
    "ETABSSQLiteSchemaInventoryV1",
    "ETABSSQLiteTableInventoryV1",
    "build_etabs_installed_sqlite_evidence_v1",
    "build_etabs_concrete_design_basis_v1",
    "finalize_etabs_sqlite_export_manifest_v1",
    "inventory_etabs_sqlite_export_v1",
]

_SHA = r"^[0-9a-f]{64}$"
_MAX_SCHEMA_TABLES = 10_000


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


class ETABSSQLiteColumnInventoryV1(StrictPublicModel):
    ordinal: int = Field(ge=0)
    name: str = Field(min_length=1, max_length=500)
    declared_type: str = Field(max_length=500)
    not_null: bool
    primary_key_ordinal: int = Field(ge=0)
    hidden: int = Field(ge=0, le=3)


class ETABSSQLiteTableInventoryV1(StrictPublicModel):
    table_name: str = Field(min_length=1, max_length=500)
    schema_sql_sha256: str = Field(pattern=_SHA)
    row_count: int = Field(ge=0)
    columns: tuple[ETABSSQLiteColumnInventoryV1, ...] = Field(min_length=1)
    primary_key_columns: tuple[str, ...]

    @model_validator(mode="after")
    def validate_table(self) -> Self:
        ordinals = tuple(column.ordinal for column in self.columns)
        if ordinals != tuple(range(len(self.columns))):
            raise ValueError("SQLite column ordinals must be contiguous and ordered")
        names = tuple(column.name for column in self.columns)
        if len(names) != len(set(names)):
            raise ValueError("SQLite column names must be unique")
        primary = tuple(
            column.name
            for column in sorted(
                self.columns,
                key=lambda item: item.primary_key_ordinal,
            )
            if column.primary_key_ordinal > 0
        )
        if self.primary_key_columns != primary:
            raise ValueError("primary key columns must match SQLite key ordinals")
        return self


class ETABSSQLiteRequestedFieldResolutionV1(StrictPublicModel):
    requested_field: str = Field(min_length=1, max_length=500)
    comparison_row: str = Field(min_length=1, max_length=500)
    disposition: Literal["FOUND", "REJECTED"]
    observed_column: str | None = Field(default=None, max_length=500)
    reason: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_resolution(self) -> Self:
        if self.disposition == "FOUND":
            if self.observed_column != self.requested_field or self.reason is not None:
                raise ValueError("found field requires one exact observed column")
        elif self.observed_column is not None or not self.reason:
            raise ValueError("rejected field requires a reason and no observed column")
        return self


class ETABSSQLiteRequestedTableResolutionV1(StrictPublicModel):
    request_id: str = Field(min_length=1, max_length=160)
    requested_table_key: str = Field(min_length=1, max_length=500)
    disposition: Literal["FOUND", "REJECTED"]
    observed_table_name: str | None = Field(default=None, max_length=500)
    reason: str | None = Field(default=None, max_length=500)
    fields: tuple[ETABSSQLiteRequestedFieldResolutionV1, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_resolution(self) -> Self:
        requested = tuple(field.requested_field for field in self.fields)
        if len(requested) != len(set(requested)):
            raise ValueError("requested field resolutions must be unique")
        if self.disposition == "FOUND":
            if self.observed_table_name != self.requested_table_key or self.reason:
                raise ValueError("found table requires one exact observed table")
        else:
            if self.observed_table_name is not None or not self.reason:
                raise ValueError(
                    "rejected table requires a reason and no observed table"
                )
            if any(field.disposition != "REJECTED" for field in self.fields):
                raise ValueError("a rejected table cannot contain found fields")
        return self


class ETABSSQLiteSchemaInventoryV1(StrictPublicModel):
    schema_version: Literal["etabs-sqlite-schema-inventory/v1"] = (
        "etabs-sqlite-schema-inventory/v1"
    )
    inventory_status: Literal["COMPLETE"] = "COMPLETE"
    acquisition_mode: Literal["OPERATOR_UI_EXPORT"] = "OPERATOR_UI_EXPORT"
    export_manifest_sha256: str = Field(pattern=_SHA)
    artifact_sha256: str = Field(pattern=_SHA)
    artifact_size_bytes: int = Field(ge=1)
    target_observation_sha256: str = Field(pattern=_SHA)
    runtime_fingerprint_sha256: str = Field(pattern=_SHA)
    model_identity_sha256: str = Field(pattern=_SHA)
    result_epoch_sha256: str = Field(pattern=_SHA)
    sqlite_version: str = Field(min_length=1, max_length=120)
    application_id: int
    user_version: int
    page_size_bytes: int = Field(ge=1)
    page_count: int = Field(ge=1)
    integrity_check: Literal["ok"] = "ok"
    tables: tuple[ETABSSQLiteTableInventoryV1, ...] = Field(min_length=1)
    request_resolutions: tuple[ETABSSQLiteRequestedTableResolutionV1, ...] = Field(
        min_length=1
    )
    inspected_at_utc: datetime
    source_stable_during_inspection: Literal[True] = True
    pending_wal_present: Literal[False] = False
    pending_shm_present: Literal[False] = False
    parser_support_claimed: Literal[False] = False
    limitations: tuple[str, ...] = Field(min_length=1)
    inventory_sha256: str = Field(pattern=_SHA)

    @model_validator(mode="after")
    def validate_inventory(self) -> Self:
        _utc(self.inspected_at_utc, "inspected_at_utc")
        table_names = tuple(table.table_name for table in self.tables)
        if table_names != tuple(sorted(set(table_names))):
            raise ValueError("SQLite tables must be unique and sorted")
        request_ids = tuple(item.request_id for item in self.request_resolutions)
        if len(request_ids) != len(set(request_ids)):
            raise ValueError("SQLite request resolutions must be unique")
        expected = _digest(self.model_dump(mode="json", exclude={"inventory_sha256"}))
        if self.inventory_sha256 != expected:
            raise ValueError("inventory_sha256 does not match canonical inventory")
        return self


class ETABSInstalledSQLiteEvidenceV1(StrictPublicModel):
    schema_version: Literal["etabs-installed-sqlite-evidence/v1"] = (
        "etabs-installed-sqlite-evidence/v1"
    )
    export_manifest: ETABSSQLiteExportManifestV1
    schema_inventory: ETABSSQLiteSchemaInventoryV1
    parser_support_claimed: Literal[False] = False
    evidence_sha256: str = Field(pattern=_SHA)

    @model_validator(mode="after")
    def validate_binding(self) -> Self:
        manifest = self.export_manifest
        inventory = self.schema_inventory
        if manifest.artifact_scope != "INSTALLED_C1_EXPORT":
            raise ValueError("installed evidence requires an installed C1 export")
        if inventory.export_manifest_sha256 != manifest.manifest_sha256:
            raise ValueError("schema inventory is bound to another export manifest")
        if (
            inventory.artifact_sha256 != manifest.artifact_sha256
            or inventory.artifact_size_bytes != manifest.artifact_size_bytes
            or inventory.target_observation_sha256 != manifest.target_observation_sha256
            or inventory.runtime_fingerprint_sha256
            != manifest.runtime_fingerprint_sha256
            or inventory.model_identity_sha256 != manifest.model_identity_sha256
            or inventory.result_epoch_sha256 != manifest.result_epoch.epoch_sha256
        ):
            raise ValueError("schema inventory identity differs from export identity")
        expected = _digest(self.model_dump(mode="json", exclude={"evidence_sha256"}))
        if self.evidence_sha256 != expected:
            raise ValueError("evidence_sha256 does not match installed SQLite evidence")
        return self


def _quote_sqlite_identifier(value: str) -> str:
    if "\x00" in value:
        raise ValueError("SQLite identifier contains a null character")
    return '"' + value.replace('"', '""') + '"'


def _sqlite_pragma_int(connection: sqlite3.Connection, name: str) -> int:
    if name not in {"application_id", "user_version", "page_size", "page_count"}:
        raise ValueError("unsupported SQLite pragma")
    row = connection.execute(f"PRAGMA {name}").fetchone()
    if row is None or len(row) != 1:
        raise RuntimeError(f"ETABS_SQLITE_{name.upper()}_UNAVAILABLE")
    return int(row[0])


def inventory_etabs_sqlite_export_v1(
    manifest: ETABSSQLiteExportManifestV1,
    /,
    *,
    artifact_path: str | Path,
    inspected_at_utc: datetime | None = None,
) -> ETABSSQLiteSchemaInventoryV1:
    """Inventory one frozen C1 export without interpreting any ETABS data row."""

    if manifest.artifact_scope != "INSTALLED_C1_EXPORT":
        raise ValueError("schema inventory requires an installed C1 export")
    artifact = Path(artifact_path).resolve(strict=True)
    expected_path = Path(manifest.destination_path).resolve(strict=True)
    if artifact != expected_path or not artifact.is_file():
        raise ValueError("artifact must equal the installed export destination")
    wal = Path(str(artifact) + "-wal")
    shm = Path(str(artifact) + "-shm")
    if wal.exists() or shm.exists():
        raise RuntimeError("ETABS_SQLITE_EXPORT_PENDING_WAL_OR_SHM")
    before = artifact.stat()
    before_sha256 = _sha256_file(artifact)
    if (
        before.st_size != manifest.artifact_size_bytes
        or before_sha256 != manifest.artifact_sha256
    ):
        raise RuntimeError("ETABS_SQLITE_EXPORT_IDENTITY_MISMATCH")

    tables: list[ETABSSQLiteTableInventoryV1] = []
    try:
        uri = f"{artifact.as_uri()}?mode=ro&immutable=1"
        with sqlite3.connect(uri, uri=True, timeout=1.0) as connection:
            connection.execute("PRAGMA query_only = ON")
            integrity_rows = tuple(
                str(row[0]) for row in connection.execute("PRAGMA quick_check")
            )
            if integrity_rows != ("ok",):
                raise RuntimeError("ETABS_SQLITE_INTEGRITY_CHECK_FAILED")
            sqlite_version = str(
                connection.execute("SELECT sqlite_version()").fetchone()[0]
            )
            application_id = _sqlite_pragma_int(connection, "application_id")
            user_version = _sqlite_pragma_int(connection, "user_version")
            page_size = _sqlite_pragma_int(connection, "page_size")
            page_count = _sqlite_pragma_int(connection, "page_count")
            schema_rows = tuple(
                connection.execute(
                    "SELECT name, sql FROM sqlite_master "
                    "WHERE type = 'table' ORDER BY name COLLATE BINARY"
                )
            )
            if not schema_rows:
                raise RuntimeError("ETABS_SQLITE_SCHEMA_HAS_NO_TABLES")
            if len(schema_rows) > _MAX_SCHEMA_TABLES:
                raise RuntimeError("ETABS_SQLITE_SCHEMA_TABLE_BOUND_EXCEEDED")
            for raw_table_name, create_sql in schema_rows:
                table_name = str(raw_table_name)
                column_rows = tuple(
                    connection.execute(
                        'SELECT cid, name, type, "notnull", pk, hidden '
                        "FROM pragma_table_xinfo(?) ORDER BY cid",
                        (table_name,),
                    )
                )
                if not column_rows:
                    raise RuntimeError("ETABS_SQLITE_TABLE_HAS_NO_COLUMNS")
                if len(column_rows) > manifest.bounds.maximum_fields_per_table:
                    raise RuntimeError("ETABS_SQLITE_FIELD_BOUND_EXCEEDED")
                columns = tuple(
                    ETABSSQLiteColumnInventoryV1(
                        ordinal=int(row[0]),
                        name=str(row[1]),
                        declared_type=str(row[2] or ""),
                        not_null=bool(row[3]),
                        primary_key_ordinal=int(row[4]),
                        hidden=int(row[5]),
                    )
                    for row in column_rows
                )
                count_sql = (
                    f"SELECT COUNT(*) FROM {_quote_sqlite_identifier(table_name)}"
                )
                count_row = connection.execute(count_sql).fetchone()
                if count_row is None:
                    raise RuntimeError("ETABS_SQLITE_ROW_COUNT_UNAVAILABLE")
                row_count = int(count_row[0])
                if row_count > manifest.bounds.maximum_rows_per_table:
                    raise RuntimeError("ETABS_SQLITE_ROW_BOUND_EXCEEDED")
                primary_key_columns = tuple(
                    column.name
                    for column in sorted(
                        columns,
                        key=lambda item: item.primary_key_ordinal,
                    )
                    if column.primary_key_ordinal > 0
                )
                tables.append(
                    ETABSSQLiteTableInventoryV1(
                        table_name=table_name,
                        schema_sql_sha256=_digest({"sql": create_sql}),
                        row_count=row_count,
                        columns=columns,
                        primary_key_columns=primary_key_columns,
                    )
                )
    except sqlite3.Error as exc:
        raise RuntimeError("ETABS_SQLITE_SCHEMA_INVENTORY_FAILED") from exc

    table_by_name = {table.table_name: table for table in tables}
    resolutions: list[ETABSSQLiteRequestedTableResolutionV1] = []
    for request in manifest.requested_tables:
        table = table_by_name.get(request.requested_table_key)
        comparison_rows = dict(request.comparison_row_by_field)
        if table is None:
            fields = tuple(
                ETABSSQLiteRequestedFieldResolutionV1(
                    requested_field=field,
                    comparison_row=comparison_rows[field],
                    disposition="REJECTED",
                    reason="REQUESTED_TABLE_NOT_FOUND",
                )
                for field in request.requested_fields
            )
            resolutions.append(
                ETABSSQLiteRequestedTableResolutionV1(
                    request_id=request.request_id,
                    requested_table_key=request.requested_table_key,
                    disposition="REJECTED",
                    reason="REQUESTED_TABLE_NOT_FOUND",
                    fields=fields,
                )
            )
            continue
        column_names = {column.name for column in table.columns}
        fields = tuple(
            ETABSSQLiteRequestedFieldResolutionV1(
                requested_field=field,
                comparison_row=comparison_rows[field],
                disposition="FOUND" if field in column_names else "REJECTED",
                observed_column=field if field in column_names else None,
                reason=None if field in column_names else "REQUESTED_FIELD_NOT_FOUND",
            )
            for field in request.requested_fields
        )
        resolutions.append(
            ETABSSQLiteRequestedTableResolutionV1(
                request_id=request.request_id,
                requested_table_key=request.requested_table_key,
                disposition="FOUND",
                observed_table_name=table.table_name,
                fields=fields,
            )
        )

    after = artifact.stat()
    after_sha256 = _sha256_file(artifact)
    if wal.exists() or shm.exists():
        raise RuntimeError("ETABS_SQLITE_EXPORT_PENDING_WAL_OR_SHM")
    if (before.st_size, before.st_mtime_ns) != (
        after.st_size,
        after.st_mtime_ns,
    ) or after_sha256 != before_sha256:
        raise RuntimeError("ETABS_SQLITE_EXPORT_CHANGED_DURING_INVENTORY")
    inspected = _utc(inspected_at_utc or datetime.now(UTC), "inspected_at_utc")
    limitations = (
        "C1 records schema metadata and row counts only; C2 parser support is not claimed.",
    )
    basis = {
        "schema_version": "etabs-sqlite-schema-inventory/v1",
        "inventory_status": "COMPLETE",
        "acquisition_mode": "OPERATOR_UI_EXPORT",
        "export_manifest_sha256": manifest.manifest_sha256,
        "artifact_sha256": manifest.artifact_sha256,
        "artifact_size_bytes": manifest.artifact_size_bytes,
        "target_observation_sha256": manifest.target_observation_sha256,
        "runtime_fingerprint_sha256": manifest.runtime_fingerprint_sha256,
        "model_identity_sha256": manifest.model_identity_sha256,
        "result_epoch_sha256": manifest.result_epoch.epoch_sha256,
        "sqlite_version": sqlite_version,
        "application_id": application_id,
        "user_version": user_version,
        "page_size_bytes": page_size,
        "page_count": page_count,
        "integrity_check": "ok",
        "tables": [table.model_dump(mode="json") for table in tables],
        "request_resolutions": [
            resolution.model_dump(mode="json") for resolution in resolutions
        ],
        "inspected_at_utc": inspected.isoformat().replace("+00:00", "Z"),
        "source_stable_during_inspection": True,
        "pending_wal_present": False,
        "pending_shm_present": False,
        "parser_support_claimed": False,
        "limitations": list(limitations),
    }
    return ETABSSQLiteSchemaInventoryV1.model_validate(
        {
            **basis,
            "tables": tuple(tables),
            "request_resolutions": tuple(resolutions),
            "inspected_at_utc": inspected,
            "limitations": limitations,
            "inventory_sha256": _digest(basis),
        }
    )


def build_etabs_installed_sqlite_evidence_v1(
    manifest: ETABSSQLiteExportManifestV1,
    inventory: ETABSSQLiteSchemaInventoryV1,
    /,
) -> ETABSInstalledSQLiteEvidenceV1:
    basis = {
        "schema_version": "etabs-installed-sqlite-evidence/v1",
        "export_manifest": manifest.model_dump(mode="json"),
        "schema_inventory": inventory.model_dump(mode="json"),
        "parser_support_claimed": False,
    }
    return ETABSInstalledSQLiteEvidenceV1.model_validate(
        {
            **basis,
            "export_manifest": manifest,
            "schema_inventory": inventory,
            "evidence_sha256": _digest(basis),
        }
    )
