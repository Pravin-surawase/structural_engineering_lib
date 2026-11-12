"""Run the bounded COL02 six- and eight-bar column examples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from structural_lib.design.is456 import column

_LAYOUTS = (
    "eight_bar",
    "six_bar_omit_x_face_midpoints",
    "six_bar_omit_y_face_midpoints",
)


def member_input(
    layout: str = "eight_bar", mx_knm: float = 50, my_knm: float = 35
) -> dict:
    """Build the supplied short-column example for one of three layouts."""
    cross_ties = {
        "eight_bar": (
            ("XT", ("M_LEFT", "M_RIGHT"), 12),
            ("YT", ("M_TOP", "M_BOTTOM"), 24),
        ),
        "six_bar_omit_x_face_midpoints": (("YT", ("M_TOP", "M_BOTTOM"), 12),),
        "six_bar_omit_y_face_midpoints": (("XT", ("M_LEFT", "M_RIGHT"), 12),),
    }[layout]
    return {
        "identity": {
            "family_id": "column",
            "case_id": layout,
            "member_id": "COL02",
            "source_reference": "COL02 independent fixed-Pu reference",
        },
        "geometry": {
            "b_mm": 300,
            "D_mm": 400,
            "unsupported_length_mm": 3000,
            "end_condition": "FIXED_FIXED",
            "braced": True,
        },
        "actions": {
            "pu_kn": 500,
            "mx_knm": mx_knm,
            "my_knm": my_knm,
            "check_station_mm": 1500,
        },
        "materials": {"fck_nmm2": 25, "fy_nmm2": 415},
        "reinforcement": {
            "layout": layout,
            "longitudinal_bar_diameter_mm": 20,
            "bar_center_offset_mm": 60,
            "nominal_cover_mm": 40,
            "aggregate_size_mm": 20,
            "project_required_cover_mm": 40,
            "project_required_bend_radius_mm": 12,
            "detailing_basis_reference": "COL02 frozen ordinary tie section and reviewed project bend schedule",
            "tie": {
                "tie_id": "HOOP",
                "diameter_mm": 8,
                "spacing_mm": 150,
                "internal_bend_radius_mm": 12,
                "closed": True,
                "hook_angle_deg": 135,
                "hook_tail_mm": 60,
            },
            "cross_ties": [
                {
                    "tie_id": tie_id,
                    "restrained_bar_ids": list(bar_ids),
                    "station_offset_mm": offset,
                }
                for tie_id, bar_ids, offset in cross_ties
            ],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--layout", choices=_LAYOUTS, default="eight_bar")
    parser.add_argument("--mx", type=float, default=50, help="Signed kNm")
    parser.add_argument("--my", type=float, default=35, help="Signed kNm")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    request = column.load_tied_rectangular_member(
        member_input(args.layout, args.mx, args.my)
    )
    result = column.check_tied_rectangular_member(request)
    text = json.dumps(result.to_dict(), indent=2, allow_nan=False) + "\n"
    if args.output_dir is not None:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "result.json").write_text(text, encoding="utf-8")
        (args.output_dir / "report.html").write_text(
            column.render_tied_rectangular_member_html(result), encoding="utf-8"
        )
    print(text, end="")


if __name__ == "__main__":
    main()
