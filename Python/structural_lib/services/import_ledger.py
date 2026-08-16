# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Versioned, lossless import evidence models.

The legacy adapters return canonical geometry and force models.  These models
record what happened to every source row and field before those canonical
models are allowed to enter a project calculation path.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from structural_lib.core.models import BeamBatchInput


class ImportStatus(StrEnum):
    """Fail-closed status shared by import rows and the complete result."""

    ACCEPTED = "ACCEPTED"
    BLOCKED = "BLOCKED"


class ImportFieldAction(StrEnum):
    """Disposition of one physical source field."""

    NORMALIZED = "NORMALIZED"
    METADATA_ONLY = "METADATA_ONLY"
    REJECTED = "REJECTED"


class ImportIssueCode(StrEnum):
    """Stable issue codes for the strict import boundary."""

    UNKNOWN_FORMAT = "import.unknown_format"
    AMBIGUOUS_FORMAT = "import.ambiguous_format"
    ADAPTER_MISMATCH = "import.adapter_mismatch"
    EMPTY_ARTIFACT = "import.empty_artifact"
    DUPLICATE_HEADER = "import.duplicate_header"
    CONFLICTING_HEADER = "import.conflicting_header"
    UNKNOWN_CALCULATION_HEADER = "import.unknown_calculation_header"
    MISSING_REQUIRED_HEADER = "import.missing_required_header"
    MISSING_PROJECT_DEFAULTS = "import.missing_project_defaults"
    MISSING_VALUE = "import.missing_value"
    MALFORMED_NUMBER = "import.malformed_number"
    NON_FINITE_NUMBER = "import.non_finite_number"
    DUPLICATE_RECORD_ID = "import.duplicate_record_id"
    ADAPTER_PARSE_ERROR = "import.adapter_parse_error"
    ADAPTER_ROW_LOSS = "import.adapter_row_loss"
    UNMATCHED_GEOMETRY = "import.unmatched_geometry"
    UNMATCHED_FORCE = "import.unmatched_force"


class ImportIssueV1(BaseModel):
    """One deterministic import problem."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    code: ImportIssueCode
    path: str
    message: str
    artifact_role: Literal["geometry", "forces", "combined"] | None = None
    source_row_number: int | None = Field(default=None, ge=2)


class ImportArtifactV1(BaseModel):
    """Identity and physical shape of one imported artifact."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    media_type: Literal["text/csv"] = "text/csv"
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    headers: tuple[str, ...]
    source_rows: int = Field(ge=0)


class AdapterSelectionV1(BaseModel):
    """Explicit evidence for adapter selection."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    requested_format: str
    candidates: tuple[str, ...]
    selected_format: str | None
    reason: Literal["explicit", "unique_auto_detection", "blocked"]


class ImportFieldLedgerV1(BaseModel):
    """Disposition of one field in one physical source row."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    raw_header: str
    canonical_field: str | None
    raw_value: str
    parsed_value: str | float | None
    units: str | None
    action: ImportFieldAction


class ImportRowLedgerV1(BaseModel):
    """Accounting record for one physical CSV row."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    artifact_role: Literal["geometry", "forces", "combined"]
    source_row_number: int = Field(ge=2)
    source_record_id: str
    status: ImportStatus
    fields: tuple[ImportFieldLedgerV1, ...]
    issue_codes: tuple[ImportIssueCode, ...] = ()
    exclusion_reason: str | None = None


class ImportTotalsV1(BaseModel):
    """Conservation totals for both artifacts and their match."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    source_rows: int = Field(ge=0)
    accepted_rows: int = Field(ge=0)
    blocked_rows: int = Field(ge=0)
    excluded_rows: int = Field(ge=0)
    geometry_records: int = Field(ge=0)
    force_records: int = Field(ge=0)
    matched_records: int = Field(ge=0)
    unmatched_geometry: int = Field(ge=0)
    unmatched_forces: int = Field(ge=0)

    @model_validator(mode="after")
    def _rows_are_conserved(self) -> ImportTotalsV1:
        if self.source_rows != self.accepted_rows + self.blocked_rows:
            raise ValueError("source_rows must equal accepted_rows + blocked_rows")
        return self


class ImportNormalizationLedgerV1(BaseModel):
    """Replayable field, row, adapter, and matching evidence."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal["import-ledger-v1"] = "import-ledger-v1"
    geometry_artifact: ImportArtifactV1
    forces_artifact: ImportArtifactV1
    adapter_selection: AdapterSelectionV1
    rows: tuple[ImportRowLedgerV1, ...]
    totals: ImportTotalsV1


class LosslessImportResultV1(BaseModel):
    """Strict import outcome; a blocked result never exposes a batch."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal["lossless-import-result-v1"] = "lossless-import-result-v1"
    status: ImportStatus
    batch: BeamBatchInput | None
    ledger: ImportNormalizationLedgerV1
    issues: tuple[ImportIssueV1, ...]

    @model_validator(mode="after")
    def _blocked_results_do_not_expose_work(self) -> LosslessImportResultV1:
        if self.status is ImportStatus.BLOCKED and self.batch is not None:
            raise ValueError("blocked imports cannot expose a calculable batch")
        if self.status is ImportStatus.ACCEPTED and self.batch is None:
            raise ValueError("accepted imports require a canonical batch")
        return self


__all__ = [
    "AdapterSelectionV1",
    "ImportArtifactV1",
    "ImportFieldAction",
    "ImportFieldLedgerV1",
    "ImportIssueCode",
    "ImportIssueV1",
    "ImportNormalizationLedgerV1",
    "ImportRowLedgerV1",
    "ImportStatus",
    "ImportTotalsV1",
    "LosslessImportResultV1",
]
