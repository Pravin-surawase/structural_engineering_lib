#!/usr/bin/env python3
"""Generate and byte-check the catalogue-derived beam tool manifest.

When to use: After changing workflow catalogue or tool-manifest contracts. Use
``--write --check`` to regenerate the artifact and verify its exact bytes.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.utils import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "Python"))
from structural_lib.services.tool_manifest import serialize_tool_manifest

DEFAULT_OUTPUT = REPO_ROOT / "docs" / "reference" / "beam-tool-manifest.json"


def expected_manifest_text() -> str:
    """Return the canonical pretty-printed artifact bytes as text."""
    return serialize_tool_manifest(indent=2) + "\n"


def write_manifest(path: Path = DEFAULT_OUTPUT) -> None:
    """Write the deterministic manifest artifact."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(expected_manifest_text(), encoding="utf-8")


def check_manifest(path: Path = DEFAULT_OUTPUT) -> bool:
    """Return whether an existing artifact exactly matches catalogue output."""
    return (
        path.is_file() and path.read_text(encoding="utf-8") == expected_manifest_text()
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true", help="Regenerate the artifact")
    parser.add_argument("--check", action="store_true", help="Fail on artifact drift")
    args = parser.parse_args()

    if args.write:
        write_manifest(args.out)
        print(f"Wrote beam tool manifest: {args.out}")
    if args.check or not args.write:
        if not check_manifest(args.out):
            print(
                "ERROR: beam tool manifest is missing or stale. Run "
                "scripts/generate_beam_tool_manifest.py --write --check"
            )
            return 1
        print(f"Beam tool manifest matches catalogue: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
