import { Environment, Grid, Html } from '@react-three/drei';
import { useMemo } from 'react';
import * as THREE from 'three';
import { useWebGLContextLoss } from '../../hooks/useWebGLContextLoss';
import type { BeamCSVRow } from '../../types/csv';
import type { WorkspaceSnapshotV1 } from '../../workspace/types';
import { SelectedBeamDetailLayer } from './BeamDetailLayer';
import { BuildingCameraRig } from './BuildingCameraRig';
import { cameraPoseForMembers } from './cameraModel';
import {
  globalSourcePointToRendererM,
  type GeometryMemberV1,
  type GeometrySpaceV1,
} from './geometrySpace';
import {
  VIEWPORT_STATUS_STYLE,
  type ViewportMemberInspection,
} from './inspectionModel';
import { MM_TO_M } from './renderPrimitives';

export type ViewportFrameFilter = 'all' | GeometryMemberV1['frameType'];

function matchesFloor(member: GeometryMemberV1, selectedFloor: string | null): boolean {
  return !selectedFloor
    || member.story.trim().toLowerCase() === selectedFloor.trim().toLowerCase();
}

function memberTransform(member: GeometryMemberV1) {
  const start = new THREE.Vector3(...globalSourcePointToRendererM(member.start));
  const end = new THREE.Vector3(...globalSourcePointToRendererM(member.end));
  const midpoint = new THREE.Vector3().addVectors(start, end).multiplyScalar(0.5);
  const direction = new THREE.Vector3().subVectors(end, start);
  const length = direction.length();
  if (length < 0.01) return null;
  direction.normalize();
  return {
    midpoint,
    length,
    quaternion: new THREE.Quaternion().setFromUnitVectors(
      new THREE.Vector3(1, 0, 0),
      direction,
    ),
  };
}

export function BuildingScene({
  space,
  snapshot,
  beamsByMemberId,
  inspection,
  selectedMemberId,
  selectedFloor,
  frameFilter,
  isolateSelection,
  showStatus,
  showUtilization,
  focusRequest,
  onSelectMember,
}: {
  space: GeometrySpaceV1;
  snapshot: WorkspaceSnapshotV1;
  beamsByMemberId: ReadonlyMap<string, BeamCSVRow>;
  inspection: readonly ViewportMemberInspection[];
  selectedMemberId: string | null;
  selectedFloor: string | null;
  frameFilter: ViewportFrameFilter;
  isolateSelection: boolean;
  showStatus: boolean;
  showUtilization: boolean;
  focusRequest: number;
  onSelectMember: (memberId: string) => void;
}) {
  const contextLost = useWebGLContextLoss();
  const inspectionByMemberId = useMemo(
    () => new Map(inspection.map((member) => [member.memberId, member] as const)),
    [inspection],
  );
  const visibleMembers = useMemo(() => space.members.filter((member) => (
    matchesFloor(member, selectedFloor)
    && (frameFilter === 'all' || member.frameType === frameFilter)
    && (!isolateSelection || !selectedMemberId || member.memberId === selectedMemberId)
  )), [frameFilter, isolateSelection, selectedFloor, selectedMemberId, space.members]);
  const cameraMembers = visibleMembers.length > 0 ? visibleMembers : space.members;
  const selectedIsVisible = Boolean(
    selectedMemberId && visibleMembers.some((member) => member.memberId === selectedMemberId),
  );
  const cameraPose = useMemo(
    () => cameraPoseForMembers(cameraMembers, selectedIsVisible ? selectedMemberId : null),
    [cameraMembers, selectedIsVisible, selectedMemberId],
  );

  if (contextLost) {
    return (
      <Html center>
        <div className="rounded-xl border border-amber-500/30 bg-zinc-950/95 px-4 py-3 text-center text-sm text-white">
          <p className="font-semibold">3D context interrupted</p>
          <p className="mt-1 text-xs text-zinc-400">Project status and selection remain available outside the canvas.</p>
        </div>
      </Html>
    );
  }

  return (
    <>
      <BuildingCameraRig pose={cameraPose} focusRequest={focusRequest} />
      <ambientLight intensity={0.6} />
      <directionalLight position={[10, 20, 10]} intensity={1} />
      <directionalLight position={[-10, 10, -10]} intensity={0.3} />
      <Environment preset="city" />
      <Grid
        args={[50, 50]}
        cellSize={1}
        cellThickness={0.5}
        cellColor="#3a3a3a"
        sectionSize={5}
        sectionThickness={1}
        sectionColor="#5a5a5a"
        fadeDistance={50}
        fadeStrength={1}
        infiniteGrid
      />

      {visibleMembers.map((member) => {
        const transform = memberTransform(member);
        if (!transform) return null;
        const memberInspection = inspectionByMemberId.get(member.memberId);
        const isSelected = member.memberId === selectedMemberId;
        const color = showStatus && memberInspection
          ? VIEWPORT_STATUS_STYLE[memberInspection.status].color
          : '#4aa3ff';
        const depthM = member.section.depthMm * MM_TO_M;
        const widthM = member.section.widthMm * MM_TO_M;
        return (
          <group key={member.memberId}>
            <mesh
              position={transform.midpoint}
              quaternion={transform.quaternion}
              onClick={(event) => {
                event.stopPropagation();
                onSelectMember(member.memberId);
              }}
            >
              <boxGeometry args={[transform.length, depthM, widthM]} />
              <meshStandardMaterial
                color={color}
                metalness={0.1}
                roughness={0.8}
                emissive={isSelected ? '#38bdf8' : '#000000'}
                emissiveIntensity={isSelected ? 0.45 : 0}
              />
            </mesh>
            {isSelected ? (
              <>
                <mesh position={transform.midpoint} quaternion={transform.quaternion}>
                  <boxGeometry args={[transform.length * 1.01, depthM * 1.08, widthM * 1.08]} />
                  <meshBasicMaterial color="#38bdf8" wireframe transparent opacity={0.8} />
                </mesh>
                <Html
                  position={[
                    transform.midpoint.x,
                    transform.midpoint.y + depthM + 0.3,
                    transform.midpoint.z,
                  ]}
                  center
                  sprite
                  style={{ pointerEvents: 'none' }}
                >
                  <div className="whitespace-nowrap rounded-md border border-sky-400/40 bg-black/85 px-2 py-1 text-xs text-white shadow-lg">
                    <span className="font-medium">{member.label}</span>
                    <span className="ml-1 text-sky-300">{member.story}</span>
                    {memberInspection ? (
                      <span className="ml-2" style={{ color: VIEWPORT_STATUS_STYLE[memberInspection.status].color }}>
                        {VIEWPORT_STATUS_STYLE[memberInspection.status].label}
                      </span>
                    ) : null}
                    {showUtilization && memberInspection?.utilization != null ? (
                      <span className="ml-2 text-zinc-300">
                        U {memberInspection.utilization.toFixed(3)}
                      </span>
                    ) : null}
                  </div>
                </Html>
              </>
            ) : null}
          </group>
        );
      })}

      {visibleMembers.length === 0 ? (
        <Html center>
          <div className="rounded-lg border border-zinc-700 bg-zinc-950/95 px-3 py-2 text-sm text-zinc-200">
            No members match the current viewport filters.
          </div>
        </Html>
      ) : null}

      <SelectedBeamDetailLayer
        selectedMemberId={selectedIsVisible ? selectedMemberId : null}
        snapshot={snapshot}
        beamsByMemberId={beamsByMemberId}
        inspectionByMemberId={inspectionByMemberId}
      />
    </>
  );
}
