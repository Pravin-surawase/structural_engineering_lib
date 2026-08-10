import { describe, expect, it } from 'vitest';

import {
  GEOMETRY_SPACE_FALLBACK,
  boundsForMembers,
  centerForBounds,
  globalSourcePointToRendererM,
  localBeamPointToRendererM,
  validateGeometrySpaceV1,
} from '../geometrySpace';

// Mirrors tests/fixtures/geometry-space-v1.json without adding Node types to
// the browser TypeScript project. The Python contract test reads that file.
const fixture = {
  global: {
    schemaVersion: 'GeometrySpaceV1',
    frame: 'GlobalSourceSpaceV1',
    units: 'm',
    axes: 'x=east,y=north,z=up',
    members: [
      {
        memberId: 'ETABS-Frame-101', sourceId: 'ETABS-Frame-101', label: 'B1', story: 'GF', frameType: 'beam',
        section: { widthMm: 300, depthMm: 500 }, inputHash: 'input-b1',
        projectRevision: 3, memberRevision: 7, sourceRevision: 7, geometryRevision: 7,
        start: { x: 0, y: 0, z: 0 }, end: { x: 6, y: 0, z: 0 },
      },
      {
        memberId: 'ETABS-Frame-201', sourceId: 'ETABS-Frame-201', label: 'C1', story: 'GF', frameType: 'column',
        section: { widthMm: 450, depthMm: 450 }, inputHash: 'input-c1',
        projectRevision: 3, memberRevision: 7, sourceRevision: 7, geometryRevision: 7,
        start: { x: 6, y: 0, z: 0 }, end: { x: 6, y: 0, z: 3 },
      },
    ],
    bounds: { minX: 0, maxX: 6, minY: 0, maxY: 0, minZ: 0, maxZ: 3 },
    center: { x: 3, y: 0, z: 1.5 },
  },
  detail: {
    route: '/api/v1/geometry/beam/full', origin: 'left-support,center-width,soffit',
    rebar: { end: { x: 6000, y: -96, z: 56 } }, stirrup: { positionX: 150 },
  },
} as const;

describe('GeometrySpaceV1', () => {
  it('preserves source IDs as stable member IDs in global source metres', () => {
    const validated = validateGeometrySpaceV1(fixture.global);
    expect(validated).toMatchObject({ ok: true });
    expect(fixture.global.members.map((member) => member.memberId)).toEqual(fixture.global.members.map((member) => member.sourceId));
    expect(fixture.global.members[0]).toMatchObject({
      inputHash: 'input-b1',
      projectRevision: 3,
      memberRevision: 7,
    });
  });

  it('maps global source metres to renderer metres exactly once', () => {
    expect(globalSourcePointToRendererM(fixture.global.members[1].end)).toEqual([6, 3, 0]);
    expect(globalSourcePointToRendererM({ x: 1, y: 2, z: 3 })).toEqual([1, 3, -2]);
  });

  it('derives fixture bounds and centre without dropping members', () => {
    const bounds = boundsForMembers(fixture.global.members);
    expect(bounds).toEqual(fixture.global.bounds);
    expect(centerForBounds(bounds)).toEqual(fixture.global.center);
    expect(new Set(fixture.global.members.map((member) => member.memberId)).size).toBe(2);
  });

  it('rejects incompatible schemas with a visible fallback marker', () => {
    const invalid = validateGeometrySpaceV1({ ...fixture.global, schemaVersion: 'GeometrySpaceV0' });
    expect(invalid).toEqual(expect.objectContaining({ ok: false, fallbackMarker: GEOMETRY_SPACE_FALLBACK }));
  });

  it('keeps known local-detail placement in millimetres', () => {
    expect(fixture.detail.route).toBe('/api/v1/geometry/beam/full');
    expect(fixture.detail.origin).toBe('left-support,center-width,soffit');
    expect(localBeamPointToRendererM(fixture.detail.rebar.end)).toEqual([6, 0.056, -0.096]);
    expect(fixture.detail.stirrup.positionX).toBe(150);
  });
});
