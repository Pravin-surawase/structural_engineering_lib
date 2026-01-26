/**
 * Viewport3D Component
 *
 * 3D visualization of beam using React Three Fiber.
 * Renders concrete beam mesh with reinforcement bars and stirrups.
 *
 * Uses library API via useBeamGeometry hook for accurate bar positions
 * instead of manual calculations.
 */
import { useMemo, Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Grid, Environment, PerspectiveCamera } from '@react-three/drei';
import * as THREE from 'three';
import { useDesignStore } from '../store/designStore';
import { useBeamGeometry } from '../hooks/useBeamGeometry';
import type { RebarPath, StirrupLoop } from '../hooks/useBeamGeometry';
import './Viewport3D.css';

// Constants
const SCALE = 0.001; // mm to meters

interface BeamMeshProps {
  width: number; // mm
  depth: number; // mm
  length: number; // mm
  isDesigned: boolean;
}

function BeamMesh({ width, depth, length, isDesigned }: BeamMeshProps) {
  const w = width * SCALE;
  const d = depth * SCALE;
  const l = length * SCALE;

  const material = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: isDesigned ? '#b0b0b0' : '#909090',
        metalness: 0.1,
        roughness: 0.85,
        transparent: true,
        opacity: isDesigned ? 0.7 : 0.9, // Semi-transparent when designed to show rebar
      }),
    [isDesigned]
  );

  return (
    <mesh position={[0, d / 2, 0]} material={material}>
      <boxGeometry args={[l, d, w]} />
    </mesh>
  );
}

interface RebarProps {
  rebars: RebarPath[];
}

/**
 * RebarVisualization - Renders rebars from API geometry.
 *
 * Uses accurate bar positions from library's geometry_3d module
 * instead of manual calculations.
 */
function RebarVisualization({ rebars }: RebarProps) {
  const rebarMaterial = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: '#c87533',
        metalness: 0.7,
        roughness: 0.35,
      }),
    []
  );

  return (
    <group>
      {rebars.map((rebar) =>
        rebar.segments.map((segment, segIdx) => {
          // Convert mm to meters
          const start: [number, number, number] = [
            segment.start.x * SCALE,
            segment.start.z * SCALE, // Z in library = Y in Three.js (up)
            segment.start.y * SCALE, // Y in library = Z in Three.js (depth)
          ];
          const end: [number, number, number] = [
            segment.end.x * SCALE,
            segment.end.z * SCALE,
            segment.end.y * SCALE,
          ];

          // Calculate bar position (midpoint) and length
          const midpoint: [number, number, number] = [
            (start[0] + end[0]) / 2,
            (start[1] + end[1]) / 2,
            (start[2] + end[2]) / 2,
          ];
          const length = segment.length * SCALE;
          const radius = (segment.diameter / 2) * SCALE;

          return (
            <mesh
              key={`${rebar.barId}-${segIdx}`}
              position={midpoint}
              rotation={[0, 0, Math.PI / 2]}
              material={rebarMaterial}
            >
              <cylinderGeometry args={[radius, radius, length, 12]} />
            </mesh>
          );
        })
      )}
    </group>
  );
}

interface StirrupsProps {
  stirrups: StirrupLoop[];
}

/**
 * StirrupVisualization - Renders stirrups from API geometry.
 *
 * Uses accurate stirrup positions and paths from library.
 */
function StirrupVisualization({ stirrups }: StirrupsProps) {
  const stirrupMaterial = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: '#a06020',
        metalness: 0.6,
        roughness: 0.4,
      }),
    []
  );

  return (
    <group>
      {stirrups.map((stirrup, i) => {
        // Stirrup path is a closed loop of 4 corners in Y-Z plane at position X
        const path = stirrup.path;
        const xPos = stirrup.positionX * SCALE;
        const radius = (stirrup.diameter / 2) * SCALE;

        // Render each edge of the stirrup loop
        return (
          <group key={i}>
            {path.map((point, j) => {
              const nextPoint = path[(j + 1) % path.length];

              // Convert library coordinates to Three.js
              // Library: X=span, Y=width, Z=height
              // Three.js: X=span, Y=height, Z=width
              const start: [number, number, number] = [
                xPos,
                point.z * SCALE, // Z->Y (height)
                point.y * SCALE, // Y->Z (width)
              ];
              const end: [number, number, number] = [
                xPos,
                nextPoint.z * SCALE,
                nextPoint.y * SCALE,
              ];

              // Calculate segment properties
              const dx = end[0] - start[0];
              const dy = end[1] - start[1];
              const dz = end[2] - start[2];
              const segmentLength = Math.sqrt(dx * dx + dy * dy + dz * dz);

              if (segmentLength < 0.001) return null;

              const midpoint: [number, number, number] = [
                (start[0] + end[0]) / 2,
                (start[1] + end[1]) / 2,
                (start[2] + end[2]) / 2,
              ];

              // Calculate rotation to align cylinder with segment
              const isVertical = Math.abs(dy) > Math.abs(dz);

              return (
                <mesh
                  key={`${i}-${j}`}
                  position={midpoint}
                  rotation={isVertical ? [Math.PI / 2, 0, 0] : [0, Math.PI / 2, 0]}
                  material={stirrupMaterial}
                >
                  <cylinderGeometry args={[radius, radius, segmentLength, 8]} />
                </mesh>
              );
            })}
          </group>
        );
      })}
    </group>
  );
}

function Scene() {
  const { inputs, length, result } = useDesignStore();

  // Fetch geometry from library API when design is complete
  const { data: geometry } = useBeamGeometry(
    result
      ? {
          width: inputs.width,
          depth: inputs.depth,
          span: length,
          ast_start: result.flexure?.ast_required ?? 500,
          ast_mid: result.flexure?.ast_required ?? 400,
          ast_end: result.flexure?.ast_required ?? 500,
          stirrup_spacing_start: result.shear?.stirrup_spacing ?? 100,
          stirrup_spacing_mid: result.shear?.stirrup_spacing ?? 150,
          stirrup_spacing_end: result.shear?.stirrup_spacing ?? 100,
          cover: 40,
        }
      : null,
    { enabled: result !== null }
  );

  return (
    <>
      {/* Camera */}
      <PerspectiveCamera makeDefault position={[3, 2, 3]} fov={50} />

      {/* Lighting */}
      <ambientLight intensity={0.5} />
      <directionalLight position={[5, 10, 5]} intensity={1.2} castShadow />
      <directionalLight position={[-5, 5, -5]} intensity={0.4} />

      {/* Environment for reflections */}
      <Environment preset="city" />

      {/* Grid */}
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

      {/* Beam Mesh */}
      <BeamMesh
        width={inputs.width}
        depth={inputs.depth}
        length={length}
        isDesigned={result !== null}
      />

      {/* Reinforcement from API geometry */}
      {geometry && geometry.rebars.length > 0 && (
        <>
          <RebarVisualization rebars={geometry.rebars} />
          <StirrupVisualization stirrups={geometry.stirrups} />
        </>
      )}

      {/* Controls */}
      <OrbitControls
        enableDamping
        dampingFactor={0.1}
        minDistance={1}
        maxDistance={20}
        target={[0, 0.2, 0]}
      />
    </>
  );
}

export function Viewport3D() {
  return (
    <div className="viewport3d">
      <Canvas shadows>
        <Suspense fallback={null}>
          <Scene />
        </Suspense>
      </Canvas>
      <div className="viewport-overlay">
        <span>3D Viewport • Scroll to zoom • Drag to rotate</span>
      </div>
    </div>
  );
}
