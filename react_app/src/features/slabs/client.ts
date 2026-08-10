import { API_BASE_URL } from '../../config';
import { unwrapResponse } from '../../api/client';
import type {
  SlabWorkflowMode,
  SlabWorkflowRequest,
  SlabWorkflowResult,
} from './types';

const PATHS: Record<SlabWorkflowMode, string> = {
  'simply-supported': '/api/v1/design/slab/one-way/complete',
  continuous: '/api/v1/design/slab/one-way/continuous/builtin',
  'two-way': '/api/v1/design/slab/two-way/panel/builtin',
};

export async function designSlabWorkflow(
  mode: SlabWorkflowMode,
  request: SlabWorkflowRequest,
  signal?: AbortSignal,
): Promise<SlabWorkflowResult> {
  const response = await fetch(`${API_BASE_URL}${PATHS[mode]}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
    ...(signal ? { signal } : {}),
  });
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    const message = body?.error?.message ?? `Slab design failed (${response.status})`;
    throw new Error(message);
  }
  return unwrapResponse<SlabWorkflowResult>(body);
}
