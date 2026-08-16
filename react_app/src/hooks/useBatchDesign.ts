/** Revision-bound SSE batch design with explicit evidence lifecycles. */
import { useCallback, useEffect, useRef, useState } from 'react';
import type { EvidenceEnvelope } from '../api/client';
import { toast } from '../components/ui/Toast';
import { API_BASE_URL } from '../config';
import { useImportedBeamsStore } from '../store/importedBeamsStore';
import type { BeamCSVRow } from '../types/csv';
import {
  applyBatchResultToBeam,
  completedBatchRecord,
  failedBatchRecord,
} from '../workspace/resultRecords';
import type { EvidenceRecord } from '../workspace/types';
import { useWorkspaceStore } from '../workspace/workspaceStore';

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
  status: 'PASS' | 'FAIL' | 'HOLD';
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
  evidence?: EvidenceEnvelope;
}

type ServerBatchResult = BatchResult & {
  input?: {
    member_id?: string;
    beam_id?: string;
    source_metadata?: {
      request_id?: string;
      project_revision?: number;
      input_revision?: number;
    };
  };
  issues?: Array<{ code: string; message: string }>;
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

interface ActiveBatchRun {
  token: string;
  localRunId: string;
  serverJobId: string | null;
  projectId: string | null;
  projectRevision: number | null;
  pendingByMember: Map<string, EvidenceRecord>;
  memberByResponseId: Map<string, string>;
  receivedMemberIds: Set<string>;
}

const SAFE_EVENT_SOURCE_URL_LENGTH = 7_000;

type BatchStreamHandler = (event: MessageEvent) => void;

/** EventSource-compatible POST transport for payloads too large for a request URL. */
class PostBatchEventStream {
  private readonly controller = new AbortController();
  private readonly listeners = new Map<string, Set<BatchStreamHandler>>();
  private closed = false;

  constructor(beams: unknown[]) {
    void this.connect(beams);
  }

  addEventListener(event: string, handler: BatchStreamHandler): void {
    const handlers = this.listeners.get(event) ?? new Set<BatchStreamHandler>();
    handlers.add(handler);
    this.listeners.set(event, handlers);
  }

  close(): void {
    this.closed = true;
    this.controller.abort();
  }

  private dispatch(event: string, data = ''): void {
    for (const handler of this.listeners.get(event) ?? []) {
      handler({ data } as MessageEvent);
    }
  }

  private consumeBlock(block: string): void {
    let event = 'message';
    const data: string[] = [];
    for (const line of block.split('\n')) {
      if (line.startsWith('event:')) event = line.slice(6).trim();
      if (line.startsWith('data:')) data.push(line.slice(5).trimStart());
    }
    if (data.length > 0) this.dispatch(event, data.join('\n'));
  }

  private async connect(beams: unknown[]): Promise<void> {
    try {
      const response = await fetch(`${API_BASE_URL}/stream/batch-design`, {
        method: 'POST',
        headers: {
          Accept: 'text/event-stream',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(beams),
        signal: this.controller.signal,
      });
      if (!response.ok || !response.body) throw new Error(`Batch stream returned ${response.status}`);

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      while (!this.closed) {
        const { done, value } = await reader.read();
        buffer = (buffer + decoder.decode(value, { stream: !done })).replaceAll('\r\n', '\n');
        let boundary = buffer.indexOf('\n\n');
        while (boundary >= 0) {
          this.consumeBlock(buffer.slice(0, boundary));
          buffer = buffer.slice(boundary + 2);
          boundary = buffer.indexOf('\n\n');
        }
        if (done) break;
      }
      if (!this.closed && buffer.trim()) this.consumeBlock(buffer.trim());
    } catch (error) {
      if (!this.closed && !(error instanceof DOMException && error.name === 'AbortError')) {
        this.dispatch('error');
      }
    }
  }
}

function uniqueId(prefix: string): string {
  return `${prefix}-${crypto.randomUUID()}`;
}

function runId(run: ActiveBatchRun): string {
  return run.serverJobId ?? run.localRunId;
}

function updateCompatibilityBeam(
  memberId: string,
  update: (beam: BeamCSVRow) => BeamCSVRow,
): void {
  useImportedBeamsStore.setState((state) => ({
    beams: state.beams.map((beam) => (
      (beam.source_id ?? beam.id) === memberId ? update(beam) : beam
    )),
  }));
}

function settleUnreceived(
  run: ActiveBatchRun,
  code: string,
  message: string,
  lifecycle: 'error' | 'not_evaluated',
): BatchResult[] {
  const workspace = useWorkspaceStore.getState();
  const heldResults: BatchResult[] = [];
  for (const [memberId, pending] of run.pendingByMember) {
    if (run.receivedMemberIds.has(memberId)) continue;
    const record = failedBatchRecord(pending, runId(run), code, message, lifecycle);
    if (workspace.applyMemberRecord(memberId, 'result', record)) {
      updateCompatibilityBeam(memberId, (beam) => ({
        ...beam,
        status: 'pending',
        is_valid: false,
        remarks: [message],
      }));
      heldResults.push({
        beam_id: memberId,
        design_succeeded: false,
        is_safe: false,
        status: 'HOLD',
        error: message,
      });
    }
  }
  return heldResults;
}

function normalizedResult(data: ServerBatchResult): BatchResult | null {
  const beamId = data.beam_id ?? data.input?.member_id;
  if (!beamId) return null;
  const status = data.status === 'PASS'
    ? 'PASS'
    : data.status === 'FAIL'
      ? 'FAIL'
      : 'HOLD';
  return {
    beam_id: beamId,
    design_succeeded: data.design_succeeded === true,
    is_safe: data.is_safe === true,
    status,
    flexure: data.flexure,
    shear: data.shear,
    utilization_ratio: data.utilization_ratio,
    utilizations: data.utilizations,
    failed_checks: data.failed_checks,
    remarks: data.remarks,
    error: data.error ?? data.issues?.[0]?.message,
    evidence: data.evidence,
  };
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

  const eventSourceRef = useRef<{ close: () => void } | null>(null);
  const activeRunRef = useRef<ActiveBatchRun | null>(null);

  const closeActiveRun = useCallback((
    code: string,
    message: string,
    lifecycle: 'error' | 'not_evaluated',
  ) => {
    eventSourceRef.current?.close();
    eventSourceRef.current = null;
    const run = activeRunRef.current;
    if (run) settleUnreceived(run, code, message, lifecycle);
    activeRunRef.current = null;
  }, []);

  const cancel = useCallback(() => {
    closeActiveRun(
      'BATCH_CANCELLED',
      'Batch design was cancelled before this member was evaluated.',
      'not_evaluated',
    );
    setState((previous) => ({ ...previous, status: 'idle' }));
  }, [closeActiveRun]);

  const startBatchDesign = useCallback((beams: BeamCSVRow[]) => {
    closeActiveRun(
      'BATCH_SUPERSEDED',
      'A newer batch design superseded this request.',
      'not_evaluated',
    );

    const workspace = useWorkspaceStore.getState();
    const snapshot = workspace.snapshot;
    const token = uniqueId('batch-token');
    const localRunId = uniqueId('batch-run');
    const pendingByMember = new Map<string, EvidenceRecord>();
    const memberByResponseId = new Map<string, string>();
    const receivedMemberIds = new Set<string>();
    const heldResults: BatchResult[] = [];

    const beamParams = beams.map((beam) => {
      const responseId = beam.source_id ?? beam.id;
      const member = snapshot?.members.find((candidate) => candidate.memberId === responseId);
      const requestId = uniqueId('batch-request');
      const pending = member
        ? workspace.beginMemberRequest(member.memberId, 'result', requestId)
        : null;
      if (member && pending) {
        pendingByMember.set(member.memberId, pending);
        memberByResponseId.set(responseId, member.memberId);
        updateCompatibilityBeam(member.memberId, (current) => ({
          ...current,
          status: 'designing',
          is_valid: false,
        }));
      }
      const depth = beam.d_mm !== undefined
        ? { d_mm: beam.d_mm }
        : beam.cover !== undefined
          && beam.stirrup_diameter_mm !== undefined
          && beam.tension_bar_diameter_mm !== undefined
          ? {
              effective_depth_basis: {
                clear_cover_mm: beam.cover,
                stirrup_diameter_mm: beam.stirrup_diameter_mm,
                tension_bar_diameter_mm: beam.tension_bar_diameter_mm,
              },
            }
          : {};
      return {
        schema_version: 'project-beam-design/v1',
        member_id: responseId,
        b_mm: beam.b,
        D_mm: beam.D,
        mu_knm: beam.mu_envelope ?? beam.Mu_mid,
        vu_kn: beam.vu_envelope ?? beam.Vu_start,
        fck_nmm2: beam.fck,
        fy_nmm2: beam.fy,
        ...depth,
        source_metadata: {
          ...beam.source_metadata,
          request_id: requestId,
          project_id: snapshot?.projectId,
          project_revision: snapshot?.projectRevision,
          input_revision: member?.inputRevision,
          span_mm: beam.span,
        },
      };
    });

    const run: ActiveBatchRun = {
      token,
      localRunId,
      serverJobId: null,
      projectId: snapshot?.projectId ?? null,
      projectRevision: snapshot?.projectRevision ?? null,
      pendingByMember,
      memberByResponseId,
      receivedMemberIds,
    };
    if (snapshot) workspace.setStage('design');

    if (beamParams.length === 0) {
      if (snapshot) workspace.setStage('results');
      setState({
        status: 'complete',
        progress: { completed: 0, total: 0, failed: 0, percent: 100 },
        results: heldResults,
        jobId: localRunId,
        error: null,
        duration: 0,
      });
      return;
    }
    activeRunRef.current = run;

    const beamsJson = encodeURIComponent(JSON.stringify(beamParams));
    const eventSourceUrlLength = `${API_BASE_URL}/stream/batch-design?beams=${beamsJson}`.length;
    const es = eventSourceUrlLength <= SAFE_EVENT_SOURCE_URL_LENGTH
      ? new EventSource(`${API_BASE_URL}/stream/batch-design?beams=${beamsJson}`)
      : new PostBatchEventStream(beamParams);
    eventSourceRef.current = es;

    setState({
      status: 'running',
      progress: { completed: 0, total: beamParams.length, failed: 0, percent: 0 },
      results: heldResults,
      jobId: null,
      error: null,
      duration: null,
    });

    const isActive = () => activeRunRef.current?.token === token && eventSourceRef.current === es;

    es.addEventListener('start', (event: MessageEvent) => {
      if (!isActive()) return;
      const data = JSON.parse(event.data) as { job_id: string };
      run.serverJobId = data.job_id;
      setState((previous) => ({ ...previous, jobId: data.job_id }));
    });

    es.addEventListener('design_result', (event: MessageEvent) => {
      if (!isActive()) return;
      const data = JSON.parse(event.data) as ServerBatchResult;
      const result = normalizedResult(data);
      if (!result) {
        setState((previous) => ({ ...previous, error: 'A batch result was missing its source identity.' }));
        return;
      }
      const memberId = run.memberByResponseId.get(result.beam_id);
      const pending = memberId ? run.pendingByMember.get(memberId) : undefined;
      const responseMetadata = data.input?.source_metadata;
      if (pending && responseMetadata?.request_id && responseMetadata.request_id !== pending.requestId) return;
      if (
        pending
        && responseMetadata?.project_revision != null
        && responseMetadata.project_revision !== pending.projectRevision
      ) return;
      if (
        pending
        && responseMetadata?.input_revision != null
        && responseMetadata.input_revision !== pending.inputRevision
      ) return;

      let accepted = true;
      let presentedResult = result;
      if (memberId && pending) {
        const record = completedBatchRecord(pending, result, runId(run));
        accepted = useWorkspaceStore.getState().applyMemberRecord(memberId, 'result', record);
        if (accepted) {
          run.receivedMemberIds.add(memberId);
          if (record.lifecycle === 'current') {
            updateCompatibilityBeam(memberId, (beam) => applyBatchResultToBeam(beam, result));
          } else {
            const message = record.error?.message ?? 'This result is outside the supported evidence boundary.';
            presentedResult = { ...result, status: 'HOLD', error: message };
            updateCompatibilityBeam(memberId, (beam) => ({
              ...beam,
              status: 'pending',
              is_valid: false,
              remarks: [message],
            }));
          }
        }
      }
      if (!accepted) return;
      setState((previous) => ({ ...previous, results: [...previous.results, presentedResult] }));
    });

    es.addEventListener('error', (event: MessageEvent) => {
      if (!isActive()) return;
      if (event.data) {
        const data = JSON.parse(event.data) as ServerBatchResult;
        const responseId = data.beam_id ?? data.input?.beam_id;
        const memberId = responseId ? run.memberByResponseId.get(responseId) : undefined;
        const pending = memberId ? run.pendingByMember.get(memberId) : undefined;
        const message = data.message ?? 'Design failed';
        let accepted = true;
        if (memberId && pending) {
          const record = failedBatchRecord(
            pending,
            runId(run),
            'BATCH_MEMBER_FAILED',
            message,
          );
          accepted = useWorkspaceStore.getState().applyMemberRecord(memberId, 'result', record);
          if (accepted) {
            run.receivedMemberIds.add(memberId);
            updateCompatibilityBeam(memberId, (beam) => ({
              ...beam,
              status: 'fail',
              is_valid: false,
              remarks: [message],
            }));
          }
        }
        if (!accepted) return;
        setState((previous) => ({
          ...previous,
          results: [...previous.results, {
            beam_id: responseId ?? 'unidentified-member',
            design_succeeded: false,
            is_safe: false,
            status: 'HOLD',
            error: message,
          }],
        }));
        return;
      }

      const heldResults = settleUnreceived(
        run,
        'BATCH_CONNECTION_LOST',
        'Connection to the batch design service was lost.',
        'error',
      );
      es.close();
      eventSourceRef.current = null;
      activeRunRef.current = null;
      const errorMessage = 'Connection to server lost';
      setState((previous) => ({
        ...previous,
        status: 'error',
        error: errorMessage,
        results: [...previous.results, ...heldResults],
      }));
      toast.error('Batch Design Failed', errorMessage);
    });

    es.addEventListener('progress', (event: MessageEvent) => {
      if (!isActive()) return;
      const data = JSON.parse(event.data) as BatchProgress;
      setState((previous) => ({
        ...previous,
        progress: {
          completed: data.completed,
          total: data.total,
          failed: data.failed,
          percent: data.percent,
        },
      }));
    });

    es.addEventListener('complete', (event: MessageEvent) => {
      if (!isActive()) return;
      const data = JSON.parse(event.data) as { duration_seconds: number | null };
      const heldResults = settleUnreceived(
        run,
        'BATCH_RESULT_MISSING',
        'The batch completed without a result for this member.',
        'not_evaluated',
      );
      es.close();
      eventSourceRef.current = null;
      activeRunRef.current = null;
      const current = useWorkspaceStore.getState().snapshot;
      if (
        current
        && current.projectId === run.projectId
        && current.projectRevision === run.projectRevision
      ) {
        useWorkspaceStore.getState().setStage('results');
      }
      setState((previous) => ({
        ...previous,
        status: 'complete',
        duration: data.duration_seconds,
        results: [...previous.results, ...heldResults],
      }));
    });
  }, [closeActiveRun]);

  useEffect(() => () => {
    eventSourceRef.current?.close();
    if (activeRunRef.current) {
      settleUnreceived(
        activeRunRef.current,
        'BATCH_VIEW_CLOSED',
        'The batch view closed before this member was evaluated.',
        'not_evaluated',
      );
    }
    activeRunRef.current = null;
  }, []);

  return { ...state, startBatchDesign, cancel };
}
