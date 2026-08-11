import { API_BASE_URL } from '../../config';
import type { ApiEnvelope, ConcentricIsolatedFootingRequest, ConcentricIsolatedFootingResponse } from './types';

const ENDPOINT = '/api/v1/design/footing/isolated/concentric';

/** Transport only: the service remains authoritative for all checks and decisions. */
export async function designConcentricIsolatedFooting(
  request: ConcentricIsolatedFootingRequest,
  signal?: AbortSignal,
): Promise<ConcentricIsolatedFootingResponse> {
  const response = await fetch(`${API_BASE_URL}${ENDPOINT}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify(request),
    signal,
  });
  const envelope = await response.json().catch(() => null) as ApiEnvelope<ConcentricIsolatedFootingResponse> | null;
  if (!response.ok || !envelope?.success || !envelope.data) {
    const message = typeof envelope?.error === 'string'
      ? envelope.error
      : envelope?.error?.message;
    throw new Error(message || `Footing design request failed (${response.status})`);
  }
  return envelope.data;
}
