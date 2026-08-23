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

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

const GRAVITY_STATUSES = new Set([
  'BLOCKED',
  'ERROR',
  'NOT_EVALUATED',
  'STALE',
  'PASS',
  'FAIL',
  'HOLD',
]);

function hasCanonicalIssues(value: unknown): boolean {
  return Array.isArray(value) && value.every((issue) => (
    isRecord(issue)
    && typeof issue.code === 'string'
    && typeof issue.path === 'string'
    && typeof issue.message === 'string'
  ));
}

function hasGravityEnvelope(value: unknown): boolean {
  return isRecord(value)
    && GRAVITY_STATUSES.has(String(value.overall_status))
    && typeof value.qualified_review_required === 'boolean'
    && typeof value.review_status === 'string'
    && hasCanonicalIssues(value.issues);
}

/** Fail closed before React accepts a gravity result identity or issue list. */
export function parseGravityWorkflowRunBundle(value: unknown): GravityWorkflowRunBundle {
  if (!isRecord(value) || value.schema_version !== 'gravity-workflow-run-bundle/v1') {
    throw new Error('Gravity workflow bundle is missing or unsupported.');
  }
  const workflow = value.workflow_result;
  const book = value.calculation_book;
  if (
    !isRecord(workflow)
    || workflow.schema_version !== 'gravity-workflow-result/v1'
    || typeof workflow.workflow_result_hash !== 'string'
    || !/^[0-9a-f]{64}$/.test(workflow.workflow_result_hash)
    || !hasGravityEnvelope(workflow.result_envelope)
    || !Array.isArray(workflow.components)
    || workflow.components.some(
      (component) => !isRecord(component) || !hasGravityEnvelope(component.result_envelope),
    )
    || !isRecord(book)
    || book.schema_version !== 'gravity-calculation-book/v1'
    || book.workflow_result_hash !== workflow.workflow_result_hash
    || !hasCanonicalIssues(book.issues)
  ) {
    throw new Error('Gravity workflow bundle has inconsistent identity, status, or issues.');
  }
  return value as unknown as GravityWorkflowRunBundle;
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
  return parseGravityWorkflowRunBundle(
    await readResponse<unknown>(response, 'Gravity workflow failed'),
  );
}
