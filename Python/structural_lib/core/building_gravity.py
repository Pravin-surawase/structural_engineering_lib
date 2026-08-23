# SPDX-License-Identifier: MIT
"""Versioned physical-model and load-basis contracts for gravity workflow V1.

These models describe the deliberately narrow, hand-checkable building selected
for Building Gravity Workflow V1.  They contain no IS 456 design mathematics and
do not turn render geometry into an analysis model.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from enum import StrEnum
from typing import Literal, Protocol

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_validator,
    model_validator,
)

__all__ = [
    "BuildingModelV1",
    "BuildingSourceRecordV1",
    "CoordinateSystemV1",
    "ExcludedGravityActionV1",
    "GravityActionCategoryV1",
    "GravityApprovedExclusionV1",
    "GravityCombinationFactorV1",
    "GravityCombinationV1",
    "GravityFootingDestinationV1",
    "GravityInclusionDispositionV1",
    "GravityInclusionRuleV1",
    "GravityLoadCaseV1",
    "GravityLoadStateV1",
    "GravityMaterialV1",
    "GravityMemberKindV1",
    "GravityMemberV1",
    "GravityNodeV1",
    "GravityPanelV1",
    "GravityPracticalActionKindV1",
    "GravityPracticalActionUnitsV1",
    "GravityPracticalActionV1",
    "GravitySectionKindV1",
    "GravitySectionV1",
    "GravitySourceReferenceV1",
    "GravitySupportIdealizationV1",
    "LoadModelV1",
    "SourceDispositionV1",
    "canonical_building_model_hash_v1",
    "canonical_load_model_hash_v1",
]

_ID_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9_.:-]*$"
_SHA256_PATTERN = r"^[0-9a-f]{64}$"


class _FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", allow_inf_nan=False)


class _HasId(Protocol):
    id: str


class CoordinateSystemV1(StrEnum):
    """Only coordinate system accepted by the bounded V1 topology."""

    RIGHT_HANDED_XY_HORIZONTAL_Z_UP = "RIGHT_HANDED_XY_HORIZONTAL_Z_UP"


class GravitySectionKindV1(StrEnum):
    SLAB = "SLAB"
    BEAM = "BEAM"
    COLUMN = "COLUMN"


class GravityMemberKindV1(StrEnum):
    BEAM = "BEAM"
    COLUMN = "COLUMN"


class GravitySupportIdealizationV1(StrEnum):
    BEAM_SIMPLY_SUPPORTED = "BEAM_SIMPLY_SUPPORTED"
    COLUMN_BRACED_AXIAL_ONLY = "COLUMN_BRACED_AXIAL_ONLY"


class SourceDispositionV1(StrEnum):
    ACCEPTED = "ACCEPTED"
    APPROVED_EXCLUSION = "APPROVED_EXCLUSION"


class GravityLoadCaseV1(StrEnum):
    DEAD = "DL"
    LIVE = "LL"


class GravityLoadStateV1(StrEnum):
    SERVICE = "SERVICE"
    FACTORED = "FACTORED"


class GravityActionCategoryV1(StrEnum):
    """Source categories plus the derived aggregate used after load transfer."""

    SLAB_SELF_WEIGHT = "SLAB_SELF_WEIGHT"
    SLAB_SUPERIMPOSED_DEAD = "SLAB_SUPERIMPOSED_DEAD"
    BEAM_SELF_WEIGHT = "BEAM_SELF_WEIGHT"
    COLUMN_SELF_WEIGHT = "COLUMN_SELF_WEIGHT"
    LIVE_OCCUPANCY = "LIVE_OCCUPANCY"
    PRACTICAL_WALL_LINE = "PRACTICAL_WALL_LINE"
    PRACTICAL_BEAM_LINE = "PRACTICAL_BEAM_LINE"
    PRACTICAL_BEAM_POINT = "PRACTICAL_BEAM_POINT"
    PRACTICAL_SLAB_AREA = "PRACTICAL_SLAB_AREA"
    COMBINED_DEAD = "COMBINED_DEAD"


class GravityInclusionDispositionV1(StrEnum):
    GENERATED = "GENERATED"
    SUPPLIED = "SUPPLIED"


class ExcludedGravityActionV1(StrEnum):
    WALL = "WALL"
    FACADE = "FACADE"
    EQUIPMENT = "EQUIPMENT"
    TANK = "TANK"
    STAIR = "STAIR"
    ROOF_SPECIAL = "ROOF_SPECIAL"
    LATERAL = "LATERAL"
    SOIL = "SOIL"
    FOOTING_SELF_WEIGHT = "FOOTING_SELF_WEIGHT"
    OVERBURDEN = "OVERBURDEN"
    LIVE_LOAD_REDUCTION = "LIVE_LOAD_REDUCTION"


class GravityPracticalActionKindV1(StrEnum):
    """Only caller-assigned practical gravity actions accepted by V1."""

    WALL_LINE = "WALL_LINE"
    BEAM_LINE = "BEAM_LINE"
    BEAM_POINT = "BEAM_POINT"
    SLAB_AREA = "SLAB_AREA"


class GravityPracticalActionUnitsV1(StrEnum):
    KILONEWTON_PER_METRE = "kN/m"
    KILONEWTON = "kN"
    KILONEWTON_PER_SQUARE_METRE = "kN/m2"


_SUPPORTED_PRACTICAL_SOURCE_CATEGORIES = frozenset(
    {
        ExcludedGravityActionV1.WALL,
        ExcludedGravityActionV1.FACADE,
        ExcludedGravityActionV1.EQUIPMENT,
        ExcludedGravityActionV1.TANK,
        ExcludedGravityActionV1.STAIR,
        ExcludedGravityActionV1.ROOF_SPECIAL,
    }
)


class GravityPracticalActionV1(_FrozenModel):
    """One explicit action assigned by the caller to a supported destination."""

    id: str = Field(min_length=1, max_length=128, pattern=_ID_PATTERN)
    kind: GravityPracticalActionKindV1
    source_category: ExcludedGravityActionV1
    case_id: GravityLoadCaseV1
    source_identity: str = Field(min_length=1, max_length=256, pattern=_ID_PATTERN)
    source_ref_id: str = Field(min_length=1, max_length=128, pattern=_ID_PATTERN)
    destination_id: str = Field(min_length=1, max_length=128, pattern=_ID_PATTERN)
    magnitude: float = Field(gt=0)
    units: GravityPracticalActionUnitsV1
    point_position_mm: float | None = Field(default=None, ge=0)
    assignment_basis: str = Field(min_length=1, max_length=512)
    assignment: Literal["CALLER_ASSIGNED_NO_DISTRIBUTION_INFERENCE"] = (
        "CALLER_ASSIGNED_NO_DISTRIBUTION_INFERENCE"
    )

    @model_validator(mode="after")
    def validate_action_shape(self) -> GravityPracticalActionV1:
        if self.source_category not in _SUPPORTED_PRACTICAL_SOURCE_CATEGORIES:
            raise ValueError(
                f"{self.source_category.value} is not a supported practical "
                "gravity-action source category"
            )
        expected_units = {
            GravityPracticalActionKindV1.WALL_LINE: (
                GravityPracticalActionUnitsV1.KILONEWTON_PER_METRE
            ),
            GravityPracticalActionKindV1.BEAM_LINE: (
                GravityPracticalActionUnitsV1.KILONEWTON_PER_METRE
            ),
            GravityPracticalActionKindV1.BEAM_POINT: (
                GravityPracticalActionUnitsV1.KILONEWTON
            ),
            GravityPracticalActionKindV1.SLAB_AREA: (
                GravityPracticalActionUnitsV1.KILONEWTON_PER_SQUARE_METRE
            ),
        }[self.kind]
        if self.units is not expected_units:
            raise ValueError(f"{self.kind.value} requires units={expected_units.value}")
        if self.kind is GravityPracticalActionKindV1.BEAM_POINT:
            if self.point_position_mm is None:
                raise ValueError("BEAM_POINT requires point_position_mm")
        elif self.point_position_mm is not None:
            raise ValueError(f"{self.kind.value} must not include point_position_mm")
        if self.kind is GravityPracticalActionKindV1.WALL_LINE:
            if self.source_category is not ExcludedGravityActionV1.WALL:
                raise ValueError("WALL_LINE requires source_category=WALL")
            if self.case_id is not GravityLoadCaseV1.DEAD:
                raise ValueError("WALL_LINE is accepted only in the DL case")
        elif self.source_category is ExcludedGravityActionV1.WALL:
            raise ValueError("WALL sources require kind=WALL_LINE")
        return self


class GravityNodeV1(_FrozenModel):
    id: str = Field(min_length=1, max_length=128, pattern=_ID_PATTERN)
    x_mm: float
    y_mm: float
    z_mm: float


class GravityMaterialV1(_FrozenModel):
    id: str = Field(min_length=1, max_length=128, pattern=_ID_PATTERN)
    material_kind: Literal["CONCRETE"] = "CONCRETE"
    unit_weight_kn_m3: float = Field(gt=0)
    fck_nmm2: float = Field(gt=0)


class GravitySectionV1(_FrozenModel):
    id: str = Field(min_length=1, max_length=128, pattern=_ID_PATTERN)
    kind: GravitySectionKindV1
    material_id: str = Field(min_length=1, max_length=128, pattern=_ID_PATTERN)
    width_mm: float | None = Field(default=None, gt=0)
    depth_mm: float | None = Field(default=None, gt=0)
    thickness_mm: float | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def validate_dimensions(self) -> GravitySectionV1:
        if self.kind is GravitySectionKindV1.SLAB:
            if (
                self.thickness_mm is None
                or self.width_mm is not None
                or self.depth_mm is not None
            ):
                raise ValueError(
                    "SLAB section requires only thickness_mm; width_mm/depth_mm are not accepted"
                )
        elif (
            self.width_mm is None
            or self.depth_mm is None
            or self.thickness_mm is not None
        ):
            raise ValueError(
                f"{self.kind.value} section requires width_mm and depth_mm only"
            )
        return self


class GravityPanelV1(_FrozenModel):
    id: str = Field(min_length=1, max_length=128, pattern=_ID_PATTERN)
    corner_node_ids: tuple[str, str, str, str]
    section_id: str = Field(min_length=1, max_length=128, pattern=_ID_PATTERN)
    span_direction: Literal["Y"] = "Y"
    supporting_beam_ids: tuple[str, str]
    load_path_id: str = Field(min_length=1, max_length=128, pattern=_ID_PATTERN)
    render_id: str = Field(min_length=1, max_length=128, pattern=_ID_PATTERN)

    @model_validator(mode="after")
    def validate_unique_references(self) -> GravityPanelV1:
        if len(set(self.corner_node_ids)) != 4:
            raise ValueError("panel corner_node_ids must contain four unique nodes")
        if len(set(self.supporting_beam_ids)) != 2:
            raise ValueError("panel supporting_beam_ids must contain two unique beams")
        return self


class GravityMemberV1(_FrozenModel):
    id: str = Field(min_length=1, max_length=128, pattern=_ID_PATTERN)
    kind: GravityMemberKindV1
    start_node_id: str = Field(min_length=1, max_length=128, pattern=_ID_PATTERN)
    end_node_id: str = Field(min_length=1, max_length=128, pattern=_ID_PATTERN)
    section_id: str = Field(min_length=1, max_length=128, pattern=_ID_PATTERN)
    support_idealization: GravitySupportIdealizationV1
    load_path_id: str = Field(min_length=1, max_length=128, pattern=_ID_PATTERN)
    render_id: str = Field(min_length=1, max_length=128, pattern=_ID_PATTERN)

    @model_validator(mode="after")
    def validate_member_contract(self) -> GravityMemberV1:
        if self.start_node_id == self.end_node_id:
            raise ValueError("member start_node_id and end_node_id must differ")
        expected = (
            GravitySupportIdealizationV1.BEAM_SIMPLY_SUPPORTED
            if self.kind is GravityMemberKindV1.BEAM
            else GravitySupportIdealizationV1.COLUMN_BRACED_AXIAL_ONLY
        )
        if self.support_idealization is not expected:
            raise ValueError(
                f"{self.kind.value} requires support_idealization={expected.value}"
            )
        return self


class GravityFootingDestinationV1(_FrozenModel):
    id: str = Field(min_length=1, max_length=128, pattern=_ID_PATTERN)
    column_id: str = Field(min_length=1, max_length=128, pattern=_ID_PATTERN)
    node_id: str = Field(min_length=1, max_length=128, pattern=_ID_PATTERN)
    action_idealization: Literal["CONCENTRIC_AXIAL_ONLY"] = "CONCENTRIC_AXIAL_ONLY"
    load_path_id: str = Field(min_length=1, max_length=128, pattern=_ID_PATTERN)


class BuildingSourceRecordV1(_FrozenModel):
    """Raw-source accounting; order is provenance, not canonical-model identity."""

    source_index: int = Field(ge=0)
    source_id: str = Field(min_length=1, max_length=256)
    disposition: SourceDispositionV1
    canonical_id: str | None = Field(default=None, min_length=1, max_length=128)
    reason: str | None = Field(default=None, min_length=1, max_length=512)

    @model_validator(mode="after")
    def validate_disposition(self) -> BuildingSourceRecordV1:
        if self.disposition is SourceDispositionV1.ACCEPTED:
            if self.canonical_id is None or self.reason is not None:
                raise ValueError(
                    "ACCEPTED source record requires canonical_id and no reason"
                )
        elif self.canonical_id is not None or self.reason is None:
            raise ValueError(
                "APPROVED_EXCLUSION source record requires reason and no canonical_id"
            )
        return self


class BuildingModelV1(_FrozenModel):
    """Exact physical-model contract for the selected one-storey V1 topology."""

    schema_version: Literal["building-model/v1"] = "building-model/v1"
    model_id: str = Field(min_length=1, max_length=128, pattern=_ID_PATTERN)
    project_id: str = Field(min_length=1, max_length=128, pattern=_ID_PATTERN)
    units: Literal["mm"] = "mm"
    coordinate_system: CoordinateSystemV1 = (
        CoordinateSystemV1.RIGHT_HANDED_XY_HORIZONTAL_Z_UP
    )
    raw_source_hash: str = Field(pattern=_SHA256_PATTERN)
    nodes: tuple[GravityNodeV1, ...]
    materials: tuple[GravityMaterialV1, ...]
    sections: tuple[GravitySectionV1, ...]
    panels: tuple[GravityPanelV1, ...]
    members: tuple[GravityMemberV1, ...]
    footing_destinations: tuple[GravityFootingDestinationV1, ...]
    source_records: tuple[BuildingSourceRecordV1, ...]

    @field_validator(
        "nodes",
        "materials",
        "sections",
        "panels",
        "members",
        "footing_destinations",
        mode="after",
    )
    @classmethod
    def sort_canonical_entities(cls, values: tuple[_HasId, ...]) -> tuple[_HasId, ...]:
        return tuple(sorted(values, key=lambda item: item.id))

    @field_validator("source_records", mode="after")
    @classmethod
    def sort_source_records(
        cls, values: tuple[BuildingSourceRecordV1, ...]
    ) -> tuple[BuildingSourceRecordV1, ...]:
        return tuple(sorted(values, key=lambda item: item.source_index))

    @model_validator(mode="after")
    def validate_exact_topology(self) -> BuildingModelV1:
        if len(self.nodes) != 8:
            raise ValueError("BuildingModelV1 requires exactly eight nodes")
        if len(self.materials) != 1:
            raise ValueError("BuildingModelV1 requires exactly one material")
        if len(self.sections) != 3:
            raise ValueError(
                "BuildingModelV1 requires one slab, one beam, and one column section"
            )
        if len(self.panels) != 1:
            raise ValueError("BuildingModelV1 requires exactly one slab panel")
        if len(self.members) != 6:
            raise ValueError(
                "BuildingModelV1 requires exactly two beams and four columns"
            )
        if len(self.footing_destinations) != 4:
            raise ValueError(
                "BuildingModelV1 requires exactly four footing destinations"
            )

        entity_groups = (
            self.nodes,
            self.materials,
            self.sections,
            self.panels,
            self.members,
            self.footing_destinations,
        )
        for group in entity_groups:
            ids = [item.id for item in group]
            if len(ids) != len(set(ids)):
                raise ValueError(
                    "duplicate IDs are not accepted within an entity group"
                )
        all_ids = [item.id for group in entity_groups for item in group]
        if len(all_ids) != len(set(all_ids)):
            raise ValueError("canonical IDs must be unique across the building model")

        nodes = {node.id: node for node in self.nodes}
        materials = {material.id: material for material in self.materials}
        sections = {section.id: section for section in self.sections}
        if {section.kind for section in self.sections} != set(GravitySectionKindV1):
            raise ValueError(
                "BuildingModelV1 requires one slab, one beam, and one column section"
            )
        if {section.material_id for section in self.sections} != set(materials):
            raise ValueError("every material and section must participate in the model")
        beams = tuple(
            member for member in self.members if member.kind is GravityMemberKindV1.BEAM
        )
        columns = tuple(
            member
            for member in self.members
            if member.kind is GravityMemberKindV1.COLUMN
        )
        if len(beams) != 2 or len(columns) != 4:
            raise ValueError(
                "BuildingModelV1 requires exactly two beams and four columns"
            )

        for section in self.sections:
            if section.material_id not in materials:
                raise ValueError(f"section {section.id} references unknown material")
        for member in self.members:
            if member.start_node_id not in nodes or member.end_node_id not in nodes:
                raise ValueError(f"member {member.id} references unknown node")
            member_section = sections.get(member.section_id)
            if member_section is None:
                raise ValueError(f"member {member.id} references unknown section")
            expected_kind = (
                GravitySectionKindV1.BEAM
                if member.kind is GravityMemberKindV1.BEAM
                else GravitySectionKindV1.COLUMN
            )
            if member_section.kind is not expected_kind:
                raise ValueError(
                    f"member {member.id} section kind does not match member kind"
                )

        panel = self.panels[0]
        if any(node_id not in nodes for node_id in panel.corner_node_ids):
            raise ValueError("panel references unknown corner node")
        panel_section = sections.get(panel.section_id)
        if panel_section is None or panel_section.kind is not GravitySectionKindV1.SLAB:
            raise ValueError("panel requires a known SLAB section")
        beam_ids = {beam.id for beam in beams}
        if set(panel.supporting_beam_ids) != beam_ids:
            raise ValueError("panel must be supported by exactly the two V1 beams")

        beam_endpoint_ids = {
            node_id
            for beam in beams
            for node_id in (beam.start_node_id, beam.end_node_id)
        }
        if (
            len(beam_endpoint_ids) != 4
            or set(panel.corner_node_ids) != beam_endpoint_ids
        ):
            raise ValueError(
                "beam endpoints and panel corners must be the same four top nodes"
            )
        top_nodes = tuple(nodes[node_id] for node_id in beam_endpoint_ids)
        top_z = {node.z_mm for node in top_nodes}
        x_values = {node.x_mm for node in top_nodes}
        y_values = {node.y_mm for node in top_nodes}
        expected_plan = set(itertools.product(x_values, y_values))
        actual_plan = {(node.x_mm, node.y_mm) for node in top_nodes}
        if (
            len(top_z) != 1
            or len(x_values) != 2
            or len(y_values) != 2
            or actual_plan != expected_plan
        ):
            raise ValueError(
                "panel top nodes must form one axis-aligned rectangle at one elevation"
            )

        beam_y_values: set[float] = set()
        x_min, x_max = min(x_values), max(x_values)
        for beam in beams:
            start, end = nodes[beam.start_node_id], nodes[beam.end_node_id]
            if start.z_mm != end.z_mm or start.y_mm != end.y_mm:
                raise ValueError(
                    "V1 beams must be horizontal and parallel to the X axis"
                )
            if {start.x_mm, end.x_mm} != {x_min, x_max}:
                raise ValueError("each V1 beam must span the full panel X dimension")
            beam_y_values.add(start.y_mm)
        if beam_y_values != y_values:
            raise ValueError("the two V1 beams must lie on opposite panel Y edges")

        column_top_ids: set[str] = set()
        column_base_ids: set[str] = set()
        column_by_id = {column.id: column for column in columns}
        for column in columns:
            start, end = nodes[column.start_node_id], nodes[column.end_node_id]
            if (
                start.x_mm != end.x_mm
                or start.y_mm != end.y_mm
                or start.z_mm >= end.z_mm
            ):
                raise ValueError("V1 columns must be vertical with start below end")
            column_base_ids.add(column.start_node_id)
            column_top_ids.add(column.end_node_id)
        if column_top_ids != beam_endpoint_ids or len(column_base_ids) != 4:
            raise ValueError("each beam end requires one unique vertical column")
        if len({nodes[node_id].z_mm for node_id in column_base_ids}) != 1:
            raise ValueError("the four V1 column bases must share one elevation")

        footing_column_ids = {
            footing.column_id for footing in self.footing_destinations
        }
        footing_node_ids = {footing.node_id for footing in self.footing_destinations}
        if (
            footing_column_ids != set(column_by_id)
            or footing_node_ids != column_base_ids
        ):
            raise ValueError(
                "each column requires one footing destination at its base node"
            )
        for footing in self.footing_destinations:
            if column_by_id[footing.column_id].start_node_id != footing.node_id:
                raise ValueError(
                    f"footing {footing.id} does not own its column base node"
                )

        coordinates = [(node.x_mm, node.y_mm, node.z_mm) for node in self.nodes]
        if len(coordinates) != len(set(coordinates)):
            raise ValueError("node coordinates must be unique")
        render_ids = [panel.render_id, *(member.render_id for member in self.members)]
        if len(render_ids) != len(set(render_ids)):
            raise ValueError("physical-to-render IDs must be unique")
        load_path_ids = [
            panel.load_path_id,
            *(member.load_path_id for member in self.members),
            *(footing.load_path_id for footing in self.footing_destinations),
        ]
        if len(load_path_ids) != len(set(load_path_ids)):
            raise ValueError("physical-to-load-path IDs must be unique")

        source_indices = [record.source_index for record in self.source_records]
        source_ids = [record.source_id for record in self.source_records]
        if len(source_indices) != len(set(source_indices)) or len(source_ids) != len(
            set(source_ids)
        ):
            raise ValueError("source ledger indices and source IDs must be unique")
        accepted_ids = {
            record.canonical_id
            for record in self.source_records
            if record.disposition is SourceDispositionV1.ACCEPTED
            and record.canonical_id is not None
        }
        accepted_records = [
            record
            for record in self.source_records
            if record.disposition is SourceDispositionV1.ACCEPTED
        ]
        if accepted_ids != set(all_ids) or len(accepted_records) != len(all_ids):
            missing = sorted(set(all_ids) - accepted_ids)
            extra = sorted(accepted_ids - set(all_ids))
            raise ValueError(
                f"source ledger must account for every canonical entity; missing={missing}, extra={extra}"
            )
        return self

    def canonical_payload(self) -> dict[str, object]:
        return self.model_dump(
            mode="json",
            exclude={"raw_source_hash", "source_records", "accepted_model_hash"},
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def accepted_model_hash(self) -> str:
        return canonical_building_model_hash_v1(self)


class GravitySourceReferenceV1(_FrozenModel):
    id: str = Field(min_length=1, max_length=128, pattern=_ID_PATTERN)
    title: str = Field(min_length=1, max_length=256)
    reference: str = Field(min_length=1, max_length=512)
    source_hash: str = Field(pattern=_SHA256_PATTERN)


class GravityInclusionRuleV1(_FrozenModel):
    category: GravityActionCategoryV1
    disposition: GravityInclusionDispositionV1
    owner: Literal["GRAVITY_LOAD_LEDGER"] = "GRAVITY_LOAD_LEDGER"
    source_ref_id: str = Field(min_length=1, max_length=128, pattern=_ID_PATTERN)


class GravityCombinationFactorV1(_FrozenModel):
    case_id: GravityLoadCaseV1
    factor: float = Field(gt=0)


class GravityCombinationV1(_FrozenModel):
    id: Literal["SERVICE_DL_LL", "ULS_1_5_DL_LL"]
    state: GravityLoadStateV1
    factors: tuple[GravityCombinationFactorV1, GravityCombinationFactorV1]
    source_ref_id: str = Field(min_length=1, max_length=128, pattern=_ID_PATTERN)

    @field_validator("factors", mode="after")
    @classmethod
    def sort_factors(
        cls, values: tuple[GravityCombinationFactorV1, GravityCombinationFactorV1]
    ) -> tuple[GravityCombinationFactorV1, GravityCombinationFactorV1]:
        return tuple(sorted(values, key=lambda item: item.case_id.value))  # type: ignore[return-value]

    @model_validator(mode="after")
    def validate_factors(self) -> GravityCombinationV1:
        factors = {item.case_id: item.factor for item in self.factors}
        if set(factors) != {GravityLoadCaseV1.DEAD, GravityLoadCaseV1.LIVE}:
            raise ValueError("combination must contain one DL factor and one LL factor")
        expected_state = (
            GravityLoadStateV1.SERVICE
            if self.id == "SERVICE_DL_LL"
            else GravityLoadStateV1.FACTORED
        )
        expected_factor = 1.0 if self.id == "SERVICE_DL_LL" else 1.5
        if self.state is not expected_state or any(
            factor != expected_factor for factor in factors.values()
        ):
            raise ValueError(
                f"{self.id} requires state={expected_state.value} and DL/LL factor={expected_factor}"
            )
        return self


class GravityApprovedExclusionV1(_FrozenModel):
    category: ExcludedGravityActionV1
    reason: str = Field(min_length=1, max_length=512)
    source_ref_id: str = Field(min_length=1, max_length=128, pattern=_ID_PATTERN)


_EXPECTED_INCLUSION: dict[GravityActionCategoryV1, GravityInclusionDispositionV1] = {
    GravityActionCategoryV1.SLAB_SELF_WEIGHT: GravityInclusionDispositionV1.GENERATED,
    GravityActionCategoryV1.SLAB_SUPERIMPOSED_DEAD: GravityInclusionDispositionV1.SUPPLIED,
    GravityActionCategoryV1.BEAM_SELF_WEIGHT: GravityInclusionDispositionV1.GENERATED,
    GravityActionCategoryV1.COLUMN_SELF_WEIGHT: GravityInclusionDispositionV1.GENERATED,
    GravityActionCategoryV1.LIVE_OCCUPANCY: GravityInclusionDispositionV1.SUPPLIED,
}


class LoadModelV1(_FrozenModel):
    """Frozen dead/live basis plus explicitly assigned practical actions."""

    schema_version: Literal["load-model/v1"] = "load-model/v1"
    model_hash: str = Field(pattern=_SHA256_PATTERN)
    raw_source_hash: str = Field(pattern=_SHA256_PATTERN)
    superimposed_dead_load_kn_m2: float = Field(ge=0)
    live_load_kn_m2: float = Field(ge=0)
    live_load_category: str = Field(min_length=1, max_length=128)
    balance_tolerance_kn: float = Field(default=1e-9, gt=0, le=1e-3)
    source_references: tuple[GravitySourceReferenceV1, ...]
    inclusion_rules: tuple[GravityInclusionRuleV1, ...]
    combinations: tuple[GravityCombinationV1, GravityCombinationV1]
    practical_actions: tuple[GravityPracticalActionV1, ...] = ()
    approved_exclusions: tuple[GravityApprovedExclusionV1, ...]

    @field_validator(
        "source_references",
        "inclusion_rules",
        "combinations",
        "practical_actions",
        "approved_exclusions",
        mode="after",
    )
    @classmethod
    def sort_contract_items(cls, values: tuple[object, ...]) -> tuple[object, ...]:
        key_name = "id" if values and hasattr(values[0], "id") else "category"
        return tuple(sorted(values, key=lambda item: str(getattr(item, key_name))))

    @model_validator(mode="after")
    def validate_frozen_basis(self) -> LoadModelV1:
        reference_ids = [reference.id for reference in self.source_references]
        if not reference_ids or len(reference_ids) != len(set(reference_ids)):
            raise ValueError("source reference IDs must be present and unique")
        reference_set = set(reference_ids)

        inclusion = {rule.category: rule for rule in self.inclusion_rules}
        if len(inclusion) != len(self.inclusion_rules) or set(inclusion) != set(
            _EXPECTED_INCLUSION
        ):
            raise ValueError(
                "inclusion_rules must cover exactly the five V1 dead/live categories"
            )
        for category, disposition in _EXPECTED_INCLUSION.items():
            rule = inclusion[category]
            if rule.disposition is not disposition:
                raise ValueError(
                    f"{category.value} must be {disposition.value} by GRAVITY_LOAD_LEDGER"
                )
            if rule.source_ref_id not in reference_set:
                raise ValueError(f"{category.value} references an unknown source")

        combinations = {
            combination.id: combination for combination in self.combinations
        }
        if set(combinations) != {"SERVICE_DL_LL", "ULS_1_5_DL_LL"}:
            raise ValueError(
                "LoadModelV1 requires exactly service DL+LL and 1.5(DL+LL)"
            )
        if any(
            combination.source_ref_id not in reference_set
            for combination in self.combinations
        ):
            raise ValueError("combination references an unknown source")

        action_ids = [action.id for action in self.practical_actions]
        source_identities = [
            action.source_identity for action in self.practical_actions
        ]
        if len(action_ids) != len(set(action_ids)):
            raise ValueError("practical action IDs must be unique")
        if len(source_identities) != len(set(source_identities)):
            raise ValueError("practical action source identities must be unique")
        if any(
            action.source_ref_id not in reference_set
            for action in self.practical_actions
        ):
            raise ValueError("practical action references an unknown source")

        exclusions = {item.category: item for item in self.approved_exclusions}
        included_categories = {
            action.source_category for action in self.practical_actions
        }
        expected_exclusions = set(ExcludedGravityActionV1) - included_categories
        if (
            len(exclusions) != len(self.approved_exclusions)
            or set(exclusions) != expected_exclusions
        ):
            raise ValueError(
                "approved_exclusions must list every action excluded from V1, "
                "including every unsupported or unsupplied category, and must "
                "omit explicitly supplied practical categories"
            )
        if any(
            item.source_ref_id not in reference_set for item in self.approved_exclusions
        ):
            raise ValueError("approved exclusion references an unknown source")
        return self

    def canonical_payload(self) -> dict[str, object]:
        return self.model_dump(
            mode="json",
            exclude={"raw_source_hash", "load_model_hash"},
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def load_model_hash(self) -> str:
        return canonical_load_model_hash_v1(self)


def _canonical_hash(payload: dict[str, object]) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def canonical_building_model_hash_v1(model: BuildingModelV1) -> str:
    """Hash normalized accepted geometry; raw-source ordering is provenance only."""

    return _canonical_hash(model.canonical_payload())


def canonical_load_model_hash_v1(model: LoadModelV1) -> str:
    """Hash the accepted dead/live basis independently of raw-source serialization."""

    return _canonical_hash(model.canonical_payload())
