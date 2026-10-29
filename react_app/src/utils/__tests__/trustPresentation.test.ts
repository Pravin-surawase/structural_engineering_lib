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
    result_envelope: {
      schema_version: 'structural-result-envelope/v2',
      intake_status: 'VALID',
      calculation_status: 'COMPLETED',
      engineering_status: status,
      review_status: 'QUALIFIED_REVIEW_REQUIRED',
      qualified_review_required: true,
      freshness_status: 'CURRENT',
      serviceability_escalation: null,
      overall_status: status,
      issues: status === 'PASS' ? [] : [{ code: `BEAM_${status}`, path: '$.calculation', message: status }],
      result_identity: {
        contract_version: 'canonical-beam-result/v1',
        library_version: '0.23.0',
        input_hash: 'input-hash',
        calculation_identity: 'calculation-id',
        artifact_sha256: null,
      },
    },
    evidence: {
      artifact_schema: 'structural_lib.beam-evidence',
      artifact_schema_version: '2.0',
      library_version: '0.23.0',
      library_content_identity: 'library-content-id',
      code_edition: 'IS 456:2000',
      code_amendment_identity: 'not-declared-in-artifact',
      amendment_applicability: 'REVIEWED_NO_CALCULATION_CHANGE',
      amendment_applicability_review_id: 'review-id',
      controlled_source_ids: ['source-id'],
      controlled_source_basis_hash: 'source-basis-hash',
      capability_id: 'design_beam_is456',
      support_status: status === 'HOLD' ? 'HELD' : 'SUPPORTED',
      unit_system: 'IS456',
      explicit_units: { length: 'mm' },
      normalized_input_hash: 'input-hash',
      provenance_hash: 'provenance-hash',
      source_metadata: {},
      calculation_identity: 'calculation-id',
      replay_receipt: {},
      replay_receipt_hash: 'replay-receipt-hash',
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

  it('fails closed when freshness or aggregate status is not a current outcome', () => {
    const stale = result(0.5, 'PASS');
    stale.result_envelope.freshness_status = 'STALE';
    stale.result_envelope.overall_status = 'STALE';
    expect(getTrustPresentation(stale).status).toBe('HOLD');

    const contradictory = result(0.5, 'PASS');
    contradictory.result_envelope.overall_status = 'FAIL';
    expect(getTrustPresentation(contradictory).status).toBe('HOLD');
  });
});

it('preserves explicit unavailable values instead of the legacy display cap', () => {
  const payload = result(2, 'FAIL');
  payload.governing_utilization = null;
  payload.evidence!.exact_utilization = null;
  payload.evidence!.margin = null;
  const trust = getTrustPresentation(payload);
  expect(trust.exactUtilization).toBeNull();
  expect(trust.margin).toBeNull();
  expect(formatRatio(trust.exactUtilization)).toBe('Unavailable');
  expect(formatPercent(trust.exactUtilization)).toBe('Unavailable');
  expect(trust.canExport).toBe(false);
});

it('uses uncapped actual utilization and never reconstructs it from a display field', () => {
  const payload = result(3.25, 'FAIL');
  payload.utilization_ratio = 2;
  payload.governing_utilization = 3.25;
  expect(getTrustPresentation(payload).exactUtilization).toBe(3.25);
  payload.evidence = null;
  delete payload.governing_utilization;
  expect(getTrustPresentation(payload).exactUtilization).toBeNull();
});

it('holds a projection that contradicts its evidence quantity', () => {
  const payload = result(0.5, 'PASS');
  payload.governing_utilization = 0.6;
  expect(getTrustPresentation(payload).status).toBe('HOLD');
  expect(getTrustPresentation(payload).canExport).toBe(false);
});

it('retains a finite saved batch-v1 ratio but never overrides explicit null', async () => {
  const { batchGoverningUtilization } = await import('../../api/client');
  expect(batchGoverningUtilization({ utilization_ratio: 3.25 })).toBe(3.25);
  expect(batchGoverningUtilization({ utilization_ratio: 2, governing_utilization: null })).toBeNull();
  expect(batchGoverningUtilization({ utilization_ratio: 2, evidence: { exact_utilization: null } })).toBeNull();
});
