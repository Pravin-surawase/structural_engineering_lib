"""Default-disabled transport for the one allowlisted beam workflow."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

from fastapi_app.config import get_settings
from fastapi_app.models.response import APIResponse, error_response, success_response
from fastapi_app.models.workflows import (
    WorkflowCancellationResponse,
    WorkflowDefinitionModel,
    WorkflowRunRequest,
    WorkflowRunResponse,
    WorkflowValidateRequest,
    WorkflowValidationResponse,
)
from structural_lib.services.workflow_runner import WorkflowRunner

router = APIRouter(prefix="/workflows", tags=["workflows"])


def _runner_disabled() -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content=error_response(
            {
                "code": "WORKFLOW_RUNNER_DISABLED",
                "message": "Workflow execution is disabled for this process.",
            }
        ),
    )


@router.get(
    "/beam-template",
    response_model=APIResponse[WorkflowDefinitionModel],
    summary="Discover the approved beam workflow template",
)
async def get_beam_workflow_template():
    from structural_lib.services.workflow_runner import (
        get_beam_workflow_template_document,
    )

    return success_response(get_beam_workflow_template_document())


@router.post(
    "/validate",
    response_model=APIResponse[WorkflowValidationResponse],
    summary="Validate the bounded beam workflow",
)
async def validate_beam_workflow(request: WorkflowValidateRequest):
    if not get_settings().workflow_runner_enabled:
        return _runner_disabled()

    from structural_lib.services.workflow_catalog import (
        get_workflow_catalog,
        get_workflow_input_defaults,
    )
    from structural_lib.services.workflow_runner import (
        WorkflowDefinitionError,
        WorkflowInputError,
        validate_example_input,
        validate_workflow_definition,
    )

    try:
        definition = validate_workflow_definition(request.definition.model_dump())
        capability = get_workflow_catalog().capabilities[0]
        defaults = get_workflow_input_defaults(capability)
        inputs = {**defaults, **request.inputs}
        validate_example_input(capability, inputs)
    except (WorkflowDefinitionError, WorkflowInputError, ValueError) as exc:
        return JSONResponse(
            status_code=422,
            content=error_response(
                {"code": "WORKFLOW_VALIDATION_ERROR", "message": str(exc)}
            ),
        )

    return success_response(
        WorkflowValidationResponse(
            workflow_id="is456.beam.review",
            normalized_definition=WorkflowDefinitionModel.model_validate(definition),
            normalized_inputs={key: float(value) for key, value in inputs.items()},
        )
    )


@router.post(
    "/run",
    response_model=APIResponse[WorkflowRunResponse],
    summary="Run the bounded beam workflow",
)
async def run_beam_workflow(request: WorkflowRunRequest):
    if not get_settings().workflow_runner_enabled:
        return _runner_disabled()

    from structural_lib.services.workflow_runner import (
        WorkflowBusyError,
        WorkflowDefinitionError,
        WorkflowIdempotencyError,
        WorkflowInputError,
    )

    runner: WorkflowRunner = _RUNNER
    try:
        result = await run_in_threadpool(
            runner.run,
            definition=request.definition.model_dump(),
            inputs=request.inputs,
            run_id=request.run_id,
            review_acknowledged=request.review_acknowledged,
            timeout_ms=request.timeout_ms,
        )
    except (WorkflowDefinitionError, WorkflowInputError) as exc:
        return JSONResponse(
            status_code=422,
            content=error_response(
                {"code": "WORKFLOW_VALIDATION_ERROR", "message": str(exc)}
            ),
        )
    except WorkflowIdempotencyError as exc:
        return JSONResponse(
            status_code=409,
            content=error_response(
                {"code": "WORKFLOW_IDEMPOTENCY_CONFLICT", "message": str(exc)}
            ),
        )
    except WorkflowBusyError as exc:
        return JSONResponse(
            status_code=429,
            content=error_response(
                {"code": "WORKFLOW_CONCURRENCY_LIMIT", "message": str(exc)}
            ),
        )
    return success_response(WorkflowRunResponse.model_validate(result))


@router.post(
    "/runs/{run_id}/cancel",
    response_model=APIResponse[WorkflowCancellationResponse],
    summary="Cancel a bounded workflow run",
)
async def cancel_beam_workflow(run_id: str):
    if not get_settings().workflow_runner_enabled:
        return _runner_disabled()

    from structural_lib.services.workflow_runner import WorkflowInputError

    try:
        cancelled = _RUNNER.cancel(run_id)
    except WorkflowInputError as exc:
        return JSONResponse(
            status_code=422,
            content=error_response(
                {"code": "WORKFLOW_VALIDATION_ERROR", "message": str(exc)}
            ),
        )
    return success_response(
        WorkflowCancellationResponse(
            run_id=run_id,
            cancellation_requested=cancelled,
        )
    )


_RUNNER = WorkflowRunner()
