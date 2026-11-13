"""Independent COL04 code-action worksheet and fixed-compression replay."""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from functools import cache
from hashlib import sha256
from itertools import product
from pathlib import Path

from check_library_029_col03_reference import resultants, verify_values

FIXTURE = Path(__file__).with_name("library-029-col04-slender-column.json")
COL02 = FIXTURE.with_name("library-029-col02-rectangular-column.json")
COL03 = FIXTURE.with_name("library-029-col03-mixed-column.json")


def _end(mx, my):
    return {"mx_knm": mx, "my_knm": my}


def _elastic_stations(length, pu, b, depth, elastic_modulus, mx, my):
    # Elastic beam-column boundary value problem with equal signed end
    # moments, zero end translations and no transverse load. This supplies
    # actions for a synthetic transport benchmark, independent of RC capacity.
    ix, iy = b * depth**3 / 12, depth * b**3 / 12
    ratios = [math.sqrt(pu * 1000 / (elastic_modulus * i)) for i in (ix, iy)]
    rows = []
    for identifier, station in (("A", 0), ("MID", length / 2), ("B", length)):
        moments = [
            moment * math.cos(k * (station - length / 2)) / math.cos(k * length / 2)
            for moment, k in zip((mx, my), ratios, strict=True)
        ]
        rows.append({"station_id": identifier, "station_mm": station, **_end(*moments)})
    return rows


def inputs():
    col02, col03 = (json.loads(path.read_text()) for path in (COL02, COL03))
    data = col02["inputs"]
    tied = {
        key: data[key]
        for key in (
            "longitudinal_bar_diameter_mm",
            "bar_center_offset_mm",
            "nominal_cover_mm",
            "aggregate_size_mm",
            "project_required_cover_mm",
            "project_required_bend_radius_mm",
            "detailing_basis_reference",
        )
    }
    tied.update(
        layout="eight_bar",
        tie={
            "tie_id": "HOOP",
            "closed": True,
            "diameter_mm": data["tie_diameter_mm"],
            "spacing_mm": data["tie_spacing_mm"],
            "internal_bend_radius_mm": data["tie_internal_bend_radius_mm"],
            "hook_angle_deg": data["tie_hook_angle_deg"],
            "hook_tail_mm": data["tie_hook_tail_mm"],
        },
        cross_ties=col02["layouts"]["eight_bar"]["cross_ties"],
    )
    mixed = col03["cases"]["admitted_12_bar"]["request"]

    def plane(lu, le):
        return {
            "unsupported_length_mm": lu,
            "effective_length_mm": le,
            "restraint_basis": "Synthetic braced fixture with the stated effective length",
        }

    def column(length, lex, ley, *, mixed_bars=False, pu=500):
        b, d = (450, 550) if mixed_bars else (300, 400)
        return {
            "geometry": {
                "b_mm": b,
                "D_mm": d,
                "length_mm": length,
                "braced": True,
                "x": plane(length, lex),
                "y": plane(length, ley),
            },
            "materials": (
                mixed["materials"] if mixed_bars else {"fck_nmm2": 25, "fy_nmm2": 415}
            ),
            "reinforcement": deepcopy(mixed["reinforcement"] if mixed_bars else tied),
            "analysis_revision": "model-01",
            "current_analysis_revision": "model-01",
            "actions": {
                "basis": "first_order",
                "combination_id": "U1",
                "pu_kn": pu,
                "has_transverse_member_load": False,
                "end_a": _end(75, -45) if mixed_bars else _end(-60, 25),
                "end_b": _end(35, 25) if mixed_bars else _end(-30, -25),
            },
        }

    cases = {
        "both_short": column(3000, 3000, 3000),
        "minor_slender": column(6000, 3900, 6000),
        "both_slender": column(6000, 6000, 6000),
        "below_12": column(6000, 3900, 3599),
        "at_12": column(6000, 3900, 3600),
        "above_12": column(6000, 3900, 3601),
        "reversed_ends": column(6000, 3900, 6000),
        "rotated": column(6000, 6000, 3900),
        "minimum_governs": column(6000, 2600, 3000),
        "matching_summary": column(6000, 3900, 6000),
        "conflicting_summary": column(6000, 3900, 6000),
        "overload": column(6000, 3900, 6000),
        "mixed": column(7200, 6800, 6000, mixed_bars=True, pu=800),
        "reflected": column(7200, 6800, 6000, mixed_bars=True, pu=800),
        "mixed_high_axial": column(7200, 6800, 6000, mixed_bars=True, pu=2800),
        "missing_link": column(7200, 6800, 6000, mixed_bars=True, pu=800),
        "unsupported_transverse_load": column(6000, 3900, 6000),
    }
    case = cases["reversed_ends"]["actions"]
    case["end_a"], case["end_b"] = case["end_b"], case["end_a"]
    case = cases["rotated"]
    case["geometry"].update(b_mm=400, D_mm=300)
    for end in ("end_a", "end_b"):
        row = case["actions"][end]
        case["actions"][end] = _end(row["my_knm"], -row["mx_knm"])
    cases["minimum_governs"]["geometry"]["x"]["unsupported_length_mm"] = 4000
    cases["minimum_governs"]["actions"].update(end_a=_end(0, 0), end_b=_end(0, 0))
    cases["matching_summary"]["actions"]["magnitude_summary"] = _end(60, 25)
    cases["conflicting_summary"]["actions"].update(
        end_a=_end(0, 0),
        end_b=_end(0, 0),
        magnitude_summary=_end(60, 25),
    )
    cases["overload"]["actions"].update(end_a=_end(-240, 100), end_b=_end(-120, -100))
    for bar in cases["reflected"]["reinforcement"]["bars"]:
        bar["x_from_left_mm"] = 450 - bar["x_from_left_mm"]
        bar["y_from_top_mm"] = 550 - bar["y_from_top_mm"]
    for tie in cases["reflected"]["reinforcement"]["cross_ties"]:
        tie["hook_side"] = "positive" if tie["hook_side"] == "negative" else "negative"
    cases["reflected"]["actions"].update(end_a=_end(-75, 45), end_b=_end(-35, -25))
    cases["missing_link"]["reinforcement"]["cross_ties"].pop()
    cases["unsupported_transverse_load"]["actions"]["has_transverse_member_load"] = True

    second_order = column(6000, 6000, 6000)
    second_order["actions"] = {
        "basis": "supplied_second_order",
        "combination_id": "U1",
        "pu_kn": 500,
        "member_deflection_basis": "Analytic constant-EI eccentric-load beam-column, COL04 secant worksheet",
        "required_station_ids": ["A", "MID", "B"],
        "stations": _elastic_stations(6000, 500, 300, 400, 25000, -50, 30),
    }
    for case_id in (
        "supplied_second_order",
        "missing_basis",
        "stale_revision",
        "double_magnification",
        "missing_station",
    ):
        cases[case_id] = deepcopy(second_order)
    cases["missing_basis"]["actions"]["member_deflection_basis"] = None
    cases["stale_revision"]["current_analysis_revision"] = "model-02"
    cases["double_magnification"]["actions"]["apply_local_additional_moments"] = True
    cases["missing_station"]["actions"]["stations"].pop(1)
    for case_id, request in cases.items():
        request["identity"] = {
            "family_id": "column",
            "member_id": "COL04-C",
            "case_id": case_id,
            "source_reference": "COL04 independent column worksheet",
        }
    return cases


def _bars(request):
    steel = request["reinforcement"]
    if "bars" in steel:
        return steel["bars"]
    b, d = (request["geometry"][key] for key in ("b_mm", "D_mm"))
    c = steel["bar_center_offset_mm"]
    return [
        {
            "x_from_left_mm": x,
            "y_from_top_mm": y,
            "diameter_mm": steel["longitudinal_bar_diameter_mm"],
        }
        for x, y in (
            (c, c),
            (b - c, c),
            (b - c, d - c),
            (c, d - c),
            (c, d / 2),
            (b - c, d / 2),
            (b / 2, c),
            (b / 2, d - c),
        )
    ]


@cache
def _section_reference(b, d, fck, fy, pu, bars_key, samples):
    bars = json.loads(bars_key)
    data = {
        "geometry": {"b_mm": b, "D_mm": d},
        "materials": {"fck_nmm2": fck, "fy_nmm2": fy},
        "reinforcement": {"bars": bars},
    }

    @cache
    def plane(theta):
        projected = abs(b * math.cos(theta)) + abs(d * math.sin(theta))
        left, right = projected / 100000, projected * 256
        assert resultants(data, theta, left)[0] < pu < resultants(data, theta, right)[0]
        for _ in range(44):
            mid = (left + right) / 2
            if resultants(data, theta, mid)[0] > pu:
                right = mid
            else:
                left = mid
        xu = (left + right) / 2
        return (xu, *resultants(data, theta, xu))

    @cache
    def ray(dx, dy):
        magnitude = math.hypot(dx, dy)
        dx, dy = dx / magnitude, dy / magnitude

        def perpendicular(theta):
            _, _, x, y = plane(theta)
            return dx * y - dy * x

        angles = [2 * math.pi * index / samples for index in range(samples + 1)]
        cuts = [perpendicular(angle) for angle in angles]
        roots = [
            angle
            for angle, cut in zip(angles[:-1], cuts[:-1], strict=True)
            if abs(cut) < 1e-9
        ]
        for index, (left_cut, right_cut) in enumerate(
            zip(cuts[:-1], cuts[1:], strict=True)
        ):
            if (
                abs(left_cut) < 1e-9
                or abs(right_cut) < 1e-9
                or left_cut * right_cut >= 0
            ):
                continue
            lo, hi = angles[index : index + 2]
            for _ in range(39):
                mid = (lo + hi) / 2
                if perpendicular(mid) * left_cut > 0:
                    lo = mid
                else:
                    hi = mid
            roots.append((lo + hi) / 2)
        hits = []
        for angle in roots:
            xu, p, mx, my = plane(angle)
            length = dx * mx + dy * my
            if length > 0:
                hits.append(
                    {
                        "xu_mm": xu,
                        "mx_knm": mx,
                        "my_knm": my,
                        "capacity_knm": length,
                        "axial_residual_kn": p - pu,
                        "transverse_residual_knm": dx * my - dy * mx,
                    }
                )
        assert len(hits) == 1
        return hits[0]

    axes = {
        "x_positive": ray(1, 0),
        "x_negative": ray(-1, 0),
        "y_positive": ray(0, 1),
        "y_negative": ray(0, -1),
    }
    steel = sum(math.pi * bar["diameter_mm"] ** 2 / 4 for bar in bars)
    puz = (0.45 * fck * (b * d - steel) + 0.75 * fy * steel) / 1000
    alpha = min(2, max(1, 1 + (pu / puz - 0.2) / 0.6))
    return axes, puz, alpha, ray, data


def reference(case_id, request, samples):
    geo, actions, mat = (request[key] for key in ("geometry", "actions", "materials"))
    pu = actions["pu_kn"]
    if case_id in ("conflicting_summary", "double_magnification"):
        return {
            "member_status": "REJECT",
            "issue": (
                "COLUMN_ACTION_CONFLICT"
                if case_id == "conflicting_summary"
                else "COLUMN_ACTION_BASIS_CONFLICT"
            ),
        }
    b, d = geo["b_mm"], geo["D_mm"]
    first_order = actions["basis"] == "first_order"
    axis_results, envelopes = {}, {}
    for axis, size in (("x", d), ("y", b)):
        lu, le = (
            geo[axis][key] for key in ("unsupported_length_mm", "effective_length_mm")
        )
        slender = le / size >= 12
        ma = pu * le**2 / (2e6 * size) if slender and first_order else 0
        initial = floor = 0
        if first_order:
            moments = [actions[end][f"m{axis}_knm"] for end in ("end_a", "end_b")]
            floor = max(map(abs, moments))
            same_curvature = moments[0] * moments[1] >= 0
            small = min(map(abs, moments)) * (1 if same_curvature else -1)
            initial = max(0.6 * floor + 0.4 * small, 0.4 * floor)
            directions = {1 if m > 0 else -1 for m in moments if m != 0}
            bound = max(floor, initial + ma)
            envelopes[axis] = (
                sorted(sign * bound for sign in (directions or {-1, 1}))
                if bound
                else [0]
            )
        axis_results[axis] = {
            "slenderness": le / size,
            "classification": "SLENDER" if slender else "SHORT",
            "minimum_eccentricity_mm": max(20, lu / 500 + size / 30),
            "initial_moment_knm": initial,
            "end_floor_knm": floor,
            "additional_moment_knm": ma,
        }

    holds = {
        "missing_basis": "COLUMN.MEMBER_DEFLECTION_BASIS",
        "stale_revision": "COLUMN.STALE_ANALYSIS",
        "missing_station": "COLUMN.REQUIRED_STATIONS",
        "unsupported_transverse_load": "COLUMN.FIRST_ORDER_PROFILE",
    }
    if case_id in holds:
        return {
            "member_status": "HOLD",
            "strength_status": "HOLD",
            "restraint_status": "PASS",
            "issue": holds[case_id],
            "axes": axis_results,
        }

    axes, puz, alpha, ray, data = _section_reference(
        b,
        d,
        mat["fck_nmm2"],
        mat["fy_nmm2"],
        pu,
        json.dumps(_bars(request), sort_keys=True),
        samples,
    )
    if first_order:
        rows = [(end.upper()[-1], actions[end]) for end in ("end_a", "end_b")]
        for mx, my in product(envelopes["x"], envelopes["y"]):
            key = "EQUIVALENT-" + "".join(
                "N" if m < 0 else "P" if m > 0 else "0" for m in (mx, my)
            )
            rows.append((key, _end(mx, my)))
    else:
        rows = [(row["station_id"], row) for row in actions["stations"]]

    evaluated = {}
    for identifier, row in rows:
        mx, my = row["mx_knm"], row["my_knm"]
        cap_x = axes["x_negative" if mx < 0 else "x_positive"]["capacity_knm"]
        cap_y = axes["y_negative" if my < 0 else "y_positive"]["capacity_knm"]
        demand = ray(mx, my) if mx or my else None
        direct = math.hypot(mx, my) / demand["capacity_knm"] if demand else 0
        contour = (abs(mx) / cap_x) ** alpha + (abs(my) / cap_y) ** alpha
        evaluated[identifier] = {
            **_end(mx, my),
            "contour_ratio": contour,
            "direct_ratio": direct,
            "ratio": max(contour, direct),
        }
        if demand is not None:
            evaluated[identifier]["demand"] = demand

    minimum = {}
    for axis, values in axis_results.items():
        limit = min(
            axes[f"{axis}_{sign}"]["capacity_knm"] for sign in ("positive", "negative")
        )
        minimum[axis] = pu * values["minimum_eccentricity_mm"] / 1000 / limit
    all_ratios = {
        **{name: row["ratio"] for name, row in evaluated.items()},
        **{f"MIN-ECC-{axis.upper()}": value for axis, value in minimum.items()},
    }
    governing = max(all_ratios.values())
    # Equal peaks on symmetric contours can differ by root-roundoff.
    governing_id = min(
        name for name, ratio in all_ratios.items() if governing - ratio < 1e-8
    )
    strength = "PASS" if governing <= 1 else "FAIL"
    restraint = "HOLD" if case_id == "missing_link" else "PASS"
    member = "FAIL" if strength == "FAIL" else restraint
    result = {
        "member_status": member,
        "strength_status": strength,
        "restraint_status": restraint,
        "axes": axis_results,
        "capacities": axes,
        "puz_kn": puz,
        "alpha_n": alpha,
        "evaluated": evaluated,
        "minimum_eccentricity_ratios": minimum,
        "governing_id": governing_id,
        "governing_ratio": governing,
    }
    if case_id in ("mixed", "mixed_high_axial"):
        study = {}
        for axis, theta, length, key, orientation in (
            ("x_positive", -math.pi / 2, d, "y_from_top_mm", 1),
            ("x_negative", math.pi / 2, d, "y_from_top_mm", -1),
            ("y_positive", math.pi, b, "x_from_left_mm", 1),
            ("y_negative", 0, b, "x_from_left_mm", -1),
        ):
            distances = [
                bar[key] if orientation > 0 else length - bar[key]
                for bar in _bars(request)
            ]
            neutral_axis = max(distances) * 0.0035 / (0.0035 + 0.002)
            pb = resultants(data, theta, neutral_axis)[0]
            study[axis] = {"pb_kn": pb, "k": min(1, (puz - pu) / (puz - pb))}
        result["optional_reduction_study"] = study
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--derive", action="store_true")
    args = parser.parse_args()
    cases = inputs()
    hashes = {
        path.name: sha256(path.read_bytes()).hexdigest() for path in (COL02, COL03)
    }
    if args.derive:
        fixture = {
            "schema_version": "library-029-col04-slender-column-reference/v1",
            "frozen_before_implementation": True,
            "frozen_production_base": "38249b6f724239fd8434bd811ce1db5620a8fdef",
            "source_fixtures_sha256": hashes,
            "sources": [
                "IS 456:2000 Cl. 25.1–25.4, 39.1, 39.5, 39.6 and 39.7 through Amendment 5",
                "IIT Kharagpur Lesson 27 https://archive.nptel.ac.in/content/storage2/courses/105105104/pdf/m10l27.pdf",
                "University of Washington elastic secant model https://faculty.washington.edu/nsniadec/ME354/W08/Lecture33_EcceBuck.pdf",
            ],
            "method": {
                "first_order": "Unreduced Cl. 39.7.1 on slender planes. Orient the smaller end relative to the larger end, keep both physical end rows and check the product of signed component bounds. Reverse curvature checks both signs and the equivalent pairs have no physical station.",
                "strength": "Independent COL03 strip integration with 32 to 64 angular refinement. Check signed zero-cross-moment capacities, the IS 456 contour, the demand ray and adverse minimum-eccentricity cases one axis at a time.",
                "second_order": "Constant E=25000 MPa, gross Ix/Iy, 6000 mm, 500 kN, signed end moments (-50,+30) kNm. Exact elastic secant solution, both axes peak at mid-height, no other critical section. An action replay, not a project RC stiffness or global stability reference.",
                "optional_reduction": "Independent signed prescribed strain state for diagnostic study only. Unreduced additions govern this delivery.",
            },
            "tolerances": {
                "moment_knm": 0.01,
                "residual_kn_or_knm": 0.01,
                "ratio": 0.0001,
                "xu_mm": 0.01,
            },
            "cases": {},
        }
    else:
        fixture = json.loads(FIXTURE.read_text())
        assert fixture["source_fixtures_sha256"] == hashes
        assert set(fixture["cases"]) == set(cases)
    for name, request in cases.items():
        result = reference(name, request, 64)
        verify_values(reference(name, request, 32), result, name)
        if args.derive:
            fixture["cases"][name] = {"request": request, "expected": result}
        else:
            assert fixture["cases"][name]["request"] == request, name
            verify_values(result, fixture["cases"][name]["expected"], name)
            print(f"PASS independent COL04 {name}")
    if args.derive:
        print(json.dumps(fixture, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
