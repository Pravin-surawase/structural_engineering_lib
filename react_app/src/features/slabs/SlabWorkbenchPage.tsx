import { useMemo, useRef, useState } from 'react';
import {
  AlertTriangle,
  Calculator,
  Download,
  ShieldCheck,
  SlidersHorizontal,
} from 'lucide-react';
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

type ChoiceOption = { value: string; label: string };
type ChoiceField = { field: string; label: string; options: ChoiceOption[] };
type ReviewCheck = { label: string; status: string | null; pass: boolean | null };

const CONTINUOUS_CHOICES: ChoiceField[] = [
  {
    field: 'positive_location',
    label: 'Positive action location',
    options: [
      { value: 'end_span_positive', label: 'End span positive' },
      { value: 'interior_span_positive', label: 'Interior span positive' },
    ],
  },
  {
    field: 'negative_location',
    label: 'Negative action location',
    options: [
      { value: 'next_to_end_support_negative', label: 'Next-to-end support' },
      { value: 'other_interior_support_negative', label: 'Other interior support' },
    ],
  },
  {
    field: 'shear_location',
    label: 'Shear action location',
    options: [
      { value: 'end_support', label: 'End support' },
      { value: 'next_to_end_support_outer', label: 'Next-to-end, outer side' },
      { value: 'next_to_end_support_inner', label: 'Next-to-end, inner side' },
      { value: 'other_interior_support', label: 'Other interior support' },
    ],
  },
];

const EDGE_OPTIONS: ChoiceOption[] = [
  { value: 'continuous', label: 'Continuous' },
  { value: 'discontinuous', label: 'Discontinuous' },
];
const TWO_WAY_CHOICES: ChoiceField[] = [
  { field: 'x_min_edge', label: 'x-min edge', options: EDGE_OPTIONS },
  { field: 'x_max_edge', label: 'x-max edge', options: EDGE_OPTIONS },
  { field: 'y_min_edge', label: 'y-min edge', options: EDGE_OPTIONS },
  { field: 'y_max_edge', label: 'y-max edge', options: EDGE_OPTIONS },
  {
    field: 'corner_lift_condition',
    label: 'Corner lift condition',
    options: [
      { value: 'restrained', label: 'Restrained' },
      { value: 'free_to_lift', label: 'Free to lift' },
    ],
  },
];
const EDGE_FIELDS = new Set(['x_min_edge', 'x_max_edge', 'y_min_edge', 'y_max_edge']);

function readValue(result: SlabWorkflowResult | null, path: string): unknown {
  let current: unknown = result;
  for (const key of path.split('.')) {
    if (!current || typeof current !== 'object') return null;
    current = (current as Record<string, unknown>)[key];
  }
  return current;
}

function readNumber(result: SlabWorkflowResult | null, path: string): number | null {
  const value = readValue(result, path);
  return typeof value === 'number' ? value : null;
}

function readText(result: SlabWorkflowResult | null, path: string): string | null {
  const value = readValue(result, path);
  return typeof value === 'string' ? value : null;
}

function readBoolean(result: SlabWorkflowResult | null, path: string): boolean | null {
  const value = readValue(result, path);
  return typeof value === 'boolean' ? value : null;
}

function readTextArray(result: SlabWorkflowResult | null, path: string): string[] {
  const value = readValue(result, path);
  return Array.isArray(value)
    ? value.filter((item): item is string => typeof item === 'string')
    : [];
}

function readObjectArray(
  result: SlabWorkflowResult | null,
  path: string,
): Array<Record<string, unknown>> {
  const value = readValue(result, path);
  return Array.isArray(value)
    ? value.filter(
        (item): item is Record<string, unknown> =>
          item !== null && typeof item === 'object' && !Array.isArray(item),
      )
    : [];
}

function format(value: number | null, digits = 3) {
  return value === null ? '—' : value.toFixed(digits);
}

function formatStatus(value: string | null) {
  return value ? value.replaceAll('_', ' ') : 'not evaluated';
}

function regionAdequacy(result: SlabWorkflowResult | null, path: string): boolean | null {
  const checks = ['area_passed', 'diameter_passed', 'spacing_passed'].map((field) =>
    readBoolean(result, `${path}.${field}`),
  );
  return checks.some((value) => value === null)
    ? null
    : checks.every((value) => value === true);
}

function recordText(record: Record<string, unknown>, key: string): string | null {
  const value = record[key];
  return typeof value === 'string' ? value : null;
}

function recordNumber(record: Record<string, unknown>, key: string): number | null {
  const value = record[key];
  return typeof value === 'number' ? value : null;
}

function recordBoolean(record: Record<string, unknown>, key: string): boolean | null {
  const value = record[key];
  return typeof value === 'boolean' ? value : null;
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

  const choiceFields = mode === 'continuous'
    ? CONTINUOUS_CHOICES
    : mode === 'two-way'
      ? TWO_WAY_CHOICES
      : [];
  const coefficientRoot = mode === 'continuous'
    ? 'flexure.input.coefficients'
    : 'panel.input.coefficients';
  const coefficientSource = mode === 'simply-supported'
    ? 'Closed-form UDL strip action'
    : readText(result, `${coefficientRoot}.source_reference`);
  const coefficientCase = mode === 'simply-supported'
    ? 'wL²/8'
    : readText(result, `${coefficientRoot}.case_id`);
  const interpolationBounds = readValue(result, `${coefficientRoot}.interpolation_bounds`);
  const interpolationLabel = Array.isArray(interpolationBounds)
    ? interpolationBounds.filter((value): value is number => typeof value === 'number').join(' → ')
    : null;
  const coefficientAspectRatio = readNumber(result, `${coefficientRoot}.aspect_ratio_ly_lx`);

  const reinforcementChecks = useMemo<ReviewCheck[]>(() => {
    if (!result) return [];
    if (mode === 'simply-supported') {
      const status = readText(result, 'reinforcement.detailing.detailing_adequacy');
      return [{ label: 'Provided reinforcement', status, pass: status === 'adequate' }];
    }
    if (mode === 'continuous') {
      return [
        ['Positive region', 'positive_reinforcement'],
        ['Negative region', 'negative_reinforcement'],
        ['Distribution steel', 'distribution_reinforcement'],
      ].map(([label, path]) => {
        const pass = regionAdequacy(result, path);
        return { label, status: pass === null ? null : pass ? 'adequate' : 'inadequate', pass };
      });
    }
    const checks = [
      ['x negative region', 'panel.x_negative.reinforcement'],
      ['x positive region', 'panel.x_positive.reinforcement'],
      ['y negative region', 'panel.y_negative.reinforcement'],
      ['y positive region', 'panel.y_positive.reinforcement'],
      ['Edge strips', 'panel.edge_strip_reinforcement'],
    ].map(([label, path]) => {
      const pass = regionAdequacy(result, path);
      return { label, status: pass === null ? null : pass ? 'adequate' : 'inadequate', pass };
    });
    const torsion = readObjectArray(result, 'panel.corner_torsion');
    const torsionPass = torsion.length > 0
      ? torsion.every((corner) => corner.is_adequate === true)
      : null;
    checks.push({
      label: 'Corner torsion',
      status: torsionPass === null ? null : torsionPass ? 'adequate' : 'inadequate',
      pass: torsionPass,
    });
    return checks;
  }, [mode, result]);

  const shearStatus = readText(
    result,
    mode === 'two-way' ? 'panel.shear.status' : 'shear.status',
  );
  const punchingDisposition = readText(
    result,
    mode === 'two-way' ? 'panel.punching_shear_disposition' : 'punching_shear_disposition',
  );
  const serviceabilityStatus = readText(result, 'serviceability.status');
  const reviewChecks: ReviewCheck[] = [
    ...reinforcementChecks,
    {
      label: 'Ordinary slab shear',
      status: shearStatus,
      pass: shearStatus === null ? null : shearStatus === 'concrete_capacity_satisfied',
    },
    {
      label: 'Punching shear boundary',
      status: punchingDisposition,
      pass: punchingDisposition === null
        ? null
        : punchingDisposition.startsWith('not_applicable'),
    },
    {
      label: 'Reviewed span/depth',
      status: serviceabilityStatus,
      pass: serviceabilityStatus === null
        ? null
        : serviceabilityStatus === 'satisfied_with_reviewed_limit',
    },
  ];
  const boundedReviewPass = result && reviewChecks.every((check) => check.pass !== null)
    ? reviewChecks.every((check) => check.pass === true)
    : null;

  const heldItems = useMemo(() => {
    if (!result) return [];
    const items: string[] = [];
    if (mode === 'simply-supported') {
      items.push(
        ...readTextArray(result, 'reinforcement.flexure.limitations'),
        ...readTextArray(result, 'reinforcement.detailing.limitations'),
      );
    } else if (mode === 'two-way') {
      items.push(...readTextArray(result, 'panel.held_scope'));
    }
    const directDeflection = readText(result, 'serviceability.direct_deflection_status');
    const shearReinforcement = readText(
      result,
      mode === 'two-way'
        ? 'panel.shear.shear_reinforcement_design_status'
        : 'shear.shear_reinforcement_design_status',
    );
    if (
      directDeflection === 'held_not_implemented'
      && !items.some((item) => item.toLowerCase().includes('direct deflection'))
    ) {
      items.push('Direct deflection calculation is held.');
    }
    if (
      shearReinforcement === 'not_automatically_designed'
      && !items.some((item) => item.toLowerCase().includes('automatic slab shear'))
    ) {
      items.push('Automatic slab shear reinforcement is not designed.');
    }
    if (!items.some((item) => item.toLowerCase().includes('flat slabs'))) {
      items.push('Flat slabs, drops, column strips and column-supported punching are held.');
    }
    return [...new Set(items.filter((item) => !item.startsWith('COMPOSED WORKFLOW:')))];
  }, [mode, result]);

  const cornerTorsion = readObjectArray(result, 'panel.corner_torsion');

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

  function updateChoice(field: string, value: string) {
    setRequest((current) => {
      const next = { ...current, [field]: value };
      if (field === 'corner_lift_condition' && value === 'free_to_lift') {
        for (const edge of EDGE_FIELDS) next[edge] = 'discontinuous';
      } else if (
        EDGE_FIELDS.has(field)
        && value === 'continuous'
        && current.corner_lift_condition === 'free_to_lift'
      ) {
        next.corner_lift_condition = 'restrained';
      }
      return next;
    });
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
  const reviewPresentation = boundedReviewPass === true
    ? {
        title: 'Bounded checks satisfied',
        message: 'The returned provided-bar, shear and reviewed span/depth checks pass. Qualified project review remains required.',
        container: 'border-emerald-400/20 bg-emerald-400/[0.05]',
        text: 'text-emerald-100/80',
        icon: 'text-emerald-300',
      }
    : boundedReviewPass === false
      ? {
          title: 'Redesign or qualified review required',
          message: 'At least one returned reinforcement, shear or serviceability check is not satisfied.',
          container: 'border-rose-400/30 bg-rose-500/10',
          text: 'text-rose-100/90',
          icon: 'text-rose-300',
        }
      : {
          title: result ? 'Review evidence incomplete' : 'Awaiting calculation',
          message: result
            ? 'The response does not contain every bounded review disposition.'
            : 'Run the design to evaluate reinforcement, shear and serviceability.',
          container: 'border-amber-400/20 bg-amber-400/[0.05]',
          text: 'text-amber-100/80',
          icon: 'text-amber-300',
        };

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
              {choiceFields.length > 0 ? (
                <div className="mt-4 grid gap-3 border-t border-white/10 pt-4">
                  {choiceFields.map(({ field, label, options }) => (
                    <label key={field} className="grid gap-1 text-xs text-zinc-400">
                      <span>{label}</span>
                      <select
                        aria-label={label}
                        value={String(request[field])}
                        onChange={(event) => updateChoice(field, event.target.value)}
                        className="rounded-lg border border-white/10 bg-zinc-950 px-3 py-2 text-sm text-zinc-100 outline-none focus:border-blue-400/60"
                      >
                        {options.map((option) => (
                          <option key={option.value} value={option.value} className="bg-zinc-950">
                            {option.label}
                          </option>
                        ))}
                      </select>
                    </label>
                  ))}
                  {mode === 'two-way' ? (
                    <p className="text-xs leading-5 text-zinc-500">
                      Free-to-lift corners select the four-edge discontinuous Table 27 route.
                      Choosing a continuous edge restores restrained corners.
                    </p>
                  ) : null}
                </div>
              ) : null}
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
                    {result ? (
                      <dl className="mt-3 grid gap-2 border-t border-blue-300/10 pt-3 text-xs">
                        <div>
                          <dt className="text-zinc-500">Source</dt>
                          <dd className="mt-0.5 break-words text-zinc-200">{coefficientSource ?? '—'}</dd>
                        </div>
                        <div>
                          <dt className="text-zinc-500">Case</dt>
                          <dd className="mt-0.5 text-zinc-200">{coefficientCase ?? '—'}</dd>
                        </div>
                        {coefficientAspectRatio !== null ? (
                          <div>
                            <dt className="text-zinc-500">Aspect ratio Ly/Lx</dt>
                            <dd className="mt-0.5 text-zinc-200">{format(coefficientAspectRatio, 3)}</dd>
                          </div>
                        ) : null}
                        {interpolationLabel ? (
                          <div>
                            <dt className="text-zinc-500">Interpolation bounds</dt>
                            <dd className="mt-0.5 text-zinc-200">{interpolationLabel}</dd>
                          </div>
                        ) : null}
                      </dl>
                    ) : null}
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
              {result ? (
                <div className="mt-4 grid gap-4 xl:grid-cols-2">
                  <section className="rounded-xl border border-white/10 bg-zinc-950/40 p-4" aria-labelledby="slab-review-heading">
                    <h3 id="slab-review-heading" className="text-sm font-semibold text-zinc-100">Returned check dispositions</h3>
                    <div className="mt-3 grid gap-2">
                      {reviewChecks.map((check) => (
                        <div key={check.label} className="flex items-center justify-between gap-3 rounded-lg border border-white/10 px-3 py-2 text-xs">
                          <span className="text-zinc-400">{check.label}</span>
                          <strong className={check.pass === true ? 'text-emerald-300' : check.pass === false ? 'text-rose-300' : 'text-amber-300'}>
                            {formatStatus(check.status)}
                          </strong>
                        </div>
                      ))}
                    </div>
                  </section>

                  <section className="rounded-xl border border-amber-400/20 bg-amber-400/[0.04] p-4" aria-labelledby="slab-holds-heading">
                    <h3 id="slab-holds-heading" className="text-sm font-semibold text-amber-100">Held and excluded scope</h3>
                    <ul className="mt-3 grid gap-2 text-xs leading-5 text-amber-100/75">
                      {heldItems.map((item) => <li key={item}>• {item}</li>)}
                    </ul>
                  </section>
                </div>
              ) : null}

              {mode === 'two-way' && result ? (
                <div className="mt-4 grid gap-4">
                  <section className="rounded-xl border border-white/10 bg-zinc-950/40 p-4" aria-labelledby="slab-strips-heading">
                    <h3 id="slab-strips-heading" className="text-sm font-semibold text-zinc-100">Middle and edge strips</h3>
                    <div className="mt-3 grid gap-2 sm:grid-cols-2 xl:grid-cols-4">
                      {[
                        ['x middle strip', 'panel.strip_distribution.x_moment_middle_strip_width_mm'],
                        ['x edge strip each', 'panel.strip_distribution.x_moment_edge_strip_width_each_mm'],
                        ['y middle strip', 'panel.strip_distribution.y_moment_middle_strip_width_mm'],
                        ['y edge strip each', 'panel.strip_distribution.y_moment_edge_strip_width_each_mm'],
                      ].map(([label, path]) => (
                        <div key={path} className="rounded-lg border border-white/10 p-3 text-xs text-zinc-400">
                          <span className="block">{label}</span>
                          <strong className="mt-1 block text-sm text-zinc-100">{format(readNumber(result, path), 1)} mm</strong>
                        </div>
                      ))}
                    </div>
                  </section>

                  <section className="rounded-xl border border-white/10 bg-zinc-950/40 p-4" aria-labelledby="slab-torsion-heading">
                    <h3 id="slab-torsion-heading" className="text-sm font-semibold text-zinc-100">Per-corner torsion schedule</h3>
                    <div className="mt-3 grid gap-2 md:grid-cols-2">
                      {cornerTorsion.map((corner) => {
                        const adequate = recordBoolean(corner, 'is_adequate');
                        return (
                          <div key={recordText(corner, 'corner') ?? JSON.stringify(corner)} className="rounded-lg border border-white/10 p-3 text-xs">
                            <div className="flex items-center justify-between gap-3">
                              <strong className="text-zinc-100">{formatStatus(recordText(corner, 'corner'))}</strong>
                              <span className={adequate === true ? 'text-emerald-300' : adequate === false ? 'text-rose-300' : 'text-amber-300'}>
                                {formatStatus(recordText(corner, 'torsion_class'))} · {adequate === true ? 'adequate' : adequate === false ? 'inadequate' : 'not evaluated'}
                              </span>
                            </div>
                            <dl className="mt-2 grid grid-cols-3 gap-2 text-zinc-500">
                              <div><dt>Zone</dt><dd className="text-zinc-300">{format(recordNumber(corner, 'zone_extent_from_each_edge_mm'), 1)} mm</dd></div>
                              <div><dt>Required/layer</dt><dd className="text-zinc-300">{format(recordNumber(corner, 'required_each_of_four_layers_mm2_per_m'), 1)} mm²/m</dd></div>
                              <div><dt>Provided/layer</dt><dd className="text-zinc-300">{format(recordNumber(corner, 'provided_each_layer_mm2_per_m'), 1)} mm²/m</dd></div>
                            </dl>
                          </div>
                        );
                      })}
                    </div>
                  </section>
                </div>
              ) : null}

              <div className={`mt-4 flex flex-wrap items-center justify-between gap-3 rounded-xl border p-4 ${reviewPresentation.container}`} role={boundedReviewPass === false ? 'alert' : undefined}>
                <div className="flex gap-3">
                  {boundedReviewPass === true
                    ? <ShieldCheck className={`mt-0.5 h-5 w-5 shrink-0 ${reviewPresentation.icon}`} aria-hidden="true" />
                    : <AlertTriangle className={`mt-0.5 h-5 w-5 shrink-0 ${reviewPresentation.icon}`} aria-hidden="true" />}
                  <div>
                    <p className={`text-sm font-semibold ${reviewPresentation.text}`}>{reviewPresentation.title}</p>
                    <p className={`mt-1 max-w-2xl text-xs leading-5 ${reviewPresentation.text}`}>{reviewPresentation.message}</p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={downloadPassport}
                  disabled={!isCurrent}
                  className="inline-flex items-center gap-2 rounded-lg border border-white/20 px-3 py-2 text-sm font-semibold text-zinc-100 hover:bg-white/5 disabled:cursor-not-allowed disabled:opacity-40"
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
