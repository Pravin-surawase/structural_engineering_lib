import { useMemo, useRef, useState } from 'react';
import { Calculator, Download, ShieldCheck, SlidersHorizontal } from 'lucide-react';
import { WorkbenchHeader } from '../../components/workbench/WorkbenchHeader';
import { WorkbenchPanel } from '../../components/workbench/WorkbenchPanel';
import { WorkbenchShell } from '../../components/workbench/WorkbenchShell';
import { designSlabWorkflow } from './client';
import { SlabPanelMap } from './SlabPanelMap';
import type {
  SlabWorkflowMode,
  SlabWorkflowRequest,
  SlabWorkflowResult,
} from './types';

const MODES: Array<{ id: SlabWorkflowMode; label: string; note: string }> = [
  { id: 'simply-supported', label: 'One-way simple', note: 'Flexure, bars, shear and span/depth' },
  { id: 'continuous', label: 'One-way continuous', note: 'Built-in Tables 12 and 13' },
  { id: 'two-way', label: 'Two-way panel', note: 'Built-in Table 26 or 27' },
];

const SAMPLES: Record<SlabWorkflowMode, SlabWorkflowRequest> = {
  'simply-supported': {
    short_effective_span_mm: 3000,
    long_effective_span_mm: 7500,
    thickness_mm: 150,
    d_mm: 125,
    factored_area_load_kn_per_m2: 10,
    fck_n_per_mm2: 20,
    fy_n_per_mm2: 415,
    main_bar_diameter_mm: 10,
    main_bar_spacing_mm: 250,
    distribution_bar_diameter_mm: 8,
    distribution_bar_spacing_mm: 250,
    reviewed_base_span_depth_limit: 20,
    reviewed_aggregate_modification_factor: 1.2,
    serviceability_limit_source_reference: 'IS456_CL23_REVIEWED',
    serviceability_limit_source_is_approved: true,
    qualified_serviceability_acceptance_reference: 'SLAB_UI_REVIEW_SIMPLE',
    qualified_serviceability_acceptance_acknowledged: true,
    strip_width_mm: 1000,
  },
  continuous: {
    short_effective_span_mm: 3000,
    long_effective_span_mm: 7500,
    thickness_mm: 140,
    d_mm: 115,
    factored_dead_and_fixed_imposed_load_kn_per_m2: 14.25,
    factored_nonfixed_imposed_load_kn_per_m2: 0,
    positive_location: 'end_span_positive',
    negative_location: 'next_to_end_support_negative',
    shear_location: 'end_support',
    fck_n_per_mm2: 20,
    fy_n_per_mm2: 415,
    number_of_spans: 3,
    maximum_span_variation_percent: 0,
    uniform_cross_section_acknowledged: true,
    substantially_uniform_load_acknowledged: true,
    redistribution_applied: false,
    positive_bar_diameter_mm: 8,
    positive_bar_spacing_mm: 180,
    negative_bar_diameter_mm: 10,
    negative_bar_spacing_mm: 230,
    distribution_bar_diameter_mm: 8,
    distribution_bar_spacing_mm: 250,
    reviewed_base_span_depth_limit: 23,
    reviewed_aggregate_modification_factor: 1.18,
    serviceability_limit_source_reference: 'IS456_CL23_REVIEWED',
    serviceability_limit_source_is_approved: true,
    qualified_serviceability_acceptance_reference: 'SLAB_UI_REVIEW_CONTINUOUS',
    qualified_serviceability_acceptance_acknowledged: true,
    strip_width_mm: 1000,
  },
  'two-way': {
    x_effective_span_mm: 4000,
    y_effective_span_mm: 6000,
    thickness_mm: 160,
    x_min_edge: 'discontinuous',
    x_max_edge: 'continuous',
    y_min_edge: 'discontinuous',
    y_max_edge: 'continuous',
    corner_lift_condition: 'restrained',
    factored_area_load_kn_per_m2: 15.5,
    d_x_mm: 135,
    d_y_mm: 125,
    fck_n_per_mm2: 20,
    fy_n_per_mm2: 415,
    x_positive_bar_diameter_mm: 10,
    x_positive_bar_spacing_mm: 200,
    x_negative_bar_diameter_mm: 10,
    x_negative_bar_spacing_mm: 200,
    y_positive_bar_diameter_mm: 8,
    y_positive_bar_spacing_mm: 200,
    y_negative_bar_diameter_mm: 8,
    y_negative_bar_spacing_mm: 200,
    edge_strip_bar_diameter_mm: 8,
    edge_strip_bar_spacing_mm: 250,
    torsion_bar_diameter_mm: 8,
    torsion_bar_spacing_mm: 200,
    reviewed_base_span_depth_limit: 30,
    reviewed_aggregate_modification_factor: 1,
    serviceability_limit_source_reference: 'IS456_CL24_REVIEWED',
    serviceability_limit_source_is_approved: true,
    qualified_serviceability_acceptance_reference: 'SLAB_UI_REVIEW_TWO_WAY',
    qualified_serviceability_acceptance_acknowledged: true,
  },
};

const EDITABLE: Record<SlabWorkflowMode, Array<[string, string, string]>> = {
  'simply-supported': [
    ['short_effective_span_mm', 'Short effective span', 'mm'],
    ['long_effective_span_mm', 'Long effective span', 'mm'],
    ['thickness_mm', 'Overall depth', 'mm'],
    ['d_mm', 'Effective depth', 'mm'],
    ['factored_area_load_kn_per_m2', 'Factored area load', 'kN/m²'],
    ['main_bar_spacing_mm', 'Main bar spacing', 'mm'],
    ['distribution_bar_spacing_mm', 'Distribution spacing', 'mm'],
    ['reviewed_aggregate_modification_factor', 'Reviewed modification factor', 'ratio'],
  ],
  continuous: [
    ['short_effective_span_mm', 'Effective span', 'mm'],
    ['long_effective_span_mm', 'Transverse span', 'mm'],
    ['thickness_mm', 'Overall depth', 'mm'],
    ['d_mm', 'Effective depth', 'mm'],
    ['factored_dead_and_fixed_imposed_load_kn_per_m2', 'Factored fixed load', 'kN/m²'],
    ['factored_nonfixed_imposed_load_kn_per_m2', 'Factored non-fixed load', 'kN/m²'],
    ['number_of_spans', 'Number of spans', 'count'],
    ['maximum_span_variation_percent', 'Maximum span variation', '%'],
  ],
  'two-way': [
    ['x_effective_span_mm', 'Short x span', 'mm'],
    ['y_effective_span_mm', 'Long y span', 'mm'],
    ['thickness_mm', 'Overall depth', 'mm'],
    ['d_x_mm', 'x effective depth', 'mm'],
    ['d_y_mm', 'y effective depth', 'mm'],
    ['factored_area_load_kn_per_m2', 'Factored area load', 'kN/m²'],
    ['x_positive_bar_spacing_mm', 'x positive spacing', 'mm'],
    ['y_positive_bar_spacing_mm', 'y positive spacing', 'mm'],
  ],
};

function readNumber(result: SlabWorkflowResult | null, path: string): number | null {
  let current: unknown = result;
  for (const key of path.split('.')) {
    if (!current || typeof current !== 'object') return null;
    current = (current as Record<string, unknown>)[key];
  }
  return typeof current === 'number' ? current : null;
}

function readText(result: SlabWorkflowResult | null, path: string): string | null {
  let current: unknown = result;
  for (const key of path.split('.')) {
    if (!current || typeof current !== 'object') return null;
    current = (current as Record<string, unknown>)[key];
  }
  return typeof current === 'string' ? current : null;
}

function format(value: number | null, digits = 3) {
  return value === null ? '—' : value.toFixed(digits);
}

export function SlabWorkbenchPage() {
  const [mode, setMode] = useState<SlabWorkflowMode>('continuous');
  const [request, setRequest] = useState<SlabWorkflowRequest>({ ...SAMPLES.continuous });
  const [revision, setRevision] = useState(0);
  const [resultRevision, setResultRevision] = useState<number | null>(null);
  const [result, setResult] = useState<SlabWorkflowResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState(false);
  const abortRef = useRef<AbortController | null>(null);
  const isCurrent = result !== null && resultRevision === revision;

  const coefficientLabel = useMemo(() => {
    if (mode === 'simply-supported') return 'Closed-form one-way action';
    const methodPath = mode === 'continuous'
      ? 'flexure.input.coefficients.method'
      : 'panel.input.coefficients.method';
    const tablePath = mode === 'continuous'
      ? 'flexure.input.coefficients.table_id'
      : 'panel.input.coefficients.table_id';
    return `${readText(result, tablePath) ?? 'IS 456 built-in lookup'} · ${readText(result, methodPath) ?? 'pending'}`;
  }, [mode, result]);

  function switchMode(nextMode: SlabWorkflowMode) {
    abortRef.current?.abort();
    setMode(nextMode);
    setRequest({ ...SAMPLES[nextMode] });
    setRevision((value) => value + 1);
    setResult(null);
    setResultRevision(null);
    setError(null);
  }

  function updateNumber(field: string, raw: string) {
    const value = Number(raw);
    setRequest((current) => ({ ...current, [field]: value }));
    setRevision((current) => current + 1);
    setError(null);
  }

  async function calculate() {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    const submittedRevision = revision;
    setRunning(true);
    setError(null);
    try {
      const response = await designSlabWorkflow(mode, request, controller.signal);
      if (!controller.signal.aborted) {
        setResult(response);
        setResultRevision(submittedRevision);
      }
    } catch (caught) {
      if (!controller.signal.aborted) {
        setError(caught instanceof Error ? caught.message : 'Slab design failed');
      }
    } finally {
      if (!controller.signal.aborted) setRunning(false);
    }
  }

  function downloadPassport() {
    if (!result || !isCurrent) return;
    const passport = {
      schema: 'structural-lib-is456-slab-passport-v1',
      mode,
      request_revision: revision,
      request,
      result,
      boundaries: {
        qualified_review_required: true,
        complete_engineering_design_approved: false,
        flat_slabs: 'separate_held_extension',
      },
    };
    const url = URL.createObjectURL(new Blob([JSON.stringify(passport, null, 2)], { type: 'application/json' }));
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `slab-passport-${mode}.json`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  const momentPaths = mode === 'simply-supported'
    ? [['Positive moment', 'reinforcement.flexure.factored_moment_knm']]
    : mode === 'continuous'
      ? [
          ['Positive moment', 'flexure.positive_midspan.factored_moment_knm_per_m'],
          ['Negative moment', 'flexure.negative_support.factored_moment_knm_per_m'],
        ]
      : [
          ['Mx negative', 'panel.x_negative.factored_moment_knm_per_m'],
          ['Mx positive', 'panel.x_positive.factored_moment_knm_per_m'],
          ['My negative', 'panel.y_negative.factored_moment_knm_per_m'],
          ['My positive', 'panel.y_positive.factored_moment_knm_per_m'],
        ];

  return (
    <WorkbenchShell
      className="pt-14"
      header={<WorkbenchHeader title="Solid slab workbench" projectName="IS 456 · bounded beam/wall-supported panels" />}
    >
      <div className="h-full overflow-y-auto p-4 pb-24 sm:p-6 md:pb-8">
        <div className="mx-auto grid max-w-7xl gap-4 xl:grid-cols-[360px_minmax(0,1fr)]">
          <div className="space-y-4">
            <WorkbenchPanel title="Design route" description="Choose the physical slab system before entering values.">
              <div className="grid gap-2">
                {MODES.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => switchMode(item.id)}
                    className={`rounded-lg border p-3 text-left ${mode === item.id ? 'border-blue-400/60 bg-blue-500/10' : 'border-white/10 bg-zinc-950/40 hover:border-white/20'}`}
                  >
                    <span className="block text-sm font-semibold text-zinc-100">{item.label}</span>
                    <span className="mt-1 block text-xs text-zinc-400">{item.note}</span>
                  </button>
                ))}
              </div>
            </WorkbenchPanel>

            <WorkbenchPanel title="Inputs" description="All displayed dimensions and actions have explicit units.">
              <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-1">
                {EDITABLE[mode].map(([field, label, unit]) => (
                  <label key={field} className="grid gap-1 text-xs text-zinc-400">
                    <span>{label}</span>
                    <span className="flex overflow-hidden rounded-lg border border-white/10 bg-zinc-950 focus-within:border-blue-400/60">
                      <input
                        aria-label={label}
                        type="number"
                        value={String(request[field])}
                        onChange={(event) => updateNumber(field, event.target.value)}
                        className="min-w-0 flex-1 bg-transparent px-3 py-2 text-sm text-zinc-100 outline-none"
                      />
                      <span className="border-l border-white/10 px-2 py-2 text-zinc-500">{unit}</span>
                    </span>
                  </label>
                ))}
              </div>
              <button
                type="button"
                onClick={calculate}
                disabled={running}
                className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-500 disabled:cursor-wait disabled:opacity-60"
              >
                <Calculator className="h-4 w-4" aria-hidden="true" />
                {running ? 'Calculating…' : 'Run slab design'}
              </button>
            </WorkbenchPanel>
          </div>

          <div className="space-y-4">
            <WorkbenchPanel title="Support and reinforcement map" description={coefficientLabel}>
              <div className="grid items-stretch gap-4 lg:grid-cols-[minmax(0,1fr)_260px]">
                <div className="rounded-xl border border-white/10 bg-zinc-950/70 p-3">
                  <SlabPanelMap mode={mode} request={request} />
                </div>
                <div className="grid content-start gap-3">
                  <div className="rounded-xl border border-blue-400/20 bg-blue-500/[0.06] p-4">
                    <div className="flex items-center gap-2 text-sm font-semibold text-blue-200">
                      <SlidersHorizontal className="h-4 w-4" aria-hidden="true" />
                      Coefficient handling
                    </div>
                    <p className="mt-2 text-xs leading-5 text-zinc-400">
                      {mode === 'continuous' ? 'Table 12/13 values are selected by load and action location.' : mode === 'two-way' ? 'Physical edges resolve the Table 26/27 case; only bounded interpolation is used.' : 'Simply supported one-way action uses the explicit UDL strip model.'}
                    </p>
                  </div>
                  <div className="rounded-xl border border-amber-400/20 bg-amber-400/[0.05] p-4 text-xs leading-5 text-amber-100/80">
                    Flat slabs, drops, column strips and column-supported punching are not part of this workbench.
                  </div>
                </div>
              </div>
            </WorkbenchPanel>

            <WorkbenchPanel title="Calculation result" description={isCurrent ? 'Current response matches the displayed inputs.' : result ? 'Inputs changed after this response; rerun before export.' : 'Run the design to create a calculation passport.'}>
              {error ? <div role="alert" className="rounded-lg border border-rose-400/30 bg-rose-500/10 p-3 text-sm text-rose-200">{error}</div> : null}
              <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                {momentPaths.map(([label, path]) => (
                  <div key={path} className="rounded-xl border border-white/10 bg-zinc-950/50 p-4">
                    <p className="text-xs text-zinc-500">{label}</p>
                    <p className="mt-2 text-xl font-semibold text-zinc-100">{format(readNumber(result, path))}</p>
                    <p className="mt-1 text-xs text-zinc-500">kN m/m</p>
                  </div>
                ))}
              </div>
              <div className="mt-4 grid gap-3 sm:grid-cols-3">
                <div className="rounded-lg border border-white/10 p-3 text-sm text-zinc-300">Shear stress <strong className="float-right text-zinc-100">{format(readNumber(result, mode === 'two-way' ? 'panel.shear.tau_v_n_per_mm2' : 'shear.tau_v_n_per_mm2'))}</strong></div>
                <div className="rounded-lg border border-white/10 p-3 text-sm text-zinc-300">L/d utilization <strong className="float-right text-zinc-100">{format(readNumber(result, 'serviceability.utilization'))}</strong></div>
                <div className="rounded-lg border border-white/10 p-3 text-sm text-zinc-300">Revision <strong className="float-right text-zinc-100">{isCurrent ? 'current' : result ? 'stale' : 'none'}</strong></div>
              </div>
              <div className="mt-4 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-emerald-400/20 bg-emerald-400/[0.05] p-4">
                <div className="flex gap-3">
                  <ShieldCheck className="mt-0.5 h-5 w-5 shrink-0 text-emerald-300" aria-hidden="true" />
                  <p className="max-w-2xl text-xs leading-5 text-emerald-100/80">Software evidence records topology, coefficient source, checks and held boundaries. Qualified project review remains required.</p>
                </div>
                <button
                  type="button"
                  onClick={downloadPassport}
                  disabled={!isCurrent}
                  className="inline-flex items-center gap-2 rounded-lg border border-emerald-300/30 px-3 py-2 text-sm font-semibold text-emerald-200 hover:bg-emerald-400/10 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  <Download className="h-4 w-4" aria-hidden="true" />
                  Download passport
                </button>
              </div>
            </WorkbenchPanel>
          </div>
        </div>
      </div>
    </WorkbenchShell>
  );
}
