import { Html } from '@react-three/drei';
import { useMemo } from 'react';
import * as THREE from 'three';
import { useBeamGeometry, type BeamGeometryRequest } from '../../hooks/useBeamGeometry';
import type { BeamCSVRow } from '../../types/csv';
import type { WorkspaceMember, WorkspaceSnapshotV1 } from '../../workspace/types';
import { globalSourcePointToRendererM } from './geometrySpace';
import type { ViewportMemberInspection } from './inspectionModel';
import { RebarLayer, StirrupLayer } from './renderPrimitives';

function astForBeam(beam: BeamCSVRow): number | null {
  if (typeof beam.ast_provided === 'number') return beam.ast_provided;
  if (typeof beam.ast_required === 'number') return beam.ast_required;
  if (typeof beam.bar_count === 'number' && typeof beam.bar_diameter === 'number') {
    return beam.bar_count * Math.PI * (beam.bar_diameter / 2) ** 2;
  }
  return null;
}

function geometryRequest(beam: BeamCSVRow): BeamGeometryRequest | null {
  const ast = astForBeam(beam);
  if (!ast || beam.b <= 0 || beam.D <= 0 || beam.span <= 0) return null;
  const spacing = beam.stirrup_spacing ?? 150;
  return {
    beam_id: beam.source_id ?? beam.id,
    story: beam.story ?? 'Unknown',
    width: beam.b,
    depth: beam.D,
    span: beam.span,
    fck: beam.fck ?? 25,
    fy: beam.fy ?? 500,
    ast_start: ast,
    ast_mid: ast,
    ast_end: ast,
    stirrup_dia: beam.stirrup_diameter ?? 8,
    stirrup_spacing_start: spacing,
    stirrup_spacing_mid: spacing,
    stirrup_spacing_end: spacing,
    cover: beam.cover ?? 40,
  };
}

function placementForBeam(beam: BeamCSVRow) {
  if (!beam.point1 || !beam.point2) return null;
  const startTuple = globalSourcePointToRendererM(beam.point1);
  const endTuple = globalSourcePointToRendererM(beam.point2);
  const start = new THREE.Vector3(...startTuple);
  const end = new THREE.Vector3(...endTuple);
  const direction = new THREE.Vector3().subVectors(end, start);
  if (direction.length() === 0) return null;
  direction.normalize();
  return {
    start,
    quaternion: new THREE.Quaternion().setFromUnitVectors(
      new THREE.Vector3(1, 0, 0),
      direction,
    ),
  };
}

function membersAreAdjacent(left: BeamCSVRow, right: BeamCSVRow): boolean {
  if (!left.point1 || !left.point2 || !right.point1 || !right.point2) return false;
  const toleranceM = 0.1;
  const distance = (a: BeamCSVRow['point1'], b: BeamCSVRow['point1']) => (
    a && b ? Math.hypot(a.x - b.x, a.y - b.y, a.z - b.z) : Number.POSITIVE_INFINITY
  );
  return distance(left.point1, right.point1) < toleranceM
    || distance(left.point1, right.point2) < toleranceM
    || distance(left.point2, right.point1) < toleranceM
    || distance(left.point2, right.point2) < toleranceM;
}

function DetailGeometry({
  beam,
  member,
  projectRevision,
  selected,
}: {
  beam: BeamCSVRow;
  member: WorkspaceMember;
  projectRevision: number;
  selected: boolean;
}) {
  const request = useMemo(() => geometryRequest(beam), [beam]);
  const placement = useMemo(() => placementForBeam(beam), [beam]);
  const { data, error } = useBeamGeometry(request, {
    enabled: request !== null,
    identity: {
      projectRevision,
      memberRevision: member.memberRevision,
      inputHash: member.inputHash,
    },
  });

  if (error && selected) {
    return (
      <Html center>
        <div className="rounded-lg border border-amber-500/30 bg-zinc-950/95 px-3 py-2 text-xs text-amber-100">
          Selected detailing is unavailable: {error.message}
        </div>
      </Html>
    );
  }
  if (!data || !placement) return null;
  return (
    <group position={placement.start} quaternion={placement.quaternion}>
      <RebarLayer rebars={data.rebars} opacity={selected ? 1 : 0.45} />
      {selected && data.stirrups.length > 0 ? <StirrupLayer stirrups={data.stirrups} /> : null}
    </group>
  );
}

export function SelectedBeamDetailLayer({
  selectedMemberId,
  snapshot,
  beamsByMemberId,
  inspectionByMemberId,
}: {
  selectedMemberId: string | null;
  snapshot: WorkspaceSnapshotV1;
  beamsByMemberId: ReadonlyMap<string, BeamCSVRow>;
  inspectionByMemberId: ReadonlyMap<string, ViewportMemberInspection>;
}) {
  const selectedBeam = selectedMemberId ? beamsByMemberId.get(selectedMemberId) : undefined;
  const selectedMember = selectedMemberId
    ? snapshot.members.find((member) => member.memberId === selectedMemberId)
    : undefined;
  const selectedInspection = selectedMemberId ? inspectionByMemberId.get(selectedMemberId) : undefined;
  const canShowDetail = selectedInspection?.status === 'pass' || selectedInspection?.status === 'fail';
  const adjacent = useMemo(() => {
    if (!selectedBeam || !canShowDetail) return [];
    return snapshot.members.flatMap((member) => {
      if (member.memberId === selectedMemberId) return [];
      const beam = beamsByMemberId.get(member.memberId);
      const inspection = inspectionByMemberId.get(member.memberId);
      const current = inspection?.status === 'pass' || inspection?.status === 'fail';
      return beam && current && membersAreAdjacent(selectedBeam, beam) ? [{ beam, member }] : [];
    });
  }, [beamsByMemberId, canShowDetail, inspectionByMemberId, selectedBeam, selectedMemberId, snapshot.members]);

  if (!selectedBeam || !selectedMember || !canShowDetail) return null;
  return (
    <>
      <DetailGeometry
        beam={selectedBeam}
        member={selectedMember}
        projectRevision={snapshot.projectRevision}
        selected
      />
      {adjacent.map(({ beam, member }) => (
        <DetailGeometry
          key={member.memberId}
          beam={beam}
          member={member}
          projectRevision={snapshot.projectRevision}
          selected={false}
        />
      ))}
    </>
  );
}
