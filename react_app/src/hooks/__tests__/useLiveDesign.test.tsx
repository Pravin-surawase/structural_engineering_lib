import { act, renderHook, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import type { BeamDesignResponse } from '../../api/client';
import { useDesignStore } from '../../store/designStore';
import { createQuickDesignIdentity, useLiveDesign } from '../useLiveDesign';

const mocks = vi.hoisted(() => ({
  designBeam: vi.fn(),
  useBeamGeometry: vi.fn(),
}));

vi.mock('../../api/client', async (importOriginal) => ({
  ...await importOriginal<typeof import('../../api/client')>(),
  designBeam: mocks.designBeam,
}));

vi.mock('../useBeamGeometry', () => ({
  useBeamGeometry: mocks.useBeamGeometry,
}));

function designResult(message: string, utilization = 0.8): BeamDesignResponse {
  return {
    success: true,
    message,
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
    utilization_ratio: utilization,
    holds: [],
    evidence: {
      artifact_schema: 'structural_lib.beam-evidence',
      artifact_schema_version: '2.0',
      library_version: '0.23.0',
      code_edition: 'IS 456:2000',
      code_amendment_identity: 'not-declared-in-artifact',
      capability_id: 'design_beam_is456',
      support_status: 'SUPPORTED',
      unit_system: 'IS456',
      explicit_units: { length: 'mm' },
      normalized_input_hash: `input-${message}`,
      calculation_identity: `calculation-${message}`,
      governing_check: 'flexure',
      exact_utilization: utilization,
      margin: 1 - utilization,
      status: 'PASS',
      generated_at: '2026-08-10T00:00:00Z',
      qualified_review_required: true,
      qualified_review_requirement: 'Qualified review required.',
    },
  };
}

function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason?: unknown) => void;
  const promise = new Promise<T>((resolvePromise, rejectPromise) => {
    resolve = resolvePromise;
    reject = rejectPromise;
  });
  return { promise, resolve, reject };
}

describe('useLiveDesign request truth', () => {
  beforeEach(() => {
    useDesignStore.getState().reset();
    mocks.designBeam.mockReset();
    mocks.useBeamGeometry.mockReset();
    mocks.useBeamGeometry.mockReturnValue({
      data: null,
      isLoading: false,
      error: null,
    });
  });

  it('binds the accepted result and export eligibility to the dispatched revision', async () => {
    mocks.designBeam.mockResolvedValue(designResult('current'));
    const { result } = renderHook(() => useLiveDesign({ autoDesign: false }));

    act(() => {
      expect(result.current.actions.triggerDesign()).toBe(true);
    });

    await waitFor(() => expect(result.current.state.result?.message).toBe('current'));
    const [, options] = mocks.designBeam.mock.calls[0];
    expect(options.signal).toBeInstanceOf(AbortSignal);
    expect(result.current.state.resultRevision).toBe(result.current.state.inputRevision);
    expect(result.current.state.resultLifecycle).toBe('current');
    expect(result.current.state.exportEligible).toBe(true);
  });

  it('replaces the Strict Mode probe request instead of leaving loading stuck', async () => {
    const first = deferred<BeamDesignResponse>();
    mocks.designBeam
      .mockReturnValueOnce(first.promise)
      .mockResolvedValueOnce(designResult('strict-mode-current'));

    const { result } = renderHook(
      () => useLiveDesign({ autoDesign: true }),
      { reactStrictMode: true },
    );

    await waitFor(() => expect(mocks.designBeam).toHaveBeenCalledTimes(2));
    expect((mocks.designBeam.mock.calls[0][1].signal as AbortSignal).aborted).toBe(true);
    await waitFor(() => expect(result.current.state.result?.message).toBe('strict-mode-current'));
    expect(result.current.state.isDesigning).toBe(false);
    expect(result.current.state.exportEligible).toBe(true);
  });

  it('ignores a cancelled older response and its finalizer while a newer request runs', async () => {
    const first = deferred<BeamDesignResponse>();
    const second = deferred<BeamDesignResponse>();
    mocks.designBeam
      .mockReturnValueOnce(first.promise)
      .mockReturnValueOnce(second.promise);
    const { result } = renderHook(() => useLiveDesign({ autoDesign: false }));

    act(() => {
      result.current.actions.triggerDesign();
    });
    const firstSignal = mocks.designBeam.mock.calls[0][1].signal as AbortSignal;

    act(() => {
      result.current.actions.updateInputs({ moment: 225 });
    });
    expect(firstSignal.aborted).toBe(true);

    act(() => {
      result.current.actions.triggerDesign();
    });
    expect(result.current.state.isDesigning).toBe(true);

    await act(async () => {
      first.resolve(designResult('older'));
      await first.promise;
    });
    expect(result.current.state.isDesigning).toBe(true);
    expect(result.current.state.result).toBeNull();

    await act(async () => {
      second.resolve(designResult('newer', 0.72));
      await second.promise;
    });
    await waitFor(() => expect(result.current.state.result?.message).toBe('newer'));
    expect(result.current.state.isDesigning).toBe(false);
    expect(result.current.state.exportEligible).toBe(true);
  });

  it('marks a retained result stale immediately after an edit', async () => {
    mocks.designBeam.mockResolvedValue(designResult('settled'));
    const { result } = renderHook(() => useLiveDesign({ autoDesign: false }));

    act(() => {
      result.current.actions.triggerDesign();
    });
    await waitFor(() => expect(result.current.state.resultLifecycle).toBe('current'));

    act(() => {
      result.current.actions.updateLength(6000);
    });

    expect(result.current.state.result?.message).toBe('settled');
    expect(result.current.state.resultLifecycle).toBe('stale');
    expect(result.current.state.exportEligible).toBe(false);
    expect(mocks.useBeamGeometry).toHaveBeenLastCalledWith(null, { enabled: false });
  });

  it('creates a stable identity for equal canonical quick inputs', () => {
    const state = useDesignStore.getState();
    expect(createQuickDesignIdentity(state.inputs, state.length, state.inputRevision)).toEqual(
      createQuickDesignIdentity({ ...state.inputs }, state.length, state.inputRevision),
    );
  });

  it('binds torsion and enabled serviceability to revision identity', () => {
    const state = useDesignStore.getState();
    const baseline = createQuickDesignIdentity(state.inputs, state.length, 1);
    const torsion = createQuickDesignIdentity({ ...state.inputs, torsion: 10 }, state.length, 1);
    const service = createQuickDesignIdentity({
      ...state.inputs,
      include_serviceability: true,
      span_mm: 5000,
      crack_width_params: {
        exposure_class: 'moderate',
        acr_mm: 40,
        cmin_mm: 25,
        h_mm: 500,
        x_mm: 150,
        fs_service_nmm2: 180,
      },
    }, state.length, 1);

    expect(torsion.inputHash).not.toBe(baseline.inputHash);
    expect(service.inputHash).not.toBe(baseline.inputHash);
  });

  it('withholds export eligibility when identity evidence is missing', async () => {
    const response = designResult('missing-evidence');
    response.evidence = null;
    mocks.designBeam.mockResolvedValue(response);
    const { result } = renderHook(() => useLiveDesign({ autoDesign: false }));

    act(() => {
      result.current.actions.triggerDesign();
    });
    await waitFor(() => expect(result.current.state.resultLifecycle).toBe('current'));
    expect(result.current.state.exportEligible).toBe(false);
  });
});
