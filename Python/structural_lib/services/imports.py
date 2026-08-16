# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Fail-closed multi-format CSV import boundary."""

from __future__ import annotations

import csv
import math
import re
from collections import Counter, defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Literal

from structural_lib.core.data_types import ValidationReport
from structural_lib.core.models import (
    BeamBatchInput,
    BeamForces,
    BeamGeometry,
    DesignDefaults,
)

from .adapters import (
    ETABSAdapter,
    GenericCSVAdapter,
    InputAdapter,
    SAFEAdapter,
    STAADAdapter,
)
from .import_ledger import (
    AdapterSelectionV1,
    ImportArtifactV1,
    ImportFieldAction,
    ImportFieldLedgerV1,
    ImportIssueCode,
    ImportIssueV1,
    ImportNormalizationLedgerV1,
    ImportRowLedgerV1,
    ImportStatus,
    ImportTotalsV1,
    LosslessImportResultV1,
)


@dataclass(frozen=True)
class ImportWarnings:
    """Compatibility view for an accepted import."""

    warnings: list[str]
    unmatched_beams: list[str]
    unmatched_forces: list[str]


class LosslessImportBlockedError(ValueError):
    """Raised when the compatibility API cannot expose a safe batch."""

    def __init__(self, result: LosslessImportResultV1):
        self.result = result
        codes = ", ".join(sorted({issue.code.value for issue in result.issues}))
        super().__init__(f"Import blocked: {codes or 'unknown import error'}")


def build_import_design_defaults(
    *,
    fck_mpa: float,
    fy_mpa: float,
    cover_mm: float,
    stirrup_dia_mm: int,
) -> DesignDefaults:
    """Build the explicit import basis at the service boundary.

    The historical core type retains its compatibility name, but these values
    are required caller inputs for strict imports rather than silent defaults.
    UI/IO layers use this service factory and do not import core models.
    """

    return DesignDefaults(
        fck_mpa=fck_mpa,
        fy_mpa=fy_mpa,
        cover_mm=cover_mm,
        # These legacy compatibility fields are not consumed by any import
        # adapter. Keep their values explicit so this strict boundary never
        # relies on Pydantic's structural defaults.
        min_bar_dia_mm=12,
        max_bar_dia_mm=32,
        stirrup_dia_mm=stirrup_dia_mm,
    )


_ADAPTER_FACTORIES: dict[str, type[InputAdapter]] = {
    "etabs": ETABSAdapter,
    "safe": SAFEAdapter,
    "staad": STAADAdapter,
    "generic": GenericCSVAdapter,
}

_NUMERIC_FIELDS = {
    "angle",
    "cover_mm",
    "depth_mm",
    "eff_depth_mm",
    "fck_mpa",
    "fy_mpa",
    "m3",
    "mu_knm",
    "mu_max",
    "mu_min",
    "p",
    "point1_x",
    "point1_y",
    "point1_z",
    "point2_x",
    "point2_y",
    "point2_z",
    "pu_kn",
    "span_mm",
    "station",
    "v2",
    "vu_kn",
    "vu_max",
    "width_mm",
}

_UNITS = {
    "angle": "degree",
    "cover_mm": "mm",
    "depth_mm": "mm",
    "eff_depth_mm": "mm",
    "fck_mpa": "N/mm2",
    "fy_mpa": "N/mm2",
    "m3": "kN-m",
    "mu_knm": "kN-m",
    "mu_max": "kN-m",
    "mu_min": "kN-m",
    "p": "kN",
    "point1_x": "source-coordinate-unit",
    "point1_y": "source-coordinate-unit",
    "point1_z": "source-coordinate-unit",
    "point2_x": "source-coordinate-unit",
    "point2_y": "source-coordinate-unit",
    "point2_z": "source-coordinate-unit",
    "pu_kn": "kN",
    "span_mm": "mm",
    "station": "source-length-unit",
    "v2": "kN",
    "vu_kn": "kN",
    "vu_max": "kN",
    "width_mm": "mm",
}

_CALCULATION_HEADER = re.compile(
    r"(?:moment|shear|axial|force|mu|vu|pu|width|depth|cover|fck|fy|"
    r"span|length|diameter|load)",
    re.IGNORECASE,
)

# These redundant fields are present in the maintained ETABS VBA force export.
# The ETABS force parser deliberately takes section geometry from the separate
# geometry artifact, so the ledger records them as metadata rather than
# silently treating them as force inputs.
_EXPLICIT_METADATA_HEADERS = {"width_mm", "depth_mm", "span_m", "span_mm"}


def _build_adapters() -> list[InputAdapter]:
    return [ETABSAdapter(), SAFEAdapter(), STAADAdapter(), GenericCSVAdapter()]


def _adapter_key(adapter: InputAdapter) -> str:
    if isinstance(adapter, STAADAdapter):
        return "staad"
    return adapter.name.strip().lower()


def _select_adapter_with_evidence(
    *,
    geometry_csv: Path | str,
    forces_csv: Path | str,
    format_hint: str | None,
) -> tuple[InputAdapter | None, AdapterSelectionV1, tuple[ImportIssueV1, ...]]:
    requested = (format_hint or "auto").strip().lower()
    candidates = tuple(
        _adapter_key(adapter)
        for adapter in _build_adapters()
        if adapter.can_handle(geometry_csv) and adapter.can_handle(forces_csv)
    )

    if requested != "auto":
        factory = _ADAPTER_FACTORIES.get(requested)
        if factory is None:
            issue = ImportIssueV1(
                code=ImportIssueCode.UNKNOWN_FORMAT,
                path="format_hint",
                message=f"Unknown import format {requested!r}",
            )
            return (
                None,
                AdapterSelectionV1(
                    requested_format=requested,
                    candidates=candidates,
                    selected_format=None,
                    reason="blocked",
                ),
                (issue,),
            )
        adapter = factory()
        return (
            adapter,
            AdapterSelectionV1(
                requested_format=requested,
                candidates=candidates,
                selected_format=requested,
                reason="explicit",
            ),
            (),
        )

    if len(candidates) != 1:
        code = (
            ImportIssueCode.AMBIGUOUS_FORMAT
            if len(candidates) > 1
            else ImportIssueCode.UNKNOWN_FORMAT
        )
        issue = ImportIssueV1(
            code=code,
            path="format_hint",
            message=(
                "Automatic detection requires exactly one adapter; "
                f"candidates={list(candidates)}"
            ),
        )
        return (
            None,
            AdapterSelectionV1(
                requested_format=requested,
                candidates=candidates,
                selected_format=None,
                reason="blocked",
            ),
            (issue,),
        )

    selected = candidates[0]
    return (
        _ADAPTER_FACTORIES[selected](),
        AdapterSelectionV1(
            requested_format=requested,
            candidates=candidates,
            selected_format=selected,
            reason="unique_auto_detection",
        ),
        (),
    )


def _select_adapter(
    *,
    geometry_csv: Path | str,
    forces_csv: Path | str,
    format_hint: str | None,
) -> InputAdapter:
    """Compatibility selector with explicit/unique fail-closed semantics."""

    adapter, selection, issues = _select_adapter_with_evidence(
        geometry_csv=geometry_csv,
        forces_csv=forces_csv,
        format_hint=format_hint,
    )
    if adapter is None:
        codes = ", ".join(issue.code.value for issue in issues)
        raise ValueError(
            f"Adapter selection blocked ({codes}); candidates={selection.candidates}"
        )
    return adapter


def _column_spec(
    adapter: InputAdapter, role: Literal["geometry", "forces", "combined"]
) -> dict[str, list[str]]:
    if role == "combined":
        merged: dict[str, list[str]] = {}
        for component_role in ("geometry", "forces"):
            for field, aliases in _column_spec(adapter, component_role).items():
                merged.setdefault(field, [])
                merged[field].extend(
                    alias for alias in aliases if alias not in merged[field]
                )
        return merged
    attribute = "GEOMETRY_COLUMNS" if role == "geometry" else "FORCES_COLUMNS"
    value = getattr(adapter, attribute, None)
    return value if isinstance(value, dict) else {}


def _canonical_headers(
    headers: Sequence[str], spec: dict[str, list[str]]
) -> tuple[list[str | None], list[tuple[int, ImportIssueCode, str]]]:
    canonical: list[str | None] = []
    problems: list[tuple[int, ImportIssueCode, str]] = []
    for index, raw_header in enumerate(headers):
        header = raw_header.strip()
        exact = {
            field
            for field, aliases in spec.items()
            if any(header == alias.strip() for alias in aliases)
        }
        matches = exact or {
            field
            for field, aliases in spec.items()
            if any(header.casefold() == alias.strip().casefold() for alias in aliases)
        }
        if len(matches) > 1:
            canonical.append(None)
            problems.append(
                (
                    index,
                    ImportIssueCode.CONFLICTING_HEADER,
                    f"Header {raw_header!r} maps to multiple fields: {sorted(matches)}",
                )
            )
        else:
            canonical.append(next(iter(matches), None))

    by_field: dict[str, list[int]] = defaultdict(list)
    for index, field in enumerate(canonical):
        if field is not None:
            by_field[field].append(index)
    for field, indexes in by_field.items():
        if len(indexes) > 1:
            for index in indexes:
                problems.append(
                    (
                        index,
                        ImportIssueCode.CONFLICTING_HEADER,
                        f"Multiple source headers map to {field!r}",
                    )
                )
    return canonical, problems


def _required_fields(
    adapter: InputAdapter,
    role: Literal["geometry", "forces", "combined"],
    available: set[str],
) -> set[str]:
    if role == "combined":
        return _required_fields(adapter, "geometry", available) | _required_fields(
            adapter, "forces", available
        )
    if role == "geometry":
        if isinstance(adapter, ETABSAdapter):
            return {
                "label",
                "story",
                "point1_x",
                "point1_y",
                "point1_z",
                "point2_x",
                "point2_y",
                "point2_z",
            }
        if isinstance(adapter, GenericCSVAdapter):
            return {
                "beam_id",
                "width_mm",
                "depth_mm",
                "fck_mpa",
                "fy_mpa",
                "cover_mm",
            }
        return {"beam_id"}
    if isinstance(adapter, GenericCSVAdapter):
        return {"beam_id", "mu_knm", "vu_kn"}
    if {"m3", "v2"}.issubset(available):
        return {"beam_id", "m3", "v2"}
    if "mu_max" in available or "vu_max" in available:
        return (
            {"beam_id"}
            | ({"mu_max"} if "mu_max" in available else set())
            | ({"vu_max"} if "vu_max" in available else set())
        )
    return {"beam_id", "m3", "v2"}


def _read_rows(path: Path) -> tuple[bytes, list[str], list[list[str]]]:
    raw = path.read_bytes()
    parsed = list(csv.reader(raw.decode("utf-8-sig").splitlines()))
    if not parsed:
        return raw, [], []
    return raw, [value.strip() for value in parsed[0]], parsed[1:]


def _source_record_id(
    role: Literal["geometry", "forces", "combined"],
    source_row_number: int,
    values: dict[str, str],
    adapter: InputAdapter,
) -> str:
    member = (values.get("beam_id") or values.get("label") or "").strip()
    story = values.get("story", "").strip()
    if not member:
        return f"{role}:row:{source_row_number}"
    member_id = f"{member}_{story}" if story else member
    if role in {"geometry", "combined"} or isinstance(adapter, GenericCSVAdapter):
        return member_id
    case = values.get("case_id", "").strip()
    station = values.get("station", "").strip()
    suffix = ":".join(value for value in (case, station) if value)
    return f"{member_id}:{suffix}" if suffix else member_id


def _artifact_ledger(
    path_value: Path | str,
    *,
    role: Literal["geometry", "forces", "combined"],
    adapter: InputAdapter | None,
    artifact_name: str | None = None,
) -> tuple[ImportArtifactV1, list[ImportRowLedgerV1], list[ImportIssueV1]]:
    path = Path(path_value)
    raw, headers, physical_rows = _read_rows(path)
    artifact = ImportArtifactV1(
        name=artifact_name or path.name,
        sha256=sha256(raw).hexdigest(),
        headers=tuple(headers),
        source_rows=len(physical_rows),
    )
    issues: list[ImportIssueV1] = []
    if not headers:
        issues.append(
            ImportIssueV1(
                code=ImportIssueCode.EMPTY_ARTIFACT,
                path=f"{role}.headers",
                message=f"{role.title()} artifact has no header row",
                artifact_role=role,
            )
        )
    if adapter is None:
        return (
            artifact,
            [
                ImportRowLedgerV1(
                    artifact_role=role,
                    source_row_number=row_number,
                    source_record_id=f"{role}:row:{row_number}",
                    status=ImportStatus.BLOCKED,
                    fields=tuple(
                        ImportFieldLedgerV1(
                            raw_header=header,
                            canonical_field=None,
                            raw_value=(row[index] if index < len(row) else ""),
                            parsed_value=None,
                            units=None,
                            action=ImportFieldAction.REJECTED,
                        )
                        for index, header in enumerate(headers)
                    ),
                )
                for row_number, row in enumerate(physical_rows, start=2)
            ],
            issues,
        )

    canonical, header_problems = _canonical_headers(
        headers, _column_spec(adapter, role)
    )
    header_block_codes: set[ImportIssueCode] = set()
    counts = Counter(header.casefold() for header in headers)
    for index, header in enumerate(headers):
        if counts[header.casefold()] > 1:
            header_problems.append(
                (
                    index,
                    ImportIssueCode.DUPLICATE_HEADER,
                    f"Duplicate source header {header!r}",
                )
            )
    for index, code, message in header_problems:
        header_block_codes.add(code)
        issues.append(
            ImportIssueV1(
                code=code,
                path=f"{role}.headers[{index}]",
                message=message,
                artifact_role=role,
            )
        )

    available = {field for field in canonical if field is not None}
    required = _required_fields(adapter, role, available)
    for field in sorted(required - available):
        header_block_codes.add(ImportIssueCode.MISSING_REQUIRED_HEADER)
        issues.append(
            ImportIssueV1(
                code=ImportIssueCode.MISSING_REQUIRED_HEADER,
                path=f"{role}.headers.{field}",
                message=f"Missing required {role} field {field!r}",
                artifact_role=role,
            )
        )

    rows: list[ImportRowLedgerV1] = []
    for source_row_number, physical_row in enumerate(physical_rows, start=2):
        values: dict[str, str] = {}
        row_codes = set(header_block_codes)
        fields: list[ImportFieldLedgerV1] = []
        for index, header in enumerate(headers):
            raw_value = physical_row[index] if index < len(physical_row) else ""
            stripped = raw_value.strip()
            canonical_field = canonical[index]
            if canonical_field is None:
                explicitly_metadata = header.strip().casefold() in (
                    _EXPLICIT_METADATA_HEADERS
                )
                calculation_like = (
                    bool(_CALCULATION_HEADER.search(header)) and not explicitly_metadata
                )
                action = (
                    ImportFieldAction.REJECTED
                    if calculation_like
                    else ImportFieldAction.METADATA_ONLY
                )
                if calculation_like:
                    row_codes.add(ImportIssueCode.UNKNOWN_CALCULATION_HEADER)
                    issues.append(
                        ImportIssueV1(
                            code=ImportIssueCode.UNKNOWN_CALCULATION_HEADER,
                            path=f"{role}.rows[{source_row_number}].{header}",
                            message=f"Unknown calculation-looking header {header!r}",
                            artifact_role=role,
                            source_row_number=source_row_number,
                        )
                    )
                parsed: str | float | None = stripped or None
            else:
                values[canonical_field] = stripped
                action = ImportFieldAction.NORMALIZED
                parsed = stripped or None
                if not stripped and canonical_field in required:
                    row_codes.add(ImportIssueCode.MISSING_VALUE)
                    issues.append(
                        ImportIssueV1(
                            code=ImportIssueCode.MISSING_VALUE,
                            path=f"{role}.rows[{source_row_number}].{canonical_field}",
                            message=f"Required field {canonical_field!r} is empty",
                            artifact_role=role,
                            source_row_number=source_row_number,
                        )
                    )
                elif stripped and canonical_field in _NUMERIC_FIELDS:
                    try:
                        number = float(stripped)
                    except ValueError:
                        row_codes.add(ImportIssueCode.MALFORMED_NUMBER)
                        action = ImportFieldAction.REJECTED
                        parsed = None
                        issues.append(
                            ImportIssueV1(
                                code=ImportIssueCode.MALFORMED_NUMBER,
                                path=f"{role}.rows[{source_row_number}].{canonical_field}",
                                message=(
                                    f"Field {canonical_field!r} is not a valid number"
                                ),
                                artifact_role=role,
                                source_row_number=source_row_number,
                            )
                        )
                    else:
                        if not math.isfinite(number):
                            row_codes.add(ImportIssueCode.NON_FINITE_NUMBER)
                            action = ImportFieldAction.REJECTED
                            parsed = None
                            issues.append(
                                ImportIssueV1(
                                    code=ImportIssueCode.NON_FINITE_NUMBER,
                                    path=(
                                        f"{role}.rows[{source_row_number}]."
                                        f"{canonical_field}"
                                    ),
                                    message=f"Field {canonical_field!r} must be finite",
                                    artifact_role=role,
                                    source_row_number=source_row_number,
                                )
                            )
                        else:
                            parsed = number
            fields.append(
                ImportFieldLedgerV1(
                    raw_header=header,
                    canonical_field=canonical_field,
                    raw_value=raw_value,
                    parsed_value=parsed,
                    units=_UNITS.get(canonical_field) if canonical_field else None,
                    action=action,
                )
            )

        if len(physical_row) > len(headers):
            row_codes.add(ImportIssueCode.CONFLICTING_HEADER)
            issues.append(
                ImportIssueV1(
                    code=ImportIssueCode.CONFLICTING_HEADER,
                    path=f"{role}.rows[{source_row_number}]",
                    message="Source row contains more values than the header row",
                    artifact_role=role,
                    source_row_number=source_row_number,
                )
            )
        exclusion_reason = None
        if role in {"geometry", "combined"}:
            frame_type = values.get("frame_type", "").casefold()
            if frame_type and frame_type != "beam":
                exclusion_reason = f"non-beam frame_type={values['frame_type']}"
        rows.append(
            ImportRowLedgerV1(
                artifact_role=role,
                source_row_number=source_row_number,
                source_record_id=_source_record_id(
                    role, source_row_number, values, adapter
                ),
                status=ImportStatus.BLOCKED if row_codes else ImportStatus.ACCEPTED,
                fields=tuple(fields),
                issue_codes=tuple(sorted(row_codes, key=lambda code: code.value)),
                exclusion_reason=exclusion_reason,
            )
        )

    identities: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        if row.exclusion_reason is None:
            identities[row.source_record_id].append(index)
    duplicate_indexes = {
        index
        for indexes in identities.values()
        if len(indexes) > 1
        for index in indexes
    }
    for index in sorted(duplicate_indexes):
        row = rows[index]
        code_set = set(row.issue_codes) | {ImportIssueCode.DUPLICATE_RECORD_ID}
        rows[index] = row.model_copy(
            update={
                "status": ImportStatus.BLOCKED,
                "issue_codes": tuple(sorted(code_set, key=lambda code: code.value)),
            }
        )
        issues.append(
            ImportIssueV1(
                code=ImportIssueCode.DUPLICATE_RECORD_ID,
                path=f"{role}.rows[{row.source_row_number}].source_record_id",
                message=f"Duplicate source record identity {row.source_record_id!r}",
                artifact_role=role,
                source_row_number=row.source_row_number,
            )
        )
    return artifact, rows, issues


def parse_single_csv_lossless(
    combined_csv: Path | str,
    *,
    format_hint: str | None = None,
    defaults: DesignDefaults | None = None,
    artifact_name: str | None = None,
) -> LosslessImportResultV1:
    """Parse one combined geometry/actions artifact with physical-row accounting."""

    adapter, selection, selection_issues = _select_adapter_with_evidence(
        geometry_csv=combined_csv,
        forces_csv=combined_csv,
        format_hint=format_hint,
    )
    artifact, rows, ledger_issues = _artifact_ledger(
        combined_csv,
        role="combined",
        adapter=adapter,
        artifact_name=artifact_name,
    )
    issues = list(selection_issues) + ledger_issues
    batch: BeamBatchInput | None = None
    beams: list[BeamGeometry] = []
    forces: list[BeamForces] = []
    unmatched_beams: list[str] = []
    unmatched_forces: list[str] = []

    if (
        adapter is not None
        and not isinstance(adapter, GenericCSVAdapter)
        and defaults is None
    ):
        issues.append(
            ImportIssueV1(
                code=ImportIssueCode.MISSING_PROJECT_DEFAULTS,
                path="defaults",
                message=(
                    "This adapter requires explicit project material, cover, and "
                    "detailing-basis defaults; no structural defaults are supplied."
                ),
            )
        )

    if (
        adapter is not None
        and not issues
        and all(row.status is ImportStatus.ACCEPTED for row in rows)
    ):
        try:
            selected_defaults = defaults or DesignDefaults()  # type: ignore[call-arg]
            beams = adapter.load_geometry(combined_csv, selected_defaults)
            forces = adapter.load_forces(combined_csv)
        except (OSError, TypeError, ValueError, KeyError) as exc:
            issues.append(
                ImportIssueV1(
                    code=ImportIssueCode.ADAPTER_PARSE_ERROR,
                    path="adapter",
                    message=f"Adapter parse failed: {exc}",
                )
            )
        else:
            expected_records = sum(row.exclusion_reason is None for row in rows)
            if len(beams) != expected_records or len(forces) != expected_records:
                issues.append(
                    ImportIssueV1(
                        code=ImportIssueCode.ADAPTER_ROW_LOSS,
                        path="combined",
                        message=(
                            f"Adapter returned {len(beams)} geometry and {len(forces)} "
                            f"force records from {expected_records} accepted source rows"
                        ),
                        artifact_role="combined",
                    )
                )
            duplicates = {
                value
                for value, count in Counter(beam.id for beam in beams).items()
                if count > 1
            } | {
                value
                for value, count in Counter(force.id for force in forces).items()
                if count > 1
            }
            for duplicate in sorted(duplicates):
                issues.append(
                    ImportIssueV1(
                        code=ImportIssueCode.DUPLICATE_RECORD_ID,
                        path="adapter.output",
                        message=(
                            f"Adapter output contains duplicate member ID {duplicate!r}"
                        ),
                    )
                )
            if beams and forces:
                candidate = BeamBatchInput(
                    beams=beams,
                    forces=forces,
                    defaults=selected_defaults,
                )
                unmatched_beams = candidate.get_unmatched_beams()
                unmatched_forces = candidate.get_unmatched_forces()
                for member_id in unmatched_beams:
                    issues.append(
                        ImportIssueV1(
                            code=ImportIssueCode.UNMATCHED_GEOMETRY,
                            path=f"matching.geometry.{member_id}",
                            message=(
                                f"Geometry member {member_id!r} has no matching forces"
                            ),
                        )
                    )
                for member_id in unmatched_forces:
                    issues.append(
                        ImportIssueV1(
                            code=ImportIssueCode.UNMATCHED_FORCE,
                            path=f"matching.forces.{member_id}",
                            message=(
                                f"Force member {member_id!r} has no matching geometry"
                            ),
                        )
                    )
                if not issues:
                    batch = candidate
            else:
                issues.append(
                    ImportIssueV1(
                        code=ImportIssueCode.ADAPTER_ROW_LOSS,
                        path="adapter.output",
                        message="Adapter returned no usable geometry or force records",
                    )
                )

    accepted_rows = sum(row.status is ImportStatus.ACCEPTED for row in rows)
    totals = ImportTotalsV1(
        source_rows=len(rows),
        accepted_rows=accepted_rows,
        blocked_rows=len(rows) - accepted_rows,
        excluded_rows=sum(row.exclusion_reason is not None for row in rows),
        geometry_records=len(beams),
        force_records=len(forces),
        matched_records=len(
            {beam.id for beam in beams} & {force.id for force in forces}
        ),
        unmatched_geometry=len(unmatched_beams),
        unmatched_forces=len(unmatched_forces),
    )
    ledger = ImportNormalizationLedgerV1(
        geometry_artifact=artifact,
        forces_artifact=artifact,
        adapter_selection=selection,
        rows=tuple(rows),
        totals=totals,
    )
    status = (
        ImportStatus.ACCEPTED
        if batch is not None and not issues
        else ImportStatus.BLOCKED
    )
    return LosslessImportResultV1(
        status=status,
        batch=batch,
        ledger=ledger,
        issues=tuple(issues),
    )


def parse_dual_csv_lossless(
    geometry_csv: Path | str,
    forces_csv: Path | str,
    *,
    format_hint: str | None = None,
    defaults: DesignDefaults | None = None,
    geometry_artifact_name: str | None = None,
    forces_artifact_name: str | None = None,
) -> LosslessImportResultV1:
    """Parse two CSV artifacts only when every design-bearing record is safe."""

    adapter, selection, selection_issues = _select_adapter_with_evidence(
        geometry_csv=geometry_csv,
        forces_csv=forces_csv,
        format_hint=format_hint,
    )
    geometry_artifact, geometry_rows, geometry_issues = _artifact_ledger(
        geometry_csv,
        role="geometry",
        adapter=adapter,
        artifact_name=geometry_artifact_name,
    )
    forces_artifact, force_rows, force_issues = _artifact_ledger(
        forces_csv,
        role="forces",
        adapter=adapter,
        artifact_name=forces_artifact_name,
    )
    rows = geometry_rows + force_rows
    issues = list(selection_issues) + geometry_issues + force_issues
    batch: BeamBatchInput | None = None
    beams: list[BeamGeometry] = []
    forces: list[BeamForces] = []
    unmatched_beams: list[str] = []
    unmatched_forces: list[str] = []

    if (
        adapter is not None
        and not isinstance(adapter, GenericCSVAdapter)
        and defaults is None
    ):
        issues.append(
            ImportIssueV1(
                code=ImportIssueCode.MISSING_PROJECT_DEFAULTS,
                path="defaults",
                message=(
                    "This adapter requires explicit project material, cover, and "
                    "detailing-basis defaults; no structural defaults are supplied."
                ),
            )
        )

    if (
        adapter is not None
        and not issues
        and all(row.status is ImportStatus.ACCEPTED for row in rows)
    ):
        try:
            # Generic rows are required to carry these values. The object is
            # therefore a non-consumed adapter argument, not a project default.
            selected_defaults = defaults or DesignDefaults()  # type: ignore[call-arg]
            beams = adapter.load_geometry(geometry_csv, selected_defaults)
            forces = adapter.load_forces(forces_csv)
        except (OSError, TypeError, ValueError, KeyError) as exc:
            issues.append(
                ImportIssueV1(
                    code=ImportIssueCode.ADAPTER_PARSE_ERROR,
                    path="adapter",
                    message=f"Adapter parse failed: {exc}",
                )
            )
        else:
            expected_geometry = sum(
                row.exclusion_reason is None for row in geometry_rows
            )
            if len(beams) != expected_geometry:
                issues.append(
                    ImportIssueV1(
                        code=ImportIssueCode.ADAPTER_ROW_LOSS,
                        path="geometry",
                        message=(
                            f"Adapter returned {len(beams)} geometry records from "
                            f"{expected_geometry} accepted source rows"
                        ),
                        artifact_role="geometry",
                    )
                )
            duplicates = {
                value
                for value, count in Counter(beam.id for beam in beams).items()
                if count > 1
            } | {
                value
                for value, count in Counter(force.id for force in forces).items()
                if count > 1
            }
            for duplicate in sorted(duplicates):
                issues.append(
                    ImportIssueV1(
                        code=ImportIssueCode.DUPLICATE_RECORD_ID,
                        path="adapter.output",
                        message=f"Adapter output contains duplicate member ID {duplicate!r}",
                    )
                )
            if beams and forces:
                candidate = BeamBatchInput(
                    beams=beams, forces=forces, defaults=selected_defaults
                )
                unmatched_beams = candidate.get_unmatched_beams()
                unmatched_forces = candidate.get_unmatched_forces()
                for member_id in unmatched_beams:
                    issues.append(
                        ImportIssueV1(
                            code=ImportIssueCode.UNMATCHED_GEOMETRY,
                            path=f"matching.geometry.{member_id}",
                            message=f"Geometry member {member_id!r} has no matching forces",
                        )
                    )
                for member_id in unmatched_forces:
                    issues.append(
                        ImportIssueV1(
                            code=ImportIssueCode.UNMATCHED_FORCE,
                            path=f"matching.forces.{member_id}",
                            message=f"Force member {member_id!r} has no matching geometry",
                        )
                    )
                if not issues:
                    batch = candidate
            else:
                issues.append(
                    ImportIssueV1(
                        code=ImportIssueCode.ADAPTER_ROW_LOSS,
                        path="adapter.output",
                        message="Adapter returned no usable geometry or force records",
                    )
                )

    accepted_rows = sum(row.status is ImportStatus.ACCEPTED for row in rows)
    totals = ImportTotalsV1(
        source_rows=len(rows),
        accepted_rows=accepted_rows,
        blocked_rows=len(rows) - accepted_rows,
        excluded_rows=sum(row.exclusion_reason is not None for row in rows),
        geometry_records=len(beams),
        force_records=len(forces),
        matched_records=len(
            {beam.id for beam in beams} & {force.id for force in forces}
        ),
        unmatched_geometry=len(unmatched_beams),
        unmatched_forces=len(unmatched_forces),
    )
    ledger = ImportNormalizationLedgerV1(
        geometry_artifact=geometry_artifact,
        forces_artifact=forces_artifact,
        adapter_selection=selection,
        rows=tuple(rows),
        totals=totals,
    )
    status = (
        ImportStatus.ACCEPTED
        if batch is not None and not issues
        else ImportStatus.BLOCKED
    )
    return LosslessImportResultV1(
        status=status,
        batch=batch,
        ledger=ledger,
        issues=tuple(issues),
    )


def parse_dual_csv(
    geometry_csv: Path | str,
    forces_csv: Path | str,
    *,
    format_hint: str | None = None,
    defaults: DesignDefaults | None = None,
) -> tuple[BeamBatchInput, ImportWarnings]:
    """Compatibility facade delegating to the strict lossless boundary."""

    result = parse_dual_csv_lossless(
        geometry_csv, forces_csv, format_hint=format_hint, defaults=defaults
    )
    if result.batch is None:
        raise LosslessImportBlockedError(result)
    return result.batch, ImportWarnings([], [], [])


def merge_geometry_forces(
    geometry_list: Iterable[BeamGeometry],
    forces_list: Iterable[BeamForces],
) -> list[tuple[BeamGeometry, BeamForces]]:
    """Merge geometry and forces by beam ID, returning matched pairs only."""

    forces_by_id = {force.id: force for force in forces_list}
    return [
        (geometry, forces_by_id[geometry.id])
        for geometry in geometry_list
        if geometry.id in forces_by_id
    ]


def validate_import(batch: BeamBatchInput) -> ValidationReport:
    """Validate canonical matching; unaccounted design records block."""

    errors: list[str] = []
    if not batch.beams:
        errors.append("No geometry records found")
    if not batch.forces:
        errors.append("No force records found")
    matched = batch.get_merged_data()
    if not matched:
        errors.append("No matching beam IDs between geometry and forces")
    unmatched_beams = batch.get_unmatched_beams()
    unmatched_forces = batch.get_unmatched_forces()
    if unmatched_beams:
        errors.append(f"{len(unmatched_beams)} beams have no matching forces")
    if unmatched_forces:
        errors.append(f"{len(unmatched_forces)} forces have no matching beams")
    details: dict[str, Any] = {
        "total_beams": len(batch.beams),
        "total_forces": len(batch.forces),
        "matched": len(matched),
        "unmatched_beams": unmatched_beams,
        "unmatched_forces": unmatched_forces,
    }
    return ValidationReport(ok=not errors, errors=errors, warnings=[], details=details)


__all__ = [
    "ImportWarnings",
    "LosslessImportBlockedError",
    "merge_geometry_forces",
    "parse_dual_csv",
    "parse_dual_csv_lossless",
    "parse_single_csv_lossless",
    "validate_import",
]
