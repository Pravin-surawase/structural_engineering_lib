"""Check continuous two-span beam detailing and export eligible review outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from structural_lib.design.is456 import beam

_REFERENCE = (
    Path(__file__).resolve().parents[2]
    / "docs/verification/library-029-beam05-member-detailing.json"
)


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
        cases = json.loads(args.reference.read_text(encoding="utf-8"))["cases"]
        if args.case not in cases:
            parser.error(f"Unknown case {args.case}. Choices are {', '.join(cases)}.")
        payload = cases[args.case]["request"]
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
