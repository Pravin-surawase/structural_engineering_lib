#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Compatibility wrapper for the canonical public API manifest check.

Use ``generate_api_manifest.py --check`` for validation and
``generate_api_manifest.py`` to update ``docs/reference/api-manifest.json``.
This retained command delegates to that single source of truth so older
automation cannot create or compare a second private manifest.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GENERATOR = PROJECT_ROOT / "scripts" / "generate_api_manifest.py"


def main() -> int:
    """Delegate legacy invocations to the canonical manifest generator."""
    parser = argparse.ArgumentParser(
        description="Validate the canonical public API manifest"
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update docs/reference/api-manifest.json instead of checking it",
    )
    args = parser.parse_args()

    command = [sys.executable, str(GENERATOR)]
    if not args.update:
        command.append("--check")
    return subprocess.run(command, cwd=PROJECT_ROOT, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
