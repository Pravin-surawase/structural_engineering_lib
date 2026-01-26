/**
 * Viewport3D Component
 *
 * 3D visualization of beam using React Three Fiber.
 * Renders concrete beam mesh with reinforcement bars and stirrups.
 */
import { useMemo, Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Grid, Environment, PerspectiveCamera } from '@react-three/drei';
import * as THREE from 'three';
import { useDesignStore } from '../store/designStore';
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
  width: number;
  depth: number;
  length: number;
  astRequired: number;
  ascRequired?: number;
}

function RebarVisualization({ width, depth, length, astRequired, ascRequired = 0 }: RebarProps) {
  const cover = 40 * SCALE;
  const stirrupDia = 8 * SCALE;

  // Calculate tension bar layout
  const { tensionBars, compressionBars } = useMemo(() => {
    const barDiameter = 16 * SCALE;
    const barArea = Math.PI * Math.pow(8, 2); // mm² for 16mm bar

    const numTension = Math.max(2, Math.min(6, Math.ceil(astRequired / barArea)));
    const numCompression = ascRequired > 0 ? Math.max(2, Math.min(4, Math.ceil(ascRequired / barArea))) : 0;

    const w = width * SCALE;
    const d = depth * SCALE;
    const effectiveWidth = w - 2 * (cover + stirrupDia) - barDiameter;

    const tension: [number, number, number][] = [];
    for (let i = 0; i < numTension; i++) {
      const x = 0;
      const y = cover + stirrupDia + barDiameter / 2;
      const z = -effectiveWidth / 2 + (i / Math.max(numTension - 1, 1)) * effectiveWidth;
      tension.push([x, y, z]);
    }

    const compression: [number, number, number][] = [];
    for (let i = 0; i < numCompression; i++) {
      const x = 0;
      const y = d - cover - stirrupDia - barDiameter / 2;
      const z = -effectiveWidth / 2 + (i / Math.max(numCompression - 1, 1)) * effectiveWidth;
      compression.push([x, y, z]);
    }

    return { tensionBars: tension, compressionBars: compression, barDiameter };
  }, [width, depth, astRequired, ascRequired, cover, stirrupDia]);

  const rebarMaterial = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: '#c87533',
        metalness: 0.7,
        roughness: 0.35,
      }),
    []
  );

  const barDiameter = 16 * SCALE;

  return (
    <group>
      {/* Tension bars (bottom) */}
      {tensionBars.map((pos, i) => (
        <mesh key={`t-${i}`} position={pos} rotation={[0, 0, Math.PI / 2]} material={rebarMaterial}>
          <cylinderGeometry args={[barDiameter / 2, barDiameter / 2, length * SCALE * 0.98, 12]} />
        </mesh>
      ))}
      {/* Compression bars (top) */}
      {compressionBars.map((pos, i) => (
        <mesh key={`c-${i}`} position={pos} rotation={[0, 0, Math.PI / 2]} material={rebarMaterial}>
          <cylinderGeometry args={[barDiameter / 2, barDiameter / 2, length * SCALE * 0.98, 12]} />
        </mesh>
      ))}
    </group>
  );
}

interface StirrupsProps {
  width: number;
  depth: number;
  length: number;
  spacing: number;
}

function StirrupVisualization({ width, depth, length, spacing }: StirrupsProps) {
  const cover = 40 * SCALE;
  const stirrupDia = 8 * SCALE;
  const halfDia = stirrupDia / 2;

  const stirrups = useMemo(() => {
    const w = width * SCALE - 2 * cover;
    const d = depth * SCALE - 2 * cover;
    const l = length * SCALE;
    const spacingM = spacing * SCALE;

    const numStirrups = Math.floor(l / spacingM);
    const startX = -l / 2 + spacingM / 2;

    const positions: number[] = [];
    for (let i = 0; i < numStirrups; i++) {
      positions.push(startX + i * spacingM);
    }

    return { positions, w, d };
  }, [width, depth, length, spacing, cover]);

  const stirrupMaterial = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: '#a06020',
        metalness: 0.6,
        roughness: 0.4,
      }),
    []
  );

  const { positions, w, d } = stirrups;

  return (
    <group>
      {positions.map((xPos, i) => (
        <group key={i} position={[xPos, depth * SCALE / 2, 0]}>
          {/* Bottom horizontal */}
          <mesh position={[0, -d / 2 + halfDia, 0]} rotation={[0, Math.PI / 2, 0]} material={stirrupMaterial}>
            <cylinderGeometry args={[halfDia, halfDia, w - stirrupDia, 8]} />
          </mesh>
          {/* Top horizontal */}
          <mesh position={[0, d / 2 - halfDia, 0]} rotation={[0, Math.PI / 2, 0]} material={stirrupMaterial}>
            <cylinderGeometry args={[halfDia, halfDia, w - stirrupDia, 8]} />
          </mesh>
          {/* Left vertical */}
          <mesh position={[0, 0, -w / 2 + halfDia]} rotation={[Math.PI / 2, 0, 0]} material={stirrupMaterial}>
            <cylinderGeometry args={[halfDia, halfDia, d - stirrupDia, 8]} />
          </mesh>
          {/* Right vertical */}
          <mesh position={[0, 0, w / 2 - halfDia]} rotation={[Math.PI / 2, 0, 0]} material={stirrupMaterial}>
            <cylinderGeometry args={[halfDia, halfDia, d - stirrupDia, 8]} />
          </mesh>
        </group>
      ))}
    </group>
  );
}

function Scene() {
  const { inputs, length, result } = useDesignStore();

  // Get stirrup spacing from result or use default
  const stirrupSpacing = result?.shear?.stirrup_spacing ?? 150;

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

      {/* Reinforcement (only if designed) */}
      {result && result.flexure && (
        <>
          {/* Rebar */}
          <RebarVisualization
            width={inputs.width}
            depth={inputs.depth}
            length={length}
            astRequired={result.flexure.ast_required}
            ascRequired={result.flexure.asc_required}
          />
          {/* Stirrups (if shear result available) */}
          {result.shear && (
            <StirrupVisualization
              width={inputs.width}
              depth={inputs.depth}
              length={length}
              spacing={stirrupSpacing}
            />
          )}
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
