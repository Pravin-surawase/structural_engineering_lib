#!/usr/bin/env python3
"""Compatibility bridge from the retired global docs index to live context.

When to use: Only for an older caller that still invokes the former generator.
Use ./run.sh context show docs or ./run.sh context summary docs for current
documentation routing without a committed generated catalogue.
"""

from __future__ import annotations

import argparse
import sys

from repo_context import main as context_main


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Deprecated read-only bridge to live documentation context"
    )
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    print(
        "DEPRECATED: docs/docs-index.json is retired; "
        "use ./run.sh context summary docs."
    )
    if args.write:
        print(
            "ERROR: the global generated docs index is no longer written",
            file=sys.stderr,
        )
        return 2
    return context_main(["summary", "docs"])


if __name__ == "__main__":
    raise SystemExit(main())
