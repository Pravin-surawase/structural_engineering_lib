"""Freeze an ordinary three-zone link specimen without importing the library."""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from pathlib import Path

FIXTURE = Path(__file__).with_name("library-030-beam05-varied-links.json")
SPAN_M = 4.0
POINT_X_M = 3.75
WIDTH_MM, DEPTH_MM, COVER_MM = 250, 600, 30
BAR_DIA_MM, LINK_DIA_MM = 20, 8
CORNER_OFFSET_MM = COVER_MM + LINK_DIA_MM + BAR_DIA_MM / 2
DEPTH_EFFECTIVE_MM = DEPTH_MM - CORNER_OFFSET_MM
LINK_RADIUS_MM, VERTEX_LEG_MM, HOOK_OFFSET_MM = 10, 100, 10
STEEL_AREA_MM2 = 2 * math.pi * BAR_DIA_MM**2 / 4
LINK_AREA_MM2 = 2 * math.pi * LINK_DIA_MM**2 / 4
TAU_C_NMM2 = 0.37 + (0.50 - 0.37) / 0.25 * (
    100 * STEEL_AREA_MM2 / (WIDTH_MM * DEPTH_EFFECTIVE_MM) - 0.25
)
MAX_PITCH_MM = min(
    300,
    WIDTH_MM,
    0.75 * DEPTH_EFFECTIVE_MM,
    0.87 * 415 * LINK_AREA_MM2 / (0.4 * WIDTH_MM),
    16 * BAR_DIA_MM,
)


def _zone(zone_id, start, end, pitch, include_start=True):
    return {
        "zone_id": zone_id,
        "start_station_mm": start,
        "end_station_mm": end,
        "spacing_mm": pitch,
        "include_start": include_start,
        "include_end": True,
    }


ZONES = [
    _zone("LEFT", 0, 2000, 250),
    _zone("INTERIOR", 2000, 6000, 100, False),
    _zone("RIGHT", 6000, 8000, 250, False),
]
UNIFORM = [_zone("UNIFORM", 0, 8000, 250)]


def _stations():
    dense_sag_peak = _left_reaction(32, 145) / 32 * 1000
    definitions = (
        ("A", 0, "RIGHT"),
        ("A-FACE", 500, "CONTINUOUS"),
        ("SAG-LEFT", 1500, "CONTINUOUS"),
        ("SAG-LEFT-DENSE", dense_sag_peak, "CONTINUOUS"),
        ("ZONE-LEFT", 2000, "CONTINUOUS"),
        ("PL-IN", 3750, "LEFT"),
        ("PL-OUT", 3750, "RIGHT"),
        ("B-LEFT-FACE", 3850, "CONTINUOUS"),
        ("B-LEFT", 4000, "LEFT"),
        ("B-RIGHT", 4000, "RIGHT"),
        ("B-RIGHT-FACE", 4150, "CONTINUOUS"),
        ("PR-IN", 4250, "LEFT"),
        ("PR-OUT", 4250, "RIGHT"),
        ("ZONE-RIGHT", 6000, "CONTINUOUS"),
        ("SAG-RIGHT", 6500, "CONTINUOUS"),
        ("SAG-RIGHT-DENSE", 8000 - dense_sag_peak, "CONTINUOUS"),
        ("C-FACE", 7500, "CONTINUOUS"),
        ("C", 8000, "LEFT"),
    )
    return [
        {"station_id": name, "x_mm": x_mm, "side": side}
        for name, x_mm, side in definitions
    ]


def _left_reaction(w, point):
    # Mirror symmetry sets the slope at B to zero. Integrating x*M(x) over
    # the left span gives the internal support moment from the simple-span
    # UDL parabola and concentrated-load triangle. End reactions then follow
    # from equilibrium.
    L, a = SPAN_M, POINT_X_M
    m_b = -w * L**2 / 8 - point * a * (L**2 - a**2) / (2 * L**2)
    return w * L / 2 + point * (L - a) / L + m_b / L


def _actions(x_mm, side, w, point):
    a = POINT_X_M
    reaction = _left_reaction(w, point)
    # Mirror the left span to recover signed right shear.
    reflected = x_mm > 4000 or (x_mm == 4000 and side == "RIGHT")
    x = (8000 - x_mm if reflected else x_mm) / 1000
    after_load = x > a or (x == a and side == ("LEFT" if reflected else "RIGHT"))
    m = reaction * x - w * x**2 / 2 - point * max(0, x - a)
    v = reaction - w * x - (point if after_load else 0)
    return m, -v if reflected else v


def _request(case_id, *, point_loads):
    member_id = "B-ZONES"
    stations = _stations()
    combinations = [
        {
            "combination_id": name,
            "kind": "ULS",
            "required_station_ids": [station["station_id"] for station in stations],
        }
        for name in ("U1", "U2")
    ]
    actions = []
    for combination, w, point in zip(("U1", "U2"), (24, 32), point_loads, strict=True):
        for station in stations:
            moment, shear = _actions(station["x_mm"], station["side"], w, point)
            station_id = station["station_id"]
            actions.append(
                {
                    "row_id": f"{combination}:{station_id}",
                    "combination_id": combination,
                    "station_id": station_id,
                    "mu_knm": moment,
                    "vu_kn": shear,
                    "tu_knm": 0,
                }
            )
    bars = [
        {
            "bar_id": f"{prefix}{i}",
            "face": face,
            "diameter_mm": BAR_DIA_MM,
            "x_from_left_mm": x,
            "y_from_top_mm": y,
        }
        for face, prefix, y in (
            ("top", "T", CORNER_OFFSET_MM),
            ("bottom", "B", DEPTH_EFFECTIVE_MM),
        )
        for i, x in enumerate((CORNER_OFFSET_MM, WIDTH_MM - CORNER_OFFSET_MM), 1)
    ]
    return {
        "identity": {"family_id": "beam", "case_id": case_id, "member_id": member_id},
        "member": {
            "schema_version": "is456-continuous-beam-check/v1",
            "member_id": member_id,
            "analysis_revision": "ZONES-A1",
            "current_analysis_revision": "ZONES-A1",
            "reinforcement_revision": "ZONES-D1",
            "source_reference": "Independent two-span factored load and station worksheet",
            "width_mm": WIDTH_MM,
            "depth_mm": DEPTH_MM,
            "clear_cover_mm": COVER_MM,
            "aggregate_size_mm": 20,
            "fck_nmm2": 30,
            "fy_nmm2": 500,
            "link_diameter_mm": LINK_DIA_MM,
            "link_fy_nmm2": 415,
            "link_spacing_mm": 250,
            "bars": bars,
            "straight_bars": {
                "start_mm": -460,
                "end_mm": 8460,
                "source_reference": "Uninterrupted straight bars from A to C",
            },
            "supports": [
                {"support_id": "A", "centre_mm": 0, "width_mm": 1000},
                {"support_id": "B", "centre_mm": 4000, "width_mm": 300},
                {"support_id": "C", "centre_mm": 8000, "width_mm": 1000},
            ],
            "stations": stations,
            "combinations": combinations,
            "actions": actions,
        },
        "link_detail": {
            "first_station_mm": 0,
            "last_station_mm": 8000,
            "internal_bend_radius_mm": LINK_RADIUS_MM,
            "hook_vertex_leg_mm": VERTEX_LEG_MM,
            "hook_plane_offset_mm": HOOK_OFFSET_MM,
            "source_reference": "One fabricated ordinary closed shape with separated 90-degree hooks",
        },
        "stock_length_mm": 12000,
    }


def _capacity(pitch_mm):
    concrete = TAU_C_NMM2 * WIDTH_MM * DEPTH_EFFECTIVE_MM / 1000
    steel = 0.87 * 415 * LINK_AREA_MM2 * DEPTH_EFFECTIVE_MM / pitch_mm / 1000
    return min(concrete + steel, 3.5 * WIDTH_MM * DEPTH_EFFECTIVE_MM / 1000)


def _grid(zone):
    start, end, pitch = (
        zone["start_station_mm"],
        zone["end_station_mm"],
        zone["spacing_mm"],
    )
    assert (end - start) % pitch == 0
    return list(
        range(
            start if zone["include_start"] else start + pitch,
            end + int(zone["include_end"]),
            pitch,
        )
    )


def _reference(request, zones):
    member = request["member"]
    stations = {row["station_id"]: row for row in member["stations"]}
    rows = [
        row
        for row in member["actions"]
        if stations[row["station_id"]]["x_mm"] not in (0, 4000, 8000)
    ]
    zone_rows = []
    for zone in zones:
        start, end, pitch = (
            zone["start_station_mm"],
            zone["end_station_mm"],
            zone["spacing_mm"],
        )
        applicable = [
            row for row in rows if start <= stations[row["station_id"]]["x_mm"] <= end
        ]
        governing = min(applicable, key=lambda row: (-abs(row["vu_kn"]), row["row_id"]))
        grid = _grid(zone)
        zone_rows.append(
            {
                "zone_id": zone["zone_id"],
                "spacing_mm": pitch,
                "stations_mm": grid,
                "quantity": len(grid),
                "capacity_kn": _capacity(pitch),
                "governing_row_id": governing["row_id"],
                "governing_shear_kn": governing["vu_kn"],
                "governing_ratio": abs(governing["vu_kn"]) / _capacity(pitch),
            }
        )
    transitions = []
    for left, right in zip(zones, zones[1:]):
        boundary = left["end_station_mm"]
        assert left["include_end"] != right["include_start"]
        relevant = [
            row for row in rows if stations[row["station_id"]]["x_mm"] == boundary
        ]
        for row in relevant:
            transitions.append(
                {
                    "station_mm": boundary,
                    "row_id": row["row_id"],
                    "shear_kn": row["vu_kn"],
                    "owner_zone_id": (
                        left["zone_id"] if left["include_end"] else right["zone_id"]
                    ),
                    "adjacent": [
                        {
                            "zone_id": zone["zone_id"],
                            "spacing_mm": zone["spacing_mm"],
                            "capacity_kn": _capacity(zone["spacing_mm"]),
                            "shear_ratio": abs(row["vu_kn"])
                            / _capacity(zone["spacing_mm"]),
                        }
                        for zone in (left, right)
                    ],
                }
            )
    links = [x for row in zone_rows for x in row["stations_mm"]]
    assert len(links) == len(set(links))
    inset = COVER_MM + LINK_DIA_MM / 2
    width, height = WIDTH_MM - 2 * inset, DEPTH_MM - 2 * inset
    bend_radius = LINK_RADIUS_MM + LINK_DIA_MM / 2
    cut = (
        2 * VERTEX_LEG_MM
        + width
        + 2 * height
        + math.hypot(width, HOOK_OFFSET_MM)
        + 5 * bend_radius * (math.pi / 2 - 2)
    )
    mass_factor = math.pi / 4 * 7850e-9
    return {
        "status": (
            "PASS"
            if all(zone["governing_ratio"] <= 1 for zone in zone_rows)
            else "FAIL"
        ),
        "zones": zone_rows,
        "transitions": transitions,
        "drawing": {
            "bar_axes_mm": {
                bar["bar_id"]: [bar["x_from_left_mm"], bar["y_from_top_mm"]]
                for bar in member["bars"]
            },
            "link_stations_mm": links,
        },
        "bbs": {
            "link_count": len(links),
            "link_cut_mm": cut,
            "longitudinal_count": 4,
            "longitudinal_cut_mm": 8920,
            "mass_kg": mass_factor
            * (len(links) * cut * LINK_DIA_MM**2 + 4 * 8920 * BAR_DIA_MM**2),
        },
    }


def fixture():
    uniform = _request("BEAM05-uniform-links", point_loads=(0, 0))
    varied = _request("BEAM05-varied-links", point_loads=(0, 0))
    dense = _request("BEAM05-varied-links-point-loads", point_loads=(108.75, 145))
    varied["link_zones"] = deepcopy(ZONES)
    dense["link_zones"] = deepcopy(ZONES)
    coarse = deepcopy(dense)
    del coarse["link_zones"]
    coarse["identity"]["case_id"] = "BEAM05-uniform-links-point-loads"
    cases = {
        "uniform": {"request": uniform, "expected": _reference(uniform, UNIFORM)},
        "varied": {"request": varied, "expected": _reference(varied, ZONES)},
        "dense_required": {"request": dense, "expected": _reference(dense, ZONES)},
        "uniform_with_point_loads": {
            "request": coarse,
            "expected": {
                **_reference(coarse, UNIFORM),
                "required_issue_codes": ["BEAM_SECTION_FAIL"],
            },
        },
    }
    for name, status, code in (
        ("overpitch", "FAIL", "BEAM.LINK_ZONE_PITCH_FAIL"),
        ("duplicate_boundary", "FAIL", "BEAM.LINK_ZONE_PLACEMENT_FAIL"),
        ("right_transition_overload", "FAIL", "BEAM_SECTION_FAIL"),
        ("missing_zone_plan", "HOLD", "BEAM.LINK_ZONE_BASIS_HELD"),
        ("missing_transition", "HOLD", "BEAM.LINK_ZONE_TRANSITION_ACTIONS_HELD"),
        ("stale_actions", "HOLD", "BEAM_ANALYSIS_STALE"),
    ):
        request = deepcopy(varied)
        request["identity"]["case_id"] = f"BEAM05-{name.replace('_', '-')}"
        if name == "overpitch":
            request["link_zones"][0]["spacing_mm"] = 400
            assert 400 > MAX_PITCH_MM and len(_grid(request["link_zones"][0])) == 6
        elif name == "duplicate_boundary":
            request["link_zones"][1]["include_start"] = True
            assert (
                _grid(request["link_zones"][0])[-1]
                == _grid(request["link_zones"][1])[0]
            )
        elif name == "right_transition_overload":
            # A synthetic row isolates the two-pitch decision. At 6000 the
            # INTERIOR zone owns the link, while RIGHT has the weaker check.
            action = next(
                row
                for row in request["member"]["actions"]
                if row["row_id"] == "U2:ZONE-RIGHT"
            )
            action["vu_kn"] = 180
            assert _capacity(250) < action["vu_kn"] < _capacity(100)
        elif name == "missing_zone_plan":
            request["link_zones"] = None
        elif name == "missing_transition":
            member = request["member"]
            member["stations"] = [
                row for row in member["stations"] if row["station_id"] != "ZONE-RIGHT"
            ]
            member["actions"] = [
                row for row in member["actions"] if row["station_id"] != "ZONE-RIGHT"
            ]
            for combination in member["combinations"]:
                combination["required_station_ids"].remove("ZONE-RIGHT")
        else:
            request["member"]["current_analysis_revision"] = "ZONES-A2"
        cases[name] = {
            "request": request,
            "expected": {"status": status, "required_issue_codes": [code]},
        }
        if name == "right_transition_overload":
            cases[name]["expected"]["transitions"] = _reference(request, ZONES)[
                "transitions"
            ]
    assert cases["uniform"]["expected"]["bbs"]["link_count"] == 33
    assert cases["varied"]["expected"]["bbs"]["link_count"] == 57
    assert [z["quantity"] for z in cases["varied"]["expected"]["zones"]] == [9, 40, 8]
    assert cases["dense_required"]["expected"]["status"] == "PASS"
    assert cases["uniform_with_point_loads"]["expected"]["status"] == "FAIL"
    clear_face_spacing = WIDTH_MM - 2 * CORNER_OFFSET_MM - BAR_DIA_MM
    assert 25 <= clear_face_spacing <= 150
    return {
        "fixture_version": "library-030-beam05-varied-links/v1",
        "sources": [
            "Symmetric elastic two-span equilibrium and zero rotation at support B.",
            "IS 456:2000 clauses 26.3.2–3, 26.5.1.5–6, 26.5.3.2, 40.2–4 and Tables 15, 19 and 20.",
            "Ordinary rounded centreline tangent lengths and discrete link ownership.",
        ],
        "effective_depth_mm": DEPTH_EFFECTIVE_MM,
        "maximum_pitch_mm": MAX_PITCH_MM,
        "clear_spacing_mm": clear_face_spacing,
        "maximum_clear_spacing_mm": 150,
        "cases": cases,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    data = fixture()
    encoded = json.dumps(data, indent=2, allow_nan=False) + "\n"
    if parser.parse_args().freeze:
        FIXTURE.write_text(encoded, encoding="utf-8")
    else:
        assert FIXTURE.read_text(encoding="utf-8") == encoded
    for case, row in data["cases"].items():
        print(f"Independent BEAM05 varied-link {case}: {row['expected']['status']}")


if __name__ == "__main__":
    main()
