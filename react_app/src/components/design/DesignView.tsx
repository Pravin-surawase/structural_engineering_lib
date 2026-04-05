/**
 * DesignView - Compact single beam design with live 3D preview.
 *
 * Layout: Left 340px compact form | Right: 3D viewport + results
 */
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Calculator, CheckCircle, AlertCircle, Loader2, Eye, ChevronDown, ChevronRight, Shield, Lightbulb, Download, FileText, Ruler, ChevronUp, RotateCcw, ArrowRight, Activity } from "lucide-react";
import { useExportBBS, useExportDXF, useExportReport, useLoadAnalysis } from "../../hooks";
import type { LoadAnalysisResponse } from "../../api/client";
import { useTorsionDesign } from "../../hooks/useTorsionDesign";
import type { TorsionDesignResponse } from "../../hooks/useTorsionDesign";
import type { BeamDesignResponse } from "../../api/client";
import { useDesignStore } from "../../store/designStore";
import { useLiveDesign } from "../../hooks/useLiveDesign";
import { useCodeChecks, useRebarSuggestions } from "../../hooks/useInsights";
import type { CheckDetail, SuggestionItem } from "../../hooks/useInsights";
import { ConnectionStatus } from "../ui/ConnectionStatus";
import { Viewport3D } from "../viewport/Viewport3D";
import { WorkflowHint } from "../ui/WorkflowHint";

/** Collapsible accordion section */
function AccordionSection({ title, children, defaultOpen = true }: { title: string; children: React.ReactNode; defaultOpen?: boolean }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="rounded-xl bg-white/[0.03] border border-white/8">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-3.5 py-2.5 text-xs font-semibold text-white/70 hover:text-white/90 transition-colors"
      >
        {title}
        {open ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
      </button>
      {open && <div className="px-3.5 pb-3.5 grid grid-cols-2 gap-2.5">{children}</div>}
    </div>
  );
}

export function DesignView() {
  const navigate = useNavigate();
  const { inputs, length } = useDesignStore();
  const [autoDesign, setAutoDesign] = useState(true);
  const [resultsCollapsed, setResultsCollapsed] = useState(false);
  const [showExportMenu, setShowExportMenu] = useState(false);
  const [torsionEnabled, setTorsionEnabled] = useState(false);
  const [torsionMoment, setTorsionMoment] = useState(10); // kN·m
  const [loadCalcEnabled, setLoadCalcEnabled] = useState(false);
  const [loadCalcType, setLoadCalcType] = useState<'udl' | 'point'>('udl');
  const [loadCalcMagnitude, setLoadCalcMagnitude] = useState(20); // kN/m or kN
  const [loadCalcSupport, setLoadCalcSupport] = useState<'simply_supported' | 'cantilever'>('simply_supported');

  const exportParams = {
    width: inputs.width,
    depth: inputs.depth,
    span_length: length,
    clear_cover: 40,
    fck: inputs.fck,
    fy: inputs.fy,
    ast_required: 0, // filled below when result exists
    moment: inputs.moment,
    shear: inputs.shear ?? 0,
  };
  const { mutate: exportBBS, isPending: bbsPending } = useExportBBS();
  const { mutate: exportDXF, isPending: dxfPending } = useExportDXF();
  const { mutate: exportReport, isPending: reportPending } = useExportReport();

  const { state, actions } = useLiveDesign({
    autoDesign,
    enabled: true,
  });

  const codeChecks = useCodeChecks();
  const rebarSuggestions = useRebarSuggestions();
  const torsionDesign = useTorsionDesign();
  const loadAnalysis = useLoadAnalysis();

  const spanMeters = useMemo(() => Number((length / 1000).toFixed(2)), [length]);

  // Auto-trigger code checks + rebar suggestions when design result changes
  useEffect(() => {
    if (!state.result) return;
    const r = state.result;
    codeChecks.mutate({
      beam: {
        b_mm: inputs.width,
        D_mm: inputs.depth,
        span_mm: length,
        fck_mpa: inputs.fck,
        fy_mpa: inputs.fy,
        mu_knm: inputs.moment,
        vu_kn: inputs.shear,
      },
      config: r.ast_total ? { ast_mm2: r.ast_total } : null,
    });
    if (r.flexure?.ast_required) {
      rebarSuggestions.mutate({
        ast_required: r.flexure.ast_required,
        ast_provided: r.ast_total,
        b_mm: inputs.width,
        cover_mm: 40,
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.result]);

  // Auto-trigger torsion design when enabled and flexure result exists
  useEffect(() => {
    if (!torsionEnabled || !state.result) return;
    torsionDesign.mutate({
      width: inputs.width,
      depth: inputs.depth,
      torsion: torsionMoment,
      moment: inputs.moment,
      shear: inputs.shear ?? 0,
      fck: inputs.fck,
      fy: inputs.fy,
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [torsionEnabled, torsionMoment, state.result]);

  return (
    <div className="flex h-screen pt-14">
      {/* Left: Compact Input Form */}
      <div className="w-[340px] min-w-[300px] flex flex-col border-r border-white/5 bg-zinc-950">
        {/* Header strip */}
        <div className="px-4 py-3 border-b border-white/5 flex items-center justify-between">
          <div>
            <h2 className="text-sm font-bold text-white">Beam Design</h2>
            <p className="text-[10px] text-zinc-400">IS 456:2000</p>
          </div>
          <ConnectionStatus
            status={state.connectionStatus}
            latency={state.latency}
            error={state.error}
            onReconnect={actions.reconnect}
            isFallbackActive={state.isFallbackActive}
          />
        </div>

        {/* Form body */}
        <div className="flex-1 overflow-y-auto px-3 py-3 space-y-2.5">
          {/* Auto design toggle */}
          <div className="flex items-center justify-between px-3 py-2 rounded-lg bg-white/[0.03] border border-white/8">
            <label className="flex items-center gap-2 text-xs text-white/60">
              <input
                type="checkbox"
                checked={autoDesign}
                onChange={(e) => setAutoDesign(e.target.checked)}
                className="accent-blue-500 w-3.5 h-3.5"
              />
              Auto Design
            </label>
            {state.isDesigning && <Loader2 className="w-3.5 h-3.5 text-blue-400 animate-spin" />}
          </div>

          <AccordionSection title="Dimensions">
            <InputField label="Width" value={inputs.width} onChange={(v) => actions.updateInputs({ width: v })} unit="mm" min={150} max={600} />
            <InputField label="Depth" value={inputs.depth} onChange={(v) => actions.updateInputs({ depth: v })} unit="mm" min={300} max={1200} />
            <InputField label="Span" value={spanMeters} onChange={(v) => actions.updateLength(v * 1000)} unit="m" min={1} max={15} step={0.5} />
            <InputField label="Cover" value={40} onChange={() => {}} unit="mm" disabled />
          </AccordionSection>

          <AccordionSection title="Materials">
            <DropdownField label="Concrete" value={inputs.fck} onChange={(v) => actions.updateInputs({ fck: v })} options={[20, 25, 30, 35, 40, 45, 50]} format={(v) => `M${v}`} />
            <DropdownField label="Steel" value={inputs.fy} onChange={(v) => actions.updateInputs({ fy: v })} options={[415, 500, 550]} format={(v) => `Fe${v}`} />
          </AccordionSection>

          <AccordionSection title="Design Forces">
            <InputField label="Moment (Mu)" value={inputs.moment} onChange={(v) => actions.updateInputs({ moment: v })} unit="kN·m" min={0} max={2000} />
            <InputField label="Shear (Vu)" value={inputs.shear ?? 0} onChange={(v) => actions.updateInputs({ shear: v })} unit="kN" min={0} max={1000} />

            {/* Load Calculator toggle */}
            <div className="col-span-2 flex items-center gap-2 px-1 pt-1">
              <label className="flex items-center gap-2 text-xs text-white/60 cursor-pointer">
                <input
                  type="checkbox"
                  checked={loadCalcEnabled}
                  onChange={(e) => setLoadCalcEnabled(e.target.checked)}
                  className="accent-cyan-500 w-3.5 h-3.5"
                />
                <Activity className="w-3 h-3 text-cyan-400" />
                Load Calculator
              </label>
            </div>
            {loadCalcEnabled && (
              <>
                <DropdownField label="Support" value={loadCalcSupport} onChange={setLoadCalcSupport as (v: string | number) => void} options={['simply_supported', 'cantilever']} format={(v) => v === 'simply_supported' ? 'SS' : 'Cantilever'} />
                <DropdownField label="Load Type" value={loadCalcType} onChange={setLoadCalcType as (v: string | number) => void} options={['udl', 'point']} format={(v) => v === 'udl' ? 'UDL' : 'Point'} />
                <InputField label={loadCalcType === 'udl' ? 'w' : 'P'} value={loadCalcMagnitude} onChange={setLoadCalcMagnitude} unit={loadCalcType === 'udl' ? 'kN/m' : 'kN'} min={0.1} max={500} step={0.5} />
                <div className="col-span-2 flex gap-2">
                  <button
                    onClick={() => {
                      const load = loadCalcType === 'udl'
                        ? { load_type: 'udl' as const, magnitude: loadCalcMagnitude }
                        : { load_type: 'point' as const, magnitude: loadCalcMagnitude, position_mm: length / 2 };
                      loadAnalysis.mutate({
                        span_mm: length,
                        support_condition: loadCalcSupport,
                        loads: [load],
                        num_points: 51,
                      });
                    }}
                    disabled={loadAnalysis.isPending}
                    className="flex-1 py-1.5 rounded-lg bg-cyan-600/20 border border-cyan-500/30 text-[11px] text-cyan-300 hover:bg-cyan-600/30 transition-colors flex items-center justify-center gap-1.5 disabled:opacity-40"
                  >
                    {loadAnalysis.isPending ? <Loader2 className="w-3 h-3 animate-spin" /> : <Activity className="w-3 h-3" />}
                    Compute
                  </button>
                  {loadAnalysis.data && (
                    <button
                      onClick={() => {
                        const d = loadAnalysis.data!;
                        const muAbs = Math.max(Math.abs(d.max_bm_knm), Math.abs(d.min_bm_knm));
                        const vuAbs = Math.max(Math.abs(d.max_sf_kn), Math.abs(d.min_sf_kn));
                        actions.updateInputs({ moment: Math.round(muAbs * 10) / 10, shear: Math.round(vuAbs * 10) / 10 });
                      }}
                      className="flex-1 py-1.5 rounded-lg bg-emerald-600/20 border border-emerald-500/30 text-[11px] text-emerald-300 hover:bg-emerald-600/30 transition-colors flex items-center justify-center gap-1.5"
                    >
                      Use Values <ArrowRight className="w-3 h-3" />
                    </button>
                  )}
                </div>
                {loadAnalysis.data && <MiniDiagram data={loadAnalysis.data} />}
              </>
            )}
            <div className="col-span-2 flex items-center gap-2 px-1 pt-1">
              <label className="flex items-center gap-2 text-xs text-white/60 cursor-pointer">
                <input
                  type="checkbox"
                  checked={torsionEnabled}
                  onChange={(e) => setTorsionEnabled(e.target.checked)}
                  className="accent-purple-500 w-3.5 h-3.5"
                />
                <RotateCcw className="w-3 h-3 text-purple-400" />
                Include Torsion
              </label>
            </div>
            {torsionEnabled && (
              <InputField label="Torsion (Tu)" value={torsionMoment} onChange={setTorsionMoment} unit="kN·m" min={0.1} max={200} step={0.5} />
            )}
          </AccordionSection>
        </div>

        {/* Bottom actions */}
        <div className="px-3 pb-3 space-y-2">
          <button
            onClick={actions.triggerDesign}
            disabled={state.isDesigning}
            className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold rounded-xl transition-colors flex items-center justify-center gap-2 disabled:opacity-40"
          >
            {state.isDesigning ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Calculating...
              </>
            ) : (
              <>
                <Calculator className="w-4 h-4" />
                Design Beam
              </>
            )}
          </button>
          {state.isFallbackActive && (
            <p className="text-[10px] text-amber-400/60 text-center">Using REST API (WebSocket unavailable)</p>
          )}
          {state.result && (
            <button
              onClick={() => navigate("/design/results")}
              className="w-full py-2.5 bg-white/5 hover:bg-white/10 text-white/70 text-sm font-medium rounded-xl transition-colors flex items-center justify-center gap-2 border border-white/10"
            >
              <Eye className="w-4 h-4" />
              Full 3D Detail View
            </button>
          )}
        </div>
      </div>

      {/* Right: 3D Viewport + Results — dynamic layout */}
      <div className="flex-1 flex flex-col bg-zinc-900/30 relative">
        {/* Workflow hint */}
        <div className="px-4 pt-3 pb-2">
          <WorkflowHint
            stepNumber={state.result ? 3 : 1}
            totalSteps={4}
            title={state.result ? "Review Results" : "Enter Beam Dimensions"}
            description={
              state.result
                ? "Check the design results above. Adjust inputs if needed, or export BBS/DXF."
                : "Fill in dimensions, materials, and forces in the left panel, then click 'Design Beam'."
            }
            nextAction={state.result ? "Export → BBS/DXF/Report" : "Design Beam"}
            storageKey="workflow_hint_design_view"
          />
        </div>

        {/* Export dropdown (top-right corner, shown when result exists) */}
        {state.result && (
          <div className="absolute top-3 right-3 z-10">
            <button
              onClick={() => setShowExportMenu(!showExportMenu)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-900/80 backdrop-blur border border-white/10 text-xs text-white/60 hover:text-white/90 hover:border-white/20 transition-all"
            >
              <Download className="w-3.5 h-3.5" />
              Export
              <ChevronDown className="w-3 h-3" />
            </button>
            {showExportMenu && (
              <div className="absolute right-0 mt-1.5 w-44 rounded-xl bg-zinc-900 border border-white/10 shadow-2xl shadow-black/50 overflow-hidden">
                {[
                  { label: "BBS (CSV)", icon: <Download className="w-3.5 h-3.5" />, loading: bbsPending, onClick: () => { exportBBS({ ...exportParams, ast_required: state.result?.flexure?.ast_required ?? 0 }); setShowExportMenu(false); } },
                  { label: "DXF Drawing", icon: <Ruler className="w-3.5 h-3.5" />, loading: dxfPending, onClick: () => { exportDXF({ ...exportParams, ast_required: state.result?.flexure?.ast_required ?? 0 }); setShowExportMenu(false); } },
                  { label: "HTML Report", icon: <FileText className="w-3.5 h-3.5" />, loading: reportPending, onClick: () => { exportReport({ ...exportParams, ast_required: state.result?.flexure?.ast_required, ast_provided: state.result?.ast_total, utilization: state.result?.utilization_ratio, is_safe: state.result?.success }); setShowExportMenu(false); } },
                  { label: "PDF Report", icon: <FileText className="w-3.5 h-3.5" />, loading: reportPending, onClick: () => { exportReport({ ...exportParams, ast_required: state.result?.flexure?.ast_required, ast_provided: state.result?.ast_total, utilization: state.result?.utilization_ratio, is_safe: state.result?.success, format: "pdf" }); setShowExportMenu(false); } },
                ].map((item) => (
                  <button key={item.label} onClick={item.onClick} disabled={item.loading}
                    className="w-full flex items-center gap-2.5 px-3.5 py-2.5 text-xs text-white/60 hover:bg-white/5 hover:text-white/90 transition-colors disabled:opacity-40">
                    {item.loading ? <div className="w-3.5 h-3.5 rounded-full border border-white/30 border-t-white/70 animate-spin" /> : item.icon}
                    {item.label}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {/* 3D Viewport — expands to fill when no result */}
        <div
          className={`min-h-0 relative transition-all duration-300 ease-in-out ${
            !state.result ? "flex-[5]" : resultsCollapsed ? "flex-[5]" : "flex-[3]"
          }`}
        >
          <Viewport3D mode="design" forceMode />
          {state.isConnected && state.latency !== null && (
            <div className="absolute top-3 left-3 px-2 py-1 rounded-lg bg-black/50 text-[10px] text-zinc-400 backdrop-blur">
              {state.latency}ms
            </div>
          )}

          {/* Empty state preset button — only when no result and not designing */}
          {!state.result && !state.isDesigning && (
            <div className="absolute bottom-6 left-1/2 -translate-x-1/2">
              <button
                onClick={() => {
                  actions.updateInputs({ width: 300, depth: 500, fck: 25, fy: 500, moment: 120, shear: 75 });
                  actions.updateLength(5000);
                }}
                className="px-4 py-2 rounded-xl bg-blue-600/20 border border-blue-500/30 text-xs text-blue-300 hover:bg-blue-600/30 hover:border-blue-500/50 backdrop-blur transition-all"
              >
                Try: 300×500 · M25 · Mu=120 kN·m →
              </button>
            </div>
          )}
        </div>

        {/* Results — collapses to single bar or expands fully */}
        {state.result ? (
          resultsCollapsed ? (
            /* Collapsed: single-line summary bar */
            <div
              className="h-10 shrink-0 border-t border-white/5 flex items-center justify-between px-4 cursor-pointer hover:bg-white/[0.02] transition-colors"
              onClick={() => setResultsCollapsed(false)}
            >
              <CompactResultsBar result={state.result} />
              <ChevronUp className="w-3.5 h-3.5 text-zinc-500" />
            </div>
          ) : (
            /* Expanded results panel */
            <div className="flex-[2] min-h-0 border-t border-white/5 flex flex-col">
              <button
                onClick={() => setResultsCollapsed(true)}
                className="h-7 shrink-0 flex items-center justify-end px-3 hover:bg-white/[0.02] transition-colors"
              >
                <ChevronDown className="w-3.5 h-3.5 text-white/20" aria-hidden="true" />
              </button>
              <div className="flex-1 overflow-y-auto px-4 pb-4 space-y-3">
                <CompactResults result={state.result} />
                {torsionDesign.data && <TorsionResultsPanel data={torsionDesign.data} isPending={torsionDesign.isPending} />}
                <CodeChecksPanel data={codeChecks.data} isPending={codeChecks.isPending} />
                <RebarSuggestionsPanel data={rebarSuggestions.data} isPending={rebarSuggestions.isPending} />
              </div>
            </div>
          )
        ) : state.error ? (
          <div className="shrink-0 mx-4 mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/30 flex items-center gap-3">
            <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
            <div>
              <p className="text-red-400 font-medium text-xs">Design Failed</p>
              <p className="text-[10px] text-red-400/60">{state.error}</p>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}

/** Compact results display */
/** Single-line summary bar shown when results panel is collapsed */
function CompactResultsBar({ result }: { result: BeamDesignResponse }) {
  const pct = Math.round((result.utilization_ratio ?? 0) * 100);
  const isOk = result.success;
  const barColor = pct > 100 ? "bg-rose-500" : pct > 90 ? "bg-amber-400" : "bg-emerald-400";
  return (
    <div className="flex items-center gap-3 flex-1 min-w-0">
      <span className={`text-xs font-semibold ${isOk ? "text-emerald-400" : "text-rose-400"}`}>
        {isOk ? "✓ SAFE" : "✕ FAIL"}
      </span>
      <div className="flex items-center gap-1.5 flex-1 min-w-0">
        <div className="w-20 h-1.5 bg-zinc-800 rounded-full overflow-hidden shrink-0">
          <div className={`h-full rounded-full ${barColor}`} style={{ width: `${Math.min(pct, 100)}%` }} />
        </div>
        <span className="text-xs text-zinc-400 tabular-nums">{pct}%</span>
      </div>
      {result.flexure?.ast_required && (
        <span className="text-xs text-zinc-400 tabular-nums shrink-0">
          Ast {Math.round(result.flexure.ast_required)} mm²
        </span>
      )}
      {result.shear?.stirrup_spacing && (
        <span className="text-xs text-zinc-500 tabular-nums shrink-0">
          Sv {result.shear.stirrup_spacing}
        </span>
      )}
    </div>
  );
}

function CompactResults({ result }: { result: BeamDesignResponse }) {
  const isSuccess = result.success;
  return (
    <div className="space-y-3">
      {/* Status */}
      <div className={`p-3 rounded-xl border flex items-center gap-2.5 ${isSuccess ? "bg-green-500/10 border-green-500/30" : "bg-red-500/10 border-red-500/30"}`}>
        {isSuccess ? <CheckCircle className="w-5 h-5 text-green-400" /> : <AlertCircle className="w-5 h-5 text-red-400" />}
        <div>
          <p className={`font-semibold text-sm ${isSuccess ? "text-green-400" : "text-red-400"}`}>
            {isSuccess ? "Design Safe" : "Requires Revision"}
          </p>
          <p className="text-[11px] text-white/50">{result.message || "IS 456:2000"}</p>
        </div>
        <div className="ml-auto text-right">
          <p className="text-lg font-bold text-white">{(result.utilization_ratio * 100).toFixed(0)}%</p>
          <p className="text-[10px] text-zinc-400">utilization</p>
        </div>
      </div>

      {/* Cards row */}
      <div className="grid grid-cols-3 gap-2.5">
        <ResultMiniCard title="Flexure" items={[
          { l: "Ast", v: `${result.flexure?.ast_required?.toFixed(0) || "-"} mm²` },
          { l: "xu", v: `${result.flexure?.xu?.toFixed(1) || "-"} mm` },
          { l: "Mu,cap", v: `${result.flexure?.moment_capacity?.toFixed(0) || "-"} kN·m` },
        ]} />
        <ResultMiniCard title="Shear" items={[
          { l: "τv", v: result.shear?.tau_v ? `${result.shear.tau_v.toFixed(2)} MPa` : "-" },
          { l: "Sv", v: result.shear?.stirrup_spacing ? `${result.shear.stirrup_spacing} mm` : "-" },
          { l: "Vu,cap", v: result.shear?.shear_capacity ? `${result.shear.shear_capacity.toFixed(0)} kN` : "-" },
        ]} />
        <ResultMiniCard title="Summary" items={[
          { l: "Ast total", v: `${result.ast_total?.toFixed(0) || "-"} mm²` },
          { l: "Asc", v: `${result.asc_total?.toFixed(0) || "0"} mm²` },
          { l: "Status", v: result.success ? "SAFE" : "FAIL" },
        ]} />
      </div>

      {/* Warnings */}
      {result.warnings && result.warnings.length > 0 && (
        <div className="p-2.5 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
          {result.warnings.map((w, i) => (
            <p key={i} className="text-xs text-yellow-400/80">• {w}</p>
          ))}
        </div>
      )}
    </div>
  );
}

function ResultMiniCard({ title, items }: { title: string; items: { l: string; v: string }[] }) {
  return (
    <div className="p-3 rounded-xl bg-white/[0.03] border border-white/8">
      <h4 className="text-[10px] font-semibold text-white/50 uppercase tracking-wider mb-2">{title}</h4>
      <div className="space-y-1.5">
        {items.map((item) => (
          <div key={item.l} className="flex justify-between text-xs">
            <span className="text-zinc-400">{item.l}</span>
            <span className="text-white font-medium">{item.v}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ---------- Code Checks Panel ---------- */

function CodeChecksPanel({ data, isPending }: { data: ReturnType<typeof useCodeChecks>["data"]; isPending: boolean }) {
  const [expanded, setExpanded] = useState(false);
  if (isPending) {
    return (
      <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-white/[0.02] border border-white/5">
        <Loader2 className="w-3.5 h-3.5 text-blue-400 animate-spin" />
        <span className="text-xs text-zinc-400">Running code checks...</span>
      </div>
    );
  }
  if (!data) return null;

  const passCount = data.checks.filter((c: CheckDetail) => c.passed).length;
  const totalCount = data.checks.length;
  const allPassed = data.passed;

  return (
    <div className={`rounded-xl border ${allPassed ? "bg-green-500/5 border-green-500/20" : "bg-red-500/5 border-red-500/20"}`}>
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-2.5 px-3 py-2.5"
      >
        <Shield className={`w-4 h-4 ${allPassed ? "text-green-400" : "text-red-400"}`} />
        <span className="text-xs font-semibold text-white/80">
          Code Checks: {passCount}/{totalCount} passed
        </span>
        {data.governing_check && (
          <span className="ml-auto text-[10px] text-zinc-400 mr-2">Gov: {data.governing_check}</span>
        )}
        {expanded ? <ChevronDown className="w-3.5 h-3.5 text-zinc-400" /> : <ChevronRight className="w-3.5 h-3.5 text-zinc-400" />}
      </button>
      {expanded && (
        <div className="px-3 pb-3 space-y-1.5">
          {data.checks.map((check: CheckDetail) => (
            <div key={check.name} className="flex items-center gap-2 text-xs">
              {check.passed ? (
                <CheckCircle className="w-3.5 h-3.5 text-green-400 shrink-0" />
              ) : (
                <AlertCircle className="w-3.5 h-3.5 text-red-400 shrink-0" />
              )}
              <span className="text-white/70 flex-1">{check.name}</span>
              <span className="text-[10px] text-zinc-500">{check.clause}</span>
              {check.utilization != null && (
                <span className={`text-[10px] font-medium ${check.utilization <= 1 ? "text-green-400/70" : "text-red-400/70"}`}>
                  {(check.utilization * 100).toFixed(0)}%
                </span>
              )}
            </div>
          ))}
          {data.critical_failures.length > 0 && (
            <div className="mt-2 p-2 rounded-lg bg-red-500/10 border border-red-500/20">
              <p className="text-[10px] font-semibold text-red-400 mb-1">Critical Failures:</p>
              {data.critical_failures.map((f: string, i: number) => (
                <p key={i} className="text-[10px] text-red-400/70">• {f}</p>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

/* ---------- Rebar Suggestions Panel ---------- */

function RebarSuggestionsPanel({ data, isPending }: { data: ReturnType<typeof useRebarSuggestions>["data"]; isPending: boolean }) {
  const [expanded, setExpanded] = useState(false);
  if (isPending) {
    return (
      <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-white/[0.02] border border-white/5">
        <Loader2 className="w-3.5 h-3.5 text-purple-400 animate-spin" />
        <span className="text-xs text-zinc-400">Finding rebar options...</span>
      </div>
    );
  }
  if (!data || data.suggestions.length === 0) return null;

  return (
    <div className="rounded-xl bg-purple-500/5 border border-purple-500/20">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-2.5 px-3 py-2.5"
      >
        <Lightbulb className="w-4 h-4 text-purple-400" />
        <span className="text-xs font-semibold text-white/80">
          {data.suggestion_count} Rebar Option{data.suggestion_count !== 1 ? "s" : ""}
        </span>
        {data.max_savings_percent > 0 && (
          <span className="ml-1 px-1.5 py-0.5 text-[10px] font-medium bg-purple-500/20 text-purple-300 rounded">
            up to {data.max_savings_percent.toFixed(0)}% saving
          </span>
        )}
        {expanded ? <ChevronDown className="w-3.5 h-3.5 text-zinc-400 ml-auto" /> : <ChevronRight className="w-3.5 h-3.5 text-zinc-400 ml-auto" />}
      </button>
      {expanded && (
        <div className="px-3 pb-3 space-y-2">
          {data.suggestions.map((s: SuggestionItem) => (
            <div key={s.id} className="p-2.5 rounded-lg bg-white/[0.03] border border-white/8">
              <div className="flex items-center gap-2 mb-1.5">
                <span className="text-xs font-semibold text-white/90">{s.title}</span>
                <span className={`px-1.5 py-0.5 text-[10px] font-medium rounded ${
                  s.impact === "HIGH" ? "bg-green-500/20 text-green-300" :
                  s.impact === "MEDIUM" ? "bg-yellow-500/20 text-yellow-300" :
                  "bg-white/10 text-white/50"
                }`}>
                  {s.impact}
                </span>
                {s.savings_percent > 0 && (
                  <span className="text-[10px] text-green-400/70 ml-auto">-{s.savings_percent.toFixed(0)}% steel</span>
                )}
              </div>
              <p className="text-[10px] text-white/50 mb-1">{s.description}</p>
              <div className="flex gap-3 text-[10px] text-zinc-400">
                <span>{s.suggested_config.bar_count}Ø{s.suggested_config.bar_dia_mm}mm</span>
                <span>Ast: {s.suggested_config.ast_provided_mm2.toFixed(0)} mm²</span>
                {s.suggested_config.excess_mm2 > 0 && (
                  <span>+{s.suggested_config.excess_mm2.toFixed(0)} mm² excess</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ---------- Input Components ---------- */

function InputField({ label, value, onChange, unit, min, max, step = 1, disabled = false }: {
  label: string; value: number; onChange: (v: number) => void; unit: string;
  min?: number; max?: number; step?: number; disabled?: boolean;
}) {
  const fieldId = `design-${label.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`;
  return (
    <div>
      <label htmlFor={fieldId} className="block text-[10px] text-zinc-400 mb-0.5">
        {label}
      </label>
      <div className="relative">
        <input
          id={fieldId}
          type="number"
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          min={min}
          max={max}
          step={step}
          disabled={disabled}
          aria-label={`${label} in ${unit}`}
          className="w-full px-2.5 py-1.5 pr-10 text-xs text-white bg-white/[0.04] border border-white/8 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500/50 disabled:opacity-40"
        />
        <span className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[10px] text-zinc-500" aria-hidden="true">
          {unit}
        </span>
      </div>
    </div>
  );
}

function DropdownField<T extends string | number>({ label, value, onChange, options, format }: {
  label: string; value: T; onChange: (v: T) => void; options: T[]; format: (v: T) => string;
}) {
  const fieldId = `design-dropdown-${label.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`;
  return (
    <div>
      <label htmlFor={fieldId} className="block text-[10px] text-zinc-400 mb-0.5">
        {label}
      </label>
      <select
        id={fieldId}
        value={String(value)}
        onChange={(e) => {
          const raw = e.target.value;
          // If options are numbers, parse as number; otherwise keep as string
          const parsed = typeof options[0] === 'number' ? Number(raw) : raw;
          onChange(parsed as T);
        }}
        aria-label={label}
        className="w-full px-2.5 py-1.5 text-xs text-white bg-white/[0.04] border border-white/8 rounded-lg appearance-none cursor-pointer focus:outline-none focus:ring-1 focus:ring-blue-500/50"
      >
        {options.map((opt) => (
          <option key={String(opt)} value={String(opt)} className="bg-zinc-900">{format(opt)}</option>
        ))}
      </select>
    </div>
  );
}

/* ---------- Torsion Results Panel ---------- */

function TorsionResultsPanel({ data, isPending }: { data: TorsionDesignResponse | undefined; isPending: boolean }) {
  const [expanded, setExpanded] = useState(true);
  if (isPending) {
    return (
      <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-white/[0.02] border border-white/5">
        <Loader2 className="w-3.5 h-3.5 text-purple-400 animate-spin" />
        <span className="text-xs text-zinc-400">Calculating torsion...</span>
      </div>
    );
  }
  if (!data) return null;

  return (
    <div className={`rounded-xl border ${data.is_safe ? "bg-purple-500/5 border-purple-500/20" : "bg-red-500/5 border-red-500/20"}`}>
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-2.5 px-3 py-2.5"
      >
        <RotateCcw className={`w-4 h-4 ${data.is_safe ? "text-purple-400" : "text-red-400"}`} />
        <span className="text-xs font-semibold text-white/80">
          Torsion (IS 456 Cl 41) — {data.is_safe ? "Safe" : "UNSAFE"}
        </span>
        <span className="ml-auto text-[10px] text-zinc-400 mr-2">
          Sv {data.stirrup_spacing}mm · Al {data.al_torsion} mm²
        </span>
        {expanded ? <ChevronDown className="w-3.5 h-3.5 text-zinc-400" /> : <ChevronRight className="w-3.5 h-3.5 text-zinc-400" />}
      </button>
      {expanded && (
        <div className="px-3 pb-3 space-y-2.5">
          {/* Equivalent forces */}
          <div className="grid grid-cols-2 gap-2">
            <div className="p-2.5 rounded-lg bg-white/[0.03] border border-white/8">
              <h5 className="text-[10px] font-semibold text-white/50 uppercase tracking-wider mb-1.5">Equivalent Forces</h5>
              <div className="space-y-1">
                <div className="flex justify-between text-xs"><span className="text-zinc-400">Ve</span><span className="text-white font-medium">{data.ve_kn.toFixed(1)} kN</span></div>
                <div className="flex justify-between text-xs"><span className="text-zinc-400">Me</span><span className="text-white font-medium">{data.me_knm.toFixed(1)} kN·m</span></div>
              </div>
            </div>
            <div className="p-2.5 rounded-lg bg-white/[0.03] border border-white/8">
              <h5 className="text-[10px] font-semibold text-white/50 uppercase tracking-wider mb-1.5">Shear Stress</h5>
              <div className="space-y-1">
                <div className="flex justify-between text-xs"><span className="text-zinc-400">τve</span><span className={`font-medium ${data.tv_equiv <= data.tc_max ? "text-white" : "text-red-400"}`}>{data.tv_equiv.toFixed(3)} MPa</span></div>
                <div className="flex justify-between text-xs"><span className="text-zinc-400">τc</span><span className="text-white font-medium">{data.tc.toFixed(3)} MPa</span></div>
                <div className="flex justify-between text-xs"><span className="text-zinc-400">τc,max</span><span className="text-white font-medium">{data.tc_max.toFixed(2)} MPa</span></div>
              </div>
            </div>
          </div>

          {/* Reinforcement */}
          <div className="p-2.5 rounded-lg bg-white/[0.03] border border-white/8">
            <h5 className="text-[10px] font-semibold text-white/50 uppercase tracking-wider mb-1.5">Reinforcement (Closed Stirrups)</h5>
            <div className="grid grid-cols-2 gap-x-4 gap-y-1">
              <div className="flex justify-between text-xs"><span className="text-zinc-400">Asv (torsion)</span><span className="text-white font-medium">{data.asv_torsion.toFixed(4)} mm²/mm</span></div>
              <div className="flex justify-between text-xs"><span className="text-zinc-400">Asv (shear)</span><span className="text-white font-medium">{data.asv_shear.toFixed(4)} mm²/mm</span></div>
              <div className="flex justify-between text-xs"><span className="text-zinc-400">Asv (total)</span><span className="text-purple-300 font-semibold">{data.asv_total.toFixed(4)} mm²/mm</span></div>
              <div className="flex justify-between text-xs"><span className="text-zinc-400">Spacing Sv</span><span className="text-purple-300 font-semibold">{data.stirrup_spacing} mm</span></div>
            </div>
            <div className="mt-2 pt-2 border-t border-white/5">
              <div className="flex justify-between text-xs"><span className="text-zinc-400">Longitudinal Al</span><span className="text-purple-300 font-semibold">{data.al_torsion} mm²</span></div>
            </div>
          </div>

          {/* Warnings */}
          {data.warnings && data.warnings.length > 0 && (
            <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/30">
              {data.warnings.map((w, i) => (
                <p key={i} className="text-[10px] text-amber-400/80">• {w}</p>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

/* ---------- Mini BMD/SFD Diagram ---------- */

function MiniDiagram({ data }: { data: LoadAnalysisResponse }) {
  const w = 260;
  const h = 60;
  const pad = 4;

  const drawPath = (values: number[]) => {
    const maxAbs = Math.max(...values.map(Math.abs), 0.01);
    const n = values.length;
    return values
      .map((v, i) => {
        const x = pad + ((w - 2 * pad) * i) / (n - 1);
        const y = h / 2 - (v / maxAbs) * (h / 2 - pad);
        return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
      })
      .join(" ");
  };

  return (
    <div className="col-span-2 rounded-lg bg-white/[0.03] border border-white/8 p-2 space-y-1">
      <div className="flex justify-between text-[10px] text-zinc-400 px-1">
        <span>Mu,max = <span className="text-cyan-300 font-semibold">{Math.abs(data.max_bm_knm).toFixed(1)}</span> kN·m</span>
        <span>Vu,max = <span className="text-cyan-300 font-semibold">{Math.abs(data.max_sf_kn).toFixed(1)}</span> kN</span>
      </div>
      <svg width={w} height={h} className="w-full" viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none">
        {/* Zero line */}
        <line x1={pad} y1={h / 2} x2={w - pad} y2={h / 2} stroke="rgba(255,255,255,0.1)" strokeWidth="1" />
        {/* BMD */}
        <path d={drawPath(data.bmd_knm)} fill="none" stroke="#22d3ee" strokeWidth="1.5" opacity="0.8" />
        {/* SFD */}
        <path d={drawPath(data.sfd_kn)} fill="none" stroke="#a78bfa" strokeWidth="1" opacity="0.5" strokeDasharray="3,2" />
      </svg>
      <div className="flex gap-3 justify-center">
        <span className="text-[9px] text-cyan-400/60 flex items-center gap-1"><span className="w-3 h-0.5 bg-cyan-400 inline-block rounded" /> BMD</span>
        <span className="text-[9px] text-violet-400/60 flex items-center gap-1"><span className="w-3 h-0.5 bg-violet-400 inline-block rounded border-dashed" /> SFD</span>
      </div>
    </div>
  );
}
