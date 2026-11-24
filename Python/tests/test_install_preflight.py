"""Installed-package preflight is source-independent and decisive."""

from __future__ import annotations

import json
import logging
import os
import shlex
import subprocess
import sys
from pathlib import Path

import pytest

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
    if sys.platform == "win32":
        executable = report["interpreter"].replace("'", "''")
        assert report["repair_command"].startswith(f"& '{executable}' ")
    else:
        assert shlex.split(report["repair_command"])[0] == report["interpreter"]
    assert (
        f"structural-lib-is456==={report['package_version']}"
        in report["repair_command"]
    )
    assert report["qualified_review_required"] is True


@pytest.mark.parametrize(
    ("modules", "expected"),
    [
        (
            {"matplotlib", "reportlab"},
            {
                "dxf": False,
                "report": False,
                "pdf": False,
                "render": False,
                "validation": False,
            },
        ),
        (
            {"ezdxf", "weasyprint"},
            {
                "dxf": True,
                "report": False,
                "pdf": False,
                "render": False,
                "validation": False,
            },
        ),
        (
            {"ezdxf", "matplotlib", "reportlab", "weasyprint", "jinja2", "jsonschema"},
            {
                "dxf": True,
                "report": True,
                "pdf": True,
                "render": True,
                "validation": True,
            },
        ),
    ],
)
def test_install_preflight_checks_every_module_in_an_extra(
    modules, expected, monkeypatch, capsys
) -> None:
    monkeypatch.setattr(
        cli.importlib.util,
        "find_spec",
        lambda name: object() if name in modules else None,
    )

    assert cli.main(["install-preflight", "--json"]) == 0

    extras = json.loads(capsys.readouterr().out)["optional_extras"]
    assert extras == expected
    assert all(isinstance(value, bool) for value in extras.values())


def test_install_preflight_quotes_repair_command_for_posix() -> None:
    executable = "/tmp/Audit O'Brien/bin/python"
    command = cli._format_preflight_repair_command(
        executable, "0.31.1", powershell=False
    )

    assert shlex.split(command) == [
        executable,
        "-m",
        "pip",
        "install",
        "--upgrade",
        "structural-lib-is456===0.31.1",
    ]


def test_install_preflight_quotes_repair_command_for_powershell() -> None:
    executable = r"C:\Audit O'Brien\Scripts\python.exe"
    command = cli._format_preflight_repair_command(
        executable, "0.31.1", powershell=True
    )

    assert command == (
        r"& 'C:\Audit O''Brien\Scripts\python.exe' '-m' 'pip' 'install' "
        "'--upgrade' 'structural-lib-is456===0.31.1'"
    )


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
