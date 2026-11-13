"""Exhaustively enumerate the frozen two-layer beam catalogue independently."""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from itertools import product
from pathlib import Path

from check_library_029_beam_sections_reference import section

ROOT = Path(__file__).resolve().parent
FIXTURE = ROOT / "library-029-flow02-beam-catalogue.json"
TABLE_19_M30 = (
    (0.25, 0.37),
    (0.50, 0.50),
    (0.75, 0.59),
    (1, 0.66),
    (1.25, 0.71),
    (1.50, 0.76),
    (1.75, 0.80),
    (2, 0.84),
    (2.25, 0.88),
    (2.50, 0.91),
    (2.75, 0.94),
    (3.00, 0.96),
)


def fixture():
    cases = json.loads((ROOT / "library-029-beam03-beam04-sections.json").read_text())[
        "cases"
    ]
    member = deepcopy(cases["multilayer"]["request"])
    # The independent BEAM04 hogging overload stays in its own fixture.
    # This catalogue varies bottom steel while retaining usable top demand.
    member["actions"][1]["mu_knm"] = -95
    member["reinforcement_revision"] = "B05-R-catalogue"
    request = {
        "identity": {"family_id": "beam", "case_id": "FLOW02-B05", "member_id": "B05"},
        "member": member,
        "layers": [
            {
                "layer": layer,
                "options": [
                    {
                        "option_id": f"{count}x{diameter}",
                        "diameter_mm": diameter,
                        "x_from_left_mm": [
                            55 + i * 190 / (count - 1) for i in range(count)
                        ],
                    }
                    for count, diameter in product((2, 3, 4), (16, 20, 25))
                ],
            }
            for layer in (1, 2)
        ],
        "evaluation_limit": 81,
        "analysis_basis": "fixed_supplied_actions",
    }
    evaluated = {}
    for left, right in product(*(layer["options"] for layer in request["layers"])):
        candidate = deepcopy(member)
        fixed = [bar for bar in member["bars"] if bar["face"] == "top"]
        candidate["bars"] = fixed + [
            {
                "bar_id": f"B{layer}-{index}",
                "face": "bottom",
                "layer": layer,
                "diameter_mm": option["diameter_mm"],
                "x_from_left_mm": x,
                "y_from_top_mm": depth,
            }
            for layer, depth, option in ((1, 520, left), (2, 450, right))
            for index, x in enumerate(option["x_from_left_mm"], 1)
        ]
        results = {
            face: section(candidate, face, None, TABLE_19_M30)
            for face in ("top", "bottom")
        }
        status = "PASS"
        row_scores = []
        for action in candidate["actions"]:
            state = results["top" if action["mu_knm"] < 0 else "bottom"]
            m = abs(action["mu_knm"]) / state["capacity_knm"]
            v = abs(action["vu_kn"]) / state["shear_capacity_kn"]
            row_scores.append((max(m, v), action["row_id"]))
            if state["over_reinforced"] or m > 1 or v > 1:
                status = "FAIL"
        area = math.fsum(
            math.pi * bar["diameter_mm"] ** 2 / 4
            for bar in candidate["bars"]
            if bar["face"] == "bottom"
        )
        key = f"{left['option_id']}/{right['option_id']}"
        evaluated[key] = {
            "status": status,
            "bottom_area_mm2": area,
            "rank": [area, len(candidate["bars"]) - len(fixed), key],
            "governing_row_id": min(row_scores, key=lambda item: (-item[0], item[1]))[
                1
            ],
            "capacities_knm": {
                face: result["capacity_knm"] for face, result in results.items()
            },
        }
    ranked = sorted(
        (key for key, row in evaluated.items() if row["status"] == "PASS"),
        key=lambda key: evaluated[key]["rank"],
    )
    return {
        "fixture_version": "library-029-flow02-beam-catalogue-reference/v1",
        "sources": [
            "BEAM04 rectangular section; finite two-layer positions and diameters.",
            "IS 456 signed independent strain equilibrium and Table 19 interpolation.",
            "Catalogue rank uses total variable area, number of variable bars and option IDs.",
        ],
        "request": request,
        "expected": {
            "evaluated": evaluated,
            "eligible_ids": ranked,
            "selected_id": ranked[0],
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args()
    data = fixture()
    if args.freeze:
        FIXTURE.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")
    else:
        assert json.loads(FIXTURE.read_text()) == data
    print(
        f"Independent FLOW02 reference: {len(data['expected']['evaluated'])} candidates"
    )


if __name__ == "__main__":
    main()
