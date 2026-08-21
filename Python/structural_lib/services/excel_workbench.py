# SPDX-License-Identifier: MIT
"""Strict selected-table orchestration for Excel Routine Workbench V1."""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from importlib import resources
from numbers import Real
from typing import Any

from structural_lib.core.excel_workbook import (
    ExcelCalculationPassportV1,
    ExcelCapabilityStateV1,
    ExcelFreshnessCheckV1,
    ExcelFreshnessRequestV1,
    ExcelMappingFieldV1,
    ExcelMappingPreviewV1,
    ExcelRetainedEvidenceV1,
    ExcelReviewBundleExportRequestV1,
    ExcelReviewBundleV1,
    ExcelReviewStateV1,
    ExcelRowCountV1,
    ExcelRowDispositionV1,
    ExcelRowIssueV1,
    ExcelRowLedgerEntryV1,
    ExcelWorkbenchDefinitionV1,
    ExcelWorkbookContractV1,
    ExcelWorkbookPreviewRequestV1,
    ExcelWorkbookRunRequestV1,
    ExcelWorkbookRunResultV1,
)
from structural_lib.core.result_contract import (
    CalculationStatus,
    EngineeringStatus,
    IntakeStatus,
    StructuralIssueV1,
    StructuralResultEnvelopeV2,
)
from structural_lib.services.beam_api import design_beam_is456
from structural_lib.services.common_api import get_library_version
from structural_lib.services.evidence import get_library_content_identity
from structural_lib.services.project_beam import EffectiveDepthBasisV1
from structural_lib.services.serialization import to_transport_value

__all__ = [
    "ExcelReviewBundleConflictError",
    "build_excel_review_bundle_v1",
    "build_excel_mapping_preview_v1",
    "check_excel_workbook_freshness_v1",
    "get_excel_workbench_definition_v1",
    "retain_excel_workbook_evidence_v1",
    "render_excel_review_bundle_markdown_v1",
    "run_excel_workbook_v1",
    "serialize_excel_review_bundle_v1",
]

_REQUIRED_FIELDS = (
    "row_id",
    "beam_id",
    "case_id",
    "mu_knm",
    "vu_kn",
    "b_mm",
    "D_mm",
    "depth_basis_mode",
    "d_mm",
    "clear_cover_mm",
    "stirrup_dia_mm",
    "tension_bar_dia_mm",
    "d_dash_mm",
    "asv_mm2",
    "fck_nmm2",
    "fy_nmm2",
    "shear_basis_mode",
)
_HELD_SCOPES = (
    "torsion",
    "serviceability",
    "flanged beams",
    "columns, slabs, footings, and other components",
    "ETABS acquisition or write-back",
    "professional approval",
)
_EXACT_HEADER_ALIASES = {
    "Row ID": "row_id",
    "Beam ID": "beam_id",
    "Case ID": "case_id",
    "Mu (kN·m)": "mu_knm",
    "Mu (kNm)": "mu_knm",
    "Vu (kN)": "vu_kn",
    "b (mm)": "b_mm",
    "D (mm)": "D_mm",
    "D_mm": "D_mm",
    "Depth Basis": "depth_basis_mode",
    "d (mm)": "d_mm",
    "d_mm": "d_mm",
    "Clear Cover (mm)": "clear_cover_mm",
    "Stirrup Dia (mm)": "stirrup_dia_mm",
    "Tension Bar Dia (mm)": "tension_bar_dia_mm",
    "d' (mm)": "d_dash_mm",
    "Asv (mm²)": "asv_mm2",
    "Asv (mm2)": "asv_mm2",
    "fck (N/mm²)": "fck_nmm2",
    "fck (N/mm2)": "fck_nmm2",
    "fy (N/mm²)": "fy_nmm2",
    "fy (N/mm2)": "fy_nmm2",
    "Shear Basis": "shear_basis_mode",
}
_FOLDED_HEADER_ALIASES = {
    "row id": "row_id",
    "row_id": "row_id",
    "beam id": "beam_id",
    "beam_id": "beam_id",
    "beamid": "beam_id",
    "case id": "case_id",
    "case_id": "case_id",
    "mu_knm": "mu_knm",
    "vu_kn": "vu_kn",
    "b_mm": "b_mm",
    "depth basis": "depth_basis_mode",
    "depth_basis_mode": "depth_basis_mode",
    "d_mm": "d_mm",
    "clear cover": "clear_cover_mm",
    "clear_cover_mm": "clear_cover_mm",
    "stirrup dia": "stirrup_dia_mm",
    "stirrup_dia_mm": "stirrup_dia_mm",
    "tension bar dia": "tension_bar_dia_mm",
    "tension_bar_dia_mm": "tension_bar_dia_mm",
    "d_dash_mm": "d_dash_mm",
    "asv_mm2": "asv_mm2",
    "fck_nmm2": "fck_nmm2",
    "fy_nmm2": "fy_nmm2",
    "shear basis": "shear_basis_mode",
    "shear_basis_mode": "shear_basis_mode",
}
_KNOWN_HELD_HEADERS = {
    "tu",
    "tu_knm",
    "torsion",
    "serviceability",
    "deflection",
    "crack width",
    "beam type",
    "flange width",
    "flange depth",
}
_WORKBOOK_ARTIFACT_NAME = "structural-lib-rectangular-beam-workbench-v1.xlsx"
_WORKBOOK_RESOURCE_DIR = "data/excel/outputs/e1-excel-routine-workbench"


def _workbook_artifact_identity() -> tuple[str, int]:
    package_root = resources.files("structural_lib")
    resource_dir = package_root.joinpath(_WORKBOOK_RESOURCE_DIR)
    manifest = json.loads(
        resource_dir.joinpath("workbook-manifest.json").read_text(encoding="utf-8")
    )
    payload = resource_dir.joinpath(_WORKBOOK_ARTIFACT_NAME).read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if manifest.get("artifact_sha256") != digest:
        raise RuntimeError("Installed Excel workbook does not match its manifest hash.")
    if manifest.get("artifact_size_bytes") != len(payload):
        raise RuntimeError("Installed Excel workbook does not match its manifest size.")
    return digest, len(payload)


def _canonical_json_hash(value: Any) -> str:
    payload = to_transport_value(value)
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _canonical_json_bytes(value: Any) -> bytes:
    payload = to_transport_value(value)
    return (
        json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


class ExcelReviewBundleConflictError(ValueError):
    """The retained result identity conflicts with the current workbook state."""


def _contract() -> ExcelWorkbookContractV1:
    return ExcelWorkbookContractV1(
        required_fields=_REQUIRED_FIELDS,
        held_scopes=_HELD_SCOPES,
    )


def get_excel_workbench_definition_v1() -> ExcelWorkbenchDefinitionV1:
    workbook_sha256, workbook_size = _workbook_artifact_identity()
    return ExcelWorkbenchDefinitionV1(
        contract=_contract(),
        software_capability=ExcelCapabilityStateV1.AVAILABLE,
        installed_windows_excel_evidence=ExcelCapabilityStateV1.TO_VERIFY_WINDOWS,
        workbook_artifact_sha256=workbook_sha256,
        workbook_artifact_size_bytes=workbook_size,
        library_version=get_library_version(),
        library_content_identity=get_library_content_identity(),
        supported_scope=(
            "One selected rectangular-beam strength table using explicit IS 456 "
            "units and the canonical design_beam_is456 result."
        ),
        held_scopes=_HELD_SCOPES,
    )


def _header_key(header: str) -> str:
    return re.sub(r"\s+", " ", header.strip()).casefold()


def _mapped_header(header: str) -> str | None:
    stripped = header.strip()
    exact = _EXACT_HEADER_ALIASES.get(stripped)
    if exact is not None:
        return exact
    return _FOLDED_HEADER_ALIASES.get(_header_key(stripped))


def _issue(code: str, path: str, message: str) -> ExcelRowIssueV1:
    return ExcelRowIssueV1(code=code, path=path, message=message)


def build_excel_mapping_preview_v1(
    request: ExcelWorkbookPreviewRequestV1,
) -> ExcelMappingPreviewV1:
    fields: list[ExcelMappingFieldV1] = []
    excluded: list[str] = []
    issues: list[ExcelRowIssueV1] = []
    mapped: dict[str, list[ExcelMappingFieldV1]] = {}
    seen_headers: Counter[str] = Counter()

    for index, original in enumerate(request.headers):
        header = original.strip()
        if not header:
            issues.append(
                _issue(
                    "E_EXCEL_HEADER_BLANK",
                    f"headers[{index}]",
                    "Header cells must be nonblank.",
                )
            )
            continue
        seen_headers[re.sub(r"\s+", " ", header)] += 1
        canonical = _mapped_header(header)
        if canonical is None:
            excluded.append(header)
            continue
        field = ExcelMappingFieldV1(
            canonical_field=canonical,
            source_header=header,
            source_column_index=index,
        )
        fields.append(field)
        mapped.setdefault(canonical, []).append(field)

    for header_key, count in sorted(seen_headers.items()):
        if count > 1:
            issues.append(
                _issue(
                    "E_EXCEL_HEADER_DUPLICATE",
                    "headers",
                    f"Header {header_key!r} appears {count} times.",
                )
            )
    for canonical, candidates in sorted(mapped.items()):
        if len(candidates) > 1:
            issues.append(
                _issue(
                    "E_EXCEL_MAPPING_DUPLICATE",
                    f"mapping.{canonical}",
                    f"Multiple source columns map to {canonical}.",
                )
            )
    for missing in sorted(set(_REQUIRED_FIELDS) - set(mapped)):
        issues.append(
            _issue(
                "E_EXCEL_MAPPING_REQUIRED",
                f"mapping.{missing}",
                f"Required Excel field {missing} is not mapped.",
            )
        )

    payload = {
        "source_headers": list(request.headers),
        "mapped_fields": [item.model_dump(mode="json") for item in fields],
        "excluded_headers": excluded,
        "issues": [item.model_dump(mode="json") for item in issues],
    }
    return ExcelMappingPreviewV1(
        source_headers=request.headers,
        mapped_fields=tuple(fields),
        excluded_headers=tuple(excluded),
        issues=tuple(issues),
        is_blocked=bool(issues),
        mapping_hash=_canonical_json_hash(payload),
    )


def _is_blank(value: object) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _strict_identifier(
    value: object, path: str, issues: list[ExcelRowIssueV1]
) -> str | None:
    if not isinstance(value, str) or not value.strip():
        issues.append(
            _issue("E_EXCEL_TEXT_REQUIRED", path, "A nonblank text value is required.")
        )
        return None
    return value.strip()


def _strict_number(
    value: object,
    path: str,
    issues: list[ExcelRowIssueV1],
    *,
    positive: bool = True,
) -> float | None:
    if isinstance(value, bool) or not isinstance(value, Real):
        issues.append(
            _issue(
                "E_EXCEL_NUMBER_REQUIRED",
                path,
                "A typed numeric Excel cell is required; numeric text is not accepted.",
            )
        )
        return None
    result = float(value)
    if not math.isfinite(result):
        issues.append(
            _issue("E_EXCEL_NUMBER_NONFINITE", path, "The value must be finite.")
        )
        return None
    if positive and result <= 0:
        issues.append(
            _issue(
                "E_EXCEL_NUMBER_POSITIVE", path, "The value must be greater than zero."
            )
        )
        return None
    if not positive and result < 0:
        issues.append(
            _issue(
                "E_EXCEL_NUMBER_NONNEGATIVE", path, "The value must not be negative."
            )
        )
        return None
    return result


def _blocked_envelope(issues: Sequence[ExcelRowIssueV1]) -> dict[str, Any]:
    held_scope_only = bool(issues) and all(
        item.code == "E_EXCEL_UNSUPPORTED_E1_SCOPE" for item in issues
    )
    envelope = StructuralResultEnvelopeV2(
        intake_status=IntakeStatus.PARTIAL if held_scope_only else IntakeStatus.BLOCKED,
        calculation_status=CalculationStatus.NOT_EVALUATED,
        engineering_status=EngineeringStatus.HOLD,
        issues=tuple(
            StructuralIssueV1(code=item.code, path=item.path, message=item.message)
            for item in issues
        ),
    )
    return envelope.to_dict()


def _calculation_error_envelope(exc: Exception, row_path: str) -> dict[str, Any]:
    envelope = StructuralResultEnvelopeV2(
        intake_status=IntakeStatus.VALID,
        calculation_status=CalculationStatus.ERROR,
        engineering_status=EngineeringStatus.HOLD,
        issues=(
            StructuralIssueV1(
                code="E_EXCEL_CANONICAL_CALCULATION",
                path=row_path,
                message=str(exc),
            ),
        ),
    )
    return envelope.to_dict()


def _row_mapping(preview: ExcelMappingPreviewV1) -> dict[str, int]:
    return {
        field.canonical_field: field.source_column_index
        for field in preview.mapped_fields
    }


def _row_values(raw: Sequence[object], mapping: Mapping[str, int]) -> dict[str, object]:
    return {name: raw[index] for name, index in mapping.items()}


def _nonblank_held_headers(
    raw: Sequence[object], headers: Sequence[str], excluded_headers: Sequence[str]
) -> list[str]:
    excluded_keys = {_header_key(item) for item in excluded_headers}
    held: list[str] = []
    for index, header in enumerate(headers):
        key = _header_key(header)
        if (
            key in excluded_keys
            and key in _KNOWN_HELD_HEADERS
            and index < len(raw)
            and not _is_blank(raw[index])
        ):
            held.append(header.strip())
    return held


def _normalize_row(
    values: Mapping[str, object], row_path: str
) -> tuple[dict[str, Any] | None, list[ExcelRowIssueV1], str | None, str | None]:
    issues: list[ExcelRowIssueV1] = []
    row_id = _strict_identifier(values.get("row_id"), f"{row_path}.row_id", issues)
    beam_id = _strict_identifier(values.get("beam_id"), f"{row_path}.beam_id", issues)
    case_id = _strict_identifier(values.get("case_id"), f"{row_path}.case_id", issues)
    mode = _strict_identifier(
        values.get("depth_basis_mode"), f"{row_path}.depth_basis_mode", issues
    )
    shear_mode = _strict_identifier(
        values.get("shear_basis_mode"), f"{row_path}.shear_basis_mode", issues
    )
    numeric = {
        "mu_knm": _strict_number(
            values.get("mu_knm"), f"{row_path}.mu_knm", issues, positive=False
        ),
        "vu_kn": _strict_number(
            values.get("vu_kn"), f"{row_path}.vu_kn", issues, positive=False
        ),
        "b_mm": _strict_number(values.get("b_mm"), f"{row_path}.b_mm", issues),
        "D_mm": _strict_number(values.get("D_mm"), f"{row_path}.D_mm", issues),
        "stirrup_dia_mm": _strict_number(
            values.get("stirrup_dia_mm"), f"{row_path}.stirrup_dia_mm", issues
        ),
        "asv_mm2": _strict_number(values.get("asv_mm2"), f"{row_path}.asv_mm2", issues),
        "fck_nmm2": _strict_number(
            values.get("fck_nmm2"), f"{row_path}.fck_nmm2", issues
        ),
        "fy_nmm2": _strict_number(values.get("fy_nmm2"), f"{row_path}.fy_nmm2", issues),
    }
    if shear_mode is not None and shear_mode != "AUTO_FROM_FLEXURE":
        issues.append(
            _issue(
                "E_EXCEL_SHEAR_BASIS_UNSUPPORTED",
                f"{row_path}.shear_basis_mode",
                "E1 accepts only AUTO_FROM_FLEXURE.",
            )
        )

    d_mm: float | None = None
    d_dash_mm: float | None = None
    basis: dict[str, float] | None = None
    if mode == "EXPLICIT_D":
        d_mm = _strict_number(values.get("d_mm"), f"{row_path}.d_mm", issues)
        d_dash_mm = _strict_number(
            values.get("d_dash_mm"), f"{row_path}.d_dash_mm", issues
        )
        for name in ("clear_cover_mm", "tension_bar_dia_mm"):
            if not _is_blank(values.get(name)):
                issues.append(
                    _issue(
                        "E_EXCEL_DEPTH_CONFLICT",
                        f"{row_path}.{name}",
                        f"{name} must be blank when depth_basis_mode is EXPLICIT_D.",
                    )
                )
    elif mode == "DERIVED_FROM_BARS":
        for name in ("d_mm", "d_dash_mm"):
            if not _is_blank(values.get(name)):
                issues.append(
                    _issue(
                        "E_EXCEL_DEPTH_CONFLICT",
                        f"{row_path}.{name}",
                        f"{name} must be blank when depth is derived from bars.",
                    )
                )
        cover = _strict_number(
            values.get("clear_cover_mm"), f"{row_path}.clear_cover_mm", issues
        )
        tension = _strict_number(
            values.get("tension_bar_dia_mm"),
            f"{row_path}.tension_bar_dia_mm",
            issues,
        )
        if (
            cover is not None
            and tension is not None
            and numeric["stirrup_dia_mm"] is not None
        ):
            basis = {
                "clear_cover_mm": cover,
                "stirrup_diameter_mm": numeric["stirrup_dia_mm"],
                "tension_bar_diameter_mm": tension,
            }
    elif mode is not None:
        issues.append(
            _issue(
                "E_EXCEL_DEPTH_MODE",
                f"{row_path}.depth_basis_mode",
                "Depth basis must be EXPLICIT_D or DERIVED_FROM_BARS.",
            )
        )

    if issues:
        return None, issues, row_id, beam_id
    assert row_id is not None and beam_id is not None and case_id is not None
    normalized: dict[str, Any] = {
        "units": "IS456",
        "case_id": case_id,
        "mu_knm": numeric["mu_knm"],
        "vu_kn": numeric["vu_kn"],
        "b_mm": numeric["b_mm"],
        "D_mm": numeric["D_mm"],
        "d_mm": d_mm,
        "fck_nmm2": numeric["fck_nmm2"],
        "fy_nmm2": numeric["fy_nmm2"],
        "d_dash_mm": d_dash_mm,
        "asv_mm2": numeric["asv_mm2"],
        "pt_percent": None,
        "ast_mm2_for_shear": None,
        "tu_knm": 0.0,
        "cover_mm": None,
        "stirrup_dia_mm": numeric["stirrup_dia_mm"],
        "effective_depth_basis": basis,
    }
    return normalized, issues, row_id, beam_id


def _source_table_hash(request: ExcelWorkbookPreviewRequestV1) -> str:
    return _canonical_json_hash(
        {
            "selection": request.selection.model_dump(mode="json"),
            "headers": request.headers,
            "rows": request.rows,
        }
    )


def _selection_hash(request: ExcelWorkbookPreviewRequestV1) -> str:
    return _canonical_json_hash(request.selection.model_dump(mode="json"))


def _passport(
    *,
    row_id: str,
    beam_id: str,
    case_id: str,
    raw_row_hash: str,
    result: dict[str, Any],
    selection_hash: str,
    mapping_hash: str,
    library_content_identity: str,
) -> ExcelCalculationPassportV1:
    envelope = result["result_envelope"]
    identity = envelope["result_identity"]
    result_hash = _canonical_json_hash(result)
    payload = {
        "row_id": row_id,
        "beam_id": beam_id,
        "case_id": case_id,
        "raw_row_hash": raw_row_hash,
        "normalized_input_hash": identity["input_hash"],
        "calculation_identity": identity["calculation_identity"],
        "result_hash": result_hash,
        "library_version": identity["library_version"],
        "library_content_identity": library_content_identity,
        "workbook_selection_hash": selection_hash,
        "mapping_hash": mapping_hash,
    }
    return ExcelCalculationPassportV1(
        **payload,
        passport_hash=_canonical_json_hash(payload),
    )


def run_excel_workbook_v1(
    request: ExcelWorkbookRunRequestV1,
) -> ExcelWorkbookRunResultV1:
    preview_request = ExcelWorkbookPreviewRequestV1(
        selection=request.selection,
        headers=request.headers,
        rows=request.rows,
    )
    preview = build_excel_mapping_preview_v1(preview_request)
    if preview.is_blocked:
        raise ValueError("Excel mapping preview is blocked; calculation did not run.")
    if request.confirmed_mapping_hash != preview.mapping_hash:
        raise ValueError(
            "confirmed_mapping_hash does not match the current mapping preview"
        )

    mapping = _row_mapping(preview)
    row_ids = []
    for raw in request.rows:
        if len(raw) == len(request.headers) and not all(
            _is_blank(value) for value in raw
        ):
            value = raw[mapping["row_id"]]
            if isinstance(value, str) and value.strip():
                row_ids.append(value.strip())
    duplicate_ids = {item for item, count in Counter(row_ids).items() if count > 1}

    selection_hash = _selection_hash(preview_request)
    library_content_identity = get_library_content_identity()
    ledger: list[ExcelRowLedgerEntryV1] = []
    normalized_inputs: list[dict[str, Any]] = []
    for offset, raw in enumerate(request.rows):
        source_row = request.selection.first_data_row_number + offset
        row_path = f"rows[{offset}]"
        raw_row_hash = _canonical_json_hash(list(raw))
        if all(_is_blank(value) for value in raw):
            ledger.append(
                ExcelRowLedgerEntryV1(
                    source_row_number=source_row,
                    raw_values=raw,
                    raw_row_hash=raw_row_hash,
                    disposition=ExcelRowDispositionV1.EXCLUDED,
                    issues=(
                        _issue(
                            "I_EXCEL_BLANK_SOURCE_ROW",
                            row_path,
                            "Blank source row was counted and explicitly excluded.",
                        ),
                    ),
                )
            )
            continue

        issues: list[ExcelRowIssueV1] = []
        if len(raw) != len(request.headers):
            issues.append(
                _issue(
                    "E_EXCEL_ROW_WIDTH",
                    row_path,
                    f"Row has {len(raw)} cells but the selected table has {len(request.headers)} headers.",
                )
            )
            values: dict[str, object] = {}
            row_id = beam_id = None
            normalized = None
        else:
            values = _row_values(raw, mapping)
            normalized, row_issues, row_id, beam_id = _normalize_row(values, row_path)
            issues.extend(row_issues)
            held_headers = _nonblank_held_headers(
                raw, request.headers, preview.excluded_headers
            )
            if held_headers:
                issues.append(
                    _issue(
                        "E_EXCEL_UNSUPPORTED_E1_SCOPE",
                        row_path,
                        "E1 does not calculate populated held-scope columns: "
                        + ", ".join(held_headers),
                    )
                )
            if row_id in duplicate_ids:
                issues.append(
                    _issue(
                        "E_EXCEL_ROW_ID_DUPLICATE",
                        f"{row_path}.row_id",
                        f"row_id {row_id!r} is duplicated in the selected table.",
                    )
                )

        if issues or normalized is None or row_id is None or beam_id is None:
            ledger.append(
                ExcelRowLedgerEntryV1(
                    source_row_number=source_row,
                    raw_values=raw,
                    raw_row_hash=raw_row_hash,
                    row_id=row_id,
                    beam_id=beam_id,
                    disposition=ExcelRowDispositionV1.BLOCKED,
                    issues=tuple(issues),
                    result_envelope=_blocked_envelope(issues),
                )
            )
            continue

        normalized_inputs.append(normalized)
        call = dict(normalized)
        basis = call.pop("effective_depth_basis")
        if basis is not None:
            call["effective_depth_basis"] = EffectiveDepthBasisV1(**basis)
        try:
            canonical = to_transport_value(design_beam_is456(**call))
            assert isinstance(canonical, dict)
            passport = _passport(
                row_id=row_id,
                beam_id=beam_id,
                case_id=str(normalized["case_id"]),
                raw_row_hash=raw_row_hash,
                result=canonical,
                selection_hash=selection_hash,
                mapping_hash=preview.mapping_hash,
                library_content_identity=library_content_identity,
            )
            ledger.append(
                ExcelRowLedgerEntryV1(
                    source_row_number=source_row,
                    raw_values=raw,
                    raw_row_hash=raw_row_hash,
                    row_id=row_id,
                    beam_id=beam_id,
                    disposition=ExcelRowDispositionV1.ACCEPTED,
                    normalized_input=normalized,
                    result_envelope=canonical["result_envelope"],
                    result=canonical,
                    passport=passport,
                )
            )
        except (TypeError, ValueError) as exc:
            ledger.append(
                ExcelRowLedgerEntryV1(
                    source_row_number=source_row,
                    raw_values=raw,
                    raw_row_hash=raw_row_hash,
                    row_id=row_id,
                    beam_id=beam_id,
                    disposition=ExcelRowDispositionV1.ACCEPTED,
                    normalized_input=normalized,
                    result_envelope=_calculation_error_envelope(exc, row_path),
                    issues=(
                        _issue(
                            "E_EXCEL_CANONICAL_CALCULATION",
                            row_path,
                            str(exc),
                        ),
                    ),
                )
            )

    counts = ExcelRowCountV1(
        source_rows=len(ledger),
        accepted_rows=sum(
            item.disposition is ExcelRowDispositionV1.ACCEPTED for item in ledger
        ),
        blocked_rows=sum(
            item.disposition is ExcelRowDispositionV1.BLOCKED for item in ledger
        ),
        excluded_rows=sum(
            item.disposition is ExcelRowDispositionV1.EXCLUDED for item in ledger
        ),
    )
    contract = _contract()
    source_table_hash = _source_table_hash(preview_request)
    normalized_input_hash = _canonical_json_hash(normalized_inputs)
    library_version = get_library_version()
    payload = {
        "contract": contract.model_dump(mode="json"),
        "selection": request.selection.model_dump(mode="json"),
        "workbook_selection_hash": selection_hash,
        "source_table_hash": source_table_hash,
        "mapping": preview.model_dump(mode="json"),
        "counts": counts.model_dump(mode="json"),
        "row_ledger": [item.model_dump(mode="json") for item in ledger],
        "normalized_input_hash": normalized_input_hash,
        "library_version": library_version,
        "library_content_identity": library_content_identity,
        "review_state": "NOT_REVIEWED",
        "qualified_review_required": True,
        "limitations": _HELD_SCOPES,
    }
    return ExcelWorkbookRunResultV1(
        contract=contract,
        selection=request.selection,
        workbook_selection_hash=selection_hash,
        source_table_hash=source_table_hash,
        mapping=preview,
        counts=counts,
        row_ledger=tuple(ledger),
        normalized_input_hash=normalized_input_hash,
        library_version=library_version,
        library_content_identity=library_content_identity,
        review_state=ExcelReviewStateV1.NOT_REVIEWED,
        qualified_review_required=True,
        limitations=_HELD_SCOPES,
        bundle_hash=_canonical_json_hash(payload),
    )


def check_excel_workbook_freshness_v1(
    request: ExcelFreshnessRequestV1,
) -> ExcelFreshnessCheckV1:
    preview = build_excel_mapping_preview_v1(request.current_request)
    current_source_hash = _source_table_hash(request.current_request)
    current_library_identity = get_library_content_identity()
    reasons: list[str] = []
    if request.previous_evidence.source_table_hash != current_source_hash:
        reasons.append("SOURCE_TABLE_CHANGED")
    if request.previous_evidence.mapping_hash != preview.mapping_hash:
        reasons.append("MAPPING_CHANGED")
    if request.previous_evidence.library_content_identity != current_library_identity:
        reasons.append("ENGINE_CHANGED")
    return ExcelFreshnessCheckV1(
        freshness_status="STALE" if reasons else "CURRENT",
        reasons=tuple(reasons),
        previous_bundle_hash=request.previous_evidence.bundle_hash,
        current_source_table_hash=current_source_hash,
        current_mapping_hash=preview.mapping_hash,
        current_library_content_identity=current_library_identity,
    )


def retain_excel_workbook_evidence_v1(
    result: ExcelWorkbookRunResultV1,
) -> ExcelRetainedEvidenceV1:
    return ExcelRetainedEvidenceV1(
        bundle_hash=result.bundle_hash,
        source_table_hash=result.source_table_hash,
        mapping_hash=result.mapping.mapping_hash,
        library_content_identity=result.library_content_identity,
    )


def build_excel_review_bundle_v1(
    request: ExcelReviewBundleExportRequestV1,
) -> ExcelReviewBundleV1:
    preview = build_excel_mapping_preview_v1(request.current_request)
    if preview.is_blocked:
        raise ValueError(
            "Excel mapping preview is blocked; review bundle was not exported."
        )
    if request.confirmed_mapping_hash != preview.mapping_hash:
        raise ValueError(
            "confirmed_mapping_hash does not match the current mapping preview"
        )
    if request.previous_evidence.mapping_hash != request.confirmed_mapping_hash:
        raise ExcelReviewBundleConflictError(
            "Retained mapping identity does not match the confirmed mapping."
        )

    freshness = check_excel_workbook_freshness_v1(
        ExcelFreshnessRequestV1(
            previous_evidence=request.previous_evidence,
            current_request=request.current_request,
        )
    )
    if freshness.freshness_status != "CURRENT":
        raise ExcelReviewBundleConflictError(
            "Retained Excel result is stale: " + ", ".join(freshness.reasons)
        )

    result = run_excel_workbook_v1(
        ExcelWorkbookRunRequestV1(
            selection=request.current_request.selection,
            headers=request.current_request.headers,
            rows=request.current_request.rows,
            confirmed_mapping_hash=request.confirmed_mapping_hash,
        )
    )
    if result.bundle_hash != request.previous_evidence.bundle_hash:
        raise ExcelReviewBundleConflictError(
            "Regenerated result identity does not match the retained result."
        )

    payload = {
        "schema_version": "excel-review-bundle/v1",
        "export_disposition": "EVIDENCE_FOR_QUALIFIED_REVIEW",
        "freshness_check": freshness.model_dump(mode="json"),
        "result": result.model_dump(mode="json"),
    }
    return ExcelReviewBundleV1(
        freshness_check=freshness,
        result=result,
        review_bundle_hash=_canonical_json_hash(payload),
    )


def serialize_excel_review_bundle_v1(bundle: ExcelReviewBundleV1) -> bytes:
    """Return deterministic complete review evidence as UTF-8 JSON plus one LF."""

    return _canonical_json_bytes(bundle.model_dump(mode="json"))


def render_excel_review_bundle_markdown_v1(
    result: ExcelWorkbookRunResultV1,
) -> str:
    lines = [
        "# Excel Routine Workbench V1 Review Bundle",
        "",
        f"- Workbook: `{result.selection.workbook_instance_id}`",
        f"- Template: `{result.selection.template_id}` v{result.selection.template_version}",
        f"- Table: `{result.selection.worksheet_name}` / `{result.selection.table_name}`",
        f"- Bundle hash: `{result.bundle_hash}`",
        f"- Mapping hash: `{result.mapping.mapping_hash}`",
        f"- Library version: `{result.library_version}`",
        "- Qualified review required: `true`",
        "",
        "## Row reconciliation",
        "",
        f"- Source: {result.counts.source_rows}",
        f"- Accepted: {result.counts.accepted_rows}",
        f"- Blocked: {result.counts.blocked_rows}",
        f"- Excluded: {result.counts.excluded_rows}",
        "",
        "## Rows",
        "",
        "| Excel row | Row ID | Beam ID | Intake | Calculation | Engineering | Freshness | Overall |",
        "|---:|---|---|---|---|---|---|---|",
    ]
    for item in result.row_ledger:
        envelope = item.result_envelope or {}
        lines.append(
            "| "
            + " | ".join(
                [
                    str(item.source_row_number),
                    item.row_id or "-",
                    item.beam_id or "-",
                    str(envelope.get("intake_status", "-")),
                    str(envelope.get("calculation_status", "-")),
                    str(envelope.get("engineering_status", "-")),
                    str(envelope.get("freshness_status", "-")),
                    str(envelope.get("overall_status", item.disposition.value)),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "This review bundle is calculation evidence, not professional approval.",
            "",
        ]
    )
    return "\n".join(lines)
