"""Freeze the nominal and limiting fit of the nested-link Ø20 lap."""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from hashlib import sha256
from itertools import pairwise, product
from pathlib import Path

from check_library_030_beam05_t_lap_reference import _strengths, expected

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "library-030-beam05-flanged-lap-restraint-reference.json"
TARGET = HERE / "library-030-beam05-lap-placement-reference.json"
BASE = "d99c7e7bffe28dbc72cf5b987663490642d4596e"

PLACEMENT = {
    "source_reference": "Declared trial cage geometry and procurement limits for the straight web cage",
    "bar_axis_tolerance_mm": 2,
    "bar_end_tolerance_mm": 10,
    "cage_location_tolerance_mm": 5,
    "link_station_tolerance_mm": 5,
    "internal_bend_radius_tolerance_mm": 1,
    "hook_plane_tolerance_mm": 1,
    "hook_vertex_leg_tolerance_mm": 5,
    "longitudinal_diameter_allowance_mm": 2,
    "link_diameter_allowance_mm": 1,
    "required_cover_mm": 30,
    "concrete_placement_access_diameter_mm": 25,
}


def revised_request(entry):
    request = deepcopy(entry["request"])
    member, link, lap = request["member"], request["link_detail"], request["lap"]
    member["clear_cover_mm"] = 40
    member["reinforcement_revision"] += "-PLACEMENT"
    link["internal_bend_radius_mm"] = 22
    link["restraint_link"].update(
        left_centre_x_mm=96, right_centre_x_mm=204, station_offset_mm=60
    )
    centres = {
        "T1-1": (66, 66),
        "T1-2": (234, 66),
        "T1-3": (118, 66),
        "T1-4": (182, 66),
        "B1-1": (66, 534),
        "B1-2": (118, 534),
        "B1-3": (234, 534),
        "B2-1": (66, 464),
        "B2-2": (234, 464),
    }
    for bar in member["bars"]:
        bar["x_from_left_mm"], bar["y_from_top_mm"] = centres[bar["bar_id"]]
    lap["partner_x_from_left_mm"] = 182
    return request


def layouts(member, lap):
    original = next(bar for bar in member["bars"] if bar["bar_id"] == lap["bar_id"])
    partner = dict(
        original,
        bar_id=lap["partner_bar_id"],
        x_from_left_mm=lap["partner_x_from_left_mm"],
    )
    return {
        "upstream": member["bars"],
        "downstream": [bar for bar in member["bars"] if bar != original] + [partner],
    }, partner


def placement_geometry(request, basis):
    member, link, lap = request["member"], request["link_detail"], request["lap"]
    if basis is None:
        return {"status": "HOLD", "issue": "placement_basis_missing"}
    _, partner = layouts(member, lap)
    bars = {bar["bar_id"]: bar for bar in [*member["bars"], partner]}
    inner = link["restraint_link"]
    d_link = member["link_diameter_mm"]
    max_link = d_link + basis["link_diameter_allowance_mm"]
    mesh = basis["bar_axis_tolerance_mm"]
    bar_allowance = basis["longitudinal_diameter_allowance_mm"]
    radius = link["internal_bend_radius_mm"]
    max_radius = radius + basis["internal_bend_radius_tolerance_mm"]
    min_radius = radius - basis["internal_bend_radius_tolerance_mm"]
    centre_radius = radius + d_link / 2
    width, depth = member["width_mm"], member["depth_mm"]
    centre_inset = member["clear_cover_mm"] + d_link / 2
    inner_bounds = (inner["left_centre_x_mm"], inner["right_centre_x_mm"])
    seats = {
        "T1-1": (centre_inset, True, True),
        "T1-2": (width - centre_inset, False, True),
        "T1-3": (inner_bounds[0], True, True),
        "T1-4": (inner_bounds[1], False, True),
        "B1-1": (centre_inset, True, False),
        "B1-2": (inner_bounds[0], True, False),
        "B1-2-partner": (inner_bounds[1], False, False),
        "B1-3": (width - centre_inset, False, False),
    }
    returns = {}
    for mark, (side, left, top) in seats.items():
        x = side + centre_radius * (1 if left else -1)
        y = centre_inset + centre_radius
        if not top:
            y = depth - y
        bar = bars[mark]
        dx = (x - bar["x_from_left_mm"]) * (1 if left else -1)
        dy = (y - bar["y_from_top_mm"]) * (1 if top else -1)
        # The jig bounds both axes relative to the formed bend centre.
        # Use the radial stress-free fit at the controlling interval corner.
        radial = math.hypot(abs(dx) + mesh, abs(dy) + mesh)
        max_bar_radius = (bar["diameter_mm"] + bar_allowance) / 2
        returns[mark] = {
            "min_clearance_mm": min_radius - max_bar_radius - radial,
            "outward_offsets_mm": [dx, dy],
            "stays_inside_bend_sector": min(dx, dy) > mesh,
        }
    clearances = {}
    for face, layer in (("top", 1), ("bottom", 1), ("bottom", 2)):
        row = sorted(
            (
                bar
                for bar in bars.values()
                if bar["face"] == face and bar["layer"] == layer
            ),
            key=lambda bar: bar["x_from_left_mm"],
        )
        clearances[f"{face}-{layer}"] = [
            second["x_from_left_mm"]
            - first["x_from_left_mm"]
            - 2 * mesh
            - (first["diameter_mm"] + second["diameter_mm"]) / 2
            - bar_allowance
            for first, second in pairwise(row)
        ]
    inner_bottom_y = max(
        bar["y_from_top_mm"] for bar in bars.values() if bar["layer"] == 2
    )
    vertical = (
        bars["B1-1"]["y_from_top_mm"] - inner_bottom_y - 2 * mesh - 20 - bar_allowance
    )
    maximum_shift = link["hook_plane_offset_mm"] + basis["hook_plane_tolerance_mm"]
    min_grid_pitch = min(
        inner["station_offset_mm"],
        member["link_spacing_mm"] - inner["station_offset_mm"],
    )
    grid_clearance = (
        min_grid_pitch
        - 2 * basis["link_station_tolerance_mm"]
        - maximum_shift
        - max_link
    )
    nominal_opening = member["link_spacing_mm"] - inner["station_offset_mm"]
    centre = width / 2
    left_edge = max(
        bar["x_from_left_mm"] + (bar["diameter_mm"] + bar_allowance) / 2 + mesh
        for bar in bars.values()
        if bar["x_from_left_mm"] < centre
    )
    right_edge = min(
        bar["x_from_left_mm"] - (bar["diameter_mm"] + bar_allowance) / 2 - mesh
        for bar in bars.values()
        if bar["x_from_left_mm"] >= centre
    )
    access = [
        right_edge - left_edge,
        nominal_opening
        - 2 * basis["link_station_tolerance_mm"]
        - maximum_shift
        - max_link,
    ]
    tolerance_tail = basis["hook_vertex_leg_tolerance_mm"]
    min_hook_tail = (
        link["hook_vertex_leg_mm"] - tolerance_tail - max_radius - max_link / 2
    )
    min_cover = (
        member["clear_cover_mm"]
        - basis["cage_location_tolerance_mm"]
        - basis["link_diameter_allowance_mm"] / 2
    )
    extent = member["straight_bars"]
    left, _, right = member["supports"]
    end_cover = (
        min(
            extent["start_mm"] - left["centre_mm"] + left["width_mm"] / 2,
            right["centre_mm"] + right["width_mm"] / 2 - extent["end_mm"],
        )
        - basis["bar_end_tolerance_mm"]
    )
    minimum_shift = link["hook_plane_offset_mm"] - basis["hook_plane_tolerance_mm"]
    link_width = inner_bounds[1] - inner_bounds[0]
    min_gap = min(gap for row in clearances.values() for gap in row)
    required_gap = max(20, member["aggregate_size_mm"] + 5)
    if (
        min(row["min_clearance_mm"] for row in returns.values()) < 0
        or min_gap < required_gap
        or vertical < max(20, 2 * member["aggregate_size_mm"] / 3)
        or grid_clearance < required_gap
        or min(access) < basis["concrete_placement_access_diameter_mm"]
        or min_hook_tail < 8 * d_link
        or minimum_shift < max_link
        or link["hook_vertex_leg_mm"] + tolerance_tail >= link_width
        or min_cover < basis["required_cover_mm"]
        or end_cover < basis["required_cover_mm"]
    ):
        status, issue = "FAIL", "placement_interference"
    elif not all(row["stays_inside_bend_sector"] for row in returns.values()):
        status, issue = "HOLD", "restraint_sector_unresolved"
    else:
        status, issue = "PASS", None
    return {
        "status": status,
        "issue": issue,
        "returns": returns,
        "minimum_steel_cover_mm": min_cover,
        "minimum_main_bar_end_cover_mm": end_cover,
        "minimum_horizontal_clearances_mm": clearances,
        "minimum_vertical_clearance_mm": vertical,
        "minimum_grid_clearance_mm": grid_clearance,
        "maximum_perimeter_pitch_mm": member["link_spacing_mm"]
        + 2 * basis["link_station_tolerance_mm"],
        "minimum_hook_tail_mm": min_hook_tail,
        "minimum_hook_plane_shift_mm": minimum_shift,
        "minimum_clear_concrete_access_mm": access,
    }


def worst_strength(request, basis, nominal):
    member, lap = deepcopy(request["member"]), request["lap"]
    member["link_spacing_mm"] += 2 * basis["link_station_tolerance_mm"]
    move = basis["bar_axis_tolerance_mm"] + basis["cage_location_tolerance_mm"]
    # Resolve all extremes. One common inward shift is not conservative
    # for both signs when the inner-layer compression credit changes.
    extremes = []
    for shifts in product((-move, move), repeat=3):
        row_shift = dict(zip(("top-1", "bottom-1", "bottom-2"), shifts, strict=True))
        displaced = [
            dict(
                bar,
                y_from_top_mm=bar["y_from_top_mm"]
                + row_shift[f"{bar['face']}-{bar['layer']}"],
            )
            for bar in member["bars"]
        ]
        candidate = dict(member, bars=displaced)
        arrangement, _ = layouts(candidate, lap)
        _, _, capacities = _strengths(candidate, arrangement)
        extremes.append((row_shift, capacities["upstream"]))
    result = {}
    for face in ("bottom", "top"):
        moment_shift, moment_case = min(
            extremes, key=lambda case: case[1][face]["capacity_knm"]
        )
        shear_shift, shear_case = min(
            extremes, key=lambda case: case[1][face]["shear_capacity_kn"]
        )
        shear = shear_case[face]["shear_capacity_kn"]
        moment = moment_case[face]["capacity_knm"]
        rows = [
            row
            for row in nominal["signed_rows"]
            if not row["diagnostic_only"] and row["tension_face"] == face
        ]
        moment_row = max(rows, key=lambda row: abs(row["moment_knm"]))
        shear_row = max(rows, key=lambda row: abs(row["shear_kn"]))
        result[face] = {
            "capacity_knm": moment,
            "shear_capacity_kn": shear,
            "flexure_row_shifts_mm": moment_shift,
            "shear_row_shifts_mm": shear_shift,
            "moment_row_id": moment_row["row_id"],
            "shear_row_id": shear_row["row_id"],
            "flexure_utilization": abs(moment_row["moment_knm"]) / moment,
            "shear_utilization": abs(shear_row["shear_kn"]) / shear,
        }
        assert (
            max(result[face]["flexure_utilization"], result[face]["shear_utilization"])
            < 1
        )
    return result


def nominal_artifacts(request, nominal):
    member, detail = request["member"], request["link_detail"]
    inner = detail["restraint_link"]
    drawing, bbs = nominal["drawing"], nominal["bbs"]
    width = inner["right_centre_x_mm"] - inner["left_centre_x_mm"]
    _, top, _, bottom = drawing["web_link_centreline_bounds_mm"]
    diameter = member["link_diameter_mm"]
    radius = detail["internal_bend_radius_mm"] + diameter / 2
    # The diagonal lower limb is the only side spanning the hook planes.
    cut = (
        2 * detail["hook_vertex_leg_mm"]
        + width
        + 2 * (bottom - top)
        + math.hypot(width, detail["hook_plane_offset_mm"])
        + 5 * radius * (math.pi / 2 - 2)
    )
    offset = inner["station_offset_mm"]
    grid = [station + offset for station in drawing["link_stations_mm"]]
    drawing["restraint_link_stations_mm"] = grid
    drawing["restraint_link_centreline_bounds_mm"] = [
        inner["left_centre_x_mm"],
        top,
        inner["right_centre_x_mm"],
        bottom,
    ]
    mark = f"{member['member_id']}-L{diameter:g}-restraint"
    bbs["rows_qty_cut_mm_diameter_mm"][mark] = [len(grid), cut, diameter]
    bbs["total_quantity"] += len(grid)
    bbs["total_length_mm"] += len(grid) * cut
    bbs["total_mass_kg"] += 7850e-9 * math.pi * diameter**2 / 4 * len(grid) * cut
    return {"drawing": drawing, "bbs": bbs}


def fixture():
    parent = json.loads(SOURCE.read_text())["cases"]
    cases = {}
    for name in ("l_lap", "t_control"):
        request = revised_request(parent[name])
        geometry = placement_geometry(request, PLACEMENT)
        assert geometry["status"] == "PASS"
        nominal = expected(request)
        assert nominal["status"] == "PASS"
        length_loss = PLACEMENT["bar_end_tolerance_mm"]
        overlap = nominal["overlap_mm"] - 2 * length_loss
        anchorage = (
            min(
                row["straight_available_mm"]
                for row in nominal["support_anchorage"].values()
            )
            - length_loss
        )
        assert min(overlap, anchorage) >= nominal["required_lap_mm"]
        cases[name] = {
            "request": request,
            "placement": PLACEMENT,
            "expected": geometry,
            "nominal_governing_acceptance_rows": nominal["governing_acceptance_rows"],
            "nominal_overlap_mm": nominal["overlap_mm"],
            "nominal_required_lap_mm": nominal["required_lap_mm"],
            "minimum_overlap_mm": overlap,
            "minimum_straight_support_development_mm": anchorage,
            "worst_strength": worst_strength(request, PLACEMENT, nominal),
            **nominal_artifacts(request, nominal),
        }
    request = cases["l_lap"]["request"]
    for name, candidate, basis, status, issue in (
        (
            "bend_interference",
            request,
            dict(PLACEMENT, bar_axis_tolerance_mm=4),
            "FAIL",
            "placement_interference",
        ),
        ("missing_placement", request, None, "HOLD", "placement_basis_missing"),
    ):
        result = placement_geometry(candidate, basis)
        assert (result["status"], result["issue"]) == (status, issue)
        cases[name] = {"request": candidate, "placement": basis, "expected": result}
    moved = deepcopy(request)
    next(bar for bar in moved["member"]["bars"] if bar["bar_id"] == "T1-3")[
        "x_from_left_mm"
    ] = 122
    result = placement_geometry(moved, PLACEMENT)
    assert (result["status"], result["issue"]) == (
        "HOLD",
        "restraint_sector_unresolved",
    )
    cases["restraint_sector"] = {
        "request": moved,
        "placement": PLACEMENT,
        "expected": result,
    }
    return {
        "fixture_version": "library-030-beam05-lap-placement-reference/v1",
        "frozen_before_implementation": True,
        "frozen_production_base": BASE,
        "bound_sources": {SOURCE.name: sha256(SOURCE.read_bytes()).hexdigest()},
        "sources": [
            "IS 456:2000 clauses 26.2.2.4(b), 26.3.2, 26.5.1.2, 26.5.3.2(b)(1) and Figure 8. https://law.resource.org/pub/in/bis/S03/is.456.2000.pdf",
            "SP 34:1987 Fig. 8.8B shows the single fully nested closed link. https://law.resource.org/pub/in/bis/S03/is.sp.34.1987.pdf",
        ],
        "scope": [
            "The reported tolerance values are declared for this fixture. The bar positions are bounded both relative to the nominal cage and to the actual return. Verify the formed-bend and cage location limits.",
            "The checked corner region lies beyond both bend tangency axes, so the same rounded return surrounds each designated outer bar in both directions throughout the declared axis range.",
            "The access rectangle applies to a straight unobstructed web cage. Assemble the two link grids on a jig and install the longitudinal bars and spacers before locating the cage. Cover blocks retain the stated placement. Obstructions from slab and support bars require supplied geometry and a separate placement check.",
        ],
        "cases": cases,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    data = fixture()
    if parser.parse_args().freeze:
        TARGET.write_text(
            json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8"
        )
    else:
        assert json.loads(TARGET.read_text(encoding="utf-8")) == data
    for name, case in data["cases"].items():
        print(
            f"PASS independent BEAM05 lap placement {name}: {case['expected']['status']}"
        )


if __name__ == "__main__":
    main()
