# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Stable orchestration entry points for the bounded IS 456 slab workflows."""

from __future__ import annotations

from dataclasses import dataclass, replace

from structural_lib.codes.is456.slab.built_in_coefficients import (
    resolve_builtin_one_way_continuous_coefficients,
    resolve_builtin_two_way_panel_coefficients,
)
from structural_lib.codes.is456.slab.coefficients import (
    OneWayContinuousCoefficientSet,
    TwoWayPanelCoefficientSet,
)
from structural_lib.codes.is456.slab.detailing import (
    ProvidedSlabBars,
    SlabReinforcementRegionResult,
    check_slab_reinforcement_region,
)
from structural_lib.codes.is456.slab.external_coefficients import (
    record_external_two_way_slab_coefficients,
)
from structural_lib.codes.is456.slab.models import (
    SlabCapacityFailureResult,
    SolidRectangularSlabGeometry,
)
from structural_lib.codes.is456.slab.one_way import (
    OneWaySlabFlexureInput,
    OneWaySlabFlexureResult,
    OneWaySlabFlexureStatus,
    design_simply_supported_one_way_slab_flexure,
)
from structural_lib.codes.is456.slab.one_way_continuous import (
    ContinuousOneWaySlabInput,
    ContinuousOneWaySlabResult,
    design_continuous_one_way_slab_flexure,
)
from structural_lib.codes.is456.slab.one_way_detailing import (
    OneWaySlabDetailingInput,
    OneWaySlabDetailingResult,
    check_simply_supported_one_way_slab_detailing,
)
from structural_lib.codes.is456.slab.serviceability import (
    SlabServiceabilityInput,
    SlabServiceabilityResult,
    check_slab_span_depth_serviceability,
)
from structural_lib.codes.is456.slab.shear import (
    SlabShearInput,
    SlabShearResult,
    check_solid_slab_one_way_shear,
)
from structural_lib.codes.is456.slab.topology import (
    CornerLiftCondition,
    OrientedSlabPanelGeometry,
    SlabEdgeContinuity,
    SlabSupportTopology,
    SlabSupportTopologyKind,
)
from structural_lib.codes.is456.slab.two_way import (
    SUPPORTED_INTERIOR_SOLID_RECTANGULAR_FOUR_EDGES_CONTINUOUS_SUPPORT_CASE_ID,
    TwoWaySlabFlexureInput,
    TwoWaySlabFlexureResult,
    design_supported_interior_two_way_slab_flexure,
)
from structural_lib.codes.is456.slab.two_way_complete import (
    TwoWayPanelDesignInput,
    TwoWayPanelDesignResult,
    design_two_way_slab_panel,
)

__all__ = [
    "CompleteOneWaySlabDesignResult",
    "ContinuousOneWaySlabDesignResult",
    "OneWaySlabDesignResult",
    "TwoWaySlabPanelWorkflowResult",
    "design_complete_one_way_slab_is456",
    "design_continuous_one_way_slab_builtin_is456",
    "design_continuous_one_way_slab_is456",
    "design_one_way_slab_is456",
    "design_two_way_slab_panel_is456",
    "design_two_way_slab_panel_builtin_is456",
    "design_two_way_slab_is456",
]


_COMPLETE_ONE_WAY_FLEXURE_LIMITATIONS = (
    "COMPOSED WORKFLOW: minimum reinforcement, provided-bar detailing, reviewed "
    "span/depth serviceability, and ordinary one-way shear are evaluated in this result.",
    "HOLD: load combinations, support moments, continuity, cantilevers, and load "
    "patterns are not inferred.",
)
_COMPLETE_ONE_WAY_DETAILING_LIMITATIONS = (
    "COMPOSED WORKFLOW: provided-bar detailing, reviewed span/depth serviceability, "
    "and ordinary one-way shear are evaluated in this result.",
    "HOLD: direct deflection and crack-width calculations are not implemented.",
    "HOLD: automatic slab shear reinforcement is not designed.",
    "REVIEW LIMITATION: qualified structural-engineering review remains required.",
)
_SINGLE_ACTION_LOAD_BOUNDARY = (
    "not_generated_single_caller_supplied_factored_udl_or_coefficient_basis"
)


@dataclass(frozen=True)
class OneWaySlabDesignResult:
    """Flexure and provided-bar checks for the supported one-way slab strip."""

    flexure: OneWaySlabFlexureResult | SlabCapacityFailureResult
    detailing: OneWaySlabDetailingResult | None
    load_envelope_status: str = _SINGLE_ACTION_LOAD_BOUNDARY

    @property
    def is_detailing_adequate(self) -> bool:
        """Return the bounded provided-bar detailing outcome."""
        return self.detailing is not None and self.detailing.is_detailing_adequate


@dataclass(frozen=True)
class CompleteOneWaySlabDesignResult:
    """Compatibility one-way design plus explicit shear and serviceability."""

    reinforcement: OneWaySlabDesignResult
    shear: SlabShearResult | None
    serviceability: SlabServiceabilityResult | None
    punching_shear_disposition: str
    complete_engineering_design_approved: bool = False
    load_envelope_status: str = _SINGLE_ACTION_LOAD_BOUNDARY


@dataclass(frozen=True)
class ContinuousOneWaySlabDesignResult:
    """Continuous actions, supplied-bar checks, shear and serviceability."""

    flexure: ContinuousOneWaySlabResult
    positive_reinforcement: SlabReinforcementRegionResult
    negative_reinforcement: SlabReinforcementRegionResult
    distribution_reinforcement: SlabReinforcementRegionResult
    shear: SlabShearResult
    serviceability: SlabServiceabilityResult
    punching_shear_disposition: str
    complete_engineering_design_approved: bool = False
    load_envelope_status: str = _SINGLE_ACTION_LOAD_BOUNDARY


@dataclass(frozen=True)
class TwoWaySlabPanelWorkflowResult:
    """Bounded common two-way panel design with explicit serviceability carrier."""

    panel: TwoWayPanelDesignResult | SlabCapacityFailureResult
    serviceability: SlabServiceabilityResult | None
    complete_engineering_design_approved: bool = False
    load_envelope_status: str = _SINGLE_ACTION_LOAD_BOUNDARY


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
    if isinstance(flexure, SlabCapacityFailureResult):
        return OneWaySlabDesignResult(flexure=flexure, detailing=None)
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


def design_complete_one_way_slab_is456(
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
    reviewed_base_span_depth_limit: float,
    reviewed_aggregate_modification_factor: float,
    serviceability_limit_source_reference: str,
    serviceability_limit_source_is_approved: bool,
    qualified_serviceability_acceptance_reference: str,
    qualified_serviceability_acceptance_acknowledged: bool,
    strip_width_mm: float = 1000.0,
) -> CompleteOneWaySlabDesignResult:
    """Complete the bounded simply supported strip checks without inference."""
    reinforcement = design_one_way_slab_is456(
        short_effective_span_mm=short_effective_span_mm,
        long_effective_span_mm=long_effective_span_mm,
        thickness_mm=thickness_mm,
        d_mm=d_mm,
        factored_area_load_kn_per_m2=factored_area_load_kn_per_m2,
        fck_n_per_mm2=fck_n_per_mm2,
        fy_n_per_mm2=fy_n_per_mm2,
        main_bar_diameter_mm=main_bar_diameter_mm,
        main_bar_spacing_mm=main_bar_spacing_mm,
        distribution_bar_diameter_mm=distribution_bar_diameter_mm,
        distribution_bar_spacing_mm=distribution_bar_spacing_mm,
        strip_width_mm=strip_width_mm,
    )
    if isinstance(reinforcement.flexure, SlabCapacityFailureResult):
        return CompleteOneWaySlabDesignResult(
            reinforcement=reinforcement,
            shear=None,
            serviceability=None,
            punching_shear_disposition=(
                "not_evaluated_due_to_flexural_capacity_failure"
            ),
        )
    if reinforcement.detailing is None:  # pragma: no cover - guarded invariant
        raise RuntimeError("accepted slab flexure must include detailing")
    factored_shear_kn = (
        reinforcement.flexure.line_load_kn_per_m
        * (reinforcement.flexure.effective_short_span_mm / 1000.0)
        / 2.0
    )
    shear = check_solid_slab_one_way_shear(
        SlabShearInput(
            factored_shear_kn=factored_shear_kn,
            strip_width_mm=strip_width_mm,
            effective_depth_mm=d_mm,
            overall_depth_mm=thickness_mm,
            fck_n_per_mm2=fck_n_per_mm2,
            tension_reinforcement_mm2=(
                reinforcement.detailing.main_reinforcement_provided_mm2
            ),
            uniformly_distributed_load_only=True,
            beam_or_wall_supported=True,
        )
    )
    serviceability = check_slab_span_depth_serviceability(
        SlabServiceabilityInput(
            effective_span_mm=short_effective_span_mm,
            effective_depth_mm=d_mm,
            reviewed_base_span_depth_limit=reviewed_base_span_depth_limit,
            reviewed_aggregate_modification_factor=(
                reviewed_aggregate_modification_factor
            ),
            limit_source_reference=serviceability_limit_source_reference,
            limit_source_is_approved=serviceability_limit_source_is_approved,
            qualified_acceptance_reference=(
                qualified_serviceability_acceptance_reference
            ),
            qualified_acceptance_acknowledged=(
                qualified_serviceability_acceptance_acknowledged
            ),
        )
    )
    completed_flexure = replace(
        reinforcement.flexure,
        status=OneWaySlabFlexureStatus.COMPLETE_WORKFLOW_CHECKS_COMPOSED,
        limitations=_COMPLETE_ONE_WAY_FLEXURE_LIMITATIONS,
    )
    completed_detailing_input = replace(
        reinforcement.detailing.input,
        flexure_result=completed_flexure,
    )
    completed_detailing = replace(
        reinforcement.detailing,
        input=completed_detailing_input,
        limitations=_COMPLETE_ONE_WAY_DETAILING_LIMITATIONS,
    )
    reinforcement = replace(
        reinforcement,
        flexure=completed_flexure,
        detailing=completed_detailing,
    )
    return CompleteOneWaySlabDesignResult(
        reinforcement=reinforcement,
        shear=shear,
        serviceability=serviceability,
        punching_shear_disposition=shear.punching_shear_disposition,
    )


def design_continuous_one_way_slab_is456(
    *,
    short_effective_span_mm: float,
    long_effective_span_mm: float,
    thickness_mm: float,
    d_mm: float,
    factored_area_load_kn_per_m2: float,
    fck_n_per_mm2: float,
    fy_n_per_mm2: float,
    positive_moment_coefficient: float,
    negative_moment_coefficient: float,
    shear_coefficient: float,
    coefficient_source_reference: str,
    coefficient_source_is_approved: bool,
    qualified_coefficient_acceptance_reference: str,
    qualified_coefficient_acceptance_acknowledged: bool,
    number_of_spans: int,
    maximum_span_variation_percent: float,
    uniform_cross_section_acknowledged: bool,
    substantially_uniform_load_acknowledged: bool,
    redistribution_applied: bool,
    positive_bar_diameter_mm: float,
    positive_bar_spacing_mm: float,
    negative_bar_diameter_mm: float,
    negative_bar_spacing_mm: float,
    distribution_bar_diameter_mm: float,
    distribution_bar_spacing_mm: float,
    reviewed_base_span_depth_limit: float,
    reviewed_aggregate_modification_factor: float,
    serviceability_limit_source_reference: str,
    serviceability_limit_source_is_approved: bool,
    qualified_serviceability_acceptance_reference: str,
    qualified_serviceability_acceptance_acknowledged: bool,
    strip_width_mm: float = 1000.0,
) -> ContinuousOneWaySlabDesignResult:
    """Run the bounded continuous one-way coefficient workflow end to end."""
    geometry = SolidRectangularSlabGeometry(
        short_effective_span_mm,
        long_effective_span_mm,
        thickness_mm,
        strip_width_mm,
    )
    coefficients = OneWayContinuousCoefficientSet(
        positive_midspan=positive_moment_coefficient,
        negative_support=negative_moment_coefficient,
        shear_support=shear_coefficient,
        source_reference=coefficient_source_reference,
        source_is_approved=coefficient_source_is_approved,
        qualified_acceptance_reference=(qualified_coefficient_acceptance_reference),
        qualified_acceptance_acknowledged=(
            qualified_coefficient_acceptance_acknowledged
        ),
    )
    flexure = design_continuous_one_way_slab_flexure(
        ContinuousOneWaySlabInput(
            geometry=geometry,
            d_mm=d_mm,
            factored_area_load_kn_per_m2=factored_area_load_kn_per_m2,
            fck_n_per_mm2=fck_n_per_mm2,
            fy_n_per_mm2=fy_n_per_mm2,
            coefficients=coefficients,
            number_of_spans=number_of_spans,
            maximum_span_variation_percent=maximum_span_variation_percent,
            uniform_cross_section_acknowledged=uniform_cross_section_acknowledged,
            substantially_uniform_load_acknowledged=(
                substantially_uniform_load_acknowledged
            ),
            redistribution_applied=redistribution_applied,
        )
    )
    positive_bars = ProvidedSlabBars(positive_bar_diameter_mm, positive_bar_spacing_mm)
    negative_bars = ProvidedSlabBars(negative_bar_diameter_mm, negative_bar_spacing_mm)
    distribution_bars = ProvidedSlabBars(
        distribution_bar_diameter_mm, distribution_bar_spacing_mm
    )
    positive = check_slab_reinforcement_region(
        region_id="continuous_positive_midspan",
        required_for_moment_mm2_per_m=(flexure.positive_midspan.ast_required_mm2_per_m),
        bars=positive_bars,
        overall_depth_mm=thickness_mm,
        effective_depth_mm=d_mm,
        fy_n_per_mm2=fy_n_per_mm2,
    )
    negative = check_slab_reinforcement_region(
        region_id="continuous_negative_support",
        required_for_moment_mm2_per_m=(flexure.negative_support.ast_required_mm2_per_m),
        bars=negative_bars,
        overall_depth_mm=thickness_mm,
        effective_depth_mm=d_mm,
        fy_n_per_mm2=fy_n_per_mm2,
    )
    distribution = check_slab_reinforcement_region(
        region_id="continuous_distribution",
        required_for_moment_mm2_per_m=0.0,
        bars=distribution_bars,
        distribution_only=True,
        overall_depth_mm=thickness_mm,
        effective_depth_mm=d_mm,
        fy_n_per_mm2=fy_n_per_mm2,
    )
    shear = check_solid_slab_one_way_shear(
        SlabShearInput(
            factored_shear_kn=flexure.factored_shear_kn_per_m,
            strip_width_mm=strip_width_mm,
            effective_depth_mm=d_mm,
            overall_depth_mm=thickness_mm,
            fck_n_per_mm2=fck_n_per_mm2,
            tension_reinforcement_mm2=min(
                positive.provided_mm2_per_m, negative.provided_mm2_per_m
            ),
            uniformly_distributed_load_only=True,
            beam_or_wall_supported=True,
        )
    )
    serviceability = check_slab_span_depth_serviceability(
        SlabServiceabilityInput(
            effective_span_mm=short_effective_span_mm,
            effective_depth_mm=d_mm,
            reviewed_base_span_depth_limit=reviewed_base_span_depth_limit,
            reviewed_aggregate_modification_factor=(
                reviewed_aggregate_modification_factor
            ),
            limit_source_reference=serviceability_limit_source_reference,
            limit_source_is_approved=serviceability_limit_source_is_approved,
            qualified_acceptance_reference=(
                qualified_serviceability_acceptance_reference
            ),
            qualified_acceptance_acknowledged=(
                qualified_serviceability_acceptance_acknowledged
            ),
        )
    )
    return ContinuousOneWaySlabDesignResult(
        flexure=flexure,
        positive_reinforcement=positive,
        negative_reinforcement=negative,
        distribution_reinforcement=distribution,
        shear=shear,
        serviceability=serviceability,
        punching_shear_disposition=shear.punching_shear_disposition,
    )


def design_continuous_one_way_slab_builtin_is456(
    *,
    short_effective_span_mm: float,
    long_effective_span_mm: float,
    thickness_mm: float,
    d_mm: float,
    factored_dead_and_fixed_imposed_load_kn_per_m2: float,
    factored_nonfixed_imposed_load_kn_per_m2: float,
    positive_location: str,
    negative_location: str,
    shear_location: str,
    fck_n_per_mm2: float,
    fy_n_per_mm2: float,
    number_of_spans: int,
    maximum_span_variation_percent: float,
    uniform_cross_section_acknowledged: bool,
    substantially_uniform_load_acknowledged: bool,
    redistribution_applied: bool,
    positive_bar_diameter_mm: float,
    positive_bar_spacing_mm: float,
    negative_bar_diameter_mm: float,
    negative_bar_spacing_mm: float,
    distribution_bar_diameter_mm: float,
    distribution_bar_spacing_mm: float,
    reviewed_base_span_depth_limit: float,
    reviewed_aggregate_modification_factor: float,
    serviceability_limit_source_reference: str,
    serviceability_limit_source_is_approved: bool,
    qualified_serviceability_acceptance_reference: str,
    qualified_serviceability_acceptance_acknowledged: bool,
    strip_width_mm: float = 1000.0,
) -> ContinuousOneWaySlabDesignResult:
    """Run continuous one-way design with built-in Table 12/13 coefficients."""
    coefficients = resolve_builtin_one_way_continuous_coefficients(
        factored_dead_and_fixed_imposed_load_kn_per_m2=(
            factored_dead_and_fixed_imposed_load_kn_per_m2
        ),
        factored_nonfixed_imposed_load_kn_per_m2=(
            factored_nonfixed_imposed_load_kn_per_m2
        ),
        positive_location=positive_location,
        negative_location=negative_location,
        shear_location=shear_location,
    )
    total_load = (
        factored_dead_and_fixed_imposed_load_kn_per_m2
        + factored_nonfixed_imposed_load_kn_per_m2
    )
    result = design_continuous_one_way_slab_is456(
        factored_area_load_kn_per_m2=total_load,
        positive_moment_coefficient=coefficients.positive_midspan,
        negative_moment_coefficient=coefficients.negative_support,
        shear_coefficient=coefficients.shear_support,
        coefficient_source_reference=coefficients.source_reference,
        coefficient_source_is_approved=True,
        qualified_coefficient_acceptance_reference=(
            coefficients.qualified_acceptance_reference
        ),
        qualified_coefficient_acceptance_acknowledged=True,
        short_effective_span_mm=short_effective_span_mm,
        long_effective_span_mm=long_effective_span_mm,
        thickness_mm=thickness_mm,
        d_mm=d_mm,
        fck_n_per_mm2=fck_n_per_mm2,
        fy_n_per_mm2=fy_n_per_mm2,
        number_of_spans=number_of_spans,
        maximum_span_variation_percent=maximum_span_variation_percent,
        uniform_cross_section_acknowledged=uniform_cross_section_acknowledged,
        substantially_uniform_load_acknowledged=(
            substantially_uniform_load_acknowledged
        ),
        redistribution_applied=redistribution_applied,
        positive_bar_diameter_mm=positive_bar_diameter_mm,
        positive_bar_spacing_mm=positive_bar_spacing_mm,
        negative_bar_diameter_mm=negative_bar_diameter_mm,
        negative_bar_spacing_mm=negative_bar_spacing_mm,
        distribution_bar_diameter_mm=distribution_bar_diameter_mm,
        distribution_bar_spacing_mm=distribution_bar_spacing_mm,
        reviewed_base_span_depth_limit=reviewed_base_span_depth_limit,
        reviewed_aggregate_modification_factor=(reviewed_aggregate_modification_factor),
        serviceability_limit_source_reference=serviceability_limit_source_reference,
        serviceability_limit_source_is_approved=(
            serviceability_limit_source_is_approved
        ),
        qualified_serviceability_acceptance_reference=(
            qualified_serviceability_acceptance_reference
        ),
        qualified_serviceability_acceptance_acknowledged=(
            qualified_serviceability_acceptance_acknowledged
        ),
        strip_width_mm=strip_width_mm,
    )
    built_in_input = replace(result.flexure.input, coefficients=coefficients)
    built_in_flexure = replace(
        result.flexure,
        input=built_in_input,
        coefficient_correctness_verified_by_library=True,
        source_refs=(
            "IS 456:2000 Cl. 22.5, Table 12 and Table 13",
            coefficients.source_reference,
            coefficients.qualified_acceptance_reference,
        ),
    )
    return replace(result, flexure=built_in_flexure)


def design_two_way_slab_panel_is456(
    *,
    x_effective_span_mm: float,
    y_effective_span_mm: float,
    thickness_mm: float,
    x_min_edge: str,
    x_max_edge: str,
    y_min_edge: str,
    y_max_edge: str,
    corner_lift_condition: str,
    support_topology_kind: str,
    alpha_x_negative: float,
    alpha_x_positive: float,
    alpha_y_negative: float,
    alpha_y_positive: float,
    coefficient_source_reference: str,
    coefficient_source_is_approved: bool,
    qualified_coefficient_acceptance_reference: str,
    qualified_coefficient_acceptance_acknowledged: bool,
    factored_area_load_kn_per_m2: float,
    d_x_mm: float,
    d_y_mm: float,
    fck_n_per_mm2: float,
    fy_n_per_mm2: float,
    x_positive_bar_diameter_mm: float,
    x_positive_bar_spacing_mm: float,
    x_negative_bar_diameter_mm: float,
    x_negative_bar_spacing_mm: float,
    y_positive_bar_diameter_mm: float,
    y_positive_bar_spacing_mm: float,
    y_negative_bar_diameter_mm: float,
    y_negative_bar_spacing_mm: float,
    edge_strip_bar_diameter_mm: float,
    edge_strip_bar_spacing_mm: float,
    torsion_bar_diameter_mm: float,
    torsion_bar_spacing_mm: float,
    reviewed_base_span_depth_limit: float,
    reviewed_aggregate_modification_factor: float,
    serviceability_limit_source_reference: str,
    serviceability_limit_source_is_approved: bool,
    qualified_serviceability_acceptance_reference: str,
    qualified_serviceability_acceptance_acknowledged: bool,
) -> TwoWaySlabPanelWorkflowResult:
    """Run a common beam/wall-supported two-way panel with external coefficients."""
    geometry = OrientedSlabPanelGeometry(
        x_effective_span_mm=x_effective_span_mm,
        y_effective_span_mm=y_effective_span_mm,
        thickness_mm=thickness_mm,
    )
    topology = SlabSupportTopology(
        x_min=SlabEdgeContinuity(x_min_edge),
        x_max=SlabEdgeContinuity(x_max_edge),
        y_min=SlabEdgeContinuity(y_min_edge),
        y_max=SlabEdgeContinuity(y_max_edge),
        corner_lift_condition=CornerLiftCondition(corner_lift_condition),
    )
    coefficients = TwoWayPanelCoefficientSet(
        support_topology_kind=SlabSupportTopologyKind(support_topology_kind),
        alpha_x_negative=alpha_x_negative,
        alpha_x_positive=alpha_x_positive,
        alpha_y_negative=alpha_y_negative,
        alpha_y_positive=alpha_y_positive,
        source_reference=coefficient_source_reference,
        source_is_approved=coefficient_source_is_approved,
        qualified_acceptance_reference=(qualified_coefficient_acceptance_reference),
        qualified_acceptance_acknowledged=(
            qualified_coefficient_acceptance_acknowledged
        ),
    )
    panel = design_two_way_slab_panel(
        TwoWayPanelDesignInput(
            geometry=geometry,
            support_topology=topology,
            coefficients=coefficients,
            factored_area_load_kn_per_m2=factored_area_load_kn_per_m2,
            d_x_mm=d_x_mm,
            d_y_mm=d_y_mm,
            fck_n_per_mm2=fck_n_per_mm2,
            fy_n_per_mm2=fy_n_per_mm2,
            x_positive_bars=ProvidedSlabBars(
                x_positive_bar_diameter_mm, x_positive_bar_spacing_mm
            ),
            x_negative_bars=ProvidedSlabBars(
                x_negative_bar_diameter_mm, x_negative_bar_spacing_mm
            ),
            y_positive_bars=ProvidedSlabBars(
                y_positive_bar_diameter_mm, y_positive_bar_spacing_mm
            ),
            y_negative_bars=ProvidedSlabBars(
                y_negative_bar_diameter_mm, y_negative_bar_spacing_mm
            ),
            edge_strip_bars=ProvidedSlabBars(
                edge_strip_bar_diameter_mm, edge_strip_bar_spacing_mm
            ),
            torsion_bars_each_layer=ProvidedSlabBars(
                torsion_bar_diameter_mm, torsion_bar_spacing_mm
            ),
        )
    )
    if isinstance(panel, SlabCapacityFailureResult):
        return TwoWaySlabPanelWorkflowResult(panel=panel, serviceability=None)
    serviceability = check_slab_span_depth_serviceability(
        SlabServiceabilityInput(
            effective_span_mm=x_effective_span_mm,
            effective_depth_mm=min(d_x_mm, d_y_mm),
            reviewed_base_span_depth_limit=reviewed_base_span_depth_limit,
            reviewed_aggregate_modification_factor=(
                reviewed_aggregate_modification_factor
            ),
            limit_source_reference=serviceability_limit_source_reference,
            limit_source_is_approved=serviceability_limit_source_is_approved,
            qualified_acceptance_reference=(
                qualified_serviceability_acceptance_reference
            ),
            qualified_acceptance_acknowledged=(
                qualified_serviceability_acceptance_acknowledged
            ),
        )
    )
    panel = replace(
        panel,
        serviceability_dependency=(
            "evaluated_by_composed_workflow_with_reviewed_limit_carrier"
        ),
    )
    return TwoWaySlabPanelWorkflowResult(panel=panel, serviceability=serviceability)


def design_two_way_slab_panel_builtin_is456(
    *,
    x_effective_span_mm: float,
    y_effective_span_mm: float,
    thickness_mm: float,
    x_min_edge: str,
    x_max_edge: str,
    y_min_edge: str,
    y_max_edge: str,
    corner_lift_condition: str,
    factored_area_load_kn_per_m2: float,
    d_x_mm: float,
    d_y_mm: float,
    fck_n_per_mm2: float,
    fy_n_per_mm2: float,
    x_positive_bar_diameter_mm: float,
    x_positive_bar_spacing_mm: float,
    x_negative_bar_diameter_mm: float,
    x_negative_bar_spacing_mm: float,
    y_positive_bar_diameter_mm: float,
    y_positive_bar_spacing_mm: float,
    y_negative_bar_diameter_mm: float,
    y_negative_bar_spacing_mm: float,
    edge_strip_bar_diameter_mm: float,
    edge_strip_bar_spacing_mm: float,
    torsion_bar_diameter_mm: float,
    torsion_bar_spacing_mm: float,
    reviewed_base_span_depth_limit: float,
    reviewed_aggregate_modification_factor: float,
    serviceability_limit_source_reference: str,
    serviceability_limit_source_is_approved: bool,
    qualified_serviceability_acceptance_reference: str,
    qualified_serviceability_acceptance_acknowledged: bool,
) -> TwoWaySlabPanelWorkflowResult:
    """Run a two-way panel with built-in Table 26/27 interpolation."""
    geometry = OrientedSlabPanelGeometry(
        x_effective_span_mm=x_effective_span_mm,
        y_effective_span_mm=y_effective_span_mm,
        thickness_mm=thickness_mm,
    )
    topology = SlabSupportTopology(
        x_min=SlabEdgeContinuity(x_min_edge),
        x_max=SlabEdgeContinuity(x_max_edge),
        y_min=SlabEdgeContinuity(y_min_edge),
        y_max=SlabEdgeContinuity(y_max_edge),
        corner_lift_condition=CornerLiftCondition(corner_lift_condition),
    )
    coefficients = resolve_builtin_two_way_panel_coefficients(
        geometry=geometry, topology=topology
    )
    result = design_two_way_slab_panel_is456(
        x_effective_span_mm=x_effective_span_mm,
        y_effective_span_mm=y_effective_span_mm,
        thickness_mm=thickness_mm,
        x_min_edge=x_min_edge,
        x_max_edge=x_max_edge,
        y_min_edge=y_min_edge,
        y_max_edge=y_max_edge,
        corner_lift_condition=corner_lift_condition,
        support_topology_kind=topology.kind.value,
        alpha_x_negative=coefficients.alpha_x_negative,
        alpha_x_positive=coefficients.alpha_x_positive,
        alpha_y_negative=coefficients.alpha_y_negative,
        alpha_y_positive=coefficients.alpha_y_positive,
        coefficient_source_reference=coefficients.source_reference,
        coefficient_source_is_approved=True,
        qualified_coefficient_acceptance_reference=(
            coefficients.qualified_acceptance_reference
        ),
        qualified_coefficient_acceptance_acknowledged=True,
        factored_area_load_kn_per_m2=factored_area_load_kn_per_m2,
        d_x_mm=d_x_mm,
        d_y_mm=d_y_mm,
        fck_n_per_mm2=fck_n_per_mm2,
        fy_n_per_mm2=fy_n_per_mm2,
        x_positive_bar_diameter_mm=x_positive_bar_diameter_mm,
        x_positive_bar_spacing_mm=x_positive_bar_spacing_mm,
        x_negative_bar_diameter_mm=x_negative_bar_diameter_mm,
        x_negative_bar_spacing_mm=x_negative_bar_spacing_mm,
        y_positive_bar_diameter_mm=y_positive_bar_diameter_mm,
        y_positive_bar_spacing_mm=y_positive_bar_spacing_mm,
        y_negative_bar_diameter_mm=y_negative_bar_diameter_mm,
        y_negative_bar_spacing_mm=y_negative_bar_spacing_mm,
        edge_strip_bar_diameter_mm=edge_strip_bar_diameter_mm,
        edge_strip_bar_spacing_mm=edge_strip_bar_spacing_mm,
        torsion_bar_diameter_mm=torsion_bar_diameter_mm,
        torsion_bar_spacing_mm=torsion_bar_spacing_mm,
        reviewed_base_span_depth_limit=reviewed_base_span_depth_limit,
        reviewed_aggregate_modification_factor=(reviewed_aggregate_modification_factor),
        serviceability_limit_source_reference=serviceability_limit_source_reference,
        serviceability_limit_source_is_approved=(
            serviceability_limit_source_is_approved
        ),
        qualified_serviceability_acceptance_reference=(
            qualified_serviceability_acceptance_reference
        ),
        qualified_serviceability_acceptance_acknowledged=(
            qualified_serviceability_acceptance_acknowledged
        ),
    )
    if isinstance(result.panel, SlabCapacityFailureResult):
        return result
    built_in_input = replace(result.panel.input, coefficients=coefficients)
    built_in_panel = replace(
        result.panel,
        input=built_in_input,
        coefficient_correctness_verified_by_library=True,
    )
    return replace(result, panel=built_in_panel)


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
) -> TwoWaySlabFlexureResult | SlabCapacityFailureResult:
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
