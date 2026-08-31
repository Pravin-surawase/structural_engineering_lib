#!/usr/bin/env python3
"""Replay every F0 facade class, including one invalid vector, from one wheel."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Recipe:
    journey_id: str
    module: str
    loader: str
    operation: str
    payload: dict[str, Any]
    invalid_path: tuple[str, ...]
    invalid_value: Any
    expected_engineering_status: str


def _identity(family_id: str, case_id: str) -> dict[str, str]:
    return {
        "family_id": family_id,
        "case_id": case_id,
        "member_id": case_id,
        "story": "F0",
        "source_reference": "LIB-PRO-013-F0",
    }


def _serviceability() -> dict[str, Any]:
    return {
        "reviewed_base_span_depth_limit": 20.0,
        "reviewed_aggregate_modification_factor": 1.2,
        "serviceability_limit_source_reference": "reviewed-limit:F0",
        "serviceability_limit_source_is_approved": True,
        "qualified_serviceability_acceptance_reference": "review:F0",
        "qualified_serviceability_acceptance_acknowledged": True,
    }


def _flat_direction() -> dict[str, Any]:
    return {
        "column_strip_negative_bars": {"diameter_mm": 12.0, "spacing_mm": 160.0},
        "column_strip_positive_bars": {"diameter_mm": 10.0, "spacing_mm": 200.0},
        "middle_strip_negative_bars": {"diameter_mm": 10.0, "spacing_mm": 200.0},
        "middle_strip_positive_bars": {"diameter_mm": 10.0, "spacing_mm": 200.0},
        "support_top_extension_from_face_mm": 1650.0,
    }


def recipe_specs() -> tuple[Recipe, ...]:
    """Return the frozen 13-class F0 exact-wheel recipe inventory."""

    serviceability = _serviceability()
    recipes = [
        Recipe(
            "is456.beam.design/v1",
            "structural_lib.design.is456.beam",
            "load",
            "design",
            {
                "identity": {"member_id": "B-F0", "story": "F0", "case_id": "B-F0"},
                "section": {
                    "span_mm": 5000.0,
                    "b_mm": 300.0,
                    "D_mm": 500.0,
                    "d_mm": 457.0,
                },
                "materials": {"fck_nmm2": 25.0, "fy_nmm2": 500.0},
                "actions": {"mu_knm": 150.0, "vu_kn": 75.0, "tu_knm": 0.0},
                "calculation_basis": {"d_dash_mm": 43.0, "asv_mm2": 100.53096491487338},
                "source_provenance": "LIB-PRO-013-F0",
            },
            ("actions", "mu_knm"),
            -1.0,
            "PASS",
        ),
        Recipe(
            "is456.torsion.design/v1",
            "structural_lib.design.is456.torsion",
            "load",
            "design",
            {
                "identity": _identity("torsion", "TOR-F0"),
                "geometry": {
                    "corner_bar_centres_b1_mm": 214.0,
                    "corner_bar_centres_d1_mm": 414.0,
                    "d_opposite_mm": 457.0,
                    "b_mm": 300.0,
                    "D_mm": 500.0,
                    "d_mm": 457.0,
                    "clear_cover_mm": 25.0,
                },
                "actions": {"tu_knm": 10.0, "vu_kn": 75.0, "mu_knm": 150.0},
                "materials": {"fck_nmm2": 25.0, "fy_nmm2": 500.0},
                "reinforcement": {
                    "stirrup_diameter_mm": 8.0,
                    "tension_steel_percent": 1.0,
                },
            },
            ("actions", "tu_knm"),
            "10",
            "PASS",
        ),
        Recipe(
            "is456.column.supplied-steel-check/v1",
            "structural_lib.design.is456.column",
            "load",
            "design",
            {
                "identity": _identity("column", "COL-F0"),
                "geometry": {
                    "b_mm": 300.0,
                    "D_mm": 450.0,
                    "unsupported_length_mm": 3000.0,
                    "minimum_eccentricity_length_mm": 3000.0,
                    "end_condition": "FIXED_FIXED",
                    "braced": True,
                },
                "actions": {
                    "pu_kn": 800.0,
                    "mux_knm": 120.0,
                    "muy_knm": 0.0,
                    "m1x_signed_knm": 120.0,
                    "m2x_signed_knm": 120.0,
                    "m1y_signed_knm": 0.0,
                    "m2y_signed_knm": 0.0,
                },
                "materials": {"fck_nmm2": 25.0, "fy_nmm2": 415.0},
                "reinforcement": {
                    "supplied_steel_area_mm2": 2400.0,
                    "reinforcement_centroid_depth_mm": 50.0,
                },
            },
            ("geometry", "braced"),
            1,
            "PASS",
        ),
        Recipe(
            "is456.slab.one-way/v1",
            "structural_lib.design.is456.slab",
            "load_one_way",
            "design_one_way",
            {
                "identity": _identity("solid_slab", "SLAB-OW-F0"),
                "geometry": {
                    "short_effective_span_mm": 3000.0,
                    "long_effective_span_mm": 7500.0,
                    "thickness_mm": 150.0,
                    "effective_depth_mm": 125.0,
                    "strip_width_mm": 1000.0,
                },
                "actions": {"factored_area_load_kn_per_m2": 10.0},
                "materials": {"fck_nmm2": 20.0, "fy_nmm2": 415.0},
                "reinforcement": {
                    "main_bar_diameter_mm": 10.0,
                    "main_bar_spacing_mm": 250.0,
                    "distribution_bar_diameter_mm": 8.0,
                    "distribution_bar_spacing_mm": 250.0,
                },
                "serviceability_evidence": serviceability,
            },
            ("geometry", "effective_depth_mm"),
            "125",
            "PASS",
        ),
        Recipe(
            "is456.slab.continuous-one-way/v1",
            "structural_lib.design.is456.slab",
            "load_continuous_one_way",
            "design_continuous_one_way",
            {
                "identity": _identity("solid_slab", "SLAB-C-F0"),
                "geometry": {
                    "short_effective_span_mm": 3000.0,
                    "long_effective_span_mm": 7500.0,
                    "thickness_mm": 160.0,
                    "effective_depth_mm": 130.0,
                    "strip_width_mm": 1000.0,
                    "number_of_spans": 3,
                    "maximum_span_variation_percent": 0.0,
                    "uniform_cross_section_acknowledged": True,
                },
                "actions": {
                    "factored_dead_and_fixed_imposed_load_kn_per_m2": 7.5,
                    "factored_nonfixed_imposed_load_kn_per_m2": 2.5,
                    "positive_location": "end_span_positive",
                    "negative_location": "next_to_end_support_negative",
                    "shear_location": "end_support",
                    "substantially_uniform_load_acknowledged": True,
                    "redistribution_applied": False,
                },
                "materials": {"fck_nmm2": 20.0, "fy_nmm2": 415.0},
                "reinforcement": {
                    "positive_bar_diameter_mm": 10.0,
                    "positive_bar_spacing_mm": 150.0,
                    "negative_bar_diameter_mm": 10.0,
                    "negative_bar_spacing_mm": 150.0,
                    "distribution_bar_diameter_mm": 8.0,
                    "distribution_bar_spacing_mm": 200.0,
                },
                "serviceability_evidence": serviceability,
            },
            ("actions", "redistribution_applied"),
            True,
            "PASS",
        ),
        Recipe(
            "is456.slab.two-way/v1",
            "structural_lib.design.is456.slab",
            "load_two_way",
            "design_two_way",
            {
                "identity": _identity("solid_slab", "SLAB-TW-F0"),
                "geometry": {
                    "x_effective_span_mm": 4000.0,
                    "y_effective_span_mm": 6000.0,
                    "thickness_mm": 160.0,
                    "d_x_mm": 135.0,
                    "d_y_mm": 125.0,
                    "x_min_edge": "discontinuous",
                    "x_max_edge": "continuous",
                    "y_min_edge": "discontinuous",
                    "y_max_edge": "continuous",
                    "corner_lift_condition": "restrained",
                },
                "actions": {"factored_area_load_kn_per_m2": 15.5},
                "materials": {"fck_nmm2": 20.0, "fy_nmm2": 415.0},
                "reinforcement": {
                    "x_positive_bar_diameter_mm": 10.0,
                    "x_positive_bar_spacing_mm": 200.0,
                    "x_negative_bar_diameter_mm": 10.0,
                    "x_negative_bar_spacing_mm": 200.0,
                    "y_positive_bar_diameter_mm": 8.0,
                    "y_positive_bar_spacing_mm": 200.0,
                    "y_negative_bar_diameter_mm": 8.0,
                    "y_negative_bar_spacing_mm": 200.0,
                    "edge_strip_bar_diameter_mm": 8.0,
                    "edge_strip_bar_spacing_mm": 250.0,
                    "torsion_bar_diameter_mm": 8.0,
                    "torsion_bar_spacing_mm": 200.0,
                },
                "serviceability_evidence": {
                    **serviceability,
                    "reviewed_base_span_depth_limit": 30.0,
                    "reviewed_aggregate_modification_factor": 1.0,
                },
            },
            ("geometry", "corner_lift_condition"),
            "invented",
            "FAIL",
        ),
    ]
    recipes.extend(_f2_recipes())
    recipes.extend(_f3_recipes())
    return tuple(recipes)


def _f2_recipes() -> list[Recipe]:
    direction = _flat_direction()
    return [
        Recipe(
            "is456.wall.braced-axial/v1",
            "structural_lib.design.is456.wall",
            "load",
            "design",
            {
                "identity_source": {
                    "identity": _identity("wall", "WALL-F0"),
                    "bracing_basis_reference": "WALL-F0-BRACING",
                },
                "geometry_topology": {
                    "unsupported_height_mm": 3000.0,
                    "lateral_restraint_spacing_mm": 4000.0,
                    "wall_length_mm": 4000.0,
                    "wall_thickness_mm": 150.0,
                    "rotation_restraint": "restrained_both_ends",
                    "bracing_elements_in_two_directions": True,
                    "lateral_forces_resisted_by_bracing_system": True,
                    "diaphragm_transfer_confirmed": True,
                    "lateral_connection_capacity_confirmed": True,
                },
                "actions": {
                    "factored_axial_load_kn": 2000.0,
                    "supplied_eccentricity_mm": 0.0,
                    "action_basis_reference": "WALL-F0-ACTIONS",
                },
                "materials_reinforcement": {
                    "concrete_grade_nmm2": 20,
                    "vertical_bar_diameter_mm": 8.0,
                    "vertical_bar_spacing_mm": 250.0,
                    "horizontal_bar_diameter_mm": 10.0,
                    "horizontal_bar_spacing_mm": 250.0,
                    "reinforcement_kind": "deformed_415_or_greater",
                },
                "evidence_review": {
                    "reinforcement_basis_reference": "WALL-F0-REINFORCEMENT",
                    "qualified_review_required": True,
                },
            },
            ("geometry_topology", "wall_thickness_mm"),
            "150",
            "PASS",
        ),
        Recipe(
            "is456.staircase.straight-flight/v1",
            "structural_lib.design.is456.staircase",
            "load",
            "design",
            {
                "identity_source": {
                    "identity": _identity("stair", "STAIR-F0"),
                    "load_basis_reference": "NPTEL-M9L20-EX9.1",
                },
                "geometry_topology": {
                    "lower_landing_effective_length_mm": 750.0,
                    "going_mm": 2700.0,
                    "upper_landing_effective_length_mm": 1650.0,
                    "flight_width_mm": 1500.0,
                    "riser_mm": 160.0,
                    "tread_mm": 270.0,
                    "waist_thickness_mm": 250.0,
                    "landing_thickness_mm": 200.0,
                    "support_case": "landings_span_with_flight",
                    "span_direction": "longitudinal",
                    "landings_collinear": True,
                    "has_stringer_beams": False,
                    "is_cast_in_situ_solid": True,
                },
                "actions": {
                    "lower_landing_superimposed_service_load_kn_per_m2": 6.0,
                    "flight_superimposed_service_load_kn_per_m2": 6.0,
                    "upper_landing_superimposed_service_load_kn_per_m2": 6.0,
                    "lower_landing_load_share": 0.5,
                    "upper_landing_load_share": 1.0,
                    "concrete_unit_weight_kn_per_m3": 25.0,
                    "ultimate_load_factor": 1.5,
                },
                "materials_reinforcement": {
                    "effective_depth_mm": 224.0,
                    "fck_nmm2": 20.0,
                    "fy_nmm2": 415.0,
                    "main_bar_diameter_mm": 12.0,
                    "main_bar_spacing_mm": 120.0,
                    "distribution_bar_diameter_mm": 8.0,
                    "distribution_bar_spacing_mm": 160.0,
                },
                "evidence_review": {"qualified_review_required": True},
            },
            ("geometry_topology", "has_stringer_beams"),
            True,
            "HOLD",
        ),
        Recipe(
            "is456.deep-beam.simply-supported/v1",
            "structural_lib.design.is456.deep_beam",
            "load",
            "design",
            {
                "identity_source": {
                    "identity": _identity("deep_beam", "DEEP-F0"),
                    "geometry_basis_reference": "DEEP-F0-GEOMETRY",
                },
                "geometry_topology": {
                    "centre_to_centre_span_mm": 3000.0,
                    "clear_span_mm": 2800.0,
                    "overall_depth_mm": 2000.0,
                    "beam_width_mm": 300.0,
                    "support_type": "simply_supported",
                    "solid_rectangular_section": True,
                    "openings_present": False,
                    "dapped_ends_present": False,
                    "top_loaded": True,
                    "hanging_action_required": False,
                },
                "actions": {
                    "factored_positive_moment_knm": 900.0,
                    "action_basis_reference": "DEEP-F0-ACTIONS",
                },
                "materials_reinforcement": {
                    "concrete_grade_nmm2": 30,
                    "steel_grade_nmm2": 500,
                    "main_bar_count": 4,
                    "main_bar_diameter_mm": 22.0,
                    "furthest_main_bar_from_tension_face_mm": 250.0,
                    "main_bars_continuous_between_supports": True,
                    "main_bars_bundled": False,
                    "main_bar_splices_present": False,
                    "left_support_embedment_mm": 850.0,
                    "right_support_embedment_mm": 850.0,
                    "face_grid_count": 2,
                    "vertical_side_bar_diameter_mm": 10.0,
                    "vertical_side_bar_spacing_mm": 300.0,
                    "horizontal_side_bar_diameter_mm": 10.0,
                    "horizontal_side_bar_spacing_mm": 250.0,
                },
                "evidence_review": {
                    "bearing_nodal_zone_verified": True,
                    "bearing_nodal_zone_reference": "DEEP-F0-BEARING",
                    "reinforcement_basis_reference": "DEEP-F0-REINFORCEMENT",
                    "qualified_review_required": True,
                },
            },
            ("geometry_topology", "openings_present"),
            True,
            "PASS",
        ),
        Recipe(
            "is456.flat-slab.regular-interior/v1",
            "structural_lib.design.is456.flat_slab",
            "load",
            "design",
            {
                "identity_source": {
                    "identity": _identity("flat_slab", "FLAT-F0"),
                    "geometry_basis_reference": "FLAT-F0-GEOMETRY",
                    "material_basis_reference": "FLAT-F0-MATERIAL",
                    "load_basis_reference": "FLAT-F0-LOAD",
                },
                "geometry_topology": {
                    "centre_to_centre_span_x_mm": 6000.0,
                    "centre_to_centre_span_y_mm": 6000.0,
                    "continuous_span_count_x": 3,
                    "continuous_span_count_y": 3,
                    "column_width_x_mm": 500.0,
                    "column_width_y_mm": 500.0,
                    "overall_depth_mm": 300.0,
                    "conservative_effective_depth_mm": 260.0,
                    "analysis_method": "direct_design",
                    "panel_location": "interior",
                    "all_spans_equal_x": True,
                    "all_spans_equal_y": True,
                    "columns_offset_from_grid": False,
                    "solid_slab": True,
                    "drop_present": False,
                    "column_head_present": False,
                    "marginal_beam_or_wall_present": False,
                    "openings_present": False,
                },
                "actions": {
                    "service_dead_load_kn_per_m2": 9.0,
                    "service_live_load_kn_per_m2": 4.0,
                    "factored_uniform_load_kn_per_m2": 19.5,
                    "factored_support_reaction_kn": 702.0,
                    "self_weight_included": True,
                    "identical_full_loading_on_represented_panels": True,
                    "patterned_loading_required": False,
                    "unbalanced_or_lateral_moment_transfer_present": False,
                    "load_combination_approved": True,
                },
                "materials_reinforcement": {
                    "concrete_grade_nmm2": 30,
                    "steel_grade_nmm2": 500,
                    "uncoated_deformed_bars": True,
                    "x": direction,
                    "y": direction,
                },
                "evidence_review": {
                    "straight_bars_only": True,
                    "all_bottom_bars_continuous": True,
                    "splices_present": False,
                    "serviceability_acceptance_acknowledged": True,
                    "centred_concentric_reaction": True,
                    "full_critical_perimeter_available": True,
                    "no_punching_reinforcement_provided": True,
                    "qualified_review_required": True,
                    "detailing_basis_reference": "FLAT-F0-DETAILING",
                    "serviceability_acceptance_reference": "FLAT-F0-SERVICEABILITY",
                    "support_reaction_basis_reference": "FLAT-F0-REACTION",
                    "punching_basis_reference": "FLAT-F0-PUNCHING",
                },
            },
            ("geometry_topology", "openings_present"),
            True,
            "PASS",
        ),
    ]


def _f3_recipes() -> list[Recipe]:
    return [_isolated_recipe(), _combined_recipe(), _strap_recipe()]


def _isolated_recipe() -> Recipe:
    return Recipe(
        "is456.isolated-footing.concentric/v1",
        "structural_lib.design.is456.isolated_footing",
        "load",
        "design",
        {
            "identity_source": {
                "identity": _identity("isolated_footing", "ISO-F0"),
                "service_load_combination_id": "SLS-GRAVITY-01",
                "service_load_basis": "includes_footing_self_weight_and_overburden",
                "service_load_origin": "provided",
                "factored_load_combination_id": "ULS-GRAVITY-01",
                "allowable_soil_pressure_source_reference": "GEO-REPORT-001",
                "allowable_soil_pressure_origin": "verified",
            },
            "geometry_topology": {
                "footing_type": "ISOLATED_SQUARE",
                "column_length_mm": 400.0,
                "column_width_mm": 400.0,
                "minimum_overall_thickness_mm": 500.0,
                "maximum_overall_thickness_mm": 500.0,
                "thickness_increment_mm": 50.0,
                "effective_depth_offset_length_mm": 100.0,
                "effective_depth_offset_width_mm": 100.0,
            },
            "actions": {
                "service_axial_load_kn": 800.0,
                "factored_axial_load_kn": 1200.0,
                "allowable_soil_pressure_kpa": 200.0,
            },
            "materials_reinforcement": {
                "footing_concrete_fck_nmm2": 25.0,
                "column_concrete_fck_nmm2": 25.0,
                "steel_fy_nmm2": 415.0,
                "dowel_count": 4,
                "dowel_diameter_mm": 20.0,
                "column_longitudinal_bar_diameter_mm": 20.0,
                "available_dowel_development_length_into_footing_mm": 1000.0,
                "available_dowel_development_length_into_column_mm": 1000.0,
                "dowel_bar_type": "deformed",
                "nominal_cover_mm": 50.0,
                "nominal_max_aggregate_size_mm": 20.0,
                "lower_bottom_bar_direction": "L",
                "upper_bottom_bar_direction": "B",
                "permitted_bottom_bar_diameters_mm": [12, 16, 20, 25, 32],
                "footing_bottom_bar_type": "deformed",
                "bottom_bar_end_arrangement": "straight",
            },
            "evidence_review": {
                "allowable_soil_pressure_is_externally_approved": True,
                "effective_supporting_area_mm2": 640000.0,
                "effective_supporting_area_basis": "largest_frustum_1v_2h",
                "effective_supporting_area_origin": "provided",
                "effective_supporting_area_is_approved": True,
                "cover_exposure_basis": "approved severe footing schedule",
                "cover_exposure_basis_is_approved": True,
                "qualified_review_required": True,
            },
        },
        ("evidence_review", "allowable_soil_pressure_is_externally_approved"),
        False,
        "PASS",
    )


def _combined_recipe() -> Recipe:
    return Recipe(
        "is456.combined-footing.symmetric/v1",
        "structural_lib.design.is456.combined_footing",
        "load",
        "design",
        {
            "identity_source": {
                "identity": _identity("combined_footing", "COMBINED-F0"),
                "geometry_basis_reference": "COMBINED-F0-GEOMETRY",
                "rigidity_basis_reference": "COMBINED-F0-RIGIDITY",
                "load_basis_reference": "COMBINED-F0-LOAD",
                "bearing_settlement_basis_reference": "COMBINED-F0-BEARING",
                "cancellation_basis_reference": "COMBINED-F0-CANCELLATION",
                "material_basis_reference": "COMBINED-F0-MATERIAL",
            },
            "geometry_topology": {
                "footing_length_mm": 6000.0,
                "footing_width_mm": 2500.0,
                "overall_depth_mm": 850.0,
                "effective_depth_mm": 750.0,
                "column_side_mm": 500.0,
                "left_column_center_x_mm": 1000.0,
                "right_column_center_x_mm": 5000.0,
                "column_count": 2,
                "columns_identical": True,
                "columns_square": True,
                "columns_centered_across_width": True,
                "foundation_on_soil": True,
                "constant_depth": True,
                "openings_present": False,
                "pedestals_present": False,
                "analysis_method": "conventional_rigid",
                "pressure_model": "uniform",
                "rigid_footing_verified": True,
            },
            "actions": {
                "service_axial_load_each_kn": 900.0,
                "factored_axial_load_each_kn": 1350.0,
                "service_uniform_carrier_kn_per_m2": 25.0,
                "factored_uniform_carrier_kn_per_m2": 37.5,
                "allowable_gross_bearing_pressure_kn_per_m2": 150.0,
                "load_combination_approved": True,
                "bearing_and_settlement_approved": True,
                "pressure_uniformity_approved": True,
                "distributed_carrier_cancellation_approved": True,
                "column_moments_present": False,
                "horizontal_actions_present": False,
                "uplift_or_load_reversal_present": False,
            },
            "materials_reinforcement": {
                "footing_concrete_grade_nmm2": 30,
                "column_concrete_grade_nmm2": 30,
                "steel_grade_nmm2": 500,
                "uncoated_deformed_bars": True,
                "top_longitudinal_diameter_mm": 16,
                "top_longitudinal_spacing_mm": 190.0,
                "bottom_longitudinal_diameter_mm": 16,
                "bottom_longitudinal_spacing_mm": 190.0,
                "transverse_diameter_mm": 12,
                "transverse_spacing_mm": 110.0,
                "nominal_cover_mm": 50.0,
                "aggregate_size_mm": 20.0,
                "available_top_longitudinal_anchorage_each_end_mm": 800.0,
                "available_bottom_longitudinal_anchorage_each_end_mm": 800.0,
                "available_transverse_anchorage_each_edge_mm": 800.0,
                "straight_uncoated_deformed_bars": True,
                "effective_depth_basis_approved": True,
                "reinforcement_schedule_approved": True,
                "effective_supporting_area_each_mm2": 250000.0,
                "effective_supporting_area_basis": "largest_frustum_1v_2h",
                "effective_supporting_area_approved": True,
                "dowel_count_each": 4,
                "dowel_diameter_mm": 20,
                "column_longitudinal_bar_diameter_mm": 20,
                "available_dowel_development_into_footing_mm": 800.0,
                "available_dowel_development_into_column_mm": 800.0,
                "uncoated_deformed_dowels": True,
            },
            "evidence_review": {
                "detailing_basis_reference": "COMBINED-F0-DETAILING",
                "transfer_basis_reference": "COMBINED-F0-TRANSFER",
                "qualified_review_required": True,
            },
        },
        ("actions", "column_moments_present"),
        True,
        "PASS",
    )


def _strap_recipe() -> Recipe:
    return Recipe(
        "is456.strap-footing.property-line/v1",
        "structural_lib.design.is456.strap_footing",
        "load",
        "design",
        {
            "identity_source": {
                "identity": _identity("strap_footing", "STRAP-F0"),
                "geometry_basis_reference": "STRAP-F0-GEOMETRY",
                "rigidity_basis_reference": "STRAP-F0-RIGIDITY",
                "strap_isolation_basis_reference": "STRAP-F0-ISOLATION",
                "load_basis_reference": "STRAP-F0-LOAD",
                "bearing_settlement_basis_reference": "STRAP-F0-GEOTECH",
                "footing_carrier_basis_reference": "STRAP-F0-CARRIER",
                "strap_line_load_basis_reference": "STRAP-F0-LINE-LOAD",
                "load_pattern_basis_reference": "STRAP-F0-PATTERN",
                "material_basis_reference": "STRAP-F0-MATERIAL",
            },
            "geometry_topology": {
                "exterior_footing_length_mm": 2400.0,
                "exterior_footing_width_mm": 2500.0,
                "exterior_footing_depth_mm": 700.0,
                "interior_footing_length_mm": 2500.0,
                "interior_footing_width_mm": 3200.0,
                "interior_footing_depth_mm": 700.0,
                "exterior_column_side_mm": 500.0,
                "interior_column_side_mm": 500.0,
                "exterior_column_center_x_mm": 400.0,
                "interior_column_center_x_mm": 6400.0,
                "strap_width_mm": 500.0,
                "strap_overall_depth_mm": 950.0,
                "strap_effective_depth_mm": 850.0,
                "footing_count": 2,
                "column_count": 2,
                "footings_rectangular": True,
                "footings_parallel": True,
                "footings_constant_depth": True,
                "columns_square": True,
                "columns_and_strap_share_centerline": True,
                "interior_column_centered_on_footing": True,
                "strap_straight_and_prismatic": True,
                "strap_centered_across_footings": True,
                "foundation_on_soil": True,
                "strap_soil_contact": False,
                "openings_present": False,
                "pedestals_present": False,
                "analysis_method": "rigid_equal_pressure",
                "pressure_model": "equal_uniform_net",
            },
            "actions": {
                "service_exterior_column_load_kn": 1025.5625,
                "service_interior_column_load_kn": 1741.4375,
                "factored_exterior_column_load_kn": 1538.34375,
                "factored_interior_column_load_kn": 2612.15625,
                "service_clear_strap_line_load_kn_per_m": 12.0,
                "factored_clear_strap_line_load_kn_per_m": 18.0,
                "service_exterior_footing_carrier_kn_per_m2": 20.0,
                "service_interior_footing_carrier_kn_per_m2": 20.0,
                "factored_exterior_footing_carrier_kn_per_m2": 30.0,
                "factored_interior_footing_carrier_kn_per_m2": 30.0,
                "allowable_gross_bearing_pressure_kn_per_m2": 250.0,
                "load_combination_approved": True,
                "bearing_and_settlement_approved": True,
                "equal_uniform_pressure_approved": True,
                "footing_carrier_basis_approved": True,
                "strap_line_load_basis_approved": True,
                "load_pattern_compatible": True,
                "column_moments_present": False,
                "horizontal_actions_present": False,
                "uplift_or_load_reversal_present": False,
                "independently_factored_or_patterned_actions_present": False,
            },
            "materials_reinforcement": {
                "strap_concrete_grade_nmm2": 30,
                "steel_grade_nmm2": 500,
                "uncoated_deformed_bars": True,
                "top_bar_count": 6,
                "top_bar_diameter_mm": 25,
                "bottom_bar_count": 4,
                "bottom_bar_diameter_mm": 16,
                "side_face_bar_count_each_face": 4,
                "side_face_bar_diameter_mm": 12,
                "side_face_vertical_spacing_mm": 250.0,
                "stirrup_leg_count": 2,
                "stirrup_diameter_mm": 10,
                "stirrup_spacing_mm": 250.0,
                "nominal_cover_mm": 50.0,
                "required_nominal_cover_mm": 50.0,
                "maximum_aggregate_size_mm": 20.0,
                "available_top_anchorage_exterior_mm": 1200.0,
                "available_top_anchorage_interior_mm": 1200.0,
                "available_bottom_anchorage_exterior_mm": 1200.0,
                "available_bottom_anchorage_interior_mm": 1200.0,
                "vertical_closed_stirrups": True,
                "straight_anchorage": True,
                "bars_bundled": False,
                "bars_spliced": False,
                "bars_curtailed": False,
                "reinforcement_schedule_approved": True,
                "effective_depth_basis_approved": True,
                "durability_cover_basis_approved": True,
            },
            "evidence_review": {
                "exterior_footing_design_verified": True,
                "interior_footing_design_verified": True,
                "column_and_strap_transfer_verified": True,
                "footing_reinforcement_and_anchorage_verified": True,
                "supporting_areas_verified": True,
                "construction_clearances_verified": True,
                "exterior_footing_verification_reference": "EXT-FOOTING-01",
                "interior_footing_verification_reference": "INT-FOOTING-01",
                "transfer_verification_reference": "TRANSFER-01",
                "construction_verification_reference": "CONSTRUCTION-01",
                "detailing_basis_reference": "STRAP-F0-DETAILING",
                "durability_basis_reference": "STRAP-F0-DURABILITY",
                "qualified_review_required": True,
            },
        },
        ("geometry_topology", "strap_soil_contact"),
        True,
        "PASS",
    )


def _set_path(payload: dict[str, Any], path: tuple[str, ...], value: Any) -> None:
    current = payload
    for name in path[:-1]:
        current = current[name]
    current[path[-1]] = value


def run_recipes() -> list[dict[str, Any]]:
    """Run all valid/invalid vectors against the currently imported package."""

    from structural_lib.core.errors import InputContractError

    receipts: list[dict[str, Any]] = []
    for recipe in recipe_specs():
        module = importlib.import_module(recipe.module)
        request = getattr(module, recipe.loader)(copy.deepcopy(recipe.payload))
        result = getattr(module, recipe.operation)(request)
        serialized = result.to_dict()
        json.dumps(serialized, allow_nan=False)
        actual = result.engineering_status.value
        if actual != recipe.expected_engineering_status:
            raise AssertionError(
                f"{recipe.journey_id}: expected {recipe.expected_engineering_status}, got {actual}"
            )
        invalid = copy.deepcopy(recipe.payload)
        _set_path(invalid, recipe.invalid_path, recipe.invalid_value)
        try:
            getattr(module, recipe.loader)(invalid)
        except InputContractError as error:
            invalid_issue_codes = [issue.code for issue in error.issues]
        else:
            raise AssertionError(f"{recipe.journey_id}: invalid vector was accepted")
        receipts.append(
            {
                "journey_id": recipe.journey_id,
                "module": recipe.module,
                "request_schema_version": request.schema_version,
                "result_schema_version": result.schema_version,
                "engineering_status": actual,
                "invalid_issue_codes": invalid_issue_codes,
            }
        )
    return receipts


def _clean_env(installed_root: Path) -> dict[str, str]:
    env = {
        key: value
        for key, value in os.environ.items()
        if key not in {"PYTHONPATH", "VIRTUAL_ENV"}
    }
    env["PYTHONPATH"] = os.pathsep.join((str(installed_root), str(REPO_ROOT)))
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify(wheel: Path) -> dict[str, Any]:
    wheel = wheel.resolve()
    if not wheel.is_file() or wheel.suffix != ".whl":
        raise ValueError(f"Wheel does not exist: {wheel}")
    with tempfile.TemporaryDirectory(prefix="lib_pro_013_f0_") as raw_temp:
        temp_root = Path(raw_temp)
        installed_root = temp_root / "installed"
        installed_root.mkdir()
        install = subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                "--no-deps",
                "--target",
                str(installed_root),
                str(wheel),
            ],
            cwd=temp_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if install.returncode:
            raise RuntimeError(install.stderr)
        probe = (
            "import json; "
            "from scripts.verify_lib_pro_013_f0_family_artifact import run_recipes; "
            "print(json.dumps(run_recipes()))"
        )
        result = subprocess.run(
            [sys.executable, "-c", probe],
            cwd=temp_root,
            env=_clean_env(installed_root),
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode:
            raise RuntimeError(
                f"source-free recipe probe failed\n{result.stdout}\n{result.stderr}"
            )
        receipts = json.loads(result.stdout)
        return {
            "schema_version": "lib-pro-013-f0-artifact-evidence/v1",
            "wheel": str(wheel),
            "wheel_sha256": _sha256(wheel),
            "recipe_count": len(receipts),
            "source_free": True,
            "recipes": receipts,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", type=Path)
    parser.add_argument("--current", action="store_true")
    args = parser.parse_args()
    if args.current:
        print(
            json.dumps(
                {"recipe_count": 13, "recipes": run_recipes()}, indent=2, sort_keys=True
            )
        )
        return 0
    if args.wheel is None:
        parser.error("supply --wheel or --current")
    print(json.dumps(verify(args.wheel), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
