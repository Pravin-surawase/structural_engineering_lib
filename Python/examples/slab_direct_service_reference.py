"""Replay a frozen positioned slab service case through the public Python API."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from structural_lib.design.is456 import slab


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--case", default="b01_service_history")
    args = parser.parse_args()
    cases = json.loads(args.fixture.read_text(encoding="utf-8"))["cases"]
    if args.case not in cases:
        parser.error(f"unknown case {args.case!r}; choose from {', '.join(cases)}")
    request = slab.load_direct_service(cases[args.case]["request"])
    result = slab.check_direct_service(request)
    print(json.dumps({"case": args.case, "result": result.to_dict()}, allow_nan=False))


if __name__ == "__main__":
    main()
