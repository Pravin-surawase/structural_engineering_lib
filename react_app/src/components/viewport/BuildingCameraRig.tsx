import { OrbitControls, PerspectiveCamera } from '@react-three/drei';
import { useFrame, useThree } from '@react-three/fiber';
import { useEffect, useRef } from 'react';
import * as THREE from 'three';
import type { OrbitControls as OrbitControlsImpl } from 'three-stdlib';
import { useReducedMotion } from '../../hooks/useReducedMotion';
import type { DeterministicCameraPose } from './cameraModel';

export function BuildingCameraRig({
  pose,
  focusRequest,
}: {
  pose: DeterministicCameraPose;
  focusRequest: number;
}) {
  const { camera } = useThree();
  const reducedMotion = useReducedMotion();
  const controlsRef = useRef<OrbitControlsImpl | null>(null);
  const transitionRef = useRef({
    startedAt: 0,
    durationMs: 900,
    startPosition: new THREE.Vector3(),
    startTarget: new THREE.Vector3(),
    endPosition: new THREE.Vector3(...pose.position),
    endTarget: new THREE.Vector3(...pose.target),
    active: false,
  });

  useEffect(() => {
    const transition = transitionRef.current;
    transition.startedAt = performance.now();
    transition.durationMs = reducedMotion ? 0 : 900;
    transition.startPosition.copy(camera.position);
    transition.startTarget.copy(controlsRef.current?.target ?? new THREE.Vector3(...pose.target));
    transition.endPosition.set(...pose.position);
    transition.endTarget.set(...pose.target);
    transition.active = true;
  }, [camera, focusRequest, pose, reducedMotion]);

  useFrame(() => {
    const transition = transitionRef.current;
    if (!transition.active) return;
    const progress = transition.durationMs === 0
      ? 1
      : Math.min(1, (performance.now() - transition.startedAt) / transition.durationMs);
    const eased = 1 - (1 - progress) ** 3;
    camera.position.lerpVectors(transition.startPosition, transition.endPosition, eased);
    if (controlsRef.current) {
      controlsRef.current.target.lerpVectors(
        transition.startTarget,
        transition.endTarget,
        eased,
      );
      controlsRef.current.update();
    }
    if (progress >= 1) transition.active = false;
  });

  return (
    <>
      <PerspectiveCamera makeDefault position={pose.position} fov={50} />
      <OrbitControls
        ref={controlsRef}
        enableDamping
        dampingFactor={0.1}
        minDistance={pose.minDistance}
        maxDistance={pose.maxDistance}
        target={pose.target}
      />
    </>
  );
}
