"""Standardized API response wrappers.

Provides a consistent response shape across all API endpoints:
    {"success": true, "data": {...}, "error": null, "clause_refs": null}
"""

from __future__ import annotations

from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standardized response wrapper for all API endpoints."""

    success: bool = True
    data: T
    error: Optional[str] = None
    clause_refs: Optional[dict[str, str]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"Ast_mm2": 603.2},
                "error": None,
            }
        }


def success_response(data: Any, clause_refs: dict[str, str] | None = None) -> dict:
    """Wrap any response in standardized APIResponse format."""
    result: dict[str, Any] = {"success": True, "data": data}
    if clause_refs:
        result["clause_refs"] = clause_refs
    return result


def error_response(error: str) -> dict:
    """Wrap error in standardized APIResponse format."""
    return {"success": False, "data": None, "error": error}
