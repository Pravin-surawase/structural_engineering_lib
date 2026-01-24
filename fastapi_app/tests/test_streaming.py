"""
Tests for SSE Streaming Endpoint.

Week 3 Priority 3: SSE for batch processing tests.
"""

import json

import pytest
from fastapi.testclient import TestClient
from fastapi_app.main import app


class TestSSEBatchDesign:
    """Test SSE batch design endpoint."""

    def test_batch_design_single_beam(self):
        """Test batch design with single beam."""
        client = TestClient(app)
        beams = json.dumps([{"width": 300, "depth": 500, "moment": 100, "fck": 25, "fy": 500}])

        with client.stream("GET", f"/stream/batch-design?beams={beams}") as response:
            events = list(response.iter_lines())

        # Should have start, design_result, progress, complete events
        assert len(events) >= 4, f"Expected at least 4 events, got {len(events)}"

        # Parse events (SSE format: event: type\ndata: {...})
        event_types = []
        for line in events:
            if line.startswith("event:"):
                event_types.append(line.split(":")[1].strip())

        assert "start" in event_types
        assert "design_result" in event_types
        assert "complete" in event_types

    def test_batch_design_multiple_beams(self):
        """Test batch design with multiple beams."""
        client = TestClient(app)
        beams = json.dumps([
            {"id": "B1", "width": 300, "depth": 500, "moment": 100, "fck": 25, "fy": 500},
            {"id": "B2", "width": 350, "depth": 600, "moment": 200, "fck": 30, "fy": 500},
            {"id": "B3", "width": 400, "depth": 700, "moment": 300, "fck": 25, "fy": 500},
        ])

        with client.stream("GET", f"/stream/batch-design?beams={beams}") as response:
            events = list(response.iter_lines())

        # Count design_result events
        result_count = sum(1 for line in events if "design_result" in line)
        assert result_count >= 3, f"Expected at least 3 design_result events, got {result_count}"

    def test_batch_design_invalid_json(self):
        """Test batch design with invalid JSON."""
        client = TestClient(app)

        with client.stream("GET", "/stream/batch-design?beams=not_valid_json") as response:
            events = list(response.iter_lines())

        # Should have error event
        has_error = any("error" in line for line in events)
        assert has_error, "Expected error event for invalid JSON"

    def test_batch_design_empty_array(self):
        """Test batch design with empty array."""
        client = TestClient(app)

        with client.stream("GET", "/stream/batch-design?beams=[]") as response:
            events = list(response.iter_lines())

        has_error = any("error" in line for line in events)
        assert has_error, "Expected error event for empty array"

    def test_batch_design_progress_tracking(self):
        """Test that progress events are sent."""
        client = TestClient(app)
        beams = json.dumps([
            {"width": 300, "depth": 500, "moment": 100, "fck": 25, "fy": 500},
            {"width": 300, "depth": 500, "moment": 150, "fck": 25, "fy": 500},
        ])

        with client.stream("GET", f"/stream/batch-design?beams={beams}") as response:
            events = list(response.iter_lines())

        progress_count = sum(1 for line in events if "progress" in line)
        assert progress_count >= 2, f"Expected at least 2 progress events, got {progress_count}"


class TestJobStatus:
    """Test job status endpoint."""

    def test_get_job_status_not_found(self):
        """Test getting status of non-existent job."""
        client = TestClient(app)
        response = client.get("/stream/job/nonexistent123")

        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"] == "Job not found"

    def test_get_job_status_after_batch(self):
        """Test getting job status after running a batch."""
        client = TestClient(app)
        beams = json.dumps([{"width": 300, "depth": 500, "moment": 100, "fck": 25, "fy": 500}])

        # First run batch to get job_id from start event
        job_id = None
        with client.stream("GET", f"/stream/batch-design?beams={beams}") as response:
            for line in response.iter_lines():
                if "start" in line:
                    # Next line should have the data
                    continue
                if line.startswith("data:"):
                    try:
                        data = json.loads(line[5:].strip())
                        if "job_id" in data:
                            job_id = data["job_id"]
                            break
                    except json.JSONDecodeError:
                        continue

        if job_id:
            # Now check job status
            response = client.get(f"/stream/job/{job_id}")
            assert response.status_code == 200
            status = response.json()
            assert status["job_id"] == job_id
            assert status["status"] == "complete"
