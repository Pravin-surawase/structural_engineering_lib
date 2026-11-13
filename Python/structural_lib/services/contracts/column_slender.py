"""Typed input for the actual-cage slender rectangular column workflow."""

from __future__ import annotations

from math import isclose
from typing import Annotated, Literal, Self

from pydantic import Field, StrictBool, field_validator, model_validator

from structural_lib.core.errors import InputContractError, InputIssueV1
from structural_lib.services.canonical_family import FamilyIdentityV1
from structural_lib.services.contracts.column_member import (
    PositionedColumnCageV1,
    RectangularColumnCageV1,
)
from structural_lib.services.contracts.common import (
    StrictPublicModel,
    complete_field_contracts_from_schema,
)
from structural_lib.services.contracts.family_f1 import ColumnMaterialsV1

_Identity = Annotated[str, Field(min_length=1, max_length=160)]


class ColumnRestraintPlaneV1(StrictPublicModel):
    """Explicit unsupported and effective lengths in one plane."""

    unsupported_length_mm: float = Field(ge=100, le=50000)
    effective_length_mm: float = Field(gt=0, le=50000)
    restraint_basis: _Identity


class SlenderRectangularGeometryV1(StrictPublicModel):
    """Prismatic braced rectangle with restraint specified by axis."""

    b_mm: float = Field(ge=100, le=2000)
    D_mm: float = Field(ge=100, le=2000)
    length_mm: float = Field(ge=100, le=50000)
    braced: Literal[True]
    x: ColumnRestraintPlaneV1
    y: ColumnRestraintPlaneV1

    @model_validator(mode="after")
    def check_restraint_lengths(self) -> Self:
        if (
            max(self.x.unsupported_length_mm, self.y.unsupported_length_mm)
            > self.length_mm
        ):
            raise ValueError(
                "Unsupported length cannot exceed the physical member length"
            )
        return self


class ColumnMomentPairV1(StrictPublicModel):
    """Signed simultaneous moments in the section convention."""

    mx_knm: float = Field(ge=-1e9, le=1e9)
    my_knm: float = Field(ge=-1e9, le=1e9)


class ColumnCriticalStationV1(ColumnMomentPairV1):
    """One labelled simultaneous moment pair from the supplied analysis."""

    station_id: _Identity
    station_mm: float = Field(ge=0)


class FirstOrderColumnActionsV1(StrictPublicModel):
    """A concurrent first-order combination with physical end actions."""

    basis: Literal["first_order"]
    combination_id: _Identity
    pu_kn: float = Field(gt=0, le=1e9)
    end_a: ColumnMomentPairV1
    end_b: ColumnMomentPairV1
    magnitude_summary: ColumnMomentPairV1 | None = None
    has_transverse_member_load: StrictBool | None = None

    @model_validator(mode="after")
    def check_envelope(self) -> Self:
        if self.magnitude_summary is not None:
            for name in ("mx_knm", "my_knm"):
                actual = getattr(self.magnitude_summary, name)
                expected = max(
                    abs(getattr(end, name)) for end in (self.end_a, self.end_b)
                )
                if not isclose(actual, expected, rel_tol=0, abs_tol=1e-9):
                    raise InputContractError(
                        (
                            InputIssueV1(
                                "COLUMN_ACTION_CONFLICT",
                                f"actions.magnitude_summary.{name}",
                                "The supplied magnitude must match the two signed end actions.",
                                received=actual,
                                constraint=f"Expected {expected:g} kNm",
                            ),
                        )
                    )
        return self


class SuppliedSecondOrderColumnActionsV1(StrictPublicModel):
    """Concurrent action rows from analysis including local member deflection."""

    basis: Literal["supplied_second_order"]
    combination_id: _Identity
    pu_kn: float = Field(gt=0, le=1e9)
    member_deflection_basis: (
        Annotated[str, Field(min_length=1, max_length=320)] | None
    ) = None
    required_station_ids: tuple[_Identity, ...] = Field(default=(), max_length=32)
    stations: tuple[ColumnCriticalStationV1, ...] = Field(default=(), max_length=32)
    apply_local_additional_moments: StrictBool = False

    @field_validator("required_station_ids", "stations", mode="before")
    @classmethod
    def accept_json_arrays(cls, value: object) -> object:
        return tuple(value) if isinstance(value, list) else value

    @model_validator(mode="after")
    def check_actions(self) -> Self:
        if self.apply_local_additional_moments:
            raise InputContractError(
                (
                    InputIssueV1(
                        "COLUMN_ACTION_BASIS_CONFLICT",
                        "actions.apply_local_additional_moments",
                        "Supplied second-order actions cannot be combined with local additional moments.",
                    ),
                )
            )
        if len(set(self.required_station_ids)) != len(self.required_station_ids):
            raise ValueError("Required station IDs must be unique")
        if len({row.station_id for row in self.stations}) != len(self.stations):
            raise ValueError("Supplied station IDs must be unique")
        if any(row.station_id in {"MIN-ECC-X", "MIN-ECC-Y"} for row in self.stations):
            raise ValueError(
                "Station IDs must differ from the minimum-eccentricity check IDs"
            )
        if len({row.station_mm for row in self.stations}) != len(self.stations):
            raise ValueError("One concurrent row per physical station is supported")
        return self


class SlenderRectangularColumnInputV1(StrictPublicModel):
    """Actual rectangular cage, member restraint and one concurrent combination."""

    schema_version: Literal["column-slender-rectangular-member-input/v1"] = (
        "column-slender-rectangular-member-input/v1"
    )
    identity: FamilyIdentityV1
    geometry: SlenderRectangularGeometryV1
    materials: ColumnMaterialsV1
    reinforcement: RectangularColumnCageV1 | PositionedColumnCageV1
    actions: Annotated[
        FirstOrderColumnActionsV1 | SuppliedSecondOrderColumnActionsV1,
        Field(discriminator="basis"),
    ]
    analysis_revision: _Identity
    current_analysis_revision: _Identity

    @model_validator(mode="after")
    def check_positions(self) -> Self:
        if isinstance(self.actions, SuppliedSecondOrderColumnActionsV1) and any(
            row.station_mm > self.geometry.length_mm for row in self.actions.stations
        ):
            raise ValueError("Every station must lie on the physical member")
        steel = self.reinforcement
        if isinstance(steel, PositionedColumnCageV1):
            steel.validate_positions(self.geometry.b_mm, self.geometry.D_mm)
        return self


SlenderRectangularColumnInputV1.field_contracts = complete_field_contracts_from_schema(
    SlenderRectangularColumnInputV1
)
