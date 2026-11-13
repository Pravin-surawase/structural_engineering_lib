/**
 * Imported Beams Store
 *
 * Zustand store for managing imported CSV beam data.
 */
import { create } from 'zustand';
import type { BeamCSVRow } from '../types/csv';
import {
  synchronizeImportedBeams,
  workspaceSnapshotToBeamRows,
} from '../workspace/importAdapter';
import type { WorkspaceSnapshotV1 } from '../workspace/types';
import { useWorkspaceStore } from '../workspace/workspaceStore';

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
  restoreFromWorkspace: (snapshot: WorkspaceSnapshotV1) => void;
  clearBeams: () => void;
}

export const useImportedBeamsStore = create<ImportedBeamsState>((set, get) => ({
  beams: [],
  selectedId: null,
  selectedFloor: null,
  isImporting: false,
  error: null,

  setBeams: (beams) => {
    try {
      synchronizeImportedBeams(beams);
      const staleIds = new Set(useWorkspaceStore.getState().snapshot?.members
        .filter((member) => member.result?.lifecycle === 'stale')
        .map((member) => member.memberId));
      set({
        beams: beams.map((beam) => staleIds.has(beam.source_id ?? beam.id) ? {
          ...beam,
          status: 'pending',
          is_valid: false,
          utilization: undefined,
          ast_required: undefined,
          ast_provided: undefined,
          asc_required: undefined,
          bar_count: undefined,
          bar_diameter: undefined,
          stirrup_spacing: undefined,
          stirrup_diameter: undefined,
          remarks: undefined,
        } : beam),
        error: null,
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Imported project synchronization failed.',
        isImporting: false,
      });
    }
  },

  addBeam: (beam) => {
    const beams = [...get().beams, beam];
    try {
      synchronizeImportedBeams(beams);
      set({ beams, error: null });
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Beam could not be added.' });
    }
  },

  selectBeam: (selectedId) => {
    const state = get();
    const beam = state.beams.find((candidate) => candidate.id === selectedId);
    useWorkspaceStore.getState().selectMember(beam ? (beam.source_id ?? beam.id) : null);
    set({ selectedId, selectedFloor: beam?.story ?? state.selectedFloor });
  },

  selectFloor: (selectedFloor) => {
    useWorkspaceStore.getState().selectFloor(selectedFloor);
    set({ selectedFloor });
  },

  setImporting: (isImporting) => set({ isImporting }),

  setError: (error) => set({ error, isImporting: false }),

  restoreFromWorkspace: (snapshot) => {
    const beams = workspaceSnapshotToBeamRows(snapshot);
    const selectedBeam = snapshot.selectedMemberId
      ? beams.find((beam) => (beam.source_id ?? beam.id) === snapshot.selectedMemberId)
      : undefined;
    set({
      beams,
      selectedId: selectedBeam?.id ?? null,
      selectedFloor: snapshot.selectedFloor,
      error: null,
      isImporting: false,
    });
  },

  clearBeams: () => set({ beams: [], selectedId: null, selectedFloor: null, error: null }),
}));
