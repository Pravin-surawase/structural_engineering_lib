/**
 * DesignView - Compact single beam design with live 3D preview.
 *
 * Layout: Left 340px compact form | Right: 3D viewport + results
 */
import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Calculator, CheckCircle, AlertCircle, Loader2, Eye, ChevronDown, ChevronRight } from "lucide-react";
import type { BeamDesignResponse } from "../api/client";
import { useDesignStore } from "../store/designStore";
import { useLiveDesign } from "../hooks/useLiveDesign";
import { ConnectionStatus } from "./ui/ConnectionStatus";
import { Viewport3D } from "./Viewport3D";

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

  const { state, actions } = useLiveDesign({
    autoDesign,
    enabled: true,
  });

  const spanMeters = useMemo(() => Number((length / 1000).toFixed(2)), [length]);

  return (
    <div className="flex h-screen pt-14">
      {/* Left: Compact Input Form */}
      <div className="w-[340px] min-w-[300px] flex flex-col border-r border-white/5 bg-zinc-950">
        {/* Header strip */}
        <div className="px-4 py-3 border-b border-white/5 flex items-center justify-between">
          <div>
            <h2 className="text-sm font-bold text-white">Beam Design</h2>
            <p className="text-[10px] text-white/40">IS 456:2000</p>
          </div>
          <ConnectionStatus
            status={state.connectionStatus}
            latency={state.latency}
            error={state.error}
            onReconnect={actions.reconnect}
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
          </AccordionSection>
        </div>

        {/* Bottom actions */}
        <div className="px-3 pb-3 space-y-2">
          <button
            onClick={actions.triggerDesign}
            disabled={!state.isConnected || state.isDesigning}
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

      {/* Right: 3D Viewport + Results */}
      <div className="flex-1 flex flex-col bg-zinc-900/30">
        {/* 3D Viewport (top 60%) */}
        <div className="flex-[3] min-h-0 relative">
          <Viewport3D mode="design" />
          {state.isConnected && state.latency !== null && (
            <div className="absolute top-3 right-3 px-2 py-1 rounded-lg bg-black/50 text-[10px] text-white/40 backdrop-blur">
              {state.latency}ms
            </div>
          )}
        </div>

        {/* Results (bottom 40%) */}
        <div className="flex-[2] min-h-0 overflow-y-auto border-t border-white/5 p-4">
          {state.result ? (
            <CompactResults result={state.result} />
          ) : state.error ? (
            <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
              <div>
                <p className="text-red-400 font-medium text-sm">Design Failed</p>
                <p className="text-xs text-red-400/60">{state.error}</p>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <Calculator className="w-10 h-10 text-white/10 mb-3" />
              <p className="text-white/30 text-sm">Enter parameters to see results</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/** Compact results display */
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
          <p className="text-[10px] text-white/40">utilization</p>
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
            <span className="text-white/40">{item.l}</span>
            <span className="text-white font-medium">{item.v}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ---------- Input Components ---------- */

function InputField({ label, value, onChange, unit, min, max, step = 1, disabled = false }: {
  label: string; value: number; onChange: (v: number) => void; unit: string;
  min?: number; max?: number; step?: number; disabled?: boolean;
}) {
  return (
    <div>
      <label className="block text-[10px] text-white/40 mb-0.5">{label}</label>
      <div className="relative">
        <input
          type="number"
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          min={min} max={max} step={step} disabled={disabled}
          className="w-full px-2.5 py-1.5 pr-10 text-xs text-white bg-white/[0.04] border border-white/8 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500/50 disabled:opacity-40"
        />
        <span className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[10px] text-white/30">{unit}</span>
      </div>
    </div>
  );
}

function DropdownField({ label, value, onChange, options, format }: {
  label: string; value: number; onChange: (v: number) => void; options: number[]; format: (v: number) => string;
}) {
  return (
    <div>
      <label className="block text-[10px] text-white/40 mb-0.5">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full px-2.5 py-1.5 text-xs text-white bg-white/[0.04] border border-white/8 rounded-lg appearance-none cursor-pointer focus:outline-none focus:ring-1 focus:ring-blue-500/50"
      >
        {options.map((opt) => (
          <option key={opt} value={opt} className="bg-zinc-900">{format(opt)}</option>
        ))}
      </select>
    </div>
  );
}
