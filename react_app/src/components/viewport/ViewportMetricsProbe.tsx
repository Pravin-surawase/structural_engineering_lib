import { useFrame } from '@react-three/fiber';
import { useRef } from 'react';

export interface ViewportRendererMetrics {
  averageFrameMs: number;
  maxFrameMs: number;
  drawCalls: number;
  geometries: number;
  textures: number;
}

/** Capture a bounded warm-render sample without changing scene behavior. */
export function ViewportMetricsProbe({
  onSample,
}: {
  onSample: (metrics: ViewportRendererMetrics) => void;
}) {
  const sampleRef = useRef({ frames: 0, totalMs: 0, maxMs: 0, drawCalls: 0 });

  useFrame(({ gl }, delta) => {
    const sample = sampleRef.current;
    if (sample.frames >= 30) return;
    const frameMs = delta * 1000;
    sample.frames += 1;
    sample.totalMs += frameMs;
    sample.maxMs = Math.max(sample.maxMs, frameMs);
    sample.drawCalls = Math.max(sample.drawCalls, gl.info.render.calls);
    if (sample.frames === 30) {
      onSample({
        averageFrameMs: sample.totalMs / sample.frames,
        maxFrameMs: sample.maxMs,
        drawCalls: sample.drawCalls,
        geometries: gl.info.memory.geometries,
        textures: gl.info.memory.textures,
      });
    }
  });

  return null;
}
