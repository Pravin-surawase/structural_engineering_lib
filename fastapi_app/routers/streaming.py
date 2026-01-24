"""
Server-Sent Events (SSE) Router for Batch Processing.

This module provides SSE endpoints for streaming batch operations:
- /stream/batch-design - Stream design results for multiple beams
- /stream/progress/{job_id} - Stream job progress updates

Week 3 Priority 3 Implementation (V3 Migration)

Usage:
    GET /stream/batch-design?beams=[{...}]
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
from typing import Any, AsyncGenerator

from fastapi import APIRouter, Depends, Query, Request
from sse_starlette.sse import EventSourceResponse

# Import structural_lib API with proper signature discovery
from structural_lib import api
from fastapi_app.auth import check_rate_limit

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stream", tags=["streaming"])


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
            "failed": 0,
            "results": [],
            "errors": [],
            "started_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": None,
        }
        return job_id

    def update_progress(self, job_id: str, success: bool, result: dict | None = None, error: str | None = None) -> None:
        """Update job progress."""
        if job_id not in self.jobs:
            return

        job = self.jobs[job_id]
        job["completed"] += 1

        if success and result:
            job["results"].append(result)
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
                completed = datetime.fromisoformat(job["completed_at"].replace("Z", "+00:00"))
                if (now - completed).total_seconds() > max_age_seconds:
                    to_remove.append(job_id)
        for job_id in to_remove:
            del self.jobs[job_id]


# Global job manager
job_manager = BatchJobManager()


# =============================================================================
# SSE Endpoints
# =============================================================================


@router.get("/batch-design")
async def stream_batch_design(
    request: Request,
    beams: str = Query(..., description="JSON array of beam parameters"),
    _: None = Depends(check_rate_limit),
) -> EventSourceResponse:
    """
    Stream batch beam design results.

    Accepts JSON array of beam parameters and streams results as they complete.

    Events:
        - start: Job started with job_id and total count
        - progress: Current progress (completed/total)
        - design_result: Individual beam result
        - error: Individual beam error
        - complete: All beams processed

    Example:
        ```javascript
        const beams = JSON.stringify([
            {width: 300, depth: 500, moment: 100, fck: 25, fy: 500},
            {width: 300, depth: 500, moment: 150, fck: 25, fy: 500}
        ]);
        const es = new EventSource(`/stream/batch-design?beams=${encodeURIComponent(beams)}`);

        es.addEventListener('design_result', (e) => {
            const result = JSON.parse(e.data);
            console.log('Beam completed:', result);
        });

        es.addEventListener('complete', (e) => {
            console.log('All done!');
            es.close();
        });
        ```
    """
    try:
        beam_list = json.loads(beams)
    except json.JSONDecodeError:
        async def error_generator():
            yield {"event": "error", "data": json.dumps({"message": "Invalid JSON in beams parameter"})}
        return EventSourceResponse(error_generator())

    if not isinstance(beam_list, list) or len(beam_list) == 0:
        async def error_generator():
            yield {"event": "error", "data": json.dumps({"message": "beams must be a non-empty array"})}
        return EventSourceResponse(error_generator())

    async def event_generator() -> AsyncGenerator[dict, None]:
        """Generate SSE events for batch design."""
        job_id = job_manager.create_job(len(beam_list))

        # Send start event
        yield {
            "event": "start",
            "data": json.dumps({
                "job_id": job_id,
                "total": len(beam_list),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        }

        for idx, beam_params in enumerate(beam_list):
            # Check if client disconnected
            if await request.is_disconnected():
                logger.info(f"Client disconnected during batch job {job_id}")
                break

            try:
                # Extract parameters with defaults
                width = beam_params.get("width", 300)
                depth = beam_params.get("depth", 500)
                moment = beam_params.get("moment", 100)
                shear = beam_params.get("shear", 50)
                fck = beam_params.get("fck", 25)
                fy = beam_params.get("fy", 500)
                cover = beam_params.get("cover", 40)
                beam_id = beam_params.get("id", f"beam_{idx + 1}")

                d_mm = depth - cover - 8

                # Run design in thread pool
                result = await asyncio.to_thread(
                    api.design_beam_is456,
                    units="IS456",
                    b_mm=float(width),
                    D_mm=float(depth),
                    d_mm=float(d_mm),
                    mu_knm=float(moment),
                    vu_kn=float(shear),
                    fck_nmm2=float(fck),
                    fy_nmm2=float(fy),
                )

                result_data = {
                    "beam_id": beam_id,
                    "index": idx,
                    "input": beam_params,
                    "flexure": {
                        "ast_required": result.flexure.ast_required,
                        "mu_lim": result.flexure.mu_lim,
                        "xu": result.flexure.xu,
                        "is_safe": result.flexure.is_safe,
                    },
                    "shear": {
                        "tv": result.shear.tv if result.shear else None,
                        "tc": result.shear.tc if result.shear else None,
                        "is_safe": result.shear.is_safe if result.shear else None,
                    } if result.shear else None,
                    "status": "PASS" if result.flexure.is_safe else "FAIL",
                }

                job_manager.update_progress(job_id, success=True, result=result_data)

                yield {
                    "event": "design_result",
                    "data": json.dumps(result_data)
                }

            except Exception as e:
                logger.exception(f"Error designing beam {idx}")
                error_msg = str(e)
                job_manager.update_progress(job_id, success=False, error=error_msg)

                yield {
                    "event": "error",
                    "data": json.dumps({
                        "beam_id": beam_params.get("id", f"beam_{idx + 1}"),
                        "index": idx,
                        "message": error_msg
                    })
                }

            # Send progress update
            job = job_manager.get_job(job_id)
            yield {
                "event": "progress",
                "data": json.dumps({
                    "completed": job["completed"],
                    "total": job["total"],
                    "failed": job["failed"],
                    "percent": round(job["completed"] / job["total"] * 100, 1)
                })
            }

        # Send complete event
        job = job_manager.get_job(job_id)
        yield {
            "event": "complete",
            "data": json.dumps({
                "job_id": job_id,
                "total": job["total"],
                "completed": job["completed"],
                "failed": job["failed"],
                "duration_seconds": (
                    datetime.fromisoformat(job["completed_at"].replace("Z", "+00:00")) -
                    datetime.fromisoformat(job["started_at"].replace("Z", "+00:00"))
                ).total_seconds() if job.get("completed_at") else None
            })
        }

    return EventSourceResponse(event_generator())


@router.get("/job/{job_id}")
async def get_job_status(
    job_id: str,
    _: None = Depends(check_rate_limit),
) -> dict:
    """
    Get status of a batch job.

    Returns job progress, results count, and any errors.
    """
    job = job_manager.get_job(job_id)
    if not job:
        return {"error": "Job not found", "job_id": job_id}

    return {
        "job_id": job["id"],
        "status": job["status"],
        "progress": {
            "completed": job["completed"],
            "total": job["total"],
            "failed": job["failed"],
            "percent": round(job["completed"] / job["total"] * 100, 1) if job["total"] > 0 else 0,
        },
        "started_at": job["started_at"],
        "completed_at": job["completed_at"],
        "error_count": len(job["errors"]),
    }
