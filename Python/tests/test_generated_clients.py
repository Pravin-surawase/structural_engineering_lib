"""Contract checks for the checked-in basic generated clients."""

from __future__ import annotations

import sys
from pathlib import Path

import httpx
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CLIENT_ROOT = REPO_ROOT / "clients/python"
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(CLIENT_ROOT))

from scripts.generate_client_sdks import generate_basic_typescript_client  # noqa: E402
from scripts.validate_imports import can_resolve_module  # noqa: E402
from structural_client.client import StructuralDesignClient  # noqa: E402


class _Response:
    def __init__(self, payload: dict, status_code: int = 200):
        self.payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                "request failed",
                request=httpx.Request("POST", "http://test"),
                response=httpx.Response(self.status_code),
            )

    def json(self) -> dict:
        return self.payload


class _Transport:
    def post(self, path: str, **kwargs) -> _Response:
        if path == "/api/v2/design/beam":
            request = kwargs["json"]
            if request["section"]["b_mm"] <= 0:
                return _Response(
                    {
                        "success": False,
                        "data": None,
                        "error": {
                            "schema_version": "structural-problem/v1",
                            "code": "INPUT_CONTRACT_INVALID",
                            "message": "Input contract rejected 1 issue(s).",
                        },
                    },
                    status_code=422,
                )
            return _Response(
                {
                    "schema_version": "beam-design-result/v1",
                    "identity": request["identity"],
                    "request": request,
                    "envelope": {"overall_status": "PASS"},
                    "calculation": {},
                    "limitations": [],
                    "assumptions": [],
                    "provenance": [],
                }
            )
        if path.endswith("/design/beam"):
            if kwargs["json"]["width"] <= 0:
                return _Response(
                    {
                        "success": False,
                        "data": None,
                        "error": {
                            "schema_version": "structural-problem/v1",
                            "code": "BEAM_DESIGN_INPUT_INVALID",
                            "message": "Width must be positive",
                        },
                    },
                    status_code=422,
                )
            return _Response(
                {
                    "success": True,
                    "data": {
                        "success": True,
                        "message": "ok",
                        "flexure": {
                            "ast_required": 600.0,
                            "ast_min": 300.0,
                            "ast_max": 1200.0,
                            "xu": 100.0,
                            "xu_max": 200.0,
                            "is_under_reinforced": True,
                            "moment_capacity": 160.0,
                            "asc_required": 0.0,
                        },
                        "shear": None,
                        "ast_total": 600.0,
                        "asc_total": 0.0,
                        "utilization_ratio": 0.75,
                        "effective_depth_basis": {
                            "contract_version": "effective-depth-basis/v1",
                            "source": "DERIVED",
                            "D_mm": 500.0,
                            "d_mm": 457.0,
                            "effective_depth_basis": {
                                "clear_cover_mm": 25.0,
                                "stirrup_diameter_mm": 8.0,
                                "tension_bar_diameter_mm": 20.0,
                            },
                        },
                        "result_envelope": {
                            "schema_version": "structural-result-envelope/v2",
                            "engineering_status": "PASS",
                            "overall_status": "PASS",
                        },
                        "warnings": [],
                    },
                }
            )
        return _Response({"success": True, "data": {"success": True, "components": []}})


def test_python_client_unwraps_success_envelopes_and_uses_maintained_routes():
    client = StructuralDesignClient.__new__(StructuralDesignClient)
    client._client = _Transport()

    design = client.design_beam(300, 500, 100, 25, 500, 75, 25, 8, 20)
    geometry = client.calculate_geometry(300, 500, 5000)

    assert design.flexure.ast_required == 600.0
    assert design.result_envelope["engineering_status"] == "PASS"
    assert design.effective_depth_basis is not None
    assert design.effective_depth_basis["d_mm"] == 457.0
    assert geometry["components"] == []


def test_import_validator_resolves_checked_in_generated_client():
    assert can_resolve_module("structural_client.client")


def test_python_client_preserves_canonical_problem_code_and_message():
    client = StructuralDesignClient.__new__(StructuralDesignClient)
    client._client = _Transport()

    with pytest.raises(
        RuntimeError,
        match="BEAM_DESIGN_INPUT_INVALID: Width must be positive",
    ):
        client.design_beam(0, 500, 100, 25, 500, 75, 25, 8, 20)


def test_python_client_exposes_versioned_canonical_beam_route():
    client = StructuralDesignClient.__new__(StructuralDesignClient)
    client._client = _Transport()
    request = {
        "identity": {"member_id": "B1", "story": "GF", "case_id": "ULS"},
        "section": {"span_mm": 5000, "b_mm": 300, "D_mm": 550, "d_mm": 500},
        "materials": {"fck_nmm2": 25, "fy_nmm2": 500},
        "actions": {"mu_knm": 150, "vu_kn": 80, "tu_knm": 0},
        "calculation_basis": {"d_dash_mm": 50, "asv_mm2": 100},
    }

    result = client.design_beam_v2(request)

    assert result["schema_version"] == "beam-design-result/v1"
    assert result["envelope"]["overall_status"] == "PASS"


def test_typescript_client_matches_generator_with_side_face_choice(tmp_path):
    assert generate_basic_typescript_client(tmp_path)
    generated = tmp_path / "typescript" / "src" / "index.ts"
    checked_in = REPO_ROOT / "clients" / "typescript" / "src" / "index.ts"
    assert generated.read_text(encoding="utf-8") == checked_in.read_text(
        encoding="utf-8"
    )
    assert "side_face_bar_diameter_mm?:" in generated.read_text(encoding="utf-8")
