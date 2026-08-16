"""Installed-package preflight is source-independent and decisive."""

from __future__ import annotations

import json

from structural_lib import __main__ as cli


def test_install_preflight_reports_origin_version_extras_and_repair(capsys) -> None:
    assert cli.main(["install-preflight", "--json"]) == 0

    report = json.loads(capsys.readouterr().out)
    assert report["interpreter"]
    assert report["python_version"]
    assert report["package_version"]
    assert report["package_origin"].endswith("structural_lib/__init__.py")
    assert set(report["optional_extras"]) == {
        "dxf",
        "report",
        "pdf",
        "render",
        "validation",
    }
    assert report["repair_command"].startswith(report["interpreter"])
    assert report["qualified_review_required"] is True
