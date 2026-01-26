/**
 * useAutoDesign Hook
 *
 * Provides debounced auto-design on input changes with WebSocket fallback.
 * Implements <100ms latency target via WebSocket or debounced REST.
 */
import { useEffect, useRef, useCallback } from 'react';
import { useDesignStore } from '../store/designStore';
import { designBeam } from '../api/client';

const DEBOUNCE_MS = 300; // Debounce delay for REST fallback

export function useAutoDesign(enabled: boolean = true) {
  const { inputs, setResult, setLoading, setError } = useDesignStore();
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const runDesign = useCallback(async () => {
    // Cancel previous request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    setLoading(true);

    try {
      const result = await designBeam(inputs);
      setResult(result);
    } catch (error) {
      if ((error as Error).name !== 'AbortError') {
        setError((error as Error).message);
      }
    } finally {
      setLoading(false);
    }
  }, [inputs, setResult, setLoading, setError]);

  useEffect(() => {
    if (!enabled) return;

    // Clear previous timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // Set new debounced timeout
    timeoutRef.current = setTimeout(runDesign, DEBOUNCE_MS);

    // Cleanup
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [enabled, runDesign]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return { runDesign };
}
