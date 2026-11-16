"""Independent nominal haunch geometry, signed strength and fabrication reference."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from copy import deepcopy
from itertools import pairwise
from pathlib import Path

from check_library_029_beam05_flanged_reference import TABLE_19
from check_library_029_beam_sections_reference import section

FIXTURE = Path(__file__).with_name("library-030-beam05-haunch.json")
OUTLINE = [
    (-500, 500),
    (3000, 500),
    (3600, 600),
    (4400, 600),
    (5000, 500),
    (8500, 500),
]
KNEES = tuple(x for x, _ in OUTLINE[1:-1])
WIDTH = 250
BAR_DIA, LINK_DIA = 20, 8
ABSCISSAE = (54, WIDTH - 54)
BAR_OFFSET = 56
BAR_BEND_RADIUS, LINK_RADIUS = 300, 22
LINK_AXIS = 36
HOOK_OFFSET, HOOK_VERTEX_LEG = 10, 100
PIECE_ENDS = (-460, 8460)
RUN, RISE = 600, 100
SLOPE = RISE / RUN
ANGLE = math.atan(SLOPE)
SECANT = math.hypot(1, SLOPE)
PITCH = 200
OUTWARD_AREA = math.pi * BAR_DIA**2 / 4
MAX_BAR_FORCE_KN = 0.87 * 500 * OUTWARD_AREA / 1000


def _depth(x):
    for (start, d1), (end, d2) in pairwise(OUTLINE):
        if start <= x <= end:
            return d1 + (d2 - d1) * (x - start) / (end - start)
    raise ValueError(f"Station {x} lies outside the concrete outline.")


def _soffit_slope(x, side):
    if (3000 < x < 3600) or (x, side) in ((3000, "RIGHT"), (3600, "LEFT")):
        return SLOPE
    if (4400 < x < 5000) or (x, side) in ((4400, "RIGHT"), (5000, "LEFT")):
        return -SLOPE
    return 0.0


def _rotation_integral(function, panels):
    """Composite Simpson integration split at both stiffness breakpoints."""
    result = 0.0
    for start, end in pairwise((0.0, 3.0, 3.6, 4.0)):
        h = (end - start) / panels
        for i in range(panels + 1):
            x = start + i * h
            weight = 1 if i in (0, panels) else 4 if i % 2 else 2
            result += h * weight / 3 * function(x) / (_depth(1000 * x) / 1000) ** 3
    return result


def _support_moment(w):
    # Mirror symmetry gives zero rotation at the interior support. With
    # constant E and width, only the cube of depth remains in 1/EI.
    def evaluate(panels):
        numerator = _rotation_integral(lambda x: w * x**2 * (4 - x) / 2, panels)
        denominator = _rotation_integral(lambda x: x**2 / 4, panels)
        return -numerator / denominator

    result = evaluate(800)
    assert abs(result - evaluate(400)) < 1e-9
    return result


def _actions(w, moment_b, name, station):
    is_right = station["x_mm"] > 4000 or (
        station["x_mm"] == 4000 and station["side"] == "RIGHT"
    )
    x = (8000 - station["x_mm"] if is_right else station["x_mm"]) / 1000
    reaction = 2 * w + moment_b / 4
    return {
        "row_id": f"{name}:{station['station_id']}",
        "combination_id": name,
        "station_id": station["station_id"],
        "mu_knm": reaction * x - w * x**2 / 2,
        "vu_kn": (reaction - w * x) * (-1 if is_right else 1),
        "tu_knm": 0,
    }


def _stations():
    ordinary = (
        ("A", 0, "RIGHT"),
        ("AF", 500, "CONTINUOUS"),
        ("SAG-LEFT", 1424.195292958916, "CONTINUOUS"),
        ("RAMP-LEFT", 3300, "CONTINUOUS"),
        ("BF1", 3850, "CONTINUOUS"),
        ("B1", 4000, "LEFT"),
        ("B2", 4000, "RIGHT"),
        ("BF2", 4150, "CONTINUOUS"),
        ("RAMP-RIGHT", 4700, "CONTINUOUS"),
        ("SAG-RIGHT", 6575.804707041084, "CONTINUOUS"),
        ("CF", 7500, "CONTINUOUS"),
        ("C", 8000, "LEFT"),
    )
    breaks = [
        (f"K{i}-{side}", x, side)
        for i, x in enumerate(KNEES, 1)
        for side in ("LEFT", "RIGHT")
    ]
    return [
        {"station_id": name, "x_mm": x, "side": side}
        for name, x, side in sorted([*ordinary, *breaks], key=lambda row: row[1:])
    ]


def _bottom_nodes():
    # Intersect the two horizontal offsets with the ramp offset measured
    # normal to the soffit. Tangent fillets are constructed separately.
    x_shift = BAR_OFFSET * (SECANT - 1) / SLOPE
    shallow, deep = 500 - BAR_OFFSET, 600 - BAR_OFFSET
    points = [
        (PIECE_ENDS[0], shallow),
        (3000 + x_shift, shallow),
        (3600 + x_shift, deep),
        (4400 - x_shift, deep),
        (5000 - x_shift, shallow),
        (PIECE_ENDS[1], shallow),
    ]
    return [
        {
            "node_id": name,
            "station_mm": x,
            "y_mm": y,
            "radius_mm": BAR_BEND_RADIUS if name.startswith("K") else None,
        }
        for name, (x, y) in zip(
            ("start", "K1", "K2", "K3", "K4", "end"), points, strict=True
        )
    ]


def _bottom_chain(nodes):
    """Intersect tangent offsets and solve each circular arc analytically."""
    xyz = [(node["station_mm"], node["y_mm"]) for node in nodes]
    bends = {}
    path = []
    head = xyz[0]
    for prior, node, after, detail in zip(
        xyz[:-2], xyz[1:-1], xyz[2:], nodes[1:-1], strict=True
    ):
        incoming = math.atan2(node[1] - prior[1], node[0] - prior[0])
        outgoing = math.atan2(after[1] - node[1], after[0] - node[0])
        turn = outgoing - incoming
        radius = detail["radius_mm"]
        offset = radius * math.tan(abs(turn) / 2)
        p = (
            node[0] - offset * math.cos(incoming),
            node[1] - offset * math.sin(incoming),
        )
        q = (
            node[0] + offset * math.cos(outgoing),
            node[1] + offset * math.sin(outgoing),
        )
        sign = math.copysign(1, turn)
        c = (
            p[0] - sign * radius * math.sin(incoming),
            p[1] + sign * radius * math.cos(incoming),
        )
        assert abs(math.dist(q, c) - radius) < 1e-9
        assert head[0] < p[0] < q[0]
        path.extend(
            (
                {"start": head, "end": p, "length_mm": math.dist(head, p)},
                {
                    "start": p,
                    "end": q,
                    "centre": c,
                    "radius_mm": radius,
                    "length_mm": radius * abs(turn),
                },
            )
        )
        bends[detail["node_id"]] = (p, q, turn)
        head = q
    path.append({"start": head, "end": xyz[-1], "length_mm": math.dist(head, xyz[-1])})
    return path, bends


def _axis_at(chain, x):
    for segment in chain:
        p, q = segment["start"], segment["end"]
        if p[0] <= x <= q[0]:
            if "centre" in segment:
                cx, cy = segment["centre"]
                return cy + math.copysign(
                    math.sqrt(segment["radius_mm"] ** 2 - (x - cx) ** 2), p[1] - cy
                )
            return p[1] + (q[1] - p[1]) * (x - p[0]) / (q[0] - p[0])
    raise ValueError(f"No resolved longitudinal path at {x}.")


def _bottom_cover_bound(chain):
    # Both the soffit and bar ordinate are Lipschitz in station with
    # constant 1/6. A one-millimetre grid bounds their vertical separation
    # to within 1/6 mm. The soffit's slope then bounds normal clearance.
    sampled = min(
        _depth(x) - _axis_at(chain, x) for x in range(PIECE_ENDS[0], PIECE_ENDS[1] + 1)
    )
    return (sampled - SLOPE) / SECANT - BAR_DIA / 2


def _point_to_segment(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
    return math.dist(p, (a[0] + t * dx, a[1] + t * dy))


def _link_clearance(chain, x, bottom):
    next_plane = x + HOOK_OFFSET
    rectangle = [
        (x, LINK_AXIS),
        (x, bottom),
        (next_plane, bottom),
        (next_plane, LINK_AXIS),
        (x, LINK_AXIS),
    ]
    # The vertical projection of all rounded steel axes lies in this
    # rectangle. Its separation from the piecewise soffit bounds cover.
    assert bottom < min(_depth(x), _depth(next_plane))
    separation = min(
        min(
            _point_to_segment(a, p, q),
            _point_to_segment(b, p, q),
            _point_to_segment(p, a, b),
            _point_to_segment(q, a, b),
        )
        for a, b in pairwise(rectangle)
        for p, q in pairwise(OUTLINE)
    )
    corner_y = bottom - (LINK_RADIUS + LINK_DIA / 2)
    lower_axes = [_axis_at(chain, station) for station in (x, next_plane)]
    # A conservative circle bounds the oblique Ø20 intersection at a
    # transverse plane. Bound both sides of the 10 mm gap between planes.
    distances = [math.hypot(8, y - corner_y) for y in lower_axes]
    return {
        "cover_mm": min(LINK_AXIS - LINK_DIA / 2, separation - LINK_DIA / 2),
        "minimum_seat_gap_mm": LINK_RADIUS - BAR_DIA / 2 * SECANT - max(distances),
        "maximum_seat_gap_mm": LINK_RADIUS - BAR_DIA / 2 - min(distances),
        "bottom_axes_mm": lower_axes,
    }


def _link_cut(bottom):
    width = WIDTH - 2 * LINK_AXIS
    height = bottom - LINK_AXIS
    radius = LINK_RADIUS + LINK_DIA / 2
    return (
        2 * HOOK_VERTEX_LEG
        + width
        + 2 * height
        + math.hypot(width, HOOK_OFFSET)
        + 5 * radius * (math.pi / 2 - 2)
    )


def _links(chain, member_id):
    dedicated = {x + offset for x in KNEES for offset in (-50, 50)}
    stations = sorted(set(range(0, 8001, PITCH)) | dedicated)
    links = []
    for x in stations:
        mean = (_axis_at(chain, x) + _axis_at(chain, x + HOOK_OFFSET)) / 2
        candidates = []
        for y in range(math.floor(mean + 16), math.ceil(mean + 21)):
            clearance = _link_clearance(chain, x, y)
            if (
                clearance["cover_mm"] >= 30
                and clearance["minimum_seat_gap_mm"] >= 0
                and clearance["maximum_seat_gap_mm"] <= 2
            ):
                candidates.append(y)
        bottom = min(candidates, key=lambda y: (abs(y - mean - 18.75), y))
        links.append(
            {
                "station_mm": x,
                "bottom_axis_mm": bottom,
                "bar_mark": f"{member_id}-L8-H{bottom - LINK_AXIS}",
                "purpose": "bend" if x in dedicated else "shear",
            }
        )
    return links


def _member():
    stations = _stations()
    load_cases = (("U1", 24), ("U2", 32))
    return {
        "schema_version": "is456-continuous-beam-check/v1",
        "member_id": "B-HAUNCH",
        "analysis_revision": "HAUNCH-A1",
        "current_analysis_revision": "HAUNCH-A1",
        "reinforcement_revision": "HAUNCH-R1",
        "source_reference": "Two symmetric 4 m spans with gross-depth-dependent EI and factored UDL",
        "width_mm": WIDTH,
        "depth_mm": 500,
        "clear_cover_mm": 32,
        "aggregate_size_mm": 20,
        "fck_nmm2": 30,
        "fy_nmm2": 500,
        "link_diameter_mm": LINK_DIA,
        "link_fy_nmm2": 415,
        "link_spacing_mm": PITCH,
        "supports": [
            {"support_id": name, "centre_mm": x, "width_mm": width}
            for name, x, width in (("A", 0, 1000), ("B", 4000, 300), ("C", 8000, 1000))
        ],
        "straight_bars": {
            "start_mm": PIECE_ENDS[0],
            "end_mm": PIECE_ENDS[1],
            "source_reference": "Common covered endpoints of continuous corner bars",
        },
        "bars": [
            {
                "bar_id": f"{face[0].upper()}{i}",
                "face": face,
                "diameter_mm": BAR_DIA,
                "x_from_left_mm": x,
                "y_from_top_mm": y,
            }
            for face, y in (("top", 54), ("bottom", 500 - BAR_OFFSET))
            for i, x in enumerate(ABSCISSAE, 1)
        ],
        "stations": stations,
        "combinations": [
            {
                "combination_id": name,
                "kind": "ULS",
                "required_station_ids": [station["station_id"] for station in stations],
            }
            for name, _ in load_cases
        ],
        "actions": [
            _actions(w, moment, name, station)
            for name, w, moment in (
                (name, w, _support_moment(w)) for name, w in load_cases
            )
            for station in stations
        ],
    }


def _section_rows(member, chain):
    rows = []
    stations = {station["station_id"]: station for station in member["stations"]}
    for action in member["actions"]:
        station = stations[action["station_id"]]
        x = station["x_mm"]
        if x in (0, 4000, 8000):
            continue
        depth, bottom = _depth(x), _axis_at(chain, x)
        face = "top" if action["mu_knm"] < 0 else "bottom"
        local = {
            **member,
            "depth_mm": depth,
            "bars": [
                {**bar, "y_from_top_mm": bottom if bar["face"] == "bottom" else 54}
                for bar in member["bars"]
            ],
        }
        capacity = section(local, face, None, TABLE_19[30])
        d = capacity["effective_depth_mm"]
        slope = _soffit_slope(x, station["side"])
        moment, shear = action["mu_knm"], action["vu_kn"]
        adjustment = abs(moment) * abs(slope) * 1000 / d
        if moment * shear * slope > 0:
            adjustment = -adjustment
        demand = abs(abs(shear) + adjustment)
        rows.append(
            {
                "row_id": action["row_id"],
                "station_mm": x,
                "side": station["side"],
                "depth_mm": depth,
                "bottom_axis_mm": bottom,
                "soffit_slope": slope,
                "moment_knm": moment,
                "concurrent_shear_kn": shear,
                "shear_adjustment_kn": adjustment,
                "shear_demand_kn": demand,
                "effective_depth_mm": d,
                "tension_face": face,
                "moment_capacity_knm": capacity["capacity_knm"],
                "shear_capacity_kn": capacity["shear_capacity_kn"],
                "nominal_shear_nmm2": demand * 1000 / (WIDTH * d),
                "flexure_utilization": abs(moment) / capacity["capacity_knm"],
                "shear_utilization": demand / capacity["shear_capacity_kn"],
            }
        )
    return rows


def _schedule(links, bottom_cut):
    by_mark = Counter(link["bar_mark"] for link in links)
    cut_by_mark = {
        link["bar_mark"]: _link_cut(link["bottom_axis_mm"]) for link in links
    }
    cuts = [
        {
            "bar_mark": "B-HAUNCH-top-D20",
            "diameter_mm": 20,
            "quantity": 2,
            "cut_mm": 8920,
        },
        {
            "bar_mark": "B-HAUNCH-bottom-D20",
            "diameter_mm": 20,
            "quantity": 2,
            "cut_mm": bottom_cut,
        },
        *[
            {
                "bar_mark": mark,
                "diameter_mm": 8,
                "quantity": count,
                "cut_mm": cut_by_mark[mark],
            }
            for mark, count in sorted(by_mark.items())
        ],
    ]
    mass = sum(
        r["quantity"] * r["cut_mm"] * math.pi * r["diameter_mm"] ** 2 / 4 * 7850e-9
        for r in cuts
    )
    return {"rows": cuts, "quantity": len(links) + 4, "mass_kg": mass}


def build():
    member = _member()
    nodes = _bottom_nodes()
    chain, bends = _bottom_chain(nodes)
    soffit_cover = _bottom_cover_bound(chain)
    assert soffit_cover >= 30
    links = _links(chain, member["member_id"])
    measured = [
        {
            "station_mm": link["station_mm"],
            "bottom_axis_mm": link["bottom_axis_mm"],
            **_link_clearance(chain, link["station_mm"], link["bottom_axis_mm"]),
        }
        for link in links
    ]
    assert min(row["cover_mm"] for row in measured) >= 30
    assert 25 <= (ABSCISSAE[1] - ABSCISSAE[0] - BAR_DIA) <= 150
    gap = min(b["station_mm"] - a["station_mm"] for a, b in pairwise(links))
    assert gap - HOOK_OFFSET - LINK_DIA >= 25
    assert HOOK_VERTEX_LEG - LINK_RADIUS - LINK_DIA / 2 >= 8 * LINK_DIA
    assert len(links) == 49
    strength = _section_rows(member, chain)
    assert max(row["flexure_utilization"] for row in strength) < 1
    assert max(row["shear_utilization"] for row in strength) < 1
    assert max(row["nominal_shear_nmm2"] for row in strength) < 3.5
    bend_groups = []
    force_bands = []
    for (bend_id, (p, q, turn)), nominal in zip(bends.items(), KNEES, strict=True):
        stations = [nominal - 50, nominal + 50]
        assert stations[0] < p[0] < q[0] < stations[1]
        demand = 2 * MAX_BAR_FORCE_KN * math.sin(abs(turn) / 2)
        one_leg = 0.87 * 415 * math.pi * LINK_DIA**2 / 4 / 1000
        bearing = MAX_BAR_FORCE_KN * 1000 / ((BAR_BEND_RADIUS - BAR_DIA / 2) * BAR_DIA)
        bearing_limit = 1.5 * 30 / (1 + 2 * BAR_DIA / (ABSCISSAE[0] + BAR_DIA / 2))
        available = min(p[0] - PIECE_ENDS[0], PIECE_ENDS[1] - q[0])
        assert one_leg < demand <= 2 * one_leg and bearing <= bearing_limit
        assert available >= 725
        bend_groups.append({"node_id": bend_id, "link_stations_mm": stations})
        force_bands.append(
            {
                "node_id": bend_id,
                "link_stations_mm": stations,
                "tangent_x_mm": [p[0], q[0]],
                "demand_per_bar_kn": demand,
                "resistance_per_bar_kn": 2 * one_leg,
                "bearing_nmm2": bearing,
                "bearing_limit_nmm2": bearing_limit,
                "minimum_projected_development_mm": available,
                "required_compression_development_mm": 725,
            }
        )
    request = {
        "identity": {
            "family_id": "beam",
            "case_id": "BEAM05-variable-depth",
            "member_id": "B-HAUNCH",
        },
        "member": member,
        "stock_length_mm": 12000,
        "link_detail": {
            "first_station_mm": 0,
            "last_station_mm": 8000,
            "internal_bend_radius_mm": LINK_RADIUS,
            "hook_vertex_leg_mm": HOOK_VERTEX_LEG,
            "hook_plane_offset_mm": HOOK_OFFSET,
            "source_reference": "Vertically placed individual closed links with two separated hook planes",
        },
        "haunch": {
            "source_reference": "Nominal trial jig and rounded continuous four-corner cage",
            "outline": [{"station_mm": x, "depth_mm": depth} for x, depth in OUTLINE],
            "bottom_bar_path": nodes,
            "links": links,
            "bend_restraint": bend_groups,
            "minimum_cover_mm": 30,
            "maximum_seat_gap_mm": 2,
        },
    }
    expected = {
        "status": "PASS",
        "rows": strength,
        "bend_checks": force_bands,
        "link_checks": measured,
        "bottom_segments": chain,
        "minimum_link_cover_mm": min(row["cover_mm"] for row in measured),
        "bottom_bar_soffit_cover_bound_mm": soffit_cover,
        "face_bar_clear_spacing_mm": ABSCISSAE[1] - ABSCISSAE[0] - BAR_DIA,
        "minimum_axial_opening_mm": gap - HOOK_OFFSET - LINK_DIA,
        "support_development_mm": {"AF": 960, "BF1": 4610, "BF2": 4610, "CF": 960},
        "required_tension_development_mm": 906.25,
        "bbs": _schedule(links, sum(part["length_mm"] for part in chain)),
    }
    cases = {"haunch": {"request": request, "expected": expected}}
    for name, status, code in (
        ("clashing_link", "FAIL", "BEAM.HAUNCH_LINK_FIT_FAIL"),
        ("bend_restraint_short", "FAIL", "BEAM.HAUNCH_BEND_RESTRAINT_FAIL"),
        ("corrected_shear_overload", "FAIL", "BEAM_SECTION_FAIL"),
        ("missing_transition_row", "HOLD", "BEAM_ACTION_MISSING"),
        ("missing_bend_evidence", "HOLD", "BEAM.HAUNCH_BASIS_HELD"),
        ("stale", "HOLD", "BEAM_ANALYSIS_STALE"),
    ):
        trial = deepcopy(request)
        trial["identity"]["case_id"] = f"BEAM05-{name.replace('_', '-')}"
        extra = {}
        if name == "clashing_link":
            link = next(
                link for link in trial["haunch"]["links"] if link["station_mm"] == 3200
            )
            link["bottom_axis_mm"] -= 6
            link["bar_mark"] = "B-HAUNCH-L8-clashing"
            fit = _link_clearance(chain, 3200, link["bottom_axis_mm"])
            assert fit["cover_mm"] >= 30 and fit["minimum_seat_gap_mm"] < 0
            extra = {
                "station_mm": 3200,
                "minimum_seat_gap_mm": fit["minimum_seat_gap_mm"],
            }
        elif name == "bend_restraint_short":
            removed = trial["haunch"]["bend_restraint"][0]["link_stations_mm"].pop()
            trial["haunch"]["links"] = [
                link
                for link in trial["haunch"]["links"]
                if link["station_mm"] != removed
            ]
            extra = {"node_id": "K1"}
        elif name == "corrected_shear_overload":
            reference = next(row for row in strength if row["row_id"] == "U2:RAMP-LEFT")
            action = next(
                row
                for row in trial["member"]["actions"]
                if row["row_id"] == reference["row_id"]
            )
            # Isolated signed-demand sensitivity: only the correction
            # pushes the positive shear ordinate above the local capacity.
            action["vu_kn"] = (
                reference["shear_capacity_kn"]
                - abs(reference["shear_adjustment_kn"]) / 2
            )
            row = next(
                row
                for row in _section_rows(trial["member"], chain)
                if row["row_id"] == action["row_id"]
            )
            assert action["vu_kn"] < row["shear_capacity_kn"] < row["shear_demand_kn"]
            extra = {"row": row}
        elif name == "missing_transition_row":
            trial["member"]["actions"] = [
                row
                for row in trial["member"]["actions"]
                if row["row_id"] != "U2:K1-RIGHT"
            ]
        elif name == "missing_bend_evidence":
            trial["haunch"]["bend_restraint"] = None
        else:
            trial["member"]["current_analysis_revision"] = "HAUNCH-A2"
        cases[name] = {
            "request": trial,
            "expected": {"status": status, "required_issue_codes": [code], **extra},
        }

    return {
        "fixture_version": "library-030-beam05-haunch/v1",
        "sources": [
            "IS 456:2000 §§26.2.1–4, 26.5.1–3, 40.1.1–40.4 and Tables 15, 19 and 20",
            "BIS SP 34 §§8.10.2 and 8.11, vertically arranged individual links",
            "Independent gross EI compatibility, section force equilibrium, tangent geometry and cut take-off",
        ],
        "cases": cases,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    result = build()
    encoded = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if parser.parse_args().freeze:
        FIXTURE.write_text(encoded, encoding="utf-8")
    else:
        assert FIXTURE.read_text(encoding="utf-8") == encoded
    for name, case in result["cases"].items():
        print(f"Independent BEAM05 haunch {name}: {case['expected']['status']}")


if __name__ == "__main__":
    main()
