"""Versioned contracts for the prescribed rectangular column section response."""

from __future__ import annotations

from itertools import combinations
from math import fsum, hypot, isfinite, pi
from typing import Annotated, Literal, Self

from pydantic import Field, field_validator, model_validator

from structural_lib.services.canonical_family import FamilyIdentityV1
from structural_lib.services.contracts.column_member import PositionedColumnBarV1
from structural_lib.services.contracts.common import StrictPublicModel
from structural_lib.services.contracts.family_f1 import ColumnMaterialsV1


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


class RectangularInteractionGeometryV1(StrictPublicModel):
    """Solid rectangular geometry in a top-left coordinate system."""

    shape: Literal["rectangular"]
    b_mm: float = Field(ge=100, le=2000)
    D_mm: float = Field(ge=100, le=2000)


class CircularInteractionGeometryV1(StrictPublicModel):
    """Solid circle with bar coordinates relative to its bounding box."""

    shape: Literal["circular"]
    diameter_mm: float = Field(ge=200, le=2000)


class _PositionedColumnSection(StrictPublicModel):
    """Shared physical geometry and bar admission for column section workflows."""

    identity: FamilyIdentityV1
    geometry: Annotated[
        RectangularInteractionGeometryV1 | CircularInteractionGeometryV1,
        Field(discriminator="shape"),
    ]
    bars: tuple[PositionedColumnBarV1, ...] = Field(min_length=4, max_length=32)
    materials: ColumnMaterialsV1

    @field_validator("bars", mode="before")
    @classmethod
    def accept_json_bars(cls, value: object) -> object:
        return tuple(value) if isinstance(value, list) else value

    @model_validator(mode="after")
    def validate_section(self) -> Self:
        geometry = self.geometry
        if len({bar.bar_id for bar in self.bars}) != len(self.bars):
            raise ValueError("Longitudinal bar IDs must be unique.")
        for bar in self.bars:
            radius = bar.diameter_mm / 2
            x, y = bar.x_from_left_mm, bar.y_from_top_mm
            if isinstance(geometry, RectangularInteractionGeometryV1):
                fits = (
                    radius <= x <= geometry.b_mm - radius
                    and radius <= y <= geometry.D_mm - radius
                )
            else:
                centre = geometry.diameter_mm / 2
                fits = hypot(x - centre, y - centre) + radius <= centre
            if not fits:
                raise ValueError(f"Bar {bar.bar_id} extends beyond the section.")
        if any(
            hypot(
                a.x_from_left_mm - b.x_from_left_mm, a.y_from_top_mm - b.y_from_top_mm
            )
            < (a.diameter_mm + b.diameter_mm) / 2
            for a, b in combinations(self.bars, 2)
        ):
            raise ValueError("Section bars must not overlap.")
        return self


class ColumnInteractionInputV1(_PositionedColumnSection):
    """A fixed signed axial-force section slice with explicit physical bars."""

    schema_version: Literal["column-interaction-input/v1"] = (
        "column-interaction-input/v1"
    )
    pu_kn: float = Field(ge=-1e9, le=1e9)
    modular_ratio: float = Field(ge=1, le=30)
    point_count: int = Field(ge=8, le=64, multiple_of=4)


class ColumnServiceActionsV1(StrictPublicModel):
    """Concurrent service actions about the gross section centroid."""

    p_kn: float = Field(ge=-1e6, le=1e6)
    mx_knm: float = Field(ge=-1e6, le=1e6)
    my_knm: float = Field(ge=-1e6, le=1e6)


class ColumnServiceModuliV1(StrictPublicModel):
    """Declared elastic moduli, in N/mm², of concrete and reinforcement."""

    ec_nmm2: float = Field(ge=1000, le=100000)
    es_nmm2: float = Field(ge=100000, le=250000)

    @model_validator(mode="after")
    def validate_modular_ratio(self) -> Self:
        if not 1 < self.es_nmm2 / self.ec_nmm2 <= 30:
            raise ValueError(
                "The steel-to-concrete modular ratio must exceed 1 and be at most 30."
            )
        return self


class ColumnServiceSectionInputV1(_PositionedColumnSection):
    """One solid rectangular or circular section under elastic service actions."""

    schema_version: Literal["column-service-section-input/v1"] = (
        "column-service-section-input/v1"
    )
    actions: ColumnServiceActionsV1
    moduli: ColumnServiceModuliV1
    concrete_linear_limit_nmm2: float = Field(gt=0)

    @model_validator(mode="after")
    def validate_concrete_limit(self) -> Self:
        if self.concrete_linear_limit_nmm2 >= self.materials.fck_nmm2:
            raise ValueError("The declared concrete linear limit must be below fck.")
        return self
