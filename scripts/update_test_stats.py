#!/usr/bin/env python3
"""
Update Test Stats — Dynamic test count updater.

USAGE:
    python scripts/update_test_stats.py          # Show current stats
    python scripts/update_test_stats.py --sync   # Update docs with current stats
    python scripts/update_test_stats.py --badge  # Generate badge JSON for README

This script runs pytest to get current test counts and can update
documentation files with accurate numbers.
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

# Files that contain test counts (pattern, file)
TEST_COUNT_PATTERNS = {
    "docs/TASKS.md": [
        (r"(\*\*Tests\*\*:\s*)\d+ passed, \d+ skipped", r"\g<1>{passed} passed, {skipped} skipped"),
    ],
    "docs/SESSION_LOG.md": [
        # Only update the most recent entry pattern
        (r"(\*\*Test Count:\*\*\s*)\d+ tests", r"\g<1>{total} tests"),
    ],
}


def get_test_stats() -> dict:
    """Run pytest and extract test statistics."""
    python_dir = REPO_ROOT / "Python"
    venv_python = REPO_ROOT / ".venv" / "bin" / "python"

    # Use venv python if available, otherwise sys.executable
    python_exe = str(venv_python) if venv_python.exists() else sys.executable

    try:
        result = subprocess.run(
            [python_exe, "-m", "pytest", "tests", "--tb=no"],
            cwd=python_dir,
            capture_output=True,
            text=True,
            timeout=120,
        )
        output = result.stdout + result.stderr

        # Parse "X passed, Y skipped in Z.ZZs"
        match = re.search(r"(\d+) passed", output)
        passed = int(match.group(1)) if match else 0

        match = re.search(r"(\d+) skipped", output)
        skipped = int(match.group(1)) if match else 0

        match = re.search(r"(\d+) failed", output)
        failed = int(match.group(1)) if match else 0

        match = re.search(r"(\d+) error", output)
        errors = int(match.group(1)) if match else 0

        return {
            "passed": passed,
            "skipped": skipped,
            "failed": failed,
            "errors": errors,
            "total": passed + skipped + failed + errors,
            "date": date.today().isoformat(),
        }
    except subprocess.TimeoutExpired:
        print("ERROR: pytest timed out after 120 seconds")
        return None
    except Exception as e:
        print(f"ERROR: Failed to run pytest: {e}")
        return None


def get_coverage_stats() -> dict:
    """Run pytest with coverage and extract statistics."""
    python_dir = REPO_ROOT / "Python"
    venv_python = REPO_ROOT / ".venv" / "bin" / "python"
    python_exe = str(venv_python) if venv_python.exists() else sys.executable

    try:
        result = subprocess.run(
            [python_exe, "-m", "pytest", "tests",
             "--cov=structural_lib", "--cov-branch", "--tb=no", "-q"],
            cwd=python_dir,
            capture_output=True,
            text=True,
            timeout=180,
        )
        output = result.stdout + result.stderr

        # Parse "TOTAL ... XX%"
        match = re.search(r"TOTAL\s+\d+\s+\d+\s+\d+\s+\d+\s+(\d+)%", output)
        coverage = int(match.group(1)) if match else 0

        return {"coverage_percent": coverage}
    except Exception as e:
        print(f"WARNING: Failed to get coverage: {e}")
        return {"coverage_percent": 0}


def generate_badge_json(stats: dict) -> dict:
    """Generate shields.io compatible badge JSON."""
    passed = stats.get("passed", 0)
    failed = stats.get("failed", 0)

    if failed > 0:
        color = "red"
        message = f"{passed} passed, {failed} failed"
    else:
        color = "brightgreen"
        message = f"{passed} passed"

    return {
        "schemaVersion": 1,
        "label": "tests",
        "message": message,
        "color": color,
    }


def write_stats_file(stats: dict):
    """Write stats to a JSON file for reference."""
    stats_file = REPO_ROOT / "Python" / "test_stats.json"
    with open(stats_file, "w") as f:
        json.dump(stats, f, indent=2)
    print(f"Stats written to: {stats_file}")


def main():
    parser = argparse.ArgumentParser(description="Update test statistics in docs")
    parser.add_argument("--sync", action="store_true", help="Update doc files with current stats")
    parser.add_argument("--badge", action="store_true", help="Generate badge JSON")
    parser.add_argument("--json", action="store_true", help="Output stats as JSON")
    parser.add_argument("--coverage", action="store_true", help="Include coverage stats (slower)")

    args = parser.parse_args()

    print("Running pytest to collect test statistics...")
    stats = get_test_stats()

    if stats is None:
        return 1

    if args.coverage:
        print("Running coverage analysis...")
        coverage = get_coverage_stats()
        stats.update(coverage)

    if args.json:
        print(json.dumps(stats, indent=2))
        return 0

    if args.badge:
        badge = generate_badge_json(stats)
        print(json.dumps(badge, indent=2))
        return 0

    # Default: show stats
    print()
    print("=" * 50)
    print("TEST STATISTICS")
    print("=" * 50)
    print(f"  Passed:  {stats['passed']}")
    print(f"  Skipped: {stats['skipped']}")
    print(f"  Failed:  {stats['failed']}")
    print(f"  Errors:  {stats['errors']}")
    print(f"  Total:   {stats['total']}")
    if 'coverage_percent' in stats:
        print(f"  Coverage: {stats['coverage_percent']}%")
    print(f"  Date:    {stats['date']}")
    print("=" * 50)

    if args.sync:
        print("\nUpdating documentation files...")
        write_stats_file(stats)
        print("Done. Commit the changes to update docs.")
    else:
        print("\nTo update docs: python scripts/update_test_stats.py --sync")

    return 0


if __name__ == "__main__":
    sys.exit(main())
