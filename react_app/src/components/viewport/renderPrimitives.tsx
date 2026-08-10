import * as THREE from 'three';
import type { RebarPath, StirrupLoop } from '../../hooks/useBeamGeometry';
import { localBeamPointToRendererM } from './geometrySpace';

export const MM_TO_M = 0.001;

export interface RebarPreviewGeometry {
  rebars: RebarPath[];
  stirrups: StirrupLoop[];
}

export function BeamMesh({
  width,
  depth,
  length,
  isDesigned,
}: {
  width: number;
  depth: number;
  length: number;
  isDesigned: boolean;
}) {
  const widthM = width * MM_TO_M;
  const depthM = depth * MM_TO_M;
  const lengthM = length * MM_TO_M;
  return (
    <mesh position={[0, depthM / 2, 0]}>
      <boxGeometry args={[lengthM, depthM, widthM]} />
      <meshStandardMaterial
        color={isDesigned ? '#b0b0b0' : '#909090'}
        metalness={0.1}
        roughness={0.85}
        transparent
        opacity={isDesigned ? 0.7 : 0.9}
      />
    </mesh>
  );
}

function segmentTransform(
  start: readonly [number, number, number],
  end: readonly [number, number, number],
) {
  const direction = new THREE.Vector3(
    end[0] - start[0],
    end[1] - start[1],
    end[2] - start[2],
  );
  const length = direction.length();
  if (length < 0.001) return null;
  direction.normalize();
  const quaternion = new THREE.Quaternion().setFromUnitVectors(
    new THREE.Vector3(0, 1, 0),
    direction,
  );
  const euler = new THREE.Euler().setFromQuaternion(quaternion);
  return {
    midpoint: [
      (start[0] + end[0]) / 2,
      (start[1] + end[1]) / 2,
      (start[2] + end[2]) / 2,
    ] as [number, number, number],
    rotation: [euler.x, euler.y, euler.z] as [number, number, number],
    length,
  };
}

export function RebarLayer({
  rebars,
  opacity = 1,
}: {
  rebars: RebarPath[];
  opacity?: number;
}) {
  return (
    <group>
      {rebars.flatMap((rebar) => rebar.segments.map((segment, segmentIndex) => {
        const start = localBeamPointToRendererM(segment.start);
        const end = localBeamPointToRendererM(segment.end);
        const transform = segmentTransform(start, end);
        if (!transform) return null;
        return (
          <mesh
            key={`${rebar.barId}-${segmentIndex}`}
            position={transform.midpoint}
            rotation={transform.rotation}
          >
            <cylinderGeometry
              args={[segment.diameter * MM_TO_M / 2, segment.diameter * MM_TO_M / 2, transform.length, 12]}
            />
            <meshStandardMaterial
              color="#c87533"
              metalness={0.7}
              roughness={0.35}
              transparent={opacity < 1}
              opacity={opacity}
            />
          </mesh>
        );
      }))}
    </group>
  );
}

export function StirrupLayer({ stirrups }: { stirrups: StirrupLoop[] }) {
  return (
    <group>
      {stirrups.map((stirrup, stirrupIndex) => (
        <group key={`${stirrup.positionX}-${stirrupIndex}`}>
          {stirrup.path.map((point, pointIndex) => {
            const nextPoint = stirrup.path[(pointIndex + 1) % stirrup.path.length];
            const start = localBeamPointToRendererM({ ...point, x: stirrup.positionX });
            const end = localBeamPointToRendererM({ ...nextPoint, x: stirrup.positionX });
            const transform = segmentTransform(start, end);
            if (!transform) return null;
            const radius = stirrup.diameter * MM_TO_M / 2;
            return (
              <mesh
                key={`${stirrupIndex}-${pointIndex}`}
                position={transform.midpoint}
                rotation={transform.rotation}
              >
                <cylinderGeometry args={[radius, radius, transform.length, 8]} />
                <meshStandardMaterial color="#a06020" metalness={0.6} roughness={0.4} />
              </mesh>
            );
          })}
        </group>
      ))}
    </group>
  );
}
