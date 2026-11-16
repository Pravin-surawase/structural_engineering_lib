"""Freeze the right-flanged L-beam lap before implementing its checked route."""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

from check_library_030_beam05_t_lap_reference import expected, fixture as t_reference

HERE = Path(__file__).resolve().parent
L_CUTOFF = HERE / "library-030-beam05-layered-cutoff.json"
T_LAP = HERE / "library-030-beam05-t-lap-reference.json"
TARGET = HERE / "library-030-beam05-l-lap-reference.json"
BASE = "326ec8f0098c811d5127b8023fcc3229d57b2900"


def l_request(name, t_request, published_l):
    request = deepcopy(t_request)
    member, published_member = request["member"], published_l["member"]
    base_geometry = (
        "width_mm",
        "depth_mm",
        "fck_nmm2",
        "fy_nmm2",
        "supports",
        "straight_bars",
        "clear_cover_mm",
        "aggregate_size_mm",
        "link_diameter_mm",
        "link_spacing_mm",
        "link_fy_nmm2",
    )
    assert all(member[key] == published_member[key] for key in base_geometry)
    assert request["link_detail"] == published_l["link_detail"]
    # B2-3 would be left without an uninterrupted outer bar behind it.
    bars = [bar for bar in published_member["bars"] if bar["bar_id"] != "B2-3"]
    assert member["bars"] == bars
    published_stations = [
        row
        for row in published_member["stations"]
        if not row["station_id"].startswith("CUT-")
    ]
    assert published_stations == [
        row for row in member["stations"] if not row["station_id"].startswith("LAP-")
    ]
    bound_actions = {
        row["row_id"]: row
        for row in published_member["actions"]
        if not row["station_id"].startswith("CUT-")
    }
    assert bound_actions == {
        row["row_id"]: row
        for row in member["actions"]
        if not row["station_id"].startswith("LAP-")
    }
    assert request.get("cutoff") is None
    flange = deepcopy(published_member["flange"])
    assert flange["kind"] == "l_beam"
    assert flange["left_overhang_mm"] == 0 and flange["right_overhang_mm"] == 300
    member_id = published_member["member_id"]
    current = f"{member_id}-LAP-A1"
    stale = member["analysis_revision"] != member["current_analysis_revision"]
    member.update(
        member_id=member_id,
        flange=flange,
        bars=deepcopy(bars),
        analysis_revision=current,
        current_analysis_revision=f"{current}-EDITED" if stale else current,
        reinforcement_revision=f"{member_id}-LAP-R1-{name}",
        source_reference="BEAM05 right-flanged L beam, equal-EI two-span three-moment actions",
    )
    request["identity"].update(member_id=member_id, case_id=name)
    return request


def fixture():
    published_l = json.loads(L_CUTOFF.read_text())["cases"]["l_multilayer"]["request"]
    stored_t = json.loads(T_LAP.read_text())
    assert t_reference() == stored_t
    t_cases = stored_t["cases"]
    dispositions = {
        "l_lap": ("PASS", []),
        "short_overlap": ("FAIL", ["SPLICE.NONCOMPLIANT"]),
        "congested_partner": ("FAIL", ["SPACING.HORIZONTAL"]),
        "missing_lap_action": ("HOLD", ["BEAM_ACTION_MISSING"]),
        "stale_analysis": ("HOLD", ["BEAM_ANALYSIS_STALE"]),
    }
    cases = {"t_control": t_cases["t_lap"]}
    for name, (status, issues) in dispositions.items():
        t_case = t_cases["t_lap" if name == "l_lap" else name]
        request = l_request(name, t_case["request"], published_l)
        target = expected(request)
        assert (target["status"], target["required_issue_codes"]) == (status, issues)
        cases[name] = {"request": request, "expected": target}

    l_case = cases["l_lap"]
    l_result = l_case["expected"]
    t_result = cases["t_control"]["expected"]
    member = l_case["request"]["member"]
    flange = member["flange"]
    width_limit = (
        member["width_mm"]
        + flange["zero_moment_distance_mm"] / 12
        + 3 * flange["thickness_mm"]
    )
    assert (
        l_result["effective_flange_width_mm"]
        == l_result["physical_width_mm"]
        < width_limit
    )
    l_result["effective_flange_formula_limit_mm"] = width_limit
    l_result["effective_flange_governor"] = "physical_width"
    assert l_result["support_anchorage"] == t_result["support_anchorage"]
    for layout in ("upstream", "downstream"):
        l_strength = l_result["strength_by_layout"][layout]
        t_strength = t_result["strength_by_layout"][layout]
        for face in ("top", "bottom_web"):
            assert l_strength[face] == t_strength[face]
        assert (
            l_strength["bottom"]["shear_capacity_kn"]
            == t_strength["bottom"]["shear_capacity_kn"]
        )
        assert (
            l_strength["bottom"]["capacity_knm"] < t_strength["bottom"]["capacity_knm"]
        )
    for key in ("total_quantity", "total_length_mm", "total_mass_kg"):
        assert math.isclose(l_result["bbs"][key], t_result["bbs"][key])
    assert (
        l_result["drawing"]["section_outline_mm"]
        != t_result["drawing"]["section_outline_mm"]
    )
    overlap_rows = l_result["overlap_rows"]
    governing_lap_id = max(
        overlap_rows, key=lambda row_id: overlap_rows[row_id]["moment_knm"]
    )
    governing_lap = overlap_rows[governing_lap_id]
    combination_id, _ = governing_lap_id.split(":")
    continuous_interval = l_result["lap_interval_by_combination"][combination_id]
    assert governing_lap["moment_knm"] == continuous_interval["maximum_moment_knm"]
    l_result["governing_lap_row"] = {"row_id": governing_lap_id, **governing_lap}
    anchorage = l_result["support_anchorage"]
    straight_minimum = min(row["straight_available_mm"] for row in anchorage.values())
    development = {row["development_required_mm"] for row in anchorage.values()}
    assert len(development) == 1
    l_result["governing_straight_anchorage"] = {
        "tied_row_ids": sorted(
            row_id
            for row_id, row in anchorage.items()
            if row["straight_available_mm"] == straight_minimum
        ),
        "available_mm": straight_minimum,
        "required_mm": development.pop(),
    }
    for case in cases.values():
        case["expected"]["report_available"] = True
    return {
        "fixture_version": "library-030-beam05-l-lap-reference/v1",
        "frozen_before_implementation": True,
        "frozen_production_base": BASE,
        "bound_sources": {
            "published_l_multilayer": [
                L_CUTOFF.name,
                "l_multilayer",
                sha256(L_CUTOFF.read_bytes()).hexdigest(),
            ],
            "published_t_lap": [
                T_LAP.name,
                "t_lap",
                sha256(T_LAP.read_bytes()).hexdigest(),
            ],
        },
        "sources": [
            "IS 456:2000 Cl. 23.1.2, 26.2.1, 26.2.3.3, 26.2.5, 26.3.2, 26.5.1, 38 and 40 with Table 19. https://www.cracindia.in/admin/uploads/IS-456.pdf",
            "Published BEAM05 layered L cutoff and symmetric T lap inputs, with three-moment statics and independent section equilibrium and link takeoff.",
        ],
        "method": {
            "scope": "One separated Ø20 outer-bottom lap in span 1 of the prismatic right-flanged L web cage. Use two aligned inner bars, uniform closed web links and supplied vertical-plane ULS rows with zero torsion. Keep B2-3 omitted as in the symmetric T control. The result covers the declared in-plane actions, web reinforcement and bent links.",
            "actions": "Check the U1/U2 signed moment and shear pairs from 24/32 kN/m on equal 4 m spans with uniform stiffness and simple outer supports. Loads and reactions define a vertical-plane benchmark with no supplied torque or transverse action. Keep support-centre rows diagnostic.",
            "section": "Use the L expression bw + l0/12 + 3 Df, capped by the physical one-sided tributary width, for sagging compression. Monolithic flange participation and vertical-plane response are prescribed by the benchmark. Check that the neutral axis lies in the flange. Use the web for hogging compression and signed shear. Flange reinforcement, lateral flexure and torsion transfer require separate evidence.",
            "lap_window": "Screen the entire positive-moment interval using its analytical extrema and the declared half-sagging-resistance limit. Verify M/V from both single-partner transfer layouts. Check straight development, spliced fraction, cover, clearances and link pitch. Count and draw both physical partners inside the overlap.",
            "support": "Check straight development in the physical support direction using each support-face row. For positive anchorage, compare the three-times-projection limit with the web-only flexural resistance divided by the concurrent shear plus extension beyond the support centre.",
            "outputs": "The checked report identifies the L profile, effective flange, lap transfer rows and governing acceptance and anchorage checks. The elevation, three physical sections and BBS use the same checked paths and current revisions. FAIL and HOLD specify diagnostic report availability and withhold the checked drawing and BBS.",
        },
        "absolute_tolerances": stored_t["absolute_tolerances"],
        "cases": cases,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args()
    data = fixture()
    if args.freeze:
        TARGET.write_text(
            json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8"
        )
    else:
        assert json.loads(TARGET.read_text(encoding="utf-8")) == data
    for name, case in data["cases"].items():
        print(f"PASS independent BEAM05 L lap {name}: {case['expected']['status']}")


if __name__ == "__main__":
    main()
