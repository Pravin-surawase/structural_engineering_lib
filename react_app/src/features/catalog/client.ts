import { API_BASE_URL } from '../../config';
import { unwrapResponse } from '../../api/client';
import type { WorkflowCatalog } from './types';
import { parseWorkflowCatalog } from './validation';

export async function fetchWorkflowCatalog(signal?: AbortSignal): Promise<WorkflowCatalog> {
  const response = await fetch(`${API_BASE_URL}/api/v1/catalog/workflows?version=1.2.0`, {
    headers: { Accept: 'application/json' },
    signal,
  });
  if (!response.ok) {
    throw new Error(`Workflow catalogue unavailable (${response.status})`);
  }
  const payload = unwrapResponse<unknown>(await response.json());
  return parseWorkflowCatalog(payload);
}
