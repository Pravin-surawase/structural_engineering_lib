/**
 * Tests for useBatchDesign hook — SSE-based batch design processing.
 *
 * Mocks EventSource to simulate server-sent events for batch beam design.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useBatchDesign } from '../../hooks/useBatchDesign';
import type { BeamCSVRow } from '../../types/csv';

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
  }) as BeamCSVRow;

describe('useBatchDesign', () => {
  beforeEach(() => {
    MockEventSource.instances = [];
    vi.stubGlobal('EventSource', MockEventSource);
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
      status: 'FAIL',
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
});
