#!/usr/bin/env python3
"""
Unified release management CLI.

When to use: At release time. Runs release verification checks and manages the release process.

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
import signal
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


def _semver_tuple(v: str) -> tuple[int, int, int]:
    """Parse version string to comparable tuple."""
    parts = v.split(".")
    if len(parts) != 3:
        return (0, 0, 0)
    return (int(parts[0]), int(parts[1]), int(parts[2]))


# ─── Run (bump + checklist) ─────────────────────────────────────────────────


def _run_command(cmd: list, dry_run: bool = False) -> bool:
    if dry_run:
        print(f"  [DRY-RUN] Would run: {' '.join(str(c) for c in cmd)}")
        return True
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr}")
        return False
    if result.stdout:
        for line in result.stdout.strip().split("\n"):
            print(f"  {line}")
    return True


def _run_with_timeout(
    cmd: list, timeout: int = 600, cwd: Path | None = None, env: dict | None = None
) -> subprocess.CompletedProcess:
    """Run subprocess with timeout and guaranteed cleanup on interrupt."""
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=cwd or REPO_ROOT,
        env=env,
        start_new_session=True,
    )
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
        return subprocess.CompletedProcess(cmd, proc.returncode, stdout, stderr)
    except subprocess.TimeoutExpired:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            proc.wait(timeout=5)
        raise
    except KeyboardInterrupt:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            proc.wait(timeout=5)
        raise


def _check_available_ram(min_gb: float = 2.0) -> bool:
    """Check if enough RAM is available for heavy operations."""
    try:
        result = subprocess.run(["vm_stat"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            lines = result.stdout.splitlines()
            free_pages = 0
            for line in lines:
                if "Pages free" in line or "Pages speculative" in line:
                    parts = line.split(":")
                    if len(parts) == 2:
                        free_pages += int(parts[1].strip().rstrip("."))
            # macOS page size is 16384 on ARM, 4096 on Intel
            page_size_result = subprocess.run(
                ["sysctl", "-n", "hw.pagesize"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            page_size = (
                int(page_size_result.stdout.strip())
                if page_size_result.returncode == 0
                else 16384
            )
            available_gb = (free_pages * page_size) / (1024**3)
            if available_gb < min_gb:
                print(
                    f"  ⚠ Low RAM: {available_gb:.1f}GB available (recommend {min_gb}GB)"
                )
                print(
                    "    Close other apps or use: ./run.sh release preflight --docker"
                )
                return False
            print(f"  ✓ Available RAM: {available_gb:.1f}GB")
            return True
    except Exception:
        pass
    return True  # Can't check, proceed optimistically


def _print_checklist(version: str) -> None:
    print()
    print("=" * 60)
    print("RELEASE CHECKLIST")
    print("=" * 60)
    print()
    print(f"Version: v{version}")
    print()
    print("Automated (done by this script):")
    print("  ✓ Version bumped in pyproject.toml, package.json, CITATION.cff")
    print("  ✓ Doc version references synced")
    print("  ✓ Doc dates updated to today")
    print()
    print("Manual steps (you must do these):")
    print(
        "  [ ] 1. Edit CHANGELOG.md — Add release notes under [Unreleased] → [{version}]"
    )
    print("  [ ] 2. Edit docs/getting-started/releases.md — Add release entry")
    print("  [ ] 3. Review changes: git diff")
    print(f"  [ ] 4. Commit: ./scripts/ai_commit.sh 'chore: release v{version}'")
    print(f"  [ ] 5. Tag and push: git tag v{version} && git push origin v{version}")
    print("  [ ] 6. Monitor GitHub Actions → Publish to PyPI workflow")
    print()
    print("Verification:")
    print(f"  [ ] Check PyPI: pip install structural-lib-is456=={version}")
    print(
        f"  [ ] Clean-venv verify: python scripts/release.py verify --version {version} --source pypi"
    )
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
            capture_output=True,
            text=True,
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

    # Pre-flight checks
    print("Pre-flight checks...")

    # Check git working tree is clean
    result = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True, cwd=REPO_ROOT
    )
    if result.stdout.strip():
        print("  ERROR: Git working tree is not clean. Commit or stash changes first.")
        print(f"  Dirty files:\n{result.stdout}")
        if not dry_run:
            return 1
        print("  (continuing in dry-run mode)")
    else:
        print("  ✓ Git working tree is clean")

    # Check branch
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    branch = result.stdout.strip()
    if (
        branch != "main"
        and not branch.startswith("release/")
        and not branch.startswith("task/")
    ):
        print(
            f"  WARNING: On branch '{branch}', expected 'main' or release/task branch"
        )
    else:
        print(f"  ✓ Branch: {branch}")

    # Check version ordering
    result = subprocess.run(
        [sys.executable, str(BUMP_SCRIPT), "--current"],
        capture_output=True,
        text=True,
    )
    current_version = (
        result.stdout.strip().split(": ")[-1] if result.returncode == 0 else "unknown"
    )

    try:
        if _semver_tuple(version) <= _semver_tuple(current_version):
            print(
                f"  ERROR: New version {version} must be higher than current {current_version}"
            )
            return 1
        print(f"  ✓ Version: {current_version} → {version}")
    except (ValueError, IndexError):
        print(f"  WARNING: Could not compare versions ({current_version} → {version})")

    # Run tests
    print("\n  Running Python tests...")
    try:
        test_result = _run_with_timeout(
            [sys.executable, "-m", "pytest", "Python/tests/", "-v", "--tb=short", "-q"],
            timeout=600,
        )
    except subprocess.TimeoutExpired:
        print("  ERROR: Tests TIMED OUT (>600s)")
        if not dry_run:
            return 1
        print("  (continuing in dry-run mode)")
        test_result = None

    if test_result is None:
        pass
    elif test_result.returncode != 0:
        print("  ERROR: Tests failed! Fix failures before releasing.")
        print(
            test_result.stdout[-500:]
            if len(test_result.stdout) > 500
            else test_result.stdout
        )
        if not dry_run:
            return 1
        print("  (continuing in dry-run mode)")
    else:
        # Extract test count from output
        lines = test_result.stdout.strip().split("\n")
        summary = lines[-1] if lines else "tests passed"
        print(f"  ✓ Tests: {summary}")

    # Check React build
    react_dir = REPO_ROOT / "react_app"
    if react_dir.exists():
        print("  Checking React build...")
        try:
            react_result = _run_with_timeout(
                ["npm", "run", "build"],
                timeout=300,
                cwd=react_dir,
                env={**os.environ, "NODE_OPTIONS": "--max-old-space-size=1536"},
            )
        except subprocess.TimeoutExpired:
            print("  ERROR: React build TIMED OUT (>300s)")
            if not dry_run:
                return 1
            print("  (continuing in dry-run mode)")
            react_result = None

        if react_result is None:
            pass
        elif react_result.returncode != 0:
            print("  ERROR: React build failed!")
            print(
                react_result.stderr[-500:]
                if len(react_result.stderr) > 500
                else react_result.stderr
            )
            if not dry_run:
                return 1
            print("  (continuing in dry-run mode)")
        else:
            print("  ✓ React build succeeds")

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


def _run_check(cmd: list[str], *, cwd: Path | None = None, timeout: int = 600) -> None:
    print(f"+ {' '.join(str(c) for c in cmd)}")
    subprocess.run(cmd, check=True, cwd=cwd, timeout=timeout)


def _find_wheel(wheel_dir: Path, version: str | None) -> Path:
    pattern = (
        f"structural_lib_is456-{version}*.whl"
        if version
        else "structural_lib_is456-*.whl"
    )
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

        _run_check(
            [
                str(python),
                "-c",
                "from structural_lib import api; print(api.get_library_version())",
            ]
        )

        # Run core tests
        print("\nRunning core tests in clean venv...")
        _run_check([str(pip), "install", "pytest"])
        _run_check(
            [
                str(python),
                "-m",
                "pytest",
                str(REPO_ROOT / "Python" / "tests"),
                "-v",
                "--tb=short",
                "-q",
                "-x",  # Stop on first failure
            ]
        )

        if not args.skip_cli:
            if not job_path.exists():
                print(f"error: job file not found: {job_path}")
                return 2
            out_dir = Path(tmp) / "job_out"
            _run_check(
                [
                    str(python),
                    "-m",
                    "structural_lib",
                    "job",
                    str(job_path),
                    "-o",
                    str(out_dir),
                ]
            )
            _run_check(
                [
                    str(python),
                    "-m",
                    "structural_lib",
                    "critical",
                    str(out_dir),
                    "--top",
                    "1",
                    "--format",
                    "csv",
                ]
            )
            _run_check(
                [
                    str(python),
                    "-m",
                    "structural_lib",
                    "report",
                    str(out_dir),
                    "--format",
                    "html",
                    "-o",
                    str(out_dir / "report.html"),
                ]
            )

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

    missing_in_releases = sorted(
        set(changelog_versions) - set(releases_versions), key=_semver_tuple
    )
    missing_in_changelog = sorted(
        set(releases_versions) - set(changelog_versions), key=_semver_tuple
    )

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

    latest_changelog = max(changelog_versions, key=_semver_tuple)
    latest_releases = max(releases_versions, key=_semver_tuple)
    if latest_changelog != latest_releases:
        print(
            f"ERROR: Latest versions do not match: CHANGELOG={latest_changelog}, RELEASES={latest_releases}"
        )
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


# ─── Preflight ───────────────────────────────────────────────────────────────


def cmd_preflight(args: argparse.Namespace) -> int:
    """Run all pre-release validation checks without making changes."""
    print("=" * 60)
    print("PRE-RELEASE VALIDATION")
    print("=" * 60)
    print()

    errors = 0
    warnings = 0

    # 0. RAM check
    print("0. System Resources")
    if not _check_available_ram(min_gb=2.0):
        errors += 1
        print("  ✗ Insufficient RAM for preflight (need 2GB free)")

    # 1. Git state
    print("1. Git State")
    result = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True, cwd=REPO_ROOT
    )
    if result.stdout.strip():
        print("  ✗ Working tree is dirty")
        errors += 1
    else:
        print("  ✓ Working tree is clean")

    result = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    branch = result.stdout.strip()
    print(f"  → Branch: {branch}")

    # 2. Version
    print("\n2. Version")
    result = subprocess.run(
        [sys.executable, str(BUMP_SCRIPT), "--current"],
        capture_output=True,
        text=True,
    )
    current = (
        result.stdout.strip().split(": ")[-1] if result.returncode == 0 else "unknown"
    )
    print(f"  → Current: {current}")

    if args.version:
        if not re.match(r"^\d+\.\d+\.\d+$", args.version):
            print(f"  ✗ Invalid version format: {args.version}")
            errors += 1
        else:
            try:
                if _semver_tuple(args.version) <= _semver_tuple(current):
                    print(f"  ✗ Target {args.version} is not higher than {current}")
                    errors += 1
                else:
                    print(f"  ✓ Target: {args.version} (valid upgrade)")
            except (ValueError, IndexError):
                print("  ⚠ Could not compare versions")
                warnings += 1

    if getattr(args, "docker", False):
        # Run heavy operations in Docker with memory limits
        print("\n3. Python Tests (Docker, 2GB limit)")
        try:
            test_result = _run_with_timeout(
                [
                    "docker",
                    "compose",
                    "-f",
                    "docker-compose.preflight.yml",
                    "run",
                    "--rm",
                    "test-python",
                ],
                timeout=600,
            )
            if test_result.returncode != 0:
                print("  ✗ Tests FAILED (in Docker)")
                errors += 1
            else:
                print("  ✓ Tests passed (in Docker)")
        except subprocess.TimeoutExpired:
            print("  ✗ Tests TIMED OUT (>600s)")
            errors += 1
        except FileNotFoundError:
            print(
                "  ✗ Docker not available — start Colima: colima start --cpu 4 --memory 4"
            )
            errors += 1

        print("\n4. React Build (Docker, 2GB limit)")
        try:
            react_result = _run_with_timeout(
                [
                    "docker",
                    "compose",
                    "-f",
                    "docker-compose.preflight.yml",
                    "run",
                    "--rm",
                    "build-react",
                ],
                timeout=300,
            )
            if react_result.returncode != 0:
                print("  ✗ Build FAILED (in Docker)")
                errors += 1
            else:
                print("  ✓ Build succeeds (in Docker)")
        except subprocess.TimeoutExpired:
            print("  ✗ Build TIMED OUT (>300s)")
            errors += 1
        except FileNotFoundError:
            print(
                "  ✗ Docker not available — start Colima: colima start --cpu 4 --memory 4"
            )
            errors += 1
    else:
        # 3. Tests (local)
        print("\n3. Python Tests")
        try:
            test_result = _run_with_timeout(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "Python/tests/",
                    "-v",
                    "--tb=short",
                    "-q",
                ],
                timeout=600,
            )
        except subprocess.TimeoutExpired:
            print("  ✗ Tests TIMED OUT (>600s)")
            errors += 1
            test_result = None

        if test_result is None:
            pass
        elif test_result.returncode != 0:
            print("  ✗ Tests FAILED")
            # Show last few lines
            lines = test_result.stdout.strip().split("\n")
            for line in lines[-5:]:
                print(f"    {line}")
            errors += 1
        else:
            lines = test_result.stdout.strip().split("\n")
            summary = lines[-1] if lines else "passed"
            print(f"  ✓ {summary}")

        # 4. React build (local)
        print("\n4. React Build")
        react_dir = REPO_ROOT / "react_app"
        if react_dir.exists():
            try:
                react_result = _run_with_timeout(
                    ["npm", "run", "build"],
                    timeout=300,
                    cwd=react_dir,
                    env={**os.environ, "NODE_OPTIONS": "--max-old-space-size=1536"},
                )
            except subprocess.TimeoutExpired:
                print("  ✗ React build TIMED OUT (>300s)")
                errors += 1
                react_result = None

            if react_result is None:
                pass
            elif react_result.returncode != 0:
                print("  ✗ Build FAILED")
                errors += 1
            else:
                print("  ✓ Build succeeds")
        else:
            print("  ⚠ react_app/ not found")
            warnings += 1

    # 5. Doc version sync
    print("\n5. Doc Version Sync")
    sync_result = subprocess.run(
        [sys.executable, str(BUMP_SCRIPT), "--check-docs"],
        capture_output=True,
        text=True,
    )
    if sync_result.returncode != 0:
        print("  ✗ Doc versions are stale")
        warnings += 1
    else:
        print("  ✓ Doc versions are synced")

    # 6. CHANGELOG check
    print("\n6. Release Docs")
    docs_result = cmd_check_docs(argparse.Namespace())
    if docs_result != 0:
        print("  ⚠ CHANGELOG ↔ releases.md mismatch (expected before new release)")
        warnings += 1
    else:
        print("  ✓ CHANGELOG ↔ releases.md in sync")

    # 7. Version files exist
    print("\n7. Version Files")
    version_files_check = subprocess.run(
        [sys.executable, str(BUMP_SCRIPT), "--report"],
        capture_output=True,
        text=True,
    )
    if version_files_check.returncode == 0:
        # Parse core version pins from report output
        in_core = False
        for line in version_files_check.stdout.strip().split("\n"):
            if "Core version pins:" in line:
                in_core = True
                continue
            if in_core and line.strip().startswith("- "):
                rel_path = line.strip().lstrip("- ").strip()
                filepath = REPO_ROOT / rel_path
                if filepath.exists():
                    print(f"  ✓ {rel_path}")
                else:
                    print(f"  ✗ {rel_path} — NOT FOUND")
                    errors += 1
            elif in_core and not line.strip().startswith("- "):
                in_core = False
    else:
        print("  ⚠ Could not check version files")
        warnings += 1

    # Summary
    print()
    print("=" * 60)
    if errors == 0:
        print(f"✓ READY TO RELEASE ({warnings} warnings)")
    else:
        print(f"✗ NOT READY — {errors} error(s), {warnings} warning(s)")
    print("=" * 60)

    return 1 if errors > 0 else 0


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
    p_run.add_argument(
        "--no-open", action="store_true", help="Don't open files in editor"
    )

    # verify
    p_verify = sub.add_parser("verify", help="Verify release in clean venv")
    p_verify.add_argument("--version", help="Version to verify (e.g., 0.11.0)")
    p_verify.add_argument(
        "--source", choices=["wheel", "pypi"], default="wheel", help="Install source"
    )
    p_verify.add_argument("--wheel-dir", default="Python/dist", help="Wheel directory")
    p_verify.add_argument(
        "--job",
        default="Python/examples/sample_job_is456.json",
        help="Job spec for smoke test",
    )
    p_verify.add_argument(
        "--skip-cli", action="store_true", help="Skip CLI smoke checks"
    )

    # check-docs
    sub.add_parser("check-docs", help="Validate CHANGELOG ↔ releases.md versions")

    # checklist
    sub.add_parser("checklist", help="Validate pre-release checklist structure")

    # preflight
    p_preflight = sub.add_parser("preflight", help="Run pre-release validation checks")
    p_preflight.add_argument("version", nargs="?", help="Target version to validate")
    p_preflight.add_argument(
        "--docker",
        action="store_true",
        help="Run heavy checks (pytest, npm build) inside Docker containers with memory limits",
    )

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
        "preflight": cmd_preflight,
    }

    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
