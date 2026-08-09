/**
 * useBatchDesign Hook
 *
 * Connects to the SSE /stream/batch-design endpoint to run batch design
 * on multiple beams with live progress tracking.
 */
import { useState, useCallback, useRef } from 'react';
import { toast } from '../components/ui/Toast';
import type { BeamCSVRow } from '../types/csv';

import { API_BASE_URL } from '../config';

export interface BatchProgress {
  completed: number;
  total: number;
  failed: number;
  percent: number;
}

export interface BatchResult {
  beam_id: string;
  design_succeeded: boolean;
  is_safe: boolean;
  status: 'PASS' | 'FAIL';
  flexure?: {
    ast_required: number;
    asc_required: number;
    mu_lim: number;
    xu: number;
    is_safe: boolean;
  };
  shear?: {
    tau_v: number;
    tau_c: number;
    tau_c_max: number;
    vus: number;
    stirrup_spacing: number;
    is_safe: boolean;
  };
  utilization_ratio?: number;
  utilizations?: Record<string, number>;
  failed_checks?: string[];
  remarks?: string;
  error?: string;
}

type ServerBatchResult = BatchResult & {
  input?: { beam_id?: string };
  message?: string;
};

export type BatchStatus = 'idle' | 'running' | 'complete' | 'error';

export interface BatchDesignState {
  status: BatchStatus;
  progress: BatchProgress;
  results: BatchResult[];
  jobId: string | null;
  error: string | null;
  duration: number | null;
}

export function useBatchDesign() {
  const [state, setState] = useState<BatchDesignState>({
    status: 'idle',
    progress: { completed: 0, total: 0, failed: 0, percent: 0 },
    results: [],
    jobId: null,
    error: null,
    duration: null,
  });

  const eventSourceRef = useRef<EventSource | null>(null);

  const cancel = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setState(prev => ({ ...prev, status: 'idle' }));
  }, []);

  const startBatchDesign = useCallback((beams: BeamCSVRow[]) => {
    // Close any existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    // Map BeamCSVRow to the format the API expects
    const beamParams = beams.map(b => ({
      beam_id: b.id,
      width: b.b,
      depth: b.D,
      moment: b.mu_envelope ?? b.Mu_mid ?? 100,
      shear: b.vu_envelope ?? b.Vu_start ?? 50,
      fck: b.fck ?? 25,
      fy: b.fy ?? 500,
      cover: b.cover ?? 40,
      span: b.span,
    }));

    const beamsJson = encodeURIComponent(JSON.stringify(beamParams));
    const url = `${API_BASE_URL}/stream/batch-design?beams=${beamsJson}`;

    setState({
      status: 'running',
      progress: { completed: 0, total: beams.length, failed: 0, percent: 0 },
      results: [],
      jobId: null,
      error: null,
      duration: null,
    });

    const es = new EventSource(url);
    eventSourceRef.current = es;

    es.addEventListener('start', (e: MessageEvent) => {
      const data = JSON.parse(e.data);
      setState(prev => ({ ...prev, jobId: data.job_id }));
    });

    es.addEventListener('design_result', (e: MessageEvent) => {
      const data = JSON.parse(e.data) as ServerBatchResult;
      const result: BatchResult = {
        beam_id: data.beam_id ?? data.input?.beam_id ?? `beam-${Date.now()}`,
        // The server owns the engineering verdict.  Do not promote a completed
        // calculation to PASS on the client.
        design_succeeded: data.design_succeeded === true,
        is_safe: data.is_safe === true,
        status: data.status === 'PASS' ? 'PASS' : 'FAIL',
        flexure: data.flexure,
        shear: data.shear,
        utilization_ratio: data.utilization_ratio,
        utilizations: data.utilizations,
        failed_checks: data.failed_checks,
        remarks: data.remarks,
      };
      setState(prev => ({
        ...prev,
        results: [...prev.results, result],
      }));
    });

    es.addEventListener('error', (e: MessageEvent) => {
      // SSE error events can be connection errors (no data) or beam errors (with data)
      if (e.data) {
        const data = JSON.parse(e.data) as ServerBatchResult;
        const result: BatchResult = {
          beam_id: data.beam_id ?? data.input?.beam_id ?? `error-${Date.now()}`,
          design_succeeded: false,
          is_safe: false,
          status: 'FAIL',
          error: data.message ?? 'Design failed',
        };
        setState(prev => ({
          ...prev,
          results: [...prev.results, result],
        }));
      } else {
        // Connection error
        es.close();
        eventSourceRef.current = null;
        const errorMsg = 'Connection to server lost';
        setState(prev => ({
          ...prev,
          status: 'error',
          error: errorMsg,
        }));
        toast.error('Batch Design Failed', errorMsg);
      }
    });

    es.addEventListener('progress', (e: MessageEvent) => {
      const data = JSON.parse(e.data);
      setState(prev => ({
        ...prev,
        progress: {
          completed: data.completed,
          total: data.total,
          failed: data.failed,
          percent: data.percent,
        },
      }));
    });

    es.addEventListener('complete', (e: MessageEvent) => {
      const data = JSON.parse(e.data);
      es.close();
      eventSourceRef.current = null;
      setState(prev => ({
        ...prev,
        status: 'complete',
        duration: data.duration_seconds,
      }));
    });
  }, []);

  return {
    ...state,
    startBatchDesign,
    cancel,
  };
}
