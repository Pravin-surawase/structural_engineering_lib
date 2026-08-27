"""
Integration tests for FastAPI structural design endpoints.

Tests end-to-end flows that exercise multiple API components together:
- Design workflow: input validation → calculation → response formatting
- Batch processing: multiple beams → aggregated results
- Error propagation: invalid input → proper error responses
- Cross-endpoint consistency: same input → same results across endpoints

Week 3 Implementation - V3 Migration
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from fastapi_app.main import app
from fastapi_app.tests.conftest import unwrap


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    return TestClient(app)


def _beam_request(**overrides):
    """Return one explicit valid v1 beam request with requested overrides."""
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
    payload.update(overrides)
    return payload


# =============================================================================
# Design Workflow Integration Tests
# =============================================================================


class TestDesignWorkflow:
    """Test complete design workflow from input to output."""

    def test_complete_beam_design_workflow(self, client: TestClient):
        """Test full beam design from valid input to complete result."""
        # Step 1: Design beam
        design_response = client.post(
            "/api/v1/design/beam",
            json=_beam_request(),
        )

        assert design_response.status_code == 200
        result = unwrap(design_response)

        # Verify complete response structure
        assert "message" in result
        assert "flexure" in result

        # Verify flexure details
        flexure = result["flexure"]
        assert "ast_required" in flexure
        assert "ast_min" in flexure
        assert "ast_max" in flexure
        assert isinstance(flexure["ast_required"], (int, float))
        assert flexure["ast_required"] > 0

    def test_design_with_flexure_consistency(self, client: TestClient):
        """Test that flexure design produces consistent results."""
        width, depth = 300, 500

        # Design beam
        response = client.post(
            "/api/v1/design/beam",
            json=_beam_request(width=width, depth=depth),
        )

        assert response.status_code == 200
        result = unwrap(response)

        # Verify flexure metrics are present
        assert "flexure" in result
        assert "ast_required" in result["flexure"]
        assert "ast_min" in result["flexure"]

        # Verify required steel is within bounds
        flexure = result["flexure"]
        assert flexure["ast_required"] >= flexure["ast_min"]
        assert flexure["ast_required"] <= flexure["ast_max"]

    def test_design_validation_chain(self, client: TestClient):
        """Test that validation errors are properly propagated."""
        # Invalid dimensions should fail validation
        response = client.post(
            "/api/v1/design/beam",
            json=_beam_request(width=-100),
        )

        # Should get validation error
        assert response.status_code == 422

    def test_design_calculation_consistency(self, client: TestClient):
        """Test that same input always produces same output."""
        payload = _beam_request()

        # Make multiple requests
        results = []
        for _ in range(3):
            response = client.post("/api/v1/design/beam", json=payload)
            assert response.status_code == 200
            results.append(unwrap(response))

        # Verify consistency
        for i in range(1, len(results)):
            assert (
                results[i]["flexure"]["ast_required"]
                == results[0]["flexure"]["ast_required"]
            )


# =============================================================================
# Batch Processing Integration Tests
# =============================================================================


class TestBatchProcessing:
    """Test batch processing workflows."""

    def test_multiple_beam_designs_sequential(self, client: TestClient):
        """Test sequential design of multiple beams."""
        beams = [
            _beam_request(width=300, depth=500, moment=100),
            _beam_request(width=350, depth=550, moment=150),
            _beam_request(width=400, depth=600, moment=200, fck=30),
        ]

        results = []
        for beam in beams:
            response = client.post("/api/v1/design/beam", json=beam)
            assert response.status_code == 200
            results.append(unwrap(response))

        # Verify all designs completed
        assert len(results) == 3

        # Verify all have valid results
        for result in results:
            assert "flexure" in result
            assert result["flexure"]["ast_required"] > 0

    def test_mixed_valid_invalid_batch(self, client: TestClient):
        """Test that valid requests succeed even when mixed with invalid ones."""
        # Valid request
        valid_response = client.post(
            "/api/v1/design/beam",
            json=_beam_request(moment=100),
        )
        assert valid_response.status_code == 200

        # Invalid request
        invalid_response = client.post(
            "/api/v1/design/beam",
            json=_beam_request(width=-100, moment=100),
        )
        assert invalid_response.status_code == 422

        # Another valid request (system should still work)
        valid_response2 = client.post(
            "/api/v1/design/beam",
            json=_beam_request(width=400, depth=600, moment=200, fck=30),
        )
        assert valid_response2.status_code == 200


# =============================================================================
# Error Handling Integration Tests
# =============================================================================


class TestErrorHandling:
    """Test error handling across the API."""

    def test_validation_error_format(self, client: TestClient):
        """Test validation errors have consistent format."""
        response = client.post(
            "/api/v1/design/beam",
            json=_beam_request(width="not a number"),
        )

        assert response.status_code == 422
        error = response.json()

        assert set(error) == {"success", "data", "error"}
        assert error["success"] is False
        assert error["data"] is None
        assert error["error"]["code"] == "REQUEST_VALIDATION_ERROR"
        assert isinstance(error["error"]["details"], list)
        assert error["error"]["details"]

    def test_missing_required_fields(self, client: TestClient):
        """Test error when required fields are missing."""
        response = client.post(
            "/api/v1/design/beam",
            json={
                "width": 300,
                # Missing depth, moment, etc.
            },
        )

        assert response.status_code == 422

    def test_boundary_values(self, client: TestClient):
        """Test boundary value handling."""
        # Very small moment (edge case)
        response = client.post(
            "/api/v1/design/beam",
            json=_beam_request(moment=0.001),
        )

        # Should either succeed or fail gracefully
        assert response.status_code in [200, 422]


# =============================================================================
# Health & Status Integration Tests
# =============================================================================


class TestHealthStatus:
    """Test health and status endpoints."""

    def test_health_check_complete(self, client: TestClient):
        """Test health endpoint returns complete status."""
        response = client.get("/health")

        assert response.status_code == 200
        health = response.json()

        assert "status" in health
        assert health["status"] == "healthy"

    def test_api_docs_accessible(self, client: TestClient):
        """Test OpenAPI docs are accessible."""
        # OpenAPI JSON
        response = client.get("/openapi.json")
        assert response.status_code == 200

        spec = response.json()
        assert "openapi" in spec
        assert "paths" in spec

    def test_health_before_and_after_design(self, client: TestClient):
        """Test health remains stable after design operations."""
        # Check health
        health1 = client.get("/health").json()
        assert health1["status"] == "healthy"

        # Do some design work
        client.post(
            "/api/v1/design/beam",
            json=_beam_request(),
        )

        # Check health again
        health2 = client.get("/health").json()
        assert health2["status"] == "healthy"


# =============================================================================
# Cross-Endpoint Consistency Tests
# =============================================================================


class TestCrossEndpointConsistency:
    """Test consistency across different API endpoints."""

    def test_design_result_format_consistency(self, client: TestClient):
        """Test that design results have consistent format."""
        payloads = [
            _beam_request(width=300, depth=500, moment=100),
            _beam_request(width=400, depth=600, moment=200, fck=30),
            _beam_request(width=250, depth=450, moment=80, fck=20, fy=415),
        ]

        for payload in payloads:
            response = client.post("/api/v1/design/beam", json=payload)
            assert response.status_code == 200

            result = unwrap(response)

            # All results should have same structure
            assert "flexure" in result
            assert "ast_required" in result["flexure"]
            assert "ast_min" in result["flexure"]


# =============================================================================
# Content Type & Format Tests
# =============================================================================


class TestContentFormats:
    """Test content type handling."""

    def test_json_content_type_required(self, client: TestClient):
        """Test that endpoints require proper content type."""
        response = client.post(
            "/api/v1/design/beam",
            content="width=300&depth=500",  # Form data instead of JSON
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        # Should reject non-JSON
        assert response.status_code == 422

    def test_response_json_format(self, client: TestClient):
        """Test that responses are proper JSON."""
        response = client.post(
            "/api/v1/design/beam",
            json=_beam_request(),
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        # Should parse as valid JSON
        data = response.json()
        assert isinstance(data, dict)


# =============================================================================
# Rate & Limit Tests
# =============================================================================


class TestRatesAndLimits:
    """Test API handles rate and load appropriately."""

    def test_rapid_sequential_requests(self, client: TestClient):
        """Test API handles rapid sequential requests."""
        payload = _beam_request()

        success_count = 0
        for _ in range(20):
            response = client.post("/api/v1/design/beam", json=payload)
            if response.status_code == 200:
                success_count += 1

        # All should succeed
        assert success_count == 20

    def test_large_payload_handling(self, client: TestClient):
        """Test handling of reasonable payload sizes."""
        # Large but valid dimensions
        response = client.post(
            "/api/v1/design/beam",
            json=_beam_request(width=1000, depth=2000, moment=5000, shear=75, fck=40),
        )

        # Should handle large values
        assert response.status_code == 200
