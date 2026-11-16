"""Check a regular IS 13920 joint from a versioned JSON request."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from structural_lib.core.errors import InputContractError
from structural_lib.design.is13920 import joint


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    try:
        request = joint.load_joint(args.request.read_bytes())
        result = joint.check_joint(request)
    except InputContractError as exc:
        print(json.dumps(exc.to_problem()))
        return 2

    serialized = json.dumps(result.to_dict(), allow_nan=False) + "\n"
    if args.output_dir is not None:
        output = args.output_dir
        output.mkdir(parents=True, exist_ok=True)
        for name, contents in (
            ("joint.svg", joint.render_joint_svg(result, current=request)),
            ("bbs.csv", joint.render_joint_bbs_csv(result, current=request)),
        ):
            path = output / name
            if contents is None:
                path.unlink(missing_ok=True)
            else:
                path.write_text(contents, encoding="utf-8")
        (output / "result.json").write_text(serialized, encoding="utf-8")
        (output / "report.html").write_text(
            joint.render_joint_html(result, current=request), encoding="utf-8"
        )
    print(serialized, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
