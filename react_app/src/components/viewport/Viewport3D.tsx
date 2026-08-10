import { Canvas } from '@react-three/fiber';
import React, { Suspense, useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useImportedBeamsStore } from '../../store/importedBeamsStore';
import { useWorkspaceStore } from '../../workspace/workspaceStore';
import { buildGeometrySpaceV1 } from './buildingGeometry';
import { BuildingScene, type ViewportFrameFilter } from './BuildingScene';
import { DesignScene } from './DesignScene';
import {
  buildViewportInspection,
  viewportStatusCounts,
} from './inspectionModel';
import type { RebarPreviewGeometry } from './renderPrimitives';
import { ViewportOverlay } from './ViewportOverlay';

export type { RebarPreviewGeometry } from './renderPrimitives';

export type Viewport3DMode = 'design' | 'building';

export interface Viewport3DProps {
  mode?: Viewport3DMode;
  overrideGeometry?: RebarPreviewGeometry | null;
  /** If true, do not auto-detect building mode from imported geometry. */
  forceMode?: boolean;
  /** Beam dimensions in mm for an explicitly selected design preview. */
  overrideDimensions?: { width: number; depth: number; span: number } | null;
}

interface Viewport3DErrorBoundaryProps {
  children: React.ReactNode;
  fallback: React.ReactNode;
}

class Viewport3DErrorBoundary extends React.Component<
  Viewport3DErrorBoundaryProps,
  { hasError: boolean }
> {
  state = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('[Viewport3D Error]', error, errorInfo);
  }

  render() {
    return this.state.hasError ? this.props.fallback : this.props.children;
  }
}

function CanvasFailure() {
  return (
    <div className="flex h-full items-center justify-center p-4 text-center text-sm text-zinc-200">
      <div className="rounded-xl border border-amber-500/30 bg-zinc-950/90 px-4 py-3">
        <p className="font-semibold text-amber-100">3D rendering unavailable</p>
        <p className="mt-1 text-xs text-zinc-400">Member selection and current evidence remain available in the overlay.</p>
      </div>
    </div>
  );
}

export function Viewport3D({
  mode = 'design',
  overrideGeometry = null,
  forceMode = false,
  overrideDimensions = null,
}: Viewport3DProps) {
  const beams = useImportedBeamsStore((state) => state.beams);
  const selectBeam = useImportedBeamsStore((state) => state.selectBeam);
  const selectFloor = useImportedBeamsStore((state) => state.selectFloor);
  const snapshot = useWorkspaceStore((state) => state.snapshot);
  const [frameFilter, setFrameFilter] = useState<ViewportFrameFilter>('all');
  const [isolateSelection, setIsolateSelection] = useState(false);
  const [showStatus, setShowStatus] = useState(true);
  const [showUtilization, setShowUtilization] = useState(true);
  const [focusRequest, setFocusRequest] = useState(0);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const startedAtRef = useRef(0);

  useEffect(() => {
    startedAtRef.current = performance.now();
  }, []);

  const effectiveMode = forceMode
    ? mode
    : mode === 'building' || beams.some((beam) => beam.point1 && beam.point2)
      ? 'building'
      : 'design';
  const contract = useMemo(
    () => effectiveMode === 'building' ? buildGeometrySpaceV1(snapshot, beams) : null,
    [beams, effectiveMode, snapshot],
  );
  const inspection = useMemo(() => buildViewportInspection(snapshot), [snapshot]);
  const inspectionByMemberId = useMemo(
    () => new Map(inspection.map((member) => [member.memberId, member] as const)),
    [inspection],
  );
  const statusCounts = useMemo(() => viewportStatusCounts(inspection), [inspection]);
  const selectedMemberId = snapshot?.selectedMemberId ?? null;
  const selectedInspection = selectedMemberId
    ? inspectionByMemberId.get(selectedMemberId) ?? null
    : null;
  const floors = useMemo(
    () => contract?.ok
      ? [...new Set(contract.space.members.map((member) => member.story))].sort()
      : [],
    [contract],
  );
  const frameTypes = useMemo(
    () => contract?.ok
      ? [...new Set(contract.space.members.map((member) => member.frameType))].sort()
      : [],
    [contract],
  );
  const hasCurrentUtilization = inspection.some((member) => member.utilization !== null);
  const handleSelectMember = useCallback((memberId: string) => {
    if (!contract?.ok) return;
    const beam = contract.beamsByMemberId.get(memberId);
    if (beam) selectBeam(beam.id);
  }, [contract, selectBeam]);
  const handleFit = useCallback(() => {
    if (selectedInspection) {
      selectFloor(null);
      setFrameFilter('all');
    }
    setFocusRequest((request) => request + 1);
  }, [selectFloor, selectedInspection]);
  const handleCanvasCreated = useCallback(({ gl }: { gl: {
    info: {
      memory: { geometries: number; textures: number };
      render: { calls: number };
    };
  } }) => {
    const usableAt = performance.now();
    const startedAt = startedAtRef.current || usableAt;
    const durationMs = usableAt - startedAt;
    performance.measure('uix-viewport-load-to-usable', {
      start: startedAt,
      end: usableAt,
    });
    requestAnimationFrame(() => requestAnimationFrame(() => {
      const container = containerRef.current;
      if (!container) return;
      container.dataset.viewportUsableMs = durationMs.toFixed(1);
      container.dataset.viewportDrawCalls = String(gl.info.render.calls);
      container.dataset.viewportGeometries = String(gl.info.memory.geometries);
      container.dataset.viewportTextures = String(gl.info.memory.textures);
    }));
  }, []);

  const geometryFailure = contract && !contract.ok ? contract.reason : null;
  const buildingScene = effectiveMode === 'building' && contract?.ok && snapshot ? (
    <BuildingScene
      space={contract.space}
      snapshot={snapshot}
      beamsByMemberId={contract.beamsByMemberId}
      inspection={inspection}
      selectedMemberId={selectedMemberId}
      selectedFloor={snapshot.selectedFloor}
      frameFilter={frameFilter}
      isolateSelection={isolateSelection}
      showStatus={showStatus}
      showUtilization={showUtilization && hasCurrentUtilization}
      focusRequest={focusRequest}
      onSelectMember={handleSelectMember}
    />
  ) : null;

  return (
    <div
      ref={containerRef}
      className="relative h-full w-full overflow-hidden"
      style={{ background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)' }}
      role="region"
      aria-label={effectiveMode === 'building'
        ? `3D building visualization with ${beams.length} members`
        : '3D beam and reinforcement visualization'}
    >
      {effectiveMode === 'building' ? (
        <ViewportOverlay
          floors={floors}
          frameTypes={frameTypes}
          selectedFloor={snapshot?.selectedFloor ?? null}
          frameFilter={frameFilter}
          isolateSelection={isolateSelection}
          showStatus={showStatus}
          showUtilization={showUtilization}
          hasCurrentUtilization={hasCurrentUtilization}
          selected={selectedInspection}
          statusCounts={statusCounts}
          geometryFailure={geometryFailure}
          onFloorChange={selectFloor}
          onFrameFilterChange={setFrameFilter}
          onIsolateSelectionChange={setIsolateSelection}
          onShowStatusChange={setShowStatus}
          onShowUtilizationChange={setShowUtilization}
          onFit={handleFit}
        />
      ) : null}

      {effectiveMode === 'building' && !buildingScene ? (
        <CanvasFailure />
      ) : (
        <Viewport3DErrorBoundary fallback={<CanvasFailure />}>
          <Canvas shadows className="!h-full !w-full" onCreated={handleCanvasCreated}>
            <Suspense fallback={null}>
              {buildingScene ?? (
                <DesignScene
                  overrideGeometry={overrideGeometry}
                  overrideDimensions={overrideDimensions}
                />
              )}
            </Suspense>
          </Canvas>
        </Viewport3DErrorBoundary>
      )}

      <div className="pointer-events-none absolute bottom-2 left-2 rounded bg-black/50 px-2 py-1 text-[11px] text-zinc-400">
        {effectiveMode === 'building'
          ? `${beams.length} members · click to select · drag to orbit`
          : '3D viewport · scroll to zoom · drag to rotate'}
      </div>
    </div>
  );
}
