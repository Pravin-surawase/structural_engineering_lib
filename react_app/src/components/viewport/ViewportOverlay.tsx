import { useState } from 'react';
import type { ViewportFrameFilter } from './BuildingScene';
import {
  VIEWPORT_STATUS_STYLE,
  type ViewportMemberInspection,
  type ViewportMemberStatus,
} from './inspectionModel';

const STATUS_ORDER: readonly ViewportMemberStatus[] = [
  'fail',
  'hold',
  'error',
  'stale',
  'pending',
  'pass',
  'not_evaluated',
];

interface ViewportOverlayProps {
  floors: readonly string[];
  frameTypes: readonly Exclude<ViewportFrameFilter, 'all'>[];
  selectedFloor: string | null;
  frameFilter: ViewportFrameFilter;
  isolateSelection: boolean;
  showStatus: boolean;
  showUtilization: boolean;
  hasCurrentUtilization: boolean;
  selected: ViewportMemberInspection | null;
  statusCounts: Record<ViewportMemberStatus, number>;
  geometryFailure: string | null;
  onFloorChange: (floor: string | null) => void;
  onFrameFilterChange: (frameType: ViewportFrameFilter) => void;
  onIsolateSelectionChange: (isolate: boolean) => void;
  onShowStatusChange: (show: boolean) => void;
  onShowUtilizationChange: (show: boolean) => void;
  onFit: () => void;
}

const selectClassName = 'min-h-8 rounded-md border border-white/10 bg-zinc-950/90 px-2 text-[11px] text-zinc-100 focus:border-sky-400 focus:outline-none';

export function ViewportOverlay({
  floors,
  frameTypes,
  selectedFloor,
  frameFilter,
  isolateSelection,
  showStatus,
  showUtilization,
  hasCurrentUtilization,
  selected,
  statusCounts,
  geometryFailure,
  onFloorChange,
  onFrameFilterChange,
  onIsolateSelectionChange,
  onShowStatusChange,
  onShowUtilizationChange,
  onFit,
}: ViewportOverlayProps) {
  const [mobileControlsOpen, setMobileControlsOpen] = useState(false);

  return (
    <div className="pointer-events-none absolute inset-0 z-10 flex flex-col justify-between p-2 text-zinc-100">
      <div className="shrink-0">
        <button
          type="button"
          className="pointer-events-auto min-h-8 rounded-md border border-white/10 bg-zinc-950/88 px-3 text-[11px] text-zinc-100 shadow-lg backdrop-blur-sm sm:hidden"
          aria-expanded={mobileControlsOpen}
          onClick={() => setMobileControlsOpen((open) => !open)}
        >
          {mobileControlsOpen ? 'Hide 3D controls' : 'Show 3D controls'}
        </button>
        <div className={`${mobileControlsOpen ? 'grid' : 'hidden'} pointer-events-auto mt-1.5 max-h-[55%] shrink-0 grid-cols-2 items-start gap-1.5 overflow-auto rounded-lg border border-white/10 bg-zinc-950/88 p-2 shadow-xl backdrop-blur-sm sm:mt-0 sm:flex sm:max-h-[48%] sm:w-fit sm:max-w-[calc(100%-1rem)] sm:flex-wrap`}>
          <label className="flex items-center gap-1 text-[10px] text-zinc-400">
            Floor
            <select
              aria-label="Viewport floor"
              className={selectClassName}
              value={selectedFloor ?? 'all'}
              onChange={(event) => onFloorChange(event.target.value === 'all' ? null : event.target.value)}
            >
              <option value="all">All</option>
              {floors.map((floor) => <option key={floor} value={floor}>{floor}</option>)}
            </select>
          </label>
          <label className="flex items-center gap-1 text-[10px] text-zinc-400">
            Frame
            <select
              aria-label="Viewport frame type"
              className={selectClassName}
              value={frameFilter}
              onChange={(event) => onFrameFilterChange(event.target.value as ViewportFrameFilter)}
            >
              <option value="all">All</option>
              {frameTypes.map((frameType) => (
                <option key={frameType} value={frameType}>{frameType}</option>
              ))}
            </select>
          </label>
          <Toggle
            label="Isolate"
            checked={isolateSelection}
            disabled={!selected}
            onChange={onIsolateSelectionChange}
          />
          <Toggle label="Status" checked={showStatus} onChange={onShowStatusChange} />
          <Toggle
            label="Utilization"
            checked={showUtilization}
            disabled={!hasCurrentUtilization}
            onChange={onShowUtilizationChange}
          />
          <button
            type="button"
            className="min-h-8 rounded-md border border-sky-400/30 bg-sky-400/10 px-2 text-[11px] text-sky-100 hover:bg-sky-400/20 focus:outline-none focus:ring-2 focus:ring-sky-400"
            onClick={onFit}
          >
            {selected ? 'Fit selected' : 'Fit building'}
          </button>
        </div>
      </div>

      <div className={`${mobileControlsOpen ? 'hidden sm:flex' : 'flex'} shrink-0 items-end justify-between gap-2`}>
        <div
          className="pointer-events-auto max-w-[70%] rounded-lg border border-white/10 bg-zinc-950/88 px-2.5 py-2 text-[11px] shadow-lg backdrop-blur-sm sm:max-w-md"
          aria-live="polite"
        >
          {geometryFailure ? (
            <div data-testid="geometry-space-v1-invalid">
              <p className="font-semibold text-amber-200">3D geometry unavailable</p>
              <p className="mt-0.5 text-zinc-300">{geometryFailure}</p>
            </div>
          ) : selected ? (
            <div data-testid="viewport-selected-member">
              <p className="font-semibold text-white">{selected.label}</p>
              <p className="text-zinc-400">{selected.memberId} · {selected.story} · {selected.frameType}</p>
              <p style={{ color: VIEWPORT_STATUS_STYLE[selected.status].color }}>
                {VIEWPORT_STATUS_STYLE[selected.status].label}
                {showUtilization && selected.utilization !== null
                  ? ` · utilization ${selected.utilization.toFixed(3)}`
                  : ''}
              </p>
            </div>
          ) : (
            <p className="text-zinc-400">Select a member to inspect its source identity and current evidence.</p>
          )}
        </div>

        {showStatus ? (
          <section
            aria-label="Current member status legend"
            className="pointer-events-auto max-h-20 overflow-auto rounded-lg border border-white/10 bg-zinc-950/88 p-2 text-[10px] shadow-lg backdrop-blur-sm sm:max-h-24"
          >
            <p className="mb-1 font-medium text-zinc-300">Current evidence</p>
            <ul className="space-y-0.5">
              {STATUS_ORDER.map((status) => (
                <li key={status} className="flex items-center justify-between gap-1.5">
                  <span className="flex items-center gap-1.5">
                    <span
                      aria-hidden="true"
                      className="h-2 w-2 rounded-full"
                      style={{ backgroundColor: VIEWPORT_STATUS_STYLE[status].color }}
                    />
                    {VIEWPORT_STATUS_STYLE[status].label}
                  </span>
                  <span className="font-mono text-zinc-400">{statusCounts[status]}</span>
                </li>
              ))}
            </ul>
          </section>
        ) : null}
      </div>
    </div>
  );
}

function Toggle({
  label,
  checked,
  disabled = false,
  onChange,
}: {
  label: string;
  checked: boolean;
  disabled?: boolean;
  onChange: (checked: boolean) => void;
}) {
  return (
    <label className={`flex min-h-8 items-center gap-1 rounded-md border border-white/10 px-2 text-[11px] ${disabled ? 'cursor-not-allowed text-zinc-600' : 'cursor-pointer text-zinc-200'}`}>
      <input
        type="checkbox"
        checked={checked}
        disabled={disabled}
        onChange={(event) => onChange(event.target.checked)}
        className="accent-sky-400"
      />
      {label}
    </label>
  );
}
