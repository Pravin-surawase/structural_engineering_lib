/**
 * Design State Store using Zustand
 *
 * Manages beam design inputs and results for live preview.
 */
import { create } from 'zustand';
import type { BeamDesignRequest, BeamDesignResponse } from '../api/client';
import type { ResultLifecycle } from '../workspace/types';

export interface DesignState {
  // Input parameters
  inputs: BeamDesignRequest;
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

export const useDesignStore = create<DesignState>((set) => ({
  inputs: DEFAULT_INPUTS,
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
      const changed = Object.entries(inputs).some(
        ([key, value]) => state.inputs[key as keyof BeamDesignRequest] !== value,
      );
      if (!changed) return state;
      return {
        inputs: { ...state.inputs, ...inputs },
        inputRevision: state.inputRevision + 1,
        resultLifecycle: state.result ? 'stale' : 'not_evaluated',
        isLoading: false,
        error: null,
      };
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
