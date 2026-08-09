"""Regression tests for local release preflight environment selection."""

from __future__ import annotations

import importlib
import os
import subprocess
import sys
import tomllib
import zipfile
from pathlib import Path

import pytest

pytestmark = pytest.mark.repo_only

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

release = importlib.import_module("scripts.release")
node_runtime = importlib.import_module("scripts.node_runtime")


def test_type_check_toolchain_requires_explicit_migration():
    """Do not let CI silently cross known Mypy/NumPy stub boundaries."""
    pyproject = tomllib.loads(
        (REPO_ROOT / "Python" / "pyproject.toml").read_text(encoding="utf-8")
    )
    dev_requirements = pyproject["project"]["optional-dependencies"]["dev"]
    root_requirements = (REPO_ROOT / "requirements.txt").read_text(encoding="utf-8")
    locked_requirements = (REPO_ROOT / "requirements-lock.txt").read_text(
        encoding="utf-8"
    )

    assert "mypy>=1.19,<2" in dev_requirements
    assert "numpy>=2.0,<2.5" in dev_requirements
    assert "mypy>=1.19,<2" in root_requirements.splitlines()
    assert "numpy>=2.0,<2.5" in root_requirements.splitlines()
    assert any(line.startswith("mypy==1.") for line in locked_requirements.splitlines())
    assert "numpy==2.4.6" in locked_requirements.splitlines()


def test_available_ram_uses_memory_pressure_percentage(
    monkeypatch: pytest.MonkeyPatch,
):
    def fake_run(args, **kwargs):
        if args[:2] == ["memory_pressure", "-Q"]:
            return subprocess.CompletedProcess(
                args, 0, "System-wide memory free percentage: 67%\n", ""
            )
        if args == ["sysctl", "-n", "hw.memsize"]:
            return subprocess.CompletedProcess(args, 0, str(16 * 1024**3), "")
        raise AssertionError(args)

    monkeypatch.setattr(release.subprocess, "run", fake_run)

    assert release._available_ram_gb() == pytest.approx(10.72)


def test_node_runtime_prefers_required_healthy_binary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    node_bin = tmp_path / "node24" / "bin"
    node_bin.mkdir(parents=True)
    node = node_bin / "node"
    npm = node_bin / "npm"
    node.write_text("#!/bin/sh\necho v24.19.0\n", encoding="utf-8")
    npm.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    node.chmod(0o755)
    npm.chmod(0o755)
    monkeypatch.setattr(release, "_required_node_major", lambda: "24")

    env, status = release._node_runtime_env(candidate_bins=[node_bin])

    assert env is not None
    assert env["PATH"].split(os.pathsep)[0] == str(node_bin.resolve())
    assert status == "v24.19.0"


def test_node_runtime_rejects_wrong_major(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    node_bin = tmp_path / "node25" / "bin"
    node_bin.mkdir(parents=True)
    for name in ("node", "npm"):
        executable = node_bin / name
        executable.write_text(
            "#!/bin/sh\necho v25.2.1\n" if name == "node" else "#!/bin/sh\nexit 0\n",
            encoding="utf-8",
        )
        executable.chmod(0o755)
    monkeypatch.setattr(release, "_required_node_major", lambda: "24")

    env, status = release._node_runtime_env(candidate_bins=[node_bin])

    assert env is None
    assert "Node 24.x" in status


def test_shared_node_runtime_reads_repo_pin(tmp_path: Path):
    (tmp_path / ".nvmrc").write_text("24\n", encoding="utf-8")

    assert node_runtime.required_node_major(tmp_path) == "24"


def test_shared_node_runtime_rejects_missing_npm(tmp_path: Path):
    node_bin = tmp_path / "node24" / "bin"
    node_bin.mkdir(parents=True)
    node = node_bin / "node"
    node.write_text("#!/bin/sh\necho v24.19.0\n", encoding="utf-8")
    node.chmod(0o755)

    env, status = node_runtime.node_runtime_env(
        required_major="24", candidate_bins=[node_bin]
    )

    assert env is None
    assert "Node 24.x" in status


def test_launcher_delegates_to_shared_node_runtime():
    launcher = (REPO_ROOT / "scripts" / "launch_stack.sh").read_text(encoding="utf-8")

    assert '"$REPO_ROOT/scripts/node_runtime.py" --bin-dir' in launcher


def _write_release_surfaces(tmp_path: Path, version: str = "0.23.0") -> dict[str, Path]:
    pyproject = tmp_path / "Python" / "pyproject.toml"
    pyproject.parent.mkdir()
    pyproject.write_text(f'[project]\nversion = "{version}"\n', encoding="utf-8")
    fastapi_init = tmp_path / "fastapi_app" / "__init__.py"
    fastapi_init.parent.mkdir()
    fastapi_init.write_text(f'__version__ = "{version}"\n', encoding="utf-8")
    react_package = tmp_path / "react_app" / "package.json"
    react_package.parent.mkdir()
    react_package.write_text(f'{{"version": "{version}"}}\n', encoding="utf-8")
    citation = tmp_path / "CITATION.cff"
    citation.write_text(
        f"version: {version}\nmessage: not tagged or published\n", encoding="utf-8"
    )
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(
        f"## [{version}] — Prepared candidate (unreleased; on hold)\n",
        encoding="utf-8",
    )
    releases = tmp_path / "releases.md"
    releases.write_text(
        f"## v{version}\n\nStatus: not tagged or published\n", encoding="utf-8"
    )
    return {
        "PYPROJECT": pyproject,
        "FASTAPI_INIT": fastapi_init,
        "REACT_PACKAGE": react_package,
        "CITATION": citation,
        "CHANGELOG": changelog,
        "RELEASES": releases,
    }


def test_source_surface_versions_match_prepared_candidate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    for name, path in _write_release_surfaces(tmp_path).items():
        monkeypatch.setattr(release, name, path)

    assert release._source_surface_version_errors("0.23.0") == []


def test_source_surface_versions_match_owner_authorized_release(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    paths = _write_release_surfaces(tmp_path)
    paths["CITATION"].write_text(
        "version: 0.23.0\ndate-released: 2026-08-10\n"
        "message: Alpha development preview\n",
        encoding="utf-8",
    )
    paths["CHANGELOG"].write_text("## [0.23.0] — 2026-08-10\n", encoding="utf-8")
    paths["RELEASES"].write_text(
        "## v0.23.0\n\nStatus: Alpha release authorized\n", encoding="utf-8"
    )
    checklist = tmp_path / "pre-release-checklist.md"
    checklist.write_text(
        "- [x] Owner authorizes the v0.23.0 tag, production PyPI publication, "
        "and GitHub Release after exact CI evidence passes\n",
        encoding="utf-8",
    )
    paths["CHECKLIST_PATH"] = checklist
    for name, path in paths.items():
        monkeypatch.setattr(release, name, path)

    assert (
        release._source_surface_version_errors("0.23.0", allow_authorized_release=True)
        == []
    )


def test_release_ready_metadata_requires_recorded_owner_authorization(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    paths = _write_release_surfaces(tmp_path)
    paths["CITATION"].write_text(
        "version: 0.23.0\ndate-released: 2026-08-10\n",
        encoding="utf-8",
    )
    checklist = tmp_path / "pre-release-checklist.md"
    checklist.write_text(
        "- [ ] Owner authorizes the v0.23.0 tag, production PyPI publication, "
        "and GitHub Release after exact CI evidence passes\n",
        encoding="utf-8",
    )
    paths["CHECKLIST_PATH"] = checklist
    for name, path in paths.items():
        monkeypatch.setattr(release, name, path)

    errors = release._source_surface_version_errors(
        "0.23.0", allow_authorized_release=True
    )

    assert "CITATION.cff declares date-released for an unpublished candidate" in errors


def test_source_surface_versions_fail_on_deliberate_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    paths = _write_release_surfaces(tmp_path)
    paths["REACT_PACKAGE"].write_text('{"version": "0.23.1"}\n', encoding="utf-8")
    for name, path in paths.items():
        monkeypatch.setattr(release, name, path)

    assert (
        "react_app/package.json=0.23.1, expected 0.23.0"
        in release._source_surface_version_errors("0.23.0")
    )


def test_wheel_versions_fail_on_deliberate_metadata_mismatch(tmp_path: Path):
    wheel = tmp_path / "structural_lib_is456-0.23.0-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr(
            "structural_lib_is456-0.23.1.dist-info/METADATA",
            "Metadata-Version: 2.4\nName: structural-lib-is456\nVersion: 0.23.1\n",
        )

    assert release._wheel_version_errors(wheel, "0.23.0") == [
        "wheel METADATA=0.23.1, expected 0.23.0"
    ]


def test_wheel_check_rejects_excluded_package_content(tmp_path: Path):
    wheel = tmp_path / "structural_lib_is456-0.23.0-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr(
            "structural_lib_is456-0.23.0.dist-info/METADATA",
            "Metadata-Version: 2.4\nName: structural-lib-is456\nVersion: 0.23.0\n",
        )
        archive.writestr("structural_lib/research/__init__.py", "")

    assert release._wheel_version_errors(wheel, "0.23.0") == [
        "wheel contains excluded package content: structural_lib/research/__init__.py"
    ]
