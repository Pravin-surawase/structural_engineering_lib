import { ResultLifecycleBadge } from '../../components/workbench/ResultLifecycleBadge';
import { columnReviewCanExport, columnReviewIsCurrent } from './identity';
import type { ColumnReviewRecord } from './types';

export interface ColumnResultReviewerProps {
  record: ColumnReviewRecord | null;
  currentInputHash: string;
  currentInputRevision: number;
  onExport: (record: ColumnReviewRecord) => void;
}

function format(value: number, digits = 2): string {
  return Number.isFinite(value) ? value.toFixed(digits) : '—';
}

function governingMetric(record: ColumnReviewRecord): string | null {
  const check = record.design.checks[record.design.governing_check];
  const ratio = check?.interaction_ratio ?? check?.utilization_ratio;
  return typeof ratio === 'number' ? format(ratio, 4) : null;
}

function inputDisposition(record: ColumnReviewRecord): string {
  if (record.design.classification === 'SLENDER') return 'Slender-column check with additional moments';
  if (record.inputs.Mux_kNm === 0 && record.inputs.Muy_kNm === 0) {
    return 'Short axial input; minimum eccentricity enforced about both axes';
  }
  if (record.design.governing_check.startsWith('uniaxial')) return 'Short uniaxial check';
  return 'Short biaxial Bresler check';
}

export function ColumnResultReviewer({
  record,
  currentInputHash,
  currentInputRevision,
  onExport,
}: ColumnResultReviewerProps) {
  if (!record) {
    return (
      <section className="rounded-xl border border-dashed border-white/15 p-6 text-sm text-zinc-400">
        Run the supplied-column check to create a revision-bound review result.
      </section>
    );
  }

  const isCurrent = columnReviewIsCurrent(record, currentInputHash, currentInputRevision);
  const canExport = columnReviewCanExport(record, currentInputHash, currentInputRevision);
  const passed = record.decision === 'PASS' && isCurrent;
  const metric = governingMetric(record);
  const warnings = [...record.design.warnings, ...record.detailing.warnings];

  return (
    <section className="space-y-4" aria-label="Column result review">
      <div className={`rounded-xl border p-4 ${passed ? 'border-emerald-400/30 bg-emerald-400/10' : 'border-rose-400/30 bg-rose-400/10'}`}>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-wider text-zinc-400">Adequacy disposition</p>
            <h2 className="mt-1 text-xl font-semibold text-white">
              {isCurrent ? (record.decision === 'PASS' ? 'CHECK PASSED' : 'CHECK FAILED') : 'RESULT STALE'}
            </h2>
            <p className="mt-1 text-sm text-zinc-300">{inputDisposition(record)}</p>
          </div>
          <ResultLifecycleBadge lifecycle={isCurrent ? 'current' : 'stale'} />
        </div>
        <p className="mt-3 text-xs font-medium text-amber-100">
          Qualified structural-engineering review is required before project use.
        </p>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        <ReviewValue label="Axis classification" value={`x ${record.design.classification_x} · y ${record.design.classification_y}`} />
        <ReviewValue label="Effective lengths" value={`x ${format(record.design.le_x_mm)} mm · y ${format(record.design.le_y_mm)} mm`} />
        <ReviewValue label="Slenderness" value={`x ${format(record.design.slenderness_x, 3)} · y ${format(record.design.slenderness_y, 3)}`} />
        <ReviewValue label="Minimum eccentricity" value={`x ${format(record.design.emin_x_mm)} mm · y ${format(record.design.emin_y_mm)} mm`} />
        <ReviewValue label="Applied moments" value={`x ${format(record.design.Mux_applied_kNm)} · y ${format(record.design.Muy_applied_kNm)} kN·m`} />
        <ReviewValue label="Design moments" value={`x ${format(record.design.Mux_design_kNm)} · y ${format(record.design.Muy_design_kNm)} kN·m`} />
        <ReviewValue label="Additional moments" value={`x ${format(record.design.Ma_x_kNm ?? 0)} · y ${format(record.design.Ma_y_kNm ?? 0)} kN·m`} />
        <ReviewValue label="Governing check" value={record.design.governing_check.replaceAll('_', ' ')} />
        <ReviewValue label="Governing ratio" value={metric ?? 'Reported in governing result'} />
      </div>

      <div className="rounded-xl border border-white/10 p-4">
        <h3 className="text-sm font-semibold text-white">Supplied reinforcement and detailing</h3>
        <dl className="mt-3 grid grid-cols-2 gap-3 text-xs sm:grid-cols-3">
          <ReviewTerm label="Longitudinal steel" value={`${record.detailing.num_bars}-T${format(record.detailing.bar_dia_mm, 0)}`} />
          <ReviewTerm label="Provided area" value={`${format(record.detailing.Asc_provided_mm2)} mm²`} />
          <ReviewTerm label="Steel ratio" value={`${format(record.detailing.steel_ratio * 100, 3)}%`} />
          <ReviewTerm label="Ties" value={`T${format(record.detailing.tie_dia_mm, 0)} @ ${format(record.detailing.tie_spacing_mm, 0)} mm`} />
          <ReviewTerm label="Bar spacing" value={`${format(record.detailing.bar_spacing_mm)} mm`} />
          <ReviewTerm label="Cross-ties" value={record.detailing.cross_ties_needed ? 'Required' : 'Not indicated'} />
        </dl>
      </div>

      {warnings.length > 0 ? (
        <div className="rounded-xl border border-amber-400/20 bg-amber-400/10 p-4">
          <h3 className="text-sm font-semibold text-amber-100">Warnings requiring review</h3>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-xs text-amber-50">
            {warnings.map((warning) => <li key={warning}>{warning}</li>)}
          </ul>
        </div>
      ) : null}

      <div className="rounded-xl border border-white/10 p-4 text-xs text-zinc-300">
        <p><strong>Revision:</strong> {record.revision.input_revision} · {record.revision.input_hash}</p>
        <p className="mt-1"><strong>Request:</strong> {record.revision.request_id}</p>
        <p className="mt-1"><strong>Clauses:</strong> {[...record.design.clause_refs, record.detailing.clause_ref].join(', ')}</p>
        <p className="mt-2 text-zinc-400">
          Held scope: circular columns, PMM/arbitrary reinforcement, automatic sizing, global frame analysis, and general second-order analysis.
        </p>
      </div>

      <button
        type="button"
        disabled={!canExport}
        onClick={() => onExport(record)}
        className="w-full rounded-lg border border-white/15 px-4 py-2.5 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-40"
      >
        Export current review packet
      </button>
      {!isCurrent ? (
        <p className="text-xs text-amber-200" role="status">Export blocked because the result does not match the current input revision.</p>
      ) : !canExport ? (
        <p className="text-xs text-rose-200" role="status">Export held until both adequacy and supplied-detailing checks pass.</p>
      ) : null}
    </section>
  );
}

function ReviewValue({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-white/10 bg-white/[0.03] p-3">
      <p className="text-[11px] uppercase tracking-wide text-zinc-500">{label}</p>
      <p className="mt-1 text-sm font-medium text-zinc-100">{value}</p>
    </div>
  );
}

function ReviewTerm({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-zinc-500">{label}</dt>
      <dd className="mt-0.5 font-medium text-zinc-100">{value}</dd>
    </div>
  );
}
