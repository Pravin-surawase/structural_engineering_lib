# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Complete bounded two-way panel arithmetic using reviewed external coefficients."""

from __future__ import annotations

import math
from dataclasses import dataclass

from structural_lib.codes.is456 import materials
from structural_lib.codes.is456.slab._flexure import (
    calculate_ast_from_rectangular_stress_block,
)
from structural_lib.codes.is456.slab.coefficients import TwoWayPanelCoefficientSet
from structural_lib.codes.is456.slab.detailing import (
    ProvidedSlabBars,
    SlabReinforcementRegionResult,
    check_slab_reinforcement_region,
)
from structural_lib.codes.is456.slab.models import SlabContractError
from structural_lib.codes.is456.slab.shear import (
    SlabShearInput,
    SlabShearResult,
    check_solid_slab_one_way_shear,
)
from structural_lib.codes.is456.slab.topology import (
    CornerTorsionClass,
    OrientedSlabPanelGeometry,
    SlabCorner,
    SlabSupportTopology,
)
from structural_lib.codes.is456.traceability import clause

__all__ = [
    "TwoWayCornerTorsionResult",
    "TwoWayMomentRegionResult",
    "TwoWayPanelDesignInput",
    "TwoWayPanelDesignResult",
    "TwoWayStripDistribution",
    "design_two_way_slab_panel",
]


@dataclass(frozen=True)
class TwoWayPanelDesignInput:
    geometry: OrientedSlabPanelGeometry
    support_topology: SlabSupportTopology
    coefficients: TwoWayPanelCoefficientSet
    factored_area_load_kn_per_m2: float
    d_x_mm: float
    d_y_mm: float
    fck_n_per_mm2: float
    fy_n_per_mm2: float
    x_positive_bars: ProvidedSlabBars
    x_negative_bars: ProvidedSlabBars
    y_positive_bars: ProvidedSlabBars
    y_negative_bars: ProvidedSlabBars
    edge_strip_bars: ProvidedSlabBars
    torsion_bars_each_layer: ProvidedSlabBars

    def __post_init__(self) -> None:
        if not isinstance(self.geometry, OrientedSlabPanelGeometry):
            raise SlabContractError("geometry must be OrientedSlabPanelGeometry")
        if self.geometry.span_ratio_ly_lx > 2.0:
            raise SlabContractError("two-way panel requires Ly/Lx no greater than 2")
        if not isinstance(self.support_topology, SlabSupportTopology):
            raise SlabContractError("support_topology must be SlabSupportTopology")
        if not isinstance(self.coefficients, TwoWayPanelCoefficientSet):
            raise SlabContractError("coefficients must be TwoWayPanelCoefficientSet")
        if self.coefficients.support_topology_kind is not self.support_topology.kind:
            raise SlabContractError(
                "coefficient support_topology_kind must match the physical edge topology"
            )
        for name in (
            "factored_area_load_kn_per_m2",
            "d_x_mm",
            "d_y_mm",
            "fck_n_per_mm2",
            "fy_n_per_mm2",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise SlabContractError(f"{name} must be a real value")
            normalized = float(value)
            if not math.isfinite(normalized) or normalized <= 0.0:
                raise SlabContractError(f"{name} must be finite and positive")
            object.__setattr__(self, name, normalized)
        if (
            self.d_x_mm >= self.geometry.thickness_mm
            or self.d_y_mm >= self.geometry.thickness_mm
        ):
            raise SlabContractError(
                "directional effective depths must be less than thickness"
            )
        if not 20.0 <= self.fck_n_per_mm2 <= 40.0:
            raise SlabContractError(
                "complete two-way route supports fck_n_per_mm2 from 20 to 40 because shear is included"
            )
        if not any(abs(self.fy_n_per_mm2 - grade) < 0.5 for grade in (250, 415, 500)):
            raise SlabContractError("fy_n_per_mm2 must be 250, 415, or 500")
        for name in (
            "x_positive_bars",
            "x_negative_bars",
            "y_positive_bars",
            "y_negative_bars",
            "edge_strip_bars",
            "torsion_bars_each_layer",
        ):
            if not isinstance(getattr(self, name), ProvidedSlabBars):
                raise SlabContractError(f"{name} must be ProvidedSlabBars")


@dataclass(frozen=True)
class TwoWayMomentRegionResult:
    region_id: str
    coefficient: float
    factored_moment_knm_per_m: float
    ast_required_mm2_per_m: float
    neutral_axis_depth_mm: float
    reinforcement: SlabReinforcementRegionResult


@dataclass(frozen=True)
class TwoWayStripDistribution:
    x_moment_middle_strip_width_mm: float
    x_moment_edge_strip_width_each_mm: float
    y_moment_middle_strip_width_mm: float
    y_moment_edge_strip_width_each_mm: float
    moment_redistribution_applied: bool


@dataclass(frozen=True)
class TwoWayCornerTorsionResult:
    corner: SlabCorner
    torsion_class: CornerTorsionClass
    zone_extent_from_each_edge_mm: float
    required_each_of_four_layers_mm2_per_m: float
    provided_each_layer_mm2_per_m: float
    is_adequate: bool


@dataclass(frozen=True)
class TwoWayPanelDesignResult:
    input: TwoWayPanelDesignInput
    x_negative: TwoWayMomentRegionResult
    x_positive: TwoWayMomentRegionResult
    y_negative: TwoWayMomentRegionResult
    y_positive: TwoWayMomentRegionResult
    strip_distribution: TwoWayStripDistribution
    edge_strip_reinforcement: SlabReinforcementRegionResult
    corner_torsion: tuple[TwoWayCornerTorsionResult, ...]
    shear: SlabShearResult
    coefficient_correctness_verified_by_library: bool
    complete_engineering_design_approved: bool
    serviceability_dependency: str
    punching_shear_disposition: str
    held_scope: tuple[str, ...]

    @property
    def provided_reinforcement_is_adequate(self) -> bool:
        return (
            all(
                region.reinforcement.is_adequate
                for region in (
                    self.x_negative,
                    self.x_positive,
                    self.y_negative,
                    self.y_positive,
                )
            )
            and self.edge_strip_reinforcement.is_adequate
            and all(corner.is_adequate for corner in self.corner_torsion)
        )


def _moment_region(
    *,
    region_id: str,
    coefficient: float,
    load: float,
    short_span_m: float,
    d_mm: float,
    fck: float,
    fy: float,
    thickness: float,
    bars: ProvidedSlabBars,
) -> TwoWayMomentRegionResult:
    moment = coefficient * load * short_span_m**2
    xu_max_over_d = materials.get_xu_max_d(fy)
    limiting = (
        0.36
        * xu_max_over_d
        * (1.0 - 0.42 * xu_max_over_d)
        * fck
        * 1000.0
        * d_mm**2
        / 1_000_000.0
    )
    if moment > limiting:
        raise SlabContractError(f"{region_id} exceeds singly reinforced capacity")
    if moment == 0.0:
        ast, xu = 0.0, 0.0
    else:
        ast, xu = calculate_ast_from_rectangular_stress_block(
            b_mm=1000.0,
            d_mm=d_mm,
            factored_moment_knm=moment,
            fck_n_per_mm2=fck,
            fy_n_per_mm2=fy,
        )
    reinforcement = check_slab_reinforcement_region(
        region_id=region_id,
        required_for_moment_mm2_per_m=ast,
        bars=bars,
        overall_depth_mm=thickness,
        effective_depth_mm=d_mm,
        fy_n_per_mm2=fy,
    )
    return TwoWayMomentRegionResult(
        region_id=region_id,
        coefficient=coefficient,
        factored_moment_knm_per_m=moment,
        ast_required_mm2_per_m=ast,
        neutral_axis_depth_mm=xu,
        reinforcement=reinforcement,
    )


@clause("24.4", "40.2")
def design_two_way_slab_panel(
    design_input: TwoWayPanelDesignInput,
) -> TwoWayPanelDesignResult:
    """Design common physical topologies without bundling coefficient tables."""
    if not isinstance(design_input, TwoWayPanelDesignInput):
        raise SlabContractError("design_input must be TwoWayPanelDesignInput")
    coefficients = design_input.coefficients
    common = {
        "load": design_input.factored_area_load_kn_per_m2,
        "short_span_m": design_input.geometry.x_effective_span_mm / 1000.0,
        "fck": design_input.fck_n_per_mm2,
        "fy": design_input.fy_n_per_mm2,
        "thickness": design_input.geometry.thickness_mm,
    }
    x_negative = _moment_region(
        region_id="x_negative_continuous_edge",
        coefficient=coefficients.alpha_x_negative,
        d_mm=design_input.d_x_mm,
        bars=design_input.x_negative_bars,
        **common,
    )
    x_positive = _moment_region(
        region_id="x_positive_middle_strip",
        coefficient=coefficients.alpha_x_positive,
        d_mm=design_input.d_x_mm,
        bars=design_input.x_positive_bars,
        **common,
    )
    y_negative = _moment_region(
        region_id="y_negative_continuous_edge",
        coefficient=coefficients.alpha_y_negative,
        d_mm=design_input.d_y_mm,
        bars=design_input.y_negative_bars,
        **common,
    )
    y_positive = _moment_region(
        region_id="y_positive_middle_strip",
        coefficient=coefficients.alpha_y_positive,
        d_mm=design_input.d_y_mm,
        bars=design_input.y_positive_bars,
        **common,
    )
    edge_strip = check_slab_reinforcement_region(
        region_id="edge_strips_minimum_reinforcement",
        required_for_moment_mm2_per_m=0.0,
        bars=design_input.edge_strip_bars,
        overall_depth_mm=design_input.geometry.thickness_mm,
        effective_depth_mm=min(design_input.d_x_mm, design_input.d_y_mm),
        fy_n_per_mm2=design_input.fy_n_per_mm2,
        distribution_only=True,
    )
    max_positive_ast = max(
        x_positive.ast_required_mm2_per_m, y_positive.ast_required_mm2_per_m
    )
    torsion_zone = design_input.geometry.x_effective_span_mm / 5.0
    corner_results = []
    factor_by_class = {
        CornerTorsionClass.FULL: 0.75,
        CornerTorsionClass.HALF: 0.375,
        CornerTorsionClass.NONE: 0.0,
        CornerTorsionClass.NOT_APPLICABLE_FREE_TO_LIFT: 0.0,
    }
    for corner in SlabCorner:
        torsion_class = design_input.support_topology.corner_torsion_class(corner)
        required = factor_by_class[torsion_class] * max_positive_ast
        corner_results.append(
            TwoWayCornerTorsionResult(
                corner=corner,
                torsion_class=torsion_class,
                zone_extent_from_each_edge_mm=torsion_zone,
                required_each_of_four_layers_mm2_per_m=required,
                provided_each_layer_mm2_per_m=(
                    design_input.torsion_bars_each_layer.area_mm2_per_m
                ),
                is_adequate=(
                    required == 0.0
                    or design_input.torsion_bars_each_layer.area_mm2_per_m >= required
                ),
            )
        )
    shear = check_solid_slab_one_way_shear(
        SlabShearInput(
            factored_shear_kn=(
                design_input.factored_area_load_kn_per_m2
                * (design_input.geometry.x_effective_span_mm / 1000.0)
                / 2.0
            ),
            strip_width_mm=1000.0,
            effective_depth_mm=min(design_input.d_x_mm, design_input.d_y_mm),
            overall_depth_mm=design_input.geometry.thickness_mm,
            fck_n_per_mm2=design_input.fck_n_per_mm2,
            tension_reinforcement_mm2=min(
                design_input.x_positive_bars.area_mm2_per_m,
                design_input.y_positive_bars.area_mm2_per_m,
            ),
            uniformly_distributed_load_only=True,
            beam_or_wall_supported=True,
        )
    )
    return TwoWayPanelDesignResult(
        input=design_input,
        x_negative=x_negative,
        x_positive=x_positive,
        y_negative=y_negative,
        y_positive=y_positive,
        strip_distribution=TwoWayStripDistribution(
            x_moment_middle_strip_width_mm=0.75
            * design_input.geometry.y_effective_span_mm,
            x_moment_edge_strip_width_each_mm=0.125
            * design_input.geometry.y_effective_span_mm,
            y_moment_middle_strip_width_mm=0.75
            * design_input.geometry.x_effective_span_mm,
            y_moment_edge_strip_width_each_mm=0.125
            * design_input.geometry.x_effective_span_mm,
            moment_redistribution_applied=False,
        ),
        edge_strip_reinforcement=edge_strip,
        corner_torsion=tuple(corner_results),
        shear=shear,
        coefficient_correctness_verified_by_library=coefficients.verified_by_library,
        complete_engineering_design_approved=False,
        serviceability_dependency=(
            "Run check_slab_span_depth_serviceability with an approved limit carrier."
        ),
        punching_shear_disposition=(
            "not_applicable_to_supported_beam_or_wall_supported_udl_panel"
        ),
        held_scope=(
            "Built-in coefficient lookup and interpolation are held.",
            "Direct deflection and crack-width calculations are held.",
            "Openings, concentrated loads, irregular geometry, and FEM are held.",
            "Flat slabs, drops, column strips, and punching shear require separate approval.",
        ),
    )
