/**
 * Viewport3D Component
 *
 * 3D visualization of beam using React Three Fiber.
 * Renders:
 * - Single beam with reinforcement for design mode
 * - Building frame with all beams for import mode
 *
 * Uses library API via useBeamGeometry hook for accurate bar positions
 * instead of manual calculations.
 */
import { useMemo, useCallback, Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Grid, Environment, PerspectiveCamera, Line } from '@react-three/drei';
import * as THREE from 'three';
import { useDesignStore } from '../store/designStore';
import { useImportedBeamsStore } from '../store/importedBeamsStore';
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

/**
 * BuildingFrame - Renders all imported beams as a wireframe.
 *
 * Shows beams from the imported CSV data with 3D positions,
 * allowing users to visualize the building structure.
 * Supports color-coding by design status.
 */
function BuildingFrame() {
  const { beams, selectedId, selectBeam } = useImportedBeamsStore();

  // Filter beams that have 3D positions
  const beamsWithGeometry = useMemo(
    () => beams.filter((b) => b.point1 && b.point2),
    [beams]
  );

  // Calculate center of building for camera target
  const buildingCenter = useMemo(() => {
    if (beamsWithGeometry.length === 0) return [0, 5, 0];
    let sumX = 0, sumY = 0, sumZ = 0;
    beamsWithGeometry.forEach((b) => {
      if (b.point1 && b.point2) {
        sumX += (b.point1.x + b.point2.x) / 2;
        sumY += (b.point1.y + b.point2.y) / 2;
        sumZ += (b.point1.z + b.point2.z) / 2;
      }
    });
    const n = beamsWithGeometry.length;
    return [sumX / n, sumZ / n, -sumY / n]; // Transform to Three.js coords
  }, [beamsWithGeometry]);

  // Calculate building bounds for camera distance
  const buildingSize = useMemo(() => {
    if (beamsWithGeometry.length === 0) return 10;
    let maxDist = 0;
    beamsWithGeometry.forEach((b) => {
      if (b.point1 && b.point2) {
        const dist = Math.max(
          Math.abs(b.point1.x - buildingCenter[0]),
          Math.abs(b.point2.x - buildingCenter[0]),
          Math.abs(b.point1.y + buildingCenter[2]),
          Math.abs(b.point2.y + buildingCenter[2]),
          Math.abs(b.point1.z - buildingCenter[1]),
          Math.abs(b.point2.z - buildingCenter[1])
        );
        maxDist = Math.max(maxDist, dist);
      }
    });
    return Math.max(maxDist * 2, 10);
  }, [beamsWithGeometry, buildingCenter]);

  // Get beam color based on design status
  const getBeamColor = useCallback((beam: typeof beams[0], isSelected: boolean) => {
    if (isSelected) return '#00ff88'; // Selected - green

    // Check for design status (from design result)
    const status = beam.status;
    switch (status) {
      case 'pass':
        return '#22c55e'; // Emerald - safe
      case 'fail':
        return '#ef4444'; // Red - failed
      case 'warning':
        return '#f59e0b'; // Amber - warning
      case 'designing':
        return '#3b82f6'; // Blue - in progress
      default:
        return '#4aa3ff'; // Default blue - pending
    }
  }, []);

  return (
    <>
      {/* Camera positioned to view building */}
      <PerspectiveCamera
        makeDefault
        position={[
          buildingCenter[0] + buildingSize * 1.5,
          buildingCenter[1] + buildingSize * 0.8,
          buildingCenter[2] + buildingSize * 1.5,
        ]}
        fov={50}
      />

      {/* Lighting */}
      <ambientLight intensity={0.6} />
      <directionalLight position={[10, 20, 10]} intensity={1.0} />
      <directionalLight position={[-10, 10, -10]} intensity={0.3} />

      {/* Environment */}
      <Environment preset="city" />

      {/* Grid */}
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

      {/* Render each beam as a line with status color */}
      {beamsWithGeometry.map((beam) => {
        if (!beam.point1 || !beam.point2) return null;

        // Transform from ETABS coords (X, Y horizontal, Z vertical)
        // to Three.js coords (X, Z horizontal, Y vertical)
        const start: [number, number, number] = [
          beam.point1.x,
          beam.point1.z, // Z in ETABS = Y in Three.js (up)
          -beam.point1.y, // Y in ETABS = -Z in Three.js
        ];
        const end: [number, number, number] = [
          beam.point2.x,
          beam.point2.z,
          -beam.point2.y,
        ];

        const isSelected = beam.id === selectedId;
        const color = getBeamColor(beam, isSelected);

        return (
          <Line
            key={beam.id}
            points={[start, end]}
            color={color}
            lineWidth={isSelected ? 4 : 2}
            onClick={() => selectBeam(beam.id)}
          />
        );
      })}

      {/* Controls */}
      <OrbitControls
        enableDamping
        dampingFactor={0.1}
        minDistance={5}
        maxDistance={100}
        target={buildingCenter as [number, number, number]}
      />
    </>
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

export type Viewport3DMode = 'design' | 'building';

interface Viewport3DProps {
  mode?: Viewport3DMode;
}

/**
 * Viewport3D - 3D visualization component.
 *
 * @param mode - 'design' for single beam with rebar, 'building' for imported beams frame
 */
export function Viewport3D({ mode = 'design' }: Viewport3DProps) {
  const { beams } = useImportedBeamsStore();

  // Auto-detect mode: use building view if there are imported beams with 3D positions
  const effectiveMode =
    mode === 'building' ||
    (beams.length > 0 && beams.some((b) => b.point1 && b.point2))
      ? 'building'
      : 'design';

  return (
    <div className="viewport3d">
      <Canvas shadows>
        <Suspense fallback={null}>
          {effectiveMode === 'building' ? <BuildingFrame /> : <Scene />}
        </Suspense>
      </Canvas>
      <div className="viewport-overlay">
        <span>
          {effectiveMode === 'building'
            ? `Building Frame (${beams.length} beams) • Click to select`
            : '3D Viewport • Scroll to zoom • Drag to rotate'}
        </span>
      </div>
    </div>
  );
}
