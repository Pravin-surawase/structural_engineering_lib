"""
Server-Sent Events (SSE) Router for Batch Processing.

This module provides SSE endpoints for streaming batch operations:
- /stream/batch-design - Stream design results for multiple beams
- /stream/progress/{job_id} - Stream job progress updates

Week 3 Priority 3 Implementation (V3 Migration)

Usage:
    POST /stream/batch-design with a JSON array body
    Returns: Event stream with design_result, progress, complete events

Client Example:
    const eventSource = new EventSource('/stream/batch-design?...');
    eventSource.onmessage = (event) => console.log(JSON.parse(event.data));
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Mapping

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from structural_lib.services import batch
from fastapi_app.auth import check_rate_limit
from fastapi_app.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stream", tags=["streaming"])


class BatchJobProgress(BaseModel):
    """Completed and total item counts for one batch job."""

    completed: int
    total: int
    passed: int
    failed: int
    held: int
    blocked: int
    percent: float


class BatchJobStatusResponse(BaseModel):
    """Typed polling response for one streamed batch job."""

    job_id: str
    status: str
    progress: BatchJobProgress
    started_at: str
    completed_at: str | None
    error_count: int
    is_safe: bool | None
    overall_status: str


def _job_engineering_status(job: Mapping[str, Any]) -> dict[str, bool | None | str]:
    """Return a verdict only after every batch item has been evaluated."""
    if job["completed"] < job["total"]:
        return {"is_safe": None, "overall_status": "IN_PROGRESS"}

    if job["blocked"]:
        return {"is_safe": False, "overall_status": "BLOCKED"}
    if job["held"]:
        return {"is_safe": False, "overall_status": "HOLD"}
    is_safe = job["failed"] == 0
    return {
        "is_safe": is_safe,
        "overall_status": "PASS" if is_safe else "FAIL",
    }


# =============================================================================
# Job Tracking (In-Memory for Demo)
# =============================================================================


class BatchJobManager:
    """
    Manages batch job state for progress tracking.

    In production, use Redis or database for persistence.
    """

    def __init__(self) -> None:
        self.jobs: dict[str, dict[str, Any]] = {}

    def create_job(self, total_items: int) -> str:
        """Create a new batch job and return its ID."""
        job_id = str(uuid.uuid4())[:8]
        self.jobs[job_id] = {
            "id": job_id,
            "status": "running",
            "total": total_items,
            "completed": 0,
            "passed": 0,
            "failed": 0,
            "held": 0,
            "blocked": 0,
            "results": [],
            "errors": [],
            "started_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": None,
        }
        return job_id

    def update_progress(
        self,
        job_id: str,
        design_succeeded: bool,
        result: dict | None = None,
        error: str | None = None,
    ) -> None:
        """Update job progress."""
        if job_id not in self.jobs:
            return

        job = self.jobs[job_id]
        job["completed"] += 1

        if result:
            job["results"].append(result)
            overall_status = result.get("overall_status")
            if overall_status == "PASS":
                job["passed"] += 1
            elif overall_status == "FAIL":
                job["failed"] += 1
            else:
                job["held"] += 1
                if overall_status == "BLOCKED":
                    job["blocked"] += 1
        elif error:
            job["failed"] += 1
            job["errors"].append(error)

        if job["completed"] >= job["total"]:
            job["status"] = "complete"
            job["completed_at"] = datetime.now(timezone.utc).isoformat()

    def get_job(self, job_id: str) -> dict | None:
        """Get job status."""
        return self.jobs.get(job_id)

    def cleanup_old_jobs(self, max_age_seconds: int = 3600) -> None:
        """Remove jobs older than max_age_seconds."""
        now = datetime.now(timezone.utc)
        to_remove = []
        for job_id, job in self.jobs.items():
            if job.get("completed_at"):
                completed = datetime.fromisoformat(
                    job["completed_at"].replace("Z", "+00:00")
                )
                if (now - completed).total_seconds() > max_age_seconds:
                    to_remove.append(job_id)
        for job_id in to_remove:
            del self.jobs[job_id]


# Global job manager
job_manager = BatchJobManager()


# =============================================================================
# SSE Endpoints
# =============================================================================


def _stream_batch_response(
    request: Request,
    beam_list: list[Any],
) -> EventSourceResponse:
    """Build one SSE response after the transport has decoded the beam list."""
    if not isinstance(beam_list, list) or len(beam_list) == 0:

        async def error_generator():
            yield {
                "event": "error",
                "data": json.dumps({"message": "beams must be a non-empty array"}),
            }

        return EventSourceResponse(error_generator())

    settings = get_settings()
    if len(beam_list) > settings.max_batch_size:

        async def error_response():
            yield {
                "event": "error",
                "data": json.dumps(
                    {
                        "error": f"Batch size {len(beam_list)} exceeds maximum of {settings.max_batch_size}"
                    }
                ),
            }

        return EventSourceResponse(error_response())

    async def event_generator() -> AsyncGenerator[dict, None]:
        """Generate SSE events for batch design."""
        job_id = job_manager.create_job(len(beam_list))

        # Send start event
        yield {
            "event": "start",
            "data": json.dumps(
                {
                    "job_id": job_id,
                    "total": len(beam_list),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ),
        }

        for member in batch.design_project_beams_iter_v1(beam_list, units="IS456"):
            # Check if client disconnected
            if await request.is_disconnected():
                logger.info(f"Client disconnected during batch job {job_id}")
                break

            result_data = member.to_dict()
            result_data["beam_id"] = member.member_id
            result_data["design_succeeded"] = (
                member.calculation_status.value == "COMPLETED"
            )
            result_data["is_safe"] = member.overall_status.value == "PASS"
            result_data["status"] = member.overall_status.value
            if member.calculation is not None:
                result_data.update(member.calculation)
            job_manager.update_progress(
                job_id,
                design_succeeded=result_data["design_succeeded"],
                result=result_data,
            )
            yield {"event": "design_result", "data": json.dumps(result_data)}

            # Send progress update
            job = job_manager.get_job(job_id)
            if job is not None:
                engineering_status = _job_engineering_status(job)
                yield {
                    "event": "progress",
                    "data": json.dumps(
                        {
                            "completed": job["completed"],
                            "total": job["total"],
                            "passed": job["passed"],
                            "failed": job["failed"],
                            "held": job["held"],
                            "blocked": job["blocked"],
                            **engineering_status,
                            "percent": round(job["completed"] / job["total"] * 100, 1),
                        }
                    ),
                }

            await asyncio.sleep(0)

        # Send complete event
        job = job_manager.get_job(job_id)
        if job is not None:
            engineering_status = _job_engineering_status(job)
            yield {
                "event": "complete",
                "data": json.dumps(
                    {
                        "job_id": job_id,
                        "total": job["total"],
                        "completed": job["completed"],
                        "passed": job["passed"],
                        "failed": job["failed"],
                        "held": job["held"],
                        "blocked": job["blocked"],
                        **engineering_status,
                        "duration_seconds": (
                            (
                                datetime.fromisoformat(
                                    job["completed_at"].replace("Z", "+00:00")
                                )
                                - datetime.fromisoformat(
                                    job["started_at"].replace("Z", "+00:00")
                                )
                            ).total_seconds()
                            if job.get("completed_at")
                            else None
                        ),
                    }
                ),
            }

    return EventSourceResponse(event_generator())


@router.get(
    "/batch-design",
    response_class=EventSourceResponse,
    deprecated=True,
    summary="Deprecated query-string batch stream",
    description="Compatibility transport; use POST /stream/batch-design.",
)
async def stream_batch_design(
    request: Request,
    beams: str = Query(..., description="JSON array of beam parameters"),
    _: None = Depends(check_rate_limit),
) -> EventSourceResponse:
    """Deprecated query transport delegating to the canonical project command."""
    try:
        beam_list = json.loads(beams)
    except json.JSONDecodeError:

        async def error_generator():
            yield {
                "event": "error",
                "data": json.dumps({"message": "Invalid JSON in beams parameter"}),
            }

        response = EventSourceResponse(error_generator())
        response.headers["Deprecation"] = "true"
        response.headers["Warning"] = (
            '299 - "Deprecated GET transport; use POST /stream/batch-design"'
        )
        return response

    response = _stream_batch_response(request, beam_list)
    response.headers["Deprecation"] = "true"
    response.headers["Warning"] = (
        '299 - "Deprecated GET transport; use POST /stream/batch-design"'
    )
    return response


@router.post("/batch-design", response_class=EventSourceResponse)
async def stream_batch_design_post(
    request: Request,
    beams: list[dict[str, Any]],
    _: None = Depends(check_rate_limit),
) -> EventSourceResponse:
    """Canonical project-beam stream using a POST request body."""
    return _stream_batch_response(request, beams)


@router.get("/job/{job_id}", response_model=BatchJobStatusResponse)
async def get_job_status(
    job_id: str = Path(..., pattern=r"^[a-f0-9]{8}$", description="Batch job ID"),
    _: None = Depends(check_rate_limit),
) -> dict:
    """
    Get status of a batch job.

    Returns job progress, results count, and any errors.
    """
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    engineering_status = _job_engineering_status(job)

    return {
        "job_id": job["id"],
        "status": job["status"],
        "progress": {
            "completed": job["completed"],
            "total": job["total"],
            "passed": job["passed"],
            "failed": job["failed"],
            "held": job["held"],
            "blocked": job["blocked"],
            "percent": (
                round(job["completed"] / job["total"] * 100, 1)
                if job["total"] > 0
                else 0
            ),
        },
        "started_at": job["started_at"],
        "completed_at": job["completed_at"],
        "error_count": len(job["errors"]),
        **engineering_status,
    }
