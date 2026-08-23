import { afterEach, describe, expect, it, vi } from 'vitest';

import {
  parseGravityWorkflowRunBundle,
  runGravityWorkflow,
} from './client';

const WORKFLOW_HASH = 'a'.repeat(64);

function bundle() {
  const envelope = {
    overall_status: 'HOLD',
    qualified_review_required: true,
    review_status: 'QUALIFIED_REVIEW_REQUIRED',
    issues: [{
      code: 'BEAM_SUPPLIED_REINFORCEMENT_NOT_SUPPLIED',
      path: '$.components.B1',
      message: 'A supplied bar schedule is required.',
    }],
  };
  return {
    schema_version: 'gravity-workflow-run-bundle/v1',
    workflow_result: {
      schema_version: 'gravity-workflow-result/v1',
      model_hash: 'b'.repeat(64),
      load_model_hash: 'c'.repeat(64),
      ledger_hash: 'd'.repeat(64),
      workflow_result_hash: WORKFLOW_HASH,
      practical_action_reconciliation: [],
      actions: [],
      components: [{
        component_id: 'B1',
        kind: 'BEAM',
        canonical_function: 'design_beam_is456',
        result_envelope: envelope,
        result: null,
      }],
      result_envelope: envelope,
      limitations: [],
    },
    calculation_book: {
      schema_version: 'gravity-calculation-book/v1',
      workflow_result_hash: WORKFLOW_HASH,
      practical_action_reconciliation: [],
      reconciliation: {
        all_balanced: true,
        boundary_count: 1,
        maximum_absolute_residual_kn: 0,
        balance_tolerance_kn: 0.001,
        accepted_entry_count: 1,
        blocked_entry_count: 0,
      },
      approved_exclusions: [],
      limitations: [],
      issues: envelope.issues,
      review_disposition: 'QUALIFIED_REVIEW_REQUIRED',
    },
  };
}

describe('building gravity parity client', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('preserves the REST workflow identity, governing status, and issues', async () => {
    const payload = bundle();
    const fetchMock = vi.fn<
      (input: RequestInfo | URL, init?: RequestInit) => Promise<Response>
    >(async () => new Response(JSON.stringify({
      success: true,
      data: payload,
    }), { status: 200, headers: { 'Content-Type': 'application/json' } }));
    vi.stubGlobal('fetch', fetchMock);

    const result = await runGravityWorkflow({ schema_version: 'gravity-workflow-request/v1' });

    expect(result.workflow_result.workflow_result_hash).toBe(WORKFLOW_HASH);
    expect(result.workflow_result.result_envelope.overall_status).toBe('HOLD');
    expect(result.workflow_result.result_envelope.issues).toEqual(
      payload.workflow_result.result_envelope.issues,
    );
    const [, request] = fetchMock.mock.calls[0];
    expect(JSON.parse(String(request?.body))).toEqual({
      schema_version: 'gravity-workflow-request/v1',
    });
  });

  it('blocks a mismatched calculation-book identity', () => {
    const payload = bundle();
    payload.calculation_book.workflow_result_hash = 'f'.repeat(64);

    expect(() => parseGravityWorkflowRunBundle(payload)).toThrow(
      /inconsistent identity/i,
    );
  });
});
