#!/usr/bin/env python3
"""
Unified release management CLI.

Consolidates: release.py, verify_release.py, check_release_docs.py, check_pre_release_checklist.py

USAGE:
    python scripts/release.py run 0.9.7 [--dry-run] [--no-open]
    python scripts/release.py verify [--version 0.9.7] [--source wheel]
    python scripts/release.py check-docs
    python scripts/release.py checklist
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.utils import REPO_ROOT
BUMP_SCRIPT = REPO_ROOT / "scripts" / "bump_version.py"
CHANGELOG = REPO_ROOT / "CHANGELOG.md"
RELEASES = REPO_ROOT / "docs" / "getting-started" / "releases.md"
CHECKLIST_PATH = REPO_ROOT / "docs" / "planning" / "pre-release-checklist.md"
VERSION_RE = re.compile(r"^##\s*\[?v?(\d+\.\d+\.\d+)\b")


# ─── Run (bump + checklist) ─────────────────────────────────────────────────


def _run_command(cmd: list, dry_run: bool = False) -> bool:
    if dry_run:
        print(f"  [DRY-RUN] Would run: {' '.join(str(c) for c in cmd)}")
        return True
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr}")
        return False
    if result.stdout:
        for line in result.stdout.strip().split("\n"):
            print(f"  {line}")
    return True


def _print_checklist(version: str) -> None:
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
    print(f"  [ ] 4. Commit: git add -A && git commit -m 'chore: release v{version}'")
    print("  [ ] 5. Create PR and merge to main")
    print(f"  [ ] 6. Tag: git tag v{version} && git push origin v{version}")
    print("  [ ] 7. GitHub Release will trigger PyPI publish")
    print()
    print("Verification:")
    print(f"  [ ] Check PyPI: pip install structural-lib-is456=={version}")
    print(f"  [ ] Clean-venv verify: python scripts/release.py verify --version {version} --source pypi")
    print("  [ ] Check GitHub Release page")
    print()


def _open_file_in_editor(filepath: Path) -> None:
    try:
        subprocess.run(["open", str(filepath)], check=True)
        print(f"  Opened: {filepath}")
    except Exception as e:
        print(f"  (Could not open {filepath}: {e})")


def cmd_run(args: argparse.Namespace) -> int:
    if not args.version:
        result = subprocess.run(
            [sys.executable, str(BUMP_SCRIPT), "--current"],
            capture_output=True, text=True,
        )
        print(result.stdout.strip())
        print("\nUsage: python scripts/release.py run <new_version>")
        print("Example: python scripts/release.py run 0.9.7")
        return 1

    version = args.version
    dry_run = args.dry_run

    print()
    print("=" * 60)
    print(f"{'[DRY-RUN] ' if dry_run else ''}RELEASE v{version}")
    print("=" * 60)
    print()

    print("Step 1: Bumping version...")
    bump_cmd = [sys.executable, str(BUMP_SCRIPT), version]
    if dry_run:
        bump_cmd.append("--dry-run")
    if not _run_command(bump_cmd):
        print("ERROR: Version bump failed")
        return 1
    print()

    _print_checklist(version)

    if not args.no_open and not dry_run:
        print("Opening files for editing...")
        _open_file_in_editor(REPO_ROOT / "CHANGELOG.md")
        _open_file_in_editor(REPO_ROOT / "docs" / "releases.md")
        print()

    if dry_run:
        print("[DRY-RUN] No changes were made.")
    else:
        print("Done! Follow the checklist above to complete the release.")

    return 0


# ─── Verify ──────────────────────────────────────────────────────────────────


def _bin_path(venv_dir: Path, name: str) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / f"{name}.exe"
    return venv_dir / "bin" / name


def _run_check(cmd: list[str], *, cwd: Path | None = None) -> None:
    print(f"+ {' '.join(str(c) for c in cmd)}")
    subprocess.run(cmd, check=True, cwd=cwd)


def _find_wheel(wheel_dir: Path, version: str | None) -> Path:
    pattern = f"structural_lib_is456-{version}*.whl" if version else "structural_lib_is456-*.whl"
    wheels = sorted(wheel_dir.glob(pattern))
    if not wheels:
        raise FileNotFoundError(f"No wheel found in {wheel_dir} (pattern: {pattern})")
    return wheels[-1]


def cmd_verify(args: argparse.Namespace) -> int:
    wheel_dir = REPO_ROOT / args.wheel_dir
    job_path = REPO_ROOT / args.job

    with tempfile.TemporaryDirectory(prefix="verify_release_") as tmp:
        venv_dir = Path(tmp) / "venv"
        _run_check([sys.executable, "-m", "venv", str(venv_dir)])

        pip = _bin_path(venv_dir, "pip")
        python = _bin_path(venv_dir, "python")

        _run_check([str(pip), "install", "--upgrade", "pip"])

        if args.source == "wheel":
            wheel = _find_wheel(wheel_dir, args.version)
            _run_check([str(pip), "install", str(wheel)])
        else:
            if not args.version:
                print("error: --version is required when using --source pypi")
                return 2
            _run_check([str(pip), "install", f"structural-lib-is456=={args.version}"])

        _run_check([str(python), "-c", "from structural_lib import api; print(api.get_library_version())"])

        if not args.skip_cli:
            if not job_path.exists():
                print(f"error: job file not found: {job_path}")
                return 2
            out_dir = Path(tmp) / "job_out"
            _run_check([str(python), "-m", "structural_lib", "job", str(job_path), "-o", str(out_dir)])
            _run_check([str(python), "-m", "structural_lib", "critical", str(out_dir), "--top", "1", "--format", "csv"])
            _run_check([str(python), "-m", "structural_lib", "report", str(out_dir), "--format", "html", "-o", str(out_dir / "report.html")])

        print("Release verification OK.")
    return 0


# ─── Check Docs ──────────────────────────────────────────────────────────────


def _parse_versions(path: Path) -> list[str]:
    versions: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = VERSION_RE.match(line.strip())
        if match:
            versions.append(match.group(1))
    return versions


def _semver_key(version: str) -> tuple[int, int, int]:
    parts = version.split(".")
    if len(parts) != 3:
        return (0, 0, 0)
    return tuple(int(p) for p in parts)  # type: ignore[return-value]


def cmd_check_docs(args: argparse.Namespace) -> int:
    if not CHANGELOG.exists():
        print("ERROR: CHANGELOG.md not found")
        return 1
    if not RELEASES.exists():
        print("ERROR: docs/getting-started/releases.md not found")
        return 1

    changelog_versions = _parse_versions(CHANGELOG)
    releases_versions = _parse_versions(RELEASES)

    if not changelog_versions:
        print("ERROR: No versions found in CHANGELOG.md")
        return 1
    if not releases_versions:
        print("ERROR: No versions found in docs/getting-started/releases.md")
        return 1

    missing_in_releases = sorted(set(changelog_versions) - set(releases_versions), key=_semver_key)
    missing_in_changelog = sorted(set(releases_versions) - set(changelog_versions), key=_semver_key)

    if missing_in_releases:
        print("ERROR: Versions in CHANGELOG missing from RELEASES:")
        for v in missing_in_releases:
            print(f"  - {v}")
        return 1

    if missing_in_changelog:
        print("ERROR: Versions in RELEASES missing from CHANGELOG:")
        for v in missing_in_changelog:
            print(f"  - {v}")
        return 1

    latest_changelog = max(changelog_versions, key=_semver_key)
    latest_releases = max(releases_versions, key=_semver_key)
    if latest_changelog != latest_releases:
        print(f"ERROR: Latest versions do not match: CHANGELOG={latest_changelog}, RELEASES={latest_releases}")
        return 1

    return 0


# ─── Checklist ───────────────────────────────────────────────────────────────


REQUIRED_HEADINGS = [
    "# Pre-Release Checklist",
    "## Current State",
    "## Beta Readiness Checklist",
    "### Required Before Beta",
    "### Required Before 1.0",
]


def _find_heading_prefix(lines: list[str], heading: str) -> int:
    for idx, line in enumerate(lines):
        if line.strip().startswith(heading):
            return idx
    return -1


def _checklist_section(lines: list[str], start_idx: int) -> list[str]:
    end_idx = len(lines)
    for idx in range(start_idx + 1, len(lines)):
        if lines[idx].startswith("## ") or lines[idx].startswith("### "):
            end_idx = idx
            break
    return lines[start_idx + 1 : end_idx]


def _has_checkboxes(section_lines: list[str]) -> bool:
    return any(line.strip().startswith("- [") for line in section_lines)


def cmd_checklist(args: argparse.Namespace) -> int:
    if not CHECKLIST_PATH.exists():
        print("ERROR: docs/planning/pre-release-checklist.md not found")
        return 1

    lines = CHECKLIST_PATH.read_text(encoding="utf-8").splitlines()

    for heading in REQUIRED_HEADINGS:
        if _find_heading_prefix(lines, heading) == -1:
            print(f"ERROR: Missing heading: {heading}")
            return 1

    required_beta_idx = _find_heading_prefix(lines, "### Required Before Beta")
    required_1_idx = _find_heading_prefix(lines, "### Required Before 1.0")

    if required_beta_idx != -1:
        beta_lines = _checklist_section(lines, required_beta_idx)
        if not _has_checkboxes(beta_lines):
            print("ERROR: 'Required Before Beta' must include checklist items")
            return 1

    if required_1_idx != -1:
        one_lines = _checklist_section(lines, required_1_idx)
        if not _has_checkboxes(one_lines):
            print("ERROR: 'Required Before 1.0' must include checklist items")
            return 1

    return 0


# ─── CLI ─────────────────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="release.py",
        description="Unified release management (run, verify, check-docs, checklist)",
    )
    sub = parser.add_subparsers(dest="command", help="Release command")

    # run
    p_run = sub.add_parser("run", help="Bump version + release flow")
    p_run.add_argument("version", nargs="?", help="New version (e.g., 0.9.7)")
    p_run.add_argument("--dry-run", action="store_true", help="Preview without changes")
    p_run.add_argument("--no-open", action="store_true", help="Don't open files in editor")

    # verify
    p_verify = sub.add_parser("verify", help="Verify release in clean venv")
    p_verify.add_argument("--version", help="Version to verify (e.g., 0.11.0)")
    p_verify.add_argument("--source", choices=["wheel", "pypi"], default="wheel", help="Install source")
    p_verify.add_argument("--wheel-dir", default="Python/dist", help="Wheel directory")
    p_verify.add_argument("--job", default="Python/examples/sample_job_is456.json", help="Job spec for smoke test")
    p_verify.add_argument("--skip-cli", action="store_true", help="Skip CLI smoke checks")

    # check-docs
    sub.add_parser("check-docs", help="Validate CHANGELOG ↔ releases.md versions")

    # checklist
    sub.add_parser("checklist", help="Validate pre-release checklist structure")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    handlers = {
        "run": cmd_run,
        "verify": cmd_verify,
        "check-docs": cmd_check_docs,
        "checklist": cmd_checklist,
    }

    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
