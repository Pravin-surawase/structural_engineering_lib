#!/usr/bin/env python3
"""Fail if tracked hygiene artifacts exist in the repository."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys


ARTIFACT_NAMES = {".DS_Store", ".coverage"}


def _tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        print("ERROR: git ls-files failed.", file=sys.stderr)
        print(result.stderr.strip(), file=sys.stderr)
        return []
    return [path for path in result.stdout.split("\0") if path]


def main() -> int:
    tracked = [path for path in _tracked_files() if Path(path).name in ARTIFACT_NAMES]
    if tracked:
        print("ERROR: tracked hygiene artifacts detected:")
        for path in tracked:
            print(f" - {path}")
        print("Remove these files; they should be ignored.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
