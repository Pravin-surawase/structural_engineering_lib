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

# Import structural_lib API with proper signature discovery
# See: scripts/discover_api_signatures.py design_beam_is456
from structural_lib import api
from fastapi_app.auth import verify_ws_token

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
        logger.info(f"Client connected: {session_id} (total: {len(self.active_connections)})")

    def disconnect(self, session_id: str) -> None:
        """Remove a disconnected client."""
        self.active_connections.pop(session_id, None)
        logger.info(f"Client disconnected: {session_id} (total: {len(self.active_connections)})")

    async def send_json(self, session_id: str, data: dict[str, Any]) -> None:
        """Send JSON data to a specific session."""
        if websocket := self.active_connections.get(session_id):
            await websocket.send_json(data)

    async def broadcast(self, data: dict[str, Any]) -> None:
        """Broadcast message to all connected clients."""
        for websocket in self.active_connections.values():
            try:
                await websocket.send_json(data)
            except Exception:
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
                    await manager.send_json(session_id, {
                        "type": "pong",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })

                else:
                    await manager.send_json(session_id, {
                        "type": "error",
                        "message": f"Unknown message type: {message_type}"
                    })

            except Exception as e:
                logger.exception(f"Error handling message type {message_type}")
                await manager.send_json(session_id, {
                    "type": "error",
                    "message": str(e)
                })

    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.exception(f"WebSocket error for session {session_id}")
        manager.disconnect(session_id)


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

    # Map user-friendly params to library params
    # User sends: width, depth, moment, fck, fy
    # Library needs: b_mm, D_mm, d_mm, mu_knm, vu_kn, fck_nmm2, fy_nmm2

    width = params.get("width", 300)
    depth = params.get("depth", 500)
    moment = params.get("moment", 100)
    shear = params.get("shear", 50)
    fck = params.get("fck", 25)
    fy = params.get("fy", 500)
    cover = params.get("cover", 40)

    # Calculate effective depth
    d_mm = depth - cover - 8  # Assuming 8mm stirrup + half bar

    # Run design calculation in thread pool (non-blocking)
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

    # Calculate response time
    end_time = datetime.now(timezone.utc)
    latency_ms = (end_time - start_time).total_seconds() * 1000

    # Send result with structure matching ComplianceCaseResult
    await manager.send_json(session_id, {
        "type": "design_result",
        "latency_ms": round(latency_ms, 2),
        "data": {
            "flexure": {
                "ast_required": result.flexure.ast_required,
                "mu_lim": result.flexure.mu_lim,
                "xu": result.flexure.xu,
                "xu_max": result.flexure.xu_max,
                "is_safe": result.flexure.is_safe,
            },
            "shear": {
                "tv": result.shear.tv if result.shear else None,
                "tc": result.shear.tc if result.shear else None,
                "spacing": result.shear.spacing if result.shear else None,
                "is_safe": result.shear.is_safe if result.shear else None,
            },
        }
    })


async def handle_check_beam(session_id: str, params: dict[str, Any]) -> None:
    """
    Handle check_beam message for compliance check.

    Uses structural_lib.api.check_beam_is456 with correct signature.
    Discovered via: scripts/discover_api_signatures.py check_beam_is456
    """
    start_time = datetime.now(timezone.utc)

    width = params.get("width", 300)
    depth = params.get("depth", 500)
    fck = params.get("fck", 25)
    fy = params.get("fy", 500)
    cover = params.get("cover", 40)
    cases = params.get("cases", [])

    if not cases:
        await manager.send_json(session_id, {
            "type": "error",
            "message": "No load cases provided"
        })
        return

    d_mm = depth - cover - 8

    # Run check in thread pool
    result = await asyncio.to_thread(
        api.check_beam_is456,
        units="IS456",
        cases=cases,
        b_mm=float(width),
        D_mm=float(depth),
        d_mm=float(d_mm),
        fck_nmm2=float(fck),
        fy_nmm2=float(fy),
    )

    end_time = datetime.now(timezone.utc)
    latency_ms = (end_time - start_time).total_seconds() * 1000

    await manager.send_json(session_id, {
        "type": "check_result",
        "latency_ms": round(latency_ms, 2),
        "data": {
            "is_ok": result.is_ok,
            "governing_case_id": result.governing_case_id,
            "governing_utilization": result.governing_utilization,
            "summary": result.summary,
            "num_cases": len(result.cases),
        }
    })
