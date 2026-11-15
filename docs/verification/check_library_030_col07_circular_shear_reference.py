"""Independent single-plane circular tied-column shear reference for COL07."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from copy import deepcopy
from pathlib import Path

REFERENCE = Path(__file__).with_name("library-030-col07-circular-shear.json")
TIED = Path(__file__).with_name("library-029-col07-circular-member.json")
RING_GRADE_NMM2 = 415


def requests() -> dict[str, dict]:
    """Return synthetic rows; this oracle intentionally imports no product code."""
    base = deepcopy(json.loads(TIED.read_text())["cases"]["tied"]["request"])
    base["schema_version"] = "column-circular-member-detailing-input/v1"
    base["identity"]["case_id"] = "single_plane_pass"
    base["basis"][
        "action_source_reference"
    ] = "COL07 circular shear synthetic station worksheet with signed Vy"
    base["actions"][0]["vy_kn"] = -120
    base["actions"][1]["vy_kn"] = 80
    cases = {"single_plane_pass": base}
    cases["shear_capacity_fail"] = deepcopy(base)
    cases["shear_capacity_fail"]["identity"]["case_id"] = "shear_capacity_fail"
    cases["shear_capacity_fail"]["actions"][0]["vy_kn"] = -210
    cases["combined_planes_hold"] = deepcopy(base)
    cases["combined_planes_hold"]["identity"]["case_id"] = "combined_planes_hold"
    cases["combined_planes_hold"]["actions"][0]["vx_kn"] = 20
    cases["missing_shear_evidence_hold"] = deepcopy(base)
    cases["missing_shear_evidence_hold"]["identity"][
        "case_id"
    ] = "missing_shear_evidence_hold"
    cases["missing_shear_evidence_hold"]["basis"]["action_source_reference"] = None
    return cases


def shear_row(request: dict, action: dict) -> dict:
    diameter = request["geometry"]["diameter_mm"]
    transverse = request["reinforcement"]["transverse"]
    fck = request["materials"]["fck_nmm2"]
    fy = min(RING_GRADE_NMM2, 415)
    # Use an equivalent circular hoop depth from ACI 318-14 §22.5.2.2.
    # Bound the effective concrete area separately for this reference.
    d = 0.8 * diameter
    gross_area = math.pi * diameter**2 / 4
    effective_area = min(diameter * d, 0.8 * gross_area)
    width = effective_area / d
    axial_factor = min(1.0 + 3000 * action["pu_kn"] / (gross_area * fck), 1.5)
    tc = 0.29  # Table 19 M30, deliberately lowest 0.15% row.
    vc = tc * axial_factor * effective_area / 1000
    asv = 2 * math.pi * transverse["diameter_mm"] ** 2 / 4
    vus = 0.87 * fy * asv * d / transverse["pitch_mm"] / 1000
    crushing = 3.5 * effective_area / 1000  # Table 20 M30.
    capacity = min(vc + vus, crushing)
    demand = abs(action["vy_kn"])
    pitch = transverse["pitch_mm"]
    return {
        "combination_id": action["combination_id"],
        "station_mm": action["check_station_mm"],
        "shear_plane": "y",
        "signed_demand_kn": action["vy_kn"],
        "demand_kn": demand,
        "width_mm": width,
        "d_mm": d,
        "gross_area_mm2": gross_area,
        "effective_shear_area_mm2": effective_area,
        "axial_factor": axial_factor,
        "table_19_tc_nmm2": tc,
        "effective_hoop_area_mm2": asv,
        "vc_kn": vc,
        "vus_kn": vus,
        "crushing_kn": crushing,
        "capacity_kn": capacity,
        "margin_kn": capacity - demand,
        "utilization": demand / capacity,
        "pitch_mm": pitch,
        "pitch_limit_mm": min(0.75 * d, 300, 0.87 * fy * asv / (0.4 * width)),
    }


def expected(name: str, request: dict) -> dict:
    """Compute the frozen hand-equation values and explicit admission controls."""
    statuses = {
        "single_plane_pass": ("PASS", None),
        "shear_capacity_fail": ("FAIL", "COLUMN.SHEAR_CAPACITY"),
        "combined_planes_hold": ("HOLD", "COLUMN.COMBINED_SHEAR"),
        "missing_shear_evidence_hold": ("HOLD", "COLUMN.CIRCULAR_MEMBER_BASIS_HELD"),
    }
    status, issue = statuses[name]
    placement = request["placement"]
    pitch = request["reinforcement"]["transverse"]["pitch_mm"]
    stations = list(
        range(placement["first_station_mm"], placement["last_station_mm"] + 1, pitch)
    )
    rows = (
        [shear_row(request, action) for action in request["actions"]]
        if status != "HOLD"
        else []
    )
    governing = max(rows, key=lambda row: row["utilization"], default=None)
    if governing is not None:
        assert governing["combination_id"] == "U1"
        assert all(row["pitch_mm"] <= row["pitch_limit_mm"] for row in rows)
        assert (governing["utilization"] <= 1) == (status == "PASS")
    longitudinal_qty = request["reinforcement"]["bar_count"]
    longitudinal_dia = request["reinforcement"]["bar_diameter_mm"]
    ends = request["end_detail"]
    length = (
        request["geometry"]["unsupported_length_mm"]
        + ends["start_straight_mm"]
        + ends["end_straight_mm"]
    )
    ring = request["reinforcement"]["transverse"]
    ring_cut = request["transverse_cut_schedule"]["cut_lengths_mm"][ring["tie_id"]]
    return {
        "status": status,
        "issue": issue,
        "bbs_available": status == "PASS",
        "checked_drawing_available": status == "PASS",
        "governing_action": governing,
        "evaluated_shear_rows": rows,
        "ring_stations_mm": stations,
        "ring_count": len(stations),
        "ring_cut_mm": ring_cut,
        "longitudinal_count": longitudinal_qty,
        "longitudinal_cut_mm": length,
        "straight_end_required_mm": longitudinal_dia * 0.87 * 500 / (4 * 1.5 * 1.6),
        "bbs_quantity": longitudinal_qty + len(stations),
        "bbs_mass_kg": (
            longitudinal_qty * length * longitudinal_dia**2
            + len(stations) * ring_cut * ring["diameter_mm"] ** 2
        )
        * (math.pi / 4)
        * 7850e-9,
    }


def fixture() -> dict:
    cases = {
        name: {"request": request, "expected": expected(name, request)}
        for name, request in requests().items()
    }
    return {
        "schema_version": "library-030-col07-circular-shear-reference/v1",
        "frozen_production_base": "6476a3ca08b70e6956a91e049d27e62d0bc0a9fa",
        "base_fixture_sha256": hashlib.sha256(TIED.read_bytes()).hexdigest(),
        "supplied_shear_basis": {
            "plane": "y",
            "ring_grade_nmm2": RING_GRADE_NMM2,
            "effective_depth_diameter_factor": 0.8,
            "effective_concrete_area_gross_cap_factor": 0.8,
            "credit_closed_ring_legs": 2,
        },
        "sources": [
            "IS 456:2000 Cl. 26.5.1.5–6, 40.2.1.2, 40.2.3 and 40.4, Tables 19 and 20. https://www.cracindia.in/admin/uploads/IS-456.pdf",
            "ACI 318-14 §22.5.2.2 and commentary inform the circular effective depth and closed-hoop analogy only. https://unaribas.com/wp-content/uploads/2021/04/aci-318-14.pdf",
            "The concrete area is conservatively capped at 0.8Ag as a declared specimen assumption. The existing COL07 tied reference supplies the cage, signed bending actions, grid and R1 cut.",
        ],
        "method": "Use the declared circular geometry and ordinary IS 456 shear equations in one principal plane with documented actions and a closed ring. Use the M30 Table 19 lower row, concurrent compression multiplier, and the Table 20 cap. Shear pitch must meet the geometric and minimum steel limits. Retain the independent tied-cage strength and physical controls. Section geometry assumptions are specific to this reference.",
        "absolute_tolerances": {
            "force_kn": 0.001,
            "length_mm": 0.001,
            "ratio": 0.000001,
            "mass_kg": 0.001,
        },
        "cases": cases,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args()
    data = fixture()
    if args.freeze:
        REFERENCE.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")
    else:
        assert json.loads(REFERENCE.read_text()) == data
    for name in data["cases"]:
        print(f"PASS independent COL07 circular shear {name}")


if __name__ == "__main__":
    main()
