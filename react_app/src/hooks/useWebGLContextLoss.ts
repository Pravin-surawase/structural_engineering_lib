import { useEffect, useState } from 'react';
import { useThree } from '@react-three/fiber';

export function useWebGLContextLoss() {
  const { gl } = useThree();
  const [contextLost, setContextLost] = useState(false);

  useEffect(() => {
    const canvas = gl.domElement;

    const handleContextLost = (event: Event) => {
      event.preventDefault();
      console.warn('[Viewport3D] WebGL context lost');
      setContextLost(true);
    };

    const handleContextRestored = () => {
      console.info('[Viewport3D] WebGL context restored');
      setContextLost(false);
    };

    canvas.addEventListener('webglcontextlost', handleContextLost);
    canvas.addEventListener('webglcontextrestored', handleContextRestored);

    return () => {
      canvas.removeEventListener('webglcontextlost', handleContextLost);
      canvas.removeEventListener('webglcontextrestored', handleContextRestored);
    };
  }, [gl]);

  return contextLost;
}
