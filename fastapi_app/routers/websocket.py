"""
WebSocket Router for Live Design Updates.

This module provides WebSocket endpoints for real-time beam design:
- /ws/design/{session_id} - Live interactive design
- Supports bi-directional communication for instant feedback

Week 3 Priority 2 Implementation (V3 Migration)

Usage:
    Connect to ws://localhost:8000/ws/design/{session_id}?token={jwt}
    Send: {"type": "design_beam", "params": {...}}
    Receive: {"type": "design_result", "data": {...}}
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Literal

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    ValidationError,
    field_validator,
    model_validator,
)
from pydantic_core import PydanticCustomError
from structural_lib.design.is456.beam import InputContractError, InputIssueV1
from structural_lib.services.contracts.common import (
    model_validate_or_error,
    parse_json_or_error,
)

# Import the owning beam services with proper signature discovery.
# See: scripts/discover_api_signatures.py design_beam_is456
from structural_lib.services.beam_api import design_beam_is456
from structural_lib.services.contracts.beam_supplied_check import (
    BeamSuppliedCheckRequestV2,
)
from structural_lib.services.supplied_beam_check import check_supplied_beam_v2
from fastapi_app.beam_projection import project_beam_design_result
from fastapi_app.auth import verify_ws_token
from fastapi_app.error_utils import sanitize_error
from fastapi_app.models.beam import BeamDesignResponse, BeamSuppliedCheckResponseV2
from fastapi_app.models.response import ProblemDetailResponse

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
        const ws = new WebSocket(
            'ws://localhost:8000/ws/design/session123?token=' + token
        );

        ws.send(JSON.stringify({
            type: 'design_beam',
            params: {
                width: 300,
                depth: 500,
                moment: 150,
                shear: 75,
                fck: 25,
                fy: 500,
                cover: 25,
                stirrup_dia_mm: 8,
                main_bar_dia_mm: 20
            }
        }));
        ```
    """
    user = await verify_ws_token(websocket, token, required_scopes=("design",))
    if not user:
        return

    await manager.connect(session_id, websocket)

    try:
        while True:
            try:
                # Decode before dispatch without discarding duplicate actions or
                # accepting non-standard numeric values such as NaN/Infinity.
                data = parse_json_or_error(await websocket.receive_text())
                if not isinstance(data, dict):
                    raise InputContractError(
                        (
                            InputIssueV1(
                                code="INPUT_TYPE_INVALID",
                                path="$",
                                message="A WebSocket message must be a JSON object.",
                            ),
                        )
                    )
                message_type = data.get("type", "unknown")
                if message_type == "design_beam":
                    validated = model_validate_or_error(WSDesignMessage, data)
                    await handle_design_beam(session_id, validated.params.model_dump())

                elif message_type == "check_beam":
                    await handle_check_beam(session_id, data)

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

            except InputContractError as e:
                await manager.send_json(
                    session_id,
                    {
                        "type": "error",
                        "message": f"Invalid input: {e.message}",
                        "error": e.to_problem(),
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
    """Legacy numeric-string adapter for the declared flexure/shear inputs.

    Unknown inputs must not silently discard actions, depth or source identity.
    ``clear_cover`` remains an accepted alias; ``length`` is viewport metadata,
    not a declaration that span-dependent serviceability has been evaluated.
    """

    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    @model_validator(mode="before")
    @classmethod
    def normalize_cover_alias(cls, value: Any) -> Any:
        if not isinstance(value, dict) or "clear_cover" not in value:
            return value
        value = dict(value)
        alias = value.pop("clear_cover")
        if "cover" in value:
            try:
                equal = float(value["cover"]) == float(alias)
            except (TypeError, ValueError):
                raise PydanticCustomError(
                    "float_type", "Cover aliases must be numeric"
                ) from None
            if not equal:
                raise ValueError(
                    "COVER_ALIAS_CONFLICT: cover and clear_cover must agree"
                )
        value.setdefault("cover", alias)
        return value

    @field_validator(
        "width",
        "depth",
        "moment",
        "shear",
        "fck",
        "fy",
        "cover",
        "stirrup_dia_mm",
        "main_bar_dia_mm",
        mode="before",
        json_schema_input_type=float | str,
    )
    @classmethod
    def reject_boolean_quantity(cls, value: Any) -> Any:
        if isinstance(value, bool):
            raise PydanticCustomError(
                "float_type", "A boolean is not a numeric quantity"
            )
        return value

    @field_validator("length", mode="before", json_schema_input_type=float | str | None)
    @classmethod
    def reject_boolean_length(cls, value: Any) -> Any:
        return cls.reject_boolean_quantity(value)

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
    length: float | None = Field(
        default=None,
        gt=0,
        description="Optional viewport length in mm; no span-dependent check is performed",
    )


class WSDesignMessage(BaseModel):
    """Declared compatibility design request; params retain numeric strings."""

    model_config = ConfigDict(extra="forbid")
    type: Literal["design_beam"]
    params: WSDesignParams


class WSDesignResultMessage(BaseModel):
    """Same compatibility calculation payload as the HTTP beam endpoint."""

    type: Literal["design_result"]
    latency_ms: float = Field(ge=0, allow_inf_nan=False)
    data: BeamDesignResponse


class WSInputProblemMessage(BaseModel):
    """Rejected JSON or request; no calculation outcome is implied."""

    type: Literal["error"]
    message: str
    error: ProblemDetailResponse


def beam_design_websocket_schema_v1() -> dict[str, Any]:
    """Compatibility design and structured intake-error exchange schema."""
    schema = TypeAdapter(
        WSDesignMessage | WSDesignResultMessage | WSInputProblemMessage
    ).json_schema()
    params = schema["$defs"]["WSDesignParams"]
    params["properties"]["clear_cover"] = dict(params["properties"]["cover"])
    params["required"].remove("cover")
    params["anyOf"] = [{"required": ["cover"]}, {"required": ["clear_cover"]}]
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    schema["title"] = "Beam compatibility WebSocket design exchange V1"
    schema["description"] = (
        "Numeric strings remain accepted for legacy params; booleans, non-finite "
        "values, duplicate JSON keys, conflicting cover aliases and unknown inputs reject. "
        "clear_cover is an accepted input alias for cover. length is viewport metadata only."
    )
    return schema


class WSBeamCheckMessageV2(BaseModel):
    """Exact client message for the supplied-beam V2 check."""

    model_config = ConfigDict(strict=True, extra="forbid", allow_inf_nan=False)

    type: Literal["check_beam"]
    params: BeamSuppliedCheckRequestV2


class WSBeamCheckResultMessageV2(BaseModel):
    """One terminal supplied-beam result emitted by the WebSocket."""

    model_config = ConfigDict(strict=True, extra="forbid", allow_inf_nan=False)

    type: Literal["check_result"]
    latency_ms: float = Field(ge=0)
    correlation_id: str
    data: BeamSuppliedCheckResponseV2


class WSBeamCheckErrorMessageV2(BaseModel):
    """Terminal intake or calculation error for the WebSocket check."""

    model_config = ConfigDict(strict=True, extra="forbid", allow_inf_nan=False)

    type: Literal["error"]
    schema_version: Literal["beam-supplied-check-error/v2"]
    terminal_status: Literal["ERROR"]
    correlation_id: str | None
    message: str


_WS_BEAM_CHECK_MACHINE_MESSAGE_V2 = TypeAdapter(
    WSBeamCheckMessageV2 | WSBeamCheckResultMessageV2 | WSBeamCheckErrorMessageV2
)


def beam_check_websocket_schema_v2() -> dict[str, Any]:
    """Return the exact machine schema for the V2 WebSocket exchange."""

    schema = _WS_BEAM_CHECK_MACHINE_MESSAGE_V2.json_schema()
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    schema["$id"] = (
        "https://structural-lib.example/schemas/beam-supplied-check-websocket-v2.json"
    )
    schema["title"] = "Beam supplied-check WebSocket exchange V2"
    schema["description"] = (
        "Exact check_beam client message and terminal check_result/error messages."
    )
    return schema


# =============================================================================
# Message Handlers
# =============================================================================


async def handle_design_beam(session_id: str, params: dict[str, Any]) -> None:
    """
    Handle design_beam message.

    Uses structural_lib.services.beam_api.design_beam_is456 with correct signature:
    - units: "IS456"
    - b_mm, D_mm, d_mm: dimensions in mm
    - mu_knm, vu_kn: forces
    - fck_nmm2, fy_nmm2: material properties

    Discovered via: scripts/discover_api_signatures.py design_beam_is456
    """
    start_time = datetime.now(timezone.utc)

    # Validate input with Pydantic
    try:
        validated = model_validate_or_error(
            WSDesignParams, params, path_prefix="$.params"
        )
    except InputContractError as e:
        await manager.send_json(
            session_id,
            {
                "type": "error",
                "message": f"Invalid input: {e.message}",
                "error": e.to_problem(),
            },
        )
        return

    from structural_lib.services.project_beam import EffectiveDepthBasisV1

    # The legacy adapter retains its documented numeric-string coercion. The
    # calculated depth/basis uses the same explicit physical inputs as HTTP.
    basis = EffectiveDepthBasisV1(
        clear_cover_mm=validated.cover,
        stirrup_diameter_mm=validated.stirrup_dia_mm,
        tension_bar_diameter_mm=validated.main_bar_dia_mm,
    )
    result = await asyncio.to_thread(
        design_beam_is456,
        units="IS456",
        b_mm=validated.width,
        D_mm=validated.depth,
        d_mm=None,
        effective_depth_basis=basis,
        mu_knm=validated.moment,
        vu_kn=validated.shear,
        fck_nmm2=validated.fck,
        fy_nmm2=validated.fy,
        d_dash_mm=validated.cover
        + validated.stirrup_dia_mm
        + validated.main_bar_dia_mm / 2,
        cover_mm=validated.cover,
        stirrup_dia_mm=validated.stirrup_dia_mm,
    )
    inputs = dict(result.design_inputs)
    inputs.pop("pt_percent", None)
    inputs.pop("ast_mm2_for_shear", None)
    inputs["torsion_corner_bar_centres_mm"] = None
    response = project_beam_design_result(result, evidence_inputs=inputs)
    latency_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
    await manager.send_json(
        session_id,
        {
            "type": "design_result",
            "latency_ms": round(latency_ms, 2),
            "data": response.model_dump(mode="json"),
        },
    )


async def handle_check_beam(session_id: str, message: dict[str, Any]) -> None:
    """
    Run the same supplied-beam V2 request and result used by REST.
    """
    start_time = datetime.now(timezone.utc)
    params = message.get("params") if isinstance(message, dict) else None
    correlation_id = (
        params.get("correlation_id")
        if isinstance(params, dict) and isinstance(params.get("correlation_id"), str)
        else None
    )

    try:
        validated = WSBeamCheckMessageV2.model_validate(message).params
    except ValidationError as e:
        error = WSBeamCheckErrorMessageV2(
            type="error",
            schema_version="beam-supplied-check-error/v2",
            terminal_status="ERROR",
            correlation_id=correlation_id,
            message=sanitize_error(e, "live check input"),
        )
        await manager.send_json(
            session_id,
            error.model_dump(mode="json"),
        )
        return

    try:
        result = await asyncio.to_thread(check_supplied_beam_v2, validated)
    except (ValueError, TypeError, RuntimeError, KeyError, AttributeError) as e:
        logger.exception("Supplied beam WebSocket check failed for %s", session_id)
        error = WSBeamCheckErrorMessageV2(
            type="error",
            schema_version="beam-supplied-check-error/v2",
            terminal_status="ERROR",
            correlation_id=validated.correlation_id,
            message=sanitize_error(e, "live check calculation"),
        )
        await manager.send_json(
            session_id,
            error.model_dump(mode="json"),
        )
        return

    end_time = datetime.now(timezone.utc)
    latency_ms = (end_time - start_time).total_seconds() * 1000

    response = WSBeamCheckResultMessageV2(
        type="check_result",
        latency_ms=round(latency_ms, 2),
        correlation_id=result.correlation_id,
        data=BeamSuppliedCheckResponseV2.model_validate(result.to_dict()),
    )
    await manager.send_json(
        session_id,
        response.model_dump(mode="json", by_alias=True),
    )
