import type { RevisionIdentity } from './types';

export interface RequestToken {
  key: string;
  requestId: string;
  identity: RevisionIdentity;
  signal: AbortSignal;
}

interface ActiveRequest extends RequestToken {
  controller: AbortController;
}

function sameIdentity(left: RevisionIdentity, right: RevisionIdentity): boolean {
  return (
    left.projectId === right.projectId
    && left.memberId === right.memberId
    && left.inputHash === right.inputHash
    && left.inputRevision === right.inputRevision
    && left.memberRevision === right.memberRevision
    && left.projectRevision === right.projectRevision
  );
}

export class LatestRequestCoordinator {
  private readonly active = new Map<string, ActiveRequest>();

  begin(key: string, requestId: string, identity: RevisionIdentity): RequestToken {
    const normalizedKey = key.trim();
    const normalizedRequestId = requestId.trim();
    if (!normalizedKey || !normalizedRequestId) {
      throw new Error('Request key and request ID are required.');
    }

    this.cancel(normalizedKey);
    const controller = new AbortController();
    const request: ActiveRequest = {
      key: normalizedKey,
      requestId: normalizedRequestId,
      identity: { ...identity },
      signal: controller.signal,
      controller,
    };
    this.active.set(normalizedKey, request);
    return request;
  }

  isCurrent(token: RequestToken, currentIdentity: RevisionIdentity): boolean {
    const active = this.active.get(token.key);
    return Boolean(
      active
      && !token.signal.aborted
      && active.requestId === token.requestId
      && sameIdentity(active.identity, token.identity)
      && sameIdentity(token.identity, currentIdentity),
    );
  }

  settle(token: RequestToken, currentIdentity: RevisionIdentity): boolean {
    if (!this.isCurrent(token, currentIdentity)) return false;
    this.active.delete(token.key);
    return true;
  }

  cancel(key: string): void {
    const active = this.active.get(key);
    if (!active) return;
    active.controller.abort();
    this.active.delete(key);
  }

  cancelAll(): void {
    for (const active of this.active.values()) {
      active.controller.abort();
    }
    this.active.clear();
  }
}
