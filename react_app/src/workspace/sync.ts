import type { WorkspaceSnapshotV1 } from './types';

const CHANNEL_NAME = 'structlib-workbench-projects';

export interface WorkspaceRevisionNotice {
  type: 'workspace-revision';
  sourceId: string;
  projectId: string;
  projectRevision: number;
  updatedAt: string;
}

interface RevisionChannel {
  postMessage(message: WorkspaceRevisionNotice): void;
  addEventListener(
    type: 'message',
    listener: (event: MessageEvent<WorkspaceRevisionNotice>) => void,
  ): void;
  removeEventListener(
    type: 'message',
    listener: (event: MessageEvent<WorkspaceRevisionNotice>) => void,
  ): void;
  close(): void;
}

export interface WorkspaceRevisionSync {
  announce(snapshot: WorkspaceSnapshotV1): void;
  close(): void;
}

export function createWorkspaceRevisionSync(
  sourceId: string,
  onExternalRevision: (notice: WorkspaceRevisionNotice) => void,
  createChannel: (name: string) => RevisionChannel = (name) => new BroadcastChannel(name),
): WorkspaceRevisionSync {
  const normalizedSourceId = sourceId.trim();
  if (!normalizedSourceId) throw new Error('A workspace sync source ID is required.');
  const channel = createChannel(CHANNEL_NAME);
  const listener = (event: MessageEvent<WorkspaceRevisionNotice>) => {
    const notice = event.data;
    if (
      notice?.type !== 'workspace-revision'
      || notice.sourceId === normalizedSourceId
      || !notice.projectId
      || !Number.isInteger(notice.projectRevision)
    ) {
      return;
    }
    onExternalRevision(notice);
  };
  channel.addEventListener('message', listener);

  return {
    announce(snapshot) {
      channel.postMessage({
        type: 'workspace-revision',
        sourceId: normalizedSourceId,
        projectId: snapshot.projectId,
        projectRevision: snapshot.projectRevision,
        updatedAt: snapshot.updatedAt,
      });
    },
    close() {
      channel.removeEventListener('message', listener);
      channel.close();
    },
  };
}
