# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Typed inputs for a declared set of supported slab ULS combinations."""

from __future__ import annotations

from typing import Annotated, Literal, Self

from pydantic import Field, field_validator, model_validator

from structural_lib.services.canonical_family import FamilyIdentityV1
from structural_lib.services.contracts.common import StrictPublicModel
from structural_lib.services.contracts.family_f1 import (
    ContinuousOneWaySlabGeometryV1,
    ContinuousOneWaySlabReinforcementV1,
    SlabMaterialsV1,
    SlabServiceabilityEvidenceV1,
    TwoWaySlabGeometryV1,
    TwoWaySlabReinforcementV1,
)

RowId = Annotated[str, Field(min_length=1, max_length=80)]
Revision = Annotated[str, Field(min_length=1, max_length=160)]


class _ExternalSlabCoefficientBasisV1(StrictPublicModel):
    kind: Literal["external"]
    coefficient_source_reference: str = Field(min_length=1)
    coefficient_source_is_approved: Literal[True]
    qualified_coefficient_acceptance_reference: str = Field(min_length=1)
    qualified_coefficient_acceptance_acknowledged: Literal[True]


class ExternalOneWaySlabCoefficientBasisV1(_ExternalSlabCoefficientBasisV1):
    """Approved positive, negative and shear coefficients for one continuous row."""

    positive_moment_coefficient: float = Field(gt=0)
    negative_moment_coefficient: float = Field(gt=0)
    shear_coefficient: float = Field(gt=0)


class BuiltinOneWaySlabCoefficientBasisV1(StrictPublicModel):
    """Tables 12/13 locations and the non-fixed portion of the row's total UDL."""

    kind: Literal["builtin"]
    factored_nonfixed_imposed_load_kn_per_m2: float = Field(ge=0)
    positive_location: Literal["end_span_positive", "interior_span_positive"]
    negative_location: Literal[
        "next_to_end_support_negative", "other_interior_support_negative"
    ]
    shear_location: Literal[
        "end_support",
        "next_to_end_support_outer",
        "next_to_end_support_inner",
        "other_interior_support",
    ]


class ExternalTwoWaySlabCoefficientBasisV1(_ExternalSlabCoefficientBasisV1):
    """Approved regional coefficient magnitudes for one oriented panel row."""

    support_topology_kind: str = Field(min_length=1)
    alpha_x_negative: float = Field(ge=0)
    alpha_x_positive: float = Field(gt=0)
    alpha_y_negative: float = Field(ge=0)
    alpha_y_positive: float = Field(gt=0)


class BuiltinTwoWaySlabCoefficientBasisV1(StrictPublicModel):
    """Select Table 26 or 27 from the shared physical topology."""

    kind: Literal["builtin"]


class _SlabActionRowInputV1(StrictPublicModel):
    row_id: RowId
    factored_area_load_kn_per_m2: float = Field(gt=0)


class OneWaySlabActionRowInputV1(_SlabActionRowInputV1):
    """A continuous one-way UDL and its complete coefficient basis."""

    coefficient_basis: Annotated[
        ExternalOneWaySlabCoefficientBasisV1 | BuiltinOneWaySlabCoefficientBasisV1,
        Field(discriminator="kind"),
    ]

    @model_validator(mode="after")
    def validate_load_split(self) -> Self:
        basis = self.coefficient_basis
        if (
            isinstance(basis, BuiltinOneWaySlabCoefficientBasisV1)
            and basis.factored_nonfixed_imposed_load_kn_per_m2
            > self.factored_area_load_kn_per_m2
        ):
            raise ValueError("non-fixed UDL must not exceed the total UDL")
        return self


class TwoWaySlabActionRowInputV1(_SlabActionRowInputV1):
    """An oriented two-way panel UDL and its complete coefficient basis."""

    coefficient_basis: Annotated[
        ExternalTwoWaySlabCoefficientBasisV1 | BuiltinTwoWaySlabCoefficientBasisV1,
        Field(discriminator="kind"),
    ]


class _SlabActionSetInputV1(StrictPublicModel):
    schema_version: Literal["slab-action-set-input/v1"] = "slab-action-set-input/v1"
    identity: FamilyIdentityV1
    geometry_revision: Revision
    reinforcement_revision: Revision
    materials: SlabMaterialsV1
    serviceability_evidence: SlabServiceabilityEvidenceV1 | None = None
    required_row_ids: tuple[RowId, ...] = Field(min_length=1)

    @field_validator("required_row_ids", "rows", mode="before", check_fields=False)
    @classmethod
    def _tuple_from_list(cls, value: object) -> object:
        return tuple(value) if isinstance(value, list) else value

    def _validate_inventory(self, supplied: tuple[RowId, ...]) -> None:
        if len(set(self.required_row_ids)) != len(self.required_row_ids):
            raise ValueError("required_row_ids contains duplicate IDs")
        if len(set(supplied)) != len(supplied):
            raise ValueError("rows contains duplicate row IDs")
        unexpected = sorted(set(supplied) - set(self.required_row_ids))
        if unexpected:
            raise ValueError(
                f"rows contains undeclared row IDs: {', '.join(unexpected)}"
            )


class ContinuousOneWaySlabActionSetInputV1(_SlabActionSetInputV1):
    """One continuous strip, one bar revision and multiple required UDL rows."""

    kind: Literal["continuous_one_way"]
    geometry: ContinuousOneWaySlabGeometryV1
    reinforcement: ContinuousOneWaySlabReinforcementV1
    substantially_uniform_load_acknowledged: Literal[True]
    redistribution_applied: Literal[False]
    rows: tuple[OneWaySlabActionRowInputV1, ...]

    @model_validator(mode="after")
    def validate_inventory(self) -> Self:
        if self.geometry.strip_width_mm != 1000:
            raise ValueError("supplied one-way slab actions require a 1000 mm strip")
        self._validate_inventory(tuple(row.row_id for row in self.rows))
        return self


class TwoWaySlabActionSetInputV1(_SlabActionSetInputV1):
    """One oriented panel, one bar revision and multiple required UDL rows."""

    kind: Literal["two_way_panel"]
    geometry: TwoWaySlabGeometryV1
    reinforcement: TwoWaySlabReinforcementV1
    rows: tuple[TwoWaySlabActionRowInputV1, ...]

    @model_validator(mode="after")
    def validate_inventory(self) -> Self:
        self._validate_inventory(tuple(row.row_id for row in self.rows))
        return self


SlabActionSetInputV1 = ContinuousOneWaySlabActionSetInputV1 | TwoWaySlabActionSetInputV1
