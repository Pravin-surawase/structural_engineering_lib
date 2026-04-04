/**
 * ProjectBOQPanel — Compact panel showing project-level Bill of Quantities.
 *
 * Displays grand totals for steel, concrete, and cost, plus a by-story
 * breakdown table. Includes an "Export CSV" button.
 */
import { Download, Loader2, Package } from "lucide-react";
import type { ProjectBOQResponse } from "../../hooks/useInsights";

/** Format a number with Indian locale (₹ prefix, comma separation). */
function formatINR(value: number): string {
  return "₹" + value.toLocaleString("en-IN", { maximumFractionDigits: 0 });
}

function formatNum(value: number, decimals = 0): string {
  return value.toLocaleString("en-IN", { maximumFractionDigits: decimals });
}

/** Download BOQ data as a CSV file. */
function downloadBOQCSV(data: ProjectBOQResponse) {
  const rows: string[] = [];
  rows.push("Story,Beams,Steel (kg),Concrete (m³),Cost (₹)");
  for (const s of data.by_story) {
    rows.push(
      `${s.story},${s.beam_count},${s.steel_kg.toFixed(1)},${s.concrete_m3.toFixed(2)},${s.cost_inr.toFixed(0)}`
    );
  }
  rows.push("");
  rows.push(
    `TOTAL,${data.total_beams},${data.grand_total_steel_kg.toFixed(1)},${data.grand_total_concrete_m3.toFixed(2)},${data.grand_total_cost_inr.toFixed(0)}`
  );

  const blob = new Blob([rows.join("\n")], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `Project_BOQ_${data.project_name || "export"}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

interface ProjectBOQPanelProps {
  data: ProjectBOQResponse | null;
  isLoading?: boolean;
  error?: string | null;
}

export function ProjectBOQPanel({ data, isLoading, error }: ProjectBOQPanelProps) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-10 gap-2">
        <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />
        <span className="text-sm text-zinc-400">Generating BOQ…</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="py-6 text-center">
        <p className="text-sm text-rose-400">{error}</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex flex-col items-center justify-center py-10 gap-2">
        <Package className="w-8 h-8 text-white/10" />
        <p className="text-xs text-zinc-500">No BOQ data yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Grand Totals */}
      <div className="grid grid-cols-3 gap-3">
        <div>
          <p className="text-[9px] text-zinc-500 uppercase tracking-wider">Total Steel</p>
          <p className="text-xl font-bold text-blue-400 tabular-nums">
            {formatNum(data.grand_total_steel_kg)}
            <span className="text-xs text-zinc-500 ml-1">kg</span>
          </p>
        </div>
        <div>
          <p className="text-[9px] text-zinc-500 uppercase tracking-wider">Total Concrete</p>
          <p className="text-xl font-bold text-blue-400 tabular-nums">
            {formatNum(data.grand_total_concrete_m3, 1)}
            <span className="text-xs text-zinc-500 ml-1">m³</span>
          </p>
        </div>
        <div>
          <p className="text-[9px] text-zinc-500 uppercase tracking-wider">Est. Cost</p>
          <p className="text-xl font-bold text-emerald-400 tabular-nums">
            {formatINR(data.grand_total_cost_inr)}
          </p>
        </div>
      </div>

      {/* By Story Table */}
      {data.by_story.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="text-zinc-400 border-b border-white/5">
                <th className="text-left py-1.5 font-medium">Story</th>
                <th className="text-right py-1.5 font-medium">Beams</th>
                <th className="text-right py-1.5 font-medium">Steel kg</th>
                <th className="text-right py-1.5 font-medium">Conc. m³</th>
                <th className="text-right py-1.5 font-medium">Cost ₹</th>
              </tr>
            </thead>
            <tbody>
              {data.by_story.map((s) => (
                <tr key={s.story} className="border-b border-white/[0.03] hover:bg-white/[0.02]">
                  <td className="py-1.5 text-white/70 font-medium">{s.story}</td>
                  <td className="py-1.5 text-right text-white/50 tabular-nums">{s.beam_count}</td>
                  <td className="py-1.5 text-right text-white/50 tabular-nums">{formatNum(s.steel_kg)}</td>
                  <td className="py-1.5 text-right text-white/50 tabular-nums">{formatNum(s.concrete_m3, 1)}</td>
                  <td className="py-1.5 text-right text-white/50 tabular-nums">{formatINR(s.cost_inr)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Export CSV button */}
      <div className="flex justify-end">
        <button
          onClick={() => downloadBOQCSV(data)}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg
            bg-white/5 border border-white/8 text-xs text-white/60
            hover:bg-white/10 hover:text-white/90 hover:border-white/15
            transition-all"
        >
          <Download className="w-3.5 h-3.5" />
          Export CSV
        </button>
      </div>
    </div>
  );
}
