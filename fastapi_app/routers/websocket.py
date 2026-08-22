"""
WebSocket Router for Live Design Updates.

This module provides WebSocket endpoints for real-time beam design:
- /ws/design/{session_id} - Live interactive design
- Supports bi-directional communication for instant feedback

Week 3 Priority 2 Implementation (V3 Migration)

Usage:
    Connect to ws://localhost:8000/ws/design/{session_id}
    Send: {"type": "design_beam", "params": {...}}
    Receive: {"type": "design_result", "data": {...}}
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field, ValidationError

# Import structural_lib API with proper signature discovery
# See: scripts/discover_api_signatures.py design_beam_is456
from structural_lib import api
from fastapi_app.auth import verify_ws_token
from fastapi_app.error_utils import sanitize_error

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


# =============================================================================
# Connection Manager
# =============================================================================


class DesignConnectionManager:
    """
    Manages WebSocket connections for live design updates.

    Features:
    - Track active connections by session ID
    - Handle connect/disconnect lifecycle
    - Broadcast messages to all connected clients
    """

    def __init__(self) -> None:
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket) -> None:
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(
            f"Client connected: {session_id} (total: {len(self.active_connections)})"
        )

    def disconnect(self, session_id: str) -> None:
        """Remove a disconnected client."""
        self.active_connections.pop(session_id, None)
        logger.info(
            f"Client disconnected: {session_id} (total: {len(self.active_connections)})"
        )

    async def send_json(self, session_id: str, data: dict[str, Any]) -> None:
        """Send JSON data to a specific session."""
        if websocket := self.active_connections.get(session_id):
            await websocket.send_json(data)

    async def broadcast(self, data: dict[str, Any]) -> None:
        """Broadcast message to all connected clients."""
        for websocket in self.active_connections.values():
            try:
                await websocket.send_json(data)
            except (RuntimeError, ConnectionError, OSError):
                pass  # Client may have disconnected


# Global connection manager instance
manager = DesignConnectionManager()


# =============================================================================
# WebSocket Endpoint
# =============================================================================


@router.websocket("/ws/design/{session_id}")
async def design_websocket(
    websocket: WebSocket,
    session_id: str,
    token: str | None = Query(None),
) -> None:
    """
    WebSocket endpoint for live beam design.

    Message Types (Client → Server):
        - design_beam: Design a single beam
        - check_beam: Check beam compliance
        - ping: Heartbeat

    Message Types (Server → Client):
        - design_result: Design calculation result
        - check_result: Compliance check result
        - pong: Heartbeat response
        - error: Error message

    Example:
        ```javascript
        const ws = new WebSocket('ws://localhost:8000/ws/design/session123');

        ws.send(JSON.stringify({
            type: 'design_beam',
            params: {
                width: 300,
                depth: 500,
                moment: 150,
                fck: 25,
                fy: 500
            }
        }));
        ```
    """
    user = await verify_ws_token(websocket, token)
    if token and not user:
        return

    await manager.connect(session_id, websocket)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message_type = data.get("type", "unknown")

            try:
                if message_type == "design_beam":
                    await handle_design_beam(session_id, data.get("params", {}))

                elif message_type == "check_beam":
                    await handle_check_beam(session_id, data.get("params", {}))

                elif message_type == "ping":
                    await manager.send_json(
                        session_id,
                        {
                            "type": "pong",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        },
                    )

                else:
                    await manager.send_json(
                        session_id,
                        {
                            "type": "error",
                            "message": f"Unknown message type: {message_type}",
                        },
                    )

            except (ValueError, TypeError) as e:
                await manager.send_json(
                    session_id,
                    {"type": "error", "message": sanitize_error(e, "live design")},
                )
            except (RuntimeError, KeyError, AttributeError):
                logger.exception("WebSocket handler error for session %s", session_id)
                await manager.send_json(
                    session_id,
                    {"type": "error", "message": "Internal error processing request"},
                )

    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except (RuntimeError, ConnectionError, OSError):
        logger.exception(f"WebSocket error for session {session_id}")
        manager.disconnect(session_id)


# =============================================================================
# WebSocket Message Pydantic Models
# =============================================================================


class WSDesignParams(BaseModel):
    """Validated parameters for design_beam WebSocket messages."""

    width: float = Field(..., ge=100, le=2000, description="Beam width in mm")
    depth: float = Field(..., ge=150, le=3000, description="Overall beam depth in mm")
    moment: float = Field(..., ge=0, description="Factored moment Mu in kN·m")
    shear: float = Field(..., ge=0, description="Factored shear Vu in kN")
    fck: float = Field(..., ge=15, le=80, description="Concrete strength fck in N/mm²")
    fy: float = Field(
        ..., ge=250, le=550, description="Steel yield strength fy in N/mm²"
    )
    cover: float = Field(..., ge=20, le=75, description="Clear cover in mm")
    stirrup_dia_mm: float = Field(
        ..., ge=6, le=16, description="Stirrup diameter in mm"
    )
    main_bar_dia_mm: float = Field(
        ..., ge=8, le=36, description="Main bar diameter in mm"
    )


class WSCheckParams(BaseModel):
    """Validated parameters for check_beam WebSocket messages."""

    width: float = Field(default=300, ge=100, le=2000, description="Beam width in mm")
    depth: float = Field(
        default=500, ge=150, le=3000, description="Overall beam depth in mm"
    )
    fck: float = Field(
        default=25, ge=15, le=80, description="Concrete strength fck in N/mm²"
    )
    fy: float = Field(
        default=500, ge=250, le=600, description="Steel yield strength fy in N/mm²"
    )
    cover: float = Field(default=40, ge=20, le=75, description="Clear cover in mm")
    cases: list[dict[str, Any]] = Field(default_factory=list, description="Load cases")


# =============================================================================
# Message Handlers
# =============================================================================


async def handle_design_beam(session_id: str, params: dict[str, Any]) -> None:
    """
    Handle design_beam message.

    Uses structural_lib.api.design_beam_is456 with correct signature:
    - units: "IS456"
    - b_mm, D_mm, d_mm: dimensions in mm
    - mu_knm, vu_kn: forces
    - fck_nmm2, fy_nmm2: material properties

    Discovered via: scripts/discover_api_signatures.py design_beam_is456
    """
    start_time = datetime.now(timezone.utc)

    # Validate input with Pydantic
    try:
        validated = WSDesignParams(**params)
    except ValidationError as e:
        await manager.send_json(
            session_id,
            {"type": "error", "message": sanitize_error(e, "live design input")},
        )
        return

    # Use the same declared section inputs as the REST beam route.
    d_dash_mm = (
        validated.cover + validated.stirrup_dia_mm + validated.main_bar_dia_mm / 2
    )
    d_mm = validated.depth - d_dash_mm

    # Run design calculation in thread pool (non-blocking)
    result = await asyncio.to_thread(
        api.design_beam_is456,
        units="IS456",
        b_mm=float(validated.width),
        D_mm=float(validated.depth),
        d_mm=float(d_mm),
        mu_knm=float(validated.moment),
        vu_kn=float(validated.shear),
        fck_nmm2=float(validated.fck),
        fy_nmm2=float(validated.fy),
        d_dash_mm=float(d_dash_mm),
    )

    # Calculate response time
    end_time = datetime.now(timezone.utc)
    latency_ms = (end_time - start_time).total_seconds() * 1000

    flexure = result.flexure
    shear = result.shear
    warnings: list[str] = []
    if flexure.Asc_required > 0:
        warnings.append(
            "Doubly reinforced design required because moment demand exceeds "
            "the singly reinforced limit"
        )
    if flexure.xu > flexure.xu_max:
        warnings.append("Section is over-reinforced - consider increasing depth")

    from structural_lib.services.evidence import build_beam_evidence_envelope

    evidence = build_beam_evidence_envelope(
        inputs={
            "units": "IS456",
            "case_id": "CASE-1",
            "mu_knm": validated.moment,
            "vu_kn": validated.shear,
            "b_mm": validated.width,
            "D_mm": validated.depth,
            "d_mm": d_mm,
            "fck_nmm2": validated.fck,
            "fy_nmm2": validated.fy,
            "d_dash_mm": d_dash_mm,
            "asv_mm2": 100.0,
        },
        is_ok=result.is_ok,
        governing_utilization=result.governing_utilization,
        utilizations=result.utilizations,
    )

    # Keep the WebSocket payload aligned with the REST BeamDesignResponse.
    # The frontend can then switch transports without silently losing fields.
    await manager.send_json(
        session_id,
        {
            "type": "design_result",
            "latency_ms": round(latency_ms, 2),
            "data": {
                "success": result.is_ok,
                "message": (
                    f"Design complete: Ast = {flexure.Ast_required:.0f} mm²"
                    if result.is_ok
                    else f"Design failed: {result.remarks}"
                ),
                "flexure": {
                    "ast_required": flexure.Ast_required,
                    "ast_min": flexure.Ast_min,
                    "ast_max": flexure.Ast_max,
                    "xu": flexure.xu,
                    "xu_max": flexure.xu_max,
                    "is_under_reinforced": flexure.xu <= flexure.xu_max,
                    "moment_capacity": flexure.Mu_lim,
                    "asc_required": flexure.Asc_required,
                },
                "shear": (
                    {
                        "tau_v": shear.tau_v,
                        "tau_c": shear.tau_c,
                        "tau_c_max": shear.tau_c_max,
                        "asv_required": (
                            shear.Vus / (0.87 * validated.fy) * 1000
                            if shear.Vus > 0
                            else 0.0
                        ),
                        "stirrup_spacing": shear.spacing,
                        "sv_max": 300.0,
                        "shear_capacity": (
                            shear.tau_c * validated.width * d_mm / 1000 + shear.Vus
                            if shear.Vus > 0
                            else validated.shear
                        ),
                    }
                    if shear
                    else None
                ),
                "ast_total": flexure.Ast_required,
                "asc_total": flexure.Asc_required,
                "utilization_ratio": min(result.governing_utilization, 2.0),
                "effective_depth_used": d_mm,
                "warnings": warnings,
                "evidence": evidence,
            },
        },
    )


async def handle_check_beam(session_id: str, params: dict[str, Any]) -> None:
    """
    Handle check_beam message for compliance check.

    Uses structural_lib.api.check_beam_is456 with correct signature.
    Discovered via: scripts/discover_api_signatures.py check_beam_is456
    """
    start_time = datetime.now(timezone.utc)

    # Validate input with Pydantic
    try:
        validated = WSCheckParams(**params)
    except ValidationError as e:
        await manager.send_json(
            session_id,
            {"type": "error", "message": sanitize_error(e, "live check input")},
        )
        return

    if not validated.cases:
        await manager.send_json(
            session_id, {"type": "error", "message": "No load cases provided"}
        )
        return

    d_mm = validated.depth - validated.cover - 8

    # Run check in thread pool
    result = await asyncio.to_thread(
        api.check_beam_is456,
        units="IS456",
        cases=validated.cases,
        b_mm=float(validated.width),
        D_mm=float(validated.depth),
        d_mm=float(d_mm),
        fck_nmm2=float(validated.fck),
        fy_nmm2=float(validated.fy),
    )

    end_time = datetime.now(timezone.utc)
    latency_ms = (end_time - start_time).total_seconds() * 1000

    await manager.send_json(
        session_id,
        {
            "type": "check_result",
            "latency_ms": round(latency_ms, 2),
            "data": {
                "is_ok": result.is_ok,
                "governing_case_id": result.governing_case_id,
                "governing_utilization": result.governing_utilization,
                "summary": result.summary,
                "num_cases": len(result.cases),
            },
        },
    )
