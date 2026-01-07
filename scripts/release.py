#!/usr/bin/env python3
"""
Release Helper Script — One-command release workflow.

USAGE:
    python scripts/release.py 0.9.7           # Full release flow
    python scripts/release.py 0.9.7 --dry-run # Preview what would happen
    python scripts/release.py --checklist     # Show release checklist only

This script:
1. Bumps version via bump_version.py
2. Syncs doc versions/dates
3. Prints release checklist
4. Opens CHANGELOG.md for editing (macOS only)
"""

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
BUMP_SCRIPT = REPO_ROOT / "scripts" / "bump_version.py"


def run_command(cmd: list, dry_run: bool = False) -> bool:
    """Run a command and return success status."""
    if dry_run:
        print(f"  [DRY-RUN] Would run: {' '.join(cmd)}")
        return True

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr}")
        return False
    if result.stdout:
        for line in result.stdout.strip().split("\n"):
            print(f"  {line}")
    return True


def print_checklist(version: str):
    """Print the release checklist."""
    print()
    print("=" * 60)
    print("RELEASE CHECKLIST")
    print("=" * 60)
    print()
    print(f"Version: v{version}")
    print()
    print("Automated (done by this script):")
    print("  ✓ Version bumped in pyproject.toml, api.py, M08_API.bas")
    print("  ✓ Doc version references synced")
    print("  ✓ Doc dates updated to today")
    print()
    print("Manual steps (you must do these):")
    print("  [ ] 1. Edit CHANGELOG.md — Add release notes")
    print("  [ ] 2. Edit docs/releases.md — Add release entry")
    print("  [ ] 3. Review changes: git diff")
    print("  [ ] 4. Commit: git add -A && git commit -m 'chore: release v{}'".format(version))
    print("  [ ] 5. Create PR and merge to main")
    print("  [ ] 6. Tag: git tag v{} && git push origin v{}".format(version, version))
    print("  [ ] 7. GitHub Release will trigger PyPI publish")
    print()
    print("Verification:")
    print("  [ ] Check PyPI: pip install structural-lib-is456=={}".format(version))
    print("  [ ] Clean-venv verify: python scripts/verify_release.py --version {} --source pypi".format(version))
    print("  [ ] Check GitHub Release page")
    print()


def open_file_in_editor(filepath: Path):
    """Open a file in the default editor (macOS)."""
    try:
        subprocess.run(["open", str(filepath)], check=True)
        print(f"  Opened: {filepath}")
    except Exception as e:
        print(f"  (Could not open {filepath}: {e})")


def main():
    parser = argparse.ArgumentParser(description="Release helper script")
    parser.add_argument("version", nargs="?", help="New version (e.g., 0.9.7)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without making changes")
    parser.add_argument("--checklist", action="store_true", help="Show checklist only")
    parser.add_argument("--no-open", action="store_true", help="Don't open files in editor")

    args = parser.parse_args()

    if args.checklist:
        if not args.version:
            # Read current version
            result = subprocess.run(
                [sys.executable, str(BUMP_SCRIPT), "--current"],
                capture_output=True, text=True
            )
            current = result.stdout.strip().replace("Current version: ", "")
            print(f"Current version: {current}")
            print("\nUsage: python scripts/release.py <new_version>")
            print("Example: python scripts/release.py 0.9.7")
        else:
            print_checklist(args.version)
        return 0

    if not args.version:
        # Show current version and usage
        result = subprocess.run(
            [sys.executable, str(BUMP_SCRIPT), "--current"],
            capture_output=True, text=True
        )
        print(result.stdout.strip())
        print("\nUsage: python scripts/release.py <new_version>")
        print("Example: python scripts/release.py 0.9.7")
        print("\nOptions:")
        print("  --dry-run    Preview what would happen")
        print("  --checklist  Show release checklist only")
        print("  --no-open    Don't open files in editor")
        return 1

    version = args.version
    dry_run = args.dry_run

    print()
    print("=" * 60)
    print(f"{'[DRY-RUN] ' if dry_run else ''}RELEASE v{version}")
    print("=" * 60)
    print()

    # Step 1: Bump version
    print("Step 1: Bumping version...")
    bump_cmd = [sys.executable, str(BUMP_SCRIPT), version]
    if dry_run:
        bump_cmd.append("--dry-run")
    if not run_command(bump_cmd, dry_run=False):  # Actually run bump_version
        print("ERROR: Version bump failed")
        return 1
    print()

    # Step 2: Print checklist
    print_checklist(version)

    # Step 3: Open files for editing
    if not args.no_open and not dry_run:
        print("Opening files for editing...")
        open_file_in_editor(REPO_ROOT / "CHANGELOG.md")
        open_file_in_editor(REPO_ROOT / "docs" / "releases.md")
        print()

    if dry_run:
        print("[DRY-RUN] No changes were made.")
    else:
        print("Done! Follow the checklist above to complete the release.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
