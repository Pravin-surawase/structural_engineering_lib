/**
 * BeamDetailPanel - Slide-in beam detail panel for BuildingEditorPage.
 *
 * Shows 3D reinforcement, cross-section, results, IS 456 checks, and export
 * for a selected beam from the AG Grid or 3D building view.
 *
 * Layout (top-to-bottom):
 *   Header (beam ID + story + close)
 *   3D rebar viewport (200px)
 *   Result bar (status + utilization + key numbers)
 *   Cross-section SVG
 *   IS 456 checks
 *   Export buttons
 */
import { Suspense } from "react";
import { X, Download, FileText, Ruler } from "lucide-react";
import type { BeamCSVRow } from "../../types/csv";
import { useBeamGeometry } from "../../hooks/useBeamGeometry";
import { useExportBBS, useExportDXF, useExportReport } from "../../hooks";
import { CrossSectionView } from "./CrossSectionView";
import { Viewport3D } from "../viewport/Viewport3D";
import { deriveBeamStatus } from "../../utils/beamStatus";

interface BeamDetailPanelProps {
  beam: BeamCSVRow;
  onClose: () => void;
}

export function BeamDetailPanel({ beam, onClose }: BeamDetailPanelProps) {
  const status = deriveBeamStatus(beam);
  const utilPct = beam.utilization != null ? Math.round(beam.utilization * 100) : null;

  // Build geometry request only when beam has been designed
  const geoParams =
    beam.ast_required != null
      ? {
          beam_id: beam.id,
          width: beam.b,
          depth: beam.D,
          span: beam.span || 5000,
          fck: beam.fck ?? 25,
          fy: beam.fy ?? 500,
          ast_start: beam.ast_required,
          ast_mid: beam.ast_required,
          ast_end: beam.ast_required,
          stirrup_dia: beam.stirrup_diameter ?? 8,
          stirrup_spacing_start: beam.stirrup_spacing ?? 150,
          stirrup_spacing_mid: beam.stirrup_spacing ?? 150,
          stirrup_spacing_end: beam.stirrup_spacing ?? 150,
          cover: beam.cover ?? 40,
        }
      : null;

  const { data: geometry } = useBeamGeometry(geoParams);

  const exportParams = {
    beam_id: beam.id,
    width: beam.b,
    depth: beam.D,
    span_length: beam.span,
    clear_cover: beam.cover ?? 40,
    fck: beam.fck ?? 25,
    fy: beam.fy ?? 500,
    ast_required: beam.ast_required ?? 0,
    asc_required: beam.asc_required ?? 0,
    moment: Math.max(
      Math.abs(beam.Mu_start ?? 0),
      Math.abs(beam.Mu_mid ?? 0),
      Math.abs(beam.Mu_end ?? 0),
      Math.abs(beam.mu_envelope ?? 0)
    ),
    shear: Math.max(
      Math.abs(beam.Vu_start ?? 0),
      Math.abs(beam.Vu_end ?? 0),
      Math.abs(beam.vu_envelope ?? 0)
    ),
  };

  const { mutate: exportBBS, isPending: bbsPending } = useExportBBS();
  const { mutate: exportDXF, isPending: dxfPending } = useExportDXF();
  const { mutate: exportReport, isPending: reportPending } = useExportReport();

  const statusConfig = {
    pass:      { label: "✓ SAFE",   cls: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30" },
    fail:      { label: "✕ FAIL",   cls: "text-rose-400 bg-rose-500/10 border-rose-500/30" },
    warning:   { label: "⚠ CHECK",  cls: "text-amber-400 bg-amber-500/10 border-amber-500/30" },
    pending:   { label: "PENDING",  cls: "text-white/40 bg-white/5 border-white/10" },
    designing: { label: "DESIGNING",cls: "text-blue-400 bg-blue-500/10 border-blue-500/30 animate-pulse" },
  };

  const utilBarColor =
    utilPct == null      ? "bg-white/20"   :
    utilPct > 100        ? "bg-rose-500"   :
    utilPct > 90         ? "bg-amber-400"  :
    utilPct > 75         ? "bg-amber-400/70" :
                           "bg-emerald-400";

  return (
    <div className="flex flex-col h-full bg-zinc-950 border-l border-white/5 overflow-y-auto">

      {/* ── Header ── */}
      <div className="flex items-start justify-between px-4 pt-3 pb-2.5 border-b border-white/5 shrink-0">
        <div className="min-w-0">
          <p className="text-[10px] text-white/30 uppercase tracking-widest mb-0.5">
            {beam.story ?? "—"}
          </p>
          <p className="text-sm font-semibold text-white truncate">{beam.id}</p>
          <p className="text-xs text-white/40 mt-0.5 font-mono">
            {beam.b}×{beam.D} mm &middot; {beam.span ? `${beam.span} mm span` : "span —"}
          </p>
          <p className="text-[10px] text-white/25 mt-0.5">
            M{beam.fck ?? 25} &middot; Fe{beam.fy ?? 500} &middot; {beam.cover ?? 40}mm cover
          </p>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-lg hover:bg-white/5 text-white/25 hover:text-white/60 transition-colors shrink-0 mt-0.5"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* ── 3D Reinforcement View ── */}
      <div className="h-[210px] shrink-0 border-b border-white/5 relative bg-[#0f1320]">
        {geometry ? (
          <Suspense fallback={<Spinner />}>
            <Viewport3D
              mode="design"
              forceMode
              overrideGeometry={{ rebars: geometry.rebars, stirrups: geometry.stirrups }}
              overrideDimensions={{ width: beam.b, depth: beam.D, span: beam.span || 5000 }}
            />
          </Suspense>
        ) : (
          <div className="flex flex-col items-center justify-center h-full gap-1.5">
            {beam.ast_required != null ? (
              <p className="text-xs text-white/30 animate-pulse">Loading 3D rebar…</p>
            ) : (
              <>
                <div className="w-8 h-8 rounded-xl bg-white/5 flex items-center justify-center mb-1">
                  <Ruler className="w-4 h-4 text-white/20" />
                </div>
                <p className="text-xs text-white/25">Design beam to see reinforcement</p>
              </>
            )}
          </div>
        )}
        {geometry && (
          <div className="absolute bottom-2 right-2 text-[9px] text-white/20 font-mono">
            {geometry.rebars.length}b &middot; {geometry.stirrups.length}s
          </div>
        )}
      </div>

      {/* ── Result Bar ── */}
      <div className="px-4 py-3 border-b border-white/5 space-y-2.5 shrink-0">
        <div className="flex items-center gap-2">
          <span
            className={`px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${
              statusConfig[status]?.cls ?? statusConfig.pending.cls
            }`}
          >
            {statusConfig[status]?.label ?? status.toUpperCase()}
          </span>
          {utilPct != null && (
            <span className="text-xs text-white/40 tabular-nums">
              {utilPct}% utilized
            </span>
          )}
        </div>

        {utilPct != null && (
          <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-700 ${utilBarColor}`}
              style={{ width: `${Math.min(utilPct, 100)}%` }}
            />
          </div>
        )}

        <div className="grid grid-cols-3 gap-2">
          <Metric
            label="Ast req"
            value={beam.ast_required != null ? `${Math.round(beam.ast_required)}` : "—"}
            unit={beam.ast_required != null ? "mm²" : ""}
          />
          <Metric
            label="Bars"
            value={
              beam.bar_count && beam.bar_diameter
                ? `${beam.bar_count}-T${beam.bar_diameter}`
                : "—"
            }
          />
          <Metric
            label="Stirrups"
            value={
              beam.stirrup_spacing
                ? `${beam.stirrup_diameter ?? 8}ø@${beam.stirrup_spacing}`
                : "—"
            }
          />
        </div>
      </div>

      {/* ── Cross-Section ── */}
      {beam.ast_required != null && (
        <div className="px-4 py-3 border-b border-white/5 shrink-0">
          <p className="text-[10px] text-white/30 uppercase tracking-widest mb-3">
            Cross-Section
          </p>
          <CrossSectionView
            width={beam.b}
            depth={beam.D}
            cover={beam.cover ?? 40}
            astRequired={beam.ast_required}
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
        <p className="text-[10px] text-white/30 uppercase tracking-widest">IS 456 Checks</p>
        <CheckRow
          label="Flexure"
          clause="Cl. 38.1"
          status={
            status === "fail" ? "fail" :
            beam.ast_required != null ? "pass" :
            "pending"
          }
          detail={beam.ast_required ? `Ast = ${Math.round(beam.ast_required)} mm²` : "Not designed"}
        />
        <CheckRow
          label="Shear"
          clause="Cl. 40"
          status={beam.stirrup_spacing ? (status === "fail" ? "fail" : "pass") : "pending"}
          detail={beam.stirrup_spacing ? `Sv = ${beam.stirrup_spacing} mm c/c` : "Not designed"}
        />
        <CheckRow
          label="Min Steel"
          clause="Cl. 26.5.1.1"
          status={beam.ast_required != null ? "pass" : "pending"}
          detail={`≥ 0.${(beam.fy ?? 500) === 415 ? "085" : "12"}% of Ag`}
        />
        <CheckRow
          label="L/d Ratio"
          clause="Cl. 23.2"
          status={
            beam.span && beam.D
              ? beam.span / beam.D < 20 ? "pass" : "warning"
              : "pending"
          }
          detail={
            beam.span && beam.D
              ? `L/d = ${(beam.span / beam.D).toFixed(1)} ${beam.span / beam.D < 20 ? "✓" : "⚠ > 20"}`
              : "—"
          }
        />
      </div>

      {/* ── Export ── */}
      {beam.ast_required != null && (
        <div className="px-4 py-3 shrink-0">
          <p className="text-[10px] text-white/30 uppercase tracking-widest mb-2.5">Export</p>
          <div className="flex gap-2">
            <ExportBtn
              label="BBS"
              icon={<Download className="w-3.5 h-3.5" />}
              loading={bbsPending}
              onClick={() => exportBBS(exportParams)}
            />
            <ExportBtn
              label="DXF"
              icon={<Ruler className="w-3.5 h-3.5" />}
              loading={dxfPending}
              onClick={() => exportDXF(exportParams)}
            />
            <ExportBtn
              label="Report"
              icon={<FileText className="w-3.5 h-3.5" />}
              loading={reportPending}
              onClick={() =>
                exportReport({
                  ...exportParams,
                  ast_provided: beam.ast_provided,
                  utilization: beam.utilization,
                  is_safe: beam.is_valid,
                })
              }
            />
          </div>
        </div>
      )}
    </div>
  );
}

/* ── Sub-components ── */

function Spinner() {
  return (
    <div className="flex items-center justify-center h-full">
      <div className="w-5 h-5 rounded-full border-2 border-white/10 border-t-white/40 animate-spin" />
    </div>
  );
}

function Metric({ label, value, unit = "" }: { label: string; value: string; unit?: string }) {
  return (
    <div className="p-2 rounded-lg bg-white/[0.03] border border-white/6">
      <p className="text-[9px] text-white/30 uppercase tracking-wider mb-0.5">{label}</p>
      <p className="text-xs font-medium text-white tabular-nums">
        {value}
        {unit && <span className="text-[10px] text-white/40 ml-0.5">{unit}</span>}
      </p>
    </div>
  );
}

function CheckRow({
  label, clause, status, detail,
}: {
  label: string;
  clause: string;
  status: "pass" | "fail" | "warning" | "pending";
  detail: string;
}) {
  const dot = {
    pass:    "bg-emerald-400",
    fail:    "bg-rose-400",
    warning: "bg-amber-400",
    pending: "bg-zinc-600",
  }[status];

  return (
    <div className="flex items-start gap-2.5 py-1.5">
      <div className={`w-1.5 h-1.5 rounded-full mt-1 shrink-0 ${dot}`} />
      <div className="min-w-0 flex-1">
        <div className="flex items-baseline gap-2">
          <span className="text-xs text-white/70 font-medium">{label}</span>
          <span className="text-[9px] text-white/25">{clause}</span>
        </div>
        <p className="text-[10px] text-white/40 mt-0.5 truncate">{detail}</p>
      </div>
    </div>
  );
}

function ExportBtn({
  label, icon, loading, onClick,
}: {
  label: string;
  icon: React.ReactNode;
  loading: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      disabled={loading}
      className="flex-1 flex items-center justify-center gap-1.5 px-2 py-2 rounded-lg
        bg-white/[0.04] border border-white/8 text-xs text-white/60
        hover:bg-white/[0.07] hover:text-white/90 hover:border-white/15
        transition-all disabled:opacity-40 disabled:cursor-not-allowed"
    >
      {loading ? (
        <div className="w-3.5 h-3.5 rounded-full border border-white/30 border-t-white/70 animate-spin" />
      ) : (
        icon
      )}
      {label}
    </button>
  );
}
