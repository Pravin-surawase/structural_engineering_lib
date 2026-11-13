"""Run a checked slender rectangular column and write its local outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from structural_lib.core.errors import InputContractError
from structural_lib.design.is456 import column

_REFERENCE = (
    Path(__file__).resolve().parent
    / ".."
    / ".."
    / "docs/verification/library-029-col04-slender-column.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, default=_REFERENCE)
    parser.add_argument(
        "--case", default="minor_slender", help="Case ID in the reference"
    )
    parser.add_argument("--input", type=Path, help="One complete request JSON file")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    if args.input is not None:
        payload = args.input.read_text(encoding="utf-8")
    else:
        if not args.reference.is_file():
            parser.error(
                "Supply the matching frozen JSON via --reference or a request via --input."
            )
        cases = json.loads(args.reference.read_text(encoding="utf-8"))["cases"]
        if args.case not in cases:
            parser.error(f"Unknown case {args.case}. Choices: {', '.join(cases)}.")
        payload = cases[args.case]["request"]

    try:
        request = column.load_slender_rectangular_member(payload)
    except InputContractError as exc:
        print(json.dumps(exc.to_problem(), indent=2))
        return 2

    result = column.check_slender_rectangular_member(request)
    serialized = json.dumps(result.to_dict(), indent=2, allow_nan=False) + "\n"
    if args.output_dir is not None:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        outputs = {
            "result.json": serialized,
            "report.html": column.render_slender_rectangular_member_html(result),
            "section.svg": column.render_slender_rectangular_member_svg(result),
        }
        for name, content in outputs.items():
            (args.output_dir / name).write_text(content, encoding="utf-8")
    print(serialized, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
