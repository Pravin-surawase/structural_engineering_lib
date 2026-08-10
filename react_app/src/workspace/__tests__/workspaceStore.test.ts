import { beforeEach, describe, expect, it } from 'vitest';
import { memberIdentity, recordCanExport } from '../identity';
import type { EvidenceRecord } from '../types';
import { useWorkspaceStore } from '../workspaceStore';

function resetWithMember(): void {
  const store = useWorkspaceStore.getState();
  store.reset();
  store.createProject('project-1', 'Project 1', '2026-08-10T00:00:00.000Z');
  useWorkspaceStore.getState().replaceMembers(
    [
      {
        memberId: 'beam-1',
        sourceId: 'B1',
        label: 'B1',
        story: '1',
        inputHash: 'hash-1',
        inputs: { widthMm: 300, depthMm: 450 },
      },
    ],
    '2026-08-10T00:01:00.000Z',
  );
}

function settledResult(pending: EvidenceRecord): EvidenceRecord {
  return {
    ...pending,
    lifecycle: 'current',
    decision: 'PASS',
    supportStatus: 'SUPPORTED',
    calculationIdentity: 'calc-1',
    libraryVersion: '0.23.0',
    data: { utilization: 0.8 },
    settledAt: '2026-08-10T00:02:00.000Z',
  };
}

describe('workspace revision contract', () => {
  beforeEach(resetWithMember);

  it('applies only the active request at the current full identity', () => {
    const pending = useWorkspaceStore.getState().beginMemberRequest(
      'beam-1',
      'result',
      'request-1',
      '2026-08-10T00:01:30.000Z',
    );
    expect(pending).not.toBeNull();

    const result = settledResult(pending!);
    expect(
      useWorkspaceStore.getState().applyMemberRecord(
        'beam-1',
        'result',
        result,
        '2026-08-10T00:02:00.000Z',
      ),
    ).toBe(true);

    const snapshot = useWorkspaceStore.getState().snapshot!;
    const member = snapshot.members[0];
    expect(recordCanExport(member.result, memberIdentity(snapshot, member))).toBe(true);
  });

  it('invalidates every dependent record atomically after an input edit', () => {
    for (const kind of ['result', 'geometry', 'alternatives', 'metrics'] as const) {
      const pending = useWorkspaceStore.getState().beginMemberRequest(
        'beam-1',
        kind,
        `request-${kind}`,
      )!;
      expect(
        useWorkspaceStore.getState().applyMemberRecord(
          'beam-1',
          kind,
          settledResult(pending),
        ),
      ).toBe(true);
    }

    useWorkspaceStore.getState().updateMemberInputs(
      'beam-1',
      { widthMm: 350, depthMm: 450 },
      'hash-2',
      '2026-08-10T00:03:00.000Z',
    );

    const snapshot = useWorkspaceStore.getState().snapshot!;
    const member = snapshot.members[0];
    expect(member.inputRevision).toBe(2);
    expect(member.memberRevision).toBe(2);
    expect(snapshot.projectRevision).toBe(3);
    expect([
      member.result?.lifecycle,
      member.geometry?.lifecycle,
      member.alternatives?.lifecycle,
      member.metrics?.lifecycle,
    ]).toEqual(['stale', 'stale', 'stale', 'stale']);
    expect(recordCanExport(member.result, memberIdentity(snapshot, member))).toBe(false);
  });

  it('rejects a delayed result from the prior revision', () => {
    const pending = useWorkspaceStore.getState().beginMemberRequest(
      'beam-1',
      'result',
      'request-old',
    )!;
    const delayed = settledResult(pending);

    useWorkspaceStore.getState().updateMemberInputs(
      'beam-1',
      { widthMm: 400, depthMm: 450 },
      'hash-new',
    );
    useWorkspaceStore.getState().beginMemberRequest('beam-1', 'result', 'request-new');

    expect(
      useWorkspaceStore.getState().applyMemberRecord(
        'beam-1',
        'result',
        delayed,
      ),
    ).toBe(false);
    expect(
      useWorkspaceStore.getState().snapshot!.members[0].result?.requestId,
    ).toBe('request-new');
  });

  it('marks other member evidence stale when the project revision changes', () => {
    useWorkspaceStore.getState().replaceMembers(
      [
        {
          memberId: 'beam-1', sourceId: 'B1', label: 'B1', story: '1',
          inputHash: 'hash-1', inputs: { widthMm: 300, depthMm: 450 },
        },
        {
          memberId: 'beam-2', sourceId: 'B2', label: 'B2', story: '1',
          inputHash: 'hash-2', inputs: { widthMm: 300, depthMm: 450 },
        },
      ],
      '2026-08-10T00:02:00.000Z',
    );
    const pending = useWorkspaceStore.getState().beginMemberRequest(
      'beam-2',
      'result',
      'request-beam-2',
    )!;
    expect(
      useWorkspaceStore.getState().applyMemberRecord(
        'beam-2',
        'result',
        settledResult(pending),
      ),
    ).toBe(true);

    useWorkspaceStore.getState().updateMemberInputs(
      'beam-1',
      { widthMm: 350, depthMm: 450 },
      'hash-1-next',
    );

    expect(
      useWorkspaceStore.getState().snapshot!.members[1].result?.lifecycle,
    ).toBe('stale');
  });
});
