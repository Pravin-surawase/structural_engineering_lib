import { create } from 'zustand';
import type { ProjectStage } from '../app/navigation';
import {
  invalidateMemberRecords,
  memberIdentity,
  pendingRecord,
  recordMatchesIdentity,
} from './identity';
import {
  WORKSPACE_SCHEMA_VERSION,
  isWorkspaceSnapshotV1,
  type EvidenceRecord,
  type JsonValue,
  type WorkspaceMember,
  type WorkspaceSnapshotV1,
} from './types';

export type MemberRecordKind = 'result' | 'geometry' | 'alternatives' | 'metrics';

export interface MemberInputState {
  inputHash: string;
  inputs: { [key: string]: JsonValue };
}

const MAX_MEMBER_INPUT_HISTORY = 20;

export interface NewWorkspaceMember {
  memberId: string;
  sourceId: string;
  label: string;
  story?: string | null;
  frameType?: string;
  inputHash: string;
  inputs: { [key: string]: JsonValue };
}

interface WorkspaceState {
  snapshot: WorkspaceSnapshotV1 | null;
  memberInputHistory: Record<string, MemberInputState[]>;
  createProject: (projectId: string, projectName: string, now?: string) => void;
  loadSnapshot: (snapshot: WorkspaceSnapshotV1) => void;
  replaceMembers: (members: NewWorkspaceMember[], now?: string) => void;
  setStage: (stage: ProjectStage, now?: string) => void;
  selectMember: (memberId: string | null) => void;
  selectFloor: (floor: string | null) => void;
  updateMemberInputs: (
    memberId: string,
    inputs: { [key: string]: JsonValue },
    inputHash: string,
    now?: string,
  ) => void;
  undoMemberInputs: (memberId: string, now?: string) => boolean;
  revertMemberInputs: (
    memberId: string,
    prior: MemberInputState,
    now?: string,
  ) => boolean;
  beginMemberRequest: (
    memberId: string,
    kind: MemberRecordKind,
    requestId: string,
    now?: string,
  ) => EvidenceRecord | null;
  applyMemberRecord: (
    memberId: string,
    kind: MemberRecordKind,
    record: EvidenceRecord,
    now?: string,
  ) => boolean;
  markSaved: (savedAt?: string) => void;
  reset: () => void;
}

function timestamp(now?: string): string {
  return now ?? new Date().toISOString();
}

function normalizeMember(member: NewWorkspaceMember): WorkspaceMember {
  return {
    memberId: member.memberId,
    sourceId: member.sourceId,
    label: member.label,
    story: member.story ?? null,
    frameType: member.frameType ?? 'beam',
    inputHash: member.inputHash,
    inputRevision: 1,
    memberRevision: 1,
    inputs: member.inputs,
    result: null,
    geometry: null,
    alternatives: null,
    metrics: null,
  };
}

function normalizeMembers(members: NewWorkspaceMember[]): WorkspaceMember[] {
  const normalized = members.map(normalizeMember);
  const ids = normalized.map((member) => member.memberId.trim());
  if (
    ids.some((id) => !id)
    || normalized.some((member) => !member.sourceId.trim() || !member.inputHash.trim())
    || new Set(ids).size !== ids.length
  ) {
    throw new Error('Workspace members require unique IDs, source IDs, and input hashes.');
  }
  return normalized;
}

function cloneInputs(inputs: { [key: string]: JsonValue }): { [key: string]: JsonValue } {
  return structuredClone(inputs);
}

function changedSnapshotForMemberInputs(
  snapshot: WorkspaceSnapshotV1,
  memberId: string,
  next: MemberInputState,
  now?: string,
): WorkspaceSnapshotV1 | null {
  const memberIndex = snapshot.members.findIndex((member) => member.memberId === memberId);
  if (memberIndex < 0 || !next.inputHash.trim()) return null;
  const existing = snapshot.members[memberIndex];
  if (existing.inputHash === next.inputHash) return null;
  const members = snapshot.members.map((member, index) => (
    index === memberIndex
      ? invalidateMemberRecords({
        ...existing,
        inputs: cloneInputs(next.inputs),
        inputHash: next.inputHash,
        inputRevision: existing.inputRevision + 1,
        memberRevision: existing.memberRevision + 1,
      })
      : invalidateMemberRecords(member)
  ));
  return {
    ...snapshot,
    members,
    projectRevision: snapshot.projectRevision + 1,
    dirty: true,
    saveState: 'dirty',
    updatedAt: timestamp(now),
  };
}

function appendInputHistory(
  history: MemberInputState[],
  state: MemberInputState,
): MemberInputState[] {
  return [...history, state].slice(-MAX_MEMBER_INPUT_HISTORY);
}

export const useWorkspaceStore = create<WorkspaceState>((set, get) => ({
  snapshot: null,
  memberInputHistory: {},

  createProject: (projectId, projectName, now) => {
    const normalizedProjectId = projectId.trim();
    const normalizedProjectName = projectName.trim();
    if (!normalizedProjectId || !normalizedProjectName) {
      throw new Error('Project ID and project name are required.');
    }
    const createdAt = timestamp(now);
    set({
      snapshot: {
        schemaVersion: WORKSPACE_SCHEMA_VERSION,
        projectId: normalizedProjectId,
        projectName: normalizedProjectName,
        projectRevision: 1,
        members: [],
        selectedStage: 'import',
        selectedMemberId: null,
        selectedFloor: null,
        dirty: true,
        saveState: 'dirty',
        createdAt,
        updatedAt: createdAt,
        savedAt: null,
        migrationOrigin: null,
      },
      memberInputHistory: {},
    });
  },

  loadSnapshot: (snapshot) => {
    if (!isWorkspaceSnapshotV1(snapshot)) {
      throw new Error('Cannot load an invalid workspace snapshot.');
    }
    set({ snapshot, memberInputHistory: {} });
  },

  replaceMembers: (members, now) => {
    const normalizedMembers = normalizeMembers(members);
    set((state) => {
      if (!state.snapshot) return state;
      const updatedAt = timestamp(now);
      return {
        snapshot: {
          ...state.snapshot,
          members: normalizedMembers,
          projectRevision: state.snapshot.projectRevision + 1,
          selectedMemberId: null,
          dirty: true,
          saveState: 'dirty',
          updatedAt,
        },
        memberInputHistory: {},
      };
    });
  },

  setStage: (selectedStage, now) =>
    set((state) => {
      if (!state.snapshot || state.snapshot.selectedStage === selectedStage) return state;
      return {
        snapshot: {
          ...state.snapshot,
          selectedStage,
          updatedAt: timestamp(now),
        },
      };
    }),

  selectMember: (selectedMemberId) =>
    set((state) => {
      if (!state.snapshot) return state;
      const exists = selectedMemberId === null
        || state.snapshot.members.some((member) => member.memberId === selectedMemberId);
      return exists
        ? { snapshot: { ...state.snapshot, selectedMemberId } }
        : state;
    }),

  selectFloor: (selectedFloor) =>
    set((state) => (
      state.snapshot
        ? { snapshot: { ...state.snapshot, selectedFloor } }
        : state
    )),

  updateMemberInputs: (memberId, inputs, inputHash, now) => {
    if (!inputHash.trim()) throw new Error('A normalized input hash is required.');
    set((state) => {
      if (!state.snapshot) return state;
      const existing = state.snapshot.members.find((member) => member.memberId === memberId);
      if (!existing) return state;
      const snapshot = changedSnapshotForMemberInputs(
        state.snapshot,
        memberId,
        { inputs, inputHash },
        now,
      );
      if (!snapshot) return state;
      return {
        snapshot,
        memberInputHistory: {
          ...state.memberInputHistory,
          [memberId]: appendInputHistory(
            state.memberInputHistory[memberId] ?? [],
            { inputHash: existing.inputHash, inputs: cloneInputs(existing.inputs) },
          ),
        },
      };
    });
  },

  undoMemberInputs: (memberId, now) => {
    const state = get();
    const history = state.memberInputHistory[memberId] ?? [];
    const prior = history.at(-1);
    if (!state.snapshot || !prior) return false;
    const snapshot = changedSnapshotForMemberInputs(state.snapshot, memberId, prior, now);
    if (!snapshot) return false;
    set({
      snapshot,
      memberInputHistory: {
        ...state.memberInputHistory,
        [memberId]: history.slice(0, -1),
      },
    });
    return true;
  },

  revertMemberInputs: (memberId, prior, now) => {
    if (!prior.inputHash.trim()) throw new Error('A normalized input hash is required.');
    const state = get();
    const existing = state.snapshot?.members.find((member) => member.memberId === memberId);
    if (!state.snapshot || !existing) return false;
    const snapshot = changedSnapshotForMemberInputs(state.snapshot, memberId, prior, now);
    if (!snapshot) return false;
    set({
      snapshot,
      memberInputHistory: {
        ...state.memberInputHistory,
        [memberId]: appendInputHistory(
          state.memberInputHistory[memberId] ?? [],
          { inputHash: existing.inputHash, inputs: cloneInputs(existing.inputs) },
        ),
      },
    });
    return true;
  },

  beginMemberRequest: (memberId, kind, requestId, now) => {
    if (!requestId.trim()) throw new Error('A request ID is required.');
    const snapshot = get().snapshot;
    const member = snapshot?.members.find((candidate) => candidate.memberId === memberId);
    if (!snapshot || !member) return null;
    const record = pendingRecord(memberIdentity(snapshot, member), requestId, timestamp(now));
    set({
      snapshot: {
        ...snapshot,
        members: snapshot.members.map((candidate) => (
          candidate.memberId === memberId
            ? { ...candidate, [kind]: record }
            : candidate
        )),
      },
    });
    return record;
  },

  applyMemberRecord: (memberId, kind, record, now) => {
    const snapshot = get().snapshot;
    const member = snapshot?.members.find((candidate) => candidate.memberId === memberId);
    if (!snapshot || !member) return false;
    const activeRecord = member[kind];
    const identity = memberIdentity(snapshot, member);
    if (
      !recordMatchesIdentity(record, identity)
      || activeRecord?.requestId !== record.requestId
      || activeRecord.lifecycle !== 'pending'
      || record.lifecycle === 'pending'
      || record.lifecycle === 'stale'
      || record.settledAt === null
    ) {
      return false;
    }

    const members = snapshot.members.map((candidate) => (
      candidate.memberId === memberId
        ? { ...candidate, [kind]: record }
        : candidate
    ));
    set({
      snapshot: {
        ...snapshot,
        members,
        dirty: true,
        saveState: 'dirty',
        updatedAt: timestamp(now),
      },
    });
    return true;
  },

  markSaved: (savedAt) =>
    set((state) => {
      if (!state.snapshot) return state;
      const saved = timestamp(savedAt);
      return {
        snapshot: {
          ...state.snapshot,
          dirty: false,
          saveState: 'clean',
          savedAt: saved,
          updatedAt: saved,
        },
      };
    }),

  reset: () => set({ snapshot: null, memberInputHistory: {} }),
}));
