"""Section capacities and signed equilibrium for the centred interior profile."""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from structural_lib.codes.is456 import tables
from structural_lib.codes.is456.beam.shear import shear_reinforcement_component_kn
from structural_lib.codes.is456.column.member_detailing import ordinary_column_shear
from structural_lib.codes.is456.common.constants import (
    STRESS_BLOCK_DEPTH,
    STRESS_BLOCK_FACTOR,
)
from structural_lib.codes.is456.section_materials import (
    ELASTIC_MODULUS_N_PER_MM2,
    ULTIMATE_CONCRETE_STRAIN,
    section_concrete_stress,
    section_steel_stress,
)
from structural_lib.codes.is13920.beam import (
    calculate_confinement_spacing,
    check_geometry,
    get_max_tension_steel_percentage,
    get_min_tension_steel_percentage,
)
from structural_lib.codes.is13920.joint import (
    ColumnCapacityBasis,
    JointTopology,
    PrincipalPlane,
    ShakingDirection,
    check_scwb,
)


class JointStrengthDomainError(ValueError):
    """Supplied actions or sections leave the bounded equilibrium domain."""


def _axis_for_force(residual: Callable[[float], float], depth_mm: float) -> float:
    lower, upper = 1e-6, depth_mm
    if not lower < upper or residual(lower) >= 0 or residual(upper) <= 0:
        raise JointStrengthDomainError(
            "No partial-compression equilibrium exists for the supplied section and load."
        )
    for _ in range(90):
        neutral = (upper + lower) / 2
        if residual(neutral) < 0:
            lower = neutral
        else:
            upper = neutral
    return (upper + lower) / 2


def _area(diameter: float, count: int = 1) -> float:
    return count * math.pi * diameter**2 / 4


@dataclass(frozen=True)
class _Section:
    width_mm: float
    depth_mm: float
    fck_mpa: float
    fy_mpa: float

    def concrete_force(self, axis_mm: float) -> float:
        return STRESS_BLOCK_FACTOR * self.fck_mpa * self.width_mm * axis_mm

    def steel_strain(self, layer_mm: float, axis_mm: float) -> float:
        return ULTIMATE_CONCRETE_STRAIN * (1 - layer_mm / axis_mm)

    def section_response(
        self, layers: tuple[tuple[float, int, float], ...], axial_kn: float = 0.0
    ) -> dict[str, Any]:
        steel_areas = tuple(_area(diameter, count) for _, count, diameter in layers)

        def stresses(layer_mm: float, axis_mm: float) -> tuple[float, float, float]:
            strain = self.steel_strain(layer_mm, axis_mm)
            return (
                strain,
                section_steel_stress(strain, self.fy_mpa),
                section_concrete_stress(strain, self.fck_mpa),
            )

        def residual(axis_mm: float) -> float:
            net_forces = (
                area * (steel - concrete)
                for (position, _, _), area in zip(layers, steel_areas, strict=True)
                for _, steel, concrete in (stresses(position, axis_mm),)
            )
            return self.concrete_force(axis_mm) + sum(net_forces) - axial_kn * 1000

        axis = _axis_for_force(residual, self.depth_mm)
        concrete = self.concrete_force(axis)
        centroid = self.depth_mm / 2
        moment = concrete * (centroid - STRESS_BLOCK_DEPTH * axis)
        responses = []
        for index, ((position, count, diameter), area) in enumerate(
            zip(layers, steel_areas, strict=True), start=1
        ):
            strain, stress, displaced = stresses(position, axis)
            net = area * (stress - displaced)
            moment += net * (centroid - position)
            responses.append(
                {
                    "layer": index,
                    "distance_from_compression_face_mm": position,
                    "count": count,
                    "diameter_mm": diameter,
                    "area_mm2": area,
                    "strain": strain,
                    "steel_stress_mpa": stress,
                    "displaced_concrete_stress_mpa": displaced,
                    "force_n": net,
                }
            )
        max_tension_strain = max(-item["strain"] for item in responses)
        design_yield = self.fy_mpa / 1.15
        strain_limit = 0.002 + design_yield / ELASTIC_MODULUS_N_PER_MM2
        return {
            "neutral_axis_mm": axis,
            "moment_knm": abs(moment) / 1e6,
            "axial_kn": axial_kn,
            "concrete_compression_force_n": concrete,
            "equilibrium_residual_n": residual(axis),
            "tension_yielded": any(
                item["steel_stress_mpa"] <= -design_yield + 1e-9 for item in responses
            ),
            "tension_ductile": max_tension_strain >= strain_limit,
            "yield_strain_threshold": strain_limit,
            "layers": responses,
        }

    def capacity_mechanism(
        self, bar_depth_mm: float, steel_area_mm2: float
    ) -> dict[str, float]:
        """Balance the joint-design tension force with concrete and compression bars."""
        tension = 1.25 * self.fy_mpa * steel_area_mm2

        def steel_force(axis_mm: float) -> float:
            strain = max(0.0, self.steel_strain(bar_depth_mm, axis_mm))
            return steel_area_mm2 * (
                section_steel_stress(strain, self.fy_mpa)
                - section_concrete_stress(strain, self.fck_mpa)
            )

        d_mm = self.depth_mm - bar_depth_mm
        axis = _axis_for_force(
            lambda x: self.concrete_force(x) + steel_force(x) - tension, d_mm
        )
        concrete = self.concrete_force(axis)
        steel = steel_force(axis)
        moment = concrete * (d_mm - STRESS_BLOCK_DEPTH * axis) + steel * (
            d_mm - bar_depth_mm
        )
        return {
            "tension_kn": tension / 1000,
            "concrete_compression_kn": concrete / 1000,
            "net_steel_compression_kn": steel / 1000,
            "neutral_axis_mm": axis,
            "moment_knm": moment / 1e6,
        }


def _beam_reactions(
    loads_kn_m: Mapping[str, float],
    spans_mm: Mapping[str, float],
    moment_knm: float,
    sway_sign: int,
) -> dict[str, float]:
    """Downward joint forces, with opposite hinge increments for the two ends."""
    reactions = {}
    for side, multiplier in (("minus", sway_sign), ("plus", -sway_sign)):
        length_m = spans_mm[side] / 1000
        reactions[side] = (
            0.6 * loads_kn_m[side] * length_m + multiplier * 2 * moment_knm / length_m
        )
    return reactions


def _column_axial(action: Mapping[str, Any]) -> dict[str, float]:
    upper = action["upper_axial_compression_kn"]
    lower = upper + sum(action["beam_on_joint_downward_shear_kn"].values())
    if lower <= 0:
        raise JointStrengthDomainError(
            "The interior profile requires compression at both column ends."
        )
    return {"upper": upper, "lower": lower}


def _direction_strength(
    request: Mapping[str, Any],
    direction: str,
    beam_moment_knm: float,
    mechanism: Mapping[str, float],
    confinement: Mapping[str, Any],
    column_governing: Mapping[str, dict[str, Any]],
) -> dict[str, Any]:
    plane = direction[0]
    positive = direction.endswith("+")
    shaking = ShakingDirection.POSITIVE if positive else ShakingDirection.NEGATIVE
    sign = 1 if positive else -1
    width = request["column_width_mm"]
    depth = request["joint_depth_mm"]
    column_d = width - request["column_bar_edge_mm"]
    tension_steel_percent = (
        100 * _area(request["column_bar_mm"], 3) / (width * column_d)
    )
    column_table19_percent = 0.25 if tension_steel_percent >= 0.25 else 0.15
    beam_d = depth - request["beam_row_depth_from_top_mm"][plane]
    beam_width = request["beam_width_mm"]
    link_fy = request["link_fy_mpa"]
    tolerance = request["tie_station_tolerance_mm"]
    beam_pitch = request["beam_pitch_mm"] + 2 * tolerance
    beam_limit = calculate_confinement_spacing(beam_d, request["beam_bar_mm"])
    first_link = (
        request["beam_first_link_mm"] + request["beam_inner_link_offset_mm"] + tolerance
    )
    beam_vus = shear_reinforcement_component_kn(
        _area(request["beam_link_mm"], 2), link_fy, beam_d, 90, beam_pitch
    )
    beam_crush = (
        tables.get_tc_max_value(request["beam_fck_mpa"]) * beam_width * beam_d / 1000
    )
    beam_capacity = min(beam_vus, beam_crush)
    gravity = request["beam_dead_plus_live_kn_m"][plane]
    spans = request["beam_clear_spans_mm"][plane]
    hinge_moment = 1.4 * beam_moment_knm
    hinge_reactions = _beam_reactions(gravity, spans, hinge_moment, sign)
    mechanism_reactions = _beam_reactions(gravity, spans, mechanism["moment_knm"], sign)

    # Equilibrium of the joint and column portions between the two inflections.
    # The opposing downward reactions contribute moments about the column centre.
    mechanism_arm_mm = sum(request["mechanism_inflection_offsets_mm"].values()) + depth
    reaction_couple = (
        sign
        * (mechanism_reactions["minus"] - mechanism_reactions["plus"])
        * width
        / 2000
    )
    mechanism_column_shear = (
        1000 * (2 * mechanism["moment_knm"] + reaction_couple) / mechanism_arm_mm
    )
    joint_shear = 2 * mechanism["tension_kn"] - mechanism_column_shear
    if min(joint_shear, mechanism_column_shear) <= 0:
        raise JointStrengthDomainError(
            "The supplied inflection offsets do not resolve the declared joint shear mechanism."
        )
    joint_breadth = min(width, beam_width + width / 2)
    joint_area = joint_breadth * width
    joint_stress = 1000 * joint_shear / joint_area
    joint_limit = (1.5 if confinement["confined_faces"] == 4 else 1.0) * math.sqrt(
        request["joint_fck_mpa"]
    )
    top = column_governing["upper"]
    bottom = column_governing["lower"]
    scwb = check_scwb(
        column_top_capacity_knm=top["moment_knm"],
        column_bottom_capacity_knm=bottom["moment_knm"],
        beam_left_capacity_knm=beam_moment_knm,
        beam_right_capacity_knm=beam_moment_knm,
        topology=JointTopology.INTERIOR,
        principal_plane=PrincipalPlane(plane),
        shaking_direction=shaking,
        column_capacity_direction=shaking.opposite(),
        column_top_factored_axial_load_kn=top["axial_kn"],
        column_bottom_factored_axial_load_kn=bottom["axial_kn"],
        column_capacity_basis=ColumnCapacityBasis.FACTORED_AXIAL_LOAD,
        is_roof_joint=False,
        is_flat_slab_system=False,
    )
    rows = []
    for action in request["directions"][direction]:
        axial = _column_axial(action)
        elastic = action["beam_on_joint_downward_shear_kn"]
        beam_shears = {}
        for side, hinge_sign in (("minus", -sign), ("plus", sign)):
            demand = max(abs(elastic[side]), abs(hinge_reactions[side]))
            beam_shears[side] = {
                "signed_near_hinge_moment_knm": hinge_sign * beam_moment_knm,
                "analysis_downward_reaction_kn": elastic[side],
                "capacity_downward_reaction_kn": hinge_reactions[side],
                "demand_kn": demand,
                "steel_capacity_kn": beam_vus,
                "concrete_crushing_cap_kn": beam_crush,
                "accepted_capacity_kn": beam_capacity,
                "pitch_mm": beam_pitch,
                "pitch_limit_mm": beam_limit,
                "utilization": demand / beam_capacity,
                "pass": demand <= beam_capacity
                and beam_pitch <= beam_limit
                and first_link <= 50,
            }
        column_shears = {}
        for end, pu in axial.items():
            hinge = 2000 * hinge_moment / request["column_clear_heights_mm"][end]
            analysis = action["analysis_column_shear_magnitude_kn"]
            demand = max(analysis, hinge)
            shear = ordinary_column_shear(
                width_mm=width,
                d_mm=column_d,
                gross_area_mm2=width**2,
                pu_kn=pu,
                vu_kn=demand,
                fck_nmm2=request["column_fck_mpa"],
                hoop_diameter_mm=request["column_link_mm"],
                hoop_fy_nmm2=link_fy,
                pitch_mm=confinement["end_pitch_mm"],
                table19_steel_percent=column_table19_percent,
            )
            column_shears[end] = {
                "signed_analysis_shear_kn": sign * analysis,
                "signed_capacity_shear_kn": sign * hinge,
                "concurrent_axial_compression_kn": pu,
                "axial_shear_multiplier": shear.axial_factor,
                "table19_steel_percent": column_table19_percent,
                "concrete_capacity_kn": shear.vc_kn,
                "steel_capacity_kn": shear.vus_kn,
                "concrete_crushing_cap_kn": shear.crushing_kn,
                "demand_kn": demand,
                "accepted_capacity_kn": shear.capacity_kn,
                "utilization": shear.utilization,
                "pass": shear.utilization <= 1,
            }
        rows.append(
            {
                "combination_id": action["combination_id"],
                "column_axial_compression_kn": axial,
                "signed_axial_balance_residual_kn": axial["lower"]
                - axial["upper"]
                - sum(elastic.values()),
                "maximum_axial_stress_mpa": 1000 * max(axial.values()) / width**2,
                "beam_capacity_shear": beam_shears,
                "column_capacity_shear": column_shears,
            }
        )

    return {
        "rows": rows,
        "scwb": {
            "beam_capacity_direction": direction,
            "column_capacity_direction": f"{plane}{'-' if positive else '+'}",
            "required_column_capacity_knm": scwb.required_column_capacity_knm,
            "available_column_capacity_knm": scwb.sum_column_capacity_knm,
            "governing_column_combination_ids": {
                "upper": top["combination_id"],
                "lower": bottom["combination_id"],
            },
            "utilization": 1 / scwb.ratio,
            "pass": scwb.is_satisfied,
        },
        "joint_shear": {
            "design_beam_tension_kn_each": mechanism["tension_kn"],
            "mechanism_beam_reactions_kn": mechanism_reactions,
            "reaction_moment_about_centre_knm": reaction_couple,
            "column_inflection_force_couple_arm_mm": mechanism_arm_mm,
            "signed_compatible_column_shear_kn": sign * mechanism_column_shear,
            "signed_joint_shear_kn": sign * joint_shear,
            "effective_breadth_mm": joint_breadth,
            "effective_area_mm2": joint_area,
            "stress_mpa": joint_stress,
            "strength_mpa": joint_limit,
            "utilization": joint_stress / joint_limit,
            "pass": joint_stress <= joint_limit,
        },
    }


def check_interior_joint_strength(
    request: Mapping[str, Any], confinement: Mapping[str, Any]
) -> dict[str, Any]:
    """Calculate direction, combination and section evidence from admitted geometry."""
    width = request["column_width_mm"]
    depth = request["joint_depth_mm"]
    beam_width = request["beam_width_mm"]
    beam_phi = request["beam_bar_mm"]
    fy = request["longitudinal_fy_mpa"]
    beam = _Section(beam_width, depth, request["beam_fck_mpa"], fy)
    beams = {}
    mechanisms = {}
    beam_area = _area(beam_phi, 4)
    spans = request["beam_clear_spans_mm"].values()
    minimum_span = min(value for plane in spans for value in plane.values())
    minimum_steel = get_min_tension_steel_percentage(beam.fck_mpa, fy)
    maximum_steel = get_max_tension_steel_percentage()
    beam_flexure_pass = (
        check_geometry(beam_width, depth)[0] and depth <= minimum_span / 4
    )
    for plane, level in request["beam_row_depth_from_top_mm"].items():
        effective_depth = depth - level
        beams[plane] = beam.section_response(
            ((level, 4, beam_phi), (effective_depth, 4, beam_phi))
        )
        mechanisms[plane] = beam.capacity_mechanism(level, beam_area)
        ratio = 100 * beam_area / (beam_width * effective_depth)
        beam_flexure_pass &= (
            beams[plane]["tension_ductile"] and minimum_steel <= ratio <= maximum_steel
        )

    col_phi = request["column_bar_mm"]
    edge = request["column_bar_edge_mm"]
    column = _Section(width, width, request["column_fck_mpa"], fy)
    layers = ((edge, 3, col_phi), (width / 2, 2, col_phi), (width - edge, 3, col_phi))
    columns: dict[str, list[dict[str, Any]]] = {"upper": [], "lower": []}
    for actions in request["directions"].values():
        for action in actions:
            for end, load in _column_axial(action).items():
                response = column.section_response(layers, load)
                columns[end].append(
                    {"combination_id": action["combination_id"], **response}
                )
    governing_column = {
        end: min(rows, key=lambda row: row["moment_knm"])
        for end, rows in columns.items()
    }
    directions = {
        direction: _direction_strength(
            request,
            direction,
            beams[direction[0]]["moment_knm"],
            mechanisms[direction[0]],
            confinement,
            governing_column,
        )
        for direction in request["directions"]
    }
    return {
        "directions": directions,
        "beam_section_by_plane": beams,
        "column_sections_by_combination_and_end": columns,
        "beam_joint_shear_mechanism_by_plane": mechanisms,
        "beam_flexure_pass": beam_flexure_pass,
    }
