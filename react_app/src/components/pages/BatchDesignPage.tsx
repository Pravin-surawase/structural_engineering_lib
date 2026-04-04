/**
 * BatchDesignPage — Design all imported beams with live SSE progress.
 *
 * Flow: Select beams from store → Start batch design → Live progress → Results table
 */
import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import type { BeamCSVRow } from '../../types/csv';
import {
  Play,
  Loader2,
  CheckCircle,
  XCircle,
  ArrowLeft,
  Download,
  BarChart3,
  AlertTriangle,
} from 'lucide-react';
import { useImportedBeamsStore } from '../../store/importedBeamsStore';
import { useBatchDesign, type BatchResult } from '../../hooks/useBatchDesign';

export default function BatchDesignPage() {
  const navigate = useNavigate();
  const { beams, setBeams } = useImportedBeamsStore();
  const {
    status,
    progress,
    results,
    error,
    duration,
    startBatchDesign,
    cancel,
  } = useBatchDesign();

  const [selectedBeamIds, setSelectedBeamIds] = useState<Set<string>>(
    () => new Set(beams.map(b => b.id))
  );

  // Summary stats
  const stats = useMemo(() => {
    const passed = results.filter(r => r.success).length;
    const failed = results.filter(r => !r.success).length;
    return { passed, failed, total: results.length };
  }, [results]);

  const handleStart = () => {
    const selectedBeams = beams.filter(b => selectedBeamIds.has(b.id));
    if (selectedBeams.length === 0) return;
    startBatchDesign(selectedBeams);
  };

  const handleExportCSV = () => {
    if (results.length === 0) return;
    const headers = ['Beam ID', 'Status', 'Ast Required (mm²)', 'Utilization', 'Stirrup Spacing (mm)', 'Error'];
    const rows = results.map(r => [
      r.beam_id,
      r.success ? 'Pass' : 'Fail',
      r.flexure?.ast_required?.toFixed(1) ?? '',
      r.utilization_ratio?.toFixed(3) ?? '',
      r.shear?.stirrup_spacing?.toFixed(0) ?? '',
      r.error ?? '',
    ]);
    const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'batch_design_results.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  // Apply results back to beam store
  const handleApplyResults = () => {
    const resultMap = new Map(results.filter(r => r.success).map(r => [r.beam_id, r]));
    const updated = beams.map(b => {
      const r = resultMap.get(b.id);
      if (!r) return b;
      return {
        ...b,
        ast_required: r.flexure?.ast_required,
        utilization: r.utilization_ratio,
        stirrup_spacing: r.shear?.stirrup_spacing,
        status: r.success ? 'pass' as const : 'fail' as const,
        is_valid: r.success,
      } as BeamCSVRow;
    });
    setBeams(updated);
  };

  if (beams.length === 0) {
    return (
      <div className="h-screen pt-14 flex flex-col items-center justify-center bg-zinc-950 text-white/60">
        <BarChart3 className="w-12 h-12 mb-4 text-white/20" aria-hidden="true" />
        <p className="text-lg mb-2">No beams imported</p>
        <p className="text-sm mb-6">Import beams from CSV first, then run batch design.</p>
        <button
          onClick={() => navigate('/import')}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500 transition-colors"
        >
          Go to Import
        </button>
      </div>
    );
  }

  return (
    <div className="h-screen pt-14 flex flex-col bg-zinc-950 text-white">
      {/* Header */}
      <div className="px-6 pt-4 pb-3 border-b border-white/8 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate(-1)}
            className="p-1.5 rounded-lg hover:bg-white/10 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <h1 className="text-lg font-semibold">Batch Design</h1>
            <p className="text-xs text-zinc-400">
              Design {selectedBeamIds.size} of {beams.length} beams per IS 456:2000
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {status === 'idle' && (
            <button
              onClick={handleStart}
              disabled={selectedBeamIds.size === 0}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-500 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              <Play className="w-4 h-4" />
              Design All ({selectedBeamIds.size})
            </button>
          )}
          {status === 'running' && (
            <button
              onClick={cancel}
              className="flex items-center gap-2 px-4 py-2 bg-red-600/80 text-white rounded-lg hover:bg-red-500 transition-colors"
            >
              <XCircle className="w-4 h-4" />
              Cancel
            </button>
          )}
          {status === 'complete' && (
            <>
              <button
                onClick={handleApplyResults}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500 transition-colors"
              >
                <CheckCircle className="w-4 h-4" />
                Apply to Beams
              </button>
              <button
                onClick={handleExportCSV}
                className="flex items-center gap-2 px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/15 transition-colors"
              >
                <Download className="w-4 h-4" />
                Export CSV
              </button>
            </>
          )}
        </div>
      </div>

      {/* Progress bar */}
      {status === 'running' && (
        <div className="px-6 py-3 border-b border-white/8">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2 text-sm">
              <Loader2 className="w-4 h-4 animate-spin text-blue-400" />
              <span>Designing beams...</span>
            </div>
            <span className="text-sm text-white/60">
              {progress.completed}/{progress.total}
              {progress.failed > 0 && (
                <span className="text-red-400 ml-2">({progress.failed} failed)</span>
              )}
            </span>
          </div>
          <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-500 rounded-full transition-all duration-300"
              style={{ width: `${progress.percent}%` }}
            />
          </div>
        </div>
      )}

      {/* Complete summary */}
      {status === 'complete' && (
        <div className="px-6 py-3 border-b border-white/8">
          <div className="flex items-center gap-6 text-sm">
            <div className="flex items-center gap-1.5 text-green-400">
              <CheckCircle className="w-4 h-4" />
              {stats.passed} passed
            </div>
            {stats.failed > 0 && (
              <div className="flex items-center gap-1.5 text-red-400">
                <XCircle className="w-4 h-4" />
                {stats.failed} failed
              </div>
            )}
            {duration != null && (
              <span className="text-zinc-400">
                Completed in {duration.toFixed(1)}s
              </span>
            )}
          </div>
        </div>
      )}

      {/* Error banner */}
      {error && (
        <div className="px-6 py-3 bg-red-500/10 border-b border-red-500/20">
          <div className="flex items-center gap-2 text-sm text-red-400">
            <AlertTriangle className="w-4 h-4" />
            {error}
          </div>
        </div>
      )}

      {/* Beam selection / results table */}
      <div className="flex-1 overflow-auto px-6 py-4">
        {status === 'idle' ? (
          <BeamSelectionTable
            beams={beams}
            selectedIds={selectedBeamIds}
            onToggle={(id) => {
              setSelectedBeamIds(prev => {
                const next = new Set(prev);
                if (next.has(id)) next.delete(id);
                else next.add(id);
                return next;
              });
            }}
            onSelectAll={() => setSelectedBeamIds(new Set(beams.map(b => b.id)))}
            onSelectNone={() => setSelectedBeamIds(new Set())}
          />
        ) : (
          <ResultsTable results={results} />
        )}
      </div>
    </div>
  );
}

/* ---- Beam Selection Table ---- */

function BeamSelectionTable({
  beams,
  selectedIds,
  onToggle,
  onSelectAll,
  onSelectNone,
}: {
  beams: { id: string; story?: string; b: number; D: number; mu_envelope?: number; vu_envelope?: number }[];
  selectedIds: Set<string>;
  onToggle: (id: string) => void;
  onSelectAll: () => void;
  onSelectNone: () => void;
}) {
  const allSelected = selectedIds.size === beams.length;

  return (
    <div>
      <div className="flex items-center gap-3 mb-3">
        <button
          onClick={allSelected ? onSelectNone : onSelectAll}
          className="text-xs px-3 py-1 rounded bg-white/10 hover:bg-white/15 transition-colors"
        >
          {allSelected ? 'Deselect All' : 'Select All'}
        </button>
        <span className="text-xs text-zinc-400">
          {selectedIds.size} of {beams.length} selected
        </span>
      </div>

      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-zinc-400 border-b border-white/8">
            <th className="py-2 px-3 w-10"></th>
            <th className="py-2 px-3">Beam ID</th>
            <th className="py-2 px-3">Story</th>
            <th className="py-2 px-3 text-right">Width (mm)</th>
            <th className="py-2 px-3 text-right">Depth (mm)</th>
            <th className="py-2 px-3 text-right">Mu (kN·m)</th>
            <th className="py-2 px-3 text-right">Vu (kN)</th>
          </tr>
        </thead>
        <tbody>
          {beams.map(b => (
            <tr
              key={b.id}
              className={`border-b border-white/5 cursor-pointer transition-colors ${
                selectedIds.has(b.id) ? 'bg-blue-500/10' : 'hover:bg-white/5'
              }`}
              onClick={() => onToggle(b.id)}
            >
              <td className="py-2 px-3">
                <input
                  type="checkbox"
                  checked={selectedIds.has(b.id)}
                  onChange={() => onToggle(b.id)}
                  className="accent-blue-500"
                />
              </td>
              <td className="py-2 px-3 font-mono text-white/80">{b.id}</td>
              <td className="py-2 px-3 text-white/60">{b.story ?? '—'}</td>
              <td className="py-2 px-3 text-right text-white/70">{b.b}</td>
              <td className="py-2 px-3 text-right text-white/70">{b.D}</td>
              <td className="py-2 px-3 text-right text-white/70">
                {b.mu_envelope?.toFixed(1) ?? '—'}
              </td>
              <td className="py-2 px-3 text-right text-white/70">
                {b.vu_envelope?.toFixed(1) ?? '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/* ---- Results Table ---- */

function ResultsTable({ results }: { results: BatchResult[] }) {
  if (results.length === 0) {
    return (
      <div className="flex items-center justify-center h-32 text-zinc-400 text-sm">
        <Loader2 className="w-4 h-4 animate-spin mr-2" />
        Waiting for results...
      </div>
    );
  }

  return (
    <table className="w-full text-sm">
      <thead>
        <tr className="text-left text-zinc-400 border-b border-white/8">
          <th className="py-2 px-3 w-10">Status</th>
          <th className="py-2 px-3">Beam ID</th>
          <th className="py-2 px-3 text-right">Ast Required (mm²)</th>
          <th className="py-2 px-3 text-right">Utilization</th>
          <th className="py-2 px-3 text-right">Stirrup Spacing (mm)</th>
          <th className="py-2 px-3">Notes</th>
        </tr>
      </thead>
      <tbody>
        {results.map((r, i) => (
          <tr key={i} className="border-b border-white/5">
            <td className="py-2 px-3">
              {r.success ? (
                <CheckCircle className="w-4 h-4 text-green-400" />
              ) : (
                <XCircle className="w-4 h-4 text-red-400" />
              )}
            </td>
            <td className="py-2 px-3 font-mono text-white/80">{r.beam_id}</td>
            <td className="py-2 px-3 text-right text-white/70">
              {r.flexure?.ast_required?.toFixed(1) ?? '—'}
            </td>
            <td className="py-2 px-3 text-right">
              <UtilizationBadge value={r.utilization_ratio} />
            </td>
            <td className="py-2 px-3 text-right text-white/70">
              {r.shear?.stirrup_spacing?.toFixed(0) ?? '—'}
            </td>
            <td className="py-2 px-3 text-white/50 text-xs">
              {r.error ?? (r.flexure?.is_under_reinforced ? 'Under-reinforced ✓' : 'Over-reinforced ⚠')}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function UtilizationBadge({ value }: { value?: number }) {
  if (value == null) return <span className="text-zinc-500">—</span>;
  const pct = (value * 100).toFixed(0);
  const color =
    value < 0.7 ? 'text-green-400' :
    value < 0.9 ? 'text-yellow-400' :
    value < 1.0 ? 'text-orange-400' :
    'text-red-400';
  return <span className={`font-mono ${color}`}>{pct}%</span>;
}
