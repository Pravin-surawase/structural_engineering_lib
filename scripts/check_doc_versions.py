#!/usr/bin/env python3
"""Doc Version Drift Check — Validate no stale *library* version references in docs.

This is intentionally a thin wrapper around scripts/bump_version.py to ensure:
- The check is aligned with the project's supported auto-fix path.
- CI only fails on references that can be synced via `--sync-docs`.

USAGE:
    python scripts/check_doc_versions.py          # Report drift (non-failing)
    python scripts/check_doc_versions.py --fix    # Auto-fix with bump_version.py --sync-docs
    python scripts/check_doc_versions.py --ci     # Exit non-zero if drift found
"""

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
BUMP_SCRIPT = REPO_ROOT / "scripts" / "bump_version.py"


def run_bump_version(args: list[str]) -> int:
    """Run bump_version.py with provided args and return exit code."""
    result = subprocess.run([sys.executable, str(BUMP_SCRIPT), *args])
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Check for doc version drift")
    parser.add_argument("--fix", action="store_true", help="Auto-fix with bump_version.py --sync-docs")
    parser.add_argument("--ci", action="store_true", help="Exit with error code if drift found")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show all checked patterns")

    args = parser.parse_args()

    if args.fix:
        print("Attempting auto-fix with bump_version.py --sync-docs...")
        rc = run_bump_version(["--sync-docs"])
        if rc == 0:
            print("✓ Auto-fix complete. Re-run to verify.")
        return rc

    if args.verbose:
        print("Delegating to: python scripts/bump_version.py --check-docs")
        print()

    rc = run_bump_version(["--check-docs"])
    if rc == 0:
        return 0

    if args.ci:
        print("CI mode: failing due to version drift.")
        print("Run: python scripts/check_doc_versions.py --fix")
        return 1

    # Non-CI mode: report-only (don't fail the command)
    print("To fix: python scripts/check_doc_versions.py --fix")
    return 0


if __name__ == "__main__":
    sys.exit(main())
