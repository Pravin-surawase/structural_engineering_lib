# SPDX-License-Identifier: MIT
"""Deterministic dead/live source, transfer, combination, and balance ledger.

The engine is intentionally limited to ``BuildingModelV1``.  It performs
closed-form vertical load transfer only; it is not a frame solver and it does
not invoke component design workflows.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from collections.abc import Mapping
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

from structural_lib.core.building_gravity import (
    BuildingModelV1,
    ExcludedGravityActionV1,
    GravityActionCategoryV1,
    GravityLoadCaseV1,
    GravityLoadStateV1,
    GravityMemberKindV1,
    GravityMemberV1,
    GravityNodeV1,
    GravityPracticalActionKindV1,
    GravityPracticalActionUnitsV1,
    GravityPracticalActionV1,
    GravitySectionKindV1,
    LoadModelV1,
)

__all__ = [
    "GravityBalanceBoundaryV1",
    "GravityBalanceV1",
    "GravityCombinationActionV1",
    "GravityCombinationContributionV1",
    "GravityLedgerEntryV1",
    "GravityLedgerStageV1",
    "GravityLoadLedgerError",
    "GravityLoadLedgerV1",
    "build_gravity_load_ledger_v1",
]


class GravityLoadLedgerError(ValueError):
    """The accepted model/load contracts cannot produce a V1 ledger."""


class GravityLedgerStageV1(StrEnum):
    SOURCE = "SOURCE"
    BEAM_LINE = "BEAM_LINE"
    BEAM_POINT = "BEAM_POINT"
    BEAM_REACTION = "BEAM_REACTION"
    COLUMN_ACTION = "COLUMN_ACTION"
    FOOTING_ACTION = "FOOTING_ACTION"


class GravityBalanceBoundaryV1(StrEnum):
    PRACTICAL_ACTION_ASSIGNMENT = "PRACTICAL_ACTION_ASSIGNMENT"
    SLAB_TO_BEAM = "SLAB_TO_BEAM"
    BEAM_TO_COLUMN = "BEAM_TO_COLUMN"
    COLUMN_ACCUMULATION = "COLUMN_ACCUMULATION"
    COLUMN_TO_FOOTING = "COLUMN_TO_FOOTING"
    STOREY_TO_FOUNDATION = "STOREY_TO_FOUNDATION"
    COMBINATION_TO_FOUNDATION = "COMBINATION_TO_FOUNDATION"


class _FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", allow_inf_nan=False)


class GravityLedgerEntryV1(_FrozenModel):
    entry_id: str = Field(min_length=1, max_length=256)
    case_id: GravityLoadCaseV1
    stage: GravityLedgerStageV1
    action_category: GravityActionCategoryV1
    source_id: str = Field(min_length=1, max_length=128)
    destination_id: str = Field(min_length=1, max_length=128)
    magnitude_kn: float = Field(ge=0)
    area_load_kn_m2: float | None = Field(default=None, ge=0)
    line_load_kn_m: float | None = Field(default=None, ge=0)
    point_load_kn: float | None = Field(default=None, ge=0)
    point_position_mm: float | None = Field(default=None, ge=0)
    origin_entry_ids: tuple[str, ...] = ()
    formula_basis: str = Field(min_length=1, max_length=512)
    practical_action_id: str | None = Field(default=None, min_length=1, max_length=128)
    practical_action_kind: GravityPracticalActionKindV1 | None = None
    practical_source_category: ExcludedGravityActionV1 | None = None
    practical_source_identity: str | None = Field(
        default=None, min_length=1, max_length=256
    )
    practical_source_ref_id: str | None = Field(
        default=None, min_length=1, max_length=128
    )
    practical_input_units: GravityPracticalActionUnitsV1 | None = None
    practical_assignment_basis: str | None = Field(
        default=None, min_length=1, max_length=512
    )
    sign_convention: Literal["DOWNWARD_AND_COMPRESSION_POSITIVE"] = (
        "DOWNWARD_AND_COMPRESSION_POSITIVE"
    )

    @model_validator(mode="after")
    def validate_practical_metadata(self) -> GravityLedgerEntryV1:
        practical_values = (
            self.practical_action_id,
            self.practical_action_kind,
            self.practical_source_category,
            self.practical_source_identity,
            self.practical_source_ref_id,
            self.practical_input_units,
            self.practical_assignment_basis,
        )
        if any(value is not None for value in practical_values) and any(
            value is None for value in practical_values
        ):
            raise ValueError("practical ledger metadata must be complete")
        if self.practical_action_kind is GravityPracticalActionKindV1.BEAM_POINT:
            if self.point_load_kn is None or self.point_position_mm is None:
                raise ValueError("BEAM_POINT ledger entry requires load and position")
        elif self.point_load_kn is not None or self.point_position_mm is not None:
            raise ValueError("only BEAM_POINT ledger entries may carry point fields")
        return self


class GravityBalanceV1(_FrozenModel):
    balance_id: str = Field(min_length=1, max_length=256)
    boundary: GravityBalanceBoundaryV1
    case_or_combination_id: str = Field(min_length=1, max_length=128)
    source_id: str = Field(min_length=1, max_length=128)
    destination_ids: tuple[str, ...]
    source_total_kn: float = Field(ge=0)
    destination_total_kn: float = Field(ge=0)
    residual_kn: float
    tolerance_kn: float = Field(gt=0)
    passed: bool


class GravityCombinationContributionV1(_FrozenModel):
    case_id: GravityLoadCaseV1
    factor: float = Field(gt=0)
    unfactored_kn: float = Field(ge=0)
    contributed_kn: float = Field(ge=0)


class GravityCombinationActionV1(_FrozenModel):
    action_id: str = Field(min_length=1, max_length=256)
    combination_id: Literal["SERVICE_DL_LL", "ULS_1_5_DL_LL"]
    state: GravityLoadStateV1
    destination_id: str = Field(min_length=1, max_length=128)
    total_kn: float = Field(ge=0)
    contributions: tuple[
        GravityCombinationContributionV1, GravityCombinationContributionV1
    ]
    sign_convention: Literal["COMPRESSION_POSITIVE"] = "COMPRESSION_POSITIVE"


class GravityLoadLedgerV1(_FrozenModel):
    schema_version: Literal["gravity-load-ledger/v1"] = "gravity-load-ledger/v1"
    formula_version: Literal["gravity-load-path/v1"] = "gravity-load-path/v1"
    model_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    load_model_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    entries: tuple[GravityLedgerEntryV1, ...]
    combination_actions: tuple[GravityCombinationActionV1, ...]
    balances: tuple[GravityBalanceV1, ...]
    source_entry_count: int = Field(ge=1)
    accepted_entry_count: int = Field(ge=1)
    blocked_entry_count: Literal[0] = 0
    approved_exclusion_count: int = Field(ge=1)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_balanced(self) -> bool:
        return all(balance.passed for balance in self.balances)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def ledger_hash(self) -> str:
        payload = self.model_dump(mode="json", exclude={"ledger_hash", "all_balanced"})
        encoded = json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


def _member_length_m(
    member: GravityMemberV1, nodes: Mapping[str, GravityNodeV1]
) -> float:
    start = nodes[member.start_node_id]
    end = nodes[member.end_node_id]
    dx = end.x_mm - start.x_mm
    dy = end.y_mm - start.y_mm
    dz = end.z_mm - start.z_mm
    return math.sqrt(dx * dx + dy * dy + dz * dz) / 1000.0


def _balance(
    *,
    balance_id: str,
    boundary: GravityBalanceBoundaryV1,
    case_or_combination_id: str,
    source_id: str,
    destination_ids: tuple[str, ...],
    source_total_kn: float,
    destination_total_kn: float,
    tolerance_kn: float,
) -> GravityBalanceV1:
    residual = source_total_kn - destination_total_kn
    return GravityBalanceV1(
        balance_id=balance_id,
        boundary=boundary,
        case_or_combination_id=case_or_combination_id,
        source_id=source_id,
        destination_ids=tuple(sorted(destination_ids)),
        source_total_kn=source_total_kn,
        destination_total_kn=destination_total_kn,
        residual_kn=residual,
        tolerance_kn=tolerance_kn,
        passed=abs(residual) <= tolerance_kn,
    )


def _practical_ledger_entry(
    *,
    action: GravityPracticalActionV1,
    entry_id: str,
    stage: GravityLedgerStageV1,
    action_category: GravityActionCategoryV1,
    destination_id: str,
    magnitude_kn: float,
    formula_basis: str,
    area_load_kn_m2: float | None = None,
    line_load_kn_m: float | None = None,
    point_load_kn: float | None = None,
    point_position_mm: float | None = None,
    origin_entry_ids: tuple[str, ...] = (),
) -> GravityLedgerEntryV1:
    return GravityLedgerEntryV1(
        entry_id=entry_id,
        case_id=action.case_id,
        stage=stage,
        action_category=action_category,
        source_id=action.id,
        destination_id=destination_id,
        magnitude_kn=magnitude_kn,
        area_load_kn_m2=area_load_kn_m2,
        line_load_kn_m=line_load_kn_m,
        point_load_kn=point_load_kn,
        point_position_mm=point_position_mm,
        origin_entry_ids=origin_entry_ids,
        formula_basis=formula_basis,
        practical_action_id=action.id,
        practical_action_kind=action.kind,
        practical_source_category=action.source_category,
        practical_source_identity=action.source_identity,
        practical_source_ref_id=action.source_ref_id,
        practical_input_units=action.units,
        practical_assignment_basis=action.assignment_basis,
    )


def build_gravity_load_ledger_v1(
    building: BuildingModelV1,
    loads: LoadModelV1,
) -> GravityLoadLedgerV1:
    """Build the exact V1 vertical load path with complete source accounting."""

    if loads.model_hash != building.accepted_model_hash:
        raise GravityLoadLedgerError(
            "LoadModelV1.model_hash does not match BuildingModelV1.accepted_model_hash"
        )

    nodes = {node.id: node for node in building.nodes}
    materials = {material.id: material for material in building.materials}
    sections = {section.id: section for section in building.sections}
    panel = building.panels[0]
    panel_section = sections[panel.section_id]
    if (
        panel_section.kind is not GravitySectionKindV1.SLAB
        or panel_section.thickness_mm is None
    ):
        raise GravityLoadLedgerError("V1 panel requires an explicit slab thickness")
    panel_material = materials[panel_section.material_id]

    beams = tuple(
        member for member in building.members if member.kind is GravityMemberKindV1.BEAM
    )
    columns = tuple(
        member
        for member in building.members
        if member.kind is GravityMemberKindV1.COLUMN
    )
    beam_by_id = {beam.id: beam for beam in beams}
    column_by_top_node = {column.end_node_id: column for column in columns}
    footing_by_column = {
        footing.column_id: footing for footing in building.footing_destinations
    }

    x_values = [nodes[node_id].x_mm for node_id in panel.corner_node_ids]
    y_values = [nodes[node_id].y_mm for node_id in panel.corner_node_ids]
    panel_length_m = (max(x_values) - min(x_values)) / 1000.0
    panel_span_m = (max(y_values) - min(y_values)) / 1000.0
    panel_area_m2 = panel_length_m * panel_span_m
    if panel_length_m <= 0 or panel_span_m <= 0:
        raise GravityLoadLedgerError("accepted panel dimensions must be positive")
    for practical_action in loads.practical_actions:
        if practical_action.kind is GravityPracticalActionKindV1.SLAB_AREA:
            if practical_action.destination_id != panel.id:
                raise GravityLoadLedgerError(
                    f"SLAB_AREA action {practical_action.id} requires "
                    f"destination {panel.id}"
                )
            continue
        beam = beam_by_id.get(practical_action.destination_id)
        if beam is None:
            raise GravityLoadLedgerError(
                f"{practical_action.kind.value} action {practical_action.id} "
                "requires a known beam destination"
            )
        if practical_action.kind is GravityPracticalActionKindV1.BEAM_POINT:
            span_mm = _member_length_m(beam, nodes) * 1000.0
            if (
                practical_action.point_position_mm is None
                or practical_action.point_position_mm > span_mm
            ):
                raise GravityLoadLedgerError(
                    f"BEAM_POINT action {practical_action.id} position must lie within "
                    f"destination span [0, {span_mm}] mm"
                )

    entries: list[GravityLedgerEntryV1] = []
    source_entries: dict[tuple[GravityLoadCaseV1, str], GravityLedgerEntryV1] = {}
    beam_line_entries: dict[
        tuple[GravityLoadCaseV1, str], list[GravityLedgerEntryV1]
    ] = defaultdict(list)
    beam_point_entries: dict[
        tuple[GravityLoadCaseV1, str], list[GravityLedgerEntryV1]
    ] = defaultdict(list)
    reaction_entries: dict[
        tuple[GravityLoadCaseV1, str], list[GravityLedgerEntryV1]
    ] = defaultdict(list)
    column_action_entries: dict[tuple[GravityLoadCaseV1, str], GravityLedgerEntryV1] = (
        {}
    )
    footing_action_entries: dict[
        tuple[GravityLoadCaseV1, str], GravityLedgerEntryV1
    ] = {}
    practical_balances: list[GravityBalanceV1] = []

    panel_area_loads = {
        GravityLoadCaseV1.DEAD: (
            (
                GravityActionCategoryV1.SLAB_SELF_WEIGHT,
                panel_section.thickness_mm / 1000.0 * panel_material.unit_weight_kn_m3,
                "slab thickness x concrete unit weight",
            ),
            (
                GravityActionCategoryV1.SLAB_SUPERIMPOSED_DEAD,
                loads.superimposed_dead_load_kn_m2,
                "explicit supplied superimposed dead area load",
            ),
        ),
        GravityLoadCaseV1.LIVE: (
            (
                GravityActionCategoryV1.LIVE_OCCUPANCY,
                loads.live_load_kn_m2,
                f"explicit unreduced live area load: {loads.live_load_category}",
            ),
        ),
    }

    for case_id, actions in panel_area_loads.items():
        for category, intensity, formula in actions:
            entry_id = f"source:{case_id.value}:{panel.id}:{category.value}"
            source = GravityLedgerEntryV1(
                entry_id=entry_id,
                case_id=case_id,
                stage=GravityLedgerStageV1.SOURCE,
                action_category=category,
                source_id=panel.id,
                destination_id=panel.id,
                magnitude_kn=intensity * panel_area_m2,
                area_load_kn_m2=intensity,
                formula_basis=formula,
            )
            entries.append(source)
            source_entries[(case_id, entry_id)] = source
            for beam_id in panel.supporting_beam_ids:
                beam = beam_by_id[beam_id]
                beam_length_m = _member_length_m(beam, nodes)
                transferred_total = source.magnitude_kn / 2.0
                line = GravityLedgerEntryV1(
                    entry_id=f"transfer:{case_id.value}:{source.entry_id}:{beam.id}",
                    case_id=case_id,
                    stage=GravityLedgerStageV1.BEAM_LINE,
                    action_category=category,
                    source_id=panel.id,
                    destination_id=beam.id,
                    magnitude_kn=transferred_total,
                    line_load_kn_m=transferred_total / beam_length_m,
                    origin_entry_ids=(source.entry_id,),
                    formula_basis="one-way slab action x half transverse span",
                )
                entries.append(line)
                beam_line_entries[(case_id, beam.id)].append(line)

    practical_category = {
        GravityPracticalActionKindV1.WALL_LINE: (
            GravityActionCategoryV1.PRACTICAL_WALL_LINE
        ),
        GravityPracticalActionKindV1.BEAM_LINE: (
            GravityActionCategoryV1.PRACTICAL_BEAM_LINE
        ),
        GravityPracticalActionKindV1.BEAM_POINT: (
            GravityActionCategoryV1.PRACTICAL_BEAM_POINT
        ),
        GravityPracticalActionKindV1.SLAB_AREA: (
            GravityActionCategoryV1.PRACTICAL_SLAB_AREA
        ),
    }
    for practical_action in loads.practical_actions:
        category = practical_category[practical_action.kind]
        source_entry_id = (
            f"source:{practical_action.case_id.value}:practical:{practical_action.id}"
        )
        destination_entries: list[GravityLedgerEntryV1] = []
        if practical_action.kind is GravityPracticalActionKindV1.SLAB_AREA:
            source = _practical_ledger_entry(
                action=practical_action,
                entry_id=source_entry_id,
                stage=GravityLedgerStageV1.SOURCE,
                action_category=category,
                destination_id=practical_action.destination_id,
                magnitude_kn=practical_action.magnitude * panel_area_m2,
                area_load_kn_m2=practical_action.magnitude,
                formula_basis=practical_action.assignment_basis,
            )
            for beam_id in panel.supporting_beam_ids:
                beam = beam_by_id[beam_id]
                transferred_total = source.magnitude_kn / 2.0
                applied = _practical_ledger_entry(
                    action=practical_action,
                    entry_id=(
                        f"transfer:{practical_action.case_id.value}:practical:"
                        f"{practical_action.id}:{beam.id}"
                    ),
                    stage=GravityLedgerStageV1.BEAM_LINE,
                    action_category=category,
                    destination_id=beam.id,
                    magnitude_kn=transferred_total,
                    line_load_kn_m=(transferred_total / _member_length_m(beam, nodes)),
                    origin_entry_ids=(source.entry_id,),
                    formula_basis=(
                        "caller-assigned supported slab-area action transferred "
                        "equally to the two declared supporting beams"
                    ),
                )
                destination_entries.append(applied)
                beam_line_entries[(practical_action.case_id, beam.id)].append(applied)
        else:
            beam = beam_by_id[practical_action.destination_id]
            beam_length_m = _member_length_m(beam, nodes)
            is_point = practical_action.kind is GravityPracticalActionKindV1.BEAM_POINT
            source = _practical_ledger_entry(
                action=practical_action,
                entry_id=source_entry_id,
                stage=GravityLedgerStageV1.SOURCE,
                action_category=category,
                destination_id=beam.id,
                magnitude_kn=(
                    practical_action.magnitude
                    if is_point
                    else practical_action.magnitude * beam_length_m
                ),
                line_load_kn_m=None if is_point else practical_action.magnitude,
                point_load_kn=practical_action.magnitude if is_point else None,
                point_position_mm=(
                    practical_action.point_position_mm if is_point else None
                ),
                formula_basis=practical_action.assignment_basis,
            )
            applied = _practical_ledger_entry(
                action=practical_action,
                entry_id=(
                    f"apply:{practical_action.case_id.value}:practical:"
                    f"{practical_action.id}"
                ),
                stage=(
                    GravityLedgerStageV1.BEAM_POINT
                    if is_point
                    else GravityLedgerStageV1.BEAM_LINE
                ),
                action_category=category,
                destination_id=beam.id,
                magnitude_kn=source.magnitude_kn,
                line_load_kn_m=None if is_point else practical_action.magnitude,
                point_load_kn=practical_action.magnitude if is_point else None,
                point_position_mm=(
                    practical_action.point_position_mm if is_point else None
                ),
                origin_entry_ids=(source.entry_id,),
                formula_basis=(
                    "caller-assigned action applied once to the explicit beam "
                    "destination without distribution inference"
                ),
            )
            destination_entries.append(applied)
            target = beam_point_entries if is_point else beam_line_entries
            target[(practical_action.case_id, beam.id)].append(applied)

        entries.append(source)
        entries.extend(destination_entries)
        source_entries[(practical_action.case_id, source.entry_id)] = source
        destination_total = math.fsum(item.magnitude_kn for item in destination_entries)
        practical_balances.append(
            _balance(
                balance_id=(
                    f"balance:{practical_action.case_id.value}:practical:"
                    f"{practical_action.id}"
                ),
                boundary=GravityBalanceBoundaryV1.PRACTICAL_ACTION_ASSIGNMENT,
                case_or_combination_id=practical_action.case_id.value,
                source_id=practical_action.id,
                destination_ids=tuple(
                    item.destination_id for item in destination_entries
                ),
                source_total_kn=source.magnitude_kn,
                destination_total_kn=destination_total,
                tolerance_kn=loads.balance_tolerance_kn,
            )
        )

    for beam in beams:
        section = sections[beam.section_id]
        if section.width_mm is None or section.depth_mm is None:
            raise GravityLoadLedgerError(f"beam {beam.id} lacks rectangular dimensions")
        material = materials[section.material_id]
        length_m = _member_length_m(beam, nodes)
        line_load = (
            section.width_mm
            / 1000.0
            * section.depth_mm
            / 1000.0
            * material.unit_weight_kn_m3
        )
        source_id = (
            f"source:DL:{beam.id}:{GravityActionCategoryV1.BEAM_SELF_WEIGHT.value}"
        )
        source = GravityLedgerEntryV1(
            entry_id=source_id,
            case_id=GravityLoadCaseV1.DEAD,
            stage=GravityLedgerStageV1.SOURCE,
            action_category=GravityActionCategoryV1.BEAM_SELF_WEIGHT,
            source_id=beam.id,
            destination_id=beam.id,
            magnitude_kn=line_load * length_m,
            line_load_kn_m=line_load,
            formula_basis="rectangular beam area x length x concrete unit weight",
        )
        applied_self_weight = GravityLedgerEntryV1(
            entry_id=f"apply:{source_id}",
            case_id=GravityLoadCaseV1.DEAD,
            stage=GravityLedgerStageV1.BEAM_LINE,
            action_category=GravityActionCategoryV1.BEAM_SELF_WEIGHT,
            source_id=beam.id,
            destination_id=beam.id,
            magnitude_kn=source.magnitude_kn,
            line_load_kn_m=line_load,
            origin_entry_ids=(source.entry_id,),
            formula_basis="beam self-weight applied once to owning beam",
        )
        entries.extend((source, applied_self_weight))
        source_entries[(GravityLoadCaseV1.DEAD, source.entry_id)] = source
        beam_line_entries[(GravityLoadCaseV1.DEAD, beam.id)].append(applied_self_weight)

    column_self_sources: dict[str, GravityLedgerEntryV1] = {}
    for column in columns:
        section = sections[column.section_id]
        if section.width_mm is None or section.depth_mm is None:
            raise GravityLoadLedgerError(
                f"column {column.id} lacks rectangular dimensions"
            )
        material = materials[section.material_id]
        height_m = _member_length_m(column, nodes)
        total = (
            section.width_mm
            / 1000.0
            * section.depth_mm
            / 1000.0
            * height_m
            * material.unit_weight_kn_m3
        )
        source = GravityLedgerEntryV1(
            entry_id=f"source:DL:{column.id}:{GravityActionCategoryV1.COLUMN_SELF_WEIGHT.value}",
            case_id=GravityLoadCaseV1.DEAD,
            stage=GravityLedgerStageV1.SOURCE,
            action_category=GravityActionCategoryV1.COLUMN_SELF_WEIGHT,
            source_id=column.id,
            destination_id=column.id,
            magnitude_kn=total,
            formula_basis="rectangular column area x storey height x concrete unit weight",
        )
        entries.append(source)
        source_entries[(GravityLoadCaseV1.DEAD, source.entry_id)] = source
        column_self_sources[column.id] = source

    for case_id in GravityLoadCaseV1:
        for beam in beams:
            line_loads = beam_line_entries[(case_id, beam.id)]
            point_loads = beam_point_entries[(case_id, beam.id)]
            applied_loads = [*line_loads, *point_loads]
            span_mm = _member_length_m(beam, nodes) * 1000.0
            line_reaction = math.fsum(item.magnitude_kn / 2.0 for item in line_loads)
            for end_index, end_node_id in enumerate(
                (beam.start_node_id, beam.end_node_id)
            ):
                column = column_by_top_node[end_node_id]
                point_reaction = math.fsum(
                    item.magnitude_kn
                    * (
                        (span_mm - (item.point_position_mm or 0.0)) / span_mm
                        if end_index == 0
                        else (item.point_position_mm or 0.0) / span_mm
                    )
                    for item in point_loads
                )
                reaction = GravityLedgerEntryV1(
                    entry_id=f"reaction:{case_id.value}:{beam.id}:{column.id}",
                    case_id=case_id,
                    stage=GravityLedgerStageV1.BEAM_REACTION,
                    action_category=(
                        GravityActionCategoryV1.COMBINED_DEAD
                        if case_id is GravityLoadCaseV1.DEAD
                        else GravityActionCategoryV1.LIVE_OCCUPANCY
                    ),
                    source_id=beam.id,
                    destination_id=column.id,
                    magnitude_kn=line_reaction + point_reaction,
                    origin_entry_ids=tuple(
                        sorted(item.entry_id for item in applied_loads)
                    ),
                    formula_basis=(
                        "simply supported full-span line reactions plus exact "
                        "caller-positioned point-load reaction"
                    ),
                )
                entries.append(reaction)
                reaction_entries[(case_id, column.id)].append(reaction)

        for column in columns:
            origins = list(reaction_entries[(case_id, column.id)])
            if case_id is GravityLoadCaseV1.DEAD:
                origins.append(column_self_sources[column.id])
            total = math.fsum(item.magnitude_kn for item in origins)
            category = (
                GravityActionCategoryV1.COMBINED_DEAD
                if case_id is GravityLoadCaseV1.DEAD
                else GravityActionCategoryV1.LIVE_OCCUPANCY
            )
            column_action = GravityLedgerEntryV1(
                entry_id=f"column:{case_id.value}:{column.id}",
                case_id=case_id,
                stage=GravityLedgerStageV1.COLUMN_ACTION,
                action_category=category,
                source_id=column.id,
                destination_id=column.id,
                magnitude_kn=total,
                origin_entry_ids=tuple(sorted(item.entry_id for item in origins)),
                formula_basis="beam-end reactions plus owning column self-weight",
            )
            footing = footing_by_column[column.id]
            footing_action = GravityLedgerEntryV1(
                entry_id=f"footing:{case_id.value}:{footing.id}",
                case_id=case_id,
                stage=GravityLedgerStageV1.FOOTING_ACTION,
                action_category=category,
                source_id=column.id,
                destination_id=footing.id,
                magnitude_kn=total,
                origin_entry_ids=(column_action.entry_id,),
                formula_basis="concentric axial column action handoff; footing weight excluded",
            )
            entries.extend((column_action, footing_action))
            column_action_entries[(case_id, column.id)] = column_action
            footing_action_entries[(case_id, footing.id)] = footing_action

    balances: list[GravityBalanceV1] = list(practical_balances)
    for case_id in GravityLoadCaseV1:
        panel_sources = [
            item
            for (entry_case, _), item in source_entries.items()
            if entry_case is case_id
            and item.destination_id == panel.id
            and item.area_load_kn_m2 is not None
        ]
        panel_source_ids = {item.entry_id for item in panel_sources}
        slab_transfers = [
            item
            for (entry_case, _), items in beam_line_entries.items()
            if entry_case is case_id
            for item in items
            if set(item.origin_entry_ids) & panel_source_ids
        ]
        balances.append(
            _balance(
                balance_id=f"balance:{case_id.value}:slab-to-beam",
                boundary=GravityBalanceBoundaryV1.SLAB_TO_BEAM,
                case_or_combination_id=case_id.value,
                source_id=panel.id,
                destination_ids=tuple(panel.supporting_beam_ids),
                source_total_kn=math.fsum(item.magnitude_kn for item in panel_sources),
                destination_total_kn=math.fsum(
                    item.magnitude_kn for item in slab_transfers
                ),
                tolerance_kn=loads.balance_tolerance_kn,
            )
        )
        for beam in beams:
            applied_loads = [
                *beam_line_entries[(case_id, beam.id)],
                *beam_point_entries[(case_id, beam.id)],
            ]
            reactions = [
                item
                for column in columns
                for item in reaction_entries[(case_id, column.id)]
                if item.source_id == beam.id
            ]
            balances.append(
                _balance(
                    balance_id=f"balance:{case_id.value}:beam:{beam.id}",
                    boundary=GravityBalanceBoundaryV1.BEAM_TO_COLUMN,
                    case_or_combination_id=case_id.value,
                    source_id=beam.id,
                    destination_ids=tuple(item.destination_id for item in reactions),
                    source_total_kn=math.fsum(
                        item.magnitude_kn for item in applied_loads
                    ),
                    destination_total_kn=math.fsum(
                        item.magnitude_kn for item in reactions
                    ),
                    tolerance_kn=loads.balance_tolerance_kn,
                )
            )
        for column in columns:
            origins = reaction_entries[(case_id, column.id)]
            origin_total = math.fsum(item.magnitude_kn for item in origins)
            if case_id is GravityLoadCaseV1.DEAD:
                origin_total += column_self_sources[column.id].magnitude_kn
            column_action = column_action_entries[(case_id, column.id)]
            footing = footing_by_column[column.id]
            footing_action = footing_action_entries[(case_id, footing.id)]
            balances.extend(
                (
                    _balance(
                        balance_id=f"balance:{case_id.value}:column:{column.id}",
                        boundary=GravityBalanceBoundaryV1.COLUMN_ACCUMULATION,
                        case_or_combination_id=case_id.value,
                        source_id=column.id,
                        destination_ids=(column.id,),
                        source_total_kn=origin_total,
                        destination_total_kn=column_action.magnitude_kn,
                        tolerance_kn=loads.balance_tolerance_kn,
                    ),
                    _balance(
                        balance_id=f"balance:{case_id.value}:footing:{footing.id}",
                        boundary=GravityBalanceBoundaryV1.COLUMN_TO_FOOTING,
                        case_or_combination_id=case_id.value,
                        source_id=column.id,
                        destination_ids=(footing.id,),
                        source_total_kn=column_action.magnitude_kn,
                        destination_total_kn=footing_action.magnitude_kn,
                        tolerance_kn=loads.balance_tolerance_kn,
                    ),
                )
            )
        all_case_sources = [
            item
            for (entry_case, _), item in source_entries.items()
            if entry_case is case_id
        ]
        all_case_footings = [
            footing_action_entries[(case_id, footing.id)]
            for footing in building.footing_destinations
        ]
        balances.append(
            _balance(
                balance_id=f"balance:{case_id.value}:storey",
                boundary=GravityBalanceBoundaryV1.STOREY_TO_FOUNDATION,
                case_or_combination_id=case_id.value,
                source_id=building.model_id,
                destination_ids=tuple(
                    footing.id for footing in building.footing_destinations
                ),
                source_total_kn=math.fsum(
                    item.magnitude_kn for item in all_case_sources
                ),
                destination_total_kn=math.fsum(
                    item.magnitude_kn for item in all_case_footings
                ),
                tolerance_kn=loads.balance_tolerance_kn,
            )
        )

    combination_actions: list[GravityCombinationActionV1] = []
    for combination in loads.combinations:
        factor_map = {factor.case_id: factor.factor for factor in combination.factors}
        for footing in building.footing_destinations:
            contributions = tuple(
                GravityCombinationContributionV1(
                    case_id=case_id,
                    factor=factor_map[case_id],
                    unfactored_kn=footing_action_entries[
                        (case_id, footing.id)
                    ].magnitude_kn,
                    contributed_kn=(
                        footing_action_entries[(case_id, footing.id)].magnitude_kn
                        * factor_map[case_id]
                    ),
                )
                for case_id in GravityLoadCaseV1
            )
            action = GravityCombinationActionV1(
                action_id=f"combination:{combination.id}:{footing.id}",
                combination_id=combination.id,
                state=combination.state,
                destination_id=footing.id,
                total_kn=math.fsum(item.contributed_kn for item in contributions),
                contributions=contributions,  # type: ignore[arg-type]
            )
            combination_actions.append(action)
        source_total = math.fsum(
            math.fsum(
                item.magnitude_kn
                for (entry_case, _), item in source_entries.items()
                if entry_case is case_id
            )
            * factor_map[case_id]
            for case_id in GravityLoadCaseV1
        )
        destination_total = math.fsum(
            action.total_kn
            for action in combination_actions
            if action.combination_id == combination.id
        )
        balances.append(
            _balance(
                balance_id=f"balance:{combination.id}:foundation",
                boundary=GravityBalanceBoundaryV1.COMBINATION_TO_FOUNDATION,
                case_or_combination_id=combination.id,
                source_id=building.model_id,
                destination_ids=tuple(
                    footing.id for footing in building.footing_destinations
                ),
                source_total_kn=source_total,
                destination_total_kn=destination_total,
                tolerance_kn=loads.balance_tolerance_kn,
            )
        )

    ledger = GravityLoadLedgerV1(
        model_hash=building.accepted_model_hash,
        load_model_hash=loads.load_model_hash,
        entries=tuple(sorted(entries, key=lambda item: item.entry_id)),
        combination_actions=tuple(
            sorted(combination_actions, key=lambda item: item.action_id)
        ),
        balances=tuple(sorted(balances, key=lambda item: item.balance_id)),
        source_entry_count=len(source_entries),
        accepted_entry_count=len(entries),
        approved_exclusion_count=len(loads.approved_exclusions),
    )
    if not ledger.all_balanced:
        failed = [
            balance.balance_id for balance in ledger.balances if not balance.passed
        ]
        raise GravityLoadLedgerError(
            f"gravity load path failed reconciliation: {failed}"
        )
    return ledger
