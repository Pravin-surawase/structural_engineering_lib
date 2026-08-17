import { describe, it, expect, beforeEach } from 'vitest';
import type { StructuralResultEnvelope } from '../../api/client';
import { useDesignStore } from '../../store/designStore';

const RESULT_ENVELOPE: StructuralResultEnvelope = {
  schema_version: 'structural-result-envelope/v2',
  intake_status: 'VALID',
  calculation_status: 'COMPLETED',
  engineering_status: 'PASS',
  review_status: 'QUALIFIED_REVIEW_REQUIRED',
  qualified_review_required: true,
  freshness_status: 'CURRENT',
  serviceability_escalation: null,
  overall_status: 'PASS',
  issues: [],
  result_identity: null,
};

describe('designStore', () => {
  beforeEach(() => {
    useDesignStore.getState().reset();
  });

  it('has correct default inputs', () => {
    const state = useDesignStore.getState();
    expect(state.inputs.width).toBe(300);
    expect(state.inputs.depth).toBe(450);
    expect(state.inputs.moment).toBe(150);
    expect(state.inputs.fck).toBe(25.0);
    expect(state.inputs.fy).toBe(500.0);
    expect(state.length).toBe(4000);
  });

  it('has correct default flags', () => {
    const state = useDesignStore.getState();
    expect(state.result).toBeNull();
    expect(state.isLoading).toBe(false);
    expect(state.error).toBeNull();
    expect(state.autoDesign).toBe(true);
    expect(state.useWebSocket).toBe(false);
  });

  it('setInputs merges partial inputs', () => {
    const initialRevision = useDesignStore.getState().inputRevision;
    useDesignStore.getState().setInputs({ width: 400, depth: 600 });
    const state = useDesignStore.getState();
    expect(state.inputs.width).toBe(400);
    expect(state.inputs.depth).toBe(600);
    // Unchanged fields preserved
    expect(state.inputs.moment).toBe(150);
    expect(state.inputs.fck).toBe(25.0);
    expect(state.inputRevision).toBe(initialRevision + 1);
  });

  it('setResult clears error', () => {
    const store = useDesignStore.getState();
    store.setError('some error');
    expect(useDesignStore.getState().error).toBe('some error');

    const mockResult = {
      success: true,
      message: 'ok',
      flexure: {
        ast_required: 500,
        ast_min: 200,
        ast_max: 3000,
        xu: 50,
        xu_max: 200,
        is_under_reinforced: true,
        moment_capacity: 180,
      },
      ast_total: 500,
      asc_total: 0,
      utilization_ratio: 0.83,
      result_envelope: RESULT_ENVELOPE,
    };
    store.setResult(mockResult);

    const updated = useDesignStore.getState();
    expect(updated.result).toEqual(mockResult);
    expect(updated.error).toBeNull();
    expect(updated.resultLifecycle).toBe('current');
    expect(updated.resultRevision).toBe(updated.inputRevision);
  });

  it('invalidates a retained result when inputs change', () => {
    const store = useDesignStore.getState();
    store.setResult({
      success: true,
      message: 'current',
      flexure: {
        ast_required: 500,
        ast_min: 200,
        ast_max: 3000,
        xu: 50,
        xu_max: 200,
        is_under_reinforced: true,
        moment_capacity: 180,
      },
      ast_total: 500,
      asc_total: 0,
      utilization_ratio: 0.83,
      result_envelope: RESULT_ENVELOPE,
    });

    const settledRevision = useDesignStore.getState().inputRevision;
    store.setInputs({ moment: 175 });

    const updated = useDesignStore.getState();
    expect(updated.inputRevision).toBe(settledRevision + 1);
    expect(updated.resultRevision).toBe(settledRevision);
    expect(updated.resultLifecycle).toBe('stale');
    expect(updated.result?.message).toBe('current');
  });

  it('rejects result, error, and finalizer writes from an older revision', () => {
    const store = useDesignStore.getState();
    const oldRevision = store.inputRevision;
    store.setInputs({ width: 350 });

    expect(store.setResult({
      success: true,
      message: 'late',
      flexure: {
        ast_required: 500,
        ast_min: 200,
        ast_max: 3000,
        xu: 50,
        xu_max: 200,
        is_under_reinforced: true,
        moment_capacity: 180,
      },
      ast_total: 500,
      asc_total: 0,
      utilization_ratio: 0.83,
      result_envelope: RESULT_ENVELOPE,
    }, oldRevision)).toBe(false);
    expect(store.setError('late error', oldRevision)).toBe(false);
    expect(store.setLoading(false, oldRevision)).toBe(false);

    const updated = useDesignStore.getState();
    expect(updated.result).toBeNull();
    expect(updated.error).toBeNull();
    expect(updated.resultLifecycle).toBe('not_evaluated');
  });

  it('setLoading updates loading state', () => {
    useDesignStore.getState().setLoading(true);
    expect(useDesignStore.getState().isLoading).toBe(true);
  });

  it('setError sets error and clears loading', () => {
    useDesignStore.getState().setLoading(true);
    useDesignStore.getState().setError('API failed');
    const state = useDesignStore.getState();
    expect(state.error).toBe('API failed');
    expect(state.isLoading).toBe(false);
  });

  it('reset restores defaults', () => {
    const store = useDesignStore.getState();
    store.setInputs({ width: 999 });
    store.setLength(8000);
    store.setError('error');
    store.reset();

    const state = useDesignStore.getState();
    expect(state.inputs.width).toBe(300);
    expect(state.length).toBe(4000);
    expect(state.error).toBeNull();
    expect(state.result).toBeNull();
  });
});
