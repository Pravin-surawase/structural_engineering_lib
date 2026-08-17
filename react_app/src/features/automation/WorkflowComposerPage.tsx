import { useEffect, useRef, useState } from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  Download,
  Loader2,
  Play,
  RotateCcw,
  Save,
  Square,
} from 'lucide-react';
import { WorkbenchHeader } from '../../components/workbench/WorkbenchHeader';
import { WorkbenchPanel } from '../../components/workbench/WorkbenchPanel';
import { WorkbenchShell } from '../../components/workbench/WorkbenchShell';
import { CatalogBeamInputPanel } from '../catalog/CatalogBeamInputPanel';
import type { CatalogBeamTransportName, CatalogBeamValues } from '../catalog/types';
import {
  cancelBeamWorkflow,
  fetchBeamWorkflowTemplate,
  runBeamWorkflow,
  validateBeamWorkflow,
} from './client';
import {
  parseWorkflowDraft,
  serializeWorkflowDraft,
  WORKFLOW_DRAFT_STORAGE_KEY,
} from './draft';
import type {
  WorkflowDefinition,
  WorkflowRunResult,
  WorkflowValidationResult,
} from './types';

const INITIAL_VALUES: CatalogBeamValues = {
  width: 300,
  depth: 500,
  clear_cover: 25,
  stirrup_dia_mm: 8,
  main_bar_dia_mm: 20,
  moment: 150,
  shear: 75,
  fck: 25,
  fy: 500,
};

function createRunId(): string {
  return `beam-${crypto.randomUUID()}`;
}

export function WorkflowComposerPage() {
  const [definition, setDefinition] = useState<WorkflowDefinition | null>(null);
  const [values, setValues] = useState<CatalogBeamValues>(INITIAL_VALUES);
  const [reviewAcknowledged, setReviewAcknowledged] = useState(false);
  const [validation, setValidation] = useState<WorkflowValidationResult | null>(null);
  const [result, setResult] = useState<WorkflowRunResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const runRef = useRef<{ id: string; controller: AbortController } | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    fetchBeamWorkflowTemplate(controller.signal).then(
      (template) => {
        setDefinition(template);
        setLoading(false);
      },
      (reason: unknown) => {
        if (!controller.signal.aborted) {
          setError(reason instanceof Error ? reason.message : 'Workflow template unavailable');
          setLoading(false);
        }
      },
    );
    return () => controller.abort();
  }, []);

  useEffect(() => () => {
    const active = runRef.current;
    if (!active) return;
    void cancelBeamWorkflow(active.id).catch(() => undefined);
    active.controller.abort();
  }, []);

  const updateValue = (name: CatalogBeamTransportName, value: number | undefined) => {
    setValues((current) => ({ ...current, [name]: value }));
    setValidation(null);
    setResult(null);
  };

  const preview = async () => {
    if (!definition) return;
    setError(null);
    setMessage(null);
    try {
      setValidation(await validateBeamWorkflow(definition, values));
      setMessage('Definition and bindings are valid for the approved beam workflow.');
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Workflow validation failed');
    }
  };

  const run = async () => {
    if (!definition) return;
    const id = createRunId();
    const controller = new AbortController();
    runRef.current = { id, controller };
    setRunning(true);
    setError(null);
    setMessage(null);
    try {
      const next = await runBeamWorkflow(
        definition,
        values,
        id,
        reviewAcknowledged,
        controller.signal,
      );
      setResult(next);
    } catch (reason) {
      if (!(reason instanceof DOMException && reason.name === 'AbortError')) {
        setError(reason instanceof Error ? reason.message : 'Workflow run failed');
      }
    } finally {
      if (runRef.current?.id === id) runRef.current = null;
      setRunning(false);
    }
  };

  const cancel = async () => {
    const active = runRef.current;
    if (!active) return;
    try {
      const cancellationRequested = await cancelBeamWorkflow(active.id);
      if (!cancellationRequested) {
        throw new Error('The workflow already finished before cancellation.');
      }
      active.controller.abort();
      setMessage(`Cancellation requested for ${active.id}.`);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Cancellation failed');
    }
  };

  const save = () => {
    if (!definition) return;
    localStorage.setItem(
      WORKFLOW_DRAFT_STORAGE_KEY,
      serializeWorkflowDraft({
        schema_version: '2.0',
        definition,
        inputs: values,
        review_acknowledged: reviewAcknowledged,
      }),
    );
    setMessage('Workflow draft saved locally.');
  };

  const load = () => {
    const saved = localStorage.getItem(WORKFLOW_DRAFT_STORAGE_KEY);
    if (!saved) {
      setError('No saved workflow draft is available.');
      return;
    }
    try {
      const draft = parseWorkflowDraft(saved);
      setDefinition(draft.definition);
      setValues(draft.inputs);
      setReviewAcknowledged(draft.review_acknowledged);
      setValidation(null);
      setResult(null);
      setError(null);
      setMessage('Workflow draft restored.');
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Saved workflow is invalid');
    }
  };

  const exportDraft = () => {
    if (!definition) return;
    const payload = serializeWorkflowDraft({
      schema_version: '2.0',
      definition,
      inputs: values,
      review_acknowledged: reviewAcknowledged,
    });
    const url = URL.createObjectURL(new Blob([payload], { type: 'application/json' }));
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = 'beam-workflow-v2.json';
    anchor.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="h-screen pt-14">
      <WorkbenchShell
        header={(
          <WorkbenchHeader
            title="Beam workflow composer"
            projectName="Development/test activation · one allowlisted template"
          />
        )}
      >
        <div className="mx-auto grid max-w-6xl gap-4 p-4 pb-24 md:grid-cols-[minmax(0,1fr)_22rem] md:p-6">
          <div className="space-y-4">
            <WorkbenchPanel
              title="1. Beam inputs"
              description="Catalogue names, units, defaults and bounds remain authoritative."
            >
              <CatalogBeamInputPanel
                values={values}
                onChange={updateValue}
                onUseManual={() => window.location.assign('/workbench/quick/manual')}
                disabled={running}
              />
            </WorkbenchPanel>

            <WorkbenchPanel
              title="2. Ordered workflow"
              description="The order and handler IDs cannot be edited or replaced."
            >
              {loading ? (
                <p className="flex items-center gap-2 text-sm text-zinc-400" role="status">
                  <Loader2 className="h-4 w-4 animate-spin" /> Loading approved template…
                </p>
              ) : definition ? (
                <ol className="grid gap-2 sm:grid-cols-5">
                  {definition.steps.map((step) => {
                    const stepResult = result?.steps.find((item) => item.step_id === step.step_id);
                    return (
                      <li key={step.step_id} className="rounded-lg border border-white/10 bg-white/[0.03] p-3">
                        <p className="text-xs font-semibold capitalize text-white">{step.position}. {step.step_id}</p>
                        <p className="mt-1 break-words text-[10px] text-zinc-500">{step.handler_id}</p>
                        {stepResult ? <p className="mt-2 text-[10px] font-semibold text-blue-300">{stepResult.status}</p> : null}
                      </li>
                    );
                  })}
                </ol>
              ) : null}
            </WorkbenchPanel>

            <WorkbenchPanel
              title="3. Review and run"
              description="Unsafe results always stop. Passing results stop until this review boundary is acknowledged."
            >
              <label className="flex items-start gap-2 text-sm text-zinc-300">
                <input
                  type="checkbox"
                  checked={reviewAcknowledged}
                  disabled={running}
                  onChange={(event) => setReviewAcknowledged(event.target.checked)}
                  className="mt-0.5 accent-blue-500"
                />
                I reviewed the input and understand that the output remains software evidence requiring qualified engineering review.
              </label>
              <div className="mt-4 flex flex-wrap gap-2">
                <button type="button" onClick={preview} disabled={!definition || running} className="rounded-lg border border-white/10 px-3 py-2 text-sm text-zinc-200 hover:bg-white/5 disabled:opacity-40">
                  Preview validation
                </button>
                <button type="button" onClick={run} disabled={!definition || running} className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-3 py-2 text-sm font-semibold text-white hover:bg-blue-500 disabled:opacity-40">
                  {running ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
                  Run sample
                </button>
                {running ? (
                  <button type="button" onClick={cancel} className="inline-flex items-center gap-2 rounded-lg border border-rose-400/30 px-3 py-2 text-sm text-rose-200">
                    <Square className="h-3.5 w-3.5" /> Cancel
                  </button>
                ) : null}
              </div>
            </WorkbenchPanel>
          </div>

          <div className="space-y-4">
            <WorkbenchPanel title="Draft" description="Versioned local save/load and JSON export.">
              <div className="grid gap-2">
                <button type="button" onClick={save} disabled={!definition} className="inline-flex items-center gap-2 rounded-lg border border-white/10 px-3 py-2 text-sm text-zinc-200 disabled:opacity-40"><Save className="h-4 w-4" /> Save locally</button>
                <button type="button" onClick={load} disabled={running} className="inline-flex items-center gap-2 rounded-lg border border-white/10 px-3 py-2 text-sm text-zinc-200 disabled:opacity-40"><RotateCcw className="h-4 w-4" /> Load saved</button>
                <button type="button" onClick={exportDraft} disabled={!definition} className="inline-flex items-center gap-2 rounded-lg border border-white/10 px-3 py-2 text-sm text-zinc-200 disabled:opacity-40"><Download className="h-4 w-4" /> Export definition</button>
              </div>
            </WorkbenchPanel>

            {validation ? (
              <div className="rounded-xl border border-emerald-400/30 bg-emerald-400/10 p-4 text-sm text-emerald-100">
                <CheckCircle2 className="mb-2 h-5 w-5" /> Validated against {validation.workflow_id}
              </div>
            ) : null}
            {result ? (
              <div className="rounded-xl border border-blue-400/30 bg-blue-400/10 p-4" aria-live="polite">
                <p className="text-sm font-semibold text-blue-100">Run {result.status}</p>
                <p className="mt-1 text-xs text-blue-100/80">
                  Engineering: {result.result_envelope.engineering_status}
                </p>
                <p className="mt-1 break-all text-[10px] text-blue-100/60">{result.run_id}</p>
                {result.audit.review_stop ? <p className="mt-2 text-xs text-amber-200">Stop: {result.audit.review_stop}</p> : null}
              </div>
            ) : null}
            {message ? <div className="rounded-xl border border-emerald-400/20 bg-emerald-400/[0.06] p-3 text-xs text-emerald-100" role="status">{message}</div> : null}
            {error ? (
              <div className="flex gap-2 rounded-xl border border-rose-400/30 bg-rose-400/10 p-3 text-xs text-rose-100" role="alert">
                <AlertTriangle className="h-4 w-4 shrink-0" /> {error}
              </div>
            ) : null}
          </div>
        </div>
      </WorkbenchShell>
    </div>
  );
}
