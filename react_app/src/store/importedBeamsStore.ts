/**
 * Imported Beams Store
 *
 * Zustand store for managing imported CSV beam data.
 */
import { create } from 'zustand';
import type { BeamCSVRow } from '../types/csv';

export interface ImportedBeamsState {
  beams: BeamCSVRow[];
  selectedId: string | null;
  isImporting: boolean;
  error: string | null;
  warnings: string[];
  unmatchedBeams: string[];
  unmatchedForces: string[];

  // Actions
  setBeams: (beams: BeamCSVRow[]) => void;
  addBeam: (beam: BeamCSVRow) => void;
  selectBeam: (id: string | null) => void;
  setImporting: (importing: boolean) => void;
  setError: (error: string | null) => void;
  setImportWarnings: (warnings: string[], unmatchedBeams: string[], unmatchedForces: string[]) => void;
  clearBeams: () => void;
}

export const useImportedBeamsStore = create<ImportedBeamsState>((set) => ({
  beams: [],
  selectedId: null,
  isImporting: false,
  error: null,
  warnings: [],
  unmatchedBeams: [],
  unmatchedForces: [],

  setBeams: (beams) => set({ beams, error: null }),

  addBeam: (beam) =>
    set((state) => ({
      beams: [...state.beams, beam],
    })),

  selectBeam: (selectedId) => set({ selectedId }),

  setImporting: (isImporting) => set({ isImporting }),

  setError: (error) => set({ error, isImporting: false }),

  setImportWarnings: (warnings, unmatchedBeams, unmatchedForces) =>
    set({ warnings, unmatchedBeams, unmatchedForces }),

  clearBeams: () =>
    set({
      beams: [],
      selectedId: null,
      error: null,
      warnings: [],
      unmatchedBeams: [],
      unmatchedForces: [],
    }),
}));
