"""Check a tied column and write the result, drawing and available BBS."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from structural_lib.core.errors import InputContractError
from structural_lib.design.is456 import column

_REFERENCE = (
    Path(__file__).resolve().parents[2]
    / "docs/verification/library-029-col07-column-member.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, default=_REFERENCE)
    parser.add_argument("--case", default="continuous", help="Case ID in the reference")
    profile = parser.add_mutually_exclusive_group()
    profile.add_argument(
        "--positioned",
        action="store_true",
        help="Use the positioned mixed member contract",
    )
    profile.add_argument(
        "--slender",
        action="store_true",
        help="Use the supplied second-order member contract",
    )
    parser.add_argument("--input", type=Path, help="A complete request JSON file")
    parser.add_argument(
        "--output-dir", type=Path, help="Fresh directory for this result"
    )
    args = parser.parse_args()
    if args.input is not None:
        payload = args.input.read_text(encoding="utf-8")
    else:
        if not args.reference.is_file():
            parser.error(
                "Supply the matching fixture via --reference or a request via --input."
            )
        cases = json.loads(args.reference.read_text(encoding="utf-8"))["cases"]
        if args.case not in cases:
            parser.error(f"Unknown case {args.case}. Choices: {', '.join(cases)}.")
        payload = cases[args.case]["request"]
    try:
        if args.positioned:
            request = column.load_positioned_column_member_detailing(payload)
        elif args.slender:
            request = column.load_slender_column_member_detailing(payload)
        else:
            request = column.load_column_member_detailing(payload)
    except InputContractError as exc:
        print(json.dumps(exc.to_problem(), indent=2))
        return 2

    result = column.check_column_member_detailing(request)
    serialized = json.dumps(result.to_dict(), indent=2, allow_nan=False) + "\n"
    if args.output_dir is not None:
        directory = args.output_dir
        names = ("result.json", "report.html", "member.svg", "bbs.csv")
        if any((directory / name).exists() for name in names):
            parser.error(
                "Use a fresh --output-dir so checked outputs from different runs do not mix."
            )
        directory.mkdir(parents=True, exist_ok=True)
        outputs = {
            "result.json": serialized,
            "report.html": column.render_column_member_detailing_html(result),
            "member.svg": column.render_column_member_detailing_svg(result),
            "bbs.csv": column.render_column_member_bbs_csv(result),
        }
        for name, content in outputs.items():
            if content is not None:
                (directory / name).write_text(content, encoding="utf-8")
    print(serialized, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
