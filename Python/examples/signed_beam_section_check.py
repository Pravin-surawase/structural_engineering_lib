"""Check a signed beam section with actual bar layers and write the revision-bound report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from structural_lib.design.is456 import beam

_REFERENCE = (
    Path(__file__).resolve().parents[2]
    / "docs/verification/library-029-beam03-beam04-sections.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, default=_REFERENCE)
    parser.add_argument("--case", default="l")
    parser.add_argument("--input", type=Path, help="A complete request JSON file")
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
        request = beam.load_section(payload)
    except beam.InputContractError as exc:
        print(json.dumps(exc.to_problem(), indent=2))
        return 2

    result = beam.check_section(request)
    output = json.dumps(result.to_dict(), indent=2, allow_nan=False) + "\n"
    if args.output_dir is not None:
        folder = args.output_dir
        if any((folder / name).exists() for name in ("result.json", "report.html")):
            parser.error("Use a fresh directory for this result and report.")
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "result.json").write_text(output, encoding="utf-8")
        (folder / "report.html").write_text(
            beam.render_section_html(result), encoding="utf-8"
        )
    print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
