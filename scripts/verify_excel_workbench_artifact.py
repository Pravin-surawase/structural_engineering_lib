#!/usr/bin/env python3
"""Verify E1 workbook identity and behavior from one source-free wheel."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any

_RESOURCE_DIR = "structural_lib/data/excel/outputs/e1-excel-routine-workbench"
_WORKBOOK_MEMBER = f"{_RESOURCE_DIR}/structural-lib-rectangular-beam-workbench-v1.xlsx"
_MANIFEST_MEMBER = f"{_RESOURCE_DIR}/workbook-manifest.json"

_INSTALLED_PROBE = r"""
import hashlib
import json
import os
from importlib import resources
from pathlib import Path

import structural_lib
from structural_lib.core.excel_workbook import (
    ExcelReviewBundleExportRequestV1,
    ExcelWorkbookPreviewRequestV1,
    ExcelWorkbookRunRequestV1,
    ExcelWorkbookSelectionV1,
)
from structural_lib.services.excel_workbench import (
    build_excel_mapping_preview_v1,
    build_excel_review_bundle_v1,
    get_excel_workbench_definition_v1,
    retain_excel_workbook_evidence_v1,
    run_excel_workbook_v1,
    serialize_excel_review_bundle_v1,
)

installed_root = Path(os.environ["E1_INSTALLED_ROOT"]).resolve()
origin = Path(structural_lib.__file__).resolve()
if not origin.is_relative_to(installed_root):
    raise AssertionError(f"structural_lib imported outside wheel target: {origin}")

definition = get_excel_workbench_definition_v1()
if definition.software_capability != "AVAILABLE":
    raise AssertionError(definition)
if definition.installed_windows_excel_evidence != "TO_VERIFY_WINDOWS":
    raise AssertionError(definition)

headers = (
    "Row ID", "Beam ID", "Case ID", "Mu (kN·m)", "Vu (kN)", "b (mm)",
    "D (mm)", "Depth Basis", "d (mm)", "Clear Cover (mm)",
    "Stirrup Dia (mm)", "Tension Bar Dia (mm)", "d' (mm)", "Asv (mm²)",
    "fck (N/mm²)", "fy (N/mm²)", "Shear Basis",
)
rows = ((
    "R1", "B1", "ULS-1", 150.0, 100.0, 300.0, 500.0,
    "DERIVED_FROM_BARS", None, 40.0, 8.0, 18.0, None, 100.0, 25.0, 500.0,
    "AUTO_FROM_FLEXURE",
),)
selection = ExcelWorkbookSelectionV1(
    workbook_instance_id="WHEEL-E1-001",
    first_data_row_number=5,
    locale="en-IN",
    calculation_mode="AUTOMATIC",
)
preview_request = ExcelWorkbookPreviewRequestV1(
    selection=selection,
    headers=headers,
    rows=rows,
)
preview = build_excel_mapping_preview_v1(preview_request)
result = run_excel_workbook_v1(ExcelWorkbookRunRequestV1(
    selection=selection,
    headers=headers,
    rows=rows,
    confirmed_mapping_hash=preview.mapping_hash,
))
if result.row_ledger[0].result_envelope["overall_status"] != "PASS":
    raise AssertionError(result.row_ledger[0])
export_request = ExcelReviewBundleExportRequestV1(
    current_request=preview_request,
    previous_evidence=retain_excel_workbook_evidence_v1(result),
    confirmed_mapping_hash=preview.mapping_hash,
)
review_bundle = build_excel_review_bundle_v1(export_request)
review_bytes = serialize_excel_review_bundle_v1(review_bundle)
repeat_bytes = serialize_excel_review_bundle_v1(
    build_excel_review_bundle_v1(export_request)
)
if review_bytes != repeat_bytes:
    raise AssertionError("Installed review-bundle bytes are not deterministic.")
decoded_bundle = json.loads(review_bytes)
if decoded_bundle["result"]["bundle_hash"] != result.bundle_hash:
    raise AssertionError("Installed review bundle changed the result identity.")
if not decoded_bundle["result"]["row_ledger"][0]["result"]:
    raise AssertionError("Installed review bundle omitted the structured result.")
if not decoded_bundle["result"]["row_ledger"][0]["passport"]:
    raise AssertionError("Installed review bundle omitted the calculation passport.")

resource = resources.files("structural_lib").joinpath(
    "data/excel/outputs/e1-excel-routine-workbench/structural-lib-rectangular-beam-workbench-v1.xlsx"
)
print(json.dumps({
    "origin": str(origin),
    "workbook_resource": str(resource),
    "workbook_sha256": definition.workbook_artifact_sha256,
    "workbook_size_bytes": definition.workbook_artifact_size_bytes,
    "library_version": definition.library_version,
    "library_content_identity": definition.library_content_identity,
    "software_capability": definition.software_capability,
    "installed_windows_excel_evidence": definition.installed_windows_excel_evidence,
    "row_counts": result.counts.model_dump(mode="json"),
    "overall_status": result.row_ledger[0].result_envelope["overall_status"],
    "review_bundle_hash": review_bundle.review_bundle_hash,
    "review_bundle_file_sha256": hashlib.sha256(review_bytes).hexdigest(),
    "review_bundle_size_bytes": len(review_bytes),
}))
"""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _clean_env(installed_root: Path | None = None) -> dict[str, str]:
    env = {
        key: value
        for key, value in os.environ.items()
        if key not in {"PYTHONPATH", "VIRTUAL_ENV"}
    }
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    if installed_root is not None:
        env["PYTHONPATH"] = str(installed_root)
        env["E1_INSTALLED_ROOT"] = str(installed_root)
    return env


def _run(command: list[str], *, cwd: Path, env: dict[str, str]) -> str:
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"command failed ({result.returncode}): {' '.join(command)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result.stdout.strip()


def verify(wheel: Path) -> dict[str, Any]:
    wheel = wheel.resolve()
    if not wheel.is_file() or wheel.suffix != ".whl":
        raise ValueError(f"Wheel does not exist: {wheel}")

    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        if _WORKBOOK_MEMBER not in names or _MANIFEST_MEMBER not in names:
            raise AssertionError("Wheel is missing the E1 workbook or manifest.")
        workbook = archive.read(_WORKBOOK_MEMBER)
        manifest = json.loads(archive.read(_MANIFEST_MEMBER))
        workbook_sha256 = hashlib.sha256(workbook).hexdigest()
        if manifest["artifact_sha256"] != workbook_sha256:
            raise AssertionError("Wheel workbook does not match its artifact manifest.")
        if manifest["artifact_size_bytes"] != len(workbook):
            raise AssertionError("Wheel workbook size does not match its manifest.")

    with tempfile.TemporaryDirectory(prefix="e1_excel_workbench_") as raw_temp:
        temp_root = Path(raw_temp)
        installed_root = temp_root / "installed"
        installed_root.mkdir()
        _run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                "--no-deps",
                "--target",
                str(installed_root),
                str(wheel),
            ],
            cwd=temp_root,
            env=_clean_env(),
        )
        installed_env = _clean_env(installed_root)
        probe = json.loads(
            _run(
                [sys.executable, "-c", _INSTALLED_PROBE],
                cwd=temp_root,
                env=installed_env,
            )
        )
        cli = json.loads(
            _run(
                [sys.executable, "-m", "structural_lib", "excel-v1", "definition"],
                cwd=temp_root,
                env=installed_env,
            )
        )
        if cli["workbook_artifact_sha256"] != workbook_sha256:
            raise AssertionError(
                "Installed CLI definition reports a different workbook."
            )

    return {
        "schema_version": "e1-excel-workbench-artifact-binding/v1",
        "wheel": str(wheel),
        "wheel_sha256": _sha256(wheel),
        "workbook_member": _WORKBOOK_MEMBER,
        "workbook_sha256": workbook_sha256,
        "workbook_size_bytes": len(workbook),
        "source_free_probe": probe,
        "source_free_cli_definition": cli,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.wheel), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
