/**
 * ParetoPanel — Displays Pareto-optimal beam design alternatives.
 *
 * Shows results from POST /api/v1/optimization/beam/pareto as a compact table
 * highlighting cheapest, safest, and lightest alternatives.
 */
import { useState } from "react";
import { Loader2, Sparkles, DollarSign, Zap, Feather, CheckCircle, XCircle, ChevronDown, ChevronRight } from "lucide-react";
import { useParetoDesign } from "../../hooks/useParetoDesign";
import type { ParetoCandidateResponse } from "../../api/client";
import { useDesignStore } from "../../store/designStore";

interface ParetoPanelProps {
  /** Current design inputs */
  spanMm: number;
  muKnm: number;
  vuKn: number;
}

export function ParetoPanel({ spanMm, muKnm, vuKn }: ParetoPanelProps) {
  const [expanded, setExpanded] = useState(false);
  const { mutate, data, isPending, error } = useParetoDesign();
  const { setInputs } = useDesignStore();

  const handleFindAlternatives = () => {
    mutate({
      span_mm: spanMm,
      mu_knm: muKnm,
      vu_kn: vuKn,
      cover_mm: 40,
      max_candidates: 50,
    });
  };

  const handleApplyCandidate = (candidate: ParetoCandidateResponse) => {
    setInputs({
      width: candidate.b_mm,
      depth: candidate.d_mm + 40, // d_mm + cover
      fck: candidate.fck_nmm2,
      fy: candidate.fy_nmm2,
    });
  };

  if (!data && !isPending && !error) {
    return (
      <div className="rounded-xl bg-gradient-to-br from-violet-500/10 to-pink-500/10 border border-violet-500/20 p-3">
        <button
          onClick={handleFindAlternatives}
          className="w-full flex items-center justify-center gap-2 py-2.5 rounded-lg bg-violet-600/20 border border-violet-500/30 text-sm font-medium text-violet-300 hover:bg-violet-600/30 transition-colors"
        >
          <Sparkles className="w-4 h-4" />
          Find Alternatives
        </button>
        <p className="text-[10px] text-white/40 text-center mt-2">
          Discover cost-optimized designs balancing efficiency and weight
        </p>
      </div>
    );
  }

  if (isPending) {
    return (
      <div className="rounded-xl bg-violet-500/5 border border-violet-500/20 p-3 flex items-center gap-3">
        <Loader2 className="w-4 h-4 text-violet-400 animate-spin shrink-0" />
        <div>
          <p className="text-xs font-semibold text-white/80">Finding alternatives...</p>
          <p className="text-[10px] text-white/40">Evaluating Pareto-optimal designs</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl bg-red-500/10 border border-red-500/30 p-3">
        <p className="text-xs text-red-400">Optimization failed: {error.message}</p>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="rounded-xl bg-gradient-to-br from-violet-500/10 to-pink-500/10 border border-violet-500/20">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-2.5 px-3 py-2.5"
      >
        <Sparkles className="w-4 h-4 text-violet-400" />
        <span className="text-xs font-semibold text-white/80">
          {data.pareto_count} Alternative Design{data.pareto_count !== 1 ? "s" : ""}
        </span>
        <span className="ml-auto text-[10px] text-zinc-400">
          {data.computation_time_sec.toFixed(2)}s
        </span>
        {expanded ? (
          <ChevronDown className="w-3.5 h-3.5 text-zinc-400" />
        ) : (
          <ChevronRight className="w-3.5 h-3.5 text-zinc-400" />
        )}
      </button>

      {expanded && (
        <div className="px-3 pb-3 space-y-2">
          {/* Best picks header */}
          <div className="flex gap-2 text-[10px]">
            {data.best_by_cost && (
              <div className="flex items-center gap-1 text-green-400/70">
                <DollarSign className="w-3 h-3" />
                Cheapest
              </div>
            )}
            {data.best_by_utilization && (
              <div className="flex items-center gap-1 text-blue-400/70">
                <Zap className="w-3 h-3" />
                Most Efficient
              </div>
            )}
            {data.best_by_weight && (
              <div className="flex items-center gap-1 text-orange-400/70">
                <Feather className="w-3 h-3" />
                Lightest
              </div>
            )}
          </div>

          {/* Candidates table */}
          <div className="space-y-1.5">
            {data.pareto_front.slice(0, 8).map((candidate, idx) => {
              const isCheapest = data.best_by_cost?.cost === candidate.cost;
              const isEfficient = data.best_by_utilization?.utilization === candidate.utilization;
              const isLightest = data.best_by_weight?.steel_weight_kg === candidate.steel_weight_kg;

              return (
                <div
                  key={idx}
                  className="p-2 rounded-lg bg-white/[0.03] border border-white/8 hover:border-violet-500/30 transition-colors"
                >
                  <div className="flex items-start justify-between mb-1.5">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold text-white/90">
                        {candidate.b_mm}×{candidate.D_mm}mm
                      </span>
                      {candidate.is_safe ? (
                        <CheckCircle className="w-3 h-3 text-green-400" />
                      ) : (
                        <XCircle className="w-3 h-3 text-red-400" />
                      )}
                      {isCheapest && (
                        <span className="px-1.5 py-0.5 text-[9px] font-medium bg-green-500/20 text-green-300 rounded">
                          <DollarSign className="w-2.5 h-2.5 inline -mt-0.5" /> Cheapest
                        </span>
                      )}
                      {isEfficient && (
                        <span className="px-1.5 py-0.5 text-[9px] font-medium bg-blue-500/20 text-blue-300 rounded">
                          <Zap className="w-2.5 h-2.5 inline -mt-0.5" /> Efficient
                        </span>
                      )}
                      {isLightest && (
                        <span className="px-1.5 py-0.5 text-[9px] font-medium bg-orange-500/20 text-orange-300 rounded">
                          <Feather className="w-2.5 h-2.5 inline -mt-0.5" /> Lightest
                        </span>
                      )}
                    </div>
                    <button
                      onClick={() => handleApplyCandidate(candidate)}
                      className="px-2 py-0.5 text-[10px] font-medium rounded bg-violet-600/20 border border-violet-500/30 text-violet-300 hover:bg-violet-600/30 transition-colors"
                    >
                      Apply
                    </button>
                  </div>

                  <div className="grid grid-cols-4 gap-2 text-[10px]">
                    <div>
                      <span className="text-zinc-400">Rebar:</span>{" "}
                      <span className="text-white/80 font-medium">{candidate.bar_config}</span>
                    </div>
                    <div>
                      <span className="text-zinc-400">Cost:</span>{" "}
                      <span className="text-white/80 font-medium">₹{candidate.cost.toFixed(0)}</span>
                    </div>
                    <div>
                      <span className="text-zinc-400">Utilization:</span>{" "}
                      <span className={`font-medium ${candidate.utilization > 0.9 ? "text-amber-400" : "text-white/80"}`}>
                        {(candidate.utilization * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div>
                      <span className="text-zinc-400">Weight:</span>{" "}
                      <span className="text-white/80 font-medium">{candidate.steel_weight_kg.toFixed(1)} kg</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {data.pareto_front.length > 8 && (
            <p className="text-[10px] text-zinc-400 text-center pt-1">
              +{data.pareto_front.length - 8} more alternative{data.pareto_front.length - 8 !== 1 ? "s" : ""}
            </p>
          )}

          <button
            onClick={handleFindAlternatives}
            className="w-full py-1.5 text-[10px] text-violet-300/60 hover:text-violet-300/90 transition-colors"
          >
            Refresh Alternatives
          </button>
        </div>
      )}
    </div>
  );
}
