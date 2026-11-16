"""Check continuous two-span beam detailing and export eligible review outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from structural_lib.design.is456 import beam

_REFERENCE = (
    Path(__file__).resolve().parents[2]
    / "docs/verification/library-029-beam05-member-detailing.json"
)


def physical_flange_fixture_input(frozen: dict[str, Any]) -> dict[str, Any]:
    """Translate the independent fixture axes to the normal detailing contract."""
    member_id = frozen["member_id"]
    beam_data = frozen["beam"]
    web, cap = frozen["web_links"], frozen["flange_links"]
    web_vertices, cap_vertices = web["vertices"], cap["vertices"]
    required = frozen["required_cover_mm"]
    stations = frozen["stations"]
    return {
        "identity": {
            "family_id": "beam",
            "case_id": "physical_flange",
            "member_id": member_id,
        },
        "stock_length_mm": 12000,
        "member": {
            **beam_data,
            "schema_version": "is456-layered-continuous-beam-check/v1",
            "member_id": member_id,
            "source_reference": "BEAM05 independent equal-span beam and perpendicular slab strip",
            "analysis_revision": frozen["analysis_revision"],
            "current_analysis_revision": frozen["analysis_revision"],
            "reinforcement_revision": frozen["reinforcement_revision"],
            "clear_cover_mm": web_vertices[1][1] - web["diameter_mm"] / 2,
            "aggregate_size_mm": frozen["maximum_aggregate_mm"],
            "bars": [
                {
                    "layer": 1,
                    **{
                        name: bar[name]
                        for name in (
                            "bar_id",
                            "face",
                            "x_from_left_mm",
                            "y_from_top_mm",
                            "diameter_mm",
                        )
                    },
                }
                for bar in beam_data["bars"]
            ],
            "straight_bars": {
                "start_mm": beam_data["bars"][0]["start_mm"],
                "end_mm": beam_data["bars"][0]["end_mm"],
                "source_reference": "Full straight web bars with covered ends",
            },
            "supports": [
                {"support_id": name, "centre_mm": x, "width_mm": width}
                for name, x, width in zip(
                    ("A", "B", "C"),
                    (
                        0,
                        beam_data["flange"]["zero_moment_distance_mm"] / 0.75,
                        max(st["x_mm"] for st in stations),
                    ),
                    frozen["support_widths_mm"],
                    strict=True,
                )
            ],
            "stations": stations,
            "combinations": [
                {
                    "combination_id": name,
                    "kind": "ULS",
                    "required_station_ids": [s["station_id"] for s in stations],
                }
                for name in dict.fromkeys(
                    row["combination_id"] for row in frozen["actions"]
                )
            ],
            "actions": frozen["actions"],
        },
        "link_detail": {
            "first_station_mm": web["stations_mm"][0],
            "last_station_mm": web["stations_mm"][-1],
            "internal_bend_radius_mm": web["centreline_radius_mm"]
            - web["diameter_mm"] / 2,
            "hook_vertex_leg_mm": web_vertices[0][1] - web_vertices[1][1],
            "hook_plane_offset_mm": web_vertices[3][0],
            "source_reference": "Independent web-link geometry with separated hook planes",
        },
        "physical_flange": {
            **{
                name: frozen[name]
                for name in (
                    "geometry_revision",
                    "analysis_revision",
                    "reinforcement_revision",
                    "flange_bars",
                    "slab_strip",
                )
            },
            "flange_links": {
                "mark": "FL8",
                "first_station_mm": cap["stations_mm"][0],
                "last_station_mm": cap["stations_mm"][-1],
                "spacing_mm": cap["stations_mm"][1] - cap["stations_mm"][0],
                "left_axis_mm": cap_vertices[1][1],
                "right_axis_mm": cap_vertices[3][1],
                "top_axis_mm": cap_vertices[1][2],
                "bottom_axis_mm": cap_vertices[2][2],
                "diameter_mm": cap["diameter_mm"],
                "internal_bend_radius_mm": cap["centreline_radius_mm"]
                - cap["diameter_mm"] / 2,
                "hook_vertex_leg_mm": cap_vertices[0][1] - cap_vertices[1][1],
                "hook_plane_offset_mm": (
                    cap_vertices[3][0] if len(cap_vertices) == 7 else None
                ),
                "closing_hook_vertex_leg_mm": (
                    cap_vertices[-1][2] - cap_vertices[5][2]
                    if len(cap_vertices) == 7
                    else None
                ),
            },
            "placement": {
                "maximum_assembly_translation_per_axis_mm": frozen["placement"][
                    "maximum_assembly_translation_per_axis_mm"
                ],
                "minimum_compaction_access_mm": frozen["minimum_compaction_access_mm"],
                "web_cover_mm": required["web_mm"],
                "flange_link_cover_mm": required["cap_mm"],
                "slab_cover_mm": required["slab_mm"],
            },
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, default=_REFERENCE)
    parser.add_argument("--case", default="continuous")
    parser.add_argument("--input", type=Path, help="A complete request JSON file")
    parser.add_argument("--edit-bar", help="Longitudinal bar ID to recheck")
    parser.add_argument("--edit-diameter-mm", type=float)
    parser.add_argument("--edit-centre-mm", type=float)
    parser.add_argument("--stiffness-dependent", action="store_true")
    parser.add_argument(
        "--output-dir", type=Path, help="Fresh directory for this result"
    )
    args = parser.parse_args()
    if args.input is not None:
        payload = args.input.read_text(encoding="utf-8")
    else:
        if not args.reference.is_file():
            parser.error("Supply the frozen fixture via --reference or use --input.")
        fixture = json.loads(args.reference.read_text(encoding="utf-8"))
        cases = fixture["cases"]
        if args.case not in cases:
            parser.error(f"Unknown case {args.case}. Choices are {', '.join(cases)}.")
        case = cases[args.case]
        payload = case["request"]
        if (
            fixture.get("fixture_version")
            == "library-030-beam05-physical-flange-reference/v1"
        ):
            payload = physical_flange_fixture_input(payload)
        if "placement" in case:
            payload = {**payload, "placement_envelope": case["placement"]}
    try:
        request = beam.load_continuous_detailing(payload)
    except beam.InputContractError as exc:
        print(json.dumps(exc.to_problem(), indent=2))
        return 2

    result = beam.check_continuous_detailing(request)
    if args.edit_bar is not None:
        if args.edit_diameter_mm is None:
            parser.error("--edit-bar requires --edit-diameter-mm")
        result = beam.recheck_continuous_bar_edit(
            request,
            result,
            beam.BeamBarEditV1(
                bar_id=args.edit_bar,
                diameter_mm=args.edit_diameter_mm,
                x_from_left_mm=args.edit_centre_mm,
            ),
            analysis_basis=(
                "reinforcement_dependent_stiffness"
                if args.stiffness_dependent
                else "fixed_supplied_actions"
            ),
        )
    output = json.dumps(result.to_dict(), indent=2, allow_nan=False) + "\n"
    if args.output_dir is not None:
        folder = args.output_dir
        if any(
            (folder / name).exists()
            for name in ("result.json", "report.html", "member.svg", "bbs.csv")
        ):
            parser.error("Use a fresh directory for this result and report.")
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "result.json").write_text(output, encoding="utf-8")
        (folder / "report.html").write_text(
            beam.render_continuous_detailing_html(result), encoding="utf-8"
        )
        drawing = beam.render_continuous_detailing_svg(result)
        schedule = beam.render_continuous_detailing_bbs_csv(result)
        if drawing is not None and schedule is not None:
            (folder / "member.svg").write_text(drawing, encoding="utf-8")
            (folder / "bbs.csv").write_text(schedule, encoding="utf-8")
    print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
