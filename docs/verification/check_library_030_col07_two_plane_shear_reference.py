"""Freeze a bounded, independent two-plane shear allocation screen for COL07.

This is an evidence oracle, deliberately independent of product code.  It is
not a claim that IS 456 supplies a biaxial-column-shear interaction equation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).parent
BASE = HERE / "library-029-col07-column-member.json"
FIXTURE = HERE / "library-030-col07-two-plane-shear.json"


def requests() -> dict[str, dict]:
    """Extend the short tied specimen with a proposed interaction basis field."""
    request = deepcopy(json.loads(BASE.read_text())["cases"]["continuous"]["request"])
    request["schema_version"] = "column-member-detailing-input/v1"
    request["identity"]["case_id"] = "two_plane_pass"
    request["basis"][
        "action_source_reference"
    ] = "COL07 two-plane synthetic signed factored station worksheet"
    request["basis"][
        "two_plane_interaction_basis"
    ] = "bounded shared-transverse-reinforcement allocation v1"
    request["actions"] = [
        {
            "combination_id": "U1",
            "check_station_mm": 150,
            "pu_kn": 500,
            "mx_knm": 50,
            "my_knm": 35,
            "vx_kn": -50,
            "vy_kn": 60,
        }
    ]
    cases = {"two_plane_pass": request}
    cases["shared_reinforcement_fail"] = deepcopy(request)
    cases["shared_reinforcement_fail"]["identity"][
        "case_id"
    ] = "shared_reinforcement_fail"
    # Each directional check is below 1.0, while their shared-credit sum exceeds 1.0.
    cases["shared_reinforcement_fail"]["actions"][0].update(vx_kn=-70, vy_kn=90)
    cases["directional_capacity_fail"] = deepcopy(request)
    cases["directional_capacity_fail"]["identity"][
        "case_id"
    ] = "directional_capacity_fail"
    cases["directional_capacity_fail"]["actions"][0].update(vx_kn=-140, vy_kn=30)
    cases["interaction_basis_hold"] = deepcopy(request)
    cases["interaction_basis_hold"]["identity"]["case_id"] = "interaction_basis_hold"
    cases["interaction_basis_hold"]["basis"]["two_plane_interaction_basis"] = None
    cases["action_source_hold"] = deepcopy(request)
    cases["action_source_hold"]["identity"]["case_id"] = "action_source_hold"
    cases["action_source_hold"]["basis"]["action_source_reference"] = None
    return cases


def component(request: dict, action: dict, direction: str) -> dict:
    """One principal-plane, ordinary IS 456 component check at the base hoop pitch."""
    b, D = request["geometry"]["b_mm"], request["geometry"]["D_mm"]
    steel = request["reinforcement"]
    tie = steel["tie"]
    pitch = tie["spacing_mm"]
    setback = steel["bar_center_offset_mm"]
    web, d = (D, b - setback) if direction == "x" else (b, D - setback)
    fck = request["materials"]["fck_nmm2"]
    fy = min(request["tie_fy_nmm2"], 415.0)
    demand = action[f"v{direction}_kn"]
    axial_factor = min(1.5, 1 + 3000 * action["pu_kn"] / (b * D * fck))
    tc = 0.29  # M25 Table 19, deliberately lower 0.15% reinforcement row.
    vc = tc * axial_factor * web * d / 1000
    asv = 2 * math.pi * tie["diameter_mm"] ** 2 / 4
    vus = 0.87 * fy * asv * d / (1000 * pitch)
    tc_max = 3.1  # M25 Table 20.
    crushing = tc_max * web * d / 1000
    capacity = min(vc + vus, crushing)
    pitch_limit = min(0.75 * d, 300, 0.87 * fy * asv / (0.4 * web))
    return {
        "combination_id": action["combination_id"],
        "station_mm": action["check_station_mm"],
        "direction": direction,
        "signed_demand_kn": demand,
        "demand_kn": abs(demand),
        "web_width_mm": web,
        "d_mm": d,
        "pitch_mm": pitch,
        "pitch_limit_mm": pitch_limit,
        "link_spacing_pass": pitch <= pitch_limit,
        "credited_hoop_id": tie["tie_id"],
        "credited_legs": 2,
        "effective_hoop_area_mm2": asv,
        "axial_factor": axial_factor,
        "table_19_tc_nmm2": tc,
        "table_20_tc_max_nmm2": tc_max,
        "vc_kn": vc,
        "vus_kn": vus,
        "crushing_kn": crushing,
        "capacity_kn": capacity,
        "utilization": abs(demand) / capacity,
    }


def expected(name: str, request: dict) -> dict:
    action = request["actions"][0]
    hold = None
    if request["basis"].get("two_plane_interaction_basis") is None:
        hold = "COLUMN.TWO_PLANE_INTERACTION_BASIS_HELD"
    if request["basis"].get("action_source_reference") is None:
        hold = "COLUMN.MEMBER_BASIS_REQUIRED"
    if hold:
        return {
            "status": "HOLD",
            "issue": hold,
            "bbs_available": False,
            "checked_drawing_available": False,
            "evaluated_shear_rows": [],
            "governing_action": None,
            "physical_bbs_reference": None,
        }
    rows = [component(request, action, direction) for direction in ("x", "y")]
    assert all(row["link_spacing_pass"] for row in rows)
    interaction = sum(row["utilization"] for row in rows)
    directional_fail = any(row["utilization"] > 1 for row in rows)
    status = "FAIL" if directional_fail or interaction > 1 else "PASS"
    issue = (
        "COLUMN.SHEAR_CAPACITY"
        if directional_fail
        else "COLUMN.TWO_PLANE_SHARED_REINFORCEMENT" if interaction > 1 else None
    )
    assert (status, issue) == {
        "two_plane_pass": ("PASS", None),
        "shared_reinforcement_fail": ("FAIL", "COLUMN.TWO_PLANE_SHARED_REINFORCEMENT"),
        "directional_capacity_fail": ("FAIL", "COLUMN.SHEAR_CAPACITY"),
    }[name]
    base_expected = json.loads(BASE.read_text())["cases"]["continuous"]["expected"]
    return {
        "status": status,
        "issue": issue,
        "bbs_available": status == "PASS",
        "checked_drawing_available": status == "PASS",
        "evaluated_shear_rows": rows,
        "governing_action": {
            "combination_id": action["combination_id"],
            "station_mm": action["check_station_mm"],
            "interaction_utilization": interaction,
            "interaction_limit": 1.0,
            "check": issue or "COLUMN.TWO_PLANE_SHARED_REINFORCEMENT",
        },
        "physical_bbs_reference": {
            "source_case": "library-029-col07-column-member.json:continuous",
            "hoop_cut_mm": request["transverse_cut_schedule"]["cut_lengths_mm"]["H"],
            "hoop_stations_mm": base_expected["hoop_stations_mm"],
            "bbs_quantity": base_expected["bbs_quantity"],
            "bbs_length_mm": base_expected["bbs_length_mm"],
            "bbs_weight_kg": base_expected["bbs_weight_kg"],
        },
    }


def fixture() -> dict:
    cases = {
        name: {"request": value, "expected": expected(name, value)}
        for name, value in requests().items()
    }
    return {
        "schema_version": "library-030-col07-two-plane-shear-reference/v1",
        "frozen_production_base": "2f6dbf6413ebe8ffa637d8bf8649855c69e73bea",
        "base_fixture_sha256": hashlib.sha256(BASE.read_bytes()).hexdigest(),
        "sources": [
            "IS 456:2000 Cl. 26.5.1.5–6, 40.2.2, 40.2.3 and 40.4, Tables 19 and 20: ordinary principal-plane component equations and link limits. https://www.cracindia.in/admin/uploads/IS-456.pdf",
            "Behavior of reinforced concrete columns under biaxial shear forces based on ACI 318: rectangular test results support an elliptical interaction. The linear screen lies inside that curve for the same normalized directional capacities. The paper motivates the restriction, and does not validate this fixture's IS 456 capacities. https://www.sciencedirect.com/science/article/abs/pii/S0141029619302330",
            "COL07 continuous short tied rectangular physical specimen: signed actions, M25/Fe415 materials, H closed hoop, and BBS register.",
        ],
        "interaction_basis": {
            "name": "bounded shared-transverse-reinforcement allocation",
            "equation": "abs(Vx)/Vx_capacity + abs(Vy)/Vy_capacity <= 1.0",
            "engineering_rationale": "Both directional calculations credit the same closed H hoop. Normalize each demand by its full concrete-plus-hoop capacity, and limit the sum to one. For nonnegative normalized demands, the unit linear domain is contained in the unit elliptical domain. This is a conservative specimen acceptance screen relative to that ellipse.",
            "scope": "Independent COL07 evidence fixture only; not an IS 456 biaxial-shear prescription and not product implementation.",
        },
        "method": "Evaluate concurrent signed shears at U1, station 150 mm, using only the two legs of the closed H hoop in each principal plane. Cross-ties restrain longitudinal bars without additional shear credit. Require the pitch limits, each directional check and the declared linear interaction to pass. Retain the base specimen's unchanged P–M action, cage, end development, and cut schedule. Withhold checked drawing and BBS on FAIL or HOLD.",
        "absolute_tolerances": {
            "force_kn": 0.001,
            "ratio": 0.000001,
            "length_mm": 0.001,
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
        FIXTURE.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")
    else:
        assert (
            json.loads(FIXTURE.read_text()) == data
        ), "COL07 two-plane reference drifted"
    for name, case in data["cases"].items():
        print(f"PASS independent COL07 two-plane {name}: {case['expected']['status']}")


if __name__ == "__main__":
    main()
