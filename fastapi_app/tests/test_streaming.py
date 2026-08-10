"""
Tests for SSE Streaming Endpoint.

Week 3 Priority 3: SSE for batch processing tests.
"""

import json

from fastapi.testclient import TestClient
from fastapi_app.main import app
from fastapi_app.routers.streaming import job_manager


class TestSSEBatchDesign:
    """Test SSE batch design endpoint."""

    @staticmethod
    def _event_data(events: list[str], event_name: str) -> list[dict]:
        """Return decoded data records for a named SSE event."""
        records: list[dict] = []
        current_event: str | None = None
        for line in events:
            if line.startswith("event:"):
                current_event = line.split(":", 1)[1].strip()
            elif line.startswith("data:") and current_event == event_name:
                records.append(json.loads(line[5:].strip()))
        return records

    def test_batch_design_single_beam(self):
        """Test batch design with single beam."""
        client = TestClient(app)
        beams = json.dumps(
            [{"width": 300, "depth": 500, "moment": 100, "fck": 25, "fy": 500}]
        )

        with client.stream(
            "GET", "/stream/batch-design", params={"beams": beams}
        ) as response:
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

    def test_batch_design_stream_preserves_unsafe_shear_failure(self):
        """A completed calculation with unsafe shear must stream as FAIL."""
        client = TestClient(app)
        beams = json.dumps(
            [
                {
                    "id": "B-UNSAFE-SHEAR",
                    "width": 300,
                    "depth": 500,
                    "moment": 100,
                    "shear": 600,
                    "fck": 25,
                    "fy": 500,
                    "cover": 40,
                }
            ]
        )

        with client.stream(
            "GET", "/stream/batch-design", params={"beams": beams}
        ) as response:
            events = list(response.iter_lines())

        result = self._event_data(events, "design_result")[0]
        progress = self._event_data(events, "progress")[0]
        complete = self._event_data(events, "complete")[0]
        assert result["design_succeeded"] is True
        assert result["is_safe"] is False
        assert result["status"] == "FAIL"
        assert result["evidence"]["status"] == "FAIL"
        assert result["evidence"]["support_status"] == "SUPPORTED"
        assert result["evidence"]["calculation_identity"]
        assert result["shear"]["is_safe"] is False
        for field in ("tau_v", "tau_c", "tau_c_max", "stirrup_spacing"):
            assert result["shear"][field] is not None
        assert progress["failed"] == 1
        assert complete["failed"] == 1
        assert complete["overall_status"] == "FAIL"

    def test_batch_design_multiple_beams(self):
        """Test batch design with multiple beams."""
        client = TestClient(app)
        beams = json.dumps(
            [
                {
                    "id": "B1",
                    "width": 300,
                    "depth": 500,
                    "moment": 100,
                    "fck": 25,
                    "fy": 500,
                },
                {
                    "id": "B2",
                    "width": 350,
                    "depth": 600,
                    "moment": 200,
                    "fck": 30,
                    "fy": 500,
                },
                {
                    "id": "B3",
                    "width": 400,
                    "depth": 700,
                    "moment": 300,
                    "fck": 25,
                    "fy": 500,
                },
            ]
        )

        with client.stream(
            "GET", "/stream/batch-design", params={"beams": beams}
        ) as response:
            events = list(response.iter_lines())

        # Count design_result events
        result_count = sum(1 for line in events if "design_result" in line)
        assert (
            result_count >= 3
        ), f"Expected at least 3 design_result events, got {result_count}"

    def test_batch_design_post_accepts_maintained_sample_size(self):
        """Large browser batches use a body so the request target stays bounded."""
        client = TestClient(app)
        beams = [
            {
                "beam_id": f"B{index}",
                "width": 300,
                "depth": 500,
                "moment": 100,
                "shear": 50,
                "fck": 25,
                "fy": 500,
            }
            for index in range(153)
        ]

        with client.stream("POST", "/stream/batch-design", json=beams) as response:
            events = list(response.iter_lines())

        assert response.status_code == 200
        assert len(self._event_data(events, "design_result")) == 153
        complete = self._event_data(events, "complete")[0]
        assert complete["completed"] == 153

    def test_batch_design_invalid_json(self):
        """Test batch design with invalid JSON."""
        client = TestClient(app)

        with client.stream(
            "GET", "/stream/batch-design", params={"beams": "not_valid_json"}
        ) as response:
            events = list(response.iter_lines())

        # Should have error event
        has_error = any("error" in line for line in events)
        assert has_error, "Expected error event for invalid JSON"

    def test_batch_design_empty_array(self):
        """Test batch design with empty array."""
        client = TestClient(app)

        with client.stream(
            "GET", "/stream/batch-design", params={"beams": "[]"}
        ) as response:
            events = list(response.iter_lines())

        has_error = any("error" in line for line in events)
        assert has_error, "Expected error event for empty array"

    def test_batch_design_progress_tracking(self):
        """Test that progress events are sent."""
        client = TestClient(app)
        beams = json.dumps(
            [
                {"width": 300, "depth": 500, "moment": 100, "fck": 25, "fy": 500},
                {"width": 300, "depth": 500, "moment": 150, "fck": 25, "fy": 500},
            ]
        )

        with client.stream(
            "GET", "/stream/batch-design", params={"beams": beams}
        ) as response:
            events = list(response.iter_lines())

        progress_count = sum(1 for line in events if "progress" in line)
        assert (
            progress_count >= 2
        ), f"Expected at least 2 progress events, got {progress_count}"
        progress_events = self._event_data(events, "progress")
        assert progress_events[0]["is_safe"] is None
        assert progress_events[0]["overall_status"] == "IN_PROGRESS"
        assert progress_events[-1]["is_safe"] is True
        assert progress_events[-1]["overall_status"] == "PASS"


class TestJobStatus:
    """Test job status endpoint."""

    def test_get_job_status_not_found(self):
        """Test getting status of non-existent job."""
        client = TestClient(app)
        response = client.get("/stream/job/abcd1234")

        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Job not found"

    def test_get_job_status_is_in_progress_until_every_item_completes(self):
        """A partial batch must not report a provisional engineering PASS."""
        client = TestClient(app)
        job_id = job_manager.create_job(total_items=2)
        job_manager.update_progress(
            job_id,
            design_succeeded=True,
            result={"is_safe": True},
        )

        response = client.get(f"/stream/job/{job_id}")

        assert response.status_code == 200
        status = response.json()
        assert status["status"] == "running"
        assert status["progress"]["completed"] == 1
        assert status["is_safe"] is None
        assert status["overall_status"] == "IN_PROGRESS"

    def test_get_job_status_after_batch(self):
        """Test getting job status after running a batch."""
        client = TestClient(app)
        beams = json.dumps(
            [{"width": 300, "depth": 500, "moment": 100, "fck": 25, "fy": 500}]
        )

        # First run batch to get job_id from start event
        job_id = None
        with client.stream(
            "GET", "/stream/batch-design", params={"beams": beams}
        ) as response:
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
            assert status["is_safe"] is True
            assert status["overall_status"] == "PASS"
