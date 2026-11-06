"""Evaluate a layered rectangular column at two prescribed neutral-axis depths.

Run with python layered_column_section.py using a build that includes the
layered section API. The JSON contains the forces, strains and method identity
for each section response.
"""

from __future__ import annotations

import json

from structural_lib.design.is456 import column


def main() -> None:
    section = {
        "b_mm": 230,
        "D_mm": 450,
        "fck_nmm2": 20,
        "fy_nmm2": 415,
        "layers": [
            {"depth_from_top_mm": 50, "count": 3, "diameter_mm": 16},
            {"depth_from_top_mm": 225, "count": 2, "diameter_mm": 16},
            {"depth_from_top_mm": 400, "count": 3, "diameter_mm": 16},
        ],
    }
    responses = {}
    for name, xu_mm in (
        ("frozen_900mm", 900),
        ("full_depth_boundary", section["D_mm"]),
    ):
        request = column.load_layered_section({**section, "xu_mm": xu_mm})
        result = column.layered_section_response(request)
        responses[name] = result.model_dump(mode="json")
    print(json.dumps(responses, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
