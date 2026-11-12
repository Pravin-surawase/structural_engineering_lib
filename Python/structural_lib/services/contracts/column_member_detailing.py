"""Inputs for the COL07 ordinary tied rectangular member workflow."""

from __future__ import annotations

from typing import Annotated, Literal, Self

from pydantic import Field, field_validator, model_validator

from structural_lib.services.canonical_family import FamilyIdentityV1
from structural_lib.services.contracts.column_member import (
    FourCornerColumnGeometryV1,
    RectangularColumnActionsV1,
    RectangularColumnCageV1,
)
from structural_lib.services.contracts.common import (
    StrictPublicModel,
    complete_field_contracts_from_schema,
)
from structural_lib.services.contracts.family_f1 import ColumnMaterialsV1

_Id = Annotated[str, Field(min_length=1, max_length=80, pattern=r"\S")]
_Reference = Annotated[str, Field(min_length=1, max_length=240, pattern=r"\S")]
_Station = Annotated[float, Field(ge=0, le=50000)]


class ColumnDetailingBasisV1(StrictPublicModel):
    """Declared action and detailing revisions and project evidence."""

    analysis_revision: _Id
    current_analysis_revision: _Id
    detailing_revision: _Id
    nonseismic_reference: _Reference | None
    action_source_reference: _Reference | None
    end_development_reference: _Reference | None
    placement_reference: _Reference | None


class ColumnStraightEndDetailV1(StrictPublicModel):
    """Straight deformed-bar projections and end tie placement limits."""

    start_straight_mm: float = Field(ge=0, le=5000)
    end_straight_mm: float = Field(ge=0, le=5000)
    end_hoop_offset_mm: float = Field(gt=0, le=300)
    max_end_hoop_offset_mm: float = Field(gt=0, le=300)
    end_face_clearance_mm: float = Field(gt=0, le=300)


class ColumnTieZoneV1(StrictPublicModel):
    """A uniform hoop grid, including both endpoint hoop levels."""

    zone_id: _Id
    start_mm: _Station
    end_mm: _Station
    pitch_mm: float = Field(ge=6, le=500)

    @model_validator(mode="after")
    def increasing_limits(self) -> Self:
        if self.end_mm <= self.start_mm:
            raise ValueError("Tie zone end must be after its start")
        return self


class ColumnDetailingActionV1(RectangularColumnActionsV1):
    """Concurrent ULS section actions, in the same local axes as the cage."""

    combination_id: _Id
    vx_kn: float = Field(ge=-1e9, le=1e9)
    vy_kn: float = Field(ge=-1e9, le=1e9)


class ColumnLapZoneV1(StrictPublicModel):
    """A caller-approved low-stress splice window and tie limit."""

    start_mm: _Station
    end_mm: _Station
    max_tie_pitch_mm: float = Field(ge=6, le=300)
    reference: _Reference

    @model_validator(mode="after")
    def increasing_limits(self) -> Self:
        if self.end_mm <= self.start_mm:
            raise ValueError("Approved lap zone end must be after its start")
        return self


class ColumnContactAssemblyV1(StrictPublicModel):
    """Straight contact partners and the fabricated double-return link."""

    partner_y_mm: float = Field(gt=0, le=2000)
    lap_link_id: _Id
    hook_tail_mm: float = Field(gt=0, le=500)
    fabrication_reference: _Reference
    compression_reference: _Reference | None


class ColumnCompressionLapV1(StrictPublicModel):
    """A proposed straight equal-diameter compression lap group."""

    lap_id: _Id
    bar_ids: tuple[_Id, ...] = Field(min_length=1, max_length=8)
    start_mm: _Station
    end_mm: _Station
    stress_basis: Literal["compression", "unverified"]
    contact_assembly: ColumnContactAssemblyV1 | None = None

    @field_validator("bar_ids", mode="before")
    @classmethod
    def accept_json_array(cls, value: object) -> object:
        return tuple(value) if isinstance(value, list) else value

    @model_validator(mode="after")
    def increasing_limits(self) -> Self:
        if self.end_mm <= self.start_mm or len(set(self.bar_ids)) != len(self.bar_ids):
            raise ValueError("Each lap needs increasing limits and distinct bar IDs")
        return self


class ColumnTransverseCutScheduleV1(StrictPublicModel):
    """Approved fabrication cut lengths for the checked transverse bar marks."""

    detailing_revision: _Id
    reference: _Reference
    cut_lengths_mm: dict[_Id, Annotated[float, Field(gt=0, le=12000)]] = Field(
        min_length=1, max_length=3
    )


class ColumnMemberDetailingInputV1(StrictPublicModel):
    """Physical column, complete tie grid, supplied actions and fabrication basis."""

    schema_version: Literal["column-member-detailing-input/v1"] = (
        "column-member-detailing-input/v1"
    )
    identity: FamilyIdentityV1
    geometry: FourCornerColumnGeometryV1
    materials: ColumnMaterialsV1
    reinforcement: RectangularColumnCageV1
    basis: ColumnDetailingBasisV1
    end_detail: ColumnStraightEndDetailV1
    tie_fy_nmm2: float = Field(ge=250, le=600)
    tie_zones: tuple[ColumnTieZoneV1, ...] = Field(min_length=1, max_length=12)
    actions: tuple[ColumnDetailingActionV1, ...] = Field(min_length=1, max_length=48)
    approved_lap_zone: ColumnLapZoneV1 | None = None
    laps: tuple[ColumnCompressionLapV1, ...] = Field(default=(), max_length=8)
    transverse_cut_schedule: ColumnTransverseCutScheduleV1 | None = None

    @field_validator("tie_zones", "actions", "laps", mode="before")
    @classmethod
    def accept_json_arrays(cls, value: object) -> object:
        return tuple(value) if isinstance(value, list) else value

    @model_validator(mode="after")
    def check_member_domain(self) -> Self:
        length = self.geometry.unsupported_length_mm
        if any(row.check_station_mm > length for row in self.actions):
            raise ValueError("Action stations must lie between the member faces")
        if any(zone.end_mm > length for zone in self.tie_zones):
            raise ValueError("Tie zones must lie between the member faces")
        if any(lap.end_mm > length for lap in self.laps) or (
            self.approved_lap_zone is not None
            and self.approved_lap_zone.end_mm > length
        ):
            raise ValueError(
                "Lap groups and the approved window must lie within the member"
            )
        stations = {(row.combination_id, row.check_station_mm) for row in self.actions}
        if len(stations) != len(self.actions):
            raise ValueError("Each combination and station pair must be unique")
        if len({zone.zone_id for zone in self.tie_zones}) != len(self.tie_zones):
            raise ValueError("Tie zone IDs must be unique")
        if len({lap.lap_id for lap in self.laps}) != len(self.laps):
            raise ValueError("Lap IDs must be unique")
        return self


ColumnMemberDetailingInputV1.field_contracts = complete_field_contracts_from_schema(
    ColumnMemberDetailingInputV1
)
