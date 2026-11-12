"""Typed request for a short circular tied or spiral column."""

from __future__ import annotations

from typing import Annotated, Literal, Self

from pydantic import Field, StrictBool, model_validator

from structural_lib.services.canonical_family import FamilyIdentityV1
from structural_lib.services.contracts.column_member import RectangularColumnActionsV1
from structural_lib.services.contracts.common import (
    StrictPublicModel,
    complete_field_contracts_from_schema,
)
from structural_lib.services.contracts.family_f1 import ColumnMaterialsV1


class CircularColumnGeometryV1(StrictPublicModel):
    """One solid braced circle and its ordinary end restraint."""

    diameter_mm: float = Field(ge=200, le=2000)
    unsupported_length_mm: float = Field(ge=100, le=50000)
    end_condition: Literal["FIXED_FIXED", "FIXED_HINGED", "HINGED_HINGED"]
    braced: Literal[True]


class CircularTransverseV1(StrictPublicModel):
    """Common section and axial spacing of a ring or spiral."""

    tie_id: str = Field(min_length=1, max_length=80)
    diameter_mm: float = Field(gt=0, le=80)
    pitch_mm: float = Field(gt=0, le=50000)


class CircularRingV1(CircularTransverseV1):
    """Closed ring with a supplied circumferential closure detail."""

    kind: Literal["tied"]
    closed: StrictBool
    closure_reference: Annotated[str, Field(min_length=1, max_length=240)] | None = None


class CircularSpiralV1(CircularTransverseV1):
    """Uniform spiral and declared extra turns at the two ends."""

    kind: Literal["spiral"]
    fy_nmm2: float = Field(ge=250, le=550)
    start_extra_turns: Annotated[float, Field(ge=0, le=100)] | None = None
    end_extra_turns: Annotated[float, Field(ge=0, le=100)] | None = None
    axial_enhancement: StrictBool


class CircularColumnCageV1(StrictPublicModel):
    """A regular ring of equal bars with optional transverse evidence."""

    bar_count: int = Field(ge=3, le=32)
    bar_diameter_mm: float = Field(gt=0, le=80)
    ring_radius_mm: float = Field(gt=0, le=1000)
    first_bar_angle_deg: float = Field(ge=0, lt=360)
    aggregate_size_mm: float = Field(gt=0, le=100)
    nominal_cover_mm: float = Field(gt=0, le=1000)
    project_required_cover_mm: float = Field(ge=0, le=1000)
    transverse: (
        Annotated[CircularRingV1 | CircularSpiralV1, Field(discriminator="kind")] | None
    )


class CircularColumnInputV1(StrictPublicModel):
    """One concurrent compression and signed moment pair on an actual cage."""

    schema_version: Literal["column-circular-member-input/v1"] = (
        "column-circular-member-input/v1"
    )
    identity: FamilyIdentityV1
    geometry: CircularColumnGeometryV1
    actions: RectangularColumnActionsV1
    materials: ColumnMaterialsV1
    reinforcement: CircularColumnCageV1

    @model_validator(mode="after")
    def check_dimensions(self) -> Self:
        geometry, steel = self.geometry, self.reinforcement
        radius = geometry.diameter_mm / 2
        if self.actions.check_station_mm > geometry.unsupported_length_mm:
            raise ValueError("check_station_mm must lie within the unsupported length")
        if steel.ring_radius_mm + steel.bar_diameter_mm / 2 > radius:
            raise ValueError("The longitudinal bar circles must fit inside the section")
        transverse = steel.transverse
        if (
            transverse is not None
            and steel.nominal_cover_mm + transverse.diameter_mm >= radius
        ):
            raise ValueError(
                "The circular transverse reinforcement must enclose a positive core"
            )
        return self


CircularColumnInputV1.field_contracts = complete_field_contracts_from_schema(
    CircularColumnInputV1
)
