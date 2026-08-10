import { Environment, Grid, Html, OrbitControls, PerspectiveCamera } from '@react-three/drei';
import { useMemo } from 'react';
import { useBeamGeometry } from '../../hooks/useBeamGeometry';
import { useWebGLContextLoss } from '../../hooks/useWebGLContextLoss';
import { useDesignStore } from '../../store/designStore';
import {
  BeamMesh,
  MM_TO_M,
  RebarLayer,
  StirrupLayer,
  type RebarPreviewGeometry,
} from './renderPrimitives';

export function DesignScene({
  overrideGeometry,
  overrideDimensions,
}: {
  overrideGeometry?: RebarPreviewGeometry | null;
  overrideDimensions?: { width: number; depth: number; span: number } | null;
}) {
  const contextLost = useWebGLContextLoss();
  const { inputs, length, result, inputRevision, resultRevision, resultLifecycle } = useDesignStore();
  const currentResult = resultLifecycle === 'current' && resultRevision === inputRevision ? result : null;
  const displayWidth = overrideDimensions?.width ?? inputs.width;
  const displayDepth = overrideDimensions?.depth ?? inputs.depth;
  const displaySpan = overrideDimensions?.span ?? length;
  const lengthM = displaySpan * MM_TO_M;
  const depthM = displayDepth * MM_TO_M;
  const cameraDistance = Math.max(lengthM * 0.8, 2);
  const cameraPosition = useMemo<[number, number, number]>(() => [
    cameraDistance * 0.5,
    depthM / 2 + cameraDistance * 0.4,
    cameraDistance * 0.8,
  ], [cameraDistance, depthM]);
  const cameraTarget = useMemo<[number, number, number]>(
    () => [0, depthM / 2, 0],
    [depthM],
  );
  const geometryParams = currentResult ? {
    beam_id: 'quick-design',
    story: 'Quick',
    width: inputs.width,
    depth: inputs.depth,
    span: length,
    fck: inputs.fck,
    fy: inputs.fy,
    ast_start: currentResult.flexure?.ast_required ?? 500,
    ast_mid: currentResult.flexure?.ast_required ?? 400,
    ast_end: currentResult.flexure?.ast_required ?? 500,
    stirrup_spacing_start: currentResult.shear?.stirrup_spacing ?? 100,
    stirrup_spacing_mid: currentResult.shear?.stirrup_spacing ?? 150,
    stirrup_spacing_end: currentResult.shear?.stirrup_spacing ?? 100,
    cover: inputs.clear_cover ?? 40,
  } : null;
  const { data: geometry } = useBeamGeometry(geometryParams, {
    enabled: currentResult !== null,
  });
  const activeGeometry = overrideGeometry ?? geometry;

  if (contextLost) {
    return (
      <Html center>
        <div className="rounded-xl border border-amber-500/30 bg-zinc-950/95 px-4 py-3 text-center text-sm text-white">
          <p className="font-semibold">3D context interrupted</p>
          <p className="mt-1 text-xs text-zinc-400">The current design result remains available in the result panel.</p>
        </div>
      </Html>
    );
  }

  return (
    <>
      <PerspectiveCamera makeDefault position={cameraPosition} fov={50} />
      <ambientLight intensity={0.5} />
      <directionalLight position={[5, 10, 5]} intensity={1.2} castShadow />
      <directionalLight position={[-5, 5, -5]} intensity={0.4} />
      <Environment preset="city" />
      <Grid
        args={[10, 10]}
        cellSize={0.5}
        cellThickness={0.5}
        cellColor="#3a3a3a"
        sectionSize={2}
        sectionThickness={1}
        sectionColor="#5a5a5a"
        fadeDistance={20}
        fadeStrength={1}
        infiniteGrid
      />
      <BeamMesh
        width={displayWidth}
        depth={displayDepth}
        length={displaySpan}
        isDesigned={currentResult !== null || overrideDimensions !== null}
      />
      {activeGeometry ? (
        <group position={[-displaySpan * MM_TO_M / 2, 0, 0]}>
          {activeGeometry.rebars.length > 0 ? <RebarLayer rebars={activeGeometry.rebars} /> : null}
          {activeGeometry.stirrups.length > 0 ? <StirrupLayer stirrups={activeGeometry.stirrups} /> : null}
        </group>
      ) : null}
      <OrbitControls
        enableDamping
        dampingFactor={0.1}
        minDistance={0.5}
        maxDistance={20}
        target={cameraTarget}
      />
    </>
  );
}
