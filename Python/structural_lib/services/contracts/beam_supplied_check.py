"""Strict request contract for supplied rectangular-beam checking."""

from __future__ import annotations

import math
from typing import Literal, Self

from pydantic import Field, field_validator, model_validator

from structural_lib.services.beam_reinforcement import (
    BeamReinforcementSelectionConstraintsV1,
    LongitudinalBarLayersV1,
    SuppliedBeamReinforcementV1,
)
from structural_lib.services.contracts.beam import (
    CentroidCoverDepthRequestV1,
    EffectiveDepthBasisRequestV1,
    IS456ReinforcementMaterialsV1,
    MemberIdentityV1,
)
from structural_lib.services.contracts.common import StrictPublicModel
from structural_lib.services.project_beam import (
    EffectiveDepthResolutionV1,
    resolve_effective_depth_v1,
)

__all__ = [
    "BEAM_SUPPLIED_CHECK_SCHEMA_VERSION",
    "BeamBarLayersV2",
    "BeamReinforcementSelectionV2",
    "BeamSuppliedCheckActionsV2",
    "BeamSuppliedCheckRequestV2",
    "BeamSuppliedCheckSectionV2",
    "BeamSuppliedReinforcementV2",
    "BeamSupportBasisV2",
]


BEAM_SUPPLIED_CHECK_SCHEMA_VERSION: Literal["beam-supplied-check/v2"] = (
    "beam-supplied-check/v2"
)


class BeamBarLayersV2(StrictPublicModel):
    """One diameter in explicit layers, ordered inward from one beam face."""

    diameter_mm: float = Field(gt=0, le=40)
    bars_per_layer: tuple[int, ...] = Field(min_length=1, max_length=4)
    vertical_center_spacings_mm: tuple[float, ...] = ()

    @field_validator("bars_per_layer", "vertical_center_spacings_mm", mode="before")
    @classmethod
    def accept_json_arrays(cls, value: object) -> object:
        """Normalize decoded JSON arrays to the immutable runtime carrier."""

        return tuple(value) if isinstance(value, list) else value

    @model_validator(mode="after")
    def validate_layers(self) -> Self:
        if any(count < 2 for count in self.bars_per_layer):
            raise ValueError("bars_per_layer must contain at least two bars per layer")
        if len(self.vertical_center_spacings_mm) != len(self.bars_per_layer) - 1:
            raise ValueError(
                "vertical_center_spacings_mm must contain one value between layers"
            )
        if any(spacing <= 0 for spacing in self.vertical_center_spacings_mm):
            raise ValueError("vertical_center_spacings_mm values must be positive")
        return self

    @property
    def count(self) -> int:
        """Return the total longitudinal bar count."""

        return sum(self.bars_per_layer)

    @property
    def area_provided_mm2(self) -> float:
        """Return the exact area represented by the declared bar layers."""

        return self.count * math.pi * self.diameter_mm**2 / 4.0

    def to_service(self) -> LongitudinalBarLayersV1:
        """Translate to the accepted supplied-reinforcement service contract."""

        return LongitudinalBarLayersV1(
            diameter_mm=self.diameter_mm,
            bars_per_layer=self.bars_per_layer,
            vertical_center_spacings_mm=self.vertical_center_spacings_mm,
        )


class BeamSuppliedCheckSectionV2(StrictPublicModel):
    """Rectangular section with exactly one complete effective-depth owner."""

    b_mm: float = Field(gt=0, le=2000)
    D_mm: float = Field(gt=0, le=3000)
    d_mm: float | None = Field(default=None, gt=0)
    effective_depth_basis: (
        EffectiveDepthBasisRequestV1 | CentroidCoverDepthRequestV1 | None
    ) = None

    @model_validator(mode="after")
    def validate_depth_basis(self) -> Self:
        supplied = (self.d_mm is not None) + (self.effective_depth_basis is not None)
        if supplied != 1:
            raise ValueError(
                "supply exactly one of d_mm or a complete effective_depth_basis"
            )
        self.resolve_effective_depth()
        if self.D_mm / self.b_mm > 6:
            raise ValueError("D_mm / b_mm must not exceed the supported ratio 6")
        return self

    def resolve_effective_depth(self) -> EffectiveDepthResolutionV1:
        """Return the shared explicit-or-derived effective-depth resolution."""

        basis = self.effective_depth_basis
        return resolve_effective_depth_v1(
            D_mm=self.D_mm,
            d_mm=self.d_mm,
            effective_depth_basis=basis.to_service() if basis is not None else None,
        )


class BeamSuppliedCheckActionsV2(StrictPublicModel):
    """Factored actions supported by the rectangular supplied-check slice."""

    mu_knm: float = Field(ge=0)
    vu_kn: float = Field(ge=0)
    primary_tension_face: Literal["TOP", "BOTTOM"]


class BeamSuppliedReinforcementV2(StrictPublicModel):
    """Exact longitudinal layers and transverse reinforcement being checked."""

    clear_cover_mm: float = Field(gt=0, le=100)
    tension: BeamBarLayersV2
    compression_or_hanger: BeamBarLayersV2
    stirrup_diameter_mm: float = Field(ge=6, le=16)
    stirrup_legs: int = Field(ge=2, le=6)
    stirrup_spacing_mm: float = Field(gt=0, le=300)
    bar_type: Literal["deformed", "plain"]
    has_standard_bend_at_start: bool
    has_standard_bend_at_end: bool
    source_reference: str = Field(min_length=1, max_length=240)

    @property
    def asv_mm2(self) -> float:
        """Return the total area of the declared vertical stirrup legs."""

        return self.stirrup_legs * math.pi * self.stirrup_diameter_mm**2 / 4.0

    def to_service(self) -> SuppliedBeamReinforcementV1:
        """Translate without changing the declared reinforcement geometry."""

        return SuppliedBeamReinforcementV1(
            tension=self.tension.to_service(),
            compression_or_hanger=self.compression_or_hanger.to_service(),
            bar_type=self.bar_type,
            has_standard_bend_at_start=self.has_standard_bend_at_start,
            has_standard_bend_at_end=self.has_standard_bend_at_end,
            source_reference=self.source_reference,
        )


class BeamReinforcementSelectionV2(StrictPublicModel):
    """Caller-owned limits used by the bounded arrangement evaluator."""

    permitted_diameters_mm: tuple[float, ...] = Field(min_length=1)
    maximum_layers: int = Field(ge=1, le=4)
    maximum_bars_per_layer: int = Field(ge=2, le=20)
    nominal_max_aggregate_size_mm: float = Field(gt=0)
    effective_depth_tolerance_mm: float = Field(ge=0)
    objective: Literal["min_area", "min_bar_count", "max_spacing"]
    source_reference: str = Field(min_length=1, max_length=240)

    @field_validator("permitted_diameters_mm", mode="before")
    @classmethod
    def accept_json_array(cls, value: object) -> object:
        """Normalize a decoded JSON array before strict tuple validation."""

        return tuple(value) if isinstance(value, list) else value

    def to_service(self) -> BeamReinforcementSelectionConstraintsV1:
        """Translate to the accepted selection-constraint owner."""

        return BeamReinforcementSelectionConstraintsV1(
            permitted_diameters_mm=self.permitted_diameters_mm,
            maximum_layers=self.maximum_layers,
            maximum_bars_per_layer=self.maximum_bars_per_layer,
            nominal_max_aggregate_size_mm=self.nominal_max_aggregate_size_mm,
            effective_depth_tolerance_mm=self.effective_depth_tolerance_mm,
            objective=self.objective,
            source_reference=self.source_reference,
        )


class BeamSupportBasisV2(StrictPublicModel):
    """Source-referenced support widths used for the anchorage check."""

    start_width_mm: float = Field(gt=0)
    end_width_mm: float = Field(gt=0)
    source_reference: str = Field(min_length=1, max_length=240)


class BeamSuppliedCheckRequestV2(StrictPublicModel):
    """Complete supplied-reinforcement beam-check request."""

    schema_version: Literal["beam-supplied-check/v2"] = (
        BEAM_SUPPLIED_CHECK_SCHEMA_VERSION
    )
    correlation_id: str = Field(min_length=1, max_length=120)
    identity: MemberIdentityV1
    section: BeamSuppliedCheckSectionV2
    materials: IS456ReinforcementMaterialsV1
    actions: BeamSuppliedCheckActionsV2
    reinforcement: BeamSuppliedReinforcementV2
    selection: BeamReinforcementSelectionV2
    support: BeamSupportBasisV2 | None = None
    source_provenance: str | None = Field(default=None, max_length=240)

    @model_validator(mode="after")
    def validate_consumability(self) -> Self:
        if self.schema_version != BEAM_SUPPLIED_CHECK_SCHEMA_VERSION:
            raise ValueError(
                f"schema_version must be {BEAM_SUPPLIED_CHECK_SCHEMA_VERSION}"
            )
        if self.reinforcement.clear_cover_mm >= self.section.D_mm:
            raise ValueError(
                "reinforcement.clear_cover_mm must be less than section.D_mm"
            )
        for group_name, group in (
            ("tension", self.reinforcement.tension),
            ("compression_or_hanger", self.reinforcement.compression_or_hanger),
        ):
            if group.diameter_mm not in self.selection.permitted_diameters_mm:
                raise ValueError(
                    f"reinforcement.{group_name}.diameter_mm must be permitted by selection"
                )
            if len(group.bars_per_layer) > self.selection.maximum_layers:
                raise ValueError(
                    f"reinforcement.{group_name} exceeds selection.maximum_layers"
                )
            if max(group.bars_per_layer) > self.selection.maximum_bars_per_layer:
                raise ValueError(
                    f"reinforcement.{group_name} exceeds selection.maximum_bars_per_layer"
                )
        basis = self.section.effective_depth_basis
        if isinstance(basis, EffectiveDepthBasisRequestV1):
            if len(self.reinforcement.tension.bars_per_layer) != 1:
                raise ValueError(
                    "bar-diameter effective_depth_basis supports one tension layer; "
                    "use centroid_cover_mm for multilayer reinforcement"
                )
            if not (
                math.isclose(basis.clear_cover_mm, self.reinforcement.clear_cover_mm)
                and math.isclose(
                    basis.stirrup_diameter_mm,
                    self.reinforcement.stirrup_diameter_mm,
                )
                and math.isclose(
                    basis.tension_bar_diameter_mm,
                    self.reinforcement.tension.diameter_mm,
                )
            ):
                raise ValueError(
                    "effective_depth_basis must match the supplied cover, stirrup, "
                    "and tension-bar diameter"
                )
        return self
