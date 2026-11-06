"""Versioned contracts for the prescribed rectangular column section response."""

from __future__ import annotations

from math import fsum, isfinite, pi
from typing import Literal, Self

from pydantic import Field, field_validator, model_validator

from structural_lib.services.contracts.common import StrictPublicModel


class ColumnSectionLayerV1(StrictPublicModel):
    """One diameter group on a depth line parallel to the centroidal axis."""

    depth_from_top_mm: float = Field(gt=0)
    count: int = Field(gt=0, le=2000)
    diameter_mm: float = Field(ge=1, le=2000)

    @property
    def area_mm2(self) -> float:
        return self.count * pi * self.diameter_mm**2 / 4


class ColumnSectionInputV1(StrictPublicModel):
    """Response of a solid rectangular section at a prescribed neutral axis."""

    schema_version: Literal["column-layered-section-input/v1"] = (
        "column-layered-section-input/v1"
    )
    b_mm: float = Field(gt=0, le=2000)
    D_mm: float = Field(gt=0, le=2000)
    xu_mm: float = Field(gt=0)
    fck_nmm2: float = Field(ge=15, le=80)
    fy_nmm2: float = Field(ge=250, le=550)
    layers: tuple[ColumnSectionLayerV1, ...] = Field(min_length=1)

    @field_validator("layers", mode="before")
    @classmethod
    def accept_json_array(cls, value: object) -> object:
        """Keep the validated layer sequence immutable."""
        return tuple(value) if isinstance(value, list) else value

    @model_validator(mode="after")
    def validate_section(self) -> Self:
        if not isfinite(self.D_mm / self.xu_mm):
            raise ValueError("xu_mm must give a finite section depth ratio")
        widths_by_depth: dict[float, list[float]] = {}
        for index, layer in enumerate(self.layers):
            depth = layer.depth_from_top_mm
            radius = layer.diameter_mm / 2
            if not radius <= depth <= self.D_mm - radius:
                raise ValueError(
                    f"layers[{index}] bar diameter extends beyond a depth face"
                )
            widths_by_depth.setdefault(depth, []).append(
                layer.count * layer.diameter_mm
            )
        for depth, widths in widths_by_depth.items():
            if fsum(widths) > self.b_mm:
                raise ValueError(
                    f"combined bar diameters at depth {depth:g} mm exceed the section width"
                )
        if fsum(layer.area_mm2 for layer in self.layers) >= self.b_mm * self.D_mm:
            raise ValueError("Total bar area must be below the gross section area")
        return self


class ColumnSectionLayerResponseV1(StrictPublicModel):
    """Strain and net contribution of one diameter group after concrete displacement."""

    layer: ColumnSectionLayerV1
    area_mm2: float
    strain: float
    steel_stress_nmm2: float
    displaced_concrete_stress_nmm2: float
    net_axial_kn: float
    centroid_moment_knm: float


class ColumnSectionResponseV1(StrictPublicModel):
    """Raw calculated section response, with explicit moment datum and status."""

    schema_version: Literal["column-layered-section-response/v1"] = (
        "column-layered-section-response/v1"
    )
    calculation_status: Literal["COMPLETED"] = "COMPLETED"
    member_acceptance: Literal["NOT_EVALUATED"] = "NOT_EVALUATED"
    detailing_acceptance: Literal["NOT_EVALUATED"] = "NOT_EVALUATED"
    compression_face: Literal["top"] = "top"
    bending_axis: Literal["centroidal_parallel_to_width"] = (
        "centroidal_parallel_to_width"
    )
    request: ColumnSectionInputV1
    method_revision_id: str
    source_references: tuple[str, ...]
    top_strain: float
    far_face_strain: float
    gross_concrete_axial_kn: float
    gross_concrete_centroid_moment_knm: float
    axial_kn: float
    centroid_moment_knm: float
    layers: tuple[ColumnSectionLayerResponseV1, ...]

    @field_validator("source_references", "layers", mode="before")
    @classmethod
    def accept_json_arrays(cls, value: object) -> object:
        """Restore immutable sequences from serialized JSON arrays."""
        return tuple(value) if isinstance(value, list) else value
