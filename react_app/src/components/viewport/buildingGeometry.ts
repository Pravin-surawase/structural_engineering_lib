import type { BeamCSVRow } from '../../types/csv';
import type { JsonValue, WorkspaceMember, WorkspaceSnapshotV1 } from '../../workspace/types';
import {
  GEOMETRY_SPACE_FALLBACK,
  GEOMETRY_SPACE_V1,
  GLOBAL_SOURCE_SPACE_V1,
  validateGeometrySpaceV1,
  type GeometryMemberV1,
  type GeometrySpaceV1,
} from './geometrySpace';

export type BuildingGeometryContract =
  | {
    ok: true;
    space: GeometrySpaceV1;
    beamsByMemberId: ReadonlyMap<string, BeamCSVRow>;
  }
  | {
    ok: false;
    fallbackMarker: typeof GEOMETRY_SPACE_FALLBACK;
    reason: string;
  };

function pointFromInput(value: JsonValue | undefined) {
  if (value === null || typeof value !== 'object' || Array.isArray(value)) return null;
  const { x, y, z } = value;
  return typeof x === 'number' && Number.isFinite(x)
    && typeof y === 'number' && Number.isFinite(y)
    && typeof z === 'number' && Number.isFinite(z)
    ? { x, y, z }
    : null;
}

function positiveNumber(member: WorkspaceMember, key: string): number | null {
  const value = member.inputs[key];
  return typeof value === 'number' && Number.isFinite(value) && value > 0 ? value : null;
}

function frameType(member: WorkspaceMember): GeometryMemberV1['frameType'] | null {
  return member.frameType === 'beam' || member.frameType === 'column' || member.frameType === 'brace'
    ? member.frameType
    : null;
}

/** Build the authoritative renderer contract without dropping malformed members. */
export function buildGeometrySpaceV1(
  snapshot: WorkspaceSnapshotV1 | null,
  beams: readonly BeamCSVRow[],
): BuildingGeometryContract {
  if (!snapshot) return invalid('A revisioned project is required for the building viewport.');
  if (snapshot.members.length === 0) return invalid('The project has no structural members.');

  const beamsByMemberId = new Map(
    beams.map((beam) => [beam.source_id ?? beam.id, beam] as const),
  );
  if (beamsByMemberId.size !== beams.length) {
    return invalid('Building geometry contains duplicate source identities.');
  }

  const members: GeometryMemberV1[] = [];
  for (const member of snapshot.members) {
    const beam = beamsByMemberId.get(member.memberId);
    const start = pointFromInput(member.inputs.point1);
    const end = pointFromInput(member.inputs.point2);
    const widthMm = positiveNumber(member, 'widthMm');
    const depthMm = positiveNumber(member, 'depthMm');
    const normalizedFrameType = frameType(member);
    if (!beam || !start || !end || !widthMm || !depthMm || !normalizedFrameType) {
      return invalid(`Member ${member.memberId} has incomplete identity, section, or source geometry.`);
    }
    if (member.sourceId !== member.memberId || (beam.source_id ?? beam.id) !== member.memberId) {
      return invalid(`Member ${member.memberId} does not preserve its source identity.`);
    }
    members.push({
      memberId: member.memberId,
      sourceId: member.sourceId,
      label: member.label,
      story: member.story?.trim() || 'Unknown',
      frameType: normalizedFrameType,
      section: { widthMm, depthMm },
      inputHash: member.inputHash,
      projectRevision: snapshot.projectRevision,
      memberRevision: member.memberRevision,
      sourceRevision: member.inputRevision,
      // Imported global geometry is a canonical input, so its revision is the
      // owning member revision rather than a synthetic API-result revision.
      geometryRevision: member.memberRevision,
      start,
      end,
    });
  }

  const candidate: GeometrySpaceV1 = {
    schemaVersion: GEOMETRY_SPACE_V1,
    frame: GLOBAL_SOURCE_SPACE_V1,
    units: 'm',
    axes: 'x=east,y=north,z=up',
    members,
  };
  const validation = validateGeometrySpaceV1(candidate);
  if (!validation.ok) return validation;
  return { ok: true, space: validation.value, beamsByMemberId };
}

function invalid(reason: string): BuildingGeometryContract {
  return { ok: false, fallbackMarker: GEOMETRY_SPACE_FALLBACK, reason };
}

/** Render-only large-scene fixture. It must never feed engineering workflows. */
export function createSyntheticPerformanceSpace(
  source: GeometrySpaceV1,
  copies = 10,
  tileOffsetM = 50,
): GeometrySpaceV1 {
  if (!Number.isInteger(copies) || copies < 1) throw new Error('Performance copies must be a positive integer.');
  return {
    ...source,
    members: Array.from({ length: copies }, (_, tile) => source.members.map((member) => ({
      ...member,
      memberId: `perf:${tile}:${member.sourceId}`,
      sourceId: `perf:${tile}:${member.sourceId}`,
      start: { ...member.start, x: member.start.x + tile * tileOffsetM },
      end: { ...member.end, x: member.end.x + tile * tileOffsetM },
    }))).flat(),
  };
}
