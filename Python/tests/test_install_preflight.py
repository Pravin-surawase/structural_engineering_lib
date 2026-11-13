"""Installed-package preflight is source-independent and decisive."""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
from pathlib import Path

from structural_lib import __main__ as cli


def test_install_preflight_reports_origin_version_extras_and_repair(capsys) -> None:
    assert cli.main(["install-preflight", "--json"]) == 0

    report = json.loads(capsys.readouterr().out)
    assert report["interpreter"]
    assert report["python_version"]
    assert report["package_version"]
    assert Path(report["package_origin"]).parts[-2:] == (
        "structural_lib",
        "__init__.py",
    )
    assert report["runtime_identity"]["package_version"] == report["package_version"]
    assert report["runtime_identity"]["package_origin"] == report["package_origin"]
    assert report["runtime_identity"]["execution_mode"] in {
        "SOURCE_CHECKOUT",
        "INSTALLED_DISTRIBUTION",
    }
    assert set(report["optional_extras"]) == {
        "dxf",
        "report",
        "pdf",
        "render",
        "validation",
    }
    assert report["repair_command"].startswith(report["interpreter"])
    assert report["qualified_review_required"] is True


def test_unsupported_log_level_keeps_package_and_cli_available() -> None:
    env = {
        **os.environ,
        "PYTHONPATH": str(Path(cli.__file__).resolve().parents[1]),
        "STRUCTURAL_LIB_LOG_LEVEL": "BASIC_FORMAT",
    }
    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            "import logging, structural_lib; "
            "print(logging.getLogger('structural_lib').getEffectiveLevel())",
        ],
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    assert probe.stdout.strip() == str(logging.WARNING)
    preflight = subprocess.run(
        [sys.executable, "-m", "structural_lib", "install-preflight", "--json"],
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(preflight.stdout)["package_version"]
