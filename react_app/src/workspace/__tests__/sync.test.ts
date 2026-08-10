import { describe, expect, it, vi } from 'vitest';
import { createWorkspaceRevisionSync, type WorkspaceRevisionNotice } from '../sync';
import type { WorkspaceSnapshotV1 } from '../types';

class FakeChannel {
  listener: ((event: MessageEvent<WorkspaceRevisionNotice>) => void) | null = null;
  posted: WorkspaceRevisionNotice[] = [];
  closed = false;

  postMessage(message: WorkspaceRevisionNotice): void {
    this.posted.push(message);
  }

  addEventListener(
    _type: 'message',
    listener: (event: MessageEvent<WorkspaceRevisionNotice>) => void,
  ): void {
    this.listener = listener;
  }

  removeEventListener(): void {
    this.listener = null;
  }

  close(): void {
    this.closed = true;
  }
}

const snapshot = {
  projectId: 'project-1',
  projectRevision: 4,
  updatedAt: '2026-08-10T00:00:00.000Z',
} as WorkspaceSnapshotV1;

describe('workspace revision sync', () => {
  it('broadcasts only project revision metadata', () => {
    const channel = new FakeChannel();
    const sync = createWorkspaceRevisionSync('tab-1', vi.fn(), () => channel);

    sync.announce(snapshot);

    expect(channel.posted).toEqual([{
      type: 'workspace-revision',
      sourceId: 'tab-1',
      projectId: 'project-1',
      projectRevision: 4,
      updatedAt: '2026-08-10T00:00:00.000Z',
    }]);
    expect(channel.posted[0]).not.toHaveProperty('members');
  });

  it('ignores its own notice and reports another tab revision', () => {
    const channel = new FakeChannel();
    const onExternal = vi.fn();
    const sync = createWorkspaceRevisionSync('tab-1', onExternal, () => channel);
    const notice: WorkspaceRevisionNotice = {
      type: 'workspace-revision',
      sourceId: 'tab-1',
      projectId: 'project-1',
      projectRevision: 5,
      updatedAt: '2026-08-10T00:01:00.000Z',
    };

    channel.listener?.({ data: notice } as MessageEvent<WorkspaceRevisionNotice>);
    expect(onExternal).not.toHaveBeenCalled();

    channel.listener?.({
      data: { ...notice, sourceId: 'tab-2' },
    } as MessageEvent<WorkspaceRevisionNotice>);
    expect(onExternal).toHaveBeenCalledOnce();

    sync.close();
    expect(channel.closed).toBe(true);
  });
});
