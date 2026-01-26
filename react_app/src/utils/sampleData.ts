import type { SampleBeam } from '../api/client';
import type { BeamCSVRow } from '../types/csv';

export function mapSampleBeamsToRows(beams: SampleBeam[]): BeamCSVRow[] {
  return beams.map((beam) => ({
    id: beam.id,
    story: beam.story,
    b: beam.width_mm,
    D: beam.depth_mm,
    span: beam.span_mm,
    fck: beam.fck_mpa,
    fy: beam.fy_mpa,
    Mu_mid: beam.mu_knm,
    Vu_start: beam.vu_kn,
    cover: beam.cover_mm,
    point1: beam.point1,
    point2: beam.point2,
  }));
}
