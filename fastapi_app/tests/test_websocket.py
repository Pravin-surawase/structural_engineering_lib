"""
Tests for WebSocket Live Design Endpoint.

Week 3 Priority 2: WebSocket Live Design Tests
"""

import pytest
from fastapi.testclient import TestClient
from fastapi_app.auth import create_access_token
from fastapi_app.main import app
from fastapi_app.routers import websocket as websocket_router
from starlette.websockets import WebSocketDisconnect


def _design_params(**overrides):
    params = {
        "width": 300,
        "depth": 500,
        "moment": 150,
        "shear": 75,
        "fck": 25,
        "fy": 500,
        "cover": 40,
        "stirrup_dia_mm": 8,
        "main_bar_dia_mm": 20,
    }
    params.update(overrides)
    return params


def _check_params(**overrides):
    params = {
        "schema_version": "beam-supplied-check/v2",
        "correlation_id": "WS-B1-ULS-1",
        "identity": {"member_id": "B1", "story": "L1", "case_id": "ULS-1"},
        "section": {
            "b_mm": 300.0,
            "D_mm": 500.0,
            "effective_depth_basis": {
                "clear_cover_mm": 40.0,
                "stirrup_diameter_mm": 8.0,
                "tension_bar_diameter_mm": 20.0,
            },
        },
        "materials": {
            "fck_nmm2": 25.0,
            "fy_nmm2": 500.0,
            "fy_transverse_nmm2": 415.0,
        },
        "actions": {
            "mu_knm": 100.0,
            "vu_kn": 60.0,
            "primary_tension_face": "BOTTOM",
        },
        "reinforcement": {
            "clear_cover_mm": 40.0,
            "tension": {"diameter_mm": 20.0, "bars_per_layer": [4]},
            "compression_or_hanger": {
                "diameter_mm": 12.0,
                "bars_per_layer": [2],
            },
            "stirrup_diameter_mm": 8.0,
            "stirrup_legs": 2,
            "stirrup_spacing_mm": 150.0,
            "bar_type": "deformed",
            "has_standard_bend_at_start": True,
            "has_standard_bend_at_end": True,
            "source_reference": "Reviewed schedule B1-R1",
        },
        "selection": {
            "permitted_diameters_mm": [12.0, 16.0, 20.0, 25.0],
            "maximum_layers": 2,
            "maximum_bars_per_layer": 8,
            "nominal_max_aggregate_size_mm": 20.0,
            "effective_depth_tolerance_mm": 1.0,
            "objective": "min_area",
            "source_reference": "Reviewed project bar catalogue P1",
        },
        "support": {
            "start_width_mm": 5000.0,
            "end_width_mm": 5000.0,
            "source_reference": "Reviewed supports C1 and C2",
        },
    }
    params.update(overrides)
    return params


def _ws_path(session_id: str, *scopes: str) -> str:
    token = create_access_token(
        {
            "sub": "websocket-test-user",
            "email": "websocket@example.com",
            "scopes": list(scopes or ("design",)),
        }
    )
    return f"/ws/design/{session_id}?token={token}"


class TestWebSocketDesign:
    """Test WebSocket design endpoint."""

    @pytest.mark.parametrize(
        ("path", "close_code"),
        [
            ("/ws/design/auth-missing", 4001),
            ("/ws/design/auth-invalid?token=invalid", 4001),
            (_ws_path("auth-wrong-scope", "analyze"), 4003),
        ],
    )
    def test_websocket_rejects_auth_failure_before_accept(
        self, monkeypatch, path, close_code
    ):
        async def fail_if_accepted(*_args, **_kwargs):
            raise AssertionError("WebSocket must not be accepted before auth passes")

        monkeypatch.setattr(websocket_router.manager, "connect", fail_if_accepted)
        client = TestClient(app)

        with pytest.raises(WebSocketDisconnect) as exc_info:
            with client.websocket_connect(path):
                pass

        assert exc_info.value.code == close_code

    def test_websocket_connect_disconnect(self):
        """Test basic WebSocket connection lifecycle."""
        client = TestClient(app)
        with client.websocket_connect(_ws_path("test-session-1")) as websocket:
            # Send ping
            websocket.send_json({"type": "ping"})
            response = websocket.receive_json()

            assert response["type"] == "pong"
            assert "timestamp" in response

    def test_websocket_design_beam(self):
        """Test design_beam message via WebSocket."""
        client = TestClient(app)
        with client.websocket_connect(_ws_path("test-session-2")) as websocket:
            # Send design request
            websocket.send_json(
                {
                    "type": "design_beam",
                    "params": _design_params(),
                }
            )
            response = websocket.receive_json()

            assert response["type"] == "design_result"
            assert "latency_ms" in response
            assert "data" in response

            # Verify flexure results
            data = response["data"]
            flexure = data["flexure"]
            assert flexure["ast_required"] > 0
            assert flexure["moment_capacity"] > 0
            assert data["success"] is True
            assert data["ast_total"] == flexure["ast_required"]
            assert 0 < data["utilization_ratio"] <= 1.0
            assert data["effective_depth_used"] > 0
            assert data["evidence"]["status"] == "PASS"
            assert data["evidence"]["exact_utilization"] == data["utilization_ratio"]

            shear = data["shear"]
            assert shear["tau_v"] > 0
            assert shear["tau_c_max"] > 0
            assert shear["stirrup_spacing"] > 0

    def test_websocket_and_rest_share_calculation_identity(self):
        client = TestClient(app)
        rest_payload = {
            "width": 300,
            "depth": 500,
            "moment": 150,
            "shear": 75,
            "fck": 25,
            "fy": 500,
            "clear_cover": 40,
            "stirrup_dia_mm": 8,
            "main_bar_dia_mm": 20,
        }
        rest = client.post("/api/v1/design/beam", json=rest_payload).json()["data"]

        with client.websocket_connect(_ws_path("evidence-parity")) as websocket:
            websocket.send_json(
                {
                    "type": "design_beam",
                    "params": {**rest_payload, "cover": rest_payload["clear_cover"]},
                }
            )
            live = websocket.receive_json()["data"]

        assert (
            live["evidence"]["normalized_input_hash"]
            == rest["evidence"]["normalized_input_hash"]
        )
        assert (
            live["evidence"]["calculation_identity"]
            == rest["evidence"]["calculation_identity"]
        )

    def test_websocket_design_beam_latency(self):
        """Test that WebSocket design is fast (<100ms)."""
        client = TestClient(app)
        with client.websocket_connect(_ws_path("test-session-3")) as websocket:
            websocket.send_json(
                {
                    "type": "design_beam",
                    "params": _design_params(),
                }
            )
            response = websocket.receive_json()

            # Should complete in under 100ms (target for V3)
            assert (
                response["latency_ms"] < 100
            ), f"Latency {response['latency_ms']}ms exceeds 100ms target"

    def test_websocket_design_beam_rejects_empty_params(self):
        """No calculation may run from implicit engineering defaults."""
        client = TestClient(app)
        with client.websocket_connect(_ws_path("missing-inputs")) as websocket:
            websocket.send_json({"type": "design_beam", "params": {}})
            response = websocket.receive_json()

        assert response["type"] == "error"
        assert "invalid input" in response["message"].lower()
        assert "data" not in response

    def test_websocket_unknown_message_type(self):
        """Test handling of unknown message types."""
        client = TestClient(app)
        with client.websocket_connect(_ws_path("test-session-4")) as websocket:
            websocket.send_json({"type": "unknown_type"})
            response = websocket.receive_json()

            assert response["type"] == "error"
            assert "unknown_type" in response["message"].lower()

    def test_websocket_check_beam(self):
        """Test check_beam message via WebSocket."""
        client = TestClient(app)
        with client.websocket_connect(_ws_path("test-session-5")) as websocket:
            websocket.send_json(
                {
                    "type": "check_beam",
                    "params": _check_params(),
                }
            )
            response = websocket.receive_json()

            assert response["type"] == "check_result"
            assert response["correlation_id"] == "WS-B1-ULS-1"
            assert response["data"]["schema_version"] == (
                "beam-supplied-check-result/v2"
            )
            assert response["data"]["status"] == "PASS"
            assert response["data"]["effective_depth_resolution"]["d_mm"] == 442.0

    def test_websocket_check_beam_matches_rest_result_exactly(self):
        """REST and WebSocket project the same V2 service result."""

        client = TestClient(app)
        params = _check_params()
        rest = client.post("/api/v1/design/beam/check", json=params)
        assert rest.status_code == 200

        with client.websocket_connect(_ws_path("check-parity")) as websocket:
            websocket.send_json({"type": "check_beam", "params": params})
            websocket_result = websocket.receive_json()

        assert websocket_result["type"] == "check_result"
        assert websocket_result["correlation_id"] == params["correlation_id"]
        assert websocket_result["data"] == rest.json()["data"]

    def test_websocket_check_beam_rejects_legacy_cases_shape(self):
        """The old load-case screening payload cannot claim supplied adequacy."""
        client = TestClient(app)
        with client.websocket_connect(_ws_path("test-session-6")) as websocket:
            websocket.send_json(
                {
                    "type": "check_beam",
                    "params": {"correlation_id": "WS-LEGACY", "cases": []},
                }
            )
            response = websocket.receive_json()

            assert response["type"] == "error"
            assert response["terminal_status"] == "ERROR"
            assert response["correlation_id"] == "WS-LEGACY"
            assert "invalid input" in response["message"].lower()

    def test_websocket_check_beam_rejects_hidden_engineering_defaults(self):
        """The exact load-case-only reproducer must not run a calculation."""
        client = TestClient(app)
        with client.websocket_connect(_ws_path("check-missing-inputs")) as websocket:
            websocket.send_json(
                {
                    "type": "check_beam",
                    "params": {"cases": [{"case_id": "LC1", "mu_knm": 10, "vu_kn": 5}]},
                }
            )
            response = websocket.receive_json()

        assert response["type"] == "error"
        assert response["terminal_status"] == "ERROR"
        assert "invalid input" in response["message"].lower()
        assert "data" not in response

    def test_websocket_check_beam_rejects_unknown_field(self):
        client = TestClient(app)
        with client.websocket_connect(_ws_path("check-unknown-input")) as websocket:
            websocket.send_json(
                {
                    "type": "check_beam",
                    "params": _check_params(widht=300),
                }
            )
            response = websocket.receive_json()

        assert response["type"] == "error"
        assert "invalid input" in response["message"].lower()
        assert "data" not in response

    def test_websocket_check_beam_rejects_non_finite_case_action(self):
        client = TestClient(app)
        params = _check_params()
        params["actions"]["mu_knm"] = float("nan")
        with client.websocket_connect(_ws_path("check-nan-input")) as websocket:
            websocket.send_json(
                {
                    "type": "check_beam",
                    "params": params,
                }
            )
            response = websocket.receive_json()

        assert response["type"] == "error"
        assert "invalid input" in response["message"].lower()
        assert "data" not in response

    def test_websocket_multiple_messages(self):
        """Test multiple design messages on same connection."""
        client = TestClient(app)
        with client.websocket_connect(_ws_path("test-session-7")) as websocket:
            # First design
            websocket.send_json(
                {
                    "type": "design_beam",
                    "params": _design_params(moment=100),
                }
            )
            resp1 = websocket.receive_json()
            ast1 = resp1["data"]["flexure"]["ast_required"]

            # Second design with higher moment
            websocket.send_json(
                {
                    "type": "design_beam",
                    "params": _design_params(moment=200),
                }
            )
            resp2 = websocket.receive_json()
            ast2 = resp2["data"]["flexure"]["ast_required"]

            # Higher moment should require more steel
            assert ast2 > ast1
