/**
 * ResultsPanel Component
 *
 * Displays beam design results from the API.
 */
import { useDesignStore } from '../../store/designStore';
import { formatPercent, formatRatio, formatSignedRatio, getTrustPresentation } from '../../utils/trustPresentation';

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
        <div className="text-zinc-400 italic p-5 text-center">
          Click "Design Beam" to calculate reinforcement.
        </div>
      </div>
    );
  }

  const { flexure, shear, ast_total, asc_total, warnings } = result;
  const trust = getTrustPresentation(result);
  const isPass = trust.status === 'PASS';

  return (
    <div className="p-4 h-full overflow-y-auto bg-[#1e1e1e] text-[#e0e0e0]">
      <h2 className="m-0 mb-3 text-lg text-white border-b border-[#333] pb-2">Design Results</h2>

      {/* Status */}
      <div className={`p-2 px-3 rounded font-semibold mb-4 text-center ${
        isPass
          ? 'bg-green-500/20 text-green-500 border border-green-500'
          : trust.status === 'HOLD'
            ? 'bg-amber-500/20 text-amber-400 border border-amber-500'
            : 'bg-red-500/20 text-red-500 border border-red-500'
      }`}>
        {isPass ? '✓ Design PASS' : trust.status === 'HOLD' ? '◼ Design HOLD' : '✗ Design FAIL'}
      </div>

      {/* Flexure Results */}
      <div className="mb-4">
        <h3 className="m-0 mb-2 text-[13px] text-zinc-400 uppercase tracking-wide">Flexure</h3>
        <div className="grid grid-cols-2 gap-2">
          <div className="flex flex-col gap-0.5 p-2 bg-[#2d2d2d] rounded">
            <span className="text-[11px] text-zinc-400">Ast Required</span>
            <span className="text-sm font-semibold text-white">{flexure.ast_required.toFixed(0)} mm²</span>
          </div>
          <div className="flex flex-col gap-0.5 p-2 bg-[#2d2d2d] rounded">
            <span className="text-[11px] text-zinc-400">Ast Min</span>
            <span className="text-sm font-semibold text-white">{flexure.ast_min.toFixed(0)} mm²</span>
          </div>
          <div className="flex flex-col gap-0.5 p-2 bg-[#2d2d2d] rounded">
            <span className="text-[11px] text-zinc-400">Ast Max</span>
            <span className="text-sm font-semibold text-white">{flexure.ast_max.toFixed(0)} mm²</span>
          </div>
          <div className="flex flex-col gap-0.5 p-2 bg-[#2d2d2d] rounded">
            <span className="text-[11px] text-zinc-400">xu/xu,max</span>
            <span className="text-sm font-semibold text-white">
              {((flexure.xu / flexure.xu_max) * 100).toFixed(1)}%
            </span>
          </div>
          <div className="flex flex-col gap-0.5 p-2 bg-[#2d2d2d] rounded">
            <span className="text-[11px] text-zinc-400">Under-reinforced</span>
            <span className={`text-sm font-semibold ${flexure.is_under_reinforced ? 'text-green-500' : 'text-red-500'}`}>
              {flexure.is_under_reinforced ? 'Yes ✓' : 'No ✗'}
            </span>
          </div>
          <div className="flex flex-col gap-0.5 p-2 bg-[#2d2d2d] rounded">
            <span className="text-[11px] text-zinc-400">Moment Capacity</span>
            <span className="text-sm font-semibold text-white">{flexure.moment_capacity.toFixed(1)} kN·m</span>
          </div>
        </div>
      </div>

      {/* Shear Results */}
      {shear && (
        <div className="mb-4">
          <h3 className="m-0 mb-2 text-[13px] text-zinc-400 uppercase tracking-wide">Shear</h3>
          <div className="grid grid-cols-2 gap-2">
            <div className="flex flex-col gap-0.5 p-2 bg-[#2d2d2d] rounded">
              <span className="text-[11px] text-zinc-400">τv</span>
              <span className="text-sm font-semibold text-white">{shear.tau_v.toFixed(2)} N/mm²</span>
            </div>
            <div className="flex flex-col gap-0.5 p-2 bg-[#2d2d2d] rounded">
              <span className="text-[11px] text-zinc-400">τc</span>
              <span className="text-sm font-semibold text-white">{shear.tau_c.toFixed(2)} N/mm²</span>
            </div>
            <div className="flex flex-col gap-0.5 p-2 bg-[#2d2d2d] rounded">
              <span className="text-[11px] text-zinc-400">Stirrup Asv/s</span>
              <span className="text-sm font-semibold text-white">{shear.asv_required.toFixed(4)} {shear.asv_required_unit}</span>
            </div>
            <div className="flex flex-col gap-0.5 p-2 bg-[#2d2d2d] rounded">
              <span className="text-[11px] text-zinc-400">Spacing</span>
              <span className="text-sm font-semibold text-white">{shear.stirrup_spacing.toFixed(0)} mm</span>
            </div>
          </div>
        </div>
      )}

      {result.combined_actions && result.torsion && (
        <div className="mb-4">
          <h3 className="m-0 mb-2 text-[13px] text-zinc-400 uppercase tracking-wide">Combined actions and torsion</h3>
          <div className="grid grid-cols-2 gap-2">
            <div className="p-2 bg-[#2d2d2d] rounded text-sm">
              <p className="text-[11px] text-zinc-400">Original Mu / Vu / Tu</p>
              <p>{result.combined_actions.mu_knm.toFixed(1)} kN·m / {result.combined_actions.vu_kn.toFixed(1)} kN / {result.combined_actions.tu_knm.toFixed(1)} kN·m</p>
            </div>
            <div className="p-2 bg-[#2d2d2d] rounded text-sm">
              <p className="text-[11px] text-zinc-400">Equivalent Me / Ve</p>
              <p>{result.combined_actions.me_knm.toFixed(1)} kN·m / {result.combined_actions.ve_kn.toFixed(1)} kN</p>
            </div>
            <div className="p-2 bg-[#2d2d2d] rounded text-sm">
              <p className="text-[11px] text-zinc-400">Combined Asv/s · Al</p>
              <p>{result.torsion.asv_total.toFixed(4)} mm²/mm · {result.torsion.al_torsion.toFixed(1)} mm²</p>
            </div>
            <div className="p-2 bg-[#2d2d2d] rounded text-sm">
              <p className="text-[11px] text-zinc-400">Closed stirrups</p>
              <p>{result.torsion.requires_closed_stirrups ? 'Required' : 'Not required'}</p>
            </div>
            <p className="col-span-2 text-[11px] text-zinc-400">{result.torsion.source} · {Object.values(result.torsion.clause_refs).join(' · ')}</p>
          </div>
        </div>
      )}

      {(result.deflection_check || result.crack_width_check) && (
        <div className="mb-4">
          <h3 className="m-0 mb-2 text-[13px] text-zinc-400 uppercase tracking-wide">Serviceability</h3>
          <div className="grid grid-cols-2 gap-2">
            {result.deflection_check && (
              <div className="p-2 bg-[#2d2d2d] rounded text-sm">
                <p className="text-[11px] text-zinc-400">Deflection</p>
                <p>{result.deflection_check.is_ok ? 'PASS' : 'FAIL'} · L/d {result.deflection_check.span_depth_actual?.toFixed(2) ?? '—'} / {result.deflection_check.span_depth_allowable?.toFixed(2) ?? '—'}</p>
              </div>
            )}
            {result.crack_width_check && (
              <div className="p-2 bg-[#2d2d2d] rounded text-sm">
                <p className="text-[11px] text-zinc-400">Crack width</p>
                <p>{result.crack_width_check.is_ok ? 'PASS' : 'FAIL'} · {result.crack_width_check.crack_width_mm?.toFixed(3) ?? '—'} / {result.crack_width_check.crack_width_limit_mm?.toFixed(3) ?? '—'} mm</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Summary */}
      <div className="mb-4 pt-2 border-t border-[#333]">
        <h3 className="m-0 mb-2 text-[13px] text-zinc-400 uppercase tracking-wide">Summary</h3>
        <div className="grid grid-cols-2 gap-2">
          <div className="flex flex-col gap-0.5 p-2 bg-[#0078d4]/20 rounded border border-[#0078d4]/50">
            <span className="text-[11px] text-zinc-400">Total Tension Steel</span>
            <span className="text-sm font-semibold text-white">{ast_total.toFixed(0)} mm²</span>
          </div>
          <div className="flex flex-col gap-0.5 p-2 bg-[#2d2d2d] rounded">
            <span className="text-[11px] text-zinc-400">Compression Steel</span>
            <span className="text-sm font-semibold text-white">{asc_total.toFixed(0)} mm²</span>
          </div>
          <div className="flex flex-col gap-0.5 p-2 bg-[#2d2d2d] rounded">
            <span className="text-[11px] text-zinc-400">Utilization</span>
            <span
              className={`text-sm font-semibold ${
                trust.exactUtilization < 0.9 ? 'text-green-500' : trust.exactUtilization <= 1.0 ? 'text-amber-500' : 'text-red-500'
              }`}
            >
              {formatPercent(trust.exactUtilization)}
            </span>
          </div>
          <div className="flex flex-col gap-0.5 p-2 bg-[#2d2d2d] rounded">
            <span className="text-[11px] text-zinc-400">Exact Ratio / Margin</span>
            <span className="text-xs font-semibold text-white font-mono">
              {formatRatio(trust.exactUtilization)} / {formatSignedRatio(trust.margin)}
            </span>
          </div>
          <div className="col-span-2 flex flex-col gap-0.5 p-2 bg-[#2d2d2d] rounded">
            <span className="text-[11px] text-zinc-400">Governing Check / Calculation</span>
            <span className="text-xs font-semibold text-white font-mono break-all">
              {trust.governingCheck} · {trust.calculationIdentity?.slice(0, 16) ?? 'evidence unavailable'}
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
      {result.holds && result.holds.length > 0 && (
        <div className="mt-3 bg-amber-500/10 p-3 rounded border-l-[3px] border-amber-500">
          <h3 className="m-0 mb-2 text-[13px] text-amber-500 uppercase tracking-wide">Holds</h3>
          {result.holds.map((hold) => <p key={hold} className="text-[13px] text-[#ccc]">{hold}</p>)}
        </div>
      )}
    </div>
  );
}
