/**
 * useLiveDesign Hook
 *
 * Ties together the design store, WebSocket updates, and 3D geometry.
 * Provides a unified interface for live design workflow:
 * 1. Input changes → WebSocket design request
 * 2. Design result → Store update
 * 3. Store update → 3D geometry refresh
 *
 * This creates the <100ms latency design experience.
 */
import { useEffect, useCallback, useRef, useMemo } from 'react';
import { useDesignStore } from '../store/designStore';
import { useDesignWebSocket } from './useDesignWebSocket';
import { useBeamGeometry } from './useBeamGeometry';
import type { Beam3DGeometry, BeamGeometryRequest } from './useBeamGeometry';

interface LiveDesignOptions {
  /** Enable WebSocket connection */
  enabled?: boolean;
  /** Debounce delay for input changes (ms) */
  debounceMs?: number;
  /** Session ID for WebSocket */
  sessionId?: string;
  /** Enable auto-design on input change */
  autoDesign?: boolean;
}

interface LiveDesignState {
  /** Is WebSocket connected */
  isConnected: boolean;
  /** Is design currently running */
  isDesigning: boolean;
  /** Is geometry loading */
  isLoadingGeometry: boolean;
  /** WebSocket latency in ms */
  latency: number | null;
  /** Last design result */
  result: import('../api/client').BeamDesignResponse | null;
  /** 3D geometry data */
  geometry: Beam3DGeometry | null;
  /** Any error message */
  error: string | null;
  /** Connection status */
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'reconnecting' | 'error';
}

interface LiveDesignActions {
  /** Manually trigger a design */
  triggerDesign: () => boolean;
  /** Reconnect WebSocket */
  reconnect: () => void;
  /** Update inputs */
  updateInputs: (inputs: Partial<import('../api/client').BeamDesignRequest>) => void;
  /** Update length */
  updateLength: (length: number) => void;
  /** Reset to defaults */
  reset: () => void;
}

/**
 * useLiveDesign - Complete live design workflow hook.
 *
 * @example
 * ```tsx
 * function DesignView() {
 *   const { state, actions } = useLiveDesign({ autoDesign: true });
 *
 *   return (
 *     <>
 *       <BeamForm onChange={actions.updateInputs} />
 *       <ConnectionStatus status={state.connectionStatus} latency={state.latency} />
 *       {state.geometry && <Viewport3D geometry={state.geometry} />}
 *       <ResultsPanel result={state.result} isLoading={state.isDesigning} />
 *     </>
 *   );
 * }
 * ```
 */
export function useLiveDesign(options: LiveDesignOptions = {}): {
  state: LiveDesignState;
  actions: LiveDesignActions;
} {
  const {
    enabled = true,
    debounceMs = 150,
    sessionId = 'default',
    autoDesign = true,
  } = options;

  // Design store
  const store = useDesignStore();
  const { inputs, length, result, isLoading, setInputs, setLength, reset } = store;

  // WebSocket hook
  const ws = useDesignWebSocket(sessionId, enabled);

  // Debounce ref for auto-design
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const lastInputsRef = useRef(inputs);

  // Build geometry request from current state
  const geometryParams = useMemo<BeamGeometryRequest | null>(() => {
    if (!result?.success || !result.flexure) return null;

    return {
      beam_id: 'live-design',
      story: 'Live',
      width: inputs.width,
      depth: inputs.depth,
      span: length,
      fck: inputs.fck,
      fy: inputs.fy,
      ast_start: result.flexure.ast_required,
      ast_mid: result.flexure.ast_required,
      ast_end: result.flexure.ast_required,
      stirrup_dia: 8,
      stirrup_spacing_start: result.shear?.stirrup_spacing ?? 150,
      stirrup_spacing_mid: result.shear?.stirrup_spacing ?? 200,
      stirrup_spacing_end: result.shear?.stirrup_spacing ?? 150,
      cover: 40,
      is_seismic: false,
    };
  }, [inputs, length, result]);

  // Fetch geometry when design result changes
  const {
    data: geometry,
    isLoading: isLoadingGeometry,
    error: geometryError,
  } = useBeamGeometry(geometryParams, { enabled: Boolean(geometryParams) });

  // Auto-design when inputs change
  useEffect(() => {
    if (!autoDesign || !enabled || !ws.isConnected) return;

    // Check if inputs actually changed
    const inputsChanged =
      lastInputsRef.current.width !== inputs.width ||
      lastInputsRef.current.depth !== inputs.depth ||
      lastInputsRef.current.moment !== inputs.moment ||
      lastInputsRef.current.shear !== inputs.shear ||
      lastInputsRef.current.fck !== inputs.fck ||
      lastInputsRef.current.fy !== inputs.fy;

    if (!inputsChanged) return;
    lastInputsRef.current = { ...inputs };

    // Debounce the design request
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    debounceRef.current = setTimeout(() => {
      ws.sendDesign();
    }, debounceMs);

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, [inputs, autoDesign, enabled, ws.isConnected, ws.sendDesign, debounceMs]);

  // Actions
  const triggerDesign = useCallback(() => {
    return ws.sendDesign();
  }, [ws]);

  const updateInputs = useCallback(
    (newInputs: Partial<typeof inputs>) => {
      setInputs({ ...inputs, ...newInputs });
    },
    [inputs, setInputs]
  );

  const updateLength = useCallback(
    (newLength: number) => {
      setLength(newLength);
    },
    [setLength]
  );

  // Combined state
  const state: LiveDesignState = {
    isConnected: ws.isConnected,
    isDesigning: isLoading,
    isLoadingGeometry,
    latency: ws.latency,
    result,
    geometry: geometry ?? null,
    error: ws.error || (geometryError as Error | null)?.message || null,
    connectionStatus: ws.status,
  };

  // Combined actions
  const actions: LiveDesignActions = {
    triggerDesign,
    reconnect: ws.reconnect,
    updateInputs,
    updateLength,
    reset,
  };

  return { state, actions };
}

export default useLiveDesign;
