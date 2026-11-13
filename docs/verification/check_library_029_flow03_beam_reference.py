"""Freeze physical bar edit quantities independently of production checks."""

import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / "library-029-flow03-beam-edit.json"


def reference():
    prior = json.loads((HERE / "library-029-beam05-cutoff.json").read_text())
    cutoff = prior["cases"]["cutoff"]
    length = cutoff["expected"]["cut_mm"]
    prior_mass = cutoff["expected"]["mass_kg"]
    edited_diameter = 16
    mass = prior_mass + math.pi / 4 * (edited_diameter**2 - 20**2) * length * 7850e-9
    return {
        "bar_id": "bottom-3",
        "edited_diameter_mm": edited_diameter,
        "edited_cut_mm": length,
        "edited_mass_kg": mass,
        "congested_centre_mm": 175,
        "congested_clear_gap_mm": 175 - 150 - (20 + edited_diameter) / 2,
        "required_clear_gap_mm": 25,
        "states": {
            "edited": "PASS",
            "congested": "FAIL",
            "stale_base": "HOLD",
            "changed_stiffness": "HOLD",
        },
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args()
    expected = reference()
    if args.freeze:
        TARGET.write_text(json.dumps(expected, indent=2) + "\n")
    else:
        assert json.loads(TARGET.read_text()) == expected
    print("Independent FLOW03 beam edit reference: 4 cases")
