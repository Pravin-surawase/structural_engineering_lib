# SPDX-License-Identifier: MIT
"""Read local, hash-bound manifests for the two maintained ETABS intake profiles."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Annotated, Any, Literal

from pydantic import Field

from structural_lib.beam.analysis import (
    ForceUnit,
    LengthUnit,
    LocalAxes,
    MomentUnit,
    Vector3,
)
from structural_lib.beam.semantics import plain
from structural_lib.core.models import DesignDefaults

from .contracts.beam_continuous import BeamSectionBarV1, Identifier, Reference
from .contracts.common import StrictPublicModel, model_validate_json_or_error
from .etabs_paired_forces import (
    EtabsActionBasis,
    EtabsCombination,
    EtabsForceTable,
    EtabsMemberBinding,
    EtabsPairedForcesRequest,
    EtabsTableUnits,
    import_etabs_paired_forces,
)
from .etabs_snapshot import (
    ETABSApprovedExclusionV1,
    ETABSBeamRequestBasisV1,
    ETABSExportUnitsV1,
    ETABSLocalAxisMappingV1,
    ETABSProjectExportIdentityV1,
    ETABSResultIdentityV1,
    ETABSSnapshotAmbiguityV1,
    ETABSSnapshotIssueV1,
    build_etabs_canonical_snapshot_v1,
)
from .import_ledger import ImportRowLedgerV1

Digest = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
Vector = Annotated[list[float], Field(min_length=3, max_length=3)]


class _RunBasis(StrictPublicModel):
    model_id: Identifier
    model_sha256: Digest
    analysis_revision: Identifier
    section_stiffness_connectivity_revision: Identifier

    def to_basis(self) -> EtabsActionBasis:
        return EtabsActionBasis(**self.model_dump())


class _CapturedFile(StrictPublicModel):
    file: Reference
    sha256: Digest
    capture_id: Identifier
    basis: _RunBasis
    worksheet: Identifier | None = None


class _Packet(StrictPublicModel):
    review_story: Identifier
    current_basis: _RunBasis


class _SnapshotDefaults(StrictPublicModel):
    # Every design-bearing project setting is declared, even when it matches
    # the compatibility importer's defaults.
    fck_mpa: float
    fy_mpa: float
    cover_mm: float
    min_bar_dia_mm: int
    max_bar_dia_mm: int
    stirrup_dia_mm: int


class _SnapshotPacket(_Packet):
    schema_version: Literal["floor-etabs-snapshot-packet/v1"]
    geometry: _CapturedFile
    forces: _CapturedFile
    model_definition: _CapturedFile
    project_export_identity: ETABSProjectExportIdentityV1
    units: ETABSExportUnitsV1
    local_axis_mapping: ETABSLocalAxisMappingV1
    result_identity: ETABSResultIdentityV1
    defaults: _SnapshotDefaults
    beam_request_basis: ETABSBeamRequestBasisV1
    approved_exclusions: list[ETABSApprovedExclusionV1]


class _Section(StrictPublicModel):
    """Caller-verified rectangular section and two-leg links at every declared station."""

    analysis_revision: Identifier
    reinforcement_revision: Identifier
    source_reference: Reference
    width_mm: float
    depth_mm: float
    fck_nmm2: float
    fy_nmm2: Literal[415, 500]
    clear_cover_mm: float
    aggregate_size_mm: float
    link_diameter_mm: float
    link_spacing_mm: float
    link_fy_nmm2: Literal[250, 415, 500]
    bars: list[BeamSectionBarV1]


class _PairedMember(StrictPublicModel):
    member_kind: Literal["beam", "column"]
    story: Identifier
    label: Identifier
    object_id: Identifier
    analysis_element_id: Identifier
    i_mm: Vector
    j_mm: Vector
    axis_id: Identifier
    e1: Vector
    e2: Vector
    e3: Vector
    required_stations_mm: list[float]
    required_combination_ids: list[Identifier]
    section: _Section | None = None

    def to_binding(self) -> EtabsMemberBinding:
        return EtabsMemberBinding(
            self.member_kind,
            self.story,
            self.label,
            self.object_id,
            self.analysis_element_id,
            Vector3(*self.i_mm),
            Vector3(*self.j_mm),
            LocalAxes(
                self.axis_id, Vector3(*self.e1), Vector3(*self.e2), Vector3(*self.e3)
            ),
            tuple(self.required_stations_mm),
            tuple(self.required_combination_ids),
        )


class _Combination(StrictPublicModel):
    combination_id: Identifier
    source_type: Identifier
    design_use: Literal["ultimate", "service", "sustained_service"]


class _PairedUnits(StrictPublicModel):
    force: Literal["N", "kN"]
    moment: Literal["N-mm", "N-m", "kN-mm", "kN-m"]
    station: Literal["mm", "m"]


class _PairedPacket(_Packet):
    schema_version: Literal["floor-etabs-paired-packet/v1"]
    etabs_release: Identifier
    beam_table: _CapturedFile
    column_table: _CapturedFile
    units: _PairedUnits
    members: list[_PairedMember]
    combinations: list[_Combination]


@dataclass
class EtabsFloorIntakeV1:
    """Local ETABS evidence shared by preview and evaluation."""

    status: str
    artifacts: list[dict[str, Any]]
    provenance: dict[str, Any]
    members: list[dict[str, Any]]
    issues: list[dict[str, str]]


def issue(code: str, path: str, message: str) -> dict[str, str]:
    return {"code": code, "path": path, "message": message}


def _source(
    folder: Path, role: str, source: _CapturedFile, expected_suffix: str
) -> tuple[dict[str, Any], bytes, dict[str, str] | None]:
    relative = Path(source.file)
    path = (folder / relative).resolve()
    if relative.is_absolute() or not path.is_relative_to(folder.resolve()):
        raise ValueError(f"{role}: use a path within the packet directory.")
    raw = path.read_bytes()
    digest = sha256(raw).hexdigest()
    evidence = {
        "role": role,
        "file": source.file,
        "sha256": digest,
        "byte_count": len(raw),
        "declared_sha256": source.sha256,
        "capture_id": source.capture_id,
        "action_basis": source.basis.model_dump(),
    }
    if source.worksheet is not None:
        evidence["worksheet"] = source.worksheet
    problem = None
    if digest != source.sha256:
        problem = issue(
            "FLOOR.ARTIFACT_HASH_MISMATCH",
            role,
            "File bytes differ from the captured SHA-256.",
        )
    suffix = path.suffix.casefold()
    if expected_suffix == ".csv" and suffix == ".xlsx" and source.worksheet:
        if problem:
            return evidence, b"", problem
        from .floor_etabs_excel import project_etabs_worksheet_v1

        # Bind the projection to the same bytes that were hashed above.
        try:
            with TemporaryDirectory() as directory:
                captured = Path(directory) / path.name
                captured.write_bytes(raw)
                projected = project_etabs_worksheet_v1(
                    captured, worksheet=source.worksheet
                )
        except ValueError as exc:
            return (
                evidence,
                b"",
                issue("FLOOR.WORKSHEET_PROJECTION_BLOCKED", role, str(exc)),
            )
        evidence["projection_sha256"] = sha256(projected).hexdigest()
        return evidence, projected, problem
    if suffix != expected_suffix or source.worksheet is not None:
        raise ValueError(
            f"{role}: expected {expected_suffix} or, for tables, .xlsx with an explicit worksheet."
        )
    return evidence, raw, problem


def _table_text(data: bytes) -> str:
    # Keep even a rejected table visible in the packet. The maintained import
    # owner supplies signed and normalized fields only after validation.
    return data.decode("utf-8-sig", errors="backslashreplace")


def _snapshot(
    folder: Path, packet: _SnapshotPacket, result: EtabsFloorIntakeV1
) -> None:
    specified = (
        ("geometry", packet.geometry, ".csv"),
        ("forces", packet.forces, ".csv"),
        ("model_definition", packet.model_definition, ".e2k"),
    )
    identity = packet.project_export_identity
    if (
        identity.source_edb_sha256 != packet.current_basis.model_sha256
        or identity.project_id != packet.current_basis.model_id
        or any(
            artifact.basis != packet.current_basis
            or artifact.capture_id != identity.export_id
            for _, artifact, _ in specified
        )
    ):
        result.issues.append(
            issue(
                "FLOOR.STALE_OR_MIXED_CAPTURE",
                "capture",
                "Geometry, actions and E2K must identify the same current export.",
            )
        )
    with TemporaryDirectory() as directory:
        paths = []
        for role, source, suffix in specified:
            evidence, raw, problem = _source(folder, role, source, suffix)
            result.artifacts.append(evidence)
            if suffix == ".csv":
                evidence["table_text"] = _table_text(raw)
            if problem:
                result.issues.append(problem)
            target = Path(directory) / role / Path(source.file).with_suffix(suffix).name
            target.parent.mkdir()
            target.write_bytes(raw)
            paths.append(target)
        if result.issues:
            return
        built = build_etabs_canonical_snapshot_v1(
            *paths,
            project_export_identity=identity,
            units=packet.units,
            local_axis_mapping=packet.local_axis_mapping,
            result_identity=packet.result_identity,
            defaults=DesignDefaults(**packet.defaults.model_dump()),
            beam_request_basis=packet.beam_request_basis,
            approved_exclusions=packet.approved_exclusions,
        )

    result.provenance["snapshot"] = built.model_dump(mode="json")
    findings: tuple[ETABSSnapshotIssueV1 | ETABSSnapshotAmbiguityV1, ...] = (
        *built.issues,
        *built.ambiguities,
    )
    result.issues.extend(issue(item.code, item.path, item.message) for item in findings)
    if built.snapshot is None:
        return
    imported = built.source_import
    assert imported is not None and imported.batch is not None
    identities = {
        member.source_member_id: member for member in built.snapshot.member_identities
    }
    rows_by_member: dict[
        tuple[str | float | None, str | float | None],
        list[tuple[ImportRowLedgerV1, dict[str | None, str | float | None]]],
    ] = {}
    for row in imported.ledger.rows:
        fields = {field.canonical_field: field.parsed_value for field in row.fields}
        key = (fields.get("story"), fields.get("label") or fields.get("beam_id"))
        rows_by_member.setdefault(key, []).append((row, fields))
    for geometry in imported.batch.beams:
        member = identities[geometry.id]
        scoped_rows = rows_by_member.get((geometry.story, geometry.label), [])
        source_rows = [row.model_dump(mode="json") for row, _ in scoped_rows]
        signed_actions = [
            {
                "source_row_number": row.source_row_number,
                "source_record_id": row.source_record_id,
                "combination": fields.get("case_id"),
                "station_m": fields.get("station"),
                "m3_knm": fields.get("m3"),
                "v2_kn": fields.get("v2"),
                "p_kn": fields.get("p"),
            }
            for row, fields in scoped_rows
            if row.artifact_role == "forces" and "station" in fields
        ]
        result.members.append(
            {
                "member_id": member.canonical_member_id,
                "story": geometry.story,
                "label": geometry.label,
                "member_kind": "beam",
                "geometry": geometry.model_dump(mode="json"),
                "source_identity": member.model_dump(mode="json"),
                "source_rows": source_rows,
                "signed_actions": signed_actions,
            }
        )
    result.status = "ACCEPTED"


def _paired(folder: Path, packet: _PairedPacket, result: EtabsFloorIntakeV1) -> None:
    tables = []
    for role, source in (
        ("beam_table", packet.beam_table),
        ("column_table", packet.column_table),
    ):
        evidence, raw, problem = _source(folder, role, source, ".csv")
        evidence["table_text"] = _table_text(raw)
        result.artifacts.append(evidence)
        if problem:
            result.issues.append(problem)
        tables.append(
            EtabsForceTable(
                raw, packet.etabs_release, source.capture_id, source.basis.to_basis()
            )
        )
    if result.issues:
        return

    members = tuple(item.to_binding() for item in packet.members)
    outcome = import_etabs_paired_forces(
        EtabsPairedForcesRequest(
            tables[0],
            tables[1],
            packet.current_basis.to_basis(),
            EtabsTableUnits(
                ForceUnit(packet.units.force.lower()),
                MomentUnit(packet.units.moment.lower().replace("-", "_")),
                LengthUnit(packet.units.station),
            ),
            members,
            tuple(
                EtabsCombination(**item.model_dump()) for item in packet.combinations
            ),
        )
    ).to_dict()
    result.provenance["paired_intake"] = outcome
    outputs = outcome.get("outputs") or {}
    status = outputs.get("status")
    result.status = (
        "ACCEPTED"
        if status == "COMPLETE_FOR_DECLARED_ROWS"
        else "HOLD"
        if status == "HOLD"
        else "BLOCKED"
    )
    result.issues.extend(
        issue(
            item["code"], item["field_or_location"] or "paired_tables", item["message"]
        )
        for item in outcome["diagnostics"]
    )
    snapshot = (
        outputs.get("normalized_snapshot") or outputs.get("diagnostic_snapshot") or {}
    )
    rows_by_object: dict[str, list[dict[str, Any]]] = {}
    uses = {item.combination_id: item.design_use for item in packet.combinations}
    for row in snapshot.get("rows", []):
        rows_by_object.setdefault(row["object_id"], []).append(
            {**row, "design_use": uses.get(row["load_case_id"])}
        )
    for declared, member in zip(packet.members, members, strict=True):
        binding = plain(member)
        result.members.append(
            {
                "member_id": f"{member.story}/{member.label}",
                "story": member.story,
                "label": member.label,
                "member_kind": member.member_kind,
                "geometry": {
                    "i_mm": binding["i_mm"],
                    "j_mm": binding["j_mm"],
                    "local_axes": binding["local_axes"],
                    "section": declared.section.model_dump(mode="json")
                    if declared.section
                    else None,
                },
                "source_identity": {
                    "object_id": member.object_id,
                    "analysis_element_id": member.analysis_element_id,
                    "required_stations_mm": list(member.required_stations_mm),
                    "required_combination_ids": list(member.required_combination_ids),
                },
                "signed_actions": rows_by_object.get(member.object_id, []),
            }
        )


def load_etabs_floor_v1(path: Path, *, profile: str) -> EtabsFloorIntakeV1:
    """Load a declared ETABS capture without access to ETABS or its EDB."""
    if path.suffix.casefold() != ".json":
        raise ValueError(
            "Supply the versioned export manifest (.json). Keep the EDB in licensed ETABS on Windows."
        )
    data = path.read_bytes()
    result = EtabsFloorIntakeV1(
        "BLOCKED",
        [
            {
                "role": "manifest",
                "file": path.name,
                "sha256": sha256(data).hexdigest(),
                "byte_count": len(data),
            }
        ],
        {},
        [],
        [],
    )
    packet: _SnapshotPacket | _PairedPacket
    if profile == "etabs-snapshot":
        packet = model_validate_json_or_error(_SnapshotPacket, data)
        _snapshot(path.parent, packet, result)
    elif profile == "etabs-paired":
        packet = model_validate_json_or_error(_PairedPacket, data)
        _paired(path.parent, packet, result)
    else:
        raise ValueError(f"Unknown ETABS profile {profile!r}.")
    result.provenance.update(
        review_story=packet.review_story,
        current_basis=packet.current_basis.model_dump(),
    )
    return result
