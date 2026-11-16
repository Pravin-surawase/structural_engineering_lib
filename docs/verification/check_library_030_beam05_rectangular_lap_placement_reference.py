"""Freeze the first-span rectangular lap on the checked placement topology."""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

from check_library_030_beam05_lap_placement_reference import (
    nominal_artifacts,
    placement_geometry,
    worst_strength,
)
from check_library_030_beam05_t_lap_reference import _span_actions, expected

HERE = Path(__file__).resolve().parent
RECTANGLE = HERE / "library-030-beam05-layered-lap.json"
PLACEMENT = HERE / "library-030-beam05-lap-placement-reference.json"
TARGET = HERE / "library-030-beam05-rectangular-lap-placement-reference.json"
BASE = "5b4eaed52b2d7d894a68b9457ec0849e4cc6218e"


def _control(request, basis, name):
    control = deepcopy(request)
    member = control["member"]
    control["identity"]["case_id"] = name
    member["reinforcement_revision"] += f"-{name}"
    geometric_basis = deepcopy(basis)
    if name == "short_overlap":
        # 800 mm overlap, with the supplied three-moment statics at both
        # edited stations. Ends stay in the positive moment region.
        sites = {"LAP-MID": 1950, "LAP-END": 2350}
        for station in member["stations"]:
            location = sites.get(station["station_id"])
            if location is not None:
                station["x_mm"] = location
        for row in member["actions"]:
            location = sites.get(row["station_id"])
            if location is not None:
                load = {"U1": 24, "U2": 32}[row["combination_id"]]
                row["mu_knm"], row["vu_kn"] = _span_actions(load, location)
    elif name == "congested_partner":
        control["lap"]["partner_x_from_left_mm"] = 150
    elif name == "missing_lap_action":
        member["actions"] = [
            row for row in member["actions"] if row["row_id"] != "U2:LAP-MID"
        ]
    elif name == "stale_analysis":
        member["current_analysis_revision"] += "-EDITED"
    elif name == "bend_interference":
        geometric_basis["bar_axis_tolerance_mm"] = 4
    elif name == "restraint_sector":
        next(bar for bar in member["bars"] if bar["bar_id"] == "T1-3")[
            "x_from_left_mm"
        ] = 122
    elif name == "missing_placement":
        geometric_basis = None
    return control, geometric_basis


def fixture():
    rectangle = json.loads(RECTANGLE.read_text())["cases"]["layered_lap"]["request"]
    flanged = json.loads(PLACEMENT.read_text())["cases"]["l_lap"]
    source = flanged["request"]
    request = deepcopy(rectangle)
    member = request["member"]
    assert member.get("flange") is None
    assert all(
        member[field] == source["member"][field]
        for field in (
            "width_mm",
            "depth_mm",
            "fck_nmm2",
            "fy_nmm2",
            "supports",
            "stations",
            "actions",
            "combinations",
            "straight_bars",
            "aggregate_size_mm",
            "link_spacing_mm",
            "link_diameter_mm",
            "link_fy_nmm2",
        )
    )
    member["bars"] = deepcopy(source["member"]["bars"])
    member["clear_cover_mm"] = source["member"]["clear_cover_mm"]
    member["reinforcement_revision"] += "-PLACEMENT"
    request["link_detail"] = deepcopy(source["link_detail"])
    request["lap"] = deepcopy(source["lap"])
    request["identity"]["case_id"] = "rectangular_lap"
    basis = deepcopy(flanged["placement"])
    result = expected(request)
    geometry = placement_geometry(request, basis)
    assert result["status"] == geometry["status"] == "PASS"
    assert result["physical_width_mm"] == member["width_mm"]
    assert result["effective_flange_width_mm"] is None
    assert {
        point["x_from_left_mm"] for point in member["bars"] if point["layer"] == 2
    } == {66, 234}
    assert request["lap"]["bar_id"] == "B1-2"
    end_tolerance = basis["bar_end_tolerance_mm"]
    min_overlap = result["overlap_mm"] - 2 * end_tolerance
    min_development = (
        min(
            row["straight_available_mm"] for row in result["support_anchorage"].values()
        )
        - end_tolerance
    )
    assert min(min_overlap, min_development) >= result["required_lap_mm"]
    cases = {
        "rectangular_lap": {
            "request": request,
            "placement": basis,
            "expected": geometry,
            "nominal_governing_acceptance_rows": result["governing_acceptance_rows"],
            "nominal_overlap_mm": result["overlap_mm"],
            "nominal_required_lap_mm": result["required_lap_mm"],
            "minimum_overlap_mm": min_overlap,
            "minimum_straight_support_development_mm": min_development,
            "worst_strength": worst_strength(request, basis, result),
            **nominal_artifacts(request, result),
        }
    }
    early_controls = {
        "short_overlap": ("FAIL", "SPLICE.NONCOMPLIANT"),
        "congested_partner": ("FAIL", "SPACING.HORIZONTAL"),
        "missing_lap_action": ("HOLD", "BEAM_ACTION_MISSING"),
        "stale_analysis": ("HOLD", "BEAM_ANALYSIS_STALE"),
    }
    for name, (status, code) in early_controls.items():
        control, placement = _control(request, basis, name)
        target = expected(control)
        assert target["status"] == status and code in target["required_issue_codes"]
        cases[name] = {
            "request": control,
            "placement": placement,
            "expected": {"status": status, "required_issue_codes": [code]},
        }
    fit_controls = {
        "bend_interference": ("FAIL", "placement_interference"),
        "restraint_sector": ("HOLD", "restraint_sector_unresolved"),
        "missing_placement": ("HOLD", "placement_basis_missing"),
    }
    for name, (status, issue) in fit_controls.items():
        control, placement = _control(request, basis, name)
        target = placement_geometry(control, placement)
        assert (target["status"], target["issue"]) == (status, issue)
        cases[name] = {"request": control, "placement": placement, "expected": target}
    return {
        "fixture_version": "library-030-beam05-rectangular-lap-placement-reference/v1",
        "frozen_before_implementation": True,
        "frozen_production_base": BASE,
        "bound_sources": {
            path.name: sha256(path.read_bytes()).hexdigest()
            for path in (RECTANGLE, PLACEMENT)
        },
        "scope": [
            "Use the original rectangular web, support geometry and signed actions. Use the flanged reference's nominal web cage and declared placement limits.",
            "The four exterior corners are continuous. The two inner bottom bars align with the exterior bottom corners. Only the one intermediate Ø20 bar laps.",
            "The nested closed link restrains the intermediate lap pieces and two continuous top bars. Credit only the exterior links in shear. Compare all eight adverse depth-endpoint combinations.",
            "Coordinates, the link grids, assembly and cover limits apply to the declared unobstructed web. Project support obstructions need separate evidence.",
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
    for name, entry in data["cases"].items():
        print(
            f"PASS independent BEAM05 rectangular placement {name}: {entry['expected']['status']}"
        )


if __name__ == "__main__":
    main()
