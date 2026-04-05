/**
 * HomePage - Minimal landing page with full-screen 3D beam construction animation
 */
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Float } from "@react-three/drei";
import { Suspense, useMemo, useRef, useEffect } from "react";
import * as THREE from "three";
import { useReducedMotion } from "../../hooks/useReducedMotion";

/** Animated beam construction (12s build + continuous rotation) */
function AnimatedBeamConstruction() {
  const prefersReducedMotion = useReducedMotion();
  const elapsed = useRef(0);
  const groupRef = useRef<THREE.Group>(null);
  const constructionComplete = useRef(false);

  // Beam dimensions
  const beamLength = 4.0;
  const beamDepth = 0.5;
  const beamWidth = 0.3;
  const cover = 0.025;
  const rebarDia = 0.016;

  // Refs for animated objects
  const formworkRef = useRef<THREE.LineSegments>(null);
  const concreteRef = useRef<THREE.Mesh>(null);
  const bottomRebarsRef = useRef<THREE.Group>(null);
  const topRebarsRef = useRef<THREE.Group>(null);
  const stirrupsRef = useRef<THREE.Group>(null);
  const loadsRef = useRef<THREE.Group>(null);

  // Geometries - imperatively created, need manual disposal
  const { formworkGeometry, formworkBaseGeometry } = useMemo(() => {
    const baseGeo = new THREE.BoxGeometry(beamLength, beamDepth, beamWidth);
    const edgesGeo = new THREE.EdgesGeometry(baseGeo);
    return { formworkGeometry: edgesGeo, formworkBaseGeometry: baseGeo };
  }, []);

  const concreteGeometry = useMemo(() => {
    return new THREE.BoxGeometry(beamLength, beamDepth, beamWidth);
  }, []);

  const stirrupGeometry = useMemo(() => {
    const w = beamWidth - 2 * cover;
    const h = beamDepth - 2 * cover;
    const points = [
      new THREE.Vector3(-w / 2, -h / 2, 0),
      new THREE.Vector3(w / 2, -h / 2, 0),
      new THREE.Vector3(w / 2, h / 2, 0),
      new THREE.Vector3(-w / 2, h / 2, 0),
      new THREE.Vector3(-w / 2, -h / 2, 0),
    ];
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    return geometry;
  }, []);

  // Pre-create stirrup geometries
  const stirrupGeometries = useMemo(() => {
    const count = 8;
    return Array.from({ length: count }, () => stirrupGeometry.clone());
  }, [stirrupGeometry]);

  // Dispose Three.js geometries on unmount to prevent GPU memory leaks
  useEffect(() => {
    return () => {
      formworkGeometry.dispose();
      formworkBaseGeometry.dispose(); // Dispose the BoxGeometry used to create EdgesGeometry
      concreteGeometry.dispose();
      stirrupGeometry.dispose();
      stirrupGeometries.forEach((geo) => geo.dispose());
    };
  }, [formworkGeometry, formworkBaseGeometry, concreteGeometry, stirrupGeometry, stirrupGeometries]);

  // Bottom rebars: 4 bars
  const bottomRebarPositions = useMemo(() => {
    const y = -beamDepth / 2 + cover + rebarDia / 2;
    const spacing = (beamWidth - 2 * cover - rebarDia) / 3;
    return [
      [-beamWidth / 2 + cover + rebarDia / 2, y],
      [-beamWidth / 2 + cover + rebarDia / 2 + spacing, y],
      [-beamWidth / 2 + cover + rebarDia / 2 + 2 * spacing, y],
      [beamWidth / 2 - cover - rebarDia / 2, y],
    ];
  }, []);

  // Top rebars: 2 bars
  const topRebarPositions = useMemo(() => {
    const y = beamDepth / 2 - cover - rebarDia / 2;
    const spacing = beamWidth - 2 * cover - rebarDia;
    return [
      [-spacing / 2, y],
      [spacing / 2, y],
    ];
  }, []);

  // Stirrup positions: 8 stirrups
  const stirrupPositions = useMemo(() => {
    const count = 8;
    const spacing = beamLength / (count + 1);
    return Array.from({ length: count }, (_, i) => -beamLength / 2 + spacing * (i + 1));
  }, []);

  useFrame((_, delta) => {
    // Skip animations if user prefers reduced motion
    if (prefersReducedMotion) {
      // Show final state - all elements visible, construction complete
      if (formworkRef.current) {
        formworkRef.current.scale.setScalar(1);
        (formworkRef.current.material as THREE.LineBasicMaterial).opacity = 0.3;
      }
      if (concreteRef.current) {
        (concreteRef.current.material as THREE.MeshPhysicalMaterial).opacity = 0.45;
      }
      if (bottomRebarsRef.current) {
        bottomRebarsRef.current.children.forEach((rebar) => {
          rebar.position.x = 0;
          ((rebar as THREE.Mesh).material as THREE.MeshStandardMaterial).opacity = 0.85;
        });
      }
      if (topRebarsRef.current) {
        topRebarsRef.current.children.forEach((rebar) => {
          rebar.position.x = 0;
          ((rebar as THREE.Mesh).material as THREE.MeshStandardMaterial).opacity = 0.85;
        });
      }
      if (stirrupsRef.current) {
        stirrupsRef.current.children.forEach((stirrup) => {
          stirrup.scale.set(1, 1, 1);
          ((stirrup as THREE.LineSegments).material as THREE.LineBasicMaterial).opacity = 0.75;
        });
      }
      if (loadsRef.current) {
        loadsRef.current.children.forEach((load) => {
          load.scale.setScalar(1);
          load.children.forEach((child) => {
            ((child as THREE.Mesh).material as THREE.MeshStandardMaterial).opacity = 0.85;
          });
        });
      }
      return;
    }

    elapsed.current += delta;
    const t = elapsed.current;

    // Construction phases (0-12s), then continuous rotation
    const constructionDuration = 12;

    if (t <= constructionDuration) {
      // Phase 1 (0-2s): Formwork appears
      if (formworkRef.current) {
        const scale = Math.min(1, t / 2);
        const easedScale = scale < 1 ? 1 - Math.cos((scale * Math.PI) / 2) : 1;
        formworkRef.current.scale.setScalar(easedScale);
        (formworkRef.current.material as THREE.LineBasicMaterial).opacity = easedScale * 0.7;
      }

      // Phase 2 (2-4s): Bottom rebars slide in
      if (bottomRebarsRef.current && t >= 2) {
        const rebarPhase = Math.max(0, t - 2) / 2.0;

        bottomRebarsRef.current.children.forEach((rebar, i) => {
          const stagger = i * 0.15;
          const progress = Math.min(1, Math.max(0, rebarPhase - stagger / 2.0) * (2.0 / (2.0 - stagger)));
          const easedProgress = progress < 1 ? 1 - Math.cos((progress * Math.PI) / 2) : 1;
          rebar.position.x = THREE.MathUtils.lerp(-beamLength, 0, easedProgress);
          ((rebar as THREE.Mesh).material as THREE.MeshStandardMaterial).opacity = easedProgress * 0.85;
        });
      }

      // Phase 3 (4-6s): Top rebars slide in
      if (topRebarsRef.current && t >= 4) {
        const topRebarPhase = Math.max(0, t - 4) / 2.0;

        topRebarsRef.current.children.forEach((rebar, i) => {
          const stagger = i * 0.15;
          const progress = Math.min(1, Math.max(0, topRebarPhase - stagger / 2.0) * (2.0 / (2.0 - stagger)));
          const easedProgress = progress < 1 ? 1 - Math.cos((progress * Math.PI) / 2) : 1;
          rebar.position.x = THREE.MathUtils.lerp(beamLength, 0, easedProgress);
          ((rebar as THREE.Mesh).material as THREE.MeshStandardMaterial).opacity = easedProgress * 0.85;
        });
      }

      // Phase 4 (6-8.5s): Stirrups materialize
      if (stirrupsRef.current && t >= 6) {
        const stirrupPhase = Math.max(0, t - 6) / 2.5;
        stirrupsRef.current.children.forEach((stirrup, i) => {
          const stagger = i * 0.12;
          const progress = Math.min(1, Math.max(0, stirrupPhase - stagger / 2.5) * (2.5 / (2.5 - stagger)));
          const easedProgress = progress < 1 ? 1 - Math.cos((progress * Math.PI) / 2) : 1;
          const scale = THREE.MathUtils.lerp(0.8, 1, easedProgress);
          stirrup.scale.set(scale, scale, scale);
          ((stirrup as THREE.LineSegments).material as THREE.LineBasicMaterial).opacity = easedProgress * 0.75;
        });
      }

      // Phase 5 (8.5-10.5s): Concrete fills
      if (concreteRef.current && formworkRef.current && t >= 8.5) {
        const concretePhase = Math.max(0, t - 8.5) / 2.0;
        const easedPhase = concretePhase < 1 ? 1 - Math.cos((concretePhase * Math.PI) / 2) : 1;
        (concreteRef.current.material as THREE.MeshPhysicalMaterial).opacity = easedPhase * 0.45;
        (formworkRef.current.material as THREE.LineBasicMaterial).opacity = THREE.MathUtils.lerp(0.7, 0.3, easedPhase);
      }

      // Phase 6 (10.5-12s): Load arrows + deflection
      if (loadsRef.current && t >= 10.5) {
        const loadPhase = Math.max(0, t - 10.5) / 1.5;
        const easedPhase = loadPhase < 1 ? 1 - Math.cos((loadPhase * Math.PI) / 2) : 1;

        loadsRef.current.children.forEach((load) => {
          load.scale.setScalar(easedPhase);
          load.children.forEach((child) => {
            ((child as THREE.Mesh).material as THREE.MeshStandardMaterial).opacity = easedPhase * 0.85;
          });
        });

        // Subtle deflection
        const deflection = -0.02 * easedPhase * Math.sin(Math.PI / 2);
        if (concreteRef.current) concreteRef.current.position.y = deflection;
        if (bottomRebarsRef.current) bottomRebarsRef.current.position.y = deflection;
        if (topRebarsRef.current) topRebarsRef.current.position.y = deflection;
        if (stirrupsRef.current) stirrupsRef.current.position.y = deflection;
      }
    } else {
      // Construction complete - continuous slow rotation (15s per 360°)
      if (!constructionComplete.current) {
        constructionComplete.current = true;
      }

      // Continuous rotation on Y axis (~15 seconds per full rotation)
      if (groupRef.current) {
        const rotationSpeed = (Math.PI * 2) / 15; // Full 360° in 15 seconds
        const rotationTime = t - constructionDuration;
        groupRef.current.rotation.y = rotationTime * rotationSpeed;
      }
    }
  });

  return (
    <Float speed={1.5} rotationIntensity={0.2} floatIntensity={0.4}>
      <group ref={groupRef} rotation={[0.3, 0.5, 0.1]}>
        {/* Formwork */}
        <lineSegments ref={formworkRef} geometry={formworkGeometry}>
          <lineBasicMaterial color="#6366f1" transparent opacity={0} />
        </lineSegments>

        {/* Concrete */}
        <mesh ref={concreteRef} geometry={concreteGeometry}>
          <meshPhysicalMaterial
            color="#a8a29e"
            transparent
            opacity={0}
            metalness={0.1}
            roughness={0.7}
            transmission={0.2}
          />
        </mesh>

        {/* Bottom rebars */}
        <group ref={bottomRebarsRef}>
          {bottomRebarPositions.map(([z, y], i) => (
            <mesh key={`bottom-${i}`} position={[-beamLength, y, z]} rotation={[0, 0, Math.PI / 2]}>
              <cylinderGeometry args={[rebarDia / 2, rebarDia / 2, beamLength, 8]} />
              <meshStandardMaterial
                color="#a78bfa"
                transparent
                opacity={0}
                metalness={0.7}
                roughness={0.3}
                emissive="#a78bfa"
                emissiveIntensity={0.1}
              />
            </mesh>
          ))}
        </group>

        {/* Top rebars */}
        <group ref={topRebarsRef}>
          {topRebarPositions.map(([z, y], i) => (
            <mesh key={`top-${i}`} position={[beamLength, y, z]} rotation={[0, 0, Math.PI / 2]}>
              <cylinderGeometry args={[rebarDia / 2, rebarDia / 2, beamLength, 8]} />
              <meshStandardMaterial
                color="#a78bfa"
                transparent
                opacity={0}
                metalness={0.7}
                roughness={0.3}
                emissive="#a78bfa"
                emissiveIntensity={0.1}
              />
            </mesh>
          ))}
        </group>

        {/* Stirrups */}
        <group ref={stirrupsRef}>
          {stirrupPositions.map((x, i) => (
            <lineSegments key={`stirrup-${i}`} position={[x, 0, 0]} rotation={[0, Math.PI / 2, 0]} geometry={stirrupGeometries[i]}>
              <lineBasicMaterial color="#2dd4bf" transparent opacity={0} linewidth={2} />
            </lineSegments>
          ))}
        </group>

        {/* Load arrows */}
        <group ref={loadsRef}>
          {[-beamLength / 4, 0, beamLength / 4].map((x, i) => (
            <group key={`load-${i}`} position={[x, beamDepth / 2 + 0.15, 0]}>
              <mesh rotation={[Math.PI, 0, 0]}>
                <coneGeometry args={[0.04, 0.12, 8]} />
                <meshStandardMaterial color="#f43f5e" transparent opacity={0} />
              </mesh>
              <mesh position={[0, 0.1, 0]}>
                <cylinderGeometry args={[0.015, 0.015, 0.08, 8]} />
                <meshStandardMaterial color="#f43f5e" transparent opacity={0} />
              </mesh>
            </group>
          ))}
        </group>
      </group>
    </Float>
  );
}

export function HomePage() {
  const navigate = useNavigate();
  const prefersReducedMotion = useReducedMotion();

  return (
    <div className="relative w-screen h-screen bg-zinc-950 overflow-hidden">
      {/* Full-screen 3D Beam Background */}
      <div className="absolute inset-0" aria-hidden="true">
        <Canvas camera={{ position: [0, 0, 5], fov: 45 }}>
          <Suspense fallback={null}>
            <ambientLight intensity={0.4} />
            <directionalLight position={[5, 5, 5]} intensity={0.5} />
            <pointLight position={[-5, -5, -5]} intensity={0.3} color="#a78bfa" />
            <AnimatedBeamConstruction />
            <OrbitControls enableZoom={false} enablePan={false} autoRotate={!prefersReducedMotion} autoRotateSpeed={0.3} />
          </Suspense>
        </Canvas>
      </div>

      {/* Subtle gradient orbs */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-600/10 rounded-full blur-[120px]" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-[120px]" />
      </div>

      {/* Minimal Overlay - Center positioned */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: prefersReducedMotion ? 0 : 0.8, delay: prefersReducedMotion ? 0 : 0.3 }}
          className="flex flex-col items-center text-center px-6 py-8 rounded-2xl max-w-xl pointer-events-auto"
          style={{
            background: "rgba(0, 0, 0, 0.25)",
            backdropFilter: "blur(12px)",
            border: "1px solid rgba(255, 255, 255, 0.05)",
          }}
        >
          {/* Small Logo */}
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={prefersReducedMotion ? { duration: 0 } : { type: "spring", stiffness: 200, damping: 20, delay: 0.5 }}
            className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center mb-6"
          >
            <svg
              className="w-6 h-6 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </motion.div>

          {/* Clean Title */}
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: prefersReducedMotion ? 0 : 0.6, delay: prefersReducedMotion ? 0 : 0.7 }}
            className="text-4xl font-bold text-white tracking-tight mb-3"
          >
            StructLib
          </motion.h1>

          {/* Subtle Tagline */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: prefersReducedMotion ? 0 : 0.6, delay: prefersReducedMotion ? 0 : 0.9 }}
            className="text-sm text-white/60 mb-8"
          >
            IS 456:2000 Beam Design — Precision. Visualization. Export.
          </motion.p>

          {/* Action Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: prefersReducedMotion ? 0 : 0.5, delay: prefersReducedMotion ? 0 : 1.1 }}
            className="flex items-center gap-4"
          >
            {/* Primary CTA */}
            <motion.button
              whileHover={prefersReducedMotion ? {} : { scale: 1.05 }}
              whileTap={prefersReducedMotion ? {} : { scale: 0.97 }}
              onClick={() => navigate("/design")}
              className="group relative px-8 py-3 text-white font-semibold rounded-xl shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40 transition-shadow flex items-center gap-2 overflow-hidden"
            >
              <div
                className="absolute inset-0 bg-gradient-to-r from-blue-500 via-purple-600 to-blue-500 bg-[length:200%_100%]"
                style={{ animation: prefersReducedMotion ? 'none' : 'shimmer 3s linear infinite' }}
              />
              <span className="relative z-10 flex items-center gap-2">
                Start Designing
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </span>
            </motion.button>

            {/* Secondary CTA - Ghost Button */}
            <motion.button
              whileHover={prefersReducedMotion ? {} : { scale: 1.05, borderColor: "rgba(255, 255, 255, 0.25)" }}
              whileTap={prefersReducedMotion ? {} : { scale: 0.98 }}
              onClick={() => navigate("/import")}
              className="px-8 py-3 text-white font-semibold rounded-xl border-2 border-white/15 hover:bg-white/5 transition-all"
            >
              Explore
            </motion.button>
          </motion.div>
        </motion.div>
      </div>

      <style>{`
        @keyframes shimmer {
          0% { background-position: 200% 0; }
          100% { background-position: -200% 0; }
        }
      `}</style>
    </div>
  );
}
