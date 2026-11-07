"""Check an ordinary four-corner column and export matching JSON and HTML.

Run with python four_corner_column_member.py --output-dir column-output.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from structural_lib.design.is456 import column


def member_input(axis: str = "x") -> dict:
    return {
        "identity": {
            "family_id": "column",
            "case_id": f"LIB-027-C-{axis}",
            "member_id": "C1",
            "source_reference": "LIB-027-C-001 independent reference",
        },
        "geometry": {
            "b_mm": 300,
            "D_mm": 400,
            "unsupported_length_mm": 3000,
            "end_condition": "FIXED_FIXED",
            "braced": True,
        },
        "actions": {"pu_kn": 500, "moment_knm": 50, "bending_axis": axis},
        "materials": {"fck_nmm2": 25, "fy_nmm2": 415},
        "reinforcement": {
            "longitudinal_bar_diameter_mm": 20,
            "nominal_cover_mm": 40,
            "corner_inset_mm": 2,
            "aggregate_size_mm": 20,
            "project_required_cover_mm": 40,
            "project_required_bend_radius_mm": 16,
            "detailing_basis_reference": "LIB-027-C-001 project cover, aggregate and bend schedule",
            "tie": {
                "tie_id": "T1",
                "diameter_mm": 8,
                "spacing_mm": 300,
                "internal_bend_radius_mm": 16,
                "closed": True,
                "hook_angle_deg": 135,
                "hook_tail_mm": 48,
            },
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("column-output"))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    summaries = {}
    for name in ("axis_x", "axis_y", "overload", "insufficient_tie", "missing_tie"):
        payload = member_input("y" if name == "axis_y" else "x")
        if name == "overload":
            payload["actions"]["pu_kn"] *= 3
            payload["actions"]["moment_knm"] *= 3
        if name == "insufficient_tie":
            payload["reinforcement"]["tie"]["diameter_mm"] = 4
            payload["reinforcement"]["tie"]["spacing_mm"] = 350
        if name == "missing_tie":
            payload["reinforcement"]["tie"] = None
        request = column.load_four_corner_member(payload)
        result = column.check_four_corner_member(request)
        (args.output_dir / f"{name}.json").write_text(
            json.dumps(result.to_dict(), indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        (args.output_dir / f"{name}.html").write_text(
            column.render_four_corner_member_html(result), encoding="utf-8"
        )
        summaries[name] = {
            "status": result.engineering_status.value,
            "input_hash": result.envelope.result_identity.input_hash,
            "utilization": (result.calculation["strength"] or {}).get(
                "utilization_ratio"
            ),
        }
    print(json.dumps(summaries, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
