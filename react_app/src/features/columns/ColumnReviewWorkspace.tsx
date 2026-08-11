import { useMemo, useState } from 'react';
import { reviewRectangularColumn } from './api';
import { ColumnInputEditor } from './ColumnInputEditor';
import { DEFAULT_COLUMN_REVIEW_INPUTS } from './defaults';
import { columnInputHash } from './identity';
import { ColumnResultReviewer } from './ColumnResultReviewer';
import type { ColumnReviewInputs, ColumnReviewRecord } from './types';

export interface ColumnReviewWorkspaceProps {
  initialInputs?: ColumnReviewInputs;
  onExport?: (record: ColumnReviewRecord) => void;
}

function downloadReviewPacket(record: ColumnReviewRecord) {
  const blob = new Blob([JSON.stringify(record, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${record.inputs.member_label || 'column'}-review-${record.revision.input_hash}.json`;
  link.click();
  URL.revokeObjectURL(url);
}

export function ColumnReviewWorkspace({
  initialInputs = DEFAULT_COLUMN_REVIEW_INPUTS,
  onExport = downloadReviewPacket,
}: ColumnReviewWorkspaceProps) {
  const [inputs, setInputs] = useState<ColumnReviewInputs>(initialInputs);
  const [inputRevision, setInputRevision] = useState(1);
  const [record, setRecord] = useState<ColumnReviewRecord | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const currentInputHash = useMemo(() => columnInputHash(inputs), [inputs]);

  const updateInputs = (patch: Partial<ColumnReviewInputs>) => {
    setInputs((current) => ({ ...current, ...patch }));
    setInputRevision((current) => current + 1);
  };

  const submit = async () => {
    const submittedInputs = { ...inputs };
    const submittedRevision = inputRevision;
    const submittedHash = columnInputHash(submittedInputs);
    const requestId = `column-${submittedRevision}-${submittedHash}`;
    setIsSubmitting(true);
    setError(null);
    setRecord(null);
    try {
      const bundle = await reviewRectangularColumn(submittedInputs);
      const decision = bundle.design.is_safe && bundle.detailing.is_valid ? 'PASS' : 'FAIL';
      setRecord({
        ...bundle,
        inputs: submittedInputs,
        decision,
        revision: {
          request_id: requestId,
          input_hash: submittedHash,
          input_revision: submittedRevision,
          calculated_at: new Date().toISOString(),
        },
      });
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Column check failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="h-full overflow-y-auto bg-zinc-950 p-4 text-white">
      <header className="mx-auto mb-4 max-w-7xl rounded-xl border border-white/10 bg-white/[0.03] p-4">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-blue-300">COLUMN-RECTANGULAR-REVIEW-V1</p>
        <h1 className="mt-1 text-2xl font-semibold">Rectangular tied-column check and review</h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-zinc-400">
          Review a supplied section and reinforcement arrangement using the maintained IS 456 rectangular-column routes. This workflow does not automatically design the member or reinforcement.
        </p>
      </header>
      <div className="mx-auto grid max-w-7xl gap-4 lg:grid-cols-[22rem_minmax(0,1fr)]">
        <aside className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
          <ColumnInputEditor inputs={inputs} isSubmitting={isSubmitting} onChange={updateInputs} onSubmit={submit} />
        </aside>
        <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
          {error ? (
            <div className="mb-4 rounded-lg border border-rose-400/30 bg-rose-400/10 p-3 text-sm text-rose-100" role="alert">
              HOLD — {error}. No adequacy result or export is available.
            </div>
          ) : null}
          <ColumnResultReviewer
            record={record}
            currentInputHash={currentInputHash}
            currentInputRevision={inputRevision}
            onExport={onExport}
          />
        </div>
      </div>
    </main>
  );
}
