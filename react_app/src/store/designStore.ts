/**
 * Design State Store using Zustand
 *
 * Manages beam design inputs and results for live preview.
 */
import { create } from 'zustand';
import type { BeamDesignRequest, BeamDesignResponse } from '../api/client';
import type { ResultLifecycle } from '../workspace/types';

type EffectiveDepthSource = 'pareto_proposal' | 'explicit' | null;

const EFFECTIVE_DEPTH_BASIS_KEYS = [
  'depth',
  'clear_cover',
  'stirrup_dia_mm',
  'main_bar_dia_mm',
] as const satisfies readonly (keyof BeamDesignRequest)[];

export interface DesignState {
  // Input parameters
  inputs: BeamDesignRequest;
  /**
   * Pareto alternatives carry an optimizer-selected depth.  It is a proposal,
   * not a manual effective-depth override, so a later manual basis edit must
   * return the request to the API's derived-depth contract.
   */
  effectiveDepthSource: EffectiveDepthSource;
  length: number; // mm - for 3D visualization

  // Result from API
  result: BeamDesignResponse | null;
  inputRevision: number;
  resultRevision: number | null;
  resultLifecycle: ResultLifecycle;
  isLoading: boolean;
  error: string | null;

  // Live update settings
  autoDesign: boolean; // Auto-run design on input changes
  useWebSocket: boolean; // Use WebSocket for <100ms latency
  wsLatency: number | null; // Last WebSocket latency in ms

  // Actions
  setInputs: (inputs: Partial<BeamDesignRequest>) => void;
  applyParetoProposal: (inputs: Partial<BeamDesignRequest> & { effective_depth: number }) => void;
  setLength: (length: number) => void;
  setResult: (result: BeamDesignResponse | null, inputRevision?: number) => boolean;
  setLoading: (loading: boolean, inputRevision?: number) => boolean;
  setError: (error: string | null, inputRevision?: number) => boolean;
  setAutoDesign: (enabled: boolean) => void;
  setUseWebSocket: (enabled: boolean) => void;
  setWsLatency: (latency: number | null) => void;
  reset: () => void;
}

const DEFAULT_INPUTS: BeamDesignRequest = {
  width: 300, // mm
  depth: 450, // mm
  moment: 150, // kN·m
  shear: 80, // kN
  torsion: 0, // kN·m
  fck: 25.0, // N/mm² (M25)
  fy: 500.0, // N/mm² (Fe500)
  clear_cover: 40, // mm
  stirrup_dia_mm: 8, // mm
  main_bar_dia_mm: 20, // mm
  include_serviceability: false,
  support_condition: 'simply_supported',
};

const DEFAULT_LENGTH = 4000; // mm

function revisedInputState(
  state: DesignState,
  inputs: BeamDesignRequest,
  effectiveDepthSource: EffectiveDepthSource,
): Pick<DesignState, 'inputs' | 'effectiveDepthSource' | 'inputRevision' | 'resultLifecycle' | 'isLoading' | 'error'> {
  return {
    inputs,
    effectiveDepthSource,
    inputRevision: state.inputRevision + 1,
    resultLifecycle: state.result ? 'stale' : 'not_evaluated',
    isLoading: false,
    error: null,
  };
}

function withoutEffectiveDepth(inputs: BeamDesignRequest): BeamDesignRequest {
  const { effective_depth: _effectiveDepth, ...derivedInputs } = inputs;
  return derivedInputs;
}

export const useDesignStore = create<DesignState>((set) => ({
  inputs: DEFAULT_INPUTS,
  effectiveDepthSource: null,
  length: DEFAULT_LENGTH,
  result: null,
  inputRevision: 1,
  resultRevision: null,
  resultLifecycle: 'not_evaluated',
  isLoading: false,
  error: null,
  autoDesign: true, // Enable by default
  useWebSocket: false, // Disable WebSocket by default (requires backend)
  wsLatency: null,

  setInputs: (inputs) =>
    set((state) => {
      const suppliesEffectiveDepth = Object.prototype.hasOwnProperty.call(inputs, 'effective_depth');
      const geometryChanged = EFFECTIVE_DEPTH_BASIS_KEYS.some(
        (key) => Object.prototype.hasOwnProperty.call(inputs, key)
          && state.inputs[key as keyof BeamDesignRequest] !== inputs[key as keyof BeamDesignRequest],
      );
      const clearParetoDepth = state.effectiveDepthSource === 'pareto_proposal'
        && !suppliesEffectiveDepth
        && geometryChanged;
      const nextInputs = clearParetoDepth
        ? { ...inputs, effective_depth: undefined }
        : inputs;
      const inputsChanged = Object.entries(nextInputs).some(
        ([key, value]) => state.inputs[key as keyof BeamDesignRequest] !== value,
      );
      const effectiveDepthSource: EffectiveDepthSource = suppliesEffectiveDepth
        ? (inputs.effective_depth === undefined ? null : 'explicit')
        : (clearParetoDepth ? null : state.effectiveDepthSource);
      if (!inputsChanged) {
        return effectiveDepthSource === state.effectiveDepthSource
          ? state
          : { effectiveDepthSource };
      }
      const mergedInputs = { ...state.inputs, ...nextInputs };
      // Omit rather than assign `undefined` so consumers that inspect the
      // in-memory request see the same derived-depth contract sent on HTTP.
      return revisedInputState(
        state,
        clearParetoDepth ? withoutEffectiveDepth(mergedInputs) : mergedInputs,
        effectiveDepthSource,
      );
    }),

  applyParetoProposal: (inputs) =>
    set((state) => {
      const inputsChanged = Object.entries(inputs).some(
        ([key, value]) => state.inputs[key as keyof BeamDesignRequest] !== value,
      );
      if (!inputsChanged) {
        return state.effectiveDepthSource === 'pareto_proposal'
          ? state
          : { effectiveDepthSource: 'pareto_proposal' };
      }
      return revisedInputState(state, { ...state.inputs, ...inputs }, 'pareto_proposal');
    }),

  setLength: (length) =>
    set((state) => {
      if (state.length === length) return state;
      return {
        length,
        inputRevision: state.inputRevision + 1,
        resultLifecycle: state.result ? 'stale' : 'not_evaluated',
        isLoading: false,
        error: null,
      };
    }),

  setResult: (result, inputRevision) => {
    let accepted = false;
    set((state) => {
      const targetRevision = inputRevision ?? state.inputRevision;
      if (targetRevision !== state.inputRevision) return state;
      accepted = true;
      return {
        result,
        resultRevision: result ? targetRevision : null,
        resultLifecycle: result ? 'current' : 'not_evaluated',
        isLoading: false,
        error: null,
      };
    });
    return accepted;
  },

  setLoading: (isLoading, inputRevision) => {
    let accepted = false;
    set((state) => {
      const targetRevision = inputRevision ?? state.inputRevision;
      if (targetRevision !== state.inputRevision) return state;
      accepted = true;
      return {
        isLoading,
        resultLifecycle: isLoading ? 'pending' : state.resultLifecycle,
      };
    });
    return accepted;
  },

  setError: (error, inputRevision) => {
    let accepted = false;
    set((state) => {
      const targetRevision = inputRevision ?? state.inputRevision;
      if (targetRevision !== state.inputRevision) return state;
      accepted = true;
      return {
        error,
        isLoading: false,
        resultLifecycle: error ? 'error' : state.resultLifecycle,
      };
    });
    return accepted;
  },

  setAutoDesign: (autoDesign) => set({ autoDesign }),

  setUseWebSocket: (useWebSocket) => set({ useWebSocket }),

  setWsLatency: (wsLatency) => set({ wsLatency }),

  reset: () =>
    set((state) => ({
      inputs: DEFAULT_INPUTS,
      effectiveDepthSource: null,
      length: DEFAULT_LENGTH,
      result: null,
      inputRevision: state.inputRevision + 1,
      resultRevision: null,
      resultLifecycle: 'not_evaluated',
      isLoading: false,
      error: null,
      autoDesign: true,
      useWebSocket: false,
      wsLatency: null,
    })),
}));
