import { describe, expect, it } from 'vitest';
import { LatestRequestCoordinator } from '../requestCoordinator';
import type { RevisionIdentity } from '../types';

const identity: RevisionIdentity = {
  projectId: 'project-1',
  memberId: 'beam-1',
  inputHash: 'hash-1',
  inputRevision: 1,
  memberRevision: 1,
  projectRevision: 1,
};

describe('LatestRequestCoordinator', () => {
  it('aborts the older request and rejects its response', () => {
    const coordinator = new LatestRequestCoordinator();
    const older = coordinator.begin('beam-1:design', 'request-1', identity);
    const newer = coordinator.begin('beam-1:design', 'request-2', identity);

    expect(older.signal.aborted).toBe(true);
    expect(coordinator.isCurrent(older, identity)).toBe(false);
    expect(coordinator.isCurrent(newer, identity)).toBe(true);
  });

  it('rejects a response when any active revision changed', () => {
    const coordinator = new LatestRequestCoordinator();
    const token = coordinator.begin('beam-1:design', 'request-1', identity);

    expect(
      coordinator.isCurrent(token, {
        ...identity,
        inputHash: 'hash-2',
        inputRevision: 2,
      }),
    ).toBe(false);
    expect(coordinator.settle(token, identity)).toBe(true);
    expect(coordinator.settle(token, identity)).toBe(false);
  });

  it('cancels all active work', () => {
    const coordinator = new LatestRequestCoordinator();
    const first = coordinator.begin('beam-1:design', 'request-1', identity);
    const second = coordinator.begin('beam-1:geometry', 'request-2', identity);

    coordinator.cancelAll();

    expect(first.signal.aborted).toBe(true);
    expect(second.signal.aborted).toBe(true);
    expect(coordinator.isCurrent(first, identity)).toBe(false);
  });
});
