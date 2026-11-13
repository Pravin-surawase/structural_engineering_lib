"""Independent exhaustive reference for the COL06 supplied column catalogue."""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from functools import cache
from itertools import product
from pathlib import Path

from check_library_029_col02_reference import axis_reference
from check_library_029_col03_reference import verify_values

FIXTURE = Path(__file__).with_name("library-029-col06-column-catalogue.json")


def _tie(option_id, diameter, pitch, bend, tail, offsets):
    return {
        "option_id": option_id,
        "tie": {
            "tie_id": f"H-{option_id}",
            "diameter_mm": diameter,
            "spacing_mm": pitch,
            "internal_bend_radius_mm": bend,
            "closed": True,
            "hook_angle_deg": 135,
            "hook_tail_mm": tail,
        },
        "cross_ties": [
            {
                "tie_id": "XT",
                "restrained_bar_ids": ["M_LEFT", "M_RIGHT"],
                "station_offset_mm": offsets[0],
            },
            {
                "tie_id": "YT",
                "restrained_bar_ids": ["M_TOP", "M_BOTTOM"],
                "station_offset_mm": offsets[1],
            },
        ],
    }


def requests():
    member = {
        "unsupported_length_mm": 3000,
        "end_condition": "FIXED_FIXED",
        "braced": True,
    }
    base = {
        "member": member,
        "materials": {"fck_nmm2": 25, "fy_nmm2": 415},
        "detailing": {
            "nominal_cover_mm": 40,
            "project_required_cover_mm": 40,
            "corner_inset_mm": 2,
            "aggregate_size_mm": 20,
            "project_required_bend_radius_mm": 10,
            "detailing_basis_reference": "COL06 supplied local bend and link schedule",
        },
        "analysis": {
            "geometry": {**member, "b_mm": 300, "D_mm": 400},
            "fck_nmm2": 25,
            "analysis_revision": "analysis-01",
            "current_analysis_revision": "analysis-01",
            "stiffness_basis": "gross_section",
        },
        "sizes": [
            {"size_id": "R300x400", "b_mm": 300, "D_mm": 400},
            {"size_id": "R350x450", "b_mm": 350, "D_mm": 450},
            {"size_id": "R400x500", "b_mm": 400, "D_mm": 500},
        ],
        "longitudinal_diameters_mm": [16, 20, 25],
        "tie_options": [
            _tie("T08-P150", 8, 150, 10, 48, (12, 24)),
            _tie("T08-P300", 8, 300, 10, 48, (12, 24)),
            _tie("T10-P200", 10, 200, 13, 60, (14, 28)),
        ],
        "actions": [
            {
                "combination_id": "U1",
                "pu_kn": 500,
                "mx_knm": 50,
                "my_knm": 35,
                "check_station_mm": 1500,
            },
        ],
    }
    names = (
        "nominal",
        "reordered",
        "multiple_combinations",
        "changed_size",
        "stale_analysis",
        "reinforcement_dependent",
        "budget_exhausted",
        "no_feasible",
        "missing_restraint",
        "colliding_links",
    )
    rows = {name: deepcopy(base) for name in names}
    for name, request in rows.items():
        request["identity"] = {
            "family_id": "column",
            "member_id": "COL06-C",
            "case_id": name,
            "source_reference": "COL06 independent catalogue worksheet",
        }
    for key in ("sizes", "longitudinal_diameters_mm", "tie_options"):
        rows["reordered"][key].reverse()
    rows["multiple_combinations"]["actions"].insert(
        0,
        {
            "combination_id": "U2",
            "pu_kn": 500,
            "mx_knm": -75,
            "my_knm": 55,
            "check_station_mm": 750,
        },
    )
    rows["changed_size"]["analysis"]["geometry"].update(b_mm=400, D_mm=500)
    rows["stale_analysis"]["analysis"]["current_analysis_revision"] = "analysis-02"
    rows["reinforcement_dependent"]["analysis"][
        "stiffness_basis"
    ] = "reinforcement_dependent"
    rows["budget_exhausted"]["evaluation_limit"] = 2
    rows["no_feasible"]["actions"][0].update(mx_knm=400, my_knm=320)
    rows["missing_restraint"]["tie_options"][0]["cross_ties"].pop()
    rows["colliding_links"]["tie_options"][0]["cross_ties"][1]["station_offset_mm"] = 12
    return rows


@cache
def _strength(b, d, diameter, offset, fck, fy, pu, length):
    bars = {
        f"B{index}": xy
        for index, xy in enumerate(
            (
                (offset, offset),
                (b - offset, offset),
                (b - offset, d - offset),
                (offset, d - offset),
                (offset, d / 2),
                (b - offset, d / 2),
                (b / 2, offset),
                (b / 2, d - offset),
            )
        )
    }
    inputs = {
        "b_mm": b,
        "D_mm": d,
        "longitudinal_bar_diameter_mm": diameter,
        "fck_nmm2": fck,
        "fy_nmm2": fy,
        "pu_kn": pu,
    }
    capacities = [
        axis_reference(inputs, bars, axis)["capacity_knm"] for axis in ("x", "y")
    ]
    steel = 2 * math.pi * diameter**2
    puz = (0.45 * fck * (b * d - steel) + 0.75 * fy * steel) / 1000
    alpha = max(1, min(2, 1 + (pu / puz - 0.2) / 0.6))
    minimum = max(
        pu * max(20, length / 500 + size / 30) / 1000 / capacity
        for size, capacity in zip((d, b), capacities, strict=True)
    )
    return capacities, alpha, minimum


def _disposition(b, d, diameter, schedule, offset):
    # These exact fixtures share 40 cover and a 2 mm inset. Verify their
    # corner arcs and spacing separately, then distinguish hoop and link failures.
    hoop = schedule["tie"]
    dt, pitch = hoop["diameter_mm"], hoop["spacing_mm"]
    bend, tail = hoop["internal_bend_radius_mm"], hoop["hook_tail_mm"]
    spans = b - 2 * offset, d - 2 * offset
    steel_ratio = 2 * math.pi * diameter**2 / (b * d)
    r = diameter / 2
    # Circle inside the convex corner after inward erosion by the bar radius.
    corner = max(0, bend - r)
    enclosure = math.sqrt(2) * max(0, corner - 2) <= corner
    assert (
        enclosure and min(spans) / 2 - diameter >= 25 and 0.008 <= steel_ratio <= 0.04
    )
    assert dt >= max(6, diameter / 4) and tail >= 6 * dt
    assert 2 * bend + dt + tail <= min(b, d) - 80 - dt
    if pitch > min(300, b, d, 16 * diameter):
        return "FAIL", "COLUMN.TIE_SPACING"
    if any(span > 48 * dt for span in spans):
        return "FAIL", "COLUMN.MIDPOINT_RESTRAINT_SPAN"
    extent = bend + dt
    if bend < r or offset - extent < 40 or extent + tail > min(spans) / 2 - r:
        return "FAIL", "COLUMN.MIDPOINT_TIE_HOOK_FIT"
    offsets = (
        0,
        *sorted(link["station_offset_mm"] for link in schedule["cross_ties"]),
        pitch,
    )
    if (
        min(end - start for start, end in zip(offsets[:-1], offsets[1:], strict=True))
        < dt
    ):
        return "FAIL", "COLUMN.MIDPOINT_TIE_LEVELS"
    if len(schedule["cross_ties"]) != 2:
        return "HOLD", "COLUMN.MIDPOINT_TIE_REQUIRED"
    return "PASS", None


def reference(request):
    catalogue = []
    for size, diameter, schedule in product(
        request["sizes"], request["longitudinal_diameters_mm"], request["tie_options"]
    ):
        b, d = size["b_mm"], size["D_mm"]
        hoop = schedule["tie"]
        rank = (
            b * d,
            diameter**2,
            b,
            d,
            diameter,
            hoop["diameter_mm"],
            -hoop["spacing_mm"],
            schedule["option_id"],
            size["size_id"],
        )
        identifier = f'{size["size_id"]}/{diameter}/{schedule["option_id"]}'
        catalogue.append((rank, identifier, size, diameter, schedule))
    catalogue.sort()

    evaluated = {}
    for _, identifier, size, diameter, schedule in catalogue[
        : request.get("evaluation_limit", 128)
    ]:
        b, d = size["b_mm"], size["D_mm"]
        hoop = schedule["tie"]
        offset = 42 + hoop["diameter_mm"] + diameter / 2
        status, issue = _disposition(b, d, diameter, schedule, offset)
        expected = {
            "status": status,
            "bar_center_offset_mm": offset,
            "combinations": {},
        }
        if issue:
            expected["issue"] = issue
        for row in sorted(
            request["actions"], key=lambda action: action["combination_id"]
        ):
            outcome = {"status": status}
            if status == "PASS":
                (cap_x, cap_y), alpha, minimum = _strength(
                    b,
                    d,
                    diameter,
                    offset,
                    request["materials"]["fck_nmm2"],
                    request["materials"]["fy_nmm2"],
                    row["pu_kn"],
                    request["member"]["unsupported_length_mm"],
                )
                utilization = max(
                    minimum,
                    (abs(row["mx_knm"]) / cap_x) ** alpha
                    + (abs(row["my_knm"]) / cap_y) ** alpha,
                )
                outcome.update(
                    status="PASS" if utilization <= 1 else "FAIL",
                    utilization=utilization,
                )
            expected["combinations"][row["combination_id"]] = outcome
        outcomes = {row["status"] for row in expected["combinations"].values()}
        expected["status"] = (
            "FAIL" if "FAIL" in outcomes else "HOLD" if "HOLD" in outcomes else "PASS"
        )
        if status == "PASS":
            worst = max(row["utilization"] for row in expected["combinations"].values())
            governing = min(
                name
                for name, row in expected["combinations"].items()
                if row["utilization"] == worst
            )
            expected.update(governing_combination_id=governing, utilization=worst)
        evaluated[identifier] = expected

    eligible = [
        identifier for identifier, row in evaluated.items() if row["status"] == "PASS"
    ]
    complete = len(evaluated) == len(catalogue)
    selected = None
    analysis_status = None
    if not complete:
        terminal, engineering = "INCOMPLETE_BUDGET", "HOLD"
    elif any(row["status"] == "HOLD" for row in evaluated.values()):
        terminal, engineering = "BLOCKED_MANDATORY_CHECK", "HOLD"
    elif not eligible:
        terminal, engineering = "COMPLETE_INFEASIBLE", "FAIL"
    else:
        terminal = "COMPLETE_FEASIBLE"
        selected = eligible[0]
        _, _, size, _, _ = next(row for row in catalogue if row[1] == selected)
        analysis = request["analysis"]
        if analysis["analysis_revision"] != analysis["current_analysis_revision"]:
            analysis_status = "STALE_ANALYSIS"
        elif (size["b_mm"], size["D_mm"]) != (
            analysis["geometry"]["b_mm"],
            analysis["geometry"]["D_mm"],
        ) or analysis["stiffness_basis"] != "gross_section":
            analysis_status = "ANALYSIS_REFRESH_REQUIRED"
        else:
            analysis_status = "BOUND"
        engineering = "PASS" if analysis_status == "BOUND" else "HOLD"
    return {
        "terminal_state": terminal,
        "engineering_status": engineering,
        "catalogue_count": len(catalogue),
        "enumeration_complete": complete,
        "evaluated": evaluated,
        "eligible_ids": eligible,
        "selected_id": selected,
        "analysis_status": analysis_status,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--derive", action="store_true")
    args = parser.parse_args()
    cases = requests()
    if args.derive:
        fixture = {
            "schema_version": "library-029-col06-catalogue-reference/v1",
            "frozen_before_implementation": True,
            "frozen_production_base": "7df541042b44ad92c710ca59c14a90bd7fa55634",
            "sources": [
                "IS 456:2000 Cl. 25.4, 26.2.2.4(b), 26.3–26.5.3, 38.1, 39.1, 39.5 and 39.6.",
                "IIT Kharagpur Lesson 26 https://archive.nptel.ac.in/content/storage2/courses/105105104/pdf/m10l26.pdf",
            ],
            "method": "Enumerate the supplied sizes, bar diameters and tie schedules. Resolve cover, offset, fit and restraint independently. Integrate the COL02 strip reference at fixed compression on both axes and check each supplied combination. Order by gross area, steel area, b, D, bar diameter, tie diameter, larger pitch, then catalogue IDs. Only a fully resolved catalogue can return a selection.",
            "tolerances": {"utilization": 0.0001, "dimension_mm": 0.000001},
            "cases": {},
        }
    else:
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        assert set(cases) == set(fixture["cases"])
    for name, request in cases.items():
        expected = reference(request)
        if args.derive:
            fixture["cases"][name] = {"request": request, "expected": expected}
        else:
            assert request == fixture["cases"][name]["request"], name
            frozen = fixture["cases"][name]["expected"]
            for key in (
                "enumeration_complete",
                "eligible_ids",
                "selected_id",
                "analysis_status",
            ):
                assert expected.pop(key) == frozen[key], (name, key)
            assert tuple(expected["evaluated"]) == tuple(frozen["evaluated"])
            verify_values(expected, {key: frozen[key] for key in expected}, name)
            print(f"PASS independent COL06 {name}")
    if args.derive:
        print(json.dumps(fixture, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
