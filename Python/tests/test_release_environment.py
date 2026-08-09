"""Regression tests for local release preflight environment selection."""

from __future__ import annotations

import importlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.repo_only

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

release = importlib.import_module("scripts.release")


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
