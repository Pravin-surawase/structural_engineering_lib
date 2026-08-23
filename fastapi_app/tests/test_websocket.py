"""
Tests for WebSocket Live Design Endpoint.

Week 3 Priority 2: WebSocket Live Design Tests
"""

from fastapi.testclient import TestClient
from fastapi_app.main import app


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
        "width": 300,
        "depth": 500,
        "fck": 25,
        "fy": 500,
        "cover": 40,
        "cases": [{"case_id": "LC1", "mu_knm": 100, "vu_kn": 50}],
    }
    params.update(overrides)
    return params


class TestWebSocketDesign:
    """Test WebSocket design endpoint."""

    def test_websocket_connect_disconnect(self):
        """Test basic WebSocket connection lifecycle."""
        client = TestClient(app)
        with client.websocket_connect("/ws/design/test-session-1") as websocket:
            # Send ping
            websocket.send_json({"type": "ping"})
            response = websocket.receive_json()

            assert response["type"] == "pong"
            assert "timestamp" in response

    def test_websocket_design_beam(self):
        """Test design_beam message via WebSocket."""
        client = TestClient(app)
        with client.websocket_connect("/ws/design/test-session-2") as websocket:
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

        with client.websocket_connect("/ws/design/evidence-parity") as websocket:
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
        with client.websocket_connect("/ws/design/test-session-3") as websocket:
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
        with client.websocket_connect("/ws/design/missing-inputs") as websocket:
            websocket.send_json({"type": "design_beam", "params": {}})
            response = websocket.receive_json()

        assert response["type"] == "error"
        assert "invalid input" in response["message"].lower()
        assert "data" not in response

    def test_websocket_unknown_message_type(self):
        """Test handling of unknown message types."""
        client = TestClient(app)
        with client.websocket_connect("/ws/design/test-session-4") as websocket:
            websocket.send_json({"type": "unknown_type"})
            response = websocket.receive_json()

            assert response["type"] == "error"
            assert "unknown_type" in response["message"].lower()

    def test_websocket_check_beam(self):
        """Test check_beam message via WebSocket."""
        client = TestClient(app)
        with client.websocket_connect("/ws/design/test-session-5") as websocket:
            websocket.send_json(
                {
                    "type": "check_beam",
                    "params": _check_params(
                        cases=[
                            {"case_id": "DL", "mu_knm": 100, "vu_kn": 50},
                            {"case_id": "LL", "mu_knm": 150, "vu_kn": 75},
                        ]
                    ),
                }
            )
            response = websocket.receive_json()

            assert response["type"] == "check_result"
            assert "data" in response
            assert "is_ok" in response["data"]
            assert response["data"]["num_cases"] == 2

    def test_websocket_check_beam_no_cases(self):
        """Test check_beam with no cases returns error."""
        client = TestClient(app)
        with client.websocket_connect("/ws/design/test-session-6") as websocket:
            websocket.send_json(
                {
                    "type": "check_beam",
                    "params": _check_params(cases=[]),
                }
            )
            response = websocket.receive_json()

            assert response["type"] == "error"
            assert "no load cases" in response["message"].lower()

    def test_websocket_check_beam_rejects_hidden_engineering_defaults(self):
        """The exact load-case-only reproducer must not run a calculation."""
        client = TestClient(app)
        with client.websocket_connect("/ws/design/check-missing-inputs") as websocket:
            websocket.send_json(
                {
                    "type": "check_beam",
                    "params": {"cases": [{"case_id": "LC1", "mu_knm": 10, "vu_kn": 5}]},
                }
            )
            response = websocket.receive_json()

        assert response["type"] == "error"
        assert "invalid input" in response["message"].lower()
        assert "data" not in response

    def test_websocket_check_beam_rejects_unknown_field(self):
        client = TestClient(app)
        with client.websocket_connect("/ws/design/check-unknown-input") as websocket:
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
        with client.websocket_connect("/ws/design/check-nan-input") as websocket:
            websocket.send_json(
                {
                    "type": "check_beam",
                    "params": _check_params(
                        cases=[
                            {
                                "case_id": "LC1",
                                "mu_knm": float("nan"),
                                "vu_kn": 5,
                            }
                        ]
                    ),
                }
            )
            response = websocket.receive_json()

        assert response["type"] == "error"
        assert "invalid input" in response["message"].lower()
        assert "data" not in response

    def test_websocket_multiple_messages(self):
        """Test multiple design messages on same connection."""
        client = TestClient(app)
        with client.websocket_connect("/ws/design/test-session-7") as websocket:
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
