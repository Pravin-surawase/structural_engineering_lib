"""Inputs for the finite-age simply supported one-way slab strip."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field

from structural_lib.services.canonical_family import FamilyIdentityV1
from structural_lib.services.contracts.common import StrictPublicModel

Positive = Annotated[float, Field(gt=0)]
Nonnegative = Annotated[float, Field(ge=0)]
Reference = Annotated[str, Field(min_length=1, max_length=240)]
Edge = Literal["simple", "free", "continuous", "fixed"]


class SlabServiceEdgesV1(StrictPublicModel):
    x_min: Edge
    x_max: Edge
    y_min: Edge
    y_max: Edge


class SlabServiceMainBarV1(StrictPublicModel):
    bar_id: Reference
    x_from_left_mm: Positive
    y_from_top_mm: Positive
    diameter_mm: Positive


class SlabServiceDistributionV1(StrictPublicModel):
    pitch_mm: Positive
    y_from_top_mm: Positive
    diameter_mm: Positive


class SlabServiceSectionV1(StrictPublicModel):
    """Actual main-bar axes and the upper, orthogonal distribution row."""

    strip_width_mm: Literal[1000]
    thickness_mm: Positive
    nominal_cover_mm: Positive
    fck_nmm2: float = Field(ge=20, le=55)
    fy_nmm2: Literal[250, 415, 500]
    maximum_aggregate_mm: Positive
    main_pitch_mm: Positive
    main_bars: tuple[SlabServiceMainBarV1, ...] = Field(min_length=1, strict=False)
    distribution: SlabServiceDistributionV1


class SlabServiceActionRowV1(StrictPublicModel):
    """Caller-supplied gravity UDL and concurrent unfactored strip actions."""

    combination_id: Reference
    action_row_id: Reference
    analysis_revision: Reference
    reinforcement_revision: Reference
    uniform_area_load_kn_per_m2: Nonnegative
    midspan_moment_knm: Nonnegative
    support_shear_kn: Nonnegative


class SlabServiceLoadsV1(StrictPublicModel):
    total: SlabServiceActionRowV1
    sustained: SlabServiceActionRowV1


class SlabServiceAgeV1(StrictPublicModel):
    age_days: Positive
    creep_coefficient: Nonnegative
    shrinkage_strain: Nonnegative


class SlabServiceHistoryV1(StrictPublicModel):
    """Prescribed age effects for one permanent load and a later transient."""

    loading_age_days: Positive
    finishes: SlabServiceAgeV1
    assessment: SlabServiceAgeV1
    finish_added_load_kn_per_m2: Nonnegative
    relative_humidity_percent: float = Field(gt=0, le=100)
    notional_size_mm: Positive
    axial_restraint: Literal["free_shortening", "restrained"]
    shrinkage_basis: Literal["uniform_through_depth", "nonuniform_through_depth"]
    source_reference: Reference


class SlabDirectServiceInputV1(StrictPublicModel):
    """One regular, periodic, uniaxial interior strip under gravity UDL."""

    schema_version: Literal["is456-slab-direct-service-input/v1"] = (
        "is456-slab-direct-service-input/v1"
    )
    identity: FamilyIdentityV1
    analysis_revision: Reference
    reinforcement_revision: Reference
    effective_span_mm: Positive
    transverse_panel_span_mm: Positive
    support_edges: SlabServiceEdgesV1 | None = None
    section: SlabServiceSectionV1
    service_loads: SlabServiceLoadsV1 | None = None
    history: SlabServiceHistoryV1 | None = None
    exposure: Literal["mild"]
    crack_width_limit_mm: float = Field(gt=0, le=0.3)
    elastic_witness_load_kn_per_m2: Positive | None = None
    source_reference: Reference
