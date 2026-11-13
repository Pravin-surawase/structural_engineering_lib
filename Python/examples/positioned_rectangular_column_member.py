"""Replay the independently frozen COL03 cases through the public column API."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from structural_lib.design.is456 import column

_REFERENCE = (
    Path(__file__).resolve().parents[2]
    / "docs/verification/library-029-col03-mixed-column.json"
)


def main() -> None:
    cases = json.loads(_REFERENCE.read_text(encoding="utf-8"))["cases"]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=cases, default="admitted_12_bar")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    request = column.load_positioned_rectangular_member(cases[args.case]["request"])
    result = column.check_positioned_rectangular_member(request)
    text = json.dumps(result.to_dict(), indent=2, allow_nan=False) + "\n"
    if args.output_dir is not None:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "result.json").write_text(text, encoding="utf-8")
        (args.output_dir / "report.html").write_text(
            column.render_positioned_rectangular_member_html(result), encoding="utf-8"
        )
    print(text, end="")


if __name__ == "__main__":
    main()
