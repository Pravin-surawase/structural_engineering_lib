import type { BeamCSVRow, Point3D } from '../types/csv';
import type { JsonValue, WorkspaceMember, WorkspaceSnapshotV1 } from './types';
import type { NewWorkspaceMember } from './workspaceStore';
import { useWorkspaceStore } from './workspaceStore';
import { applyBatchResultToBeam, currentBatchResult } from './resultRecords';

function stableJsonValue(value: JsonValue): JsonValue {
  if (Array.isArray(value)) return value.map(stableJsonValue);
  if (value !== null && typeof value === 'object') {
    return Object.fromEntries(
      Object.entries(value)
        .sort(([left], [right]) => left.localeCompare(right))
        .map(([key, child]) => [key, stableJsonValue(child)]),
    );
  }
  return value;
}

function importedJsonValue(value: unknown, path = 'source_metadata'): JsonValue {
  if (
    value === null
    || typeof value === 'string'
    || typeof value === 'boolean'
    || (typeof value === 'number' && Number.isFinite(value))
  ) {
    return value;
  }
  if (Array.isArray(value)) {
    return value.map((item, index) => importedJsonValue(item, `${path}[${index}]`));
  }
  if (typeof value === 'object' && value !== null) {
    return Object.fromEntries(
      Object.entries(value).map(([key, item]) => [
        key,
        importedJsonValue(item, `${path}.${key}`),
      ]),
    );
  }
  throw new Error(`${path} must contain only finite JSON values.`);
}

export function hashWorkspaceInputs(inputs: { [key: string]: JsonValue }): string {
  const canonical = JSON.stringify(stableJsonValue(inputs));
  let hash = 2166136261;
  for (let index = 0; index < canonical.length; index += 1) {
    hash ^= canonical.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return `workspace-fnv1a-${(hash >>> 0).toString(16).padStart(8, '0')}`;
}

function pointInput(point: Point3D | undefined): JsonValue {
  return point ? { x: point.x, y: point.y, z: point.z } : null;
}

function sourceSnapshotSha256(beam: BeamCSVRow): JsonValue {
  const value = beam.source_metadata?.snapshot_sha256;
  return typeof value === 'string' ? value : null;
}

export function beamRowInputs(beam: BeamCSVRow): { [key: string]: JsonValue } {
  return {
    widthMm: beam.b,
    depthMm: beam.D,
    spanMm: beam.span,
    fckMpa: beam.fck ?? 25,
    fyMpa: beam.fy ?? 500,
    coverMm: beam.cover ?? 40,
    muStartKnm: beam.Mu_start ?? null,
    muMidKnm: beam.Mu_mid ?? null,
    muEndKnm: beam.Mu_end ?? null,
    vuStartKn: beam.Vu_start ?? null,
    vuEndKn: beam.Vu_end ?? null,
    muEnvelopeKnm: beam.mu_envelope ?? null,
    vuEnvelopeKn: beam.vu_envelope ?? null,
    point1: pointInput(beam.point1),
    point2: pointInput(beam.point2),
    datasetId: beam.dataset_id ?? null,
    datasetVersion: beam.dataset_version ?? null,
    datasetSha256: beam.dataset_sha256 ?? null,
    sourceSnapshotSha256: sourceSnapshotSha256(beam),
    sourceMetadata: importedJsonValue(beam.source_metadata ?? null),
  };
}

export function beamRowsToWorkspaceMembers(beams: BeamCSVRow[]): NewWorkspaceMember[] {
  const members = beams.map((beam) => {
    const sourceId = (beam.source_id ?? beam.id).trim();
    const inputs = beamRowInputs(beam);
    return {
      memberId: sourceId,
      sourceId,
      label: beam.id,
      story: beam.story ?? null,
      frameType: 'beam',
      inputHash: hashWorkspaceInputs(inputs),
      inputs,
    };
  });
  const memberIds = members.map((member) => member.memberId);
  if (memberIds.some((memberId) => !memberId) || new Set(memberIds).size !== memberIds.length) {
    throw new Error('Imported members require non-empty, unique source identities.');
  }
  return members;
}

function importProjectId(members: NewWorkspaceMember[]): string {
  const datasetId = members[0]?.inputs.datasetId;
  const datasetVersion = members[0]?.inputs.datasetVersion;
  if (typeof datasetId === 'string' && datasetId && typeof datasetVersion === 'string') {
    return `${datasetId}-${datasetVersion}`.replace(/[^a-zA-Z0-9_-]+/g, '-');
  }
  const identityInputs = {
    members: members.map((member) => member.sourceId),
  } satisfies { [key: string]: JsonValue };
  return `import-${hashWorkspaceInputs(identityInputs).replace('workspace-fnv1a-', '')}`;
}

function importProjectName(beams: BeamCSVRow[]): string {
  if (beams[0]?.dataset_id) return 'Bundled ETABS sample';
  const stories = new Set(beams.map((beam) => beam.story).filter(Boolean));
  return stories.size > 0 ? `Imported project · ${stories.size} stories` : 'Imported beam project';
}

/**
 * Reconciles the legacy imported-beam adapter with the revisioned workspace.
 * Result-only changes do not alter input hashes; real edits advance one project
 * revision and invalidate every dependent record atomically.
 */
export function synchronizeImportedBeams(beams: BeamCSVRow[]): void {
  if (beams.length === 0) return;
  const members = beamRowsToWorkspaceMembers(beams);
  const store = useWorkspaceStore.getState();
  const projectId = importProjectId(members);
  const existingIds = store.snapshot?.members.map((member) => member.memberId) ?? [];
  const incomingIds = members.map((member) => member.memberId);
  const sameProject = store.snapshot?.projectId === projectId;
  const sameMembers = sameProject
    && existingIds.length === incomingIds.length
    && existingIds.every((memberId, index) => memberId === incomingIds[index]);

  if (!sameProject) {
    store.createProject(projectId, importProjectName(beams));
    useWorkspaceStore.getState().replaceMembers(members);
  } else if (!sameMembers) {
    store.replaceMembers(members);
  } else {
    store.updateMembersInputs(members.map((member) => ({
      memberId: member.memberId,
      inputs: member.inputs,
      inputHash: member.inputHash,
    })));
  }
  useWorkspaceStore.getState().setStage('review');
}

function numericInput(member: WorkspaceMember, key: string, fallback: number): number {
  const value = member.inputs[key];
  return typeof value === 'number' && Number.isFinite(value) ? value : fallback;
}

function optionalNumericInput(member: WorkspaceMember, key: string): number | undefined {
  const value = member.inputs[key];
  return typeof value === 'number' && Number.isFinite(value) ? value : undefined;
}

function pointFromInput(value: JsonValue | undefined): Point3D | undefined {
  if (value === null || typeof value !== 'object' || Array.isArray(value)) return undefined;
  const { x, y, z } = value;
  return typeof x === 'number' && typeof y === 'number' && typeof z === 'number'
    ? { x, y, z }
    : undefined;
}

function sourceMetadataFromInput(
  value: JsonValue | undefined,
): Record<string, unknown> | undefined {
  if (value === null || typeof value !== 'object' || Array.isArray(value)) return undefined;
  return value;
}

/** Restore the imported-beam compatibility view from durable canonical inputs. */
export function workspaceSnapshotToBeamRows(snapshot: WorkspaceSnapshotV1): BeamCSVRow[] {
  return snapshot.members.map((member) => {
    const beam: BeamCSVRow = {
      id: member.label,
      source_id: member.sourceId,
      story: member.story ?? undefined,
      b: numericInput(member, 'widthMm', 0),
      D: numericInput(member, 'depthMm', 0),
      span: numericInput(member, 'spanMm', 0),
      fck: numericInput(member, 'fckMpa', 25),
      fy: numericInput(member, 'fyMpa', 500),
      cover: numericInput(member, 'coverMm', 40),
      Mu_start: optionalNumericInput(member, 'muStartKnm'),
      Mu_mid: optionalNumericInput(member, 'muMidKnm'),
      Mu_end: optionalNumericInput(member, 'muEndKnm'),
      Vu_start: optionalNumericInput(member, 'vuStartKn'),
      Vu_end: optionalNumericInput(member, 'vuEndKn'),
      mu_envelope: optionalNumericInput(member, 'muEnvelopeKnm'),
      vu_envelope: optionalNumericInput(member, 'vuEnvelopeKn'),
      point1: pointFromInput(member.inputs.point1),
      point2: pointFromInput(member.inputs.point2),
      dataset_id: typeof member.inputs.datasetId === 'string' ? member.inputs.datasetId : undefined,
      dataset_version: typeof member.inputs.datasetVersion === 'string' ? member.inputs.datasetVersion : undefined,
      dataset_sha256: typeof member.inputs.datasetSha256 === 'string' ? member.inputs.datasetSha256 : undefined,
      source_metadata: sourceMetadataFromInput(member.inputs.sourceMetadata),
      status: member.result?.lifecycle === 'current'
        ? member.result.decision === 'PASS' ? 'pass' : 'fail'
        : 'pending',
    };
    const result = currentBatchResult(snapshot, member.memberId);
    return result ? applyBatchResultToBeam(beam, result) : beam;
  });
}
