import {
  boundsForMembers,
  centerForBounds,
  globalSourcePointToRendererM,
  type GeometryMemberV1,
  type RendererPointM,
} from './geometrySpace';

export interface DeterministicCameraPose {
  target: RendererPointM;
  position: RendererPointM;
  minDistance: number;
  maxDistance: number;
}

function distanceForMember(member: GeometryMemberV1): number {
  const dx = member.end.x - member.start.x;
  const dy = member.end.y - member.start.y;
  const dz = member.end.z - member.start.z;
  return Math.sqrt(dx * dx + dy * dy + dz * dz);
}

export function cameraPoseForMembers(
  members: readonly GeometryMemberV1[],
  selectedMemberId: string | null,
): DeterministicCameraPose {
  if (members.length === 0) {
    return { target: [0, 0, 0], position: [10, 6, 10], minDistance: 1, maxDistance: 120 };
  }
  const selected = selectedMemberId
    ? members.find((member) => member.memberId === selectedMemberId)
    : undefined;
  const sourceTarget = selected
    ? {
      x: (selected.start.x + selected.end.x) / 2,
      y: (selected.start.y + selected.end.y) / 2,
      z: (selected.start.z + selected.end.z) / 2,
    }
    : centerForBounds(boundsForMembers(members));
  const target = globalSourcePointToRendererM(sourceTarget);
  const bounds = boundsForMembers(members);
  const fullExtent = Math.max(
    bounds.maxX - bounds.minX,
    bounds.maxY - bounds.minY,
    bounds.maxZ - bounds.minZ,
    5,
  );
  const distance = selected
    ? Math.min(Math.max(distanceForMember(selected) * 1.8, 8), 120)
    : Math.min(Math.max(fullExtent * 1.8, 10), 120);
  return {
    target,
    position: [target[0] + distance, target[1] + distance * 0.6, target[2] + distance],
    minDistance: Math.max(0.5, distance * 0.05),
    maxDistance: Math.max(100, fullExtent * 8),
  };
}
