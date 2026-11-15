"""Independent COL07 S1 reference for one compression lap on a tied circle."""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from hashlib import sha256
from itertools import combinations, pairwise
from pathlib import Path

from check_library_029_col03_reference import verify_values
from check_library_029_col05_reference import positioned_capacity_model

ROOT = Path(__file__).resolve().parent
BASE = ROOT / "library-029-col07-circular-member.json"
FIXTURE = ROOT / "library-030-col07-circular-lap-reference.json"
PRODUCTION_BASE = "145a3229c2f06700c33ba9260b72c3e3e2152f6a"
BARS = tuple(f"B{index + 1}" for index in range(8))


def specimen():
    request = deepcopy(json.loads(BASE.read_text())["cases"]["tied"]["request"])
    request["identity"].update(
        case_id="circular_contact_lap",
        source_reference="COL07 tied circular compression lap specimen",
    )
    request["basis"].update(
        action_source_reference="CL1 worksheet: constant signed U1 at every cut",
        lap_action_continuity_reference="CL1 U1: constant Pu, Mx and My over the lap interval",
    )
    request["end_detail"]["end_hoop_offset_mm"] = 75
    request["transverse_cut_schedule"][
        "reference"
    ] = "CL1-R1 external full-strength closure and 1180 mm shop cut, revision D1"
    request["actions"] = [
        {
            "station_id": label,
            "check_station_mm": station,
            "combination_id": "U1",
            "pu_kn": 650,
            "mx_knm": -9,
            "my_knm": 30,
            "vx_kn": 0,
            "vy_kn": 0,
        }
        for label, station in (("A", 0), ("MID", 1500), ("B", 3000))
    ]
    request["laps"] = [
        {
            "lap_id": "CL1",
            "bar_id": "B1",
            "start_mm": 1130,
            "end_mm": 1970,
            "upper_bar_angle_deg": math.degrees(2 * math.asin(20 / (2 * 165))),
            "compression_reference": "CL1 interval compression worksheet",
            "additional_ring_stations_mm": list(range(1200, 1951, 150)),
            "maximum_lap_ring_pitch_mm": 75,
            "maximum_lap_end_ring_distance_mm": 75,
            "closure_clear_sector_deg": [195, 210],
            "closure_centreline_radial_envelope_mm": [158, 180],
        }
    ]
    return request


def strength(geometry, materials, action, diameter, bars, samples):
    section_diameter = geometry["diameter_mm"]
    fck, fy = materials["fck_nmm2"], materials["fy_nmm2"]
    pu, mx, my = (action[key] for key in ("pu_kn", "mx_knm", "my_knm"))
    steel_area = len(bars) * math.pi * diameter**2 / 4
    concrete_area = math.pi * section_diameter**2 / 4 - steel_area
    puz = (0.45 * fck * concrete_area + 0.75 * fy * steel_area) / 1000
    ray = positioned_capacity_model(
        section_diameter, fck, fy, pu, diameter, tuple(bars.values()), samples
    )
    axes = {
        "x_positive": ray(1, 0)["capacity_knm"],
        "x_negative": ray(-1, 0)["capacity_knm"],
        "y_positive": ray(0, 1)["capacity_knm"],
        "y_negative": ray(0, -1)["capacity_knm"],
    }
    alpha = max(1, min(2, 1 + (pu / puz - 0.2) / 0.6))
    cap_x = axes["x_positive" if mx >= 0 else "x_negative"]
    cap_y = axes["y_positive" if my >= 0 else "y_negative"]
    demand_ray = ray(mx, my)
    contour = (abs(mx) / cap_x) ** alpha + (abs(my) / cap_y) ** alpha
    direct = math.hypot(mx, my) / demand_ray["capacity_knm"]
    eccentricity = max(
        20, geometry["unsupported_length_mm"] / 500 + section_diameter / 30
    )
    minimum_ratios = {
        axis: pu
        * eccentricity
        / 1000
        / min(axes[f"{axis}_positive"], axes[f"{axis}_negative"])
        for axis in ("x", "y")
    }
    checks = {
        "contour": contour,
        "direct_ray": direct,
        **{
            f"minimum_eccentricity_{axis}": value
            for axis, value in minimum_ratios.items()
        },
    }
    assert abs(demand_ray["axial_residual_kn"]) < 1e-6
    assert abs(demand_ray["transverse_residual_knm"]) < 1e-6
    governing_check = max(checks, key=checks.__getitem__)
    return {
        "capacity_bar_ids": list(bars),
        "puz_kn": puz,
        "alpha_n": alpha,
        "axis_capacities_knm": axes,
        "demand_ray": demand_ray,
        "minimum_eccentricity_mm": eccentricity,
        "ratios": checks,
        "governing_check": governing_check,
        "utilization": checks[governing_check],
    }


def _ring_grid(request, lap):
    placement = request["placement"]
    tie = request["reinforcement"]["transverse"]
    field = list(
        range(
            placement["first_station_mm"],
            placement["last_station_mm"] + 1,
            tie["pitch_mm"],
        )
    )
    return sorted(field + lap["additional_ring_stations_mm"])


def calculate(request, samples):
    geometry, materials, steel, ends = (
        request[key] for key in ("geometry", "materials", "reinforcement", "end_detail")
    )
    (lap,) = request["laps"]
    start, end = lap["start_mm"], lap["end_mm"]
    bar_id = lap["bar_id"]
    tie = steel["transverse"]
    diameter, ring = steel["bar_diameter_mm"], steel["ring_radius_mm"]
    radius = geometry["diameter_mm"] / 2
    ring_dia = tie["diameter_mm"]
    hoop_radius = radius - steel["nominal_cover_mm"] - ring_dia / 2
    gross = math.pi * radius**2
    inertia = math.pi * radius**4 / 4
    bar_area = math.pi * diameter**2 / 4
    steel_stress = 0.87 * materials["fy_nmm2"]
    tension_bond = 1.5 * 1.60
    tension_ld = diameter * steel_stress / (4 * tension_bond)
    compression_ld = tension_ld / 1.25
    lap_required = max(1.10 * compression_ld, 24 * diameter)

    def centre(angle):
        return ring * math.cos(math.radians(angle)), ring * math.sin(
            math.radians(angle)
        )

    lower = {
        (f"{mark}-L" if mark == bar_id else mark): centre(index * 45)
        for index, mark in enumerate(BARS)
    }
    lower_mark, upper_mark = f"{bar_id}-L", f"{bar_id}-U"
    upper = {
        **{mark: xy for mark, xy in lower.items() if mark != lower_mark},
        upper_mark: centre(lap["upper_bar_angle_deg"]),
    }
    overlap = {**lower, upper_mark: upper[upper_mark]}
    contact_distance = math.dist(overlap[lower_mark], overlap[upper_mark])
    unrelated_clearance = min(
        math.dist(overlap[a], overlap[b]) - diameter
        for a, b in combinations(overlap, 2)
        if {a, b} != {lower_mark, upper_mark}
    )
    min_clearance = max(diameter, steel["aggregate_size_mm"] + 5)
    radial_gaps = {
        mark: hoop_radius - ring_dia / 2 - math.hypot(*xy) - diameter / 2
        for mark, xy in overlap.items()
    }
    # Closure is part of the external ring register. Its occupied angular sector
    # is independently separated from the two partners and the continuous bars.
    closure_low, closure_high = lap["closure_clear_sector_deg"]
    angles = sorted(
        [index * 45 for index in range(len(BARS))] + [lap["upper_bar_angle_deg"]]
    )
    closure_angular_gap = min(
        min((closure_low - angle) % 360, (angle - closure_high) % 360)
        for angle in angles
    )
    assert all(not closure_low <= angle <= closure_high for angle in angles)
    closure_min_radius, closure_max_radius = lap[
        "closure_centreline_radial_envelope_mm"
    ]
    assert 0 < closure_min_radius <= closure_max_radius <= hoop_radius
    cos_gap = math.cos(math.radians(closure_angular_gap))
    closest_radius = min(closure_max_radius, max(closure_min_radius, ring * cos_gap))
    closure_plan_clearance = (
        math.sqrt(ring**2 + closest_radius**2 - 2 * ring * closest_radius * cos_gap)
        - (diameter + ring_dia) / 2
    )
    upper_angles = angles.copy()
    upper_angles.remove(0)
    periphery_spacing = radius * math.radians(
        max(b - a for a, b in pairwise(upper_angles + [upper_angles[0] + 360]))
    )
    grid = _ring_grid(request, lap)
    inside = [z for z in grid if start < z < end]
    brackets = [
        max(z for z in grid if z < start),
        inside[0],
        inside[-1],
        min(z for z in grid if z > end),
    ]
    end_distances = [
        abs(z - end_z)
        for z, end_z in zip(brackets, (start, start, end, end), strict=True)
    ]
    field_pitch = max(b - a for a, b in pairwise(grid))
    lap_bracketed = [brackets[0], *inside, brackets[-1]]
    lap_pitch = max(b - a for a, b in pairwise(lap_bracketed))
    ring_clear_spacing = min(b - a for a, b in pairwise(grid)) - ring_dia

    issues = []
    if end - start < lap_required:
        issues.append(("FAIL", "COLUMN.LAP_LENGTH"))
    if not math.isclose(contact_distance, diameter, abs_tol=1e-6):
        issues.append(("FAIL", "COLUMN.LAP_CONTACT_GEOMETRY"))
    if lap_pitch > lap["maximum_lap_ring_pitch_mm"]:
        issues.append(("FAIL", "COLUMN.CIRCULAR_LAP_RING_PITCH"))
    if (
        request["basis"]["analysis_revision"]
        != request["basis"]["current_analysis_revision"]
    ):
        issues.append(("HOLD", "COLUMN.STALE_ANALYSIS"))
    if (
        request["transverse_cut_schedule"]["detailing_revision"]
        != request["basis"]["detailing_revision"]
    ):
        issues.append(("HOLD", "COLUMN.CIRCULAR_RING_CUT_HELD"))

    in_lap = [
        row for row in request["actions"] if start <= row["check_station_mm"] <= end
    ]
    stresses = [
        1000 * row["pu_kn"] / gross
        - 1e6 * math.hypot(row["mx_knm"], row["my_knm"]) * radius / inertia
        for row in in_lap
    ]
    min_stress = min(stresses)
    if (
        not lap["compression_reference"]
        or not request["basis"]["lap_action_continuity_reference"]
        or min_stress <= 0
    ):
        issues.append(("HOLD", "COLUMN.LAP_COMPRESSION_BASIS"))

    assert len(set(grid)) == len(grid)
    end_clearances = [grid[0], geometry["unsupported_length_mm"] - grid[-1]]
    required_end_clearance = max(
        ends["end_hoop_offset_mm"], request["placement"]["end_clearance_mm"]
    )
    assert all(
        required_end_clearance <= gap <= ends["max_end_hoop_offset_mm"]
        for gap in end_clearances
    )
    assert min(ends["start_straight_mm"], ends["end_straight_mm"]) >= tension_ld
    assert min_clearance <= unrelated_clearance and periphery_spacing <= 300
    assert all(abs(gap) < 1e-6 for gap in radial_gaps.values())
    assert closure_plan_clearance >= min_clearance
    assert min(end_distances) >= ring_dia / 2
    assert max(end_distances) <= lap["maximum_lap_end_ring_distance_mm"]
    field_pitch_limit = min(geometry["diameter_mm"], 16 * diameter, 300)
    assert field_pitch <= field_pitch_limit
    assert ring_clear_spacing >= steel["aggregate_size_mm"] + 5
    assert ring_dia >= max(6, diameter / 4)
    steel_ratio = len(lower) * bar_area / gross
    overlap_steel_ratio = len(overlap) * bar_area / gross
    assert 0.008 <= steel_ratio <= overlap_steel_ratio <= 0.04
    assert geometry["unsupported_length_mm"] / geometry["diameter_mm"] < 12
    assert steel["nominal_cover_mm"] >= max(
        40, diameter, steel["project_required_cover_mm"]
    )

    status = (
        "FAIL"
        if any(level == "FAIL" for level, _ in issues)
        else "HOLD" if issues else "PASS"
    )
    result = {
        "status": status,
        "issues": [code for _, code in issues],
        "checked_drawing_available": status == "PASS",
        "bbs_available": status == "PASS",
        "lap_provided_mm": end - start,
        "lap_required_mm": lap_required,
        "contact_centre_distance_mm": contact_distance,
        "maximum_lap_pitch_mm": lap_pitch,
        "minimum_gross_stress_nmm2": min_stress,
    }
    if status != "PASS":
        return result

    layouts = []
    for action, (phase, bars) in (
        (request["actions"][0], ("LOWER_ONLY", lower)),
        (request["actions"][1], ("OVERLAP_LOWER", lower)),
        (request["actions"][1], ("OVERLAP_UPPER", upper)),
        (request["actions"][2], ("UPPER_ONLY", upper)),
    ):
        layouts.append(
            {
                "station_id": action["station_id"],
                "combination_id": action["combination_id"],
                "phase": phase,
                **strength(geometry, materials, action, diameter, bars, samples),
            }
        )
    governing_ratio = max(row["utilization"] for row in layouts)
    governing = [
        {
            key: row[key]
            for key in (
                "station_id",
                "combination_id",
                "phase",
                "governing_check",
                "utilization",
            )
        }
        for row in layouts
        if math.isclose(row["utilization"], governing_ratio, abs_tol=1e-9)
    ]
    assert governing_ratio < 1
    assert all(len(layout["capacity_bar_ids"]) == 8 for layout in layouts)

    z0, z1 = (
        -ends["start_straight_mm"],
        geometry["unsupported_length_mm"] + ends["end_straight_mm"],
    )
    # Straight cuts use the physical piece limits. Ring cuts come from the
    # declared closure register.
    pieces = {
        **{mark: [1, z1 - z0, diameter] for mark in BARS if mark != bar_id},
        lower_mark: [1, end - z0, diameter],
        upper_mark: [1, z1 - start, diameter],
        tie["tie_id"]: [
            len(grid),
            request["transverse_cut_schedule"]["cut_lengths_mm"][tie["tie_id"]],
            ring_dia,
        ],
    }
    return {
        **result,
        "end_tension_development_mm": tension_ld,
        "unmodified_compression_development_mm": compression_ld,
        "unsupported_length_over_diameter": geometry["unsupported_length_mm"]
        / geometry["diameter_mm"],
        "end_clearances_mm": end_clearances,
        "ordinary_ring_pitch_limit_mm": field_pitch_limit,
        "actual_maximum_field_pitch_mm": field_pitch,
        "minimum_ring_clear_spacing_mm": ring_clear_spacing,
        "longitudinal_maximum_periphery_spacing_mm": periphery_spacing,
        "minimum_unrelated_clearance_mm": unrelated_clearance,
        "minimum_required_unrelated_clearance_mm": min_clearance,
        "closure_sector_projected_clearance_mm": closure_plan_clearance,
        "ring_outer_cover_mm": radius - hoop_radius - ring_dia / 2,
        "ring_centreline_radius_mm": hoop_radius,
        "ordinary_steel_ratio": steel_ratio,
        "overlap_physical_steel_ratio": overlap_steel_ratio,
        "spliced_bar_fraction": 1 / len(BARS),
        "overlap_bounds_mm": [start, end],
        "overlap_centres_from_column_centre_mm": overlap,
        "overlap_radial_gaps_to_ring_mm": radial_gaps,
        "ring_stations_mm": grid,
        "rings_inside_lap_mm": inside,
        "lap_end_bracket_stations_mm": brackets,
        "lap_end_bracket_distances_mm": end_distances,
        "strength_by_phase": layouts,
        "governing_strength": governing,
        "bbs": {
            "rows_qty_cut_mm_diameter_mm": pieces,
            "quantity": sum(qty for qty, _, _ in pieces.values()),
            "length_mm": sum(qty * length for qty, length, _ in pieces.values()),
            "mass_kg": 7850e-9
            * sum(
                qty * length * math.pi * dia**2 / 4
                for qty, length, dia in pieces.values()
            ),
        },
    }


def fixture():
    passing = specimen()
    controls = [
        ("short_overlap", "FAIL", "COLUMN.LAP_LENGTH"),
        ("coincident_contact", "FAIL", "COLUMN.LAP_CONTACT_GEOMETRY"),
        ("wide_lap_ring_pitch", "FAIL", "COLUMN.CIRCULAR_LAP_RING_PITCH"),
        ("missing_compression_interval", "HOLD", "COLUMN.LAP_COMPRESSION_BASIS"),
        ("outside_compression_kern", "HOLD", "COLUMN.LAP_COMPRESSION_BASIS"),
        ("stale_analysis", "HOLD", "COLUMN.STALE_ANALYSIS"),
        ("stale_ring_register", "HOLD", "COLUMN.CIRCULAR_RING_CUT_HELD"),
    ]
    cases = {
        "circular_contact_lap": {"request": passing, "expected": calculate(passing, 64)}
    }
    for name, status, code in controls:
        request = deepcopy(passing)
        request["identity"]["case_id"] = name
        (lap,) = request["laps"]
        if name == "short_overlap":
            lap.update(start_mm=1160, end_mm=1940)
        elif name == "coincident_contact":
            lap["upper_bar_angle_deg"] = 0
        elif name == "wide_lap_ring_pitch":
            lap["additional_ring_stations_mm"].remove(1500)
        elif name == "missing_compression_interval":
            request["basis"]["lap_action_continuity_reference"] = None
        elif name == "outside_compression_kern":
            for row in request["actions"]:
                row["my_knm"] = 40
        elif name == "stale_analysis":
            request["basis"]["current_analysis_revision"] = "A2"
        elif name == "stale_ring_register":
            request["transverse_cut_schedule"]["detailing_revision"] = "D0"
        expected = calculate(request, 64)
        assert expected["status"] == status and expected["issues"] == [code], name
        cases[name] = {"request": request, "expected": expected}

    compare_frozen(
        calculate(passing, 32),
        cases["circular_contact_lap"]["expected"],
        "32-to-64 angular refinement",
    )
    return {
        "schema_version": "library-030-col07-circular-lap-reference/v1",
        "frozen_before_implementation": True,
        "frozen_production_base": PRODUCTION_BASE,
        "base_tied_fixture_sha256": sha256(BASE.read_bytes()).hexdigest(),
        "sources": [
            "IS 456:2000 with Amendment 1 (6 mm minimum tie diameter), Cl. 25.1, 25.4, 26.1.1, 26.2.1, 26.2.5, 26.3.2, 26.4, 26.5.3 and 39.1–39.6. https://law.resource.org/pub/in/bis/S03/is.456.2000.pdf",
            "COL05 independent circular chord reference for the material laws and signed capacity method. COL07 tied circular member fixture for the underlying cage and full-strength R1 closure and cut.",
        ],
        "method": {
            "scope": "One straight Ø20 compression contact pair on the same perimeter of the short braced nonseismic eight-bar tied circular cage. Zero shear. CL1 is the only splice in the specimen.",
            "axes": "Coordinates relative to centre, x right and y down. Bar angles increase clockwise from the right. Positive Mx compresses the top and positive My the left.",
            "lap": "Use the M30 plain-bar bond basis of 1.5 N/mm² with the 1.60 deformed-bar and 1.25 compression factors. Check full-tension straight end development, 24 diameters and full-stress compression development with the conservative 10% two-bar contact allowance.",
            "compression": "The declared U1 action is constant over the interval and has positive minimum gross-section elastic stress. Withhold outputs on missing interval provenance or loss of this conservative compression screen.",
            "rings": "Same-radius partners directly touch the inner face of the same full-strength Ø10 closed ring. The project uses 75 mm maximum pitch through the lap and its bracketing rings and 75 mm maximum end-to-ring distance. The external R1 closure and cut remain on the same detailing revision. The closure projection stays between bars in the declared unobstructed sector.",
            "strength": "Use independent closed-form circular chord concrete resultants and discrete steel with displaced concrete. Solve P and signed biaxial moment equilibrium. Check the direct ray, signed Cl. 39.6 contour, and separate minimum eccentricity directions on both physical transfer layouts in the overlap. Credit one partner per layout.",
            "controls": "A FAIL or HOLD retains diagnostic evidence and withholds the checked drawing and BBS.",
        },
        "absolute_tolerances": {
            "length_mm": 0.001,
            "moment_knm": 0.01,
            "force_kn": 0.01,
            "ratio": 0.0001,
            "angle_deg": 0.01,
            "stress_nmm2": 0.001,
            "mass_kg": 0.001,
        },
        "cases": cases,
    }


def compare_frozen(actual, expected, path):
    """Compare discrete evidence exactly and allow round-off in the numerics."""
    if isinstance(expected, dict):
        assert actual.keys() == expected.keys(), path
        for key, value in expected.items():
            compare_frozen(actual[key], value, f"{path}.{key}")
    elif isinstance(expected, list):
        for index, (observed, target) in enumerate(zip(actual, expected, strict=True)):
            compare_frozen(observed, target, f"{path}[{index}]")
    elif isinstance(expected, float):
        verify_values(actual, expected, path)
    else:
        assert actual == expected, path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args()
    data = fixture()
    if args.freeze:
        FIXTURE.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")
    else:
        compare_frozen(data, json.loads(FIXTURE.read_text()), "fixture")
    for name, case in data["cases"].items():
        print(
            f"PASS independent COL07 circular lap {name}: {case['expected']['status']}"
        )


if __name__ == "__main__":
    main()
