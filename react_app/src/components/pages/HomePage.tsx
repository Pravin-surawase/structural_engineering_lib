/**
 * HomePage - Animated splash screen with brand and single CTA.
 */
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Float } from "@react-three/drei";
import { Suspense, useMemo } from "react";
import * as THREE from "three";

/** Animated wireframe beam in the background */
function WireframeBeam() {
  const edges = useMemo(() => {
    const geo = new THREE.BoxGeometry(3, 0.6, 0.3);
    return new THREE.EdgesGeometry(geo);
  }, []);

  return (
    <Float speed={1.5} rotationIntensity={0.3} floatIntensity={0.5}>
      <group rotation={[0.3, 0.5, 0.1]}>
        <lineSegments geometry={edges}>
          <lineBasicMaterial color="#6366f1" transparent opacity={0.4} />
        </lineSegments>
        {/* Inner rebar lines */}
        {[-0.08, 0.08].map((z) =>
          [-0.2, 0.2].map((y) => (
            <mesh key={`${z}-${y}`} position={[0, y, z]} rotation={[0, 0, Math.PI / 2]}>
              <cylinderGeometry args={[0.015, 0.015, 2.8, 6]} />
              <meshBasicMaterial color="#a78bfa" transparent opacity={0.3} />
            </mesh>
          ))
        )}
      </group>
    </Float>
  );
}

export function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="relative h-screen w-screen bg-zinc-950 overflow-hidden flex flex-col items-center justify-center">
      {/* 3D Background */}
      <div className="absolute inset-0 opacity-40">
        <Canvas camera={{ position: [0, 0, 5], fov: 45 }}>
          <Suspense fallback={null}>
            <ambientLight intensity={0.3} />
            <WireframeBeam />
            <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.5} />
          </Suspense>
        </Canvas>
      </div>

      {/* Gradient orbs */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-600/10 rounded-full blur-[120px]" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-[120px]" />
      </div>

      {/* Content */}
      <div className="relative z-10 flex flex-col items-center text-center px-6">
        {/* Logo */}
        <motion.div
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ type: "spring", stiffness: 200, damping: 20, delay: 0.1 }}
          className="w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center mb-8 shadow-2xl shadow-blue-500/30"
        >
          <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
          </svg>
        </motion.div>

        {/* Title */}
        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.3 }}
          className="text-5xl md:text-7xl font-bold text-white tracking-tight mb-3"
        >
          StructLib
        </motion.h1>

        {/* Tagline */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="text-lg md:text-xl text-white/40 mb-12 max-w-md"
        >
          IS 456 Beam Design Engine
        </motion.p>

        {/* CTA */}
        <motion.button
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.7 }}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.97 }}
          onClick={() => navigate("/start")}
          className="group px-10 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold rounded-2xl shadow-xl shadow-blue-500/30 hover:shadow-2xl hover:shadow-blue-500/40 transition-shadow flex items-center gap-3 text-lg"
        >
          Start Engineering
          <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
        </motion.button>

        {/* Version */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2 }}
          className="mt-16 text-xs text-white/20"
        >
          v3.0 &middot; React + Three.js + FastAPI
        </motion.p>
      </div>
    </div>
  );
}
