"""Requests for the bounded footing and slab public-library workflows."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, StrictInt


class FootingLoadTransferRequest(BaseModel):
    """Explicit inputs for the bounded concentric isolated-footing transfer check."""

    Pu_kN: float = Field(gt=0)
    loaded_area_A2_mm2: float = Field(gt=0)
    effective_supporting_area_A1_mm2: float = Field(gt=0)
    effective_supporting_area_basis: Literal["largest_frustum_1v_2h"]
    effective_supporting_area_is_approved: Literal[True]
    supporting_concrete_fck_nmm2: float = Field(gt=0)
    supported_concrete_fck_nmm2: float = Field(gt=0)
    steel_fy_nmm2: float = Field(gt=0)
    dowel_count: StrictInt = Field(gt=0)
    dowel_diameter_mm: float = Field(gt=0)
    column_longitudinal_bar_diameter_mm: float = Field(gt=0)
    available_dowel_development_length_into_footing_mm: float = Field(gt=0)
    available_dowel_development_length_into_supported_member_mm: float = Field(gt=0)
    dowel_bar_type: Literal["deformed", "plain"] = "deformed"


class OneWaySlabDesignRequest(BaseModel):
    """Explicit inputs for the supported simply supported one-way slab strip."""

    short_effective_span_mm: float = Field(gt=0)
    long_effective_span_mm: float = Field(gt=0)
    thickness_mm: float = Field(gt=0)
    d_mm: float = Field(gt=0)
    factored_area_load_kn_per_m2: float = Field(gt=0)
    fck_n_per_mm2: float = Field(ge=20, le=80)
    fy_n_per_mm2: Literal[250.0, 415.0, 500.0]
    main_bar_diameter_mm: float = Field(gt=0)
    main_bar_spacing_mm: float = Field(gt=0)
    distribution_bar_diameter_mm: float = Field(gt=0)
    distribution_bar_spacing_mm: float = Field(gt=0)
    strip_width_mm: float = Field(default=1000.0, gt=0)
