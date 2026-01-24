"""
Tests for WebSocket Live Design Endpoint.

Week 3 Priority 2: WebSocket Live Design Tests
"""

import pytest
from fastapi.testclient import TestClient
from fastapi_app.main import app


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
            websocket.send_json({
                "type": "design_beam",
                "params": {
                    "width": 300,
                    "depth": 500,
                    "moment": 150,
                    "shear": 75,
                    "fck": 25,
                    "fy": 500
                }
            })
            response = websocket.receive_json()

            assert response["type"] == "design_result"
            assert "latency_ms" in response
            assert "data" in response

            # Verify flexure results
            flexure = response["data"]["flexure"]
            assert flexure["ast_required"] > 0
            assert flexure["is_safe"] is not None

    def test_websocket_design_beam_latency(self):
        """Test that WebSocket design is fast (<100ms)."""
        client = TestClient(app)
        with client.websocket_connect("/ws/design/test-session-3") as websocket:
            websocket.send_json({
                "type": "design_beam",
                "params": {
                    "width": 300,
                    "depth": 500,
                    "moment": 150,
                    "fck": 25,
                    "fy": 500
                }
            })
            response = websocket.receive_json()

            # Should complete in under 100ms (target for V3)
            assert response["latency_ms"] < 100, f"Latency {response['latency_ms']}ms exceeds 100ms target"

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
            websocket.send_json({
                "type": "check_beam",
                "params": {
                    "width": 300,
                    "depth": 500,
                    "fck": 25,
                    "fy": 500,
                    "cases": [
                        {"case_id": "DL", "mu_knm": 100, "vu_kn": 50},
                        {"case_id": "LL", "mu_knm": 150, "vu_kn": 75}
                    ]
                }
            })
            response = websocket.receive_json()

            assert response["type"] == "check_result"
            assert "data" in response
            assert "is_ok" in response["data"]
            assert response["data"]["num_cases"] == 2

    def test_websocket_check_beam_no_cases(self):
        """Test check_beam with no cases returns error."""
        client = TestClient(app)
        with client.websocket_connect("/ws/design/test-session-6") as websocket:
            websocket.send_json({
                "type": "check_beam",
                "params": {
                    "width": 300,
                    "depth": 500,
                    "cases": []  # Empty cases
                }
            })
            response = websocket.receive_json()

            assert response["type"] == "error"
            assert "no load cases" in response["message"].lower()

    def test_websocket_multiple_messages(self):
        """Test multiple design messages on same connection."""
        client = TestClient(app)
        with client.websocket_connect("/ws/design/test-session-7") as websocket:
            # First design
            websocket.send_json({
                "type": "design_beam",
                "params": {"width": 300, "depth": 500, "moment": 100, "fck": 25, "fy": 500}
            })
            resp1 = websocket.receive_json()
            ast1 = resp1["data"]["flexure"]["ast_required"]

            # Second design with higher moment
            websocket.send_json({
                "type": "design_beam",
                "params": {"width": 300, "depth": 500, "moment": 200, "fck": 25, "fy": 500}
            })
            resp2 = websocket.receive_json()
            ast2 = resp2["data"]["flexure"]["ast_required"]

            # Higher moment should require more steel
            assert ast2 > ast1
