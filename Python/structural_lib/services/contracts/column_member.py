"""Versioned physical four-corner column request."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, StrictBool

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
