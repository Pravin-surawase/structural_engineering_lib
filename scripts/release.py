#!/usr/bin/env python3
"""
Unified release management CLI.

When to use: At release time. Runs release verification checks and manages the release process.

Consolidates: release.py, verify_release.py, check_release_docs.py, check_pre_release_checklist.py

USAGE:
    python scripts/release.py run 0.24.0a1 [--dry-run] [--no-open]
    python scripts/release.py verify [--version 0.24.0a1] [--source wheel]
    python scripts/release.py check-docs
    python scripts/release.py checklist
    python scripts/release.py permission-check
    python scripts/release.py footing-inclusion-check
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import tempfile
import tomllib
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.utils import REPO_ROOT
from node_runtime import (
    node_bin_candidates as _shared_node_bin_candidates,
    node_runtime_env as _shared_node_runtime_env,
    required_node_major as _shared_required_node_major,
)

BUMP_SCRIPT = REPO_ROOT / "scripts" / "bump_version.py"
CHANGELOG = REPO_ROOT / "CHANGELOG.md"
RELEASES = REPO_ROOT / "docs" / "getting-started" / "releases.md"
CHECKLIST_PATH = REPO_ROOT / "docs" / "planning" / "pre-release-checklist.md"
PUBLIC_DISTRIBUTION_PERMISSION = (
    REPO_ROOT / "docs" / "verification" / "is456-public-distribution-permission.json"
)
FOOTING_RELEASE_INCLUSION = (
    REPO_ROOT / "docs" / "verification" / "footing-release-inclusion.json"
)
PYPROJECT = REPO_ROOT / "Python" / "pyproject.toml"
FASTAPI_INIT = REPO_ROOT / "fastapi_app" / "__init__.py"
REACT_PACKAGE = REPO_ROOT / "react_app" / "package.json"
CITATION = REPO_ROOT / "CITATION.cff"
ALPHA_VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)a(\d+)$")
LEGACY_STABLE_VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
VERSION_RE = re.compile(r"^##\s*\[?v?(\d+\.\d+\.\d+(?:a\d+)?)\b")
_EXCLUDED_WHEEL_PREFIXES = (
    "structural_lib/_migration_fixtures/",
    "structural_lib/codes/aci318/",
    "structural_lib/codes/ec2/",
    "structural_lib/research/",
)

_REQUIRED_NORMALIZED_CONTENT = {
    "formulas",
    "normalized tables",
    "limits",
    "figure-derived values",
    "lookup",
    "interpolation",
}


def _public_distribution_permission_errors(path: Path | None = None) -> list[str]:
    """Return fail-closed errors for the standing IS 456 distribution decision."""
    path = path or PUBLIC_DISTRIBUTION_PERMISSION
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return [f"public-distribution permission record unavailable: {exc}"]
    except json.JSONDecodeError as exc:
        return [f"public-distribution permission record is invalid JSON: {exc}"]

    expected_values = {
        "schema_version": 1,
        "record_id": "IS456-PUBLIC-DISTRIBUTION-001",
        "decision": "AUTHORIZED",
        "authority": "repository_owner",
    }
    errors = [
        f"permission record {key}={data.get(key)!r}, expected {expected!r}"
        for key, expected in expected_values.items()
        if data.get(key) != expected
    ]

    effective_date = data.get("effective_date")
    if not isinstance(effective_date, str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}", effective_date
    ):
        errors.append("permission record effective_date must be ISO YYYY-MM-DD")

    scope = data.get("scope")
    if not isinstance(scope, dict):
        errors.append("permission record scope must be an object")
    else:
        if scope.get("public_distribution_of_normalized_code_data") is not True:
            errors.append("normalized IS 456 public distribution is not authorized")
        if scope.get("approved_feature_scope_only") is not True:
            errors.append("permission must remain limited to approved feature scopes")
        includes = scope.get("includes")
        if not isinstance(includes, list) or not _REQUIRED_NORMALIZED_CONTENT.issubset(
            set(includes)
        ):
            errors.append("permission scope omits required normalized content types")

    restrictions = data.get("restrictions")
    required_restrictions = {
        "protected_clause_prose_in_repository": False,
        "page_images_in_repository": False,
        "unrelated_standard_content_in_repository": False,
        "preserve_runtime_provenance": True,
    }
    if not isinstance(restrictions, dict):
        errors.append("permission record restrictions must be an object")
    else:
        errors.extend(
            f"permission restriction {key}={restrictions.get(key)!r}, expected {expected!r}"
            for key, expected in required_restrictions.items()
            if restrictions.get(key) is not expected
        )

    boundaries = data.get("release_boundaries")
    required_boundaries = {
        "authorizes_tag_or_publish": False,
        "per_release_owner_authorization_required": True,
        "qualified_structural_engineering_review_required_for_stable_or_engineering_use": True,
    }
    if not isinstance(boundaries, dict):
        errors.append("permission record release_boundaries must be an object")
    else:
        errors.extend(
            f"release boundary {key}={boundaries.get(key)!r}, expected {expected!r}"
            for key, expected in required_boundaries.items()
            if boundaries.get(key) is not expected
        )

    return errors


def cmd_permission_check(args: argparse.Namespace) -> int:
    """Verify the standing owner-confirmed public-distribution permission."""
    errors = _public_distribution_permission_errors()
    if errors:
        _print_version_errors(errors)
        return 1
    print(
        "  ✓ Owner-confirmed IS 456 normalized-data public-distribution "
        "permission is recorded"
    )
    print("  ✓ Protected source content remains excluded")
    print("  ✓ Per-release tag/publication authorization remains required")
    return 0


def _footing_release_inclusion_errors(
    path: Path | None = None, *, repo_root: Path | None = None
) -> list[str]:
    """Return errors until the complete reviewed footing D1 slice is present."""
    path = path or FOOTING_RELEASE_INCLUSION
    repo_root = repo_root or REPO_ROOT
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return [f"footing release-inclusion record unavailable: {exc}"]
    except json.JSONDecodeError as exc:
        return [f"footing release-inclusion record is invalid JSON: {exc}"]

    expected_values = {
        "schema_version": 1,
        "record_id": "FOOT-ISO-RC-V1-RELEASE-INCLUSION",
        "source_head": "886871aef93d9a955a3cc2fa613fe49bad589ce7",
    }
    errors = [
        f"footing inclusion {key}={data.get(key)!r}, expected {expected!r}"
        for key, expected in expected_values.items()
        if data.get(key) != expected
    ]

    required_files = data.get("required_owned_file_sha256")
    if not isinstance(required_files, dict) or not required_files:
        errors.append("footing inclusion record has no owned-file hashes")
    else:
        for relative_path, expected_sha256 in required_files.items():
            candidate = repo_root / relative_path
            if not candidate.is_file():
                errors.append(f"required footing file is missing: {relative_path}")
                continue
            actual_sha256 = hashlib.sha256(candidate.read_bytes()).hexdigest()
            if actual_sha256 != expected_sha256:
                errors.append(
                    f"required footing file changed: {relative_path}; review and "
                    "refresh the inclusion receipt"
                )

    shared_markers = data.get("required_shared_markers")
    if not isinstance(shared_markers, dict) or not shared_markers:
        errors.append("footing inclusion record has no shared-surface markers")
    else:
        for relative_path, markers in shared_markers.items():
            candidate = repo_root / relative_path
            if not candidate.is_file():
                errors.append(
                    f"required footing integration file is missing: {relative_path}"
                )
                continue
            content = candidate.read_text(encoding="utf-8")
            if not isinstance(markers, list) or not markers:
                errors.append(
                    f"footing integration markers are invalid: {relative_path}"
                )
                continue
            for marker in markers:
                if marker not in content:
                    errors.append(
                        f"footing integration marker missing from {relative_path}: "
                        f"{marker}"
                    )

    return errors


def cmd_footing_inclusion_check(args: argparse.Namespace) -> int:
    """Verify that the complete reviewed footing D1 slice is integrated."""
    errors = _footing_release_inclusion_errors()
    if errors:
        _print_version_errors(errors)
        return 1
    print("  ✓ FOOT-ISO-RC-V1 owned files match reviewed source head 886871ae")
    print("  ✓ Footing Python, FastAPI, and React integration markers are present")
    return 0


def _release_version_key(v: str) -> tuple[int, int, int, int, int]:
    """Order supported Alpha identifiers and the legacy stable release."""
    alpha_match = ALPHA_VERSION_RE.fullmatch(v)
    if alpha_match:
        major, minor, patch, alpha = (int(part) for part in alpha_match.groups())
        return (major, minor, patch, 0, alpha)

    stable_match = LEGACY_STABLE_VERSION_RE.fullmatch(v)
    if stable_match:
        major, minor, patch = (int(part) for part in stable_match.groups())
        return (major, minor, patch, 1, 0)

    raise ValueError(f"Unsupported version format: {v}")


# ─── Candidate version evidence ────────────────────────────────────────────


def _version_from_pyproject(path: Path | None = None) -> str:
    """Read the authoritative source-candidate version from Python metadata."""
    path = path or PYPROJECT
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    return str(data["project"]["version"])


def _version_from_assignment(path: Path, variable: str = "__version__") -> str:
    match = re.search(
        rf'^{re.escape(variable)}\s*=\s*["\']([^"\']+)["\']',
        path.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    if not match:
        raise ValueError(f"{variable} is missing from {path.relative_to(REPO_ROOT)}")
    return match.group(1)


def _version_from_cff(path: Path | None = None) -> str:
    path = path or CITATION
    match = re.search(
        r"^version:\s*([^\s#]+)", path.read_text(encoding="utf-8"), re.MULTILINE
    )
    if not match:
        raise ValueError("version is missing from CITATION.cff")
    return match.group(1)


def _latest_documented_version(path: Path) -> str:
    versions = _parse_versions(path)
    if not versions:
        raise ValueError(f"no release version found in {path.relative_to(REPO_ROOT)}")
    return max(versions, key=_release_version_key)


def _release_authorization_recorded(expected: str) -> bool:
    """Return whether the owner-authorized publication sequence is recorded."""
    try:
        checklist_text = CHECKLIST_PATH.read_text(encoding="utf-8")
    except OSError:
        return False
    normalized = " ".join(checklist_text.lower().split())
    marker = (
        f"[x] owner authorizes the v{expected} tag, production pypi publication, "
        "and github release"
    )
    return marker in normalized


def _source_surface_version_errors(
    expected: str, *, allow_authorized_release: bool = False
) -> list[str]:
    """Return exact source/doc version contradictions for a release candidate."""
    try:
        surfaces = {
            "Python/pyproject.toml": _version_from_pyproject(),
            "fastapi_app/__init__.py": _version_from_assignment(FASTAPI_INIT),
            "react_app/package.json": str(
                json.loads(REACT_PACKAGE.read_text(encoding="utf-8"))["version"]
            ),
            "CITATION.cff": _version_from_cff(),
            "CHANGELOG.md": _latest_documented_version(CHANGELOG),
            "docs/getting-started/releases.md": _latest_documented_version(RELEASES),
        }
    except (KeyError, OSError, ValueError, tomllib.TOMLDecodeError) as exc:
        return [f"could not read release surface: {exc}"]

    errors = [
        f"{path}={actual}, expected {expected}"
        for path, actual in surfaces.items()
        if actual != expected
    ]

    citation_text = CITATION.read_text(encoding="utf-8")
    changelog_text = CHANGELOG.read_text(encoding="utf-8")
    release_text = RELEASES.read_text(encoding="utf-8")
    has_release_date = bool(re.search(r"^date-released:", citation_text, re.MULTILINE))
    authorization_recorded = _release_authorization_recorded(expected)

    if allow_authorized_release and authorization_recorded:
        if not has_release_date:
            errors.append(
                "CITATION.cff must declare date-released for an authorized release"
            )
        dated_header = re.search(
            rf"^##\s*\[{re.escape(expected)}\]\s*[—-]\s*\d{{4}}-\d{{2}}-\d{{2}}\s*$",
            changelog_text,
            re.MULTILINE,
        )
        if not dated_header:
            errors.append(
                f"CHANGELOG.md must give authorized v{expected} an ISO release date"
            )
        authorized_release_markers = (
            "release authorized",
            "published to pypi and github releases",
        )
        if not any(
            marker in release_text.lower() for marker in authorized_release_markers
        ):
            errors.append("release ledger must record the authorized release state")
    else:
        if has_release_date:
            errors.append(
                "CITATION.cff declares date-released for an unpublished candidate"
            )
        changelog_lower = changelog_text.lower()
        release_lower = release_text.lower()
        if "prepared candidate (unreleased; on hold)" not in changelog_lower:
            errors.append(
                f"CHANGELOG.md must label v{expected} as prepared/unreleased/on hold"
            )
        if "not tagged or published" not in release_lower:
            errors.append(
                f"release ledger must state v{expected} is not tagged or published"
            )
        if "not tagged or published" not in citation_text.lower():
            errors.append(f"CITATION.cff must not imply v{expected} is published")

    return errors


def _wheel_metadata_version(wheel: Path) -> str:
    """Read Version from the one METADATA record inside a wheel."""
    with zipfile.ZipFile(wheel) as archive:
        metadata_paths = [
            name for name in archive.namelist() if name.endswith(".dist-info/METADATA")
        ]
        if len(metadata_paths) != 1:
            raise ValueError(
                f"expected one wheel METADATA record, found {len(metadata_paths)}"
            )
        metadata = archive.read(metadata_paths[0]).decode("utf-8")
    match = re.search(r"^Version:\s*(.+)$", metadata, re.MULTILINE)
    if not match:
        raise ValueError("wheel METADATA has no Version field")
    return match.group(1).strip()


def _wheel_filename_version(wheel: Path) -> str:
    match = re.match(
        r"^structural_lib_is456-([0-9]+\.[0-9]+\.[0-9]+(?:a[0-9]+)?)-.+\.whl$",
        wheel.name,
    )
    if not match:
        raise ValueError(f"unexpected wheel filename: {wheel.name}")
    return match.group(1)


def _wheel_version_errors(wheel: Path, expected: str) -> list[str]:
    """Return version or excluded-content defects for one candidate wheel."""
    try:
        filename_version = _wheel_filename_version(wheel)
        metadata_version = _wheel_metadata_version(wheel)
        with zipfile.ZipFile(wheel) as archive:
            excluded_members = sorted(
                name
                for name in archive.namelist()
                if name.startswith(_EXCLUDED_WHEEL_PREFIXES)
            )
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        return [f"could not inspect wheel {wheel}: {exc}"]

    errors = []
    if filename_version != expected:
        errors.append(f"wheel filename={filename_version}, expected {expected}")
    if metadata_version != expected:
        errors.append(f"wheel METADATA={metadata_version}, expected {expected}")
    if excluded_members:
        errors.append(
            "wheel contains excluded package content: " + ", ".join(excluded_members)
        )
    return errors


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _clean_wheel_import_version(wheel: Path) -> str:
    """Install one wheel in a disposable venv and return imported package version."""
    with tempfile.TemporaryDirectory(prefix="release_candidate_") as tmp:
        temp_root = Path(tmp)
        venv_dir = temp_root / "venv"
        _run_check([sys.executable, "-m", "venv", str(venv_dir)])
        pip = _bin_path(venv_dir, "pip")
        python = _bin_path(venv_dir, "python")
        clean_env = {
            key: value for key, value in os.environ.items() if key != "PYTHONPATH"
        }
        _run_check(
            [str(pip), "install", "--disable-pip-version-check", str(wheel)],
            env=clean_env,
        )
        result = subprocess.run(
            [
                str(python),
                "-c",
                "import structural_lib; print(structural_lib.__version__)",
            ],
            check=True,
            capture_output=True,
            text=True,
            cwd=temp_root,
            env=clean_env,
            timeout=120,
        )
        subprocess.run(
            [str(python), "-m", "structural_lib", "--help"],
            check=True,
            capture_output=True,
            text=True,
            cwd=temp_root,
            env=clean_env,
            timeout=120,
        )
        return result.stdout.strip()


def _print_version_errors(errors: list[str]) -> None:
    for error in errors:
        print(f"  ✗ {error}")


def cmd_candidate_check(args: argparse.Namespace) -> int:
    """Verify exact source, artifact, and clean-install version evidence."""
    expected = args.version or _version_from_pyproject()
    wheel = Path(args.wheel).expanduser().resolve()
    print(f"Candidate version evidence: {expected}")

    errors = _public_distribution_permission_errors()
    errors.extend(_footing_release_inclusion_errors())
    errors.extend(
        _source_surface_version_errors(expected, allow_authorized_release=True)
    )
    errors.extend(_wheel_version_errors(wheel, expected))
    if errors:
        _print_version_errors(errors)
        return 1

    try:
        imported_version = _clean_wheel_import_version(wheel)
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        print(f"  ✗ clean wheel import failed: {exc}")
        return 1
    if imported_version != expected:
        print(
            f"  ✗ clean imported structural_lib={imported_version}, expected {expected}"
        )
        return 1

    print(f"  ✓ wheel: {wheel.name}")
    print(f"  ✓ sha256: {_sha256(wheel)}")
    print(f"  ✓ clean imported structural_lib={imported_version}")
    print("  ✓ clean structural_lib CLI --help")
    return 0


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


def _print_failure_tail(
    result: subprocess.CompletedProcess, *, max_chars: int = 4000
) -> None:
    """Print useful subprocess diagnostics without flooding preflight output."""
    parts = [part.strip() for part in (result.stdout, result.stderr) if part.strip()]
    if not parts:
        return
    print("  ↳ Last command output:")
    for line in "\n".join(parts)[-max_chars:].splitlines():
        print(f"    {line}")


def _available_ram_gb() -> float | None:
    """Return reclaimable memory, not only immediately free pages."""
    try:
        pressure = subprocess.run(
            ["memory_pressure", "-Q"], capture_output=True, text=True, timeout=5
        )
        total = subprocess.run(
            ["sysctl", "-n", "hw.memsize"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        match = re.search(
            r"System-wide memory free percentage:\s*(\d+)%", pressure.stdout
        )
        if pressure.returncode == 0 and total.returncode == 0 and match:
            return int(total.stdout.strip()) * int(match.group(1)) / 100 / (1024**3)

        # Fallback for macOS versions without ``memory_pressure -Q``. Inactive
        # and purgeable pages are reclaimable and must not be treated as used.
        result = subprocess.run(["vm_stat"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            available_pages = 0
            reclaimable = (
                "Pages free",
                "Pages inactive",
                "Pages speculative",
                "Pages purgeable",
            )
            for line in result.stdout.splitlines():
                if any(label in line for label in reclaimable):
                    parts = line.split(":")
                    if len(parts) == 2:
                        available_pages += int(parts[1].strip().rstrip("."))
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
            return (available_pages * page_size) / (1024**3)
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError, OSError):
        return None

    return None


def _check_available_ram(min_gb: float = 2.0) -> bool:
    """Check if enough reclaimable RAM is available for heavy operations."""
    available_gb = _available_ram_gb()
    if available_gb is None:
        print("  ⚠ Could not determine available RAM — continuing")
        return True
    if available_gb < min_gb:
        print(f"  ⚠ Low RAM: {available_gb:.1f}GB available (recommend {min_gb}GB)")
        print("    Close other apps or use: ./run.sh release preflight --docker")
        return False
    print(f"  ✓ RAM available: {available_gb:.1f}GB")
    return True


def _required_node_major() -> str | None:
    """Compatibility wrapper around the shared Node runtime selector."""
    return _shared_required_node_major(REPO_ROOT)


def _node_bin_candidates(required_major: str) -> list[Path]:
    """Compatibility wrapper around the shared Node runtime selector."""
    return _shared_node_bin_candidates(required_major)


def _node_runtime_env(
    candidate_bins: list[Path] | None = None,
) -> tuple[dict[str, str] | None, str]:
    """Select the shared healthy Node runtime for release checks."""
    required_major = _required_node_major()
    return _shared_node_runtime_env(
        repo_root=REPO_ROOT,
        required_major=required_major,
        candidate_bins=(
            _node_bin_candidates(required_major)
            if required_major and candidate_bins is None
            else candidate_bins
        ),
    )


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
        f"  [ ] 1. Edit CHANGELOG.md — Add release notes under [Unreleased] → [{version}]"
    )
    print("  [ ] 2. Edit docs/getting-started/releases.md — Add release entry")
    print("  [ ] 3. Review changes: git diff")
    print(f"  [ ] 4. Codex commit and PR update: 'chore: release v{version}'")
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
        print("Example: python scripts/release.py run 0.24.0a1")
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

    permission_errors = _public_distribution_permission_errors()
    if permission_errors:
        _print_version_errors(permission_errors)
        return 1
    print("  ✓ Public-distribution permission record")

    footing_errors = _footing_release_inclusion_errors()
    if footing_errors:
        _print_version_errors(footing_errors)
        return 1
    print("  ✓ Complete footing D1 release inclusion")

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
        and not branch.startswith("codex/")
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
        if not ALPHA_VERSION_RE.fullmatch(version):
            print(f"  ERROR: Version {version} must use PEP 440 Alpha format X.Y.ZaN")
            return 1
        if _release_version_key(version) <= _release_version_key(current_version):
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
            [
                sys.executable,
                "-m",
                "pytest",
                "Python/tests/",
                "-v",
                "--tb=short",
                "-q",
                "-m",
                "not slow",
            ],
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
        node_env, node_version = _node_runtime_env()
        if node_env is None:
            print(f"  ERROR: {node_version}")
            return 1
        node_env["NODE_OPTIONS"] = "--max-old-space-size=1536"
        print(f"  → Selected {node_version}")
        try:
            react_result = _run_with_timeout(
                ["npm", "run", "build"],
                timeout=300,
                cwd=react_dir,
                env=node_env,
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
        _open_file_in_editor(RELEASES)
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


def _run_check(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    timeout: int = 600,
    env: dict[str, str] | None = None,
) -> None:
    print(f"+ {' '.join(str(c) for c in cmd)}")
    subprocess.run(cmd, check=True, cwd=cwd, timeout=timeout, env=env)


def _find_wheel(wheel_dir: Path, version: str | None) -> Path:
    pattern = (
        f"structural_lib_is456-{version}-*.whl"
        if version
        else "structural_lib_is456-*.whl"
    )
    wheels = sorted(wheel_dir.glob(pattern))
    if not wheels:
        raise FileNotFoundError(f"No wheel found in {wheel_dir} (pattern: {pattern})")
    if len(wheels) > 1:
        candidates = ", ".join(wheel.name for wheel in wheels)
        if version:
            raise RuntimeError(
                f"Multiple wheels match version {version}; remove stale artifacts or "
                f"select a clean wheel directory: {candidates}"
            )
        raise RuntimeError(
            "Multiple wheel versions found; pass --version to select the exact "
            f"release artifact: {candidates}"
        )
    return wheels[0]


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
            _run_check([str(pip), "install", f"{wheel}[dev]"])
        else:
            if not args.version:
                print("error: --version is required when using --source pypi")
                return 2
            _run_check(
                [str(pip), "install", f"structural-lib-is456[dev]=={args.version}"]
            )

        _run_check(
            [
                str(python),
                "-c",
                "from structural_lib import api; print(api.get_library_version())",
            ]
        )

        # Run core tests
        print("\nRunning core tests in clean venv...")
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
                "-m",
                "not slow",
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
        set(changelog_versions) - set(releases_versions), key=_release_version_key
    )
    missing_in_changelog = sorted(
        set(releases_versions) - set(changelog_versions), key=_release_version_key
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

    latest_changelog = max(changelog_versions, key=_release_version_key)
    latest_releases = max(releases_versions, key=_release_version_key)
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

    wheel_arg = getattr(args, "wheel", None)
    source_version_errors = _source_surface_version_errors(
        current, allow_authorized_release=True
    )
    if source_version_errors:
        _print_version_errors(source_version_errors)
        errors += len(source_version_errors)
    else:
        print("  ✓ Source, FastAPI, React, CITATION, and release docs agree")

    permission_errors = _public_distribution_permission_errors()
    if permission_errors:
        _print_version_errors(permission_errors)
        errors += len(permission_errors)
    else:
        print("  ✓ Public-distribution permission is recorded and bounded")

    footing_errors = _footing_release_inclusion_errors()
    if footing_errors:
        _print_version_errors(footing_errors)
        errors += len(footing_errors)
    else:
        print("  ✓ Complete footing D1 slice is included")

    if wheel_arg:
        wheel_errors = _wheel_version_errors(Path(wheel_arg).expanduser(), current)
        if wheel_errors:
            _print_version_errors(wheel_errors)
            errors += len(wheel_errors)
        else:
            print("  ✓ Candidate wheel filename and METADATA agree")
            try:
                imported_version = _clean_wheel_import_version(
                    Path(wheel_arg).expanduser().resolve()
                )
            except (
                OSError,
                subprocess.CalledProcessError,
                subprocess.TimeoutExpired,
            ) as exc:
                print(f"  ✗ clean wheel install/library/CLI check failed: {exc}")
                errors += 1
            else:
                if imported_version != current:
                    print(
                        f"  ✗ clean imported structural_lib={imported_version}, expected {current}"
                    )
                    errors += 1
                else:
                    print("  ✓ Clean installed package and structural_lib CLI agree")
    else:
        print("  ⚠ No candidate wheel supplied; clean-install evidence is pending")
        warnings += 1

    if args.version:
        if not ALPHA_VERSION_RE.fullmatch(args.version):
            print(f"  ✗ Invalid version format: {args.version}")
            print("    Expected PEP 440 Alpha format X.Y.ZaN (for example, 0.24.0a1)")
            errors += 1
        else:
            try:
                if _release_version_key(args.version) <= _release_version_key(current):
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
                _print_failure_tail(test_result)
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
                _print_failure_tail(react_result)
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
                    "-m",
                    "not slow",
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
            node_env, node_status = _node_runtime_env()
            if node_env is None:
                print(f"  ✗ {node_status}")
                errors += 1
                react_result = None
            else:
                print(f"  → Selected {node_status}")
                node_env["NODE_OPTIONS"] = "--max-old-space-size=1536"
                try:
                    react_result = _run_with_timeout(
                        ["npm", "run", "build"],
                        timeout=300,
                        cwd=react_dir,
                        env=node_env,
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
        description=(
            "Unified release management "
            "(run, verify, check-docs, checklist, permission-check, "
            "footing-inclusion-check)"
        ),
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

    # permission-check
    sub.add_parser(
        "permission-check",
        help="Validate owner-confirmed IS 456 public-distribution permission",
    )

    sub.add_parser(
        "footing-inclusion-check",
        help="Validate complete FOOT-ISO-RC-V1 release inclusion",
    )

    # preflight
    p_preflight = sub.add_parser("preflight", help="Run pre-release validation checks")
    p_preflight.add_argument("version", nargs="?", help="Target version to validate")
    p_preflight.add_argument(
        "--docker",
        action="store_true",
        help="Run heavy checks (pytest, npm build) inside Docker containers with memory limits",
    )
    p_preflight.add_argument(
        "--wheel",
        help="Candidate wheel to inspect against the current source version",
    )

    # candidate-check
    p_candidate = sub.add_parser(
        "candidate-check",
        help="Verify source, wheel METADATA, and clean installed package versions",
    )
    p_candidate.add_argument(
        "--wheel", required=True, help="Exact candidate wheel path"
    )
    p_candidate.add_argument(
        "--version", help="Expected version (defaults to Python/pyproject.toml)"
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
        "permission-check": cmd_permission_check,
        "footing-inclusion-check": cmd_footing_inclusion_check,
        "preflight": cmd_preflight,
        "candidate-check": cmd_candidate_check,
    }

    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
