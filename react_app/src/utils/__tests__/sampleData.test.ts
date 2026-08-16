import { describe, expect, it } from 'vitest';
import type { SampleBeam, SampleDatasetEvidence } from '../../api/client';
import { mapSampleBeamsToRows } from '../sampleData';

describe('mapSampleBeamsToRows', () => {
  it('preserves bundled dataset and assumption provenance', () => {
    const dataset: SampleDatasetEvidence = {
      dataset_id: 'sample-id',
      dataset_version: 'sample-v1',
      dataset_sha256: 'sample-hash',
      hash_algorithm: 'sha256-framed-files-v1',
      source_files: ['forces.csv', 'geometry.csv'],
      beam_count: 1,
    };
    const beam: SampleBeam = {
      id: 'B1_Ground',
      source_id: '82',
      story: 'Ground',
      width_mm: 230,
      depth_mm: 450,
      span_mm: 2750,
      mu_knm: 7.526,
      vu_kn: 13.088,
      fck_mpa: 25,
      fy_mpa: 500,
      cover_mm: 40,
      source_metadata: {
        sample_only: true,
        calculation_basis_origins: { fck_mpa: 'assumed_sample' },
      },
      point1: { x: 0, y: 0, z: 0 },
      point2: { x: 2.75, y: 0, z: 0 },
    };

    expect(mapSampleBeamsToRows([beam], dataset)[0]).toMatchObject({
      dataset_id: 'sample-id',
      dataset_version: 'sample-v1',
      dataset_sha256: 'sample-hash',
      source_metadata: beam.source_metadata,
    });
  });
});
