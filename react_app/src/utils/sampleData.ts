import type { SampleBeam, SampleDatasetEvidence } from '../api/client';
import type { BeamCSVRow } from '../types/csv';

export function mapSampleBeamsToRows(
  beams: SampleBeam[],
  dataset?: SampleDatasetEvidence,
): BeamCSVRow[] {
  return beams.map((beam) => ({
    id: beam.id,
    source_id: beam.source_id,
    story: beam.story,
    b: beam.width_mm,
    D: beam.depth_mm,
    span: beam.span_mm,
    fck: beam.fck_mpa,
    fy: beam.fy_mpa,
    Mu_mid: beam.mu_knm,
    Vu_start: beam.vu_kn,
    Vu_end: beam.vu_kn,
    cover: beam.cover_mm,
    point1: beam.point1,
    point2: beam.point2,
    dataset_id: dataset?.dataset_id,
    dataset_version: dataset?.dataset_version,
    dataset_sha256: dataset?.dataset_sha256,
  }));
}
