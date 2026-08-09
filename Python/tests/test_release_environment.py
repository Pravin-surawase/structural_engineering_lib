"""Regression tests for local release preflight environment selection."""

from __future__ import annotations

import importlib
import os
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

pytestmark = pytest.mark.repo_only

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

release = importlib.import_module("scripts.release")
node_runtime = importlib.import_module("scripts.node_runtime")


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
