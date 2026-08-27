#!/usr/bin/env python3
"""Verify LIB-PRO-012 S0 against an installed wheel and exact-head FastAPI."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

_PYTHON_PROBE = r"""
import copy
import inspect
import json
import math
import os
from pathlib import Path

import structural_lib
from structural_lib.codes.is456.beam.torsion import design_torsion
from structural_lib.core.errors import ValidationError
from structural_lib.core.inputs import (
    BeamGeometryInput,
    BeamInput,
    DetailingConfigInput,
    LoadsInput,
)
from structural_lib.services.api import (
    check_beam_is456,
    compute_bbs,
    design_and_detail_beam_is456,
    design_beam_is456,
    design_column_is456,
    detail_beam_is456,
    smart_analyze_design,
)

installed_root = Path(os.environ["S0_INSTALLED_ROOT"]).resolve()
origin = Path(structural_lib.__file__).resolve()
if not origin.is_relative_to(installed_root):
    raise AssertionError(f"structural_lib imported outside installed wheel: {origin}")


def rejects(label, callback, exception_types=(ValueError, TypeError, ValidationError)):
    try:
        callback()
    except exception_types:
        return label
    raise AssertionError(f"{label} did not reject invalid intake")


combined = {
    "units": "IS456",
    "beam_id": "B-S0-WHEEL",
    "story": "GF",
    "span_mm": 5000.0,
    "mu_knm": 150.0,
    "vu_kn": 80.0,
    "b_mm": 300.0,
    "D_mm": 500.0,
    "d_mm": 450.0,
    "cover_mm": 40.0,
    "fck_nmm2": 25.0,
    "fy_nmm2": 500.0,
}
detail = {
    "units": "IS456",
    "beam_id": "B-S0-WHEEL",
    "story": "GF",
    "b_mm": 300.0,
    "D_mm": 500.0,
    "span_mm": 5000.0,
    "cover_mm": 40.0,
    "fck_nmm2": 25.0,
    "fy_nmm2": 500.0,
    "ast_start_mm2": 900.0,
    "ast_mid_mm2": 900.0,
    "ast_end_mm2": 900.0,
}
torsion = {
    "tu_knm": 10.0,
    "vu_kn": 100.0,
    "mu_knm": 150.0,
    "b": 300.0,
    "D": 500.0,
    "d": 450.0,
    "fck": 25.0,
    "fy": 500.0,
    "cover": 40.0,
    "stirrup_dia": 8.0,
    "pt": 1.0,
}
column = {
    "Pu_kN": 800.0,
    "Mux_kNm": 120.0,
    "Muy_kNm": 0.0,
    "b_mm": 300.0,
    "D_mm": 450.0,
    "l_mm": 3000.0,
    "fck_nmm2": 25.0,
    "fy_nmm2": 415.0,
    "Asc_mm2": 2400.0,
}

rejections = []
rejections.append(rejects("combined_span", lambda: design_and_detail_beam_is456(**{**combined, "span_mm": -1.0})))
rejections.append(rejects("combined_action", lambda: design_and_detail_beam_is456(**{**combined, "mu_knm": -1.0})))
rejections.append(rejects("design_action", lambda: design_beam_is456(
    units="IS456", case_id="S0", mu_knm=-1.0, vu_kn=80.0, b_mm=300.0,
    D_mm=500.0, d_mm=450.0, fck_nmm2=25.0, fy_nmm2=500.0,
)))
rejections.append(rejects("compliance_action", lambda: check_beam_is456(
    units="IS456", cases=[{"case_id": "S0", "mu_knm": -1.0, "vu_kn": 80.0}],
    b_mm=300.0, D_mm=500.0, d_mm=450.0, fck_nmm2=25.0, fy_nmm2=500.0,
)))
rejections.append(rejects("smart_action", lambda: smart_analyze_design(
    units="IS456", span_mm=5000.0, mu_knm=-1.0, vu_kn=80.0, b_mm=300.0,
    D_mm=500.0, d_mm=450.0, fck_nmm2=25.0, fy_nmm2=500.0,
)))
rejections.append(rejects("direct_detailing", lambda: detail_beam_is456(**{**detail, "stirrup_spacing_start_mm": 0.0})))
rejections.append(rejects("torsion_action", lambda: design_torsion(**{**torsion, "tu_knm": -1.0})))
rejections.append(rejects("torsion_domain", lambda: design_torsion(**{**torsion, "fy": 600.0})))
rejections.append(rejects("column_action", lambda: design_column_is456(**{**column, "Mux_kNm": -1.0})))
column_without_steel = dict(column)
del column_without_steel["Asc_mm2"]
rejections.append(rejects("column_required_steel", lambda: design_column_is456(**column_without_steel)))
rejections.append(rejects("typed_geometry", lambda: BeamGeometryInput(300.0, 500.0, math.nan)))
rejections.append(rejects("typed_numeric_bool", lambda: LoadsInput(True, 80.0)))
rejections.append(rejects("typed_boolean_string", lambda: DetailingConfigInput.from_dict({"is_seismic": "false"})))
rejections.append(rejects("typed_identity", lambda: BeamInput.from_dict({
    "story": "GF", "geometry": {"b_mm": 300, "D_mm": 500, "span_mm": 5000},
    "materials": {"fck_nmm2": 25, "fy_nmm2": 500},
    "loads": {"mu_knm": 150, "vu_kn": 80},
})))

valid = design_and_detail_beam_is456(**combined)
document = compute_bbs(valid)
if len(document.items) != 9 or document.summary.total_items != 9:
    raise AssertionError("valid BBS reference is not exactly nine items")
invalid_detailing = copy.deepcopy(valid.detailing)
invalid_detailing.span = 0.0
rejections.append(rejects("bbs_direct_input", lambda: compute_bbs(invalid_detailing)))
if not math.isclose(valid.design.flexure.Ast_required, 883.7158126109596):
    raise AssertionError(valid.design.flexure.Ast_required)
valid_torsion = design_torsion(**torsion)
if not math.isclose(valid_torsion.Ve_kn, 153.33333333333334):
    raise AssertionError(valid_torsion.Ve_kn)
if inspect.signature(design_column_is456).parameters["Asc_mm2"].default is not None:
    raise AssertionError("Asc_mm2 signature did not retain the required sentinel")

zero_loads = LoadsInput.from_dict({"mu_knm": 0, "vu_kn": 0})
if zero_loads.mu_knm != 0 or zero_loads.vu_kn != 0:
    raise AssertionError(zero_loads)

print(json.dumps({
    "origin": str(origin),
    "invalid_routes_rejected": rejections,
    "invalid_route_count": len(rejections),
    "valid_bbs_items": len(document.items),
    "valid_ast_required_mm2": valid.design.flexure.Ast_required,
    "valid_torsion_ve_kn": valid_torsion.Ve_kn,
}))
"""

_FASTAPI_PROBE = r"""
import json
import os
from pathlib import Path

import structural_lib
from fastapi.testclient import TestClient
from fastapi_app.main import app

installed_root = Path(os.environ["S0_INSTALLED_ROOT"]).resolve()
origin = Path(structural_lib.__file__).resolve()
if not origin.is_relative_to(installed_root):
    raise AssertionError(f"FastAPI imported checkout structural_lib: {origin}")

client = TestClient(app)
payload = {
    "width": 300,
    "depth": 500,
    "moment": 150,
    "shear": 75,
    "fck": 25,
    "fy": 500,
    "clear_cover": 25,
    "stirrup_dia_mm": 8,
    "main_bar_dia_mm": 20,
}
required = list(payload)
for field in required:
    invalid = dict(payload)
    del invalid[field]
    response = client.post("/api/v1/design/beam", json=invalid)
    if response.status_code != 422:
        raise AssertionError((field, response.status_code, response.text))

strict_vectors = [
    {**payload, "width": "300"},
    {**payload, "moment": True},
    {**payload, "unexpected_engineering_field": 999},
    {**payload, "width": -1},
]
for invalid in strict_vectors:
    response = client.post("/api/v1/design/beam", json=invalid)
    if response.status_code != 422:
        raise AssertionError((invalid, response.status_code, response.text))

invalid_bbs_response = client.post(
    "/api/v1/export/bbs",
    json={
        "width": 300,
        "depth": 500,
        "fck": 25,
        "fy": 500,
        "ast_required": 0,
    },
)
if invalid_bbs_response.status_code != 422:
    raise AssertionError(invalid_bbs_response.text)
invalid_bbs_details = invalid_bbs_response.json()["error"]["details"]
if invalid_bbs_details[0]["loc"] != ["body", "ast_required"]:
    raise AssertionError(invalid_bbs_details)

valid_response = client.post("/api/v1/design/beam", json=payload)
if valid_response.status_code != 200:
    raise AssertionError(valid_response.text)
valid_data = valid_response.json()["data"]
if valid_data["effective_depth_basis"]["source"] != "DERIVED":
    raise AssertionError(valid_data["effective_depth_basis"])
if valid_data["effective_depth_used"] != 457.0:
    raise AssertionError(valid_data["effective_depth_used"])

fail_response = client.post(
    "/api/v1/design/beam", json={**payload, "shear": 10000}
)
if fail_response.status_code != 200:
    raise AssertionError(fail_response.text)
fail_data = fail_response.json()["data"]
if fail_data["result_envelope"]["engineering_status"] != "FAIL":
    raise AssertionError(fail_data["result_envelope"])

print(json.dumps({
    "structural_lib_origin": str(origin),
    "fastapi_origin": str(Path(__import__("fastapi_app").__file__).resolve()),
    "required_field_rejections": required,
    "strict_vector_count": len(strict_vectors),
    "invalid_bbs_http_status": invalid_bbs_response.status_code,
    "valid_http_status": valid_response.status_code,
    "valid_effective_depth_mm": valid_data["effective_depth_used"],
    "engineering_fail_http_status": fail_response.status_code,
    "engineering_fail_status": fail_data["result_envelope"]["engineering_status"],
}))
"""


def _run(command: list[str], *, cwd: Path, env: dict[str, str]) -> str:
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        timeout=240,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"command failed ({result.returncode}): {' '.join(command)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result.stdout.strip()


def _clean_env(*paths: Path) -> dict[str, str]:
    env = {
        key: value
        for key, value in os.environ.items()
        if key not in {"PYTHONPATH", "VIRTUAL_ENV"}
    }
    env["PYTHONPATH"] = os.pathsep.join(str(path) for path in paths)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify(wheel: Path) -> dict[str, Any]:
    """Install one wheel and return its source-free S0 receipt."""
    wheel = wheel.resolve()
    if not wheel.is_file() or wheel.suffix != ".whl":
        raise ValueError(f"Wheel does not exist: {wheel}")

    with tempfile.TemporaryDirectory(prefix="lib_pro_012_s0_") as raw_temp:
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

        wheel_env = _clean_env(installed_root)
        wheel_env["S0_INSTALLED_ROOT"] = str(installed_root)
        python_receipt = json.loads(
            _run([sys.executable, "-c", _PYTHON_PROBE], cwd=temp_root, env=wheel_env)
        )

        app_env = _clean_env(installed_root, REPO_ROOT)
        app_env["S0_INSTALLED_ROOT"] = str(installed_root)
        fastapi_receipt = json.loads(
            _run([sys.executable, "-c", _FASTAPI_PROBE], cwd=temp_root, env=app_env)
        )

        return {
            "schema_version": "lib-pro-012-s0-artifact-replay/v1",
            "wheel": str(wheel),
            "wheel_sha256": _sha256(wheel),
            "source_free_python": python_receipt,
            "exact_head_fastapi_to_wheel": fastapi_receipt,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.wheel), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
