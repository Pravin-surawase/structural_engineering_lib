"""Installed-package preflight is source-independent and decisive."""

from __future__ import annotations

import json
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
