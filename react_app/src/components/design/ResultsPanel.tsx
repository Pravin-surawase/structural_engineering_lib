/**
 * ResultsPanel Component
 *
 * Displays beam design results from the API.
 */
import { useDesignStore } from '../../store/designStore';

export function ResultsPanel() {
  const { result, error, isLoading } = useDesignStore();

  if (isLoading) {
    return (
      <div className="p-4 h-full overflow-y-auto bg-[#1e1e1e] text-[#e0e0e0]">
        <h2 className="m-0 mb-3 text-lg text-white border-b border-[#333] pb-2">Results</h2>
        <div className="text-[#0078d4] text-center p-5">Calculating...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 h-full overflow-y-auto bg-[#1e1e1e] text-[#e0e0e0]">
        <h2 className="m-0 mb-3 text-lg text-white border-b border-[#333] pb-2">Results</h2>
        <div className="text-red-500 p-3 bg-red-500/10 rounded border-l-[3px] border-red-500">{error}</div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="p-4 h-full overflow-y-auto bg-[#1e1e1e] text-[#e0e0e0]">
        <h2 className="m-0 mb-3 text-lg text-white border-b border-[#333] pb-2">Results</h2>
        <div className="text-[#666] italic p-5 text-center">
          Click "Design Beam" to calculate reinforcement.
        </div>
      </div>
    );
  }

  const { flexure, shear, ast_total, asc_total, utilization_ratio, warnings } = result;

  return (
    <div className="p-4 h-full overflow-y-auto bg-[#1e1e1e] text-[#e0e0e0]">
      <h2 className="m-0 mb-3 text-lg text-white border-b border-[#333] pb-2">Design Results</h2>

      {/* Status */}
      <div className={`p-2 px-3 rounded font-semibold mb-4 text-center ${
        result.success
          ? 'bg-green-500/20 text-green-500 border border-green-500'
          : 'bg-red-500/20 text-red-500 border border-red-500'
      }`}>
        {result.success ? '✓ Design OK' : '✗ Design Failed'}
      </div>

      {/* Flexure Results */}
      <div className="mb-4">
        <h3 className="m-0 mb-2 text-[13px] text-[#888] uppercase tracking-wide">Flexure</h3>
        <div className="grid grid-cols-2 gap-2">
          <div className="flex flex-col gap-0.5 p-2 bg-[#2d2d2d] rounded">
            <span className="text-[11px] text-[#888]">Ast Required</span>
            <span className="text-sm font-semibold text-white">{flexure.ast_required.toFixed(0)} mm²</span>
          </div>
          <div className="flex flex-col gap-0.5 p-2 bg-[#2d2d2d] rounded">
            <span className="text-[11px] text-[#888]">Ast Min</span>
            <span className="text-sm font-semibold text-white">{flexure.ast_min.toFixed(0)} mm²</span>
          </div>
          <div className="flex flex-col gap-0.5 p-2 bg-[#2d2d2d] rounded">
            <span className="text-[11px] text-[#888]">Ast Max</span>
            <span className="text-sm font-semibold text-white">{flexure.ast_max.toFixed(0)} mm²</span>
          </div>
          <div className="flex flex-col gap-0.5 p-2 bg-[#2d2d2d] rounded">
            <span className="text-[11px] text-[#888]">xu/xu,max</span>
            <span className="text-sm font-semibold text-white">
              {((flexure.xu / flexure.xu_max) * 100).toFixed(1)}%
            </span>
          </div>
          <div className="flex flex-col gap-0.5 p-2 bg-[#2d2d2d] rounded">
            <span className="text-[11px] text-[#888]">Under-reinforced</span>
            <span className={`text-sm font-semibold ${flexure.is_under_reinforced ? 'text-green-500' : 'text-red-500'}`}>
              {flexure.is_under_reinforced ? 'Yes ✓' : 'No ✗'}
            </span>
          </div>
          <div className="flex flex-col gap-0.5 p-2 bg-[#2d2d2d] rounded">
            <span className="text-[11px] text-[#888]">Moment Capacity</span>
            <span className="text-sm font-semibold text-white">{flexure.moment_capacity.toFixed(1)} kN·m</span>
          </div>
        </div>
      </div>

      {/* Shear Results */}
      {shear && (
        <div className="mb-4">
          <h3 className="m-0 mb-2 text-[13px] text-[#888] uppercase tracking-wide">Shear</h3>
          <div className="grid grid-cols-2 gap-2">
            <div className="flex flex-col gap-0.5 p-2 bg-[#2d2d2d] rounded">
              <span className="text-[11px] text-[#888]">τv</span>
              <span className="text-sm font-semibold text-white">{shear.tau_v.toFixed(2)} N/mm²</span>
            </div>
            <div className="flex flex-col gap-0.5 p-2 bg-[#2d2d2d] rounded">
              <span className="text-[11px] text-[#888]">τc</span>
              <span className="text-sm font-semibold text-white">{shear.tau_c.toFixed(2)} N/mm²</span>
            </div>
            <div className="flex flex-col gap-0.5 p-2 bg-[#2d2d2d] rounded">
              <span className="text-[11px] text-[#888]">Stirrup Asv</span>
              <span className="text-sm font-semibold text-white">{shear.asv_required.toFixed(0)} mm²</span>
            </div>
            <div className="flex flex-col gap-0.5 p-2 bg-[#2d2d2d] rounded">
              <span className="text-[11px] text-[#888]">Spacing</span>
              <span className="text-sm font-semibold text-white">{shear.stirrup_spacing.toFixed(0)} mm</span>
            </div>
          </div>
        </div>
      )}

      {/* Summary */}
      <div className="mb-4 pt-2 border-t border-[#333]">
        <h3 className="m-0 mb-2 text-[13px] text-[#888] uppercase tracking-wide">Summary</h3>
        <div className="grid grid-cols-2 gap-2">
          <div className="flex flex-col gap-0.5 p-2 bg-[#0078d4]/20 rounded border border-[#0078d4]/50">
            <span className="text-[11px] text-[#888]">Total Tension Steel</span>
            <span className="text-sm font-semibold text-white">{ast_total.toFixed(0)} mm²</span>
          </div>
          <div className="flex flex-col gap-0.5 p-2 bg-[#2d2d2d] rounded">
            <span className="text-[11px] text-[#888]">Compression Steel</span>
            <span className="text-sm font-semibold text-white">{asc_total.toFixed(0)} mm²</span>
          </div>
          <div className="flex flex-col gap-0.5 p-2 bg-[#2d2d2d] rounded">
            <span className="text-[11px] text-[#888]">Utilization</span>
            <span
              className={`text-sm font-semibold ${
                utilization_ratio < 0.9 ? 'text-green-500' : utilization_ratio < 1.0 ? 'text-amber-500' : 'text-red-500'
              }`}
            >
              {(utilization_ratio * 100).toFixed(1)}%
            </span>
          </div>
        </div>
      </div>

      {/* Warnings */}
      {warnings && warnings.length > 0 && (
        <div className="bg-amber-500/10 p-3 rounded border-l-[3px] border-amber-500">
          <h3 className="m-0 mb-2 text-[13px] text-amber-500 uppercase tracking-wide">Warnings</h3>
          <ul className="m-0 pl-4">
            {warnings.map((w, i) => (
              <li key={i} className="text-[13px] text-[#ccc] mb-1">{w}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
