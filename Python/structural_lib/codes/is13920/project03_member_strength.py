"""Member-strength witness checks for the bounded PROJECT03 frame packet."""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

from structural_lib.codes.is456 import tables
from structural_lib.codes.is456.beam.shear import shear_reinforcement_component_kn
from structural_lib.codes.is456.column.member_detailing import ordinary_column_shear
from structural_lib.codes.is13920.joint_strength import _Section


def _area(diameter_mm: float, count: int = 1) -> float:
    return count * math.pi * diameter_mm**2 / 4


def _shear_capacity(
    d_mm: float,
    width_mm: float,
    link_diameter_mm: float,
    pitch_mm: float,
    link_fy_mpa: float,
    concrete_kn: float = 0.0,
) -> tuple[float, float, float]:
    """Return accepted, steel and crushing shear capacities in kN.

    The PROJECT03 witness deliberately counts the two closed-link legs and does
    not credit ordinary concrete shear in the shared beam.
    """
    steel_kn = shear_reinforcement_component_kn(
        _area(link_diameter_mm, 2), link_fy_mpa, d_mm, 90, pitch_mm
    )
    crushing_kn = tables.get_tc_max_value(30) * width_mm * d_mm / 1000
    return min(steel_kn + concrete_kn, crushing_kn), steel_kn, crushing_kn


def _section_response(
    width_mm: float,
    depth_mm: float,
    fck_mpa: float,
    fy_mpa: float,
    layers: tuple[tuple[float, int, float], ...],
    axial_kn: float = 0.0,
) -> dict[str, Any]:
    response = _Section(width_mm, depth_mm, fck_mpa, fy_mpa).section_response(
        layers, axial_kn
    )
    # Keep the witness' documented 200 GPa strain threshold expression stable
    # at the JSON boundary while retaining the maintained equilibrium solver.
    response["yield_strain_threshold"] = 0.002 + fy_mpa / (1.15 * 200000.0)
    return response


def _beam_rows(
    actions: Mapping[str, Mapping[str, Any]],
    request: Mapping[str, Any],
    pitch_mm: float,
) -> tuple[dict[str, Any], dict[str, Any]]:
    width = request["beam_width_mm"]
    depth = request["joint_depth_mm"]
    bar_diameter = request["beam_bar_mm"]
    top_depth = request["beam_row_depth_from_top_mm"]["X"]
    count = len(request["beam_axis_across_column_mm"])
    response = _section_response(
        width,
        depth,
        request["beam_fck_mpa"],
        request["longitudinal_fy_mpa"],
        ((top_depth, count, bar_diameter), (depth - top_depth, count, bar_diameter)),
    )
    capacity, steel, crushing = _shear_capacity(
        depth - top_depth,
        width,
        request["beam_link_mm"],
        pitch_mm,
        request["link_fy_mpa"],
    )
    min_ratio = 0.4 / (0.87 * 415.0)
    rows: dict[str, Any] = {}
    for combination_id, action in actions.items():
        beam = action["beams"]["BX12"]
        span_m = float(beam["clear_span_m"])
        load = float(beam["factored_udl_kn_m"])
        moment_a, moment_b = beam["sectional_end_moments_knm"]
        reaction_a, reaction_b = beam["vertical_reactions_kn"]
        checks = {
            "J1-face": (0.0, moment_a, reaction_a),
            "J2-face": (span_m, moment_b, -reaction_b),
        }
        zero_shear = reaction_a / load
        if 0.0 < zero_shear < span_m:
            checks["zero-shear"] = (
                zero_shear,
                moment_a + reaction_a * zero_shear - load * zero_shear**2 / 2,
                0.0,
            )
        rows[combination_id] = {
            "flexural_capacity_knm_each_face": response["moment_knm"],
            "steel_shear_capacity_kn": steel,
            "crushing_bound_kn": crushing,
            "accepted_shear_capacity_kn": capacity,
            "minimum_shear_links_pass": _area(request["beam_link_mm"], 2)
            / (width * pitch_mm)
            >= min_ratio,
            "stations": {
                name: {
                    "x_m": x_m,
                    "sectional_moment_knm": moment,
                    "sectional_shear_kn": shear,
                    "flexure_utilization": abs(moment) / response["moment_knm"],
                    "shear_utilization": abs(shear) / capacity,
                }
                for name, (x_m, moment, shear) in checks.items()
            },
        }
    return response, rows


def _beam_strength(
    actions: Mapping[str, Mapping[str, Any]],
    joints: Mapping[str, Mapping[str, Any]],
    inputs: Mapping[str, Mapping[str, Any]],
    pitch_mm: float,
) -> dict[str, Any]:
    request = inputs["J1"]
    response, rows = _beam_rows(actions, request, pitch_mm)
    face_controls: dict[str, Any] = {}
    for joint_id, side in (("J1", "plus"), ("J2", "minus")):
        face_controls[joint_id] = max(
            (
                {
                    "direction": direction,
                    "combination_id": row["combination_id"],
                    **row["beam_capacity_shear"][side],
                }
                for direction in ("X+", "X-")
                for row in joints[joint_id]["directions"][direction]["rows"]
            ),
            key=lambda value: value["utilization"],
        )
    governing = {
        family: max(
            (
                {"combination_id": combo, "station": station_id, **station}
                for combo, row in rows.items()
                for station_id, station in row["stations"].items()
            ),
            key=lambda value: value[f"{family}_utilization"],
        )
        for family in ("flexure", "shear")
    }
    return {
        "section": response,
        "rows": rows,
        "governing": governing,
        "governing_capacity_shear_at_faces": face_controls,
        "pass": response["tension_ductile"]
        and all(
            governing[family][f"{family}_utilization"] <= 1.0 for family in governing
        )
        and all(row["pass"] for row in face_controls.values())
        and all(row["minimum_shear_links_pass"] for row in rows.values()),
    }


def _column_legs(
    actions: Mapping[str, Mapping[str, Any]],
    joints: Mapping[str, Mapping[str, Any]],
    inputs: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    columns: dict[str, dict[str, Any]] = {}
    for combination_id, source in actions.items():
        direction = source["direction"]
        for member, leg in source["columns"].items():
            joint_id = leg["joint"]
            end = leg["position"]
            request = inputs[joint_id]
            width = request["column_width_mm"]
            edge = request["column_bar_edge_mm"]
            diameter = request["column_bar_mm"]
            height = request["column_clear_heights_mm"][end]
            shear_row = next(
                row
                for row in joints[joint_id]["directions"][direction]["rows"]
                if row["combination_id"] == combination_id
            )["column_capacity_shear"][end]
            near = leg["near_face"]
            far = leg["boundary_face"]
            concurrent = near["force_kn"]
            concurrent_index = 1 if direction[0] == "X" else 0
            shear_demand = shear_row["demand_kn"] + abs(concurrent[concurrent_index])
            min_pu = min(abs(near["force_kn"][2]), abs(far["force_kn"][2]))
            d_column = width - edge
            pitch_mm = (
                request["column_end_pitch_mm"] + 2 * request["tie_station_tolerance_mm"]
            )
            provided_pt = 100 * _area(diameter, 3) / (width * d_column)
            plane_capacity = ordinary_column_shear(
                width_mm=width,
                d_mm=d_column,
                gross_area_mm2=width**2,
                pu_kn=min_pu,
                vu_kn=shear_demand,
                fck_nmm2=request["column_fck_mpa"],
                hoop_diameter_mm=request["column_link_mm"],
                hoop_fy_nmm2=request["link_fy_mpa"],
                pitch_mm=pitch_mm,
                table19_steel_percent=0.25 if provided_pt >= 0.25 else 0.15,
            )
            layers = (
                (edge, 3, diameter),
                (width / 2, 2, diameter),
                (width - edge, 3, diameter),
            )
            ends: dict[str, Any] = {}
            for label, face in (("joint", near), ("boundary", far)):
                pu = abs(face["force_kn"][2])
                response = _section_response(
                    width,
                    width,
                    request["column_fck_mpa"],
                    request["longitudinal_fy_mpa"],
                    layers,
                    pu,
                )
                eccentricity = max(20.0, height / 500.0 + width / 30.0)
                minimum_moment = pu * eccentricity / 1000.0
                demand_x, demand_y = (
                    max(abs(moment), minimum_moment)
                    for moment in face["couple_knm"][:2]
                )
                resistance = response["moment_knm"]
                ends[label] = {
                    "pu_kn": pu,
                    "signed_moments_knm": list(face["couple_knm"][:2]),
                    "minimum_eccentricity_mm": eccentricity,
                    "biaxial_demand_abs_knm": [demand_x, demand_y],
                    "uniaxial_moment_capacity_knm_each_axis": resistance,
                    "conservative_linear_biaxial_utilization": (demand_x + demand_y)
                    / resistance,
                }
            columns.setdefault(member, {})[combination_id] = {
                "ends": ends,
                "effective_length_mm": height,
                "slenderness_each_axis": height / width,
                "shear_component_sum_kn": shear_demand,
                "steel_shear_capacity_kn": plane_capacity.vus_kn,
                "crushing_bound_kn": plane_capacity.crushing_kn,
                "accepted_shear_capacity_kn": plane_capacity.capacity_kn,
                "shear_utilization": plane_capacity.utilization,
            }
    result: dict[str, Any] = {}
    for member, rows in columns.items():
        flexure = max(
            (
                {"combination_id": combo, "end": end, **values}
                for combo, row in rows.items()
                for end, values in row["ends"].items()
            ),
            key=lambda value: value["conservative_linear_biaxial_utilization"],
        )
        shear = max(
            ({"combination_id": combo, **row} for combo, row in rows.items()),
            key=lambda value: value["shear_utilization"],
        )
        joint_id = member.split("-")[1]
        request = inputs[joint_id]
        first_key = (
            "column_first_end_hoop_mm"
            if joint_id == "J1"
            else "column_end_link_first_mm"
        )
        first = request[first_key]
        pitch = request["column_end_pitch_mm"]
        tolerance = request["tie_station_tolerance_mm"]
        length = shear["effective_length_mm"]
        stations = [
            first + i * pitch for i in range(math.ceil((length - first) / pitch))
        ]
        transition_ok = (
            len(stations) >= 2
            and first + tolerance <= 50
            and length - stations[-1] <= pitch
        )
        width = request["column_width_mm"]
        max_pu = max(
            end["pu_kn"] for row in rows.values() for end in row["ends"].values()
        )
        result[member] = {
            "rows": rows,
            "governing_flexure": flexure,
            "governing_shear": shear,
            "longitudinal_bar_count": 8,
            "longitudinal_bar_diameter_mm": request["column_bar_mm"],
            "transverse_group_stations_from_face_mm": stations,
            "transverse_pieces_per_group": 3,
            "adverse_transverse_pitch_mm": pitch + 2 * tolerance,
            "pass": flexure["conservative_linear_biaxial_utilization"] <= 1.0
            and shear["shear_utilization"] <= 1.0
            and shear["slenderness_each_axis"] <= 12.0
            and max_pu / (width**2 / 1000) <= 0.40 * request["column_fck_mpa"]
            and transition_ok,
        }
    return result


def check_project_members(
    actions: Mapping[str, Mapping[str, Any]],
    joints: Mapping[str, Mapping[str, Any]],
    inputs: Mapping[str, Mapping[str, Any]],
    adverse_beam_pitch_mm: float,
) -> dict[str, Any]:
    """Check the common PROJECT03 beam and its admitted column legs.

    Callers supply already-normalized, already-admitted action and joint data;
    this owner intentionally does not accept source-packet or geometry duties.
    """
    if adverse_beam_pitch_mm <= 0:
        raise ValueError("PROJECT03 adverse beam-link pitch must be positive.")
    return {
        "beam_strength": _beam_strength(actions, joints, inputs, adverse_beam_pitch_mm),
        "column_legs": _column_legs(actions, joints, inputs),
    }
