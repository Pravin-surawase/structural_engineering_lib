# SPDX-License-Identifier: MIT
"""Versioned, calculation-free contracts for Excel Routine Workbench V1."""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Final, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

__all__ = [
    "EXCEL_WORKBOOK_CONTRACT_SCHEMA_VERSION",
    "EXCEL_WORKBOOK_TEMPLATE_ID",
    "EXCEL_WORKBOOK_TEMPLATE_VERSION",
    "ExcelCalculationModeV1",
    "ExcelCalculationPassportV1",
    "ExcelCapabilityStateV1",
    "ExcelFreshnessCheckV1",
    "ExcelFreshnessRequestV1",
    "ExcelMappingFieldV1",
    "ExcelMappingPreviewV1",
    "ExcelRetainedEvidenceV1",
    "ExcelReviewStateV1",
    "ExcelRowCountV1",
    "ExcelRowDispositionV1",
    "ExcelRowIssueV1",
    "ExcelRowLedgerEntryV1",
    "ExcelTrustModeV1",
    "ExcelWorkbookContractV1",
    "ExcelWorkbookPreviewRequestV1",
    "ExcelWorkbookRunRequestV1",
    "ExcelWorkbookRunResultV1",
    "ExcelWorkbookSelectionV1",
    "ExcelWorkbenchDefinitionV1",
]

EXCEL_WORKBOOK_CONTRACT_SCHEMA_VERSION: Final[Literal["excel-workbook-contract/v1"]] = (
    "excel-workbook-contract/v1"
)
EXCEL_WORKBOOK_TEMPLATE_ID: Final[
    Literal["structural-lib-rectangular-beam-workbench"]
] = "structural-lib-rectangular-beam-workbench"
EXCEL_WORKBOOK_TEMPLATE_VERSION: Final[Literal["1.0"]] = "1.0"
_ID_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9_.:-]*$"
_SHA256_PATTERN = r"^[0-9a-f]{64}$"

ExcelCellValueV1 = str | int | float | bool | None


class _FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", allow_inf_nan=False)


class ExcelCalculationModeV1(StrEnum):
    AUTOMATIC = "AUTOMATIC"
    MANUAL = "MANUAL"
    AUTOMATIC_EXCEPT_TABLES = "AUTOMATIC_EXCEPT_TABLES"


class ExcelTrustModeV1(StrEnum):
    MACRO_FREE_OFFICE_JS = "MACRO_FREE_OFFICE_JS"


class ExcelRowDispositionV1(StrEnum):
    ACCEPTED = "ACCEPTED"
    BLOCKED = "BLOCKED"
    EXCLUDED = "EXCLUDED"


class ExcelReviewStateV1(StrEnum):
    NOT_REVIEWED = "NOT_REVIEWED"
    REVIEW_ACCEPTED = "REVIEW_ACCEPTED"
    REVIEW_REJECTED = "REVIEW_REJECTED"


class ExcelCapabilityStateV1(StrEnum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    TO_VERIFY_WINDOWS = "TO_VERIFY_WINDOWS"


class ExcelWorkbookContractV1(_FrozenModel):
    schema_version: Literal["excel-workbook-contract/v1"] = (
        EXCEL_WORKBOOK_CONTRACT_SCHEMA_VERSION
    )
    template_id: Literal["structural-lib-rectangular-beam-workbench"] = (
        EXCEL_WORKBOOK_TEMPLATE_ID
    )
    template_version: Literal["1.0"] = EXCEL_WORKBOOK_TEMPLATE_VERSION
    input_worksheet: Literal["Beam_Workbench"] = "Beam_Workbench"
    input_table: Literal["tbl_Beam_Workbench_V1"] = "tbl_Beam_Workbench_V1"
    metadata_worksheet: Literal["Workbook_Info"] = "Workbook_Info"
    mapping_worksheet: Literal["Mapping_Preview"] = "Mapping_Preview"
    ledger_worksheet: Literal["Row_Ledger"] = "Row_Ledger"
    result_worksheet: Literal["Results"] = "Results"
    passport_worksheet: Literal["Passports"] = "Passports"
    unit_system: Literal["IS456"] = "IS456"
    torsion_mode: Literal["DISABLED_E1"] = "DISABLED_E1"
    serviceability_mode: Literal["DISABLED_E1"] = "DISABLED_E1"
    trust_mode: Literal[ExcelTrustModeV1.MACRO_FREE_OFFICE_JS] = (
        ExcelTrustModeV1.MACRO_FREE_OFFICE_JS
    )
    required_fields: tuple[str, ...]
    held_scopes: tuple[str, ...]


class ExcelWorkbookSelectionV1(_FrozenModel):
    workbook_instance_id: str = Field(min_length=1, max_length=128, pattern=_ID_PATTERN)
    template_id: Literal["structural-lib-rectangular-beam-workbench"] = (
        EXCEL_WORKBOOK_TEMPLATE_ID
    )
    template_version: Literal["1.0"] = EXCEL_WORKBOOK_TEMPLATE_VERSION
    worksheet_name: Literal["Beam_Workbench"] = "Beam_Workbench"
    table_name: Literal["tbl_Beam_Workbench_V1"] = "tbl_Beam_Workbench_V1"
    first_data_row_number: int = Field(ge=2)
    locale: str = Field(min_length=2, max_length=32)
    decimal_separator: Literal["."] = "."
    calculation_mode: ExcelCalculationModeV1
    unit_system: Literal["IS456"] = "IS456"
    trust_mode: Literal[ExcelTrustModeV1.MACRO_FREE_OFFICE_JS] = (
        ExcelTrustModeV1.MACRO_FREE_OFFICE_JS
    )


class ExcelWorkbookPreviewRequestV1(_FrozenModel):
    schema_version: Literal["excel-workbook-preview-request/v1"] = (
        "excel-workbook-preview-request/v1"
    )
    selection: ExcelWorkbookSelectionV1
    headers: tuple[str, ...] = Field(min_length=1, max_length=128)
    rows: tuple[tuple[ExcelCellValueV1, ...], ...] = Field(max_length=10000)


class ExcelWorkbookRunRequestV1(_FrozenModel):
    schema_version: Literal["excel-workbook-run-request/v1"] = (
        "excel-workbook-run-request/v1"
    )
    selection: ExcelWorkbookSelectionV1
    headers: tuple[str, ...] = Field(min_length=1, max_length=128)
    rows: tuple[tuple[ExcelCellValueV1, ...], ...] = Field(max_length=10000)
    confirmed_mapping_hash: str = Field(pattern=_SHA256_PATTERN)


class ExcelRowIssueV1(_FrozenModel):
    code: str = Field(min_length=1, max_length=128)
    path: str = Field(min_length=1, max_length=512)
    message: str = Field(min_length=1, max_length=1024)


class ExcelMappingFieldV1(_FrozenModel):
    canonical_field: str = Field(min_length=1, max_length=128)
    source_header: str = Field(min_length=1, max_length=256)
    source_column_index: int = Field(ge=0)


class ExcelMappingPreviewV1(_FrozenModel):
    schema_version: Literal["excel-mapping-preview/v1"] = "excel-mapping-preview/v1"
    source_headers: tuple[str, ...]
    mapped_fields: tuple[ExcelMappingFieldV1, ...]
    excluded_headers: tuple[str, ...]
    issues: tuple[ExcelRowIssueV1, ...]
    is_blocked: bool
    mapping_hash: str = Field(pattern=_SHA256_PATTERN)


class ExcelRowCountV1(_FrozenModel):
    source_rows: int = Field(ge=0)
    accepted_rows: int = Field(ge=0)
    blocked_rows: int = Field(ge=0)
    excluded_rows: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_reconciliation(self) -> ExcelRowCountV1:
        if self.source_rows != (
            self.accepted_rows + self.blocked_rows + self.excluded_rows
        ):
            raise ValueError(
                "source_rows must equal accepted_rows + blocked_rows + excluded_rows"
            )
        return self


class ExcelCalculationPassportV1(_FrozenModel):
    schema_version: Literal["excel-calculation-passport/v1"] = (
        "excel-calculation-passport/v1"
    )
    row_id: str = Field(min_length=1, max_length=128)
    beam_id: str = Field(min_length=1, max_length=128)
    case_id: str = Field(min_length=1, max_length=128)
    raw_row_hash: str = Field(pattern=_SHA256_PATTERN)
    normalized_input_hash: str = Field(pattern=_SHA256_PATTERN)
    calculation_identity: str = Field(pattern=_SHA256_PATTERN)
    result_hash: str = Field(pattern=_SHA256_PATTERN)
    library_version: str = Field(min_length=1, max_length=64)
    library_content_identity: str = Field(pattern=_SHA256_PATTERN)
    workbook_selection_hash: str = Field(pattern=_SHA256_PATTERN)
    mapping_hash: str = Field(pattern=_SHA256_PATTERN)
    passport_hash: str = Field(pattern=_SHA256_PATTERN)


class ExcelRowLedgerEntryV1(_FrozenModel):
    source_row_number: int = Field(ge=2)
    raw_values: tuple[ExcelCellValueV1, ...]
    raw_row_hash: str = Field(pattern=_SHA256_PATTERN)
    row_id: str | None = Field(default=None, max_length=128)
    beam_id: str | None = Field(default=None, max_length=128)
    disposition: ExcelRowDispositionV1
    issues: tuple[ExcelRowIssueV1, ...] = ()
    normalized_input: dict[str, Any] | None = None
    result_envelope: dict[str, Any] | None = None
    result: dict[str, Any] | None = None
    passport: ExcelCalculationPassportV1 | None = None


class ExcelWorkbookRunResultV1(_FrozenModel):
    schema_version: Literal["excel-workbook-run-result/v1"] = (
        "excel-workbook-run-result/v1"
    )
    contract: ExcelWorkbookContractV1
    selection: ExcelWorkbookSelectionV1
    workbook_selection_hash: str = Field(pattern=_SHA256_PATTERN)
    source_table_hash: str = Field(pattern=_SHA256_PATTERN)
    mapping: ExcelMappingPreviewV1
    counts: ExcelRowCountV1
    row_ledger: tuple[ExcelRowLedgerEntryV1, ...]
    normalized_input_hash: str = Field(pattern=_SHA256_PATTERN)
    library_version: str = Field(min_length=1, max_length=64)
    library_content_identity: str = Field(pattern=_SHA256_PATTERN)
    review_state: ExcelReviewStateV1 = ExcelReviewStateV1.NOT_REVIEWED
    qualified_review_required: Literal[True] = True
    limitations: tuple[str, ...]
    bundle_hash: str = Field(pattern=_SHA256_PATTERN)


class ExcelRetainedEvidenceV1(_FrozenModel):
    schema_version: Literal["excel-retained-evidence/v1"] = "excel-retained-evidence/v1"
    bundle_hash: str = Field(pattern=_SHA256_PATTERN)
    source_table_hash: str = Field(pattern=_SHA256_PATTERN)
    mapping_hash: str = Field(pattern=_SHA256_PATTERN)
    library_content_identity: str = Field(pattern=_SHA256_PATTERN)


class ExcelFreshnessRequestV1(_FrozenModel):
    schema_version: Literal["excel-freshness-request/v1"] = "excel-freshness-request/v1"
    previous_evidence: ExcelRetainedEvidenceV1
    current_request: ExcelWorkbookPreviewRequestV1


class ExcelFreshnessCheckV1(_FrozenModel):
    schema_version: Literal["excel-freshness-check/v1"] = "excel-freshness-check/v1"
    freshness_status: Literal["CURRENT", "STALE"]
    reasons: tuple[str, ...]
    previous_bundle_hash: str = Field(pattern=_SHA256_PATTERN)
    current_source_table_hash: str = Field(pattern=_SHA256_PATTERN)
    current_mapping_hash: str = Field(pattern=_SHA256_PATTERN)
    current_library_content_identity: str = Field(pattern=_SHA256_PATTERN)


class ExcelWorkbenchDefinitionV1(_FrozenModel):
    schema_version: Literal["excel-workbench-definition/v1"] = (
        "excel-workbench-definition/v1"
    )
    contract: ExcelWorkbookContractV1
    canonical_function: Literal["design_beam_is456"] = "design_beam_is456"
    canonical_result_contract: Literal["canonical-beam-result/v1"] = (
        "canonical-beam-result/v1"
    )
    software_capability: ExcelCapabilityStateV1
    installed_windows_excel_evidence: ExcelCapabilityStateV1
    workbook_artifact_name: Literal[
        "structural-lib-rectangular-beam-workbench-v1.xlsx"
    ] = "structural-lib-rectangular-beam-workbench-v1.xlsx"
    workbook_artifact_sha256: str = Field(pattern=_SHA256_PATTERN)
    workbook_artifact_size_bytes: int = Field(gt=0)
    library_version: str = Field(min_length=1, max_length=64)
    library_content_identity: str = Field(pattern=_SHA256_PATTERN)
    supported_scope: str
    held_scopes: tuple[str, ...]
