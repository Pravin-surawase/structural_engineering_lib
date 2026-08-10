import { beforeEach, describe, expect, it } from 'vitest';

import type { BeamCSVRow } from '../../types/csv';
import { useWorkspaceStore } from '../workspaceStore';
import {
  beamRowsToWorkspaceMembers,
  synchronizeImportedBeams,
  workspaceSnapshotToBeamRows,
} from '../importAdapter';

const beams: BeamCSVRow[] = [
  {
    id: 'B1',
    source_id: 'ETABS-101',
    story: 'GF',
    b: 300,
    D: 500,
    span: 5000,
    fck: 25,
    fy: 500,
    cover: 40,
    Mu_mid: 120,
    Vu_start: 75,
    point1: { x: 0, y: 0, z: 0 },
    point2: { x: 5, y: 0, z: 0 },
  },
  {
    id: 'B2',
    source_id: 'ETABS-102',
    story: 'GF',
    b: 300,
    D: 450,
    span: 4500,
    fck: 25,
    fy: 500,
    cover: 40,
    Mu_mid: 100,
    Vu_start: 60,
  },
];

describe('import workspace adapter', () => {
  beforeEach(() => useWorkspaceStore.getState().reset());

  it('preserves source identity separately from the display label', () => {
    const members = beamRowsToWorkspaceMembers(beams);
    expect(members[0]).toMatchObject({
      memberId: 'ETABS-101',
      sourceId: 'ETABS-101',
      label: 'B1',
      story: 'GF',
    });
    expect(members[0].inputHash).toMatch(/^workspace-fnv1a-/);
  });

  it('creates review state and advances one revision for a bulk input edit', () => {
    synchronizeImportedBeams(beams);
    const first = useWorkspaceStore.getState().snapshot!;
    expect(first.selectedStage).toBe('review');
    expect(first.members).toHaveLength(2);

    synchronizeImportedBeams(beams.map((beam) => ({ ...beam, fck: 30 })));
    const updated = useWorkspaceStore.getState().snapshot!;
    expect(updated.projectRevision).toBe(first.projectRevision + 1);
    expect(updated.members.map((member) => member.inputRevision)).toEqual([2, 2]);
  });

  it('restores canonical member inputs without changing source identity', () => {
    synchronizeImportedBeams(beams);
    const restored = workspaceSnapshotToBeamRows(useWorkspaceStore.getState().snapshot!);
    expect(restored).toMatchObject([
      { id: 'B1', source_id: 'ETABS-101', b: 300, D: 500, Mu_mid: 120 },
      { id: 'B2', source_id: 'ETABS-102', b: 300, D: 450, Mu_mid: 100 },
    ]);
  });
});
