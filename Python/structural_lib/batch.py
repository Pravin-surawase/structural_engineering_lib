# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Batch Design Module — Synchronous and Streaming Batch Design Functions.

This module provides high-level batch design functions that wrap the
beam pipeline for common use cases. It supports both synchronous
batch processing and async streaming for real-time UI updates.

Key Functions:
    - design_beams(): Synchronous batch design returning all results at once
    - design_beams_iter(): Async generator yielding results as they complete

Architecture:
    This module is UI-agnostic and provides canonical functions for:
    - FastAPI SSE/WebSocket streaming endpoints
    - React real-time progress updates
    - CLI batch processing
    - Streamlit batch workflows

Example:
    >>> from structural_lib.batch import design_beams, design_beams_iter
    >>>
    >>> # Synchronous batch
    >>> result = design_beams(batch_input, include_detailing=True)
    >>> print(f"Pass rate: {result.pass_rate:.1f}%")
    >>>
    >>> # Async streaming
    >>> async for beam_result in design_beams_iter(batch_input):
    ...     print(f"Designed {beam_result.beam_id}: {beam_result.status}")

Author: Session 46 Agent
Task: TASK-V3-FOUNDATION
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncGenerator, Sequence
from dataclasses import dataclass, field
from typing import Any

from .api import design_beam_is456
from .beam_pipeline import design_multiple_beams as _design_multiple_beams
from .models import (
    BeamBatchInput,
    BeamBatchResult,
    BeamDesignResult,
    BeamForces,
    BeamGeometry,
    DesignDefaults,
    DesignStatus,
)

__all__ = [
    # Core functions
    "design_beams",
    "design_beams_iter",
    # Result types
    "BatchProgress",
    "DesignEvent",
]


# =============================================================================
# Progress Tracking
# =============================================================================


@dataclass
class BatchProgress:
    """Progress tracking for batch design operations.

    Attributes:
        total: Total number of beams to design
        completed: Number of beams completed (success or failure)
        passed: Number of beams that passed design checks
        failed: Number of beams that failed design checks
        current_beam_id: ID of beam currently being designed
        elapsed_seconds: Time elapsed since batch start
        estimated_remaining_seconds: Estimated time remaining
    """

    total: int = 0
    completed: int = 0
    passed: int = 0
    failed: int = 0
    current_beam_id: str | None = None
    elapsed_seconds: float = 0.0
    estimated_remaining_seconds: float | None = None

    @property
    def progress_percent(self) -> float:
        """Return completion percentage (0-100)."""
        if self.total == 0:
            return 0.0
        return (self.completed / self.total) * 100

    @property
    def pass_rate(self) -> float:
        """Return pass rate percentage (0-100)."""
        if self.completed == 0:
            return 0.0
        return (self.passed / self.completed) * 100

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "total": self.total,
            "completed": self.completed,
            "passed": self.passed,
            "failed": self.failed,
            "current_beam_id": self.current_beam_id,
            "progress_percent": self.progress_percent,
            "pass_rate": self.pass_rate,
            "elapsed_seconds": self.elapsed_seconds,
            "estimated_remaining_seconds": self.estimated_remaining_seconds,
        }


@dataclass
class DesignEvent:
    """Event emitted during batch design streaming.

    Attributes:
        event_type: Type of event ("start", "progress", "result", "complete", "error")
        beam_id: Beam ID (for result/error events)
        result: Design result (for result events)
        progress: Current progress (for progress events)
        error: Error message (for error events)
        message: Human-readable message
    """

    event_type: str
    beam_id: str | None = None
    result: BeamDesignResult | None = None
    progress: BatchProgress | None = None
    error: str | None = None
    message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for SSE/WebSocket serialization."""
        data: dict[str, Any] = {"event": self.event_type}

        if self.beam_id:
            data["beam_id"] = self.beam_id
        if self.message:
            data["message"] = self.message
        if self.error:
            data["error"] = self.error
        if self.progress:
            data["progress"] = self.progress.to_dict()
        if self.result:
            data["result"] = {
                "beam_id": self.result.beam_id,
                "status": self.result.status.value,
                "ast_required": getattr(self.result, "ast_required", 0),
                "stirrup_spacing": getattr(self.result, "stirrup_spacing", 0),
            }

        return data


# =============================================================================
# Helper Functions
# =============================================================================


def _beam_to_params(
    geom: BeamGeometry,
    forces: BeamForces,
    defaults: DesignDefaults,
) -> dict[str, Any]:
    """Convert BeamGeometry + BeamForces to design parameters dict.

    Args:
        geom: Beam geometry model
        forces: Beam forces model
        defaults: Default design parameters

    Returns:
        Dictionary of parameters for design_beam_is456()
    """
    # Calculate effective depth
    cover = getattr(geom.section, "cover_mm", defaults.cover_mm)
    d_mm = geom.section.depth_mm - cover - (defaults.min_bar_dia_mm / 2)

    return {
        "beam_id": geom.id,
        "story": geom.story or "STORY",
        "b_mm": geom.section.width_mm,
        "D_mm": geom.section.depth_mm,
        "d_mm": d_mm,
        "span_mm": geom.length_mm,
        "cover_mm": cover,
        "fck_nmm2": getattr(geom.section, "fck_mpa", None) or defaults.fck_mpa,
        "fy_nmm2": getattr(geom.section, "fy_mpa", None) or defaults.fy_mpa,
        "mu_knm": forces.mu_knm,
        "vu_kn": forces.vu_kn,
        "case_id": forces.case_id or "CASE-1",
        "d_dash_mm": 50.0,
        "asv_mm2": 100.0,
    }


def _design_single(params: dict[str, Any]) -> BeamDesignResult:
    """Design a single beam and convert to BeamDesignResult.

    Args:
        params: Design parameters dictionary

    Returns:
        BeamDesignResult with design outcome
    """
    try:
        result = design_beam_is456(
            units="IS456",
            case_id=params["case_id"],
            mu_knm=params["mu_knm"],
            vu_kn=params["vu_kn"],
            b_mm=params["b_mm"],
            D_mm=params["D_mm"],
            d_mm=params["d_mm"],
            fck_nmm2=params["fck_nmm2"],
            fy_nmm2=params["fy_nmm2"],
            d_dash_mm=params.get("d_dash_mm", 50.0),
            asv_mm2=params.get("asv_mm2", 100.0),
        )

        # Determine status
        is_safe = result.flexure.is_safe
        if result.shear:
            is_safe = is_safe and result.shear.is_safe

        status = DesignStatus.PASS if is_safe else DesignStatus.FAIL

        return BeamDesignResult(
            beam_id=params["beam_id"],
            story=params.get("story", "STORY"),
            status=status,
            ast_required=result.flexure.ast_required,
            asc_required=result.flexure.asc_required or 0.0,
            stirrup_spacing=result.shear.spacing if result.shear else 0.0,
            mu_capacity=result.flexure.mu_capacity,
            vu_capacity=result.shear.vu_capacity if result.shear else 0.0,
        )

    except Exception as e:
        return BeamDesignResult(
            beam_id=params["beam_id"],
            story=params.get("story", "STORY"),
            status=DesignStatus.FAIL,
            error_message=str(e),
        )


# =============================================================================
# Core Batch Design Functions
# =============================================================================


def design_beams(
    data: BeamBatchInput | Sequence[tuple[BeamGeometry, BeamForces]],
    *,
    defaults: DesignDefaults | None = None,
    include_detailing: bool = False,
) -> BeamBatchResult:
    """Synchronous batch design of multiple beams.

    Designs all beams and returns a complete result with statistics.
    For streaming results, use design_beams_iter() instead.

    Args:
        data: BeamBatchInput or list of (geometry, forces) tuples
        defaults: Default design parameters (used if not in data)
        include_detailing: Generate detailing output for each beam

    Returns:
        BeamBatchResult with all results and summary statistics

    Example:
        >>> from structural_lib.batch import design_beams
        >>> from structural_lib.models import BeamBatchInput
        >>>
        >>> batch_input = BeamBatchInput(beams=beams, forces=forces)
        >>> result = design_beams(batch_input)
        >>> print(f"Designed {result.total_beams} beams")
        >>> print(f"Pass rate: {result.pass_rate:.1f}%")
    """
    # Extract geometry/forces pairs
    if isinstance(data, BeamBatchInput):
        defaults = defaults or data.defaults
        pairs = data.get_merged_data()
    else:
        pairs = list(data)
        defaults = defaults or DesignDefaults()

    # Design each beam
    results: list[BeamDesignResult] = []
    for geom, forces in pairs:
        params = _beam_to_params(geom, forces, defaults)
        result = _design_single(params)
        results.append(result)

    # Build result
    return BeamBatchResult.from_results(
        results=results,
        metadata={
            "include_detailing": include_detailing,
            "design_code": "IS456",
        },
    )


async def design_beams_iter(
    data: BeamBatchInput | Sequence[tuple[BeamGeometry, BeamForces]],
    *,
    defaults: DesignDefaults | None = None,
    include_detailing: bool = False,
    yield_progress: bool = True,
    progress_interval: int = 1,
) -> AsyncGenerator[DesignEvent, None]:
    """Async generator that yields design results as they complete.

    This function is designed for streaming to React via SSE or WebSocket.
    It yields events for:
    - Start of batch (total count)
    - Progress updates (configurable interval)
    - Individual design results
    - Completion with summary

    Args:
        data: BeamBatchInput or list of (geometry, forces) tuples
        defaults: Default design parameters
        include_detailing: Generate detailing for each beam
        yield_progress: Emit progress events (default True)
        progress_interval: Emit progress every N beams (default 1)

    Yields:
        DesignEvent with result or progress information

    Example:
        >>> async for event in design_beams_iter(batch_input):
        ...     if event.event_type == "result":
        ...         print(f"Beam {event.beam_id}: {event.result.status}")
        ...     elif event.event_type == "progress":
        ...         print(f"Progress: {event.progress.progress_percent:.0f}%")
    """
    # Extract geometry/forces pairs
    if isinstance(data, BeamBatchInput):
        defaults = defaults or data.defaults
        pairs = data.get_merged_data()
    else:
        pairs = list(data)
        defaults = defaults or DesignDefaults()

    total = len(pairs)
    start_time = time.time()

    # Initialize progress
    progress = BatchProgress(total=total)

    # Emit start event
    yield DesignEvent(
        event_type="start",
        message=f"Starting batch design of {total} beams",
        progress=progress,
    )

    # Design each beam
    results: list[BeamDesignResult] = []

    for i, (geom, forces) in enumerate(pairs):
        progress.current_beam_id = geom.id

        # Design beam (in a thread to avoid blocking)
        params = _beam_to_params(geom, forces, defaults)

        # Run design in executor to avoid blocking event loop
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, _design_single, params)

        results.append(result)

        # Update progress
        progress.completed = i + 1
        if result.status == DesignStatus.PASS:
            progress.passed += 1
        else:
            progress.failed += 1

        progress.elapsed_seconds = time.time() - start_time

        # Estimate remaining time
        if progress.completed > 0:
            avg_time = progress.elapsed_seconds / progress.completed
            remaining = total - progress.completed
            progress.estimated_remaining_seconds = avg_time * remaining

        # Emit result event
        yield DesignEvent(
            event_type="result",
            beam_id=geom.id,
            result=result,
            progress=progress,
            message=f"Designed beam {geom.id}: {result.status.value}",
        )

        # Emit progress event if configured
        if yield_progress and (i + 1) % progress_interval == 0:
            yield DesignEvent(
                event_type="progress",
                progress=progress,
                message=f"Progress: {progress.progress_percent:.0f}%",
            )

        # Yield control to event loop
        await asyncio.sleep(0)

    # Emit completion event
    final_result = BeamBatchResult.from_results(results)
    progress.current_beam_id = None

    yield DesignEvent(
        event_type="complete",
        progress=progress,
        message=(
            f"Batch complete: {progress.passed}/{progress.total} passed "
            f"({progress.pass_rate:.1f}% pass rate)"
        ),
    )
