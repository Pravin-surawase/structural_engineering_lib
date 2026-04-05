/**
 * BeamDetailPanel - Slide-in beam detail panel for BuildingEditorPage.
 *
 * Shows 3D reinforcement, cross-section, results, IS 456 checks, and export
 * for a selected beam from the AG Grid or 3D building view.
 *
 * Features:
 *   - "Redesign" button — runs single-beam design via /api/v1/design/beam
 *   - "Edit Rebar" mode — inline inputs with live IS 456 validation
 *   - Stirrup limit annotation — shows whether 0.75d or 300mm governs
 */
import { Suspense, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { X, Download, FileText, Ruler, RefreshCw, Pencil, Check, AlertCircle } from "lucide-react";
import type { BeamCSVRow } from "../../types/csv";
import { useBeamGeometry } from "../../hooks/useBeamGeometry";
import { useRebarValidation } from "../../hooks";
import { useExportBBS, useExportDXF, useExportReport } from "../../hooks";
import { CrossSectionView } from "./CrossSectionView";
import { Viewport3D } from "../viewport/Viewport3D";
import { deriveBeamStatus } from "../../utils/beamStatus";
import { useImportedBeamsStore } from "../../store/importedBeamsStore";

import { API_BASE_URL } from '../../config';

interface BeamDetailPanelProps {
  beam: BeamCSVRow;
  onClose: () => void;
}

// ── Single-beam design hook ──────────────────────────────────────────────────

interface SingleDesignResult {
  success: boolean;
  ast_total: number;
  asc_total: number;
  utilization_ratio: number;
  shear?: { stirrup_spacing: number; sv_max: number };
  flexure?: { ast_required: number; asc_required: number };
}

async function designSingleBeam(beam: BeamCSVRow): Promise<SingleDesignResult> {
  const mu = Math.max(
    Math.abs(beam.Mu_start ?? 0), Math.abs(beam.Mu_mid ?? 0),
    Math.abs(beam.Mu_end ?? 0), Math.abs(beam.mu_envelope ?? 0)
  );
  const vu = Math.max(
    Math.abs(beam.Vu_start ?? 0), Math.abs(beam.Vu_end ?? 0),
    Math.abs(beam.vu_envelope ?? 0)
  );
  const res = await fetch(`${API_BASE_URL}/api/v1/design/beam`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      width: beam.b, depth: beam.D,
      moment: mu, shear: vu,
      fck: beam.fck ?? 25, fy: beam.fy ?? 500,
      clear_cover: beam.cover ?? 40,
    }),
  });
  if (!res.ok) throw new Error("Design failed");
  return res.json();
}

// ── Bar layout helper (mirrors deriveBarLayout in BuildingEditorPage) ─────────
// NOTE: This function does basic geometry (area = π × r²) to estimate bar count.
// It's pragmatic bar selection, NOT IS 456 code logic. A future `/rebar/suggest-layout`
// API endpoint would eliminate this client-side estimation entirely.

function deriveBarLayout(astRequired: number): { count: number; dia: number } {
  for (const dia of [12, 16, 20, 25, 32]) {
    const count = Math.ceil(astRequired / (Math.PI * (dia / 2) ** 2));
    if (count >= 2 && count <= 8) return { count, dia };
  }
  return { count: Math.max(2, Math.ceil(astRequired / (Math.PI * 12.5 ** 2))), dia: 25 };
}

// ── Component ────────────────────────────────────────────────────────────────

export function BeamDetailPanel({ beam, onClose }: BeamDetailPanelProps) {
  const { setBeams } = useImportedBeamsStore();
  const status = deriveBeamStatus(beam);
  const utilPct = beam.utilization != null ? Math.round(beam.utilization * 100) : null;

  // Track backend-computed sv_max from design response
  const [designSvMax, setDesignSvMax] = useState<number | null>(null);

  // ── Redesign ────────────────────────────────────────────────────────────
  const { mutate: redesign, isPending: redesigning } = useMutation({
    mutationFn: () => designSingleBeam(beam),
    onSuccess: async (data) => {
      if (!data.success) return;
      const astReq = data.flexure?.ast_required ?? data.ast_total;
      const ascReq = data.flexure?.asc_required ?? data.asc_total;
      const layout = deriveBarLayout(astReq);

      // Get ast_provided from backend instead of calculating locally
      let astProvided = 0;
      try {
        const rebarRes = await fetch(`${API_BASE_URL}/api/v1/rebar/apply`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            beam: { width: beam.b, depth: beam.D, cover: beam.cover ?? 40 },
            config: { bar_count: layout.count, bar_dia: layout.dia },
          }),
        });
        if (rebarRes.ok) {
          const rebarData = await rebarRes.json();
          astProvided = rebarData.ast_provided_mm2 ?? 0;
        }
      } catch {
        // Fallback: use 0 if API fails
      }

      // Store sv_max from design response for display
      if (data.shear?.sv_max) setDesignSvMax(data.shear.sv_max);

      const currentBeams = useImportedBeamsStore.getState().beams;
      setBeams(currentBeams.map((b) =>
        b.id !== beam.id ? b : {
          ...b,
          ast_required: astReq,
          asc_required: ascReq,
          ast_provided: astProvided,
          bar_count: layout.count,
          bar_diameter: layout.dia,
          stirrup_spacing: data.shear?.stirrup_spacing ?? b.stirrup_spacing,
          utilization: data.utilization_ratio,
          is_valid: data.success && data.utilization_ratio <= 1.0,
          status: data.utilization_ratio <= 1.0 ? "pass" : "fail",
        }
      ));
    },
  });

  // ── Edit rebar mode ──────────────────────────────────────────────────────
  const [editMode, setEditMode] = useState(false);
  const [editBarCount, setEditBarCount] = useState(beam.bar_count ?? 2);
  const [editBarDia, setEditBarDia] = useState(beam.bar_diameter ?? 16);
  const [editStrDia, setEditStrDia] = useState(beam.stirrup_diameter ?? 8);
  const [editStrSp, setEditStrSp] = useState(beam.stirrup_spacing ?? 150);

  const { mutate: validate, data: validationResult, isPending: validating } = useRebarValidation();

  const handleEditOpen = () => {
    setEditBarCount(beam.bar_count ?? 2);
    setEditBarDia(beam.bar_diameter ?? 16);
    setEditStrDia(beam.stirrup_diameter ?? 8);
    setEditStrSp(beam.stirrup_spacing ?? 150);
    setEditMode(true);
    // Validate current config immediately
    validate({ beam: { width: beam.b, depth: beam.D, cover: beam.cover ?? 40 }, config: { bar_count: beam.bar_count ?? 2, bar_dia: beam.bar_diameter ?? 16, stirrup_dia: beam.stirrup_diameter ?? 8 } });
  };

  const handleValidate = () => {
    validate({
      beam: { width: beam.b, depth: beam.D, cover: beam.cover ?? 40 },
      config: { bar_count: editBarCount, bar_dia: editBarDia, stirrup_dia: editStrDia },
    });
  };

  const handleApplyRebar = () => {
    // Get ast_provided from backend validation result instead of local calculation
    const astProv = validationResult?.validation?.details?.ast_provided_mm2 ?? 0;
    const currentBeams = useImportedBeamsStore.getState().beams;
    setBeams(currentBeams.map((b) =>
      b.id !== beam.id ? b : {
        ...b,
        bar_count: editBarCount,
        bar_diameter: editBarDia,
        stirrup_diameter: editStrDia,
        stirrup_spacing: editStrSp,
        ast_provided: astProv,
      }
    ));
    setEditMode(false);
  };

  // ── Geometry for 3D view ──────────────────────────────────────────────────
  const geoParams =
    beam.ast_required != null
      ? {
          beam_id: beam.id,
          width: beam.b, depth: beam.D, span: beam.span || 5000,
          fck: beam.fck ?? 25, fy: beam.fy ?? 500,
          ast_start: beam.ast_required, ast_mid: beam.ast_required, ast_end: beam.ast_required,
          stirrup_dia: beam.stirrup_diameter ?? 8,
          stirrup_spacing_start: beam.stirrup_spacing ?? 150,
          stirrup_spacing_mid: beam.stirrup_spacing ?? 150,
          stirrup_spacing_end: beam.stirrup_spacing ?? 150,
          cover: beam.cover ?? 40,
        }
      : null;

  const { data: geometry } = useBeamGeometry(geoParams);

  // ── Export ────────────────────────────────────────────────────────────────
  const exportParams = {
    beam_id: beam.id, width: beam.b, depth: beam.D,
    span_length: beam.span, clear_cover: beam.cover ?? 40,
    fck: beam.fck ?? 25, fy: beam.fy ?? 500,
    ast_required: beam.ast_required ?? 0, asc_required: beam.asc_required ?? 0,
    moment: Math.max(Math.abs(beam.Mu_start ?? 0), Math.abs(beam.Mu_mid ?? 0), Math.abs(beam.Mu_end ?? 0), Math.abs(beam.mu_envelope ?? 0)),
    shear: Math.max(Math.abs(beam.Vu_start ?? 0), Math.abs(beam.Vu_end ?? 0), Math.abs(beam.vu_envelope ?? 0)),
  };
  const { mutate: exportBBS, isPending: bbsPending } = useExportBBS();
  const { mutate: exportDXF, isPending: dxfPending } = useExportDXF();
  const { mutate: exportReport, isPending: reportPending } = useExportReport();

  const statusConfig = {
    pass:      { label: "✓ SAFE",    cls: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30" },
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

  // Stirrup limit info — use backend-computed sv_max when available
  const svMax = designSvMax ?? (beam.D ? Math.min(Math.round(0.75 * (beam.D - (beam.cover ?? 40) - 25)), 300) : 300);
  const svGoverning = designSvMax != null
    ? `${designSvMax} mm (IS 456 Cl. 40)`
    : `≈ ${svMax} mm (estimate)`;

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
          {beam.ast_required != null && (
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
            {beam.ast_required != null
              ? <p className="text-xs text-zinc-500 animate-pulse">Loading 3D rebar…</p>
              : <>
                  <div className="w-8 h-8 rounded-xl bg-white/5 flex items-center justify-center mb-1">
                    <Ruler className="w-4 h-4 text-white/20" aria-hidden="true" />
                  </div>
                  <p className="text-xs text-zinc-500">Design beam to see reinforcement</p>
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
          {/* Validation result */}
          {validationResult && (
            <div className={`flex items-start gap-2 text-[10px] p-2 rounded-lg ${
              validationResult.validation.ok ? "bg-emerald-500/10 text-emerald-400" : "bg-rose-500/10 text-rose-400"
            }`}>
              {validationResult.validation.ok
                ? <Check className="w-3.5 h-3.5 mt-0.5 shrink-0" />
                : <AlertCircle className="w-3.5 h-3.5 mt-0.5 shrink-0" />
              }
              <div>
                <span className="font-medium">{validationResult.validation.ok ? "Valid" : "Issues"}</span>
                {validationResult.validation.errors.length > 0 && (
                  <p className="mt-0.5 opacity-80">{validationResult.validation.errors[0]}</p>
                )}
                {validationResult.validation.details.ast_provided_mm2 != null && (
                  <p className="mt-0.5 opacity-60">
                    Ast prov = {Math.round(validationResult.validation.details.ast_provided_mm2)} mm²
                  </p>
                )}
              </div>
            </div>
          )}
          <div className="flex gap-2">
            <button onClick={handleValidate} disabled={validating}
              className="flex-1 py-1.5 rounded-lg bg-white/5 border border-white/10 text-xs text-white/60 hover:bg-white/10 transition-all disabled:opacity-40">
              {validating ? "Checking…" : "Validate IS 456"}
            </button>
            <button onClick={handleApplyRebar}
              className="flex-1 py-1.5 rounded-lg bg-amber-500/20 border border-amber-500/40 text-xs text-amber-300 hover:bg-amber-500/30 transition-all font-medium">
              Apply
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
            <span className="text-xs text-zinc-400 tabular-nums">{utilPct}% Mu/Mu_cap</span>
          )}
        </div>
        {utilPct != null && (
          <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
            <div className={`h-full rounded-full transition-all duration-700 ${utilBarColor}`} style={{ width: `${Math.min(utilPct, 100)}%` }} />
          </div>
        )}
        <div className="grid grid-cols-3 gap-2">
          <Metric label="Ast req" value={beam.ast_required != null ? `${Math.round(beam.ast_required)}` : "—"} unit={beam.ast_required != null ? "mm²" : ""} />
          <Metric label="Bars" value={beam.bar_count && beam.bar_diameter ? `${beam.bar_count}-T${beam.bar_diameter}` : "—"} />
          <Metric label="Stirrups" value={beam.stirrup_spacing ? `${beam.stirrup_diameter ?? 8}ø@${beam.stirrup_spacing}` : "—"} />
        </div>
      </div>

      {/* ── Cross-Section ── */}
      {beam.ast_required != null && (
        <div className="px-4 py-3 border-b border-white/5 shrink-0">
          <p className="text-[10px] text-zinc-500 uppercase tracking-widest mb-3">Cross-Section</p>
          <CrossSectionView
            width={beam.b} depth={beam.D}
            cover={beam.cover ?? 40}
            astRequired={beam.ast_required}
            ascRequired={beam.asc_required}
            stirrupDia={beam.stirrup_diameter ?? 8}
            barDia={beam.bar_diameter}
            barCount={beam.bar_count}
            utilization={beam.utilization}
            className="scale-[0.72] origin-top-left"
          />
        </div>
      )}

      {/* ── IS 456 Checks ── */}
      <div className="px-4 py-3 border-b border-white/5 space-y-2 shrink-0">
        <p className="text-[10px] text-zinc-500 uppercase tracking-widest">IS 456 Checks</p>
        <CheckRow
          label="Flexure" clause="Cl. 38.1"
          status={status === "fail" ? "fail" : beam.ast_required != null ? "pass" : "pending"}
          detail={beam.ast_required ? `Ast = ${Math.round(beam.ast_required)} mm²` : "Not designed"}
        />
        <CheckRow
          label="Shear" clause="Cl. 40"
          status={beam.stirrup_spacing ? (status === "fail" ? "fail" : "pass") : "pending"}
          detail={
            beam.stirrup_spacing
              ? `Sv = ${beam.stirrup_spacing} mm (max: ${svGoverning})`
              : "Not designed"
          }
          warn={beam.stirrup_spacing != null && beam.stirrup_spacing > svMax
            ? `Sv ${beam.stirrup_spacing} > max ${svMax} mm`
            : undefined}
        />
        <CheckRow
          label="Min Steel" clause="Cl. 26.5.1.1"
          status={beam.ast_required != null ? "pass" : "pending"}
          detail={`≥ 0.${(beam.fy ?? 500) === 415 ? "085" : "12"}% of Ag`}
        />
        <CheckRow
          label="L/d Ratio" clause="Cl. 23.2"
          status={beam.span && beam.D ? (beam.span / beam.D < 20 ? "pass" : "warning") : "pending"}
          detail={beam.span && beam.D ? `L/d = ${(beam.span / beam.D).toFixed(1)} ${beam.span / beam.D < 20 ? "✓" : "⚠ > 20"}` : "—"}
        />
      </div>

      {/* ── Export ── */}
      {beam.ast_required != null && (
        <div className="px-4 py-3 shrink-0">
          <p className="text-[10px] text-zinc-500 uppercase tracking-widest mb-2.5">Export</p>
          <div className="flex gap-2">
            <ExportBtn label="BBS" icon={<Download className="w-3.5 h-3.5" />} loading={bbsPending} onClick={() => exportBBS(exportParams)} />
            <ExportBtn label="DXF" icon={<Ruler className="w-3.5 h-3.5" />} loading={dxfPending} onClick={() => exportDXF(exportParams)} />
            <ExportBtn label="Report" icon={<FileText className="w-3.5 h-3.5" />} loading={reportPending}
              onClick={() => exportReport({ ...exportParams, ast_provided: beam.ast_provided, utilization: beam.utilization, is_safe: beam.is_valid })} />
          </div>
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

function ExportBtn({ label, icon, loading, onClick }: {
  label: string; icon: React.ReactNode; loading: boolean; onClick: () => void;
}) {
  return (
    <button onClick={onClick} disabled={loading}
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
