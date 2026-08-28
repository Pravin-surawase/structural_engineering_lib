"""Strict public request contract for the canonical IS 456 beam journey."""

from __future__ import annotations

import math
import re
from enum import StrEnum
from typing import Any, Self

from pydantic import Field, ValidationInfo, field_validator, model_validator
from pydantic_core import PydanticCustomError

from structural_lib.services.contracts.common import (
    FieldContractV1,
    StrictPublicModel,
    ValidationDimension,
    complete_field_contracts_from_schema,
)
from structural_lib.services.project_beam import EffectiveDepthBasisV1

__all__ = [
    "BEAM_DESIGN_SCHEMA_VERSION",
    "BEAM_FIELD_CONTRACTS",
    "BeamActionsV1",
    "BeamCalculationBasisV1",
    "BeamDesignInputV1",
    "BeamDetailingOptionsV1",
    "BeamServiceabilityV1",
    "DetailingStandard",
    "EffectiveDepthBasisRequestV1",
    "IS456MaterialsV1",
    "MemberIdentityV1",
    "RectangularBeamSectionV1",
]


BEAM_DESIGN_SCHEMA_VERSION = "beam-design-input/v1"
_IDENTITY_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:/@+ -]{0,79}$")


class DetailingStandard(StrEnum):
    """Explicit detailing ruleset selected by the caller."""

    IS456 = "IS456"
    IS13920 = "IS13920"


class MemberIdentityV1(StrictPublicModel):
    """Distinct, stable identities for the member, storey, and load case."""

    member_id: str = Field(min_length=1, max_length=80)
    story: str = Field(min_length=1, max_length=80)
    case_id: str = Field(min_length=1, max_length=80)

    @field_validator("member_id", "story", "case_id")
    @classmethod
    def validate_identity(cls, value: str) -> str:
        if not _IDENTITY_PATTERN.fullmatch(value):
            raise ValueError(
                "identity must use letters, digits, spaces, and . _ : / @ + - only"
            )
        return value


class EffectiveDepthBasisRequestV1(StrictPublicModel):
    """Complete basis for deriving effective depth without hidden arithmetic."""

    clear_cover_mm: float = Field(gt=0)
    stirrup_diameter_mm: float = Field(gt=0)
    tension_bar_diameter_mm: float = Field(gt=0)

    def to_service(self) -> EffectiveDepthBasisV1:
        return EffectiveDepthBasisV1(
            clear_cover_mm=self.clear_cover_mm,
            stirrup_diameter_mm=self.stirrup_diameter_mm,
            tension_bar_diameter_mm=self.tension_bar_diameter_mm,
        )


class RectangularBeamSectionV1(StrictPublicModel):
    """Rectangular section with one explicit effective-depth basis."""

    span_mm: float | None = Field(default=None, gt=0)
    b_mm: float = Field(gt=0, le=2000)
    D_mm: float = Field(gt=0, le=3000)
    d_mm: float | None = Field(default=None, gt=0)
    effective_depth_basis: EffectiveDepthBasisRequestV1 | None = None

    @model_validator(mode="after")
    def validate_depth_basis(self) -> Self:
        supplied = (self.d_mm is not None) + (self.effective_depth_basis is not None)
        if supplied != 1:
            raise ValueError(
                "supply exactly one of d_mm or a complete effective_depth_basis"
            )
        if self.d_mm is not None:
            d_mm = self.d_mm
        else:
            basis = self.effective_depth_basis
            assert basis is not None
            d_mm = (
                self.D_mm
                - basis.clear_cover_mm
                - basis.stirrup_diameter_mm
                - basis.tension_bar_diameter_mm / 2
            )
        if d_mm >= self.D_mm:
            raise ValueError("effective depth must be less than D_mm")
        if self.D_mm / self.b_mm > 6:
            raise ValueError("D_mm / b_mm must not exceed the supported ratio 6")
        return self


class IS456MaterialsV1(StrictPublicModel):
    """Explicit supported material strengths in N/mm2."""

    fck_nmm2: float = Field(ge=15, le=40)
    fy_nmm2: float = Field(ge=250, le=500)


class BeamActionsV1(StrictPublicModel):
    """Finite non-negative factored action magnitudes."""

    mu_knm: float = Field(ge=0)
    vu_kn: float = Field(ge=0)
    tu_knm: float = Field(default=0.0, ge=0)


class BeamCalculationBasisV1(StrictPublicModel):
    """Explicit section/reinforcement values consumed by strength calculation."""

    d_dash_mm: float = Field(gt=0)
    asv_mm2: float = Field(gt=0)
    pt_percent: float | None = Field(default=None, gt=0)
    ast_mm2_for_shear: float | None = Field(default=None, gt=0)


class BeamServiceabilityV1(StrictPublicModel):
    """Explicit opt-in serviceability parameters consumed by the beam service."""

    deflection_params: dict[str, Any] | None = None
    crack_width_params: dict[str, Any] | None = None

    @model_validator(mode="after")
    def require_one_check(self) -> Self:
        if self.deflection_params is None and self.crack_width_params is None:
            raise ValueError("at least one serviceability parameter group is required")
        return self


class BeamDetailingOptionsV1(StrictPublicModel):
    """All caller-owned choices required for detailing and BBS composition."""

    standard: DetailingStandard = Field(strict=False)
    clear_cover_mm: float = Field(gt=0)
    tension_bar_diameter_mm: float = Field(ge=8, le=36)
    compression_bar_diameter_mm: float = Field(ge=8, le=36)
    nominal_top_steel_ratio: float = Field(gt=0, le=1)
    stirrup_diameter_mm: float = Field(ge=6, le=16)
    stirrup_legs: int = Field(ge=2, le=6)
    stirrup_spacing_support_mm: float = Field(gt=0)
    stirrup_spacing_mid_mm: float = Field(gt=0)

    @field_validator("tension_bar_diameter_mm", "compression_bar_diameter_mm")
    @classmethod
    def validate_supported_bar_diameter(cls, value: float) -> float:
        allowed = (8, 10, 12, 16, 20, 25, 32)
        if value not in allowed:
            raise ValueError(f"bar diameter must be one of {allowed}")
        return value

    @property
    def asv_mm2(self) -> float:
        """Return the explicitly selected total stirrup-leg area."""

        return self.stirrup_legs * math.pi * self.stirrup_diameter_mm**2 / 4


class BeamDesignInputV1(StrictPublicModel):
    """Canonical nested request shared by Python and REST v2."""

    schema_version: str = Field(default=BEAM_DESIGN_SCHEMA_VERSION, frozen=True)
    identity: MemberIdentityV1
    section: RectangularBeamSectionV1
    materials: IS456MaterialsV1
    actions: BeamActionsV1
    calculation_basis: BeamCalculationBasisV1
    detailing: BeamDetailingOptionsV1 | None = None
    serviceability: BeamServiceabilityV1 | None = None
    source_provenance: str | None = Field(default=None, max_length=240)

    @field_validator("serviceability")
    @classmethod
    def hold_unfrozen_serviceability(
        cls, value: BeamServiceabilityV1 | None
    ) -> BeamServiceabilityV1 | None:
        if value is not None:
            raise PydanticCustomError(
                "serviceability_scope_hold",
                "canonical serviceability is held until its strict typed models freeze",
            )
        return value

    @field_validator("calculation_basis")
    @classmethod
    def validate_calculation_depth_relation(
        cls,
        value: BeamCalculationBasisV1,
        info: ValidationInfo,
    ) -> BeamCalculationBasisV1:
        section = info.data.get("section")
        if isinstance(section, RectangularBeamSectionV1):
            if section.d_mm is not None:
                d_mm = section.d_mm
            else:
                basis = section.effective_depth_basis
                assert basis is not None
                d_mm = (
                    section.D_mm
                    - basis.clear_cover_mm
                    - basis.stirrup_diameter_mm
                    - basis.tension_bar_diameter_mm / 2
                )
            if value.d_dash_mm >= d_mm:
                raise ValueError("d_dash_mm must be less than effective depth")
        return value

    @field_validator("detailing")
    @classmethod
    def validate_detailing_relations(
        cls,
        value: BeamDetailingOptionsV1 | None,
        info: ValidationInfo,
    ) -> BeamDetailingOptionsV1 | None:
        if value is None:
            return value
        calculation_basis = info.data.get("calculation_basis")
        if isinstance(calculation_basis, BeamCalculationBasisV1) and not math.isclose(
            calculation_basis.asv_mm2,
            value.asv_mm2,
            rel_tol=1e-9,
            abs_tol=1e-9,
        ):
            raise ValueError(
                "calculation_basis.asv_mm2 must equal the selected stirrup-leg area"
            )
        section = info.data.get("section")
        if (
            isinstance(section, RectangularBeamSectionV1)
            and section.effective_depth_basis is not None
        ):
            basis = section.effective_depth_basis
            if not (
                math.isclose(basis.clear_cover_mm, value.clear_cover_mm)
                and math.isclose(basis.stirrup_diameter_mm, value.stirrup_diameter_mm)
                and math.isclose(
                    basis.tension_bar_diameter_mm,
                    value.tension_bar_diameter_mm,
                )
            ):
                raise ValueError(
                    "detailing cover and bar choices must match effective_depth_basis"
                )
        return value

    @model_validator(mode="after")
    def validate_consumability(self) -> Self:
        if self.schema_version != BEAM_DESIGN_SCHEMA_VERSION:
            raise ValueError(f"schema_version must be {BEAM_DESIGN_SCHEMA_VERSION}")
        if self.actions.tu_knm > 0 and self.detailing is None:
            raise ValueError("detailing is required when tu_knm is greater than zero")
        if self.detailing is not None:
            if self.section.span_mm is None:
                raise ValueError("section.span_mm is required for detailing")
            if self.detailing.clear_cover_mm >= self.section.D_mm:
                raise ValueError(
                    "detailing.clear_cover_mm must be less than section.D_mm"
                )
        return self


_TYPE = ValidationDimension.TYPE_AND_FINITE_VALUE
_RANGE = ValidationDimension.RANGE_AND_ZERO_POLICY
_UNIT = ValidationDimension.UNIT_AND_QUANTITY
_CODE = ValidationDimension.CODE_AND_MATERIAL_DOMAIN
_RELATION = ValidationDimension.CROSS_FIELD_RELATION
_IDENTITY = ValidationDimension.IDENTITY_AND_PROVENANCE
_ENUM = ValidationDimension.ENUM_AND_TOPOLOGY
_DOWNSTREAM = ValidationDimension.DOWNSTREAM_CONSUMABILITY


BEAM_FIELD_CONTRACTS = (
    FieldContractV1(path="identity.member_id", dimensions=(_TYPE, _IDENTITY)),
    FieldContractV1(path="identity.story", dimensions=(_TYPE, _IDENTITY)),
    FieldContractV1(path="identity.case_id", dimensions=(_TYPE, _IDENTITY)),
    FieldContractV1(
        path="section.span_mm",
        dimensions=(_TYPE, _RANGE, _UNIT, _DOWNSTREAM),
        unit="mm",
        zero_allowed=False,
    ),
    FieldContractV1(
        path="section.b_mm",
        dimensions=(_TYPE, _RANGE, _UNIT, _RELATION),
        unit="mm",
        zero_allowed=False,
    ),
    FieldContractV1(
        path="section.D_mm",
        dimensions=(_TYPE, _RANGE, _UNIT, _RELATION),
        unit="mm",
        zero_allowed=False,
    ),
    FieldContractV1(
        path="section.d_mm",
        dimensions=(_TYPE, _RANGE, _UNIT, _RELATION),
        unit="mm",
        zero_allowed=False,
    ),
    FieldContractV1(
        path="section.effective_depth_basis",
        dimensions=(_TYPE, _UNIT, _RELATION, _DOWNSTREAM),
        unit="mm",
    ),
    FieldContractV1(
        path="materials.fck_nmm2",
        dimensions=(_TYPE, _RANGE, _UNIT, _CODE),
        unit="N/mm2",
        zero_allowed=False,
    ),
    FieldContractV1(
        path="materials.fy_nmm2",
        dimensions=(_TYPE, _RANGE, _UNIT, _CODE),
        unit="N/mm2",
        zero_allowed=False,
    ),
    FieldContractV1(
        path="actions.mu_knm",
        dimensions=(_TYPE, _RANGE, _UNIT),
        unit="kN.m",
        zero_allowed=True,
    ),
    FieldContractV1(
        path="actions.vu_kn",
        dimensions=(_TYPE, _RANGE, _UNIT),
        unit="kN",
        zero_allowed=True,
    ),
    FieldContractV1(
        path="actions.tu_knm",
        dimensions=(_TYPE, _RANGE, _UNIT, _RELATION),
        unit="kN.m",
        zero_allowed=True,
    ),
    FieldContractV1(
        path="calculation_basis.d_dash_mm",
        dimensions=(_TYPE, _RANGE, _UNIT, _DOWNSTREAM),
        unit="mm",
        zero_allowed=False,
    ),
    FieldContractV1(
        path="calculation_basis.asv_mm2",
        dimensions=(_TYPE, _RANGE, _UNIT, _DOWNSTREAM),
        unit="mm2",
        zero_allowed=False,
    ),
    FieldContractV1(path="detailing.standard", dimensions=(_TYPE, _ENUM, _DOWNSTREAM)),
    FieldContractV1(
        path="detailing.clear_cover_mm",
        dimensions=(_TYPE, _RANGE, _UNIT, _RELATION, _DOWNSTREAM),
        unit="mm",
        zero_allowed=False,
    ),
    FieldContractV1(
        path="detailing.tension_bar_diameter_mm",
        dimensions=(_TYPE, _RANGE, _UNIT, _ENUM, _DOWNSTREAM),
        unit="mm",
        zero_allowed=False,
    ),
    FieldContractV1(
        path="detailing.compression_bar_diameter_mm",
        dimensions=(_TYPE, _RANGE, _UNIT, _ENUM, _DOWNSTREAM),
        unit="mm",
        zero_allowed=False,
    ),
    FieldContractV1(
        path="detailing.nominal_top_steel_ratio",
        dimensions=(_TYPE, _RANGE, _DOWNSTREAM),
        zero_allowed=False,
    ),
    FieldContractV1(
        path="detailing.stirrup_diameter_mm",
        dimensions=(_TYPE, _RANGE, _UNIT, _DOWNSTREAM),
        unit="mm",
        zero_allowed=False,
    ),
    FieldContractV1(
        path="detailing.stirrup_legs",
        dimensions=(_TYPE, _RANGE, _DOWNSTREAM),
        zero_allowed=False,
    ),
    FieldContractV1(
        path="detailing.stirrup_spacing_support_mm",
        dimensions=(_TYPE, _RANGE, _UNIT, _DOWNSTREAM),
        unit="mm",
        zero_allowed=False,
    ),
    FieldContractV1(
        path="detailing.stirrup_spacing_mid_mm",
        dimensions=(_TYPE, _RANGE, _UNIT, _DOWNSTREAM),
        unit="mm",
        zero_allowed=False,
    ),
)

BeamDesignInputV1.field_contracts = complete_field_contracts_from_schema(
    BeamDesignInputV1, overrides=BEAM_FIELD_CONTRACTS
)
