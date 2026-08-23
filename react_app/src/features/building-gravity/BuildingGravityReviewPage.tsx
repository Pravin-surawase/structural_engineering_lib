import { useEffect, useMemo, useState } from 'react';
import { Download, Play, ShieldAlert } from 'lucide-react';
import { getGravityWorkflowDefinition, runGravityWorkflow } from './client';
import type {
  GravityOverallStatus,
  GravityWorkflowDefinition,
  GravityWorkflowRunBundle,
} from './types';

const STATUS_LABELS: Record<GravityOverallStatus, string> = {
  BLOCKED: 'INPUT BLOCKED',
  ERROR: 'CALCULATION ERROR',
  NOT_EVALUATED: 'NOT EVALUATED',
  STALE: 'STALE',
  PASS: 'PASS',
  FAIL: 'FAIL',
  HOLD: 'HOLD',
};

const STATUS_CLASSES: Record<GravityOverallStatus, string> = {
  BLOCKED: 'border-rose-400/40 bg-rose-400/10 text-rose-200',
  ERROR: 'border-rose-400/40 bg-rose-400/10 text-rose-200',
  NOT_EVALUATED: 'border-zinc-400/40 bg-zinc-400/10 text-zinc-200',
  STALE: 'border-amber-400/40 bg-amber-400/10 text-amber-200',
  PASS: 'border-emerald-400/40 bg-emerald-400/10 text-emerald-200',
  FAIL: 'border-red-400/40 bg-red-400/10 text-red-200',
  HOLD: 'border-amber-400/40 bg-amber-400/10 text-amber-200',
};

function StatusBadge({ status }: { status: GravityOverallStatus }) {
  return (
    <span className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold ${STATUS_CLASSES[status]}`}>
      {STATUS_LABELS[status]}
    </span>
  );
}

function actionValue(action: GravityWorkflowRunBundle['workflow_result']['actions'][number]) {
  if (action.area_load_kn_m2 !== null) return `${action.area_load_kn_m2.toFixed(3)} kN/m²`;
  if (action.moment_knm !== null) {
    return `${action.moment_knm.toFixed(3)} kN·m / ${action.shear_kn?.toFixed(3)} kN`;
  }
  return `${action.axial_kn?.toFixed(3)} kN`;
}

function practicalActionValue(
  action: GravityWorkflowRunBundle['workflow_result']['practical_action_reconciliation'][number],
) {
  const position = action.point_position_mm === null ? '' : ` @ ${action.point_position_mm} mm`;
  return `${action.supplied_magnitude.toFixed(3)} ${action.units}${position}`;
}

export function BuildingGravityReviewPage() {
  const [definition, setDefinition] = useState<GravityWorkflowDefinition | null>(null);
  const [requestText, setRequestText] = useState('');
  const [bundle, setBundle] = useState<GravityWorkflowRunBundle | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    getGravityWorkflowDefinition(controller.signal)
      .then(setDefinition)
      .catch((caught: unknown) => {
        if (!controller.signal.aborted) {
          setError(caught instanceof Error ? caught.message : 'Workflow discovery failed');
        }
      });
    return () => controller.abort();
  }, []);

  const componentCounts = useMemo(() => {
    const counts: Partial<Record<GravityOverallStatus, number>> = {};
    bundle?.workflow_result.components.forEach((component) => {
      const status = component.result_envelope.overall_status;
      counts[status] = (counts[status] ?? 0) + 1;
    });
    return counts;
  }, [bundle]);

  const governingIssue = bundle?.workflow_result.result_envelope.issues[0] ?? null;

  function loadExample() {
    if (!definition) return;
    setError(null);
    setBundle(null);
    setRequestText(JSON.stringify(definition.example_request, null, 2));
  }

  async function handleRun() {
    setError(null);
    setBundle(null);
    let request: unknown;
    try {
      request = JSON.parse(requestText);
    } catch {
      setError('The request must be valid JSON before calculation can start.');
      return;
    }
    if (typeof request !== 'object' || request === null || Array.isArray(request)) {
      setError('The request must be one JSON object.');
      return;
    }
    setRunning(true);
    try {
      setBundle(await runGravityWorkflow(request as Record<string, unknown>));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Gravity workflow failed');
    } finally {
      setRunning(false);
    }
  }

  function downloadBook() {
    if (!bundle) return;
    const blob = new Blob([JSON.stringify(bundle.calculation_book, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `gravity-calculation-book-${bundle.workflow_result.workflow_result_hash.slice(0, 12)}.json`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="h-full overflow-auto bg-zinc-950 px-4 pb-16 pt-20 text-zinc-100 sm:px-6">
      <div className="mx-auto max-w-6xl space-y-5">
        <header>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-300">
            building.gravity.dead-live.v1
          </p>
          <h1 className="mt-2 text-2xl font-semibold">Building Gravity Workflow V1</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-zinc-400">
            Review one accepted physical model, its reconciled dead/live load path,
            caller-assigned practical actions, exact member actions, conditional
            component checks, and visible holds.
          </p>
        </header>

        <section className="rounded-xl border border-amber-400/25 bg-amber-400/[0.06] p-4">
          <div className="flex gap-3">
            <ShieldAlert className="mt-0.5 h-5 w-5 shrink-0 text-amber-300" aria-hidden="true" />
            <div>
              <h2 className="text-sm font-semibold text-amber-100">Qualified review required</h2>
              <p className="mt-1 text-xs leading-5 text-amber-100/75">
                PASS and FAIL are bounded software dispositions. HOLD stays visible when
                a required design, soil, detailing, or acceptance basis is missing.
              </p>
            </div>
          </div>
        </section>

        {definition ? (
          <section className="rounded-xl border border-white/10 bg-zinc-900/60 p-4">
            <h2 className="text-sm font-semibold">Accepted topology</h2>
            <ul className="mt-2 grid gap-1 text-xs text-zinc-400 sm:grid-cols-2">
              {definition.accepted_topology.map((item) => <li key={item}>• {item}</li>)}
            </ul>
          </section>
        ) : null}

        <section className="rounded-xl border border-white/10 bg-zinc-900/60 p-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <label htmlFor="gravity-request" className="text-sm font-semibold">
              GravityWorkflowRequestV1 JSON
            </label>
            <button
              type="button"
              onClick={loadExample}
              disabled={!definition}
              className="rounded-lg border border-white/10 px-3 py-1.5 text-xs font-semibold enabled:hover:bg-white/5 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Load maintained example
            </button>
          </div>
          <p className="mt-1 text-xs text-zinc-500">
            Paste the exported, hash-bound request. Unknown or incomplete fields are rejected before calculation.
          </p>
          <textarea
            id="gravity-request"
            value={requestText}
            onChange={(event) => setRequestText(event.target.value)}
            rows={12}
            spellCheck={false}
            className="mt-3 w-full rounded-lg border border-white/10 bg-zinc-950 p-3 font-mono text-xs text-zinc-200 outline-none focus:border-cyan-400/60"
            placeholder='{"schema_version":"gravity-workflow-request/v1", ...}'
          />
          <div className="mt-3 flex flex-wrap items-center gap-3">
            <button
              type="button"
              onClick={handleRun}
              disabled={running || requestText.trim().length === 0}
              className="inline-flex items-center gap-2 rounded-lg bg-cyan-600 px-4 py-2 text-sm font-semibold text-white enabled:hover:bg-cyan-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <Play className="h-4 w-4" aria-hidden="true" />
              {running ? 'Running…' : 'Run gravity review'}
            </button>
            {error ? <p role="alert" className="text-sm text-rose-300">INPUT BLOCKED — {error}</p> : null}
          </div>
        </section>

        {bundle ? (
          <>
            <section className="rounded-xl border border-white/10 bg-zinc-900/60 p-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <StatusBadge status={bundle.workflow_result.result_envelope.overall_status} />
                  <p className="text-xs text-zinc-400">
                    {bundle.calculation_book.reconciliation.boundary_count} load boundaries ·{' '}
                    residual {bundle.calculation_book.reconciliation.maximum_absolute_residual_kn} kN
                  </p>
                </div>
                <button
                  type="button"
                  onClick={downloadBook}
                  className="inline-flex items-center gap-2 rounded-lg border border-white/10 px-3 py-2 text-xs font-semibold hover:bg-white/5"
                >
                  <Download className="h-4 w-4" aria-hidden="true" />
                  Download calculation book
                </button>
              </div>
              <div className="mt-4 grid gap-2 font-mono text-[11px] text-zinc-500">
                <p>model {bundle.workflow_result.model_hash}</p>
                <p>loads {bundle.workflow_result.load_model_hash}</p>
                <p>ledger {bundle.workflow_result.ledger_hash}</p>
                <p>result {bundle.workflow_result.workflow_result_hash}</p>
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                {(Object.keys(componentCounts) as GravityOverallStatus[]).map((status) => (
                  <span key={status} className="text-xs text-zinc-400">
                    {STATUS_LABELS[status]} {componentCounts[status]}
                  </span>
                ))}
              </div>
              {governingIssue ? (
                <div className="mt-4 rounded-lg border border-amber-400/20 bg-amber-400/[0.05] p-3 text-xs text-amber-100/85">
                  <p className="font-mono font-semibold">{governingIssue.code}</p>
                  <p className="mt-1">{governingIssue.message}</p>
                </div>
              ) : null}
            </section>

            {bundle.workflow_result.practical_action_reconciliation.length > 0 ? (
              <section className="overflow-hidden rounded-xl border border-white/10 bg-zinc-900/60">
                <h2 className="p-4 text-sm font-semibold">Caller-assigned practical actions</h2>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="border-y border-white/10 text-zinc-500">
                      <tr><th className="p-3">Source</th><th>Case / kind</th><th>Destination</th><th>Supplied</th><th>Reconciliation</th></tr>
                    </thead>
                    <tbody>
                      {bundle.workflow_result.practical_action_reconciliation.map((action) => (
                        <tr key={action.action_id} className="border-b border-white/5">
                          <td className="p-3 font-mono">
                            {action.source_identity}
                            <span className="mt-1 block text-zinc-500">{action.source_ref_id}</span>
                          </td>
                          <td>{action.case_id} · {action.kind}</td>
                          <td className="font-mono">{action.destination_id}</td>
                          <td>{practicalActionValue(action)}</td>
                          <td className={action.reconciled ? 'text-emerald-300' : 'text-rose-300'}>
                            {action.reconciled ? 'BALANCED' : 'UNBALANCED'} · residual {action.residual_kn} kN
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            ) : null}

            <section className="overflow-hidden rounded-xl border border-white/10 bg-zinc-900/60">
              <h2 className="p-4 text-sm font-semibold">Component review</h2>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="border-y border-white/10 text-zinc-500">
                    <tr><th className="p-3">ID</th><th>Kind</th><th>Status</th><th>Canonical function</th></tr>
                  </thead>
                  <tbody>
                    {bundle.workflow_result.components.map((component) => (
                      <tr key={component.component_id} className="border-b border-white/5">
                        <td className="p-3 font-mono">{component.component_id}</td>
                        <td>{component.kind}</td>
                        <td><StatusBadge status={component.result_envelope.overall_status} /></td>
                        <td className="pr-3 font-mono text-zinc-400">{component.canonical_function}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            <section className="overflow-hidden rounded-xl border border-white/10 bg-zinc-900/60">
              <h2 className="p-4 text-sm font-semibold">Transferred actions</h2>
              <div className="max-h-80 overflow-auto">
                <table className="w-full text-left text-xs">
                  <thead className="sticky top-0 border-y border-white/10 bg-zinc-900 text-zinc-500">
                    <tr><th className="p-3">Component</th><th>Combination</th><th>Action</th></tr>
                  </thead>
                  <tbody>
                    {bundle.workflow_result.actions.map((action) => (
                      <tr key={action.action_id} className="border-b border-white/5">
                        <td className="p-3 font-mono">{action.component_id} · {action.kind}</td>
                        <td>{action.combination_id}</td>
                        <td>{actionValue(action)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          </>
        ) : null}

        <section className="rounded-xl border border-white/10 bg-zinc-900/60 p-4">
          <h2 className="text-sm font-semibold">Status meanings</h2>
          <div className="mt-3 flex flex-wrap gap-2">
            {(['BLOCKED', 'ERROR', 'PASS', 'FAIL', 'HOLD'] as GravityOverallStatus[]).map((status) => (
              <StatusBadge key={status} status={status} />
            ))}
            <span className="inline-flex rounded-full border border-violet-400/40 bg-violet-400/10 px-2.5 py-1 text-xs font-semibold text-violet-200">
              QUALIFIED REVIEW REQUIRED
            </span>
          </div>
        </section>
      </div>
    </div>
  );
}
