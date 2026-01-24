"""
Load Tests for FastAPI Application.

Tests API behavior under concurrent load to validate:
- Request handling capacity
- Response time under load
- Error rates at scale
- Memory stability

Usage:
    pytest fastapi_app/tests/test_load.py -v
    pytest fastapi_app/tests/test_load.py -v -k "test_sequential"

Requirements:
    pytest-asyncio, httpx
"""

from __future__ import annotations

import asyncio
import statistics
import time
from typing import Any

import pytest
from fastapi.testclient import TestClient

from fastapi_app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def valid_beam_data() -> dict[str, Any]:
    """Standard valid beam data for testing."""
    return {
        "width": 300,
        "depth": 450,
        "length": 5000,
        "moment": 120,
        "shear": 80,
        "fck": 25,
        "fy": 500,
    }


class TestSequentialLoad:
    """Tests for sequential request load patterns."""

    def test_sequential_design_requests(
        self, client: TestClient, valid_beam_data: dict
    ):
        """Test handling many sequential design requests."""
        num_requests = 50
        latencies = []
        errors = 0

        for _ in range(num_requests):
            start = time.perf_counter()
            response = client.post("/api/v1/design/beam", json=valid_beam_data)
            latencies.append((time.perf_counter() - start) * 1000)
            if response.status_code != 200:
                errors += 1

        success_rate = (num_requests - errors) / num_requests * 100
        assert success_rate >= 95, f"Expected 95%+ success rate, got {success_rate:.1f}%"

        p95 = sorted(latencies)[int(len(latencies) * 0.95)]
        assert p95 < 100, f"P95 latency {p95:.1f}ms exceeds 100ms threshold"

    def test_health_endpoint_under_sequential_load(self, client: TestClient):
        """Health endpoint should remain responsive under load."""
        num_requests = 100
        latencies = []

        for _ in range(num_requests):
            start = time.perf_counter()
            response = client.get("/health")
            latencies.append((time.perf_counter() - start) * 1000)
            assert response.status_code == 200

        assert max(latencies) < 50, f"Max latency {max(latencies):.1f}ms exceeds 50ms"


class TestSustainedLoad:
    """Tests for sustained load over time."""

    def test_sustained_requests_no_degradation(
        self, client: TestClient, valid_beam_data: dict
    ):
        """Response times should not degrade over sustained requests."""
        batches = 5
        requests_per_batch = 20
        batch_latencies = []

        for batch in range(batches):
            latencies = []
            for _ in range(requests_per_batch):
                start = time.perf_counter()
                response = client.post("/api/v1/design/beam", json=valid_beam_data)
                latencies.append((time.perf_counter() - start) * 1000)
                assert response.status_code == 200

            batch_latencies.append(statistics.mean(latencies))

        # Check that later batches are not significantly slower
        first_batch = batch_latencies[0]
        last_batch = batch_latencies[-1]
        degradation = (last_batch - first_batch) / first_batch * 100

        assert degradation < 100, (
            f"Performance degraded {degradation:.1f}% over sustained load"
        )


class TestMixedEndpoints:
    """Tests for mixed endpoint patterns."""

    def test_mixed_endpoint_load(self, client: TestClient, valid_beam_data: dict):
        """Test mixed read/write endpoint patterns."""
        num_iterations = 30
        results = {"design": [], "health": [], "limits": []}

        for _ in range(num_iterations):
            # Design endpoint (write-heavy)
            start = time.perf_counter()
            r = client.post("/api/v1/design/beam", json=valid_beam_data)
            results["design"].append(
                (r.status_code, (time.perf_counter() - start) * 1000)
            )

            # Health endpoint (read-only)
            start = time.perf_counter()
            r = client.get("/health")
            results["health"].append(
                (r.status_code, (time.perf_counter() - start) * 1000)
            )

            # Limits endpoint (read-only)
            start = time.perf_counter()
            r = client.get("/api/v1/design/limits")
            results["limits"].append(
                (r.status_code, (time.perf_counter() - start) * 1000)
            )

        # Validate all endpoints succeeded
        for endpoint, data in results.items():
            successes = sum(1 for status, _ in data if status == 200)
            assert successes == num_iterations, (
                f"{endpoint}: {successes}/{num_iterations} succeeded"
            )


class TestErrorHandlingUnderLoad:
    """Tests for error handling under load."""

    def test_invalid_requests_under_load(self, client: TestClient):
        """Invalid requests should be handled gracefully under load."""
        invalid_data = {"width": -100, "depth": "invalid"}  # Invalid data
        num_requests = 30
        graceful_errors = 0

        for _ in range(num_requests):
            response = client.post("/api/v1/design/beam", json=invalid_data)
            # Should return 422 (validation error), not 500
            if response.status_code in [400, 422]:
                graceful_errors += 1

        assert graceful_errors == num_requests, (
            f"Expected all {num_requests} invalid requests to be handled gracefully"
        )


class TestResourceUsage:
    """Tests for resource consumption."""

    def test_no_connection_leaks(self, client: TestClient, valid_beam_data: dict):
        """Connections should not leak over many requests."""
        # Make many sequential requests
        for _ in range(100):
            response = client.post("/api/v1/design/beam", json=valid_beam_data)
            assert response.status_code == 200

        # If there were connection leaks, we'd start getting errors
        # Final request should still work
        response = client.post("/api/v1/design/beam", json=valid_beam_data)
        assert response.status_code == 200


class TestAsyncConcurrentLoad:
    """Async load tests for true concurrent testing."""

    @pytest.mark.asyncio
    async def test_async_concurrent_requests(self, valid_beam_data: dict):
        """Test async concurrent requests using httpx."""
        import httpx

        num_requests = 30
        results = []

        # Use ASGI transport for async testing
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as client:

            async def make_request():
                start = time.perf_counter()
                response = await client.post(
                    "/api/v1/design/beam", json=valid_beam_data
                )
                return response.status_code, (time.perf_counter() - start) * 1000

            tasks = [make_request() for _ in range(num_requests)]
            results = await asyncio.gather(*tasks)

        successful = [(s, t) for s, t in results if s == 200]
        assert len(successful) >= num_requests * 0.95, (
            f"Expected 95%+ success, got {len(successful)}/{num_requests}"
        )

        if successful:
            latencies = [t for _, t in successful]
            avg_latency = statistics.mean(latencies)
            assert avg_latency < 100, f"Average latency {avg_latency:.1f}ms too high"

    @pytest.mark.asyncio
    async def test_async_mixed_endpoints(self, valid_beam_data: dict):
        """Test concurrent mixed endpoint requests."""
        import httpx

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            # Create mix of request types
            tasks = []
            for i in range(30):
                if i % 3 == 0:
                    tasks.append(
                        client.post("/api/v1/design/beam", json=valid_beam_data)
                    )
                elif i % 3 == 1:
                    tasks.append(client.get("/health"))
                else:
                    tasks.append(client.get("/api/v1/design/limits"))

            results = await asyncio.gather(*tasks)

        successes = sum(1 for r in results if r.status_code == 200)
        assert successes == 30, f"Expected all 30 requests to succeed, got {successes}"
