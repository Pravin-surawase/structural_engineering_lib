/**
 * BeamDetailPanel - Slide-in beam detail panel for BuildingEditorPage.
 *
 * Shows 3D reinforcement, cross-section, results, IS 456 checks, and export
 * for a selected beam from the AG Grid or 3D building view.
 *
 * Features:
 *   - Rechecks one imported member through the revision-bound batch route.
 *   - Uses the checked physical layout for the view and every download.
 */
import { Suspense, useState } from "react";
import { X, Download, FileText, Ruler, RefreshCw, Pencil } from "lucide-react";
import type { BeamCSVRow } from "../../types/csv";
import { useBeamGeometry } from "../../hooks/useBeamGeometry";
import { useExportBBS, useExportDXF, useExportReport } from "../../hooks";
import { CrossSectionView } from "./CrossSectionView";
import { Viewport3D } from "../viewport/Viewport3D";
import { deriveBeamStatus } from "../../utils/beamStatus";
import { useImportedBeamsStore } from "../../store/importedBeamsStore";
import { formatPercent, formatRatio } from "../../utils/trustPresentation";

import { useBatchDesign } from "../../hooks/useBatchDesign";
import { currentWorkbenchLayout } from "../../workspace/resultRecords";
import { useWorkspaceStore } from "../../workspace/workspaceStore";
import type { WorkbenchExportParams } from "../../hooks/useExport";

interface BeamDetailPanelProps {
  beam: BeamCSVRow;
  onClose: () => void;
}

export function BeamDetailPanel({ beam, onClose }: BeamDetailPanelProps) {
  const memberId = beam.source_id ?? beam.id;
  const snapshot = useWorkspaceStore((state) => state.snapshot);
  const layout = currentWorkbenchLayout(snapshot, memberId);
  const mid = layout?.zones.find((zone) => zone.zone === "mid");
  const rawStatus = deriveBeamStatus(beam);
  const status = !layout && rawStatus === "pass" ? "warning" : rawStatus;
  const utilPct = layout ? layout.utilization * 100 : null;
  const { startBatchDesign, status: batchStatus } = useBatchDesign();
  const redesigning = batchStatus === "running";
  const redesign = () => startBatchDesign([beam]);

  const [editMode, setEditMode] = useState(false);
  const [editBarCount, setEditBarCount] = useState(mid?.tension.count ?? 2);
  const [editBarDia, setEditBarDia] = useState(mid?.tension.diameter_mm ?? 16);
  const [editStrDia, setEditStrDia] = useState(mid?.stirrup.diameter_mm ?? 8);
  const [editStrSp, setEditStrSp] = useState(mid?.stirrup.spacing_mm ?? 150);
  const handleEditOpen = () => {
    setEditBarCount(beam.requested_bar_count ?? mid?.tension.count ?? 2);
    setEditBarDia(beam.tension_bar_diameter_mm ?? mid?.tension.diameter_mm ?? 16);
    setEditStrDia(beam.stirrup_diameter_mm ?? mid?.stirrup.diameter_mm ?? 8);
    setEditStrSp(beam.requested_stirrup_spacing_mm ?? mid?.stirrup.spacing_mm ?? 150);
    setEditMode(true);
  };
  const handleApplyRebar = () => {
    const store = useImportedBeamsStore.getState();
    const current = store.beams.find((item) => (item.source_id ?? item.id) === memberId);
    if (!current) return;
    const edited: BeamCSVRow = {
      ...current,
      tension_bar_diameter_mm: editBarDia,
      stirrup_diameter_mm: editStrDia,
      requested_bar_count: editBarCount,
      requested_stirrup_spacing_mm: editStrSp,
      status: "pending",
      is_valid: false,
    };
    store.setBeams(store.beams.map((item) => item === current ? edited : item));
    if (useImportedBeamsStore.getState().error) return;
    setEditMode(false);
    startBatchDesign([edited]);
  };

  const exportParams = (current: typeof layout): WorkbenchExportParams | null => current ? {
    checked_request: current.checked_request,
    checked_layout_id: current.checked_layout_id,
  } : null;
  const { data: geometry, isPending: geometryPending } = useBeamGeometry(exportParams(layout));
  const { mutate: exportBBS, isPending: bbsPending } = useExportBBS();
  const { mutate: exportDXF, isPending: dxfPending } = useExportDXF();
  const { mutate: exportReport, isPending: reportPending } = useExportReport();
  const exportHeld = !layout || editMode || redesigning;
  const downloadChecked = (download: (params: WorkbenchExportParams) => void) => {
    if (editMode || redesigning) return;
    const current = currentWorkbenchLayout(useWorkspaceStore.getState().snapshot, memberId);
    const params = exportParams(current);
    if (params) download(params);
  };

  const statusConfig = {
    pass:      { label: "✓ PASS",    cls: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30" },
    fail:      { label: "✕ FAIL",    cls: "text-rose-400 bg-rose-500/10 border-rose-500/30" },
    warning:   { label: "⚠ CHECK",   cls: "text-amber-400 bg-amber-500/10 border-amber-500/30" },
    pending:   { label: "PENDING",   cls: "text-zinc-400 bg-white/5 border-white/10" },
    designing: { label: "DESIGNING", cls: "text-blue-400 bg-blue-500/10 border-blue-500/30 animate-pulse" },
  };

  const utilBarColor =
    utilPct == null      ? "bg-white/20"      :
    utilPct > 100        ? "bg-rose-500"      :
    utilPct > 90         ? "bg-amber-400"     :
    utilPct > 75         ? "bg-amber-400/70"  :
                           "bg-emerald-400";

  const svMax = layout?.shear_spacing_limit_mm;
  const svGoverning = svMax == null ? "—" : `${svMax} mm (IS 456 Cl. 40)`;

  return (
    <div className="flex flex-col h-full bg-zinc-950 border-l border-white/5 overflow-y-auto">

      {/* ── Header ── */}
      <div className="flex items-start justify-between px-4 pt-3 pb-2.5 border-b border-white/5 shrink-0">
        <div className="min-w-0 flex-1">
          <p className="text-[10px] text-zinc-500 uppercase tracking-widest mb-0.5">{beam.story ?? "—"}</p>
          <p className="text-sm font-semibold text-white truncate">{beam.id}</p>
          <p className="text-xs text-zinc-400 mt-0.5 font-mono">{beam.b}×{beam.D} mm &middot; {beam.span ? `${beam.span} mm` : "span —"}</p>
          <p className="text-[10px] text-zinc-500 mt-0.5">M{beam.fck ?? 25} &middot; Fe{beam.fy ?? 500} &middot; {beam.cover ?? 40}mm cover</p>
        </div>
        <div className="flex items-center gap-1.5 mt-0.5 shrink-0">
          {(beam.ast_required != null || !layout) && (
            <button
              onClick={() => { if (!redesigning) redesign(); }}
              disabled={redesigning}
              title="Re-run design with current forces"
              className="flex items-center gap-1 px-2 py-1 rounded-md text-[10px] font-medium
                bg-blue-500/10 border border-blue-500/30 text-blue-400
                hover:bg-blue-500/20 hover:text-blue-300 transition-all disabled:opacity-40"
            >
              <RefreshCw className={`w-3 h-3 ${redesigning ? "animate-spin" : ""}`} />
              {redesigning ? "…" : "Redesign"}
            </button>
          )}
          <button
            onClick={() => editMode ? setEditMode(false) : handleEditOpen()}
            title="Edit reinforcement"
            className={`flex items-center gap-1 px-2 py-1 rounded-md text-[10px] font-medium transition-all
              ${editMode
                ? "bg-amber-500/20 border border-amber-500/40 text-amber-300"
                : "bg-white/5 border border-white/10 text-zinc-400 hover:text-zinc-200 hover:bg-white/10"
              }`}
          >
            <Pencil className="w-3 h-3" />
            {editMode ? "Editing" : "Edit Rebar"}
          </button>
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-white/5 text-zinc-500 hover:text-zinc-200 transition-colors">
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* ── 3D Reinforcement View ── */}
      <div className="h-[210px] shrink-0 border-b border-white/5 relative bg-[#0f1320]">
        {geometry ? (
          <Suspense fallback={<Spinner />}>
            <Viewport3D
              mode="design" forceMode
              overrideGeometry={{ rebars: geometry.rebars, stirrups: geometry.stirrups }}
              overrideDimensions={{ width: beam.b, depth: beam.D, span: beam.span || 5000 }}
            />
          </Suspense>
        ) : (
          <div className="flex flex-col items-center justify-center h-full gap-1.5">
            {layout && geometryPending
              ? <p className="text-xs text-zinc-500 animate-pulse">Loading checked reinforcement…</p>
              : <>
                  <div className="w-8 h-8 rounded-xl bg-white/5 flex items-center justify-center mb-1">
                    <Ruler className="w-4 h-4 text-white/20" aria-hidden="true" />
                  </div>
                  <p className="text-xs text-zinc-500">Check this beam to see its reinforcement</p>
                </>
            }
          </div>
        )}
        {geometry && (
          <div className="absolute bottom-2 right-2 text-[9px] text-zinc-500 font-mono">
            {geometry.rebars.length}b &middot; {geometry.stirrups.length}s
          </div>
        )}
      </div>

      {/* ── Edit Rebar Mode ── */}
      {editMode && (
        <div className="px-4 py-3 border-b border-amber-500/20 bg-amber-500/[0.03] space-y-3 shrink-0">
          <p className="text-[10px] text-amber-400/70 uppercase tracking-widest">Override Reinforcement</p>
          <div className="grid grid-cols-2 gap-2">
            <EditField label="Bar Count" value={editBarCount} onChange={setEditBarCount} min={2} max={12} />
            <EditField label="Bar Ø (mm)" value={editBarDia} onChange={setEditBarDia} options={[10,12,16,20,25,32]} />
            <EditField label="Stirrup Ø" value={editStrDia} onChange={setEditStrDia} options={[6,8,10,12]} />
            <EditField label="Sv (mm)" value={editStrSp} onChange={setEditStrSp} options={[75,100,125,150,175,200,225,250,275,300]} />
          </div>
          <p className="text-xs text-zinc-400">Saving these inputs checks a new layout and invalidates the old downloads.</p>
          <div className="flex gap-2">
            <button onClick={handleApplyRebar} disabled={redesigning}
              className="flex-1 py-1.5 rounded-lg bg-amber-500/20 border border-amber-500/40 text-xs text-amber-300 hover:bg-amber-500/30 transition-all font-medium">
              Save and check
            </button>
          </div>
        </div>
      )}

      {/* ── Result Bar ── */}
      <div className="px-4 py-3 border-b border-white/5 space-y-2.5 shrink-0">
        <div className="flex items-center gap-2">
          <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${statusConfig[status]?.cls ?? statusConfig.pending.cls}`}>
            {statusConfig[status]?.label ?? status.toUpperCase()}
          </span>
          {utilPct != null && (
            <span className="text-xs text-zinc-400 tabular-nums">
              {formatPercent(layout?.utilization ?? 0)} · ratio {formatRatio(layout?.utilization ?? 0)}
            </span>
          )}
        </div>
        {utilPct != null && (
          <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
            <div className={`h-full rounded-full transition-all duration-700 ${utilBarColor}`} style={{ width: `${Math.min(utilPct, 100)}%` }} />
          </div>
        )}
        <div className="grid grid-cols-3 gap-2">
          <Metric label="Ast req" value={beam.ast_required != null ? `${Math.round(beam.ast_required)}` : "—"} unit={beam.ast_required != null ? "mm²" : ""} />
          <Metric label="Midspan bars" value={mid ? `${mid.tension.count}Ø${mid.tension.diameter_mm}` : "—"} />
          <Metric label="Midspan stirrups" value={mid ? `Ø${mid.stirrup.diameter_mm} @ ${mid.stirrup.spacing_mm}` : "—"} />
        </div>
      </div>

      {/* ── Cross-Section ── */}
      {layout && mid && (
        <div className="px-4 py-3 border-b border-white/5 shrink-0">
          <p className="text-[10px] text-zinc-500 uppercase tracking-widest mb-3">Checked reinforcement by zone</p>
          <table className="w-full text-left text-xs text-zinc-300">
            <thead><tr><th>Zone</th><th>Bottom</th><th>Top</th><th>Stirrups</th></tr></thead>
            <tbody>{layout.zones.map((zone) => (
              <tr key={zone.zone}>
                <th scope="row">{zone.zone}</th>
                <td>{zone.tension.count}Ø{zone.tension.diameter_mm}</td>
                <td>{zone.compression.count}Ø{zone.compression.diameter_mm}</td>
                <td>Ø{zone.stirrup.diameter_mm} @ {zone.stirrup.spacing_mm} mm ({zone.stirrup.count})</td>
              </tr>
            ))}</tbody>
          </table>
          <p className="text-[10px] text-zinc-500 uppercase tracking-widest mt-3">Midspan cross-section</p>
          <CrossSectionView
            width={beam.b} depth={beam.D}
            cover={beam.cover ?? 40}
            astRequired={layout.ast_required_mm2}
            stirrupDia={mid.stirrup.diameter_mm}
            barDia={mid.tension.diameter_mm}
            barCount={mid.tension.count}
            topBarDia={mid.compression.diameter_mm}
            topBarCount={mid.compression.count}
            utilization={layout.utilization}
            className="scale-[0.72] origin-top-left"
          />
        </div>
      )}

      {/* ── IS 456 Checks ── */}
      <div className="px-4 py-3 border-b border-white/5 space-y-2 shrink-0">
        <p className="text-[10px] text-zinc-500 uppercase tracking-widest">IS 456 Checks</p>
        <CheckRow
          label="Flexure" clause="Cl. 38.1"
          status={status === "fail" ? "fail" : layout ? "pass" : "pending"}
          detail={beam.ast_required ? `Ast = ${Math.round(beam.ast_required)} mm²` : "Not designed"}
        />
        <CheckRow
          label="Shear" clause="Cl. 40"
          status={layout ? "pass" : status === "fail" ? "fail" : "pending"}
          detail={
            mid
              ? `Sv = ${mid.stirrup.spacing_mm} mm (max: ${svGoverning})`
              : "Not designed"
          }
        />
        {layout && (
          <p className="text-[10px] text-zinc-400">
            Qualified review required. This check covers the supplied factored moment and shear.
          </p>
        )}
      </div>

      {/* ── Export ── */}
      {beam.ast_required != null && (
        <div className="px-4 py-3 shrink-0">
          <p className="text-[10px] text-zinc-500 uppercase tracking-widest mb-2.5">Export</p>
          <div className="flex gap-2">
            <ExportBtn label="BBS" icon={<Download className="w-3.5 h-3.5" />} loading={bbsPending} disabled={exportHeld} onClick={() => downloadChecked(exportBBS)} />
            <ExportBtn label="DXF" icon={<Ruler className="w-3.5 h-3.5" />} loading={dxfPending} disabled={exportHeld} onClick={() => downloadChecked(exportDXF)} />
            <ExportBtn label="Report" icon={<FileText className="w-3.5 h-3.5" />} loading={reportPending} disabled={exportHeld}
              onClick={() => downloadChecked(exportReport)} />
          </div>
          {exportHeld && (
            <p className="mt-2 text-[10px] text-amber-400/80" role="status">
              {beam.remarks?.[0] || "Exports require a current checked reinforcement layout."}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

/* ── Sub-components ─────────────────────────────────────────────────────────── */

function Spinner() {
  return (
    <div className="flex items-center justify-center h-full">
      <div className="w-5 h-5 rounded-full border-2 border-white/10 border-t-white/40 animate-spin" />
    </div>
  );
}

function Metric({ label, value, unit = "" }: { label: string; value: string; unit?: string }) {
  return (
    <div className="p-2 rounded-lg bg-white/[0.03] border border-white/[0.06]">
      <p className="text-[9px] text-zinc-500 uppercase tracking-wider mb-0.5">{label}</p>
      <p className="text-xs font-medium text-white tabular-nums">
        {value}
        {unit && <span className="text-[10px] text-zinc-400 ml-0.5">{unit}</span>}
      </p>
    </div>
  );
}

function CheckRow({ label, clause, status, detail, warn }: {
  label: string; clause: string;
  status: "pass" | "fail" | "warning" | "pending";
  detail: string;
  warn?: string;
}) {
  const dot = { pass: "bg-emerald-400", fail: "bg-rose-400", warning: "bg-amber-400", pending: "bg-zinc-600" }[status];
  return (
    <div className="flex items-start gap-2.5 py-1.5">
      <div className={`w-1.5 h-1.5 rounded-full mt-1 shrink-0 ${dot}`} />
      <div className="min-w-0 flex-1">
        <div className="flex items-baseline gap-2">
          <span className="text-xs text-white/70 font-medium">{label}</span>
          <span className="text-[9px] text-zinc-500">{clause}</span>
        </div>
        <p className="text-[10px] text-zinc-400 mt-0.5 truncate">{detail}</p>
        {warn && <p className="text-[10px] text-rose-400/70 mt-0.5">{warn}</p>}
      </div>
    </div>
  );
}

function ExportBtn({ label, icon, loading, disabled = false, onClick }: {
  label: string; icon: React.ReactNode; loading: boolean; disabled?: boolean; onClick: () => void;
}) {
  return (
    <button onClick={onClick} disabled={loading || disabled}
      className="flex-1 flex items-center justify-center gap-1.5 px-2 py-2 rounded-lg
        bg-white/[0.04] border border-white/[0.08] text-xs text-white/60
        hover:bg-white/[0.07] hover:text-white/90 hover:border-white/15
        transition-all disabled:opacity-40 disabled:cursor-not-allowed">
      {loading ? <div className="w-3.5 h-3.5 rounded-full border border-white/30 border-t-white/70 animate-spin" /> : icon}
      {label}
    </button>
  );
}

function EditField({ label, value, onChange, min, max, options }: {
  label: string; value: number; onChange: (v: number) => void;
  min?: number; max?: number; options?: number[];
}) {
  const fieldId = `edit-${label.toLowerCase().replace(/\s+/g, '-')}`;
  if (options) {
    return (
      <div>
        <label htmlFor={fieldId} className="text-[9px] text-zinc-500 uppercase tracking-wider mb-1 block">
          {label}
        </label>
        <select
          id={fieldId}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          aria-label={label}
          className="w-full px-2 py-1 text-xs text-white bg-white/[0.05] border border-white/10 rounded-md appearance-none focus:outline-none focus:ring-1 focus:ring-amber-500/50"
        >
          {options.map((o) => <option key={o} value={o} className="bg-zinc-900">{o}</option>)}
        </select>
      </div>
    );
  }
  return (
    <div>
      <label htmlFor={fieldId} className="text-[9px] text-zinc-500 uppercase tracking-wider mb-1 block">
        {label}
      </label>
      <input
        id={fieldId}
        type="number"
        value={value}
        min={min}
        max={max}
        onChange={(e) => onChange(Number(e.target.value))}
        aria-label={label}
        className="w-full px-2 py-1 text-xs text-white bg-white/[0.05] border border-white/10 rounded-md focus:outline-none focus:ring-1 focus:ring-amber-500/50"
      />
    </div>
  );
}
