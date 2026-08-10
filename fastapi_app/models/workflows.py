"""Typed models for the default-disabled bounded beam workflow transport."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class WorkflowStepDefinitionModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step_id: Literal["input", "validate", "design", "review", "export"]
    handler_id: str
    position: int = Field(ge=1, le=5)


class WorkflowBindingModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str
    target: str
    unit_contract: str


class WorkflowLimitsModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    max_steps: Literal[5]
    max_definition_bytes: Literal[16384]
    max_input_bytes: Literal[32768]
    max_output_bytes: Literal[262144]
    max_timeout_ms: Literal[2000]
    max_concurrency: Literal[1]
    max_project_members: Literal[1]
    max_batch_items: Literal[1]
    max_cached_runs: Literal[128]


class WorkflowDefinitionModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"]
    workflow_id: Literal["is456.beam.review"]
    workflow_version: Literal["1.0.0"]
    title: str
    capability_id: Literal["is456.beam.design"]
    steps: list[WorkflowStepDefinitionModel] = Field(min_length=5, max_length=5)
    bindings: list[WorkflowBindingModel] = Field(min_length=2, max_length=2)
    limits: WorkflowLimitsModel


class WorkflowValidateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    definition: WorkflowDefinitionModel
    inputs: dict[str, float]


class WorkflowRunRequest(WorkflowValidateRequest):
    run_id: str = Field(pattern=r"^[A-Za-z0-9_-]{1,64}$")
    review_acknowledged: bool = False
    timeout_ms: int = Field(default=1500, ge=0, le=2000)


class WorkflowValidationResponse(BaseModel):
    valid: Literal[True] = True
    workflow_id: Literal["is456.beam.review"]
    normalized_definition: WorkflowDefinitionModel
    normalized_inputs: dict[str, float]


class WorkflowStepResultModel(BaseModel):
    step_id: str
    status: str
    reason: str | None = None
    output: dict[str, Any] | None = None


class WorkflowAuditModel(BaseModel):
    review_stop: str | None


class WorkflowRunResponse(BaseModel):
    run_id: str
    workflow_id: Literal["is456.beam.review"]
    status: Literal["COMPLETED", "REVIEW_REQUIRED", "UNSAFE", "CANCELLED", "TIMED_OUT"]
    steps: list[WorkflowStepResultModel]
    export: dict[str, Any] | None
    audit: WorkflowAuditModel
    definition_hash: str
    input_hash: str
    idempotent_replay: bool


class WorkflowCancellationResponse(BaseModel):
    run_id: str
    cancellation_requested: bool
