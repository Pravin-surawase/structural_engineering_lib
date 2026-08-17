import { afterEach, describe, expect, it, vi } from 'vitest';
import { runBeamWorkflow } from '../client';
import type { WorkflowDefinition } from '../types';

const ENVELOPE = {
  schema_version: 'structural-result-envelope/v2',
  intake_status: 'VALID',
  calculation_status: 'COMPLETED',
  engineering_status: 'FAIL',
  review_status: 'QUALIFIED_REVIEW_REQUIRED',
  qualified_review_required: true,
  freshness_status: 'CURRENT',
  serviceability_escalation: null,
  overall_status: 'FAIL',
  issues: [{ code: 'BEAM_DESIGN_CHECK_FAILED', path: '$.calculation', message: 'Failed' }],
  result_identity: null,
};
const VALUES = {
  width: 300,
  depth: 500,
  clear_cover: 40,
  stirrup_dia_mm: 8,
  main_bar_dia_mm: 18,
  moment: 150,
  shear: 420,
  fck: 25,
  fy: 500,
};

afterEach(() => vi.unstubAllGlobals());

describe('workflow client result contract', () => {
  it('preserves the canonical engineering disposition', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({
      success: true,
      data: { status: 'UNSAFE', result_envelope: ENVELOPE },
    }))));

    const result = await runBeamWorkflow(
      {} as WorkflowDefinition,
      VALUES,
      'client-contract',
      true,
    );

    expect(result.result_envelope.engineering_status).toBe('FAIL');
  });

  it('rejects a successful transport with no structural result envelope', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({
      success: true,
      data: { status: 'UNSAFE' },
    }))));

    await expect(runBeamWorkflow(
      {} as WorkflowDefinition,
      VALUES,
      'client-contract-missing',
      true,
    )).rejects.toThrow('result envelope is missing or unsupported');
  });
});
