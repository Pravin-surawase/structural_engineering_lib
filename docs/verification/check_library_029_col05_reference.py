"""Independent COL05 circular chord primitives and physical restraint checks."""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from functools import cache
from pathlib import Path

from check_library_027_references import concrete_stress, steel_stress
from check_library_029_col03_reference import verify_values

FIXTURE = Path(__file__).with_name("library-029-col05-circular-column.json")


def requests():
    base = {
        "geometry": {
            "diameter_mm": 450,
            "unsupported_length_mm": 3000,
            "end_condition": "HINGED_HINGED",
            "braced": True,
        },
        "materials": {"fck_nmm2": 30, "fy_nmm2": 500},
        "actions": {"pu_kn": 650, "mx_knm": 70, "my_knm": 40, "check_station_mm": 1500},
        "reinforcement": {
            "bar_count": 8,
            "bar_diameter_mm": 20,
            "ring_radius_mm": 165,
            "first_bar_angle_deg": 0,
            "aggregate_size_mm": 20,
            "nominal_cover_mm": 40,
            "project_required_cover_mm": 40,
            "transverse": {
                "kind": "tied",
                "tie_id": "R1",
                "diameter_mm": 10,
                "pitch_mm": 150,
                "closed": True,
                "closure_reference": "COL05 assumed full-strength closed ring closure, externally detailed",
            },
        },
    }
    spiral = deepcopy(base)
    spiral["reinforcement"]["transverse"] = {
        "kind": "spiral",
        "tie_id": "S1",
        "diameter_mm": 10,
        "pitch_mm": 60,
        "fy_nmm2": 500,
        "start_extra_turns": 1.5,
        "end_extra_turns": 1.5,
        "axial_enhancement": True,
    }
    sources = {
        "tied": base,
        "spiral": spiral,
        "spiral_wide": spiral,
        "spiral_ordinary_wide": spiral,
        "spiral_weak_ratio": spiral,
        "spiral_missing_anchor": spiral,
        "spiral_short_anchor": spiral,
        "tied_open_ring": base,
        "tied_missing_closure": base,
        "missing_transverse": base,
        "short_cover": base,
        "off_contact": spiral,
        "too_few_bars": base,
        "reflected": base,
        "rotated": base,
        "overload": base,
        "axial_limit": base,
        "axial_tied": base,
        "axial_spiral": spiral,
        "axial_spiral_wide": spiral,
        "axial_min_eccentricity": spiral,
        "slender_hold": base,
    }
    rows = {name: deepcopy(payload) for name, payload in sources.items()}
    for name, request in rows.items():
        request["identity"] = {
            "family_id": "column",
            "case_id": name,
            "member_id": "COL05-C",
            "source_reference": "COL05 independent circular reference",
        }
    for name in ("spiral_wide", "spiral_ordinary_wide", "axial_spiral_wide"):
        rows[name]["reinforcement"]["transverse"]["pitch_mm"] = 120
    rows["spiral_ordinary_wide"]["reinforcement"]["transverse"][
        "axial_enhancement"
    ] = False
    rows["spiral_weak_ratio"]["reinforcement"]["transverse"]["diameter_mm"] = 8
    rows["spiral_weak_ratio"]["reinforcement"]["ring_radius_mm"] = 167
    rows["spiral_missing_anchor"]["reinforcement"]["transverse"][
        "end_extra_turns"
    ] = None
    rows["spiral_short_anchor"]["reinforcement"]["transverse"]["end_extra_turns"] = 1
    rows["tied_open_ring"]["reinforcement"]["transverse"]["closed"] = False
    rows["tied_missing_closure"]["reinforcement"]["transverse"][
        "closure_reference"
    ] = None
    rows["missing_transverse"]["reinforcement"]["transverse"] = None
    rows["short_cover"]["reinforcement"].update(nominal_cover_mm=35, ring_radius_mm=170)
    rows["off_contact"]["reinforcement"]["ring_radius_mm"] = 160
    rows["too_few_bars"]["reinforcement"]["bar_count"] = 5
    rows["reflected"]["actions"].update(mx_knm=-70, my_knm=-40)
    angle = math.radians(22.5)
    rows["rotated"]["reinforcement"]["first_bar_angle_deg"] = 22.5
    rows["rotated"]["actions"].update(
        mx_knm=70 * math.cos(angle) + 40 * math.sin(angle),
        my_knm=40 * math.cos(angle) - 70 * math.sin(angle),
    )
    rows["overload"]["actions"].update(mx_knm=350, my_knm=200)
    rows["axial_limit"]["actions"]["pu_kn"] = 3100
    for name in ("axial_tied", "axial_spiral", "axial_spiral_wide"):
        rows[name]["actions"].update(pu_kn=2800, mx_knm=0, my_knm=0)
    rows["axial_min_eccentricity"]["geometry"]["unsupported_length_mm"] = 4500
    rows["axial_min_eccentricity"]["actions"].update(mx_knm=0, my_knm=0)
    rows["slender_hold"]["geometry"]["unsupported_length_mm"] = 6000
    return rows


def _moments(t):
    """Primitives of 2 t^j sqrt(1-t²) on the unit-radius circle."""
    w = math.sqrt(max(0, 1 - t * t))
    return (
        t * w + math.asin(t),
        -2 * w**3 / 3,
        (math.asin(t) - t * w * (1 - 2 * t * t)) / 4,
        -2 * w**3 / 3 + 2 * w**5 / 5,
    )


def concrete_circle_resultants(radius, xu, fck):
    """Analytic polynomial times circular chord, independent of runtime quadrature."""
    limit = 0.0035 if xu <= 2 * radius else 0.0035 / (1 + 0.75 * (1 - 2 * radius / xu))
    b = limit * radius / (0.002 * xu)
    a = limit / 0.002 - b
    lower = max(-1.0, -a / b)
    split = max(lower, min(1.0, (1 - a) / b))
    p0, p1, p2 = 2 * a - a * a, 2 * b * (1 - a), -b * b
    at_zero, at_split, at_top = (_moments(t) for t in (lower, split, 1))
    integrals = [high - low for high, low in zip(at_split, at_zero, strict=True)]
    fc = 0.67 * fck / 1.5
    force = (
        fc
        * radius**2
        * (
            at_top[0]
            - at_split[0]
            + sum(
                coeff * val
                for coeff, val in zip(
                    (p0, p1, p2),
                    integrals[:3],
                    strict=True,
                )
            )
        )
    )
    first_moment = (
        fc
        * radius**3
        * (
            at_top[1]
            - at_split[1]
            + sum(
                coeff * val
                for coeff, val in zip(
                    (p0, p1, p2),
                    integrals[1:],
                    strict=True,
                )
            )
        )
    )
    return force, first_moment, limit


@cache
def _capacity_model(
    diameter, fck, fy, pu, count, bar_diameter, ring, first_angle, samples
):
    radius = diameter / 2
    area = math.pi * bar_diameter**2 / 4
    angles = [
        math.radians(first_angle) + 2 * math.pi * index / count
        for index in range(count)
    ]
    bars = [(ring * math.cos(theta), ring * math.sin(theta)) for theta in angles]

    @cache
    def plane(normal):
        nx, ny = math.cos(normal), math.sin(normal)

        def resultants(xu):
            p, q, limit = concrete_circle_resultants(radius, xu, fck)
            mx, my = -ny * q, -nx * q
            for x, y in bars:
                strain = limit * (1 - (radius - nx * x - ny * y) / xu)
                force = area * (steel_stress(strain, fy) - concrete_stress(strain, fck))
                p += force
                mx -= force * y
                my -= force * x
            return p / 1000, mx / 1e6, my / 1e6

        lo, hi = 0.01, 256 * diameter
        assert resultants(lo)[0] < pu < resultants(hi)[0]
        for _ in range(46):
            mid = (lo + hi) / 2
            if resultants(mid)[0] > pu:
                hi = mid
            else:
                lo = mid
        xu = (lo + hi) / 2
        return xu, *resultants(xu)

    @cache
    def ray(dx, dy):
        size = math.hypot(dx, dy)
        dx, dy = dx / size, dy / size

        def perpendicular(normal):
            _, _, mx, my = plane(normal)
            return dx * my - dy * mx

        normals = [2 * math.pi * index / samples for index in range(samples + 1)]
        errors = [perpendicular(angle) for angle in normals]
        roots = [
            angle
            for angle, error in zip(normals[:-1], errors[:-1], strict=True)
            if abs(error) < 1e-9
        ]
        for index, (left, right) in enumerate(
            zip(errors[:-1], errors[1:], strict=True)
        ):
            if left * right >= 0 or min(abs(left), abs(right)) < 1e-9:
                continue
            lo, hi = normals[index : index + 2]
            for _ in range(39):
                mid = (lo + hi) / 2
                if perpendicular(mid) * left > 0:
                    lo = mid
                else:
                    hi = mid
            roots.append((lo + hi) / 2)
        candidates = []
        for normal in roots:
            xu, p, mx, my = plane(normal)
            capacity = dx * mx + dy * my
            if capacity > 0:
                candidates.append(
                    {
                        "normal_deg": math.degrees(normal) % 360,
                        "xu_mm": xu,
                        "mx_knm": mx,
                        "my_knm": my,
                        "capacity_knm": capacity,
                        "axial_residual_kn": p - pu,
                        "transverse_residual_knm": dx * my - dy * mx,
                    }
                )
        assert len(candidates) == 1
        return candidates[0]

    return ray


def reference(request, samples):
    geo, mat, actions, steel = (
        request[key] for key in ("geometry", "materials", "actions", "reinforcement")
    )
    d, length = geo["diameter_mm"], geo["unsupported_length_mm"]
    fck, fy = mat["fck_nmm2"], mat["fy_nmm2"]
    pu, mx, my = actions["pu_kn"], actions["mx_knm"], actions["my_knm"]
    count, db, ring = (
        steel[key] for key in ("bar_count", "bar_diameter_mm", "ring_radius_mm")
    )
    tie = steel["transverse"]
    gross = math.pi * d * d / 4
    area = count * math.pi * db * db / 4
    net = gross - area
    puz = (0.45 * fck * net + 0.75 * fy * area) / 1000
    eccentricity = max(20, length / 500 + d / 30)
    detail = {
        "clear_spacing_mm": 2 * ring * math.sin(math.pi / count) - db,
        "minimum_clear_spacing_mm": max(db, steel["aggregate_size_mm"] + 5),
        "periphery_spacing_mm": math.pi * d / count,
        "required_cover_mm": max(40, db, steel["project_required_cover_mm"]),
        "longitudinal_cover_mm": d / 2 - ring - db / 2,
        "ordinary_pitch_limit_mm": min(d, 16 * db, 300),
        "minimum_transverse_diameter_mm": max(db / 4, 6),
    }
    fail = count < 6 or not 0.008 <= area / gross <= 0.04
    fail |= detail["clear_spacing_mm"] < detail["minimum_clear_spacing_mm"]
    fail |= detail["periphery_spacing_mm"] > 300
    fail |= detail["longitudinal_cover_mm"] < detail["required_cover_mm"]
    hold = tie is None
    spiral_eligible = False
    if tie is not None:
        dt, pitch = tie["diameter_mm"], tie["pitch_mm"]
        core, centreline = (
            d - 2 * steel["nominal_cover_mm"],
            d - 2 * steel["nominal_cover_mm"] - dt,
        )
        gap = core / 2 - dt - ring - db / 2
        detail.update(
            core_outside_mm=core,
            transverse_centreline_diameter_mm=centreline,
            radial_gap_mm=gap,
        )
        fail |= (
            abs(gap) > 1e-6 or steel["nominal_cover_mm"] < detail["required_cover_mm"]
        )
        fail |= (
            dt < detail["minimum_transverse_diameter_mm"]
            or pitch > detail["ordinary_pitch_limit_mm"]
        )
        turn = math.pi * centreline
        if tie["kind"] == "tied":
            fail |= not tie["closed"]
            hold |= not tie["closure_reference"]
        else:
            turn = math.hypot(turn, pitch)
            used_fy = min(415, tie["fy_nmm2"])
            provided = (dt / core) ** 2 * turn / pitch
            required = 0.36 * ((d / core) ** 2 - 1) * fck / used_fy
            minimum_pitch, maximum_pitch = max(25, 3 * dt), min(75, core / 6)
            detail.update(
                spiral_ratio_provided=provided,
                spiral_ratio_required=required,
                spiral_fy_used_nmm2=used_fy,
                enhanced_min_pitch_mm=minimum_pitch,
                enhanced_max_pitch_mm=maximum_pitch,
            )
            anchors = [tie["start_extra_turns"], tie["end_extra_turns"]]
            hold |= None in anchors
            fail |= any(turns < 1.5 for turns in anchors if turns is not None)
            qualifies = minimum_pitch <= pitch <= maximum_pitch and provided >= required
            if tie["axial_enhancement"]:
                fail |= not qualifies
                spiral_eligible = qualifies
        detail["centreline_length_per_pitch_mm"] = turn
    restraint = "FAIL" if fail else "HOLD" if hold else "PASS"
    expected = {
        "restraint_status": restraint,
        "detail": detail,
        "gross_area_mm2": gross,
        "steel_area_mm2": area,
        "gross_inertia_mm4": math.pi * d**4 / 64,
        "minimum_eccentricity_mm": eccentricity,
        "puz_kn": puz,
        "spiral_enhancement_eligible": spiral_eligible and restraint == "PASS",
    }

    if length / d >= 12:
        strength = "HOLD"
    elif mx == my == 0 and eccentricity <= 0.05 * d:
        tied_cap = (0.4 * fck * net + 0.67 * fy * area) / 1000
        factor = 1.05 if expected["spiral_enhancement_eligible"] else 1
        ratio = pu / (factor * tied_cap)
        expected["strength"] = {
            "method": "short_axial",
            "tied_axial_capacity_kn": tied_cap,
            "axial_capacity_kn": factor * tied_cap,
            "enhancement_factor": factor,
            "governing_ratio": ratio,
        }
        strength = "PASS" if ratio <= 1 else "FAIL"
    elif pu >= puz:
        strength = "FAIL"
    else:
        ray = _capacity_model(
            d, fck, fy, pu, count, db, ring, steel["first_bar_angle_deg"], samples
        )
        axes = {
            "x_positive": ray(1, 0),
            "x_negative": ray(-1, 0),
            "y_positive": ray(0, 1),
            "y_negative": ray(0, -1),
        }
        alpha = max(1, min(2, 1 + (pu / puz - 0.2) / 0.6))
        cap_x = axes["x_negative" if mx < 0 else "x_positive"]["capacity_knm"]
        cap_y = axes["y_negative" if my < 0 else "y_positive"]["capacity_knm"]
        contour = (abs(mx) / cap_x) ** alpha + (abs(my) / cap_y) ** alpha
        minimum = {
            axis: pu
            * eccentricity
            / 1000
            / min(
                axes[f"{axis}_{side}"]["capacity_knm"]
                for side in ("positive", "negative")
            )
            for axis in ("x", "y")
        }
        demand = ray(mx, my) if mx or my else None
        direct = math.hypot(mx, my) / demand["capacity_knm"] if demand else 0
        ratio = max(contour, direct, *minimum.values())
        expected["strength"] = {
            "method": "fixed_compression",
            "enhancement_factor": 1,
            "axes": axes,
            "alpha_n": alpha,
            "contour_ratio": contour,
            "direct_ratio": direct,
            "minimum_eccentricity_ratios": minimum,
            "governing_ratio": ratio,
        }
        if demand:
            expected["strength"]["demand"] = demand
        strength = "PASS" if ratio <= 1 else "FAIL"

    expected["strength_status"] = strength
    expected["member_status"] = (
        "FAIL"
        if "FAIL" in (strength, restraint)
        else "HOLD" if "HOLD" in (strength, restraint) else "PASS"
    )
    return expected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--derive", action="store_true")
    args = parser.parse_args()
    cases = requests()
    if args.derive:
        fixture = {
            "schema_version": "library-029-col05-circular-column-reference/v1",
            "frozen_before_implementation": True,
            "frozen_production_base": "e043589c2b1ee33297bbb973653e3d69efb1ecf0",
            "sources": [
                "IS 456:2000 through Amendment 5, Cl. 25, 26.2.2.4(b), 26.3, 26.4, 26.5.3, 38.1, 39.1, 39.3–39.6. https://law.resource.org/pub/in/bis/S03/is.456.2000.pdf",
                "IIT Kharagpur NPTEL Lesson 22 compression members https://archive.nptel.ac.in/content/storage2/courses/105105104/pdf/m10l22.pdf",
            ],
            "method": {
                "section": "Exact primitives of the circular chord times the Fig. 21 plateau/parabola; discrete steel with displaced concrete. Root at fixed compression then solve signed axes and demand direction with angular refinement 32 to 64.",
                "axes": "Top-left coordinates, first bar at the specified clockwise angle from the right. Mx positive compresses top; My positive compresses left.",
                "helix": "Core area to outside diameter; physical centreline length per pitch; transverse fy capped at 415; check anchorage at both ends. 1.05 only for the admitted Cl. 39.3 short axial branch. Ordinary spiral without enhancement uses ordinary pitch limit.",
                "axial": "For zero supplied moments and admissible minimum eccentricity use Cl. 39.3 capacity. Otherwise check net-area Puz, Cl. 39.6, direct ray and separate minimum eccentricities.",
            },
            "tolerances": {
                "moment_knm": 0.01,
                "xu_mm": 0.01,
                "residual_kn_or_knm": 0.01,
                "ratio": 0.0001,
                "normal_deg": 0.01,
            },
            "cases": {},
        }
    else:
        fixture = json.loads(FIXTURE.read_text())
        assert set(fixture["cases"]) == set(cases)
    for name, request in cases.items():
        expected = reference(request, 64)
        verify_values(reference(request, 32), expected, name)
        if args.derive:
            fixture["cases"][name] = {"request": request, "expected": expected}
        else:
            assert fixture["cases"][name]["request"] == request, name
            verify_values(expected, fixture["cases"][name]["expected"], name)
            print(f"PASS independent COL05 {name}")
    if args.derive:
        print(json.dumps(fixture, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
