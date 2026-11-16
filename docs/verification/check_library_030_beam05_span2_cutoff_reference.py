"""Freeze a decreasing-x bottom cutoff in the rectangular second clear span."""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

from check_library_030_beam05_cutoff_reference import build as layered_reference
from check_library_030_beam05_t_lap_reference import LOADS_KNM, _span_actions

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "library-030-beam05-layered-cutoff.json"
TARGET = HERE / "library-030-beam05-span2-cutoff-reference.json"
END_MM = 8000
MIRROR = dict(
    A="C",
    AF="CF",
    S1="S2",
    BF1="BF2",
    B1="B2",
    B2="B1",
    BF2="BF1",
    S2="S1",
    CF="AF",
    C="A",
    **{"CUT-THEORETICAL": "CUT-THEORETICAL", "CUT-END": "CUT-END"},
)
DIRECTION = {"LEFT": "RIGHT", "RIGHT": "LEFT", "CONTINUOUS": "CONTINUOUS"}


def reflect_case(source, name, issue_codes):
    request = deepcopy(source["request"])
    request["identity"]["case_id"] = name
    member = request["member"]
    member["reinforcement_revision"] = f"{member['member_id']}-R1-{name}"
    left, centre, right = member["supports"]
    assert left["centre_mm"] + right["centre_mm"] == 2 * centre["centre_mm"] == END_MM
    assert left["width_mm"] == right["width_mm"]
    extent = member["straight_bars"]
    assert extent["start_mm"] + extent["end_mm"] == END_MM
    grid = request["link_detail"]
    assert grid["first_station_mm"] + grid["last_station_mm"] == END_MM

    stations = {station["station_id"]: station for station in member["stations"]}
    assert stations.keys() == MIRROR.keys()
    for station_id, other_id in MIRROR.items():
        station, other = stations[station_id], stations[other_id]
        if station_id.startswith("CUT-"):
            station["x_mm"] = END_MM - station["x_mm"]
        else:
            assert station["x_mm"] + other["x_mm"] == END_MM
            assert station["side"] == DIRECTION[other["side"]]

    original_actions = {
        row["row_id"]: row for row in source["request"]["member"]["actions"]
    }
    rows = {}
    for row in member["actions"]:
        cid, station_id = row["combination_id"], row["station_id"]
        station = stations[station_id]
        x = station["x_mm"]
        right_span = x > 4000 or (x == 4000 and station["side"] == "RIGHT")
        moment, shear = _span_actions(LOADS_KNM[cid], x, right_span=right_span)
        original = original_actions[f"{cid}:{MIRROR[station_id]}"]
        assert math.isclose(moment, original["mu_knm"], abs_tol=1e-9)
        assert math.isclose(shear, -original["vu_kn"], abs_tol=1e-9)
        assert original["tu_knm"] == row["tu_knm"] == 0
        row.update(mu_knm=moment, vu_kn=shear)
        rows[row["row_id"]] = row

    expected = deepcopy(source["expected"])
    expected.update(
        required_issue_codes=issue_codes,
        checked_drawing_available=expected["status"] == "PASS",
        bbs_available=expected["status"] == "PASS",
        report_available=True,
        cutoff_direction="decreasing_x",
    )
    theoretical = stations["CUT-THEORETICAL"]["x_mm"]
    termination = stations["CUT-END"]["x_mm"]
    assert 4150 < termination < theoretical < 7500
    assert 4500 <= termination < theoretical <= 7500
    expected.update(
        theoretical_station_mm=theoretical,
        termination_station_mm=termination,
        analysis_revision=member["analysis_revision"],
        current_analysis_revision=member["current_analysis_revision"],
    )
    if expected["status"] == "HOLD":
        expected["missing_required_rows"] = sorted(
            f"{combo['combination_id']}:{station_id}"
            for combo in member["combinations"]
            for station_id in combo["required_station_ids"]
            if f"{combo['combination_id']}:{station_id}" not in rows
        )
        return {"request": request, "expected": expected}

    extension = theoretical - termination
    assert math.isclose(extension, expected["available_extension_mm"], abs_tol=1e-9)
    assert math.isclose(
        extent["end_mm"] - termination, expected["cut_mm"], abs_tol=1e-9
    )
    assert (extension >= expected["development_mm"]) == (expected["status"] == "PASS")
    expected["physical_cut_bar_extent_mm"] = [termination, extent["end_mm"]]
    signed_reduced = {}
    for source_id, result in expected["reduced_rows"].items():
        cid, source_station = source_id.split(":")
        row_id = f"{cid}:{MIRROR[source_station]}"
        row = rows[row_id]
        station = stations[row["station_id"]]
        assert station["x_mm"] <= theoretical
        signed_reduced[row_id] = {
            **result,
            "station_mm": station["x_mm"],
            "moment_knm": row["mu_knm"],
            "shear_kn": row["vu_kn"],
            "diagnostic_only": station["x_mm"] in (0, 4000, 8000),
        }
    assert signed_reduced.keys() == {
        row_id
        for row_id, row in rows.items()
        if stations[row["station_id"]]["x_mm"] <= theoretical
    }
    expected["reduced_rows"] = signed_reduced
    at_end = {
        row_id: row
        for row_id, row in signed_reduced.items()
        if row_id.endswith(":CUT-END")
    }
    governor = max(at_end, key=lambda row_id: abs(at_end[row_id]["shear_kn"]))
    expected["governing_termination_shear"] = {
        "row_id": governor,
        "shear_kn": at_end[governor]["shear_kn"],
        "limit_kn": expected["termination_limit_kn"],
    }
    return {"request": request, "expected": expected}


def fixture():
    independent = layered_reference()
    assert independent == json.loads(SOURCE.read_text(encoding="utf-8"))
    cases = independent["cases"]
    return {
        "fixture_version": "library-030-beam05-span2-cutoff-reference/v1",
        "frozen_before_implementation": True,
        "frozen_production_base": "1b22725faa5413d650611bef55323ecbc5e1f594",
        "source": [SOURCE.name, sha256(SOURCE.read_bytes()).hexdigest()],
        "catalogue_window_mm": [4500, 7500],
        "method": {
            "boundary": "Reflect the rectangular first-span reference along the member station axis only. Retain the section, reinforcement, links and symmetric supports. Qualify one outer-bottom cutoff in the second clear span.",
            "statics": "Recompute signed U1 and U2 rows from three-moment statics and cross-check moment equality and shear reversal at each mirrored station. Exchange the left and right limits at the internal support.",
            "development": "Follow the cut bar in decreasing x from the theoretical station to its actual left end. Check the reduced cage from the theoretical station toward decreasing x, including the affected left support face. Keep the published section, spacing and cut-length checks.",
            "outputs": "Verify the actual start and continuing extent of the cut bar in the report and elevation and from the same resolved bar path in the BBS. Non-PASS cases retain a diagnostic report and withhold the checked drawing and BBS.",
        },
        "absolute_tolerances": {
            "length_mm": 0.001,
            "moment_knm": 0.01,
            "force_kn": 0.01,
            "ratio": 0.0001,
            "mass_kg": 0.001,
        },
        "cases": {
            "first_span_control": cases["rect_multilayer"],
            "span2_cutoff": reflect_case(cases["rect_multilayer"], "span2_cutoff", []),
            "short_development": reflect_case(
                cases["short_development"],
                "short_development",
                ["BEAM.CUTOFF_EXTENSION_FAIL"],
            ),
            "missing_action": reflect_case(
                cases["missing_action"], "missing_action", ["BEAM_ACTION_MISSING"]
            ),
            "stale_action": reflect_case(
                cases["stale_action"], "stale_action", ["BEAM_ANALYSIS_STALE"]
            ),
        },
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
        print(
            f"PASS independent BEAM05 span 2 cutoff {name}: {case['expected']['status']}"
        )


if __name__ == "__main__":
    main()
