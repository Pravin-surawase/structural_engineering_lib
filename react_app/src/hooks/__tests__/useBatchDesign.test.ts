/**
 * Tests for useBatchDesign hook — SSE-based batch design processing.
 *
 * Mocks EventSource to simulate server-sent events for batch beam design.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useBatchDesign } from '../../hooks/useBatchDesign';
import type { BeamCSVRow } from '../../types/csv';
import { useImportedBeamsStore } from '../../store/importedBeamsStore';
import { projectExportReadiness } from '../../workspace/resultRecords';
import { useWorkspaceStore } from '../../workspace/workspaceStore';

// ── EventSource Mock ────────────────────────────────────────────────
type SSEHandler = (e: MessageEvent) => void;

class MockEventSource {
  static instances: MockEventSource[] = [];

  url: string;
  listeners: Record<string, SSEHandler[]> = {};
  closed = false;

  constructor(url: string) {
    this.url = url;
    MockEventSource.instances.push(this);
  }

  addEventListener(event: string, handler: SSEHandler) {
    if (!this.listeners[event]) this.listeners[event] = [];
    this.listeners[event].push(handler);
  }

  close() {
    this.closed = true;
  }

  // Test helper — emit a named SSE event
  emit(event: string, data: unknown) {
    const handlers = this.listeners[event] ?? [];
    const messageEvent = { data: JSON.stringify(data) } as MessageEvent;
    handlers.forEach(h => h(messageEvent));
  }

  // Emit a connection error (no data property)
  emitConnectionError() {
    const handlers = this.listeners['error'] ?? [];
    handlers.forEach(h => h({} as MessageEvent));
  }
}

const mockBeam = (id: string): BeamCSVRow =>
  ({
    id,
    story: 'GF',
    b: 300,
    D: 500,
    span: 5000,
    fck: 25,
    fy: 500,
    cover: 40,
    d_mm: 450,
    Mu_mid: 100,
    Vu_start: 50,
  }) as BeamCSVRow;

const evidence = {
  artifact_schema: 'structural_lib.beam-evidence',
  artifact_schema_version: '1.0',
  library_version: '0.23.0',
  library_content_identity: 'library-content-id',
  code_edition: 'IS 456:2000',
  code_amendment_identity: 'not-declared-in-artifact',
  amendment_applicability: 'REVIEWED_NO_CALCULATION_CHANGE',
  amendment_applicability_review_id: 'review-id',
  controlled_source_ids: ['source-id'],
  controlled_source_basis_hash: 'source-basis-hash',
  capability_id: 'design_beam_is456',
  support_status: 'SUPPORTED' as const,
  unit_system: 'IS456',
  explicit_units: { length: 'mm' },
  normalized_input_hash: 'server-sha256',
  provenance_hash: 'provenance-sha256',
  source_metadata: {},
  calculation_identity: 'calculation-identity',
  replay_receipt: {},
  replay_receipt_hash: 'replay-receipt-sha256',
  governing_check: 'flexure',
  exact_utilization: 0.78,
  margin: 0.22,
  status: 'PASS' as const,
  generated_at: '2026-08-10T00:00:00.000Z',
  qualified_review_required: true,
  qualified_review_requirement: 'Qualified review required.',
};

describe('useBatchDesign', () => {
  beforeEach(() => {
    MockEventSource.instances = [];
    vi.stubGlobal('EventSource', MockEventSource);
    useWorkspaceStore.getState().reset();
    useImportedBeamsStore.setState({ beams: [], selectedId: null, selectedFloor: null });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('starts with idle state', () => {
    const { result } = renderHook(() => useBatchDesign());

    expect(result.current.status).toBe('idle');
    expect(result.current.progress.completed).toBe(0);
    expect(result.current.results).toEqual([]);
    expect(result.current.jobId).toBeNull();
    expect(result.current.error).toBeNull();
  });

  it('startBatchDesign opens EventSource and sets running state', () => {
    const { result } = renderHook(() => useBatchDesign());
    const beams = [mockBeam('B1'), mockBeam('B2')];

    act(() => {
      result.current.startBatchDesign(beams);
    });

    expect(MockEventSource.instances).toHaveLength(1);
    expect(MockEventSource.instances[0].url).toContain('/stream/batch-design');
    expect(result.current.status).toBe('running');
    expect(result.current.progress.total).toBe(2);
  });

  it('sends canonical source-derived values without structural defaults', () => {
    const { result } = renderHook(() => useBatchDesign());
    const beam = {
      ...mockBeam('B-MISSING'),
      fck: undefined,
      d_mm: undefined,
      cover: undefined,
    };

    act(() => result.current.startBatchDesign([beam]));

    const url = new URL(MockEventSource.instances[0].url, 'http://localhost');
    const payload = JSON.parse(url.searchParams.get('beams') ?? '[]');
    expect(payload).toHaveLength(1);
    expect(payload[0]).toMatchObject({
      schema_version: 'project-beam-design/v1',
      member_id: 'B-MISSING',
      b_mm: 300,
      D_mm: 500,
      mu_knm: 100,
      vu_kn: 50,
      fy_nmm2: 500,
    });
    expect(payload[0]).not.toHaveProperty('fck_nmm2');
    expect(payload[0]).not.toHaveProperty('d_mm');
    expect(payload[0]).not.toHaveProperty('effective_depth_basis');
  });

  it('posts a maintained-size batch instead of placing it in the request URL', () => {
    const fetchMock = vi.fn<
      (input: RequestInfo | URL, init?: RequestInit) => Promise<Response>
    >(() => new Promise<Response>(() => {}));
    vi.stubGlobal('fetch', fetchMock);
    const { result } = renderHook(() => useBatchDesign());
    const beams = Array.from({ length: 153 }, (_, index) => mockBeam(`B-${index}`));

    act(() => {
      result.current.startBatchDesign(beams);
    });

    expect(MockEventSource.instances).toHaveLength(0);
    expect(fetchMock).toHaveBeenCalledOnce();
    const [url, options] = fetchMock.mock.calls[0];
    expect(String(url)).toMatch(/\/stream\/batch-design$/);
    expect(options).toMatchObject({ method: 'POST' });
    expect(JSON.parse(String(options?.body))).toHaveLength(153);
  });

  it('handles start event with job_id', () => {
    const { result } = renderHook(() => useBatchDesign());

    act(() => {
      result.current.startBatchDesign([mockBeam('B1')]);
    });

    const es = MockEventSource.instances[0];
    act(() => {
      es.emit('start', { job_id: 'job-123' });
    });

    expect(result.current.jobId).toBe('job-123');
  });

  it('handles design_result events', () => {
    const { result } = renderHook(() => useBatchDesign());

    act(() => {
      result.current.startBatchDesign([mockBeam('B1'), mockBeam('B2')]);
    });

    const es = MockEventSource.instances[0];
    act(() => {
      es.emit('design_result', {
        beam_id: 'B1',
        design_succeeded: true,
        is_safe: true,
        status: 'PASS',
        flexure: { ast_required: 850, asc_required: 0, mu_lim: 165, xu: 120, is_safe: true },
        shear: { tau_v: 0.65, tau_c: 0.48, tau_c_max: 3.1, vus: 42, stirrup_spacing: 150, is_safe: true },
        utilization_ratio: 0.78,
      });
    });

    expect(result.current.results).toHaveLength(1);
    expect(result.current.results[0].beam_id).toBe('B1');
    expect(result.current.results[0]).toMatchObject({
      design_succeeded: true,
      is_safe: true,
      status: 'PASS',
    });
  });

  it('preserves a completed unsafe design as FAIL', () => {
    const { result } = renderHook(() => useBatchDesign());

    act(() => {
      result.current.startBatchDesign([mockBeam('B-UNSAFE-SHEAR')]);
    });

    const es = MockEventSource.instances[0];
    act(() => {
      es.emit('design_result', {
        beam_id: 'B-UNSAFE-SHEAR',
        design_succeeded: true,
        is_safe: false,
        status: 'FAIL',
        flexure: { ast_required: 554, asc_required: 0, mu_lim: 205, xu: 89, is_safe: true },
        shear: { tau_v: 4.42, tau_c: 0, tau_c_max: 3.1, vus: 0, stirrup_spacing: 0, is_safe: false },
        utilization_ratio: 1.43,
      });
    });

    expect(result.current.results[0]).toMatchObject({
      design_succeeded: true,
      is_safe: false,
      status: 'FAIL',
      shear: { tau_v: 4.42, tau_c_max: 3.1, is_safe: false },
    });
  });

  it('preserves a server BLOCKED result instead of relabeling it HOLD', () => {
    const beam = { ...mockBeam('B-BLOCKED'), source_id: 'B-BLOCKED' };
    useImportedBeamsStore.getState().setBeams([beam]);
    const { result } = renderHook(() => useBatchDesign());

    act(() => result.current.startBatchDesign([beam]));
    act(() => {
      MockEventSource.instances[0].emit('design_result', {
        beam_id: 'B-BLOCKED',
        design_succeeded: false,
        is_safe: false,
        status: 'BLOCKED',
        issues: [{ code: 'PROJECT_BEAM_REQUIRED_FIELD', message: 'vu_kn is required' }],
      });
    });

    expect(result.current.results[0]).toMatchObject({
      status: 'BLOCKED',
      error: 'The batch result did not include a traceable evidence identity.',
    });
    expect(useWorkspaceStore.getState().snapshot!.members[0].result).toMatchObject({
      lifecycle: 'unsupported',
      decision: 'HOLD',
    });
    expect(useImportedBeamsStore.getState().beams[0]).toMatchObject({
      status: 'pending',
      is_valid: false,
    });
  });

  it('handles progress events', () => {
    const { result } = renderHook(() => useBatchDesign());

    act(() => {
      result.current.startBatchDesign([mockBeam('B1'), mockBeam('B2')]);
    });

    const es = MockEventSource.instances[0];
    act(() => {
      es.emit('progress', { completed: 1, total: 2, failed: 0, percent: 50 });
    });

    expect(result.current.progress).toEqual({
      completed: 1,
      total: 2,
      failed: 0,
      percent: 50,
    });
  });

  it('handles complete event and closes connection', () => {
    const { result } = renderHook(() => useBatchDesign());

    act(() => {
      result.current.startBatchDesign([mockBeam('B1')]);
    });

    const es = MockEventSource.instances[0];
    act(() => {
      es.emit('complete', { duration_seconds: 2.5 });
    });

    expect(result.current.status).toBe('complete');
    expect(result.current.duration).toBe(2.5);
    expect(es.closed).toBe(true);
  });

  it('handles error event with beam data', () => {
    const { result } = renderHook(() => useBatchDesign());

    act(() => {
      result.current.startBatchDesign([mockBeam('B1')]);
    });

    const es = MockEventSource.instances[0];
    act(() => {
      es.emit('error', { beam_id: 'B1', message: 'Invalid dimensions' });
    });

    expect(result.current.results).toHaveLength(1);
    expect(result.current.results[0]).toMatchObject({
      design_succeeded: false,
      is_safe: false,
      status: 'HOLD',
    });
    expect(result.current.results[0].error).toBe('Invalid dimensions');
  });

  it('handles connection error (no data)', () => {
    const { result } = renderHook(() => useBatchDesign());

    act(() => {
      result.current.startBatchDesign([mockBeam('B1')]);
    });

    const es = MockEventSource.instances[0];
    act(() => {
      es.emitConnectionError();
    });

    expect(result.current.status).toBe('error');
    expect(result.current.error).toBe('Connection to server lost');
    expect(es.closed).toBe(true);
  });

  it('cancel closes EventSource and resets to idle', () => {
    const { result } = renderHook(() => useBatchDesign());

    act(() => {
      result.current.startBatchDesign([mockBeam('B1')]);
    });

    const es = MockEventSource.instances[0];

    act(() => {
      result.current.cancel();
    });

    expect(es.closed).toBe(true);
    expect(result.current.status).toBe('idle');
  });

  it('starting new batch closes previous EventSource', () => {
    const { result } = renderHook(() => useBatchDesign());

    act(() => {
      result.current.startBatchDesign([mockBeam('B1')]);
    });

    const firstES = MockEventSource.instances[0];

    act(() => {
      result.current.startBatchDesign([mockBeam('B2')]);
    });

    expect(firstES.closed).toBe(true);
    expect(MockEventSource.instances).toHaveLength(2);
  });

  it('stores evidence only when the exact workspace revision is still current', () => {
    const beam = { ...mockBeam('Label B1'), source_id: 'ETABS-101' };
    useImportedBeamsStore.getState().setBeams([beam]);
    const { result } = renderHook(() => useBatchDesign());

    act(() => result.current.startBatchDesign([beam]));
    const es = MockEventSource.instances[0];
    act(() => {
      es.emit('start', { job_id: 'job-123' });
      es.emit('design_result', {
        beam_id: 'ETABS-101',
        design_succeeded: true,
        is_safe: true,
        status: 'PASS',
        flexure: { ast_required: 850, asc_required: 0, mu_lim: 165, xu: 120, is_safe: true },
        shear: { tau_v: 0.65, tau_c: 0.48, tau_c_max: 3.1, vus: 42, stirrup_spacing: 150, is_safe: true },
        utilization_ratio: 0.78,
        evidence,
      });
    });

    const snapshot = useWorkspaceStore.getState().snapshot!;
    expect(snapshot.members[0].result).toMatchObject({
      lifecycle: 'current',
      runId: 'job-123',
      calculationIdentity: 'calculation-identity',
      libraryVersion: '0.23.0',
      decision: 'PASS',
      supportStatus: 'SUPPORTED',
    });
    expect(projectExportReadiness(snapshot).eligible).toBe(true);
    expect(useImportedBeamsStore.getState().beams[0]).toMatchObject({
      source_id: 'ETABS-101',
      ast_required: 850,
      status: 'pass',
    });
  });

  it('rejects a late result after the member input revision changes', () => {
    const beam = { ...mockBeam('Label B1'), source_id: 'ETABS-101' };
    useImportedBeamsStore.getState().setBeams([beam]);
    const { result } = renderHook(() => useBatchDesign());

    act(() => result.current.startBatchDesign([beam]));
    const es = MockEventSource.instances[0];
    const member = useWorkspaceStore.getState().snapshot!.members[0];
    act(() => {
      useWorkspaceStore.getState().updateMemberInputs(
        member.memberId,
        { ...member.inputs, widthMm: 350 },
        'changed-input-hash',
      );
      es.emit('start', { job_id: 'old-job' });
      es.emit('design_result', {
        beam_id: 'ETABS-101',
        design_succeeded: true,
        is_safe: true,
        status: 'PASS',
        utilization_ratio: 0.78,
        evidence,
      });
    });

    expect(result.current.results).toEqual([]);
    expect(useWorkspaceStore.getState().snapshot!.members[0].result?.lifecycle).toBe('stale');
    expect(projectExportReadiness(useWorkspaceStore.getState().snapshot).eligible).toBe(false);
  });

  it('keeps a completed result on HOLD when canonical evidence is missing', () => {
    const beam = { ...mockBeam('Label B1'), source_id: 'ETABS-101' };
    useImportedBeamsStore.getState().setBeams([beam]);
    const { result } = renderHook(() => useBatchDesign());

    act(() => result.current.startBatchDesign([beam]));
    act(() => {
      MockEventSource.instances[0].emit('design_result', {
        beam_id: 'ETABS-101',
        design_succeeded: true,
        is_safe: true,
        status: 'PASS',
      });
    });

    const snapshot = useWorkspaceStore.getState().snapshot!;
    expect(snapshot.members[0].result).toMatchObject({
      lifecycle: 'unsupported',
      decision: 'HOLD',
      supportStatus: 'HELD',
      error: { code: 'EVIDENCE_MISSING' },
    });
    expect(result.current.results[0]).toMatchObject({ status: 'HOLD' });
    expect(useImportedBeamsStore.getState().beams[0]).toMatchObject({
      status: 'pending',
      is_valid: false,
    });
    expect(projectExportReadiness(snapshot).eligible).toBe(false);
  });
});
