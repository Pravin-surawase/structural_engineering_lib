"""Versioned physical four-corner column request."""

from __future__ import annotations

from itertools import combinations
from math import hypot
from typing import Literal, Self

from pydantic import Field, StrictBool, field_validator, model_validator

from structural_lib.services.canonical_family import FamilyIdentityV1
from structural_lib.services.contracts.common import (
    StrictPublicModel,
    complete_field_contracts_from_schema,
)
from structural_lib.services.contracts.family_f1 import ColumnMaterialsV1


class FourCornerColumnGeometryV1(StrictPublicModel):
    """Solid rectangle and explicit ordinary braced end restraint."""

    b_mm: float = Field(gt=0, le=2000)
    D_mm: float = Field(gt=0, le=2000)
    unsupported_length_mm: float = Field(ge=100, le=50000)
    end_condition: Literal["FIXED_FIXED", "FIXED_HINGED", "HINGED_HINGED"]
    braced: Literal[True]


class FourCornerColumnActionsV1(StrictPublicModel):
    """Compression and moment magnitude for one principal-axis member check."""

    pu_kn: float = Field(gt=0, le=1e9)
    moment_knm: float = Field(ge=0, le=1e9)
    bending_axis: Literal["x", "y"]


class ColumnClosedTieV1(StrictPublicModel):
    """One actual ordinary rectangular tie family at the checked section."""

    tie_id: str = Field(min_length=1, max_length=80)
    diameter_mm: float = Field(gt=0, le=80)
    spacing_mm: float = Field(gt=0, le=50000)
    internal_bend_radius_mm: float = Field(ge=0, le=2000)
    closed: StrictBool
    hook_angle_deg: float = Field(gt=0, le=180)
    hook_tail_mm: float = Field(ge=0, le=2000)


class FourCornerColumnReinforcementV1(StrictPublicModel):
    """Four equal bars with cover to the tie and an explicit corner inset."""

    longitudinal_bar_diameter_mm: float = Field(gt=0, le=80)
    nominal_cover_mm: float = Field(gt=0, le=2000)
    corner_inset_mm: float = Field(ge=0, le=2000)
    aggregate_size_mm: float = Field(gt=0, le=100)
    project_required_cover_mm: float = Field(ge=0, le=2000)
    project_required_bend_radius_mm: float = Field(ge=0, le=2000)
    detailing_basis_reference: str = Field(min_length=1, max_length=240)
    tie: ColumnClosedTieV1 | None


class FourCornerColumnInputV1(StrictPublicModel):
    """One short braced principal-axis check with a physically resolved cage."""

    schema_version: Literal["column-four-corner-member-input/v1"] = (
        "column-four-corner-member-input/v1"
    )
    identity: FamilyIdentityV1
    geometry: FourCornerColumnGeometryV1
    actions: FourCornerColumnActionsV1
    materials: ColumnMaterialsV1
    reinforcement: FourCornerColumnReinforcementV1


FourCornerColumnInputV1.field_contracts = complete_field_contracts_from_schema(
    FourCornerColumnInputV1
)


class RectangularColumnActionsV1(StrictPublicModel):
    """One simultaneous factored compression and signed moment pair."""

    pu_kn: float = Field(gt=0, le=1e9)
    mx_knm: float = Field(ge=-1e9, le=1e9)
    my_knm: float = Field(ge=-1e9, le=1e9)
    check_station_mm: float = Field(ge=0)


class ColumnMidpointCrossTieV1(StrictPublicModel):
    """One open cross-tie using the perimeter tie's section and hook schedule."""

    tie_id: str = Field(min_length=1, max_length=80)
    restrained_bar_ids: tuple[str, str]
    station_offset_mm: float = Field(ge=0)

    @field_validator("restrained_bar_ids", mode="before")
    @classmethod
    def accept_json_array(cls, value: object) -> object:
        return tuple(value) if isinstance(value, list) else value


class RectangularColumnCageV1(StrictPublicModel):
    """One symmetric equal-bar cage with an outer tie and paired midpoint ties."""

    layout: Literal[
        "eight_bar",
        "six_bar_omit_x_face_midpoints",
        "six_bar_omit_y_face_midpoints",
    ]
    longitudinal_bar_diameter_mm: float = Field(gt=0, le=80)
    nominal_cover_mm: float = Field(gt=0, le=2000)
    bar_center_offset_mm: float = Field(gt=0, le=2000)
    aggregate_size_mm: float = Field(gt=0, le=100)
    project_required_cover_mm: float = Field(ge=0, le=2000)
    project_required_bend_radius_mm: float = Field(ge=0, le=2000)
    detailing_basis_reference: str = Field(min_length=1, max_length=240)
    tie: ColumnClosedTieV1 | None
    cross_ties: tuple[ColumnMidpointCrossTieV1, ...] = Field(default=(), max_length=2)

    @field_validator("cross_ties", mode="before")
    @classmethod
    def accept_json_array(cls, value: object) -> object:
        return tuple(value) if isinstance(value, list) else value


class TiedRectangularColumnInputV1(StrictPublicModel):
    """A short braced rectangular member checked at one supplied station."""

    schema_version: Literal["column-tied-rectangular-member-input/v1"] = (
        "column-tied-rectangular-member-input/v1"
    )
    identity: FamilyIdentityV1
    geometry: FourCornerColumnGeometryV1
    actions: RectangularColumnActionsV1
    materials: ColumnMaterialsV1
    reinforcement: RectangularColumnCageV1

    @model_validator(mode="after")
    def check_station(self) -> Self:
        if self.actions.check_station_mm > self.geometry.unsupported_length_mm:
            raise ValueError("check_station_mm must lie within the unsupported length")
        return self


TiedRectangularColumnInputV1.field_contracts = complete_field_contracts_from_schema(
    TiedRectangularColumnInputV1
)


class PositionedRectangularGeometryV1(FourCornerColumnGeometryV1):
    """Ordinary rectangular member dimensions for the positioned cage."""

    b_mm: float = Field(ge=100, le=2000)
    D_mm: float = Field(ge=100, le=2000)


class PositionedColumnBarV1(StrictPublicModel):
    """Explicit centre, diameter and row of one longitudinal bar."""

    bar_id: str = Field(min_length=1, max_length=80)
    x_from_left_mm: float = Field(gt=0)
    y_from_top_mm: float = Field(gt=0)
    diameter_mm: float = Field(ge=1, le=80)
    row: Literal["outer", "inner"]


class PositionedColumnCrossTieV1(ColumnMidpointCrossTieV1):
    """Open link with explicit geometry and side of the aligned bar pair."""

    diameter_mm: float = Field(gt=0, le=80)
    internal_bend_radius_mm: float = Field(ge=0, le=2000)
    hook_angle_deg: float = Field(gt=0, le=180)
    hook_tail_mm: float = Field(ge=0, le=2000)
    hook_side: Literal["negative", "positive"]


class PositionedColumnCageV1(StrictPublicModel):
    """Nine to 32 discrete bars with one hoop and aligned open links."""

    bars: tuple[PositionedColumnBarV1, ...] = Field(min_length=9, max_length=32)
    nominal_cover_mm: float = Field(gt=0, le=2000)
    project_required_cover_mm: float = Field(ge=0, le=2000)
    aggregate_size_mm: float = Field(gt=0, le=100)
    project_required_bend_radius_mm: float = Field(ge=0, le=2000)
    project_required_cross_tie_bend_radius_mm: float = Field(ge=0, le=2000)
    detailing_basis_reference: str = Field(min_length=1, max_length=240)
    tie: ColumnClosedTieV1 | None
    cross_ties: tuple[PositionedColumnCrossTieV1, ...] = Field(
        default=(), max_length=14
    )

    @field_validator("bars", "cross_ties", mode="before")
    @classmethod
    def accept_json_arrays(cls, value: object) -> object:
        return tuple(value) if isinstance(value, list) else value


class PositionedRectangularColumnInputV1(StrictPublicModel):
    """One short braced member with actual mixed bar geometry and signed demand."""

    schema_version: Literal["column-positioned-rectangular-member-input/v1"] = (
        "column-positioned-rectangular-member-input/v1"
    )
    identity: FamilyIdentityV1
    geometry: PositionedRectangularGeometryV1
    actions: RectangularColumnActionsV1
    materials: ColumnMaterialsV1
    reinforcement: PositionedColumnCageV1

    @model_validator(mode="after")
    def check_section(self) -> Self:
        if self.actions.check_station_mm > self.geometry.unsupported_length_mm:
            raise ValueError("check_station_mm must lie within the unsupported length")
        bars = self.reinforcement.bars
        if len({bar.bar_id for bar in bars}) != len(bars):
            raise ValueError("Longitudinal bar IDs must be unique")
        for bar in bars:
            radius = bar.diameter_mm / 2
            if not (
                radius <= bar.x_from_left_mm <= self.geometry.b_mm - radius
                and radius <= bar.y_from_top_mm <= self.geometry.D_mm - radius
            ):
                raise ValueError(f"Bar {bar.bar_id} extends beyond the concrete faces")
        for first, second in combinations(bars, 2):
            if (
                hypot(
                    first.x_from_left_mm - second.x_from_left_mm,
                    first.y_from_top_mm - second.y_from_top_mm,
                )
                < (first.diameter_mm + second.diameter_mm) / 2
            ):
                raise ValueError(
                    f"Bars {first.bar_id} and {second.bar_id} are coincident or overlap"
                )
        return self


PositionedRectangularColumnInputV1.field_contracts = (
    complete_field_contracts_from_schema(PositionedRectangularColumnInputV1)
)
