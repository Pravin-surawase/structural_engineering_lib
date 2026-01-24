/**
 * Viewport3D Component
 *
 * 3D visualization of beam using React Three Fiber.
 * Renders concrete beam mesh with basic material.
 */
import { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Grid, Environment, PerspectiveCamera } from '@react-three/drei';
import * as THREE from 'three';
import { useDesignStore } from '../store/designStore';
import './Viewport3D.css';

interface BeamMeshProps {
  width: number; // mm
  depth: number; // mm
  length: number; // mm
  isDesigned: boolean;
}

function BeamMesh({ width, depth, length, isDesigned }: BeamMeshProps) {
  const meshRef = useRef<THREE.Mesh>(null);

  // Convert mm to meters for Three.js units
  const scale = 0.001;
  const w = width * scale;
  const d = depth * scale;
  const l = length * scale;

  // Subtle animation when designed
  useFrame(() => {
    if (meshRef.current && isDesigned) {
      // Small pulse effect when newly designed
    }
  });

  const material = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: isDesigned ? '#a0a0a0' : '#808080',
        metalness: 0.1,
        roughness: 0.8,
      }),
    [isDesigned]
  );

  return (
    <mesh ref={meshRef} position={[0, d / 2, 0]} material={material}>
      <boxGeometry args={[l, d, w]} />
    </mesh>
  );
}

function RebarVisualization({
  width,
  length,
  astRequired,
}: {
  width: number;
  length: number;
  astRequired: number;
}) {
  const scale = 0.001;
  const cover = 40 * scale; // 40mm cover

  // Calculate number of bars (simplified: assume 16mm bars)
  const barDiameter = 16 * scale;
  const barArea = Math.PI * Math.pow(8, 2); // mm² for 16mm bar
  const numBars = Math.max(2, Math.ceil(astRequired / barArea));

  // Generate bar positions
  const barPositions = useMemo(() => {
    const positions: [number, number, number][] = [];
    const w = width * scale;
    const effectiveWidth = w - 2 * cover - barDiameter;

    for (let i = 0; i < Math.min(numBars, 6); i++) {
      const x = 0;
      const y = cover + barDiameter / 2;
      const z = -effectiveWidth / 2 + (i / Math.max(numBars - 1, 1)) * effectiveWidth;
      positions.push([x, y, z]);
    }

    return positions;
  }, [width, numBars, cover, barDiameter, scale]);

  const rebarMaterial = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: '#b87333', // Copper/rebar color
        metalness: 0.6,
        roughness: 0.4,
      }),
    []
  );

  return (
    <group>
      {barPositions.map((pos, i) => (
        <mesh key={i} position={pos} rotation={[0, 0, Math.PI / 2]} material={rebarMaterial}>
          <cylinderGeometry args={[barDiameter / 2, barDiameter / 2, length * scale, 16]} />
        </mesh>
      ))}
    </group>
  );
}

function Scene() {
  const { inputs, length, result } = useDesignStore();

  return (
    <>
      {/* Camera */}
      <PerspectiveCamera makeDefault position={[3, 2, 3]} fov={50} />

      {/* Lighting */}
      <ambientLight intensity={0.4} />
      <directionalLight position={[5, 10, 5]} intensity={1} castShadow />
      <directionalLight position={[-5, 5, -5]} intensity={0.3} />

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

      {/* Rebar (only if designed) */}
      {result && result.flexure && (
        <RebarVisualization
          width={inputs.width}
          length={length}
          astRequired={result.flexure.ast_required}
        />
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
        <Scene />
      </Canvas>
      <div className="viewport-overlay">
        <span>3D Viewport • Scroll to zoom • Drag to rotate</span>
      </div>
    </div>
  );
}
