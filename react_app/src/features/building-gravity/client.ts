import { unwrapResponse } from '../../api/client';
import { API_BASE_URL } from '../../config';
import type {
  GravityWorkflowDefinition,
  GravityWorkflowRunBundle,
} from './types';

async function readResponse<T>(response: Response, fallback: string): Promise<T> {
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(body?.error?.message ?? `${fallback} (${response.status})`);
  }
  return unwrapResponse<T>(body);
}

export async function getGravityWorkflowDefinition(
  signal?: AbortSignal,
): Promise<GravityWorkflowDefinition> {
  const response = await fetch(`${API_BASE_URL}/api/v1/building-gravity/v1/definition`, {
    ...(signal ? { signal } : {}),
  });
  return readResponse(response, 'Gravity workflow discovery failed');
}

export async function runGravityWorkflow(
  request: Record<string, unknown>,
  signal?: AbortSignal,
): Promise<GravityWorkflowRunBundle> {
  const response = await fetch(`${API_BASE_URL}/api/v1/building-gravity/v1/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
    ...(signal ? { signal } : {}),
  });
  return readResponse(response, 'Gravity workflow failed');
}
