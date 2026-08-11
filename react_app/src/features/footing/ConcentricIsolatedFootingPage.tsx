import { useEffect, useRef, useState } from 'react';
import { AlertTriangle, Loader2 } from 'lucide-react';
import { ResultLifecycleBadge } from '../../components/workbench/ResultLifecycleBadge';
import { WorkbenchHeader } from '../../components/workbench/WorkbenchHeader';
import { WorkbenchPanel } from '../../components/workbench/WorkbenchPanel';
import { WorkbenchShell } from '../../components/workbench/WorkbenchShell';
import type { ResultLifecycle } from '../../workspace/types';
import { designConcentricIsolatedFooting } from './client';
import {
  createFootingRequest,
  INITIAL_FOOTING_DRAFT,
  updateFootingDraft,
  validateFootingDraft,
  type FootingDraft,
} from './draft';
import { FootingInputForm } from './FootingInputForm';
import { FootingResults } from './FootingResults';
import type { ConcentricIsolatedFootingResponse } from './types';

export function ConcentricIsolatedFootingPage() {
  const [draft, setDraft] = useState(INITIAL_FOOTING_DRAFT);
  const [result, setResult] = useState<ConcentricIsolatedFootingResponse | null>(null);
  const [lifecycle, setLifecycle] = useState<ResultLifecycle>('not_evaluated');
  const [error, setError] = useState<string | null>(null);
  const revisionRef = useRef(0);
  const activeRequestRef = useRef<AbortController | null>(null);
  const issues = validateFootingDraft(draft);
  const requestPending = lifecycle === 'pending';
  const canRun = issues.length === 0 && !requestPending;

  useEffect(() => {
    const requestRef = activeRequestRef;
    return () => requestRef.current?.abort();
  }, []);

  const editDraft = (
    key: keyof FootingDraft,
    value: FootingDraft[keyof FootingDraft],
  ) => {
    revisionRef.current += 1;
    activeRequestRef.current?.abort();
    activeRequestRef.current = null;
    setDraft((current) => updateFootingDraft(current, key, value));
    setLifecycle(result ? 'stale' : 'not_evaluated');
    setError(null);
  };

  const runDesign = async () => {
    const request = createFootingRequest(draft);
    if (!request) {
      setLifecycle('error');
      setError(issues[0] ?? 'Review the footing inputs before running the design.');
      return;
    }

    const requestRevision = revisionRef.current;
    const controller = new AbortController();
    activeRequestRef.current?.abort();
    activeRequestRef.current = controller;
    setLifecycle('pending');
    setError(null);

    try {
      const response = await designConcentricIsolatedFooting(request, controller.signal);
      if (!controller.signal.aborted && requestRevision === revisionRef.current) {
        setResult(response);
        setLifecycle('current');
      }
    } catch (reason) {
      if (!controller.signal.aborted && requestRevision === revisionRef.current) {
        setResult(null);
        setLifecycle('error');
        setError(
          reason instanceof Error ? reason.message : 'Footing design request failed.',
        );
      }
    } finally {
      if (activeRequestRef.current === controller) {
        activeRequestRef.current = null;
      }
    }
  };

  return (
    <div className="h-screen pt-14">
      <WorkbenchShell
        header={(
          <WorkbenchHeader
            title="Concentric isolated footing"
            projectName="IS 456 ordinary centred square/rectangular case · server evidence is authoritative"
            primaryAction={(
              <button
                type="button"
                disabled={!canRun}
                title={canRun ? 'Run the maintained footing service' : issues[0] ?? 'Request pending'}
                className="inline-flex min-h-10 items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-40"
                onClick={() => void runDesign()}
              >
                {requestPending ? (
                  <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
                ) : null}
                {requestPending ? 'Calculating…' : result ? 'Recalculate' : 'Run footing design'}
              </button>
            )}
          >
            <ResultLifecycleBadge lifecycle={lifecycle} />
          </WorkbenchHeader>
        )}
      >
        <p className="sr-only" aria-live="polite">
          Footing request lifecycle: {lifecycle}.
        </p>
        <div className="mx-auto grid max-w-screen-2xl gap-4 p-4 pb-24 md:p-6 xl:grid-cols-[minmax(32rem,1fr)_minmax(30rem,0.9fr)]">
          <WorkbenchPanel
            title="Footing inputs"
            description="All units and approvals are explicit. Client checks improve usability; FastAPI remains the calculation authority."
          >
            <FootingInputForm
              draft={draft}
              issues={issues}
              disabled={requestPending}
              onChange={editDraft}
            />
          </WorkbenchPanel>

          <div className="space-y-4">
            <WorkbenchPanel
              title="Returned evidence"
              description="Calculation, detailing and aggregate decisions remain separate."
            >
              <div className="mb-4 flex flex-wrap items-center justify-between gap-2 rounded-xl border border-white/8 bg-zinc-950/60 p-3">
                <ResultLifecycleBadge lifecycle={lifecycle} />
                <span className="text-xs font-medium text-amber-200">
                  Report/export closeout is not enabled in D1
                </span>
              </div>

              {result ? (
                <FootingResults result={result} lifecycle={lifecycle} />
              ) : (
                <div className="rounded-xl border border-dashed border-white/10 p-6 text-center text-sm text-zinc-400">
                  Confirm the external approvals and run the maintained service to obtain
                  bounded footing evidence.
                </div>
              )}

              {result?.status === 'HOLD' ? (
                <div
                  className="mt-4 rounded-xl border border-amber-400/30 bg-amber-400/10 p-3 text-xs leading-5 text-amber-100"
                  role="alert"
                >
                  Returned HOLD: {result.hold_reasons.join(', ')
                    || result.detailing_hold_reason
                    || 'Qualified review is required.'}
                </div>
              ) : null}

              {error ? (
                <div
                  className="mt-4 flex gap-2 rounded-xl border border-rose-400/30 bg-rose-400/10 p-3 text-xs text-rose-100"
                  role="alert"
                >
                  <AlertTriangle className="h-4 w-4 shrink-0" aria-hidden="true" />
                  <span>{error}</span>
                </div>
              ) : null}
            </WorkbenchPanel>

            <WorkbenchPanel
              title="Maintained boundary"
              description="Structural pressure checks are not a geotechnical approval."
            >
              <ul className="list-disc space-y-1 pl-5 text-xs leading-5 text-zinc-400">
                <li>Allowable soil pressure is an externally approved input.</li>
                <li>Settlement, SBC derivation and soil-structure interaction are excluded.</li>
                <li>Eccentric, partial-contact, biaxial, combined and strap cases are excluded.</li>
                <li>Every returned result remains subject to qualified engineering review.</li>
              </ul>
            </WorkbenchPanel>
          </div>
        </div>
      </WorkbenchShell>
    </div>
  );
}
