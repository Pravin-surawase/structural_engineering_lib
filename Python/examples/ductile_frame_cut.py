"""Evaluate a signed two-joint ductile frame cut and its review artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from structural_lib.core.errors import InputContractError
from structural_lib.design.is13920 import frame


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        request = frame.load_frame(args.request.read_bytes())
        result = frame.check_frame(request)
    except InputContractError as exc:
        print(json.dumps(exc.to_problem()))
        return 2

    directory = args.output_dir
    directory.mkdir(parents=True, exist_ok=True)
    for filename, content in (
        ("frame.svg", frame.render_frame_svg(result, current=request)),
        ("bbs.csv", frame.render_frame_bbs_csv(result, current=request)),
        ("report.html", frame.render_frame_html(result)),
    ):
        output = directory / filename
        if content is None:
            output.unlink(missing_ok=True)
        else:
            output.write_text(content, encoding="utf-8")
    payload = json.dumps(result.to_dict(), allow_nan=False) + "\n"
    (directory / "result.json").write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
