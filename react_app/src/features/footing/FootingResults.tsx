import type { ResultLifecycle } from '../../workspace/types';
import type {
  CalculationStatus,
  ConcentricIsolatedFootingResponse,
  FootingDirectionDetail,
  FootingStatus,
} from './types';

interface FootingResultsProps {
  result: ConcentricIsolatedFootingResponse;
  lifecycle: ResultLifecycle;
}

type DisplayStatus = FootingStatus | CalculationStatus;

const STATUS_CLASS: Record<DisplayStatus, string> = {
  PASS: 'border-emerald-400/30 bg-emerald-400/10 text-emerald-100',
  FAIL: 'border-rose-400/30 bg-rose-400/10 text-rose-100',
  HOLD: 'border-amber-400/30 bg-amber-400/10 text-amber-100',
  NOT_EVALUATED: 'border-zinc-500/40 bg-zinc-500/10 text-zinc-200',
};

function formatNumber(value: number | null, digits = 3): string {
  if (value === null) return '—';
  return new Intl.NumberFormat('en-IN', {
    maximumFractionDigits: digits,
  }).format(value);
}

function formatDirectionMap(values: Record<string, number>): string {
  const entries = Object.entries(values);
  if (entries.length === 0) return 'Not available';
  return entries
    .map(([direction, value]) => `${direction} ${formatNumber(value, 6)}%`)
    .join(' · ');
}

function StatusCard({ label, status }: { label: string; status: DisplayStatus }) {
  return (
    <div className={`rounded-xl border p-3 ${STATUS_CLASS[status]}`}>
      <p className="text-[10px] font-semibold uppercase tracking-[0.16em] opacity-70">
        {label}
      </p>
      <p className="mt-1 text-base font-bold">{status}</p>
    </div>
  );
}

function EvidenceCard({
  title,
  status,
  utilization,
  clause,
  children,
}: {
  title: string;
  status: 'PASS' | 'FAIL' | 'NOT_EVALUATED';
  utilization: number | null;
  clause: string | null;
  children: React.ReactNode;
}) {
  return (
    <article className="rounded-xl border border-white/8 bg-zinc-950/55 p-3">
      <div className="flex items-start justify-between gap-2">
        <div>
          <h3 className="text-xs font-semibold text-white">{title}</h3>
          {clause ? <p className="mt-1 text-[10px] text-zinc-500">{clause}</p> : null}
        </div>
        <span className={`rounded-full border px-2 py-0.5 text-[10px] font-semibold ${STATUS_CLASS[status]}`}>
          {status}
        </span>
      </div>
      {utilization === null ? null : (
        <p className="mt-2 text-xl font-semibold tabular-nums text-white">
          {formatNumber(utilization, 4)}
          <span className="ml-1 text-[10px] font-normal text-zinc-500">utilization</span>
        </p>
      )}
      <div className="mt-2 text-xs leading-5 text-zinc-300">{children}</div>
    </article>
  );
}

function DirectionSchedule({ detail }: { detail: FootingDirectionDetail }) {
  return (
    <article className="rounded-xl border border-white/8 bg-zinc-950/55 p-3">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h4 className="text-sm font-semibold text-white">
          {detail.layer} layer · direction {detail.direction}
        </h4>
        <span className="text-sm font-semibold text-blue-200">
          {detail.bar_count}-T{detail.diameter_mm} @ {formatNumber(detail.spacing_mm, 1)} mm
        </span>
      </div>
      <dl className="mt-3 grid grid-cols-2 gap-2 text-xs sm:grid-cols-4">
        <div>
          <dt className="text-zinc-500">Required / provided Ast</dt>
          <dd className="mt-1 text-zinc-100">
            {formatNumber(detail.required_area_mm2, 1)} / {formatNumber(detail.provided_area_mm2, 1)} mm²
          </dd>
        </div>
        <div>
          <dt className="text-zinc-500">Physical / analysis d</dt>
          <dd className="mt-1 text-zinc-100">
            {formatNumber(detail.physical_effective_depth_mm, 1)} / {formatNumber(detail.analysis_effective_depth_mm, 1)} mm
          </dd>
        </div>
        <div>
          <dt className="text-zinc-500">Clear / maximum spacing</dt>
          <dd className="mt-1 text-zinc-100">
            {formatNumber(detail.clear_spacing_mm, 1)} / {formatNumber(detail.max_spacing_mm, 1)} mm
          </dd>
        </div>
        <div>
          <dt className="text-zinc-500">Development / available end</dt>
          <dd className="mt-1 text-zinc-100">
            {formatNumber(detail.development_length_mm, 1)} / {formatNumber(detail.straight_anchorage_available_each_end_mm, 1)} mm
          </dd>
        </div>
      </dl>
      <div className="mt-3 overflow-x-auto">
        <table className="min-w-full text-left text-[11px]">
          <caption className="sr-only">{detail.direction} reinforcement zones</caption>
          <thead className="text-zinc-500">
            <tr>
              <th className="pb-1 pr-3 font-medium">Zone</th>
              <th className="pb-1 pr-3 font-medium">Width</th>
              <th className="pb-1 pr-3 font-medium">Ast req/prov</th>
              <th className="pb-1 pr-3 font-medium">Bars</th>
              <th className="pb-1 font-medium">Spacing / clear</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5 text-zinc-300">
            {detail.zones.map((zone) => (
              <tr key={zone.zone}>
                <td className="py-1.5 pr-3">{zone.zone.replaceAll('_', ' ')}</td>
                <td className="py-1.5 pr-3">{formatNumber(zone.width_mm, 1)} mm</td>
                <td className="py-1.5 pr-3">
                  {formatNumber(zone.required_area_mm2, 1)} / {formatNumber(zone.provided_area_mm2, 1)} mm²
                </td>
                <td className="py-1.5 pr-3">{zone.bar_count}</td>
                <td className="py-1.5">
                  {formatNumber(zone.spacing_mm, 1)} / {formatNumber(zone.clear_spacing_mm, 1)} mm
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </article>
  );
}

export function FootingResults({ result, lifecycle }: FootingResultsProps) {
  const isStale = lifecycle === 'stale';
  const flexureStatus = result.flexure
    ? (result.flexure.is_safe ? 'PASS' : 'FAIL')
    : 'NOT_EVALUATED';
  const oneWayStatus = result.one_way_shear
    ? (result.one_way_shear.is_safe ? 'PASS' : 'FAIL')
    : 'NOT_EVALUATED';
  const punchingStatus = result.punching
    ? (result.punching.is_safe ? 'PASS' : 'FAIL')
    : 'NOT_EVALUATED';
  const loadTransferStatus = result.load_transfer.is_safe ? 'PASS' : 'FAIL';

  return (
    <div className="space-y-4" aria-label="Footing design evidence">
      {isStale ? (
        <div
          className="rounded-xl border border-amber-400/30 bg-amber-400/10 p-3 text-xs leading-5 text-amber-100"
          role="alert"
        >
          Retained evidence is stale because the inputs changed. Recalculate before
          relying on this result.
        </div>
      ) : null}

      <div className="grid grid-cols-3 gap-2">
        <StatusCard label="Aggregate" status={result.status} />
        <StatusCard label="Calculation" status={result.calculation_status} />
        <StatusCard label="Detailing" status={result.detailing_status} />
      </div>

      <section className="rounded-xl border border-white/8 bg-white/[0.02] p-4">
        <h3 className="text-sm font-semibold text-white">Plan, actions and selected depth</h3>
        <dl className="mt-3 grid grid-cols-2 gap-3 text-xs sm:grid-cols-4">
          <div>
            <dt className="text-zinc-500">Plan</dt>
            <dd className="mt-1 font-medium text-zinc-100">
              {formatNumber(result.bearing.L_mm, 1)} × {formatNumber(result.bearing.B_mm, 1)} mm
            </dd>
          </div>
          <div>
            <dt className="text-zinc-500">Service / factored load</dt>
            <dd className="mt-1 font-medium text-zinc-100">
              {formatNumber(result.service_axial_load_kN, 1)} / {formatNumber(result.factored_axial_load_kN, 1)} kN
            </dd>
          </div>
          <div>
            <dt className="text-zinc-500">Overall thickness</dt>
            <dd className="mt-1 font-medium text-zinc-100">
              {formatNumber(result.selected_overall_thickness_mm, 1)} mm
            </dd>
          </div>
          <div>
            <dt className="text-zinc-500">Effective depth L / B</dt>
            <dd className="mt-1 font-medium text-zinc-100">
              {formatNumber(result.selected_effective_depth_L_mm, 1)} / {formatNumber(result.selected_effective_depth_B_mm, 1)} mm
            </dd>
          </div>
        </dl>
      </section>

      <section>
        <h3 className="mb-2 text-sm font-semibold text-white">Governing checks</h3>
        <div className="grid gap-2 sm:grid-cols-2">
          <EvidenceCard
            title="Bearing pressure"
            status={result.bearing.is_safe ? 'PASS' : 'FAIL'}
            utilization={result.bearing.utilization_ratio}
            clause={result.bearing.clause_ref}
          >
            qmin/qmax {formatNumber(result.bearing.q_min_kPa, 2)} / {formatNumber(result.bearing.q_max_kPa, 2)} kPa against {formatNumber(result.bearing.q_safe_kPa, 2)} kPa allowable.
          </EvidenceCard>
          <EvidenceCard
            title="Flexure"
            status={flexureStatus}
            utilization={null}
            clause={result.flexure?.clause_ref ?? null}
          >
            {result.flexure
              ? `Mu L/B ${formatNumber(result.flexure.Mu_L_kNm, 2)} / ${formatNumber(result.flexure.Mu_B_kNm, 2)} kNm; Ast L/B ${formatNumber(result.flexure.Ast_L_mm2, 1)} / ${formatNumber(result.flexure.Ast_B_mm2, 1)} mm².`
              : 'No selected flexure result.'}
          </EvidenceCard>
          <EvidenceCard
            title="One-way shear"
            status={oneWayStatus}
            utilization={result.one_way_shear?.utilization_ratio ?? null}
            clause={result.one_way_shear?.clause_ref ?? null}
          >
            Governing direction {result.one_way_shear?.governing_direction ?? '—'}; returned authority is {result.one_way_shear_basis}.
          </EvidenceCard>
          <EvidenceCard
            title="Punching shear"
            status={punchingStatus}
            utilization={result.punching?.utilization_ratio ?? null}
            clause={result.punching?.clause_ref ?? null}
          >
            Critical perimeter {formatNumber(result.punching?.perimeter_mm ?? null, 1)} mm; Vu {formatNumber(result.punching?.Vu_punch_kN ?? null, 2)} kN.
          </EvidenceCard>
          <EvidenceCard
            title="Column-footing load transfer"
            status={loadTransferStatus}
            utilization={null}
            clause={result.load_transfer.clause_refs.join(', ')}
          >
            Transfer steel required/provided {formatNumber(result.load_transfer.required_transfer_steel_area_mm2, 1)} / {formatNumber(result.load_transfer.provided_transfer_steel_area_mm2, 1)} mm². Governing member: {result.load_transfer.governing_concrete_member}.
          </EvidenceCard>
        </div>
      </section>

      <section className="rounded-xl border border-blue-400/20 bg-blue-400/[0.06] p-4">
        <h3 className="text-sm font-semibold text-blue-100">One-way shear authority</h3>
        <dl className="mt-3 grid gap-3 text-xs sm:grid-cols-2">
          <div>
            <dt className="text-blue-100/60">Required-pt screening</dt>
            <dd className="mt-1 text-blue-50">
              {formatDirectionMap(result.screening_pt_passed_to_one_way_shear_percent)}
            </dd>
            <dd className="mt-1 text-blue-100/60">
              Utilization {formatNumber(result.one_way_shear_screening?.utilization_ratio ?? null, 6)}
            </dd>
          </div>
          <div>
            <dt className="text-blue-100/60">Returned authoritative basis</dt>
            <dd className="mt-1 font-semibold text-blue-50">{result.one_way_shear_basis}</dd>
            <dd className="mt-1 text-blue-100/60">
              pt {formatDirectionMap(result.pt_passed_to_one_way_shear_percent)}
            </dd>
          </div>
        </dl>
      </section>

      <section>
        <h3 className="text-sm font-semibold text-white">Depth candidates</h3>
        <div className="mt-2 overflow-x-auto rounded-xl border border-white/8">
          <table className="min-w-full text-left text-xs">
            <thead className="bg-zinc-950/70 text-zinc-500">
              <tr>
                <th className="px-3 py-2 font-medium">D / dL / dB</th>
                <th className="px-3 py-2 font-medium">Status</th>
                <th className="px-3 py-2 font-medium">One-way / punching</th>
                <th className="px-3 py-2 font-medium">Reasons</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5 text-zinc-300">
              {result.depth_candidates.map((candidate) => (
                <tr key={`${candidate.overall_thickness_mm}-${candidate.effective_depth_L_mm}-${candidate.effective_depth_B_mm}`}>
                  <td className="px-3 py-2">
                    {formatNumber(candidate.overall_thickness_mm, 1)} / {formatNumber(candidate.effective_depth_L_mm, 1)} / {formatNumber(candidate.effective_depth_B_mm, 1)} mm
                  </td>
                  <td className="px-3 py-2">{candidate.structural_status}</td>
                  <td className="px-3 py-2">
                    {formatNumber(candidate.one_way_shear_utilization, 4)} / {formatNumber(candidate.punching_shear_utilization, 4)}
                  </td>
                  <td className="px-3 py-2">{candidate.reasons.join(', ') || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h3 className="text-sm font-semibold text-white">Directional reinforcement</h3>
        <div className="mt-2 overflow-x-auto rounded-xl border border-white/8">
          <table className="min-w-full text-left text-xs">
            <thead className="bg-zinc-950/70 text-zinc-500">
              <tr>
                <th className="px-3 py-2 font-medium">Direction</th>
                <th className="px-3 py-2 font-medium">Ast required / provided</th>
                <th className="px-3 py-2 font-medium">pt required / provided</th>
                <th className="px-3 py-2 font-medium">Basis</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5 text-zinc-300">
              {result.reinforcement_demands.map((demand) => (
                <tr key={demand.direction}>
                  <td className="px-3 py-2 font-medium text-white">{demand.direction}</td>
                  <td className="px-3 py-2">
                    {formatNumber(demand.required_steel_area_mm2, 1)} / {formatNumber(demand.provided_steel_area_mm2, 1)} mm²
                  </td>
                  <td className="px-3 py-2">
                    {formatNumber(demand.required_steel_percent, 6)} / {formatNumber(demand.provided_steel_percent, 6)}%
                  </td>
                  <td className="px-3 py-2">{demand.required_steel_basis}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {result.detailing ? (
        <section className="space-y-2">
          <h3 className="text-sm font-semibold text-white">Buildable detailing schedule</h3>
          {result.detailing.lower ? <DirectionSchedule detail={result.detailing.lower} /> : null}
          {result.detailing.upper ? <DirectionSchedule detail={result.detailing.upper} /> : null}
          <article className="rounded-xl border border-white/8 bg-zinc-950/55 p-3 text-xs text-zinc-300">
            <h4 className="font-semibold text-white">Dowel schedule linkage</h4>
            <p className="mt-2">
              {result.detailing.dowel_schedule_link.bar_count}-T{result.detailing.dowel_schedule_link.diameter_mm}; required/provided {formatNumber(result.detailing.dowel_schedule_link.required_area_mm2, 1)} / {formatNumber(result.detailing.dowel_schedule_link.provided_area_mm2, 1)} mm².
            </p>
            <p className="mt-1">
              Development into footing required/available {formatNumber(result.detailing.dowel_schedule_link.required_development_length_into_footing_mm, 1)} / {formatNumber(result.detailing.dowel_schedule_link.available_development_length_into_footing_mm, 1)} mm; into column {formatNumber(result.detailing.dowel_schedule_link.required_development_length_into_supported_member_mm, 1)} / {formatNumber(result.detailing.dowel_schedule_link.available_development_length_into_supported_member_mm, 1)} mm.
            </p>
          </article>
        </section>
      ) : (
        <div
          className="rounded-xl border border-amber-400/30 bg-amber-400/10 p-3 text-xs text-amber-100"
          role="alert"
        >
          Detailing HOLD: {result.detailing_hold_reason ?? 'Complete detailing inputs were not supplied.'}
        </div>
      )}

      <section className="rounded-xl border border-white/8 bg-white/[0.02] p-4">
        <h3 className="text-sm font-semibold text-white">Provenance and boundary</h3>
        <dl className="mt-3 grid gap-3 text-xs sm:grid-cols-2">
          <div>
            <dt className="text-zinc-500">Code / schema</dt>
            <dd className="mt-1 text-zinc-200">
              {result.provenance.code_edition} · {result.provenance.schema_version}
            </dd>
          </div>
          <div>
            <dt className="text-zinc-500">Soil-pressure source</dt>
            <dd className="mt-1 text-zinc-200">
              {result.provenance.allowable_soil_pressure_source_reference}
            </dd>
          </div>
          <div>
            <dt className="text-zinc-500">Source IDs</dt>
            <dd className="mt-1 break-words text-zinc-200">
              {result.provenance.source_ids.join(', ')}
            </dd>
          </div>
          <div>
            <dt className="text-zinc-500">Core function IDs</dt>
            <dd className="mt-1 break-words text-zinc-200">
              {result.provenance.core_function_ids.join(', ')}
            </dd>
          </div>
        </dl>
        <div className="mt-3">
          <p className="text-xs font-medium text-zinc-300">Clause bases</p>
          <ul className="mt-1 space-y-1 text-xs text-zinc-400">
            {Object.entries(result.provenance.clause_bases).map(([check, basis]) => (
              <li key={check}><span className="text-zinc-200">{check}:</span> {basis}</li>
            ))}
          </ul>
        </div>
        <div className="mt-3">
          <p className="text-xs font-medium text-zinc-300">Explicit exclusions</p>
          <ul className="mt-1 list-disc space-y-1 pl-5 text-xs text-zinc-400">
            {result.exclusions.map((exclusion) => <li key={exclusion}>{exclusion}</li>)}
          </ul>
        </div>
        <p className="mt-4 rounded-lg border border-amber-400/20 bg-amber-400/[0.06] p-3 text-xs leading-5 text-amber-100">
          Qualified review required: {result.provenance.qualified_review_requirement}
        </p>
      </section>
    </div>
  );
}
