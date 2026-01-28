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
import { useMemo, useCallback, Suspense, useEffect, useRef } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Grid, Environment, PerspectiveCamera, Html } from '@react-three/drei';
import * as THREE from 'three';
import type { OrbitControls as OrbitControlsImpl } from 'three-stdlib';
import { useDesignStore } from '../store/designStore';
import { useImportedBeamsStore } from '../store/importedBeamsStore';
import { useBeamGeometry } from '../hooks/useBeamGeometry';
import type { RebarPath, StirrupLoop } from '../hooks/useBeamGeometry';
import { deriveBeamStatus } from '../utils/beamStatus';
import type { BeamCSVRow } from '../types/csv';
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
    <mesh position={[l / 2, d / 2, 0]} material={material}>
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
  const { beams, selectedId, selectedFloor, selectBeam } = useImportedBeamsStore();
  const { camera } = useThree();
  const controlsRef = useRef<OrbitControlsImpl | null>(null);
  const focusRef = useRef({
    target: new THREE.Vector3(0, 0, 0),
    position: new THREE.Vector3(0, 5, 10),
  });
  const transitionRef = useRef({
    startTime: 0,
    durationMs: 900,
    startPos: new THREE.Vector3(0, 5, 10),
    startTarget: new THREE.Vector3(0, 0, 0),
    endPos: new THREE.Vector3(0, 5, 10),
    endTarget: new THREE.Vector3(0, 0, 0),
    active: false,
  });

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

  const selectedBeam = useMemo(
    () => beamsWithGeometry.find((beam) => beam.id === selectedId) ?? null,
    [beamsWithGeometry, selectedId]
  );

  const selectedTarget = useMemo(() => {
    if (!selectedBeam?.point1 || !selectedBeam?.point2) return null;
    return [
      (selectedBeam.point1.x + selectedBeam.point2.x) / 2,
      (selectedBeam.point1.z + selectedBeam.point2.z) / 2,
      -(selectedBeam.point1.y + selectedBeam.point2.y) / 2,
    ] as [number, number, number];
  }, [selectedBeam]);

  const selectedLength = useMemo(() => {
    if (!selectedBeam?.point1 || !selectedBeam?.point2) return null;
    const dx = selectedBeam.point1.x - selectedBeam.point2.x;
    const dy = selectedBeam.point1.z - selectedBeam.point2.z;
    const dz = selectedBeam.point1.y - selectedBeam.point2.y;
    return Math.sqrt(dx * dx + dy * dy + dz * dz);
  }, [selectedBeam]);

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

  // Get beam color based on design status and floor isolation
  const getBeamColor = useCallback((beam: typeof beams[0], isSelected: boolean) => {
    if (isSelected) return '#00ff88'; // Selected - bright green

    const status = deriveBeamStatus(beam);
    switch (status) {
      case 'pass':
        return '#22c55e';
      case 'fail':
        return '#ef4444';
      case 'warning':
        return '#f59e0b';
      case 'designing':
        return '#3b82f6';
      default:
        return '#4aa3ff';
    }
  }, []);

  // Determine opacity for floor isolation (normalize story names for comparison)
  const getBeamOpacity = useCallback((beam: typeof beams[0], isSelected: boolean) => {
    if (isSelected) return 1;
    if (selectedFloor) {
      const normalizedSelectedFloor = selectedFloor.trim().toLowerCase();
      const normalizedBeamStory = (beam.story ?? '').trim().toLowerCase();
      // If a floor is selected and this beam is on a different floor, fade it
      if (normalizedBeamStory !== normalizedSelectedFloor) return 0.08;
    }
    return 1;
  }, [selectedFloor]);

  useEffect(() => {
    const target = (selectedTarget ?? buildingCenter) as [number, number, number];
    const distance = selectedLength
      ? Math.min(Math.max(selectedLength * 1.8, 8), 120)
      : Math.min(Math.max(buildingSize * 1.2, 10), 120);

    focusRef.current.target.set(target[0], target[1], target[2]);
    focusRef.current.position.set(
      target[0] + distance,
      target[1] + distance * 0.6,
      target[2] + distance
    );

    transitionRef.current.startTime = performance.now();
    transitionRef.current.startPos.copy(camera.position);
    transitionRef.current.startTarget.copy(
      controlsRef.current?.target ?? focusRef.current.target
    );
    transitionRef.current.endPos.copy(focusRef.current.position);
    transitionRef.current.endTarget.copy(focusRef.current.target);
    transitionRef.current.active = true;
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedTarget, selectedLength]);

  useFrame(() => {
    const transition = transitionRef.current;
    if (!transition.active) {
      camera.position.lerp(focusRef.current.position, 0.08);
      if (controlsRef.current) {
        controlsRef.current.target.lerp(focusRef.current.target, 0.1);
        controlsRef.current.update();
      } else {
        camera.lookAt(focusRef.current.target);
      }
      return;
    }

    const elapsed = performance.now() - transition.startTime;
    const t = Math.min(1, elapsed / transition.durationMs);
    const c1 = 1.70158;
    const c3 = c1 + 1;
    const eased =
      t >= 1 ? 1 : 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);

    camera.position.lerpVectors(transition.startPos, transition.endPos, eased);
    if (controlsRef.current) {
      controlsRef.current.target.lerpVectors(
        transition.startTarget,
        transition.endTarget,
        eased
      );
      controlsRef.current.update();
    } else {
      camera.lookAt(transition.endTarget);
    }

    if (t >= 1) {
      transition.active = false;
    }
  });

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

      {/* Render each beam as a 3D box */}
      {beamsWithGeometry.map((beam) => {
        if (!beam.point1 || !beam.point2) return null;

        const start = new THREE.Vector3(beam.point1.x, beam.point1.z, -beam.point1.y);
        const end = new THREE.Vector3(beam.point2.x, beam.point2.z, -beam.point2.y);
        const mid = new THREE.Vector3().addVectors(start, end).multiplyScalar(0.5);
        const dir = new THREE.Vector3().subVectors(end, start);
        const beamLength = dir.length();
        if (beamLength < 0.01) return null;
        dir.normalize();

        // Beam cross-section (use data or fallback)
        const bW = (beam.b ?? 230) * SCALE; // width in meters
        const bD = (beam.D ?? 450) * SCALE; // depth in meters

        const quat = new THREE.Quaternion().setFromUnitVectors(
          new THREE.Vector3(1, 0, 0),
          dir
        );

        const isSelected = beam.id === selectedId;
        const color = getBeamColor(beam, isSelected);
        const opacity = getBeamOpacity(beam, isSelected);

        return (
          <group key={beam.id}>
            <mesh
              position={mid}
              quaternion={quat}
              onClick={() => selectBeam(beam.id)}
            >
              <boxGeometry args={[beamLength, bD, bW]} />
              <meshStandardMaterial
                color={color}
                transparent={opacity < 1}
                opacity={opacity}
                metalness={0.1}
                roughness={0.8}
                emissive={isSelected ? '#00ff88' : '#000000'}
                emissiveIntensity={isSelected ? 0.3 : 0}
              />
            </mesh>
            {/* Glow effect + wireframe for selected beam */}
            {isSelected && (
              <>
                <mesh position={mid} quaternion={quat}>
                  <boxGeometry args={[beamLength * 1.02, bD * 1.1, bW * 1.1]} />
                  <meshBasicMaterial color="#00ff88" transparent opacity={0.15} />
                </mesh>
                <mesh position={mid} quaternion={quat}>
                  <boxGeometry args={[beamLength, bD, bW]} />
                  <meshBasicMaterial color="#ffffff" wireframe opacity={0.5} transparent />
                </mesh>
                {/* Beam label */}
                <Html
                  position={[mid.x, mid.y + bD + 0.3, mid.z]}
                  center
                  distanceFactor={15}
                  style={{ pointerEvents: 'none' }}
                >
                  <div className="px-2 py-1 rounded-md bg-black/80 backdrop-blur text-white text-xs font-medium whitespace-nowrap border border-green-400/50 shadow-lg">
                    {beam.id}
                    <span className="text-green-400 ml-1">{beam.story}</span>
                  </div>
                </Html>
              </>
            )}
          </group>
        );
      })}

      <SelectedBeamDetail beam={selectedBeam} />

      {/* Controls */}
      <OrbitControls
        ref={controlsRef}
        enableDamping
        dampingFactor={0.1}
        minDistance={5}
        maxDistance={100}
        target={(selectedTarget ?? buildingCenter) as [number, number, number]}
      />
    </>
  );
}

function SelectedBeamDetail({ beam }: { beam: BeamCSVRow | null }) {
  const { beams } = useImportedBeamsStore();

  // Find adjacent beams (share an endpoint with selected beam, within tolerance)
  const adjacentBeams = useMemo(() => {
    if (!beam?.point1 || !beam.point2) return [];
    const tolerance = 0.1; // 10cm tolerance for matching endpoints
    const beamP1 = beam.point1;
    const beamP2 = beam.point2;

    const isNear = (p1: { x: number; y: number; z: number }, p2: { x: number; y: number; z: number }) => {
      const dist = Math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2 + (p1.z - p2.z) ** 2);
      return dist < tolerance;
    };

    return beams.filter((b) => {
      if (b.id === beam.id) return false;
      if (!b.point1 || !b.point2) return false;
      // Check if any endpoint matches
      return (
        isNear(b.point1, beamP1) ||
        isNear(b.point1, beamP2) ||
        isNear(b.point2, beamP1) ||
        isNear(b.point2, beamP2)
      );
    });
  }, [beam, beams]);

  const astBase = useMemo(() => {
    if (!beam) return null;
    if (typeof beam.ast_provided === "number") return beam.ast_provided;
    if (typeof beam.ast_required === "number") return beam.ast_required;
    if (typeof beam.bar_count === "number" && typeof beam.bar_diameter === "number") {
      return beam.bar_count * Math.PI * (beam.bar_diameter / 2) ** 2;
    }
    return null;
  }, [beam]);

  const detailParams = useMemo(() => {
    if (!beam || !astBase) return null;
    const spanMm = beam.span
      ? beam.span
      : beam.point1 && beam.point2
      ? Math.sqrt(
          (beam.point1.x - beam.point2.x) ** 2 +
            (beam.point1.y - beam.point2.y) ** 2 +
            (beam.point1.z - beam.point2.z) ** 2
        ) * 1000
      : 0;
    const stirrupSpacing = beam.stirrup_spacing ?? 150;
    return {
      width: beam.b,
      depth: beam.D,
      span: spanMm,
      fck: beam.fck ?? 25,
      fy: beam.fy ?? 500,
      ast_start: astBase,
      ast_mid: astBase,
      ast_end: astBase,
      stirrup_dia: beam.stirrup_diameter ?? 8,
      stirrup_spacing_start: stirrupSpacing,
      stirrup_spacing_mid: stirrupSpacing,
      stirrup_spacing_end: stirrupSpacing,
      cover: beam.cover ?? 40,
    };
  }, [astBase, beam]);

  const shouldShow = Boolean(beam && astBase && detailParams);
  const { data: detailGeometry } = useBeamGeometry(detailParams, { enabled: shouldShow });

  const placement = useMemo(() => {
    if (!beam?.point1 || !beam.point2) return null;
    const start = new THREE.Vector3(
      beam.point1.x,
      beam.point1.z,
      -beam.point1.y
    );
    const end = new THREE.Vector3(
      beam.point2.x,
      beam.point2.z,
      -beam.point2.y
    );
    const direction = new THREE.Vector3().subVectors(end, start);
    if (direction.length() === 0) return null;
    direction.normalize();
    const quat = new THREE.Quaternion().setFromUnitVectors(
      new THREE.Vector3(1, 0, 0),
      direction
    );
    return { start, quat };
  }, [beam]);

  if (!detailGeometry || !placement) return null;

  return (
    <>
      {/* Selected beam rebar */}
      <group position={placement.start} quaternion={placement.quat}>
        <RebarVisualization rebars={detailGeometry.rebars} />
        {detailGeometry.stirrups.length > 0 && (
          <StirrupVisualization stirrups={detailGeometry.stirrups} />
        )}
      </group>

      {/* Adjacent beams rebar (for continuity check) */}
      {adjacentBeams.map((adjBeam) => (
        <AdjacentBeamRebar key={adjBeam.id} beam={adjBeam} />
      ))}
    </>
  );
}

/** Render rebar for an adjacent beam (lighter opacity) */
function AdjacentBeamRebar({ beam }: { beam: BeamCSVRow }) {
  const astBase = useMemo(() => {
    if (typeof beam.ast_provided === "number") return beam.ast_provided;
    if (typeof beam.ast_required === "number") return beam.ast_required;
    if (typeof beam.bar_count === "number" && typeof beam.bar_diameter === "number") {
      return beam.bar_count * Math.PI * (beam.bar_diameter / 2) ** 2;
    }
    return null;
  }, [beam]);

  const detailParams = useMemo(() => {
    if (!astBase) return null;
    const spanMm = beam.span
      ? beam.span
      : beam.point1 && beam.point2
      ? Math.sqrt(
          (beam.point1.x - beam.point2.x) ** 2 +
            (beam.point1.y - beam.point2.y) ** 2 +
            (beam.point1.z - beam.point2.z) ** 2
        ) * 1000
      : 0;
    const stirrupSpacing = beam.stirrup_spacing ?? 150;
    return {
      width: beam.b,
      depth: beam.D,
      span: spanMm,
      fck: beam.fck ?? 25,
      fy: beam.fy ?? 500,
      ast_start: astBase,
      ast_mid: astBase,
      ast_end: astBase,
      stirrup_dia: beam.stirrup_diameter ?? 8,
      stirrup_spacing_start: stirrupSpacing,
      stirrup_spacing_mid: stirrupSpacing,
      stirrup_spacing_end: stirrupSpacing,
      cover: beam.cover ?? 40,
    };
  }, [astBase, beam]);

  const { data: geom } = useBeamGeometry(detailParams, { enabled: Boolean(astBase && detailParams) });

  const placement = useMemo(() => {
    if (!beam.point1 || !beam.point2) return null;
    const start = new THREE.Vector3(beam.point1.x, beam.point1.z, -beam.point1.y);
    const end = new THREE.Vector3(beam.point2.x, beam.point2.z, -beam.point2.y);
    const direction = new THREE.Vector3().subVectors(end, start);
    if (direction.length() === 0) return null;
    direction.normalize();
    const quat = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(1, 0, 0), direction);
    return { start, quat };
  }, [beam]);

  if (!geom || !placement) return null;

  // Render with reduced opacity to show adjacency
  const fadedRebarMaterial = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: '#a06838',
        metalness: 0.5,
        roughness: 0.5,
        transparent: true,
        opacity: 0.5,
      }),
    []
  );

  return (
    <group position={placement.start} quaternion={placement.quat}>
      {geom.rebars.map((rebar) =>
        rebar.segments.map((segment, segIdx) => {
          const start: [number, number, number] = [
            segment.start.x * SCALE,
            segment.start.z * SCALE,
            segment.start.y * SCALE,
          ];
          const end: [number, number, number] = [
            segment.end.x * SCALE,
            segment.end.z * SCALE,
            segment.end.y * SCALE,
          ];
          const midpoint: [number, number, number] = [
            (start[0] + end[0]) / 2,
            (start[1] + end[1]) / 2,
            (start[2] + end[2]) / 2,
          ];
          const length = segment.length * SCALE;
          const radius = (segment.diameter / 2) * SCALE;

          return (
            <mesh
              key={`adj-${beam.id}-${rebar.barId}-${segIdx}`}
              position={midpoint}
              rotation={[0, 0, Math.PI / 2]}
              material={fadedRebarMaterial}
            >
              <cylinderGeometry args={[radius, radius, length, 8]} />
            </mesh>
          );
        })
      )}
    </group>
  );
}

export interface RebarPreviewGeometry {
  rebars: RebarPath[];
  stirrups: StirrupLoop[];
}

function Scene({ overrideGeometry }: { overrideGeometry?: RebarPreviewGeometry | null }) {
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

  const activeGeometry = overrideGeometry ?? geometry;

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
      {activeGeometry && activeGeometry.rebars.length > 0 && (
        <>
          <RebarVisualization rebars={activeGeometry.rebars} />
          <StirrupVisualization stirrups={activeGeometry.stirrups} />
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
  overrideGeometry?: RebarPreviewGeometry | null;
  /** If true, don't auto-detect mode; use the provided mode exactly */
  forceMode?: boolean;
}

/**
 * Viewport3D - 3D visualization component.
 *
 * @param mode - 'design' for single beam with rebar, 'building' for imported beams frame
 * @param forceMode - if true, don't auto-detect mode, use the provided mode
 */
export function Viewport3D({ mode = 'design', overrideGeometry = null, forceMode = false }: Viewport3DProps) {
  const { beams } = useImportedBeamsStore();

  // Use exact mode if forced, otherwise auto-detect for 'design' mode
  // Auto-detect only if mode is 'design' AND not forced
  const effectiveMode = forceMode
    ? mode
    : mode === 'building'
      ? 'building'
      : beams.length > 0 && beams.some((b) => b.point1 && b.point2)
        ? 'building'
        : 'design';

  return (
    <div className="viewport3d">
      <Canvas shadows>
        <Suspense fallback={null}>
          {effectiveMode === 'building' ? (
            <BuildingFrame />
          ) : (
            <Scene overrideGeometry={overrideGeometry} />
          )}
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
