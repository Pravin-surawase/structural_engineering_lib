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
  selectedFloor: string | null;
  isImporting: boolean;
  error: string | null;

  // Actions
  setBeams: (beams: BeamCSVRow[]) => void;
  addBeam: (beam: BeamCSVRow) => void;
  selectBeam: (id: string | null) => void;
  selectFloor: (floor: string | null) => void;
  setImporting: (importing: boolean) => void;
  setError: (error: string | null) => void;
  clearBeams: () => void;
}

export const useImportedBeamsStore = create<ImportedBeamsState>((set) => ({
  beams: [],
  selectedId: null,
  selectedFloor: null,
  isImporting: false,
  error: null,

  setBeams: (beams) => set({ beams, error: null }),

  addBeam: (beam) =>
    set((state) => ({
      beams: [...state.beams, beam],
    })),

  selectBeam: (selectedId) =>
    set((state) => {
      const beam = state.beams.find((b) => b.id === selectedId);
      return { selectedId, selectedFloor: beam?.story ?? state.selectedFloor };
    }),

  selectFloor: (selectedFloor) => set({ selectedFloor }),

  setImporting: (isImporting) => set({ isImporting }),

  setError: (error) => set({ error, isImporting: false }),

  clearBeams: () => set({ beams: [], selectedId: null, selectedFloor: null, error: null }),
}));
