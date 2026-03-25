/**
 * Tests for useImportedBeamsStore — Zustand store for CSV beam data.
 */
import { describe, it, expect, beforeEach } from 'vitest';
import { useImportedBeamsStore } from '../../store/importedBeamsStore';
import type { BeamCSVRow } from '../../types/csv';

const mockBeam = (overrides: Partial<BeamCSVRow> = {}): BeamCSVRow => ({
  id: 'B1',
  story: 'GF',
  b: 300,
  D: 500,
  span: 5000,
  fck: 25,
  fy: 500,
  cover: 40,
  ...overrides,
} as BeamCSVRow);

describe('useImportedBeamsStore', () => {
  beforeEach(() => {
    // Reset store between tests
    useImportedBeamsStore.setState({
      beams: [],
      selectedId: null,
      selectedFloor: null,
      isImporting: false,
      error: null,
    });
  });

  it('starts with empty state', () => {
    const state = useImportedBeamsStore.getState();
    expect(state.beams).toEqual([]);
    expect(state.selectedId).toBeNull();
    expect(state.selectedFloor).toBeNull();
    expect(state.isImporting).toBe(false);
    expect(state.error).toBeNull();
  });

  it('setBeams replaces all beams and clears error', () => {
    useImportedBeamsStore.getState().setError('old error');
    const beams = [mockBeam(), mockBeam({ id: 'B2', story: '1F' })];

    useImportedBeamsStore.getState().setBeams(beams);

    const state = useImportedBeamsStore.getState();
    expect(state.beams).toHaveLength(2);
    expect(state.error).toBeNull();
  });

  it('addBeam appends a single beam', () => {
    useImportedBeamsStore.getState().setBeams([mockBeam()]);
    useImportedBeamsStore.getState().addBeam(mockBeam({ id: 'B2' }));

    expect(useImportedBeamsStore.getState().beams).toHaveLength(2);
  });

  it('selectBeam sets selectedId and auto-sets floor from beam data', () => {
    useImportedBeamsStore.getState().setBeams([
      mockBeam({ id: 'B1', story: 'GF' }),
      mockBeam({ id: 'B2', story: '1F' }),
    ]);

    useImportedBeamsStore.getState().selectBeam('B2');

    const state = useImportedBeamsStore.getState();
    expect(state.selectedId).toBe('B2');
    expect(state.selectedFloor).toBe('1F');
  });

  it('selectBeam with null clears selection but keeps floor', () => {
    useImportedBeamsStore.getState().setBeams([mockBeam()]);
    useImportedBeamsStore.getState().selectBeam('B1');
    useImportedBeamsStore.getState().selectBeam(null);

    const state = useImportedBeamsStore.getState();
    expect(state.selectedId).toBeNull();
    expect(state.selectedFloor).toBe('GF'); // preserved from last beam
  });

  it('selectFloor sets floor filter', () => {
    useImportedBeamsStore.getState().selectFloor('2F');
    expect(useImportedBeamsStore.getState().selectedFloor).toBe('2F');
  });

  it('setImporting toggles importing state', () => {
    useImportedBeamsStore.getState().setImporting(true);
    expect(useImportedBeamsStore.getState().isImporting).toBe(true);

    useImportedBeamsStore.getState().setImporting(false);
    expect(useImportedBeamsStore.getState().isImporting).toBe(false);
  });

  it('setError sets error and resets isImporting', () => {
    useImportedBeamsStore.getState().setImporting(true);
    useImportedBeamsStore.getState().setError('Network error');

    const state = useImportedBeamsStore.getState();
    expect(state.error).toBe('Network error');
    expect(state.isImporting).toBe(false);
  });

  it('clearBeams resets beams, selection, floor, and error', () => {
    useImportedBeamsStore.getState().setBeams([mockBeam()]);
    useImportedBeamsStore.getState().selectBeam('B1');
    useImportedBeamsStore.getState().setError('some error');

    useImportedBeamsStore.getState().clearBeams();

    const state = useImportedBeamsStore.getState();
    expect(state.beams).toEqual([]);
    expect(state.selectedId).toBeNull();
    expect(state.selectedFloor).toBeNull();
    expect(state.error).toBeNull();
  });
});
