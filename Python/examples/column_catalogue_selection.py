"""Select a short tied rectangular column and write its checked outputs."""

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
    / "docs/verification/library-029-col06-column-catalogue.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, default=_REFERENCE)
    parser.add_argument("--case", default="nominal", help="Case ID in the reference")
    parser.add_argument("--input", type=Path, help="One complete request JSON file")
    parser.add_argument(
        "--output-dir", type=Path, help="Use a fresh directory for each result"
    )
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
        request = column.load_column_catalogue(payload)
    except InputContractError as exc:
        print(json.dumps(exc.to_problem(), indent=2))
        return 2

    result = column.select_column_from_catalogue(request)
    serialized = json.dumps(result.to_dict(), indent=2, allow_nan=False) + "\n"
    if args.output_dir is not None:
        directory = args.output_dir
        if any(
            (directory / name).exists()
            for name in ("result.json", "report.html", "section.svg")
        ):
            parser.error(
                "Use a fresh --output-dir so results from different runs do not mix."
            )
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "result.json").write_text(serialized, encoding="utf-8")
        (directory / "report.html").write_text(
            column.render_column_catalogue_html(result), encoding="utf-8"
        )
        svg = column.render_column_catalogue_svg(result)
        if svg is not None:
            (directory / "section.svg").write_text(svg, encoding="utf-8")
    print(serialized, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
