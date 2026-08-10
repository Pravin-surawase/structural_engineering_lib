"""Contract checks for the checked-in basic generated clients."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CLIENT_ROOT = REPO_ROOT / "clients/python"
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(CLIENT_ROOT))

from scripts.validate_imports import can_resolve_module  # noqa: E402
from structural_client.client import StructuralDesignClient  # noqa: E402


class _Response:
    def __init__(self, payload: dict):
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self.payload


class _Transport:
    def post(self, path: str, **_kwargs) -> _Response:
        if path.endswith("/design/beam"):
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
                        "warnings": [],
                    },
                }
            )
        return _Response({"success": True, "data": {"success": True, "components": []}})


def test_python_client_unwraps_success_envelopes_and_uses_maintained_routes():
    client = StructuralDesignClient.__new__(StructuralDesignClient)
    client._client = _Transport()

    design = client.design_beam(300, 500, 100, 25, 500)
    geometry = client.calculate_geometry(300, 500, 5000)

    assert design.flexure.ast_required == 600.0
    assert geometry["components"] == []


def test_import_validator_resolves_checked_in_generated_client():
    assert can_resolve_module("structural_client.client")
