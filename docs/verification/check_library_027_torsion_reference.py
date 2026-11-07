"""Independent IS 456 station torsion arithmetic for Packet D."""

from __future__ import annotations

import json
import math
from pathlib import Path

FIXTURE = Path(__file__).with_name("library-027-torsion-station.json")


def reference(data):
    b, depth, d = data["b_mm"], data["D_mm"], data["d_mm"]
    b1, d1 = data["corner_width_mm"], data["corner_depth_mm"]
    link = data["link"]
    stress = 0.87 * min(415, link["fy_nmm2"])
    ve = abs(data["v2_kn"]) + 1.6 * abs(data["torsion_knm"]) * 1000 / b
    mt = abs(data["torsion_knm"]) * (1 + depth / b) / 1.7
    ast = 2 * math.pi * data["longitudinal_diameter_mm"] ** 2 / 4
    pt = 100 * ast / (b * d)
    (p0, t0), (p1, t1) = data["table_19_bracket"]
    assert p0 <= pt <= p1
    tc = t0 + (t1 - t0) * (pt - p0) / (p1 - p0)
    tau_ve = 1000 * ve / (b * d)
    torsion = abs(data["torsion_knm"]) * 1e6 / (b1 * d1 * stress)
    shear = abs(data["v2_kn"]) * 1000 / (2.5 * d1 * stress)
    floor = max(0, (tau_ve - tc) * b / stress)
    return {
        "equivalent_shear_kn": ve,
        "torsion_moment_knm": mt,
        "primary_equivalent_moment_knm": abs(data["m3_knm"]) + mt,
        "opposite_equivalent_moment_knm": max(0, mt - abs(data["m3_knm"])),
        "tau_ve_n_per_mm2": tau_ve,
        "tau_c_n_per_mm2": tc,
        "corner_width_mm": b1,
        "corner_depth_mm": d1,
        "torsion_area_per_spacing_mm": torsion,
        "shear_area_per_spacing_mm": shear,
        "shear_floor_area_per_spacing_mm": floor,
        "required_link_area_per_spacing_mm": max(
            torsion + shear, floor, 0.4 * b / stress
        ),
        "provided_link_area_per_spacing_mm": 2
        * math.pi
        * link["diameter_mm"] ** 2
        / 4
        / link["spacing_mm"],
        "maximum_spacing_mm": min(
            0.75 * d,
            300,
            link["centre_width_mm"],
            link["centre_depth_mm"],
            (link["centre_width_mm"] + link["centre_depth_mm"]) / 4,
        ),
    }


def main():
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    for case in fixture["cases"]:
        values = reference(case["inputs"])
        for key, target in case["expected"].items():
            if not math.isclose(values[key], target, rel_tol=0, abs_tol=1e-9):
                raise ValueError(f"{case['id']}.{key} differs from frozen target")
        print("PASS independent torsion", case["id"])


if __name__ == "__main__":
    main()
