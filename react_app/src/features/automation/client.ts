import { parseStructuralResultEnvelope, unwrapResponse } from '../../api/client';
import { API_BASE_URL } from '../../config';
import type { CatalogBeamValues } from '../catalog/types';
import type {
  WorkflowDefinition,
  WorkflowRunResult,
  WorkflowValidationResult,
} from './types';

async function readPayload<T>(response: Response): Promise<T> {
  const payload = await response.json().catch(() => null) as unknown;
  if (!response.ok) {
    const message =
      payload && typeof payload === 'object' && 'error' in payload
        ? JSON.stringify((payload as { error: unknown }).error)
        : `Request failed (${response.status})`;
    throw new Error(message);
  }
  return unwrapResponse<T>(payload);
}

export async function fetchBeamWorkflowTemplate(signal?: AbortSignal): Promise<WorkflowDefinition> {
  const response = await fetch(`${API_BASE_URL}/api/v1/workflows/beam-template`, {
    headers: { Accept: 'application/json' },
    signal,
  });
  return readPayload<WorkflowDefinition>(response);
}

export async function validateBeamWorkflow(
  definition: WorkflowDefinition,
  inputs: CatalogBeamValues,
  signal?: AbortSignal,
): Promise<WorkflowValidationResult> {
  const response = await fetch(`${API_BASE_URL}/api/v1/workflows/validate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ definition, inputs }),
    signal,
  });
  return readPayload<WorkflowValidationResult>(response);
}

export async function runBeamWorkflow(
  definition: WorkflowDefinition,
  inputs: CatalogBeamValues,
  runId: string,
  reviewAcknowledged: boolean,
  signal?: AbortSignal,
): Promise<WorkflowRunResult> {
  const response = await fetch(`${API_BASE_URL}/api/v1/workflows/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      definition,
      inputs,
      run_id: runId,
      review_acknowledged: reviewAcknowledged,
      timeout_ms: 1500,
    }),
    signal,
  });
  const payload = await readPayload<unknown>(response);
  if (typeof payload !== 'object' || payload === null || Array.isArray(payload)) {
    throw new Error('Workflow run response must be an object');
  }
  return {
    ...payload,
    result_envelope: parseStructuralResultEnvelope(
      (payload as Record<string, unknown>).result_envelope,
    ),
  } as WorkflowRunResult;
}

export async function cancelBeamWorkflow(runId: string): Promise<boolean> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/workflows/runs/${encodeURIComponent(runId)}/cancel`,
    { method: 'POST' },
  );
  const result = await readPayload<{ cancellation_requested: boolean }>(response);
  return result.cancellation_requested;
}
