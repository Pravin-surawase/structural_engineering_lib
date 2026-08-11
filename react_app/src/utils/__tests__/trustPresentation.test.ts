import { describe, expect, it } from 'vitest';
import type { BeamDesignResponse } from '../../api/client';
import { formatPercent, formatRatio, getTrustPresentation } from '../trustPresentation';

function result(utilization: number, status: 'PASS' | 'FAIL' | 'HOLD'): BeamDesignResponse {
  return {
    success: status === 'PASS',
    message: 'test',
    flexure: {
      ast_required: 500,
      ast_min: 200,
      ast_max: 2_000,
      xu: 100,
      xu_max: 200,
      is_under_reinforced: true,
      moment_capacity: 150,
    },
    ast_total: 500,
    asc_total: 0,
    utilization_ratio: utilization,
    evidence: {
      artifact_schema: 'structural_lib.beam-evidence',
      artifact_schema_version: '2.0',
      library_version: '0.23.0',
      code_edition: 'IS 456:2000',
      code_amendment_identity: 'not-declared-in-artifact',
      capability_id: 'design_beam_is456',
      support_status: status === 'HOLD' ? 'HELD' : 'SUPPORTED',
      unit_system: 'IS456',
      explicit_units: { length: 'mm' },
      normalized_input_hash: 'input-hash',
      calculation_identity: 'calculation-id',
      governing_check: 'flexure',
      exact_utilization: utilization,
      margin: status === 'HOLD' ? null : 1 - utilization,
      status,
      generated_at: '2026-08-10T00:00:00Z',
      qualified_review_required: true,
      qualified_review_requirement: 'Qualified review required.',
    },
  };
}

describe('trust presentation', () => {
  it('keeps a near-limit PASS distinguishable from rounded 100%', () => {
    const trust = getTrustPresentation(result(0.9996, 'PASS'));
    expect(trust.canExport).toBe(true);
    expect(formatRatio(trust.exactUtilization)).toBe('0.999600');
    expect(formatPercent(trust.exactUtilization)).toBe('99.960%');
    expect(trust.margin).toBeCloseTo(0.0004);
  });

  it.each(['FAIL', 'HOLD'] as const)('quarantines %s results', (status) => {
    expect(getTrustPresentation(result(status === 'FAIL' ? 1.01 : 0, status)).canExport).toBe(false);
  });

  it('fails closed when evidence identity is absent or a backend hold exists', () => {
    const missing = result(0.5, 'PASS');
    missing.evidence = null;
    expect(getTrustPresentation(missing).status).toBe('HOLD');
    expect(getTrustPresentation(missing).canExport).toBe(false);

    const held = result(0.5, 'PASS');
    held.holds = ['TORSION_SCOPE_HOLD'];
    expect(getTrustPresentation(held).status).toBe('HOLD');
    expect(getTrustPresentation(held).canExport).toBe(false);
  });

  it('fails closed when evidence contradicts the combined primary result', () => {
    const contradictory = result(0.5, 'PASS');
    contradictory.success = false;
    expect(getTrustPresentation(contradictory).status).toBe('HOLD');
  });
});
