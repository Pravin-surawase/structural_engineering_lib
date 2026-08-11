import type { SlabWorkflowMode, SlabWorkflowRequest } from './types';

function edgeClass(condition: unknown) {
  return condition === 'continuous' ? 'stroke-emerald-300' : 'stroke-amber-300';
}

function edgeDash(condition: unknown) {
  return condition === 'continuous' ? undefined : '8 6';
}

export function SlabPanelMap({
  mode,
  request,
}: {
  mode: SlabWorkflowMode;
  request: SlabWorkflowRequest;
}) {
  const twoWay = mode === 'two-way';
  return (
    <svg viewBox="0 0 360 240" className="h-full min-h-56 w-full" role="img" aria-label="Slab support and reinforcement map">
      <rect x="45" y="30" width="270" height="180" rx="3" className="fill-zinc-900 stroke-zinc-700" strokeWidth="2" />
      {twoWay ? (
        <>
          <line x1="45" y1="30" x2="45" y2="210" className={edgeClass(request.x_min_edge)} strokeDasharray={edgeDash(request.x_min_edge)} strokeWidth="7" />
          <line x1="315" y1="30" x2="315" y2="210" className={edgeClass(request.x_max_edge)} strokeDasharray={edgeDash(request.x_max_edge)} strokeWidth="7" />
          <line x1="45" y1="30" x2="315" y2="30" className={edgeClass(request.y_max_edge)} strokeDasharray={edgeDash(request.y_max_edge)} strokeWidth="7" />
          <line x1="45" y1="210" x2="315" y2="210" className={edgeClass(request.y_min_edge)} strokeDasharray={edgeDash(request.y_min_edge)} strokeWidth="7" />
          {[78, 110, 142, 174].map((y) => <line key={`x-${y}`} x1="62" y1={y} x2="298" y2={y} className="stroke-blue-400/70" strokeWidth="2" />)}
          {[100, 140, 180, 220, 260].map((x) => <line key={`y-${x}`} x1={x} y1="48" x2={x} y2="192" className="stroke-violet-400/70" strokeWidth="2" />)}
          <rect x="45" y="30" width="54" height="54" className="fill-amber-400/10 stroke-amber-300/50" />
          <text x="58" y="62" className="fill-amber-200 text-[11px]">corner</text>
        </>
      ) : (
        <>
          {[75, 105, 135, 165].map((y) => <line key={y} x1="62" y1={y} x2="298" y2={y} className="stroke-blue-400/80" strokeWidth="3" />)}
          <line x1="45" y1="30" x2="45" y2="210" className="stroke-emerald-300" strokeWidth="7" />
          <line x1="315" y1="30" x2="315" y2="210" className="stroke-emerald-300" strokeWidth="7" />
          {mode === 'continuous' ? <line x1="180" y1="30" x2="180" y2="210" className="stroke-emerald-300" strokeWidth="5" /> : null}
        </>
      )}
      <text x="180" y="228" textAnchor="middle" className="fill-zinc-400 text-[11px]">
        {twoWay ? 'physical edges • middle and edge strips' : 'main bars follow short-span action'}
      </text>
    </svg>
  );
}
