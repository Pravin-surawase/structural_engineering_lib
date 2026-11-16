"""Independent BEAM05 T-flange hogging cage, slab strip and fabrication reference."""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from pathlib import Path

from check_library_029_beam05_flanged_reference import STATIONS, TABLE_19
from check_library_029_beam_sections_reference import section

FIXTURE = Path(__file__).with_name("library-030-beam05-physical-flange.json")
WEB, HEIGHT, FLANGE = 300, 550, 150
SPAN, PHYSICAL_WIDTH = 4000, 1000
COVER, RADIUS = 40, 14
PIECE_ENDS = (-460, 8460)
XY_TOLERANCE = 2
PITCH = 150
SLAB_PITCH = 220
BOND = 1.4 * 1.6
FY = 415


def bar(key, mark, face, x, y, diameter):
    return {
        "bar_id": key,
        "mark": mark,
        "face": face,
        "x_from_left_mm": x,
        "y_from_top_mm": y,
        "diameter_mm": diameter,
        "start_mm": PIECE_ENDS[0],
        "end_mm": PIECE_ENDS[1],
    }


def room(station, x, y):
    return [station, x, y]


def link(stations, vertices, hook_vertices, owner):
    return {
        "owner": owner,
        "stations_mm": stations,
        "vertices": vertices,
        "hook_vertices": hook_vertices,
        "diameter_mm": 8,
        "centreline_radius_mm": RADIUS,
    }


def link_cut_mm(vertices):
    total = sum(math.dist(a, b) for a, b in zip(vertices, vertices[1:]))
    tail_lengths = []
    for i in range(1, len(vertices) - 1):
        before, middle, after = vertices[i - 1 : i + 2]
        a = [q - p for p, q in zip(before, middle)]
        b = [q - p for p, q in zip(middle, after)]
        angle = math.acos(
            sum(x * y for x, y in zip(a, b)) / math.hypot(*a) / math.hypot(*b)
        )
        tangent = RADIUS * math.tan(angle / 2)
        total += RADIUS * angle - 2 * tangent
        if i == 1:
            tail_lengths.append(math.hypot(*a) - tangent)
        if i == len(vertices) - 2:
            tail_lengths.append(math.hypot(*b) - tangent)
    assert min(tail_lengths) >= 8 * 8
    return total, tail_lengths


def member_actions(stations, combinations):
    rows = []
    for case in combinations:
        load = case["beam_udl_kn_per_m"]
        # Equal prismatic spans and pinned outer supports. Apply three moments.
        support = -load * (SPAN / 1000) ** 2 / 8
        reaction = load * SPAN / 2000 + support / (SPAN / 1000)
        for name, x, side in stations:
            reflect = x > SPAN or (x == SPAN and side == "RIGHT")
            s = (2 * SPAN - x if reflect else x) / 1000
            rows.append(
                {
                    "row_id": f"{case['combination_id']}:{name}",
                    "combination_id": case["combination_id"],
                    "station_id": name,
                    "mu_knm": reaction * s - load * s**2 / 2,
                    "vu_kn": (reaction - load * s) * (-1 if reflect else 1),
                    "tu_knm": 0,
                }
            )
    return rows


def schedule(mark, diameter, count, cut, owner):
    return {
        "mark": mark,
        "owner": owner,
        "diameter_mm": diameter,
        "quantity": count,
        "cut_length_mm": cut,
        "mass_kg": math.pi * diameter**2 / 4 * count * cut * 7850e-9,
    }


def fixture():
    # Station along beam, x from web-left, y from flange top. The bar axes
    # at the four web corners match the centres of the rounded link bends.
    upper = [
        bar(f"WT{i}", "WT20", "top", x, 58, 20) for i, x in enumerate((58, 242), 1)
    ]
    lower = [
        bar(f"WB{i}", "WB20", "bottom", x, 492, 20)
        for i, x in enumerate((58, 58 + 184 / 3, 242 - 184 / 3, 242), 1)
    ]
    sides = [
        bar(f"F{i}", "FT16", "top", x, 50, 16) for i, x in enumerate((-12, 312), 1)
    ]
    web_link = link(
        list(range(-80, 8021, PITCH)),
        [
            room(0, 144, 44),
            room(0, 44, 44),
            room(0, 44, 506),
            room(10, 256, 506),
            room(10, 256, 44),
            room(10, 44, 44),
            room(10, 44, 144),
        ],
        [1, 5],
        "BEAM",
    )
    # The shallow closed link surrounds the outboard Ø16 bars. Two
    # overlapping returns sit in different station planes. The link
    # supplies no web shear or torsion resistance.
    cap = link(
        list(range(-45, 8056, PITCH)),
        [
            room(0, 69, 36),
            room(0, -26, 36),
            room(0, -26, 118),
            room(10, 326, 118),
            room(10, 326, 36),
            room(10, -26, 36),
            room(10, -26, 115),
        ],
        [1, 5],
        "BEAM",
    )
    slab_transverse = {
        "owner": "SLAB",
        "top_axis_mm": 30,
        "bottom_axis_mm": 120,
        "stations_mm": list(range(-425, 8426, PITCH)),
        "x_ends_mm": [-975, 1275],
        "diameter_mm": 10,
    }
    slab_distribution = {
        "owner": "SLAB",
        "top_axis_mm": 70,
        "bottom_axis_mm": 98,
        "x_axes_mm": [150 + SLAB_PITCH * i for i in range(-5, 6)],
        "end_stations_mm": list(PIECE_ENDS),
        "diameter_mm": 8,
    }
    thickness = FLANGE
    strip = {
        "geometry_revision": "BEAM05-TF-G1",
        "transverse_support_x_mm": [-850, 150, 1150],
        "transverse_support_widths_mm": [300, WEB, 300],
        "transverse_edge_x_mm": [-1000, 1300],
        "width_between_stations_mm": [-500, 8500],
        "main": slab_transverse,
        "distribution": slab_distribution,
    }
    combos = [
        {
            "combination_id": name,
            "beam_udl_kn_per_m": q,
            "slab_udl_kn_per_m2": p,
            "other_beam_line_load_kn_per_m": q - 1.25 * p,
        }
        for name, q, p in (("U1", 48, 9), ("U2", 64, 12))
    ]
    rows = member_actions(STATIONS, combos)
    beam = {
        "width_mm": WEB,
        "depth_mm": HEIGHT,
        "fck_nmm2": 25,
        "fy_nmm2": FY,
        "link_diameter_mm": 8,
        "link_fy_nmm2": FY,
        "link_spacing_mm": PITCH,
        "flange": {
            "kind": "t_beam",
            "thickness_mm": FLANGE,
            "left_overhang_mm": 350,
            "right_overhang_mm": 350,
            "zero_moment_distance_mm": 3000,
            "monolithic": True,
        },
        "bars": upper + lower,
    }
    # Both neighbouring webs are 300 mm wide at 1 m centres, so adjoining
    # spans leave 700 mm clear on either side. The midpoint cap is 1000 mm.
    adjacent_cap = WEB + (1000 - WEB) / 2 + (1000 - WEB) / 2
    effective = min(PHYSICAL_WIDTH, adjacent_cap, WEB + 3000 / 6 + 6 * thickness)
    band = min(effective, SPAN / 10)
    assert max(abs(b["x_from_left_mm"] - WEB / 2) for b in sides) + 8 < band / 2
    assert -12 < 0 < WEB < 312
    assert any(
        x < (WEB - band) / 2 for x in slab_distribution["x_axes_mm"] if x >= -350
    )
    assert any(x > (WEB + band) / 2 for x in slab_distribution["x_axes_mm"] if x <= 650)

    web_only = {
        face: section(beam, face, effective, TABLE_19[25]) for face in ("top", "bottom")
    }
    hogging = section(
        dict(beam, bars=beam["bars"] + sides), "top", effective, TABLE_19[25]
    )
    assert (
        max(abs(row["mu_knm"]) for row in rows if row["mu_knm"] < 0)
        > web_only["top"]["capacity_knm"]
    )
    assert web_only["bottom"]["neutral_axis_mm"] < thickness
    checks = []
    for row in rows:
        face = "top" if row["mu_knm"] < 0 else "bottom"
        cap_m = (hogging if face == "top" else web_only[face])["capacity_knm"]
        cap_v = web_only[face]["shear_capacity_kn"]
        assert (
            not hogging["over_reinforced"]
            and abs(row["mu_knm"]) < cap_m
            and abs(row["vu_kn"]) < cap_v
        )
        checks.append(dict(row, moment_capacity_knm=cap_m, shear_capacity_kn=cap_v))
    governing_m = max(
        checks, key=lambda row: abs(row["mu_knm"]) / row["moment_capacity_knm"]
    )
    governing_v = max(
        checks, key=lambda row: abs(row["vu_kn"]) / row["shear_capacity_kn"]
    )
    adverse = {}
    for face, bars in (("top", beam["bars"] + sides), ("bottom", beam["bars"])):
        # Bound the loss in section depth/lever arm by moving tension steel
        # toward the compression face and compression steel inward by 2 mm.
        # This bound is conservative for the two faces of a rigid cage.
        inward = [
            dict(
                b,
                y_from_top_mm=b["y_from_top_mm"]
                + (XY_TOLERANCE if b["face"] == "top" else -XY_TOLERANCE),
            )
            for b in bars
        ]
        adverse[face] = section(dict(beam, bars=inward), face, effective, TABLE_19[25])
        assert (
            max(
                abs(row["mu_knm"])
                for row in rows
                if (row["mu_knm"] < 0) == (face == "top")
            )
            < adverse[face]["capacity_knm"]
        )

    # Independent local two-span slab checks on a repeating 600 mm strip.
    sample = [
        bar(f"M-{face}-{i}", "M10", face, x, y, 10)
        for face, y in (("top", 30), ("bottom", 120))
        for i, x in enumerate((75, 225, 375, 525), 1)
    ]
    slab = dict(beam, width_mm=600, depth_mm=FLANGE, bars=sample)
    capacity = section(slab, "top", None, TABLE_19[25])
    width_m, span_m = slab["width_mm"] / 1000, 1
    strip_checks = []
    for c in combos:
        line = c["slab_udl_kn_per_m2"] * width_m
        moment = line * span_m**2 / 8
        shear = 5 * line * span_m / 8
        tau = shear * 1000 / (600 * 120)
        pt = 100 * math.pi * 10**2 / (600 * 120)
        tau_c = 0.36 + (pt - 0.25) * (0.49 - 0.36) / 0.25
        assert moment < capacity["capacity_knm"] and tau < tau_c
        strip_checks.append(
            {
                "combination_id": c["combination_id"],
                "interior_support_moment_knm": -moment,
                "same_span_positive_peak_knm": 9 * line * span_m**2 / 128,
                "support_shear_magnitude_kn": shear,
                "tau_v_nmm2": tau,
                "tau_c_nmm2": tau_c,
            }
        )

    required_flange_ld = FY * 0.87 * 16 / (4 * BOND)
    required_main_ld = FY * 0.87 * 10 / (4 * BOND)
    # Available straight projection beyond each controlling support face.
    main_anchor = 1000 - WEB / 2 + 125
    outer_end = 500 + PIECE_ENDS[1] - 8000
    beam_anchor = [3850 - PIECE_ENDS[0], PIECE_ENDS[1] - 4150]
    min_ext_after_zero = min(3000 - PIECE_ENDS[0], PIECE_ENDS[1] - 5000)
    assert all(a > required_flange_ld for a in (*beam_anchor, outer_end))
    extension_required = max(HEIGHT - 50 + XY_TOLERANCE, 12 * 16, 3350 / 16)
    assert main_anchor > required_main_ld and min_ext_after_zero > extension_required

    # All bend fillets stay within their nominal vertex boxes. Axial
    # separation therefore bounds both crossing link systems, and the
    # horizontal cap rail clears the lower slab distribution row vertically.
    separation = {
        "web_to_flange_link_mm": 25 - 8,
        "web_to_slab_main_mm": 45 - 9,
        "flange_link_to_slab_main_mm": 60 - 9,
        "flange_link_to_web_top_bar_mm": 58 - 36 - 14,
        "flange_bar_to_top_slab_main_mm": 50 - 30 - 13,
        "web_bar_to_top_slab_main_mm": 58 - 30 - 15,
        "flange_link_to_slab_distribution_mm": 118 - 98 - 8,
        "between_slab_distribution_layers_mm": 98 - 70 - 8,
        "cap_to_next_main_access_mm": 60 - 9 - 2 * XY_TOLERANCE,
    }
    assert all(v > 2 * XY_TOLERANCE for v in separation.values())
    assert separation["cap_to_next_main_access_mm"] >= 40
    required_cover = {"web_mm": 35, "cap_mm": 25, "slab_mm": 20}
    lowest_cover = {"web_mm": COVER, "cap_mm": 150 - 118 - 4, "slab_mm": 25}
    assert all(lowest_cover[k] - XY_TOLERANCE >= v for k, v in required_cover.items())
    slab_main_area = math.pi * 10**2 / 4 * 1000 / PITCH
    slab_distrib_area = math.pi * 8**2 / 4 * 1000 / SLAB_PITCH
    assert min(slab_main_area, slab_distrib_area) >= 0.0012 * FLANGE * 1000
    web_cut, web_tails = link_cut_mm(web_link["vertices"])
    cap_cut, cap_tails = link_cut_mm(cap["vertices"])
    # At the closing vertical tail, the left bottom fillet is within one
    # radius measured along the slightly skew bottom rail. Conservatively
    # bound its approach toward the closing hook plane by that projection.
    cap_hook_plane_clearance = 10 - RADIUS * 10 / math.hypot(352, 10) - 8
    assert cap_hook_plane_clearance > 0
    assert cap["vertices"][0][1] + RADIUS < cap["vertices"][4][1] - RADIUS

    schedule_rows = [
        schedule("WT20", 20, 2, 8920, "BEAM"),
        schedule("WB20", 20, 4, 8920, "BEAM"),
        schedule("FT16", 16, 2, 8920, "BEAM"),
        schedule("WL8", 8, len(web_link["stations_mm"]), web_cut, "BEAM"),
        schedule("FL8", 8, len(cap["stations_mm"]), cap_cut, "BEAM"),
        *[
            schedule(
                "SM10-" + face, 10, len(slab_transverse["stations_mm"]), 2250, "SLAB"
            )
            for face in ("TOP", "BOTTOM")
        ],
        *[
            schedule(
                "SD8-" + face, 8, len(slab_distribution["x_axes_mm"]), 8920, "SLAB"
            )
            for face in ("TOP", "BOTTOM")
        ],
    ]
    request = {
        "member_id": "BEAM05-TF",
        "coordinate_system": "beam station, x from web-left, y down from flange top, all mm",
        "geometry_revision": "BEAM05-TF-G1",
        "analysis_revision": "BEAM05-TF-A1",
        "reinforcement_revision": "BEAM05-TF-R1",
        "beam": beam,
        "flange_bars": sides,
        "web_links": web_link,
        "flange_links": cap,
        "slab_strip": dict(strip, combinations=combos),
        "actions": rows,
        "stations": [dict(station_id=n, x_mm=x, side=s) for n, x, s in STATIONS],
        "support_widths_mm": [1000, 300, 1000],
        "placement": {
            "maximum_assembly_translation_per_axis_mm": XY_TOLERANCE,
            "fixed_tied_assemblies": ["web bars and links", "flange bars and links"],
            "independently_positioned_slab_layers": True,
            "access_scope": "Local beam and slab bars at interior support only",
        },
        "maximum_aggregate_mm": 20,
        "minimum_compaction_access_mm": 40,
        "required_cover_mm": required_cover,
    }
    expected = {
        "status": "PASS",
        "effective_width_mm": effective,
        "adjacency_cap_mm": adjacent_cap,
        "hogging_distribution_width_mm": band,
        "hogging_strength": hogging,
        "web_only_strength": web_only,
        "adverse_placement_capacity_knm": {
            face: value["capacity_knm"] for face, value in adverse.items()
        },
        "checks": checks,
        "governing_moment_row": governing_m["row_id"],
        "governing_shear_row": governing_v["row_id"],
        "minimum_clearances_mm": separation,
        "nominal_cover_mm": lowest_cover,
        "required_flange_development_mm": required_flange_ld,
        "minimum_flange_support_development_mm": min(beam_anchor),
        "flange_beyond_zero_moment_mm": min_ext_after_zero,
        "required_flange_extension_mm": extension_required,
        "required_slab_main_development_mm": required_main_ld,
        "available_slab_main_development_mm": main_anchor,
        "web_hook_tails_mm": web_tails,
        "flange_hook_tails_mm": cap_tails,
        "flange_hook_plane_clearance_mm": cap_hook_plane_clearance,
        "strip_main_area_per_m_mm2": slab_main_area,
        "strip_distribution_area_per_m_mm2": slab_distrib_area,
        "strip_flexure_capacity_knm": capacity["capacity_knm"],
        "strip_checks": strip_checks,
        "schedule": schedule_rows,
        "pieces": sum(r["quantity"] for r in schedule_rows),
        "mass_kg": sum(r["mass_kg"] for r in schedule_rows),
    }

    cases = {"physical_flange": {"request": request, "expected": expected}}
    for name, status, check in (
        ("link_clash", "FAIL", "web_flange_link_intersection"),
        ("open_flange_link", "FAIL", "flange_link_closure"),
        ("short_flange_development", "FAIL", "flange_bar_support_development"),
        ("missing_strip_actions", "HOLD", "slab_strip_action_basis"),
        ("stale_strip_geometry", "HOLD", "slab_strip_geometry_revision"),
    ):
        altered = deepcopy(request)
        if name == "link_clash":
            altered["flange_links"]["stations_mm"] = web_link["stations_mm"]
            assert cap["vertices"][2][1] < 44 < cap["vertices"][3][1]
            assert 44 < cap["vertices"][2][2] < 506
        elif name == "open_flange_link":
            altered["flange_links"]["vertices"] = [
                room(0, 69, 36),
                room(0, -26, 36),
                room(0, -26, 118),
                room(0, 326, 118),
                room(0, 326, 36),
                room(0, 231, 36),
            ]
            altered["flange_links"]["hook_vertices"] = [1, 4]
            assert 231 - 69 == 162
        elif name == "short_flange_development":
            altered["flange_bars"][0]["start_mm"] = 3400
            assert 3850 - 3400 < required_flange_ld
        elif name == "missing_strip_actions":
            del altered["slab_strip"]["combinations"]
        else:
            altered["slab_strip"]["geometry_revision"] = "BEAM05-TF-G0"
        cases[name] = {
            "request": altered,
            "expected": {
                "status": status,
                "check": check,
                "checked_drawing": False,
                "bbs": False,
            },
        }
    return {
        "fixture_version": "library-030-beam05-physical-flange-reference/v1",
        "sources": [
            "IS 456:2000 §§23.1.1–2, 26.2, 26.3, 26.4, 26.5.1.4–8, 26.5.2, 38, 40 and Table 19",
            "Two-span three-moment equality, signed checks and sectional force equilibrium",
            "BEAM05 published two-span T geometry and web-only reference retained separately",
        ],
        "cases": cases,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    options = parser.parse_args()
    generated = json.dumps(fixture(), indent=2, allow_nan=False) + "\n"
    if options.write:
        FIXTURE.write_text(generated, encoding="utf-8")
    else:
        assert (
            FIXTURE.read_text(encoding="utf-8") == generated
        ), "Independent reference drift"
    print("Reproduced physical T-flange PASS, three FAIL and two HOLD cases.")
