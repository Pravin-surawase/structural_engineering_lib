"""Typed supplied catalogue and analysis basis for COL06."""

from __future__ import annotations

from typing import Annotated, Literal, Self

from pydantic import Field, field_validator, model_validator

from structural_lib.services.canonical_family import FamilyIdentityV1
from structural_lib.services.contracts.column_member import (
    ColumnClosedTieV1,
    ColumnMidpointCrossTieV1,
    FourCornerColumnGeometryV1,
    RectangularColumnActionsV1,
)
from structural_lib.services.contracts.common import (
    StrictPublicModel,
    complete_field_contracts_from_schema,
)
from structural_lib.services.contracts.family_f1 import ColumnMaterialsV1

MAX_COLUMN_CANDIDATES = 128
_CatalogueId = Annotated[
    str, Field(min_length=1, max_length=24, pattern=r"^[A-Za-z0-9_-]+$")
]
_Revision = Annotated[str, Field(min_length=1, max_length=160, pattern=r"\S")]


class ColumnCatalogueSizeV1(StrictPublicModel):
    """One approved rectangular size with its orientation retained."""

    size_id: _CatalogueId
    b_mm: float = Field(ge=200, le=2000)
    D_mm: float = Field(ge=200, le=2000)


class ColumnCatalogueMemberV1(StrictPublicModel):
    """Restraint and length shared by every candidate."""

    unsupported_length_mm: float = Field(ge=100, le=50000)
    end_condition: Literal["FIXED_FIXED", "FIXED_HINGED", "HINGED_HINGED"]
    braced: Literal[True]


class ColumnCatalogueTieV1(StrictPublicModel):
    """One supplied hoop and its midpoint restraint schedule."""

    option_id: _CatalogueId
    tie: ColumnClosedTieV1
    cross_ties: tuple[ColumnMidpointCrossTieV1, ...] = Field(default=(), max_length=2)

    @field_validator("cross_ties", mode="before")
    @classmethod
    def accept_json_arrays(cls, value: object) -> object:
        return tuple(value) if isinstance(value, list) else value


class ColumnCatalogueDetailingV1(StrictPublicModel):
    """Shared local cover, bend requirements and corner inset."""

    nominal_cover_mm: float = Field(gt=0, le=500)
    project_required_cover_mm: float = Field(ge=0, le=500)
    corner_inset_mm: float = Field(ge=0, le=2)
    aggregate_size_mm: float = Field(gt=0, le=100)
    project_required_bend_radius_mm: float = Field(ge=0, le=2000)
    detailing_basis_reference: str = Field(min_length=1, max_length=240)


class ColumnCatalogueActionV1(RectangularColumnActionsV1):
    """One supplied concurrent combination at an identified station."""

    combination_id: _CatalogueId


class ColumnCatalogueAnalysisV1(StrictPublicModel):
    """Caller-declared geometry and stiffness of the analysis supplying actions."""

    geometry: FourCornerColumnGeometryV1
    fck_nmm2: float = Field(ge=15, le=80)
    analysis_revision: _Revision
    current_analysis_revision: _Revision
    stiffness_basis: Literal["gross_section", "reinforcement_dependent"]


class ColumnCatalogueInputV1(StrictPublicModel):
    """Finite selection domain for the eight-bar short rectangular profile."""

    schema_version: Literal["column-catalogue-selection-input/v1"] = (
        "column-catalogue-selection-input/v1"
    )
    identity: FamilyIdentityV1
    member: ColumnCatalogueMemberV1
    materials: ColumnMaterialsV1
    detailing: ColumnCatalogueDetailingV1
    analysis: ColumnCatalogueAnalysisV1
    sizes: tuple[ColumnCatalogueSizeV1, ...] = Field(min_length=1, max_length=16)
    longitudinal_diameters_mm: tuple[Annotated[int, Field(ge=12, le=40)], ...] = Field(
        min_length=1, max_length=16
    )
    tie_options: tuple[ColumnCatalogueTieV1, ...] = Field(min_length=1, max_length=16)
    actions: tuple[ColumnCatalogueActionV1, ...] = Field(min_length=1, max_length=8)
    evaluation_limit: int = Field(
        default=MAX_COLUMN_CANDIDATES, ge=1, le=MAX_COLUMN_CANDIDATES
    )

    @field_validator(
        "sizes", "longitudinal_diameters_mm", "tie_options", "actions", mode="before"
    )
    @classmethod
    def accept_json_arrays(cls, value: object) -> object:
        return tuple(value) if isinstance(value, list) else value

    @model_validator(mode="after")
    def check_catalogue(self) -> Self:
        unique_entries = (
            ("size IDs", [size.size_id for size in self.sizes]),
            ("oriented sizes", [(size.b_mm, size.D_mm) for size in self.sizes]),
            ("longitudinal diameters", list(self.longitudinal_diameters_mm)),
            ("tie option IDs", [option.option_id for option in self.tie_options]),
            ("combination IDs", [row.combination_id for row in self.actions]),
        )
        for name, entries in unique_entries:
            if len(set(entries)) != len(entries):
                raise ValueError(f"Supply unique {name}")
        count = (
            len(self.sizes)
            * len(self.longitudinal_diameters_mm)
            * len(self.tie_options)
        )
        if count > MAX_COLUMN_CANDIDATES:
            raise ValueError(
                f"Supply at most {MAX_COLUMN_CANDIDATES} catalogue combinations"
            )
        if any(
            row.check_station_mm > self.member.unsupported_length_mm
            for row in self.actions
        ):
            raise ValueError("Every check station must lie on the column member")
        return self


ColumnCatalogueInputV1.field_contracts = complete_field_contracts_from_schema(
    ColumnCatalogueInputV1
)
