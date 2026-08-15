#!/usr/bin/env python3
"""Generate or verify the INDIA-0 Indian-code truth manifest."""

from __future__ import annotations

import argparse
import sys

from _lib.indian_code_manifest import MANIFEST_PATH, render_manifest


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate the standard-namespaced Indian-code capability and registration manifest"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="Write the canonical manifest")
    mode.add_argument("--check", action="store_true", help="Fail if the committed manifest is stale")
    args = parser.parse_args()

    rendered = render_manifest()
    if args.write:
        MANIFEST_PATH.write_text(rendered, encoding="utf-8")
        print(f"Wrote {MANIFEST_PATH}")
        return 0
    if args.check:
        if not MANIFEST_PATH.exists() or MANIFEST_PATH.read_text(encoding="utf-8") != rendered:
            print(
                "Indian-code manifest is stale; run "
                "./scripts/python_runtime.sh scripts/generate_indian_code_manifest.py --write",
                file=sys.stderr,
            )
            return 1
        print(f"Indian-code manifest is current: {MANIFEST_PATH}")
        return 0

    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
