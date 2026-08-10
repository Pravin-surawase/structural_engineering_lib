/**
 * GeometrySpaceV1 owns the two renderer boundaries frozen for P7.
 *
 * Global structural coordinates use x=east, y=north, z=up. Local beam-detail
 * coordinates use x=span, y=section width, z=height above soffit. Callers must
 * not pre-scale or pre-swap either frame.
 */

export const GEOMETRY_SPACE_V1 = 'GeometrySpaceV1' as const;
export const GLOBAL_SOURCE_SPACE_V1 = 'GlobalSourceSpaceV1' as const;
export const LOCAL_BEAM_SPACE_V1 = 'LocalBeamSpaceV1' as const;
export const GEOMETRY_SPACE_FALLBACK = 'geometry-space-v1-invalid' as const;

export type GlobalSourcePointM = Readonly<{ x: number; y: number; z: number }>;
export type LocalBeamPointMm = Readonly<{ x: number; y: number; z: number }>;
export type RendererPointM = readonly [number, number, number];

export interface GeometryMemberV1 {
  memberId: string;
  sourceId: string;
  label: string;
  story: string;
  frameType: 'beam' | 'column' | 'brace';
  section: { widthMm: number; depthMm: number };
  inputHash: string;
  projectRevision: number;
  memberRevision: number;
  sourceRevision: number;
  geometryRevision: number;
  start: GlobalSourcePointM;
  end: GlobalSourcePointM;
}

export interface GeometrySpaceV1 {
  schemaVersion: typeof GEOMETRY_SPACE_V1;
  frame: typeof GLOBAL_SOURCE_SPACE_V1;
  units: 'm';
  axes: 'x=east,y=north,z=up';
  members: readonly GeometryMemberV1[];
}

export type GeometrySpaceValidation =
  | { ok: true; value: GeometrySpaceV1 }
  | { ok: false; fallbackMarker: typeof GEOMETRY_SPACE_FALLBACK; reason: string };

/** Map source-metre global geometry into Three.js world metres exactly once. */
export function globalSourcePointToRendererM(point: GlobalSourcePointM): RendererPointM {
  const rendererZ = -point.y;
  return [point.x, point.z, rendererZ === 0 ? 0 : rendererZ];
}

/** Map local beam-detail mm without applying the global north-axis inversion. */
export function localBeamPointToRendererM(point: LocalBeamPointMm): RendererPointM {
  const rendererZ = point.y * 0.001;
  return [point.x * 0.001, point.z * 0.001, rendererZ === 0 ? 0 : rendererZ];
}

export function boundsForMembers(members: readonly GeometryMemberV1[]) {
  const points = members.flatMap((member) => [member.start, member.end]);
  if (points.length === 0) throw new Error('GeometrySpaceV1 requires one or more members.');

  return {
    minX: Math.min(...points.map((point) => point.x)),
    maxX: Math.max(...points.map((point) => point.x)),
    minY: Math.min(...points.map((point) => point.y)),
    maxY: Math.max(...points.map((point) => point.y)),
    minZ: Math.min(...points.map((point) => point.z)),
    maxZ: Math.max(...points.map((point) => point.z)),
  };
}

export function centerForBounds(bounds: ReturnType<typeof boundsForMembers>): GlobalSourcePointM {
  return {
    x: (bounds.minX + bounds.maxX) / 2,
    y: (bounds.minY + bounds.maxY) / 2,
    z: (bounds.minZ + bounds.maxZ) / 2,
  };
}

export function validateGeometrySpaceV1(value: unknown): GeometrySpaceValidation {
  if (!isRecord(value)
    || value.schemaVersion !== GEOMETRY_SPACE_V1
    || value.frame !== GLOBAL_SOURCE_SPACE_V1
    || value.units !== 'm'
    || value.axes !== 'x=east,y=north,z=up') {
    return invalid('Unsupported GeometrySpaceV1 schema, frame, units, or axes.');
  }
  if (!Array.isArray(value.members) || value.members.length === 0) return invalid('GeometrySpaceV1 requires members.');

  const ids = new Set<string>();
  for (const member of value.members) {
    if (!isGeometryMember(member)) return invalid('GeometrySpaceV1 member is incomplete or invalid.');
    if (ids.has(member.memberId)) return invalid('GeometrySpaceV1 contains duplicate memberId values.');
    ids.add(member.memberId);
  }
  return { ok: true, value: value as unknown as GeometrySpaceV1 };
}

function invalid(reason: string): GeometrySpaceValidation {
  return { ok: false, fallbackMarker: GEOMETRY_SPACE_FALLBACK, reason };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}

function isPoint(value: unknown): value is GlobalSourcePointM {
  return isRecord(value) && ['x', 'y', 'z'].every((key) => typeof value[key] === 'number' && Number.isFinite(value[key]));
}

function isPositiveInteger(value: unknown): value is number {
  return typeof value === 'number' && Number.isInteger(value) && value > 0;
}

function isGeometryMember(value: unknown): value is GeometryMemberV1 {
  if (!isRecord(value) || !isRecord(value.section)) return false;
  return ['memberId', 'sourceId', 'label', 'story'].every((key) => typeof value[key] === 'string' && value[key].length > 0)
    && (value.frameType === 'beam' || value.frameType === 'column' || value.frameType === 'brace')
    && typeof value.section.widthMm === 'number' && value.section.widthMm > 0
    && typeof value.section.depthMm === 'number' && value.section.depthMm > 0
    && typeof value.inputHash === 'string' && value.inputHash.length > 0
    && isPositiveInteger(value.projectRevision)
    && isPositiveInteger(value.memberRevision)
    && isPositiveInteger(value.sourceRevision)
    && isPositiveInteger(value.geometryRevision)
    && isPoint(value.start) && isPoint(value.end);
}
