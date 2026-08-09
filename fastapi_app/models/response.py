"""Standardized API response wrappers.

Provides a consistent response shape across all API endpoints:
    {"success": true, "data": {...}, "error": null, "clause_refs": null}
"""

from __future__ import annotations

from typing import Any, Generic, Literal, Optional, TypeVar

from pydantic import BaseModel, model_serializer

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standardized response wrapper for all API endpoints."""

    success: bool = True
    data: T
    error: Optional[str | dict[str, Any]] = None
    clause_refs: Optional[dict[str, str]] = None

    @model_serializer(mode="wrap")
    def _serialize_envelope(self, handler):
        """Omit absent envelope metadata without filtering nested payload nulls."""
        serialized = handler(self)
        if self.error is None:
            serialized.pop("error", None)
        if self.clause_refs is None:
            serialized.pop("clause_refs", None)
        return serialized

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"Ast_mm2": 603.2},
                "error": None,
            }
        }


class RequestValidationErrorPayload(BaseModel):
    """Field-preserving Pydantic request validation error."""

    code: Literal["REQUEST_VALIDATION_ERROR"]
    message: str
    details: list[dict[str, Any]]


class RequestValidationErrorResponse(BaseModel):
    """Documented 422 form of the maintained response envelope."""

    success: Literal[False] = False
    data: None = None
    error: RequestValidationErrorPayload


def success_response(data: Any, clause_refs: dict[str, str] | None = None) -> dict:
    """Wrap any response in standardized APIResponse format."""
    result: dict[str, Any] = {"success": True, "data": data}
    if clause_refs:
        result["clause_refs"] = clause_refs
    return result


def error_response(error: str | dict[str, Any]) -> dict:
    """Wrap error in standardized APIResponse format."""
    return {"success": False, "data": None, "error": error}
