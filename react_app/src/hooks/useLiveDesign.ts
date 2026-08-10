/**
 * useLiveDesign Hook
 *
 * Ties together the design store, revision-safe REST design, and 3D geometry.
 * Provides a unified interface for live design workflow:
 * 1. Input changes → cancellable design request
 * 2. Design result → Store update
 * 3. Store update → 3D geometry refresh
 *
 * Results apply only when the request still owns the current input revision.
 */
import { useEffect, useCallback, useRef, useMemo } from 'react';
import { useDesignStore } from '../store/designStore';
import { useBeamGeometry } from './useBeamGeometry';
import { designBeam } from '../api/client';
import type { BeamDesignRequest } from '../api/client';
import type { Beam3DGeometry, BeamGeometryRequest } from './useBeamGeometry';
import { LatestRequestCoordinator } from '../workspace/requestCoordinator';
import type { ResultLifecycle, RevisionIdentity } from '../workspace/types';

interface LiveDesignOptions {
  /** Enable WebSocket connection */
  enabled?: boolean;
  /** Debounce delay for input changes (ms) */
  debounceMs?: number;
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
  /** Monotonic revision of the visible inputs. */
  inputRevision: number;
  /** Revision that produced the retained result, if any. */
  resultRevision: number | null;
  /** Truthful lifecycle of the retained result. */
  resultLifecycle: ResultLifecycle;
  /** Whether the retained result may drive a current-revision export. */
  exportEligible: boolean;
  /** 3D geometry data */
  geometry: Beam3DGeometry | null;
  /** Any error message */
  error: string | null;
  /** Connection status */
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'reconnecting' | 'error';
  /** Whether REST fallback is active (WS unavailable) */
  isFallbackActive: boolean;
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

const QUICK_REQUEST_KEY = 'quick-design';

export function createQuickDesignIdentity(
  inputs: BeamDesignRequest,
  length: number,
  inputRevision: number,
): RevisionIdentity {
  const canonicalInputs = JSON.stringify({
    width: inputs.width,
    depth: inputs.depth,
    length,
    moment: inputs.moment,
    shear: inputs.shear ?? 0,
    fck: inputs.fck,
    fy: inputs.fy,
    clearCover: inputs.clear_cover ?? 40,
    stirrupDiameter: inputs.stirrup_dia_mm ?? 8,
    mainBarDiameter: inputs.main_bar_dia_mm ?? 20,
  });
  let hash = 2166136261;
  for (let index = 0; index < canonicalInputs.length; index += 1) {
    hash ^= canonicalInputs.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  const inputHash = `quick-fnv1a-${(hash >>> 0).toString(16).padStart(8, '0')}`;
  return {
    projectId: 'quick-design',
    memberId: 'quick-beam',
    inputHash,
    inputRevision,
    memberRevision: inputRevision,
    projectRevision: inputRevision,
  };
}

function currentQuickDesignIdentity(): RevisionIdentity {
  const { inputs, length, inputRevision } = useDesignStore.getState();
  return createQuickDesignIdentity(inputs, length, inputRevision);
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
    autoDesign = true,
  } = options;

  // Design store
  const store = useDesignStore();
  const {
    inputs,
    length,
    result,
    inputRevision,
    resultRevision,
    resultLifecycle,
    isLoading,
    error,
    setInputs,
    setLength,
    setResult,
    setLoading,
    setError,
    reset,
  } = store;

  // Debounce ref for auto-design
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const lastInputsRef = useRef(inputs);
  const coordinatorRef = useRef(new LatestRequestCoordinator());
  const requestSequenceRef = useRef(0);
  const initialDesignRunnerRef = useRef<() => Promise<void>>(() => Promise.resolve());

  // Quick design deliberately uses the AbortSignal-aware REST facade until the
  // WebSocket contract carries a request/input revision that can be echoed back.
  const runRestDesign = useCallback(async () => {
    const requestInputs = { ...inputs };
    const requestRevision = inputRevision;
    const identity = createQuickDesignIdentity(requestInputs, length, requestRevision);
    requestSequenceRef.current += 1;
    const token = coordinatorRef.current.begin(
      QUICK_REQUEST_KEY,
      `quick-${requestSequenceRef.current}`,
      identity,
    );

    setLoading(true, requestRevision);
    try {
      const res = await designBeam(requestInputs, { signal: token.signal });
      if (coordinatorRef.current.isCurrent(token, currentQuickDesignIdentity())) {
        setResult(res, requestRevision);
      }
    } catch (err) {
      if (
        (err as Error).name !== 'AbortError'
        && coordinatorRef.current.isCurrent(token, currentQuickDesignIdentity())
      ) {
        setError((err as Error).message, requestRevision);
      }
    } finally {
      if (coordinatorRef.current.settle(token, currentQuickDesignIdentity())) {
        setLoading(false, requestRevision);
      }
    }
  }, [inputRevision, inputs, length, setError, setLoading, setResult]);
  initialDesignRunnerRef.current = runRestDesign;

  // Build geometry request from current state
  const geometryParams = useMemo<BeamGeometryRequest | null>(() => {
    if (resultLifecycle !== 'current' || !result?.success || !result.flexure) return null;

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
      cover: inputs.clear_cover ?? 40,
      is_seismic: false,
    };
  }, [inputs, length, result, resultLifecycle]);

  // Fetch geometry when design result changes
  const {
    data: geometry,
    isLoading: isLoadingGeometry,
    error: geometryError,
  } = useBeamGeometry(geometryParams, { enabled: Boolean(geometryParams) });

  // Initial design on mount — fire REST immediately so user sees a result
  useEffect(() => {
    if (!autoDesign || !enabled) return;
    void initialDesignRunnerRef.current();
  }, [autoDesign, enabled]);

  // Auto-design when inputs change. One debounced REST transport keeps request
  // ownership explicit and prevents the previous duplicate WS + REST dispatch.
  useEffect(() => {
    if (!autoDesign || !enabled) return;

    // Check if inputs actually changed
    const inputsChanged =
      lastInputsRef.current.width !== inputs.width ||
      lastInputsRef.current.depth !== inputs.depth ||
      lastInputsRef.current.moment !== inputs.moment ||
      lastInputsRef.current.shear !== inputs.shear ||
      lastInputsRef.current.fck !== inputs.fck ||
      lastInputsRef.current.fy !== inputs.fy ||
      lastInputsRef.current.clear_cover !== inputs.clear_cover ||
      lastInputsRef.current.stirrup_dia_mm !== inputs.stirrup_dia_mm ||
      lastInputsRef.current.main_bar_dia_mm !== inputs.main_bar_dia_mm;

    if (!inputsChanged) return;
    lastInputsRef.current = { ...inputs };

    // Debounce the design request
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    debounceRef.current = setTimeout(() => {
      void runRestDesign();
    }, debounceMs);

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, [inputs, autoDesign, enabled, debounceMs, runRestDesign]);

  // Actions
  const triggerDesign = useCallback(() => {
    if (!enabled) return false;
    void runRestDesign();
    return true;
  }, [enabled, runRestDesign]);

  const updateInputs = useCallback(
    (newInputs: Partial<typeof inputs>) => {
      coordinatorRef.current.cancel(QUICK_REQUEST_KEY);
      setInputs(newInputs);
    },
    [setInputs]
  );

  const updateLength = useCallback(
    (newLength: number) => {
      coordinatorRef.current.cancel(QUICK_REQUEST_KEY);
      setLength(newLength);
    },
    [setLength]
  );

  const resetDesign = useCallback(() => {
    coordinatorRef.current.cancel(QUICK_REQUEST_KEY);
    reset();
  }, [reset]);

  const reconnect = useCallback(() => {
    if (enabled) void runRestDesign();
  }, [enabled, runRestDesign]);

  // Cleanup any pending request on unmount.
  useEffect(() => {
    const coordinator = coordinatorRef.current;
    return () => {
      coordinator.cancelAll();
    };
  }, []);

  // Combined state
  const state: LiveDesignState = {
    isConnected: enabled,
    isDesigning: isLoading,
    isLoadingGeometry,
    latency: null,
    result,
    inputRevision,
    resultRevision,
    resultLifecycle,
    exportEligible: Boolean(
      result
      && resultLifecycle === 'current'
      && resultRevision === inputRevision,
    ),
    geometry: geometry ?? null,
    error: error || (geometryError as Error | null)?.message || null,
    connectionStatus: enabled ? 'connected' : 'disconnected',
    isFallbackActive: true,
  };

  // Combined actions
  const actions: LiveDesignActions = {
    triggerDesign,
    reconnect,
    updateInputs,
    updateLength,
    reset: resetDesign,
  };

  return { state, actions };
}

export default useLiveDesign;
