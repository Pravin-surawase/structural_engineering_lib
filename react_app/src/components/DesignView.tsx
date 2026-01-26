/**
 * DesignView - Single beam design form with live results.
 */
import { useMemo, useState } from "react";
import { ArrowLeft, Calculator, CheckCircle, AlertCircle, Loader2 } from "lucide-react";
import type { BeamDesignResponse } from "../api/client";
import { useDesignStore } from "../store/designStore";
import { useLiveDesign } from "../hooks/useLiveDesign";
import { ConnectionStatus } from "./ui/ConnectionStatus";
import { Viewport3D } from "./Viewport3D";

interface DesignViewProps {
  onBack: () => void;
}

export function DesignView({ onBack }: DesignViewProps) {
  const { inputs, length } = useDesignStore();
  const [autoDesign, setAutoDesign] = useState(true);

  const { state, actions } = useLiveDesign({
    autoDesign,
    enabled: true,
  });

  const spanMeters = useMemo(() => Number((length / 1000).toFixed(2)), [length]);

  return (
    <div className="flex flex-col h-full p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-4">
          <button
            onClick={onBack}
            className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-white/60" />
          </button>
          <div>
            <h2 className="text-2xl font-bold text-white">Single Beam Design</h2>
            <p className="text-white/50">
              IS 456:2000 flexure and shear design
            </p>
          </div>
        </div>
        <ConnectionStatus
          status={state.connectionStatus}
          latency={state.latency}
          error={state.error}
          onReconnect={actions.reconnect}
        />
      </div>

      <div className="grid grid-cols-12 gap-6 flex-1">
        {/* Left: Inputs */}
        <div className="col-span-5 space-y-6">
          <div className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-white/10">
            <label className="flex items-center gap-2 text-sm text-white/70">
              <input
                type="checkbox"
                checked={autoDesign}
                onChange={(e) => setAutoDesign(e.target.checked)}
                className="accent-blue-500"
              />
              Auto Design
            </label>
            {!autoDesign && (
              <button
                onClick={actions.triggerDesign}
                disabled={!state.isConnected || state.isDesigning}
                className="px-3 py-1.5 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-500 rounded-lg transition-colors disabled:opacity-50"
              >
                {state.isDesigning ? "Designing..." : "Design Beam"}
              </button>
            )}
          </div>

          <InputSection title="Beam Dimensions">
            <InputField
              label="Width"
              value={inputs.width}
              onChange={(value) => actions.updateInputs({ width: value })}
              unit="mm"
              min={150}
              max={600}
            />
            <InputField
              label="Depth"
              value={inputs.depth}
              onChange={(value) => actions.updateInputs({ depth: value })}
              unit="mm"
              min={300}
              max={1200}
            />
            <InputField
              label="Span"
              value={spanMeters}
              onChange={(value) => actions.updateLength(value * 1000)}
              unit="m"
              min={1}
              max={15}
              step={0.5}
            />
            <InputField
              label="Clear Cover"
              value={40}
              onChange={() => {}}
              unit="mm"
              min={25}
              max={75}
              disabled
            />
          </InputSection>

          <InputSection title="Material Properties">
            <DropdownField
              label="Concrete Grade"
              value={inputs.fck}
              onChange={(value) => actions.updateInputs({ fck: value })}
              options={[20, 25, 30, 35, 40, 45, 50]}
              format={(v) => `M${v} (${v} MPa)`}
            />
            <DropdownField
              label="Steel Grade"
              value={inputs.fy}
              onChange={(value) => actions.updateInputs({ fy: value })}
              options={[415, 500, 550]}
              format={(v) => `Fe ${v} (${v} MPa)`}
            />
          </InputSection>

          <InputSection title="Design Forces">
            <InputField
              label="Moment (Mu)"
              value={inputs.moment}
              onChange={(value) => actions.updateInputs({ moment: value })}
              unit="kN·m"
              min={0}
              max={2000}
            />
            <InputField
              label="Shear (Vu)"
              value={inputs.shear ?? 0}
              onChange={(value) => actions.updateInputs({ shear: value })}
              unit="kN"
              min={0}
              max={1000}
            />
          </InputSection>

          <button
            onClick={actions.triggerDesign}
            disabled={!state.isConnected || state.isDesigning}
            className="w-full py-3 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-xl transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {state.isDesigning ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Calculating...
              </>
            ) : (
              <>
                <Calculator className="w-5 h-5" />
                Design Beam
              </>
            )}
          </button>
        </div>

        {/* Right: Preview + Results */}
        <div className="col-span-7 flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-white">Live 3D Preview</h3>
              <p className="text-xs text-white/50">WebSocket-driven updates</p>
            </div>
            {state.isConnected && state.latency !== null && (
              <span className="text-xs text-white/40">{state.latency}ms</span>
            )}
          </div>

          <div className="h-[300px] rounded-2xl overflow-hidden border border-white/10 bg-zinc-900">
            <Viewport3D mode="design" />
          </div>

          {state.result ? (
            <ResultsPanel result={state.result} />
          ) : state.error ? (
            <div className="p-6 rounded-xl bg-red-500/10 border border-red-500/30">
              <div className="flex items-center gap-3">
                <AlertCircle className="w-6 h-6 text-red-400" />
                <div>
                  <p className="text-red-400 font-medium">Design Failed</p>
                  <p className="text-sm text-red-400/70">
                    {state.error}
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-8 rounded-xl bg-white/5 border border-white/10 flex flex-col items-center justify-center text-center">
              <Calculator className="w-12 h-12 text-white/20 mb-4" />
              <p className="text-white/40">
                Enter beam parameters and click "Design Beam"
              </p>
              <p className="text-sm text-white/30 mt-2">
                Results will appear here
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

interface InputSectionProps {
  title: string;
  children: React.ReactNode;
}

function InputSection({ title, children }: InputSectionProps) {
  return (
    <div className="p-4 rounded-xl bg-white/5 border border-white/10">
      <h3 className="text-sm font-semibold text-white/80 mb-4">{title}</h3>
      <div className="grid grid-cols-2 gap-3">{children}</div>
    </div>
  );
}

interface InputFieldProps {
  label: string;
  value: number;
  onChange: (v: number) => void;
  unit: string;
  min?: number;
  max?: number;
  step?: number;
  disabled?: boolean;
}

function InputField({
  label,
  value,
  onChange,
  unit,
  min,
  max,
  step = 1,
  disabled = false,
}: InputFieldProps) {
  return (
    <div>
      <label className="block text-xs text-white/50 mb-1">{label}</label>
      <div className="relative">
        <input
          type="number"
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          min={min}
          max={max}
          step={step}
          disabled={disabled}
          className="w-full px-3 py-2 pr-12 text-sm text-white bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500/50"
        />
        <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-white/40">
          {unit}
        </span>
      </div>
    </div>
  );
}

interface DropdownFieldProps {
  label: string;
  value: number;
  onChange: (v: number) => void;
  options: number[];
  format: (v: number) => string;
}

function DropdownField({ label, value, onChange, options, format }: DropdownFieldProps) {
  return (
    <div className="col-span-2">
      <label className="block text-xs text-white/50 mb-1">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full px-3 py-2 text-sm text-white bg-white/5 border border-white/10 rounded-lg appearance-none cursor-pointer focus:outline-none focus:ring-1 focus:ring-blue-500/50"
      >
        {options.map((opt) => (
          <option key={opt} value={opt} className="bg-zinc-900">
            {format(opt)}
          </option>
        ))}
      </select>
    </div>
  );
}

interface ResultsPanelProps {
  result: BeamDesignResponse;
}

function ResultsPanel({ result }: ResultsPanelProps) {
  const isSuccess = result.success;

  return (
    <div className="h-full flex flex-col gap-4">
      {/* Status Banner */}
      <div
        className={`p-4 rounded-xl border flex items-center gap-3 ${
          isSuccess
            ? "bg-green-500/10 border-green-500/30"
            : "bg-red-500/10 border-red-500/30"
        }`}
      >
        {isSuccess ? (
          <CheckCircle className="w-6 h-6 text-green-400" />
        ) : (
          <AlertCircle className="w-6 h-6 text-red-400" />
        )}
        <div>
          <p className={`font-semibold ${isSuccess ? "text-green-400" : "text-red-400"}`}>
            Design {isSuccess ? "Safe" : "Requires Revision"}
          </p>
          <p className="text-sm text-white/60">
            {result.message || "IS 456:2000 compliant"}
          </p>
        </div>
      </div>

      {/* Results Grid */}
      <div className="grid grid-cols-2 gap-4 flex-1">
        <ResultCard
          title="Flexure Design"
          items={[
            { label: "Ast Required", value: `${result.flexure?.ast_required?.toFixed(0) || "-"} mm²` },
            { label: "Ast Min", value: `${result.flexure?.ast_min?.toFixed(0) || "-"} mm²` },
            { label: "Ast Max", value: `${result.flexure?.ast_max?.toFixed(0) || "-"} mm²` },
            { label: "Moment Capacity", value: `${result.flexure?.moment_capacity?.toFixed(0) || "-"} kN·m` },
          ]}
        />
        <ResultCard
          title="Shear Design"
          items={[
            { label: "τv", value: result.shear?.tau_v ? `${result.shear.tau_v.toFixed(2)} MPa` : "-" },
            { label: "τc", value: result.shear?.tau_c ? `${result.shear.tau_c.toFixed(2)} MPa` : "-" },
            { label: "Stirrup Spacing", value: result.shear?.stirrup_spacing ? `${result.shear.stirrup_spacing} mm` : "-" },
            { label: "Shear Capacity", value: result.shear?.shear_capacity ? `${result.shear.shear_capacity.toFixed(0)} kN` : "-" },
          ]}
        />
        <ResultCard
          title="Neutral Axis"
          items={[
            { label: "xu", value: `${result.flexure?.xu?.toFixed(1) || "-"} mm` },
            { label: "xu,max", value: `${result.flexure?.xu_max?.toFixed(1) || "-"} mm` },
            { label: "Under Reinforced", value: result.flexure?.is_under_reinforced ? "Yes ✓" : "No" },
            { label: "Utilization", value: `${(result.utilization_ratio * 100).toFixed(0)}%` },
          ]}
        />
        <ResultCard
          title="Summary"
          items={[
            { label: "Total Ast", value: `${result.ast_total?.toFixed(0) || "-"} mm²` },
            { label: "Asc (if any)", value: `${result.asc_total?.toFixed(0) || "0"} mm²` },
            { label: "Code", value: "IS 456:2000" },
            { label: "Status", value: result.success ? "SAFE" : "FAIL" },
          ]}
        />
      </div>

      {/* Warnings */}
      {result.warnings && result.warnings.length > 0 && (
        <div className="p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
          <p className="text-sm text-yellow-400 font-medium">Warnings:</p>
          <ul className="mt-1 text-sm text-yellow-400/70">
            {result.warnings.map((w, i) => (
              <li key={i}>• {w}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

interface ResultCardProps {
  title: string;
  items: { label: string; value: string }[];
}

function ResultCard({ title, items }: ResultCardProps) {
  return (
    <div className="p-4 rounded-xl bg-white/5 border border-white/10">
      <h4 className="text-sm font-semibold text-white/80 mb-3">{title}</h4>
      <div className="space-y-2">
        {items.map((item) => (
          <div key={item.label} className="flex justify-between text-sm">
            <span className="text-white/50">{item.label}</span>
            <span className="text-white font-medium">{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
