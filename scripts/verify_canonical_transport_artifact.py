#!/usr/bin/env python3
"""Verify A1's source-free wheel and exact-head application import boundary.

When to use: after building the frozen A1 wheel outside the repository.
"""

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
import json
import os
from pathlib import Path

import structural_lib
from structural_lib import api as compatibility_api
from structural_lib.core.version import get_runtime_version_identity
from structural_lib.services import api as service_api
from structural_lib.services.project_beam import EffectiveDepthBasisV1
from structural_lib.services.serialization import to_transport_value

installed_root = Path(os.environ["A1_INSTALLED_ROOT"]).resolve()
origin = Path(structural_lib.__file__).resolve()
if not origin.is_relative_to(installed_root):
    raise AssertionError(f"structural_lib imported outside wheel target: {origin}")
identity = get_runtime_version_identity(origin)
if identity.execution_mode != "INSTALLED_DISTRIBUTION":
    raise AssertionError(identity.to_dict())

inputs = {
    "units": "IS456",
    "case_id": "CASE-1",
    "b_mm": 300.0,
    "D_mm": 500.0,
    "d_mm": None,
    "effective_depth_basis": EffectiveDepthBasisV1(40.0, 8.0, 18.0),
    "mu_knm": 150.0,
    "vu_kn": 420.0,
    "fck_nmm2": 25.0,
    "fy_nmm2": 500.0,
}
results = [
    service_api.design_beam_is456(**inputs),
    structural_lib.design_beam_is456(**inputs),
    compatibility_api.design_beam_is456(**inputs),
]
payloads = [to_transport_value(result) for result in results]
if not payloads[0] == payloads[1] == payloads[2]:
    raise AssertionError("wheel facades returned different results")
result = payloads[0]
if result["effective_depth_resolution"]["d_mm"] != 443.0:
    raise AssertionError(result["effective_depth_resolution"])
if result["result_envelope"]["engineering_status"] != "FAIL":
    raise AssertionError(result["result_envelope"])
print(json.dumps({
    "origin": str(origin),
    "version_identity": identity.to_dict(),
    "engineering_status": result["result_envelope"]["engineering_status"],
    "effective_depth_mm": result["effective_depth_resolution"]["d_mm"],
}))
"""

_FASTAPI_PROBE = r"""
import json
import os
from pathlib import Path

import structural_lib
from fastapi.testclient import TestClient
from fastapi_app.main import app

installed_root = Path(os.environ["A1_INSTALLED_ROOT"]).resolve()
origin = Path(structural_lib.__file__).resolve()
if not origin.is_relative_to(installed_root):
    raise AssertionError(f"FastAPI imported checkout structural_lib: {origin}")
response = TestClient(app).post("/api/v1/design/beam", json={
    "width": 300.0,
    "depth": 500.0,
    "clear_cover": 40.0,
    "stirrup_dia_mm": 8.0,
    "main_bar_dia_mm": 18.0,
    "moment": 150.0,
    "shear": 420.0,
    "fck": 25.0,
    "fy": 500.0,
})
if response.status_code != 200:
    raise AssertionError(response.text)
outer = response.json()
result = outer["data"]
if outer["success"] is not True or result["success"] is not False:
    raise AssertionError(outer)
if result["effective_depth_basis"]["d_mm"] != 443.0:
    raise AssertionError(result["effective_depth_basis"])
if result["result_envelope"]["engineering_status"] != "FAIL":
    raise AssertionError(result["result_envelope"])
print(json.dumps({
    "structural_lib_origin": str(origin),
    "fastapi_origin": str(Path(__import__("fastapi_app").__file__).resolve()),
    "http_status": response.status_code,
    "outer_success": outer["success"],
    "engineering_status": result["result_envelope"]["engineering_status"],
    "effective_depth_mm": result["effective_depth_basis"]["d_mm"],
}))
"""


def _run(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    timeout: int = 180,
) -> str:
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
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


def _wheel_sha256(wheel: Path) -> str:
    digest = hashlib.sha256()
    with wheel.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify(wheel: Path) -> dict[str, Any]:
    """Return a machine-readable receipt for one exact wheel."""

    wheel = wheel.resolve()
    if not wheel.is_file() or wheel.suffix != ".whl":
        raise ValueError(f"Wheel does not exist: {wheel}")

    with tempfile.TemporaryDirectory(prefix="a1_canonical_transport_") as raw_temp:
        temp_root = Path(raw_temp)
        installed_root = temp_root / "installed"
        installed_root.mkdir()
        install_env = _clean_env()
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
            env=install_env,
        )

        wheel_env = _clean_env(installed_root)
        wheel_env["A1_INSTALLED_ROOT"] = str(installed_root)
        python_receipt = json.loads(
            _run(
                [sys.executable, "-c", _PYTHON_PROBE],
                cwd=temp_root,
                env=wheel_env,
            )
        )

        cli_input = temp_root / "beam.json"
        cli_output = temp_root / "result.json"
        cli_input.write_text(
            json.dumps(
                {
                    "schema_version": "cli-beam-design-input/v1",
                    "beams": [
                        {
                            "member_id": "B-BOUNDARY",
                            "story": "L1",
                            "b_mm": 300.0,
                            "D_mm": 500.0,
                            "span_mm": 5000.0,
                            "clear_cover_mm": 40.0,
                            "stirrup_diameter_mm": 8.0,
                            "stirrup_spacing_mm": 150.0,
                            "tension_bar_diameter_mm": 18.0,
                            "mu_knm": 150.0,
                            "vu_kn": 420.0,
                            "fck_nmm2": 25.0,
                            "fy_nmm2": 500.0,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        _run(
            [
                sys.executable,
                "-m",
                "structural_lib",
                "design",
                str(cli_input),
                "-o",
                str(cli_output),
            ],
            cwd=temp_root,
            env=wheel_env,
        )
        cli_result = json.loads(cli_output.read_text(encoding="utf-8"))["beams"][0]
        if cli_result["effective_depth_resolution"]["d_mm"] != 443.0:
            raise AssertionError(cli_result["effective_depth_resolution"])
        if cli_result["result_envelope"]["engineering_status"] != "FAIL":
            raise AssertionError(cli_result["result_envelope"])

        app_env = _clean_env(installed_root, REPO_ROOT)
        app_env["A1_INSTALLED_ROOT"] = str(installed_root)
        fastapi_receipt = json.loads(
            _run(
                [sys.executable, "-c", _FASTAPI_PROBE],
                cwd=temp_root,
                env=app_env,
            )
        )
        return {
            "schema_version": "a1-canonical-artifact-binding/v1",
            "wheel": str(wheel),
            "wheel_sha256": _wheel_sha256(wheel),
            "source_free_python": python_receipt,
            "source_free_cli": {
                "engineering_status": cli_result["result_envelope"][
                    "engineering_status"
                ],
                "effective_depth_mm": cli_result["effective_depth_resolution"]["d_mm"],
            },
            "exact_head_fastapi": fastapi_receipt,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.wheel), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
