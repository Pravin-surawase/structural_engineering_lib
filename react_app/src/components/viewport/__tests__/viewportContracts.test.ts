import { beforeEach, describe, expect, it } from 'vitest';

import { useImportedBeamsStore } from '../../../store/importedBeamsStore';
import type { BeamCSVRow } from '../../../types/csv';
import { useWorkspaceStore } from '../../../workspace/workspaceStore';
import {
  buildGeometrySpaceV1,
  createSyntheticPerformanceSpace,
} from '../buildingGeometry';
import { cameraPoseForMembers } from '../cameraModel';
import { GEOMETRY_SPACE_FALLBACK } from '../geometrySpace';
import {
  buildViewportInspection,
  viewportStatusCounts,
} from '../inspectionModel';

const beams: BeamCSVRow[] = [
  {
    id: 'B1', source_id: 'ETABS-101', story: 'GF', b: 300, D: 500, span: 6000,
    fck: 25, fy: 500, cover: 40, Mu_mid: 120, Vu_start: 70,
    point1: { x: 0, y: 0, z: 0 }, point2: { x: 6, y: 0, z: 0 },
  },
  {
    id: 'B2', source_id: 'ETABS-102', story: 'GF', b: 300, D: 450, span: 4000,
    fck: 25, fy: 500, cover: 40, Mu_mid: 90, Vu_start: 50,
    point1: { x: 6, y: 0, z: 0 }, point2: { x: 6, y: 4, z: 0 },
  },
];

describe('viewport contracts', () => {
  beforeEach(() => {
    useWorkspaceStore.getState().reset();
    useImportedBeamsStore.setState({ beams: [], selectedId: null, selectedFloor: null });
  });

  it('builds GeometrySpaceV1 with stable source IDs and one global transform boundary', () => {
    useImportedBeamsStore.getState().setBeams(beams);
    const contract = buildGeometrySpaceV1(useWorkspaceStore.getState().snapshot, beams);
    expect(contract.ok).toBe(true);
    if (!contract.ok) return;
    expect(contract.space.members.map((member) => member.memberId)).toEqual(['ETABS-101', 'ETABS-102']);
    expect(contract.space.members[0]).toMatchObject({
      sourceId: 'ETABS-101', label: 'B1', projectRevision: 2,
      start: { x: 0, y: 0, z: 0 }, end: { x: 6, y: 0, z: 0 },
    });
  });

  it('fails closed rather than silently dropping a member without source geometry', () => {
    const incomplete = [{ ...beams[0], point1: undefined, point2: undefined }];
    useImportedBeamsStore.getState().setBeams(incomplete);
    expect(buildGeometrySpaceV1(useWorkspaceStore.getState().snapshot, incomplete)).toEqual({
      ok: false,
      fallbackMarker: GEOMETRY_SPACE_FALLBACK,
      reason: 'Member ETABS-101 has incomplete identity, section, or source geometry.',
    });
  });

  it('derives a deterministic selected-member camera pose', () => {
    useImportedBeamsStore.getState().setBeams(beams);
    const contract = buildGeometrySpaceV1(useWorkspaceStore.getState().snapshot, beams);
    if (!contract.ok) throw new Error(contract.reason);
    const first = cameraPoseForMembers(contract.space.members, 'ETABS-101');
    const second = cameraPoseForMembers(contract.space.members, 'ETABS-101');
    expect(first).toEqual(second);
    expect(first.target).toEqual([3, 0, 0]);
  });

  it('uses current workspace evidence for status/utilization and marks edits stale', () => {
    useImportedBeamsStore.getState().setBeams(beams);
    const workspace = useWorkspaceStore.getState();
    const pending = workspace.beginMemberRequest('ETABS-101', 'result', 'request-1')!;
    workspace.applyMemberRecord('ETABS-101', 'result', {
      ...pending,
      lifecycle: 'current',
      runId: 'run-1',
      calculationIdentity: 'calc-1',
      libraryVersion: '0.23.0',
      decision: 'PASS',
      supportStatus: 'SUPPORTED',
      data: { utilization_ratio: 0.8 },
      settledAt: '2026-08-10T00:00:00.000Z',
    });

    const current = buildViewportInspection(useWorkspaceStore.getState().snapshot);
    expect(current[0]).toMatchObject({ status: 'pass', utilization: 0.8 });
    expect(viewportStatusCounts(current)).toMatchObject({ pass: 1, not_evaluated: 1 });

    const member = useWorkspaceStore.getState().snapshot!.members[0];
    workspace.updateMemberInputs(
      member.memberId,
      { ...member.inputs, widthMm: 350 },
      'changed-input-hash',
    );
    expect(buildViewportInspection(useWorkspaceStore.getState().snapshot)[0]).toMatchObject({
      status: 'stale',
      utilization: null,
    });
  });

  it('creates the declared 1,530-member render-only performance fixture deterministically', () => {
    useImportedBeamsStore.getState().setBeams(beams);
    const contract = buildGeometrySpaceV1(useWorkspaceStore.getState().snapshot, beams);
    if (!contract.ok) throw new Error(contract.reason);
    const source153 = {
      ...contract.space,
      members: Array.from({ length: 153 }, (_, index) => ({
        ...contract.space.members[index % 2],
        memberId: `source-${index}`,
        sourceId: `source-${index}`,
      })),
    };
    const large = createSyntheticPerformanceSpace(source153, 10);
    expect(large.members).toHaveLength(1530);
    expect(large.members[0].memberId).toBe('perf:0:source-0');
    expect(large.members[1529].memberId).toBe('perf:9:source-152');
    expect(new Set(large.members.map((member) => member.memberId)).size).toBe(1530);
  });
});
