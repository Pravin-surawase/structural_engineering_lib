/**
 * Design State Store using Zustand
 *
 * Manages beam design inputs and results for live preview.
 */
import { create } from 'zustand';
import type { BeamDesignRequest, BeamDesignResponse } from '../api/client';

export interface DesignState {
  // Input parameters
  inputs: BeamDesignRequest;
  length: number; // mm - for 3D visualization

  // Result from API
  result: BeamDesignResponse | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  setInputs: (inputs: Partial<BeamDesignRequest>) => void;
  setLength: (length: number) => void;
  setResult: (result: BeamDesignResponse | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

const DEFAULT_INPUTS: BeamDesignRequest = {
  width: 300, // mm
  depth: 450, // mm
  moment: 150, // kN·m
  shear: 80, // kN
  fck: 25.0, // N/mm² (M25)
  fy: 500.0, // N/mm² (Fe500)
};

const DEFAULT_LENGTH = 4000; // mm

export const useDesignStore = create<DesignState>((set) => ({
  inputs: DEFAULT_INPUTS,
  length: DEFAULT_LENGTH,
  result: null,
  isLoading: false,
  error: null,

  setInputs: (inputs) =>
    set((state) => ({
      inputs: { ...state.inputs, ...inputs },
    })),

  setLength: (length) => set({ length }),

  setResult: (result) => set({ result, error: null }),

  setLoading: (isLoading) => set({ isLoading }),

  setError: (error) => set({ error, isLoading: false }),

  reset: () =>
    set({
      inputs: DEFAULT_INPUTS,
      length: DEFAULT_LENGTH,
      result: null,
      isLoading: false,
      error: null,
    }),
}));
