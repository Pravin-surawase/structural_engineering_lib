"""Freeze/replay independent BEAM01 and FLOW01 calculations using the stdlib."""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from pathlib import Path

FIXTURE = Path(__file__).with_name("library-029-beam01-flow01.json")


def section_reference():
    b, fck, fy, d, dc = 300, 25, 415, 500, 50
    ast = 3 * math.pi * 20**2 / 4
    # For this root the remote face yields and the near face stays elastic.
    tensile_force = ast * fy / 1.15

    def compression(x):
        strain = 0.0035 * (1 - dc / x)
        assert 0 <= strain < 0.002
        r = strain / 0.002
        concrete_stress = (0.67 / 1.5) * fck * (2 * r - r * r)
        assert 200000 * strain < 0.8 * fy / 1.15
        return 0.36 * fck * b * x, ast * (200000 * strain - concrete_stress)

    low, high = 60.0, 75.0
    for _ in range(65):
        mid = (low + high) / 2
        if sum(compression(mid)) < tensile_force:
            low = mid
        else:
            high = mid
    x = (low + high) / 2
    assert 0.0035 * (d / x - 1) > fy / 1.15 / 200000 + 0.002
    cc, cs = compression(x)
    pt = 100 * ast / (b * d)
    tc = 0.49 + (pt - 0.50) / 0.25 * (0.57 - 0.49)
    asv = 2 * math.pi * 8**2 / 4
    vc = tc * b * d / 1000
    vs = 0.87 * fy * asv * d / 300 / 1000
    ld = 20 * 0.87 * fy / (4 * 1.4 * 1.6)
    return {
        "d_mm": d,
        "tension_area_mm2": ast,
        "xu_mm": x,
        "concrete_compression_kn": cc / 1000,
        "net_compression_steel_kn": cs / 1000,
        "flexural_capacity_knm": (cc * (d - 0.42 * x) + cs * (d - dc)) / 1e6,
        "longitudinal_percent": pt,
        "tau_c_nmm2": tc,
        "concrete_shear_kn": vc,
        "link_shear_kn": vs,
        "shear_capacity_kn": vc + vs,
        "max_shear_kn": 3.1 * b * d / 1000,
        "development_mm": ld,
        "external_available_mm": 3 * 468,
        "internal_available_mm": 4368,
    }


def pattern_actions(stations):
    # Two equal constant-EI spans, zero end moments. Permanent 10 kN/m on
    # both spans plus 20 kN/m imposed on the left span. Three-moment equation.
    q_left, q_right, length = 30, 10, 4
    mb = -(q_left + q_right) * length**2 / 16
    ra = q_left * length / 2 + mb / length
    vb_right = q_right * length / 2 - mb / length
    out = {}
    for key, (station_mm, side) in stations.items():
        x = station_mm / 1000
        if x < length or (x == length and side == "LEFT"):
            out[key] = (ra * x - q_left * x**2 / 2, ra - q_left * x)
        else:
            a = x - length
            out[key] = (mb + vb_right * a - q_right * a**2 / 2, vb_right - q_right * a)
    return out


def fixture():
    stations = {
        "A": (0, "RIGHT"),
        "A-FACE": (250, "CONTINUOUS"),
        "L-MAX": (5000 / 3, "CONTINUOUS"),
        "L-MID": (2000, "CONTINUOUS"),
        "B-LEFT-FACE": (3850, "CONTINUOUS"),
        "B-LEFT": (4000, "LEFT"),
        "B-RIGHT": (4000, "RIGHT"),
        "B-RIGHT-FACE": (4150, "CONTINUOUS"),
        "R-MID": (6000, "CONTINUOUS"),
        "R-MAX": (7000, "CONTINUOUS"),
        "C-FACE": (7750, "CONTINUOUS"),
        "C": (8000, "LEFT"),
    }
    baseline = {
        "A": (0, 70),
        "A-FACE": (17.5, 70),
        "L-MID": (90, 0),
        "B-LEFT-FACE": (-109.5, -70),
        "B-LEFT": (-120, -70),
        "B-RIGHT": (-120, 70),
        "B-RIGHT-FACE": (-109.5, 70),
        "R-MID": (90, 0),
        "C-FACE": (17.5, -70),
        "C": (0, -70),
    }
    pattern = pattern_actions(stations)
    support_face = "B-RIGHT-FACE"
    combinations = {
        "B01": ("ULS", baseline),
        "PATTERN": ("ULS", pattern),
        "U1": ("ULS", {support_face: (-120, 70)}),
        "U2": ("ULS", {support_face: (-85, 115)}),
        "S1": ("SLS", {support_face: (-70, 40)}),
        "S2": ("SUSTAINED_SLS", {support_face: (-42, 24)}),
    }
    request = {
        "schema_version": "is456-continuous-beam-check/v1",
        "member_id": "B01",
        "analysis_revision": "SPECIMEN-A1",
        "current_analysis_revision": "SPECIMEN-A1",
        "reinforcement_revision": "SPECIMEN-R1",
        "source_reference": "BEAM01 supplied station actions and independent two-span pattern",
        "width_mm": 300,
        "depth_mm": 550,
        "fck_nmm2": 25,
        "fy_nmm2": 415,
        "clear_cover_mm": 32,
        "aggregate_size_mm": 20,
        "link_diameter_mm": 8,
        "link_spacing_mm": 300,
        "link_fy_nmm2": 415,
        "supports": [
            {"support_id": "A", "centre_mm": 0, "width_mm": 500},
            {"support_id": "B", "centre_mm": 4000, "width_mm": 300},
            {"support_id": "C", "centre_mm": 8000, "width_mm": 500},
        ],
        "bars": [
            {
                "bar_id": f"{face}-{i}",
                "face": face,
                "diameter_mm": 20,
                "x_from_left_mm": x,
                "y_from_top_mm": y,
            }
            for face, y in (("top", 50), ("bottom", 500))
            for i, x in enumerate((50, 150, 250), start=1)
        ],
        "straight_bars": {
            "start_mm": -218,
            "end_mm": 8218,
            "source_reference": "Specimen schedule, six continuous straight bars through both spans",
        },
        "stations": [
            {"station_id": key, "x_mm": x, "side": side}
            for key, (x, side) in stations.items()
        ],
        "combinations": [
            {"combination_id": key, "kind": kind, "required_station_ids": list(rows)}
            for key, (kind, rows) in combinations.items()
        ],
        "actions": [
            {
                "row_id": f"{key}:{station}",
                "combination_id": key,
                "station_id": station,
                "mu_knm": m,
                "vu_kn": v,
            }
            for key, (_, rows) in combinations.items()
            for station, (m, v) in rows.items()
        ],
    }
    sec = section_reference()
    controls = {}
    for name, status in (
        ("missing_internal_side", "HOLD"),
        ("missing_sustained", "PASS"),
        ("missing_anchorage", "HOLD"),
        ("short_anchorage", "FAIL"),
        ("strength_failure", "FAIL"),
        ("stale_analysis", "HOLD"),
        ("duplicate_station", "BLOCKED"),
    ):
        controls[name] = {"request": deepcopy(request), "ultimate_status": status}
    for name, row in (
        ("missing_internal_side", "B01:B-RIGHT"),
        ("missing_sustained", "S2:B-RIGHT-FACE"),
    ):
        data = controls[name]["request"]
        data["actions"] = [item for item in data["actions"] if item["row_id"] != row]
    controls["missing_anchorage"]["request"].pop("straight_bars")
    controls["short_anchorage"]["request"]["straight_bars"]["start_mm"] = 0
    for action in controls["strength_failure"]["request"]["actions"]:
        if action["row_id"] == "U2:B-RIGHT-FACE":
            action["vu_kn"] = 200
    controls["stale_analysis"]["request"]["current_analysis_revision"] = "SPECIMEN-A2"
    controls["duplicate_station"]["request"]["stations"].append(
        {"station_id": "B-LEFT", "x_mm": 4000, "side": "RIGHT"}
    )
    return {
        "fixture_version": "library-029-beam01-flow01-reference/v1",
        "sources": [
            "IS 456:2000 Clause 38.1, Figures 21–23 and Annex G rectangular stress block",
            "IS 456:2000 Clauses 26.2, 26.5.1 and 40, Tables 19, 20 and 26",
            "Independent three-moment equilibrium for two equal constant-EI spans",
        ],
        "notes": [
            "B01 and U1/U2 are supplied section-action examples, including specified face values. They are not outputs of the pattern calculation.",
            "PATTERN uses three ideal vertical supports with free outer rotations and 30/10 kN/m. Critical physical faces and both sides of the internal support centreline are retained.",
            "S1/S2 are recorded service combinations. Deflection, cracking, lateral restraint verification and fabrication remain outside this packet.",
        ],
        "tolerances": {"capacity_knm": 0.02, "xu_mm": 0.01, "shear_kn": 0.01},
        "section": sec,
        "actions": {
            "pattern_internal_reaction_kn": pattern["B-RIGHT"][1]
            - pattern["B-LEFT"][1],
            "u1_hogging_utilization": 120 / sec["flexural_capacity_knm"],
            "u2_shear_utilization": 115 / sec["shear_capacity_kn"],
            "sagging_utilization": 90 / sec["flexural_capacity_knm"],
            "governing_hogging_row": "U1:B-RIGHT-FACE",
            "baseline_centreline_hogging_row": "B01:B-LEFT",
            "governing_shear_row": "U2:B-RIGHT-FACE",
            "flow01_governing_hogging_row": "U1:B-RIGHT-FACE",
        },
        "cases": {
            "two_span": {"request": request, "ultimate_status": "PASS"},
            **controls,
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args()
    expected = fixture()
    if args.freeze:
        FIXTURE.write_text(json.dumps(expected, indent=2, allow_nan=False) + "\n")
    else:
        assert json.loads(FIXTURE.read_text()) == expected
    print(f"Independent BEAM01/FLOW01 reference: {len(expected['cases'])} cases")


if __name__ == "__main__":
    main()
