"""Portable intake of paired ETABS 22.7.0 Element Forces table projections."""

from __future__ import annotations

import csv
import hashlib
import io
import math
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Literal

from structural_lib.beam.analysis import (
    ActionConcurrency,
    ForceUnit,
    LengthUnit,
    LocalAxes,
    MomentUnit,
    RawActionRow,
    RawActionSnapshot,
    Vector3,
    normalize_action_snapshot,
)
from structural_lib.beam.semantics import (
    Diagnostic,
    EngineeringState,
    ExecutionState,
    FreshnessState,
    OperationResult,
    Provenance,
    completed_result,
    effective_inputs,
    partial_result,
    rejected_result,
    semantic_hash,
)

__all__ = [
    "EtabsActionBasis",
    "EtabsCombination",
    "EtabsForceTable",
    "EtabsMemberBinding",
    "EtabsPairedForcesRequest",
    "EtabsTableUnits",
    "import_etabs_paired_forces",
]

_OPERATION = "structural.etabs_paired_forces.import/v1"
_PROVENANCE = Provenance(
    "no-code-calculation",
    "etabs-22.7.0-element-forces-paired-v1",
    (
        "CSI ETABS 22.7.0 Element Forces - Beams / Columns",
        "CSI ETABS Analysis Reference Manual, Frame Element Internal Forces",
    ),
)
_FORCE_LABELS = {"N": ForceUnit.N, "kN": ForceUnit.KN}
_MOMENT_LABELS = {
    "N-mm": MomentUnit.N_MM,
    "N-m": MomentUnit.N_M,
    "kN-mm": MomentUnit.KN_MM,
    "kN-m": MomentUnit.KN_M,
}
_STATION_LABELS = {"mm": LengthUnit.MM, "m": LengthUnit.M}
_DESIGN_USES = ("ultimate", "service", "sustained_service")
_MEMBER_KINDS = ("beam", "column")
_STATION_TOL_MM = 1e-6


@dataclass(frozen=True)
class EtabsActionBasis:
    """Caller-supplied identity from an independently retained model and run."""

    model_id: str
    model_sha256: str
    analysis_revision: str
    section_stiffness_connectivity_revision: str


@dataclass(frozen=True)
class EtabsTableUnits:
    force: ForceUnit
    moment: MomentUnit
    station: LengthUnit


@dataclass(frozen=True)
class EtabsForceTable:
    csv_bytes: bytes
    etabs_release: str
    capture_id: str
    basis: EtabsActionBasis


@dataclass(frozen=True)
class EtabsMemberBinding:
    """One unmeshed member in its source I→J orientation."""

    member_kind: Literal["beam", "column"]
    story: str
    label: str
    object_id: str
    analysis_element_id: str
    i_mm: Vector3
    j_mm: Vector3
    local_axes: LocalAxes
    required_stations_mm: tuple[float, ...]
    required_combination_ids: tuple[str, ...]


@dataclass(frozen=True)
class EtabsCombination:
    combination_id: str
    source_type: str
    design_use: Literal["ultimate", "service", "sustained_service"]


@dataclass(frozen=True)
class EtabsPairedForcesRequest:
    beam_table: EtabsForceTable
    column_table: EtabsForceTable
    current_basis: EtabsActionBasis
    configured_units: EtabsTableUnits
    members: tuple[EtabsMemberBinding, ...]
    combinations: tuple[EtabsCombination, ...]


class _TableError(ValueError):
    pass


@dataclass(frozen=True)
class _SourceRow:
    line: int
    cells: tuple[str, ...]
    common_cells: tuple[str, ...]
    step_type: str
    location: str


def _issue(code: str, message: str, location: str) -> Diagnostic:
    return Diagnostic(
        code, "error", message, _OPERATION, location, "etabs-paired-forces"
    )


def _basis_valid(basis: EtabsActionBasis) -> bool:
    return (
        bool(basis.model_id.strip())
        and len(basis.model_sha256) == 64
        and all(c in "0123456789abcdef" for c in basis.model_sha256)
        and bool(basis.analysis_revision.strip())
        and bool(basis.section_stiffness_connectivity_revision.strip())
    )


def _coordinates(point: Vector3) -> tuple[float, float, float]:
    return point.x, point.y, point.z


def _member_length(member: EtabsMemberBinding) -> float:
    displacement = tuple(
        end - start
        for start, end in zip(
            _coordinates(member.i_mm), _coordinates(member.j_mm), strict=True
        )
    )
    length = math.hypot(*displacement)
    if (
        not math.isfinite(length)
        or length <= 0
        or any(
            abs(actual / length - declared) > 1e-9
            for actual, declared in zip(
                displacement, _coordinates(member.local_axes.e1), strict=True
            )
        )
    ):
        raise _TableError(
            f"Local axis 1 must point from I to J for {member.object_id}."
        )
    return length


def _table_rows(
    table: EtabsForceTable, kind: Literal["beam", "column"], units: EtabsTableUnits
) -> Iterator[_SourceRow]:
    label = kind.capitalize()
    identity = (
        "Story",
        label,
        "Unique Name",
        "Output Case",
        "Case Type",
    )
    values = (
        "Station",
        "P",
        "V2",
        "V3",
        "T",
        "M2",
        "M3",
        "Element",
        "Elem Station",
    )
    columns = (
        (*identity, "Step Type", *values)
        if kind == "beam"
        else (*identity, *values, "Location")
    )
    if table.etabs_release != "22.7.0":
        raise _TableError("The paired profile requires ETABS release 22.7.0.")
    reader = csv.reader(io.StringIO(table.csv_bytes.decode("utf-8-sig")), strict=True)
    title = next(reader, [])
    if (
        not title
        or title[0].strip() != f"TABLE:  Element Forces - {label}s"
        or any(item.strip() for item in title[1:])
    ):
        raise _TableError(f"Expected the Element Forces - {label}s table title.")
    if tuple(next(reader, [])) != columns:
        raise _TableError(f"Unexpected Element Forces - {label}s column layout.")
    unit_row = next(reader, [])
    if len(unit_row) != len(columns):
        raise _TableError("The table must include its native column units row.")
    start = columns.index("Station")
    station_label, p, v2, v3, t, m2, m3, element, element_station = unit_row[
        start : start + 9
    ]
    station = _STATION_LABELS.get(station_label)
    force = _FORCE_LABELS.get(p)
    moment = _MOMENT_LABELS.get(t)
    if (
        station is None
        or force is None
        or moment is None
        or element_station != station_label
        or p != v2
        or p != v3
        or t != m2
        or t != m3
        or element
        or any(unit_row[:start])
        or any(unit_row[start + 9 :])
        or EtabsTableUnits(force, moment, station) != units
    ):
        raise _TableError("Native table units and configured units must agree.")
    for row in reader:
        cells = tuple(cell.strip() for cell in row)
        common = (*cells[:5], *cells[start : start + 9])
        if len(cells) != len(columns) or not all(common):
            raise _TableError(f"Incomplete force row at source line {reader.line_num}.")
        yield _SourceRow(
            reader.line_num,
            tuple(row),
            common,
            cells[5] if kind == "beam" else "",
            cells[14] if kind == "column" else "",
        )


def _bindings(
    request: EtabsPairedForcesRequest,
) -> tuple[
    dict[str, EtabsMemberBinding], dict[str, float], dict[str, EtabsCombination]
]:
    combinations = {item.combination_id: item for item in request.combinations}
    if len(combinations) != len(request.combinations) or any(
        not item.combination_id.strip()
        or not item.source_type.strip()
        or item.design_use not in _DESIGN_USES
        for item in request.combinations
    ):
        raise _TableError(
            "Combination definitions must have unique IDs and a declared use."
        )
    members = {member.object_id: member for member in request.members}
    if len(members) != len(request.members) or {
        member.member_kind for member in request.members
    } != set(_MEMBER_KINDS):
        raise _TableError(
            "The inventory requires distinct ETABS objects of both member kinds."
        )
    if len({(m.story, m.label) for m in request.members}) != len(members) or len(
        {m.local_axes.axis_id for m in request.members}
    ) != len(members):
        raise _TableError("Member identities and axis IDs must be unique.")
    lengths = {}
    for member in members.values():
        length = _member_length(member)
        stations = sorted(member.required_stations_mm)
        ids = member.required_combination_ids
        if (
            not all(
                (
                    member.story,
                    member.label,
                    member.object_id,
                    member.analysis_element_id,
                )
            )
            or not stations
            or not all(math.isfinite(x) and 0 <= x <= length for x in stations)
            or any(
                b - a <= 2 * _STATION_TOL_MM
                for a, b in zip(stations, stations[1:], strict=False)
            )
            or not ids
            or len(set(ids)) != len(ids)
            or not set(ids).issubset(combinations)
        ):
            raise _TableError(
                f"Invalid station or combination inventory for {member.object_id}."
            )
        lengths[member.object_id] = length
    return members, lengths, combinations


def _number(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise _TableError("Action and station cells must be finite numbers.")
    return number


def import_etabs_paired_forces(request: EtabsPairedForcesRequest) -> OperationResult:
    """Reconcile native six-component rows from one beam and column export.

    A complete result describes the declared member, station and combination
    inventory. The original ETABS sign convention and local axes are retained.
    A partial result exposes diagnostic rows and their exact source identities.
    Engineering status remains not evaluated for every intake outcome.
    """
    tables = (request.beam_table, request.column_table)
    hashes = tuple(hashlib.sha256(table.csv_bytes).hexdigest() for table in tables)
    identities = {
        "table_sha256": hashes,
        "table_bases": tuple(table.basis for table in tables),
        "captures": tuple(table.capture_id for table in tables),
        "etabs_releases": tuple(table.etabs_release for table in tables),
        "current_basis": request.current_basis,
    }
    try:
        inputs = effective_inputs(
            **identities,
            configured_units=request.configured_units,
            members=request.members,
            combinations=request.combinations,
        )
    except ValueError as exc:
        return rejected_result(
            _OPERATION,
            effective_inputs(**identities),
            (_issue("IMPORT.INVALID_BINDING", str(exc), "members"),),
            provenance=_PROVENANCE,
        )
    issues: list[Diagnostic] = []
    raw_rows: list[RawActionRow] = []
    source_rows: list[dict[str, object]] = []
    seen: set[tuple[str, str, float]] = set()
    declared_seen: set[tuple[str, str, float]] = set()
    units = request.configured_units
    source_id = semantic_hash("etabs_paired_source", identities)
    try:
        if not all(
            table.capture_id.strip() and _basis_valid(table.basis) for table in tables
        ) or not _basis_valid(request.current_basis):
            raise _TableError(
                "Each source and the current model require complete run identities."
            )
        members, lengths, combinations = _bindings(request)
        station_scale = 1000 if units.station == LengthUnit.M else 1
        kinds: tuple[Literal["beam", "column"], ...] = ("beam", "column")
        for table, kind, digest in zip(tables, kinds, hashes, strict=True):
            for source in _table_rows(table, kind, units):
                line, cells = source.line, source.common_cells
                story, label, object_id, case, case_type = cells[:5]
                member = members.get(object_id)
                if member is None or (
                    member.member_kind,
                    member.story,
                    member.label,
                    member.analysis_element_id,
                ) != (kind, story, label, cells[12]):
                    raise _TableError(
                        f"Source {kind} line {line} does not match its member binding."
                    )
                station, elem_station = _number(cells[5]), _number(cells[13])
                station_mm = station * station_scale
                if not (
                    0 <= station_mm <= lengths[object_id] + _STATION_TOL_MM
                    and elem_station >= 0
                    and abs(elem_station * station_scale - station_mm)
                    <= _STATION_TOL_MM
                    and not source.location
                ):
                    raise _TableError(
                        f"Unsupported station or station side at {kind} line {line}."
                    )
                key = (object_id, case, station_mm)
                if key in seen:
                    raise _TableError(f"Duplicate force row at {kind} line {line}.")
                seen.add(key)
                row_id = f"{kind}:{digest}:{line}"
                definition = combinations.get(case)
                source_type = definition.source_type if definition else None
                concurrency = ActionConcurrency.COMPONENT_ENVELOPE
                if (
                    case_type == "Combination"
                    and source_type == "Linear Add"
                    and not source.step_type
                ):
                    concurrency = ActionConcurrency.STATIC_CONCURRENT
                else:
                    issues.append(
                        _issue(
                            "IMPORT.COMBINATION_NOT_CONCURRENT",
                            "A verified Linear Add combination is required.",
                            row_id,
                        )
                    )
                expected = next(
                    (
                        x
                        for x in member.required_stations_mm
                        if abs(x - station_mm) <= _STATION_TOL_MM
                    ),
                    None,
                )
                if expected is None or case not in member.required_combination_ids:
                    issues.append(
                        _issue(
                            "IMPORT.ROW_OUTSIDE_INVENTORY",
                            "Station or combination is outside the declared member inventory.",
                            row_id,
                        )
                    )
                elif (object_id, case, expected) in declared_seen:
                    raise _TableError(
                        f"Duplicate declared station at {kind} line {line}."
                    )
                else:
                    declared_seen.add((object_id, case, expected))
                p, v2, v3, t, m2, m3 = map(_number, cells[6:12])
                if (kind == "beam" and (p or v3 or m2)) or (kind == "column" and p > 0):
                    issues.append(
                        _issue(
                            "IMPORT.ACTION_OUTSIDE_PROFILE",
                            "Beam axial/minor-axis actions and column uplift require a separate design profile.",
                            row_id,
                        )
                    )
                qualified_id = f"{story}/{label}"
                raw_rows.append(
                    RawActionRow(
                        row_id,
                        qualified_id,
                        qualified_id,
                        object_id,
                        cells[12],
                        member.local_axes.axis_id,
                        station,
                        elem_station,
                        case,
                        source.step_type or case_type,
                        None,
                        concurrency,
                        p,
                        v2,
                        v3,
                        t,
                        m2,
                        m3,
                    )
                )
                source_rows.append(
                    {
                        "source_row_id": row_id,
                        "source_line": line,
                        "table_sha256": digest,
                        "member_kind": kind,
                        "case_type": case_type,
                        "combination_source_type": source_type,
                        "combination_design_use": (
                            definition.design_use if definition else None
                        ),
                        "cells": source.cells,
                    }
                )
        required = {
            (member.object_id, case, station)
            for member in members.values()
            for case in member.required_combination_ids
            for station in member.required_stations_mm
        }
        for object_id, case, station in sorted(required - declared_seen):
            issues.append(
                _issue(
                    "IMPORT.REQUIRED_ROW_MISSING",
                    "The declared combination and station row is missing.",
                    f"{object_id}/{case}/{station:g} mm",
                )
            )
        stale = any(table.basis != request.current_basis for table in tables)
        different_capture = tables[0].capture_id != tables[1].capture_id
        if stale or different_capture:
            issues.append(
                _issue(
                    "IMPORT.STALE_OR_UNMATCHED_CAPTURE",
                    "Both tables must identify the same current model, analysis and capture.",
                    "table_bases",
                )
            )
        outputs: dict[str, object] = {
            "status": "HOLD" if issues else "COMPLETE_FOR_DECLARED_ROWS",
            "normalized_snapshot": None,
            "diagnostic_snapshot": None,
            "source_rows": source_rows,
            "configured_units": units,
            "table_sha256": hashes,
        }
        if raw_rows and not stale and not different_capture:
            normalized = normalize_action_snapshot(
                RawActionSnapshot(
                    source_id,
                    request.current_basis.model_id,
                    request.current_basis.analysis_revision,
                    tables[0].capture_id,
                    units.force,
                    units.moment,
                    units.station,
                    tuple(member.local_axes for member in members.values()),
                    tuple(raw_rows),
                )
            )
            if normalized.execution != ExecutionState.COMPLETED:
                message = normalized.diagnostics[0].message
                raise _TableError(message)
            snapshot_key = "diagnostic_snapshot" if issues else "normalized_snapshot"
            outputs[snapshot_key] = normalized.outputs
    except (ValueError, csv.Error) as exc:
        return rejected_result(
            _OPERATION,
            inputs,
            (_issue("IMPORT.INVALID_TABLE_OR_BINDING", str(exc), "tables"),),
            provenance=_PROVENANCE,
        )
    if issues:
        return partial_result(
            _OPERATION,
            inputs,
            outputs,
            issues,
            provenance=_PROVENANCE,
            freshness=(
                FreshnessState.STALE
                if stale or different_capture
                else FreshnessState.CURRENT
            ),
        )
    return completed_result(
        _OPERATION,
        inputs,
        outputs,
        engineering=EngineeringState.NOT_EVALUATED,
        provenance=_PROVENANCE,
    )
