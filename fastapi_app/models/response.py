"""Canonical FastAPI success, structural-result, and problem envelopes."""

from __future__ import annotations

from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, Field, model_serializer

T = TypeVar("T")


class StructuralIssueResponse(BaseModel):
    """Stable issue code, path, and explanation."""

    code: str
    path: str
    message: str


class ResultIdentityResponse(BaseModel):
    """Replay identity attached to a calculation-bearing result."""

    contract_version: str
    library_version: str
    input_hash: str | None = None
    calculation_identity: str | None = None
    artifact_sha256: str | None = None


class StructuralResultEnvelopeResponse(BaseModel):
    """Transport model of the canonical structural-result envelope."""

    schema_version: Literal["structural-result-envelope/v2"]
    intake_status: Literal["VALID", "PARTIAL", "BLOCKED"]
    calculation_status: Literal["NOT_EVALUATED", "COMPLETED", "ERROR"]
    engineering_status: Literal["NOT_EVALUATED", "PASS", "FAIL", "HOLD"]
    review_status: Literal[
        "QUALIFIED_REVIEW_REQUIRED", "REVIEWED_ACCEPTED", "REVIEWED_REJECTED"
    ]
    qualified_review_required: bool
    freshness_status: Literal["CURRENT", "STALE"]
    serviceability_escalation: str | None = None
    overall_status: Literal[
        "BLOCKED", "ERROR", "NOT_EVALUATED", "STALE", "PASS", "FAIL", "HOLD"
    ]
    issues: list[StructuralIssueResponse] = Field(default_factory=list)
    result_identity: ResultIdentityResponse | None = None


class ProblemDetailResponse(BaseModel):
    """Versioned problem body used by every maintained JSON error response."""

    schema_version: Literal["structural-problem/v1"] = "structural-problem/v1"
    code: str
    message: str
    details: Any | None = None
    request_id: str | None = None


class ProblemResponse(BaseModel):
    """Rejected transport envelope; never an engineering result."""

    success: Literal[False] = False
    data: None = None
    error: ProblemDetailResponse


# Compatibility import names now point to the one problem schema.
RequestValidationErrorPayload = ProblemDetailResponse
RequestValidationErrorResponse = ProblemResponse


class APIResponse(BaseModel, Generic[T]):
    """Accepted transport envelope.

    ``success`` means only that the HTTP operation returned its declared payload.
    Engineering PASS/FAIL/HOLD lives in a calculation-bearing result envelope.
    """

    success: Literal[True] = True
    data: T
    error: ProblemDetailResponse | None = None
    clause_refs: dict[str, str] | None = None

    @model_serializer(mode="wrap")
    def _serialize_envelope(self, handler):
        """Omit absent metadata without filtering nested payload nulls."""

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
            }
        }


def success_response(data: Any, clause_refs: dict[str, str] | None = None) -> dict:
    """Wrap an accepted transport payload without inferring engineering status."""

    result: dict[str, Any] = {"success": True, "data": data}
    if clause_refs:
        result["clause_refs"] = clause_refs
    return result


def _problem_detail(
    error: str | dict[str, Any],
    *,
    request_id: str | None = None,
) -> dict[str, Any]:
    if isinstance(error, str):
        problem = ProblemDetailResponse(
            code="APPLICATION_ERROR",
            message=error,
            request_id=request_id,
        )
        return problem.model_dump(exclude_none=True)

    code = error.get("code") or error.get("error_code") or "APPLICATION_ERROR"
    message = error.get("message") or error.get("detail") or "Operation failed"
    details = error.get("details")
    if details is None:
        extras = {
            key: value
            for key, value in error.items()
            if key not in {"code", "error_code", "message", "detail", "request_id"}
        }
        details = extras or None
    problem = ProblemDetailResponse(
        code=str(code),
        message=str(message),
        details=details,
        request_id=(
            str(error["request_id"])
            if error.get("request_id") is not None
            else request_id
        ),
    )
    return problem.model_dump(exclude_none=True)


def error_response(
    error: str | dict[str, Any],
    *,
    request_id: str | None = None,
) -> dict[str, Any]:
    """Wrap every rejected JSON transport in the canonical problem schema."""

    return {
        "success": False,
        "data": None,
        "error": _problem_detail(error, request_id=request_id),
    }
