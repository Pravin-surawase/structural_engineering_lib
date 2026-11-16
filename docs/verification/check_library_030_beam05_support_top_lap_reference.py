"""Freeze an ordinary top tension lap on the left of the interior support."""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

from check_library_030_beam05_lap_placement_reference import (
    layouts,
    nominal_artifacts,
    placement_geometry,
    worst_strength,
)
from check_library_030_beam05_t_lap_reference import (
    LOADS_KNM,
    _governing,
    _span_actions,
    _strengths,
    _support_evidence,
    _takeoff,
)

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "library-030-beam05-rectangular-lap-placement-reference.json"
TARGET = HERE / "library-030-beam05-support-top-lap-reference.json"
BASE = "f848468382e6c3e841eed108094b9bf493849180"
SEATS = {
    ("outer", "top", "left"): "T1-1",
    ("outer", "top", "right"): "T1-2",
    ("restraint", "top", "left"): "T1-3",
    ("restraint", "top", "right"): "T1-3-partner",
    ("outer", "bottom", "left"): "B1-1",
    ("outer", "bottom", "right"): "B1-3",
    ("restraint", "bottom", "left"): "B1-2",
    ("restraint", "bottom", "right"): "B1-4",
}


def _revised_request(parent, name):
    request = deepcopy(parent)
    member, lap = request["member"], request["lap"]
    request["identity"]["case_id"] = name
    member["analysis_revision"] += "-TOP-LAP"
    member["current_analysis_revision"] = member["analysis_revision"]
    member["reinforcement_revision"] += f"-TOP-LAP-{name}"
    bars = {bar["bar_id"]: bar for bar in member["bars"]}
    del bars["T1-4"]
    bars["T1-3"]["diameter_mm"] = 16
    bars["B1-4"] = dict(bars["B1-2"], bar_id="B1-4", x_from_left_mm=182)
    member["bars"] = list(bars.values())
    lap.update(
        bar_id="T1-3",
        partner_bar_id="T1-3-partner",
        partner_x_from_left_mm=182,
        placement_reference="Separated top Ø16 tension lap on the left of support B",
    )
    start = {"wrong_lap_sign": 2980, "wrong_expanded_sign": 3005}.get(name, 3020)
    end = {"short_overlap": 3730, "short_after_tolerance": 3760}.get(name, 3780)
    locations = {
        "LAP-START": start,
        "LAP-MID": (start + end) / 2,
        "LAP-END": end,
        "LAP-TOL-START": start - 10,
        "LAP-TOL-END": end + 10,
        "INFLECTION-LEFT": 3000,
        "INFLECTION-RIGHT": 5000,
    }
    if name == "missing_tolerance_station":
        del locations["LAP-TOL-END"]
    if name == "missing_continuity_station":
        del locations["INFLECTION-LEFT"]
    member["stations"] = [
        site for site in member["stations"] if not site["station_id"].startswith("LAP-")
    ] + [
        {"station_id": key, "x_mm": value, "side": "CONTINUOUS"}
        for key, value in locations.items()
    ]
    loads = dict(LOADS_KNM)
    if name == "high_lap_moment":
        loads["U2"] = 66
        member["analysis_revision"] += "-HIGH-U2"
        member["current_analysis_revision"] = member["analysis_revision"]
    member["actions"] = []
    for combination in member["combinations"]:
        tag = combination["combination_id"]
        combination["required_station_ids"] = [
            station["station_id"] for station in member["stations"]
        ]
        for site in member["stations"]:
            station, x = site["station_id"], site["x_mm"]
            right = x > 4000 or (x == 4000 and site["side"] == "RIGHT")
            moment, shear = _span_actions(loads[tag], x, right_span=right)
            member["actions"].append(
                {
                    "row_id": f"{tag}:{station}",
                    "combination_id": tag,
                    "station_id": station,
                    "mu_knm": moment,
                    "vu_kn": shear,
                    "tu_knm": 0,
                }
            )
    if name == "congested_partner":
        lap["partner_x_from_left_mm"] = 150
    if name == "missing_lap_action":
        member["actions"] = [
            row for row in member["actions"] if row["row_id"] != "U2:LAP-TOL-END"
        ]
    if name == "stale_analysis":
        member["current_analysis_revision"] += "-EDITED"
    if name == "restraint_sector":
        bars["T1-3"]["x_from_left_mm"] = 122
    return request, loads, start, end


def _signed_rows(member, arrangements, capacities, start, end):
    stations = {item["station_id"]: item["x_mm"] for item in member["stations"]}
    rows = []
    for action in member["actions"]:
        x = stations[action["station_id"]]
        moment, shear = action["mu_knm"], action["vu_kn"]
        face = "top" if moment < 0 else "bottom"
        for layout, active in (("upstream", x <= end), ("downstream", x >= start)):
            if not active:
                continue
            capability = capacities[layout][face]
            shear_capacity = (
                capability["shear_capacity_kn"]
                if moment
                else min(
                    capacities[layout][side]["shear_capacity_kn"]
                    for side in ("bottom", "top")
                )
            )
            rows.append(
                {
                    "row_id": action["row_id"],
                    "station_mm": x,
                    "layout": layout,
                    "layout_bar_ids": [bar["bar_id"] for bar in arrangements[layout]],
                    "tension_face": face if moment else None,
                    "moment_knm": moment,
                    "shear_kn": shear,
                    "flexure_utilization": abs(moment) / capability["capacity_knm"],
                    "shear_utilization": abs(shear) / shear_capacity,
                    "diagnostic_only": x in (0, 4000, 8000),
                }
            )
    return rows


def _required_top_lap(member, diameter_mm):
    assert member["fck_nmm2"] == 30
    design_bond = 1.5 * 1.6
    development = 0.87 * member["fy_nmm2"] * diameter_mm / (4 * design_bond)
    return max(development, 30 * diameter_mm, 15 * diameter_mm, 200)


def _nominal_cage(request, basis, loads, start, end):
    member, lap = request["member"], request["lap"]
    original = next(bar for bar in member["bars"] if bar["bar_id"] == lap["bar_id"])
    arrangement, partner = layouts(member, lap)
    _, _, capacities = _strengths(member, arrangement)
    depth_tol = basis["cage_location_tolerance_mm"] + basis["bar_axis_tolerance_mm"]
    end_tol = basis["bar_end_tolerance_mm"]
    expanded = (start - end_tol, end + end_tol)
    # In this first span the moment decreases on this entire window.
    assert 1500 < expanded[0] < expanded[1] < 4000
    window = {
        tag: [_span_actions(load, x)[0] for x in expanded]
        for tag, load in loads.items()
    }
    rows = _signed_rows(member, arrangement, capacities, start, end)
    acceptance = [row for row in rows if not row["diagnostic_only"]]
    adverse = worst_strength(request, basis, {"signed_rows": rows})
    assert all(max(values) < 0 for values in window.values())
    half_capacity = adverse["top"]["capacity_knm"] / 2
    assert max(abs(values[-1]) for values in window.values()) < half_capacity
    length = end - start
    required = _required_top_lap(member, original["diameter_mm"])
    assert length - 2 * end_tol >= required
    all_bars = [*member["bars"], partner]
    artefacts = nominal_artifacts(
        request, _takeoff(request, all_bars, original, partner, (start, end))
    )
    paths = artefacts["drawing"]["bar_extents_mm"]
    diameters = {bar["bar_id"]: bar["diameter_mm"] for bar in all_bars}
    supports = _support_evidence(
        member, acceptance, capacities, paths, diameters, detailed=True
    )
    shortened = {bar: [a + end_tol, b - end_tol] for bar, (a, b) in paths.items()}
    # Both transfer layouts are rectangular and have the same web resistance.
    lower_web = {
        name: {"bottom_web": {"capacity_knm": adverse["bottom"]["capacity_knm"]}}
        for name in arrangement
    }
    adverse_supports = _support_evidence(
        member, acceptance, lower_web, shortened, diameters, detailed=True
    )
    lap_cover = (
        original["y_from_top_mm"]
        - depth_tol
        - (original["diameter_mm"] + basis["longitudinal_diameter_allowance_mm"]) / 2
    )
    assert lap_cover >= 2 * original["diameter_mm"]
    continuous_top = [
        bar for bar in member["bars"] if bar["bar_id"] in ("T1-1", "T1-2")
    ]
    inflections = [
        next(site["x_mm"] for site in member["stations"] if site["station_id"] == name)
        for name in ("INFLECTION-LEFT", "INFLECTION-RIGHT")
    ]
    assert all(
        math.isclose(_span_actions(load, x, right_span=x > 4000)[0], 0, abs_tol=1e-10)
        for load in loads.values()
        for x in inflections
    )
    continuity_fraction = sum(bar["diameter_mm"] ** 2 for bar in continuous_top) / sum(
        bar["diameter_mm"] ** 2 for bar in member["bars"] if bar["face"] == "top"
    )
    extension = min(
        min(
            inflections[0] - shortened[bar["bar_id"]][0],
            shortened[bar["bar_id"]][1] - inflections[1],
        )
        for bar in continuous_top
    )
    clear_spans = [
        right["centre_mm"]
        - right["width_mm"] / 2
        - left["centre_mm"]
        - left["width_mm"] / 2
        for left, right in zip(member["supports"], member["supports"][1:], strict=False)
    ]
    extension_required = max(
        member["depth_mm"] - original["y_from_top_mm"] + depth_tol,
        12 * max(bar["diameter_mm"] for bar in continuous_top),
        max(clear_spans) / 16,
    )
    assert continuity_fraction >= 1 / 3 and extension >= extension_required
    credit = {
        name: {
            face: sorted(
                mark
                for mark, force in section[face]["bar_net_forces_n"].items()
                if force > 0
            )
            for face in ("bottom", "top")
        }
        for name, section in capacities.items()
    }
    assert original["bar_id"] in credit["upstream"]["bottom"]
    assert partner["bar_id"] in credit["downstream"]["bottom"]
    assert all(
        set(marks) <= set(SEATS.values())
        for faces in credit.values()
        for marks in faces.values()
    )
    return {
        "minimum_overlap_mm": length - 2 * end_tol,
        "nominal_required_lap_mm": required,
        "nominal_overlap_mm": length,
        "minimum_lap_cover_mm": lap_cover,
        "minimum_straight_support_development_mm": min(
            row["straight_available_mm"] for row in adverse_supports.values()
        ),
        "nominal_governing_acceptance_rows": {
            "sagging": _governing(acceptance, "flexure_utilization", "bottom"),
            "hogging": _governing(acceptance, "flexure_utilization", "top"),
            "shear": _governing(acceptance, "shear_utilization"),
        },
        "expanded_lap": {
            "stations_mm": list(expanded),
            "moments_knm": window,
            "maximum_required_knm": max(abs(values[-1]) for values in window.values()),
            "half_capacity_knm": half_capacity,
        },
        "spliced_top_area_fraction": original["diameter_mm"] ** 2
        / sum(
            bar["diameter_mm"] ** 2 for bar in member["bars"] if bar["face"] == "top"
        ),
        "spliced_top_bar_fraction": 1
        / sum(bar["face"] == "top" for bar in member["bars"]),
        "negative_steel_continuity": {
            "bar_ids": [bar["bar_id"] for bar in continuous_top],
            "area_fraction": continuity_fraction,
            "minimum_extension_mm": extension,
            "required_extension_mm": extension_required,
            "inflection_stations_mm": inflections,
        },
        "support_anchorage": supports,
        "adverse_support_anchorage": adverse_supports,
        "compression_bar_ids_by_tension_face": credit,
        "worst_strength": adverse,
        **artefacts,
    }


def _control_result(request, placement, loads, start, end):
    member, lap = request["member"], request["lap"]
    if member["current_analysis_revision"] != member["analysis_revision"]:
        return {"status": "HOLD", "required_issue_codes": ["BEAM_ANALYSIS_STALE"]}
    required_rows = {
        (combination["combination_id"], station)
        for combination in member["combinations"]
        for station in combination["required_station_ids"]
    }
    supplied_rows = {
        (row["combination_id"], row["station_id"]) for row in member["actions"]
    }
    if required_rows != supplied_rows:
        return {"status": "HOLD", "required_issue_codes": ["BEAM_ACTION_MISSING"]}
    if placement is not None:
        end_tolerance = placement["bar_end_tolerance_mm"]
        expanded = (start - end_tolerance, end + end_tolerance)
        if not set(expanded) <= {site["x_mm"] for site in member["stations"]}:
            return {"status": "HOLD", "required_issue_codes": ["BEAM.LAP_ACTIONS_HELD"]}
    else:
        expanded = (start, end)
    if any(_span_actions(load, expanded[0])[0] >= 0 for load in loads.values()):
        return {
            "status": "HOLD",
            "required_issue_codes": ["BEAM.LAP_TENSION_BASIS_HELD"],
        }
    if not {3000, 5000} <= {site["x_mm"] for site in member["stations"]}:
        return {"status": "HOLD", "required_issue_codes": ["BEAM.LAP_CONTINUITY_HELD"]}
    original = next(bar for bar in member["bars"] if bar["bar_id"] == lap["bar_id"])
    required_length = _required_top_lap(member, original["diameter_mm"])
    if end - start < required_length:
        return {"status": "FAIL", "required_issue_codes": ["SPLICE.NONCOMPLIANT"]}
    arrangement, partner = layouts(member, lap)
    if (
        abs(partner["x_from_left_mm"] - original["x_from_left_mm"])
        - original["diameter_mm"]
        < 25
    ):
        return {"status": "FAIL", "required_issue_codes": ["SPACING.HORIZONTAL"]}
    _, _, capacities = _strengths(member, arrangement)
    if (
        max(abs(_span_actions(load, end)[0]) for load in loads.values())
        > capacities["upstream"]["top"]["capacity_knm"] / 2
    ):
        return {"status": "FAIL", "required_issue_codes": ["BEAM.LAP_MOMENT_LIMIT"]}
    fit = placement_geometry(request, placement, seat_ids=SEATS)
    if fit["status"] != "PASS":
        return fit
    if end - start - 2 * placement["bar_end_tolerance_mm"] < required_length:
        return {
            "status": "FAIL",
            "required_issue_codes": ["BEAM.LAP_PLACEMENT_LENGTH_FAIL"],
        }
    return fit


def fixture():
    parent = json.loads(SOURCE.read_text())["cases"]["rectangular_lap"]
    cases = {}
    dispositions = {
        "support_top_lap": "PASS",
        "short_overlap": "FAIL",
        "short_after_tolerance": "FAIL",
        "congested_partner": "FAIL",
        "high_lap_moment": "FAIL",
        "bend_interference": "FAIL",
        "wrong_lap_sign": "HOLD",
        "wrong_expanded_sign": "HOLD",
        "missing_tolerance_station": "HOLD",
        "missing_continuity_station": "HOLD",
        "missing_lap_action": "HOLD",
        "stale_analysis": "HOLD",
        "restraint_sector": "HOLD",
        "missing_placement": "HOLD",
    }
    for name, status in dispositions.items():
        request, loads, start, end = _revised_request(parent["request"], name)
        basis = deepcopy(parent["placement"])
        if name == "bend_interference":
            basis["bar_axis_tolerance_mm"] = 4
        if name == "missing_placement":
            basis = None
        target = _control_result(request, basis, loads, start, end)
        assert target["status"] == status, (name, target)
        entry = {"request": request, "placement": basis, "expected": target}
        if status == "PASS":
            entry.update(_nominal_cage(request, basis, loads, start, end))
        cases[name] = entry
    return {
        "fixture_version": "library-030-beam05-support-top-lap-reference/v1",
        "frozen_before_implementation": True,
        "frozen_production_base": BASE,
        "bound_sources": {SOURCE.name: sha256(SOURCE.read_bytes()).hexdigest()},
        "code_basis": [
            "IS 456:2000 §§26.2.3.4, 26.2.5.1, 26.3.2, 26.5.1.2 and 26.5.3.2.",
            "SP 34:1987 Fig. 8.8B exterior closed link with one fully nested closed link.",
        ],
        "scope": [
            "Ordinary non-ductile rectangular web. One top Ø16 tension lap in the first clear span adjacent to support B.",
            "The signed analytic window includes both end tolerances; check the two transfer cages separately.",
            "The top pieces can be credited as compression bars in sagging beyond the lap. Retain both physical link grids throughout.",
            "The project cage uses the stated fit bounds. Adjacent beams, slab bars and support reinforcement need their own clash evidence.",
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
            f"PASS independent BEAM05 support top lap {name}: {case['expected']['status']}"
        )


if __name__ == "__main__":
    main()
