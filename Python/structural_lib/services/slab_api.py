# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Stable orchestration entry points for the bounded IS 456 slab workflows."""

from __future__ import annotations

from dataclasses import dataclass

from structural_lib.codes.is456.slab.external_coefficients import (
    record_external_two_way_slab_coefficients,
)
from structural_lib.codes.is456.slab.models import SolidRectangularSlabGeometry
from structural_lib.codes.is456.slab.one_way import (
    OneWaySlabFlexureInput,
    OneWaySlabFlexureResult,
    design_simply_supported_one_way_slab_flexure,
)
from structural_lib.codes.is456.slab.one_way_detailing import (
    OneWaySlabDetailingInput,
    OneWaySlabDetailingResult,
    check_simply_supported_one_way_slab_detailing,
)
from structural_lib.codes.is456.slab.two_way import (
    SUPPORTED_INTERIOR_SOLID_RECTANGULAR_FOUR_EDGES_CONTINUOUS_SUPPORT_CASE_ID,
    TwoWaySlabFlexureInput,
    TwoWaySlabFlexureResult,
    design_supported_interior_two_way_slab_flexure,
)

__all__ = [
    "OneWaySlabDesignResult",
    "design_one_way_slab_is456",
    "design_two_way_slab_is456",
]


@dataclass(frozen=True)
class OneWaySlabDesignResult:
    """Flexure and provided-bar checks for the supported one-way slab strip."""

    flexure: OneWaySlabFlexureResult
    detailing: OneWaySlabDetailingResult

    @property
    def is_detailing_adequate(self) -> bool:
        """Return the bounded provided-bar detailing outcome."""
        return self.detailing.is_detailing_adequate


def design_one_way_slab_is456(
    *,
    short_effective_span_mm: float,
    long_effective_span_mm: float,
    thickness_mm: float,
    d_mm: float,
    factored_area_load_kn_per_m2: float,
    fck_n_per_mm2: float,
    fy_n_per_mm2: float,
    main_bar_diameter_mm: float,
    main_bar_spacing_mm: float,
    distribution_bar_diameter_mm: float,
    distribution_bar_spacing_mm: float,
    strip_width_mm: float = 1000.0,
) -> OneWaySlabDesignResult:
    """Design the bounded simply supported one-way slab strip.

    Inputs use mm, kN/m2 and N/mm2. This route checks flexure and supplied
    reinforcement only. A span/depth ratio above the basic limit is returned
    as a qualified-review requirement, not silently accepted.
    """
    geometry = SolidRectangularSlabGeometry(
        span_a_effective_mm=short_effective_span_mm,
        span_b_effective_mm=long_effective_span_mm,
        thickness_mm=thickness_mm,
        strip_width_mm=strip_width_mm,
    )
    flexure = design_simply_supported_one_way_slab_flexure(
        OneWaySlabFlexureInput(
            geometry=geometry,
            d_mm=d_mm,
            factored_area_load_kn_per_m2=factored_area_load_kn_per_m2,
            fck_n_per_mm2=fck_n_per_mm2,
            fy_n_per_mm2=fy_n_per_mm2,
        )
    )
    detailing = check_simply_supported_one_way_slab_detailing(
        OneWaySlabDetailingInput(
            flexure_result=flexure,
            main_bar_diameter_mm=main_bar_diameter_mm,
            main_bar_spacing_mm=main_bar_spacing_mm,
            distribution_bar_diameter_mm=distribution_bar_diameter_mm,
            distribution_bar_spacing_mm=distribution_bar_spacing_mm,
        )
    )
    return OneWaySlabDesignResult(flexure=flexure, detailing=detailing)


def design_two_way_slab_is456(
    *,
    short_effective_span_mm: float,
    long_effective_span_mm: float,
    thickness_mm: float,
    alpha_x: float,
    alpha_y: float,
    coefficient_source_reference: str,
    coefficient_source_is_approved: bool,
    qualified_coefficient_acceptance_reference: str,
    qualified_coefficient_acceptance_acknowledged: bool,
    is_interior_solid_rectangular_panel: bool,
    all_four_edges_continuous: bool,
    factored_area_load_kn_per_m2: float,
    d_x_mm: float,
    d_y_mm: float,
    fck_n_per_mm2: float,
    fy_n_per_mm2: float,
    strip_width_mm: float = 1000.0,
) -> TwoWaySlabFlexureResult:
    """Compute flexure for the sole externally accepted-coefficient case.

    Coefficients are caller supplied and must carry explicit source approval
    plus a separate qualified acceptance reference. The caller must also
    declare the exact interior, four-edge-continuous configuration; the core
    requires both declarations to be literal ``True``. This route does not
    look up coefficients or perform a complete two-way slab design. The result
    explicitly records outstanding reinforcement detailing, serviceability,
    shear/punching, load-patterning, and other-panel-case dependencies.
    """
    geometry = SolidRectangularSlabGeometry(
        span_a_effective_mm=short_effective_span_mm,
        span_b_effective_mm=long_effective_span_mm,
        thickness_mm=thickness_mm,
        strip_width_mm=strip_width_mm,
    )
    coefficient_record = record_external_two_way_slab_coefficients(
        geometry=geometry,
        support_case_id=(
            SUPPORTED_INTERIOR_SOLID_RECTANGULAR_FOUR_EDGES_CONTINUOUS_SUPPORT_CASE_ID
        ),
        alpha_x=alpha_x,
        alpha_y=alpha_y,
        coefficient_source_reference=coefficient_source_reference,
        coefficient_source_is_approved=coefficient_source_is_approved,
    )
    return design_supported_interior_two_way_slab_flexure(
        TwoWaySlabFlexureInput(
            coefficient_record=coefficient_record,
            qualified_coefficient_acceptance_reference=(
                qualified_coefficient_acceptance_reference
            ),
            qualified_coefficient_acceptance_acknowledged=(
                qualified_coefficient_acceptance_acknowledged
            ),
            is_interior_solid_rectangular_panel=is_interior_solid_rectangular_panel,
            all_four_edges_continuous=all_four_edges_continuous,
            factored_area_load_kn_per_m2=factored_area_load_kn_per_m2,
            d_x_mm=d_x_mm,
            d_y_mm=d_y_mm,
            fck_n_per_mm2=fck_n_per_mm2,
            fy_n_per_mm2=fy_n_per_mm2,
        )
    )
